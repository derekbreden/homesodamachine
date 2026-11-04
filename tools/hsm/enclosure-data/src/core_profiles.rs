//! Display-roof curves and numeric loft sections.
use super::{array, f, text};
use anyhow::{Result, anyhow};
use serde_json::{Value, json};

fn outer(v: &Value) -> Result<[f64; 6]> {
    let rows = array(v, "outer")?;
    if rows.len() != 6 {
        return Err(anyhow!("outer has six bounds"));
    }
    let mut out = [0.; 6];
    for (x, y) in out.iter_mut().zip(rows) {
        *x = y
            .as_f64()
            .ok_or_else(|| anyhow!("outer bound is numeric"))?;
    }
    Ok(out)
}

fn profile(v: &Value) -> Result<Value> {
    let o = outer(v)?;
    let d = &v["parameters"];
    let (yf, zt) = (o[2], o[5]);
    let angle = f(d, "ANGLE")?.to_radians();
    let (rb, rt, flat) = (f(d, "FRONT_RADIUS")?, f(d, "TOP_RADIUS")?, f(d, "FLAT")?);
    let zb = zt - rb * angle.cos() - flat * angle.sin() - rt * (1. - angle.cos());
    let start = [yf + rb * (1. - angle.sin()), zb + rb * angle.cos()];
    let end = [start[0] + flat * angle.cos(), start[1] + flat * angle.sin()];
    let roof = [end[0] + rt * angle.sin(), zt];
    let amid = (180. - (90. - f(d, "ANGLE")?) / 2.).to_radians();
    Ok(
        json!({"foot":[yf,zb],"front_mid":[yf+rb+rb*amid.cos(),zb+rb*amid.sin()],
        "start":start,"end":end,"top_mid":[roof[0]-rt*(angle/2.).sin(),zt-rt+rt*(angle/2.).cos()],
        "roof":roof,"origin":[0.,(start[0]+end[0])/2.,(start[1]+end[1])/2.],
        "normal":[0.,-angle.sin(),angle.cos()]}),
    )
}

pub fn transition(radius: f64, slope: f64) -> [f64; 2] {
    let height = radius - radius * slope / (1. + slope * slope).sqrt();
    let inset = radius - radius / (1. + slope * slope).sqrt();
    [height, inset + slope * height]
}

fn roof_fill(v: &Value) -> Result<Value> {
    let o = outer(v)?;
    let d = &v["parameters"];
    let p = profile(v)?;
    let (radius, rt) = (f(d, "SIDE_RADIUS")?, f(d, "TOP_RADIUS")?);
    let slope = f(v, "outward_per_height")?;
    let angle = f(d, "ANGLE")?.to_radians();
    let (sa, ca) = (angle.sin(), angle.cos());
    let cy = p["roof"][0].as_f64().unwrap();
    let cz = o[5] - rt;
    let aft = cy + 2. * radius;
    let [height, foot] = transition(radius, slope);
    let tangent = foot - slope * height;
    let mut depths = (0..=90)
        .step_by(2)
        .map(|a| radius * (1. - (a as f64).to_radians().sin()))
        .filter(|d| *d >= tangent)
        .chain([tangent, foot, radius])
        .collect::<Vec<_>>();
    depths.sort_by(f64::total_cmp);
    depths.dedup();
    let mut fills = Vec::new();
    for (edge, inward) in [(o[0], 1.), (o[1], -1.)] {
        let mut sections = Vec::new();
        for &depth in &depths {
            let mut side = radius - (radius.powi(2) - (radius - depth).powi(2)).max(0.).sqrt();
            let roof = side.min(((foot - depth) / slope).max(0.));
            side += 0.01;
            let (k, b) = (rt - side, rt - roof);
            let a = ((k * k - b * b * ca * ca) / (sa * sa)).sqrt();
            let top = [cy - a * a * sa / k, cz + b * b * ca / k];
            let theta = (a * sa).atan2(b * ca).to_degrees();
            let ey = p["end"][0].as_f64().unwrap();
            let ez = p["end"][1].as_f64().unwrap();
            let start = [ey + sa * side - ca, ez - ca * side - sa];
            let inner = rt - side - 0.25;
            let inner_end = [cy - inner * sa, cz + inner * ca];
            sections.push(json!({"x":edge+inward*depth,"centre":[cy,cz],
                "ellipse":[b,a,theta],"inner_radius":inner,"start":start,"top_tangent":top,
                "inner_end":inner_end,"inner_mid":[cy-inner*(angle/2.).sin(),cz+inner*(angle/2.).cos()],
                "inner_start":[inner_end[0]-ca,inner_end[1]-sa],
                "upper_roof":[cy,cz+b],"lower_roof":[cy,cz+inner],
                "upper_aft":[aft,cz+b],"lower_aft":[aft,cz+inner]}));
        }
        fills.push(sections);
    }
    Ok(json!(fills))
}

pub fn dispatch(v: &Value) -> Result<Value> {
    match text(v, "op")? {
        "swept-defaults" => Ok(
            json!({"ANGLE":30.,"FLAT":87.,"FRONT_RADIUS":v["dimensions"]["show_corner_r"],
            "TOP_RADIUS":3.*f(&v["dimensions"],"show_edge_r")?,
            "SIDE_RADIUS":v["dimensions"]["show_edge_r"],"FUNNEL_SEAT":6.}),
        ),
        "swept-profile" => profile(v),
        "swept-roof-fill" => roof_fill(v),
        "swept-transition" => Ok(json!(transition(
            f(v, "radius")?,
            f(v, "outward_per_height")?
        ))),
        "swept-structure" => {
            let p = &v["parameters"];
            let slope = f(v, "outward_per_height")?;
            let [height, foot] = transition(f(p, "SIDE_RADIUS")?, slope);
            Ok(
                json!({"outer":v["outer"],"profile":profile(v)?,"standing_radius":p["FRONT_RADIUS"],
                "side_radius":p["SIDE_RADIUS"],"angle":p["ANGLE"],"roof_fill_sections":roof_fill(v)?,
                "roof_transition":{"height":height,"foot":foot,"outward_per_height":slope}}),
            )
        }
        _ => Err(anyhow!("unknown swept-roof data operation")),
    }
}
