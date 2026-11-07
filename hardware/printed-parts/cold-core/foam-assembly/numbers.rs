//! The foam assembly's numbers: the cold core's casing as the machine seats it, and the cap's
//! conduits as the casing presents them. The casing is its printed pieces in the shell's frame:
//! the foam shell, the equipment lid turned a half turn onto the shell's rim, and the bottom
//! closure under the shell's floor. A conduit is where a line or a cable leaves the stack: its
//! mouth on the lid's face, and the bore or the run below it, which the machine's own run to it
//! continues. The cold core's assembly places the same pieces.
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::{b_fill, cap as frames, routes};
use hsm_foam_cap_numbers as cap;
use hsm_foam_shell_numbers as shell;

/// A point or a direction.
pub type P3 = [f64; 3];

/// A casing piece: its name, its printed file's fine model from the checkout's root, the turn
/// about Z it installs with in degrees, the height its own frame is lifted to, and its colour.
#[derive(Clone, Copy, Debug)]
pub struct Piece {
    pub name: &'static str,
    pub model: &'static str,
    pub turn: f64,
    pub lift: f64,
    pub colour: catalog::Colour,
}

/// The casing: the shell where it is made, the lid with its face on the cap's face, and the
/// bottom closure with its outer face on the stack's floor.
pub fn pieces() -> [Piece; 3] {
    let lid_height = core::foam_cap_lid_height(&cap::fits());
    [
        Piece {
            name: "foam-shell",
            model: "hardware/printed-parts/cold-core/foam-shell/foam-shell.step.npz",
            turn: 0.,
            lift: 0.,
            colour: shell::colour(),
        },
        Piece {
            name: "foam-cap-lid-top",
            model: "hardware/printed-parts/cold-core/foam-cap/foam-cap-lid-top.step.npz",
            turn: 180.,
            lift: cap::face_z() - lid_height,
            colour: cap::colour(),
        },
        Piece {
            name: "foam-cap-bottom",
            model: "hardware/printed-parts/cold-core/foam-cap/foam-cap-bottom.step.npz",
            turn: 0.,
            lift: cap::stack_floor_z(),
            colour: cap::colour(),
        },
    ]
}

// --- The conduits -------------------------------------------------------------------------------

/// How a line or a cable passes the cap below a conduit's mouth.
#[derive(Clone, Debug, PartialEq)]
pub enum Passage {
    /// A straight bore down from the mouth, to its foot under the shell's rim.
    Bore { foot: P3 },
    /// A run's corners up to the mouth, and the bend it turns at.
    Run { points: Vec<P3>, bend: f64 },
}

/// One conduit: its name, its mouth and its passage.
#[derive(Clone, Debug, PartialEq)]
pub struct Conduit {
    pub name: &'static str,
    pub mouth: P3,
    pub passage: Passage,
}

/// How far under the shell's rim a straight bore's foot stands.
pub const BORE_FOOT_DROP: f64 = 1.;

/// The conduits a line climbs in a run of its own, whose corners the core's lines give: the
/// water inlet's and the carbonated water's straight guides, reservoir A's guided fill and
/// reservoir B's fill through its holder.
pub const RUN_CONDUITS: [&str; 4] = ["water-in", "carb-water-out", "reservoir-a-fill", "reservoir-b-fill"];

/// A cap-frame station in the shell's frame: the cap installs spun a half turn.
fn spun(xy: [f64; 2]) -> [f64; 2] {
    [-xy[0], -xy[1]]
}

