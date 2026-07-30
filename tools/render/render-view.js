#!/usr/bin/env node
// render-view.js — LOOK at the placed world. `probe` asks where a body sits,
// `fit` asks where one could sit, `arrange` asks how a set goes together, and
// all three answer in numbers. This one answers in a picture, through the same
// /3d viewer the machine is read in.
//
// A body renders in one of four modes. `--only` names the SOLID set — opaque
// faces and feature edges, one distinct tint each. `--xray` keeps faces at low
// opacity, for a body something else stands in front of. Everything else GHOSTS:
// feature edges alone, faint, no faces, still in frame. `--hide` removes.
//
// On the frame with it: callout labels in the margins, leader-lined to each
// solid body; a millimetre grid with numbered ticks in the view plane; a scale
// bar measured through the projection actually used; and section clips, cut
// faces left open.
//
// The legend — printed and burned into the corner — carries the camera, the
// projection, the target, the clip bands, the mm-per-pixel scale, the world
// rectangle the frame covers, the count of solid, ghosted and hidden bodies,
// and the name of every hidden one. A render is a bounded scan, and the box
// goes with the answer: `calibration/Fences.md`, and the `holding out` clause
// `fit.slab` prints for the same reason.
//
// Usage:
//   node tools/render/render-view.js <step-rel> <out.png> [options]
//   node tools/render/render-view.js <step-rel> --list          # names + boxes, no render
//
// Selection (comma-separated; `*` globs; matched against component names):
//   --only <globs>     render these SOLID. Default: everything is solid.
//   --xray <globs>     translucent faces + edges, for a body behind another.
//   --ghost <globs>    force these to edges-only context.
//   --hide <globs>     remove entirely. Reported by name in the legend.
//   --context <mode>   what unnamed bodies become when --only is given:
//                      ghost (default) | hide | solid | xray
//   --no-tint          one grey for the solid set instead of a hue each
//
// Camera:
//   --view <name>      right|left|front|back|top|bottom|iso  (repo axes: +Z up,
//                      -Y front). Sets --cam and --up together.
//   --cam x,y,z        camera direction from target. Default from --view, else 1,-1,1
//   --up x,y,z         camera up. Default from --view, else 0,0,1
//   --target x,y,z     look-at point. Default: centre of the SOLID set's bbox
//                      (not the whole model's — the subject is what you framed).
//   --span mm          orthographic half-height in mm. Implies --ortho.
//   --ortho            orthographic; span defaults to fit the solid set + 15%
//   --zoom f           perspective only: distance = f · solid-set radius. Default 2.5
//
// Reading aids:
//   --label            callout labels for the solid set (default on when --only
//                      is given and the solid set is 40 bodies or fewer)
//   --no-label         off
//   --grid             mm grid + numbered ticks (default on for --ortho)
//   --no-grid          off
//   --clip <a>:lo,hi   keep only geometry with world a∈[lo,hi]; a is x|y|z.
//                      Repeatable. Cut faces are left open, so a clipped body
//                      reads as clipped.
//   --ports            keep the port markers (off by default — they are dense)
//   --caption <text>   extra line in the burned-in legend
//
// Output:
//   --size WxH         default 1400x1100
//   --bg #hex          default #1a1a2e (site navy)
//   --edition id       which machine's tree the step path is in. Default kitchen.
//                      The trees mirror each other's filenames, so without this a
//                      thin path renders the kitchen's twin silently.
//
// The step path is relative to the edition's content root (matches /steps/*).

import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import puppeteer from "puppeteer";
import sharp from "sharp";

import { start } from "../../web/server.js";
import { DEFAULT_EDITION, EDITION_IDS, editionById } from "../../web/lib/editions.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");

// Camera presets. Repo convention is +Z up, -Y front (the user's side), +X right.
// `up` on the two Z-axis views lays onto ∓Y, as in scene.js's snapCameraToFace.
const VIEWS = {
  right:  { cam: [ 1,  0,  0], up: [0, 0,  1] },
  left:   { cam: [-1,  0,  0], up: [0, 0,  1] },
  front:  { cam: [ 0, -1,  0], up: [0, 0,  1] },
  back:   { cam: [ 0,  1,  0], up: [0, 0,  1] },
  top:    { cam: [ 0,  0,  1], up: [0, -1, 0] },
  bottom: { cam: [ 0,  0, -1], up: [0,  1, 0] },
  // Front-right-above — the front-iso of resetCamera() and the grid thumbnails.
  iso:    { cam: [ 1, -1,  1], up: [0, 0,  1] },
};

function usage(msg) {
  if (msg) console.error(`render-view: ${msg}`);
  console.error(
    "usage: node tools/render/render-view.js <step-rel> <out.png>\n" +
      "       [--only globs] [--xray globs] [--ghost globs] [--hide globs]\n" +
      "       [--context ghost|hide|solid|xray] [--no-tint]\n" +
      "       [--view right|left|front|back|top|bottom|iso] [--cam x,y,z] [--up x,y,z]\n" +
      "       [--target x,y,z] [--span mm] [--ortho] [--zoom f] [--label|--no-label]\n" +
      "       [--grid|--no-grid] [--clip x|y|z:lo,hi] [--ports] [--caption text]\n" +
      "       [--size WxH] [--bg #hex] [--edition id]\n" +
      "       node tools/render/render-view.js <step-rel> --list",
  );
  process.exit(1);
}

