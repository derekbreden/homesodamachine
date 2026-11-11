//! Replaces the faucet base’s first suspended outer wall with matching arcs along its tilted rim.

use std::{
    collections::BTreeMap,
    env, fs,
    io::{self, BufWriter, Write},
    path::Path,
};

const BEAD_WIDTH: f64 = 0.44;
const COURSE_HEIGHT: f64 = 0.23;
const MIN_JOIN_HEIGHT: f64 = 0.09;
const FIRST_LAYER_Z: f64 = 0.2;
const LAYER_HEIGHT: f64 = 0.24;
const FILAMENT_RADIUS: f64 = 0.875;
const TRAVEL_CLEARANCE: f64 = 0.40;
const PATH_STEP: f64 = 0.22;
const CONTACT_FEED: f64 = 900.;
const BED_BLEND_END: f64 = 4.0;
const PI: f64 = std::f64::consts::PI;
type Point = [f64; 3];

/// The rim’s center in print coordinates and semi-axes in its own seat plane.
/// A positive fall angle puts the positive seat Y edge closer to the bed.
#[derive(Clone, Copy, Debug)]
pub struct RimSpec {
    pub identify_id: u64,
    pub center_mm: [f64; 3],
    pub seat_fall_angle_degrees: f64,
    pub semi_axes_mm: [f64; 2],
    pub supported_angles_degrees: [f64; 2],
}

#[derive(Clone, Copy, Debug)]
pub struct ContourReport {
    pub arc_count: usize,
    pub emitted_contact_segments: usize,
    pub modified_native_paths: usize,
    pub extrusion_added_mm: f64,
    pub extrusion_removed_mm: f64,
    pub estimated_motion_delta_seconds: f64,
    pub maximum_contact_depth_below_prior_peak_mm: f64,
    pub minimum_contact_z_mm: f64,
}

/// Applies the first perimeter to G-code restored from the faucet contact-band map.
/// The native body uses absolute XYZ and relative extrusion. The caller supplies
/// the bounds of the rim with a support roof and keeps the resulting executable.
pub fn apply(input: &Path, output: &Path, spec: RimSpec) -> io::Result<ContourReport> {
    let [start, end] = spec.supported_angles_degrees;
    let (sin, cos) = spec.seat_fall_angle_degrees.to_radians().sin_cos();
    if spec.identify_id == 0
        || !spec.center_mm.iter().all(|v| v.is_finite())
        || !(0. ..90.).contains(&spec.seat_fall_angle_degrees)
        || spec
            .semi_axes_mm
            .iter()
            .any(|r| !r.is_finite() || *r <= BEAD_WIDTH)
        || !(0. < end - start && end - start <= 360.)
    {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "expected a native object identity, finite seat frame, and a supported angular interval",
        ));
    }
    let rim = Rim {
        center: spec.center_mm,
        sin,
        cos,
        radii: spec.semi_axes_mm,
        start,
        end,
        object: spec.identify_id,
    };
    build(input, output, &rim)
}

fn distance(a: Point, b: Point) -> f64 {
    (b[0] - a[0]).hypot(b[1] - a[1]).hypot(b[2] - a[2])
}

fn lerp(a: Point, b: Point, t: f64) -> Point {
    std::array::from_fn(|i| a[i] + (b[i] - a[i]) * t)
}

struct Rim {
    center: Point,
    // The print pose rotates the seat around the plate's X axis.
    sin: f64,
    cos: f64,
    radii: [f64; 2],
    start: f64,
    end: f64,
    object: u64,
}

impl Rim {
    fn local(&self, p: Point) -> (f64, f64, f64) {
        let [x, y, z] = std::array::from_fn(|i| p[i] - self.center[i]);
        let along = y * self.cos - z * self.sin;
        let height = z + y * self.sin / self.cos;
        let nx = x / self.radii[0];
        let ny = along / self.radii[1];
        let angle = (ny.atan2(nx).to_degrees() - self.start).rem_euclid(360.) + self.start;
        let radial_offset = x.hypot(along)
            - (self.radii[0] * angle.to_radians().cos())
                .hypot(self.radii[1] * angle.to_radians().sin());
        (radial_offset, angle, height)
    }

