"""Ghost Tribunal — Configuration"""

import os
from dotenv import load_dotenv

load_dotenv()

# X Layer — default to testnet for development
XLAYER_NETWORK = os.getenv("XLAYER_NETWORK", "testnet")  # "testnet" or "mainnet"
XLAYER_RPC = os.getenv("XLAYER_RPC", "https://testrpc.xlayer.tech" if XLAYER_NETWORK == "testnet" else "https://rpc.xlayer.tech")
XLAYER_CHAIN_ID = 1952 if XLAYER_NETWORK == "testnet" else 196
XLAYER_CHAIN_INDEX = str(XLAYER_CHAIN_ID)
XLAYER_EXPLORER = "https://www.okx.com/web3/explorer/xlayer-test" if XLAYER_NETWORK == "testnet" else "https://www.okx.com/web3/explorer/xlayer"

# OKX OnchainOS
OKX_API_KEY = os.getenv("OKX_API_KEY", "")
OKX_SECRET_KEY = os.getenv("OKX_SECRET_KEY", "")
OKX_PASSPHRASE = os.getenv("OKX_PASSPHRASE", "")
OKX_PROJECT_ID = os.getenv("OKX_PROJECT_ID", "")
OKX_BASE_URL = "https://web3.okx.com/api/v5"

# Wallet
TRIBUNAL_PRIVATE_KEY = os.getenv("TRIBUNAL_PRIVATE_KEY", "")

# AI (OpenRouter)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
AGENT_MODEL = os.getenv("AGENT_MODEL", "google/gemini-2.5-flash")

# Discord
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")

# Tribunal settings
VOTE_THRESHOLD = 3          # 3/4 agents must agree to trade
VERDICT_COOLDOWN = 300      # 5 min between verdicts on same token
MAX_TRADE_SIZE_USD = 50     # max trade size for demo
