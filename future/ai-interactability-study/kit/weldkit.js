/* weldkit.js - shared scene kit for the welding-arrangement interactability study.
 *
 * Classic script (no modules, no fetch, no CDN) so a scene's index.html works from file://.
 * Needs THREE r147 (kit/vendor/three.min.js) and, for 3D stages, THREE.OrbitControls.
 * Units are millimetres, +Z is up. Tube axis = Z axis, tube bottom at z=0, weld station on +X.
 * Everything drawn here is EXPLANATORY geometry, never measured hardware. See kit/README.md.
 */
(function (global) {
'use strict';
if (typeof THREE === 'undefined') throw new Error('WK: load kit/vendor/three.min.js before weldkit.js');

const WK = {};
global.WK = WK;
WK.version = '1.1.0';

// ---------------------------------------------------------------- error collection
// Tools read window.__sceneErrors; uncaught errors and failed resource loads land here.
global.__sceneErrors = global.__sceneErrors || [];
global.addEventListener('error', function (e) {
  const t = e.target;
  if (t && t !== global && (t.src || t.href)) global.__sceneErrors.push('load failed: ' + (t.src || t.href));
  else global.__sceneErrors.push((e.message || 'error') + (e.filename ? ' (' + String(e.filename).split('/').pop() + ':' + e.lineno + ')' : ''));
}, true);
global.addEventListener('unhandledrejection', function (e) {
  global.__sceneErrors.push('unhandled rejection: ' + ((e.reason && e.reason.message) || e.reason));
});
function fail(where, e) {
  const msg = where + ': ' + ((e && e.stack) ? String(e.stack).split('\n').slice(0, 3).join(' | ') : e);
  global.__sceneErrors.push(msg);
  if (global.console) console.error(msg);
}
WK._fail = fail;

// ---------------------------------------------------------------- small helpers
const V3 = THREE.Vector3;
const DEG = Math.PI / 180;
const AX = { x: new V3(1, 0, 0), y: new V3(0, 1, 0), z: new V3(0, 0, 1) };
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
function v3(p) {
  if (!p) return new V3();
  if (p.isVector3) return p.clone();
  if (Array.isArray(p)) return new V3(p[0] || 0, p[1] || 0, p[2] || 0);
  return new V3(p.x || 0, p.y || 0, p.z || 0);
}
WK.v3 = v3;
WK.deg = DEG;
WK.clamp = clamp;
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
WK.esc = esc;
function decimals(step) {
  const s = String(step);
  if (s.indexOf('e-') >= 0) return parseInt(s.split('e-')[1], 10);
  const i = s.indexOf('.');
  return i < 0 ? 0 : Math.min(6, s.length - i - 1);
}

// Tiny DOM builder: h('div', {class:'x', text:'..', html:'..', on:{click:fn}}, child, child...)
function h(tag, attrs) {
  const n = document.createElement(tag);
  if (attrs) for (const k in attrs) {
    const v = attrs[k];
    if (v == null || v === false) continue;
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k === 'html') n.innerHTML = v;
    else if (k === 'on') for (const ev in v) n.addEventListener(ev, v[ev]);
    else if (k === 'style' && typeof v === 'object') Object.assign(n.style, v);
    else n.setAttribute(k, v === true ? '' : v);
  }
  for (let i = 2; i < arguments.length; i++) {
    const c = arguments[i];
    if (c == null || c === false) continue;
    n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return n;
}
WK.h = h;
const SVGNS = 'http://www.w3.org/2000/svg';
// WK.svg('rect', {x:0, y:0, width:10}, child...) -> SVG element (for custom 2D stages)
WK.svg = function (tag, attrs) {
  const n = document.createElementNS(SVGNS, tag);
  if (attrs) for (const k in attrs) {
    if (attrs[k] == null) continue;
    if (k === 'text') n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]);
  }
  for (let i = 2; i < arguments.length; i++) if (arguments[i]) n.appendChild(arguments[i]);
  return n;
};

// ---------------------------------------------------------------- ground-truth geometry
// Ported from web/public/js/weld-position/pose.js. Proxy gun geometry, pitch and nozzle
// clearance are ILLUSTRATIVE (the reference scene says so); tube/cap numbers come from the
// fabrication sources.
const IN = 25.4;
const DIM = Object.freeze({
  tubeOd: 5 * IN, tubeWall: 0.065 * IN, tubeHeight: 6 * IN,
  capDiameter: 4.860 * IN, capThickness: 0.250 * IN, capRecess: 0.250 * IN,
  portDiameter: 0.438 * IN, portOffset: 0.750 * IN,
  gunLength: 253, gunWidth: 34, gunHeight: 143,   // manual section 3.4 envelope
});
const INNER_RADIUS = DIM.tubeOd / 2 - DIM.tubeWall;
const CAP_TOP = DIM.tubeHeight - DIM.capRecess;
const JOINT_ARR = [INNER_RADIUS, 0, CAP_TOP];
const PITCH = 60 * DEG;
const CLEARANCE = 16;
const GRIP_BASE_ARR = [0, -118, 237];
const WIRE_TIP_ARR = [0, 0, -CLEARANCE];
const _ax = Math.hypot(GRIP_BASE_ARR[1], GRIP_BASE_ARR[2] + CLEARANCE);
const LOCAL_ROLL_AXIS_ARR = [0, GRIP_BASE_ARR[1] / _ax, (GRIP_BASE_ARR[2] + CLEARANCE) / _ax];
const WIRE_BRACE_MOUNT_ARR = [0, -12, 110];
const WIRE_GUIDE_BACK_ARR = [0, -24.7, 87.1];
const WIRE_GUIDE_LENGTH = 40;
const _gv = WIRE_GUIDE_BACK_ARR.map((v, i) => v - WIRE_TIP_ARR[i]);
const _gl = Math.hypot(_gv[0], _gv[1], _gv[2]);
const WIRE_GUIDE_DIR_ARR = _gv.map(v => v / _gl);
const WIRE_GUIDE_END_ARR = WIRE_GUIDE_BACK_ARR.map((v, i) => v - WIRE_GUIDE_LENGTH * WIRE_GUIDE_DIR_ARR[i]);
const HOLE_AXIS_OFFSET = 35;   // dial reads 35 at the reference mounting inclination; posePoint's own angle = dial - 35

const fz = v => Object.freeze(v);
WK.DIM = DIM;
WK.INNER_RADIUS = INNER_RADIUS;
WK.CAP_TOP = CAP_TOP;
WK.JOINT = fz(new V3(JOINT_ARR[0], JOINT_ARR[1], JOINT_ARR[2]));   // frozen: use .clone() before changing
WK.PITCH = PITCH;
WK.CLEARANCE = CLEARANCE;
WK.GRIP_BASE_LOCAL = fz(new V3(...GRIP_BASE_ARR));
WK.WIRE_TIP_LOCAL = fz(new V3(...WIRE_TIP_ARR));
WK.LOCAL_ROLL_AXIS = fz(new V3(...LOCAL_ROLL_AXIS_ARR));
WK.HOLE_AXIS_OFFSET = HOLE_AXIS_OFFSET;
// The reference scene's opening pose. Illustrative; not a recommended or required setup.
WK.OPENING = fz({ roll: 45, holeDial: 30, vertical: -15, note: "the reference scene's opening pose, illustrative" });
// Existing rotator numbers (hardware/assembly/weld-rotation-rig.md). The layout of towers is a proxy.
WK.RIG = fz({
  baseX: 300, baseY: 250, baseZ: 12, footH: 24, benchToTubeBottom: 86, benchToRim: 238.4,
  nestOd: 150, tubeBottomAboveBaseBottom: 62,
  runoutRadialTIR: 0.25, runoutFaceTIR: 0.30,   // acceptance limits stated in the rig doc
  weldCircleDia: 123.7, rpmNominal: 1.235, degPerSecNominal: 1.235 * 6,
});

function posePointArr(point, rollDegrees, holeRollDegrees, verticalDegrees) {
  rollDegrees = rollDegrees || 0; holeRollDegrees = holeRollDegrees || 0; verticalDegrees = verticalDegrees || 0;
  const p = Array.isArray(point) ? point : [point.x, point.y, point.z];
  const x = p[0], y = p[1], z = p[2];
  const s = Math.sin(PITCH), c = Math.cos(PITCH);
  const along = z + CLEARANCE;
  const py = -c * along + s * y;
  const pz = s * along + c * y;
  const roll = rollDegrees * DEG;
  const ay = -c * LOCAL_ROLL_AXIS_ARR[2] + s * LOCAL_ROLL_AXIS_ARR[1];
  const az = s * LOCAL_ROLL_AXIS_ARR[2] + c * LOCAL_ROLL_AXIS_ARR[1];
  const dot = ay * py + az * pz;
  const cr = Math.cos(roll), sr = Math.sin(roll);
  const rx = x * cr + (ay * pz - az * py) * sr;
  const ry = py * cr + az * x * sr + ay * dot * (1 - cr);
  const rz = pz * cr - ay * x * sr + az * dot * (1 - cr);
  const holeRoll = holeRollDegrees * DEG;
  const ch = Math.cos(holeRoll), sh = Math.sin(holeRoll);
  const hy = ry * ch + rz * sh;
  const hz = -ry * sh + rz * ch;
  const vertical = verticalDegrees * DEG;
  const cv = Math.cos(vertical), sv = Math.sin(vertical);
  return [JOINT_ARR[0] + rx * cv - hy * sv, JOINT_ARR[1] + rx * sv + hy * cv, JOINT_ARR[2] + hz];
}
// Port of posePoint(). NOTE the 3rd argument is posePoint's own hole angle (= holeDial - 35).
// Prefer WK.dialsToPose, which takes the dial values as the sliders show them.
WK.posePoint = function (point, rollDeg, holeRollDeg, verticalDeg) {
  const r = posePointArr(point, rollDeg, holeRollDeg, verticalDeg);
  return new V3(r[0], r[1], r[2]);
};
// Same maths as updatePose() in main.js: pose of the gun group (local origin = nozzle tip).
WK.dialsToPose = function (roll, holeDial, vertical) {
  const hr = holeDial - HOLE_AXIS_OFFSET;
  const o = posePointArr([0, 0, 0], roll, hr, vertical);
  const b = [0, 1, 2].map(function (axis) {
    const p = [0, 0, 0]; p[axis] = 1;
    const q = posePointArr(p, roll, hr, vertical);
    return new V3(q[0] - o[0], q[1] - o[1], q[2] - o[2]);
  });
  const quaternion = new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(b[0], b[1], b[2]));
  return { position: new V3(o[0], o[1], o[2]), quaternion: quaternion };
};

// ---------------------------------------------------------------- role palette
// Colour parts by ROLE so every scene reads the same way. Hex values are sRGB.
const ROLE = {
  fixed:     { label: 'Fixed / ground',                 color: 0x6b7a90, metal: 0.15, rough: 0.75 },
  load:      { label: 'Carries load',                   color: 0xf5a524, metal: 0.10, rough: 0.60 },
  locate:    { label: 'Locates / reference',            color: 0x14b8a6, metal: 0.10, rough: 0.60 },
  actuated:  { label: 'Actuated (software could command)', color: 0xa855f7, metal: 0.10, rough: 0.55 },
  compliant: { label: 'Compliant / free',               color: 0x4ade80, metal: 0.05, rough: 0.65 },
  sensor:    { label: 'Sensor / observer',              color: 0x3b82f6, metal: 0.10, rough: 0.50 },
  gun:       { label: 'Gun (proxy, not measured)',      color: 0x59636f, metal: 0.35, rough: 0.50 },
  work:      { label: 'Work (tube, plate)',             color: 0xc8d0da, metal: 0.45, rough: 0.38 },
  cable:     { label: 'Cable / umbilical',              color: 0x30343b, metal: 0.05, rough: 0.80 },
  wire:      { label: 'Wire feed',                      color: 0xe6b422, metal: 0.25, rough: 0.45 },
  laser:     { label: 'Laser / dot',                    color: 0xff3b30, metal: 0,    rough: 1 },
  ghost:     { label: 'Ghost / context',                color: 0x9aa4b2, metal: 0,    rough: 1, opacity: 0.16 },
};
const ROLE_ALIAS = {
  ground: 'fixed', static: 'fixed', carries: 'load', carry: 'load', locates: 'locate', reference: 'locate',
  moves: 'actuated', actuator: 'actuated', free: 'compliant', observer: 'sensor', camera: 'sensor',
  umbilical: 'cable', feed: 'wire', wirefeed: 'wire', dot: 'laser', steel: 'gun', tube: 'work', plate: 'work',
};
WK.ROLE = ROLE;
const _warned = {};
WK.role = function (name) {
  if (ROLE[name]) return name;
  if (ROLE_ALIAS[name]) return ROLE_ALIAS[name];
  if (!_warned[name]) { _warned[name] = 1; if (global.console) console.warn('WK: unknown role "' + name + '", using ghost. Roles: ' + Object.keys(ROLE).join(', ')); }
  return 'ghost';
};
WK.roleHex = function (name) { return '#' + ('000000' + ROLE[WK.role(name)].color.toString(16)).slice(-6); };

// r147 gotcha: colour management is in "legacy" mode, so lit and basic materials need LINEAR colours
// (the renderer encodes to sRGB on output). Always build material colours with WK.color(hex).
WK.color = function (hex) { return new THREE.Color(hex).convertSRGBToLinear(); };

const _matCache = new Map();
// Role material. o: {shade (multiplier, default 1), opacity, side, flat, basic}
WK.mat = function (role, o) {
  role = WK.role(role); o = o || {};
  const key = [role, o.shade || 1, o.opacity == null ? '' : o.opacity, o.side || '', o.flat ? 1 : 0, o.basic ? 1 : 0].join('|');
  let m = _matCache.get(key);
  if (m) return m;
  const R = ROLE[role];
  const color = WK.color(R.color);
  if (o.shade) color.multiplyScalar(o.shade);
  const opacity = o.opacity != null ? o.opacity : R.opacity;
  const common = { color: color };
  if (opacity != null && opacity < 1) { common.transparent = true; common.opacity = opacity; common.depthWrite = false; }
  if (o.side === 'double' || role === 'ghost') common.side = THREE.DoubleSide;
  if (role === 'laser' || o.basic) m = new THREE.MeshBasicMaterial(common);
  else m = new THREE.MeshStandardMaterial(Object.assign({ metalness: R.metal, roughness: R.rough, flatShading: !!o.flat }, common));
  m.userData.wkRole = role;
  if (o.shade) m.userData.wkShade = o.shade;
  _matCache.set(key, m);
  return m;
};
const _lineCache = new Map();
// Line material (solid or dashed). o: {dashed, dash, gap, opacity, onTop}
WK.lineMat = function (role, o) {
  role = WK.role(role); o = o || {};
  const key = [role, o.dashed ? [o.dash, o.gap].join(',') : '', o.opacity == null ? '' : o.opacity, o.onTop ? 1 : 0].join('|');
  let m = _lineCache.get(key);
  if (m) return m;
  const p = { color: WK.color(ROLE[role].color), transparent: o.opacity != null || !!o.onTop, opacity: o.opacity == null ? 1 : o.opacity, depthTest: !o.onTop };
  m = o.dashed ? new THREE.LineDashedMaterial(Object.assign(p, { dashSize: o.dash || 4, gapSize: o.gap || 3 })) : new THREE.LineBasicMaterial(p);
  m.userData.wkRole = role;
  _lineCache.set(key, m);
  return m;
};

function isRenderable(o) { return o.isMesh || o.isLine || o.isLineSegments || o.isPoints; }
function tagRole(obj, role) { obj.userData.role = WK.role(role); return obj; }
function mesh(geo, role, o) {
  const m = new THREE.Mesh(geo, WK.mat(role, o));
  m.userData.role = WK.role(role);
  if (o && o.occludes === false) m.userData.occludes = false;
  return m;
}

// Change a part's role (and colour) at runtime, e.g. a link turns 'locate' when it locks.
// Only sub-meshes that share the group's main role (or have none) are recoloured.
WK.setRole = function (obj, role) {
  role = WK.role(role);
  const main = obj.userData.role;
  WK.highlight(obj, false);
  obj.traverse(function (m) {
    if (!isRenderable(m)) return;
    const r = m.userData.role;
    if (r && main && r !== main) return;
    const old = m.material;
    if (m.isMesh) {
      const shade = old && old.userData && old.userData.wkShade;
      m.material = WK.mat(role, shade ? { shade: shade } : (old && old.transparent && role !== 'ghost' ? { opacity: old.opacity } : undefined));
    } else if (m.isLine || m.isLineSegments) {
      m.material = WK.lineMat(role, old && old.isLineDashedMaterial ? { dashed: true, dash: old.dashSize, gap: old.gapSize, onTop: !old.depthTest } : { onTop: !old.depthTest });
    }
    m.userData.role = role;
  });
  obj.userData.role = role;
  return obj;
};

// Hover highlight (used by control `visual:` option). Swaps in a brighter clone; never mutates shared materials.
const _hl = new WeakMap();
function hlMat(m) {
  let c = _hl.get(m);
  if (c) return c;
  c = m.clone();
  if (c.emissive) { c.emissive.setRGB(0.55, 0.55, 0.55); }
  else if (c.color) { c.color.lerp(new THREE.Color(1, 1, 1), 0.55); }
  _hl.set(m, c);
  return c;
}
WK.highlight = function (target, on) {
  const list = typeof target === 'function' ? target() : target;
  const arr = Array.isArray(list) ? list : [list];
  arr.forEach(function (root) {
    if (!root || !root.traverse) return;
    root.traverse(function (m) {
      if (!isRenderable(m) || !m.material || Array.isArray(m.material)) return;
      if (on) { if (!m.userData._hl0) { m.userData._hl0 = m.material; m.material = hlMat(m.material); } }
      else if (m.userData._hl0) { m.material = m.userData._hl0; delete m.userData._hl0; }
    });
  });
};

// Fast frame from a direction (local Y = dir, local Z ~ world up). Used by rails/carriages.
function frameFromDir(dir, upHint) {
  const y = dir.clone().normalize();
  let up = upHint ? upHint.clone() : new V3(0, 0, 1);
  if (Math.abs(y.dot(up)) > 0.98) up = new V3(1, 0, 0);
  const x = new V3().crossVectors(y, up).normalize();
  const z = new V3().crossVectors(x, y).normalize();
  return new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(x, y, z));
}

