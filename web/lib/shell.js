// Shared page head, navigation, and theme.
import fs from "fs";
import path from "path";
import { createHash } from "crypto";
import { fileURLToPath } from "url";
import { PARTS_SVG, GUIDES_SVG, DOLLAR_SVG, LATEST_SVG } from "./icons.js";

const PUBLIC_DIR = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "public");

function escape(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

const BASE_CSS = `
:root {
  color-scheme: dark;
  --brand-blue: #1749d1;
  --brand-navy: #10319c;
  --brand-ice: #dce6ff;
  --brand-orange: #ff9152;
  --bg: var(--brand-navy);
  --surface: #1238aa;
  --surface-2: var(--brand-blue);
  --border: #6b8fe9;
  --text: #ffffff;
  --text-2: var(--brand-ice);
  --text-3: #b7caf8;
  --accent: var(--brand-ice);
  --action: var(--brand-orange);
  --on-action: var(--brand-navy);
  --action-hover: #ffa46f;
  --ok: #8ddca0;
  --err: #ffa3a3;
  --warn: #ffd28a;
  --chart-one: var(--brand-orange);
  --chart-two: var(--brand-ice);
  --chart-three: #94b8ff;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans, "Montserrat", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
  font-size: 16px;
  line-height: 1.5;
  /* 100vh on iOS Safari is the *large* viewport (URL bar retracted), so when
     the URL bar is visible the body is taller than the visible area and the
     page bounces vertically with nothing to scroll to. 100svh is the small
     viewport (URL-bar-visible size) — page fits exactly, no phantom scroll,
     no layout shift when the URL bar shows/hides. */
  min-height: 100vh;
  min-height: 100svh;
  display: flex;
  flex-direction: column;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
/* The bar's own inset stops at the safe area; the rest of it belongs to the
   links, which spend it as hit area (see .nav-icon). The gap closes as the bar
   narrows, so all nine icons land inside a phone's width (364px of a 375px
   bar) and the right cluster keeps its edge.

   iOS paints the status bar above in this bar's colour: Safari samples an
   opaque, full-width bar that is sticky or fixed at the top edge. A Home
   Screen app with nothing to sample there gets the system's top-edge blur,
   which reaches down across the icons. */
.site-nav {
  display: flex;
  gap: clamp(0.25rem, 2.2vw, 0.75rem);
  align-items: center;
  padding:
    env(safe-area-inset-top, 0px)
    calc(env(safe-area-inset-right, 0px) + 0.875rem)
    0
    calc(env(safe-area-inset-left, 0px) + 0.875rem);
  font-size: 0.875rem;
  line-height: 1.5;
  border-bottom: 1px solid var(--border);
  background: var(--bg);
  position: sticky;
  top: 0;
  z-index: 100;
}
.site-nav a {
  color: var(--text-2);
  text-decoration: none;
  letter-spacing: 0.01em;
  display: inline-flex;
  align-items: center;
  transition: color 0.15s;
}
.site-nav a:hover { color: var(--text); }
/* The page you are on, in the accent — the colour nothing else in the bar
   reaches, hover included. */
.site-nav a.active { color: var(--action); }
/* The link fills the bar's height and takes the gap's other half, so the tap
   lands on the icon rather than between two of them. */
.site-nav a.nav-icon {
  padding: 0.75rem 0.375rem;
  position: relative;
}
/* The link's box runs to the top edge of a sticky bar, so the ring is drawn
   inside it — outside, its top edge is off the window. */
.site-nav a.nav-icon:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: -4px;
  border-radius: 8px;
}
.site-nav a.nav-icon svg,
.site-nav a.nav-icon img {
  width: 1.125rem;
  height: 1.125rem;
  display: block;
}
.site-nav a[data-nav="home"] img { width: 1.7rem; height: 1.7rem; margin: -0.2875rem; }
.site-nav a[data-nav="home"].active::before {
  content: "";
  position: absolute;
  height: 3px;
  left: 0.375rem;
  right: 0.375rem;
  bottom: 0;
  border-radius: 3px;
  background: var(--action);
}
`;

// The artwork's own fingerprint, carried by every icon href below.
//
// Safari keys its favicon cache by page URL and keeps what it stored there for weeks —
// art replaced at an unchanged URL goes on being drawn from that cache long after the
// deploy that replaced it, and a page whose entry was written wrong keeps the wrong icon.
// New bytes are a new URL, so the cache has nothing to hold and re-resolves.
//
// The icons ship with the deploy, so read their fingerprint at startup.
const ICON_V = (() => {
  try {
    const bytes = fs.readFileSync(path.join(PUBLIC_DIR, "pwa-icons", "favicon-32.png"));
    return "?v=" + createHash("sha256").update(bytes).digest("hex").slice(0, 8);
  } catch {
    return "";
  }
})();

const HEAD_TAGS = `<script type="module" src="/boot.js"></script>
<script type="module" src="/js/site-search.js"></script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/pwa-icons/favicon-32.png${ICON_V}">
<link rel="icon" type="image/png" sizes="64x64" href="/pwa-icons/favicon-64.png${ICON_V}">
<link rel="apple-touch-icon" sizes="152x152" href="/pwa-icons/apple-touch-icon-152.png${ICON_V}">
<link rel="apple-touch-icon" sizes="167x167" href="/pwa-icons/apple-touch-icon-167.png${ICON_V}">
<link rel="apple-touch-icon" sizes="180x180" href="/pwa-icons/apple-touch-icon-180.png${ICON_V}">
<link rel="apple-touch-icon" href="/pwa-icons/apple-touch-icon-180.png${ICON_V}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Soda Machine">`;

export function renderHead({
  title, pageStyles = "", pageHead = "", importMap = null,
  pageClass = "",
  fontStylesheet = "https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap",
  themeColor = "#10319c",
}) {
  // A page's module map must be installed before the shared boot module resolves imports.
  const moduleMap = importMap
    ? `<script type="importmap">${JSON.stringify(importMap).replaceAll("<", "\\u003c")}</script>\n` : "";
  return `<!doctype html>
<html lang="en">
<head>
${moduleMap}${HEAD_TAGS}
<link rel="stylesheet" href="${escape(fontStylesheet)}">
<meta name="theme-color" content="${escape(themeColor)}">
<title>${escape(title)}</title>
<style>${BASE_CSS}${pageStyles ? "\n" + pageStyles : ""}</style>
${pageHead}
<link rel="stylesheet" href="/css/site.css">
</head>
<body${pageClass ? ` class="${escape(pageClass)}"` : ""}>
`;
}

export function renderNav({ active = null, searchQuery = "" } = {}) {
  const iconLinks = [
    { href: "/", name: "home", label: "Home", svg: '<img src="/brand/mark.svg" width="28" height="28" alt="" aria-hidden="true">' },
    // One item for both feeds: it opens the /latest hub, and reads as the page you are on from
    // anywhere in either feed.
    { href: "/latest", name: "latest", label: "Latest", svg: LATEST_SVG, also: ["updates", "changes"] },
    { href: "/parts", name: "parts", label: "Parts", svg: PARTS_SVG },
    { href: "/guides", name: "guides", label: "Guides", svg: GUIDES_SVG },
    { href: "/cost", name: "cost", label: "Cost", svg: DOLLAR_SVG },
  ];
  const iconItems = iconLinks
    .map((l) => {
      const here = l.name === active;
      const within = !here && Boolean(l.also?.includes(active));
      const activeCls = here || within ? " active" : "";
      const current = here ? ' aria-current="page"' : within ? ' aria-current="true"' : "";
      return `  <a href="${l.href}" class="nav-icon${activeCls}"${current} data-nav="${l.name}" aria-label="${escape(l.label)}">${l.svg}</a>`;
    })
    .join("\n");
  return `<nav class="site-nav" id="site-nav" aria-label="Primary">
${iconItems}
  <form id="site-search" class="nav-search" role="search" action="/parts">
    <button type="submit" aria-label="Search parts">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="10.75" cy="10.75" r="5.75"/><path d="m15 15 4.5 4.5"/></svg>
    </button>
    <input id="site-search-input" name="q" type="search" value="${escape(searchQuery)}" placeholder="Search parts" aria-label="Find a part or feature" aria-controls="site-search-results" autocomplete="off">
    <p id="site-search-status" class="nav-search-status" role="status"></p>
    <div id="site-search-results" class="nav-search-results" role="region" aria-label="Search results" hidden></div>
  </form>
</nav>
`;
}

export function renderPageHeader({ eyebrow, title, description = "" }) {
  return `<header class="site-page-header">
  <div class="site-masthead site-inner">
    <a class="site-brand" href="/" aria-label="Home Soda Machine home"><img src="/brand/wordmark-reverse.svg" width="1680" height="640" alt="Home Soda Machine"></a>
    <a class="site-project-link" href="/latest">Design &amp; development <span aria-hidden="true">↗</span></a>
  </div>
  <div class="site-page-intro site-inner">
    <p class="site-eyebrow">${escape(eyebrow)}</p>
    <h1>${escape(title)}</h1>
    ${description ? `<p class="site-lede">${escape(description)}</p>` : ""}
  </div>
</header>`;
}

export function renderFooter({ siteFooter = false } = {}) {
  return `${siteFooter ? `<footer class="site-footer">
  <div class="site-inner site-footer-inner">
    <a href="/" class="site-footer-brand"><img src="/brand/mark-blue.svg" width="36" height="36" alt=""><span>Home Soda Machine<small>A kitchen appliance in development.</small></span></a>
    <nav aria-label="Project"><a href="/latest">Follow the build</a><a href="/parts">Explore the design</a><a href="/cost">Parts &amp; costs</a></nav>
  </div>
</footer>` : ""}</body>
</html>
`;
}
