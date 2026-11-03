//! Fine tube samples, read one named tube group at a time.
use anyhow::{Context, Result, ensure};
use hsm_geometry::{payload::Mesh, queries};
use hsm_kernel::{import, part};
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

fn point(value: &Value) -> Result<[f64; 3]> {
    let values = value.as_array().context("a tube sample has three coordinates")?;
    ensure!(values.len() == 3, "a tube sample has three coordinates");
    let mut answer = [0.0; 3];
    for (axis, value) in values.iter().enumerate() {
        answer[axis] = value.as_f64().filter(|x| x.is_finite()).context("a tube sample is finite")?;
    }
    Ok(answer)
}

fn read_group(spec: &Value, meshes: &[Mesh]) -> Result<Value> {
    let started = std::time::Instant::now();
    let mut batches = Vec::new();
    for batch in spec["batches"].as_array().context("tube batches are ordered")? {
        let tolerance = batch.get("inside_tolerance_mm")
            .map(|value| value.as_f64().filter(|x| x.is_finite() && *x > 0.0)
                 .context("containment tolerance is positive")).transpose()?;
        let mut samples = Vec::new();
        for value in batch["points"].as_array().context("tube points are ordered")? {
            let point = point(value)?;
            let mut distance = f64::INFINITY;
            let mut inside = false;
            for mesh in meshes {
                distance = distance.min(queries::surface_distance(mesh, point)?);
                if let Some(tolerance) = tolerance {
                    if !inside { inside = queries::contains_probe(mesh, point, tolerance)?; }
                }
            }
            ensure!(distance.is_finite(), "a tube sample needs a nonempty surface");
            samples.push(json!({"distance_mm":distance,
                                "inside":tolerance.map(|_| inside)}));
        }
        batches.push(json!({"name":batch["name"], "samples":samples}));
    }
    Ok(json!({"name":spec["name"], "batches":batches,
              "seconds":started.elapsed().as_secs_f64()}))
}

fn main() -> Result<()> {
    let (numbers, _output) = part::args()?;
    let groups = numbers.get("groups")?.as_array().context("tube groups are ordered")?;
    let mut owners = BTreeMap::new();
    let mut final_indices = Vec::new();
    for (group, spec) in groups.iter().enumerate() {
        let indices = spec["indices"].as_array().context("tube indices are ordered")?;
        ensure!(!indices.is_empty(), "a named tube has a fine model entry");
        let mut unique = BTreeSet::new();
        for value in indices {
            let index = value.as_u64().and_then(|x| usize::try_from(x).ok())
                .context("a tube entry index is nonnegative")?;
            ensure!(unique.insert(index), "a tube repeats an entry");
            ensure!(owners.insert(index, group).is_none(), "two tube groups share an entry");
        }
        final_indices.push(*unique.last().unwrap());
    }
    let mut pending: Vec<Vec<Mesh>> = (0..groups.len()).map(|_| Vec::new()).collect();
    let mut answers: Vec<Option<Value>> = (0..groups.len()).map(|_| None).collect();
    let count = import::visit_model(numbers.text("model")?, |index, body| {
        if let Some(&group) = owners.get(&index) {
            pending[group].push(Mesh::from_arrays(body.name,
                body.solid.verts().iter().map(|p| p.to_array()).collect(),
                body.solid.tris().to_vec())?);
            if index == final_indices[group] {
                answers[group] = Some(read_group(&groups[group], &pending[group])?);
                pending[group].clear();
            }
        }
        Ok(())
    })?;
    ensure!(owners.keys().all(|&index| index < count), "a tube entry is outside the fine model");
    let answers = answers.into_iter().collect::<Option<Vec<_>>>()
        .context("every named tube was read")?;
    println!("{}", json!({"files":[],"groups":answers}));
    Ok(())
}