    fn contour(&self, angle: f64, height: f64) -> Point {
        let (sin, cos) = angle.to_radians().sin_cos();
        let normal = height * self.cos;
        [
            self.center[0] + (self.radii[0] - BEAD_WIDTH / 2.) * cos,
            self.center[1] + (self.radii[1] - BEAD_WIDTH / 2.) * sin * self.cos + normal * self.sin,
            self.center[2] - (self.radii[1] - BEAD_WIDTH / 2.) * sin * self.sin + normal * self.cos,
        ]
    }
}

fn smooth(t: f64) -> f64 {
    let t = t.clamp(0., 1.);
    t * t * (3. - 2. * t)
}

fn nominal_z(rim: &Rim, p: Point) -> f64 {
    let (_, _, depth) = rim.local(p);
    let face = p[2] - depth;
    let period = 1.92;
    let phase = 0.2;
    let r = (face - phase + period / 2.).rem_euclid(period) - period / 2.;
    let delta = if r.abs() <= period / 4. {
        r
    } else {
        r.signum() * (period / 2. - r.abs())
    };
    let weight = if depth < -1.5 {
        smooth((depth + 4.5) / 3.)
    } else {
        1. - smooth((depth - 1.) / 3.)
    };
    p[2] - delta * smooth((p[2] - 0.44) / (BED_BLEND_END - 0.44)) * weight
}

fn baseline_thickness(rim: &Rim, p: Point, layer: usize, height: f64) -> f64 {
    let mut below = p;
    if layer <= 2 {
        return if layer == 1 { FIRST_LAYER_Z } else { height };
    }
    let target = nominal_z(rim, p) - height;
    for _ in 0..12 {
        below[2] += target - nominal_z(rim, below);
    }
    p[2] - below[2]
}

fn layer_at(rim: &Rim, planes: &[(usize, f64)], angle: f64) -> usize {
    let plane = nominal_z(rim, rim.contour(angle, COURSE_HEIGHT));
    let bucket = planes
        .partition_point(|&(_, z)| z <= plane + 1e-7)
        .saturating_sub(1);
    planes[bucket].0
}

struct Arc {
    from: f64,
    to: f64,
}

fn arcs_by_layer(rim: &Rim, planes: &[(usize, f64)]) -> BTreeMap<usize, Vec<Arc>> {
    let mut layers = BTreeMap::<usize, Vec<Arc>>::new();
    let samples = ((rim.end - rim.start).to_radians() * rim.radii[0].max(rim.radii[1]) / PATH_STEP)
        .ceil() as usize;
    let mut start = rim.start;
    let mut previous = start;
    let mut layer = layer_at(rim, planes, start);
    for i in 1..=samples {
        let angle = rim.start + (rim.end - rim.start) * i as f64 / samples as f64;
        let next = layer_at(rim, planes, angle);
        if next != layer {
            let (mut lo, mut hi) = (previous, angle);
            for _ in 0..32 {
                let mid = (lo + hi) * 0.5;
                if layer_at(rim, planes, mid) == layer {
                    lo = mid;
                } else {
                    hi = mid;
                }
            }
            let boundary = (lo + hi) * 0.5;
            layers.entry(layer).or_default().push(Arc {
                from: start,
                to: boundary,
            });
            start = boundary;
            layer = next;
        }
        previous = angle;
    }
    if rim.end > start {
        layers.entry(layer).or_default().push(Arc {
            from: start,
            to: rim.end,
        });
    }
    for arcs in layers.values_mut() {
        arcs.sort_by(|a, b| {
            let low = |arc: &Arc| {
                rim.contour(arc.from, COURSE_HEIGHT)[2].min(rim.contour(arc.to, COURSE_HEIGHT)[2])
            };
            low(a).total_cmp(&low(b))
        });
    }
    layers
}

