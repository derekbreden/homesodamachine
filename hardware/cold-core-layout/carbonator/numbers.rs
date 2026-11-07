//! The carbonator's numbers, in millimetres, in the cold core's frame: Z up from the casing's
//! base, the carbonator's axis on Z, ±Y the axis its ports stand on, −Y the register azimuth
//! its float rod and level reeds read on. The vessel is the 316 tube with the end cap's disc
//! recessed its own thickness into each end and welded there, the float rod between the discs'
//! blind registers and its upper stop; on the top disc's tapped ports a street elbow each, one
//! carrying the water inlet's jet and collet and the other the PRV; on the bottom disc's a push-fit
//! male elbow each; and the earth bond screwed radially into the tube's open upper rim. The cold
//! core's assembly takes these, and the cold core's data provider hands the earth bond's datums to
//! the BOM and the wiring.
use hsm_aero_float_numbers as float;
use hsm_carbonator_tube_numbers as tube;
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::routes;
use hsm_endcap_circular_numbers as cap;
use hsm_foam_shell_numbers as shell;

/// A point or a direction.
pub type P3 = [f64; 3];

/// Millimetres in an inch: the catalog parts are sized in inches.
pub const INCH: f64 = 25.4;

// --- The vessel ---------------------------------------------------------------------------------

/// The tube stands on the casing's floor and the carbonator's support ring, and runs its own length
/// up from there.
pub const BOTTOM_Z: f64 = core::WALL_AND_FLOOR_THICKNESS + core::CARBONATOR_SUPPORT_RING_HEIGHT;
pub const TOP_Z: f64 = core::CARBONATOR_TOP_PLATE_Z;
pub const HEIGHT: f64 = core::CARBONATOR_HEIGHT;

/// The plates: the end cap's disc, set its own thickness in from each tube end, where the closure
/// fillet is laid.
pub const PLATE_DIAMETER: f64 = cap::DIAMETER_IN * INCH;
pub const PLATE_THICKNESS: f64 = cap::THICKNESS_IN * INCH;
pub const PLATE_RECESS: f64 = PLATE_THICKNESS;
/// Each plate's two faces, and the wetted column between them.
pub const BOTTOM_PLATE_Z: [f64; 2] = [BOTTOM_Z + PLATE_RECESS, BOTTOM_Z + PLATE_RECESS + PLATE_THICKNESS];
pub const TOP_PLATE_Z: [f64; 2] = [TOP_Z - PLATE_RECESS - PLATE_THICKNESS, TOP_Z - PLATE_RECESS];
pub const INTERIOR_Z: [f64; 2] = [BOTTOM_PLATE_Z[1], TOP_PLATE_Z[0]];
/// The tap drill each plate's ports are tapped through.
pub const PORT_TAP_DIAMETER: f64 = cap::HOLE_DIAMETER_IN * INCH;

/// The float's guide: round bar the float rides, welded between the plates' blind registers on
/// the register azimuth, under the end cap's register.
pub const ROD_DIAMETER: f64 = float::GUIDE_DIAMETER;
pub const ROD_RADIUS: f64 = cap::REGISTER_RADIUS_IN * INCH;
/// The register: drilled into each plate's inside face, as deep as the end cap says.
pub const REGISTER_DIAMETER: f64 = cap::REGISTER_DRILL_IN * INCH;
pub const REGISTER_DEPTH: f64 = cap::REGISTER_DEPTH_IN * INCH;

/// The rod's station in plan.
pub fn rod_xy() -> [f64; 2] {
    core::CARBONATOR_SENSOR_AXIS.map(|v| ROD_RADIUS * v)
}

/// The rod's ends: in each plate's register.
pub const ROD_Z: [f64; 2] = [INTERIOR_Z[0] - REGISTER_DEPTH, INTERIOR_Z[1] + REGISTER_DEPTH];

