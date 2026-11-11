//! Back-top's rear wall: the openings through it, what identifies the machine on it, and what it
//! carries inside, the wall hosts, valve seats and plumbing seats, and back-top's plain lands on
//! the rear face, the flats its flutes stay off.
use crate::catalog::{running, slip, supported};
use crate::disposal::disposal_field;
use crate::layout::{Pose, layout};
use crate::plan::{Bounds, Flange, Graph, Op, P2, P3, Shape, Snap};
use crate::quadrant::{Quadrant, sorted};
use crate::rear_wall::{
    FIELD_PROUD, PLATE_HEIGHT, PLATE_THICK, PLATE_WIDTH, c14, keystone, keystone_land,
    label_channels, rail_bounds, rail_roots,
};
use crate::shapes::{place, rounded};
use crate::shell::{DISPOSAL_EMBED, WALL, back_top_ceiling_face, shell};
use crate::spec::Box;
use crate::supports::supports;
use crate::valves::{seat, valve};
use crate::walls::back_top_flank_face;
use serde::{Deserialize, Serialize};
use std::rc::Rc;

#[path = "../../nameplate/snap_dimensions.rs"]
mod snap_dimensions;

/// The wet ports' bores run through the rear wall from inside its relief to past its face.
pub const WET_PORT_Y: P2 = [458.0, 472.3];

/// The wall's hosted insert bosses and their pilots.
pub const BOSS_RADIUS: f64 = 5.0;
const PILOT_RADIUS: f64 = 2.0;
/// The PSU's native hole half-spacings and each relay end bar's half-width.
const PSU_HOLES: P2 = [16.5, 49.0];
pub const RELAY_BAR_HALF: f64 = 5.0;

/// The PSU's ceiling bosses root at this plane, the relays' bosses and bars this far into the
/// west flank, and the valve seats this far into their flanks.
const PSU_ROOT_Z: f64 = 349.25;
const RELAY_ROOT_X: f64 = -98.52;
const SEAT_ROOT_X: f64 = 98.51;

/// The rear wall's features on back-top, after its wells; `keep_clear` is the wells' pockets.
pub fn apply(g: &mut Graph, mut piece: Shape, b: &Box, keep_clear: Option<Shape>) -> Shape {
    let wall = &layout().rear_wall;
    let relief = rounded(
        g,
        2,
        wall.interior_panel_relief.bounds(),
        0.0,
        &[0, 1, 2, 3],
    );
    let relief = g.feature(relief, "rear-interior-relief", "Rear interior panel relief", &[]);
    piece = g.cut(piece, &[relief]);
    for port in &wall.wet_ports {
        let bore = g.teardrop_y(
            shell().teardrop_roof_angle,
            port.bore_diameter_mm / 2.0,
            port.center_x_mm,
            port.center_z_mm,
            WET_PORT_Y[0],
            WET_PORT_Y[1].max(b.exterior_bounds()[3] + running()),
            -1.0,
        );
        let bore = g.feature(bore, "rear-bulkhead-openings", "Rear fluid bulkhead openings", &[]);
        piece = g.cut(piece, &[bore]);
    }
    let stock = g.box_(c14_stock_bounds());
    let outline = g.silhouette(b.exterior_bounds());
    let stock = g.intersect(stock, &[outline]);
    let stock = g.feature(stock, "power-inlet-mount", "Power inlet mount and tunnel", &["c14-inlet"]);
    piece = g.union(piece, &[stock]);
    let inlet = g.scoped("power-inlet-mount", "Power inlet mount and tunnel", &["c14-inlet"], |g| c14_cutters(g, b.exterior_bounds()[3]));
    piece = g.cut(piece, &inlet);
    piece = g.scoped("keystone-mount", "Ethernet keystone mount", &["keystone"], |g| keystone(g, piece, &b.pack.core_holds, keep_clear));
    piece = g.scoped("identification-mounts", "Nameplate and connector label mounts", &["nameplate"], |g| identify(g, piece, b));
    piece = hosts(g, piece);
    piece = g.scoped("rear-valve-seats", "Rear valve mounting seats", &["valve-v-a", "vk-solenoid"], |g| valve_seats(g, piece));
    for ((id, label, part), support) in [
        ("asse-receiver", "ASSE chain snap receiver", "discharge-chain"),
        ("pisco-receiver", "Pisco regulator snap receiver", "gas-regulator"),
        ("flow-meter-receiver", "Flow meter snap receiver", "digiten-flow"),
        ("water-regulator-receiver", "Water regulator snap receiver", "flow-regulator"),
    ].into_iter().zip(supports(g)) {
        let support = g.feature(support, id, label, &[part]);
        piece = g.union(piece, &[support]);
    }
    let tips = g.scoped("receiver-catch-pockets", "Snap receiver catch pockets", &[], crate::supports::tip_clearances);
    piece = g.cut(piece, &tips);
    // The measured inlet opening stays clear after every integral mount joins.
    g.cut(piece, &inlet)
}

