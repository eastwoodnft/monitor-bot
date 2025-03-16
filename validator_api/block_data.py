import aiohttp
import logging
from config.settings import *
from config.state import state

async def get_chain_info():
    """Get chain-wide information from public RPC"""
    url = f"{UNION_RPC}/status"
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Extract block height safely
                sync_info = data.get("result", {}).get("sync_info", {})
                height = int(sync_info.get("latest_block_height", 0))
                
                # Calculate avg_block_time from earliest and latest block times if not directly provided
                # For now, use a default value as this calculation requires parsing timestamps
                avg_block_time = 6.0  # Default value in seconds
                
                logging.info(f"Successfully fetched chain info: height={height}")
                
                return {
                    'height': height,
                    'avg_block_time': avg_block_time
                }
        except (aiohttp.ClientError, KeyError, ValueError) as e:
            logging.error(f"⚠️ Public RPC Connection error: {e}")
            return None

async def get_latest_height():
    chain_info = await get_chain_info()
    return chain_info['height'] if chain_info else 0

async def get_missed_blocks(last_height, missed_blocks_timestamps=None):
    # Get chain info from public RPC
    chain_info = await get_chain_info()
    if not chain_info:
        return 0, last_height, 0, 0

    # Get signing info from public RPC
    url = f"{UNION_REST_API}/slashing/signing_info/{VALIDATOR_CONSENSUS_ADDRESS}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                
                total_missed = int(data["result"]["missed_blocks_counter"])
                
                # Calculate missed blocks since last check
                missed = total_missed - (state.total_missed if hasattr(state, 'total_missed') else 0)
                if missed < 0:
                    missed = 0
                
                logging.info(f"Missed blocks: {missed}, total: {total_missed}")
                return missed, chain_info['height'], total_missed, chain_info['avg_block_time']

        except (aiohttp.ClientError, KeyError) as e:
            logging.error(f"⚠️ Error fetching missed blocks: {e}")
            return 0, last_height, 0, 0
