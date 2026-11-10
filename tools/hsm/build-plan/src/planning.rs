//! Typed producer declarations render selective Rust build actions and stable graph support inputs.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::{inventory, publication, sources, support};
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{collections::{BTreeMap, BTreeSet}, fs, path::{Component, Path, PathBuf}};

/// A producer's compiled program and the source files it also reads while running.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct Program {
    #[serde(rename = "crate")] pub krate: String,
    pub name: String,
    #[serde(default)] pub sources: BTreeSet<String>,
    #[serde(default, skip_serializing_if = "BTreeSet::is_empty")] pub runtime_inputs: BTreeSet<String>,
}

/// An inventory entry keeps whole generated outputs separate from rewritten authored media.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct InventoryEntry {
    #[serde(default)] pub solids: Vec<String>,
    #[serde(default)] pub docs: Vec<String>,
    #[serde(default)] pub reads: BTreeSet<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")] pub program: Option<Program>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct InventoryRow(pub Vec<String>, pub InventoryEntry);

/// An action names the generator cohort, runtime inputs and other producers it depends on.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Action {
    pub generators: Vec<String>,
    pub entrypoints: Vec<Vec<String>>,
    pub solids: Vec<String>,
    pub docs: Vec<String>,
    pub reads: Vec<String>,
    pub optional: Vec<String>,
    pub producers: BTreeMap<String, String>,
    pub dependencies: BTreeSet<String>,
    pub node_runtimes: Vec<String>,
    pub support_inputs: BTreeMap<String, String>,
    pub program: Program,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum RuleKind { Action, Graph, Runtime, Aggregate }

/// Rule declarations are shared by BUILD rendering and affected-target discovery.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Rule {
    pub kind: RuleKind,
    #[serde(default, skip_serializing_if = "Vec::is_empty")] pub srcs: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")] pub outs: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")] pub tools: Vec<String>,
    #[serde(default, skip_serializing_if = "Vec::is_empty")] pub globs: Vec<(Vec<String>, Vec<String>)>,
    #[serde(default, skip_serializing_if = "Option::is_none")] pub generator: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")] pub program: Option<Program>,
}

impl Rule {
    fn new(kind: RuleKind) -> Self { Self { kind, srcs: Vec::new(), outs: Vec::new(), tools: Vec::new(), globs: Vec::new(), generator: None, program: None } }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Plan {
    pub actions: BTreeMap<String, Action>,
    pub inventory: Vec<InventoryRow>,
    pub action_order: Vec<String>,
    pub producers: BTreeMap<String, String>,
}

pub struct RenderedBuild { pub text: String, pub plan: Plan }

const GRAPH_OUTPUT: &str = "support/enclosure-assembly-graph.json";
const GRAPH_READER: &str = "hardware/manifold-layout/installed_machine.rs";
const GRAPH_CONSUMERS: &[&str] = &["installed-machine", "bom-masses", "enclosure-mechanical-sync", "internal-plumbing-sync", "fluid-topology-sync", "enclosure-dimensions"];
const NODE_ROOTS: &[&str] = &["tools/render/", "web/"];

pub fn inventory_config(root: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&fs::read(root.join("tools/hsm/build-plan/inventory.json"))?)?)
}

pub fn publication_config(root: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&fs::read(root.join("tools/hsm/publication/config.json"))?)?)
}

pub fn load_inventory(root: &Path) -> Result<Vec<InventoryRow>> {
    let config = inventory_config(root)?;
    let files = inventory::tracked(root, &config, &publication_config(root)?)?;
    let graph: Value = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
    Ok(serde_json::from_value(inventory::inventory(root, &graph, files, &config)?)?)
}

pub fn target_name(generator: &str, shared: &BTreeSet<String>) -> String { publication::target_name(generator, shared) }

fn stem(generator: &str) -> String {
    Path::new(generator).file_stem().unwrap_or_default().to_string_lossy().trim_matches('_').replace('_', "-")
}

fn normalized(path: PathBuf) -> String {
    let mut result = PathBuf::new();
    for component in path.components() {
        match component { Component::CurDir => (), Component::ParentDir if result.file_name().is_some() => { result.pop(); }, _ => result.push(component.as_os_str()) }
    }
    result.to_string_lossy().into_owned()
}