/// The internal inlet tunnel joins the rear wall, west flank and ceiling as plain stock.
pub fn c14_stock_bounds() -> Bounds {
    let plan = &layout().rear_wall.dry_openings.c14;
    let [x, y, z] = layout().parts.c14_inlet.translation_mm;
    let floor = y + c14::RIM_PROUD;
    let half_x = (c14::FLANGE_W / 2.0 + plan.profile_clearance_mm + WALL)
        .max(plan.cord_access_width_mm / 2.0 + c14::TUNNEL_WALL);
    let half_z = (c14::POCKET_H / 2.0 + plan.profile_clearance_mm + WALL)
        .max(plan.cord_access_height_mm / 2.0 + c14::TUNNEL_WALL);
    [
        (x - half_x).min(back_top_flank_face()[0]),
        x + half_x,
        floor - plan.flange_pocket_depth_mm,
        floor + c14::PILOT_DEPTH,
        z - half_z - supported(),
        (z + half_z).max(back_top_ceiling_face() + WALL),
    ]
}

/// The inlet loads from inside; its rim seats on the pocket floor around the cord passage.
/// The blind insert pilots open into that same internal pocket and leave the rear face plain.
fn c14_cutters(g: &mut Graph, rear_face: f64) -> Vec<Shape> {
    let plan = &layout().rear_wall.dry_openings.c14;
    let [x, y, z] = layout().parts.c14_inlet.translation_mm;
    let floor = y + c14::RIM_PROUD;
    let flange = g.add(
        Op::InletFlange(flange(
            plan.profile_clearance_mm,
            [floor - plan.flange_pocket_depth_mm - 1.0, floor],
        )),
        vec![],
        None,
    );
    let flange = g.translate(flange, [x, 0.0, z]);
    let flange = supported_cut(g, flange, -1.0);
    let (hw, hh) = (
        plan.cord_access_width_mm / 2.0,
        plan.cord_access_height_mm / 2.0,
    );
    let cord = rounded(
        g,
        1,
        [
            x - hw,
            x + hw,
            floor - 0.01,
            rear_face + 1.0,
            z - hh,
            z + hh,
        ],
        plan.cord_access_radius_mm,
        &[0, 1, 2, 3],
    );
    let cord = supported_cut(g, cord, -1.0);
    let mut cuts = vec![flange, cord];
    for dx in [-plan.mount_pitch_mm / 2.0, plan.mount_pitch_mm / 2.0] {
        cuts.push(g.ycyl(
            PILOT_RADIUS,
            x + dx,
            z,
            floor - 0.01,
            floor + c14::PILOT_DEPTH,
        ));
    }
    cuts
}

