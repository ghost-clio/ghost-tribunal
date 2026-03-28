#!/usr/bin/env python3
"""
Ghost Tribunal — Trend Watcher

Monitors trending topics and matches them to X Layer tokens.
When a match is found, triggers a tribunal session.

Sources: X Trending (trends24.in), Wikipedia spikes
"""

import asyncio
import json
import logging
import re
import time
from pathlib import Path

import aiohttp

from config import XLAYER_CHAIN_INDEX, OKX_BASE_URL
from xlayer import _okx_headers, search_token
from tribunal import run_tribunal

log = logging.getLogger("tribunal.watcher")

POLL_INTERVAL = 300  # 5 min
STATE_FILE = Path("state/watcher_state.json")


class WatcherState:
    def __init__(self):
        self.seen_trends: set[str] = set()
        self.load()

    def load(self):
        if STATE_FILE.exists():
            try:
                d = json.loads(STATE_FILE.read_text())
                self.seen_trends = set(d.get("seen_trends", []))
            except Exception:
                pass

    def save(self):
        STATE_FILE.parent.mkdir(exist_ok=True)
        STATE_FILE.write_text(json.dumps({
            "seen_trends": list(self.seen_trends)[-200],
        }))

    def is_new(self, trend: str) -> bool:
        key = trend.lower().strip()
        if key in self.seen_trends:
            return False
        self.seen_trends.add(key)
        return True


state = WatcherState()


async def fetch_x_trending(session: aiohttp.ClientSession) -> list[str]:
    """Scrape X trending from trends24.in."""
    try:
        async with session.get(
            "https://trends24.in/united-states/",
            headers={"User-Agent": "Mozilla/5.0 (GhostTribunal/1.0)"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as r:
            if r.status != 200:
                return []
            html = await r.text()
    except Exception as e:
        log.error(f"X trends error: {e}")
        return []

    topics = re.findall(r'<a[^>]*href="https://(?:twitter|x)\.com/search[^"]*"[^>]*>([^<]+)</a>', html)
    topics += re.findall(r'class="trend-card__name[^"]*"[^>]*>([^<]+)<', html)

    seen = set()
    clean = []
    for t in topics:
        t = t.strip()
        key = t.lower()
        if not t or len(t) < 3 or key in seen:
            continue
        seen.add(key)
        clean.append(t)

    return clean[:20]


async def match_trend_to_xlayer_token(
    session: aiohttp.ClientSession, trend: str
) -> dict | None:
    """Check if a trending topic matches any token on X Layer."""
    results = await search_token(session, trend)
    if results:
        token = results[0]
        return {
            "name": token.get("tokenName", trend),
            "symbol": token.get("tokenSymbol", "?"),
            "address": token.get("tokenContractAddress", ""),
            "decimals": token.get("decimals", 18),
        }
    return None


async def watch_loop():
    """Main watch loop: detect trends → match to X Layer tokens → tribunal."""
    log.info("Ghost Tribunal Watcher starting...")
    log.info(f"Poll interval: {POLL_INTERVAL}s")

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                trends = await fetch_x_trending(session)
                new_trends = [t for t in trends if state.is_new(t)]

                if new_trends:
                    log.info(f"New trends: {len(new_trends)}")
                    for trend in new_trends[:5]:  # max 5 per cycle
                        match = await match_trend_to_xlayer_token(session, trend)
                        if match and match["address"]:
                            log.info(f"MATCH: '{trend}' → {match['name']} ({match['symbol']})")
                            token_data = {
                                "symbol": match["symbol"],
                                "mcap": 0,
                                "volume_24h": 0,
                                "liquidity": 0,
                                "price_change_1h": 0,
                                "price_change_24h": 0,
                                "holders": 0,
                                "top10_pct": 0,
                                "verified": False,
                            }
                            await run_tribunal(
                                session,
                                token_name=match["name"],
                                token_address=match["address"],
                                token_data=token_data,
                                trend_info=f"Trending on X: '{trend}'",
                            )
                            await asyncio.sleep(5)  # rate limit

                state.save()

            except Exception as e:
                log.error(f"Watch loop error: {e}", exc_info=True)

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(watch_loop())
