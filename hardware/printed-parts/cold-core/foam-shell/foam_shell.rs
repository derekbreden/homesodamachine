//! The cold-core shell from the mating cavity, stock, supports and passages Python owns.
use anyhow::{ensure, Context, Result};
use hsm_kernel::math::{acos, cos, sin, tan, TAU};
use hsm_kernel::part::{args, write_printed, Numbers};
use hsm_kernel::*;
use serde_json::{json, Value};

fn f(value: &Value, name: &str) -> Result<f64> {
    value[name]
        .as_f64()
        .with_context(|| format!("no number {name}"))
}

fn point2(value: &Value) -> Result<V2> {
    Ok(v2(
        value[0].as_f64().context("point x")?,
        value[1].as_f64().context("point y")?,
    ))
}

fn point3(value: &Value) -> Result<V3> {
    Ok(v3(
        value[0].as_f64().context("point x")?,
        value[1].as_f64().context("point y")?,
        value[2].as_f64().context("point z")?,
    ))
}

fn box3(x: (f64, f64), y: (f64, f64), z: (f64, f64)) -> Solid {
    Solid::cuboid(
        v3(x.0.min(x.1), y.0.min(y.1), z.0.min(z.1)),
        v3(x.0.max(x.1), y.0.max(y.1), z.0.max(z.1)),
    )
}

fn ranges(value: &Value) -> Result<Solid> {
    let range = |i: usize| -> Result<(f64, f64)> {
        Ok((
            value[i][0].as_f64().context("range start")?,
            value[i][1].as_f64().context("range end")?,
        ))
    };
    Ok(box3(range(0)?, range(1)?, range(2)?))
}

fn pocket_loop(p: &Value) -> Result<Loop> {
    let (x, y, far, r) = (
        f(p, "middle_x")?,
        f(p, "inner_y")?,
        f(p, "far_x")?,
        f(p, "corner_radius")?,
    );
    let (tx, ty, turn) = (
        f(p, "transition_x")?,
        f(p, "transition_mid_y")?,
        f(p, "transition_y")?,
    );
    Pen::new(v2(x, y))
        .line_to(v2(far - r, y))
        .radius_arc(v2(far, y - r), r)?
        .line_to(v2(far, -y + r))
        .radius_arc(v2(far - r, -y), r)?
        .line_to(v2(x, -y))
        .arc_through(v2(tx, -ty), v2(x, -turn))?
        .arc_through(v2(f(p, "arc_radius")?, 0.0), v2(x, turn))?
        .arc_through(v2(tx, ty), v2(x, y))?
        .close()
}

fn support_ring(n: &Numbers) -> Result<Solid> {
    let s = n.get("support")?;
    let (inner, outer, z0, z1) = (
        f(s, "inner_radius")?,
        f(s, "outer_radius")?,
        f(s, "bottom")?,
        f(s, "top")?,
    );
    let section = |a, b| Profile::polygon(&[v2(a, z0), v2(b, z0), v2(b, z1), v2(a, z1)]);
    let mut ring = Plane::XZ.revolve(&section(inner, outer), 360.0, v2(0.0, 0.0), v2(0.0, 1.0))?;
    let margin = f(s, "slot_margin")?;
    let angle = f(s, "slot_angle")?;
    let slot = Plane::XZ.revolve(
        &section(inner - margin, outer + margin),
        angle,
        v2(0.0, 0.0),
        v2(0.0, 1.0),
    )?;
    let count = s["slots"].as_u64().context("support slot count")?;
    for i in 0..count {
        let start = 360.0 / count as f64 * (i as f64 + 0.5) + f(s, "slot_clock")? - angle / 2.0;
        ring = ring.cut(&slot.rotate(V3::ZERO, v3(0.0, 0.0, 1.0), start))?;
    }
    Ok(ring)
}

