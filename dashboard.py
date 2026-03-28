#!/usr/bin/env python3
"""
Ghost Tribunal — Live Dashboard

Serves a web dashboard showing tribunal sessions, agent debates,
on-chain verdicts, and trade history in real-time.
"""

import json
import asyncio
import logging
from pathlib import Path
from aiohttp import web

log = logging.getLogger("tribunal.dashboard")

SESSIONS_FILE = Path("state/sessions.jsonl")
STATIC_DIR = Path("dashboard")


def load_sessions(limit=50) -> list[dict]:
    """Load recent tribunal sessions from log."""
    if not SESSIONS_FILE.exists():
        return []
    sessions = []
    for line in SESSIONS_FILE.read_text().strip().split("\n"):
        if line:
            try:
                sessions.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return sessions[-limit:]


async def handle_index(request):
    return web.FileResponse(STATIC_DIR / "index.html")


async def handle_api_sessions(request):
    sessions = load_sessions()
    return web.json_response(sessions)


async def handle_api_submit(request):
    """Submit a token for tribunal review (x402-gated)."""
    # x402 payment check
    from x402_gate import handle_paid_submit
    payment_response = await handle_paid_submit(request)
    if payment_response is not None:
        return payment_response

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    token_address = body.get("address", "").strip()
    token_name = body.get("name", "").strip() or "Unknown"

    if not token_address or len(token_address) < 10:
        return web.json_response({"error": "Invalid token address"}, status=400)

    # Check if tribunal is already running
    app = request.app
    if app.get("_tribunal_running"):
        return web.json_response({"error": "Tribunal session in progress, try again shortly"}, status=429)

    app["_tribunal_running"] = True

    try:
        import aiohttp as aio
        from tribunal import run_tribunal

        token_data = {
            "symbol": token_name.upper()[:6],
            "mcap": 0, "volume_24h": 0, "liquidity": 0,
            "price_change_1h": 0, "price_change_24h": 0,
            "holders": 0, "top10_pct": 0, "verified": False,
        }

        # Try to enrich with onchainos data
        from xlayer import get_token_info
        info = await get_token_info(token_address)
        if info and isinstance(info, dict):
            token_data.update({
                "symbol": info.get("tokenSymbol", token_data["symbol"]),
                "mcap": info.get("marketCap", 0) or 0,
                "holders": info.get("holders", 0) or 0,
            })
            token_name = info.get("tokenName", token_name)

        async with aio.ClientSession() as session:
            result = await run_tribunal(
                session,
                token_name=token_name,
                token_address=token_address,
                token_data=token_data,
                trend_info=body.get("context", ""),
            )

        return web.json_response({
            "status": "ok",
            "consensus": result.get("consensus", False),
            "buy_votes": result.get("buy_votes", 0),
            "tx_hashes": result.get("tx_hashes", []),
        })

    except Exception as e:
        log.error(f"Submit error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)
    finally:
        app["_tribunal_running"] = False


async def handle_api_stats(request):
    sessions = load_sessions(limit=500)
    total = len(sessions)
    buys = sum(1 for s in sessions if s.get("consensus"))
    passes = total - buys

    agent_records = {}
    for s in sessions:
        for v in s.get("verdicts", []):
            aid = v["agent"]
            if aid not in agent_records:
                agent_records[aid] = {"buys": 0, "passes": 0, "total": 0}
            agent_records[aid]["total"] += 1
            if v["verdict"] == "BUY":
                agent_records[aid]["buys"] += 1
            else:
                agent_records[aid]["passes"] += 1

    return web.json_response({
        "total_sessions": total,
        "consensus_buys": buys,
        "passes": passes,
        "agents": agent_records,
    })


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/api/sessions", handle_api_sessions)
    app.router.add_post("/api/submit", handle_api_submit)
    app.router.add_get("/api/stats", handle_api_stats)
    app.router.add_static("/static", STATIC_DIR / "static", name="static")
    return app


if __name__ == "__main__":
    STATIC_DIR.mkdir(exist_ok=True)
    (STATIC_DIR / "static").mkdir(exist_ok=True)
    app = create_app()
    log.info("Dashboard running at http://localhost:3000")
    web.run_app(app, host="0.0.0.0", port=3000)