/// Every conduit, in the order the cap's numbers list them.
pub fn conduits() -> Vec<Conduit> {
    let face = cap::face_z();
    let lines = routes::lines();
    cap::conduits::conduits()
        .into_iter()
        .map(|c| {
            let [x, y] = spun(c.xy);
            let mouth = if c.name == "reservoir-b-fill" {
                frames::world_to_shell(b_fill::passage().entry)
            } else {
                [x, y, face]
            };
            let passage = if let Some(cable) = cable_guides::CABLES.iter().find(|cable| cable.name == c.name)
            {
                let points =
                    cable_guides::corridor(cable, c.xy).into_iter().map(frames::world_to_shell).collect();
                Passage::Run { points, bend: cable_guides::BEND }
            } else if RUN_CONDUITS.contains(&c.name) {
                let line = lines.iter().find(|l| l.name == c.name).expect("a run conduit's line");
                Passage::Run { points: line.points.clone(), bend: routes::bend_radius() }
            } else {
                Passage::Bore { foot: [x, y, core::FOAM_SHELL_OUTER_HEIGHT - BORE_FOOT_DROP] }
            };
            Conduit { name: c.name, mouth, passage }
        })
        .collect()
}

/// The cable passages through the cap, in the enclosure's frame: each rises from its floor entry
/// below the cup, crosses the cup on one storey to under its guide on the lid's face, and leaves
/// past the face. The cap cuts the same corridors through its cup and lid.
pub mod cable_guides {
    use super::{P3, cap, core, frames};

    /// A cable passage's plan: straight across to its guide, or out along X and then along Y.
    #[derive(Clone, Copy, Debug, PartialEq, Eq)]
    pub enum Plan {
        Direct,
        Dogleg,
    }

    /// A cable conduit: its name, its floor entry in the cap's frame, and its plan.
    #[derive(Clone, Copy, Debug)]
    pub struct Cable {
        pub name: &'static str,
        pub floor_xy: [f64; 2],
        pub plan: Plan,
    }

    /// Reservoir A's reed ribbon, over its reed column, and the shared sensor loom.
    pub const CABLES: [Cable; 2] = [
        Cable {
            name: "reed-cable-a",
            floor_xy: [-core::REED_CABLE_CONDUIT_X, -core::REED_CABLE_CONDUIT_Y],
            plan: Plan::Direct,
        },
        Cable { name: "sensor-cable", floor_xy: core::SENSOR_CABLE_CONDUIT_XY, plan: Plan::Dogleg },
    ];

    /// The bend a printed cable passage turns at; it says nothing of the cable's own.
    pub const BEND: f64 = 5.5;
    /// The storey a passage crosses the cup on, under the lid's underside.
    pub const CROSSING_DEPTH: f64 = 6.6;
    /// How far under the cup's floor a passage starts, and past the lid's face it ends.
    pub const START_DROP: f64 = 1.;
    pub const END_RISE: f64 = 2.;

    /// `cable`'s corridor up to the conduit at `upper_xy` in the cap's frame.
    pub fn corridor(cable: &Cable, upper_xy: [f64; 2]) -> Vec<P3> {
        let plan_at = |xy: [f64; 2]| {
            let [x, y, _] = frames::cap_to_world([xy[0], xy[1], 0.]);
            [x, y]
        };
        let (lower, upper) = (plan_at(cable.floor_xy), plan_at(upper_xy));
        let lid_bottom = frames::cap_lid_pose().translation[2];
        let cup_bottom = lid_bottom - core::top_cap_height(&cap::fits());
        let crossing = lid_bottom - CROSSING_DEPTH;
        let top = frames::cap_face_z() + END_RISE;
        let at = |xy: [f64; 2], z: f64| [xy[0], xy[1], z];
        let distance = 0f64.hypot(lower[0] - upper[0]).hypot(lower[1] - upper[1]);
        if distance < 1e-9 {
            return vec![at(lower, cup_bottom - START_DROP), at(upper, top)];
        }
        let plan = match cable.plan {
            Plan::Direct => vec![lower, upper],
            Plan::Dogleg => vec![lower, [lower[0], upper[1]], upper],
        };
        let mut points = vec![at(lower, cup_bottom - START_DROP)];
        points.extend(plan.into_iter().map(|xy| at(xy, crossing)));
        points.push(at(upper, top));
        points
    }
}
