// Ghost Tribunal — Dashboard

const API_BASE = '';

let connectedWallet = null;
let freeRunUsed = false;

async function connectWallet() {
  if (!window.ethereum) {
    alert('Install MetaMask or an EVM wallet to connect');
    return;
  }
  try {
    const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
    if (accounts.length > 0) {
      connectedWallet = accounts[0];
      document.getElementById('connect-btn').style.display = 'none';
      document.getElementById('wallet-info').style.display = 'flex';
      document.getElementById('wallet-addr').textContent =
        connectedWallet.slice(0, 6) + '...' + connectedWallet.slice(-4);
      
      // Check if free run already used (stored locally)
      const used = localStorage.getItem('gt_free_' + connectedWallet.toLowerCase());
      if (used) {
        freeRunUsed = true;
        document.getElementById('free-badge').textContent = '💰 $0.01/session';
        document.getElementById('free-badge').className = 'free-badge paid';
      }
    }
  } catch (e) {
    console.error('Wallet connect failed:', e);
  }
}

// Auto-reconnect if previously connected
if (window.ethereum) {
  window.ethereum.request({ method: 'eth_accounts' }).then(accounts => {
    if (accounts.length > 0) {
      connectedWallet = accounts[0];
      document.getElementById('connect-btn').style.display = 'none';
      document.getElementById('wallet-info').style.display = 'flex';
      document.getElementById('wallet-addr').textContent =
        connectedWallet.slice(0, 6) + '...' + connectedWallet.slice(-4);
      const used = localStorage.getItem('gt_free_' + connectedWallet.toLowerCase());
      if (used) {
        freeRunUsed = true;
        document.getElementById('free-badge').textContent = '💰 $0.01/session';
        document.getElementById('free-badge').className = 'free-badge paid';
      }
    }
  });
}

const AGENTS = {
  degen:   { name: 'The Degen',    emoji: '🎰' },
  sentinel:{ name: 'The Sentinel', emoji: '🛡️' },
  oracle:  { name: 'The Oracle',   emoji: '🔮' },
  quant:   { name: 'The Quant',    emoji: '📊' },
};

const EXPLORER = 'https://www.okx.com/web3/explorer/xlayer/tx/';
const REFRESH_MS = 10000;

function timeAgo(iso) {
  const s = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return 'just now';
  if (s < 3600) return Math.floor(s / 60) + 'm ago';
  if (s < 86400) return Math.floor(s / 3600) + 'h ago';
  return Math.floor(s / 86400) + 'd ago';
}

function verdictClass(v) {
  if (v === 'BUY') return 'buy';
  if (['DANGER','FADE','SHORT'].includes(v)) return 'pass';
  return 'wait';
}

function renderSession(s) {
  const isBuy = s.consensus;
  const verdicts = (s.verdicts || []).map(v => {
    const agent = AGENTS[v.agent] || { name: v.agent, emoji: '?' };
    const cls = verdictClass(v.verdict);
    const text = (v.reasoning || '').slice(0, 140) + ((v.reasoning || '').length > 140 ? '...' : '');
    return `
      <div class="verdict">
        <div class="verdict-header">
          <span class="verdict-agent">${agent.emoji} ${agent.name}</span>
          <span class="verdict-badge ${cls}">${v.verdict}</span>
        </div>
        <div class="verdict-text">${escHtml(text)}</div>
      </div>
    `;
  }).join('');

  const txLinks = (s.tx_hashes || []).slice(0, 2).map(h =>
    `<a href="${EXPLORER}${h}" target="_blank">${h.slice(0, 10)}...</a>`
  ).join(' ');

  return `
    <div class="session-card ${isBuy ? 'consensus' : 'rejected'}">
      <div class="session-header">
        <span class="session-token">👻 ${escHtml(s.token_name || '?')}</span>
        <span class="session-result ${isBuy ? 'buy' : 'pass'}">
          ${isBuy ? `✅ BUY (${s.buy_votes}/4)` : `❌ PASS (${s.buy_votes}/4)`}
        </span>
      </div>
      <div class="session-verdicts">${verdicts}</div>
      <div class="session-footer">
        <span class="session-time">${timeAgo(s.timestamp)}</span>
        <span>${txLinks || 'no on-chain txs'}</span>
      </div>
    </div>
  `;
}

function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

async function loadSessions() {
  const el = document.getElementById('sessions');
  let sessions = null;
  try {
    const resp = await fetch(API_BASE + '/api/sessions');
    if (resp.ok) sessions = await resp.json();
  } catch(e) { /* no backend */ }

  // Fallback to demo data (GitHub Pages, no backend)
  if (!sessions && typeof DEMO_SESSIONS !== 'undefined') sessions = DEMO_SESSIONS;
  if (!sessions || !sessions.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-icon">👻</div><p>No tribunal sessions yet</p><p class="empty-sub">Submit a token above or run <code>python tribunal.py</code></p></div>';
    return;
  }
  el.innerHTML = sessions.reverse().map(renderSession).join('');
}