fn js_closure(root: &Path, reads: &BTreeSet<String>) -> Result<BTreeSet<String>> {
    let local = Regex::new(r#"(?:from|import|require)\s*\(?\s*["'](\.[^"']*)["']"#)?;
    let is_js = |path: &str| [".js", ".mjs", ".cjs"].iter().any(|suffix| path.ends_with(suffix));
    let mut stack = reads.iter().filter(|path| is_js(path)).cloned().collect::<Vec<_>>();
    let mut seen = BTreeSet::new();
    while let Some(current) = stack.pop() {
        let Ok(text) = fs::read_to_string(root.join(&current)) else { continue };
        for found in local.captures_iter(&text) {
            let path = normalized(Path::new(&current).parent().unwrap_or_else(|| Path::new("")).join(&found[1]));
            if root.join(&path).is_file() && seen.insert(path.clone()) { stack.push(path); }
        }
    }
    Ok(seen.difference(reads).cloned().collect())
}

fn node_runtimes(reads: &[String]) -> Vec<String> {
    if reads.iter().any(|path| NODE_ROOTS.iter().any(|root| path.starts_with(root)) && [".js", ".mjs", ".cjs"].iter().any(|suffix| path.ends_with(suffix))) {
        vec![":node-packages".to_owned()]
    } else { Vec::new() }
}

fn no_cycles(wants: &BTreeMap<String, BTreeSet<String>>) -> Result<()> {
    fn walk<'a>(name: &'a str, wants: &'a BTreeMap<String, BTreeSet<String>>, seen: &mut BTreeSet<&'a str>, stack: &mut Vec<&'a str>) -> Result<()> {
        if let Some(at) = stack.iter().position(|value| *value == name) {
            let mut cycle = stack[at..].to_vec(); cycle.push(name);
            bail!("build-plan: these rules wait on each other:\n    {}", cycle.windows(2).map(|pair| format!("{} reads {}", pair[0], pair[1])).collect::<Vec<_>>().join("\n    "));
        }
        if !seen.insert(name) { return Ok(()); }
        stack.push(name);
        for next in wants.get(name).into_iter().flatten() { walk(next, wants, seen, stack)?; }
        stack.pop(); Ok(())
    }
    let mut seen = BTreeSet::new(); let mut stack = Vec::new();
    for name in wants.keys() { walk(name, wants, &mut seen, &mut stack)?; }
    Ok(())
}

/// Planning reads the existing inventory once and preserves producer edges through selected actions.
pub fn action_plan(root: &Path, only: Option<&str>) -> Result<Plan> {
    let config = inventory_config(root)?;
    let files = inventory::tracked(root, &config, &publication_config(root)?)?;
    let graph: Value = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
    let inventory: Vec<InventoryRow> = serde_json::from_value(inventory::inventory(root, &graph, files.clone(), &config)?)?;
    actions_from_inventory(root, inventory, files, only)
}

