//! Explicit native receipt carrying preserves authored text and the publisher's model cohort.
use crate::{
    planning::{self, Plan},
    receipt::RunReceipt,
};
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::bookkeeping_sync::{self, CarryRequest, CarryResult};
use serde_json::Value;
use std::{
    collections::BTreeSet,
    fs,
    io::Write,
    path::{Component, Path, PathBuf},
    process::{Command, Stdio},
};

#[derive(Debug, Default)]
pub struct CarryOptions {
    pub selectors: Vec<String>,
    pub write: bool,
    pub runtime_only: bool,
    pub derived_only: bool,
}

/// Receipt status supplies producer identity before any output path enters the carrier.
pub fn receipt_pairs(
    plan: &Plan,
    receipt: &RunReceipt,
    selectors: &[String],
) -> Result<Vec<(PathBuf, String)>> {
    ensure!(
        receipt.schema == 1,
        "unsupported native receipt schema {}",
        receipt.schema
    );
    let selected = plan.select(selectors)?.closure;
    let mut destinations = BTreeSet::new();
    let mut pairs = Vec::new();
    for (name, result) in &receipt.targets {
        if !selected.contains(name) || !result.status.usable() {
            continue;
        }
        let action = &plan.actions[name];
        let declared = action.outputs().collect::<BTreeSet<_>>();
        for (destination, source) in &result.outputs {
            ensure!(
                declared.contains(destination.as_str()),
                "native receipt target {name} does not declare {destination}"
            );
            ensure!(
                !Path::new(destination).components().any(|part| matches!(
                    part,
                    Component::ParentDir | Component::RootDir | Component::Prefix(_)
                )),
                "native output leaves the checkout: {destination}"
            );
            ensure!(
                source.is_absolute(),
                "native receipt output source must be absolute: {}",
                source.display()
            );
            ensure!(
                destinations.insert(destination.clone()),
                "native receipt repeats destination {destination}"
            );
            pairs.push((source.clone(), destination.clone()));
        }
    }
    Ok(pairs)
}

pub fn carry(
    root: &Path,
    plan: &Plan,
    receipt: &RunReceipt,
    options: &CarryOptions,
) -> Result<CarryResult> {
    ensure!(
        !(options.runtime_only && options.derived_only),
        "choose runtime-only or derived-only"
    );
    let request = CarryRequest {
        root: root.to_owned(),
        pairs: receipt_pairs(plan, receipt, &options.selectors)?,
        write: options.write,
        runtime_only: options.runtime_only,
        derived_only: options.derived_only,
        config: planning::inventory_config(root)?,
        rewritten: plan
            .actions
            .values()
            .flat_map(|action| action.docs.iter().cloned())
            .collect(),
        ..CarryRequest::default()
    };
    bookkeeping_sync::carry_request(&request)
}

fn change(root: &Path, command: &[&str], paths: &[Vec<u8>]) -> Result<()> {
    if paths.is_empty() {
        return Ok(());
    }
    let mut child = Command::new("git")
        .arg("-C")
        .arg(root)
        .arg("--literal-pathspecs")
        .args(command)
        .args(["--pathspec-from-file=-", "--pathspec-file-nul"])
        .stdin(Stdio::piped())
        .spawn()?;
    let mut input = child.stdin.take().context("git pathspec input")?;
    for path in paths {
        input.write_all(path)?;
        input.write_all(&[0])?;
    }
    drop(input);
    ensure!(child.wait()?.success(), "git {} failed", command.join(" "));
    Ok(())
}

fn stage_destinations(plan: &Plan, receipt: Option<&RunReceipt>) -> Result<BTreeSet<String>> {
    if let Some(receipt) = receipt {
        Ok(receipt_pairs(plan, receipt, &[])?
            .into_iter()
            .map(|(_, destination)| destination)
            .collect())
    } else {
        Ok(plan
            .actions
            .values()
            .flat_map(|action| action.outputs().map(str::to_owned))
            .collect())
    }
}

