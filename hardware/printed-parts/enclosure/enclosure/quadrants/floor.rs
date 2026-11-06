//! The pack's mounts on the front floor and walls: the floor posts, the MQ6 card cradle, the
//! condenser's slot cradles and mount, and the core's stops and holds.
use crate::catalog::running;
use crate::columns::{cond_slot_half, cond_slot_mouth};
use crate::handholds::{handhold_levels, handhold_y};
use crate::plan::{Bounds, Graph, Shape};
use crate::quadrant::sorted;
use crate::shell::*;
use crate::walls::lip_face_x;
use crate::ystacks::y_stack_gap;

/// The MQ6 gas sensor's card, as the reference catalog measures it.
pub mod mq6 {
    pub const PCB_X: f64 = 32.0;
    pub const PCB_Y: f64 = 20.0;
    pub const PCB_T: f64 = 1.6;
    pub const CAN_D: f64 = 19.0;
    pub const PIN_SQ: f64 = 0.64;
    pub const PIN_PITCH: f64 = 2.54;
    pub const PIN_COUNT: f64 = 4.0;
    pub const PIN_ROW_INSET: f64 = 3.0;

    /// The header's half span along its row, and its row's offset from the card's middle.
    pub fn header_span() -> (f64, f64) {
        ((PIN_COUNT - 1.0) * PIN_PITCH / 2.0 + PIN_SQ / 2.0, PCB_X / 2.0 - PIN_ROW_INSET)
    }
}

pub fn floor_bosses(g: &mut Graph, mut solid: Shape, inner: &Bounds, stations: &[[f64; 4]],
                    [y0, y1, z0, _]: [f64; 4]) -> Shape {
    if z0 > inner[4] + 1e-6 {
        return solid;
    }
    for &[sx, sy, tip, dia] in stations {
        if !(y0 <= sy && sy <= y1) {
            continue;
        }
        assert!(
            (dia - FLOOR_HEATSET_DIA) / 2.0 >= FLOOR_HEATSET_MIN_WALL,
            "the floor post at ({sx}, {sy}) leaves less than the insert's minimum surrounding wall"
        );
        let post = g.zcyl(dia / 2.0, sx, sy, inner[4], tip);
        solid = g.union(solid, &[post]);
        let bore = g.zcyl(FLOOR_HEATSET_DIA / 2.0, sx, sy, tip - FLOOR_HEATSET_DEPTH - MOUNT_BORE_RELIEF, tip);
        solid = g.cut(solid, &[bore]);
    }
    solid
}

/// The MQ6 card's slotted rails off the west lip.
pub fn west_cradle(g: &mut Graph, mut solid: Shape, inner: &Bounds, stations: &[[f64; 3]],
                   [y0, y1, z0, z1]: [f64; 4]) -> Shape {
    let (span, off) = mq6::header_span();
    let across = mq6::PIN_SQ / 2.0 + MQ6_HEADER_RELIEF;
    let (card_x, card_y, card_z) = (mq6::PCB_T, mq6::PCB_X, mq6::PCB_Y);
    let press = running();
    let grip = MQ6_GRIP.min((card_y - mq6::CAN_D) / 2.0);
    for &[sx, sy, sz] in stations {
        if !(y0 <= sy && sy <= y1 && z0 <= sz && sz <= z1) {
            continue;
        }
        let (gx0, gx1) = (sx - card_x / 2.0 - press, sx + card_x / 2.0 + press);
        let (px0, px1) = (lip_face_x()[0], gx1 + MQ6_RAIL_WALL);
        let (zb, zt) = (sz - card_z / 2.0, sz + card_z / 2.0);
        for into in [1.0, -1.0] {
            let end = sy - into * card_y / 2.0;
            let (pa, pb) = sorted(end - into * (press + MQ6_RAIL_WALL), end + into * grip);
            let rail = g.box_([px0, px1, pa, pb, inner[4], zt]);
            solid = g.union(solid, &[rail]);
            let (ga, gb) = sorted(end - into * press, end + into * (grip + 1.0));
            let slot = g.box_([gx0, gx1, ga, gb, zb, zt + 1.0]);
            solid = g.cut(solid, &[slot]);
            let (ha, hb) = sorted(end + into * (card_y / 2.0 - off - across), end + into * (card_y / 2.0 - off + across));
            let header = g.box_([gx1, px1 + 1.0, ha, hb, sz - span - MQ6_HEADER_RELIEF, zt + 1.0]);
            solid = g.cut(solid, &[header]);
        }
    }
    solid
}