function vec(s, name) {
  const parts = String(s).split(",").map(Number);
  if (parts.length !== 3 || parts.some((n) => !Number.isFinite(n))) usage(`bad ${name}: ${s}`);
  return parts;
}

function globs(s) {
  return String(s)
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);
}

function parseArgs(argv) {
  const positional = [];
  const opts = {
    only: null,        // null = no subject named; everything is solid
    xray: [],
    ghost: [],
    hide: [],
    context: "ghost",
    tint: true,
    view: null,
    cam: null,
    up: null,
    target: null,
    span: null,
    ortho: false,
    zoom: 2.5,
    label: null,       // null = decide from the solid-set size
    grid: null,        // null = decide from the projection
    clips: [],
    ports: false,
    caption: null,
    width: 1400,
    height: 1100,
    bg: "#1a1a2e",
    edition: DEFAULT_EDITION,
    list: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const val = (flag) => (a.includes("=") ? a.split("=").slice(1).join("=") : argv[++i]);
    if (a === "--list") opts.list = true;
    else if (a === "--ortho") opts.ortho = true;
    else if (a === "--ports") opts.ports = true;
    else if (a === "--label") opts.label = true;
    else if (a === "--no-label") opts.label = false;
    else if (a === "--grid") opts.grid = true;
    else if (a === "--no-grid") opts.grid = false;
    else if (a === "--no-tint") opts.tint = false;
    else if (a.startsWith("--only")) opts.only = globs(val("only"));
    else if (a.startsWith("--xray")) opts.xray = globs(val("xray"));
    else if (a.startsWith("--ghost")) opts.ghost = globs(val("ghost"));
    else if (a.startsWith("--hide")) opts.hide = globs(val("hide"));
    else if (a.startsWith("--context")) opts.context = val("context");
    else if (a.startsWith("--view")) opts.view = val("view");
    else if (a.startsWith("--caption")) opts.caption = val("caption");
    else if (a.startsWith("--cam")) opts.cam = vec(val("cam"), "--cam");
    else if (a.startsWith("--up")) opts.up = vec(val("up"), "--up");
    else if (a.startsWith("--target")) opts.target = vec(val("target"), "--target");
    else if (a.startsWith("--span")) { opts.span = Number(val("span")); opts.ortho = true; }
    else if (a.startsWith("--zoom")) opts.zoom = Number(val("zoom"));
    else if (a.startsWith("--clip")) {
      const raw = String(val("clip"));
      const m = raw.match(/^([xyz])\s*[:=]\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)$/i);
      if (!m) usage(`bad --clip ${raw} (want x:lo,hi)`);
      const lo = Number(m[2]);
      const hi = Number(m[3]);
      if (!(hi > lo)) usage(`bad --clip ${raw} (hi must exceed lo)`);
      opts.clips.push({ axis: m[1].toLowerCase(), lo, hi });
    } else if (a.startsWith("--size")) {
      const m = String(val("size")).match(/^(\d+)x(\d+)$/);
      if (!m) usage("bad --size");
      opts.width = Number(m[1]);
      opts.height = Number(m[2]);
    } else if (a.startsWith("--bg")) opts.bg = val("bg");
    else if (a.startsWith("--edition")) opts.edition = val("edition");
    else positional.push(a);
  }
  if (opts.view) {
    if (!VIEWS[opts.view]) usage(`unknown --view ${opts.view} (have ${Object.keys(VIEWS).join(", ")})`);
    if (!opts.cam) opts.cam = VIEWS[opts.view].cam;
    if (!opts.up) opts.up = VIEWS[opts.view].up;
  }
  if (!opts.cam) opts.cam = VIEWS.iso.cam;
  if (!opts.up) opts.up = VIEWS.iso.up;
  if (!["ghost", "hide", "solid", "xray"].includes(opts.context)) usage(`bad --context ${opts.context}`);
  if (!Number.isFinite(opts.zoom) || opts.zoom <= 0) usage("bad --zoom");
  if (opts.span !== null && (!Number.isFinite(opts.span) || opts.span <= 0)) usage("bad --span");
  return { positional, opts };
}

