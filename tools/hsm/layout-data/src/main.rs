use anyhow::{Result, bail};
use hsm_layout_data::request;
use std::io::{self, BufRead, Write};

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    if args.next().as_deref() != Some("--serve") {
        bail!("usage: layout-data --serve")
    }
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut output = stdout.lock();
    for line in stdin.lock().lines() {
        let result = serde_json::from_str(&line?)
            .map_err(Into::into)
            .and_then(request);
        let value =
            result.unwrap_or_else(|error| serde_json::json!({"error": format!("{error:#}")}));
        serde_json::to_writer(&mut output, &value)?;
        writeln!(output)?;
        output.flush()?;
    }
    Ok(())
}
