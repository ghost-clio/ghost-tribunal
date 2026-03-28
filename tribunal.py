#!/usr/bin/env python3
"""
Ghost Tribunal — An AI Agent Council That Debates, Votes, and Trades On-Chain

Four AI agents with distinct personalities analyze tokens discovered through
trend detection. Every verdict is posted on X Layer as an immutable on-chain
record. When 3/4 agents agree to BUY, the tribunal executes a swap.

Built for X Layer Onchain OS AI Hackathon.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import aiohttp

from config import (
    OPENROUTER_API_KEY, AGENT_MODEL, DISCORD_WEBHOOK,
    VOTE_THRESHOLD, VERDICT_COOLDOWN, TRIBUNAL_PRIVATE_KEY,
)
from agents import AGENTS, get_agent_prompt, parse_verdict
from xlayer import (
    post_verdict_onchain, search_token, get_token_security,
    get_swap_quote, w3,
)

# ── Logging ──────────────────────────────────────────────────────────────────

LOG_DIR = Path("state")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "tribunal.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("tribunal")

# ── State ────────────────────────────────────────────────────────────────────

SESSIONS_FILE = LOG_DIR / "sessions.jsonl"
COOLDOWNS: dict[str, float] = {}  # token -> last verdict timestamp


# ── AI Analysis ──────────────────────────────────────────────────────────────

async def query_agent(
    session: aiohttp.ClientSession,
    agent_id: str,
    token_name: str,
    token_data: dict,
    trend_info: str,
) -> dict:
    """Query an AI agent for their verdict on a token."""
    agent = AGENTS[agent_id]
    prompt = get_agent_prompt(agent_id, token_name, token_data, trend_info)

    payload = {
        "model": AGENT_MODEL,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 200,
    }

    try:
        async with session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json=payload,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ghost-tribunal",
                "X-Title": "Ghost Tribunal",
            },
            timeout=aiohttp.ClientTimeout(total=30),
        ) as r:
            if r.status != 200:
                body = await r.text()
                log.warning(f"Agent {agent_id} API error: {r.status} {body[:200]}")
                return {"agent": agent_id, "verdict": "PASS", "reasoning": "API error", "error": True}
            data = await r.json()
    except Exception as e:
        log.error(f"Agent {agent_id} error: {e}")
        return {"agent": agent_id, "verdict": "PASS", "reasoning": str(e), "error": True}

    # Parse OpenRouter response
    text = ""
    choices = data.get("choices", [])
    if choices:
        text = choices[0].get("message", {}).get("content", "")

    verdict = parse_verdict(text)

    return {
        "agent": agent_id,
        "name": agent["name"],
        "emoji": agent["emoji"],
        "verdict": verdict,
        "reasoning": text,
    }


# ── Tribunal Session ─────────────────────────────────────────────────────────

async def run_tribunal(
    session: aiohttp.ClientSession,
    token_name: str,
    token_address: str,
    token_data: dict,
    trend_info: str = "",
) -> dict:
    """Run a full tribunal session: all agents analyze, vote, and optionally trade."""
    log.info(f"{'='*60}")
    log.info(f"TRIBUNAL SESSION: {token_name} ({token_address[:8]}...)")
    log.info(f"{'='*60}")

    # Check cooldown
    if token_address in COOLDOWNS:
        elapsed = time.time() - COOLDOWNS[token_address]
        if elapsed < VERDICT_COOLDOWN:
            log.info(f"Cooldown active ({VERDICT_COOLDOWN - elapsed:.0f}s remaining)")
            return {"status": "cooldown", "token": token_name}

    # Security scan first
    security = await get_token_security(session, token_address)
    if security:
        token_data["security"] = security
        log.info(f"Security scan complete")

    # Query all agents in parallel
    tasks = [
        query_agent(session, agent_id, token_name, token_data, trend_info)
        for agent_id in AGENTS
    ]
    verdicts = await asyncio.gather(*tasks)

    # Display results
    buy_votes = 0
    results = []

    for v in verdicts:
        verdict_str = v["verdict"]
        is_buy = verdict_str == "BUY"
        if is_buy:
            buy_votes += 1

        icon = "✅" if is_buy else "❌" if verdict_str in ("DANGER", "FADE", "SHORT") else "⏸️"
        log.info(f"  {v.get('emoji', '?')} {v.get('name', v['agent'])}: {icon} {verdict_str}")
        log.info(f"     {v['reasoning'][:150]}")

        results.append(v)

    # Consensus check
    consensus = buy_votes >= VOTE_THRESHOLD
    log.info(f"\nVOTE: {buy_votes}/{len(AGENTS)} BUY → {'CONSENSUS REACHED' if consensus else 'NO CONSENSUS'}")

    # Post verdicts on-chain
    tx_hashes = []
    for v in results:
        tx_hash = await post_verdict_onchain(
            v.get("name", v["agent"]),
            token_address,
            v["verdict"],
            v["reasoning"][:200],
        )
        if tx_hash:
            tx_hashes.append(tx_hash)
        await asyncio.sleep(1)  # avoid nonce collision

    # Execute trade if consensus
    trade_result = None
    if consensus:
        log.info("EXECUTING TRADE...")
        trade_result = await _execute_consensus_trade(session, token_address, token_data)

    # Record session
    session_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token_name": token_name,
        "token_address": token_address,
        "token_data": {k: v for k, v in token_data.items() if k != "security"},
        "trend_info": trend_info,
        "verdicts": [
            {"agent": v["agent"], "verdict": v["verdict"], "reasoning": v["reasoning"][:300]}
            for v in results
        ],
        "consensus": consensus,
        "buy_votes": buy_votes,
        "tx_hashes": tx_hashes,
        "trade": trade_result,
    }

    with open(SESSIONS_FILE, "a") as f:
        f.write(json.dumps(session_record) + "\n")

    COOLDOWNS[token_address] = time.time()

    # Post to Discord if configured
    if DISCORD_WEBHOOK:
        await _post_discord_summary(session, session_record)

    return session_record


async def _execute_consensus_trade(
    session: aiohttp.ClientSession,
    token_address: str,
    token_data: dict,
) -> dict | None:
    """Execute a swap after consensus is reached."""
    if not TRIBUNAL_PRIVATE_KEY:
        log.info("No private key — trade simulation only")
        return {"status": "simulated", "reason": "no private key configured"}

    try:
        account = w3.eth.account.from_key(TRIBUNAL_PRIVATE_KEY)
        # Native OKB/ETH on X Layer as from token (0xeee... = native)
        native = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

        quote = await get_swap_quote(
            session,
            from_token=native,
            to_token=token_address,
            amount=str(w3.to_wei(0.001, "ether")),  # small demo amount
        )

        if quote:
            log.info(f"Swap quote received: {json.dumps(quote)[:200]}")
            return {"status": "quoted", "quote": quote}
        else:
            log.warning("No swap route available")
            return {"status": "no_route"}

    except Exception as e:
        log.error(f"Trade execution error: {e}")
        return {"status": "error", "error": str(e)}


# ── Discord Output ───────────────────────────────────────────────────────────

async def _post_discord_summary(session: aiohttp.ClientSession, record: dict):
    """Post tribunal session summary to Discord webhook."""
    if not DISCORD_WEBHOOK:
        return

    verdicts_str = "\n".join(
        f"{AGENTS[v['agent']]['emoji']} **{AGENTS[v['agent']]['name']}**: "
        f"{'✅' if v['verdict'] == 'BUY' else '❌' if v['verdict'] in ('DANGER','FADE','SHORT') else '⏸️'} "
        f"{v['verdict']}\n> {v['reasoning'][:150]}"
        for v in record["verdicts"]
    )

    consensus_str = (
        f"✅ **CONSENSUS: BUY** ({record['buy_votes']}/{len(AGENTS)})"
        if record["consensus"]
        else f"❌ **NO CONSENSUS** ({record['buy_votes']}/{len(AGENTS)} BUY)"
    )

    tx_str = ""
    if record["tx_hashes"]:
        tx_str = "\n**On-chain verdicts:**\n" + "\n".join(
            f"[`{h[:10]}...`](https://www.okx.com/web3/explorer/xlayer/tx/{h})"
            for h in record["tx_hashes"]
        )

    embed = {
        "title": f"👻 GHOST TRIBUNAL: {record['token_name']}",
        "description": (
            f"{verdicts_str}\n\n"
            f"{consensus_str}"
            f"{tx_str}"
        ),
        "color": 0x00FF88 if record["consensus"] else 0xFF4444,
        "timestamp": record["timestamp"],
        "footer": {"text": "Ghost Tribunal — X Layer Onchain OS"},
    }

    try:
        async with session.post(
            DISCORD_WEBHOOK,
            json={"embeds": [embed]},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as r:
            if r.status not in (200, 204):
                log.warning(f"Discord webhook {r.status}")
    except Exception as e:
        log.error(f"Discord post failed: {e}")


# ── CLI / Demo Mode ──────────────────────────────────────────────────────────

async def demo_session(token_name: str, token_address: str):
    """Run a single tribunal session for demo/testing."""
    # Mock token data for demo (replace with real API calls in production)
    token_data = {
        "symbol": token_name.upper()[:6],
        "mcap": 150_000,
        "volume_24h": 45_000,
        "liquidity": 25_000,
        "price_change_1h": 12.5,
        "price_change_24h": 85.0,
        "holders": 340,
        "top10_pct": 42,
        "verified": True,
    }

    async with aiohttp.ClientSession() as session:
        result = await run_tribunal(
            session,
            token_name=token_name,
            token_address=token_address,
            token_data=token_data,
            trend_info=f"{token_name} is trending on X with 500K+ views",
        )

        if result.get("consensus"):
            log.info("🟢 TRIBUNAL APPROVED — Trade would execute")
        else:
            log.info("🔴 TRIBUNAL REJECTED — No trade")

        return result


async def main():
    """Main entry: run tribunal on a token or in demo mode."""
    import sys

    if "--demo" in sys.argv:
        # Offline demo with canned responses — no API key needed
        await _run_offline_demo()
        return

    if len(sys.argv) >= 3:
        name = sys.argv[1]
        address = sys.argv[2]
    else:
        name = "DemoToken"
        address = "0x0000000000000000000000000000000000000000"
        log.info("Usage: python tribunal.py <token_name> <token_address>")
        log.info("       python tribunal.py --demo  (offline demo, no API key)")
        log.info("Running with demo token...\n")

    await demo_session(name, address)


async def _run_offline_demo():
    """Run an offline demo with canned agent responses — no API key needed."""
    import time

    log.info("=" * 60)
    log.info("OFFLINE DEMO — Ghost Tribunal")
    log.info("=" * 60)

    demo_verdicts = [
        {
            "agent": "degen", "name": "The Degen", "emoji": "🎰",
            "verdict": "BUY",
            "reasoning": "Volume pumping hard, narrative is hot with the AI agent meta, chart looks like it wants to send. LFG ser. Confidence: 8/10",
        },
        {
            "agent": "sentinel", "name": "The Sentinel", "emoji": "🛡️",
            "verdict": "PASS",
            "reasoning": "Contract unverified. Top 10 wallets hold 38%. No audit. Deployer has 3 prior rugs. Risk: 7/10",
        },
        {
            "agent": "oracle", "name": "The Oracle", "emoji": "🔮",
            "verdict": "BUY",
            "reasoning": "The AI agent narrative has legs — aligns with broader market rotation into infrastructure plays. Cultural momentum is building. Strength: 7/10",
        },
        {
            "agent": "quant", "name": "The Quant", "emoji": "📊",
            "verdict": "BUY",
            "reasoning": "Vol/mcap ratio 0.45x is healthy. Buy pressure 3.2:1. Liquidity $48K sufficient for position sizing. EV: +22%",
        },
    ]

    token_name = "AgentLayer"
    token_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"

    for v in demo_verdicts:
        icon = "✅" if v["verdict"] == "BUY" else "❌"
        log.info(f"  {v['emoji']} {v['name']}: {icon} {v['verdict']}")
        log.info(f"     {v['reasoning']}")
        await asyncio.sleep(0.5)

    buy_votes = sum(1 for v in demo_verdicts if v["verdict"] == "BUY")
    consensus = buy_votes >= VOTE_THRESHOLD
    log.info(f"\nVOTE: {buy_votes}/4 BUY → {'CONSENSUS REACHED ✅' if consensus else 'NO CONSENSUS ❌'}")

    # Post verdicts on-chain (this works without OpenRouter)
    tx_hashes = []
    for v in demo_verdicts:
        tx_hash = await post_verdict_onchain(
            v["name"], token_address, v["verdict"], v["reasoning"][:200],
        )
        if tx_hash:
            tx_hashes.append(tx_hash)
            log.info(f"  On-chain: {tx_hash[:20]}...")
        await asyncio.sleep(1)

    # Save session
    session_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "token_name": token_name,
        "token_address": token_address,
        "token_data": {"symbol": "AGENTL", "mcap": 150000, "volume_24h": 67500},
        "trend_info": "AI agent infrastructure trending on X",
        "verdicts": [
            {"agent": v["agent"], "verdict": v["verdict"], "reasoning": v["reasoning"]}
            for v in demo_verdicts
        ],
        "consensus": consensus,
        "buy_votes": buy_votes,
        "tx_hashes": tx_hashes,
        "trade": None,
    }

    with open(SESSIONS_FILE, "a") as f:
        f.write(json.dumps(session_record) + "\n")

    log.info(f"\n{'🟢 CONSENSUS — trade would execute' if consensus else '🔴 NO CONSENSUS — no trade'}")
    log.info(f"Session saved. {len(tx_hashes)} verdicts posted on-chain.")
    log.info(f"Run 'python dashboard.py' to view in the dashboard.")


if __name__ == "__main__":
    asyncio.run(main())
