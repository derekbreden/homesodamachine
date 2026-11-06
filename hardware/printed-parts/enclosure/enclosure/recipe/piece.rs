//! One quadrant's construction: its half of the shell, the joints it carries, and every pack
//! feature that falls in its bands.
use crate::above;
use crate::backtop;
use crate::columns::{column_relief, column_relief_rise};
use crate::floor;
use crate::front::y_lip_channel;
use crate::fronttop;
use crate::funnel::funnel_cut;
use crate::handholds::{finish_handholds, handholds};
use crate::plan::{Graph, Shape};
use crate::quadrant::{Quadrant, Y, Z};
use crate::rails::{z_rail_channels, z_rail_feet, z_rail_heads};
use crate::routes;
use crate::seam::seam_fit_reliefs;
use crate::seat;
use crate::shell::{LIP_LEN, WALL};
use crate::spec::Box;
use crate::valves;
use crate::vent::{flank_vents, vent_chase};
use crate::walls::*;
use crate::ystacks::y_stacks;

/// The recipe's inputs for one quadrant: the declared Box, the swept silhouette every piece is
/// trimmed to, and the half shell the quadrant is cut from.
pub struct Build<'a> {
    pub b: &'a Box,
    pub q: Quadrant,
    pub silhouette: Shape,
    pub half: Shape,
}

impl Build<'_> {
    fn relief_split(&self, sy: f64) -> f64 {
        if sy < 0.0 { self.b.splits[0] } else { self.b.splits[1] }
    }
}