/// The float's upper stop: a ring of round bar round the rod, tacked to the top plate's inside face,
/// bored to the register's drill.
pub const UPPER_STOP_HEIGHT: f64 = core::CARBONATOR_FLOAT_TOP_STOP_HEIGHT;
pub const UPPER_STOP_DIAMETER: f64 = core::CARBONATOR_FLOAT_TOP_STOP_DIAMETER;
pub const UPPER_STOP_BORE: f64 = REGISTER_DIAMETER;

/// The vessel, its rod and its stop are 316 stainless.
pub fn colour() -> catalog::Colour {
    catalog::stainless()
}

// --- The ports ----------------------------------------------------------------------------------

/// The plate a port is tapped through.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Plate {
    Bottom,
    Top,
}

/// The ports, each where the casing's interface puts it on the port axis: the CO2 in and the
/// carbonated water out under the liquid, the water in and the PRV over it.
pub const PORTS: [(&str, Plate, f64); 4] = [
    ("co2-in", Plate::Bottom, core::CO2_INLET_Y),
    ("carb-water-out", Plate::Bottom, -core::CO2_INLET_Y),
    ("water-in", Plate::Top, core::WATER_INLET_PORT_Y),
    ("prv", Plate::Top, core::PRV_PORT_Y),
];

/// The street elbow's leg off the top plate's outer face to the band its line turns onto, and the
/// push-fit elbow's socket axis off the bottom plate's outer face to the storey its line leaves on.
pub const TOP_AXIS_OFFSET: f64 = core::HOLE_SHIFT_FROM_EDGE + PLATE_RECESS;
pub const BOTTOM_AXIS_OFFSET: f64 = BOTTOM_PLATE_Z[0] - shell::FRONT_FACE_PORT_Z;

/// One port as made up: where its elbow's two axes cross, the way its male leg threads into the
/// plate, the way its socket faces, and the mouth the next fitting or line lands on.
#[derive(Clone, Copy, Debug)]
pub struct Port {
    pub name: &'static str,
    pub plate: Plate,
    pub corner: P3,
    pub up: P3,
    pub out: P3,
    pub mouth: P3,
    pub axis: P3,
}

impl Port {
    /// How far off the plate's outer face the elbow turns its line.
    pub fn axis_offset(&self) -> f64 {
        match self.plate {
            Plate::Bottom => BOTTOM_AXIS_OFFSET,
            Plate::Top => TOP_AXIS_OFFSET,
        }
    }

    /// The male engagement drawn past the plate's outer face, at the catalog's nominal: the
    /// installed engagement and the tip's projection are unmeasured.
    pub fn male_length(&self) -> f64 {
        match self.plate {
            Plate::Bottom => male_elbow::THREAD - (BOTTOM_AXIS_OFFSET - male_elbow::AXIS_REACH),
            Plate::Top => street_elbow::MALE_LENGTH,
        }
    }

    /// The male leg's tip, where it enters the carbonator.
    pub fn male_tip(&self) -> P3 {
        add(self.corner, scale(self.up, self.axis_offset() + self.male_length()))
    }
}

/// Which line each port hands to, and whether the port is that line's start or its end: a socket
/// is clocked by the run it receives.
pub const PORT_LINES: [(&str, &str, bool); 3] =
    [("co2-in", "co2-in", false), ("carb-water-out", "carb-water-out", true), ("water-in", "water-in", true)];

/// The PRV carries no line into the core, so its socket faces out along its own side of the port
/// axis: the shroud made up on it lands its vent on that side's lane.
pub fn prv_out() -> P3 {
    [0.0, if core::PRV_PORT_Y > 0. { 1.0 } else { -1.0 }, 0.0]
}

