//! A compiled program's sources from Cargo's dep-info, and the manifests that configure them.
use anyhow::Result;
use std::{collections::BTreeSet,fs,path::{Path,PathBuf}};

pub fn compiled(dep_info:&Path,workspace:&Path)->Result<Vec<String>> {
    let text=fs::read_to_string(dep_info)?;
    let rule=text.split("\n\n").next().unwrap_or("").replace("\\\n"," ");
    let deps=rule.split_once(": ").map(|(_,deps)|deps).unwrap_or("");
    let mut out=BTreeSet::new();
    for dep in deps.replace("\\ ","\0").split_whitespace() {
        let path=PathBuf::from(dep.replace('\0'," "));
        let path=path.canonicalize().unwrap_or(path);
        if let Ok(relative)=path.strip_prefix(workspace) {out.insert(relative.to_string_lossy().into_owned());}
    }
    Ok(out.into_iter().collect())
}

pub fn manifests(sources:&[String],krate:&str,workspace:&Path)->Vec<String> {
    let mut out:BTreeSet<_>=["tools/hsm/cargo-config.json".into(),format!("tools/hsm/{krate}/Cargo.toml")].into();
    for source in sources {
        let parts:Vec<_>=source.split('/').collect();
        if parts.len()<4 || parts[..2]!=["tools","hsm"] {continue;}
        for n in (3..parts.len()).rev() {
            let manifest=format!("{}/Cargo.toml",parts[..n].join("/"));
            if workspace.join(&manifest).is_file() {out.insert(manifest);break;}
        }
    }
    out.into_iter().collect()
}
