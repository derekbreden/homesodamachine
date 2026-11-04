//! Scalar route measurements used by the machine checks.
use anyhow::{Context,Result,ensure};
use serde_json::Value;
use hsm_layout_data::{norm,sub,cross,xyz as vector};
fn array(v:&Value)->&[Value]{v.as_array().map(Vec::as_slice).unwrap_or(&[])}
fn round(x:f64,places:i32)->f64{let k=10f64.powi(places);(x*k).round_ties_even()/k}
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
                    norm(sub(a,b))*norm(sub(b,c))*norm(sub(c,a))/(2.*norm(cross(sub(b,a),sub(c,a)))),
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
