//! Stage receipts retain current assembly work while its recipe, implementation and reads agree.
use anyhow::{Context, Result};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::io::{Read, Seek, SeekFrom};
use std::path::{Path, PathBuf};
use std::time::Instant;

pub struct Cache {
    root: PathBuf,
    persistent: PathBuf,
    work: PathBuf,
    implementation: String,
    reads: PathBuf,
    owned_reads: bool,
    fingerprints: BTreeMap<String, Value>,
    stages: Vec<Value>,
}

/// Concurrent requests for this assembly share its retained outputs under one file lease.
pub struct WorkLock {
    _file: std::fs::File,
}

fn work_lock(work: &Path, wait: bool) -> Result<Option<WorkLock>> {
    use std::os::fd::AsRawFd;
    unsafe extern "C" {
        fn flock(fd: i32, operation: i32) -> i32;
    }
    std::fs::create_dir_all(work)?;
    let file = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(work.join("work.lock"))?;
    let result = unsafe { flock(file.as_raw_fd(), if wait { 2 } else { 6 }) };
    if result != 0 {
        let error = std::io::Error::last_os_error();
        if !wait && error.kind() == std::io::ErrorKind::WouldBlock {
            return Ok(None);
        }
        return Err(error).context("locking retained assembly work");
    }
    Ok(Some(WorkLock { _file: file }))
}

pub fn lock(work: &Path) -> Result<WorkLock> {
    work_lock(work, true)?.context("retained assembly work lock")
}

/// Optional placement previews yield immediately when another producer owns the assembly work.
pub fn try_lock(work: &Path) -> Result<Option<WorkLock>> {
    work_lock(work, false)
}

fn digest_file(path: &Path) -> Result<String> {
    let mut file =
        std::fs::File::open(path).with_context(|| format!("reading {}", path.display()))?;
    let mut hash = Sha256::new();
    let mut bytes = [0u8; 65536];
    loop {
        let count = file.read(&mut bytes)?;
        if count == 0 {
            break;
        }
        hash.update(&bytes[..count]);
    }
    Ok(format!("{:x}", hash.finalize()))
}

fn identity(path: &Path) -> Result<Value> {
    use std::os::unix::fs::MetadataExt;
    let meta = std::fs::metadata(path)?;
    Ok(
        json!({"device":meta.dev(),"inode":meta.ino(),"bytes":meta.len(),
        "mtime":meta.mtime(),"mtime_ns":meta.mtime_nsec(),"ctime":meta.ctime(),"ctime_ns":meta.ctime_nsec()}),
    )
}

fn read_json(path: &Path) -> Option<Value> {
    serde_json::from_slice(&std::fs::read(path).ok()?).ok()
}

impl Cache {
    /// Runtime inputs remain rooted in the staged tree; retained work lives in the writable cache.
    pub fn new(root: &Path, work: &Path) -> Result<Self> {
        std::fs::create_dir_all(work)?;
        let (reads, owned_reads) = match std::env::var_os("HSM_READS") {
            Some(path) => (PathBuf::from(path), false),
            None => {
                let path = work.join(format!(".reads-{}.log", std::process::id()));
                std::fs::write(&path, "hsm-reads 1\n")?;
                // Initialization precedes the geometry workers that read this environment.
                unsafe {
                    std::env::set_var("HSM_READS", &path);
                }
                (path, true)
            }
        };
        if !reads.is_file() {
            std::fs::write(&reads, "hsm-reads 1\n")?;
        }
        hsm_kernel::reads::begin();
        let fingerprints: BTreeMap<String, Value> = read_json(&work.join("fingerprints.json"))
            .and_then(|value| serde_json::from_value(value).ok())
            .unwrap_or_default();
        let executable = std::env::current_exe()?;
        let key = "@executable".to_owned();
        let stamp = identity(&executable)?;
        let implementation = match fingerprints
            .get(&key)
            .filter(|record: &&Value| record["identity"] == stamp)
            .and_then(|record| record["sha256"].as_str())
        {
            Some(hash) => hash.to_owned(),
            None => digest_file(&executable)?,
        };
        let persistent = std::env::var_os("HSM_WORKSPACE")
            .map(PathBuf::from)
            .unwrap_or_else(|| root.to_owned())
            .join(".cache");
        let mut result = Self {
            root: root.to_owned(),
            persistent,
            work: work.to_owned(),
            implementation,
            reads,
            owned_reads,
            fingerprints,
            stages: vec![],
        };
        result.fingerprints.insert(
            key,
            json!({"identity":stamp,"sha256":result.implementation}),
        );
        Ok(result)
    }

    fn logical(&self, path: &Path) -> String {
        if path.starts_with(&self.persistent) {
            return path.to_string_lossy().into_owned();
        }
        path.strip_prefix(&self.root)
            .map(|relative| format!("@input/{}", relative.display()))
            .unwrap_or_else(|_| path.to_string_lossy().into_owned())
    }

