//! Appliance frames and native tube recipes, in enclosure millimetres.

use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::f64::consts::PI;

pub type V3 = [f64; 3];
pub fn xyz(v: &Value) -> Result<V3> {
    let a = v.as_array().context("expected three coordinates")?;
    ensure!(a.len() == 3, "expected three coordinates");
    Ok([number(&a[0])?, number(&a[1])?, number(&a[2])?])
}
pub fn number(v: &Value) -> Result<f64> {
    v.as_f64().context("expected a number")
}
pub fn add(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] + b[i])
}
pub fn sub(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] - b[i])
}
pub fn mul(a: V3, b: f64) -> V3 {
    a.map(|v| v * b)
}
pub fn dot(a: V3, b: V3) -> f64 {
    a.into_iter().zip(b).map(|(x, y)| x * y).sum()
}
pub fn norm(a: V3) -> f64 {
    dot(a, a).sqrt()
}
pub fn unit(a: V3) -> Result<V3> {
    let n = norm(a);
    ensure!(n > 0., "zero direction");
    Ok(mul(a, 1. / n))
}
pub fn cross(a: V3, b: V3) -> V3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn vector(r: &Value, p: V3) -> Result<V3> {
    Ok([
        dot(xyz(&r[0])?, p),
        dot(xyz(&r[1])?, p),
        dot(xyz(&r[2])?, p),
    ])
}
pub fn point(frame: &Value, p: V3) -> Result<V3> {
    Ok(add(
        vector(&frame["rotation"], p)?,
        xyz(&frame["translation_mm"])?,
    ))
}
pub fn compose(outer: &Value, inner: &Value) -> Result<Value> {
    let a = &outer["rotation"];
    let b = &inner["rotation"];
    let mut r = [[0.; 3]; 3];
    for i in 0..3 {
        for j in 0..3 {
            for k in 0..3 {
                r[i][j] += number(&a[i][k])? * number(&b[k][j])?;
            }
        }
    }
    Ok(json!({"rotation":r,"translation_mm":point(outer,xyz(&inner["translation_mm"])?)?}))
}
pub use tube::{Segment, Tube};
pub fn line(a: V3, b: V3) -> Segment {
    Segment::Line { points_mm: [a, b] }
}
pub fn bezier(control: &[V3]) -> Segment {
    Segment::Bezier { control_points_mm: control.to_vec() }
}
/// The segments an authored list states.
pub fn segments(v: &Value) -> Result<Vec<Segment>> {
    use serde::Deserialize;
    Vec::deserialize(v).context("expected tube segments")
}
pub fn points3(v: &Value) -> Result<Vec<V3>> {
    v.as_array()
        .context("expected point rows")?
        .iter()
        .map(xyz)
        .collect()
}
pub fn arc(start: V3, tangent: V3, axis: V3, angle: f64, radius: f64) -> (Segment, V3) {
    let center = add(start, mul(cross(axis, tangent), radius));
    let radial = sub(start, center);
    let at = |t: f64| {
        add(
            center,
            add(mul(radial, t.cos()), mul(cross(axis, radial), t.sin())),
        )
    };
    let end = at(angle);
    (
        Segment::Arc {
            points_mm: [start, at(angle / 2.), end],
            radius_mm: Some(radius),
            center_mm: Some(center),
            axis: Some(axis),
            angle_rad: Some(angle),
        },
        end,
    )
}
pub fn arc_three(points: &[V3]) -> Result<Segment> {
    ensure!(points.len() == 3, "an arc takes three points");
    let [a, m, b] = [points[0], points[1], points[2]];
    let u = sub(m, a);
    let v = sub(b, a);
    let n = cross(u, v);
    ensure!(dot(n, n) > 0., "collinear arc points");
    let center = add(
        a,
        mul(
            add(mul(cross(v, n), dot(u, u)), mul(cross(n, u), dot(v, v))),
            1. / (2. * dot(n, n)),
        ),
    );
    let axis = unit(n)?;
    let start = sub(a, center);
    let end = sub(b, center);
    let mut angle = dot(cross(start, end), axis).atan2(dot(start, end));
    if angle < 0. {
        angle += 2. * PI;
    }
    Ok(Segment::Arc {
        points_mm: [a, m, b],
        radius_mm: Some(norm(start)),
        center_mm: Some(center),
        axis: Some(axis),
        angle_rad: Some(angle),
    })
}
pub fn rounded(points: &[V3], radius: f64) -> Result<Vec<Segment>> {
    let mut clean = Vec::new();
    for &p in points {
        if clean.last().is_none_or(|&q| norm(sub(q, p)) > 1e-7) {
            clean.push(p);
        }
    }
    ensure!(!clean.is_empty(), "a path needs at least one point");
    loop {
        let mut remove = Vec::new();
        for i in 1..clean.len().saturating_sub(1) {
            if dot(
                unit(sub(clean[i], clean[i - 1]))?,
                unit(sub(clean[i + 1], clean[i]))?,
            ) > 1. - 1e-8
            {
                remove.push(i);
            }
        }
        if remove.is_empty() {
            break;
        }
        clean = clean
            .into_iter()
            .enumerate()
            .filter_map(|(i, p)| (!remove.contains(&i)).then_some(p))
            .collect();
    }
    let mut bends = vec![None; clean.len()];
    for i in 1..clean.len().saturating_sub(1) {
        let incoming = unit(sub(clean[i], clean[i - 1]))?;
        let outgoing = unit(sub(clean[i + 1], clean[i]))?;
        let angle = dot(incoming, outgoing).clamp(-1., 1.).acos();
        bends[i] = Some((incoming, outgoing, angle, radius * (angle / 2.).tan()));
    }
    for i in 0..clean.len().saturating_sub(1) {
        let used = bends[i].map_or(0., |v| v.3) + bends[i + 1].map_or(0., |v| v.3);
        let available = norm(sub(clean[i], clean[i + 1]));
        ensure!(
            used <= available + 1e-5,
            "R{radius} needs {used:.3} mm on leg {i}; only {available:.3} mm available"
        );
    }
    let mut segments = Vec::new();
    let mut cursor = clean[0];
    for (i, bend) in bends.into_iter().enumerate() {
        if let Some((incoming, outgoing, angle, reach)) = bend {
            let before = sub(clean[i], mul(incoming, reach));
            if norm(sub(cursor, before)) > 1e-7 {
                segments.push(line(cursor, before));
            }
            let (segment, end) = arc(
                before,
                incoming,
                unit(cross(incoming, outgoing))?,
                angle,
                radius,
            );
            segments.push(segment);
            cursor = end;
        }
    }
    if norm(sub(cursor, *clean.last().unwrap())) > 1e-7 {
        segments.push(line(cursor, *clean.last().unwrap()));
    }
    Ok(segments)
}
pub fn binomial(n: usize, k: usize) -> f64 {
    let mut c = 1u64;
    for i in 0..k.min(n - k) {
        c = c * (n - i) as u64 / (i + 1) as u64;
    }
    c as f64
}
pub fn bezier_at(control: &[V3], t: f64) -> V3 {
    let n = control.len() - 1;
    let weights: Vec<_> = (0..=n)
        .map(|k| binomial(n, k) * (1. - t).powi((n - k) as i32) * t.powi(k as i32))
        .collect();
    std::array::from_fn(|i| control.iter().zip(&weights).map(|(p, w)| w * p[i]).sum())
}
pub fn sample(segments: &[Segment]) -> Result<Vec<V3>> {
    let mut result: Vec<V3> = Vec::new();
    for s in segments {
        let points: Vec<V3> = match s {
            Segment::Line { points_mm } => points_mm.to_vec(),
            Segment::Bezier { control_points_mm } => {
                let c = control_points_mm;
                (0..65).map(|i| bezier_at(c, i as f64 / 64.)).collect()
            }
            Segment::Arc { points_mm, center_mm, axis, angle_rad, .. } => {
                let c = center_mm.context("expected three coordinates")?;
                let axis = axis.context("expected three coordinates")?;
                let radial = sub(points_mm[0], c);
                let angle = angle_rad.context("expected a number")?;
                (0..25)
                    .map(|i| {
                        let t = angle * i as f64 / 24.;
                        add(
                            c,
                            add(mul(radial, t.cos()), mul(cross(axis, radial), t.sin())),
                        )
                    })
                    .collect()
            }
        };
        for p in points {
            if result.last().is_none_or(|&q| norm(sub(q, p)) > 1e-6) {
                result.push(p);
            }
        }
    }
    Ok(result)
}
pub fn crowned_beziers(control: &[V3], crown: f64, intervals: usize) -> Result<Vec<Segment>> {
    ensure!(
        control.len() == 4 && intervals > 0,
        "crowned cubic needs four controls and positive intervals"
    );
    let at = |t: f64| {
        let weights = [
            (1. - t).powi(3),
            3. * (1. - t).powi(2) * t,
            3. * (1. - t) * t * t,
            t.powi(3),
        ];
        let mut p: V3 =
            std::array::from_fn(|k| weights.iter().zip(control).map(|(w, p)| w * p[k]).sum());
        let mut d: V3 = std::array::from_fn(|k| {
            3. * ((1. - t).powi(2) * (control[1][k] - control[0][k])
                + 2. * (1. - t) * t * (control[2][k] - control[1][k])
                + t * t * (control[3][k] - control[2][k]))
        });
        p[2] += crown * (PI * t).sin().powi(2);
        d[2] += crown * PI * (2. * PI * t).sin();
        (p, d)
    };
    let h = 1. / intervals as f64;
    let mut out = Vec::new();
    for i in 0..intervals {
        let (a, da) = at(i as f64 * h);
        let (b, db) = at((i + 1) as f64 * h);
        // Keep multiplication and division in the authored order.
        out.push(bezier(&[
            a,
            add(a, da.map(|d| h * d / 3.)),
            sub(b, db.map(|d| h * d / 3.)),
            b,
        ]));
    }
    Ok(out)
}
/// Reservoir A's tubes as they are written down, by name. A tube that is not laid out is left
/// out of them and listed beside them.
pub fn reservoir_routes(
    data: &Value,
) -> Result<(std::collections::BTreeMap<String, Tube>, Vec<tube::Unrouted>)> {
    let mut out = std::collections::BTreeMap::new();
    let mut unrouted = Vec::new();
    for (id, row) in data["paths"].as_object().context("reservoir paths")? {
        match reservoir_route(data, row) {
            Ok(tube) => {
                out.insert(id.clone(), tube);
            }
            Err(error) => unrouted.push(tube::Unrouted::of(
                id,
                row["frm"].as_str().unwrap_or(""),
                row["to"].as_str().unwrap_or(""),
                &error,
            )),
        }
    }
    Ok((out, unrouted))
}