fn rounded_path(points: &[V3], bend: f64) -> Result<Path> {
    ensure!(points.len() >= 2, "a route has at least two points");
    let mut v = vec![points[0]];
    for &p in &points[1..] {
        if (p - v[v.len() - 1]).norm() < 1e-9 {
            continue;
        }
        if v.len() >= 2 {
            let (a, b) = (v[v.len() - 2], v[v.len() - 1]);
            if (b - a).unit().cross((p - b).unit()).norm() < 1e-9 {
                *v.last_mut().unwrap() = p;
                continue;
            }
        }
        v.push(p);
    }
    let count = v.len();
    let mut half = vec![0.0; count];
    let mut radii = vec![0.0; count];
    for i in 1..count - 1 {
        half[i] = acos(
            (v[i - 1] - v[i])
                .unit()
                .dot((v[i + 1] - v[i]).unit())
                .clamp(-1.0, 1.0),
        ) / 2.0;
        radii[i] = bend;
    }
    for _ in 0..64 {
        let setback: Vec<f64> = (0..count)
            .map(|i| {
                if half[i] > 1e-9 {
                    radii[i] / tan(half[i])
                } else {
                    0.0
                }
            })
            .collect();
        let mut worst: f64 = 1.0;
        for i in 0..count - 1 {
            let (leg, want) = ((v[i + 1] - v[i]).norm(), setback[i] + setback[i + 1]);
            if want > leg {
                worst = worst.min(leg / want);
            }
        }
        if worst >= 1.0 - 1e-12 {
            break;
        }
        for r in &mut radii[1..count - 1] {
            *r *= worst * 0.999;
        }
    }
    let mut path = Path::new(v[0]);
    let mut tail = v[0];
    for i in 1..count - 1 {
        let (u, w) = ((v[i - 1] - v[i]).unit(), (v[i + 1] - v[i]).unit());
        let setback = radii[i] / tan(half[i]);
        let (enter, leave) = (v[i] + u * setback, v[i] + w * setback);
        let centre = v[i] + (u + w).unit() * (radii[i] / sin(half[i]));
        let mid = centre + (v[i] - centre).unit() * radii[i];
        if (enter - tail).norm() > 1e-7 {
            path = path.line_to(enter);
        }
        path = path.arc_through(mid, leave)?;
        tail = leave;
    }
    if (v[count - 1] - tail).norm() > 1e-7 {
        path = path.line_to(v[count - 1]);
    }
    Ok(path)
}

