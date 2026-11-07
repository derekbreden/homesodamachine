use hsm_ledger::{analysis, ledger_totals, shared};
use anyhow::{Context as _,Result,bail};
use serde_json::{Value,json};
use std::io::{self,BufRead,Write};
fn answer(r:Value)->Result<Value>{
    let mut ctx=shared::Context::new(&r);let op=r["op"].as_str().context("evidence operation")?;
    let result=if let Some(op)=op.strip_prefix("analysis."){analysis::dispatch(op,&r,&mut ctx)?}else if let Some(op)=op.strip_prefix("ledger."){ledger_totals::dispatch(op,&r,&mut ctx)?}else{bail!("unknown evidence operation {op}")};
    Ok(json!({"result":result,"reads":ctx.reads,"rewritten":ctx.rewritten}))
}
fn main()->Result<()>{
    let mut out=io::stdout().lock();
    for line in io::stdin().lock().lines(){let line=line?;if line.trim().is_empty(){continue}let response=serde_json::from_str(&line).context("reading evidence request").and_then(answer).unwrap_or_else(|e|json!({"error":format!("{e:#}")}));serde_json::to_writer(&mut out,&response)?;writeln!(&mut out)?;out.flush()?;}
    Ok(())
}
