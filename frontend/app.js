/**
 * app.js — Rodman Historic Feats v3
 *
 * Pages: index, ranking, timeline, career
 * Features:
 *   - Animated value counters
 *   - Share button
 *   - Sound design (Web Audio API)
 *   - Did You Know panel (per feat, static)
 *   - Head-to-Head comparison drawer
 *   - Timeline animated bar chart
 *   - Career Arc animated line chart (SVG)
 */

const API_BASE = "http://localhost:8000";

// ============================================================
// STATIC DATA
// ============================================================

/** One wild fact per feat — shown in the Did You Know panel */
const DID_YOU_KNOW = {
  rebounding_titles: {
    headline: "Seven. Consecutive. Titles.",
    fact: "Rodman won the rebounding crown in 1991–92 with Detroit — a team that was his rival. He then moved to San Antonio and kept winning. Then Chicago. The titles followed him across three franchises, three coaches, and three different offensive systems. The next best in the modern era has four at most.",
    emoji: "👑",
  },
  season_rpg: {
    headline: "Shorter than most power forwards. Didn't care.",
    fact: "Rodman's 18.7 RPG in 1991–92 is the highest single-season average by any player since Bill Russell in 1964. He pulled this off at 6'7\" — shorter than almost every center and most power forwards he competed against. His secret: he watched film obsessively and calculated where each teammate's shot would land before it left their hands.",
    emoji: "📐",
  },
  offensive_rebounds_season: {
    headline: "He studied shooters like a scientist.",
    fact: "Rodman once explained that he mentally mapped every teammate's shooting arc and spin to predict the direction of a missed shot. He didn't just outwork people for offensive rebounds — he outthought them. He would position himself before the ball left the shooter's hands, often while defenders were still watching the flight path.",
    emoji: "🧪",
  },
  consecutive_titles: {
    headline: "He was 36. Still averaging 15 RPG.",
    fact: "The streak ended after the 1997–98 season — not because someone outrebounded him, but because Rodman was aging out of the game. He was 36 years old in that final title season and still pulled 15 RPG. The only other player to match his seven-season streak is Wilt Chamberlain, who played in an era with no other elite rebounders.",
    emoji: "🕰️",
  },
  chaos_index: {
    headline: "He showed up to his own press conference in a wedding dress.",
    fact: "In 1997, Rodman was suspended 6 games for headbutting a referee. His response: hold a press conference dressed as a bride, arriving in a horse-drawn carriage to promote his book 'I Should Be Dead By Now'. He also got suspended for kicking a courtside cameraman, for which he paid $200,000. The NBA once fined him for dyeing his hair.",
    emoji: "👰",
  },
};


