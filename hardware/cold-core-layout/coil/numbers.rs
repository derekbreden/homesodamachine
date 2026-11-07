//! The evaporator coil's numbers, in millimetres: the soft ACR copper tube wound on the
//! carbonator and lifted over the reed bridge, the tails that take it to the front wall, the
//! copper a carbonator takes off the roll, and the undersized helix the coil mandrel rough-forms
//! it on. They sit with the cold core's layout, which winds the coil on the carbonator and draws
//! it; the cold core's assembly, the coil's drawing, the BOM and the mandrel take them by name.
//!
//! Frame: the cold core's. +Z is the carbonator's axis, Z = 0 at the casing's base; an azimuth
//! is in degrees about +Z from +X.
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as casing;
use hsm_reed_bridge_numbers as bridge;
use std::f64::consts::PI;

// --- The copper ------------------------------------------------------------------------------

/// The copper's outside diameter, in inches and in millimetres, and its radius.
pub const TUBE_OD_IN: f64 = 0.250;
pub const TUBE_OD: f64 = TUBE_OD_IN * 25.4;
pub const TUBE_RADIUS: f64 = (TUBE_OD_IN / 2.) * 25.4;

/// The copper's stock in the routing catalog.
pub fn stock() -> catalog::Stock {
    catalog::refrigerant_stock(TUBE_OD)
}

/// The least radius the copper is bent to.
pub fn bend_floor() -> f64 {
    stock().min_bend
}

// --- The winding -----------------------------------------------------------------------------

/// The copper's centreline on the carbonator: a tube radius off its wall.
pub const WIND_RADIUS: f64 = casing::CARBONATOR_OUTER_RADIUS + TUBE_RADIUS;
/// The finished right-hand turns.
pub const WRAPS: f64 = 9.5;
/// The winding runs between the tails' heights, in the bands the carbonator's own elbows
/// leave clear below and above it.
pub const LOW_Z: f64 = casing::EVAP_TAIL_LOW_Z;
pub const HIGH_Z: f64 = casing::EVAP_TAIL_HIGH_Z;
pub const WIND_HEIGHT: f64 = HIGH_Z - LOW_Z;
pub const PITCH: f64 = WIND_HEIGHT / WRAPS;
/// The tails leave the winding on opposite tangents: the inlet's at -Y, the outlet's at +Y.
pub const INLET_AZIMUTH: f64 = -90.;
pub const OUTLET_AZIMUTH: f64 = 90.;
/// Samples per turn of the laid wrap's centreline.
pub const SAMPLES_PER_TURN: u32 = 96;

/// The point at `azimuth` degrees, `z` up, `radius` off the axis.
pub fn at(azimuth: f64, z: f64, radius: f64) -> [f64; 3] {
    let angle = azimuth.to_radians();
    [radius * angle.cos(), radius * angle.sin(), z]
}

/// A cosine ease from 0 to 1 over `t` from 0 to 1.
pub fn ease(t: f64) -> f64 {
    0.5 - 0.5 * (PI * t.clamp(0., 1.)).cos()
}

// --- The ride over the reed bridge -----------------------------------------------------------

/// How far the bridge's plateau stands the copper off the wall.
pub fn bridge_lift() -> f64 {
    bridge::plateau_radius() - casing::CARBONATOR_OUTER_RADIUS
}

/// The run the copper climbs that lift over: a cosine ramp whose sharpest bend is the copper's
/// least radius.
pub fn bridge_ramp() -> f64 {
    (bend_floor() * bridge_lift() * PI.powi(2) / 2.).sqrt()
}

/// The ramp's run round the plateau's edge, in degrees.
pub fn bridge_arc_runout() -> f64 {
    (bridge_ramp() / bridge::plateau_radius()).to_degrees()
}

/// The surface the copper rides round the azimuth, off the register azimuth, in degrees: the
/// plateau's radius out to the bridge's edge, easing down to the wall's over the arc runout.
pub fn ride_radii() -> [(f64, f64); 2] {
    let edge = bridge::bridge_half_angle().to_degrees();
    [
        (edge, bridge::plateau_radius()),
        (edge + bridge_arc_runout(), casing::CARBONATOR_OUTER_RADIUS),
    ]
}

/// The bridge's span up the casing: its ends in the carbonator's frame, raised by the floor and
/// the support ring the carbonator stands on.
pub fn bridge_z() -> [f64; 2] {
    let bottom = casing::WALL_AND_FLOOR_THICKNESS + casing::CARBONATOR_SUPPORT_RING_HEIGHT;
    [bridge::bridge_z_bottom() + bottom, bridge::bridge_z_top() + bottom]
}

