// The Updates feed: one entry per reporting window, newest first.
//
// Entries are markdown files in `updates/` at the repo root. Each opens with a
// frontmatter block naming its window; the body renders from a fixed markdown
// subset — `##` headings, paragraphs, `-` bullets, `**bold**`, `[text](href)`.
// Text outside that subset renders literally.
//
// Both pages are server-rendered: `/updates` carries every entry's summary and
// `/updates/<slug>` carries one entry whole. Each response holds its entire
// document.

import fs from "node:fs";
import path from "node:path";
import { renderHead, renderNav, renderFooter } from "./shell.js";
import { FIGURES, FIGURE_CSS } from "./update-figures.js";

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ESC[c]);
}

// --- parsing ---------------------------------------------------------------

// Frontmatter is `key: value` lines between two `---` fences at the head of the
// file. A value runs to end of line.
export function parseFrontmatter(src) {
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(src);
  if (!m) return { meta: {}, body: src };
  const meta = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = /^([a-z_]+):\s*(.*)$/.exec(line.trim());
    if (kv) meta[kv[1]] = kv[2].trim();
  }
  return { meta, body: src.slice(m[0].length) };
}

function inline(s) {
  return esc(s)
    .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2">$1</a>');
}

// A figure line stands alone in the source and renders as a <figure>: either
// `{{fig:name}}`, drawn inline from the figure registry, or `![caption](src)`
// for a rendered image. Both carry their caption below the frame.
const FIG_LINE = /^\{\{fig:([a-z0-9-]+)\}\}$/;
const IMG_LINE = /^!\[([^\]]*)\]\(([^)\s]+)\)$/;

function figure(inner, caption, cls = "") {
  const cap = caption ? `<figcaption>${inline(caption)}</figcaption>` : "";
  return `<figure class="up-fig${cls ? " " + cls : ""}">${inner}${cap}</figure>`;
}

// A PNG's pixel size lives in the IHDR chunk, at a fixed offset behind the
// 8-byte signature. An <img> carrying it holds its own aspect ratio in the
// layout before the bytes arrive, so the prose below it never jumps.
export function pngSize(file) {
  let fd;
  try {
    fd = fs.openSync(file, "r");
    const head = Buffer.alloc(24);
    if (fs.readSync(fd, head, 0, 24, 0) < 24) return null;
    if (head.toString("latin1", 1, 4) !== "PNG") return null;
    return { w: head.readUInt32BE(16), h: head.readUInt32BE(20) };
  } catch {
    return null;
  } finally {
    if (fd !== undefined) fs.closeSync(fd);
  }
}

