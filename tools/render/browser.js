// browser.js — one Chrome lifetime, shared by every tool here that renders
// through a headless browser.
//
// Chrome is a separate process, and an abandoned one does not idle: the
// viewer's compose step leaves a requestAnimationFrame loop redrawing the whole
// model at frame rate, so a browser nobody is reading still costs a core. That
// is what makes the leak compound. A killed render leaves its tree spinning;
// the next render finds a machine with less to give and takes longer; the
// caller's own timeout fires and SIGKILLs it, leaking another tree — until
// every render dies on `Page.captureScreenshot timed out` and the renderer
// looks broken on files nobody has touched, in and out of a sandbox.
//
// Three ties hold Chrome to the node process that launched it, because none of
// them covers the others' case. `pipe: true` puts the CDP transport on fd 3/4,
// so however node dies — SIGKILL included, which no handler can intercept and
// which is exactly what a timed-out `subprocess.run` sends — the pipes close
// and Chrome exits on EOF. The signal handlers below cover what is catchable,
// and they kill rather than close because a signal handler does not outlive the
// tick it runs in; puppeteer's own handling is off so it cannot race them with
// a CDP close. `closeBrowser` is the ordinary path.
//
// `sweepAbandonedBrowsers` is for the trees left behind before any of that was
// true. It runs at the top of a tool, so a machine already carrying a leak
// renders on the cores it should have had.

import { execFileSync } from "child_process";
import puppeteer from "puppeteer";

// Puppeteer's browser cache, read off the binary it would launch — so a moved
// PUPPETEER_CACHE_DIR names itself, and so do the builds beside the current one
// (an older version, chrome-headless-shell) that a leak can just as easily be.
// Chrome installed for a person lives elsewhere and never matches.
const BROWSER_ROOT = (() => {
  try {
    // …/<cache>/chrome/<build>/chrome-mac-arm64/… — the segment before `chrome`.
    const m = puppeteer.executablePath().match(/^(.*[/\\])chrome[/\\]/);
    if (m) return m[1];
  } catch { /* no browser installed — the sweep has nothing to find */ }
  return "/.cache/puppeteer/";
})();

// How long a STEP parse gets. This is a fact about the file's size and the
// machine — the enclosure assembly is a 20 MB STEP and occt-import-js runs it
// single-threaded on the page's own main thread — not a fact about the
// geometry, so it stands well past what a loaded laptop takes and
// `HSM_PARSE_TIMEOUT` moves it. It bounds the CDP protocol timeout in every
// tool that drives the viewer: while the parse holds the main thread, that
// round trip is what runs out first, and it fails naming the protocol instead
// of the file.
export const PARSE_TIMEOUT = Number(process.env.HSM_PARSE_TIMEOUT || 900000);

const LIVE_BROWSERS = new Set();

function killBrowserNow(browser) {
  const proc = browser.process();
  if (proc && proc.exitCode === null) {
    try { proc.kill("SIGKILL"); } catch { /* already gone */ }
  }
}

export async function closeBrowser(browser) {
  if (!browser) return;
  LIVE_BROWSERS.delete(browser);
  // close() negotiates over CDP, which a page still holding the main thread can
  // stall; the kill is what makes "the process is gone" true rather than likely.
  try { await browser.close(); } catch { /* fall through to the kill */ }
  killBrowserNow(browser);
}

for (const sig of ["SIGINT", "SIGTERM", "SIGHUP"]) {
  process.on(sig, () => {
    for (const b of LIVE_BROWSERS) killBrowserNow(b);
    LIVE_BROWSERS.clear();
    process.exit(sig === "SIGINT" ? 130 : sig === "SIGTERM" ? 143 : 129);
  });
}

// A render killed before any of that ran leaves its browser reparented to init.
// A live one never is — puppeteer's Chrome carries its node process as parent
// for as long as that process exists — so ppid 1 under puppeteer's own cache
// names a leak exactly, with no age threshold to trip over a slow peer render.
export function sweepAbandonedBrowsers(tool = "render") {
  let out;
  try {
    out = execFileSync("/bin/ps", ["-Ao", "pid=,ppid=,command="], { encoding: "utf8", maxBuffer: 1 << 24 });
  } catch { return; }
  const doomed = [];
  for (const line of out.split("\n")) {
    const m = line.match(/^\s*(\d+)\s+(\d+)\s+(.*)$/);
    if (!m) continue;
    const [, pid, ppid, cmd] = m;
    // The path is the whole test.
    if (ppid !== "1" || !cmd.includes(BROWSER_ROOT)) continue;
    doomed.push(Number(pid));
  }
  if (!doomed.length) return;
  // Killing a root orphans its renderers onto init, where this same rule finds
  // them; taking the whole set in one pass leaves nothing for a later sweep.
  const all = new Set(doomed);
  for (const line of out.split("\n")) {
    const m = line.match(/^\s*(\d+)\s+(\d+)\s+(.*)$/);
    if (m && all.has(Number(m[2])) && m[3].includes(BROWSER_ROOT)) all.add(Number(m[1]));
  }
  for (const pid of all) { try { process.kill(pid, "SIGKILL"); } catch { /* raced */ } }
  console.error(`${tool}: cleared ${all.size} abandoned browser process(es) from an earlier render`);
}

// Every launch in this directory goes through here, so the three ties are a
// property of the toolchain rather than of whichever tool remembered them.
// `args` extends the shared set instead of replacing it; anything else passes
// through to puppeteer.
export async function launchBrowser({ args = [], ...rest } = {}) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", "--disable-dev-shm-usage", ...args],
    // Ties Chrome's life to this process's — see the block at the top.
    pipe: true,
    // Puppeteer's own signal handling closes over CDP, which is the slow path
    // and races the exit. The handlers above own these and kill outright.
    handleSIGINT: false,
    handleSIGTERM: false,
    handleSIGHUP: false,
    ...rest,
  });
  LIVE_BROWSERS.add(browser);
  return browser;
}
