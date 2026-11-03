//! Scalar route measurements used by the machine checks.
use super::*;
type Poly = Vec<f64>;
fn add(a: &[f64], b: &[f64]) -> Poly {
    let mut c = vec![0.; a.len().max(b.len())];
    for (i, &v) in a.iter().enumerate() {
        c[i] += v;
    }
    for (i, &v) in b.iter().enumerate() {
        c[i] += v;
    }
    c
}
fn scale(a: &[f64], n: f64) -> Poly {
    a.iter().map(|x| x * n).collect()
}
fn mul(a: &[f64], b: &[f64]) -> Poly {
    let mut c = vec![0.; a.len() + b.len() - 1];
    for (i, &u) in a.iter().enumerate() {
        for (j, &v) in b.iter().enumerate() {
            c[i + j] += u * v;
        }
    }
    c
}
fn deriv(a: &[f64]) -> Poly {
    if a.len() < 2 {
        return vec![0.];
    }
    a.iter()
        .enumerate()
        .skip(1)
        .map(|(i, x)| x * i as f64)
        .collect()
}
fn eval(p: &[f64], t: f64) -> f64 {
    p.iter().rev().fold(0., |v, c| v * t + c)
}
fn pow(a: &[f64], n: usize) -> Poly {
    (0..n).fold(vec![1.], |v, _| mul(&v, a))
}
fn choose(n: usize, k: usize) -> f64 {
    (0..k.min(n - k)).fold(1., |v, i| v * (n - i) as f64 / (i + 1) as f64)
}
fn roots(p: &[f64]) -> Vec<f64> {
    let mut p = p.to_vec();
    while p.len() > 1 && p.last() == Some(&0.) {
        p.pop();
    }
    if p.len() < 2 {
        return vec![];
    }
    if p.len() == 2 {
        let x = -p[0] / p[1];
        return if (0. ..=1.).contains(&x) {
            vec![x]
        } else {
            vec![]
        };
    }
    let mut stations = vec![0.];
    stations.extend(roots(&deriv(&p)));
    stations.push(1.);
    stations.sort_by(f64::total_cmp);
    stations.dedup_by(|a, b| (*a - *b).abs() < 1e-12);
    let norm = p.iter().map(|x| x.abs()).sum::<f64>().max(1.);
    let mut out = Vec::new();
    for &s in &stations {
        if eval(&p, s).abs() < 1e-12 * norm {
            out.push(s);
        }
    }
    for w in stations.windows(2) {
        let (mut lo, mut hi) = (w[0], w[1]);
        let sign = eval(&p, lo);
        if sign * eval(&p, hi) >= 0. {
            continue;
        }
        for _ in 0..64 {
            let mid = (lo + hi) / 2.;
            if eval(&p, mid) * sign > 0. {
                lo = mid;
            } else {
                hi = mid;
            }
        }
        out.push((lo + hi) / 2.);
    }
    out.sort_by(f64::total_cmp);
    out.dedup_by(|a, b| (*a - *b).abs() < 1e-9);
    out
}
fn bezier_derivatives(segment: &Value) -> Result<[Poly; 3]> {
    let q = array(&segment["control_points_mm"]);
    ensure!(q.len() >= 2, "Bezier needs two 3D control points");
    let degree = q.len() - 1;
    let mut p: [Poly; 3] = [vec![0.], vec![0.], vec![0.]];
    for (i, v) in q.iter().enumerate() {
        let v = vector(v)?;
        let b = scale(
            &mul(&pow(&[0., 1.], i), &pow(&[1., -1.], degree - i)),
            choose(degree, i),
        );
        for k in 0..3 {
            p[k] = add(&p[k], &scale(&b, v[k]));
        }
    }
    Ok(p.map(|p| deriv(&p)))
}
pub fn centerline_radii(segments: &Value) -> Result<Vec<f64>> {
    let mut out = Vec::new();
    for s in array(segments) {
        match s["kind"].as_str().unwrap_or("") {
            "line" => {}
            "arc" => {
                let ps = array(&s["points_mm"])
                    .iter()
                    .map(vector)
                    .collect::<Result<Vec<_>>>()?;
                ensure!(ps.len() == 3, "arc needs three points");
                let (a, b, c) = (ps[0], ps[1], ps[2]);
                out.push(
                    (a - b).norm() * (b - c).norm() * (c - a).norm()
                        / (2. * (b - a).cross(c - a).norm()),
                );
            }
            _ => {
                let v = bezier_derivatives(s)?;
                let a = v.clone().map(|p| deriv(&p));
                let c = [
                    add(&mul(&v[1], &a[2]), &scale(&mul(&v[2], &a[1]), -1.)),
                    add(&mul(&v[2], &a[0]), &scale(&mul(&v[0], &a[2]), -1.)),
                    add(&mul(&v[0], &a[1]), &scale(&mul(&v[1], &a[0]), -1.)),
                ];
                let speed = v.iter().fold(vec![0.], |p, v| add(&p, &mul(v, v)));
                let cross = c.iter().fold(vec![0.], |p, v| add(&p, &mul(v, v)));
                let stationary = add(
                    &mul(&deriv(&cross), &speed),
                    &scale(&mul(&cross, &deriv(&speed)), -3.),
                );
                let mut candidates = vec![0., 1.];
                candidates.extend(roots(&stationary));
                let min = candidates
                    .iter()
                    .filter_map(|&t| {
                        let v = eval(&speed, t);
                        let c = eval(&cross, t);
                        if v <= 1e-16 {
                            Some(0.)
                        } else if c > 1e-16 {
                            Some((v.max(0.).powi(3) / c).sqrt())
                        } else {
                            None
                        }
                    })
                    .min_by(f64::total_cmp);
                if let Some(min) = min {
                    out.push(min);
                }
            }
        }
    }
    for v in &mut out {
        *v = round(*v, 7);
    }
    out.sort_by(f64::total_cmp);
    out.dedup();
    Ok(out)
}
pub fn grade(r: f64) -> &'static str {
    if r >= 1.5 {
        "A"
    } else if r >= 1. {
        "B"
    } else if r >= 0.75 {
        "C"
    } else if r >= 0.5 {
        "D"
    } else {
        "F"
    }
}
pub fn grade_index(g: &Value) -> usize {
    match g.as_str() {
        Some("A") => 0,
        Some("B") => 1,
        Some("C") => 2,
        Some("D") => 3,
        Some("F") => 4,
        _ => 0,
    }
}
pub fn points(r: &Value) -> Result<Vec<V3>> {
    array(&r["pts"]).iter().map(vector).collect()
}
pub fn radius(r: &Value, i: usize) -> f64 {
    if r["radii"].is_array() {
        num(&r["radii"][i])
    } else {
        num(&r["radii"][i.to_string()])
    }
}
pub fn length(r: &Value) -> Result<f64> {
    if let Some(n) = r["length"].as_f64() {
        return Ok(n);
    }
    let p = points(r)?;
    let mut n = p.windows(2).map(|w| (w[1] - w[0]).norm()).sum::<f64>();
    for b in array(&r["bends"]) {
        let radius = radius(r, b[0].as_u64().unwrap_or(0) as usize);
        let turn = num(&b[1]).to_radians();
        n -= 2. * radius * (turn / 2.).tan() - radius * turn;
    }
    Ok(n)
}
pub fn need(r: &Value) -> Result<Value> {
    let p = points(r)?;
    ensure!(!p.is_empty(), "a run needs endpoints");
    let (a, b) = (p[0], p[p.len() - 1]);
    let span = (a - b).norm();
    let path = length(r)?;
    Ok(
        json!({"ends":[a.to_array().map(|v|round(v,2)),b.to_array().map(|v|round(v,2))],"axis":{"x":round((a.x-b.x).abs(),2),"y":round((a.y-b.y).abs(),2),"z":round((a.z-b.z).abs(),2)},"span":round(span,2),"path":round(path,2),"detour":if span<1e-9{Value::Null}else{json!(round(path/span,3))}}),
    )
}
pub fn need_clause(n: &Value) -> String {
    if n["detour"].is_null() {
        String::new()
    } else {
        format!(
            " — {:.2}× its need: {:.0} mm of path for ends {:.0} mm apart",
            num(&n["detour"]),
            num(&n["path"]),
            num(&n["span"])
        )
    }
}
pub fn bends(runs: &Value, specs: &Value) -> Result<Vec<Value>> {
    let mut out = Vec::new();
    for r in array(runs) {
        let id = string(&r["id"]);
        let kind = string(&r["kind"]);
        let od = num(&r["diam"]);
        let (stock, floor) = if kind == "refrigerant" && (od - 6.35).abs() < 0.05 {
            ("1/4\" soft ACR copper", 12.7)
        } else if kind == "fluid" && (od - 4.).abs() < 0.05 {
            ("4 mm LLDPE", 25.)
        } else if ["fluid", "water", "co2"].contains(&kind.as_str()) && (od - 6.35).abs() < 0.05 {
            ("1/4\" LLDPE", 14.)
        } else {
            bail!("no stock declared for {kind} OD {od}");
        };
        let spec = &specs[&id];
        let mut n = need(r)?;
        if spec.is_object() {
            let curved = array(&spec["segments"])
                .iter()
                .filter(|s| s["kind"] != "line")
                .collect::<Vec<_>>();
            let radi = spec["minimum_radius_mm"].as_f64();
            let ratio = radi.map(|r| r / floor);
            let corners=curved.iter().enumerate().map(|(i,s)|{let bound=s["radius_mm"].as_f64().or(radi);let turn=s["angle_rad"].as_f64().map(|v|v.abs().to_degrees());
                json!({"at":i,"turn":turn,"radius":bound,"ratio":bound.map(|v|round(v/floor,4)),"grade":bound.map(|v|grade(v/floor)),"legs":[]})}).collect::<Vec<_>>();
            let len = spec["length"]
                .as_f64()
                .or_else(|| spec["length_mm"].as_f64())
                .unwrap_or(length(r)?);
            n["path"] = json!(round(len, 2));
            n["detour"] = if num(&n["span"]) < 1e-9 {
                Value::Null
            } else {
                json!(round(len / num(&n["span"]), 3))
            };
            out.push(json!({"id":id,"kind":kind,"frm":r["frm"],"to":r["to"],"stock":stock,"od":od,"length":round(len,2),"radius":radi,"cap":radi,"minBend":floor,"ratio":ratio,"grade":if curved.is_empty(){None}else{ratio.map(grade)},"atSpec":corners.iter().filter(|c|c["radius"].as_f64().is_some_and(|v|v>=floor-1e-9)).count(),"bends":curved.len(),"worstTurn":corners.iter().filter_map(|c|c["turn"].as_f64()).max_by(f64::total_cmp),"seat":null,"reach":null,"reachRatio":null,"reachGrade":null,"binding":null,"need":n,"corners":corners}));
            continue;
        }
        let p = points(r)?;
        let mut caps = Vec::new();
        let tang = array(&r["bends"])
            .iter()
            .map(|b| {
                (
                    b[0].as_u64().unwrap() as usize,
                    (num(&b[1]).to_radians() / 2.).tan(),
                )
            })
            .collect::<BTreeMap<_, _>>();
        for i in 0..p.len().saturating_sub(1) {
            let demand = tang.get(&i).unwrap_or(&0.) + tang.get(&(i + 1)).unwrap_or(&0.);
            if demand <= 1e-12 {
                continue;
            }
            let len = (p[i + 1] - p[i]).norm();
            caps.push((len / demand, i, len, demand, i != 0 && i != p.len() - 2));
        }
        let seat = caps.iter().map(|c| c.0).min_by(f64::total_cmp);
        let binding = caps
            .iter()
            .filter(|c| c.4)
            .min_by(|a, b| a.0.total_cmp(&b.0));
        let hold = binding.map(|c| c.0);
        let corners=array(&r["bends"]).iter().map(|b|{let i=b[0].as_u64().unwrap()as usize;let radius=radius(r,i);json!({"at":i,"turn":round(num(&b[1]),1),"radius":round(radius,3),"ratio":round(radius/floor,4),"grade":grade(radius/floor),"legs":[round(num(&b[2]),2),round(num(&b[3]),2)]})}).collect::<Vec<_>>();
        let tight = corners
            .iter()
            .map(|v| num(&v["radius"]))
            .min_by(f64::total_cmp)
            .unwrap_or(num(&r["bend"]));
        let stock_floor = floor;
        let floor = r["min_bend"].as_f64().filter(|x| *x != 0.).unwrap_or(floor);
        let ratio = tight / floor;
        out.push(json!({"id":id,"kind":kind,"frm":r["frm"],"to":r["to"],"stock":stock,"od":od,"length":round(length(r)?,2),"radius":round(tight,3),"cap":round(num(&r["bend"]),3),"minBend":floor,"ratio":round(ratio,4),"grade":if corners.is_empty(){None}else{Some(grade(ratio))},"atSpec":corners.iter().filter(|c|num(&c["radius"])>=floor-1e-9).count(),"bends":corners.len(),"worstTurn":corners.iter().map(|v|num(&v["turn"])).max_by(f64::total_cmp),"seat":seat.map(|v|round(v,3)),"reach":hold.map(|v|round(v,3)),"reachRatio":hold.map(|v|round(v/stock_floor,4)),"reachGrade":if corners.is_empty(){None}else{Some(hold.map(|h|grade(h/stock_floor)).unwrap_or("A"))},"binding":binding.map(|c|json!({"leg":c.1,"length":round(c.2,3),"demand":round(c.3,4),"from":p[c.1].to_array().map(|v|round(v,2)),"to":p[c.1+1].to_array().map(|v|round(v,2))})),"need":n,"corners":corners}));
    }
    out.sort_by(|a, b| {
        let key = |v: &Value| {
            (
                v["grade"].is_null(),
                std::cmp::Reverse(grade_index(&v["grade"])),
                std::cmp::Reverse(grade_index(&v["reachGrade"])),
            )
        };
        key(a).cmp(&key(b)).then_with(|| {
            a["reachRatio"]
                .as_f64()
                .unwrap_or(1e9)
                .total_cmp(&b["reachRatio"].as_f64().unwrap_or(1e9))
        })
    });
    Ok(out)
}
pub fn on_leg(p: V3, a: V3, b: V3, tol: f64) -> bool {
    let d = (a - b).norm();
    d >= tol && ((a - p).norm() + (p - b).norm() - d).abs() < tol
}
fn native_cuts(r: &Value, stations: &Value, specs: &Value) -> Result<Option<Vec<f64>>> {
    let id = string(&r["id"]);
    if id != "fluid-14" && id != "fluid-16" {
        return Ok(None);
    }
    let spec = &specs[&id];
    let expected = spec.get("points_mm").or_else(|| spec.get("centerline_mm"));
    let Some(expected) = expected else {
        return Ok(None);
    };
    let actual = points(r)?;
    let expected = array(expected)
        .iter()
        .map(vector)
        .collect::<Result<Vec<_>>>()?;
    if actual.len() != expected.len()
        || actual
            .iter()
            .zip(&expected)
            .any(|(a, b)| (*a - *b).norm() > 1e-6)
    {
        return Ok(None);
    }
    let mut cuts = vec![0.];
    let mut distance = 0.;
    for s in array(&spec["segments"]) {
        if s["kind"] == "line" {
            let p = vector(&s["points_mm"][0])?;
            let q = vector(&s["points_mm"][1])?;
            for station in array(stations) {
                let point = vector(station.get("point").unwrap_or(&station[0]))?;
                if on_leg(point, p, q, 1e-6) {
                    cuts.push(distance + (p - point).norm());
                }
            }
            distance += (p - q).norm();
        } else {
            let center = vector(&s["center_mm"])?;
            let axis = vector(s.get("axis").unwrap_or(&s["axis_world"]))?;
            let radius = num(&s["radius_mm"]);
            let angle = num(&s["angle_rad"]);
            let start = vector(&s["points_mm"][0])? - center;
            for station in array(stations) {
                let point = vector(station.get("point").unwrap_or(&station[0]))?;
                let radial = point - center;
                if (radial.norm() - radius).abs() > 1e-6 || radial.dot(axis).abs() > 1e-6 {
                    continue;
                }
                let mut turn =
                    (angle.signum() * axis.dot(start.cross(radial))).atan2(start.dot(radial));
                if turn < -1e-6 / radius {
                    turn += 2. * std::f64::consts::PI;
                }
                if turn <= angle.abs() + 1e-6 / radius {
                    cuts.push(distance + radius * turn.max(0.));
                }
            }
            distance += radius * angle.abs();
        }
    }
    cuts.push(distance);
    cuts.sort_by(f64::total_cmp);
    cuts.dedup();
    Ok(Some(cuts))
}
pub fn unsupported(
    runs: &Value,
    stations: &Value,
    developed: &Value,
    specs: &Value,
) -> Result<BTreeMap<String, f64>> {
    let mut out = BTreeMap::new();
    for r in array(runs) {
        let id = string(&r["id"]);
        let computed = native_cuts(r, stations, specs)?;
        let provided = array(&developed[&id]).iter().map(num).collect::<Vec<_>>();
        let native = computed.as_deref().unwrap_or(&provided);
        if !native.is_empty() {
            out.insert(
                id,
                native.windows(2).map(|w| w[1] - w[0]).fold(0., f64::max),
            );
            continue;
        }
        let p = points(r)?;
        let mut cuts = vec![0.];
        let mut s = 0.;
        let short = array(&r["bends"])
            .iter()
            .map(|b| {
                let i = b[0].as_u64().unwrap() as usize;
                let rr = radius(r, i);
                let t = num(&b[1]).to_radians();
                (i, 2. * rr * (t / 2.).tan() - rr * t)
            })
            .collect::<BTreeMap<_, _>>();
        for (i, w) in p.windows(2).enumerate() {
            s -= short.get(&i).unwrap_or(&0.);
            for station in array(stations) {
                let mid = vector(station.get("point").unwrap_or(&station[0]))?;
                if on_leg(mid, w[0], w[1], 1e-6) {
                    cuts.push(s + (w[0] - mid).norm());
                }
            }
            s += (w[1] - w[0]).norm();
        }
        cuts.push(s);
        cuts.sort_by(f64::total_cmp);
        out.insert(id, cuts.windows(2).map(|w| w[1] - w[0]).fold(0., f64::max));
    }
    Ok(out)
}