/// One of reservoir A's tubes from its written-down lines and arcs.
fn reservoir_route(data: &Value, row: &Value) -> Result<Tube> {
    let mut segments = Vec::new();
    for s in row["segments"].as_array().context("reservoir segments")? {
        if s["kind"] == "line" {
            segments.push(line(xyz(&s["points_mm"][0])?, xyz(&s["points_mm"][1])?));
            continue;
        }
        let start = xyz(&s["start_mm"])?;
        let axis = xyz(&s["axis"])?;
        let tangent = unit(cross(axis, sub(start, xyz(&s["center_mm"])?)))?;
        let (mut native, _) = arc(
            start,
            tangent,
            axis,
            number(&s["angle_rad"])?,
            number(&s["radius_mm"])?,
        );
        if let Segment::Arc { points_mm, .. } = &mut native {
            points_mm[0] = start;
            points_mm[2] = xyz(&s["end_mm"])?;
        }
        segments.push(native);
    }
    if row["reverse"].as_bool().unwrap_or(false) {
        segments.reverse();
        for s in &mut segments {
            match s {
                Segment::Line { points_mm } => points_mm.reverse(),
                Segment::Bezier { control_points_mm } => control_points_mm.reverse(),
                Segment::Arc { points_mm, axis, .. } => {
                    points_mm.reverse();
                    *axis = match *axis {
                        Some(axis) => Some(mul(axis, -1.)),
                        None => None,
                    };
                }
            }
        }
    }
    let points = sample(&segments)?;
    let from = row["frm"].as_str().context("reservoir from")?;
    let to = row["to"].as_str().context("reservoir to")?;
    let a = from.split('.').next().unwrap();
    let b = to.split('.').next().unwrap();
    let owners = if a == b { vec![a] } else { vec![a, b] };
    let radius = data["minimum_radius_mm"].as_f64();
    Ok(Tube {
        radius_mm: Some(radius),
        minimum_radius_mm: Some(radius),
        from: Some(from.to_owned()),
        frm: Some(from.to_owned()),
        to: Some(to.to_owned()),
        owners: Some(owners.into_iter().map(str::to_owned).collect()),
        status: Some("selected_native_layout".to_owned()),
        note: Some("Reservoir A continuous tube retained by the fore and aft paired lid anchors; the plain guide adds no joint or cut".to_owned()),
        ..Tube::of(
            segments,
            number(&data["tube_od_mm"])?,
            number(&data["tube_id_mm"])?,
            data["spool"].as_str().context("reservoir spool")?,
        )
        .through(points)
    })
}

