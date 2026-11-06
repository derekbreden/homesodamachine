//! Front-top's own construction: its grown flanks, the bulkhead and display backing over the pump
//! bay, the bay floor and the dock's cuts, the funnel's seat ledges, the valve coils' flank
//! pockets, the integral pump mount's cuts and receivers, and the analytic front corner its
//! evaluator draws.
use crate::catalog::running;
use crate::dock;
use crate::walls::{CEILING_LIP_DROP, flank_bedding_cut};
use crate::funnel::{self, BODY_WIDTH};
use crate::mount;
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::sorted;
use crate::shell::*;
use crate::spec::Box;
use crate::structure::{ANGLE, FLAT, FRONT_RADIUS, FUNNEL_SEAT, SIDE_RADIUS, TOP_RADIUS, profile};
use crate::walls::front_top_flank_face;
use serde::{Deserialize, Serialize};
use std::sync::OnceLock;

/// The flanks grown inward over the rail rim, from the front wall to the end of the Y lip, on
/// their bedding.
pub fn flanks(g: &mut Graph, inner: &Bounds, outer: &Bounds, y_joint: f64, zj: f64) -> Shape {
    let [fx0, fx1] = front_top_flank_face();
    let (y0, y1) = (outer[2] - 1.0, y_joint + LIP_LEN);
    let rim = zj + Z_RISE;
    let [west, east] = [(inner[0], fx0), (inner[1], fx1)]
        .map(|(x_in, x_face)| g.box_([x_in.min(x_face), x_in.max(x_face), y0, y1, rim, inner[5]]));
    let band = g.union(west, &[east]);
    let bedding = flank_bedding_cut(g, inner, y0 - 1.0, y1 + 1.0, zj);
    g.cut(band, &[bedding])
}

/// The bulkhead closing the pump bay over the tee wall, then the ridge wall standing from the
/// plate up the funnel frame's front to the roof, the display housing's backing.
pub fn bulkhead_and_ridge(g: &mut Graph, piece: Shape, b: &Box) -> Shape {
    let (inner, outer, plate) = (&b.inner, &b.outer, &b.pack.collet_plate);
    let bay_top = b.pump_bay[2];
    let bulkhead = g.box_([inner[0], inner[1], shell().bay_back_y(plate), plate.wall_aft_y, Z_SEAM, bay_top]);
    let piece = g.union(piece, &[bulkhead]);
    let (fore, root) = (plate.aft_y, plate.wall_aft_y);
    let face = funnel::housing_back_y(b.pack.funnel[1]);
    let rise = (face - root).abs();
    let mut section = vec![[fore, bay_top], [root, bay_top]];
    if rise > 1e-9 {
        section.push([face, bay_top + rise]);
    }
    section.extend([[face, outer[5]], [fore, outer[5]]]);
    let slab = g.yz_prism(inner[0], inner[1], section);
    let silhouette = g.silhouette(*outer);
    let mut backing = g.intersect(slab, &[silhouette]);
    if !b.pack.pump_trays.is_empty() {
        let keep = g.box_([inner[0], inner[1], outer[2] - 1.0, funnel::housing_back_y(funnel::CENTER_Y), outer[4] - 1.0,
                           outer[5] + 1.0]);
        backing = g.intersect(backing, &[keep]);
    }
    g.union(piece, &[backing])
}

/// Each rear valve's return channel down through the piece, then the bay floor under the heads,
/// wall to wall from the front plane to the tee wall.
pub fn dock_and_bay(g: &mut Graph, mut piece: Shape, b: &Box) -> Shape {
    let (inner, plate) = (&b.inner, &b.pack.collet_plate);
    for channel in dock::return_clearances(g, plate) {
        piece = g.cut(piece, &[channel]);
    }
    let (z0, z1) = shell().bay_floor_z(&b.pack.pump_trays);
    let floor = g.box_([inner[0], inner[1], FRONT_PLANE_Y, plate.wall_aft_y, z0, z1]);
    g.union(piece, &[floor])
}

/// The corbels under the funnel seat's ledges along both walls: under the frame's body ahead of
/// the funnel's centre, under the Y stacks' plumb aft of it, each rising as far as it reaches out, up to the
/// shoulder under the ceiling lip.
pub fn seat_ledge_corbels(g: &mut Graph, mut piece: Shape, b: &Box) -> Shape {
    let (inner, outer) = (&b.inner, &b.outer);
    let cy = b.pack.funnel[1];
    let floor = funnel::seat_z(outer) - FUNNEL_SEAT;
    let reach = BODY_WIDTH / 2.0 + slide_slip();
    let plumb = inner[1] - Y_STACK_HIGH_DEPTH;
    let shoulder = inner[5] - CEILING_LIP_DROP - WALL - running();
    let front = funnel::housing_back_y(funnel::CENTER_Y);
    for (wall_x, sx) in [(inner[1], 1.0), (inner[0], -1.0)] {
        for (ya, yb, x_in) in [(front, cy, reach), (cy, b.y_joint, plumb)] {
            let corbel = g.xz_prism(ya, yb, vec![
                [sx * x_in, floor],
                [wall_x, floor],
                [wall_x, shoulder + plumb - wall_x.abs()],
                [sx * x_in, shoulder + plumb - x_in],
            ]);
            piece = g.union(piece, &[corbel]);
        }
    }
    piece
}

