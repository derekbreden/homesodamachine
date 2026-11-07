//! The PET-GF cradle that holds the funnel's drain elbow under the frame, in the drain hole's
//! frame: the origin on the hole's axis in the frame's flat underside, +Z up and +Y aft. The
//! elbow's pocket is its scanned profile grown by the slip; each side of the block carries on up
//! as a wing through a slot in the frame's bottom web, and a flat hook at its top springs out over
//! the web, where the funnel's plug rests on it.
use crate::{Color, catalog, funnel};
use hsm_enclosure_interface::fits;
use serde::Deserialize;
use std::sync::OnceLock;

/// The frame's bottom web the hooks reach over.
pub const WEB: f64 = 3.0;
/// The wall round the elbow's pocket.
pub const WALL: f64 = 3.0;
/// The relief along the block's lower sides, and the stock left at the wing's root.
pub const LOWER_SIDE_RELIEF: f64 = 0.65;
pub const ROOT_STOCK: f64 = 3.0;
/// The air between the block's aft end and the elbow's stem body.
pub const STEM_BODY_AIR: f64 = 1.0;
/// The frame's drain hole.
pub const HOLE_D: f64 = 11.25;
/// The wings' root, and the slots' ends.
pub const WING_ROOT: f64 = -8.84;
pub const SLOT_FORE: f64 = -11.24;
pub const SLOT_AFT: f64 = 20.56239;
/// The socket's half width across X.
pub const SOCKET_HALF: f64 = 18.3;
/// A wing's leaf, its side air in the slot, and how far its hook reaches over the web.
pub const LEAF_T: f64 = 1.3;
pub const SIDE: f64 = 0.5;
pub const OVERLAP: f64 = 2.6;
/// The hook's thickness, and how far its top stands above the catch.
pub const HOOK_T: f64 = 2.75;
pub const HOOK_RISE: f64 = 0.25;
/// The slip at each slot's end, and the socket's corner.
pub const END_SLIP: f64 = 0.25;
pub const SOCKET_CORNER: f64 = 0.25;

/// The socket's half length along Y: the farther slot end with its slip.
pub fn socket_half_length() -> f64 {
    (SLOT_AFT + END_SLIP).max(-(SLOT_FORE - END_SLIP))
}

/// How far the installed cradle hangs below the frame's underside.
pub fn catch_gap() -> f64 {
    fits::slip() + fits::supported() + HOOK_RISE
}

/// The air between a hook and the web it reaches over.
pub fn web_air() -> f64 {
    fits::slip() + fits::supported()
}

#[derive(Deserialize)]
struct Profiles {
    fixed_body_y: Vec<[f64; 2]>,
    release_collet_y: Vec<[f64; 2]>,
    stem_x: Vec<[f64; 2]>,
}

/// The NeoFit stem elbow's measured reference: its bend and its turned profiles, station by
/// radius, the stem along its own X and the socket along Y.
#[derive(Deserialize)]
struct Elbow {
    bend_radius_mm: f64,
    stem_tip_x_mm: f64,
    profiles: Profiles,
}

fn elbow() -> &'static Elbow {
    static ELBOW: OnceLock<Elbow> = OnceLock::new();
    ELBOW.get_or_init(|| {
        serde_json::from_str(include_str!("../../../reference/neofit-stem-elbow/reference-parameters.json"))
            .expect("the stem elbow's reference parses")
    })
}

#[derive(Deserialize)]
struct Pose {
    translation_mm: [f64; 3],
}

#[derive(Deserialize)]
struct Snapshots {
    #[serde(rename = "drain-outlet-stem")]
    drain_outlet_stem: Pose,
}

#[derive(Deserialize)]
struct ForeRoutes {
    drain_union_corner_mm: [f64; 3],
}

/// The above-core layout's drain: the outlet stem the elbow plugs into and the union's corner.
#[derive(Deserialize)]
struct Layout {
    snapshots: Snapshots,
    fore_routes: ForeRoutes,
}

fn layout() -> &'static Layout {
    static LAYOUT: OnceLock<Layout> = OnceLock::new();
    LAYOUT.get_or_init(|| {
        serde_json::from_str(include_str!("../../../manifold-layout/above-core.json")).expect("the above-core layout parses")
    })
}

/// The elbow's profiles along a leg: the socket's (`y`), its fixed body and its collet, or the
/// stem's (any other), turned to point up.
fn profiles(leg: &str) -> (Vec<[f64; 2]>, Vec<[f64; 2]>) {
    let p = &elbow().profiles;
    if leg == "y" {
        (p.fixed_body_y.clone(), p.release_collet_y.clone())
    } else {
        let mut stem: Vec<[f64; 2]> = p.stem_x.iter().map(|&[x, r]| [-x, r]).collect();
        stem.sort_by(|a, b| a[0].total_cmp(&b[0]).then(a[1].total_cmp(&b[1])));
        (stem, vec![])
    }
}

