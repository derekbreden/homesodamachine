//! The lid's tube clips: each a C2 seat whose filled root stands on the lid's face and whose two
//! free jaws close over a tube along its axis. The water seats follow their routed bends and
//! the flavor-line seats and reservoir pair follow their mounting datums.
use crate::P3;
use crate::design::above_core;
use crate::{deck, reservoir_a};
use crate::vector::{add, cross, dot, mul, norm, sub};
use anyhow::{Context, Result};
use hsm_cold_core_layout::cap::cap_face_z;
use hsm_layout_data::Segment;

/// The accepted C2 seat's jaw tips, in degrees off its root's plane.
pub const TIP_DEGREES: f64 = 125.42102606277044;

/// A clip: its bore's centre and axis, its bore's radius, its jaws' section, its span along the
/// tube and its tips' angle.
#[derive(Clone, Copy, Debug)]
pub struct Clip {
    pub centre: P3,
    pub along: P3,
    pub radius: f64,
    pub wing: f64,
    pub span: f64,
    pub tip_degrees: f64,
}

/// The length of straight tube gripped about the V-A feed snap's placement datum.
const FEED_SPAN: f64 = 8.;
/// The space between the feed clip's outside face and the PCB.
const FEED_BOARD_CLEARANCE: f64 = 2.;

/// The round-ended slot across both lips of a split seat.
pub const WING_SLOT_WIDTH: f64 = 2.;

/// A level seat on its tube's arc, with the wing slot between the ends.
pub struct SplitBend {
    pub centre: P3,
    pub start: P3,
    pub slot: P3,
    pub end: P3,
    pub degrees: f64,
}

pub fn vb_return_bend() -> Result<SplitBend> {
    above_core().fore_routes.native_segments.vb_return.iter().find_map(|run| match run {
        Segment::Arc { points_mm, center_mm: Some(c), angle_rad: Some(angle), .. } =>
            Some(SplitBend { centre: *c, start: points_mm[0], slot: points_mm[1], end: points_mm[2], degrees: angle.to_degrees() }),
        _ => None,
    }).context("V-B's outlet route needs its lid bend")
}

/// Extends a split seat's footprint through the lid footing and up to the tips.
fn stock_bounds(lo: [f64; 2], hi: [f64; 2], tube_z: f64) -> [P3; 2] {
    use reservoir_a::pair;
    let tip = tube_z - (pair::BORE / 2. + pair::WING / 2.) * TIP_DEGREES.to_radians().cos() + pair::WING / 2.;
    [[lo[0], lo[1], cap_face_z() - pair::FLOOR], [hi[0], hi[1], tip]]
}

pub fn vb_stock_bounds() -> Result<[P3; 2]> {
    let bend = vb_return_bend()?;
    let outer = reservoir_a::pair::BORE / 2. + reservoir_a::pair::WING;
    Ok(stock_bounds([bend.end[0] - outer, bend.end[1]], [bend.start[0], bend.start[1] + outer], bend.start[2]))
}

/// Width of the pump-discharge seat along the tangent at the crown.
pub const DISCHARGE_SPAN: f64 = 6.4;

/// The vertical bend that carries pump discharge down into the lid passage.
pub struct DischargeBend {
    pub centre: P3,
    pub axis: P3,
    pub radius: f64,
}

pub fn pump_discharge() -> Result<DischargeBend> {
    let runs = &above_core().rear_plumbing.water5_bend.segments;
    let [.., Segment::Arc { center_mm: Some(centre), axis: Some(axis), radius_mm: Some(radius), .. },
        Segment::Line { .. }] = runs.as_slice() else {
        anyhow::bail!("the pump-discharge seat needs the bend leading into the lid passage");
    };
    Ok(DischargeBend { centre: *centre, axis: *axis, radius: *radius })
}

