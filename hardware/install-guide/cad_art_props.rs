//! The customer pictures' closed crops and authored presentation props.
use super::{Shown, add, block, color, cylinder, numbers, point};
use anyhow::{Context, Result};
use hsm_kernel::part::Numbers;
use hsm_kernel::*;
use serde_json::Value;
use std::path::Path as FilePath;

fn write_props(directory: &FilePath, name: &str, shown: &Shown) -> Result<()> {
    let bodies: Vec<_> = shown
        .iter()
        .map(|(name, solid, rgb)| Body {
            name,
            solid,
            color: Some(*rgb),
        })
        .collect();
    write_payload(
        directory.join(format!("{name}.props.mesh")),
        &bodies,
        None,
        None,
    )
}

fn cropped(solid: &Solid, lo: f64, hi: f64) -> Result<Option<Solid>> {
    let bounds = solid.bounds();
    if bounds.max.z <= lo || bounds.min.z >= hi {
        return Ok(None);
    }
    let crop = solid.intersect(&block(v3(-300., -300., lo), v3(600., 600., hi - lo)))?;
    Ok((!crop.tris().is_empty()).then_some(crop))
}

fn legs(value: &Value) -> Result<Path> {
    let mut path: Option<Path> = None;
    for leg in value.as_array().context("signal legs")? {
        let (kind, points) = leg
            .as_object()
            .context("signal leg")?
            .iter()
            .next()
            .context("empty leg")?;
        let points: Vec<_> = points
            .as_array()
            .context("leg points")?
            .iter()
            .map(point)
            .collect();
        let current = path.take().unwrap_or_else(|| Path::new(points[0]));
        path = Some(match kind.as_str() {
            "line" => current.line_to(points[1]),
            "arc" => current.arc_through(points[1], points[2])?,
            _ => anyhow::bail!("unsupported signal leg {kind}"),
        });
    }
    path.context("empty signal path")
}

pub(super) fn lever(parameters: &[f64]) -> Result<(Solid, Solid)> {
    let [plateau, port_y, tube_r, pivot_y, pivot_z, pressed_angle] = *parameters else {
        anyhow::bail!("lever dimensions")
    };
    let cut = cylinder(
        v3(0., port_y + 0.125, plateau + 1.),
        2. * (tube_r + 1.),
        50.,
        V3::Z,
    )?;
    let base = block(v3(-6.5, -6., plateau + 1.), v3(13., 15., 12.));
    let p0 = Plane::XZ
        .offset(6.)
        .shifted(v2(0., plateau + 4.5 + 8.5 / 2.));
    let p1 = Plane::XZ
        .offset(42.)
        .shifted(v2(0., plateau + 10. + 3. / 2.));
    let taper = Solid::loft(&[
        Profile::rect(V2::ZERO, 13., 8.5).place(&p0),
        Profile::rect(V2::ZERO, 13., 3.).place(&p1),
    ])?;
    let rest = base.union(&taper)?.cut(&cut)?;
    let pressed = rest
        .rotate(v3(0., pivot_y, pivot_z), V3::X, pressed_angle)
        .cut(&cut)?;
    Ok((rest, pressed))
}

fn hardware(out: &mut Shown, n: &Numbers, top: f64, under: bool) -> Result<()> {
    let prefix = if under { "under-" } else { "" };
    let washer = Profile::circle(V2::ZERO, 12.).with_hole(Loop::circle(V2::ZERO, 6.1));
    add(
        out,
        &format!("{prefix}retained-donor-washer"),
        Plane::XY.at(v3(0., 0., top - 1.5)).extrude(&washer, 1.5)?,
        color(n, "washer"),
    );
    let hex: Vec<_> = (0..6)
        .map(|i| {
            let t = i as f64 * std::f64::consts::PI / 3.;
            v2(11. * t.cos(), 11. * t.sin())
        })
        .collect();
    let nut = Profile::polygon(&hex).with_hole(Loop::circle(V2::ZERO, 6.1));
    add(
        out,
        &format!("{prefix}retained-donor-nut"),
        Plane::XY.at(v3(0., 0., top - 6.5)).extrude(&nut, 5.)?,
        color(n, "nut"),
    );
    Ok(())
}