/// The cradle's root face: the front plane, or a fridge relief's face the cradle stands in.
fn cradle_root_y(cx0: f64, cx1: f64, mid_z: f64) -> f64 {
    FRIDGE_RELIEFS
        .iter()
        .filter(|&&[rx0, rx1, rz0, rz1, _]| cx0 >= rx0 - 1e-6 && cx1 <= rx1 + 1e-6 && rz0 <= mid_z && mid_z <= rz1)
        .map(|r| r[4])
        .fold(FRONT_PLANE_Y, f64::min)
}

fn cond_cradle_corbel(g: &mut Graph, [face, cx0, cx1, fz0, fz1, root]: [f64; 6]) -> Shape {
    let root_y = cradle_root_y(cx0, cx1, (fz0 + fz1) / 2.0);
    let free_y = face + COND_SLOT_GRIP;
    let reach = free_y - root_y;
    g.yz_prism(cx0, cx1, vec![[root_y, root - reach], [root_y, root], [free_y, root]])
}

/// The condenser sheet's slot cradles off the front wall.
pub fn cond_cradle(g: &mut Graph, mut solid: Shape, inner: &Bounds, stations: &[[f64; 6]],
                   [y0, y1, z0, z1]: [f64; 4]) -> Shape {
    for &[face, cx0, cx1, fz0, fz1, declared_root] in stations {
        let mid_z = (fz0 + fz1) / 2.0;
        if !(y0 <= face && face <= y1 && z0 <= mid_z && mid_z <= z1) {
            continue;
        }
        let root = if declared_root < inner[4] + COND_RAIL_WALL { inner[4] } else { declared_root };
        let half = cond_slot_half(fz1 - fz0);
        let root_y = cradle_root_y(cx0, cx1, mid_z);
        let crown = fz1 + half + COND_SLOT_GRIP + COND_RAIL_WALL;
        let body = g.box_([cx0, cx1, root_y, face + COND_SLOT_GRIP, root, crown]);
        solid = g.union(solid, &[body]);
        if root > inner[4] + 1e-6 {
            let corbel = cond_cradle_corbel(g, [face, cx0, cx1, fz0, fz1, root]);
            solid = g.union(solid, &[corbel]);
        }
        let mouth = cond_slot_mouth(face);
        let run = mouth - face;
        let slot = g.yz_prism(cx0 - 1.0, cx1 + 1.0, vec![[face, fz0 - half], [mouth, fz0 - half],
                                                          [mouth, fz1 + half + run], [face, fz1 + half]]);
        solid = g.cut(solid, &[slot]);
    }
    solid
}

/// The condenser's east mount: the flank, its M3 bosses, and the corbel under the raised ones.
pub fn cond_mount(g: &mut Graph, mut solid: Shape, inner: &Bounds, station: &(f64, f64, f64, Vec<[f64; 3]>),
                  [y0, y1, z0, z1]: [f64; 4]) -> Shape {
    let (flank, my0, my1, bosses) = station;
    let (flank, my0, my1) = (*flank, *my0, *my1);
    let mid_y = (my0 + my1) / 2.0;
    if bosses.is_empty() || !(y0 <= mid_y && mid_y <= y1 && z0 <= inner[4] && inner[4] <= z1) {
        return solid;
    }
    let crown = bosses.iter().map(|b| b[2]).fold(f64::NEG_INFINITY, f64::max);
    let floor_tip = bosses.iter().map(|b| b[2]).fold(f64::INFINITY, f64::min);
    assert!(floor_tip > inner[4], "the lowest condenser flange leaves the boss under it no height");
    let west = bosses.iter().map(|b| b[0]).fold(f64::INFINITY, f64::min) - MOUNT_BOSS_DIA;
    let body = g.box_([flank, inner[1], my0, my1, inner[4], crown]);
    solid = g.union(solid, &[body]);
    for &[_, _, tip] in bosses {
        let root = if tip == floor_tip { inner[4] } else { tip - COND_BOSS_T };
        let boss = g.box_([west, inner[1], my0, my1, root, tip]);
        solid = g.union(solid, &[boss]);
    }
    if crown > floor_tip + 1e-6 {
        let root = crown - COND_BOSS_T;
        let corbel = g.xz_prism(my0, my1, vec![[west, root], [flank, root], [flank, root - (flank - west)]]);
        solid = g.union(solid, &[corbel]);
    }
    for &[bx, by, tip] in bosses {
        let bore = g.zcyl(HEATSET_DIA / 2.0, bx, by, tip - COND_BORE_DEPTH, tip);
        solid = g.cut(solid, &[bore]);
    }
    solid
}

