//! Four rear equipment caps, cut from the live snap sections and measured reference profiles.
use anyhow::{Result, anyhow, bail, ensure};
use hsm_kernel::part::{args, write_part, write_shown};
use hsm_kernel::{Affine, Body, Loop, Path, Plane, Profile, Seg, Solid, V2, V3, v2, v3};
use serde_json::Value;

fn array(v: &Value) -> Result<&Vec<Value>> {
    v.as_array()
        .ok_or_else(|| anyhow!("a cap figure is a list"))
}

fn f(v: &Value) -> Result<f64> {
    v.as_f64()
        .ok_or_else(|| anyhow!("a cap coordinate is numeric"))
}

fn point2(v: &Value) -> Result<V2> {
    let a = array(v)?;
    ensure!(a.len() == 2, "a cap section point has two coordinates");
    Ok(v2(f(&a[0])?, f(&a[1])?))
}

fn point3(v: &Value) -> Result<V3> {
    let a = array(v)?;
    ensure!(a.len() == 3, "a cap placement has three coordinates");
    Ok(v3(f(&a[0])?, f(&a[1])?, f(&a[2])?))
}

fn span(v: &Value) -> Result<(f64, f64)> {
    let a = array(v)?;
    ensure!(a.len() == 2, "a cap span has two ends");
    Ok((f(&a[0])?, f(&a[1])?))
}

fn profile(outer: Loop) -> Profile {
    Profile {
        outer,
        holes: vec![],
    }
}

fn section(v: &Value) -> Result<Solid> {
    let mut segments = vec![];
    for s in array(&v["segments"])? {
        if let Some(line) = s.get("line") {
            let a = array(line)?;
            ensure!(a.len() == 2, "a cap line has two points");
            segments.push(Seg::Line {
                a: point2(&a[0])?,
                b: point2(&a[1])?,
            });
        } else {
            let a = array(&s["arc"])?;
            ensure!(
                a.len() == 4,
                "a cap arc has endpoints, a midpoint and its centre"
            );
            segments.push(Seg::Arc {
                a: point2(&a[0])?,
                b: point2(&a[2])?,
                c: point2(&a[3])?,
                ccw: s.get("ccw").and_then(Value::as_bool).unwrap_or(false),
            });
        }
    }
    let (lo, hi) = span(&v["span"])?;
    Plane::XZ
        .at(v3(0.0, lo, 0.0))
        .extrude(&profile(Loop::new(segments)?), -(hi - lo))
}

fn cylinder_y(v: &Value) -> Result<Solid> {
    let centre = point2(&v["centre"])?;
    let (lo, hi) = span(&v["span"])?;
    let r = f(&v["radius"])?;
    let mut segments = vec![];
    circle_arc(&mut segments, centre, r, 0.0, std::f64::consts::TAU);
    Plane::XZ
        .at(v3(0.0, lo, 0.0))
        .extrude(&profile(Loop::new(segments)?), -(hi - lo))
}

fn circle_arc(segments: &mut Vec<Seg>, c: V2, r: f64, start: f64, turn: f64) {
    // The intersecting meter bores share the distance budget at their seam.
    // Keep the same circles with a midpoint on each of the rule's chords.
    let steps = (hsm_kernel::rule::ring_count(r) as f64 * turn.abs() / std::f64::consts::PI).round()
        as usize;
    let point = |i: usize| {
        let angle = start + turn * i as f64 / steps as f64;
        c + v2(angle.cos(), angle.sin()) * r
    };
    for i in 0..steps {
        segments.push(Seg::Arc {
            a: point(i),
            b: point(i + 1),
            c,
            ccw: turn > 0.0,
        });
    }
}

fn turned(v: &Value) -> Result<Solid> {
    let rows = array(&v["profile"])?;
    ensure!(!rows.is_empty(), "a cap clearance profile has axial runs");
    let mut points = vec![v2(f(&array(&rows[0])?[0])?, 0.0)];
    for row in rows {
        let a = array(row)?;
        ensure!(a.len() == 3, "a cap run has two ends and one radius");
        points.push(v2(f(&a[0])?, f(&a[2])?));
        points.push(v2(f(&a[1])?, f(&a[2])?));
    }
    points.push(v2(f(&array(rows.last().unwrap())?[1])?, 0.0));
    points.dedup_by(|a, b| (a.x - b.x).abs() <= 1e-9 && (a.y - b.y).abs() <= 1e-9);
    let axis = point2(&v["axis"])?;
    Ok(Plane::XY
        .revolve(
            &profile(Loop::polygon(&points)),
            360.0,
            V2::ZERO,
            v2(1.0, 0.0),
        )?
        .rotate(V3::ZERO, V3::Z, 90.0)
        .translate(v3(axis.x, 0.0, axis.y)))
}

fn radial_profile(v: &Value) -> Result<Solid> {
    let rows=array(&v["points"])?;
    let mut points=vec![v2(f(&rows[0][0])?,0.)];
    for row in rows {points.push(point2(row)?);}
    points.push(v2(f(&rows.last().unwrap()[0])?,0.));
    let shape=Plane::XY.revolve(&Profile::polygon(&points),360.,V2::ZERO,v2(1.,0.))?;
    let pose=&v["frame"];
    let r=&pose["rotation"];
    let col=|i:usize|->Result<V3>{Ok(v3(f(&r[0][i])?,f(&r[1][i])?,f(&r[2][i])?))};
    Ok(shape.transformed(&Affine::from_columns(col(0)?,col(1)?,col(2)?,point3(&pose["translation_mm"])?)))
}

