// How much of a per-turn sine linearity error does an offset-and-gain fit over a pose window remove?
// (borrowed-03 wave 3: the scene's "calibrated by a fixed-point trial" toggle uses this fit per joint.)
function resid(A, phase, th0, W) {
  const n = 41, xs = [], ys = [];
  for (let i = 0; i < n; i++) { const t = th0 + (-W + 2 * W * i / (n - 1)) * Math.PI / 180; xs.push(t - th0); ys.push(A * Math.sin(t + phase)); }
  const mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
  let sxx = 0, sxy = 0; for (let i = 0; i < n; i++) { sxx += (xs[i] - mx) ** 2; sxy += (xs[i] - mx) * (ys[i] - my); }
  const b = sxy / sxx, a = my - b * mx;
  let m = 0; for (let i = 0; i < n; i++) m += (ys[i] - (a + b * xs[i])) ** 2;
  return Math.sqrt(m / n) / (A / Math.SQRT2);   // rms residual over the rms of the raw sine
}
for (const W of [5, 10, 15, 25, 40]) {
  const r = []; for (let ph = 0; ph < 6.2; ph += 0.4) r.push(resid(1, ph, 0.7, W));
  console.log('window +-' + W + ' deg: residual / raw rms  mean ' + (r.reduce((a, b) => a + b, 0) / r.length).toFixed(3) + '  max ' + Math.max(...r).toFixed(3));
}