fn restrict_staging(
    selected: &mut bookkeeping_sync::StageSelection,
    allowed: &BTreeSet<String>,
) -> usize {
    let before = selected.paths.len();
    selected
        .paths
        .retain(|path| std::str::from_utf8(path).is_ok_and(|path| allowed.contains(path)));
    before - selected.paths.len()
}

fn stage(root: &Path, config: &Value, plan: &Plan, receipt: Option<&RunReceipt>) -> Result<i32> {
    let status = Command::new("git")
        .arg("-C")
        .arg(root)
        .args([
            "-c",
            "status.renames=false",
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ])
        .output()?;
    ensure!(
        status.status.success(),
        "git status: {}",
        String::from_utf8_lossy(&status.stderr)
    );
    let mut selected = bookkeeping_sync::stage_selection(&status.stdout, config);
    let outside = restrict_staging(&mut selected, &stage_destinations(plan, receipt)?);
    change(root, &["restore", "--staged"], &selected.staged)?;
    change(root, &["add", "-A"], &selected.paths)?;
    change(
        root,
        &["restore", "--worktree", "--source=HEAD"],
        &selected.tracked,
    )?;
    println!(
        "{} derived path(s) staged; {} publisher-owned and {} authored or unselected path(s) left out",
        selected.paths.len(),
        selected.held.len(),
        outside
    );
    Ok(0)
}

pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut options = CarryOptions::default();
    let mut receipt_path = None;
    let mut do_stage = false;
    let mut at = 0;
    while at < args.len() {
        match args[at].as_str() {
            "--write" => options.write = true,
            "--solids-only" | "--runtime-only" => options.runtime_only = true,
            "--derived-only" => options.derived_only = true,
            "--stage" => do_stage = true,
            flag @ ("--receipt" | "--targets") => {
                at += 1;
                let value = args
                    .get(at)
                    .with_context(|| format!("{flag} requires a value"))?;
                if flag == "--receipt" {
                    receipt_path = Some(root.join(value));
                } else {
                    options.selectors.extend(
                        value
                            .split(|character: char| character.is_whitespace() || character == ',')
                            .filter(|value| !value.is_empty())
                            .map(str::to_owned),
                    );
                }
            }
            "--help" | "-h" => {
                println!(
                    "Compare or carry declared exports from an explicit native run receipt.\n\nUsage: hsm-build-plan sync-tree --receipt FILE [--write] [--targets TARGETS] [--runtime-only | --derived-only]\n       hsm-build-plan sync-tree --derived-only --stage [--receipt FILE]\nThe print executor carries current results progressively; this command rereads the named receipt. Receipt-scoped staging admits only declared outputs of usable targets."
                );
                return Ok(0);
            }
            option => bail!("unknown sync option {option}"),
        }
        at += 1;
    }
    let receipt: Option<RunReceipt> = match &receipt_path {
        Some(path) => Some(serde_json::from_slice(
            &fs::read(path).with_context(|| format!("read native receipt {}", path.display()))?,
        )?),
        None => None,
    };
    if do_stage {
        ensure!(
            options.derived_only
                && !options.write
                && !options.runtime_only
                && options.selectors.is_empty(),
            "--stage is used only with --derived-only"
        );
        return stage(
            root,
            &planning::inventory_config(root)?,
            &planning::action_plan(root, None)?,
            receipt.as_ref(),
        );
    }
    let receipt=receipt.context("sync-tree requires --receipt FILE; the native executor already carries its completed outputs")?;
    let result = carry(
        root,
        &planning::action_plan(root, None)?,
        &receipt,
        &options,
    )?;
    print!("{}", result.output);
    Ok(result.status.unwrap_or(0))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        planning::{InventoryRow, actions_from_inventory},
        receipt::{TargetReceipt, TargetStatus},
    };
    use serde_json::json;
    use std::collections::BTreeMap;
    fn plan() -> Plan {
        let rows:Vec<InventoryRow>=serde_json::from_value(json!([[ ["part.rs"],{"solids":["part.step","part.stl"],"docs":[],"reads":[],"program":{"crate":"part","name":"part","sources":["part.rs"]}} ],[ ["bad.rs"],{"solids":["bad.step"],"docs":[],"reads":[],"program":{"crate":"bad","name":"bad","sources":["bad.rs"]}} ]])).unwrap();
        actions_from_inventory(Path::new("/fixture"), rows, BTreeSet::new(), None).unwrap()
    }
    #[test]
    fn shared_blob_keeps_each_destination_and_failed_producers_never_carry() {
        let receipt = RunReceipt {
            targets: BTreeMap::from([
                (
                    "part".into(),
                    TargetReceipt {
                        status: TargetStatus::Cached,
                        outputs: BTreeMap::from([
                            ("part.step".into(), "/cache/shared".into()),
                            ("part.stl".into(), "/cache/shared".into()),
                        ]),
                        ..TargetReceipt::default()
                    },
                ),
                (
                    "bad".into(),
                    TargetReceipt {
                        status: TargetStatus::Failed,
                        outputs: BTreeMap::from([("bad.step".into(), "/cache/bad".into())]),
                        ..TargetReceipt::default()
                    },
                ),
            ]),
            ..RunReceipt::default()
        };
        assert_eq!(
            receipt_pairs(&plan(), &receipt, &[]).unwrap(),
            vec![
                ("/cache/shared".into(), "part.step".into()),
                ("/cache/shared".into(), "part.stl".into())
            ]
        );
    }
    #[test]
    fn undeclared_receipt_output_is_refused() {
        let receipt = RunReceipt {
            targets: BTreeMap::from([(
                "part".into(),
                TargetReceipt {
                    status: TargetStatus::Built,
                    outputs: BTreeMap::from([("unknown.step".into(), "/cache/blob".into())]),
                    ..TargetReceipt::default()
                },
            )]),
            ..RunReceipt::default()
        };
        assert!(
            receipt_pairs(&plan(), &receipt, &[])
                .unwrap_err()
                .to_string()
                .contains("does not declare")
        );
    }
    #[test]
    fn receipt_staging_keeps_authored_sources_and_failed_checkpoints_out() {
        let mut plan = plan();
        plan.actions
            .get_mut("part")
            .unwrap()
            .docs
            .push("part.md".to_owned());
        plan.actions
            .get_mut("bad")
            .unwrap()
            .docs
            .push("bad.md".to_owned());
        let receipt = RunReceipt {
            targets: BTreeMap::from([
                (
                    "part".into(),
                    TargetReceipt {
                        status: TargetStatus::Built,
                        outputs: BTreeMap::from([("part.md".into(), "/cache/good".into())]),
                        ..Default::default()
                    },
                ),
                (
                    "bad".into(),
                    TargetReceipt {
                        status: TargetStatus::Failed,
                        outputs: BTreeMap::from([("bad.md".into(), "/cache/checkpoint".into())]),
                        ..Default::default()
                    },
                ),
            ]),
            ..Default::default()
        };
        let mut selected = bookkeeping_sync::StageSelection {
            paths: [
                "part.md",
                "bad.md",
                "hardware/source.rs",
                planning::GRAPH_PATH,
            ]
            .map(|path| path.as_bytes().to_vec())
            .into(),
            ..Default::default()
        };
        let allowed = stage_destinations(&plan, Some(&receipt)).unwrap();
        assert_eq!(restrict_staging(&mut selected, &allowed), 3);
        assert_eq!(selected.paths, vec![b"part.md".to_vec()]);
        let declared = stage_destinations(&plan, None).unwrap();
        assert!(declared.contains("bad.md"));
        assert!(!declared.contains("hardware/source.rs"));
        assert!(!declared.contains(planning::GRAPH_PATH));
    }
}
