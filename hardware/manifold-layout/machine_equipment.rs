//! Placed above-core equipment, installed pump joints and warm-side tube solids.
//!
//! Purchased models retain their fine triangles. Parameter-dependent mating stock,
//! hardware, insulation and tube paths are constructed on the Rust kernel.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Body, Imported, Path as SweepPath, Plane, Profile, Solid, V2, V3,
                 import, step, v2, v3};
use hsm_layout_data::tube::Segment;
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::sync::Arc;

/// One piece of placed equipment: where it stands, its colour, and how its solids are made.
/// A reference that sets `presentation` false is drawn from its placed solids alone.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Item {
    pub name: String,
    pub transform: [[f64; 4]; 3],
    pub color: Option<[f64; 3]>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub presentation: Option<bool>,
    #[serde(flatten)]
    pub make: Make,
}

/// The bodies an item takes from a reference model: all of them, or those under the
/// `select`ed names, less any whose name holds an `exclude`d text.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Source {
    pub source: String,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub select: Option<Vec<String>>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub exclude: Option<Vec<String>>,
}

/// How an item's solids are made, before they are placed.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(tag = "op", rename_all = "kebab-case")]
pub enum Make {
    /// A reference model's bodies as they are.
    Reference(Source),
    /// A solenoid valve, each clocked port's bodies turned about the valve's axis.
    Valve {
        #[serde(flatten)]
        from: Source,
        #[serde(default)]
        clock: BTreeMap<String, f64>,
    },
    /// A stem elbow with its stem trimmed back to `tip_x`.
    StemElbow {
        #[serde(flatten)]
        from: Source,
        tip_x: f64,
    },
    /// A pump's tube from its barb to the reducer's stem.
    PumpTube { side: Side, joint: Joint, bend: Bend },
    /// A reducer cut at `cut_x` and seated on the cut.
    PumpReducer {
        #[serde(flatten)]
        from: Source,
        cut_x: f64,
    },
    /// A worm clamp's band and housing, or its key.
    PumpClamp { kind: ClampPiece, diameter: f64, xc: f64, keys: f64 },
    /// A bulkhead fitting cut to its stock envelope.
    Bulkhead {
        #[serde(flatten)]
        from: Source,
    },
    /// A bulkhead's hex nut.
    BulkheadNut { data: Nut },
    /// A mounting screw, or the heat-set insert it threads into.
    MountHardware {
        axis: [f64; 3],
        point: [f64; 3],
        head_reach: f64,
        length: f64,
        setback: f64,
        dimensions: Hardware,
    },
    /// The drain vent's adapter with its barb's tip at `vent_tip`.
    VentAdapter { vent_tip: [f64; 3] },
}

impl Make {
    /// The reference model the item's solids come from, where it has one.
    fn from(&self) -> Option<&Source> {
        match self {
            Make::Reference(from)
            | Make::Valve { from, .. }
            | Make::StemElbow { from, .. }
            | Make::PumpReducer { from, .. }
            | Make::Bulkhead { from } => Some(from),
            _ => None,
        }
    }
}

/// Which side of the pump a tube is on.
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum Side {
    Suction,
    Discharge,
}

/// Which piece of a worm clamp an item is.
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ClampPiece {
    Clamp,
    Key,
}

/// A pump tube's joint: the bore it is stretched over, as axial stations and radii, and the
/// tube's stock.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Joint {
    pub bore: Vec<[f64; 2]>,
    pub tube_od_mm: f64,
    pub tube_id_mm: f64,
    pub pivot_z: f64,
}

/// A pump tube's bend: the frame of its far end, and the arcs between where it has them.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Bend {
    pub end_frame: Frame,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub segments: Option<Vec<Segment>>,
}

/// A frame: the rows of its rotation and its translation.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Frame {
    pub rotation: [[f64; 3]; 3],
    pub translation_mm: [f64; 3],
}

/// Where a bulkhead's nut sits on the rear wall, and its hex and bore.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Nut {
    pub x: f64,
    pub flange_y: f64,
    pub z: f64,
    pub nut_af_mm: f64,
    pub barrel_d_mm: f64,
    pub nut_depth_mm: f64,
}

/// A mounting screw's dimensions, or its insert's.
#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(untagged)]
pub enum Hardware {
    Screw {
        head_height: f64,
        head_radius: f64,
        shaft_radius: f64,
        socket_af: f64,
        socket_depth: f64,
    },
    Insert {
        radius: f64,
        bore_radius: f64,
        length: f64,
    },
}

