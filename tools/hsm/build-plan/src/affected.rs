//! Native changed-source selection reads the declared producer closure and preserves publication's dirty-source boundary.
use crate::planning::{self, Plan, Rule};
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::{bookkeeping_affected as scope, bookkeeping_common::strings};
use serde::Serialize;
use serde_json::{Value, json};
use std::{collections::{BTreeMap, BTreeSet}, fs, path::{Path, PathBuf}, process::{Command, Output}};

#[derive(Debug, Default)]
pub struct Options {
    pub why: bool,
    pub base: Option<String>,
    pub head: String,
    pub artifacts: bool,
    pub manifest: bool,
    pub all_artifacts: bool,
    pub dirty_sources: bool,
    pub explicit_paths: Option<BTreeSet<String>>,
    pub exclude: BTreeSet<String>,
    pub bazel: Option<PathBuf>,
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
    let output = Command::new("git").arg("-C").arg(root).args(args).output()?;
    ensure!(output.status.success(), "git {}: {}", args.join(" "), String::from_utf8_lossy(&output.stderr));
    Ok(output)
}

fn git_file(root: &Path, reference: &str, path: &str) -> Option<String> {
    let value = Command::new("git").arg("-C").arg(root).args(["show", &format!("{reference}:{path}")]).output().ok()?;
    value.status.success().then(|| String::from_utf8(value.stdout).ok()).flatten()
}

fn git_tree(root: &Path, reference: &str) -> Option<String> {
    let value = Command::new("git").arg("-C").arg(root).args(["rev-parse", &format!("{reference}^{{tree}}")]).output().ok()?;
    value.status.success().then(|| String::from_utf8(value.stdout).ok().map(|text| text.trim().to_owned())).flatten()
}

fn nul_paths(bytes: &[u8]) -> Result<BTreeSet<String>> {
    Ok(std::str::from_utf8(bytes)?.split('\0').filter(|path| !path.is_empty()).map(str::to_owned).collect())
}

fn named_changes(bytes: &[u8]) -> Result<BTreeSet<String>> {
    let fields = std::str::from_utf8(bytes)?.split('\0').collect::<Vec<_>>();
    let mut paths = BTreeSet::new(); let mut at = 0;
    while at < fields.len() && !fields[at].is_empty() {
        let status = fields[at]; at += 1;
        let count = if status.starts_with(['R', 'C']) { 2 } else { 1 };
        ensure!(at + count <= fields.len(), "truncated Git name-status record");
        for path in &fields[at..at + count] { if !path.is_empty() && !path.ends_with('/') { paths.insert((*path).to_owned()); } }
        at += count;
    }
    Ok(paths)
}

/// Working-tree source changes exclude ignored generated artifacts by Git's own tracking rules.
pub fn changed(root: &Path, base: Option<&str>, head: &str) -> Result<BTreeSet<String>> {
    if let Some(base) = base {
        return named_changes(&git(root, &["diff", "--name-status", "--find-renames", "-z", base, head])?.stdout);
    }
    let mut paths = nul_paths(&git(root, &["diff", "--name-only", "--no-renames", "-z", "HEAD"])?.stdout)?;
    paths.extend(nul_paths(&git(root, &["ls-files", "--others", "--exclude-standard", "-z"])?.stdout)?);
    Ok(paths)
}

fn bazel(root: &Path, program: Option<&Path>, args: &[String]) -> Result<String> {
    let mut command = Command::new(root.join("tools/run"));
    command.arg("--").arg(program.unwrap_or_else(|| Path::new("bazel"))).args(args).current_dir(root);
    if let Some(lease) = hsm_run_slots::inherited()? { lease.apply(&mut command)?; }
    let output = command.output()?;
    ensure!(output.status.success(), "Bazel {}: {}", args.join(" "), String::from_utf8_lossy(&output.stderr));
    Ok(String::from_utf8(output.stdout)?)
}

