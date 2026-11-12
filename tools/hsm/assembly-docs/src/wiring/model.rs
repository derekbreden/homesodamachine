use super::*;
use graph::Connection;
use serde::{Deserialize, Serialize};
pub use wire_request::{Segment, Spline, V};
use wire_request::Shape;

/// A colour as its source states it: sRGB channels, or linear ones.
#[derive(Clone, Copy, Debug)]
pub enum Colour {
    Srgb(V),
    Linear(V),
}

impl Colour {
    /// The colour's linear channels, as the payload carries them.
    pub fn linear(self) -> V {
        match self {
            Colour::Linear(channels) => channels,
            Colour::Srgb(mut color) => {
                for c in &mut color {
                    let v = if *c <= 0.04045 {
                        *c / 12.92
                    } else {
                        ((*c + 0.055) / 1.055).powf(2.4)
                    };
                    *c = v as f32 as f64;
                }
                color
            }
        }
    }
}

/// A termination or a jacket to cut: its name, its shape and its colour.
#[derive(Clone, Debug)]
pub struct Body {
    pub name: String,
    pub shape: Shape,
    pub colour: Colour,
}

/// A point of a source document.
pub fn v(value: &Value) -> Result<V> {
    let a = rows(value)?;
    ensure!(a.len() == 3, "three wire coordinates");
    Ok([number(&a[0])?, number(&a[1])?, number(&a[2])?])
}
pub fn add(a: V, b: V) -> V {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}
pub fn sub(a: V, b: V) -> V {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
pub fn mul(a: V, t: f64) -> V {
    [a[0] * t, a[1] * t, a[2] * t]
}
pub fn dot(a: V, b: V) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}
pub fn cross(a: V, b: V) -> V {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
pub fn norm(a: V) -> f64 {
    dot(a, a).sqrt()
}
pub fn unit(a: V) -> V {
    mul(a, 1. / norm(a))
}

/// One kind of wire: its gauge, its insulated diameter, its colour and what the review says of
/// it.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Stock {
    pub awg: u64,
    pub od_mm: f64,
    pub color: V,
    pub basis: String,
    pub construction: String,
}

/// Every kind of wire the installed wiring is cut from, by name. The cord's neutral and earth
/// cores are its hot core in their own colours.
pub fn stock() -> Result<BTreeMap<String, Stock>> {
    let mut stock: BTreeMap<String, Stock> = serde_json::from_value(hsm_kernel::reads::json(
        "tools/hsm/assembly-docs/src/wiring/stock.json",
    )?)
    .context("the wire stock")?;
    for (name, color) in [
        ("neutral18", [0.9, 0.9, 0.87]),
        ("earth18", [0.06, 0.42, 0.12]),
    ] {
        let mut row = stock.get("cord18").context("the cord's stock")?.clone();
        row.color = color;
        stock.insert(name.into(), row);
    }
    Ok(stock)
}

/// The stock `connection` is cut from.
pub fn stock_of<'a>(stock: &'a BTreeMap<String, Stock>, connection: &Connection) -> Result<&'a Stock> {
    stock
        .get(&connection.stock)
        .with_context(|| format!("{} names the unknown stock {}", connection.id, connection.stock))
}

/// The straight run from `a` to `b`.
pub fn line(a: V, b: V) -> Segment {
    Segment::Line {
        start_mm: a,
        end_mm: b,
        length_mm: norm(sub(b, a)),
    }
}

