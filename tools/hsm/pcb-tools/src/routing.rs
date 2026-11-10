//! Routing queries expose authored copper approaches and the connected top-layer free space.
use crate::{
    circuit::{Circuit, Element, Pad, Point},
    geometry::{self, Segment},
};
use anyhow::{bail, ensure, Context, Result};
use std::{
    collections::{BTreeMap, BTreeSet, VecDeque},
    fmt::Write as _,
    fs,
    path::{Path, PathBuf},
    process::Command,
};

fn strip_comments(text: &str) -> String {
    let mut out = String::new();
    let mut rest = text;
    while let Some(index) = rest.find("/*") {
        out.push_str(&rest[..index]);
        rest = &rest[index + 2..];
        if let Some(end) = rest.find("*/") {
            rest = &rest[end + 2..];
        } else {
            return out;
        }
    }
    out.push_str(rest);
    out
}
fn normalize(text: &str) -> String {
    text.chars()
        .filter(|c| !matches!(c, ' ' | '.' | '>'))
        .collect()
}
fn pair(a: &str, b: &str) -> [String; 2] {
    let mut p = [normalize(a), normalize(b)];
    p.sort();
    p
}
fn attribute<'a>(tag: &'a str, name: &str) -> Option<&'a str> {
    let marker = format!("{name}=\"");
    let rest = tag.split_once(&marker)?.1;
    Some(rest.split_once('"')?.0)
}

