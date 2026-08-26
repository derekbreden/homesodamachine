// browser.js — one Chrome lifetime, shared by every tool here that renders
// through a headless browser.
//
// Chrome is a separate process, and an abandoned one does not idle: the viewer
// redraws the whole model at frame rate on scene.js's own animation loop, so a
// browser nobody is reading still costs a core. That is what makes the leak
// compound. A killed render leaves its tree spinning;
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

import fs from "fs";
import { execFileSync } from "child_process";
import puppeteer from "puppeteer";

// Puppeteer's browser cache, read off the binary it would launch — so a moved
// PUPPETEER_CACHE_DIR names itself, and so do the builds beside the current one
// (an older version, chrome-headless-shell) that a leak can just as easily be.
// Chrome installed for a person lives elsewhere and never matches.
async function browserRoot() {
  try {
    // …/<cache>/chrome/<build>/chrome-mac-arm64/… — the segment before `chrome`.
    const m = (await puppeteer.executablePath()).match(/^(.*[/\\])chrome[/\\]/);
    if (m) return m[1];
  } catch { /* no browser installed — the sweep has nothing to find */ }
  return "/.cache/puppeteer/";
}

// How long a STEP parse gets. This is a fact about the file's size and the
// machine — the enclosure assembly is a 20 MB STEP and occt-import-js runs it
// single-threaded on the page's own main thread — not a fact about the
// geometry, so it stands well past what a loaded laptop takes and
// `HSM_PARSE_TIMEOUT` moves it. It bounds the CDP protocol timeout in every
// tool that drives the viewer: while the parse holds the main thread, that
// round trip is what runs out first, and it fails naming the protocol instead
// of the file.
export const PARSE_TIMEOUT = Number(process.env.HSM_PARSE_TIMEOUT || 900000);

// A FRAME IS READ BACK IN THE TASK THAT DREW IT. scene.js's WebGLRenderer is
// built without `preserveDrawingBuffer`, so the drawing buffer holds a frame
// only between a render and the browser's next composite. A capture that goes
// through the page — `page.screenshot`, however long it waits first — reaches
// that cycle wherever it happens to land, which is a different frame each run:
// one scene gave four distinct pictures in eight runs of identical geometry,
// and `trim` then measured a different content box off each. Waiting cannot fix
// it and makes it worse, because the wait is what the arbitrary landing is
// measured across.
//
// So every renderer here ends its `page.evaluate` with the render and the read
// on adjacent lines,
//
//     renderer.render(scene, cam);
//     return renderer.domElement.toDataURL("image/png");
//
// and passes what comes back to this. One task runs to completion, so nothing
// composites between those two statements and the read sees the frame the
// render just drew.
//
// The picture is the canvas, not the page, so the viewer's nav, gizmo, buttons
// and modal are not in it and no tool here hides them to take a clean shot.
export function frameBuffer(dataURL) {
  return Buffer.from(String(dataURL).split(",")[1], "base64");
}

// THE VIEWER ASKS TWO ENDPOINTS WHETHER A THING EXISTS, AND 404 IS THE ANSWER "no".
// `mountScorecard` asks for a sidecar most models do not carry, and `probeEditor` asks
// whether the dev-only editor answers for this file at all — each reads the miss and draws
// nothing, which is the feature working. The browser logs every miss as a failed resource
// regardless, so a run over thirteen subjects prints twenty-six errors naming nothing that
// is wrong, and a real 404 stands in that crowd unread.
//
// These two are the only misses that are answers. Every other line is reported, and it
// carries the URL that failed: a console line naming no resource cannot be acted on, and
// dropping whole classes of them by their text hides the breakage the render exists to show.
const VIEWER_PROBES = ["/api/step-scorecard/", "/api/step-editor/overrides"];

export function consoleLine(msg) {
  const type = msg.type();
  if (type !== "error" && type !== "warning") return null;
  const url = (msg.location() || {}).url || "";
  if (VIEWER_PROBES.some((probe) => url.includes(probe))) return null;
  return `console.${type}: ${msg.text()}${url ? ` (${url})` : ""}`;
}

const LIVE_BROWSERS = new Set();

function killBrowserNow(browser) {
  const proc = browser.process();
  if (proc && proc.exitCode === null) {
    try { proc.kill("SIGKILL"); } catch { /* already gone */ }
  }
}

// A protocol request that missed its own deadline still occupies the browser's CDP pipe.
// Asking that poisoned browser to close or open another page queues behind the original
// 240-second protocol timeout. A caller that has already decided to discard every result from
// that browser needs the process gone now, before it can make a genuinely independent retry.
export function abortBrowser(browser) {
  if (!browser) return;
  LIVE_BROWSERS.delete(browser);
  killBrowserNow(browser);
}

// How long a teardown negotiates before it stops asking. The render is over by the time either
// of these runs — the PNG is written — so what is left is the process going away, and every
// second past this one buys nothing a SIGKILL does not.
const TEARDOWN_GRACE = 10000;

// Resolve when `work` does, or when the grace runs out, whichever comes first. A `catch` bounds
// a rejection and not a wait: an await that never settles is an await the line after it never
// reaches, so a teardown that only catches is a teardown that runs its kill only when it did
// not need it.
function within(ms, work) {
  return new Promise((resolve) => {
    const timer = setTimeout(resolve, ms);
    Promise.resolve(work).catch(() => {}).then(() => {
      clearTimeout(timer);
      resolve();
    });
  });
}