// ---------------------------------------------------------------- kinematics helpers (rigid links)
// The study forbids silently stretching rigid links or moving fixed anchors. These helpers return
// a LIMITED result instead: draw the reachable point and show a red badge (app.badge(..., 'limit')).
WK.kin = {
  // Keep p1 within L of p0. -> {point, length, limited, over}. p0 stays put; p1 stops at the limit.
  clampLength: function (p0, p1, L) {
    const a = v3(p0), b = v3(p1), d = b.clone().sub(a), len = d.length();
    if (len <= L) return { point: b, length: len, limited: false, over: 0 };
    return { point: a.clone().addScaledVector(d, L / len), length: L, limited: true, over: len - L };
  },
  // The point exactly L from p0 toward `target` (a rigid rod that swings freely about p0).
  projectToLength: function (p0, target, L) {
    const a = v3(p0), d = v3(target).sub(a);
    if (d.lengthSq() < 1e-12) d.set(0, 0, -1);
    return a.addScaledVector(d.normalize(), L);
  },
  // Translate obj (orientation kept) so its LOCAL point lands on a WORLD point. Returns the residual (mm).
  attachAtOffset: function (obj, localPoint, worldPoint) {
    obj.updateWorldMatrix(true, false);
    const target = v3(worldPoint), lp = v3(localPoint);
    const delta = target.clone().sub(obj.localToWorld(lp.clone()));
    if (obj.parent) {
      obj.parent.updateWorldMatrix(true, false);
      delta.applyMatrix3(new THREE.Matrix3().setFromMatrix4(new THREE.Matrix4().copy(obj.parent.matrixWorld).invert()));
    }
    obj.position.add(delta);
    obj.updateWorldMatrix(true, false);
    return obj.localToWorld(lp.clone()).distanceTo(target);
  },
  // Two-link IK in 3D. `bend` = direction the elbow prefers (default +Z). Never stretches:
  // beyond reach the end stops at max reach (limited:'far'); inside min reach it stops (limited:'near').
  // -> {ok, elbow, end, limited, over, reach, angles:{shoulder, elbow}} (angles in radians)
  twoLinkIK: function (base, target, L1, L2, o) {
    o = o || {};
    const b = v3(base), t = v3(target), d = t.clone().sub(b);
    const dist = d.length();
    const u = dist > 1e-9 ? d.clone().multiplyScalar(1 / dist) : new V3(1, 0, 0);
    const maxR = L1 + L2, minR = Math.abs(L1 - L2);
    let D = dist, limited = null, over = 0;
    if (dist > maxR) { limited = 'far'; over = dist - maxR; D = maxR; }
    else if (dist < minR + 1e-6) { limited = 'near'; over = minR - dist; D = minR + 1e-6; }
    const a = (L1 * L1 - L2 * L2 + D * D) / (2 * D);
    const hh = Math.sqrt(Math.max(0, L1 * L1 - a * a));
    const hint = v3(o.bend || [0, 0, 1]);
    hint.addScaledVector(u, -hint.dot(u));
    if (hint.lengthSq() < 1e-9) { const ax = Math.abs(u.x) < 0.9 ? AX.x : AX.y; hint.copy(ax).addScaledVector(u, -ax.dot(u)); }
    hint.normalize();
    const elbow = b.clone().addScaledVector(u, a).addScaledVector(hint, hh);
    const end = b.clone().addScaledVector(u, D);
    return {
      ok: !limited, limited: limited, over: over, reach: D, elbow: elbow, end: end,
      angles: { shoulder: Math.acos(clamp(a / L1, -1, 1)), elbow: Math.acos(clamp((L1 * L1 + L2 * L2 - D * D) / (2 * L1 * L2), -1, 1)) },
    };
  },
};

// ---------------------------------------------------------------- cable helpers
// Manufacturer manual values (XLaserlab X1 Pro): 350 mm minimum bend radius while emitting, 240 mm stored.
// The badge built from them is an ILLUSTRATIVE check on a drawn curve, not a cable model.
WK.CABLE = fz({ minBendEmitting: 350, minBendStored: 240, source: 'XLaserlab X1 Pro manual (manufacturer values)' });
// Smallest local radius of curvature (mm) of a THREE.Curve or of an array of points (Vector3 | [x,y,z] | {x,y,z}).
// A curve is sampled (o.samples, default 240 in t). Points that turn at most 15 deg at every vertex (a sampled curve, a
// dense cable polyline, also the control points of a Catmull-Rom curve) are measured AS GIVEN: the circumradius of each
// consecutive triple is exact on circles and helices. Coarser points have corners, which have no radius, so they are
// smoothed first (centripetal Catmull-Rom, the curve P.cable draws). Never feed a Catmull-Rom spline through dense
// samples of a smooth curve: its phantom end points make the first and last segment about twice as tight.
// o.detail:true returns {radius, point, index} so a scene can mark where the tightest bend is.
WK.curveMinRadius = function (c, o) {
  o = o || {};
  const done = (r, pt, i) => (o.detail ? { radius: r, point: pt || null, index: i == null ? -1 : i } : r);
  const isCurve = !!(c && c.getPoints);
  let src = isCurve ? (c.isCatmullRomCurve3 && c.points ? c.points : null) : (c || []), pts;
  if (src) {
    const arr = [];
    src.forEach(function (q) { const v = v3(q); if (!arr.length || v.distanceToSquared(arr[arr.length - 1]) > 1e-8) arr.push(v); });
    if (arr.length < 3) return done(Infinity);
    let turn = 0;
    for (let i = 1; i < arr.length - 1; i++) turn = Math.max(turn, arr[i].clone().sub(arr[i - 1]).angleTo(arr[i + 1].clone().sub(arr[i])));
    if (turn <= 15 * DEG) pts = arr;
    else if (!isCurve) pts = new THREE.CatmullRomCurve3(arr, false, 'centripetal').getPoints(Math.max(80, (arr.length - 1) * 30));
  }
  if (!pts) pts = c.getPoints(o.samples || 240);
  let min = Infinity, at = -1;
  const ab = new V3(), bc = new V3(), ca = new V3(), cr = new V3();
  for (let i = 1; i < pts.length - 1; i++) {
    ab.subVectors(pts[i], pts[i - 1]); bc.subVectors(pts[i + 1], pts[i]); ca.subVectors(pts[i + 1], pts[i - 1]);
    const area2 = cr.crossVectors(ab, bc).length();
    if (area2 < 1e-9) continue;
    const R = (ab.length() * bc.length() * ca.length()) / (2 * area2);
    if (R < min) { min = R; at = i; }
  }
  return done(min, at >= 0 ? pts[at].clone() : null, at);
};
// -> {level:'ok'|'warn'|'limit', text}. Feed to app.badge(id, text, level).
WK.cableBadge = function (minR) {
  const E = WK.CABLE.minBendEmitting, S = WK.CABLE.minBendStored;
  const r = isFinite(minR) ? Math.round(minR) + ' mm' : 'straight';
  if (!isFinite(minR) || minR >= E) return { level: 'ok', text: 'min bend R ' + r + ' (manual: ' + E + ' emitting / ' + S + ' stored; illustrative check)' };
  if (minR >= S) return { level: 'warn', text: 'min bend R ' + r + ' < ' + E + ' emitting (ok only stored, ' + S + '); illustrative' };
  return { level: 'limit', text: 'min bend R ' + r + ' < ' + S + ' stored minimum; illustrative' };
};
// Cubic Bezier cable. startDir / endDir = direction of travel leaving the start and arriving at the end.
// stiffness = handle length / chord (default 0.4). It is NOT "bigger = wider bend": for a quarter turn the bend is widest
// near 0.39 and tightens both ways (R 400 mm arc: 0.2 -> 70, 0.4 -> 386, 0.6 -> 166, 0.8 -> 71 mm). stiffness:'auto'
// picks the handle length (0.15..0.9 of the chord) that maximises the smallest radius. Returns a THREE.CubicBezierCurve3
// with .minRadius() and .stiffness (the value used).
WK.bezierCable = function (startPoint, startDir, endPoint, endDir, o) {
  o = o || {};
  const a = v3(startPoint), b = v3(endPoint);
  const da = v3(startDir).normalize(), db = v3(endDir).normalize(), chord = a.distanceTo(b);
  const make = s => { const k = Math.max(15, s * chord); return new THREE.CubicBezierCurve3(a, a.clone().addScaledVector(da, k), b.clone().addScaledVector(db, -k), b); };
  let st = o.stiffness == null ? 0.4 : o.stiffness, curve;
  if (st === 'auto') {
    let best = -1;
    for (let s = 0.15; s <= 0.9001; s += 0.05) { const c = make(s), r = WK.curveMinRadius(c, { samples: 90 }); if (r > best) { best = r; st = s; curve = c; } }
    if (!curve) curve = make(st = 0.4);
  } else curve = make(st);
  curve.stiffness = st;
  curve.minRadius = function () { return WK.curveMinRadius(curve); };
  return curve;
};

// ---------------------------------------------------------------- line of sight (scene geometry, NOT a measurement)
// Meshes that block a proposed sensor: everything solid and visible, not ghost/laser/sensor/helper.
// o.ignore = [Object3D...]: those objects (and their children) are skipped, e.g. the part that carries the target.
// A mesh or group with userData.occludes === false never blocks (children of such a group too); WK.prim.camera sets it.
WK.occluders = function (app, o) {
  const out = [], ignore = (o && o.ignore) || [];
  app.scene.traverse(function (m) {
    if (!m.isMesh || !m.visible || m.layers.mask === 2) return;
    const r = m.userData.role;
    if (m.userData.occludes === false || r === 'ghost' || r === 'laser' || r === 'sensor') return;
    let p = m, skip = false;
    while (p) { if (p.visible === false || (p !== m && p.userData.occludes === false) || ignore.indexOf(p) >= 0) { skip = true; break; } p = p.parent; }
    if (!skip) out.push(m);
  });
  return out;
};
// Ray from `from` to `to` against occluders (Object3D[]; recursive). This is drawn-scene geometry that
// says whether a PROPOSED sensor could see a point; it does not model optics, lighting or fume.
// o.eps (default 0.8 mm): the last eps mm of the ray, at the TARGET end, are not tested, so a target that sits ON a surface
// is not blocked by that surface's own facets. Keep eps below the 1.65 mm tube wall: a larger value lets a point behind
// the wall look visible from outside. For a target exactly on a surface or corner, test a point nudged toward the observer
// (see WK.beamSurfacePoint().viewPoint) instead of raising eps.
WK.lineOfSight = function (from, to, occluders, o) {
  o = o || {};
  const a = v3(from), b = v3(to), d = b.clone().sub(a), dist = d.length();
  if (dist < 1e-6) return { visible: true, hitObject: null, hitDistance: null, distance: 0 };
  d.multiplyScalar(1 / dist);
  const rc = new THREE.Raycaster(a, d, 0, Math.max(0, dist - (o.eps == null ? 0.8 : o.eps)));
  const list = occluders || [];
  list.forEach(function (x) { x.updateWorldMatrix(true, false); });
  const hits = rc.intersectObjects(list, true);
  const hit = hits[0];
  return { visible: !hit, hitObject: hit ? hit.object : null, hitDistance: hit ? hit.distance : null, hitPoint: hit ? hit.point : null, distance: dist };
};

// Where a beam from `origin` along `dir` first lands on the drawn work (tube wall, endcap; o.targets overrides). The laser
// dot is a point in space that may sit inside the wall or above the plate; this is the surface point a camera could see.
// -> {point, viewPoint (point nudged o.lift mm, default 0.3, toward the beam source: test THIS with markVisibility),
//     normal (faces the source), object, part:'tube'|'cap'|'other', distance} or null when the beam misses.
WK.beamSurfacePoint = function (origin, dir, o) {
  o = o || {};
  const ws = WK.workstation;
  const targets = (o.targets || (ws ? [ws.tube, ws.cap] : [])).filter(Boolean);
  if (!targets.length) return null;
  targets.forEach(function (t) { t.updateWorldMatrix(true, false); });
  const d = v3(dir).normalize(), rc = new THREE.Raycaster(v3(origin), d, 0, o.maxDistance == null ? Infinity : o.maxDistance);
  const hit = rc.intersectObjects(targets, true)[0];
  if (!hit) return null;
  const n = hit.face ? hit.face.normal.clone().transformDirection(hit.object.matrixWorld) : d.clone().negate();
  if (n.dot(d) > 0) n.negate();
  const lift = o.lift == null ? 0.3 : o.lift;
  return { point: hit.point.clone(), viewPoint: hit.point.clone().addScaledVector(n, lift), normal: n, object: hit.object, distance: hit.distance,
    part: ws && hit.object === ws.tube ? 'tube' : (ws && hit.object === ws.cap ? 'cap' : 'other') };
};

