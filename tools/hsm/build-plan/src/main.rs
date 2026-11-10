//! The build planner exposes native metadata, selective rules and explicit maintenance commands.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_plan::{affected, cleanup, planning, sync, trace};
use serde::Serialize;
use std::{env, fs, path::{Path, PathBuf}};

const HELP: &str = "hsm-build-plan [--root ROOT] COMMAND [OPTIONS]

write                       Write BUILD.bazel and checkout-local Bazel paths (default)
render [--only PRODUCER]     Print native BUILD rules without writing them
check                       Compare checked-out rules and local paths with the current plan
cycles                      Report whether declared producers wait on each other
inventory                   Print producer cohorts and classified inputs/outputs as JSON
actions [--only PRODUCER]    Print typed action metadata as JSON
dependency-rules            Print declared rule dependencies as JSON
rc-paths                    Print checkout-local Bazel path flags
project-graph-file GENERATOR INPUT OUTPUT
                            Write a stable reader-specific graph projection
trace-inputs [OPTIONS]       Trace native producers into the build graph
sync-tree [OPTIONS]          Carry completed Bazel outputs into the checkout
affected [OPTIONS]          Select geometry targets affected by source changes
failed-targets [OPTIONS]     List failed Bazel targets
drop-derived [OPTIONS]      Remove selected generated outputs

--only accepts a generator source path or target name. It prints the selected rules.
--check, --cycles and --project-graph remain aliases for the corresponding commands.
";

fn take_option(args: &mut Vec<String>, name: &str) -> Result<Option<String>> {
    let Some(at) = args.iter().position(|arg| arg == name || arg.starts_with(&format!("{name}="))) else { return Ok(None) };
    let option = args.remove(at);
    if let Some((_, value)) = option.split_once('=') { ensure!(!value.is_empty(), "{name} needs a value"); return Ok(Some(value.to_owned())); }
    ensure!(at < args.len(), "{name} needs a value");
    let value = args.remove(at); ensure!(!value.starts_with("--"), "{name} needs a value"); Ok(Some(value))
}

fn root_from(explicit: Option<String>) -> Result<PathBuf> {
    let path = explicit.map(PathBuf::from)
        .or_else(|| env::var_os("HSM_WORKSPACE").map(PathBuf::from))
        .unwrap_or_else(|| Path::new(env!("CARGO_MANIFEST_DIR")).join("../../.."));
    path.canonicalize().with_context(|| format!("repository root {}", path.display()))
}

fn json(value: &impl Serialize) -> Result<()> { println!("{}", serde_json::to_string_pretty(value)?); Ok(()) }

fn projection(args: &[String]) -> Result<()> {
    ensure!(args.len() == 3, "project-graph-file needs GENERATOR INPUT OUTPUT");
    planning::write_graph_projection(&args[0], Path::new(&args[1]), Path::new(&args[2]))
}

fn execute() -> Result<i32> {
    let mut args = env::args().skip(1).collect::<Vec<_>>();
    let explicit_root = take_option(&mut args, "--root")?;
    if args.first().is_some_and(|arg| arg == "--help" || arg == "-h") { print!("{HELP}"); return Ok(0) }
    let command = if args.first().is_some_and(|arg| !arg.starts_with('-') || ["--check", "--cycles", "--project-graph"].contains(&arg.as_str())) { args.remove(0) } else { "write".to_owned() };
    // A support action has only its graph input, so projection does not load checkout metadata.
    if command == "project-graph-file" || command == "--project-graph" { projection(&args)?; return Ok(0) }
    let root = root_from(explicit_root)?;
    match command.as_str() {
        "trace-inputs" => return trace::cli(&root, &args),
        "sync-tree" => return sync::cli(&root, &args),
        "affected" => return affected::cli(&root, &args),
        "failed-targets" => return cleanup::failed_cli(&root, &args),
        "drop-derived" => return cleanup::drop_cli(&root, &args),
        _ => (),
    }
    if args.iter().any(|arg| arg == "--help" || arg == "-h") { print!("{HELP}"); return Ok(0) }
    let only = take_option(&mut args, "--only")?;
    ensure!(args.is_empty(), "unrecognized arguments: {}", args.join(" "));
    match command.as_str() {
        "inventory" => json(&planning::load_inventory(&root)?)?,
        "actions" => json(&planning::action_plan(&root, only.as_deref())?.actions)?,
        "dependency-rules" => {
            let plan = planning::action_plan(&root, only.as_deref())?;
            json(&planning::dependency_rules_for_plan(&root, &plan)?)?;
        },
        "rc-paths" => print!("{}", planning::render_rc_paths(&root)?),
        "cycles" | "--cycles" => { planning::action_plan(&root, only.as_deref())?; println!("No producer cycles."); },
        "check" | "--check" => {
            ensure!(only.is_none(), "check compares the full plan; use render --only for a selected producer");
            let built = planning::render_build(&root, None)?;
            let mut changed = Vec::new();
            for (path, wanted) in [("BUILD.bazel", built.text), (".bazelrc.paths", planning::render_rc_paths(&root)?)] {
                if fs::read_to_string(root.join(path)).ok().as_deref() != Some(wanted.as_str()) { changed.push(path); }
            }
            if !changed.is_empty() { eprintln!("{} differ from the current native plan; run hsm-build-plan write", changed.join(" and ")); return Ok(1) }
            println!("Build rules and checkout paths match.");
        },
        "render" => print!("{}", planning::render_build(&root, only.as_deref())?.text),
        "write" if only.is_some() => print!("{}", planning::render_build(&root, only.as_deref())?.text),
        "write" => { let built = planning::write(&root, None)?; println!("Wrote BUILD.bazel and .bazelrc.paths for {} producers.", built.plan.actions.len()); },
        _ => bail!("unknown command {command}; use --help"),
    }
    Ok(0)
}

fn main() {
    match execute() {
        Ok(code) => std::process::exit(code),
        Err(error) => { eprintln!("hsm-build-plan: {error:#}"); std::process::exit(1) },
    }
}
