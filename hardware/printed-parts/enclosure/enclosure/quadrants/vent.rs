//! The PRV vent chase, a ribbed duct up the west wall from the relief valve to a groove that
//! vents through the flank, and the condenser's grilles pierced through both flanks' flutes.
use crate::catalog::{pierce_width, running, supported};
use crate::field::{flute_pitch, plan_at};
use crate::plan::{Bounds, FlankVents, Graph, Op, Shape, VentColumn};
use crate::quadrant::{Y, sorted};
use crate::rails::{rail_channel_span, rail_x};
use crate::shell::*;
use crate::walls::{back_top_flank_face, front_bottom_flank_face};

pub fn vent_chase(
    g: &mut Graph,
    mut solid: Shape,
    inner: &Bounds,
    outer: &Bounds,
    stations: &[[f64; 3]],
    [y0, y1, z0, z1]: [f64; 4],
    up: f64,
) -> Shape {
    for &[sx, sy, sz] in stations {
        let half = VENT_CHANNEL_W / 2.0 + VENT_RIB_WALL;
        let rib_x = sx - running();
        let floor_x = rib_x - VENT_RIB_WALL;
        let ramp_depth = floor_x - outer[0];
        let ramp_rise = ramp_depth / VENT_RAMP_ANGLE.to_radians().tan();
        let vent = sz - VENT_DUCT_DROP - VENT_GROOVE_DROP - ramp_rise;
        if !(y0 <= sy && sy <= y1 && vent < z1 && sz + half > z0) {
            continue;
        }
        let owns = z0 <= vent && vent <= z1;
        let mouth_top = sz + VENT_CHANNEL_W / 2.0;
        let mouth_bot = sz - VENT_CHANNEL_W / 2.0 - if up < 0.0 { supported() } else { 0.0 };
        let groove_top = sz - VENT_DUCT_DROP;
        let groove_rise = if up > 0.0 { 1.0 } else { 0.0 };
        let ramp_top = groove_top - VENT_GROOVE_DROP;
        let ramp_bot = ramp_top - ramp_rise;
        let over = ramp_rise / ramp_depth;
        let rib_end = ramp_top - ramp_rise * ((floor_x - (inner[0] - VENT_RIB_WALL)) / ramp_depth);
        let rim = Z_SEAM + Z_RISE;
        let liner_x = inner[0] + slide_slip() + VENT_RIB_WALL;
        let passage_half = VENT_CHANNEL_W / 2.0;
        let root_x = back_top_flank_face()[0];
        let roof_root = mouth_top + (root_x - liner_x);
        let roof_run = rib_x - root_x;
        assert!(roof_run > 0.0, "the PRV chase lip at x={rib_x} does not stand inboard of its wall root x={root_x}");
        let under = VENT_RIB_WALL * (2f64.sqrt() - 1.0);
        let rib = g.xz_prism(sy - half, sy + half, vec![[inner[0], sz + half], [rib_x, sz + half],
                                                         [rib_x, ramp_top - under], [inner[0], rib_end - under]]);
        let cap_root = roof_root + 2.0 * VENT_RIB_WALL;
        let cap_lip = cap_root + roof_run;
        let cap_wall = if up < 0.0 { cap_lip + roof_run } else { cap_root };
        let cap = g.xz_prism(sy - half, sy + half, vec![[root_x, sz + half], [rib_x, sz + half], [rib_x, cap_lip],
                                                         [root_x, cap_wall]]);
        let mut rib = g.union(rib, &[cap]);
        if up < 0.0 {
            let rear = sy + half;
            let backing = g.xy_prism(rim + WALL, cap_lip, vec![
                [root_x, rear], [rib_x, rear], [root_x, rear + roof_run]]);
            rib = g.union(rib, &[backing]);
        }
        let arm_end = rail_x(1.0, Y::Back).arm_end;
        let lane = g.box_([inner[0] - 1.0, arm_end + if owns { 0.0 } else { slide_slip() }, sy - half - 1.0,
                           sy + half + 1.0, Z_SEAM, rim]);
        let rib = g.cut(rib, &[lane]);
        let band = if owns { (outer[4] - 1.0, rim) } else { (rim + slide_slip(), outer[5] + 1.0) };
        let rear_reach = if up < 0.0 { roof_run } else { 0.0 };
        let keep = g.box_([outer[0] - 1.0, outer[1] + 1.0, sy - half - 1.0, sy + half + rear_reach + 1.0, band.0, band.1]);
        let mut share = g.intersect(rib, &[keep]);
        if !owns && up > 0.0 {
            let [_, _, far] = rail_channel_span(1.0, Y::Back);
            let gable_bed = (slide_slip() + far + inner[0]) / 2.0;
            let gable_lip = (slide_slip() + far + root_x) / 2.0;
            let gable = g.xz_prism(sy - half - 1.0, sy + half + 1.0, vec![
                [inner[0], rim - 1.0], [rib_x + 1.0, rim - 1.0], [rib_x + 1.0, rim + (rib_x + 1.0 - root_x)],
                [gable_lip, rim + (gable_lip - root_x)], [gable_bed, rim + (gable_bed - inner[0])], [inner[0], rim]]);
            share = g.cut(share, &[gable]);
        }
        solid = g.union(solid, &[share]);
        let duct = g.xz_prism(sy - VENT_CHANNEL_W / 2.0, sy + VENT_CHANNEL_W / 2.0, vec![
            [rib_x + 1.0, mouth_top], [rib_x + 1.0, mouth_bot], [floor_x, mouth_bot], [floor_x, ramp_top],
            [outer[0] - 1.0, ramp_bot - over], [outer[0] - 1.0, groove_top - groove_rise],
            [inner[0], groove_top + groove_rise * (inner[0] - outer[0])], [inner[0], rim + slide_slip()],
            [liner_x, rim + slide_slip()], [liner_x, mouth_top]]);
        solid = g.cut(solid, &[duct]);
        let passage = g.xz_prism(sy - passage_half, sy + passage_half, vec![
            [liner_x, mouth_top], [rib_x + 1.0, mouth_top], [rib_x + 1.0, mouth_top + (rib_x + 1.0 - liner_x)]]);
        solid = g.cut(solid, &[passage]);
    }
    solid
}