// ---------------------------------------------------------------- primitives
const P = WK.prim = {};
function orientGeo(g, axis) {
  if (axis === 'z') g.rotateX(Math.PI / 2);
  else if (axis === 'x') g.rotateZ(-Math.PI / 2);
  return g;
}
function placeRod(m, a, b) {
  a = v3(a); b = v3(b);
  const d = b.clone().sub(a), L = Math.max(d.length(), 1e-6);
  m.position.copy(a).add(b).multiplyScalar(0.5);
  m.quaternion.setFromUnitVectors(AX.y, d.multiplyScalar(1 / L));
  m.scale.set(m.userData.kx || 1, L, m.userData.kx || 1);
}
// box(w,d,h,role): w along X, d along Y, h along Z, centred.
P.box = function (w, d, h, role, o) { return mesh(new THREE.BoxGeometry(w, d, h), role || 'fixed', o); };
// cyl(r,h,role,{axis:'z'|'x'|'y'}): centred; default axis Z.
P.cyl = function (r, hgt, role, o) { o = o || {}; return mesh(orientGeo(new THREE.CylinderGeometry(r, r, hgt, o.segments || 32), o.axis || 'z'), role || 'fixed', o); };
P.sphere = function (r, role, o) { return mesh(new THREE.SphereGeometry(r, 20, 14), role || 'fixed', o); };
// rod(p0,p1,r,role): cylinder between two points. rod.setEnds(p0,p1) re-aims it (stays rigid in radius).
P.rod = function (p0, p1, r, role, o) {
  o = o || {};
  const m = mesh(new THREE.CylinderGeometry(r, r, 1, o.segments || 14), role || 'fixed', o);
  m.setEnds = function (a, b) { placeRod(m, a, b); return m; };
  return m.setEnds(p0, p1);
};
// rail(p0,p1,{width,height,role}): flat guide bar with a groove line; rail.setEnds(p0,p1). Carriages ride on it.
P.rail = function (p0, p1, o) {
  o = o || {};
  const width = o.width || 12, height = o.height || 6, role = o.role || 'fixed';
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const bar = mesh(new THREE.BoxGeometry(width, 1, height), role);
  const groove = mesh(new THREE.BoxGeometry(width * 0.32, 1.001, 0.4), role, { shade: 0.45 });
  groove.position.z = height / 2;
  g.add(bar, groove);
  g.userData.width = width; g.userData.height = height;
  g.setEnds = function (a, b) {
    a = v3(a); b = v3(b);
    const d = b.clone().sub(a), L = Math.max(d.length(), 1e-6);
    g.position.copy(a).add(b).multiplyScalar(0.5);
    g.quaternion.copy(frameFromDir(d, o.up ? v3(o.up) : null));
    g.scale.set(1, L, 1);
    g.userData.p0 = a; g.userData.p1 = b;
    return g;
  };
  return g.setEnds(p0, p1);
};
// carriage(size:[w,l,h], role, {rail, t}): block that rides a rail; carriage.setT(t) slides it (t 0..1).
P.carriage = function (size, role, o) {
  o = o || {};
  const s = size || [24, 30, 16];
  const g = new THREE.Group(); g.userData.role = WK.role(role || 'actuated');
  const body = mesh(new THREE.BoxGeometry(s[0], s[1], s[2]), role || 'actuated');
  body.position.z = (o.rail ? o.rail.userData.height / 2 : 0) + s[2] / 2;
  const nub = mesh(new THREE.BoxGeometry(s[0] * 0.5, s[1] * 0.5, 1.5), role || 'actuated', { shade: 0.6 });
  nub.position.z = body.position.z + s[2] / 2 + 0.7;
  g.add(body, nub);
  g.setT = function (t) {
    const r = g.userData.rail; if (!r) return g;
    const a = r.userData.p0, b = r.userData.p1;
    g.position.copy(a).lerp(b, clamp(t, 0, 1));
    g.quaternion.copy(r.quaternion);
    g.userData.t = t;
    return g;
  };
  g.onRail = function (r, t) { g.userData.rail = r; return g.setT(t == null ? 0 : t); };
  if (o.rail) g.onRail(o.rail, o.t);
  return g;
};
// motor(size,role): NEMA-style block. Shaft points +Z; origin at the mounting face; body extends toward -Z.
P.motor = function (size, role, o) {
  o = o || {};
  const s = size || 42, len = o.length || s * 1.25;
  role = role || 'actuated';
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const sh = o.shade || 1;
  const body = mesh(new THREE.BoxGeometry(s, s, len), role, o.shade ? { shade: sh } : undefined); body.position.z = -len / 2;
  const boss = mesh(orientGeo(new THREE.CylinderGeometry(s * 0.2, s * 0.2, s * 0.06, 24), 'z'), role, { shade: 0.7 * sh }); boss.position.z = s * 0.03;
  const shaft = mesh(orientGeo(new THREE.CylinderGeometry(s * 0.09, s * 0.09, s * 0.5, 16), 'z'), 'work'); shaft.position.z = s * 0.28;
  g.add(body, boss, shaft);
  return g;
};
// ring(radius,tube,{openGap,gapDeg,axis,role}): loop in the XY plane (axis = local Z). openGap shows a latch gap.
P.ring = function (radius, tube, o) {
  o = o || {};
  radius = radius || 20; tube = tube || 2;
  const role = o.role || 'load';
  const gap = o.openGap ? (o.gapDeg || 28) * DEG : 0;
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const arc = mesh(new THREE.TorusGeometry(radius, tube, 10, 56, Math.PI * 2 - gap), role);
  arc.rotation.z = gap / 2;
  g.add(arc);
  if (gap) {
    [gap / 2, -gap / 2].forEach(function (a) {
      const n = mesh(new THREE.SphereGeometry(tube * 1.5, 12, 8), role, { shade: 0.65 });
      n.position.set(Math.cos(a) * radius, Math.sin(a) * radius, 0); g.add(n);
    });
  }
  g.userData.ring = { radius: radius, tube: tube, openGap: !!o.openGap };
  if (o.axis) g.quaternion.setFromUnitVectors(AX.z, v3(o.axis).normalize());
  return g;
};
// spring(p0,p1,{coils,radius,wire,role}): helix that follows its ends; spring.setEnds(p0,p1). Generic primitive.
P.spring = function (p0, p1, o) {
  o = o || {};
  const coils = o.coils || 9, R = o.radius || 4, wire = o.wire || 0.7, role = o.role || 'compliant';
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const m = mesh(new THREE.BufferGeometry(), role); g.add(m);
  let lastL = -1;
  const smooth = t => t * t * (3 - 2 * t);
  function build(L) {
    const N = coils * 16, pts = [];
    for (let i = 0; i <= N; i++) {
      const t = i / N, e = smooth(clamp(t / 0.07, 0, 1)) * smooth(clamp((1 - t) / 0.07, 0, 1)), a = Math.PI * 2 * coils * t;
      pts.push(new V3(R * e * Math.cos(a), R * e * Math.sin(a), L * t));
    }
    m.geometry.dispose();
    m.geometry = new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), N * 2, wire, 5, false);
  }
  g.setEnds = function (a, b) {
    a = v3(a); b = v3(b);
    const d = b.clone().sub(a), L = d.length();
    if (L < 1e-3) return g;
    g.position.copy(a); g.quaternion.setFromUnitVectors(AX.z, d.multiplyScalar(1 / L));
    if (Math.abs(L - lastL) > 0.02) { build(L); lastL = L; }
    g.userData.length = L;
    return g;
  };
  return g.setEnds(p0, p1);
};
// elastic(p0,p1,{role,radius,rest}): thin cord; with `rest` it thins as it stretches. elastic.setEnds(p0,p1).
P.elastic = function (p0, p1, o) {
  o = o || {};
  const r = o.radius || 0.9;
  const m = mesh(new THREE.CylinderGeometry(r, r, 1, 8), o.role || 'compliant');
  m.setEnds = function (a, b) {
    a = v3(a); b = v3(b);
    const L = a.distanceTo(b);
    m.userData.kx = o.rest ? clamp(Math.sqrt(o.rest / Math.max(L, 1e-3)), 0.45, 1.6) : 1;
    m.userData.length = L;
    placeRod(m, a, b);
    return m;
  };
  m.strain = function () { return o.rest ? (m.userData.length - o.rest) / o.rest : 0; };
  return m.setEnds(p0, p1);
};
// cable(points|curve,{radius,role,segments}): tube along a smooth curve; cable.setPoints(pointsOrCurve), .minRadius()
P.cable = function (pts, o) {
  o = o || {};
  const radius = o.radius || 2.5, role = o.role || 'cable';
  const m = mesh(new THREE.BufferGeometry(), role);
  m.setPoints = function (p) {
    let curve = p;
    if (Array.isArray(p)) { const arr = p.map(v3); curve = arr.length < 3 ? new THREE.LineCurve3(arr[0], arr[arr.length - 1]) : new THREE.CatmullRomCurve3(arr, false, 'centripetal'); }
    m.curve = curve;
    m.geometry.dispose();
    m.geometry = new THREE.TubeGeometry(curve, o.segments || 64, radius, 10, false);
    return m;
  };
  m.minRadius = function () { return WK.curveMinRadius(m.curve); };
  return m.setPoints(pts);
};
// arrow(origin,dir,len,role): shaft + head. arrow.set(origin,dir,len)
P.arrow = function (origin, dir, len, role) {
  const g = new THREE.Group(); g.userData.role = WK.role(role || 'laser');
  const shaft = mesh(new THREE.CylinderGeometry(1, 1, 1, 10), role || 'laser', { basic: true });
  const head = mesh(new THREE.ConeGeometry(1, 1, 14), role || 'laser', { basic: true });
  g.add(shaft, head);
  g.set = function (o, d, L) {
    const dv = v3(d).normalize(), sr = Math.max(0.45, L * 0.018), hl = Math.min(L * 0.3, sr * 7), hr = sr * 2.6;
    g.position.copy(v3(o)); g.quaternion.setFromUnitVectors(AX.y, dv);
    shaft.scale.set(sr, Math.max(L - hl, 0.01), sr); shaft.position.y = (L - hl) / 2;
    head.scale.set(hr, hl, hr); head.position.y = L - hl / 2;
    return g;
  };
  return g.set(origin || [0, 0, 0], dir || [0, 0, 1], len || 30);
};
// axes(size): XYZ triad (red/green/blue lines, conventional, not roles).
P.axes = function (size) {
  size = size || 50;
  const g = new THREE.Group();
  [[AX.x, 0xd1495b], [AX.y, 0x5fae7c], [AX.z, 0x4a86e8]].forEach(function (a) {
    const geo = new THREE.BufferGeometry().setFromPoints([new V3(), a[0].clone().multiplyScalar(size)]);
    g.add(new THREE.Line(geo, new THREE.LineBasicMaterial({ color: WK.color(a[1]) })));
  });
  return g;
};
// dashed(points,role,{dash,gap,onTop}): dashed polyline (axes, paths). dashed.setPoints(points)
P.dashed = function (points, role, o) {
  o = o || {};
  const line = new THREE.Line(new THREE.BufferGeometry(), WK.lineMat(role || 'ghost', { dashed: true, dash: o.dash || 4, gap: o.gap || 3, opacity: 0.85, onTop: o.onTop !== false }));
  line.userData.role = WK.role(role || 'ghost'); line.userData.occludes = false;
  line.renderOrder = 5;
  line.setPoints = function (pts) {
    line.geometry.setFromPoints(pts.map(v3)); line.geometry.computeBoundingSphere(); line.computeLineDistances(); return line;
  };
  return line.setPoints(points);
};
// camera({role,fov,size}): little camera body. Lens looks along local -Z (same as THREE.Camera); +Y is up.
// Origin = optical centre. camera.aimAt(target, up) orients -Z at a world point.
P.camera = function (o) {
  o = o || {};
  const s = o.size || 22, role = o.role || 'sensor';
  const g = new THREE.Group(); g.userData.role = WK.role(role); g.userData.occludes = false;   // a camera body must not block its own view (its lens glass is a 'work' part)
  const NO = { occludes: false };
  const body = mesh(new THREE.BoxGeometry(s, s * 0.7, s * 0.8), role, NO); body.position.z = s * 0.4;
  const lens = mesh(orientGeo(new THREE.CylinderGeometry(s * 0.2, s * 0.26, s * 0.34, 20), 'z'), role, { shade: 0.55, occludes: false }); lens.position.z = -s * 0.02;
  const glass = mesh(orientGeo(new THREE.CylinderGeometry(s * 0.15, s * 0.15, s * 0.02, 20), 'z'), 'work', { shade: 0.5, occludes: false }); glass.position.z = -s * 0.2;
  const top = mesh(new THREE.BoxGeometry(s * 0.3, s * 0.12, s * 0.3), role, { shade: 0.7, occludes: false }); top.position.set(0, s * 0.4, s * 0.25);
  g.add(body, lens, glass, top);
  g.userData.fov = o.fov || 45;
  g.aimAt = function (target, up) {
    g.updateWorldMatrix(true, false);
    const eye = new V3().setFromMatrixPosition(g.matrixWorld);
    g.quaternion.setFromRotationMatrix(new THREE.Matrix4().lookAt(eye, v3(target), up ? v3(up) : (Math.abs(v3(target).sub(eye).normalize().z) > 0.98 ? new V3(0, 1, 0) : new V3(0, 0, 1))));
    return g;
  };
  return g;
};
// frustum({fov,aspect,near,far,role}): wireframe view volume in camera-local space (looks along -Z). .set(params)
P.frustum = function (o) {
  o = o || {};
  const role = o.role || 'sensor';
  const geo = new THREE.BufferGeometry();
  const line = new THREE.LineSegments(geo, WK.lineMat(role, { opacity: 0.55 }));
  line.userData.role = WK.role(role); line.userData.occludes = false;
  line.set = function (p) {
    p = Object.assign({ fov: 45, aspect: 4 / 3, near: 8, far: 120 }, o, p || {});
    const tv = Math.tan(p.fov * DEG / 2), c = [];
    [p.near, p.far].forEach(function (z) { const hh = tv * z, ww = hh * p.aspect; c.push([-ww, -hh, -z], [ww, -hh, -z], [ww, hh, -z], [-ww, hh, -z]); });
    const seg = [];
    for (let i = 0; i < 4; i++) {
      seg.push(c[i], c[(i + 1) % 4], c[4 + i], c[4 + (i + 1) % 4], c[i], c[4 + i]);
    }
    seg.push([0, 0, 0], c[4], [0, 0, 0], c[5], [0, 0, 0], c[6], [0, 0, 0], c[7]);
    geo.setFromPoints(seg.map(v3));
    return line;
  };
  return line.set();
};
// pulley(r,w,role): flanged wheel, axis Z.
P.pulley = function (r, w, role) {
  role = role || 'fixed'; r = r || 15; w = w || 8;
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const core = mesh(orientGeo(new THREE.CylinderGeometry(r * 0.82, r * 0.82, w, 32), 'z'), role, { shade: 0.75 });
  [-1, 1].forEach(function (s) { const f = mesh(orientGeo(new THREE.CylinderGeometry(r, r, w * 0.16, 32), 'z'), role); f.position.z = s * w * 0.42; g.add(f); });
  g.add(core);
  return g;
};
// magnet(size,role): disc magnet, two-tone poles along Z.
P.magnet = function (size, role) {
  role = role || 'locate'; size = size || 10;
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const a = mesh(orientGeo(new THREE.CylinderGeometry(size / 2, size / 2, size * 0.25, 24), 'z'), role); a.position.z = size * 0.125;
  const b = mesh(orientGeo(new THREE.CylinderGeometry(size / 2, size / 2, size * 0.25, 24), 'z'), 'work', { shade: 0.9 }); b.position.z = -size * 0.125;
  g.add(a, b);
  return g;
};
// plane(w,h,role): thin translucent sheet (XY plane) with an outline; for plates, tables, cut planes.
P.plane = function (w, hgt, role, o) {
  o = o || {};
  role = role || 'ghost';
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const f = mesh(new THREE.PlaneGeometry(w, hgt), role, { opacity: o.opacity == null ? 0.22 : o.opacity, side: 'double' });
  f.userData.occludes = false;
  const hw = w / 2, hh = hgt / 2;
  const edge = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([new V3(-hw, -hh, 0), new V3(hw, -hh, 0), new V3(hw, hh, 0), new V3(-hw, hh, 0)]), WK.lineMat(role, { opacity: 0.8 }));
  edge.userData.role = WK.role(role); edge.userData.occludes = false;
  g.add(f, edge);
  return g;
};
// groundHatch(size,role): ground/anchor symbol: thin plate with hatch marks below it (-Z). Rotate for walls/ceilings.
P.groundHatch = function (size, role) {
  role = role || 'fixed'; size = size || 30;
  const g = new THREE.Group(); g.userData.role = WK.role(role);
  const plate = mesh(new THREE.BoxGeometry(size, size, 2), role); plate.position.z = -1;
  const pts = [], n = 5;
  for (let i = 0; i <= n; i++) { const x = -size / 2 + (size * i) / n; pts.push(new V3(x, -size / 2, -2), new V3(x - size * 0.16, -size / 2, -2 - size * 0.2)); pts.push(new V3(x, size / 2, -2), new V3(x - size * 0.16, size / 2, -2 - size * 0.2)); }
  const hatch = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), WK.lineMat(role, {}));
  hatch.userData.role = WK.role(role); hatch.userData.occludes = false;
  g.add(plate, hatch);
  return g;
};

// ---------------------------------------------------------------- seam offset (exact scene geometry)
const NOMINAL_SEAM = { cx: 0, cy: 0, amp: 0, beta: 0 };
WK.NOMINAL_SEAM = fz(NOMINAL_SEAM);
// Where is point p relative to the weld seam (circle of radius INNER_RADIUS on the plate face)?
//   radial   distance from the seam circle in plan; + = toward / into the wall, - = over the plate
//   along    arc length along the seam from the weld station (+X axis); + = toward +Y
//   vertical height above the plate face at that angle; + = above the plate, - = inside the plate
// Works for any point (gun dot, pointer tip, camera target). `seam` comes from workstation.seam(): circle centre, runout
// and, when the work has been moved with ws.setWorkPose, the pose (toLocal / toWorld matrices). Without `seam` the page's
// workstation is used (WK.workstation: its current pose, spin and runout); with no workstation the ideal seam.
WK.seamOffset = function (p, seam) {
  p = v3(p);
  const s = seam || (WK.workstation ? WK.workstation.seam() : NOMINAL_SEAM);
  if (s.toLocal) p.applyMatrix4(s.toLocal);        // into the work's own frame (rotator axis = Z)
  const dx = p.x - s.cx, dy = p.y - s.cy, psi = Math.atan2(dy, dx);
  const zFace = CAP_TOP - s.amp * Math.cos(psi - s.beta);
  const radial = Math.hypot(dx, dy) - INNER_RADIUS, along = INNER_RADIUS * psi, vertical = p.z - zFace;
  const joint = new V3(s.cx + INNER_RADIUS * Math.cos(psi), s.cy + INNER_RADIUS * Math.sin(psi), zFace);
  if (s.toWorld) joint.applyMatrix4(s.toWorld);
  return { radial: radial, along: along, vertical: vertical, total: Math.hypot(radial, along, vertical), angleDeg: psi / DEG, joint: joint };
};

// ---------------------------------------------------------------- workstation (rotator, bench, tube, endcap)
// Layout of the rotator's towers is a PROXY built from the documented dimensions (rig doc, rotator README):
// base 300x250x12 on four 24 mm feet, tube bottom 62 mm above the base bottom (86 mm above the bench),
// 150 mm nest, motor tower on -X, ground tower on +Y. The gun lives on the -Y / +X side.
WK.addWorkstation = function (app, o) {
  o = Object.assign({ rotator: true, bench: true, tube: true, cap: true, benchZ: -WK.RIG.benchToTubeBottom, ghostTube: false,
    benchSize: [860, 700], benchCenter: [0, -120], grid: true, indexDeg: 160 }, o || {});
  const RG = WK.RIG, H = DIM.tubeHeight, RO = DIM.tubeOd / 2, RI = INNER_RADIUS;
  const root = new THREE.Group(); root.name = 'workstation';
  // `work` carries everything that belongs to the workpiece (rotator, turntable, tube, cap) so ws.setWorkPose can move it
  // as one rigid body while the bench and grid stay. Identity by default.
  const work = new THREE.Group(); work.name = 'work: rotator + tube (pose)';
  root.add(work);
  const ws = { group: root, work: work, benchZ: o.benchZ, spin: { on: false, speedDegPerSec: RG.degPerSecNominal }, spinAngle: 0,
    runout: { on: false, radialTIR: 0, faceTIR: 0, exaggeration: 1, phaseRadial: 0, phaseFace: 1.05 }, parts: {} };
  const rotZ = -RG.benchToTubeBottom;               // bottom of the feet (rotator datum, independent of benchZ)
  const baseBottom = rotZ + RG.footH;               // -62
  const baseTop = baseBottom + RG.baseZ;            // -50

  function fixedBox(w, d, hh, x, y, z, role, opts) { const m = P.box(w, d, hh, role || 'fixed', opts); m.position.set(x, y, z); return m; }

  if (o.bench) {
    const bw = o.benchSize[0], bd = o.benchSize[1], cx = o.benchCenter[0], cy = o.benchCenter[1];
    const slab = mesh(new THREE.BoxGeometry(bw, bd, 20), 'fixed', { opacity: 0.32, occludes: false });
    slab.position.set(cx, cy, ws.benchZ - 10); slab.userData.occludes = false; slab.name = 'bench';
    root.add(slab); ws.bench = slab;
    if (o.grid) {
      const pts = [], z = ws.benchZ + 0.15, step = 50;
      for (let x = Math.ceil((cx - bw / 2) / step) * step; x <= cx + bw / 2; x += step) pts.push(new V3(x, cy - bd / 2, z), new V3(x, cy + bd / 2, z));
      for (let y = Math.ceil((cy - bd / 2) / step) * step; y <= cy + bd / 2; y += step) pts.push(new V3(cx - bw / 2, y, z), new V3(cx + bw / 2, y, z));
      const grid = new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), WK.lineMat('fixed', { opacity: 0.45 }));
      grid.userData.role = 'fixed'; grid.userData.occludes = false;
      root.add(grid); ws.grid = grid;
    }
  }

  if (o.rotator) {
    const rot = new THREE.Group(); rot.name = 'rotator (proxy)';
    [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (s) { rot.add(fixedBox(36, 36, RG.footH, s[0] * 126, s[1] * 101, rotZ + RG.footH / 2)); });
    rot.add(fixedBox(RG.baseX, RG.baseY, RG.baseZ, 0, 0, baseBottom + RG.baseZ / 2));
    // lower bearing race ring (165 mm pitch circle) - decoration that reads as "ball race"
    const race = mesh(new THREE.LatheGeometry([[75, baseTop], [90, baseTop], [90, baseTop + 4], [75, baseTop + 4], [75, baseTop]].map(p => new THREE.Vector2(p[0], p[1])), 64).rotateX(Math.PI / 2), 'fixed', { shade: 0.7, side: 'double' });
    rot.add(race);
    // motor tower: rear wall + two rails; motor hangs face-down (shaft toward the base)
    rot.add(fixedBox(10, 80, 100, -141, 0, baseTop + 50));
    rot.add(fixedBox(46, 10, 60, -123, 33, baseTop + 30));
    rot.add(fixedBox(46, 10, 60, -123, -33, baseTop + 30));
    const motor = P.motor(57.3, 'actuated', { length: 76, shade: 0.55 });
    motor.rotation.x = Math.PI; motor.position.set(-125.1, 0, baseBottom + 53.35);
    rot.add(motor); ws.parts.motor = motor;
    // ground tower (continuity shoe on the tube OD)
    rot.add(fixedBox(40, 24, 79, 0, 96, baseTop + 39.5));
    rot.add(fixedBox(25, 26, 8, 0, 76, 26));
    work.add(rot); ws.rotator = rot;

    // turntable + nest: one lathe with the 90 mm service bore; spins with the tube.
    const prof = [[45, -34], [98, -34], [98, -10], [75, -10], [75, 20], [63.9, 20], [63.9, 0], [45, 0], [45, -34]].map(p => new THREE.Vector2(p[0], p[1]));
    const tt = new THREE.Group(); tt.name = 'turntable + nest (spins)';
    const ttMesh = mesh(new THREE.LatheGeometry(prof, 96).rotateX(Math.PI / 2), 'actuated', { shade: 0.5, side: 'double' });
    tt.add(ttMesh);
    const tick = P.box(10, 3, 2, 'locate');   // rim tick shows rotation even with a ghost tube
    tick.position.set(96 * Math.cos(o.indexDeg * DEG), 96 * Math.sin(o.indexDeg * DEG), -9); tick.rotation.z = o.indexDeg * DEG;
    tt.add(tick);
    work.add(tt); ws.turntable = tt; ws.parts.turntableMesh = ttMesh; ws.parts.turntableTick = tick;
  } else {
    ws.turntable = new THREE.Group(); work.add(ws.turntable);
  }

  // ---- tube + endcap (+ weld circle, index marks). tubeGroup carries spin + runout.
  const tg = new THREE.Group(); tg.name = 'tube + endcap'; tg.matrixAutoUpdate = false;
  work.add(tg); ws.tubeGroup = tg;
  if (o.tube) {
    const profile = [[RO, 0], [RO, H], [RI, H], [RI, 0], [RO, 0]].map(p => new THREE.Vector2(p[0], p[1]));
    const tubeGeo = new THREE.LatheGeometry(profile, 160); tubeGeo.rotateX(Math.PI / 2);
    const tube = mesh(tubeGeo, 'work', { side: 'double' }); tube.name = 'tube'; tg.add(tube); ws.tube = tube;
    if (o.cap) {
      const shape = new THREE.Shape(); shape.absarc(0, 0, DIM.capDiameter / 2, 0, Math.PI * 2, false);
      [-DIM.portOffset, DIM.portOffset].forEach(function (x) { const hole = new THREE.Path(); hole.absarc(x, 0, DIM.portDiameter / 2, 0, Math.PI * 2, true); shape.holes.push(hole); });
      const cg = new THREE.ExtrudeGeometry(shape, { depth: DIM.capThickness, bevelEnabled: false, curveSegments: 48 });
      cg.translate(0, 0, CAP_TOP - DIM.capThickness);
      const cap = mesh(cg, 'work', { shade: 0.62, side: 'double' }); cap.name = 'recessed endcap'; tg.add(cap); ws.cap = cap;
    }
    // rim circles + weld circle (thin torus so it stays visible at any zoom)
    [[RO, H], [RI, H]].forEach(function (rz) {
      const pts = []; for (let i = 0; i <= 160; i++) { const a = i / 160 * Math.PI * 2; pts.push(new V3(rz[0] * Math.cos(a), rz[0] * Math.sin(a), rz[1])); }
      const l = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), WK.lineMat('work', { opacity: 0.6 })); l.userData.role = 'work'; l.userData.occludes = false; tg.add(l);
    });
    const weld = mesh(new THREE.TorusGeometry(RI, 0.45, 6, 160), 'locate', { basic: true }); weld.position.z = CAP_TOP + 0.3; weld.name = 'weld circle'; weld.userData.occludes = false; tg.add(weld); ws.weldCircle = weld;
    // index stripe on the OD + radial tick on the plate face: rotation is readable without labels
    const phi = o.indexDeg * DEG, half = 3 * DEG;
    const sg = new THREE.CylinderGeometry(RO + 0.15, RO + 0.15, H, 4, 1, true, phi + Math.PI / 2 - half, half * 2); sg.rotateX(Math.PI / 2); sg.translate(0, 0, H / 2);
    const stripe = mesh(sg, 'locate', { side: 'double', basic: true }); stripe.userData.occludes = false; tg.add(stripe);
    const rtick = P.box(RI - 12, 1.6, 0.4, 'locate', { basic: true }); rtick.userData.occludes = false;
    rtick.position.set(Math.cos(phi) * (RI + 10) / 2, Math.sin(phi) * (RI + 10) / 2, CAP_TOP + 0.25); rtick.rotation.z = phi; tg.add(rtick);
    ws.parts.stripe = stripe; ws.parts.plateTick = rtick;
  }

  // ---- ghost (semi-transparent tube/cap so an observer camera inside/around still reads the scene)
  ws.setGhost = function (on) {
    ws.ghost = !!on;
    if (ws.tube) ws.tube.material = WK.mat('work', on ? { side: 'double', opacity: 0.28 } : { side: 'double' });
    if (ws.cap) ws.cap.material = WK.mat('work', on ? { shade: 0.62, side: 'double', opacity: 0.55 } : { shade: 0.62, side: 'double' });
    app.invalidate();
    return ws;
  };

  // ---- spin + illustrative runout
  const M = new THREE.Matrix4(), T1 = new THREE.Matrix4(), T2 = new THREE.Matrix4(), Rt = new THREE.Matrix4(), Tp = new THREE.Matrix4(), Tn = new THREE.Matrix4();
  function wobble() {
    const r = ws.runout, th = ws.spinAngle * DEG;
    M.makeRotationZ(th);
    if (r.on) {
      const ecc = r.radialTIR / 2 * r.exaggeration, a = r.faceTIR / 2 * r.exaggeration;
      const b1 = th + r.phaseRadial, b2 = th + r.phaseFace;
      const n = new V3(-Math.sin(b2), Math.cos(b2), 0);
      Rt.makeRotationAxis(n, a / RI);
      Tp.makeTranslation(0, 0, CAP_TOP); Tn.makeTranslation(0, 0, -CAP_TOP);
      T1.makeTranslation(ecc * Math.cos(b1), ecc * Math.sin(b1), 0);
      M.premultiply(Tn).premultiply(Rt).premultiply(Tp).premultiply(T1);
    }
    tg.matrix.copy(M); tg.matrixWorldNeedsUpdate = true;
  }
  ws.setSpin = function (deg) {
    ws.spinAngle = ((deg % 360) + 360) % 360;
    ws.turntable.rotation.z = ws.spinAngle * DEG;
    wobble();
    app.invalidate();
    return ws;
  };
  // Illustrative wobble: indicated runout (total indicator reading, mm) makes the joint move under a fixed
  // gun. Rig-doc limits are 0.25 mm radial / 0.30 mm face; exaggeration (x1..x40) makes it visible. Not measured.
  ws.setRunout = function (radialTIR, faceTIR, exaggeration) {
    const r = ws.runout;
    r.radialTIR = radialTIR == null ? r.radialTIR : radialTIR;
    r.faceTIR = faceTIR == null ? r.faceTIR : faceTIR;
    r.exaggeration = exaggeration == null ? r.exaggeration : exaggeration;
    r.on = r.radialTIR > 0 || r.faceTIR > 0;
    wobble(); app.invalidate();
    return ws;
  };
  // ---- work pose: the rotator, turntable, tube and cap move as one rigid body; bench and grid stay.
  // Pose is relative to ws.group (identity by default); rotation is about the work frame origin (tube axis, tube bottom,
  // z = 0). pose.m / pose.inv are replaced, never mutated, so a seam object taken earlier stays valid.
  let pose = { m: new THREE.Matrix4(), inv: new THREE.Matrix4(), identity: true };
  ws.setWorkPose = function (position, quaternion, po) {
    work.position.copy(v3(position));
    if (!quaternion) work.quaternion.identity();
    else if (quaternion.isQuaternion) work.quaternion.copy(quaternion);
    else if (quaternion.isEuler) work.quaternion.setFromEuler(quaternion);
    else work.quaternion.set(quaternion[0], quaternion[1], quaternion[2], quaternion[3]);
    if (po && po.about) {   // rotate about this point (ws.group frame) instead of the work origin: position then shifts the pivot
      const c = v3(po.about), moved = c.clone().applyQuaternion(work.quaternion);
      work.position.add(c.sub(moved));
    }
    work.updateMatrix();
    const m = work.matrix.clone();
    pose = { m: m, inv: m.clone().invert(), identity: m.equals(new THREE.Matrix4()) };
    work.matrixWorldNeedsUpdate = true;
    app.invalidate();
    return ws;
  };
  ws.workPose = function () { return { position: work.position.clone(), quaternion: work.quaternion.clone() }; };
  // The work-frame seam at the weld station (+X of the work frame), including runout. First-order maths.
  function jointLocal() {
    const r = ws.runout;
    if (!r.on) return new V3(RI, 0, CAP_TOP);
    const th = ws.spinAngle * DEG, ecc = r.radialTIR / 2 * r.exaggeration, a = r.faceTIR / 2 * r.exaggeration;
    const ex = ecc * Math.cos(th + r.phaseRadial), ey = ecc * Math.sin(th + r.phaseRadial);
    return new V3(ex + Math.sqrt(Math.max(0, RI * RI - ey * ey)), 0, CAP_TOP - a * Math.cos(th + r.phaseFace));
  }
  // Where the seam currently is at the work's +X station: work pose, spin and runout included. World / group frame.
  ws.jointNow = function () { const j = jointLocal(); return pose.identity ? j : j.applyMatrix4(pose.m); };
  // Current seam descriptor (circle centre, face-tilt amplitude and phase in the work frame, plus the pose matrices when
  // the work has been moved). Feed it to WK.seamOffset(p, seam); ws.offsetOf(p) does that for you.
  ws.seam = function () {
    const r = ws.runout, s = !r.on ? NOMINAL_SEAM : (function () {
      const th = ws.spinAngle * DEG, ecc = r.radialTIR / 2 * r.exaggeration;
      return { cx: ecc * Math.cos(th + r.phaseRadial), cy: ecc * Math.sin(th + r.phaseRadial), amp: r.faceTIR / 2 * r.exaggeration, beta: th + r.phaseFace };
    })();
    return pose.identity ? s : { cx: s.cx, cy: s.cy, amp: s.amp, beta: s.beta, toLocal: pose.inv, toWorld: pose.m };
  };
  ws.offsetOf = function (point) { return WK.seamOffset(point, ws.seam()); };
  app.onFrame(function (dt) {
    if (!ws.spin.on) return false;
    ws.setSpin(ws.spinAngle + ws.spin.speedDegPerSec * dt);
    return true;
  });
  ws.setSpin(o.spinDeg || 0);
  if (o.ghostTube) ws.setGhost(true);
  app.add(root);
  WK.workstation = ws;
  return ws;
};