// ---------------------------------------------------------------------------
// In-page work. Everything below runs inside the viewer, where the mounted
// group, the camera and THREE all live. One function: the scene edit lands
// between two frames.
// ---------------------------------------------------------------------------
async function inPageCompose(o) {
  const { THREE, renderer, scene, camera, controls, currentGroup } = window.__hsm;

  // scene.js's animate() closes over its own module binding of `camera` and
  // calls controls.update() every frame, so it renders the module's camera at
  // whatever pose the controls carry, not the one set here. It stops, and the
  // controls come off with it. ES modules are singletons, so this is the running
  // instance.
  const sceneMod = await import("/js/viewer/scene.js");
  sceneMod.stopAnimate();
  controls.enabled = false;

  // --- Selection -----------------------------------------------------------
  const rx = (pat) =>
    new RegExp("^" + pat.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*") + "$");
  const matchers = (pats) => (pats || []).map(rx);
  const hit = (ms, name) => ms.some((m) => m.test(name));

  const onlyM = o.only ? matchers(o.only) : null;
  const xrayM = matchers(o.xray);
  const ghostM = matchers(o.ghost);
  const hideM = matchers(o.hide);

  // Every distinct body name in the mounted group, and the meshes under it. An
  // unnamed mesh collects under "" and reports as "(unnamed)".
  const byName = new Map();
  for (const c of currentGroup.children) {
    if (!c.isMesh) continue;
    const n = c.name || "";
    if (!byName.has(n)) byName.set(n, []);
    byName.get(n).push(c);
  }

  // hide wins over ghost wins over xray wins over only. `--context` decides what
  // a body the caller never named becomes once a subject exists.
  const mode = new Map();
  for (const name of byName.keys()) {
    if (hit(hideM, name)) mode.set(name, "hidden");
    else if (hit(ghostM, name)) mode.set(name, "ghost");
    else if (hit(xrayM, name)) mode.set(name, "xray");
    else if (!onlyM) mode.set(name, "solid");
    else if (hit(onlyM, name)) mode.set(name, "solid");
    else mode.set(name, o.context);
  }

  // Names the caller asked for that no body answers to. Reported.
  const unmatched = [];
  for (const [flag, pats] of [["only", o.only], ["xray", o.xray], ["ghost", o.ghost], ["hide", o.hide]]) {
    for (const p of pats || []) {
      const r = rx(p);
      if (![...byName.keys()].some((n) => r.test(n))) unmatched.push(`--${flag} ${p}`);
    }
  }

  // --- Materials -----------------------------------------------------------
  // A ghost body is its feature EDGES alone: faint, no faces.
  const ghostEdge = new THREE.LineBasicMaterial({
    color: 0x8fa3bd, transparent: true, opacity: 0.34, depthWrite: false,
  });

  // One hue per solid body, taken in name order so a body keeps its colour
  // across runs. The label chip carries the same hex.
  const TINTS = [
    "#7fb3ff", "#ffb454", "#6fd6a6", "#ff8fa3", "#c79bff", "#ffe066",
    "#5fd4d6", "#ff9d6f", "#9fd356", "#f58fd8", "#8fa8ff", "#d6c48f",
  ];
  const solidNames = [...byName.keys()].filter((n) => mode.get(n) === "solid").sort();
  const tintOf = new Map();
  if (o.tint) solidNames.forEach((n, i) => tintOf.set(n, TINTS[i % TINTS.length]));

  for (const [name, meshes] of byName) {
    const m = mode.get(name);
    for (const mesh of meshes) {
      if (m === "solid") {
        const tint = tintOf.get(name);
        if (tint) {
          const c = new THREE.Color(tint);
          const isBack = mesh.material && mesh.material.side === THREE.BackSide;
          mesh.material = new THREE.MeshStandardMaterial({
            color: isBack ? c.clone().multiplyScalar(0.75) : c,
            metalness: 0.1, roughness: 0.6,
            side: isBack ? THREE.BackSide : THREE.FrontSide,
          });
        } else if (mesh.userData.baseMaterial) {
          // The shading material applyXray() parked.
          mesh.material = mesh.userData.baseMaterial;
        }
        mesh.visible = true;
      } else if (m === "xray") {
        mesh.visible = true; // the ghosted clone applyXray() already put on it
      } else {
        mesh.visible = false; // ghost and hidden both drop faces
      }
    }
  }

  // The x-ray pass added one LineSegments per solid carrying its component
  // name. A tinted body's edges darken its own tint; ghosts take the shared
  // faint one; hidden bodies lose theirs with their faces.
  const tintEdge = new Map();
  for (const [n, hex] of tintOf) {
    tintEdge.set(n, new THREE.LineBasicMaterial({
      color: new THREE.Color(hex).multiplyScalar(0.42),
    }));
  }
  for (const c of currentGroup.children) {
    if (!(c.userData && c.userData.isXrayEdge)) continue;
    const name = c.userData.xrayComponent || "";
    const m = mode.get(name) || "ghost";
    if (m === "hidden") { c.visible = false; continue; }
    c.visible = true;
    if (m === "ghost") c.material = ghostEdge;
    else if (m === "solid" && tintEdge.has(name)) c.material = tintEdge.get(name);
  }

  // Overlay groups are scene-level, not part of the model. Off unless asked for.
  for (const child of scene.children) {
    if (child.name === "port-markers" && !o.ports) child.visible = false;
    if (child.name === "shape-boxes") child.visible = false;
  }

  // --- Section clips -------------------------------------------------------
  // Global renderer planes, two per band, facing inward. Cut faces are left open.
  const AX = { x: [1, 0, 0], y: [0, 1, 0], z: [0, 0, 1] };
  const planes = [];
  for (const c of o.clips || []) {
    const a = new THREE.Vector3(...AX[c.axis]);
    planes.push(new THREE.Plane(a.clone(), -c.lo));          // keep a >= lo
    planes.push(new THREE.Plane(a.clone().negate(), c.hi));   // keep a <= hi
  }
  renderer.clippingPlanes = planes;
  renderer.localClippingEnabled = false;

  // --- Framing -------------------------------------------------------------
  // The subject frames the shot: the bbox of the SOLID set. The whole model's
  // box is the fallback, for a view that named no subject.
  const subject = new THREE.Box3();
  let solidCount = 0;
  for (const [name, meshes] of byName) {
    if (mode.get(name) !== "solid") continue;
    solidCount++;
    for (const mesh of meshes) subject.expandByObject(mesh);
  }
  const whole = new THREE.Box3().setFromObject(currentGroup);
  const frameBox = solidCount > 0 && !subject.isEmpty() ? subject : whole;

  const center = frameBox.getCenter(new THREE.Vector3());
  const size = frameBox.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y, size.z, 1) * 0.5;
  const target = o.target ? new THREE.Vector3(...o.target) : center.clone();
  const dir = new THREE.Vector3(...o.cam).normalize();

  const W = window.innerWidth;
  const H = window.innerHeight;
  const aspect = W / H;

  let cam = camera;
  let spanUsed = null;
  if (o.ortho) {
    // Half-height in mm. Given, or the subject plus 15%.
    const half = o.span !== null ? o.span : radius * 1.15;
    spanUsed = half;
    cam = new THREE.OrthographicCamera(
      -half * aspect, half * aspect, half, -half, 0.01, Math.max(radius, half) * 200,
    );
    window.__hsm.camera = cam;
    cam.position.copy(target).add(dir.clone().multiplyScalar(Math.max(radius, half) * 8));
  } else {
    cam.aspect = aspect;
    cam.position.copy(target).add(dir.clone().multiplyScalar(radius * o.zoom));
  }
  cam.up.set(...o.up);
  cam.lookAt(target);
  controls.object = cam;
  controls.target.copy(target);
  renderer.setSize(W, H, false);
  cam.updateProjectionMatrix();
  cam.updateMatrixWorld(true);

  // The viewer's WebGLRenderer is built without preserveDrawingBuffer, so the
  // drawing buffer is undefined once the browser has composited it and a
  // screenshot taken after that reads back blank. Re-render every frame, from the
  // posed camera, so whenever the capture lands there is a fresh frame in the
  // buffer.
  const draw = () => {
    renderer.render(scene, cam);
    window.__hsmPosedRaf = requestAnimationFrame(draw);
  };
  draw();

  // --- Projection helpers --------------------------------------------------
  const toScreen = (v) => {
    const p = v.clone().project(cam);
    return { x: (p.x * 0.5 + 0.5) * W, y: (-p.y * 0.5 + 0.5) * H, z: p.z };
  };
  // The world rectangle the frame covers at the target's depth, from the NDC
  // corners of the camera actually used. The grid and the scale bar read off it.
  const ndcZ = target.clone().project(cam).z;
  const cornerLo = new THREE.Vector3(-1, -1, ndcZ).unproject(cam);
  const cornerHi = new THREE.Vector3(1, 1, ndcZ).unproject(cam);

  // mm per pixel, measured: two points one screen-width apart in world.
  const mmPerPx = cornerLo.distanceTo(
    new THREE.Vector3(1, -1, ndcZ).unproject(cam),
  ) / W;

  // --- Annotation ----------------------------------------------------------
  // Computed here, drawn in node over the screenshot. A DOM overlay is composited
  // under the WebGL canvas whatever its z-index, so the frame is annotated after
  // it is a PNG.
  const gridLines = [];
  const gridTicks = [];

  // --- mm grid -------------------------------------------------------------
  // Lines of constant world coordinate on the two axes most perpendicular to the
  // view, ticked with the coordinate they hold.
  const gridInfo = { drawn: false, step: null, axes: null };
  if (o.grid) {
    const viewDir = new THREE.Vector3();
    cam.getWorldDirection(viewDir);
    const axes = [
      { k: "x", v: new THREE.Vector3(1, 0, 0) },
      { k: "y", v: new THREE.Vector3(0, 1, 0) },
      { k: "z", v: new THREE.Vector3(0, 0, 1) },
    ]
      .map((a) => ({ ...a, d: Math.abs(a.v.dot(viewDir)) }))
      .sort((a, b) => a.d - b.d);
    const inPlane = [axes[0], axes[1]]; // the two least along the view
    const depthAxis = axes[2];

    // Extents of the visible rectangle on each in-plane axis.
    const lo = {}, hi = {};
    for (const a of inPlane) {
      const c1 = cornerLo[a.k], c2 = cornerHi[a.k];
      lo[a.k] = Math.min(c1, c2);
      hi[a.k] = Math.max(c1, c2);
    }
    const nice = (raw) => {
      const pows = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500];
      for (const p of pows) if (raw <= p) return p;
      return 1000;
    };
    const step = nice(Math.max(hi[inPlane[0].k] - lo[inPlane[0].k],
                               hi[inPlane[1].k] - lo[inPlane[1].k]) / 9);
    gridInfo.drawn = true;
    gridInfo.step = step;
    gridInfo.axes = inPlane.map((a) => a.k).join("/");

    for (const a of inPlane) {
      const other = inPlane.find((b) => b.k !== a.k);
      const first = Math.ceil(lo[a.k] / step) * step;
      for (let v = first; v <= hi[a.k]; v += step) {
        const p1 = new THREE.Vector3(), p2 = new THREE.Vector3();
        p1[a.k] = v; p2[a.k] = v;
        p1[other.k] = lo[other.k]; p2[other.k] = hi[other.k];
        p1[depthAxis.k] = p2[depthAxis.k] = target[depthAxis.k];
        const s1 = toScreen(p1), s2 = toScreen(p2);
        if (!Number.isFinite(s1.x) || !Number.isFinite(s2.x)) continue;
        gridLines.push({ x1: s1.x, y1: s1.y, x2: s2.x, y2: s2.y, zero: Math.abs(v) < 1e-9 });
        // Tick number at the low-coordinate end, nudged inside the frame.
        gridTicks.push({
          x: Math.min(Math.max(s1.x, 30), W - 30),
          y: Math.min(Math.max(s1.y, 16), H - 10),
          text: `${a.k}${v}`,
        });
      }
    }
  }

  // --- Scale bar -----------------------------------------------------------
  // A round number of millimetres, measured through the same projection.
  const barMM = (() => {
    const wantPx = W * 0.16;
    const raw = wantPx * mmPerPx;
    const pows = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500];
    for (const p of pows) if (raw <= p) return p;
    return 1000;
  })();
  const barPx = barMM / mmPerPx;

  // --- Legend --------------------------------------------------------------
  // Ahead of the labels: its height is where the left gutter can start.
  const counts = { solid: 0, xray: 0, ghost: 0, hidden: 0 };
  const hiddenNames = [];
  for (const [name, m] of mode) {
    counts[m]++;
    if (m === "hidden") hiddenNames.push(name || "(unnamed)");
  }
  hiddenNames.sort();

  const lines = [];
  lines.push(o.title);
  lines.push(
    `${o.ortho ? `ortho span ±${spanUsed.toFixed(1)} mm` : `persp zoom ${o.zoom}`}` +
      `  cam ${o.cam.join(",")}  up ${o.up.join(",")}  target ${target.toArray().map((v) => v.toFixed(1)).join(",")}`,
  );
  lines.push(
    `${counts.solid} solid  ${counts.xray ? `${counts.xray} x-ray  ` : ""}` +
      `${counts.ghost} ghost (edges only)  ${counts.hidden} hidden   ${mmPerPx.toFixed(3)} mm/px`,
  );
  if (o.clips.length) {
    lines.push("clip  " + o.clips.map((c) => `${c.axis}[${c.lo},${c.hi}]`).join("  ") + "  (cuts left open)");
  }
  if (hiddenNames.length) {
    const shown = hiddenNames.slice(0, 6).join(" ");
    lines.push(`hiding  ${shown}${hiddenNames.length > 6 ? ` +${hiddenNames.length - 6} more` : ""}`);
  }
  if (gridInfo.drawn) lines.push(`grid  ${gridInfo.step} mm on ${gridInfo.axes}`);
  if (!o.ports) lines.push("port markers off");
  if (o.caption) lines.push(o.caption);
  o.legendBottom = 10 + lines.length * 17 + 14;

  // --- Callout labels ------------------------------------------------------
  // Labels sit in the left and right margins, each leader-lined to a dot on the
  // body it names.
  const labels = [];
  if (o.label) {
    const anchors = [];
    for (const [name, meshes] of byName) {
      if (mode.get(name) !== "solid") continue;
      const bb = new THREE.Box3();
      for (const mesh of meshes) bb.expandByObject(mesh);
      if (bb.isEmpty()) continue;
      const c = bb.getCenter(new THREE.Vector3());
      const s = toScreen(c);
      anchors.push({ name, s, world: c });
    }
    const left = anchors.filter((a) => a.s.x < W / 2).sort((a, b) => a.s.y - b.s.y);
    const right = anchors.filter((a) => a.s.x >= W / 2).sort((a, b) => a.s.y - b.s.y);
    // Each label wants its anchor's own height, so the leader stays short. Taken
    // in Y order, pushed down only as far as the one above forces, then pushed
    // back up off the bottom. The left gutter starts below the legend.
    const place = (list, side) => {
      const n = list.length;
      if (!n) return;
      const PITCH = 21;
      const top = side === "left" ? o.legendBottom + 14 : 22;
      const bot = H - 46;
      const ys = [];
      let prev = -Infinity;
      for (const a of list) {
        const want = Number.isFinite(a.s.y) ? a.s.y : top;
        const y = Math.max(want, prev + PITCH, top);
        ys.push(y);
        prev = y;
      }
      for (let i = ys.length - 1; i >= 0; i--) {
        if (ys[i] > bot) ys[i] = bot - (ys.length - 1 - i) * PITCH;
        if (i > 0 && ys[i] - ys[i - 1] < PITCH) ys[i - 1] = ys[i] - PITCH;
      }
      list.forEach((a, i) => {
        labels.push({
          name: a.name,
          side,
          tint: tintOf.get(a.name) || null,
          ax: a.s.x,
          ay: a.s.y,
          ly: Math.max(ys[i], 16),
          onScreen: Number.isFinite(a.s.x) && Number.isFinite(a.s.y) &&
                    a.s.x > -50 && a.s.x < W + 50 && a.s.y > -50 && a.s.y < H + 50,
          world: a.world.toArray().map((v) => +v.toFixed(2)),
        });
      });
    };
    place(left, "left");
    place(right, "right");
  }

  return {
    annot: {
      size: [W, H],
      gridLines,
      gridTicks,
      labels,
      scale: { x: W - barPx - 26, y: H - 24, px: barPx, mm: barMM },
      legend: lines,
    },
    names: [...byName.keys()].sort(),
    mode: Object.fromEntries(mode),
    counts,
    hiddenNames,
    unmatched,
    labels,
    mmPerPx,
    spanUsed,
    grid: gridInfo,
    barMM,
    target: target.toArray().map((v) => +v.toFixed(2)),
    subject: subject.isEmpty()
      ? null
      : { min: subject.min.toArray().map((v) => +v.toFixed(2)), max: subject.max.toArray().map((v) => +v.toFixed(2)) },
    frameWorld: {
      lo: cornerLo.toArray().map((v) => +v.toFixed(2)),
      hi: cornerHi.toArray().map((v) => +v.toFixed(2)),
    },
  };
}