/// The vent's open passage stays clear while its exterior walls can receive accessible trees.
pub fn mouth_support_bounds(inner: &Bounds, [x, y, z]: [f64; 3]) -> Bounds {
    let rib = x - running();
    let half = VENT_CHANNEL_W / 2.0;
    let liner = inner[0] + slide_slip() + VENT_RIB_WALL;
    [liner, rib, y-half, y+half, Z_SEAM-1.0, z+half+rib-liner]
}

/// The mouth's end walls and their backing grow without supports through the passage.
pub fn mouth_blocking_bounds(inner: &Bounds, [x, y, z]: [f64; 3]) -> Bounds {
    let rib = x - running();
    let root = back_top_flank_face()[0];
    let liner = inner[0] + slide_slip() + VENT_RIB_WALL;
    let half = VENT_CHANNEL_W / 2.0 + VENT_RIB_WALL;
    let top = z + VENT_CHANNEL_W / 2.0 + root - liner + 2.0 * VENT_RIB_WALL + 2.0 * (rib-root);
    [root-WALL, rib+1.0, y-half, y+half+rib-root, Z_SEAM-1.0, top]
}

/// The mouth's open passage, used to distinguish a branch inside it from an exterior tree.
pub fn mouth_void(inner: &Bounds, [x, y, z]: [f64; 3]) -> serde_json::Value {
    let rib = x-running();
    let floor = rib-VENT_RIB_WALL;
    let liner = inner[0]+slide_slip()+VENT_RIB_WALL;
    let half = VENT_CHANNEL_W/2.0;
    let top = z+half;
    let bottom = z-half-supported();
    let shaft = z-VENT_DUCT_DROP-VENT_GROOVE_DROP;
    serde_json::json!({"kind":"prism_y","span_y_mm":[y-half,y+half],
        "profile_xz_mm":[[liner,top],[liner,shaft],[floor,shaft],[floor,bottom],
                         [rib,bottom],[rib,top+rib-liner]]})
}

/// The height the condenser's vents are pierced over: the fan's footprint on the flank.
pub fn vent_band(airway: &[f64; 4]) -> [f64; 2] {
    [airway[2] + COND_FAN_RISE, airway[3] - COND_FAN_DROP]
}

