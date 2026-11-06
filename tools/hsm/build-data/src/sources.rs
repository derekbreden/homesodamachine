//! Source-closure selection and the build's compact content digests.
use anyhow::{Context,Result};
use serde_json::{Value,json};
use std::{collections::{BTreeSet,HashMap},fs,path::{Path,PathBuf},sync::{Mutex,OnceLock},time::UNIX_EPOCH};

const IV:[u64;8]=[0x6a09e667f3bcc908,0xbb67ae8584caa73b,0x3c6ef372fe94f82b,0xa54ff53a5f1d36f1,
    0x510e527fade682d1,0x9b05688c2b3e6c1f,0x1f83d9abfb41bd6b,0x5be0cd19137e2179];
const SIGMA:[[usize;16];12]=[
    [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    [14,10,4,8,9,15,13,6,1,12,0,2,11,7,5,3],
    [11,8,12,0,5,2,15,13,10,14,3,6,7,1,9,4],
    [7,9,3,1,13,12,11,14,2,6,5,10,4,0,15,8],
    [9,0,5,7,2,4,10,15,14,1,11,12,6,8,3,13],
    [2,12,6,10,0,11,8,3,4,13,7,5,15,14,1,9],
    [12,5,1,15,14,13,4,10,0,7,6,3,9,2,8,11],
    [13,11,7,14,12,1,3,9,5,0,15,4,8,6,2,10],
    [6,15,14,9,11,3,0,8,12,2,13,7,1,4,10,5],
    [10,2,8,4,7,6,1,5,15,11,9,14,3,12,13,0],
    [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
    [14,10,4,8,9,15,13,6,1,12,0,2,11,7,5,3]];

pub fn blake2b16(data:&[u8])->String {
    fn g(v:&mut [u64;16],a:usize,b:usize,c:usize,d:usize,x:u64,y:u64) {
        v[a]=v[a].wrapping_add(v[b]).wrapping_add(x);v[d]=(v[d]^v[a]).rotate_right(32);
        v[c]=v[c].wrapping_add(v[d]);v[b]=(v[b]^v[c]).rotate_right(24);
        v[a]=v[a].wrapping_add(v[b]).wrapping_add(y);v[d]=(v[d]^v[a]).rotate_right(16);
        v[c]=v[c].wrapping_add(v[d]);v[b]=(v[b]^v[c]).rotate_right(63);
    }
    fn block(h:&mut [u64;8],data:&[u8],count:u128,last:bool) {
        let mut bytes=[0;128];bytes[..data.len()].copy_from_slice(data);
        let m:[u64;16]=std::array::from_fn(|i|u64::from_le_bytes(bytes[i*8..i*8+8].try_into().unwrap()));
        let mut v=[0;16];v[..8].copy_from_slice(h);v[8..].copy_from_slice(&IV);
        v[12]^=count as u64;v[13]^=(count>>64)as u64;if last {v[14]=!v[14];}
        for s in SIGMA {
            g(&mut v,0,4,8,12,m[s[0]],m[s[1]]);g(&mut v,1,5,9,13,m[s[2]],m[s[3]]);
            g(&mut v,2,6,10,14,m[s[4]],m[s[5]]);g(&mut v,3,7,11,15,m[s[6]],m[s[7]]);
            g(&mut v,0,5,10,15,m[s[8]],m[s[9]]);g(&mut v,1,6,11,12,m[s[10]],m[s[11]]);
            g(&mut v,2,7,8,13,m[s[12]],m[s[13]]);g(&mut v,3,4,9,14,m[s[14]],m[s[15]]);
        }
        for i in 0..8 {h[i]^=v[i]^v[i+8];}
    }
    let mut h=IV;h[0]^=0x01010010;let mut rest=data;let mut count=0;
    while rest.len()>128 {count+=128;block(&mut h,&rest[..128],count,false);rest=&rest[128..];}
    count+=rest.len() as u128;block(&mut h,rest,count,true);
    h[..2].iter().flat_map(|v|v.to_le_bytes()).map(|b|format!("{b:02x}")).collect()
}

type Stamp=(u128,u64);
fn stamp(path:&Path)->Option<Stamp> {let m=path.metadata().ok()?;Some((m.modified().ok()?.duration_since(UNIX_EPOCH).ok()?.as_nanos(),m.len()))}
type Cache=HashMap<PathBuf,(Stamp,Value)>;
static PARSED:OnceLock<Mutex<Cache>>=OnceLock::new();

fn parsed(path:&Path,callback:&mut impl FnMut(Value)->Result<Value>)->Result<Option<Value>> {
    let Some(stamp)=stamp(path) else {return Ok(None);};
    let cache=PARSED.get_or_init(Default::default);
    if let Some((held,value))=cache.lock().unwrap().get(path) {if *held==stamp {return Ok(Some(value.clone()));}}
    let Ok(raw)=fs::read(path) else {return Ok(None);};
    // The Python standard-library parser supplies its AST object and canonical
    // dump; source selection, closure walking, file reads and hashing are native.
    let parsed=callback(json!({"op":"parse-source","bytes":raw}))?;
    let form=parsed["dump"].as_str().map(|s|s.as_bytes()).unwrap_or(&raw);
    let value=json!({"digest":blake2b16(form),"tree":parsed["tree"]});
    cache.lock().unwrap().insert(path.into(),(stamp,value.clone()));
    Ok(Some(value))
}

pub fn code_digest(path:&Path,callback:&mut impl FnMut(Value)->Result<Value>)->Result<Option<String>> {
    Ok(parsed(path,callback)?.and_then(|v|v["digest"].as_str().map(str::to_owned)))
}

pub fn digest(paths:&[PathBuf],callback:&mut impl FnMut(Value)->Result<Value>)->Result<String> {
    let mut input=Vec::new();
    for path in paths {input.extend(code_digest(path,callback)?.unwrap_or_default().as_bytes());}
    Ok(blake2b16(&input))
}

fn imported(tree:&Value)->BTreeSet<String> {
    fn visit(value:&Value,out:&mut BTreeSet<String>) {
        if let Some(nodes)=value.as_array() {for node in nodes {visit(node,out);}return;}
        let Some(fields)=value.as_object() else {return;};
        match fields.get("_ast_type").and_then(Value::as_str).unwrap_or("") {
            "Import"=> {if let Some(names)=value["names"].as_array() {for alias in names {if let Some(name)=alias["name"].as_str(){out.insert(name.into());}}}},
            "ImportFrom" if value["level"]==0=>{
                if let Some(module)=value["module"].as_str() {
                    out.insert(module.into());
                    if let Some(names)=value["names"].as_array() {for alias in names {if let Some(name)=alias["name"].as_str(){out.insert(format!("{module}.{name}"));}}}
                }
            },
            _=>{},
        }
        for field in fields.values() {visit(field,out);}
    }
    let mut out=BTreeSet::new();
    if let Some(body)=tree["body"].as_array() {for top in body {
        if matches!(top["_ast_type"].as_str(),Some("FunctionDef"|"AsyncFunctionDef"))
            && matches!(top["name"].as_str(),Some("main"|"selftest"|"machine_of")) {continue;}
        visit(top,&mut out);
    }}
    out
}

pub fn source_files(root:&Path,start:&Path,callback:&mut impl FnMut(Value)->Result<Value>)->Result<Vec<PathBuf>> {
    let root=root.canonicalize()?;
    let mut seen=BTreeSet::new();let mut queue=vec![start.canonicalize().unwrap_or_else(|_|start.into())];
    while let Some(path)=queue.pop() {
        if !seen.insert(path.clone()) {continue;}
        let Some(parsed)=parsed(&path,callback)? else {continue;};
        for module in imported(&parsed["tree"]) {
            let candidate=callback(json!({"op":"resolve-module","name":module}))?;
            let Some(candidate)=candidate.as_str() else {continue;};
            let candidate=Path::new(candidate).canonicalize().context("resolved source module")?;
            if candidate.starts_with(&root) && candidate.extension().is_some_and(|e|e=="py")
                && !candidate.components().any(|part|part.as_os_str()=="site-packages") {queue.push(candidate);}
        }
    }
    Ok(seen.into_iter().collect())
}

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
