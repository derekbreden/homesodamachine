//! The lower pump retainer: a cartridge installed from below the pumps, held by two snap wings
//! whose hooks catch the front-top flanks, with the fitted skirt wells and outlet tube passages
//! cut through it. The print carries the wings relaxed; the assemblies carry them seated.
use crate::catalog::{clearance, wall_color};
use crate::plan::{Graph, P2, P3, Seg, Shape};
use crate::pump::{case, tray};
use crate::shell::shell;
use crate::spec::Box;
use hsm_enclosure_retainer_numbers::*;

/// The rigid rear head wall's scanned extent below the skirt, and where its full clearance
/// begins. The relief blends into the fitted skirt land without moving that bearing.
const AFT_BODY_Y: f64 = 27.45;
const AFT_BODY_FULL_Z: f64 = -20.0;

/// A ruled stack of case sections in the case frame, from `start` down by `steps`. A section
/// whose two transitions coincide is given its missing correspondences, so every section has
/// the same number of points in the same order.
fn stack(g: &mut Graph, start: f64, steps: &[f64], profiles: &[Vec<P2>]) -> Shape {
    let c = case();
    let collapsed = 4 * (c.arc_segments + 1) + 2;
    let at = 2 * (c.arc_segments + 1);
    let aligned = |profile: &Vec<P2>| -> Vec<P2> {
        if profile.len() == collapsed + 2 {
            return profile.clone();
        }
        assert_eq!(profile.len(), collapsed, "the pump skirt section has an unknown correspondence");
        let mut out = profile[..=at].to_vec();
        out.push(profile[at]);
        out.extend_from_slice(&profile[at + 1..]);
        out.push(profile[profile.len() - 1]);
        out
    };
    let place = |profile: &Vec<P2>, z: f64| -> Vec<P3> {
        aligned(profile).into_iter().map(|[x, y]| [c.center_x + x, c.center_y + y, z]).collect()
    };
    let mut z = start;
    let mut sections = vec![place(&profiles[0], z)];
    for (dz, profile) in steps.iter().zip(&profiles[1..]) {
        z += dz;
        sections.push(place(profile, z));
    }
    g.ruled_stack(sections)
}

fn profile_prism(g: &mut Graph, profile: &[P2], z0: f64, z1: f64) -> Shape {
    let c = case();
    g.xy_prism(z0, z1, profile.iter().map(|[x, y]| [c.center_x + x, c.center_y + y]).collect())
}

/// The case's skirt and lower body as a well `air` off its faces, filled to the skirt top.
fn case_drop_well(g: &mut Graph, air: f64) -> Shape {
    let c = case();
    let offset = c.skirt_wall - air;
    let skirt = stack(g, 0.0, &c.skirt_z_steps, &c.skirt_set(offset));
    let lower = stack(g, c.skirt_bottom_z, &c.lower_z_steps(), &c.lower_set(offset));
    let mut solid = g.union(skirt, &[lower]);
    for (z, profile) in c.stack_levels().into_iter().zip(c.stack_profiles(offset)) {
        if z < -1e-9 {
            let fill = profile_prism(g, &profile, z, 0.0);
            solid = g.union(solid, &[fill]);
        }
    }
    solid
}

/// One pump's lower well in its own frame: the skirt's upper room above the support lands, the
/// body room below them, and the outlet miters' tube openings.
fn lower_well(g: &mut Graph, trays: &[[f64; 3]]) -> Shape {
    let e = shell();
    let t = tray();
    let c = case();
    let air = e.cap_pump_air;
    let support = e.pump_skirt_support_z(trays) - e.cap_split_z(trays);
    let offset = c.skirt_wall - air;
    let skirts = c.skirt_set(offset);
    let (upper, lower) = (&skirts[1], &skirts[3]);
    let bottom = c.lower_cap_top_z - c.overcut;
    let mask = |g: &mut Graph, z0: f64, z1: f64, y0: f64, y1: f64| {
        g.box_([c.center_x - c.cutter_half_extent, c.center_x + c.cutter_half_extent,
                c.center_y + y0, c.center_y + y1, z0, z1])
    };
    let well = case_drop_well(g, air);
    let body = profile_prism(g, lower, bottom, support);
    let lower_room = g.intersect(well, &[body]);
    let [open0, open1] = t.skirt_body_open_y_bounds;
    let aft = AFT_BODY_Y + clearance(true, true, false);
    let lower_mask = g.yz_prism(c.center_x - c.cutter_half_extent, c.center_x + c.cutter_half_extent,
                              vec![[c.center_y + open0, bottom], [c.center_y + aft, bottom],
                                   [c.center_y + aft, AFT_BODY_FULL_Z], [c.center_y + open1, support],
                                   [c.center_y + open0, support]]);
    let lower_room = g.intersect(lower_room, &[lower_mask]);
    let upper_skirt = profile_prism(g, upper, support, 0.0);
    let lower_skirt = profile_prism(g, lower, support, 0.0);
    let upper_room = g.union(upper_skirt, &[lower_skirt]);
    let upper_mask = mask(g, support, 0.0, -c.cutter_half_extent, t.skirt_open_y_max);
    let upper_room = g.intersect(upper_room, &[upper_mask]);
    let room = g.union(upper_room, &[lower_room]);
    let mut room = g.translate(room, [-c.center_x, -c.center_y, 0.0]);
    let m = t.outlet_fore_miter(air);
    if m.open_half > m.body_half + 1e-9 {
        let (y1, z0) = (m.body_half, t.outlet_axis_z);
        let minus = g.box_([-m.open_half, -m.body_half, m.y0, y1, z0, 0.0]);
        let plus = g.box_([m.body_half, m.open_half, m.y0, y1, z0, 0.0]);
        room = g.union(room, &[minus, plus]);
    }
    room
}

