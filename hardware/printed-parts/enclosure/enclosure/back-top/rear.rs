//! Back-top's rear wall: the openings through it, what identifies the machine on it, and what it
//! carries inside, the wall hosts, valve seats and plumbing seats, and back-top's plain lands on
//! the rear face, the flats its flutes stay off.
use crate::catalog::{slip, supported};
use crate::layout::{Pose, layout};
use crate::plan::{Bounds, Flange, Graph, Op, P2, P3, Shape, Snap};
use crate::quadrant::{Quadrant, sorted};
use crate::shapes::{place, rounded};
use crate::shell::{DISPOSAL_EMBED, WALL, shell};
use crate::spec::Box;
use crate::supports::supports;
use crate::disposal::disposal_field;
use crate::valves::{seat, valve};
use crate::rear_wall::{FIELD_PROUD, PLATE_HEIGHT, PLATE_THICK, PLATE_WIDTH, c14, keystone, keystone_land, label_channels, rail_bounds, rail_roots};
use serde::{Deserialize, Serialize};
use std::rc::Rc;

#[path = "../../nameplate/snap_dimensions.rs"]
mod snap_dimensions;

/// The wet ports' bores run through the rear wall from inside its relief to past its face.
pub const WET_PORT_Y: P2 = [458.0, 472.3];

/// The wall's insert bosses and their pilots, for the C14 inlet's screws and the parts it hosts.
const BOSS_RADIUS: f64 = 5.0;
const PILOT_RADIUS: f64 = 2.0;

/// The PSU's ceiling bosses root at this plane, the relays' bosses and bars this far into the
/// west flank, and the valve seats this far into their flanks.
const PSU_ROOT_Z: f64 = 349.25;
const RELAY_ROOT_X: f64 = -98.52;
const SEAT_ROOT_X: f64 = 98.51;

/// The rear wall's features on back-top, after its wells; `keep_clear` is the wells' pockets.
pub fn apply(g: &mut Graph, mut piece: Shape, b: &Box, keep_clear: Option<Shape>) -> Shape {
    let wall = &layout().rear_wall;
    let relief = rounded(g, 2, wall.interior_panel_relief.bounds(), 0.0, &[0, 1, 2, 3]);
    piece = g.cut(piece, &[relief]);
    for port in &wall.wet_ports {
        let bore = g.teardrop_y(shell().teardrop_roof_angle, port.bore_diameter_mm / 2.0,
                                port.center_x_mm, port.center_z_mm, WET_PORT_Y[0], WET_PORT_Y[1], -1.0);
        piece = g.cut(piece, &[bore]);
    }
    let inlet = c14_cutters(g);
    piece = g.cut(piece, &inlet);
    piece = c14_bosses(g, piece);
    piece = keystone(g, piece, &b.pack.core_holds, keep_clear);
    piece = identify(g, piece);
    piece = hosts(g, piece);
    piece = valve_seats(g, piece);
    for support in supports(g) {
        piece = g.union(piece, &[support]);
    }
    // The measured inlet opening stays clear after every integral mount joins.
    g.cut(piece, &inlet)
}

/// The inlet's flange pocket and body opening through the wall, each one clearance outside the
/// measured outline.
fn c14_cutters(g: &mut Graph) -> [Shape; 2] {
    let plan = &layout().rear_wall.dry_openings.c14;
    let [x, y, z] = layout().parts.c14_inlet.translation_mm;
    let clearance = plan.profile_clearance_mm;
    let flange = g.add(Op::InletFlange(flange(clearance, [plan.flange_pocket_ymin_mm, y + 1.0])), vec![], None);
    let (hw, hh, k) = (c14::BODY_W / 2.0, c14::BODY_H / 2.0, c14::BODY_CHAMFER_LEG);
    let section = vec![[-hw, hh], [hw, hh], [hw, -(hh - k)], [hw - k, -hh], [-(hw - k), -hh], [-hw, -(hh - k)]];
    let span = [plan.body_opening_ymin_mm, plan.flange_pocket_ymin_mm + 0.01];
    let mut bounds = Graph::prism_bounds(1, span, &section);
    for k in [0, 2] {
        bounds[2 * k] -= clearance;
        bounds[2 * k + 1] += clearance;
    }
    let body = g.add(Op::CornerPrism { axis: 1, span, section, corners: vec![0, 1], radius: c14::BODY_TOP_R,
                                       offset: Some(clearance) }, vec![], Some(bounds));
    [g.translate(flange, [x, 0.0, z]), g.translate(body, [x, 0.0, z])]
}