/// The air a core stop's tail leaves under the handhold's roof, where the two meet.
fn core_stop_handhold_air(g: &mut Graph, inner: &Bounds, [cx, cy, r]: [f64; 3], band_end_y: f64) -> Option<Shape> {
    let [hand_y0, hand_y1] = handhold_y();
    let (ya, yb) = (band_end_y.max(hand_y0), cy.min(hand_y1));
    if yb <= ya {
        return None;
    }
    let side = if cx > 0.0 { 1.0 } else { -1.0 };
    let wall_x = if side > 0.0 { inner[1] } else { inner[0] };
    let lap = cx - side * r;
    let roof = handhold_levels(inner)[1];
    Some(g.box_([lap.min(wall_x), lap.max(wall_x), ya, yb, roof - y_stack_gap(false, true), roof]))
}

/// The core's fore stops: webs off the side walls with a slot each round post takes.
pub fn core_stops(g: &mut Graph, mut solid: Shape, inner: &Bounds, stations: &[[f64; 3]],
                  [y0, y1, z0, _]: [f64; 4]) -> Shape {
    if z0 > inner[4] + 1e-6 {
        return solid;
    }
    for &[cx, cy, r] in stations {
        let slip = running();
        let face = cy - r - slip;
        if !(y0 <= face && face <= y1) {
            continue;
        }
        let side = if cx > 0.0 { 1.0 } else { -1.0 };
        let wall_x = if side > 0.0 { inner[1] } else { inner[0] };
        let lap = cx - side * r;
        let tip = inner[4] + CORE_STOP_RISE;
        let web = g.box_([lap.min(wall_x), lap.max(wall_x), face - CORE_STOP_WEB, cy, inner[4], tip]);
        solid = g.union(solid, &[web]);
        let slot = g.box_([lap.min(cx), lap.max(cx), face, cy + 1.0, inner[4], tip + 1.0]);
        solid = g.cut(solid, &[slot]);
        let post = g.zcyl(r + slip, cx, cy, inner[4], tip + 1.0);
        solid = g.cut(solid, &[post]);
        if let Some(air) = core_stop_handhold_air(g, inner, [cx, cy, r], y1) {
            solid = g.cut(solid, &[air]);
        }
    }
    solid
}

/// The core's aft holds: brackets off the rear wall over its crown.
pub fn core_holds(g: &mut Graph, mut solid: Shape, inner: &Bounds, stations: &[[f64; 4]],
                  [y0, y1, z0, z1]: [f64; 4], face: Option<f64>) -> Shape {
    let back = face.unwrap_or(inner[3]);
    let lead = 1.0;
    for &[sx0, sx1, aft, declared_crown] in stations {
        if !(y0 <= aft && aft <= y1 && z0 <= declared_crown && declared_crown <= z1) {
            continue;
        }
        let tip = aft - CORE_HOLD_REACH;
        let crown = declared_crown + running();
        let bracket = g.yz_prism(sx0, sx1, vec![[tip + lead, crown], [back, crown], [back, crown + CORE_HOLD_RISE],
                                                [tip, crown + CORE_HOLD_LAND], [tip, crown + lead]]);
        solid = g.union(solid, &[bracket]);
    }
    solid
}