impl DischargeBend {
    pub fn stock_bounds(&self) -> [P3; 2] {
        let width = reservoir_a::pair::BORE / 2. + reservoir_a::pair::WING;
        let half = DISCHARGE_SPAN / 2.;
        let [x, y, z] = self.centre;
        let dx = self.axis[0].abs() * width + self.axis[1].abs() * half;
        let dy = self.axis[1].abs() * width + self.axis[0].abs() * half;
        stock_bounds([x - dx, y - dy], [x + dx, y + dy], z + self.radius)
    }
}

/// A flavor line's seat: a bore just over the flavor line's size, the jaws' section and the span.
pub const FLAVOR_RADIUS: f64 = 4.1 / 2.;
pub const FLAVOR_WING: f64 = 1.52;
pub const FLAVOR_SPAN: f64 = 8.;

/// The V-A seat follows the bend from the board edge and continues onto the outgoing straight.
pub struct FeedSeat {
    pub bend: SplitBend,
    pub exit: P3,
    pub stock_bounds: [P3; 2],
}

pub fn va_feed() -> Result<FeedSeat> {
    use reservoir_a::pair;
    let routes = &above_core().fore_routes;
    let snap = &routes.va_feed_snap;
    let along = snap.along_world;
    let (centre, end, radius) = routes.native_segments.va_feed.windows(2).find_map(|runs| {
        let [Segment::Arc { center_mm: Some(c), radius_mm: Some(r), .. }, Segment::Line { points_mm: [a, b] }] = runs else {
            return None;
        };
        let to_snap = sub(snap.centre_world_mm, *a);
        let distance = dot(to_snap, along);
        (norm(cross(to_snap, along)) < 1e-6 && distance >= 0. && distance <= dot(sub(*b, *a), along))
            .then_some((*c, *a, *r))
    }).context("V-A needs the level bend leading into its feed seat")?;
    let centre = [centre[0], centre[1], end[2]];
    let bore = pair::BORE / 2.;
    let outer = bore + pair::WING;
    let west = deck::board_east_x() + FEED_BOARD_CLEARANCE;
    let start_angle = -((west - centre[0]) / (radius + outer)).acos();
    let end_angle = (end[1] - centre[1]).atan2(end[0] - centre[0]);
    let sweep = end_angle - start_angle;
    let span = dot(sub(snap.centre_world_mm, end), along) + FEED_SPAN / 2.;
    let on_arc = |angle: f64| [centre[0] + radius * angle.cos(), centre[1] + radius * angle.sin(), end[2]];
    let slot = on_arc(start_angle + (sweep + span / radius) / 2.);
    let bend = SplitBend { centre, start: on_arc(start_angle), slot, end, degrees: sweep.to_degrees() };
    let exit = add(end, mul(along, span));
    let bounds = stock_bounds([west, centre[1] - radius - outer],
        [exit[0] + along[1].abs() * outer, centre[1] + (radius - outer) * start_angle.sin()], end[2]);
    Ok(FeedSeat { bend, exit, stock_bounds: bounds })
}

/// The crossover's seat, along X beside V-B's wall; its root joins the wall.
pub fn flavor_a() -> Clip {
    Clip { centre: [26.5, 266., 296.], along: [1., 0., 0.], radius: FLAVOR_RADIUS, wing: FLAVOR_WING, span: FLAVOR_SPAN, tip_degrees: TIP_DEGREES }
}

/// The aft flavor line's seat, along Y.
pub fn flavor_b() -> Clip {
    Clip { centre: [35., 414., 264.], along: [0., 1., 0.], radius: FLAVOR_RADIUS, wing: FLAVOR_WING, span: FLAVOR_SPAN, tip_degrees: TIP_DEGREES }
}

/// The straight seats with free jaws on the lid.
pub fn straight_clips() -> Vec<Clip> {
    let pair = reservoir_a::pair();
    let mut clips = vec![flavor_b()];
    clips.extend(pair.tube_centres.map(|centre| Clip {
        centre,
        along: reservoir_a::TUBE_AXIS,
        radius: pair.seat_radius,
        wing: reservoir_a::pair::WING,
        span: reservoir_a::pair::SPAN,
        tip_degrees: reservoir_a::pair::TIP_DEGREES,
    }));
    clips
}
