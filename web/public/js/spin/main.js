// /spin — WHAT THE ROTATION LOOKS LIKE.
//
// One claim, drawn: the weld head does not move, the part does, and one cap
// closes in one continuous bead. Nothing else about the machine is modelled,
// because nothing else is in question. What is in question is the RATE — a
// 388.6 mm lap of bead at a hand-weld travel speed is a minute of standing
// still, and a number on a page does not tell you that. This does.
//
// The clock runs at 1× by default for exactly that reason. The time-scale
// buttons are there to skip the middle of a lap, not to watch it.
//
// The rig this is a picture of: hardware/assembly/weld-rotation-rig.md.
// The joint: hardware/assembly/pressure-vessel.md steps 3 and 5.

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { DIM, WIRE_AREA, buildPart, buildHead, setWireSide, buildTack, Bead } from "./rig.js";

// The head stands ACROSS THE BORE from where a camera naturally sits. The
// corner is 6.35 mm down a bore whose rim stands at the same radius, so the
// near-side corner is only visible from within ~15° of straight down — the
// far-side one is visible from any ordinary 3/4 view.
const HEAD_THETA = Math.PI;
const TACK_ORDER = [0, 4, 2, 6, 1, 5, 3, 7];   // opposite-side-bisecting, 45° apart
const INDEX_RATE = THREE.MathUtils.degToRad(28);  // rad/s the rig indexes between tacks
const TACK_DWELL = 0.55;            // s the table is stopped while a tack fires

const S = {
  travel: 8,          // mm/s at the bead radius — the only speed that matters
  wireFeed: 12,       // mm/s of ER316L .030
  overlap: 20,        // ° past 360 before the power comes off
  dir: 1,             // +1 = CCW seen from above
  scale: 1,           // time scale
  mode: "lap",        // "lap" | "tacks"
  running: true,
};

// ---------------------------------------------------------------- derived

const rpm      = () => (S.travel * 60) / DIM.beadC;
const revTime  = () => DIM.beadC / S.travel;
const sweepEnd = () => Math.PI * 2 * (1 + S.overlap / 360);
// Deposit per unit length is the wire's area times how much wire arrives per
// mm travelled; a triangular fillet of that area has legs of √(2A).
const fillet   = () => Math.sqrt(2 * (S.wireFeed / S.travel) * WIRE_AREA);

// ---------------------------------------------------------------- scene

const stage = document.getElementById("spin-stage");
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
// Without it the plate's up-facing face clips to flat white under the room
// environment, and a blown-out face is a face with no corner on it.
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.85;
stage.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);

const camera = new THREE.PerspectiveCamera(38, 1, 1, 4000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, DIM.capTopY - 18, 0);

// STAINLESS IS ITS SURROUNDINGS. A MeshStandardMaterial at metalness 0.9 with
// nothing to reflect renders black, which is what a bare three-point rig gives
// you and why the first pass of this page looked like charcoal. The room is
// the light: PMREM it once, hand it to the scene, and every material in
// rig.js reflects it.
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.05).texture;
scene.environmentIntensity = 0.6;
pmrem.dispose();

scene.add(new THREE.HemisphereLight(0xbcd0ff, 0x24243a, 0.7));
const key = new THREE.DirectionalLight(0xffffff, 2.4);
key.position.set(200, 340, 240);
scene.add(key);
const rim = new THREE.DirectionalLight(0x9ab8ff, 0.7);
rim.position.set(-220, 140, -200);
scene.add(rim);

// The bench the part stands on, so "vertical axis" reads as vertical.
const bench = new THREE.Mesh(
  new THREE.BoxGeometry(520, 12, 440),
  new THREE.MeshStandardMaterial({ color: 0x1c1c32, metalness: 0.05, roughness: 1 }),
);
bench.position.y = -34;
scene.add(bench);
// The table. It carries four radial marks because a plain disc turning at
// 1.2 RPM is a plain disc standing still — the same reason the part carries a
// seam and two ports.
const chuck = new THREE.Group();
chuck.position.y = -28;
scene.add(chuck);
const chuckMat = new THREE.MeshStandardMaterial({ color: 0x3b3b63, metalness: 0.6, roughness: 0.5 });
const markMat  = new THREE.MeshStandardMaterial({ color: 0x8f9bd6, metalness: 0.3, roughness: 0.7 });
chuck.add(new THREE.Mesh(new THREE.CylinderGeometry(104, 110, 28, 64), chuckMat));
for (let i = 0; i < 8; i++) {
  const a = (i * Math.PI) / 4;
  const long = i % 2 === 0;
  const m = new THREE.Mesh(new THREE.BoxGeometry(4, 2, long ? 30 : 16), markMat);
  m.position.set((long ? 86 : 93) * Math.sin(a), 15, (long ? 86 : 93) * Math.cos(a));
  m.rotation.y = a;
  chuck.add(m);
}

