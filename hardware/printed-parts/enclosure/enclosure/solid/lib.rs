//! The enclosure's construction plans and what evaluates them: the typed operations a recipe
//! records, the kernel calls that make its solids, and the steps every piece's files share.
pub mod eval;
pub mod letters;
pub mod ops;
pub mod pieces;
pub mod plan;
pub use hsm_print_payload as presentation;
pub mod run;
pub mod skin;
#[path = "../../nameplate/snap_geometry.rs"]
pub mod snap_geometry;
pub mod sources;
pub mod structure;
pub mod text;
