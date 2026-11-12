//! Each conductor and termination retains its own fine geometry and shared presentation object.
use super::wire_request::{Part, Request, Shape, Wire};
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Body, Solid};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};

#[path = "../../manifold-layout/installed-machine/cache.rs"]
mod stage_cache;

/// One thing to cut: a conductor, or a termination or jacket.
#[derive(Clone, Copy)]
enum Entity<'a> {
    Wire(&'a Wire),
    Part(&'a Part),
}

impl Entity<'_> {
    fn name(&self) -> &str {
        match self {
            Entity::Wire(wire) => &wire.name,
            Entity::Part(part) => &part.name,
        }
    }

    fn colour(&self) -> [f64; 3] {
        match self {
            Entity::Wire(wire) => wire.linear_rgb,
            Entity::Part(part) => part.linear_rgb,
        }
    }

    /// The name the entity's fine model is retained under.
    fn id(&self) -> String {
        match self {
            Entity::Wire(wire) => format!("route:{}", wire.name),
            Entity::Part(part) => format!("component:{}", part.name),
        }
    }

    /// The diameter of a swept section, which its presentation tolerance follows.
    fn diameter(&self) -> Option<f64> {
        match self {
            Entity::Wire(wire) => Some(wire.diameter_mm),
            Entity::Part(part) => match &part.shape {
                Shape::Sweep { diameter_mm, .. } | Shape::AnnularSweep { diameter_mm, .. } => {
                    Some(*diameter_mm)
                }
                _ => None,
            },
        }
    }

    /// The entity as it is asked for, which its fine model is retained against.
    fn recipe(&self) -> Result<Value> {
        Ok(match self {
            Entity::Wire(wire) => serde_json::to_value(wire)?,
            Entity::Part(part) => serde_json::to_value(part)?,
        })
    }

    fn build(&self) -> Result<Vec<Solid>> {
        match self {
            Entity::Wire(wire) => Ok(vec![super::wire(&wire.segments, wire.diameter_mm)?]),
            Entity::Part(part) => super::wire_components::build(&part.shape),
        }
    }
}

/// The request's conductors, then its terminations and jackets.
fn entities(request: &Request) -> impl Iterator<Item = Entity<'_>> {
    request
        .routes
        .iter()
        .map(Entity::Wire)
        .chain(request.components.iter().map(Entity::Part))
}

fn records(name: &str, rgb: [f64; 3], parts: &[Solid]) -> Vec<Value> {
    parts.iter().map(|solid| {
        let bounds=solid.bounds();
        json!({"name":name,"color":rgb,"min":bounds.min.to_array(),"max":bounds.max.to_array(),
            "volume":solid.volume(),"area":solid.area(),"center":solid.centroid().to_array(),
            "vertices":solid.verts().len(),"triangles":solid.tris().len(),"faces":solid.faces().len()})
    }).collect()
}

fn key(name: &str) -> String {
    hsm_model_export::digest(name.as_bytes())
}

