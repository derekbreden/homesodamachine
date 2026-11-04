//! Published member source identities, Git index decoding and transitive inputs.
use anyhow::{Context,Result};
use serde::{Deserialize,Serialize};
use serde_json::{Value,json};
use sha2::{Digest,Sha256};
use std::{cell::RefCell,collections::{BTreeMap,BTreeSet},fs,path::{Path,PathBuf},process::Command,sync::atomic::{AtomicU64,Ordering}};

static NEXT_ID:AtomicU64=AtomicU64::new(1);
thread_local! {static IDENT_CACHE:RefCell<BTreeMap<u64,BTreeMap<String,String>>>=const{RefCell::new(BTreeMap::new())};}

fn ident(spec:&Value,id:u64,path:&str,writers:&BTreeMap<String,Vec<String>>)->Option<String> {
    if spec["kind"]=="committed" {
        return spec["index"].get(path).or_else(||spec["lines"].get(path)).and_then(Value::as_str).map(str::to_owned);
    }
    let tracked=spec["index"].get(path).is_some();
    if !tracked {
        if spec["lines"].get(path).is_some()||spec["members"].get(path).is_some() {
            return Some(spec["members"][path].as_str().unwrap_or("-").to_owned());
        }
        if writers.contains_key(path) {return None;}
    }
    if let Some(value)=IDENT_CACHE.with(|cache|cache.borrow().get(&id).and_then(|c|c.get(path)).cloned()) {return Some(value);}
    let value=blob_id(&Path::new(spec["root"].as_str().unwrap_or(".")).join(path));
    IDENT_CACHE.with(|cache|cache.borrow_mut().entry(id).or_default().insert(path.to_owned(),value.clone()));Some(value)
}

fn sha1(data:&[u8])->String {
    let mut bytes=data.to_vec();let bits=(bytes.len()as u64)*8;bytes.push(0x80);
    while bytes.len()%64!=56 {bytes.push(0);}bytes.extend(bits.to_be_bytes());
    let mut state=[0x67452301_u32,0xefcdab89,0x98badcfe,0x10325476,0xc3d2e1f0];
    for block in bytes.chunks_exact(64) {
        let mut w=[0_u32;80];for i in 0..16 {w[i]=u32::from_be_bytes(block[i*4..i*4+4].try_into().unwrap());}
        for i in 16..80 {w[i]=(w[i-3]^w[i-8]^w[i-14]^w[i-16]).rotate_left(1);}
        let [mut a,mut b,mut c,mut d,mut e]=state;
        for (i,&word) in w.iter().enumerate() {
            let(f,k)=match i {0..20=>((b&c)|(!b&d),0x5a827999),20..40=>(b^c^d,0x6ed9eba1),40..60=>((b&c)|(b&d)|(c&d),0x8f1bbcdc),_=>(b^c^d,0xca62c1d6)};
            let next=a.rotate_left(5).wrapping_add(f).wrapping_add(e).wrapping_add(k).wrapping_add(word);
            e=d;d=c;c=b.rotate_left(30);b=a;a=next;
        }
        for (held,value) in state.iter_mut().zip([a,b,c,d,e]) {*held=held.wrapping_add(value);}
    }
    state.into_iter().map(|value|format!("{value:08x}")).collect()
}

pub fn blob_id(path:&Path)->String {
    #[cfg(unix)] use std::os::unix::ffi::OsStrExt;
    let bytes=if path.is_symlink() {fs::read_link(path).map(|p|p.as_os_str().as_bytes().to_vec())} else {fs::read(path)};
    let Ok(bytes)=bytes else {return "-".into();};
    let mut data=format!("blob {}\0",bytes.len()).into_bytes();data.extend(bytes);sha1(&data)
}

pub fn git_dir(root:&Path)->PathBuf {
    let dot=root.join(".git");
    if dot.is_file() {if let Ok(text)=fs::read_to_string(&dot) {if let Some(path)=text.trim().strip_prefix("gitdir:") {
        let path=root.join(path.trim());return path.canonicalize().unwrap_or(path);
    }}}
    dot
}

