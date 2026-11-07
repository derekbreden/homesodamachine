//! Reservoir A's two anchors on the lid, where its fill and draw lines run over the lid: the fore
//! pair of integral C2 seats the lines snap down into, their lower halves on one broad filled
//! base, and the aft pair of open seats on one filled stepped saddle, whose through-slot takes the
//! tie that holds both lines down. The aft seats follow the lines where they cross the saddle, as
//! reservoir A's routes (`hardware/manifold-layout/reservoir-a-routes.json`) lay them.
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

/// The aft pair: where it stands along Y, its span, the lines it holds west to east, and its
/// seats' lip below each line's axis; the saddle's root under the lid's face and its flank past
/// the seats' swept clearance; the seats' bore and the stock under it; the tie's slot across Y,
/// its floor, and the stock the saddle keeps west and east of the lines.
pub mod aft {
    pub const WORLD_Y: f64 = 390.5;
    pub const STATION_LENGTH: f64 = 9.2;
    pub const ROUTES_WEST_TO_EAST: [&str; 2] = ["fluid-16", "fluid-14"];
    pub const SEAT_LIP_BELOW_AXIS: f64 = 1.2;
    pub const ROOT_Z: f64 = 248.;
    pub const FLANK: f64 = 3.;
    pub const SEAT_RADIUS: f64 = 3.325;
    pub const SEAT_FLOOR_STOCK: f64 = 3.;
    pub const TIE_SLOT_WIDTH_Y: f64 = 3.2;
    pub const TIE_SLOT_BOTTOM_Z: f64 = 251.6;
    pub const STOCK_WEST_OF_FIRST_TUBE: f64 = 6.325;
    pub const STOCK_EAST_OF_LAST_TUBE: f64 = 6.325;
    /// The tie's access mouths run this far over the saddle's top.
    pub const MOUTH_OVERRUN: f64 = 0.1;
    /// The stations along the span each seat's clearance is swept at.
    pub const SAMPLES: usize = 64;
    /// The nominal tie strip the slot is laid out for: its section, the outer radius it bends
    /// round each line at, its lower run's centre height, and the turn into that run.
    pub const TIE_WIDTH: f64 = 2.5;
    pub const TIE_THICKNESS: f64 = 0.8;
    pub const TIE_OUTER_BEND_RADIUS: f64 = 3.75;
    pub const TIE_BOTTOM_CENTRE_Z: f64 = 252.4;
    pub const TIE_TURN: f64 = 1.5;
}

/// A run of a route as the cap sweeps a seat's clearance along it and finds where it crosses a
/// station: straight between two points, or a circular turn through three points about its centre
/// and axis through its angle.
#[derive(Clone, Copy, Debug)]
pub enum Run {
    Line { points: [P3; 2] },
    Arc { points: [P3; 3], centre: P3, axis: P3, angle: f64, radius: f64 },
}

impl Run {
    pub fn first(&self) -> P3 {
        match self {
            Run::Line { points } => points[0],
            Run::Arc { points, .. } => points[0],
        }
    }

