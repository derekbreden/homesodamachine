//! Native rule rendering separates compiled recipe sources from the data read by each producer.
use crate::planning::{Program, Rule, shell_quote};
use anyhow::{Context, Result, ensure};
use std::collections::{BTreeMap, BTreeSet};

// Copying keeps the host's clone-on-write path while retaining ordinary copy semantics.
const COPY_FILES: &str = r#"case "$$(uname -s)" in
  Darwin)
    copy_mask=$$((8#$$(umask)))
    copy_bits=("" x w wx r rx rw rwx)
    copy_mode="u-$${copy_bits[$$((copy_mask >> 6 & 7))]},g-$${copy_bits[$$((copy_mask >> 3 & 7))]},o-$${copy_bits[$$((copy_mask & 7))]}"
    copy_file() {
      local copy_dest="$${!#}" copy_target copy_permissions="$$copy_mode"
      if [ -e "$$copy_dest" ] || [ -L "$$copy_dest" ]; then
        if [ ! -f "$$copy_dest" ] || [ -L "$$copy_dest" ]; then cp "$$@"; return; fi
        copy_permissions=$$(stat -f %Lp "$$copy_dest")
        copy_target=$$(mktemp "$$copy_dest.hsm-copy.XXXXXX")
      else copy_target="$$copy_dest"; fi
      if cp -c "$${@:1:$$(( $$# - 1 ))}" "$$copy_target" 2>/dev/null; then
        chmod "$$copy_permissions" "$$copy_target"
        touch "$$copy_target"
        if [ "$$copy_target" != "$$copy_dest" ]; then mv -f "$$copy_target" "$$copy_dest"; fi
      else rm -f "$$copy_target"; cp "$$@"; fi
    };;
  *) copy_file() { cp "$$@"; };;
esac
"#;

// The action uses the runner whose sources match its host checkout and inherited lease.
const RUNNER: &str = r#"hsm_run=
for r in "$$(awk -F'"' '$$2 == "runner" {print $$4}' ~/.local/lib/hsm/runtime.json 2>/dev/null)" "$$HSM_WORKSPACE/tools/hsm/target/release/hsm-run"; do
  if [ -x "$$r" ] && "$$r" --runtime-info "$$HSM_WORKSPACE" 2>/dev/null | grep -q '"source_match":true'; then hsm_run=$$r; break; fi
done
if [ -z "$$hsm_run" ]; then echo "no runner matches $$HSM_WORKSPACE; run the build through tools/run" >&2; exit 1; fi
"#;

// Cargo discovery retains rustup's matching compiler on the action's PATH.
const CARGO: &str = r#"cargo=$$(command -v cargo || true)
for c in "$$cargo" /opt/homebrew/opt/rustup/bin/cargo ~/.cargo/bin/cargo; do if [ -x "$$c" ]; then cargo=$$c; break; fi; done
if [ ! -x "$$cargo" ]; then echo "cargo is not installed (https://rustup.rs)" >&2; exit 1; fi
export PATH="$$(dirname "$$cargo"):$$PATH"
"#;

fn path_of(label: &str) -> Option<&str> {
    label.strip_prefix(":out/").and_then(|rest| rest.split_once('/')).map(|(_, path)| path)
}

fn source_label(source: &str, srcs: &[String]) -> String {
    srcs.iter().find(|label| path_of(label) == Some(source)).cloned().unwrap_or_else(|| source.to_owned())
}

fn quoted(value: &str) -> String { serde_json::to_string(value).expect("text serialization") }

pub fn program_output(name: &str, program: &Program) -> String { format!("out/{name}-program/{}", program.name) }

/// A program rule compiles declared recipe inputs through the shared host runner.
pub fn program_rule(name: &str, program: &Program, srcs: &[String]) -> Result<String> {
    ensure!(!program.krate.is_empty() && !program.name.is_empty(), "{name} has an incomplete native program declaration");
    let built = program_output(name, program);
    let mut text = format!("genrule(\n    name = \"{name}-program\",\n    srcs = [\n");
    for source in &program.sources { text += &format!("        {},\n", quoted(&source_label(source, srcs))); }
    text += &format!("    ],\n    outs = [{}],\n    tags = [\"no-sandbox\"],\n    cmd = \"\"\"\nset -e\n", quoted(&built));
    text += COPY_FILES; text += RUNNER; text += CARGO;
    text += &format!("O0=$$PWD/$(location {built})\ncd \"$$HSM_WORKSPACE/tools/hsm\"\n");
    text += &format!("CARGO_TARGET_DIR=\"$$PWD/target\" \"$$hsm_run\" -- \"$$cargo\" build --release --locked --quiet -j 2 --manifest-path {} --bin {}\n", shell_quote(&format!("{}/Cargo.toml", program.krate)), shell_quote(&program.name));
    text += &format!("copy_file {} \"$$O0\"\n\"\"\",\n)", shell_quote(&format!("target/release/{}", program.name)));
    Ok(text)
}

fn runtime_sources<'a>(declaration: &'a Rule, program: &Program) -> BTreeSet<&'a str> {
    let code = |source: &str| source.ends_with(".rs") || ["Cargo.toml", "Cargo.lock", "cargo-config.json"].iter().any(|name| source.ends_with(name));
    let compiled = |source: &str| program.sources.contains(source) && code(source) && !program.runtime_inputs.contains(source);
    declaration.srcs.iter().map(String::as_str).filter(|source| !compiled(path_of(source).unwrap_or(source))).collect()
}

