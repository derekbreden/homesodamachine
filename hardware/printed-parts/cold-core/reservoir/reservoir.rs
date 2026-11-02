//! The two PETG reservoirs, their caps, gasket and matched TPU liquid/air spools.
//! Native dimensions, selected profile rounds and boss cut planes come from Python.
use anyhow::{Context, Result};
use hsm_kernel::math::{cos, sin, TAU};
use hsm_kernel::part::{args, write_part, Numbers};
use hsm_kernel::*;
use serde_json::{json, Value};

fn f(value: &Value, key: &str) -> Result<f64> {
    value[key]
        .as_f64()
        .with_context(|| format!("no number {key}"))
}

fn point(value: &Value) -> Result<V2> {
    Ok(v2(
        value[0].as_f64().context("point x")?,
        value[1].as_f64().context("point y")?,
    ))
}

fn profile(n: &Numbers, inset: f64, round: Option<f64>) -> Result<Profile> {
    let (far, y, radius) = (
        n.f("outer_far_x")? - inset,
        n.f("outer_y")? - inset,
        n.f("outer_radius")? + inset,
    );
    let x = (radius * radius - y * y).sqrt();
    let outline = Pen::new(v2(x, y))
        .line_to(v2(far, y))
        .line_to(v2(far, -y))
        .line_to(v2(x, -y))
        .arc_through(v2(radius, 0.0), v2(x, y))?
        .close()?;
    let rounded = match round {
        Some(r) => outline.fillet(r)?,
        None => outline,
    };
    Ok(Profile::new(fine_loop(rounded)?))
}

fn fine_loop(outline: Loop) -> Result<Loop> {
    // Keep the same analytic arcs and bisect their angular intervals. The
    // large concave wall meets its corner rounds within the fabrication rule.
    let mut segments = vec![];
    for segment in outline.segs {
        if let Seg::Arc { a, b, c, ccw } = segment {
            let v = a - c;
            let mut turn = (b - c).angle() - v.angle();
            if ccw {
                while turn <= 0. {
                    turn += TAU;
                }
            } else {
                while turn >= 0. {
                    turn -= TAU;
                }
            }
            let count = 2
                * ((hsm_kernel::rule::ring_count(v.norm()) as f64 * turn.abs() / TAU - 1e-9).ceil()
                    as usize)
                    .max(1);
            let mut start = a;
            for i in 1..=count {
                let angle = turn * i as f64 / count as f64;
                let end = if i == count {
                    b
                } else {
                    c + v2(
                        v.x * cos(angle) - v.y * sin(angle),
                        v.x * sin(angle) + v.y * cos(angle),
                    )
                };
                segments.push(Seg::Arc {
                    a: start,
                    b: end,
                    c,
                    ccw,
                });
                start = end;
            }
        } else {
            segments.push(segment);
        }
    }
    Loop::new(segments)
}

fn envelope(n: &Numbers, bottom: f64, top: f64, inset: f64, round: Option<f64>) -> Result<Solid> {
    Plane::XY
        .at(v3(0.0, 0.0, bottom))
        .extrude(&profile(n, inset, round)?, top - bottom)
}

fn cylinder(p: V2, bottom: f64, top: f64, radius: f64) -> Result<Solid> {
    Plane::XY
        .at(v3(p.x, p.y, bottom))
        .cylinder(radius, top - bottom)
}

fn placed_side(shape: &Solid, side: f64) -> Solid {
    if side < 0.0 {
        shape.mirror(V3::ZERO, v3(1.0, 0.0, 0.0))
    } else {
        shape.clone()
    }
}

