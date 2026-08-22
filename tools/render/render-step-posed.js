#!/usr/bin/env node
// render-step-posed.js — render STEP files to PNG with a caller-posed camera,
// for imagery that needs a specific viewpoint (assembly instruction cards).
// Same server + /3d viewer path as render-step.js; differs in taking the
// camera, framing, background, and output size from the caller instead of the
// fixed isometric pose.
//
// Usage:
//   node tools/render/render-step-posed.js <step-file-relative> <output-png> [options]
//   node tools/render/render-step-posed.js --jobs <manifest.json>
//   node tools/render/render-step-posed.js --jobs -            # the manifest on stdin
//
// Options:
//   --cam x,y,z      camera direction from target (unnormalized ok). Default 1,1,1
//   --target x,y,z   look-at point in model coords. Default: bbox center
//   --zoom f         perspective only: distance = f · bbox-radius along --cam.
//                    Default 3.0. Under --ortho the half-height is the frame and
//                    it fits the subject; tools/render/render-view.js takes an
//                    orthographic half-height in millimetres as --span.
//   --up x,y,z       camera up. Default 0,1,0
//   --size WxH       viewport + output size. Default 1600x1200
//   --bg #hex        background. Default #1a1a2e (site navy)
//   --trim           trim to background and cap long side 1600 (default: off —
//                    cards want the exact framed viewport)
//   --solid          opaque surfaces, no feature-edge ghost (default: the
//                    viewer's own x-ray, which every part draws through)
//   --ortho          orthographic projection (dimension-drawing look)
//
// The step path is relative to hardware/ (matches /api/steps + /steps/*).
//
// ONE BOOT, HOWEVER MANY PICTURES. A server, a Chromium, a navigation and the
// page's whole module graph — three.js, the viewer, occt-import-js in wasm —
// come to ~1.6 s, and the render itself to a fraction of that. Paid once per
// picture that is 34 boots for the assembly cards' 34 pictures; paid once per
// RUN it is one. `--jobs` is that run: a JSON array, each entry one picture with
// its own camera and flags,
//
//     [{"step": "...", "out": "...", "cam": [1,1,1], "zoom": 3.0,
//       "target": [x,y,z], "up": [0,0,1], "size": "1600x1200", "bg": "#1a1a2e",
//       "trim": true, "solid": true, "ortho": false}, ...]
//
// and only `step` and `out` are required — every other key defaults to the flag
// of the same name. `render-thumbnails.js` takes its `--payloads` manifest the
// same way and reuses one page across a root's files for the same reason.
//
// THE VIEWER IS RE-POINTED, NOT RELOADED. `window.__hsm.loadStepFile` is the
// page's own mount — it drops the previous group, disposes its geometry, builds
// the new one and re-frames the camera, which is exactly what the navigation
// did — so a second subject costs the fetch and the build rather than the boot.
// A job asking for a different viewport gets a fresh page rather than a
// `setViewport` on a page whose layout has already settled around the old one.
//
// A FAILURE IS ONE PICTURE, NOT THE RUN. A job that throws is reported by name,
// its page is dropped so a wedged one cannot take the rest with it, and the
// remaining jobs still draw; the process then exits non-zero naming every job
// that failed. A partial render that reports success is the one outcome this
// must not have.
//
// AND A PAGE THAT THREW IS NOT A PICTURE. An uncaught exception in the viewer —
// a `seatParts` that cannot read its tree, a module that fails to import — leaves
// the page standing, the canvas mounted and `toDataURL` answering, so a run that
// only watched its own awaits photographed whatever survived and exited 0. Every
// `pageerror` is collected on the page and the job holding it fails by name.
// `pageerror` IS THE UNCAUGHT-EXCEPTION EVENT and nothing else: the four misses a
// clean run makes — `/api/step-editor/overrides`, `/api/step-scorecard/…`,
// `/meshes/….step.mesh`, `/steps/….step` — arrive as console entries behind an
// `onerror` fallback, and no 404 is read here.
//
// AND A PICTURE IS THE SAME PICTURE WHEREVER IN A RUN IT IS DRAWN. Everything
// the viewer keeps between mounts — the shared shading materials, the edge
// materials' pixel resolution, the scene fog scene.js's animate loop refits on
// whatever the camera is doing — is set here, per picture, rather than
// inherited. `HSM_POSE_DEBUG=1` prints what each frame was composed against;
// it is what the byte-for-byte comparison between a run of N invocations and
// one invocation of N jobs was settled with.
//
// `sweepAbandonedBrowsers` still runs, once, at the top: it clears Chrome trees
// left behind by renders that were killed before their own teardown ran, and
// that leak is a property of how a run ends rather than of how many pictures it
// drew. Batching makes it cheaper — once a run instead of once a picture — not
// unnecessary.

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { PARSE_TIMEOUT, closeBrowser, closeServer, finish, frameBuffer, launchBrowser, sweepAbandonedBrowsers } from "./browser.js";
import sharp from "sharp";

