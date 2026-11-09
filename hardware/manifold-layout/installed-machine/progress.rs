//! Source-authored placement checkpoints update shared scene references while dependent geometry continues.
use crate::cache::Cache;
use anyhow::{Context, Result, ensure};
use hsm_geometry::scene;
use serde_json::{Value, json};
use std::collections::BTreeMap;
use std::io::Write;
use std::path::{Path, PathBuf};

type Frame = [[f64; 4]; 3];
const ID: Frame = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.]];

fn frame(value: &Value) -> Result<Frame> {
    if value.is_null() {
        return Ok(ID);
    }
    let mut result = ID;
    for r in 0..3 {
        for c in 0..4 {
            result[r][c] = value[r][c]
                .as_f64()
                .context("placement matrix coordinate")?;
        }
    }
    Ok(result)
}

fn multiply(a: Frame, b: Frame) -> Frame {
    std::array::from_fn(|r| {
        std::array::from_fn(|c| {
            (0..3).map(|k| a[r][k] * b[k][c]).sum::<f64>() + if c == 3 { a[r][3] } else { 0. }
        })
    })
}

fn inverse(a: Frame) -> Result<Frame> {
    let d = a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]);
    ensure!(d.abs() > 1e-15, "singular authored placement");
    let mut out = ID;
    for r in 0..3 {
        for c in 0..3 {
            let (r1, r2, c1, c2) = ((c + 1) % 3, (c + 2) % 3, (r + 1) % 3, (r + 2) % 3);
            out[r][c] = (a[r1][c1] * a[r2][c2] - a[r1][c2] * a[r2][c1]) / d;
        }
    }
    for r in 0..3 {
        out[r][3] = -(0..3).map(|c| out[r][c] * a[c][3]).sum::<f64>();
    }
    Ok(out)
}

fn construction(item: &Value) -> Value {
    let mut item = item.as_object().cloned().unwrap_or_default();
    for field in ["name", "transform", "color", "point"] {
        item.remove(field);
    }
    Value::Object(item)
}

