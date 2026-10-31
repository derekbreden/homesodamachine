// The machine's own geometry service, where the server has one (web/lib/hsm.js). There the open
// model redraws when its payload moves, and the component panel measures picked bodies with
// hsm. The deployed site answers /api/hsm with a 404, and nothing below runs there.
//
// A PAYLOAD THAT MOVED IS READ OFF /meshes. Once a second while a model is open and the page is
// visible, the payload the page drew is asked for again under the ETag it came with, and the
// server answers off a stat: 304 while it stands. A new ETag is given one more second to hold,
// so a payload still being written is not read half-written, and then the page takes it the way
// it takes a `files-changed` frame (live.js): card and open model redrawn in place, camera kept.
//
// WHAT HSM MEASURES OF A PICK. With Measure on, the selected body is asked for by name: its
// payload index and size, and its clearance to the body picked before it, read off the same
// payload the page drew. The closest points are drawn between the two.

import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { scene } from "./scene.js";
import { state } from "./state.js";

const TICK_MS = 1000;
const MEASURE_KEY = "step-hsm-measure";
const WITNESS = 0x9cff57; // lime — apart from selection amber, hover blue, highlight cyan, find magenta

let service = null; // what /api/hsm answered, or null where nothing did
fetch("/api/hsm", { cache: "no-store" })
  .then((resp) => (resp.ok ? resp.json() : null))
  .catch(() => null)
  .then((body) => {
    service = body;
    if (body) setInterval(look, TICK_MS);
  });

let looking = false;
let moving = null; // { file, etag }: an ETag waiting a tick to hold
let taken = null;  // { file, etag }: the ETag last handed to live.js

async function look() {
  const mounted = state.mountedDetail;
  if (looking || document.hidden || mounted?.type !== "step") return;
  const loaded = state.stepEtags.get(mounted.file);
  if (!loaded) return; // drawn from the store, or still loading
  const url = mounted.surface === "mesh" ? `/meshes/${mounted.sourceFile}.mesh` : `/steps/${mounted.sourceFile}`;
  looking = true;
  let etag = null;
  try {
    const resp = await fetch(url, { method: "HEAD", cache: "no-store", headers: { "If-None-Match": loaded } });
    if (resp.status === 200) etag = resp.headers.get("etag");
  } catch {
    // The server is restarting; the next tick asks again.
  } finally {
    looking = false;
  }
  const at = (mark) => mark?.file === mounted.file && mark.etag === etag;
  if (!etag || etag === loaded || at(taken)) { moving = null; return; }
  if (!at(moving)) { moving = { file: mounted.file, etag }; return; }
  moving = null;
  taken = { file: mounted.file, etag };
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.FILES_CHANGED, { detail: { files: [mounted.sourceFile] } }));
}

// --- measurement ------------------------------------------------------------

let measuring = (() => {
  try { return localStorage.getItem(MEASURE_KEY) === "1"; } catch { return false; }
})();
let current = null;  // { file, name }: the body measured now
let previous = null; // { file, name }: the body measured before it, in the same model
const replies = new Map(); // `${op} ${file} ${names}` -> Promise of hsm's reply

const witness = new THREE.Group();
witness.name = "hsm-witness";
witness.renderOrder = 995;
scene.add(witness);
const witnessLine = new THREE.LineBasicMaterial({ color: WITNESS, depthTest: false, transparent: true });
const witnessDot = new THREE.PointsMaterial({ color: WITNESS, size: 7, sizeAttenuation: false, depthTest: false, transparent: true });

function clearWitness() {
  for (const child of witness.children) child.geometry.dispose();
  witness.clear();
}

function drawWitness(a, b) {
  clearWitness();
  const geometry = () => new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a), new THREE.Vector3(...b)]);
  witness.add(new THREE.Line(geometry(), witnessLine), new THREE.Points(geometry(), witnessDot));
}

// A model that drew again holds bodies the replies may not describe.
window.addEventListener(HSM_EVENTS.STEP_MOUNTED, () => {
  replies.clear();
  clearWitness();
});