#[derive(Clone, Copy, Default)]
struct Words {
    xyz: [Option<f64>; 3],
    e: Option<f64>,
    f: Option<f64>,
    fan: Option<f64>,
}

fn words(line: &str) -> Words {
    let mut result = Words::default();
    for token in line.split(';').next().unwrap().split_whitespace().skip(1) {
        if token.len() < 2 {
            continue;
        }
        let value = token[1..].parse::<f64>().ok();
        match token.as_bytes()[0] {
            b'X' => result.xyz[0] = value,
            b'Y' => result.xyz[1] = value,
            b'Z' => result.xyz[2] = value,
            b'E' => result.e = value,
            b'F' => result.f = value,
            b'S' => result.fan = value,
            _ => {}
        }
    }
    result
}

fn is_support(feature: &str) -> bool {
    matches!(
        feature,
        "Support" | "Support interface" | "Support transition"
    )
}

fn is_rim_feature(feature: &str) -> bool {
    matches!(
        feature,
        "Outer wall"
            | "Overhang wall"
            | "Inner wall"
            | "Floating vertical shell"
            | "Internal solid infill"
            | "Gap infill"
    )
}

fn lateral(a: Point, b: Point) -> f64 {
    (b[0] - a[0]).hypot(b[1] - a[1])
}

fn volume_per_mm(width: f64, height: f64) -> f64 {
    height * (width - height * (1. - PI / 4.)) / (PI * FILAMENT_RADIUS.powi(2))
}

fn remnant_flow(rim: &Rim, p: Point, width: f64, layer: usize, height: f64) -> f64 {
    let (offset, angle, depth) = rim.local(p);
    // An under-running fill end needs more lateral room beside the completed first course.
    let inner_limit = if rim.contour(angle, COURSE_HEIGHT)[2] > p[2] + 0.025 {
        -0.545
    } else {
        -0.445
    };
    if !(inner_limit..0.35).contains(&offset) || angle > rim.end || !(0.015..0.72).contains(&depth)
    {
        return 1.;
    }
    let above_course = depth - COURSE_HEIGHT;
    if above_course < MIN_JOIN_HEIGHT {
        return 0.;
    }
    let baseline = baseline_thickness(rim, p, layer, height);
    let available = above_course.min(baseline);
    volume_per_mm(width, available) / volume_per_mm(width, baseline)
}

struct Move {
    source: Point,
    target: Point,
    feed: f64,
    amount: f64,
    explicit_e: bool,
    arc: bool,
}

struct Emitter<'a, W: Write> {
    out: W,
    rim: &'a Rim,
    actual: Point,
    feed: f64,
    retract_debt: f64,
    highest: f64,
    added_points: Vec<Point>,
    estimated_add_seconds: f64,
    estimated_cut_seconds: f64,
    added_extrusion: f64,
    removed_extrusion: f64,
    max_rim_below_peak: f64,
    minimum_contact_z: f64,
    moved_paths: usize,
}

