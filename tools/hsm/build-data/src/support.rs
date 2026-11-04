//! Stable source and graph inputs for build support actions.
use anyhow::{Context,Result};
use serde_json::{Value,json};
use std::{collections::{BTreeMap,BTreeSet},fs,path::Path};

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

pub fn same_code(before:&[u8],after:&[u8],callback:&mut impl FnMut(Value)->Result<Value>)->Result<bool> {
    let a=callback(json!({"op":"parse-source","bytes":before}))?;
    let b=callback(json!({"op":"parse-source","bytes":after}))?;
    Ok(if a["dump"].is_null()||b["dump"].is_null() {before==after} else {a["dump"]==b["dump"]})
}

fn lines(text:&str)->Vec<&str> {
    let mut rows=Vec::new();let mut start=0;let mut chars=text.char_indices().peekable();
    while let Some((at,c))=chars.next() {
        if matches!(c,'\n'|'\r'|'\x0b'|'\x0c'|'\x1c'|'\x1d'|'\x1e'|'\u{85}'|'\u{2028}'|'\u{2029}') {
            let mut end=at+c.len_utf8();
            if c=='\r' && chars.peek().is_some_and(|(_,c)|*c=='\n') {let(at,c)=chars.next().unwrap();end=at+c.len_utf8();}
            rows.push(&text[start..end]);start=end;
        }
    }
    if start<text.len(){rows.push(&text[start..]);}rows
}

pub fn stripped(raw:&[u8],callback:&mut impl FnMut(Value)->Result<Value>)->Result<Vec<u8>> {
    let tokens=callback(json!({"op":"tokenize-source","bytes":raw}))?;
    if tokens["encoding"]!="utf-8" {return Ok(raw.to_vec());}
    let Ok(text)=std::str::from_utf8(raw) else {return Ok(raw.to_vec());};
    let mut cut=BTreeMap::<usize,usize>::new();let mut inside=BTreeSet::new();
    for token in tokens["tokens"].as_array().context("tokenized source")? {
        let start=token[1][0].as_u64().context("token row")?as usize;
        let end=token[2][0].as_u64().context("token end row")?as usize;
        if token[0]=="COMMENT" {
            let column=token[1][1].as_u64().context("token column")?as usize;
            let held=cut.entry(start).or_insert(column);*held=(*held).min(column);
        } else if end>start {inside.extend(start..=end);}
    }
    let mut output=String::new();
    for (i,line) in lines(text).into_iter().enumerate() {
        let row=i+1;
        if inside.contains(&row) {output.push_str(line);continue;}
        let stop=cut.get(&row).and_then(|&column|line.char_indices().nth(column).map(|(at,_)|at)).unwrap_or(line.len());
        let code=line[..stop].trim_end_matches(|c:char|c.is_whitespace()||matches!(c,'\x1c'|'\x1d'|'\x1e'));
        if !code.is_empty() {output.push_str(code);if line.ends_with('\n') {output.push('\n');}}
    }
    Ok(output.into_bytes())
}

pub fn strip_files(root:&Path,files:&[String],callback:&mut impl FnMut(Value)->Result<Value>)->Result<Value> {
    for relative in files {
        let raw=fs::read(relative)?;
        let before=callback(json!({"op":"parse-source","bytes":raw}))?;
        let output=if before["dump"].is_null() {raw.clone()} else {stripped(&raw,callback)?};
        let after=callback(json!({"op":"parse-source","bytes":output}))?;
        if if before["dump"].is_null()||after["dump"].is_null() {raw!=output} else {before["dump"]!=after["dump"]} {
            return Ok(json!({"status":1,"error":format!("  {relative}: stripping its comments moved what it computes")}));
        }
        let destination=root.join(relative);fs::create_dir_all(destination.parent().context("stripped source parent")?)?;
        fs::write(destination,output)?;
    }
    Ok(json!({"status":0}))
}