    fn physical(&self, path: &str) -> PathBuf {
        path.strip_prefix("@input/")
            .map(|path| self.root.join(path))
            .unwrap_or_else(|| PathBuf::from(path))
    }

    fn map_paths(&self, value: &Value, storing: bool) -> Value {
        match value {
            Value::String(text) => {
                if storing && Path::new(text).is_absolute() {
                    json!(self.logical(Path::new(text)))
                } else if !storing && text.starts_with("@input/") {
                    json!(self.physical(text))
                } else {
                    value.clone()
                }
            }
            Value::Array(rows) => Value::Array(
                rows.iter()
                    .map(|row| self.map_paths(row, storing))
                    .collect(),
            ),
            Value::Object(fields) => Value::Object(
                fields
                    .iter()
                    .map(|(key, value)| (key.clone(), self.map_paths(value, storing)))
                    .collect(),
            ),
            _ => value.clone(),
        }
    }

    fn fingerprint(&mut self, path: &Path) -> Result<String> {
        let key = self.logical(path);
        let stamp = identity(path)?;
        if let Some(hash) = self
            .fingerprints
            .get(&key)
            .filter(|record| record["identity"] == stamp)
            .and_then(|record| record["sha256"].as_str())
        {
            return Ok(hash.to_owned());
        }
        let hash = digest_file(path)?;
        self.fingerprints
            .insert(key, json!({"identity":stamp,"sha256":hash}));
        Ok(hash)
    }

    /// Read tracking reuses a digest while the file's filesystem identity is unchanged.
    pub fn input_digest(&mut self, path: &Path) -> Result<String> {
        let hash = self.fingerprint(path)?;
        hsm_kernel::reads::digest(path, &hash);
        Ok(hash)
    }

    pub fn implementation(&self) -> &str {
        &self.implementation
    }

    fn agrees(&mut self, records: &Value) -> bool {
        records.as_object().is_some_and(|records| {
            records.iter().all(|(path, expected)| {
                self.fingerprint(&self.physical(path)).ok().as_deref() == expected.as_str()
            })
        })
    }

    fn record_path(&self, name: &str) -> PathBuf {
        let name = format!("{:x}", Sha256::digest(name.as_bytes()));
        self.work.join("receipts").join(format!("{name}.json"))
    }

    /// The preceding value is available to progressive placement without claiming it is current.
    pub fn previous(&self, name: &str) -> Option<Value> {
        read_json(&self.record_path(name)).map(|record| self.map_paths(&record["value"], false))
    }

    /// A placement-only request uses retained prerequisites and never constructs a missing stage.
    pub fn try_reuse(
        &mut self,
        name: &str,
        recipe: &Value,
        outputs: &[PathBuf],
    ) -> Result<Option<Value>> {
        let started = Instant::now();
        let recipe = self.map_paths(recipe, true);
        let key = format!("{:x}", Sha256::digest(serde_json::to_vec(&recipe)?));
        let path = self.record_path(name);
        if let Some(record) = read_json(&path).filter(|record| {
            record["implementation"] == self.implementation && record["recipe"] == key
        }) {
            if self.agrees(&record["reads"])
                && self.agrees(&record["outputs"])
                && outputs
                    .iter()
                    .all(|file| record["outputs"].get(self.logical(file)).is_some())
            {
                for (path, hash) in record["reads"].as_object().into_iter().flatten() {
                    hsm_kernel::reads::digest(&self.physical(path), hash.as_str().unwrap());
                }
                self.stages.push(
                    json!({"stage":name,"reused":true,"seconds":started.elapsed().as_secs_f64()}),
                );
                return Ok(Some(self.map_paths(&record["value"], false)));
            }
        }
        Ok(None)
    }