pub fn read_index(data:&[u8])->Option<BTreeMap<String,String>> {
    if data.len()<32 || &data[..4]!=b"DIRC" {return None;}
    let uint=|start|->Option<u32>{Some(u32::from_be_bytes(data.get(start..start+4)?.try_into().ok()?))};
    let version=uint(4)?;let count=uint(8)?;
    if !matches!(version,2|3){return None;}
    let mut out=BTreeMap::new();let mut pos=12usize;let end=data.len()-20;
    for _ in 0..count {
        let mode=uint(pos+24)?;
        let flags=u16::from_be_bytes(data.get(pos+60..pos+62)?.try_into().ok()?);
        let head=if flags&0x4000!=0 {64} else {62};
        let stop=pos+head+data.get(pos+head..)?.iter().position(|&b|b==0)?;
        if stop>end || mode==0o040000 {return None;}
        if flags>>12&3==0 {
            let path=std::str::from_utf8(data.get(pos+head..stop)?).ok()?.to_owned();
            let digest=data.get(pos+40..pos+60)?.iter().map(|b|format!("{b:02x}")).collect();out.insert(path,digest);
        }
        pos+=(stop-pos+8)&!7;
    }
    while pos+8<=end {
        if matches!(data.get(pos..pos+4)?,b"link"|b"sdir") {return None;}
        pos=pos.checked_add(8+uint(pos+4)?as usize)?;
    }
    Some(out)
}

pub fn staged(root:&Path)->Result<BTreeMap<String,String>> {
    if let Ok(bytes)=fs::read(git_dir(root).join("index")) {if let Some(index)=read_index(&bytes) {return Ok(index);}}
    let listing=Command::new("git").arg("-C").arg(root).args(["--no-optional-locks","ls-files","--stage","-z"]).output()?;
    let mut out=BTreeMap::new();
    for row in listing.stdout.split(|&b|b==0) {
        let Some(tab)=row.iter().position(|&b|b==b'\t') else {continue;};
        let fields=row[..tab].split(|b|b.is_ascii_whitespace()).collect::<Vec<_>>();
        if fields.len()==3&&fields[2]==b"0" {out.insert(String::from_utf8(row[tab+1..].to_vec())?,String::from_utf8(fields[1].to_vec())?);}
    }
    Ok(out)
}

#[derive(Serialize,Deserialize)]
pub struct Graph {pub writers:BTreeMap<String,Vec<String>>,pub reads:BTreeMap<String,BTreeSet<String>>}

pub fn names(value:&Value)->BTreeSet<String>{value.as_array().map(|a|a.iter().filter_map(Value::as_str).map(str::to_owned).collect()).unwrap_or_default()}

