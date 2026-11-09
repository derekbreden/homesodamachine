//! A Rust step's rules: its program, compiled in a rule of its own from the checkout's `tools/hsm`
//! workspace, and the rule that runs the program to make the step's files. Neither runs Python.
//!
//! The program rule's sources are what cargo compiled into the program, so an edit to one
//! recompiles it, and the step reruns only when the program or a file it reads comes out
//! different. Both take the host's admission through its runner, and cargo the compiler lease.
use anyhow::{Context, Result};
use serde_json::Value;
use std::collections::BTreeSet;

/// The program a step runs: a `[[bin]]` of a crate under `tools/hsm`, and what it compiles from.
struct Program {
    krate: String,
    name: String,
    sources: BTreeSet<String>,
}

impl Program {
    fn from(value: &Value) -> Result<Self> {
        let text = |key: &str| value[key].as_str().map(str::to_owned).with_context(|| format!("a program's {key}"));
        let sources = value["sources"].as_array().context("a program's sources")?;
        Ok(Self {
            krate: text("crate")?,
            name: text("name")?,
            sources: sources.iter().filter_map(Value::as_str).map(str::to_owned).collect(),
        })
    }
}

/// The installed runner, or the checkout's own build of it: whichever matches the checkout's
/// runtime sources, the way `tools/run.py` chooses.
const RUNNER: [&str; 5] = [
    "hsm_run=",
    "for r in \"$$(awk -F'\"' '$$2 == \"runner\" {print $$4}' ~/.local/lib/hsm/runtime.json 2>/dev/null)\" \"$$HSM_WORKSPACE/tools/hsm/target/release/hsm-run\"; do",
    "  if [ -x \"$$r\" ] && \"$$r\" --runtime-info \"$$HSM_WORKSPACE\" 2>/dev/null | grep -q '\"source_match\":true'; then hsm_run=$$r; break; fi",
    "done",
    "if [ -z \"$$hsm_run\" ]; then echo \"no runner matches $$HSM_WORKSPACE; run the build through tools/run.py\" >&2; exit 1; fi",
];

/// cargo where rustup puts it, with the `rustc` beside it first on the PATH.
const CARGO: [&str; 4] = [
    "cargo=$$(command -v cargo || true)",
    "for c in \"$$cargo\" /opt/homebrew/opt/rustup/bin/cargo ~/.cargo/bin/cargo; do if [ -x \"$$c\" ]; then cargo=$$c; break; fi; done",
    "if [ ! -x \"$$cargo\" ]; then echo \"cargo is not installed (https://rustup.rs)\" >&2; exit 1; fi",
    "export HOME=~ PATH=\"$$(dirname \"$$cargo\"):$$PATH\"",
];

/// A value of the build plan as plain JSON: the plan hands its dicts, tuples and sets over tagged.
fn plain(value: &Value) -> Value {
    match value {
        Value::Array(items) => Value::Array(items.iter().map(plain).collect()),
        Value::Object(map) => match map.iter().next() {
            Some((tag, Value::Array(entries))) if map.len() == 1 && tag == "$dict" => Value::Object(
                entries
                    .iter()
                    .filter_map(|entry| Some((entry.get(0)?.as_str()?.to_owned(), plain(entry.get(1)?))))
                    .collect(),
            ),
            Some((tag, Value::Array(items))) if map.len() == 1 && ["$tuple", "$set", "$frozenset"].contains(&tag.as_str()) => {
                Value::Array(items.iter().map(plain).collect())
            }
            Some((tag, path)) if map.len() == 1 && tag == "$path" => path.clone(),
            _ => Value::Object(map.iter().map(|(key, item)| (key.clone(), plain(item))).collect()),
        },
        other => other.clone(),
    }
}

