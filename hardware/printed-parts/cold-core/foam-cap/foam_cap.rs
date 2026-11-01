//! The cold-core equipment lid, bottom closure, R14 holder and continuous pump snap.
use anyhow::{Context, Result};
use hsm_kernel::math::{cos, sin, PI, TAU};
use hsm_kernel::part::{args, write_printed, Numbers};
use hsm_kernel::*;
use serde_json::Value;

fn sqrt(v: f64) -> f64 {
    v.sqrt()
}
fn f(v: &Value, key: &str) -> Result<f64> {
    v[key].as_f64().with_context(|| format!("number {key}"))
}
fn a(v: &Value) -> Result<&Vec<Value>> {
    v.as_array().context("array")
}
fn p2(v: &Value) -> Result<V2> {
    Ok(v2(v[0].as_f64().context("x")?, v[1].as_f64().context("y")?))
}
fn p3(v: &Value) -> Result<V3> {
    Ok(v3(
        v[0].as_f64().context("x")?,
        v[1].as_f64().context("y")?,
        v[2].as_f64().context("z")?,
    ))
}
fn box3(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(
        v3(x0.min(x1), y0.min(y1), z0.min(z1)),
        v3(x0.max(x1), y0.max(y1), z0.max(z1)),
    )
}
fn bounds(v: &Value) -> Result<Solid> {
    Ok(Solid::cuboid(p3(&v[0])?, p3(&v[1])?))
}
fn frame(v: &Value) -> Result<Affine> {
    let r = &v["rotation"];
    let column = |i| -> Result<V3> {
        Ok(v3(
            r[0][i].as_f64().context("rotation")?,
            r[1][i].as_f64().context("rotation")?,
            r[2][i].as_f64().context("rotation")?,
        ))
    };
    Ok(Affine::from_columns(
        column(0)?,
        column(1)?,
        column(2)?,
        p3(&v["translation_mm"])?,
    ))
}
fn world_to_cap(n: &Numbers) -> Result<Affine> {
    let axes = n.get("world_to_cap_axes")?;
    Ok(Affine::from_columns(
        p3(&axes[0])?,
        p3(&axes[1])?,
        p3(&axes[2])?,
        p3(n.get("world_to_cap_origin")?)?,
    ))
}
fn outline(n: &Numbers, z0: f64, z1: f64, inset: f64) -> Result<Solid> {
    Plane::XY.offset(z0).extrude(
        &Profile::new(Loop::rounded_rect(
            v2(0., 0.),
            n.f("width")? - 2. * inset,
            n.f("depth")? - 2. * inset,
            n.f("corner")? - inset,
        )?),
        z1 - z0,
    )
}
fn cylinder(xy: V2, z0: f64, z1: f64, radius: f64) -> Result<Solid> {
    Solid::cylinder(v3(xy.x, xy.y, z0), V3::Z, radius, z1 - z0)
}
fn head_pockets(n: &Numbers, top: bool, z: f64, depth: f64) -> Result<Solid> {
    let r = n.f("head_radius")?;
    let mut cuts = vec![];
    for station in a(n.get(if top {
        "top_stations"
    } else {
        "bottom_stations"
    })?)? {
        let p = p2(&station["xy"])?;
        cuts.push(cylinder(p, z, z + depth, r)?);
        match station["wall"].as_str().context("wall")? {
            "corner" => {
                let ox = p.x - p.x.signum() * (n.f("width")? / 2. - n.f("corner")?);
                let oy = p.y - p.y.signum() * (n.f("depth")? / 2. - n.f("corner")?);
                let angle = hsm_kernel::math::atan2(oy, ox) * 180. / PI - 90.;
                cuts.push(
                    box3(-r, r, 0., 2. * n.f("corner")? + 2., 0., depth)
                        .rotate(V3::ZERO, V3::Z, angle)
                        .translate(v3(p.x, p.y, z)),
                );
            }
            "x" => cuts.push(box3(
                p.x,
                p.x.signum() * (n.f("width")? / 2. + 1.),
                p.y - r,
                p.y + r,
                z,
                z + depth,
            )),
            _ => cuts.push(box3(
                p.x - r,
                p.x + r,
                p.y,
                p.y.signum() * (n.f("depth")? / 2. + 1.),
                z,
                z + depth,
            )),
        }
    }
    Solid::union_all(&cuts)
}
fn bosses(n: &Numbers, height: f64, r: f64) -> Result<Solid> {
    let mut stock = vec![];
    for station in a(n.get("bottom_stations")?)? {
        let p = p2(&station["xy"])?;
        stock.push(cylinder(p, 0., height, r)?);
        let wall = station["wall"].as_str().context("wall")?;
        if matches!(wall, "corner" | "y") {
            stock.push(box3(
                p.x - r,
                p.x + r,
                p.y,
                p.y.signum() * n.f("depth")? / 2.,
                0.,
                height,
            ));
        }
        if matches!(wall, "corner" | "x") {
            stock.push(box3(
                p.x,
                p.x.signum() * n.f("width")? / 2.,
                p.y - r,
                p.y + r,
                0.,
                height,
            ));
        }
    }
    Solid::union_all(&stock)?.intersect(&outline(n, 0., height, 0.)?)
}
fn bottom_cap(n: &Numbers) -> Result<Solid> {
    let h = n.f("bottom_height")?;
    let mut body = outline(n, 0., h, 0.)?
        .cut(&outline(n, n.f("floor")?, h, n.f("wall")?)?)?
        .union(&bosses(n, h, n.f("boss_radius")?)?)?
        .union(&bosses(
            n,
            n.f("lid_height")?,
            n.f("boss_radius")? + n.f("head_pad_growth")?,
        )?)?
        .cut(&head_pockets(
            n,
            false,
            0.,
            n.f("head_depth")? + n.f("supported_surface")?,
        )?)?;
    let mut cuts = vec![];
    for station in a(n.get("bottom_stations")?)? {
        cuts.push(cylinder(
            p2(&station["xy"])?,
            0.,
            h + 0.1,
            n.f("screw_radius")?,
        )?);
    }
    for hole in a(n.get("bottom_holes")?)? {
        cuts.push(cylinder(
            p2(&hole["xy"])?,
            -0.1,
            h + 0.1,
            f(hole, "radius")?,
        )?);
    }
    body = body.cut(&Solid::union_all(&cuts)?)?;
    Ok(body)
}

