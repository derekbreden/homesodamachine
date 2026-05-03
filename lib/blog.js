import path from "path";
import fs from "fs";
import matter from "gray-matter";
import { marked } from "marked";
import { renderHead, renderNav, renderFooter } from "./shell.js";

// Render the blog index page from markdown files in `postsDir`.
// Posts are read at request time (count is small, grows slowly), parsed for
// YAML frontmatter, sorted by `date` descending, and concatenated into a
// single page. Malformed posts are skipped with a warning so one bad file
// can't take down the page.

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

function loadPosts(postsDir) {
  if (!fs.existsSync(postsDir)) return [];
  const entries = fs.readdirSync(postsDir, { withFileTypes: true });
  const posts = [];
  for (const entry of entries) {
    if (!entry.isFile() || !entry.name.endsWith(".md")) continue;
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
`;

function renderPage(posts) {
  const articles = posts
    .map((p) => {
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
    })
    .join("\n");

  const body = `<div class="wrap">
  <header class="page"><h1>Updates</h1></header>
${posts.length === 0 ? `  <p class="empty">No posts yet.</p>` : articles}
</div>
<script src="/pan-zoom.js"></script>
<script src="/content-viewer.js"></script>
<script>
(function () {
  // Tap-to-zoom: every <img> inside .post-body opens in ContentViewer with
  // pan + pinch-zoom. The image inside the modal is a clone so the
  // unmodified original stays in the post flow.
  for (const img of document.querySelectorAll(".post-body img")) {
    img.style.cursor = "zoom-in";
    img.addEventListener("click", function () {
      const cloned = img.cloneNode(true);
      cloned.style.maxWidth = "none";
      cloned.style.maxHeight = "none";
      cloned.style.width = "auto";
      cloned.style.height = "auto";
      cloned.style.display = "block";
      cloned.style.margin = "0";
      cloned.style.borderRadius = "0";
      cloned.draggable = false;
      const wrapper = document.createElement("div");
      wrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
      wrapper.appendChild(cloned);
      const pz = PanZoom.wrap(cloned, { container: wrapper, initialFit: true });
      ContentViewer.open({
        content: wrapper,
        filename: img.alt || undefined,
        onClose: function () { pz.destroy(); },
      });
    });
  }
})();
</script>
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
    res.send(renderPage(posts));
  });
}