/// Cut one quadrant from its half shell.
pub fn build_piece(g: &mut Graph, k: &Build) -> Shape {
    let (b, q) = (k.b, k.q);
    let (inner, outer, y_joint) = (&b.inner, &b.outer, b.y_joint);
    let [ox0, ox1, oy0, oy1, oz0, oz1] = *outer;
    let zj = q.zj(b);
    let up = q.up();
    let pack = &b.pack;
    let plate = Some(&pack.collet_plate);
    let mut piece = match q.z {
        Z::Bottom => {
            let lower = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, oz0 - 1.0, zj]);
            let mut piece = g.intersect(k.half, &[lower]);
            let col = match q.y {
                Y::Front => g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, y_joint, oz0 - 1.0, oz1 + 1.0]),
                Y::Back => g.box_([ox0 - 1.0, ox1 + 1.0, y_joint, oy1 + 1.0, oz0 - 1.0, oz1 + 1.0]),
            };
            let lip = lip_underwall(g, inner, y_joint, zj);
            let lip = g.intersect(lip, &[col]);
            piece = g.union(piece, &[lip]);
            match q.y {
                Y::Front => {
                    let skin = front_bottom_flank_skin(g, inner, y_joint, zj);
                    let skin = g.intersect(skin, &[col]);
                    piece = g.union(piece, &[skin]);
                    let foot = plate_foot(g, &pack.collet_plate, zj);
                    let foot = g.intersect(foot, &[col]);
                    piece = g.union(piece, &[foot]);
                }
                Y::Back => {
                    let skin = back_bottom_flank_skin(g, inner, y_joint, zj);
                    let skin = g.intersect(skin, &[col]);
                    piece = g.union(piece, &[skin]);
                }
            }
            if q.y == Y::Front {
                let flat = front_flat_lip_drop(g, inner, zj);
                piece = g.cut(piece, &[flat]);
                let flanks = flank_lip_drop(g, inner, &pack.collet_plate, zj);
                piece = g.cut(piece, &[flanks]);
            }
            let heads = z_rail_heads(g, inner, y_joint, zj, q.y, plate);
            g.union(piece, &[heads])
        }
        Z::Top => {
            let upper = g.box_([ox0 - 1.0, ox1 + 1.0, oy0 - 1.0, oy1 + 1.0, zj, oz1 + 1.0]);
            let mut piece = g.intersect(k.half, &[upper]);
            match q.y {
                Y::Front => {
                    let flanks = fronttop::flanks(g, inner, outer, y_joint, zj);
                    piece = g.union(piece, &[flanks]);
                    let bedding = fronttop::flank_bedding_cut(g, inner, y_joint - WALL - 1.0, y_joint + LIP_LEN + 1.0, zj);
                    piece = g.cut(piece, &[bedding]);
                }
                Y::Back => {
                    let flanks = backtop::flanks(g, b, zj, up);
                    piece = g.union(piece, &[flanks]);
                }
            }
            let feet = z_rail_feet(g, inner, y_joint, zj, q.y, plate);
            piece = g.union(piece, &[feet]);
            if q.y == Y::Back {
                let wall = backtop::wall(g, b, zj, up);
                piece = g.union(piece, &[wall]);
                piece = backtop::ceiling(g, piece, b);
            }
            piece
        }
    };
    piece = g.intersect(piece, &[k.silhouette]);
    for relief in &b.column_reliefs {
        let rise = column_relief_rise(g, inner, relief.0, relief.1, &relief.3, k.relief_split(relief.1), up,
                                      &pack.cond_cradle);
        piece = g.cut(piece, &[rise]);
    }
    let bands = q.bands(b);
    piece = floor::floor_bosses(g, piece, inner, &pack.floor_bosses, bands);
    piece = floor::west_cradle(g, piece, inner, &pack.west_cradle, bands);
    piece = floor::cond_cradle(g, piece, inner, &pack.cond_cradle, bands);
    piece = floor::cond_mount(g, piece, inner, &pack.cond_mount, bands);
    piece = floor::core_stops(g, piece, inner, &pack.core_stops, bands);
    let hold_face = if q == Quadrant::BACK_TOP { Some(crate::shell::back_top_wall_face()) } else { None };
    piece = floor::core_holds(g, piece, inner, &pack.core_holds, bands, hold_face);
    piece = vent_chase(g, piece, inner, outer, &pack.vent_chase, bands, up);
    if q == Quadrant::FRONT_TOP {
        piece = fronttop::bulkhead_and_ridge(g, piece, b);
    }
    piece = valves::valve_trays(g, piece, b, q, bands);
    if q == Quadrant::FRONT_TOP {
        piece = fronttop::dock_and_bay(g, piece, b);
        piece = fronttop::seat_ledge_corbels(g, piece, b);
        piece = fronttop::loading_and_dock_cuts(g, piece, b);
    }
    for relief in &b.column_reliefs {
        let split = k.relief_split(relief.1);
        let cut = column_relief(g, inner, relief.0, relief.1, &relief.3, split, &pack.cond_cradle);
        piece = g.cut(piece, &[cut]);
        let rise = column_relief_rise(g, inner, relief.0, relief.1, &relief.3, split, up, &pack.cond_cradle);
        piece = g.cut(piece, &[rise]);
    }
    if q.z == Z::Top {
        piece = above::apply(g, piece, b, q.y);
    }
    if airway_in(b, bands) {
        piece = flank_vents(g, piece, outer, &pack.cond_airway);
    }
    if q.z == Z::Top {
        let channels = z_rail_channels(g, inner, y_joint, zj, q.y, plate);
        piece = g.cut(piece, &[channels]);
    }
    if q.y == Y::Front {
        let channel = y_lip_channel(g, inner, y_joint);
        piece = g.cut(piece, &[channel]);
    }
    if q.z == Z::Top {
        piece = seat::funnel_seat(g, piece, b, q, k.silhouette, up);
    }
    if q == Quadrant::FRONT_TOP {
        piece = fronttop::flank_pockets(g, piece, &pack.front_flank_reliefs);
    }
    if q.z == Z::Bottom {
        piece = handholds(g, piece, inner, y_joint, q.y);
    }
    if q == Quadrant::BACK_BOTTOM {
        let letters = crate::text::disposal_letters(g, outer);
        piece = g.union(piece, &[letters]);
    }
    piece = routes::apply(g, piece, q);
    let knuckle_cut = if q == Quadrant::FRONT_TOP { Some(funnel_cut(g, inner, outer, pack.funnel)) } else { None };
    piece = y_stacks(g, piece, inner, k.silhouette, y_joint, q, knuckle_cut);
    if q.z == Z::Bottom {
        piece = finish_handholds(g, piece, inner);
    }
    let rear = if q == Quadrant::BACK_TOP { crate::rear::seam_lands(g) } else { vec![] };
    piece = seam_fit_reliefs(g, piece, b, q, &rear);
    if q == Quadrant::FRONT_TOP {
        piece = fronttop::pump_mount_cuts(g, piece, b);
    }
    piece
}

/// Whether the condenser's airway centre falls in these bands.
fn airway_in(b: &Box, [y0, y1, z0, z1]: [f64; 4]) -> bool {
    let [ay0, ay1, az0, az1] = b.pack.cond_airway;
    let (my, mz) = ((ay0 + ay1) / 2.0, (az0 + az1) / 2.0);
    y0 <= my && my <= y1 && z0 <= mz && mz <= z1
}