/// Retain only placement recipes whose unchanged local geometry can be reused exactly.
pub fn state(cache: &mut Cache, equipment: &Value, junctions: &[Value]) -> Result<Value> {
    let mut inputs = serde_json::Map::new();
    for relative in [
        "hardware/manifold-layout/above-core.json",
        "hardware/manifold-layout/junctions.json",
        "hardware/manifold-layout/enclosure-box.json",
    ] {
        inputs.insert(
            relative.to_owned(),
            json!(cache.input_digest(Path::new(relative))?),
        );
    }
    let mut items = Vec::new();
    let core: Vec<&str> = equipment["core_equipment"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .collect();
    for item in equipment["items"].as_array().into_iter().flatten() {
        if !matches!(item["op"].as_str(), Some("reference" | "mount-hardware")) {
            continue;
        }
        let mut item = item.clone();
        if let Some(source) = item["source"].as_str() {
            item["source_sha256"] = json!(cache.input_digest(Path::new(source))?);
        }
        if core.contains(&item["name"].as_str().unwrap_or("")) {
            item["name"] = json!(format!("cold-core/{}", item["name"].as_str().unwrap()));
        }
        items.push(item);
    }
    for junction in junctions {
        let mut item = junction.clone();
        item["op"] = json!("reference");
        let model = item["model"]
            .as_str()
            .context("junction reference")?
            .to_owned();
        item["source_sha256"] = json!(cache.input_digest(Path::new(&model))?);
        if item["owner"] == "cold-core" {
            item["name"] = json!(format!("cold-core/{}", item["name"].as_str().unwrap()));
        }
        items.push(item);
    }
    Ok(json!({"implementation":cache.implementation(),"items":items,"inputs":inputs}))
}

fn read(path: &Path) -> Result<Value> {
    scene::pack(&std::fs::read(path).with_context(|| format!("reading scene {}", path.display()))?)
}

fn wiring(name: &str) -> bool {
    ["wire-", "wiring-", "terminal-"]
        .iter()
        .any(|prefix| name.starts_with(prefix))
}

fn replace_source(head: &mut Value, source: &str, bytes: &[u8]) -> Result<usize> {
    if !head["source_inventory"][source].is_array() {
        let incoming = scene::digest(bytes);
        let nodes = head["meshes"].as_array().context("scene nodes")?;
        let bound = nodes.iter().any(|node| node["source"] == source);
        let historical = nodes
            .iter()
            .filter(|node| node["source"] == source)
            .filter_map(|node| node["source_sha256"].as_str())
            .find(|hash| *hash != incoming)
            .or_else(|| {
                head["sources"][source]
                    .as_str()
                    .filter(|hash| *hash != incoming)
            });
        if let Some(hash) = historical.filter(|_| bound) {
            let path = scene::asset_path(hash)?;
            let retained = std::fs::read(&path).with_context(|| {
                format!("previous source inventory for {source} is not retained")
            })?;
            ensure!(
                scene::digest(&retained) == hash,
                "previous source inventory for {source} differs from its digest"
            );
        }
    }
    scene::replace(head, source, bytes)
}

fn prepare_placements(
    cache: &mut Cache,
    root: &Path,
    state: &Value,
    previous_scene: &Path,
) -> Result<Option<Value>> {
    let Some(previous) = cache.previous("presentation-state") else {
        return Ok(None);
    };
    if previous["implementation"] != state["implementation"] || !previous_scene.is_file() {
        return Ok(None);
    }
    let mut head = read(previous_scene)?;
    let mut changed = Vec::new();
    let imports: Vec<_> = head["sources"]
        .as_object()
        .into_iter()
        .flatten()
        .map(|(source, hash)| (source.clone(), hash.clone()))
        .collect();
    for (source, expected) in imports {
        let path = root.join(&source);
        if !path.is_file() {
            continue;
        }
        let hash = cache.input_digest(&path)?;
        if expected == hash {
            continue;
        }
        let bytes = std::fs::read(&path)?;
        if replace_source(&mut head, &source, &bytes)? > 0 {
            changed.push(source);
        }
    }
    let prior: BTreeMap<_, _> = previous["items"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|item| item["name"].as_str().map(|name| (name, item)))
        .collect();
    let nodes = head["meshes"].as_array_mut().context("scene nodes")?;
    for item in state["items"].as_array().into_iter().flatten() {
        let name = item["name"].as_str().context("placement name")?;
        let Some(old) = prior.get(name) else { continue };
        if construction(item) != construction(old) {
            continue;
        }
        let mut from = frame(&old["transform"])?;
        let mut to = frame(&item["transform"])?;
        if item["op"] == "mount-hardware" {
            for axis in 0..3 {
                from[axis][3] = old["point"][axis].as_f64().context("mount point")?;
                to[axis][3] = item["point"][axis].as_f64().context("mount point")?;
            }
        }
        if from == to && old["color"] == item["color"] {
            continue;
        }
        let delta = multiply(to, inverse(from)?);
        for node in nodes.iter_mut().filter(|node| node["name"] == name) {
            node["transform"] = json!(multiply(delta, frame(&node["transform"])?));
            if item["color"].is_array() {
                for entry in node["entries"].as_array_mut().context("scene entries")? {
                    entry["color"] = item["color"].clone();
                }
            }
            changed.push(name.to_owned());
        }
    }
    if changed.is_empty() {
        return Ok(None);
    }
    head["iteration"] = json!({"stage":"placements","complete":false,"changed":changed,"pending":["mechanical geometry","wiring"]});
    Ok(Some(head))
}

/// Place unchanged source geometry when its retained baseline can be reconciled without rebuilding.
pub fn placements(
    cache: &mut Cache,
    root: &Path,
    state: &Value,
    previous_scene: &Path,
    out: &Path,
) -> Result<bool> {
    let head = match prepare_placements(cache, root, state, previous_scene) {
        Ok(Some(head)) => head,
        Ok(None) => return Ok(false),
        Err(error) => {
            let _ = writeln!(
                std::io::stderr(),
                "[installed-machine] placement preview unavailable: {error:#}"
            );
            return Ok(false);
        }
    };
    write(out, head)?;
    emit(out, "placements")?;
    Ok(true)
}

/// Completed mechanics replace the prior mechanics while the preceding wiring remains visible.
pub fn mechanics(mechanical: &Path, previous_scene: &Path, out: &Path) -> Result<()> {
    let mut head = read(mechanical)?;
    if previous_scene.is_file() {
        let prior = read(previous_scene)?;
        let nodes = head["meshes"].as_array_mut().context("mechanical nodes")?;
        nodes.extend(
            prior["meshes"]
                .as_array()
                .into_iter()
                .flatten()
                .filter(|node| wiring(node["name"].as_str().unwrap_or("")))
                .cloned(),
        );
    }
    head["iteration"] = json!({"stage":"mechanics","complete":false,"pending":["wiring"]});
    write(out, head)?;
    emit(out, "mechanics")
}

/// Installed wiring replaces only wiring nodes in the completed mechanical scene.
pub fn complete(mechanical: &Path, wires: &Path, out: &Path) -> Result<()> {
    let mut head = read(mechanical)?;
    let wires = read(wires)?;
    let nodes = head["meshes"].as_array_mut().context("mechanical nodes")?;
    nodes.retain(|node| !wiring(node["name"].as_str().unwrap_or("")));
    nodes.extend(
        wires["meshes"]
            .as_array()
            .context("wiring nodes")?
            .iter()
            .cloned(),
    );
    head["iteration"] = json!({"stage":"installed","complete":true});
    write(out, head)?;
    emit(out, "installed")
}

fn write(path: &Path, mut head: Value) -> Result<()> {
    head["src"] = json!(scene::digest(&serde_json::to_vec(&head["meshes"])?));
    head["source_kind"] = json!("scene");
    head["step_export"] = json!(false);
    scene::persist(path, &head)
}

/// Notification failures leave the successfully written producer outputs available to the normal build.
fn emit(path: &Path, stage: &str) -> Result<()> {
    if let Err(error) = notify(path, stage) {
        let _ = writeln!(
            std::io::stderr(),
            "[installed-machine] progress notification unavailable: {error:#}"
        );
    }
    Ok(())
}

/// A checkpoint names atomic output files to the normal print build's progressive publisher.
fn notify(path: &Path, stage: &str) -> Result<()> {
    let log = std::env::var_os("HSM_BUILD_PROGRESS")
        .map(PathBuf::from)
        .or_else(|| {
            std::env::var_os("HSM_WORKSPACE")
                .map(|root| PathBuf::from(root).join(".cache/realized/print-build-progress.jsonl"))
        });
    let Some(log) = log else { return Ok(()) };
    if let Some(parent) = log.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let event = json!({"producer":"hardware/manifold-layout/installed_machine.rs","stage":stage,"files":[std::path::absolute(path)?]});
    let mut line = serde_json::to_vec(&event)?;
    line.push(b'\n');
    std::fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(log)?
        .write_all(&line)?;
    Ok(())
}

/// Retain the last published scene and authored placements without retaining another geometry tree.
pub fn remember(
    cache: &mut Cache,
    mut state: Value,
    scene: &Path,
    previous_scene: &Path,
) -> Result<()> {
    let bytes = std::fs::read(scene)?;
    state["scene_sha256"] = json!(hsm_model_export::digest(&bytes));
    let mut head = hsm_geometry::scene::pack(&bytes)?;
    let imports: Vec<_> = head["sources"]
        .as_object()
        .into_iter()
        .flatten()
        .filter(|(source, _)| !head["source_inventory"][source.as_str()].is_array())
        .map(|(source, hash)| (source.clone(), hash.clone()))
        .collect();
    for (source, expected) in imports {
        let update = (|| -> Result<()> {
            let path = Path::new(&source);
            if !path.is_file() {
                return Ok(());
            }
            if cache.input_digest(path)?.as_str() != expected.as_str().unwrap_or("") {
                return Ok(());
            }
            let incoming = std::fs::read(path)?;
            if scene::digest(&incoming) != expected.as_str().unwrap_or("") {
                return Ok(());
            }
            if head["meshes"].as_array().into_iter().flatten().any(|node| {
                node["source"] == source
                    && !node["source_sha256"].is_null()
                    && node["source_sha256"] != expected
            }) {
                return Ok(());
            }
            replace_source(&mut head, &source, &incoming)?;
            Ok(())
        })();
        if let Err(error) = update {
            let _ = writeln!(
                std::io::stderr(),
                "[installed-machine] retained source inventory unavailable: {error:#}"
            );
        }
    }
    let bytes = hsm_geometry::scene::encode(&head, &[])?;
    state["retained_scene_sha256"] = json!(hsm_model_export::digest(&bytes));
    let value = state.clone();
    cache.run(
        "presentation-state",
        &state,
        &[previous_scene.to_owned()],
        || {
            hsm_model_export::put(previous_scene, &bytes)?;
            Ok(value)
        },
    )?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn missing_source_inventory_skips_preview_and_current_baseline_retains_inventory() -> Result<()>
    {
        struct Restore(Option<std::ffi::OsString>);
        impl Drop for Restore {
            fn drop(&mut self) {
                unsafe {
                    match &self.0 {
                        Some(value) => std::env::set_var("HSM_READS", value),
                        None => std::env::remove_var("HSM_READS"),
                    }
                }
            }
        }
        let base = std::env::temp_dir().join(format!(
            "hsm-preview-inventory-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_nanos()
        ));
        std::fs::create_dir_all(&base)?;
        let _restore = Restore(std::env::var_os("HSM_READS"));
        let log = base.join("reads.log");
        std::fs::write(&log, "hsm-reads 1\n")?;
        unsafe {
            std::env::set_var("HSM_READS", &log);
        }
        let mut cache = Cache::new(&base, &base.join("work"))?;
        let state = json!({"implementation":cache.implementation(),"items":[]});
        cache.run("presentation-state", &state, &[], || Ok(state.clone()))?;
        let source = base.join("part.step.mesh");
        scene::persist(
            &source,
            &json!({"v":4,"meshes":[{"name":"part","asset":"a".repeat(64),"bytes":0,
            "entries":[{"name":"part","color":[0.1,0.2,0.3]}]}]}),
        )?;
        let incoming = std::fs::read(&source)?;
        let hash = scene::digest(&incoming);
        let source = source.to_string_lossy().into_owned();
        let historical = scene::digest(
            base.join("unavailable historical source")
                .to_string_lossy()
                .as_bytes(),
        );
        let previous = base.join("previous.step.mesh");
        let old = json!({"v":4,"sources":{(source.clone()):historical.clone()},"meshes":[{
            "name":"part","source":source,"source_sha256":historical,"asset":"b".repeat(64),"bytes":0,
            "entries":[{"name":"part","color":[0.1,0.2,0.3]}]}]});
        write(&previous, old.clone())?;
        let output = base.join("output.step.mesh");
        write(&output, old)?;
        let before = std::fs::read(&output)?;
        assert!(!placements(&mut cache, &base, &state, &previous, &output)?);
        assert_eq!(std::fs::read(&output)?, before);

        let current = json!({"v":4,"sources":{(source.clone()):hash.clone()},"meshes":[{
            "name":"part","source":source,"source_sha256":hash,"asset":"a".repeat(64),"bytes":0,
            "entries":[{"name":"part","color":[0.1,0.2,0.3]}]}]});
        write(&output, current)?;
        remember(&mut cache, state, &output, &previous)?;
        let retained = read(&previous)?;
        assert!(retained["source_inventory"][&source].is_array());
        drop(cache);
        std::fs::remove_dir_all(base)?;
        Ok(())
    }

    #[test]
    fn relative_placements_preserve_mirrored_multisolid_frames() -> Result<()> {
        let before = [[-1., 0., 0., 12.], [0., 0., -1., 23.], [0., 1., 0., 34.]];
        let after = [[0., 1., 0., 45.], [1., 0., 0., 56.], [0., 0., 1., 67.]];
        let delta = multiply(after, inverse(before)?);
        let local = [[1., 0., 0., 3.], [0., 1., 0., 4.], [0., 0., 1., 5.]];
        let moved = multiply(delta, multiply(before, local));
        let expected = multiply(after, local);
        for r in 0..3 {
            for c in 0..4 {
                assert!((moved[r][c] - expected[r][c]).abs() < 1e-12);
            }
        }
        Ok(())
    }

    #[test]
    fn unavailable_journal_keeps_output_and_output_errors_remain_errors() -> Result<()> {
        struct Restore(Option<std::ffi::OsString>);
        impl Drop for Restore {
            fn drop(&mut self) {
                unsafe {
                    match &self.0 {
                        Some(value) => std::env::set_var("HSM_BUILD_PROGRESS", value),
                        None => std::env::remove_var("HSM_BUILD_PROGRESS"),
                    }
                }
            }
        }
        let base = std::env::temp_dir().join(format!(
            "hsm-progress-journal-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_nanos()
        ));
        std::fs::create_dir_all(&base)?;
        let blocked = base.join("regular-file");
        std::fs::write(&blocked, "occupied")?;
        let _restore = Restore(std::env::var_os("HSM_BUILD_PROGRESS"));
        unsafe {
            std::env::set_var("HSM_BUILD_PROGRESS", blocked.join("progress.jsonl"));
        }
        let output = base.join("output.step.mesh");
        write(&output, json!({"v":4,"meshes":[]}))?;
        let before = std::fs::read(&output)?;
        emit(&output, "mechanics")?;
        assert_eq!(std::fs::read(&output)?, before);
        assert!(
            write(
                &blocked.join("output.step.mesh"),
                json!({"v":4,"meshes":[]})
            )
            .is_err()
        );
        std::fs::remove_dir_all(base)?;
        Ok(())
    }
}
