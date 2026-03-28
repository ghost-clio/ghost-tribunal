"""Ghost Tribunal — x402 Payment Gate

Implements HTTP 402 Payment Required flow for tribunal sessions.
Users pay a small fee (in USDC on X Layer) per tribunal session.
Revenue covers OpenRouter API costs, making the system self-sustaining.

Flow:
1. Client requests /api/submit without payment → gets 402 + payment instructions
2. Client signs a USDC transfer authorization
3. Client retries with X-PAYMENT header
4. Server verifies via CodeNut facilitator → runs tribunal → returns results
"""

import json
import logging
import os
from aiohttp import web, ClientSession

from config import (
    XLAYER_CHAIN_ID, TRIBUNAL_PRIVATE_KEY,
    XLAYER_NETWORK,
)

log = logging.getLogger("tribunal.x402")

# x402 config
FACILITATOR_URL = os.getenv("X402_FACILITATOR_URL", "https://facilitator.codenut.ai")
USDC_XLAYER = os.getenv("USDC_XLAYER_ADDRESS", "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbC035")  # USDC on X Layer
TRIBUNAL_FEE = os.getenv("TRIBUNAL_FEE", "0.01")  # $0.01 USDC per session
XLAYER_NETWORK_ID = f"xlayer-{'testnet' if XLAYER_NETWORK == 'testnet' else 'mainnet'}"

# Derive tribunal wallet address from private key
from web3 import Web3
w3 = Web3()
TRIBUNAL_ADDRESS = w3.eth.account.from_key(TRIBUNAL_PRIVATE_KEY).address if TRIBUNAL_PRIVATE_KEY else ""


# Track free runs per wallet (in-memory, resets on restart)
FREE_RUNS: dict[str, int] = {}
FREE_RUNS_PER_WALLET = 1


def payment_required_response(resource: str = "/api/submit") -> web.Response:
    """Return HTTP 402 with x402 payment instructions."""
    payment_details = {
        "x402Version": 1,
        "schemes": [{
            "scheme": "exact",
            "network": XLAYER_NETWORK_ID,
            "maxAmountRequired": TRIBUNAL_FEE,
            "resource": resource,
            "description": "Ghost Tribunal session — 4 AI agents analyze your token on-chain",
            "mimeType": "application/json",
            "payTo": TRIBUNAL_ADDRESS,
            "asset": USDC_XLAYER,
            "extra": {
                "name": "Ghost Tribunal",
                "agents": ["The Degen", "The Sentinel", "The Oracle", "The Quant"],
            }
        }],
    }

    return web.json_response(
        payment_details,
        status=402,
        headers={
            "X-Payment-Required": "true",
            "Access-Control-Expose-Headers": "X-Payment-Required",
        },
    )


async def verify_payment(payment_header: str) -> dict | None:
    """Verify x402 payment via CodeNut facilitator."""
    if not payment_header:
        return None

    try:
        async with ClientSession() as session:
            resp = await session.post(
                f"{FACILITATOR_URL}/verify",
                json={"payment": payment_header},
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            if resp.status == 200:
                return await resp.json()
            else:
                body = await resp.text()
                log.warning(f"Payment verification failed: {resp.status} {body[:200]}")
                return None
    except Exception as e:
        log.error(f"Payment verification error: {e}")
        return None


async def settle_payment(payment_header: str) -> dict | None:
    """Settle x402 payment via CodeNut facilitator."""
    try:
        async with ClientSession() as session:
            resp = await session.post(
                f"{FACILITATOR_URL}/settle",
                json={"payment": payment_header},
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            if resp.status == 200:
                result = await resp.json()
                log.info(f"Payment settled: {json.dumps(result)[:200]}")
                return result
            else:
                body = await resp.text()
                log.warning(f"Payment settlement failed: {resp.status} {body[:200]}")
                return None
    except Exception as e:
        log.error(f"Payment settlement error: {e}")
        return None


def has_payment(request: web.Request) -> str | None:
    """Extract X-PAYMENT header from request."""
    return request.headers.get("X-PAYMENT") or request.headers.get("x-payment")


# ── x402-gated submit handler ──────────────────────────────────────────

async def handle_paid_submit(request: web.Request) -> web.Response:
    """x402-gated tribunal submission.
    
    - No X-PAYMENT header → 402 Payment Required
    - Valid payment → verify → settle → run tribunal → return results
    - Free mode available via TRIBUNAL_FREE_MODE=1 env var
    """
    # Free mode for demos/testing
    if os.getenv("TRIBUNAL_FREE_MODE", "0") == "1":
        return None  # Skip to regular handler

    # Check for connected wallet address (sent by frontend)
    try:
        body = await request.clone().json()
    except Exception:
        body = {}
    wallet = (body.get("wallet") or "").lower().strip()

    # 1 free run per connected wallet
    if wallet and len(wallet) == 42 and wallet.startswith("0x"):
        used = FREE_RUNS.get(wallet, 0)
        if used < FREE_RUNS_PER_WALLET:
            FREE_RUNS[wallet] = used + 1
            remaining = FREE_RUNS_PER_WALLET - used - 1
            log.info(f"Free run for wallet {wallet} ({remaining} remaining)")
            return None  # Allow through — free run

    payment = has_payment(request)
    if not payment:
        resp = payment_required_response("/api/submit")
        # Add free run info to help frontend show the right UI
        return resp

    # Verify payment
    verification = await verify_payment(payment)
    if not verification:
        return web.json_response(
            {"error": "Payment verification failed"},
            status=402,
        )

    # Settle payment
    settlement = await settle_payment(payment)
    if not settlement:
        log.warning("Settlement failed but proceeding — verification passed")

    # Payment valid — return None to indicate the regular handler should proceed
    return None
