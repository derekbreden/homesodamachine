//! The integral cable hooks each quadrant grows for the wire routes the wiring model lays
//! against its walls, and the tube seats that hold the fluid routes' straights.
use crate::catalog::{route_root_overlap, route_tube_tip_degrees};
use crate::plan::{Bounds, Graph, Op, P2, P3, Shape, Step};
use crate::quadrant::Quadrant;
use crate::shapes::place;
use crate::walls::back_top_flank_face;
use serde::Deserialize;
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
        wing: 2.40,
    }]
}

/// One seat: a C-section whose spring wings wrap the tube to the tip angle, their noses rounded,
/// on a root out to the wall face; a seat whose section stands across the print grows a gusset as
/// tall as it is deep under its root, so the root never overhangs.
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
    let segments = vec![
        Step::Arc([0.0, ro], b),
        Step::Arc([cp[0] + nose * qp[0], cp[1] + nose * qp[1]], c),
        Step::Arc([0.0, ri], d),
        Step::Arc([cn[0] + -nose * qn[0], cn[1] + -nose * qn[1]], a),
    ];
    let body = g.add(Op::ArcPrism { axis: 2, span: [0.0, span], start: a, segments }, vec![], None);
    let reach = (site.face - centre[site.face_axis]).abs() + route_root_overlap();
    let mut root = g.prism(2, 0.0, span, vec![[-ro, 0.0], [ro, 0.0], [ro, reach], [-ro, reach]]);
    let growth = unit(print_up);
    let vertical = t[0] * growth[0] + t[1] * growth[1] + t[2] * growth[2];
    if (vertical.abs() - 1.0).abs() < 1e-7 {
        let sign = if vertical > 0.0 { 1.0 } else { -1.0 };
        let edge = -sign * ro;
        let gusset = g.prism(2, 0.0, span, vec![[edge, 0.0], [edge, reach], [edge - sign * reach, reach]]);
        root = g.union(root, &[gusset]);
    }
    let body = g.union(body, &[root]);
    let bore = g.cylinder(2, ri, 0.0, 0.0, -0.1, span + 0.1);
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

/// Accessible hook lands and the tube seat's outer underside, clear of the fitted bore roof.
pub fn underside_support_regions(q: Quadrant) -> Vec<(String, Bounds)> {
    let host = format!("enclosure-{}", q.name());
    let mut regions = Vec::new();
    let air = crate::catalog::running();
    for (index, site) in cable_sites().iter().filter(|site| site.host == host).enumerate() {
        let (n, p) = (unit(site.outward), unit(site.profile_up));
        let u = unit(cross(n, p));
        let section = cable_section(site);
        for (edge, a) in section.iter().enumerate() {
            let b = section[(edge+1)%section.len()];
            let (dx, dy) = (b[0]-a[0], b[1]-a[1]);
            if dy*n[2]-dx*p[2] < 0.99*dx.hypot(dy) {continue;}
            let points: Vec<P3> = [*a,b].into_iter().flat_map(|point| [-0.5,0.5].map(|end| {
                std::array::from_fn(|k| site.origin[k]+n[k]*point[0]+p[k]*point[1]+u[k]*site.span*end)
            })).collect();
            let mut bounds: Bounds = std::array::from_fn(|i| {
                let values = points.iter().map(|point|point[i/2]);
                if i%2==0 {values.fold(f64::INFINITY,f64::min)} else {values.fold(f64::NEG_INFINITY,f64::max)}
            });
            bounds[4] -= air;
            bounds[5] += air;
            regions.push((format!("Accessible cable hook {} land {edge}",index+1),bounds));
        }
    }
    for site in tube_sites().iter().filter(|site|site.host==q) {
        let centre: P3 = std::array::from_fn(|k|(site.endpoints[0][k]+site.endpoints[1][k])/2.0);
        let u = unit(std::array::from_fn(|k|site.endpoints[1][k]-site.endpoints[0][k]));
        let n = unit(site.outward);
        let t = unit(cross(u,n));
        let outer = site.bore/2.0+site.wing;
        let reach = (site.face-centre[site.face_axis]).abs()+route_root_overlap();
        let half: P3 = std::array::from_fn(|k|
            (outer+reach)*t[k].abs()+outer.max(reach)*n[k].abs()+TUBE_SEAT_SPAN/2.0*u[k].abs());
        let mut bounds: Bounds = std::array::from_fn(|i|
            centre[i/2]+if i%2==0 {-half[i/2]} else {half[i/2]});
        bounds[4] = centre[2]+outer*std::f64::consts::FRAC_1_SQRT_2;
        regions.push(("Accessible tube seat outer underside".into(),bounds));
    }
    regions
}
