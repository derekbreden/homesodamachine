// The Changes feed: each recorded change to the machine, before and after, newest first.
//
// An entry is a directory under `changes/` at the repo root, named `YYYY-MM-DD-HHMM-<slug>`.
// `entry.md` carries its words — frontmatter, then a body in the /updates markdown subset — and
// `views.json` the pictures the render tool drew: per view a Before and an After at one camera,
// their pixel size, and any marks to ring on both. `changes/README.md` says how one is made.
//
//     GET /changes                 the feed, ten entries, and /api/changes as it scrolls
//     GET /api/changes             the page after `?before=<id>`, as cards and as data
//     GET /changes/<id>            one entry whole; `?fragment=1` is the part the feed's modal mounts
//     GET /changes/<id>/<file>     a picture one of its views names, and nothing else there
//
// AN ENTRY IS DATA, SO IT DOES NOT DEPLOY. Entries land many times a day, and `render.yaml`
// keeps `changes/` out of its buildFilter rather than buy an `npm ci` and a restart for each.
// A container's clone holds the entries that existed when it was built; on the deployed
// container `makeCarry` below brings down the ones committed since, when the feed is asked for.

import fs from "node:fs";
import fsp from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { renderHead, renderNav, renderFooter } from "./shell.js";
import { parseFrontmatter, renderMarkdown } from "./updates.js";
import { FIGURE_CSS } from "./update-figures.js";

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ESC[c]);
}

// --- reading ---------------------------------------------------------------

// The names an entry and a file inside one may have. Both arrive in URLs and become paths, so
// a name outside these shapes is never read, served or carried — and the README beside the
// entries, a file rather than a directory, is never taken for one.
export const ID = /^[a-z0-9][a-z0-9-]{0,119}$/;
const FILE = /^[A-Za-z0-9][A-Za-z0-9._-]{0,119}$/;
const fileOk = (f) => typeof f === "string" && FILE.test(f) && !f.includes("..");

const IMAGE_TYPES = { ".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg" };
const ENTRY = "entry.md";
const VIEWS = "views.json";

const STAMP = /^(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})(?:-|$)/;
const WHEN = /^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2}))?/;
const SHA = /^[0-9a-f]{7,40}$/i;
// A path under hardware/, for the viewer's `#step:` route.
const MODEL = /^[A-Za-z0-9_][A-Za-z0-9_.\/-]*$/;

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function isFile(abs) {
  try {
    return fs.statSync(abs).isFile();
  } catch {
    return false;
  }
}

// When an entry happened, for the order: its `date`, or the stamp its name opens with. The
// stamp carries no offset, so an entry that gives no date sorts as though written in UTC — an
// hour or so off among its neighbours, never off the feed.
function whenOf(date, id) {
  const t = Date.parse(date || "");
  if (Number.isFinite(t)) return t;
  const m = STAMP.exec(id);
  return m ? Date.UTC(+m[1], +m[2] - 1, +m[3], +m[4], +m[5]) : 0;
}

// The date as its author wrote it — the change commit's own clock, not this server's zone.
function shownOf(date, id) {
  const m = WHEN.exec(date || "") || STAMP.exec(id);
  if (!m || +m[2] < 1 || +m[2] > 12) return "";
  return `${MONTHS[+m[2] - 1]} ${+m[3]}, ${m[1]}${m[4] ? ` · ${m[4]}:${m[5]}` : ""}`;
}

function titleFromId(id) {
  const words = id.replace(STAMP, "").replace(/-/g, " ").trim() || id;
  return words.charAt(0).toUpperCase() + words.slice(1);
}

const text = (v, max) => (typeof v === "string" ? v.trim().slice(0, max) : "");

// A view the page can draw: a Before and an After that are both in the directory, in a picture
// format, at a stated pixel size. A view short of any of that is left out rather than drawn as
// a broken frame; an entry left with none reads as a text card.
function usableView(dir, v) {
  if (!v || typeof v !== "object") return null;
  const width = Math.round(Number(v.width));
  const height = Math.round(Number(v.height));
  if (!(width > 0 && height > 0)) return null;
  for (const f of [v.before, v.after]) {
    if (!fileOk(f) || !IMAGE_TYPES[path.extname(f).toLowerCase()]) return null;
    if (!isFile(path.join(dir, f))) return null;
  }
  const marks = [];
  for (const m of Array.isArray(v.marks) ? v.marks : []) {
    const x = Number(m?.x);
    const y = Number(m?.y);
    if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
    const r = Number(m.r);
    marks.push({ x, y, r: r > 0 ? r : null, label: text(m.label, 120) });
  }
  return {
    name: text(v.name, 120), caption: text(v.caption, 400),
    before: v.before, after: v.after, width, height, marks,
  };
}

