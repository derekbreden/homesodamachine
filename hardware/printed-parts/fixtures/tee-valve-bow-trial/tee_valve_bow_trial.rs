//! The bowed-stub bench frame, witness gauge and seated purchased references.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::{AssemblyBody, Numbers, args, write_assembly_with_root, write_part};
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V3, import, v2, v3};
use serde_json::{Value, json};

fn values(v: &Value) -> Result<Vec<f64>> {
    v.as_array()
        .context("a coordinate list")?
        .iter()
        .map(|v| v.as_f64().context("a coordinate"))
        .collect()
}

fn point(v: &Value) -> Result<V3> {
    let a = values(v)?;
    ensure!(a.len() == 3, "a point has three coordinates");
    Ok(v3(a[0], a[1], a[2]))
}

fn box_at(a: &[f64]) -> Solid {
    Solid::cuboid(v3(a[0], a[2], a[4]), v3(a[1], a[3], a[5]))
}

fn socket(a: &[f64]) -> Result<Solid> {
    // The purchased post and socket share the authored circle. Circumscribe its
    // cutter mesh, including the frozen payload's f32 coordinate roundoff, so
    // polygon phase does not invent interference at that tangent contact.
    let r = a[3];
    let count = 2 * hsm_kernel::rule::ring_count(r);
    let at = |i: usize| {
        let angle = std::f64::consts::TAU * i as f64 / count as f64;
        v2(r * angle.cos(), r * angle.sin())
    };
    let edges = (0..count)
        .map(|i| Seg::Arc {
            a: at(i),
            b: at(i + 1),
            c: v2(0.0, 0.0),
            ccw: true,
        })
        .collect();
    let nominal = Plane::XY
        .at(v3(a[0], a[1], a[2]))
        .extrude(&Profile::new(Loop::new(edges)?), a[4])?;
    let roundoff = f32::EPSILON as f64 * (a[0].abs().max(a[1].abs()) + r);
    let scale = (r / (std::f64::consts::PI / count as f64).cos() + roundoff) / r;
    let vertices = nominal
        .verts()
        .iter()
        .map(|p| {
            v3(
                a[0] + (p.x - a[0]) * scale,
                a[1] + (p.y - a[1]) * scale,
                p.z,
            )
        })
        .collect::<Vec<_>>();
    // The retained analytic records state the nominal cylinder; these triangles
    // approximate it within 0.0003 mm, well inside the kernel's surface budget.
    Solid::from_mesh(
        &vertices,
        nominal.tris(),
        nominal.face_of(),
        nominal.faces(),
    )
}

fn tray(v: &Value) -> Result<Solid> {
    let stock = Solid::cuboid(point(&v["slab"][0])?, point(&v["slab"][1])?);
    let mut cuts = Vec::new();
    for row in v["sockets"].as_array().context("socket cuts")? {
        let a = values(row)?;
        cuts.push(socket(&a)?);
    }
    for row in v["channels"].as_array().context("port channels")? {
        let a = values(row)?;
        cuts.push(Solid::cylinder(
            v3(a[0], a[1] - a[4] / 2.0, a[2]),
            V3::Y,
            a[3],
            a[4],
        )?);
    }
    stock.cut_all(&cuts)
}

fn frame(n: &Numbers) -> Result<Solid> {
    let plate = tray(n.get("tray")?)?
        .rotate(V3::ZERO, V3::X, 90.0)
        .translate(point(n.get("valve_frame")?)?);
    let backing = box_at(&n.list("backing")?);
    let guide = box_at(&n.list("guide")?);
    let a = n.list("journal")?;
    let bore = Solid::cylinder(v3(0.0, a[1], a[3]), V3::Y, a[0], a[2])?;
    Solid::union_all(&[backing, plate, guide])?.cut(&bore)
}

fn gauge(n: &Numbers) -> Result<Solid> {
    let stock = n
        .get("gauge_stock")?
        .as_array()
        .context("gauge stock")?
        .iter()
        .map(|v| Ok(box_at(&values(v)?)))
        .collect::<Result<Vec<_>>>()?;
    Solid::union_all(&stock)?.cut(&box_at(&n.list("gauge_window")?))
}