/// The same request supplies explicit checks and retained production geometry.
pub fn run(request: &Request, output: &Path) -> Result<Value> {
    if output == Path::new("--check") {
        let mut rows = Vec::new();
        for entity in entities(request) {
            rows.extend(records(entity.name(), entity.colour(), &entity.build()?));
        }
        return Ok(json!({"files":[],"bodies":rows}));
    }
    std::fs::create_dir_all(output)?;
    let root = std::path::absolute(".")?;
    let parts_dir = output.join("parts");
    std::fs::create_dir_all(&parts_dir)?;
    let _work_lock = stage_cache::lock(&parts_dir)?;
    let mut cache = stage_cache::Cache::new(&root, &parts_dir)?;
    let mut cut = Vec::new();
    for entity in entities(request) {
        let name = entity.name();
        let id = entity.id();
        let fine = parts_dir.join(format!("{}.npz", key(&id)));
        let rgb = entity.colour();
        let record = cache.run(&format!("fine {id}"), &entity.recipe()?, &[fine.clone()], || {
            let mut solids = entity.build().with_context(|| format!("building {name}"))?;
            for solid in &mut solids {
                solid.forget_backend();
            }
            let rows = records(name, rgb, &solids);
            let bodies: Vec<_> = solids
                .iter()
                .map(|solid| Body {
                    name,
                    color: Some(rgb),
                    solid,
                })
                .collect();
            hsm_kernel::step::write_model(&fine, &bodies)?;
            Ok(json!({"name":name,"fine":fine,"bodies":rows,"diameter_mm":entity.diameter()}))
        })?;
        cut.push(record);
    }
    let mut lower = [f64::INFINITY; 3];
    let mut upper = [f64::NEG_INFINITY; 3];
    for body in cut
        .iter()
        .flat_map(|entity| entity["bodies"].as_array().into_iter().flatten())
    {
        for k in 0..3 {
            lower[k] = lower[k].min(body["min"][k].as_f64().context("wire bound")?);
            upper[k] = upper[k].max(body["max"][k].as_f64().context("wire bound")?);
        }
    }
    ensure!(
        lower.iter().chain(&upper).all(|v| v.is_finite()),
        "wire assembly is empty"
    );
    let deflection =
        (0..3).map(|k| upper[k] - lower[k]).sum::<f64>() / 3. * request.presentation_deflection_ratio;
    let angular = request.presentation_angular_deflection_rad;
    let angular_tolerance =
        |diameter: f64| deflection.min(diameter / 2. * (1. - (angular / 2.).cos()));
    let radius = request
        .routes
        .iter()
        .map(|wire| wire.diameter_mm)
        .fold(f64::INFINITY, f64::min)
        / 2.;
    let fallback = deflection.min(radius * (1. - (angular / 2.).cos()));
    let mut entries = Vec::new();
    let mut nodes = Vec::new();
    let mut bodies = Vec::new();
    let mut tolerances = serde_json::Map::new();
    let mut fine_digests = Vec::new();
    for entity in &cut {
        let name = entity["name"].as_str().unwrap();
        let fine = PathBuf::from(entity["fine"].as_str().context("retained wire model")?);
        let fine_sha = cache.input_digest(&fine)?;
        let tolerance = entity["diameter_mm"]
            .as_f64()
            .map(angular_tolerance)
            .unwrap_or(fallback);
        let mesh = parts_dir.join(format!("{}.step.mesh", key(name)));
        let recipe = json!({"fine_sha256":fine_sha,"tolerance_mm":tolerance});
        cache.run(
            &format!("presentation {name}"),
            &recipe,
            &[mesh.clone()],
            || {
                let mut imported = hsm_kernel::import::model(&fine)?;
                let mut shown = Vec::new();
                for part in &mut imported {
                    shown.push(
                        super::presentation(&part.solid, tolerance)
                            .with_context(|| format!("presenting {name}"))?,
                    );
                    part.solid.forget_backend();
                }
                let names: Vec<_> = (0..imported.len())
                    .map(|i| {
                        if imported.len() == 1 {
                            name.to_owned()
                        } else {
                            format!("{name}/{}", i + 1)
                        }
                    })
                    .collect();
                let displayed: Vec<_> = shown
                    .iter()
                    .enumerate()
                    .map(|(i, solid)| Body {
                        name: &names[i],
                        color: imported[i].color,
                        solid,
                    })
                    .collect();
                let bytes = hsm_kernel::write::payload_bytes_with_sources(
                    &displayed,
                    Some(&fine_sha),
                    None,
                );
                let mut head = hsm_geometry::scene::pack(&bytes)?;
                head["source_kind"] = json!("model");
                head["step_export"] = json!(false);
                hsm_geometry::scene::persist(&mesh, &head)?;
                Ok(json!({"mesh":mesh}))
            },
        )?;
        let head = hsm_geometry::scene::pack(&std::fs::read(&mesh)?)?;
        nodes.extend(
            head["meshes"]
                .as_array()
                .context("wire scene nodes")?
                .iter()
                .cloned(),
        );
        for (index, body) in entity["bodies"]
            .as_array()
            .context("fine wire bodies")?
            .iter()
            .enumerate()
        {
            entries.push(json!([fine, index, name, body["color"]]));
            let mut body = body.clone();
            body["presentation_tolerance_mm"] = json!(tolerance);
            bodies.push(body);
        }
        tolerances.insert(name.to_owned(), json!(tolerance));
        fine_digests.push(json!({"name":name,"sha256":fine_sha}));
    }
    let root_name = request.name.as_str();
    let file_stem = request.file_stem.as_deref().unwrap_or(root_name);
    let fine = output.join(format!("{file_stem}.step.npz"));
    let mesh = output.join(format!("{file_stem}.step.mesh"));
    let mut head = json!({"v":4,"meshes":nodes,"source_kind":"scene","step_export":false});
    head["src"] = json!(hsm_geometry::scene::digest(&serde_json::to_vec(
        &head["meshes"]
    )?));
    let recipe = json!({"parts":fine_digests,"presentation":head,"root":root_name,
        "angular":angular,"tolerances":tolerances});
    let result=cache.run("wire assembly",&recipe,&[fine.clone(),mesh.clone()],|| {
        hsm_geometry::scene::persist(&mesh,&head)?;
        let payload=std::fs::read(&mesh)?;
        let document=json!({"schema":"hsm-installed-wires-1","frame":"Enclosure assembly XYZ; Z up",
            "presentation_tolerance_mm":fallback,"presentation_angular_deflection_rad":angular,
            "presentation_surface_partitions":"coalesced with complete fine-face contributors",
            "presentation_tolerance_by_name_mm":tolerances,
            "alpha_by_name":cut.iter().map(|entity|(entity["name"].as_str().unwrap().to_owned(),json!(1.))).collect::<serde_json::Map<_,_>>(),
            "presentation":{"path":format!("{file_stem}.step.mesh"),"sha256":hsm_geometry::scene::digest(&payload)}});
        hsm_model_export::model::entries(&json!({"target":fine,"entries":entries,"document":document}),output)?;
        Ok(json!({"files":[format!("{file_stem}.step.npz"),format!("{file_stem}.step.mesh")],"bodies":bodies}))
    })?;
    Ok(result)
}