async function loadStats() {
  let stats = null;
  try {
    const resp = await fetch(API_BASE + '/api/stats');
    if (resp.ok) stats = await resp.json();
  } catch(e) { /* no backend */ }
  if (!stats && typeof DEMO_STATS !== 'undefined') stats = DEMO_STATS;
  if (!stats) return;

    document.getElementById('stat-total').textContent = stats.total_sessions;
    document.getElementById('stat-buys').textContent = stats.consensus_buys;
    document.getElementById('stat-passes').textContent = stats.passes;
    document.getElementById('stat-rate').textContent =
      stats.total_sessions > 0
        ? Math.round((stats.consensus_buys / stats.total_sessions) * 100) + '%'
        : '—';

    // Agent stats
    for (const [id, data] of Object.entries(stats.agents || {})) {
      const el = document.getElementById(`${id}-stat`);
      if (el) {
        const rate = data.total > 0 ? Math.round((data.buys / data.total) * 100) : 0;
        el.textContent = `${rate}% bullish`;
        el.style.color = rate > 60 ? 'var(--green)' : rate < 30 ? 'var(--red)' : 'var(--text)';
      }
    }
}

async function refresh() {
  await Promise.all([loadSessions(), loadStats()]);
}

// Submit token to tribunal
async function submitToken() {
  const addrEl = document.getElementById('token-input');
  const nameEl = document.getElementById('name-input');
  const ctxEl = document.getElementById('context-input');
  const btn = document.getElementById('submit-btn');
  const status = document.getElementById('submit-status');

  const address = addrEl.value.trim();
  if (!address) { addrEl.focus(); return; }

  btn.disabled = true;
  btn.textContent = '👻';
  status.className = 'submit-status thinking';
  status.textContent = 'The tribunal is deliberating...';

  try {
    const payload = {
      address: address,
      name: nameEl.value.trim(),
      context: ctxEl.value.trim(),
    };
    if (connectedWallet) payload.wallet = connectedWallet;

    const resp = await fetch(API_BASE + '/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!resp.ok && resp.headers.get('content-type')?.includes('text/html')) {
      throw new Error('NO_BACKEND');
    }

    const data = await resp.json();

    if (resp.status === 402) {
      // Payment required — free run used up
      status.className = 'submit-status payment';
      status.innerHTML = '💰 Free run used! Pay <strong>$0.01 USDC</strong> per session via x402 to continue. <a href="https://x402.org" target="_blank">Learn about x402 →</a>';
      if (connectedWallet) {
        freeRunUsed = true;
        localStorage.setItem('gt_free_' + connectedWallet.toLowerCase(), '1');
        document.getElementById('free-badge').textContent = '💰 $0.01/session';
        document.getElementById('free-badge').className = 'free-badge paid';
      }
    } else if (resp.ok) {
      const verdict = data.consensus
        ? `✅ CONSENSUS BUY (${data.buy_votes}/4)`
        : `❌ NO CONSENSUS (${data.buy_votes}/4 BUY)`;
      const txs = (data.tx_hashes || []).length;
      status.className = 'submit-status success';
      status.textContent = `${verdict} — ${txs} verdicts posted on-chain`;
      
      // Mark free run as used
      if (connectedWallet && !freeRunUsed) {
        freeRunUsed = true;
        localStorage.setItem('gt_free_' + connectedWallet.toLowerCase(), '1');
        document.getElementById('free-badge').textContent = '💰 $0.01/session';
        document.getElementById('free-badge').className = 'free-badge paid';
      }
      
      addrEl.value = '';
      nameEl.value = '';
      ctxEl.value = '';
      await refresh();
    } else {
      status.className = 'submit-status error';
      status.textContent = `Error: ${data.error || 'Unknown error'}`;
    }
  } catch(e) {
    status.className = 'submit-status error';
    if (e.message === 'NO_BACKEND' || e.message?.includes('Unexpected token')) {
      status.innerHTML = '🔧 Live tribunal requires a running backend.<br><code>git clone ghost-clio/ghost-tribunal && python tribunal.py</code><br>Or view the demo sessions below ↓';
    } else {
      status.textContent = `Error: ${e.message}`;
    }
  }

  btn.disabled = false;
  btn.textContent = 'SUMMON';
}

// Submit on Enter in any input field
['token-input', 'name-input', 'context-input'].forEach(id => {
  document.getElementById(id).addEventListener('keydown', e => {
    if (e.key === 'Enter') submitToken();
  });
});

// Init
refresh();
setInterval(refresh, REFRESH_MS);