/// The flange outline's right-top landmarks: a long flat, the knuckle round at its end, the
/// external tangent it shares with the ear arc, and the nose.
fn flange(clearance: f64, span: P2) -> Flange {
    use c14::*;
    let ear_r = FLANGE_W / 2.0 - EAR_CX;
    let h = POCKET_H / 2.0;
    let a = FLANGE_W / 2.0 - (FLANGE_END_CHORD * FLANGE_END_CHORD - h * h).sqrt();
    let kr = KNUCKLE_R;
    let shoulder = [a, h - kr];
    let (dx, dz) = (EAR_CX - shoulder[0], 0.0 - shoulder[1]);
    let reach = dx.hypot(dz);
    assert!(
        reach > (ear_r - kr).abs(),
        "the flange shoulder and ear rounds swallow their tangent"
    );
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

/// A cavity with extra room at its supported face, along the piece's build direction.
fn supported_cut(g: &mut Graph, cutter: Shape, up: f64) -> Shape {
    let lifted = g.translate(cutter, [0.0, 0.0, up * supported()]);
    g.union(cutter, &[lifted])
}

/// A rectangle across Y about `(x, z)`, over a Y span.
fn rect_cut_y(g: &mut Graph, x: f64, z: f64, w: f64, h: f64, [y0, y1]: P2) -> Shape {
    rounded(
        g,
        1,
        [x - w / 2.0, x + w / 2.0, y0, y1, z - h / 2.0, z + h / 2.0],
        0.0,
        &[0, 1, 2, 3],
    )
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
    let pocket = rect_cut_y(
        g,
        x,
        z + POCKET_RISE,
        keystone_pocket_width(),
        pocket_h,
        [back - 0.01, y_lip + 0.01],
    );
    let top = z + ah / 2.0;
    let rise = LIP_D * EASE_DEG.to_radians().tan();
    let ease = g.prism(
        0,
        x - aw / 2.0,
        x + aw / 2.0,
        vec![
            [y_face + 0.01, top],
            [y_lip + 0.01, top],
            [y_lip + 0.01, top + rise],
            [
                y_face + 0.01 - EASE_SHOULDER * LIP_D / rise,
                top + EASE_SHOULDER,
            ],
            [y_face + 0.01, top + EASE_SHOULDER],
        ],
    );
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
    let block = g.box_([
        x0,
        x1,
        fore,
        root + 0.01,
        centre_z - half_z,
        centre_z + half_z,
    ]);
    let mut stock = supported_cut(g, block, up);
    let top = centre_z + half_z;
    let roof = g.prism(
        0,
        x0,
        x1,
        vec![[root, top], [fore, top], [root, top + root - fore]],
    );
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
            g.box_([
                x - POCKET_W / 2.0 - growth,
                x + POCKET_W / 2.0 + growth,
                y_back,
                y_back + proud,
                za,
                zb,
            ])
        })
        .collect();
    let catches = g.union(catches[0], &catches[1..]);
    let piece = g.union(piece, &[stock]);
    let piece = g.cut(piece, &[cutter]);
    g.union(piece, &[catches])
}

/// The nameplate's dimension record, shared with the plate it receives.
fn snap() -> Rc<Snap> {
    Rc::new(Snap::read(&snap_dimensions::dimensions(
        PLATE_WIDTH,
        PLATE_HEIGHT,
        PLATE_THICK,
        slip(),
        supported(),
        FIELD_PROUD,
    )))
}

/// The printable contact profiles of the receiver, in the back-top source frame.
pub fn nameplate_print_support(bed_source_z_mm: f64) -> serde_json::Value {
    let s = snap();
    let p = &layout().rear_identification.nameplate;
    serde_json::json!({
        "name": "Removable exterior nameplate support",
        "shape": "nameplate_panel",
        "center_x_mm": p.center_x_mm,
        "center_z_mm": p.center_z_mm,
        "face_y_mm": p.face_y_mm,
        "frame_top_mm": p.center_z_mm + s.frame_top,
        "frame_half_width_mm": s.frame_width / 2.0,
        "frame_corner_mm": s.frame_corner,
        "field_proud_mm": s.field_proud,
        "mouth_floor_mm": p.center_z_mm - s.mouth_height / 2.0 - s.supported,
        "mouth_half_width_mm": s.mouth_width / 2.0,
        "mouth_corner_mm": s.corner + s.slip,
        "bed_source_z_mm": bed_source_z_mm,
        "reason": "Both rounded contact bands carry on a separate bed-rooted panel with an open aft removal path."
    })
}