function readEntry(dir, id) {
  let src;
  try {
    src = fs.readFileSync(path.join(dir, ENTRY), "utf-8");
  } catch {
    return null;
  }
  const { meta, body } = parseFrontmatter(src);
  let views = [];
  try {
    const doc = JSON.parse(fs.readFileSync(path.join(dir, VIEWS), "utf-8"));
    views = (Array.isArray(doc?.views) ? doc.views : []).map((v) => usableView(dir, v)).filter(Boolean);
  } catch { /* no pictures yet: a text card */ }
  const date = meta.date || "";
  return {
    id,
    title: meta.title || titleFromId(id),
    lede: meta.lede || "",
    date,
    dated: Number.isFinite(Date.parse(date)),
    when: whenOf(date, id),
    shown: shownOf(date, id),
    commits: (meta.commit || "").split(/[\s,]+/).filter((c) => SHA.test(c)),
    model: MODEL.test(meta.model || "") && !meta.model.includes("..") ? meta.model : "",
    body,
    views,
  };
}

// What says an entry needs reading again: its directory (a picture added or renamed moves it),
// its words, and its views. An entry with no `entry.md` has no stamp and is not an entry.
function stampOf(dir) {
  try {
    const words = fs.statSync(path.join(dir, ENTRY));
    if (!words.isFile()) return null;
    const own = fs.statSync(dir);
    let views = "-";
    try {
      const st = fs.statSync(path.join(dir, VIEWS));
      views = `${st.mtimeMs}:${st.size}`;
    } catch { /* no views.json */ }
    return `${own.mtimeMs}|${words.mtimeMs}:${words.size}|${views}`;
  } catch {
    return null;
  }
}

const byRecency = (a, b) => b.when - a.when || (a.id < b.id ? 1 : a.id > b.id ? -1 : 0);

// Every entry on this disk, newest first. Read on each request so an entry written a moment ago
// is on the next page load; only an entry whose stamp moved is parsed again.
export function makeReader(changesDir) {
  const cache = new Map();
  return function readChanges() {
    let dirents;
    try {
      dirents = fs.readdirSync(changesDir, { withFileTypes: true });
    } catch {
      return [];
    }
    const out = [];
    const seen = new Set();
    for (const d of dirents) {
      if (!d.isDirectory() || !ID.test(d.name)) continue;
      const dir = path.join(changesDir, d.name);
      const stamp = stampOf(dir);
      if (!stamp) continue;
      seen.add(d.name);
      let hit = cache.get(d.name);
      if (!hit || hit.stamp !== stamp) {
        hit = { stamp, entry: readEntry(dir, d.name) };
        cache.set(d.name, hit);
      }
      if (hit.entry) out.push(hit.entry);
    }
    for (const id of cache.keys()) if (!seen.has(id)) cache.delete(id);
    return out.sort(byRecency);
  };
}

// The page after `before`: by its place in the order, or — for an id this disk no longer
// holds — after where that id's own stamp would stand.
export function pageAfter(all, before, limit) {
  let start = 0;
  if (before) {
    start = all.findIndex((e) => e.id === before) + 1;
    if (start === 0) {
      const t = whenOf("", before);
      start = all.findIndex((e) => e.when < t || (e.when === t && e.id < before));
      if (start < 0) start = all.length;
    }
  }
  const page = all.slice(start, start + limit);
  const next = start + limit < all.length && page.length ? page[page.length - 1].id : null;
  return { page, next };
}

// --- rendering -------------------------------------------------------------

// A picture's URL carries its bytes' digest, so the feed's images are cached for good and a
// view drawn again under the same name is a new URL rather than a stale hit.
const versions = new Map();
function versionOf(abs) {
  try {
    const st = fs.statSync(abs);
    const key = `${st.mtimeMs}:${st.size}`;
    const hit = versions.get(abs);
    if (hit && hit.key === key) return hit.v;
    const v = createHash("sha256").update(fs.readFileSync(abs)).digest("hex").slice(0, 12);
    versions.set(abs, { key, v });
    return v;
  } catch {
    return "";
  }
}