/// The ports, as made up, in the order `PORTS` lists them.
pub fn ports() -> Vec<Port> {
    let lines = routes::lines();
    PORTS
        .iter()
        .map(|&(name, plate, y)| {
            let out = match PORT_LINES.iter().find(|(port, _, _)| *port == name) {
                Some(&(_, line, start)) => {
                    let points = &lines.iter().find(|l| l.name == line).expect("a port's line").points;
                    let n = points.len();
                    let (a, b) = if start { (points[0], points[1]) } else { (points[n - 1], points[n - 2]) };
                    unit(sub(b, a))
                }
                None => prv_out(),
            };
            let (corner, up, reach) = match plate {
                Plate::Bottom => (
                    [0.0, y, BOTTOM_PLATE_Z[0] - BOTTOM_AXIS_OFFSET],
                    [0.0, 0.0, 1.0],
                    male_elbow::MOUTH_REACH,
                ),
                Plate::Top => {
                    ([0.0, y, TOP_PLATE_Z[1] + TOP_AXIS_OFFSET], [0.0, 0.0, -1.0], street_elbow::LEG)
                }
            };
            let axis = unit(out);
            Port { name, plate, corner, up, out, mouth: add(corner, scale(axis, reach)), axis }
        })
        .collect()
}

/// One port, by name.
pub fn port(name: &str) -> Port {
    ports().into_iter().find(|p| p.name == name).expect("the carbonator has that port")
}

// --- The fittings -------------------------------------------------------------------------------

/// The TAISHER 316L barstock street elbow, ¼" NPT male by female, on each top-plate port: a hex
/// bar on each leg, sized so its corners clear the PRV shroud's bore, the male stub drawn as the
/// tap drill it threads into, and the female socket at the male's major diameter for a stub's
/// depth. The bore is a layout stand-in, not a measured one.
pub mod street_elbow {
    use super::INCH;
    pub const HEX_AF: f64 = 0.625 * INCH;
    pub const LEG: f64 = 0.81 * INCH;
    pub const BORE: f64 = 0.25 * INCH;
    pub const MALE_RADIUS: f64 = 0.5 * 0.4375 * INCH;
    pub const MALE_LENGTH: f64 = 0.26 * INCH;
    pub const SOCKET_RADIUS: f64 = 0.5 * 0.540 * INCH;
    pub const SOCKET_DEPTH: f64 = 0.5 * INCH;
}

/// The neoFit AME4-N2-E push-fit male elbow, ¼" tube by ¼" NPTF, on each bottom-plate port, from
/// neoFit's drawing: its thread, its overall height, the socket body's diameter and length, the
/// post over the thread, the tube's insertion, the flow bore and the tube it takes.
pub mod male_elbow {
    use super::INCH;
    pub const THREAD: f64 = 0.520 * INCH;
    pub const HEIGHT: f64 = 1.256 * INCH;
    pub const BODY_DIAMETER: f64 = 0.610 * INCH;
    pub const LENGTH: f64 = 1.063 * INCH;
    pub const POST_WIDTH: f64 = 0.4375 * INCH;
    pub const INSERTION: f64 = 0.665 * INCH;
    pub const FLOW_BORE: f64 = 4.3;
    pub const TUBE_OD: f64 = 0.25 * INCH;
    /// The socket's axis over the thread's shoulder, and its mouth off the thread's axis.
    pub const AXIS_REACH: f64 = HEIGHT - THREAD - BODY_DIAMETER / 2.;
    pub const MOUTH_REACH: f64 = LENGTH - POST_WIDTH / 2.;
}

/// The Control Devices SV-125 safety valve, ¼" NPT, made up on the PRV port's elbow: a hex base on a
/// round cap, and the male stub back into the socket.
pub mod prv {
    use super::INCH;
    pub const HEX_AF: f64 = 0.5625 * INCH;
    pub const HEX_HEIGHT: f64 = 0.44 * INCH;
    pub const CAP_RADIUS: f64 = 0.5 * 0.62 * INCH;
    pub const CAP_HEIGHT: f64 = 1.06 * INCH;
    pub const MALE_LENGTH: f64 = 0.50 * INCH;
}

