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

pub(crate) fn transform(value: Option<&Value>) -> Result<Option<Affine>> {
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

pub(crate) fn assemble(instances: &Value) -> Result<Vec<Imported>> {
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
        let visit = |_index, mut part: Imported| {
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
        };
        let count = if let Some(indices) = &selected {
            hsm_kernel::import::visit_model_indices(model, indices, visit)?
        } else {
            hsm_kernel::import::visit_model(model, visit)?
        };
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
    let mut raw = residual(&hit);
    let positive_components = query.get("positive_components").map(|value| {
        value.as_bool().context("positive_components is a boolean")
    }).transpose()?.unwrap_or(false);
    if positive_components {
        raw["components"] = json!(hit.components().iter()
            .filter(|component| component.volume() > 0.0)
            .map(residual).collect::<Vec<_>>());
    }
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
    let components = values.iter().any(|value| value.get("components").is_some()).then(||
        values.iter().filter_map(|value| value.get("components").and_then(Value::as_array))
            .flatten().cloned().collect::<Vec<_>>());
    if occupied.is_empty() {
        let mut result = json!({"volume_mm3":volume,"min":null,"max":null});
        if let Some(components) = components { result["components"] = json!(components); }
        return result;
    }
    let lower = (0..3).map(|axis| occupied.iter()
        .map(|value| value["min"][axis].as_f64().unwrap()).fold(f64::INFINITY, f64::min)).collect::<Vec<_>>();
    let upper = (0..3).map(|axis| occupied.iter()
        .map(|value| value["max"][axis].as_f64().unwrap()).fold(f64::NEG_INFINITY, f64::max)).collect::<Vec<_>>();
    let mut result = json!({"volume_mm3":volume,"min":lower,"max":upper});
    if let Some(components) = components { result["components"] = json!(components); }
    result
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

fn box_operand(value: &Value) -> Result<Solid> {
    let points = value.as_array().context("a box operand has its low and high points")?;
    ensure!(points.len() == 2, "a box operand has two points");
    let mut xyz = [[0.0; 3]; 2];
    for (i, point) in points.iter().enumerate() {
        let coordinates = point.as_array().context("a box point is a three-vector")?;
        ensure!(coordinates.len() == 3, "a box point has three coordinates");
        for (k, coordinate) in coordinates.iter().enumerate() {
            xyz[i][k] = coordinate.as_f64().filter(|v| v.is_finite())
                .context("a box coordinate is finite")?;
        }
    }
    ensure!((0..3).all(|k| xyz[1][k] > xyz[0][k]), "a box operand has positive spans");
    Ok(Solid::cuboid(V3::from(xyz[0]), V3::from(xyz[1])))
}


/// Search representations that may be rebuilt without changing the raw model.
/// The byte budget counts the exact source arrays underlying a cached operand;
/// native scratch and the two operands of one question can exceed that estimate.
pub(crate) struct SearchRetention {
    pub array_bytes: usize,
}

struct SearchUse {
    next: Option<usize>,
    bytes: usize,
}

pub(crate) fn operand_bytes(parts: &[Imported], indices: &[usize]) -> usize {
    indices.iter().map(|&i| {
        let s = &parts[i].solid;
        std::mem::size_of_val(s.verts()) + std::mem::size_of_val(s.tris())
            + std::mem::size_of_val(s.face_of()) + std::mem::size_of_val(s.faces())
    }).sum()
}

fn forget_search(parts: &mut [Imported], groups: &mut BTreeMap<Vec<usize>, Solid>,
                 meshes: &mut BTreeMap<Vec<usize>, Mesh>, indices: &[usize]) {
    // Cached compound arrays and unbounded-gap meshes have no identity outside
    // this question batch. Every source array and record stays in `parts`.
    groups.remove(indices);
    meshes.remove(indices);
    for &i in indices { parts[i].solid.forget_backend(); }
}

pub(crate) fn retained_query(parts: &mut [Imported], queries: &Value,
                            retention: SearchRetention) -> Result<Vec<Value>> {
    query_with_retention(parts, queries, false, Some(retention))
}

pub(crate) fn query(parts: &mut [Imported], queries: &Value, query_only: bool) -> Result<Vec<Value>> {
    query_with_retention(parts, queries, query_only, None)
}

fn query_with_retention(parts: &mut [Imported], queries: &Value, query_only: bool,
                        retention: Option<SearchRetention>) -> Result<Vec<Value>> {
    let mut gap_meshes = BTreeMap::new();
    let mut groups = BTreeMap::new();
    let values = queries.as_array().context("queries is an ordered array")?;
    let operands = values.iter().map(|value| {
        let b = if value.get("b_box").is_some() {
            ensure!(text(value, "kind")? == "common" && value.get("b").is_none(),
                    "a common query has one b operand");
            vec![]
        } else { operand(value.get("b"), parts.len())? };
        Ok((operand(value.get("a"), parts.len())?, b))
    }).collect::<Result<Vec<_>>>()?;
    let mut last = BTreeMap::new();
    for (index, (a, b)) in operands.iter().enumerate() {
        last.insert(a.clone(), index);
        if !b.is_empty() { last.insert(b.clone(), index); }
    }
    let mut next_use = vec![[None; 2]; values.len()];
    if query_only || retention.is_some() {
        let mut future = BTreeMap::new();
        for (index, (a, b)) in operands.iter().enumerate().rev() {
            for (side, indices) in [a, b].into_iter().enumerate() {
                if !indices.is_empty() { next_use[index][side] = future.get(indices).copied(); }
            }
            for indices in [a, b] {
                if !indices.is_empty() { future.insert(indices.clone(), index); }
            }
        }
    }
    let mut release_at = vec![Vec::new(); values.len()];
    if query_only {
        let mut part_last = vec![None; parts.len()];
        for (index, (value, (a, b))) in values.iter().zip(&operands).enumerate() {
            for &part in a.iter().chain(b) { part_last[part] = Some(index); }
            if let Some(stages) = value.get("fine_mask_stages") {
                for stage in stages.as_array().context("fine mask stages is an array")? {
                    for part in operand(stage.get("indices"), parts.len())? {
                        part_last[part] = Some(index);
                    }
                }
            }
        }
        for (part, at) in part_last.into_iter().enumerate() {
            if let Some(at) = at { release_at[at].push(part); }
        }
    }
    let mut readings = Vec::with_capacity(values.len());
    let mut searched: BTreeMap<Vec<usize>, SearchUse> = BTreeMap::new();
    for (index, (value, (a, b))) in values.iter().zip(&operands).enumerate() {
            let kind = text(value, "kind")?;
            let distribute = kind == "common" && value.get("distribute_a").and_then(Value::as_bool).unwrap_or(false);
            if let Some(policy) = &retention {
                for (side, indices) in [a, b].into_iter().enumerate() {
                    if !indices.is_empty() {
                        // Unbounded gaps own a separate mesh/search structure.
                        // Charge both representations before retaining native
                        // data for a following common-volume question.
                        let gap_copy = gap_meshes.contains_key(indices) ||
                            (kind == "gap" && value.get("within_mm").is_none() && a != b);
                        searched.insert(indices.clone(), SearchUse { next: next_use[index][side],
                            bytes: operand_bytes(parts, indices) * if gap_copy { 2 } else { 1 } });
                    }
                }
                // Bound retained search state before constructing new operands.
                // A single question always keeps both its exact operands.
                while searched.values().map(|s| s.bytes).sum::<usize>() > policy.array_bytes {
                    // The complete question order is known. Keep the expensive
                    // representation needed soonest, regardless of when it was
                    // last used; this changes no question or operand order.
                    let farthest = searched.iter().filter(|(indices, _)| *indices != a && *indices != b)
                        .max_by_key(|(_, used)| used.next.unwrap_or(usize::MAX))
                        .map(|(indices, _)| indices.clone());
                    let Some(indices) = farthest else { break; };
                    forget_search(parts, &mut groups, &mut gap_meshes, &indices);
                    searched.remove(&indices);
                }
            }
            for indices in [a, b] {
                if indices.is_empty() { continue; }
                if distribute && indices == a && indices != b { continue; }
                if indices.len() > 1 && !groups.contains_key(indices) {
                    // meshcad.manifold resolves a compound's union for cross-body queries.
                    let solids = indices.iter().map(|&i| parts[i].solid.clone()).collect::<Vec<_>>();
                    groups.insert(indices.clone(), Solid::union_all(&solids)?);
                }
            }
            let reading = if kind == "common" {
                let boxed = value.get("b_box").map(box_operand).transpose()?;
                let right = boxed.as_ref().unwrap_or_else(|| query_solid(parts, &groups, b));
                let answer = if distribute {
                    distributed_common(parts, a, right, value)
                } else {
                    common(query_solid(parts, &groups, a), right, value, parts)
                };
                let mut result = json!({"a":value["a"],"kind":kind});
                if boxed.is_some() { result["b_box"] = value["b_box"].clone(); }
                else { result["b"] = value["b"].clone(); }
                match answer {
                    Ok(reading) => result["common"] = reading,
                    Err(error) => result["error"] = json!(format!("{error:#}")),
                }
                if retention.is_none() && !value.get("retain_until_last_use")
                    .and_then(Value::as_bool).unwrap_or(false) {
                    for indices in [a, b] {
                        if indices.is_empty() { continue; }
                        if indices.len() == 1 { parts[indices[0]].solid.forget_backend(); }
                        else if let Some(group) = groups.get_mut(indices) { group.forget_backend(); }
                        for &part in indices { parts[part].solid.forget_backend(); }
                    }
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
                "gap" if value.get("within_mm").is_some() => {
                    let within = value["within_mm"].as_f64().context("gap within_mm is a number")?;
                    query_solid(parts, &groups, a).gap_within(query_solid(parts, &groups, b), within)?
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
            // Query-only clearance sweeps retain nearby reuse without holding every
            // native search representation for the entire sweep. Mesh arrays stay exact.
            if query_only && kind == "gap" && value.get("within_mm").is_some() {
                for (side, indices) in [a, b].into_iter().enumerate() {
                    if next_use[index][side].is_some_and(|next| next - index > 64) {
                        if indices.len() == 1 { parts[indices[0]].solid.forget_backend(); }
                        else if let Some(group) = groups.get_mut(indices) { group.forget_backend(); }
                    }
                }
            }
            if retention.is_some() {
                for (side, indices) in [a, b].into_iter().enumerate() {
                    // A distant next use does not cost anything while this
                    // operand fits the bounded cache. Budget pressure, rather
                    // than an arbitrary number of questions, chooses eviction.
                    if !indices.is_empty() && next_use[index][side].is_none() {
                        forget_search(parts, &mut groups, &mut gap_meshes, indices);
                        searched.remove(indices);
                    }
                }
            }
            for indices in [a, b] {
                if indices.is_empty() { continue; }
                if last[indices] == index {
                    gap_meshes.remove(indices);
                    groups.remove(indices);
                    searched.remove(indices);
                    for &part in indices { parts[part].solid.forget_backend(); }
                }
            }
            // A query-only caller needs no later body summary or model export.
            // Count actual entries across groups and masks before dropping raw geometry.
            for &part in &release_at[index] { parts[part].solid = Solid::empty(); }
    }
    Ok(readings)
}

pub(crate) fn summary(part: &Imported, components: bool) -> Value {
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
    let query_only = match numbers.get("query_only") {
        Ok(value) => value.as_bool().context("query_only is a boolean")?,
        Err(_) => false,
    };
    ensure!(!query_only || output == Path::new("--check"), "query-only requests do not write a model");
    if !query_only && output == Path::new("--check") && queries.as_array().is_some_and(|rows| rows.is_empty()) {
        if let Some(summaries) = model_summaries(numbers.get("instances")?, &components)? {
            println!("{}", json!({"files":[],"bodies":summaries,"queries":[]}));
            return Ok(());
        }
    }
    let mut parts = assemble(numbers.get("instances")?)?;
    let readings = query(&mut parts, queries, query_only)?;
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
    let summaries: Vec<Value> = if query_only { Vec::new() } else {
        parts.iter().map(|part| summary(part, components.contains(&part.name))).collect()
    };
    println!(
        "{}",
        json!({"files":files,"bodies":summaries,"queries":readings})
    );
    Ok(())
}
