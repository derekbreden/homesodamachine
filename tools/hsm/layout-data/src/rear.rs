//! Rear tube recipes from raw world-port stations and reference dimensions.
use crate::*;

pub type Routes = Vec<(String, Value)>;

pub fn station(stations: &Value, name: &str, port: &str) -> Result<(V3, V3)> {
    let key = format!("{name}.{port}");
    let row = stations
        .get(&key)
        .with_context(|| format!("missing station {key}"))?;
    Ok((xyz(&row[0])?, xyz(&row[1])?))
}

fn add_route(
    out: &mut Routes,
    name: &str,
    segments: Vec<Value>,
    source: (&str, &str),
    destination: (&str, &str),
    radius: Option<f64>,
    spool: &str,
    od: f64,
    inside: f64,
) -> Result<()> {
    let points = sample(&segments)?;
    out.push((name.to_owned(),json!({"segments":segments,"points_mm":points,"centerline_mm":points,
        "od_mm":od,"id_mm":inside,"spool":spool,"owners":[source.0,destination.0],
        "from":format!("{}.{}",source.0,source.1),"frm":format!("{}.{}",source.0,source.1),
        "to":format!("{}.{}",destination.0,destination.1),"minimum_radius_mm":radius,"radius_mm":radius,
        "status":"selected_native_layout"})));
    Ok(())
}

fn links(
    params: &Value,
) -> Result<
    Vec<(
        &'static str,
        &'static str,
        &'static str,
        f64,
        &'static str,
        &'static str,
        f64,
    )>,
> {
    Ok(vec![
        (
            "tee-vk-link",
            "water-split",
            "to-vk",
            15.7,
            "tee-fold",
            "socket",
            16.891,
        ),
        (
            "reg-va-link",
            "flow-regulator",
            "outlet",
            15.,
            "reg-va-elbow",
            "socket",
            16.891,
        ),
        (
            "tee-regulator",
            "water-split",
            "to-flavor",
            15.7,
            "flow-regulator",
            "inlet",
            15.,
        ),
        (
            "pump-inlet-link",
            "suction-reducer",
            "tube",
            number(&params["reducer_insertion"])?,
            "lower-pump-elbow",
            "socket",
            number(&params["stem_insertion"])?,
        ),
    ])
}