/// The elbow's bend centre's height: the stem stands its engagement up into the funnel's bore,
/// over the plug's lift and the catch.
pub fn elbow_z() -> f64 {
    WEB + catch_gap() + funnel::PLUG_LIFT + funnel::STEM_ENGAGEMENT + elbow().stem_tip_x_mm
}

/// The block: its half width, its fore and aft ends, its bottom and its top.
pub fn block() -> [f64; 5] {
    let collar = profiles("y").0.iter().map(|p| p[1]).fold(f64::NEG_INFINITY, f64::max);
    let ry = collar + fits::slip() + WALL;
    let half = SOCKET_HALF - fits::slip() - OVERLAP - SIDE;
    let stem_y = layout().snapshots.drain_outlet_stem.translation_mm[1];
    let drain_y = layout().fore_routes.drain_union_corner_mm[1];
    let aft = SLOT_AFT.min(stem_y - drain_y - collar - STEM_BODY_AIR);
    [half, SLOT_FORE, aft, elbow_z() - ry, WING_ROOT]
}

/// A wing's spring through its slot: its free length, how far its hook bends in to pass, how far
/// its inner face travels, and the strain at its root.
pub struct Bend {
    pub free_length: f64,
    pub hook_deflection: f64,
    pub inner_face_travel: f64,
    pub root_strain: f64,
}

fn bent(points: &[[f64; 3]], length: f64, tip: f64) -> Vec<[f64; 2]> {
    let th = 1.5 * tip / length;
    points
        .iter()
        .map(|&[x, h, xn]| {
            if h <= length {
                let s = h / length;
                let d = tip * s * s * (3.0 - s) / 2.0;
                let t = tip * 3.0 / (2.0 * length) * (2.0 * s - s * s);
                [xn - d + (x - xn) * t.cos(), h + (x - xn) * t.sin()]
            } else {
                let (dx, dh) = (x - xn, h - length);
                [xn - tip + dx * th.cos() - dh * th.sin(), length + dx * th.sin() + dh * th.cos()]
            }
        })
        .collect()
}

#[allow(clippy::too_many_arguments)]
fn passage(w_in: f64, w_out: f64, tip: f64, slot_out: f64, base: f64, face: f64, top: f64, insertion_slip: f64) -> Bend {
    let (length, height) = (face - base, top - base);
    let xn = (w_in + w_out) / 2.0;
    let n = 60;
    let mut points = vec![];
    for k in 0..=n {
        for x in [w_in, w_out] {
            points.push([x, height * k as f64 / n as f64, xn]);
        }
    }
    for k in 0..=n {
        for h in [length, height] {
            points.push([w_out + (tip - w_out) * k as f64 / n as f64, h, xn]);
        }
    }
    for k in 0..=n {
        points.push([tip, length + (height - length) * k as f64 / n as f64, xn]);
    }
    let (mut need, mut travel) = (0_f64, 0_f64);
    let mut t = -top;
    while t <= WEB - face + 1e-9 {
        let (a, b) = (-base - t, WEB - base - t);
        let (mut lo, mut hi) = (0.0, 6.0);
        for _ in 0..40 {
            let mid = (lo + hi) / 2.0;
            let ok = bent(&points, length, mid).iter().all(|&[x, h]| !(a < h && h < b) || x <= slot_out - insertion_slip);
            if ok {
                hi = mid
            } else {
                lo = mid
            }
        }
        need = need.max(hi);
        for ([x, h], p) in bent(&points, length, hi).into_iter().zip(&points) {
            if p[0] == w_in && a < h && h < b {
                travel = travel.max(w_in - x);
            }
        }
        t += 0.05;
    }
    Bend { free_length: length, hook_deflection: need, inner_face_travel: travel, root_strain: 1.5 * (w_out - w_in) * need / length.powi(2) }
}

/// The wing and hook stations across X and up Z, and the slot's lanes.
pub struct Stations {
    pub half: f64,
    pub y0: f64,
    pub y1: f64,
    pub z0: f64,
    pub top: f64,
    pub w_in: f64,
    pub w_out: f64,
    pub slot_out: f64,
    pub hook_tip: f64,
    pub face: f64,
    pub hook_top: f64,
    pub bend: Bend,
    pub lane: f64,
    pub slot_in: f64,
}

/// The cradle's stations.
pub fn stations() -> Stations {
    let [half, y0, y1, z0, z1] = block();
    let (w_in, w_out) = (half - LEAF_T, half);
    let slot_out = w_out + SIDE;
    let face = WEB + catch_gap() + web_air();
    let hook_tip = slot_out + OVERLAP;
    let hook_top = face + HOOK_T;
    let bend = passage(w_in, w_out, hook_tip, slot_out, z1, face, hook_top, fits::running());
    let lane = ((bend.inner_face_travel + fits::running()) * 100.0).ceil() / 100.0;
    Stations { half, y0, y1, z0, top: z1, w_in, w_out, slot_out, hook_tip, face, hook_top, bend, lane, slot_in: w_in - lane }
}

