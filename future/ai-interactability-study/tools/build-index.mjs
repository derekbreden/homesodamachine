#!/usr/bin/env node
// Builds index.html (the visual entry point) from scenes/*/index.html scene-meta blocks,
// thumbs/<id>.png, context/map.json (families, extra connections, perspectives) and the explorer table below.
//   node tools/build-index.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const study = path.resolve(here, "..");
const read = f => fs.readFileSync(path.join(study, f), "utf8");
const exists = f => fs.existsSync(path.join(study, f));

const EXPLORERS = [
  { code: "freedom", name: "Freedom and force", examples: true, blurb: "Motions free, restrained, driven or locked; the forces that push along each; who supplies precision when." },
  { code: "room", name: "The room is the first stage", examples: true, blurb: "Bench, table, opening, wall, ceiling, frame: the space the gun already lives in as the coarse stage." },
  { code: "travel", name: "Split the travel", examples: true, blurb: "Which body moves, by what, at setup or during the weld; where each stage's error lands at the dot." },
  { code: "trials", name: "The machine runs trials", examples: true, blurb: "The station as an instrument for repeated dry runs by software across tubes; what resets between trials." },
  { code: "datum", name: "The seam is the datum", examples: false, blurb: "Gun-to-corner is the pose that matters; rim, plate, ports and wall as the reference." },
  { code: "eyes", name: "Seeing first", examples: false, blurb: "Begin from what can be observed, from where, and what the rim, gun and glare hide." },
  { code: "borrowed", name: "Borrowed from elsewhere", examples: false, blurb: "Mass-produced products for other purposes that already do part of the job." },
  { code: "use", name: "The day of use", examples: false, blurb: "The arrangement as a sequence of states — setup, dry run, weld, retract, swap — with handovers." },
];

