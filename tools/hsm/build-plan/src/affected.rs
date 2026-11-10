//! Native changed-source selection follows declared producer edges and preserves publication's dirty-source boundary.
use crate::planning::{self, GRAPH_PATH, Plan};
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::bookkeeping_affected as scope;
use serde::Serialize;
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::Path,
    process::{Command, Output},
};

#[derive(Debug, Default)]
pub struct Options {
    pub why: bool,
    pub base: Option<String>,
    pub head: String,
    pub artifacts: bool,
    pub all_artifacts: bool,
    pub dirty_sources: bool,
    pub explicit_paths: Option<BTreeSet<String>>,
    pub exclude: BTreeSet<String>,
}

#[derive(Debug, Default, Serialize)]
pub struct Selection {
    pub targets: BTreeSet<String>,
    pub paths: BTreeSet<String>,
    pub known: BTreeSet<String>,
    pub risky: Vec<String>,
    pub reach: BTreeMap<String, BTreeSet<String>>,
}

fn git(root: &Path, args: &[&str]) -> Result<Output> {
    let output = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(args)
        .output()?;
    ensure!(
        output.status.success(),
        "git {}: {}",
        args.join(" "),
        String::from_utf8_lossy(&output.stderr)
    );
    Ok(output)
}
fn git_file(root: &Path, reference: &str, path: &str) -> Option<String> {
    let value = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["show", &format!("{reference}:{path}")])
        .output()
        .ok()?;
    value
        .status
        .success()
        .then(|| String::from_utf8(value.stdout).ok())
        .flatten()
}
fn nul_paths(bytes: &[u8]) -> Result<BTreeSet<String>> {
    Ok(std::str::from_utf8(bytes)?
        .split('\0')
        .filter(|path| !path.is_empty())
        .map(str::to_owned)
        .collect())
}
fn named_changes(bytes: &[u8]) -> Result<BTreeSet<String>> {
    let fields = std::str::from_utf8(bytes)?.split('\0').collect::<Vec<_>>();
    let mut paths = BTreeSet::new();
    let mut at = 0;
    while at < fields.len() && !fields[at].is_empty() {
        let status = fields[at];
        at += 1;
        let count = if status.starts_with(['R', 'C']) { 2 } else { 1 };
        ensure!(
            at + count <= fields.len(),
            "truncated Git name-status record"
        );
        paths.extend(
            fields[at..at + count]
                .iter()
                .filter(|path| !path.is_empty() && !path.ends_with('/'))
                .map(|path| (*path).to_owned()),
        );
        at += count;
    }
    Ok(paths)
}

/// Working-tree source changes follow Git's tracked and authored untracked paths.
pub fn changed(root: &Path, base: Option<&str>, head: &str) -> Result<BTreeSet<String>> {
    if let Some(base) = base {
        return named_changes(
            &git(
                root,
                &["diff", "--name-status", "--find-renames", "-z", base, head],
            )?
            .stdout,
        );
    }
    let mut paths =
        nul_paths(&git(root, &["diff", "--name-only", "--no-renames", "-z", "HEAD"])?.stdout)?;
    paths.extend(nul_paths(
        &git(root, &["ls-files", "--others", "--exclude-standard", "-z"])?.stdout,
    )?);
    Ok(paths)
}

fn metadata_scope(
    root: &Path,
    options: &Options,
    paths: &BTreeSet<String>,
    config: &Value,
) -> BTreeSet<String> {
    if !options.artifacts || !paths.contains(GRAPH_PATH) {
        return BTreeSet::new();
    }
    let (before, after) = if let Some(base) = &options.base {
        (
            git_file(root, base, GRAPH_PATH),
            git_file(root, &options.head, GRAPH_PATH),
        )
    } else {
        (
            git_file(root, "HEAD", GRAPH_PATH),
            fs::read_to_string(root.join(GRAPH_PATH)).ok(),
        )
    };
    match (
        before.as_deref().and_then(scope::normalized),
        after.as_deref().and_then(scope::normalized),
    ) {
        (Some(a), Some(b)) if scope::projection(&a, config) == scope::projection(&b, config) => {
            BTreeSet::from([GRAPH_PATH.to_owned()])
        }
        _ => BTreeSet::new(),
    }
}

fn labels(targets: BTreeSet<String>) -> BTreeSet<String> {
    targets
        .into_iter()
        .map(|name| format!("//:{name}"))
        .collect()
}
fn reach(paths: &BTreeSet<String>, plan: &Plan) -> (BTreeSet<String>, BTreeSet<String>) {
    let (targets, known) = plan.affected(paths);
    (labels(targets), known)
}
fn sentinels(paths: &BTreeSet<String>, artifacts: &BTreeSet<String>) -> BTreeSet<String> {
    if !paths.iter().any(|path| {
        path == "tools/hsm/build-plan/src/sync.rs" || path.starts_with("tools/hsm/publication/")
    }) {
        return BTreeSet::new();
    }
    [
        "//:cold-core-assembly",
        "//:installed-machine",
        "//:enclosure",
    ]
    .into_iter()
    .filter(|target| artifacts.contains(*target))
    .map(str::to_owned)
    .collect()
}

