use anyhow::Result;
use serde_json::json;
use std::io::{self, Write};
fn main() -> Result<()> {
    hsm_documents::interop::set_dispatch(hsm_guides::request);
    loop {
        let mut line = String::new();
        if io::stdin().read_line(&mut line)? == 0 {
            break;
        }
        let result = serde_json::from_str(&line)
            .map_err(Into::into)
            .and_then(hsm_guides::request);
        let result = result.unwrap_or_else(|e| json!({"error":format!("{e:#}")}));
        let mut stdout = io::stdout().lock();
        writeln!(stdout, "{}", serde_json::to_string(&result)?)?;
        stdout.flush()?;
    }
    Ok(())
}