import { start } from "../../web/server.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

function usage(msg) {
  if (msg) console.error(`render-step-posed: ${msg}`);
  console.error(
    "usage: node tools/render/render-step-posed.js <step-file-relative> <output-png> " +
      "[--cam x,y,z] [--target x,y,z] [--zoom f] [--up x,y,z] [--size WxH] [--bg #hex] [--trim] " +
      "[--solid] [--ortho]\n" +
      "       node tools/render/render-step-posed.js --jobs <manifest.json|->",
  );
  process.exit(1);
}

// The camera, the framing and the flags a picture is drawn with, before a
// caller has said anything. Both front doors start here, so a manifest entry
// that states nothing draws what the bare command line draws.
function defaults() {
  return {
    cam: [1, 1, 1],
    target: null,
    zoom: 3.0,
    up: [0, 1, 0],
    width: 1600,
    height: 1200,
    bg: "#1a1a2e",
    trim: false,
    solid: false,
    ortho: false,
  };
}

// `1,2,3` off a command line or `[1, 2, 3]` out of a manifest — one shape by
// the time anything reads it.
function vec(s, name) {
  const parts = (Array.isArray(s) ? s : String(s).split(",")).map(Number);
  if (parts.length !== 3 || parts.some((n) => !Number.isFinite(n)))
    usage(`bad ${name}: ${JSON.stringify(s)}`);
  return parts;
}

function size(s, opts, name) {
  const m = String(s).match(/^(\d+)x(\d+)$/);
  if (!m) usage(`bad ${name}: ${s}`);
  opts.width = Number(m[1]);
  opts.height = Number(m[2]);
}

function parseArgs(argv) {
  const positional = [];
  const opts = defaults();
  let jobs = null;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = (flag) => (a.includes("=") ? a.split("=").slice(1).join("=") : argv[++i]);
    if (a.startsWith("--jobs")) jobs = val("jobs");
    else if (a.startsWith("--cam")) opts.cam = vec(val("cam"), "--cam");
    else if (a.startsWith("--target")) opts.target = vec(val("target"), "--target");
    else if (a.startsWith("--zoom")) opts.zoom = Number(val("zoom"));
    else if (a.startsWith("--up")) opts.up = vec(val("up"), "--up");
    else if (a.startsWith("--size")) size(val("size"), opts, "--size");
    else if (a.startsWith("--bg")) opts.bg = val("bg");
    else if (a === "--trim") opts.trim = true;
    else if (a === "--solid") opts.solid = true;
    else if (a === "--ortho") opts.ortho = true;
    else positional.push(a);
  }
  if (!Number.isFinite(opts.zoom) || opts.zoom <= 0) usage("bad --zoom");
  return { positional, opts, jobs };
}

function outPath(out) {
  const abs = path.isAbsolute(out) ? out : path.join(REPO_ROOT, out);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  return abs;
}