/// Selection resolves source changes from the native plan without invoking a build command.
pub fn select(root: &Path, options: &Options) -> Result<Selection> {
    let plan = planning::action_plan(root, None)?;
    let inventory = serde_json::to_value(&plan.inventory)?;
    let config = planning::inventory_config(root)?;
    let classification =
        scope::Classification::new(config.clone(), planning::graph(root)?, &inventory);
    let artifacts = labels(plan.artifact_targets());
    if options.all_artifacts {
        return Ok(Selection {
            targets: artifacts,
            ..Selection::default()
        });
    }
    let head = if options.head.is_empty() {
        "HEAD"
    } else {
        &options.head
    };
    let mut paths = match &options.explicit_paths {
        Some(paths) => paths.clone(),
        None => changed(root, options.base.as_deref(), head)?,
    };
    paths.retain(|path| !options.exclude.contains(path));
    if options.dirty_sources {
        paths.remove("hardware/cad-artifacts.json");
    }
    paths = classification.filter_moved(&paths, false);
    if options.dirty_sources {
        paths.retain(|path| {
            !classification.presentation(path)
                && !(path.ends_with(".scorecard.json") && classification.declared.contains(path))
        });
        let (found, known) = reach(&paths, &plan);
        let mut targets = found
            .intersection(&artifacts)
            .cloned()
            .collect::<BTreeSet<_>>();
        targets.extend(sentinels(&paths, &artifacts));
        return Ok(Selection {
            targets,
            paths,
            known,
            ..Selection::default()
        });
    }
    let safe = metadata_scope(root, options, &paths, &config);
    paths = classification.filter_moved(&paths, options.artifacts);
    if paths.is_empty() {
        return Ok(Selection::default());
    }
    let (mut targets, known) = reach(&paths, &plan);
    let risky = classification.risky(&paths, &known, &safe, options.artifacts);
    if !risky.is_empty() {
        targets = if options.artifacts {
            artifacts.clone()
        } else {
            BTreeSet::from(["//:everything".into()])
        };
    } else if options.artifacts {
        targets = targets.intersection(&artifacts).cloned().collect();
    }
    let mut details = BTreeMap::new();
    if options.why {
        for path in &known {
            details.insert(
                path.clone(),
                reach(&BTreeSet::from([path.clone()]), &plan).0,
            );
        }
    }
    Ok(Selection {
        targets,
        paths,
        known,
        risky,
        reach: details,
    })
}

pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut options = Options {
        head: "HEAD".to_owned(),
        ..Options::default()
    };
    let mut json_output = false;
    let mut at = 0;
    while at < args.len() {
        match args[at].as_str() {
            "--why" => options.why = true,
            "--artifacts" => options.artifacts = true,
            "--all-artifacts" => options.all_artifacts = true,
            "--dirty-sources" => {
                options.dirty_sources = true;
                options.artifacts = true;
            }
            "--json" => json_output = true,
            "--base" | "--head" | "--path" | "--exclude" => {
                let flag = &args[at];
                at += 1;
                let value = args
                    .get(at)
                    .with_context(|| format!("{flag} requires a value"))?;
                match flag.as_str() {
                    "--base" => options.base = Some(value.clone()),
                    "--head" => options.head = value.clone(),
                    "--path" => {
                        options
                            .explicit_paths
                            .get_or_insert_with(BTreeSet::new)
                            .insert(value.clone());
                    }
                    "--exclude" => {
                        options.exclude.insert(value.clone());
                    }
                    _ => unreachable!(),
                }
            }
            "--help" | "-h" => {
                println!(
                    "Select native producer targets reached by changed sources.\n\nUsage: hsm-build-plan affected [--artifacts] [--base REF --head REF] [--why] [--json] [--path PATH ...]\n       hsm-build-plan affected --dirty-sources --json [--exclude PATH ...]"
                );
                return Ok(0);
            }
            argument => bail!("unknown affected argument {argument}"),
        }
        at += 1;
    }
    let selection = select(root, &options)?;
    if json_output {
        println!("{}", serde_json::to_string(&selection)?);
        return Ok(0);
    }
    if selection.paths.is_empty() && !options.all_artifacts {
        eprintln!("nothing has moved — the selected source set holds nothing to build");
    }
    if !selection.risky.is_empty() {
        eprintln!(
            "{} changed paths cannot be scoped; the selected build widens:",
            selection.risky.len()
        );
        for path in &selection.risky {
            eprintln!("    {path}");
        }
    }
    for target in &selection.targets {
        println!("{target}");
        if options.why {
            for (path, targets) in &selection.reach {
                if targets.contains(target) {
                    println!("    {path}");
                }
            }
        }
    }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn rename_reading_keeps_both_source_paths() {
        assert_eq!(
            named_changes(b"R100\0old name.rs\0new name.rs\0M\0hardware/layout.json\0").unwrap(),
            ["old name.rs", "new name.rs", "hardware/layout.json"]
                .map(str::to_owned)
                .into()
        );
    }
    #[test]
    fn presentation_changes_leave_native_artifact_projection_intact() {
        let native = |name: &str, sources: Value| json!({"reads":sources,"writes":[format!("hardware/{name}.stl")],"rewritten":[],"program":{"crate":name,"name":name,"sources":[format!("{name}.rs")]}});
        let mut graph = json!({"part.rs":native("part",json!(["part.rs"])),"docs.rs":{"reads":["guide.md"],"writes":["guide.pdf"],"rewritten":[],"program":{"crate":"docs","name":"docs","sources":["docs.rs"]}}});
        let before = scope::normalized(&graph.to_string()).unwrap();
        graph["docs.rs"]["reads"] = json!(["new-guide.md"]);
        let after = scope::normalized(&graph.to_string()).unwrap();
        assert_eq!(
            scope::projection(&before, &json!({})),
            scope::projection(&after, &json!({}))
        );
        graph["part.rs"]["program"]["runtime_inputs"] = json!(["part.rs"]);
        assert_ne!(
            scope::projection(&before, &json!({})),
            scope::projection(&scope::normalized(&graph.to_string()).unwrap(), &json!({}))
        );
    }
}
