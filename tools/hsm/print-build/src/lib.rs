//! Native producer orchestration carries completed files and publishes useful views while other work continues.
mod native;
use anyhow::{Context, Result, ensure};
use hsm_build_plan::{
    planning::{self, Plan},
    receipt::{RunReceipt, TargetReceipt, TargetStatus},
};
use hsm_run_slots::Lease;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet},
    env,
    fs::{self, File, OpenOptions},
    io::{Read, Seek, SeekFrom, Write},
    os::unix::{
        fs::{MetadataExt, OpenOptionsExt},
        process::ExitStatusExt,
    },
    path::{Path, PathBuf},
    process::{Child, Command, ExitStatus},
    sync::atomic::{AtomicU64, Ordering},
    thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};
const POLL: Duration = Duration::from_millis(10);
static TEMPORARY: AtomicU64 = AtomicU64::new(0);

/// Commands and paths select a native checkout, its engine and its progressive publication.
#[derive(Debug, Clone)]
pub struct Config {
    pub root: PathBuf,
    pub run_dir: Option<PathBuf>,
    pub runner: Option<PathBuf>,
    pub engine: Option<PathBuf>,
    pub publisher: Option<PathBuf>,
    pub progress: Option<PathBuf>,
    pub selectors: Vec<String>,
    pub publish: bool,
    pub check_current: bool,
}
impl Config {
    pub fn defaults() -> Result<Self> {
        let root = env::var_os("HSM_WORKSPACE")
            .map(PathBuf::from)
            .unwrap_or_else(|| {
                Path::new(env!("CARGO_MANIFEST_DIR"))
                    .ancestors()
                    .nth(3)
                    .unwrap()
                    .to_owned()
            });
        Ok(Self {
            root,
            run_dir: None,
            runner: None,
            engine: None,
            publisher: None,
            progress: None,
            selectors: Vec::new(),
            publish: true,
            check_current: false,
        })
    }
}
#[derive(Debug, Deserialize)]
struct Checkpoint {
    files: Vec<PathBuf>,
    #[serde(default)]
    stage: Option<String>,
}

/// A tail keeps incomplete writes until their terminating newline arrives.
struct Tail {
    path: PathBuf,
    stream: Option<File>,
    pending: Vec<u8>,
}

impl Tail {
    fn progress(path: PathBuf) -> Result<Self> {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        let mut stream = OpenOptions::new()
            .create(true)
            .read(true)
            .append(true)
            .open(&path)?;
        stream.seek(SeekFrom::End(0))?;
        Ok(Self {
            path,
            stream: Some(stream),
            pending: Vec::new(),
        })
    }
    fn poll(&mut self, final_chunk: bool) -> Result<Vec<Vec<u8>>> {
        if self.stream.is_none() {
            match File::open(&self.path) {
                Ok(file) => self.stream = Some(file),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()),
                Err(error) => return Err(error.into()),
            }
        }
        self.stream
            .as_mut()
            .unwrap()
            .read_to_end(&mut self.pending)?;
        let mut rows = Vec::new();
        let mut start = 0;
        for (index, byte) in self.pending.iter().enumerate() {
            if *byte == b'\n' {
                rows.push(self.pending[start..index].to_vec());
                start = index + 1;
            }
        }
        if final_chunk && start < self.pending.len() {
            rows.push(self.pending[start..].to_vec());
            start = self.pending.len();
        }
        self.pending.drain(..start);
        rows.retain(|row| row.iter().any(|byte| !byte.is_ascii_whitespace()));
        Ok(rows)
    }
}

#[derive(Debug, Default, Deserialize)]
struct Pointers {
    #[serde(default)]
    solids: BTreeMap<String, String>,
    #[serde(default)]
    sidecars: BTreeMap<String, String>,
}

#[derive(Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Signature {
    path: PathBuf,
    device: u64,
    inode: u64,
    size: u64,
    mtime: (i64, i64),
    ctime: (i64, i64),
}

/// Publication debt follows the served pointer and exact completed output bytes.
struct Publications {
    served: BTreeMap<String, String>,
    digests: BTreeMap<Signature, String>,
    requested: BTreeSet<(String, String)>,
}

impl Publications {
    fn new(root: &Path) -> Self {
        let mut pointers: Pointers = fs::read(root.join("hardware/cad-artifacts.json"))
            .ok()
            .and_then(|bytes| serde_json::from_slice(&bytes).ok())
            .unwrap_or_default();
        pointers.solids.append(&mut pointers.sidecars);
        Self {
            served: pointers.solids,
            digests: BTreeMap::new(),
            requested: BTreeSet::new(),
        }
    }
    fn needs(&mut self, name: &str, path: &Path, changed: bool) -> Result<bool> {
        if !self.served.contains_key(name)
            && ![".mesh", ".stl", ".step", ".glb"]
                .iter()
                .any(|suffix| name.ends_with(suffix))
        {
            return Ok(false);
        }
        let stat = path.metadata()?;
        let signature = Signature {
            path: path.to_owned(),
            device: stat.dev(),
            inode: stat.ino(),
            size: stat.len(),
            mtime: (stat.mtime(), stat.mtime_nsec()),
            ctime: (stat.ctime(), stat.ctime_nsec()),
        };
        let digest = if let Some(digest) = self.digests.get(&signature) {
            digest.clone()
        } else {
            let digest = file_digest(path)?;
            self.digests.insert(signature, digest.clone());
            digest
        };
        let key = (name.to_owned(), digest.clone());
        if !changed && (self.served.get(name) == Some(&digest) || self.requested.contains(&key)) {
            return Ok(false);
        }
        self.requested.insert(key);
        Ok(true)
    }
}

#[derive(Debug, Default, Serialize)]
struct QueueRecord {
    requests: usize,
    started: usize,
    coalesced: usize,
    exit_codes: Vec<i32>,
}

/// A running publisher consumes completed bytes while later requests coalesce into its successor.
struct PublicationQueue<'a> {
    root: &'a Path,
    run: &'a Path,
    executable: &'a Path,
    lease: &'a Lease,
    active: Option<Child>,
    pending: bool,
    record: QueueRecord,
    enabled: bool,
}

