//! Cubics through points, as OCCT's `GeomAPI_Interpolate` fits them for CadQuery's
//! `Edge.makeSpline`.
//!
//! Each point stands at its chord-length parameter: the first at 0, each next one further on by
//! its distance from the last. Through four points or more the curve is the cubic spline knotted
//! at every point whose end slopes are those of the cubic through the first four points and of
//! the cubic through the last four (OCCT's `BuildTangents`); through three it is the one
//! parabola, and through two the line. Between two points with end tangents it is the cubic
//! leaving and arriving along them, each scaled until the absolute values of its coordinates sum
//! to those of the chord's slope, as `Load(t0, t1, Scale = true)` scales them.
//!
//! A sweep cuts a curve where its turn at its radius plus the profile's reach uses up the rule,
//! as it cuts an arc.
use crate::math::{V3, asin, atan2};
use crate::rule::{ANGULAR, LINEAR};
use anyhow::{Result, ensure};

/// A curve in Hermite form: its points, the parameter each stands at, and its slope at each.
#[derive(Clone, Debug, PartialEq)]
pub struct Spline {
    t: Vec<f64>,
    p: Vec<V3>,
    m: Vec<V3>,
}

/// The parameter step of the walk that measures a curve's turn.
const FINE: f64 = 0.02;

/// The most a bend of radius `r` may turn between two points of the rule.
fn step(r: f64) -> f64 {
    if r <= LINEAR { ANGULAR } else { ANGULAR.min(4.0 * asin((LINEAR / (2.0 * r)).sqrt())) }
}

/// The slope at `t[at]` of the cubic through the four points `p` at parameters `t`.
fn lagrange_slope(t: &[f64], p: &[V3], at: usize) -> V3 {
    let x = t[at];
    let mut slope = V3::ZERO;
    for j in 0..4 {
        let below: f64 = (0..4).filter(|&k| k != j).map(|k| t[j] - t[k]).product();
        let weight = if j == at {
            (0..4).filter(|&k| k != j).map(|k| 1.0 / (x - t[k])).sum::<f64>()
        } else {
            (0..4).filter(|&k| k != j && k != at).map(|k| x - t[k]).product::<f64>() / below
        };
        slope += p[j] * weight;
    }
    slope
}

/// Slopes of the cubic spline through `p` at parameters `t`, `h` apart with chord slopes `d`,
/// whose end slopes those of the cubics through its first four and last four points.
fn clamped(t: &[f64], p: &[V3], h: &[f64], d: &[V3]) -> Vec<V3> {
    let n = p.len();
    let mut m = vec![V3::ZERO; n];
    m[0] = lagrange_slope(&t[..4], &p[..4], 0);
    m[n - 1] = lagrange_slope(&t[n - 4..], &p[n - 4..], 3);
    let (mut b, mut c, mut r) = (vec![0.0; n], vec![0.0; n], vec![V3::ZERO; n]);
    for i in 1..n - 1 {
        b[i] = 2.0 * (h[i - 1] + h[i]);
        c[i] = h[i - 1];
        r[i] = (d[i - 1] * h[i] + d[i] * h[i - 1]) * 3.0;
    }
    r[1] = r[1] - m[0] * h[1];
    r[n - 2] = r[n - 2] - m[n - 1] * h[n - 3];
    for i in 2..n - 1 {
        let w = h[i] / b[i - 1];
        b[i] -= w * c[i - 1];
        r[i] = r[i] - r[i - 1] * w;
    }
    m[n - 2] = r[n - 2] / b[n - 2];
    for i in (1..n - 2).rev() {
        m[i] = (r[i] - m[i + 1] * c[i]) / b[i];
    }
    m
}

impl Spline {
    /// The curve through `points` at their chord-length parameters.
    pub fn through(points: &[V3]) -> Result<Spline> {
        let n = points.len();
        ensure!(n >= 2, "a spline through {n} point(s)");
        let mut t = vec![0.0];
        for w in points.windows(2) {
            let gap = (w[1] - w[0]).norm();
            ensure!(gap > 1e-9, "a spline through two points {gap:e} apart");
            t.push(t[t.len() - 1] + gap);
        }
        let h: Vec<f64> = t.windows(2).map(|w| w[1] - w[0]).collect();
        let d: Vec<V3> = (0..n - 1).map(|i| (points[i + 1] - points[i]) / h[i]).collect();
        let m = match n {
            2 => vec![d[0], d[0]],
            3 => {
                let bend = (d[1] - d[0]) / (h[0] + h[1]);
                vec![d[0] - bend * h[0], d[0] + bend * h[0], d[0] + bend * (h[0] + 2.0 * h[1])]
            }
            _ => clamped(&t, points, &h, &d),
        };
        Ok(Spline { t, p: points.to_vec(), m })
    }

    /// The cubic from `a` to `b` leaving along `ta` and arriving along `tb`.
    pub fn hermite(a: V3, b: V3, ta: V3, tb: V3) -> Result<Spline> {
        let gap = (b - a).norm();
        ensure!(gap > 1e-9, "a spline between two points {gap:e} apart");
        ensure!(ta.norm() > 1e-12 && tb.norm() > 1e-12, "a spline along a tangent of no length");
        let sum = |v: V3| v.x.abs() + v.y.abs() + v.z.abs();
        let chord = sum(b - a) / gap;
        Ok(Spline { t: vec![0.0, gap], p: vec![a, b], m: vec![ta * (chord / sum(ta)), tb * (chord / sum(tb))] })
    }