/// The axial ease onto and off the bridge: its own ramp, or the copper's run, whichever is
/// longer.
pub fn bridge_axial_ramp() -> f64 {
    bridge::AXIAL_RAMP_LENGTH.max(bridge_ramp())
}

/// The copper's centreline radius at `azimuth` degrees and `z` up: the winding's, lifted over
/// the reed bridge where it crosses it.
pub fn ride_radius(azimuth: f64, z: f64) -> f64 {
    let angle = ((azimuth - casing::CARBONATOR_SENSOR_AZIMUTH + 180.).rem_euclid(360.) - 180.).abs();
    let radii = ride_radii();
    let mut surface = casing::CARBONATOR_OUTER_RADIUS;
    for (i, &(edge, radius)) in radii.iter().enumerate() {
        if angle <= edge {
            surface = if i == 0 {
                radius
            } else {
                let (low_edge, low_radius) = radii[i - 1];
                low_radius + (radius - low_radius) * ease((angle - low_edge) / (edge - low_edge))
            };
            break;
        }
    }
    let [z0, z1] = bridge_z();
    let ramp = bridge_axial_ramp();
    let axial = ease(((z - (z0 - ramp)) / ramp).min(((z1 + ramp) - z) / ramp));
    WIND_RADIUS + axial * (surface - casing::CARBONATOR_OUTER_RADIUS).max(0.)
}

/// The laid wrap's sampled centreline, inlet to outlet, lifted over the bridge. Each sample
/// stands off the true curve by the chord's sag, so the polyline's length is the copper's.
pub fn wrap_points() -> Vec<[f64; 3]> {
    let count = ((WRAPS * f64::from(SAMPLES_PER_TURN)).round_ties_even() as usize).max(2);
    let swell = 1. / (PI * WRAPS / count as f64).cos();
    (0..=count)
        .map(|i| {
            let turn = WRAPS * i as f64 / count as f64;
            let angle = INLET_AZIMUTH + 360. * turn;
            let z = LOW_Z + PITCH * turn;
            at(angle, z, ride_radius(angle, z) * swell)
        })
        .collect()
}

/// The copper in the laid wrap.
pub fn wrap_length() -> f64 {
    wrap_points().windows(2).map(|pair| distance(pair[1], pair[0])).sum()
}

/// The copper the winding takes without the bridge under it.
pub fn plain_wrap_length() -> f64 {
    WRAPS * (2. * PI * WIND_RADIUS).hypot(PITCH)
}

/// The copper the lift over the bridge adds to the plain winding.
pub fn bridge_lift_length() -> f64 {
    wrap_length() - plain_wrap_length()
}

/// The height midway between adjacent wraps nearest `target_z` at `azimuth` degrees: where a line
/// crosses the winding clear of the copper.
pub fn gap_z_near(azimuth: f64, target_z: f64) -> f64 {
    let turns = (target_z - LOW_Z) / PITCH - (azimuth - INLET_AZIMUTH) / 360.;
    let wrap_z = LOW_Z + (turns.floor() + (azimuth - INLET_AZIMUTH) / 360.) * PITCH;
    wrap_z + PITCH / 2.
}

// --- The tails -------------------------------------------------------------------------------

/// The tails: the inlet leaves the winding's bottom for the port lane, the outlet its top for
/// the west lane.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Tail {
    Inlet,
    Outlet,
}

impl Tail {
    pub const BOTH: [Tail; 2] = [Tail::Inlet, Tail::Outlet];

    pub fn name(self) -> &'static str {
        match self {
            Tail::Inlet => "inlet",
            Tail::Outlet => "outlet",
        }
    }
}

/// Every bend in a tail is formed on this radius.
pub const TAIL_BEND_RADIUS: f64 = 15.;

/// One piece of a tail's form, each tangent to the next.
#[derive(Clone, Debug)]
pub enum Segment {
    /// An arc of `degrees` on `radius`, from `start` along `tangent`, turning toward `normal`;
    /// `mid` is the arc's midpoint.
    Bend {
        id: &'static str,
        start: [f64; 3],
        end: [f64; 3],
        mid: [f64; 3],
        radius: f64,
        degrees: f64,
        tangent: [f64; 3],
        normal: [f64; 3],
    },
    /// A straight run of `length`.
    Straight { id: &'static str, start: [f64; 3], end: [f64; 3], length: f64 },
}

impl Segment {
    pub fn start(&self) -> [f64; 3] {
        match self {
            Segment::Bend { start, .. } | Segment::Straight { start, .. } => *start,
        }
    }