// ---------------------------------------------------------------- gun (proxy of the XLaserlab X1 Pro)
// Local frame: origin = nozzle tip, +Z toward the back of the gun, -Y = grip side, dot at (0,0,-16).
// Proxy envelope follows the manual's 253 x 143 x 34 mm drawing; sections, grip, guide are illustrative.
WK.addGun = function (app, o) {
  o = Object.assign({ shell: false, umbilical: true, wire: true, dotMarker: true, pose: 'opening' }, o || {});
  const g = new THREE.Group(); g.name = 'X1 Pro gun proxy';
  const gun = { group: g, app: app, dials: { roll: WK.OPENING.roll, holeDial: WK.OPENING.holeDial, vertical: WK.OPENING.vertical }, laserOn: false, laserTargets: null };
  const A = v3;

  function cylBetween(parent, a, b, rA, rB, role, opts) {
    a = A(a); b = A(b);
    const d = b.clone().sub(a);
    const m = mesh(new THREE.CylinderGeometry(rB, rA, d.length(), 24), role, opts);
    m.position.copy(a).add(b).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(AX.y, d.normalize());
    parent.add(m); return m;
  }
  const body = new THREE.Group(); body.name = 'gun body'; g.add(body); gun.body = body;
  cylBetween(body, [0, 0, 0], [0, 0, 23], 2.2, 5, 'gun', { shade: 0.6 });
  cylBetween(body, [0, 0, 23], [0, 0, 54], 8.5, 8.5, 'gun', { shade: 1.4 });
  cylBetween(body, [0, 0, 54], [0, 0, 100], 5.5, 5.5, 'gun', { shade: 1.4 });
  cylBetween(body, [0, 0, 100], [0, 0, 118], 12, 12, 'gun', { shade: 0.6 });
  const housing = mesh(new THREE.BoxGeometry(DIM.gunWidth, 34, 135), 'gun'); housing.position.set(0, 0, 185.5); body.add(housing);
  const gripStart = new V3(0, -25, 172), gripEnd = new V3(0, -111, 232);
  const gripLen = gripStart.distanceTo(gripEnd), gripDir = gripEnd.clone().sub(gripStart).normalize();
  const grip = mesh(new THREE.BoxGeometry(30, gripLen + 16, 28), 'gun', { shade: 0.6 });
  grip.position.copy(gripStart).add(gripEnd).multiplyScalar(0.5);
  grip.quaternion.setFromUnitVectors(AX.y, gripDir); body.add(grip);
  gun.parts = { housing: housing, grip: grip };

  // umbilical stub (5.5 mm radius) leaves the grip base; the external wire conduit runs beside it
  const base = A(GRIP_BASE_ARR), axis = A(LOCAL_ROLL_AXIS_ARR);
  if (o.umbilical) {
    const cableEnd = base.clone().addScaledVector(axis, 70);
    const cc = new THREE.CubicBezierCurve3(base, base.clone().addScaledVector(gripDir, 24), cableEnd.clone().addScaledVector(axis, -25), cableEnd);
    const um = mesh(new THREE.TubeGeometry(cc, 32, 5.5, 12, false), 'cable'); um.name = 'umbilical stub';
    const cap = mesh(new THREE.SphereGeometry(5.5, 12, 8), 'cable'); cap.position.copy(cableEnd);
    const ug = new THREE.Group(); ug.userData.role = 'cable'; ug.add(um, cap); g.add(ug); gun.umbilical = ug;
  }
  const guideBack = A(WIRE_GUIDE_BACK_ARR), guideEnd = A(WIRE_GUIDE_END_ARR), wireTip = A(WIRE_TIP_ARR);
  const feedAtGrip = base.clone().add(new V3(23, 0, 0));
  const feedTail = feedAtGrip.clone().addScaledVector(axis, 70), feedBend = feedAtGrip.clone().addScaledVector(axis, -35);
  if (o.wire) {
    const wg = new THREE.Group(); wg.name = 'wire guide + wire + feed conduit'; wg.userData.role = 'wire';
    cylBetween(wg, guideBack, guideEnd, 2.5, 2.5, 'cable');                   // straight tip guide
    cylBetween(wg, A(WIRE_BRACE_MOUNT_ARR), guideBack, 2, 2, 'gun');          // support leg to the barrel collar
    cylBetween(wg, guideEnd, wireTip, 0.48, 0.48, 'wire', { occludes: false });   // 0.48 mm wire, guide to dot (too thin to block a view)
    const feed = new THREE.CurvePath();
    feed.add(new THREE.LineCurve3(feedTail, feedBend));
    // both bezier end tangents follow the adjacent straight runs (as in the reference scene)
    feed.add(new THREE.CubicBezierCurve3(feedBend, feedBend.clone().addScaledVector(axis, -50), guideBack.clone().addScaledVector(A(WIRE_GUIDE_DIR_ARR), 45), guideBack));
    const fm = mesh(new THREE.TubeGeometry(feed, 64, 1.8, 10, false), 'wire'); fm.name = 'external wire-feed conduit';
    wg.add(fm); g.add(wg); gun.wire = wg;
  }
  if (o.dotMarker) { const dm = mesh(new THREE.SphereGeometry(1.4, 14, 10), 'laser'); dm.position.set(0, 0, -CLEARANCE); dm.userData.occludes = false; g.add(dm); gun.dotMarker = dm; }

  // ---- anchors: named local points (approximate proxy positions)
  const front = new V3(0, -gripDir.z, gripDir.y);   // grip's face toward the nozzle
  const A_ = {
    nozzleTip: [0, 0, 0], dot: [0, 0, -CLEARANCE], barrelMid: [0, 0, 77], collar: [0, 0, 109],
    housingTop: [0, 17, 185.5], housingBack: [0, 0, 253],
    gripTop: gripStart.toArray(), gripMid: gripStart.clone().add(gripEnd).multiplyScalar(0.5).toArray(), gripBase: GRIP_BASE_ARR.slice(), cableExit: GRIP_BASE_ARR.slice(),
    cablePair: base.clone().addScaledVector(axis, 20).add(new V3(11.5, 0, 0)).toArray(),      // centre of umbilical + wire feed bundle
    umbilicalMid: base.clone().addScaledVector(axis, 35).toArray(),
    wireGuide: guideBack.clone().add(guideEnd).multiplyScalar(0.5).toArray(), wireGuideEnd: guideEnd.toArray(), wireBracket: WIRE_BRACE_MOUNT_ARR.slice(),
    trigger: gripStart.clone().addScaledVector(gripDir, 22).addScaledVector(front, 15).toArray(),   // proxy: front face of the grip
  };
  gun.anchors = {};
  Object.keys(A_).forEach(function (k) { gun.anchors[k] = A(A_[k]); });
  gun.anchorNames = function () { return Object.keys(gun.anchors); };
  gun.anchor = function (where) {
    if (typeof where === 'string') {
      if (!gun.anchors[where]) throw new Error('WK gun: unknown anchor "' + where + '". Known: ' + gun.anchorNames().join(', '));
      return gun.anchors[where].clone();
    }
    return v3(where);
  };

  // ---- pose
  gun.setDials = function (roll, holeDial, vertical) {
    const p = WK.dialsToPose(roll, holeDial, vertical);
    g.position.copy(p.position); g.quaternion.copy(p.quaternion);
    gun.dials = { roll: roll, holeDial: holeDial, vertical: vertical };
    app.invalidate();
    return gun;
  };
  // Free 6-DoF placement for arrangements that do not use the three dials.
  gun.setTransform = function (position, quaternion) {
    g.position.copy(v3(position));
    if (quaternion) { if (quaternion.isQuaternion) g.quaternion.copy(quaternion); else if (quaternion.isEuler) g.quaternion.setFromEuler(quaternion); else g.quaternion.set(quaternion[0], quaternion[1], quaternion[2], quaternion[3]); }
    app.invalidate();
    return gun;
  };
  gun.local = function (where) {   // local point or anchor name -> world Vector3
    g.updateWorldMatrix(true, false);
    return g.localToWorld(gun.anchor(where));
  };
  gun.dotWorld = function () { return gun.local('dot'); };
  gun.dir = function (localDir) { g.updateWorldMatrix(true, false); return v3(localDir).transformDirection(g.matrixWorld); };
  // Beam direction (nozzle toward dot), world.
  gun.beamDir = function () { return gun.dir([0, 0, -1]); };
  gun.frame = function () {
    return { origin: gun.local('nozzleTip'), x: gun.dir([1, 0, 0]), y: gun.dir([0, 1, 0]), z: gun.dir([0, 0, 1]), beamDir: gun.beamDir(), dot: gun.dotWorld() };
  };
  // Dot relative to the seam (see WK.seamOffset): radial / along / vertical / total, plus the seam point `joint`.
  // Exact scene geometry, follows illustrative runout when a workstation with runout is present.
  gun.dotOffset = function () { return app.workstation ? app.workstation.offsetOf(gun.dotWorld()) : WK.seamOffset(gun.dotWorld()); };
  // First drawn surface (tube / cap) the beam hits: where the light lands, as opposed to the dot (a point in space).
  // Same result shape as WK.beamSurfacePoint; o.targets defaults to gun.laserTargets, else the workstation's tube and cap.
  gun.beamSurfacePoint = function (bo) { return WK.beamSurfacePoint(gun.local('nozzleTip'), gun.beamDir(), Object.assign({ targets: gun.laserTargets || undefined }, bo || {})); };
  gun.cableExit = function () { return { point: gun.local('cableExit'), dir: gun.dir(axis) }; };
  gun.wireExit = function () { return { point: gun.local(feedTail.toArray()), dir: gun.dir(axis) }; };

  // ---- laser (optional): beam + a short 2 mm sweep intersected with tube/cap, as in the reference scene.
  const laser = new THREE.Group(); laser.name = 'laser'; laser.visible = false; laser.userData.role = 'laser';
  const beamGeo = new THREE.BufferGeometry().setFromPoints([new V3(), new V3(0, 0, 1)]);
  const beam = new THREE.Line(beamGeo, WK.lineMat('laser', {})); beam.userData.role = 'laser'; beam.userData.occludes = false;
  const sweepGeo = new THREE.BufferGeometry(); sweepGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(41 * 2 * 3), 3)); sweepGeo.setDrawRange(0, 0);
  const sweep = new THREE.LineSegments(sweepGeo, WK.lineMat('laser', { onTop: true })); sweep.frustumCulled = false; sweep.userData.role = 'laser'; sweep.userData.occludes = false;
  const fanGeo = new THREE.BufferGeometry(); fanGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(9), 3));
  const fan = new THREE.Mesh(fanGeo, WK.mat('laser', { opacity: 0.14, side: 'double' })); fan.frustumCulled = false; fan.userData.role = 'laser'; fan.userData.occludes = false; fan.visible = false;
  beam.frustumCulled = false;
  laser.add(beam, sweep, fan); app.add(laser);
  gun.laser = laser;
  const rc = new THREE.Raycaster();
  gun.laserOpts = { sweepMm: 2, offsetMm: 0 };
  gun.updateLaser = function () {
    if (!gun.laserOn) return;
    g.updateWorldMatrix(true, true);
    const targets = gun.laserTargets || (app.workstation ? [app.workstation.tube, app.workstation.cap].filter(Boolean) : []);
    targets.forEach(function (t) { t.updateWorldMatrix(true, false); });
    const origin = gun.local('nozzleTip'), hits = [], sw = gun.laserOpts.sweepMm, oc = gun.laserOpts.offsetMm;
    if (targets.length) for (let i = 0; i <= 40; i++) {
      const focal = gun.local([oc + sw * (i / 40 - 0.5), 0, -CLEARANCE]);   // sweep along gun-local X, centred on the offset
      rc.set(origin, focal.clone().sub(origin).normalize());
      const hit = rc.intersectObjects(targets, false)[0];
      hits.push(hit ? hit.point : null);
    }
    const sp = sweepGeo.attributes.position.array; let n = 0;
    const gap = Math.max(1, sw / 40 * 2);   // neighbours further apart than this are different surfaces (edge, wall to plate)
    for (let i = 1; i < hits.length; i++) {
      if (hits[i] && hits[i - 1] && hits[i].distanceTo(hits[i - 1]) < gap) { hits[i - 1].toArray(sp, n * 3); hits[i].toArray(sp, (n + 1) * 3); n += 2; }
    }
    sweepGeo.setDrawRange(0, n); sweepGeo.attributes.position.needsUpdate = true;
    const good = hits.filter(Boolean);
    const end = good.length ? good[Math.floor(good.length / 2)] : gun.dotWorld();
    beamGeo.setFromPoints([origin, end]); beamGeo.computeBoundingSphere();
    if (good.length) { origin.toArray(fanGeo.attributes.position.array, 0); good[0].toArray(fanGeo.attributes.position.array, 3); good[good.length - 1].toArray(fanGeo.attributes.position.array, 6); fanGeo.attributes.position.needsUpdate = true; fanGeo.computeVertexNormals(); fanGeo.computeBoundingSphere(); }
    fan.visible = good.length > 0;
  };
  // setLaser(on, {sweepMm: 2, offsetMm: 0}): the sweep is sweepMm long along the gun's local X (across the seam) and centred
  // offsetMm from the dot along it. Options persist until changed, so a toggle can call setLaser(v) alone.
  gun.setLaser = function (on, lo) {
    if (lo) { if (lo.sweepMm != null) gun.laserOpts.sweepMm = Math.max(0.01, +lo.sweepMm); if (lo.offsetMm != null) gun.laserOpts.offsetMm = +lo.offsetMm; }
    gun.laserOn = !!on; laser.visible = !!on; if (on) gun.updateLaser(); app.invalidate(); return gun;
  };
  app._before.push(function () { if (gun.laserOn) gun.updateLaser(); });

  // ---- shell: a printed sleeve proxy wrapping the gun; attachments (lugs) can go anywhere on it.
  // Zones ranked nozzle(0) < barrel(1) < housing(2) < grip(3); from/to pick which zones the sleeve covers.
  const RANK = { nozzleTip: 0, dot: 0, barrelMid: 1, collar: 1, wireGuide: 1, wireGuideEnd: 0, wireBracket: 1, housingTop: 2, housingBack: 2, trigger: 3, gripTop: 3, gripMid: 3, gripBase: 3, cableExit: 3, cablePair: 3, umbilicalMid: 3 };
  gun.addShell = function (so) {
    so = Object.assign({ style: 'sleeve', from: 'nozzleTip', to: 'gripBase', clearance: 3, role: 'load', opacity: 0.26 }, so || {});
    const c = so.clearance, sg = new THREE.Group(); sg.name = 'printed shell (proxy)'; sg.userData.role = WK.role(so.role);
    const zones = [
      { rank: 0, type: 'cyl', z0: 0, z1: 23, r0: 2.2 + c, r1: 5 + c },
      { rank: 1, type: 'cyl', z0: 23, z1: 54, r0: 8.5 + c, r1: 8.5 + c },
      { rank: 1, type: 'cyl', z0: 54, z1: 100, r0: 5.5 + c, r1: 5.5 + c },
      { rank: 1, type: 'cyl', z0: 100, z1: 118, r0: 12 + c, r1: 12 + c },
      { rank: 2, type: 'box', center: new V3(0, 0, 185.5), quat: new THREE.Quaternion(), half: new V3(17 + c, 17 + c, 67.5 + c) },
      { rank: 3, type: 'box', center: gripStart.clone().add(gripEnd).multiplyScalar(0.5), quat: grip.quaternion.clone(), half: new V3(15 + c, (gripLen + 16) / 2 + c, 14 + c) },
    ];
    const nearest = (function () { const k = RANK[typeof so.from === 'string' ? so.from : ''], k2 = RANK[typeof so.to === 'string' ? so.to : '']; return [k == null ? 0 : k, k2 == null ? 3 : k2]; })();
    const lo = Math.min(nearest[0], nearest[1]), hi = Math.max(nearest[0], nearest[1]);
    const active = zones.filter(z => z.rank >= lo && z.rank <= hi);
    const fillMat = WK.mat(so.role, { opacity: so.opacity, side: 'double' });
    active.forEach(function (z) {
      let geo;
      if (z.type === 'cyl') { geo = new THREE.CylinderGeometry(z.r1, z.r0, z.z1 - z.z0, 32, 1, false); geo.rotateX(Math.PI / 2); geo.translate(0, 0, (z.z0 + z.z1) / 2); }
      else { geo = new THREE.BoxGeometry(z.half.x * 2, z.half.y * 2, z.half.z * 2); geo.applyQuaternion(z.quat); geo.translate(z.center.x, z.center.y, z.center.z); }
      if (so.style !== 'frame') { const m = new THREE.Mesh(geo, fillMat); m.userData.role = WK.role(so.role); m.userData.occludes = false; sg.add(m); }
      const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 25), WK.lineMat(so.role, { opacity: 0.7 })); e.userData.role = WK.role(so.role); e.userData.occludes = false; sg.add(e);
    });
    g.add(sg);
    const shell = { group: sg, zones: active, role: so.role, lugs: [] };
    // point on the shell surface for an anchor/local point. side = hint (name or vector) for which way to exit.
    const SIDES = { top: [0, 1, 0], grip: [0, -1, 0], left: [-1, 0, 0], right: [1, 0, 0], back: [0, 0, 1], front: [0, 0, -1] };
    function surface(p, dir) {
      let best = null;
      active.forEach(function (z) {
        let pt, nrm, dist;
        if (z.type === 'cyl') {
          const zc = clamp(p.z, z.z0, z.z1), r = z.r0 + (z.r1 - z.r0) * (zc - z.z0) / (z.z1 - z.z0), rad = Math.hypot(p.x, p.y);
          const inside = rad < r && p.z >= z.z0 && p.z <= z.z1;
          let ux = p.x, uy = p.y, ul = rad;
          if (inside || rad < 1e-6) { ux = dir.x; uy = dir.y; ul = Math.hypot(ux, uy); if (ul < 1e-6) { ux = 0; uy = 1; ul = 1; } }
          pt = new V3(ux / ul * r, uy / ul * r, zc); nrm = new V3(ux / ul, uy / ul, 0); dist = inside ? 0 : Math.hypot(rad - r, p.z - zc);
        } else {
          const inv = z.quat.clone().invert(), q = p.clone().sub(z.center).applyQuaternion(inv), d = dir.clone().applyQuaternion(inv);
          const inside = Math.abs(q.x) < z.half.x && Math.abs(q.y) < z.half.y && Math.abs(q.z) < z.half.z;
          let s;
          if (inside) {
            let t = Infinity; ['x', 'y', 'z'].forEach(function (k) { if (Math.abs(d[k]) > 1e-6) { const tt = ((d[k] > 0 ? z.half[k] : -z.half[k]) - q[k]) / d[k]; if (tt >= 0 && tt < t) t = tt; } });
            s = q.clone().addScaledVector(d, isFinite(t) ? t : 0);
          } else s = new V3(clamp(q.x, -z.half.x, z.half.x), clamp(q.y, -z.half.y, z.half.y), clamp(q.z, -z.half.z, z.half.z));
          let k = 'x', mx = -1; ['x', 'y', 'z'].forEach(function (a) { const r = Math.abs(s[a]) / z.half[a]; if (r > mx) { mx = r; k = a; } });
          const nl = new V3(); nl[k] = s[k] >= 0 ? 1 : -1;
          pt = s.clone().applyQuaternion(z.quat).add(z.center); nrm = nl.applyQuaternion(z.quat);
          dist = inside ? 0 : q.distanceTo(s);
        }
        if (!best || dist < best.dist) best = { pt: pt, nrm: nrm, dist: dist };
      });
      return best;
    }
    // shell.attachPoint(nameOrLocalPoint, {side, role, size}) -> {lug, local, normal, world()} ; lug is a small pad marker
    shell.attachPoint = function (where, ao) {
      ao = ao || {};
      const p = gun.anchor(where);
      const dir = typeof ao.side === 'string' ? v3(SIDES[ao.side] || SIDES.top) : (ao.side ? v3(ao.side) : v3(SIDES.top));
      const s = surface(p, dir.normalize());
      if (!s) return null;
      const lug = new THREE.Group(); lug.userData.role = WK.role(ao.role || 'load');
      const sz = ao.size || 6;
      const pad = mesh(new THREE.BoxGeometry(sz, sz, 2), ao.role || 'load'); pad.position.z = 1;
      const eye = mesh(new THREE.SphereGeometry(sz * 0.32, 12, 8), ao.role || 'load', { shade: 1.25 }); eye.position.z = 3.2;
      lug.add(pad, eye);
      lug.position.copy(s.pt); lug.quaternion.setFromUnitVectors(AX.z, s.nrm);
      g.add(lug);
      const rec = { lug: lug, local: s.pt.clone(), normal: s.nrm.clone(), world: function () { return gun.local(s.pt); } };
      shell.lugs.push(rec);
      return rec;
    };
    gun.shell = shell;
    app.invalidate();
    return shell;
  };

  // ---- ring: an openable loop around the gun at a location; the group follows the gun.
  // Generic building block. axis defaults follow the zone (barrel/housing: local Z; grip: grip direction).
  gun.addRing = function (where, ro) {
    ro = ro || {};
    let c = gun.anchor(where), ax, r;
    const isBundle = where === 'cablePair' || where === 'umbilicalMid';
    if (isBundle) { ax = axis.clone(); r = 21; }
    else {
      const dAxis = Math.hypot(c.x, c.y), tg = clamp(c.clone().sub(gripStart).dot(gripDir), 0, gripLen), onGrip = gripStart.clone().addScaledVector(gripDir, tg);
      const dGrip = c.distanceTo(onGrip);
      if (c.z >= 118 && dAxis - 24 <= dGrip - 21) { ax = AX.z.clone(); r = 26.5; c = new V3(0, 0, c.z); }
      else if (c.z < 118) { ax = AX.z.clone(); r = (c.z < 23 ? 2.2 + 2.8 * c.z / 23 : c.z < 54 ? 8.5 : c.z < 100 ? 5.5 : 12) + 3; c = new V3(0, 0, c.z); }
      else { ax = gripDir.clone(); r = 23; c = onGrip; }
    }
    const ring = P.ring(ro.radius || r, ro.tube || 1.8, { openGap: ro.openGap !== false, role: ro.role || 'load', axis: ro.axis || ax });
    ring.position.copy(c);
    ring.userData.axisLocal = (ro.axis ? v3(ro.axis) : ax).clone().normalize();
    ring.setCenter = function (p) { ring.position.copy(gun.anchor(p)); app.invalidate(); return ring; };
    g.add(ring); app.invalidate();
    return ring;
  };

  if (o.pose === 'opening') gun.setDials(WK.OPENING.roll, WK.OPENING.holeDial, WK.OPENING.vertical);
  else if (o.pose && typeof o.pose === 'object') gun.setDials(o.pose.roll || 0, o.pose.holeDial == null ? 35 : o.pose.holeDial, o.pose.vertical || 0);
  app.add(g);
  if (o.shell) gun.addShell(o.shell === true ? {} : o.shell);
  return gun;
};

