//! Typed build events, retained checkpoints and publication coalescing keep first view independent of later producers.
use anyhow::{Context, Result, bail, ensure};
use hsm_run_slots::Lease;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet},
    env,
    fs::{self, File, OpenOptions},
    io::{Read, Seek, SeekFrom, Write},
    os::unix::{fs::{MetadataExt, OpenOptionsExt}, process::ExitStatusExt},
    path::{Path, PathBuf},
    process::{Child, Command, ExitStatus},
    sync::atomic::{AtomicU64, Ordering},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

const POLL: Duration = Duration::from_millis(100);
static TEMPORARY: AtomicU64 = AtomicU64::new(0);

/// Commands and paths let a run use the current checkout or isolated producer fixtures.
#[derive(Debug, Clone)]
pub struct Config {
    pub root: PathBuf,
    pub run_dir: Option<PathBuf>,
    pub runner: Option<PathBuf>,
    pub bazel: PathBuf,
    pub publisher: Option<PathBuf>,
    pub progress: Option<PathBuf>,
    pub bazel_args: Vec<String>,
}

impl Config {
    pub fn defaults() -> Result<Self> {
        let root = env::var_os("HSM_WORKSPACE").map(PathBuf::from).unwrap_or_else(||
            Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap().to_owned());
        Ok(Self { root, run_dir: None, runner: None, bazel: "bazel".into(), publisher: None, progress: None, bazel_args: Vec::new() })
    }
}

#[derive(Debug, Clone, Default, Deserialize)]
struct GraphNode { #[serde(default)] writes: Vec<String> }
type Graph = BTreeMap<String, GraphNode>;

#[derive(Debug, Clone, Default, Deserialize)]
struct FileEntry {
    #[serde(default)] name: String,
    #[serde(default)] uri: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
struct SetId { id: String }

#[derive(Debug, Clone, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct FileSet {
    #[serde(default)] files: Vec<FileEntry>,
    #[serde(default)] file_sets: Vec<SetId>,
}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct OutputGroup { #[serde(default)] file_sets: Vec<SetId> }

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct TargetCompleted {
    #[serde(default)] success: bool,
    #[serde(default)] output_group: Vec<OutputGroup>,
}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ActionCompleted {
    #[serde(default)] success: bool,
    #[serde(default)] primary_output: FileEntry,
}

#[derive(Debug, Default, Deserialize)]
struct ActionId { #[serde(default)] label: Option<String> }

#[derive(Debug, Default, Deserialize)]
struct TargetId {}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct EventId {
    #[serde(default)] named_set: Option<SetId>,
    #[serde(default)] target_completed: Option<TargetId>,
    #[serde(default)] action_completed: Option<ActionId>,
}

#[derive(Debug, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
struct BuildEvent {
    #[serde(default)] id: EventId,
    #[serde(default)] named_set_of_files: FileSet,
    #[serde(default)] completed: TargetCompleted,
    #[serde(default)] action: ActionCompleted,
}

#[derive(Debug, Deserialize)]
struct Checkpoint {
    files: Vec<PathBuf>,
    #[serde(default)] stage: Option<String>,
}

/// A tail keeps incomplete writes until their terminating newline arrives.
struct Tail { path: PathBuf, stream: Option<File>, pending: Vec<u8> }

impl Tail {
    fn event(path: PathBuf) -> Self { Self { path, stream: None, pending: Vec::new() } }
    fn progress(path: PathBuf) -> Result<Self> {
        if let Some(parent) = path.parent() { fs::create_dir_all(parent)?; }
        let mut stream = OpenOptions::new().create(true).read(true).append(true).open(&path)?;
        stream.seek(SeekFrom::End(0))?;
        Ok(Self { path, stream: Some(stream), pending: Vec::new() })
    }
    fn poll(&mut self, final_chunk: bool) -> Result<Vec<Vec<u8>>> {
        if self.stream.is_none() {
            match File::open(&self.path) {
                Ok(file) => self.stream = Some(file),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
                Err(error) => return Err(error.into()),
            }
        }
        self.stream.as_mut().unwrap().read_to_end(&mut self.pending)?;
        let mut rows = Vec::new();
        let mut start = 0;
        for (index, byte) in self.pending.iter().enumerate() {
            if *byte == b'\n' { rows.push(self.pending[start..index].to_vec()); start = index + 1; }
        }
        if final_chunk && start < self.pending.len() { rows.push(self.pending[start..].to_vec()); start = self.pending.len(); }
        self.pending.drain(..start);
        rows.retain(|row| row.iter().any(|byte| !byte.is_ascii_whitespace()));
        Ok(rows)
    }
}

#[derive(Debug, Default, Deserialize)]
struct Pointers {
    #[serde(default)] solids: BTreeMap<String, String>,
    #[serde(default)] sidecars: BTreeMap<String, String>,
}

#[derive(Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Signature { path: PathBuf, device: u64, inode: u64, size: u64, mtime: (i64, i64), ctime: (i64, i64) }

/// Publication debt follows the served pointer and exact completed output bytes.
struct Publications {
    served: BTreeMap<String, String>,
    digests: BTreeMap<Signature, String>,
    requested: BTreeSet<(String, String)>,
}

impl Publications {
    fn new(root: &Path) -> Self {
        let mut pointers: Pointers = fs::read(root.join("hardware/cad-artifacts.json")).ok()
            .and_then(|bytes| serde_json::from_slice(&bytes).ok()).unwrap_or_default();
        pointers.solids.append(&mut pointers.sidecars);
        Self { served: pointers.solids, digests: BTreeMap::new(), requested: BTreeSet::new() }
    }
    fn needs(&mut self, name: &str, path: &Path, changed: bool) -> Result<bool> {
        if !self.served.contains_key(name) && ![".mesh", ".stl", ".step", ".glb"].iter().any(|suffix| name.ends_with(suffix)) { return Ok(false); }
        let stat = path.metadata()?;
        let signature = Signature { path: path.to_owned(), device: stat.dev(), inode: stat.ino(), size: stat.len(),
            mtime: (stat.mtime(), stat.mtime_nsec()), ctime: (stat.ctime(), stat.ctime_nsec()) };
        let digest = if let Some(digest) = self.digests.get(&signature) { digest.clone() } else {
            let digest = file_digest(path)?; self.digests.insert(signature, digest.clone()); digest
        };
        let key = (name.to_owned(), digest.clone());
        if !changed && (self.served.get(name) == Some(&digest) || self.requested.contains(&key)) { return Ok(false); }
        self.requested.insert(key);
        Ok(true)
    }
}

#[derive(Debug, Default, Serialize)]
struct QueueRecord { requests: usize, started: usize, coalesced: usize, exit_codes: Vec<i32> }

/// A running publisher consumes completed bytes while later requests coalesce into its successor.
struct PublicationQueue<'a> {
    root: &'a Path, run: &'a Path, executable: &'a Path, lease: &'a Lease,
    active: Option<Child>, pending: bool, record: QueueRecord,
}

impl<'a> PublicationQueue<'a> {
    fn new(root: &'a Path, run: &'a Path, executable: &'a Path, lease: &'a Lease) -> Self {
        Self { root, run, executable, lease, active: None, pending: false, record: QueueRecord::default() }
    }
    fn request(&mut self) -> Result<()> {
        self.record.requests += 1;
        if let Some(child) = &mut self.active { if child.try_wait()?.is_none() { self.record.coalesced += 1; } }
        self.pending = true;
        self.poll()
    }
    fn poll(&mut self) -> Result<()> {
        if let Some(child) = &mut self.active {
            if let Some(code) = child.try_wait()? {
                self.record.exit_codes.push(exit_code(code)); self.active = None;
            }
        }
        if self.active.is_none() && self.pending {
            let log = File::create(self.run.join(format!("publish-{}.log", self.record.started)))?;
            let mut command = Command::new(self.executable);
            command.arg("--root").arg(self.root).current_dir(self.root).stdout(log.try_clone()?).stderr(log);
            self.lease.apply(&mut command)?;
            self.active = Some(command.spawn().with_context(|| format!("start {}", self.executable.display()))?);
            self.pending = false; self.record.started += 1;
        }
        Ok(())
    }
    fn drain(&mut self) -> Result<()> {
        while self.active.is_some() || self.pending {
            self.poll()?;
            if let Some(child) = &mut self.active { child.wait()?; }
        }
        Ok(())
    }
}

/// A build child is terminated on an interrupted event stream instead of leaving its wrapper alive.
struct BuildChild(Child);
impl Drop for BuildChild {
    fn drop(&mut self) {
        if self.0.try_wait().ok().flatten().is_none() {
            // The child PID is owned here and unreaped; SIGTERM lets its native wrapper clean up.
            unsafe { libc::kill(self.0.id() as libc::pid_t, libc::SIGTERM); }
            let _ = self.0.wait();
        }
    }
}

#[derive(Debug, Serialize)]
struct Carried {
    seconds: f64, wall_time_ns: u128, files: Vec<String>, publication: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")] stage: Option<String>,
}

#[derive(Debug, Serialize)]
struct Suppressed { seconds: f64, stage: String, files: Vec<String> }

#[derive(Debug, Serialize)]
struct Preview {
    phase: &'static str,
    #[serde(skip_serializing_if = "Option::is_none")] seconds: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")] exit_code: Option<i32>,
    #[serde(skip_serializing_if = "Option::is_none")] error: Option<String>,
}

#[derive(Serialize)]
struct RunRecord<'a> {
    purpose: &'static str, success: bool, wall_seconds: f64, preview: &'a [Preview],
    checkpoint_errors: &'a [String], carried: &'a [Carried], suppressed_checkpoints: &'a [Suppressed],
    publication_queue: &'a QueueRecord,
}

struct Driver<'a> {
    root: &'a Path, graph: Graph, outputs: BTreeSet<String>, started: Instant,
    publication: Publications, publishing: PublicationQueue<'a>,
    sets: BTreeMap<String, FileSet>, pending: BTreeSet<String>, seen: BTreeSet<String>,
    carried: Vec<Carried>, suppressed: Vec<Suppressed>,
}