/** Career stats for head-to-head comparison. Shown when user clicks a ranking entry. */
const PLAYER_STATS = {
  "Dennis Rodman": {
    seasons: 14, career_rpg: 13.1, best_rpg: 18.7,
    career_ppg: 7.3,  career_apg: 1.8,  career_spg: 0.7, career_bpg: 0.6,
    reb_titles: 7, championships: 5, all_defensive: 8,
    note: "6'7\" PF / SF — The Worm",
  },
  "Wilt Chamberlain": {
    seasons: 14, career_rpg: 22.9, best_rpg: 27.2,
    career_ppg: 30.1, career_apg: 4.4,  career_spg: null, career_bpg: null,
    reb_titles: 11, championships: 2, all_defensive: 0,
    note: "7'1\" C — The Big Dipper (pre-1980 era)",
  },
  "Moses Malone": {
    seasons: 21, career_rpg: 12.2, best_rpg: 17.6,
    career_ppg: 20.3, career_apg: 1.4,  career_spg: 0.8, career_bpg: 1.3,
    reb_titles: 4, championships: 1, all_defensive: 0,
    note: "6'10\" C — Chairman of the Boards",
  },
  "Kevin Willis": {
    seasons: 21, career_rpg: 8.0,  best_rpg: 11.0,
    career_ppg: 13.0, career_apg: 1.1,  career_spg: 0.6, career_bpg: 0.7,
    reb_titles: 0, championships: 1, all_defensive: 0,
    note: "7'0\" C/PF",
  },
  "Hakeem Olajuwon": {
    seasons: 18, career_rpg: 11.1, best_rpg: 14.0,
    career_ppg: 21.8, career_apg: 2.5,  career_spg: 1.7, career_bpg: 3.1,
    reb_titles: 1, championships: 2, all_defensive: 5,
    note: "7'0\" C — The Dream",
  },
  "Charles Barkley": {
    seasons: 16, career_rpg: 11.7, best_rpg: 14.6,
    career_ppg: 22.1, career_apg: 3.9,  career_spg: 1.5, career_bpg: 0.8,
    reb_titles: 1, championships: 0, all_defensive: 0,
    note: "6'6\" PF — Sir Charles",
  },
  "Bill Laimbeer": {
    seasons: 14, career_rpg: 9.7,  best_rpg: 11.9,
    career_ppg: 12.9, career_apg: 2.4,  career_spg: 0.6, career_bpg: 0.8,
    reb_titles: 1, championships: 2, all_defensive: 0,
    note: "6'11\" C — Bad Boys Detroit",
  },
  "David Robinson": {
    seasons: 14, career_rpg: 10.6, best_rpg: 13.0,
    career_ppg: 21.1, career_apg: 2.5,  career_spg: 1.7, career_bpg: 3.0,
    reb_titles: 1, championships: 2, all_defensive: 4,
    note: "7'1\" C — The Admiral",
  },
  "Dikembe Mutombo": {
    seasons: 18, career_rpg: 10.3, best_rpg: 13.0,
    career_ppg: 9.8,  career_apg: 1.5,  career_spg: 0.5, career_bpg: 3.3,
    reb_titles: 1, championships: 0, all_defensive: 8,
    note: "7'2\" C — Finger Wag",
  },
  "Kevin Garnett": {
    seasons: 21, career_rpg: 10.0, best_rpg: 13.9,
    career_ppg: 17.8, career_apg: 3.7,  career_spg: 1.3, career_bpg: 1.4,
    reb_titles: 1, championships: 1, all_defensive: 9,
    note: "6'11\" PF — The Big Ticket",
  },
  "Buck Williams": {
    seasons: 17, career_rpg: 9.9,  best_rpg: 12.5,
    career_ppg: 12.8, career_apg: 1.3,  career_spg: 0.8, career_bpg: 0.7,
    reb_titles: 1, championships: 0, all_defensive: 0,
    note: "6'8\" PF",
  },
  "Dwight Howard": {
    seasons: 19, career_rpg: 11.8, best_rpg: 14.5,
    career_ppg: 16.9, career_apg: 1.5,  career_spg: 0.9, career_bpg: 2.1,
    reb_titles: 3, championships: 0, all_defensive: 5,
    note: "6'10\" C — Superman",
  },
  "Rudy Gobert": {
    seasons: 11, career_rpg: 12.3, best_rpg: 15.1,
    career_ppg: 12.4, career_apg: 1.3,  career_spg: 0.6, career_bpg: 2.3,
    reb_titles: 3, championships: 0, all_defensive: 5,
    note: "7'1\" C — The Stifle Tower",
  },
  "Andre Drummond": {
    seasons: 12, career_rpg: 13.8, best_rpg: 17.8,
    career_ppg: 14.0, career_apg: 1.6,  career_spg: 1.2, career_bpg: 1.6,
    reb_titles: 2, championships: 0, all_defensive: 0,
    note: "6'10\" C",
  },
  "Rasheed Wallace": {
    seasons: 16, career_rpg: 6.7,  best_rpg: 9.5,
    career_ppg: 14.4, career_apg: 2.0,  career_spg: 1.0, career_bpg: 1.4,
    reb_titles: 0, championships: 1, all_defensive: 0,
    note: "6'11\" PF — Ball don't lie",
  },
  "Gary Payton": {
    seasons: 17, career_rpg: 4.3,  best_rpg: 7.0,
    career_ppg: 16.3, career_apg: 6.7,  career_spg: 2.0, career_bpg: 0.2,
    reb_titles: 0, championships: 1, all_defensive: 9,
    note: "6'4\" PG — The Glove",
  },
  "Karl Malone": {
    seasons: 19, career_rpg: 10.1, best_rpg: 11.8,
    career_ppg: 25.0, career_apg: 3.6,  career_spg: 1.4, career_bpg: 0.8,
    reb_titles: 0, championships: 0, all_defensive: 4,
    note: "6'9\" PF — The Mailman",
  },
  "Patrick Ewing": {
    seasons: 17, career_rpg: 9.8,  best_rpg: 11.8,
    career_ppg: 21.0, career_apg: 2.4,  career_spg: 1.0, career_bpg: 2.4,
    reb_titles: 0, championships: 0, all_defensive: 1,
    note: "7'0\" C — New York's finest",
  },
  "Charles Barkley": {
    seasons: 16, career_rpg: 11.7, best_rpg: 14.6,
    career_ppg: 22.1, career_apg: 3.9,  career_spg: 1.5, career_bpg: 0.8,
    reb_titles: 1, championships: 0, all_defensive: 0,
    note: "6'6\" PF — Sir Charles",
  },
  "Bill Russell": {
    seasons: 13, career_rpg: 22.5, best_rpg: 24.7,
    career_ppg: 15.1, career_apg: 4.3,  career_spg: null, career_bpg: null,
    reb_titles: 0, championships: 11, all_defensive: 0,
    note: "6'10\" C — 11 rings (pre-1980 era)",
  },
  "Rick Mahorn": {
    seasons: 13, career_rpg: 6.3,  best_rpg: 9.0,
    career_ppg: 8.5,  career_apg: 1.4,  career_spg: 0.8, career_bpg: 0.9,
    reb_titles: 0, championships: 1, all_defensive: 0,
    note: "6'10\" PF — Bad Boys Detroit",
  },
  "Vernon Maxwell": {
    seasons: 13, career_rpg: 2.8,  best_rpg: 4.5,
    career_ppg: 12.7, career_apg: 3.5,  career_spg: 1.5, career_bpg: 0.3,
    reb_titles: 0, championships: 1, all_defensive: 0,
    note: "6'4\" SG — Mad Max",
  },
  "Anthony Mason": {
    seasons: 13, career_rpg: 7.0,  best_rpg: 10.0,
    career_ppg: 11.8, career_apg: 3.0,  career_spg: 1.1, career_bpg: 0.5,
    reb_titles: 0, championships: 0, all_defensive: 0,
    note: "6'7\" PF",
  },
};

