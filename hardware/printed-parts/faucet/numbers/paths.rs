//! The tubes' centrelines through the faucet, in millimetres: X lateral, Y toward the appliance's
//! back, Z up. Below the bend the soda tube stands on the Westbrass's water port and the flavor
//! pair, the drain and the cable ease in onto it from where the mounting stack holds them; up the
//! bend every centreline keeps a fixed offset from the water's; past the split joint they converge
//! onto the dispense face. A station `s` is the distance along the water's centreline from the
//! split joint.

use crate::P3;
use std::f64::consts::PI;

/// The water's centreline in Y, on the Westbrass's water port.
pub const WATER_Y: f64 = 8.875;
/// The 3/8" soda tube's outside diameter.
pub const WATER_OD: f64 = 9.525;
/// The flavor tubes' outside diameter.
pub const FLAVOR_OD: f64 = 4.0;
/// The flavor tubes' bore.
pub const FLAVOR_ID: f64 = 2.5;
/// The tightest bend a flavor tube takes.
pub const FLAVOR_MIN_BEND: f64 = 25.0;
/// The drain tube's outside diameter.
pub const DRAIN_OD: f64 = 4.0;
/// The drain tube's bore.
pub const DRAIN_ID: f64 = 2.5;
/// Each flavor tube's offset in X where the mounting stack holds them.
pub const LOWER_FLAVOR_X: f64 = 5.45;
/// The bundle's mounting centre in X.
pub const LOWER_BUNDLE_X: f64 = 0.0;
/// The flavor pair's Y in the mounting stack.
pub const LOWER_Y: f64 = 18.925;
/// The drain's Y in the mounting stack.
pub const LOWER_DRAIN_Y: f64 = 18.525;
/// The cable's Y in the mounting stack.
pub const LOWER_RIBBON_Y: f64 = 21.4875;
/// The signal cable's width, by caliper (`reference/bntechgo-signal-ribbon/physical-observations.json`).
pub const RIBBON_WIDTH: f64 = 4.6;
/// The signal cable's thickness, by caliper.
pub const RIBBON_DEPTH: f64 = 1.18;
/// Where the tubes start easing in from the mounting stack.
pub const LOWER_START_Z: f64 = 40.0;
/// Where they have closed onto the soda tube.
pub const LOWER_END_Z: f64 = 67.5;
/// How far the flavor pair bows out on the way in.
pub const LOWER_FLAVOR_FLARE: f64 = 0.10;
/// The dispense outlet, where the water's centreline leaves the tip.
pub const OUTLET_Y: f64 = -133.99672200476698;
pub const OUTLET_Z: f64 = 180.38874339162197;
/// The gooseneck's whole turn.
pub const TOTAL_ANGLE: f64 = 140.0 * PI / 180.0;
/// The straight tip beyond the bend.
pub const TIP_LENGTH: f64 = 25.0;
/// The split joint's angle round the bend.
pub const JOINT_ANGLE: f64 = 70.0 * PI / 180.0;
/// The tube shell's centre, out along the bend's normal from the water's centreline.
pub const SHELL_CENTER_N: f64 = 4.027512922;
/// The tube shell's outer radius.
pub const SHELL_RADIUS: f64 = 13.5;
/// The vent cavity's radius about the shell's centre.
pub const CAVITY_RADIUS: f64 = 11.5;
/// The web the seal leaves between neighbouring tubes.
pub const SEAL_WEB: f64 = 0.8;
/// The cable's offset along the normal, packed tight to the tubes.
pub const TIGHT_RIBBON_N: f64 = 9.75;
/// The cable's offset through the vent seals.
pub const SEAL_RIBBON_N: f64 = 11.0125;
/// The cable's offset at the dispense face.
pub const FACE_RIBBON_N: f64 = 11.55;
/// Where the packed tubes finish spreading.
pub const SPREAD_END_S: f64 = 14.0;
/// The upstream vent gland's station.
pub const UPSTREAM_GLAND_S: f64 = 30.0;
/// The downstream vent gland's station.
pub const DOWNSTREAM_GLAND_S: f64 = 59.3;
/// A gland's length along the bend.
pub const GLAND_LENGTH: f64 = 7.3;
/// The gland body's mid-height.
pub const GLAND_BODY_MID_Z: f64 = 4.1;
/// The angle round the bend where the drain is cut square.
pub const DRAIN_END_ANGLE: f64 = 80.68709001137978 * PI / 180.0;
/// How long the flavor pair takes to converge onto the face.
pub const CONVERGE_LENGTH: f64 = 24.0;
/// How long the cable takes to converge.
pub const RIBBON_CONVERGE_LENGTH: f64 = 8.0;
/// The vent port's length along the bend.
pub const PORT_LENGTH_S: f64 = 22.0;
/// The vent port's width.
pub const PORT_WIDTH: f64 = 12.0;
/// The vent port's corner radius.
pub const PORT_CORNER_R: f64 = 2.0;
/// Where the drip pocket opens.
pub const DRIP_POCKET_ENTRY_S: f64 = 30.0;
/// Where the drip pocket closes.
pub const DRIP_POCKET_EXIT_S: f64 = 59.3;
/// The drip guide's wall.
pub const DRIP_GUIDE_WALL_THICKNESS: f64 = 2.0;
/// The drip hole under the bend.
pub const DRIP_HOLE_DIAMETER: f64 = 4.0;
/// The drip hole's angle round the bend.
pub const DRIP_HOLE_ANGLE: f64 = 75.72139663878282 * PI / 180.0;
/// What the drain's square end clears.
pub const DRIP_END_CLEARANCE_MM: f64 = 3.0;

