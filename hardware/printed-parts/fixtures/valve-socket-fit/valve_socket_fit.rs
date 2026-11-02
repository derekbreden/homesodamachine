//! One production-profile Beduan socket panel, in its standing print frame.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{Numbers, args, write_part};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V3, import, v2, v3};
use serde_json::{Value, json};

fn values(v: &Value) -> Result<Vec<f64>> {
    v.as_array()
        .context("coordinate list")?
        .iter()
        .map(|v| v.as_f64().context("coordinate"))
        .collect()
}

fn circle_cut(x: f64, z: f64, y0: f64, y1: f64, r: f64) -> Result<Solid> {
    // At V69 the post and socket have the same nominal radius. Circumscribe the
    // cutter's fine triangles so polygon phase and the frozen post's f32 rounding
    // do not invent interference. The analytic record retains the nominal circle.
    let count = 2 * hsm_kernel::rule::ring_count(r);
    let at = |i: usize| {
        let a = std::f64::consts::TAU * i as f64 / count as f64;
        v2(r * a.cos(), r * a.sin())
    };
    let edges = (0..count)
        .map(|i| Seg::Arc {
            a: at(i), b: at(i + 1), c: v2(0.0, 0.0), ccw: true,
        })
        .collect();
    let nominal = Plane::XZ.at(v3(x, y1, z))
        .extrude(&Profile::new(Loop::new(edges)?), y1 - y0)?;
    let roundoff = f32::EPSILON as f64 * (x.abs().max(z.abs()) + r);
    let scale = (r / (std::f64::consts::PI / count as f64).cos() + roundoff) / r;
    let vertices = nominal.verts().iter()
        .map(|p| v3(x + (p.x - x) * scale, p.y, z + (p.z - z) * scale))
        .collect::<Vec<_>>();
    Solid::from_mesh(&vertices, nominal.tris(), nominal.face_of(), nominal.faces())
}

fn socket(a: &[f64], angle: f64) -> Result<Solid> {
    let (x, z, y0, y1, r) = (a[0], a[1], a[2], a[3], a[4]);
    let half = r * angle.sin();
    let tangent = z + r * angle.cos();
    let apex = z + r / angle.cos();
    let roof = Plane::XZ.at(v3(0.0, y1, 0.0)).extrude(
        &Profile::polygon(&[v2(x - half, tangent), v2(x + half, tangent), v2(x, apex)]),
        y1 - y0,
    )?;
    circle_cut(x, z, y0, y1, r)?.union(&roof)
}

fn placed(body: Solid, station: f64) -> Solid {
    body.rotate(V3::ZERO, V3::X, -90.0).translate(v3(0.0, 0.0, station))
}

fn panel(n: &Numbers) -> Result<Solid> {
    let a = n.list("stock")?;
    let stock = Solid::cuboid(v3(a[0], a[2], a[4]), v3(a[1], a[3], a[5]));
    let station = n.f("station_z")?;
    let mut cuts = Vec::new();
    for row in n.get("body_cylinders")?.as_array().context("body cylinders")? {
        let a = values(row)?;
        cuts.push(placed(Solid::cylinder(v3(a[0], a[1], a[3]), V3::Z, a[2], a[4] - a[3])?, station));
    }
    let a = n.list("body_cap")?;
    let cap = Plane::XY.at(v3(0.0, 0.0, a[2])).extrude(
        &Profile::new(Loop::rounded_rect(v2(0.0, 0.0), a[0], a[1], a[4])?), a[3] - a[2],
    )?;
    cuts.push(placed(cap, station));
    for row in n.get("sockets")?.as_array().context("four sockets")? {
        cuts.push(socket(&values(row)?, n.f("roof_angle_deg")?.to_radians())?);
    }
    let a = n.list("port_channel")?;
    cuts.push(Solid::cylinder(v3(a[0], a[1], a[2]), V3::Z, a[3], a[4])?);
    stock.cut_all(&cuts)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let body = panel(&n)?;
    body.check()?;
    ensure!(body.components().len() == 1 && body.volume() > 0.0,
            "socket panel must be one closed positive-volume body");
    let station = n.f("station_z")?;
    let valve = import::step(n.text("valve_step")?)?.into_iter()
        .map(|b| placed(b.solid, station))
        .collect::<Vec<_>>();
    // Only the frozen f32 bearing plane's known coordinate-roundoff strip is
    // excluded from the contact witness. Neither the output nor its placement is
    // moved, and the native 1e-5 mm3 overlap threshold remains in force.
    let face = n.f("bearing_face_y")?;
    let bearing_roundoff = f32::EPSILON as f64 * face.abs() + 2.0_f64.powi(-30);
    let b = body.bounds();
    let witness = body.intersect(&Solid::cuboid(
        v3(b.min.x - 1.0, b.min.y - 1.0, b.min.z - 1.0),
        v3(b.max.x + 1.0, face - bearing_roundoff, b.max.z + 1.0),
    ))?;
    let mut samples = Vec::new();
    for offset in n.list("insertion_offsets")? {
        let mut raw = 0.0;
        let mut measured = 0.0;
        for part in &valve {
            let part = part.translate(v3(0.0, offset, 0.0));
            raw += body.shared_volume(&part)?;
            measured += witness.shared_volume(&part)?;
        }
        ensure!(measured <= n.f("overlap_limit")?,
                "valve interference at {offset} mm: {measured} mm3");
        samples.push(json!({"valve_outward_offset_mm":offset,
                            "interference_mm3":measured,"raw_interference_mm3":raw}));
    }
    let checks = json!({"valve_insertion_samples":samples,
                        "bearing_coordinate_roundoff_mm":bearing_roundoff,
                        "volume_mm3":body.volume(),
                        "bounds_mm":[[b.min.x,b.min.y,b.min.z],[b.max.x,b.max.y,b.max.z]]});
    if out.as_os_str() == "--check" {
        println!("{checks}");
        return Ok(());
    }
    let mut said = write_part(&out, "valve-socket-fit", &[Body {
        name: "valve-socket-fit", color: Some(n.color("black")?), solid: &body,
    }])?;
    said["checks"] = checks;
    println!("{said}");
    Ok(())
}
