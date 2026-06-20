// ================================================================
// kundali.js — AstroLogic Complete Frontend v2
// Fixes: getRashi, house analysis, dasha timeline, download
// ================================================================

const safe = v => (v == null || v === "") ? "—" : v;
const safeNum = (v, fb = 0) => { const n = parseFloat(v); return isNaN(n) ? fb : n; };

const SHORT = {Sun:"Su",Moon:"Mo",Mars:"Ma",Mercury:"Me",Jupiter:"Ju",Venus:"Ve",Saturn:"Sa",Rahu:"Ra",Ketu:"Ke",Lagna:"La"};
const RASHI_FULL  = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"];
const RASHI_SHORT = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"];
const RASHI_EN    = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];

const STRENGTH_MAP = {
  Sun:{exalt:"Mesha",debil:"Tula",own:["Simha"]},
  Moon:{exalt:"Vrishabha",debil:"Vrischika",own:["Karka"]},
  Mars:{exalt:"Makara",debil:"Karka",own:["Mesha","Vrischika"]},
  Mercury:{exalt:"Kanya",debil:"Meena",own:["Mithuna","Kanya"]},
  Jupiter:{exalt:"Karka",debil:"Makara",own:["Dhanu","Meena"]},
  Venus:{exalt:"Meena",debil:"Kanya",own:["Vrishabha","Tula"]},
  Saturn:{exalt:"Tula",debil:"Mesha",own:["Makara","Kumbha"]},
  Rahu:{exalt:"Mithuna",debil:"Dhanu",own:[]},
  Ketu:{exalt:"Dhanu",debil:"Mithuna",own:[]},
};

const HOUSE_MEANINGS = {
  1:"Self, personality, vitality & physical appearance",
  2:"Wealth, family, speech & food habits",
  3:"Courage, siblings, communication & short travel",
  4:"Mother, home, property & inner happiness",
  5:"Creativity, children, intelligence & past life merit",
  6:"Health, enemies, debts & daily routine",
  7:"Marriage, partnerships & business dealings",
  8:"Longevity, occult, transformation & hidden wealth",
  9:"Luck, dharma, father & higher learning",
  10:"Career, status, authority & public image",
  11:"Income, gains, elder siblings & fulfilment of desires",
  12:"Losses, foreign lands, spirituality & moksha"
};

const HOUSE_KARAKAS = {
  1:"Sun (vitality)", 2:"Jupiter (wealth)", 3:"Mars (courage)", 4:"Moon (happiness)",
  5:"Jupiter (children)", 6:"Saturn (service)", 7:"Venus (marriage)", 8:"Saturn (longevity)",
  9:"Jupiter (fortune)", 10:"Sun (career)", 11:"Jupiter (gains)", 12:"Saturn (liberation)"
};

const PLANET_KARAKAS = {
  Sun:"Soul, authority, father, government, health",
  Moon:"Mind, emotions, mother, public, water",
  Mars:"Energy, courage, siblings, land, accidents",
  Mercury:"Intellect, communication, business, skin",
  Jupiter:"Wisdom, children, wealth, teachers, spirituality",
  Venus:"Love, beauty, arts, marriage, luxury",
  Saturn:"Karma, discipline, delays, servants, old age",
  Rahu:"Obsessions, foreign, technology, ambition, illusion",
  Ketu:"Spirituality, past karma, liberation, detachment"
};

// North-Indian chart: visual position → actual house slot
const POSITION_MAP = {1:1,2:12,3:11,4:2,5:10,6:3,7:9,8:4,9:5,10:6,11:7,12:8};

// SVG coordinates for each visual slot
const HOUSE_COORDS = {
  1:{nx:300,ny:78,px:300,py:114},
  2:{nx:168,ny:60,px:156,py:96},
  3:{nx:70,ny:118,px:62,py:154},
  4:{nx:70,ny:208,px:108,py:208},
  5:{nx:70,ny:298,px:62,py:262},
  6:{nx:168,ny:356,px:156,py:320},
  7:{nx:300,ny:368,px:300,py:332},
  8:{nx:432,ny:356,px:444,py:320},
  9:{nx:530,ny:298,px:538,py:262},
  10:{nx:530,ny:208,px:492,py:208},
  11:{nx:530,ny:118,px:538,py:154},
  12:{nx:432,ny:60,px:444,py:96},
};

const DASHA_YEARS = {Ketu:7,Venus:20,Sun:6,Moon:10,Mars:7,Rahu:18,Jupiter:16,Saturn:19,Mercury:17};
const DASHA_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"];

let _data = null, _person = null, _cities = [];

// ── Boot ──────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("generateBtn")?.addEventListener("click", generateKundali);
  document.getElementById("downloadBtn")?.addEventListener("click", downloadPDF);
  setupCityAutocomplete();
  loadCities();
});

async function loadCities() {
  try {
    const r = await fetch("/api/cities");
    if (r.ok) _cities = await r.json();
  } catch {}
}

function setupCityAutocomplete() {
  const input = document.getElementById("city");
  const list  = document.getElementById("cityDropdown");
  if (!input || !list) return;
  input.addEventListener("input", () => {
    const q = input.value.trim().toLowerCase();
    list.innerHTML = "";
    if (q.length < 2) { list.style.display = "none"; return; }
    const matches = _cities.filter(c => c.toLowerCase().startsWith(q)).slice(0, 10);
    if (!matches.length) { list.style.display = "none"; return; }
    matches.forEach(city => {
      const li = document.createElement("li");
      li.textContent = city;
      li.addEventListener("click", () => { input.value = city; list.style.display = "none"; });
      list.appendChild(li);
    });
    list.style.display = "block";
  });
  document.addEventListener("click", e => { if (!input.contains(e.target)) list.style.display = "none"; });
}

// ── getRashi (FIXED) ──────────────────────────────────────────────
// Returns 0-based index of the sign in house `h` given lagna sign name
function getRashiIndex(lagnaSign, h) {
  const i = RASHI_FULL.indexOf(lagnaSign);
  if (i === -1) return (h - 1) % 12;
  return (i + h - 1) % 12;
}

// ── Chart Renderer (North Indian) ────────────────────────────────
function renderChart(containerId, housesData, lagnaSign, bg) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const lagnaIndex = RASHI_FULL.indexOf(lagnaSign);
  let svg = `<svg viewBox="0 0 600 420" style="width:100%;max-width:520px;display:block;margin:auto">`;
  svg += `<rect x="10" y="10" width="580" height="400" fill="${bg}" stroke="rgba(245,193,108,0.3)" stroke-width="1.5" rx="4"/>`;
  svg += `<line x1="10" y1="10" x2="590" y2="410" stroke="rgba(245,193,108,0.25)" stroke-width="1"/>`;
  svg += `<line x1="590" y1="10" x2="10" y2="410" stroke="rgba(245,193,108,0.25)" stroke-width="1"/>`;
  svg += `<polygon points="300,10 590,210 300,410 10,210" stroke="rgba(245,193,108,0.25)" stroke-width="1" fill="none"/>`;

  for (let pos = 1; pos <= 12; pos++) {
    const house = POSITION_MAP[pos];
    const c = HOUSE_COORDS[pos];
    const rashiIdx = lagnaIndex === -1 ? (house - 1) % 12 : (lagnaIndex + house - 1) % 12;
    const rs = RASHI_SHORT[rashiIdx];
    const label = house === 1 ? `La` : rs;
    const numColor = house === 1 ? "#f5c16c" : "#6a9ab0";
    svg += `<text x="${c.nx}" y="${c.ny}" class="num" text-anchor="middle" style="fill:${numColor};font-weight:${house===1?700:500}">${label}</text>`;
    const planets = (housesData && housesData[house]) ? housesData[house].filter(p => p !== "Lagna") : [];
    if (planets.length) {
      const lh = 14, th = (planets.length - 1) * lh, sy = c.py - th / 2;
      planets.forEach((p, i) => {
        const isSpecial = ["Sun","Moon","Jupiter"].includes(p);
        svg += `<text x="${c.px}" y="${sy + i * lh}" class="planet-text" text-anchor="middle" style="fill:${isSpecial?"#8b2a2a":"#6b2222"}">${SHORT[p] || p}</text>`;
      });
    }
  }
  svg += `</svg>`;
  el.innerHTML = svg;
}

