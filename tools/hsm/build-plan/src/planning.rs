//! Declared native producers share target selection, dependency closure and compact runtime inputs.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::{inventory, publication, support};
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Component, Path, PathBuf},
};

pub const GRAPH_PATH: &str = "tools/hsm/build-plan/graph.json";
const CAD_OUTPUTS: &[&str] = &[".step", ".stl", ".glb", ".step.mesh"];

/// A program separates its compiler closure from source files it explicitly reads while running.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct Program {
    #[serde(rename = "crate")]
    pub krate: String,
    pub name: String,
    #[serde(default)]
    pub sources: BTreeSet<String>,
    #[serde(default, skip_serializing_if = "BTreeSet::is_empty")]
    pub runtime_inputs: BTreeSet<String>,
}

impl Program {
    pub fn compiler_only(&self, source: &str) -> bool {
        let code = source.ends_with(".rs")
            || ["Cargo.toml", "Cargo.lock", "cargo-config.json"].contains(
                &Path::new(source)
                    .file_name()
                    .unwrap_or_default()
                    .to_string_lossy()
                    .as_ref(),
            );
        self.sources.contains(source) && code && !self.runtime_inputs.contains(source)
    }
}

/// Inventory keeps whole generated outputs separate from rewritten authored media.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct InventoryEntry {
    #[serde(default)]
    pub solids: Vec<String>,
    #[serde(default)]
    pub docs: Vec<String>,
    #[serde(default)]
    pub reads: BTreeSet<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub program: Option<Program>,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct InventoryRow(pub Vec<String>, pub InventoryEntry);

/// A graph projection retains only the classifications a producer actually reads.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct GraphProjection {
    pub generator: String,
}

impl GraphProjection {
    pub fn render_value(&self, graph: &Value) -> Result<Vec<u8>> {
        let mut bytes = serde_json::to_vec(&support::project_graph(graph, &self.generator))?;
        bytes.push(b'\n');
        Ok(bytes)
    }
    pub fn render(&self, root: &Path) -> Result<Vec<u8>> {
        self.render_value(&serde_json::from_slice(&fs::read(root.join(GRAPH_PATH))?)?)
    }
    pub fn write(&self, root: &Path, destination: &Path) -> Result<()> {
        let bytes = self.render(root)?;
        if fs::read(destination).ok().as_deref() != Some(bytes.as_slice()) {
            if let Some(parent) = destination.parent() {
                fs::create_dir_all(parent)?;
            }
            fs::write(destination, bytes)?;
        }
        Ok(())
    }
}

/// A runtime input names the source or producer export staged at its repository path.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct RuntimeInput {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub producer: Option<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub projection: Option<GraphProjection>,
    #[serde(default, skip_serializing_if = "is_false")]
    pub optional: bool,
}
fn is_false(value: &bool) -> bool {
    !*value
}

/// An action is one native executable with declared exports and producer dependencies.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct Action {
    pub generators: Vec<String>,
    pub solids: Vec<String>,
    pub docs: Vec<String>,
    pub reads: Vec<String>,
    pub optional: Vec<String>,
    pub producers: BTreeMap<String, String>,
    pub dependencies: BTreeSet<String>,
    pub support_inputs: BTreeMap<String, GraphProjection>,
    pub program: Program,
}

