//! The Z rails that hook each top piece onto its bottom piece: the heads the bottoms carry over
//! the seam, and the runs they slide along.
use crate::catalog::supported;
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::{Y, sorted};
use crate::shell::*;
use crate::walls::*;

/// One flank's rail run: its wall, the side it reaches in from, and its Y span.
#[derive(Clone, Copy, Debug)]
pub struct Run {
    pub x_in: f64,
    pub sx: f64,
    pub y0: f64,
    pub y1: f64,
    pub lane_aft: f64,
}

pub fn z_rail_runs(inner: &Bounds, y_joint: f64, col: Y) -> [Run; 2] {
    [(inner[0], 1.0), (inner[1], -1.0)].map(|(x_in, sx)| match col {
        Y::Front => Run {
            x_in,
            sx,
            y0: front_rail_start_y(inner[2]),
            y1: y_joint - WALL - Z_LIP_Y_MARGIN,
            lane_aft: y_joint + LIP_LEN + Z_LIP_Y_MARGIN,
        },
        Y::Back => Run {
            x_in,
            sx,
            y0: inner[3] - CORNER_ROUND,
            y1: y_joint + LIP_LEN + Z_LIP_Y_MARGIN,
            lane_aft: y_joint - 1.0,
        },
    })
}

/// How far the top piece slides along its rails before the stops meet.
pub fn z_rail_travel(inner: &Bounds, y_joint: f64, col: Y) -> f64 {
    let runs = z_rail_runs(inner, y_joint, col);
    runs.iter().map(|r| (r.y1 - r.y0).abs()).fold(f64::NEG_INFINITY, f64::max) - RAIL_STOP_LEN + RAIL_ENTRY
}

/// The rail's foot face: the thinner of the column's two flank faces.
pub fn rail_nominal_foot_face(col: Y, sx: f64) -> f64 {
    let (top, bottom) = match col {
        Y::Front => (front_top_flank_face(), front_bottom_flank_face()),
        Y::Back => (back_top_flank_face(), back_bottom_flank_face()),
    };
    if sx > 0.0 { top[0].min(bottom[0]) } else { top[1].max(bottom[1]) }
}

pub fn rail_hook_lap(col: Y) -> f64 {
    match col {
        Y::Back => BACK_HOOK_LAP,
        Y::Front => FRONT_HOOK_LAP,
    }
}

/// A rail's X stations: the hook's lap, the foot face, the arm's face and the arm's end.
#[derive(Clone, Copy, Debug)]
pub struct RailX {
    pub hook: f64,
    pub foot: f64,
    pub arm: f64,
    pub arm_end: f64,
}

pub fn rail_x(sx: f64, col: Y) -> RailX {
    let foot = rail_nominal_foot_face(col, sx);
    let hook = foot - sx * rail_hook_lap(col);
    let arm = foot + sx * slide_slip();
    RailX { hook, foot, arm, arm_end: arm + sx * HOOK_ARM }
}

/// The top piece's rail channel: its open face, the foot face and its far wall.
pub fn rail_channel_span(sx: f64, col: Y) -> [f64; 3] {
    let x = rail_x(sx, col);
    let open = x.hook - sx * slide_slip();
    let arm_clear = x.arm_end + sx * slide_slip();
    let far = if col == Y::Back { arm_clear } else { 2.0 * x.foot - open };
    assert!(
        (far - x.foot) * sx + 1e-6 >= (arm_clear - x.foot) * sx,
        "the rail channel ends before the arm's running-clear envelope"
    );
    [open, x.foot, far]
}

/// The catch's air over the hook: running clearance plus each supported face's allowance.
pub fn rail_catch_air(col: Y) -> f64 {
    let supported_faces = if col == Y::Back { 2.0 } else { 1.0 };
    slide_slip() + supported_faces * supported()
}

