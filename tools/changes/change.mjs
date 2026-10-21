#!/usr/bin/env node
// change.mjs — a change to a model as two pictures from one camera: the model as it stood
// before the change and as it stands after it, for the entry the change leaves under changes/.
//
//   node tools/changes/change.mjs snapshot [--model <rel>]... [--out <dir>]
//   node tools/changes/change.mjs changed --before <stash|payload> [--after <stash|payload>]
//        [--model <rel>] [--tol mm] [--cell mm] [--top n] [--json]
//   node tools/changes/change.mjs render <entry-dir> --view <name> --before <stash|payload>
//        [--after <stash|payload>] [--model <rel>] [--caption "..."]
//        [--cam x,y,z] [--target x,y,z] [--up x,y,z] [--span mm | --zoom f] [--ortho]
//        [--size WxH] [--only names] [--section "x,y,z:nx,ny,nz"] [--highlight names|changed]
//        [--ghost names] [--xray] [--mark "x,y,z[,r][:label]"]... [--no-fog] [--no-ground]
//        [--bg #hex] [--quality q]
//
// `<rel>` is a STEP path under hardware/, the way /3d names it; the default is the machine,
// `manifold-layout/enclosure-assembly.step`. What is drawn is its viewer payload, `<rel>.mesh`,
// which is the triangles /3d draws. Names are the solid names the viewer's picker shows, with `*`
// and `?` as wildcards, comma-separated or the flag repeated. Coordinates are millimetres on the
// machine's axes: front is -Y, up is +Z.
//
// THE BEFORE IS GONE BY THE TIME ANYONE ASKS FOR IT, SO IT IS SET ASIDE FIRST. A generator
// rewrites its outputs in place, the site's store drops every object main's pointer file stops
// naming within the hour, and the release keeps no member of a past cut on its own. So the
// geometry a change replaced exists only until the rebuild, and `snapshot` is the copy made
// before it: the payload of each model about to change, outside the tree, with its sha256 and
// the HEAD it stood at. Seconds and no browser. A stash is scratch — it is never committed and
// nothing under changes/ holds one.
//
// `changed` SAYS WHAT TO POINT AT. Mesh by mesh, by name and by bytes, then, for each mesh whose
// bytes moved, by surface: every vertex of one version is measured against the other version's
// triangles, and the vertices that stand off it by more than `--tol` are the change. A part
// whose bytes moved while its surface did not was re-meshed, not changed. What moved is grouped
// into regions `--cell` mm apart, and each region is printed with a camera that frames it, the
// `render` line that draws it, and a `--section` through it for a change inside a part. The
// deviation is the reading; the camera is a starting point.
//
// `render` DRAWS ONE VIEW OF THE ENTRY. One browser, one page per picture, the /3d viewer as
// `render-step-posed.js` stands it, with the payload the page asks for answered from the stash
// rather than the tree: the request for `/meshes/<rel>.mesh` is fulfilled with the bytes given,
// so the model is drawn at its own path with everything the viewer keys off that path, and no
// file is put anywhere for it. Both pictures take one camera — computed once, here, off both
// versions — at one size, and the run fails if the two pages report different ones. Unaimed, it
// takes the camera `changed` gives the first region that moved; with nothing moved, it looks from
// the viewer's own front-right-above at the highlighted solids, or at everything shown.
//
// FEWER SOLIDS AND A CUT READ; SEE-THROUGH ONES DO NOT. The pictures are opaque. `--only` drops
// every other solid and hands the page a payload of just those, so a part-sized view costs a
// part's worth of parsing, and stands the part on no floor. `--section "x,y,z:nx,ny,nz"` cuts both pictures with one plane through
// that point and removes the side its normal points to, so a camera on that side looks at the cut;
// the cut faces are drawn filled in a flat section colour, a darker amber on a highlighted solid.
// Highlight is the viewer's selection amber, and `--highlight changed` is the solids `changed`
// stars. `--ghost` (a faint shell left out of the framing) and `--xray` (the viewer's see-through
// mode) are there for the view that cannot be had by hiding or cutting, and only for that.
//
// It writes `<view>-before.webp` and `<view>-after.webp` into the entry and merges the view into
// the entry's `views.json`, replacing a view of the same name; the first view is the one the feed
// shows. The page reads `name`, `caption`, `before`, `after`, `width`, `height` and `marks` —
// points in millimetres projected through the view's camera to pixels, drawn as a ring and a
// label over both pictures. The rest is what was drawn and from what: `model`, `camera`,
// `highlight`, `ghost`, `only`, `xray`, `source` (each payload's sha256 and the commit it stood
// at) and `changed` / `withinMeshing` (the solids that moved, as `changed` reads them); a section
// is recorded in `camera`.
//
// THIS DOES NOT EXTEND `render-step-posed.js`, AND IT DOES NOT LIVE BESIDE IT, BECAUSE BOTH OF
// THOSE ARE INPUTS TO THE BUILD. `render-step-posed.js` and `browser.js` are named in the
// installation-art and plumbing-scene rules, and `:node-packages` hands every file under
// tools/render/ to four rules more — so an edit there, or a new file, re-renders that art on
// whoever commits next. This file is no rule's input; it imports them.

import crypto from "crypto";
import fs from "fs";
import os from "os";
import path from "path";
import { execFileSync } from "child_process";
import { createRequire } from "module";
import { fileURLToPath } from "url";

import { closeBrowser, closeServer, consoleLine, finish, frameBuffer, launchBrowser, PARSE_TIMEOUT, sweepAbandonedBrowsers } from "../render/browser.js";

// sharp is installed beside the renderers it serves (tools/render/package.json), and resolved
// from there rather than installed a second time here.
const sharp = createRequire(new URL("../render/package.json", import.meta.url))("sharp");

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..", "..");
const HARDWARE = path.join(REPO_ROOT, "hardware");
const POINTERS = path.join(HARDWARE, "cad-artifacts.json");
const DEFAULT_MODEL = "manifold-layout/enclosure-assembly.step";

// The viewer's own selection colour (component-picker.js SEL), drawn at the finish the viz pages
// give a highlight (tools/viz/page.html).
const AMBER = 0xffa733;
// A cut face: the solid's own colour taken most of the way to a steel blue-grey, a hue no lit
// surface here has, so a cut never reads as a face that was there — a black shell cuts a mid
// blue-grey and a white body a pale one — and a highlighted solid cuts a darker amber.
const SECTION_TINT = 0x8fa6bd;
const SECTION_MIX = 0.7;
const SECTION_AMBER = 0xb8700f;
// What `_mesh_payload.py` meshes a model at: a ratio of the mean of its box's three extents.
// Two meshings of one surface stand within about this of each other.
const LINEAR_DEFLECTION_RATIO = 0.001;

// A refusal names what was asked wrongly; `main` prints it and exits 2. Thrown rather than exited
// on, so a browser or server already standing is closed by the `finally` that owns it.
class Refusal extends Error {}

function die(msg) {
  throw new Refusal(msg);
}

// --- arguments -------------------------------------------------------------------------------

const REPEATED = new Set(["model", "highlight", "ghost", "only", "mark"]);
const FLAGS = new Set(["ortho", "xray", "no-fog", "no-ground", "json"]);
const VALUES = new Set(["out", "before", "after", "tol", "cell", "top", "view", "caption", "cam", "target",
                        "up", "span", "zoom", "size", "section", "bg", "quality"]);

