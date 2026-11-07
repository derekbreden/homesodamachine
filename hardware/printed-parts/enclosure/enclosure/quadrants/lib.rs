//! The construction two or more quadrants share: the walls and the lip ring they join on, the Z
//! rails, the Y seam's knuckle stacks, the seam and column reliefs, the floor's features, the
//! vents, the valve trays, the route snaps, the funnel's cut and receivers, the display's cut,
//! the tops' above-core wells and funnel seat, the bottoms' handholds, and the stages each
//! quadrant's pipeline takes in turn. The numbers crate's modules and the plan stand here under
//! their own names, as the recipes name them.
pub use hsm_enclosure_numbers::{catalog, disposal, faces, field, junctions, layout, pump, quadrant, rear_wall, shell, spec, structure};
pub use hsm_enclosure_solid::plan;

pub mod above;
pub mod columns;
pub mod display;
pub mod floor;
pub mod funnel;
pub mod handholds;
pub mod piece;
pub mod rails;
pub mod routes;
pub mod seam;
pub mod seat;
pub mod shapes;
pub mod valves;
pub mod vent;
pub mod walls;
pub mod ystacks;