fn teardrop(b: &Value, radius: f64) -> Result<Profile> {
    let (x, z) = (f(b, "bend")?, f(b, "centre")?);
    let k = radius / sqrt(2.);
    Ok(Profile::new(
        Pen::new(v2(x + k, z + k))
            .line_to(v2(x, z + sqrt(2.) * radius))
            .line_to(v2(x - k, z + k))
            .arc_through(v2(x, z - radius), v2(x + k, z + k))?
            .close()?,
    ))
}
fn b_body(b: &Value) -> Result<Profile> {
    let (bend, outer, z) = (
        f(b, "bend")?,
        f(b, "outer")?,
        f(b, "centre")? + f(b, "dome_lift")?,
    );
    Ok(Profile::new(
        Pen::new(v2(bend - outer, 0.))
            .line_to(v2(bend + outer, 0.))
            .line_to(v2(bend + outer, z))
            .arc_through(v2(bend, z + outer), v2(bend - outer, z))?
            .close()?,
    ))
}
fn b_mouth(b: &Value, tear: bool) -> Result<Solid> {
    let mut sections = vec![];
    for (y, r) in [
        (f(b, "mouth_start")?, f(b, "radius")? + f(b, "mouth")? + 0.3),
        (f(b, "mouth_end")?, f(b, "radius")? - 0.05),
    ] {
        let profile = if tear {
            teardrop(b, r)?
        } else {
            Profile::circle(v2(f(b, "bend")?, f(b, "centre")?), r)
        };
        sections.push(profile.place(&Plane::XZ.at(v3(0., y, 0.))));
    }
    Solid::loft(&sections)
}
fn b_channel(n: &Numbers) -> Result<Solid> {
    let b = n.get("b_fill")?;
    let section = Profile::circle(v2(f(b, "bend")?, f(b, "centre")?), f(b, "radius")?);
    let mut air = Plane::XZ
        .revolve(&section, 90., v2(0., 0.), v2(0., 1.))?
        .union(&Plane::XZ.extrude(&section, f(b, "inlet")?)?)?;
    let mouth = b_mouth(b, false)?;
    air = air
        .union(&mouth.translate(v3(0., -f(b, "inlet")?, 0.)))?
        .union(&mouth.mirror(V3::ZERO, v3(1., -1., 0.)))?;
    let end = p3(&b["end_world"])?;
    air = air.rotate(V3::ZERO, V3::Y, -90.).translate(v3(
        end.x + f(b, "centre")?,
        end.y - f(b, "bend")?,
        end.z,
    ));
    air = air.union(&air.translate(V3::Z * n.f("supported_surface")?))?;
    Ok(air.transformed(&world_to_cap(n)?))
}
fn fine_section(profile: Profile) -> Result<Profile> {
    let mut segments = vec![];
    for segment in profile.outer.segs {
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
    Ok(Profile::new(Loop::new(segments)?))
}
fn b_holder(n: &Numbers) -> Result<Solid> {
    let b = n.get("b_fill")?;
    // Section and turn both curve. Bisect the section's circular intervals
    // so their combined chord error stays inside the fabrication rule.
    let body = Plane::XZ.revolve(&fine_section(b_body(b)?)?, 90., v2(0., 0.), v2(0., 1.))?;
    let air = Plane::XZ.revolve(
        &fine_section(teardrop(b, f(b, "radius")?)?)?,
        90.,
        v2(0., 0.),
        v2(0., 1.),
    )?;
    let mouth = b_mouth(b, true)?;
    body.cut(&air)?
        .cut(&mouth)?
        .cut(&mouth.mirror(V3::ZERO, v3(1., -1., 0.)))
}

fn pump_room(n: &Numbers, datum: &Value, seat: bool) -> Result<Solid> {
    let can = &datum["can"];
    let axis = p3(&can["axis_direction"])?;
    let origin = p3(&can["axis_point_mm"])?;
    let ends = &datum["band_native_x_mm"];
    let (first, last) = (
        ends[0].as_f64().context("first")?,
        ends[1].as_f64().context("last")?,
    );
    let start = v3(
        first - 1.,
        origin.y,
        origin.z + axis.z * (first - 1. - origin.x) / axis.x,
    );
    let t = frame(&datum["frame"])?;
    let radius = f(
        datum,
        if seat {
            "seat_bore_radius_mm"
        } else {
            "bore_radius_mm"
        },
    )?;
    let _ = n;
    Solid::cylinder(
        t.point(start),
        t.vector(axis),
        radius,
        (last - first + 2.) / axis.x,
    )
}
fn pump_cap_world(shape: &Solid, d: &Value) -> Result<Solid> {
    let c = p3(&d["centre_world_mm"])?;
    Ok(shape
        .rotate(v3(c.x, 0., 0.), V3::Y, 180.)
        .translate(V3::Z * c.z))
}
fn pump_cradle(n: &Numbers) -> Result<Solid> {
    let d = n.get("pump")?;
    let c = p3(&d["centre_world_mm"])?;
    let first = d["band_native_x_mm"][0].as_f64().context("first")?;
    let last = d["band_native_x_mm"][1].as_f64().context("last")?;
    let fy = d["frame"]["translation_mm"][1].as_f64().context("pump y")?;
    let face = n.f("cap_face_world_z")?;
    let wide = f(d, "stock_half_width_mm")?;
    let mut body = box3(
        c.x - wide,
        c.x + wide,
        fy + first,
        fy + last,
        face - 0.1,
        c.z,
    )
    .cut(&pump_room(n, d, true)?)?;
    let lo = d["cover_room_native_y_mm"][0]
        .as_f64()
        .context("cover lo")?;
    let hi = d["cover_room_native_y_mm"][1]
        .as_f64()
        .context("cover hi")?;
    body = body.cut(&box3(
        c.x - hi,
        c.x - lo,
        fy + first - 0.1,
        fy + last + 0.1,
        face - 0.2,
        c.z + 0.8,
    ))?;
    for rail in a(&d["rail_rooms"])? {
        let planes = a(&rail["floor_planes"])?;
        let plane = |v: &Value| -> Result<[f64; 3]> {
            let p = p3(v)?;
            Ok([
                p.x,
                p.y,
                p.z - n.f("running")? * sqrt(1. + p.x * p.x + p.y * p.y),
            ])
        };
        let (a, b) = (plane(&planes[0])?, plane(&planes[1])?);
        let outer = f(rail, "outer_y_mm")?;
        let mut profiles = vec![];
        for x in [first - 0.1, last + 0.1] {
            let y = ((b[0] - a[0]) * x + b[2] - a[2]) / (a[1] - b[1]);
            profiles.push(Region::polygon(vec![
                v3(x, outer, a[0] * x + a[1] * outer + a[2]),
                v3(x, y, a[0] * x + a[1] * y + a[2]),
                v3(x, 0., b[0] * x + b[2]),
                v3(x, 0., 100.),
                v3(x, outer, 100.),
            ]));
        }
        body = body.cut(&Solid::loft(&profiles)?.transformed(&frame(&d["frame"])?))?;
    }
    let selected = &d["selected"];
    let inner = selected["rail_stop_contact_native_y_mm"][1]
        .as_f64()
        .context("stop inner contact")?;
    let top = d["frame"]["translation_mm"][2].as_f64().context("pump z")?
        + f(selected, "rail_stop_native_z_mm")?;
    let stops = a(&selected["rail_stop_native_x_mm"])?;
    let fore = &stops[0];
    let rear = &stops[1];
    let fore0 = fore[0].as_f64().context("fore stop outside")?;
    let fore1 = fore[1].as_f64().context("fore stop inside")?;
    let rear0 = rear[0].as_f64().context("rear stop inside")?;
    let rear1 = rear[1].as_f64().context("rear stop outside")?;
    let rail = a(&d["rail_rooms"])?
        .iter()
        .find(|rail| rail["side"].as_f64().is_some_and(|side| side < 0.))
        .context("negative-Y fixed rail")?;
    let rail_outer = f(rail, "outer_y_mm")?;
    let backing = box3(
        c.x - inner,
        c.x + wide,
        fy + fore0,
        fy + rear1,
        face - 0.1,
        c.z,
    );
    let head_room = box3(
        c.x - inner - 0.1,
        c.x + wide + 0.1,
        fy + fore0 - 0.1,
        fy + first,
        top,
        c.z + 0.2,
    );
    let corridor = box3(
        c.x - inner - 0.1,
        c.x - rail_outer,
        fy + fore1,
        fy + rear0,
        face - 0.2,
        c.z + 0.1,
    );
    body = body.union(&backing.cut(&head_room)?.cut(&corridor)?)?;
    for cap in a(&d["caps"])? {
        let s = &cap["snap_station"];
        for side in [-1., 1.] {
            let far = f(s, "axis_x")? + side * (f(s, "outer")? + 1.);
            for (start, z0, z1) in [
                ("ledge", f(s, "split")? - 1., f(s, "bearing")?),
                ("neck", f(s, "bearing")?, f(s, "ceiling")?),
            ] {
                let x = f(s, "axis_x")? + side * f(s, start)?;
                let pocket = box3(
                    x,
                    far,
                    f(s, "y0")? - n.f("running")?,
                    f(s, "y1")? + n.f("running")?,
                    z0,
                    z1,
                );
                body = body.cut(&pump_cap_world(&pocket, cap)?)?;
            }
        }
    }
    Ok(body.transformed(&world_to_cap(n)?))
}
fn pump_snap(n: &Numbers) -> Result<Solid> {
    let d = &n.get("pump")?["caps"][0];
    let s = &d["snap_station"];
    let (c, w, wi, h) = (
        f(s, "axis_x")?,
        f(s, "outer")?,
        f(s, "inner")?,
        f(s, "hook")?,
    );
    let (catch, tip) = (f(s, "catch")?, f(s, "tip")?);
    let base = -n.f("slip")?;
    let r = f(d, "bore_radius_mm")? + f(&d["selected"], "cap_arch_wall_mm")?;
    let west = [
        v2(c - w, 0.),
        v2(c - w, tip),
        v2(c - h, tip),
        v2(c - h, catch),
        v2(c - wi, catch),
        v2(c - wi, base),
    ];
    let mut pen = Pen::new(west[0]);
    for &p in &west[1..] {
        pen = pen.line_to(p);
    }
    for p in west.iter().rev() {
        pen = pen.line_to(v2(2. * c - p.x, p.y));
    }
    let tx = r * r / w;
    let tz = -r * sqrt((1. - (r / w) * (r / w)).max(0.));
    pen = pen
        .line_to(v2(c + tx, tz))
        .arc_through(v2(c, -r), v2(c - tx, tz))?;
    let profile = Profile::new(pen.close()?);
    let blank = Plane::XZ
        .at(v3(0., f(s, "y1")?, 0.))
        .extrude(&profile, f(s, "y1")? - f(s, "y0")?)?;
    let snap = pump_cap_world(&blank, d)?
        .cut(&pump_room(n, d, false)?)?
        .rotate(V3::ZERO, V3::X, 90.);
    let b = snap.bounds();
    Ok(snap.translate(v3(
        -(b.min.x + b.max.x) / 2.,
        -(b.min.y + b.max.y) / 2.,
        -b.min.z,
    )))
}

fn valve_wall(n: &Numbers) -> Result<Solid> {
    let d = n.get("valve_wall")?;
    let mut body = Solid::cuboid(
        p3(&d["bearing_min_world_mm"])?,
        p3(&d["bearing_max_world_mm"])?,
    )
    .union(&Solid::cuboid(
        p3(&d["root_min_world_mm"])?,
        p3(&d["root_max_world_mm"])?,
    ))?;
    let v = n.get("valve")?;
    let t = frame(n.get("valve_pose")?)?;
    let mut cuts = vec![];
    for sx in [-1., 1.] {
        for sy in [-1., 1.] {
            cuts.push(
                cylinder(
                    v2(sx * f(v, "corner_inset_x")?, sy * f(v, "corner_inset_y")?),
                    f(v, "socket_floor_z")?,
                    f(v, "seat_top_z")? + 1.,
                    f(v, "socket_radius")?,
                )?
                .transformed(&t),
            );
        }
    }
    let length = 2. * f(v, "seat_half_y")? + 2.;
    cuts.push(
        Solid::cylinder(
            v3(0., -length / 2., n.f("valve_port_z")?),
            V3::Y,
            n.f("valve_port_radius")? + f(v, "port_air")?,
            length,
        )?
        .transformed(&t),
    );
    body = body.cut(&Solid::union_all(&cuts)?)?;
    Ok(body.transformed(&world_to_cap(n)?))
}
fn union_features(n: &Numbers) -> Result<(Vec<Solid>, Vec<Solid>)> {
    let (mut stock, mut cuts) = (vec![], vec![]);
    let t = world_to_cap(n)?;
    for d in n
        .get("union_supports")?
        .as_object()
        .context("union supports")?
        .values()
    {
        if d["parent"].as_str() != Some("foam-assembly") {
            continue;
        }
        stock.push(
            Solid::cuboid(p3(&d["stock_min_world_mm"])?, p3(&d["stock_max_world_mm"])?)
                .cut(&Solid::cylinder(
                    p3(&d["bore_origin_world_mm"])?,
                    p3(&d["bore_axis_world"])?,
                    f(d, "seat_radius_mm")?,
                    f(d, "bore_length_mm")?,
                )?)?
                .transformed(&t),
        );
        let normal = p3(&d["tie_profile_normal_world"])?;
        let plane = Plane::new(
            p3(&d["tie_profile_origin_world_mm"])? - normal * 40.,
            p3(&d["tie_profile_x_world"])?,
            normal,
        )?;
        let pts = a(&d["tie_profile_mm"])?
            .iter()
            .map(p2)
            .collect::<Result<Vec<_>>>()?;
        cuts.push(plane.extrude(&Profile::polygon(&pts), 80.)?.transformed(&t));
    }
    Ok((stock, cuts))
}
fn wells(n: &Numbers) -> Result<(Solid, Solid)> {
    let (mut stock, mut cuts) = (vec![], vec![]);
    let (wall, fit) = (n.f("well_wall")?, n.f("well_fit")?);
    let t = world_to_cap(n)?;
    for w in a(n.get("wells")?)? {
        let size = &w["size"];
        let (width, depth, height) = (
            size[0].as_f64().context("well width")?,
            size[1].as_f64().context("well depth")?,
            size[2].as_f64().context("well height")?,
        );
        let placement = frame(&w["pose"])?;
        stock.push(
            box3(
                -width / 2. - fit - wall,
                width / 2. + fit + wall,
                -depth / 2. - fit - wall,
                0.,
                -fit - wall,
                height + fit + wall,
            )
            .transformed(&placement)
            .transformed(&t),
        );
        cuts.push(
            box3(
                -width / 2. - fit,
                width / 2. + fit,
                -depth / 2. - fit,
                1.,
                -fit,
                height + fit,
            )
            .transformed(&placement)
            .transformed(&t),
        );
    }
    Ok((Solid::union_all(&stock)?, Solid::union_all(&cuts)?))
}

fn tube_clip(n: &Numbers, c: &Value) -> Result<Solid> {
    let centre = p3(&c["centre"])?;
    let u = p3(&c["along"])?.unit();
    let plane = Plane::new(centre - u * (f(c, "span")? / 2.), u.cross(V3::Z), u)?;
    let (ri, wing, span) = (f(c, "radius")?, f(c, "wing")?, f(c, "span")?);
    let (ro, rm, nose) = (ri + wing, ri + wing / 2., wing / 2.);
    let tip = f(c, "tip_degrees")? * PI / 180.;
    let point = |r: f64, t: f64| v2(r * sin(t), r * cos(t));
    let (a, b, c, d) = (
        point(ro, -tip),
        point(ro, tip),
        point(ri, tip),
        point(ri, -tip),
    );
    let (cp, cn) = (point(rm, tip), point(rm, -tip));
    let reach = centre.z - n.f("cap_face_world_z")? + 0.1;
    // Trace the filled root and the two free jaws as one section. The root
    // replaces the outer half-circle on the host side of the tube axis.
    let outer = Pen::new(v2(-ro, reach))
        .line_to(v2(ro, reach))
        .line_to(v2(ro, 0.))
        .arc_through(point(ro, (PI / 2. + tip) / 2.), b)?
        .arc_through(cp + v2(nose * cos(tip), -nose * sin(tip)), c)?
        .arc_through(v2(0., ri), d)?
        .arc_through(cn + v2(-nose * cos(-tip), nose * sin(-tip)), a)?
        .arc_through(point(ro, -(PI / 2. + tip) / 2.), v2(-ro, 0.))?
        .close()?;
    plane.extrude(&Profile::new(outer), span)
}
fn cable_seat(n: &Numbers, bank: bool) -> Result<Solid> {
    let s = n.get(if bank { "cable_bank" } else { "cable_hook" })?;
    let (stock, depth, beak, span) = (
        f(s, "stock")?,
        f(s, "seat_depth")?,
        f(s, "beak")?,
        f(s, "span")?,
    );
    let points = if bank {
        let first = s["seat_heights"][0].as_f64().context("first seat")?;
        let second = s["seat_heights"][1].as_f64().context("second seat")?;
        let (a, b, c, d) = (
            stock,
            stock + depth,
            2. * stock + depth,
            2. * (stock + depth),
        );
        let width = 3. * stock + 2. * depth;
        let (ra, rb) = (stock + first, stock + second);
        let (ta, tb) = (ra + stock + beak, rb + stock + beak);
        vec![
            v2(0., -0.1),
            v2(width - stock, -0.1),
            v2(width, stock - 0.1),
            v2(width, tb),
            v2(d, tb),
            v2(d - beak, tb - beak),
            v2(d - beak, rb),
            v2(d, rb),
            v2(d, stock),
            v2(c, stock),
            v2(c, ta),
            v2(b, ta),
            v2(b - beak, ta - beak),
            v2(b - beak, ra),
            v2(b, ra),
            v2(b, stock),
            v2(a, stock),
            v2(a, ta),
            v2(0., ta),
        ]
    } else {
        let inner = stock + depth;
        let width = 2. * stock + depth;
        let roof = stock + f(s, "seat_height")?;
        let top = roof + stock + beak;
        vec![
            v2(0., -0.1),
            v2(width, -0.1),
            v2(width, top),
            v2(inner, top),
            v2(inner - beak, top - beak),
            v2(inner - beak, roof),
            v2(inner, roof),
            v2(inner, stock),
            v2(stock, stock),
            v2(stock, top),
            v2(0., top),
        ]
    };
    let origin = p3(&s["origin"])? + V3::Y * (span / 2.);
    Ok(Plane::XZ
        .at(origin)
        .extrude(&Profile::polygon(&points), span)?
        .transformed(&world_to_cap(n)?))
}

fn route_air(segments: &Value, radius: f64) -> Result<Solid> {
    let segments = a(segments)?;
    let first = p3(&segments[0]["points_mm"][0])?;
    let mut path = Path::new(first);
    for segment in segments {
        let points = a(&segment["points_mm"])?;
        match segment["kind"].as_str().context("route kind")? {
            "line" => {
                let end = p3(points.last().context("route end")?)?;
                path = path.line_to(end);
            }
            "arc" => path = path.arc_through(p3(&points[1])?, p3(&points[2])?)?,
            other => anyhow::bail!("route segment {other}"),
        }
    }
    // A swept circle has both section and path chord error; subdivide the same
    // circular path at half intervals so the combined error stays within LINEAR.
    let mut fine = Path::new(first);
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
                            + d * (d.dot(v) * (1. - cos(angle)))
                    };
                    fine = fine.arc_center(c, end, d)?;
                }
            }
            Leg::Curve { .. } => anyhow::bail!("circular seat route"),
        }
    }
    let normal = match path.legs.first().context("first route leg")? {
        Leg::Line { a, b } => (*b - *a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(*a - *c).unit(),
        _ => anyhow::bail!("circular seat route"),
    };
    let (_, x, _) = hsm_kernel::rule::plane_frame(normal);
    Plane::new(first, x, normal)?.sweep(&Profile::circle(v2(0., 0.), radius), &fine)
}
fn a_seats(n: &Numbers) -> Result<(Solid, Solid)> {
    let (mut additions, mut cuts) = (vec![], vec![]);
    let t = world_to_cap(n)?;
    let spec = n.get("a_seat_spec")?;
    for row in n.get("a_seats")?.as_object().context("a seats")?.values() {
        if row["closure"].as_str() == Some("direct-snap") {
            let d = n.get("a_snap")?;
            let stock = bounds(&d["base_bounds_mm"])?;
            let mut body = stock;
            // Fore clips are appended with the other C2 seats below; their
            // bore also cuts the broad common base across the complete span.
            for p in a(&d["tube_centers_world_mm"])? {
                let p = p3(p)?;
                body = body.cut(&Solid::cylinder(
                    p - V3::Y * (f(d, "station_length_mm")? / 2. + 0.1),
                    V3::Y,
                    f(d, "seat_radius_mm")?,
                    f(d, "station_length_mm")? + 0.2,
                )?)?;
            }
            additions.push(body.transformed(&t));
            continue;
        }
        let lo = p3(&row["stock_bounds_mm"][0])?;
        let hi = p3(&row["stock_bounds_mm"][1])?;
        let mut profile = vec![v2(lo.x, lo.z), v2(hi.x, lo.z)];
        for p in a(&row["seat_roof_xz_mm"])?.iter().rev() {
            profile.push(p2(p)?);
        }
        let mut body = Plane::XZ
            .at(v3(0., hi.y, 0.))
            .extrude(&Profile::polygon(&profile), hi.y - lo.y)?;
        for route in a(&row["routes_west_to_east"])? {
            let id = route.as_str().context("route id")?;
            body = body.cut(&route_air(
                &n.get("a_routes")?[id],
                f(spec, "seat_radius_mm")?,
            )?)?;
        }
        let mut mouths = vec![bounds(&row["tie_slot_bounds_mm"])?];
        for cut in a(&row["access_bounds_mm"])? {
            mouths.push(bounds(cut)?);
        }
        if !row["open_quarter_bounds_mm"].is_null() {
            mouths.push(bounds(&row["open_quarter_bounds_mm"])?);
        }
        let cut = Solid::union_all(&mouths)?;
        additions.push(body.cut(&cut)?.transformed(&t));
        cuts.push(cut.transformed(&t));
    }
    Ok((Solid::union_all(&additions)?, Solid::union_all(&cuts)?))
}