impl<'a> Driver<'a> {
    fn new(root: &'a Path, graph: Graph, started: Instant, publishing: PublicationQueue<'a>) -> Self {
        let outputs = graph.values().flat_map(|node| node.writes.iter().cloned()).collect();
        Self { root, graph, outputs, started, publication: Publications::new(root), publishing,
            sets: BTreeMap::new(), pending: BTreeSet::new(), seen: BTreeSet::new(), carried: Vec::new(), suppressed: Vec::new() }
    }
    fn output_name<'b>(&'b self, name: &str) -> Option<&'b str> {
        self.outputs.get(name).map(String::as_str).or_else(|| self.outputs.iter().find(|rel| name.ends_with(&format!("/{rel}"))).map(String::as_str))
    }
    fn carry(&mut self, entries: &[FileEntry], stage: Option<&str>) -> Result<()> {
        let mut moved = Vec::new(); let mut ready = Vec::new(); let mut status_only = Vec::new();
        for entry in entries {
            let Some(name) = self.output_name(&entry.name).map(str::to_owned) else { continue };
            if !name.starts_with("hardware/") || ![".mesh", ".step", ".stl", ".glb", ".npz", ".print-features.json", ".facts.json"].iter().any(|suffix| name.ends_with(suffix)) { continue; }
            let Some(uri) = &entry.uri else { continue };
            let Ok(source) = file_uri(uri) else { continue };
            if !source.is_file() { continue; }
            let target = self.root.join(&name);
            let mut changed = !same_file_bytes(&source, &target)?;
            if changed && stage.is_some() && name.ends_with(".mesh") && unchanged_checkpoint(&source, &target) {
                status_only.push(name.clone()); changed = false;
            }
            if changed { carry_file(&source, &target)?; moved.push(name.clone()); }
            if self.publication.needs(&name, &target, changed)? { ready.push(name.clone()); }
            if name.ends_with(".mesh") && raw_export_replaced(&name, &target)? {
                let old = PathBuf::from(target.as_os_str().to_string_lossy().trim_end_matches(".mesh"));
                if old.is_file() { fs::remove_file(old)?; }
            }
        }
        if !status_only.is_empty() { self.suppressed.push(Suppressed { seconds: self.started.elapsed().as_secs_f64(), stage: stage.unwrap().to_owned(), files: status_only }); }
        if !moved.is_empty() || !ready.is_empty() {
            if !moved.is_empty() { println!("[print-build] carried {}", moved.join(", ")); }
            else { println!("[print-build] completed outputs await publication: {}", ready.join(", ")); }
            std::io::stdout().flush()?;
            self.carried.push(Carried { seconds: self.started.elapsed().as_secs_f64(), wall_time_ns: SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos(),
                files: moved, publication: ready.clone(), stage: stage.map(str::to_owned) });
        }
        if !ready.is_empty() { self.publishing.request()?; }
        Ok(())
    }
    fn event(&mut self, row: BuildEvent) -> Result<()> {
        if let Some(id) = row.id.named_set { self.sets.insert(id.id, row.named_set_of_files); }
        if row.id.target_completed.is_some() && row.completed.success {
            self.pending.extend(row.completed.output_group.into_iter().flat_map(|group| group.file_sets.into_iter().map(|set| set.id)));
        }
        if let Some(id) = row.id.action_completed.filter(|_| row.action.success) {
            let primary = row.action.primary_output;
            if primary.uri.is_some() { self.carry(std::slice::from_ref(&primary), None)?; }
            if id.label.is_some() {
                if let Some(path) = primary.uri.as_ref().and_then(|uri| file_uri(uri).ok()) {
                    let path = path.to_string_lossy();
                    if let Some(rel) = self.outputs.iter().find(|rel| path.ends_with(&format!("/{rel}"))) {
                        let prefix = &path[..path.len() - rel.len()];
                        let peers = self.graph.values().filter(|node| node.writes.contains(rel)).flat_map(|node| node.writes.iter()).map(|name|
                            FileEntry { name: name.clone(), uri: Some(path_uri(&PathBuf::from(format!("{prefix}{name}")))) }).collect::<Vec<_>>();
                        self.carry(&peers, None)?;
                    }
                }
            }
        }
        for id in self.pending.clone() {
            if self.seen.contains(&id) { self.pending.remove(&id); continue; }
            if let Some(files) = files_for(&id, &self.sets, &mut BTreeSet::new()) {
                self.carry(&files, None)?; self.seen.insert(id.clone()); self.pending.remove(&id);
            }
        }
        Ok(())
    }
    fn checkpoints(&mut self, progress: &mut Option<Tail>, errors: &mut Vec<String>) {
        let Some(progress) = progress else { return };
        match progress.poll(false) {
            Ok(lines) => for line in lines {
                match serde_json::from_slice::<Checkpoint>(&line) {
                    Ok(row) => {
                        let entries = row.files.iter().filter(|path| path.is_absolute()).filter_map(|source| {
                            let name = self.outputs.iter().find(|rel| source.to_string_lossy().ends_with(&format!("/{rel}")))?;
                            Some(FileEntry { name: name.clone(), uri: Some(path_uri(source)) })
                        }).collect::<Vec<_>>();
                        if let Err(error) = self.carry(&entries, row.stage.as_deref()) { errors.push(format!("{error:#}")); }
                    }
                    Err(error) => errors.push(error.to_string()),
                }
            },
            Err(error) => errors.push(error.to_string()),
        }
    }
}

