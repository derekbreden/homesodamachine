//! Fine-model assembly from Python's ordered references and installed frames.
//!
//! This program emits the measurement model only. Production STEP and viewer
//! drawing reduction remain separate, so importing a fine model cannot silently
//! change the approved display mesh or any printed surface.
use anyhow::{Context, Result, bail, ensure};
use hsm_geometry::{payload::Mesh, queries as geometry_queries};
use hsm_kernel::{Affine, Imported, Solid, V3, part, step, write::Body};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str> {
    value
        .get(key)
        .and_then(Value::as_str)
        .with_context(|| format!("missing text `{key}`"))
}

fn transform(value: Option<&Value>) -> Result<Option<Affine>> {
    let Some(value) = value else { return Ok(None) };
    let rows = value
        .as_array()
        .context("an installed frame is three rows of four numbers")?;
    ensure!(
        rows.len() == 3,
        "an installed frame has {} rows",
        rows.len()
    );
    let mut m = [[0.0; 4]; 3];
    for (r, row) in rows.iter().enumerate() {
        let values = row
            .as_array()
            .context("an installed frame row is an array")?;
        ensure!(
            values.len() == 4,
            "an installed frame row has {} values",
            values.len()
        );
        for (c, value) in values.iter().enumerate() {
            m[r][c] = value
                .as_f64()
                .filter(|v| v.is_finite())
                .context("a frame holds a non-finite number")?;
        }
    }
    let placed = Affine { m };
    Ok((placed != Affine::IDENTITY).then_some(placed))
}

fn assemble(instances: &Value) -> Result<Vec<Imported>> {
    let mut placed = Vec::new();
    for instance in instances
        .as_array()
        .context("instances is an ordered array")?
    {
        let model = text(instance, "model")?;
        let selected: Option<BTreeSet<usize>> = instance
            .get("indices")
            .map(|value| -> Result<_> {
                value
                    .as_array()
                    .context("indices is an array")?
                    .iter()
                    .map(|v| {
                        let index = v
                            .as_u64()
                            .and_then(|n| usize::try_from(n).ok())
                            .context("an entry index is a nonnegative integer")?;
                        Ok(index)
                    })
                    .collect()
            })
            .transpose()?;
        let frame = transform(instance.get("transform"))?;
        let name = instance
            .get("name")
            .map(|v| v.as_str().context("a component name is text"))
            .transpose()?;
        let prefix = instance
            .get("prefix")
            .map(|v| v.as_str().context("a name prefix is text"))
            .transpose()?
            .unwrap_or("");
        let color = instance
            .get("color")
            .map(|value| -> Result<Option<[f64; 3]>> {
                if value.is_null() {
                    return Ok(None);
                }
                let values = value
                    .as_array()
                    .context("a color is three linear channels or null")?;
                ensure!(values.len() == 3, "a color has {} channels", values.len());
                let mut rgb = [0.0; 3];
                for (i, channel) in values.iter().enumerate() {
                    rgb[i] = channel
                        .as_f64()
                        .filter(|v| v.is_finite())
                        .context("a color holds a non-finite channel")?;
                }
                Ok(Some(rgb))
            })
            .transpose()?;
        let count = hsm_kernel::import::visit_model(model, |index, mut part| {
            if selected
                .as_ref()
                .is_some_and(|indices| !indices.contains(&index))
            {
                return Ok(());
            }
            part.name = match name {
                Some(name) => name.to_owned(),
                None => format!("{prefix}{}", part.name),
            };
            if let Some(color) = color {
                part.color = color;
            }
            if let Some(frame) = &frame {
                part.solid = part.solid.transformed(frame);
            }
            placed.push(part);
            Ok(())
        })?;
        if let Some(selected) = &selected {
            ensure!(selected.iter().all(|&index| index < count),
                    "a selected entry is outside {model}'s {count} solids");
        }
    }
    Ok(placed)
}

fn residual(solid: &Solid) -> Value {
    if solid.is_empty() {
        json!({"volume_mm3":0.0,"min":null,"max":null})
    } else {
        let bounds = solid.bounds();
        json!({"volume_mm3":solid.volume(),"min":bounds.min.to_array(),"max":bounds.max.to_array()})
    }
}

