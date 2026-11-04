//! Length, arc-length positions and bend samples of recorded installed-wire splines.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Spline, V3, part, v3};
use serde_json::{Value, json};

fn point(value: &Value) -> Result<V3> {
    let values = value.as_array().context("wire interpolation point")?;
    ensure!(values.len() == 3, "three wire coordinates");
    Ok(v3(
        values[0].as_f64().context("wire x")?,
        values[1].as_f64().context("wire y")?,
        values[2].as_f64().context("wire z")?,
    ))
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
    fn new(value: &Value) -> Result<Self> {
        let points = value["interpolation_points_mm"]
            .as_array()
            .context("wire interpolation points")?
            .iter()
            .map(point)
            .collect::<Result<Vec<_>>>()?;
        let parameters = value["parameters"]
            .as_array()
            .context("wire spline parameters")?
            .iter()
            .map(|v| v.as_f64().context("numeric wire parameter"))
            .collect::<Result<Vec<_>>>()?;
        let derivatives = value["endpoint_derivatives"]
            .as_array()
            .context("wire endpoint derivatives")?;
        ensure!(derivatives.len() == 2, "two wire endpoint derivatives");
        let curve = Spline::clamped(
            &points,
            &parameters,
            [point(&derivatives[0])?, point(&derivatives[1])?],
        )?;
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

    fn reading(&self) -> Value {
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
        json!({"length_mm":length,"sampled_points_mm":positions,
            "maximum_sample_step_mm":length/count as f64,"minimum_bend_mm":minimum})
    }
}

fn main() -> Result<()> {
    let (numbers, output) = part::args()?;
    ensure!(
        output.as_os_str() == "--check",
        "wire-route-samples reads numeric splines only"
    );
    let readings = numbers
        .get("splines")?
        .as_array()
        .context("wire spline requests")?
        .iter()
        .map(|value| Ok(Measured::new(value)?.reading()))
        .collect::<Result<Vec<_>>>()?;
    println!("{}", json!({"splines":readings}));
    Ok(())
}

/// Scalar spline measurements shared with the installed wiring recipe composer.
pub fn measure(value: &Value) -> Result<Value> {
    Ok(Measured::new(value)?.reading())
}