    pub fn start(&self) -> V3 {
        self.p[0]
    }

    pub fn end(&self) -> V3 {
        self.p[self.p.len() - 1]
    }

    /// The first and last parameters.
    pub fn range(&self) -> (f64, f64) {
        (self.t[0], self.t[self.t.len() - 1])
    }

    /// The span holding parameter `t` and the share `t` stands along it.
    fn span(&self, t: f64) -> (usize, f64) {
        let i = self.t.partition_point(|&x| x <= t).clamp(1, self.t.len() - 1) - 1;
        (i, (t - self.t[i]) / (self.t[i + 1] - self.t[i]))
    }

    /// The point at parameter `t`.
    pub fn point(&self, t: f64) -> V3 {
        let (i, s) = self.span(t);
        let h = self.t[i + 1] - self.t[i];
        let (s2, s3) = (s * s, s * s * s);
        self.p[i] * (2.0 * s3 - 3.0 * s2 + 1.0)
            + self.m[i] * ((s3 - 2.0 * s2 + s) * h)
            + self.p[i + 1] * (3.0 * s2 - 2.0 * s3)
            + self.m[i + 1] * ((s3 - s2) * h)
    }

    /// The curve's slope at parameter `t`.
    pub fn derivative(&self, t: f64) -> V3 {
        let (i, s) = self.span(t);
        let h = self.t[i + 1] - self.t[i];
        let s2 = s * s;
        (self.p[i + 1] - self.p[i]) * ((6.0 * s - 6.0 * s2) / h)
            + self.m[i] * (3.0 * s2 - 4.0 * s + 1.0)
            + self.m[i + 1] * (3.0 * s2 - 2.0 * s)
    }

    /// Points along the curve and its direction at each, cut so that no stretch between two of
    /// them turns further than an arc of its radius plus `reach` is cut into: the turn the rule
    /// allows, measured on a fine walk, shared out evenly.
    pub(crate) fn track(&self, reach: f64) -> (Vec<V3>, Vec<V3>) {
        let mut walk = vec![self.t[0]];
        for w in self.t.windows(2) {
            let n = ((w[1] - w[0]) / FINE).ceil().max(16.0) as usize;
            walk.extend((1..=n).map(|j| w[0] + (w[1] - w[0]) * j as f64 / n as f64));
        }
        let at: Vec<V3> = walk.iter().map(|&t| self.point(t)).collect();
        let dir: Vec<V3> = walk.iter().map(|&t| self.derivative(t).unit()).collect();
        let mut used = vec![0.0];
        for j in 0..walk.len() - 1 {
            let turn = atan2(dir[j].cross(dir[j + 1]).norm(), dir[j].dot(dir[j + 1]));
            let share = if turn > 0.0 { turn / step((at[j + 1] - at[j]).norm() / turn + reach) } else { 0.0 };
            used.push(used[j] + share);
        }
        let total = used[used.len() - 1];
        let n = ((total - 1e-9).ceil() as usize).max(1);
        let (mut p, mut d) = (vec![self.start()], vec![dir[0]]);
        let mut j = 0;
        for k in 1..n {
            let goal = total * k as f64 / n as f64;
            while used[j + 1] < goal {
                j += 1;
            }
            let t = walk[j] + (walk[j + 1] - walk[j]) * (goal - used[j]) / (used[j + 1] - used[j]);
            p.push(self.point(t));
            d.push(self.derivative(t).unit());
        }
        p.push(self.end());
        d.push(dir[dir.len() - 1]);
        (p, d)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::math::{sin, v3};

    #[test]
    fn the_curve_meets_every_point_at_its_parameter() {
        let pts: Vec<V3> = (0..9).map(|i| {
            let x = i as f64 * 0.37;
            v3(x, 0.5 * x * x * x - x, 2.0 + sin(x * 3.0))
        }).collect();
        let s = Spline::through(&pts).unwrap();
        for (q, &t) in pts.iter().zip(&s.t) {
            assert!((s.point(t) - *q).norm() < 1e-12);
        }
        let h = Spline::hermite(v3(1.0, 2.0, 3.0), v3(4.0, 2.0, -1.0), v3(0.0, 0.0, -2.0), v3(0.0, 0.0, -1.0)).unwrap();
        assert_eq!(h.range(), (0.0, 5.0));
        assert!((h.point(5.0) - v3(4.0, 2.0, -1.0)).norm() < 1e-12);
        assert!((h.derivative(0.0) - v3(0.0, 0.0, -1.4)).norm() < 1e-12);
    }

    #[test]
    fn a_straight_spline_is_cut_at_its_ends() {
        let s = Spline::through(&[v3(0.0, 0.0, 0.0), v3(0.0, 0.0, 1.0), v3(0.0, 0.0, 3.0), v3(0.0, 0.0, 7.0)]).unwrap();
        let (p, d) = s.track(5.0);
        assert_eq!(p, vec![v3(0.0, 0.0, 0.0), v3(0.0, 0.0, 7.0)]);
        assert!(d.iter().all(|&t| (t - V3::Z).norm() < 1e-12));
    }
}
