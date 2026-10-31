use anyhow::{Context, Result, ensure};
use hsm_geometry::payload::{self, Payload};
use serde_json::json;
use sha2::{Digest, Sha256};
use std::{
    collections::BTreeMap,
    fs::{self, File},
    io::{BufReader, BufWriter},
    os::unix::fs::MetadataExt,
    path::{Path, PathBuf},
    sync::Arc,
};

// Cached BVHs are versioned by their reader, geometry code and dependency lock.
pub fn geometry_version() -> String {
    let mut h = Sha256::new();
    h.update(include_str!("../../geometry/src/payload.rs"));
    h.update(include_str!("../../geometry/src/queries.rs"));
    h.update(include_str!("../../geometry/src/lib.rs"));
    h.update(include_str!("../../geometry/Cargo.toml"));
    h.update(include_str!("../../Cargo.toml"));
    h.update(include_str!("../../Cargo.lock"));
    format!("{:x}", h.finalize())
}

fn signature(path: &Path) -> Result<[u64; 7]> {
    let m = path.metadata()?;
    Ok([
        m.dev(),
        m.ino(),
        m.len(),
        m.mtime() as u64,
        m.mtime_nsec() as u64,
        m.ctime() as u64,
        m.ctime_nsec() as u64,
    ])
}

struct Resident {
    payload: Arc<Payload>,
    used: u64,
    budget: u64,
}

pub struct Store {
    directory: PathBuf,
    paths: BTreeMap<PathBuf, ([u64; 7], String)>,
    resident: BTreeMap<String, Resident>,
    tick: u64,
    budget: u64,
    pub loads: u64,
    pub restores: u64,
}

impl Store {
    pub fn new(directory: PathBuf, budget_mb: u64) -> Result<Self> {
        fs::create_dir_all(&directory)?;
        Ok(Self {
            directory: directory.join(geometry_version()),
            paths: BTreeMap::new(),
            resident: BTreeMap::new(),
            tick: 0,
            budget: budget_mb
                .checked_mul(1024 * 1024)
                .context("cache budget overflow")?,
            loads: 0,
            restores: 0,
        })
    }

    pub fn status(&self) -> serde_json::Value {
        json!({"resident_payloads": self.resident.len(), "payload_loads": self.loads,
            "bvh_restores": self.restores, "cache_budget_bytes": self.budget,
            "estimated_resident_bytes": self.resident.values().map(|v| v.budget).sum::<u64>(),
            "geometry_cache": self.directory})
    }

    pub fn load(&mut self, path: &Path) -> Result<Arc<Payload>> {
        let path = path
            .canonicalize()
            .with_context(|| format!("payload not found: {}", path.display()))?;
        self.tick += 1;
        let before = signature(&path)?;
        if let Some((stamp, digest)) = self.paths.get(&path) {
            if stamp == &before {
                if let Some(held) = self.resident.get_mut(digest) {
                    held.used = self.tick;
                    return Ok(held.payload.clone());
                }
            }
        }
        let budget = before[2].checked_mul(12).context("scene budget overflow")?;
        ensure!(
            budget <= self.budget,
            "scene needs an estimated {} MiB cache; daemon budget is {} MiB",
            budget / 1048576,
            self.budget / 1048576
        );
        let bytes = fs::read(&path)?;
        ensure!(
            before == signature(&path)?,
            "payload changed while loading; retry the query"
        );
        let digest = format!("{:x}", Sha256::digest(&bytes));
        self.paths.insert(path, (before, digest.clone()));
        if let Some(held) = self.resident.get_mut(&digest) {
            held.used = self.tick;
            return Ok(held.payload.clone());
        }
        // Conservative cache accounting includes lazy Manifold copies. This is
        // a cache budget, not a hard limit on process RSS or a query's scratch.
        while self.resident.values().map(|v| v.budget).sum::<u64>() + budget > self.budget {
            let oldest = self
                .resident
                .iter()
                .min_by_key(|(_, v)| v.used)
                .map(|(k, _)| k.clone());
            if let Some(key) = oldest {
                self.resident.remove(&key);
            } else {
                break;
            }
        }
        let cached = self.directory.join(format!("{digest}.bvh"));
        let restored: Option<Payload> = File::open(&cached)
            .ok()
            .and_then(|f| bincode::deserialize_from(BufReader::new(f)).ok());
        let payload = if let Some(p) = restored.filter(|p| p.digest == digest) {
            self.restores += 1;
            p
        } else {
            let p = payload::decode(&bytes)?;
            // Persistence failure costs only the next cold load; the requested
            // query still has a complete in-memory scene.
            if let Err(e) = self.save(&cached, &p) {
                eprintln!("hsm: BVH cache: {e}");
            }
            p
        };
        self.loads += 1;
        let payload = Arc::new(payload);
        self.resident.insert(
            digest,
            Resident {
                payload: payload.clone(),
                used: self.tick,
                budget,
            },
        );
        Ok(payload)
    }

    fn save(&self, dest: &Path, payload: &Payload) -> Result<()> {
        fs::create_dir_all(&self.directory)?;
        let tmp = dest.with_extension(format!("{}.tmp", std::process::id()));
        let result = (|| {
            let mut writer = BufWriter::new(File::create(&tmp)?);
            bincode::serialize_into(&mut writer, payload)?;
            use std::io::Write;
            writer.flush()?;
            fs::rename(&tmp, dest)?;
            Ok(())
        })();
        let _ = fs::remove_file(tmp);
        result
    }
}
