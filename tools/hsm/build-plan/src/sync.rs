//! Explicit output carrying preserves authored text and the publisher's model cohort.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::{bookkeeping_common::labels, bookkeeping_sync::{self, CarryRequest}, inventory};
use serde::Deserialize;
use serde_json::Value;
use std::{collections::{BTreeMap, BTreeSet}, fs, io::Write, path::Path, process::{Command, Stdio}};

#[derive(Default, Deserialize)]
struct ProducerOutputs {
    #[serde(default)] writes: BTreeSet<String>,
    #[serde(default)] rewritten: BTreeSet<String>,
}

#[derive(Default)]
struct DeclaredOutputs { files: BTreeSet<String>, rewritten: BTreeSet<String> }

fn config(root: &Path) -> Result<Value> {
    serde_json::from_slice(&fs::read(root.join("tools/hsm/build-plan/inventory.json"))?).context("read authored inventory groups")
}

fn declared(graph: BTreeMap<String, ProducerOutputs>, config: &Value) -> DeclaredOutputs {
    let mut result = DeclaredOutputs::default();
    for producer in graph.into_values() { result.files.extend(producer.writes); result.rewritten.extend(producer.rewritten); }
    result.files.extend(config["implicit_solids"].as_object().into_iter().flatten().flat_map(|(_, paths)| paths.as_array().into_iter().flatten()).filter_map(Value::as_str).map(str::to_owned));
    result
}

fn declared_outputs(root: &Path, config: &Value) -> Result<DeclaredOutputs> {
    let graph = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
    Ok(declared(graph, config))
}

// Only declared producer exports cross from Bazel into the checkout.
fn retain_declared(pairs: &mut BTreeMap<std::path::PathBuf, String>, declared: &DeclaredOutputs) -> usize {
    let count = pairs.len(); pairs.retain(|_, path| declared.files.contains(path)); count - pairs.len()
}

fn change(root: &Path, command: &[&str], paths: &[Vec<u8>]) -> Result<()> {
    if paths.is_empty() { return Ok(()); }
    let mut child = Command::new("git").arg("-C").arg(root).arg("--literal-pathspecs").args(command)
        .args(["--pathspec-from-file=-", "--pathspec-file-nul"]).stdin(Stdio::piped()).spawn()?;
    let mut input = child.stdin.take().context("git pathspec input")?;
    for path in paths { input.write_all(path)?; input.write_all(&[0])?; }
    drop(input); ensure!(child.wait()?.success(), "git {} failed", command.join(" ")); Ok(())
}

fn stage(root: &Path, config: &Value) -> Result<i32> {
    let status = Command::new("git").arg("-C").arg(root).args(["-c", "status.renames=false", "status", "--porcelain=v1", "-z", "--untracked-files=all"]).output()?;
    ensure!(status.status.success(), "git status: {}", String::from_utf8_lossy(&status.stderr));
    let selected = bookkeeping_sync::stage_selection(&status.stdout, config);
    change(root, &["restore", "--staged"], &selected.staged)?;
    change(root, &["add", "-A"], &selected.paths)?;
    change(root, &["restore", "--worktree", "--source=HEAD"], &selected.tracked)?;
    println!("{} derived path(s) staged; {} publisher-owned path(s) left out", selected.paths.len(), selected.held.len());
    Ok(0)
}

