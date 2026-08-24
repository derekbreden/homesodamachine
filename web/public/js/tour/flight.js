// THE MOVE BETWEEN TWO STEPS, WHICH IS THE PART THAT TEACHES. A cut from a
// close-up of one fitting to a close-up of another says nothing about how the
// two are related; the reader arrives without knowing where they went. So the
// camera never cuts, and it never travels in a straight line through the
// machine either.
//
// EVERY TRANSITION PASSES THROUGH A THIRD POSE, and the third pose is the one
// that holds BOTH subjects at once — computed from the union of the two, not
// authored. The camera pulls back until where it is leaving and where it is
// going are in the same frame, swings around to the new heading while it is
// out there, and pushes back in. That wide beat is the whole answer to "where
// am I now": it is a map, shown at the moment it is needed, in the same
// continuous move.
//
// THE INTERPOLATION IS IN ORBIT SPACE — a target point, a radius, an azimuth
// and an elevation — rather than in world positions. Lerping positions dives
// the camera through the middle of the model; orbiting around a target that
// itself glides keeps the subject on screen the whole way and reads as one
// hand moving one camera.
//
// The curve through the three poses is the quadratic that PASSES THROUGH the
// middle one at t = 0.5, not one that merely leans toward it — the wide shot
// is a place the camera actually reaches.

import * as THREE from "three";

/** Signed shortest angular difference, in (−π, π]. */
const wrap = (d) => Math.atan2(Math.sin(d), Math.cos(d));

const easeInOut = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

// Slow at both ends AND at the middle, so the wide shot is legible without the
// camera ever stopping. Half the timing is this curve and half is the plain
// ease, which leaves about two thirds of full speed at the halfway mark: a
// beat, not a stall.
const PLATEAU_MIX = 0.5;
function plateau(t) {
  return t < 0.5 ? 0.5 * easeInOut(t * 2) : 0.5 + 0.5 * easeInOut((t - 0.5) * 2);
}
export function timing(t) {
  return (1 - PLATEAU_MIX) * easeInOut(t) + PLATEAU_MIX * plateau(t);
}

/** Quadratic through a, m, b that is exactly `m` at t = 0.5. */
function q(a, m, b, t) {
  const c = 2 * m - 0.5 * (a + b);
  const u = 1 - t;
  return u * u * a + 2 * u * t * c + t * t * b;
}

export function toOrbit(pose) {
  const o = pose.position.clone().sub(pose.target);
  const r = Math.max(o.length(), 1e-3);
  return {
    t: pose.target.clone(),
    r,
    az: Math.atan2(o.y, o.x),
    el: Math.asin(THREE.MathUtils.clamp(o.z / r, -1, 1)),
    up: (pose.up || new THREE.Vector3(0, 0, 1)).clone(),
  };
}

export function fromOrbit(o) {
  const ce = Math.cos(o.el);
  return {
    target: o.t.clone(),
    position: new THREE.Vector3(
      o.t.x + o.r * ce * Math.cos(o.az),
      o.t.y + o.r * ce * Math.sin(o.az),
      o.t.z + o.r * Math.sin(o.el),
    ),
    up: o.up.clone(),
  };
}

/** The heading halfway between two poses, as a unit direction. Used to pick
 *  where the wide shot stands before its distance is worked out. */
export function midHeading(a, b) {
  const A = toOrbit(a), B = toOrbit(b);
  const az = A.az + wrap(B.az - A.az) / 2;
  const el = (A.el + B.el) / 2;
  const ce = Math.cos(el);
  return [ce * Math.cos(az), ce * Math.sin(az), Math.sin(el)];
}

/**
 * How long the move should take. A quarter turn across the machine earns more
 * seconds than a nudge, and a big change of scale earns some too, so the
 * reading time is proportional to how much there is to follow.
 *
 * `span` is the model's own size, which is what makes the target travel a
 * fraction rather than a number of millimetres.
 */
export function durationFor(a, b, span) {
  const A = toOrbit(a), B = toOrbit(b);
  const turn = Math.abs(wrap(B.az - A.az)) + Math.abs(B.el - A.el);
  const move = span > 0 ? A.t.distanceTo(B.t) / span : 0;
  const zoom = Math.abs(Math.log(B.r / A.r));
  // The floor is low because a chapter's beats are neighbours: a step across
  // one fitting to the next should read as an adjustment, not as a journey.
  // What earns seconds is angle, distance and change of scale, and a move with
  // none of those has nothing to explain.
  return THREE.MathUtils.clamp(600 + 1150 * turn + 1500 * move + 750 * zoom, 900, 5000);
}

