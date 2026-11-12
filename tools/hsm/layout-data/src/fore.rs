use crate::tube::Unrouted;
use crate::*;

/// The two bodies a fore tube joins.
fn owners(name: &str) -> Option<[&'static str; 2]> {
    match name {
        "drain-vb-east-link" => Some(["drain-outlet-stem", "vb-inlet-turn"]),
        "drain-vb-inlet-link" => Some(["vb-inlet-turn", "valve-v-b"]),
        "vb-yb-cross" => Some(["vb-outlet-stem", "vb-outlet-return"]),
        "vb-yb-link" => Some(["vb-outlet-return", "yb-stem-elbow"]),
        _ => None,
    }
}

/// Short warm-side tubes and the socket insertions authored in the layout. A tube that cannot
/// be laid out is left out of them and listed beside them.
pub fn routes(spec: &Value) -> Result<(std::collections::BTreeMap<String, Tube>, Vec<Unrouted>)> {
    let fore = &spec["fore_routes"];
    let mut result = std::collections::BTreeMap::new();
    let mut unrouted = Vec::new();
    for (name, raw) in fore["tubes"].as_object().context("fore tubes")? {
        if name.starts_with("soda-")
            || matches!(name.as_str(), "va-fore-feed" | "ya-concealed-link")
        {
            continue;
        }
        let id = format!("above-core-{name}");
        match tube(fore, name, raw, &id) {
            Ok(tube) => {
                result.insert(id, tube);
            }
            Err(error) => {
                let [from, to] = owners(name).unwrap_or(["", ""]);
                unrouted.push(Unrouted::of(&id, from, to, &error));
            }
        }
    }
    Ok((result, unrouted))
}

/// The fore tube `name`, named `id` among the machine's tubes, through its authored points.
fn tube(fore: &Value, name: &str, raw: &Value, id: &str) -> Result<Tube> {
    let mut points = points3(raw)?;
    let mut segments = match &fore["native_segments"][name] {
        authored @ Value::Array(_) => Some(crate::segments(authored)?),
        _ => None,
    };
    if segments.is_none() && name == "drain-vb-east-link" {
        let control = fore
            .get("vb_drain_control_mm")
            .unwrap_or(&fore["b_plumbing"]["inlet_control_mm"]);
        if fore["b_plumbing"]["inlet_minimum_radius_mm"].is_null() {
            points = vec![points[0], *points.last().context("fore path end")?];
            segments = Some(vec![line(points[0], points[1])]);
        } else {
            let c = points3(control)?;
            segments = Some(vec![
                line(points[0], c[0]),
                bezier(&c),
                line(*c.last().unwrap(), *points.last().unwrap()),
            ]);
        }
    } else if segments.is_none() && name == "vb-yb-link" {
        let control = fore
            .get("vb_return_control_mm")
            .unwrap_or(&fore["b_plumbing"]["return_control_mm"]);
        let c = points3(control)?;
        let crown = fore["b_plumbing"]["return_crown_mm"].as_f64().unwrap_or(0.);
        let mut s = vec![line(points[0], c[0])];
        if crown != 0. {
            s.extend(crowned_beziers(&c, crown, 16)?);
        } else {
            s.push(bezier(&c));
        }
        s.push(line(*c.last().unwrap(), *points.last().unwrap()));
        segments = Some(s);
    }
    let segments = segments
        .filter(|s| !s.is_empty())
        .unwrap_or_else(|| points.windows(2).map(|w| line(w[0], w[1])).collect());
    let radius = match name {
        "drain-vb-east-link" => fore
            .get("vb_drain_minimum_radius_mm")
            .filter(|v| !v.is_null())
            .unwrap_or(&fore["b_plumbing"]["inlet_minimum_radius_mm"])
            .as_f64(),
        "vb-yb-link" => fore["vb_return_minimum_radius_mm"].as_f64(),
        _ => None,
    };
    let owners = owners(name).with_context(|| format!("unknown fore tube owner {name}"))?;
    let spool = if id.contains("gas-") {
        "red"
    } else if id.contains("drain-vb") || id.contains("vb-yb") {
        "black"
    } else {
        "white"
    };
    Ok(Tube {
        owners: Some(owners.map(str::to_owned).to_vec()),
        status: Some("complete_between_named_interfaces".to_owned()),
        basis: Some("Nominal socket insertion".to_owned()),
        minimum_radius_mm: Some(radius),
        ..Tube::of(segments, 6.35, 4.24, spool).through(points)
    })
}