fn common(a: &Solid, b: &Solid, query: &Value, parts: &[Imported]) -> Result<Value> {
    let mut hit = a.intersect(b)?;
    let raw = residual(&hit);
    let threshold = query.get("mask_above_mm3").map(|v| {
        v.as_f64().filter(|v| v.is_finite() && *v >= 0.0)
            .context("mask threshold is finite and nonnegative")
    }).transpose()?.unwrap_or(0.0);
    let apply_masks = hit.volume() > threshold;
    let mut stages = Vec::new();
    if let Some(values) = query.get("fine_mask_stages") {
        for stage in values.as_array().context("fine mask stages is an array")? {
            let indices = operand(stage.get("indices"), parts.len())?;
            for &index in &indices {
                if apply_masks && hit.volume() > 0.0 {
                    hit = hit.cut(&parts[index].solid)?;
                }
            }
            stages.push(json!({"name":text(stage,"name")?,"indices":indices,
                               "residual":residual(&hit),"masks_applied":apply_masks}));
        }
    }
    if let Some(values) = query.get("mask_stages") {
        for stage in values.as_array().context("mask stages is an array")? {
            let spheres = stage["spheres"].as_array().context("mask spheres is an array")?;
            for sphere in spheres {
                let center = sphere["center_mm"].as_array().context("sphere center is a three-vector")?;
                ensure!(center.len() == 3, "sphere center has {} coordinates", center.len());
                let mut point = [0.0; 3];
                for (i, value) in center.iter().enumerate() {
                    point[i] = value.as_f64().filter(|v| v.is_finite())
                        .context("sphere center is not finite")?;
                }
                let radius = sphere["radius_mm"].as_f64()
                    .filter(|v| v.is_finite() && *v > 0.0).context("sphere radius must be positive and finite")?;
                if apply_masks && hit.volume() >= 1e-12 {
                    hit = hit.cut(&Solid::sphere(V3::from(point), radius)?)?;
                }
            }
            stages.push(json!({"name":text(stage,"name")?,"spheres":spheres,
                               "residual":residual(&hit),"masks_applied":apply_masks}));
        }
    }
    Ok(json!({"raw":raw,"stages":stages,"residual":residual(&hit)}))
}

fn operand(value: Option<&Value>, count: usize) -> Result<Vec<usize>> {
    let value = value.context("a query operand is a solid index or ordered index array")?;
    let values = value.as_array().map(Vec::as_slice).unwrap_or(std::slice::from_ref(value));
    ensure!(!values.is_empty(), "a query operand needs a solid");
    let indices = values.iter().map(|value| {
        let index = value.as_u64().and_then(|n| usize::try_from(n).ok())
            .context("a query solid index is nonnegative")?;
        ensure!(index < count, "query solid {index} is outside {count} solids");
        Ok(index)
    }).collect::<Result<Vec<_>>>()?;
    ensure!(indices.iter().copied().collect::<BTreeSet<_>>().len() == indices.len(),
            "a query operand repeats a solid");
    Ok(indices)
}

fn query_solid<'a>(parts: &'a [Imported], groups: &'a BTreeMap<Vec<usize>, Solid>,
                   indices: &[usize]) -> &'a Solid {
    if indices.len() == 1 { &parts[indices[0]].solid } else { &groups[indices] }
}

fn summed_residual(values: &[&Value]) -> Value {
    let volume: f64 = values.iter().map(|value| value["volume_mm3"].as_f64().unwrap()).sum();
    let occupied = values.iter().filter(|value| value["min"].is_array()).collect::<Vec<_>>();
    if occupied.is_empty() {
        return json!({"volume_mm3":volume,"min":null,"max":null});
    }
    let lower = (0..3).map(|axis| occupied.iter()
        .map(|value| value["min"][axis].as_f64().unwrap()).fold(f64::INFINITY, f64::min)).collect::<Vec<_>>();
    let upper = (0..3).map(|axis| occupied.iter()
        .map(|value| value["max"][axis].as_f64().unwrap()).fold(f64::NEG_INFINITY, f64::max)).collect::<Vec<_>>();
    json!({"volume_mm3":volume,"min":lower,"max":upper})
}