pub fn actions_from_inventory(root: &Path, all_inventory: Vec<InventoryRow>, files: BTreeSet<String>, only: Option<&str>) -> Result<Plan> {
    let mut seen = BTreeSet::new(); let mut shared = BTreeSet::new();
    for InventoryRow(generators, _) in &all_inventory { for generator in generators { let name = stem(generator); if !seen.insert(name.clone()) { shared.insert(name); } } }
    let mut names = BTreeMap::new();
    for InventoryRow(generators, _) in &all_inventory {
        let generator = generators.first().context("a generator cohort is empty")?;
        names.insert(generators.clone(), target_name(generator, &shared));
    }
    let mut producers = BTreeMap::new();
    let mut held = files;
    for InventoryRow(generators, made) in &all_inventory {
        held.extend(generators.iter().cloned()); held.extend(made.solids.iter().cloned()); held.extend(made.docs.iter().cloned());
        for path in made.solids.iter().chain(made.docs.iter().filter(|path| path.ends_with(".png") || path.ends_with(".json"))) { producers.insert(path.clone(), names[generators].clone()); }
    }
    let mut inventory = all_inventory.into_iter().filter(|InventoryRow(generators, _)| only.is_none_or(|only| generators.iter().any(|generator| generator == only) || names[generators] == only)).collect::<Vec<_>>();
    inventory.sort_by(|a, b| a.0.cmp(&b.0));
    let mut actions = BTreeMap::new(); let mut order = Vec::new(); let mut wants = BTreeMap::new();
    for InventoryRow(generators, made) in &inventory {
        let name = names[generators].clone();
        let solids = made.solids.iter().cloned().collect::<BTreeSet<_>>();
        let probes = made.reads.iter().filter(|read| read.strip_suffix(".mesh").is_some_and(|path| read.ends_with(".step.mesh") && solids.contains(path))).cloned().collect::<BTreeSet<_>>();
        let optional = made.docs.iter().filter(|path| path.ends_with(".png") || path.ends_with(".json")).cloned().collect::<BTreeSet<_>>();
        let mut reads = made.reads.iter().chain(made.docs.iter()).chain(generators.iter()).filter(|path| !solids.contains(*path) && !probes.contains(*path) && !optional.contains(*path)).cloned().collect::<BTreeSet<_>>();
        reads.extend(js_closure(root, &reads)?); reads.retain(|path| held.contains(path));
        let reads = reads.into_iter().collect::<Vec<_>>();
        let dependencies = reads.iter().filter_map(|path| producers.get(path)).filter(|producer| *producer != &name).cloned().collect::<BTreeSet<_>>();
        let support_inputs = if GRAPH_CONSUMERS.contains(&name.as_str()) && reads.iter().any(|path| path == "tools/bazel/graph.json") {
            BTreeMap::from([("tools/bazel/graph.json".to_owned(), GRAPH_OUTPUT.to_owned())])
        } else { BTreeMap::new() };
        let program = made.program.clone().with_context(|| format!("{name} has no native program declaration; register its Rust producer before rendering the print build"))?;
        wants.insert(name.clone(), dependencies.clone()); order.push(name.clone());
        actions.insert(name, Action { generators: generators.clone(), entrypoints: generators.iter().map(|generator| vec![generator.clone()]).collect(),
            solids: made.solids.clone(), docs: made.docs.clone(), node_runtimes: node_runtimes(&reads),
            reads: reads.clone(), optional: optional.into_iter().collect(), producers: reads.iter().filter_map(|path| producers.get(path).map(|producer| (path.clone(), producer.clone()))).collect(),
            dependencies, support_inputs, program });
    }
    no_cycles(&wants)?;
    Ok(Plan { actions, inventory, action_order: order, producers })
}

pub fn read_from(source: &str, producers: &BTreeMap<String, String>, consumer: &str, support: &BTreeMap<String, String>) -> String {
    if let Some(output) = support.get(source) { return format!(":{output}"); }
    if let Some(producer) = producers.get(source).filter(|producer| *producer != consumer) { return format!(":out/{producer}/{source}"); }
    source.to_owned()
}

pub fn dependency_rules(actions: &BTreeMap<String, Action>) -> Result<BTreeMap<String, Rule>> {
    let mut rules = BTreeMap::new(); let mut support_used = BTreeSet::new();
    for (name, action) in actions {
        let mut rule = Rule::new(RuleKind::Action);
        rule.srcs = action.reads.iter().map(|source| read_from(source, &action.producers, name, &action.support_inputs)).chain(action.node_runtimes.iter().cloned()).collect();
        rule.outs = action.solids.iter().chain(action.docs.iter()).map(|path| format!("out/{name}/{path}")).collect();
        if !action.optional.is_empty() { rule.globs.push((action.optional.clone(), Vec::new())); }
        rule.program = Some(action.program.clone()); rules.insert(name.clone(), rule); support_used.extend(action.support_inputs.values().cloned());
    }
    for output in support_used {
        ensure!(output == GRAPH_OUTPUT, "unknown graph support output {output}");
        let mut rule = Rule::new(RuleKind::Graph);
        rule.generator = Some(GRAPH_READER.to_owned()); rule.srcs = vec!["tools/bazel/graph.json".to_owned()]; rule.outs = vec![output.clone()];
        rule.tools = vec![":out/build-plan-support-program/hsm-build-plan".to_owned()];
        rules.insert(format!("support-{}", Path::new(&output).file_stem().unwrap_or_default().to_string_lossy()), rule);
    }
    let mut cards = Rule::new(RuleKind::Runtime); cards.globs.push((vec!["tools/render/node_modules/**".to_owned()], Vec::new())); rules.insert("render-card-runtime".to_owned(), cards);
    let mut node = Rule::new(RuleKind::Runtime); node.globs.push((vec!["tools/render/**".to_owned(), "web/**".to_owned()], Vec::new())); rules.insert("node-packages".to_owned(), node);
    let mut all = Rule::new(RuleKind::Aggregate); all.srcs = actions.keys().map(|name| format!(":{name}")).collect(); rules.insert("everything".to_owned(), all);
    Ok(rules)
}