fn counter(out: &mut Shown, n: &Numbers, c: &Value, under: bool) -> Result<()> {
    let a = numbers(&c["counter"]);
    let slab = block(v3(-a[4] / 2., -a[5] / 2., a[0]), v3(a[4], a[5], a[1]));
    let hole = cylinder(v3(0., a[2], a[0] - 1.), 2. * a[3], a[1] + 2., V3::Z)?;
    add(
        out,
        if under {
            "under-countertop-window"
        } else {
            "countertop-window"
        },
        slab.cut(&hole)?,
        color(n, "counter"),
    );
    Ok(())
}

fn frame(out: &mut Shown, n: &Numbers, points: &Value, under: bool) {
    for (i, p) in points.as_array().unwrap().iter().enumerate() {
        let p = point(p) - v3(0.75, 0.75, 0.75);
        add(
            out,
            &format!(
                "{}render-frame-anchor-{}",
                if under { "under-" } else { "" },
                i + 1
            ),
            block(p, v3(1.5, 1.5, 1.5)),
            color(n, "anchor"),
        );
    }
}

fn signal(c: &Value, bodies: &[Imported]) -> Result<(Solid, Vec<Solid>)> {
    let path = legs(&c["signal_legs"])?;
    let origin = point(&c["signal_origin"]);
    let size = numbers(&c["signal_size"]);
    let tail = Plane::XY
        .sweep(&Profile::rect(V2::ZERO, size[0], size[1]), &path)?
        .translate(origin);
    let fitted = &bodies
        .iter()
        .find(|b| b.name == "display_signal_ribbon")
        .context("signal source body")?
        .solid;
    let ribbon = fitted.union(&tail)?;
    let mut stripes = vec![];
    for x in [-1.05, 0., 1.05] {
        let stripe = Plane::XY.sweep(&Profile::rect(v2(x, 0.), 0.24, 0.08), &path)?;
        stripes.push(stripe.translate(origin - v3(0., size[1] / 2. + 0.04, 0.)));
    }
    Ok((ribbon, stripes))
}

fn faucet(n: &Numbers, c: &Value, directory: &FilePath) -> Result<()> {
    let bodies = import::payload(c["input"].as_str().context("faucet crop input")?)?;
    let (rest, pressed) = lever(&numbers(&c["lever"]))?;
    let (ribbon, stripes) = signal(c, &bodies)?;
    for row in c["scenes"].as_array().context("faucet scenes")? {
        let name = row["name"].as_str().unwrap();
        let kind = row["kind"].as_str().unwrap();
        let mut out = vec![];
        if kind == "user" {
            for body in &bodies {
                if [
                    "westbrass",
                    "drain_tube",
                    "flavor_tube_pos_x",
                    "flavor_tube_neg_x",
                ]
                .contains(&body.name.as_str())
                {
                    if let Some(solid) = cropped(&body.solid, c["top_z"].as_f64().unwrap(), 260.)? {
                        add(&mut out, &body.name, solid, body.color.unwrap());
                    }
                }
            }
            add(
                &mut out,
                "lever",
                if row["pressed"].as_bool().unwrap() {
                    pressed.clone()
                } else {
                    rest.clone()
                },
                color(n, "lever"),
            );
        } else if kind != "full" {
            let under = kind == "under";
            let lift = row["lift"].as_f64().unwrap_or(0.);
            let move_by = v3(0., 0., lift);
            let (lo, hi) = if under { (-86., -2.) } else { (-88., 380.) };
            counter(&mut out, n, c, under)?;
            if !under {
                add(
                    &mut out,
                    "lever",
                    rest.translate(move_by),
                    color(n, "lever"),
                );
            }
            for body in &bodies {
                let body_name = body.name.as_str();
                if body_name == "display_signal_ribbon" || (!under && body_name == "westbrass") {
                    continue;
                }
                if let Some(solid) = cropped(&body.solid.translate(move_by), lo, hi)? {
                    let rgb = if body_name.starts_with("flavor_") {
                        color(
                            n,
                            if body_name.ends_with("pos_x") {
                                "flavor_a"
                            } else {
                                "flavor_b"
                            },
                        )
                    } else {
                        body.color.unwrap()
                    };
                    add(
                        &mut out,
                        &format!("{}{body_name}", if under { "under-" } else { "" }),
                        solid,
                        rgb,
                    );
                }
            }
            let prefix = if under { "under-" } else { "" };
            if let Some(solid) = cropped(&ribbon.translate(move_by), lo, hi)? {
                add(
                    &mut out,
                    &format!("{prefix}sig6-flat-ribbon"),
                    solid,
                    color(n, "signal"),
                );
            }
            for (i, stripe) in stripes.iter().enumerate() {
                if let Some(solid) = cropped(&stripe.translate(move_by), lo, hi)? {
                    add(
                        &mut out,
                        &format!("{prefix}sig6-ribbon-face-stripes/{}", i + 1),
                        solid,
                        color(n, "stripe"),
                    );
                }
            }
            hardware(&mut out, n, row["washer"].as_f64().unwrap(), under)?;
            frame(
                &mut out,
                n,
                &c[if under { "under_frame" } else { "frame" }],
                under,
            );
        }
        write_props(directory, name, &out)?;
    }
    Ok(())
}

