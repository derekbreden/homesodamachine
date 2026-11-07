//! The flavor manifold's model: its purchased valves, coils, tees, pumps and stem elbows cut from
//! their reference models where its numbers stand them, and its tubes swept along their
//! centrelines, written as the STEP, the fine model and the viewer payload the installed machine
//! places, with the frames it seats each valve and tee by.
//!
//!     manifold-layout [<output directory>]
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Affine, Imported, Loop, Path as Centreline, Plane, Profile, Solid, V2, V3, part, v3};
use hsm_manifold_numbers::{BODIES, Body, Part, Placement, Seg, TUBE_OD, Tube, stem_keep};
use serde_json::{Value, json};
use std::collections::HashMap;
use std::path::{Path, PathBuf, absolute};

/// Where the manifold's files go when the program is given no directory.
const OUT: &str = "hardware/manifold-layout";
/// The name its files and its STEP's product carry.
const NAME: &str = "manifold-layout";
/// The swept tubes' chord tolerance along their centrelines, mm.
const SWEEP_TOLERANCE: f64 = 0.003;

/// A purchased model the manifold is cut from: its key in the construction the machine reads,
/// and its STEP under the checkout.
#[derive(Clone, Copy, PartialEq, Eq, Hash)]
enum Model {
    Valve,
    Tee,
    Pump,
    Stem,
}

impl Model {
    fn key(self) -> &'static str {
        match self {
            Model::Valve => "valve",
            Model::Tee => "tee",
            Model::Pump => "pump",
            Model::Stem => "stem",
        }
    }
    fn step(self) -> &'static str {
        match self {
            Model::Valve => "hardware/reference/beduan-solenoid/beduan-solenoid.step",
            Model::Tee => "hardware/reference/tee-connector/tee-connector.step",
            Model::Pump => "hardware/reference/kamoer-kphm400/kamoer-kphm400.step",
            Model::Stem => "hardware/reference/neofit-stem-elbow/neofit-stem-elbow.step",
        }
    }
}

/// One group of a reference model's bodies a part keeps: the bodies by name (all of them when
/// none are named), fused or kept apart, and the box cut off the group.
struct Group {
    names: Option<&'static [&'static str]>,
    union: bool,
    cut: Option<([f64; 3], [f64; 3])>,
}

/// The model a part is cut from, the groups of its bodies it keeps, and the catalog colour it is
/// painted.
fn selection(part: Part) -> (Model, Vec<Group>, &'static str) {
    let named = |names, union| Group { names: Some(names), union, cut: None };
    match part {
        Part::Valve => (Model::Valve, vec![named(&["body", "collets"], true)], "C_VALVE"),
        Part::Coil => (
            Model::Valve,
            vec![named(&["winding", "yoke", "screw-heads"], true), named(&["terminals"], false)],
            "C_COIL",
        ),
        Part::Tee => (Model::Tee, vec![Group { names: None, union: false, cut: None }], "M_JG_BLACK_PP"),
        Part::PumpHead => (Model::Pump, vec![named(&["head"], false)], "C_PUMP_HEAD"),
        Part::PumpBoss => (Model::Pump, vec![named(&["rotor_housing"], false)], "C_PUMP_BOSS"),
        Part::PumpMotor => (Model::Pump, vec![named(&["motor_body"], false)], "C_PUMP_MOTOR"),
        Part::StemElbow { stem } => {
            // The stem is cut off where it stops standing in its collet.
            let keep = stem_keep(stem);
            let stem = Group {
                names: Some(&["body_and_stem"]),
                union: false,
                cut: Some(([-keep - 40.0, -20.0, -20.0], [40.0, 40.0, 40.0])),
            };
            (Model::Stem, vec![stem, named(&["release_collet"], false)], "M_NEOFIT_WHITE_ACETAL")
        }
    }
}

/// A placement's frame: its axes as columns, then its origin.
fn frame(p: &Placement) -> [[f64; 4]; 3] {
    let (x, z) = (p.x, p.z);
    let y = [z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0]];
    [0, 1, 2].map(|k| [x[k], y[k], z[k], p.at[k]])
}

