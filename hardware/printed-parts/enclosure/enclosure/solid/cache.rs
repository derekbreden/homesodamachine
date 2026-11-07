//! Retained construction stages reuse exact solids while their operation, inputs and engine agree.
use anyhow::Result;
use hsm_kernel::{Body, Solid};
use sha2::{Digest, Sha256};
use std::{
    fs,
    path::{Path, PathBuf},
    sync::atomic::{AtomicU64, Ordering},
    time::Instant,
};

const IMPLEMENTATION: &str = env!("HSM_STAGE_IMPLEMENTATION");
include!(concat!(env!("OUT_DIR"), "/stage_inputs.rs"));
const BUILD_SOURCE: &[u8] = include_bytes!(concat!(env!("CARGO_MANIFEST_DIR"), "/build.rs"));
const LIMIT: u64 = 2 * 1024 * 1024 * 1024;
static NEXT: AtomicU64 = AtomicU64::new(0);

pub struct Cache {
    directory: Option<PathBuf>,
    pub hits: usize,
    pub stored: usize,
    pub bytes_read: u64,
    pub bytes_written: u64,
    pub io_seconds: f64,
    swept: bool,
}

impl Cache {
    pub fn new() -> Self {
        let directory = if std::env::var_os("HSM_STAGE_CACHE_OFF").is_some() {
            None
        } else {
            Some(
                std::env::var_os("HSM_STAGE_CACHE_DIR")
                    .map(PathBuf::from)
                    .unwrap_or_else(|| {
                        std::env::var_os("HSM_WORKSPACE")
                            .map(PathBuf::from)
                            .unwrap_or_else(|| {
                                Path::new(env!("CARGO_MANIFEST_DIR"))
                                    .ancestors()
                                    .nth(3)
                                    .unwrap()
                                    .to_path_buf()
                            })
                            .join(".cache/realized/rust-stages")
                    }),
            )
        };
        Self {
            directory,
            hits: 0,
            stored: 0,
            bytes_read: 0,
            bytes_written: 0,
            io_seconds: 0.0,
            swept: false,
        }
    }

    pub fn key(operation: &[u8], inputs: &[&str]) -> String {
        let mut hash = Sha256::new();
        hash.update(IMPLEMENTATION);
        hash.update(BUILD_SOURCE);
        hash.update((operation.len() as u64).to_le_bytes());
        hash.update(operation);
        for input in inputs {
            hash.update(input.as_bytes());
        }
        format!("{:x}", hash.finalize())
    }

    pub fn load(&mut self, key: &str) -> Option<Solid> {
        let path = self.directory.as_ref()?.join(format!("{key}.npz"));
        let start = Instant::now();
        let result = (|| {
            let bytes = fs::read(&path).ok()?;
            let solid = hsm_kernel::import::model_bodies(&bytes).ok()?.pop()?.solid;
            self.bytes_read += bytes.len() as u64;
            Some(solid)
        })();
        self.io_seconds += start.elapsed().as_secs_f64();
        if result.is_some() {
            self.hits += 1;
        }
        result
    }

    pub fn save(&mut self, key: &str, solid: &Solid) {
        let Some(directory) = self.directory.clone() else {
            return;
        };
        let start = Instant::now();
        let result = (|| -> Result<()> {
            fs::create_dir_all(&directory)?;
            if !self.swept {
                sweep(&directory, LIMIT)?;
                self.swept = true;
            }
            let bytes = hsm_kernel::model_bytes(&[Body {
                name: "stage",
                color: None,
                solid,
            }]);
            let final_path = directory.join(format!("{key}.npz"));
            let temporary = directory.join(format!(
                ".{}-{}.npz",
                std::process::id(),
                NEXT.fetch_add(1, Ordering::Relaxed)
            ));
            fs::write(&temporary, &bytes)?;
            fs::rename(&temporary, &final_path)?;
            self.bytes_written += bytes.len() as u64;
            self.stored += 1;
            Ok(())
        })();
        self.io_seconds += start.elapsed().as_secs_f64();
        let _ = result;
    }
}

/// A materialized stage takes its explicit solid, values and caller's implementation.
pub fn retained(
    name: &str,
    code: &[u8],
    input: &Solid,
    parameters: &impl serde::Serialize,
    make: impl FnOnce() -> Result<Solid>,
) -> Result<Solid> {
    let started = Instant::now();
    let mut cache = Cache::new();
    if cache.directory.is_none() {
        return phase(name, make);
    }
    let source = hsm_kernel::model_bytes(&[Body {
        name: "input",
        color: None,
        solid: input,
    }]);
    let input = format!("{:x}", Sha256::digest(source));
    let operation = serde_json::json!({"stage":name,"code":format!("{:x}",Sha256::digest(code)),"parameters":parameters});
    let key = Cache::key(&serde_json::to_vec(&operation)?, &[&input]);
    let result = if let Some(solid) = cache.load(&key) {
        solid
    } else {
        let solid = make()?;
        cache.save(&key, &solid);
        solid
    };
    record(
        serde_json::json!({"stage":name,"seconds":started.elapsed().as_secs_f64(),"reused":cache.hits,
        "cache_io_seconds":cache.io_seconds,"bytes_read":cache.bytes_read,"bytes_written":cache.bytes_written}),
    );
    Ok(result)
}

/// Requested phase measurements keep geometry, finish and export time distinguishable.
pub fn phase<T>(name: &str, make: impl FnOnce() -> Result<T>) -> Result<T> {
    if std::env::var_os("HSM_PHASE_PROFILE").is_none() {
        return make();
    }
    let started = Instant::now();
    let result = make();
    record(
        serde_json::json!({"stage":name,"seconds":started.elapsed().as_secs_f64(),"ok":result.is_ok()}),
    );
    result
}

fn record(value: serde_json::Value) {
    use std::io::Write;
    if let Some(path) = std::env::var_os("HSM_PHASE_PROFILE") {
        if let Ok(mut file) = fs::OpenOptions::new().create(true).append(true).open(path) {
            let _ = writeln!(file, "{value}");
        }
    }
}

/// Bound disposable stage storage; losing an entry only makes its construction run again.
fn sweep(directory: &Path, limit: u64) -> Result<()> {
    let mut entries = vec![];
    let mut size = 0;
    for entry in fs::read_dir(directory)? {
        let entry = entry?;
        if entry
            .path()
            .extension()
            .is_none_or(|extension| extension != "npz")
        {
            continue;
        }
        let metadata = entry.metadata()?;
        size += metadata.len();
        entries.push((metadata.modified()?, metadata.len(), entry.path()));
    }
    if size > limit {
        entries.sort_by_key(|entry| entry.0);
        for (_, bytes, path) in entries {
            if size <= limit * 3 / 4 {
                break;
            }
            if fs::remove_file(path).is_ok() {
                size -= bytes;
            }
        }
    }
    Ok(())
}