pub fn shell_quote(text: &str) -> String {
    if !text.is_empty() && text.chars().all(|c| c.is_ascii_alphanumeric() || "_@%+=:,./-".contains(c)) { text.to_owned() }
    else { format!("'{}'", text.replace('\'', "'\"'\"'")) }
}

fn support_program(root: &Path) -> Result<Program> {
    let mut source_files = sources::compiled(&root.join("tools/hsm/target/release/hsm-build-plan.d"), root).context("read compiled graph-support program sources")?;
    let manifests = sources::manifests(&source_files, "build-plan", root);
    source_files.extend(manifests);
    Ok(Program { krate: "build-plan".to_owned(), name: "hsm-build-plan".to_owned(), sources: source_files.into_iter().collect(), runtime_inputs: BTreeSet::new() })
}

/// Graph support compilation declares its own sources when a producer needs a projection.
pub fn dependency_rules_for_plan(root: &Path, plan: &Plan) -> Result<BTreeMap<String, Rule>> {
    let mut rules = dependency_rules(&plan.actions)?;
    if rules.values().any(|rule| rule.kind == RuleKind::Graph) {
        let program = support_program(root)?;
        let mut rule = Rule::new(RuleKind::Runtime);
        rule.srcs = program.sources.iter().map(|source| read_from(source, &plan.producers, "build-plan-support", &BTreeMap::new())).collect();
        rule.outs = vec![crate::rust_step::program_output("build-plan-support", &program)];
        rule.program = Some(program);
        rules.insert("build-plan-support-program".to_owned(), rule);
    }
    Ok(rules)
}

/// BUILD text names each native program's compilation separately from its runtime data.
pub fn render_build(root: &Path, only: Option<&str>) -> Result<RenderedBuild> {
    let plan = action_plan(root, only)?;
    let rules = dependency_rules_for_plan(root, &plan)?;
    render_from_plan(plan, rules)
}

/// Rendering accepts an already loaded plan so affected-target discovery reuses its inventory.
pub fn render_from_plan(plan: Plan, mut rules: BTreeMap<String, Rule>) -> Result<RenderedBuild> {
    let mut blocks = Vec::new();
    for name in &plan.action_order {
        let action = &plan.actions[name];
        let made = action.solids.iter().chain(action.docs.iter()).cloned().collect::<Vec<_>>();
        blocks.push(crate::rust_step::render(name, &rules[name], &made, &action.support_inputs)?);
    }
    if rules.values().any(|rule| rule.kind == RuleKind::Graph) {
        let compiler = &rules["build-plan-support-program"];
        blocks.push(crate::rust_step::program_rule("build-plan-support", compiler.program.as_ref().context("graph support program")?, &compiler.srcs)?);
        for (name, rule) in rules.iter().filter(|(_, rule)| rule.kind == RuleKind::Graph) {
            let generator = rule.generator.as_deref().context("graph support generator")?;
            let tool = rule.tools.first().context("graph support tool")?;
            let source = rule.srcs.first().context("graph support source")?;
            let output = rule.outs.first().context("graph support output")?;
            blocks.push(format!("genrule(\n    name = \"{name}\",\n    srcs = [\"{source}\"],\n    outs = [\"{output}\"],\n    tools = [\"{tool}\"],\n    cmd = \"$(location {tool}) project-graph-file {generator} $(location {source}) $@\",\n)"));
        }
    }
    for name in ["render-card-runtime", "node-packages"] {
        let rule = &rules[name]; let patterns = &rule.globs[0].0;
        blocks.push(format!("filegroup(\n    name = \"{name}\",\n    srcs = glob(\n        {},\n        allow_empty = True,\n    ),\n)", serde_json::to_string(patterns)?));
    }
    rules.get_mut("everything").unwrap().srcs = plan.action_order.iter().map(|name| format!(":{name}")).collect();
    blocks.push(format!("filegroup(\n    name = \"everything\",\n    srcs = [\n{}    ],\n)", rules["everything"].srcs.iter().map(|source| format!("        \"{source}\",\n")).collect::<String>()));
    Ok(RenderedBuild { text: format!("# Native producer actions and their declared data are rendered by hsm-build-plan.\n\n{}\n", blocks.join("\n\n")), plan })
}

