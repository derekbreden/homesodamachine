//! The cold core's assembly numbers: what the assembly places that no part of its own holds. The
//! clamp screws through the casing; the level-sensing parts in the carbonator and the reservoirs;
//! the temperature probes; the reservoirs' grips and air tubes; where the PRV shroud, the reed
//! bridge and reservoir B's fill holder stand; and what each body is drawn in. The frame is the
//! foam shell's. The cold core's assembly takes these.
use hsm_carbonator_numbers as carbonator;
use hsm_coil_numbers as coil;
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::{b_fill, cap as frames};
use hsm_foam_cap_numbers as cap;
use hsm_reed_bridge_numbers as bridge;
use hsm_reservoir_numbers as reservoir;

pub mod presentation;

/// A point or a direction.
pub type P3 = [f64; 3];

/// The fits the casing is cut to.
fn fits() -> core::Fits {
    catalog::fits()
}

// --- The clamp screws ---------------------------------------------------------------------------

/// The M5 socket-head cap screws that clamp the stack, one down through the lid and one up through
/// the bottom closure at each of the casing's attachment stations: the shank and the head, and the
/// hex socket with the overrun its cutter takes past the head's face.
pub mod clamp {
    use super::core;
    pub const SHANK_RADIUS: f64 = 2.5;
    pub const LENGTH: f64 = core::CAP_SCREW_LENGTH;
    pub const HEAD_RADIUS: f64 = 4.25;
    pub const HEAD_HEIGHT: f64 = core::SCREW_HEAD_HEIGHT;
    pub const SOCKET_AF: f64 = 4.;
    pub const SOCKET_DEPTH: f64 = 2.5;
    pub const SOCKET_OVERRUN: f64 = 0.1;
}

/// One clamp screw: its name, its station, the height its head seats at, and the way its shank
/// runs from there.
#[derive(Clone, Debug)]
pub struct Clamp {
    pub name: String,
    pub xy: [f64; 2],
    pub seat: f64,
    pub direction: f64,
}

/// The clamp screws, the lid's then the bottom closure's: the lid's heads seat in its counterbores
/// under the cap's face and drive down, the closure's seat on its head pads and drive up.
pub fn clamps() -> Vec<Clamp> {
    let fits = fits();
    let sides = [
        ("top", cap::face_z() - core::head_cbore_depth(&fits), -1.),
        ("bottom", cap::stack_floor_z() + core::head_pad_height(&fits), 1.),
    ];
    let mut clamps = vec![];
    for (side, seat, direction) in sides {
        for (i, (xy, _)) in core::attachment_stations().into_iter().enumerate() {
            clamps.push(Clamp { name: format!("cap-clamp-{side}-{}", i + 1), xy, seat, direction });
        }
    }
    clamps
}

// --- Level sensing ------------------------------------------------------------------------------

/// A reed's glass, the whole of what a reed takes room for: the bridge's mounting envelope.
pub const REED_LENGTH: f64 = bridge::REED_GLASS_LENGTH;
pub const REED_RADIUS: f64 = bridge::REED_GLASS_DIAMETER / 2.;

/// The carbonator's reeds, at the bridge's pockets against the bare wall on the register
/// azimuth: the low and the high, in the shell's frame.
pub fn carbonator_reeds() -> [P3; 2] {
    let radius = core::CARBONATOR_OUTER_RADIUS + REED_RADIUS;
    let [x, y] = core::CARBONATOR_SENSOR_AXIS.map(|v| radius * v);
    [bridge::reed_low_z(), bridge::reed_high_z()].map(|z| [x, y, z + carbonator::BOTTOM_Z])
}

/// The carbonator's float, on its rod at the high reed's centre.
pub fn carbonator_float() -> P3 {
    let [x, y] = carbonator::rod_xy();
    [x, y, bridge::reed_high_z() + carbonator::BOTTOM_Z]
}

/// A reservoir: its letter, the side its pocket is on, and the files its body and cap print from.
#[derive(Clone, Copy, Debug)]
pub struct Reservoir {
    pub letter: &'static str,
    pub side: f64,
    pub body: &'static str,
    pub cap: &'static str,
}

/// Reservoir A fills the +X pocket and reservoir B the −X one, each from its own side's print.
pub const RESERVOIRS: [Reservoir; 2] = [
    Reservoir {
        letter: "a",
        side: 1.,
        body: "hardware/printed-parts/cold-core/reservoir/reservoir-right.step.npz",
        cap: "hardware/printed-parts/cold-core/reservoir/reservoir-cap-right.step.npz",
    },
    Reservoir {
        letter: "b",
        side: -1.,
        body: "hardware/printed-parts/cold-core/reservoir/reservoir-left.step.npz",
        cap: "hardware/printed-parts/cold-core/reservoir/reservoir-cap-left.step.npz",
    },
];

/// Both reservoirs' gaskets print from one file, the −X one mirrored.
pub const GASKET: &str = "hardware/printed-parts/cold-core/reservoir/reservoir-gasket.step.npz";

impl Reservoir {
    /// Where the gasket's own frame lands: on the cup's rim, under the cap's foot.
    pub fn gasket_lift(&self) -> f64 {
        reservoir::cap_assembly_lift() - reservoir::GASKET_THICKNESS
    }

