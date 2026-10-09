// room-08: what a fiducial-tag pose from ONE fixed camera could do at the gun's distance, IDEAL optics (a lower bound; real
// systems are typically several times worse).  Numbers [illustrative]: 1920 px across a 30 deg field, tag 20 mm, corner noise
// 0.1 px.   Run: node explorers/room/calc/fiducial-pose-error.mjs
const fov = 30 * Math.PI / 180, W = 1920, f = (W / 2) / Math.tan(fov / 2);
for (const d of [250, 400, 600]) {
  const mmPerPx = d / f;
  for (const tag of [15, 20, 30]) {
    const tagPx = tag / mmPerPx, sig = 0.1;
    const lateral = sig * mmPerPx, depth = d * sig / tagPx, tilt = (sig / tagPx) * 180 / Math.PI;
    console.log(`distance ${d} mm: ${mmPerPx.toFixed(3)} mm/px; tag ${tag} mm = ${tagPx.toFixed(0)} px -> lateral ${lateral.toFixed(3)} mm, depth ${depth.toFixed(3)} mm, tag tilt ${tilt.toFixed(3)} deg (ideal)`);
  }
}
console.log('Rule of thumb for a real rig: multiply by 5 to 10 for lens distortion, calibration and glare. The dot itself is a point source and needs no tag.');