/// The John Guest PP010822E adapter's envelope, made up on the water inlet's elbow: the push-fit
/// collet, the wrench hex and the NPT shank, along its own axis.
pub mod collet {
    pub const COLLET_DIAMETER: f64 = 14.0;
    pub const COLLET_LENGTH: f64 = 13.5;
    pub const HEX_ACROSS_CORNERS: f64 = 16.5;
    pub const HEX_LENGTH: f64 = 5.0;
    pub const SHANK_DIAMETER: f64 = 13.7;
    pub const SHANK_LENGTH: f64 = 11.0;
    /// The collet stands its collet and hex out of the socket it threads into.
    pub const STANDOFF: f64 = COLLET_LENGTH + HEX_LENGTH;
}

/// The ports that take the adapter: the water inlet's.
pub const COLLET_PORTS: [&str; 1] = ["water-in"];

/// The inlet jet's cap: a drilled slice of 316 round bar welded to the water inlet elbow's male
/// tip, pointing into the carbonator, at its fabrication targets. Its fit, weld and installed
/// projection are unqualified.
pub mod jet {
    pub const CAP_DIAMETER: f64 = 9.5;
    pub const CAP_THICKNESS: f64 = 2.0;
    pub const PASSAGE_DIAMETER: f64 = 25.4 / 16.0;
}

/// The elbows on the top plate are 316 stainless; the push-fit elbows on the bottom plate are
/// neoFit's black acetal; the PRV is brass; the adapter John Guest's black polypropylene.
pub fn street_elbow_colour() -> catalog::Colour {
    catalog::stainless()
}

pub fn male_elbow_colour() -> catalog::Colour {
    catalog::neofit_acetal()
}

pub fn prv_colour() -> catalog::Colour {
    catalog::brass()
}

pub fn collet_colour() -> catalog::Colour {
    catalog::jg_black_pp()
}

// --- The earth bond -----------------------------------------------------------------------------

/// The carbonator's earth: a closed ring screwed radially into the tube's open upper rim, over the
/// recessed top plate, with an external-tooth lockwasher under a shortened screw's head. The ring
/// tongue, washer and head stay outside the tube, and the short screw clears the recess inside.
pub mod bond {
    use super::{P3, core, tube};

    /// The rim azimuth the hole is tapped on, in plan: toward the sensor loom's conduit in the
    /// shell's frame, which the earth lead rises through with the carbonator's other leads.
    pub const RIM_AZIMUTH_XY: [f64; 2] =
        [-core::SENSOR_CABLE_CONDUIT_XY[0], -core::SENSOR_CABLE_CONDUIT_XY[1]];
    /// The hole's height over the top plate's outer face, within the rim's open recess.
    pub const HOLE_HEIGHT: f64 = 3.5;
    /// The M3 × 0.5 thread tapped through the wall, and its tap drill.
    pub const TAP_DRILL_DIAMETER: f64 = 2.5;
    pub const THREAD_DIAMETER: f64 = 3.0;
    pub const THREAD_PITCH: f64 = 0.5;
    /// The screw: M3 stock shortened and end-finished to this length.
    pub const SCREW_LENGTH: f64 = 4.0;
    pub const SCREW_DIAMETER: f64 = 3.0;
    pub const SCREW_HEAD_DIAMETER: f64 = 5.5;
    pub const SCREW_HEAD_HEIGHT: f64 = 3.0;
    /// The closed ring: its tongue, its eye and the barrel the lead is crimped in.
    pub const RING_TONGUE_THICKNESS: f64 = 0.8;
    pub const RING_EYE_DIAMETER: f64 = 8.0;
    pub const RING_BARREL_DIAMETER: f64 = 4.2;
    pub const RING_BARREL_LENGTH: f64 = 6.0;
    /// The DIN 6797 A lockwasher.
    pub const WASHER_DIAMETER: f64 = 6.0;
    pub const WASHER_BORE: f64 = 3.2;
    pub const WASHER_THICKNESS: f64 = 0.4;
    pub const WASHER_PART: &str = "M3 DIN 6797 A external-tooth lockwasher, A2 stainless";
    pub const WASHER_SOURCE: &str =
        "https://damesa.com/en/products/fasteners/washers/din-6797-external-tooth-lock-washer-form-a";
    pub const SCREW_SOURCE: &str = "304 stainless M3x12 stock shortened and end-finished to M3x4";
    /// The wall the thread is cut in, and the open rim over the recessed plate.
    pub const TUBE_OUTER_RADIUS: f64 = tube::OUTER_RADIUS;
    pub const TUBE_WALL: f64 = tube::WALL;
    pub const RIM_HEIGHT: f64 = super::PLATE_RECESS;
    /// How far up the ring's barrel the lead leaves it.
    pub const WIRE_EXIT_RISE: f64 = 9.0;

