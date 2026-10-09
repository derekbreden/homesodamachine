// travel-22: an arm brings the gun to a three-ball dock, then holds it, brakes, or floats it. Statics of a rigid plate on three spring
// contacts with a spring (hold, brake) or a force (float) at the flange. ILLUSTRATIVE numbers; the same model is in scenes/travel-22-arm-docks-then-floats.
//   node explorers/travel/calc/17-float-release.mjs
const G = 9.81;
export function model(mode, o) {
  const mEff = (o.teach ? 0.03 + o.drift : o.m + o.drift) + (mode === 'brake' ? 0.03 : 0), mvEff = o.teach ? 0.03 : o.mv;
  const ka = mode === 'hold' ? o.ka : mode === 'brake' ? 20 : o.kf, fext = o.dF + (mode === 'float' ? o.fr : 0);
  const Ctr = 1 / (1.5 * o.kc), Crk = o.h * o.L / (1.5 * o.kc * o.rb * o.rb), Cdot = Ctr + Crk;
  const x = Cdot * (ka * mEff + fext) / (1 + Cdot * ka), Fs = x / Cdot, Farm = ka * (mEff - x);
  const Ntot = mode === 'float' ? o.P - o.dm * G : o.P + ka * mvEff * (mode === 'hold' ? 1 : 0.5);
  const dN = Fs * o.h / (1.5 * o.rb * o.rb), Ni = [90, 210, 330].map(a => Ntot / 3 + dN * o.rb * Math.cos((a - o.phi) * Math.PI / 180));
  return { x, xt: Fs * Ctr, xr: Fs * Crk, Fs, Farm, Ntot, minN: Math.min(...Ni), slip: Math.abs(Fs) > 0.2 * Math.max(Ntot, 0) };
}
const D = { m: 0.5, mv: 0.1, drift: 0.05, ka: 5, kf: 0.1, fr: 1.5, dm: 0.1, dF: 1.0, phi: 0, P: 15, kc: 40, rb: 50, h: 120, L: 200 };
const f = v => (v * 1000).toFixed(0).padStart(5);
if (process.argv[1] && process.argv[1].endsWith('17-float-release.mjs')) {
  console.log('defaults: mismatch 0.5 mm, arm 5 N/mm, float residual 1.5 N, 0.1 kg declaration error, umbilical change 1 N, preload 15 N, 40 N/mm per ball, ball circle 50 mm, flange 120 mm up, dot 200 mm from the rocking axis');
  console.log('case                                             dot shift  translation  rocking   arm force N  lowest ball N  slips');
  const show = (name, o, mode) => { const r = model(mode, o); console.log(name.padEnd(48), f(r.x), 'um', f(r.xt), '   ', f(r.xr), '   ', r.Farm.toFixed(1).padStart(9), r.minN.toFixed(1).padStart(12), r.slip ? '   yes' : '    no'); };
  show('hold, taught pose 0.5 mm off', D, 'hold');
  show('brake', D, 'brake');
  show('float', D, 'float');
  show('float, declaration exact, friction 0.5 N', { ...D, dm: 0, fr: 0.5 }, 'float');
  show('float, read joints, re-teach, then hold', { ...D, teach: true }, 'hold');
  show('re-taught hold, seat near the dot (L 20, ring 80, h 60)', { ...D, teach: true, L: 20, rb: 80, h: 60 }, 'hold');
  show('float, seat near the dot', { ...D, L: 20, rb: 80, h: 60 }, 'float');
  show('re-taught hold, stiff contacts (400 N/mm)', { ...D, teach: true, kc: 400 }, 'hold');
  show('hold, arm 20 N/mm, taught pose 0.5 mm off', { ...D, ka: 20 }, 'hold');
  show('hold, arm 20 N/mm, re-taught', { ...D, ka: 20, teach: true }, 'hold');
  const h = model('hold', { ...D, teach: true }), fl = model('float', { ...D, teach: true });
  console.log('\nrelease shift (a re-taught hold, then the arm lets go into float):', ((fl.x - h.x) * 1000).toFixed(0), 'um');
  console.log('rocking against translation compliance at the dot (mm per N):', (D.h * D.L / (1.5 * D.kc * D.rb * D.rb)).toFixed(3), 'against', (1 / (1.5 * D.kc)).toFixed(3));
  console.log('a preload that keeps the lowest ball closed at 3 N sideways at 120 mm up, 50 mm circle: N/3 >= 3 x 120 / (1.5 x 50) =', (3 * 120 / (1.5 * 50)).toFixed(1), 'N per ball, i.e. at least', (3 * 3 * 120 / (1.5 * 50)).toFixed(0), 'N of preload plus margin');
}