export async function closeBrowser(browser) {
  if (!browser) return;
  LIVE_BROWSERS.delete(browser);
  // close() negotiates over CDP, which a page still holding the main thread can
  // stall; the kill is what makes "the process is gone" true rather than likely.
  await within(TEARDOWN_GRACE, browser.close());
  killBrowserNow(browser);
}

// The sibling of closeBrowser: stop the in-process server the render booted.
//
// close() stops new connections and then waits for the open ones to end. The
// viewer holds a websocket on /ws for the life of the page, and that one does
// not end — so a tool that only calls close() writes its PNG and then hangs,
// leaving the caller to poll for the file and kill the process. Dropping the
// sockets first is what makes the wait finish.
export async function closeServer(server) {
  if (!server) return;
  server.closeAllConnections?.();
  await within(TEARDOWN_GRACE, new Promise((resolve, reject) =>
    server.close((err) => (err ? reject(err) : resolve())),
  ));
}

// THE WORK IS THE FILE, AND THE FILE IS WRITTEN. A one-shot render exits when its PNG is on
// disk; the event loop's remaining handles — a listening socket, a socket the page left open,
// a child whose pipes are still up — outlive that and hold a process with nothing left to do.
// `uv_run` idling on `kevent` for an hour is what that looks like from outside.
//
// stdout is flushed first, so a caller reading this through a pipe is handed what the run said.
export function finish(code = 0) {
  process.exitCode = code;
  process.stdout.write("", () => process.exit(code));
}

// What the teardown holds, on fixtures rather than on Chrome:
//
//     node tools/render/browser.js selftest
//
// A stalled close is the case that matters and the one a live browser will not stage on demand,
// so both halves are stood up here as objects that never settle.
export async function selftest() {
  let holds = 0;
  const hold = (label, ok, got) => {
    holds += ok ? 1 : 0;
    console.log(`  ${ok ? "\u2713" : "\u2717"} ${label}${ok ? "" : ` \u2014 ${got}`}`);
  };

  let killed = null;
  const stalled = {
    close: () => new Promise(() => {}),
    process: () => ({ exitCode: null, kill: (sig) => { killed = sig; } }),
  };
  let t = Date.now();
  await closeBrowser(stalled);
  const stalledMs = Date.now() - t;
  hold("a close that never settles still hands back", stalledMs < TEARDOWN_GRACE * 2, `${stalledMs} ms`);
  hold("and the process is killed rather than asked again", killed === "SIGKILL", String(killed));

  t = Date.now();
  await closeServer({ closeAllConnections: () => {}, close: () => {} });
  const srvMs = Date.now() - t;
  hold("a server whose close never calls back hands back", srvMs < TEARDOWN_GRACE * 2, `${srvMs} ms`);

  t = Date.now();
  await closeBrowser({ close: async () => {}, process: () => ({ exitCode: 0, kill: () => {} }) });
  const cleanMs = Date.now() - t;
  hold("a close that settles costs the grace nothing", cleanMs < 1000, `${cleanMs} ms`);

  console.log(`browser selftest ${holds}/4`);
  return holds === 4 ? 0 : 1;
}

if (process.argv[1] && process.argv[1].endsWith("browser.js") && process.argv[2] === "selftest") {
  process.exit(await selftest());
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
export async function sweepAbandonedBrowsers(tool = "render") {
  const BROWSER_ROOT = await browserRoot();
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
// A capture of one page reads the same pixels every time. The tree keeps these
// pictures and `sync_tree` holds each against the one the build cuts, byte for byte.
//
// Text rasterises unhinted, without subpixel blending or subpixel positioning. An
// image decodes before it is drawn. A tile is drawn whole. Skia takes one code path
// rather than one chosen off the host's CPU. The compositor finishes every stage
// before a capture reads it.
const DETERMINISTIC = [
  "--force-color-profile=srgb",
  "--disable-lcd-text",
  "--font-render-hinting=none",
  "--disable-font-subpixel-positioning",
  "--disable-checker-imaging",
  "--disable-partial-raster",
  "--disable-skia-runtime-opts",
  "--disable-threaded-animation",
  "--disable-image-animation-resync",
  // The capture reads a frame the compositor has finished. Without this one a second run of
  // `//:cards-build` over one source differs in 35 of 169 files; with it, 0.
  "--run-all-compositor-stages-before-draw",
  "--hide-scrollbars",
];

// `--disable-dev-shm-usage` MOVES CHROME'S FRAMES OFF SHARED MEMORY AND ONTO `/tmp`, which is
// the right trade only when `/dev/shm` is too small to hold them — a container's default is
// 64 MB and a 12.1 MP capture is ~48 MB raw. Where `/tmp` is a real disk, as it is under an
// overlay filesystem, that trade turns a capture into disk I/O and a large page stops
// answering. So ask the mount instead of assuming: 256 MB is past the largest frame this repo
// draws, and a host without `/dev/shm` at all (macOS) needs no flag either way.
const SHM_ARGS = (() => {
  try {
    const { bsize, blocks } = fs.statfsSync("/dev/shm");
    return bsize * blocks >= 256 * 1024 * 1024 ? [] : ["--disable-dev-shm-usage"];
  } catch {
    return [];
  }
})();

export async function launchBrowser({ args = [], ...rest } = {}) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ["--no-sandbox", ...SHM_ARGS, ...DETERMINISTIC, ...args],
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
