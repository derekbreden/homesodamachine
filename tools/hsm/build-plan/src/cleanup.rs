//! Requested build-log and derived-change readings preserve authored work while exposing generated state.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::bookkeeping_sync;
use serde::Deserialize;
use std::{collections::{BTreeMap, BTreeSet}, fs, io::{BufRead, BufReader}, path::Path, process::Command};

#[derive(Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct EventIdentity {
    #[serde(default)] target_completed: Option<Label>,
    #[serde(default)] action_completed: Option<Label>,
}
#[derive(Deserialize)]
struct Label { #[serde(default)] label: String }
#[derive(Default, Deserialize)]
struct Completion { #[serde(default)] success: bool }
#[derive(Default, Deserialize)]
struct Event {
    #[serde(default)] id: EventIdentity,
    #[serde(default)] completed: Completion,
    #[serde(default)] action: Completion,
}

pub fn failed(lines: impl IntoIterator<Item = String>) -> BTreeSet<String> {
    let mut labels = BTreeSet::new();
    for line in lines {
        let Ok(event) = serde_json::from_str::<Event>(&line) else { continue };
        if let Some(label) = event.id.target_completed.filter(|_| !event.completed.success).filter(|label| !label.label.is_empty()) { labels.insert(label.label); }
        if let Some(label) = event.id.action_completed.filter(|_| !event.action.success).filter(|label| !label.label.is_empty()) { labels.insert(label.label); }
    }
    labels
}

pub fn failed_cli(root: &Path, args: &[String]) -> Result<i32> {
    if args.first().is_some_and(|arg| ["--help", "-h"].contains(&arg.as_str())) {
        println!("Read failed requested targets and producer actions from a Bazel event log.\n\nUsage: hsm-build-plan failed-targets FILE"); return Ok(0);
    }
    ensure!(args.len() == 1, "failed-targets requires one build-event file");
    let path = root.join(args.first().context("failed-targets requires a build-event file")?);
    if !path.is_file() { return Ok(0); }
    let lines = BufReader::new(fs::File::open(path)?).lines().collect::<std::io::Result<Vec<_>>>()?;
    println!("{}", failed(lines).into_iter().collect::<Vec<_>>().join(",")); Ok(0)
}

#[derive(Default, Deserialize)]
struct Derived {
    #[serde(default)] writes: BTreeSet<String>,
    #[serde(default)] rewritten: BTreeSet<String>,
}

pub fn drop_cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut write = false;
    for argument in args {
        match argument.as_str() {
            "--write" => write = true,
            "--help" | "-h" => { println!("Name or restore unstaged generated outputs while retaining authored files.\n\nUsage: hsm-build-plan drop-derived [--write]"); return Ok(0); }
            option => bail!("unknown drop-derived option {option}"),
        }
    }
    let changed = Command::new("git").arg("-C").arg(root).args(["diff", "--name-only", "-z"]).output()?;
    ensure!(changed.status.success(), "git diff: {}", String::from_utf8_lossy(&changed.stderr));
    let dirty = changed.stdout.split(|byte| *byte == 0).filter(|path| !path.is_empty())
        .map(|path| String::from_utf8(path.to_vec()).context("changed path is not UTF-8")).collect::<Result<Vec<_>>>()?;
    if dirty.is_empty() { println!("The worktree carries no unstaged change."); return Ok(0); }
    let graph: BTreeMap<String, Derived> = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
    let made = graph.into_values().flat_map(|entry| entry.writes.into_iter().chain(entry.rewritten)).collect();
    let (drop, keep) = bookkeeping_sync::drop_paths(&dirty, &made);
    if !keep.is_empty() {
        println!("{} authored or unclassified path(s) left alone:", keep.len());
        for path in &keep { println!("  {path}"); }
    }
    if drop.is_empty() { println!("No unstaged path is classified as wholly generated."); return Ok(0); }
    println!("{} generated path(s) {}:", drop.len(), if write { "restored" } else { "would be restored" });
    for path in &drop { println!("  {path}"); }
    if write {
        let result = Command::new("git").arg("-C").arg(root).args(["checkout", "--"]).args(drop).status()?;
        ensure!(result.success(), "git checkout failed");
    } else { println!("Use --write to restore them."); }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn failed_actions_are_retained_beside_failed_requested_umbrellas() {
        let lines = [
            r#"{"id":{"targetCompleted":{"label":"//:everything"}},"completed":{}}"#,
            r#"{"id":{"actionCompleted":{"label":"//:enclosure"}},"action":{"exitCode":1}}"#,
            r#"{"id":{"actionCompleted":{"label":"//:good"}},"action":{"success":true}}"#,
            r#"{"id":{"targetCompleted":{"label":"//:good"}},"completed":{"success":true}}"#,
            "not JSON",
            r#"{"id":{"actionCompleted":{"label":"//:enclosure"}},"action":{}}"#,
        ];
        assert_eq!(failed(lines.map(str::to_owned)), ["//:enclosure", "//:everything"].map(str::to_owned).into());
    }

    #[test]
    fn derived_restore_protects_rust_authored_source_and_trace_graph() {
        let paths = ["hardware/part/part.rs", "hardware/legacy/part.py", "tools/bazel/graph.json", "hardware/derived.md", "notes.txt"].map(str::to_owned);
        let made = paths.iter().cloned().collect();
        let (drop, keep) = bookkeeping_sync::drop_paths(&paths, &made);
        assert_eq!(drop, ["hardware/derived.md", "notes.txt"]);
        assert_eq!(keep, ["hardware/part/part.rs", "hardware/legacy/part.py", "tools/bazel/graph.json"]);
    }
}