impl<'a> PublicationQueue<'a> {
    fn new(
        root: &'a Path,
        run: &'a Path,
        executable: &'a Path,
        lease: &'a Lease,
        enabled: bool,
    ) -> Self {
        Self {
            root,
            run,
            executable,
            lease,
            active: None,
            pending: false,
            record: QueueRecord::default(),
            enabled,
        }
    }
    fn request(&mut self) -> Result<()> {
        if !self.enabled {
            return Ok(());
        }
        self.record.requests += 1;
        if let Some(child) = &mut self.active {
            if child.try_wait()?.is_none() {
                self.record.coalesced += 1;
            }
        }
        self.pending = true;
        self.poll()
    }
    fn poll(&mut self) -> Result<()> {
        if let Some(child) = &mut self.active {
            if let Some(code) = child.try_wait()? {
                self.record.exit_codes.push(exit_code(code));
                self.active = None;
            }
        }
        if self.active.is_none() && self.pending {
            let log = File::create(
                self.run
                    .join(format!("publish-{}.log", self.record.started)),
            )?;
            let mut command = Command::new(self.executable);
            command
                .arg("--root")
                .arg(self.root)
                .current_dir(self.root)
                .stdout(log.try_clone()?)
                .stderr(log);
            self.lease.apply(&mut command)?;
            self.active = Some(
                command
                    .spawn()
                    .with_context(|| format!("start {}", self.executable.display()))?,
            );
            self.pending = false;
            self.record.started += 1;
        }
        Ok(())
    }
    fn drain(&mut self) -> Result<()> {
        while self.active.is_some() || self.pending {
            self.poll()?;
            if let Some(child) = &mut self.active {
                child.wait()?;
            }
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
            unsafe {
                libc::kill(self.0.id() as libc::pid_t, libc::SIGTERM);
            }
            let _ = self.0.wait();
        }
    }
}

#[derive(Debug, Serialize)]
struct Carried {
    seconds: f64,
    wall_time_ns: u128,
    files: Vec<String>,
    publication: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    stage: Option<String>,
}

#[derive(Debug, Serialize)]
struct Suppressed {
    seconds: f64,
    stage: String,
    files: Vec<String>,
}

#[derive(Debug, Serialize)]
struct Preview {
    phase: &'static str,
    seconds: f64,
    available: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
}

struct Driver<'a> {
    root: &'a Path,
    outputs: BTreeSet<String>,
    started: Instant,
    publication: Publications,
    publishing: PublicationQueue<'a>,
    carried: Vec<Carried>,
    suppressed: Vec<Suppressed>,
}
impl<'a> Driver<'a> {
    fn new(
        root: &'a Path,
        outputs: BTreeSet<String>,
        started: Instant,
        publishing: PublicationQueue<'a>,
    ) -> Self {
        Self {
            root,
            outputs,
            started,
            publication: Publications::new(root),
            publishing,
            carried: Vec::new(),
            suppressed: Vec::new(),
        }
    }
    fn carry(&mut self, outputs: &BTreeMap<String, PathBuf>, stage: Option<&str>) -> Result<()> {
        let mut moved = Vec::new();
        let mut ready = Vec::new();
        let mut status_only = Vec::new();
        for (name, source) in outputs {
            if !self.outputs.contains(name) || !source.is_file() {
                continue;
            }
            let target = self.root.join(native::repository_path(name)?);
            let mut changed = !same_file_bytes(source, &target)?;
            if changed
                && stage.is_some()
                && name.ends_with(".mesh")
                && unchanged_checkpoint(source, &target)
            {
                status_only.push(name.clone());
                changed = false;
            }
            if changed {
                carry_file(source, &target)?;
                moved.push(name.clone());
            }
            if self.publication.needs(name, &target, changed)? {
                ready.push(name.clone());
            }
            if name.ends_with(".mesh") && raw_export_replaced(name, &target)? {
                let old = PathBuf::from(
                    target
                        .as_os_str()
                        .to_string_lossy()
                        .trim_end_matches(".mesh"),
                );
                if old.is_file() {
                    fs::remove_file(old)?;
                }
            }
        }
        if !status_only.is_empty() {
            self.suppressed.push(Suppressed {
                seconds: self.started.elapsed().as_secs_f64(),
                stage: stage.unwrap().to_owned(),
                files: status_only,
            });
        }
        if !moved.is_empty() || !ready.is_empty() {
            if !moved.is_empty() {
                println!("[print-build] carried {}", moved.join(", "));
            } else {
                println!(
                    "[print-build] completed outputs await publication: {}",
                    ready.join(", ")
                );
            }
            std::io::stdout().flush()?;
            self.carried.push(Carried {
                seconds: self.started.elapsed().as_secs_f64(),
                wall_time_ns: SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos(),
                files: moved,
                publication: ready.clone(),
                stage: stage.map(str::to_owned),
            });
        }
        if !ready.is_empty() {
            self.publishing.request()?;
        }
        Ok(())
    }
    fn checkpoints(&mut self, progress: &mut Option<Tail>, errors: &mut Vec<String>) {
        let Some(progress) = progress else { return };
        match progress.poll(false) {
            Ok(lines) => {
                for line in lines {
                    match serde_json::from_slice::<Checkpoint>(&line) {
                        Ok(row) => {
                            let outputs = row
                                .files
                                .iter()
                                .filter(|path| path.is_absolute())
                                .filter_map(|source| {
                                    let name = self.outputs.iter().find(|rel| {
                                        source.to_string_lossy().ends_with(&format!("/{rel}"))
                                    })?;
                                    Some((name.clone(), source.clone()))
                                })
                                .collect();
                            if let Err(error) = self.carry(&outputs, row.stage.as_deref()) {
                                errors.push(format!("{error:#}"));
                            }
                        }
                        Err(error) => errors.push(error.to_string()),
                    }
                }
            }
            Err(error) => errors.push(error.to_string()),
        }
    }
}

#[derive(Debug, Deserialize)]
struct Receipt {
    value: PresentationState,
}
#[derive(Debug, Deserialize)]
struct PresentationState {
    inputs: BTreeMap<String, String>,
}

/// Retained placement inputs select the advisory preview before dependent geometry rebuilds.
pub fn placement_changed(args: &[String], root: &Path) -> bool {
    if !args.is_empty()
        && !args.iter().any(|arg| {
            let name = arg.trim_start_matches("//:").trim_start_matches(':');
            ["installed-machine", "everything"].contains(&name) || name.starts_with("enclosure-")
        })
    {
        return false;
    }
    let name = format!("{:x}.json", Sha256::digest(b"presentation-state"));
    let read = || -> Result<bool> {
        let receipt: Receipt = serde_json::from_slice(&fs::read(
            root.join(".cache/realized/installed-machine/receipts")
                .join(name),
        )?)?;
        ensure!(
            !receipt.value.inputs.is_empty(),
            "placement receipt has no inputs"
        );
        for (path, expected) in receipt.value.inputs {
            if file_digest(&root.join(path))? != expected {
                return Ok(true);
            }
        }
        Ok(false)
    };
    read().unwrap_or(false)
}