/** Rodman's career stats by season — used in career.html */
const CAREER_DATA = [
  { season: "86-87", team: "DET", rpg: 6.5,  champion: false, title: false },
  { season: "87-88", team: "DET", rpg: 11.6, champion: false, title: false },
  { season: "88-89", team: "DET", rpg: 9.4,  champion: true,  title: false },
  { season: "89-90", team: "DET", rpg: 10.8, champion: true,  title: false },
  { season: "90-91", team: "DET", rpg: 12.5, champion: false, title: false },
  { season: "91-92", team: "DET", rpg: 18.7, champion: false, title: true  },
  { season: "92-93", team: "DET", rpg: 18.3, champion: false, title: true  },
  { season: "93-94", team: "SAS", rpg: 17.3, champion: false, title: true  },
  { season: "94-95", team: "SAS", rpg: 16.8, champion: false, title: true  },
  { season: "95-96", team: "CHI", rpg: 14.9, champion: true,  title: true  },
  { season: "96-97", team: "CHI", rpg: 16.1, champion: true,  title: true  },
  { season: "97-98", team: "CHI", rpg: 15.0, champion: true,  title: true  },
  { season: "98-99", team: "LAL", rpg: 11.2, champion: false, title: false },
  { season: "99-00", team: "DAL", rpg: 14.3, champion: false, title: false },
];

