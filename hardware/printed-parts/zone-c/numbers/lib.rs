//! Zone C's numbers, in millimetres, as its parts take them: the cast silicone funnel, the elbow
//! cradle that holds its drain elbow, the frame it drops into under the roof, the lift-off cover,
//! the casting mold, and the catalogs' colours. Each part names the numbers it takes from another.
pub mod catalog;
pub mod cover;
pub mod cradle;
pub mod frame;
pub mod funnel;
pub mod mold;

pub type P2 = (f64, f64);
pub type Color = [f64; 3];