/// The straight runs through `input` with each corner filleted at `radius`, or as near it as
/// the corner's legs allow.
pub fn rounded(
    input: &[V],
    radius: f64,
    keep_collinear: bool,
    endpoint_fraction: f64,
) -> Result<Vec<Segment>> {
    let mut pts: Vec<V> = Vec::new();
    for &point in input {
        if pts.last().is_none_or(|last| norm(sub(*last, point)) > 1e-6) {
            pts.push(point);
        }
        if !keep_collinear {
            while pts.len() > 2 {
                let n = pts.len();
                let a = sub(pts[n - 2], pts[n - 3]);
                let b = sub(pts[n - 1], pts[n - 2]);
                if dot(unit(a), unit(b)) < 1. - 1e-10 {
                    break;
                }
                pts.remove(n - 2);
            }
        }
    }
    ensure!(!pts.is_empty(), "wire route has no points");
    let mut corners = BTreeMap::new();
    for i in 1..pts.len().saturating_sub(1) {
        let before = sub(pts[i - 1], pts[i]);
        let after = sub(pts[i + 1], pts[i]);
        let (la, lb) = (norm(before), norm(after));
        let (u, v) = (unit(before), unit(after));
        let included = dot(u, v).clamp(-1., 1.).acos();
        if included < 1e-5 || (std::f64::consts::PI - included).abs() < 1e-5 {
            continue;
        }
        let tangent = (radius / (included / 2.).tan())
            .min((if i == 1 { endpoint_fraction } else { 0.44 }) * la)
            .min(
                (if i == pts.len() - 2 {
                    endpoint_fraction
                } else {
                    0.44
                }) * lb,
            );
        let r = tangent * (included / 2.).tan();
        let a = add(pts[i], mul(u, tangent));
        let b = add(pts[i], mul(v, tangent));
        let bisector = unit(add(u, v));
        let centre = add(pts[i], mul(bisector, r / (included / 2.).sin()));
        let midpoint = add(centre, mul(bisector, -r));
        corners.insert(i, (a, midpoint, b, r, std::f64::consts::PI - included));
    }
    let mut out = Vec::new();
    let mut current = pts[0];
    fn append(out: &mut Vec<Segment>, current: &mut V, end: V) {
        let segment = line(*current, end);
        if segment.length() > 1e-6 {
            out.push(segment);
        }
        *current = end;
    }
    for i in 1..pts.len().saturating_sub(1) {
        if let Some(&(a, mid, b, r, angle)) = corners.get(&i) {
            append(&mut out, &mut current, a);
            out.push(Segment::Arc {
                start_mm: a,
                midpoint_mm: mid,
                end_mm: b,
                radius_mm: r,
                angle_radians: angle,
                length_mm: r * angle,
            });
            current = b;
        } else {
            append(&mut out, &mut current, pts[i]);
        }
    }
    append(&mut out, &mut current, *pts.last().unwrap());
    Ok(out)
}

/// The clamped spline through `points` that leaves and arrives along `tangents`, its
/// parameters spaced evenly or by chord length.
pub fn spline(points: &[V], tangents: [V; 2], chord_length: bool) -> Result<Segment> {
    ensure!(points.len() >= 3, "spline endpoints and tangents");
    let count = points.len() - 1;
    let mut derivatives = Vec::new();
    for (direction, a, b, c) in [
        (tangents[0], points[0], points[1], points[2]),
        (
            tangents[1],
            points[count],
            points[count - 1],
            points[count - 2],
        ),
    ] {
        let derivative = mul(sub(sub(mul(b, 4.), c), mul(a, 3.)), count as f64 / 2.);
        derivatives.push(mul(unit(direction), dot(derivative, unit(direction)).abs()));
    }
    let mut parameters = (0..=count)
        .map(|i| i as f64 / count as f64)
        .collect::<Vec<_>>();
    if chord_length {
        let mut distances = vec![0.];
        for pair in points.windows(2) {
            distances.push(distances.last().unwrap() + norm(sub(pair[1], pair[0])));
        }
        let length = *distances.last().unwrap();
        parameters = distances.iter().map(|d| d / length).collect();
        derivatives = tangents.iter().map(|t| mul(unit(*t), length)).collect();
    }
    let derivatives = [derivatives[0], derivatives[1]];
    let measured = wire_samples::measure(points, &parameters, derivatives)?;
    Ok(Segment::Spline(Spline {
        start_mm: points[0],
        end_mm: points[count],
        interpolation_points_mm: points.to_vec(),
        endpoint_tangents: tangents,
        endpoint_derivatives: derivatives,
        parameters,
        length_mm: measured.length_mm,
        sampled_points_mm: measured.sampled_points_mm,
        maximum_sample_step_mm: measured.maximum_sample_step_mm,
        minimum_bend_mm: measured.minimum_bend_mm,
    }))
}

/// The centre and axis of the arc from `start` through `midpoint` to `end`.
pub fn circle(start: V, midpoint: V, end: V) -> (V, V) {
    let a = start;
    let u = sub(midpoint, a);
    let b = sub(end, a);
    let n = cross(u, b);
    let centre = add(
        a,
        mul(
            add(mul(cross(n, u), dot(b, b)), mul(cross(b, n), dot(u, u))),
            1. / (2. * dot(n, n)),
        ),
    );
    (centre, unit(n))
}
pub fn rotate(v: V, axis: V, angle: f64) -> V {
    add(
        add(mul(v, angle.cos()), mul(cross(axis, v), angle.sin())),
        mul(axis, dot(axis, v) * (1. - angle.cos())),
    )
}

