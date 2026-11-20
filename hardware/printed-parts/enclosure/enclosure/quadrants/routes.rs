//! The integral cable hooks each quadrant grows for the wire routes the wiring model lays
//! against its walls, and the tube seats that hold the fluid routes' straights.
use crate::catalog::{route_root_overlap, route_tube_tip_degrees, route_tube_wing, route_upper_wing_lift};
use crate::plan::{Graph, Op, P2, P3, Shape, Step};
use crate::quadrant::Quadrant;
use crate::shapes::place;
use crate::walls::back_top_flank_face;
use serde::Deserialize;
use serde_json::{Value, json};
use std::sync::OnceLock;

/// One hook: where its root lands and its local frame, and the cable section it seats.
#[derive(Deserialize)]
struct CableSite {
    host: String,
    origin: P3,
    outward: P3,
    profile_up: P3,
    seat_depth: f64,
    seat_height: f64,
    span: f64,
    stock: f64,
    beak: f64,
}

fn cable_sites() -> &'static [CableSite] {
    static SITES: OnceLock<Vec<CableSite>> = OnceLock::new();
    SITES.get_or_init(|| {
        hsm_enclosure_numbers::input::json("tools/hsm/assembly-docs/src/wiring/cable-sites.json")
            .expect("the wiring's cable sites parse")
    })
}

fn unit(v: P3) -> P3 {
    let length = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt();
    v.map(|k| k / length)
}

fn cross(a: P3, b: P3) -> P3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}

/// A shape placed in the frame whose axes are `x`, `y` and `z`, at `origin`.
fn frame_place(g: &mut Graph, shape: Shape, origin: P3, x: P3, y: P3, z: P3) -> Shape {
    place(g, shape, [[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]], origin)
}

/// One hook's section, out from its root along the site's outward axis and up its profile:
/// the arm, the beak over the seat and the chamfered entry under it, run along the site's span.
fn cable_hook(g: &mut Graph, site: &CableSite) -> Shape {
    let (n, p) = (unit(site.outward), unit(site.profile_up));
    let u = unit(cross(n, p));
    let span = site.span;
    let origin = std::array::from_fn(|k| site.origin[k] - u[k] * span / 2.0);
    let hook = g.prism(2, 0.0, span, cable_section(site));
    frame_place(g, hook, origin, n, p, u)
}

/// The cable hook's section is shared by its stock and underside contact regions.
fn cable_section(site: &CableSite) -> Vec<P2> {
    let (d, h, stock, beak) = (site.seat_depth, site.seat_height, site.stock, site.beak);
    let projection = d + stock;
    let floor = projection + stock;
    let roof = floor + h;
    let top = roof + beak + stock;
    let mouth = d - beak;
    let ro = route_root_overlap();
    vec![[-ro, -ro], [projection, projection], [projection, top], [d, top], [mouth, top - beak],
         [mouth, roof], [d, roof], [d, floor], [-ro, floor]]
}

/// One integral tube seat: its host, the straight of the fluid route it holds, the axis and
/// plane of the wall face its root lands on, and the tube it snaps over.
struct TubeSite {
    host: Quadrant,
    endpoints: [P3; 2],
    face_axis: usize,
    face: f64,
    outward: P3,
    bore: f64,
    wing: f64,
    upper_wing_lift: f64,
}

/// How far each seat runs along its tube, centred on its straight.
const TUBE_SEAT_SPAN: f64 = 8.0;

/// The seats in their routing order: reservoir A's fill, on its east-wall straight.
fn tube_sites() -> [TubeSite; 1] {
    [TubeSite {
        host: Quadrant::BACK_TOP,
        endpoints: [[94.31, 244.0, 258.5], [94.31, 286.0, 258.5]],
        face_axis: 0,
        face: back_top_flank_face()[1],
        outward: [-1.0, 0.0, 0.0],
        bore: 6.35,
        wing: route_tube_wing(),
        upper_wing_lift: route_upper_wing_lift(),
    }]
}

/// Removable strips span the free wing from breakaway feet on the corbelled wing.
pub fn upper_wing_support_stock(q: Quadrant) -> Vec<Value> {
    tube_sites().iter().filter(|site| site.host == q).map(|site| {
        let centre = [0, 1, 2].map(|k| (site.endpoints[0][k] + site.endpoints[1][k]) / 2.0);
        json!({"name":"Fill tube snap removable upper-wing support",
            "shape":"tube_wing_strips", "centre_source_mm":centre,
            "bore_radius_mm":site.bore / 2.0, "wing_thickness_mm":site.wing,
            "upper_wing_lift_mm":site.upper_wing_lift,
            "tip_degrees":route_tube_tip_degrees(),
            "span_y_mm":[centre[1] - TUBE_SEAT_SPAN / 2.0, centre[1] + TUBE_SEAT_SPAN / 2.0],
            "reason":"Separate contoured caps carry the upper wing from narrow breakaway feet on the lower wing. The open mouth admits a screwdriver under each cap."})
    }).collect()
}