    pub fn last(&self) -> P3 {
        match self {
            Run::Line { points } => points[1],
            Run::Arc { points, .. } => points[2],
        }
    }
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

/// Where route `name`'s centreline crosses the plane at `y`, and its direction there: the first
/// run that spans it, an arc's crossing found by halving its turn.
pub fn station(name: &str, y: f64) -> (P3, P3) {
    for run in &routes()[name] {
        let (first, last) = (run.first(), run.last());
        if !(first[1].min(last[1]) - 1.0e-8 <= y && y <= first[1].max(last[1]) + 1.0e-8) {
            continue;
        }
        match *run {
            Run::Line { points: [a, b] } => {
                if (b[1] - a[1]).abs() < 1.0e-9 {
                    continue;
                }
                let t = (y - a[1]) / (b[1] - a[1]);
                return (add(a, mul(sub(b, a), t)), unit(sub(b, a)));
            }
            Run::Arc { centre, axis, angle, .. } => {
                let radial = sub(first, centre);
                let sideways = cross(axis, radial);
                let point = |t: f64| add(centre, add(mul(radial, t.cos()), mul(sideways, t.sin())));
                let (mut lo, mut hi) = (0., angle);
                let increasing = last[1] > first[1];
                for _ in 0..48 {
                    let mid = (lo + hi) / 2.;
                    if (point(mid)[1] < y) == increasing {
                        lo = mid;
                    } else {
                        hi = mid;
                    }
                }
                let at = point((lo + hi) / 2.);
                return (at, unit(cross(axis, sub(at, centre))));
            }
        }
    }
    panic!("{name} crosses no station at Y {y}")
}

/// The aft pair's saddle, seats, slot and the tie's access mouths, in the enclosure.
#[derive(Clone, Copy, Debug)]
pub struct AftSeat {
    /// Where each line crosses the anchor's plane, and how it runs there, west to east; the
    /// nominal crossings the anchor's plane is read off.
    pub tube_centres: [P3; 2],
    pub tube_axes: [P3; 2],
    pub nominal_tube_centres: [P3; 2],
    /// The saddle's stock, and its roof across X and Z: high over the west line, stepping down
    /// over the east.
    pub stock: [P3; 2],
    pub seat_roof: [[f64; 2]; 4],
    /// The tie's through-slot under the seats, and the two mouths it is threaded through.
    pub tie_slot: [P3; 2],
    pub access: [[P3; 2]; 2],
}

pub fn aft_seat() -> AftSeat {
    use aft::*;
    let nominal = ROUTES_WEST_TO_EAST.map(|route| station(route, WORLD_Y).0);
    let tie_slot_top = nominal.iter().map(|p| p[2]).fold(f64::INFINITY, f64::min) - SEAT_RADIUS - SEAT_FLOOR_STOCK;
    let [first, last] = nominal;
    let (x0, x1, y) = (first[0], last[0], first[1]);
    let half = STATION_LENGTH / 2.;
    let slot_half = TIE_SLOT_WIDTH_Y / 2.;
    let held = ROUTES_WEST_TO_EAST.map(|route| station(route, y));
    let lanes = ROUTES_WEST_TO_EAST.map(|route| {
        (0..=SAMPLES).map(|i| station(route, y - half + (i * 2) as f64 * half / SAMPLES as f64)).collect::<Vec<_>>()
    });
    let edges = lanes.each_ref().map(|lane| {
        let west = lane.iter().map(|(p, u)| p[0] - SEAT_RADIUS / u[1].abs()).fold(f64::INFINITY, f64::min);
        let east = lane.iter().map(|(p, u)| p[0] + SEAT_RADIUS / u[1].abs()).fold(f64::NEG_INFINITY, f64::max);
        [west, east]
    });
    let tops = lanes.each_ref().map(|lane| {
        lane.iter().map(|(p, _)| p[2]).fold(f64::INFINITY, f64::min) - SEAT_LIP_BELOW_AXIS
    });
    let top = tops[0].max(tops[1]);
    let (west_edge, east_edge) = (edges[0][0] - FLANK, edges[1][1] + FLANK);
    // The roof crosses both curved clearance bores with one broad step; ending it at their swept
    // extremes would leave vanishing tips.
    let reach = SEAT_FLOOR_STOCK;
    AftSeat {
        tube_centres: held.map(|(p, _)| p),
        tube_axes: held.map(|(_, u)| u),
        nominal_tube_centres: nominal,
        stock: [[west_edge, y - half, ROOT_Z], [east_edge, y + half, top]],
        seat_roof: [
            [west_edge, tops[0]],
            [edges[0][1] - reach, tops[0]],
            [edges[1][0] + reach, tops[1]],
            [east_edge, tops[1]],
        ],
        tie_slot: [[west_edge, y - slot_half, TIE_SLOT_BOTTOM_Z], [east_edge, y + slot_half, tie_slot_top]],
        access: [
            [[west_edge, y - slot_half, TIE_SLOT_BOTTOM_Z], [x0, y + slot_half, top + MOUTH_OVERRUN]],
            [[x1, y - slot_half, TIE_SLOT_BOTTOM_Z], [east_edge, y + slot_half, top + MOUTH_OVERRUN]],
        ],
    }
}

/// The aft tie's closed nominal centreline across X and Z: round over each line at the strip's
/// outer bend and down under the slot's floor, without its loose tail.
pub fn aft_tie_witness() -> Vec<[f64; 2]> {
    use aft::*;
    let seat = aft_seat();
    let [first, last] = seat.tube_centres;
    let (x0, x1, z) = (first[0], last[0], first[2]);
    let (radius, bottom, turn) = (TIE_OUTER_BEND_RADIUS, TIE_BOTTOM_CENTRE_Z, TIE_TURN);
    let pi = std::f64::consts::PI;
    let mut points = vec![];
    let mut arc = |x: f64, zz: f64, r: f64, start: f64, end: f64| {
        for i in 0..13 {
            let angle = start + (end - start) * i as f64 / 12.;
            points.push([x + r * angle.cos(), zz + r * angle.sin()]);
        }
    };
    let tangent = (last[2] - first[2]).atan2(x1 - x0) + pi / 2.;
    arc(x0, z, radius, pi, tangent);
    arc(x1, last[2], radius, tangent, 0.);
    arc(x1 + radius - turn, bottom + turn, turn, 0., -pi / 2.);
    arc(x0 - radius + turn, bottom + turn, turn, -pi / 2., -pi);
    points
}
