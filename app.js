/**
 * app.js — Rodman Historic Feats frontend logic
 * Handles: page detection, API calls, rendering index + ranking pages.
 */

const API_BASE = "http://localhost:8000";

// ── Detect current page ────────────────────────────────────────────────────

const isRankingPage = window.location.pathname.includes("ranking");

if (isRankingPage) {
  initRankingPage();
} else {
  initIndexPage();
}

// ============================================================
// INDEX PAGE
// ============================================================

async function initIndexPage() {
  const grid = document.getElementById("featsGrid");
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

  feats.forEach((feat) => {
    const card = document.createElement("div");
    card.className = "feat-card";
    card.innerHTML = `
      <span class="feat-icon">${feat.icon}</span>
      <div class="feat-title">${feat.title}</div>
      <div class="feat-subtitle">${feat.subtitle}</div>
      <p class="feat-description">${feat.description}</p>
      <span class="feat-arrow">→</span>
    `;
    card.addEventListener("click", () => navigateToRanking(feat.id, overlay));
    grid.appendChild(card);
  });
}

function navigateToRanking(featId, overlay) {
  overlay.classList.add("visible");
  // Small delay so the spinner is visible before navigation
  setTimeout(() => {
    window.location.href = `/ranking?feat=${featId}`;
  }, 150);
}

// ============================================================
// RANKING PAGE
// ============================================================

async function initRankingPage() {
  const params   = new URLSearchParams(window.location.search);
  const featId   = params.get("feat");
  const overlay  = document.getElementById("loadingOverlay");
  const header   = document.getElementById("rankingHeader");
  const list     = document.getElementById("rankingList");
  const errorEl  = document.getElementById("errorState");
  const backBtn  = document.getElementById("backBtn");

  // Fix back button: if served from FastAPI, go to root
  backBtn.href = "/";

  if (!featId) {
    showError(errorEl, list, "No feat specified in URL.");
    return;
  }

  overlay.classList.add("visible");

  try {
    const data = await apiFetch(`/api/feats/${featId}/ranking`);
    overlay.classList.remove("visible");
    renderRankingHeader(data, header);
    renderRankingList(data, list);
  } catch (err) {
    overlay.classList.remove("visible");
    errorEl.style.display = "block";
  }
}

function renderRankingHeader(data, container) {
  // Find the feat icon from the title emoji
  const iconMap = {
    rebounds:        "🏀",
    defensive_teams: "🛡️",
    championships:   "💍",
    steals:          "🕵️",
    intensity:       "🔥",
  };
  const icon = iconMap[data.feat_id] || "🏆";

  const sourceClass = data.source === "live" ? "live" : "mock";
  const sourceLabel = data.source === "live" ? "Live data" : "Demo data";
  const sourceDot   = data.source === "live" ? "●" : "●";

  container.innerHTML = `
    <span class="feat-icon-lg">${icon}</span>
    <h1>${data.title}</h1>
    <p class="subtitle">${data.subtitle}</p>
    <span class="source-badge ${sourceClass}">
      <span class="dot"></span>
      ${sourceLabel}
    </span>
  `;
}

function renderRankingList(data, container) {
  container.innerHTML = "";

  if (!data.ranking || data.ranking.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted); text-align:center; padding:2rem;">No ranking data available.</p>`;
    return;
  }

  data.ranking.forEach((player, index) => {
    const item = document.createElement("div");

    const isFirst  = player.rank === 1;
    const isRodman = player.is_rodman;

    let classes = "ranking-item";
    if (isFirst)  classes += " rank-first";
    if (isRodman) classes += " is-rodman";

    const wormBadge = isRodman
      ? `<span class="worm-badge">🐛 The Worm</span>`
      : "";

    const teamLabel = player.team
      ? `<div class="player-team">${player.team}</div>`
      : "";

    const valueFormatted = Number(player.value).toLocaleString("en-US");

    item.className = classes;
    item.innerHTML = `
      <div class="rank-number">${player.rank}</div>
      <div class="player-info">
        <div class="player-name">
          ${player.player}${wormBadge}
        </div>
        ${teamLabel}
      </div>
      <div class="player-value">
        <span class="value-number">${valueFormatted}</span>
        <span class="value-unit">${data.unit}</span>
      </div>
    `;

    container.appendChild(item);

    // Staggered reveal animation
    setTimeout(() => {
      item.classList.add("visible");
    }, 60 * index);
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
  if (listEl) listEl.innerHTML = "";
  if (errorEl) {
    errorEl.style.display = "block";
    const p = errorEl.querySelector("p");
    if (p && message) p.textContent = message;
  }
}