/// The band divided by its transoms into equal opening courses, bottom to top.
pub fn vent_segments(airway: &[f64; 4]) -> Vec<[f64; 2]> {
    let [z0, z1] = vent_band(airway);
    let n = COND_VENT_TRANSOMS as f64;
    let run = (z1 - z0 - n * COND_VENT_TRANSOM_H) / (n + 1.0);
    let mut out = Vec::new();
    let mut lo = z0;
    for k in 0..COND_VENT_TRANSOMS {
        let k = k as f64;
        out.push([lo, z0 + (k + 1.0) * run + k * COND_VENT_TRANSOM_H]);
        lo = z0 + (k + 1.0) * run + (k + 1.0) * COND_VENT_TRANSOM_H;
    }
    out.push([lo, z1]);
    out
}

/// The interior face a vent slot is struck from: front-bottom's own flank face.
pub fn vent_flank_face(sx: f64) -> f64 {
    let [ix0, ix1] = front_bottom_flank_face();
    if sx > 0.0 { ix1 } else { ix0 }
}

/// Every flute the vents pierce, as its flank's sign and its station: the grooves on a ±X
/// run whose whole slot lies within the block's airway.
pub fn vent_grooves(outer: &Bounds, airway: &[f64; 4]) -> Vec<(f64, f64)> {
    let (ay0, ay1) = (airway[0], airway[1]);
    let half = pierce_width() / 2.0;
    let pitch = flute_pitch(outer);
    let mut out = Vec::new();
    for k in 0..FLUTE_COUNT as usize {
        let ([_, py], [nx, _]) = plan_at(k as f64 * pitch, outer);
        if (nx.abs() - 1.0).abs() > 1e-9 {
            continue;
        }
        if ay0 - STATED_BOUND_TOL <= py - half && py + half <= ay1 + STATED_BOUND_TOL {
            out.push((if nx > 0.0 { 1.0 } else { -1.0 }, py));
        }
    }
    out.sort_by(|a, b| a.partial_cmp(b).expect("vent stations are numbers"));
    out
}

/// One course's slot down a groove's centre, through the flank, closed at both ends by a hip
/// at the relief chamfer.
fn vent_cutter(g: &mut Graph, outer: &Bounds, sx: f64, y: f64, z0: f64, z1: f64) -> Shape {
    let face = vent_flank_face(sx);
    let skin = if sx > 0.0 { outer[1] } else { outer[0] };
    let half = pierce_width() / 2.0;
    let hip = half * RELIEF_CHAMFER.to_radians().tan();
    g.yz_prism(face - sx * 1.0, skin + sx * 1.0, vec![[y, z0], [y + half, z0 + hip], [y + half, z1 - hip], [y, z1],
                                                      [y - half, z1 - hip], [y - half, z0 + hip]])
}

/// The condenser's intake and exhaust: every course of every groove over the airway, each
/// opened only where the flank behind it stands clear.
pub fn flank_vents(g: &mut Graph, solid: Shape, outer: &Bounds, airway: &[f64; 4]) -> Shape {
    let courses = vent_segments(airway);
    let band = vent_band(airway);
    let half = pierce_width() / 2.0;
    let clear = COND_VENT_CLEAR;
    let (mut columns, mut cutters) = (Vec::new(), Vec::new());
    for (side, y) in vent_grooves(outer, airway) {
        let face = vent_flank_face(side);
        let (xa, xb) = sorted(face - side * COND_VENT_PROBE, face - side * STATED_BOUND_TOL);
        let mut indices = Vec::new();
        for &[lo, hi] in &courses {
            indices.push(cutters.len());
            cutters.push(vent_cutter(g, outer, side, y, lo, hi));
        }
        columns.push(VentColumn {
            cutters: indices,
            probe: [xa, xb, y - half - clear, y + half + clear, band[0] - clear, band[1] + clear],
            side,
        });
    }
    let inputs = std::iter::once(solid.index).chain(cutters.iter().map(|c: &Shape| c.index)).collect();
    let vents = FlankVents { columns, courses, clearance: clear, tolerance: STATED_BOUND_TOL,
                             island_min: COND_VENT_ISLAND_MIN };
    g.add(Op::FlankVents(vents), inputs, solid.bounds)
}
