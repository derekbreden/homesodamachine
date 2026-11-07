//! The purchase ledger's figures: `purchases.md`'s managed totals and their sidecar, and the
//! JSON and CSV views of the ledger, its orders and its payment evidence. The other modes read
//! and write nothing.
//!
//!     purchases [--check | --report | --audit | --export-json | --export-csv]
//!               [--ledger <md>] [--orders <json>] [--evidence <json>] [<output directory>]
use anyhow::{Context as _, Result, bail};
use hsm_ledger::{ledger_totals, shared::Context};
use serde_json::json;
use std::path::{PathBuf, absolute};

const MODES: [&str; 6] = ["write", "check", "report", "audit", "export-json", "export-csv"];

fn main() -> Result<()> {
    hsm_kernel::reads::begin();
    let mut request = json!({"mode": "write"});
    let mut out = None;
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.strip_prefix("--") {
            Some(mode) if MODES.contains(&mode) => request["mode"] = json!(mode),
            Some(input @ ("ledger" | "orders" | "evidence")) => {
                let path = args.next().with_context(|| format!("--{input} takes a path"))?;
                request[input] = json!(absolute(path)?);
            }
            Some(other) => bail!("unknown option --{other}"),
            None => out = Some(absolute(PathBuf::from(arg))?),
        }
    }
    let mut ledger = Context::at(absolute(".")?, out);
    let result = ledger_totals::dispatch("main", &request, &mut ledger)?;
    print!("{}", result["output"].as_str().unwrap_or(""));
    eprint!("{}", result["stderr"].as_str().unwrap_or(""));
    std::process::exit(result["status"].as_i64().unwrap_or(1) as i32)
}