// ---- gather scenes
const scenes = [];
for (const id of fs.readdirSync(path.join(study, "scenes")).sort()) {
  const f = `scenes/${id}/index.html`;
  if (!exists(f)) continue;
  const m = read(f).match(/<script[^>]*id=["']scene-meta["'][^>]*>([\s\S]*?)<\/script>/);
  let meta = {};
  if (m) { try { meta = JSON.parse(m[1]); } catch (e) { console.error(`bad scene-meta in ${id}: ${e.message}`); } }
  else console.error(`no scene-meta in ${id}`);
  scenes.push({
    id, title: meta.title || id, by: meta.by || id.split("-")[0], origin: meta.origin || "swarm", summary: meta.summary || "",
    status: meta.status || meta.sceneStatus || "", tags: meta.tags || [], branchOf: meta.branchOf || [], combines: meta.combines || [],
    transferable: meta.transferable || [], how: meta.how || null, software: meta.software || null,
    notes: meta.notes || [], sources: meta.sources || [],
    thumb: exists(`thumbs/${id}.png`) ? `thumbs/${id}.png` : null, href: `scenes/${id}/index.html`,
  });
}
const byId = Object.fromEntries(scenes.map(s => [s.id, s]));
const map = exists("context/map.json") ? JSON.parse(read("context/map.json")) : {};

// ---- edges: from meta plus the coordinator's map
const edges = [];
for (const s of scenes) {
  for (const b of s.branchOf) if (byId[b]) edges.push({ from: b, to: s.id, type: "branch", label: "branch" });
  for (const c of s.combines) if (byId[c]) edges.push({ from: c, to: s.id, type: "combines", label: "combined into" });
}
for (const e of map.edges || []) if (byId[e.from] && byId[e.to]) edges.push(e);

const data = { scenes, edges, families: map.families || [], perspectives: map.perspectives || [], explorers: EXPLORERS, groupNote: map.note || "" };
const json = JSON.stringify(data).replace(/</g, "\\u003c");

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Welding arrangements — a visual collection</title>
<style>
:root{--bg:#0e1114;--panel:#151a20;--line:#27303a;--text:#e3e8ee;--mute:#94a0ad;--acc:#5fb0ff;--load:#e6a935;--loc:#26b79a;--act:#a06af0;--comp:#6cc24a;--sens:#3f8cff;--laser:#ff4a4a}
*{box-sizing:border-box}html{color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
header{padding:26px 24px 8px;max-width:1500px;margin:0 auto}
h1{margin:0 0 6px;font-size:26px;letter-spacing:-.01em}
.lede{color:var(--mute);max-width:78ch;margin:0 0 6px}
.how{display:flex;flex-wrap:wrap;gap:8px 18px;color:var(--mute);font-size:13px;margin:8px 0 0}
.how b{color:var(--text);font-weight:600}
nav{position:sticky;top:0;z-index:20;background:rgba(14,17,20,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);margin-top:14px}
nav .in{max-width:1500px;margin:0 auto;padding:8px 24px;display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center}
.tab,.chip{border:1px solid var(--line);background:var(--panel);color:var(--text);border-radius:999px;padding:5px 12px;font:inherit;font-size:13px;cursor:pointer}
.tab[aria-pressed=true],.chip[aria-pressed=true]{background:#20406a;border-color:#3d6ea8}
.sep{width:1px;height:22px;background:var(--line);margin:0 6px}
.lab{color:var(--mute);font-size:12px;text-transform:uppercase;letter-spacing:.06em;margin-right:2px}
main{max-width:1500px;margin:0 auto;padding:18px 24px 80px}
section.family{margin:0 0 34px}
section.family h2{margin:0 0 2px;font-size:18px}
section.family .blurb{margin:0 0 12px;color:var(--mute);max-width:90ch;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;display:flex;flex-direction:column;color:inherit}
.card:hover{border-color:#4b6d93;text-decoration:none}
.card .img{aspect-ratio:16/10;background:#0a0d10;display:block;position:relative}
.card img{width:100%;height:100%;object-fit:cover;display:block}
.card .noimg{position:absolute;inset:0;display:grid;place-items:center;color:var(--mute);font-size:13px}
.card .body{padding:9px 11px 11px;display:flex;flex-direction:column;gap:5px;flex:1}
.card h3{margin:0;font-size:14.5px;line-height:1.25}
.card p{margin:0;color:var(--mute);font-size:12.5px;line-height:1.4;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.badges{display:flex;flex-wrap:wrap;gap:4px}
.b{font-size:11px;border:1px solid var(--line);border-radius:999px;padding:1px 7px;color:var(--mute);white-space:nowrap}
.b.derek{border-color:#7a5f22;color:#f0c46a}.b.combo{border-color:#5c3f8f;color:#c9a6ff}.b.branch{border-color:#2f6a5c;color:#7ad9bf}
.strip{display:grid;grid-template-columns:auto 1fr;gap:1px 8px;font-size:11.5px;color:var(--mute);margin-top:2px}
.strip span:nth-child(odd){color:#6f7c8a;text-transform:uppercase;font-size:10px;letter-spacing:.05em;padding-top:1px}
.sw{display:flex;gap:10px;font-size:11.5px;color:var(--mute)}
.sw i{font-style:normal;color:var(--text)}
#graphwrap{position:relative;height:78vh;min-height:520px;border:1px solid var(--line);border-radius:10px;background:#0a0d10;overflow:hidden}
#graph{width:100%;height:100%;display:block}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12.5px;color:var(--mute);margin:0 0 10px}
.legend s{display:inline-block;width:26px;border-top:2px solid;vertical-align:middle;margin-right:5px;text-decoration:none}
#tip{position:absolute;pointer-events:none;background:#000c;border:1px solid var(--line);border-radius:8px;padding:6px 9px;font-size:12.5px;max-width:300px;display:none}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{position:sticky;top:44px;background:var(--bg);color:var(--mute);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.05em}
td img{width:120px;border-radius:5px;display:block}
.views{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.view{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--panel)}
.view h3{margin:0 0 3px;font-size:15px}.view p{margin:0;color:var(--mute);font-size:13.5px}
.hide{display:none!important}
footer{max-width:1500px;margin:0 auto;padding:0 24px 60px;color:var(--mute);font-size:13.5px}
footer h2{color:var(--text);font-size:16px}
footer ul{margin:4px 0 0;padding-left:18px}
@media (max-width:640px){header,main,footer,nav .in{padding-left:14px;padding-right:14px}.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
<h1>Welding arrangements — a visual collection</h1>
<p class="lede">Ways for software to control and observe the arrangement that holds and aims the X1 Pro gun at the carbonator's recessed corner. Each card opens an interactive scene: drag to orbit, use the controls on the right, and read what carries the load, what software could command and observe, what was tried and what is still open. Nothing here is ranked; maturity and polish vary and decide nothing.</p>
<div class="how"><span><b>Open</b> this file directly in a browser (no server needed). Scenes are in <code>scenes/</code>.</span><span><b>Start</b> with <a href="scenes/00-reference-orientation/index.html">the reference scene</a> — the gun, tube, plate, rotator and laser dot every scene shares.</span><span><b>Colours</b> in every scene: slate = fixed, amber = carries load, teal = locates, purple = actuated, green = compliant, blue = sensor.</span></div>
</header>
<nav><div class="in" id="nav"></div></nav>
<main id="main"></main>
<footer>
<h2>Notes and evidence</h2>
<ul>
<li><a href="README.md">README</a> — how the study ran, the eight views, what the swarm came to understand.</li>
<li><a href="context/shared-context.md">Shared context</a> · <a href="context/assignment-full.md">Derek's request</a> · <a href="context/examples.md">Derek's examples</a> · <a href="context/framings.md">The eight framings</a></li>
<li><a href="sourcing/README.md">Sourcing overview</a> · per-explorer notes in <code>sourcing/</code> · idea files in <code>explorers/&lt;view&gt;/ideas/</code> · critiques in <code>exchange/</code></li>
</ul>
</footer>
<script id="data" type="application/json">${json}</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const S = Object.fromEntries(D.scenes.map(s => [s.id, s]));
const EX = Object.fromEntries(D.explorers.map(e => [e.code, e]));
const $ = (t, a, ...k) => { const e = document.createElement(t); for (const [n, v] of Object.entries(a || {})) { if (n === 'class') e.className = v; else if (n === 'html') e.innerHTML = v; else if (n.startsWith('on')) e.addEventListener(n.slice(2), v); else e.setAttribute(n, v); } for (const c of k.flat()) if (c != null) e.append(c.nodeType ? c : document.createTextNode(c)); return e; };
const ORIGIN = { 'derek-example': ["Derek's example", 'derek'], branch: ['branch', 'branch'], 'branch-of-derek-example': ['branch of an example', 'derek'], combination: ['combination', 'combo'], swarm: ['swarm', ''], reference: ['reference', ''] };
let tab = 'map', originFilter = null, viewFilter = null;

function card(s) {
  const o = ORIGIN[s.origin] || [s.origin, ''];
  const sw = s.software || {};
  const strip = s.how ? $('div', { class: 'strip' }, ...[['Moves', s.how.motion], ['Carries', s.how.load], ['Locates', s.how.reference], ['Observed', s.how.observe]].filter(r => r[1]).flatMap(r => [$('span', {}, r[0]), $('span', {}, r[1])])) : null;
  const counts = (sw.commands || sw.observes || sw.manual) ? $('div', { class: 'sw' }, $('span', {}, '⚙ commands ', $('i', {}, (sw.commands || []).length)), $('span', {}, '◉ observes ', $('i', {}, (sw.observes || []).length)), $('span', {}, '✋ manual ', $('i', {}, (sw.manual || []).length))) : null;
  return $('a', { class: 'card', href: s.href, 'data-id': s.id },
    $('span', { class: 'img' }, s.thumb ? $('img', { src: s.thumb, alt: '', loading: 'lazy' }) : $('span', { class: 'noimg' }, 'no preview yet')),
    $('div', { class: 'body' },
      $('h3', {}, s.title),
      $('div', { class: 'badges' }, $('span', { class: 'b ' + o[1] }, o[0]), $('span', { class: 'b' }, (EX[s.by] || {}).name || s.by), s.status ? $('span', { class: 'b' }, s.status) : null),
      $('p', {}, s.summary), strip, counts));
}
function visible(s) { return s.origin !== 'reference' && (!originFilter || (originFilter === 'derek' ? /derek/.test(s.origin) : s.origin === originFilter)) && (!viewFilter || s.by === viewFilter); }

function renderMap(root) {
  const refs = D.scenes.filter(s => s.origin === 'reference');
  if (refs.length && !originFilter && !viewFilter) root.append($('section', { class: 'family' }, $('h2', {}, 'Start here'), $('p', { class: 'blurb' }, 'The shared reference: the gun, tube, plate, rotator and laser dot every scene draws, and the kit the scenes are built with.'), $('div', { class: 'grid' }, refs.map(card))));
  const fams = D.families.length ? D.families : D.explorers.map(e => ({ id: e.code, title: e.name, blurb: e.blurb, scenes: D.scenes.filter(s => s.by === e.code).map(s => s.id) }));
  const placed = new Set();
  for (const f of fams) {
    const list = f.scenes.map(id => S[id]).filter(s => s && visible(s));
    f.scenes.forEach(id => placed.add(id));
    if (!list.length) continue;
    root.append($('section', { class: 'family' }, $('h2', {}, f.title), f.blurb ? $('p', { class: 'blurb' }, f.blurb) : null, $('div', { class: 'grid' }, list.map(card))));
  }
  const rest = D.scenes.filter(s => !placed.has(s.id) && visible(s));
  if (rest.length) root.append($('section', { class: 'family' }, $('h2', {}, 'Scenes not yet placed on the map'), $('div', { class: 'grid' }, rest.map(card))));
}
function renderViews(root) {
  root.append($('p', { class: 'blurb' }, 'Eight explorers each saw the whole problem one way. Four began with Derek\\'s examples in hand; four began without them and met the examples after their first pass.'));
  const box = $('div', { class: 'views' });
  for (const e of D.explorers) {
    const n = D.scenes.filter(s => s.by === e.code);
    box.append($('div', { class: 'view' }, $('h3', {}, e.name), $('p', {}, e.blurb), $('p', { style: 'margin-top:6px' }, e.examples ? 'Began with the examples' : 'Began without the examples', ' · ', n.length + ' scenes')));
  }
  root.append(box);
  for (const e of D.explorers) {
    const list = D.scenes.filter(s => s.by === e.code && visible(s));
    if (list.length) root.append($('section', { class: 'family', style: 'margin-top:26px' }, $('h2', {}, e.name), $('div', { class: 'grid' }, list.map(card))));
  }
  if (D.perspectives.length) {
    root.append($('h2', { style: 'margin-top:36px' }, 'Perspectives the swarm added beyond the examples'));
    const pb = $('div', { class: 'views' });
    for (const p of D.perspectives) pb.append($('div', { class: 'view' }, $('h3', {}, p.title), $('p', {}, p.blurb), $('p', { style: 'margin-top:6px' }, (p.scenes || []).map(id => S[id] ? [$('a', { href: S[id].href }, S[id].title), ' · '] : []).flat())));
    root.append(pb);
  }
}
function renderSoftware(root) {
  root.append($('p', { class: 'blurb' }, 'For each arrangement: what software could command, what it could observe, and what stays manual or unresolved. Proposed, not built.'));
  const t = $('table', {}, $('tr', {}, ['Arrangement', 'Software could command', 'Software could observe', 'Manual or unresolved'].map(h => $('th', {}, h))));
  for (const s of D.scenes.filter(visible)) { const w = s.software || {}; t.append($('tr', {}, $('td', {}, $('a', { href: s.href }, s.thumb ? $('img', { src: s.thumb, alt: '' }) : '', $('div', {}, s.title))), $('td', {}, (w.commands || []).map(x => $('div', {}, x))), $('td', {}, (w.observes || []).map(x => $('div', {}, x))), $('td', {}, (w.manual || []).map(x => $('div', {}, x))))); }
  root.append(t);
}

// ---- connection graph
const EDGE = { branch: ['#7ad9bf', ''], combines: ['#c9a6ff', ''], transfers: ['#e6a935', '5 4'], perspective: ['#5fb0ff', '2 4'] };
function renderGraph(root) {
  root.append($('div', { class: 'legend' }, ...Object.entries({ branch: 'branch of', combines: 'combined into', transfers: 'mechanism that transfers', perspective: 'shared way of seeing' }).map(([k, v]) => $('span', {}, $('s', { style: 'border-color:' + EDGE[k][0] + ';border-top-style:' + (EDGE[k][1] ? 'dashed' : 'solid') }), v)), $('span', {}, 'Click a picture to open it. Drag to move. Ideas with no links float apart.')));
  const wrap = $('div', { id: 'graphwrap' }); const svgNS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(svgNS, 'svg'); svg.id = 'graph'; wrap.append(svg); const tip = $('div', { id: 'tip' }); wrap.append(tip); root.append(wrap);
  const W = () => wrap.clientWidth, H = () => wrap.clientHeight;
  const nodes = D.scenes.filter(visible).map((s, i) => ({ s, x: W() / 2 + Math.cos(i * 2.4) * 200 + (i % 7) * 20, y: H() / 2 + Math.sin(i * 2.4) * 160, vx: 0, vy: 0 }));
  const N = Object.fromEntries(nodes.map(n => [n.s.id, n]));
  const links = D.edges.filter(e => N[e.from] && N[e.to]).map(e => ({ a: N[e.from], b: N[e.to], e }));
  const R = 27;
  for (let it = 0; it < 420; it++) {
    const cool = 1 - it / 420;
    for (const a of nodes) for (const b of nodes) { if (a === b) continue; let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + 0.01, d = Math.sqrt(d2); const f = 5200 / d2 * cool; a.vx += dx / d * f; a.vy += dy / d * f; }
    for (const l of links) { const dx = l.b.x - l.a.x, dy = l.b.y - l.a.y, d = Math.hypot(dx, dy) + 0.01, f = (d - 120) * 0.02; l.a.vx += dx / d * f; l.a.vy += dy / d * f; l.b.vx -= dx / d * f; l.b.vy -= dy / d * f; }
    for (const n of nodes) { n.vx += (W() / 2 - n.x) * 0.004; n.vy += (H() / 2 - n.y) * 0.004; n.x += n.vx * 0.5; n.y += n.vy * 0.5; n.vx *= 0.6; n.vy *= 0.6; n.x = Math.max(R + 4, Math.min(W() - R - 4, n.x)); n.y = Math.max(R + 4, Math.min(H() - R - 4, n.y)); }
  }
  const mk = (t, a) => { const e = document.createElementNS(svgNS, t); for (const [k, v] of Object.entries(a || {})) e.setAttribute(k, v); return e; };
  const gl = mk('g'), gn = mk('g'); svg.append(gl, gn);
  const lineEls = links.map(l => { const el = mk('line', { stroke: EDGE[l.e.type]?.[0] || '#888', 'stroke-width': 2, 'stroke-dasharray': EDGE[l.e.type]?.[1] || '', opacity: .85 }); const t = mk('title'); t.textContent = l.e.label || l.e.type; el.append(t); gl.append(el); return el; });
  const place = () => { links.forEach((l, i) => { const el = lineEls[i]; el.setAttribute('x1', l.a.x); el.setAttribute('y1', l.a.y); el.setAttribute('x2', l.b.x); el.setAttribute('y2', l.b.y); }); nodes.forEach(n => n.g.setAttribute('transform', 'translate(' + n.x + ',' + n.y + ')')); };
  nodes.forEach((n, i) => {
    const g = mk('g', { style: 'cursor:pointer' }); n.g = g; const id = 'clip' + i;
    const cp = mk('clipPath', { id }); cp.append(mk('circle', { r: R })); g.append(cp);
    g.append(mk('circle', { r: R + 2, fill: '#0a0d10', stroke: ({ derek: '#f0c46a', combo: '#c9a6ff' })[(ORIGIN[n.s.origin] || [])[1]] || '#3a4653', 'stroke-width': 2 }));
    if (n.s.thumb) { const im = mk('image', { href: n.s.thumb, x: -R * 1.6, y: -R, width: R * 3.2, height: R * 2, 'clip-path': 'url(#' + id + ')', preserveAspectRatio: 'xMidYMid slice' }); g.append(im); }
    let moved = false, drag = false;
    g.addEventListener('pointerdown', ev => { drag = true; moved = false; g.setPointerCapture(ev.pointerId); });
    g.addEventListener('pointermove', ev => { const r = wrap.getBoundingClientRect(); if (drag) { moved = true; n.x = ev.clientX - r.left; n.y = ev.clientY - r.top; place(); } tip.style.display = 'block'; tip.style.left = Math.min(r.width - 310, ev.clientX - r.left + 14) + 'px'; tip.style.top = (ev.clientY - r.top + 14) + 'px'; tip.innerHTML = ''; tip.append($('b', {}, n.s.title), $('div', { style: 'color:#94a0ad' }, (EX[n.s.by] || {}).name || n.s.by)); });
    g.addEventListener('pointerleave', () => { tip.style.display = 'none'; });
    g.addEventListener('pointerup', () => { drag = false; if (!moved) location.href = n.s.href; });
    gn.append(g);
  });
  place();
}

function render() {
  const main = document.getElementById('main'); main.innerHTML = '';
  ({ map: renderMap, views: renderViews, connections: renderGraph, software: renderSoftware })[tab](main);
  document.querySelectorAll('.tab').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.tab === tab)));
}
const nav = document.getElementById('nav');
nav.append($('span', { class: 'lab' }, 'View'));
for (const [k, v] of [['map', 'Map of arrangements'], ['views', 'The eight views'], ['connections', 'Connections'], ['software', 'Software: commands and observations']]) nav.append($('button', { class: 'tab', 'data-tab': k, onclick: () => { tab = k; render(); } }, v));
nav.append($('span', { class: 'sep' }), $('span', { class: 'lab' }, 'Show'));
const chips = [['All', () => { originFilter = null; viewFilter = null; }], ["Derek's examples", () => { originFilter = 'derek'; viewFilter = null; }], ['Swarm originals', () => { originFilter = 'swarm'; viewFilter = null; }], ['Branches', () => { originFilter = 'branch'; viewFilter = null; }], ['Combinations', () => { originFilter = 'combination'; viewFilter = null; }]];
chips.forEach(([l, f], i) => nav.append($('button', { class: 'chip', 'data-chip': i, 'aria-pressed': String(i === 0), onclick: ev => { f(); document.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c === ev.currentTarget))); render(); } }, l)));
render();
</script>
</body>
</html>
`;
fs.writeFileSync(path.join(study, "index.html"), html);
console.log(`index.html: ${scenes.length} scenes, ${edges.length} edges, ${scenes.filter(s => s.thumb).length} with thumbnails`);