/// The hooked heads a bottom piece carries over the seam on each flank.
pub fn z_rail_heads(
    g: &mut Graph,
    inner: &Bounds,
    y_joint: f64,
    zj: f64,
    col: Y,
) -> Shape {
    let z_foot = zj + HOOK_FOOT;
    let rim = zj + Z_RISE;
    let catch_z = z_foot + rail_catch_air(col);
    assert!(rim - catch_z >= WALL, "a supported Z-rail catch leaves less than one wall of head stock");
    let mut out: Option<Shape> = None;
    for run in z_rail_runs(inner, y_joint, col) {
        let sx = run.sx;
        let sy = if run.y1 > run.y0 { 1.0 } else { -1.0 };
        let y0 = if col == Y::Front { run.y0 + slide_slip() } else { run.y0 };
        let y1 = run.y1;
        let x = rail_x(sx, col);
        let arm = g.xz_prism(y0, y1, vec![[x.arm, zj], [x.arm, catch_z], [x.hook, catch_z], [x.hook, rim],
                                          [x.arm_end, rim], [x.arm_end, zj]]);
        let x_uw = rail_nominal_foot_face(col, sx) - sx * 0.5;
        let flare = g.xz_prism(y0, y1, vec![[x_uw, zj], [x.arm_end, zj], [x_uw, zj - rail_flare_drop()]]);
        let arm = g.union(arm, &[flare]);
        let lead = g.xy_prism(z_foot - 1.0, rim + 1.0, vec![[x.arm, y0], [x.hook - sx, y0],
                                                            [x.hook - sx, y0 + sy * RAIL_LEAD]]);
        let arm = g.cut(arm, &[lead]);
        let (yb0, yb1) = sorted(y1 - sy * (RAIL_STOP_LEN - slide_slip()), y1);
        let block = g.box_([x.hook.min(x.arm_end), x.hook.max(x.arm_end), yb0, yb1, zj, rim]);
        let head = g.union(arm, &[block]);
        let name = if x_in_west(run.x_in) { "west" } else { "east" };
        let head = g.feature(head, format!("{name}-z-rail"), format!("{name} sliding rail"), &[]);
        out = Some(match out {
            None => head,
            Some(o) => g.union(o, &[head]),
        });
    }
    out.expect("each column has two rail runs")
}

/// The feet a top piece stands on over each flank's run: a slab from the wall to the foot face,
/// and on the front column the rail's lead-in carried on to the Y joint.
pub fn z_rail_feet(g: &mut Graph, inner: &Bounds, y_joint: f64, zj: f64, col: Y) -> Shape {
    let z_foot = zj + HOOK_FOOT;
    let mut out: Option<Shape> = None;
    for run in z_rail_runs(inner, y_joint, col) {
        let (x_in, sx) = (run.x_in, run.sx);
        let sy = if run.y1 > run.y0 { 1.0 } else { -1.0 };
        let (mut y0, mut y1) = (run.y0, run.y1);
        match col {
            Y::Back => y0 -= sy * WALL,
            Y::Front => y1 -= sy * RAIL_STOP_LEN,
        }
        let x_f = rail_x(sx, col).foot;
        let x_root = x_in - sx * 1.0;
        let slab = g.box_([x_root.min(x_f), x_root.max(x_f), y0.min(y1), y0.max(y1), zj, z_foot]);
        let name = if x_in_west(x_in) { "west" } else { "east" };
        let slab = g.feature(slab, format!("{name}-z-rail"), format!("{name} sliding rail"), &[]);
        let mut feet = match out {
            None => slab,
            Some(o) => g.union(o, &[slab]),
        };
        if col == Y::Front {
            let x_open = rail_channel_span(sx, col)[0];
            let rim = zj + Z_RISE;
            let lead = g.xz_prism(y0, y_joint, vec![[x_root, zj], [x_open, zj], [x_open, rim + (x_in - x_open).abs()],
                                                    [x_in, rim], [x_root, rim]]);
            let lead = g.feature(lead, format!("{name}-z-rail"), format!("{name} sliding rail"), &[]);
            feet = g.union(feet, &[lead]);
        }
        out = Some(feet);
    }
    out.expect("each column has two rail runs")
}

