//! The copper refrigerant runs between the compressor, the condenser and the cold core's
//! evaporator: each a centreline from port to port, rounded at every corner by the largest radius
//! its legs seat under the run's cap.
use crate::design;
use crate::routes_program::Sweep;
use anyhow::{Context, Result, ensure};
use hsm_layout_data::tube::Segment;
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

type V3 = [f64; 3];

/// Two points closer than this are one point of a centreline.
const SAME_POINT: f64 = 1e-9;
/// A waypoint the run turns through by less than this many degrees is run straight through.
const STRAIGHT_DEGREES: f64 = 2.;
/// A turn of less than this many degrees is no corner.
const NO_TURN_DEGREES: f64 = 1e-6;
/// A corner seated under this radius is drawn square.
const SQUARE: f64 = 1e-6;
/// How near a corner's radius comes to its cap, or a leg to its spent length, and counts as there.
const REACHED: f64 = 1e-9;

/// How one copper run is authored: the ports it joins, the straight it leaves and enters them
/// along, the radius it caps its corners at when not the stock's own, and the bend floor it states
/// for itself.
struct Authored {
    id: &'static str,
    from: &'static str,
    to: &'static str,
    lead: Option<f64>,
    cap: Option<f64>,
    floor: Option<f64>,
}

/// The machine's copper runs: discharge to condenser, condenser to evaporator, evaporator to suction.
const AUTHORED: &[Authored] = &[
    Authored {
        id: "refrig-1",
        from: "compressor.refrig-discharge",
        to: "condenser+fan.refrig-inlet",
        lead: None,
        cap: None,
        floor: None,
    },
    Authored {
        id: "refrig-2",
        from: "condenser+fan.refrig-outlet",
        to: "foam-assembly.evap-inlet",
        lead: Some(2.),
        cap: None,
        floor: Some(8.),
    },
    Authored {
        id: "refrig-3",
        from: "compressor.refrig-suction",
        to: "foam-assembly.evap-outlet",
        lead: Some(20.),
        cap: Some(12.7),
        floor: None,
    },
];

/// A port a run ends at: where it is, the way a tube leaves it, and the bore it takes.
struct Port {
    at: V3,
    out: V3,
    bore: f64,
}

/// One corner of a centreline: the waypoint it turns at, by how many degrees, and the lengths of
/// the leg into it and the leg out of it.
pub struct Corner {
    pub index: usize,
    pub turn: f64,
    pub leg_in: f64,
    pub leg_out: f64,
}

/// One solved copper run: its waypoints with every corner square, and the radius each corner
/// turns at.
pub struct Run {
    pub id: &'static str,
    pub from: &'static str,
    pub to: &'static str,
    pub points: Vec<V3>,
    pub bore: f64,
    pub cap: f64,
    pub floor: Option<f64>,
    pub corners: Vec<Corner>,
    pub radii: BTreeMap<usize, f64>,
    pub caps: BTreeMap<usize, f64>,
}

/// The sum of two vectors.
fn add(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] + b[i])
}

/// The difference of two vectors.
fn sub(a: V3, b: V3) -> V3 {
    std::array::from_fn(|i| a[i] - b[i])
}

/// A vector scaled by `s`.
fn scale(a: V3, s: f64) -> V3 {
    a.map(|v| v * s)
}

/// A vector divided by `d`.
fn divide(a: V3, d: f64) -> V3 {
    a.map(|v| v / d)
}