/** Rebounding title streak data — used in timeline.html */
const TITLE_STREAK = [
  { season: "1991–92", team: "DET", rpg: 18.7, champion: false },
  { season: "1992–93", team: "DET", rpg: 18.3, champion: false },
  { season: "1993–94", team: "SAS", rpg: 17.3, champion: false },
  { season: "1994–95", team: "SAS", rpg: 16.8, champion: false },
  { season: "1995–96", team: "CHI", rpg: 14.9, champion: true  },
  { season: "1996–97", team: "CHI", rpg: 16.1, champion: true  },
  { season: "1997–98", team: "CHI", rpg: 15.0, champion: true  },
];

const TEAM_COLORS = { DET: "#C8102E", SAS: "#C4CED4", CHI: "#CE1141" };


// ============================================================
// SOUND ENGINE
// ============================================================

const Sound = (() => {
  let ctx = null;
  let enabled = true;
  try {
    const s = localStorage.getItem("rodman_sound");
    if (s !== null) enabled = s === "true";
  } catch (_) {}

  function getCtx() {
    if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
    if (ctx.state === "suspended") ctx.resume();
    return ctx;
  }
  function setEnabled(val) {
    enabled = val;
    try { localStorage.setItem("rodman_sound", String(val)); } catch (_) {}
  }
  function playCrowdHum(dur = 1.2) {
    if (!enabled) return;
    const c = getCtx(), n = c.sampleRate * dur;
    const buf = c.createBuffer(1, n, c.sampleRate);
    const d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * 0.15;
    const src = c.createBufferSource(); src.buffer = buf;
    const bpf = c.createBiquadFilter(); bpf.type = "bandpass"; bpf.frequency.value = 800; bpf.Q.value = 0.4;
    const gain = c.createGain();
    gain.gain.setValueAtTime(0, c.currentTime);
    gain.gain.linearRampToValueAtTime(0.4, c.currentTime + 0.3);
    gain.gain.linearRampToValueAtTime(0, c.currentTime + dur);
    src.connect(bpf); bpf.connect(gain); gain.connect(c.destination);
    src.start(); src.stop(c.currentTime + dur);
  }
  function playBuzzer() {
    if (!enabled) return;
    const c = getCtx(), osc = c.createOscillator(), gain = c.createGain();
    osc.type = "square";
    osc.frequency.setValueAtTime(220, c.currentTime);
    osc.frequency.exponentialRampToValueAtTime(110, c.currentTime + 0.5);
    gain.gain.setValueAtTime(0.18, c.currentTime);
    gain.gain.linearRampToValueAtTime(0, c.currentTime + 0.5);
    osc.connect(gain); gain.connect(c.destination);
    osc.start(); osc.stop(c.currentTime + 0.5);
  }
  function playChime() {
    if (!enabled) return;
    const c = getCtx();
    [523, 659, 784].forEach((freq, i) => {
      const osc = c.createOscillator(), gain = c.createGain();
      osc.type = "sine"; osc.frequency.value = freq;
      const t = c.currentTime + i * 0.1;
      gain.gain.setValueAtTime(0.12, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.6);
      osc.connect(gain); gain.connect(c.destination);
      osc.start(t); osc.stop(t + 0.6);
    });
  }
  return { playCrowdHum, playBuzzer, playChime, setEnabled, get enabled() { return enabled; } };
})();

function initSoundToggle() {
  const btn = document.getElementById("soundToggle");
  const icon = document.getElementById("soundIcon");
  if (!btn) return;
  const upd = () => { icon.textContent = Sound.enabled ? "🔊" : "🔇"; };
  upd();
  btn.addEventListener("click", () => {
    Sound.setEnabled(!Sound.enabled);
    upd();
    if (Sound.enabled) Sound.playCrowdHum(0.6);
  });
}


// ============================================================
// ANIMATED COUNTER
// ============================================================

