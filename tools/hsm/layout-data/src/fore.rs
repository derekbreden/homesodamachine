use crate::*;

/// Short warm-side tubes and the socket insertions authored in the layout.
pub fn routes(spec: &Value, rear: &Value) -> Result<Value> {
    let fore = &spec["fore_routes"];
    let mut result = serde_json::Map::new();
    for (name, raw) in fore["tubes"].as_object().context("fore tubes")? {
        if name.starts_with("soda-")
            || matches!(name.as_str(), "va-fore-feed" | "ya-concealed-link")
        {
            continue;
        }
        let mut points = points3(raw)?;
        let mut segments = fore["native_segments"][name].as_array().cloned();
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
        let radius = match name.as_str() {
            "drain-vb-east-link" => fore
                .get("vb_drain_minimum_radius_mm")
                .filter(|v| !v.is_null())
                .unwrap_or(&fore["b_plumbing"]["inlet_minimum_radius_mm"])
                .clone(),
            "vb-yb-link" => fore["vb_return_minimum_radius_mm"].clone(),
            _ => Value::Null,
        };
        let owners = match name.as_str() {
            "drain-vb-east-link" => ["drain-outlet-stem", "vb-inlet-turn"],
            "drain-vb-inlet-link" => ["vb-inlet-turn", "valve-v-b"],
            "vb-yb-cross" => ["vb-outlet-stem", "vb-outlet-return"],
            "vb-yb-link" => ["vb-outlet-return", "yb-stem-elbow"],
            _ => bail!("unknown fore tube owner {name}"),
        };
        let id = format!("above-core-{name}");
        let spool = if id.contains("gas-") {
            "red"
        } else if id.contains("drain-vb") || id.contains("vb-yb") {
            "black"
        } else {
            "white"
        };
        result.insert(id,json!({"points_mm":points,"centerline_mm":points,"od_mm":6.35,"id_mm":4.24,
            "owners":owners,"status":"complete_between_named_interfaces","basis":"Nominal socket insertion",
            "segments":segments,"spool":spool,"minimum_radius_mm":radius}));
    }
    if let Some(rows) = rear.as_object() {
        result.extend(rows.clone());
    }
    Ok(Value::Object(result))
}
