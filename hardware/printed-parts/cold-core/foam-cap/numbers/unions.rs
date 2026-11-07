//! The lid's union support: a filled pedestal under the forward leg of V-B's outlet return elbow,
//! whose cylindrical seat bears on the elbow's fixed body band, clear of its moving collets, and
//! whose closed passage takes the tie that holds the leg down; and that tie's route. V-A's union
//! travels with its valve on its tubing, so the lid carries no other.
use crate::P3;
use crate::design::{above_core, elbow_scan};
use crate::vector::{add, cross, dist, mul, radians};
use hsm_cold_core_layout::cap::{Pose, cap_face_z};

/// The elbow leg the seat bears on and the band along it, in the elbow's frame.
pub const NATIVE_LEG: &str = "z";
pub const NATIVE_BAND: [f64; 2] = [13., 16.];
/// The seat's station along the leg, the bore's start behind it and the bore's length.
pub const SEAT_STATION: f64 = 14.5;
pub const BORE_START: f64 = -5.;
pub const BORE_LENGTH: f64 = 50.;
/// The pedestal's wall round the seat, its half-span along the leg, and how far its root sinks
/// into the lid's face.
pub const WALL: f64 = 3.;
pub const HALF_SPAN: f64 = 5.75;
pub const ROOT_SINK: f64 = 0.15;
/// The tie passage's section, peaked below the seat to print without trapped support: points
/// across the leg and down from the peak.
pub const TIE_PROFILE: [[f64; 2]; 5] = [[-1.4, -4.4], [1.4, -4.4], [1.4, -2.6], [0., 0.], [-1.4, -2.6]];
/// How far below the seat the tie's lower run passes, past the seat's own radius.
pub const TIE_DROP: f64 = 6.3;
/// The passage's window runs this far past the pedestal's faces, and the passage runs this long
/// through it, centred on the section's plane.
pub const WINDOW_OVERRUN: f64 = 0.1;
pub const TIE_PASSAGE_LENGTH: f64 = 80.;
/// The part whose lid carries the support.
pub const HOST: &str = "foam-assembly";

/// The pedestal and its tie passage, in the enclosure.
#[derive(Clone, Copy, Debug)]
pub struct Support {
    /// The seat's centre on the leg.
    pub centre: P3,
    pub stock_min: P3,
    pub stock_max: P3,
    pub bore_origin: P3,
    pub bore_axis: P3,
    pub bore_length: f64,
    /// The seat: the band's largest measured radius on the head-on fit.
    pub seat_radius: f64,
    /// The passage's window through the pedestal, and the section's plane: the peak it hangs
    /// from, the section's X and the direction it runs through the pedestal.
    pub tie_window_min: P3,
    pub tie_window_max: P3,
    pub tie_profile_origin: P3,
    pub tie_profile_x: P3,
    pub tie_profile_normal: P3,
    /// How far down the leg's frame the tie's lower run passes.
    pub tie_route_down: f64,
}

/// The outlet return elbow's pose, as the above-core design's snapshot places it.
pub fn elbow_pose() -> Pose {
    above_core().snapshots.vb_outlet_return.pose()
}

/// The support under V-B's outlet return.
pub fn vb_outlet_return() -> Support {
    let frame = elbow_pose();
    let face = cap_face_z() - ROOT_SINK;
    let centre = frame.point([0., 0., SEAT_STATION]);
    let band = elbow_scan().profiles.z.fixed_body.iter().filter(|[station, _]| {
        NATIVE_BAND[0] <= *station && *station <= NATIVE_BAND[1]
    });
    let radius = band.map(|[_, r]| *r).fold(f64::NEG_INFINITY, f64::max) + crate::fits().slip;
    let down = frame.vector([1., 0., 0.]);
    let through = frame.vector([0., 1., 0.]);
    let wide = frame.vector([0., 0., -1.]);
    let peak = add(centre, mul(down, radius + WALL));
    let low = [centre[0] - radius - WALL, centre[1] - HALF_SPAN, face];
    let high = [centre[0], centre[1] + HALF_SPAN, centre[2]];
    let mut corners = vec![];
    for x in [low[0] - WINDOW_OVERRUN, high[0] + WINDOW_OVERRUN] {
        for [u, v] in TIE_PROFILE {
            let point: P3 = std::array::from_fn(|i| peak[i] + u * wide[i] - v * down[i]);
            let t = (x - point[0]) / through[0];
            corners.push(std::array::from_fn(|i| point[i] + t * through[i]));
        }
    }
    let [window_min, window_max] = crate::vector::bounds(&corners);
    Support {
        centre,
        stock_min: low,
        stock_max: high,
        bore_origin: frame.point([0., 0., BORE_START]),
        bore_axis: frame.vector([0., 0., 1.]),
        bore_length: BORE_LENGTH,
        seat_radius: radius,
        tie_window_min: window_min,
        tie_window_max: window_max,
        tie_profile_origin: peak,
        tie_profile_x: wide,
        tie_profile_normal: through,
        tie_route_down: radius + TIE_DROP,
    }
}