fn files_for(id: &str, sets: &BTreeMap<String, FileSet>, visiting: &mut BTreeSet<String>) -> Option<Vec<FileEntry>> {
    if !visiting.insert(id.to_owned()) { return Some(Vec::new()); }
    let set = sets.get(id)?;
    let mut files = set.files.clone();
    for child in &set.file_sets { files.extend(files_for(&child.id, sets, visiting)?); }
    Some(files)
}

#[derive(Debug, Deserialize)]
struct Receipt { value: PresentationState }
#[derive(Debug, Deserialize)]
struct PresentationState { inputs: BTreeMap<String, String> }

/// Retained placement inputs select the advisory preview before dependent geometry rebuilds.
pub fn placement_changed(args: &[String], root: &Path) -> bool {
    if args.iter().any(|arg| arg.starts_with("--nobuild")) { return false; }
    if !args.is_empty() && !args.iter().any(|arg| ["//:installed-machine", "//:everything"].contains(&arg.as_str()) || arg.starts_with("//:enclosure-")) { return false; }
    let name = format!("{:x}.json", Sha256::digest(b"presentation-state"));
    let read = || -> Result<bool> {
        let receipt: Receipt = serde_json::from_slice(&fs::read(root.join(".cache/realized/installed-machine/receipts").join(name))?)?;
        ensure!(!receipt.value.inputs.is_empty(), "placement receipt has no inputs");
        for (path, expected) in receipt.value.inputs { if file_digest(&root.join(path))? != expected { return Ok(true); } }
        Ok(false)
    };
    read().unwrap_or(false)
}

#[derive(Debug, Deserialize)]
struct IterationStatus { #[serde(default)] complete: bool }
#[derive(Debug, Deserialize)]
struct MeshHeader {
    #[serde(default)] v: Option<u32>,
    #[serde(default)] step_export: Option<bool>,
    #[serde(default)] iteration: Option<IterationStatus>,
    #[serde(flatten)] content: BTreeMap<String, Value>,
}

fn mesh_header(path: &Path, complete_header: bool) -> Result<MeshHeader> {
    let mut file = File::open(path)?;
    let mut size = [0; 4]; file.read_exact(&mut size)?;
    let size = u32::from_le_bytes(size) as usize;
    ensure!(size as u64 <= file.metadata()?.len().saturating_sub(4), "truncated mesh header");
    let mut bytes = vec![0; size]; file.read_exact(&mut bytes)?;
    let head = serde_json::from_slice(&bytes)?;
    if complete_header { let mut byte = [0]; ensure!(file.read(&mut byte)? == 0, "mesh has geometry after its shared header"); }
    Ok(head)
}

// Shared meshes replace raw GLBs only inside the viewer's named assembly-view directory.
fn raw_export_replaced(name: &str, payload: &Path) -> Result<bool> {
    let glb = name.ends_with(".glb.mesh");
    if glb && !name.starts_with("hardware/assembly/scenes/glb/") { return Ok(false); }
    let head = mesh_header(payload, false)?;
    Ok(head.v == Some(4) && (glb || head.step_export == Some(false)))
}

fn same_geometry(a: MeshHeader, b: MeshHeader) -> bool {
    a.v == b.v && a.step_export == b.step_export && a.content == b.content
}

/// Status-only intermediate checkpoints retain the held scene's inode and completed identity.
pub fn unchanged_checkpoint(source: &Path, target: &Path) -> bool {
    let compare = || -> Result<bool> {
        let incoming = mesh_header(source, true)?; let held = mesh_header(target, true)?;
        if incoming.v != Some(4) || held.v != Some(4) || incoming.iteration.as_ref().is_some_and(|status| status.complete) { return Ok(false); }
        Ok(same_geometry(incoming, held))
    };
    compare().unwrap_or(false)
}

fn same_file_bytes(source: &Path, target: &Path) -> Result<bool> {
    let mut incoming = File::open(source)?;
    let mut held = match File::open(target) { Ok(file) => file, Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false), Err(error) => return Err(error.into()) };
    if incoming.metadata()?.len() != held.metadata()?.len() { return Ok(false); }
    let mut a = [0u8; 65536]; let mut b = [0u8; 65536];
    loop {
        let na = incoming.read(&mut a)?;
        let nb = held.read(&mut b)?;
        if na != nb || a[..na] != b[..nb] { return Ok(false); }
        if na == 0 { return Ok(true); }
    }
}