/// A turned profile's outline, `[radius, station]`, closed on the axis and with its straight
/// runs merged.
fn turn_profile(points: &[[f64; 2]]) -> Vec<[f64; 2]> {
    let mut raw = vec![[0.0, points[0][0]]];
    raw.extend(points.iter().map(|&[t, r]| [r, t]));
    raw.push([0.0, points[points.len() - 1][0]]);
    let mut pts: Vec<[f64; 2]> = vec![];
    for p in raw {
        if pts.last().is_none_or(|q| (p[0] - q[0]).abs() > 1e-6 || (p[1] - q[1]).abs() > 1e-6) {
            pts.push(p)
        }
    }
    let mut k = 1;
    while k + 1 < pts.len() {
        let ([x0, y0], [x1, y1], [x2, y2]) = (pts[k - 1], pts[k], pts[k + 1]);
        if ((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)).abs() < 1e-9 {
            pts.remove(k);
        } else {
            k += 1;
        }
    }
    pts
}

/// The cradle's numbers, as its geometry draws it.
pub struct Cradle {
    pub block: [f64; 5],
    pub elbow_z: f64,
    pub vertical_profile: Vec<[f64; 2]>,
    pub horizontal_profile: Vec<[f64; 2]>,
    pub mouth_tangent: [f64; 2],
    pub mouth_chain: Vec<[f64; 2]>,
    pub mouth_lift: f64,
    pub shadow_height: f64,
    pub shadow_core_radius: f64,
    pub wing_x: [f64; 2],
    pub hook_tip: f64,
    pub hook_face: f64,
    pub hook_top: f64,
    pub catch_gap: f64,
    pub color: Color,
}

/// The cradle: its block, the elbow's shadow it is pocketed by, its wings and hooks.
pub fn cradle() -> Cradle {
    let slip = fits::slip();
    let b = block();
    let s = stations();
    let h = b[4] + 2.0 - elbow_z();
    let (zb, zc) = profiles("z");
    let (yb, yc) = profiles("y");
    let (mut run, mut reach) = (vec![], 0_f64);
    for [station, radius] in zb.into_iter().chain(zc.into_iter().skip(1)) {
        reach = reach.max(radius);
        run.push([station, reach + slip]);
    }
    let last = *run.last().expect("the stem's profile");
    run.push([(h + 1.0).max(last[0]), last[1]]);
    let mouth_radius = yc.iter().map(|p| p[1]).fold(yb.last().expect("the socket's profile")[1], f64::max);
    let mut horizontal = yb;
    horizontal.push([yc.last().expect("the collet's profile")[0] + slip, mouth_radius]);
    let (mut lower, mut reach) = (vec![], 0_f64);
    for &[station, radius] in &horizontal {
        reach = reach.max(radius);
        lower.push([station - slip, reach + slip]);
    }
    let (mut plan, mut reach) = (vec![], 0_f64);
    for &[station, radius] in &horizontal {
        reach = reach.max(radius + slip);
        plan.push([reach, station]);
    }
    let core = elbow().bend_radius_mm;
    let radius = core + slip;
    let mut tangents = vec![];
    for (index, &[x, y]) in plan.iter().enumerate() {
        let d2 = x * x + y * y;
        if d2 > radius * radius {
            let (a, c) = (radius * radius / d2, radius * (d2 - radius * radius).sqrt() / d2);
            let tangent = [a * x + c * y, a * y - c * x];
            tangents.push((tangent[1].atan2(tangent[0]), index, tangent));
        }
    }
    let (_, start, tangent) = tangents.into_iter().min_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1))).expect("the elbow mouth's tangent");
    let mut edge = vec![tangent];
    for &p in &plan[start..] {
        while edge.len() > 1 {
            let (a, c) = (edge[edge.len() - 2], edge[edge.len() - 1]);
            if (c[0] - a[0]) * (p[1] - c[1]) - (c[1] - a[1]) * (p[0] - c[0]) > 1e-12 {
                break;
            }
            edge.pop();
        }
        edge.push(p);
    }
    let mut vertical = vec![[0.0, run[0][1]]];
    vertical.extend_from_slice(&run);
    Cradle {
        block: b,
        elbow_z: elbow_z(),
        vertical_profile: turn_profile(&vertical),
        horizontal_profile: turn_profile(&lower),
        mouth_tangent: tangent,
        mouth_chain: edge,
        mouth_lift: (WING_ROOT - elbow_z()).max(0.0),
        shadow_height: h + 1.0,
        shadow_core_radius: core.max(run[0][1] - slip).max(horizontal[0][1]) + slip,
        wing_x: [s.w_in, s.w_out],
        hook_tip: s.hook_tip,
        hook_face: s.face,
        hook_top: s.hook_top,
        catch_gap: catch_gap(),
        color: catalog::petgf_black(),
    }
}
