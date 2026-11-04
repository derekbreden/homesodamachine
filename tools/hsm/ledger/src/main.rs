//! Ledger readers, model-derived costs, production estimates and document updates.
mod bom;
mod bom_sync;
mod build_time;
mod labor;
mod printing;
mod shared;
mod tools;

use anyhow::{Context, Result, bail};
use serde_json::{Value, json};
use shared::Context as LedgerContext;
use std::io::{self, BufRead, Write};

fn answer(request: Value) -> Result<Value> {
    let mut context = LedgerContext::new(&request);
    let op = request["op"]
        .as_str()
        .context("ledger operation is required")?;
    let result = if let Some(name) = op.strip_prefix("bom.") {
        bom::dispatch(name, &request, &mut context)?
    } else if let Some(name) = op.strip_prefix("bom_sync.") {
        bom_sync::dispatch(name, &request, &mut context)?
    } else if let Some(name) = op.strip_prefix("build.") {
        build_time::dispatch(name, &request, &mut context)?
    } else if let Some(name) = op.strip_prefix("printing.") {
        printing::dispatch(name, &request, &mut context)?
    } else if let Some(name) = op.strip_prefix("labor.") {
        labor::dispatch(name, &request, &mut context)?
    } else if let Some(name) = op.strip_prefix("tools.") {
        tools::dispatch(name, &request, &mut context)?
    } else {
        bail!("unknown ledger operation: {op}")
    };
    Ok(json!({"result":result,"reads":context.reads,"rewritten":context.rewritten}))
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.first().is_some_and(|s| s == "--serve") {
        let mut out = io::stdout().lock();
        for line in io::stdin().lock().lines() {
            let line = line?;
            if line.trim().is_empty() {
                continue;
            }
            let response = serde_json::from_str(&line)
                .context("reading ledger request")
                .and_then(answer)
                .unwrap_or_else(|error| json!({"error":format!("{error:#}")}));
            serde_json::to_writer(&mut out, &response)?;
            writeln!(&mut out)?;
            out.flush()?;
        }
    } else {
        let request =
            serde_json::from_str(args.first().context("pass a JSON request or --serve")?)?;
        println!("{}", answer(request)?);
    }
    Ok(())
}
