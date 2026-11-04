use anyhow::{Result, bail};
use std::io::{self, BufRead, Write};

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args == ["--serve"] {
        let stdin = io::stdin();
        let mut stdout = io::stdout().lock();
        for line in stdin.lock().lines() {
            let request: serde_json::Value = serde_json::from_str(&line?)?;
            let response = match hsm_faucet_data::dispatch(&request) {
                Ok(value) => value,
                Err(error) => serde_json::json!({"error": format!("{error:#}")}),
            };
            serde_json::to_writer(&mut stdout, &response)?;
            stdout.write_all(b"\n")?;
            stdout.flush()?;
        }
        return Ok(());
    }
    if args.len() != 1 {
        bail!("usage: faucet-data '<request JSON>' | --serve");
    }
    let request = serde_json::from_str(&args[0])?;
    println!("{}", hsm_faucet_data::dispatch(&request)?);
    Ok(())
}
