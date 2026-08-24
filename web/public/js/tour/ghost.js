// THE MACHINE, FADED OUT AND BACK — so a beat that takes 137 bodies out of the
// view does it by dissolving them rather than by blinking them off.
//
// Isolating a sub-assembly is a change to `mesh.visible`, which is one frame
// wide: the cabinet, the compressor, the manifold and the power column are
// there and then they are not. Under camera motion that reads as a glitch, not
// as a reveal.
//
// WHAT FADES IS THE MODEL, NOT THE LIGHTS. The spotlight's tiers draw with
// their own materials at depth-test off, so the subject stays bright the whole
// way through and the box appears to dissolve off it. That is the picture worth
// having: not "everything goes, then the core arrives", but "the machine opens
// and the core was already standing there".
//
// IT MUTATES SHARED MATERIALS AND PUTS THEM BACK. The x-ray ghost caches one
// material per base colour and one per edge colour (viewer/xray.js), so there
// are a couple of dozen of them for two hundred bodies — cheap to drive, and
// wrong to leave changed. Every opacity is recorded the first time it is
// touched and restored exactly, so nothing about the reader's parts viewer is
// different for having watched this.

const base = new Map();   // material -> the opacity it had before we touched it

function collect(group) {
  const mats = new Set();
  if (!group) return mats;
  for (const child of group.children) {
    if (child.material) mats.add(child.material);
  }
  return mats;
}

/** Everything the model is drawn with, at `k` of its own brightness. */
export function setModelOpacity(group, k) {
  for (const m of collect(group)) {
    if (!base.has(m)) base.set(m, m.opacity);
    const b = base.get(m);
    m.opacity = b * k;
    // A material that was opaque has to be told it is not, or the alpha is
    // ignored and the body stays solid all the way to zero.
    if (k < 1 && !m.transparent) { m.transparent = true; m.userData.tourForcedAlpha = true; }
    m.visible = m.opacity > 0.001;
  }
}

/** Put every opacity back exactly as it was found. */
export function restoreModel(group) {
  for (const m of collect(group)) {
    if (base.has(m)) m.opacity = base.get(m);
    if (m.userData && m.userData.tourForcedAlpha) {
      m.transparent = false;
      delete m.userData.tourForcedAlpha;
    }
    m.visible = true;
  }
  base.clear();
}

/**
 * A dissolve with something happening at the bottom of it.
 *
 * `at(t)` for t in 0..1 drives the fade — down to `floor` at the halfway mark,
 * back to full at the end — and calls `midpoint` once, at the bottom, which is
 * where the thing being hidden or shown actually changes. The camera keeps
 * moving throughout; this only touches what it is looking at.
 *
 * `floor` is not zero. A machine that goes completely away and comes back is a
 * cut with extra steps; one that thins to a fifth stays present as a shape, and
 * the core is read as having been inside it all along.
 */
export function dissolve(group, midpoint, floor = 0.26) {
  let fired = false;
  return function at(t) {
    const u = Math.min(Math.max(t, 0), 1);
    // Symmetric: 1 at both ends, `floor` at the middle, eased so the bottom is
    // a moment rather than an instant.
    const v = 1 - Math.sin(Math.PI * u) ** 0.7;
    setModelOpacity(group, floor + (1 - floor) * v);
    if (!fired && u >= 0.5) { fired = true; midpoint(); }
    if (u >= 1) restoreModel(group);
  };
}
