//! Native producer declarations classify shared outputs and retained authored inputs.
use anyhow::{Result,bail};
use serde_json::{Value,json};
use std::{collections::{BTreeMap,BTreeSet},fs,path::Path,process::Command};
use crate::{artifacts::names,publication,payload};

fn strings(v:&Value)->Vec<String>{v.as_array().map(|a|a.iter().filter_map(Value::as_str).map(str::to_owned).collect()).unwrap_or_default()}

pub fn inert(path:&str,config:&Value)->bool {
    let path=path.to_lowercase();strings(&config["inert_suffixes"]).iter().any(|s|path.ends_with(s))
        ||names(&config["inert_basenames"]).contains(path.rsplit('/').next().unwrap_or(""))
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
fn git_paths(root:&Path,args:&[&str])->Result<Vec<String>> {
    let output=Command::new("git").arg("-C").arg(root).args(["ls-files", "-z"]).args(args).output()?;
    anyhow::ensure!(output.status.success(),"git: {}",String::from_utf8_lossy(&output.stderr));
    Ok(String::from_utf8(output.stdout)?.split('\0').filter(|path|!path.is_empty()).map(str::to_owned).collect())
}
pub fn tracked(root:&Path,config:&Value,publication_config:&Value)->Result<BTreeSet<String>> {
    let mut files:BTreeSet<_>=git_paths(root,&[])?.into_iter().collect();
    files.extend(publication::solids(root,publication_config)?);
    if let Some(pointer)=fs::read(root.join("hardware/cad-artifacts.json")).ok().and_then(|b|serde_json::from_slice::<Value>(&b).ok()) {
        if let Some(members)=pointer["solids"].as_object(){files.extend(members.keys().cloned());}
    }
    if let Some(entries)=config["implicit_solids"].as_object(){for paths in entries.values(){files.extend(names(paths));}}
    files.extend(publication::frozen_assets(root)?.into_keys());
    files.extend(git_paths(root,&["--others","--ignored","--exclude-standard","--","hardware/*.step.npz","hardware/*.scene.npz"])?);
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

pub fn inventory(_root:&Path,graph:&Value,mut files:BTreeSet<String>,config:&Value)->Result<Value> {
    let Some(rows)=graph.as_object() else {return Ok(json!([]));};
    for (generator,row) in rows { if row.get("program").is_none() { bail!("{generator} has no native program declaration; register its Rust producer with hsm-build-plan trace-inputs"); } }
    let stale=rows.iter().filter(|(_,v)|v.get("rewritten").is_none()).map(|(name,_)|name.clone()).collect::<Vec<_>>();
    let mut graph=serde_json::Map::new();
    for(generator,row)in rows {
        let mut filtered=serde_json::Map::new();for side in ["reads","writes","rewritten"]{
            filtered.insert(side.into(),json!(strings(&row[side]).into_iter().filter(|p|!inert(p,config)).collect::<Vec<_>>()));
        }graph.insert(generator.clone(),Value::Object(filtered));
    }
    let orphaned=graph.keys().filter(|g|!files.contains(*g)).cloned().collect::<Vec<_>>();
    if !orphaned.is_empty(){bail!("  {} build-graph generator(s) are absent from the tree — {} among them. Re-trace the renamed generator or remove its stale graph entry.",orphaned.len(),orphaned[0]);}
    files.extend(graph.values().flat_map(|row|names(&row["writes"])));
    if let Some(entries)=config["implicit_solids"].as_object(){files.extend(entries.values().flat_map(names));}
    let ghosts=graph.iter().map(|(g,row)|(g.clone(),names(&row["reads"]).difference(&files).cloned().collect::<Vec<_>>())).filter(|(_,bad)|!bad.is_empty()).collect::<BTreeMap<_,_>>();
    if let Some((generator,bad))=ghosts.first_key_value() {
        bail!("  {} declared read(s) across {} generator(s) name a file\n  the tree does not hold and no rule writes — {}, read by {},\n  among them. Drop the read if what wrote it is gone, or declare the writer.",ghosts.values().map(Vec::len).sum::<usize>(),ghosts.len(),bad[0],Path::new(generator).file_name().unwrap_or_default().to_string_lossy());
    }
    if !stale.is_empty(){bail!("producer {} lacks rewritten-output classification; run hsm-build-plan trace-inputs {}",stale[0],stale.join(" "));}
    let mut writes=BTreeMap::new();
    for(generator,row)in &graph {
        if !files.contains(generator){continue;}
        let mut targets=names(&row["writes"]);targets.extend(names(&config["implicit_solids"][generator]));
        if !targets.is_empty(){writes.insert(generator.clone(),targets);}
    }
    let mut output=Vec::new();
    for generators in together(&writes) {
        let program=generators.iter().find_map(|g|rows.get(g).and_then(|row|row.get("program")).cloned());
        if generators.iter().any(|generator| rows[generator].get("program") != program.as_ref()) {
            bail!("co-writers {} declare different native programs; each native producer must own its outputs", generators.join(", "));
        }
        let mut reads=BTreeSet::new();
        let mut rewritten=BTreeSet::new();let mut targets=BTreeSet::new();
        for generator in &generators {
            reads.extend(names(&graph[generator]["reads"]).intersection(&files).cloned());
            rewritten.extend(names(&graph[generator]["rewritten"]).intersection(&files).cloned());
            targets.extend(writes[generator].iter().cloned());
        }
        let(docs,solids):(Vec<_>,Vec<_>)=targets.into_iter().partition(|p|rewritten.contains(p));
        let mut made=json!({"solids":solids,"docs":docs,"reads":reads});
        if let Some(program)=program {made["program"]=program;}
        output.push(json!([generators,made]));
    }
    Ok(json!(output))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn native(reads: &[&str], writes: &[&str], rewritten: &[&str]) -> Value {
        json!({"reads": reads, "writes": writes, "rewritten": rewritten,
            "program": {"crate":"part", "name":"part", "sources":["part.rs"], "runtime_inputs":["Cargo.toml"]}})
    }

    #[test]
    fn native_inventory_preserves_program_and_authored_rewrites() {
        let graph = json!({"part.rs":native(&["part.rs", "Cargo.toml", "guide.md"], &["part.stl", "guide.md"], &["guide.md"])});
        let files = ["part.rs", "Cargo.toml", "guide.md"].map(str::to_owned).into();
        let result = inventory(Path::new("/absent"), &graph, files, &json!({})).unwrap();
        assert_eq!(result[0][1]["solids"], json!(["part.stl"]));
        assert_eq!(result[0][1]["docs"], json!(["guide.md"]));
        assert_eq!(result[0][1]["program"], graph["part.rs"]["program"]);
    }

    #[test]
    fn native_inventory_rejects_undeclared_programs() {
        let graph = json!({"part.rs":{"reads":[], "writes":["part.stl"], "rewritten":[]}});
        let error = inventory(Path::new("/absent"), &graph, ["part.rs".to_owned()].into(), &json!({})).unwrap_err();
        assert!(error.to_string().contains("no native program declaration"));
    }

    #[test]
    fn co_writers_share_their_inputs_and_outputs() {
        let graph = json!({
            "a.rs":native(&["a.rs"], &["shared.stl"], &[]),
            "b.rs":native(&["b.rs"], &["shared.stl", "b.stl"], &[])
        });
        let result = inventory(Path::new("/absent"), &graph, ["a.rs", "b.rs"].map(str::to_owned).into(), &json!({})).unwrap();
        assert_eq!(result.as_array().unwrap().len(), 1);
        assert_eq!(result[0][0], json!(["a.rs", "b.rs"]));
        assert_eq!(result[0][1]["solids"], json!(["b.stl", "shared.stl"]));
        assert_eq!(result[0][1]["reads"], json!(["a.rs", "b.rs"]));
    }

    #[test]
    fn differing_co_writer_programs_cannot_omit_a_producers_outputs() {
        let mut graph = json!({
            "a.rs":native(&["a.rs"], &["shared.stl"], &[]),
            "b.rs":native(&["b.rs"], &["shared.stl", "b.stl"], &[])
        });
        graph["b.rs"]["program"]["name"] = json!("other-producer");
        let error = inventory(Path::new("/absent"), &graph, ["a.rs", "b.rs"].map(str::to_owned).into(), &json!({})).unwrap_err();
        assert!(error.to_string().contains("different native programs"));
    }

    #[test]
    fn nul_listings_preserve_spaces_and_ignored_payload_paths() {
        struct Temporary(std::path::PathBuf);
        impl Drop for Temporary { fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); } }
        let directory = Path::new(env!("CARGO_MANIFEST_DIR")).join("../../../.cache/runs");
        let stamp = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos();
        let fixture = Temporary(directory.join(format!("inventory-path-fixture-{}-{stamp}", std::process::id())));
        fs::create_dir_all(fixture.0.join("hardware/nested")).unwrap();
        fs::write(fixture.0.join(".gitignore"), "*.scene.npz\n*.step.npz\n").unwrap();
        fs::write(fixture.0.join("part with spaces.rs"), "fn main() {}\n").unwrap();
        fs::write(fixture.0.join("hardware/nested/first.scene.npz"), "scene").unwrap();
        fs::write(fixture.0.join("hardware/second.step.npz"), "step").unwrap();
        for args in [vec!["init", "-q"], vec!["add", "--", ".gitignore", "part with spaces.rs"]] {
            assert!(Command::new("git").arg("-C").arg(&fixture.0).args(args).status().unwrap().success());
        }
        assert_eq!(git_paths(&fixture.0, &[]).unwrap(), [".gitignore", "part with spaces.rs"]);
        assert_eq!(git_paths(&fixture.0, &["--others", "--ignored", "--exclude-standard", "--", "hardware/*.step.npz", "hardware/*.scene.npz"]).unwrap(),
            ["hardware/nested/first.scene.npz", "hardware/second.step.npz"]);
    }
}
