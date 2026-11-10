// Settings page — reachable via the gear in the top-right of every nav.
//
// Two rows, both rendered with the .ios-toggle pill from shell.js:
//   1. Notifications — only visible inside the installed PWA, since iOS
//      web push only works in standalone mode and the toggle is inert
//      otherwise. First-time enable shows a warning modal, requests
//      permission, registers the SW, gets a token, POSTs files=["*"] so
//      any STEP change pushes; turning off DELETEs the subscription.
//   2. Live-reload debug — flips the on-screen panel boot.js renders
//      (socket health, build commit, deploy events) via
//      window.__hsmLiveDebug + localStorage.
//
// Below the card, the Checks section: every check in the tree and what it
// answered, out of the verdict this deploy carries. It is what the gear's dot
// is the summary of — shell.js colours that dot, this page names the rows.
//
// Below the checks, the Build time section: how long each full build took,
// newest first, out of `public/build-times.json` (`hsm-build-times`).
// Both are read per request, since artifacts-live.js carries both files onto
// the running container.

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { renderHead, renderNav, renderPageHeader, renderFooter, renderChecksRows } from "./shell.js";

const BUILD_TIMES_FILE = path.join(path.dirname(fileURLToPath(import.meta.url)), "..", "public", "build-times.json");
const BUILDS_SHOWN = 12;
const ZONE = "America/Chicago";

function readBuildTimes() {
  try {
    const value = JSON.parse(fs.readFileSync(BUILD_TIMES_FILE, "utf-8"));
    return Array.isArray(value.builds) ? value.builds : null;
  } catch {
    return null;
  }
}

function escape(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function duration(seconds) {
  const s = Math.round(seconds);
  const m = Math.floor(s / 60);
  return m ? `${m} min ${String(s % 60).padStart(2, "0")} s` : `${s} s`;
}

function when(iso) {
  return new Date(iso).toLocaleString("en-US", {
    timeZone: ZONE, month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });
}

function renderBuildTimeRows() {
  const builds = readBuildTimes();
  if (!builds?.length) {
    return `    <div class="setting-row">
      <div><div class="setting-help">No full build is recorded yet.</div></div>
    </div>`;
  }
  return builds
    .slice(-BUILDS_SHOWN)
    .reverse()
    .map((b) => {
      const reran = b.steps ? `reran ${b.reran} of ${b.steps} steps` : `reran ${b.reran} steps`;
      const help = [when(b.started), reran, b.commit].filter(Boolean).join(" · ");
      const label = b.finished ? duration(b.seconds) : `Failed after ${duration(b.seconds)}`;
      return `    <div class="setting-row">
      <div>
        <div class="setting-label${b.finished ? "" : " build-failed"}">${escape(label)}</div>
        <div class="setting-help">${escape(help)}</div>
      </div>
    </div>`;
    })
    .join("\n");
}

const PAGE_STYLES = `
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
/* The card's own 20px is the gutter on all four sides, so the first line
   starts at the top of it. */
.modal h2 { font-size: 17px; font-weight: 600; margin: 0 0 12px; color: var(--text); }
.modal p { font-size: 14px; line-height: 1.5; margin: 0 0 10px; color: var(--text-2); }
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
.modal button.primary { background: var(--action); border-color: var(--action); color: var(--on-action); }
.modal button.primary:hover { background: var(--action-hover); border-color: var(--action-hover); }
/* The checks the gear's dot is the summary of. A row per check, its own last
   line as the help text, and under a red one the lines it printed — which carry
   the command that repairs it, so it wraps rather than truncating. */
h2.section { font-size: 14px; font-weight: 600; margin: 2rem 0 0.75rem; color: var(--text-2); }
.checks-row { align-items: flex-start; }
.checks-mark { font-size: 14px; line-height: 1.5; padding-left: 12px; }
.checks-mark.ok { color: var(--ok); }
.checks-mark.red { color: var(--err); }
.setting-label.build-failed { color: var(--err); }
.checks-detail {
  margin-top: 6px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 11px;
  line-height: 1.5;
  color: var(--text);
  overflow-wrap: anywhere;
}
`;

const body = () => `<main class="settings-wrap site-content">
  <div class="settings-card">
    <div class="setting-row" id="row-notifs" hidden>
      <div>
        <div class="setting-label">Notifications</div>
        <div class="setting-help">Push when STEP files or posts change.</div>
      </div>
      <button id="notifs-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Notifications">
        <span class="ios-toggle-spinner"></span>
      </button>
    </div>

    <div class="setting-row" id="row-livedebug">
      <div>
        <div class="setting-label">Live-reload debug</div>
        <div class="setting-help">On-screen panel: socket health, build commit, deploy events.</div>
      </div>
      <button id="livedebug-toggle" class="ios-toggle" type="button" role="switch" aria-checked="false" aria-label="Live-reload debug"></button>
    </div>

  </div>

  <h2 class="section">Checks</h2>
  <div class="settings-card">
${renderChecksRows()}
  </div>

  <h2 class="section">Build time</h2>
  <div class="settings-card">
${renderBuildTimeRows()}
  </div>
</main>

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

export function mountSettingsRoutes(app) {
  app.get("/settings", (_req, res) => {
    res.set("Content-Type", "text/html; charset=utf-8");
    res.set("Cache-Control", "no-cache");
    res.send(
      renderHead({
        title: "Settings · Home Soda Machine",
        pageStyles: PAGE_STYLES,
        pageClass: "site-interior",
      }) +
      renderNav({ active: "settings" }) +
      renderPageHeader({ eyebrow: "Settings", title: "Stay connected.", description: "Choose how you follow the build, and see the project’s latest check results and build times." }) +
      body() +
      renderFooter({ siteFooter: true }),
    );
  });
}
