//! The native planner exposes producer selection, source attribution and explicit maintenance commands.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_plan::{affected, cleanup, planning, sync, trace};
use serde::Serialize;
use std::{
    collections::BTreeMap,
    env,
    path::{Path, PathBuf},
};

const HELP:&str="hsm-build-plan [--root ROOT] COMMAND [OPTIONS]

plan [SELECTORS...]          Print selected native actions, prerequisites and staged runtime inputs (default)
actions [SELECTORS...]       Print selected action declarations as JSON
inventory                   Print producer cohorts and classified inputs/outputs as JSON
cycles                      Report whether declared producers wait on each other
project-graph-file GENERATOR INPUT OUTPUT
                            Write a stable reader-specific graph projection
trace-inputs [OPTIONS]       Trace native producers into the authored graph
affected [OPTIONS]           Select native targets affected by changed sources
sync-tree [OPTIONS]          Reread a native receipt or stage derived Git changes
failed-targets FILE          Read unavailable targets from a native receipt
drop-derived [OPTIONS]       Name or restore generated exports

Selectors name native targets, producer source files or declared input paths.
Empty selection and everything select the normal print graph. //:target and :target are aliases.
";

fn take_root(args: &mut Vec<String>) -> Result<Option<PathBuf>> {
    let Some(at) = args
        .iter()
        .position(|argument| argument == "--root" || argument.starts_with("--root="))
    else {
        return Ok(None);
    };
    let option = args.remove(at);
    if let Some((_, value)) = option.split_once('=') {
        ensure!(!value.is_empty(), "--root requires a path");
        return Ok(Some(value.into()));
    }
    ensure!(at < args.len(), "--root requires a path");
    let value = args.remove(at);
    ensure!(!value.starts_with("--"), "--root requires a path");
    Ok(Some(value.into()))
}
fn root_from(explicit: Option<PathBuf>) -> Result<PathBuf> {
    let root = explicit
        .or_else(|| env::var_os("HSM_WORKSPACE").map(PathBuf::from))
        .unwrap_or_else(|| Path::new(env!("CARGO_MANIFEST_DIR")).join("../../.."));
    root.canonicalize()
        .with_context(|| format!("repository root {}", root.display()))
}
fn json(value: &impl Serialize) -> Result<()> {
    println!("{}", serde_json::to_string_pretty(value)?);
    Ok(())
}

fn execute() -> Result<i32> {
    let mut args = env::args().skip(1).collect::<Vec<_>>();
    let explicit_root = take_root(&mut args)?;
    if args
        .first()
        .is_some_and(|argument| ["--help", "-h"].contains(&argument.as_str()))
    {
        print!("{HELP}");
        return Ok(0);
    }
    let command = if args.is_empty() {
        "plan".to_owned()
    } else {
        args.remove(0)
    };
    if command == "project-graph-file" {
        ensure!(
            args.len() == 3,
            "project-graph-file requires GENERATOR INPUT OUTPUT"
        );
        planning::write_graph_projection(&args[0], Path::new(&args[1]), Path::new(&args[2]))?;
        return Ok(0);
    }
    let root = root_from(explicit_root)?;
    match command.as_str() {
        "trace-inputs" => return trace::cli(&root, &args),
        "affected" => return affected::cli(&root, &args),
        "sync-tree" => return sync::cli(&root, &args),
        "failed-targets" => return cleanup::failed_cli(&root, &args),
        "drop-derived" => return cleanup::drop_cli(&root, &args),
        _ => (),
    }
    if args
        .iter()
        .any(|argument| ["--help", "-h"].contains(&argument.as_str()))
    {
        print!("{HELP}");
        return Ok(0);
    }
    if args.first().is_some_and(|argument| argument == "--") {
        args.remove(0);
    }
    ensure!(
        !args.iter().any(|argument| argument.starts_with('-')),
        "selectors cannot contain command options"
    );
    match command.as_str() {
        "inventory" => {
            ensure!(args.is_empty(), "inventory takes no selectors");
            json(&planning::load_inventory(&root)?)?;
        }
        "cycles" => {
            ensure!(args.is_empty(), "cycles takes no selectors");
            planning::action_plan(&root, None)?;
            println!("No native producer cycles.");
        }
        "plan" | "actions" => {
            let plan = planning::action_plan(&root, None)?;
            let selection = plan.select(&args)?;
            let actions = selection
                .order
                .iter()
                .map(|name| (name.clone(), &plan.actions[name]))
                .collect::<BTreeMap<_, _>>();
            if command == "actions" {
                json(&actions)?;
            } else {
                let runtime_inputs = selection
                    .order
                    .iter()
                    .map(|name| Ok((name.clone(), plan.runtime_inputs(name)?)))
                    .collect::<Result<BTreeMap<_, _>>>()?;
                json(
                    &serde_json::json!({"selection":selection,"actions":actions,"runtime_inputs":runtime_inputs}),
                )?;
            }
        }
        _ => bail!("unknown command {command}; use --help"),
    }
    Ok(0)
}
fn main() {
    match execute() {
        Ok(code) => std::process::exit(code),
        Err(error) => {
            eprintln!("hsm-build-plan: {error:#}");
            std::process::exit(1)
        }
    }
}