impl<W: Write> Emitter<'_, W> {
    fn line(&mut self, line: &str) -> io::Result<()> {
        writeln!(self.out, "{line}")
    }
    fn e(&mut self, amount: f64, feed: f64) -> io::Result<()> {
        writeln!(self.out, "G1 E{amount:.7} F{feed:.4}")?;
        self.feed = feed;
        self.retract_debt = (self.retract_debt - amount).max(0.);
        Ok(())
    }
    fn to(&mut self, p: Point, feed: f64) -> io::Result<()> {
        if distance(self.actual, p) <= 0.000018 {
            return Ok(());
        }
        self.estimated_add_seconds += distance(self.actual, p) / (feed / 60.);
        writeln!(
            self.out,
            "G1 X{:.5} Y{:.5} Z{:.5} F{feed:.4}",
            p[0], p[1], p[2]
        )?;
        self.actual = p;
        self.feed = feed;
        Ok(())
    }
    fn move_safely(&mut self, p: Point) -> io::Result<()> {
        if distance(self.actual, p) <= 0.000018 {
            return Ok(());
        }
        let retract = self.retract_debt < 0.01;
        if retract {
            self.e(-0.8, 1800.)?;
        }
        if lateral(self.actual, p) > 0.000018 {
            let safe = p[2]
                .max(self.actual[2])
                .max(self.highest + TRAVEL_CLEARANCE);
            self.to([self.actual[0], self.actual[1], safe], 900.)?;
            self.to([p[0], p[1], safe], 9000.)?;
        }
        self.to(p, 900.)?;
        if retract {
            self.e(0.8, 1800.)?;
            self.estimated_add_seconds += 1.6 / 30.;
        }
        Ok(())
    }
    fn top_near(&self, p: Point) -> f64 {
        if self.added_points.is_empty() {
            return f64::NEG_INFINITY;
        }
        let (offset, _, d) = self.rim.local(p);
        if !(-0.65..0.25).contains(&offset) || d > 0.85 {
            return f64::NEG_INFINITY;
        }
        self.added_points
            .iter()
            .filter(|q| lateral(p, **q) < 0.29)
            .map(|q| q[2])
            .fold(f64::NEG_INFINITY, f64::max)
    }
    fn crosses_added(&self, a: Point, b: Point) -> bool {
        if self.added_points.is_empty() || a[2].min(b[2]) >= self.highest + 0.005 {
            return false;
        }
        let n = (lateral(a, b) / 0.20).ceil().max(1.) as usize;
        (1..=n).any(|i| {
            let p = lerp(a, b, i as f64 / n as f64);
            self.top_near(p) > p[2] + 0.025
        })
    }
    fn extrude(&mut self, p: Point, amount: f64, feed: f64) -> io::Result<()> {
        let travel = distance(self.actual, p);
        self.estimated_add_seconds += travel / (feed / 60.);
        writeln!(
            self.out,
            "G1 X{:.5} Y{:.5} Z{:.5} E{amount:.7} F{feed:.4}",
            p[0], p[1], p[2]
        )?;
        self.actual = p;
        self.feed = feed;
        self.highest = self.highest.max(p[2]);
        Ok(())
    }
    fn arc(&mut self, arc: &Arc) -> io::Result<()> {
        writeln!(
            self.out,
            "; hsm contour course 1 angles {:.6} {:.6}",
            arc.from, arc.to
        )?;
        self.line("; FEATURE: Outer wall")?;
        writeln!(self.out, "; LINE_WIDTH: {BEAD_WIDTH}")?;
        let a = self.rim.contour(arc.from, COURSE_HEIGHT);
        let b = self.rim.contour(arc.to, COURSE_HEIGHT);
        let (from, to, start) = if a[2] <= b[2] {
            (arc.from, arc.to, a)
        } else {
            (arc.to, arc.from, b)
        };
        self.move_safely(start)?;
        let debt = self.retract_debt;
        if debt > 0.000001 {
            self.e(debt, 1800.)?;
        }
        let n = ((arc.to - arc.from).to_radians() * self.rim.radii[0].max(self.rim.radii[1])
            / PATH_STEP)
            .ceil()
            .max(1.) as usize;
        self.added_points.push(start);
        for i in 1..=n {
            let p = self
                .rim
                .contour(from + (to - from) * i as f64 / n as f64, COURSE_HEIGHT);
            self.max_rim_below_peak = self
                .max_rim_below_peak
                .max(self.highest - p[2].min(self.actual[2]));
            self.minimum_contact_z = self.minimum_contact_z.min(p[2]);
            let amount = lateral(self.actual, p) * volume_per_mm(BEAD_WIDTH, COURSE_HEIGHT);
            self.extrude(p, amount, CONTACT_FEED)?;
            self.added_points.push(p);
            self.added_extrusion += amount;
        }
        if debt > 0.000001 {
            self.e(-debt, 1800.)?;
        }
        Ok(())
    }
    fn preserve(&mut self, line: &str, m: &Move, deposition: bool) -> io::Result<()> {
        if (self.feed - m.feed).abs() > 0.0001 {
            writeln!(self.out, "G1 F{:.4}", m.feed)?;
        }
        self.line(line)?;
        self.actual = m.target;
        self.feed = m.feed;
        self.retract_debt = (self.retract_debt - m.amount).max(0.);
        if deposition {
            self.highest = self.highest.max(m.target[2]);
        }
        Ok(())
    }
    fn original_move(&mut self, line: &str, m: &Move, deposition: bool) -> io::Result<()> {
        let sync = distance(self.actual, m.source) < 0.00002;
        if deposition {
            if !sync {
                self.move_safely(m.source)?;
            }
            return self.preserve(line, m, true);
        }
        let moving = distance(m.source, m.target) > 0.00002 || m.arc;
        if !moving {
            if m.explicit_e {
                self.e(m.amount, m.feed)?;
            } else if (self.feed - m.feed).abs() > 0.0001 {
                writeln!(self.out, "G1 F{:.4}", m.feed)?;
                self.feed = m.feed;
            }
            return Ok(());
        }
        let clashes = self.crosses_added(self.actual, m.target);
        if sync && !clashes {
            return self.preserve(line, m, false);
        }
        if m.explicit_e {
            self.e(m.amount, m.feed)?;
        }
        if lateral(m.source, m.target) < 0.00002 && !sync {
            return Ok(());
        }
        let mut target = m.target;
        if self.top_near(target) > target[2] + 0.025 {
            target[2] = self.highest.max(target[2]) + TRAVEL_CLEARANCE;
        }
        self.move_safely(target)
    }
    fn retained_flow(&self, p: Point, width: f64, layer: usize, height: f64) -> f64 {
        let (offset, angle, depth) = self.rim.local(p);
        if (depth < 0.015 || angle > self.rim.end)
            && (-0.18..COURSE_HEIGHT + MIN_JOIN_HEIGHT).contains(&depth)
            && (-0.55..0.35).contains(&offset)
            && self.top_near(p) > p[2] + 0.04
        {
            // A native skin road can run below the seat or across a tangent
            // join. Clear the section that would pass below a completed arc.
            return 0.;
        }
        remnant_flow(self.rim, p, width, layer, height)
    }

    fn replace(&mut self, m: &Move, width: f64, layer: usize, height: f64) -> io::Result<()> {
        let mut intervals: Vec<(f64, f64, f64)> = Vec::new();
        let n = (lateral(m.source, m.target) / 0.045).ceil().max(5.) as usize;
        for i in 0..n {
            let a = i as f64 / n as f64;
            let b = (i + 1) as f64 / n as f64;
            let flow = self.retained_flow(
                lerp(m.source, m.target, (a + b) * 0.5),
                width,
                layer,
                height,
            );
            if let Some(last) = intervals.last_mut() {
                if (last.2 - flow).abs() < 0.018 {
                    last.1 = b;
                    continue;
                }
            }
            intervals.push((a, b, flow));
        }
        let mut kept = 0.;
        for (a, b, flow) in intervals {
            if flow <= 0.00001 {
                continue;
            }
            let start = lerp(m.source, m.target, a);
            self.move_safely(start)?;
            let amount = m.amount * (b - a) * flow;
            self.extrude(lerp(m.source, m.target, b), amount, m.feed)?;
            kept += amount;
        }
        self.removed_extrusion += m.amount - kept;
        self.estimated_cut_seconds += distance(m.source, m.target) / (m.feed / 60.);
        self.moved_paths += 1;
        Ok(())
    }
}