/// The above-core fittings that are NeoFit stem elbows, among those the layout places: every
/// candidate the layout's `snapshots` stand, unless it stands as a John Guest union elbow.
pub fn stem_elbow_names(snapshots: &Value) -> Vec<&'static str> {
    const CANDIDATES: [&str; 23] = [
        "tee-fold",
        "lower-valve-elbow",
        "lower-pump-elbow",
        "reg-va-elbow",
        "va-outlet-elbow",
        "va-south-elbow",
        "carbonator-fold",
        "gas-inlet-elbow",
        "gas-lower-a",
        "gas-lower-b",
        "gas-upper-a",
        "gas-upper-b",
        "soda-stem-elbow",
        "soda-outlet-return-stem",
        "ya-stem-elbow",
        "drain-outlet-stem",
        "vb-inlet-turn",
        "vb-outlet-stem",
        "vb-outlet-return",
        "yb-stem-elbow",
        "reservoir-a-fill-turn",
        "reservoir-a-draw-turn",
        "reservoir-b-fill-turn",
    ];
    CANDIDATES
        .into_iter()
        .filter(|n| !snapshots[n].is_null() && snapshots[n]["geometry"] != "jg-turn-elbow")
        .collect()
}

/// The above-core fittings that stand as John Guest union elbows.
pub fn union_elbow_names(snapshots: &Value) -> Vec<&'static str> {
    ["va-east-turn", "ya-fold-inner", "vb-inlet-turn", "vb-outlet-return"]
        .into_iter()
        .filter(|n| snapshots[n]["geometry"] == "jg-turn-elbow")
        .collect()
}