/// The flange outline's right-top landmarks: a long flat, the knuckle round at its end, the
/// external tangent it shares with the ear arc, and the nose.
fn flange(clearance: f64, span: P2) -> Flange {
    use c14::*;
    let ear_r = FLANGE_W / 2.0 - EAR_CX;
    let h = FLANGE_H / 2.0;
    let a = FLANGE_W / 2.0 - (FLANGE_END_CHORD * FLANGE_END_CHORD - h * h).sqrt();
    let kr = KNUCKLE_R;
    let shoulder = [a, h - kr];
    let (dx, dz) = (EAR_CX - shoulder[0], 0.0 - shoulder[1]);
    let reach = dx.hypot(dz);
    assert!(reach > (ear_r - kr).abs(), "the flange shoulder and ear rounds swallow their tangent");
    let (ux, uz) = (dx / reach, dz / reach);
    let along = (kr - ear_r) / reach;
    let across = (1.0 - along * along).sqrt();
    let (nx, nz) = (along * ux + across * -uz, along * uz + across * ux);
    let q = [shoulder[0] + kr * nx, shoulder[1] + kr * nz];
    let t = [EAR_CX + ear_r * nx, ear_r * nz];
    let mid = (std::f64::consts::PI / 2.0 + nz.atan2(nx)) / 2.0;
    Flange {
        clearance,
        span,
        shoulder: [a, h],
        round_mid: [shoulder[0] + kr * mid.cos(), shoulder[1] + kr * mid.sin()],
        tangent_start: q,
        ear_tangent: t,
        nose: [FLANGE_W / 2.0, 0.0],
        taper_angle_deg: (q[1] - t[1]).atan2(t[0] - q[0]).to_degrees(),
    }
}

/// The flange's two insert bosses behind its seat on the wall, each with its blind pilot.
fn c14_bosses(g: &mut Graph, mut piece: Shape) -> Shape {
    let pitch = layout().rear_wall.dry_openings.c14.mount_pitch_mm;
    let [x, y, z] = layout().parts.c14_inlet.translation_mm;
    let seat_y = y - c14::FLANGE_T;
    for dx in [-pitch / 2.0, pitch / 2.0] {
        let boss = g.ycyl(BOSS_RADIUS, x + dx, z, seat_y - c14::BOSS_DEPTH, seat_y);
        piece = g.union(piece, &[boss]);
        let pilot = g.ycyl(PILOT_RADIUS, x + dx, z, seat_y - c14::PILOT_DEPTH, seat_y + 0.01);
        piece = g.cut(piece, &[pilot]);
    }
    piece
}

/// A cavity with extra room at its supported face, along the piece's build direction.
fn supported_cut(g: &mut Graph, cutter: Shape, up: f64) -> Shape {
    let lifted = g.translate(cutter, [0.0, 0.0, up * supported()]);
    g.union(cutter, &[lifted])
}

/// A rectangle across Y about `(x, z)`, over a Y span.
fn rect_cut_y(g: &mut Graph, x: f64, z: f64, w: f64, h: f64, [y0, y1]: P2) -> Shape {
    rounded(g, 1, [x - w / 2.0, x + w / 2.0, y0, y1, z - h / 2.0, z + h / 2.0], 0.0, &[0, 1, 2, 3])
}

