# 👻 Ghost Tribunal

**An AI Agent Council That Debates, Votes, and Trades On-Chain**

[![Try it live](https://img.shields.io/badge/🔗_Try_It_Live-ghost--tribunal-blueviolet?style=for-the-badge)](https://ghost-clio.github.io/ghost-tribunal)
[![X Layer](https://img.shields.io/badge/X_Layer-Mainnet-blue?style=flat-square)](https://www.okx.com/web3/explorer/xlayer)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

> Four AI agents with clashing personalities debate every token. Their verdicts are posted as immutable on-chain records. When 3 out of 4 agree — they execute.
>
> No black boxes. No hidden logic. Every decision public, permanent, and verifiable.

**[→ Live Demo](https://ghost-clio.github.io/ghost-tribunal)** · **[→ On-Chain Proof](https://www.okx.com/web3/explorer/xlayer/tx/0x5f59121eb7cfea5ddc81d28e903639eafa6e3ec6f451351ffa071ff241759d7a)** · **[→ Demo Video](https://github.com/ghost-clio/ghost-tribunal/releases/download/v1.0.0/ghost-tribunal.mp4)**

---

## Why This Exists

AI trading bots are black boxes. One model, one perspective, one hidden decision. You never know *why* it bought, *why* it passed, or what it missed.

Ghost Tribunal replaces the black box with a **public debate**:

- 4 AI agents argue from radically different perspectives
- Every verdict is written to X Layer as an immutable memo transaction
- Every decision is auditable — by anyone, forever
- Consensus (3/4) triggers execution via OKX DEX Aggregator

The result: an AI trading system where **trust is verifiable, not assumed**.

---

## The Four Agents

| | Agent | Perspective | What They Catch |
|---|-------|------------|-----------------|
| 🎰 | **The Degen** | Momentum & hype | Trends the Quant would ignore |
| 🛡️ | **The Sentinel** | Security & risk | Rugs the Degen would ape into |
| 🔮 | **The Oracle** | Narrative & culture | Stories the Quant can't quantify |
| 📊 | **The Quant** | Data & numbers | Value the Oracle would overlook |

Each agent has a distinct system prompt, bias, and analysis style. They don't collaborate — they **debate**. The Sentinel is paranoid by design. The Degen is impatient. The Oracle speaks in cultural currents. The Quant only sees numbers.

**The disagreement is the feature.**

When The Sentinel approves a BUY, it carries weight — because everyone knows how hard it is to convince.

---

## How It Works

```
Token Address Submitted
    ↓
Token Data Fetched (OKX OnchainOS — Market, Security, Token APIs)
    ↓
4 Agents Analyze Independently
    ↓
Each Verdict Posted On-Chain (X Layer memo transaction)
    ↓
Consensus Check (≥3 of 4 = BUY)
    ↓
Trade Execution (OKX DEX Aggregator, 500+ liquidity sources)
```

### Real On-Chain Verdict

Every verdict is a JSON memo embedded in a self-transfer on X Layer. Here's a real one from our xETH session:

```json
{
  "tribunal": "ghost",
  "agent": "The Sentinel",
  "token": "0x5a77f1443d16ee5761d310e38b7069f7dfdcd8d8",
  "verdict": "BUY",
  "reasoning": "Contract verified. Top 10 hold 2.8% — healthy distribution. $4M liquidity relative to $7.8M mcap is strong. No honeypot flags. Risk: 3/10",
  "ts": 1711584000
}
```

**Verify it yourself:** [View on X Layer Explorer →](https://www.okx.com/web3/explorer/xlayer/tx/0x5f59121eb7cfea5ddc81d28e903639eafa6e3ec6f451351ffa071ff241759d7a)

---

## Live Dashboard

**[→ ghost-clio.github.io/ghost-tribunal](https://ghost-clio.github.io/ghost-tribunal)**

Paste any X Layer token contract address. Get real AI verdicts in ~20 seconds.

- **Connect wallet** — 1 free tribunal session per wallet
- **Watch the deliberation** — animated progress as each agent analyzes
- **Read the reasoning** — every agent explains their verdict
- **Check consensus** — see if the tribunal would buy
- **Verify on-chain** — every past verdict links to X Layer Explorer

No sign-up. No API key. Just paste an address and summon the tribunal.

---

## x402: Self-Sustaining Economics

Ghost Tribunal uses the [x402 protocol](https://x402.org) to pay for itself:

```
First session  →  FREE (per connected wallet)
Every session after  →  $0.01 USDC via x402
```

The flow:

1. Client submits a token → server responds `402 Payment Required`
2. Client signs a USDC authorization (ERC-3009) in their wallet
3. Payment verified through [CodeNut facilitator](https://facilitator.codenut.ai) on X Layer
4. Tribunal runs → verdicts returned

No accounts. No subscriptions. No API keys. Just `402 → sign → pay → results`.

**Why it matters:** Each session costs ~$0.0001 in gas + $0 in AI inference (free-tier model). At $0.01/session, the tribunal is profitable from session #1 — a self-sustaining AI agent that funds its own compute.

---

## OKX OnchainOS Integration

| OnchainOS Capability | How Ghost Tribunal Uses It |
|---------------------|---------------------------|
| **Token API** | Discover and identify tokens on X Layer |
| **Security API** | Scan for honeypots, dev concentration, contract risks |
| **Market API** | Real-time price, volume, liquidity, and holder data |
| **DEX Aggregator** | Execute consensus trades across 500+ liquidity sources |
| **x402 Payments** | Per-session micropayments — users pay, tribunal runs |

The tribunal doesn't just *read* on-chain data — it **writes** to the chain. Every verdict becomes a permanent, auditable record that anyone can verify.

---

## Quick Start

```bash
git clone https://github.com/ghost-clio/ghost-tribunal.git
cd ghost-tribunal

pip install -r requirements.txt
cp .env.example .env
# Add your OPENROUTER_API_KEY and TRIBUNAL_PRIVATE_KEY

# Run a tribunal session on any X Layer token
python tribunal.py "WOKB" "0xe538905cf8410324e03a5a23c1c177a474d59b2b"

# Start the dashboard
python dashboard.py  # → http://localhost:3000

# Auto-monitor trending tokens
python watcher.py
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | AI model access via [OpenRouter](https://openrouter.ai) |
| `TRIBUNAL_PRIVATE_KEY` | ✅ | Wallet for posting verdict transactions |
| `XLAYER_NETWORK` | — | `mainnet` (default) or `testnet` |
| `AGENT_MODEL` | — | Default: `nvidia/nemotron-3-super-120b-a12b:free` |
| `TRIBUNAL_FREE_MODE` | — | `1` = skip x402 payment check |
| `DISCORD_WEBHOOK` | — | Post verdicts to Discord |

---

## Architecture

```
ghost-tribunal/
├── tribunal.py               # Orchestrator — queries agents, posts on-chain, checks consensus
├── agents.py                 # The Four — personalities, prompts, verdict parsing
├── xlayer.py                 # X Layer — on-chain txs, onchainos CLI, security scans
├── x402_gate.py              # Payment — HTTP 402 flow via CodeNut facilitator
├── watcher.py                # Trend detection — finds tokens, triggers tribunal
├── config.py                 # Configuration from .env
├── dashboard.py              # Local web server for self-hosted dashboard
├── dashboard/                # Frontend UI
│   ├── index.html
│   └── static/
│       ├── style.css
│       └── app.js
├── docs/                     # GitHub Pages — live public dashboard
└── supabase/functions/
    └── tribunal-session/     # Serverless API powering the live demo
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Inference** | Nemotron 120B (MoE, 12B active) via OpenRouter — $0/session |
| **Blockchain** | X Layer mainnet (Chain ID 196) |
| **On-Chain Ops** | OKX OnchainOS (Token, Security, Market, DEX APIs) |
| **Payments** | x402 protocol + CodeNut facilitator |
| **Frontend** | Static HTML/CSS/JS on GitHub Pages |
| **Backend** | Supabase Edge Functions (Deno) + Python (aiohttp) |
| **Smart Contracts** | Self-transfer memo transactions (verdict records) |

---

## Cost Economics

| Component | Cost per Session |
|-----------|-----------------|
| AI inference (4 × Nemotron 120B) | $0.00 |
| On-chain verdicts (4 memo txs) | ~$0.0001 |
| x402 revenue per session | +$0.01 |
| **Net margin** | **~$0.01** |

Profitable from session #1. No VC funding required.

---

## License

MIT