fn hex(v: &Value) -> Result<Solid> {
    let points = array(&v["points"])?
        .iter()
        .map(point2)
        .collect::<Result<Vec<_>>>()?;
    let (lo, hi) = span(&v["span"])?;
    let axis = point2(&v["axis"])?;
    let prism = Plane::XZ
        .at(v3(0.0, lo, 0.0))
        .extrude(&profile(Loop::polygon(&points)), -(hi - lo))?;
    prism.intersect(&Solid::cylinder(
        v3(axis.x, lo, axis.y),
        V3::Y,
        f(&v["corner"])?,
        hi - lo,
    )?)
}

fn stadium(v: &Value) -> Result<Solid> {
    let c = point2(&v["centre"])?;
    let r = f(&v["radius"])?;
    let (a, b) = (c.x - f(&v["fore"])?, c.x + f(&v["aft"])?);
    let (lo, hi) = span(&v["span"])?;
    let lower_a = v2(a, c.y - r);
    let lower_b = v2(b, c.y - r);
    let upper_b = v2(b, c.y + r);
    let upper_a = v2(a, c.y + r);
    let mut segments = vec![Seg::Line {
        a: lower_a,
        b: lower_b,
    }];
    circle_arc(
        &mut segments,
        v2(b, c.y),
        r,
        -std::f64::consts::FRAC_PI_2,
        std::f64::consts::PI,
    );
    segments.push(Seg::Line {
        a: upper_b,
        b: upper_a,
    });
    circle_arc(
        &mut segments,
        v2(a, c.y),
        r,
        std::f64::consts::FRAC_PI_2,
        std::f64::consts::PI,
    );
    let outer = Loop::new(segments)?;
    Plane::YZ
        .at(v3(lo, 0.0, 0.0))
        .extrude(&profile(outer), hi - lo)
}

fn sweep(v: &Value) -> Result<Solid> {
    let segments = array(&v["segments"])?;
    ensure!(!segments.is_empty(), "the meter corridor has a path");
    let start = point3(&array(&segments[0]["points_mm"])?[0])?;
    let mut path = Path::new(start);
    for segment in segments {
        let points = array(&segment["points_mm"])?;
        path = match segment["kind"].as_str() {
            Some("line") => path.line_to(point3(&points[1])?),
            Some("arc") => path.arc_through(point3(&points[1])?, point3(&points[2])?)?,
            _ => bail!("the meter corridor uses lines and circular bends"),
        };
    }
    Plane::new(start, V3::X, V3::Y)?
        .sweep(&profile(Loop::circle(V2::ZERO, f(&v["radius"])?)), &path)
}

fn cut(v: &Value) -> Result<Solid> {
    match v["op"].as_str() {
        Some("box") => {
            let a = array(&v["bounds"])?;
            ensure!(a.len() == 6, "a cap box has six bounds");
            Ok(Solid::cuboid(
                v3(f(&a[0])?, f(&a[2])?, f(&a[4])?),
                v3(f(&a[1])?, f(&a[3])?, f(&a[5])?),
            ))
        }
        Some("turned") => turned(v),
        Some("radial-profile") => radial_profile(v),
        Some("hex") => hex(v),
        Some("section") => section(v),
        Some("stadium-x") => stadium(v),
        Some("cylinder-y") => cylinder_y(v),
        Some("sweep") => sweep(v),
        _ => bail!("a cap clearance names its primitive"),
    }
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let mut installed = vec![];
    for cap in array(n.get("caps")?)? {
        let mut body = section(&cap["section"])?;
        if let Some(stock)=cap.get("stock") {
            for addition in array(stock)? {body=body.union(&cut(addition)?)?;}
        }
        if let Some(pry)=cap.get("pry") {
            for slot in array(pry)? {body=body.cut(&cut(slot)?)?;}
        }
        if let Some(p) = cap.get("placement") {
            body = body
                .rotate(V3::ZERO, V3::Y, f(&p["rotate_y"])?)
                .translate(point3(&p["translation"])?);
        }
        let cutters = array(&cap["cuts"])?
            .iter()
            .map(cut)
            .collect::<Result<Vec<_>>>()?;
        body = body.cut_all(&cutters)?;
        if let Some(angle) = cap.get("rotate_z") {
            body = body.rotate(V3::ZERO, V3::Z, f(angle)?);
        }
        let name = cap["name"]
            .as_str()
            .ok_or_else(|| anyhow!("a cap has a name"))?;
        installed.push((name, body.clone()));
        if let Some(angle) = cap.get("print_rotate_x") {
            body = body.rotate(V3::ZERO, V3::X, f(angle)?);
        }
        if let Some(angle) = cap.get("print_rotate_y") {
            body = body.rotate(V3::ZERO, V3::Y, f(angle)?);
        }
        let b = body.bounds();
        body = body.translate(v3(
            -(b.min.x + b.max.x) / 2.0,
            -(b.min.y + b.max.y) / 2.0,
            -b.min.z,
        ));
        println!(
            "{}",
            write_part(
                &out,
                name,
                &[Body {
                    name,
                    color: Some(n.color("color")?),
                    solid: &body
                },]
            )?
        );
    }
    let bodies = installed
        .iter()
        .map(|(name, body)| {
            Ok(Body {
                name,
                color: Some(n.color("color")?),
                solid: body,
            })
        })
        .collect::<Result<Vec<_>>>()?;
    println!(
        "{}",
        write_shown(&out, "rear-equipment-caps-installed", &bodies)?
    );
    Ok(())
}
