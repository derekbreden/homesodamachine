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
