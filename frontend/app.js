/**
 * app.js — Rodman Historic Feats v2
 *
 * Features:
 *   1. Real Wikimedia photos (index page)
 *   2. Animated value counters (ranking page)
 *   3. Share button per ranking (ranking page)
 *   4. Sound design — synthesized crowd + buzzer via Web Audio API (both pages)
 */

const API_BASE = "http://localhost:8000";

// ============================================================
// SOUND ENGINE  (Web Audio API — no external files needed)
// ============================================================

const Sound = (() => {
  let ctx = null;
  let enabled = true;

  // Persist preference across pages
  try {
    const stored = localStorage.getItem("rodman_sound");
    if (stored !== null) enabled = stored === "true";
  } catch (_) {}

  function getCtx() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    // Resume if suspended (browser autoplay policy)
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }

  function setEnabled(val) {
    enabled = val;
    try { localStorage.setItem("rodman_sound", String(val)); } catch (_) {}
  }

  // ── Synthesised crowd hum: layered noise bursts ──
  function playCrowdHum(duration = 1.2) {
    if (!enabled) return;
    const c = getCtx();
    const bufSize = c.sampleRate * duration;
    const buf = c.createBuffer(1, bufSize, c.sampleRate);
    const data = buf.getChannelData(0);
    for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * 0.15;

    const src = c.createBufferSource();
    src.buffer = buf;

    // Band-pass filter to make it sound like crowd noise
    const bpf = c.createBiquadFilter();
    bpf.type = "bandpass";
    bpf.frequency.value = 800;
    bpf.Q.value = 0.4;

    const gain = c.createGain();
    gain.gain.setValueAtTime(0, c.currentTime);
    gain.gain.linearRampToValueAtTime(0.4, c.currentTime + 0.3);
    gain.gain.linearRampToValueAtTime(0, c.currentTime + duration);

    src.connect(bpf);
    bpf.connect(gain);
    gain.connect(c.destination);
    src.start();
    src.stop(c.currentTime + duration);
  }

  // ── Synthesised buzzer: descending square-wave sweep ──
  function playBuzzer() {
    if (!enabled) return;
    const c = getCtx();

    const osc = c.createOscillator();
    const gain = c.createGain();
    osc.type = "square";
    osc.frequency.setValueAtTime(220, c.currentTime);
    osc.frequency.exponentialRampToValueAtTime(110, c.currentTime + 0.5);

    gain.gain.setValueAtTime(0.18, c.currentTime);
    gain.gain.linearRampToValueAtTime(0, c.currentTime + 0.5);

    osc.connect(gain);
    gain.connect(c.destination);
    osc.start();
    osc.stop(c.currentTime + 0.5);
  }

  // ── Gold shimmer: short ascending chime for #1 reveal ──
  function playChime() {
    if (!enabled) return;
    const c = getCtx();
    [523, 659, 784].forEach((freq, i) => {
      const osc = c.createOscillator();
      const gain = c.createGain();
      osc.type = "sine";
      osc.frequency.value = freq;
      const t = c.currentTime + i * 0.1;
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.6);
      osc.connect(gain);
      gain.connect(c.destination);
      osc.start(t);
      osc.stop(t + 0.6);
    });
  }

  return { playCrowdHum, playBuzzer, playChime, setEnabled, get enabled() { return enabled; } };
})();


// ============================================================
// SOUND TOGGLE BUTTON (both pages)
// ============================================================

function initSoundToggle() {
  const btn  = document.getElementById("soundToggle");
  const icon = document.getElementById("soundIcon");
  if (!btn) return;

  const update = () => { icon.textContent = Sound.enabled ? "🔊" : "🔇"; };
  update();

  btn.addEventListener("click", () => {
    Sound.setEnabled(!Sound.enabled);
    update();
    if (Sound.enabled) Sound.playCrowdHum(0.6);
  });
}


// ============================================================
// ANIMATED COUNTER
// ============================================================

/**
 * Animates a numeric display from 0 → target over `ms` milliseconds.
 * Supports integers and floats (auto-detects decimals from target string).
 */
function animateCounter(el, target, ms = 1200) {
  const raw       = String(target).replace(/,/g, "");
  const isFloat   = raw.includes(".");
  const decimals  = isFloat ? raw.split(".")[1].length : 0;
  const end       = parseFloat(raw);
  const start     = performance.now();

  // Easing: ease-out cubic
  const ease = t => 1 - Math.pow(1 - t, 3);

  function step(now) {
    const progress = Math.min((now - start) / ms, 1);
    const current  = end * ease(progress);
    el.textContent = isFloat
      ? current.toFixed(decimals)
      : Math.floor(current).toLocaleString("en-US");
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = isFloat ? end.toFixed(decimals) : end.toLocaleString("en-US");
  }

  requestAnimationFrame(step);
}


// ============================================================
// PAGE ROUTER
// ============================================================

const isRankingPage = window.location.pathname.includes("ranking");
initSoundToggle();

if (isRankingPage) {
  Sound.playCrowdHum();
  initRankingPage();
} else {
  Sound.playCrowdHum(0.8);
  initIndexPage();
}


// ============================================================
// INDEX PAGE
// ============================================================

async function initIndexPage() {
  const grid    = document.getElementById("featsGrid");
  const overlay = document.getElementById("loadingOverlay");

  try {
    const data = await apiFetch("/api/feats");
    renderFeatCards(data.feats, grid, overlay);
  } catch (err) {
    grid.innerHTML = `
      <div class="error-state" style="grid-column:1/-1">
        <div class="error-icon">⚠️</div>
        <h3>Backend Not Reachable</h3>
        <p>Make sure the server is running:<br>
           <code style="color:var(--red);">uvicorn app:app --port 8000 --reload</code>
        </p>
      </div>`;
  }
}