/// What a rail channel may open: the cavity's plan round, from the front wall's inner skin to
/// the rear interior, floor slab to roof.
pub fn rail_keep(g: &mut Graph, inner: &Bounds) -> Shape {
    let [ix0, ix1, iy0, iy1, iz0, iz1] = *inner;
    let stock = g.box_([ix0, ix1, (iy0 - FRONT_WALL) + WALL, iy1, iz0 - slab_t() - 1.0, iz1 + WALL + 1.0]);
    g.rounded(stock, CORNER_ROUND - WALL)
}

/// The channels a top piece's feet ride in: the slot over each run to its stop, the lane on past
/// the stop at full section, and on the front column the crossing over the Y joint's lip.
pub fn z_rail_channels(g: &mut Graph, inner: &Bounds, y_joint: f64, zj: f64, col: Y) -> Shape {
    let (z_foot, rim) = (zj + HOOK_FOOT, zj + Z_RISE);
    let z_roof = rim + slide_slip();
    let keep = rail_keep(g, inner);
    let mut out: Option<Shape> = None;
    for run in z_rail_runs(inner, y_joint, col) {
        let (x_in, sx, y0, y1, lane_aft) = (run.x_in, run.sx, run.y0, run.y1, run.lane_aft);
        let sy = if y1 > y0 { 1.0 } else { -1.0 };
        let stop = y1 - sy * RAIL_STOP_LEN;
        let [x_open, x_f, x_d] = rail_channel_span(sx, col);
        let x_peak = (x_open + x_d) / 2.0;
        let z_peak = z_roof + (x_d - x_open).abs() / 2.0;
        let roof = match col {
            Y::Back => vec![[x_d, z_roof], [x_open, z_roof]],
            Y::Front => vec![[x_d, z_roof], [x_peak, z_peak], [x_open, z_roof]],
        };
        let mut section = vec![[x_open, z_foot], [x_f, z_foot], [x_f, zj - 1.0], [x_d, zj - 1.0]];
        section.extend(&roof);
        let mut void = g.xz_prism(y0, stop, section);
        if (lane_aft - stop) * sy > 0.0 {
            let mut lane = vec![[x_open, zj - 1.0], [x_d, zj - 1.0]];
            lane.extend(&roof);
            let lane = g.xz_prism(stop, lane_aft, lane);
            void = g.union(void, &[lane]);
        }
        if col == Y::Front {
            let rise = lane_aft - y_joint;
            let floor = zj - 1.0 - rise;
            let crossing = g.yz_prism(x_f.min(x_in), x_f.max(x_in), vec![
                [y_joint, floor], [lane_aft, floor + lane_aft - y_joint], [lane_aft, z_peak + lane_aft - y_joint],
                [y_joint, z_peak]]);
            void = g.union(void, &[crossing]);
        }
        let void = g.intersect(void, &[keep]);
        let name = if x_in_west(x_in) { "west" } else { "east" };
        let void = g.feature(void, format!("{name}-z-rail"), format!("{name} sliding rail"), &[]);
        out = Some(match out {
            None => void,
            Some(o) => g.union(o, &[void]),
        });
    }
    out.expect("each column has two rail runs")
}

fn x_in_west(x: f64) -> bool { x < 0.0 }

const REAR_RIB_WIDTH: f64 = 3.0;
const REAR_RIB_STRAIGHT_RISE: f64 = 1.5;
const REAR_RIB_LENGTH: f64 = 80.0;
const REAR_RIB_SETBACK: f64 = 10.2;
const REAR_RIB_ROOT: f64 = 0.8;
const REAR_GROOVE_SHOULDER: f64 = 3.0;
const REAR_SHOULDER_ROOT: f64 = 0.4;
const REAR_SUPPORT_ROOT_INSET: f64 = 0.65;

/// The matched ribs and grooves locate the rear halves in X during their slide.
pub struct RearAlignment {
    rib_y: [f64; 2],
    groove_y: [f64; 2],
    rib_outboard_x: f64,
    groove_x: [f64; 2],
    crown_z: f64,
}

