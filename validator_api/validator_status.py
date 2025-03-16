import aiohttp
import os
from dotenv import load_dotenv
from config.settings import *

async def get_validator_status():
    """Get comprehensive validator status using both public API and validator RPC"""
    validator_data = {}
    
    # 1. Get validator-specific info from validator's RPC
    try:
        # Get validator node status (sync info, voting power)
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(f"{VALIDATOR_RPC}/status?") as response:
                response.raise_for_status()
                data = await response.json()
                validator_info = data["result"]["validator_info"]
                sync_info = data["result"]["sync_info"]
                
                validator_data["voting_power"] = int(validator_info["voting_power"])
                validator_data["is_synced"] = not sync_info["catching_up"]
                validator_data["latest_height"] = int(sync_info["latest_block_height"])
                validator_data["consensus_address"] = validator_info["address"]
                
            # Get peer count from validator node
            async with session.get(f"{VALIDATOR_RPC}/net_info?") as response:
                response.raise_for_status()
                data = await response.json()
                validator_data["peer_count"] = len(data["result"]["peers"])
    except (aiohttp.ClientError, KeyError, ValueError) as e:
        print(f"⚠️ Error fetching data from validator node: {e}")
        return False, 0, 0, 0, False, 0, 0.0
    
    # 2. Get network-wide info from public API
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # Get validator rank from public RPC
            validators_url = f"{UNION_RPC}/validators?height={validator_data['latest_height']}&page=1&per_page=100"
            async with session.get(validators_url) as response:
                response.raise_for_status()
                validators_data = await response.json()
                
                # Find validator's rank and calculate total voting power
                total_voting_power = 0
                rank = 0
                
                for idx, val in enumerate(validators_data["result"]["validators"], 1):
                    total_voting_power += int(val["voting_power"])
                    if val["address"] == validator_data["consensus_address"]:
                        rank = idx
                        break
                
                validator_data["total_voting_power"] = total_voting_power
                validator_data["rank"] = rank
            
            # Get jailed status and delegator count from REST API
            status_url = f"{UNION_REST_API}/cosmos/staking/v1beta1/validators/{VALIDATOR_OPERATOR_ADDRESS}"
            async with session.get(status_url) as response:
                response.raise_for_status()
                data = await response.json()
                validator_data["jailed"] = data["validator"].get("jailed", False)
                
            # Get delegator count
            delegators_url = f"{UNION_REST_API}/cosmos/staking/v1beta1/validators/{VALIDATOR_OPERATOR_ADDRESS}/delegations?pagination.limit=1&pagination.count_total=true"
            async with session.get(delegators_url) as response:
                response.raise_for_status()
                data = await response.json()
                validator_data["delegator_count"] = int(data["pagination"]["total"])
    except (aiohttp.ClientError, KeyError, ValueError) as e:
        print(f"⚠️ Error fetching data from public API: {e}")
        # Use data we have so far, don't completely fail
        validator_data.setdefault("total_voting_power", 0)
        validator_data.setdefault("rank", 0)
        validator_data.setdefault("jailed", False)
        validator_data.setdefault("delegator_count", 0)
    
    return (
        validator_data["is_synced"],
        validator_data["voting_power"],
        validator_data["total_voting_power"],
        validator_data["rank"],
        validator_data["jailed"],
        validator_data["delegator_count"],
        validator_data.get("peer_count", 0)  # Add peer count as last value
    )