    pub fn end(&self) -> [f64; 3] {
        match self {
            Segment::Bend { end, .. } | Segment::Straight { end, .. } => *end,
        }
    }

    /// The copper along the segment.
    pub fn length(&self) -> f64 {
        match self {
            Segment::Bend { radius, degrees, .. } => radius * degrees.to_radians(),
            Segment::Straight { length, .. } => *length,
        }
    }
}

/// A tail's form, and where it ends and which way.
#[derive(Clone, Debug)]
pub struct TailForm {
    pub segments: Vec<Segment>,
    pub point: [f64; 3],
    pub tangent: [f64; 3],
}

impl TailForm {
    fn new(point: [f64; 3], tangent: [f64; 3]) -> Self {
        Self { segments: vec![], point, tangent: unit(tangent) }
    }

    fn bend(&mut self, normal: [f64; 3], degrees: f64, id: &'static str) {
        let normal = unit(normal);
        let angle = degrees.to_radians();
        let (start, tangent, radius) = (self.point, self.tangent, TAIL_BEND_RADIUS);
        let arc = |angle: f64| {
            add(add(start, scale(tangent, radius * angle.sin())), scale(normal, radius * (1. - angle.cos())))
        };
        let end = arc(angle);
        let mid = arc(angle / 2.);
        self.segments.push(Segment::Bend { id, start, end, mid, radius, degrees, tangent, normal });
        self.point = end;
        self.tangent = add(scale(tangent, angle.cos()), scale(normal, angle.sin()));
    }