// The annotation layer, as one SVG the size of the frame, composited over the
// screenshot. Text is monospace at a known size, so a backing plate is sized
// arithmetically from the character count.
const FONT = "ui-monospace, SFMono-Regular, Menlo, DejaVu Sans Mono, monospace";
const CH = 7.22; // advance width of 12px monospace

function esc(s) {
  return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function annotationSvg(a) {
  const [W, H] = a.size;
  const p = [];
  p.push(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">`);
  p.push(`<style>text{font-family:${FONT};font-size:12px}</style>`);

  for (const g of a.gridLines) {
    p.push(
      `<line x1="${g.x1.toFixed(1)}" y1="${g.y1.toFixed(1)}" x2="${g.x2.toFixed(1)}" y2="${g.y2.toFixed(1)}" ` +
        `stroke="${g.zero ? "#5a7099" : "#38436b"}" stroke-width="${g.zero ? 1.5 : 1}" opacity="0.85"/>`,
    );
  }
  for (const t of a.gridTicks) {
    const w = t.text.length * CH + 6;
    p.push(
      `<rect x="${(t.x - w / 2).toFixed(1)}" y="${(t.y - 11).toFixed(1)}" width="${w.toFixed(1)}" height="15" rx="2" fill="#1a1a2e" opacity="0.8"/>` +
        `<text x="${t.x.toFixed(1)}" y="${t.y.toFixed(1)}" fill="#8b9dc0" text-anchor="middle">${esc(t.text)}</text>`,
    );
  }

  for (const l of a.labels) {
    const swatch = l.tint ? 12 : 0; // room for the tint chip inside the plate
    const lx = l.side === "left" ? 16 + swatch : W - 16;
    const anchor = l.side === "left" ? "start" : "end";
    const ink = l.tint || "#ffd479";
    if (l.onScreen) {
      const jx = l.side === "left" ? 22 : W - 22;
      p.push(
        `<line x1="${l.ax.toFixed(1)}" y1="${l.ay.toFixed(1)}" x2="${jx}" y2="${(l.ly - 4).toFixed(1)}" ` +
          `stroke="${ink}" stroke-width="1" stroke-dasharray="3 3" opacity="0.85"/>` +
          `<circle cx="${l.ax.toFixed(1)}" cy="${l.ay.toFixed(1)}" r="3.2" fill="${ink}" stroke="#0c0e1c" stroke-width="0.8"/>`,
      );
    }
    const w = l.name.length * CH + 10 + swatch;
    const rx = l.side === "left" ? 11 : W - 11 - w;
    p.push(
      `<rect x="${rx.toFixed(1)}" y="${(l.ly - 12).toFixed(1)}" width="${w.toFixed(1)}" height="17" rx="3" ` +
        `fill="#0c0e1c" fill-opacity="0.9" stroke="#3d4a75" stroke-width="1"/>`,
    );
    if (l.tint) {
      const sx = l.side === "left" ? rx + 5 : rx + w - 12;
      p.push(`<rect x="${sx.toFixed(1)}" y="${(l.ly - 9).toFixed(1)}" width="7" height="11" rx="1.5" fill="${l.tint}"/>`);
    }
    const tx = l.side === "left" ? rx + 5 + swatch : rx + w - 5 - swatch;
    p.push(
      `<text x="${tx.toFixed(1)}" y="${l.ly.toFixed(1)}" fill="#eaf0fa" text-anchor="${anchor}" font-weight="600">${esc(l.name)}</text>`,
    );
  }

  const s = a.scale;
  p.push(
    `<line x1="${s.x.toFixed(1)}" y1="${s.y}" x2="${(s.x + s.px).toFixed(1)}" y2="${s.y}" stroke="#eaf0fa" stroke-width="2"/>` +
      `<line x1="${s.x.toFixed(1)}" y1="${s.y - 5}" x2="${s.x.toFixed(1)}" y2="${s.y + 5}" stroke="#eaf0fa" stroke-width="2"/>` +
      `<line x1="${(s.x + s.px).toFixed(1)}" y1="${s.y - 5}" x2="${(s.x + s.px).toFixed(1)}" y2="${s.y + 5}" stroke="#eaf0fa" stroke-width="2"/>` +
      `<text x="${(s.x + s.px / 2).toFixed(1)}" y="${s.y - 9}" fill="#eaf0fa" text-anchor="middle" font-weight="600">${s.mm} mm</text>`,
  );

  const lh = 17;
  const lw = Math.max(...a.legend.map((t) => t.length)) * CH + 22;
  p.push(
    `<rect x="12" y="10" width="${lw.toFixed(1)}" height="${a.legend.length * lh + 14}" rx="6" ` +
      `fill="#0c0e1c" fill-opacity="0.86" stroke="#3d4a75" stroke-width="1"/>`,
  );
  a.legend.forEach((t, i) => {
    p.push(
      `<text x="23" y="${28 + i * lh}" fill="${i === 0 ? "#eaf0fa" : "#b3c1da"}" ` +
        `font-weight="${i === 0 ? 600 : 400}">${esc(t)}</text>`,
    );
  });

  p.push("</svg>");
  return Buffer.from(p.join(""));
}

// The name/box table --list prints. Same walk as the compose pass, so a name
// here is a name --only accepts.
function inPageList() {
  const { THREE, currentGroup } = window.__hsm;
  const byName = new Map();
  for (const c of currentGroup.children) {
    if (!c.isMesh) continue;
    const n = c.name || "";
    if (!byName.has(n)) byName.set(n, new THREE.Box3());
    byName.get(n).expandByObject(c);
  }
  return [...byName.entries()]
    .map(([name, bb]) => ({
      name: name || "(unnamed)",
      min: bb.min.toArray().map((v) => +v.toFixed(2)),
      max: bb.max.toArray().map((v) => +v.toFixed(2)),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

async function withViewer({ stepRel, opts }, fn) {
  const edition = editionById(opts.edition);
  if (!edition) usage(`unknown --edition ${opts.edition} (have ${EDITION_IDS.join(", ")})`);
  const hardwareDir = path.join(REPO_ROOT, ...edition.dir);
  const stepAbs = path.join(hardwareDir, stepRel);
  if (!fs.existsSync(stepAbs)) throw new Error(`step file not found: ${stepAbs}`);

  const { server } = await start({ port: 0, dev: false, hardwareDir });
  const port = server.address().port;
  let browser;
  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-dev-shm-usage"],
    });
    const page = await browser.newPage();
    await page.setViewport({ width: opts.width, height: opts.height, deviceScaleFactor: 1 });
    page.on("pageerror", (err) => console.error("pageerror:", err.message));
    page.on("console", (msg) => {
      if (msg.type() === "error" && !/404/.test(msg.text())) console.error("console.error:", msg.text());
    });

    const url = `http://localhost:${port}/3d?file=${encodeURIComponent(stepRel)}`;
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForFunction(
      () => window.__hsm && window.__hsm.scene && window.__hsm.camera,
      { timeout: 30000 },
    );
    process.stderr.write("parsing STEP (occt-import-js)…\n");
    await page.waitForFunction(
      (want) => window.__hsm && window.__hsm.mountedStepFile === want,
      { timeout: 180000 },
      stepRel,
    );
    return await fn(page);
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve, reject) => server.close((err) => (err ? reject(err) : resolve())));
  }
}

async function main() {
  const { positional, opts } = parseArgs(process.argv.slice(2));
  const [stepRel, outRel] = positional;
  if (!stepRel) usage("missing <step-rel>");
  if (!opts.list && !outRel) usage("missing <out.png>");

  if (opts.list) {
    const rows = await withViewer({ stepRel, opts }, (page) => page.evaluate(inPageList));
    const w = Math.max(...rows.map((r) => r.name.length), 4);
    console.log(`${rows.length} named bodies in ${stepRel}`);
    for (const r of rows) {
      console.log(
        `${r.name.padEnd(w)}  x[${r.min[0].toFixed(2).padStart(9)},${r.max[0].toFixed(2).padStart(9)}]` +
          ` y[${r.min[1].toFixed(2).padStart(9)},${r.max[1].toFixed(2).padStart(9)}]` +
          ` z[${r.min[2].toFixed(2).padStart(9)},${r.max[2].toFixed(2).padStart(9)}]`,
      );
    }
    return;
  }

  const outAbs = path.isAbsolute(outRel) ? outRel : path.join(REPO_ROOT, outRel);
  fs.mkdirSync(path.dirname(outAbs), { recursive: true });

  const info = await withViewer({ stepRel, opts }, async (page) => {
    // Chrome hidden as in render-step.js. Applied before the overlay is built,
    // so none of these rules catch it.
    await page.addStyleTag({
      content: `
        nav, #site-nav, .nav-gear, footer, #site-footer,
        .cv-filename, .cv-close, .cv-backdrop, #gizmoCanvas,
        .cad-wrapper > .cad-loading, .cad-wrapper > .ruler-toggle,
        .cad-wrapper > .reset-view { display: none !important; }
        button, [role="button"] { display: none !important; }
        [class^="sc-"], [class*=" sc-"] { display: none !important; }
        .cv-card { width:100vw !important; height:100vh !important;
                   max-width:100vw !important; max-height:100vh !important;
                   border-radius:0 !important; }
        body, html, .cv-card, .cv-content, .cad-wrapper, #viewport {
          background: ${opts.bg} !important; }
      `,
    });

    // Labels on when a subject was named; grid on under ortho, where a
    // millimetre is the same length everywhere in the frame.
    const resolved = { ...opts, title: `${opts.edition}/${stepRel}` };
    if (resolved.label === null) resolved.label = !!opts.only;
    if (resolved.grid === null) resolved.grid = opts.ortho;

    const out = await page.evaluate(inPageCompose, resolved);
    await new Promise((r) => setTimeout(r, 150));
    const raw = await page.screenshot({ type: "png", omitBackground: false });
    const buf = await sharp(raw)
      .composite([{ input: annotationSvg(out.annot), top: 0, left: 0 }])
      .png({ compressionLevel: 9 })
      .toBuffer();
    fs.writeFileSync(outAbs, buf);
    return out;
  });

  // The legend, on stdout as well as in the frame.
  console.log(`\nwrote ${outAbs}  (${opts.width}x${opts.height})`);
  console.log(`  view      ${opts.view || "custom"}  cam ${opts.cam.join(",")}  up ${opts.up.join(",")}`);
  console.log(
    `  framing   ${opts.ortho ? `ortho, span ±${info.spanUsed.toFixed(2)} mm` : `perspective, zoom ${opts.zoom}`}` +
      `  target ${info.target.join(",")}  ${info.mmPerPx.toFixed(4)} mm/px  scale bar ${info.barMM} mm`,
  );
  if (info.subject) {
    console.log(
      `  subject   x[${info.subject.min[0]},${info.subject.max[0]}]` +
        ` y[${info.subject.min[1]},${info.subject.max[1]}]` +
        ` z[${info.subject.min[2]},${info.subject.max[2]}]  (the solid set's box — what framed the shot)`,
    );
  }
  console.log(`  frame     covers world lo ${info.frameWorld.lo.join(",")} → hi ${info.frameWorld.hi.join(",")} at the target plane`);
  console.log(
    `  bodies    ${info.counts.solid} solid   ${info.counts.xray} x-ray   ` +
      `${info.counts.ghost} ghost (edges only)   ${info.counts.hidden} hidden`,
  );
  if (info.hiddenNames.length) console.log(`  hiding    ${info.hiddenNames.join(" ")}`);
  if (info.grid.drawn) console.log(`  grid      ${info.grid.step} mm on ${info.grid.axes}`);
  if (info.labels.length) console.log(`  labelled  ${info.labels.map((l) => l.name).join(" ")}`);
  if (info.counts.ghost && opts.context === "ghost") {
    console.log(`  note      nothing was removed except the ${info.counts.hidden} above; ghosts are edges, still in frame`);
  }
  if (info.unmatched.length) {
    console.log(`\n  !! matched no body: ${info.unmatched.join("  ")}`);
    for (const u of info.unmatched) {
      const pat = u.split(" ").pop().replace(/\*/g, "");
      const stem = pat.split("-")[0];
      const near = info.names.filter((n) => n.includes(stem) || n.startsWith(pat.slice(0, 4)));
      console.log(`     ${u} — nearest names present: ${near.length ? near.join(" ") : "(none)"}`);
    }
    console.log(`     all ${info.names.length} names in the mounted group:`);
    console.log(`     ${info.names.map((n) => n || "(unnamed)").join(" ")}`);
  }
}

main().catch((err) => {
  console.error(err.stack || err.message || err);
  process.exit(1);
});