/// The step's rules, when its declaration names a program: the program's, then the step's own.
/// `made` is each output as the program writes it, in the order of the declaration's `outs`.
pub fn render(name: &str, declaration: &Value, made: &[String], copy_files: &[String]) -> Result<Option<String>> {
    let declaration = &plain(declaration);
    let Some(program) = declaration.get("program").filter(|p| !p.is_null()) else { return Ok(None) };
    let program = Program::from(program)?;
    let outs: Vec<&str> = declaration["outs"].as_array().context("a step's outs")?.iter().filter_map(Value::as_str).collect();
    anyhow::ensure!(outs.len() == made.len(), "{name} declares {} outputs and makes {}", outs.len(), made.len());
    let built = format!("out/{name}-program/{}", program.name);
    let mut text = String::new();
    // A source another rule makes, such as the workspace's cargo-config.json, by that rule's
    // label, as the step's own srcs name it.
    let srcs: Vec<&str> = declaration["srcs"].as_array().context("a step's srcs")?.iter().filter_map(Value::as_str).collect();
    let path_of = |label: &str| -> Option<String> {
        label.strip_prefix(":out/").and_then(|rest| rest.split_once('/')).map(|(_, path)| path.to_owned())
    };
    let label_of = |source: &str| -> String {
        srcs.iter().find(|s| path_of(s).as_deref() == Some(source)).map(|s| (*s).to_owned()).unwrap_or_else(|| source.to_owned())
    };

    // The program: compiled where the checkout's other programs are, so a recipe edit
    // recompiles only the crates it reaches.
    text += &format!("genrule(\n    name = \"{name}-program\",\n    srcs = [\n");
    for source in &program.sources {
        text += &format!("        \"{}\",\n", label_of(source));
    }
    text += &format!("    ],\n    outs = [\"{built}\"],\n    tags = [\"no-sandbox\"],\n    cmd = \"\"\"\nset -e\n");
    for line in copy_files.iter().map(String::as_str).chain(RUNNER).chain(CARGO) {
        text += line;
        text += "\n";
    }
    text += &format!("O0=$$PWD/$(location {built})\n");
    text += "cd \"$$HSM_WORKSPACE/tools/hsm\"\n";
    text += &format!(
        "CARGO_TARGET_DIR=\"$$PWD/target\" \"$$hsm_run\" -- \"$$cargo\" build --release --locked --quiet --manifest-path {}/Cargo.toml --bin {}\n",
        program.krate, program.name
    );
    text += &format!("copy_file target/release/{} \"$$O0\"\n\"\"\",\n)\n\n", program.name);

    // The step: the program, run where only what it declared stands at its repository path. The
    // code it was compiled from stays out; data it was compiled with stays in, since it may also
    // read that data where it runs.
    let code = |source: &str| {
        source.ends_with(".rs") || ["Cargo.toml", "Cargo.lock", "cargo-config.json"].iter().any(|m| source.ends_with(m))
    };
    let compiled = |source: &str| program.sources.contains(source) && code(source);
    let sources: BTreeSet<&str> = srcs
        .iter()
        .copied()
        .filter(|source| !compiled(source))
        .filter(|source| path_of(source).is_none_or(|path| !compiled(&path)))
        .collect();
    text += &format!("genrule(\n    name = \"{name}\",\n    srcs = [\n        \":{built}\",\n");
    for source in &sources {
        text += &format!("        \"{source}\",\n");
    }
    text += "    ],\n    outs = [\n";
    for out in &outs {
        text += &format!("        \"{out}\",\n");
    }
    text += "    ],\n    cmd = \"\"\"\nset -e\n";
    for line in copy_files.iter().map(String::as_str).chain(RUNNER) {
        text += line;
        text += "\n";
    }
    for (i, out) in outs.iter().enumerate() {
        text += &format!("O{i}=$$PWD/$(location {out})\n");
    }
    text += "rm -rf work\nfor f in $(SRCS); do\n  case $$f in\n    */bin/out/*/*) t=$${f#*/bin/out/}; t=$${t#*/};;\n    *) t=$$f;;\n  esac\n";
    text += "  mkdir -p \"work/$$(dirname \"$$t\")\"; copy_file -L \"$$f\" \"work/$$t\"\ndone\ncd work\n";
    text += &format!("\"$$hsm_run\" -- ./{} > /dev/null\n", program.name);
    for (i, file) in made.iter().enumerate() {
        text += &format!("copy_file {file} \"$$O{i}\"\n");
    }
    text += "\"\"\",\n)";
    Ok(Some(text))
}

#[cfg(test)]
mod tests {
    use super::render;
    use serde_json::{Value, json};
    use std::collections::BTreeSet;

    fn inputs(text: &str, name: &str) -> BTreeSet<String> {
        let start = text.find(&format!("    name = \"{name}\",\n")).unwrap();
        let rule = &text[start..];
        let start = rule.find("    srcs = [\n").unwrap() + "    srcs = [\n".len();
        let end = rule[start..].find("    ],\n").unwrap() + start;
        rule[start..end].lines().map(|line| line.trim().trim_matches(',').trim_matches('"').to_owned()).collect()
    }

    fn rules(srcs: Value, sources: Value) -> String {
        render("machine", &json!({
            "program": {"crate":"installed-machine", "name":"installed-machine", "sources":sources},
            "srcs":srcs,
            "outs":["out/machine/hardware/manifold-layout/enclosure-assembly.step.mesh"],
        }), &["hardware/manifold-layout/enclosure-assembly.step.mesh".into()], &[]).unwrap().unwrap()
    }

    #[test]
    fn runtime_parameters_invalidate_the_producer_without_reaching_the_compiler() {
        let source = "hardware/manifold-layout/installed_machine.rs";
        let manifest = "tools/hsm/installed-machine/Cargo.toml";
        let data = [
            "hardware/manifold-layout/above-core.json",
            "hardware/manifold-layout/junctions.json",
            "hardware/manifold-layout/enclosure-box.json",
        ];
        let srcs: Vec<_> = [source, manifest].into_iter().chain(data).collect();
        let text = rules(json!(srcs), json!([source, manifest]));
        assert_eq!(inputs(&text, "machine-program"), [source, manifest].map(str::to_owned).into_iter().collect());
        assert_eq!(inputs(&text, "machine"), [":out/machine-program/installed-machine"].into_iter().chain(data).map(str::to_owned).collect());
    }

    #[test]
    fn generated_runtime_parameters_do_not_add_their_producer_to_the_compiler() {
        let source = "hardware/manifold-layout/installed_machine.rs";
        let runtime = ":out/enclosure-box/hardware/manifold-layout/enclosure-box.json";
        let text = rules(json!([source, runtime]), json!([source]));
        assert_eq!(inputs(&text, "machine-program"), [source.to_owned()].into_iter().collect());
        assert!(inputs(&text, "machine").contains(runtime));
    }

    #[test]
    fn data_compiled_with_include_str_remains_a_compiler_input() {
        let source = "hardware/manifold-layout/installed_machine.rs";
        let data = "tools/hsm/shared-data/catalog/materials.json";
        let provider = ":out/catalog/tools/hsm/shared-data/catalog/materials.json";
        let text = rules(json!([source, provider]), json!([source, data]));
        assert_eq!(inputs(&text, "machine-program"), [source, provider].map(str::to_owned).into_iter().collect());
        assert!(inputs(&text, "machine").contains(provider));
    }
}
