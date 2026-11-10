//! Requested receipt and generated-change readings retain authored work while exposing unfinished targets.
use crate::{planning, receipt::RunReceipt};
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::bookkeeping_sync;
use std::{collections::BTreeSet, fs, path::Path, process::Command};

pub fn failed(receipt: &RunReceipt) -> BTreeSet<String> {
    receipt
        .unavailable_targets()
        .into_iter()
        .map(|target| format!("//:{target}"))
        .collect()
}

pub fn failed_cli(root: &Path, args: &[String]) -> Result<i32> {
    if args
        .first()
        .is_some_and(|argument| ["--help", "-h"].contains(&argument.as_str()))
    {
        println!(
            "Read failed, blocked or non-current targets from a native receipt.\n\nUsage: hsm-build-plan failed-targets FILE"
        );
        return Ok(0);
    }
    ensure!(
        args.len() == 1,
        "failed-targets requires one native receipt file"
    );
    let path = root.join(args.first().context("native receipt file")?);
    let receipt: RunReceipt = serde_json::from_slice(
        &fs::read(&path).with_context(|| format!("read native receipt {}", path.display()))?,
    )?;
    ensure!(
        receipt.schema == 1,
        "unsupported native receipt schema {}",
        receipt.schema
    );
    println!(
        "{}",
        failed(&receipt).into_iter().collect::<Vec<_>>().join(",")
    );
    Ok(0)
}

pub fn drop_cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut write = false;
    for argument in args {
        match argument.as_str() {
            "--write" => write = true,
            "--help" | "-h" => {
                println!(
                    "Name or restore unstaged generated exports while retaining authored files.\n\nUsage: hsm-build-plan drop-derived [--write]"
                );
                return Ok(0);
            }
            option => bail!("unknown drop-derived option {option}"),
        }
    }
    let changed = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["diff", "--name-only", "-z"])
        .output()?;
    ensure!(
        changed.status.success(),
        "git diff: {}",
        String::from_utf8_lossy(&changed.stderr)
    );
    let dirty = changed
        .stdout
        .split(|byte| *byte == 0)
        .filter(|path| !path.is_empty())
        .map(|path| String::from_utf8(path.to_vec()).context("changed path is not UTF-8"))
        .collect::<Result<Vec<_>>>()?;
    if dirty.is_empty() {
        println!("The worktree carries no unstaged change.");
        return Ok(0);
    }
    let made = planning::load_inventory(root)?
        .into_iter()
        .flat_map(|row| row.1.solids.into_iter().chain(row.1.docs))
        .collect();
    let (drop, keep) = bookkeeping_sync::drop_paths(&dirty, &made);
    if !keep.is_empty() {
        println!(
            "{} authored or unclassified path(s) left alone:",
            keep.len()
        );
        for path in &keep {
            println!("  {path}");
        }
    }
    if drop.is_empty() {
        println!("No unstaged path is classified as wholly generated.");
        return Ok(0);
    }
    println!(
        "{} generated path(s) {}:",
        drop.len(),
        if write {
            "restored"
        } else {
            "would be restored"
        }
    );
    for path in &drop {
        println!("  {path}");
    }
    if write {
        ensure!(
            Command::new("git")
                .arg("-C")
                .arg(root)
                .args(["checkout", "--"])
                .args(drop)
                .status()?
                .success(),
            "git checkout failed"
        );
    } else {
        println!("Use --write to restore them.");
    }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::receipt::{TargetReceipt, TargetStatus};
    use std::collections::BTreeMap;
    #[test]
    fn native_unavailable_statuses_keep_failed_and_blocked_targets() {
        let receipt = RunReceipt {
            targets: BTreeMap::from([
                (
                    "good".into(),
                    TargetReceipt {
                        status: TargetStatus::Cached,
                        ..Default::default()
                    },
                ),
                (
                    "bad".into(),
                    TargetReceipt {
                        status: TargetStatus::Failed,
                        ..Default::default()
                    },
                ),
                (
                    "later".into(),
                    TargetReceipt {
                        status: TargetStatus::Blocked,
                        ..Default::default()
                    },
                ),
                (
                    "changed".into(),
                    TargetReceipt {
                        status: TargetStatus::NotCurrent,
                        ..Default::default()
                    },
                ),
            ]),
            ..Default::default()
        };
        assert_eq!(
            failed(&receipt),
            ["//:bad", "//:changed", "//:later"]
                .map(str::to_owned)
                .into()
        );
    }
}