/// The bend's radius at the water's centreline.
pub fn water_radius() -> f64 {
    (WATER_Y - OUTLET_Y - TIP_LENGTH * TOTAL_ANGLE.sin()) / (1.0 - TOTAL_ANGLE.cos())
}

/// Where the bend starts, in Z.
pub fn arc_start_z() -> f64 {
    OUTLET_Z - water_radius() * TOTAL_ANGLE.sin() - TIP_LENGTH * TOTAL_ANGLE.cos()
}

/// Water to flavor, centre to centre, packed.
fn rf() -> f64 {
    (WATER_OD + FLAVOR_OD) / 2.0
}

/// Drain to flavor, centre to centre, packed.
fn rd() -> f64 {
    (DRAIN_OD + FLAVOR_OD) / 2.0
}

/// The drain's offset along the normal, packed on the water.
pub fn tight_drain_n() -> f64 {
    (WATER_OD + DRAIN_OD) / 2.0
}

/// The flavor pair's offset along the normal, packed on the water and the drain.
pub fn tight_flavor_n() -> f64 {
    (rf().powi(2) - rd().powi(2) + tight_drain_n().powi(2)) / (2.0 * tight_drain_n())
}

/// The flavor pair's offset in X, packed.
pub fn tight_flavor_x() -> f64 {
    (rf().powi(2) - tight_flavor_n().powi(2)).sqrt()
}

/// The flavor pair's offset in X at the dispense face.
pub fn face_flavor_x() -> f64 {
    FLAVOR_OD / 2.0
}

/// The flavor pair's offset along the normal at the dispense face.
pub fn face_flavor_n() -> f64 {
    (rf().powi(2) - face_flavor_x().powi(2)).sqrt()
}

/// How far a gland's mid-height shifts its station.
pub fn gland_mid_shift_s() -> f64 {
    GLAND_BODY_MID_Z * water_radius() / (water_radius() + SHELL_CENTER_N)
}

/// The vent cavity's floor radius about the bend's centre.
fn floor_radius() -> f64 {
    water_radius() + SHELL_CENTER_N - CAVITY_RADIUS
}

/// Where the vent's wet region starts.
pub fn wet_start_s() -> f64 {
    UPSTREAM_GLAND_S + gland_mid_shift_s() + water_radius() * ((GLAND_LENGTH - GLAND_BODY_MID_Z) / floor_radius()).asin()
}

/// Where the drain is cut square.
pub fn drain_cut_s() -> f64 {
    (DRAIN_END_ANGLE - JOINT_ANGLE) * water_radius()
}

/// Where the flavor pair starts converging onto the face.
pub fn converge_start_s() -> f64 {
    drain_cut_s() + 3.0
}

/// The drip hole's station.
pub fn drip_hole_s() -> f64 {
    (DRIP_HOLE_ANGLE - JOINT_ANGLE) * water_radius()
}

/// Smoothstep of the fifth order, clamped to [0, 1].
pub fn ease(t: f64) -> f64 {
    let t = t.clamp(0.0, 1.0);
    t * t * t * (10.0 + t * (-15.0 + 6.0 * t))
}