struct Temporary(PathBuf);
impl Drop for Temporary { fn drop(&mut self) { let _ = fs::remove_file(&self.0); } }

/// Independent same-directory copies make completed producer replacement atomic under concurrent carries.
pub fn carry_file(source: &Path, target: &Path) -> Result<()> {
    let parent = target.parent().context("output parent")?; fs::create_dir_all(parent)?;
    let (temporary, mut output) = loop {
        let serial = TEMPORARY.fetch_add(1, Ordering::Relaxed);
        let path = parent.join(format!(".{}.carry-{}-{serial}", target.file_name().context("output name")?.to_string_lossy(), std::process::id()));
        match OpenOptions::new().create_new(true).write(true).mode(0o600).open(&path) {
            Ok(file) => break (Temporary(path), file),
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error.into()),
        }
    };
    std::io::copy(&mut File::open(source)?, &mut output)?;
    output.flush()?; drop(output);
    fs::rename(&temporary.0, target)?;
    Ok(())
}

fn file_digest(path: &Path) -> Result<String> {
    let mut file = File::open(path)?; let mut digest = Sha256::new(); let mut bytes = [0u8; 65536];
    loop { let n = file.read(&mut bytes)?; if n == 0 { break; } digest.update(&bytes[..n]); }
    Ok(format!("{:x}", digest.finalize()))
}

fn file_uri(uri: &str) -> Result<PathBuf> {
    let path = if let Some(value) = uri.strip_prefix("file://") {
        if value.starts_with('/') { value } else { value.strip_prefix("localhost").filter(|v| v.starts_with('/')).context("non-local file URI")? }
    } else if uri.starts_with('/') { uri } else { bail!("completed output does not name a local file URI: {uri}"); };
    let bytes = path.as_bytes(); let mut out = Vec::new(); let mut index = 0;
    while index < bytes.len() {
        if bytes[index] == b'%' {
            ensure!(index + 2 < bytes.len(), "truncated file URI escape");
            let nibble = |byte: u8| -> Result<u8> { (byte as char).to_digit(16).map(|n| n as u8).context("invalid file URI escape") };
            out.push((nibble(bytes[index + 1])? << 4) | nibble(bytes[index + 2])?); index += 3;
        } else { out.push(bytes[index]); index += 1; }
    }
    Ok(String::from_utf8(out).context("file URI is not UTF-8")?.into())
}

fn path_uri(path: &Path) -> String {
    let mut uri = String::from("file://");
    for byte in path.to_string_lossy().as_bytes() {
        if byte.is_ascii_alphanumeric() || b"/-._~".contains(byte) { uri.push(*byte as char); }
        else { uri.push_str(&format!("%{byte:02X}")); }
    }
    uri
}

fn exit_code(status: ExitStatus) -> i32 { status.code().unwrap_or_else(|| 128 + status.signal().unwrap_or(1)) }

fn relative(root: &Path, path: PathBuf) -> PathBuf { if path.is_absolute() { path } else { root.join(path) } }

fn executable(root: &Path, name: &str, configured: Option<PathBuf>) -> PathBuf {
    if let Some(path) = configured { return if path.components().count() == 1 { path } else { relative(root, path) }; }
    let beside = env::current_exe().ok().and_then(|exe| exe.parent().map(|parent| parent.join(name)));
    let local = root.join("tools/hsm/target/release").join(name);
    if let Some(path) = beside.filter(|path| path.is_file()) { return path; }
    if local.is_file() { return local; }
    if name == "hsm-run" {
        #[derive(Deserialize)] struct Runtime { runner: PathBuf }
        #[allow(deprecated)] let home = env::home_dir();
        if let Some(runtime) = home.and_then(|home| fs::read(home.join(".local/lib/hsm/runtime.json")).ok())
            .and_then(|bytes| serde_json::from_slice::<Runtime>(&bytes).ok()).filter(|runtime| runtime.runner.is_file()) { return runtime.runner; }
    }
    name.into()
}

fn wrapped(runner: &Path, root: &Path, program: &Path, args: &[String], lease: &Lease) -> Result<Command> {
    let mut command = Command::new(runner);
    command.arg("--").arg(program).args(args).current_dir(root).env("HSM_WORKSPACE", root);
    lease.apply(&mut command)?;
    Ok(command)
}