export function renderMarkdown(body, figures = {}, imageSize = () => null) {
  const out = [];
  let list = null;
  let para = null;
  const closeList = () => {
    if (list) out.push(`<ul>${list.join("")}</ul>`);
    list = null;
  };
  const closePara = () => {
    if (para) out.push(`<p>${inline(para.join(" "))}</p>`);
    para = null;
  };
  for (const raw of body.split(/\r?\n/)) {
    const line = raw.trim();
    const fig = FIG_LINE.exec(line);
    const img = IMG_LINE.exec(line);
    if (!line) {
      closeList();
      closePara();
    } else if (fig) {
      closeList();
      closePara();
      const f = figures[fig[1]];
      if (f) out.push(figure(`<div class="up-fig-scroll">${f.svg}</div>`, f.caption, f.cls));
    } else if (img) {
      closeList();
      closePara();
      const size = imageSize(img[2]);
      const dims = size ? ` width="${size.w}" height="${size.h}"` : "";
      out.push(figure(
        `<img src="${esc(img[2])}" alt="${esc(img[1])}"${dims} loading="lazy" decoding="async">`,
        img[1], "up-fig-photo"
      ));
    } else if (line.startsWith("## ")) {
      closeList();
      closePara();
      out.push(`<h2>${inline(line.slice(3))}</h2>`);
    } else if (line.startsWith("- ")) {
      closePara();
      (list ||= []).push(`<li>${inline(line.slice(2))}</li>`);
    } else {
      closeList();
      (para ||= []).push(line);
    }
  }
  closeList();
  closePara();
  return out.join("\n");
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function fmtRange(start, end) {
  const [sy, sm, sd] = start.split("-").map(Number);
  const [ey, em, ed] = end.split("-").map(Number);
  const s = `${MONTHS[sm - 1]} ${sd}`;
  const e = `${MONTHS[em - 1]} ${ed}`;
  return sy === ey ? `${s} – ${e}, ${ey}` : `${s}, ${sy} – ${e}, ${ey}`;
}

const KIND_LABEL = { week: "Week", period: "Four weeks" };

const days = (p) => (Date.parse(p.end) - Date.parse(p.start)) / 86400000;

// Newest window first. Windows sharing an end date run widest first, so a
// four-week entry leads the weeks that close with it.
function byRecency(a, b) {
  if (a.end !== b.end) return a.end < b.end ? 1 : -1;
  return days(b) - days(a);
}

export function readUpdates(updatesDir) {
  let names;
  try {
    names = fs.readdirSync(updatesDir).filter((f) => f.endsWith(".md"));
  } catch {
    return [];
  }
  const posts = [];
  for (const name of names) {
    const src = fs.readFileSync(path.join(updatesDir, name), "utf8");
    const { meta, body } = parseFrontmatter(src);
    if (!meta.start || !meta.end || !meta.title) continue;
    posts.push({
      slug: name.replace(/\.md$/, ""),
      title: meta.title,
      start: meta.start,
      end: meta.end,
      kind: meta.kind === "week" ? "week" : "period",
      lede: meta.lede || "",
      image: meta.image || "",
      image_alt: meta.image_alt || "",
      image_fig: meta.image_fig || "",
      body,
    });
  }
  return posts.sort(byRecency);
}

// --- rendering -------------------------------------------------------------

function renderCard(p, imageSize) {
  // An entry leads with a photograph, a render, or one of its own drawings.
  // Where the entry is about a difference in size, the drawing leads: a render
  // is framed and trimmed per model, so two of them side by side share no
  // scale. The picture stands only when it is actually there, so a row whose
  // image has not been made yet reads as text rather than a broken frame.
  const fig = p.image_fig ? FIGURES[p.image_fig] : null;
  const size = p.image ? imageSize(p.image) : null;
  const shot = fig
    ? `<span class="up-shot up-shot-fig">${fig.svg}</span>`
    : size
      ? `<span class="up-shot"><img src="${esc(p.image)}" alt="${esc(p.image_alt || p.title)}"` +
        ` width="${size.w}" height="${size.h}" loading="lazy" decoding="async"></span>`
      : "";
  return `<li class="up-item">
  <a href="/updates/${esc(p.slug)}">
    ${shot}
    <span class="up-text">
      <span class="up-meta"><span class="up-kind up-kind-${esc(p.kind)}">${esc(KIND_LABEL[p.kind])}</span>
      <span class="up-range">${esc(fmtRange(p.start, p.end))}</span></span>
      <span class="up-title">${esc(p.title)}</span>
      ${p.lede ? `<span class="up-lede">${esc(p.lede)}</span>` : ""}
    </span>
  </a>
</li>`;
}

export function renderIndexBody(posts, imageSize = () => null) {
  if (!posts.length) {
    return `<main class="up-wrap"><h1 class="up-h1">Updates</h1>
  <p class="up-empty">No entries.</p></main>`;
  }
  const first = posts[posts.length - 1].start;
  const last = posts[0].end;
  return `<main class="up-wrap">
  <h1 class="up-h1">Updates</h1>
  <p class="up-lede-top">What changed in the machine, ${esc(fmtRange(first, last))}.
  Four-week entries cover a whole period; week entries cover the most recent one.</p>
  ${FIGURES.timeline ? `<figure class="up-fig"><div class="up-fig-scroll">${FIGURES.timeline.svg}</div><figcaption>${esc(FIGURES.timeline.caption)}</figcaption></figure>` : ""}
  <ul class="up-list">
${posts.map((p) => renderCard(p, imageSize)).join("\n")}
  </ul>
</main>`;
}

export function renderPostBody(p, imageSize) {
  return `<main class="up-wrap up-post">
  <p class="up-meta"><span class="up-kind up-kind-${esc(p.kind)}">${esc(KIND_LABEL[p.kind])}</span>
  <span class="up-range">${esc(fmtRange(p.start, p.end))}</span></p>
  <h1 class="up-h1">${esc(p.title)}</h1>
  ${p.lede ? `<p class="up-lede-top">${esc(p.lede)}</p>` : ""}
  <div class="up-body">
${renderMarkdown(p.body, FIGURES, imageSize)}
  </div>
  <p class="up-back"><a href="/updates">All updates</a></p>
</main>`;
}

const UPDATES_CSS = `
/* The shell lays body out as a flex column, where the line's cross size grows
   to the widest item and stretches the rest to match. An explicit width keeps
   this column on the viewport, so a figure wider than it scrolls in its own
   track instead of taking the page sideways. */
.up-wrap { width: 100%; max-width: 46rem; min-width: 0; margin: 0 auto; padding: 1.5rem 1rem 5rem; }
.up-h1 { font-size: 1.6rem; margin: 0 0 .5rem; line-height: 1.25; }
.up-lede-top { color: var(--text-2); line-height: 1.55; margin: 0 0 1.5rem; font-size: .92rem; }
.up-empty { color: var(--text-2); }

.up-list { list-style: none; margin: 0; padding: 0; }
.up-item { border-top: 1px solid var(--border); }
.up-item:last-child { border-bottom: 1px solid var(--border); }
/* A row leads with the thing the entry is about, at the full width of the
   column and its own aspect. These drawings carry the whole machine — the box,
   the cold core, every board and reservoir — and the entry is recognised by
   that subject, so the picture gets the width the detail is drawn at. It is
   never boxed to a common height: a tall subject makes a tall row, and nothing
   is cropped. */
.up-item > a {
  display: flex; flex-direction: column; gap: .7rem;
  padding: 1rem .35rem 1.2rem; text-decoration: none; color: inherit;
}
.up-text { display: flex; flex-direction: column; gap: .35rem; min-width: 0; }
.up-shot {
  display: block; width: 100%; background: var(--bg);
  border: 1px solid var(--border); border-radius: 8px; overflow: hidden;
}
.up-shot img { width: 100%; height: auto; display: block; }
/* A drawing leading a row scales to the row; its full-size reading, with the
   labels at the width they were drawn for, is in the entry itself. */
.up-shot-fig { background: var(--surface); padding: .5rem 0; }
.up-shot-fig svg.uf { min-width: 0; border: 0; background: none; padding: 0; }
.up-item > a:hover { background: var(--surface); }
.up-item > a:hover .up-title { color: var(--accent); }
.up-item > a:hover .up-shot { border-color: var(--accent); }

.up-meta { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.up-kind {
  font-size: .68rem; letter-spacing: .06em; text-transform: uppercase;
  padding: .12rem .4rem; border-radius: 4px; border: 1px solid var(--border);
  color: var(--text-2); white-space: nowrap;
}
.up-kind-period { color: var(--accent); border-color: var(--accent); }
.up-range { font-size: .8rem; color: var(--text-2); }
.up-title { font-size: 1.05rem; font-weight: 600; line-height: 1.35; }
.up-lede { font-size: .88rem; color: var(--text-2); line-height: 1.5; }

.up-post .up-meta { margin: 0 0 .4rem; }
.up-body { line-height: 1.65; font-size: .95rem; }
.up-body h2 { font-size: 1.08rem; margin: 1.8rem 0 .5rem; }
.up-body p { margin: 0 0 .9rem; }
.up-body ul { margin: 0 0 .9rem; padding-left: 1.15rem; }
.up-body li { margin: 0 0 .45rem; }
.up-body b { color: var(--text); font-weight: 600; }
.up-body a { color: var(--accent); }
.up-back { margin: 2.5rem 0 0; border-top: 1px solid var(--border); padding-top: 1rem; }
.up-back a { color: var(--accent); text-decoration: none; padding: .35rem 0; display: inline-block; }
.up-back a:hover { text-decoration: underline; }

.up-item > a:focus-visible, .up-back a:focus-visible, .up-body a:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 2px;
}

@media (pointer: coarse) {
  .up-item > a { padding: 1rem .35rem; }
  .up-back a { min-height: 40px; display: inline-flex; align-items: center; }
}
` + FIGURE_CSS;

export function mountUpdatesRoutes(app, { updatesDir, publicDir }) {
  // Posts name their images by URL path; the file behind one lives under the
  // public root. Only the feed's own image directory resolves.
  const imageSize = (src) => {
    if (!publicDir || !src.startsWith("/update-images/") || src.includes("..")) return null;
    return pngSize(path.join(publicDir, src));
  };

  app.get("/api/updates", (_req, res) => {
    res.set("Cache-Control", "no-cache");
    res.json(readUpdates(updatesDir).map(({ body, ...rest }) => rest));
  });

  app.get("/updates", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    const surface = res.locals && res.locals.surface === "dev" ? "dev" : "public";
    res.send(
      renderHead({ title: "Updates — Home Soda Machine", pageStyles: UPDATES_CSS }) +
      renderNav({ surface, active: "updates" }) +
      renderIndexBody(readUpdates(updatesDir), imageSize) +
      renderFooter()
    );
  });

  app.get("/updates/:slug", (req, res, next) => {
    const post = readUpdates(updatesDir).find((p) => p.slug === req.params.slug);
    if (!post) return next();
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    const surface = res.locals && res.locals.surface === "dev" ? "dev" : "public";
    res.send(
      renderHead({ title: `${post.title} — Updates`, pageStyles: UPDATES_CSS }) +
      renderNav({ surface, active: "updates" }) +
      renderPostBody(post, imageSize) +
      renderFooter()
    );
  });
}