struct TraceSegment {
    line: Segment,
    layer: String,
    width: f64,
}
struct Trace {
    display: String,
    key: String,
    authored: bool,
    segments: Vec<TraceSegment>,
}
struct Obstacle {
    name: String,
    point: Point,
    half: [f64; 2],
    rotation: f64,
    layers: Vec<String>,
    net: Option<String>,
}
fn traces(circuit: &Circuit, source: &Path) -> Result<(Vec<Trace>, Vec<Obstacle>)> {
    let text = strip_comments(&fs::read_to_string(source)?);
    let mut authored = BTreeSet::new();
    let mut rest = text.as_str();
    while let Some(index) = rest.find("<trace") {
        rest = &rest[index + 6..];
        let Some(end) = rest.find("/>") else { break };
        let tag = &rest[..end];
        rest = &rest[end + 2..];
        if ["pcbPath", "pcbComb", "pcbStraightLine"]
            .iter()
            .any(|p| tag.contains(p))
        {
            if let (Some(a), Some(b)) = (attribute(tag, "from"), attribute(tag, "to")) {
                authored.insert(pair(a, b));
            }
        }
    }
    let source = circuit
        .elements
        .iter()
        .filter_map(|e| {
            if let Element::SourceTrace(t) = e {
                Some((t.source_trace_id.as_str(), t))
            } else {
                None
            }
        })
        .collect::<BTreeMap<_, _>>();
    let names = circuit.names();
    let nets = circuit.nets();
    let mut traces = vec![];
    let mut obstacles = vec![];
    for e in &circuit.elements {
        match e {
            Element::Trace(trace) => {
                let source = source.get(trace.source_trace_id.as_str());
                let display = source
                    .map(|s| s.display_name.clone())
                    .filter(|s| !s.is_empty())
                    .unwrap_or_else(|| trace.source_trace_id.clone());
                let key = source
                    .and_then(|s| s.subcircuit_connectivity_map_key.clone())
                    .unwrap_or_else(|| display.clone());
                let auth = display
                    .split_once(" to ")
                    .is_some_and(|(a, b)| authored.contains(&pair(a, b)));
                let mut segments = vec![];
                for p in trace.route.windows(2) {
                    let (Some(a), Some(b)) = (p[0].point(), p[1].point()) else {
                        continue;
                    };
                    if a.x == b.x && a.y == b.y {
                        continue;
                    }
                    let layer = if p[0].route_type.as_deref() == Some("via") {
                        p[0].to_layer.clone()
                    } else if p[1].route_type.as_deref() == Some("via") {
                        p[1].from_layer.clone()
                    } else if p[0].layer == p[1].layer {
                        p[0].layer.clone()
                    } else {
                        None
                    };
                    if let Some(layer) = layer {
                        segments.push(TraceSegment {
                            line: (a, b),
                            layer,
                            width: p[0].width,
                        });
                    }
                }
                traces.push(Trace {
                    display,
                    key,
                    authored: auth,
                    segments,
                });
            }
            Element::SmtPad(p) => obstacles.push(Obstacle {
                name: format!(
                    "{}.{}",
                    names.get(&p.pcb_component_id).map_or("?", String::as_str),
                    p.port_hints.first().map_or("?", String::as_str)
                ),
                point: p.point(),
                half: [p.width.unwrap_or(0.0) / 2.0, p.height.unwrap_or(0.0) / 2.0],
                rotation: p.ccw_rotation.unwrap_or(0.0),
                layers: vec![p.layer.clone().unwrap_or_default()],
                net: nets.get(&p.pcb_port_id).cloned(),
            }),
            Element::PlatedHole(p) | Element::Via(p) => {
                let via = matches!(e, Element::Via(_));
                let r = p.outer_diameter.unwrap_or_else(|| {
                    if via {
                        0.5
                    } else {
                        p.radius.unwrap_or(0.5) * 2.0
                    }
                }) / 2.0;
                obstacles.push(Obstacle {
                    name: if via {
                        "via".into()
                    } else {
                        format!(
                            "{}.{}",
                            names.get(&p.pcb_component_id).map_or("?", String::as_str),
                            p.port_hints.first().map_or("?", String::as_str)
                        )
                    },
                    point: p.point(),
                    half: [r, r],
                    rotation: 0.0,
                    layers: if via {
                        vec!["top", "bottom", "inner1", "inner2", "inner3", "inner4"]
                    } else {
                        vec!["top", "bottom", "inner1", "inner2"]
                    }
                    .into_iter()
                    .map(str::to_owned)
                    .collect(),
                    net: if via {
                        p.subcircuit_connectivity_map_key.clone()
                    } else {
                        nets.get(&p.pcb_port_id).cloned()
                    },
                });
            }
            _ => {}
        }
    }
    Ok((traces, obstacles))
}
pub fn trace_check(args: &[String]) -> Result<()> {
    ensure!(
        args.len() >= 2,
        "trace-check CIRCUIT.json SOURCE.tsx [--region X0 X1 Y0 Y1] [--net TEXT] [--floor MM]"
    );
    let mut region = None;
    let mut net = None;
    let mut floor = 0.14;
    let mut index = 2;
    while index < args.len() {
        match args[index].as_str() {
            "--region" => {
                ensure!(index + 4 < args.len(), "--region requires board bounds");
                let mut values = [0.0; 4];
                for i in 0..4 {
                    values[i] = args[index + i + 1].parse::<f64>()?;
                }
                region = Some(values);
                index += 5;
            }
            "--net" => {
                net = Some(
                    args.get(index + 1)
                        .context("--net requires text")?
                        .replace(' ', ""),
                );
                index += 2;
            }
            "--floor" => {
                floor = args
                    .get(index + 1)
                    .context("--floor requires a distance")?
                    .parse::<f64>()?;
                index += 2;
            }
            other => bail!("unknown option {other}"),
        }
    }
    let circuit = Circuit::load(Path::new(&args[0]))?;
    let (traces, pads) = traces(&circuit, Path::new(&args[1]))?;
    let in_region = |segment: &TraceSegment| {
        region.is_none_or(|[x0, x1, y0, y1]| {
            let (a, b) = segment.line;
            !(a.x.max(b.x) < x0.min(x1)
                || a.x.min(b.x) > x0.max(x1)
                || a.y.max(b.y) < y0.min(y1)
                || a.y.min(b.y) > y0.max(y1))
        })
    };
    let focus = traces
        .iter()
        .enumerate()
        .filter(|(_, t)| {
            net.as_ref().map_or_else(
                || t.authored && t.segments.iter().any(&in_region),
                |needle| t.display.replace(' ', "").contains(needle),
            )
        })
        .collect::<Vec<_>>();
    if focus.is_empty() {
        println!("no matching hand traces");
        return Ok(());
    }
    struct Finding<'a> {
        gap: f64,
        trace: &'a Trace,
        segment: &'a TraceSegment,
        other: String,
        class: &'static str,
        point: Point,
    }
    let mut findings = vec![];
    for (index, trace) in &focus {
        for segment in &trace.segments {
            if !in_region(segment) {
                continue;
            }
            let (a, b) = segment.line;
            for (other_index, other) in traces.iter().enumerate() {
                if *index == other_index || trace.key == other.key {
                    continue;
                }
                for target in &other.segments {
                    if segment.layer != target.layer {
                        continue;
                    }
                    let (distance, point) =
                        geometry::segment_distance(a, b, target.line.0, target.line.1);
                    let gap = distance - segment.width / 2.0 - target.width / 2.0;
                    if gap < floor {
                        findings.push(Finding {
                            gap,
                            trace,
                            segment,
                            other: other.display.clone(),
                            class: if other.authored { "hand" } else { "AUTO" },
                            point,
                        });
                    }
                }
            }
            for pad in &pads {
                if pad.net.as_ref() == Some(&trace.key) {
                    continue;
                }
                let gap = geometry::rect_distance(a, b, pad.point, pad.half, pad.rotation)
                    - segment.width / 2.0;
                if gap < floor {
                    findings.push(Finding {
                        gap,
                        trace,
                        segment,
                        other: format!("pad {}", pad.name),
                        class: if pad.layers.contains(&segment.layer) {
                            "pad"
                        } else {
                            "shadow"
                        },
                        point: pad.point,
                    });
                }
            }
        }
    }
    findings.sort_by(|a, b| a.gap.total_cmp(&b.gap));
    println!(
        "# {} hand trace(s) in filter; floor {floor} mm\n",
        focus.len()
    );
    let mut groups = BTreeMap::<(String, &str), (f64, usize)>::new();
    for finding in findings {
        let (a, b) = finding.segment.line;
        println!(
            "{:+0.3}mm  MINE [{}] seg ({:.2},{:.2})->({:.2},{:.2}) {}\n          x {} [{}] @({:.2},{:.2})",
            finding.gap,
            finding.trace.display,
            a.x,
            a.y,
            b.x,
            b.y,
            finding.segment.layer,
            finding.class,
            finding.other,
            finding.point.x,
            finding.point.y
        );
        let entry = groups
            .entry((finding.other, finding.class))
            .or_insert((f64::INFINITY, 0));
        entry.0 = entry.0.min(finding.gap);
        entry.1 += 1;
    }
    println!("\n# by other party:");
    let mut groups = groups.into_iter().collect::<Vec<_>>();
    groups.sort_by(|a, b| a.1 .0.total_cmp(&b.1 .0));
    for ((name, class), (worst, count)) in groups {
        let verdict = match class {
            "AUTO" => "EVICT its net",
            "hand" => "fix your trace",
            "shadow" => "leave its column — pad projects through the stack",
            _ => "nudge off pad",
        };
        println!("  {worst:+0.3}mm x{count} [{name}] ({class}) -> {verdict}");
    }
    Ok(())
}