function ask(file, op, fields) {
  const key = `${op} ${file} ${JSON.stringify(fields)}`;
  if (!replies.has(key)) {
    replies.set(key, fetch("/api/hsm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ file, op, ...fields }),
    }).then((resp) => resp.json()).catch((error) => ({ ok: false, error: error.message })));
  }
  return replies.get(key);
}

const mm = (v) => (Math.abs(v) < 1 ? v.toFixed(4) : v.toFixed(3));

function line(el, text, className = "component-measure-line") {
  const row = document.createElement("div");
  row.className = className;
  row.textContent = text;
  el.appendChild(row);
  return row;
}

let rendering = 0;

// Fills the component panel's measure block for the selected body. `solids` counts the bodies
// in the model drawn under that name: hsm measures one solid by its name.
export function renderMeasure(el, name, { file, solids, label }) {
  const run = ++rendering;
  el.replaceChildren();
  if (!service?.hsm || !name || !file) {
    if (!name) clearWitness();
    return;
  }
  const head = document.createElement("div");
  head.className = "component-measure-head";
  const title = document.createElement("span");
  title.textContent = "Measured by hsm";
  const toggle = document.createElement("button");
  toggle.type = "button";
  toggle.className = "component-show";
  toggle.textContent = measuring ? "Stop" : "Measure";
  toggle.title = measuring ? "Stop measuring picks" : "Measure this pick and the clearance to the next";
  toggle.addEventListener("click", () => {
    measuring = !measuring;
    try { localStorage.setItem(MEASURE_KEY, measuring ? "1" : "0"); } catch {}
    if (!measuring) { current = previous = null; clearWitness(); }
    renderMeasure(el, name, { file, solids, label });
  });
  head.append(title, toggle);
  el.appendChild(head);
  if (!measuring) return;

  if (solids !== 1) {
    clearWitness();
    line(el, solids ? `${solids} solids carry this name; hsm measures one solid at a time`
      : "Pick a single body to measure it");
    return;
  }
  if (current?.file !== file || current.name !== name) {
    previous = current?.file === file ? current : null;
    current = { file, name };
  }
  const status = line(el, "Measuring…");
  const before = previous;
  Promise.all([
    ask(file, "where", { pattern: name }),
    before ? ask(file, "gap", { a: before.name, b: name }) : null,
  ]).then(([where, gap]) => {
    if (run !== rendering) return;
    status.remove();
    if (!where.ok) { line(el, where.error); return; }
    const part = where.result.data.parts.find((p) => p.name.toLowerCase() === name.toLowerCase())
      || where.result.data.parts[0];
    if (part) {
      line(el, `${part.id} · ${part.size_mm.map(mm).join(" × ")} mm`);
      line(el, `from ${part.min_mm.map(mm).join(", ")} to ${part.max_mm.map(mm).join(", ")}`,
        "component-body-name");
    }
    if (!gap) {
      clearWitness();
      line(el, "Pick another body for the clearance between them", "component-body-name");
    } else if (!gap.ok) {
      clearWitness();
      line(el, gap.error);
    } else {
      // Clearance is zero for bodies that touch or overlap, and unknown where a solid would
      // not close; the surface distance is known either way.
      const g = gap.result.data.gap;
      const to = `To ${label(before.name)}`;
      if (g.clearance_mm === null) {
        line(el, `${to}: ${mm(g.surface_distance_mm)} mm surface to surface`);
        line(el, `clearance unknown: ${g.volume_error}`, "component-body-name");
      } else {
        line(el, `${to}: ${mm(g.clearance_mm)} mm clearance`);
        if (g.clearance_mm !== g.surface_distance_mm) {
          line(el, `surface to surface ${mm(g.surface_distance_mm)} mm`, "component-body-name");
        }
        if (g.intersection_volume_mm3 > 0) line(el, `overlap ${mm(g.intersection_volume_mm3)} mm³`);
      }
      if (g.point_a && g.point_b) drawWitness(g.point_a, g.point_b);
      else clearWitness();
    }
    line(el, `payload ${where.result.payload_sha256.slice(0, 12)}`, "component-body-name");
  });
}