function imageUrl(changesDir, e, file) {
  const v = versionOf(path.join(changesDir, e.id, file));
  return `/changes/${e.id}/${encodeURIComponent(file)}${v ? `?v=${v}` : ""}`;
}

const SIDE = { before: "Before", after: "After" };
const pct = (f) => `${(Math.min(1, Math.max(0, f)) * 100).toFixed(2)}%`;
const ringR = (view, m) => m.r ?? Math.round(Math.min(view.width, view.height) * 0.06);

// Marks ring the same pixels on both pictures — one camera drew them. The ring is drawn in the
// picture's own pixels, so it encircles the same thing at any size; its stroke is not, so it
// stays a line rather than a smear on the card or a hairline in the modal.
function marksSvg(view) {
  if (!view.marks.length) return "";
  const rings = view.marks.map((m) => `<circle cx="${m.x}" cy="${m.y}" r="${ringR(view, m)}"></circle>`).join("");
  return `<svg class="ch-marks" viewBox="0 0 ${view.width} ${view.height}" aria-hidden="true">` +
    `<g class="ch-ring-halo">${rings}</g><g class="ch-ring">${rings}</g></svg>`;
}

// A label is type, so it is placed by the picture's proportions and set at the page's size
// rather than scaled with the pixels: beside its ring, on whichever side has the room.
function markLabels(view) {
  return view.marks.filter((m) => m.label).map((m) => {
    const r = ringR(view, m);
    const left = m.x + r > view.width * 0.62;
    const at = left ? `right:${pct(1 - (m.x - r) / view.width)}` : `left:${pct((m.x + r) / view.width)}`;
    return `<span class="ch-mark-label${left ? " ch-mark-label-left" : ""}" style="${at};top:${pct(m.y / view.height)}">${esc(m.label)}</span>`;
  }).join("");
}

function alt(e, view, side) {
  return `${SIDE[side]}: ${view.caption || e.title}`;
}

function cardShot(changesDir, e, view, side) {
  return `<span class="ch-shot">` +
    `<img src="${esc(imageUrl(changesDir, e, view[side]))}" width="${view.width}" height="${view.height}"` +
    ` alt="${esc(alt(e, view, side))}" loading="lazy" decoding="async">` +
    `${marksSvg(view)}<span class="ch-tag">${SIDE[side]}</span></span>`;
}

function timeTag(e, cls) {
  if (!e.shown) return "";
  return e.dated
    ? `<time class="${cls}" datetime="${esc(e.date)}">${esc(e.shown)}</time>`
    : `<span class="${cls}">${esc(e.shown)}</span>`;
}

// A card leads with its first view's two pictures, side by side at one scale, so the change
// is seen before a word of it is read. The words are a title, a clamped lede and the date.
export function renderCard(changesDir, e) {
  const view = e.views[0];
  const pair = view
    ? `<span class="ch-pair">${cardShot(changesDir, e, view, "before")}${cardShot(changesDir, e, view, "after")}</span>`
    : "";
  return `<li class="ch-item">
  <a class="ch-card" href="/changes/${e.id}" data-change="${e.id}">
    ${pair}
    <span class="ch-text">
      <span class="ch-title">${esc(e.title)}</span>
      ${e.lede ? `<span class="ch-lede">${esc(e.lede)}</span>` : ""}
      ${timeTag(e, "ch-date")}
    </span>
  </a>
</li>`;
}

// One view, large. The two pictures stand in one frame and a pair of radios chooses which is
// on top, so the change reads as the frame flips rather than as two pictures to compare — and
// it flips with no script: a click on a label, or the arrow keys on the focused radio.
function viewFigure(changesDir, e, view, i) {
  const g = `ch-${e.id}-${i}`;
  const img = (side) =>
    `<img class="ch-img ch-img-${side}" src="${esc(imageUrl(changesDir, e, view[side]))}"` +
    ` width="${view.width}" height="${view.height}" alt="${esc(alt(e, view, side))}"` +
    `${i ? ' loading="lazy"' : ""} decoding="async">`;
  return `<figure class="ch-view">
    <input type="radio" class="ch-r ch-r-before" name="${g}" id="${g}-before" value="before">
    <input type="radio" class="ch-r ch-r-after" name="${g}" id="${g}-after" value="after" checked>
    <div class="ch-switch"><label class="ch-l ch-l-before" for="${g}-before">Before</label><label class="ch-l ch-l-after" for="${g}-after">After</label></div>
    <div class="ch-frame" style="aspect-ratio: ${view.width} / ${view.height}; width: min(100%, calc((100svh - 17rem) * ${(view.width / view.height).toFixed(4)}))">
      ${img("before")}${img("after")}${marksSvg(view)}${markLabels(view)}
      <span class="ch-tag ch-tag-before">Before</span><span class="ch-tag ch-tag-after">After</span>
    </div>
    ${view.caption ? `<figcaption>${esc(view.caption)}</figcaption>` : ""}
  </figure>`;
}

