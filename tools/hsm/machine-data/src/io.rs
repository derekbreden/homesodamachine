//! Atomic scalar JSON files supply retained manual CAD callers.
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::{io::Write,path::Path};

pub fn write_json(v:&Value)->Result<Value>{
 let path=Path::new(v["path"].as_str().context("JSON target path")?);
 let mut bytes=Vec::new();
 if let Some(indent)=v["indent"].as_u64(){let indent=vec![b' ';indent as usize];let mut serializer=serde_json::Serializer::with_formatter(&mut bytes,serde_json::ser::PrettyFormatter::with_indent(&indent));serde::Serialize::serialize(&v["value"],&mut serializer)?;}
 else{serde_json::to_writer(&mut bytes,&v["value"])?;}
 bytes.push(b'\n');if path.is_file()&&std::fs::read(path)?==bytes{return Ok(json!({"changed":false}));}
 if let Some(parent)=path.parent(){std::fs::create_dir_all(parent)?;}
 let temporary=path.with_file_name(format!(".{}.{}.tmp",path.file_name().unwrap().to_string_lossy(),std::process::id()));std::fs::File::create(&temporary)?.write_all(&bytes)?;std::fs::rename(&temporary,path)?;Ok(json!({"changed":true}))
}
pub fn request(v:&Value)->Result<Value>{Ok(match v["op"].as_str().context("IO operation")?{
 "write_json"=>write_json(v)?,
 "json_text"=>json!(std::fs::read_to_string(v["path"].as_str().context("JSON input path")?)?),
 _=>anyhow::bail!("unknown IO operation"),
})}