/// The pocket the jack's body swings into: the module standard's, less the jack's own slip in
/// it, with the shared base fit at each wall.
fn keystone_pocket_width() -> f64 {
    keystone::POCKET_W - keystone::FIT_SLIP + 2.0 * slip()
}

/// The unchanged jack's face and body with the enclosure's static mating clearance: its
/// aperture through the lip, its pocket from the lip back to `back`, and the ease over the
/// aperture that its swing needs.
fn keystone_pocket_cut(g: &mut Graph, x: f64, z: f64, y_face: f64, back: f64) -> Shape {
    use keystone::*;
    let (aw, ah) = (FACE_W + 2.0 * slip(), FACE_H + 2.0 * slip());
    let pocket_h = POCKET_H - FIT_SLIP + 2.0 * slip();
    let y_lip = y_face - LIP_D;
    let aperture = rect_cut_y(g, x, z, aw, ah, [y_lip - 0.01, y_face + 0.01]);
    let pocket = rect_cut_y(g, x, z + POCKET_RISE, keystone_pocket_width(), pocket_h, [back - 0.01, y_lip + 0.01]);
    let top = z + ah / 2.0;
    let rise = LIP_D * EASE_DEG.to_radians().tan();
    let ease = g.prism(0, x - aw / 2.0, x + aw / 2.0, vec![
        [y_face + 0.01, top], [y_lip + 0.01, top], [y_lip + 0.01, top + rise],
        [y_face + 0.01 - EASE_SHOULDER * LIP_D / rise, top + EASE_SHOULDER], [y_face + 0.01, top + EASE_SHOULDER]]);
    let cut = g.union(aperture, &[pocket]);
    g.union(cut, &[ease])
}

/// The keystone's receptacle on the wall's inner face: its stock, widened to any core hold's lane
/// it meets and roofed back to the wall, the jack's pocket through it, and the two catches the
/// jack latches on.
fn keystone(g: &mut Graph, piece: Shape, holds: &[[f64; 4]], keep_clear: Option<Shape>) -> Shape {
    use keystone::*;
    let up = Quadrant::BACK_TOP.up();
    let [x, y, z] = layout().rear_wall.dry_openings.keystone.face_center_mm;
    let root = layout().rear_wall.rear_wall.ymin;
    let growth = (slip() - FIT_SLIP / 2.0).max(0.0);
    let half_x = keystone_pocket_width() / 2.0 + RECEPTACLE_WALL;
    let half_z = POCKET_H / 2.0 + growth + RECEPTACLE_WALL;
    let (fore, centre_z) = (root - WALL, z + POCKET_RISE);
    let (mut x0, mut x1) = (x - half_x, x + half_x);
    for &[lane0, lane1, _, _] in holds {
        if lane0 < x1 && lane1 > x0 {
            (x0, x1) = (x0.min(lane0), x1.max(lane1));
        }
    }
    let block = g.box_([x0, x1, fore, root + 0.01, centre_z - half_z, centre_z + half_z]);
    let mut stock = supported_cut(g, block, up);
    let top = centre_z + half_z;
    let roof = g.prism(0, x0, x1, vec![[root, top], [fore, top], [root, top + root - fore]]);
    stock = g.union(stock, &[roof]);
    if let Some(clear) = keep_clear {
        stock = g.cut(stock, &[clear]);
    }
    let cutter = keystone_pocket_cut(g, x, z, y, fore);
    let cutter = supported_cut(g, cutter, up);
    let y_back = y - DEPTH;
    let catches: Vec<Shape> = [(1.0, CATCH_UPPER), (-1.0, CATCH_LOWER)]
        .into_iter()
        .map(|(sign, (height, proud))| {
            let edge = z + POCKET_RISE + sign * POCKET_H / 2.0;
            let (mut za, mut zb) = sorted(edge, edge - sign * height);
            za += (sign * growth).min(0.0);
            zb += (sign * growth).max(0.0);
            if sign * up > 0.0 {
                za += up * supported();
                zb += up * supported();
            }
            g.box_([x - POCKET_W / 2.0 - growth, x + POCKET_W / 2.0 + growth, y_back, y_back + proud, za, zb])
        })
        .collect();
    let catches = g.union(catches[0], &catches[1..]);
    let piece = g.union(piece, &[stock]);
    let piece = g.cut(piece, &[cutter]);
    g.union(piece, &[catches])
}

