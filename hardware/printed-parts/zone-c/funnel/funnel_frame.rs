//! The removable frame the funnel drops into, cut round the funnel's forming air, in the printed
//! underside's coordinates: its STEP, model file, payload and STL, and the numbers the installed
//! machine places it by.
//!
//!     funnel-frame [<output directory>]
#[allow(dead_code)]
mod funnel_geometry;
#[allow(dead_code)]
mod zone_files;
use anyhow::Result;
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use hsm_kernel::write::PrintOutput;
use hsm_zone_c_numbers::catalog;
use hsm_zone_c_numbers::frame::{Frame, SEATING_RELIEF, back_axis, frame};
use serde_json::json;
use sha2::{Digest, Sha256};

fn block(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1))
}

fn cylinder(x: f64, y: f64, r: f64, z0: f64, z1: f64) -> Result<Solid> {
    Solid::cylinder(v3(x, y, z0), V3::Z, r, z1 - z0)
}

fn rounded(w: f64, d: f64, r: f64, x: f64, y: f64, z0: f64, z1: f64) -> Result<Solid> {
    let plan = Profile::new(Loop::rounded_rect(v2(x, y), w, d, r)?);
    Plane::XY.at(v3(0.0, 0.0, z0)).extrude(&plan, z1 - z0)
}

/// Square front corners and seam shoulders, with rounded aft corners.
fn blank_plan(n: &Frame, width: f64) -> Result<Profile> {
    let front = n.front;
    let back = n.back;
    let step = n.rear_start;
    let (limit_l, limit_r) = n.rear_limits;
    let r = n.corner_radius;
    let fl = -width / 2.0;
    let fr = width / 2.0;
    let left = fl.max(limit_l);
    let right = fr.min(limit_r);
    let mut edges = vec![];
    let mut at = v2(fl, front);
    let mut line = |b: V2| {
        if at != b {
            edges.push(Seg::Line { a: at, b });
            at = b;
        }
    };
    line(v2(fr, front));
    if fr > right {
        line(v2(fr, step));
        line(v2(right, step));
    }
    line(v2(right, back - r));
    let a = at;
    let b = v2(right - r, back);
    edges.push(Seg::Arc { a, b, c: v2(right - r, back - r), ccw: true });
    edges.push(Seg::Line { a: b, b: v2(left + r, back) });
    edges.push(Seg::Arc { a: v2(left + r, back), b: v2(left, back - r),
                          c: v2(left + r, back - r), ccw: true });
    at = v2(left, back - r);
    if left > fl {
        edges.push(Seg::Line { a: at, b: v2(left, step) });
        edges.push(Seg::Line { a: v2(left, step), b: v2(fl, step) });
        at = v2(fl, step);
    }
    edges.push(Seg::Line { a: at, b: v2(fl, front) });
    Ok(Profile::new(Loop::new(edges)?))
}

fn brim(n: &Frame) -> Result<Solid> {
    let (x, y) = n.brim_half_size;
    let r = n.brim_radius;
    let a = v2(-x, -y);
    let b = v2(x, -y);
    let c = v2(x, y - r);
    let d = v2(x - r, y);
    let e = v2(-x + r, y);
    let f = v2(-x, y - r);
    let plan = Profile::new(Loop::new(vec![
        Seg::Line { a, b }, Seg::Line { a: b, b: c },
        Seg::Arc { a: c, b: d, c: v2(x - r, y - r), ccw: true },
        Seg::Line { a: d, b: e },
        Seg::Arc { a: e, b: f, c: v2(-x + r, y - r), ccw: true },
        Seg::Line { a: f, b: a },
    ])?);
    Plane::XY.at(v3(0.0, 0.0, n.seat))
        .extrude(&plan, n.roof_top + 1.0 - n.seat)
}

