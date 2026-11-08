//! The hsm CAD kernel: mesh-native solids that record where every face came from.
//!
//! A `Solid` is a closed triangle mesh in canonical order. Every triangle names a `Face`
//! record: the exact surface it lies on (plane, cylinder, cone, sphere, torus, or a free
//! surface), the builder that made it, the generator line that asked for it (`#[track_caller]`),
//! and the boolean that brought it into the solid, if one did.
//!
//! Profiles are drawn exactly (`profile`) — lines, arcs, circles, Béziers, corner fillets and
//! offsets — on a workplane (`Plane`), and every builder cuts them into points by one rule
//! (`rule`), so the same surface always gets the same vertices and coincident faces of two
//! solids meet point for point.
//!
//! ```no_run
//! use hsm_kernel::*;
//!
//! # fn main() -> anyhow::Result<()> {
//! let section = Profile::polygon(&[v2(0.0, 0.0), v2(10.0, 0.0), v2(10.0, 4.0), v2(0.0, 4.0)]);
//! let bar = Plane::YZ.at(v3(-9.0, 0.0, 0.0)).extrude(&section, 18.0)?;
//! let slot = Plane::XY.at(v3(0.0, 5.0, 2.0)).cuboid(20.0, 2.0, 2.0);
//! let part = bar.cut(&slot)?;
//! println!("{:.3} mm³", part.volume());
//! write_payload("part.step.mesh", &[Body { name: "part", color: None, solid: &part }], None, None)?;
//! # Ok(()) }
//! ```
//!
//! A solid's edges are picked with CadQuery's selectors (`edge`) and rounded or chamfered
//! (`round`).
//!
//! Booleans run on Manifold (the `manifold` feature, on by default). Without it the kernel is
//! pure Rust and builds for wasm32; its booleans then return an error.
pub mod boolean;
pub mod build;
pub mod dxf;
pub mod edge;
pub mod face;
pub mod import;
#[path = "../../geometry/src/scene.rs"]
pub mod scene;
pub mod mapped;
pub mod mass;
pub mod math;
pub mod part;
pub mod plane;
pub mod profile;
pub mod reads;
pub mod round;
pub mod rule;
pub mod screw;
pub mod sketch_hull;
pub mod solid;
pub mod spline;
pub mod step;
pub mod sweep;
pub mod text;
pub mod thru;
pub mod topo;
pub mod triangulate;
pub mod write;

pub use boolean::{FUZZ, Op};
pub use edge::{Edge, Edges};
pub use face::{Face, Source, Src, Surface, SurfaceKey, Via, file_src, src_line};
pub use import::Imported;
pub use mass::Mass;
pub use math::{Affine, V2, V3, v2, v3};
pub use plane::Plane;
pub use profile::{Curve, Loop, Pen, Profile, Region, Seg};
pub use rule::{ANGULAR, GRID, LINEAR, TOLERANCE};
pub use sketch_hull::{HullEdge, Wrapped, hull_edges, hull_loop, hull_section};
pub use solid::{Bounds, Solid};
pub use spline::Spline;
pub use step::{model_bytes, step_bytes, write_model, write_step};
pub use sweep::{Leg, Path};
pub use text::{Font, HAlign, Kind, VAlign};
pub use thru::{LoftEdge, LoftSection, SmoothLoft, compatible};
pub use write::{Body, glb_bytes, payload_bytes, stl_bytes, threemf_bytes, write_3mf, write_glb, write_payload, write_stl};
