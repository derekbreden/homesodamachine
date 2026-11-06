//! The shell's walls: the cavity and its corner columns, the lip ring the halves join on, the Y
//! telescope's channel, and the bedding under front-top's grown flanks. The wall faces they
//! stand on are the numbers crate's.
use crate::catalog::running;
use crate::funnel;
use crate::handholds::handhold_backing_end;
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::Y;
use crate::shell::*;
use crate::structure::FUNNEL_SEAT;
pub use crate::faces::*;

/// The lip's ceiling stands this far under the cavity roof, clear of the funnel's seat.
pub const CEILING_LIP_DROP: f64 = FUNNEL_SEAT + funnel::BRIM_T - CEILING_SKIN;

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

/// The Y telescope's own carving, cut last of a front piece's work so the section aft of the
/// mouth runs in the back half's register whatever has fused into that band.
pub fn y_lip_channel(g: &mut Graph, inner: &Bounds, y_joint: f64) -> Shape {
    let [ix0, ix1, _, _, iz0, iz1] = *inner;
    let (y0, y1) = (y_joint, y_joint + LIP_LEN + 1.0);
    let (zlo, zhi) = (iz0 - slab_t() - 1.0, iz1 + CEILING_SKIN + 1.0);
    let west = g.box_([ix0 - 1.0, ix0 + running(), y0, y1, zlo, zhi]);
    let east = g.box_([ix1 - running(), ix1 + 1.0, y0, y1, zlo, zhi]);
    let flanks = g.union(west, &[east]);
    let roof = g.box_([ix0 - 1.0, ix1 + 1.0, y0, y1, iz1 - CEILING_LIP_DROP - running(), zhi]);
    g.union(flanks, &[roof])
}

/// The bedding under each grown flank: from the seam up the wall's face to the rim, sloping in
/// at the relief angle so the flank prints without support.
pub fn flank_bedding_cut(g: &mut Graph, inner: &Bounds, y0: f64, y1: f64, zj: f64) -> Shape {
    let [fx0, fx1] = front_top_flank_face();
    let rim = zj + Z_RISE;
    let [west, east] = [(inner[0], fx0), (inner[1], fx1)].map(|(x_in, x_face)| {
        g.xz_prism(y0, y1, vec![[x_in, zj - 1.0], [x_face, zj - 1.0], [x_face, rim + (x_face - x_in).abs()], [x_in, rim]])
    });
    g.union(west, &[east])
}
