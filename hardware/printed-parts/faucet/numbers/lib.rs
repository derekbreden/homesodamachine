//! The faucet's numbers, in millimetres, as its parts take them: the tubes' centrelines through
//! it, what its stack shares at each interface, the display cover's snap, the shell that frames
//! the rest, the stack the base stands on above the counter, the countertop it clamps through, and
//! the catalogs' colours and fits.
//! Each part's own numbers that no other part takes stay with that part.
pub mod catalog;
pub mod countertop;
pub mod interface;
pub mod paths;
pub mod shell;
pub mod snap;
pub mod stack;

pub type P2 = [f64; 2];
pub type P3 = [f64; 3];
/// A body's colour, linear RGB, as its files carry it.
pub type Color = [f64; 3];
