mod routing;
mod scalars;
mod cooling;
use anyhow::{Context,Result,bail};
use hsm_shared_data::color;
use serde_json::{Value,json};
use std::io::{self,BufRead,Write};
fn answer(r:Value)->Result<Value>{
    let op=r["op"].as_str().context("shared-data operation")?;
    if let Some(op)=op.strip_prefix("color."){color::dispatch(op,&r)}
    else if let Some(op)=op.strip_prefix("routing."){routing::dispatch(op,&r)}
    else if let Some(op)=op.strip_prefix("scalar."){scalars::dispatch(op,&r)}
    else if let Some(op)=op.strip_prefix("cooling."){cooling::dispatch(op,&r)}
    else{bail!("unknown shared-data operation {op}")}
}
fn main()->Result<()>{
    let mut output=io::stdout().lock();
    for line in io::stdin().lock().lines(){let line=line?;if line.trim().is_empty(){continue}let result=serde_json::from_str(&line).context("reading shared-data request").and_then(answer).unwrap_or_else(|e|json!({"error":format!("{e:#}")}));serde_json::to_writer(&mut output,&result)?;writeln!(&mut output)?;output.flush()?;}
    Ok(())
}