impl RearAlignment {
    pub fn new(y_joint: f64, zj: f64) -> Self {
        let mouth_y = back_flank_start(y_joint);
        let fore_y = mouth_y + REAR_RIB_SETBACK;
        let aft_y = fore_y + REAR_RIB_LENGTH;
        let rib_outboard_x = rail_x(-1.0, Y::Back).hook;
        let [channel_edge, _, _] = rail_channel_span(-1.0, Y::Back);
        let clearance = slide_slip();
        Self {
            rib_y: [fore_y, aft_y],
            groove_y: [mouth_y, aft_y + clearance],
            rib_outboard_x,
            groove_x: [rib_outboard_x - REAR_RIB_WIDTH - clearance, channel_edge],
            crown_z: zj + Z_RISE,
        }
    }

    fn shoulder_z(&self) -> f64 {
        self.crown_z + REAR_RIB_STRAIGHT_RISE
    }

    fn groove_peak_z(&self) -> f64 {
        self.shoulder_z() + REAR_RIB_WIDTH / 2.0 + slide_slip()
    }

    /// The upper groove opens upward in the ceiling-down print pose.
    pub fn groove_bounds(&self, sx: f64) -> Bounds {
        let (x0, x1) = sorted(-sx * self.groove_x[0], -sx * self.groove_x[1]);
        [x0, x1, self.groove_y[0], self.groove_y[1], self.crown_z, self.groove_peak_z()]
    }

    /// Breakaway cap necks root in the retained inboard shoulder of the rail cavity.
    pub fn support_root_x(&self, sx: f64) -> f64 {
        -sx * (self.groove_x[0] - REAR_SUPPORT_ROOT_INSET)
    }

    pub fn lower(&self, g: &mut Graph, mut piece: Shape) -> Shape {
        let [fore, aft] = self.rib_y;
        let edge = self.rib_outboard_x;
        let inboard = edge - REAR_RIB_WIDTH;
        let middle = (inboard + edge) / 2.0;
        let root = self.crown_z - REAR_RIB_ROOT;
        let shoulder = self.shoulder_z();
        let rib = g.xz_prism(fore, aft, vec![
            [inboard, root], [edge, root], [edge, shoulder],
            [middle, shoulder + REAR_RIB_WIDTH / 2.0], [inboard, shoulder],
        ]);
        for (side, mirror) in [("east", false), ("west", true)] {
            let rib = if mirror { g.mirror(rib, 0) } else { rib };
            let rib = g.feature(rib, format!("{side}-alignment-rib"), format!("{side} alignment rib"), &[]);
            piece = g.union(piece, &[rib]);
        }
        piece
    }

    pub fn upper(&self, g: &mut Graph, mut piece: Shape) -> Shape {
        let [fore, aft] = self.groove_y;
        let [left, right] = self.groove_x;
        let middle = (left + right) / 2.0;
        let inboard = left - REAR_GROOVE_SHOULDER;
        let overlap = back_top_flank_face()[1] + REAR_SHOULDER_ROOT;
        let roof = self.crown_z + slide_slip();
        let peak = self.groove_peak_z();
        let shoulder = g.xz_prism(fore, aft + REAR_GROOVE_SHOULDER, vec![
            [inboard, roof], [overlap, roof], [overlap, peak + overlap - inboard], [inboard, peak],
        ]);
        let groove = g.xz_prism(fore, aft, vec![
            [left, self.crown_z], [right, self.crown_z], [right, self.shoulder_z()],
            [middle, peak], [left, self.shoulder_z()],
        ]);
        for (side, mirror) in [("east", false), ("west", true)] {
            let (shoulder, groove) = if mirror { (g.mirror(shoulder, 0), g.mirror(groove, 0)) } else { (shoulder, groove) };
            let shoulder = g.feature(shoulder, format!("{side}-alignment-shoulder"), format!("{side} alignment shoulder"), &[]);
            let groove = g.feature(groove, format!("{side}-alignment-groove"), format!("{side} alignment groove"), &[]);
            piece = g.union(piece, &[shoulder]);
            piece = g.cut(piece, &[groove]);
        }
        piece
    }
}