function animateCounter(el, target, ms = 1000) {
  const raw = String(target).replace(/,/g, "");
  const isFloat = raw.includes(".");
  const decimals = isFloat ? raw.split(".")[1].length : 0;
  const end = parseFloat(raw);
  const start = performance.now();
  const ease = t => 1 - Math.pow(1 - t, 3);
  function step(now) {
    const p = Math.min((now - start) / ms, 1);
    const v = end * ease(p);
    el.textContent = isFloat ? v.toFixed(decimals) : Math.floor(v).toLocaleString("en-US");
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = isFloat ? end.toFixed(decimals) : end.toLocaleString("en-US");
  }
  requestAnimationFrame(step);
}


// ============================================================
// PAGE ROUTER
// ============================================================

const path = window.location.pathname;
initSoundToggle();
Sound.playCrowdHum(0.8);

if      (path.includes("ranking"))  initRankingPage();
else if (path.includes("timeline")) initTimelinePage();
else if (path.includes("career"))   initCareerPage();
else                                 initIndexPage();


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
    renderDidYouKnow(featId);
    initH2HDrawer();
  } catch (err) {
    overlay.classList.remove("visible");
    errorEl.style.display = "block";
  }
}

const ICON_MAP = {
  rebounding_titles: "👑", season_rpg: "📈",
  offensive_rebounds_season: "💥", consecutive_titles: "🔗", chaos_index: "🔥",
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
      <span class="source-badge ${sourceClass}"><span class="dot"></span>${sourceLabel}</span>
      <button class="share-btn" id="shareBtn"><span id="shareLabel">⬡ Share</span></button>
    </div>
  `;
  document.getElementById("shareBtn").addEventListener("click", handleShare);
}

function handleShare() {
  const url = window.location.href;
  const label = document.getElementById("shareLabel");
  const btn   = document.getElementById("shareBtn");
  const copy = (success) => {
    label.textContent = "✓ Copied!";
    btn.classList.add("share-copied");
    Sound.playChime();
    setTimeout(() => { label.textContent = "⬡ Share"; btn.classList.remove("share-copied"); }, 2200);
  };
  navigator.clipboard ? navigator.clipboard.writeText(url).then(copy).catch(() => fallbackCopy(url, copy))
                      : fallbackCopy(url, copy);
}
function fallbackCopy(text, cb) {
  const i = document.createElement("input"); i.value = text;
  document.body.appendChild(i); i.select(); document.execCommand("copy");
  document.body.removeChild(i); cb();
}

function renderRankingList(data, container) {
  container.innerHTML = "";
  if (!data.ranking?.length) {
    container.innerHTML = `<p style="color:var(--text-muted);text-align:center;padding:2rem;">No ranking data.</p>`;
    return;
  }
  data.ranking.forEach((player, index) => {
    const isFirst  = player.rank === 1;
    const isRodman = player.is_rodman;
    let classes = "ranking-item";
    if (isFirst)  classes += " rank-first";
    if (isRodman) classes += " is-rodman";

    const wormBadge  = isRodman ? `<span class="worm-badge">🐛 The Worm</span>` : "";
    const teamLabel  = player.team   ? `<div class="player-team">${player.team}</div>` : "";
    const seasonInfo = player.season   ? `<div class="player-team">${player.season}</div>`
                     : player.seasons ? `<div class="player-team">${player.seasons}</div>` : "";
    const hasH2H     = !isRodman && PLAYER_STATS[player.player];
    const h2hHint    = hasH2H ? `<span class="h2h-hint">⚡ vs Rodman</span>` : "";

    const item = document.createElement("div");
    item.className = classes;
    if (hasH2H) item.style.cursor = "pointer";
    item.dataset.player = player.player;

    item.innerHTML = `
      <div class="rank-number">${player.rank}</div>
      <div class="player-info">
        <div class="player-name">${player.player}${wormBadge}</div>
        ${teamLabel}${seasonInfo}
      </div>
      <div class="player-value" style="text-align:right;">
        <span class="value-number" data-target="${player.value}">0</span>
        <span class="value-unit">${data.unit}</span>
        <div>${h2hHint}</div>
      </div>
    `;

    if (hasH2H) {
      item.addEventListener("click", () => openH2H(player.player));
    }

    container.appendChild(item);

    setTimeout(() => {
      item.classList.add("visible");
      setTimeout(() => {
        const el = item.querySelector(".value-number");
        animateCounter(el, player.value, 1000);
        if (isFirst && isRodman) Sound.playChime();
      }, 150);
    }, 70 * index);
  });
}


// ============================================================
// DID YOU KNOW PANEL
// ============================================================

function renderDidYouKnow(featId) {
  const panel = document.getElementById("dykPanel");
  const dyk   = DID_YOU_KNOW[featId];
  if (!panel || !dyk) return;

  panel.style.display = "block";
  panel.innerHTML = `
    <div class="dyk-icon">${dyk.emoji}</div>
    <div class="dyk-body">
      <div class="dyk-label">DID YOU KNOW?</div>
      <div class="dyk-headline">${dyk.headline}</div>
      <p class="dyk-fact">${dyk.fact}</p>
    </div>
  `;

  // Animate in after a short delay so it doesn't compete with the ranking
  setTimeout(() => panel.classList.add("dyk-visible"), 900);
}


// ============================================================
// HEAD-TO-HEAD COMPARISON DRAWER
// ============================================================

function initH2HDrawer() {
  const overlay = document.getElementById("h2hOverlay");
  const close   = document.getElementById("h2hClose");
  overlay?.addEventListener("click", closeH2H);
  close?.addEventListener("click", closeH2H);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeH2H(); });
}

function openH2H(playerName) {
  const rodman   = PLAYER_STATS["Dennis Rodman"];
  const opponent = PLAYER_STATS[playerName];
  if (!rodman || !opponent) return;

  Sound.playBuzzer();

  const content = document.getElementById("h2hContent");
  const drawer  = document.getElementById("h2hDrawer");
  const overlay = document.getElementById("h2hOverlay");

  const stats = [
    { label: "Career RPG",        rodman: rodman.career_rpg,   opp: opponent.career_rpg,   higher: true,  fmt: v => v?.toFixed(1) ?? "N/A" },
    { label: "Best Season RPG",   rodman: rodman.best_rpg,     opp: opponent.best_rpg,     higher: true,  fmt: v => v?.toFixed(1) ?? "N/A" },
    { label: "Reb Titles",        rodman: rodman.reb_titles,   opp: opponent.reb_titles,   higher: true,  fmt: v => v ?? "0" },
    { label: "Championships",     rodman: rodman.championships, opp: opponent.championships, higher: true, fmt: v => v ?? "0" },
    { label: "Career PPG",        rodman: rodman.career_ppg,   opp: opponent.career_ppg,   higher: true,  fmt: v => v?.toFixed(1) ?? "N/A" },
    { label: "All-Defensive",     rodman: rodman.all_defensive, opp: opponent.all_defensive, higher: true, fmt: v => v ?? "N/A" },
    { label: "Career BPG",        rodman: rodman.career_bpg,   opp: opponent.career_bpg,   higher: true,  fmt: v => v?.toFixed(1) ?? "N/A" },
    { label: "Seasons Played",    rodman: rodman.seasons,      opp: opponent.seasons,      higher: false, fmt: v => v ?? "N/A" },
  ];

  const rows = stats.map(s => {
    const rv = s.rodman, ov = s.opp;
    const rodmanWins = rv != null && ov != null && (s.higher ? rv > ov : rv < ov);
    const oppWins    = rv != null && ov != null && (s.higher ? ov > rv : ov < rv);
    return `
      <tr>
        <td class="h2h-val ${rodmanWins ? 'h2h-winner' : ''}">${s.fmt(rv)}</td>
        <td class="h2h-stat-label">${s.label}</td>
        <td class="h2h-val ${oppWins ? 'h2h-winner' : ''}">${s.fmt(ov)}</td>
      </tr>`;
  }).join("");

  content.innerHTML = `
    <div class="h2h-header">
      <div class="h2h-player h2h-rodman">
        <div class="h2h-name">Dennis Rodman</div>
        <div class="h2h-note">${rodman.note}</div>
        <span class="worm-badge" style="margin-top:0.4rem;display:inline-flex;">🐛 The Worm</span>
      </div>
      <div class="h2h-vs">VS</div>
      <div class="h2h-player">
        <div class="h2h-name">${playerName}</div>
        <div class="h2h-note">${opponent.note}</div>
      </div>
    </div>
    <table class="h2h-table"><tbody>${rows}</tbody></table>
    <p class="h2h-footer">Highlighted values = better stat. Career regular season stats.</p>
  `;

  overlay.classList.add("active");
  drawer.classList.add("open");
}

function closeH2H() {
  document.getElementById("h2hDrawer")?.classList.remove("open");
  document.getElementById("h2hOverlay")?.classList.remove("active");
}


// ============================================================
// TIMELINE PAGE — Animated bar chart
// ============================================================

function initTimelinePage() {
  const container = document.getElementById("timelineChart");
  if (!container) return;

  const maxRpg = Math.max(...TITLE_STREAK.map(d => d.rpg));

  container.innerHTML = TITLE_STREAK.map((d, i) => {
    const pct       = ((d.rpg / (maxRpg * 1.1)) * 100).toFixed(1);
    const color     = d.champion ? "var(--gold)" : TEAM_COLORS[d.team] || "var(--red)";
    const badge     = d.champion ? `<span class="bar-badge">💍 Champion</span>` : "";
    const teamLabel = `<span class="bar-team">${d.team}</span>`;

    return `
      <div class="bar-row" style="animation-delay:${i * 0.12}s">
        <div class="bar-season">${d.season}</div>
        <div class="bar-track">
          <div class="bar-fill"
               data-width="${pct}"
               style="background: ${color}; width: 0%;">
            <span class="bar-value">${d.rpg} RPG</span>
          </div>
        </div>
        <div class="bar-meta">${teamLabel}${badge}</div>
      </div>`;
  }).join("");

  // Trigger bar animations after a frame
  requestAnimationFrame(() => {
    container.querySelectorAll(".bar-fill").forEach((bar, i) => {
      setTimeout(() => {
        bar.style.width = bar.dataset.width + "%";
      }, 200 + i * 120);
    });
  });
}


// ============================================================
// CAREER ARC PAGE — SVG line chart
// ============================================================

function initCareerPage() {
  const wrapper = document.getElementById("careerChart");
  const cards   = document.getElementById("seasonCards");
  if (!wrapper) return;

  drawCareerChart(wrapper);
  renderSeasonCards(cards);
}

function drawCareerChart(container) {
  const W = container.clientWidth || 800;
  const H = 320;
  const PAD = { top: 30, right: 24, bottom: 50, left: 48 };
  const cW = W - PAD.left - PAD.right;
  const cH = H - PAD.top  - PAD.bottom;

  const xs = CAREER_DATA.map((_, i) => PAD.left + (i / (CAREER_DATA.length - 1)) * cW);
  const maxRpg = 20;
  const ys = CAREER_DATA.map(d => PAD.top + cH - (d.rpg / maxRpg) * cH);

  // Build polyline path
  const linePath = xs.map((x, i) => `${i === 0 ? "M" : "L"}${x},${ys[i]}`).join(" ");

  // Y-axis gridlines
  const gridLines = [5, 10, 15, 20].map(v => {
    const y = PAD.top + cH - (v / maxRpg) * cH;
    return `
      <line x1="${PAD.left}" y1="${y}" x2="${PAD.left + cW}" y2="${y}"
            stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
      <text x="${PAD.left - 6}" y="${y + 4}" text-anchor="end"
            font-size="10" fill="var(--text-muted)" font-family="var(--font-mono)">${v}</text>`;
  }).join("");

  // X-axis labels
  const xLabels = CAREER_DATA.map((d, i) => `
    <text x="${xs[i]}" y="${H - 10}" text-anchor="middle"
          font-size="9" fill="var(--text-muted)" font-family="var(--font-mono)"
          transform="rotate(-35 ${xs[i]} ${H - 10})">${d.season}</text>`
  ).join("");

  // Data points
  const points = CAREER_DATA.map((d, i) => {
    const r     = d.champion && d.title ? 8 : d.champion ? 7 : d.title ? 7 : 5;
    const color = d.champion && d.title ? "var(--gold)"
                : d.champion            ? "var(--gold)"
                : d.title               ? "var(--red)"
                : "var(--red)";
    const stroke = d.champion ? "var(--gold)" : "var(--red)";
    const inner  = d.champion ? `<circle cx="${xs[i]}" cy="${ys[i]}" r="3" fill="var(--black)"/>` : "";
    return `
      <circle cx="${xs[i]}" cy="${ys[i]}" r="${r}"
              fill="${color}" stroke="${stroke}" stroke-width="2"
              class="career-point" data-index="${i}"
              style="cursor:pointer; transition: r 0.15s;"/>
      ${inner}`;
  }).join("");

  // Shaded area under the line
  const areaPath = linePath
    + ` L${xs[xs.length-1]},${PAD.top + cH} L${xs[0]},${PAD.top + cH} Z`;

  container.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg"
         style="width:100%;height:auto;overflow:visible;">
      <defs>
        <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stop-color="var(--red)" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="var(--red)" stop-opacity="0"/>
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="2" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>

      ${gridLines}

      <!-- Area fill -->
      <path d="${areaPath}" fill="url(#areaGrad)"/>

      <!-- Main line -->
      <path d="${linePath}" fill="none" stroke="var(--red)" stroke-width="2.5"
            filter="url(#glow)" stroke-linecap="round" stroke-linejoin="round"
            class="career-line"/>

      ${points}
      ${xLabels}

      <!-- Y-axis label -->
      <text x="${PAD.left - 32}" y="${PAD.top + cH / 2}" text-anchor="middle"
            font-size="10" fill="var(--text-muted)" font-family="var(--font-mono)"
            transform="rotate(-90 ${PAD.left - 32} ${PAD.top + cH / 2})">RPG</text>
    </svg>`;

  // Draw the line animating in
  const line = container.querySelector(".career-line");
  if (line) {
    const len = line.getTotalLength?.() || 1000;
    line.style.strokeDasharray  = len;
    line.style.strokeDashoffset = len;
    requestAnimationFrame(() => {
      line.style.transition = "stroke-dashoffset 1.8s ease";
      line.style.strokeDashoffset = "0";
    });
  }

  // Tooltip on hover
  const tooltip = document.getElementById("chartTooltip");
  container.querySelectorAll(".career-point").forEach(pt => {
    pt.addEventListener("mouseenter", e => {
      const idx = parseInt(pt.dataset.index);
      const d   = CAREER_DATA[idx];
      const badges = [];
      if (d.champion) badges.push("💍 Champion");
      if (d.title)    badges.push("👑 Reb Title");
      tooltip.innerHTML = `
        <strong>${d.season} — ${d.team}</strong><br>
        ${d.rpg} RPG${badges.length ? "<br>" + badges.join(" · ") : ""}
      `;
      tooltip.style.display = "block";
      const rect = container.getBoundingClientRect();
      tooltip.style.left = (e.clientX - rect.left + 12) + "px";
      tooltip.style.top  = (e.clientY - rect.top  - 10) + "px";
    });
    pt.addEventListener("mouseleave", () => { tooltip.style.display = "none"; });
    pt.addEventListener("click", () => { if (Sound.enabled) Sound.playChime(); });
  });
}

function renderSeasonCards(container) {
  if (!container) return;
  container.innerHTML = CAREER_DATA.map((d, i) => {
    const badges = [];
    if (d.champion) badges.push(`<span class="season-badge champ-badge">💍</span>`);
    if (d.title)    badges.push(`<span class="season-badge title-badge">👑</span>`);
    return `
      <div class="season-card ${d.champion ? 'is-champion' : ''} ${d.title ? 'is-title' : ''}"
           style="animation-delay:${i * 0.04}s">
        <div class="season-year">${d.season}</div>
        <div class="season-team">${d.team}</div>
        <div class="season-rpg">${d.rpg}</div>
        <div class="season-rpg-label">RPG</div>
        <div class="season-badges">${badges.join("")}</div>
      </div>`;
  }).join("");
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