pub fn route_specs(spec: &Value, stations: &Value, params: &Value) -> Result<Routes> {
    let plan = &spec["rear_plumbing"];
    let mut out = Vec::new();
    let mut add =
        |name: &str, segments: Vec<Value>, owners: [&str; 2], radius: Option<f64>| -> Result<()> {
            let points = sample(&segments)?;
            out.push((
                name.to_owned(),
                json!({"segments":segments,"points_mm":points,"centerline_mm":points,
            "od_mm":6.35,"id_mm":4.32,"spool":"white","owners":owners,
            "from":owners[0],"to":owners[1],"minimum_radius_mm":radius,
            "status":"complete_between_named_interfaces","basis":"Named receiving socket depths"}),
            ));
            Ok(())
        };
    let d = &plan["water_split_stub"];
    let p = points3(&d["points_mm"])?;
    let a = p[0];
    let b = *p.last().context("water split stub endpoint")?;
    let before = sub(
        a,
        mul(xyz(&d["flow_in"])?, number(&params["reducer_insertion"])?),
    );
    let after = crate::add(
        b,
        mul(xyz(&d["flow_out"])?, number(&params["tee_insertion"])?),
    );
    add(
        "above-core-water-split-stub",
        vec![line(before, a), if d["kind"] == "bezier" { bezier(&p) } else { arc_three(&p)? }, line(b, after)],
        ["jg-pp061208w", "water-split"],
        Some(number(&d["radius_mm"])?),
    )?;
    for (name, first, pa, da, second, pb, db) in links(params)? {
        let flex = &plan["flex_links"][name];
        if !flex.is_null() && flex["kind"] != "tangent_cubic" {
            let p = points3(&flex["points_mm"])?;
            let s = if flex["kind"] == "arc" {
                arc_three(&p)?
            } else {
                bezier(&p)
            };
            add(
                &format!("above-core-{name}"),
                vec![s],
                [first, second],
                flex["minimum_radius_mm"].as_f64(),
            )?;
            continue;
        }
        let (a, ua) = station(stations, first, pa)?;
        let (b, ub) = station(stations, second, pb)?;
        let a = sub(a, mul(ua, da));
        let b = sub(b, mul(ub, db));
        if flex["kind"] == "tangent_cubic" {
            let length = norm(sub(a, b));
            ensure!(length > 0., "tangent cubic endpoints coincide");
            let control = [
                a,
                crate::add(a, mul(ua, length / 3.)),
                crate::add(b, mul(ub, length / 3.)),
                b,
            ];
            let chord = mul(sub(b, a), 1. / length);
            let speed = control
                .windows(2)
                .map(|w| dot(mul(sub(w[1], w[0]), 3.), chord))
                .fold(f64::INFINITY, f64::min);
            let acceleration = control
                .windows(3)
                .map(|w| {
                    norm(std::array::from_fn(|i| {
                        6. * (w[2][i] - 2. * w[1][i] + w[0][i])
                    }))
                })
                .fold(0., f64::max);
            let radius = if speed > 0. {
                if acceleration == 0. {
                    None
                } else {
                    Some(speed * speed / acceleration)
                }
            } else {
                Some(0.)
            };
            add(
                &format!("above-core-{name}"),
                vec![bezier(&control)],
                [first, second],
                radius,
            )?;
        } else {
            add(
                &format!("above-core-{name}"),
                vec![line(a, b)],
                [first, second],
                None,
            )?;
        }
    }
    // The conservative bound is attached only to its tangent-cubic routes.
    for (name, row) in &mut out {
        let id = name.strip_prefix("above-core-").unwrap_or(name);
        if plan["flex_links"][id]["kind"] == "tangent_cubic" {
            row["radius_basis"] = json!("Conservative derivative bound on the tangent cubic");
        }
    }
    Ok(out)
}

pub fn continuations(spec: &Value, stations: &Value, params: &Value) -> Result<Routes> {
    let plan = &spec["rear_plumbing"];
    let mut out = Vec::new();
    let data = &plan["water5_bend"];
    let arcs = data["segments"].as_array().context("water5 arcs")?;
    let a = xyz(&arcs.first().context("water5 arc start")?["points_mm"][0])?;
    let inserted = sub(
        a,
        mul(xyz(&data["flow"])?, number(&params["check_insertion"])?),
    );
    let mut segments = vec![line(inserted, a)];
    segments.extend(arcs.clone());
    add_route(
        &mut out,
        "water-5",
        segments,
        ("discharge-chain", "outlet"),
        ("foam-assembly", "water-in"),
        Some(number(&data["radius_mm"])?),
        "white",
        6.35,
        4.32,
    )?;
    let (a, ua) = station(stations, "digiten-flow", "outlet")?;
    let (b, ub) = station(stations, "bulkhead-carb", "tube-in")?;
    add_route(
        &mut out,
        "soda-meter-bulkhead",
        vec![line(
            sub(a, mul(ua, 15.7)),
            sub(b, mul(ub, number(&params["bulkhead_tube_stop"])?)),
        )],
        ("digiten-flow", "outlet"),
        ("bulkhead-carb", "tube-in"),
        None,
        "blue",
        6.35,
        4.32,
    )?;
    let gas = &plan["co2_tube"];
    let (a, _) = station(stations, "gas-check", "outlet")?;
    let top = xyz(&gas["bend_foot"])?;
    let floor = xyz(&spec["gas_guide_world_mm"])?;
    let da = number(&gas["bend_tangents_mm"][0])?;
    let db = number(&gas["bend_tangents_mm"][1])?;
    let pa = number(&gas["s_tangents_mm"][0])?;
    let pb = number(&gas["s_tangents_mm"][1])?;
    let c1 = [
        a,
        [a[0], a[1] - da, a[2]],
        [top[0], top[1], top[2] + db],
        top,
    ];
    let c2 = [
        top,
        [top[0], top[1], top[2] - pb],
        [floor[0], floor[1], floor[2] + pa],
        floor,
    ];
    add_route(
        &mut out,
        "above-core-gas-core-drop",
        vec![
            line([a[0], a[1] + number(&params["check_insertion"])?, a[2]], a),
            bezier(&c1),
            bezier(&c2),
        ],
        ("gas-check", "outlet"),
        ("foam-assembly", "co2-in"),
        Some(number(&gas["minimum_radius_mm"])?),
        "red",
        6.35,
        4.32,
    )?;
    add_route(
        &mut out,
        "above-core-va-fore-feed",
        spec["fore_routes"]["native_segments"]["va-fore-feed"]
            .as_array()
            .context("VA feed segments")?
            .clone(),
        ("va-south-elbow", "socket"),
        ("ya-stem-elbow", "socket"),
        Some(14.),
        "white",
        6.35,
        4.32,
    )?;
    let (a, ua) = station(stations, "asse-drain-adapter", "tube")?;
    let (b, ub) = station(stations, "bulkhead-drain", "inboard")?;
    let vent = &plan["drain_vent"];
    let mut segments = vec![line(sub(a, mul(ua, 14.)), a)];
    segments.extend(vent["segments"].as_array().context("vent return segments")?.clone());
    segments.push(line(b, sub(b, mul(ub, 10.))));
    add_route(
        &mut out,
        "drain-vent",
        segments,
        ("asse-drain-adapter", "tube"),
        ("bulkhead-drain", "inboard"),
        Some(number(&vent["minimum_radius_mm"])?),
        "drain-white",
        4.,
        2.5,
    )?;
    Ok(out)
}