fn spline(points: &[V3]) -> Result<Path> {
    let mut parameters = vec![0.];
    for pair in points.windows(2) {
        parameters.push(parameters.last().unwrap() + (pair[1] - pair[0]).norm());
    }
    Path::new(points[0]).clamped_spline(points, &parameters, [V3::Y, V3::Y])
}

#[derive(Clone, Copy)]
struct RibbonSection {
    p: V3,
    tangent: V3,
    width: V3,
}

impl RibbonSection {
    fn aligned(mut self, previous: Self) -> Self {
        // A rectangle is unchanged by a half-turn. Keep its four vertex labels continuous
        // through a spline inflection so lofting does not cross the ruled side faces.
        if self.width.dot(previous.width) < 0. {
            self.width = -self.width;
        }
        self
    }

    fn corners(self, width: f64, thickness: f64) -> [V3; 4] {
        let x = self.width * (width / 2.);
        let y = self.tangent.cross(self.width) * (thickness / 2.);
        [
            self.p - x - y,
            self.p + x - y,
            self.p + x + y,
            self.p - x + y,
        ]
    }
}

fn frenet(curve: &Spline, t: f64) -> (V3, V3, V3) {
    let (lo, hi) = curve.range();
    let h = (hi - lo) * 1e-6;
    let velocity = curve.derivative(t);
    // A clamped cubic's velocity is quadratic on each interval. These differences retain
    // its exact second derivative away from a knot, including the two one-sided ends.
    let acceleration = if t - h < lo {
        (-velocity * 3. + curve.derivative(t + h) * 4. - curve.derivative(t + 2. * h)) / (2. * h)
    } else if t + h > hi {
        (velocity * 3. - curve.derivative(t - h) * 4. + curve.derivative(t - 2. * h)) / (2. * h)
    } else {
        (curve.derivative(t + h) - curve.derivative(t - h)) / (2. * h)
    };
    let tangent = velocity.unit();
    let binormal = tangent.cross(acceleration).unit();
    (tangent, binormal.cross(tangent), binormal)
}

fn ribbon(points: &[V3], width: f64, thickness: f64) -> Result<Solid> {
    let path = spline(points)?;
    let curve = &path.curves[0];
    let (lo, hi) = curve.range();
    let (_, first_normal, first_binormal) = frenet(curve, lo);
    let a = V3::X.dot(first_normal);
    let b = V3::X.dot(first_binormal);
    let section = |t| {
        let (tangent, normal, binormal) = frenet(curve, t);
        RibbonSection {
            p: curve.point(t),
            tangent,
            width: (normal * a + binormal * b).unit(),
        }
    };
    fn divide(
        section: &impl Fn(f64) -> RibbonSection,
        a: f64,
        b: f64,
        width: f64,
        thickness: f64,
        depth: usize,
        out: &mut Vec<RibbonSection>,
    ) {
        let first = section(a);
        let last = section(b).aligned(first);
        let corners = first.corners(width, thickness);
        let end = last.corners(width, thickness);
        let needs_split = [0.25, 0.5, 0.75].into_iter().any(|share| {
            let current = section(a + (b - a) * share).aligned(first);
            current
                .corners(width, thickness)
                .iter()
                .enumerate()
                .any(|(i, p)| (*p - (corners[i] * (1. - share) + end[i] * share)).norm() > LINEAR)
        }) || first.tangent.dot(last.tangent) < ANGULAR.cos()
            || first.width.dot(last.width) < ANGULAR.cos();
        if needs_split && depth < 24 {
            let mid = (a + b) / 2.;
            divide(section, a, mid, width, thickness, depth + 1, out);
            divide(section, mid, b, width, thickness, depth + 1, out);
        } else {
            out.push(last.aligned(*out.last().unwrap()));
        }
    }
    let mut sections = vec![section(lo)];
    // Each interpolation interval is an initial band; no inflection is hidden by testing
    // only the two ends of the entire route.
    let mut parameter = lo;
    for pair in points.windows(2) {
        let next = parameter + (pair[1] - pair[0]).norm();
        divide(
            &section,
            parameter,
            next.min(hi),
            width,
            thickness,
            0,
            &mut sections,
        );
        parameter = next;
    }
    let profile = Profile::rect(V2::ZERO, width, thickness);
    let regions: Result<Vec<_>> = sections
        .into_iter()
        .map(|s| Ok(profile.place(&Plane::new(s.p, s.width, s.tangent)?)))
        .collect();
    Solid::loft(&regions?)
}