/// A producer runs in a staged repository containing its declared runtime data.
pub fn render(name: &str, declaration: &Rule, made: &[String], support: &BTreeMap<String, String>) -> Result<String> {
    let program = declaration.program.as_ref().context("a native action's program")?;
    ensure!(declaration.outs.len() == made.len(), "{name} declares {} outputs and makes {}", declaration.outs.len(), made.len());
    let built = program_output(name, program);
    let mut text = program_rule(name, program, &declaration.srcs)?;
    let sources = runtime_sources(declaration, program);
    text += &format!("\n\ngenrule(\n    name = \"{name}\",\n    srcs = [\n        \":{built}\",\n");
    for source in sources { text += &format!("        {},\n", quoted(source)); }
    text += "    ],\n    outs = [\n";
    for out in &declaration.outs { text += &format!("        {},\n", quoted(out)); }
    text += "    ],\n    cmd = \"\"\"\nset -e\n"; text += COPY_FILES; text += RUNNER;
    for (i, out) in declaration.outs.iter().enumerate() { text += &format!("O{i}=$$PWD/$(location {out})\n"); }
    text += "rm -rf work\nfor f in $(SRCS); do\n  case $$f in\n    */node_modules/*) continue;;\n";
    for (source, output) in support { text += &format!("    */bin/{output}) t={};;\n", shell_quote(source)); }
    text += "    */bin/out/*/*) t=$${f#*/bin/out/}; t=$${t#*/};;\n    *) t=$$f;;\n  esac\n  mkdir -p \"work/$$(dirname \"$$t\")\"; copy_file -L \"$$f\" \"work/$$t\"\ndone\n";
    text += "for d in tools/render/node_modules web/node_modules hardware/pcb/pcba/node_modules; do\n  if [ -d \"$$d\" ]; then mkdir -p \"work/$$(dirname \"$$d\")\"; ln -sfn \"$$PWD/$$d\" \"work/$$d\"; fi\ndone\ncd work\n";
    text += &format!("HSM_REPO_ROOT=$$PWD \"$$hsm_run\" -- {} > /dev/null\n", shell_quote(&format!("./{}", program.name)));
    for (i, file) in made.iter().enumerate() { text += &format!("copy_file {} \"$$O{i}\"\n", shell_quote(file)); }
    text += "\"\"\",\n)";
    Ok(text)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::planning::RuleKind;

    fn inputs(text: &str, name: &str) -> BTreeSet<String> {
        let rule = &text[text.find(&format!("    name = \"{name}\",\n")).unwrap()..];
        let start = rule.find("    srcs = [\n").unwrap() + "    srcs = [\n".len();
        let end = rule[start..].find("    ],\n").unwrap() + start;
        rule[start..end].lines().map(|line| line.trim().trim_matches(',').trim_matches('"').to_owned()).collect()
    }

    fn rules(srcs: &[&str], sources: &[&str], runtime: &[&str]) -> String {
        let output = "hardware/manifold-layout/enclosure-assembly.step.mesh";
        let declaration = Rule { kind: RuleKind::Action, srcs: srcs.iter().map(|s| (*s).into()).collect(), outs: vec![format!("out/machine/{output}")], tools: vec![], globs: vec![], generator: None,
            program: Some(Program { krate: "installed-machine".into(), name: "installed-machine".into(), sources: sources.iter().map(|s| (*s).into()).collect(), runtime_inputs: runtime.iter().map(|s| (*s).into()).collect() }) };
        render("machine", &declaration, &[output.into()], &BTreeMap::new()).unwrap()
    }

    #[test]
    fn runtime_parameters_do_not_reach_the_compiler() {
        let source = "hardware/manifold-layout/installed_machine.rs";
        let manifest = "tools/hsm/installed-machine/Cargo.toml";
        let data = "hardware/manifold-layout/above-core.json";
        let text = rules(&[source, manifest, data], &[source, manifest], &[]);
        assert_eq!(inputs(&text, "machine-program"), [source, manifest].map(str::to_owned).into_iter().collect());
        assert_eq!(inputs(&text, "machine"), [":out/machine-program/installed-machine", data].map(str::to_owned).into_iter().collect());
        assert!(text.contains("HSM_REPO_ROOT=$$PWD"));
        assert!(text.contains("--quiet -j 2"));
    }

    #[test]
    fn generated_runtime_data_does_not_add_its_producer_to_the_compiler() {
        let source = "hardware/manifold-layout/installed_machine.rs";
        let runtime = ":out/enclosure-box/hardware/manifold-layout/enclosure-box.json";
        let text = rules(&[source, runtime], &[source], &[]);
        assert_eq!(inputs(&text, "machine-program"), [source.to_owned()].into_iter().collect());
        assert!(inputs(&text, "machine").contains(runtime));
    }

    #[test]
    fn include_str_data_remains_both_compiler_and_runtime_input() {
        let source = "hardware/manifold-layout/installed_machine.rs";
        let data = "tools/hsm/shared-data/catalog/materials.json";
        let provider = ":out/catalog/tools/hsm/shared-data/catalog/materials.json";
        let text = rules(&[source, provider], &[source, data], &[]);
        assert_eq!(inputs(&text, "machine-program"), [source, provider].map(str::to_owned).into_iter().collect());
        assert!(inputs(&text, "machine").contains(provider));
    }

    #[test]
    fn explicit_runtime_manifest_survives_compiler_input_filter() {
        let manifest = "tools/hsm/Cargo.toml";
        let lock = "tools/hsm/Cargo.lock";
        let text = rules(&[manifest, lock], &[manifest, lock], &[manifest, lock]);
        assert!(inputs(&text, "machine").contains(manifest));
        assert!(inputs(&text, "machine").contains(lock));
    }
}
