# 👻 Ghost Tribunal

**An AI Agent Council That Debates, Votes, and Trades Narratives On-Chain**

> Four AI agents. Four perspectives. One verdict — recorded forever on X Layer.

---

## The Problem

AI trading bots are black boxes. One model, one perspective, one hidden decision. You never know why it bought, why it passed, or what it missed.

## The Solution

Ghost Tribunal replaces the black box with a **public debate**. Four AI agents with distinct personalities analyze every token from different angles. Their verdicts are posted as **immutable on-chain records** on X Layer. When 3 out of 4 agree, the tribunal executes.

Every decision is transparent. Every vote costs something. Every trade has a public audit trail.

## The Agents

| Agent | Role | Personality |
|-------|------|-------------|
| 🎰 **The Degen** | Momentum & hype | Aggressive, apes first, speaks in crypto slang |
| 🛡️ **The Sentinel** | Security & risk | Paranoid, assumes everything is a rug |
| 🔮 **The Oracle** | Narrative & culture | Reads cultural currents, checks viral velocity |
| 📊 **The Quant** | Data & numbers | Cold, only cares about the math |

### Why Multi-Agent?

Single-agent trading bots have one perspective and one failure mode. Ghost Tribunal's four agents catch what any individual would miss:

- The Degen spots momentum the Quant would ignore
- The Sentinel catches rugs the Degen would ape into
- The Oracle identifies narratives the Quant can't quantify
- The Quant finds value the Oracle would overlook

**The debate IS the alpha.**

## How It Works

```
Trend Detected
    → Token Matched on X Layer
        → Security Scan (OKX OnchainOS)
            → 4 Agents Analyze in Parallel
                → Verdicts Posted On-Chain (memo txs)
                    → Consensus Vote (3/4 required)
                        → Trade Execution (OKX DEX Aggregator)
```

### On-Chain Verdicts

Every agent verdict is encoded as a JSON memo in a self-transfer transaction on X Layer:

```json
{
  "tribunal": "ghost",
  "agent": "The Sentinel",
  "token": "0x...",
  "verdict": "DANGER",
  "reasoning": "Unverified contract. Top 10 hold 42%. Risk: 8/10",
  "ts": 1711584000
}
```

These are **permanent, verifiable records** — anyone can decode the transaction data on [X Layer Explorer](https://www.okx.com/web3/explorer/xlayer) and see exactly what each agent thought and why.

## x402 Payment Integration

Ghost Tribunal uses the [x402 protocol](https://x402.org) for **self-sustaining economics**:

- Users submit tokens for review → pay a micro-fee in USDC via x402
- Payment is verified through the [CodeNut facilitator](https://facilitator.codenut.ai) on X Layer
- Revenue covers AI inference costs (OpenRouter API)
- No accounts, no subscriptions — just `HTTP 402 → sign → pay → results`

This creates a **flywheel**: usage funds AI costs, which powers more sessions, which generates more on-chain data. The tribunal pays for itself.

```
Client: POST /api/submit
Server: 402 Payment Required (USDC on X Layer)
Client: Signs ERC-3009 authorization
Client: POST /api/submit + X-PAYMENT header
Server: Verifies → Runs tribunal → Returns results
```

Set `TRIBUNAL_FREE_MODE=1` for demos and testing.

## Live Dashboard

**🔗 [ghost-clio.github.io/ghost-tribunal](https://ghost-clio.github.io/ghost-tribunal)** — paste any X Layer token address and get real AI verdicts.

The dashboard shows tribunal sessions with a dark terminal aesthetic:

- **Submit tokens** for tribunal review directly from the UI
- **Agent verdicts** with reasoning — see what each agent thought
- **Consensus results** (BUY / PASS) with vote counts
- **On-chain links** to X Layer Explorer for every verdict
- **Agent stats** — track each agent's bullish rate over time
- Auto-refreshes every 10 seconds

```bash
python dashboard.py  # → http://localhost:3000
```

## OKX OnchainOS Integration

| OnchainOS API | Usage in Ghost Tribunal |
|---------------|------------------------|
| **Token API** | Search and discover tokens on X Layer |
| **Security API** | Scan for rugs, honeypots, dev wallet concentration |
| **Market API** | Real-time price, volume, and liquidity data |
| **DEX Aggregator** | Execute consensus swaps across 500+ sources |
| **x402 Payments** | Pay-per-session micropayments for AI inference |

## Quick Start

```bash
# Clone
git clone https://github.com/ghost-clio/ghost-tribunal.git
cd ghost-tribunal

# Install deps
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env: add OPENROUTER_API_KEY

# Run a single tribunal session
python tribunal.py "TokenName" "0xTokenAddress"

# Run the live dashboard
python dashboard.py
# → http://localhost:3000

# Run the trend watcher (continuous monitoring)
python watcher.py
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | AI inference (Nemotron 120B via OpenRouter) |
| `TRIBUNAL_PRIVATE_KEY` | ✅ | Wallet for on-chain verdict txs |
| `XLAYER_NETWORK` | — | `mainnet` (default) or `testnet` |
| `TRIBUNAL_FREE_MODE` | — | Set to `1` to skip x402 payment |
| `AGENT_MODEL` | — | Default: `nvidia/nemotron-3-super-120b-a12b` |
| `DISCORD_WEBHOOK` | — | Post results to Discord |
| `OKX_API_KEY` | — | OnchainOS API access |

## Architecture

```
ghost-tribunal/
├── tribunal.py      # Core orchestrator — runs 4 agents, posts verdicts on-chain
├── agents.py        # Agent definitions — personalities, prompts, verdict parsing
├── xlayer.py        # X Layer ops — on-chain txs, token search, security scan, DEX
├── x402_gate.py     # x402 payment gate — HTTP 402 flow via CodeNut facilitator
├── watcher.py       # Trend detection — X trending → token matching → auto-tribunal
├── dashboard.py     # Web dashboard — submit tokens, view sessions, agent stats
├── dashboard/       # Frontend — dark terminal UI, auto-refresh
│   ├── index.html
│   └── static/
│       ├── style.css
│       └── app.js
└── config.py        # All configuration, reads from .env
```

## Tech Stack

- **Python** — async orchestration with aiohttp
- **X Layer** (Chain ID 196) — on-chain verdict records
- **OKX OnchainOS** — token discovery, security scanning, DEX aggregation
- **x402 + CodeNut** — pay-per-session micropayments
- **Nemotron 120B** (via OpenRouter) — AI agent inference (~$0/session (free model))
- **web3.py** — on-chain transaction posting

## Cost Economics

| Component | Cost per Session |
|-----------|-----------------|
| AI inference (4 agents × Nemotron 120B) | $0 (free tier) |
| On-chain verdicts (4 memo txs) | ~$0.0001 gas |
| x402 fee charged to user | $0.01 |
| **Net margin per session** | **~$0.01** |

The system is profitable from session #1.

## License

MIT