/// The reservoir turns that plug straight into a valve: each turn's valve and its port.
pub fn gates() -> Value {
    json!({"reservoir-a-fill-turn":["valve-v-f","outlet"],"reservoir-a-draw-turn":["valve-v-e","inlet"],"reservoir-b-fill-turn":["valve-v-i","outlet"]})
}

/// The equipment the cold core's side of the layout owns, by name, sorted.
pub fn equipment_names() -> Vec<String> {
    let mut names = vec![
        "pcba".to_string(),
        "g-ganen-pump".into(),
        "pump-snap-cap".into(),
        "valve-v-b".into(),
        "discharge-chain".into(),
        "carbonator-fold".into(),
        "vb-inlet-turn".into(),
        "vb-outlet-stem".into(),
        "vb-outlet-return".into(),
        "lower-pump-elbow".into(),
    ];
    for side in ["suction", "discharge"] {
        for p in [
            "tube",
            "reducer",
            "barb-clamp",
            "barb-key",
            "stem-clamp",
            "stem-key",
        ] {
            names.push(format!("{side}-{p}"));
        }
    }
    names.sort();
    names
}

/// The rear wall's bulkhead fittings in the order of the fluid grid's rows and columns: each
/// one's place on the wall and the tube, nut and barrel its kind takes.
pub fn grid(spec: &Value) -> Result<Vec<Value>> {
    let g = &spec["fluid_grid"];
    let mut rows = Vec::new();
    for (row, names) in g["assignment"]
        .as_array()
        .context("grid assignment")?
        .iter()
        .enumerate()
    {
        for (column, name) in names.as_array().context("grid row")?.iter().enumerate() {
            let gas = name == "co2-inlet";
            let quarter = name == "bulkhead-water" || name == "bulkhead-carb" || gas;
            rows.push(json!({"name":name,"x":g["columns_x_mm"][column],"z":g["rows_z_mm"][row],"tube_od_mm":if quarter{6.35}else{4.},
                "flange_y":spec["enclosure"]["rear_y_mm"],"nut_af_mm":if gas{21.0058}else if quarter{20.}else{18.},
                "nut_depth_mm":if gas{7.0104}else if quarter{4.}else{6.5},"barrel_d_mm":if gas{17.}else if quarter{17.14}else{15.},
                "native_kind":if gas{"gas"}else if quarter{"quarter"}else{"four"}}));
        }
    }
    Ok(rows)
}

pub mod fore;
pub mod soda;

pub mod rear;
pub mod routes;
pub mod tube;