// THE PART TURNS. Everything below hangs off this one group's rotation.y.
const part = new THREE.Group();
part.add(buildPart(HEAD_THETA));   // the index stripe starts under the head
scene.add(part);

const head = buildHead({ headTheta: HEAD_THETA });
scene.add(head);

const bead = new Bead(part);
let tacks = [];

// Puddle + beam, both alive only while the trigger is down.
const puddle = new THREE.Mesh(
  new THREE.SphereGeometry(1.3, 20, 14),
  new THREE.MeshBasicMaterial({ color: 0xffd9a0 }),
);
puddle.position.copy(head.userData.target);
scene.add(puddle);
const puddleLight = new THREE.PointLight(0xffa64c, 0, 70, 2);
puddleLight.position.copy(head.userData.target).setY(DIM.capTopY + 4);
scene.add(puddleLight);

const beam = new THREE.Mesh(
  new THREE.CylinderGeometry(0.35, 0.9, 15, 12, 1, true),
  new THREE.MeshBasicMaterial({ color: 0x8fc0ff, transparent: true, opacity: 0.5,
                                blending: THREE.AdditiveBlending, side: THREE.DoubleSide }),
);
{
  const t = head.userData.target, d = head.userData.dir;
  beam.position.copy(t).addScaledVector(d, -7.5);
  beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().negate());
}
scene.add(beam);

// ---------------------------------------------------------------- camera presets

// Every view but "top" sits across the bore from the head, which is the only
// place the corner it welds is visible from.
const VIEWS = {
  "3/4":  { pos: [292, 336, 214], target: [0, 112, 0] },
  "rim":  { pos: [126, 244, 104], target: [-6, DIM.capTopY - 6, -34] },
  "top":  { pos: [0.1, DIM.capTopY + 245, 0], target: [0, DIM.capTopY, 0] },
  "wide": { pos: [452, 430, 336], target: [0, 74, 0] },
};
function setView(name) {
  const v = VIEWS[name] || VIEWS["3/4"];
  camera.position.set(...v.pos);
  controls.target.set(...v.target);
  controls.update();
  for (const b of document.querySelectorAll("[data-view]")) {
    b.classList.toggle("on", b.dataset.view === name);
  }
}

// ---------------------------------------------------------------- the run

// phi is UNSIGNED progress; the sign lives in S.dir. `laid` is how much of the
// lap has actually been welded — under the tack program the table also turns
// with the trigger up, and that motion lays nothing.
let phi = 0, laid = 0, t = 0, arc = false;
let program = null;

function resetRun() {
  phi = 0; laid = 0; t = 0; arc = false;
  bead.clear();
  for (const m of tacks) { part.remove(m); m.geometry.dispose(); }
  tacks = [];
  program = S.mode === "tacks" ? tackProgram() : null;
  part.rotation.y = 0;
  chuck.rotation.y = 0;
}