function parseArgs(argv) {
  const opts = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) { opts._.push(a); continue; }
    const eq = a.indexOf("=");
    const key = a.slice(2, eq < 0 ? undefined : eq);
    if (key === "solid") die("--solid is gone: the pictures are opaque unless --xray asks otherwise");
    if (FLAGS.has(key)) { opts[key] = true; continue; }
    if (!VALUES.has(key) && !REPEATED.has(key)) die(`unknown option --${key} (the header of tools/changes/change.mjs has the options)`);
    const val = eq < 0 ? argv[++i] : a.slice(eq + 1);
    if (val === undefined) die(`--${key} needs a value`);
    if (REPEATED.has(key)) (opts[key] ||= []).push(val);
    else opts[key] = val;
  }
  return opts;
}

function vec(s, name) {
  const parts = String(s).split(",").map(Number);
  if (parts.length !== 3 || parts.some((n) => !Number.isFinite(n))) die(`bad --${name}: ${s}`);
  return parts;
}

const names = (list) => (list || []).flatMap((s) => s.split(",")).map((s) => s.trim()).filter(Boolean);

function globs(list) {
  return names(list).map((p) => new RegExp(
    "^" + p.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".") + "$"));
}

const matchesAny = (res, name) => res.some((r) => r.test(name));

function modelOf(opts) {
  const rel = (opts.model && opts.model[opts.model.length - 1]) || DEFAULT_MODEL;
  if (rel.startsWith("hardware/") || path.isAbsolute(rel) || rel.includes(".."))
    die(`--model is a path under hardware/, as /3d names it: ${rel}`);
  return rel;
}

// --- payloads --------------------------------------------------------------------------------

const sha256 = (buf) => crypto.createHash("sha256").update(buf).digest("hex");

function git(...args) {
  try {
    return execFileSync("git", ["-C", REPO_ROOT, ...args], { encoding: "utf8" }).trim();
  } catch {
    return null;
  }
}

function pointed(rel) {
  try {
    return JSON.parse(fs.readFileSync(POINTERS, "utf8")).solids?.[`hardware/${rel}.mesh`] ?? null;
  } catch {
    return null;
  }
}

// The payload's own layout (`decodeMeshPayload` in web/public/js/viewer/step.js): a uint32 header
// length, the JSON header, then the arrays the header points into by byte offset and element
// count. A mesh's key is its name, numbered on a repeat, so two versions are compared solid for
// solid. Its body is the name the viewer stamps on it and the one every flag here matches.
function readPayload(file) {
  const buf = fs.readFileSync(file);
  const headLen = buf.readUInt32LE(0);
  let head;
  try {
    head = JSON.parse(buf.toString("utf8", 4, 4 + headLen));
  } catch {
    die(`${file}: not a viewer payload`);
  }
  if (!Array.isArray(head.meshes)) die(`${file}: not a viewer payload`);
  // Copied out, as the page does, so the typed arrays below stand on an aligned buffer.
  const blob = buf.buffer.slice(buf.byteOffset + 4 + headLen, buf.byteOffset + buf.length);
  const seen = new Map();
  const meshes = head.meshes.map((m) => {
    const name = m.name || "";
    const n = seen.get(name) || 0;
    seen.set(name, n + 1);
    const pos = new Float32Array(blob, m.pos[0], m.pos[1]);
    const idx = new Uint32Array(blob, m.idx[0], m.idx[1]);
    return {
      key: n ? `${name}#${n}` : name,
      name,
      body: name.replace(/\/\d+$/, ""),
      color: m.color || null,
      pos, idx,
      bytes: [Buffer.from(blob, m.pos[0], m.pos[1] * 4), Buffer.from(blob, m.idx[0], m.idx[1] * 4)],
      box: bounds(pos),
    };
  });
  return { file, buf, size: buf.length, sha256: sha256(buf), src: head.src || null, meshes };
}

function bounds(pos) {
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < pos.length; i += 3) {
    for (let a = 0; a < 3; a++) {
      const v = pos[i + a];
      if (v < min[a]) min[a] = v;
      if (v > max[a]) max[a] = v;
    }
  }
  return { min, max };
}

function union(boxes) {
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (const b of boxes) {
    for (let a = 0; a < 3; a++) {
      if (b.min[a] < min[a]) min[a] = b.min[a];
      if (b.max[a] > max[a]) max[a] = b.max[a];
    }
  }
  return { min, max };
}

const centre = (b) => [0, 1, 2].map((a) => (b.min[a] + b.max[a]) / 2);
const extent = (b) => [0, 1, 2].map((a) => b.max[a] - b.min[a]);

// Where a `--before` or `--after` points: a stash `snapshot` wrote, a payload file, or — for the
// after alone, and its default — the tree's own payload as it stands now. Read once, so the
// pictures and the record are of the same bytes whatever a build does to the tree meanwhile.
function resolveSide(where, rel, side) {
  if (!where || where === "tree") {
    if (side === "before") die("--before names the stash `snapshot` wrote before the change, or a payload file");
    const file = path.join(HARDWARE, `${rel}.mesh`);
    if (!fs.existsSync(file)) die(`the tree holds no payload for ${rel}: ${file}`);
    const p = readPayload(file);
    // /3d draws the payload whatever the STEP beside it says, so the picture is of the payload;
    // one cut from an older STEP is still the after, but not the after of the newest build.
    const step = path.join(HARDWARE, rel);
    if (p.src && fs.existsSync(step) && sha256(fs.readFileSync(step)) !== p.src)
      console.error(`change.mjs: the tree's ${rel}.mesh was cut from an older STEP than the one beside it`);
    return { ...p, commit: git("rev-parse", "HEAD"), from: "tree", published: pointed(rel) === p.sha256 };
  }
  const abs = path.resolve(where);
  if (!fs.existsSync(abs)) die(`--${side}: no such file or directory: ${where}`);
  if (fs.statSync(abs).isDirectory()) {
    const record = path.join(abs, "snapshot.json");
    if (!fs.existsSync(record)) die(`--${side}: ${where} is not a stash (no snapshot.json)`);
    const snap = JSON.parse(fs.readFileSync(record, "utf8"));
    const entry = snap.models?.[rel];
    if (!entry) die(`--${side}: the stash at ${where} holds no payload of ${rel} (it holds ${Object.keys(snap.models || {}).join(", ") || "none"})`);
    const p = readPayload(path.join(abs, entry.payload));
    if (p.sha256 !== entry.sha256) die(`--${side}: the stash's copy of ${rel} is not the bytes it recorded`);
    return { ...p, commit: snap.head, from: "snapshot", taken: snap.taken, published: entry.published };
  }
  const p = readPayload(abs);
  return { ...p, commit: null, from: "file", published: pointed(rel) === p.sha256 };
}

const sameMesh = (a, b) =>
  a.bytes[0].equals(b.bytes[0]) && a.bytes[1].equals(b.bytes[1]) &&
  JSON.stringify(a.color) === JSON.stringify(b.color);

// Solid for solid, by bytes: what each version holds that the other does not.
function byteDiff(before, after) {
  const was = new Map(before.meshes.map((m) => [m.key, m]));
  const now = new Map(after.meshes.map((m) => [m.key, m]));
  const changed = [], added = [], removed = [];
  for (const [key, m] of now) {
    const old = was.get(key);
    if (!old) added.push(m);
    else if (!sameMesh(old, m)) changed.push([old, m]);
  }
  for (const [key, m] of was) if (!now.has(key)) removed.push(m);
  return { changed, added, removed };
}

