use super::*;
pub type V = [f64; 3];
pub fn v(value: &Value) -> Result<V> {
    let a = rows(value)?;
    ensure!(a.len() == 3, "three wire coordinates");
    Ok([number(&a[0])?, number(&a[1])?, number(&a[2])?])
}
pub fn points(value: &Value) -> Result<Vec<V>> {
    rows(value)?.iter().map(v).collect()
}
pub fn add(a: V, b: V) -> V {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}
pub fn sub(a: V, b: V) -> V {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
pub fn mul(a: V, t: f64) -> V {
    [a[0] * t, a[1] * t, a[2] * t]
}
pub fn dot(a: V, b: V) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
pub fn cross(a: V, b: V) -> V {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn norm(a: V) -> f64 {
    dot(a, a).sqrt()
}
pub fn unit(a: V) -> V {
    mul(a, 1. / norm(a))
}
pub fn stock() -> Result<Value> {
    let mut stock: Value = serde_json::from_str(include_str!("stock.json"))?;
    for (name, color) in [
        ("neutral18", json!([0.9, 0.9, 0.87])),
        ("earth18", json!([0.06, 0.42, 0.12])),
    ] {
        let mut row = stock["cord18"].clone();
        row["color"] = color;
        stock[name] = row;
    }
    Ok(stock)
}
pub fn line(a: V, b: V) -> Value {
    json!({"kind":"line","start_mm":a,"end_mm":b,"length_mm":norm(sub(b,a))})
}
pub fn rounded(
    input: &Value,
    radius: f64,
    keep_collinear: bool,
    endpoint_fraction: f64,
) -> Result<Value> {
    let mut pts: Vec<V> = Vec::new();
    for point in points(input)? {
        if pts.last().is_none_or(|last| norm(sub(*last, point)) > 1e-6) {
            pts.push(point);
        }
        if !keep_collinear {
            while pts.len() > 2 {
                let n = pts.len();
                let a = sub(pts[n - 2], pts[n - 3]);
                let b = sub(pts[n - 1], pts[n - 2]);
                if dot(unit(a), unit(b)) < 1. - 1e-10 {
                    break;
                }
                pts.remove(n - 2);
            }
        }
    }
    ensure!(!pts.is_empty(), "wire route has no points");
    let mut corners = BTreeMap::new();
    for i in 1..pts.len().saturating_sub(1) {
        let before = sub(pts[i - 1], pts[i]);
        let after = sub(pts[i + 1], pts[i]);
        let (la, lb) = (norm(before), norm(after));
        let (u, v) = (unit(before), unit(after));
        let included = dot(u, v).clamp(-1., 1.).acos();
        if included < 1e-5 || (std::f64::consts::PI - included).abs() < 1e-5 {
            continue;
        }
        let tangent = (radius / (included / 2.).tan())
            .min((if i == 1 { endpoint_fraction } else { 0.44 }) * la)
            .min(
                (if i == pts.len() - 2 {
                    endpoint_fraction
                } else {
                    0.44
                }) * lb,
            );
        let r = tangent * (included / 2.).tan();
        let a = add(pts[i], mul(u, tangent));
        let b = add(pts[i], mul(v, tangent));
        let bisector = unit(add(u, v));
        let centre = add(pts[i], mul(bisector, r / (included / 2.).sin()));
        let midpoint = add(centre, mul(bisector, -r));
        corners.insert(i, (a, midpoint, b, r, std::f64::consts::PI - included));
    }
    let mut out = Vec::new();
    let mut current = pts[0];
    fn append(out: &mut Vec<Value>, current: &mut V, end: V) {
        let segment = line(*current, end);
        if segment["length_mm"].as_f64().unwrap() > 1e-6 {
            out.push(segment);
        }
        *current = end;
    }
    for i in 1..pts.len().saturating_sub(1) {
        if let Some(&(a, mid, b, r, angle)) = corners.get(&i) {
            append(&mut out, &mut current, a);
            out.push(json!({"kind":"arc","start_mm":a,"midpoint_mm":mid,"end_mm":b,"radius_mm":r,"angle_radians":angle,"length_mm":r*angle}));
            current = b;
        } else {
            append(&mut out, &mut current, pts[i]);
        }
    }
    append(&mut out, &mut current, *pts.last().unwrap());
    Ok(json!(out))
}
pub fn spline(input: &Value, tangent_input: &Value, chord_length: bool) -> Result<Value> {
    let tangents = points(tangent_input)?;
    let points = points(input)?;
    ensure!(
        points.len() >= 3 && tangents.len() == 2,
        "spline endpoints and tangents"
    );
    let count = points.len() - 1;
    let mut derivatives = Vec::new();
    for (direction, a, b, c) in [
        (tangents[0], points[0], points[1], points[2]),
        (
            tangents[1],
            points[count],
            points[count - 1],
            points[count - 2],
        ),
    ] {
        let derivative = mul(sub(sub(mul(b, 4.), c), mul(a, 3.)), count as f64 / 2.);
        derivatives.push(mul(unit(direction), dot(derivative, unit(direction)).abs()));
    }
    let mut parameters = (0..=count)
        .map(|i| i as f64 / count as f64)
        .collect::<Vec<_>>();
    if chord_length {
        let mut distances = vec![0.];
        for pair in points.windows(2) {
            distances.push(distances.last().unwrap() + norm(sub(pair[1], pair[0])));
        }
        let length = *distances.last().unwrap();
        parameters = distances.iter().map(|d| d / length).collect();
        derivatives = tangents.iter().map(|t| mul(unit(*t), length)).collect();
    }
    let mut segment = json!({"kind":"spline","start_mm":points[0],"end_mm":points[count],"interpolation_points_mm":points,"endpoint_tangents":tangents,"endpoint_derivatives":derivatives,"parameters":parameters});
    let result = wire_samples::measure(&segment)?;
    segment
        .as_object_mut()
        .unwrap()
        .extend(result.as_object().unwrap().clone());
    Ok(segment)
}
pub fn circle(segment: &Value) -> Result<(V, V)> {
    let a = v(&segment["start_mm"])?;
    let u = sub(v(&segment["midpoint_mm"])?, a);
    let b = sub(v(&segment["end_mm"])?, a);
    let n = cross(u, b);
    let centre = add(
        a,
        mul(
            add(mul(cross(n, u), dot(b, b)), mul(cross(b, n), dot(u, u))),
            1. / (2. * dot(n, n)),
        ),
    );
    Ok((centre, unit(n)))
}
pub fn rotate(v: V, axis: V, angle: f64) -> V {
    add(
        add(mul(v, angle.cos()), mul(cross(axis, v), angle.sin())),
        mul(axis, dot(axis, v) * (1. - angle.cos())),
    )
}
pub fn sample(segments: &Value, step: f64) -> Result<Vec<V>> {
    let mut out = Vec::new();
    fn append(out: &mut Vec<V>, a: V, b: V, step: f64) {
        let count = (norm(sub(b, a)) / step).ceil().max(1.) as usize;
        for i in 0..count {
            out.push(add(a, mul(sub(b, a), i as f64 / count as f64)));
        }
    }
    for s in rows(segments)? {
        let a = v(&s["start_mm"])?;
        let b = v(&s["end_mm"])?;
        match string(&s["kind"])? {
            "line" => append(&mut out, a, b, step),
            "spline" => {
                for pair in points(&s["sampled_points_mm"])?.windows(2) {
                    append(&mut out, pair[0], pair[1], step);
                }
            }
            "arc" => {
                let (centre, n) = circle(s)?;
                let radius = number(&s["radius_mm"])?;
                let x = mul(sub(a, centre), 1. / radius);
                let y = cross(n, x);
                let count = (number(&s["length_mm"])? / step).ceil().max(2.) as usize;
                for i in 0..count {
                    let angle = number(&s["angle_radians"])? * i as f64 / count as f64;
                    out.push(add(
                        centre,
                        mul(add(mul(x, angle.cos()), mul(y, angle.sin())), radius),
                    ));
                }
            }
            kind => bail!("Unknown wire segment {kind}"),
        }
    }
    if let Some(last) = rows(segments)?.last() {
        out.push(v(&last["end_mm"])?);
    }
    Ok(out)
}
pub fn record(route: &Value) -> Result<Value> {
    let mut record = route["connection"].clone();
    let out = record.as_object_mut().context("route connection")?;
    for (from, to) in [
        ("points", "points_mm"),
        ("segments", "segments"),
        ("minimum_bend_mm", "minimum_bend_mm"),
        ("status", "route_status"),
        ("note", "routing_note"),
    ] {
        out.insert(to.into(), route[from].clone());
    }
    out.insert(
        "length_mm".into(),
        json!(py_round(number(&route["length_mm"])?, 3)?),
    );
    Ok(record)
}
pub fn finish(data: &Value) -> Result<Value> {
    let stock = stock()?;
    let connection = &data["connection"];
    let radius = optional(
        data,
        "radius",
        if stock[string(&connection["stock"])?]["awg"]
            .as_u64()
            .unwrap()
            < 22
        {
            5.
        } else {
            4.
        },
    );
    let segments = rounded(
        &data["points"],
        radius,
        false,
        optional(data, "endpoint_tangent_fraction", 0.44),
    )?;
    let length = rows(&segments)?
        .iter()
        .map(|s| number(&s["length_mm"]))
        .collect::<Result<Vec<_>>>()?
        .iter()
        .sum::<f64>();
    let minimum = rows(&segments)?
        .iter()
        .filter_map(|s| s["radius_mm"].as_f64())
        .reduce(f64::min)
        .map(|v| py_round(v, 4))
        .transpose()?;
    Ok(
        json!({"connection":connection,"points":data["points"],"segments":segments,"length_mm":length,"minimum_bend_mm":minimum,"status":"selected_layout","note":data.get("note").and_then(Value::as_str).unwrap_or("")}),
    )
}