fn distributed_common(parts: &[Imported], left: &[usize], right: &Solid, query: &Value) -> Result<Value> {
    let rows = left.iter().map(|&index| common(&parts[index].solid, right, query, parts))
        .collect::<Result<Vec<_>>>()?;
    let mut stages = rows[0]["stages"].as_array().unwrap().clone();
    for (index, stage) in stages.iter_mut().enumerate() {
        stage["residual"] = summed_residual(&rows.iter().map(|row| &row["stages"][index]["residual"]).collect::<Vec<_>>());
        stage["masks_applied"] = json!(rows.iter().any(|row| row["stages"][index]["masks_applied"] == true));
    }
    Ok(json!({"raw":summed_residual(&rows.iter().map(|row| &row["raw"]).collect::<Vec<_>>()),
              "stages":stages,"residual":summed_residual(&rows.iter().map(|row| &row["residual"]).collect::<Vec<_>>())}))
}

fn query(parts: &mut [Imported], queries: &Value) -> Result<Vec<Value>> {
    let mut gap_meshes = BTreeMap::new();
    let mut groups = BTreeMap::new();
    let values = queries.as_array().context("queries is an ordered array")?;
    let operands = values.iter().map(|value| {
        Ok((operand(value.get("a"), parts.len())?, operand(value.get("b"), parts.len())?))
    }).collect::<Result<Vec<_>>>()?;
    let mut last = BTreeMap::new();
    for (index, (a, b)) in operands.iter().enumerate() {
        last.insert(a.clone(), index);
        last.insert(b.clone(), index);
    }
    let mut readings = Vec::with_capacity(values.len());
    for (index, (value, (a, b))) in values.iter().zip(&operands).enumerate() {
            let kind = text(value, "kind")?;
            let distribute = kind == "common" && value.get("distribute_a").and_then(Value::as_bool).unwrap_or(false);
            for indices in [a, b] {
                if distribute && indices == a && indices != b { continue; }
                if indices.len() > 1 && !groups.contains_key(indices) {
                    // meshcad.manifold resolves a compound's union for cross-body queries.
                    let solids = indices.iter().map(|&i| parts[i].solid.clone()).collect::<Vec<_>>();
                    groups.insert(indices.clone(), Solid::union_all(&solids)?);
                }
            }
            let reading = if kind == "common" {
                let answer = if distribute {
                    distributed_common(parts, a, query_solid(parts, &groups, b), value)
                } else {
                    common(query_solid(parts, &groups, a), query_solid(parts, &groups, b), value, parts)
                };
                let result = match answer {
                    Ok(result) => json!({"a":value["a"],"b":value["b"],"kind":kind,"common":result}),
                    Err(error) => json!({"a":value["a"],"b":value["b"],"kind":kind,"error":format!("{error:#}")}),
                };
                for indices in [a, b] {
                    if indices.len() == 1 { parts[indices[0]].solid.forget_backend(); }
                    else if let Some(group) = groups.get_mut(indices) { group.forget_backend(); }
                    for &part in indices { parts[part].solid.forget_backend(); }
                }
                if let Some(stages) = value.get("fine_mask_stages") {
                    for stage in stages.as_array().context("fine mask stages is an array")? {
                        for mask in operand(stage.get("indices"), parts.len())? {
                            parts[mask].solid.forget_backend();
                        }
                    }
                }
                result
            } else {
              let result = match kind {
                "gap" if a == b => {
                    ensure!(!query_solid(parts, &groups, a).is_empty(), "a gap needs two nonempty solids");
                    0.0
                },
                "gap" => {
                    for indices in [a, b] {
                        if !gap_meshes.contains_key(indices) {
                            let solid = query_solid(parts, &groups, indices);
                            let mesh = Mesh::from_arrays(parts[indices[0]].name.clone(),
                                solid.verts().iter().map(|p| p.to_array()).collect(),
                                solid.tris().to_vec())?;
                            gap_meshes.insert(indices.clone(), mesh);
                        }
                    }
                    let reading = geometry_queries::gap(&gap_meshes[a], &gap_meshes[b], [0.0; 3])?;
                    reading.clearance_mm.with_context(|| format!("fine gap: {}",
                        reading.volume_error.as_deref().unwrap_or("no solid clearance")))?
                },
                "shared_volume" => query_solid(parts, &groups, a).shared_volume(query_solid(parts, &groups, b))?,
                _ => bail!("unknown model query {kind:?}"),
              };
              json!({"a":value["a"],"b":value["b"],"kind":kind,"value":result})
            };
            readings.push(reading);
            for indices in [a, b] {
                if last[indices] == index {
                    gap_meshes.remove(indices);
                    groups.remove(indices);
                    for &part in indices { parts[part].solid.forget_backend(); }
                }
            }
    }
    Ok(readings)
}

