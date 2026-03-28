# Ghost Tribunal — Project Context

## What This Is
X Layer Onchain OS AI Hackathon submission. An AI agent council (4 agents with distinct personalities) that debates token opportunities, posts verdicts on-chain on X Layer, and executes trades on consensus.

## Status
Core code built and tested. On-chain verdicts verified on testnet.

### Done:
- ✅ 4 AI agents with distinct personalities
- ✅ On-chain verdict posting (testnet TX: 972083dd...e69eb81a)
- ✅ Testnet wallet funded (0.2 OKB)
- ✅ Dashboard with live session view
- ✅ x402 payment gate (CodeNut facilitator on X Layer)
- ✅ Trend watcher (X trending → token matching)
- ✅ All imports verified clean

### Needs:
1. OpenRouter API key with credits ($5-10) — set OPENROUTER_API_KEY in .env
2. Mainnet OKB for gas (testnet verified, mainnet needed for submission)
3. Demo video / screenshots
4. OKX API keys (optional — for enhanced token data)

## Architecture
- `tribunal.py` — main orchestrator. Runs 4 agents in parallel via OpenRouter, posts verdicts as on-chain memos (X Layer txs), executes DEX swap on 3/4 consensus
- `agents.py` — The Degen (momentum), The Sentinel (security), The Oracle (narrative), The Quant (data). Each has a system prompt and returns BUY/PASS/etc.
- `xlayer.py` — X Layer ops via onchainos CLI + web3.py for verdict txs
- `watcher.py` — trend detection (X trending via trends24.in) → token matching on X Layer → auto-tribunal
- `dashboard.py` — web dashboard on port 3000. Submit tokens, watch debates live, see on-chain tx links
- `dashboard/` — frontend (dark terminal aesthetic, auto-refresh)
- `config.py` — all settings, reads from .env

## Key Files
- `.env.example` — copy to `.env` and fill in keys
- `state/sessions.jsonl` — tribunal session log (created at runtime)
- `state/tribunal.log` — runtime log

## Hackathon Requirements & Submission Checklist

**X Layer Onchain OS AI Hackathon — Phase 1**
- Prize pool: 50K USDT — 1st: 12K, 2nd: 4K x3, 3rd: 800 x20
- Special prizes (2K each): Most Innovative, Best Agentic Payments, Highest Real-World Adoption, X Layer Integration, Community Favorite
- Deadline: EXTENDED — submissions due March 28, 2026

**Qualification:**
- [ ] Build on X Layer ecosystem
- [ ] Complete at least 1 transaction on X Layer, submit tx hash as proof
- [ ] Open-source project code on GitHub public repo
- [ ] Bonus: integrate x402 payments
- [ ] Bonus: use OnchainOS skills

**To Submit:**
1. [ ] Create a new X (Twitter) account for the project
2. [ ] Reply to this thread with intro, demo video, and GitHub link: https://x.com/xlayerofficial/status/2032064684078350355
3. [ ] Fill out registration form: https://forms.gle/BgBD4SuvJ7936F...  (Google Form: "X Layer Onchain OS AI Hackathon Project Submission")

**Judging Criteria:**
- How deeply AI agents are integrated on-chain
- Autonomous agent payment flow within X Layer ecosystem
- Architecture for collaboration between multiple agents
- Overall impact on X Layer ecosystem

**Use Case Categories:**
1. Agentic Payments (x402, subscriptions, paid access) ← we target this
2. AI Agent Playground (social forums, AI vs AI, token launch)
3. AI DeFi/Trading (autonomous trading, portfolio, arbitrage)

**Key Links:**
- X Layer RPC docs: https://web3.okx.com/xlayer/docs/developer/rpc-endpoints/rpc-endpoints
- OnchainOS Skills repo: https://github.com/okx/onchainos-skills
- OKX Dev Portal (API keys): https://web3.okx.com/onchain-os/dev-portal
- X Layer Explorer: https://www.okx.com/web3/explorer/xlayer
- Hackathon announcement thread: https://x.com/xlayerofficial/status/2032064684078350355

## Model
Uses OpenRouter (default: google/gemini-2.5-flash). Change AGENT_MODEL in .env. Each tribunal session = 4 short API calls (~$0.001 total with flash).

## Business Model
Users pay x402 on X Layer to submit tokens for review → fees fund OpenRouter credits → agents deliberate → verdicts posted on-chain. Self-sustaining.