/// The socket leaves a raised T around the stem and a lower ledge beyond each wing slot.
fn socket(n: &Frame) -> Result<Solid> {
    let (w, d) = n.socket_size;
    let (x, y) = n.drain_xy;
    let r = n.socket_radius;
    let z0 = n.socket_z;
    let z1 = z0 + n.socket_height;
    let (h, grow) = n.socket_flare;
    let section = |w, d, r, z| -> Result<_> {
        Ok(Profile::new(Loop::rounded_rect(v2(x, y), w, d, r)?)
            .place(&Plane::XY.at(v3(0.0, 0.0, z))))
    };
    let lead = Solid::loft(&[
        section(w, d, r, z1 - h)?,
        section(w + 2.0 * grow, d + 2.0 * grow, r + grow, z1)?,
    ])?;
    let pocket = rounded(w, d, r, x, y, z0, z1)?.union(&lead)?;
    let wing_front = y + n.slot_y.0;
    let inner = n.slot_x.0;
    let (left, right) = (x - w / 2.0, x + w / 2.0);
    let (front, back) = (y - d / 2.0, y + d / 2.0);
    let floor_plan = Profile::new(Loop::polygon(&[
        v2(left, front), v2(right, front), v2(right, wing_front), v2(x + inner, wing_front),
        v2(x + inner, back), v2(x - inner, back), v2(x - inner, wing_front), v2(left, wing_front),
    ]));
    let floor = Plane::XY.at(v3(0.0, 0.0, z0)).extrude(&floor_plan, n.socket_floor_z - z0)?;
    pocket.cut(&floor)
}

/// Under each back notch the flange keeps a wedge whose face rises outward at the back seat's
/// slope, one slip square to back-top's ledge, from the body out to the roof's edge and aft to
/// the body's corbel. Upright, the face prints without support.
fn back_seats(n: &Frame, aft_corbel: &Solid) -> Result<Vec<Solid>> {
    let floor = n.roof_floor + SEATING_RELIEF;
    let lift = n.back_seat_air * (1.0 + n.back_seat_slope.powi(2)).sqrt();
    let face = |a: f64| n.roof_floor - (n.back_seat_flank - a) * n.back_seat_slope + lift;
    let roof = Plane::XY.at(v3(0.0, 0.0, -1.0)).extrude(&blank_plan(n, n.roof_width)?, floor + 3.0)?;
    let mut seats = vec![];
    for &(x, y, _, host, side, front, _) in &n.screws {
        if front {
            continue;
        }
        let inner = x.abs() - host - n.slide_slip - 1.0;
        let outer = n.back_seat_flank;
        let section = Profile::new(Loop::polygon(&[
            v2(side * inner, face(inner)), v2(side * outer, face(outer)),
            v2(side * outer, floor + 1.0), v2(side * inner, floor + 1.0),
        ]));
        let start = y - n.ledge_pad_half_y - n.slide_slip;
        let wedge = Plane::XZ.at(v3(0.0, n.back + 1.0, 0.0)).extrude(&section, n.back + 1.0 - start)?;
        seats.push(wedge.intersect(&roof)?.cut(aft_corbel)?);
    }
    Ok(seats)
}

/// A back screw's line in the frame's own frame: where it leaves the wedge's face, where its
/// head seats, and its axis, square to the seat, up and inward. The frame stands one slip off
/// back-top's seat, so the line is the insert's own, lifted by the drop that closes both seats.
pub fn back_line(n: &Frame, x: f64, y: f64, side: f64) -> (V3, V3, V3) {
    let lift = n.back_seat_air * (1.0 + n.back_seat_slope.powi(2)).sqrt();
    let face = v3(x, y, n.roof_floor - (n.back_seat_flank - x.abs()) * n.back_seat_slope + lift);
    let axis = V3::from(back_axis(side));
    (face, face + (n.back_screw_grip - n.back_seat_air) * axis, axis)
}

