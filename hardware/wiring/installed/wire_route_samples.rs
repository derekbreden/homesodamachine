//! Length, arc-length positions and bend samples of recorded installed-wire splines.
use anyhow::Result;
use hsm_kernel::{Spline, V3};
use serde::Serialize;

/// What is measured along a spline: its length, points at even steps of that length, the step
/// between them and its tightest bend.
#[derive(Serialize)]
pub struct Reading {
    pub length_mm: f64,
    pub sampled_points_mm: Vec<[f64; 3]>,
    pub maximum_sample_step_mm: f64,
    pub minimum_bend_mm: Option<f64>,
}

fn integrate(curve: &Spline, a: f64, b: f64) -> f64 {
    fn refine(
        curve: &Spline,
        a: f64,
        b: f64,
        speeds: [f64; 3],
        whole: f64,
        tolerance: f64,
        remaining: u32,
    ) -> f64 {
        let middle = (a + b) / 2.;
        let left_speed = curve.derivative((a + middle) / 2.).norm();
        let right_speed = curve.derivative((middle + b) / 2.).norm();
        let left = (middle - a) * (speeds[0] + 4. * left_speed + speeds[1]) / 6.;
        let right = (b - middle) * (speeds[1] + 4. * right_speed + speeds[2]) / 6.;
        let error = left + right - whole;
        if remaining == 0 || error.abs() <= 15. * tolerance {
            left + right + error / 15.
        } else {
            refine(
                curve,
                a,
                middle,
                [speeds[0], left_speed, speeds[1]],
                left,
                tolerance / 2.,
                remaining - 1,
            ) + refine(
                curve,
                middle,
                b,
                [speeds[1], right_speed, speeds[2]],
                right,
                tolerance / 2.,
                remaining - 1,
            )
        }
    }
    if a == b {
        return 0.;
    }
    let speeds = [
        curve.derivative(a).norm(),
        curve.derivative((a + b) / 2.).norm(),
        curve.derivative(b).norm(),
    ];
    let whole = (b - a) * (speeds[0] + 4. * speeds[1] + speeds[2]) / 6.;
    refine(curve, a, b, speeds, whole, 1e-10, 20)
}

struct Measured {
    curve: Spline,
    parameters: Vec<f64>,
    cumulative: Vec<f64>,
}

impl Measured {
    fn new(points: &[[f64; 3]], parameters: &[f64], derivatives: [[f64; 3]; 2]) -> Result<Self> {
        let points: Vec<V3> = points.iter().map(|&p| V3::from(p)).collect();
        let parameters = parameters.to_vec();
        let curve = Spline::clamped(&points, &parameters, derivatives.map(V3::from))?;
        let mut cumulative = vec![0.];
        for span in parameters.windows(2) {
            cumulative.push(cumulative.last().unwrap() + integrate(&curve, span[0], span[1]));
        }
        Ok(Self {
            curve,
            parameters,
            cumulative,
        })
    }

    fn length(&self) -> f64 {
        *self.cumulative.last().unwrap()
    }

    fn parameter(&self, fraction: f64) -> f64 {
        if fraction <= 0. {
            return self.parameters[0];
        }
        if fraction >= 1. {
            return *self.parameters.last().unwrap();
        }
        let target = fraction * self.length();
        let span = self
            .cumulative
            .partition_point(|&value| value <= target)
            .clamp(1, self.parameters.len() - 1)
            - 1;
        let (begin, end) = (self.parameters[span], self.parameters[span + 1]);
        let needed = target - self.cumulative[span];
        let mut lower = begin;
        let mut upper = end;
        let mut parameter =
            begin + (end - begin) * needed / (self.cumulative[span + 1] - self.cumulative[span]);
        for _ in 0..32 {
            let error = integrate(&self.curve, begin, parameter) - needed;
            if error.abs() < 1e-9 {
                break;
            }
            if error < 0. {
                lower = parameter;
            } else {
                upper = parameter;
            }
            let next = parameter - error / self.curve.derivative(parameter).norm();
            parameter = if next.is_finite() && next > lower && next < upper {
                next
            } else {
                (lower + upper) / 2.
            };
        }
        parameter
    }

    fn curvature(&self, parameter: f64) -> f64 {
        let span = self
            .parameters
            .partition_point(|&value| value <= parameter)
            .clamp(1, self.parameters.len() - 1)
            - 1;
        let (a, b) = (self.parameters[span], self.parameters[span + 1]);
        let h = b - a;
        let s = (parameter - a) / h;
        let m0 = self.curve.derivative(a);
        let m1 = self.curve.derivative(b);
        let chord = self.curve.point(b) - self.curve.point(a);
        // Exact second derivative of this Hermite span, using the kernel's own
        // endpoint values/slopes. No finite-difference curvature is introduced.
        let second = chord * ((6. - 12. * s) / (h * h))
            + m0 * ((6. * s - 4.) / h)
            + m1 * ((6. * s - 2.) / h);
        let first = self.curve.derivative(parameter);
        first.cross(second).norm() / first.norm().powi(3)
    }

    fn reading(&self) -> Reading {
        let length = self.length();
        let count = (length / 0.25).ceil().max(2.) as usize;
        let positions: Vec<_> = (0..=count)
            .map(|i| {
                self.curve
                    .point(self.parameter(i as f64 / count as f64))
                    .to_array()
            })
            .collect();
        let minimum = (0..=200)
            .map(|i| self.curvature(self.parameter(i as f64 / 200.)))
            .filter(|&k| k > 1e-12)
            .map(|k| 1. / k)
            .reduce(f64::min);
        Reading {
            length_mm: length,
            sampled_points_mm: positions,
            maximum_sample_step_mm: length / count as f64,
            minimum_bend_mm: minimum,
        }
    }
}

/// The measurements along the clamped spline through `points` at `parameters`, with
/// `derivatives` at its ends.
pub fn measure(points: &[[f64; 3]], parameters: &[f64], derivatives: [[f64; 3]; 2]) -> Result<Reading> {
    Ok(Measured::new(points, parameters, derivatives)?.reading())
}
