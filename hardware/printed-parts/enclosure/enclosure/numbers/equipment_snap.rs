//! The three-dot equipment snap in section, measured from the unbent outer wall and the seated stop.

/// The fixed face from the roof down the running guide, retaining shoulder, lip and entrance.
/// Radial coordinates increase outward. Closing coordinates increase toward the roof.
pub const CHEEK: [[f64; 2]; 7] = [
    [-1.818, 0.0],
    [-2.96475, -2.40],
    [-3.876, -6.40],
    [-4.22, -8.73],
    [-2.20, -10.75],
    [-2.20, -11.11],
    [-3.60561568737, -13.35],
];

pub const WALL: f64 = 2.0;
const JOIN: f64 = -28.40;
const LIP: f64 = -10.75;
const FREE_BIAS: f64 = 0.80;

/// Walk the relaxed leaf from the outer root to the flat foot and back down to the inner root.
/// The crest of the straight leaf is at zero. Only the rootward shank adapts to the station's join.
pub fn wing(join: f64) -> Vec<[f64; 2]> {
    let straight = [
        [0.0, JOIN - 0.05],
        [0.0, 0.0],
        [-WALL, 0.0],
        [-3.125, -2.40],
        [-4.0, -6.40],
        [-4.0, -8.95],
        [-WALL, -10.95],
        [-WALL, JOIN - 0.05],
    ];
    let load_span = LIP - JOIN;
    let tip_deflection = (3.0 * -JOIN / load_span - 1.0) / 2.0;
    let mut points = Vec::new();
    for step in straight.windows(2) {
        let [a, b] = [step[0], step[1]];
        let count = ((b[1] - a[1]).abs() / 0.60).ceil().max(1.0) as usize;
        for i in 0..count {
            let k = i as f64 / count as f64;
            let r = a[0] + k * (b[0] - a[0]);
            let z = a[1] + k * (b[1] - a[1]);
            let t = ((z - JOIN) / load_span).max(0.0);
            let bend = if t <= 1.0 { t * t * (3.0 - t) / 2.0 } else { (3.0 * t - 1.0) / 2.0 };
            let u = t.min(1.0);
            let angle = (FREE_BIAS * 1.5 * u * (2.0 - u) / (load_span * tip_deflection)).atan();
            let midwall = r + WALL / 2.0;
            let radius = midwall * angle.cos() - WALL / 2.0 - FREE_BIAS * bend / tip_deflection;
            let z = z + midwall * angle.sin();
            let blend = ((z - JOIN) / 9.0).clamp(0.0, 1.0);
            points.push([radius, z + (join - JOIN) * (1.0 - blend * blend * (3.0 - 2.0 * blend))]);
        }
    }
    points.push([-WALL, join - 0.05]);
    points
}