/// The cartridge's loading opening, then the dock's holes and bores through the tee wall.
pub fn loading_and_dock_cuts(g: &mut Graph, mut piece: Shape, b: &Box) -> Shape {
    let opening = mount::loading_opening(g, b);
    piece = g.cut(piece, &[opening]);
    for cut in dock::wall_cuts(g, &b.pack.collet_plate) {
        piece = g.cut(piece, &[cut]);
    }
    piece
}

/// Each valve coil's pocket into the flank it stands against: from the flank's face to the
/// pocket's floor, its roof rising as far as it runs into the wall.
pub fn flank_pockets(g: &mut Graph, mut piece: Shape, pockets: &[(String, f64, f64, f64, f64, f64, f64)]) -> Shape {
    for (name, x0, x1, y0, y1, z0, z1) in pockets {
        let side = if x0 + x1 > 0.0 { 1.0 } else { -1.0 };
        let (face, floor) = sorted(x0.abs(), x1.abs());
        let depth = floor - face;
        let remaining = APPLIANCE_WIDTH / 2.0 - floor - FLUTE_DEPTH;
        assert!(remaining >= WALL - STATED_BOUND_TOL, "{name} flank pocket leaves only {remaining} mm behind fluting");
        let pocket = g.xz_prism(*y0, *y1, vec![
            [side * (face - 1.0), *z0],
            [side * floor, *z0],
            [side * floor, *z1],
            [side * (face - 1.0), z1 + depth + 1.0],
        ]);
        piece = g.cut(piece, &[pocket]);
    }
    piece
}

/// The integral pump mount's cuts, then the retainer's receivers rebuilt into both flanks.
pub fn pump_mount_cuts(g: &mut Graph, mut piece: Shape, b: &Box) -> Shape {
    for cut in mount::fixed_cuts(g, b) {
        piece = g.cut(piece, &[cut]);
    }
    mount::snap_receivers(g, b, piece)
}

#[derive(Deserialize, PartialEq)]
struct Domain {
    front_radius_mm: f64,
    side_radius_mm: f64,
    top_radius_mm: f64,
    angle_deg: f64,
    display_flat_mm: f64,
}

#[derive(Deserialize)]
struct Controls {
    domain: Domain,
    surfaces: Vec<CornerSurface>,
}

fn controls() -> &'static Controls {
    static CONTROLS: OnceLock<Controls> = OnceLock::new();
    CONTROLS.get_or_init(|| {
        serde_json::from_str(include_str!("../front-corner-controls.json")).expect("the front corner's controls parse")
    })
}

/// One front corner's frame: its origin and the hand of its X axis.
#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct CornerFrame {
    pub origin: [f64; 3],
    pub x_sign: f64,
}

/// One rational B-spline patch of the retained front corner, in its unit frame.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CornerSurface {
    pub degree: [usize; 2],
    pub knots: [Vec<f64>; 2],
    pub multiplicities: [Vec<usize>; 2],
    pub poles: Vec<Vec<[f64; 3]>>,
    pub weights: Vec<Vec<f64>>,
    pub source_step_entity: u64,
}

/// The analytic front corner drawn on front-top's rounded body, scaled into each frame.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct FrontCorners {
    pub frames: Vec<CornerFrame>,
    pub scale_mm: f64,
    pub surfaces: Vec<CornerSurface>,
}

/// The retained analytic front corner, its unit patches placed on both standing rounds' centres
/// at the profile's foot, the west one mirrored.
pub fn front_corners(outer: &Bounds) -> FrontCorners {
    let c = controls();
    let live = Domain {
        front_radius_mm: FRONT_RADIUS,
        side_radius_mm: SIDE_RADIUS,
        top_radius_mm: TOP_RADIUS,
        angle_deg: ANGLE,
        display_flat_mm: FLAT,
    };
    assert!(c.domain == live && outer[1] - outer[0] > 4.0 * FRONT_RADIUS,
            "the front corner is outside its retained analytic parameter domain");
    let foot = profile(outer).foot[1];
    FrontCorners {
        frames: vec![
            CornerFrame { origin: [outer[0] + FRONT_RADIUS, outer[2] + FRONT_RADIUS, foot], x_sign: -1.0 },
            CornerFrame { origin: [outer[1] - FRONT_RADIUS, outer[2] + FRONT_RADIUS, foot], x_sign: 1.0 },
        ],
        scale_mm: SIDE_RADIUS,
        surfaces: c.surfaces.clone(),
    }
}