/// The outlet tubes' circles break where the under-tangent planes leave them.
fn outlet_stations() -> P2 {
    let e = shell();
    let t = tray();
    let q = t.outlet_under_tangent(e.cap_pump_air);
    let dz = q.z - t.outlet_axis_z;
    [dz.atan2(-q.u), dz.atan2(q.u)]
}

/// The planes that carry each outlet room's wall down to its tube, tangent to the tube.
fn under_tangent_wedges(g: &mut Graph, cx: f64, cy: f64, cz: f64) -> [Shape; 2] {
    let e = shell();
    let t = tray();
    let q = t.outlet_under_tangent(e.cap_pump_air);
    let y0 = cy + t.outlet_passage_start_y(e.cap_pump_air);
    let y1 = cy + t.skirt_body_open_y_bounds[1];
    [-1.0, 1.0].map(|sx| {
        let hx = cx + sx * t.outlet_pitch / 2.0;
        let wall = hx + sx * q.wall;
        g.xz_prism(y0, y1, vec![
            [wall, cz + q.seam],
            [hx + sx * q.u, cz + q.z],
            [wall - sx, cz + q.z],
            [wall - sx, cz + q.seam],
        ])
    })
}

/// The miters that open each outlet room fore to the tube opening's width.
fn fore_miter_wedges(g: &mut Graph, cx: f64, cy: f64, cz: f64) -> [Shape; 2] {
    let e = shell();
    let t = tray();
    let m = t.outlet_fore_miter(e.cap_pump_air);
    let z0 = cz + t.outlet_axis_z - e.cap_fitting_half - 1.0;
    let reach = m.open_half + 1.0;
    [-1.0, 1.0].map(|sx| {
        g.xy_prism(z0, cz, vec![
            [cx + sx * m.body_half, cy + m.y0],
            [cx + sx * reach, cy + m.y0 + (reach - m.body_half)],
            [cx + sx * reach, cy + m.y0 - 1.0],
            [cx + sx * m.body_half, cy + m.y0 - 1.0],
        ])
    })
}

/// Each pump's air through the cartridge: its well, outlet tube passages and loading room.
fn lower_voids(g: &mut Graph, b: &Box) -> Vec<Shape> {
    let e = shell();
    let t = tray();
    let c = case();
    let trays = &b.pack.pump_trays;
    let d = datums(b);
    let source = lower_well(g, trays);
    let wall_offset = c.skirt_wall - e.cap_pump_air;
    let upper_half = c.skirt_base_half_extent - wall_offset;
    let corner_r = c.corner_r - wall_offset;
    let support = e.pump_skirt_support_z(trays);
    let stations = outlet_stations();
    let mut out = Vec::new();
    for &[cx, cy, cz] in trays {
        let mut body = g.translate(source, [cx, cy, cz]);
        for sx in [-1.0, 1.0] {
            let x = cx + sx * t.outlet_pitch / 2.0;
            let z = cz + t.outlet_axis_z;
            let y0 = cy + t.outlet_passage_start_y(e.cap_pump_air);
            let r = e.cap_fitting_half;
            let tube = g.stationed_cylinder(1, r, [x, z], [y0, d.y1 + 1.0], stations);
            let gate = g.box_([x - r, x + r, y0, d.y1 + 1.0, z, d.retainer_top_z + 1.0]);
            body = g.union(body, &[tube, gate]);
        }
        for wedge in under_tangent_wedges(g, cx, cy, cz) {
            body = g.union(body, &[wedge]);
        }
        for wedge in fore_miter_wedges(g, cx, cy, cz) {
            body = g.cut(body, &[wedge]);
        }
        let loading = g.box_([cx - upper_half, cx + upper_half, d.y0 - 1.0,
                              cy - upper_half + corner_r + 0.01, support, d.retainer_top_z + 1.0]);
        body = g.union(body, &[loading]);
        out.push(body);
    }
    out
}

