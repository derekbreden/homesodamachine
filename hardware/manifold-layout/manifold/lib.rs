//! The flavor manifold as it is arranged: where each purchased valve, tee and pump stands and
//! where every tube between them runs (`placements`), the limbs its valves and tees form, the
//! connections between their ports and the mouths that leave it. The manifold's program cuts its
//! model from these; the plumbing chart and the BOM count and measure them.
pub mod placements;
pub use placements::BODIES;

use serde::Deserialize;
use std::sync::OnceLock;

/// A point or a direction in the manifold's authoring frame, in mm.
pub type P3 = [f64; 3];

/// The purchased model a placed body is cut from, and which of its bodies it keeps.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Part {
    /// The Beduan solenoid's body and push-fit collets.
    Valve,
    /// The same solenoid's coil: winding, yoke, screw heads and spade terminals.
    Coil,
    /// The John Guest PP0208E tee.
    Tee,
    /// The Kamoer pump's observed exterior components.
    PumpHead,
    PumpBoss,
    PumpMount,
    PumpMotor,
    PumpFasteners,
    PumpPrimer,
    PumpSleeves,
    /// The NeoFit stem elbow with its release collet, its stem trimmed to stand `stem` mm into
    /// the collet it plugs into.
    StemElbow { stem: f64 },
}

/// One purchased body where it stands: its frame's origin, and its own X and Z axes.
pub struct Placement {
    pub name: &'static str,
    pub part: Part,
    pub at: P3,
    pub x: P3,
    pub z: P3,
}

/// One piece of a tube's centreline: a straight between two points, or a circular arc through
/// its start, a point on it and its end.
#[derive(Clone, Copy, Debug)]
pub enum Seg {
    Line([P3; 2]),
    Arc([P3; 3]),
}

/// One tube: the run it belongs to, the way it leaves its first end, its bore when the model
/// shows one, and its centreline.
pub struct Tube {
    pub name: &'static str,
    pub run: &'static str,
    pub leaves: P3,
    pub bore: Option<f64>,
    pub path: &'static [Seg],
}

/// One of the manifold's bodies: a purchased one where it stands, or a tube.
pub enum Body {
    Bought(Placement),
    Tubed(Tube),
}

/// The tubes, in the model's order.
pub fn tubes() -> impl Iterator<Item = &'static Tube> {
    BODIES.iter().filter_map(|b| match b {
        Body::Tubed(t) => Some(t),
        Body::Bought(_) => None,
    })
}

/// The ¼" LLDPE every port of the manifold takes, outside.
pub const TUBE_OD: f64 = 6.35;
/// A prepared pump tube's length inside the pump's BPT tube, under the head's clamp.
pub const PUMP_TUBE_HELD: f64 = 13.149;

/// One limb: its valves and tees front to back, and how many from the front fold over onto the
/// upper deck.
pub struct Limb {
    pub name: &'static str,
    pub chain: &'static [&'static str],
    pub folded: usize,
}

pub const LIMBS: [Limb; 4] = [
    Limb { name: "A1", chain: &["V-A", "Y-A", "V-C", "Y-C", "V-E"], folded: 3 },
    Limb { name: "A2", chain: &["V-G", "Y-D", "V-F"], folded: 1 },
    Limb { name: "B1", chain: &["V-B", "Y-B", "V-D", "Y-F", "V-H"], folded: 3 },
    Limb { name: "B2", chain: &["V-J", "Y-G", "V-I"], folded: 1 },
];

/// The two pumps, one under each channel's limbs.
pub const PUMPS: [&str; 2] = ["pump-a", "pump-b"];