/// The nameplate's dimension record, shared with the plate it receives.
fn snap() -> Rc<Snap> {
    Rc::new(Snap::read(&snap_dimensions::dimensions(PLATE_WIDTH, PLATE_HEIGHT, PLATE_THICK, slip(), supported(),
                                                    FIELD_PROUD)))
}

/// The nameplate's four-screw receiver on the rear face: its frame stock fused, its mouth and
/// insert pilots cut, with the plate's back at its seat.
fn nameplate_receiver(g: &mut Graph, piece: Shape) -> Shape {
    let s = snap();
    let p = &layout().rear_identification.nameplate;
    let shift = [p.center_x_mm, p.face_y_mm - s.thick, p.center_z_mm];
    let half = s.frame_width / 2.0;
    let stock = g.add(Op::NameplateStock(s.clone()), vec![],
                      Some([-half, half, s.insert_stock_rear, s.thick, s.frame_bottom, s.frame_top]));
    let stock = g.translate(stock, shift);
    let cuts = g.add(Op::NameplateCuts(s.clone()), vec![],
                     Some([-half, half, s.pilot_rear, s.thick, s.frame_bottom, s.frame_top]));
    let cuts = g.translate(cuts, shift);
    let piece = g.union(piece, &[stock]);
    g.cut(piece, &[cuts])
}

/// The receiver on its own: its stock with its pocket, for the rear face's print.
pub fn receiver_field(g: &mut Graph) -> Shape {
    let empty = g.empty();
    nameplate_receiver(g, empty)
}

/// One open channel per column, its side rails and their roots, and the nameplate's receiver.
fn identify(g: &mut Graph, mut piece: Shape) -> Shape {
    for channel in label_channels() {
        let channel = g.box_(channel);
        piece = g.cut(piece, &[channel]);
    }
    for rail in rail_roots().into_iter().chain(rail_bounds()) {
        let rail = g.box_(rail);
        piece = g.union(piece, &[rail]);
    }
    nameplate_receiver(g, piece)
}

/// One mounting hole the wall carries an insert boss for: the hole, the insert's face behind
/// it, the boss's root in the wall, the hole's axis, and whether a screw goes in.
struct Mount {
    point: P3,
    face: P3,
    root: P3,
    axis: P3,
    threaded: bool,
}

/// A hosted part's mounting holes, its native hole pattern placed by its pose.
fn mounts(pose: &Pose, half: P2, setback: f64, root: impl Fn(P3) -> P3, threaded: impl Fn(usize) -> bool) -> Vec<Mount> {
    let axis = pose.vector([0.0, 0.0, 1.0]);
    [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)]
        .into_iter()
        .enumerate()
        .map(|(i, (sx, sy))| {
            let point = pose.point([sx * half[0], sy * half[1], 0.0]);
            let face = std::array::from_fn(|k| point[k] - setback * axis[k]);
            Mount { point, face, root: root(point), axis, threaded: threaded(i) }
        })
        .collect()
}

/// A cylinder along a principal axis from `root`, `length` along `axis`.
fn axial_cylinder(g: &mut Graph, radius: f64, root: P3, axis: P3, length: f64) -> Shape {
    let k = (0..3).find(|&k| axis[k].abs() > 1e-8).expect("a host axis has a direction");
    assert!((0..3).all(|j| j == k || axis[j].abs() <= 1e-8), "a wall host axis is no longer principal");
    let [a, b]: [f64; 2] = std::array::from_fn(|i| root[if i < k { i } else { i + 1 }]);
    g.cylinder(k, radius, a, b, root[k], root[k] + axis[k] * length)
}