fn build(input: &Path, output: &Path, rim: &Rim) -> io::Result<ContourReport> {
    let source = fs::read_to_string(input)?;
    let lines: Vec<_> = source.lines().collect();
    let mut planes = Vec::new();
    let mut plane = 0.;
    let mut object = 0;
    let mut at = BTreeMap::<usize, usize>::new();
    let mut last_support = BTreeMap::<usize, usize>::new();
    let mut body = false;
    let mut layer = 0;
    let mut feature = "";
    let mut p = [0., 0., 0.];
    for (index, line) in lines.iter().enumerate() {
        if line.starts_with("; CHANGE_LAYER") {
            body = true;
            layer += 1;
        }
        if line.starts_with("; MACHINE_END_GCODE_START") {
            break;
        }
        if let Some(f) = line.strip_prefix("; FEATURE: ") {
            feature = f;
        }
        if let Some(s) = line.strip_prefix("; OBJECT_ID: ") {
            object = s.parse().unwrap_or(0);
        }
        if let Some(s) = line.strip_prefix("; Z_HEIGHT: ") {
            plane = s.parse().unwrap();
        }
        if !body {
            continue;
        }
        let code = line.split(';').next().unwrap_or_default().trim();
        if matches!(code.split_whitespace().next(), Some("G91" | "M82"))
            || (code.starts_with("G92 ") && words(code).xyz.iter().any(Option::is_some))
        {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "the restored print body must use absolute XYZ and relative extrusion",
            ));
        }
        if !line.starts_with("G1 ") {
            continue;
        }
        let w = words(line);
        let q = std::array::from_fn(|i| w.xyz[i].unwrap_or(p[i]));
        if object == rim.object && lateral(p, q) > 1e-7 && w.e.unwrap_or(0.) > 0. {
            if is_support(feature) {
                last_support.insert(layer, index);
            } else {
                let (offset, _, depth) = rim.local(lerp(p, q, 0.5));
                if depth > 0.015 && offset < 0.75 && !at.contains_key(&layer) {
                    at.insert(layer, index);
                    planes.push((layer, plane));
                }
            }
        }
        p = q;
    }
    if planes.is_empty() {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "selected object has no model layers",
        ));
    }
    let arcs = arcs_by_layer(rim, &planes);
    if arcs.keys().any(|layer| *layer <= 2) {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "the selected rim interval overlaps the bed-backed layers",
        ));
    }
    let mut insert_at = BTreeMap::new();
    for (layer, arcs) in &arcs {
        let mut insertion = at[layer];
        if let Some(last) = last_support.get(layer) {
            if *last >= insertion {
                insertion = last + 1;
            }
        }
        insert_at.insert(insertion, arcs);
    }
    let mut e = Emitter {
        out: BufWriter::new(fs::File::create(output)?),
        rim,
        actual: [0.; 3],
        feed: 1800.,
        retract_debt: 0.,
        highest: 0.,
        added_points: Vec::new(),
        estimated_add_seconds: 0.,
        estimated_cut_seconds: 0.,
        added_extrusion: 0.,
        removed_extrusion: 0.,
        max_rim_below_peak: 0.,
        minimum_contact_z: f64::INFINITY,
        moved_paths: 0,
    };
    let mut source_position = [0.; 3];
    let mut feed = 1800.;
    let mut width = 0.42;
    let mut feature = "";
    let mut fan = 0.;
    let mut object = 0;
    let mut height = LAYER_HEIGHT;
    let mut layer = 0;
    let mut body = false;
    for (index, line) in lines.into_iter().enumerate() {
        if line.starts_with("; CHANGE_LAYER") {
            body = true;
            layer += 1;
        }
        if line.starts_with("; MACHINE_END_GCODE_START") {
            body = false;
        }
        if let Some(f) = line.strip_prefix("; FEATURE: ") {
            feature = f;
        }
        if let Some(w) = line.strip_prefix("; LINE_WIDTH: ") {
            width = w.parse().unwrap();
        }
        if let Some(s) = line.strip_prefix("; OBJECT_ID: ") {
            object = s.parse().unwrap_or(0);
        }
        if let Some(s) = line.strip_prefix("; LAYER_HEIGHT: ") {
            height = s.parse().unwrap();
        }
        if line.starts_with("M106 ") && (!line.contains(" P") || line.contains(" P1 ")) {
            fan = words(line).fan.unwrap_or(fan);
        }
        if let Some(arcs) = insert_at.get(&index) {
            e.line("M106 P1 S178.5")?;
            for arc in *arcs {
                e.arc(arc)?;
            }
            e.line("; hsm contour end")?;
            writeln!(
                e.out,
                "M106 P1 S{fan}\n; FEATURE: {feature}\n; LINE_WIDTH: {width:.5}"
            )?;
        }
        let arc = line.starts_with("G2 ") || line.starts_with("G3 ");
        if !(line.starts_with("G1 ") || line.starts_with("G0 ") || arc) {
            e.line(line)?;
            continue;
        }
        let w = words(line);
        let p = source_position;
        let target = std::array::from_fn(|i| w.xyz[i].unwrap_or(p[i]));
        source_position = target;
        feed = w.f.unwrap_or(feed);
        let m = Move {
            source: p,
            target,
            feed,
            amount: w.e.unwrap_or(0.),
            explicit_e: w.e.is_some(),
            arc,
        };
        let depositing = m.amount > 0. && lateral(p, target) > 1e-7;
        if !body || (layer <= 2 && e.added_points.is_empty()) {
            e.line(line)?;
            e.actual = target;
            e.feed = feed;
            if body {
                e.retract_debt = (e.retract_debt - m.amount).max(0.);
                if depositing {
                    e.highest = e.highest.max(target[2]);
                }
            }
            continue;
        }
        let may_clip = object == rim.object
            && depositing
            && !arc
            && is_rim_feature(feature)
            && [0., 0.25, 0.5, 0.75, 1.]
                .iter()
                .any(|t| e.retained_flow(lerp(p, target, *t), width, layer, height) < 0.9999);
        if may_clip {
            e.replace(&m, width, layer, height)?;
        } else {
            e.original_move(line, &m, depositing)?;
        }
    }
    e.out.flush()?;
    let arc_count = arcs.values().map(Vec::len).sum();
    Ok(ContourReport {
        arc_count,
        emitted_contact_segments: e.added_points.len() - arc_count,
        modified_native_paths: e.moved_paths,
        extrusion_added_mm: e.added_extrusion,
        extrusion_removed_mm: e.removed_extrusion,
        estimated_motion_delta_seconds: e.estimated_add_seconds - e.estimated_cut_seconds,
        maximum_contact_depth_below_prior_peak_mm: e.max_rim_below_peak,
        minimum_contact_z_mm: e.minimum_contact_z,
    })
}

