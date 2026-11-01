//! `hsm-render`: the jobs `hsm render --jobs` takes, drawn in this process. A build action runs it
//! where `hsm render` would ask the daemon: `_rust_part.program` builds it from the checkout the
//! action reads, so the renderer's own sources are among the action's inputs.
//!
//!     hsm-render [--root DIR] [--json] --jobs FILE|-
//!
//! Each job is a JSON object of `Job`'s keys; a key left out takes its default. Every job is
//! drawn, and a picture that fails fails the run after the others.

use anyhow::{bail, Context, Result};
use hsm_render::{job::Job, Renderer};
use serde_json::{json, Value};
use std::io::Read;
use std::path::PathBuf;
use std::process::ExitCode;

fn main() -> ExitCode {
    match run() {
        Ok(true) => ExitCode::SUCCESS,
        Ok(false) => ExitCode::FAILURE,
        Err(e) => {
            eprintln!("hsm-render: {e:#}");
            ExitCode::from(2)
        }
    }
}

fn run() -> Result<bool> {
    let (mut root, mut source, mut as_json) = (PathBuf::from("."), None, false);
    let mut args = std::env::args().skip(1);
    while let Some(a) = args.next() {
        match a.as_str() {
            "--root" => root = args.next().context("--root wants a directory")?.into(),
            "--jobs" => source = Some(args.next().context("--jobs wants a file or -")?),
            "--json" => as_json = true,
            _ => bail!("unknown argument {a:?}: hsm-render [--root DIR] [--json] --jobs FILE|-"),
        }
    }
    let source = source.context("hsm-render [--root DIR] [--json] --jobs FILE|-")?;
    let text = if source == "-" {
        let mut s = String::new();
        std::io::stdin().read_to_string(&mut s)?;
        s
    } else {
        std::fs::read_to_string(&source).with_context(|| format!("read {source}"))?
    };
    let jobs: Vec<Job> =
        serde_json::from_str(&text).with_context(|| format!("--jobs {source}: want a JSON array of jobs"))?;

    let mut renderer = Renderer::new();
    let (mut reports, mut failed) = (Vec::new(), Vec::new());
    for job in &jobs {
        let what = job.out.as_ref().map_or_else(|| job.step.clone().unwrap_or_default(), |o| o.display().to_string());
        match renderer.render(&root, job) {
            Ok(mut report) => {
                report["adapter"] = json!(renderer.adapter());
                if !as_json {
                    println!(
                        "wrote {}  {}x{}  {} ms",
                        report["out"].as_str().unwrap_or_default(),
                        report["width"],
                        report["height"],
                        report["ms"]["total"]
                    );
                }
                reports.push(report);
            }
            Err(e) => {
                eprintln!("FAILED {what}: {e:#}");
                reports.push(json!({"out": what, "error": format!("{e:#}")}));
                failed.push(what);
            }
        }
    }
    if as_json {
        println!("{}", serde_json::to_string_pretty(&Value::Array(reports))?);
    }
    Ok(failed.is_empty())
}
