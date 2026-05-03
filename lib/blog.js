import path from "path";
import fs from "fs";
import matter from "gray-matter";
import { marked } from "marked";

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

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>Updates · Home Soda Machine</title>
    <link rel="icon" type="image/png" sizes="32x32" href="/dev/pwa-icons/favicon-32.png" />
    <link rel="icon" type="image/png" sizes="64x64" href="/dev/pwa-icons/favicon-64.png" />
    <meta name="theme-color" content="#1a1a2e" />
    <style>
      :root {
        color-scheme: dark;
        --bg: #1a1a2e;
        --surface: #232342;
        --border: #3a3a5a;
        --text: #ffffff;
        --text-2: #999999;
        --text-3: #595959;
        --accent: #4488ff;
      }
      * { box-sizing: border-box; }
      html, body { margin: 0; padding: 0; }
      body {
        background: var(--bg);
        color: var(--text);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 16px;
        line-height: 1.5;
        min-height: 100vh;
      }
      .wrap {
        max-width: 44rem;
        margin: 0 auto;
        padding: 2.5rem 1.5rem 4rem;
      }
      header.page {
        margin-bottom: 2.5rem;
      }
      h1 {
        font-size: clamp(1.5rem, 4vw, 2rem);
        font-weight: 600;
        margin: 0 0 0.5rem;
        letter-spacing: -0.02em;
        color: var(--text);
      }
      .home-link {
        font-size: 0.875rem;
        color: var(--text-2);
        text-decoration: none;
      }
      .home-link:hover { color: var(--text); }
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
        color: var(--text);
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
      .post-body {
        color: var(--text-2);
      }
      .post-body p { margin: 0 0 0.75rem; }
      .post-body p:last-child { margin-bottom: 0; }
      .post-body ul, .post-body ol {
        padding-left: 1.25rem;
        margin: 0 0 0.75rem;
      }
      .post-body ul ul, .post-body ol ol,
      .post-body ul ol, .post-body ol ul {
        margin: 0.25rem 0 0.25rem;
      }
      .post-body li { margin: 0.15rem 0; }
      .post-body li::marker { color: var(--text-3); }
      .post-body strong { color: var(--text); }
      .post-body code {
        background: var(--surface);
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
        font-size: 0.9em;
        color: var(--text);
      }
      .post-body pre {
        background: var(--surface);
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
      .empty {
        color: var(--text-3);
        text-align: center;
        padding: 4rem 0;
      }
    </style>
  </head>
  <body>
    <div class="wrap">
      <header class="page">
        <h1>Updates</h1>
        <a class="home-link" href="/">Home</a>
      </header>
${posts.length === 0 ? `      <p class="empty">No posts yet.</p>` : articles}
    </div>
  </body>
</html>
`;
}

export function mountBlogRoutes(app, { postsDir }) {
  app.get("/blog", (_req, res) => {
    const posts = loadPosts(postsDir);
    res.set("Content-Type", "text/html; charset=utf-8");
    res.send(renderPage(posts));
  });
}