/// The bodies a part keeps of its reference model, each group fused or composed, in the model's
/// own frame.
fn prototype(groups: &[Group], imported: &[Imported]) -> Result<Solid> {
    let mut kept = vec![];
    for group in groups {
        let parts: Vec<Solid> = imported
            .iter()
            .filter(|body| group.names.is_none_or(|names| names.contains(&body.name.as_str())))
            .map(|body| body.solid.clone())
            .collect();
        if let Some(names) = group.names {
            for name in names {
                ensure!(imported.iter().any(|b| b.name == *name), "the reference has no body {name}");
            }
        }
        ensure!(!parts.is_empty(), "a group selects no reference body");
        let mut solid = if group.union { Solid::union_all(&parts)? } else { Solid::compose(&parts) };
        if let Some((origin, size)) = group.cut {
            let low = v3(origin[0], origin[1], origin[2]);
            solid = solid.cut(&Solid::cuboid(low, low + v3(size[0], size[1], size[2])))?;
        }
        kept.push(solid);
    }
    Ok(Solid::compose(&kept))
}

fn p3(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// A tube swept along its centreline: its outside, less its bore when it has one.
fn sweep(tube: &Tube) -> Result<Solid> {
    let first = match tube.path.first().context("a tube has a centreline")? {
        Seg::Line([a, _]) | Seg::Arc([a, _, _]) => p3(*a),
    };
    let mut path = Centreline::new(first);
    for seg in tube.path {
        path = match seg {
            Seg::Line([_, b]) => path.line_to(p3(*b)),
            Seg::Arc([_, m, b]) => path.arc_through(p3(*m), p3(*b))?,
        };
    }
    let z = p3(tube.leaves).unit();
    let x = if z.x.abs() < 0.8 { V3::X } else { V3::Y };
    let plane = Plane::new(first, x, z)?;
    let mut profile = Profile::circle(V2::ZERO, TUBE_OD / 2.0);
    if let Some(bore) = tube.bore {
        profile = profile.with_hole(Loop::circle(V2::ZERO, bore / 2.0));
    }
    Solid::sweep_with_tolerance(&profile.place(&plane), &path, SWEEP_TOLERANCE)
}

/// A colour of the materials catalog by name, as the viewer's files carry it.
fn material(name: &str) -> Result<[f64; 3]> {
    let catalog: Value = serde_json::from_str(include_str!("../../tools/hsm/shared-data/catalog/materials.json"))?;
    let color = &catalog["colors"][name];
    let linear = hsm_shared_data::color::rgba(&color["args"], &json!({}))?
        .with_context(|| format!("no colour {name} in the materials catalog"))?;
    Ok([linear[0], linear[1], linear[2]])
}

/// The colour of the tube stock a run is cut from: its own spool, else its kind's.
fn spool_color(run: &str) -> Result<[f64; 3]> {
    let routing: Value = serde_json::from_str(include_str!("../../tools/hsm/shared-data/catalog/routing.json"))?;
    let kind = run.split('-').next().unwrap_or(run);
    let spool = routing["spool_of"][run]
        .as_str()
        .or_else(|| routing["by_prefix"][kind].as_str())
        .with_context(|| format!("no spool for {run}"))?;
    let color = &routing["spools"][spool]["color"];
    let rgb = match color["palette"].as_str() {
        Some(fluid) => hsm_shared_data::color::chips()?["port_colors"][fluid].clone(),
        None => color["bytes"].clone(),
    };
    hsm_shared_data::color::rgb8_linear(&rgb, false)
}

struct Placed {
    name: &'static str,
    color: [f64; 3],
    solid: Solid,
}

fn main() -> Result<()> {
    hsm_kernel::reads::begin();
    let out = absolute(std::env::args().nth(1).map(PathBuf::from).unwrap_or_else(|| OUT.into()))?;
    std::fs::create_dir_all(&out)?;

    let mut models: HashMap<Model, Vec<Imported>> = HashMap::new();
    let mut prototypes: HashMap<String, Solid> = HashMap::new();
    let mut placed = vec![];
    let mut rows = vec![];
    for body in BODIES {
        let p = match body {
            Body::Bought(p) => p,
            Body::Tubed(t) => {
                let color = spool_color(t.run)?;
                placed.push(Placed { name: t.name, color, solid: sweep(t)? });
                let segments: Vec<Value> = t
                    .path
                    .iter()
                    .map(|s| match s {
                        Seg::Line(points) => json!({"kind": "line", "points": points}),
                        Seg::Arc(points) => json!({"kind": "arc", "points": points}),
                    })
                    .collect();
                rows.push(json!({"name": t.name, "kind": "tube", "segments": segments, "normal": t.leaves,
                                 "od": TUBE_OD, "id": t.bore, "color": color}));
                continue;
            }
        };
        let (model, groups, paint) = selection(p.part);
        if !models.contains_key(&model) {
            models.insert(model, hsm_kernel::import::step(model.step())?);
        }
        let key = format!("{:?}", p.part);
        if !prototypes.contains_key(&key) {
            prototypes.insert(key.clone(), prototype(&groups, &models[&model])?);
        }
        let m = frame(p);
        let color = material(paint)?;
        placed.push(Placed { name: p.name, color, solid: prototypes[&key].transformed(&Affine { m }) });
        let groups: Vec<Value> = groups
            .iter()
            .map(|g| {
                let mut row = json!({});
                if let Some(names) = g.names {
                    row["names"] = json!(names);
                }
                if g.union {
                    row["union"] = json!(true);
                }
                if let Some((origin, size)) = g.cut {
                    row["cut_box"] = json!({"origin": origin, "size": size});
                }
                row
            })
            .collect();
        rows.push(json!({"name": p.name, "kind": "reference", "source": model.key(), "groups": groups,
                         "transform": m, "color": color}));
    }

    // The viewer draws each body simplified to its share of the deflection the viewer meshes
    // every other model at, scaled to the manifold's whole reach.
    let (mut low, mut high) = (v3(f64::INFINITY, f64::INFINITY, f64::INFINITY), v3(f64::NEG_INFINITY, f64::NEG_INFINITY, f64::NEG_INFINITY));
    for body in &placed {
        let b = body.solid.bounds();
        low = low.min(b.min);
        high = high.max(b.max);
    }
    let extent = ((high.x - low.x) + (high.y - low.y) + (high.z - low.z)) / 3.0;
    let tolerance = (extent * hsm_print_payload::LINEAR_DEFLECTION_RATIO).max(hsm_kernel::TOLERANCE);
    let drawing: Vec<Solid> = placed
        .iter_mut()
        .map(|b| {
            let mut drawn = b.solid.simplified_to(tolerance / 2.)?;
            b.solid.forget_backend();
            drawn.forget_backend();
            Ok(drawn)
        })
        .collect::<Result<_>>()?;
    let bodies: Vec<part::AssemblyBody> = placed
        .iter()
        .zip(&drawing)
        .map(|(b, drawn)| part::AssemblyBody { name: b.name, color: Some(b.color), fine: &b.solid, presentation: drawn })
        .collect();
    let document = json!({"presentation_tolerance_mm": tolerance,
                          "presentation_simplification_tolerance_mm": tolerance / 2.});
    println!("{}", part::write_assembly(&out, NAME, &bodies, Some(&document))?);

    // The construction the installed machine seats the manifold's valves and tees by.
    let construction = json!({"name": NAME, "bodies": rows});
    write_json(&out.join(format!("{NAME}.numbers.json")), &construction)
}

/// Writes `value` as JSON with its keys sorted, one space to a level.
fn write_json(path: &Path, value: &Value) -> Result<()> {
    let mut bytes = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(&mut bytes, serde_json::ser::PrettyFormatter::with_indent(b" "));
    serde::Serialize::serialize(value, &mut writer)?;
    bytes.push(b'\n');
    std::fs::write(path, bytes)?;
    Ok(())
}