fn top_lid(n: &Numbers) -> Result<Solid> {
    let h = n.f("lid_height")?;
    let t = world_to_cap(n)?;
    let mut body = outline(n, 0., h, 0.)?.cut(&head_pockets(
        n,
        true,
        h - n.f("head_depth")?,
        n.f("head_depth")?,
    )?)?;
    let mut cuts = vec![];
    for station in a(n.get("top_stations")?)? {
        cuts.push(cylinder(
            p2(&station["xy"])?,
            0.,
            h + n.f("floor")?,
            n.f("screw_radius")?,
        )?);
    }
    for xy in n.get("conduits")?.as_object().context("conduits")?.values() {
        cuts.push(cylinder(
            p2(xy)?,
            0.,
            h + n.f("floor")?,
            n.f("conduit_radius")?,
        )?);
    }
    for xy in n.get("reliefs")?.as_object().context("reliefs")?.values() {
        let p = p2(xy)?;
        cuts.push(Solid::cone(
            v3(p.x, p.y, h - n.f("floor")?),
            V3::Z,
            n.f("conduit_radius")?,
            n.f("relief_radius")?,
            n.f("floor")?,
        )?);
    }
    cuts.push(b_channel(n)?);
    for g in a(n.get("straight_guides")?)? {
        let p = p3(&g["point"])?;
        cuts.push(
            Solid::cylinder(
                v3(p.x, p.y, f(g, "floor")? - 1.),
                V3::Z,
                n.f("conduit_radius")?,
                p.z + 2. - f(g, "floor")?,
            )?
            .transformed(&t),
        );
    }
    body = body.cut(&Solid::union_all(&cuts)?)?;
    for g in a(n.get("straight_guides")?)? {
        let p = p3(&g["point"])?;
        let z0 = t.point(p).z;
        let mut guide = cylinder(
            v2(t.point(p).x, t.point(p).y),
            0.,
            z0,
            n.f("conduit_radius")? + 3.,
        )?;
        guide = guide.cut(&cylinder(
            v2(t.point(p).x, t.point(p).y),
            -0.1,
            z0 + 1.,
            n.f("conduit_radius")?,
        )?)?;
        body = body.union(&guide)?;
    }
    let gb = &n.get("b_fill")?["guide_bounds_cap"];
    let (lo, hi) = (p3(&gb[0])?, p3(&gb[1])?);
    body = body.cut(&box3(
        lo.x - 0.15,
        hi.x + 0.15,
        lo.y - 0.15,
        hi.y + 0.15,
        -0.1,
        h + 0.1,
    ))?;
    for c in a(n.get("deck_columns")?)? {
        let p = p2(&c["xy"])?;
        let top = f(c, "top")?;
        body = body
            .union(&cylinder(p, h - 0.1, top, n.f("deck_radius")?)?)?
            .cut(&cylinder(
                p,
                top - n.f("deck_bore_depth")?,
                top + 0.1,
                n.f("deck_bore_radius")?,
            )?)?;
    }
    body = body.union(&pump_cradle(n)?)?.union(&valve_wall(n)?)?;
    let (supports, passages) = union_features(n)?;
    for s in supports {
        body = body.union(&s)?;
    }
    for c in passages {
        body = body.cut(&c)?;
    }
    let (stock, pockets) = wells(n)?;
    body = body
        .union(&stock.intersect(&outline(n, -1., stock.bounds().max.z + 1., 0.)?)?)?
        .cut(&pockets)?;
    let (stock, passages) = a_seats(n)?;
    body = body.union(&stock)?.cut(&passages)?;
    let wall = n.get("flavor_wall")?;
    let x0 = wall["root_min_world_mm"][0]
        .as_f64()
        .context("flavor wall x")?;
    let y0 = wall["root_max_world_mm"][1]
        .as_f64()
        .context("flavor wall y")?
        - 0.1;
    let z0 = n.f("cap_face_world_z")? - 0.1;
    let root_front = 266. - (4.1 / 2. + 1.52);
    let front = root_front + 0.1;
    let bridge = Plane::YZ.at(v3(x0, 0., 0.)).extrude(
        &Profile::polygon(&[
            v2(y0, z0),
            v2(front, z0),
            v2(front, 296. + front - root_front),
            v2(y0, 296. + y0 - root_front),
        ]),
        30.5 - x0,
    )?;
    for (i, c) in a(n.get("tube_clips")?)?.iter().enumerate() {
        let clip = tube_clip(n, c)?;
        let clip = if i == 1 {
            // End both axial sections on the wall root's own plane, where
            // the 45-degree bridge meets the full clip root.
            let centre = p3(&c["centre"])?;
            let half = f(c, "span")? / 2.;
            let mut left = c.clone();
            let mut right = c.clone();
            left["centre"] = serde_json::json!([(centre.x - half + x0) / 2., centre.y, centre.z]);
            left["span"] = serde_json::json!(x0 - centre.x + half);
            right["centre"] = serde_json::json!([(centre.x + half + x0) / 2., centre.y, centre.z]);
            right["span"] = serde_json::json!(centre.x + half - x0);
            tube_clip(n, &left)?.union(&tube_clip(n, &right)?.union(&bridge)?)?
        } else {
            clip
        };
        body = body.union(&clip.transformed(&t))?;
    }
    body = body
        .union(&cable_seat(n, true)?)?
        .union(&cable_seat(n, false)?)?;
    let mut air = vec![];
    for hole in a(n.get("air_holes")?)? {
        air.push(cylinder(
            p2(&hole["xy"])?,
            -0.1,
            h + 0.1,
            f(hole, "radius")?,
        )?);
    }
    body.cut(&Solid::union_all(&air)?)
}

fn main() -> Result<()> {
    let (n, dir) = args()?;
    let parts = [
        ("foam-cap-lid-top", top_lid(&n)?),
        ("foam-cap-bottom", bottom_cap(&n)?),
        ("reservoir-b-fill-guide", b_holder(&n)?),
        ("pump-snap-cap", pump_snap(&n)?),
    ];
    for (name, solid) in parts {
        let color = n.get("colors")?[name].as_array().context("color")?;
        let color = [
            color[0].as_f64().context("red")?,
            color[1].as_f64().context("green")?,
            color[2].as_f64().context("blue")?,
        ];
        let result = write_printed(
            &dir,
            name,
            &[Body {
                name,
                color: Some(color),
                solid: &solid,
            }],
        )?;
        println!("{}", result);
    }
    Ok(())
}