/// Each back screw's clearance bore square to the wedge's face, and a trough the head seats in.
/// The trough's floor is the head seat, square to the screw; it runs outward and up until it
/// leaves through the frame's top, and on its inner side a face along the screw opens the way a
/// driver comes in. Neither face meets the top at less than a right angle.
fn back_screw_cuts(n: &Frame) -> Result<Vec<Solid>> {
    let mut cuts = vec![];
    let top = n.seat + 1.0;
    for &(x, y, _, _, side, front, _) in &n.screws {
        if front {
            continue;
        }
        let (face, head, axis) = back_line(n, x, y, side);
        let bore = Solid::cylinder(face - 2.0 * axis, axis, n.screw_clear_radius,
                                   (head - face).dot(axis) + 2.5)?;
        // Across the face, up and outward.
        let across = v3(side * axis.z, 0.0, -side * axis.x);
        let wide = n.head_radius;
        let floor_out = head + ((top - head.z) / across.z) * across;
        let floor_in = head - wide * across;
        let way_in = floor_in + ((top - floor_in.z) / axis.z) * axis;
        let trough = Profile::new(Loop::polygon(&[
            v2(floor_out.x, floor_out.z), v2(floor_in.x, floor_in.z), v2(way_in.x, way_in.z),
        ]));
        let trough = Plane::XZ.at(v3(0.0, y + wide, 0.0)).extrude(&trough, 2.0 * wide)?;
        cuts.push(bore.union(&trough)?);
    }
    Ok(cuts)
}

fn build(n: &Frame) -> Result<Solid> {
    let seat = n.seat;
    let floor = n.roof_floor + SEATING_RELIEF;
    let top = n.roof_top;
    let back = n.back;
    let mut body = Plane::XY.extrude(&blank_plan(n, n.body_width)?, seat)?;
    let roof = Plane::XY.at(v3(0.0, 0.0, floor))
        .extrude(&blank_plan(n, n.roof_width)?, top - floor)?;

    let mut cuts = vec![];
    let foot = n.corbel_half_depth;
    let slope = n.corbel_slope;
    for sign in [-1.0, 1.0] {
        let (low, high) = (-2.0, 80.0);
        let points = [v2(sign * (foot + slope * low), low), v2(sign * 400.0, low),
                      v2(sign * 400.0, high), v2(sign * (foot + slope * high), high)];
        let plan = Profile::new(Loop::polygon(&points));
        cuts.push(Plane::YZ.at(v3(-150.0, 0.0, 0.0)).extrude(&plan, 300.0)?);
    }
    let seats = back_seats(n, &cuts[1])?;

    let slip = n.slide_slip;
    let pad = n.ledge_pad_half_y;
    let mut screws = vec![];
    for &(x, y, head, host, side, front, _) in &n.screws {
        let inside = x - side * (host + slip);
        let outside = side * 150.0;
        cuts.push(block(inside.min(outside), inside.max(outside), y - pad - slip,
                        if front { y + pad + slip } else { back + 1.0 }, -1.0, floor));
        if !front {
            continue;
        }
        let r = n.head_radius;
        let inner = side * (x.abs() - r).min(n.front_head_inside);
        let head_box = block(inner.min(outside), inner.max(outside), y - r, y + r, head, top + 1.0);
        let head_cut = cylinder(x, y, r, head, top + 1.0)?.union(&head_box)?;
        screws.push(cylinder(x, y, n.screw_clear_radius, -1.0, head + 0.01)?.union(&head_cut)?);
    }
    body = body.cut_all(&cuts)?.union(&roof)?;

    let (forming, _cavity) = funnel_geometry::build_solids(&n.funnel, n.forming_air, false, false)?;
    let forming = forming.translate(v3(0.0, 0.0, seat));
    let (clip0, clip1) = n.forming_clip_z;
    let forming = forming.intersect(&block(-200.0, 200.0, -200.0, 200.0, clip0, clip1))?;
    let (dx, dy) = n.drain_xy;
    let (z0, z1) = n.web_cut_z;
    let mut tools = vec![socket(n)?, forming, brim(n)?, cylinder(dx, dy, n.hole_radius, z0, z1)?];
    let (sx0, sx1) = n.slot_x;
    let (sy0, sy1) = n.slot_y;
    for side in [-1.0, 1.0] {
        tools.push(block(dx + (side * sx0).min(side * sx1), dx + (side * sx0).max(side * sx1),
                         dy + sy0, dy + sy1, z0, z1));
    }
    tools.extend(screws);
    body = body.cut_all(&tools)?;
    let half = n.body_half_width;
    let rear = block(-150.0, 150.0, n.rear_start, n.rear_start + 200.0, seat, top + 1.0);
    let body = body.cut_all(&[
        block(half, 150.0, -200.0, 200.0, -1.0, floor),
        block(-150.0, -half, -200.0, 200.0, -1.0, floor), rear,
    ])?;
    seats.iter().try_fold(body, |body, wedge| body.union(wedge))?.cut_all(&back_screw_cuts(n)?)
}

