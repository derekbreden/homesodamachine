import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import matter from "gray-matter";
import { marked } from "marked";
import { renderHead, renderNav, renderFooter } from "./shell.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(__dirname, "..", "public");

// Read a local PNG's pixel dimensions from its IHDR header (width at byte
// 16, height at byte 20, both big-endian). Memoized by src — post images
// don't change within a process. Returns null for anything we can't
// resolve to a .png under public/, so the caller just omits the attrs.
//
// Why: post images lazy-load, and without intrinsic dimensions an <img>
// occupies zero height until it loads, then shoves everything below it
// down. That layout shift is most visible on a deep link — the page
// scrolls to the target post, then an image in the post above loads and
// drags the target out of view. Emitting width/height reserves the space.
const pngSizeCache = new Map();
function pngSize(src) {
  if (pngSizeCache.has(src)) return pngSizeCache.get(src);
  let dims = null;
  if (/^\/[^?#]+\.png$/i.test(src)) {
    const rel = src.replace(/^\//, "").split("/").map(decodeURIComponent).join(path.sep);
    const file = path.join(PUBLIC_DIR, rel);
    // Stay inside public/ — never let a crafted src walk the filesystem.
    if (file === PUBLIC_DIR || file.startsWith(PUBLIC_DIR + path.sep)) {
      let fd;
      try {
        fd = fs.openSync(file, "r");
        const buf = Buffer.alloc(24);
        const n = fs.readSync(fd, buf, 0, 24, 0);
        if (n >= 24 && buf.toString("ascii", 1, 4) === "PNG") {
          dims = { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
        }
      } catch {
        // Missing/unreadable/not-a-PNG — fall through to null.
      } finally {
        if (fd !== undefined) try { fs.closeSync(fd); } catch {}
      }
    }
  }
  pngSizeCache.set(src, dims);
  return dims;
}

// Render the blog index page from markdown files in `postsDir`.
// Posts are read at request time (count is small, grows slowly), parsed for
// YAML frontmatter, sorted by `date` descending, and concatenated into a
// single page. Malformed posts are skipped with a warning so one bad file
// can't take down the page.

// Add target="_blank" rel="noopener" to absolute http(s) links in post
// bodies, so external links (YouTube, GitHub, Amazon, etc.) hand off to
// the OS-native handler — Universal Link into the YouTube app on iOS,
// Intent on Android, new tab on desktop — instead of replacing the blog
// in the current window. Internal links and same-origin paths fall
// through unchanged so /blog#post-foo or /3d?file=… stay in-window.
marked.use({
  hooks: {
    postprocess(html) {
      return html
        .replace(
          /<a href="(https?:\/\/[^"]+)"/g,
          '<a href="$1" target="_blank" rel="noopener"',
        )
        // Defer image fetches until each <img> nears the viewport (the feed
        // concatenates every post's images; without this the browser pulls
        // megabytes up front), decode off the main thread, and reserve the
        // image's space via width/height so lazy loading never shifts the
        // layout. The CSS keeps them responsive (max-width:100%; height:auto).
        .replace(/<img\b[^>]*\bsrc="([^"]+)"[^>]*>/g, (tag, src) => {
          const d = pngSize(src);
          const dims = d ? ` width="${d.w}" height="${d.h}"` : "";
          return tag.replace(/^<img\b/, `<img loading="lazy" decoding="async"${dims}`);
        });
    },
  },
});

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDate(filename) {
  // Use the YYYY-MM-DD from the filename so the displayed calendar date
  // matches the day the post is about, regardless of the server's timezone.
  // (Render runs in UTC; using getMonth/getDate on the parsed Date would
  // shift the day-of-month for any post written in a non-UTC zone.)
  const m = String(filename).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return "";
  const monthIdx = parseInt(m[2], 10) - 1;
  const day = parseInt(m[3], 10);
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];
  return `${months[monthIdx]} ${day}, ${m[1]}`;
}

