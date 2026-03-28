"""Ghost Tribunal — X Layer On-Chain Operations via onchainos CLI"""

import asyncio
import json
import logging
import subprocess
import time
from pathlib import Path

from web3 import Web3

from config import (
    XLAYER_RPC, XLAYER_CHAIN_ID, TRIBUNAL_PRIVATE_KEY,
)

log = logging.getLogger("tribunal.xlayer")

# Web3 connection for posting verdict transactions
w3 = Web3(Web3.HTTPProvider(XLAYER_RPC))

ONCHAINOS = Path.home() / ".local" / "bin" / "onchainos"


def _run_onchainos(*args, timeout=30) -> dict | None:
    """Run an onchainos CLI command and parse JSON output."""
    cmd = [str(ONCHAINOS)] + list(args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            log.warning(f"onchainos {args[0]} failed: {result.stderr[:200]}")
            return None
        # Try to parse JSON from stdout
        text = result.stdout.strip()
        if text.startswith("{") or text.startswith("["):
            return json.loads(text)
        # Some commands output non-JSON
        return {"raw": text}
    except subprocess.TimeoutExpired:
        log.error(f"onchainos {args[0]} timed out")
        return None
    except json.JSONDecodeError:
        return {"raw": result.stdout.strip()}
    except FileNotFoundError:
        log.error("onchainos CLI not found. Run: curl -sSL https://raw.githubusercontent.com/okx/onchainos-skills/main/install.sh | sh")
        return None
    except Exception as e:
        log.error(f"onchainos error: {e}")
        return None


async def _run_onchainos_async(*args, timeout=30) -> dict | None:
    """Async wrapper for onchainos CLI."""
    return await asyncio.get_event_loop().run_in_executor(
        None, lambda: _run_onchainos(*args, timeout=timeout)
    )


# ── On-Chain: Post Verdict ──────────────────────────────────────────────────

async def post_verdict_onchain(agent_name: str, token: str, verdict: str, reasoning: str) -> str | None:
    """Post an agent verdict as an on-chain memo transaction on X Layer.

    Returns the transaction hash or None on failure.
    """
    if not TRIBUNAL_PRIVATE_KEY:
        log.warning("No private key configured, skipping on-chain post")
        return None

    try:
        account = w3.eth.account.from_key(TRIBUNAL_PRIVATE_KEY)

        # Encode verdict as hex data
        memo = json.dumps({
            "tribunal": "ghost",
            "agent": agent_name,
            "token": token,
            "verdict": verdict,
            "reasoning": reasoning[:200],
            "ts": int(time.time()),
        })
        data = w3.to_hex(text=memo)

        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price

        tx = {
            "nonce": nonce,
            "to": account.address,  # self-transfer with data
            "value": 0,
            "gas": 100_000,
            "gasPrice": gas_price,
            "chainId": XLAYER_CHAIN_ID,
            "data": data,
        }

        signed = w3.eth.account.sign_transaction(tx, TRIBUNAL_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        hex_hash = tx_hash.hex()

        log.info(f"Verdict posted on-chain: {agent_name} → {verdict} | tx: {hex_hash}")
        return hex_hash

    except Exception as e:
        log.error(f"On-chain post failed: {e}")
        return None


# ── Token Search ─────────────────────────────────────────────────────────────

async def search_token(query: str) -> list[dict]:
    """Search for tokens on X Layer via onchainos CLI."""
    result = await _run_onchainos_async(
        "token", "search", "--query", query, "--chains", "196"
    )
    if result and isinstance(result, list):
        return result
    if result and isinstance(result, dict) and "data" in result:
        return result["data"] if isinstance(result["data"], list) else [result["data"]]
    return []


async def get_token_info(token_address: str) -> dict | None:
    """Get detailed token info from onchainos."""
    result = await _run_onchainos_async(
        "token", "info", "--address", token_address.lower(), "--chain", "xlayer"
    )
    return result


async def get_token_price(token_address: str) -> dict | None:
    """Get token price from onchainos."""
    result = await _run_onchainos_async(
        "market", "price", "--address", token_address.lower(), "--chain", "xlayer"
    )
    return result


# ── Security Scanning ────────────────────────────────────────────────────────

async def scan_token_security(token_address: str) -> dict | None:
    """Run security scan via onchainos CLI."""
    result = await _run_onchainos_async(
        "security", "token-scan", "--tokens", f"196:{token_address.lower()}"
    )
    return result


# ── DEX Swap ─────────────────────────────────────────────────────────────────

async def get_swap_quote(from_token: str, to_token: str, amount: str) -> dict | None:
    """Get swap quote via onchainos CLI."""
    result = await _run_onchainos_async(
        "swap", "quote",
        "--from", from_token.lower(),
        "--to", to_token.lower(),
        "--amount", amount,
        "--chain", "xlayer",
    )
    return result


async def execute_swap(
    from_token: str, to_token: str, amount: str, wallet: str
) -> dict | None:
    """Execute swap via onchainos CLI."""
    result = await _run_onchainos_async(
        "swap", "execute",
        "--from", from_token.lower(),
        "--to", to_token.lower(),
        "--amount", amount,
        "--chain", "xlayer",
        "--wallet", wallet.lower(),
        timeout=60,
    )
    return result