fn main() -> Result<()> {
    let out = zone_files::out_dir("hardware/printed-parts/zone-c/funnel")?;
    let n = frame();
    let solid = build(&n)?.simplified()?;
    let name = "funnel-frame";
    let color = Some(n.color);
    let size = solid.bounds().size();
    let display_tolerance = (size.x+size.y+size.z)/3.0*catalog::VIEWER_DEFLECTION_RATIO;
    let display = solid.simplified_to(display_tolerance)?;
    let shown = [Body { name,color,solid:&display }];
    let step = hsm_kernel::step::step_bytes(&shown,name)?;
    let digest = format!("{:x}",Sha256::digest(&step));
    let payload = hsm_kernel::write::payload_bytes_with_sources(&shown,Some(&digest),None);
    let payload_name = format!("{name}.step.mesh");
    let document = json!({"presentation":{
        "path":payload_name,"sha256":format!("{:x}",Sha256::digest(&payload)),
        "tolerance_mm":display_tolerance,
    }});
    let printed = funnel_geometry::fabrication_copy(&solid,"FUNNEL frame fabrication copy")?;
    let printed = PrintOutput::new(&[Body { name,color,solid:&printed }]);
    let stl_name = format!("{name}.stl");
    let fine = [Body { name,color,solid:&solid }];
    let model = printed.model_bytes(&fine,&stl_name,Some(&document))?;
    for (file,bytes) in [(format!("{name}.step"),step.as_slice()),
                         (format!("{name}.step.npz"),model.as_slice()),
                         (payload_name,payload.as_slice()),
                         (stl_name,printed.stl_bytes())] {
        zone_files::keep(&out.join(file),bytes)?;
    }
    // Each back screw's line as the frame draws it, and its insert's mouth on back-top's seat.
    let lift = n.back_seat_air * (1.0 + n.back_seat_slope.powi(2)).sqrt();
    let back_screws: Vec<_> = n.screws.iter().filter(|s| !s.5).map(|&(x, y, _, _, side, _, row)| {
        let (face, head, axis) = back_line(&n, x, y, side);
        json!({"row": row, "side": side, "head_seat": head.to_array(), "axis": axis.to_array(),
               "insert_mouth": (face - v3(0.0, 0.0, lift)).to_array()})
    }).collect();
    zone_files::json(&out.join("funnel-frame.numbers.json"), &json!({
        "seat": n.seat,
        "roof_floor": n.roof_floor,
        "screws": n.screws,
        "back_screws": back_screws,
    }))?;
    let bounds = solid.bounds();
    println!("{}",json!({"files":[format!("{name}.step"),format!("{name}.step.npz"),
        format!("{name}.step.mesh"),format!("{name}.stl")],
        "bodies":[{"name":name,"volume":solid.volume(),"area":solid.area(),
            "min":bounds.min.to_array(),"max":bounds.max.to_array(),
            "triangles":solid.tris().len(),"presentation_triangles":display.tris().len(),
            "presentation_tolerance_mm":display_tolerance}]}));
    Ok(())
}
