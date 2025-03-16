import aiohttp
from config.settings import *

async def get_latest_height():
    url = f"{UNION_RPC}/abci_info?"
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                # Extract latest block height from the RPC status
                return int(data["result"]["response"]["last_block_height"])
        except (aiohttp.ClientError, KeyError, ValueError) as e:
            print(f"⚠️ RPC Connection error: {e}")
            return 0

async def get_missed_blocks(last_height, missed_blocks_timestamps=None):
    # For this fix, we'll provide a dummy implementation—
    # you may later replace this with a proper RPC call.
    # We'll return 0 missed blocks, the current height, total missed 0, and a default avg_block_time.
    return 0, last_height, 0, 6.0
