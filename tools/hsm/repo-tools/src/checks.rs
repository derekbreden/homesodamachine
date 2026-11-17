//! Runs the retained check readings on request and can write a clockless verdict.
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::{
    collections::BTreeMap,
    path::{Path, PathBuf},
    process::Command,
    time::Instant,
};
const CHECKS: [(&str, &str); 6] = [
    (
        "check_enclosure_mating_clearance",
        "enclosure-mating-clearance",
    ),
    ("check_ledger", "ledger"),
    ("check_pinmap", "pinmap"),
    ("check_purchase_evidence", "purchase-evidence"),
    ("check_step_colours", "step-colours"),
    ("check_paths", "paths"),
];
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct Row {
    check: String,
    status: String,
    note: String,
}
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct Verdict {
    green: bool,
    checks: Vec<Row>,
    detail: BTreeMap<String, Vec<String>>,
}
struct Run {
    check: String,
    code: i32,
    seconds: f64,
    out: String,
    err: String,
}
fn verdict(runs: &[Run]) -> Verdict {
    let mut checks = Vec::new();
    let mut detail = BTreeMap::new();
    for run in runs {
        let body = if run.out.is_empty() {
            &run.err
        } else {
            &run.out
        };
        let note = body
            .lines()
            .rev()
            .find(|l| !l.trim().is_empty())
            .unwrap_or("")
            .trim()
            .to_owned();
        checks.push(Row {
            check: run.check.clone(),
            status: if run.code == 0 { "ok" } else { "red" }.into(),
            note,
        });
        if run.code != 0 {
            let body = run.out.clone() + &run.err;
            let mut lines = body
                .lines()
                .map(str::trim_end)
                .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with("[build]"))
                .map(str::to_owned)
                .collect::<Vec<_>>();
            if lines.len() > 25 {
                lines.drain(..lines.len() - 25);
            }
            detail.insert(run.check.clone(), lines);
        }
    }
    Verdict {
        green: detail.is_empty(),
        checks,
        detail,
    }
}
pub fn read(root: &Path) -> Result<Verdict> {
    let executable = std::env::current_exe()?;
    let mut runs = Vec::new();
    for (id, name) in CHECKS {
        let started = Instant::now();
        let run = Command::new(&executable)
            .args([
                "--root",
                root.to_str().context("UTF-8 repository path")?,
                "check",
                name,
            ])
            .current_dir(root)
            .output()?;
        runs.push(Run {
            check: id.into(),
            code: run.status.code().unwrap_or(1),
            seconds: started.elapsed().as_secs_f64(),
            out: String::from_utf8_lossy(&run.stdout).into_owned(),
            err: String::from_utf8_lossy(&run.stderr).into_owned(),
        });
    }
    let reading = verdict(&runs);
    let width = runs.iter().map(|r| r.check.len()).max().unwrap_or(0);
    for (run, row) in runs.iter().zip(&reading.checks) {
        println!(
            "  {} {:width$}  {:5.1}s  {}",
            if run.code == 0 { "ok  " } else { "RED " },
            run.check,
            run.seconds,
            row.note.chars().take(64).collect::<String>()
        );
    }
    println!(
        "\n{}/{} green, {:.0}s total",
        runs.iter().filter(|r| r.code == 0).count(),
        runs.len(),
        runs.iter().map(|r| r.seconds).sum::<f64>()
    );
    for run in runs.iter().filter(|r| r.code != 0) {
        println!("\n──── {} ────", run.check);
        let body = run.out.clone() + &run.err;
        let lines = body.trim().lines().collect::<Vec<_>>();
        for line in lines.iter().skip(lines.len().saturating_sub(25)) {
            println!("  {line}");
        }
    }
    Ok(reading)
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut json = None;
    let mut list = false;
    let mut it = args.iter();
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--list" => list = true,
            "--json" => json = Some(PathBuf::from(it.next().context("--json needs a path")?)),
            "--help" | "-h" => {
                println!(
                    "repo-tools checks [--list] [--json PATH]\nRuns the explicit retained list on request. The optional JSON carries no time or duration; red is a reading and holds no build or publish."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown checks option {arg}"),
        }
    }
    if list {
        for (id, name) in CHECKS {
            println!("  {id}  (repo-tools check {name})");
        }
        println!("{} check(s)", CHECKS.len());
        return Ok(0);
    }
    let reading = read(root)?;
    if let Some(path) = json {
        crate::write_json(
            &if path.is_absolute() {
                path
            } else {
                root.join(path)
            },
            &reading,
        )?;
    }
    Ok(i32::from(!reading.green))
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn verdict_has_no_clock_and_filters_queue_pids() {
        let runs = vec![Run {
            check: "check_example".into(),
            code: 1,
            seconds: 42.,
            out: "[build] queued pid 9\nactual finding\n".into(),
            err: String::new(),
        }];
        let first = verdict(&runs);
        let second = verdict(&[Run {
            check: "check_example".into(),
            code: 1,
            seconds: 81.,
            out: "[build] queued pid 17\nactual finding\n".into(),
            err: String::new(),
        }]);
        assert_eq!(first, second);
        assert_eq!(first.detail["check_example"], vec!["actual finding"]);
        let json = serde_json::to_string(&first).unwrap();
        assert!(!json.contains("seconds"));
    }
}
