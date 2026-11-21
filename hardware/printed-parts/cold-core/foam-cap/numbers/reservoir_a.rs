//! Reservoir A's two anchors on the lid, where its fill and draw lines run over the lid: the fore
//! pair of integral C2 seats the lines snap down into, their lower halves on one broad filled
//! base, and the aft pair of the same seats, each turned along its line's last level turn before
//! the line leaves for the reservoir, as reservoir A's routes
//! (`hardware/manifold-layout/reservoir-a-routes.json`) lay them.
use crate::P3;
use crate::clips::TIP_DEGREES;
use crate::design::{Run as Written, reservoir_routes};
use crate::vector::{add, cross, mul, radians, sub, unit};
use hsm_cold_core_layout::cap::cap_face_z;
use std::collections::BTreeMap;
use std::sync::OnceLock;

/// The lines' stock, and the axis they run along at the anchors.
pub const TUBE_OD: f64 = 6.35;
pub const TUBE_AXIS: P3 = [0., 1., 0.];

/// The fore pair: the two seats' midpoint, their pitch, the C2 bore and jaw section, the seats'
/// span along the lines and the base's floor under the lid's face.
pub mod pair {
    use crate::P3;
    pub const CENTRE: P3 = [57.25, 209.75, 258.5];
    pub const PITCH: f64 = 13.5;
    pub const BORE: f64 = 6.35;
    pub const WING: f64 = 2.4;
    pub const TIP_DEGREES: f64 = super::TIP_DEGREES;
    pub const SPAN: f64 = 8.;
    pub const FLOOR: f64 = 3.;
}

/// The fore pair's seats and base.
#[derive(Clone, Copy, Debug)]
pub struct Pair {
    pub tube_centres: [P3; 2],
    pub seat_radius: f64,
    pub outer_radius: f64,
    /// The base: one full-span block under both seats, rooted a floor into the lid, up to the
    /// seats' axis.
    pub base: [P3; 2],
    /// The pair's whole body, its jaws' tips included.
    pub body: [P3; 2],
}

pub fn pair() -> Pair {
    let radius = pair::BORE / 2.;
    let outer = radius + pair::WING;
    let [x, y, z] = pair::CENTRE;
    let tube_centres = [-1., 1.].map(|side: f64| [x + side * pair::PITCH / 2., y, z]);
    let low = [tube_centres[0][0] - outer, y - pair::SPAN / 2., cap_face_z() - pair::FLOOR];
    let high = [tube_centres[1][0] + outer, y + pair::SPAN / 2., z];
    let nose = pair::WING / 2.;
    let middle = radius + nose;
    let tip = z - middle * radians(pair::TIP_DEGREES).cos() + nose;
    Pair {
        tube_centres,
        seat_radius: radius,
        outer_radius: outer,
        base: [low, high],
        body: [low, [high[0], high[1], tip]],
    }
}

/// The aft pair: the lines it holds west to east, and a plane across the lid that both lines'
/// last level turns cross. Its seats are the fore pair's, bore, jaws and span. The lower seat's
/// jaw on the higher seat's side is filled square and joined to that root where the two meet, so
/// it bends little. Its free jaw takes the fit of a seat with one fixed jaw, as back-top's
/// east-wall fill seat has it: the free jaw's thickness, and how far it and its half of the bore
/// stand out from the stiff jaw.
pub mod aft {
    pub const ROUTES_WEST_TO_EAST: [&str; 2] = ["fluid-16", "fluid-14"];
    pub const WORLD_Y: f64 = 390.5;
    pub const FREE_WING: f64 = 2.35;
    pub const FREE_SHIFT: f64 = 0.15;
}

/// A run of a route: straight between two points, or a circular turn through three points about
/// its centre and axis through its angle.
#[derive(Clone, Copy, Debug)]
pub enum Run {
    Line { points: [P3; 2] },
    Arc { points: [P3; 3], centre: P3, axis: P3, angle: f64, radius: f64 },
}

/// Reservoir A's routes by name, from where each starts, each arc's centre worked from its start
/// and turn, its middle point halfway round.
pub fn routes() -> &'static BTreeMap<String, Vec<Run>> {
    static ROUTES: OnceLock<BTreeMap<String, Vec<Run>>> = OnceLock::new();
    ROUTES.get_or_init(|| {
        let mut out = BTreeMap::new();
        for (name, path) in &reservoir_routes().paths {
            let mut runs: Vec<Run> = path
                .segments
                .iter()
                .map(|written| match *written {
                    Written::Line { points_mm } => Run::Line { points: points_mm },
                    Written::Arc { start_mm, center_mm, axis, angle_rad, radius_mm, end_mm } => {
                        let tangent = unit(cross(axis, sub(start_mm, center_mm)));
                        let centre = add(start_mm, mul(cross(axis, tangent), radius_mm));
                        let radial = sub(start_mm, centre);
                        let half = angle_rad / 2.;
                        let middle =
                            add(centre, add(mul(radial, half.cos()), mul(cross(axis, radial), half.sin())));
                        Run::Arc { points: [start_mm, middle, end_mm], centre, axis, angle: angle_rad, radius: radius_mm }
                    }
                })
                .collect();
            if path.reverse {
                runs.reverse();
                for run in &mut runs {
                    match run {
                        Run::Line { points } => points.reverse(),
                        Run::Arc { points, axis, .. } => {
                            points.reverse();
                            *axis = mul(*axis, -1.);
                        }
                    }
                }
            }
            out.insert(name.clone(), runs);
        }
        out
    })
}