#[allow(dead_code)]
fn main() -> io::Result<()> {
    let args: Vec<_> = env::args().collect();
    if args.len() != 12 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "usage: contour INPUT.gcode OUTPUT.gcode OBJECT_ID CX CY CZ TILT_DEG RADIUS_X RADIUS_Y FIRST_ANGLE LAST_ANGLE",
        ));
    }
    let parse = |i: usize| {
        args[i]
            .parse::<f64>()
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))
    };
    let spec = RimSpec {
        identify_id: args[3]
            .parse()
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidInput, e))?,
        center_mm: [parse(4)?, parse(5)?, parse(6)?],
        seat_fall_angle_degrees: parse(7)?,
        semi_axes_mm: [parse(8)?, parse(9)?],
        supported_angles_degrees: [parse(10)?, parse(11)?],
    };
    let report = apply(Path::new(&args[1]), Path::new(&args[2]), spec)?;
    println!(
        "{{\"arc_count\":{},\"emitted_contact_segments\":{},\"modified_native_paths\":{},\"extrusion_added_mm\":{:.5},\"extrusion_removed_mm\":{:.5},\"estimated_motion_delta_seconds\":{:.5},\"maximum_contact_depth_below_prior_peak_mm\":{:.5},\"minimum_contact_z_mm\":{:.5}}}",
        report.arc_count,
        report.emitted_contact_segments,
        report.modified_native_paths,
        report.extrusion_added_mm,
        report.extrusion_removed_mm,
        report.estimated_motion_delta_seconds,
        report.maximum_contact_depth_below_prior_peak_mm,
        report.minimum_contact_z_mm
    );
    Ok(())
}