// Match the post filename format documented in posts/README.md
// (`YYYY-MM-DD-HHMM.md`) so docs/helpers like posts/README.md aren't
// attempted as posts. Without this filter the README slips in, fails the
// frontmatter check on every blog request, and logs a warning each time.
const POST_FILENAME_RE = /^\d{4}-\d{2}-\d{2}-\d{4}\.md$/;

function loadPosts(postsDir) {
  if (!fs.existsSync(postsDir)) return [];
  const entries = fs.readdirSync(postsDir, { withFileTypes: true });
  const posts = [];
  for (const entry of entries) {
    if (!entry.isFile() || !POST_FILENAME_RE.test(entry.name)) continue;
    const full = path.join(postsDir, entry.name);
    let raw;
    try {
      raw = fs.readFileSync(full, "utf-8");
    } catch (e) {
      console.warn(`blog: could not read ${entry.name}: ${e.message}`);
      continue;
    }
    let parsed;
    try {
      parsed = matter(raw);
    } catch (e) {
      console.warn(`blog: could not parse frontmatter in ${entry.name}: ${e.message}`);
      continue;
    }
    const dateStr = parsed.data?.date;
    if (!dateStr) {
      console.warn(`blog: missing date in ${entry.name}`);
      continue;
    }
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      console.warn(`blog: invalid date in ${entry.name}: ${dateStr}`);
      continue;
    }
    posts.push({
      filename: entry.name,
      date,
      title: parsed.data?.title,
      body: parsed.content,
    });
  }
  posts.sort((a, b) => b.date.getTime() - a.date.getTime());
  return posts;
}

const PAGE_STYLES = `
.wrap {
  max-width: 44rem;
  margin: 0 auto;
  /* Safe-area on sides (iPhone landscape) and bottom (PWA home indicator).
     Top doesn't need it — the sticky nav above eats safe-area-top. */
  padding:
    2.5rem
    calc(env(safe-area-inset-right, 0px) + 1.5rem)
    calc(env(safe-area-inset-bottom, 0px) + 4rem)
    calc(env(safe-area-inset-left, 0px) + 1.5rem);
}
header.page { margin-bottom: 2.5rem; }
h1 {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 600;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}
.post {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1.75rem 1.75rem 1.5rem;
  margin-bottom: 1.5rem;
  /* Deep links (/blog#post-<slug> from notification taps, the in-app
     toast, and the notifications list) jump here via the native anchor
     scroll or scrollIntoView. Offset by the sticky-nav height + the
     notch so the post title lands below the nav instead of behind it. */
  scroll-margin-top: calc(env(safe-area-inset-top, 0px) + 3rem);
}
.post:last-child { margin-bottom: 0; }
.post-title {
  font-size: 1.375rem;
  font-weight: 600;
  margin: 0 0 0.375rem;
  letter-spacing: -0.01em;
}
.post-date {
  display: block;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-2);
  margin-bottom: 1.125rem;
}
.post-body { color: var(--text-2); }
.post-body p { margin: 0 0 0.75rem; }
.post-body p:last-child { margin-bottom: 0; }
.post-body ul, .post-body ol { padding-left: 1.25rem; margin: 0 0 0.75rem; }
.post-body ul ul, .post-body ol ol,
.post-body ul ol, .post-body ol ul { margin: 0.25rem 0; }
.post-body li { margin: 0.15rem 0; }
.post-body li::marker { color: var(--text-3); }
.post-body strong { color: var(--text); }
.post-body code {
  background: var(--surface-2);
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.9em;
  color: var(--text);
}
.post-body pre {
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 0.75rem 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin: 0 0 0.75rem;
}
.post-body pre code { background: none; padding: 0; }
.post-body a { color: var(--accent); }
.post-body a:hover { text-decoration: underline; }
.post-body h1, .post-body h2, .post-body h3,
.post-body h4, .post-body h5, .post-body h6 {
  color: var(--text);
  margin: 1rem 0 0.5rem;
}
.post-body img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.25rem auto;
  border-radius: 6px;
  background: var(--bg);
}
.empty { color: var(--text-3); text-align: center; padding: 4rem 0; }
/* Infinite-scroll sentinel. Reserves a line of height (via the always-laid-
   out Loading label) so it has a stable position for the observer; the
   label only becomes visible while a page is in flight. */
#blog-sentinel { padding: 1.25rem 0 0.5rem; text-align: center; }
.blog-loading { color: var(--text-3); font-size: 0.9rem; visibility: hidden; }
#blog-sentinel.loading .blog-loading { visibility: visible; }
`;