/// How one connection between two of the manifold's ports is made.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Made {
    /// A source valve's quarter turn and the two-arc step after it: `turn-` and `step-` tubes.
    Turn,
    /// The two source tees' branch collets, face to face across the mirror plane with no tube
    /// between them.
    Crossbar,
    /// Two collet faces butted: tube in both quick-connects and none between them.
    Butt,
    /// A pump tee's lower return: a stem elbow in each collet and one tube between them.
    LowerReturn { tee: &'static str },
    /// A pump tee's upper run to the fore valve over it, on one straight tube.
    Upper { tee: &'static str },
    /// A prepared pump's tube through the collet plate into its tee.
    PumpTube { tee: &'static str },
}

/// One connection: its run number, the two ports it joins, and how it is made.
pub struct Connection {
    pub run: u32,
    pub from: &'static str,
    pub to: &'static str,
    pub made: Made,
}

pub const CONNECTIONS: [Connection; 17] = [
    Connection { run: 3, from: "V-A-O", to: "Y-A-1", made: Made::Turn },
    Connection { run: 5, from: "V-B-O", to: "Y-B-1", made: Made::Turn },
    Connection { run: 6, from: "Y-A-3", to: "Y-B-3", made: Made::Crossbar },
    Connection { run: 7, from: "Y-A-2", to: "V-C-I", made: Made::Butt },
    Connection { run: 8, from: "Y-B-2", to: "V-D-I", made: Made::Butt },
    Connection { run: 9, from: "V-C-O", to: "Y-C-1", made: Made::LowerReturn { tee: "Y-C" } },
    Connection { run: 10, from: "V-E-O", to: "Y-C-2", made: Made::Upper { tee: "Y-C" } },
    Connection { run: 11, from: "Y-C-3", to: "P-A-I", made: Made::PumpTube { tee: "Y-C" } },
    Connection { run: 12, from: "P-A-O", to: "Y-D-1", made: Made::PumpTube { tee: "Y-D" } },
    Connection { run: 13, from: "Y-D-2", to: "V-F-I", made: Made::Upper { tee: "Y-D" } },
    Connection { run: 17, from: "Y-D-3", to: "V-G-I", made: Made::LowerReturn { tee: "Y-D" } },
    Connection { run: 19, from: "V-D-O", to: "Y-F-1", made: Made::LowerReturn { tee: "Y-F" } },
    Connection { run: 20, from: "V-H-O", to: "Y-F-2", made: Made::Upper { tee: "Y-F" } },
    Connection { run: 21, from: "Y-F-3", to: "P-B-I", made: Made::PumpTube { tee: "Y-F" } },
    Connection { run: 22, from: "P-B-O", to: "Y-G-1", made: Made::PumpTube { tee: "Y-G" } },
    Connection { run: 23, from: "Y-G-3", to: "V-I-I", made: Made::Upper { tee: "Y-G" } },
    Connection { run: 27, from: "Y-G-2", to: "V-J-I", made: Made::LowerReturn { tee: "Y-G" } },
];

/// One mouth of the manifold: a port whose run leaves it, and what that run carries. Each is
/// drawn as the `stub-` tube that reaches along its axis to where the run's first corner seats.
pub struct Mouth {
    pub run: &'static str,
    pub port: &'static str,
    pub what: &'static str,
}

pub const MOUTHS: [Mouth; 8] = [
    Mouth { run: "fluid-2", port: "V-A-I", what: "tap water in" },
    Mouth { run: "fluid-4", port: "V-B-I", what: "funnel in" },
    Mouth { run: "fluid-18", port: "V-G-O", what: "flavor A" },
    Mouth { run: "fluid-28", port: "V-J-O", what: "flavor B" },
    Mouth { run: "fluid-14", port: "V-F-O", what: "reservoir A fill" },
    Mouth { run: "fluid-16", port: "V-E-I", what: "reservoir A draw" },
    Mouth { run: "fluid-24", port: "V-I-O", what: "reservoir B fill" },
    Mouth { run: "fluid-26", port: "V-H-I", what: "reservoir B draw" },
];

/// The valves and tees of every limb, front to back, and whether each folds onto the upper deck.
pub fn stations() -> impl Iterator<Item = (&'static str, &'static Limb, bool)> {
    LIMBS.iter().flat_map(|limb| {
        limb.chain.iter().enumerate().map(move |(i, &name)| (name, limb, i < limb.folded))
    })
}

/// The purchased tees: every tee of every limb.
pub fn purchased_tees() -> impl Iterator<Item = &'static str> {
    stations().map(|(name, _, _)| name).filter(|name| name.starts_with("Y-"))
}

/// The tees on the pump ports, in the connections' order.
pub fn pump_junctions() -> impl Iterator<Item = &'static str> {
    CONNECTIONS.iter().filter_map(|c| match c.made {
        Made::PumpTube { tee } => Some(tee),
        _ => None,
    })
}