/// The PSU's ceiling bosses and the two relays' west-flank bosses, each relay row's edge bar, and
/// every threaded hole's pilot.
fn hosts(g: &mut Graph, mut piece: Shape) -> Shape {
    use crate::rear_wall::hosts::{PILOT_DEPTH, RELAY_SETBACK};
    /// The PSU's and the relays' native hole half-spacings, and each relay row's edge bar's
    /// half-width.
    const PSU_HOLES: P2 = [16.5, 49.0];
    const RELAY_HOLES: P2 = [33.0, 6.5];
    const RELAY_BAR_HALF: f64 = 5.0;
    let parts = &layout().parts;
    let psu = mounts(&parts.psu, PSU_HOLES, 0.0, |p| [p[0], p[1], PSU_ROOT_Z], |_| true);
    let relay = |pose| mounts(pose, RELAY_HOLES, RELAY_SETBACK, |p| [RELAY_ROOT_X, p[1], p[2]], |i| i < 2);
    let relays: Vec<Mount> = relay(&parts.relay_1).into_iter().chain(relay(&parts.relay_2)).collect();
    let mut bosses = Vec::new();
    let mut pilots = Vec::new();
    for m in psu.iter().chain(&relays) {
        let length: f64 = (0..3).map(|k| (m.face[k] - m.root[k]) * m.axis[k]).sum();
        bosses.push(axial_cylinder(g, BOSS_RADIUS, m.root, m.axis, length));
        if m.threaded {
            let start = std::array::from_fn(|k| m.face[k] + 0.01 * m.axis[k]);
            pilots.push(axial_cylinder(g, PILOT_RADIUS, start, m.axis.map(|u| -u), PILOT_DEPTH + 0.01));
        }
    }
    let mut rows: Vec<f64> = relays.iter().map(|m| (m.point[1] * 1e6).round() / 1e6).collect();
    rows.sort_by(f64::total_cmp);
    rows.dedup();
    for y in rows {
        let row: Vec<&Mount> = relays.iter().filter(|m| (m.point[1] - y).abs() < 1e-5).collect();
        let z0 = row.iter().map(|m| m.point[2]).fold(f64::INFINITY, f64::min);
        let z1 = row.iter().map(|m| m.point[2]).fold(f64::NEG_INFINITY, f64::max);
        let x = row.iter().map(|m| m.face[0]).fold(f64::INFINITY, f64::min);
        bosses.push(g.box_([RELAY_ROOT_X, x, y - RELAY_BAR_HALF, y + RELAY_BAR_HALF, z0, z1]));
    }
    piece = g.union_each(piece, &bosses);
    g.cut_each(piece, &pilots)
}