impl Action {
    pub fn outputs(&self) -> impl Iterator<Item = &str> {
        self.solids.iter().chain(&self.docs).map(String::as_str)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Plan {
    pub actions: BTreeMap<String, Action>,
    pub inventory: Vec<InventoryRow>,
    pub action_order: Vec<String>,
    pub producers: BTreeMap<String, String>,
}

/// A selection distinguishes requested work from the prerequisites required to execute it.
#[derive(Debug, Clone, Default, Serialize, Deserialize, PartialEq, Eq)]
pub struct Selection {
    pub requested: BTreeSet<String>,
    pub closure: BTreeSet<String>,
    pub order: Vec<String>,
}

impl Plan {
    pub fn default_targets(&self) -> BTreeSet<String> {
        self.actions.keys().cloned().collect()
    }
    pub fn artifact_targets(&self) -> BTreeSet<String> {
        self.actions
            .iter()
            .filter(|(_, action)| {
                action
                    .solids
                    .iter()
                    .any(|path| CAD_OUTPUTS.iter().any(|suffix| path.ends_with(suffix)))
            })
            .map(|(name, _)| name.clone())
            .collect()
    }
    pub fn known_files(&self) -> BTreeSet<String> {
        self.actions
            .values()
            .flat_map(|action| {
                action
                    .reads
                    .iter()
                    .chain(&action.generators)
                    .chain(&action.optional)
                    .chain(&action.program.sources)
                    .chain(&action.program.runtime_inputs)
                    .cloned()
            })
            .collect()
    }
    pub fn downstream(&self, seeds: &BTreeSet<String>) -> BTreeSet<String> {
        let mut reached = seeds.clone();
        loop {
            let next = self
                .actions
                .iter()
                .filter(|(name, action)| {
                    !reached.contains(*name) && !action.dependencies.is_disjoint(&reached)
                })
                .map(|(name, _)| name.clone())
                .collect::<Vec<_>>();
            if next.is_empty() {
                return reached;
            }
            reached.extend(next);
        }
    }
    pub fn affected(&self, paths: &BTreeSet<String>) -> (BTreeSet<String>, BTreeSet<String>) {
        let known = paths.intersection(&self.known_files()).cloned().collect();
        let seeds = self
            .actions
            .iter()
            .filter(|(_, action)| {
                action
                    .generators
                    .iter()
                    .chain(&action.reads)
                    .chain(&action.optional)
                    .chain(&action.program.sources)
                    .chain(&action.program.runtime_inputs)
                    .any(|path| paths.contains(path))
            })
            .map(|(name, _)| name.clone())
            .collect();
        (self.downstream(&seeds), known)
    }
    pub fn select(&self, selectors: &[String]) -> Result<Selection> {
        let mut requested = BTreeSet::new();
        if selectors.is_empty() {
            requested = self.default_targets();
        }
        for selector in selectors {
            let key = selector
                .strip_prefix("//:")
                .or_else(|| selector.strip_prefix(':'))
                .unwrap_or(selector);
            if key == "everything" {
                requested.extend(self.default_targets());
                continue;
            }
            if self.actions.contains_key(key) {
                requested.insert(key.to_owned());
                continue;
            }
            let path = selector.strip_prefix("./").unwrap_or(selector);
            let paths = BTreeSet::from([path.to_owned()]);
            let (mut sources, _) = self.affected(&paths);
            if let Some(producer) = self.producers.get(path) {
                sources.extend(self.downstream(&BTreeSet::from([producer.clone()])));
            }
            ensure!(
                !sources.is_empty(),
                "no declared native target reads, writes or names {selector}"
            );
            requested.append(&mut sources);
        }
        let mut closure = BTreeSet::new();
        let mut order = Vec::new();
        let mut active = Vec::new();
        for name in &requested {
            self.visit(name, &mut closure, &mut active, &mut order)?;
        }
        Ok(Selection {
            requested,
            closure,
            order,
        })
    }
    fn visit(
        &self,
        name: &str,
        seen: &mut BTreeSet<String>,
        active: &mut Vec<String>,
        order: &mut Vec<String>,
    ) -> Result<()> {
        if let Some(at) = active.iter().position(|value| value == name) {
            let mut cycle = active[at..].to_vec();
            cycle.push(name.to_owned());
            bail!("native producer cycle: {}", cycle.join(" -> "));
        }
        if seen.contains(name) {
            return Ok(());
        }
        let action = self
            .actions
            .get(name)
            .with_context(|| format!("native producer {name} is absent from the plan"))?;
        active.push(name.to_owned());
        for dependency in &action.dependencies {
            self.visit(dependency, seen, active, order)?;
        }
        active.pop();
        seen.insert(name.to_owned());
        order.push(name.to_owned());
        Ok(())
    }
    pub fn runtime_inputs(&self, target: &str) -> Result<BTreeMap<String, RuntimeInput>> {
        let action = self
            .actions
            .get(target)
            .with_context(|| format!("unknown native target {target}"))?;
        let mut inputs = BTreeMap::new();
        for source in action.reads.iter().chain(&action.program.runtime_inputs) {
            if action.program.compiler_only(source) {
                continue;
            }
            inputs.insert(
                source.clone(),
                RuntimeInput {
                    producer: action
                        .producers
                        .get(source)
                        .filter(|producer| producer.as_str() != target)
                        .cloned(),
                    projection: action.support_inputs.get(source).cloned(),
                    optional: false,
                },
            );
        }
        for source in &action.optional {
            inputs
                .entry(source.clone())
                .or_insert_with(|| RuntimeInput {
                    optional: true,
                    ..RuntimeInput::default()
                });
        }
        Ok(inputs)
    }
}

pub fn inventory_config(root: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&fs::read(
        root.join("tools/hsm/build-plan/inventory.json"),
    )?)?)
}
pub fn publication_config(root: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&fs::read(
        root.join("tools/hsm/publication/config.json"),
    )?)?)
}
pub fn graph(root: &Path) -> Result<Value> {
    Ok(serde_json::from_slice(&fs::read(root.join(GRAPH_PATH))?)?)
}
pub fn load_inventory(root: &Path) -> Result<Vec<InventoryRow>> {
    let config = inventory_config(root)?;
    let files = inventory::tracked(root, &config, &publication_config(root)?)?;
    Ok(serde_json::from_value(inventory::inventory(
        root,
        &graph(root)?,
        files,
        &config,
    )?)?)
}
pub fn target_name(generator: &str, shared: &BTreeSet<String>) -> String {
    publication::target_name(generator, shared)
}
fn stem(generator: &str) -> String {
    Path::new(generator)
        .file_stem()
        .unwrap_or_default()
        .to_string_lossy()
        .trim_matches('_')
        .replace('_', "-")
}