fn rear(n: &Numbers, c: &Value, directory: &FilePath) -> Result<()> {
    let mut out = vec![];
    for tube in c["tubes"].as_array().context("rear tubes")? {
        let name = tube["name"].as_str().unwrap();
        let points: Vec<_> = tube["points"]
            .as_array()
            .unwrap()
            .iter()
            .map(point)
            .collect();
        let profile = Profile::circle(V2::ZERO, tube["diameter"].as_f64().unwrap() / 2.);
        let shape = Plane::new(points[0], V3::X, V3::Y)?.sweep(&profile, &spline(&points)?)?;
        add(
            &mut out,
            &format!("wall-end-tube-{name}"),
            shape,
            color(n, name),
        );
    }
    let p = numbers(&c["plug"]);
    let (x, y, z) = (p[0], p[1], p[2]);
    for (i, shape) in [
        block(v3(x - 4.5, y, z - 3.225), v3(9., 21., 6.45)),
        block(v3(x - 3.9, y + 21., z - 2.75), v3(7.8, 5.5, 5.5)),
    ]
    .into_iter()
    .enumerate()
    {
        add(
            &mut out,
            &format!("wall-end-rj11-plug-body/{}", i + 1),
            shape,
            color(n, "plug"),
        );
    }
    let latch_z = z - 3.225;
    add(
        &mut out,
        "wall-end-rj11-latch/1",
        block(v3(x - 1.7, y + 4., latch_z - 0.75), v3(3.4, 12., 0.75)),
        color(n, "latch"),
    );
    let ramp = Profile::polygon(&[
        v2(y + 10., latch_z - 0.75),
        v2(y + 16., latch_z - 0.75),
        v2(y + 16., latch_z - 2.35),
    ]);
    add(
        &mut out,
        "wall-end-rj11-latch/2",
        Plane::YZ.at(v3(x - 1.7, 0., 0.)).extrude(&ramp, 3.4)?,
        color(n, "latch"),
    );
    for (i, dx) in [-2.7, -0.9, 0.9, 2.7].into_iter().enumerate() {
        add(
            &mut out,
            &format!("wall-end-rj11-contact-{}", i + 1),
            block(
                v3(x + dx - 0.24, y + 0.4, z + 3.225 - 0.18),
                v3(0.48, 7., 0.18),
            ),
            color(n, "gold"),
        );
    }
    let points: Vec<_> = c["ribbon_points"]
        .as_array()
        .unwrap()
        .iter()
        .map(point)
        .collect();
    add(
        &mut out,
        "wall-end-sig6-ribbon",
        ribbon(&points, 4., 1.2)?,
        color(n, "signal"),
    );
    let mark: Vec<_> = points.iter().map(|p| *p + v3(1.55, 0., 0.63)).collect();
    add(
        &mut out,
        "wall-end-sig6-ribbon-mark",
        ribbon(&mark, 0.28, 0.08)?,
        color(n, "stripe"),
    );
    write_props(directory, "rear-leads", &out)
}

pub fn write(n: &Numbers, directory: &FilePath) -> Result<()> {
    let c = n.get("cad_art")?;
    match c["kind"].as_str() {
        Some("faucet") => faucet(n, c, directory),
        Some("rear") => rear(n, c, directory),
        _ => anyhow::bail!("unknown customer prop family"),
    }
}
