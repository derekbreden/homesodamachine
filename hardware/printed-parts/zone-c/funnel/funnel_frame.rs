//! The removable frame, in its printed underside's coordinates. Its native funnel
//! forming offset is an explicit input until the funnel has an authored kernel port.
use anyhow::{Context, Result};
use hsm_kernel::part::{Numbers, args};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V2, V3, import, v2, v3};
use hsm_kernel::write::PrintOutput;
use serde_json::json;
use sha2::{Digest, Sha256};
use std::path::Path;

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
fn blank_plan(n: &Numbers, width: f64) -> Result<Profile> {
    let front = n.f("front")?;
    let back = n.f("back")?;
    let step = n.f("rear_start")?;
    let (limit_l, limit_r) = n.pair("rear_limits")?;
    let r = n.f("corner_radius")?;
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

fn brim(n: &Numbers) -> Result<Solid> {
    let (x, y) = n.pair("brim_half_size")?;
    let r = n.f("brim_radius")?;
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
    Plane::XY.at(v3(0.0, 0.0, n.f("seat")?))
        .extrude(&plan, n.f("roof_top")? + 1.0 - n.f("seat")?)
}

fn socket(n: &Numbers) -> Result<Solid> {
    let (w, d) = n.pair("socket_size")?;
    let (x, y) = n.pair("drain_xy")?;
    let r = n.f("socket_radius")?;
    let z0 = n.f("socket_z")?;
    let z1 = z0 + n.f("socket_height")?;
    let (h, grow) = n.pair("socket_flare")?;
    let section = |w, d, r, z| -> Result<_> {
        Ok(Profile::new(Loop::rounded_rect(v2(x, y), w, d, r)?)
            .place(&Plane::XY.at(v3(0.0, 0.0, z))))
    };
    let lead = Solid::loft(&[
        section(w, d, r, z1 - h)?,
        section(w + 2.0 * grow, d + 2.0 * grow, r + grow, z1)?,
    ])?;
    rounded(w, d, r, x, y, z0, z1)?.union(&lead)
}

fn build(n: &Numbers) -> Result<Solid> {
    let seat = n.f("seat")?;
    let floor = n.f("roof_floor")?;
    let top = n.f("roof_top")?;
    let back = n.f("back")?;
    let mut body = Plane::XY.extrude(&blank_plan(n, n.f("body_width")?)?, seat)?;
    let roof = Plane::XY.at(v3(0.0, 0.0, floor))
        .extrude(&blank_plan(n, n.f("roof_width")?)?, top - floor)?;

    let mut cuts = vec![];
    let foot = n.f("corbel_half_depth")?;
    let slope = n.f("corbel_slope")?;
    for sign in [-1.0, 1.0] {
        let (low, high) = (-2.0, 80.0);
        let points = [v2(sign * (foot + slope * low), low), v2(sign * 400.0, low),
                      v2(sign * 400.0, high), v2(sign * (foot + slope * high), high)];
        let plan = Profile::new(Loop::polygon(&points));
        cuts.push(Plane::YZ.at(v3(-150.0, 0.0, 0.0)).extrude(&plan, 300.0)?);
    }

    let rows = n.get("screws")?.as_array().context("screws are frame fastener rows")?;
    let slip = n.f("slide_slip")?;
    let pad = n.f("ledge_pad_half_y")?;
    let mut screws = vec![];
    let mut rear_pads = vec![];
    for row in rows {
        let f = |i| row.get(i).and_then(|v| v.as_f64()).context("a screw datum is a number");
        let (x, y, head, host, side) = (f(0)?, f(1)?, f(2)?, f(3)?, f(4)?);
        let front = row.get(5).and_then(|v| v.as_bool()).context("a screw row names its front/back")?;
        let inside = x - side * (host + slip);
        let outside = side * 150.0;
        cuts.push(block(inside.min(outside), inside.max(outside), y - pad - slip,
                        if front { y + pad + slip } else { back + 1.0 }, -1.0, floor));
        let r = n.f("head_radius")?;
        let mut edge = x.abs() - r;
        if front { edge = edge.min(n.f("front_head_inside")?); }
        let inner = side * edge;
        let head_box = block(inner.min(outside), inner.max(outside), y - r, y + r, head, top + 1.0);
        let head_cut = cylinder(x, y, r, head, top + 1.0)?.union(&head_box)?;
        screws.push(cylinder(x, y, n.f("screw_clear_radius")?, -1.0, head + 0.01)?.union(&head_cut)?);
        if !front {
            rear_pads.push(cylinder(x, y, n.f("rear_pad_radius")?, seat - 0.5, top + 1.5)?);
        }
    }
    body = body.cut_all(&cuts)?.union(&roof)?;

    let imported = import::payload(n.text("forming_payload")?)?;
    let forming = imported.first().context("the native forming provider has a solid")?
        .solid.translate(v3(0.0, 0.0, seat));
    let (clip0, clip1) = n.pair("forming_clip_z")?;
    let forming = forming.intersect(&block(-200.0, 200.0, -200.0, 200.0, clip0, clip1))?;
    let (dx, dy) = n.pair("drain_xy")?;
    let (z0, z1) = n.pair("web_cut_z")?;
    let mut tools = vec![socket(n)?, forming, brim(n)?, cylinder(dx, dy, n.f("hole_radius")?, z0, z1)?];
    let (sx0, sx1) = n.pair("slot_x")?;
    let (sy0, sy1) = n.pair("slot_y")?;
    for side in [-1.0, 1.0] {
        tools.push(block(dx + (side * sx0).min(side * sx1), dx + (side * sx0).max(side * sx1),
                         dy + sy0, dy + sy1, z0, z1));
    }
    tools.extend(screws);
    body = body.cut_all(&tools)?;
    let half = n.f("body_half_width")?;
    let rear = block(-150.0, 150.0, n.f("rear_start")?, n.f("rear_start")? + 200.0, seat, top + 1.0)
        .cut_all(&rear_pads)?;
    body.cut_all(&[
        block(half, 150.0, -200.0, 200.0, -1.0, floor),
        block(-150.0, -half, -200.0, 200.0, -1.0, floor), rear,
    ])
}

fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).ok().as_deref() == Some(bytes) { return Ok(()); }
    let name = path.file_name().context("output has a file name")?.to_string_lossy();
    let temporary = path.with_file_name(format!(".{name}.{}.{name}",std::process::id()));
    std::fs::write(&temporary,bytes)?;
    std::fs::rename(&temporary,path)?;
    Ok(())
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let solid = build(&n)?.simplified()?;
    let name = "funnel-frame";
    let color = Some(n.color("color")?);
    let size = solid.bounds().size();
    let display_tolerance = (size.x+size.y+size.z)/3.0*n.f("viewer_deflection_ratio")?;
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
    let printed = solid.simplified()?;
    let printed = PrintOutput::new(&[Body { name,color,solid:&printed }]);
    let stl_name = format!("{name}.stl");
    let fine = [Body { name,color,solid:&solid }];
    let model = printed.model_bytes(&fine,&stl_name,Some(&document))?;
    for (file,bytes) in [(format!("{name}.step"),step.as_slice()),
                         (format!("{name}.step.npz"),model.as_slice()),
                         (payload_name,payload.as_slice()),
                         (stl_name,printed.stl_bytes())] {
        keep(&out.join(file),bytes)?;
    }
    let bounds = solid.bounds();
    println!("{}",json!({"files":[format!("{name}.step"),format!("{name}.step.npz"),
        format!("{name}.step.mesh"),format!("{name}.stl")],
        "bodies":[{"name":name,"volume":solid.volume(),"area":solid.area(),
            "min":bounds.min.to_array(),"max":bounds.max.to_array(),
            "triangles":solid.tris().len(),"presentation_triangles":display.tris().len(),
            "presentation_tolerance_mm":display_tolerance}]}));
    Ok(())
}