// The payload cut down to the solids `keep` names, laid out as `_mesh_payload.py` lays one out. A
// view drawn with `--only` hands the page this rather than the whole machine, so a part-sized
// picture costs a part's worth of parsing and edges instead of 1.3 million triangles'.
function subsetPayload(p, keep) {
  const buf = p.buf;
  const headLen = buf.readUInt32LE(0);
  const head = JSON.parse(buf.toString("utf8", 4, 4 + headLen));
  const base = 4 + headLen;
  const parts = [];
  let offset = 0;
  const meshes = [];
  head.meshes.forEach((m, i) => {
    if (!keep(p.meshes[i])) return;
    const out = { ...m };
    for (const field of ["pos", "nrm", "idx", "fac"]) {
      if (!Array.isArray(m[field])) continue;
      const [at, count] = m[field];
      parts.push(buf.subarray(base + at, base + at + count * 4));
      out[field] = [offset, count];
      offset += count * 4;
    }
    meshes.push(out);
  });
  const text = Buffer.from(JSON.stringify({ ...head, meshes }));
  const len = Buffer.alloc(4);
  len.writeUInt32LE(text.length, 0);
  return Buffer.concat([len, text, ...parts]);
}

// --- surface distance ------------------------------------------------------------------------

// Triangles in a bounding-volume tree, asked one question: how far is this point from the
// surface, once it is known to be further than `stop`. A point on the surface is answered by the
// first leaf it falls in; a point off it costs the walk to the nearest triangle, which is what
// says how far a region moved.
const LEAF = 8;

class Surface {
  constructor(pos, idx) {
    this.pos = pos;
    this.idx = idx;
    const T = (idx.length / 3) | 0;
    this.order = new Uint32Array(T);
    this.cen = new Float32Array(T * 3);
    for (let t = 0; t < T; t++) {
      this.order[t] = t;
      for (let a = 0; a < 3; a++) {
        this.cen[t * 3 + a] = (pos[idx[t * 3] * 3 + a] + pos[idx[t * 3 + 1] * 3 + a] + pos[idx[t * 3 + 2] * 3 + a]) / 3;
      }
    }
    const cap = Math.max(1, 2 * T);
    this.lo = new Float32Array(cap * 3);
    this.hi = new Float32Array(cap * 3);
    this.first = new Uint32Array(cap);
    this.count = new Uint32Array(cap);
    this.right = new Uint32Array(cap);
    this.next = 1;
    if (T) this.build(0, 0, T);
    this.stack = new Uint32Array(4096);
  }

  build(node, start, end) {
    const { pos, idx, order, cen } = this;
    const lo = [Infinity, Infinity, Infinity], hi = [-Infinity, -Infinity, -Infinity];
    const clo = [Infinity, Infinity, Infinity], chi = [-Infinity, -Infinity, -Infinity];
    for (let i = start; i < end; i++) {
      const t = order[i];
      for (let k = 0; k < 3; k++) {
        const v = idx[t * 3 + k] * 3;
        for (let a = 0; a < 3; a++) {
          const c = pos[v + a];
          if (c < lo[a]) lo[a] = c;
          if (c > hi[a]) hi[a] = c;
        }
      }
      for (let a = 0; a < 3; a++) {
        const c = cen[t * 3 + a];
        if (c < clo[a]) clo[a] = c;
        if (c > chi[a]) chi[a] = c;
      }
    }
    this.lo.set(lo, node * 3);
    this.hi.set(hi, node * 3);
    const n = end - start;
    if (n <= LEAF) {
      this.first[node] = start;
      this.count[node] = n;
      return;
    }
    let axis = 0;
    for (let a = 1; a < 3; a++) if (chi[a] - clo[a] > chi[axis] - clo[axis]) axis = a;
    const split = (clo[axis] + chi[axis]) / 2;
    let mid = start;
    for (let i = start; i < end; i++) {
      const t = order[i];
      if (cen[t * 3 + axis] < split) {
        order[i] = order[mid];
        order[mid] = t;
        mid++;
      }
    }
    // Every centroid on one side of the midpoint is a run of coincident ones: any split will do.
    if (mid === start || mid === end) mid = (start + end) >> 1;
    this.count[node] = 0;
    const left = this.next++;
    this.build(left, start, mid);
    const right = this.next++;
    this.right[node] = right;
    this.build(right, mid, end);
  }

  boxDist2(node, x, y, z) {
    const o = node * 3;
    const dx = Math.max(this.lo[o] - x, 0, x - this.hi[o]);
    const dy = Math.max(this.lo[o + 1] - y, 0, y - this.hi[o + 1]);
    const dz = Math.max(this.lo[o + 2] - z, 0, z - this.hi[o + 2]);
    return dx * dx + dy * dy + dz * dz;
  }

  // The squared distance to the nearest triangle, up to `limit2`; returns as soon as it is known
  // to be no more than `stop2`.
  dist2(x, y, z, limit2, stop2) {
    if (!this.order.length) return limit2;
    const { stack, pos, idx, order } = this;
    let best = limit2;
    let sp = 0;
    stack[sp++] = 0;
    while (sp) {
      const node = stack[--sp];
      if (this.boxDist2(node, x, y, z) >= best) continue;
      const n = this.count[node];
      if (n) {
        for (let i = this.first[node], e = i + n; i < e; i++) {
          const t = order[i];
          const a = idx[t * 3] * 3, b = idx[t * 3 + 1] * 3, c = idx[t * 3 + 2] * 3;
          const d = pointTriangle2(x, y, z, pos[a], pos[a + 1], pos[a + 2], pos[b], pos[b + 1], pos[b + 2], pos[c], pos[c + 1], pos[c + 2]);
          if (d < best) {
            best = d;
            if (best <= stop2) return best;
          }
        }
      } else if (sp + 2 <= stack.length) {
        const l = node + 1, r = this.right[node];
        if (this.boxDist2(l, x, y, z) < this.boxDist2(r, x, y, z)) {
          stack[sp++] = r;
          stack[sp++] = l;
        } else {
          stack[sp++] = l;
          stack[sp++] = r;
        }
      }
    }
    return best;
  }
}

// The closest point on a triangle (Ericson, Real-Time Collision Detection 5.1.5), as a squared
// distance. A triangle of no area falls through to its nearest corner.
function pointTriangle2(px, py, pz, ax, ay, az, bx, by, bz, cx, cy, cz) {
  const abx = bx - ax, aby = by - ay, abz = bz - az;
  const acx = cx - ax, acy = cy - ay, acz = cz - az;
  const apx = px - ax, apy = py - ay, apz = pz - az;
  const d1 = abx * apx + aby * apy + abz * apz, d2 = acx * apx + acy * apy + acz * apz;
  if (d1 <= 0 && d2 <= 0) return apx * apx + apy * apy + apz * apz;
  const bpx = px - bx, bpy = py - by, bpz = pz - bz;
  const d3 = abx * bpx + aby * bpy + abz * bpz, d4 = acx * bpx + acy * bpy + acz * bpz;
  if (d3 >= 0 && d4 <= d3) return bpx * bpx + bpy * bpy + bpz * bpz;
  const vc = d1 * d4 - d3 * d2;
  const at = (u, v, w) => {
    const qx = px - (ax * u + bx * v + cx * w), qy = py - (ay * u + by * v + cy * w), qz = pz - (az * u + bz * v + cz * w);
    return qx * qx + qy * qy + qz * qz;
  };
  if (vc <= 0 && d1 >= 0 && d3 <= 0) { const v = d1 / (d1 - d3); return at(1 - v, v, 0); }
  const cpx = px - cx, cpy = py - cy, cpz = pz - cz;
  const d5 = abx * cpx + aby * cpy + abz * cpz, d6 = acx * cpx + acy * cpy + acz * cpz;
  if (d6 >= 0 && d5 <= d6) return cpx * cpx + cpy * cpy + cpz * cpz;
  const vb = d5 * d2 - d1 * d6;
  if (vb <= 0 && d2 >= 0 && d6 <= 0) { const w = d2 / (d2 - d6); return at(1 - w, 0, w); }
  const va = d3 * d6 - d5 * d4;
  if (va <= 0 && d4 - d3 >= 0 && d5 - d6 >= 0) { const w = (d4 - d3) / ((d4 - d3) + (d5 - d6)); return at(0, 1 - w, w); }
  const denom = 1 / (va + vb + vc);
  const d = at(1 - (vb + vc) * denom, vb * denom, vc * denom);
  if (Number.isFinite(d)) return d;
  return Math.min(apx * apx + apy * apy + apz * apz, bpx * bpx + bpy * bpy + bpz * bpz, cpx * cpx + cpy * cpy + cpz * cpz);
}

