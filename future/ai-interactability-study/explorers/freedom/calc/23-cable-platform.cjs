// Six taut lines on the gun shell: statics, stretch error, stiffness. ILLUSTRATIVE: layout from 22-cable-layout.cjs, EA values order-of-magnitude.
const FS = require('./statics.js'), FR = require('./ringmodel.js'); const M = FS.math;
const LAY = JSON.parse(require('fs').readFileSync(__dirname + '/22-cable-layout.json'));
const D = FR.DEFAULTS, pose = FS.dialsToPose(45, 30, -15), W = l => M.add(pose.origin, M.mv(pose.R, l));
function build(o) {
  o = Object.assign({ EA: 25000, scale: 1, count: 6, F: 2, droop: 0.5, cmd: [0,0,0,0,0,0], comp: false }, o);
  const idx = o.count === 4 ? [0,1,4,5] : [0,1,2,3,4,5];
  const lugsW = LAY.lugsLocal.map(W);
  const anchors = idx.map(i => { const u = LAY.dirs[i], s = (LAY.zTop - lugsW[i][2]) / u[2]; return [lugsW[i][0] + o.scale * s * u[0], lugsW[i][1] + o.scale * s * u[1], LAY.zTop]; });
  const els = []; const cabs = [];
  const mk = (L0s) => { els.length = 0; cabs.length = 0; idx.forEach((i, j) => { const L = M.len(M.sub(anchors[j], lugsW[i])); const c = { type: 'spring', a: { local: LAY.lugsLocal[i] }, b: { world: anchors[j] }, k: o.EA / L, L0: L0s[j], slack: true, name: 'line ' + (j+1), group: 'lines' }; els.push(c); cabs.push(c); });
    els.push({ type: 'gravity' }); const ex = M.mv(pose.R, FS.ROLL_AXIS), pd = M.norm(M.add(M.mul(ex, 1 - o.droop), [0, 0, -o.droop])); els.push({ type: 'force', pt: { local: FS.GRIP_BASE }, F: M.mul(pd, o.F), group: 'umbilical' });
    return FS.makeModel({ body: { mass: D.mass, com: D.com, ref: pose, dotLocal: [0,0,-16] }, nodes: [], elements: els }); };
  // IK: lengths at the commanded pose
  const xc = new Float64Array(6); for (let k = 0; k < 3; k++) { xc[k] = o.cmd[k]; xc[3 + k] = o.cmd[3 + k] * Math.PI / 180 * FS.S; }
  const m0 = mk(idx.map(() => 1)); const geo = idx.map((i, j) => M.len(M.sub(anchors[j], m0.bodyPoint(xc, LAY.lugsLocal[i]))));
  let L0 = geo.slice(), model = mk(L0), res = model.solve(xc, { maxIter: 100 });
  if (o.comp) for (let it = 0; it < 3; it++) { const T = cabs.map(c => Math.max(0, model.springForce(res.x, c).T)); L0 = geo.map((g, j) => g - T[j] / cabs[j].k); model = mk(L0); res = model.solve(xc, { maxIter: 100 }); }
  return { model, res, cabs, geo, anchors, xc, idx };
}
function report(l, o) { const b = build(o); const x = b.res.x; const T = b.cabs.map(c => b.model.springForce(x, c).T); const err = [0,1,2].map(k => x[k] - b.xc[k]); const dc = b.model.dotCompliance(x); const th = [3,4,5].map(k => (x[k]-b.xc[k]) / FS.S * 180/Math.PI);
  console.log(l.padEnd(44), 'conv', b.res.converged, '| T', T.map(v=>v.toFixed(1)).join(','), '| dot err mm', err.map(v=>v.toFixed(3)).join(','), '| tilt err deg', th.map(v=>v.toFixed(3)).join(','), '| mm/N', [0,1,2].map(i=>dc.C[i][i].toFixed(3)).join(','), '| free', dc.free); return b; }
report('Dyneema-ish EA 25 kN, at reference', {});
report('thin braid EA 3 kN', { EA: 3000 });
report('thin braid, stretch compensated', { EA: 3000, comp: true });
report('steel EA 40 kN', { EA: 40000 });
report('Dyneema, cmd +5 mm z', { cmd: [0,0,5,0,0,0] });
report('Dyneema, cmd +8 mm r, 2 deg tilt', { cmd: [8,0,0,2,0,0] });
report('umbilical 6 N droop 0', { F: 6, droop: 0 });
report('four lines', { count: 4 });
for (const sc of [0.5, 0.75, 1.25]) report('frame scale ' + sc, { scale: sc });