function renderFeatCards(feats, grid, overlay) {
  grid.innerHTML = "";
  feats.forEach(feat => {
    const card = document.createElement("div");
    card.className = "feat-card";
    card.innerHTML = `
      <span class="feat-icon">${feat.icon}</span>
      <div class="feat-title">${feat.title}</div>
      <div class="feat-subtitle">${feat.subtitle}</div>
      <p class="feat-description">${feat.description}</p>
      <span class="feat-arrow">→</span>
    `;
    card.addEventListener("click", () => {
      Sound.playBuzzer();
      overlay.classList.add("visible");
      setTimeout(() => { window.location.href = `/ranking?feat=${feat.id}`; }, 180);
    });
    grid.appendChild(card);
  });
}


// ============================================================
// RANKING PAGE
// ============================================================

async function initRankingPage() {
  const params  = new URLSearchParams(window.location.search);
  const featId  = params.get("feat");
  const overlay = document.getElementById("loadingOverlay");
  const header  = document.getElementById("rankingHeader");
  const list    = document.getElementById("rankingList");
  const errorEl = document.getElementById("errorState");

  if (!featId) { showError(errorEl, list, "No feat specified in URL."); return; }

  overlay.classList.add("visible");

  try {
    const data = await apiFetch(`/api/feats/${featId}/ranking`);
    overlay.classList.remove("visible");
    renderRankingHeader(data, header, featId);
    renderRankingList(data, list);
  } catch (err) {
    overlay.classList.remove("visible");
    errorEl.style.display = "block";
  }
}

// Icon map for v2 feats
const ICON_MAP = {
  rebounding_titles:          "👑",
  season_rpg:                 "📈",
  offensive_rebounds_season:  "💥",
  consecutive_titles:         "🔗",
  chaos_index:                "🔥",
};

function renderRankingHeader(data, container, featId) {
  const icon        = ICON_MAP[featId] || "🏆";
  const sourceClass = data.source === "live" ? "live" : "mock";
  const sourceLabel = data.source === "live" ? "Live data" : "Demo data";

  container.innerHTML = `
    <span class="feat-icon-lg">${icon}</span>
    <h1>${data.title}</h1>
    <p class="subtitle">${data.subtitle}</p>
    <div class="header-actions">
      <span class="source-badge ${sourceClass}">
        <span class="dot"></span>${sourceLabel}
      </span>
      <button class="share-btn" id="shareBtn" title="Copy link to this ranking">
        <span id="shareLabel">⬡ Share</span>
      </button>
    </div>
  `;

  document.getElementById("shareBtn").addEventListener("click", handleShare);
}

function handleShare() {
  const url   = window.location.href;
  const btn   = document.getElementById("shareBtn");
  const label = document.getElementById("shareLabel");

  navigator.clipboard.writeText(url).then(() => {
    label.textContent = "✓ Copied!";
    btn.classList.add("share-copied");
    Sound.playChime();
    setTimeout(() => {
      label.textContent = "⬡ Share";
      btn.classList.remove("share-copied");
    }, 2200);
  }).catch(() => {
    // Fallback: select a temporary input
    const inp = document.createElement("input");
    inp.value = url;
    document.body.appendChild(inp);
    inp.select();
    document.execCommand("copy");
    document.body.removeChild(inp);
    label.textContent = "✓ Copied!";
    btn.classList.add("share-copied");
    setTimeout(() => {
      label.textContent = "⬡ Share";
      btn.classList.remove("share-copied");
    }, 2200);
  });
}

function renderRankingList(data, container) {
  container.innerHTML = "";

  if (!data.ranking?.length) {
    container.innerHTML = `<p style="color:var(--text-muted);text-align:center;padding:2rem;">No ranking data available.</p>`;
    return;
  }

  data.ranking.forEach((player, index) => {
    const isFirst  = player.rank === 1;
    const isRodman = player.is_rodman;

    let classes = "ranking-item";
    if (isFirst)  classes += " rank-first";
    if (isRodman) classes += " is-rodman";

    const wormBadge = isRodman ? `<span class="worm-badge">🐛 The Worm</span>` : "";
    const teamLabel = player.team ? `<div class="player-team">${player.team}</div>` : "";
    const seasonLabel = player.season
      ? `<div class="player-team">${player.season}</div>`
      : player.seasons
        ? `<div class="player-team">${player.seasons}</div>`
        : "";

    const item = document.createElement("div");
    item.className = classes;
    item.innerHTML = `
      <div class="rank-number">${player.rank}</div>
      <div class="player-info">
        <div class="player-name">${player.player}${wormBadge}</div>
        ${teamLabel}${seasonLabel}
      </div>
      <div class="player-value">
        <span class="value-number" data-target="${player.value}">0</span>
        <span class="value-unit">${data.unit}</span>
      </div>
    `;

    container.appendChild(item);

    // Staggered slide-in + counter start
    setTimeout(() => {
      item.classList.add("visible");

      // Start counter after the item slides in
      setTimeout(() => {
        const valueEl = item.querySelector(".value-number");
        animateCounter(valueEl, player.value, 1000);

        // Play chime when #1 (Rodman) appears
        if (isFirst && isRodman) Sound.playChime();
      }, 150);

    }, 70 * index);
  });
}


// ============================================================
// SHARED UTILITIES
// ============================================================

async function apiFetch(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function showError(errorEl, listEl, message) {
  if (listEl)  listEl.innerHTML = "";
  if (errorEl) {
    errorEl.style.display = "block";
    const p = errorEl.querySelector("p");
    if (p && message) p.textContent = message;
  }
}
