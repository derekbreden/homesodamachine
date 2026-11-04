//! File selection, generated-text carry and CAD pointer reconciliation.
mod bookkeeping_affected;
mod bookkeeping_common;
mod bookkeeping_cut;
mod bookkeeping_pointers;
mod bookkeeping_sync;
use anyhow::{Result, bail};
use serde_json::{Value, json};
use std::io::{self, Write};
fn answer(v: &Value) -> Result<Value> {
    let op = v["op"].as_str().unwrap_or("");
    if let Some(op) = op.strip_prefix("sync.") {
        bookkeeping_sync::dispatch(op, v)
    } else if let Some(op) = op.strip_prefix("affected.") {
        bookkeeping_affected::dispatch(op, v)
    } else if let Some(op) = op.strip_prefix("merge.") {
        bookkeeping_pointers::dispatch(op, v)
    } else if let Some(op) = op.strip_prefix("cut.") {
        bookkeeping_cut::dispatch(op, v)
    } else if let Some(op) = op.strip_prefix("drop.") {
        bookkeeping_sync::drop_dispatch(op, v)
    } else if op == "failed" {
        Ok(bookkeeping_common::failed(v))
    } else {
        bail!("unknown bookkeeping operation {op}")
    }
}
fn main() -> Result<()> {
    let mut output = io::stdout().lock();
    loop {
        let mut line = String::new();
        if io::stdin().read_line(&mut line)? == 0 {
            break;
        }
        if line.trim().is_empty() {
            continue;
        }
        let result = serde_json::from_str(&line)
            .map_err(anyhow::Error::from)
            .and_then(|v| answer(&v))
            .unwrap_or_else(|e| json!({"error":e.to_string()}));
        serde_json::to_writer(&mut output, &result)?;
        writeln!(&mut output)?;
        output.flush()?;
    }
    Ok(())
}