fn summary(part: &Imported, components: bool) -> Value {
    let bounds = part.solid.bounds();
    let mut result = json!({"name":part.name,"color":part.color,"vertices":part.solid.verts().len(),
           "triangles":part.solid.tris().len(),"faces":part.solid.faces().len(),
           "volume":part.solid.volume(),"center":part.solid.centroid().to_array(),
           "min":bounds.min.to_array(),"max":bounds.max.to_array()});
    if components {
        result["components"] = json!(part.solid.components().iter().map(|solid| {
            let bounds = solid.bounds();
            json!({"volume":solid.volume(),"min":bounds.min.to_array(),"max":bounds.max.to_array()})
        }).collect::<Vec<_>>());
    }
    result
}

fn model_summaries(instances: &Value, components: &BTreeSet<String>) -> Result<Option<Vec<Value>>> {
    let Some(instances) = instances.as_array() else {
        return Ok(None);
    };
    // The wiring reader asks for model measurements, with no placement or cross-body query.
    // Retain only the small summaries while each imported body passes its existing checks.
    if !instances.iter().all(|instance| {
        instance
            .as_object()
            .is_some_and(|fields| fields.len() == 1 && fields.contains_key("model"))
    }) {
        return Ok(None);
    }
    let mut summaries = Vec::new();
    for instance in instances {
        hsm_kernel::import::visit_model(text(instance, "model")?, |_index, part| {
            summaries.push(summary(&part, components.contains(&part.name)));
            Ok(())
        })?;
    }
    Ok(Some(summaries))
}

fn write_model(path: &Path, bodies: &[Body<'_>]) -> Result<()> {
    let bytes = step::model_bytes(bodies);
    let name = path
        .file_name()
        .and_then(|v| v.to_str())
        .context("model output has no file name")?;
    let temporary = path.with_file_name(format!(".{name}.{}", std::process::id()));
    std::fs::write(&temporary, bytes)
        .with_context(|| format!("writing {}", temporary.display()))?;
    std::fs::rename(&temporary, path).with_context(|| format!("writing {}", path.display()))
}

fn main() -> Result<()> {
    let (numbers, output) = part::args()?;
    let components: BTreeSet<String> = match numbers.get("component_names") {
        Ok(value) => value.as_array().context("component names is an array")?.iter()
            .map(|value| value.as_str().map(str::to_owned).context("a component name is text"))
            .collect::<Result<_>>()?,
        Err(_) => BTreeSet::new(),
    };
    let queries = numbers.get("queries")?;
    if output == Path::new("--check") && queries.as_array().is_some_and(|rows| rows.is_empty()) {
        if let Some(summaries) = model_summaries(numbers.get("instances")?, &components)? {
            println!("{}", json!({"files":[],"bodies":summaries,"queries":[]}));
            return Ok(());
        }
    }
    let mut parts = assemble(numbers.get("instances")?)?;
    let readings = query(&mut parts, queries)?;
    let bodies: Vec<Body<'_>> = parts
        .iter()
        .map(|part| Body {
            name: &part.name,
            color: part.color,
            solid: &part.solid,
        })
        .collect();
    let mut files = Vec::new();
    if output != Path::new("--check") {
        std::fs::create_dir_all(&output)?;
        let name = numbers.text("name")?;
        ensure!(
            Path::new(name).file_name().and_then(|v| v.to_str()) == Some(name),
            "model name must be one file name"
        );
        let file = format!("{name}.step.npz");
        write_model(&output.join(&file), &bodies)?;
        files.push(file);
    }
    let summaries: Vec<Value> = parts.iter().map(|part| summary(part, components.contains(&part.name))).collect();
    println!(
        "{}",
        json!({"files":files,"bodies":summaries,"queries":readings})
    );
    Ok(())
}