/// Below the bend at height `z`: the flavor pair's X offset, and its and the drain's Y from the
/// water's centreline.
pub fn lower_positions(z: f64) -> [f64; 3] {
    let u = ease((z - LOWER_START_Z) / (LOWER_END_Z - LOWER_START_Z));
    let flare = LOWER_FLAVOR_FLARE * 4.0 * u * (1.0 - u);
    [
        LOWER_FLAVOR_X + (tight_flavor_x() - LOWER_FLAVOR_X) * u + flare,
        LOWER_Y - WATER_Y + (tight_flavor_n() - (LOWER_Y - WATER_Y)) * u,
        LOWER_DRAIN_Y - WATER_Y + (tight_drain_n() - (LOWER_DRAIN_Y - WATER_Y)) * u,
    ]
}

/// The bundle's centre in X at height `z`.
pub fn lower_bundle_x(z: f64) -> f64 {
    LOWER_BUNDLE_X * (1.0 - ease((z - LOWER_START_Z) / (LOWER_END_Z - LOWER_START_Z)))
}

/// The cable's Y at height `z`.
pub fn lower_ribbon_y(z: f64) -> f64 {
    let u = ease((z - LOWER_START_Z) / (LOWER_END_Z - LOWER_START_Z));
    LOWER_RIBBON_Y + (WATER_Y + TIGHT_RIBBON_N - LOWER_RIBBON_Y) * u
}

/// What runs beside the water up the faucet.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Kind {
    Flavor,
    Drain,
    Ribbon,
}

/// A centreline's point below the bend at height `z`; `sign` picks the flavor tube's side.
pub fn lower_point(z: f64, kind: Kind, sign: f64) -> P3 {
    let [x, f, d] = lower_positions(z);
    let y = match kind {
        Kind::Ribbon => lower_ribbon_y(z),
        Kind::Flavor => WATER_Y + f,
        Kind::Drain => WATER_Y + d,
    };
    [lower_bundle_x(z) + if kind == Kind::Flavor { sign * x } else { 0.0 }, y, z]
}

/// At station `s`: the flavor pair's X offset and normal offset, the drain's and the cable's
/// normal offsets, and the cable's width.
pub fn positions(s: f64) -> [f64; 5] {
    let u = ease((s - converge_start_s()) / CONVERGE_LENGTH);
    let a0 = tight_flavor_x().atan2(tight_flavor_n());
    let a1 = face_flavor_x().atan2(face_flavor_n());
    let angle = a0 + (a1 - a0) * u;
    let cable_u = ease((s - converge_start_s()) / RIBBON_CONVERGE_LENGTH);
    [
        rf() * angle.sin(),
        rf() * angle.cos(),
        tight_drain_n(),
        TIGHT_RIBBON_N + (FACE_RIBBON_N - TIGHT_RIBBON_N) * cable_u,
        RIBBON_WIDTH,
    ]
}

/// The point `angle` round the bend, `x` across it and `n` out along its normal.
pub fn arc_point(angle: f64, x: f64, n: f64) -> P3 {
    [x, WATER_Y - water_radius() + (water_radius() + n) * angle.cos(), arc_start_z() + (water_radius() + n) * angle.sin()]
}

/// The point at station `s`, `x` across and `n` out.
pub fn station_point(s: f64, x: f64, n: f64) -> P3 {
    arc_point(JOINT_ANGLE + s / water_radius(), x, n)
}

/// The section plane at station `s`, about the point `center_n` out: origin, x direction and
/// normal along the bend.
pub fn station_plane(s: f64, center_n: f64) -> [P3; 3] {
    let a = JOINT_ANGLE + s / water_radius();
    [station_point(s, 0.0, center_n), [1.0, 0.0, 0.0], [0.0, -a.sin(), a.cos()]]
}

/// A tube's centreline at station `s`.
pub fn tube_arc_point(s: f64, kind: Kind, sign: f64) -> P3 {
    let [x, f, d, ribbon, _] = positions(s);
    let n = match kind {
        Kind::Flavor => f,
        Kind::Drain => d,
        Kind::Ribbon => ribbon,
    };
    station_point(s, if kind == Kind::Flavor { sign * x } else { 0.0 }, n)
}