    /// The rod: in its anchor boss's blind seat, its foot on the seat's floor.
    pub fn rod_foot(&self) -> P3 {
        [self.side * reservoir::rod_x(), reservoir::ROD_Y, reservoir::floor_z() + reservoir::ROD_ANCHOR_FLOOR]
    }

    /// The float, on its rod at the middle of its travel.
    pub fn float(&self) -> P3 {
        let [low, high] = reservoir::float_magnet_travel_z();
        [self.side * reservoir::rod_x(), reservoir::ROD_Y, (low + high) / 2.]
    }

    /// The reeds up the shell's channel beside the pocket, on the reed column's axis.
    pub fn reeds(&self) -> [P3; core::REEDS_PER_RESERVOIR] {
        reservoir::reed_centres_z().map(|z| [self.side * core::REED_COLUMN_AXIS_X, core::REED_Y_CENTER, z])
    }

    /// The cap's grips: its fill's, its draw's and its air tube's, each where its port stands, in
    /// the cap's plate.
    pub fn grips(&self) -> [(&'static str, [f64; 2], reservoir::Grip); 3] {
        let side = self.side as i64;
        let port =
            |table: &[(i64, [f64; 2])]| core::reservoir_port(table, side).expect("a port on each side");
        [
            ("fill", port(&core::RESERVOIR_FILL_PORT), reservoir::LIQUID_GRIP),
            ("draw", port(&core::RESERVOIR_DRAW_PORT), reservoir::LIQUID_GRIP),
            ("air", port(&reservoir::AIR_PORT), reservoir::AIR_GRIP),
        ]
    }
}

/// The cap's plate, which the grips are captured in: its underside, over the cap's wall on the
/// gasket.
pub fn grip_z() -> f64 {
    reservoir::cap_assembly_lift() + reservoir::CAP_WALL_HEIGHT
}

/// The air tube: from under the cap's plate up past the cap's face.
pub fn air_tube_z() -> [f64; 2] {
    [grip_z() - reservoir::AIR_TUBE_BELOW_LID, cap::face_z() + reservoir::AIR_TUBE_ABOVE_CASING]
}

// --- The probes ---------------------------------------------------------------------------------

/// The DS18B20 and DS18S20 1-wire probes: a bare TO-92, its leads sleeved, foil-taped to the
/// surface it reads and potted in the pour. The package is a rounded square stood upright.
pub mod to92 {
    pub const WIDTH: f64 = 4.3;
    pub const HEIGHT: f64 = 5.2;
    pub const CORNER_RADIUS: f64 = 1.2;
    /// What stands the package off the wall it is taped to: its half diagonal, as a share of its
    /// width.
    pub const STANDOFF_PER_WIDTH: f64 = 0.71;
    pub const STANDOFF: f64 = WIDTH * STANDOFF_PER_WIDTH;
}

/// The carbonator's probe, taped to its wall opposite the register azimuth, in a gap between the
/// coil's wraps at the wetted column's middle.
pub fn carbonator_probe() -> P3 {
    let z = coil::gap_z_near(180., (carbonator::INTERIOR_Z[0] + carbonator::INTERIOR_Z[1]) / 2.);
    [-(core::CARBONATOR_OUTER_RADIUS + to92::STANDOFF), 0., z]
}

/// The coil's probe, its flat face on the copper at the wrap's suction end, the outlet tail's.
pub fn coil_probe() -> P3 {
    coil::at(coil::OUTLET_AZIMUTH, coil::HIGH_Z, coil::WIND_RADIUS + coil::TUBE_RADIUS + to92::WIDTH / 2.)
}

/// How finely the coil's and its tails' sweeps follow their paths.
pub const COIL_PATH_CHORD: f64 = 0.0035;

// --- Where other parts' files stand -------------------------------------------------------------

/// A turn about an axis through the origin, in degrees.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Turn {
    pub axis: P3,
    pub degrees: f64,
}

/// A rigid carry: its rotation's columns and its translation.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Carry {
    pub columns: [P3; 3],
    pub translation: P3,
}

/// A part's printed file placed in the core: turned, moved, carried, then turned and moved again,
/// each in order.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Placement {
    pub turns: Vec<Turn>,
    pub shift: P3,
    pub carry: Option<Carry>,
    pub after_turns: Vec<Turn>,
    pub after_shift: P3,
}

/// The reed bridge: on the carbonator's register azimuth, its own frame's zero on the tube's
/// bottom rim.
pub const REED_BRIDGE: &str = "hardware/printed-parts/cold-core/reed-bridge/reed-bridge.step.npz";

pub fn reed_bridge() -> Placement {
    Placement {
        turns: vec![Turn { axis: [0., 0., 1.], degrees: core::CARBONATOR_SENSOR_AZIMUTH }],
        shift: [0., 0., carbonator::BOTTOM_Z],
        ..Placement::default()
    }
}