/// A run keeps one verified logical lease through early placement, producers and publication.
pub fn run(config: Config) -> Result<i32> {
    let root = fs::canonicalize(&config.root).with_context(|| format!("checkout {}", config.root.display()))?;
    let lease = hsm_run_slots::acquire("print-build", hsm_run_slots::inherited()?, env::var("HSM_RUN_TIMING").is_ok_and(|value| value == "1"))?;
    let runner = executable(&root, "hsm-run", config.runner);
    let publisher = executable(&root, "hsm-publish", config.publisher);
    let run = config.run_dir.map(|path| relative(&root, path)).unwrap_or_else(|| root.join(".cache/runs").join(format!("print-build-{}-{}", SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs(), std::process::id())));
    fs::create_dir_all(&run)?;
    let event_path = run.join("events.jsonl");
    if event_path.exists() { fs::remove_file(&event_path)?; }
    let started = Instant::now();
    let graph: Graph = serde_json::from_slice(&fs::read(root.join("tools/bazel/graph.json"))?)?;
    let publishing = PublicationQueue::new(&root, &run, &publisher, &lease);
    let mut driver = Driver::new(&root, graph, started, publishing);
    let progress_path = config.progress.map(|path| relative(&root, path)).unwrap_or_else(|| root.join(".cache/realized/print-build-progress.jsonl"));
    let mut checkpoint_errors = Vec::new();
    let mut progress = match Tail::progress(progress_path.clone()) { Ok(tail) => Some(tail), Err(error) => { checkpoint_errors.push(error.to_string()); None } };
    let mut preview = Vec::new();
    if progress.is_some() && placement_changed(&config.bazel_args, &root) {
        let mut prepass = || -> Result<()> {
            let mut flags = config.bazel_args.iter().filter(|arg| !arg.starts_with("//") && !arg.starts_with(':')).cloned().collect::<Vec<_>>();
            let mut args = vec!["build".to_owned(), "--check_up_to_date".into()]; args.append(&mut flags); args.push("//:installed-machine-program".into());
            let phase = Instant::now();
            let built = wrapped(&runner, &root, &config.bazel, &args, &lease)?.status()?;
            preview.push(Preview { phase: "current-program", seconds: Some(phase.elapsed().as_secs_f64()), exit_code: Some(exit_code(built)), error: None });
            let program = root.join("bazel-bin/out/installed-machine-program/installed-machine");
            if built.success() && program.is_file() {
                let phase = Instant::now();
                let args = vec![run.join("placement-preview").to_string_lossy().into_owned(), "--placements-only".into()];
                let placed = wrapped(&runner, &root, &program, &args, &lease)?.env("HSM_BUILD_PROGRESS", &progress_path).status()?;
                preview.push(Preview { phase: "placements", seconds: Some(phase.elapsed().as_secs_f64()), exit_code: Some(exit_code(placed)), error: None });
                driver.checkpoints(&mut progress, &mut checkpoint_errors);
            }
            Ok(())
        };
        if let Err(error) = prepass() { preview.push(Preview { phase: "placements", seconds: None, exit_code: None, error: Some(error.to_string()) }); }
    }
    let mut args = vec!["build".to_owned(), "--keep_going".into(), "--build_event_publish_all_actions".into(), format!("--build_event_json_file={}", event_path.display())];
    args.extend(if config.bazel_args.is_empty() { vec!["//:everything".to_owned()] } else { config.bazel_args });
    let mut command = wrapped(&runner, &root, &config.bazel, &args, &lease)?;
    command.env("HSM_BUILD_PROGRESS", &progress_path);
    let mut process = BuildChild(command.spawn()?);
    let mut events = Tail::event(event_path.clone());
    let mut build = || -> Result<i32> {
        loop {
            driver.checkpoints(&mut progress, &mut checkpoint_errors);
            driver.publishing.poll()?;
            let code = process.0.try_wait()?;
            for line in events.poll(code.is_some())? { driver.event(serde_json::from_slice(&line).context("read Bazel build event")?)?; }
            if let Some(code) = code { break Ok(exit_code(code)); }
            thread::sleep(POLL);
        }
    };
    let code = match build() { Ok(code) => code, Err(error) => { drop(process); driver.publishing.drain()?; return Err(error); } };
    driver.checkpoints(&mut progress, &mut checkpoint_errors);
    driver.publishing.drain()?;
    let record = RunRecord { purpose: "This record identifies each completed producer carried during the print build.",
        success: code == 0 && driver.publishing.record.exit_codes.iter().all(|code| *code == 0), wall_seconds: started.elapsed().as_secs_f64(),
        preview: &preview, checkpoint_errors: &checkpoint_errors, carried: &driver.carried, suppressed_checkpoints: &driver.suppressed,
        publication_queue: &driver.publishing.record };
    fs::write(run.join("result.json"), serde_json::to_string_pretty(&record)? + "\n")?;
    match fs::remove_file(event_path) { Ok(()) => (), Err(error) if error.kind() == std::io::ErrorKind::NotFound => (), Err(error) => return Err(error.into()) }
    Ok(if code != 0 { code } else { i32::from(!record.success) })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::{os::unix::fs::PermissionsExt, sync::Arc};

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            let root = Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap()
                .join(".cache/runs/python-retirement-20261110/print-build-fixtures")
                .join(format!("{}-{}", std::process::id(), TEMPORARY.fetch_add(1, Ordering::Relaxed)));
            fs::create_dir_all(&root).unwrap(); Self(root)
        }
        fn path(&self, path: &str) -> PathBuf { self.0.join(path) }
        fn write(&self, path: &str, bytes: impl AsRef<[u8]>) -> PathBuf {
            let path = self.path(path); fs::create_dir_all(path.parent().unwrap()).unwrap(); fs::write(&path, bytes).unwrap(); path
        }
        fn json(&self, path: &str, value: Value) -> PathBuf { self.write(path, serde_json::to_vec(&value).unwrap()) }
        fn script(&self, path: &str, code: &str) -> PathBuf {
            let path = self.write(path, format!("#!/bin/sh\nset -eu\n{code}\n"));
            fs::set_permissions(&path, fs::Permissions::from_mode(0o755)).unwrap(); path
        }
        fn lease(&self) -> Lease { hsm_run_slots::acquire("print-build-test", hsm_run_slots::inherited().unwrap(), false).unwrap() }
    }
    impl Drop for Fixture { fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); } }

    fn scene(path: &Path, head: &Value) {
        fs::create_dir_all(path.parent().unwrap()).unwrap();
        let mut bytes = serde_json::to_vec(head).unwrap();
        bytes.resize(bytes.len().div_ceil(4) * 4, b' ');
        let mut file = File::create(path).unwrap(); file.write_all(&(bytes.len() as u32).to_le_bytes()).unwrap(); file.write_all(&bytes).unwrap();
    }
    fn head(complete: bool) -> Value {
        json!({"v":4,"src":"scene revision","step_export":false,
            "meshes":[{"name":"relay","asset":"geometry","transform":[[1,0,0,0],[0,1,0,0],[0,0,1,0]],
                "entries":[{"name":"relay","color":[0.1,0.2,0.3]}],"features":{"mount":"upper-relay"},"source":"hardware/reference/relay.step.mesh"}],
            "sources":{"hardware/reference/relay.step.mesh":"source revision"},"iteration":{"stage":"mechanics","complete":complete}})
    }
    fn shell(value: &str) -> String { format!("'{}'", value.replace('\'', "'\"'\"'")) }
    fn wait_for(path: &Path) {
        let deadline = Instant::now() + Duration::from_secs(5);
        while !path.exists() && Instant::now() < deadline { thread::sleep(Duration::from_millis(10)); }
        assert!(path.exists(), "{} was not created", path.display());
    }

    #[test]
    fn checkpoint_tail_ignores_history_and_waits_for_complete_rows() {
        let f = Fixture::new(); let path = f.write("progress.jsonl", "{\"files\":[]}\n");
        let mut tail = Tail::progress(path.clone()).unwrap(); assert!(tail.poll(false).unwrap().is_empty());
        let mut writer = OpenOptions::new().append(true).open(&path).unwrap();
        writer.write_all(b"{\"stage\":\"mechanics\",\"files\":[").unwrap();
        assert!(tail.poll(false).unwrap().is_empty());
        writer.write_all(b"\"/work/hardware/model.step.mesh\"]}\ninvalid\n[]\n{\"files\":[]}\n").unwrap();
        let rows = tail.poll(false).unwrap(); assert_eq!(rows.len(), 4);
        assert_eq!(serde_json::from_slice::<Checkpoint>(&rows[0]).unwrap().stage.as_deref(), Some("mechanics"));
        assert!(serde_json::from_slice::<Checkpoint>(&rows[1]).is_err());
        assert!(serde_json::from_slice::<Checkpoint>(&rows[2]).is_err());
        assert!(serde_json::from_slice::<Checkpoint>(&rows[3]).is_ok());
        assert!(tail.poll(false).unwrap().is_empty());
    }

    #[test]
    fn status_suppression_preserves_every_geometry_binding_and_final_completion() {
        let f = Fixture::new(); let target = f.path("held.mesh"); let incoming = f.path("incoming.mesh");
        scene(&target, &head(true)); scene(&incoming, &head(false));
        assert!(unchanged_checkpoint(&incoming, &target));
        let variants = [
            ("/meshes/0/asset", json!("other geometry")),
            ("/meshes/0/transform/0/3", json!(1)),
            ("/meshes/0/entries/0/color", json!([0.3,0.2,0.1])),
            ("/meshes/0/features/mount", json!("other mount")),
            ("/meshes/0/source", json!("hardware/reference/other.step.mesh")),
            ("/sources/hardware~1reference~1relay.step.mesh", json!("other source revision")),
        ];
        for (pointer, value) in variants {
            let mut changed = head(false); *changed.pointer_mut(pointer).unwrap() = value;
            scene(&incoming, &changed); assert!(!unchanged_checkpoint(&incoming, &target), "{pointer}");
        }
        scene(&incoming, &head(true)); assert!(!unchanged_checkpoint(&incoming, &target));
        let mut ordinary = head(false); ordinary["v"] = json!(3); scene(&incoming, &ordinary);
        assert!(!unchanged_checkpoint(&incoming, &target));
        scene(&incoming, &head(false)); OpenOptions::new().append(true).open(&incoming).unwrap().write_all(b"geometry").unwrap();
        assert!(!unchanged_checkpoint(&incoming, &target));
    }

    #[test]
    fn publication_debt_tracks_completed_local_bytes_without_repeated_requests() {
        let f = Fixture::new(); let name = "hardware/model.step.mesh";
        let path = f.write(name, "served");
        f.json("hardware/cad-artifacts.json", json!({"solids":{name:file_digest(&path).unwrap()}}));
        let mut publication = Publications::new(&f.0);
        assert!(!publication.needs(name, &path, false).unwrap());
        f.write(name, "completed"); assert!(publication.needs(name, &path, false).unwrap());
        assert!(!publication.needs(name, &path, false).unwrap());
        assert!(publication.needs(name, &path, true).unwrap());
        assert!(!publication.needs("hardware/unpublished.npz", &path, true).unwrap());
    }

    #[test]
    fn placement_prepass_requires_changed_recorded_inputs_and_relevant_targets() {
        let f = Fixture::new(); let source = f.write("hardware/layout.json", "original");
        let selected = vec!["//:installed-machine".to_owned()]; assert!(!placement_changed(&selected, &f.0));
        let receipt = format!(".cache/realized/installed-machine/receipts/{:x}.json", Sha256::digest(b"presentation-state"));
        f.json(&receipt, json!({"value":{"inputs":{"hardware/layout.json":file_digest(&source).unwrap()}}}));
        assert!(!placement_changed(&selected, &f.0)); f.write("hardware/layout.json", "moved");
        assert!(placement_changed(&selected, &f.0));
        assert!(!placement_changed(&["//:tpu-o-ring".into()], &f.0));
        assert!(!placement_changed(&["--nobuild".into(), "//:installed-machine".into()], &f.0));
        f.write(&receipt, "incomplete"); assert!(!placement_changed(&selected, &f.0));
    }

    #[test]
    fn concurrent_carries_remain_complete_and_remove_temporary_files() {
        let f = Arc::new(Fixture::new()); let a = f.write("first", vec![b'a'; 65536]); let b = f.write("second", vec![b'b'; 65536]);
        let target = f.path("out/model.mesh");
        thread::scope(|scope| for i in 0..16 { let target = &target; let source = if i % 2 == 0 { &a } else { &b }; scope.spawn(move || carry_file(source, target).unwrap()); });
        let result = fs::read(&target).unwrap(); assert!(result == fs::read(a).unwrap() || result == fs::read(b).unwrap());
        assert_eq!(fs::read_dir(target.parent().unwrap()).unwrap().count(), 1);
        assert_eq!(target.metadata().unwrap().permissions().mode() & 0o200, 0o200);
    }

    #[test]
    fn publication_queue_starts_first_output_and_coalesces_to_latest_after_failure() {
        let f = Fixture::new(); let lease = f.lease(); f.write("held", "first\n");
        let publisher = f.script("publisher", "cat held >> published\ntouch publication-started\nwhile [ ! -f release ]; do sleep 0.01; done\nif [ ! -f first-finished ]; then touch first-finished; exit 7; fi\nexit 0");
        let run = f.path("run"); fs::create_dir(&run).unwrap();
        let mut queue = PublicationQueue::new(&f.0, &run, &publisher, &lease);
        queue.request().unwrap(); wait_for(&f.path("publication-started"));
        f.write("held", "intermediate\n"); queue.request().unwrap();
        f.write("held", "latest\n"); queue.request().unwrap();
        assert_eq!(queue.record.started, 1); f.write("release", ""); queue.drain().unwrap();
        assert_eq!(queue.record.requests, 3); assert_eq!(queue.record.started, 2); assert_eq!(queue.record.coalesced, 2);
        assert_eq!(queue.record.exit_codes, [7, 0]); assert_eq!(fs::read_to_string(f.path("published")).unwrap(), "first\nlatest\n");
    }

    #[test]
    fn recursive_file_sets_wait_for_missing_children_and_do_not_loop_on_cycles() {
        let mut sets = BTreeMap::new();
        sets.insert("parent".into(), FileSet { files: vec![FileEntry { name: "a".into(), uri: None }], file_sets: vec![SetId { id: "child".into() }] });
        assert!(files_for("parent", &sets, &mut BTreeSet::new()).is_none());
        sets.insert("child".into(), FileSet { files: vec![FileEntry { name: "b".into(), uri: None }], file_sets: vec![SetId { id: "parent".into() }] });
        assert_eq!(files_for("parent", &sets, &mut BTreeSet::new()).unwrap().into_iter().map(|file| file.name).collect::<Vec<_>>(), ["a", "b"]);
    }

    #[test]
    fn local_file_uris_decode_spaces_unicode_and_literal_percent_signs() {
        let path = Path::new("/work/action dir/水%/hardware/model.step.mesh");
        assert_eq!(file_uri(&path_uri(path)).unwrap(), path);
        assert_eq!(file_uri("file://localhost/work/model.mesh").unwrap(), Path::new("/work/model.mesh"));
        assert!(file_uri("https://example.com/model.mesh").is_err());
        assert!(file_uri("file://another-host/work/model.mesh").is_err());
    }

    #[test]
    fn raw_glb_replacement_stays_inside_named_v4_views() {
        let f = Fixture::new(); let payload = f.path("scene.mesh");
        let pcb = "hardware/pcb/pcba/out/pcba.glb.mesh";
        f.write("scene.mesh", "stale unrelated mesh");
        assert!(!raw_export_replaced(pcb, &payload).unwrap());
        let named = "hardware/assembly/scenes/glb/install.glb.mesh";
        let mut current = head(true); current["step_export"] = json!(true);
        scene(&payload, &current);
        assert!(raw_export_replaced(named, &payload).unwrap());
        assert!(!raw_export_replaced(pcb, &payload).unwrap());
        current["v"] = json!(3); current["step_export"] = json!(false);
        scene(&payload, &current);
        assert!(!raw_export_replaced(named, &payload).unwrap());
    }

    fn configuration(f: &Fixture) -> Config {
        Config { root: f.0.clone(), run_dir: Some(f.path("run")),
            runner: Some(f.script("runner", "test \"$1\" = --\nshift\nexec \"$@\"")),
            bazel: f.path("bazel"), publisher: Some(f.path("publisher")), progress: None,
            bazel_args: vec!["//:fixture".into()] }
    }

    #[test]
    fn completed_bep_producers_publish_before_build_exit_and_preserve_bazel_failure() {
        let f = Fixture::new(); let first = "hardware/first.step.mesh"; let second = "hardware/second.step.mesh"; let stl = "hardware/first.stl";
        let a = f.path(&format!("action dir/{first}")); let b = f.path(&format!("action dir/{second}")); scene(&a, &head(true)); scene(&b, &head(true));
        f.write(&format!("action dir/{stl}"), "print triangles"); f.write("hardware/first.step", "obsolete STEP");
        f.json("tools/bazel/graph.json", json!({"first":{"writes":[first,stl]},"second":{"writes":[second]}}));
        let first_event = json!({"id":{"actionCompleted":{"label":"//:first"}},"action":{"success":true,"primaryOutput":{"name":first,"uri":path_uri(&a)}}});
        let later = [
            json!({"id":{"targetCompleted":{"label":"//:second"}},"completed":{"success":true,"outputGroup":[{"fileSets":[{"id":"parent"}]}]}}),
            json!({"id":{"namedSet":{"id":"parent"}},"namedSetOfFiles":{"fileSets":[{"id":"child"}]}}),
            json!({"id":{"namedSet":{"id":"child"}},"namedSetOfFiles":{"files":[{"name":format!("out/config/{second}"),"uri":path_uri(&b)}]}}),
        ].into_iter().map(|row| row.to_string()).collect::<Vec<_>>().join("\n");
        f.script("bazel", &format!("events=\nfor arg in \"$@\"; do case \"$arg\" in --build_event_json_file=*) events=${{arg#*=}};; esac; done\ntest -n \"$events\"\nprintf '%s\\n' {} > \"$events\"\ni=0\nwhile [ ! -f publication-started ]; do i=$((i+1)); test \"$i\" -lt 500; sleep 0.01; done\nprintf '%s' {} >> \"$events\"\ntouch build-finished\nexit 6", shell(&first_event.to_string()), shell(&later)));
        f.script("publisher", "test \"$1\" = --root\ntest \"$2\" = \"$PWD\"\nif [ ! -f build-finished ]; then touch first-published-before-build-exit; fi\ntouch publication-started\nexit 0");
        assert_eq!(run(configuration(&f)).unwrap(), 6);
        assert!(f.path("first-published-before-build-exit").exists());
        assert_eq!(fs::read(f.path(first)).unwrap(), fs::read(a).unwrap()); assert_eq!(fs::read(f.path(second)).unwrap(), fs::read(b).unwrap());
        assert_eq!(fs::read_to_string(f.path(stl)).unwrap(), "print triangles"); assert!(!f.path("hardware/first.step").exists());
        let record: Value = serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert_eq!(record["success"], false); assert!(record["publication_queue"]["started"].as_u64().unwrap() >= 1); assert!(!f.path("run/events.jsonl").exists());
    }

    #[test]
    fn declared_pcb_raw_glb_carries_and_survives_its_mesh_sibling() {
        let f = Fixture::new();
        let name = "hardware/pcb/pcba/out/pcba.glb";
        let sibling = format!("{name}.mesh");
        let texture = "hardware/pcb/pcba/out/pcba-material.png";
        f.write(name, "held raw PCB GLB"); f.write(texture, "retained external texture");
        scene(&f.path(&sibling), &head(false));
        let source = f.write(&format!("action/{name}"), "fresh raw PCB GLB with external texture");
        let mesh = f.path(&format!("action/{sibling}")); scene(&mesh, &head(true));
        f.json("tools/bazel/graph.json", json!({"board":{"writes":[name,sibling]}}));
        let event = json!({"id":{"actionCompleted":{"label":"//:board"}},"action":{"success":true,"primaryOutput":{"name":name,"uri":path_uri(&source)}}});
        f.script("bazel", &format!("for arg in \"$@\"; do case \"$arg\" in --build_event_json_file=*) events=${{arg#*=}};; esac; done\nprintf '%s\\n' {} > \"$events\"\nexit 0", shell(&event.to_string())));
        f.script("publisher", &format!("cmp {} {}\ntest -f {}\nexit 0", shell(name), shell(&format!("action/{name}")), shell(texture)));
        assert_eq!(run(configuration(&f)).unwrap(), 0);
        assert_eq!(fs::read(f.path(name)).unwrap(), fs::read(source).unwrap());
        assert_eq!(fs::read(f.path(&sibling)).unwrap(), fs::read(mesh).unwrap());
        assert_eq!(fs::read_to_string(f.path(texture)).unwrap(), "retained external texture");
        let record: Value = serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert!(record["publication_queue"]["started"].as_u64().unwrap() >= 1);
    }

    #[test]
    fn publisher_failure_changes_a_successful_build_exit_to_failure() {
        let f = Fixture::new(); let name = "hardware/model.stl"; let source = f.write(&format!("action/{name}"), "solid");
        f.json("tools/bazel/graph.json", json!({"model":{"writes":[name]}}));
        let event = json!({"id":{"actionCompleted":{"label":"//:model"}},"action":{"success":true,"primaryOutput":{"name":name,"uri":path_uri(&source)}}});
        f.script("bazel", &format!("for arg in \"$@\"; do case \"$arg\" in --build_event_json_file=*) events=${{arg#*=}};; esac; done\nprintf '%s\\n' {} > \"$events\"\nexit 0", shell(&event.to_string())));
        f.script("publisher", "exit 9"); assert_eq!(run(configuration(&f)).unwrap(), 1);
        let record: Value = serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert_eq!(record["success"], false); assert!(record["publication_queue"]["exit_codes"].as_array().unwrap().contains(&json!(9)));
    }

    #[test]
    fn unchanged_checkpoints_preserve_inode_but_unserved_outputs_still_publish() {
        for served in [true, false] {
            let f = Fixture::new(); let name = "hardware/model.step.mesh";
            let target = f.path(name); let source = f.path(&format!("action/{name}")); scene(&target, &head(true)); scene(&source, &head(false));
            let before = target.metadata().unwrap().ino();
            f.json("tools/bazel/graph.json", json!({"model":{"writes":[name]}}));
            f.json("hardware/cad-artifacts.json", json!({"solids":{name:if served { file_digest(&target).unwrap() } else {"other".to_owned()}}}));
            let row = json!({"stage":"mechanics","files":[source]});
            f.script("bazel", &format!("printf '%s\\n' 'invalid' '[]' {} >> \"$HSM_BUILD_PROGRESS\"\nexit 0", shell(&row.to_string())));
            f.script("publisher", "exit 0"); assert_eq!(run(configuration(&f)).unwrap(), 0);
            assert_eq!(target.metadata().unwrap().ino(), before);
            let record: Value = serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
            assert_eq!(record["checkpoint_errors"].as_array().unwrap().len(), 2);
            assert_eq!(record["suppressed_checkpoints"][0]["files"][0], name);
            assert_eq!(record["publication_queue"]["started"], if served {0} else {1});
        }
    }

    #[test]
    fn advisory_preview_failure_keeps_the_normal_build_available() {
        let f = Fixture::new(); let source = f.write("hardware/layout.json", "moved");
        let receipt = format!(".cache/realized/installed-machine/receipts/{:x}.json", Sha256::digest(b"presentation-state"));
        f.json(&receipt, json!({"value":{"inputs":{"hardware/layout.json":"previous"}}}));
        assert!(source.exists()); f.json("tools/bazel/graph.json", json!({}));
        f.script("bazel", "for arg in \"$@\"; do if [ \"$arg\" = --check_up_to_date ]; then exit 3; fi; done\ntouch normal-build-ran\nexit 0");
        let mut config = configuration(&f); config.bazel_args = vec!["//:installed-machine".into()];
        assert_eq!(run(config).unwrap(), 0); assert!(f.path("normal-build-ran").exists());
        let record: Value = serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert_eq!(record["preview"][0]["phase"], "current-program"); assert_eq!(record["preview"][0]["exit_code"], 3);
    }

    #[test]
    fn retained_placement_preview_reaches_publication_before_the_normal_build_finishes() {
        let f = Fixture::new(); let name = "hardware/manifold-layout/enclosure-assembly.step.mesh";
        f.write("hardware/layout.json", "moved");
        let receipt = format!(".cache/realized/installed-machine/receipts/{:x}.json", Sha256::digest(b"presentation-state"));
        f.json(&receipt, json!({"value":{"inputs":{"hardware/layout.json":"previous"}}}));
        f.json("tools/bazel/graph.json", json!({"installed-machine":{"writes":[name]}}));
        let source = f.path(&format!("run/placement-preview/{name}")); scene(&source, &head(false));
        let checkpoint = json!({"stage":"placements","files":[source]});
        f.script("bazel-bin/out/installed-machine-program/installed-machine", &format!(
            "test \"$1\" = {}\ntest \"$2\" = --placements-only\nprintf '%s\\n' placements >> phases\nprintf '%s\\n' {} >> \"$HSM_BUILD_PROGRESS\"\nexit 0",
            shell(&f.path("run/placement-preview").to_string_lossy()), shell(&checkpoint.to_string())));
        f.script("bazel", "for arg in \"$@\"; do if [ \"$arg\" = --check_up_to_date ]; then printf '%s\\n' current-program >> phases; exit 0; fi; done\nprintf '%s\\n' normal-build >> phases\ni=0\nwhile [ ! -f publication-started ]; do i=$((i+1)); test \"$i\" -lt 500; sleep 0.01; done\ntouch build-finished\nexit 0");
        f.script("publisher", "if [ ! -f build-finished ]; then touch preview-published-before-build-exit; fi\ntouch publication-started\nexit 0");
        let mut config = configuration(&f); config.bazel_args = vec!["//:installed-machine".into()];
        assert_eq!(run(config).unwrap(), 0);
        assert!(f.path("preview-published-before-build-exit").exists());
        assert_eq!(fs::read_to_string(f.path("phases")).unwrap(), "current-program\nplacements\nnormal-build\n");
        assert_eq!(fs::read(f.path(name)).unwrap(), fs::read(source).unwrap());
        let record: Value = serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert_eq!(record["preview"][0]["exit_code"], 0); assert_eq!(record["preview"][1]["exit_code"], 0);
        assert_eq!(record["carried"][0]["stage"], "placements"); assert_eq!(record["success"], true);
    }
}