// Every vertex of `from` that stands further than `tol` off the surface of `onto`, with how far.
const FAR = 200; // mm: past this a vertex is simply somewhere the other version is not

function deviating(from, onto, tol, side, out) {
  const surface = new Surface(onto.pos, onto.idx);
  const tol2 = tol * tol;
  const pos = from.pos;
  let moved = 0;
  for (let i = 0; i < pos.length; i += 3) {
    const d2 = surface.dist2(pos[i], pos[i + 1], pos[i + 2], FAR * FAR, tol2);
    if (d2 > tol2) {
      out.push({ x: pos[i], y: pos[i + 1], z: pos[i + 2], d: Math.sqrt(d2), side, body: from.body });
      moved++;
    }
  }
  return moved;
}

// Points grouped into regions: cells of `cell` mm, joined where they touch, a region's box the
// box of its own points.
function regions(points, cell) {
  const cells = new Map();
  for (const p of points) {
    const key = `${Math.floor(p.x / cell)},${Math.floor(p.y / cell)},${Math.floor(p.z / cell)}`;
    let c = cells.get(key);
    if (!c) cells.set(key, (c = []));
    c.push(p);
  }
  const done = new Set();
  const out = [];
  for (const start of cells.keys()) {
    if (done.has(start)) continue;
    done.add(start);
    const queue = [start];
    const pts = [];
    while (queue.length) {
      const key = queue.pop();
      for (const p of cells.get(key)) pts.push(p);
      const [i, j, k] = key.split(",").map(Number);
      for (let di = -1; di <= 1; di++) for (let dj = -1; dj <= 1; dj++) for (let dk = -1; dk <= 1; dk++) {
        const n = `${i + di},${j + dj},${k + dk}`;
        if (cells.has(n) && !done.has(n)) {
          done.add(n);
          queue.push(n);
        }
      }
    }
    const box = { min: [Infinity, Infinity, Infinity], max: [-Infinity, -Infinity, -Infinity] };
    let dmax = 0, nb = 0, na = 0;
    const bodies = new Set();
    for (const p of pts) {
      const v = [p.x, p.y, p.z];
      for (let a = 0; a < 3; a++) {
        if (v[a] < box.min[a]) box.min[a] = v[a];
        if (v[a] > box.max[a]) box.max[a] = v[a];
      }
      if (p.d > dmax) dmax = p.d;
      if (p.side === "before") nb++; else na++;
      bodies.add(p.body);
    }
    out.push({ box, dmax, before: nb, after: na, bodies: [...bodies].sort() });
  }
  return out.sort((a, b) => b.dmax - a.dmax || (b.before + b.after) - (a.before + a.after));
}

const round = (v, q = 0.1) => Math.round(v / q) * q;
const fmt = (v) => String(+round(v).toFixed(1));
const fmtv = (v) => v.map(fmt).join(",");

// A camera on a region: aimed at its centre, from outside the machine on the region's side, a
// quarter of the way round toward the viewer's own front-right-above, so a face is never met
// square on. Span is the frame's half-height at the target: the region fills about half the
// frame, so what is round it says where in the machine it is.
function cameraFor(box, model) {
  const c = centre(box);
  const m = centre(model);
  const out = c.map((v, a) => v - m[a]);
  const len = Math.hypot(...out);
  const radius = Math.max(...extent(model)) / 2;
  const iso = [1, -1, 1].map((v) => v / Math.sqrt(3));
  let dir = len < radius * 0.1 ? iso : out.map((v, a) => 0.75 * (v / len) + 0.25 * iso[a]);
  const n = Math.hypot(...dir);
  dir = dir.map((v) => v / n);
  const up = Math.abs(dir[2]) > 0.95 ? [0, 1, 0] : [0, 0, 1];
  const span = Math.max(15, Math.hypot(...extent(box)));
  return { target: c, cam: dir, up, span };
}

// --- snapshot --------------------------------------------------------------------------------

function snapshot(opts) {
  const rels = opts.model?.length ? opts.model : [DEFAULT_MODEL];
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\..*/, "").replace("T", "-");
  const out = path.resolve(opts.out || path.join(os.tmpdir(), "hsm-changes", stamp));
  const inside = path.relative(REPO_ROOT, out);
  if (!inside.startsWith("..") && !path.isAbsolute(inside))
    die(`a stash goes outside the tree, not into ${out} (the session scratchpad or $TMPDIR)`);
  const head = git("rev-parse", "HEAD");
  const models = {};
  for (const rel of rels) {
    if (rel.startsWith("hardware/") || path.isAbsolute(rel) || rel.includes(".."))
      die(`--model is a path under hardware/, as /3d names it: ${rel}`);
    const src = path.join(HARDWARE, `${rel}.mesh`);
    if (!fs.existsSync(src)) die(`the tree holds no payload for ${rel}: ${src}`);
    const buf = fs.readFileSync(src);
    const dest = path.join(out, `${rel}.mesh`);
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.writeFileSync(dest, buf);
    const sha = sha256(buf);
    const headLen = buf.readUInt32LE(0);
    const meshSrc = JSON.parse(buf.toString("utf8", 4, 4 + headLen)).src || null;
    // A payload cut from an older STEP than the one beside it is still what /3d draws, and says so.
    let current = null;
    const step = path.join(HARDWARE, rel);
    if (meshSrc && fs.existsSync(step)) current = sha256(fs.readFileSync(step)) === meshSrc;
    models[rel] = { payload: `${rel}.mesh`, sha256: sha, bytes: buf.length, src: meshSrc,
                    stepCurrent: current, published: pointed(rel) === sha };
    console.log(`  ${rel}.mesh  ${(buf.length / 1e6).toFixed(1)} MB  sha256 ${sha.slice(0, 12)}` +
      `${models[rel].published ? "  (the bytes main's pointer file names)" : ""}` +
      `${current === false ? "  (cut from an older STEP than the tree's)" : ""}`);
  }
  fs.writeFileSync(path.join(out, "snapshot.json"),
    JSON.stringify({ taken: new Date().toISOString(), head, models }, null, 2) + "\n");
  console.log(`snapshot ${out}`);
}

// --- changed ---------------------------------------------------------------------------------