/// Reservoir B's fill holder: printed on its back, stood up into the enclosure at the bend's end
/// of the fill tube's passage, then carried with the cap onto the shell.
pub const B_FILL_HOLDER: &str = "hardware/printed-parts/cold-core/foam-cap/reservoir-b-fill-guide.step.npz";

pub fn b_fill_holder() -> Placement {
    let [x, y, z] = b_fill::passage().bend_end;
    let pose = frames::cap_lid_pose();
    let r = pose.rotation;
    let t = pose.translation;
    let columns: [P3; 3] = std::array::from_fn(|i| r[i]);
    let translation: P3 = std::array::from_fn(|i| -(r[0][i] * t[0] + r[1][i] * t[1] + r[2][i] * t[2]));
    Placement {
        turns: vec![Turn { axis: [0., 1., 0.], degrees: -90. }],
        shift: [x + b_fill::CHANNEL_CENTRE, y - b_fill::BEND_RADIUS, z],
        carry: Some(Carry { columns, translation }),
        after_turns: vec![Turn { axis: [0., 0., 1.], degrees: 180. }],
        after_shift: [0., 0., core::FOAM_SHELL_OUTER_HEIGHT + core::top_cap_height(&fits())],
    }
}

/// The PRV shroud: on the PRV's socket, its cup's axis along the socket's out of the elbow, rolled
/// about that axis so the vent bore in its barrel faces down the lane. The vent bore leaves the
/// cup's own frame along `SHROUD_VENT_LOCAL` and faces `SHROUD_VENT_DOWN` installed.
pub const PRV_SHROUD: &str = "hardware/printed-parts/cold-core/prv-shroud/prv-shroud.step.npz";
pub const SHROUD_VENT_LOCAL: P3 = [0., -1., 0.];
pub const SHROUD_VENT_DOWN: P3 = [0., 0., -1.];

pub fn prv_shroud() -> Placement {
    let prv = carbonator::port("prv");
    let mut turns = rotation_to_z(prv.axis);
    let vent = turned_by(SHROUD_VENT_LOCAL, &turns);
    let axis = prv.axis;
    let roll = degrees(dot(axis, cross(vent, SHROUD_VENT_DOWN)).atan2(dot(vent, SHROUD_VENT_DOWN)));
    turns.push(Turn { axis, degrees: roll });
    Placement { turns, shift: prv.mouth, ..Placement::default() }
}

/// Where the shroud's vent bore opens on its barrel, installed: the PRV's vent line starts there.
pub fn shroud_vent_mouth() -> P3 {
    let placement = prv_shroud();
    let local = [0., -hsm_prv_shroud_numbers::outer_diameter() / 2., hsm_prv_shroud_numbers::VENT_STATION_Z];
    let at = add(turned_by(local, &placement.turns), placement.shift);
    at.map(|v| format!("{v:.6}").parse().expect("a rounded coordinate"))
}

/// The turn that stands a part built along +Z on `axis`: none on +Z, a half turn about X on −Z.
fn rotation_to_z(axis: P3) -> Vec<Turn> {
    let axis = unit(axis);
    let dot = axis[2].clamp(-1., 1.);
    if dot > 1. - 1e-12 {
        vec![]
    } else if dot < -1. + 1e-12 {
        vec![Turn { axis: [1., 0., 0.], degrees: 180. }]
    } else {
        vec![Turn { axis: cross([0., 0., 1.], axis), degrees: degrees(dot.acos()) }]
    }
}

/// `vector` turned by each turn in order.
fn turned_by(mut vector: P3, turns: &[Turn]) -> P3 {
    for turn in turns {
        let axis = unit(turn.axis);
        let angle = turn.degrees * std::f64::consts::PI / 180.;
        let (c, s) = (angle.cos(), angle.sin());
        vector = add(
            add(scale(vector, c), scale(cross(axis, vector), s)),
            scale(axis, dot(axis, vector) * (1. - c)),
        );
    }
    vector
}

fn degrees(angle: f64) -> f64 {
    angle * 180. / std::f64::consts::PI
}

fn add(a: P3, b: P3) -> P3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

fn scale(a: P3, s: f64) -> P3 {
    [a[0] * s, a[1] * s, a[2] * s]
}

fn dot(a: P3, b: P3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn cross(a: P3, b: P3) -> P3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}

fn unit(a: P3) -> P3 {
    scale(a, 1. / dot(a, a).sqrt())
}

// --- The lines ----------------------------------------------------------------------------------

/// The lines as the core draws them: each line's corners, with its ends on the carbonator's ports
/// moved onto the mouths of the elbows made up there, and the PRV's vent started at the shroud's
/// bore.
pub fn lines() -> Vec<hsm_cold_core_layout::routes::Line> {
    let mut lines = hsm_cold_core_layout::routes::lines();
    for &(port, line, start) in &carbonator::PORT_LINES {
        let mouth = carbonator::port(port).mouth;
        let points = &mut lines.iter_mut().find(|l| l.name == line).expect("a port's line").points;
        let end = if start { 0 } else { points.len() - 1 };
        points[end] = mouth;
    }
    let vent = &mut lines.iter_mut().find(|l| l.name == "prv-vent").expect("the PRV's vent").points;
    vent[0] = shroud_vent_mouth();
    lines
}
