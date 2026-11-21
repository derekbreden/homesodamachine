//! The lid's tube clips: each a C2 seat whose filled root stands on the lid's face and whose two
//! free jaws close over a tube along its axis. The V-A feed's, where the above-core design places
//! it; the two flavor lines', the crossover's root joined to V-B's wall; and reservoir A's fore
//! pair, which the pair's base joins (`reservoir_a`).
use crate::P3;
use crate::design::above_core;
use crate::reservoir_a;
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

/// The V-A feed's seat: its line on a bore of the line's own size, the jaws' section and the span.
pub const FEED_RADIUS: f64 = 6.35 / 2.;
pub const FEED_WING: f64 = 2.4;
pub const FEED_SPAN: f64 = 8.;

/// The round-ended slot across both wings of the V-B return clip.
pub const RETURN_SLOT_WIDTH: f64 = 2.;

/// The level arc the return clip shares with the tube between V-B and Y-B.
pub struct ReturnBend {
    pub centre: P3,
    pub points: [P3; 3],
    pub degrees: f64,
}

pub fn vb_return_bend() -> Result<ReturnBend> {
    above_core().fore_routes.native_segments.vb_return.iter().find_map(|run| match run {
        Segment::Arc { points_mm, center_mm: Some(c), angle_rad: Some(angle), .. } =>
            Some(ReturnBend { centre: *c, points: *points_mm, degrees: angle.to_degrees() }),
        _ => None,
    }).context("V-B's outlet route needs its lid bend")
}

impl ReturnBend {
    /// The clip's infill region, from the lid below its root to the tops of the wings.
    pub fn stock_bounds(&self) -> [P3; 2] {
        let [start, _, end] = self.points;
        let radius = reservoir_a::pair::BORE / 2.;
        let wing = reservoir_a::pair::WING;
        let outer = radius + wing;
        let tip = start[2] - (radius + wing / 2.) * TIP_DEGREES.to_radians().cos() + wing / 2.;
        [[end[0] - outer, end[1], cap_face_z() - reservoir_a::pair::FLOOR],
         [start[0], start[1] + outer, tip]]
    }
}

/// A flavor line's seat: a bore just over the flavor line's size, the jaws' section and the span.
pub const FLAVOR_RADIUS: f64 = 4.1 / 2.;
pub const FLAVOR_WING: f64 = 1.52;
pub const FLAVOR_SPAN: f64 = 8.;

/// The V-A feed's seat, where the above-core design places it.
pub fn va_feed() -> Clip {
    let snap = &above_core().fore_routes.va_feed_snap;
    Clip {
        centre: snap.centre_world_mm,
        along: snap.along_world,
        radius: FEED_RADIUS,
        wing: FEED_WING,
        span: FEED_SPAN,
        tip_degrees: TIP_DEGREES,
    }
}

/// The crossover's seat, along X beside V-B's wall; its root joins the wall.
pub fn flavor_a() -> Clip {
    Clip { centre: [26.5, 266., 296.], along: [1., 0., 0.], radius: FLAVOR_RADIUS, wing: FLAVOR_WING, span: FLAVOR_SPAN, tip_degrees: TIP_DEGREES }
}

/// The aft flavor line's seat, along Y.
pub fn flavor_b() -> Clip {
    Clip { centre: [35., 414., 264.], along: [0., 1., 0.], radius: FLAVOR_RADIUS, wing: FLAVOR_WING, span: FLAVOR_SPAN, tip_degrees: TIP_DEGREES }
}

/// Every clip on the lid: the V-A feed's, the two flavor lines', and reservoir A's fore pair.
pub fn clips() -> Vec<Clip> {
    let pair = reservoir_a::pair();
    let mut clips = vec![va_feed(), flavor_a(), flavor_b()];
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
