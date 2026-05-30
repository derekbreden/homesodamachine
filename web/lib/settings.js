// Settings page — reachable via the gear in the top-right of every nav.
//
// Three rows, all rendered with the .ios-toggle pill from shell.js:
//   1. Dev mode — always visible. Toggling on adds Parts / Charts to
//      the public nav (sets html.dev-mode + persists in localStorage).
//      No async work; the slide is instant.
//   2. Notifications — only visible inside the installed PWA, since iOS
//      web push only works in standalone mode and the toggle is inert
//      otherwise. Same FCM-backed flow as before: first-time enable shows
//      a warning modal, requests permission, registers the SW, gets a
//      token, POSTs files=["*"] so any STEP change pushes; turning off
//      DELETEs the subscription.
//   3. Live-reload debug — only visible when dev mode is on. Flips the
//      on-screen panel boot.js renders (socket health, build commit,
//      deploy events) via window.__hsmLiveDebug + localStorage.
//   4. Lite edition — only visible when dev mode is on. Switches the
//      viewer's content root from hardware/ (kitchen, default) to
//      pie-in-the-sky/lite/. Stored in localStorage and mirrored to the
//      hsmEdition cookie (shell.js), which the server reads per request.

import { renderHead, renderNav, renderFooter } from "./shell.js";

const PAGE_STYLES = `
.wrap {
  flex: 1;
  width: 100%;
  max-width: 36rem;
  margin: 0 auto;
  /* Safe-area on sides (iPhone landscape) and bottom (PWA home indicator).
     Top doesn't need it — the sticky nav above eats safe-area-top. */
  padding:
    2rem
    calc(env(safe-area-inset-right, 0px) + 1.25rem)
    calc(env(safe-area-inset-bottom, 0px) + 4rem)
    calc(env(safe-area-inset-left, 0px) + 1.25rem);
}
header.page { margin-bottom: 1.5rem; }
h1 {
  font-size: clamp(1.5rem, 4vw, 2rem);
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.02em;
}
.modal-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  z-index: 1000;
  align-items: center;
  justify-content: center;
  /* Safe-area inset so the modal stays clear of the iPhone dynamic island
     and home indicator in PWA standalone mode. The 16px gutter adds to the
     inset rather than replacing it (so desktop still gets 16px). Same
     pattern as .cv-dialog in content-viewer.js. */
  padding:
    calc(env(safe-area-inset-top, 0px) + 16px)
    calc(env(safe-area-inset-right, 0px) + 16px)
    calc(env(safe-area-inset-bottom, 0px) + 16px)
    calc(env(safe-area-inset-left, 0px) + 16px);
}
.modal-backdrop.open { display: flex; }
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  max-width: 420px;
  width: 100%;
  padding: 20px;
  color: var(--text);
}
.modal h2 { font-size: 17px; font-weight: 600; margin-bottom: 12px; color: var(--text); }
.modal p { font-size: 14px; line-height: 1.5; margin-bottom: 10px; color: var(--text-2); }
.modal p em { font-style: normal; color: var(--text); font-weight: 600; }
.modal .actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
.modal button {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text);
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}
.modal button:hover { background: var(--border); }
.modal button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
.modal button.primary:hover { background: #5599ff; border-color: #5599ff; }
`;

const BODY = `<div class="wrap">
  <header class="page"><h1>Settings</h1></header>

  <div class="settings-card">
    <div class="setting-row" id="row-devmode">
      <div>
        <div class="setting-label">Dev mode</div>
        <div class="setting-help">Show Prints and Diagrams in the navigation.</div>
      </div>
      <button id="devmode-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Dev mode"></button>
    </div>

    <div class="setting-row" id="row-notifs" hidden>
      <div>
        <div class="setting-label">Notifications</div>
        <div class="setting-help">Push when STEP files or posts change.</div>
      </div>
      <button id="notifs-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Notifications">
        <span class="ios-toggle-spinner"></span>
      </button>
    </div>

    <div class="setting-row" id="row-livedebug" hidden>
      <div>
        <div class="setting-label">Live-reload debug</div>
        <div class="setting-help">On-screen panel: socket health, build commit, deploy events.</div>
      </div>
      <button id="livedebug-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Live-reload debug"></button>
    </div>

    <div class="setting-row" id="row-edition" hidden>
      <div>
        <div class="setting-label">Lite edition</div>
        <div class="setting-help">Show pie-in-the-sky/lite content instead of hardware.</div>
      </div>
      <button id="edition-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Lite edition"></button>
    </div>
  </div>
</div>

<div id="subscribe-modal" class="modal-backdrop" role="dialog" aria-modal="true">
  <div class="modal">
    <h2>Notify on every update?</h2>
    <p>This will notify on <em>every</em> update, and there are times when this happens several times an hour.</p>
    <div class="actions">
      <button id="subscribe-cancel" type="button">Cancel</button>
      <button id="subscribe-confirm" type="button" class="primary">Subscribe</button>
    </div>
  </div>
</div>

<script src="/settings.js" defer></script>
`;

export function mountSettingsRoutes(app, { surface = "public" } = {}) {
  app.get("/settings", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({
        title: "Settings · Home Soda Machine",
        pageStyles: PAGE_STYLES,
      }) +
      renderNav({ surface, active: "settings" }) +
      BODY +
      renderFooter(),
    );
  });
}