// One manifest entry as the job the render loop takes. Keys absent take the
// flag's own default, so an entry wanting a plain three-quarter view is two
// keys long.
function job(entry, i) {
  const where = `--jobs[${i}]`;
  if (!entry || typeof entry !== "object" || Array.isArray(entry))
    usage(`${where}: expected an object`);
  if (!entry.step || !entry.out) usage(`${where}: needs "step" and "out"`);
  const opts = defaults();
  if (entry.cam != null) opts.cam = vec(entry.cam, `${where}.cam`);
  if (entry.target != null) opts.target = vec(entry.target, `${where}.target`);
  if (entry.up != null) opts.up = vec(entry.up, `${where}.up`);
  if (entry.zoom != null) opts.zoom = Number(entry.zoom);
  if (entry.size != null) size(entry.size, opts, `${where}.size`);
  if (entry.bg != null) opts.bg = String(entry.bg);
  opts.trim = !!entry.trim;
  opts.solid = !!entry.solid;
  opts.ortho = !!entry.ortho;
  if (!Number.isFinite(opts.zoom) || opts.zoom <= 0) usage(`${where}: bad zoom`);
  return { stepRel: String(entry.step), outAbs: outPath(String(entry.out)), opts };
}

function readStdin() {
  return new Promise((resolve, reject) => {
    let buf = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (d) => { buf += d; });
    process.stdin.on("end", () => resolve(buf));
    process.stdin.on("error", reject);
  });
}

async function readJobs(where) {
  const text = where === "-" ? await readStdin() : fs.readFileSync(where, "utf8");
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch (e) {
    usage(`--jobs ${where}: not JSON — ${e.message}`);
  }
  if (!Array.isArray(parsed)) usage(`--jobs ${where}: expected an array of jobs`);
  return parsed.map(job);
}

// Whatever the page threw since this was last asked, as one error. Draining is
// what makes it per-job: a page carried across subjects reports each throw once,
// against the picture that was being drawn when it happened.
function throwIfPageErrored(page, when) {
  const errs = page && page.__hsmPageErrors;
  if (!errs || !errs.length) return;
  page.__hsmPageErrors = [];
  throw new Error(
    `the viewer threw while ${when} — a page that threw is not a picture:\n    ` +
    errs.join("\n    "),
  );
}

// Stand the viewer on a fresh page with `stepRel` mounted. This is the whole of
// what a one-picture invocation ever did, and it is what a job asking for a new
// viewport gets.
async function openViewer(browser, port, stepRel, opts) {
  const page = await browser.newPage();
  await page.setViewport({
    width: opts.width,
    height: opts.height,
    deviceScaleFactor: 1,
  });

  page.__hsmPageErrors = [];
  page.on("pageerror", (err) => {
    console.error("pageerror:", err.message);
    page.__hsmPageErrors.push(err.message || String(err));
  });
  page.on("console", (msg) => {
    const t = msg.type();
    if (t === "error" || t === "warning") console.error(`console.${t}:`, msg.text());
  });

  const url = `http://localhost:${port}/3d?file=${encodeURIComponent(stepRel)}`;
  console.log(`navigating: ${url}`);
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });

  console.log("waiting for viewer module...");
  // THIS DEADLINE IS THE ONE THAT FAILS BUILDS, and it was the shortest of the three for the
  // work that is least bounded. Navigation gets 60 s and the occt parse below gets 120 s; this
  // waits for the page's whole module graph — three.js, the viewer, occt-import-js in wasm — to
  // import and execute, on a box that may be in swap with seven other actions beside it. There
  // is nothing correct about 30 s: a page that is coming up slowly is not a page that is wrong,
  // and the wait exists to catch one that will never come up at all.
  await page.waitForFunction(
    () => window.__hsm && window.__hsm.scene && window.__hsm.camera,
    { timeout: 120000 },
  );

  console.log("waiting for STEP to mount (occt-import-js parse)...");
  // A THROW IS THE REASON THE WAIT NEVER COMES TRUE. `main.js` applies the route
  // in `fetchFiles().then(…)`, so an exception anywhere in the grid rejects that
  // chain and the mount this is waiting on never happens — reported, without
  // this, as a two-minute deadline against a condition, with the cause a line of
  // stdout somebody has to go and find.
  try {
    await page.waitForFunction(
      (want) => window.__hsm && window.__hsm.mountedStepFile === want,
      { timeout: 120000 },
      stepRel,
    );
  } catch (err) {
    throwIfPageErrored(page, "standing the viewer up");
    throw err;
  }

  return page;
}

