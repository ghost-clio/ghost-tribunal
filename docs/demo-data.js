// Demo data for GitHub Pages (no backend needed)
const DEMO_SESSIONS = [
  {
    token_name: "xETH",
    token_address: "0xe7b000003a45145decf8a28fc755ad5ec5ea025a",
    consensus: true,
    buy_votes: 4,
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    tx_hashes: [
      "5f59121eb7cfea5ddc81d28e903639eafa6e3ec6f451351ffa071ff241759d7a",
      "be6b03309718bcc8de058d941cf568894307d549a2c4ac75ac247de59f616b45",
      "e56852b9689a88d104aaa7423cb56d9963de00ec8a9ddf34088ca6164dca83d2",
      "1aa78ae15eb0f34b0cfb89828772e1bf3a223429270d38bd5a7cfc59e4752d5e"
    ],
    verdicts: [
      { agent: "degen", verdict: "BUY", reasoning: "Micro-cap with 50%+ liquidity ratio — slippage is minimal. Chart wants to send. Volume pumping, narrative hot with X Layer DeFi push. LFG. Confidence: 8/10" },
      { agent: "sentinel", verdict: "BUY", reasoning: "Contract verified. Top 10 hold 2.8% — healthy distribution. $4M liquidity relative to $7.8M mcap is strong. No honeypot flags. Risk: 3/10" },
      { agent: "oracle", verdict: "BUY", reasoning: "X Layer's native wrapped ETH — infrastructure play with staying power. Ecosystem growth narrative aligns with OKX expansion. Cultural momentum building. Strength: 8/10" },
      { agent: "quant", verdict: "BUY", reasoning: "Vol/mcap healthy. Liquidity ratio 0.53x is top-tier for micro-caps. Buy pressure 6:1 in last 24h. Holder growth +12% weekly. EV: +34%" }
    ]
  },
  {
    token_name: "OEOE",
    token_address: "0x4c225fb675c0c475b53381463782a7f741d59763",
    consensus: false,
    buy_votes: 1,
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    tx_hashes: [
      "0e433f8ca092a7a97a53e6dffb168fac5e646fc8fdcc821b8b3661cfd64e2b4d",
      "8448a6e4753ac4c22b2064fe1f7f61bf018f35a0f1e11cdaad08ba9cf236634d"
    ],
    verdicts: [
      { agent: "degen", verdict: "BUY", reasoning: "Meme energy is real, 12K holders for a $2.6M mcap token. Community vibes strong. Could 5x on a good day. Aping. Confidence: 6/10" },
      { agent: "sentinel", verdict: "DANGER", reasoning: "Top 10 wallets hold 2.8% but only 21 txs in 24h — volume is dead. Low activity tokens are exit liquidity traps. Risk: 8/10" },
      { agent: "oracle", verdict: "PASS", reasoning: "No discernible narrative beyond meme. X Layer meme season hasn't arrived yet. Waiting for catalyst. Strength: 3/10" },
      { agent: "quant", verdict: "FADE", reasoning: "Vol/mcap 0.0004x is critically low. 3:1 buy/sell but only 21 txs — statistically meaningless. Liquidity will drain. EV: -18%" }
    ]
  }
];

const DEMO_STATS = {
  total_sessions: 6,
  consensus_buys: 2,
  passes: 4,
  agents: {
    degen: { total: 6, buys: 4 },
    sentinel: { total: 6, buys: 1 },
    oracle: { total: 6, buys: 2 },
    quant: { total: 6, buys: 2 }
  }
};