fn manifest_reach(paths: &BTreeSet<String>, rules: &BTreeMap<String, Rule>) -> Result<(BTreeSet<String>, BTreeSet<String>)> {
    let result = scope::manifest(&json!(paths), &serde_json::to_value(rules)?);
    Ok((strings(&result[0]).into_iter().collect(), strings(&result[1]).into_iter().collect()))
}

fn query_targets(root: &Path, paths: &BTreeSet<String>, program: Option<&Path>) -> Result<BTreeSet<String>> {
    if paths.is_empty() { return Ok(BTreeSet::new()); }
    let source = paths.iter().map(|path| format!("//:{path}")).collect::<Vec<_>>().join(" ");
    let query = format!("kind(\"rule\", rdeps(//..., set({source})))");
    Ok(bazel(root, program, &["query".into(), query])?.lines().map(str::trim).filter(|line| line.starts_with("//:")).map(str::to_owned).collect())
}

fn metadata_scope(root: &Path, options: &Options, paths: &BTreeSet<String>, plan: &Plan, rules: &BTreeMap<String, Rule>, inventory: &Value, config: &Value) -> Result<BTreeSet<String>> {
    if !options.artifacts || !paths.contains("tools/bazel/graph.json") { return Ok(BTreeSet::new()); }
    let (before_graph, after_graph, before_build, build_text) = if let Some(base) = &options.base {
        let at_head = git_tree(root, &options.head).is_some_and(|tree| Some(tree) == git_tree(root, "HEAD"));
        (git_file(root, base, "tools/bazel/graph.json"), git_file(root, &options.head, "tools/bazel/graph.json"),
            git_file(root, base, "BUILD.bazel"), at_head.then(|| git_file(root, &options.head, "BUILD.bazel")).flatten())
    } else {
        (git_file(root, "HEAD", "tools/bazel/graph.json"), fs::read_to_string(root.join("tools/bazel/graph.json")).ok(),
            git_file(root, "HEAD", "BUILD.bazel"), fs::read_to_string(root.join("BUILD.bazel")).ok())
    };
    let before = before_graph.as_deref().and_then(scope::normalized);
    let after = after_graph.as_deref().and_then(scope::normalized);
    let graph_safe = match (&before, &after) { (Some(a), Some(b)) => scope::projection(a, config) == scope::projection(b, config), _ => false };
    if !graph_safe { return Ok(BTreeSet::new()); }
    let mut safe = BTreeSet::from(["tools/bazel/graph.json".to_owned()]);
    let roots = after.as_ref().map(|graph| scope::artifact_roots(graph, inventory, config)).unwrap_or_default();
    let build_safe = !roots.is_empty() && match (before_build.as_deref(), build_text.as_deref()) {
        (Some(a), Some(b)) => match (scope::build_projection(a, &json!(roots)), scope::build_projection(b, &json!(roots))) { (Some(a), Some(b)) => a == b, _ => false },
        _ => false,
    };
    let generated = if let Some(text) = &build_text { planning::render_from_plan(plan.clone(), rules.clone())?.text == *text } else { false };
    if generated && build_safe {
        if paths.contains("BUILD.bazel") { safe.insert("BUILD.bazel".to_owned()); }
    }
    Ok(safe)
}

fn sentinels(paths: &BTreeSet<String>, artifacts: &BTreeSet<String>) -> BTreeSet<String> {
    let publication_changed = paths.iter().any(|path| path == "tools/hsm/build-plan/src/sync.rs" || path.starts_with("tools/hsm/publication/"));
    if !publication_changed { return BTreeSet::new(); }
    ["//:cold-core-assembly", "//:enclosure-assembly", "//:installed-machine", "//:enclosure"].into_iter().filter(|target| artifacts.contains(*target)).map(str::to_owned).collect()
}

