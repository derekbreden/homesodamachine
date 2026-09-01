// Acceptance policy shared by edge-circle and face-cylinder fitting.
//
// A residual proportional only to the fitted radius is self-validating: the
// larger a bad fit grows, the more error it permits. Keep a hard residual cap,
// then require the sampled patch to subtend enough of the proposed circle for
// its curvature to have actually been measured. The second test rejects a
// numerically perfect giant-radius circle drawn through an almost-flat patch.

export const ROUND_FIT_RESIDUAL_MAX_MM = 0.5;
export const ROUND_FIT_MIN_SWEEP_DEG = 2.0;

export function roundFitMeasured(radius, span, residual) {
  if (![radius, span, residual].every(Number.isFinite)) return false;
  if (radius <= 1e-3 || span <= 0 || residual < 0) return false;

  const residualLimit = Math.min(
    ROUND_FIT_RESIDUAL_MAX_MM,
    Math.max(0.05, 0.02 * radius),
  );
  if (residual > residualLimit) return false;

  // A chord of `span` on radius `radius` subtends 2 asin(span / 2r).
  const sweep = 2 * Math.asin(Math.min(1, span / (2 * radius))) * (180 / Math.PI);
  return sweep >= ROUND_FIT_MIN_SWEEP_DEG;
}

// A fitted arc has to AGREE WITH ITSELF before it is reported. `fitCircle` draws its
// circle through a polyline's two ends and its midpoint, and on a chain whose ends nearly
// meet those three points are nearly two: the circumcircle through them is ill-conditioned
// and lands anywhere, while the residual test still passes because the permitted residual
// grows with the radius the bad fit invented.
//
// The reading that catches it is the one the fit never takes: a circular arc of radius r
// on a chord c runs r·θ, θ = 2 asin(c / 2r). A chord admits TWO arcs — the minor one and
// the major one that closes the rest of the circle — so a path length matching either is
// an arc and a path length matching neither is not a circle at all, whatever three points
// happen to lie on one. A near-closed chain of real arc comes through on the major branch;
// two straight segments bridging a collapsed feature match neither and report as `curve`,
// which is what they are.
export const ARC_FIT_LENGTH_REL = 0.02;
export const ARC_FIT_LENGTH_MIN_MM = 0.05;

export function arcFitMeasured(radius, chord, length) {
  if (![radius, chord, length].every(Number.isFinite)) return false;
  if (radius <= 1e-3 || length <= 0 || chord < 0) return false;
  if (chord > 2 * radius + ROUND_FIT_RESIDUAL_MAX_MM) return false;

  const theta = 2 * Math.asin(Math.min(1, chord / (2 * radius)));
  const minor = radius * theta;
  const major = radius * (2 * Math.PI - theta);
  const tol = Math.max(ARC_FIT_LENGTH_MIN_MM, ARC_FIT_LENGTH_REL * length);
  return Math.abs(length - minor) <= tol || Math.abs(length - major) <= tol;
}