const RES: f64 = 0.08;
const HALF: f64 = 0.10;
const RADIUS: f64 = 0.16 + HALF;
struct Raster {
    nx: usize,
    ny: usize,
    origin: Point,
    blocked: Vec<bool>,
}
impl Raster {
    fn world(&self, c: usize, r: usize) -> Point {
        Point {
            x: self.origin.x + c as f64 * RES,
            y: self.origin.y + r as f64 * RES,
        }
    }
    fn pixel(&self, p: Point) -> Point {
        Point {
            x: (p.x - self.origin.x) / RES,
            y: (p.y - self.origin.y) / RES,
        }
    }
    fn fill(&mut self, bounds: [f64; 4], inside: impl Fn(Point) -> bool) {
        let origin = self.origin;
        self.fill_pixels(bounds, |c, r| {
            inside(Point {
                x: origin.x + c as f64 * RES,
                y: origin.y + r as f64 * RES,
            })
        });
    }
    fn fill_pixels(&mut self, bounds: [f64; 4], inside: impl Fn(usize, usize) -> bool) {
        let a = self.pixel(Point {
            x: bounds[0],
            y: bounds[2],
        });
        let b = self.pixel(Point {
            x: bounds[1],
            y: bounds[3],
        });
        let lowx = (a.x.floor() as isize).max(0) as usize;
        let lowy = (a.y.floor() as isize).max(0) as usize;
        let highx = (b.x.ceil() as usize + 1).min(self.nx);
        let highy = (b.y.ceil() as usize + 1).min(self.ny);
        for r in lowy..highy {
            for c in lowx..highx {
                if inside(c, r) {
                    self.blocked[r * self.nx + c] = true;
                }
            }
        }
    }
    fn rect(&mut self, p: Point, half: [f64; 2], rotation: f64) {
        let (sin, cos) = rotation.to_radians().sin_cos();
        let radius = half[0].hypot(half[1]);
        let center = self.pixel(p);
        self.fill_pixels(
            [p.x - radius, p.x + radius, p.y - radius, p.y + radius],
            |c, r| {
                let (x, y) = ((c as f64 - center.x) * RES, (r as f64 - center.y) * RES);
                (cos * x + sin * y).abs() <= half[0] && (-sin * x + cos * y).abs() <= half[1]
            },
        );
    }
    fn circle(&mut self, p: Point, r: f64) {
        let center = self.pixel(p);
        self.fill_pixels([p.x - r, p.x + r, p.y - r, p.y + r], |c, row| {
            let (x, y) = ((c as f64 - center.x) * RES, (row as f64 - center.y) * RES);
            x * x + y * y <= r * r
        });
    }
    fn capsule(&mut self, a: Point, b: Point, width: f64) {
        let r = width / 2.0;
        let (ca, cb) = (self.pixel(a), self.pixel(b));
        let (vx, vy) = ((cb.x - ca.x) * RES, (cb.y - ca.y) * RES);
        let length = vx * vx + vy * vy;
        self.fill_pixels(
            [
                a.x.min(b.x) - r,
                a.x.max(b.x) + r,
                a.y.min(b.y) - r,
                a.y.max(b.y) + r,
            ],
            |col, row| {
                let (x, y) = ((col as f64 - ca.x) * RES, (row as f64 - ca.y) * RES);
                let t = if length > 0.0 {
                    ((x * vx + y * vy) / length).clamp(0.0, 1.0)
                } else {
                    0.0
                };
                let (dx, dy) = (x - t * vx, y - t * vy);
                dx * dx + dy * dy <= r * r
            },
        );
    }
    fn polygon(&mut self, points: &[Point]) {
        if points.len() < 3 {
            return;
        }
        let mut bounds = [
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
        ];
        for p in points {
            bounds[0] = bounds[0].min(p.x);
            bounds[1] = bounds[1].max(p.x);
            bounds[2] = bounds[2].min(p.y);
            bounds[3] = bounds[3].max(p.y);
        }
        self.fill(bounds, |p| {
            let mut inside = false;
            for i in 0..points.len() {
                let (a, b) = (points[i], points[(i + 1) % points.len()]);
                if (a.y > p.y) != (b.y > p.y)
                    && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y + 1e-30) + a.x
                {
                    inside = !inside;
                }
            }
            inside
        });
    }
    fn pad_pixels(&self, p: &Pad, minimum: f64) -> Vec<usize> {
        let c = self.pixel(p.point());
        let w = p
            .width
            .or(p.outer_width)
            .or(p.outer_diameter)
            .unwrap_or_else(|| p.radius.unwrap_or(0.25) * 2.0);
        let h = p
            .height
            .or(p.outer_height)
            .or(p.outer_diameter)
            .unwrap_or(w);
        let (hw, hh) = (w.max(minimum) / 2.0 / RES, h.max(minimum) / 2.0 / RES);
        let mut out = vec![];
        for r in ((c.y - hh) as isize).max(0) as usize..((c.y + hh) as usize + 1).min(self.ny) {
            for col in ((c.x - hw) as isize).max(0) as usize..((c.x + hw) as usize + 1).min(self.nx)
            {
                out.push(r * self.nx + col);
            }
        }
        out
    }
}
pub fn topreach(args: &[String]) -> Result<()> {
    ensure!(
        args.len() >= 3,
        "topreach CIRCUIT.json COMPONENT.pin COMPONENT.pin [--png PATH]"
    );
    let png = if args.len() == 5 && args[3] == "--png" {
        Some(PathBuf::from(&args[4]))
    } else {
        ensure!(args.len() == 3, "unknown topreach options");
        None
    };
    let circuit = Circuit::load(Path::new(&args[0]))?;
    let board = circuit.board()?;
    let ai = circuit.named_pad(&args[1])?;
    let bi = circuit.named_pad(&args[2])?;
    let pad = |index| match &circuit.elements[index] {
        Element::SmtPad(p) | Element::PlatedHole(p) => p,
        _ => unreachable!(),
    };
    let (pa, pb) = (pad(ai), pad(bi));
    let nets = circuit.nets();
    let exclude = [nets.get(&pa.pcb_port_id), nets.get(&pb.pcb_port_id)]
        .into_iter()
        .flatten()
        .collect::<BTreeSet<_>>();
    let skip = |p: &Pad| {
        nets.get(&p.pcb_port_id)
            .is_some_and(|key| exclude.contains(key))
    };
    let outline = if board.outline.len() >= 3 {
        board.outline.clone()
    } else {
        vec![
            Point {
                x: board.center.x - board.width / 2.0,
                y: board.center.y - board.height / 2.0,
            },
            Point {
                x: board.center.x + board.width / 2.0,
                y: board.center.y - board.height / 2.0,
            },
            Point {
                x: board.center.x + board.width / 2.0,
                y: board.center.y + board.height / 2.0,
            },
            Point {
                x: board.center.x - board.width / 2.0,
                y: board.center.y + board.height / 2.0,
            },
        ]
    };
    let bounds = outline.iter().fold(
        [
            f64::INFINITY,
            f64::NEG_INFINITY,
            f64::INFINITY,
            f64::NEG_INFINITY,
        ],
        |mut bounds, p| {
            bounds[0] = bounds[0].min(p.x);
            bounds[1] = bounds[1].max(p.x);
            bounds[2] = bounds[2].min(p.y);
            bounds[3] = bounds[3].max(p.y);
            bounds
        },
    );
    let (nx, ny) = (
        ((bounds[1] - bounds[0]) / RES).ceil() as usize + 1,
        ((bounds[3] - bounds[2]) / RES).ceil() as usize + 1,
    );
    let mut raster = Raster {
        nx,
        ny,
        origin: Point {
            x: bounds[0],
            y: bounds[2],
        },
        blocked: vec![false; nx * ny],
    };
    for (index, e) in circuit.elements.iter().enumerate() {
        match e {
            Element::SmtPad(p) => {
                if index == ai || index == bi || skip(p) || p.layer.as_deref() != Some("top") {
                    continue;
                }
                raster.rect(
                    p.point(),
                    [
                        p.width.unwrap_or(p.radius.unwrap_or(0.0) * 2.0) / 2.0,
                        p.height.unwrap_or(p.radius.unwrap_or(0.0) * 2.0) / 2.0,
                    ],
                    p.ccw_rotation.unwrap_or(0.0),
                );
            }
            Element::PlatedHole(p) => {
                if index == ai || index == bi || skip(p) {
                    continue;
                }
                let w = p
                    .outer_width
                    .or(p.outer_diameter)
                    .or(p.hole_diameter)
                    .unwrap_or(0.5);
                let h = p
                    .outer_height
                    .or(p.outer_diameter)
                    .or(p.hole_diameter)
                    .unwrap_or(w);
                raster.rect(p.point(), [w / 2.0, h / 2.0], 0.0);
            }
            Element::Via(p) => raster.circle(p.point(), p.outer_diameter.unwrap_or(0.5) / 2.0),
            Element::Trace(t) => {
                for p in t.route.windows(2) {
                    if p[0].route_type.as_deref() == Some("via")
                        || p[1].route_type.as_deref() == Some("via")
                        || p[0].layer.as_deref() != Some("top")
                        || p[1].layer.as_deref() != Some("top")
                    {
                        continue;
                    }
                    if let (Some(a), Some(b)) = (p[0].point(), p[1].point()) {
                        raster.capsule(a, b, p[0].width);
                    }
                }
            }
            Element::Pour(p) if p.layer == "top" => {
                if p.polygons.is_empty() {
                    raster.polygon(&p.outline);
                } else {
                    for poly in &p.polygons {
                        raster.polygon(if poly.points.is_empty() {
                            &poly.vertices
                        } else {
                            &poly.points
                        });
                    }
                }
            }
            _ => {}
        }
    }
    let radius = (RADIUS / RES).ceil() as isize;
    let mut offsets = vec![];
    for dr in -radius..=radius {
        for dc in -radius..=radius {
            if (dc * dc + dr * dr) as f64 * RES * RES <= RADIUS * RADIUS {
                offsets.push((dr, dc));
            }
        }
    }
    let mut blocked = vec![false; nx * ny];
    for r in 0..ny {
        for c in 0..nx {
            if raster.blocked[r * nx + c] {
                for (dr, dc) in &offsets {
                    let (rr, cc) = (r as isize + dr, c as isize + dc);
                    if rr >= 0 && rr < ny as isize && cc >= 0 && cc < nx as isize {
                        blocked[rr as usize * nx + cc as usize] = true;
                    }
                }
            }
        }
    }
    let free = (0..nx * ny)
        .map(|i| {
            let (r, c) = (i / nx, i % nx);
            let p = raster.world(c, r);
            let mut inside = false;
            for index in 0..outline.len() {
                let (a, b) = (outline[index], outline[(index + 1) % outline.len()]);
                if geometry::point_segment(p, a, b).0 < HALF {
                    return false;
                }
                if (a.y > p.y) != (b.y > p.y)
                    && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y + 1e-30) + a.x
                {
                    inside = !inside;
                }
            }
            inside && !blocked[i]
        })
        .collect::<Vec<_>>();
    let mut labels = vec![0u32; nx * ny];
    let mut next = 0u32;
    for seed in 0..free.len() {
        if !free[seed] || labels[seed] != 0 {
            continue;
        }
        next += 1;
        labels[seed] = next;
        let mut queue = VecDeque::from([seed]);
        while let Some(i) = queue.pop_front() {
            let (r, c) = (i / nx, i % nx);
            for (dr, dc) in [(1, 0), (-1, 0), (0, 1), (0, -1)] {
                let (rr, cc) = (r as isize + dr, c as isize + dc);
                if rr >= 0 && rr < ny as isize && cc >= 0 && cc < nx as isize {
                    let j = rr as usize * nx + cc as usize;
                    if free[j] && labels[j] == 0 {
                        labels[j] = next;
                        queue.push_back(j);
                    }
                }
            }
        }
    }
    let pad_labels = |p| {
        raster
            .pad_pixels(p, 0.4)
            .into_iter()
            .map(|i| labels[i])
            .filter(|v| *v != 0)
            .collect::<BTreeSet<_>>()
    };
    let (la, lb) = (pad_labels(pa), pad_labels(pb));
    let shared = la.intersection(&lb).copied().collect::<BTreeSet<_>>();
    println!(
        "{} free-components at pad: {la:?}\n{} free-components at pad: {lb:?}\n\nTOP {} — shared components {shared:?}",
        args[1],
        args[2],
        if shared.is_empty() {
            "BLOCKED"
        } else {
            "ROUTABLE"
        }
    );
    let mut thread = vec![];
    if !shared.is_empty() {
        let seeds = raster
            .pad_pixels(pa, 0.5)
            .into_iter()
            .filter(|i| free[*i] && shared.contains(&labels[*i]))
            .collect::<Vec<_>>();
        let goals = raster
            .pad_pixels(pb, 0.5)
            .into_iter()
            .filter(|i| free[*i] && shared.contains(&labels[*i]))
            .collect::<BTreeSet<_>>();
        let mut previous = vec![usize::MAX; free.len()];
        let mut queue = VecDeque::new();
        for seed in seeds {
            previous[seed] = seed;
            queue.push_back(seed);
        }
        while let Some(i) = queue.pop_front() {
            if goals.contains(&i) {
                let mut at = i;
                thread.push(at);
                while previous[at] != at {
                    at = previous[at];
                    thread.push(at);
                }
                thread.reverse();
                break;
            }
            let (r, c) = (i / nx, i % nx);
            for (dr, dc) in [
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
                (1, 1),
                (1, -1),
                (-1, 1),
                (-1, -1),
            ] {
                let (rr, cc) = (r as isize + dr, c as isize + dc);
                if rr >= 0 && rr < ny as isize && cc >= 0 && cc < nx as isize {
                    let j = rr as usize * nx + cc as usize;
                    if free[j] && previous[j] == usize::MAX {
                        previous[j] = i;
                        queue.push_back(j);
                    }
                }
            }
        }
        if !thread.is_empty() {
            let step = (2.0 / RES) as usize;
            let mut sampled = thread.iter().step_by(step).copied().collect::<Vec<_>>();
            sampled.push(*thread.last().unwrap());
            println!(
                "thread (mm, approximate samples):\n  {}",
                sampled
                    .into_iter()
                    .map(|i| {
                        let p = raster.world(i % nx, i / nx);
                        format!("({:.2},{:.2})", p.x, p.y)
                    })
                    .collect::<Vec<_>>()
                    .join(" -> ")
            );
        }
    }
    if let Some(path) = png {
        let mut pixels = vec![0u8; nx * ny * 3];
        for i in 0..free.len() {
            let mut color = if blocked[i] {
                [60, 60, 60]
            } else if free[i] {
                [20, 60, 20]
            } else {
                [0, 0, 0]
            };
            if la.contains(&labels[i]) {
                color = [0, 200, 255];
            }
            if lb.contains(&labels[i]) {
                color = [255, 200, 0];
            }
            let out = ((ny - 1 - i / nx) * nx + i % nx) * 3;
            pixels[out..out + 3].copy_from_slice(&color);
        }
        for i in &thread {
            for dr in -1isize..=1 {
                for dc in -1isize..=1 {
                    let (r, c) = ((*i / nx) as isize + dr, (*i % nx) as isize + dc);
                    if r >= 0 && r < ny as isize && c >= 0 && c < nx as isize {
                        let at = ((ny - 1 - r as usize) * nx + c as usize) * 3;
                        pixels[at..at + 3].copy_from_slice(&[255, 0, 255]);
                    }
                }
            }
        }
        if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
            fs::create_dir_all(parent)?;
        }
        let mut encoder = png::Encoder::new(fs::File::create(&path)?, nx as u32, ny as u32);
        encoder.set_color(png::ColorType::Rgb);
        encoder.set_depth(png::BitDepth::Eight);
        encoder.write_header()?.write_image_data(&pixels)?;
        println!("wrote {}", path.display());
    }
    Ok(())
}

