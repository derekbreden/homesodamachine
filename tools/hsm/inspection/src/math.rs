//! Small vector operations retain the coordinates a manual inspection measures.
pub type V3 = [f64; 3];
pub fn add(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] + b[i])
}
pub fn sub(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] - b[i])
}
pub fn scale(a: V3, n: f64) -> V3 {
    a.map(|v| v * n)
}
pub fn dot(a: V3, b: V3) -> f64 {
    (0..3).map(|i| a[i] * b[i]).sum()
}
pub fn cross(a: V3, b: V3) -> V3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn length(a: V3) -> f64 {
    dot(a, a).sqrt()
}
pub fn unit(a: V3) -> V3 {
    let n = length(a);
    if n > 0. { scale(a, 1. / n) } else { [0.; 3] }
}

/// The closest point on a triangle includes its edges and vertices.
pub fn closest(p: V3, a: V3, b: V3, c: V3) -> V3 {
    let ab = sub(b, a);
    let ac = sub(c, a);
    let ap = sub(p, a);
    let d1 = dot(ab, ap);
    let d2 = dot(ac, ap);
    if d1 <= 0. && d2 <= 0. {
        return a;
    }
    let bp = sub(p, b);
    let d3 = dot(ab, bp);
    let d4 = dot(ac, bp);
    if d3 >= 0. && d4 <= d3 {
        return b;
    }
    let vc = d1 * d4 - d3 * d2;
    if vc <= 0. && d1 >= 0. && d3 <= 0. {
        return add(a, scale(ab, d1 / (d1 - d3)));
    }
    let cp = sub(p, c);
    let d5 = dot(ab, cp);
    let d6 = dot(ac, cp);
    if d6 >= 0. && d5 <= d6 {
        return c;
    }
    let vb = d5 * d2 - d1 * d6;
    if vb <= 0. && d2 >= 0. && d6 <= 0. {
        return add(a, scale(ac, d2 / (d2 - d6)));
    }
    let va = d3 * d6 - d5 * d4;
    if va <= 0. && (d4 - d3) >= 0. && (d5 - d6) >= 0. {
        return add(b, scale(sub(c, b), (d4 - d3) / ((d4 - d3) + (d5 - d6))));
    }
    let sum = va + vb + vc;
    if sum.abs() < 1e-30 {
        let segment = |x: V3, y: V3| {
            let v = sub(y, x);
            let n = dot(v, v);
            if n == 0. {
                x
            } else {
                add(x, scale(v, (dot(sub(p, x), v) / n).clamp(0., 1.)))
            }
        };
        return [segment(a, b), segment(b, c), segment(c, a)]
            .into_iter()
            .min_by(|x, y| length(sub(p, *x)).total_cmp(&length(sub(p, *y))))
            .unwrap();
    }
    add(a, add(scale(ab, vb / sum), scale(ac, vc / sum)))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn closest_is_on_the_facet() {
        assert!(
            length(sub(
                closest([0.2, 0.3, 2.], [0., 0., 0.], [1., 0., 0.], [0., 1., 0.]),
                [0.2, 0.3, 0.]
            )) < 1e-12
        );
        assert_eq!(
            closest([2., 0., 1.], [0., 0., 0.], [1., 0., 0.], [0., 1., 0.]),
            [1., 0., 0.]
        );
    }
}