// The comparison both `changed` and `render` stand on: every solid whose bytes differ, how far its
// surface moved, and where.
function analyse(before, after, { tol = 0.05, cell = 8 } = {}) {
  const diff = byteDiff(before, after);
  const points = [];
  const bodies = new Map();
  const note = (body, field) => {
    const b = bodies.get(body) || { body, changed: 0, added: 0, removed: 0, moved: 0, dmax: 0, vertices: 0, boxes: [] };
    b[field] += 1;
    bodies.set(body, b);
    return b;
  };
  const recoloured = new Set();
  for (const [old, now] of diff.changed) {
    if (old.bytes[0].equals(now.bytes[0]) && old.bytes[1].equals(now.bytes[1])) {
      recoloured.add(now.body);
      continue;
    }
    const from = points.length;
    const b = note(now.body, "changed");
    b.moved += deviating(now, old, tol, "after", points) + deviating(old, now, tol, "before", points);
    for (let i = from; i < points.length; i++) if (points[i].d > b.dmax) b.dmax = points[i].d;
    b.vertices += (now.pos.length + old.pos.length) / 3;
    b.boxes.push(old.box, now.box);
  }
  for (const [list, side, field] of [[diff.added, "after", "added"], [diff.removed, "before", "removed"]]) {
    for (const m of list) {
      for (let i = 0; i < m.pos.length; i += 3) points.push({ x: m.pos[i], y: m.pos[i + 1], z: m.pos[i + 2], d: FAR, side, body: m.body });
      const b = note(m.body, field);
      b.moved += m.pos.length / 3;
      b.dmax = FAR;
      b.vertices += m.pos.length / 3;
      b.boxes.push(m.box);
    }
  }

  // WHAT A RE-MESHING ALONE MOVES. Each version is meshed at a tolerance off its own box, so two
  // meshings of one unchanged surface stand up to about that far apart, and a model whose box
  // grew or shrank is re-meshed everywhere at once. A move past twice the larger of the two is
  // the part; one inside it may be the part or may be the mesh, and is listed as such.
  const meshing = (p) => LINEAR_DEFLECTION_RATIO * extent(union(p.meshes.map((m) => m.box))).reduce((s, v) => s + v, 0) / 3;
  const deflection = Math.max(meshing(before), meshing(after));
  const clear = (d) => d > 2 * deflection;
  const model = union([...before.meshes, ...after.meshes].map((m) => m.box));
  const found = regions(points, cell)
    .sort((a, b) => clear(b.dmax) - clear(a.dmax) || (b.before + b.after) - (a.before + a.after))
    .map((r, i) => ({ name: `region-${i + 1}`, ...r, clear: clear(r.dmax), camera: cameraFor(r.box, model) }));
  const list = [...bodies.values()].sort((a, b) => b.dmax - a.dmax || b.moved - a.moved || a.body.localeCompare(b.body));
  return {
    list, found, recoloured, deflection, clear,
    meshing: [meshing(before), meshing(after)],
    moved: list.filter((b) => clear(b.dmax)),
    near: list.filter((b) => b.moved && !clear(b.dmax)),
    remeshed: list.filter((b) => !b.moved),
  };
}

function changed(opts) {
  const rel = modelOf(opts);
  const before = resolveSide(opts.before, rel, "before");
  const after = resolveSide(opts.after, rel, "after");
  const tol = Number(opts.tol ?? 0.05);
  const cell = Number(opts.cell ?? 8);
  const top = Number(opts.top ?? 6);
  if (!(tol > 0) || !(cell > 0) || !(top > 0)) die("--tol, --cell and --top are positive numbers");
  const { list, found, recoloured, deflection, clear, meshing, moved, near, remeshed } = analyse(before, after, { tol, cell });

  const quote = (s) => (/^[\w./:@%+-]+$/.test(s) ? s : `'${s.replace(/'/g, "'\\''")}'`);
  const sideArg = (side, where) => (where && where !== "tree" ? ` --${side} ${quote(path.resolve(where))}` : "");
  const command = (r) => `node tools/changes/change.mjs render changes/<id> --view <name>` +
    sideArg("before", opts.before) + sideArg("after", opts.after) +
    (rel !== DEFAULT_MODEL ? ` --model ${rel}` : "") +
    ` --target ${fmtv(r.camera.target)} --cam ${r.camera.cam.map((v) => v.toFixed(3)).join(",")}` +
    ` --up ${r.camera.up.join(",")} --span ${fmt(r.camera.span)} --highlight ${quote(r.bodies.join(","))}`;
  // A cut for a change inside a part: through the region's centre, square to the machine axis
  // nearest the camera's direction, removing the half the camera stands in.
  const sectionFor = (r) => {
    const d = r.camera.cam;
    let a = 0;
    for (let i = 1; i < 3; i++) if (Math.abs(d[i]) > Math.abs(d[a])) a = i;
    const n = [0, 0, 0];
    n[a] = Math.sign(d[a]) || 1;
    return `${fmtv(centre(r.box))}:${n.join(",")}`;
  };

  if (opts.json) {
    console.log(JSON.stringify({
      model: rel, tol, cell, meshing: deflection,
      before: { file: before.file, sha256: before.sha256, commit: before.commit },
      after: { file: after.file, sha256: after.sha256, commit: after.commit },
      bodies: list.map(({ boxes, ...b }) => ({ ...b, clear: clear(b.dmax), box: union(boxes) })),
      recoloured: [...recoloured].sort(),
      regions: found.map((r) => ({ ...r, render: command(r), section: sectionFor(r) })),
    }, null, 2));
    return;
  }

  const shownPath = (f) => { const r = path.relative(process.cwd(), f); return r.startsWith("..") ? f : r; };
  const said = (p) => `${shownPath(p.file)}  sha256 ${p.sha256.slice(0, 12)}` +
    `${p.commit ? `  at ${p.commit.slice(0, 9)}` : ""}${p.published ? "  (published)" : ""}`;
  const dist = (d) => (d >= FAR ? "added or removed" : `${fmt(d)} mm`);
  console.log(`before  ${said(before)}`);
  console.log(`after   ${said(after)}`);
  if (!list.length && !recoloured.size) {
    console.log(`\nno solid differs: the two payloads draw the same ${after.meshes.length} meshes`);
    return;
  }
  console.log(`\nmeshing tolerance about ${fmt(deflection)} mm` +
    (Math.abs(meshing[0] - meshing[1]) > deflection * 0.01
      ? ` (the model's box changed, so every solid is meshed afresh: ${fmt(meshing[0])} mm before, ${fmt(meshing[1])} mm after)` : ""));
  console.log(`${moved.length} solid(s) moved more than twice that; ${near.length} within it, part or mesh; ` +
    `${remeshed.length} re-meshed on the same surface${recoloured.size ? `; ${recoloured.size} recoloured` : ""}`);
  for (const b of [...moved, ...near]) {
    const box = union(b.boxes);
    const kind = b.added ? "added" : b.removed ? "removed" : "changed";
    console.log(`  ${clear(b.dmax) ? "*" : " "} ${b.body.padEnd(36)} ${kind.padEnd(8)} up to ${dist(b.dmax).padEnd(17)}` +
      `${String(b.moved).padStart(7)} of ${b.vertices} vertices   solid ${fmtv(box.min)} .. ${fmtv(box.max)}`);
  }
  if (remeshed.length) console.log(`  re-meshed, same surface: ${remeshed.map((b) => b.body).join(", ")}`);
  if (recoloured.size) console.log(`  recoloured, same triangles: ${[...recoloured].sort().join(", ")}`);
  if (!found.length) return;
  const sure = found.filter((r) => r.clear);
  console.log(`\n${found.length} region(s), ${sure.length} past twice the meshing tolerance, those first:`);
  for (const r of found.slice(0, top)) {
    const size = extent(r.box);
    console.log(`\n  ${r.name}  ${r.bodies.join(", ")}${r.clear ? "" : "  (within twice the meshing tolerance: may be the mesh alone)"}`);
    console.log(`    centre ${fmtv(centre(r.box))}  size ${size.map(fmt).join(" x ")} mm` +
      `  moved up to ${dist(r.dmax)}  (${r.before} before / ${r.after} after vertices)`);
    console.log(`    ${command(r)}`);
    console.log(`    inside a part, add a cut through it facing the camera: --section ${sectionFor(r)}`);
  }
  if (found.length > top) console.log(`\n  ... and ${found.length - top} more (--top ${found.length} lists them)`);
}

