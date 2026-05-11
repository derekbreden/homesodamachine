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

import { PARTS_SVG, CHARTS_SVG, GEAR_SVG, BELL_SVG } from "./icons.js";

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

/* Public nav hides Parts / Charts unless html.dev-mode is set. The
   dev surface (.site-nav-dev) always shows them. */
.site-nav-public a[data-nav="parts"],
.site-nav-public a[data-nav="charts"] {
  display: none;
}
html.dev-mode .site-nav-public a[data-nav="parts"],
html.dev-mode .site-nav-public a[data-nav="charts"] {
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

// Order matters: dev-mode head script first (sets html class before paint
// so the public nav doesn't flash dev links). Then the SW navigate bridge
// (so a deploy can postMessage open clients to reload onto new HEAD_TAGS).
// Then notifications-enabled gate (so .nav-bell un-hides without flash).
// Then the SSE owner + notifications state. Then preconnect/fonts/assets.
const HEAD_TAGS = `<script>(function(){try{if(localStorage.getItem("devMode")==="1")document.documentElement.classList.add("dev-mode");if(localStorage.getItem("hsmFcmToken"))document.documentElement.classList.add("notifs-enabled");}catch(e){}})();</script>
<script>
// SW → page navigate bridge. The SW posts {type:"navigate", url} in two
// situations:
//   - On activate, with url=client.url, to force open pages to reload
//     onto new HEAD_TAGS after a deploy (firebase-messaging-compat
//     handles its own message types separately).
//   - For chrome desktop / Android PWA, the SW's notificationclick path
//     also posts this so the page does location.replace; iOS PWA never
//     reaches that path but the listener is harmless on iOS.
//
// Three cases for the url:
//   - identical to current → reload (refresh content).
//   - same pathname+search, different hash → set hash, reload.
//   - different pathname/search → location.replace().
(function(){if(!("serviceWorker" in navigator))return;navigator.serviceWorker.addEventListener("message",function(e){if(!(e.data&&e.data.type==="navigate"&&e.data.url))return;try{var u=new URL(e.data.url,window.location.origin);if(u.href===window.location.href){window.location.reload();}else if(u.pathname===window.location.pathname&&u.search===window.location.search){window.location.hash=u.hash;window.location.reload();}else{window.location.replace(u.href);}}catch(err){window.location.href=e.data.url;}});})();
// Notifications state + bell + toast + warm-tap auto-redirect.
//
// The server-side notifications inbox (lib/notifications.js) is the
// single source of truth: GET /api/notifications returns the user's
// list (token-keyed, 7-day window, with seen state). We refetch on:
//   - initial page load
//   - window.focus / pageshow / visibilitychange-to-visible (covers
//     iOS PWA warm-tap, since that's the only event iOS fires on
//     tap-to-foreground)
//   - any SSE message from /api/events (real-time push received)
//
// State drives three things on the page:
//   1. .has-unread class on .nav-bell (and the accent dot via CSS).
//   2. The bottom toast: 0 unread → none; 1 → kind-specific (title/
//      body from the row, tap = navigate, ✕ = mark seen); 2+ →
//      aggregate ("N unread", body = first 3 titles, tap →
//      /notifications, ✕ = mark all seen).
//   3. Warm-tap auto-redirect: if a focus/pageshow event activates
//      the page and exactly one row is unread, navigate to it (mark
//      seen). 2+ unread → no auto-redirect; the aggregate toast lets
//      the user pick on /notifications.
//
// Cold-launch (?n=<id> in the URL): iOS opens the PWA at the FCM
// link directly, so the page is already on the target. We mark
// that one row seen on load. URL stays as-is (no shared/bookmarked
// URLs in the PWA context).
(function(){
  // ----- Helpers -----
  function getToken(){
    try { return localStorage.getItem("hsmFcmToken") || ""; } catch (e) { return ""; }
  }

  function postSeen(payload){
    var url="/api/notifications/seen";
    var body=JSON.stringify(payload);
    try{
      if(navigator.sendBeacon){
        navigator.sendBeacon(url,new Blob([body],{type:"application/json"}));
        return Promise.resolve();
      }
    }catch(e){}
    return fetch(url,{method:"POST",headers:{"Content-Type":"application/json"},body:body,keepalive:true}).catch(function(){});
  }

  // Local state mirror of the server's unread set. We update it
  // optimistically on mark-seen actions so the UI updates instantly,
  // and reconcile via fetchNotifications on the next refetch.
  window.__hsm = window.__hsm || { items: [], unread: 0 };

  function recompute(){
    var unread=0;
    for(var i=0;i<window.__hsm.items.length;i++){
      if(!window.__hsm.items[i].seen)unread++;
    }
    window.__hsm.unread=unread;
    document.documentElement.classList.toggle("notifs-enabled",!!getToken());
    var bell=document.querySelector(".nav-bell");
    if(bell)bell.classList.toggle("has-unread",unread>0);
    window.dispatchEvent(new CustomEvent("hsm:notifications-updated"));
  }

  function fetchNotifications(){
    var t=getToken();
    if(!t){window.__hsm.items=[];recompute();return Promise.resolve();}
    return fetch("/api/notifications?token="+encodeURIComponent(t))
      .then(function(r){return r.ok?r.json():null;})
      .then(function(d){
        window.__hsm.items=(d&&d.items)||[];
        recompute();
      })
      .catch(function(){});
  }

  function markSeenLocal(ids){
    var idSet={};for(var i=0;i<ids.length;i++)idSet[String(ids[i])]=true;
    for(var j=0;j<window.__hsm.items.length;j++){
      if(idSet[String(window.__hsm.items[j].id)])window.__hsm.items[j].seen=true;
    }
    recompute();
  }
  function markAllSeenLocal(){
    for(var j=0;j<window.__hsm.items.length;j++)window.__hsm.items[j].seen=true;
    recompute();
  }
  function markSeen(ids){
    markSeenLocal(ids);
    return postSeen({token:getToken(),ids:ids});
  }
  function markAllSeen(){
    markAllSeenLocal();
    return postSeen({token:getToken(),all:true});
  }

  // ----- Toast -----
  function dismissToast(){var t=document.querySelector(".hsm-toast");if(t)t.remove();}
  function showToast(opts){
    dismissToast();
    var place=function(){
      var toast=document.createElement("div");
      toast.className="hsm-toast";
      toast.setAttribute("role","status");
      toast.setAttribute("aria-live","polite");
      var link=document.createElement("a");
      link.className="hsm-toast-link";
      link.href=opts.url;
      if(opts.onTap)link.addEventListener("click",opts.onTap);
      var t=document.createElement("div");t.className="hsm-toast-title";t.textContent=opts.title;
      var b=document.createElement("div");b.className="hsm-toast-body";b.textContent=opts.body||"";
      link.appendChild(t);link.appendChild(b);
      var close=document.createElement("button");
      close.className="hsm-toast-close";close.setAttribute("aria-label","Dismiss");close.textContent="✕";
      close.addEventListener("click",function(e){
        e.preventDefault();e.stopPropagation();
        if(opts.onDismiss)opts.onDismiss();
        toast.remove();
      });
      toast.appendChild(link);toast.appendChild(close);
      document.body.appendChild(toast);
    };
    if(document.body)place();
    else document.addEventListener("DOMContentLoaded",place,{once:true});
  }

  // Re-render toast based on current state. Called on every state
  // update (notifications-updated event). Idempotent: same state →
  // same toast (replaced, not duplicated).
  function renderToast(){
    var s=window.__hsm;
    var unread=[];
    for(var i=0;i<s.items.length;i++){if(!s.items[i].seen)unread.push(s.items[i]);}
    if(unread.length===0){dismissToast();return;}
    if(unread.length===1){
      var n=unread[0];
      showToast({
        title:n.title,
        body:n.body,
        url:n.url,
        onTap:function(){ markSeen([n.id]); },
        onDismiss:function(){ markSeen([n.id]); }
      });
    }else{
      var head=unread.slice(0,3).map(function(n){return n.title;}).join(", ");
      var body=unread.length>3?head+", …":head;
      showToast({
        title:unread.length+" unread",
        body:body,
        url:"/notifications",
        onTap:null,
        onDismiss:function(){ markAllSeen(); }
      });
    }
  }
  window.addEventListener("hsm:notifications-updated",renderToast);

  // ----- Warm-tap auto-redirect -----
  // Only for "page just (re)gained focus" events, NOT for SSE-driven
  // refetches (during active use the user is in the middle of
  // something; toast is the right surface there). 1 unread → redirect
  // to that file. 2+ → leave it; the toast offers /notifications.
  function maybeAutoRedirect(){
    var s=window.__hsm;
    var unread=[];
    for(var i=0;i<s.items.length;i++){if(!s.items[i].seen)unread.push(s.items[i]);}
    if(unread.length!==1)return;
    var n=unread[0];
    try{
      var u=new URL(n.url,window.location.origin);
      if(u.href===window.location.href)return;
      // sendBeacon-flavored mark before navigating so the seen state
      // survives the unload.
      postSeen({token:getToken(),ids:[n.id]});
      window.location.replace(u.href);
    }catch(e){}
  }
  function refetchAndMaybeRedirect(){
    fetchNotifications().then(maybeAutoRedirect);
  }

  // ----- Cold-launch ?n=<id> mark-as-seen -----
  // iOS opens PWAs at the FCM link directly on cold launch, so when the
  // page boots and ?n=<id> is in the query, mark that one read. Server
  // is idempotent on already-seen rows so this is safe to call without
  // first checking state.
  (function(){
    try{
      var qs=new URLSearchParams(window.location.search);
      var nId=qs.get("n");
      if(nId&&/^\\d+$/.test(nId)&&getToken()){
        postSeen({token:getToken(),ids:[nId]});
      }
    }catch(e){}
  })();

  // ----- Initial fetch + activation hooks -----
  refetchAndMaybeRedirect();
  window.addEventListener("focus",refetchAndMaybeRedirect);
  window.addEventListener("pageshow",refetchAndMaybeRedirect);
  document.addEventListener("visibilitychange",function(){
    if(document.visibilityState==="visible")refetchAndMaybeRedirect();
  });

  // ----- SSE owner -----
  // Two roles:
  //   1. live-update bridge — dispatch hsm:files-changed + hsm:deploy
  //      DOM events for the dev viewer's per-file refresh logic.
  //   2. notifications signal — refetch /api/notifications on every
  //      message so the bell + toast track new pushes in real time.
  if("EventSource" in window){
    var es=new EventSource("/api/events");
    var seenCommit=null;
    var seenRecentCommit=null;
    es.addEventListener("message",function(ev){
      var msg;try{msg=JSON.parse(ev.data);}catch(e){return;}
      if(msg.type==="hello"){
        if(seenCommit===null){
          seenCommit=msg.commit;
          if(msg.recent&&msg.recent.commit)seenRecentCommit=msg.recent.commit;
          return;
        }
        if(msg.commit!==seenCommit){
          seenCommit=msg.commit;
          window.dispatchEvent(new CustomEvent("hsm:deploy",{detail:{commit:msg.commit}}));
        }
        if(msg.recent&&msg.recent.commit&&msg.recent.commit!==seenRecentCommit){
          seenRecentCommit=msg.recent.commit;
          if(msg.recent.files)window.dispatchEvent(new CustomEvent("hsm:files-changed",{detail:{files:msg.recent.files}}));
          if(msg.recent.posts)window.dispatchEvent(new CustomEvent("hsm:posts-changed",{detail:{posts:msg.recent.posts}}));
          fetchNotifications();
        }
        return;
      }
      if(msg.type==="files-changed"){
        window.dispatchEvent(new CustomEvent("hsm:files-changed",{detail:{files:msg.files||[]}}));
        fetchNotifications();
        return;
      }
      if(msg.type==="posts-changed"){
        window.dispatchEvent(new CustomEvent("hsm:posts-changed",{detail:{posts:msg.posts||[]}}));
        fetchNotifications();
      }
    });
  }
})();
</script>
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