/// One seat: a C-section whose spring wings wrap the tube to the tip angle, their noses rounded,
/// on a root out to the wall face. Where a wing faces the print bed, a corbel runs from its
/// outer nose to the host face so each course of that wing lands on the one below.
fn tube_seat(g: &mut Graph, site: &TubeSite, print_up: P3) -> Shape {
    let [first, last] = site.endpoints;
    let centre: P3 = std::array::from_fn(|k| first[k] + (last[k] - first[k]) * 0.5);
    let u = unit(std::array::from_fn(|k| last[k] - first[k]));
    let n = unit(site.outward);
    let t = unit(cross(u, n));
    let ri = site.bore / 2.0;
    let (ro, rm, nose) = (ri + site.wing, ri + site.wing / 2.0, site.wing / 2.0);
    let tip = route_tube_tip_degrees().to_radians();
    let point = |r: f64, a: f64| -> P2 { [r * a.sin(), r * a.cos()] };
    let (a, b, c, d) = (point(ro, -tip), point(ro, tip), point(ri, tip), point(ri, -tip));
    let (cp, cn) = (point(rm, tip), point(rm, -tip));
    let (qp, qn) = ([tip.cos(), -tip.sin()], [(-tip).cos(), -(-tip).sin()]);
    let span = TUBE_SEAT_SPAN;
    let lift = site.upper_wing_lift;
    let upper = |p: P2| -> P2 { [p[0] - lift, p[1]] };
    let segments = vec![
        Step::Arc(upper(point(ro, -tip / 2.0)), [-lift, ro]),
        Step::Line([0.0, ro]),
        Step::Arc(point(ro, tip / 2.0), b),
        Step::Arc([cp[0] + nose * qp[0], cp[1] + nose * qp[1]], c),
        Step::Arc(point(ri, tip / 2.0), [0.0, ri]),
        Step::Line([-lift, ri]),
        Step::Arc(upper(point(ri, -tip / 2.0)), upper(d)),
        Step::Arc(upper([cn[0] - nose * qn[0], cn[1] - nose * qn[1]]), upper(a)),
    ];
    let body = g.add(Op::ArcPrism { axis: 2, span: [0.0, span], start: upper(a), segments }, vec![], None);
    let reach = (site.face - centre[site.face_axis]).abs() + route_root_overlap();
    let mut root = g.prism(2, 0.0, span, vec![[-ro, 0.0], [ro, 0.0], [ro, reach], [-ro, reach]]);
    let growth = unit(print_up);
    let vertical = t[0] * growth[0] + t[1] * growth[1] + t[2] * growth[2];
    if (vertical.abs() - 1.0).abs() < 1e-7 {
        let sign = if vertical > 0.0 { 1.0 } else { -1.0 };
        let bed_wing_tip = if sign > 0.0 { a } else { b };
        let edge = bed_wing_tip[0];
        let face_corner = edge - sign * (reach - bed_wing_tip[1]);
        let corbel = g.prism(2, 0.0, span, vec![bed_wing_tip, [edge, reach], [face_corner, reach]]);
        root = g.union(root, &[corbel]);
    }
    let body = g.union(body, &[root]);
    let bore = g.add(Op::ArcPrism { axis: 2, span: [-0.1, span + 0.1], start: [0.0, -ri],
        segments: vec![Step::Arc([ri, 0.0], [0.0, ri]), Step::Line([-lift, ri]),
                       Step::Arc([-lift - ri, 0.0], [-lift, -ri]), Step::Line([0.0, -ri])] }, vec![], None);
    let body = g.cut(body, &[bore]);
    let origin = std::array::from_fn(|k| centre[k] - u[k] * span / 2.0);
    frame_place(g, body, origin, t, cross(u, t), u)
}

/// The quadrant with every hook and tube seat its walls host.
pub fn apply(g: &mut Graph, piece: Shape, q: Quadrant) -> Shape {
    let host = format!("enclosure-{}", q.name());
    let mut parts: Vec<Shape> = cable_sites().iter().filter(|s| s.host == host).map(|s| cable_hook(g, s)).collect();
    for site in tube_sites().iter().filter(|s| s.host == q) {
        parts.push(tube_seat(g, site, [0.0, 0.0, q.up()]));
    }
    g.union(piece, &parts)
}