/// The two valve seats rooted in the flanks: the shared seat's four blind sockets and open port
/// channel, the inlet valve's on its native plate and the solenoid's on a block out to its flank.
fn valve_seats(g: &mut Graph, piece: Shape) -> Shape {
    let l = layout();
    let half_x = seat::half_x();
    let half_y = seat::half_y();
    let corners = [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)];
    let sockets: Vec<Shape> = corners
        .iter()
        .map(|&(sx, sy)| g.zcyl(seat::SOCKET_RADIUS, sx * valve::CORNER_INSET_X, sy * valve::CORNER_INSET_Y,
                                seat::SOCKET_FLOOR_Z, seat::SEAT_TOP_Z + 1.0))
        .collect();
    let sockets = g.union(sockets[0], &sockets[1..]);
    let length = 2.0 * half_y + 2.0;
    let channel = g.ycyl(valve::PORT_RADIUS + seat::PORT_AIR, 0.0, valve::PORT_CENTER_Z, -length / 2.0, length / 2.0);
    let plinth = l.rear_plumbing.joint.plinth;
    let native = rounded(g, 2, [-half_x, half_x, -half_y, half_y, -plinth, seat::SEAT_TOP_Z], seat::CORNER_RADIUS, &[0, 1, 2, 3]);
    let native = g.cut(native, &[sockets, channel]);
    let inlet = &l.parts.valve_v_a;
    let inlet = place(g, native, inlet.rotation, inlet.translation_mm);
    let vk = &l.parts.vk_solenoid;
    let mut block: Bounds = std::array::from_fn(|i| if i % 2 == 0 { f64::INFINITY } else { f64::NEG_INFINITY });
    for &(sx, sy) in &corners {
        for z in [seat::SOCKET_FLOOR_Z - seat::WALL, seat::SEAT_TOP_Z] {
            let p = vk.point([sx * half_x, sy * half_y, z]);
            for k in 0..3 {
                block[2 * k] = block[2 * k].min(p[k]);
                block[2 * k + 1] = block[2 * k + 1].max(p[k]);
            }
        }
    }
    if vk.translation_mm[0] < 0.0 {
        block[0] = -SEAT_ROOT_X;
    } else {
        block[1] = SEAT_ROOT_X;
    }
    let block = g.box_(block);
    let vk_sockets: Vec<Shape> = corners.iter().map(|&(sx, sy)| {
        let at = [sx * valve::CORNER_INSET_X, sy * valve::CORNER_INSET_Y];
        let a = vk.point([at[0], at[1], seat::SOCKET_FLOOR_Z]);
        let b = vk.point([at[0], at[1], seat::SEAT_TOP_Z + 1.0]);
        g.teardrop_y(shell().teardrop_roof_angle, seat::SOCKET_RADIUS, a[0], a[2], a[1], b[1], -1.0)
    }).collect();
    let vk_sockets = g.union(vk_sockets[0], &vk_sockets[1..]);
    let vk_channel = place(g, channel, vk.rotation, vk.translation_mm);
    let solenoid = g.cut(block, &[vk_sockets, vk_channel]);
    let piece = g.union(piece, &[inlet]);
    g.union(piece, &[solenoid])
}

/// The nameplate receiver's frame on the rear face, from the wall's inner face to past the
/// plate's face.
fn snap_lip() -> Bounds {
    let s = snap();
    let p = &layout().rear_identification.nameplate;
    let half = s.frame_width / 2.0;
    [p.center_x_mm - half, p.center_x_mm + half, p.face_y_mm - 11.0, p.face_y_mm + 1.0,
     p.center_z_mm + s.frame_bottom, p.center_z_mm + s.frame_top]
}

/// Back-top's plain lands on the rear face: the warning's field, the nameplate receiver's frame,
/// the tile rails' roots and bounds, and the keystone's land.
pub fn back_top_plain(outer: &Bounds) -> Vec<Bounds> {
    let mut plain = vec![disposal_field(outer), snap_lip()];
    plain.extend(rail_roots());
    plain.extend(rail_bounds());
    plain.push(keystone_land());
    plain
}

/// What back-top's seam trim keeps past the rear face: the receiver and the rails' bounds.
pub fn seam_lands(g: &mut Graph) -> Vec<Shape> {
    let mut lands = vec![receiver_field(g)];
    for bounds in rail_bounds() {
        lands.push(g.box_(bounds));
    }
    lands
}

/// The back-top print's raised lands: how far each sinks into the wall, the rails' raised
/// bounds beside the nameplate field, and the sliding channels kept clear of their skin.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BackTopPrint {
    pub embed: f64,
    pub label_channels: Vec<Bounds>,
    pub raised_bounds: Vec<Bounds>,
}

/// Back-top's print numbers: the warning letters' embed, the tile channels, and the raised rails.
pub fn print() -> BackTopPrint {
    BackTopPrint {
        embed: DISPOSAL_EMBED,
        label_channels: label_channels(),
        raised_bounds: rail_roots().into_iter().chain(rail_bounds()).collect(),
    }
}