pub fn flavor_s_bend(start: V3, heading: V3, offset: V3, axis: V3) -> Result<(Vec<Value>, V3)> {
    let angle = (1. - norm(offset) / 50.).acos();
    ensure!(angle.is_finite(), "math domain error");
    let (first, end) = arc(start, heading, axis, angle, 25.);
    let tangent = add(
        mul(heading, angle.cos()),
        mul(cross(axis, heading), angle.sin()),
    );
    let (second, end) = arc(end, tangent, mul(axis, -1.), angle, 25.);
    Ok((vec![first, second], end))
}

pub fn flavor_rear(flavor: &str, destination: V3) -> Result<Vec<Value>> {
    let radius = 25.;
    if flavor == "a" {
        // Pass between the pump and meter caps, below the ASSE and its sleeve.
        // The final rise is aft of the sleeve's tube socket.
        let start = [61., 360., 276.5];
        let lane = 30.;
        let offset = [lane - start[0], 0., 0.];
        let normal = unit(cross([0., 1., 0.], offset))?;
        let (mut fall, low) = flavor_s_bend(start, [0., 1., 0.], offset, normal)?;
        let rise = [destination[0] - lane, 0., destination[2] - start[2]];
        let angle = (1. - norm(rise) / (2. * radius)).acos();
        ensure!(angle.is_finite(), "math domain error");
        let shift_start = [low[0], destination[1] - 2. * radius * angle.sin(), start[2]];
        let normal = unit(cross([0., 1., 0.], rise))?;
        let (shift, _) = flavor_s_bend(shift_start, [0., 1., 0.], rise, normal)?;
        fall.push(line(low, shift_start));
        fall.extend(shift);
        return Ok(fall);
    }
    let peak = 303.5;
    let low_z = destination[2];
    let start = [35., 343., peak];
    let offset = [0., 0., low_z - peak];
    let normal = unit(cross([0., 1., 0.], offset))?;
    let (mut fall, low) = flavor_s_bend(start, [0., 1., 0.], offset, normal)?;
    let offset = [destination[0] - low[0], 0., destination[2] - low_z];
    let angle = (1. - norm(offset) / (2. * radius)).acos();
    ensure!(angle.is_finite(), "math domain error");
    let shift_start = [low[0], destination[1] - 2. * radius * angle.sin(), low_z];
    let normal = unit(cross([0., 1., 0.], offset))?;
    let (shift, _) = flavor_s_bend(shift_start, [0., 1., 0.], offset, normal)?;
    fall.push(line(low, shift_start));
    fall.extend(shift);
    Ok(fall)
}