// --- render ----------------------------------------------------------------------------------

// `x,y,z:nx,ny,nz`: a plane through that point, in millimetres, with that normal. What the normal
// points into is cut away.
function parseSection(s) {
  if (s == null) return null;
  const m = String(s).match(/^([^:]+):([^:]+)$/);
  const at = m && m[1].split(",").map((v) => Number(v.trim()));
  const n = m && m[2].split(",").map((v) => Number(v.trim()));
  if (!m || at.length !== 3 || n.length !== 3 || [...at, ...n].some((v) => !Number.isFinite(v)) || !Math.hypot(...n))
    die(`bad --section: ${s} (x,y,z:nx,ny,nz — a point in mm and the normal of the side to cut away)`);
  const len = Math.hypot(...n);
  return { at, normal: n.map((v) => +(v / len).toFixed(6)) };
}

// `x,y,z`, `x,y,z:label` or `x,y,z,r:label`, in millimetres. A radius is the ring's, measured at
// the point and drawn at whatever that comes to in pixels; without one the page sizes the ring.
function parseMarks(list) {
  return (list || []).map((s) => {
    const m = String(s).match(/^([^:]*)(?::(.*))?$/);
    const nums = m[1].split(",").map((v) => Number(v.trim()));
    if ((nums.length !== 3 && nums.length !== 4) || nums.some((v) => !Number.isFinite(v)) || nums[3] <= 0)
      die(`bad --mark: ${s} (x,y,z, x,y,z:label or x,y,z,r:label, in mm)`);
    return { at: nums.slice(0, 3), rmm: nums[3] ?? null, label: m[2] ? m[2].trim() : null };
  });
}

// One picture, composed the way `render-step-posed.js` composes its frame (its `shoot`), with the
// camera handed in rather than fitted off the subject: both pictures of a view take the same one.
async function shoot(page, o) {
  return page.evaluate(async (o) => {
    const hsm = window.__hsm;
    const { THREE, renderer, scene, camera, controls, currentGroup } = hsm;
    const sceneMod = await import("/js/viewer/scene.js");
    const xray = await import("/js/viewer/xray.js");
    // No await below this line: scene.js's animate loop refits fog and edge resolution whenever
    // the task loop is handed back, so the frame is composed in one task (render-step-posed.js).
    sceneMod.stopAnimate();
    sceneMod.resetCamera(currentGroup);
    controls.enabled = false;
    if (!o.fog) scene.fog = null;
    if (!o.ground) sceneMod.fitGroundShadow(null);
    if (xray.isXrayEnabled() !== !!o.xray) xray.setXrayEnabled(!!o.xray, { persist: false });

    const re = (list) => list.map((s) => new RegExp(s));
    const only = re(o.only), ghost = re(o.ghost), hi = re(o.highlight);
    const any = (res, name) => res.some((r) => r.test(name));
    const edges = new Map();
    currentGroup.traverse((c) => { if (c.userData?.isXrayEdge && c.userData.sourceMesh) edges.set(c.userData.sourceMesh, c); });
    const amber = new THREE.MeshStandardMaterial({
      color: o.amber, roughness: 0.5, metalness: 0.05, side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    });
    const counts = { solids: 0, shown: 0, highlighted: 0, ghosted: 0 };
    for (const mesh of currentGroup.children) {
      if (!mesh.isMesh || mesh.userData?.isXrayEdge) continue;
      counts.solids++;
      const name = mesh.name || "";
      const line = edges.get(mesh);
      if (only.length && !any(only, name)) {
        mesh.visible = false;
        if (line) line.visible = false;
        continue;
      }
      if (mesh.visible === false) continue;
      counts.shown++;
      if (any(hi, name)) {
        mesh.material = amber;
        mesh.userData.highlighted = true;
        counts.highlighted++;
      } else if (any(ghost, name)) {
        const base = mesh.userData.baseMaterial || mesh.material;
        const shell = (Array.isArray(base) ? base[0] : base).clone();
        shell.transparent = true;
        shell.opacity = 0.16;
        shell.depthWrite = false;
        mesh.material = shell;
        if (line) line.visible = false;
        counts.ghosted++;
      }
    }

    // THE CUT IS A CLIP AND A CAP. Every material drawn is clipped by the one plane, and each opaque
    // solid draws its front faces only, with a second pass over the same triangles drawing their
    // back faces flat in the section colour under the same clip. Where the plane opens a solid,
    // what shows through the opening is the inside of its far walls — that pass — so the cut reads
    // as a filled face; a passage the plane opens shows its own walls, lit, because those face the
    // viewer. A see-through solid is clipped and not capped: its back faces show everywhere.
    if (o.section) {
      const n = new THREE.Vector3(...o.section.normal);
      const plane = new THREE.Plane(n.clone().negate(), n.dot(new THREE.Vector3(...o.section.at)));
      renderer.localClippingEnabled = true;
      const caps = [];
      for (const mesh of [...currentGroup.children]) {
        if (!mesh.isMesh || mesh.visible === false) continue;
        const list = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
        if (mesh.userData?.isXrayEdge) {
          // LineMaterial's clipping chunk compiles only without alpha-to-coverage (three 0.170).
          for (const m of list) { m.clippingPlanes = [plane]; m.alphaToCoverage = false; m.needsUpdate = true; }
          continue;
        }
        const cut = list.map((m) => {
          const c = m.clone();
          c.clippingPlanes = [plane];
          if (!c.transparent) c.side = THREE.FrontSide;
          return c;
        });
        mesh.material = Array.isArray(mesh.material) ? cut : cut[0];
        if (cut.some((m) => m.transparent)) continue;
        const colour = mesh.userData.highlighted ? new THREE.Color(o.sectionAmber)
          : (cut[0].color ? cut[0].color.clone() : new THREE.Color(0x8899aa)).lerp(new THREE.Color(o.sectionTint), o.sectionMix);
        const cap = new THREE.Mesh(mesh.geometry, new THREE.MeshBasicMaterial({ color: colour, side: THREE.BackSide, clippingPlanes: [plane] }));
        cap.position.copy(mesh.position);
        cap.quaternion.copy(mesh.quaternion);
        cap.scale.copy(mesh.scale);
        cap.userData.sectionCap = true;
        caps.push(cap);
      }
      for (const cap of caps) currentGroup.add(cap);
      counts.capped = caps.length;
    }

    const target = new THREE.Vector3(...o.target);
    const dir = new THREE.Vector3(...o.cam).normalize();
    const aspect = o.width / o.height;
    let cam;
    if (o.ortho) {
      cam = new THREE.OrthographicCamera(-o.half * aspect, o.half * aspect, o.half, -o.half, 0.01, o.wholeRadius * 100);
      cam.position.copy(target).addScaledVector(dir, o.wholeRadius * 3);
    } else {
      cam = camera;
      cam.aspect = aspect;
      const dist = o.span != null ? o.span / Math.tan(THREE.MathUtils.degToRad(cam.fov / 2)) : o.radius * o.zoom;
      cam.position.copy(target).addScaledVector(dir, dist);
    }
    cam.up.set(...o.up);
    cam.lookAt(target);
    controls.object = cam;
    controls.target.copy(target);
    renderer.setSize(window.innerWidth, window.innerHeight, false);
    xray.syncEdgeResolution(renderer);
    sceneMod.fitCameraDepth(cam, new THREE.Vector3(...o.wholeCentre), o.wholeRadius);
    cam.updateProjectionMatrix();
    cam.updateMatrixWorld(true);

    const px = (p) => {
      const v = p.clone().project(cam);
      return { x: (v.x + 1) / 2 * o.width, y: (1 - v.y) / 2 * o.height, z: v.z };
    };
    const screenUp = new THREE.Vector3(0, 1, 0).applyQuaternion(cam.quaternion);
    const marks = o.marks.map(({ at, rmm, label }) => {
      const p = new THREE.Vector3(...at);
      const c = px(p);
      const r = rmm ? Math.hypot(...(({ x, y }) => [x - c.x, y - c.y])(px(p.clone().addScaledVector(screenUp, rmm)))) : null;
      return { at, label, r, x: c.x, y: c.y, inFront: c.z > -1 && c.z < 1 };
    });
    const drawn = {
      projection: o.ortho ? "orthographic" : "perspective",
      position: cam.position.toArray(), target: target.toArray(), up: cam.up.toArray(),
      ...(o.ortho ? { half: o.half } : { fov: cam.fov }),
      near: cam.near, far: cam.far, aspect,
      ...(o.section ? { section: { at: o.section.at, normal: o.section.normal, removes: "the side the normal points to" } } : {}),
    };

    renderer.setClearColor(o.bg, 1);
    renderer.render(scene, cam);
    const png = renderer.domElement.toDataURL("image/png");
    return { png, drawn, marks, counts };
  }, o);
}