// Point a page that is already up at the next subject. `loadStepFile` is the
// page's own mount — the same call the route made — and it has awaited the
// fetch, the build and the re-frame by the time it resolves, so what it leaves
// mounted IS the answer and a miss is reported here rather than as a two-minute
// wait on a condition that will not come true.
async function mount(page, stepRel) {
  console.log(`re-pointing the viewer at ${stepRel} ...`);
  const got = await page.evaluate(async (file) => {
    const hsm = window.__hsm;
    // An --ortho job hands __hsm a camera of its own. The page's own one is
    // what the next mount frames against, so it is put back before the load.
    if (!hsm.__baseCamera) hsm.__baseCamera = hsm.camera;
    hsm.camera = hsm.__baseCamera;
    hsm.controls.object = hsm.camera;
    // AND THE MATERIALS THIS PAGE HAS ALREADY MADE ARE DROPPED. The viewer
    // shares them across mounts by colour, and three.js orders an opaque draw by
    // material id — so a subject arriving second is drawn in an order the first
    // one fixed, and coplanar faces change which of them survives. A fresh page
    // starts with these empty; so does every mount here.
    (await import("/js/viewer/step.js")).forgetMaterials();
    (await import("/js/viewer/xray.js")).forgetEdgeMaterials();
    await hsm.loadStepFile(file);
    return hsm.mountedStepFile;
  }, stepRel);
  if (got !== stepRel)
    throw new Error(`the viewer did not mount it — it holds ${got === null ? "nothing" : got}`);
}

