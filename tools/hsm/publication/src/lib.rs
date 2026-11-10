//! Completed geometry reaches the site through immutable objects and a source-scoped pointer commit.
pub mod build_times;
pub mod checks;
pub mod cut;
pub mod merge;
pub mod pack;
pub mod publish;
pub mod transport;

use anyhow::{Context, Result, bail};
use hsm_build_data::{artifact_cache, artifacts, inventory, publication};
use hsm_run_slots::{Lease, ipc};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, Output},
    sync::Arc,
    time::{Instant, SystemTime, UNIX_EPOCH},
};

pub const POINTERS: &str = "hardware/cad-artifacts.json";
pub const VIEWER_HOSTS: [&str; 2] = [
    "hardware/printed-parts/enclosure/enclosure/enclosure.step.mesh",
    "hardware/manifold-layout/enclosure-assembly.step.mesh",
];
pub fn strings(v: &Value) -> Vec<String> {
    v.as_array()
        .into_iter()
        .flatten()
        .filter_map(Value::as_str)
        .map(str::to_owned)
        .collect()
}
pub fn keys(v: &Value) -> Vec<String> {
    v.as_object()
        .map(|m| m.keys().cloned().collect())
        .unwrap_or_default()
}
pub fn empty() -> Value {
    json!({})
}
pub fn plain(v: Value) -> Value {
    match v {
        Value::Object(mut map)
            if map.len() == 1
                && (map.contains_key("$dict") || map.contains_key("_publication_pairs")) =>
        {
            let pairs = map
                .remove("$dict")
                .or_else(|| map.remove("_publication_pairs"))
                .unwrap();
            Value::Object(
                pairs
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter_map(|row| Some((row[0].as_str()?.into(), plain(row[1].clone()))))
                    .collect(),
            )
        }
        Value::Object(map) => Value::Object(map.into_iter().map(|(k, v)| (k, plain(v))).collect()),
        Value::Array(rows) => Value::Array(rows.into_iter().map(plain).collect()),
        other => other,
    }
}
pub fn ordered(v: &Value) -> Value {
    match v {
        Value::Object(map) => {
            json!({"_publication_pairs":map.iter().map(|(k,v)|json!([k,ordered(v)])).collect::<Vec<_>>()})
        }
        Value::Array(rows) => Value::Array(rows.iter().map(ordered).collect()),
        other => other.clone(),
    }
}
pub fn merge_maps(maps: &[&Value]) -> Value {
    let mut out = serde_json::Map::new();
    for map in maps {
        if let Some(map) = map.as_object() {
            out.extend(map.clone());
        }
    }
    Value::Object(out)
}
pub fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}
pub fn is_viewer(path: &str) -> bool {
    path.ends_with(".step.mesh") || path.ends_with(".glb.mesh") || path.ends_with(".glb")
}
/// Named views use their shared manifest; board GLBs retain the hierarchy their consumers read.
pub fn replaced_export(path: &str, head: &Value) -> bool {
    head["v"] == 4
        && ((path.ends_with(".step") && head["step_export"] == false)
            || (path.starts_with("hardware/assembly/scenes/glb/") && path.ends_with(".glb")))
}
pub fn read_json(path: impl AsRef<Path>) -> Result<Value> {
    Ok(serde_json::from_slice(&fs::read(path)?)?)
}