function linksOf(e) {
  const links = e.commits.map((c) =>
    `<a href="https://github.com/derekbreden/homesodamachine/commit/${esc(c)}">Commit ${esc(c.slice(0, 9))}</a>`);
  if (e.model) links.push(`<a href="/3d#step:${encodeURIComponent(e.model)}">Open in 3D</a>`);
  return links.length ? `<p class="ch-links">${links.join("")}</p>` : "";
}

// The entry whole: what the feed's modal mounts and what /changes/<id> stands in its page. The
// pictures come straight after the title, and each frame is held to the height of the screen,
// so a view is seen whole before anything is read or scrolled.
export function renderDetail(changesDir, e) {
  return `<article class="ch-detail" data-change="${e.id}">
  ${e.shown ? `<p class="ch-dmeta">${timeTag(e, "ch-date")}</p>` : ""}
  <h1 class="ch-dtitle">${esc(e.title)}</h1>
  ${e.views.map((v, i) => viewFigure(changesDir, e, v, i)).join("\n")}
  ${e.lede ? `<p class="ch-dlede">${esc(e.lede)}</p>` : ""}
  ${e.body.trim() ? `<div class="ch-body">\n${renderMarkdown(e.body)}\n  </div>` : ""}
  ${linksOf(e)}
</article>`;
}

function renderFeedBody(changesDir, page, next, before) {
  const head = `<h1 class="ch-h1">Changes</h1>
  <p class="ch-sub">Each recorded change to the machine, before and after, newest first.</p>`;
  if (!page.length && !before) {
    return `<main class="ch-wrap">
  ${head}
  <p class="ch-empty">No changes recorded yet.</p>
</main>`;
  }
  return `<main class="ch-wrap">
  ${head}
  ${before ? `<p class="ch-newer"><a href="/changes">Newest changes</a></p>` : ""}
  <ul class="ch-list" id="ch-list">
${page.map((e) => renderCard(changesDir, e)).join("\n")}
  </ul>
  ${next ? `<p class="ch-more" id="ch-more" data-before="${esc(next)}"><a href="/changes?before=${esc(next)}">Older changes</a></p>` : ""}
</main>`;
}

