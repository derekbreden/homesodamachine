//! Declared generator inputs, co-writer groups and retained source copies.
use anyhow::{Context,Result,bail};
use serde_json::{Value,json};
use std::{collections::{BTreeMap,BTreeSet},fs,path::Path,process::Command};
use crate::{artifacts::names,publication,payload};

fn strings(v:&Value)->Vec<String>{v.as_array().map(|a|a.iter().filter_map(Value::as_str).map(str::to_owned).collect()).unwrap_or_default()}

/// A generated recipe crate's modules: each by name, its file, the Python stub that calls it, and
/// the modules it loads by name. Its program holds every module, and a step runs only the ones
/// it reaches, so a step is made from those and not from the rest.
struct Generated { files:BTreeMap<String,String>, stubs:BTreeMap<String,String>, loads:BTreeMap<String,BTreeSet<String>> }

fn generated_crates(root:&Path)->Vec<Generated> {
    let path_attr=regex::Regex::new(r#"#\[path\s*=\s*"([^"]+)"\]\s*(?:pub\s+)?mod\s+([A-Za-z_0-9]+)\s*;"#).unwrap();
    let init_arm=regex::Regex::new(r#""([A-Za-z_0-9.]+)"\s*=>\s*([A-Za-z_0-9]+)::initialize"#).unwrap();
    let stub_arm=regex::Regex::new(r#""([A-Za-z_0-9.]+)"\s*=>\s*Some\("([^"]+\.py)"\)"#).unwrap();
    let load=regex::Regex::new(r#"(?:import_module\(|member\()"([A-Za-z_0-9.]+)""#).unwrap();
    let mut out=Vec::new();
    let Ok(dirs)=fs::read_dir(root.join("tools/hsm")) else {return out};
    let mut dirs:Vec<_>=dirs.flatten().map(|d|d.path()).collect();dirs.sort();
    for dir in dirs {
        let compiled=dir.join("src/compiled");
        let Ok(table)=fs::read_to_string(compiled.join("modules.rs")) else {continue};
        let idents:BTreeMap<String,String>=path_attr.captures_iter(&table).map(|c|(c[2].to_owned(),c[1].to_owned())).collect();
        let mut files=BTreeMap::new();
        for c in init_arm.captures_iter(&table) {
            let(name,ident)=(c[1].to_owned(),c[2].to_owned());
            let candidates=match idents.get(&ident){Some(file)=>vec![compiled.join(file)],None=>vec![compiled.join(format!("{ident}.rs")),compiled.join("modules").join(format!("{ident}.rs"))]};
            if let Some(file)=candidates.into_iter().find(|f|f.is_file()) {
                if let Ok(relative)=file.strip_prefix(root){files.insert(name,relative.to_string_lossy().into_owned());}
            }
        }
        let stubs=stub_arm.captures_iter(&table).map(|c|(c[1].to_owned(),c[2].to_owned())).filter(|(n,_)|files.contains_key(n)).collect();
        let loads=files.iter().map(|(n,f)|(n.clone(),fs::read_to_string(root.join(f)).map(|t|load.captures_iter(&t).map(|c|c[1].to_owned()).collect()).unwrap_or_default())).collect();
        out.push(Generated{files,stubs,loads});
    }
    out
}

/// Drop from a Python step's reads the modules of a generated crate it cannot reach: from the
/// stubs it read and the modules its Python names, along the modules each loads by name. A step
/// that names none of a crate's modules keeps them all.
fn prune_modules(reads:&mut BTreeSet<String>,crates:&[Generated],root:&Path) {
    let called=regex::Regex::new(r#"(?:_compiled|_member|_RustModule)\(['"]([A-Za-z_0-9.]+)['"]"#).unwrap();
    let python:Vec<String>=reads.iter().filter(|r|r.ends_with(".py")).filter_map(|r|fs::read_to_string(root.join(r)).ok()).collect();
    for krate in crates {
        let modules:BTreeSet<&String>=krate.files.values().collect();
        if !reads.iter().any(|r|modules.contains(r)){continue;}
        let mut todo:Vec<String>=krate.stubs.iter().filter(|(_,stub)|reads.contains(*stub)).map(|(n,_)|n.clone()).collect();
        for text in &python {for c in called.captures_iter(text){if krate.files.contains_key(&c[1]){todo.push(c[1].to_owned());}}}
        if todo.is_empty(){continue;}
        let mut reached=BTreeSet::new();
        while let Some(name)=todo.pop() {
            if !reached.insert(name.clone()){continue;}
            for next in krate.loads.get(&name).into_iter().flatten(){if krate.files.contains_key(next)&&!reached.contains(next){todo.push(next.clone());}}
        }
        let keep:BTreeSet<&String>=reached.iter().filter_map(|n|krate.files.get(n)).collect();
        reads.retain(|r|!modules.contains(r)||keep.contains(r));
    }
}
pub fn inert(path:&str,config:&Value)->bool {
    let path=path.to_lowercase();strings(&config["inert_suffixes"]).iter().any(|s|path.ends_with(s))
        ||names(&config["inert_basenames"]).contains(path.rsplit('/').next().unwrap_or(""))
}
pub fn one_tree(path:&str,roots:&[String],read:bool,config:&Value)->bool {
    roots.iter().any(|r|path.starts_with(r))||read&&(names(&config["flute_shared"]).contains(path)||!strings(&config["flute_trees"]).iter().any(|r|path.starts_with(r)))
}
pub fn split(graph:&Value,config:&Value)->Value {
    let mut graph=graph.as_object().cloned().unwrap_or_default();
    if let Some(source)=graph.remove("hardware/scripts/flute_payload.py") {
        if let Some(wrappers)=config["flute_roots"].as_object(){for(wrapper,roots)in wrappers {
            let roots=strings(roots);let mut row=serde_json::Map::new();
            for side in ["reads","writes","rewritten"] {
                let paths=strings(&source[side]).into_iter().filter(|p|one_tree(p,&roots,side=="reads",config)).collect::<Vec<_>>();
                row.insert(side.into(),json!(paths));
            }graph.insert(wrapper.clone(),Value::Object(row));
        }}
    }Value::Object(graph)
}

pub fn pinned(root:&Path,files:&BTreeSet<String>)->Result<BTreeSet<String>> {
    let mut out=BTreeSet::new();
    for manifest in files.iter().filter(|p|p.ends_with("/package-manifest.json")||p.ends_with("/manifest.json")) {
        let Some(base)=manifest.rsplit_once('/').map(|(base,_)|base) else{continue;};
        let Some(record)=fs::read(root.join(manifest)).ok().and_then(|b|serde_json::from_slice::<Value>(&b).ok()).filter(Value::is_object) else {continue;};
        let mut pins=BTreeMap::new();
        if manifest.ends_with("/package-manifest.json") {
            if let Some(values)=record["files_sha256"].as_object(){for(name,digest)in values{if let Some(digest)=digest.as_str(){pins.insert(name.clone(),digest.to_owned());}}}
        } else if let Some(values)=record["files"].as_object(){for(name,entry)in values{
            if entry.is_object() && truthy(&entry["source_path"]) {if let Some(digest)=entry["sha256"].as_str(){pins.insert(name.clone(),digest.to_owned());}}
        }}
        for(name,digest)in pins {let relative=format!("{base}/{name}");
            if files.contains(&relative)&&payload::digest(root.join(&relative)).ok().as_deref()==Some(digest.as_str()){out.insert(relative);}}
    }Ok(out)
}
fn truthy(v:&Value)->bool {match v {Value::Null=>false,Value::Bool(v)=>*v,Value::String(s)=>!s.is_empty(),Value::Number(n)=>n.as_f64()!=Some(0.),Value::Array(v)=>!v.is_empty(),Value::Object(v)=>!v.is_empty()}}
fn git(root:&Path,args:&[&str])->Result<Vec<String>> {
    let output=Command::new("git").arg("-C").arg(root).args(args).output()?;
    anyhow::ensure!(output.status.success(),"git: {}",String::from_utf8_lossy(&output.stderr));
    Ok(String::from_utf8(output.stdout)?.split_whitespace().map(str::to_owned).collect())
}
pub fn tracked(root:&Path,config:&Value,publication_config:&Value)->Result<BTreeSet<String>> {
    let mut files:BTreeSet<_>=git(root,&["ls-files"])?.into_iter().collect();
    files.extend(publication::solids(root,publication_config)?);
    if let Some(pointer)=fs::read(root.join("hardware/cad-artifacts.json")).ok().and_then(|b|serde_json::from_slice::<Value>(&b).ok()) {
        if let Some(members)=pointer["solids"].as_object(){files.extend(members.keys().cloned());}
    }
    if let Some(entries)=config["implicit_solids"].as_object(){for paths in entries.values(){files.extend(names(paths));}}
    files.extend(publication::frozen_assets(root)?.into_keys());
    files.extend(git(root,&["ls-files","--others","--ignored","--exclude-standard","--","hardware/*.step.npz","hardware/*.scene.npz"])?);
    files.retain(|p|!inert(p,config));Ok(files)
}

pub fn together(writes:&BTreeMap<String,BTreeSet<String>>)->Vec<Vec<String>> {
    fn find(parent:&mut BTreeMap<String,String>,mut value:String)->String {
        while parent[&value]!=value {let next=parent[&value].clone();let next=parent[&next].clone();parent.insert(value.clone(),next.clone());value=next;}value
    }
    let mut parent:BTreeMap<_,_>=writes.keys().map(|g|(g.clone(),g.clone())).collect();let mut home=BTreeMap::new();
    for(generator,files)in writes {for file in files {
        let first=home.entry(file.clone()).or_insert_with(||generator.clone()).clone();
        let a=find(&mut parent,first);let b=find(&mut parent,generator.clone());
        if a!=b {parent.insert(a.clone().max(b.clone()),a.min(b));}
    }}
    let mut out:BTreeMap<String,Vec<String>>=BTreeMap::new();
    for generator in writes.keys(){let root=find(&mut parent,generator.clone());out.entry(root).or_default().push(generator.clone());}
    out.into_values().collect()
}

pub fn inventory(root:&Path,graph:&Value,mut files:BTreeSet<String>,config:&Value)->Result<Value> {
    let generated=generated_crates(root);
    let Some(rows)=graph.as_object() else {return Ok(json!([]));};
    let stale=rows.iter().filter(|(_,v)|v.get("rewritten").is_none()).map(|(name,_)|name.clone()).collect::<Vec<_>>();
    let mut graph=serde_json::Map::new();
    for(generator,row)in rows {
        let mut filtered=serde_json::Map::new();for side in ["reads","writes","rewritten"]{
            filtered.insert(side.into(),json!(strings(&row[side]).into_iter().filter(|p|!inert(p,config)).collect::<Vec<_>>()));
        }graph.insert(generator.clone(),Value::Object(filtered));
    }
    let orphaned=graph.keys().filter(|g|!files.contains(*g)).cloned().collect::<Vec<_>>();
    if !orphaned.is_empty(){bail!("  {} build-graph generator(s) are absent from the tree — {} among them. Re-trace the renamed generator or remove its stale graph entry.",orphaned.len(),orphaned[0]);}
    let graph=split(&Value::Object(graph),config);let graph=graph.as_object().unwrap();
    if let Some(wrappers)=config["flute_roots"].as_object(){files.extend(wrappers.keys().cloned());}
    files.extend(graph.values().flat_map(|row|names(&row["writes"])));
    if let Some(entries)=config["implicit_solids"].as_object(){files.extend(entries.values().flat_map(names));}
    let ghosts=graph.iter().map(|(g,row)|(g.clone(),names(&row["reads"]).difference(&files).cloned().collect::<Vec<_>>())).filter(|(_,bad)|!bad.is_empty()).collect::<BTreeMap<_,_>>();
    if let Some((generator,bad))=ghosts.first_key_value() {
        bail!("  {} declared read(s) across {} generator(s) name a file\n  the tree does not hold and no rule writes — {}, read by {},\n  among them. Drop the read if what wrote it is gone, or declare the writer.",ghosts.values().map(Vec::len).sum::<usize>(),ghosts.len(),bad[0],Path::new(generator).file_name().unwrap_or_default().to_string_lossy());
    }
    if !stale.is_empty(){bail!("  {} generator(s) were traced before a run said which of its writes it\n  read back — {} among them. Re-trace those:\n    tools/cad-venv/bin/python tools/bazel/trace_inputs.py \\\n{}",stale.len(),Path::new(&stale[0]).file_name().unwrap_or_default().to_string_lossy(),stale.iter().map(|g|format!("      {g}")).collect::<Vec<_>>().join(" \\\n"));}
    let mut writes=BTreeMap::new();
    for(generator,row)in graph {
        if !files.contains(generator){continue;}
        let mut targets=names(&row["writes"]);targets.extend(names(&config["implicit_solids"][generator]));
        if !targets.is_empty(){writes.insert(generator.clone(),targets);}
    }
    let mut output=Vec::new();
    for generators in together(&writes) {
        // The job runner's files are not what any step is made from: a Python step copies the
        // checkout's current ones into its folder when it runs, and a Rust step holds none.
        let program=generators.iter().find_map(|g|rows.get(g).and_then(|row|row.get("program")).cloned());
        let mut reads=BTreeSet::new();
        let mut rewritten=BTreeSet::new();let mut targets=BTreeSet::new();
        for generator in &generators {
            reads.extend(names(&graph[generator]["reads"]).intersection(&files).cloned());
            rewritten.extend(names(&graph[generator]["rewritten"]).intersection(&files).cloned());
            targets.extend(writes[generator].iter().cloned());
        }
        if program.is_none(){
            for runner in names(&config["runtime_reads"]).union(&names(&config["rust_runtime_reads"])){reads.remove(runner);}
            prune_modules(&mut reads,&generated,root);
        }
        let(docs,solids):(Vec<_>,Vec<_>)=targets.into_iter().partition(|p|rewritten.contains(p));
        let mut made=json!({"solids":solids,"docs":docs,"reads":reads});
        if let Some(program)=program {made["program"]=program;}
        output.push(json!([generators,made]));
    }
    Ok(json!(output))
}

pub fn dispatch(v:&Value)->Result<Option<Value>> {
    let text=|key:&str|v[key].as_str().with_context(||format!("{key} is text"));
    let result=match text("op")? {
        "inventory-inert"=>json!(inert(text("path")?,&v["config"])),
        "inventory-one-tree"=>json!(one_tree(text("path")?,&strings(&v["roots"]),v["read"]==true,&v["config"])),
        "inventory-split"=>split(&v["graph"],&v["config"]),
        "inventory-pinned"=>json!(pinned(Path::new(text("root")?),&names(&v["files"]))?),
        "inventory-tracked"=>json!(tracked(Path::new(text("root")?),&v["config"],&v["publication_config"])?),
        "inventory-together"=>json!(together(&serde_json::from_value(v["writes"].clone())?)),
        "inventory"=>{
            let root=Path::new(text("root")?);
            let graph=fs::read(Path::new(text("graph_path")?)).ok().and_then(|b|serde_json::from_slice::<Value>(&b).ok());
            let Some(graph)=graph else{return Ok(Some(json!([])));};
            inventory(root,&graph,names(&v["files"]),&v["config"])?
        },
        _=>return Ok(None),
    };Ok(Some(result))
}
