//! The shell's walls: the cavity and its corner columns, the lip ring the halves join on, and the
//! flank skins that thicken each quadrant's side walls.
use crate::catalog::running;
use crate::handholds::handhold_backing_end;
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::Y;
use crate::shell::*;
use crate::spec::ColletPlate;

pub fn interior_x() -> [f64; 2] {
    [-(APPLIANCE_WIDTH / 2.0 - WALL), APPLIANCE_WIDTH / 2.0 - WALL]
}

fn flank_face(flank_t: f64) -> [f64; 2] {
    let [ix0, ix1] = interior_x();
    let grown = flank_t - WALL;
    [ix0 + grown, ix1 - grown]
}

pub fn back_top_flank_face() -> [f64; 2] {
    flank_face(BACK_TOP_FLANK_T)
}
pub fn back_bottom_flank_face() -> [f64; 2] {
    flank_face(BACK_BOTTOM_FLANK_T)
}
pub fn front_bottom_flank_face() -> [f64; 2] {
    flank_face(FRONT_BOTTOM_FLANK_T)
}
pub fn front_top_flank_face() -> [f64; 2] {
    flank_face(FRONT_TOP_FLANK_T)
}

/// The lip's inner face: one wall in from the interior.
pub fn lip_face_x() -> [f64; 2] {
    let [ix0, ix1] = interior_x();
    [ix0 + WALL, ix1 - WALL]
}

/// Where the back flanks start behind the Y joint's lip and its seam margin.
pub fn back_flank_start(y_joint: f64) -> f64 {
    y_joint + LIP_LEN + Z_LIP_Y_MARGIN
}

pub fn column_arc(inner: &Bounds, sx: f64, sy: f64) -> [f64; 2] {
    [if sx < 0.0 { inner[0] } else { inner[1] }, if sy < 0.0 { inner[2] } else { inner[3] }]
}

/// The solid column standing on one cavity corner, grown by `grow`.
pub fn corner_column(g: &mut Graph, inner: &Bounds, sx: f64, sy: f64, grow: f64, z: [f64; 2]) -> Shape {
    let [px, py] = column_arc(inner, sx, sy);
    g.zcyl(COLUMN_ROUND + grow, px, py, z[0], z[1])
}

/// The cavity's air, inset from the interior, with the corner columns left standing.
pub fn cavity(g: &mut Graph, inner: &Bounds, inset: f64, z: Option<[f64; 2]>) -> Shape {
    let [z0, z1] = z.unwrap_or([inner[4], inner[5]]);
    let stock = g.box_([inner[0] + inset, inner[1] - inset, inner[2] + inset, inner[3] - inset, z0, z1]);
    let mut air = g.rounded(stock, CORNER_ROUND - WALL - inset);
    for (sx, sy) in COLUMN_CORNERS {
        let column = corner_column(g, inner, sx, sy, inset, [z0 - 1.0, z1 + 1.0]);
        air = g.cut(air, &[column]);
    }
    air
}

/// One wall's band inside the cavity over a Z span.
pub fn lip_band(g: &mut Graph, inner: &Bounds, z: [f64; 2], inset: f64) -> Shape {
    let band = cavity(g, inner, inset, Some(z));
    let core = cavity(g, inner, WALL, Some([z[0] - 1.0, z[1] + 1.0]));
    g.cut(band, &[core])
}

/// A corner column with the wall band wrapped round it up to the rail heads.
pub fn column_pillar(g: &mut Graph, inner: &Bounds, sx: f64, sy: f64, zj: f64) -> Shape {
    let z = [inner[4] - 1.0, inner[5] + 1.0];
    let post = corner_column(g, inner, sx, sy, 0.0, z);
    let band = lip_band(g, inner, [inner[4], zj + Z_RISE], 0.0);
    let reach = corner_column(g, inner, sx, sy, WALL, z);
    let wrap = g.intersect(band, &[reach]);
    g.union(post, &[wrap])
}

/// The front floor's tongue under the Y joint, and the relief the back floor takes for it.
pub fn floor_tongue(g: &mut Graph, inner: &Bounds, y_joint: f64) -> (Shape, Shape) {
    let zbed = inner[4] - slab_t();
    let root = y_joint - 1.0;
    let tongue = g.box_([inner[0] + running(), inner[1] - running(), root,
                         handhold_backing_end(y_joint, Y::Front), zbed, inner[4]]);
    let relief = g.box_([inner[0], inner[1], root, handhold_backing_end(y_joint, Y::Back), zbed - 1.0, inner[4]]);
    (tongue, relief)
}

/// The lip band over a Z span, open across the Y gap the other half's lip fills.
pub fn lip_ring(g: &mut Graph, inner: &Bounds, gap: [f64; 2], z0: f64, z1: f64, inset: f64) -> Shape {
    let ring = lip_band(g, inner, [z0, z1], inset);
    let open = g.box_([inner[0] - 1.0, inner[1] + 1.0, gap[0], gap[1], z0 - 1.0, z1 + 1.0]);
    g.cut(ring, &[open])
}

/// The bottom pieces' wall band under the Z joint, open where the lip crosses the Y joint.
pub fn lip_underwall(g: &mut Graph, inner: &Bounds, y_joint: f64, zj: f64) -> Shape {
    lip_ring(g, inner, [y_joint, y_joint + LIP_LEN + Z_LIP_Y_MARGIN], inner[4], zj, 0.0)
}

/// The back-bottom flanks' grown band, behind the lip.
pub fn back_bottom_flank_skin(g: &mut Graph, inner: &Bounds, y_joint: f64, zj: f64) -> Shape {
    let [lx0, lx1] = lip_face_x();
    let [fx0, fx1] = back_bottom_flank_face();
    let y0 = back_flank_start(y_joint);
    let west = g.box_([lx0, fx0, y0, inner[3], inner[4], zj]);
    let east = g.box_([fx1, lx1, y0, inner[3], inner[4], zj]);
    g.union(west, &[east])
}

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