const CHANGES_CSS = `
.ch-wrap { width: 100%; max-width: 60rem; min-width: 0; margin: 0 auto; padding: 1.5rem 1rem 5rem; }
.ch-h1 { font-size: 1.6rem; margin: 0 0 .5rem; line-height: 1.25; }
.ch-sub { color: var(--text-2); line-height: 1.55; margin: 0 0 1.5rem; font-size: .92rem; }
.ch-empty { color: var(--text-2); }
.ch-newer { margin: -.75rem 0 1rem; font-size: .85rem; }
.ch-newer a, .ch-more a, .ch-back a { color: var(--accent); }

.ch-list { list-style: none; margin: 0; padding: 0; }
.ch-item { border-top: 1px solid var(--border); }
.ch-item:last-child { border-bottom: 1px solid var(--border); }
/* The hover ground reaches past the entry at the sides as it does at top and
   bottom; the negative margin hands the width back, so the pictures and the
   words stay on the page's own column. */
.ch-card {
  display: flex; flex-direction: column; gap: .7rem;
  padding: 1rem .9rem 1.15rem; margin: 0 -.9rem;
  text-decoration: none; color: inherit;
}
.ch-card:hover { background: var(--surface); }
.ch-card:hover .ch-title { color: var(--accent); }
.ch-card:hover .ch-shot { border-color: var(--accent); }
.ch-card:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }

/* Before and After at one scale: two equal columns, each picture at its own
   aspect, so a part that moved is seen to move between them. */
.ch-pair { display: grid; grid-template-columns: 1fr 1fr; gap: .375rem; }
.ch-shot {
  position: relative; display: block; overflow: hidden; min-width: 0;
  border: 1px solid var(--border); border-radius: 8px; background: var(--bg);
}
.ch-shot img { display: block; width: 100%; height: auto; }
.ch-tag {
  position: absolute; top: .4rem; left: .4rem;
  font-size: .62rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
  padding: .12rem .4rem; border-radius: 4px; line-height: 1.4;
  background: rgba(16, 49, 156, .82); color: var(--text-2); pointer-events: none;
}
.ch-text { display: flex; flex-direction: column; gap: .3rem; min-width: 0; }
.ch-title { font-size: 1.05rem; font-weight: 600; line-height: 1.35; }
.ch-lede {
  font-size: .88rem; color: var(--text-2); line-height: 1.5;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden;
}
.ch-date { font-size: .78rem; color: var(--text-3); }
.ch-more { margin: 1.25rem 0 0; text-align: center; font-size: .88rem; }
.ch-more a { display: inline-block; padding: .5rem .75rem; }

.ch-marks { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; overflow: visible; }
.ch-marks circle { fill: none; vector-effect: non-scaling-stroke; }
.ch-ring-halo circle { stroke: rgba(0, 0, 0, .55); stroke-width: 5px; }
.ch-ring circle { stroke: var(--action); stroke-width: 2.5px; }

.ch-detail { min-width: 0; }
.ch-dmeta { margin: 0 0 .35rem; }
.ch-dtitle { font-size: 1.25rem; line-height: 1.3; margin: 0 0 1rem; }
.ch-dlede { color: var(--text-2); line-height: 1.6; margin: 0 0 1rem; font-size: .95rem; }
.ch-view { margin: 0 0 1.5rem; padding: 0; }
.ch-r { position: absolute; width: 1px; height: 1px; margin: 0; opacity: 0; pointer-events: none; }
.ch-switch {
  display: inline-flex; margin: 0 0 .5rem;
  border: 1px solid var(--border); border-radius: 8px; overflow: hidden;
}
.ch-l {
  min-width: 5.5rem; min-height: 40px; padding: 0 .9rem;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: .8rem; color: var(--text-2); cursor: pointer; user-select: none;
  border-bottom: 2px solid transparent;
}
.ch-l + .ch-l { border-left: 1px solid var(--border); }
.ch-l:hover { color: var(--text); }
.ch-r-before:checked ~ .ch-switch .ch-l-before,
.ch-r-after:checked ~ .ch-switch .ch-l-after {
  color: var(--text); background: var(--surface-2); border-bottom-color: var(--accent);
}
.ch-r-before:focus-visible ~ .ch-switch .ch-l-before,
.ch-r-after:focus-visible ~ .ch-switch .ch-l-after { outline: 2px solid var(--accent); outline-offset: -2px; }
.ch-frame {
  position: relative; width: 100%; overflow: hidden; cursor: pointer;
  border: 1px solid var(--border); border-radius: 8px; background: var(--bg);
  -webkit-tap-highlight-color: transparent;
}
.ch-img { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
.ch-r-before:checked ~ .ch-frame .ch-img-after { opacity: 0; }
.ch-r-before:checked ~ .ch-frame .ch-tag-after,
.ch-r-after:checked ~ .ch-frame .ch-tag-before { display: none; }
.ch-view figcaption { margin: .5rem 0 0; font-size: .82rem; line-height: 1.5; color: var(--text-2); }
.ch-mark-label {
  position: absolute; transform: translateY(-50%); margin-left: .35rem;
  width: max-content; max-width: 40%;
  padding: .15rem .45rem; border-radius: 4px; border: 1px solid var(--action);
  background: rgba(16, 49, 156, .9); color: var(--text); font-size: .75rem; line-height: 1.35;
  pointer-events: none;
}
.ch-mark-label-left { margin-left: 0; margin-right: .35rem; }

.ch-body { line-height: 1.65; font-size: .95rem; }
.ch-body h2 { font-size: 1.08rem; margin: 1.8rem 0 .5rem; }
.ch-body p { margin: 0 0 .9rem; }
.ch-body ul { margin: 0 0 .9rem; padding-left: 1.15rem; }
.ch-body li { margin: 0 0 .45rem; }
.ch-body b { color: var(--text); font-weight: 600; }
.ch-body a { color: var(--accent); }
.ch-links {
  display: flex; flex-wrap: wrap; gap: .25rem 1.25rem;
  margin: 1.5rem 0 0; padding-top: 1rem; border-top: 1px solid var(--border); font-size: .88rem;
}
.ch-links a { color: var(--accent); padding: .35rem 0; }
.ch-back { margin: 2.5rem 0 0; border-top: 1px solid var(--border); padding-top: 1rem; }
.ch-back a { text-decoration: none; padding: .35rem 0; display: inline-block; }
.ch-back a:hover, .ch-links a:hover { text-decoration: underline; }

/* The entry in the feed's modal: the viewer's card is the frame and this
   scrolls inside it, clear of the close button, with the page's pinch-zoom
   left on for looking closer at a picture. */
.ch-modal {
  overflow-y: auto; overscroll-behavior: contain; touch-action: pan-y pinch-zoom;
  padding: 3.4rem 1rem 2.5rem;
}
.ch-modal .ch-detail { max-width: 64rem; margin: 0 auto; }
.ch-loading { color: var(--text-2); text-align: center; margin: 3rem 0; }

@media (min-width: 48rem) {
  .ch-pair { gap: .5rem; }
  .ch-dtitle { font-size: 1.4rem; }
  .ch-modal { padding-inline: 1.5rem; }
}
@media (pointer: coarse) {
  .ch-card { padding: 1rem .9rem; }
}
` + FIGURE_CSS;

