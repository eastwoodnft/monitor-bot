import os
import dotenv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VALIDATOR_CONSENSUS_ADDRESS = os.getenv("VALIDATOR_CONSENSUS_ADDRESS")
VALIDATOR_OPERATOR_ADDRESS = os.getenv("VALIDATOR_OPERATOR_ADDRESS")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
# Public RPC endpoints (if needed)
UNION_RPC = "https://rpc.testnet-9.union.build/"
UNION_REST_API = "https://rest.testnet-9.union.build/"

# Use the validator-specific endpoints from .env (or fall back)
VALIDATOR_RPC = os.getenv("VALIDATOR_RPC", UNION_RPC)
VALIDATOR_API = os.getenv("VALIDATOR_API", UNION_REST_API)

SLASHING_WINDOW = 100
SLASHING_THRESHOLD = 0.20  # 20% threshold for slashing alert