fn body(n: &Numbers) -> Result<Solid> {
    let (z0, z1) = n.pair("outer_z")?;
    let (floor, top) = n.pair("inner_z")?;
    let mut body = envelope(n, z0, z1, 0.0, Some(n.f("outer_round")?))?.cut(&envelope(
        n,
        floor,
        top,
        n.f("wall")?,
        Some(n.f("inner_round")?),
    )?)?;
    let bottom = z1 - n.f("boss_height")?;
    for row in n
        .get("insert_stations")?
        .as_array()
        .context("insert stations")?
    {
        let xy = point(&row["xy"])?;
        let cut = row["cut"].as_array();
        let low = if cut.is_some() {
            bottom - n.f("boss_extra_below")?
        } else {
            bottom
        };
        let mut boss = cylinder(xy, low, z1, n.f("body_boss_radius")?)?;
        if let Some(c) = cut {
            let value = |i: usize| c[i].as_f64().context("boss cut plane coordinate");
            let (x, y, dx, dy) = (value(0)?, value(1)?, value(2)?, value(3)?);
            let plane = Plane::new(v3(x, y, bottom), v3(-dy, dx, 0.0), v3(dx, dy, 1.0))?;
            boss = boss.cut(&plane.extrude(&Profile::rect(v2(0.0, 0.0), 500.0, 500.0), -500.0)?)?;
        }
        body = body.union(&boss)?.cut(&cylinder(
            xy,
            z1 - n.f("insert_depth")?,
            z1 + 0.1,
            n.f("insert_radius")?,
        )?)?;
    }
    let rod = point(n.get("rod_xy")?)?;
    body = body.union(&cylinder(
        rod,
        n.f("rod_floor")?,
        n.f("rod_floor")? + n.f("rod_anchor_height")?,
        n.f("rod_boss_radius")?,
    )?)?;
    body.cut(&cylinder(
        rod,
        n.f("rod_floor")? + n.f("rod_anchor_floor")?,
        n.f("rod_floor")? + n.f("rod_anchor_height")? + 0.1,
        n.f("rod_bore_radius")?,
    )?)
}

fn spool(n: &Numbers, spec: &Value, xy: V2, z0: f64) -> Result<Solid> {
    let (waist, flare) = (f(spec, "waist_d")? / 2.0, f(spec, "flare_d")? / 2.0);
    let (z1, depth) = (z0 + n.f("plate_thickness")?, flare - waist);
    cylinder(xy, z0, z1, waist)?
        .union(&Solid::cone(
            v3(xy.x, xy.y, z0),
            v3(0.0, 0.0, 1.0),
            flare,
            waist,
            depth,
        )?)?
        .union(&Solid::cone(
            v3(xy.x, xy.y, z1 - depth),
            v3(0.0, 0.0, 1.0),
            waist,
            flare,
            depth,
        )?)
}

fn seat(n: &Numbers, spec: &Value, xy: V2, z0: f64) -> Result<Solid> {
    let z1 = z0 + n.f("plate_thickness")?;
    spool(n, spec, xy, z0)?.union(&cylinder(xy, z1, z1 + 0.1, f(spec, "flare_d")? / 2.0)?)
}

fn grip(n: &Numbers, spec: &Value) -> Result<Solid> {
    let (radius, lead, height) = (
        f(spec, "bore_d")? / 2.0,
        f(spec, "lead_d")? / 2.0,
        f(spec, "lead_h")?,
    );
    let z1 = n.f("plate_thickness")?;
    let opening = cylinder(v2(0.0, 0.0), -0.1, z1 + 0.1, radius)?
        .union(&Solid::cone(
            V3::ZERO,
            v3(0.0, 0.0, 1.0),
            lead,
            radius,
            height,
        )?)?
        .union(&Solid::cone(
            v3(0.0, 0.0, z1 - height),
            v3(0.0, 0.0, 1.0),
            radius,
            lead,
            height,
        )?)?;
    spool(n, spec, v2(0.0, 0.0), 0.0)?.cut(&opening)
}

fn cap(n: &Numbers, row: &Value) -> Result<Solid> {
    let (height, wall_height) = (n.f("cap_height")?, n.f("cap_wall_height")?);
    let mut cap = envelope(n, 0.0, height, 0.0, Some(n.f("outer_round")?))?.cut(&envelope(
        n,
        0.0,
        wall_height,
        n.f("cap_wall_width")?,
        None,
    )?)?;
    let stations = n
        .get("insert_stations")?
        .as_array()
        .context("insert stations")?;
    let bosses = stations
        .iter()
        .map(|r| cylinder(point(&r["xy"])?, 0.0, wall_height, n.f("cap_boss_radius")?))
        .collect::<Result<Vec<_>>>()?;
    cap = cap.union(&Solid::compose(&bosses))?;
    let shafts = stations
        .iter()
        .map(|r| {
            cylinder(
                point(&r["xy"])?,
                -0.1,
                height + 0.1,
                n.f("clearance_radius")?,
            )
        })
        .collect::<Result<Vec<_>>>()?;
    cap = cap.cut(&Solid::compose(&shafts))?;
    let heads = stations
        .iter()
        .map(|r| {
            cylinder(
                point(&r["xy"])?,
                height - n.f("counterbore_depth")?,
                height + 0.1,
                n.f("counterbore_radius")?,
            )
        })
        .collect::<Result<Vec<_>>>()?;
    cap = cap.cut(&Solid::compose(&heads))?;
    let side = f(row, "side")?;
    cap = placed_side(&cap, side);
    cap = cap.cut(&seat(
        n,
        n.get("air_grip")?,
        point(&row["vent"])?,
        wall_height,
    )?)?;
    let rod = point(n.get("rod_xy")?)?;
    let rod = v2(rod.x * side, rod.y);
    cap = cap
        .union(&cylinder(
            rod,
            -n.f("rod_register_height")?,
            wall_height,
            n.f("rod_boss_radius")?,
        )?)?
        .cut(&cylinder(
            rod,
            -n.f("rod_register_height")? - 0.1,
            wall_height,
            n.f("rod_bore_radius")?,
        )?)?;
    if !row["fill"].is_null() {
        cap = cap.cut(&seat(
            n,
            n.get("liquid_grip")?,
            point(&row["fill"])?,
            wall_height,
        )?)?;
    }
    cap.cut(&seat(
        n,
        n.get("liquid_grip")?,
        point(&row["draw"])?,
        wall_height,
    )?)
}