    /// Reuse a stage only while its actual inputs and retained outputs still hold their bytes.
    pub fn run(
        &mut self,
        name: &str,
        recipe: &Value,
        outputs: &[PathBuf],
        make: impl FnOnce() -> Result<Value>,
    ) -> Result<Value> {
        let started = Instant::now();
        if let Some(value) = self.try_reuse(name, recipe, outputs)? {
            return Ok(value);
        }
        let recipe = self.map_paths(recipe, true);
        let key = format!("{:x}", Sha256::digest(serde_json::to_vec(&recipe)?));
        let path = self.record_path(name);
        let offset = std::fs::metadata(&self.reads)
            .map(|meta| meta.len())
            .unwrap_or(0);
        let result = make().with_context(|| format!("installed-machine stage {name}"))?;
        let mut file = std::fs::File::open(&self.reads)?;
        file.seek(SeekFrom::Start(offset))?;
        let mut lines = String::new();
        file.read_to_string(&mut lines)?;
        let mut reads = serde_json::Map::new();
        let mut stable = true;
        for line in lines.lines() {
            let Some((path, hash)) = line.split_once('\t') else {
                continue;
            };
            let path = self.logical(Path::new(path));
            if let Some(previous) = reads.insert(path, json!(hash)) {
                stable &= previous == hash;
            }
        }
        let mut files = serde_json::Map::new();
        for output in outputs {
            files.insert(self.logical(output), json!(self.fingerprint(output)?));
        }
        stable &= self.agrees(&Value::Object(reads.clone()));
        if stable {
            let record = json!({"purpose":"This receipt reuses a completed stage while its inputs and outputs agree.",
                "implementation":self.implementation,"recipe":key,"reads":reads,"outputs":files,
                "value":self.map_paths(&result,true)});
            hsm_model_export::put(&path, &serde_json::to_vec(&record)?)?;
        }
        self.stages.push(json!({"stage":name,"reused":false,"seconds":started.elapsed().as_secs_f64(),"retained":stable}));
        Ok(result)
    }
}

impl Drop for Cache {
    fn drop(&mut self) {
        if let Ok(bytes) = serde_json::to_vec(&self.fingerprints) {
            let _ = hsm_model_export::put(&self.work.join("fingerprints.json"), &bytes);
        }
        let record = json!({"purpose":"This record separates reused and executed assembly stages.","stages":self.stages});
        if let Ok(bytes) = serde_json::to_vec_pretty(&record) {
            let _ = hsm_model_export::put(&self.work.join("last-run.json"), &bytes);
        }
        if self.owned_reads {
            let _ = std::fs::remove_file(&self.reads);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;
    use std::io::Write;

    #[test]
    fn optional_preview_yields_to_an_existing_work_lease() -> Result<()> {
        let dir = std::env::temp_dir().join(format!(
            "hsm-assembly-lock-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_nanos()
        ));
        let held = lock(&dir)?;
        assert!(try_lock(&dir)?.is_none());
        drop(held);
        assert!(try_lock(&dir)?.is_some());
        std::fs::remove_dir_all(dir)?;
        Ok(())
    }

    #[test]
    fn staged_roots_rebind_and_changed_inputs_or_outputs_rebuild() -> Result<()> {
        let base = std::env::temp_dir().join(format!(
            "hsm-stage-cache-{}-{}",
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_nanos()
        ));
        let first = base.join("first");
        let second = base.join("second");
        let work = base.join("retained");
        for dir in [&first, &second, &work] {
            std::fs::create_dir_all(dir)?;
        }
        for dir in [&first, &second] {
            std::fs::write(dir.join("input.json"), "first")?;
        }
        let log = base.join("reads.log");
        std::fs::write(&log, "")?;
        let output = work.join("output.json");
        let make_cache = |root: &Path| Cache {
            root: root.to_owned(),
            persistent: work.clone(),
            work: work.clone(),
            implementation: "fixture".into(),
            reads: log.clone(),
            owned_reads: false,
            fingerprints: BTreeMap::new(),
            stages: vec![],
        };
        let calls = Cell::new(0);
        let make = |root: &Path| -> Result<Value> {
            calls.set(calls.get() + 1);
            let input = root.join("input.json");
            let bytes = std::fs::read(&input)?;
            let line = format!("{}\t{:x}\n", input.display(), Sha256::digest(&bytes));
            std::fs::OpenOptions::new()
                .append(true)
                .open(&log)?
                .write_all(line.as_bytes())?;
            std::fs::write(&output, &bytes)?;
            Ok(json!({"input":input,"text":String::from_utf8(bytes)?}))
        };
        let mut cache = make_cache(&first);
        cache.run(
            "stage",
            &json!({"input":first.join("input.json")}),
            &[output.clone()],
            || make(&first),
        )?;
        drop(cache);
        let mut cache = make_cache(&second);
        let recipe = json!({"input":second.join("input.json")});
        let value = cache.run("stage", &recipe, &[output.clone()], || make(&second))?;
        assert_eq!(calls.get(), 1);
        assert_eq!(value["input"], json!(second.join("input.json")));
        std::fs::write(second.join("input.json"), "second")?;
        let value = cache.run("stage", &recipe, &[output.clone()], || make(&second))?;
        assert_eq!(calls.get(), 2);
        assert_eq!(value["text"], "second");
        std::fs::write(&output, "external change")?;
        cache.run("stage", &recipe, &[output.clone()], || make(&second))?;
        assert_eq!(calls.get(), 3);
        std::fs::remove_file(&output)?;
        cache.run("stage", &recipe, &[output.clone()], || make(&second))?;
        assert_eq!(calls.get(), 4);
        drop(cache);
        std::fs::remove_dir_all(base)?;
        Ok(())
    }
}