// ── Planet Table ──────────────────────────────────────────────────
function getStrength(name, sign) {
  const s = STRENGTH_MAP[name];
  if (!s) return {label:"—", style:""};
  if (s.exalt === sign) return {label:"⬆ Exalted",    style:"color:#4ade80;font-weight:600"};
  if (s.debil === sign) return {label:"⬇ Debilitated",style:"color:#f87171;font-weight:600"};
  if (s.own.includes(sign)) return {label:"★ Own Sign", style:"color:#f5c16c;font-weight:600"};
  return {label:"Neutral", style:"color:#888"};
}

function renderPlanetTable(planets) {
  if (!planets?.length) return;
  const rows = planets.map(p => {
    const {label, style} = getStrength(p.name, p.sign);
    const nm = p.retrograde ? `${safe(p.name)} <span class="badge badge-gold ms-1" style="font-size:9px">R</span>` : safe(p.name);
    const karaka = PLANET_KARAKAS[p.name] || "—";
    return `<tr>
      <td>${nm}</td>
      <td>${safe(p.sign)}</td>
      <td class="font-monospace">${safe(p.degree)}</td>
      <td><strong>${safe(p.house)}</strong></td>
      <td>${safe(p.nakshatra)}</td>
      <td>${safe(p.pada)}</td>
      <td>${safe(p.navamsa) || "—"}</td>
      <td style="${style}">${label}</td>
      <td><span class="badge ${p.retrograde ? 'bg-warning text-dark' : 'bg-success'}" style="font-size:9px">${p.retrograde ? "Retro" : "Direct"}</span></td>
    </tr>`;
  });
  document.getElementById("planetTable").innerHTML = rows.join("");
}

// ── Scores ────────────────────────────────────────────────────────
function renderScores(s) {
  const SCORE_COLORS = {
    overall_strength:"#7c6af5", career_score:"#f5c16c", finance_score:"#4ade80",
    marriage_score:"#60d5f5", health_score:"#f87171", mental_score:"#c084fc", spirituality_score:"#fbbf24"
  };
  [
    ["overallScore","overallBar","overall_strength"],
    ["careerScore","careerBar","career_score"],
    ["financeScore","financeBar","finance_score"],
    ["relationshipScore","relationshipBar","marriage_score"],
    ["healthScore","healthBar","health_score"],
    ["mentalScore","mentalBar","mental_score"],
    ["spiritualScore","spiritualBar","spirituality_score"],
  ].forEach(([sid, bid, key]) => {
    const v = safeNum(s[key], 0);
    const el = document.getElementById(sid); if (el) el.innerText = v + "%";
    const bar = document.getElementById(bid);
    if (bar) { bar.style.width = Math.min(v, 100) + "%"; bar.style.background = SCORE_COLORS[key] || "#888"; }
  });
}

// ── Yogas ─────────────────────────────────────────────────────────
function renderYogas(yogas) {
  const c = document.getElementById("yogaContainer");
  if (!c) return;
  if (!yogas?.length) { c.innerHTML = `<p class="text-muted small">No yoga data</p>`; return; }
  const present = yogas.filter(y => y.present);
  const absent  = yogas.filter(y => !y.present);
  let html = "";
  if (present.length) {
    html += `<p style="color:var(--green);font-size:12px;margin-bottom:10px">✓ ${present.length} active yoga${present.length > 1 ? "s" : ""} detected</p>`;
    html += present.map(y => `<div class="yoga-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px">
        <h6 style="color:var(--green);font-size:13px;margin:0">${y.name}</h6>
        <span class="badge-gold" style="font-size:10px;white-space:nowrap">${y.strength || "Active"}</span>
      </div>
      <p class="text-muted mb-0" style="font-size:12px">${y.description}</p>
    </div>`).join("");
  } else {
    html += `<p class="text-muted small">No active yogas detected in this chart</p>`;
  }
  if (absent.length) {
    html += `<details class="mt-2"><summary style="color:var(--text-dim);font-size:12px;cursor:pointer">Absent yogas (${absent.length}) ▸</summary>
    <div class="mt-2">${absent.map(y => `<div style="padding:5px 10px;border-left:2px solid rgba(255,255,255,0.1);margin-bottom:5px;border-radius:4px">
      <span style="color:rgba(200,200,200,0.4);font-size:12px">${y.name}</span>
    </div>`).join("")}</div></details>`;
  }
  c.innerHTML = html;
}

// ── Doshas ────────────────────────────────────────────────────────
function renderDoshas(doshas) {
  const c = document.getElementById("doshaContainer");
  if (!c) return;
  if (!doshas?.length) { c.innerHTML = `<p class="text-muted small">No dosha data</p>`; return; }
  const present = doshas.filter(d => d.present);
  const absent  = doshas.filter(d => !d.present);
  const cls = {High:"dosha-high", Medium:"dosha-med"};
  const col = {High:"#f87171", Medium:"#f5c16c"};
  let html = "";
  if (present.length) {
    html += present.map(d => `<div class="dosha-card ${cls[d.severity] || 'dosha-med'}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
        <strong style="color:${col[d.severity] || '#f5c16c'};font-size:13px">${d.name}</strong>
        <span class="badge" style="background:rgba(248,113,113,0.15);color:${col[d.severity] || '#f5c16c'};font-size:10px;border-radius:4px;padding:2px 7px">${d.severity}</span>
      </div>
      <p class="text-muted mb-2" style="font-size:12px">${d.description}</p>
      ${d.remedies?.length ? `<details><summary style="font-size:12px;color:var(--text-dim);cursor:pointer">Remedies (${d.remedies.length}) ▸</summary>
        <ul style="margin-top:6px;padding-left:16px">${d.remedies.map(r => `<li style="font-size:12px;color:#bbb;margin-bottom:3px">${r}</li>`).join("")}</ul>
      </details>` : ""}
    </div>`).join("");
  } else {
    html += `<div class="dosha-card dosha-ok">
      <strong style="color:var(--green)">✓ No major doshas detected</strong>
      <p class="text-muted mb-0 mt-1" style="font-size:12px">This chart is relatively free from major planetary afflictions.</p>
    </div>`;
  }
  if (absent.length) {
    html += `<details class="mt-1"><summary style="font-size:12px;color:var(--text-dim);cursor:pointer">Absent doshas (${absent.length}) ▸</summary>
    <div class="mt-2">${absent.map(d => `<div style="padding:5px 10px;border-left:2px solid rgba(74,222,128,0.2);margin-bottom:4px;border-radius:4px">
      <span style="color:rgba(74,222,128,0.6);font-size:12px">✓ ${d.name}</span>
    </div>`).join("")}</div></details>`;
  }
  c.innerHTML = html;
}

