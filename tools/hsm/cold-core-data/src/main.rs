use anyhow::{Context, Result};
use std::io::{self, Write};

fn main() -> Result<()> {
    hsm_documents::interop::set_dispatch(|value| hsm_cold_core_data::request(&value));
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args.first().map(String::as_str) == Some("--serve") {
        loop {
            let mut line = String::new();
            if io::stdin().read_line(&mut line)? == 0 {
                break;
            }
            let answer = serde_json::from_str(&line)
                .context("decode request")
                .and_then(|r| hsm_cold_core_data::request(&r))
                .unwrap_or_else(|e| serde_json::json!({"error": format!("{e:#}")}));
            let mut stdout = io::stdout().lock();
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