fn vent(n: &Numbers) -> Result<Solid> {
    let points = n
        .get("vent_route")?
        .as_array()
        .context("vent route points")?
        .iter()
        .map(point3)
        .collect::<Result<Vec<_>>>()?;
    let path = rounded_path(&points, n.f("vent_bend")?)?;
    let radius = n.f("vent_radius")?;
    // The swept bend combines the path's and section's chord errors. Bisect each path
    // interval on the same circular arc so their combined error stays within LINEAR.
    let mut fine = Path::new(points[0]);
    for leg in &path.legs {
        match *leg {
            Leg::Line { b, .. } => fine = fine.line_to(b),
            Leg::Arc { a, b, c, d, turn } => {
                let count = 2
                    * ((hsm_kernel::rule::ring_count((a - c).norm() + radius) as f64 * turn / TAU
                        - 1e-9)
                        .ceil() as usize)
                        .max(1);
                let v = a - c;
                for i in 1..=count {
                    let angle = turn * i as f64 / count as f64;
                    let end = if i == count {
                        b
                    } else {
                        c + v * cos(angle)
                            + d.cross(v) * sin(angle)
                            + d * (d.dot(v) * (1.0 - cos(angle)))
                    };
                    fine = fine.arc_center(c, end, d)?;
                }
            }
            Leg::Curve { .. } => anyhow::bail!("vent route uses straight and circular legs"),
        }
    }
    let normal = match path.legs.first().context("vent route leg")? {
        Leg::Line { a, b } => (*b - *a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(*a - *c).unit(),
        Leg::Curve { .. } => anyhow::bail!("vent route uses straight and circular legs"),
    };
    let (_, x, _) = hsm_kernel::rule::plane_frame(normal);
    Plane::new(points[0], x, normal)?.sweep(&Profile::circle(v2(0.0, 0.0), radius), &fine)
}

fn b_fill_air(n: &Numbers) -> Result<Solid> {
    let b = n.get("b_fill")?;
    let (bend, centre, radius) = (
        f(b, "bend_radius")?,
        f(b, "channel_centre")?,
        f(b, "channel_radius")?,
    );
    let inlet = f(b, "inlet_leg")?;
    let section = Profile::circle(v2(bend, centre), radius);
    let turn = Plane::XZ.revolve(&section, 90.0, v2(0.0, 0.0), v2(0.0, 1.0))?;
    let mut channel = turn.union(&Plane::XZ.extrude(&section, inlet)?)?;
    let start_y = f(b, "mouth_start_y")?;
    let end_y = f(b, "mouth_end_y")?;
    let mouth = Solid::cone(
        v3(bend, start_y, centre),
        V3::Y,
        f(b, "mouth_start_radius")?,
        f(b, "mouth_end_radius")?,
        end_y - start_y,
    )?;
    channel = channel
        .union(&mouth.translate(v3(0.0, -inlet, 0.0)))?
        .union(&mouth.mirror(V3::ZERO, v3(1.0, -1.0, 0.0)))?;
    let end = point3(&b["bend_end_world"])?;
    channel =
        channel
            .rotate(V3::ZERO, V3::Y, -90.0)
            .translate(v3(end.x + centre, end.y - bend, end.z));
    channel = channel.union(&channel.translate(v3(0.0, 0.0, f(b, "roof_allowance")?)))?;
    let axes = b["world_to_shell_axes"]
        .as_array()
        .context("world-to-shell axes")?;
    let transform = Affine::from_columns(
        point3(&axes[0])?,
        point3(&axes[1])?,
        point3(&axes[2])?,
        point3(&b["world_to_shell_origin"])?,
    );
    Ok(channel.transformed(&transform))
}

fn attachment_bosses(n: &Numbers, height: f64, radius: f64) -> Result<Solid> {
    let (width, depth, corner) = (n.f("width")?, n.f("depth")?, n.f("corner_radius")?);
    let footprint = Plane::XY.extrude(
        &Profile::new(Loop::rounded_rect(v2(0.0, 0.0), width, depth, corner)?),
        height,
    )?;
    let stations = n
        .get("attachment_stations")?
        .as_array()
        .context("attachment station list")?;
    let mut bosses = vec![];
    for station in stations {
        let p = point2(&station["xy"])?;
        bosses.push(Plane::XY.at(v3(p.x, p.y, 0.0)).cylinder(radius, height)?);
    }
    for station in stations {
        let p = point2(&station["xy"])?;
        let wall = station["wall"].as_str().context("attachment wall")?;
        if matches!(wall, "corner" | "y") {
            bosses.push(box3(
                (p.x - radius, p.x + radius),
                (p.y, p.y.signum() * depth / 2.0),
                (0.0, height),
            ));
        }
        if matches!(wall, "corner" | "x") {
            bosses.push(box3(
                (p.x, p.x.signum() * width / 2.0),
                (p.y - radius, p.y + radius),
                (0.0, height),
            ));
        }
    }
    Solid::union_all(&bosses)?.intersect(&footprint)
}

fn build(n: &Numbers) -> Result<Solid> {
    let (height, wall, outer_wall) = (n.f("height")?, n.f("wall")?, n.f("outer_wall")?);
    let (width, depth, corner) = (n.f("width")?, n.f("depth")?, n.f("corner_radius")?);
    let footprint = Loop::rounded_rect(v2(0.0, 0.0), width, depth, corner)?;
    let outside = Plane::XY.extrude(&Profile::new(footprint), height)?;
    let inside = Plane::XY.at(v3(0.0, 0.0, n.f("floor")?)).extrude(
        &Profile::new(Loop::rounded_rect(
            v2(0.0, 0.0),
            width - 2.0 * outer_wall,
            depth - 2.0 * outer_wall,
            corner - outer_wall,
        )?),
        height - n.f("floor")?,
    )?;
    let stations = n
        .get("attachment_stations")?
        .as_array()
        .context("attachment station list")?;
    let hosts = attachment_bosses(n, height, n.f("host_radius")?)?;
    let mut outer = outside.cut(&inside)?.union(&hosts)?;
    let (face, seam_floor, half) = (
        depth / 2.0,
        depth / 2.0 - n.f("seam_depth")?,
        n.f("seam_width")? / 2.0,
    );
    outer = outer
        .union(&box3(
            (-half - outer_wall, half + outer_wall),
            (seam_floor - outer_wall, seam_floor),
            (0.0, height),
        ))?
        .cut(&box3(
            (-half, half),
            (seam_floor, face + 1.0),
            (-1.0, height + 1.0),
        ))?;

    let pocket = pocket_loop(n.get("pocket")?)?.ccw();
    let cavity = Plane::XY.extrude(&Profile::new(pocket.clone()), n.f("pocket_height")?)?;
    let grown = Plane::XY.extrude(
        &Profile::new(pocket.offset(wall, true)?),
        n.f("pocket_height")?,
    )?;
    let pocket = grown.cut(&cavity)?;
    let mut shell = pocket
        .union(&pocket.mirror(V3::ZERO, v3(1.0, 0.0, 0.0)))?
        .union(&support_ring(n)?)?
        .union(&outer)?;
    let envelopes = n
        .get("reed_envelopes")?
        .as_array()
        .context("reed envelopes")?;
    let cavities = n
        .get("reed_cavities")?
        .as_array()
        .context("reed cavities")?;
    let backs = n
        .get("reed_upper_backs")?
        .as_array()
        .context("upper reed backs")?;
    for ((envelope, cavity), back) in envelopes.iter().zip(cavities).zip(backs) {
        let channel = ranges(envelope)?
            .cut(&ranges(cavity)?)?
            .union(&ranges(back)?)?;
        shell = shell.union(&channel)?;
    }
    for (bottom, length) in [
        (0.0, n.f("insert_depth")? + n.f("supported_surface")?),
        (height - n.f("insert_depth")?, n.f("insert_depth")?),
    ] {
        let holes = stations
            .iter()
            .map(|s| -> Result<Solid> {
                let p = point2(&s["xy"])?;
                Plane::XY
                    .at(v3(p.x, p.y, bottom))
                    .cylinder(n.f("insert_radius")?, length)
            })
            .collect::<Result<Vec<_>>>()?;
        shell = shell.cut_all(&holes)?;
    }
    for taper in n
        .get("bottom_tapers")?
        .as_array()
        .context("bottom blind-end tapers")?
    {
        let holes = stations
            .iter()
            .map(|station| -> Result<Solid> {
                let p = point2(&station["xy"])?;
                Solid::cone(
                    v3(p.x, p.y, f(taper, "bottom")?),
                    V3::Z,
                    f(taper, "lower_radius")?,
                    f(taper, "upper_radius")?,
                    f(taper, "height")?,
                )
            })
            .collect::<Result<Vec<_>>>()?;
        shell = shell.cut_all(&holes)?;
    }
    for (bottom, length) in [
        (0.0, n.f("bottom_tail_depth")? + n.f("supported_surface")?),
        (height - n.f("top_tail_depth")?, n.f("top_tail_depth")?),
    ] {
        let holes = stations
            .iter()
            .map(|s| -> Result<Solid> {
                let p = point2(&s["xy"])?;
                Plane::XY
                    .at(v3(p.x, p.y, bottom))
                    .cylinder(n.f("tail_radius")?, length)
            })
            .collect::<Result<Vec<_>>>()?;
        shell = shell.cut_all(&holes)?;
    }
    let corridor = vent(n)?;
    shell =
        shell
            .cut(&corridor)?
            .cut(&corridor.translate(v3(0.0, 0.0, n.f("supported_surface")?)))?;
    for origin in n
        .get("copper_origins")?
        .as_array()
        .context("copper origins")?
    {
        let p = point3(origin)?;
        shell = shell.cut(&Solid::cylinder(
            p - v3(2.0, 0.0, 0.0),
            v3(1.0, 0.0, 0.0),
            n.f("copper_radius")?,
            outer_wall + 4.0,
        )?)?;
    }
    for opening in n
        .get("reed_openings")?
        .as_array()
        .context("reed openings")?
    {
        shell = shell.cut(&ranges(opening)?)?;
    }
    for roof in n
        .get("reed_roofs")?
        .as_array()
        .context("sensing window roof tapers")?
    {
        let section = roof["section"]
            .as_array()
            .context("sensing roof section")?
            .iter()
            .map(point2)
            .collect::<Result<Vec<_>>>()?;
        let wedge = Plane::new(v3(f(roof, "start_x")?, 0.0, 0.0), V3::Y, V3::X)?
            .extrude(&Profile::polygon(&section), f(roof, "depth")?)?;
        shell = shell.cut(&wedge)?;
    }
    shell = shell.cut(&b_fill_air(n)?)?;
    let outlet = n.get("reed_b_outlet")?;
    let (lo, hi) = (
        point3(&outlet["notch_min_mm"])?,
        point3(&outlet["notch_max_mm"])?,
    );
    let shoulder = f(outlet, "roof_shoulder_z_mm")?;
    let notch = Plane::new(v3(lo.x, 0.0, 0.0), V3::Y, V3::X)?.extrude(
        &Profile::polygon(&[
            v2(lo.y, lo.z),
            v2(hi.y, lo.z),
            v2(hi.y, shoulder),
            v2(
                point2(&outlet["axis_xy_mm"])?.y,
                f(outlet, "roof_peak_z_mm")?,
            ),
            v2(lo.y, shoulder),
        ]),
        hi.x - lo.x,
    )?;
    shell = shell.cut(&notch)?;
    Ok(shell)
}

fn measurements(n: &Numbers, shell: &Solid) -> Result<Value> {
    let origins = n
        .get("copper_origins")?
        .as_array()
        .context("copper origins")?;
    let names = n.get("copper_names")?.as_array().context("copper names")?;
    let mut ports = vec![];
    for (name, origin) in names.iter().zip(origins) {
        let p = point3(origin)?;
        let probe = Solid::cylinder(
            p - V3::X,
            V3::X,
            n.f("copper_radius")? - 0.25,
            n.f("floor")? + 2.0,
        )?;
        let blocked = probe.intersect(shell)?.volume();
        ensure!(
            blocked <= 1e-3,
            "front-face station {name} at {p:?} is blocked by {blocked} mm³"
        );
        ports.push(json!({"name": name, "origin": p.to_array(), "blocked_mm3": blocked}));
    }
    let b = shell.bounds();
    Ok(
        json!({"volume": shell.volume(), "centroid": shell.centroid().to_array(),
              "min": b.min.to_array(), "max": b.max.to_array(), "front_ports": ports}),
    )
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let shell = build(&n)?;
    let readings = measurements(&n, &shell)?;
    let mut written = write_printed(
        &out,
        "foam-shell",
        &[Body {
            name: "foam-shell",
            color: Some(n.color("color")?),
            solid: &shell,
        }],
    )?;
    written["bodies"][0]
        .as_object_mut()
        .context("written shell body")?
        .extend(readings.as_object().context("shell measurements")?.clone());
    println!("{written}");
    Ok(())
}