// Pose the camera, draw one frame, read it back, write the PNG.
async function shoot(page, outAbs, opts) {
  console.log("posing camera + rendering frame...");
  const shot = await page.evaluate(async (o) => {
    const hsm = window.__hsm;
    // The pose below may leave an orthographic camera behind (see --ortho), and
    // the next picture on this page starts from whatever this one left.
    if (!hsm.__baseCamera) hsm.__baseCamera = hsm.camera;
    hsm.camera = hsm.__baseCamera;
    const { THREE, renderer, scene, camera, controls, currentGroup } = hsm;

    // EVERY AWAIT IS SPENT BEFORE THE FRAME IS SET UP. An `await` hands the
    // page's task loop back, and the loop that runs there is scene.js's
    // animate() — which calls updateDepthRange() and syncEdgeResolution() on
    // whatever the camera and the buffer are at that instant. From stopAnimate()
    // down to the read-back below nothing yields, so the frame is composed
    // against state this task set and nothing else.
    const sceneMod = await import("/js/viewer/scene.js");
    const xray = await import("/js/viewer/xray.js");

    // scene.js's animate() closes over its own module binding of `camera` and
    // calls controls.update() every frame, so it renders the module's camera at
    // whatever pose the controls carry, not the one set here. It stops, and the
    // controls come off with it. ES modules are singletons, so this is the
    // running instance.
    sceneMod.stopAnimate();

    // AND THE FRAMING IS PUT BACK WHERE A LOAD LEAVES IT. `resetCamera` is the
    // page's own default framing for the mounted group, and running it is what
    // makes scene.fog a function of THIS subject rather than of where the last
    // picture's camera happened to be standing when a frame last ran. The pose
    // below overwrites the camera it sets; the fog it fits is what stays.
    sceneMod.resetCamera(currentGroup);
    controls.enabled = false;

    // xray.js remembers the mode in localStorage and applies it to the mounted
    // group as it is set. A page drawing one picture reads the default and is
    // told once; a page drawing many carries the last job's answer, so the mode
    // is set WHEN IT IS WRONG rather than when the flag is on — which leaves a
    // one-picture run doing exactly what it did.
    if (xray.isXrayEnabled() === !!o.solid) xray.setXrayEnabled(!o.solid);

    const box = new THREE.Box3().setFromObject(currentGroup);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(size.x, size.y, size.z) * 0.5;
    const target = o.target
      ? new THREE.Vector3(...o.target)
      : center.clone();
    const dir = new THREE.Vector3(...o.cam).normalize();
    const aspect = window.innerWidth / window.innerHeight;
    let cam = camera;
    if (o.ortho) {
      // An orthographic camera framing the subject. Its half-height is the
      // frame, so distance along `dir` only has to clear the near plane.
      const half = radius * 1.1;
      cam = new THREE.OrthographicCamera(
        -half * aspect, half * aspect, half, -half, 0.01, radius * 100,
      );
      hsm.camera = cam;
    } else {
      cam.aspect = aspect;
    }
    cam.position.copy(target).add(dir.multiplyScalar(radius * o.zoom));
    cam.up.set(...o.up);
    cam.lookAt(target);
    controls.object = cam;
    controls.target.copy(target);
    renderer.setSize(window.innerWidth, window.innerHeight, false);
    // AND THE FEATURE EDGES ARE SIZED TO THE BUFFER THIS FRAME IS DRAWN INTO.
    // xray.js states linewidth in pixels of whatever resolution its materials
    // were last told, and the thing that tells them is scene.js's animate loop,
    // which measures the modal wrapper mid-open-transition and which this tool
    // has just stopped. That gave one part's edges a width off how long its own
    // STEP took to mount — 1531\u00d71140 for a small subject and 1568\u00d71168 for a
    // large one, against a viewport of 1600\u00d71200 in both. The buffer above is
    // the one the frame lands in; it is what the width means.
    xray.syncEdgeResolution(renderer);
    // scene.js's animate() is stopped here, so the planes are fitted once,
    // to the group this pose is framing.
    sceneMod.fitCameraDepth(cam, center, size.length() / 2);
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld(true);

    // The read is on the line after the render — see browser.js frameBuffer.
    // The clear colour is set here so the read-back carries the background the
    // card wants: it comes off the canvas, not the page behind it.
    renderer.setClearColor(o.bg, 1);
    renderer.render(scene, cam);
    const png = renderer.domElement.toDataURL("image/png");
    // WHAT THE FRAME WAS COMPOSED AGAINST. Two pictures of one subject that
    // differ have differed in one of these, and every one of them is state some
    // module in the viewer carries across a mount rather than an argument this
    // tool passed. `HSM_POSE_DEBUG=1` prints the row; the picture never reads it.
    if (!o.__debug) return { png, state: null };
    const buf = renderer.getDrawingBufferSize(new THREE.Vector2());
    const ids = [];
    currentGroup.traverse((c) => { if (c.material) ids.push(c.material.id); });
    const ranks = [...new Set(ids)].sort((a, b) => a - b);
    return { png, state: {
      fog: scene.fog ? [scene.fog.near, scene.fog.far] : null,
      camNearFar: [cam.near, cam.far],
      camPos: cam.position.toArray(),
      camUp: cam.up.toArray(),
      aspect: cam.aspect ?? null,
      buffer: [buf.x, buf.y],
      winSize: [window.innerWidth, window.innerHeight],
      // The order three.js will draw the opaque solids in — it sorts on
      // material id, so this is the sequence, not the ids.
      drawOrder: ids.map((m) => ranks.indexOf(m)).join(","),
      edgeRes: (() => { const m = xray.makeEdgeMaterial({}); return [m.resolution.x, m.resolution.y]; })(),
      xray: xray.isXrayEnabled(),
      solids: currentGroup.children.length,
      box: [box.min.toArray(), box.max.toArray()],
    } };
  }, { ...opts, __debug: !!process.env.HSM_POSE_DEBUG });

  console.log("reading the frame back...");
  // Before the write, so a frame composed against a page that threw never
  // reaches the tree as a picture.
  throwIfPageErrored(page, "drawing the frame");
  if (shot.state) console.log("POSEDEBUG " + path.basename(outAbs) + " " + JSON.stringify(shot.state));
  const raw = frameBuffer(shot.png);

  let buf = raw;
  if (opts.trim) {
    let img = sharp(raw).trim({ background: opts.bg, threshold: 10 });
    const meta = await img.metadata();
    if (meta.width && meta.height) {
      img = img.resize({
        width: 1600,
        height: 1600,
        fit: "inside",
        withoutEnlargement: true,
      });
    }
    buf = await img.flatten({ background: opts.bg }).png().toBuffer();
  }
  fs.writeFileSync(outAbs, buf);
  const finalMeta = await sharp(buf).metadata();
  console.log(
    `wrote ${outAbs} (${finalMeta.width}x${finalMeta.height}, ${buf.length} bytes)`,
  );
}