/// One wing's outline across Y and the span it runs: a hook at its foot, the flank deflected
/// by `spread` at the hook as a cantilever rooted at the carrier, and a round at the root.
pub fn wing_profile(b: &Box, side: f64, spread: f64) -> (P2, Vec<Seg>) {
    let d = datums(b);
    let s = snap_datums(b);
    let points = [
        [s.wing_inner_x, s.floor_z],
        [s.hook_outer_x, s.floor_z],
        [s.wing_outer_x, s.hook_ramp_z],
        [s.wing_outer_x, s.root_z],
        [s.wing_inner_x - ROOT_RADIUS, s.root_z],
    ];
    let length = s.root_z - s.floor_z;
    let deflection = |z: f64| {
        let t = (s.root_z - z) / length;
        spread * t * t * (3.0 - t) / 2.0
    };
    let slope = |z: f64| {
        let t = (s.root_z - z) / length;
        -spread * (3.0 * t - 1.5 * t * t) / length
    };
    let bent = |[x, z]: P2| [side * (x + deflection(z)), z];
    let third = 1.0 / 3.0;
    let mut segments = Vec::new();
    for pair in points.windows(2) {
        let ([xa, za], [xb, zb]) = (pair[0], pair[1]);
        let (pa, pb) = (bent(pair[0]), bent(pair[1]));
        if (zb - za).abs() < 1e-9 || (xb - xa).abs() > 1e-9 || spread == 0.0 {
            segments.push(Seg::Line(pa, pb));
        } else {
            let da = [side * (xb - xa + slope(za) * (zb - za)), zb - za];
            let db = [side * (xb - xa + slope(zb) * (zb - za)), zb - za];
            segments.push(Seg::Cubic(
                pa,
                [pa[0] + da[0] * third, pa[1] + da[1] * third],
                [pb[0] - db[0] * third, pb[1] - db[1] * third],
                pb,
            ));
        }
    }
    let k = 4.0 / 3.0 * (std::f64::consts::PI / 8.0).tan() * ROOT_RADIUS;
    let a = points[4];
    let root = [s.wing_inner_x, s.root_z - ROOT_RADIUS];
    segments.push(Seg::Cubic(bent(a), bent([a[0] + k, a[1]]), bent([root[0], root[1] + k]), bent(root)));
    let (pa, pb) = (bent(root), bent(points[0]));
    let dz = points[0][1] - root[1];
    segments.push(Seg::Cubic(
        pa,
        [pa[0] + side * slope(root[1]) * dz / 3.0, root[1] + dz / 3.0],
        [pb[0] - side * slope(points[0][1]) * dz / 3.0, points[0][1] - dz / 3.0],
        pb,
    ));
    ([d.y0, d.y1], segments)
}

/// The retainer: the carrier between the flanks, its pump voids cut, and its two wings.
pub fn retainer(g: &mut Graph, b: &Box, seated: bool) -> Shape {
    let d = datums(b);
    let s = snap_datums(b);
    let mut body = g.xz_prism(d.y0, d.y1, vec![
        [d.x0, d.retainer_top_z],
        [d.x1, d.retainer_top_z],
        [d.x1, s.root_z],
        [s.carrier_inner_x, s.root_z],
        [s.carrier_inner_x, d.bottom_z],
        [-s.carrier_inner_x, d.bottom_z],
        [-s.carrier_inner_x, s.root_z],
        [d.x0, s.root_z],
    ]);
    for cutter in lower_voids(g, b) {
        body = g.cut(body, &[cutter]);
    }
    let spread = if seated { SEATED_SPREAD } else { RELAXED_SPREAD };
    let wings: Vec<Shape> = [-1.0, 1.0]
        .into_iter()
        .map(|side| {
            let (span, segments) = wing_profile(b, side, spread);
            g.bezier_prism(1, span, segments)
        })
        .collect();
    g.union(body, &wings)
}

/// One retainer pose, ready for the kernel.
pub struct Piece {
    pub name: &'static str,
    pub color: [f64; 3],
    pub graph: Graph,
    pub result: Shape,
    pub seated: bool,
}

pub fn piece(b: &Box, seated: bool) -> Piece {
    let mut graph = Graph::new();
    let result = retainer(&mut graph, b, seated);
    Piece {
        name: if seated { "enclosure-pump-retainer-seated" } else { "enclosure-pump-retainer" },
        color: wall_color(),
        graph,
        result,
        seated,
    }
}