/// What the equipment is cut from: every item in the order it is placed.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Request {
    pub name: String,
    pub items: Vec<Item>,
}

/// The file a reference item is drawn from: its fine model, or the payload beside its STEP
/// with the digest of the model that payload was cut from.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub enum Drawn {
    Model(String),
    Payload { path: String, source_sha256: Option<String> },
}

/// A reference item's drawing: the bodies of its file it stands as, and the names they take.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Skin {
    pub item: String,
    pub drawn: Drawn,
    pub indices: Vec<usize>,
    pub targets: Vec<String>,
}

/// One placed body's measures.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Measure {
    pub name: String,
    pub color: Option<[f64; 3]>,
    pub min: [f64; 3],
    pub max: [f64; 3],
    pub volume: f64,
    pub centroid: [f64; 3],
    pub vertices: usize,
    pub triangles: usize,
}

/// What the equipment stage hands on: each item's bodies in the model it wrote, the reference
/// items' drawings, and every placed body's measures.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Placed {
    pub groups: BTreeMap<String, Vec<usize>>,
    pub presentation: Vec<Skin>,
    pub bodies: Vec<Measure>,
}

fn frame(rows: &[[f64; 4]; 3]) -> Affine {
    Affine { m: *rows }
}
fn datum(v: &Frame) -> Affine {
    let mut m = [[0.; 4]; 3];
    for i in 0..3 {
        for j in 0..3 { m[i][j] = v.rotation[i][j]; }
        m[i][3] = v.translation_mm[i];
    }
    Affine { m }
}
/// An unplaced construction depends on its recipe, selected model entries and
/// numeric dimensions. Identity, installed frame, material and presentation are
/// applied separately for every instance. Keep cuffs on their authored CSG path.
fn construction_key(item: &Item) -> Result<Option<String>> {
    if matches!(item.make, Make::PumpTube { .. }) { return Ok(None); }
    Ok(Some(serde_json::to_string(&item.make)?))
}