    fn straight(&mut self, length: f64, id: &'static str) {
        if length <= 1e-8 {
            return;
        }
        let end = add(self.point, scale(self.tangent, length));
        self.segments.push(Segment::Straight { id, start: self.point, end, length });
        self.point = end;
    }
}

/// A tail's form, from the winding's tangent exit to the front wall: a roll-off that takes out
/// the pitch, a reversed pair of plan bends out to the tail's lane, then a dogleg down to the
/// copper's crossing height for the inlet, or a quarter bend at each end of a straight drop for
/// the outlet, and the straight run through the wall. With `working_tail`, the working stub runs
/// on past the wall.
pub fn tail_form(tail: Tail, working_tail: bool) -> TailForm {
    let inlet = tail == Tail::Inlet;
    let sign = if inlet { -1. } else { 1. };
    let (azimuth, z) = if inlet { (INLET_AZIMUTH, LOW_Z) } else { (OUTLET_AZIMUTH, HIGH_Z) };
    let beta = (PITCH / (2. * PI * WIND_RADIUS)).atan();
    let mut form = TailForm::new(at(azimuth, z, WIND_RADIUS), [-beta.cos(), 0., sign * beta.sin()]);
    form.bend([-beta.sin(), 0., -sign * beta.cos()], beta.to_degrees(), "B0");
    let lane_y = if inlet { casing::PORT_LANE_MID_Y } else { casing::WEST_LANE_MID_Y };
    let offset = lane_y.abs() - WIND_RADIUS;
    let angle = (1. - offset / (2. * TAIL_BEND_RADIUS)).acos();
    form.bend([0., sign, 0.], angle.to_degrees(), "B1");
    form.bend([-angle.sin(), -sign * angle.cos(), 0.], angle.to_degrees(), "B2");
    if inlet {
        let drop = form.point[2] - casing::EVAP_CROSS_Z;
        let angle = (1. - drop / (2. * TAIL_BEND_RADIUS)).acos();
        form.bend([0., 0., -1.], angle.to_degrees(), "B3");
        form.bend([-angle.sin(), 0., angle.cos()], angle.to_degrees(), "B4");
    } else {
        form.bend([0., 0., -1.], 90., "B3");
        form.straight(form.point[2] - (casing::EVAP_CROSS_Z + TAIL_BEND_RADIUS), "S1");
        form.bend([-1., 0., 0.], 90., "B4");
    }
    let exit_x = casing::FRONT_WALL_X - casing::WALL_AND_FLOOR_THICKNESS;
    form.straight(form.point[0] - exit_x, "S2");
    if working_tail {
        form.straight(stub_protrusion(tail), "WORKING TAIL");
    }
    form
}

/// The copper in a tail's form, to the front wall.
pub fn tail_length(tail: Tail) -> f64 {
    tail_form(tail, false).segments.iter().map(Segment::length).sum()
}

// --- The copper a carbonator takes -----------------------------------------------------------

/// Each tail's in-shell run as the BOM bills it, and the working stub it leaves the shell with.
pub fn tail_in_shell(tail: Tail) -> f64 {
    match tail {
        Tail::Inlet => 154.4,
        Tail::Outlet => 271.9,
    }
}

pub fn stub_protrusion(tail: Tail) -> f64 {
    match tail {
        Tail::Inlet => 200.,
        Tail::Outlet => 175.,
    }
}

/// How far a tail's drawn run may stray from the run its allowance bills.
pub const STUB_TAIL_TOLERANCE: f64 = 1.;

/// The copper cut for each tail beyond the wrap, and for both.
pub fn stub_allowance(tail: Tail) -> f64 {
    tail_in_shell(tail) + stub_protrusion(tail)
}

pub fn stub_total() -> f64 {
    stub_allowance(Tail::Inlet) + stub_allowance(Tail::Outlet)
}

/// The roll the copper comes on, in feet, and the carbonators cut from one.
pub const ROLL_LENGTH_FT: f64 = 50.;
pub const CARBONATORS_PER_ROLL: u32 = 3;

/// The copper cut for one carbonator: the laid wrap and both stubs.
pub fn cut_length() -> f64 {
    wrap_length() + stub_total()
}

/// What a roll has left after its carbonators, in feet.
pub fn roll_spare_ft() -> f64 {
    ROLL_LENGTH_FT - f64::from(CARBONATORS_PER_ROLL) * cut_length() / 304.8
}

// --- What the mandrel is wound to ------------------------------------------------------------

/// The mandrel winds the copper this far inside the carbonator's radius; it springs out onto the
/// carbonator coming off.
pub const MANDREL_UNDERSIZE: f64 = 3.;
/// The copper's centreline on the mandrel: its inside on the carbonator's radius less the
/// undersize.
pub const MANDREL_WIND_RADIUS: f64 = casing::CARBONATOR_OUTER_RADIUS - MANDREL_UNDERSIZE + TUBE_RADIUS;
/// The plan points, as (x, z), whose azimuths the mandrel's winding starts and ends at, and its
/// whole turns between them.
pub const MANDREL_INLET_STATION: [f64; 2] = [-30., 20.];
pub const MANDREL_OUTLET_STATION: [f64; 2] = [30., 20.];
pub const MANDREL_FULL_WRAPS: u32 = 9;

/// The stations' azimuths, in degrees, and the arc from the inlet's on to the outlet's.
pub fn mandrel_inlet_azimuth() -> f64 {
    MANDREL_INLET_STATION[1].atan2(MANDREL_INLET_STATION[0]).to_degrees()
}

pub fn mandrel_outlet_azimuth() -> f64 {
    MANDREL_OUTLET_STATION[1].atan2(MANDREL_OUTLET_STATION[0]).to_degrees()
}

pub fn mandrel_arc() -> f64 {
    (mandrel_outlet_azimuth() - mandrel_inlet_azimuth()).rem_euclid(360.)
}

/// The mandrel's turns over the winding's height, and their pitch.
pub fn mandrel_wraps() -> f64 {
    f64::from(MANDREL_FULL_WRAPS) + mandrel_arc() / 360.
}

pub fn mandrel_pitch() -> f64 {
    WIND_HEIGHT / mandrel_wraps()
}

/// The copper those turns take on the mandrel, and once sprung onto the carbonator.
pub fn mandrel_wrap_length() -> f64 {
    mandrel_wraps() * (2. * PI * MANDREL_WIND_RADIUS).hypot(mandrel_pitch())
}

pub fn fitted_wrap_length() -> f64 {
    mandrel_wraps() * (2. * PI * WIND_RADIUS).hypot(mandrel_pitch())
}

fn add(a: [f64; 3], b: [f64; 3]) -> [f64; 3] {
    std::array::from_fn(|i| a[i] + b[i])
}

fn scale(a: [f64; 3], s: f64) -> [f64; 3] {
    a.map(|v| v * s)
}

fn unit(a: [f64; 3]) -> [f64; 3] {
    scale(a, 1. / a.iter().map(|v| v * v).sum::<f64>().sqrt())
}

fn distance(a: [f64; 3], b: [f64; 3]) -> f64 {
    a.iter().zip(b).map(|(a, b)| (a - b).powi(2)).sum::<f64>().sqrt()
}