fn gasket(n: &Numbers) -> Result<Solid> {
    let height = n.f("gasket_thickness")?;
    let mut gasket = envelope(n, 0.0, height, 0.0, Some(n.f("outer_round")?))?.cut(&envelope(
        n,
        0.0,
        height,
        n.f("gasket_strip_width")?,
        None,
    )?)?;
    let stations = n
        .get("insert_stations")?
        .as_array()
        .context("insert stations")?;
    let pads = stations
        .iter()
        .map(|r| cylinder(point(&r["xy"])?, 0.0, height, n.f("gasket_pad_radius")?))
        .collect::<Result<Vec<_>>>()?;
    gasket = gasket.union(&Solid::compose(&pads))?;
    let holes = stations
        .iter()
        .map(|r| {
            cylinder(
                point(&r["xy"])?,
                -0.1,
                height + 0.1,
                n.f("clearance_radius")?,
            )
        })
        .collect::<Result<Vec<_>>>()?;
    gasket.cut(&Solid::compose(&holes))
}

fn held(n: &Numbers, body: &Solid, z: (f64, f64)) -> Result<f64> {
    let envelope = envelope(n, z.0, z.1, n.f("wall")?, None)?;
    Ok((envelope.volume() - envelope.intersect(body)?.volume()) / 1e6)
}

fn main() -> Result<()> {
    if std::env::args().nth(2).as_deref() == Some("--check") {
        let n = Numbers::read(std::env::args().nth(1).unwrap_or_default())?;
        let body = body(&n)?;
        println!(
            "{}",
            json!({"capacity_l": held(&n, &body, n.pair("inner_z")?)?,
                              "reed_window_l": held(&n, &body, n.pair("reed_window")?)?})
        );
        return Ok(());
    }
    let (n, out) = args()?;
    let body = body(&n)?;
    let capacity_l = held(&n, &body, n.pair("inner_z")?)?;
    let reed_window_l = held(&n, &body, n.pair("reed_window")?)?;
    for row in n.get("ports")?.as_array().context("reservoir port rows")? {
        let side = f(row, "side")?;
        let label = if side > 0.0 { "right" } else { "left" };
        let part = placed_side(&body, side);
        let cap = cap(&n, row)?;
        for (name, material, solid) in [
            (format!("reservoir-{label}"), "body", &part),
            (format!("reservoir-cap-{label}"), "cap", &cap),
        ] {
            let mut result = write_part(
                &out,
                &name,
                &[Body {
                    name: &name,
                    color: Some(n.color(&format!("color_{material}"))?),
                    solid,
                }],
            )?;
            if name == "reservoir-right" {
                result["bodies"][0]["capacity_l"] = json!(capacity_l);
                result["bodies"][0]["reed_window_l"] = json!(reed_window_l);
            }
            println!("{}", result);
        }
    }
    for (name, material, solid) in [
        ("reservoir-gasket", "gasket", gasket(&n)?),
        (
            "reservoir-tube-grip",
            "grip",
            grip(&n, n.get("liquid_grip")?)?,
        ),
        ("reservoir-air-grip", "grip", grip(&n, n.get("air_grip")?)?),
    ] {
        println!(
            "{}",
            write_part(
                &out,
                name,
                &[Body {
                    name,
                    color: Some(n.color(&format!("color_{material}"))?),
                    solid: &solid
                },]
            )?
        );
    }
    Ok(())
}