// ── House Analysis (FIXED — uses getRashiIndex) ───────────────────
function renderHouseAnalysis(houses, lagnaSign) {
  const c = document.getElementById("houseAnalysis");
  if (!c || !houses) return;
  let html = "";
  for (let h = 1; h <= 12; h++) {
    const planets = (houses[h] || []).filter(p => p !== "Lagna");
    const rashiIdx = getRashiIndex(lagnaSign, h);
    const sign = RASHI_FULL[rashiIdx] || "";
    const signEn = RASHI_EN[rashiIdx] || "";
    const meaning = HOUSE_MEANINGS[h] || "";
    const karaka = HOUSE_KARAKAS[h] || "";
    const hasOccupants = planets.length > 0;
    const badges = planets.map(p => {
      const {style} = getStrength(p, "");
      return `<span class="badge-gold me-1" style="margin-bottom:3px">${p}</span>`;
    }).join("");
    html += `<div class="house-row ${hasOccupants ? 'house-occupied' : ''}">
      <div style="flex-shrink:0">
        <span class="house-num">${h}</span>
      </div>
      <div style="flex:1;min-width:0">
        <div style="display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-bottom:4px">
          <strong style="color:var(--gold);font-size:13px">${sign}</strong>
          <span style="color:var(--text-dim);font-size:11px">(${signEn})</span>
          <span style="color:var(--blue);font-size:11px">· ${meaning}</span>
        </div>
        <div style="font-size:11px;color:rgba(200,200,200,0.4);margin-bottom:${hasOccupants?'6px':'0'}">Karaka: ${karaka}</div>
        ${hasOccupants ? `<div>${badges}</div>` : `<span style="font-size:11px;color:rgba(200,200,200,0.25)">Empty house</span>`}
      </div>
    </div>`;
  }
  c.innerHTML = html || `<p class="text-muted small">No house data</p>`;
}

// ── Vimshottari Dasha Timeline ────────────────────────────────────
function renderDashaTimeline(data) {
  const c = document.getElementById("dashaTimeline");
  if (!c) return;
  if (!data.mahadasha || !data.antardasha_list) { c.innerHTML = ""; return; }

  const birthYear = _person ? parseInt(_person.dob.split("-")[0]) : new Date().getFullYear();
  const balYears = parseFloat(data.dasha_balance) || 0;
  const currentMaha = data.mahadasha;
  const mahaIdx = DASHA_ORDER.indexOf(currentMaha);

  // Build mahadasha sequence from birth
  let rows = [];
  let yearCursor = birthYear;
  // Find the start of the current mahadasha
  const yearsSpent = DASHA_YEARS[currentMaha] - balYears;
  yearCursor -= yearsSpent;

  for (let i = 0; i < 9; i++) {
    const lord = DASHA_ORDER[(mahaIdx + i) % 9];
    const yrs = DASHA_YEARS[lord];
    const start = Math.round(yearCursor);
    const end = Math.round(yearCursor + yrs);
    const isCurrent = i === 0;
    rows.push({lord, start, end, yrs, isCurrent});
    yearCursor += yrs;
  }

  // Antardasha within current mahadasha
  const antarList = data.antardasha_list || [];

  let html = `
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
    <div>
      <div style="font-size:11px;font-weight:700;color:var(--gold);letter-spacing:1px;text-transform:uppercase;margin-bottom:12px">Mahadasha Timeline</div>
      ${rows.map(r => `
      <div style="display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:8px;margin-bottom:5px;
        background:${r.isCurrent ? 'rgba(245,193,108,0.1)' : 'rgba(255,255,255,0.02)'};
        border:1px solid ${r.isCurrent ? 'rgba(245,193,108,0.3)' : 'rgba(255,255,255,0.06)'}">
        <div style="width:8px;height:8px;border-radius:50%;background:${r.isCurrent ? 'var(--gold)' : 'rgba(255,255,255,0.15)'};flex-shrink:0"></div>
        <div style="flex:1">
          <span style="color:${r.isCurrent ? 'var(--gold)' : 'var(--text)'};font-size:13px;font-weight:${r.isCurrent?600:400}">${r.lord}</span>
          <span style="color:var(--text-dim);font-size:11px;margin-left:6px">${r.start}–${r.end}</span>
        </div>
        <span style="color:var(--text-dim);font-size:11px">${r.yrs}y</span>
        ${r.isCurrent ? '<span class="badge-gold" style="font-size:9px">Current</span>' : ''}
      </div>`).join("")}
    </div>
    <div>
      <div style="font-size:11px;font-weight:700;color:var(--blue);letter-spacing:1px;text-transform:uppercase;margin-bottom:12px">Antardasha (sub-periods)</div>
      <div style="font-size:11px;color:var(--text-dim);margin-bottom:8px">Within ${currentMaha} Mahadasha:</div>
      ${antarList.map((a, i) => `
      <div style="display:flex;align-items:center;gap:10px;padding:7px 10px;border-radius:7px;margin-bottom:4px;
        background:${i===0?'rgba(155,220,255,0.07)':'rgba(255,255,255,0.02)'};
        border:1px solid ${i===0?'rgba(155,220,255,0.2)':'rgba(255,255,255,0.05)'}">
        <div style="width:6px;height:6px;border-radius:50%;background:${i===0?'var(--blue)':'rgba(255,255,255,0.15)'};flex-shrink:0"></div>
        <span style="color:${i===0?'var(--blue)':'var(--text)'};font-size:12px;flex:1;font-weight:${i===0?600:400}">${a.lord}</span>
        <span style="color:var(--text-dim);font-size:11px">${a.years}y</span>
        ${i===0?'<span class="badge" style="background:rgba(155,220,255,0.12);color:var(--blue);font-size:9px;border-radius:3px;padding:1px 6px">Active</span>':''}
      </div>`).join("")}
    </div>
  </div>`;
  c.innerHTML = html;
}