function sendPage(res, title, body) {
  res.set("Content-Type", "text/html; charset=utf-8");
  res.set("Cache-Control", "no-cache");
  res.send(
    renderHead({ title, pageStyles: CHANGES_CSS }) +
    renderNav({ active: "changes" }) +
    body +
    `<script src="/content-viewer.js"></script>\n<script type="module" src="/changes.js"></script>\n` +
    renderFooter()
  );
}

// --- the carry -------------------------------------------------------------

// HOW THE DEPLOYED CONTAINER LEARNS OF AN ENTRY ITS CLONE PREDATES. GitHub's API names what
// `changes/` holds on main, file by file, with each file's git blob hash; a file this disk holds
// under another hash, or not at all, comes down from raw.githubusercontent.com and is kept only
// when its bytes hash to the name. Two calls at most: main's root tree, which names the
// `changes/` subtree, and that subtree whole — and the second only when the first says it moved.
//
// THE CALL BUDGET IS SHARED. Unauthenticated GitHub allows 60 calls an hour to this address,
// and `artifacts-live.js` spends about 30 of them adopting the pointer file. So a look is taken
// only when someone asks for the feed, no more than once a minute, and stands down whenever
// GitHub reports fewer than `RESERVE` calls left — the pointer file's adoption matters more
// than a feed that is a minute behind.
//
// The bytes come off `main` on raw, whose cache can serve a path's previous bytes for up to five
// minutes after it changes. The hash check is what makes that harmless: a stale file is not
// kept, the subtree is not counted as reached, and the next look asks again.
//
// IT REPORTS AND HOLDS NOTHING: a failure anywhere leaves the feed serving what this disk has.

const GITHUB = "https://api.github.com/repos/derekbreden/homesodamachine";
const RAW = "https://raw.githubusercontent.com/derekbreden/homesodamachine/main/changes/";
const LOOK_EVERY_MS = 60_000;
const LOOK_WAIT_MS = 1_500;
const RESERVE = 20;
const MAX_FILE_BYTES = 16 * 1024 * 1024;
const API_HEADERS = { accept: "application/vnd.github+json", "user-agent": "homesodamachine-site" };

export function blobSha(bytes) {
  return createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex");
}

// Within an entry the pictures land first, then views.json, then entry.md, so a reader meets
// an entry only once what it names is already on the disk.
const rank = (file) => (file === ENTRY ? 2 : file === VIEWS ? 1 : 0);