/// Compare or carry only the requested built producers, after an explicit freshness question.
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let (mut write, mut runtime_only, mut derived_only, mut do_stage) = (false, false, false, false);
    let (mut failed, mut targets) = (String::new(), String::new()); let mut at = 0;
    while at < args.len() {
        match args[at].as_str() {
            "--write" => write = true,
            "--solids-only" | "--runtime-only" => runtime_only = true,
            "--derived-only" => derived_only = true,
            "--stage" => do_stage = true,
            option @ ("--failed" | "--targets") => {
                at += 1; let value = args.get(at).with_context(|| format!("{option} requires target labels"))?;
                if option == "--failed" { failed = value.clone(); } else { targets = value.clone(); }
            }
            "--help" | "-h" => { println!("Carry completed Bazel outputs into the checkout.\n\nUsage: hsm-build-plan sync-tree [--write] [--targets LABELS] [--failed LABELS] [--solids-only | --derived-only]\nUse --derived-only --stage to stage derived changes while retaining the committed model cohort."); return Ok(0); }
            option => bail!("unknown sync option {option}"),
        }
        at += 1;
    }
    ensure!(!(runtime_only && derived_only), "choose solids-only or derived-only");
    let config = config(root)?;
    if do_stage {
        ensure!(derived_only && !write && failed.is_empty() && targets.is_empty(), "--stage is used only with --derived-only");
        return stage(root, &config);
    }
    let failed = failed.split(',').map(str::trim).filter(|value| !value.is_empty()).map(|value| value.trim_start_matches('/').trim_start_matches(':').to_owned()).collect::<BTreeSet<_>>();
    let labels = labels(&targets);
    let lease = hsm_run_slots::acquire("build-plan:sync", hsm_run_slots::inherited()?, false)?;
    if write {
        let mut flags = vec!["build".to_owned(), "--check_up_to_date".into()];
        flags.extend(if labels.is_empty() { vec!["//:everything".into()] } else { labels.clone() });
        let current = crate::trace::wrapped(root, Path::new("bazel"), &flags, &lease)?.output()?;
        let freshness = bookkeeping_sync::freshness(&failed, current.status.code().unwrap_or(1), &String::from_utf8_lossy(&current.stderr))?;
        print!("{}", freshness.output); if freshness.refused { return Ok(1); }
    }
    let query = if labels.is_empty() { "deps(//:everything)".to_owned() } else { format!("set({})", labels.join(" ")) };
    let built = crate::trace::wrapped(root, Path::new("bazel"), &["cquery".into(), query, "--output=files".into()], &lease)?.output()?;
    ensure!(built.status.success(), "the build graph does not load: {}", String::from_utf8_lossy(&built.stderr));
    let intermediate = config["action_intermediate"].as_array().into_iter().flatten().filter_map(Value::as_str).map(str::to_owned).collect();
    let mut selected = bookkeeping_sync::targets(root, &String::from_utf8_lossy(&built.stdout), &intermediate)?;
    print!("{}", selected.output);
    let declared = declared_outputs(root, &config)?;
    let held = retain_declared(&mut selected.pairs, &declared);
    if held != 0 { println!("  {held} compiler or support output(s) remain in Bazel"); }
    let mut request = CarryRequest { root: root.to_owned(), pairs: selected.pairs, write, runtime_only, derived_only,
        config, ..CarryRequest::default() };
    request.pairs.retain(|_, path| !inventory::inert(path, &request.config));
    request.rewritten = declared.rewritten; request.failed = failed;
    let result = bookkeeping_sync::carry_request(&request)?;
    print!("{}", result.output); Ok(result.status.unwrap_or(0))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn compiler_outputs_stay_in_bazel_while_new_and_implicit_exports_carry() {
        let graph = serde_json::from_value(json!({"hardware/new/part.rs": {
            "writes":["hardware/new/part.step", "hardware/new/guide.md"],
            "rewritten":["hardware/new/guide.md"]
        }})).unwrap();
        let declaration = declared(graph, &json!({"implicit_solids":{"hardware/new/part.rs":["hardware/new/part.stl"]}}));
        let mut pairs = BTreeMap::from([
            ("/bazel/bin/out/part-program/part".into(), "part".to_owned()),
            ("/bazel/bin/out/part/hardware/new/part.step".into(), "hardware/new/part.step".to_owned()),
            ("/bazel/bin/out/part/hardware/new/part.stl".into(), "hardware/new/part.stl".to_owned()),
            ("/bazel/bin/out/part/hardware/new/guide.md".into(), "hardware/new/guide.md".to_owned()),
            ("/bazel/bin/out/build-plan-support-program/hsm-build-plan".into(), "hsm-build-plan".to_owned()),
        ]);
        assert_eq!(retain_declared(&mut pairs, &declaration), 2);
        assert_eq!(pairs.into_values().collect::<BTreeSet<_>>(), ["hardware/new/part.step", "hardware/new/part.stl", "hardware/new/guide.md"].map(str::to_owned).into());
        assert_eq!(declaration.rewritten, ["hardware/new/guide.md".to_owned()].into());
    }
}
