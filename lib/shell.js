// Shared HTML shell for every server-rendered page (landing, blog, dev
// viewer, diagrams viewer, settings). One source of truth for:
//   - <head> meta tags, font loading, manifest, icons, theme color
//   - The :root CSS variables (palette tokens shared with the iOS / Android
//     apps and the S3 device — same hex values as Theme.swift / Theme.kt)
//   - body base styles (font, background)
//   - The top nav, including the gear that links to /settings
//   - Dev-mode flag: html.dev-mode reveals Prints / Diagrams in the
//     public nav; flag is persisted in localStorage and applied by an
//     inline head script before first paint to avoid a flash.
//   - The .ios-toggle pill primitive (shared between /settings rows and
//     anywhere else that wants the same delightful slide).
//
// Two surfaces:
//   "public" — civilian: Home, Updates [+ Prints, Diagrams when dev mode], Settings
//   "dev"    — engineering: Home, Updates, Prints, Diagrams, Settings (always)
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
.site-nav {
  display: flex;
  gap: 1.5rem;
  align-items: center;
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
  display: inline-flex;
  align-items: center;
}
.site-nav a:hover { color: var(--text); }
.site-nav a.active { color: var(--text); font-weight: 600; }
.site-nav a.nav-gear {
  margin-left: auto;
  padding: 0.125rem 0;
}
.site-nav a.nav-gear svg {
  width: 1.125rem;
  height: 1.125rem;
  display: block;
}
.site-nav a.nav-gear.active svg {
  /* match the active text color via stroke=currentColor */
}

/* Public nav hides Prints / Diagrams unless html.dev-mode is set. The
   dev surface (.site-nav-dev) always shows them. */
.site-nav-public a[data-nav="prints"],
.site-nav-public a[data-nav="diagrams"] {
  display: none;
}
html.dev-mode .site-nav-public a[data-nav="prints"],
html.dev-mode .site-nav-public a[data-nav="diagrams"] {
  display: inline-flex;
}

/* iOS-style pill toggle. Used on /settings (Dev mode + Notifications).
   .loading shows a centered spinner overlay on the knob without changing
   layout — the slide animation runs the moment .loading drops and .on
   goes on in the same frame. */
.ios-toggle {
  position: relative;
  width: 51px;
  height: 31px;
  border-radius: 31px;
  background: rgba(120,120,128,0.32);
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  padding: 0;
  flex-shrink: 0;
}
.ios-toggle::before {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 27px;
  height: 27px;
  background: #ffffff;
  border-radius: 50%;
  transition: transform 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.ios-toggle.on { background: var(--accent); }
.ios-toggle.on::before { transform: translateX(20px); }
.ios-toggle:disabled { cursor: default; }
.ios-toggle .ios-toggle-spinner {
  position: absolute;
  top: 8px;
  left: 8px;
  width: 15px;
  height: 15px;
  border: 2px solid rgba(80,80,90,0.35);
  border-top-color: var(--accent);
  border-radius: 50%;
  display: none;
  animation: ios-toggle-spin 0.7s linear infinite;
  pointer-events: none;
  box-sizing: border-box;
}
.ios-toggle.loading .ios-toggle-spinner { display: block; }
@keyframes ios-toggle-spin { to { transform: rotate(360deg); } }

/* Settings card — used on /settings and anywhere else that wants iOS-y
   grouped rows. */
.settings-card {
  background: var(--surface);
  border-radius: 8px;
  overflow: hidden;
}
.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
}
.setting-row:last-child { border-bottom: none; }
.setting-row[hidden] { display: none; }
.setting-label { font-size: 14px; color: var(--text); }
.setting-help {
  font-size: 12px;
  color: var(--text-2);
  margin-top: 2px;
}
`;

// Order matters: dev-mode head script first (sets html class before paint
// so the public nav doesn't flash dev links). Then preconnect, fonts, and
// site assets. Fonts start downloading as early as possible.
const HEAD_TAGS = `<script>(function(){try{if(localStorage.getItem("devMode")==="1")document.documentElement.classList.add("dev-mode");}catch(e){}})();</script>
<meta charset="utf-8">
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

const GEAR_SVG = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>`;

// devPrefix lets dev mode serve the viewer at root (prefix = "") while prod
// keeps it under /dev. The SPA's client-side JS replays the same logic to
// update active state on pushState — that's why each link carries a data-nav
// hook even though the shell-rendered version is already "correct" at first
// paint.
//
// On the public surface, Prints / Diagrams are present in the markup but
// hidden by CSS unless html.dev-mode is set (see BASE_CSS). On the dev
// surface, they're always visible.
export function renderNav({ surface = "public", active = null, devPrefix = "/dev" }) {
  const prints = devPrefix || "/";
  const diagrams = (devPrefix || "") + "/diagrams";
  const links = [
    { href: "/", name: "home", label: "Home" },
    { href: "/blog", name: "updates", label: "Updates" },
    { href: prints, name: "prints", label: "Prints" },
    { href: diagrams, name: "diagrams", label: "Diagrams" },
  ];
  const items = links
    .map((l) => {
      const cls = l.name === active ? ' class="active"' : "";
      return `  <a href="${l.href}"${cls} data-nav="${l.name}">${escape(l.label)}</a>`;
    })
    .join("\n");
  const surfaceCls = surface === "dev" ? "site-nav-dev" : "site-nav-public";
  const gearActive = active === "settings" ? " active" : "";
  return `<nav class="site-nav ${surfaceCls}" id="site-nav" aria-label="Primary">
${items}
  <a href="/settings" class="nav-gear${gearActive}" data-nav="settings" aria-label="Settings">${GEAR_SVG}</a>
</nav>
`;
}

export function renderFooter() {
  return `</body>
</html>
`;
}
