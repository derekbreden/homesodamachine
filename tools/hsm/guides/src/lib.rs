//! Owner-guide page composition and illustration transformations.
use anyhow::{Context, Result, bail};
use serde_json::Value;
pub fn request(value: Value) -> Result<Value> {
    if let Some(result) = hsm_documents::interop::native_object(&value) {
        let result = result?;
        compiled::register_io()?;
        return Ok(result);
    }
    match value["op"].as_str().context("guide operation")? {
        "compiled" => {
            let result = compiled::request(&value)?;
            compiled::register_io()?;
            Ok(result)
        }
        op => bail!("unknown guide operation {op}"),
    }
}

pub mod compiled;
mod native;