#[derive(Debug, Deserialize)]
struct IterationStatus {
    #[serde(default)]
    complete: bool,
}
#[derive(Debug, Deserialize)]
struct MeshHeader {
    #[serde(default)]
    v: Option<u32>,
    #[serde(default)]
    step_export: Option<bool>,
    #[serde(default)]
    iteration: Option<IterationStatus>,
    #[serde(flatten)]
    content: BTreeMap<String, Value>,
}

fn mesh_header(path: &Path, complete_header: bool) -> Result<MeshHeader> {
    let mut file = File::open(path)?;
    let mut size = [0; 4];
    file.read_exact(&mut size)?;
    let size = u32::from_le_bytes(size) as usize;
    ensure!(
        size as u64 <= file.metadata()?.len().saturating_sub(4),
        "truncated mesh header"
    );
    let mut bytes = vec![0; size];
    file.read_exact(&mut bytes)?;
    let head = serde_json::from_slice(&bytes)?;
    if complete_header {
        let mut byte = [0];
        ensure!(
            file.read(&mut byte)? == 0,
            "mesh has geometry after its shared header"
        );
    }
    Ok(head)
}

// Shared meshes replace raw GLBs only inside the viewer's named assembly-view directory.
fn raw_export_replaced(name: &str, payload: &Path) -> Result<bool> {
    let glb = name.ends_with(".glb.mesh");
    if glb && !name.starts_with("hardware/assembly/scenes/glb/") {
        return Ok(false);
    }
    let head = mesh_header(payload, false)?;
    Ok(head.v == Some(4) && (glb || head.step_export == Some(false)))
}

fn same_geometry(a: MeshHeader, b: MeshHeader) -> bool {
    a.v == b.v && a.step_export == b.step_export && a.content == b.content
}

/// Status-only intermediate checkpoints retain the held scene's inode and completed identity.
pub fn unchanged_checkpoint(source: &Path, target: &Path) -> bool {
    let compare = || -> Result<bool> {
        let incoming = mesh_header(source, true)?;
        let held = mesh_header(target, true)?;
        if incoming.v != Some(4)
            || held.v != Some(4)
            || incoming
                .iteration
                .as_ref()
                .is_some_and(|status| status.complete)
        {
            return Ok(false);
        }
        Ok(same_geometry(incoming, held))
    };
    compare().unwrap_or(false)
}

fn same_file_bytes(source: &Path, target: &Path) -> Result<bool> {
    let mut incoming = File::open(source)?;
    let mut held = match File::open(target) {
        Ok(file) => file,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
        Err(error) => return Err(error.into()),
    };
    if incoming.metadata()?.len() != held.metadata()?.len() {
        return Ok(false);
    }
    let mut a = [0u8; 65536];
    let mut b = [0u8; 65536];
    loop {
        let na = incoming.read(&mut a)?;
        let nb = held.read(&mut b)?;
        if na != nb || a[..na] != b[..nb] {
            return Ok(false);
        }
        if na == 0 {
            return Ok(true);
        }
    }
}

struct Temporary(PathBuf);
impl Drop for Temporary {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

/// Independent same-directory copies make completed producer replacement atomic under concurrent carries.
pub fn carry_file(source: &Path, target: &Path) -> Result<()> {
    let parent = target.parent().context("output parent")?;
    fs::create_dir_all(parent)?;
    let (temporary, mut output) = loop {
        let serial = TEMPORARY.fetch_add(1, Ordering::Relaxed);
        let path = parent.join(format!(
            ".{}.carry-{}-{serial}",
            target.file_name().context("output name")?.to_string_lossy(),
            std::process::id()
        ));
        match OpenOptions::new()
            .create_new(true)
            .write(true)
            .mode(0o600)
            .open(&path)
        {
            Ok(file) => break (Temporary(path), file),
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error.into()),
        }
    };
    std::io::copy(&mut File::open(source)?, &mut output)?;
    output.flush()?;
    drop(output);
    fs::rename(&temporary.0, target)?;
    Ok(())
}

fn file_digest(path: &Path) -> Result<String> {
    let mut file = File::open(path)?;
    let mut digest = Sha256::new();
    let mut bytes = [0u8; 65536];
    loop {
        let n = file.read(&mut bytes)?;
        if n == 0 {
            break;
        }
        digest.update(&bytes[..n]);
    }
    Ok(format!("{:x}", digest.finalize()))
}

fn exit_code(status: ExitStatus) -> i32 {
    status
        .code()
        .unwrap_or_else(|| 128 + status.signal().unwrap_or(1))
}

fn relative(root: &Path, path: PathBuf) -> PathBuf {
    if path.is_absolute() {
        path
    } else {
        root.join(path)
    }
}

fn executable(root: &Path, name: &str, configured: Option<PathBuf>) -> PathBuf {
    if let Some(path) = configured {
        return if path.components().count() == 1 {
            path
        } else {
            relative(root, path)
        };
    }
    let beside = env::current_exe()
        .ok()
        .and_then(|exe| exe.parent().map(|parent| parent.join(name)));
    let local = root.join("tools/hsm/target/release").join(name);
    if let Some(path) = beside.filter(|path| path.is_file()) {
        return path;
    }
    if local.is_file() {
        return local;
    }
    if name == "hsm-run" {
        #[derive(Deserialize)]
        struct Runtime {
            runner: PathBuf,
        }
        #[allow(deprecated)]
        let home = env::home_dir();
        if let Some(runtime) = home
            .and_then(|home| fs::read(home.join(".local/lib/hsm/runtime.json")).ok())
            .and_then(|bytes| serde_json::from_slice::<Runtime>(&bytes).ok())
            .filter(|runtime| runtime.runner.is_file())
        {
            return runtime.runner;
        }
    }
    name.into()
}

fn wrapped(
    runner: &Path,
    root: &Path,
    program: &Path,
    args: &[String],
    lease: &Lease,
) -> Result<Command> {
    let mut command = Command::new(runner);
    command
        .arg("--")
        .arg(program)
        .args(args)
        .current_dir(root)
        .env("HSM_WORKSPACE", root);
    lease.apply(&mut command)?;
    Ok(command)
}

fn write_receipt(path: &Path, value: &impl Serialize) -> Result<()> {
    let temporary = Temporary(path.with_file_name(format!(
        ".receipt-{}-{}.json",
        std::process::id(),
        TEMPORARY.fetch_add(1, Ordering::Relaxed)
    )));
    fs::write(&temporary.0, serde_json::to_vec_pretty(value)?)?;
    fs::rename(&temporary.0, path)?;
    Ok(())
}