fn check_tee(solid: &Solid, n: &Numbers) -> Result<()> {
    let expected = n.get("tee_checks")?;
    let tol = expected["tolerance"]
        .as_f64()
        .context("tee measurement tolerance")?;
    let b = solid.bounds();
    let readings = [b.size().z, b.max.z, b.max.y, b.size().x];
    for (actual, target) in readings.iter().zip(values(&expected["bounds"])?) {
        ensure!(
            (actual - target).abs() <= tol,
            "tee datum: {actual} differs from {target}"
        );
    }
    for band in expected["bands"].as_array().context("tee collar bands")? {
        let a = values(band)?;
        let (lo, hi) = if a[0] == 0.0 {
            (
                v3(b.min.x - 1.0, b.min.y - 1.0, a[1]),
                v3(b.max.x + 1.0, b.max.y + 1.0, a[2]),
            )
        } else {
            (
                v3(b.min.x - 1.0, a[1], b.min.z - 1.0),
                v3(b.max.x + 1.0, a[2], b.max.z + 1.0),
            )
        };
        let section = solid.intersect(&Solid::cuboid(lo, hi))?.bounds();
        let mut radius = section.max.x.max(-section.min.x);
        if a[0] != 0.0 {
            radius = radius.max(section.max.z).max(-section.min.z);
        }
        ensure!(
            (radius - a[3]).abs() <= tol,
            "tee collar radius {radius} differs from {}",
            a[3]
        );
    }
    let a = values(&expected["pressed_branch"])?;
    let cutter = Solid::cuboid(
        v3(b.min.x - 1.0, a[0], b.min.z - 1.0),
        v3(b.max.x + 1.0, b.max.y + 1.0, b.max.z + 1.0),
    );
    let sleeve = solid.intersect(&cutter)?.translate(v3(0.0, -a[1], 0.0));
    let pressed = solid.cut(&cutter)?.union(&sleeve)?;
    ensure!(
        (pressed.bounds().max.y - a[2]).abs() <= tol,
        "branch sleeve does not provide its measured release travel"
    );
    Ok(())
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let frame = frame(&n)?;
    let gauge = gauge(&n)?;
    for (name, body) in [("frame", &frame), ("gauge", &gauge)] {
        body.check()?;
        ensure!(
            body.components().len() == 1 && body.volume() > 0.0,
            "{name}: expected one closed positive-volume body"
        );
    }
    let tee_parts = import::step(n.text("tee_step")?)?;
    let tee = Solid::compose(
        &tee_parts
            .iter()
            .map(|b| b.solid.clone())
            .collect::<Vec<_>>(),
    );
    check_tee(&tee, &n)?;
    let tee = tee.translate(point(n.get("tee_translation")?)?);
    let seat_shift = point(n.get("valve_seat_shift")?)?;
    let valve_frame = point(n.get("valve_frame")?)?;
    let valves = import::step(n.text("valve_step")?)?
        .into_iter()
        .map(|body| {
            body.solid
                .translate(seat_shift)
                .rotate(V3::ZERO, V3::X, 90.0)
                .translate(valve_frame)
        })
        .collect::<Vec<_>>();
    // The frozen f32 bearing plane rounds 5.2 mm slightly inward. Exclude only
    // that known coordinate-roundoff strip from the contact witness; the output
    // geometry and its nominal placement stay intact, and the overlap limit stays.
    let bearing_roundoff = f32::EPSILON as f64 * seat_shift.z.abs() + 2.0_f64.powi(-30);
    let b = frame.bounds();
    let core = frame.intersect(&Solid::cuboid(
        v3(
            b.min.x - 1.0,
            valve_frame.y + bearing_roundoff,
            b.min.z - 1.0,
        ),
        v3(b.max.x + 1.0, b.max.y + 1.0, b.max.z + 1.0),
    ))?;
    let mut raw_valve_overlap = 0.0;
    let mut valve_overlap = 0.0;
    for body in &valves {
        raw_valve_overlap += frame.shared_volume(body)?;
        valve_overlap += core.shared_volume(body)?;
    }
    ensure!(
        valve_overlap <= 1e-5,
        "the seated valve overlaps its frame beyond bearing roundoff by {valve_overlap} mm3"
    );
    let mut tee_overlaps = Vec::new();
    for travel in n.list("travels")? {
        let volume = frame.shared_volume(&tee.translate(v3(0.0, travel, 0.0)))?;
        ensure!(
            volume <= 1e-5,
            "the tee overlaps its frame by {volume} mm3 at {travel} mm"
        );
        tee_overlaps.push(json!({"travel_mm":travel,"overlap_mm3":volume}));
    }
    let engagement = n.f("collar_engagement")?;
    ensure!(
        engagement > 0.0,
        "the tee branch collar leaves its guide before the ceiling"
    );
    let checks = json!({"valve_overlap_mm3":valve_overlap,"raw_valve_overlap_mm3":raw_valve_overlap,
                       "bearing_roundoff_mm":bearing_roundoff,"tee_stations":tee_overlaps,
                       "collar_engagement_mm":engagement,"frame_volume":frame.volume(),
                       "gauge_volume":gauge.volume()});
    if out.as_os_str() == "--check" {
        println!("{checks}");
        return Ok(());
    }
    let print = frame
        .rotate(V3::ZERO, V3::X, -90.0)
        .translate(point(n.get("print_shift")?)?);
    let black = Some(n.color("black")?);
    for (name, body) in [
        ("tee-valve-bow-trial-frame", &print),
        ("tee-valve-bow-trial-gauge", &gauge),
    ] {
        println!(
            "{}",
            write_part(
                &out,
                name,
                &[Body {
                    name,
                    color: black,
                    solid: body
                }]
            )?
        );
    }
    let mut assembly = vec![
        AssemblyBody {
            name: "trial-frame",
            color: black,
            fine: &frame,
            presentation: &frame,
        },
        AssemblyBody {
            name: "pp0208e-tee-reference",
            color: Some(n.color("tee_color")?),
            fine: &tee,
            presentation: &tee,
        },
    ];
    let valve_color = Some(n.color("valve_color")?);
    assembly.extend(valves.iter().map(|solid| AssemblyBody {
        name: "beduan-valve-reference",
        color: valve_color,
        fine: solid,
        presentation: solid,
    }));
    let mut said = write_assembly_with_root(
        &out,
        "tee-valve-bow-trial-assembly",
        "tee-valve-bow-trial",
        &assembly,
        None,
    )?;
    said["checks"] = checks;
    println!("{said}");
    Ok(())
}