// ---------------------------------------------------------------- scene / app
const SECTION_DEFS = [
  ['proposes', 'What is proposed'],
  ['carries', 'What carries loads and locates'],
  ['software', 'Software: controls & observes'],
  ['tried', 'Tried to break, repaired'],
  ['unresolved', 'Unresolved'],
  ['assumptions', 'Assumptions & illustrative values'],
  ['sources', 'Notes & sources'],
];
const ORIGIN_LABEL = { 'derek-example': "Derek's example", swarm: 'Swarm original', branch: 'Branch', combination: 'Combination', reference: 'Reference' };
const STATUS_LABEL = { rough: 'rough sketch', developed: 'developed', deep: 'worked deeply' };
const HOW_ROWS = [['motion', 'Moves'], ['load', 'Carries'], ['reference', 'Locates'], ['observe', 'Observed by'], ['use', 'Used by']];
const KINDS = {
  actuator: { glyph: '⚙︎', name: 'actuator', text: 'a motor or axis the software could command' },
  scene: { glyph: '✎', name: 'scene', text: 'edits the explanatory scene (placement, not hardware motion)' },
  state: { glyph: '⏱︎', name: 'state', text: 'mode: setup / operating / welding' },
  branch: { glyph: '⑂', name: 'branch', text: 'compare variants of the idea' },
  view: { glyph: '◉', name: 'view', text: 'camera / display only' },
};
const IO_STATUS = {
  seen: 'a proposed sensor would report this', partly: 'partly observable (some conditions or axes only)',
  blind: 'not observable by the proposed sensors', manual: 'a person does or checks this by hand', unresolved: 'no mechanism yet: open question',
};
const VIEWS = {
  overall: { target: [10, -95, 150], dir: [-0.62, 0.34, 0.56], dist: 1330 },
  joint: { target: [58, -6, 154], dir: [-0.80, 0.26, 0.46], dist: 190 },
  top: { target: [20, -95, 146], dir: [0, -0.0035, 1], dist: 760 },
  side: { target: [10, -85, 125], dir: [0.03, -1, 0.05], dist: 1200 },
  front: { target: [0, -85, 125], dir: [1, 0.04, 0.06], dist: 1200 },
};
function readMeta() {
  const n = document.getElementById('scene-meta');
  if (!n) return {};
  try { return JSON.parse(n.textContent); } catch (e) { fail('scene-meta JSON', e); return {}; }
}
function htmlOrText(s) {
  if (Array.isArray(s)) s = s.join('\n');
  s = String(s == null ? '' : s);
  if (/<[a-z][\s\S]*>/i.test(s)) return s;
  return s.split(/\n\s*\n/).map(p => '<p>' + esc(p.trim()) + '</p>').join('');
}
function baseName(p) { return String(p).split('/').pop().replace(/\.[a-z0-9]+$/i, '').replace(/[-_]+/g, ' '); }

