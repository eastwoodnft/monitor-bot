import asyncio
import logging
from collections import deque
from validator_api.validator_status import get_validator_status
from validator_api.block_data import get_latest_height, get_missed_blocks
from telegram_bot.alerts import send_telegram_alert
from config.settings import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class MonitorState:
    def __init__(self):
        self.last_height = 0
        self.missed_since_last_alert = 0
        self.total_missed = 0
        self.total_blocks = 0
        self.avg_block_time = 0
        self.active = False
        self.voting_power = None
        self.total_voting_power = None
        self.rank = None
        self.jailed = False
        self.delegator_count = None
        self.uptime = None

state = MonitorState()

async def get_initial_height(max_attempts=3, delay=5):
    for attempt in range(max_attempts):
        try:
            height = await get_latest_height()
            if height > 0:
                return height
            logging.warning("Received height 0, retrying...")
        except Exception as e:
            logging.error(f"Failed to fetch initial height (attempt {attempt + 1}/{max_attempts}): {e}")
            if attempt < max_attempts - 1:
                await asyncio.sleep(delay)
    logging.error("Failed to fetch initial height after all attempts.")
    return 0

async def monitor():
    last_height = await get_initial_height()
    if last_height == 0:
        await send_telegram_alert("⚠️ Failed to fetch initial block height. Starting from 0.")
    state.last_height = last_height
    missed_blocks_timestamps = deque(maxlen=SLASHING_WINDOW)
    failures = 0
    max_failures = 5

    while True:
        try:
            # Fetch validator status and block data
            active, voting_power, total_voting_power, rank, jailed, delegator_count, _ = await get_validator_status()
            missed, current_height, total_missed, avg_block_time = await get_missed_blocks(state.last_height, missed_blocks_timestamps)

            # Update state
            state.active = active if active is not None else False
            state.voting_power = voting_power
            state.total_voting_power = total_voting_power
            state.rank = rank
            state.jailed = jailed if jailed is not None else False
            state.delegator_count = delegator_count
            state.total_missed = total_missed if total_missed is not None else state.total_missed
            state.avg_block_time = avg_block_time if avg_block_time is not None else 0
            state.uptime = 100 * (1 - (total_missed / SLASHING_WINDOW)) if total_missed is not None and total_missed > 0 else 100

            logging.info(
                f"State updated: active={state.active}, voting_power={state.voting_power}, "
                f"total_missed={state.total_missed}, avg_block_time={state.avg_block_time}, uptime={state.uptime}"
            )

            # Reset failures on success
            failures = 0

            # Alert conditions
            if not state.active and state.voting_power is None:
                await send_telegram_alert("*Validator is not in the active set!*")
            if state.jailed:
                await send_telegram_alert("*Validator is jailed!* Immediate action required!")
            if voting_power is not None and voting_power < 1000:
                await send_telegram_alert(f"*Low voting power*: {voting_power // 10**6} UNION (Rank: {rank})")
            if avg_block_time is not None and avg_block_time > 10:
                await send_telegram_alert(f"*Slow block time*: {avg_block_time:.2f}s")
            if delegator_count is not None and delegator_count < 10:
                await send_telegram_alert(f"*Low delegator count*: {delegator_count} UNION")
            if state.uptime is not None and state.uptime < (100 - SLASHING_THRESHOLD * 100):
                await send_telegram_alert(f"*High miss rate*: {state.total_missed}/{SLASHING_WINDOW} blocks missed!")

            if missed > 0:
                state.missed_since_last_alert += missed
                logging.info(f"Missed {missed} blocks this check. Total since last alert: {state.missed_since_last_alert}")
                if state.missed_since_last_alert > 5:
                    miss_rate = (state.total_missed / SLASHING_WINDOW * 100)
                    await send_telegram_alert(
                        f"🚨 *Validator missed {state.missed_since_last_alert} blocks since last alert!* "
                        f"Slashing Window: {state.total_missed}/{SLASHING_WINDOW} ({miss_rate:.1f}%)"
                    )
                    state.missed_since_last_alert = 0

            state.last_height = current_height if current_height is not None else state.last_height

        except Exception as e:
            failures += 1
            logging.error(f"Loop iteration failed ({failures}/{max_failures}): {e}")
            if failures >= max_failures:
                await send_telegram_alert("🚨 *Critical Error*: RPC endpoint unreachable. Shutting down.")
                break
            await asyncio.sleep(5)  # Short delay before retrying

        await asyncio.sleep(60)  # Normal polling interval

if __name__ == "__main__":
    asyncio.run(monitor())