// Declared JavaScript entrypoints retain their relative imports and package resolution metadata.
fn js_closure(root: &Path, reads: &BTreeSet<String>) -> Result<BTreeSet<String>> {
    let local = Regex::new(r#"(?:from|import|require)\s*\(?\s*["'](\.[^"']*)["']"#)?;
    let is_js = |source: &str| {
        [".js", ".mjs", ".cjs"]
            .iter()
            .any(|suffix| source.ends_with(suffix))
    };
    let mut pending = reads
        .iter()
        .filter(|source| is_js(source))
        .cloned()
        .collect::<Vec<_>>();
    let mut closure = BTreeSet::new();
    while let Some(source) = pending.pop() {
        if !closure.insert(source.clone()) {
            continue;
        }
        let mut directory = Path::new(&source).parent();
        while let Some(parent) = directory {
            let package = parent.join("package.json");
            if root.join(&package).is_file() {
                closure.insert(package.to_string_lossy().into_owned());
                let lock = parent.join("package-lock.json");
                if root.join(&lock).is_file() {
                    closure.insert(lock.to_string_lossy().into_owned());
                }
                break;
            }
            directory = parent.parent();
        }
        let Ok(text) = fs::read_to_string(root.join(&source)) else {
            continue;
        };
        for capture in local.captures_iter(&text) {
            let mut normalized = PathBuf::new();
            for part in Path::new(&source)
                .parent()
                .unwrap_or_else(|| Path::new(""))
                .join(&capture[1])
                .components()
            {
                match part {
                    Component::CurDir => (),
                    Component::ParentDir => {
                        ensure!(
                            normalized.pop(),
                            "JavaScript import escapes the checkout: {source}"
                        );
                    }
                    _ => normalized.push(part.as_os_str()),
                }
            }
            let mut candidates = vec![normalized.clone()];
            if normalized.extension().is_none() {
                candidates.extend([
                    normalized.with_extension("js"),
                    normalized.with_extension("mjs"),
                    normalized.join("index.js"),
                ]);
            }
            if let Some(path) = candidates
                .into_iter()
                .find(|path| root.join(path).is_file())
            {
                let path = path.to_string_lossy().into_owned();
                if is_js(&path) {
                    pending.push(path);
                } else {
                    closure.insert(path);
                }
            }
        }
    }
    Ok(closure)
}

/// Loading classifies one authored graph and keeps its native prerequisite closure intact.
pub fn action_plan(root: &Path, only: Option<&str>) -> Result<Plan> {
    let config = inventory_config(root)?;
    let files = inventory::tracked(root, &config, &publication_config(root)?)?;
    let inventory = serde_json::from_value(inventory::inventory(
        root,
        &graph(root)?,
        files.clone(),
        &config,
    )?)?;
    actions_from_inventory(root, inventory, files, only)
}

pub fn actions_from_inventory(
    root: &Path,
    mut inventory: Vec<InventoryRow>,
    files: BTreeSet<String>,
    only: Option<&str>,
) -> Result<Plan> {
    inventory.sort_by(|a, b| a.0.cmp(&b.0));
    let mut seen = BTreeSet::new();
    let mut shared = BTreeSet::new();
    for InventoryRow(generators, _) in &inventory {
        for generator in generators {
            let name = stem(generator);
            if !seen.insert(name.clone()) {
                shared.insert(name);
            }
        }
    }
    let mut names = BTreeMap::new();
    for InventoryRow(generators, _) in &inventory {
        names.insert(
            generators.clone(),
            target_name(
                generators.first().context("a generator cohort is empty")?,
                &shared,
            ),
        );
    }
    let mut producers = BTreeMap::new();
    let mut held = files;
    for InventoryRow(generators, made) in &inventory {
        held.extend(generators.iter().cloned());
        held.extend(made.solids.iter().cloned());
        held.extend(made.docs.iter().cloned());
        for path in made.solids.iter().chain(
            made.docs
                .iter()
                .filter(|path| path.ends_with(".png") || path.ends_with(".json")),
        ) {
            producers.insert(path.clone(), names[generators].clone());
        }
    }
    let mut actions = BTreeMap::new();
    for InventoryRow(generators, made) in &inventory {
        let name = names[generators].clone();
        let program = made
            .program
            .clone()
            .with_context(|| format!("{name} has no native program declaration"))?;
        let solids = made.solids.iter().cloned().collect::<BTreeSet<_>>();
        let optional = made
            .docs
            .iter()
            .filter(|path| path.ends_with(".png") || path.ends_with(".json"))
            .cloned()
            .collect::<BTreeSet<_>>();
        let mut reads = made
            .reads
            .iter()
            .chain(made.docs.iter())
            .chain(generators.iter())
            .chain(&program.sources)
            .chain(&program.runtime_inputs)
            .filter(|path| {
                !solids.contains(*path)
                    && !optional.contains(*path)
                    && !(path.ends_with(".step.mesh")
                        && path
                            .strip_suffix(".mesh")
                            .is_some_and(|base| solids.contains(base)))
            })
            .cloned()
            .collect::<BTreeSet<_>>();
        reads.retain(|path| held.contains(path));
        let closure = js_closure(root, &reads)?;
        reads.extend(closure);
        let dependencies = reads
            .iter()
            .filter_map(|path| producers.get(path))
            .filter(|producer| *producer != &name)
            .cloned()
            .collect();
        let support_inputs = reads
            .contains(GRAPH_PATH)
            .then(|| {
                BTreeMap::from([(
                    GRAPH_PATH.to_owned(),
                    GraphProjection {
                        generator: generators[0].clone(),
                    },
                )])
            })
            .unwrap_or_default();
        ensure!(
            !actions.contains_key(&name),
            "native target {name} names more than one producer cohort"
        );
        actions.insert(
            name,
            Action {
                generators: generators.clone(),
                solids: made.solids.clone(),
                docs: made.docs.clone(),
                reads: reads.iter().cloned().collect(),
                optional: optional.into_iter().collect(),
                producers: reads
                    .iter()
                    .filter_map(|path| {
                        producers
                            .get(path)
                            .map(|producer| (path.clone(), producer.clone()))
                    })
                    .collect(),
                dependencies,
                support_inputs,
                program,
            },
        );
    }
    let mut plan = Plan {
        actions,
        inventory,
        action_order: Vec::new(),
        producers,
    };
    let selectors = only
        .map(|selector| vec![selector.to_owned()])
        .unwrap_or_default();
    let selection = plan.select(&selectors)?;
    if only.is_some() {
        plan.actions
            .retain(|name, _| selection.closure.contains(name));
        plan.inventory
            .retain(|InventoryRow(generators, _)| selection.closure.contains(&names[generators]));
    }
    plan.action_order = selection.order;
    Ok(plan)
}

pub fn write_graph_projection(generator: &str, source: &Path, output: &Path) -> Result<()> {
    let projection = GraphProjection {
        generator: generator.to_owned(),
    };
    let bytes = projection.render_value(&serde_json::from_slice(&fs::read(source)?)?)?;
    if let Some(parent) = output.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(output, bytes)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    fn row(generator: &str, outputs: &[&str], reads: &[&str], docs: &[&str]) -> InventoryRow {
        serde_json::from_value(json!([[generator], {"solids":outputs,"docs":docs,"reads":reads,"program":{"crate":"fixture","name":"fixture","sources":[generator]}}])).unwrap()
    }
    fn fixture(rows: Vec<InventoryRow>, files: &[&str]) -> Plan {
        actions_from_inventory(
            Path::new("/absent-build-plan-fixture"),
            rows,
            files.iter().map(|path| (*path).to_owned()).collect(),
            None,
        )
        .unwrap()
    }
    #[test]
    fn targets_select_prerequisites_and_source_paths_select_downstream_once() {
        let plan = fixture(
            vec![
                row("hardware/frame/build.rs", &["frame.step"], &[], &[]),
                row(
                    "hardware/cover/build.rs",
                    &["cover.step"],
                    &["frame.step", "size.json"],
                    &[],
                ),
                row(
                    "hardware/machine.rs",
                    &["machine.step.mesh"],
                    &["cover.step"],
                    &[],
                ),
            ],
            &["size.json"],
        );
        let selected = plan.select(&["//:cover-build".into()]).unwrap();
        assert_eq!(
            selected.requested,
            BTreeSet::from(["cover-build".to_owned()])
        );
        assert_eq!(selected.order, ["frame-build", "cover-build"]);
        assert_eq!(
            plan.select(&["size.json".into()]).unwrap().order,
            ["frame-build", "cover-build", "machine"]
        );
        assert_eq!(plan.select(&[]).unwrap().closure, plan.default_targets());
        assert!(plan.select(&["unknown".into()]).is_err());
    }
    #[test]
    fn compiler_runtime_and_optional_authored_inputs_stay_distinct() {
        let source = "hardware/part.rs";
        let manifest = "tools/hsm/Cargo.toml";
        let lock = "tools/hsm/Cargo.lock";
        let parameters = "hardware/size.json";
        let mut declaration = row(
            source,
            &["hardware/part.step"],
            &[manifest, lock, parameters, "hardware/part.step.mesh"],
            &["hardware/guide.md", "hardware/guide.png"],
        );
        let program = declaration.1.program.as_mut().unwrap();
        program
            .sources
            .extend([manifest.to_owned(), lock.to_owned()]);
        program.runtime_inputs.insert(manifest.to_owned());
        let plan = fixture(
            vec![declaration],
            &[manifest, lock, parameters, "hardware/part.step.mesh"],
        );
        let inputs = plan.runtime_inputs("part").unwrap();
        assert!(!inputs.contains_key(source));
        assert!(!inputs.contains_key(lock));
        assert!(inputs.contains_key(manifest));
        assert!(inputs.contains_key(parameters));
        assert!(!inputs.contains_key("hardware/part.step.mesh"));
        assert!(!inputs["hardware/guide.md"].optional);
        assert!(inputs["hardware/guide.png"].optional);
    }
    #[test]
    fn generated_runtime_inputs_keep_exact_producer_identity() {
        let plan = fixture(
            vec![
                row("hardware/a.rs", &["left/part.step"], &[], &[]),
                row("hardware/b.rs", &["right/part.step"], &[], &[]),
                row("hardware/view.rs", &["view.step"], &["left/part.step"], &[]),
            ],
            &[],
        );
        assert_eq!(
            plan.runtime_inputs("view").unwrap()["left/part.step"]
                .producer
                .as_deref(),
            Some("a")
        );
        assert_eq!(
            plan.actions["view"].dependencies,
            BTreeSet::from(["a".to_owned()])
        );
    }
    #[test]
    fn native_cycle_names_the_dependency_ring() {
        let rows = vec![
            row("a.rs", &["a.step"], &["b.step"], &[]),
            row("b.rs", &["b.step"], &["a.step"], &[]),
        ];
        assert!(
            actions_from_inventory(
                Path::new("/absent-build-plan-fixture"),
                rows,
                BTreeSet::new(),
                None
            )
            .unwrap_err()
            .to_string()
            .contains("a -> b -> a")
        );
    }
    #[test]
    fn artifact_selection_matches_inventory() {
        let plan = fixture(
            vec![
                row("part.rs", &["part.step"], &[], &[]),
                row("notes.rs", &["notes.pdf"], &[], &[]),
            ],
            &[],
        );
        let expected = hsm_build_data::bookkeeping_affected::artifact_targets(
            &serde_json::to_value(&plan.inventory).unwrap(),
        );
        assert_eq!(
            plan.artifact_targets()
                .into_iter()
                .map(|name| format!("//:{name}"))
                .collect::<BTreeSet<_>>(),
            expected
        );
    }
    #[test]
    fn projection_ignores_other_writers_but_keeps_reader_classification() {
        let projection = GraphProjection {
            generator: "reader.rs".into(),
        };
        let mut graph = json!({"reader.rs":{"reads":["derived.json"],"writes":[],"rewritten":[]},"writer.rs":{"reads":[],"writes":["derived.json"],"rewritten":[]}});
        let before = projection.render_value(&graph).unwrap();
        graph["unrelated.rs"] = json!({"reads":[],"writes":["elsewhere.json"],"rewritten":[]});
        assert_eq!(projection.render_value(&graph).unwrap(), before);
        graph["writer.rs"]["writes"] = json!([]);
        assert_ne!(projection.render_value(&graph).unwrap(), before);
    }
    #[test]
    fn declared_javascript_keeps_relative_modules_and_package_metadata() {
        let root = std::env::temp_dir().join(format!(
            "hsm-plan-js-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir_all(root.join("tools/render")).unwrap();
        for (path, bytes) in [
            (
                "tools/render/browser.js",
                "import { x } from '../run-slots.mjs';\n",
            ),
            ("tools/run-slots.mjs", "import './run-runtime.mjs';\n"),
            ("tools/run-runtime.mjs", "export const x = 1;\n"),
            ("tools/render/package.json", "{\"type\":\"module\"}"),
            ("tools/render/package-lock.json", "{}"),
        ] {
            fs::write(root.join(path), bytes).unwrap();
        }
        let rows = vec![row(
            "hardware/part.rs",
            &["part.step"],
            &["tools/render/browser.js"],
            &[],
        )];
        let plan = actions_from_inventory(
            &root,
            rows,
            BTreeSet::from(["tools/render/browser.js".to_owned()]),
            None,
        )
        .unwrap();
        let inputs = plan.runtime_inputs("part").unwrap();
        for path in [
            "tools/render/browser.js",
            "tools/run-slots.mjs",
            "tools/run-runtime.mjs",
            "tools/render/package.json",
            "tools/render/package-lock.json",
        ] {
            assert!(inputs.contains_key(path), "missing runtime module {path}");
        }
        fs::remove_dir_all(root).unwrap();
    }
}
