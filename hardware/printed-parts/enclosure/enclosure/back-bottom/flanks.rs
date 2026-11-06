//! Back-bottom's own wall work: its flanks' grown band behind the lip.
use crate::plan::{Bounds, Graph, Shape};
use crate::walls::{back_bottom_flank_face, back_flank_start, lip_face_x};

/// The back-bottom flanks' grown band, behind the lip.
pub fn back_bottom_flank_skin(g: &mut Graph, inner: &Bounds, y_joint: f64, zj: f64) -> Shape {
    let [lx0, lx1] = lip_face_x();
    let [fx0, fx1] = back_bottom_flank_face();
    let y0 = back_flank_start(y_joint);
    let west = g.box_([lx0, fx0, y0, inner[3], inner[4], zj]);
    let east = g.box_([fx1, lx1, y0, inner[3], inner[4], zj]);
    g.union(west, &[east])
}
