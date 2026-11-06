mod compiled;
mod rust_step;
use anyhow::Result;
use hsm_documents::interop;
use serde_json::{Value,json};
use std::io::{self,Write};
fn dispatch(value:Value)->Result<Value>{
    if let Some(result)=interop::native_object(&value){return result;}
    compiled::request(&value)
}
fn main()->Result<()> {
    interop::set_dispatch(dispatch);
    loop {
        let mut line=String::new();if io::stdin().read_line(&mut line)?==0{break;}
        let value=serde_json::from_str(&line).map_err(Into::into).and_then(dispatch);
        let value=match value {Ok(value)=>value,Err(error)=>json!({"error":format!("{error:#}")})};
        println!("{}",value);io::stdout().flush()?;
    }Ok(())
}