/// The dot product of two vectors.
fn dot(a: V3, b: V3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

/// A vector's length.
fn length(a: V3) -> f64 {
    dot(a, a).sqrt()
}

/// The distance between two points.
fn distance(a: V3, b: V3) -> f64 {
    length(sub(b, a))
}

/// The unit direction from `a` to `b`.
fn heading(a: V3, b: V3) -> V3 {
    divide(sub(b, a), distance(a, b))
}

/// A point or direction written as a JSON array.
fn xyz(value: &Value) -> Result<V3> {
    let row = value.as_array().filter(|row| row.len() == 3).context("three coordinates")?;
    let mut out = [0.; 3];
    for (slot, v) in out.iter_mut().zip(row) {
        *slot = v.as_f64().context("a coordinate")?;
    }
    Ok(out)
}

/// The radius the catalog's refrigerant stock bends no tighter than, for a run that names no cap.
fn stock_cap(root: &Path) -> Result<f64> {
    let catalog = design::read(root.join("tools/hsm/shared-data/catalog/routing.json"))?;
    let stocks: Vec<&Value> = catalog["stocks"]
        .as_array()
        .context("the routing catalog's stocks")?
        .iter()
        .filter(|stock| stock["kinds"].as_array().is_some_and(|kinds| kinds.iter().any(|k| k == "refrigerant")))
        .collect();
    ensure!(stocks.len() == 1, "the routing catalog holds {} refrigerant stocks, not one", stocks.len());
    stocks[0]["min_bend"].as_f64().context("the refrigerant stock's bend radius")
}

/// The port `anchor` (`body.port`) names, from the placed pack's frames.
fn port(frames: &Value, anchor: &str) -> Result<Port> {
    let (body, name) = anchor.split_once('.').context("a port anchor")?;
    let row = frames[body]["ports"]
        .get(name)
        .with_context(|| format!("the placed pack has no port {anchor}"))?;
    let axis = xyz(&row["axis"])?;
    Ok(Port {
        at: xyz(&row["pos"])?,
        out: divide(axis, length(axis)),
        bore: row["diam"].as_f64().context("a port's bore")?,
    })
}

/// The points with each one that repeats the point before it dropped.
fn dedupe(points: &[V3]) -> Vec<V3> {
    let mut out = vec![points[0]];
    for &p in &points[1..] {
        if distance(p, *out.last().unwrap()) > SAME_POINT {
            out.push(p);
        }
    }
    out
}

/// The points with each waypoint the run turns through too little to round dropped.
fn straighten(points: &[V3]) -> Vec<V3> {
    let straight = STRAIGHT_DEGREES.to_radians().cos();
    let mut out = vec![points[0]];
    for i in 1..points.len() - 1 {
        if dot(heading(*out.last().unwrap(), points[i]), heading(points[i], points[i + 1])) < straight {
            out.push(points[i]);
        }
    }
    out.push(*points.last().unwrap());
    out
}

/// Every interior waypoint the centreline turns at.
fn corners(points: &[V3]) -> Vec<Corner> {
    let mut out = vec![];
    for i in 1..points.len() - 1 {
        let cosine = dot(heading(points[i - 1], points[i]), heading(points[i], points[i + 1]));
        let turn = cosine.clamp(-1., 1.).acos().to_degrees();
        if turn >= NO_TURN_DEGREES {
            out.push(Corner {
                index: i,
                turn,
                leg_in: distance(points[i - 1], points[i]),
                leg_out: distance(points[i], points[i + 1]),
            });
        }
    }
    out
}

/// The largest radius each corner seats under its cap, its legs shared with the corners beside it.
///
/// Every corner rises together from nothing until it reaches its cap or a leg it shares runs out
/// of straight to back its arc down; one that stops leaves the rest of its legs to the neighbour
/// still rising.
fn seat(points: &[V3], corners: &[Corner], caps: &BTreeMap<usize, f64>) -> BTreeMap<usize, f64> {
    let tangent: BTreeMap<usize, f64> =
        corners.iter().map(|c| (c.index, (c.turn.to_radians() / 2.).tan())).collect();
    let legs: Vec<f64> = points.windows(2).map(|w| distance(w[0], w[1])).collect();
    let ends = |leg: usize| [leg, leg + 1].into_iter().filter(|i| tangent.contains_key(i)).collect::<Vec<_>>();
    let mut radii: BTreeMap<usize, f64> = tangent.keys().map(|&i| (i, 0.)).collect();
    let mut free: BTreeSet<usize> = tangent.keys().copied().collect();
    while !free.is_empty() {
        let mut step = free.iter().map(|i| caps[i] - radii[i]).fold(f64::INFINITY, f64::min);
        for (j, leg) in legs.iter().enumerate() {
            let on = ends(j);
            let rising: Vec<usize> = on.iter().copied().filter(|i| free.contains(i)).collect();
            if rising.is_empty() {
                continue;
            }
            let spent: f64 = on.iter().map(|i| radii[i] * tangent[i]).sum();
            let share: f64 = rising.iter().map(|i| tangent[i]).sum();
            step = step.min((leg - spent).max(0.) / share);
        }
        for i in &free {
            *radii.get_mut(i).unwrap() += step;
        }
        let mut done: BTreeSet<usize> = free.iter().copied().filter(|i| caps[i] - radii[i] <= REACHED).collect();
        for (j, leg) in legs.iter().enumerate() {
            let on = ends(j);
            if !on.is_empty() && leg - on.iter().map(|i| radii[i] * tangent[i]).sum::<f64>() <= REACHED {
                done.extend(on.into_iter().filter(|i| free.contains(i)));
            }
        }
        if done.is_empty() {
            break;
        }
        free.retain(|i| !done.contains(i));
    }
    for radius in radii.values_mut() {
        if *radius < SQUARE - REACHED {
            *radius = 0.;
        }
    }
    radii
}

/// One authored run solved through the placed pack's ports.
fn solve(authored: &Authored, frames: &Value, stock: f64) -> Result<Run> {
    let source = port(frames, authored.from)?;
    let target = port(frames, authored.to)?;
    let cap = authored.cap.unwrap_or(stock);
    let mut points = vec![source.at];
    if let Some(lead) = authored.lead {
        points.push(add(source.at, scale(source.out, lead)));
        points.push(add(target.at, scale(target.out, lead)));
    }
    points.push(target.at);
    let points = straighten(&dedupe(&points));
    let corners = corners(&points);
    let caps: BTreeMap<usize, f64> = corners.iter().map(|c| (c.index, cap)).collect();
    let radii = seat(&points, &corners, &caps);
    Ok(Run {
        id: authored.id,
        from: authored.from,
        to: authored.to,
        points,
        bore: source.bore,
        cap,
        floor: authored.floor,
        corners,
        radii,
        caps,
    })
}

/// The copper runs, solved through the ports of the pack the placement program set down in `prepared`.
pub fn runs(root: &Path, prepared: &Value) -> Result<Vec<Run>> {
    let frames = &prepared["metadata"]["frames"];
    let stock = stock_cap(root)?;
    AUTHORED
        .iter()
        .map(|authored| solve(authored, frames, stock).with_context(|| format!("copper run {}", authored.id)))
        .collect()
}

/// Per-corner values as a JSON object keyed by corner index.
fn indexed(values: &BTreeMap<usize, f64>) -> Value {
    Value::Object(values.iter().map(|(i, v)| (i.to_string(), json!(v))).collect::<Map<_, _>>())
}

impl Run {
    /// The length of stock the run cuts, each corner's arc in place of its square.
    pub fn length(&self) -> f64 {
        let mut total: f64 = self.points.windows(2).map(|w| distance(w[0], w[1])).sum();
        for corner in &self.corners {
            let radius = self.radii[&corner.index];
            let turn = corner.turn.to_radians();
            total -= 2. * radius * (turn / 2.).tan() - radius * turn;
        }
        total
    }

    /// The centreline as the kernel sweeps it, straights joined by an arc at each rounded corner.
    pub fn segments(&self) -> Vec<Segment> {
        let p = &self.points;
        let mut segments = vec![];
        let mut cursor = p[0];
        for corner in &self.corners {
            let radius = self.radii[&corner.index];
            let back = radius * (corner.turn.to_radians() / 2.).tan();
            if back == 0. {
                continue;
            }
            let vertex = p[corner.index];
            let incoming = heading(p[corner.index - 1], vertex);
            let outgoing = heading(vertex, p[corner.index + 1]);
            let start = sub(vertex, scale(incoming, back));
            let end = add(vertex, scale(outgoing, back));
            let bisector = sub(outgoing, incoming);
            let reach = radius / (corner.turn.to_radians() / 2.).cos();
            let center = add(vertex, scale(divide(bisector, length(bisector)), reach));
            let radial = sub(vertex, center);
            let middle = add(center, scale(divide(radial, length(radial)), radius));
            if distance(cursor, start) > SAME_POINT {
                segments.push(Segment::Line { points_mm: [cursor, start] });
            }
            segments.push(Segment::Arc { points_mm: [start, middle, end] });
            cursor = end;
        }
        if distance(cursor, *p.last().unwrap()) > SAME_POINT {
            segments.push(Segment::Line { points_mm: [cursor, *p.last().unwrap()] });
        }
        segments
    }

    /// The run as the plan's metadata records it.
    pub fn record(&self) -> Value {
        let bends: Vec<Value> =
            self.corners.iter().map(|c| json!([c.index, c.turn, c.leg_in, c.leg_out])).collect();
        json!({"id": self.id, "kind": "refrigerant", "frm": self.from, "to": self.to, "pts": self.points,
            "diam": self.bore, "bend": self.cap, "note": "", "min_bend": self.floor, "bends": bends,
            "radii": indexed(&self.radii), "caps": indexed(&self.caps), "length": self.length()})
    }

    /// The run as the routes program sweeps it: a solid copper tube along its centreline.
    pub fn sweep(&self) -> Result<Sweep> {
        Ok(Sweep {
            name: self.id.to_owned(),
            segments: self.segments(),
            od_mm: self.bore,
            id_mm: 0.,
            color: Some(design::material("M_COPPER")?),
        })
    }
}