// ── Main Generate ─────────────────────────────────────────────────
async function generateKundali() {
  const name = document.getElementById("fullName").value.trim();
  const dob  = document.getElementById("dob").value;
  const tob  = document.getElementById("tob").value;
  const city = document.getElementById("city").value.trim();
  if (!name || !dob || !tob || !city) { showToast("Please fill all fields", "error"); return; }
  const [year, month, day] = dob.split("-").map(Number);
  const [hour, minute]     = tob.split(":").map(Number);
  if (!year || !month || !day || isNaN(hour) || isNaN(minute)) { showToast("Invalid date or time", "error"); return; }

  const btn = document.getElementById("generateBtn");
  btn.disabled = true; btn.innerText = "Calculating…";

  try {
    const res = await fetch("/api/kundali", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({year, month, day, hour, minute, city})
    });
    if (!res.ok) { showToast("Server error: " + res.status, "error"); return; }
    const data = await res.json();
    _data = data; _person = {name, dob, tob, city};

    // Birth Details
    document.getElementById("displayName").innerText  = name;
    document.getElementById("displayDob").innerText   = dob;
    document.getElementById("displayTob").innerText   = tob + " IST";
    document.getElementById("displayCity").innerText  = city;
    document.getElementById("displayLagna").innerText = [
      safe(data.lagna), data.lagna_degree || "",
      data.lagna_nakshatra ? `(${data.lagna_nakshatra} P${data.lagna_pada})` : ""
    ].filter(Boolean).join(" ");

    const moon = data.planets?.find(p => p.name === "Moon");
    document.getElementById("moonSign").innerText    = moon ? `${safe(moon.sign)} ${safe(moon.degree)}` : "—";
    document.getElementById("nakshatra").innerText   = data.nakshatra ? `${data.nakshatra} (Pada ${safe(data.nakshatra_pada)})` : "—";
    document.getElementById("ayanamsa").innerText    = safe(data.ayanamsa) + "°";
    document.getElementById("tithi").innerText       = data.tithi_name && data.paksha ? `${data.tithi_name} (${data.paksha})` : safe(data.tithi_name);
    document.getElementById("birthYoga").innerText   = safe(data.yoga_name);
    document.getElementById("karana").innerText      = safe(data.karana_name);
    document.getElementById("dashaBalance").innerText = safe(data.dasha_balance);

    // Charts
    renderChart("d1Chart", data.houses, data.lagna, "rgba(139,87,42,0.08)");
    if (data.d9_houses) renderChart("d9Chart", data.d9_houses, data.d9_lagna || data.lagna, "rgba(42,87,139,0.08)");

    // Planets, scores, yogas, doshas
    renderPlanetTable(data.planets);
    if (data.scores) renderScores(data.scores);
    renderYogas(data.yogas);
    renderDoshas(data.doshas);

    // House Analysis (all 12 houses now shown)
    renderHouseAnalysis(data.houses, data.lagna);

    // Dasha
    document.getElementById("mahadasha").innerText         = safe(data.mahadasha);
    document.getElementById("antardasha").innerText        = safe(data.antardasha);
    document.getElementById("dashaBalanceDisplay").innerText = safe(data.dasha_balance);
    renderDashaTimeline(data);

    // Show download btn and scroll to results
    document.getElementById("downloadBtn").style.display = "inline-flex";
    document.getElementById("resultsSection").style.display = "block";
    initChat();  // Activate smart chart-aware chat
    setTimeout(() => document.getElementById("resultsSection").scrollIntoView({behavior:"smooth"}), 100);
    showToast("Kundali generated successfully", "success");
  } catch (err) {
    console.error(err);
    showToast("Error: " + err.message, "error");
  } finally {
    btn.disabled = false; btn.innerText = "Generate Kundali";
  }
}