/// Points along `segments` no more than `step` apart, ending on the last segment's end.
pub fn sample(segments: &[Segment], step: f64) -> Vec<V> {
    let mut out = Vec::new();
    fn append(out: &mut Vec<V>, a: V, b: V, step: f64) {
        let count = (norm(sub(b, a)) / step).ceil().max(1.) as usize;
        for i in 0..count {
            out.push(add(a, mul(sub(b, a), i as f64 / count as f64)));
        }
    }
    for s in segments {
        match s {
            Segment::Line { start_mm, end_mm, .. } => append(&mut out, *start_mm, *end_mm, step),
            Segment::Spline(spline) => {
                for pair in spline.sampled_points_mm.windows(2) {
                    append(&mut out, pair[0], pair[1], step);
                }
            }
            Segment::Arc {
                start_mm,
                midpoint_mm,
                end_mm,
                radius_mm,
                angle_radians,
                length_mm,
            } => {
                let (centre, n) = circle(*start_mm, *midpoint_mm, *end_mm);
                let radius = *radius_mm;
                let x = mul(sub(*start_mm, centre), 1. / radius);
                let y = cross(n, x);
                let count = (length_mm / step).ceil().max(2.) as usize;
                for i in 0..count {
                    let angle = angle_radians * i as f64 / count as f64;
                    out.push(add(
                        centre,
                        mul(add(mul(x, angle.cos()), mul(y, angle.sin())), radius),
                    ));
                }
            }
        }
    }
    if let Some(last) = segments.last() {
        out.push(last.end());
    }
    out
}

/// A conductor, termination or jacket the wiring is built without: its name, the two terminals
/// a conductor would join, and the error its routing or its cutting ended in.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NotRouted {
    pub id: String,
    pub from: String,
    pub to: String,
    pub reason: String,
}

/// A conductor's routed course: the points it is drawn through and the segments fitted to
/// them.
#[derive(Clone, Debug, Serialize)]
pub struct Route {
    pub connection: Connection,
    pub points: Vec<V>,
    pub segments: Vec<Segment>,
    pub length_mm: f64,
    pub minimum_bend_mm: Option<f64>,
    pub status: String,
    pub note: String,
}

/// A route as the review lists it: its connection's fields beside its course.
#[derive(Serialize)]
pub struct Record<'a> {
    #[serde(flatten)]
    connection: &'a Connection,
    points_mm: &'a [V],
    segments: &'a [Segment],
    minimum_bend_mm: Option<f64>,
    route_status: &'a str,
    routing_note: &'a str,
    length_mm: f64,
}

impl Route {
    /// The route as the review lists it, its length rounded for the listing.
    pub fn record(&self) -> Result<Record<'_>> {
        Ok(Record {
            connection: &self.connection,
            points_mm: &self.points,
            segments: &self.segments,
            minimum_bend_mm: self.minimum_bend_mm,
            route_status: &self.status,
            routing_note: &self.note,
            length_mm: places(self.length_mm, 3)?,
        })
    }
}

/// The route of `connection` through `points`, its corners filleted at `radius` or at its
/// stock's own bend where none is given.
pub fn finish(
    connection: &Connection,
    points: Vec<V>,
    radius: Option<f64>,
    endpoint_tangent_fraction: f64,
    note: &str,
    status: &str,
) -> Result<Route> {
    let stock = stock()?;
    let radius = radius.unwrap_or(if stock_of(&stock, connection)?.awg < 22 {
        5.
    } else {
        4.
    });
    let segments = rounded(&points, radius, false, endpoint_tangent_fraction)?;
    let length = segments.iter().map(Segment::length).sum::<f64>();
    let minimum = segments
        .iter()
        .filter_map(|s| match s {
            Segment::Arc { radius_mm, .. } => Some(*radius_mm),
            _ => None,
        })
        .reduce(f64::min)
        .map(|v| places(v, 4))
        .transpose()?;
    Ok(Route {
        connection: connection.clone(),
        points,
        segments,
        length_mm: length,
        minimum_bend_mm: minimum,
        status: status.to_owned(),
        note: note.to_owned(),
    })
}