#[derive(Clone)]
pub struct ContextData {
    pub root: PathBuf,
    pub policy: Value,
    pub inventory: Value,
    pub graph: Value,
    pub graph_source: Value,
    pub lease: Option<Arc<Lease>>,
}
impl ContextData {
    pub fn load(root: &Path) -> Result<Self> {
        let policy = read_json(root.join("tools/hsm/publication/config.json")).or_else(|_| {
            serde_json::from_str(include_str!("../config.json")).map_err(anyhow::Error::from)
        })?;
        let inventory = read_json(root.join("tools/hsm/build-plan/inventory.json"))
            .context("native build inventory configuration")?;
        Self::with_config(root, policy, inventory)
    }
    pub fn with_config(root: &Path, mut policy: Value, inventory: Value) -> Result<Self> {
        policy["IMPLICIT_SOLIDS"] = inventory["implicit_solids"].clone();
        policy["ACTION_INTERMEDIATE"] = inventory["action_intermediate"].clone();
        let graph_source =
            read_json(root.join("tools/hsm/build-plan/graph.json")).unwrap_or_else(|_| empty());
        let mut graph_config = inventory.clone();
        graph_config["generator_order"] = json!(keys(&graph_source));
        let graph = serde_json::to_value(artifacts::Graph::new(&graph_source, &graph_config))?;
        Ok(Self {
            root: root.canonicalize().unwrap_or_else(|_| root.to_owned()),
            policy,
            inventory,
            graph,
            graph_source,
            lease: hsm_run_slots::inherited()?.map(Arc::new),
        })
    }
    pub fn reload(&self) -> Result<Self> {
        let policy = read_json(self.root.join("tools/hsm/publication/config.json"))
            .unwrap_or_else(|_| self.policy.clone());
        let inventory = read_json(self.root.join("tools/hsm/build-plan/inventory.json"))
            .unwrap_or_else(|_| self.inventory.clone());
        let mut next = Self::with_config(&self.root, policy, inventory)?;
        next.lease = self.lease.clone();
        Ok(next)
    }
    pub fn op(&self, op: &str, mut v: Value) -> Result<Value> {
        v["op"] = json!(format!("publication-{op}"));
        v["root"] = json!(self.root);
        v["config"] = self.policy.clone();
        publication::dispatch(&v)?
            .map(plain)
            .with_context(|| format!("unknown publication operation {op}"))
    }
    pub fn command(&self, name: &str, args: &[String]) -> Result<Output> {
        let mut cmd = Command::new(name);
        cmd.args(args)
            .current_dir(&self.root)
            .env_remove("GIT_INDEX_FILE");
        if let Some(lease) = &self.lease {
            lease.apply(&mut cmd)?;
        }
        Ok(ipc::output(&mut cmd)?)
    }
    pub fn git(&self, args: &[&str]) -> Result<Output> {
        self.command("git", &args.iter().map(|s| (*s).into()).collect::<Vec<_>>())
    }
    pub fn git_text(&self, args: &[&str]) -> Result<String> {
        let got = self.git(args)?;
        if !got.status.success() {
            bail!("git: {}", String::from_utf8_lossy(&got.stderr));
        }
        Ok(String::from_utf8(got.stdout)?.trim().into())
    }
    pub fn git_input(&self, args: &[&str], input: &[u8]) -> Result<Output> {
        use std::process::Stdio;
        let mut command = Command::new("git");
        command
            .args(args)
            .current_dir(&self.root)
            .env_remove("GIT_INDEX_FILE")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        if let Some(lease) = &self.lease {
            lease.apply(&mut command)?;
        }
        let mut child = ipc::spawn(&mut command)?;
        let mut stdin = child.stdin.take().context("Git input")?;
        std::thread::scope(|scope| -> Result<Output> {
            let writer = scope.spawn(move || stdin.write_all(input));
            let output = child.wait_with_output()?;
            writer
                .join()
                .map_err(|_| anyhow::anyhow!("Git input writer failed"))??;
            Ok(output)
        })
    }
    pub fn blob(&self, bytes: &[u8]) -> Result<String> {
        let out = self.git_input(&["hash-object", "-w", "--stdin"], bytes)?;
        anyhow::ensure!(
            out.status.success(),
            "Git blob write: {}",
            String::from_utf8_lossy(&out.stderr)
        );
        Ok(String::from_utf8(out.stdout)?.trim().into())
    }
    pub fn blobs(&self, ids: &BTreeSet<String>) -> Result<BTreeMap<String, Vec<u8>>> {
        if ids.is_empty() {
            return Ok(BTreeMap::new());
        }
        let input = ids.iter().map(|id| format!("{id}\n")).collect::<String>();
        let out = self.git_input(&["cat-file", "--batch"], input.as_bytes())?;
        anyhow::ensure!(
            out.status.success(),
            "Git blob read: {}",
            String::from_utf8_lossy(&out.stderr)
        );
        let mut at = 0;
        let mut blobs = BTreeMap::new();
        while at < out.stdout.len() {
            let end = at
                + out.stdout[at..]
                    .iter()
                    .position(|b| *b == b'\n')
                    .context("Git blob header")?;
            let fields = std::str::from_utf8(&out.stdout[at..end])?
                .split_whitespace()
                .collect::<Vec<_>>();
            at = end + 1;
            if fields.len() == 2 && fields[1] == "missing" {
                continue;
            }
            anyhow::ensure!(
                fields.len() == 3 && fields[1] == "blob",
                "unexpected Git batch object"
            );
            let size = fields[2].parse::<usize>()?;
            let end = at.checked_add(size).context("Git blob length")?;
            blobs.insert(
                fields[0].into(),
                out.stdout
                    .get(at..end)
                    .context("truncated Git blob")?
                    .to_vec(),
            );
            anyhow::ensure!(out.stdout.get(end) == Some(&b'\n'), "Git blob terminator");
            at = end + 1;
        }
        Ok(blobs)
    }
    pub fn post_commit(&self) -> Result<Output> {
        let mut command = Command::new("git");
        command
            .args(["hook", "run", "post-commit"])
            .current_dir(&self.root)
            .env_remove("GIT_INDEX_FILE")
            .env_remove("HSM_PUSHING");
        if let Some(lease) = &self.lease {
            lease.apply(&mut command)?;
        }
        Ok(ipc::output(&mut command)?)
    }
    pub fn held(&self) -> Result<Value> {
        match fs::read(self.root.join(POINTERS)) {
            Ok(bytes) => Ok(serde_json::from_slice(&bytes).context("published pointer JSON")?),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(empty()),
            Err(error) => Err(error.into()),
        }
    }
    pub fn solids(&self) -> Result<Vec<String>> {
        Ok(strings(&self.op("solids", empty())?)
            .into_iter()
            .filter(|path| {
                !(path.ends_with(".step") || path.ends_with(".glb"))
                    || !hsm_build_data::payload::header(self.root.join(format!("{path}.mesh")))
                        .is_ok_and(|head| replaced_export(path, &head))
            })
            .collect())
    }
    pub fn hashes(&self, paths: &[String]) -> Result<Value> {
        Ok(serde_json::to_value(artifact_cache::hashes(
            &self.root, paths,
        )?)?)
    }
    pub fn index(&self) -> Result<Value> {
        Ok(serde_json::to_value(artifacts::staged(&self.root)?)?)
    }
    pub fn sidecars(&self, held: &Value) -> Result<Value> {
        self.op("sidecar-lines", json!({"held":held,"graph":self.graph}))
    }
    pub fn tree(&self, lines: &Value, index: &Value) -> Result<Value> {
        self.op(
            "tree-digests",
            json!({"graph":self.graph,"lines":lines,"line_order":keys(lines),"index":index}),
        )
    }
    pub fn website(&self, held: &Value) -> Result<Value> {
        self.op("website", json!({"data":held}))
    }
    pub fn write(&self, data: &Value) -> Result<()> {
        self.op(
            "write-pointers",
            json!({"path":self.root.join(POINTERS),"data":data,"ordered":ordered(data)}),
        )?;
        Ok(())
    }
    pub fn made(
        &self,
        held: &Value,
        lines: &Value,
        walked: &Value,
        moved: &[String],
        grafted: &[String],
    ) -> Result<Value> {
        self.op("made-here",json!({"held":held,"held_order":ordered(held),"graph":self.graph,"index":self.index()?,"head":self.git_text(&["rev-parse","HEAD"])?,"lines":lines,"walked":walked,"moved":moved,"grafted":grafted,"skew_ns":2_000_000_000_i64,"frozen":publication::frozen_assets(&self.root)?.keys().collect::<Vec<_>>()}))
    }
    pub fn rows(&self) -> Result<Value> {
        let tracked = inventory::tracked(&self.root, &self.inventory, &self.policy)?;
        inventory::inventory(&self.root, &self.graph_source, tracked, &self.inventory)
    }
    pub fn targets_for(&self, members: &[String]) -> Result<(Vec<String>, Vec<String>)> {
        let out = self.op(
            "member-targets",
            json!({"members":members,"inventory":self.rows()?}),
        )?;
        Ok((strings(&out[0]), strings(&out[1])))
    }
    pub fn pointers(
        &self,
        held: &Value,
        hashes: &Value,
        sidecars: &Value,
        made: &Value,
        digest: &str,
        size: u64,
        stamp: f64,
    ) -> Result<Value> {
        let remote = self.git_text(&["remote", "get-url", "origin"])?;
        let slug = self.op("origin-slug", json!({"url":remote}))?;
        self.op("pointers",json!({"rels":keys(hashes),"digest":digest,"size":size,"slug":slug,"tag":self.tag(),"store_url":self.store_url(),"prefix":self.prefix(),"hashes":hashes,"hashes_order":ordered(hashes),"sidecar_order":ordered(sidecars),"made":made,"made_order":ordered(made),"held":held,"stamp":stamp}))
    }
    pub fn tag(&self) -> &str {
        self.policy["RELEASE_TAG"]
            .as_str()
            .unwrap_or("cad-artifacts")
    }
    pub fn prefix(&self) -> &str {
        self.policy["OBJECT_PREFIX"].as_str().unwrap_or("s-")
    }
    pub fn store_url(&self) -> &str {
        self.policy["STORE_URL"]
            .as_str()
            .unwrap_or("https://homesodamachine.com/objects/")
    }
    pub fn asset(&self, sha: &str) -> String {
        format!("{}{sha}.gz", self.prefix())
    }
}