// The eight tacks, then the lap. Each step is "turn to this φ, stop, fire",
// and the last step hands the lap a part already sitting on tack #1 — a lap
// that starts on fused metal has no cold start.
function tackProgram() {
  const steps = [];
  let at = 0;
  for (const k of TACK_ORDER) {
    const local = (k * Math.PI) / 4;
    // The head is over local angle `local` when dir·φ ≡ HEAD_THETA − local.
    let want = S.dir * (HEAD_THETA - local);
    // shortest signed move from `at`
    let d = ((want - at + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI;
    steps.push({ to: at + d, tack: local });
    at += d;
  }
  let back = S.dir * HEAD_THETA;
  let d = ((back - at + Math.PI) % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2) - Math.PI;
  steps.push({ to: at + d, tack: null });
  return { steps, i: 0, dwell: 0, done: false };
}

function step(dt) {
  const omega = S.travel / DIM.beadR;   // rad/s — v = ωR, and R is the bore

  if (program && !program.done) {
    const s = program.steps[program.i];
    const gap = s.to - part.rotation.y;
    if (Math.abs(gap) > 1e-4) {
      const move = Math.min(Math.abs(gap), INDEX_RATE * dt) * Math.sign(gap);
      part.rotation.y += move;
      arc = false;
      return;
    }
    if (s.tack !== null && program.dwell < TACK_DWELL) {
      program.dwell += dt;
      arc = program.dwell > 0.12 && program.dwell < TACK_DWELL - 0.08;
      if (program.dwell >= TACK_DWELL - 0.08 && !s.fired) {
        s.fired = true;
        tacks.push(buildTack(part, s.tack, fillet()));
      }
      return;
    }
    program.i += 1; program.dwell = 0;
    if (program.i >= program.steps.length) { program.done = true; phi = 0; laid = 0; t = 0; }
    return;
  }

  if (phi >= sweepEnd()) { arc = false; return; }
  const d = omega * dt;
  phi = Math.min(sweepEnd(), phi + d);
  laid = phi;
  t += dt;
  part.rotation.y = S.dir * phi + (program ? program.steps.at(-1).to : 0);
  arc = true;
}

// ---------------------------------------------------------------- HUD

const el = (id) => document.getElementById(id);
const fmt = (n, d = 1) => n.toFixed(d);

function syncReadout() {
  el("r-rpm").textContent   = fmt(rpm(), 3);
  el("r-rev").textContent   = fmt(revTime(), 1);
  el("r-lap").textContent   = fmt(DIM.beadC, 1);
  el("r-leg").textContent   = fmt(fillet(), 2);
  el("r-ratio").textContent = fmt(S.wireFeed / S.travel, 2);
  el("r-total").textContent = fmt(revTime() * (1 + S.overlap / 360), 1);
  el("v-travel").textContent = fmt(S.travel, 1);
  el("v-wire").textContent   = fmt(S.wireFeed, 1);
  el("v-overlap").textContent = String(S.overlap);
}

function syncLive() {
  const deg = THREE.MathUtils.radToDeg(laid);
  el("r-deg").textContent = fmt(deg, 0);
  el("r-mm").textContent  = fmt((laid / (Math.PI * 2)) * DIM.beadC, 0);
  el("r-t").textContent   = fmt(t, 1);
  el("bar").style.width = `${Math.min(100, (laid / sweepEnd()) * 100)}%`;
  el("r-state").textContent = program && !program.done
    ? `tack ${Math.min(program.i + 1, 8)} of 8`
    : (laid >= sweepEnd() ? "bead closed" : (S.running ? "welding" : "held"));
}

function bindRange(id, key, after) {
  const r = el(id);
  r.addEventListener("input", () => {
    S[key] = Number(r.value);
    syncReadout();
    if (after) after();
  });
}

bindRange("travel", "travel");
bindRange("wire", "wireFeed");
bindRange("overlap", "overlap");

el("dir").addEventListener("click", () => {
  S.dir = -S.dir;
  el("dir").textContent = S.dir > 0 ? "CCW from above" : "CW from above";
  setWireSide(head, S.dir);
  resetRun();
});

el("mode").addEventListener("click", () => {
  S.mode = S.mode === "lap" ? "tacks" : "lap";
  el("mode").textContent = S.mode === "lap" ? "one continuous lap" : "8 tacks, then the lap";
  resetRun();
});

el("play").addEventListener("click", () => {
  S.running = !S.running;
  el("play").textContent = S.running ? "Pause" : "Run";
});
el("reset").addEventListener("click", resetRun);

for (const b of document.querySelectorAll("[data-scale]")) {
  b.addEventListener("click", () => {
    S.scale = Number(b.dataset.scale);
    for (const o of document.querySelectorAll("[data-scale]")) o.classList.toggle("on", o === b);
  });
}
for (const b of document.querySelectorAll("[data-view]")) {
  b.addEventListener("click", () => setView(b.dataset.view));
}

// ---------------------------------------------------------------- loop

function resize() {
  const w = stage.clientWidth, h = stage.clientHeight;
  if (!w || !h) return;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(stage);

let last = performance.now();
renderer.setAnimationLoop((now) => {
  // Clamped at both ends: 50 ms so a backgrounded tab does not jump a lap on
  // return, and 0 because a first rAF timestamp can precede the
  // performance.now() this was seeded with, which ran the clock backwards.
  const raw = Math.min(0.05, Math.max(0, (now - last) / 1000));
  last = now;
  if (S.running) step(raw * S.scale);

  chuck.rotation.y = part.rotation.y;
  bead.set(HEAD_THETA, S.dir * laid, fillet());

  const hot = arc && S.running;
  puddle.visible = hot;
  beam.visible = hot;
  const flick = 0.85 + 0.15 * Math.sin(now / 40);
  puddle.scale.setScalar(hot ? flick : 0.001);
  puddleLight.intensity = hot ? 900 * flick : 0;

  controls.update();
  syncLive();
  renderer.render(scene, camera);
});

resize();
setView("3/4");
setWireSide(head, S.dir);
syncReadout();
resetRun();

// The Puppeteer/e2e handle, same shape of escape hatch the viewer uses.
window.__hsmSpin = {
  S, rpm, revTime, fillet, resetRun,
  get phi() { return phi; },
  get laid() { return laid; },
  get tacks() { return tacks.length; },
  get angle() { return part.rotation.y; },
};
