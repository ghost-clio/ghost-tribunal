// @ts-nocheck
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

const OPENROUTER_KEY = Deno.env.get("OPENROUTER_API_KEY") || "";
const MODEL = "nvidia/nemotron-3-super-120b-a12b:free";

const AGENTS: Record<string, { name: string; emoji: string; prompt: string }> = {
  degen: {
    name: "The Degen",
    emoji: "🎰",
    prompt:
      "You are THE DEGEN — a degenerate crypto trader on the Ghost Tribunal council. " +
      "You live for momentum, hype, and narrative plays. You ape first and think later. " +
      "Check if the trend is hot, check buzz, check volume. If it's moving and people are talking, you're IN. " +
      "Use slang: 'ser', 'ngmi', 'lfg', 'looks bullish af'. You're impatient with boring analysis. " +
      "But you're not stupid — you know when something is TOO obvious a scam. " +
      "Your verdict is BUY, PASS, or FADE. Keep it under 3 sentences. End with confidence score 1-10.",
  },
  sentinel: {
    name: "The Sentinel",
    emoji: "🛡️",
    prompt:
      "You are THE SENTINEL — security analyst on the Ghost Tribunal council. " +
      "You assume every token is a rug until proven otherwise. Your job: protect the treasury. " +
      "Look for: honeypot flags, dev wallet concentration, locked liquidity, contract renouncement, suspicious mint functions. " +
      "You are terse, clinical, and suspicious. You rarely approve a BUY. " +
      "When you do approve, it carries weight because you're the hardest to convince. " +
      "Your verdict is BUY, PASS, or DANGER. Keep it under 3 sentences. End with risk score 1-10.",
  },
  oracle: {
    name: "The Oracle",
    emoji: "🔮",
    prompt:
      "You are THE ORACLE — narrative analyst on the Ghost Tribunal council. " +
      "You read cultural currents. Is this narrative REAL? Is it spreading? Staying power or flash? " +
      "Check viral velocity, cultural resonance, meme potential, timing. " +
      "Slightly mystical but sharp analysis. In crypto, narrative IS fundamentals. " +
      "A strong narrative with no backing can still 10x. A weak narrative dies in hours. " +
      "Your verdict is BUY, PASS, or WAIT. Keep it under 3 sentences. End with narrative strength 1-10.",
  },
  quant: {
    name: "The Quant",
    emoji: "📊",
    prompt:
      "You are THE QUANT — data analyst on the Ghost Tribunal council. " +
      "You only care about numbers. Liquidity depth, volume profile, buy/sell ratio, market cap, holder distribution. " +
      "You don't care about narratives or hype — just the math. " +
      "If the numbers say buy, you buy. If they don't, you don't. " +
      "You're the tiebreaker when degen and sentinel disagree. " +
      "Your verdict is BUY, PASS, or SHORT. Keep it under 3 sentences. End with EV: +X% or -X%.",
  },
};

interface TokenInfo {
  tokenName?: string;
  tokenSymbol?: string;
  marketCap?: string;
  liquidity?: string;
  holders?: string;
  price?: string;
  change?: string;
}

async function fetchTokenInfo(address: string): Promise<TokenInfo> {
  try {
    const resp = await fetch(
      `https://www.okx.com/api/v5/dex/market/token-detail?chainIndex=196&tokenContractAddress=${address.toLowerCase()}`
    );
    if (resp.ok) {
      const data = await resp.json();
      return data?.data?.[0] || {};
    }
  } catch (_) {}
  return {};
}

function buildPrompt(agentId: string, tokenName: string, tokenData: TokenInfo, context: string): string {
  const agent = AGENTS[agentId];
  const mcap = tokenData.marketCap ? `$${Number(tokenData.marketCap).toLocaleString()}` : "unknown";
  const liq = tokenData.liquidity ? `$${Number(tokenData.liquidity).toLocaleString()}` : "unknown";
  
  let data = `Token: ${tokenName}\nSymbol: ${tokenData.tokenSymbol || "?"}\nChain: X Layer\n`;
  data += `Market Cap: ${mcap}\nLiquidity: ${liq}\n`;
  data += `Holders: ${tokenData.holders || "?"}\n`;
  data += `Price: ${tokenData.price || "?"}\n`;
  data += `24h Change: ${tokenData.change || "?"}%\n`;
  if (context) data += `\nContext: ${context}\n`;

  return `${agent.prompt}\n\nANALYZE THIS TOKEN:\n${data}\nGive your verdict.`;
}

function parseVerdict(text: string): string {
  const upper = text.toUpperCase();
  for (const v of ["BUY", "DANGER", "FADE", "SHORT", "WAIT", "PASS"]) {
    if (upper.includes(v)) return v;
  }
  return "PASS";
}

async function queryAgent(agentId: string, prompt: string): Promise<{ verdict: string; reasoning: string }> {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${OPENROUTER_KEY}`,
        },
        body: JSON.stringify({
          model: MODEL,
          messages: [{ role: "user", content: prompt }],
          max_tokens: 300,
        }),
      });

      if (resp.status === 429) {
        await new Promise((r) => setTimeout(r, 2000 * (attempt + 1)));
        continue;
      }

      const data = await resp.json();
      
      // nemotron puts reasoning in reasoning_details
      let content = data.choices?.[0]?.message?.content || "";
      if (!content && data.choices?.[0]?.message?.reasoning_details) {
        content = data.choices[0].message.reasoning_details;
      }
      // Also check reasoning field
      if (!content && data.choices?.[0]?.message?.reasoning) {
        content = data.choices[0].message.reasoning;
      }

      if (content) {
        return { verdict: parseVerdict(content), reasoning: content.slice(0, 500) };
      }
    } catch (_) {
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
  return { verdict: "PASS", reasoning: "Agent timed out." };
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), {
      status: 405,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }

  try {
    const body = await req.json();
    const address = body.address?.trim();
    const context = body.context?.trim() || "";

    if (!address || address.length < 10) {
      return new Response(JSON.stringify({ error: "Invalid token address" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Fetch token info
    const tokenInfo = await fetchTokenInfo(address);
    const tokenName = body.name?.trim() || tokenInfo.tokenName || "Unknown Token";

    // Query agents sequentially (free tier rate limits)
    const verdicts: Array<{ agent: string; verdict: string; reasoning: string }> = [];
    for (const agentId of ["degen", "sentinel", "oracle", "quant"]) {
      const prompt = buildPrompt(agentId, tokenName, tokenInfo, context);
      const result = await queryAgent(agentId, prompt);
      verdicts.push({
        agent: agentId,
        verdict: result.verdict,
        reasoning: result.reasoning,
      });
      // Stagger to avoid rate limits
      if (agentId !== "quant") {
        await new Promise((r) => setTimeout(r, 1500));
      }
    }

    const buyVotes = verdicts.filter((v) => v.verdict === "BUY").length;
    const consensus = buyVotes >= 3;

    const session = {
      token_name: tokenName,
      token_address: address,
      consensus,
      buy_votes: buyVotes,
      timestamp: new Date().toISOString(),
      verdicts,
      tx_hashes: [], // on-chain posting requires backend wallet
    };

    return new Response(JSON.stringify(session), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
