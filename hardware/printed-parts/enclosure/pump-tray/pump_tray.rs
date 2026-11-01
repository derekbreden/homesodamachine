//! Measurements of the case-derived collar source; the enclosure retains its native builders.
use anyhow::{Context, Result, ensure};
use hsm_kernel::part::Numbers;
use hsm_kernel::{Body, Loop, Plane, Profile, Seg, Solid, V3, v2, v3, write_model};
use serde_json::{Value, json};

fn array(v: &Value) -> Result<&Vec<Value>> {
    v.as_array().context("a numeric list")
}

fn number(v: &Value) -> Result<f64> {
    v.as_f64().context("a stock coordinate")
}

fn point(v: &Value) -> Result<V3> {
    let p = array(v)?;
    ensure!(p.len() == 3, "a point has three coordinates");
    Ok(v3(number(&p[0])?, number(&p[1])?, number(&p[2])?))
}

fn profile(v: &Value) -> Result<Profile> {
    let points = array(v)?
        .iter()
        .map(|p| {
            let p = array(p)?;
            ensure!(p.len() == 2, "a profile point is planar");
            Ok(v2(number(&p[0])?, number(&p[1])?))
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(Profile::polygon(&points))
}

fn cylinder(y: f64, z0: f64, z1: f64, r: f64) -> Result<Solid> {
    // The native volume falls close to the doc's 0.01 cm³ rounding boundary. Quarter each
    // standard chord to retain that reading without changing the circle or its stations.
    let count = 4 * hsm_kernel::rule::ring_count(r);
    let point = |i: usize| {
        let angle = std::f64::consts::TAU * i as f64 / count as f64;
        v2(r * angle.cos(), r * angle.sin())
    };
    let segments = (0..count)
        .map(|i| Seg::Arc {
            a: point(i),
            b: point(i + 1),
            c: v2(0.0, 0.0),
            ccw: true,
        })
        .collect();
    Plane::XY
        .at(v3(0.0, y, z0))
        .extrude(&Profile::new(Loop::new(segments)?), z1 - z0)
}

fn collar_stock(n: &Numbers) -> Result<Solid> {
    let sections = array(n.get("ramp_sections")?)?
        .iter()
        .map(|section| {
            let section = array(section)?;
            ensure!(
                section.len() == 2,
                "a ramp section has a station and outline"
            );
            Ok(profile(&section[1])?.place(&Plane::XY.offset(number(&section[0])?)))
        })
        .collect::<Result<Vec<_>>>()?;
    let ramp = Solid::loft(&sections)?;
    let wall = Plane::XY.extrude(&profile(n.get("bore_wall")?)?, n.f("bore_depth")?)?;
    let tower = cylinder(
        0.0,
        n.f("tower_start")?,
        n.f("tower_end")?,
        n.f("tower_outer_radius")?,
    )?
    .cut(&cylinder(
        0.0,
        n.f("tower_bore_start")?,
        n.f("tower_bore_end")?,
        n.f("tower_inner_radius")?,
    )?)?;
    Solid::union_all(&[ramp, wall, tower])
}

fn tray(n: &Numbers, stock: &Solid, root: f64) -> Result<Solid> {
    let (hw, fr, d) = (n.f("half_width")?, n.f("far_reach")?, n.f("depth")?);
    let big = hw.max(fr).max(root) + n.f("case_half")? + 10.0;
    let slab = |x0, x1, y0, y1, z0, z1| Solid::cuboid(v3(x0, y0, z0), v3(x1, y1, z1));
    let stock = stock
        .translate(v3(0.0, n.f("rear_axis_y_shift")?, 0.0))
        .cut(&slab(-big, big, -big, big, d, d + big))?
        .union(&slab(-hw, hw, -root, fr, 0.0, n.f("plate")?))?;
    let bore = Plane::XY
        .offset(-1.0)
        .extrude(&profile(n.get("bore")?)?, n.f("boss_depth")? + 1.0)?
        .translate(v3(0.0, n.f("rear_axis_y_shift")?, 0.0));
    stock
        .cut(&bore)?
        .cut(&slab(-big, big, -root - big, -root, -1.0, d + 1.0))
}

fn main() -> Result<()> {
    let args = std::env::args().collect::<Vec<_>>();
    ensure!(
        args.len() == 3,
        "usage: {} <numbers.json> <--check|model.npz>",
        args[0]
    );
    let n = Numbers::read(&args[1])?;
    let stock = collar_stock(&n)?;
    let y = n.f("rear_axis_y_shift")?;
    let boss = Plane::XY
        .extrude(&profile(n.get("bore")?)?, n.f("boss_depth")?)?
        .translate(v3(0.0, y, 0.0));
    let motor = cylinder(
        y,
        n.f("boss_depth")?,
        n.f("motor_end")?,
        n.f("motor_radius")?,
    )?;
    // The fitted head is clipped from this box and ends on z = 0. The collar starts there,
    // so its intersection with the enclosing box is the exact zero-volume head reading.
    let head = array(n.get("head_box")?)?;
    let head = Solid::cuboid(point(&head[0])?, point(&head[1])?);
    let mut shapes = vec![];
    let mut rows = vec![];
    let mut measured = std::collections::HashMap::<u64, (Solid, Value)>::new();
    for target in array(n.get("trays")?)? {
        let name = target[0].as_str().context("a collar name")?;
        let root = number(&target[1])?;
        if let Some((shape, row)) = measured.get(&root.to_bits()) {
            let mut row = row.clone();
            row["name"] = json!(name);
            rows.push(row);
            shapes.push(shape.clone());
            continue;
        }
        let shape = tray(&n, &stock, root)?;
        let valid = shape.check().is_ok();
        let fouled = [&head, &boss, &motor]
            .into_iter()
            .map(|body| Ok(shape.intersect(body)?.volume()))
            .collect::<Result<Vec<_>>>()?
            .iter()
            .sum::<f64>();
        let span = n.f("section_span")? / 2.0;
        let thickness = n.f("section_thickness")?;
        let storeys = n
            .list("section_stations")?
            .iter()
            .map(|z| {
                let z = z + n.f("section_rise")?;
                let slab = Solid::cuboid(
                    v3(-span, -span, z - thickness / 2.0),
                    v3(span, span, z + thickness / 2.0),
                );
                Ok(shape.intersect(&slab)?.volume() / thickness)
            })
            .collect::<Result<Vec<_>>>()?;
        let row = json!({"name":name, "volume":shape.volume(), "valid":valid,
                         "fouled_volume":fouled, "storeys":storeys});
        measured.insert(root.to_bits(), (shape.clone(), row.clone()));
        rows.push(row);
        shapes.push(shape);
    }
    if args[2] != "--check" {
        let bodies = rows
            .iter()
            .zip(&shapes)
            .map(|(row, solid)| Body {
                name: row["name"].as_str().unwrap(),
                color: None,
                solid,
            })
            .collect::<Vec<_>>();
        write_model(&args[2], &bodies)?;
    }
    println!("{}", json!({"trays":rows}));
    Ok(())
}