impl Graph {
    pub fn new(graph:&Value,config:&Value)->Self {
        let mut graph=graph.as_object().cloned().unwrap_or_default();
        let mut order=config["generator_order"].as_array().map(|a|a.iter().filter_map(Value::as_str).map(str::to_owned).collect::<Vec<_>>()).unwrap_or_else(||graph.keys().cloned().collect());
        if let Some(source)=graph.remove("hardware/scripts/flute_payload.py") {
            order.retain(|name|name!="hardware/scripts/flute_payload.py");
            if let Some(wrappers)=config["flute_roots"].as_object() {for(wrapper,roots)in wrappers {
                let roots=names(roots);let trees=names(&config["flute_trees"]);let shared=names(&config["flute_shared"]);
                let mut row=serde_json::Map::new();
                for side in ["reads","writes","rewritten"] {
                    let values=source[side].as_array().map(|rows|rows.iter().filter(|p|p.as_str().is_some_and(|p| {
                        roots.iter().any(|root|p.starts_with(root))||(side=="reads"&&(shared.contains(p)||!trees.iter().any(|root|p.starts_with(root))))
                    })).cloned().collect::<Vec<_>>()).unwrap_or_default();row.insert(side.into(),json!(values));
                }
                graph.insert(wrapper.clone(),Value::Object(row));
                order.push(wrapper.clone());
            }}
        }
        let inert=|path:&str| {
            let path=path.to_lowercase();config["inert_suffixes"].as_array().is_some_and(|a|a.iter().filter_map(Value::as_str).any(|s|path.ends_with(s)))
                ||names(&config["inert_basenames"]).contains(path.rsplit('/').next().unwrap_or(""))
        };
        let mut out=Self {writers:BTreeMap::new(),reads:BTreeMap::new()};
        let mut visited=BTreeSet::new();
        for generator in order {
            if !visited.insert(generator.clone()){continue;}
            let Some(row)=graph.get(&generator) else {continue;};
            let mut writes=names(&row["writes"]);writes.extend(names(&config["implicit_solids"][&generator]));
            for path in &writes {out.writers.entry(path.clone()).or_default().push(generator.clone());}
            let mut reads=names(&row["reads"]).into_iter().filter(|p|!writes.contains(p)&&!inert(p)).collect::<BTreeSet<_>>();reads.insert(generator.clone());
            out.reads.insert(generator,reads);
        }
        out
    }
    pub fn inputs(&self,path:&str)->BTreeSet<String> {
        self.writers.get(path).into_iter().flatten().flat_map(|g|self.reads.get(g).into_iter().flatten()).cloned().collect()
    }
    pub fn digest(&self,path:&str,ident:&mut impl FnMut(&str)->Result<Option<String>>)->Result<String> {
        let mut lines=BTreeSet::new();let mut seen=BTreeSet::from([path.to_owned()]);let mut todo=self.inputs(path).into_iter().collect::<Vec<_>>();
        while let Some(path)=todo.pop() {
            if !seen.insert(path.clone()){continue;}
            let id=ident(&path)?;
            if id.is_none()&&self.writers.contains_key(&path) {todo.extend(self.inputs(&path));continue;}
            lines.insert(format!("{path}\t{}",id.as_deref().filter(|s|!s.is_empty()).unwrap_or("-")));
        }
        Ok(format!("{:x}",Sha256::digest(lines.into_iter().collect::<Vec<_>>().join("\n"))))
    }
}

pub fn dispatch(v:&Value,callback:&mut impl FnMut(Value)->Result<Value>)->Result<Option<Value>> {
    let text=|key:&str|v[key].as_str().with_context(||format!("{key} is text"));
    let result=match text("op")? {
        "artifact-index"=>json!(read_index(&serde_json::from_value::<Vec<u8>>(v["bytes"].clone())?)),
        "artifact-staged"=>json!(staged(Path::new(text("root")?))?),
        "artifact-git-dir"=>json!(git_dir(Path::new(text("root")?))),
        "artifact-blob"=>json!(blob_id(Path::new(text("path")?))),
        "artifact-graph"=>serde_json::to_value(Graph::new(&v["graph"],&v["config"]))?,
        "artifact-inputs"=>json!(serde_json::from_value::<Graph>(v["graph"].clone())?.inputs(text("path")?)),
        "artifact-identity-id"=>json!(NEXT_ID.fetch_add(1,Ordering::Relaxed)),
        "artifact-ident"=>json!(ident(&v["identity"],v["id"].as_u64().context("identity id")?,text("path")?,&serde_json::from_value(v["writers"].clone())?)),
        "artifact-digest"=>{
            let graph=serde_json::from_value::<Graph>(v["graph"].clone())?;
            json!(graph.digest(text("path")?,&mut |path| {
                if !v["identity"].is_null() {return Ok(ident(&v["identity"],v["id"].as_u64().context("identity id")?,path,&graph.writers));}
                let value=callback(json!({"op":"artifact-ident","path":path}))?;
                Ok(value.as_str().map(str::to_owned))
            })?)
        },
        _=>return Ok(None),
    };Ok(Some(result))
}