    /// The bond's datums for a top plate whose outer face is at `top_plate_outer_z`.
    #[derive(Clone, Copy, Debug)]
    pub struct Datums {
        /// The rim's centre over the plate, on the bond's azimuth.
        pub base_center: P3,
        /// The tapped hole's centre in the wall, and its axis inward.
        pub hole_center: P3,
        pub hole_axis: P3,
        /// Where the ring's tongue meets the bare rim, and the way out of the wall there.
        pub contact_point: P3,
        pub contact_outward: P3,
        /// Where the lead leaves the ring's barrel, and the way it leaves.
        pub wire_exit: P3,
        pub wire_outward: P3,
        /// The screw: its axis inward, under its head, and its tip.
        pub screw_axis: P3,
        pub screw_underhead: P3,
        pub screw_tip: P3,
        /// The rim's top, and how far the screw reaches past the wall's inside face.
        pub rim_top_z: f64,
        pub screw_projection_inside_tube: f64,
    }

    pub fn datums(top_plate_outer_z: f64) -> Datums {
        let scale = RIM_AZIMUTH_XY[0].hypot(RIM_AZIMUTH_XY[1]);
        let (ux, uy) = (RIM_AZIMUTH_XY[0] / scale, RIM_AZIMUTH_XY[1] / scale);
        let z = top_plate_outer_z + HOLE_HEIGHT;
        let radial = |radius: f64, height: f64| [ux * radius, uy * radius, height];
        let head_radius = TUBE_OUTER_RADIUS + RING_TONGUE_THICKNESS + WASHER_THICKNESS;
        let tip_radius = head_radius - SCREW_LENGTH;
        Datums {
            base_center: radial(TUBE_OUTER_RADIUS, top_plate_outer_z),
            hole_center: radial(TUBE_OUTER_RADIUS - TUBE_WALL / 2., z),
            hole_axis: [-ux, -uy, 0.],
            contact_point: radial(TUBE_OUTER_RADIUS, z),
            contact_outward: [ux, uy, 0.],
            wire_exit: radial(TUBE_OUTER_RADIUS + RING_BARREL_DIAMETER / 2., z + WIRE_EXIT_RISE),
            wire_outward: [0., 0., 1.],
            screw_axis: [-ux, -uy, 0.],
            screw_underhead: radial(head_radius, z),
            screw_tip: radial(tip_radius, z),
            rim_top_z: top_plate_outer_z + RIM_HEIGHT,
            screw_projection_inside_tube: TUBE_OUTER_RADIUS - TUBE_WALL - tip_radius,
        }
    }
}

/// The carbonator's earth bond, on its own top plate.
pub fn bond() -> bond::Datums {
    bond::datums(TOP_PLATE_Z[1])
}

/// The body the bond is screwed into.
pub const BOND_BODY: &str = "carbonator-tube";

fn add(a: P3, b: P3) -> P3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

fn sub(a: P3, b: P3) -> P3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn scale(a: P3, s: f64) -> P3 {
    [a[0] * s, a[1] * s, a[2] * s]
}

/// `a` scaled to unit length, by its length's reciprocal.
fn unit(a: P3) -> P3 {
    scale(a, 1.0 / (a[0] * a[0] + a[1] * a[1] + a[2] * a[2]).sqrt())
}