// ── Toast ──────────────────────────────────────────────────────────
function showToast(msg, type = "info") {
  const t = document.createElement("div");
  const color = type === "success" ? "#4ade80" : type === "error" ? "#f87171" : "#9bdcff";
  t.style.cssText = `position:fixed;bottom:24px;right:24px;background:rgba(1,8,18,0.95);border:1px solid ${color};
    color:${color};padding:12px 20px;border-radius:10px;font-size:13px;z-index:9999;
    animation:fadeInUp .3s ease;box-shadow:0 8px 24px rgba(0,0,0,0.4)`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

//── PDF Download ──────────────────────────────────────────────────
function downloadPDF() {
  if (!_data || !_person) { showToast("Please generate kundali first", "error"); return; }
  const d = _data, p = _person;
  const d1SVG = document.getElementById("d1Chart")?.innerHTML || "";
  const d9SVG = document.getElementById("d9Chart")?.innerHTML || "";
  const moon = (d.planets || []).find(pl => pl.name === "Moon");

  const planetRows = (d.planets || []).map(pl => {
    const s = STRENGTH_MAP[pl.name];
    let strength = "Neutral";
    if (s) {
      if (s.exalt === pl.sign) strength = "⬆ Exalted";
      else if (s.debil === pl.sign) strength = "⬇ Debilitated";
      else if (s.own?.includes(pl.sign)) strength = "★ Own Sign";
    }
    return `<tr>
      <td><strong>${safe(pl.name)}</strong>${pl.retrograde ? " <em style='color:#e67e22'>(R)</em>" : ""}</td>
      <td>${safe(pl.sign)}</td><td>${safe(pl.degree)}</td>
      <td><b>${safe(pl.house)}</b></td><td>${safe(pl.nakshatra)}</td>
      <td>${safe(pl.pada)}</td><td>${safe(pl.navamsa) || "—"}</td>
      <td style="color:${strength.includes('Exalted')?'#27ae60':strength.includes('Debilitated')?'#c0392b':strength.includes('Own')?'#d4a017':'#666'}">${strength}</td>
      <td>${pl.retrograde ? "Retrograde" : "Direct"}</td>
    </tr>`;
  }).join("");

  const allHouseRows = Array.from({length:12},(_,i)=>{
    const h = i + 1;
    const rashiIdx = getRashiIndex(d.lagna, h);
    const sign = RASHI_FULL[rashiIdx] || "";
    const meaning = HOUSE_MEANINGS[h] || "";
    const planets = (d.houses[h] || []).filter(x => x !== "Lagna");
    return `<tr>
      <td><b>H${h}</b></td>
      <td>${sign}</td>
      <td style="color:#888;font-size:11px">${meaning}</td>
      <td>${planets.length ? planets.join(", ") : '<span style="color:#ccc">—</span>'}</td>
    </tr>`;
  }).join("");

  const activeYogas  = (d.yogas  || []).filter(y => y.present);
  const activeDoshas = (d.doshas || []).filter(ds => ds.present);
  const sc = d.scores || {};

  const scoreHTML = [
    ["Overall Strength", sc.overall_strength, "#7c6af5"],
    ["Career",           sc.career_score,      "#d89b3c"],
    ["Finance",          sc.finance_score,      "#22c55e"],
    ["Relationship",     sc.marriage_score,     "#0ea5e9"],
    ["Health",           sc.health_score,       "#ef4444"],
    ["Mental",           sc.mental_score,       "#a855f7"],
    ["Spirituality",     sc.spirituality_score, "#f59e0b"],
  ].map(([lbl, val, color]) => `
    <div style="margin-bottom:10px">
      <div style="display:flex;justify-content:space-between;margin-bottom:3px">
        <span style="font-size:12px;color:#555">${lbl}</span>
        <span style="font-size:12px;font-weight:700;color:#333">${val ?? 0}%</span>
      </div>
      <div style="background:#eee;border-radius:4px;height:6px">
        <div style="background:${color};height:6px;border-radius:4px;width:${Math.min(val || 0, 100)}%"></div>
      </div>
    </div>`).join("");

  const antarList = (d.antardasha_list || []).map((a, i) =>
    `<span style="display:inline-block;margin:3px 4px;padding:3px 10px;background:${i===0?'#8b1a1a':'#f5e6c8'};color:${i===0?'#fff':'#5a2d0c'};border-radius:4px;font-size:11px">${a.lord} (${a.years}y)</span>`
  ).join("");

  const w = window.open("", "_blank", "width=1050,height=820");
  w.document.write(`<!DOCTYPE html><html><head>
  <title>Kundali — ${p.name}</title>
  <style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:"Segoe UI",Arial,sans-serif;color:#1a0a00;background:#fff;font-size:13px;line-height:1.5}
  .page{max-width:980px;margin:0 auto;padding:28px 32px}
  .header{text-align:center;padding:22px 0 18px;border-bottom:3px double #8b1a1a;margin-bottom:24px}
  .header h1{font-size:32px;color:#8b1a1a;letter-spacing:5px;font-weight:700;margin-bottom:4px}
  .header h2{font-size:15px;color:#888;font-weight:400}
  .header .meta{font-size:11px;color:#bbb;margin-top:6px}
  .sec{margin-bottom:22px}
  .sec-title{font-size:11px;background:#8b1a1a;color:#fff;padding:5px 12px;border-radius:4px;margin-bottom:12px;letter-spacing:1.5px;text-transform:uppercase;font-weight:600}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:22px}
  .grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:22px}
  .dr{display:flex;margin-bottom:5px;font-size:12px;line-height:1.4}
  .dl{color:#888;min-width:160px;flex-shrink:0}
  .dv{color:#1a0a00;font-weight:600}
  table{width:100%;border-collapse:collapse;font-size:11.5px}
  th{background:#f5e6c8;color:#5a2d0c;padding:6px 8px;text-align:left;font-weight:700;font-size:11px;letter-spacing:.5px}
  td{padding:5px 8px;border-bottom:1px solid #f0e8d8;vertical-align:middle}
  tr:nth-child(even) td{background:#faf7f2}
  .yoga-item{padding:8px 10px;margin-bottom:7px;border-left:3px solid #22c55e;background:#f0fdf4;border-radius:4px}
  .yoga-item h4{font-size:12px;color:#166534;margin-bottom:2px;font-weight:600}
  .yoga-item p{font-size:11px;color:#555;margin:0}
  .dosha-item{padding:8px 10px;margin-bottom:7px;border-radius:4px}
  .dosha-high{border-left:3px solid #ef4444;background:#fff5f5}
  .dosha-med{border-left:3px solid #f59e0b;background:#fffbeb}
  .dosha-item h4{font-size:12px;margin-bottom:2px;font-weight:600}
  .dosha-item p{font-size:11px;color:#555;margin-bottom:4px}
  .dosha-item ul{margin:0;padding-left:16px}
  .dosha-item li{font-size:11px;color:#666}
  .chart-wrap{text-align:center}
  .footer{text-align:center;font-size:10px;color:#ccc;border-top:1px solid #eee;padding-top:12px;margin-top:24px}
  @media print{@page{margin:1.5cm}button{display:none}}
  </style></head><body><div class="page">

  <div class="header">
    <h1>✦ AstroLogic ✦</h1>
    <h2>Vedic Birth Kundali — Detailed Report</h2>
    <div class="meta">Generated ${new Date().toLocaleDateString("en-IN",{dateStyle:"long"})} &nbsp;·&nbsp; Lahiri Ayanamsa &nbsp;·&nbsp; Swiss Ephemeris &nbsp;·&nbsp; Vimshottari Dasha</div>
  </div>

  <div class="grid2">
    <div class="sec">
      <div class="sec-title">Birth Details</div>
      ${[["Name", p.name],["Date of Birth", p.dob],["Time of Birth", p.tob + " IST"],["Place of Birth", p.city],
         ["Lagna (Ascendant)", `${safe(d.lagna)} ${safe(d.lagna_degree)}`],
         ["Lagna Nakshatra", d.lagna_nakshatra ? `${d.lagna_nakshatra} Pada ${d.lagna_pada}` : "—"],
         ["Moon Sign", moon?.sign || "—"],
         ["Moon Nakshatra", d.nakshatra ? `${d.nakshatra} (Pada ${d.nakshatra_pada})` : "—"],
         ["Ayanamsa (Lahiri)", safe(d.ayanamsa) + "°"],
         ["Tithi", d.tithi_name && d.paksha ? `${d.tithi_name} (${d.paksha})` : safe(d.tithi_name)],
         ["Birth Yoga", safe(d.yoga_name)],["Karana", safe(d.karana_name)],
         ["Mahadasha", safe(d.mahadasha)],["Dasha Balance", safe(d.dasha_balance)],
      ].map(([l,v]) => `<div class="dr"><span class="dl">${l}</span><span class="dv">${v}</span></div>`).join("")}
    </div>
    <div class="sec chart-wrap">
      <div class="sec-title">D1 — Rashi Chart</div>
      ${d1SVG}
    </div>
  </div>

  <div class="grid2">
    <div class="sec chart-wrap">
      <div class="sec-title">D9 — Navamsa Chart</div>
      ${d9SVG}
    </div>
    <div class="sec">
      <div class="sec-title">Chart Strength Analysis</div>
      ${scoreHTML}
    </div>
  </div>

  <div class="sec">
    <div class="sec-title">Planetary Positions (Navagraha)</div>
    <table>
      <tr><th>Planet</th><th>Sign (Rashi)</th><th>Degree</th><th>House</th>
          <th>Nakshatra</th><th>Pada</th><th>Navamsa</th><th>Strength</th><th>Status</th></tr>
      ${planetRows}
    </table>
  </div>

  <div class="sec">
    <div class="sec-title">House-wise Analysis (All 12 Houses)</div>
    <table>
      <tr><th>House</th><th>Sign (Rashi)</th><th>Significance</th><th>Occupants</th></tr>
      ${allHouseRows}
    </table>
  </div>

  <div class="grid2">
    <div class="sec">
      <div class="sec-title">Active Yogas (${activeYogas.length})</div>
      ${activeYogas.length ? activeYogas.map(y => `<div class="yoga-item">
        <h4>${y.name} <span style="float:right;font-size:10px;background:#dcfce7;color:#166534;padding:1px 7px;border-radius:3px">${y.strength}</span></h4>
        <p>${y.description}</p>
      </div>`).join("") : `<p style="color:#aaa;font-size:12px">No active yogas detected</p>`}
    </div>
    <div class="sec">
      <div class="sec-title">Dosha Analysis</div>
      ${activeDoshas.length ? activeDoshas.map(ds => `<div class="dosha-item ${ds.severity==='High'?'dosha-high':'dosha-med'}">
        <h4 style="color:${ds.severity==='High'?'#b91c1c':'#92400e'}">${ds.name}
          <span style="float:right;font-size:10px">${ds.severity}</span></h4>
        <p>${ds.description}</p>
        ${ds.remedies?.length ? `<ul>${ds.remedies.slice(0,3).map(r=>`<li>${r}</li>`).join("")}</ul>` : ""}
      </div>`).join("") : `<div class="yoga-item" style="border-color:#22c55e;background:#f0fdf4">
        <h4 style="color:#166534">✓ No major doshas detected</h4>
        <p>Chart is free from major planetary afflictions.</p>
      </div>`}
    </div>
  </div>

  <div class="sec">
    <div class="sec-title">Vimshottari Dasha</div>
    <div style="display:flex;gap:32px;margin-bottom:12px;flex-wrap:wrap">
      <div class="dr"><span class="dl">Mahadasha</span><span class="dv" style="color:#8b1a1a;font-size:15px">${safe(d.mahadasha)}</span></div>
      <div class="dr"><span class="dl">Antardasha</span><span class="dv">${safe(d.antardasha)}</span></div>
      <div class="dr"><span class="dl">Balance Remaining</span><span class="dv">${safe(d.dasha_balance)}</span></div>
    </div>
    <div style="margin-top:8px">
      <div style="font-size:11px;color:#999;margin-bottom:7px">Antardasha sequence within current Mahadasha:</div>
      ${antarList}
    </div>
  </div>

  <div class="footer">
    AstroLogic Vedic Astrology Platform &nbsp;·&nbsp; Report for <strong>${p.name}</strong>
    &nbsp;·&nbsp; Calculations via Lahiri Ayanamsa &amp; Swiss Ephemeris &nbsp;·&nbsp; For guidance purposes only
  </div>

  </div>
  <script>window.onload=()=>window.print()<\/script>
  </body></html>`);
  w.document.close();
}

// ── PDF Download — matches on-screen report template exactly ─────────
// function downloadPDF() {
//   if (!_data || !_person) { showToast("Please generate kundali first", "error"); return; }
//   const d = _data, p = _person;
//   const d1SVG = document.getElementById("d1Chart")?.innerHTML || "";
//   const d9SVG = document.getElementById("d9Chart")?.innerHTML || "";
//   const moon  = (d.planets||[]).find(pl=>pl.name==="Moon");

//   // Planet rows
//   const planetRows = (d.planets||[]).map(pl=>{
//     const {label,style} = getStrength(pl.name, pl.sign);
//     const retro = pl.retrograde ? ` <em style="color:#c0392b;font-size:10px">(R)</em>` : "";
//     return `<tr>
//       <td style="font-weight:600">${pl.name}${retro}</td>
//       <td>${pl.sign||"—"}</td>
//       <td style="font-family:monospace">${pl.degree||"—"}</td>
//       <td style="font-weight:700;text-align:center">${pl.house||"—"}</td>
//       <td>${pl.nakshatra||"—"}</td>
//       <td style="text-align:center">${pl.pada||"—"}</td>
//       <td>${pl.navamsa||"—"}</td>
//       <td style="${style}">${label}</td>
//       <td style="color:${pl.retrograde?"#c0392b":"#27ae60"}">${pl.retrograde?"Retrograde":"Direct"}</td>
//     </tr>`;
//   }).join("");

//   // House rows
//   const houseRows = Array.from({length:12},(_,i)=>{
//     const h=i+1;
//     const rashiIdx=getRashiIndex(d.lagna,h);
//     const sign=RASHI_FULL[rashiIdx]||"";
//     const meaning=HOUSE_MEANINGS[h]||"";
//     const planets=(d.houses[h]||[]).filter(x=>x!=="Lagna");
//     return `<tr>
//       <td style="font-weight:700;text-align:center">${h}</td>
//       <td style="font-weight:600">${sign}</td>
//       <td style="color:#666;font-size:11px">${meaning}</td>
//       <td>${planets.length ? `<span style="font-weight:500">${planets.join(", ")}</span>` : '<span style="color:#ccc">Empty</span>'}</td>
//     </tr>`;
//   }).join("");

//   const activeYogas  = (d.yogas||[]).filter(y=>y.present);
//   const activeDoshas = (d.doshas||[]).filter(ds=>ds.present);
//   const sc = d.scores||{};

//   const scoreBarRow = (lbl,val,color) => `
//     <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
//       <div style="width:110px;font-size:12px;color:#555;flex-shrink:0">${lbl}</div>
//       <div style="flex:1;height:7px;background:#eee;border-radius:4px">
//         <div style="height:100%;border-radius:4px;background:${color};width:${Math.min(val||0,100)}%"></div>
//       </div>
//       <div style="width:36px;text-align:right;font-size:12px;font-weight:700;color:#333">${val??0}%</div>
//     </div>`;

//   const antarList = (d.antardasha_list||[]).map((a,i)=>
//     `<span style="display:inline-block;margin:3px 4px;padding:3px 10px;
//       background:${i===0?"#8b1a1a":"#f5e6c8"};color:${i===0?"#fff":"#5a2d0c"};
//       border-radius:4px;font-size:11px;font-weight:${i===0?600:400}">${a.lord} ${a.years}y</span>`
//   ).join("");

//   // Build full Mahadasha timeline
//   const DASHA_O = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"];
//   const DASHA_Y = {Ketu:7,Venus:20,Sun:6,Moon:10,Mars:7,Rahu:18,Jupiter:16,Saturn:19,Mercury:17};
//   let bal = parseFloat(d.dasha_balance)||5;
//   const mdIdx = DASHA_O.indexOf(d.mahadasha);
//   const mdTimeline = [];
//   for(let i=0;i<9;i++){
//     const lord=DASHA_O[(mdIdx+i)%9];
//     const yrs=i===0?bal:DASHA_Y[lord];
//     mdTimeline.push(`<tr><td style="font-weight:600">${lord}</td>
//       <td style="font-size:11px;color:#666">${yrs}y</td>
//       <td>${i===0?`<span style="background:#8b1a1a;color:#fff;padding:2px 8px;border-radius:3px;font-size:10px">Current</span>`:"—"}</td></tr>`);
//   }

//   const w = window.open("","_blank","width=1100,height=900");
//   w.document.write(`<!DOCTYPE html><html><head>
//   <meta charset="UTF-8">
//   <title>Kundali — ${p.name}</title>
//   <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Crimson+Pro:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
//   <style>
//   *{margin:0;padding:0;box-sizing:border-box}
//   body{font-family:"Inter",Arial,sans-serif;color:#1a0a00;background:#fff;font-size:12.5px;line-height:1.55}
//   .page{max-width:1020px;margin:0 auto;padding:32px 36px}

//   /* Header — matches on-screen exactly */
//   .pdf-header{text-align:center;padding:28px 0 22px;border-bottom:3px double #8b1a1a;margin-bottom:28px}
//   .pdf-header h1{font-family:"Cinzel",serif;font-size:34px;color:#8b1a1a;letter-spacing:6px;font-weight:700;margin-bottom:6px}
//   .pdf-header h1 .star{font-size:20px;color:#d89b3c;vertical-align:middle;margin:0 6px}
//   .pdf-header h2{font-family:"Cinzel",serif;font-size:15px;color:#888;font-weight:400;margin-bottom:8px}
//   .pdf-header .meta{font-size:11px;color:#bbb;letter-spacing:.3px}
//   .pdf-header .meta span{margin:0 8px}

//   /* Section labels matching on-screen */
//   .sec-label{font-family:"Cinzel",serif;font-size:10.5px;font-weight:700;letter-spacing:1.5px;
//     text-transform:uppercase;color:#fff;background:#8b1a1a;padding:7px 14px;
//     border-radius:4px;margin-bottom:14px;display:block}

//   /* Grid layouts */
//   .grid2{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:28px}
//   .grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:28px}

//   /* Birth details block */
//   .detail-row{display:flex;padding:6px 0;border-bottom:1px solid #f5ede0;font-size:12.5px}
//   .detail-row:last-child{border-bottom:none}
//   .dl{color:#888;min-width:165px;flex-shrink:0}
//   .dv{color:#1a0a00;font-weight:600}
//   .dv.highlight{color:#8b1a1a;font-size:14px}

//   /* Chart box */
//   .chart-box{background:#fafaf8;border:1px solid #e8ddd0;border-radius:6px;
//     padding:18px;text-align:center}

//   /* Tables */
//   table{width:100%;border-collapse:collapse;font-size:11.5px;margin-bottom:8px}
//   thead th{background:#f5e6c8;color:#5a2d0c;padding:8px 10px;text-align:left;
//     font-weight:700;font-size:10.5px;letter-spacing:.5px;text-transform:uppercase;border-bottom:2px solid #d89b3c}
//   tbody tr{border-bottom:1px solid #f0e8d8}
//   tbody tr:nth-child(even){background:#faf7f2}
//   tbody tr:hover{background:#f5ede0}
//   tbody td{padding:7px 10px;vertical-align:middle}

//   /* Score bars */
//   .score-section{margin-bottom:28px}

//   /* Yogas */
//   .yoga-item{padding:9px 12px;margin-bottom:8px;border-left:4px solid #27ae60;
//     background:#f0fdf4;border-radius:0 5px 5px 0}
//   .yoga-item h4{font-size:12.5px;color:#166534;margin-bottom:3px;font-weight:700}
//   .yoga-item p{font-size:11px;color:#555;margin:0}
//   .yoga-strength{float:right;font-size:10px;background:#dcfce7;color:#166534;
//     padding:1px 8px;border-radius:3px}

//   /* Doshas */
//   .dosha-item{padding:9px 12px;margin-bottom:8px;border-radius:5px}
//   .dosha-high{border-left:4px solid #ef4444;background:#fff5f5}
//   .dosha-med{border-left:4px solid #f59e0b;background:#fffbeb}
//   .dosha-ok{border-left:4px solid #22c55e;background:#f0fdf4}
//   .dosha-item h4{font-size:12.5px;margin-bottom:3px;font-weight:700}
//   .dosha-item p{font-size:11px;color:#555;margin-bottom:4px}
//   .dosha-item ul{margin:0;padding-left:16px}
//   .dosha-item li{font-size:10.5px;color:#666;margin-bottom:2px}
//   .dosha-sev{float:right;font-size:10px;padding:1px 8px;border-radius:3px}

//   /* Dasha */
//   .dasha-big{font-family:"Cinzel",serif;font-size:22px;font-weight:700;color:#8b1a1a}
//   .dasha-sub{font-family:"Cinzel",serif;font-size:15px;color:#d89b3c;margin-top:2px}
//   .dasha-bal{font-size:12px;color:#888;margin-top:2px}

//   /* Footer */
//   .pdf-footer{text-align:center;font-size:10.5px;color:#bbb;border-top:1px solid #eee;
//     padding-top:14px;margin-top:28px}

//   /* Page break */
//   .page-break{page-break-before:always;padding-top:28px}

//   @media print{
//     @page{margin:1.2cm;size:A4}
//     .no-print{display:none}
//     body{font-size:11px}
//     .pdf-header h1{font-size:28px}
//   }
//   </style></head><body>
//   <div class="page">

//   <!-- ── HEADER ── -->
//   <div class="pdf-header">
//     <h1><span class="star">✦</span> AstroLogic <span class="star">✦</span></h1>
//     <h2>Vedic Birth Kundali — Detailed Report</h2>
//     <div class="meta">
//       <span>Generated ${new Date().toLocaleDateString("en-IN",{dateStyle:"long"})}</span>
//       <span>·</span><span>Lahiri Ayanamsa</span>
//       <span>·</span><span>Swiss Ephemeris</span>
//       <span>·</span><span>Vimshottari Dasha</span>
//     </div>
//   </div>

//   <!-- ── BIRTH DETAILS + D1 CHART ── -->
//   <div class="grid2">
//     <div>
//       <span class="sec-label">Birth Details</span>
//       ${[
//         ["Name", p.name, true],
//         ["Date of Birth", p.dob, false],
//         ["Time of Birth", p.tob+" IST", false],
//         ["Place of Birth", p.city, false],
//         ["Lagna (Ascendant)", `${d.lagna} ${d.lagna_degree}`, true],
//         ["Lagna Nakshatra", d.lagna_nakshatra?(d.lagna_nakshatra+" Pada "+d.lagna_pada):"—", false],
//         ["Moon Sign (Chandra)", moon?.sign||"—", false],
//         ["Moon Nakshatra", d.nakshatra?(d.nakshatra+" (Pada "+d.nakshatra_pada+")"):"—", false],
//         ["Ayanamsa (Lahiri)", (d.ayanamsa||"")+"°", false],
//         ["Tithi", d.tithi_name&&d.paksha?(d.tithi_name+" ("+d.paksha+")"):(d.tithi_name||"—"), false],
//         ["Birth Yoga", d.yoga_name||"—", false],
//         ["Karana", d.karana_name||"—", false],
//         ["Mahadasha", d.mahadasha||"—", true],
//         ["Dasha Balance", d.dasha_balance||"—", false],
//       ].map(([l,v,h])=>`<div class="detail-row"><span class="dl">${l}</span>
//         <span class="dv ${h?"highlight":""}">${v}</span></div>`).join("")}
//     </div>
//     <div>
//       <span class="sec-label">D1 — Rashi Chart (Natal)</span>
//       <div class="chart-box">${d1SVG}</div>
//     </div>
//   </div>

//   <!-- ── D9 + CHART STRENGTH ── -->
//   <div class="grid2">
//     <div>
//       <span class="sec-label">D9 — Navamsa Chart</span>
//       <div class="chart-box">${d9SVG}</div>
//     </div>
//     <div>
//       <span class="sec-label">Chart Strength Analysis</span>
//       ${scoreBarRow("Overall Strength", sc.overall_strength, "#7c6af5")}
//       ${scoreBarRow("Career", sc.career_score, "#d89b3c")}
//       ${scoreBarRow("Finance", sc.finance_score, "#22c55e")}
//       ${scoreBarRow("Relationship", sc.marriage_score, "#0ea5e9")}
//       ${scoreBarRow("Health", sc.health_score, "#ef4444")}
//       ${scoreBarRow("Mental", sc.mental_score, "#a855f7")}
//       ${scoreBarRow("Spirituality", sc.spirituality_score, "#f59e0b")}
//     </div>
//   </div>

//   <!-- ── PLANETARY POSITIONS ── -->
//   <div style="margin-bottom:28px">
//     <span class="sec-label">Planetary Positions (Navagraha)</span>
//     <table>
//       <thead><tr>
//         <th>Planet</th><th>Sign (Rashi)</th><th>Degree</th><th style="text-align:center">H</th>
//         <th>Nakshatra</th><th style="text-align:center">Pada</th><th>Navamsa</th>
//         <th>Strength</th><th>Status</th>
//       </tr></thead>
//       <tbody>${planetRows}</tbody>
//     </table>
//   </div>

//   <!-- ── HOUSE ANALYSIS ── -->
//   <div style="margin-bottom:28px">
//     <span class="sec-label">House-wise Analysis (All 12 Bhavas)</span>
//     <table>
//       <thead><tr>
//         <th style="text-align:center;width:40px">H</th>
//         <th>Sign (Rashi)</th><th>Significance</th><th>Occupants</th>
//       </tr></thead>
//       <tbody>${houseRows}</tbody>
//     </table>
//   </div>

//   <!-- ── YOGAS + DOSHAS ── -->
//   <div class="grid2" style="margin-bottom:28px">
//     <div>
//       <span class="sec-label">Active Yogas (${activeYogas.length})</span>
//       ${activeYogas.length ? activeYogas.map(y=>`<div class="yoga-item">
//         <h4>${y.name} <span class="yoga-strength">${y.strength||"Active"}</span></h4>
//         <p>${y.description||""}</p>
//       </div>`).join("")
//       : `<div class="dosha-item dosha-ok"><h4 style="color:#166534">No major yogas in this chart</h4>
//            <p>Focus on strengthening functional benefic planets.</p></div>`}
//     </div>
//     <div>
//       <span class="sec-label">Dosha Analysis</span>
//       ${activeDoshas.length ? activeDoshas.map(ds=>{
//         const sevColor = ds.severity==="High"?"#b91c1c":"#92400e";
//         const sevBg    = ds.severity==="High"?"#fff5f5":"#fffbeb";
//         const cls      = ds.severity==="High"?"dosha-high":"dosha-med";
//         return `<div class="dosha-item ${cls}">
//           <h4 style="color:${sevColor}">${ds.name}
//             <span class="dosha-sev" style="background:${sevBg};color:${sevColor}">${ds.severity}</span></h4>
//           <p>${ds.description||""}</p>
//           ${ds.remedies?.length?`<ul>${ds.remedies.slice(0,3).map(r=>`<li>${r}</li>`).join("")}</ul>`:""}
//         </div>`;
//       }).join("")
//       : `<div class="dosha-item dosha-ok"><h4 style="color:#166534">✓ No major doshas detected</h4>
//            <p>Chart is free from major afflictions.</p></div>`}
//     </div>
//   </div>

//   <!-- ── VIMSHOTTARI DASHA ── -->
//   <div style="margin-bottom:28px">
//     <span class="sec-label">Vimshottari Dasha</span>
//     <div class="grid3" style="margin-bottom:16px">
//       <div><div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">Current Mahadasha</div>
//         <div class="dasha-big">${d.mahadasha||"—"}</div></div>
//       <div><div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">Current Antardasha</div>
//         <div class="dasha-sub">${d.antardasha||"—"}</div></div>
//       <div><div style="font-size:11px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px">Balance Remaining</div>
//         <div class="dasha-bal" style="font-size:16px;font-weight:700;color:#1a0a00">${d.dasha_balance||"—"}</div></div>
//     </div>
//     <div class="grid2">
//       <div>
//         <div style="font-size:11px;font-weight:700;color:#8b1a1a;letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px">Mahadasha Sequence</div>
//         <table style="margin-bottom:0">
//           <thead><tr><th>Lord</th><th>Duration</th><th>Status</th></tr></thead>
//           <tbody>${mdTimeline.join("")}</tbody>
//         </table>
//       </div>
//       <div>
//         <div style="font-size:11px;font-weight:700;color:#d89b3c;letter-spacing:.5px;text-transform:uppercase;margin-bottom:8px">Antardasha within ${d.mahadasha}</div>
//         <div>${antarList}</div>
//       </div>
//     </div>
//   </div>

//   <!-- ── FOOTER ── -->
//   <div class="pdf-footer">
//     <strong>AstroLogic</strong> Vedic Astrology Platform &nbsp;·&nbsp;
//     Detailed Kundali Report for <strong>${p.name}</strong> &nbsp;·&nbsp;
//     Calculations via Lahiri Ayanamsa &amp; Swiss Ephemeris &nbsp;·&nbsp;
//     For guidance purposes only. Consult a qualified Jyotishi for major decisions.
//   </div>

//   </div><!-- /page -->
//   <script>
//     // Auto-print
//     window.onload = () => {
//       setTimeout(() => window.print(), 800);
//     };
//   <\/script>
//   </body></html>`);
//   w.document.close();
// }

// ── Chat ──────────────────────────────────────────────────────────
// ── Smart Kundali Chat ─────────────────────────────────────────────
const SUGGESTED_QUESTIONS = [
  "When will I get a job?",
  "When is my marriage?",
  "Will I settle abroad?",
  "When will I have children?",
  "What is my career field?",
  "What are my active yogas?",
  "Show my dasha timeline",
  "What are my remedies?",
];

function initChat() {
  const cb = document.getElementById("chatBox");
  if (!cb) return;
  cb.innerHTML = `
    <div style="text-align:center;padding:16px 8px">
      <div style="font-size:22px;margin-bottom:8px">🔮</div>
      <div style="font-size:14px;color:var(--gold);font-weight:600;margin-bottom:6px">Ask Your Kundali</div>
      <div style="font-size:12px;color:var(--text-dim);margin-bottom:16px">Your birth chart has been generated. Ask any life question.</div>
      <div style="display:flex;flex-wrap:wrap;gap:6px;justify-content:center">
        ${SUGGESTED_QUESTIONS.map(q=>`<button onclick="askSuggested('${q}')"
          style="background:rgba(245,193,108,.1);border:1px solid rgba(245,193,108,.25);
          color:var(--gold);font-size:11.5px;padding:5px 11px;border-radius:16px;cursor:pointer;
          font-family:Inter,sans-serif;transition:.2s"
          onmouseover="this.style.background='rgba(245,193,108,.2)'"
          onmouseout="this.style.background='rgba(245,193,108,.1)'">${q}</button>`).join('')}
      </div>
    </div>`;
}

function askSuggested(q) {
  document.getElementById("chatInput").value = q;
  sendMessage();
}

function _md(text) {
  // Simple markdown renderer
  return text
    .replace(/\*\*(.+?)\*\*/g,'<strong style="color:var(--gold)">$1</strong>')
    .replace(/🎯/g,'<span style="color:var(--green)">🎯</span>')
    .replace(/⚠️/g,'<span style="color:var(--red)">⚠️</span>')
    .replace(/✅/g,'<span style="color:var(--green)">✅</span>')
    .replace(/\n/g,'<br>');
}

async function sendMessage() {
  const input = document.getElementById("chatInput");
  const msg   = input?.value.trim();
  if (!msg) return;
  if (!_data) { showToast("Please generate Kundali first", "error"); return; }

  const cb = document.getElementById("chatBox");
  // Append user bubble
  cb.innerHTML += `<div style="display:flex;justify-content:flex-end;margin-bottom:12px">
    <div style="background:linear-gradient(135deg,var(--gold),var(--gold2));color:#000;
      padding:9px 14px;border-radius:14px 14px 4px 14px;font-size:13px;max-width:75%;
      font-weight:500">${msg}</div></div>`;
  input.value = "";
  cb.scrollTop = cb.scrollHeight;

  // Typing indicator
  const typingId = "typing-" + Date.now();
  cb.innerHTML += `<div id="${typingId}" style="display:flex;align-items:center;gap:8px;margin-bottom:12px;padding:10px 14px;
    background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:14px 14px 14px 4px;width:fit-content">
    <span style="color:var(--text-dim);font-size:12px">Reading your chart</span>
    <span style="display:flex;gap:3px">${[0,0.15,0.3].map(d=>`<span style="width:5px;height:5px;border-radius:50%;background:var(--gold);
      animation:tdot 1s ${d}s ease-in-out infinite"></span>`).join('')}</span>
  </div>`;
  cb.scrollTop = cb.scrollHeight;

  try {
    const r = await fetch("/api/kundali-chat", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ message: msg, chart: _data })
    });
    const res = await r.json();

    document.getElementById(typingId)?.remove();

    const topicColors = {
      career:"#f5c16c", marriage:"#f87171", wealth:"#4ade80", health:"#60a5fa",
      foreign:"#34d399", children:"#c084fc", education:"#9bdcff", timing:"#fb923c",
      yoga:"#fbbf24", dosha:"#f87171", remedy:"#a78bfa", general:"#9bdcff"
    };
    const tc = topicColors[res.topic] || "#9bdcff";
    const topicLabel = res.topic ? `<span style="font-size:10px;padding:2px 7px;border-radius:4px;
      background:rgba(255,255,255,.06);color:${tc};margin-bottom:8px;display:inline-block">${res.topic}</span>` : "";

    cb.innerHTML += `<div style="margin-bottom:16px">
      ${topicLabel}
      <div style="background:rgba(255,255,255,.04);border:1px solid var(--border);border-left:3px solid ${tc};
        padding:12px 16px;border-radius:0 14px 14px 0;font-size:13.5px;line-height:1.75;color:var(--text)">
        ${_md(res.reply)}
      </div>
    </div>`;
    cb.scrollTop = cb.scrollHeight;
  } catch(e) {
    document.getElementById(typingId)?.remove();
    cb.innerHTML += `<div style="color:var(--red);font-size:13px;padding:8px;margin-bottom:8px">Error: ${e.message}</div>`;
  }
}

// Add CSS for typing dots
const style = document.createElement("style");
style.textContent = `@keyframes tdot{0%,100%{opacity:.3;transform:translateY(0)}50%{opacity:1;transform:translateY(-3px)}}`;
document.head.appendChild(style);