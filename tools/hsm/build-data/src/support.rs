//! Stable graph inputs for build support actions.
use anyhow::{Context,Result};
use serde_json::{Value,json};
use std::{collections::BTreeSet,fs,path::Path};

pub fn project_graph(graph:&Value,generator:&str)->Value {
    let Some(row)=graph.get(generator) else {return json!({});};
    let names=|value:&Value|value.as_array().map(|a|a.iter().filter_map(Value::as_str).map(str::to_owned).collect::<BTreeSet<_>>()).unwrap_or_default();
    let reads=names(&row["reads"]);
    let mut written=BTreeSet::new();let mut rewritten=BTreeSet::new();
    if let Some(rows)=graph.as_object() {for row in rows.values() {written.extend(names(&row["writes"]));rewritten.extend(names(&row["rewritten"]));}}
    json!({generator:{"reads":reads,"writes":[],"rewritten":[]},
        "@derived-input-classification":{"reads":[],"writes":reads.intersection(&written).collect::<Vec<_>>(),"rewritten":reads.intersection(&rewritten).collect::<Vec<_>>()}})
}

pub fn write_projection(source:&Path,destination:&Path,generator:&str)->Result<()> {
    let graph:Value=serde_json::from_slice(&fs::read(source)?)?;
    let projected=project_graph(&graph,generator);
    let mut bytes=Vec::new();
    let formatter=serde_json::ser::PrettyFormatter::with_indent(b" ");
    let mut serializer=serde_json::Serializer::with_formatter(&mut bytes,formatter);
    serde::Serialize::serialize(&projected,&mut serializer)?;
    let text=crate::payload::ascii_json(&String::from_utf8(bytes)?)+"\n";
    if fs::read_to_string(destination).ok().as_deref()!=Some(text.as_str()) {
        fs::create_dir_all(destination.parent().context("graph projection parent")?)?;
        fs::write(destination,text)?;
    }
    Ok(())
}