fn unavailable(action: &planning::Action, status: TargetStatus, error: String) -> TargetReceipt {
    TargetReceipt {
        status,
        declared_outputs: action.outputs().map(str::to_owned).collect(),
        outputs: BTreeMap::new(),
        extra: BTreeMap::from([("error".into(), json!(error))]),
    }
}

/// A native request keeps one verified lease through declared producer work and progressive publication.
pub fn run(config: Config) -> Result<i32> {
    let root = fs::canonicalize(&config.root)
        .with_context(|| format!("checkout {}", config.root.display()))?;
    let plan = planning::action_plan(&root, None)?;
    run_plan(config, plan)
}

fn run_plan(config: Config, plan: Plan) -> Result<i32> {
    let root = fs::canonicalize(&config.root)
        .with_context(|| format!("checkout {}", config.root.display()))?;
    let lease = hsm_run_slots::acquire(
        "print-build",
        hsm_run_slots::inherited()?,
        env::var("HSM_RUN_TIMING").is_ok_and(|value| value == "1"),
    )?;
    let runner = executable(&root, "hsm-run", config.runner);
    let engine = executable(&root, "hsm", config.engine);
    let publisher = executable(&root, "hsm-publish", config.publisher);
    let started_unix_ns = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
    let run_id = format!("{started_unix_ns}-{}", std::process::id());
    let run = config
        .run_dir
        .map(|path| relative(&root, path))
        .unwrap_or_else(|| {
            root.join(".cache/runs")
                .join(format!("print-build-{run_id}"))
        });
    fs::create_dir_all(&run)?;
    let started = Instant::now();
    let selection = plan.select(&config.selectors)?;
    let outputs = plan
        .actions
        .values()
        .flat_map(|action| action.outputs().map(str::to_owned))
        .collect();
    let publishing = PublicationQueue::new(
        &root,
        &run,
        &publisher,
        &lease,
        config.publish && !config.check_current,
    );
    let mut driver = Driver::new(&root, outputs, started, publishing);
    let progress_path = config
        .progress
        .map(|path| relative(&root, path))
        .unwrap_or_else(|| run.join("progress.jsonl"));
    let mut checkpoint_errors = Vec::new();
    let mut progress = if config.check_current {
        None
    } else {
        match Tail::progress(progress_path.clone()) {
            Ok(tail) => Some(tail),
            Err(error) => {
                checkpoint_errors.push(error.to_string());
                None
            }
        }
    };
    let source_commit = Command::new("git")
        .args(["rev-parse", "HEAD"])
        .current_dir(&root)
        .output()
        .ok()
        .filter(|output| output.status.success())
        .map(|output| String::from_utf8_lossy(&output.stdout).trim().to_owned());
    let mut receipt = RunReceipt {
        requested: selection.requested.clone(),
        selected: selection.closure.clone(),
        ..RunReceipt::default()
    };
    receipt.extra.extend(BTreeMap::from([
        ("run_id".into(), json!(run_id)),
        ("started_unix_ns".into(), json!(started_unix_ns)),
        ("source_commit".into(), json!(source_commit)),
        ("completed".into(), json!(false)),
        (
            "full_build".into(),
            json!(selection.closure == plan.default_targets()),
        ),
        ("check_current".into(), json!(config.check_current)),
    ]));
    let receipt_path = run.join("receipt.json");
    write_receipt(&receipt_path, &receipt)?;
    let mut preview = Vec::new();
    if !config.check_current
        && progress.is_some()
        && placement_changed(
            &selection.requested.iter().cloned().collect::<Vec<_>>(),
            &root,
        )
    {
        if let Some(action) = plan.actions.get("installed-machine") {
            let phase = Instant::now();
            let prepass = (|| -> Result<bool> {
                let stage = native::Stage::prepare(
                    &root,
                    &run,
                    "placement-preview",
                    &plan.runtime_inputs("installed-machine")?,
                    &receipt.targets,
                    true,
                )?;
                let ask = native::RunAsk::new(&root, &stage, action, &progress_path, true, false);
                let mut invocation = native::Invocation::start(
                    &root,
                    &run,
                    &runner,
                    &engine,
                    &lease,
                    "placement-preview",
                    stage,
                    ask,
                )?;
                loop {
                    driver.checkpoints(&mut progress, &mut checkpoint_errors);
                    driver.publishing.poll()?;
                    if let Some(done) = invocation.poll()? {
                        driver.checkpoints(&mut progress, &mut checkpoint_errors);
                        let answer = done
                            .answer
                            .as_ref()
                            .map_err(|error| anyhow::anyhow!(error.clone()))?;
                        if answer.available {
                            driver.carry(&answer.artifacts, Some("placements"))?;
                        }
                        return Ok(answer.available);
                    }
                    thread::sleep(POLL);
                }
            })();
            preview.push(Preview {
                phase: "placements",
                seconds: phase.elapsed().as_secs_f64(),
                available: prepass.as_ref().is_ok_and(|available| *available),
                error: prepass.err().map(|error| format!("{error:#}")),
            });
        }
    }
    let mut pending = selection.closure.clone();
    let mut active: Vec<native::Invocation> = Vec::new();
    let mut code = 0;
    while !pending.is_empty() || !active.is_empty() {
        driver.checkpoints(&mut progress, &mut checkpoint_errors);
        driver.publishing.poll()?;
        for target in &selection.order {
            if !pending.contains(target) {
                continue;
            }
            let action = &plan.actions[target];
            let failed = action
                .dependencies
                .iter()
                .filter(|dependency| {
                    receipt
                        .targets
                        .get(*dependency)
                        .is_some_and(|result| !result.status.usable())
                })
                .cloned()
                .collect::<Vec<_>>();
            if !failed.is_empty() {
                receipt.targets.insert(
                    target.clone(),
                    unavailable(
                        action,
                        TargetStatus::Blocked,
                        format!("unavailable prerequisites: {}", failed.join(", ")),
                    ),
                );
                pending.remove(target);
                code = code.max(1);
                write_receipt(&receipt_path, &receipt)?;
            }
        }
        // The engine retains the host and memory admission policy; these clients expose independent replies.
        while active.len() < 2 {
            let target = selection
                .order
                .iter()
                .find(|target| {
                    pending.contains(*target)
                        && plan.actions[*target].dependencies.iter().all(|dependency| {
                            receipt
                                .targets
                                .get(dependency)
                                .is_some_and(|result| result.status.usable())
                        })
                })
                .cloned();
            let Some(target) = target else { break };
            pending.remove(&target);
            let action = &plan.actions[&target];
            let start = (|| -> Result<native::Invocation> {
                let stage = native::Stage::prepare(
                    &root,
                    &run,
                    &target,
                    &plan.runtime_inputs(&target)?,
                    &receipt.targets,
                    false,
                )?;
                let ask = native::RunAsk::new(
                    &root,
                    &stage,
                    action,
                    &progress_path,
                    false,
                    config.check_current,
                );
                native::Invocation::start(
                    &root, &run, &runner, &engine, &lease, &target, stage, ask,
                )
            })();
            match start {
                Ok(invocation) => active.push(invocation),
                Err(error) => {
                    receipt.targets.insert(
                        target,
                        unavailable(action, TargetStatus::Failed, format!("{error:#}")),
                    );
                    code = code.max(1);
                    write_receipt(&receipt_path, &receipt)?;
                }
            }
        }
        let mut index = 0;
        while index < active.len() {
            if let Some(done) = active[index].poll()? {
                active.swap_remove(index);
                driver.checkpoints(&mut progress, &mut checkpoint_errors);
                let result = done.receipt(
                    plan.actions[&done.target]
                        .outputs()
                        .map(str::to_owned)
                        .collect(),
                );
                if result.status.usable() {
                    if !config.check_current {
                        driver.carry(&result.outputs, None)?;
                    }
                } else {
                    code = if code == 0 {
                        done.exit_code.max(1)
                    } else {
                        code
                    };
                    if let Some(error) = result.extra.get("error").and_then(Value::as_str) {
                        eprintln!("[print-build] {}: {error}", done.target);
                    }
                }
                println!(
                    "[print-build] {} {}",
                    done.target,
                    serde_json::to_value(result.status)?
                        .as_str()
                        .unwrap_or("finished")
                );
                std::io::stdout().flush()?;
                receipt.targets.insert(done.target.clone(), result);
                write_receipt(&receipt_path, &receipt)?;
            } else {
                index += 1;
            }
        }
        if active.is_empty() && !pending.is_empty() {
            let ready = pending.iter().any(|target| {
                plan.actions[target].dependencies.iter().all(|dependency| {
                    receipt
                        .targets
                        .get(dependency)
                        .is_some_and(|result| result.status.usable())
                })
            });
            let blocked = pending.iter().any(|target| {
                plan.actions[target].dependencies.iter().any(|dependency| {
                    receipt
                        .targets
                        .get(dependency)
                        .is_some_and(|result| !result.status.usable())
                })
            });
            if !ready && !blocked {
                for target in std::mem::take(&mut pending) {
                    receipt.targets.insert(
                        target.clone(),
                        unavailable(
                            &plan.actions[&target],
                            TargetStatus::Blocked,
                            "no available prerequisite result".into(),
                        ),
                    );
                }
                code = code.max(1);
                write_receipt(&receipt_path, &receipt)?;
            }
        }
        if !active.is_empty() {
            thread::sleep(POLL);
        }
    }
    driver.checkpoints(&mut progress, &mut checkpoint_errors);
    driver.publishing.drain()?;
    receipt.extra.insert("completed".into(), json!(true));
    write_receipt(&receipt_path, &receipt)?;
    let mut counts: BTreeMap<String, usize> = BTreeMap::new();
    for target in receipt.targets.values() {
        *counts
            .entry(
                serde_json::to_value(target.status)?
                    .as_str()
                    .unwrap()
                    .to_owned(),
            )
            .or_default() += 1;
    }
    let success = code == 0
        && driver
            .publishing
            .record
            .exit_codes
            .iter()
            .all(|code| *code == 0);
    let mut result = serde_json::to_value(&receipt)?;
    for (name, value) in [
        (
            "purpose",
            json!(
                "This record identifies each native producer and its completed exports during the print build."
            ),
        ),
        ("success", json!(success)),
        ("wall_seconds", json!(started.elapsed().as_secs_f64())),
        ("counts", json!(counts)),
        ("preview", json!(preview)),
        ("checkpoint_errors", json!(checkpoint_errors)),
        ("carried", json!(driver.carried)),
        ("suppressed_checkpoints", json!(driver.suppressed)),
        ("publication_queue", json!(driver.publishing.record)),
    ] {
        result[name] = value;
    }
    write_receipt(&run.join("result.json"), &result)?;
    let _ = fs::remove_dir(run.join("work"));
    Ok(if code != 0 { code } else { i32::from(!success) })
}
#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::{os::unix::fs::PermissionsExt, sync::Arc};

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            let root = Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap()
                .join(".cache/runs")
                .join(format!(
                    "native-print-build-test-{}-{}",
                    std::process::id(),
                    TEMPORARY.fetch_add(1, Ordering::Relaxed)
                ));
            fs::create_dir_all(&root).unwrap();
            Self(root)
        }
        fn path(&self, path: &str) -> PathBuf {
            self.0.join(path)
        }
        fn write(&self, path: &str, bytes: impl AsRef<[u8]>) -> PathBuf {
            let path = self.path(path);
            fs::create_dir_all(path.parent().unwrap()).unwrap();
            fs::write(&path, bytes).unwrap();
            path
        }
        fn json(&self, path: &str, value: Value) -> PathBuf {
            self.write(path, serde_json::to_vec(&value).unwrap())
        }
        fn script(&self, path: &str, code: &str) -> PathBuf {
            let path = self.write(path, format!("#!/bin/sh\nset -eu\n{code}\n"));
            fs::set_permissions(&path, fs::Permissions::from_mode(0o755)).unwrap();
            path
        }
        fn lease(&self) -> Lease {
            hsm_run_slots::acquire(
                "print-build-test",
                hsm_run_slots::inherited().unwrap(),
                false,
            )
            .unwrap()
        }
    }
    impl Drop for Fixture {
        fn drop(&mut self) {
            let _ = fs::remove_dir_all(&self.0);
        }
    }

    fn scene(path: &Path, head: &Value) {
        fs::create_dir_all(path.parent().unwrap()).unwrap();
        let mut bytes = serde_json::to_vec(head).unwrap();
        bytes.resize(bytes.len().div_ceil(4) * 4, b' ');
        let mut file = File::create(path).unwrap();
        file.write_all(&(bytes.len() as u32).to_le_bytes()).unwrap();
        file.write_all(&bytes).unwrap();
    }
    fn head(complete: bool) -> Value {
        json!({"v":4,"src":"scene revision","step_export":false,
            "meshes":[{"name":"relay","asset":"geometry","transform":[[1,0,0,0],[0,1,0,0],[0,0,1,0]],
                "entries":[{"name":"relay","color":[0.1,0.2,0.3]}],"features":{"mount":"upper-relay"},"source":"hardware/reference/relay.step.mesh"}],
            "sources":{"hardware/reference/relay.step.mesh":"source revision"},"iteration":{"stage":"mechanics","complete":complete}})
    }
    fn shell(value: &str) -> String {
        format!("'{}'", value.replace('\'', "'\"'\"'"))
    }
    fn wait_for(path: &Path) {
        let deadline = Instant::now() + Duration::from_secs(5);
        while !path.exists() && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(10));
        }
        assert!(path.exists(), "{} was not created", path.display());
    }

    #[test]
    fn checkpoint_tail_ignores_history_and_waits_for_complete_rows() {
        let f = Fixture::new();
        let path = f.write("progress.jsonl", "{\"files\":[]}\n");
        let mut tail = Tail::progress(path.clone()).unwrap();
        assert!(tail.poll(false).unwrap().is_empty());
        let mut writer = OpenOptions::new().append(true).open(&path).unwrap();
        writer
            .write_all(b"{\"stage\":\"mechanics\",\"files\":[")
            .unwrap();
        assert!(tail.poll(false).unwrap().is_empty());
        writer
            .write_all(b"\"/work/hardware/model.step.mesh\"]}\ninvalid\n[]\n{\"files\":[]}\n")
            .unwrap();
        let rows = tail.poll(false).unwrap();
        assert_eq!(rows.len(), 4);
        assert_eq!(
            serde_json::from_slice::<Checkpoint>(&rows[0])
                .unwrap()
                .stage
                .as_deref(),
            Some("mechanics")
        );
        assert!(serde_json::from_slice::<Checkpoint>(&rows[1]).is_err());
        assert!(serde_json::from_slice::<Checkpoint>(&rows[2]).is_err());
        assert!(serde_json::from_slice::<Checkpoint>(&rows[3]).is_ok());
        assert!(tail.poll(false).unwrap().is_empty());
    }

    #[test]
    fn status_suppression_preserves_every_geometry_binding_and_final_completion() {
        let f = Fixture::new();
        let target = f.path("held.mesh");
        let incoming = f.path("incoming.mesh");
        scene(&target, &head(true));
        scene(&incoming, &head(false));
        assert!(unchanged_checkpoint(&incoming, &target));
        let variants = [
            ("/meshes/0/asset", json!("other geometry")),
            ("/meshes/0/transform/0/3", json!(1)),
            ("/meshes/0/entries/0/color", json!([0.3, 0.2, 0.1])),
            ("/meshes/0/features/mount", json!("other mount")),
            (
                "/meshes/0/source",
                json!("hardware/reference/other.step.mesh"),
            ),
            (
                "/sources/hardware~1reference~1relay.step.mesh",
                json!("other source revision"),
            ),
        ];
        for (pointer, value) in variants {
            let mut changed = head(false);
            *changed.pointer_mut(pointer).unwrap() = value;
            scene(&incoming, &changed);
            assert!(!unchanged_checkpoint(&incoming, &target), "{pointer}");
        }
        scene(&incoming, &head(true));
        assert!(!unchanged_checkpoint(&incoming, &target));
        let mut ordinary = head(false);
        ordinary["v"] = json!(3);
        scene(&incoming, &ordinary);
        assert!(!unchanged_checkpoint(&incoming, &target));
        scene(&incoming, &head(false));
        OpenOptions::new()
            .append(true)
            .open(&incoming)
            .unwrap()
            .write_all(b"geometry")
            .unwrap();
        assert!(!unchanged_checkpoint(&incoming, &target));
    }

    #[test]
    fn publication_debt_tracks_completed_local_bytes_without_repeated_requests() {
        let f = Fixture::new();
        let name = "hardware/model.step.mesh";
        let path = f.write(name, "served");
        f.json(
            "hardware/cad-artifacts.json",
            json!({"solids":{name:file_digest(&path).unwrap()}}),
        );
        let mut publication = Publications::new(&f.0);
        assert!(!publication.needs(name, &path, false).unwrap());
        f.write(name, "completed");
        assert!(publication.needs(name, &path, false).unwrap());
        assert!(!publication.needs(name, &path, false).unwrap());
        assert!(publication.needs(name, &path, true).unwrap());
        assert!(
            !publication
                .needs("hardware/unpublished.npz", &path, true)
                .unwrap()
        );
    }

    #[test]
    fn placement_prepass_requires_changed_recorded_inputs_and_relevant_targets() {
        let f = Fixture::new();
        let source = f.write("hardware/layout.json", "original");
        let selected = vec!["//:installed-machine".to_owned()];
        assert!(!placement_changed(&selected, &f.0));
        let receipt = format!(
            ".cache/realized/installed-machine/receipts/{:x}.json",
            Sha256::digest(b"presentation-state")
        );
        f.json(
            &receipt,
            json!({"value":{"inputs":{"hardware/layout.json":file_digest(&source).unwrap()}}}),
        );
        assert!(!placement_changed(&selected, &f.0));
        f.write("hardware/layout.json", "moved");
        assert!(placement_changed(&selected, &f.0));
        assert!(!placement_changed(&["//:tpu-o-ring".into()], &f.0));
        f.write(&receipt, "incomplete");
        assert!(!placement_changed(&selected, &f.0));
    }

    #[test]
    fn concurrent_carries_remain_complete_and_remove_temporary_files() {
        let f = Arc::new(Fixture::new());
        let a = f.write("first", vec![b'a'; 65536]);
        let b = f.write("second", vec![b'b'; 65536]);
        let target = f.path("out/model.mesh");
        thread::scope(|scope| {
            for i in 0..16 {
                let target = &target;
                let source = if i % 2 == 0 { &a } else { &b };
                scope.spawn(move || carry_file(source, target).unwrap());
            }
        });
        let result = fs::read(&target).unwrap();
        assert!(result == fs::read(a).unwrap() || result == fs::read(b).unwrap());
        assert_eq!(fs::read_dir(target.parent().unwrap()).unwrap().count(), 1);
        assert_eq!(
            target.metadata().unwrap().permissions().mode() & 0o200,
            0o200
        );
    }

    #[test]
    fn publication_queue_starts_first_output_and_coalesces_to_latest_after_failure() {
        let f = Fixture::new();
        let lease = f.lease();
        f.write("held", "first\n");
        let publisher = f.script("publisher", "cat held >> published\ntouch publication-started\nwhile [ ! -f release ]; do sleep 0.01; done\nif [ ! -f first-finished ]; then touch first-finished; exit 7; fi\nexit 0");
        let run = f.path("run");
        fs::create_dir(&run).unwrap();
        let mut queue = PublicationQueue::new(&f.0, &run, &publisher, &lease, true);
        queue.request().unwrap();
        wait_for(&f.path("publication-started"));
        f.write("held", "intermediate\n");
        queue.request().unwrap();
        f.write("held", "latest\n");
        queue.request().unwrap();
        assert_eq!(queue.record.started, 1);
        f.write("release", "");
        queue.drain().unwrap();
        assert_eq!(queue.record.requests, 3);
        assert_eq!(queue.record.started, 2);
        assert_eq!(queue.record.coalesced, 2);
        assert_eq!(queue.record.exit_codes, [7, 0]);
        assert_eq!(
            fs::read_to_string(f.path("published")).unwrap(),
            "first\nlatest\n"
        );
    }

    #[test]
    fn raw_glb_replacement_stays_inside_named_v4_views() {
        let f = Fixture::new();
        let payload = f.path("scene.mesh");
        let pcb = "hardware/pcb/pcba/out/pcba.glb.mesh";
        f.write("scene.mesh", "stale unrelated mesh");
        assert!(!raw_export_replaced(pcb, &payload).unwrap());
        let named = "hardware/assembly/scenes/glb/install.glb.mesh";
        let mut current = head(true);
        current["step_export"] = json!(true);
        scene(&payload, &current);
        assert!(raw_export_replaced(named, &payload).unwrap());
        assert!(!raw_export_replaced(pcb, &payload).unwrap());
        current["v"] = json!(3);
        current["step_export"] = json!(false);
        scene(&payload, &current);
        assert!(!raw_export_replaced(named, &payload).unwrap());
    }

    fn native_plan(f: &Fixture, declarations: &[(&str, Vec<&str>, Vec<&str>)]) -> Plan {
        let rows: Vec<planning::InventoryRow> = declarations.iter().map(|(name, outputs, reads)| {
            let source = format!("hardware/{}.rs", name.replace('-', "_")); f.write(&source, "// fixture producer\n");
            serde_json::from_value(json!([[source],{"solids":outputs,"reads":reads,"program":{"crate":"fixture","name":name,"sources":[source]}}])).unwrap()
        }).collect();
        let files: BTreeSet<String> = declarations
            .iter()
            .flat_map(|(_, _, reads)| reads.iter().map(|name| (*name).to_owned()))
            .collect();
        planning::actions_from_inventory(&f.0, rows, files, None).unwrap()
    }

    fn native_config(f: &Fixture, cases: Value) -> Config {
        f.json("cases.json", cases);
        let engine = f.write("engine.cjs", concat!("#!/usr/bin/env node\n", r#"
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ask = JSON.parse(process.argv.at(-1)), workspace = ask.workspace;
let behavior = JSON.parse(fs.readFileSync(path.join(workspace,'cases.json')))[ask.name] || {};
const preview = ask.args.includes('--placements-only');
if (preview && behavior.preview) behavior = {...behavior,...behavior.preview};
fs.appendFileSync(path.join(workspace,'calls.jsonl'),JSON.stringify(ask)+'\n');
(async()=>{
  for (const [name,expected] of Object.entries(behavior.expect_inputs || {})) {
    const filename = path.join(ask.root,name);
    if (expected === null ? fs.existsSync(filename) : fs.readFileSync(filename,'utf8') !== expected) throw Error('unexpected staged input '+name);
  }
  const artifacts = {}, file_hashes = {};
  for (const [name,value] of Object.entries(behavior.outputs || {})) {
    const bytes = typeof value === 'string' ? Buffer.from(value) : fs.readFileSync(value.file);
    const hash = crypto.createHash('sha256').update(bytes).digest('hex');
    const blob = path.join(workspace,'engine-blobs',hash);fs.mkdirSync(path.dirname(blob),{recursive:true});fs.writeFileSync(blob,bytes);
    const staged = path.join(ask.root,name);fs.mkdirSync(path.dirname(staged),{recursive:true});fs.writeFileSync(staged,bytes);
    artifacts[name]=blob;file_hashes[name]=hash;
  }
  if (behavior.checkpoint) fs.appendFileSync(ask.environment.HSM_BUILD_PROGRESS,JSON.stringify({stage:behavior.stage || 'mechanics',files:[path.join(ask.root,behavior.checkpoint)]})+'\n');
  if (behavior.wait_for) {
    const until=Date.now()+5000;
    while (!fs.existsSync(path.join(workspace,behavior.wait_for))) { if(Date.now()>until)throw Error('timed out waiting for '+behavior.wait_for);await new Promise(resolve=>setTimeout(resolve,10)); }
  }
  if(behavior.finished)fs.writeFileSync(path.join(workspace,behavior.finished),'');
  if(behavior.fail){console.log(JSON.stringify({ok:false,error:'requested producer failure'}));process.exitCode=behavior.fail;return;}
  console.log(JSON.stringify({ok:true,result:{available:behavior.available !== false,hit:!!behavior.hit,compiled:!!behavior.compiled,artifacts,file_hashes,missing_outputs:ask.outputs.filter(name=>!artifacts[name]),program_seconds:0.001}}));
})().catch(error=>{console.log(JSON.stringify({ok:false,error:String(error)}));process.exitCode=1;});
"#));
        fs::set_permissions(&engine, fs::Permissions::from_mode(0o755)).unwrap();
        Config { root: f.0.clone(), run_dir: Some(f.path("run")), runner: Some(f.script("runner", "test \"$1\" = --\nshift\nexec \"$@\"")), engine: Some(engine),
            publisher: Some(f.script("publisher", "touch publication-started\nif [ ! -f producer-finished ]; then touch first-view-before-producer-exit; fi\nexit 0")), progress: None, selectors: Vec::new(), publish: true, check_current: false }
    }

    #[test]
    fn stages_use_fresh_declared_artifacts_and_keep_absence_distinct_from_held_outputs() {
        let f = Fixture::new();
        f.write("hardware/input.json", "authored");
        f.write("hardware/export.stl", "stale retained export");
        let blob = f.write("blob", "fresh export");
        let outputs = BTreeMap::from([("hardware/export.stl".into(), blob)]);
        let mut completed = BTreeMap::from([(
            "producer".into(),
            TargetReceipt {
                status: TargetStatus::Built,
                outputs,
                ..TargetReceipt::default()
            },
        )]);
        let inputs = BTreeMap::from([
            (
                "hardware/input.json".into(),
                planning::RuntimeInput::default(),
            ),
            (
                "hardware/export.stl".into(),
                planning::RuntimeInput {
                    producer: Some("producer".into()),
                    ..planning::RuntimeInput::default()
                },
            ),
        ]);
        let stage =
            native::Stage::prepare(&f.0, &f.path("run"), "consumer", &inputs, &completed, false)
                .unwrap();
        assert_eq!(
            fs::read_to_string(stage.root.join("hardware/export.stl")).unwrap(),
            "fresh export"
        );
        assert_eq!(
            fs::read_to_string(stage.root.join("hardware/input.json")).unwrap(),
            "authored"
        );
        assert!(!stage.root.join("hardware/unrelated.rs").exists());
        completed.get_mut("producer").unwrap().outputs.clear();
        let missing =
            native::Stage::prepare(&f.0, &f.path("run"), "consumer", &inputs, &completed, false)
                .unwrap();
        assert!(!missing.root.join("hardware/export.stl").exists());
        assert!(missing.inputs.contains(&"hardware/export.stl".to_owned()));
    }

    #[test]
    fn native_progress_publishes_before_reply_and_failures_preserve_independent_results() {
        let f = Fixture::new();
        let plan = native_plan(
            &f,
            &[
                ("first", vec!["hardware/first.stl"], vec![]),
                (
                    "dependent",
                    vec!["hardware/dependent.stl"],
                    vec!["hardware/first.stl"],
                ),
                ("failure", vec!["hardware/failure.stl"], vec![]),
                (
                    "blocked",
                    vec!["hardware/blocked.stl"],
                    vec!["hardware/failure.stl"],
                ),
            ],
        );
        let config = native_config(
            &f,
            json!({
                "first":{"outputs":{"hardware/first.stl":"first bytes"},"checkpoint":"hardware/first.stl","wait_for":"publication-started","finished":"producer-finished"},
                "dependent":{"outputs":{"hardware/dependent.stl":"dependent bytes"},"expect_inputs":{"hardware/first.stl":"first bytes"},"hit":true},
                "failure":{"fail":6},"blocked":{"fail":8}
            }),
        );
        assert_eq!(run_plan(config, plan).unwrap(), 6);
        assert!(f.path("first-view-before-producer-exit").exists());
        assert_eq!(
            fs::read_to_string(f.path("hardware/dependent.stl")).unwrap(),
            "dependent bytes"
        );
        let receipt: RunReceipt =
            serde_json::from_slice(&fs::read(f.path("run/receipt.json")).unwrap()).unwrap();
        assert_eq!(receipt.targets["blocked"].status, TargetStatus::Blocked);
        assert_eq!(receipt.targets["dependent"].status, TargetStatus::Cached);
        assert_eq!(receipt.targets["failure"].status, TargetStatus::Failed);
        assert!(
            receipt.targets["first"]
                .outputs
                .values()
                .all(|file| file.is_file())
        );
        assert!(!f.path("run/work").exists());
        let calls = fs::read_to_string(f.path("calls.jsonl")).unwrap();
        assert!(!calls.contains("\"name\":\"blocked\""));
        let result: Value =
            serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert_eq!(result["completed"], true);
        assert_eq!(result["success"], false);
        assert_eq!(result["full_build"], true);
        assert_eq!(result["counts"]["failed"], 1);
    }

    #[test]
    fn explicit_cache_inspection_never_carries_checkout_files_or_starts_publication() {
        let f = Fixture::new();
        f.write("hardware/cached.stl", "held checkout");
        let plan = native_plan(
            &f,
            &[
                ("cached", vec!["hardware/cached.stl"], vec![]),
                ("missing", vec!["hardware/missing.stl"], vec![]),
                (
                    "blocked",
                    vec!["hardware/blocked.stl"],
                    vec!["hardware/missing.stl"],
                ),
            ],
        );
        let mut config = native_config(
            &f,
            json!({"cached":{"outputs":{"hardware/cached.stl":"current cached bytes"},"hit":true},"missing":{"available":false}}),
        );
        config.check_current = true;
        assert_eq!(run_plan(config, plan).unwrap(), 1);
        assert_eq!(
            fs::read_to_string(f.path("hardware/cached.stl")).unwrap(),
            "held checkout"
        );
        assert!(!f.path("publication-started").exists());
        let receipt: RunReceipt =
            serde_json::from_slice(&fs::read(f.path("run/receipt.json")).unwrap()).unwrap();
        assert_eq!(receipt.targets["cached"].status, TargetStatus::Cached);
        assert_eq!(receipt.targets["missing"].status, TargetStatus::NotCurrent);
        assert_eq!(receipt.targets["blocked"].status, TargetStatus::Blocked);
        assert_eq!(
            receipt.targets["missing"].declared_outputs,
            ["hardware/missing.stl"]
        );
    }

    #[test]
    fn placement_preview_publishes_before_normal_work_and_normal_completion_keeps_its_identity() {
        let f = Fixture::new();
        let name = "hardware/manifold-layout/enclosure-assembly.step.mesh";
        f.write("hardware/layout.json", "new placement");
        let receipt = format!(
            ".cache/realized/installed-machine/receipts/{:x}.json",
            Sha256::digest(b"presentation-state")
        );
        f.json(
            &receipt,
            json!({"value":{"inputs":{"hardware/layout.json":"old placement digest"}}}),
        );
        let partial = f.path("partial.mesh");
        scene(&partial, &head(false));
        let finished = f.path("finished.mesh");
        scene(&finished, &head(true));
        let plan = native_plan(
            &f,
            &[(
                "installed-machine",
                vec![name],
                vec!["hardware/layout.json"],
            )],
        );
        let config = native_config(
            &f,
            json!({"installed-machine":{"outputs":{name:{"file":finished}},"wait_for":"publication-started","finished":"producer-finished","preview":{"outputs":{name:{"file":partial}},"checkpoint":name,"stage":"placements","finished":"preview-finished"}}}),
        );
        assert_eq!(run_plan(config, plan).unwrap(), 0);
        assert!(f.path("first-view-before-producer-exit").exists());
        assert_eq!(fs::read(f.path(name)).unwrap(), fs::read(finished).unwrap());
        let result: Value =
            serde_json::from_slice(&fs::read(f.path("run/result.json")).unwrap()).unwrap();
        assert_eq!(result["preview"][0]["available"], true);
        assert_eq!(result["carried"][0]["stage"], "placements");
        let calls = fs::read_to_string(f.path("calls.jsonl"))
            .unwrap()
            .lines()
            .map(|row| serde_json::from_str::<Value>(row).unwrap())
            .collect::<Vec<_>>();
        assert_eq!(calls[0]["allow_compile"], false);
        assert_eq!(calls[0]["args"], json!(["--placements-only"]));
        assert_eq!(calls[1]["args"], json!([]));
    }
}