WK.app = function (opts) {
  opts = opts || {};
  const meta = readMeta();
  const o = Object.assign({ stage: '3d', workstation: true, gun: true, view: 'overall' }, meta, opts);
  o.how = Object.assign({}, meta.how || {}, opts.how || {});
  o.sections = Object.assign({}, meta.sections || {}, opts.sections || {});
  o.software = Object.assign({}, meta.software || {}, opts.software || {});
  if (!document.body) throw new Error('WK.app: put the script at the end of <body>');
  const custom = o.stage === 'custom';
  const thumb = /[?&]thumb(=1|&|$)/.test(location.search);

  Object.keys(ROLE).forEach(k => document.documentElement.style.setProperty('--role-' + k, WK.roleHex(k)));
  document.title = (o.title || o.id || 'Scene') + ' - weld study';

  const app = { opts: o, meta: meta, _before: [], _after: [], _frame: [], _dirty: true, _animate: false, custom: custom, thumb: thumb, workstation: null, gun: null };

  // ---------------------------------------------------------- chrome (header, summary, layout)
  const root = h('div', { class: 'wk-app' + (thumb ? ' wk-thumb' : ''), 'data-stage': custom ? 'custom' : '3d' });
  const chips = h('div', { class: 'wk-chips' });
  if (o.origin) chips.appendChild(h('span', { class: 'wk-chip wk-origin origin-' + esc(o.origin), text: ORIGIN_LABEL[o.origin] || o.origin, title: 'where the idea came from' }));
  if (o.by) chips.appendChild(h('span', { class: 'wk-chip', text: 'by ' + o.by }));
  const st = o.status || o.sceneStatus;
  if (st) chips.appendChild(h('span', { class: 'wk-chip wk-status', text: STATUS_LABEL[st] || st, title: 'how far the idea was taken; not a ranking' }));
  const header = h('header', { class: 'wk-header' },
    h('a', { class: 'wk-back', href: '../../index.html', text: '← Index' }),
    h('h1', { class: 'wk-title', text: o.title || 'Untitled scene' }), chips);
  root.appendChild(header);

  const head2 = h('div', { class: 'wk-summary' });
  if (o.summary) head2.appendChild(h('p', { class: 'wk-summary-text', text: o.summary }));
  const howRows = HOW_ROWS.filter(r => o.how[r[0]]);
  if (howRows.length) {
    const how = h('dl', { class: 'wk-how' });
    howRows.forEach(r => how.append(h('div', null, h('dt', { text: r[1] }), h('dd', { text: o.how[r[0]] }))));
    head2.appendChild(how);
  }
  const relRows = [['Branch of', o.branchOf], ['Combines', o.combines]].filter(r => r[1] && r[1].length);
  const trans = o.transferable && o.transferable.length ? o.transferable : null;
  if (relRows.length || trans) {
    const rel = h('div', { class: 'wk-rel' });
    relRows.forEach(r => { rel.appendChild(h('span', { class: 'wk-rel-l', text: r[0] })); r[1].forEach(id => rel.appendChild(h('a', { class: 'wk-chip wk-chip-link', href: '../' + id + '/index.html', text: id }))); });
    if (trans) { rel.appendChild(h('span', { class: 'wk-rel-l', text: 'Transferable' })); trans.forEach(t => rel.appendChild(h('span', { class: 'wk-chip', text: t }))); }
    head2.appendChild(rel);
  }
  if (head2.children.length) root.appendChild(head2);

  // 3D: the frame IS app.stageEl (canvas + overlays). Custom: frame = [badge strip | body | legend strip]; the body scrolls
  // app.stageEl (where scenes append their SVG / DOM) inside it, so badges and legend never sit on top of the content.
  const frame = h('div', { class: 'wk-stage' + (custom ? ' wk-stage-frame' : ''), id: 'wk-stage' });
  let stageEl = frame, bodyEl = null, ovl = null;
  if (custom) {
    stageEl = h('div', { class: 'wk-stage-custom' });
    if (o.minWidth) stageEl.style.minWidth = (+o.minWidth) + 'px';   // narrower stages scroll sideways instead of shrinking the drawing
    ovl = h('div', { class: 'wk-ovl' });
    ['tl', 'tr', 'bl', 'br'].forEach(c => { ovl[c] = h('div', { class: 'wk-ovl-c wk-ovl-' + c }); ovl.appendChild(ovl[c]); });
    bodyEl = h('div', { class: 'wk-stage-body' }, h('div', { class: 'wk-stage-scroll' }, stageEl), ovl);
    frame.appendChild(bodyEl);
  }
  const main = h('main', { class: 'wk-main' }, h('section', { class: 'wk-stagecol' }, frame));
  const side = h('aside', { class: 'wk-side' });
  main.appendChild(side);
  root.appendChild(main);
  document.body.appendChild(root);
  app.stageEl = stageEl;
  app.stageFrame = frame;
  app.root = root;
  const box = custom ? bodyEl : frame;   // the rectangle overlays and slots are laid out in

  // ---------------------------------------------------------- controls panel
  const ctlCard = h('section', { class: 'wk-card wk-controls' });
  const kindKey = h('div', { class: 'wk-kindkey', hidden: true });
  const ctlBody = h('div', { class: 'wk-ctl-body' });
  const resetAll = h('button', { class: 'wk-btn wk-btn-quiet', type: 'button', text: 'Reset all', title: 'restore every control to its initial value', on: { click: function () { app.ui.reset(); } } });
  ctlCard.append(h('div', { class: 'wk-card-head' }, h('h2', { text: 'Controls' }), resetAll), kindKey, ctlBody);
  side.appendChild(ctlCard);
  const ioCard = h('section', { class: 'wk-card wk-io', hidden: true });
  side.appendChild(ioCard);
  const secWrap = h('div', { class: 'wk-sections' });
  side.appendChild(secWrap);

  // ---------------------------------------------------------- 3D stage: renderer, camera, controls
  let renderer = null, scene = null, camera = null, orbit = null, W = 1, Hh = 1;
  const labels = [], slots = [], badges = new Map(), views = {};
  let obstacles = [];
  let toolsEl, labelsEl, leadersEl, badgesEl, slotsEl, legendEl, viewBtns = {};

  toolsEl = h('div', { class: 'wk-tools' });
  badgesEl = h('div', { class: 'wk-badges' });
  legendEl = h('div', { class: 'wk-legend', hidden: true });
  slotsEl = h('div', { class: 'wk-slots' });
  labelsEl = h('div', { class: 'wk-labels' });
  leadersEl = WK.svg('svg', { class: 'wk-leaders' });

  if (!custom) {
    try {
      renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
      renderer.outputEncoding = THREE.sRGBEncoding;
      renderer.setPixelRatio(Math.min(global.devicePixelRatio || 1, 2));
      scene = new THREE.Scene();
      scene.background = new THREE.Color(0x141a22);   // sRGB hex used as-is for clear colour in r147 legacy mode
      camera = new THREE.PerspectiveCamera(o.fov || 30, 1.6, 2, 8000);
      camera.up.set(0, 0, 1);                          // MUST precede OrbitControls: it snapshots camera.up
      camera.layers.enable(1);                          // layer 1 = helper layer (main view only)
      scene.add(camera);
      scene.add(new THREE.HemisphereLight(0xffffff, 0x556070, 0.95));
      const key = new THREE.DirectionalLight(0xffffff, 0.95); key.position.set(160, -260, 420); scene.add(key);
      const fill = new THREE.DirectionalLight(0xffffff, 0.45); fill.position.set(-260, 220, 240); scene.add(fill);
      const head = new THREE.DirectionalLight(0xffffff, 0.35); head.position.set(0, 0, 1); camera.add(head); head.target = camera; // camera-attached: faces toward viewer
      stageEl.appendChild(renderer.domElement);
      if (THREE.OrbitControls) {
        orbit = new THREE.OrbitControls(camera, renderer.domElement);
        orbit.enableDamping = true; orbit.dampingFactor = 0.14; orbit.screenSpacePanning = true;
        orbit.minDistance = 25; orbit.maxDistance = 4000;
        orbit.addEventListener('change', function () { app._dirty = true; });
      } else fail('WK.app', 'THREE.OrbitControls missing: load kit/vendor/OrbitControls.js');
    } catch (e) {
      fail('WebGL', e);
      stageEl.appendChild(h('div', { class: 'wk-nogl', text: '3D view could not start (WebGL unavailable).' }));
      renderer = null;
    }
  }
  if (custom) { bodyEl.append(slotsEl); frame.insertBefore(badgesEl, bodyEl); frame.appendChild(legendEl); }
  else stageEl.append(labelsEl, leadersEl, slotsEl, badgesEl, legendEl, toolsEl);
  app.scene = scene; app.camera = camera; app.renderer = renderer; app.controls = orbit;

  // ---------------------------------------------------------- basic scene API
  app.invalidate = function () { app._dirty = true; return app; };
  app.animate = function (on) { app._animate = on !== false; return app; };
  // fn(dt, t). Return false when idle (nothing changed) so the frame is not re-rendered.
  app.onFrame = function (fn) { app._frame.push(fn); return function () { const i = app._frame.indexOf(fn); if (i >= 0) app._frame.splice(i, 1); }; };
  const readyCbs = [];
  app.onReady = function (fn) { if (global.__sceneReady) fn(); else readyCbs.push(fn); return app; };
  app.add = function (obj, role) {
    if (!scene) return obj;
    if (role) WK.setRole(obj, role);
    scene.add(obj); legendDirty = true; app._dirty = true;
    return obj;
  };
  // helper layer: drawn in the main view only, never in observer insets (frustums, axes, dimension guides...)
  app.addHelper = function (obj) {
    obj.traverse(function (x) { x.layers.set(1); x.userData.helper = true; if (x.isMesh || x.isLine) x.userData.occludes = false; });
    return app.add(obj);
  };
  app.frameObject = function (obj, fo) {
    if (!camera || !orbit) return app;
    fo = fo || {};
    const box = new THREE.Box3().setFromObject(obj); if (box.isEmpty()) return app;
    const sph = box.getBoundingSphere(new THREE.Sphere());
    const dir = camera.position.clone().sub(orbit.target).normalize();
    const dist = sph.radius / Math.sin(camera.fov * DEG / 2) * (fo.pad || 1.15);
    orbit.target.copy(sph.center); camera.position.copy(sph.center).addScaledVector(dir, dist); orbit.update(); app._dirty = true;
    return app;
  };
  app.toast = function (text, ms) {
    const t = h('div', { class: 'wk-toast', text: text });
    box.appendChild(t);
    setTimeout(function () { t.classList.add('out'); setTimeout(function () { t.remove(); }, 400); }, ms || 2200);
    return app;
  };
  // Stage badge: app.badge('link', 'LIMIT: link would stretch', 'limit'); text null removes it. 3D stage: top centre of the
  // canvas. Custom stage: right-aligned strip above the drawing (the strip stays once a badge has appeared, so nothing jumps).
  app.badge = function (id, text, level) {
    let b = badges.get(id);
    if (text == null || text === false) { if (b) { b.remove(); badges.delete(id); } publishBadges(); return app; }
    if (!b) { b = h('div', { class: 'wk-stagebadge' }); badgesEl.appendChild(b); badges.set(id, b); badgesEl.classList.add('is-used'); }
    b.className = 'wk-stagebadge lvl-' + (level || 'info');
    b.textContent = ((level === 'limit') ? 'LIMIT  ' : '') + text;
    b.dataset.level = level || 'info';
    publishBadges();
    return app;
  };
  function publishBadges() { global.__badges = Array.from(badges.entries()).map(e => ({ id: e[0], level: e[1].dataset.level, text: e[1].textContent })); }
  publishBadges();

  // ---------------------------------------------------------- views
  let viewName = o.view || 'overall', tween = null, firstView = true;
  function viewSpec(name) {
    const v = (o.views && o.views[name]) || VIEWS[name];
    if (!v) { console.warn('WK: unknown view "' + name + '"'); return VIEWS.overall; }
    return v;
  }
  function resolveView(v) {
    const target = v3(v.target || [0, 0, 100]);
    let dir, dist;
    if (v.position) { const off = v3(v.position).sub(target); dist = off.length(); dir = off.normalize(); }
    else { dir = v3(v.dir || [-0.6, 0.3, 0.55]).normalize(); dist = v.dist || 1000; }
    return { target: target, dir: dir, dist: dist };
  }
  app.setView = function (nameOrSpec, so) {
    if (!camera || !orbit) return app;
    so = so || {};
    const isName = typeof nameOrSpec === 'string';
    if (isName) viewName = nameOrSpec;
    const to = resolveView(isName ? viewSpec(nameOrSpec) : nameOrSpec);
    const fromDir = camera.position.clone().sub(orbit.target); const fromDist = fromDir.length(); fromDir.normalize();
    if (so.instant || firstView || global.__noTween) {
      firstView = false; tween = null;
      orbit.target.copy(to.target); camera.position.copy(to.target).addScaledVector(to.dir, to.dist); orbit.update();
    } else {
      tween = { t: 0, dur: 0.35, fromT: orbit.target.clone(), toT: to.target, fromDir: fromDir, toDir: to.dir, fromDist: fromDist, toDist: to.dist, q: new THREE.Quaternion().setFromUnitVectors(fromDir, to.dir) };
    }
    Object.keys(viewBtns).forEach(k => viewBtns[k].setAttribute('aria-pressed', String(k === viewName)));
    app._dirty = true;
    return app;
  };
  app.getView = function () { return viewName; };
  if (!custom) app._frame.push(function (dt) {
    if (!tween) return false;
    tween.t += dt / tween.dur;
    const k = Math.min(1, tween.t), e = k * k * (3 - 2 * k);
    const dir = tween.fromDir.clone().applyQuaternion(new THREE.Quaternion().slerpQuaternions(new THREE.Quaternion(), tween.q, e));
    orbit.target.lerpVectors(tween.fromT, tween.toT, e);
    camera.position.copy(orbit.target).addScaledVector(dir, tween.fromDist + (tween.toDist - tween.fromDist) * e);
    if (k >= 1) tween = null;
    return true;
  });
  if (orbit) orbit.addEventListener('start', function () { tween = null; });

  // view buttons + reset view
  if (!custom && renderer) {
    const list = o.viewButtons || ['overall', 'joint', 'top', 'side', 'front'];
    list.forEach(function (n) {
      const b = h('button', { class: 'wk-btn wk-viewbtn', type: 'button', text: n[0].toUpperCase() + n.slice(1), 'aria-pressed': 'false', on: { click: function () { app.setView(n); } } });
      viewBtns[n] = b; toolsEl.appendChild(b);
    });
    toolsEl.appendChild(h('button', { class: 'wk-btn wk-btn-quiet wk-viewbtn', type: 'button', text: 'Reset view', title: 'return to the scene’s starting view', on: { click: function () { app.setView(o.view || 'overall'); } } }));
  }

  // ---------------------------------------------------------- UI controls
  const registry = [], byId = new Map();
  global.__controls = [];
  const used = {};
  let autoId = 0;
  function fmtNum(v, dec) { return (Math.round(v * Math.pow(10, dec)) / Math.pow(10, dec)).toFixed(dec); }
  function registerCtl(c, spec) {
    if (byId.has(c.id)) { console.warn('WK.ui: duplicate control id ' + c.id); c.id = c.id + '_' + (++autoId); }
    registry.push(c); byId.set(c.id, c);
    // noVisual:true (or visual:false) tells tools/check-scene.mjs this control is not expected to change the stage
    // (a readout, an animation speed, an effect that depends on another control's state).
    const entry = { id: c.id, type: c.type, kind: c.kind, min: c.min, max: c.max, noVisual: !!(spec && (spec.noVisual || spec.visual === false)) };
    if (c.options) entry.options = c.options.map(x => x.value);
    Object.defineProperty(entry, 'value', { get: function () { return c.value; }, enumerable: true });
    global.__controls.push(entry);
    used[c.kind] = true; renderKindKey();
  }
  function renderKindKey() {
    const ks = Object.keys(KINDS).filter(k => used[k]);
    kindKey.hidden = ks.length === 0;
    kindKey.innerHTML = '';
    ks.forEach(k => kindKey.appendChild(h('span', { class: 'wk-kk kind-' + k, title: KINDS[k].text }, h('b', { class: 'wk-glyph', text: KINDS[k].glyph }), ' ' + KINDS[k].name + ': ' + KINDS[k].text)));
  }
  function badgeEl(kind) { return h('span', { class: 'wk-kbadge kind-' + kind, title: KINDS[kind] ? KINDS[kind].name + ': ' + KINDS[kind].text : kind }, h('span', { class: 'wk-glyph', text: KINDS[kind] ? KINDS[kind].glyph : '' })); }
  function fire(c) {
    if (c.onChange) { try { c.onChange(c.value, c.api); } catch (e) { fail('control "' + c.id + '" onChange', e); } }
    app._dirty = true;
  }
  function attachVisual(el, s) {
    if (!s.visual) return;
    if (typeof s.visual === 'string') { el.appendChild(h('div', { class: 'wk-watch', text: 'watch: ' + s.visual })); return; }
    const on = () => WK.highlight(s.visual, true), off = () => { WK.highlight(s.visual, false); app._dirty = true; };
    el.addEventListener('pointerenter', function () { on(); app._dirty = true; }); el.addEventListener('pointerleave', off);
    el.addEventListener('focusin', function () { on(); app._dirty = true; }); el.addEventListener('focusout', off);
  }
  function makeUI(container) {
    const ui = {};
    function head(s, kind, forId, extra) {
      return h('div', { class: 'wk-ctl-head' }, badgeEl(kind), h('label', { for: forId, text: s.label || s.id }), extra || null);
    }
    function helpEl(s) { return s.help ? h('div', { class: 'wk-help', text: s.help }) : null; }

    ui.slider = function (s) {
      const kind = s.kind || 'scene', min = +s.min, max = +s.max, step = s.step || (max - min) / 100, dec = decimals(step);
      const initial = s.value == null ? min : +s.value, id = s.id || 'slider' + (++autoId);
      const val = h('span', { class: 'wk-val' }), input = h('input', { type: 'range', id: 'wk-in-' + id, min: min, max: max, step: step, value: initial });
      const wrap = h('div', { class: 'wk-ctl wk-slider kind-' + kind, 'data-wk-id': id }, head(s, kind, 'wk-in-' + id, val), input, helpEl(s));
      attachVisual(wrap, s);
      const fmt = v => (s.format ? s.format(v) : fmtNum(v, dec)) + (s.unit ? ' ' + s.unit : '');
      const c = { id: id, type: 'slider', kind: kind, min: min, max: max, step: step, initial: initial, value: initial, onChange: s.onChange, el: wrap };
      c.set = function (v, so) {
        v = clamp(min + Math.round((+v - min) / step) * step, min, max); v = +v.toFixed(Math.max(dec, 0) + 2);
        c.value = v; input.value = v; val.textContent = fmt(v);
        if (!(so && so.silent)) fire(c);
        return v;
      };
      c.api = { id: id, get: () => c.value, set: c.set, el: wrap, input: input };
      val.textContent = fmt(initial);
      input.addEventListener('input', function () { c.set(+input.value); });
      container.appendChild(wrap); registerCtl(c, s); return c.api;
    };
    ui.toggle = function (s) {
      const kind = s.kind || 'state', initial = !!s.value, id = s.id || 'toggle' + (++autoId);
      const input = h('input', { type: 'checkbox', id: 'wk-in-' + id }), sw = h('label', { class: 'wk-switch', for: 'wk-in-' + id }, input, h('span', { class: 'wk-track' }));
      const wrap = h('div', { class: 'wk-ctl wk-toggle kind-' + kind, 'data-wk-id': id }, h('div', { class: 'wk-ctl-head' }, badgeEl(kind), h('label', { for: 'wk-in-' + id, text: s.label || id }), sw), helpEl(s));
      attachVisual(wrap, s);
      const c = { id: id, type: 'toggle', kind: kind, initial: initial, value: initial, onChange: s.onChange, el: wrap };
      c.set = function (v, so) { c.value = !!v; input.checked = c.value; if (!(so && so.silent)) fire(c); return c.value; };
      c.api = { id: id, get: () => c.value, set: c.set, el: wrap, input: input };
      input.checked = initial;
      input.addEventListener('change', function () { c.set(input.checked); });
      container.appendChild(wrap); registerCtl(c, s); return c.api;
    };
    function optionCtl(s, type, asRadio) {
      const kind = s.kind || 'branch', id = s.id || type + (++autoId);
      const opts = (s.options || []).map(x => (typeof x === 'object' ? { value: x.value, label: x.label == null ? String(x.value) : x.label, help: x.help } : { value: x, label: String(x) }));
      const initial = s.value == null && opts.length ? opts[0].value : s.value;
      const wrap = h('div', { class: 'wk-ctl wk-' + type + ' kind-' + kind, 'data-wk-id': id });
      const c = { id: id, type: type, kind: kind, initial: initial, value: initial, options: opts, onChange: s.onChange, el: wrap };
      let sel = null; const btns = [];
      const helpLine = h('div', { class: 'wk-help' });
      function showHelp() { const cur = opts.find(x => String(x.value) === String(c.value)); helpLine.textContent = (cur && cur.help) || s.help || ''; helpLine.hidden = !helpLine.textContent; }
      if (asRadio) {
        wrap.appendChild(h('div', { class: 'wk-ctl-head' }, badgeEl(kind), h('span', { class: 'wk-lbl', text: s.label || id })));
        const seg = h('div', { class: 'wk-seg', role: 'radiogroup' });
        opts.forEach(function (op) { const b = h('button', { type: 'button', role: 'radio', class: 'wk-segbtn', 'data-value': op.value, text: op.label, on: { click: function () { c.set(op.value); } } }); btns.push(b); seg.appendChild(b); });
        wrap.appendChild(seg);
      } else {
        sel = h('select', { id: 'wk-in-' + id });
        opts.forEach(op => sel.appendChild(h('option', { value: op.value, text: op.label })));
        wrap.appendChild(h('div', { class: 'wk-ctl-head' }, badgeEl(kind), h('label', { for: 'wk-in-' + id, text: s.label || id })));
        wrap.appendChild(sel);
        sel.addEventListener('change', function () { c.set(opts[sel.selectedIndex].value); });
      }
      wrap.appendChild(helpLine); attachVisual(wrap, s);
      c.set = function (v, so) {
        const op = opts.find(x => String(x.value) === String(v)) || opts[0]; if (!op) return v;
        c.value = op.value;
        if (sel) sel.value = op.value;
        btns.forEach(b => b.setAttribute('aria-checked', String(String(b.dataset.value) === String(op.value))));
        showHelp();
        if (!(so && so.silent)) fire(c);
        return c.value;
      };
      c.api = { id: id, get: () => c.value, set: c.set, el: wrap };
      c.set(initial, { silent: true });
      container.appendChild(wrap); registerCtl(c, s); return c.api;
    }
    // select/radio: {id,label,options:[value | {value,label,help}], value, kind:'branch', onChange}
    ui.select = s => optionCtl(s, 'select', false);
    ui.radio = s => optionCtl(s, 'radio', true);
    ui.button = function (s) {
      const kind = s.kind || 'state', id = s.id || 'button' + (++autoId);
      const b = h('button', { class: 'wk-btn wk-actionbtn kind-' + kind, type: 'button', title: s.help || '' }, badgeEl(kind), ' ' + (s.label || id));
      const wrap = h('div', { class: 'wk-ctl wk-button', 'data-wk-id': id }, b);
      const c = { id: id, type: 'button', kind: kind, value: null, onChange: null, el: wrap };
      c.set = function () { try { if (s.onClick) s.onClick(c.api); } catch (e) { fail('button "' + id + '"', e); } app._dirty = true; return null; };
      c.api = { id: id, click: c.set, set: c.set, el: b };
      b.addEventListener('click', c.set);
      container.appendChild(wrap); registerCtl(c, s); return c.api;
    };
    // readout(id,label) -> setter(textOrNumber, unit)
    ui.readout = function (id, label) {
      const val = h('span', { class: 'wk-val', text: '-' });
      const wrap = h('div', { class: 'wk-readout', 'data-wk-id': id }, h('span', { class: 'wk-lbl', text: label || id }), val);
      container.appendChild(wrap);
      const set = function (v, unit) { const t = typeof v === 'number' ? (Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(2)) : String(v); if (val.textContent !== t + (unit ? ' ' + unit : '')) val.textContent = t + (unit ? ' ' + unit : ''); };
      set.el = wrap;
      return set;
    };
    ui.group = function (title, go) {
      go = go || {};
      const body = h('div', { class: 'wk-group-body' });
      if (go.help) body.appendChild(h('div', { class: 'wk-help wk-group-help', text: go.help }));
      const det = h('details', { class: 'wk-group', open: go.open !== false }, h('summary', { text: title }), body);
      container.appendChild(det);
      const g = makeUI(body); g.el = det; return g;
    };
    return ui;
  }
  app.ui = makeUI(ctlBody);
  app.ui.get = id => { const c = byId.get(id); return c ? c.value : undefined; };
  app.ui.set = (id, v, so) => { const c = byId.get(id); if (!c) throw new Error('WK.ui: no control ' + id); return c.set(v, so); };
  app.ui.enable = function (id, on) { const c = byId.get(id); if (!c) return; c.el.classList.toggle('is-disabled', on === false); c.el.querySelectorAll('input,select,button').forEach(x => { x.disabled = on === false; }); };
  app.ui.list = () => registry.map(c => ({ id: c.id, type: c.type, kind: c.kind, value: c.value }));
  app.ui.reset = function () {
    registry.forEach(function (c) { if (c.type !== 'button') c.set(c.initial); });
    app._dirty = true; return app;
  };
  // app.ui.panel({id, title, node | html, open}) -> the BODY element of a card in the controls column (under the controls,
  // above Software I/O); body.card is the whole <details>. For your own scatter / trace / budget view that is not a control.
  // Calling it again with the same id replaces the content. app.ui.enable(id, false) greys a control out; the checker skips it.
  const panels = new Map();
  app.ui.panel = function (po) {
    po = po || {};
    const id = po.id || 'panel' + (++autoId);
    let body = panels.get(id);
    if (!body) {
      body = h('div', { class: 'wk-panel-body' });
      body.card = h('details', { class: 'wk-card wk-panel', 'data-wk-panel': id, open: po.open !== false }, h('summary', { text: po.title || id }), body);
      side.insertBefore(body.card, ioCard); panels.set(id, body);
    } else if (po.title != null) body.card.firstChild.textContent = po.title;
    if (po.node) { body.textContent = ''; body.appendChild(po.node); } else if (po.html != null) body.innerHTML = po.html;
    if (po.open != null) body.card.open = !!po.open;
    return body;
  };
  global.__resetAll = () => app.ui.reset();
  // For tools: set any control by id. Sliders clamp; toggles coerce; select/radio match by value; buttons click.
  global.__setControl = function (id, value) {
    const c = byId.get(id);
    if (!c) throw new Error('no control with id "' + id + '"');
    return c.set(value);
  };
  if (!custom) resetAll.title = 'restore every control to its initial value (each onChange runs)';

  // ---------------------------------------------------------- software I/O panel
  const ioRows = { commands: new Map(), observes: new Map(), manual: new Map() };
  const ioLists = {};
  function ioBuild() {
    ioCard.innerHTML = '';
    ioCard.appendChild(h('div', { class: 'wk-card-head' }, h('h2', { text: 'Software I/O' }), h('span', { class: 'wk-tag', text: 'proposed · illustrative' })));
    [['commands', 'Software could command (proposed)'], ['observes', 'Software could observe (proposed)'], ['manual', 'Stays manual']].forEach(function (d) {
      ioLists[d[0]] = h('ul', { class: 'wk-io-list' });
      ioCard.appendChild(h('div', { class: 'wk-io-col io-' + d[0], 'data-list': d[0], hidden: true }, h('h3', { text: d[1] }), ioLists[d[0]]));
    });
  }
  function fmtIo(v) { return typeof v === 'number' ? (Number.isInteger(v) ? String(v) : v.toFixed(Math.abs(v) >= 100 ? 0 : 2)) : (v == null ? '' : String(v)); }
  function ioSync(kind, items) {
    const rows = ioRows[kind], seen = new Set();
    items.forEach(function (it, i) {
      const name = it.name == null ? String(i) : String(it.name); seen.add(name);
      let r = rows.get(name);
      if (!r) {
        r = { li: h('li', { class: 'wk-io-row' }), nm: h('span', { class: 'nm' }), val: h('span', { class: 'val' }), chip: h('span', { class: 'chip' }), note: h('div', { class: 'note' }) };
        r.li.append(r.nm, r.val); if (kind === 'observes') r.li.appendChild(r.chip); r.li.appendChild(r.note);
        rows.set(name, r); ioLists[kind].appendChild(r.li);
      }
      const val = fmtIo(it.value) + (it.unit && it.value != null && it.value !== '' ? ' ' + it.unit : '');
      if (r.nm.textContent !== name) r.nm.textContent = name;
      if (r.val.textContent !== val) r.val.textContent = val;
      if (kind === 'observes') { const s = it.status || 'unresolved'; if (r.chip.dataset.s !== s) { r.chip.dataset.s = s; r.chip.className = 'chip st-' + s; r.chip.textContent = s; r.chip.title = IO_STATUS[s] || ''; } }
      const note = it.note || ''; if (r.note.textContent !== note) { r.note.textContent = note; r.note.hidden = !note; }
      if (ioLists[kind].children[i] !== r.li) ioLists[kind].insertBefore(r.li, ioLists[kind].children[i] || null);
    });
    rows.forEach(function (r, name) { if (!seen.has(name)) { r.li.remove(); rows.delete(name); } });
    ioLists[kind].parentNode.hidden = !rows.size;
  }
  app.io = {
    // io.set({commands:[{name,value,unit,note}], observes:[{name,value,status,note}], manual:[text]}); cheap to call every frame
    set: function (d) {
      if (!ioLists.commands) ioBuild();
      ioCard.hidden = false;
      if (d.commands) ioSync('commands', d.commands);
      if (d.observes) ioSync('observes', d.observes);
      if (d.manual) app.io.manual(d.manual);
      return app;
    },
    // io.manual(text | [text]) replaces the list of steps that stay manual
    manual: function (t) {
      if (!ioLists.commands) ioBuild();
      ioCard.hidden = false;
      ioSync('manual', (Array.isArray(t) ? t : [t]).map(x => ({ name: x })));
      return app;
    },
  };

  // ---------------------------------------------------------- collapsible sections
  (function buildSections() {
    const open = o.open || ['proposes'];
    SECTION_DEFS.forEach(function (d) {
      const key = d[0];
      let html = o.sections[key] ? htmlOrText(o.sections[key]) : '';
      if (key === 'software') {
        const sw = o.software, cols = [['commands', 'Could command'], ['observes', 'Could observe'], ['manual', 'Stays manual']].filter(c => sw[c[0]] && sw[c[0]].length);
        if (cols.length) html += '<div class="wk-swmeta">' + cols.map(c => '<div><h4>' + c[1] + '</h4><ul>' + sw[c[0]].map(x => '<li>' + esc(x) + '</li>').join('') + '</ul></div>').join('') + '</div>';
      }
      if (key === 'sources') {
        const groups = [['Idea and exchange notes', o.notes], ['Sourcing notes', o.sources], ['Links', (o.links || []).map(l => ({ label: l.label, href: l.href }))]];
        groups.forEach(function (g) {
          if (!g[1] || !g[1].length) return;
          html += '<h4>' + g[0] + '</h4><ul class="wk-links">' + g[1].map(x => typeof x === 'string' ? '<li><a href="' + esc(x) + '">' + esc(baseName(x)) + '</a> <span class="wk-path">' + esc(x) + '</span></li>' : '<li><a href="' + esc(x.href) + '">' + esc(x.label || x.href) + '</a></li>').join('') + '</ul>';
        });
      }
      if (!html) return;
      secWrap.appendChild(h('details', { class: 'wk-sec', 'data-sec': key, open: open.indexOf(key) >= 0 }, h('summary', { text: d[1] }), h('div', { class: 'wk-sec-body', html: html })));
    });
  })();

  // ---------------------------------------------------------- slots (insets + corner inset) & layout
  function addSlot(s) { slots.push(s); layout(); return s; }
  function layout() {
    if (!box.clientWidth) return;
    W = box.clientWidth; Hh = box.clientHeight;
    const legendH = legendEl.hidden || custom ? 0 : legendEl.offsetHeight + 8;
    const start = { tl: 46, tr: 10, bl: 10 + legendH, br: 10 };
    const cur = { tl: start.tl, tr: start.tr, bl: start.bl, br: start.br };
    slots.forEach(function (s) {
      if (s.removed) return;
      let k = Math.min(1, (W * 0.44) / s.w, (Hh * 0.46) / s.h); if (s.zoom) k = Math.min(s.zoom, (W * 0.9) / s.w, (Hh * 0.8) / s.h);
      const narrow = W < 560, min = !!s.collapsible && narrow && !s.open;
      if (s.collapsible && narrow && s.open) k = Math.min(1.3, (W * 0.92) / s.w, (Hh * 0.92) / s.h);
      s.dw = min ? 172 : Math.round(s.w * k); s.dh = min ? 28 : Math.round(s.h * k);
      if (s.el) s.el.classList.toggle('is-min', min);
      const right = s.corner === 'tr' || s.corner === 'br', bottom = s.corner === 'bl' || s.corner === 'br';
      s.x = right ? W - s.dw - 10 : 10;
      s.el.style.width = s.dw + 'px'; s.el.style.left = s.x + 'px';
      if (s.autoH) { s.el.style.height = 'auto'; if (s.onLayout) s.onLayout(s); s.dh = s.el.offsetHeight; }
      else { s.el.style.height = s.dh + 'px'; if (s.onLayout) s.onLayout(s); }
      s.y = bottom ? Hh - cur[s.corner] - s.dh : cur[s.corner];
      cur[s.corner] += s.dh + 8;
      s.el.style.top = s.y + 'px';
    });
    obstacles = slots.filter(s => !s.removed).map(s => ({ x: s.x, y: s.y, w: s.dw, h: s.dh }));
    if (toolsEl.children.length) obstacles.push({ x: 0, y: 0, w: toolsEl.offsetWidth + 14, h: toolsEl.offsetHeight + 10 });
    if (!legendEl.hidden && !custom) obstacles.push({ x: 0, y: Hh - legendEl.offsetHeight - 10, w: legendEl.offsetWidth + 12, h: legendEl.offsetHeight + 10 });
  }
  app._addSlot = addSlot;   // internal; scenes use app.stageOverlay / app.ui.panel

  // app.stageOverlay(nodeOrHtml, {corner:'tr'|'tl'|'br'|'bl', w, h}) -> the overlay element (a HUD card on the stage). 3D stage:
  // stacks with the insets in that corner (w = width in px, default 250; height follows the content). Custom stage: a stack
  // in that corner of the drawing area, above the scrolling content. el.remove() takes it away.
  app.stageOverlay = function (node, so) {
    so = so || {};
    const corner = ['tl', 'tr', 'bl', 'br'].indexOf(so.corner) >= 0 ? so.corner : 'tr';
    const el = h('div', { class: 'wk-overlay', 'data-corner': corner });
    if (typeof node === 'string') el.innerHTML = node; else if (node) el.appendChild(node);
    if (custom) { ovl[corner].appendChild(el); if (so.w) el.style.width = so.w + 'px'; return el; }
    slotsEl.appendChild(el);
    const slot = addSlot({ corner: corner, w: so.w || 250, h: so.h || 120, el: el, autoH: true });
    if (global.ResizeObserver) new ResizeObserver(function () { requestAnimationFrame(function () { layout(); app._dirty = true; }); }).observe(el);   // content grew or shrank (next frame: no observer loop)
    el.remove = function () { slot.removed = true; Element.prototype.remove.call(el); layout(); app._dirty = true; };
    return el;
  };

  // ---------------------------------------------------------- legend (roles actually used)
  // app.legend() with no argument lists the roles found in the scene. app.legend([{role|color, label}]) shows YOUR entries and
  // keeps them (adding parts never overwrites them) until app.legend(null) hands the legend back to the scan.
  // Custom stage: the legend is a strip under the drawing; 3D stage: an overlay at the lower left of the canvas.
  let legendDirty = true, customLegend = null;
  const legendBtn = h('button', { class: 'wk-btn wk-legend-btn', type: 'button', text: 'Legend', on: { click: function () { legendEl.classList.toggle('is-collapsed'); layout(); app._dirty = true; } } });
  if (global.matchMedia && global.matchMedia('(max-width: 900px)').matches) legendEl.classList.add('is-collapsed');
  app.legend = function (items) {
    if (items === null || items === false) { customLegend = null; legendDirty = true; app._dirty = true; if (!scene) { legendEl.hidden = true; layout(); return app; } }
    else if (Array.isArray(items)) customLegend = items;
    if (customLegend) {
      legendEl.innerHTML = ''; legendEl.appendChild(legendBtn);
      customLegend.forEach(function (it) { legendEl.appendChild(h('span', { class: 'wk-lg', title: it.label }, h('i', { style: { background: it.color || WK.roleHex(it.role) } }), it.label || (ROLE[WK.role(it.role)] || {}).label)); });
      legendEl.hidden = !customLegend.length; legendDirty = false; layout(); return app;
    }
    if (!scene) return app;
    const seen = {};
    scene.traverse(function (x) { const r = x.userData && x.userData.role; if (r && ROLE[r] && !x.userData.helperOnly) seen[r] = true; });
    legendEl.innerHTML = '';
    legendEl.appendChild(legendBtn);
    Object.keys(ROLE).filter(r => seen[r]).forEach(function (r) { legendEl.appendChild(h('span', { class: 'wk-lg', 'data-role': r }, h('i', { style: { background: WK.roleHex(r) } }), ROLE[r].label)); });
    legendEl.hidden = !legendEl.children.length;
    legendDirty = false; layout();
    return app;
  };

  // ---------------------------------------------------------- labels (DOM, with leader lines)
  // app.label(worldPointOrObject3D | ()=>Vector3, text, {cls: roleName, local: [x,y,z] for Object3D})
  app.label = function (target, text, lo) {
    lo = lo || {};
    const el = h('div', { class: 'wk-label' + (lo.cls ? ' role-' + WK.role(lo.cls) : ''), text: text });
    const line = WK.svg('line', { class: 'wk-leader' }), dot = WK.svg('circle', { class: 'wk-leader-dot', r: 2.6 });
    labelsEl.appendChild(el); leadersEl.append(line, dot);
    const L = { el: el, line: line, dot: dot, shown: true, cand: 0, w: 0, h: 0, text: text, cls: lo.cls };
    const tmp = new V3();
    L.getPos = function () {
      if (typeof target === 'function') return target();
      if (target && target.isObject3D) { target.updateWorldMatrix(true, false); return lo.local ? target.localToWorld(tmp.copy(v3(lo.local))) : tmp.setFromMatrixPosition(target.matrixWorld); }
      return target;
    };
    labels.push(L); app._dirty = true;
    return {
      el: el, set: function (t) { L.text = t; el.textContent = t; L.w = 0; app._dirty = true; },
      show: function (on) { L.shown = on !== false; app._dirty = true; },
      remove: function () { el.remove(); line.remove(); dot.remove(); const i = labels.indexOf(L); if (i >= 0) labels.splice(i, 1); app._dirty = true; },
    };
  };
  const _p = new V3();
  function rectHit(a, b, pad) { return a.x < b.x + b.w + pad && b.x < a.x + a.w + pad && a.y < b.y + b.h + pad && b.y < a.y + a.h + pad; }
  function placeLabels() {
    if (!labels.length || !camera) return;
    const items = [];
    labels.forEach(function (L) {
      const p = L.getPos();
      let vis = L.shown && p;
      if (vis) { _p.copy(p).project(camera); vis = _p.z > -1 && _p.z < 1 && Math.abs(_p.x) < 1.03 && Math.abs(_p.y) < 1.03; }
      if (vis) {   // anchors that sit under an inset or the corner inset are hidden with their label
        const px = (_p.x + 1) / 2 * W, py = (1 - _p.y) / 2 * Hh;
        for (let i = 0; i < slots.length; i++) { const q = slots[i]; if (!q.removed && px > q.x && px < q.x + q.dw && py > q.y && py < q.y + q.dh) { vis = false; break; } }
      }
      if (!vis) { L.el.style.display = 'none'; L.line.style.display = 'none'; L.dot.style.display = 'none'; return; }
      L.el.style.display = ''; L.line.style.display = ''; L.dot.style.display = '';
      items.push({ L: L, px: (_p.x + 1) / 2 * W, py: (1 - _p.y) / 2 * Hh });
    });
    items.sort((a, b) => a.py - b.py || a.px - b.px);
    const placed = obstacles.slice();
    items.forEach(function (it) {
      const L = it.L;
      if (!L.w) { L.w = L.el.offsetWidth; L.h = L.el.offsetHeight; }
      const w = L.w, hh = L.h;
      const cands = [[14, -hh - 10], [14, 12], [-w - 14, -hh - 10], [-w - 14, 12], [-w / 2, -hh - 26], [-w / 2, 28]];
      const order = [L.cand].concat(cands.map((c, i) => i).filter(i => i !== L.cand));
      let pick = null;
      for (let k = 0; k < order.length && !pick; k++) {
        const c = cands[order[k]];
        const r = { x: clamp(it.px + c[0], 4, Math.max(4, W - w - 4)), y: clamp(it.py + c[1], 4, Math.max(4, Hh - hh - 4)), w: w, h: hh };
        if (!placed.some(q => rectHit(r, q, 3))) { pick = r; L.cand = order[k]; }
      }
      if (!pick) {   // stack downward from the preferred slot
        let r = { x: clamp(it.px + cands[0][0], 4, Math.max(4, W - w - 4)), y: clamp(it.py + cands[0][1], 4, Math.max(4, Hh - hh - 4)), w: w, h: hh };
        for (let n = 0; n < 12 && placed.some(q => rectHit(r, q, 3)); n++) r = { x: r.x, y: Math.min(Hh - hh - 4, r.y + hh + 4), w: w, h: hh };
        pick = r;
      }
      placed.push(pick);
      L.el.style.left = Math.round(pick.x) + 'px'; L.el.style.top = Math.round(pick.y) + 'px';
      const ex = clamp(it.px, pick.x, pick.x + pick.w), ey = clamp(it.py, pick.y, pick.y + pick.h);
      L.line.setAttribute('x1', it.px.toFixed(1)); L.line.setAttribute('y1', it.py.toFixed(1)); L.line.setAttribute('x2', ex.toFixed(1)); L.line.setAttribute('y2', ey.toFixed(1));
      L.dot.setAttribute('cx', it.px.toFixed(1)); L.dot.setAttribute('cy', it.py.toFixed(1));
    });
  }

  // ---------------------------------------------------------- observer insets (scissor viewports in the same canvas)
  const insets = new Map();
  const NOISE_URL = (function () {
    try {
      const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'), d = x.createImageData(64, 64);
      for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255; }
      x.putImageData(d, 0, 0); return c.toDataURL();
    } catch (e) { return ''; }
  })();
  const _sc = new V3();
  function syncInset(ins) {
    let src = null;
    if (ins.object3D) { ins.object3D.updateWorldMatrix(true, false); src = ins.object3D; }
    if (src) {
      src.matrixWorld.decompose(ins.camera.position, ins.camera.quaternion, _sc);
      if (ins.target) { const tp = typeof ins.target === 'function' ? ins.target() : (ins.target.isObject3D ? new V3().setFromMatrixPosition((ins.target.updateWorldMatrix(true, false), ins.target.matrixWorld)) : v3(ins.target)); ins.lookAt(tp); }
    } else {
      const pos = typeof ins.position === 'function' ? ins.position() : ins.position;
      ins.camera.position.copy(v3(pos));
      const tp = typeof ins.target === 'function' ? ins.target() : (ins.target && ins.target.isObject3D ? new V3().setFromMatrixPosition((ins.target.updateWorldMatrix(true, false), ins.target.matrixWorld)) : v3(ins.target || [0, 0, 0]));
      ins.lookAt(tp);
    }
    ins.camera.updateMatrixWorld(true);
    if (ins.helper) {
      ins.helper.position.copy(ins.camera.position); ins.helper.quaternion.copy(ins.camera.quaternion);
      const tp = ins.target ? (typeof ins.target === 'function' ? ins.target() : (ins.target.isObject3D ? new V3().setFromMatrixPosition(ins.target.matrixWorld) : v3(ins.target))) : null;
      const far = tp ? Math.min(ins.far, ins.camera.position.distanceTo(tp) * 1.12) : Math.min(ins.far, 260);
      if (Math.abs(far - ins.drawnFar) > 0.5) { ins.drawnFar = far; ins.frustum.set({ fov: ins.fov, aspect: ins.w / ins.h, near: Math.min(ins.near * 2, far * 0.2), far: far }); }
    }
  }
  app.inset = {
    // inset.add({id,label,object3D|position,target,fov,near,far,size:[w,h],corner,frustum,noise,cls})
    add: function (io) {
      if (!camera) return null;
      const id = io.id || 'inset' + (insets.size + 1), size = io.size || [230, 156];
      const ins = { id: id, label: io.label || id, object3D: io.object3D, position: io.position, target: io.target, fov: io.fov || 40, near: io.near || 4, far: io.far || 2500, w: size[0], h: size[1], corner: io.corner || 'br', corner0: io.corner || 'br', up: typeof io.up === 'function' ? io.up : (io.up ? v3(io.up) : new V3(0, 0, 1)), upFromObject: !!io.object3D && io.upFromObject !== false, drawnFar: -1, zoom: 0, noise: io.noise || 0 };
      ins.camera = new THREE.PerspectiveCamera(ins.fov, ins.w / ins.h, ins.near, ins.far); ins.camera.layers.set(0);
      // up: a camera carried by an object3D rolls with it (its +Y, read every frame) unless upFromObject:false; otherwise the
      // given vector or function, default world +Z. setPose(pos, target, up) replaces it.
      ins.currentUp = function () {
        if (ins.object3D && ins.upFromObject) return new V3(0, 1, 0).transformDirection(ins.object3D.matrixWorld);
        return typeof ins.up === 'function' ? v3(ins.up()) : ins.up;
      };
      ins.lookAt = function (tp) {
        const dir = tp.clone().sub(ins.camera.position).normalize(), u = ins.currentUp(); const up = Math.abs(dir.dot(u)) > 0.985 ? new V3(0, 1, 0) : u;
        ins.camera.quaternion.setFromRotationMatrix(new THREE.Matrix4().lookAt(ins.camera.position, tp, up));
      };
      const lab = h('div', { class: 'wk-inset-label', text: ins.label }), state = h('div', { class: 'wk-inset-state' });
      const noise = h('div', { class: 'wk-inset-noise' }); if (ins.noise && NOISE_URL) { noise.style.backgroundImage = 'url(' + NOISE_URL + ')'; noise.style.opacity = String(clamp(ins.noise, 0, 1) * 0.22); } else noise.hidden = true;
      const el = h('div', { class: 'wk-inset', 'data-inset': id, title: 'click to enlarge / shrink' }, noise, lab, state);
      slotsEl.appendChild(el); ins.el = el; ins.stateEl = state;
      el.addEventListener('click', function () { ins.zoom = ins.zoom ? 0 : 2; layout(); app._dirty = true; });
      ins.slot = addSlot({ corner: ins.corner, w: ins.w, h: ins.h, el: el, zoom: 0 });
      Object.defineProperty(ins.slot, 'zoom', { get: () => ins.zoom, set: v => { ins.zoom = v; }, configurable: true });
      if (io.frustum !== false) {
        const helper = new THREE.Group(); helper.add(P.camera({ role: io.role || 'sensor', size: 22 }));
        ins.frustum = P.frustum({ role: io.role || 'sensor', fov: ins.fov, aspect: ins.w / ins.h }); helper.add(ins.frustum);
        ins.helper = helper; app.addHelper(helper);
      }
      insets.set(id, ins);
      syncInset(ins); app._dirty = true;
      const api = {
        id: id, camera: ins.camera, el: el, helper: ins.helper,
        // setPose(position, target, up?): free camera pose (stops following an object3D). up = Vector3 | [x,y,z] | function; omitted keeps the last up.
        setPose: function (pos, target, up) { ins.object3D = null; ins.position = pos; ins.target = target; if (up) ins.up = typeof up === 'function' ? up : v3(up); app._dirty = true; return api; },
        setFov: function (f) { ins.fov = f; ins.camera.fov = f; ins.camera.updateProjectionMatrix(); ins.drawnFar = -1; app._dirty = true; return api; },
        setLabel: function (t) { lab.textContent = t; return api; },
        markVisibility: function (p, occ) { return app.inset.markVisibility(id, p, occ); },
        remove: function () { app.inset.remove(id); },
      };
      ins.api = api;
      return api;
    },
    get: function (id) { const i = insets.get(id); return i ? i.api : null; },
    remove: function (id) { const i = insets.get(id); if (!i) return; i.el.remove(); i.slot.removed = true; if (i.helper && i.helper.parent) i.helper.parent.remove(i.helper); insets.delete(id); layout(); app._dirty = true; },
    list: function () { return Array.from(insets.keys()); },
    // Is targetPoint inside the inset camera's view AND unobstructed? Scene geometry only, not a measurement.
    // Also colours the inset frame: green visible / red blocked / amber outside field of view. -> {visible, inFov, blocked, hitObject}
    // eps (default 0.8 mm, see WK.lineOfSight): a target on a surface is not blocked by that surface. For a dot or corner
    // exactly ON the wall or plate pass gun.beamSurfacePoint().viewPoint (or a point nudged toward the observer).
    markVisibility: function (id, p, mo) {
      const ins = insets.get(id); if (!ins) return null;
      mo = Array.isArray(mo) ? { occluders: mo } : (mo || {});   // mo: occluders[] | {occluders, ignore:[Object3D], eps (mm, default 0.8)}
      syncInset(ins);
      const tp = v3(p), ndc = tp.clone().project(ins.camera);
      const inFov = ndc.z > -1 && ndc.z < 1 && Math.abs(ndc.x) <= 1 && Math.abs(ndc.y) <= 1;
      const los = WK.lineOfSight(ins.camera.position, tp, mo.occluders || WK.occluders(app, { ignore: mo.ignore }), { eps: mo.eps == null ? 0.8 : mo.eps });
      const res = { inFov: inFov, blocked: !los.visible, visible: inFov && los.visible, hitObject: los.hitObject, distance: los.distance, hitDistance: los.hitDistance };
      ins.el.classList.toggle('is-visible', res.visible); ins.el.classList.toggle('is-blocked', inFov && !los.visible); ins.el.classList.toggle('is-outfov', !inFov);
      const txt = res.visible ? 'target visible' : (!inFov ? 'target outside field of view' : 'target blocked' + (los.hitObject && (los.hitObject.name || los.hitObject.userData.role) ? ' by ' + (los.hitObject.name || los.hitObject.userData.role) : ''));
      if (ins.stateEl.textContent !== txt) ins.stateEl.textContent = txt;
      return res;
    },
  };

  // ---------------------------------------------------------- corner inset (2D seam cross-section)
  // Exact scene geometry of where the gun's dot sits relative to the seam. NOT a sensor reading.
  (function () {
    let api = null, pendingEstimate = null, pendingBeam = null;
    const pendingMarkers = new Map();   // id -> {radial, vertical, label, role}; kept until the inset exists
    const R0 = -16, R1 = 8, Z0 = -8.5, Z1 = 9, S = 10, X0 = 12, Y0 = 26, VW = 264, VH = 214;
    const sx = r => X0 + (r - R0) * S, sy = z => Y0 + (Z1 - z) * S;
    function build(co) {
      const gun = co.gun || app.gun;
      const rWall = DIM.tubeWall, rec = DIM.capRecess, thick = DIM.capThickness;
      const svg = WK.svg('svg', { viewBox: '0 0 ' + VW + ' ' + VH, class: 'wk-corner-svg', role: 'img', 'aria-label': 'seam cross-section: dot position relative to the joint' });
      const g = (cls) => WK.svg('g', { class: cls });
      svg.appendChild(WK.svg('rect', { x: X0, y: Y0, width: (R1 - R0) * S, height: (Z1 - Z0) * S, class: 'cs-bg' }));
      const grid = g('cs-grid');
      for (let r = -15; r <= 5; r += 5) grid.append(WK.svg('line', { x1: sx(r), y1: Y0, x2: sx(r), y2: sy(Z0) }), WK.svg('text', { x: sx(r), y: Y0 + (Z1 - Z0) * S + 10, 'text-anchor': 'middle', text: r }));
      for (let z = -5; z <= 10; z += 5) grid.append(WK.svg('line', { x1: X0, y1: sy(z), x2: sx(R1), y2: sy(z) }));
      svg.appendChild(grid);
      // metal: plate (left of the wall, below the joint) and wall (right of the joint, full height)
      svg.appendChild(WK.svg('rect', { x: X0, y: sy(0), width: sx(0) - X0, height: thick * S, class: 'cs-plate' }));
      svg.appendChild(WK.svg('rect', { x: sx(0), y: sy(rec), width: rWall * S, height: sy(Z0) - sy(rec), class: 'cs-wall' }));
      svg.appendChild(WK.svg('circle', { cx: sx(0), cy: sy(0), r: 3, class: 'cs-seam' }));
      svg.appendChild(WK.svg('text', { x: sx(0) + 6, y: sy(0) + 14, class: 'cs-t', text: 'seam' }));
      svg.appendChild(WK.svg('text', { x: X0 + 4, y: sy(-thick / 2) + 3, class: 'cs-t2', text: 'plate 6.35' }));
      svg.appendChild(WK.svg('text', { x: sx(rWall) + 4, y: sy(-3), class: 'cs-t3', text: 'wall 1.65' }));
      svg.appendChild(WK.svg('path', { d: 'M' + sx(4.6) + ' ' + sy(0) + 'V' + sy(rec) + 'M' + (sx(4.6) - 3) + ' ' + sy(0) + 'H' + (sx(4.6) + 3) + 'M' + (sx(4.6) - 3) + ' ' + sy(rec) + 'H' + (sx(4.6) + 3), class: 'cs-dim' }));
      svg.appendChild(WK.svg('text', { x: sx(4.6) + 5, y: sy(rec / 2) + 3, class: 'cs-t3', text: 'rim 6.35' }));
      const beam = WK.svg('line', { class: 'cs-beam' }), head = WK.svg('polygon', { class: 'cs-beamhead' });
      const cross = WK.svg('path', { class: 'cs-dot' }), dotc = WK.svg('circle', { r: 4, class: 'cs-dotc' });
      const estLine = WK.svg('line', { class: 'cs-estline' }), est = WK.svg('circle', { r: 5.5, class: 'cs-est' }), estT = WK.svg('text', { class: 'cs-estt', text: 'est.' });
      const markG = g('cs-markers');
      svg.append(markG, estLine, est, estT, beam, head, cross, dotc);
      svg.appendChild(WK.svg('text', { x: X0, y: 15, class: 'cs-title', text: 'Seam cross-section (mm, joint = 0)' }));
      svg.appendChild(WK.svg('text', { x: sx(R1) - 2, y: sy(Z0) - 4, class: 'cs-axis', 'text-anchor': 'end', text: 'r → wall' }));
      svg.appendChild(WK.svg('text', { x: X0 + 3, y: Y0 + 11, class: 'cs-axis', text: '↑ z' }));
      const read = h('div', { class: 'wk-corner-read' }), note = h('div', { class: 'wk-corner-note', text: 'scene geometry — exact, not a sensor reading' });
      const pill = h('div', { class: 'wk-corner-pill', text: 'Seam cross-section \u25B8' });
      const el = h('div', { class: 'wk-corner' }, pill, svg, read, note);
      slotsEl.appendChild(el);
      const slot = addSlot({ corner: co.corner || 'tl', w: 264, h: 285, autoH: true, collapsible: true, open: false, el: el, onLayout: function (s) { const k = s.dw / 264; svg.style.width = '100%'; el.style.fontSize = Math.max(9, 11 * k) + 'px'; } });
      el.addEventListener('click', function () { if (W < 560) { slot.open = !slot.open; layout(); app._dirty = true; } });
      let last = '', est_ = pendingEstimate, beamDir_ = pendingBeam;
      const markers = new Map();   // id -> {spec, ring, txt}
      function setMarker(id, m) {
        let e = markers.get(id);
        if (!e) {
          const col = WK.roleHex(m.role || 'sensor');
          e = { ring: WK.svg('circle', { r: 3.6, class: 'cs-mark' }), txt: WK.svg('text', { class: 'cs-markt' }) };
          e.ring.style.stroke = col; e.txt.style.fill = col;   // inline: the corner-svg text rule would beat a fill attribute
          markG.append(e.ring, e.txt); markers.set(id, e);
        }
        e.spec = { radial: +m.radial, vertical: +m.vertical, label: m.label == null ? '' : String(m.label) };
        e.txt.textContent = e.spec.label; last = ''; app._dirty = true;
      }
      function dropMarker(id) { const e = markers.get(id); if (!e) return; e.ring.remove(); e.txt.remove(); markers.delete(id); last = ''; app._dirty = true; }
      pendingMarkers.forEach((m, id) => setMarker(id, m));
      const P2 = (r, z) => [clamp(sx(r), X0 + 4, sx(R1) - 4), clamp(sy(z), Y0 + 4, sy(Z0) - 4)];
      function update() {
        if (!gun) return;
        const off = gun.dotOffset(), b = beamDir_ || gun.beamDir();
        let msig = ''; markers.forEach(function (e, id) { msig += id + e.spec.radial + ',' + e.spec.vertical + e.spec.label + ';'; });
        const sig = [off.radial, off.along, off.vertical, b.x, b.y, b.z, est_ ? est_.radial + ',' + est_.vertical : '', msig].map(v => typeof v === 'number' ? v.toFixed(3) : v).join('|');
        if (sig === last) return; last = sig;
        const p = P2(off.radial, off.vertical), off_ = Math.abs(sx(off.radial) - p[0]) > 0.5 || Math.abs(sy(off.vertical) - p[1]) > 0.5;
        dotc.setAttribute('cx', p[0]); dotc.setAttribute('cy', p[1]);
        cross.setAttribute('d', 'M' + (p[0] - 9) + ' ' + p[1] + 'H' + (p[0] + 9) + 'M' + p[0] + ' ' + (p[1] - 9) + 'V' + (p[1] + 9));
        const bl = Math.hypot(b.x, b.z) || 1, ux = b.x / bl, uz = b.z / bl;   // beam travels nozzle -> dot; in section: (ux, uz)
        const sxp = p[0] - ux * 62, syp = p[1] + uz * 62;                        // source side of the drawn beam (screen y is inverted)
        beam.setAttribute('x1', sxp); beam.setAttribute('y1', syp); beam.setAttribute('x2', p[0] - ux * 7); beam.setAttribute('y2', p[1] + uz * 7);
        const hx = p[0] - ux * 6, hy = p[1] + uz * 6, nx = uz, ny = ux;
        head.setAttribute('points', [p[0], p[1]].join(',') + ' ' + [hx - ux * 8 - nx * 4, hy + uz * 8 - ny * 4].join(',') + ' ' + [hx - ux * 8 + nx * 4, hy + uz * 8 + ny * 4].join(','));
        markers.forEach(function (e) { const q = P2(e.spec.radial, e.spec.vertical); e.ring.setAttribute('cx', q[0]); e.ring.setAttribute('cy', q[1]); e.txt.setAttribute('x', q[0] + 6); e.txt.setAttribute('y', q[1] - 5); });
        est.style.display = estLine.style.display = estT.style.display = est_ ? '' : 'none';
        if (est_) { const q = P2(est_.radial, est_.vertical); est.setAttribute('cx', q[0]); est.setAttribute('cy', q[1]); estT.setAttribute('x', q[0] + 8); estT.setAttribute('y', q[1] - 6); estLine.setAttribute('x1', p[0]); estLine.setAttribute('y1', p[1]); estLine.setAttribute('x2', q[0]); estLine.setAttribute('y2', q[1]); }
        const f = v => (Math.abs(v) < 0.005 || v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2);
        const tilt = Math.atan2(b.x, -b.z) / DEG, out = Math.asin(clamp(b.y, -1, 1)) / DEG;
        read.innerHTML = '<span>Δr ' + f(off.radial) + '</span><span>Δs ' + f(off.along) + '</span><span>Δz ' + f(off.vertical) + '</span><em>mm</em>' + (off_ ? '<b class="warn">off scale</b>' : '') +
          '<div class="sub">beam ' + Math.abs(tilt).toFixed(0) + '° from vertical in section, ' + Math.abs(out).toFixed(0) + '° out of it' + (est_ ? ' · est. err ' + Math.hypot(est_.radial - off.radial, est_.vertical - off.vertical).toFixed(2) + ' mm' : '') + '</div>';
      }
      app._after.push(update);
      return {
        el: el, slot: slot, update: update,
        setEstimate: function (e) { est_ = e || null; pendingEstimate = est_; last = ''; app._dirty = true; },
        addMarker: function (id, m) { pendingMarkers.set(id, m); setMarker(id, m); },
        removeMarker: function (id) { pendingMarkers.delete(id); dropMarker(id); },
        setBeam: function (d) { beamDir_ = d ? v3(d).normalize() : null; pendingBeam = beamDir_; last = ''; app._dirty = true; },
      };
    }
    // app.cornerInset({gun}) builds it; app.cornerInset.setEstimate({radial, vertical}|null) draws a second marker.
    app.cornerInset = function (co) {
      if (custom || !renderer) return null;
      co = co || {};
      if (api) return api;
      api = build(co);
      app.cornerInset.setEstimate = api.setEstimate; app.cornerInset.update = api.update;
      app.cornerInset.addMarker = api.addMarker; app.cornerInset.removeMarker = api.removeMarker; app.cornerInset.setBeam = api.setBeam;
      return api;
    };
    app.cornerInset.setEstimate = function (e) { pendingEstimate = e || null; };
    // addMarker(id, {radial, vertical, label, role}): extra points on the cross-section (a sweep of spots, a probe stylus);
    // same id again moves it. removeMarker(id). setBeam(dir | null) overrides the drawn beam direction (world vector).
    app.cornerInset.addMarker = function (id, m) { pendingMarkers.set(id, m); };
    app.cornerInset.removeMarker = function (id) { pendingMarkers.delete(id); };
    app.cornerInset.setBeam = function (d) { pendingBeam = d ? v3(d).normalize() : null; };
  })();

  // ---------------------------------------------------------- resize, render, loop
  function resize() {
    if (!box.clientWidth || !box.clientHeight) return;
    W = box.clientWidth; Hh = box.clientHeight;
    if (renderer) { renderer.setSize(W, Hh, false); camera.aspect = W / Hh; camera.updateProjectionMatrix(); }
    leadersEl.setAttribute('viewBox', '0 0 ' + W + ' ' + Hh);
    layout(); app._dirty = true;
  }
  if (global.ResizeObserver) new ResizeObserver(resize).observe(box); else global.addEventListener('resize', resize);

  let drawn = 0;
  function render() {
    if (!renderer) return;
    for (let i = 0; i < app._before.length; i++) { try { app._before[i](); } catch (e) { fail('before-render hook', e); app._before.splice(i--, 1); } }
    insets.forEach(syncInset);
    scene.updateMatrixWorld(true);
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, W, Hh);
    renderer.render(scene, camera);
    if (insets.size) {
      renderer.setScissorTest(true);
      insets.forEach(function (ins) {
        const s = ins.slot; if (s.removed) return;
        ins.camera.aspect = s.dw / s.dh; ins.camera.updateProjectionMatrix();
        const y = Hh - s.y - s.dh;
        renderer.setViewport(s.x, y, s.dw, s.dh); renderer.setScissor(s.x, y, s.dw, s.dh);
        renderer.render(scene, ins.camera);
      });
      renderer.setScissorTest(false);
      renderer.setViewport(0, 0, W, Hh);
    }
    if (legendDirty) { if (customLegend) legendDirty = false; else app.legend(); }
    placeLabels();
    for (let i = 0; i < app._after.length; i++) { try { app._after[i](); } catch (e) { fail('after-render hook', e); app._after.splice(i--, 1); } }
    drawn++;
  }
  app.render = render;

  let applied = false, ready = false, last = performance.now();
  function applyInitial() {
    registry.forEach(function (c) { if (c.type !== 'button') fire(c); });
  }
  function tick(now) {
    requestAnimationFrame(tick);
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    try {
      if (!applied) { applied = true; resize(); if (!custom && camera && firstView) app.setView(viewName, { instant: true }); applyInitial(); }
      let active = app._animate;
      for (let i = 0; i < app._frame.length; i++) {
        let r; try { r = app._frame[i](dt, now / 1000); } catch (e) { fail('onFrame', e); app._frame.splice(i--, 1); r = false; }
        if (r !== false) active = true;
      }
      if (orbit && orbit.update()) active = true;
      if (active || app._dirty) { app._dirty = false; render(); }
    } catch (e) { fail('frame', e); }
    if (!ready && (drawn > 0 || custom || !renderer)) {
      ready = true; global.__sceneReady = true;
      readyCbs.splice(0).forEach(fn => { try { fn(); } catch (e) { fail('onReady', e); } });
    }
  }
  requestAnimationFrame(tick);

  // ---------------------------------------------------------- default content
  if (!custom && renderer) {
    if (o.workstation) app.workstation = WK.addWorkstation(app, o.workstation === true ? {} : o.workstation);
    if (o.gun) app.gun = WK.addGun(app, o.gun === true ? {} : o.gun);
  }
  global.__app = app;
  return app;
};

})(window);