export function makeCarry({ changesDir, fetchImpl = fetch, now = Date.now, log = console } = {}) {
  let lastLook = -Infinity;
  let holdUntil = 0;
  let running = null;
  let rootTag = null;
  // The `changes/` subtree this disk was last brought all the way to.
  let reached = null;
  const hashes = new Map();

  function localSha(abs) {
    try {
      const st = fs.statSync(abs);
      if (!st.isFile()) return null;
      const key = `${st.mtimeMs}:${st.size}`;
      const hit = hashes.get(abs);
      if (hit && hit.key === key) return hit.sha;
      const sha = blobSha(fs.readFileSync(abs));
      hashes.set(abs, { key, sha });
      return sha;
    } catch {
      return null;
    }
  }

  // Every answer says how much of the hour is left; below the reserve, the next look waits for
  // the hour to turn over.
  function budget(res) {
    const left = Number(res.headers.get("x-ratelimit-remaining"));
    const reset = Number(res.headers.get("x-ratelimit-reset")) * 1000;
    if (Number.isFinite(left) && left < RESERVE && reset > now()) holdUntil = Math.max(holdUntil, reset);
  }

  function refused(res) {
    if (res.status === 403 || res.status === 429) {
      const after = Number(res.headers.get("retry-after")) * 1000 || 0;
      const reset = Number(res.headers.get("x-ratelimit-reset")) * 1000 || 0;
      holdUntil = now() + Math.min(Math.max(after, reset - now(), 10 * 60_000), 60 * 60_000);
    }
    return new Error(`GitHub says ${res.status} ${res.statusText}`);
  }

  async function bring(id, file, sha) {
    const abs = path.join(changesDir, id, file);
    const res = await fetchImpl(`${RAW}${id}/${encodeURIComponent(file)}`, {
      headers: { "user-agent": API_HEADERS["user-agent"] },
    });
    if (!res.ok) throw new Error(`${id}/${file}: raw says ${res.status}`);
    const bytes = Buffer.from(await res.arrayBuffer());
    if (blobSha(bytes) !== sha) throw new Error(`${id}/${file}: not yet the bytes main names`);
    await fsp.mkdir(path.dirname(abs), { recursive: true });
    const part = path.join(path.dirname(abs), `.${file}.${process.pid}.part`);
    await fsp.writeFile(part, bytes);
    await fsp.rename(part, abs);
  }

  async function look() {
    const root = await fetchImpl(`${GITHUB}/git/trees/main`, {
      headers: rootTag ? { ...API_HEADERS, "if-none-match": rootTag } : API_HEADERS,
    });
    budget(root);
    if (root.status === 304) return;
    if (!root.ok) throw refused(root);
    rootTag = root.headers.get("etag");
    const node = (await root.json()).tree?.find((t) => t.path === "changes" && t.type === "tree");
    if (!node || node.sha === reached) return;

    const sub = await fetchImpl(`${GITHUB}/git/trees/${node.sha}?recursive=1`, { headers: API_HEADERS });
    budget(sub);
    if (!sub.ok) throw refused(sub);
    const listing = await sub.json();

    // Entries only: a file directly inside a directory with an entry's name, in a directory
    // that holds an entry.md. The README beside them and anything nested deeper stay on GitHub.
    const want = new Map();
    for (const t of listing.tree ?? []) {
      if (t.type !== "blob") continue;
      const parts = t.path.split("/");
      if (parts.length !== 2 || !ID.test(parts[0]) || !fileOk(parts[1])) continue;
      if (!want.has(parts[0])) want.set(parts[0], new Map());
      want.get(parts[0]).set(parts[1], { sha: t.sha, size: t.size });
    }
    for (const [id, files] of want) if (!files.has(ENTRY)) want.delete(id);

    let whole = !listing.truncated;
    let brought = 0;
    for (const [id, files] of want) {
      const todo = [];
      for (const [file, f] of files) {
        if (f.size > MAX_FILE_BYTES) whole = false;
        else if (localSha(path.join(changesDir, id, file)) !== f.sha) todo.push([file, f]);
      }
      for (const r of [0, 1, 2]) {
        const results = await Promise.allSettled(
          todo.filter(([file]) => rank(file) === r).map(([file, f]) => bring(id, file, f.sha)));
        for (const out of results) {
          if (out.status === "fulfilled") brought += 1;
          else {
            whole = false;
            log.error(`[changes] carry: ${out.reason.message}`);
          }
        }
        // An entry whose pictures did not all arrive does not get its words yet.
        if (results.some((out) => out.status === "rejected")) break;
      }
    }

    // What main no longer holds leaves this disk too — only when the listing was whole, and
    // only from a directory that is an entry.
    let retired = 0;
    if (!listing.truncated) {
      let dirents = [];
      try {
        dirents = await fsp.readdir(changesDir, { withFileTypes: true });
      } catch { /* no changes/ here yet */ }
      for (const d of dirents) {
        if (!d.isDirectory() || !ID.test(d.name)) continue;
        const dir = path.join(changesDir, d.name);
        const files = want.get(d.name);
        if (!files) {
          if (isFile(path.join(dir, ENTRY))) {
            await fsp.rm(dir, { recursive: true, force: true });
            retired += 1;
          }
          continue;
        }
        for (const f of await fsp.readdir(dir)) {
          if (fileOk(f) && !files.has(f)) await fsp.rm(path.join(dir, f), { force: true });
        }
      }
    }

    if (whole) reached = node.sha;
    if (brought || retired) {
      log.log(`[changes] carried ${brought} file(s) from main${retired ? `, retired ${retired} entr${retired === 1 ? "y" : "ies"}` : ""}`);
    }
  }

  // Starts a look when one is due and hands back its promise, or null when none is.
  return function carry() {
    const t = now();
    if (running) return running;
    if (t < holdUntil || t - lastLook < LOOK_EVERY_MS) return null;
    lastLook = t;
    running = look()
      .catch((err) => log.error(`[changes] carry skipped: ${err.message}`))
      .finally(() => { running = null; });
    return running;
  };
}

