import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VALIDATOR_CONSENSUS_ADDRESS = os.getenv("VALIDATOR_CONSENSUS_ADDRESS")
VALIDATOR_OPERATOR_ADDRESS = os.getenv("VALIDATOR_OPERATOR_ADDRESS")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"  # Only defined once
UNION_RPC = "https://rpc.testnet-9.union.build/"
UNION_REST_API = "https://rest.testnet-9.union.build/"
VALIDATOR_RPC = os.getenv("VALIDATOR_RPC", UNION_RPC)  # Default to public RPC if not set
VALIDATOR_API = os.getenv("VALIDATOR_API", UNION_REST_API)  # Default to public API if not set
SLASHING_WINDOW = 100
SLASHING_THRESHOLD = 0.20  # 20% threshold for slashing alert