/// One aft seat: the level turn its line makes there about the upright axis through `centre`,
/// the line's centre where the seat starts and where the turn and the seat end, and the turn
/// between them.
#[derive(Clone, Copy, Debug)]
pub struct AftSeat {
    pub centre: P3,
    pub start: P3,
    pub end: P3,
    pub degrees: f64,
    /// The side the lower seat is filled square on, up to its jaw's top, where the higher seat's
    /// root stands against it: away from the turn's centre when true, toward it when false.
    pub shoulder_outward: Option<bool>,
}

impl AftSeat {
    pub fn radius(&self) -> f64 {
        let v = sub(self.start, self.centre);
        v[0].hypot(v[1])
    }

    /// How far the seat reaches across its line, toward its turn's centre and away from it: a
    /// jaw's thickness beyond the bore, and a free jaw's stand-out opposite a fixed one.
    pub fn reaches(&self) -> [f64; 2] {
        let jaw = pair::BORE / 2. + pair::WING;
        let free = pair::BORE / 2. + aft::FREE_WING + aft::FREE_SHIFT;
        match self.shoulder_outward {
            Some(true) => [free, jaw],
            Some(false) => [jaw, free],
            None => [jaw, jaw],
        }
    }

    /// The seat's footprint on the lid: its low and high corners across X and Y.
    pub fn footprint(&self) -> [[f64; 2]; 2] {
        let [toward, away] = self.reaches();
        let outer = self.radius() + away;
        let inner = self.radius() - toward;
        let (mut low, mut high) = ([f64::INFINITY; 2], [f64::NEG_INFINITY; 2]);
        for end in [self.start, self.end] {
            let out = unit(sub(end, self.centre));
            for reach in [inner, outer] {
                for axis in 0..2 {
                    let at = self.centre[axis] + out[axis] * reach;
                    low[axis] = low[axis].min(at);
                    high[axis] = high[axis].max(at);
                }
            }
        }
        [low, high]
    }
}

/// The aft pair's seats, west to east. Each runs the seats' span back along its line's level turn
/// from where that turn ends at the aft.
pub fn aft_seats() -> [AftSeat; 2] {
    let turn = |name: &str| {
        let level = routes()[name].iter().find_map(|run| match *run {
            Run::Arc { points: [first, _, last], centre, axis, radius, .. }
                if axis[2].abs() > 1. - 1.0e-9 && first[1].min(last[1]) <= aft::WORLD_Y && aft::WORLD_Y <= first[1].max(last[1]) =>
            {
                Some((first, last, centre, radius))
            }
            _ => None,
        });
        let (first, last, centre, radius) = level.unwrap_or_else(|| panic!("{name} makes no level turn across Y {}", aft::WORLD_Y));
        let (end, other) = if last[1] > first[1] { (last, first) } else { (first, last) };
        let (from, toward) = (sub(end, centre), sub(other, centre));
        let back = (pair::SPAN / radius).copysign(from[0] * toward[1] - from[1] * toward[0]);
        let start = [
            centre[0] + from[0] * back.cos() - from[1] * back.sin(),
            centre[1] + from[0] * back.sin() + from[1] * back.cos(),
            end[2],
        ];
        AftSeat { centre, start, end, degrees: (pair::SPAN / radius).to_degrees(), shoulder_outward: None }
    };
    let mut seats = aft::ROUTES_WEST_TO_EAST.map(turn);
    let (low, high) = if seats[0].end[2] < seats[1].end[2] { (0, 1) } else { (1, 0) };
    if seats[low].end[2] < seats[high].end[2] {
        let away = sub(seats[low].end, seats[low].centre);
        let across = sub(seats[high].end, seats[low].end);
        seats[low].shoulder_outward = Some(away[0] * across[0] + away[1] * across[1] > 0.);
    }
    seats
}

/// The aft pair's whole body with the floor of lid under it: its low and high corners.
pub fn aft_body() -> [P3; 2] {
    let seats = aft_seats();
    let nose = pair::WING / 2.;
    let top = seats.iter().map(|s| s.end[2] - (pair::BORE / 2. + nose) * radians(pair::TIP_DEGREES).cos() + nose).fold(f64::NEG_INFINITY, f64::max);
    let (mut low, mut high) = ([f64::INFINITY, f64::INFINITY, cap_face_z() - pair::FLOOR], [f64::NEG_INFINITY, f64::NEG_INFINITY, top]);
    for seat in seats {
        let [a, b] = seat.footprint();
        for axis in 0..2 {
            low[axis] = low[axis].min(a[axis]);
            high[axis] = high[axis].max(b[axis]);
        }
    }
    [low, high]
}