pub fn timing(phase: &str, started: Instant, fields: Value) -> Result<()> {
    if let Some(path) = std::env::var_os("HSM_PUBLISH_TIMING") {
        let mut row = fields;
        if !row.is_object() {
            row = empty();
        }
        row["phase"] = json!(phase);
        row["pid"] = json!(std::process::id());
        row["wall_time_ns"] =
            json!(SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos() as u64);
        row["seconds"] = json!(started.elapsed().as_secs_f64());
        let mut file = fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)?;
        writeln!(file, "{row}")?;
    }
    Ok(())
}

/// Scoped worker storage retains only the changed files a publication freezes.
pub struct Work {
    pub path: PathBuf,
}
impl Work {
    pub fn new(root: &Path) -> Result<Self> {
        static SEQUENCE: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
        let parent = root.join(".cache/runs");
        fs::create_dir_all(&parent)?;
        let path = parent.join(format!(
            "publication-{}-{}-{}",
            std::process::id(),
            SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos(),
            SEQUENCE.fetch_add(1, std::sync::atomic::Ordering::Relaxed)
        ));
        fs::create_dir(&path)?;
        Ok(Self { path })
    }
}
impl Drop for Work {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.path);
    }
}

pub fn parallel<T: Sync, R: Send>(items: &[T], f: impl Fn(&T) -> R + Sync) -> Vec<R> {
    if items.is_empty() {
        return Vec::new();
    }
    std::thread::scope(|scope| {
        let f = &f;
        let workers = items
            .chunks(items.len().div_ceil(4))
            .map(|chunk| scope.spawn(move || chunk.iter().map(f).collect::<Vec<_>>()))
            .collect::<Vec<_>>();
        workers
            .into_iter()
            .flat_map(|worker| worker.join().expect("publication worker"))
            .collect()
    })
}

/// Maintenance entry points share root selection and the verified inherited lease.
pub fn maintenance_main(name: &str, run: fn(&ContextData, &[String]) -> Result<i32>) {
    let result = (|| -> Result<i32> {
        let mut root = std::env::current_dir()?;
        let mut args = Vec::new();
        let mut raw = std::env::args().skip(1);
        while let Some(arg) = raw.next() {
            if arg == "--root" {
                root = PathBuf::from(raw.next().context("--root needs a path")?);
            } else if let Some(path) = arg.strip_prefix("--root=") {
                root = PathBuf::from(path);
            } else {
                args.push(arg);
            }
        }
        let root = root.canonicalize()?;
        let ctx = ContextData::load(&root)?;
        run(&ctx, &args)
    })();
    match result {
        Ok(status) => std::process::exit(status),
        Err(error) => {
            eprintln!("{name}: {error:#}");
            std::process::exit(1);
        }
    }
}
