//! The front half the front pieces are cut from: the shell ahead of the Y joint less the
//! display housing's keepout, filled with the pump mount's stock, with the fridge reliefs, the
//! rear lip, the display facet and the display and funnel cuts.
use crate::catalog::running;
use crate::display;
use crate::funnel;
use crate::mount;
use crate::piece::{Build, build_piece};
use crate::plan::{Bounds, Graph, P3, Shape};
use crate::quadrant::{Quadrant, Y};
use crate::shell::*;
use crate::spec::Box;
use crate::structure::{FUNNEL_SEAT, profile};
use crate::walls::{cavity, floor_tongue};

/// The roof skin over the lip's ceiling run.
pub const CEILING_SKIN: f64 = 3.0;
/// The lip's ceiling stands this far under the cavity roof, clear of the funnel's seat.
pub const CEILING_LIP_DROP: f64 = FUNNEL_SEAT + funnel::BRIM_T - CEILING_SKIN;
/// A stated bound within this of zero reads as the pack's floor.
pub const STATED_BOUND_TOL: f64 = 1e-6;

/// The half-space on a plane's positive side: a square four extents across, one extent deep.
pub fn halfspace(g: &mut Graph, origin: P3, normal: P3, extent: f64) -> Shape {
    assert!(normal[0].abs() <= 1e-10, "the front display plane no longer has its declared X direction");
    let length = (normal[0] * normal[0] + normal[1] * normal[1] + normal[2] * normal[2]).sqrt();
    let (ny, nz) = (normal[1] / length, normal[2] / length);
    let section = [(-2.0 * extent, 0.0), (2.0 * extent, 0.0), (2.0 * extent, extent), (-2.0 * extent, extent)]
        .map(|(s, d)| [origin[1] + s * nz + d * ny, origin[2] - s * ny + d * nz])
        .to_vec();
    g.yz_prism(origin[0] - 2.0 * extent, origin[0] + 2.0 * extent, section)
}

fn extent(outer: &Bounds) -> f64 {
    (outer[1] - outer[0]).max(outer[3] - outer[2]).max(outer[5] - outer[4]) + 100.0
}

/// The display facet's air: everything outside its plane, wall to wall.
pub fn facet_wedge(g: &mut Graph, outer: &Bounds) -> Shape {
    let p = profile(outer);
    halfspace(g, p.origin, p.normal, extent(outer))
}

/// The relief pockets in the front wall: a box to each region's floor under a ceiling rising at
/// the relief chamfer, and where a region reaches under the cavity floor, a ramp up to it.
/// `slip` closes each pocket in on its standing faces and stands its floor aft.
pub fn front_relief_cuts(g: &mut Graph, inner: &Bounds, regions: &[[f64; 5]], slip: f64) -> Vec<Shape> {
    let (iy0, iz0) = (inner[2], inner[4]);
    let mut cuts = Vec::new();
    for &[x0, x1, z0, z1, floor] in regions {
        let z0 = if z0 <= STATED_BOUND_TOL { z0.min(iz0) } else { z0 };
        let (x0, x1, z0, z1) = (x0 + slip, x1 - slip, z0 + slip, z1 - slip);
        let floor = floor + slip;
        let depth = iy0 - floor;
        cuts.push(g.box_([x0, x1, floor, iy0 + 1.0, z0.max(iz0), z1]));
        cuts.push(g.yz_prism(x0, x1, vec![[floor, z1], [iy0 + 1.0, z1 + depth + 1.0], [iy0 + 1.0, z1]]));
        if z0 < iz0 {
            cuts.push(g.yz_prism(x0, x1, vec![[floor, z0], [iy0, z0], [iy0 + (iz0 - z0), iz0], [floor, iz0]]));
        }
    }
    cuts
}

/// The front half's rear lip: a wall band from one wall inside the body to the shoulder at the
/// joint, then three running-fit faces telescoping into the back half.
pub fn front_lip(g: &mut Graph, inner: &Bounds, y_joint: f64) -> Shape {
    let [ix0, ix1, _, _, iz0, iz1] = *inner;
    let (y0, y1) = (y_joint - WALL, y_joint + LIP_LEN);
    let lip_top = iz1 - CEILING_LIP_DROP;
    let shoulder = g.box_([ix0, ix1, y0, y_joint, iz0, iz1]);
    let tongue = g.box_([ix0 + running(), ix1 - running(), y_joint, y1, iz0, lip_top - running()]);
    let bore = g.box_([ix0 + WALL + running(), ix1 - WALL - running(), y0 - 1.0, y1 + 1.0, iz0 - 1.0,
                       lip_top - WALL - running()]);
    let lip = g.union(shoulder, &[tongue]);
    g.cut(lip, &[bore])
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

/// The front half: the shell ahead of the joint, the display housing's slab behind the facet
/// kept solid back to the funnel frame, the pump mount's stock, and the front's own cuts.
pub fn front_half(g: &mut Graph, b: &Box, silhouette: Shape) -> Shape {
    let (inner, outer) = (&b.inner, &b.outer);
    let p = profile(outer);
    let e = extent(outer);
    let back: P3 = std::array::from_fn(|k| p.origin[k] - display::FACET_THICKNESS * p.normal[k]);
    let behind = halfspace(g, back, p.normal, e);
    let reach = g.box_([outer[0] - e, outer[1] + e, outer[2] - e, funnel::housing_back_y(b.pack.funnel[1]),
                        outer[4] - e, outer[5] + e]);
    let keepout = g.intersect(behind, &[reach]);
    let air = cavity(g, inner, 0.0, None);
    let air = g.cut(air, &[keepout]);
    let fill = mount::stock(g, b, silhouette);
    let air = g.cut(air, &[fill]);
    let shell = g.cut(silhouette, &[air]);
    let band = g.box_([outer[0], outer[1], outer[2], b.y_joint, outer[4], outer[5]]);
    let mut front = g.intersect(shell, &[band]);
    for relief in front_relief_cuts(g, inner, &FRIDGE_RELIEFS, 0.0) {
        front = g.cut(front, &[relief]);
    }
    let lip = front_lip(g, inner, b.y_joint);
    let (tongue, _) = floor_tongue(g, inner, b.y_joint);
    front = g.union(front, &[lip, tongue]);
    let wedge = facet_wedge(g, outer);
    front = g.cut(front, &[wedge]);
    let display = display::display_cut(g, outer);
    front = g.cut(front, &[display]);
    let funnel = funnel::funnel_cut(g, inner, outer, b.pack.funnel);
    front = g.cut(front, &[funnel]);
    g.intersect(front, &[silhouette])
}

/// A front quadrant's construction: the front half, then the quadrant's features.
pub fn construction(b: &Box, q: Quadrant) -> (Graph, Shape) {
    assert!(q.y == Y::Front, "{} is cut from the back half", q.name());
    let mut g = Graph::new();
    let silhouette = g.silhouette(b.outer);
    let half = front_half(&mut g, b, silhouette);
    let piece = build_piece(&mut g, &Build { b, q, silhouette, half });
    (g, piece)
}
