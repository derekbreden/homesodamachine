//! World-placed warm fluid/gas tube paths and their occupied insulation.
//!
//! The caller supplies the selected authored route segments and the installed
//! equipment groups that bound foam compression.
use anyhow::{Context, Result, bail};
use hsm_kernel::{Affine, Body, Leg, Path as SweepPath, Plane, Profile,
                 Solid, Spline, V2, V3, import, step, v3};
use hsm_layout_data::tube::Segment;
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::path::PathBuf;

/// A tube to sweep along its centreline, hollow where its inner diameter is positive.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Sweep {
    pub name: String,
    pub segments: Vec<Segment>,
    pub od_mm: f64,
    pub id_mm: f64,
    pub color: Option<[f64; 3]>,
}

/// A placement: the rows of its rotation and its translation.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Pose {
    pub rotation: [[f64; 3]; 3],
    pub translation_mm: [f64; 3],
}

/// The soda inlet's foam sleeve: the foam and the tube it covers as swept sections, the valve
/// whose leads leave through it, and the placed neighbours it is cut around.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Insulation {
    pub foam_segments: Vec<Segment>,
    pub foam_od_mm: f64,
    pub foam_id_mm: f64,
    pub tube_segments: Vec<Segment>,
    pub tube_od_mm: f64,
    pub tube_id_mm: f64,
    pub valve_pose: Pose,
    pub neighbors: Vec<String>,
    pub color: Option<[f64; 3]>,
}

/// The bodies of a fine model that one placed component is.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Bodies {
    pub model: PathBuf,
    pub indices: Vec<usize>,
}

/// What the routes are cut from: the tubes in the order they are swept, the soda foam where the
/// machine has it, and the placed components the foam is cut around.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Request {
    pub name: String,
    pub tubes: Vec<Sweep>,
    pub insulation: Option<Insulation>,
    pub components: BTreeMap<String, Bodies>,
}

/// One swept body as the placement takes it: its model, its index there and its name.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Instance {
    pub model: PathBuf,
    pub indices: Vec<usize>,
    pub name: String,
}

/// What the routes stage hands on: the swept bodies to place and each tube's developed length.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Routed {
    pub instances: Vec<Instance>,
    pub lengths: BTreeMap<String, f64>,
}

fn datum(pose: &Pose) -> Affine {
    let mut m = [[0.; 4]; 3];
    for i in 0..3 {
        for j in 0..3 { m[i][j] = pose.rotation[i][j]; }
        m[i][3] = pose.translation_mm[i];
    }
    Affine { m }
}

fn start_and_tangent(segments: &[Segment]) -> Result<(V3, V3)> {
    for s in segments {
        let points: &[[f64; 3]] = match s {
            Segment::Line { points_mm } => points_mm,
            Segment::Arc { points_mm, .. } => points_mm,
            Segment::Bezier { control_points_mm } => control_points_mm,
        };
        let start = V3::from(*points.first().context("tube segment has no points")?);
        if let Segment::Arc { points_mm, .. } = s {
            let middle = V3::from(points_mm[1]);
            let end = V3::from(points_mm[2]);
            let (u, v) = (middle - start, end - start);
            let cross = u.cross(v);
            let center = start + (v * u.norm2() - u * v.norm2()).cross(cross)
                / (2. * cross.norm2());
            let axis = u.cross(end - middle).unit();
            return Ok((start, axis.cross(start - center).unit()));
        }
        for p in &points[1..] {
            let d = V3::from(*p) - start;
            if d.norm() > 1e-8 { return Ok((start, d.unit())); }
        }
    }
    bail!("tube path has no finite span")
}

fn route_path(segments: &[Segment]) -> Result<SweepPath> {
    let (start, _) = start_and_tangent(segments)?;
    let mut path = SweepPath::new(start);
    for segment in segments {
        match segment {
            Segment::Line { points_mm } => {
                let end = V3::from(points_mm[1]);
                if (end - path.at()).norm() > 1e-6 { path = path.line_to(end); }
            }
            Segment::Arc { points_mm, .. } => path = path.arc_through(V3::from(points_mm[1]),
                                                                  V3::from(points_mm[2]))?,
            Segment::Bezier { control_points_mm } => {
                let controls = control_points_mm.iter().map(|&p| V3::from(p)).collect::<Vec<_>>();
                path = path.bezier(&controls)?;
            }
        }
    }
    Ok(path)
}

fn sweep(segments: &[Segment], outer: f64, inner: Option<f64>) -> Result<Solid> {
    let (start, tangent) = start_and_tangent(segments)?;
    let path = route_path(segments)?;
    let wide = if tangent.x.abs() < 0.9 { V3::X } else { V3::Y };
    let mut profile = Profile::circle(V2::ZERO, outer);
    if let Some(inner) = inner { profile = profile.with_hole(Profile::circle(V2::ZERO, inner).outer); }
    Plane::new(start, wide, tangent)?.sweep(&profile, &path)
}

fn curve_length(curve: &Spline) -> f64 {
    fn refine(curve: &Spline, a: f64, b: f64, values: [f64; 3], whole: f64,
              tolerance: f64, remaining: u32) -> f64 {
        let middle = (a + b) / 2.;
        let left_middle = curve.derivative((a + middle) / 2.).norm();
        let right_middle = curve.derivative((middle + b) / 2.).norm();
        let left = (middle - a) * (values[0] + 4. * left_middle + values[1]) / 6.;
        let right = (b - middle) * (values[1] + 4. * right_middle + values[2]) / 6.;
        let error = left + right - whole;
        if remaining == 0 || error.abs() <= 15. * tolerance {
            left + right + error / 15.
        } else {
            refine(curve, a, middle, [values[0], left_middle, values[1]], left,
                   tolerance / 2., remaining - 1)
                + refine(curve, middle, b, [values[1], right_middle, values[2]], right,
                         tolerance / 2., remaining - 1)
        }
    }
    let (a, b) = curve.range();
    let values = [curve.derivative(a).norm(), curve.derivative((a + b) / 2.).norm(),
                  curve.derivative(b).norm()];
    let whole = (b - a) * (values[0] + 4. * values[1] + values[2]) / 6.;
    refine(curve, a, b, values, whole, 1e-9, 20)
}

