//! Stat-bound artifact digests and settled directory listings.
use anyhow::{Context,Result,bail};
use serde_json::{Value,json};
use std::{cell::RefCell,collections::{BTreeMap,BTreeSet},fs::{self,OpenOptions},io::Write,
    os::unix::fs::{MetadataExt,OpenOptionsExt},path::{Path,PathBuf},sync::atomic::{AtomicU64,Ordering},time::{SystemTime,UNIX_EPOCH}};
use crate::payload;

const SETTLED_NS:i64=2_000_000_000;
static NEXT:AtomicU64=AtomicU64::new(1);
thread_local! {static CACHES:RefCell<BTreeMap<u64,Cache>>=const{RefCell::new(BTreeMap::new())};}

pub fn identity(path:&Path)->Result<[i64;5]> {
    let s=path.metadata()?;
    Ok([s.dev() as i64,s.ino()as i64,s.len()as i64,s.mtime()*1_000_000_000+s.mtime_nsec(),s.ctime()*1_000_000_000+s.ctime_nsec()])
}
pub fn load(path:&Path)->Value {
    fs::read(path).ok().and_then(|bytes|serde_json::from_slice::<Value>(&bytes).ok()).filter(Value::is_object).unwrap_or_else(||json!({}))
}
pub fn save(path:&Path,entries:&Value)->Result<()> {
    let parent=path.parent().context("artifact cache parent")?;fs::create_dir_all(parent)?;
    let temporary=parent.join(format!(".{}-{}-{}",path.file_stem().unwrap_or_default().to_string_lossy(),std::process::id(),NEXT.fetch_add(1,Ordering::Relaxed)));
    let result=(||->Result<()> {
        let mut file=OpenOptions::new().create_new(true).write(true).mode(0o600).open(&temporary)?;
        file.write_all(payload::ascii_json(&serde_json::to_string(entries)?).as_bytes())?;
        drop(file);fs::rename(&temporary,path)?;Ok(())
    })();let _=fs::remove_file(temporary);result
}

pub struct Cache {root:PathBuf,path:PathBuf,pub entries:Value,pub dirty:bool,read:BTreeSet<String>,listings:bool}
impl Cache {
    pub fn new(root:&Path,listings:bool)->Self {
        let path=root.join(if listings {".cache/cad-artifact-listings.json"} else {".cache/cad-artifact-digests.json"});
        Self {root:root.into(),entries:load(&path),path,dirty:false,read:BTreeSet::new(),listings}
    }
    pub fn digest(&mut self,relative:&str)->Result<String> {
        let path=self.root.join(relative);let mut before=identity(&path)?;
        if let Some(held)=self.entries[relative].as_array() {
            if held.len()==2 && held[0]==json!(before) && held[1].as_str().is_some_and(|s|s.len()==64) {return Ok(held[1].as_str().unwrap().into());}
        }
        for _ in 0..3 {
            let digest=payload::digest(&path)?;let after=identity(&path)?;
            if before==after {self.entries[relative]=json!([after,digest]);self.dirty=true;return Ok(digest);}
            before=after;
        }
        bail!("artifact kept changing while hashing: {}",path.display())
    }
    pub fn listing(&mut self,relative:&str)->Result<Option<(Vec<String>,Vec<String>)>> {
        let path=self.root.join(relative);
        let result=(||->Result<_> {
            let before=identity(&path)?;
            if let Some(held)=self.entries[relative].as_array() {
                if held.len()==3 && held[0]==json!(before) {
                    self.read.insert(relative.into());
                    return Ok(Some((serde_json::from_value(held[1].clone())?,serde_json::from_value(held[2].clone())?)));
                }
            }
            let(mut dirs,mut files)=(Vec::new(),Vec::new());
            for entry in fs::read_dir(&path)? {let entry=entry?;let kind=entry.file_type()?;
                if kind.is_dir(){dirs.push(entry.file_name().to_string_lossy().into_owned());}
                else if kind.is_file(){files.push(entry.file_name().to_string_lossy().into_owned());}}
            let after=identity(&path)?;let now=SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos()as i64;
            if before==after && now-after[4]>SETTLED_NS {
                self.entries[relative]=json!([after,dirs,files]);self.read.insert(relative.into());self.dirty=true;
            }
            Ok(Some((dirs,files)))
        })();
        // The historical listing reader treats every filesystem read failure as
        // an absent directory. Invalid retained JSON remains a visible error.
        match result {Err(error) if error.downcast_ref::<std::io::Error>().is_some()=>Ok(None),other=>other}
    }
    pub fn save(&mut self)->Result<()> {
        if self.listings {
            let keys=self.entries.as_object().unwrap().keys().cloned().collect::<BTreeSet<_>>();
            if self.dirty || self.read!=keys {
                let entries:serde_json::Map<_,_>=self.read.iter().filter_map(|name|self.entries.get(name).map(|v|(name.clone(),v.clone()))).collect();
                save(&self.path,&Value::Object(entries))?;self.dirty=false;
            }
        } else if self.dirty {save(&self.path,&self.entries)?;self.dirty=false;}
        Ok(())
    }
}
pub fn hashes(root:&Path,paths:&[String])->Result<BTreeMap<String,String>> {
    let mut cache=Cache::new(root,false);let mut result=BTreeMap::new();
    for path in paths {result.insert(path.clone(),cache.digest(path)?);}cache.save()?;Ok(result)
}

pub fn dispatch(v:&Value)->Result<Option<Value>> {
    let text=|key:&str|v[key].as_str().with_context(||format!("{key} is text"));
    let result=match text("op")? {
        "artifact-stat"=>json!(identity(Path::new(text("path")?))?),
        "artifact-cache-load"=>load(Path::new(text("path")?)),
        "artifact-cache-save-file"=>{save(Path::new(text("path")?),&v["entries"])?;Value::Null},
        "artifact-hashes"=>json!(hashes(Path::new(text("root")?),&serde_json::from_value::<Vec<String>>(v["paths"].clone())?)?),
        "artifact-cache-new"=>{
            let id=NEXT.fetch_add(1,Ordering::Relaxed);let cache=Cache::new(Path::new(text("root")?),v["listings"]==true);
            CACHES.with(|caches|caches.borrow_mut().insert(id,cache));json!(id)
        },
        "artifact-cache-get"|"artifact-cache-digest"|"artifact-cache-listing"|"artifact-cache-save"=>{
            let id=v["id"].as_u64().context("cache identity")?;
            CACHES.with(|caches|->Result<Value>{
                let mut caches=caches.borrow_mut();let cache=caches.get_mut(&id).context("known artifact cache")?;
                match text("op")? {
                    "artifact-cache-get"=>Ok(json!({"entries":cache.entries,"dirty":cache.dirty,"read":cache.read})),
                    "artifact-cache-digest"=>Ok(json!(cache.digest(text("path")?)?)),
                    "artifact-cache-listing"=>Ok(json!(cache.listing(text("path")?)?)),
                    _=>{cache.save()?;Ok(Value::Null)},
                }
            })?
        },
        _=>return Ok(None),
    };Ok(Some(result))
}