/// Each lower return's run and the pump tee it leaves.
pub fn lower_returns() -> impl Iterator<Item = (u32, &'static str)> {
    CONNECTIONS.iter().filter_map(|c| match c.made {
        Made::LowerReturn { tee } => Some((c.run, tee)),
        _ => None,
    })
}

/// The tube drawn by `name`.
pub fn tube(name: &str) -> &'static Tube {
    tubes().find(|t| t.name == name).unwrap_or_else(|| panic!("the manifold draws no {name}"))
}

/// The length of one centreline piece.
pub fn seg_length(seg: &Seg) -> f64 {
    match seg {
        Seg::Line([a, b]) => distance(*a, *b),
        Seg::Arc([a, m, b]) => {
            // The circle through the three points: its radius from the triangle they make, and
            // the angle the arc turns from the chord's half-angle at the centre.
            let (u, v) = (sub(*m, *a), sub(*b, *a));
            let w = cross(u, v);
            let r = norm(u) * norm(v) * norm(sub(v, u)) / (2.0 * norm(w));
            let half = (distance(*a, *b) / (2.0 * r)).min(1.0).asin();
            // The middle point says which of the two arcs on that chord is meant: from a point
            // on the longer one the chord's ends stand less than a right angle apart.
            let major = dot(sub(*a, *m), sub(*b, *m)) > 0.0;
            r * if major { 2.0 * std::f64::consts::PI - 2.0 * half } else { 2.0 * half }
        }
    }
}

/// The length of a tube's centreline.
pub fn length(tube: &Tube) -> f64 {
    tube.path.iter().map(seg_length).sum()
}

/// A lower return's cut stock: its tube between the two elbows and each elbow socket's depth.
pub fn lower_return_cut(run: u32) -> f64 {
    length(tube(&format!("tube-fluid-{run}"))) + 2.0 * stem_elbow().published_socket_insertion_mm
}

/// A prepared pump tube's cut: what the head's clamp holds and what reaches on into its tee.
pub fn pump_tube_cut() -> f64 {
    let first = pump_junctions().next().expect("the pumps have tees");
    let run = CONNECTIONS
        .iter()
        .find(|c| c.made == Made::PumpTube { tee: first })
        .map(|c| c.run)
        .expect("a pump tee takes a pump tube");
    PUMP_TUBE_HELD + length(tube(&format!("tube-fluid-{run}")))
}

/// The NeoFit stem elbow, as its reference parameters state it.
#[derive(Deserialize)]
pub struct StemElbow {
    pub stem_shoulder_x_mm: f64,
    pub published_socket_insertion_mm: f64,
}

pub fn stem_elbow() -> &'static StemElbow {
    static STEM: OnceLock<StemElbow> = OnceLock::new();
    STEM.get_or_init(|| {
        serde_json::from_str(include_str!("../../reference/neofit-stem-elbow/reference-parameters.json"))
            .expect("the stem elbow's parameters parse")
    })
}

/// How much of a stem elbow's stem stands behind its hub, trimmed to seat `stem` mm.
pub fn stem_keep(stem: f64) -> f64 {
    -stem_elbow().stem_shoulder_x_mm + stem
}

fn sub(a: P3, b: P3) -> P3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
fn dot(a: P3, b: P3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
fn cross(a: P3, b: P3) -> P3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
fn norm(a: P3) -> f64 {
    dot(a, a).sqrt()
}
fn distance(a: P3, b: P3) -> f64 {
    norm(sub(a, b))
}
