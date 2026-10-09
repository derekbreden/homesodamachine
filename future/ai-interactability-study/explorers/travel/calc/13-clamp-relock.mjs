// travel-05b after use's exchange: the clamp is the last handover; what does a look after it buy, and how big may the closing shift be?
// Uses the closure model of explorers/use/calc/w2_handover.mjs (read, not edited). Every number ILLUSTRATIVE (the scene's defaults).
//   node explorers/travel/calc/13-clamp-relock.mjs
import { DEF, run, closure, mulberry } from '../../use/calc/w2_handover.mjs';
const pct = r => (100 * r.inside).toFixed(0).padStart(3) + '%';
console.log('re-run of use\'s numbers (2000 closures, window +-0.10 mm):');
console.log('  B, look after the clamp        ', pct(run('B', DEF)));
console.log('  B, no look after the clamp     ', pct(run('B', { ...DEF, after: false })));
console.log('  B, clamp bias 0.08, look after ', pct(run('B', { ...DEF, bm: 0.08 })), ' no look', pct(run('B', { ...DEF, bm: 0.08, after: false })), ' bias learned, no look', pct(run('B', { ...DEF, bm: 0.08, learn: true, after: false })));
console.log('\nhow large may the clamp\'s closing scatter be? (mean 0)');
console.log('  sigma mm   no look   one look-and-relock loop (up to 6)   mean relocks');
for (const sl of [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15]) {
  const a = run('B', { ...DEF, sl, after: false }), b = run('B', { ...DEF, sl }); let rel = 0, N = 1000; const rng = mulberry(11);
  for (let i = 0; i < N; i++) rel += closure('B', { ...DEF, sl }, rng).steps.filter(s => s.id === 'relock').length;
  console.log('  ' + String(sl).padEnd(8), '  ' + pct(a), '                ' + pct(b), '                      ', (rel / N).toFixed(2));
}
console.log('\na wedge that always pushes to one side (mean shift, small scatter 0.01 mm) against a pinch (mean 0, scatter 0.05):');
for (const [name, P] of [['wedge, mean 0.08, sigma 0.01, no look', { ...DEF, bm: 0.08, sl: 0.01, after: false }], ['wedge, mean 0.08, sigma 0.01, bias learned, no look', { ...DEF, bm: 0.08, sl: 0.01, learn: true, after: false }], ['wedge, mean 0.08, sigma 0.01, bias learned, one look', { ...DEF, bm: 0.08, sl: 0.01, learn: true }], ['pinch, mean 0, sigma 0.05, no look', { ...DEF, after: false }], ['pinch, mean 0, sigma 0.05, look after', { ...DEF }]])
  console.log('  ' + name.padEnd(56), pct(run('B', P)));
console.log('\nfriction: rounds, not accuracy (median rounds of the first trim, 2000 closures):');
for (const fg of [0.02, 0.15, 0.5, 1.0]) { const rng = mulberry(3); const rs = []; for (let i = 0; i < 2000; i++) { const c = closure('B', { ...DEF, fg }, rng); rs.push(c.steps.find(s => s.id === 'trim').rounds); } rs.sort((a, b) => a - b); console.log('  friction', String(fg).padEnd(5), 'N: median', rs[1000], ' 90th percentile', rs[1800], ' at the 6-round limit', (100 * rs.filter(v => v >= 6).length / 2000).toFixed(0) + '%'); }