/// One run of a tie's route: straight between two points, or round an arc through three, with
/// the direction the strip's width lies along.
#[derive(Clone, Debug)]
pub enum TieRun {
    Line { points: [P3; 2], wide_axis: P3 },
    Arc { points: [P3; 3], radius: f64, sweep_degrees: f64, wide_axis: P3 },
}

impl TieRun {
    pub fn length(&self) -> f64 {
        match self {
            TieRun::Line { points: [a, b], .. } => dist(*a, *b),
            TieRun::Arc { radius, sweep_degrees, .. } => radius * radians(*sweep_degrees).abs(),
        }
    }
}

/// The nominal strip a tie is laid out as, and the stock it is cut from.
pub const TIE_STOCK: &str = "6-inch narrow nylon tie";
pub const TIE_STOCK_LENGTH: f64 = 152.4;
pub const TIE_WIDTH: f64 = 2.5;
pub const TIE_THICKNESS: f64 = 0.8;
/// The strip's air off the seat: half its thickness and the slip fit.
pub const TIE_AIR: f64 = 0.55;
/// The strip's arc round the seat, from below the leg's east side over its crown, in degrees.
pub const TIE_ARC: [f64; 2] = [-20., 170.];
/// How far outside the pedestal's flanks the strip's upright runs pass, and how far its west run
/// stands above the seat's centre or the arc's end, whichever is higher.
pub const TIE_FLANK_AIR: f64 = 0.8;
pub const TIE_CROWN_RISE: f64 = 3.;
pub const TIE_ARC_CLEAR: f64 = 1.;

fn arc_point(centre: P3, u: P3, v: P3, radius: f64, degrees: f64) -> P3 {
    let angle = radians(degrees);
    std::array::from_fn(|i| centre[i] + radius * (u[i] * angle.cos() + v[i] * angle.sin()))
}

/// The tie round V-B's outlet return and through its pedestal: an arc over the seat, down the
/// west flank, under the leg through the passage and back up the east flank.
pub fn vb_outlet_return_tie() -> Vec<TieRun> {
    let data = vb_outlet_return();
    let frame = elbow_pose();
    let centre = data.centre;
    let u = frame.vector([0., 1., 0.]);
    let v = frame.vector([1., 0., 0.]).map(|value| -value);
    let radius = data.seat_radius + TIE_AIR;
    let lower = arc_point(centre, u, v, radius, TIE_ARC[0]);
    let upper = arc_point(centre, u, v, radius, TIE_ARC[1]);
    let down = frame.vector([1., 0., 0.]);
    let axis = frame.vector([0., 0., 1.]);
    let line_origin = add(centre, mul(down, data.tie_route_down));
    let (west_x, east_x) = (data.stock_min[0] - TIE_FLANK_AIR, data.stock_max[0] + TIE_FLANK_AIR);
    let at_x = |x: f64| {
        let t = (x - line_origin[0]) / u[0];
        add(line_origin, mul(u, t))
    };
    let (west_lower, east_lower) = (at_x(west_x), at_x(east_x));
    let west_upper = [west_x, centre[1], (centre[2] + TIE_CROWN_RISE).max(upper[2] + TIE_ARC_CLEAR)];
    let [first, last] = TIE_ARC;
    let middle = arc_point(centre, u, v, radius, (first + last) / 2.);
    vec![
        TieRun::Arc { points: [lower, middle, upper], radius, sweep_degrees: last - first, wide_axis: cross(u, v) },
        TieRun::Line { points: [upper, west_upper], wide_axis: axis },
        TieRun::Line { points: [west_upper, west_lower], wide_axis: axis },
        TieRun::Line { points: [west_lower, east_lower], wide_axis: axis },
        TieRun::Line { points: [east_lower, lower], wide_axis: axis },
    ]
}

/// A tie route's length along its runs.
pub fn tie_length(runs: &[TieRun]) -> f64 {
    runs.iter().map(TieRun::length).sum()
}