/// One run of a centreline, each from where the last one ends.
#[derive(Clone, Debug, PartialEq)]
pub enum Leg {
    Line(P3, P3),
    /// From the first point through the second to the third.
    Arc(P3, P3, P3),
    /// Through every point.
    Spline(Vec<P3>),
    /// From the first point to the second, leaving along the third and arriving along the fourth.
    Hermite(P3, P3, P3, P3),
}

impl Leg {
    pub fn start(&self) -> P3 {
        match self {
            Leg::Line(a, _) | Leg::Arc(a, _, _) | Leg::Hermite(a, _, _, _) => *a,
            Leg::Spline(p) => p[0],
        }
    }

    pub fn end(&self) -> P3 {
        match self {
            Leg::Line(_, b) | Leg::Arc(_, _, b) | Leg::Hermite(_, b, _, _) => *b,
            Leg::Spline(p) => *p.last().expect("a spline through points"),
        }
    }
}

fn line(legs: &mut Vec<Leg>, a: P3, b: P3) {
    // Only coincident ends are left out.
    if (a[0] - b[0]).hypot(a[1] - b[1]).hypot(a[2] - b[2]) > 1e-7 {
        legs.push(Leg::Line(a, b));
    }
}

fn spline(legs: &mut Vec<Leg>, point: impl Fn(f64) -> P3, a: f64, b: f64) {
    let count = (((b - a) / 0.4).ceil() as usize).max(16);
    legs.push(Leg::Spline((0..=count).map(|i| point(a + (b - a) * i as f64 / count as f64)).collect()));
}

fn constant_arc(legs: &mut Vec<Leg>, a: f64, b: f64, x: f64, n: f64) {
    if b - a > 1e-9 {
        legs.push(Leg::Arc(arc_point(a, x, n), arc_point((a + b) / 2.0, x, n), arc_point(b, x, n)));
    }
}

/// A tube's centreline from `bottom_z` below the mounting stack up through the faucet, to
/// station `end_s` or, with none, out through the tip. The drain stops where it is cut square.
pub fn path_legs(kind: Kind, bottom_z: f64, sign: f64, end_s: Option<f64>) -> Vec<Leg> {
    let mut legs = vec![];
    let lower = |z| lower_point(z, kind, sign);
    let start = lower(LOWER_START_Z);
    line(&mut legs, [start[0], start[1], bottom_z], start);
    spline(&mut legs, lower, LOWER_START_Z, LOWER_END_Z);
    let ty = lower(LOWER_END_Z)[1];
    let mut nx = if kind == Kind::Flavor { sign * tight_flavor_x() } else { 0.0 };
    let mut nn = match kind {
        Kind::Flavor => tight_flavor_n(),
        Kind::Drain => tight_drain_n(),
        Kind::Ribbon => TIGHT_RIBBON_N,
    };
    line(&mut legs, lower(LOWER_END_Z), [nx, ty, arc_start_z()]);
    constant_arc(&mut legs, 0.0, JOINT_ANGLE, nx, nn);
    let end_s = if kind == Kind::Drain { end_s.or_else(|| Some(drain_cut_s())) } else { end_s };
    let joint_to = |s: f64| JOINT_ANGLE + s / water_radius();
    match end_s {
        Some(end) if end <= converge_start_s() => constant_arc(&mut legs, JOINT_ANGLE, joint_to(end), nx, nn),
        Some(end) => {
            constant_arc(&mut legs, JOINT_ANGLE, joint_to(converge_start_s()), nx, nn);
            spline(&mut legs, |s| tube_arc_point(s, kind, sign), converge_start_s(), end);
        }
        None => {
            constant_arc(&mut legs, JOINT_ANGLE, joint_to(converge_start_s()), nx, nn);
            let converged = converge_start_s() + CONVERGE_LENGTH;
            spline(&mut legs, |s| tube_arc_point(s, kind, sign), converge_start_s(), converged);
            let p = positions(converged);
            (nx, nn) = if kind == Kind::Flavor { (sign * p[0], p[1]) } else { (0.0, p[3]) };
            constant_arc(&mut legs, joint_to(converged), TOTAL_ANGLE, nx, nn);
            let start = arc_point(TOTAL_ANGLE, nx, nn);
            line(
                &mut legs,
                start,
                [start[0], start[1] - TIP_LENGTH * TOTAL_ANGLE.sin(), start[2] + TIP_LENGTH * TOTAL_ANGLE.cos()],
            );
        }
    }
    legs
}
