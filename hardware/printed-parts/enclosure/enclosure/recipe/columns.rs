//! The reliefs a declared body takes through a corner column, and the printable rise over them.
use crate::catalog::running;
use crate::plan::{Bounds, Graph, Shape};
use crate::shell::COND_SLOT_GRIP;
use crate::walls::column_pillar;

/// A condenser slot's half allowance: the sheet presses in at the running fit.
pub fn cond_slot_half(_sheet: f64) -> f64 {
    running()
}

/// The slot's mouth: the grip's depth and a millimetre beyond the sheet's face.
pub fn cond_slot_mouth(face: f64) -> f64 {
    face + COND_SLOT_GRIP + 1.0
}

/// The condenser cradle station a relief crosses at its fore face, if any.
fn crossed(room: &Bounds, cradle: &[[f64; 6]]) -> Option<[f64; 6]> {
    let [x0, x1, y0, _, z0, z1] = *room;
    cradle.iter().copied().find(|s| (s[0] - y0).abs() < 1e-6 && z0 < s[3] && s[4] < z1 && s[1] < x1 && x0 < s[2])
}

/// A relief that keeps the cradle's slot grip where it crosses one.
pub fn cradle_relief(g: &mut Graph, room: &Bounds, station: &[f64; 6]) -> Shape {
    let [x0, x1, y0, y1, z0, z1] = *room;
    let [face, _, _, fz0, fz1, _] = *station;
    let half = cond_slot_half(fz1 - fz0);
    let (grip, roof) = (fz0 - half, fz1 + half);
    let mouth = cond_slot_mouth(face);
    g.yz_prism(x0, x1, vec![[y0, grip], [mouth, grip], [mouth + (grip - z0), z0], [y1, z0], [y1, z1],
                            [face + z1 - roof, z1], [y0, roof]])
}

pub fn column_relief(g: &mut Graph, inner: &Bounds, sx: f64, sy: f64, room: &Bounds, zj: f64,
                     cradle: &[[f64; 6]]) -> Shape {
    let body = match crossed(room, cradle) {
        Some(station) => cradle_relief(g, room, &station),
        None => g.box_(*room),
    };
    let pillar = column_pillar(g, inner, sx, sy, zj);
    g.intersect(body, &[pillar])
}

/// The wedge over a relief's lid that lets the column print without a bridge.
#[allow(clippy::too_many_arguments)]
pub fn column_relief_rise(g: &mut Graph, inner: &Bounds, sx: f64, sy: f64, room: &Bounds, zj: f64, up: f64,
                          cradle: &[[f64; 6]]) -> Shape {
    let [x0, x1, y0, y1, z0, z1] = *room;
    let (held_x, free_x) = if sx > 0.0 { (x1, x0) } else { (x0, x1) };
    let (held_y, free_y) = if sy > 0.0 { (y1, y0) } else { (y0, y1) };
    let lid = if up > 0.0 { z1 } else { z0 };
    let mut y_lid = lid;
    if up > 0.0 {
        if let Some(station) = crossed(room, cradle) {
            y_lid = station[4] + cond_slot_half(station[4] - station[3]);
        }
    }
    let (wx, wy) = (up * (x1 - x0).abs(), up * (y1 - y0).abs());
    let across = g.xz_prism(y0, y1, vec![[free_x, lid], [held_x, lid], [free_x, lid + wx]]);
    let along = g.yz_prism(x0, x1, vec![[free_y, y_lid], [held_y, y_lid], [free_y, y_lid + wy]]);
    let both = g.intersect(across, &[along]);
    let pillar = column_pillar(g, inner, sx, sy, zj);
    g.intersect(both, &[pillar])
}
