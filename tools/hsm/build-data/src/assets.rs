//! Adopt only a frozen fine payload bound to its source and kernel budget.
use anyhow::{Context,Result};
use serde_json::{Value,json};
use std::{fs,path::Path};
use crate::payload;

pub fn step_input(path:&Path,root:&Path,workspace:&Path,linear:f64,angular:f64)->Result<Value> {
    let path=path.canonicalize()?;
    let name=path.strip_prefix(root.canonicalize()?)?.to_string_lossy().into_owned();
    let data=fs::read(&path)?;
    let digest=payload::digest(&path)?;
    let mut reads=vec![path.to_string_lossy().into_owned()];
    if data[..data.len().min(200)].windows(b"meshcad tessellated".len()).any(|w|w==b"meshcad tessellated") {
        let beside=path.with_file_name(format!("{}.mesh",path.file_name().unwrap().to_string_lossy()));
        let source=payload::header(&beside).ok().and_then(|h|h["src"].as_str().map(str::to_owned));
        anyhow::ensure!(source.as_deref()==Some(digest.as_str()),"_rust_part: {name} is triangles, and the payload beside it was not cut from it; its own generator cuts both");
        reads.push(beside.to_string_lossy().into_owned());
        return Ok(json!({"name":name,"reads":reads,"tessellate":false}));
    }
    let cached=workspace.join(".cache/hsm/import").join(format!("{digest}.step.mesh"));
    let adopted=adopt(&path,&cached,&digest,linear,angular)?;
    reads.extend(adopted["reads"].as_array().unwrap().iter().filter_map(Value::as_str).map(str::to_owned));
    Ok(json!({"name":name,"reads":reads,"tessellate":adopted["adopted"]!=true && !cached.is_file(),"cached":cached,"digest":digest}))
}

pub fn adopt(path:&Path,out:&Path,digest:&str,linear:f64,angular:f64)->Result<Value> {
    let parent=path.parent().context("asset has a parent directory")?;
    let manifest=parent.join("frozen-asset.json");
    let mut reads=Vec::new();
    if !manifest.is_file() {return Ok(json!({"adopted":false,"reads":reads}));}
    reads.push(manifest.to_string_lossy().into_owned());
    let load=||->Option<(std::path::PathBuf,Vec<u8>,String)> {
        let record:Value=serde_json::from_slice(&fs::read(&manifest).ok()?).ok()?;
        let fine=record["fine_payload"].as_object()?;
        let members=record["members"].as_object()?;
        let name=path.file_name()?.to_str()?;
        if fine.get("source_step_sha256")?.as_str()!=Some(digest)||members.get(name)?.as_str()!=Some(digest) {return None;}
        for (key,budget) in [("linear_mm",linear),("angular_rad",angular)] {
            let value=fine.get(key)?.as_f64()?;
            if !(value>0. && value<=budget) {return None;}
        }
        let member=fine.get("path")?.as_str()?;
        let expected=fine.get("sha256")?.as_str()?;
        if members.get(member)?.as_str()!=Some(expected) {return None;}
        let target=parent.join(member).canonicalize().ok()?;
        if !target.starts_with(parent.canonicalize().ok()?) {return None;}
        let data=fs::read(&target).ok()?;
        if payload::digest(&target).ok()?.as_str()!=expected {return None;}
        let header=payload::header(&target).ok()?;
        if header["v"]!=3||header["src"].as_str()!=Some(digest)||header["meshes"].as_array()?.is_empty() {return None;}
        Some((target,data,expected.to_owned()))
    };
    let Some((payload,data,expected))=load() else {return Ok(json!({"adopted":false,"reads":reads}));};
    reads.push(payload.to_string_lossy().into_owned());
    if payload::digest(out).ok().as_deref()!=Some(expected.as_str()) {
        let install=||->Result<()> {
            fs::create_dir_all(out.parent().context("import cache parent")?)?;
            let temporary=out.with_file_name(format!(".{}.{}",out.file_name().unwrap_or_default().to_string_lossy(),std::process::id()));
            fs::write(&temporary,&data)?;fs::rename(&temporary,out)?;Ok(())
        };
        install().with_context(||format!("_rust_part: could not install verified fine payload for {}",path.display()))?;
    }
    Ok(json!({"adopted":true,"reads":reads}))
}