fn route_length(path: &SweepPath) -> f64 {
    path.legs.iter().map(|leg| match *leg {
        Leg::Line { a, b } => (b - a).norm(),
        Leg::Arc { a, c, turn, .. } => (a - c).norm() * turn,
        Leg::Curve { k, .. } => curve_length(&path.curves[k]),
    }).sum()
}

fn lead_exits(pose: &Affine) -> Result<Vec<Solid>> {
    let mut exits = vec![];
    for x in [-7.45,7.45] {
        let tip = pose.point(v3(x,27.1,52.2));
        // The existing R3 corner between downward and aft-facing lead stations.
        let a = tip + v3(0.,0.,2.);
        let before = tip + v3(0.,0.,-3.);
        let after = tip + v3(0.,-3.,-6.);
        let middle = tip + v3(0.,-3.+3./2_f64.sqrt(),-3.-3./2_f64.sqrt());
        exits.push(sweep(&[
            Segment::Line { points_mm: [a.to_array(), before.to_array()] },
            Segment::through(before.to_array(), middle.to_array(), after.to_array()),
            Segment::Line { points_mm: [after.to_array(), (tip+v3(0.,-12.,-6.)).to_array()] },
        ],2.,None)?);
    }
    Ok(exits)
}

fn insulation(v: &Insulation, parts: &BTreeMap<String, Vec<Solid>>) -> Result<Solid> {
    let mut foam = sweep(&v.foam_segments, v.foam_od_mm/2., Some(v.foam_id_mm/2.))?;
    let tube = sweep(&v.tube_segments, v.tube_od_mm/2., Some(v.tube_id_mm/2.))?;
    let mut tools: Vec<&Solid> = parts.get("soda-bend-holder").context("soda holder")?.iter().collect();
    tools.push(&tube);
    let exits = lead_exits(&datum(&v.valve_pose))?;
    tools.extend(exits.iter());
    for name in &v.neighbors {
        tools.extend(parts.get(name).context("placed foam neighbor")?.iter());
    }
    for tool in tools {
        for solid in tool.components() { foam = foam.cut(&solid)?; }
    }
    Ok(Solid::compose(&foam.components().into_iter().filter(|s|s.volume()>1.).collect::<Vec<_>>()))
}

fn equipment(components: &BTreeMap<String, Bodies>) -> Result<BTreeMap<String, Vec<Solid>>> {
    let mut requested: BTreeMap<&PathBuf, BTreeMap<usize, Vec<(String, usize)>>> = BTreeMap::new();
    let mut parts: BTreeMap<String, Vec<Option<Solid>>> = BTreeMap::new();
    for (name, reference) in components {
        parts.insert(name.clone(), vec![None; reference.indices.len()]);
        let model = requested.entry(&reference.model).or_default();
        for (slot, &index) in reference.indices.iter().enumerate() {
            model.entry(index).or_default().push((name.clone(), slot));
        }
    }
    for (path, bodies) in requested {
        let indices: BTreeSet<_> = bodies.keys().copied().collect();
        import::visit_model_indices(path, &indices, |index, body| {
            let (last, others) = bodies[&index].split_last().unwrap();
            for (name, slot) in others {
                parts.get_mut(name).unwrap()[*slot] = Some(body.solid.clone());
            }
            parts.get_mut(&last.0).unwrap()[last.1] = Some(body.solid);
            Ok(())
        })?;
    }
    parts.into_iter().map(|(name, bodies)| Ok((name,
        bodies.into_iter().map(|body| body.context("equipment body outside model"))
            .collect::<Result<Vec<_>>>()?))).collect()
}

/// The routed tubes cut into `output` as one model, and what the placement takes of them.
pub fn run(request: &Request, output: &std::path::Path) -> Result<Routed> {
    let mut placed: Vec<(String, Option<[f64; 3]>, Solid)> = vec![];
    if let Some(sleeve) = &request.insulation {
        let parts = equipment(&request.components)?;
        let foam = insulation(sleeve, &parts).context("occupied soda insulation")?;
        placed.push(("soda-continuous-insulation".to_owned(), sleeve.color, foam));
    }
    let mut lengths = BTreeMap::new();
    for tube in &request.tubes {
        lengths.insert(tube.name.clone(), route_length(&route_path(&tube.segments)?));
        let inside = tube.id_mm;
        let body = sweep(&tube.segments, tube.od_mm / 2.,
                         (inside > 0.).then_some(inside / 2.))
            .with_context(|| format!("warm tube route {}", tube.name))?;
        placed.push((format!("tube-{}", tube.name), tube.color, body));
    }
    let bodies = placed.iter().map(|(name, color, solid)|
        Body { name, color: *color, solid }).collect::<Vec<_>>();
    let model = output.join(format!("{}.step.npz", request.name));
    step::write_model(&model, &bodies)?;
    let instances = placed.iter().enumerate().map(|(index, (name, _, _))| Instance {
        model: model.clone(), indices: vec![index], name: name.clone() }).collect();
    Ok(Routed { instances, lengths })
}
