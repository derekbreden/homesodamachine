// Shared HTML shell for every server-rendered page (landing, blog, parts
// viewer, charts viewer, settings). One source of truth for:
//   - <head> meta tags, font loading, manifest, icons, theme color
//   - The :root CSS variables (palette tokens shared with the iOS / Android
//     apps and the S3 device — same hex values as Theme.swift / Theme.kt)
//   - body base styles (font, background)
//   - The top nav, including the gear that links to /settings
//   - Dev-mode flag: html.dev-mode reveals Parts / Charts in the
//     public nav; flag is persisted in localStorage and applied by an
//     inline head script before first paint to avoid a flash.
//   - The .ios-toggle pill primitive (shared between /settings rows and
//     anywhere else that wants the same delightful slide).
//
// Two surfaces:
//   "public" — civilian: Home, Updates [+ Parts, Charts when dev mode], Settings
//   "dev"    — engineering: Home, Updates, Parts, Charts, Settings (always)
//
// Render flow:
//   res.send(renderHead({title, ...}) + renderNav({surface, active}) +
//            <body content> + renderFooter());

import { PARTS_SVG, CHARTS_SVG, DRAWINGS_SVG, GEAR_SVG, BELL_SVG } from "./icons.js";

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
.site-nav a.nav-icon {
  padding: 0.125rem 0;
  position: relative;
}
.site-nav a.nav-icon svg {
  width: 1.125rem;
  height: 1.125rem;
  display: block;
}
/* Right cluster (bell + gear). One container with margin-left: auto
   pushes them both to the right edge as a unit; two icons each with
   their own margin-left: auto would split the available space and
   leave a big gap between them. */
.site-nav .nav-right {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 1.25rem;
}
.site-nav .nav-bell {
  display: none; /* shown only when html.notifs-enabled */
}
html.notifs-enabled .site-nav .nav-bell { display: inline-flex; }
.site-nav .nav-bell.has-unread::after {
  content: "";
  position: absolute;
  top: -1px;
  right: -3px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid var(--bg);
  box-sizing: content-box;
}

/* Public nav hides Parts / Charts / Drawings unless html.dev-mode is set.
   The dev surface (.site-nav-dev) always shows them. */
.site-nav-public a[data-nav="parts"],
.site-nav-public a[data-nav="charts"],
.site-nav-public a[data-nav="drawings"] {
  display: none;
}
html.dev-mode .site-nav-public a[data-nav="parts"],
html.dev-mode .site-nav-public a[data-nav="charts"],
html.dev-mode .site-nav-public a[data-nav="drawings"] {
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
/* In-app toast for foreground push notifications. Bottom-anchored, fixed,
   sits above any modal in the app. The HEAD_TAGS script appends a single
   .hsm-toast to body when an SSE pending-nav event arrives for a URL
   different from the current one (same-URL events trigger a reload
   instead — see HEAD_TAGS). */
.hsm-toast {
  position: fixed;
  left: max(12px, env(safe-area-inset-left, 0px));
  right: max(12px, env(safe-area-inset-right, 0px));
  bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  margin: 0 auto;
  max-width: 600px;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  /* 2147483647 = max signed 32-bit int — guaranteed above any user-supplied
     z-index in the app, including modals. */
  z-index: 2147483647;
  font-size: 14px;
  animation: hsm-toast-in 200ms ease-out;
}
.hsm-toast-link {
  flex: 1;
  min-width: 0;
  text-decoration: none;
  color: inherit;
  display: block;
}
.hsm-toast-title { font-weight: 600; margin-bottom: 2px; }
.hsm-toast-body {
  color: var(--text-2);
  font-size: 12px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.hsm-toast-close {
  background: none;
  border: 0;
  color: var(--text-2);
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  line-height: 1;
  flex-shrink: 0;
}
.hsm-toast-close:hover { color: var(--text); }
@keyframes hsm-toast-in {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
`;

// HEAD_TAGS — runs on every page via renderHead below.
//
// Synchronous flicker-prevention only: the localStorage class flips for
// dev-mode and notifs-enabled have to land before first paint, so they
// stay inline. The Edition choice (kitchen/lite) is mirrored here too:
// localStorage is the source of truth, but the server picks the viewer's
// content root from the `hsmEdition` cookie, so we write that cookie before
// the viewer's main.js fires its /api fetches. Everything else (SW navigate
// bridge, notifications state, SSE owner, toast) lives in public/boot.js
// loaded with defer — see that file's docstring for the full architecture.
const HEAD_TAGS = `<script>(function(){try{if(localStorage.getItem("devMode")==="1")document.documentElement.classList.add("dev-mode");if(localStorage.getItem("hsmFcmToken"))document.documentElement.classList.add("notifs-enabled");var ed=localStorage.getItem("hsmEdition")==="lite"?"lite":"kitchen";document.cookie="hsmEdition="+ed+";path=/;max-age=31536000;samesite=lax";if(ed==="lite")document.documentElement.classList.add("lite-mode");}catch(e){}})();</script>
<script src="/boot.js" defer></script>
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

// Nav glyphs — shared with the notifications page via lib/icons.js so
// kind=step / kind=mermaid rows in /notifications use the same cube and
// bar-chart icons as the Parts / Charts nav items.

// Layout: text labels (Home, Updates) on the left, then icon-only links
// (Parts, Charts) — they're icons rather than text so the nav fits a
// phone PWA viewport without overflow. The right cluster (bell + gear)
// is wrapped in .nav-right with margin-left: auto, so a single auto
// margin pushes both icons to the right edge as a unit (two siblings
// each with margin-left: auto would split the available space and leave
// a big gap between them).
//
// On the public surface, Parts / Charts are present in the markup but
// hidden by CSS unless html.dev-mode is set (see BASE_CSS). On the dev
// surface, they're always visible.
export function renderNav({ surface = "public", active = null }) {
  const textLinks = [
    { href: "/", name: "home", label: "Home" },
    { href: "/blog", name: "updates", label: "Updates" },
  ];
  const iconLinks = [
    { href: "/3d", name: "parts", label: "Parts", svg: PARTS_SVG },
    { href: "/charts", name: "charts", label: "Charts", svg: CHARTS_SVG },
    { href: "/drawings", name: "drawings", label: "Drawings", svg: DRAWINGS_SVG },
  ];
  const textItems = textLinks
    .map((l) => {
      const cls = l.name === active ? ' class="active"' : "";
      return `  <a href="${l.href}"${cls} data-nav="${l.name}">${escape(l.label)}</a>`;
    })
    .join("\n");
  const iconItems = iconLinks
    .map((l) => {
      const activeCls = l.name === active ? " active" : "";
      return `  <a href="${l.href}" class="nav-icon${activeCls}" data-nav="${l.name}" aria-label="${escape(l.label)}">${l.svg}</a>`;
    })
    .join("\n");
  const surfaceCls = surface === "dev" ? "site-nav-dev" : "site-nav-public";
  const gearActive = active === "settings" ? " active" : "";
  const bellActive = active === "notifications" ? " active" : "";
  return `<nav class="site-nav ${surfaceCls}" id="site-nav" aria-label="Primary">
${textItems}
${iconItems}
  <div class="nav-right">
    <a href="/notifications" class="nav-icon nav-bell${bellActive}" data-nav="notifications" aria-label="Notifications">${BELL_SVG}</a>
    <a href="/settings" class="nav-icon nav-gear${gearActive}" data-nav="settings" aria-label="Settings">${GEAR_SVG}</a>
  </div>
</nav>
`;
}

export function renderFooter() {
  return `</body>
</html>
`;
}
