//! Front-bottom's own wall work: its flanks' grown band, the lands under the collet plate's
//! ends, and the lip it gives up across the pump bay.
use crate::plan::{Bounds, Graph, Shape};
use crate::shell::*;
use crate::spec::ColletPlate;
use crate::walls::{column_pillar, front_bottom_flank_face, lip_face_x};

/// The front-bottom flanks' grown band, slab to seam mouth.
pub fn front_bottom_flank_skin(g: &mut Graph, inner: &Bounds, y_joint: f64, zj: f64) -> Shape {
    let [lx0, lx1] = lip_face_x();
    let [fx0, fx1] = front_bottom_flank_face();
    let west = g.box_([lx0, fx0, inner[2], y_joint, inner[4], zj]);
    let east = g.box_([fx1, lx1, inner[2], y_joint, inner[4], zj]);
    g.union(west, &[east])
}

/// The two lands under the collet plate's ends: each continues the flank skin inboard under
/// the seam plane, its underside rising off the flank at the corbel angle.
pub fn plate_foot(g: &mut Graph, plate: &ColletPlate, zj: f64) -> Shape {
    let [fx0, fx1] = front_bottom_flank_face();
    let ym = (plate.fore_y + plate.aft_y) / 2.0;
    let (y0, y1) = (ym - PLATE_FOOT_Y / 2.0, (ym + PLATE_FOOT_Y / 2.0).max(plate.wall_aft_y));
    let drop = PLATE_FOOT_REACH * PLATE_FOOT_CORBEL_ANGLE.to_radians().tan();
    let feet = [(fx0, 1.0), (fx1, -1.0)].map(|(x_face, into)| {
        let x_in = x_face + into * PLATE_FOOT_REACH;
        g.xz_prism(y0, y1, vec![[x_in, zj], [x_face, zj], [x_face, zj - PLATE_FOOT_T - drop], [x_in, zj - PLATE_FOOT_T]])
    });
    g.union(feet[0], &[feet[1]])
}

/// The front wall's share of the Z lip and its underwall skin, given up across the pump bay's
/// throat; the front pillars keep their wraps.
pub fn front_flat_lip_drop(g: &mut Graph, inner: &Bounds, zj: f64) -> Shape {
    let mut drop = g.box_([inner[0], inner[1], inner[2], inner[2] + WALL, inner[4], zj + Z_RISE + 1.0]);
    for (sx, sy) in COLUMN_CORNERS {
        if sy < 0.0 {
            let pillar = column_pillar(g, inner, sx, sy, zj);
            drop = g.cut(drop, &[pillar]);
        }
    }
    drop
}

/// The Z lip given up on both flanks over the front run, wall to wall and back to the bay
/// bulkhead's aft face.
pub fn flank_lip_drop(g: &mut Graph, inner: &Bounds, plate: &ColletPlate, zj: f64) -> Shape {
    g.box_([inner[0] - WALL - 1.0, inner[1] + WALL + 1.0, inner[2] - WALL - 1.0, plate.wall_aft_y, zj,
            zj + Z_RISE + WALL + 1.0])
}