pub fn flavor_routes(stations: &Value) -> Result<Routes> {
    let radius = 25.;
    let mut out = Vec::new();
    for (flavor, valve, lane, cross_y, aisle, cross_z, lift_y) in [
        ("a", "valve-v-g", -33., 266., 55.5, 296., 291.),
        ("b", "valve-v-j", -40., 274., 35., 293., 299.),
    ] {
        let bulkhead = format!("bulkhead-flavor-{flavor}");
        let (source, axis) = station(stations, valve, "outlet")?;
        let (destination, outward) = station(stations, &bulkhead, "tube-in")?;
        let (mut segments, lead_end) = if flavor == "a" {
            (
                rounded(
                    &[
                        sub(source, mul(axis, 10.)),
                        source,
                        [source[0], source[1], 292.5],
                        [35., 156., 288.5],
                        [-45., 156., 288.5],
                        [-45., 181., 288.5],
                    ],
                    radius,
                )?,
                [-45., 181., 288.5],
            )
        } else {
            (
                rounded(
                    &[
                        sub(source, mul(axis, 10.)),
                        source,
                        [source[0], source[1], 288.5],
                        [source[0], source[1] + radius, 288.5],
                    ],
                    radius,
                )?,
                [source[0], source[1] + radius, 288.5],
            )
        };
        let mut approach = [lane, cross_y - radius - 10., cross_z];
        if flavor == "b" {
            let offset = [lane - lead_end[0], 0., cross_z - lead_end[2]];
            let normal = unit(cross([0., 1., 0.], offset))?;
            let (s, end) = flavor_s_bend(lead_end, [0., 1., 0.], offset, normal)?;
            segments.extend(s);
            approach = end;
        } else {
            let step = (approach[1] - lead_end[1]) / 5.;
            segments.push(bezier(&[
                lead_end,
                [lead_end[0], lead_end[1] + step, lead_end[2]],
                [lead_end[0], lead_end[1] + 2. * step, lead_end[2]],
                [approach[0], lead_end[1] + 3. * step, approach[2]],
                [approach[0], lead_end[1] + 4. * step, approach[2]],
                approach,
            ]));
        }
        segments.extend(rounded(
            &[
                approach,
                [lane, cross_y, cross_z],
                [aisle, cross_y, cross_z],
                [aisle, lift_y, cross_z],
            ],
            radius,
        )?);
        let peak = if flavor == "a" { 276.5 } else { 303.5 };
        let offset = [if flavor == "a" { 5.5 } else { 0. }, 0., peak - cross_z];
        let normal = unit(cross([0., 1., 0.], offset))?;
        let (rise, end) = flavor_s_bend([aisle, lift_y, cross_z], [0., 1., 0.], offset, normal)?;
        segments.extend(rise);
        let rear = flavor_rear(flavor, destination)?;
        let stop = xyz(rear.last().context("flavor rear end")?["points_mm"]
            .as_array()
            .context("rear end points")?
            .last()
            .context("rear end point")?)?;
        segments.push(line(end, xyz(&rear[0]["points_mm"][0])?));
        segments.extend(rear);
        segments.push(line(stop, sub(destination, mul(outward, 10.))));
        let id = if flavor == "a" {
            "fluid-18"
        } else {
            "fluid-28"
        };
        add_route(
            &mut out,
            id,
            segments,
            (valve, "outlet"),
            (&bulkhead, "tube-in"),
            Some(radius),
            "flavor-black-4mm",
            4.,
            2.5,
        )?;
    }
    Ok(out)
}