/**
 * A flight from `a` through `m` to `b`. `at(t)` for t in [0,1] gives the pose,
 * with the timing curve already applied.
 */
export function flight(a, m, b) {
  const A = toOrbit(a), M = toOrbit(m), B = toOrbit(b);
  // Unwrap so the swing takes the short way round at every leg rather than
  // spinning the long way to reach a number that is the same angle.
  const azM = A.az + wrap(M.az - A.az);
  const azB = azM + wrap(B.az - azM);

  return function at(raw) {
    const t = timing(THREE.MathUtils.clamp(raw, 0, 1));
    const o = {
      t: new THREE.Vector3(
        q(A.t.x, M.t.x, B.t.x, t),
        q(A.t.y, M.t.y, B.t.y, t),
        q(A.t.z, M.t.z, B.t.z, t),
      ),
      // Radius is blended in log space: halving and doubling are the same
      // amount of travel to the eye, and a linear blend of a near shot and a
      // far one spends nearly the whole move already far away.
      r: Math.exp(q(Math.log(A.r), Math.log(M.r), Math.log(B.r), t)),
      az: q(A.az, azM, azB, t),
      el: q(A.el, M.el, B.el, t),
      up: A.up.clone().lerp(B.up, t).normalize(),
    };
    return fromOrbit(o);
  };
}

/**
 * THE VERTIGO SHOT. Field of view and distance changed together so the subject
 * holds its size on screen while everything around it swells or collapses.
 * Nothing about the subject moves; the machine around it does. It is the exact
 * grammar for "this is INSIDE that" — which is what a move into the vessel is
 * saying, and what a cut or an arc can only imply.
 *
 * `fov(t)` is the lens through the move; the distance that keeps a subject of
 * `radius` filling the same fraction of the frame is the distance at which it
 * subtends the same angle, so the radius rides 1/tan of the half-angle.
 *
 * Returns the multiplier to apply to the flight's own radius at `t`.
 */
export function vertigoScale(fovFrom, fovTo, t, aspect) {
  const half = (fov) => {
    const v = THREE.MathUtils.degToRad(fov) / 2;
    return Math.min(v, Math.atan(Math.tan(v) * Math.max(aspect, 0.01)));
  };
  const now = THREE.MathUtils.lerp(fovFrom, fovTo, t);
  return { fov: now, scale: Math.tan(half(fovFrom)) / Math.tan(half(now)) };
}

/** The pose a step drifts to while it is held: a few degrees of swing and a
 *  touch of dolly, so the picture is alive without becoming a second move. */
export function driftedFrom(pose, drift) {
  if (!drift) return pose;
  const o = toOrbit(pose);
  o.az += THREE.MathUtils.degToRad(drift.az || 0);
  o.el = THREE.MathUtils.clamp(o.el + THREE.MathUtils.degToRad(drift.el || 0), -1.45, 1.45);
  o.r *= 1 + (drift.dolly || 0);
  return fromOrbit(o);
}

/** Straight blend between two poses in orbit space — what the dwell's drift
 *  runs on, and what a resume from a hand-moved camera starts with. */
export function tween(a, b, raw) {
  const A = toOrbit(a), B = toOrbit(b);
  const t = easeInOut(THREE.MathUtils.clamp(raw, 0, 1));
  return fromOrbit({
    t: A.t.clone().lerp(B.t, t),
    r: Math.exp(THREE.MathUtils.lerp(Math.log(A.r), Math.log(B.r), t)),
    az: A.az + wrap(B.az - A.az) * t,
    el: THREE.MathUtils.lerp(A.el, B.el, t),
    up: A.up.clone().lerp(B.up, t).normalize(),
  });
}

/** Linear (unclamped-in-time) drift, so the held shot moves at a constant rate
 *  rather than easing — an eased drift reads as another transition starting. */
export function driftAt(pose, drift, raw) {
  if (!drift) return pose;
  const t = THREE.MathUtils.clamp(raw, 0, 1);
  const o = toOrbit(pose);
  o.az += THREE.MathUtils.degToRad(drift.az || 0) * t;
  o.el = THREE.MathUtils.clamp(o.el + THREE.MathUtils.degToRad(drift.el || 0) * t, -1.45, 1.45);
  o.r *= 1 + (drift.dolly || 0) * t;
  return fromOrbit(o);
}
