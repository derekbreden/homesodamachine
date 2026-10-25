// /latest — where Changes and Updates both begin: the newest few of each, a line on what each
// one is, and the way into its whole feed.
//
// The nav carries one item for the two, and this is where it lands. The feeds and every entry
// keep their own addresses — /changes, /changes/<id>, /updates, /updates/<slug> — so a
// thumbnail here opens its item directly and a section's header opens its feed. Each half is
// read the way its own feed reads it, the changes through the reader and carry lib/changes.js
// hands over and the posts through lib/updates.js, so the hub shows what the feeds show.

import { renderHead, renderNav, renderPageHeader, renderFooter } from "./shell.js";
import { imageUrl } from "./changes.js";
import { readUpdates, fmtRange, KIND_LABEL, imageSizer } from "./updates.js";
import { FIGURES, FIGURE_CSS } from "./update-figures.js";
import { iconSvg } from "../contracts/icons.js";

const ESC = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" };
function esc(s) {
  return String(s ?? "").replace(/[&<>"]/g, (c) => ESC[c]);
}

const CHANGES_SHOWN = 3;
const UPDATES_SHOWN = 2;

// An item with no picture keeps its frame and carries its words in it, so every thumbnail on
// the hub is the same shape and a row stays a row.
const words = (text) => `<span class="lt-shot lt-shot-words"><span>${esc(text)}</span></span>`;

// A change at thumbnail size: its first view as one frame cut down the middle, the Before's
// left half against the After's right. Two pictures side by side would each be too small to
// read here, and one frame cut at the middle still reads as a before and after; the render
// tool aims a view at what moved, so the cut runs through the change. Both pictures share one
// size, so they crop alike and stay in register.
function changeThumb(changesDir, e) {
  const view = e.views[0];
  const shot = view
    ? `<span class="lt-shot lt-split">` +
      `<img src="${esc(imageUrl(changesDir, e, view.before))}" alt="" loading="lazy" decoding="async">` +
      `<img class="lt-after" src="${esc(imageUrl(changesDir, e, view.after))}"` +
      ` alt="${esc(`Before and after: ${view.caption || e.title}`)}" loading="lazy" decoding="async">` +
      `<span class="lt-rule" aria-hidden="true"></span>` +
      `<span class="lt-tag">Before</span><span class="lt-tag lt-tag-after">After</span></span>`
    : words(e.lede || "No pictures yet.");
  return `<li class="lt-item"><a class="lt-card" href="/changes/${e.id}">
      ${shot}
      <span class="lt-title">${esc(e.title)}</span>
      ${e.shown ? `<span class="lt-meta">${esc(e.shown)}</span>` : ""}
    </a></li>`;
}

// A post at thumbnail size: its picture, else its drawing, else its words.
function updateThumb(p, imageSize) {
  const size = p.image ? imageSize(p.image) : null;
  const fig = !size && p.image_fig ? FIGURES[p.image_fig] : null;
  const shot = size
    ? `<span class="lt-shot"><img src="${esc(p.image)}" alt="${esc(p.image_alt || p.title)}"` +
      ` width="${size.w}" height="${size.h}" loading="lazy" decoding="async"></span>`
    : fig
      ? `<span class="lt-shot lt-shot-fig">${fig.svg}</span>`
      : words(p.lede || p.title);
  return `<li class="lt-item"><a class="lt-card" href="/updates/${esc(p.slug)}">
      ${shot}
      <span class="lt-title">${esc(p.title)}</span>
      <span class="lt-meta">${esc(KIND_LABEL[p.kind])} · ${esc(fmtRange(p.start, p.end))}</span>
    </a></li>`;
}

function section({ id, name, href, all, desc, items, empty }) {
  return `<section class="lt-sec" aria-labelledby="lt-${id}">
    <div class="lt-head">
      <h2 class="lt-h2" id="lt-${id}"><a href="${href}">${name}</a></h2>
      <a class="lt-all" href="${href}">${all}${iconSvg("arrow-right")}</a>
    </div>
    <p class="lt-desc">${desc}</p>
    ${items.length
      ? `<ul class="lt-grid lt-grid-${id}">\n${items.join("\n")}\n    </ul>`
      : `<p class="lt-empty">${empty}</p>`}
  </section>`;
}

export function renderLatestBody({ changesDir, changes, posts, imageSize }) {
  return renderPageHeader({ eyebrow: "Latest", title: "The latest from the build.", description: "Design changes and progress from the workshop, as the machine takes shape." }) + `<main class="lt-wrap site-content">
  ${section({
    id: "changes", name: "Changes", href: "/changes", all: "All changes",
    desc: "Every change to the enclosure, shown before and after, as it lands.",
    items: changes.slice(0, CHANGES_SHOWN).map((e) => changeThumb(changesDir, e)),
    empty: "No changes recorded yet.",
  })}
  ${section({
    id: "updates", name: "Updates", href: "/updates", all: "All updates",
    desc: "A written account of each week, and of each four-week period.",
    items: posts.slice(0, UPDATES_SHOWN).map((p) => updateThumb(p, imageSize)),
    empty: "No updates yet.",
  })}
</main>`;
}

const LATEST_CSS = `
.lt-sec { margin: 0 0 2.25rem; }
.lt-head {
  display: flex; align-items: baseline; justify-content: space-between; gap: 1rem;
  border-top: 1px solid var(--border); padding-top: .9rem;
}
.lt-h2 { font-size: 1.25rem; margin: 0; line-height: 1.3; }
.lt-h2 a { color: inherit; text-decoration: none; }
.lt-h2 a:hover { color: var(--accent); }
.lt-all {
  display: inline-flex; align-items: center; gap: .3rem; padding: .4rem 0;
  color: var(--accent); font-size: .85rem; text-decoration: none; white-space: nowrap;
}
.lt-all:hover { text-decoration: underline; }
.lt-all svg { width: .95rem; height: .95rem; flex-shrink: 0; }
.lt-desc { color: var(--text-2); font-size: .9rem; line-height: 1.5; margin: .2rem 0 1rem; }
.lt-empty {
  margin: 0; padding: 1.4rem 1rem; text-align: center; font-size: .88rem; color: var(--text-3);
  border: 1px dashed var(--border); border-radius: 8px;
}

/* Two columns on a phone, and the newest change across both, so the hub
   opens on a picture rather than a list. Three on a wider screen, for both
   sections, so every thumbnail on the hub is one size. */
.lt-grid {
  list-style: none; margin: 0; padding: 0;
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.1rem .75rem;
}
.lt-grid-changes > :first-child,
.lt-grid-changes > :nth-child(2):last-child,
.lt-grid > :only-child { grid-column: 1 / -1; }
.lt-item { min-width: 0; }
.lt-card { display: flex; flex-direction: column; gap: .45rem; color: inherit; text-decoration: none; min-width: 0; }
.lt-card:hover .lt-title { color: var(--accent); }
.lt-card:hover .lt-shot { border-color: var(--accent); }
.lt-card:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 8px; }
.lt-shot {
  position: relative; display: block; aspect-ratio: 4 / 3; overflow: hidden;
  border: 1px solid var(--border); border-radius: 8px; background: var(--bg);
}
.lt-shot img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }
.lt-split .lt-after { clip-path: inset(0 0 0 50%); }
.lt-rule {
  position: absolute; top: 0; bottom: 0; left: 50%; width: 2px; margin-left: -1px;
  background: var(--text); box-shadow: 0 0 0 1px rgba(0, 0, 0, .35);
}
.lt-tag {
  position: absolute; top: .4rem; left: .4rem;
  font-size: .6rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
  padding: .1rem .35rem; border-radius: 4px; line-height: 1.4;
  background: rgba(16, 49, 156, .82); color: var(--text-2); pointer-events: none;
}
.lt-tag-after { left: auto; right: .4rem; }
.lt-shot-fig { background: var(--surface); }
.lt-shot-words { display: flex; align-items: center; justify-content: center; padding: .9rem; background: var(--surface); }
.lt-shot-words span {
  font-size: .82rem; line-height: 1.5; color: var(--text-2); text-align: center;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 5; overflow: hidden;
}
.lt-shot-fig svg.uf { position: absolute; inset: 0; width: 100%; height: 100%; padding: .4rem; }
.lt-title {
  font-size: .95rem; font-weight: 600; line-height: 1.35;
  display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden;
}
.lt-grid-changes > :first-child .lt-title { font-size: 1.05rem; }
.lt-meta { font-size: .75rem; color: var(--text-3); }

@media (min-width: 48rem) {
  .lt-grid { gap: 1.25rem 1rem; }
  .lt-grid { grid-template-columns: repeat(3, 1fr); }
  .lt-grid-changes > :first-child,
  .lt-grid-changes > :nth-child(2):last-child,
  .lt-grid > :only-child { grid-column: auto; }
  .lt-grid-changes > :first-child .lt-title { font-size: .95rem; }
}
` + FIGURE_CSS;

export function mountLatestRoutes(app, { changesDir, changes, updatesDir, publicDir }) {
  const imageSize = imageSizer(publicDir);
  app.get("/latest", async (_req, res) => {
    // The changes carry looks here too, so an entry that landed a minute ago leads the hub.
    await changes.fresh();
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({ title: "Latest — Home Soda Machine", pageStyles: LATEST_CSS, pageClass: "site-interior" }) +
      renderNav({ active: "latest" }) +
      renderLatestBody({ changesDir, changes: changes.read(), posts: readUpdates(updatesDir), imageSize }) +
      renderFooter({ siteFooter: true })
    );
  });
}
