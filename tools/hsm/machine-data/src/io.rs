//! Atomic scalar JSON files and machine-source filesystem metadata.
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::{collections::BTreeSet,io::Write,path::Path};

pub fn write_json(v:&Value)->Result<Value>{
 let path=Path::new(v["path"].as_str().context("JSON target path")?);
 let mut bytes=Vec::new();
 if let Some(indent)=v["indent"].as_u64(){let indent=vec![b' ';indent as usize];let mut serializer=serde_json::Serializer::with_formatter(&mut bytes,serde_json::ser::PrettyFormatter::with_indent(&indent));serde::Serialize::serialize(&v["value"],&mut serializer)?;}
 else{serde_json::to_writer(&mut bytes,&v["value"])?;}
 bytes.push(b'\n');if path.is_file()&&std::fs::read(path)?==bytes{return Ok(json!({"changed":false}));}
 if let Some(parent)=path.parent(){std::fs::create_dir_all(parent)?;}
 let temporary=path.with_file_name(format!(".{}.{}.tmp",path.file_name().unwrap().to_string_lossy(),std::process::id()));std::fs::File::create(&temporary)?.write_all(&bytes)?;std::fs::rename(&temporary,path)?;Ok(json!({"changed":true}))
}
const WORLD:&str="hardware/manifold-layout/enclosure_assembly.py";
fn sources(v:&Value)->Result<Vec<String>>{
 let root=Path::new(v["root"].as_str().context("source root")?);let mut names=BTreeSet::new();let folder=root.join("hardware/scripts/meshcad");if folder.is_dir(){for entry in std::fs::read_dir(folder)?{let path=entry?.path();if path.extension().is_some_and(|s|s=="py"){names.insert(path.strip_prefix(root)?.to_string_lossy().into_owned());}}}
 let graph_path=root.join("tools/bazel/graph.json");hsm_documents::interop::note_io(&graph_path,false);
 let graph=std::fs::read(graph_path).ok().and_then(|raw|serde_json::from_slice::<Value>(&raw).ok());
 if let Some(entry)=graph.as_ref().and_then(|v|v.get(WORLD)){if let Some(reads)=entry["reads"].as_array(){for row in reads{if let Some(name)=row.as_str(){if [".py",".rs",".toml","Cargo.lock"].iter().any(|s|name.ends_with(s)){names.insert(name.to_owned());}}}}}
 else{for name in["manifold-layout/enclosure_assembly.py","manifold-layout/_lines.py","manifold-layout/manifold_layout.py","scripts/_routing.py","printed-parts/enclosure/enclosure/enclosure.py"]{names.insert(format!("hardware/{name}"));}}
 Ok(names.into_iter().collect())
}
pub fn request(v:&Value)->Result<Value>{Ok(match v["op"].as_str().context("IO operation")?{
 "write_json"=>write_json(v)?,
 "json_text"=>json!(std::fs::read_to_string(v["path"].as_str().context("JSON input path")?)?),
 "machine_sources"=>json!(sources(v)?),
 "machine_stamps"=>{let root=Path::new(v["root"].as_str().context("source root")?);let mut stamps=serde_json::Map::new();for name in sources(v)?{let value=match std::fs::metadata(root.join(&name)){Ok(metadata)=>{#[cfg(unix)]{use std::os::unix::fs::MetadataExt;json!(format!("{}:{}",metadata.len(),metadata.mtime()))}#[cfg(not(unix))]{let modified=metadata.modified()?.duration_since(std::time::UNIX_EPOCH)?.as_secs();json!(format!("{}:{modified}",metadata.len()))}},Err(_)=>json!("gone")};stamps.insert(name,value);}json!(stamps)},
 _=>anyhow::bail!("unknown IO operation"),
})}