/// The nameplate's four-screw receiver on the rear face: its frame stock fused, its mouth and
/// insert pilots cut, with the plate's back at its seat.
fn nameplate_receiver(g: &mut Graph, piece: Shape) -> Shape {
    let s = snap();
    let p = &layout().rear_identification.nameplate;
    let shift = [p.center_x_mm, p.face_y_mm - s.thick, p.center_z_mm];
    let half = s.frame_width / 2.0;
    let stock = g.add(
        Op::NameplateStock(s.clone()),
        vec![],
        Some([
            -half,
            half,
            s.insert_stock_rear,
            s.thick,
            s.frame_bottom,
            s.frame_top,
        ]),
    );
    let stock = g.translate(stock, shift);
    let cuts = g.add(
        Op::NameplateCuts(s.clone()),
        vec![],
        Some([
            -half,
            half,
            s.pilot_rear,
            s.thick,
            s.frame_bottom,
            s.frame_top,
        ]),
    );
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
fn identify(g: &mut Graph, mut piece: Shape, b: &Box) -> Shape {
    for mut channel in label_channels() {
        channel[3] = channel[3].max(b.exterior_bounds()[3] + running());
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
pub struct Mount {
    pub point: P3,
    pub face: P3,
    pub root: P3,
    pub axis: P3,
    pub threaded: bool,
    pub pilot_radius: f64,
    pub pilot_depth: f64,
}

/// A hosted part's mounting holes, its native hole pattern placed by its pose.
fn mounts(
    pose: &Pose,
    holes: &[P2],
    setback: f64,
    pilot_radius: f64,
    pilot_depth: f64,
    root: impl Fn(P3) -> P3,
) -> Vec<Mount> {
    let axis = pose.vector([0.0, 0.0, 1.0]);
    holes.iter()
        .map(|&[x, y]| {
            let point = pose.point([x, y, 0.0]);
            let face = std::array::from_fn(|k| point[k] - setback * axis[k]);
            Mount {
                point,
                face,
                root: root(point),
                axis,
                threaded: true,
                pilot_radius,
                pilot_depth,
            }
        })
        .collect()
}

/// A cylinder along a principal axis from `root`, `length` along `axis`.
fn axial_cylinder(g: &mut Graph, radius: f64, root: P3, axis: P3, length: f64) -> Shape {
    let k = (0..3)
        .find(|&k| axis[k].abs() > 1e-8)
        .expect("a host axis has a direction");
    assert!(
        (0..3).all(|j| j == k || axis[j].abs() <= 1e-8),
        "a wall host axis is no longer principal"
    );
    let [a, b]: [f64; 2] = std::array::from_fn(|i| root[if i < k { i } else { i + 1 }]);
    g.cylinder(k, radius, a, b, root[k], root[k] + axis[k] * length)
}

/// The parts the wall hosts, each with its mounting holes: the PSU on ceiling bosses, then each
/// relay on west-flank bosses.
pub fn wall_mounts() -> Vec<(&'static str, Vec<Mount>)> {
    use crate::rear_wall::hosts::{PILOT_DEPTH, RELAY_PILOT_RADIUS, RELAY_SETBACK, relay_holes, relay_pilot_depth};
    let parts = &layout().parts;
    let holes = relay_holes();
    let relay = |pose| {
        mounts(
            pose,
            &holes,
            RELAY_SETBACK,
            RELAY_PILOT_RADIUS,
            relay_pilot_depth(),
            |p| [RELAY_ROOT_X, p[1], p[2]],
        )
    };
    vec![
        (
            "psu",
            mounts(
                &parts.psu,
                &[[-PSU_HOLES[0], -PSU_HOLES[1]], [-PSU_HOLES[0], PSU_HOLES[1]],
                  [PSU_HOLES[0], -PSU_HOLES[1]], [PSU_HOLES[0], PSU_HOLES[1]]],
                0.0,
                PILOT_RADIUS,
                PILOT_DEPTH,
                |p| [p[0], p[1], PSU_ROOT_Z],
            ),
        ),
        ("relay-1", relay(&parts.relay_1)),
        ("relay-2", relay(&parts.relay_2)),
    ]
}

/// Each relay end's wall-rooted bar joins the corner posts beneath the PCB.
pub fn relay_bars(hosted: &[(&str, Vec<Mount>)]) -> Vec<Bounds> {
    let mut bars = Vec::new();
    for end in [0..2, 2..4] {
        let row: Vec<_> = hosted.iter().filter(|(part, _)| *part != "psu")
            .flat_map(|(_, mounts)| &mounts[end.clone()]).collect();
        let low = |axis| row.iter().map(|m| m.point[axis]).fold(f64::INFINITY, f64::min);
        let high = |axis| row.iter().map(|m| m.point[axis]).fold(f64::NEG_INFINITY, f64::max);
        let face = row.iter().map(|m| m.face[0]).fold(f64::INFINITY, f64::min);
        bars.push([RELAY_ROOT_X, face, low(1) - RELAY_BAR_HALF,
                   high(1) + RELAY_BAR_HALF, low(2), high(2)]);
    }
    bars
}

/// The PSU's ceiling bosses and the relays' bearing posts, each end's bar, and
/// every threaded hole's pilot.
fn hosts(g: &mut Graph, mut piece: Shape) -> Shape {
    let hosted = wall_mounts();
    let mut bosses = Vec::new();
    let mut pilots = Vec::new();
    for (part, mounts) in &hosted {
      for m in mounts {
        let length: f64 = (0..3).map(|k| (m.face[k] - m.root[k]) * m.axis[k]).sum();
        let boss = axial_cylinder(g, BOSS_RADIUS, m.root, m.axis, length);
        bosses.push(g.feature(boss, format!("{part}-mount"), format!("{part} mounting bosses"), &[part]));
        if m.threaded {
            let start = std::array::from_fn(|k| m.face[k] + 0.01 * m.axis[k]);
            let pilot = axial_cylinder(
                g,
                m.pilot_radius,
                start,
                m.axis.map(|u| -u),
                m.pilot_depth + 0.01,
            );
            pilots.push(g.feature(pilot, format!("{part}-mount"), format!("{part} mounting bosses"), &[part]));
        }
      }
    }
    for bounds in relay_bars(&hosted) {
        let bar = g.box_(bounds);
        bosses.push(g.feature(bar, "relay-mount-bars", "Relay mount bearing bars", &["relay-1", "relay-2"]));
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
        .map(|&(sx, sy)| {
            g.zcyl(
                seat::SOCKET_RADIUS,
                sx * valve::CORNER_INSET_X,
                sy * valve::CORNER_INSET_Y,
                seat::SOCKET_FLOOR_Z,
                seat::SEAT_TOP_Z + 1.0,
            )
        })
        .collect();
    let sockets = g.union(sockets[0], &sockets[1..]);
    let length = 2.0 * half_y + 2.0;
    let channel = g.ycyl(
        valve::PORT_RADIUS + seat::PORT_AIR,
        0.0,
        valve::PORT_CENTER_Z,
        -length / 2.0,
        length / 2.0,
    );
    let plinth = l.rear_plumbing.joint.plinth;
    let native = rounded(
        g,
        2,
        [-half_x, half_x, -half_y, half_y, -plinth, seat::SEAT_TOP_Z],
        seat::CORNER_RADIUS,
        &[0, 1, 2, 3],
    );
    let native = g.cut(native, &[sockets, channel]);
    let inlet = &l.parts.valve_v_a;
    let inlet = place(g, native, inlet.rotation, inlet.translation_mm);
    let vk = &l.parts.vk_solenoid;
    let block = g.box_(solenoid_seat_bounds());
    let vk_sockets: Vec<Shape> = corners
        .iter()
        .map(|&(sx, sy)| {
            let at = [sx * valve::CORNER_INSET_X, sy * valve::CORNER_INSET_Y];
            let a = vk.point([at[0], at[1], seat::SOCKET_FLOOR_Z]);
            let b = vk.point([at[0], at[1], seat::SEAT_TOP_Z + 1.0]);
            g.teardrop_y(
                shell().teardrop_roof_angle,
                seat::SOCKET_RADIUS,
                a[0],
                a[2],
                a[1],
                b[1],
                -1.0,
            )
        })
        .collect();
    let vk_sockets = g.union(vk_sockets[0], &vk_sockets[1..]);
    let vk_channel = place(g, channel, vk.rotation, vk.translation_mm);
    let solenoid = g.cut(block, &[vk_sockets, vk_channel]);
    let piece = g.union(piece, &[inlet]);
    g.union(piece, &[solenoid])
}

/// The solenoid seat stock whose exposed underside takes removable support.
pub fn solenoid_seat_bounds() -> Bounds {
    let vk = &layout().parts.vk_solenoid;
    let (half_x, half_y) = (seat::half_x(), seat::half_y());
    let mut bounds: Bounds = std::array::from_fn(|i| {
        if i % 2 == 0 {
            f64::INFINITY
        } else {
            f64::NEG_INFINITY
        }
    });
    for (sx, sy) in [(-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)] {
        for z in [seat::SOCKET_FLOOR_Z - seat::WALL, seat::SEAT_TOP_Z] {
            let p = vk.point([sx * half_x, sy * half_y, z]);
            for k in 0..3 {
                bounds[2 * k] = bounds[2 * k].min(p[k]);
                bounds[2 * k + 1] = bounds[2 * k + 1].max(p[k]);
            }
        }
    }
    if vk.translation_mm[0] < 0.0 {
        bounds[0] = -SEAT_ROOT_X;
    } else {
        bounds[1] = SEAT_ROOT_X;
    }
    bounds
}

/// The nameplate receiver's frame on the rear face, from the wall's inner face to past the
/// plate's face.
pub fn nameplate_receiver_bounds() -> Bounds {
    let s = snap();
    let p = &layout().rear_identification.nameplate;
    let half = s.frame_width / 2.0;
    [
        p.center_x_mm - half,
        p.center_x_mm + half,
        p.face_y_mm - 11.0,
        p.face_y_mm + 1.0,
        p.center_z_mm + s.frame_bottom,
        p.center_z_mm + s.frame_top,
    ]
}

/// Back-top's plain lands on the rear face: the warning's field, the nameplate receiver's frame,
/// the tile rails' roots and bounds, and the keystone's land.
pub fn back_top_plain(outer: &Bounds) -> Vec<Bounds> {
    let mut plain = vec![disposal_field(outer), nameplate_receiver_bounds()];
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