fn selected(v: &Source, name: &str) -> bool {
    let included = v.select.as_ref().map(|selected|
        selected.iter().any(|n|
            name == n || name.strip_prefix(n.as_str()).is_some_and(|rest| rest.starts_with('/'))))
        .unwrap_or(true);
    let excluded = v.exclude.as_ref().is_some_and(|excluded|
        excluded.iter().any(|n| name.contains(n.as_str())));
    included && !excluded
}
fn source(name: &str, v: &Source, cache: &mut BTreeMap<String, Vec<Imported>>) -> Result<Vec<Solid>> {
    let path = v.source.as_str();
    if !cache.contains_key(path) {
        let bodies = if path.ends_with(".npz") { import::model(path)? }
                     else { import::payload(path)? };
        cache.insert(path.to_owned(), bodies);
    }
    let mut solids = vec![];
    for body in &cache[path] {
        if selected(v,&body.name) { solids.push(body.solid.clone()); }
    }
    ensure!(!solids.is_empty(), "{name} selected no bodies in {path}");
    Ok(solids)
}
fn profile_rows(rows: &[[f64; 2]]) -> Vec<V2> {
    rows.iter().map(|row| v2(row[0], row[1])).collect()
}
fn turned(profile: &[V2], filled: bool) -> Result<Solid> {
    let mut outline = Vec::new();
    if filled { outline.push(v2(profile[0].x, 0.)); }
    outline.extend_from_slice(profile);
    if filled { outline.push(v2(profile.last().unwrap().x, 0.)); }
    Plane::XY.revolve(&Profile::polygon(&outline), 360., V2::ZERO, v2(1., 0.))
}
fn tube_turn(rows: &[V2], od: f64, id: f64) -> Result<Solid> {
    let mut clean = vec![];
    for &row in rows {
        if clean.last().is_none_or(|last: &V2|
            (row.x-last.x).abs()>1e-6 || (row.y-last.y).abs()>1e-6) { clean.push(row); }
    }
    let mut outline: Vec<_> = clean.iter().map(|p|
        v2(p.x, (p.y * p.y + (od * od - id * id) / 4.).sqrt())).collect();
    outline.extend(clean.iter().rev().copied());
    turned(&outline, false)
}
fn start_and_tangent(segments: &[Segment]) -> Result<(V3, V3)> {
    for s in segments {
        let points: &[[f64; 3]] = match s {
            Segment::Line { points_mm } => points_mm,
            Segment::Arc { points_mm } => points_mm,
            Segment::Bezier { control_points_mm } => control_points_mm,
        };
        let start = V3::from(*points.first().context("tube segment has no points")?);
        if let Segment::Arc { points_mm } = s {
            let (u, v) = (V3::from(points_mm[1]) - start, V3::from(points_mm[2]) - start);
            let w = u.cross(v);
            let center = start + (v * u.norm2() - u * v.norm2()).cross(w) / (2. * w.norm2());
            return Ok((start, w.unit().cross(start - center).unit()));
        }
        for p in &points[1..] {
            let d = V3::from(*p) - start;
            if d.norm() > 1e-8 { return Ok((start, d.unit())); }
        }
    }
    bail!("tube path has no finite span")
}
fn sweep(segments: &[Segment], outer: f64, inner: Option<f64>) -> Result<Solid> {
    let (start, tangent) = start_and_tangent(segments)?;
    let mut path = SweepPath::new(start);
    for segment in segments {
        match segment {
            Segment::Line { points_mm } => {
                let end = V3::from(points_mm[1]);
                if (end - path.at()).norm() > 1e-6 { path = path.line_to(end); }
            }
            Segment::Arc { points_mm } => path = path.arc_through(V3::from(points_mm[1]),
                                                                  V3::from(points_mm[2]))?,
            Segment::Bezier { control_points_mm } => {
                let controls = control_points_mm.iter().map(|&p| V3::from(p)).collect::<Vec<_>>();
                path = path.bezier(&controls)?;
            }
        }
    }
    let wide = if tangent.x.abs() < 0.9 { V3::X } else { V3::Y };
    let mut profile = Profile::circle(V2::ZERO, outer);
    if let Some(inner) = inner { profile = profile.with_hole(Profile::circle(V2::ZERO, inner).outer); }
    Plane::new(start, wide, tangent)?.sweep(&profile, &path)
}
fn pump_tube(side: Side, j: &Joint, bend: &Bend) -> Result<Solid> {
    let rows = profile_rows(&j.bore);
    let (od, id) = (j.tube_od_mm, j.tube_id_mm);
    let end = datum(&bend.end_frame);
    if side == Side::Suction {
        let segments = bend.segments.as_deref().context("suction arcs")?;
        let span = sweep(segments, od / 2., Some(id / 2.))?;
        let on_barb = tube_turn(&rows[..rows.len() - 2], od, id)?;
        let on_stem = tube_turn(&[v2(0., rows.last().unwrap().y),
                                 v2(10., rows.last().unwrap().y)], od, id)?.transformed(&end);
        Solid::union_all(&[on_barb,span,on_stem])
    } else {
        let direction = end.vector(V3::X);
        let angle = direction.x.clamp(-1., 1.).acos();
        let axis = V3::X.cross(direction).unit();
        let radial = v3(0., direction.y, direction.z).unit();
        let pivot = radial * -j.pivot_z;
        let half = Affine::rotation(pivot, axis, angle.to_degrees() / 2.);
        let crease = Solid::cuboid(v3(-100., -100., -100.), v3(0., 100., 100.)).transformed(&half);
        let past = od * (angle / 2.).tan() + 1.;
        let mut barb = rows[..rows.len() - 2].to_vec();
        barb.push(v2(past, rows[rows.len() - 3].y));
        let on_barb = tube_turn(&barb, od, id)?.intersect(&crease)?;
        let on_stem = tube_turn(&[v2(-past, rows.last().unwrap().y), *rows.last().unwrap()], od, id)?
            .transformed(&end).cut(&crease)?;
        on_barb.union(&on_stem)
    }
}
fn key_outline() -> Vec<V2> {
    // Same 48 samples on each of the two authored circles as the native key.
    let mut p = vec![];
    for (center, width) in [(4., 8.), (14., 26.)] {
        for i in 0..48 {
            let a = i as f64 * std::f64::consts::TAU / 48.;
            p.push(v2(center + width / 2. * a.cos(), width / 2. * a.sin()));
        }
    }
    p.sort_by(|a, b| a.x.total_cmp(&b.x).then(a.y.total_cmp(&b.y)));
    let mut hull: Vec<V2> = vec![];
    for &v in &p {
        while hull.len() > 1 && (hull[hull.len()-1]-hull[hull.len()-2]).cross(v-hull[hull.len()-1]) <= 0. {
            hull.pop();
        }
        hull.push(v);
    }
    let lower = hull.len();
    for &v in p.iter().rev().skip(1) {
        while hull.len() > lower && (hull[hull.len()-1]-hull[hull.len()-2]).cross(v-hull[hull.len()-1]) <= 0. {
            hull.pop();
        }
        hull.push(v);
    }
    hull.pop();
    hull
}
fn pump_clamp(kind: ClampPiece, diameter: f64, xc: f64, keys: f64) -> Result<Solid> {
    let r = diameter / 2.;
    let top = r + 0.6 + 7.;
    let screw_z = r + 0.6 + 3.5;
    if kind == ClampPiece::Key {
        let start = keys * (13. / 2. + 3.);
        let outline: Vec<_> = key_outline().iter().map(|p| v2(start + keys * p.x, screw_z + p.y)).collect();
        return Plane::YZ.at(v3(xc - 2.5, 0., 0.)).extrude(&Profile::polygon(&outline), 5.);
    }
    let band = Solid::cylinder(v3(xc - 4.5, 0., 0.), V3::X, r + 0.6, 9.)?
        .cut(&Solid::cylinder(v3(xc - 4.5, 0., 0.), V3::X, r, 9.)?)?;
    let housing = Solid::cuboid(v3(xc - 5., -6.5, 0.), v3(xc + 5., 6.5, top))
        .cut(&Solid::cylinder(v3(xc - 5., 0., 0.), V3::X, r + 0.6, 10.)?)?;
    let neck = Solid::cylinder(v3(xc, keys * 6.5, screw_z), V3::Y * keys, 3., 3.)?;
    band.union(&housing)?.union(&neck)
}
fn bulkhead(name: &str, from: &Source, sources: &mut BTreeMap<String, Vec<Imported>>) -> Result<Solid> {
    let fitting = Source { source: from.source.clone(), select: Some(vec!["fitting".to_owned()]),
                           exclude: from.exclude.clone() };
    let stock = Solid::compose(&source(name, &fitting, sources)?);
    let radius = 15. / 2.;
    let outside = Solid::cuboid(v3(-21., 0., -21.), v3(21., 11.827402874737649, 21.));
    let inside = Solid::cylinder(v3(0., -21.461096075301846, 0.), V3::Y,
                                 radius, 21.461096075301846)?;
    stock.intersect(&outside.union(&inside)?)
}
fn nut(d: &Nut) -> Result<Solid> {
    let center = v3(d.x, d.flange_y - 6., d.z);
    let mut p = Profile::new(hsm_kernel::Loop::regular(V2::ZERO, 6,
        d.nut_af_mm / (std::f64::consts::PI / 6.).cos()));
    p = p.with_hole(Profile::circle(V2::ZERO, d.barrel_d_mm / 2.).outer);
    Ok(Plane::new(center, V3::X, -V3::Y)?.extrude(&p, d.nut_depth_mm)?
        .rotate(v3(center.x, 0., center.z), V3::Y, 30.))
}
fn mounting(axis: V3, p: V3, head_reach: f64, length: f64, setback: f64, dimensions: &Hardware) -> Result<Solid> {
    let (head_height, head_radius, shaft_radius, socket_af, socket_depth) = match *dimensions {
        Hardware::Insert { radius, bore_radius, length } => {
            let face = p - axis * setback;
            return Solid::cylinder(face, -axis, radius, length)?
                .cut(&Solid::cylinder(face + axis * 0.1, -axis,
                                     bore_radius, length + 0.2)?);
        }
        Hardware::Screw { head_height, head_radius, shaft_radius, socket_af, socket_depth } =>
            (head_height, head_radius, shaft_radius, socket_af, socket_depth),
    };
    let head = p + axis * head_reach;
    let stock = Solid::cylinder(head - axis * length, axis,
                               shaft_radius, length)?
        .union(&Solid::cylinder(head, axis, head_radius, head_height)?)?;
    let wide = if axis.x.abs() < 0.9 { V3::X } else { V3::Y };
    let socket = Profile::new(hsm_kernel::Loop::regular(V2::ZERO, 6,
        socket_af / (std::f64::consts::PI / 6.).cos()));
    stock.cut(&Plane::new(head + axis * (head_height - socket_depth), wide, axis)?
        .extrude(&socket, socket_depth + 0.1)?)
}
fn vent_adapter(vent_tip: V3) -> Result<Solid> {
    let (rb, rt) = (((14. * 14. + 7.7 * 7.7 - 6.1 * 6.1) as f64).sqrt() / 2.,
                    ((11.7 * 11.7 + 4. * 4. - 3.8 * 3.8) as f64).sqrt() / 2.);
    let (drop, reach, bend) = (9.55, 25.4, 4.05);
    let cup = Solid::cylinder(v3(0., 0., -drop - rt), V3::Z, rb, 8.6 + drop + rt)?;
    let socket = Solid::cylinder(v3(0., 0., -drop), -V3::X, rt, reach)?;
    let channel = sweep(&[Segment::Arc { points_mm: [
        [0.,0.,-5.5],[-bend+bend/2_f64.sqrt(),0.,-5.5-bend/2_f64.sqrt()],[-bend,0.,-drop]] }],
        2., None)?;
    let bore = Solid::cylinder(v3(-bend, 0., -drop), -V3::X, 2., reach - bend + 0.1)?;
    let transition = Solid::cone(v3(0., 0., -5.5), V3::Z, 2., 7.7 / 2., 5.5)?;
    let barb = Solid::cylinder(V3::ZERO, V3::Z, 7.7 / 2., 8.7)?;
    let mut body = cup.union(&socket)?.cut(&barb)?.cut(&transition)?.cut(&channel)?.cut(&bore)?;
    for (i, (center, radius)) in [(3.1, rb), (19.4, rt)].into_iter().enumerate() {
        let (lo, hi) = (center - 1.4, center + 1.4);
        let points = [v2(radius, lo - 1.), v2(radius - 0.5, lo), v2(radius - 0.5, hi),
                      v2(radius, hi + 1.), v2(radius + 1., hi + 1.), v2(radius + 1., lo - 1.)];
        let mut groove = Plane::XZ.revolve(&Profile::polygon(&points), 360., V2::ZERO, v2(0.,1.))?;
        if i == 1 { groove = groove.rotate(V3::ZERO, V3::Y, -90.).translate(v3(0.,0.,-drop)); }
        body = body.cut(&groove)?;
    }
    let flat_z = -(rb + drop + rt) / 2_f64.sqrt() + 0.6;
    body = body.rotate(V3::ZERO, V3::Y, 45.)
        .cut(&Solid::cuboid(v3(-50.,-50.,flat_z-1.),v3(50.,50.,flat_z)))?
        .rotate(V3::ZERO, V3::Y, -45.);
    Ok(body.translate(vent_tip))
}
/// The placed equipment cut into `output` as one model, and what the plan takes of it.
pub fn run(request: &Request, output: &std::path::Path) -> Result<Placed> {
    let mut sources = BTreeMap::new();
    let mut placed: Vec<(String,Option<[f64;3]>,Solid)> = vec![];
    let mut groups = BTreeMap::new();
    let mut presentation = vec![];
    let items = &request.items;
    let keys = items.iter().map(construction_key).collect::<Result<Vec<_>>>()?;
    let mut last_construction = BTreeMap::new();
    let mut last_source = BTreeMap::new();
    for (index, (item, key)) in items.iter().zip(&keys).enumerate() {
        if let Some(key) = key.as_deref() { last_construction.insert(key, index); }
        if let Some(from) = item.make.from() {
            last_source.insert(from.source.as_str(), index);
        }
    }
    let mut constructions: BTreeMap<&str, Arc<[Solid]>> = BTreeMap::new();
    for (index, item) in items.iter().enumerate() {
        let name = item.name.as_str();
        let key = keys[index].as_deref();
        let raw = if let Some(raw) = key.and_then(|key| constructions.get(key)) {
            Arc::clone(raw)
        } else {
            let raw: Arc<[Solid]> = (|| -> Result<Vec<Solid>> { Ok(match &item.make {
                Make::Reference(from) => source(name,from,&mut sources)?,
                Make::Valve { from, clock } => {
                    let original = source(name,from,&mut sources)?;
                    let mut solids = vec![];
                    for body in original {
                        for mut solid in body.components() {
                            let b = solid.bounds();
                            let port = if b.max.y < -22.25 {Some("inlet")}
                                       else if b.min.y > 22.25 {Some("outlet")} else {None};
                            if let Some(angle) = port.and_then(|p|clock.get(p).copied()).filter(|a|*a!=0.) {
                                solid=solid.rotate(v3(0.,0.,11.05),V3::Y,angle);
                            }
                            solids.push(solid);
                        }
                    }
                    solids
                }
                Make::StemElbow { from, tip_x } => {
                    let trim = Solid::cuboid(v3(-100.,-50.,-50.),v3(*tip_x,50.,50.));
                    source(name,from,&mut sources)?.iter().map(|s|s.cut(&trim)).collect::<Result<Vec<_>>>()?
                }
                Make::PumpTube { side, joint, bend } => vec![pump_tube(*side, joint, bend)?],
                Make::PumpReducer { from, cut_x } => {
                    let cut = *cut_x;
                    let trim = Solid::cuboid(v3(-100.,-50.,-50.),v3(cut,50.,50.));
                    source(name,from,&mut sources)?.iter().map(|s|Ok(s.cut(&trim)?.translate(v3(-cut,0.,0.))))
                        .collect::<Result<Vec<_>>>()?
                }
                Make::PumpClamp { kind, diameter, xc, keys } => vec![pump_clamp(*kind, *diameter, *xc, *keys)?],
                Make::Bulkhead { from } => vec![bulkhead(name,from,&mut sources)?],
                Make::BulkheadNut { data } => vec![nut(data)?],
                Make::MountHardware { axis, point, head_reach, length, setback, dimensions } =>
                    vec![mounting(V3::from(*axis), V3::from(*point), *head_reach, *length, *setback, dimensions)?],
                Make::VentAdapter { vent_tip } => vec![vent_adapter(V3::from(*vent_tip))?],
            }) })().with_context(||format!("equipment {name}"))?.into();
            if let Some(key) = key.filter(|key| last_construction.get(*key).copied().unwrap() > index) {
                constructions.insert(key, Arc::clone(&raw));
            }
            raw
        };
        let installed = frame(&item.transform);
        let rgb = item.color;
        let start = placed.len();
        let reference = match &item.make { Make::Reference(from) => Some(from), _ => None };
        if let Some(from) = reference.filter(|_| item.presentation != Some(false)) {
            let path = from.source.as_str();
            let targets: Vec<_> = (0..raw.len()).map(|i|if raw.len()==1 {name.to_owned()}
                else {format!("{name}/{}",i+1)}).collect();
            if path.ends_with(".npz") {
                let indices: Vec<_> = sources[path].iter().enumerate()
                    .filter_map(|(i,b)|selected(from,&b.name).then_some(i)).collect();
                presentation.push(Skin { item: name.to_owned(), drawn: Drawn::Model(path.to_owned()),
                    indices, targets });
            } else {
                let bytes=std::fs::read(path)?;
                let size=u32::from_le_bytes(bytes[..4].try_into()?) as usize;
                let header:serde_json::Value=serde_json::from_slice(&bytes[4..4+size])?;
                let indices:Vec<_>=header["meshes"].as_array().context("array")?.iter().enumerate()
                    .filter_map(|(i,b)|selected(from,b["name"].as_str().unwrap_or("")).then_some(i)).collect();
                if indices.len()==raw.len() {
                    presentation.push(Skin { item: name.to_owned(),
                        drawn: Drawn::Payload { path: path.to_owned(),
                            source_sha256: header["src"].as_str().map(str::to_owned) },
                        indices, targets });
                }
            }
        }
        let source_colors: Vec<_> = match reference.filter(|_| rgb.is_none()) {
            Some(from) => sources[from.source.as_str()].iter()
                .filter(|body| selected(from, &body.name)).map(|body| body.color).collect(),
            None => Vec::new(),
        };
        placed.extend(raw.iter().enumerate().map(|(index, solid)|
            (name.to_owned(), rgb.or_else(|| source_colors.get(index).copied().flatten()),
             solid.transformed(&installed))));
        groups.insert(name.to_owned(),(start..placed.len()).collect::<Vec<_>>());
        if let Some(key) = key.filter(|key| last_construction.get(*key).copied() == Some(index)) {
            constructions.remove(key);
        }
        if let Some(path) = item.make.from().map(|from| from.source.as_str())
                .filter(|path| last_source.get(*path).copied() == Some(index)) {
            sources.remove(path);
        }
    }
    // Input geometry is released before the output tables and archive are written.
    drop(sources);
    let bodies = placed.iter().map(|(name,color,solid)|Body{name,color:*color,solid}).collect::<Vec<_>>();
    step::write_model(&output.join(format!("{}.step.npz", request.name)),&bodies)?;
    let bodies = placed.iter().map(|(name,color,solid)| {
        let bounds=solid.bounds();
        let mass=solid.mass();
        Measure { name: name.clone(), color: *color, min: bounds.min.to_array(), max: bounds.max.to_array(),
            volume: mass.volume, centroid: mass.centroid.to_array(),
            vertices: solid.verts().len(), triangles: solid.tris().len() }
    }).collect();
    Ok(Placed { groups, presentation, bodies })
}