/// Selection resolves an explicit or Git-reported source set without building geometry.
pub fn select(root: &Path, options: &Options) -> Result<Selection> {
    let plan = planning::action_plan(root, None)?;
    let inventory = serde_json::to_value(&plan.inventory)?;
    let config = planning::inventory_config(root)?;
    let graph: Value = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
    let classification = scope::Classification::new(config.clone(), graph, &inventory);
    let artifacts = scope::artifact_targets(&inventory);
    if options.all_artifacts { return Ok(Selection { targets: artifacts, ..Selection::default() }); }
    let head = if options.head.is_empty() { "HEAD" } else { &options.head };
    let mut paths = match &options.explicit_paths { Some(paths) => paths.clone(), None => changed(root, options.base.as_deref(), head)? };
    paths.retain(|path| !options.exclude.contains(path));
    if options.dirty_sources { paths.remove("hardware/cad-artifacts.json"); }
    paths = classification.filter_moved(&paths, false);
    let rules = planning::dependency_rules_for_plan(root, &plan)?;
    if options.dirty_sources {
        paths.retain(|path| !classification.presentation(path) && !(path.ends_with(".scorecard.json") && classification.declared.contains(path)));
        let (found, known) = manifest_reach(&paths, &rules)?;
        let mut targets = found.intersection(&artifacts).cloned().collect::<BTreeSet<_>>(); targets.extend(sentinels(&paths, &artifacts));
        return Ok(Selection { targets, paths, known, ..Selection::default() });
    }
    let safe = metadata_scope(root, options, &paths, &plan, &rules, &inventory, &config)?;
    paths = classification.filter_moved(&paths, options.artifacts);
    if paths.is_empty() { return Ok(Selection::default()); }
    let (mut found, known) = if options.manifest { manifest_reach(&paths, &rules)? } else {
        let source_files = bazel(root, options.bazel.as_deref(), &["query".into(), "kind(\"source file\", //:*)".into()])?
            .lines().map(str::trim).filter_map(|line| line.strip_prefix("//:").map(str::to_owned)).collect::<BTreeSet<_>>();
        let known = paths.intersection(&source_files).cloned().collect::<BTreeSet<_>>();
        (query_targets(root, &known, options.bazel.as_deref())?, known)
    };
    let risky = classification.risky(&paths, &known, &safe, options.artifacts);
    if !risky.is_empty() { found = if options.artifacts { artifacts.clone() } else { BTreeSet::from(["//:everything".into()]) }; }
    else if options.artifacts { found = found.intersection(&artifacts).cloned().collect(); }
    let mut reach = BTreeMap::new();
    if options.why {
        for path in &known {
            let one = BTreeSet::from([path.clone()]);
            let targets = if options.manifest { manifest_reach(&one, &rules)?.0 } else { query_targets(root, &one, options.bazel.as_deref())? };
            reach.insert(path.clone(), targets);
        }
    }
    Ok(Selection { targets: found, paths, known, risky, reach })
}

fn examples() -> Result<()> {
    let graph = |source: &str| json!({"part.rs":{"reads":[source],"writes":["hardware/part.stl"],"rewritten":[],
        "program":{"crate":"part","name":"part","sources":[source]}}});
    let before = scope::normalized(&graph("part.rs").to_string()).context("normalize native producer")?;
    let changed = scope::normalized(&graph("other.rs").to_string()).context("normalize changed producer")?;
    ensure!(scope::projection(&before, &json!({})) != scope::projection(&changed, &json!({})), "changed compiler sources must affect artifact scope");
    ensure!(named_changes(b"R100\0old name.rs\0new name.rs\0M\0hardware/layout.json\0")?.len() == 3, "renamed sources retain both paths");
    Ok(())
}

pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut options = Options { head: "HEAD".to_owned(), ..Options::default() };
    let mut json_output = false; let mut at = 0;
    while at < args.len() {
        match args[at].as_str() {
            "--why" => options.why = true,
            "--artifacts" => options.artifacts = true,
            "--manifest" => options.manifest = true,
            "--all-artifacts" => options.all_artifacts = true,
            "--dirty-sources" => { options.dirty_sources = true; options.artifacts = true; options.manifest = true; }
            "--json" => json_output = true,
            "--base" | "--head" | "--path" | "--exclude" | "--bazel" => {
                let flag = &args[at]; at += 1; let value = args.get(at).with_context(|| format!("{flag} requires a value"))?;
                match flag.as_str() {
                    "--base" => options.base = Some(value.clone()), "--head" => options.head = value.clone(),
                    "--path" => { options.explicit_paths.get_or_insert_with(BTreeSet::new).insert(value.clone()); }
                    "--exclude" => { options.exclude.insert(value.clone()); }
                    "--bazel" => options.bazel = Some(value.into()), _ => unreachable!(),
                }
            }
            "selftest" => { examples()?; println!("native affected fixtures pass"); return Ok(0); }
            "--help" | "-h" => {
                println!("Select declared build targets reached by changed sources.\n\nUsage: hsm-build-plan [--root ROOT] affected [--artifacts --manifest] [--base REF --head REF] [--why] [--json] [--path PATH ...]\n       hsm-build-plan [--root ROOT] affected --dirty-sources --json [--exclude SIDECAR ...]"); return Ok(0);
            }
            arg => bail!("unknown affected argument {arg}"),
        }
        at += 1;
    }
    ensure!(!options.manifest || options.artifacts, "--manifest requires --artifacts");
    let selection = select(root, &options)?;
    if json_output { println!("{}", serde_json::to_string(&selection)?); return Ok(0); }
    if selection.paths.is_empty() && !options.all_artifacts { eprintln!("nothing has moved — the selected source set holds nothing to build"); }
    if !selection.risky.is_empty() {
        eprintln!("{} changed paths cannot be scoped; the selected build widens:", selection.risky.len());
        for path in &selection.risky { eprintln!("    {path}"); }
    }
    for target in &selection.targets {
        println!("{target}");
        if options.why { for (path, reach) in &selection.reach { if reach.contains(target) { println!("    {path}"); } } }
    }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn native_metadata_and_rename_examples() { examples().unwrap(); }
    #[test]
    fn presentation_changes_leave_native_artifact_projection_intact() {
        let native = |name: &str, sources: Value| json!({"reads":sources,"writes":[format!("hardware/{name}.stl")],"rewritten":[],
            "program":{"crate":name,"name":name,"sources":[format!("{name}.rs")]}});
        let mut before = json!({"part.rs":native("part",json!(["part.rs"])),"docs.rs":{"reads":["guide.md"],"writes":["guide.pdf"],"rewritten":[],
            "program":{"crate":"docs","name":"docs","sources":["docs.rs"]}}});
        let a = scope::normalized(&before.to_string()).unwrap();
        before["docs.rs"]["reads"] = json!(["new-guide.md"]);
        let b = scope::normalized(&before.to_string()).unwrap();
        assert_eq!(scope::projection(&a, &json!({})), scope::projection(&b, &json!({})));
        before["part.rs"]["program"]["runtime_inputs"] = json!(["part.rs"]);
        let c = scope::normalized(&before.to_string()).unwrap();
        assert_ne!(scope::projection(&a, &json!({})), scope::projection(&c, &json!({})));
    }
    #[test]
    fn classification_keeps_authored_geometry_inputs_and_omits_presentation() {
        let graph = json!({"part.rs":{"reads":["part.rs","hardware/layout.json"],"writes":["hardware/part.stl"],"rewritten":[]},
            "docs.rs":{"reads":["hardware/notes.md"],"writes":["hardware/notes.md"],"rewritten":["hardware/notes.md"]}});
        let inventory = json!([[ ["part.rs"], {"solids":["hardware/part.stl"],"reads":[],"docs":[]} ]]);
        let classification = scope::Classification::new(json!({"inert_suffixes":[".3mf"]}), graph, &inventory);
        let paths = ["hardware/notes.md","hardware/layout.json","hardware/project.3mf"].into_iter().map(str::to_owned).collect();
        assert_eq!(classification.filter_moved(&paths, true), BTreeSet::from(["hardware/layout.json".to_owned()]));
        assert!(!classification.unknown("hardware/cad-artifacts.json", true));
    }
}
