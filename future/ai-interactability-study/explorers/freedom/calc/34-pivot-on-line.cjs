// freedom W3: a sled pivot on the roll-axis line (through the dot and the cable exit): what the balance and the stiffness need.
// The numbers behind scene freedom-17-hung-on-the-line. ILLUSTRATIVE: gun + shell 1.2 kg, COM (0,-18,178) local, keel 0.6 kg on a 200 mm post, cable
// static vertical load 0.6 N and step 0.03 N at the S-boot exit 709 mm from the dot (calc/33). Kit proxy gun at roll 0, hole dial 30, vertical 0 (planar, gun plane vertical).
const FS = require('./statics.js'), G = 9.80665;
const pose = FS.dialsToPose(0, 30, 0), R = pose.R, o = pose.origin;
const W2 = (yl, zl) => [o[1] + R[4] * yl + R[5] * zl, o[2] + R[7] * yl + R[8] * zl];
const dot = W2(0, -16), grip = W2(-118, 237), com = W2(-18, 178);
const l = Math.hypot(grip[0] - dot[0], grip[1] - dot[1]), u = [(grip[0] - dot[0]) / l, (grip[1] - dot[1]) / l];
console.log('dot', dot.map(v => v.toFixed(1)), 'grip base', grip.map(v => v.toFixed(1)), '|DE|', l.toFixed(1), 'axis above horizontal', (Math.asin(u[1]) * 180 / Math.PI).toFixed(1), 'COM', com.map(v => v.toFixed(1)));
const M = 1.2, mk = 0.6, d = 200, fstat = 0.6, fstep = 0.03, RELEASE = 709;
console.log('q     COM below pivot   horizontal offset   keel side offset (0.6 kg)   K (N*m/rad)   lever to release   step 0.03 N: tilt deg / dot mm   spring for 0.1 mm');
for (const q of [40, 70, 110, 150, 200, 279, 350, 420]) {
  const P = [dot[0] + u[0] * q, dot[1] + u[1] * q], Rp = [dot[0] + u[0] * RELEASE, dot[1] + u[1] * RELEASE], mc = fstat / G;
  const above = P[1] - com[1], hoff = com[0] - P[0], s = -(M * (com[0] - P[0]) + mc * (Rp[0] - P[0])) / mk;
  const K = G * (M * above + mk * d + mc * (P[1] - Rp[1])) / 1000, lever = Math.abs(Rp[0] - P[0]), dTau = fstep * lever;
  const tilt = dTau / (K * 1000), dotShift = tilt * q, need = dTau / (0.1 / q) / 1000;
  console.log(String(q).padEnd(5), (-above).toFixed(0).padStart(6), '   ', hoff.toFixed(0).padStart(6), '            ', s.toFixed(0).padStart(6), '                  ', K.toFixed(2).padStart(6), '        ', lever.toFixed(0).padStart(6), '        ', (tilt * 180 / Math.PI).toFixed(2).padStart(6), '/', dotShift.toFixed(2).padStart(6), '          ', need.toFixed(0).padStart(6));
}
