# Ghost Tribunal

**An AI Agent Council That Debates, Votes, and Trades Narratives On-Chain**

> Four AI agents. Four perspectives. One verdict — recorded forever on X Layer.

## What Is This?

Ghost Tribunal is a multi-agent trading council built on X Layer. Instead of a single AI making trading decisions in a black box, four agents with distinct personalities publicly debate every opportunity. Their verdicts are posted as immutable on-chain records. When 3 out of 4 agree, the tribunal executes.

Every decision is transparent. Every vote costs something. Every trade has a public audit trail.

## The Agents

| Agent | Role | Style |
|-------|------|-------|
| 🎰 **The Degen** | Momentum & hype | Aggressive, apes first, speaks in crypto slang |
| 🛡️ **The Sentinel** | Security & risk | Paranoid, assumes everything is a rug |
| 🔮 **The Oracle** | Narrative & culture | Reads cultural currents, checks viral velocity |
| 📊 **The Quant** | Data & numbers | Cold, only cares about the math |

## How It Works

```
Trend Detected → Token Matched on X Layer → 4 Agents Analyze → Verdicts Posted On-Chain → Vote → Trade
```

1. **Trend Watcher** monitors X/Twitter trending topics in real-time
2. **Token Matcher** checks if any X Layer token matches the trend (via OKX OnchainOS Token API)
3. **Security Scanner** runs risk analysis (via OKX OnchainOS Security API)
4. **Four Agents** each analyze from their perspective using AI (Grok)
5. **On-Chain Verdicts** — each verdict is posted as a transaction on X Layer with memo data
6. **Consensus Vote** — 3/4 must agree to BUY
7. **Trade Execution** — swap via OKX DEX Aggregator on X Layer

## Architecture

```
┌─────────────────┐     ┌──────────────────┐
│  Trend Watcher   │────▶│  Token Matcher    │
│  (X Trending)    │     │  (OKX Token API)  │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    GHOST TRIBUNAL        │
                    │                          │
                    │  🎰 Degen    🛡️ Sentinel │
                    │  🔮 Oracle   📊 Quant    │
                    │                          │
                    │  Each posts verdict      │
                    │  ON-CHAIN (X Layer tx)   │
                    └────────────┬────────────┘
                                 │
                         ┌───────▼───────┐
                         │  3/4 agree?   │
                         └───┬───────┬───┘
                          YES│       │NO
                    ┌────────▼──┐ ┌──▼────────┐
                    │ DEX Swap  │ │  Log only  │
                    │ (OKX DEX) │ │            │
                    └───────────┘ └────────────┘
```

## On-Chain Integration

Every tribunal session produces on-chain transactions on X Layer:

- **Verdict transactions** — each agent's analysis is encoded as hex data in a self-transfer transaction, creating an immutable public record
- **Trade transactions** — consensus buys are executed via OKX DEX Aggregator, routed through 500+ liquidity sources

All transactions are verifiable on [X Layer Explorer](https://www.okx.com/web3/explorer/xlayer).

## OKX OnchainOS Integration

Ghost Tribunal uses multiple OnchainOS APIs:

| API | Usage |
|-----|-------|
| **Token API** | Search and discover tokens on X Layer |
| **Security API** | Scan tokens for rug flags, honeypots, dev wallet risks |
| **Market API** | Real-time price data, volume, and candles |
| **DEX Aggregator** | Execute swaps across 500+ liquidity sources |

## Quick Start

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/ghost-tribunal.git
cd ghost-tribunal

# Install onchainos CLI
curl -sSL https://raw.githubusercontent.com/okx/onchainos-skills/main/install.sh | sh

# Install Python deps
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run a single tribunal session
python tribunal.py "TokenName" "0xTokenAddress"

# Run the live dashboard
python dashboard.py
# Open http://localhost:3000

# Run the trend watcher (continuous monitoring + auto-tribunal)
python watcher.py
```

## Dashboard

The live dashboard shows tribunal sessions in real-time:
- Agent verdicts with reasoning
- Consensus results (BUY / PASS)
- On-chain transaction links to X Layer Explorer
- Agent performance stats (bullish rate per agent)
- Auto-refreshes every 10 seconds

```bash
python dashboard.py  # → http://localhost:3000
```

## Demo

```bash
# Demo mode: runs tribunal on a sample token
python tribunal.py
```

Output:
```
============================================================
TRIBUNAL SESSION: DemoToken (0x000000...)
============================================================
  🎰 The Degen: ✅ BUY
     "Volume pumping, narrative is hot, LFG ser. Confidence: 8/10"
  🛡️ The Sentinel: ❌ PASS
     "Unverified contract. Top 10 hold 42%. Risk: 7/10"
  🔮 The Oracle: ✅ BUY
     "Strong cultural moment. Narrative has legs. Strength: 7/10"
  📊 The Quant: ✅ BUY
     "Vol/mcap ratio 0.3x is healthy. Liquidity sufficient. EV: +15%"

VOTE: 3/4 BUY → CONSENSUS REACHED
Verdict posted on-chain: tx 0xabc123...
EXECUTING TRADE...
```

## Why Multi-Agent?

Single-agent trading bots have one perspective and one failure mode. Ghost Tribunal's four agents catch what any individual would miss:

- The Degen spots momentum the Quant would ignore
- The Sentinel catches rugs the Degen would ape into
- The Oracle identifies narratives the Quant can't quantify
- The Quant finds value the Oracle would overlook

The debate IS the alpha.

## Tech Stack

- **Python** — async orchestration
- **X Layer** (Chain ID 196) — on-chain verdicts and trades
- **OKX OnchainOS** — token discovery, security scanning, DEX aggregation
- **Grok AI** — agent analysis and personality
- **web3.py** — on-chain transaction posting

## License

MIT