// Posts streamed per request. The first page is server-rendered into the
// initial HTML; /blog/posts hands out the rest in PAGE_SIZE chunks as the
// reader scrolls (see public/blog.js). One page comfortably overflows a
// phone viewport, so the sentinel gets pushed off-screen after each load.
const PAGE_SIZE = 10;

function renderArticle(p) {
  const html = marked.parse(p.body);
  const dateAttr = (p.filename.match(/^(\d{4}-\d{2}-\d{2})/) || [])[1] || "";
  const slug = p.filename.replace(/\.md$/, "");
  const titleHtml = p.title
    ? `<h2 class="post-title">${escapeHtml(p.title)}</h2>\n        `
    : "";
  return `      <article class="post" id="post-${escapeHtml(slug)}">
        ${titleHtml}<time class="post-date" datetime="${escapeHtml(dateAttr)}">${escapeHtml(formatDate(p.filename))}</time>
        <div class="post-body">${html}</div>
      </article>`;
}

function renderPage(posts) {
  const articles = posts.slice(0, PAGE_SIZE).map(renderArticle).join("\n");

  // Sentinel carries the next offset and is what the client observes to
  // page in more posts. Omitted when the first page is already everything.
  const sentinel = posts.length > PAGE_SIZE
    ? `\n  <div id="blog-sentinel" data-next-offset="${PAGE_SIZE}" aria-hidden="true"><span class="blog-loading">Loading…</span></div>`
    : "";

  const body = `<div class="wrap">
  <header class="page"><h1>Updates</h1></header>
${posts.length === 0 ? `  <p class="empty">No posts yet.</p>` : articles}${sentinel}
</div>
<script src="/pan-zoom.js"></script>
<script src="/content-viewer.js"></script>
<script src="/blog.js" defer></script>
`;

  return (
    renderHead({
      title: "Updates · Home Soda Machine",
      pageStyles: PAGE_STYLES,
    }) +
    renderNav({ surface: "public", active: "updates" }) +
    body +
    renderFooter()
  );
}

export function mountBlogRoutes(app, { postsDir }) {
  app.get("/blog", (_req, res) => {
    const posts = loadPosts(postsDir);
    res.set("Content-Type", "text/html; charset=utf-8");
    // Without an explicit Cache-Control, iOS Safari (especially in PWA
    // standalone) applies heuristic caching and can serve a stale page
    // when the SW navigates an existing window here on a notification
    // tap — user gets the Updates feed but missing today's post.
    // `no-cache` forces revalidation against the server's ETag every
    // visit; 304 when nothing's changed, fresh body when it has.
    res.set("Cache-Control", "no-cache");
    res.send(renderPage(posts));
  });

  // Pagination endpoint for the infinite scroll. Returns the next slice of
  // posts already rendered to HTML (so the client never needs a markdown
  // parser) plus the cursor for the following request. Posts are re-read
  // each call — same "read at request time" stance as /blog; the count is
  // small. no-cache for the same iOS-PWA staleness reason as the page.
  app.get("/blog/posts", (req, res) => {
    const posts = loadPosts(postsDir);
    let offset = parseInt(req.query.offset, 10);
    if (!Number.isFinite(offset) || offset < 0) offset = 0;
    const slice = posts.slice(offset, offset + PAGE_SIZE);
    const nextOffset = offset + slice.length;
    res.set("Cache-Control", "no-cache");
    res.json({
      html: slice.map(renderArticle).join("\n"),
      nextOffset,
      hasMore: nextOffset < posts.length,
    });
  });
}