// --- routes ----------------------------------------------------------------

export function mountChangesRoutes(app, { changesDir, carry = false } = {}) {
  const read = makeReader(changesDir);
  const look = carry ? makeCarry({ changesDir }) : null;

  // A due look is waited on for a moment, so an entry that landed a minute ago is on this page
  // rather than the next; a slow GitHub costs the page that moment and no more, and the look
  // carries on behind it for the next request.
  const fresh = async () => {
    const pending = look?.();
    if (!pending) return;
    await Promise.race([pending, new Promise((r) => setTimeout(r, LOOK_WAIT_MS).unref())]);
  };

  const limitOf = (q) => Math.min(Math.max(Number.parseInt(q, 10) || 10, 1), 50);
  const beforeOf = (q) => (typeof q === "string" && ID.test(q) ? q : "");

  app.get("/changes", async (req, res) => {
    const before = beforeOf(req.query.before);
    if (!before) await fresh();
    const { page, next } = pageAfter(read(), before, 10);
    sendPage(res, "Changes — Home Soda Machine", renderFeedBody(changesDir, page, next, before));
  });

  app.get("/api/changes", async (req, res) => {
    const before = beforeOf(req.query.before);
    if (!before) await fresh();
    const { page, next } = pageAfter(read(), before, limitOf(req.query.limit));
    res.set("Cache-Control", "no-cache");
    res.json({
      entries: page.map((e) => ({
        id: e.id, url: `/changes/${e.id}`, title: e.title, lede: e.lede, date: e.date,
        commits: e.commits, model: e.model,
        views: e.views.map((v) => ({
          name: v.name, caption: v.caption, width: v.width, height: v.height,
          before: imageUrl(changesDir, e, v.before), after: imageUrl(changesDir, e, v.after),
        })),
      })),
      html: page.map((e) => renderCard(changesDir, e)).join("\n"),
      next,
    });
  });

  app.get("/changes/:id", async (req, res, next) => {
    const { id } = req.params;
    if (!ID.test(id)) return next();
    let entry = read().find((e) => e.id === id);
    if (!entry) {
      await fresh();
      entry = read().find((e) => e.id === id);
    }
    if (!entry) return next();
    if (req.query.fragment) {
      res.set("Content-Type", "text/html; charset=utf-8");
      res.set("Cache-Control", "no-cache");
      return res.send(renderDetail(changesDir, entry));
    }
    sendPage(res, `${entry.title} — Changes`,
      `<main class="ch-wrap">
  ${renderDetail(changesDir, entry)}
  <p class="ch-back"><a href="/changes">All changes</a></p>
</main>`);
  });

  // Only a picture a usable view names is served; the rest of the directory is not a surface.
  app.get("/changes/:id/:file", (req, res, next) => {
    const { id, file } = req.params;
    if (!ID.test(id) || !fileOk(file)) return next();
    const entry = read().find((e) => e.id === id);
    if (!entry || !entry.views.some((v) => v.before === file || v.after === file)) return next();
    const abs = path.join(changesDir, id, file);
    const v = versionOf(abs);
    res.set("Content-Type", IMAGE_TYPES[path.extname(file).toLowerCase()]);
    res.set("Cache-Control", v && req.query.v === v ? "public, max-age=31536000, immutable" : "no-cache");
    // `send` refuses a path with a dot-prefixed component, and a git worktree lives under
    // `.claude/worktrees/…`; the path here is built from two names checked above.
    res.sendFile(abs, { dotfiles: "allow", cacheControl: false }, (err) => {
      if (err && !res.headersSent) next();
    });
  });
}
