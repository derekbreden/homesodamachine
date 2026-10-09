// A6 two stations, one head (scene use-07-two-stations): plan-view cable bend over the head's travel, and what a second station overlaps.
// Cable: kit-style cubic Bezier from the grip's stub end (along the dot-to-grip direction, projected in plan) to a hook on a rail, then hook to a fixed
// cart. Radii 350 (emitting, at the seats) and 240 (stored, in transit) [manual p.20]. Plan-view radius is conservative for a climbing cable.
// Gun geometry: the kit proxy at the opening pose (illustrative). Usage: node calc/two_stations.mjs
const G = { grip: [-0.7, -233.5], dir: [-0.224, -0.837] }, EXIT = 70;
function bez(a, da, b, db, k, n = 100) { const d = Math.hypot(b[0] - a[0], b[1] - a[1]), kk = Math.max(15, k * d), c1 = [a[0] + da[0] * kk, a[1] + da[1] * kk], c2 = [b[0] - db[0] * kk, b[1] - db[1] * kk], p = []; for (let i = 0; i <= n; i++) { const t = i / n, u = 1 - t; p.push([u * u * u * a[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * b[0], u * u * u * a[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * b[1]]); } return p; }
function minR(p) { let m = Infinity; for (let i = 1; i < p.length - 1; i++) { const a = p[i - 1], b = p[i], c = p[i + 1], ab = [b[0] - a[0], b[1] - a[1]], bc = [c[0] - b[0], c[1] - b[1]], ca = [c[0] - a[0], c[1] - a[1]], cr = Math.abs(ab[0] * bc[1] - ab[1] * bc[0]); if (cr < 1e-9) continue; m = Math.min(m, Math.hypot(...ab) * Math.hypot(...bc) * Math.hypot(...ca) / (2 * cr)); } return m; }
function cable(u, mode, P) {
  const x = -P.s / 2 + u * P.s, a = [x + G.grip[0] + G.dir[0] * EXIT, G.grip[1] + G.dir[1] * EXIT], len = Math.hypot(...G.dir), da = [G.dir[0] / len, G.dir[1] / len];
  const hx = mode === 'mid' ? 0 : mode === 'half' ? x / 2 : a[0], hook = [hx, -P.rail], anchor = [0, -P.rail - P.cart];
  return Math.min(minR(bez(a, da, hook, [0, -1], P.stiff)), minR(bez(hook, [0, -1], anchor, [0, -1], P.stiff)));
}
console.log('Tightest bend (mm) at a seat (A end) and the tightest over the whole travel; requirement 350 at the seats, 240 between. spacing 520, cart 500 beyond the rail, stiffness 0.4');
console.log('rail   mode      | at seat | worst in travel | worst vs (350 at ends, 240 between)');
for (const rail of [600, 800, 1000, 1200, 1500]) for (const mode of ['mid', 'half', 'head']) {
  const P = { s: 520, rail: rail, cart: 500, stiff: 0.4 };
  let worst = Infinity, wr = Infinity; for (let i = 0; i <= 40; i++) { const r = cable(i / 40, mode, P), req = (i === 0 || i === 40) ? 350 : 240; wr = Math.min(wr, r); worst = Math.min(worst, r - req); }
  console.log(String(rail).padStart(5), mode.padEnd(8), '|', cable(0, mode, P).toFixed(0).padStart(7), '|', wr.toFixed(0).padStart(11), '     |', worst >= 0 ? 'meets' : 'short by ' + (-worst).toFixed(0));
}
// schedule: greedy earliest-start, person needed for prep, weld, swap; head for dry and weld; dry may run without a person
function sched(K, N, unatt, D) {
  const tasks = []; for (let i = 0; i < N; i++) { const k = i % K; tasks.push({ i, k, n: 'prep', d: D.prep, h: 1, hd: 0, prev: null }, { i, k, n: 'dry', d: D.dry, h: unatt ? 0 : 1, hd: 1, prev: 'prep' }, { i, k, n: 'weld', d: D.weld, h: 1, hd: 1, prev: 'dry' }, { i, k, n: 'swap', d: D.swap, h: 1, hd: 0, prev: 'weld' }); }
  const free = { h: 0, hd: 0, st: Array(K).fill(0) }, done = new Map(); let left = tasks.slice(), T = 0, idle = 0, lastHumanEnd = 0;
  while (left.length) { let best = null; left.forEach(t => { if (t.prev && !done.has(t.i + t.prev)) return; let s = Math.max(t.prev ? done.get(t.i + t.prev) : 0, free.st[t.k]); if (t.h) s = Math.max(s, free.h); if (t.hd) s = Math.max(s, free.hd); if (!best || s < best.s - 1e-9 || (Math.abs(s - best.s) < 1e-9 && t.i < best.t.i)) best = { t, s }; }); const t = best.t, e = best.s + t.d; if (t.h) { idle += Math.max(0, best.s - lastHumanEnd); lastHumanEnd = e; free.h = e; } if (t.hd) free.hd = e; free.st[t.k] = e; done.set(t.i + t.n, e); T = Math.max(T, e); left = left.filter(x => x !== t); }
  return { T, idle };
}
const D = { prep: 14, dry: 1, weld: 1.1, swap: 1 };
console.log('\nSchedule (min), 4 tubes, prep 14 dry 1 weld+retract 1.1 swap 1 [illustrative]:');
for (const [K, un] of [[1, false], [2, false], [2, true]]) { const r = sched(K, 4, un, D); console.log(` stations ${K}, dry lap without a person: ${un}  ->  finish ${r.T.toFixed(1)} min, person idle between tasks ${r.idle.toFixed(1)} min`); }
console.log('person-minutes per tube with these numbers:', D.prep + D.weld + D.swap, '(+', D.dry, 'if the dry lap needs a person)');
