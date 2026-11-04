//! Logical warm-side route composition, retaining authored route order.
use crate::rear::{Routes, station};
use crate::*;

fn append_pairs(out: &mut Routes, rows: &Value) -> Result<()> {
    for row in rows.as_array().context("ordered route rows")? {
        let name = row[0].as_str().context("route name")?;
        if let Some((_, held)) = out.iter_mut().find(|(key, _)| key == name) {
            *held = row[1].clone();
        } else {
            out.push((name.to_owned(), row[1].clone()));
        }
    }
    Ok(())
}

pub fn specifications(v: &Value) -> Result<Value> {
    let spec = &v["spec"];
    let stations = &v["stations"];
    let mut out = vec![("soda-core-rise".to_owned(), soda::tube(spec)?)];
    append_pairs(&mut out, &v["continuations"])?;
    append_pairs(&mut out, &v["flavors"])?;
    append_pairs(&mut out, &v["reservoir"])?;
    let (a, ua) = station(stations, "foam-assembly", "reservoir-b")?;
    let (b, ub) = station(stations, "valve-v-h", "inlet")?;
    let z = 295.7;
    let lift = add(a, [0., 0., 3.6]);
    let angle = (1f64 - 13. / 28.).acos();
    let (offset_first, mid) = arc(lift, [0., 0., 1.], [0., 1., 0.], angle, 14.);
    let (offset_second, end) = arc(
        mid,
        [angle.sin(), 0., angle.cos()],
        [0., -1., 0.],
        angle,
        14.,
    );
    let down_start = [b[0] + 14., b[1], b[2] + 14.];
    let angle = (1. - (down_start[2] - z) / 28.).acos();
    ensure!(angle.is_finite(), "math domain error");
    let rise_start = [down_start[0] + 28. * angle.sin(), b[1], z];
    let (rise_first, mid) = arc(rise_start, [-1., 0., 0.], [0., 1., 0.], angle, 14.);
    let (rise_second, _) = arc(
        mid,
        [-angle.cos(), 0., angle.sin()],
        [0., -1., 0.],
        angle,
        14.,
    );
    let (down, _) = arc(down_start, [-1., 0., 0.], [0., -1., 0.], PI / 2., 14.);
    let prefix = vec![line(a, lift), offset_first, offset_second];
    let points = vec![
        [end[0], a[1], z],
        [-22.35, 214., z],
        [-22.35, 138., z],
        [b[0] + 33.65, 138., z],
        [b[0] + 33.65, b[1], z],
        rise_start,
    ];
    let mut full = vec![xyz(prefix.last().unwrap()["points_mm"]
        .as_array()
        .unwrap()
        .last()
        .unwrap())?];
    full.extend(points);
    let mut unresolved = Vec::new();
    let route = (|| -> Result<Value> {
        let mut segments = prefix;
        segments.extend(rounded(&full, 14.)?);
        segments.extend([rise_first, rise_second, down]);
        segments.push(line(b, sub(b, mul(ub, 12.7))));
        let points = sample(&segments)?;
        Ok(
            json!({"points_mm":points,"centerline_mm":points,"segments":segments,"od_mm":6.35,"id_mm":4.24,
            "radius_mm":14.,"minimum_radius_mm":14.,"spool":"black","from":"foam-assembly.reservoir-b",
            "frm":"foam-assembly.reservoir-b","to":"valve-v-h.inlet","owners":["foam-assembly","valve-v-h"],
            "status":"selected_native_layout","note":"B draw completes its westward offset aft of the drain cradle, then enters V-H from the fore corridor"}),
        )
    })();
    match route {
        Ok(row) => out.push(("fluid-26".to_owned(), row)),
        Err(error) => unresolved.push(json!({"id":"fluid-26","reason":error.to_string()})),
    }
    // The fill path is authored as exact native segments; resolving both ports
    // retains the same named-interface contract as the other continuations.
    let _ = station(stations, "reservoir-b-fill-turn", "socket")?;
    let _ = station(stations, "foam-assembly", "reservoir-b-fill")?;
    let fill = &spec["reservoir_b_fill_external"];
    let segments = fill["segments"]
        .as_array()
        .context("B fill native segments")?;
    let points = sample(segments)?;
    let bent = segments.iter().any(|s| s["kind"] != "line");
    let radius = if bent {
        fill["minimum_radius_mm"].clone()
    } else {
        Value::Null
    };
    out.push(("fluid-24".to_owned(),json!({"points_mm":points,"centerline_mm":points,"segments":segments,
        "od_mm":6.35,"id_mm":4.24,"radius_mm":radius,"minimum_radius_mm":radius,"spool":"black",
        "from":"reservoir-b-fill-turn.socket","frm":"reservoir-b-fill-turn.socket","to":"foam-assembly.reservoir-b-fill",
        "owners":["reservoir-b-fill-turn","foam-assembly"],"status":"selected_native_layout",
        "note":"B fill follows two exposed circular arcs to the fore cap entry"})));
    let _ = ua;
    Ok(json!({"routes":out,"unresolved":unresolved}))
}