// A page with the viewer up and `rel` mounted from `payload`. The page asks for the model's bytes
// at `/meshes/<rel>.mesh`, and that request is answered here; every other request goes to the
// server but two. `/api/objects` would send the page to the store for the tree's member instead.
// `/api/steps` lists the models the grid behind the detail draws a card for, and the machine's
// card parses the same payload again to draw itself — twice the memory, for a picture nobody takes.
const EMPTY = { "/api/objects": { base: null, objects: {} }, "/api/steps": [] };
async function openViewer(browser, port, rel, payload, size) {
  const page = await browser.newPage();
  await page.setViewport({ width: size.width, height: size.height, deviceScaleFactor: 1 });
  page.__errors = [];
  page.on("pageerror", (err) => page.__errors.push(err.message || String(err)));
  page.on("console", (msg) => {
    const line = consoleLine(msg);
    if (line) console.error(line);
  });
  const client = await page.createCDPSession();
  const body = payload.toString("base64");
  const want = `/meshes/${rel}.mesh`;
  let served = 0;
  client.on("Fetch.requestPaused", async (ev) => {
    const where = decodeURIComponent(new URL(ev.request.url).pathname);
    try {
      if (where === want) {
        served++;
        await client.send("Fetch.fulfillRequest", {
          requestId: ev.requestId, responseCode: 200, body,
          responseHeaders: [{ name: "Content-Type", value: "application/octet-stream" }, { name: "Cache-Control", value: "no-store" }],
        });
      } else if (where in EMPTY) {
        await client.send("Fetch.fulfillRequest", {
          requestId: ev.requestId, responseCode: 200,
          body: Buffer.from(JSON.stringify(EMPTY[where])).toString("base64"),
          responseHeaders: [{ name: "Content-Type", value: "application/json" }, { name: "Cache-Control", value: "no-store" }],
        });
      } else {
        await client.send("Fetch.continueRequest", { requestId: ev.requestId });
      }
    } catch (err) {
      page.__errors.push(`answering ${where}: ${err.message}`);
    }
  });
  await client.send("Fetch.enable", { patterns: [
    { urlPattern: `*${want}*`, requestStage: "Request" },
    ...Object.keys(EMPTY).map((p) => ({ urlPattern: `*${p}*`, requestStage: "Request" })),
  ] });

  const url = `http://localhost:${port}/3d?file=${encodeURIComponent(rel)}`;
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForFunction(() => window.__hsm && window.__hsm.scene && window.__hsm.camera, { timeout: 120000 });
  try {
    await page.waitForFunction((r) => window.__hsm.mountedStepFile === r, { timeout: 300000 }, rel);
  } catch (err) {
    throw new Error(`the viewer did not mount ${rel}${page.__errors.length ? `: ${page.__errors.join("; ")}` : ""}`);
  }
  if (!served) throw new Error(`the page drew ${rel} without asking for the payload handed to it`);
  page.__served = () => served;
  return page;
}

function readViews(file) {
  if (!fs.existsSync(file)) return { views: [] };
  const v = JSON.parse(fs.readFileSync(file, "utf8"));
  if (!Array.isArray(v.views)) die(`${file} holds no views array`);
  return v;
}

// What each picture was drawn from, by hash and by the commit it stood at. A stash's own path is
// scratch and means nothing once the session is gone, so it is not kept.
const source = (p, rel) => ({
  payload: `${rel}.mesh`,
  from: p.from,
  sha256: p.sha256,
  commit: p.commit,
  ...(p.taken ? { taken: p.taken } : {}),
  ...(p.from === "file" ? {} : { published: !!p.published }),
});

