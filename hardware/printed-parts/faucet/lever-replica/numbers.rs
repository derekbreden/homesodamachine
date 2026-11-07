//! The scan-derived faucet lever's numbers, in millimetres, in its own part frame: X lateral, +Y
//! from the paddle tip toward the attachment, +Z out through the customer-facing outer surface,
//! the inner paddle plane at Z = 0 (`evidence/datums.json` maps the scans). The body has parallel
//! lateral faces and a 9 mm cylinder channel; it prints on its side, so neither lateral face takes
//! a draft and the channel is a bridged gap. The rear of each ledge's upper face is occluded in
//! the scans, so the ledge's top is a fit-trial number, not a measurement.

pub type P2 = [f64; 2];

/// Across the lateral faces, as printed.
pub const PRINTED_OUTSIDE_WIDTH: f64 = 12.40;
/// The channel, as printed.
pub const CHANNEL_PRINTED_WIDTH: f64 = 9.00;
/// The pocket's floor, and the ledge's top.
pub const FLOOR_Z: f64 = 0.0;
pub const LEDGE_TOP: f64 = -5.55;
/// The lower slot's half width.
pub const LOWER_SLOT_HALF_WIDTH: f64 = 1.45;
/// The cutters' reach: below, above, in front of the tip and behind the attachment.
pub const CUT_BELOW: f64 = -14.0;
pub const CUT_ABOVE: f64 = 7.0;
pub const CUT_FRONT: f64 = -3.0;
pub const CUT_REAR: f64 = 60.0;

/// The outer surface's side profile, `(y, z)` stations along the paddle.
pub const SHOW_PROFILE: [P2; 13] = [
    [0.8, 2.95],
    [5.0, 2.84],
    [15.0, 2.74],
    [25.0, 2.77],
    [35.0, 2.94],
    [37.0, 2.97],
    [38.5, 4.08],
    [40.0, 4.43],
    [41.5, 4.05],
    [43.0, 3.13],
    [46.0, 3.00],
    [49.5, 3.04],
    [50.5, 3.00],
];
/// The attachment's rear underside.
pub const REAR_BOTTOM_PROFILE: [P2; 3] = [[51.0, -7.5], [50.2, -8.85], [49.3, -9.03]];
/// The rail's underside, from the ledge forward to the tip.
pub const RAIL_START: P2 = [36.65, -5.55];
pub const RAIL_BOTTOM_PROFILE: [P2; 6] = [[35.0, -5.30], [30.0, -4.86], [20.0, -3.76], [10.0, -2.56], [5.0, -1.88], [1.1, -0.75]];
/// The pocket's stop at the attachment: its first stations, then its tail, `(x, y)`.
pub const STOP_HEAD: [P2; 3] = [[CHANNEL_PRINTED_WIDTH / 2.0, 44.30], [4.20, 44.90], [4.00, 45.18]];
pub const STOP_TAIL: [P2; 7] = [[3.80, 45.31], [3.50, 45.40], [3.00, 45.48], [2.70, 45.53], [2.50, 45.60], [2.30, 45.72], [2.20, 45.92]];
/// The pocket: where it starts along Y, its front corner radius, and where it joins the stop.
pub const POCKET_START_Y: f64 = 1.2;
pub const POCKET_FRONT_RADIUS: f64 = 0.5;
pub const POCKET_STOP_JOIN_Y: f64 = 46.1;
/// The pocket's ceiling, `(y, z)`.
pub const POCKET_CEILING: [P2; 5] = [[37.0, 0.12], [39.0, 0.12], [42.0, -0.38], [44.0, -0.52], [POCKET_STOP_JOIN_Y, -0.55]];
/// The ledge's lip, `(y, z)`: its start, a point on it and its end on the ledge's top.
pub const LEDGE_LIP_START: P2 = [36.70, -10.18];
pub const LEDGE_LIP_MID: P2 = [37.7, -7.25];
pub const LEDGE_LIP_END: P2 = [40.50, LEDGE_TOP];

/// The outline's other control points, `(y, z)`: where it starts, the arc round the tip to the
/// show profile, the arc round the rear, the corner under the ledge, and the tip's return.
pub const OUTER_START: P2 = [0.0, 0.8];
pub const TIP_ARC: [P2; 2] = [[0.1, 2.4], SHOW_PROFILE[0]];
pub const REAR_ARC: [P2; 2] = [[52.65, 0.2], [52.0, -4.0]];
pub const OUTER_CORNER: [P2; 3] = [[37.5, -10.15], [36.8, -10.05], [36.70, -9.5]];
pub const TIP_RETURN_MID: P2 = [0.35, -0.2];
/// Where the pocket's floor ends, and its lower corner.
pub const POCKET_FLOOR_END: P2 = [30.0, FLOOR_Z];
pub const POCKET_LOWER_CORNER: P2 = [36.0, CUT_BELOW];

