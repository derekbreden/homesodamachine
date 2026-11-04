use anyhow::{Context, Result};
use std::io::{self, BufRead, Write};

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.first().map(String::as_str) == Some("--serve") {
        let stdin = io::stdin();
        let mut stdout = io::BufWriter::new(io::stdout().lock());
        for line in stdin.lock().lines() {
            let answer = line
                .context("read request")
                .and_then(|s| serde_json::from_str(&s).context("decode request"))
                .and_then(|r| hsm_cold_core_data::request(&r))
                .unwrap_or_else(|e| serde_json::json!({"error": format!("{e:#}")}));
            serde_json::to_writer(&mut stdout, &answer)?;
            writeln!(stdout)?;
            stdout.flush()?;
        }
    } else {
        let raw = args
            .first()
            .context("cold-core-data --serve | '<request JSON>'")?;
        let result = hsm_cold_core_data::request(&serde_json::from_str(raw)?)?;
        println!("{}", serde_json::to_string(&result)?);
    }
    Ok(())
}
