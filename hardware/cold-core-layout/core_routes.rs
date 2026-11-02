//! Tangent circular routes and the native stock-radius fitting ladder.
use anyhow::{Result, ensure};
use hsm_kernel::math::{acos, sin, tan};
use hsm_kernel::*;

fn drop_collinear(points: &[V3]) -> Vec<V3> {
    let mut kept = vec![points[0]];
    for &point in &points[1..] {
        if (point - kept[kept.len() - 1]).norm() < 1e-9 {
            continue;
        }
        if kept.len() >= 2 {
            let a = kept[kept.len() - 2];
            let b = kept[kept.len() - 1];
            if (b - a).unit().cross((point - b).unit()).norm() < 1e-9 {
                *kept.last_mut().unwrap() = point;
                continue;
            }
        }
        kept.push(point);
    }
    kept
}

pub fn corner_radii(points: &[V3], bend_radius: f64) -> Result<(Vec<V3>, Vec<f64>)> {
    ensure!(points.len() >= 2, "a route needs two points");
    let points = drop_collinear(points);
    ensure!(points.len() >= 2, "a route needs two distinct points");
    let n = points.len();
    let mut half = vec![0.; n];
    let mut radius = vec![0.; n];
    for i in 1..n - 1 {
        let u = (points[i - 1] - points[i]).unit();
        let w = (points[i + 1] - points[i]).unit();
        half[i] = acos(u.dot(w).clamp(-1., 1.)) / 2.;
        radius[i] = bend_radius;
    }
    for _ in 0..64 {
        let setback: Vec<f64> = (0..n)
            .map(|i| {
                if half[i] > 1e-9 {
                    radius[i] / tan(half[i])
                } else {
                    0.
                }
            })
            .collect();
        let mut worst = 1_f64;
        for i in 0..n - 1 {
            let leg = (points[i + 1] - points[i]).norm();
            let want = setback[i] + setback[i + 1];
            if want > leg {
                worst = worst.min(leg / want);
            }
        }
        if worst >= 1. - 1e-12 {
            break;
        }
        for radius in &mut radius[1..n - 1] {
            *radius *= worst * 0.999;
        }
    }
    Ok((points, radius))
}

pub fn route_path(points: &[V3], bend_radius: f64) -> Result<Path> {
    let (points, radius) = corner_radii(points, bend_radius)?;
    let mut tail = points[0];
    let mut path = Path::new(tail);
    for i in 1..points.len() - 1 {
        let u = (points[i - 1] - points[i]).unit();
        let w = (points[i + 1] - points[i]).unit();
        let half = acos(u.dot(w).clamp(-1., 1.)) / 2.;
        let setback = radius[i] / tan(half);
        let incoming = points[i] + u * setback;
        let outgoing = points[i] + w * setback;
        let centre = points[i] + (u.unit() + w.unit()).unit() * (radius[i] / sin(half));
        let mid = centre + (points[i] - centre).unit() * radius[i];
        if (incoming - tail).norm() > 1e-7 {
            path = path.line_to(incoming);
        }
        path = path.arc_through(mid, outgoing)?;
        tail = outgoing;
    }
    if (points[points.len() - 1] - tail).norm() > 1e-7 {
        path = path.line_to(points[points.len() - 1]);
    }
    Ok(path)
}

pub fn developed_length(points: &[V3], bend_radius: f64) -> Result<f64> {
    Ok(route_path(points, bend_radius)?
        .legs
        .iter()
        .map(|leg| match *leg {
            Leg::Line { a, b } => (b - a).norm(),
            Leg::Arc { a, c, turn, .. } => (a - c).norm() * turn.abs(),
            Leg::Curve { .. } => unreachable!("a circular route has no spline leg"),
        })
        .sum())
}

pub fn build_route(points: &[V3], bend_radius: f64, tube_radius: f64) -> Result<Solid> {
    let path = route_path(points, bend_radius)?;
    let tangent = match path.legs[0] {
        Leg::Line { a, b } => (b - a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(a - c).unit(),
        Leg::Curve { .. } => unreachable!("a circular route has no spline leg"),
    };
    let x = if tangent.x.abs() > 0.9 {
        v3(0., 1., 0.)
    } else {
        v3(1., 0., 0.)
    };
    let region =
        Profile::circle(v2(0., 0.), tube_radius).place(&Plane::new(points[0], x, tangent)?);
    // Leave room for the profile's radial facets inside the 0.005 mm surface rule.
    Solid::sweep_with_tolerance(&region, &path, 0.003)
}

pub fn fit_route(
    points: &[V3],
    stock_bend: f64,
    bend_floor: f64,
    ladder: &[f64],
    tube_radius: f64,
    touch_volume: f64,
    obstacles: &[Vec<&Solid>],
) -> Result<(f64, Solid)> {
    for &rung in ladder {
        let bend = stock_bend * rung;
        if bend < bend_floor {
            break;
        }
        let tube = build_route(points, bend, tube_radius)?;
        let mut fits = true;
        for obstacle in obstacles {
            let mut volume = 0.;
            for component in obstacle {
                volume += tube.shared_volume(component)?;
            }
            if volume > touch_volume {
                fits = false;
                break;
            }
        }
        if fits {
            return Ok((bend, tube));
        }
    }
    Ok((bend_floor, build_route(points, bend_floor, tube_radius)?))
}