/// Checkout-local flags retain the shared cache and verified lease broker in Bazel actions.
pub fn render_rc_paths(root: &Path) -> Result<String> {
    let broker = hsm_run_slots::runtime::slots::broker_config(root)?;
    let directory = hsm_run_slots::directory()?;
    Ok(format!("# hsm-build-plan names this checkout's paths and native lease broker.\nbuild --action_env=HSM_WORKSPACE={}\nbuild --sandbox_add_mount_pair={}/.cache\nbuild --sandbox_writable_path={}/.cache/meshes\nbuild --sandbox_writable_path={}/.cache/realized\nbuild --action_env=HSM_RUN_BROKER={}\nbuild --sandbox_add_mount_pair={}\n", root.display(), root.display(), root.display(), root.display(), shell_quote(&broker), directory.display()))
}

pub fn write_graph_projection(generator: &str, source: &Path, output: &Path) -> Result<()> { support::write_projection(source, output, generator) }

pub fn write(root: &Path, only: Option<&str>) -> Result<RenderedBuild> {
    let built = render_build(root, only)?;
    if only.is_none() { fs::write(root.join("BUILD.bazel"), &built.text)?; fs::write(root.join(".bazelrc.paths"), render_rc_paths(root)?)?; }
    Ok(built)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn row(generator: &str, outputs: &[&str], reads: &[&str], docs: &[&str]) -> InventoryRow {
        serde_json::from_value(json!([[generator], {
            "solids": outputs, "docs": docs, "reads": reads,
            "program": {"crate": "fixture", "name": "fixture", "sources": [generator]}
        }])).unwrap()
    }

    fn plan(rows: Vec<InventoryRow>, files: &[&str], only: Option<&str>) -> Result<Plan> {
        actions_from_inventory(Path::new("/absent-build-plan-fixture"), rows, files.iter().map(|path| (*path).to_owned()).collect(), only)
    }

    #[test]
    fn selected_action_keeps_global_producer_names_and_exact_edges() {
        let rows = vec![
            row("hardware/frame/build.rs", &["hardware/frame/part.step"], &[], &[]),
            row("hardware/cover/build.rs", &["hardware/cover/part.step"], &["hardware/frame/part.step", "hardware/cover/parameters.json"], &[]),
        ];
        let result = plan(rows, &["hardware/cover/parameters.json"], Some("hardware/cover/build.rs")).unwrap();
        assert_eq!(result.action_order, ["cover-build"]);
        let action = &result.actions["cover-build"];
        assert_eq!(action.dependencies, BTreeSet::from(["frame-build".to_owned()]));
        let rules = dependency_rules(&result.actions).unwrap();
        assert!(rules["cover-build"].srcs.contains(&":out/frame-build/hardware/frame/part.step".to_owned()));
        assert!(rules["cover-build"].srcs.contains(&"hardware/cover/parameters.json".to_owned()));
        assert_eq!(result.producers["hardware/frame/part.step"], "frame-build");
    }

    #[test]
    fn own_step_probe_and_authored_media_keep_their_classification() {
        let own_step = "hardware/cover/part.step";
        let own_probe = "hardware/cover/part.step.mesh";
        let document = "hardware/cover/guide.md";
        let image = "hardware/cover/guide.png";
        let record = "hardware/cover/guide.json";
        let rows = vec![row("hardware/cover/build.rs", &[own_step], &[own_step, own_probe, document, image, record], &[document, image, record])];
        let result = plan(rows, &[own_probe], None).unwrap();
        let action = &result.actions["cover-build"];
        assert!(!action.reads.contains(&own_step.to_owned()));
        assert!(!action.reads.contains(&own_probe.to_owned()));
        assert!(action.reads.contains(&document.to_owned()));
        assert_eq!(action.optional, [record, image]);
        assert!(action.dependencies.is_empty());
    }

    #[test]
    fn producer_cycle_reports_the_paths_between_rules() {
        let rows = vec![
            row("hardware/left.rs", &["hardware/left.step"], &["hardware/right.step"], &[]),
            row("hardware/right.rs", &["hardware/right.step"], &["hardware/left.step"], &[]),
        ];
        let error = plan(rows, &[], None).unwrap_err().to_string();
        assert!(error.contains("left reads right"));
        assert!(error.contains("right reads left"));
    }

    #[test]
    fn rendering_requires_a_declared_native_program() {
        let row = InventoryRow(vec!["hardware/forgotten.rs".to_owned()], InventoryEntry { solids: vec!["hardware/part.step".to_owned()], ..Default::default() });
        assert!(plan(vec![row], &[], None).unwrap_err().to_string().contains("no native program declaration"));
    }

    #[test]
    fn support_projection_keeps_only_the_selected_reader_classification() {
        let graph = json!({
            "reader": {"reads": ["derived.json", "authored.json"], "writes": ["own.step"], "rewritten": []},
            "writer": {"reads": ["unrelated.json"], "writes": ["derived.json"], "rewritten": ["authored.json"]}
        });
        let result = support::project_graph(&graph, "reader");
        assert_eq!(result["reader"]["reads"], json!(["authored.json", "derived.json"]));
        assert_eq!(result["@derived-input-classification"]["writes"], json!(["derived.json"]));
        assert_eq!(result["@derived-input-classification"]["rewritten"], json!(["authored.json"]));
        assert!(result.get("writer").is_none());
    }

    fn rule(kind: RuleKind, inputs: &[&str], outputs: &[&str]) -> Rule {
        let mut declaration = Rule::new(kind);
        declaration.srcs = inputs.iter().map(|path| (*path).to_owned()).collect();
        declaration.outs = outputs.iter().map(|path| (*path).to_owned()).collect();
        declaration
    }

    #[test]
    fn typed_manifest_follows_generated_outputs_and_transitive_filegroups() {
        let rules = BTreeMap::from([
            ("source", rule(RuleKind::Runtime, &["hardware/part.rs"], &["generated/hardware/part.rs"])),
            ("part", rule(RuleKind::Action, &["generated/hardware/part.rs"], &["out/part/part.step"])),
            ("pieces", rule(RuleKind::Runtime, &[":out/part/part.step"], &[])),
            ("assembly", rule(RuleKind::Action, &[":pieces"], &["out/assembly/assembly.step.mesh"])),
            ("notes", rule(RuleKind::Action, &["hardware/part.rs"], &["out/notes.md"])),
        ]);
        let reached = hsm_build_data::bookkeeping_affected::manifest(&json!(["hardware/part.rs"]), &serde_json::to_value(rules).unwrap());
        assert_eq!(reached[0], json!(["//:assembly", "//:part"]));
        assert_eq!(reached[1], json!(["hardware/part.rs"]));
    }

    #[test]
    fn typed_manifest_globs_match_zero_or_many_directories_and_exclusions() {
        let mut web = Rule::new(RuleKind::Runtime);
        web.globs.push((vec!["web/**".to_owned()], vec!["web/**/ignored.js".to_owned()]));
        let rules = BTreeMap::from([("web", web), ("part", rule(RuleKind::Action, &[":web"], &["out/part.step"]))]);
        let declarations = serde_json::to_value(rules).unwrap();
        for path in ["web/a.js", "web/a/b/c.js"] {
            let reached = hsm_build_data::bookkeeping_affected::manifest(&json!([path]), &declarations);
            assert_eq!(reached, json!([["//:part"], [path]]));
        }
        assert_eq!(hsm_build_data::bookkeeping_affected::manifest(&json!(["web/ignored.js", "web/a/ignored.js"]), &declarations), json!([[], []]));
    }

    #[test]
    fn dynamic_select_expression_cannot_deserialize_as_empty_typed_inputs() {
        let dynamic = json!({"kind":"action", "srcs":{"select":{"//conditions:default":[]}}, "outs":["part.step"]});
        assert!(serde_json::from_value::<Rule>(dynamic).is_err());
    }

    #[test]
    fn rendered_artifact_producers_equal_the_inventory() {
        let rows = vec![
            row("hardware/part.rs", &["hardware/part.step"], &[], &[]),
            row("hardware/assembly.rs", &["hardware/assembly.step.mesh"], &["hardware/part.step"], &[]),
            row("hardware/notes.rs", &["hardware/notes.pdf"], &[], &[]),
        ];
        let plan = plan(rows, &[], None).unwrap();
        let expected = hsm_build_data::bookkeeping_affected::artifact_targets(&serde_json::to_value(&plan.inventory).unwrap());
        let rules = dependency_rules(&plan.actions).unwrap();
        let rendered = render_from_plan(plan, rules).unwrap().text;
        let names_and_outputs = Regex::new(r#"(?s)genrule\(\n    name = "([^"]+)",.*?    outs = \[(.*?)\],"#).unwrap();
        let quoted_output = Regex::new(r#""([^"]+)""#).unwrap();
        let actual = names_and_outputs.captures_iter(&rendered).filter_map(|capture| {
            quoted_output.captures_iter(&capture[2]).any(|output| hsm_build_data::bookkeeping_common::CAD.iter().any(|suffix| output[1].ends_with(suffix)))
                .then(|| format!("//:{}", &capture[1]))
        }).collect::<BTreeSet<_>>();
        assert_eq!(actual, expected);
    }
}