// Every job, on one server and one browser, on one page per viewport.
async function renderAll(jobs) {
  const hardwareDir = path.join(REPO_ROOT, "hardware");

  const { server } = await start({ port: 0, dev: false, hardwareDir });
  const port = server.address().port;
  console.log(`server up on :${port}`);

  let browser;
  let page = null;
  let pageSize = null;
  const failed = [];
  try {
    browser = await launchBrowser({ protocolTimeout: PARSE_TIMEOUT + 60000 });
    for (const [i, { stepRel, outAbs, opts }] of jobs.entries()) {
      const label = jobs.length > 1 ? `[${i + 1}/${jobs.length}] ${stepRel}` : stepRel;
      if (jobs.length > 1) console.log(`\n${label}`);
      try {
        const stepAbs = path.join(hardwareDir, stepRel);
        if (!fs.existsSync(stepAbs)) throw new Error(`step file not found: ${stepAbs}`);
        const want = `${opts.width}x${opts.height}`;
        if (page && pageSize === want) {
          await mount(page, stepRel);
        } else {
          if (page) await page.close().catch(() => {});
          page = await openViewer(browser, port, stepRel, opts);
          pageSize = want;
        }
        // Before the frame: a boot or a mount that threw has already left the
        // page holding something other than this subject, drawn or not.
        throwIfPageErrored(page, "standing the viewer up");
        await shoot(page, outAbs, opts);
      } catch (err) {
        const why = err.message || String(err);
        console.error(`FAILED ${label}: ${why}`);
        failed.push(`${stepRel} -> ${outAbs}: ${why}`);
        // The next job starts on a page this one has not been in.
        if (page) {
          await page.close().catch(() => {});
          page = null;
          pageSize = null;
        }
      }
    }
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
  }

  if (failed.length)
    throw new Error(
      `${failed.length} of ${jobs.length} picture(s) failed:\n  ` + failed.join("\n  "),
    );
}

async function main() {
  await sweepAbandonedBrowsers("render-step-posed");
  const { positional, opts, jobs } = parseArgs(process.argv.slice(2));
  if (jobs !== null) {
    if (positional.length) usage(`--jobs takes the whole run: ${positional.join(" ")}`);
    const list = await readJobs(jobs);
    if (!list.length) {
      console.log("no pictures to draw");
      return;
    }
    console.log(`drawing ${list.length} picture(s) on one browser`);
    await renderAll(list);
    return;
  }
  const [stepRel, outRel] = positional;
  if (!stepRel || !outRel) usage("missing arguments");
  await renderAll([{ stepRel, outAbs: outPath(outRel), opts }]);
}

main().then(
  () => finish(0),
  (err) => {
    console.error(err.message || err);
    finish(1);
  },
);