async function render(opts) {
  const [entryArg] = opts._;
  if (!entryArg) die("render needs the entry directory: changes/<id>");
  const view = opts.view;
  if (!view || !/^[a-z0-9][a-z0-9-]*$/.test(view)) die("--view names the view: lowercase letters, digits and hyphens");
  const rel = modelOf(opts);
  const entry = path.resolve(entryArg);
  const before = resolveSide(opts.before, rel, "before");
  const after = resolveSide(opts.after, rel, "after");

  const sizeMatch = String(opts.size || "1200x900").match(/^(\d+)x(\d+)$/);
  if (!sizeMatch) die(`bad --size: ${opts.size}`);
  const size = { width: Number(sizeMatch[1]), height: Number(sizeMatch[2]) };
  const quality = Number(opts.quality ?? 82);
  // `changed` in --highlight is what `changed` stars: the solids whose surface moved past twice the
  // meshing tolerance, or, where none did, the ones that moved at all.
  const analysis = analyse(before, after);
  const moved = analysis.moved.map((b) => b.body);
  const near = analysis.near.map((b) => b.body);
  const wanted = names(opts.highlight);
  if (wanted.includes("changed") && !moved.length && !near.length)
    die("--highlight changed: no solid's surface moved between the two payloads");
  const highlightNames = wanted.flatMap((n) => (n === "changed" ? (moved.length ? moved : near) : [n]));
  const only = globs(opts.only), ghost = globs(opts.ghost), hi = globs(highlightNames);

  // THE CAMERA IS SETTLED HERE, ONCE, OFF BOTH VERSIONS. Framed off either picture alone, a
  // solid that grew would move the target between them, and a difference in the frame would
  // read as a difference in the part.
  const all = [...before.meshes, ...after.meshes];
  const kept = (m) => !only.length || matchesAny(only, m.body);
  const shown = all.filter(kept);
  if (!shown.length) die("nothing to draw: --only matched no solid");
  const subject = hi.length ? shown.filter((m) => matchesAny(hi, m.body)) : shown.filter((m) => !matchesAny(ghost, m.body));
  const frame = union((subject.length ? subject : shown).map((m) => m.box));
  const whole = union(shown.map((m) => m.box));
  const radius = Math.max(...extent(frame)) / 2;
  // UNAIMED, IT LOOKS AT WHAT MOVED. A view given no target, direction, span or zoom takes the
  // camera `changed` prints for the first region that moved among the solids shown; with nothing
  // moved, it looks from the viewer's own front-right-above at the subject.
  const aimed = ["target", "cam", "up", "span", "zoom"].some((k) => opts[k] != null);
  const region = aimed ? null : analysis.found.find((r) => r.bodies.some((b) => shown.some((m) => m.body === b)));
  if (region) console.log(`  aimed at ${region.name}: ${region.bodies.join(", ")}, moved up to ${fmt(region.dmax)} mm` +
    ` (--target ${fmtv(region.camera.target)} --cam ${region.camera.cam.map((v) => v.toFixed(3)).join(",")} --span ${fmt(region.camera.span)})`);
  const span = opts.span != null ? Number(opts.span) : region ? region.camera.span : null;
  const zoom = Number(opts.zoom ?? 3);
  if (span != null && !(span > 0)) die(`bad --span: ${opts.span}`);
  if (!(zoom > 0)) die(`bad --zoom: ${opts.zoom}`);
  const o = {
    width: size.width, height: size.height,
    cam: opts.cam ? vec(opts.cam, "cam") : region ? region.camera.cam : [1, -1, 1],
    target: opts.target ? vec(opts.target, "target") : region ? region.camera.target : centre(frame),
    up: opts.up ? vec(opts.up, "up") : region ? region.camera.up : [0, 0, 1],
    ortho: !!opts.ortho, span, zoom, radius,
    half: span ?? radius * 1.1,
    wholeCentre: centre(whole), wholeRadius: Math.hypot(...extent(whole)) / 2,
    // The floor's contact shadow is the machine standing on something; a part pulled out of it with
    // --only stands on nothing, and the shadow under it is a dark blot in a close-up.
    xray: !!opts.xray, fog: !opts["no-fog"], ground: !opts["no-ground"] && !only.length,
    bg: opts.bg || "#1a1a2e", amber: AMBER,
    section: parseSection(opts.section),
    sectionTint: SECTION_TINT, sectionMix: SECTION_MIX, sectionAmber: SECTION_AMBER,
    only: only.map((r) => r.source), ghost: ghost.map((r) => r.source), highlight: hi.map((r) => r.source),
    marks: parseMarks(opts.mark),
  };
  if (hi.length && !all.some((m) => matchesAny(hi, m.body))) die(`--highlight matched no solid: ${highlightNames.join(", ")}`);

  await sweepAbandonedBrowsers("change.mjs");
  const { start } = await import("../../web/server.js");
  const { server } = await start({ port: 0, dev: false, hardwareDir: HARDWARE });
  const port = server.address().port;
  let browser;
  const shots = {};
  try {
    browser = await launchBrowser({ protocolTimeout: PARSE_TIMEOUT + 60000 });
    for (const [side, p] of [["before", before], ["after", after]]) {
      const t0 = Date.now();
      const bytes = only.length ? subsetPayload(p, kept) : p.buf;
      const page = await openViewer(browser, port, rel, bytes, size);
      try {
        const shot = await shoot(page, o);
        if (page.__errors.length) throw new Error(`the viewer threw drawing the ${side}: ${page.__errors.join("; ")}`);
        shots[side] = shot;
        console.log(`  ${side}: ${shot.counts.shown} of ${shot.counts.solids} solids shown, ` +
          `${shot.counts.highlighted} highlighted, ${shot.counts.ghosted} ghosted` +
          `${o.section ? `, ${shot.counts.capped} cut by the section` : ""}; payload ${(bytes.length / 1e6).toFixed(1)} MB ` +
          `asked for ${page.__served()}x (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
      } finally {
        await page.close().catch(() => {});
      }
    }
  } finally {
    await closeBrowser(browser);
    await closeServer(server);
  }

  const a = shots.before.drawn, b = shots.after.drawn;
  const same = ["position", "target", "up"].every((k) => a[k].every((v, i) => Math.abs(v - b[k][i]) < 1e-6)) &&
    a.near === b.near && a.far === b.far && a.fov === b.fov && a.half === b.half &&
    JSON.stringify(a.section) === JSON.stringify(b.section);
  if (!same) die(`the two pictures were not drawn from one camera:\n  before ${JSON.stringify(a)}\n  after  ${JSON.stringify(b)}`);

  fs.mkdirSync(entry, { recursive: true });
  const files = {};
  for (const side of ["before", "after"]) {
    const name = `${view}-${side}.webp`;
    const webp = await sharp(frameBuffer(shots[side].png)).webp({ quality }).toBuffer();
    fs.writeFileSync(path.join(entry, name), webp);
    files[side] = name;
    console.log(`wrote ${path.join(entry, name)} (${size.width}x${size.height}, ${(webp.length / 1024).toFixed(0)} KB)`);
  }
  const marks = [];
  for (const m of shots.after.marks) {
    const inFrame = m.inFront && m.x >= 0 && m.x <= size.width && m.y >= 0 && m.y <= size.height;
    if (!inFrame) {
      console.error(`  mark ${fmtv(m.at)}${m.label ? ` (${m.label})` : ""} falls outside the picture and is left out`);
      continue;
    }
    marks.push({ x: +m.x.toFixed(1), y: +m.y.toFixed(1), ...(m.r ? { r: +m.r.toFixed(1) } : {}),
                 ...(m.label ? { label: m.label } : {}), at: m.at });
  }

  const record = path.join(entry, "views.json");
  const views = readViews(record);
  const entryView = {
    name: view,
    ...(opts.caption ? { caption: opts.caption } : {}),
    before: files.before,
    after: files.after,
    width: size.width,
    height: size.height,
    ...(marks.length ? { marks } : {}),
    model: rel,
    camera: b,
    highlight: highlightNames,
    ghost: names(opts.ghost),
    only: names(opts.only),
    xray: !!o.xray,
    source: { before: source(before, rel), after: source(after, rel) },
    changed: moved,
    withinMeshing: near,
  };
  const at = views.views.findIndex((v) => v.name === view);
  if (at >= 0) views.views[at] = entryView;
  else views.views.push(entryView);
  fs.writeFileSync(record, JSON.stringify(views, null, 2) + "\n");
  console.log(`views ${record}  (${views.views.map((v) => v.name).join(", ")})`);
  if (marks.length) for (const m of marks) console.log(`  mark ${m.label || ""} at ${m.x},${m.y} px${m.r ? `, ring ${m.r} px` : ""}`);
}

// --- main ------------------------------------------------------------------------------------

const USAGE = "usage: node tools/changes/change.mjs snapshot|changed|render ... (the header of tools/changes/change.mjs has the options)";

async function main() {
  const [cmd, ...rest] = process.argv.slice(2);
  const opts = parseArgs(rest);
  if (cmd === "snapshot") return snapshot(opts);
  if (cmd === "changed") return changed(opts);
  if (cmd === "render") return render(opts);
  die(USAGE);
}

main().then(
  () => finish(0),
  (err) => {
    console.error(err instanceof Refusal ? `change.mjs: ${err.message}` : (err.stack || err));
    finish(err instanceof Refusal ? 2 : 1);
  },
);
