//! The enclosure's construction plans and what evaluates them: the typed operations a recipe
//! records, the numbers each piece's evaluator reads beside its plan, and the kernel calls that
//! make its solids and files.
pub mod corner;
pub mod eval;
pub mod letters;
pub mod numbers;
pub mod ops;
pub mod pieces;
pub mod plan;
pub mod presentation;
pub mod skin;
#[path = "../../nameplate/snap_geometry.rs"]
pub mod snap_geometry;
pub mod sources;
pub mod structure;
pub mod text;
