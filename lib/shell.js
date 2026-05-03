// Shared HTML shell for every server-rendered page (landing, blog, dev
// viewer, diagrams viewer). One source of truth for:
//   - <head> meta tags, font loading, manifest, icons, theme color
//   - The :root CSS variables (palette tokens shared with the iOS / Android
//     apps and the S3 device — same hex values as Theme.swift / Theme.kt)
//   - body base styles (font, background)
//   - The top nav (public surface vs dev surface)
//
// Two surfaces:
//   "public" — civilian: Home, Updates only
//   "dev"    — engineering: Home, Updates, Prints, Diagrams
//
// Render flow:
//   res.send(renderHead({title, ...}) + renderNav({surface, active}) +
//            <body content> + renderFooter());

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
  --bg: #1a1a2e;
  --surface: #232342;
  --surface-2: #2a2a4a;
  --border: #3a3a5a;
  --text: #ffffff;
  --text-2: #999999;
  --text-3: #595959;
  --accent: #4488ff;
  --ok: #5fb56f;
  --err: #d97070;
  --chart-pink: #e64c80;
  --chart-purple: #994ce6;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: "Montserrat", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
.site-nav {
  display: flex;
  gap: 1.5rem;
  padding:
    calc(env(safe-area-inset-top, 0px) + 0.625rem)
    calc(env(safe-area-inset-right, 0px) + 1.25rem)
    0.625rem
    calc(env(safe-area-inset-left, 0px) + 1.25rem);
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
}
.site-nav a:hover { color: var(--text); }
.site-nav a.active { color: var(--text); font-weight: 600; }

/* Subtle footer for public pages — the only way into /dev/ from the
   civilian surface. Low contrast, lowercase, easy to find if you're
   looking, easy to ignore if you're not. */
.site-footer {
  margin-top: auto;
  text-align: center;
  padding: 2rem 1rem calc(env(safe-area-inset-bottom, 0px) + 2rem);
  font-size: 0.75rem;
  letter-spacing: 0.05em;
}
.site-footer a {
  color: var(--text-3);
  text-decoration: none;
}
.site-footer a:hover { color: var(--text-2); }
`;

// Order matters: preconnect first, then stylesheet, then site assets so
// fonts start downloading as early as possible.
const HEAD_TAGS = `<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="/pwa-icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="/pwa-icons/favicon-64.png">
<link rel="apple-touch-icon" sizes="152x152" href="/pwa-icons/apple-touch-icon-152.png">
<link rel="apple-touch-icon" sizes="167x167" href="/pwa-icons/apple-touch-icon-167.png">
<link rel="apple-touch-icon" sizes="180x180" href="/pwa-icons/apple-touch-icon-180.png">
<link rel="apple-touch-icon" href="/pwa-icons/apple-touch-icon-180.png">
<meta name="theme-color" content="#1a1a2e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Home Soda Machine">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">`;

export function renderHead({ title, pageStyles = "", pageHead = "" }) {
  return `<!doctype html>
<html lang="en">
<head>
${HEAD_TAGS}
<title>${escape(title)}</title>
<style>${BASE_CSS}${pageStyles ? "\n" + pageStyles : ""}</style>
${pageHead}
</head>
<body>
`;
}

// devPrefix lets dev mode serve the viewer at root (prefix = "") while prod
// keeps it under /dev. The SPA's client-side JS replays the same logic to
// update active state on pushState — that's why each link carries a data-nav
// hook even though the shell-rendered version is already "correct" at first
// paint.
export function renderNav({ surface = "public", active = null, devPrefix = "/dev" }) {
  const links = [
    { href: "/", name: "home", label: "Home" },
    { href: "/blog", name: "updates", label: "Updates" },
  ];
  if (surface === "dev") {
    links.push({ href: devPrefix || "/", name: "prints", label: "Prints" });
    links.push({ href: (devPrefix || "") + "/diagrams", name: "diagrams", label: "Diagrams" });
  }
  const items = links
    .map((l) => {
      const cls = l.name === active ? ' class="active"' : "";
      return `  <a href="${l.href}"${cls} data-nav="${l.name}">${escape(l.label)}</a>`;
    })
    .join("\n");
  return `<nav class="site-nav" id="site-nav" aria-label="Primary">
${items}
</nav>
`;
}

// Subtle "dev" link on public pages. Hidden from the visible nav but
// reachable for anyone who scrolls to the bottom — and gives the maker a
// place to tap when demoing the dev viewer to someone in person.
export function renderPublicFooter() {
  return `<footer class="site-footer"><a href="/dev">dev</a></footer>
`;
}

export function renderFooter() {
  return `</body>
</html>
`;
}