/// The lower reliefs: at each height, the right side's stations `(x, y)` the relief is ruled
/// through.
pub const LOWER_RELIEF: [(f64, [P2; 5]); 3] = [
    (-11.5, [[LOWER_SLOT_HALF_WIDTH, POCKET_START_Y], [LOWER_SLOT_HALF_WIDTH, 47.5], [2.1, 48.2], [4.4, 50.2], [5.4, 52.7]]),
    (LEDGE_TOP, [[1.65, POCKET_START_Y], [1.65, 47.5], [2.2, 48.2], [4.4, 50.2], [5.4, 52.7]]),
    (-0.55, [[2.20, POCKET_START_Y], [2.20, 47.5], [2.6, 48.25], [4.4, 50.2], [5.4, 52.7]]),
];
/// The upper reliefs.
pub const UPPER_RELIEF: [(f64, [P2; 5]); 3] = [
    (-0.56, [[0.25, 47.22], [2.2, 48.05], [3.5, 49.0], [4.4, 50.2], [5.4, 52.7]]),
    (2.75, [[2.20, 42.65], [3.35, 43.1], [3.90, 44.5], [4.50, 48.0], [5.4, 52.7]]),
    (5.20, [[5.30, 39.1], [5.80, 40.0], [6.40, 42.0], [7.00, 48.0], [8.0, 52.7]]),
];
/// The printed lever's colour, sRGB.
pub const SRGB: [f64; 3] = [0.91, 0.91, 0.87];

/// The pocket's stop, head and tail.
pub fn stop_profile() -> Vec<P2> {
    STOP_HEAD.iter().chain(STOP_TAIL.iter()).copied().collect()
}

/// The rail's underside from its start.
pub fn rail_profile() -> Vec<P2> {
    std::iter::once(RAIL_START).chain(RAIL_BOTTOM_PROFILE).collect()
}

fn edge_slope(h0: f64, h1: f64, m0: f64, m1: f64) -> f64 {
    let d = ((2.0 * h0 + h1) * m0 - h0 * m1) / (h0 + h1);
    let sign = |x: f64| if x == 0.0 { 0.0 } else { x.signum() };
    if sign(d) != sign(m0) {
        0.0
    } else if sign(m0) != sign(m1) && d.abs() > 3.0 * m0.abs() {
        3.0 * m0
    } else {
        d
    }
}

/// Each station with its shape-preserving cubic slope, `[x, y, dy/dx]`, in the stations' own
/// order: Fritsch-Butland harmonic slopes inside, one-sided shape-preserving slopes at the ends.
pub fn pchip(points: &[P2]) -> Vec<[f64; 3]> {
    assert!(points.len() >= 2, "a shape-preserving curve takes two stations at least");
    let mut sorted = points.to_vec();
    sorted.sort_by(|a, b| a[0].total_cmp(&b[0]));
    let h: Vec<f64> = sorted.windows(2).map(|w| w[1][0] - w[0][0]).collect();
    assert!(h.iter().all(|v| v.is_finite() && *v > 0.0), "the stations' x must be finite and distinct");
    let m: Vec<f64> = sorted.windows(2).zip(&h).map(|(w, h)| (w[1][1] - w[0][1]) / h).collect();
    let mut slopes = vec![0.0; sorted.len()];
    if sorted.len() == 2 {
        slopes.fill(m[0]);
    } else {
        slopes[0] = edge_slope(h[0], h[1], m[0], m[1]);
        let n = h.len();
        slopes[n] = edge_slope(h[n - 1], h[n - 2], m[n - 1], m[n - 2]);
        for k in 1..n {
            if m[k - 1] == 0.0 || m[k] == 0.0 || m[k - 1].signum() != m[k].signum() {
                continue;
            }
            let w1 = 2.0 * h[k] + h[k - 1];
            let w2 = h[k] + 2.0 * h[k - 1];
            let mean = (w1 / m[k - 1] + w2 / m[k]) / (w1 + w2);
            slopes[k] = 1.0 / mean;
        }
    }
    points
        .iter()
        .map(|p| {
            let k = sorted.iter().position(|q| q[0] == p[0]).expect("an author's station");
            [p[0], p[1], slopes[k]]
        })
        .collect()
}