fn escape(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}
pub fn plot(args: &[String]) -> Result<()> {
    let path = args
        .iter()
        .find(|v| v.ends_with(".json"))
        .map_or("out/pcba.circuit.json", String::as_str);
    let output = args
        .iter()
        .find(|v| v.ends_with(".png"))
        .map_or("/tmp/region.png", String::as_str);
    let numbers = args
        .iter()
        .filter_map(|v| v.parse::<f64>().ok())
        .collect::<Vec<_>>();
    ensure!(
        numbers.len() >= 4,
        "plot-region [CIRCUIT.json] X0 X1 Y0 Y1 [OUTPUT.png]"
    );
    let [x0, x1, y0, y1] = numbers[..4].try_into()?;
    let scale = 60.0;
    let (width, height) = (((x1 - x0) * scale) as usize, ((y1 - y0) * scale) as usize);
    ensure!(
        width > 0 && height > 0,
        "region must have positive width and height"
    );
    let p = |p: Point| Point {
        x: (p.x - x0) * scale,
        y: (y1 - p.y) * scale,
    };
    let mut svg = format!(
        "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\"><rect width=\"100%\" height=\"100%\" fill=\"#121216\"/><g font-family=\"Arial\" font-size=\"13\">"
    );
    for gx in x0.ceil() as i64..=x1.floor() as i64 {
        let x = (gx as f64 - x0) * scale;
        write!(
            svg,
            "<path d=\"M{x},0V{height}\" stroke=\"{}\"/>",
            if gx % 5 == 0 { "#37373e" } else { "#202026" }
        )?;
        if gx % 2 == 0 {
            write!(
                svg,
                "<text x=\"{}\" y=\"{}\" fill=\"#787882\">{gx}</text>",
                x + 1.0,
                height as f64 - 2.0
            )?;
        }
    }
    for gy in y0.ceil() as i64..=y1.floor() as i64 {
        let y = (y1 - gy as f64) * scale;
        write!(
            svg,
            "<path d=\"M0,{y}H{width}\" stroke=\"{}\"/>",
            if gy % 5 == 0 { "#37373e" } else { "#202026" }
        )?;
        if gy % 2 == 0 {
            write!(
                svg,
                "<text x=\"2\" y=\"{}\" fill=\"#787882\">{gy}</text>",
                y + 5.0
            )?;
        }
    }
    let circuit = Circuit::load(Path::new(path))?;
    let names = circuit.names();
    for e in &circuit.elements {
        if let Element::SmtPad(pad) | Element::PlatedHole(pad) = e {
            let center = p(pad.point());
            if pad.x < x0 - 1.0 || pad.x > x1 + 1.0 || pad.y < y0 - 1.0 || pad.y > y1 + 1.0 {
                continue;
            }
            if matches!(e, Element::PlatedHole(_)) {
                write!(
                    svg,
                    "<circle cx=\"{}\" cy=\"{}\" r=\"{}\" fill=\"none\" stroke=\"#d2c878\" stroke-width=\"2\"/>",
                    center.x,
                    center.y,
                    pad.outer_diameter.unwrap_or(1.0) / 2.0 * scale
                )?;
            } else {
                let (w, h) = (
                    pad.width.unwrap_or(0.5) * scale,
                    pad.height.unwrap_or(0.5) * scale,
                );
                write!(
                    svg,
                    "<rect x=\"{}\" y=\"{}\" width=\"{w}\" height=\"{h}\" fill=\"#3c3a28\" stroke=\"#d2c878\" transform=\"rotate({} {} {})\"/>",
                    center.x - w / 2.0,
                    center.y - h / 2.0,
                    -pad.ccw_rotation.unwrap_or(0.0),
                    center.x,
                    center.y
                )?;
            }
            if let Some(hint) = pad.port_hints.first().filter(|v| !v.is_empty()) {
                write!(
                    svg,
                    "<text x=\"{}\" y=\"{}\" fill=\"#e6dca0\">{}.{}</text>",
                    center.x + 2.0,
                    center.y + 6.0,
                    escape(names.get(&pad.pcb_component_id).map_or("?", String::as_str)),
                    escape(hint)
                )?;
            }
        }
    }
    for e in &circuit.elements {
        if let Element::Trace(trace) = e {
            for points in trace.route.windows(2) {
                if let (Some(a), Some(b)) = (points[0].point(), points[1].point()) {
                    let (a, b) = (p(a), p(b));
                    let color = match points[0]
                        .layer
                        .as_deref()
                        .or(points[1].layer.as_deref())
                        .unwrap_or("top")
                    {
                        "top" => "#eb463c",
                        "bottom" => "#4678eb",
                        "inner1" => "#3cbea5",
                        "inner2" => "#e1963c",
                        _ => "#969696",
                    };
                    write!(
                        svg,
                        "<path d=\"M{},{}L{},{}\" stroke=\"{color}\" stroke-width=\"12\"/>",
                        a.x, a.y, b.x, b.y
                    )?;
                }
            }
        }
    }
    for e in &circuit.elements {
        if let Element::Via(pad) = e {
            if pad.x >= x0 && pad.x <= x1 && pad.y >= y0 && pad.y <= y1 {
                let center = p(pad.point());
                write!(
                    svg,
                    "<circle cx=\"{}\" cy=\"{}\" r=\"{}\" fill=\"#1ec878\" stroke=\"white\"/>",
                    center.x,
                    center.y,
                    pad.outer_diameter.unwrap_or(0.5) / 2.0 * scale
                )?;
            }
        }
    }
    svg.push_str("</g></svg>");
    let temp = std::env::temp_dir().join(format!("hsm-pcb-region-{}.svg", std::process::id()));
    fs::write(&temp, svg)?;
    let result = crate::output(
        Command::new("rsvg-convert")
            .arg("--output")
            .arg(output)
            .arg(&temp),
    );
    let _ = fs::remove_file(temp);
    result?;
    println!("wrote {output} box x[{x0},{x1}] y[{y0},{y1}] {width}x{height}px");
    Ok(())
}
