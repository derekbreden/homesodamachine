//! Part runs: the program run that cuts a part's files, kept by everything that decides them.
//!
//! A run is a program of the `tools/hsm` workspace (a `[[bin]]` of a subsystem crate), its
//! arguments, and the files it reads. Its key is the program's code — the toolchain, and every
//! workspace source rustc compiled into it with the manifests and lockfile that chose them — and
//! its arguments: a file by its bytes, the output directory by its place. The kernel names each
//! file a program reads in `HSM_READS` (`hsm_kernel::reads`), and a kept run answers again only
//! while each of those holds the bytes it read. Files are kept once by content, under `blobs/`,
//! and cloned into place; a file already holding them is left as it is, as `part::keep` leaves it.
//!
//! The code needs no cargo to read. The sources a program was last compiled from are named by its
//! dep-info, their digests are kept by stat, and a built program is kept by its code under
//! `programs/`, so a checkout whose sources match runs it without compiling. cargo runs for a code
//! nothing has built, in the requesting checkout's own target directory, one at a time there.
//!
//! Runs and builds are admitted in turn within a memory budget, each at the peak its program last
//! reached, and none starts while the system reports critical memory pressure.
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_run_slots::{Lease, ipc};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet, HashMap, VecDeque},
    fs,
    io::Read,
    os::unix::fs::MetadataExt,
    path::{Component, Path, PathBuf},
    process::{Command, Stdio},
    sync::{
        Arc, Condvar, Mutex,
        atomic::{AtomicU64, AtomicUsize, Ordering},
    },
    thread,
    time::{Duration, Instant, SystemTime},
};

/// A program not yet measured is admitted at this peak; cargo at the second.
const PROGRAM_PEAK: u64 = 512 << 20;
const CARGO_PEAK: u64 = 700 << 20;
/// The variants kept for one key, which differ only in what their runs read.
const VARIANTS: usize = 4;
/// `kern.memorystatus_vm_pressure_level` at which nothing new starts.
const CRITICAL: i32 = 4;
/// How long a retired run stays before a prune deletes it.
const RETIRE: Duration = Duration::from_secs(10 * 60);

/// What a run is asked for over the socket: `{"op":"run", ...}`.
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Ask {
    /// The checkout whose `tools/hsm` workspace holds the program.
    pub workspace: PathBuf,
    /// Where the program runs, and where the paths its numbers name are read from.
    pub root: PathBuf,
    #[serde(rename = "crate")]
    pub krate: String,
    pub name: String,
    #[serde(default)]
    pub args: Vec<String>,
    /// Complete raw-file reads relative to `root`; an absent file is an input state.
    #[serde(default)]
    pub inputs: Option<Vec<String>>,
    /// Files written relative to `root`; their presence activates declared-output execution.
    #[serde(default)]
    pub outputs: Option<Vec<String>>,
    /// The planner's complete compiler inputs, relative to `workspace`, including its canonical
    /// Cargo configuration. Their supplied split replaces dep-info/whole-workspace manifests.
    #[serde(default)]
    pub compiler_inputs: Option<Vec<String>>,
    /// Explicit producer settings and subprocess environment.
    #[serde(default)]
    pub environment: BTreeMap<String, String>,
    #[serde(default = "yes")]
    pub allow_compile: bool,
    /// Restore a matching result or report unavailable without compiling or executing.
    #[serde(default)]
    pub cache_only: bool,
}

fn yes() -> bool { true }

/// A kept run.
#[derive(Clone, Deserialize, Serialize)]
struct Kept {
    /// Each file the run read: from the root, from the workspace, or `/` for a whole path.
    reads: Vec<(String, String, String)>,
    files: Vec<(String, String)>,
    #[serde(default)]
    absent: Vec<String>,
    stdout: String,
    stderr: String,
    seconds: f64,
    peak: u64,
    code: String,
    /// The run's key by its program's portable code.
    portable: String,
    sources: Vec<String>,
}

/// A program's two identities. `native` is the toolchain with the sources: a built program and a
/// run on this machine are kept by it. `portable` is the sources alone, by which a result could be
/// shared beyond this toolchain once native and wasm builds are shown to cut the same bytes.
#[derive(Clone)]
struct Code {
    native: String,
    portable: String,
}

enum Arg {
    Out(PathBuf),
    File(PathBuf, String),
    Text(String),
}

type Stamp = [u64; 7];

fn stamp(path: &Path) -> Option<Stamp> {
    let m = fs::metadata(path).ok()?;
    Some([
        m.dev(),
        m.ino(),
        m.len(),
        m.mtime() as u64,
        m.mtime_nsec() as u64,
        m.ctime() as u64,
        m.ctime_nsec() as u64,
    ])
}

struct Gate {
    held: u64,
    running: usize,
    queue: VecDeque<u64>,
    next: u64,
}

/// A place in the budget, given back when dropped.
struct Ticket<'a> {
    builder: &'a Builder,
    bytes: u64,
}

impl Drop for Ticket<'_> {
    fn drop(&mut self) {
        let mut gate = self.builder.gate.lock().unwrap();
        gate.held -= self.bytes;
        gate.running -= 1;
        self.builder.turn.notify_all();
    }
}

struct Toolchain {
    stamps: Vec<Option<Stamp>>,
    sysroot: PathBuf,
    version: String,
}

/// One run of a key at a time; a second ask for it waits and takes what the first kept.
#[derive(Default)]
struct Flight {
    done: Mutex<bool>,
    landed: Condvar,
}

pub struct Builder {
    dir: PathBuf,
    budget: u64,
    gate: Mutex<Gate>,
    turn: Condvar,
    hashes: Mutex<HashMap<PathBuf, (Stamp, String)>>,
    toolchains: Mutex<HashMap<PathBuf, Toolchain>>,
    peaks: Mutex<HashMap<String, u64>>,
    cargo: Mutex<HashMap<PathBuf, Arc<Mutex<()>>>>,
    flights: Mutex<HashMap<String, Arc<Flight>>>,
    active: AtomicUsize,
    serial: AtomicU64,
    last: Mutex<Instant>,
}

/// A program to run, the code and sources it is, whether cargo ran for it, and whether a run of it
/// may be kept.
struct Built {
    path: PathBuf,
    code: Code,
    sources: Vec<String>,
    compiled: bool,
    keepable: bool,
}

#[derive(Deserialize, Serialize)]
struct DeclaredCompiler {
    declared: Vec<String>,
    sources: Vec<String>,
}

/// A finished child: its status, its output, its seconds and the most memory it held.
struct Finished {
    ok: bool,
    code: i32,
    stdout: Vec<u8>,
    stderr: Vec<u8>,
    seconds: f64,
    peak: u64,
}

impl Builder {
    pub fn new(store: &Path, budget_mb: u64) -> Result<Self> {
        let dir = store.join("parts");
        for sub in ["blobs", "runs", "programs", "tmp"] {
            fs::create_dir_all(dir.join(sub))?;
        }
        let dir = dir.canonicalize()?;
        // A run that died with its daemon leaves its scratch behind. A daemon this one replaces
        // may still be finishing one, in a directory named for its pid.
        for entry in fs::read_dir(dir.join("tmp"))?.flatten() {
            let pid = entry.file_name().to_str().and_then(|n| n.split('-').next()?.parse().ok());
            if !pid.is_some_and(alive) {
                let _ = fs::remove_dir_all(entry.path());
            }
        }
        let peaks = fs::read(dir.join("peaks.json"))
            .ok()
            .and_then(|b| serde_json::from_slice(&b).ok())
            .unwrap_or_default();
        Ok(Self {
            dir,
            budget: budget_mb.checked_mul(1 << 20).context("build budget overflow")?,
            gate: Mutex::new(Gate {
                held: 0,
                running: 0,
                queue: VecDeque::new(),
                next: 0,
            }),
            turn: Condvar::new(),
            hashes: Mutex::new(HashMap::new()),
            toolchains: Mutex::new(HashMap::new()),
            peaks: Mutex::new(peaks),
            cargo: Mutex::new(HashMap::new()),
            flights: Mutex::new(HashMap::new()),
            active: AtomicUsize::new(0),
            serial: AtomicU64::new(0),
            last: Mutex::new(Instant::now()),
        })
    }

    /// Asks running or waiting, and how long since the last one ended.
    pub fn busy(&self) -> (usize, Duration) {
        (
            self.active.load(Ordering::SeqCst),
            self.last.lock().unwrap().elapsed(),
        )
    }

    pub fn status(&self) -> Value {
        let gate = self.gate.lock().unwrap();
        json!({"budget_bytes": self.budget, "held_bytes": gate.held, "running": gate.running,
            "waiting": gate.queue.len(), "asks": self.active.load(Ordering::SeqCst),
            "pressure": pressure()})
    }

    /// Wait until no ask is running or waiting.
    pub fn wait_idle(&self) {
        while self.active.load(Ordering::SeqCst) > 0 {
            thread::sleep(Duration::from_millis(50));
        }
    }

    /// An ask taken in, counted from now until it is answered, so the daemon does not go idle
    /// between taking it and starting it.
    pub fn enter(self: &Arc<Self>) -> Entered {
        self.active.fetch_add(1, Ordering::SeqCst);
        Entered(self.clone())
    }

    fn run(&self, mut ask: Ask, mut lease: Option<Lease>) -> Result<Value> {
        let started = Instant::now();
        ask.workspace = ask.workspace.canonicalize()
            .with_context(|| format!("no workspace at {}", ask.workspace.display()))?;
        ask.root = ask.root.canonicalize()
            .with_context(|| format!("no root at {}", ask.root.display()))?;
        ensure!(plain(&ask.krate) && plain(&ask.name), "a crate and a program are plain names");
        normalize_files(&mut ask.inputs)?;
        normalize_files(&mut ask.outputs)?;
        normalize_files(&mut ask.compiler_inputs)?;
        ensure!(!ask.compiler_inputs.as_ref().is_some_and(Vec::is_empty),
                "declared compiler inputs contain the program's sources and canonical configuration");
        let args = self.classify(&ask)?;
        let out = if ask.outputs.is_some() { Some(ask.root.clone()) } else {
            args.iter().find_map(|a| match a { Arg::Out(p) => Some(p.clone()), _ => None })
        };
        let declared = self.declared_reads(&ask)?;
        let environment = run_environment(&ask)?;
        let toolchain = self.toolchain(&ask.workspace)?;
        let known = match self.ask_sources(&ask) {
            Some(sources) => self.code(&ask.workspace, &ask.krate, &ask.name, &sources, &toolchain)?
                .map(|code| (code, sources)),
            None => None,
        };
        let mut hit = match &known {
            Some((code, _)) => self.lookup(&run_key(&code.native, &args, &ask, &declared, &environment), &ask, &declared)?,
            None => None,
        };
        let available_program = known.as_ref().and_then(|(code, sources)| self.kept_program(&ask, code, sources));
        if hit.is_none() && (ask.cache_only || (!ask.allow_compile && available_program.is_none())) {
            return Ok(json!({"available":false,"hit":false,"compiled":false,"kept":false,
                "files":[],"file_hashes":{},"artifacts":{},"missing_outputs":[],
                "reason":if ask.cache_only { "no matching kept result" } else { "no current-code program is kept" },
                "seconds":started.elapsed().as_secs_f64()}));
        }
        // Hits and explicit freshness probes do no heavy work and acquire no host lease.
        if hit.is_none() {
            lease = Some(hsm_run_slots::acquire(&format!("{}:{}", ask.krate, ask.name), lease, false)?);
        }
        let (code, sources, program, compiled, keepable) = match (&hit, known) {
            (Some(_), Some((code, sources))) => (code, sources, None, false, true),
            (_, Some((code, sources))) if !ask.allow_compile =>
                (code, sources, available_program, false, true),
            (_, known) => {
                let built = self.program(&ask, &toolchain, known, lease.as_ref().unwrap())?;
                (built.code, built.sources, Some(built.path), built.compiled, built.keepable)
            }
        };
        let key = run_key(&code.native, &args, &ask, &declared, &environment);
        if hit.is_none() && compiled { hit = self.lookup(&key, &ask, &declared)?; }
        let mut flight = None;
        if hit.is_none() {
            let (f, leader) = {
                let mut flights = self.flights.lock().unwrap();
                match flights.get(&key) {
                    Some(f) => (f.clone(), false),
                    None => {
                        let f = Arc::new(Flight::default());
                        flights.insert(key.clone(), f.clone());
                        (f, true)
                    }
                }
            };
            if leader { flight = Some(f); } else {
                let mut done = f.done.lock().unwrap();
                while !*done { done = f.landed.wait(done).unwrap(); }
                drop(done);
                hit = self.lookup(&key, &ask, &declared)?;
            }
        }
        let landing = Landing { builder: self, key: &key, flight };
        let was_kept = hit.is_some();
        let (kept, kept_now) = match hit {
            Some(kept) => (kept, false),
            None => {
                let program = program.context("no program to run")?;
                let (kept, storable) = self.execute(&program, &ask, &args, &code, &sources,
                    &declared, &environment, lease.as_ref().unwrap())?;
                let storable = storable && keepable;
                if storable { self.keep(&key, &kept)?; }
                (kept, storable)
            }
        };
        drop(landing);
        if let Some(out) = &out { self.place(&kept.files, &kept.absent, out)?; }
        let artifacts: BTreeMap<_, _> = kept.files.iter().map(|(name, digest)|
            (name, self.dir.join("blobs").join(digest))).collect();
        let hashes: BTreeMap<_, _> = kept.files.iter().map(|(name, digest)| (name, digest)).collect();
        Ok(json!({
            "available":true,"stdout":kept.stdout,"stderr":kept.stderr,"sources":kept.sources,
            "reads":kept.reads,"files":kept.files.iter().map(|(n,_)|n).collect::<Vec<_>>(),
            "file_hashes":hashes,"artifacts":artifacts,"missing_outputs":kept.absent,
            "hit":was_kept,"kept":was_kept||kept_now,"compiled":compiled,
            "program_seconds":kept.seconds,"peak_bytes":kept.peak,
            "code":code.native,"key":key,"seconds":started.elapsed().as_secs_f64(),
        }))
    }

    /// Each argument: the one directory is where the files go, a file is read by its bytes, and
    /// anything else is passed as it is.
    fn classify(&self, ask: &Ask) -> Result<Vec<Arg>> {
        if ask.outputs.is_some() {
            return Ok(ask.args.iter().cloned().map(Arg::Text).collect());
        }
        let mut args = vec![];
        for a in &ask.args {
            let path = ask.root.join(a);
            if path.is_dir() {
                ensure!(
                    !args.iter().any(|a| matches!(a, Arg::Out(_))),
                    "a run writes into one directory"
                );
                args.push(Arg::Out(path.canonicalize()?));
            } else if let Some(digest) = self.sha(&path)? {
                args.push(Arg::File(path, digest));
            } else {
                args.push(Arg::Text(a.clone()));
            }
        }
        Ok(args)
    }

    /// The SHA-256 of the file at `path`, or None where there is none; kept while its stat stands.
    fn sha(&self, path: &Path) -> Result<Option<String>> {
        let Some(before) = stamp(path) else {
            return Ok(None);
        };
        if let Some((s, d)) = self.hashes.lock().unwrap().get(path) {
            if *s == before {
                return Ok(Some(d.clone()));
            }
        }
        let mut file = match fs::File::open(path) {
            Ok(file) => file,
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
            Err(e) => return Err(e).with_context(|| format!("reading {}", path.display())),
        };
        let mut h = Sha256::new();
        let mut buffer = [0u8; 65536];
        loop {
            let size = file.read(&mut buffer).with_context(|| format!("reading {}", path.display()))?;
            if size == 0 { break; }
            h.update(&buffer[..size]);
        }
        let digest = format!("{:x}", h.finalize());
        if stamp(path) == Some(before) {
            self.hashes
                .lock()
                .unwrap()
                .insert(path.to_path_buf(), (before, digest.clone()));
        }
        Ok(Some(digest))
    }

    /// Cargo's watched directories contribute membership and entry types, while rustc's
    /// individual source dependencies contribute their bytes through `sha`.
    fn compiler_sha(&self, path: &Path) -> Result<Option<String>> {
        if !path.is_dir() { return self.sha(path); }
        let mut h = Sha256::new();
        h.update("hsm compiler directory 1\n");
        let mut pending = vec![path.to_path_buf()];
        let mut entries = BTreeMap::new();
        while let Some(directory) = pending.pop() {
            for entry in fs::read_dir(&directory)
                .with_context(|| format!("reading compiler directory {}", directory.display()))? {
                let entry = entry?;
                let kind = entry.file_type()?;
                if kind.is_dir() { pending.push(entry.path()); }
                let target = if kind.is_symlink() { Some(fs::read_link(entry.path())?) } else { None };
                entries.insert(entry.path().strip_prefix(path)?.to_path_buf(),
                    (if kind.is_dir() { b'd' } else if kind.is_file() { b'f' }
                     else if kind.is_symlink() { b'l' } else { b'o' }, target));
            }
        }
        for (name, (kind, target)) in entries {
            h.update([kind]);
            let bytes = name.as_os_str().as_encoded_bytes();
            h.update((bytes.len() as u64).to_le_bytes());
            h.update(bytes);
            if let Some(target) = target {
                let bytes = target.as_os_str().as_encoded_bytes();
                h.update((bytes.len() as u64).to_le_bytes());
                h.update(bytes);
            }
        }
        Ok(Some(format!("directory:{:x}", h.finalize())))
    }

    /// `rustc -vV` as the cargo this engine runs would run it from the workspace, kept while
    /// rustup's settings, the workspace's toolchain files and the rustc it resolved stand.
    fn toolchain(&self, workspace: &Path) -> Result<String> {
        let home = home();
        let rustup = std::env::var_os("RUSTUP_HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|| home.join(".rustup"));
        let files = [
            rustup.join("settings.toml"),
            workspace.join("rust-toolchain.toml"),
            workspace.join("rust-toolchain"),
            workspace.join("tools/hsm/rust-toolchain.toml"),
            workspace.join("tools/hsm/rust-toolchain"),
        ];
        let stamps: Vec<_> = files.iter().map(|f| stamp(f)).collect();
        if let Some(t) = self.toolchains.lock().unwrap().get(workspace) {
            let mut now = stamps.clone();
            now.push(stamp(&t.sysroot.join("bin/rustc")));
            if now == t.stamps {
                return Ok(t.version.clone());
            }
        }
        let rustc = cargo()?.with_file_name("rustc");
        let ask = |arg: &[&str]| -> Result<String> {
            let mut command = Command::new(&rustc);
            command.args(arg)
                .current_dir(workspace.join("tools/hsm"))
                .env_clear()
                .envs(cargo_env(&home))
                .stdin(Stdio::null())
                .stderr(Stdio::inherit());
            let out = ipc::output(&mut command)?;
            ensure!(out.status.success(), "rustc {arg:?} failed");
            Ok(String::from_utf8(out.stdout)?.trim().to_owned())
        };
        let sysroot = PathBuf::from(ask(&["--print", "sysroot"])?);
        let version = ask(&["-vV"])?;
        let mut all = stamps;
        all.push(stamp(&sysroot.join("bin/rustc")));
        self.toolchains.lock().unwrap().insert(
            workspace.to_path_buf(),
            Toolchain {
                stamps: all,
                sysroot,
                version: version.clone(),
            },
        );
        Ok(version)
    }

    /// The program to run for `ask`: the one kept for its code, else what cargo builds.
    fn program(&self, ask: &Ask, toolchain: &str, known: Option<(Code, Vec<String>)>, lease: &Lease) -> Result<Built> {
        if let Some((code, sources)) = known {
            if let Some(path) = self.kept_program(ask, &code, &sources) {
                return Ok(Built { path, code, sources, compiled: false, keepable: true });
            }
        }
        // cargo, one at a time in this target directory.
        let compiler = lease.compiler()?;
        let release = ask.workspace.join("tools/hsm/target/release");
        let lock = self
            .cargo
            .lock()
            .unwrap()
            .entry(release.clone())
            .or_default()
            .clone();
        let _held = lock.lock().unwrap();
        // Another ask may have built it while this one waited.
        if let Some(sources) = self.ask_sources(ask) {
            if let Some(code) = self.code(&ask.workspace, &ask.krate, &ask.name, &sources, toolchain)? {
                if let Some(path) = self.kept_program(ask, &code, &sources) {
                    return Ok(Built { path, code, sources, compiled: false, keepable: true });
                }
            }
        }
        let previous = compiled(&release.join(format!("{}.d", ask.name)), &ask.workspace)
            .unwrap_or_default();
        let began = SystemTime::now();
        let manifest = ask.workspace.join("tools/hsm").join(&ask.krate).join("Cargo.toml");
        let mut cmd = Command::new(cargo()?);
        cmd.args(["build", "--release", "--locked", "--quiet", "--manifest-path"])
            .arg(&manifest)
            .args(["--bin", &ask.name])
            .current_dir(ask.workspace.join("tools/hsm"))
            .env_clear()
            .envs(cargo_env(&home()))
            .env("CARGO_TARGET_DIR", ask.workspace.join("tools/hsm/target"))
            .env("CARGO_BUILD_JOBS", "2")
            .env("CMAKE_BUILD_PARALLEL_LEVEL", "2");
        compiler.apply(&mut cmd)?;
        let peak = format!("cargo {}", ask.krate);
        let done = {
            let _ticket = self.admit(self.peak(&peak, CARGO_PEAK));
            finish(cmd)?
        };
        self.measured(&peak, done.peak);
        if !done.ok {
            bail!(
                "cargo build of {} failed:\n{}",
                ask.name,
                String::from_utf8_lossy(&done.stderr)
            );
        }
        let sources = if let Some(declared) = &ask.compiler_inputs {
            let fresh = compiled(&release.join(format!("{}.d", ask.name)), &ask.workspace)
                .ok_or_else(|| anyhow!("cargo wrote no dep-info for {}", ask.name))?;
            let sources = refreshed_sources(declared, &previous, fresh);
            write_atomic(&self.compiler_record(ask), &serde_json::to_vec(&DeclaredCompiler {
                declared: declared.clone(), sources: sources.clone(),
            })?)?;
            sources
        } else {
            self.sources(&ask.workspace, &ask.krate, &ask.name)
                .ok_or_else(|| anyhow!("cargo wrote no dep-info for {}", ask.name))?
        };
        let code = self
            .code(&ask.workspace, &ask.krate, &ask.name, &sources, toolchain)?
            .ok_or_else(|| anyhow!("a source of {} went away while it built", ask.name))?;
        let path = release.join(&ask.name);
        // A source written while cargo ran may or may not be what rustc read, so that program
        // runs, and neither it nor its run is kept under a code it may not be.
        if sources.iter().any(|s| compiler_changed_since(&ask.workspace.join(s), began)) {
            return Ok(Built { path, code, sources, compiled: true, keepable: false });
        }
        let home = self.dir.join("programs").join(&code.native);
        fs::create_dir_all(&home)?;
        let temp = home.join(format!(".{}.{}-{}", ask.name, std::process::id(), self.serial()));
        clone_or_copy(&path, &temp)?;
        fs::rename(&temp, home.join(&ask.name))?;
        write_atomic(&home.join("built-in"), ask.workspace.as_os_str().as_encoded_bytes())?;
        write_atomic(
            &self.dir.join("programs").join(format!("{}.{}.json", ask.krate, ask.name)),
            &serde_json::to_vec(&sources)?,
        )?;
        Ok(Built { path: home.join(&ask.name), code, sources, compiled: true, keepable: true })
    }

    /// The program kept for `code`, where it may run for this workspace. One from a kernel that
    /// does not name its reads reads the import cache of the checkout that built it, so it runs
    /// for that checkout alone.
    fn kept_program(&self, ask: &Ask, code: &Code, sources: &[String]) -> Option<PathBuf> {
        let home = self.dir.join("programs").join(&code.native);
        let path = home.join(&ask.name);
        if !path.is_file() {
            return None;
        }
        let names_reads = sources.iter().any(|s| s == "tools/hsm/kernel/src/reads.rs");
        let built_in = fs::read(home.join("built-in")).ok()?;
        (names_reads || built_in == ask.workspace.as_os_str().as_encoded_bytes()).then_some(path)
    }

    /// What a program was last compiled from: the workspace sources off its dep-info there, or
    /// what it was last kept from here, with the manifests and the lockfile.
    fn sources(&self, workspace: &Path, krate: &str, name: &str) -> Option<Vec<String>> {
        let dep_info = workspace.join("tools/hsm/target/release").join(format!("{name}.d"));
        let listed = compiled(&dep_info, workspace).or_else(|| {
            let kept = fs::read(self.dir.join("programs").join(format!("{krate}.{name}.json"))).ok()?;
            serde_json::from_slice::<Vec<String>>(&kept).ok()
        })?;
        let mut all: BTreeSet<String> = listed.into_iter().collect();
        all.extend(manifests(&all.iter().cloned().collect::<Vec<_>>(), krate, workspace));
        Some(all.into_iter().collect())
    }

    fn compiler_record(&self, ask: &Ask) -> PathBuf {
        self.dir.join("programs").join(format!("{}.{}.compiler.json", ask.krate, ask.name))
    }

    /// A declared compiler split keeps its canonical configuration and the closure discovered
    /// by the last real compilation, without adding unrelated workspace membership or lock bytes.
    fn ask_sources(&self, ask: &Ask) -> Option<Vec<String>> {
        if let Some(declared) = &ask.compiler_inputs {
            let saved = fs::read(self.compiler_record(ask)).ok()
                .and_then(|bytes| serde_json::from_slice::<DeclaredCompiler>(&bytes).ok());
            Some(saved.filter(|saved| saved.declared == *declared)
                .map(|saved| saved.sources).unwrap_or_else(|| declared.clone()))
        } else {
            self.sources(&ask.workspace, &ask.krate, &ask.name)
        }
    }

    /// A program's code: its crate and name and each source with its digest, and with the
    /// toolchain; None while a source is missing.
    fn code(
        &self,
        workspace: &Path,
        krate: &str,
        name: &str,
        sources: &[String],
        toolchain: &str,
    ) -> Result<Option<Code>> {
        let mut h = Sha256::new();
        h.update(format!("hsm program 1\n{krate}\n{name}\n"));
        for source in sources {
            let Some(digest) = self.compiler_sha(&workspace.join(source))? else {
                return Ok(None);
            };
            h.update(format!("{source}\0{digest}\n"));
        }
        let portable = format!("{:x}", h.finalize());
        let native = format!("{:x}", Sha256::digest(format!("{toolchain}\n{portable}")));
        Ok(Some(Code { native, portable }))
    }

    /// The kept run for `key` whose reads still hold, if there is one.
    fn lookup(&self, key: &str, ask: &Ask, declared: &[(String, String, String)]) -> Result<Option<Kept>> {
        let path = self.dir.join("runs").join(format!("{key}.json"));
        let Ok(bytes) = fs::read(&path) else {
            return Ok(None);
        };
        let kept: Vec<Kept> = serde_json::from_slice(&bytes).unwrap_or_default();
        'each: for mut k in kept {
            // The key already binds this staged request's original input snapshot. Older
            // records may also name a generated root file reread after the producer wrote it.
            k.reads = dependency_reads(ask, declared, k.reads);
            if !self.reads_hold(&k.reads, ask)? { continue 'each; }
            if k.files.iter().all(|(_, d)| self.dir.join("blobs").join(d).is_file()) {
                // The time a run was last used is what the prune goes by.
                let _ = fs::File::options()
                    .write(true)
                    .open(&path)
                    .and_then(|f| f.set_modified(SystemTime::now()));
                return Ok(Some(k));
            }
        }
        Ok(None)
    }

    /// Run the program into a scratch directory, admitted at its peak, and keep its files.
    /// False beside the run when what it read is unknown, so it must not be kept.
    fn execute(
        &self,
        program: &Path,
        ask: &Ask,
        args: &[Arg],
        code: &Code,
        sources: &[String],
        declared: &[(String, String, String)],
        environment: &BTreeMap<String, String>,
        lease: &Lease,
    ) -> Result<(Kept, bool)> {
        let scratch = self.dir.join("tmp").join(format!("{}-{}", std::process::id(), self.serial()));
        let out = scratch.join("out");
        fs::create_dir_all(&out)?;
        let reads = scratch.join("reads");
        let result = (|| {
            let mut cmd = Command::new(program);
            for a in args {
                match a {
                    Arg::Out(_) => cmd.arg(&out),
                    Arg::File(p, _) => cmd.arg(p),
                    Arg::Text(s) => cmd.arg(s),
                };
            }
            cmd.current_dir(&ask.root)
                .env_clear()
                .envs(environment)
                .env("HSM_READS", &reads)
                .env("HSM_IMPORT_DIR", ask.workspace.join(".cache/hsm/import"));
            lease.apply(&mut cmd)?;
            let peak = format!("{} {}", ask.krate, ask.name);
            let done = {
                let _ticket = self.admit(self.peak(&peak, PROGRAM_PEAK));
                finish(cmd)?
            };
            self.measured(&peak, done.peak);
            if !done.ok {
                bail!(
                    "{} exited {}:\n{}",
                    ask.name,
                    done.code,
                    String::from_utf8_lossy(&done.stderr)
                );
            }
            let (dynamic, named_reads) = match fs::read_to_string(&reads) {
                Ok(text) => (self.read_list(&text, ask)?, true),
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => (vec![], false),
                Err(error) => return Err(error).context("reading the program's input record"),
            };
            let read = dependency_reads(ask, declared, dynamic);
            let stable_reads: Vec<_> = read.iter().filter(|(base, file, _)|
                !(staged(ask) && base == "root" && ask.outputs.as_ref().unwrap().contains(file)))
                .cloned().collect();
            let storable = (named_reads || ask.inputs.is_some()) && self.reads_hold(&stable_reads, ask)?;
            let (files, absent) = if let Some(outputs) = &ask.outputs {
                self.ingest_declared(&ask.root, outputs)?
            } else { (self.ingest(&out)?, Vec::new()) };
            Ok((
                Kept {
                    reads: read,
                    files,
                    absent,
                    stdout: String::from_utf8(done.stdout)?,
                    stderr: String::from_utf8_lossy(&done.stderr).into_owned(),
                    seconds: done.seconds,
                    peak: done.peak,
                    code: code.native.clone(),
                    portable: run_key(&code.portable, args, ask, declared, environment),
                    sources: sources.to_vec(),
                },
                storable,
            ))
        })();
        let _ = fs::remove_dir_all(&scratch);
        result
    }

    fn declared_reads(&self, ask: &Ask) -> Result<Vec<(String, String, String)>> {
        ask.inputs.iter().flatten().map(|name| {
            let digest = self.sha(&ask.root.join(name))?.unwrap_or_else(|| "absent".to_owned());
            Ok(("root".to_owned(), name.clone(), digest))
        }).collect()
    }

    fn reads_hold(&self, reads: &[(String, String, String)], ask: &Ask) -> Result<bool> {
        for (base, file, digest) in reads {
            let current = self.sha(&resolve(base, file, ask))?;
            if if digest == "absent" { current.is_some() }
                else { current.as_deref() != Some(digest.as_str()) } { return Ok(false); }
        }
        Ok(true)
    }

    /// Declared graph outputs share the same immutable blobs as directory-argument part runs.
    fn ingest_declared(&self, root: &Path, outputs: &[String]) -> Result<(Vec<(String, String)>, Vec<String>)> {
        let (mut files, mut absent) = (Vec::new(), Vec::new());
        for name in outputs {
            let path = root.join(name);
            let Some(digest) = self.sha(&path)? else { absent.push(name.clone()); continue; };
            let blob = self.dir.join("blobs").join(&digest);
            if !blob.is_file() {
                let temporary = self.dir.join("blobs").join(format!(".{}-{}", std::process::id(), self.serial()));
                clone_or_copy(&path, &temporary)?;
                fs::rename(&temporary, &blob)?;
            }
            let _ = fs::File::options().write(true).open(&blob)
                .and_then(|file| file.set_modified(SystemTime::now()));
            files.push((name.clone(), digest));
        }
        Ok((files, absent))
    }

    /// The reads the kernel listed, `hsm-reads 1` and then `path\tsha256` a line, each named
    /// from the root, from the workspace, or whole.
    fn read_list(&self, text: &str, ask: &Ask) -> Result<Vec<(String, String, String)>> {
        let mut lines = text.lines();
        ensure!(lines.next() == Some("hsm-reads 1"), "unreadable HSM_READS");
        let mut out = BTreeSet::new();
        for line in lines {
            let (path, digest) = line.rsplit_once('\t').context("unreadable HSM_READS line")?;
            let full = normal(&ask.root.join(path));
            let named = if let Ok(r) = full.strip_prefix(&ask.root) {
                ("root".to_owned(), r.to_string_lossy().into_owned())
            } else if let Ok(r) = full.strip_prefix(&ask.workspace) {
                ("workspace".to_owned(), r.to_string_lossy().into_owned())
            } else {
                ("/".to_owned(), full.to_string_lossy().into_owned())
            };
            out.insert((named.0, named.1, digest.to_owned()));
        }
        Ok(out.into_iter().collect())
    }

    /// Each file the run left, kept by content: its name and SHA-256.
    fn ingest(&self, out: &Path) -> Result<Vec<(String, String)>> {
        let mut files = vec![];
        let mut pending = vec![out.to_path_buf()];
        while let Some(directory) = pending.pop() {
        for entry in fs::read_dir(directory)? {
            let entry = entry?;
            let name = entry
                .file_name()
                .into_string()
                .map_err(|_| anyhow!("a file name that is not UTF-8"))?;
            if name.starts_with('.') {
                continue;
            }
            if entry.file_type()?.is_dir() { pending.push(entry.path()); continue; }
            ensure!(entry.file_type()?.is_file(), "{name}: a program writes files, not directories");
            let path = entry.path();
            let name = path.strip_prefix(out)?.to_string_lossy().into_owned();
            let bytes = fs::read(entry.path())?;
            let digest = format!("{:x}", Sha256::digest(&bytes));
            let blob = self.dir.join("blobs").join(&digest);
            if !blob.is_file() {
                fs::rename(entry.path(), &blob)?;
            }
            // Fresh until the run that names it lands, however long the program ran.
            let _ = fs::File::options()
                .write(true)
                .open(&blob)
                .and_then(|f| f.set_modified(SystemTime::now()));
            files.push((name, digest));
        }
        }
        files.sort();
        Ok(files)
    }

    fn keep(&self, key: &str, kept: &Kept) -> Result<()> {
        let path = self.dir.join("runs").join(format!("{key}.json"));
        let mut all: Vec<Kept> = fs::read(&path)
            .ok()
            .and_then(|b| serde_json::from_slice(&b).ok())
            .unwrap_or_default();
        all.retain(|k| k.reads != kept.reads);
        all.insert(0, kept.clone());
        all.truncate(VARIANTS);
        write_atomic(&path, &serde_json::to_vec(&all)?)
    }

    /// Each file into `out`, cloned from its blob, unless the file there holds it already.
    fn place(&self, files: &[(String, String)], absent: &[String], out: &Path) -> Result<()> {
        for (name, digest) in files {
            let dest = out.join(name);
            ensure!(Path::new(name).components().all(|c| matches!(c, Component::Normal(_))),
                    "an output has a relative path");
            if self.sha(&dest)?.as_deref() == Some(digest.as_str()) {
                continue;
            }
            // Named to end as the file does, so whatever keeps it out of the tree keeps this out.
            fs::create_dir_all(dest.parent().context("output parent")?)?;
            let leaf = dest.file_name().context("output file name")?.to_string_lossy();
            let temp = dest.with_file_name(format!(".{leaf}.{}-{}.{leaf}", std::process::id(), self.serial()));
            clone_or_copy(&self.dir.join("blobs").join(digest), &temp)?;
            fs::File::options()
                .write(true)
                .open(&temp)?
                .set_modified(SystemTime::now())?;
            fs::rename(&temp, &dest)?;
        }
        for name in absent {
            ensure!(relative_file(name), "an absent output has a relative path");
            match fs::remove_file(out.join(name)) {
                Ok(()) => {},
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => {},
                Err(error) => return Err(error).with_context(|| format!("removing absent output {name}")),
            }
        }
        Ok(())
    }

    fn serial(&self) -> u64 {
        self.serial.fetch_add(1, Ordering::SeqCst)
    }

    fn peak(&self, program: &str, unknown: u64) -> u64 {
        self.peaks.lock().unwrap().get(program).copied().unwrap_or(unknown)
    }

    fn measured(&self, program: &str, peak: u64) {
        let mut peaks = self.peaks.lock().unwrap();
        peaks.insert(program.to_owned(), peak);
        if let Ok(bytes) = serde_json::to_vec(&*peaks) {
            let _ = write_atomic(&self.dir.join("peaks.json"), &bytes);
        }
    }

    /// Wait in turn for room in the budget, and for the system's memory pressure to fall below
    /// critical. A run larger than the whole budget runs alone.
    fn admit(&self, bytes: u64) -> Ticket<'_> {
        let mut gate = self.gate.lock().unwrap();
        let me = gate.next;
        gate.next += 1;
        gate.queue.push_back(me);
        loop {
            let first = gate.queue.front() == Some(&me);
            let fits = gate.running == 0 || gate.held + bytes <= self.budget;
            if first && fits && (gate.running == 0 || pressure() < CRITICAL) {
                break;
            }
            // Pressure falls without telling anyone, so a waiter looks again on its own.
            gate = self.turn.wait_timeout(gate, Duration::from_millis(250)).unwrap().0;
        }
        gate.queue.pop_front();
        gate.held += bytes;
        gate.running += 1;
        self.turn.notify_all();
        Ticket { builder: self, bytes }
    }

    /// A run unused for `keep` retires: renamed where no lookup finds it, and deleted at a prune
    /// `RETIRE` later, when an ask that found it before has placed its files. Blobs no live or
    /// retiring run names go once unwritten for `keep`; a landing run names its files only after
    /// they are in. With `programs`, so do the programs no such run names.
    pub fn prune(&self, keep: Duration, programs: bool) -> Result<()> {
        let now = SystemTime::now();
        let older = |meta: &fs::Metadata, age: Duration| {
            meta.modified().ok().and_then(|t| now.duration_since(t).ok()).is_some_and(|a| a > age)
        };
        let seconds = now.duration_since(SystemTime::UNIX_EPOCH).unwrap_or_default().as_secs();
        let (mut blobs, mut codes) = (BTreeSet::new(), BTreeSet::new());
        for entry in fs::read_dir(self.dir.join("runs"))?.flatten() {
            let mut path = entry.path();
            let Ok(meta) = entry.metadata() else { continue };
            match path.extension().and_then(|e| e.to_str()) {
                // Its name carries when it retired, so its time stays its last use: a daemon
                // that prunes the least recently used first still takes it before a live run.
                Some("json") if older(&meta, keep) => {
                    let retired = path.with_extension(format!("{seconds}.retired"));
                    if fs::rename(&path, &retired).is_ok() {
                        path = retired;
                    }
                }
                Some("retired") => {
                    let at = path.file_stem().map(Path::new).and_then(|s| s.extension())
                        .and_then(|e| e.to_str()?.parse::<u64>().ok());
                    if at.map_or(older(&meta, RETIRE), |at| seconds.saturating_sub(at) > RETIRE.as_secs()) {
                        let _ = fs::remove_file(&path);
                        continue;
                    }
                }
                Some("json") => {}
                _ => continue,
            }
            let Ok(bytes) = fs::read(&path) else { continue };
            for k in serde_json::from_slice::<Vec<Kept>>(&bytes).unwrap_or_default() {
                blobs.extend(k.files.into_iter().map(|(_, d)| d));
                codes.insert(k.code);
            }
        }
        for entry in fs::read_dir(self.dir.join("blobs"))?.flatten() {
            let name = entry.file_name().to_string_lossy().into_owned();
            if !blobs.contains(&name) && entry.metadata().is_ok_and(|m| older(&m, keep)) {
                let _ = fs::remove_file(entry.path());
            }
        }
        if programs {
            for entry in fs::read_dir(self.dir.join("programs"))?.flatten() {
                let name = entry.file_name().to_string_lossy().into_owned();
                if entry.path().is_dir() && !codes.contains(&name) && entry.metadata().is_ok_and(|m| older(&m, keep)) {
                    let _ = fs::remove_dir_all(entry.path());
                }
            }
        }
        Ok(())
    }
}

pub struct Entered(Arc<Builder>);

impl Entered {
    /// Answer the ask: its files placed, and what the program said.
    pub fn answer(self, ask: Ask, lease: Option<Lease>) -> Result<Value> {
        self.0.run(ask, lease)
    }
}

impl Drop for Entered {
    fn drop(&mut self) {
        *self.0.last.lock().unwrap() = Instant::now();
        self.0.active.fetch_sub(1, Ordering::SeqCst);
    }
}

/// Marks a key's run done when the ask that ran it is through, kept or not, so an ask waiting
/// on it looks again.
struct Landing<'a> {
    builder: &'a Builder,
    key: &'a str,
    flight: Option<Arc<Flight>>,
}

impl Drop for Landing<'_> {
    fn drop(&mut self) {
        if let Some(f) = self.flight.take() {
            self.builder.flights.lock().unwrap().remove(self.key);
            *f.done.lock().unwrap() = true;
            f.landed.notify_all();
        }
    }
}

/// A run's key: its program's code, and its arguments, a file by its bytes and the output
/// directory by its place.
fn primary(code: &str, args: &[Arg]) -> String {
    let mut h = Sha256::new();
    h.update(format!("hsm run 1\n{code}\n"));
    for a in args {
        match a {
            Arg::Out(_) => h.update("out\n"),
            Arg::File(_, d) => h.update(format!("file {d}\n")),
            Arg::Text(s) => h.update(format!("text {} {s}\n", s.len())),
        }
    }
    format!("{:x}", h.finalize())
}

/// A graph run includes declared raw reads and semantic settings; physical staging and progress
/// locations do not distinguish equal work in two fresh staged roots.
fn run_key(code: &str, args: &[Arg], ask: &Ask, reads: &[(String, String, String)],
           environment: &BTreeMap<String, String>) -> String {
    let mut h = Sha256::new();
    h.update(format!("hsm run 2\n{}\n", primary(code, args)));
    h.update(if ask.inputs.is_some() { b"declared\n".as_slice() } else { b"dynamic\n".as_slice() });
    for (base, path, digest) in reads { h.update(format!("input {base}\0{path}\0{digest}\n")); }
    if let Some(outputs) = &ask.outputs {
        h.update("declared outputs\n");
        for name in outputs { h.update(format!("{name}\n")); }
    }
    for (key, value) in environment {
        if matches!(key.as_str(), "HSM_BUILD_PROGRESS" | "HSM_KEEP_HOURS") { continue; }
        h.update(format!("env {key}\0{}\n", semantic_path(value, ask)));
    }
    format!("{:x}", h.finalize())
}

fn staged(ask: &Ask) -> bool { ask.inputs.is_some() && ask.outputs.is_some() }

/// A staged producer's declared pre-run reads define its root inputs. Dynamic reads of files
/// it creates inside that root are output/intermediate implementation details. Reads outside
/// the stage remain dependencies, and legacy dynamic-only runs retain their full read record.
fn dependency_reads(ask: &Ask, declared: &[(String, String, String)],
                    dynamic: Vec<(String, String, String)>) -> Vec<(String, String, String)> {
    declared.iter().cloned().chain(dynamic.into_iter()
        .filter(|(base, _, _)| !staged(ask) || base != "root"))
        .collect::<BTreeSet<_>>().into_iter().collect()
}

fn semantic_path(value: &str, ask: &Ask) -> String {
    value.replace(ask.root.to_string_lossy().as_ref(), "$HSM_ROOT")
        .replace(ask.workspace.to_string_lossy().as_ref(), "$HSM_WORKSPACE")
}

fn relative_file(name: &str) -> bool {
    !name.is_empty() && Path::new(name).components().all(|c| matches!(c, Component::Normal(_)))
}

fn normalize_files(files: &mut Option<Vec<String>>) -> Result<()> {
    if let Some(files) = files {
        let mut normalized = BTreeSet::new();
        for name in files.iter() {
            let path = Path::new(name);
            ensure!(path.components().all(|c| matches!(c, Component::Normal(_) | Component::CurDir)),
                    "declared files are relative to their root: {name}");
            let name = normal(path).to_string_lossy().into_owned();
            ensure!(relative_file(&name), "a declared file has a relative path");
            normalized.insert(name);
        }
        *files = normalized.into_iter().collect();
    }
    Ok(())
}

fn run_environment(ask: &Ask) -> Result<BTreeMap<String, String>> {
    let mut environment: BTreeMap<_, _> = cargo_env(&home()).into_iter().collect();
    if let Ok(path) = std::env::var("PATH") {
        let fallback = environment.get("PATH").cloned().unwrap_or_default();
        environment.insert("PATH".to_owned(), format!("{path}:{fallback}"));
    }
    for (key, value) in &ask.environment {
        ensure!(!key.is_empty() && !key.contains('=') && !key.contains('\0') && !value.contains('\0'),
                "a producer environment has valid process keys and values");
        environment.insert(key.clone(), value.clone());
    }
    environment.insert("HSM_WORKSPACE".to_owned(), ask.workspace.to_string_lossy().into_owned());
    environment.insert("HSM_REPO_ROOT".to_owned(), ask.root.to_string_lossy().into_owned());
    Ok(environment)
}

/// A real compiler run replaces its prior module/include closure and keeps the caller's
/// canonical/configuration inputs that were not part of that closure.
fn refreshed_sources(declared: &[String], previous: &[String], fresh: Vec<String>) -> Vec<String> {
    let previous: BTreeSet<_> = previous.iter().cloned().collect();
    fresh.into_iter().chain(declared.iter().filter(|path| !previous.contains(path.as_str())).cloned())
        .collect::<BTreeSet<_>>().into_iter().collect()
}

fn resolve(base: &str, file: &str, ask: &Ask) -> PathBuf {
    match base {
        "root" => ask.root.join(file),
        "workspace" => ask.workspace.join(file),
        _ => PathBuf::from(file),
    }
}

/// `path` with its `.` and `..` taken out, without reading the disk.
fn normal(path: &Path) -> PathBuf {
    let mut out = PathBuf::new();
    for c in path.components() {
        match c {
            Component::ParentDir => {
                out.pop();
            }
            Component::CurDir => {}
            c => out.push(c),
        }
    }
    out
}

/// Whether the file at `path` changed at or after `t`, by its ctime, which every write moves.
fn changed_since(path: &Path, t: SystemTime) -> bool {
    fs::metadata(path)
        .map(|m| {
            SystemTime::UNIX_EPOCH + Duration::new(m.ctime() as u64, m.ctime_nsec() as u32) >= t
        })
        .unwrap_or(true)
}

fn compiler_changed_since(path: &Path, t: SystemTime) -> bool {
    if !path.is_dir() { return changed_since(path, t); }
    let mut pending = vec![path.to_path_buf()];
    while let Some(directory) = pending.pop() {
        if changed_since(&directory, t) { return true; }
        let Ok(entries) = fs::read_dir(directory) else { return true; };
        for entry in entries {
            let Ok(entry) = entry else { return true; };
            match entry.file_type() {
                Ok(kind) if kind.is_dir() => pending.push(entry.path()),
                Ok(_) => {},
                Err(_) => return true,
            }
        }
    }
    false
}

fn plain(name: &str) -> bool {
    !name.is_empty()
        && name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_')
}

/// The files under `workspace` rustc compiled into a program, off the dep-info file cargo wrote
/// beside it: one make rule, a space inside a path written `\ `.
fn compiled(dep_info: &Path, workspace: &Path) -> Option<Vec<String>> {
    let text = fs::read_to_string(dep_info).ok()?;
    let rule = text.split("\n\n").next()?.replace("\\\n", " ");
    let (_, deps) = rule.split_once(": ")?;
    let mut out = vec![];
    for dep in deps.replace("\\ ", "\0").split_whitespace() {
        let path = PathBuf::from(dep.replace('\0', " "));
        let path = path.canonicalize().unwrap_or(path);
        if let Ok(rel) = path.strip_prefix(workspace) {
            out.push(rel.to_string_lossy().into_owned());
        }
    }
    Some(out)
}

/// The lockfile, the workspace's manifest, and the manifest of each package a source is
/// compiled in: the nearest `Cargo.toml` above it, or the crate's for a program kept beside its
/// part, as `_rust_part._manifests` names them for the trace.
fn manifests(sources: &[String], krate: &str, workspace: &Path) -> Vec<String> {
    let mut out: BTreeSet<String> = [
        "tools/hsm/Cargo.toml".to_owned(),
        "tools/hsm/Cargo.lock".to_owned(),
        format!("tools/hsm/{krate}/Cargo.toml"),
    ]
    .into();
    for src in sources {
        let parts: Vec<&str> = src.split('/').collect();
        if parts.len() < 4 || parts[0] != "tools" || parts[1] != "hsm" {
            continue;
        }
        for n in (3..parts.len()).rev() {
            let dir = parts[..n].join("/");
            if workspace.join(&dir).join("Cargo.toml").is_file() {
                out.insert(format!("{dir}/Cargo.toml"));
                break;
            }
        }
    }
    out.into_iter().collect()
}

fn home() -> PathBuf {
    std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/"))
}

/// `cargo` on the PATH, else where rustup puts it: Homebrew's rustup on a Mac, `~/.cargo`.
fn cargo() -> Result<PathBuf> {
    let path = std::env::var_os("PATH").unwrap_or_default();
    std::env::split_paths(&path)
        .map(|d| d.join("cargo"))
        .chain([
            PathBuf::from("/opt/homebrew/opt/rustup/bin/cargo"),
            home().join(".cargo/bin/cargo"),
        ])
        .find(|p| p.is_file())
        .ok_or_else(|| anyhow!("cargo is not installed (https://rustup.rs)"))
}

/// What cargo and rustc run with: the user's home and rustup's, the cargo's own directory first
/// on the PATH, then the compilers and CMake the C++ of Manifold builds with.
fn cargo_env(home: &Path) -> Vec<(String, String)> {
    let dir = cargo()
        .ok()
        .and_then(|c| c.parent().map(Path::to_path_buf))
        .unwrap_or_default();
    let mut env = vec![
        ("HOME".to_owned(), home.display().to_string()),
        (
            "PATH".to_owned(),
            format!("{}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin", dir.display()),
        ),
    ];
    for name in ["RUSTUP_HOME", "CARGO_HOME", "RUSTUP_TOOLCHAIN"] {
        if let Some(v) = std::env::var_os(name) {
            env.push((name.to_owned(), v.to_string_lossy().into_owned()));
        }
    }
    env
}

/// Run `cmd` to its end, its output and error read as it goes.
fn finish(mut cmd: Command) -> Result<Finished> {
    let started = Instant::now();
    cmd
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    let mut child = ipc::spawn(&mut cmd).context("starting a part program")?;
    let mut err = child.stderr.take().context("no stderr")?;
    let errors = thread::spawn(move || {
        let mut v = vec![];
        let _ = err.read_to_end(&mut v);
        v
    });
    let mut stdout = vec![];
    child.stdout.take().context("no stdout")?.read_to_end(&mut stdout)?;
    let stderr = errors.join().unwrap_or_default();
    let pid = child.id() as libc::pid_t;
    let mut status = 0;
    // wait4 reaps the one child started here and writes `status` and `usage`, both owned here.
    let mut usage: libc::rusage = unsafe { std::mem::zeroed() };
    loop {
        let r = unsafe { libc::wait4(pid, &mut status, 0, &mut usage) };
        if r == pid {
            break;
        }
        let e = std::io::Error::last_os_error();
        if e.kind() != std::io::ErrorKind::Interrupted {
            return Err(e).context("waiting for a part program");
        }
    }
    let ok = libc::WIFEXITED(status) && libc::WEXITSTATUS(status) == 0;
    let code = if libc::WIFEXITED(status) {
        libc::WEXITSTATUS(status)
    } else {
        128 + libc::WTERMSIG(status)
    };
    let peak = usage.ru_maxrss as u64 * if cfg!(target_os = "macos") { 1 } else { 1024 };
    Ok(Finished {
        ok,
        code,
        stdout,
        stderr,
        seconds: started.elapsed().as_secs_f64(),
        peak,
    })
}

/// The system's memory pressure: 1 normal, 2 warn, 4 critical; 0 where it says nothing.
fn pressure() -> i32 {
    #[cfg(target_os = "macos")]
    {
        let mut level: libc::c_int = 0;
        let mut size = std::mem::size_of::<libc::c_int>();
        // sysctlbyname reads a NUL-terminated name and writes at most `size` bytes into `level`.
        let r = unsafe {
            libc::sysctlbyname(
                c"kern.memorystatus_vm_pressure_level".as_ptr(),
                (&mut level as *mut libc::c_int).cast(),
                &mut size,
                std::ptr::null_mut(),
                0,
            )
        };
        if r == 0 {
            return level;
        }
    }
    0
}

/// `from` at `to`: an APFS clone where it can be, sharing blocks until either side writes.
fn clone_or_copy(from: &Path, to: &Path) -> Result<()> {
    #[cfg(target_os = "macos")]
    {
        use std::os::unix::ffi::OsStrExt;
        let a = std::ffi::CString::new(from.as_os_str().as_bytes())?;
        let b = std::ffi::CString::new(to.as_os_str().as_bytes())?;
        // clonefile reads two NUL-terminated paths owned here.
        if unsafe { libc::clonefile(a.as_ptr(), b.as_ptr(), 0) } == 0 {
            return Ok(());
        }
    }
    fs::copy(from, to).with_context(|| format!("copying {} to {}", from.display(), to.display()))?;
    Ok(())
}

/// Whether the process `pid` is running.
fn alive(pid: libc::pid_t) -> bool {
    // kill with no signal only asks whether `pid` may be signalled.
    pid > 0 && unsafe { libc::kill(pid, 0) } == 0
}

fn write_atomic(path: &Path, bytes: &[u8]) -> Result<()> {
    static SERIAL: AtomicU64 = AtomicU64::new(0);
    let serial = SERIAL.fetch_add(1, Ordering::SeqCst);
    let temp = path.with_extension(format!("tmp{}-{serial}", std::process::id()));
    fs::write(&temp, bytes)?;
    fs::rename(&temp, path)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::os::unix::fs::PermissionsExt;

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Result<Self> {
            static SERIAL: AtomicUsize = AtomicUsize::new(0);
            let root = std::env::temp_dir().join(format!("hsm-run-fixture-{}-{}-{}",
                std::process::id(), SERIAL.fetch_add(1, Ordering::Relaxed),
                SystemTime::now().duration_since(SystemTime::UNIX_EPOCH)?.as_nanos()));
            fs::create_dir_all(&root)?;
            Ok(Self(root.canonicalize()?))
        }
        fn put(&self, path: &str, text: &str) -> Result<()> { put(&self.0.join(path), text) }
        fn stage(&self, name: &str) -> Result<PathBuf> {
            let root = self.0.join(name);
            put(&root.join("runtime.txt"), "first input")?;
            put(&root.join("tools/hsm/fixture/src/embedded.txt"), "embedded")?;
            put(&root.join("bin/native-helper"), "#!/bin/sh\nprintf helper\n")?;
            fs::set_permissions(root.join("bin/native-helper"), fs::Permissions::from_mode(0o755))?;
            Ok(root)
        }
        fn ask(&self, root: PathBuf) -> Ask {
            Ask {
                workspace: self.0.join("workspace"),
                environment: BTreeMap::from([
                    ("PATH".into(), format!("{}/bin:/usr/bin:/bin", root.display())),
                    ("HSM_BUILD_PROGRESS".into(), root.join("progress.log").display().to_string()),
                    ("FLAVOR".into(), "plain".into()),
                ]),
                root, krate: "fixture".into(), name: "fixture".into(), args: vec![],
                inputs: Some(vec!["runtime.txt".into(), "optional.txt".into(),
                    "bin/native-helper".into(), "tools/hsm/fixture/src/embedded.txt".into()]),
                outputs: Some(vec!["products/result.txt".into(), "products/optional.txt".into()]),
                compiler_inputs: Some(vec!["tools/hsm/fixture/src/main.rs".into(), "tools/hsm/canonical.json".into()]),
                allow_compile: true, cache_only: false,
            }
        }
    }
    impl Drop for Fixture { fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); } }

    fn put(path: &Path, text: &str) -> Result<()> {
        fs::create_dir_all(path.parent().context("fixture parent")?)?;
        fs::write(path, text)?;
        Ok(())
    }
    fn run(builder: &Builder, ask: &Ask) -> Result<Value> {
        builder.run(ask.clone(), hsm_run_slots::inherited()?)
    }

    const PROGRAM: &str = r#"// EXTRA_DECL
use std::{env, fs, path::Path, process::Command};
const EMBEDDED: &str = include_str!("embedded.txt");
fn main() -> std::io::Result<()> {
    if let Ok(path) = env::var("HSM_BUILD_PROGRESS") { fs::write(path, "done")?; }
    fs::create_dir_all("products")?;
    let args: Vec<_> = env::args().collect();
    if args.get(1).map(String::as_str) == Some("--legacy-out") {
        fs::write(Path::new(&args[2]).join("legacy.txt"), "legacy output")?;
        fs::write(env::var("HSM_READS").unwrap(), "hsm-reads 1\n")?;
        return Ok(());
    }
    if args.get(1).map(String::as_str) == Some("--self-reads") {
        let _original = fs::read("metadata.txt")?;
        fs::write("metadata.txt", "generated metadata")?;
        fs::write("products/self.txt", "self output")?;
        fs::write("products/intermediate.txt", "generated intermediate")?;
        let mut reads = String::from("hsm-reads 1\n");
        for (path, key) in [("metadata.txt", "METADATA_DIGEST"),
            ("products/self.txt", "SELF_DIGEST"), ("products/intermediate.txt", "INTERMEDIATE_DIGEST")] {
            let _reread = fs::read(path)?;
            reads.push_str(&format!("{path}\t{}\n", env::var(key).unwrap()));
        }
        fs::write(env::var("HSM_READS").unwrap(), reads)?;
        return Ok(());
    }
    if env::args().any(|arg| arg == "--consumer") {
        fs::write("products/final.txt", fs::read("products/result.txt")?)?;
        return Ok(());
    }
    let _read = fs::read("runtime.txt")?;
    let helper = Command::new("native-helper").output()?;
    assert!(helper.status.success());
    let text = format!("{}:{}:{}:{}:{}", EMBEDDED.trim(), "extra-default",
        Path::new("optional.txt").is_file(), env::var("FLAVOR").unwrap(),
        String::from_utf8_lossy(&helper.stdout));
    fs::write("products/result.txt", text)?;
    Ok(())
}
"#;

    #[test]
    fn declared_graph_runs_reuse_code_and_bytes_across_fresh_stages() -> Result<()> {
        let f = Fixture::new()?;
        f.put("workspace/tools/hsm/Cargo.toml", "[workspace]\nmembers=[\"fixture\",\"other\"]\nresolver=\"2\"\n")?;
        f.put("workspace/tools/hsm/Cargo.lock", "version=4\n[[package]]\nname=\"fixture\"\nversion=\"0.1.0\"\n[[package]]\nname=\"other\"\nversion=\"0.1.0\"\n")?;
        f.put("workspace/tools/hsm/fixture/Cargo.toml", "[package]\nname=\"fixture\"\nversion=\"0.1.0\"\nedition=\"2021\"\n")?;
        f.put("workspace/tools/hsm/other/Cargo.toml", "[package]\nname=\"other\"\nversion=\"0.1.0\"\nedition=\"2021\"\n[lib]\npath=\"lib.rs\"\n")?;
        f.put("workspace/tools/hsm/other/lib.rs", "pub const OTHER: bool = true;\n")?;
        f.put("workspace/tools/hsm/fixture/src/main.rs", PROGRAM)?;
        f.put("workspace/tools/hsm/fixture/src/embedded.txt", "embedded")?;
        f.put("workspace/tools/hsm/canonical.json", "{\"selected_configuration\":true}\n")?;
        let builder = Builder::new(&f.0.join("store"), 1024)?;
        let first_root = f.stage("first")?;
        let mut first = f.ask(first_root.clone());
        first.cache_only = true;
        assert_eq!(run(&builder, &first)?["available"], false);
        assert!(!f.0.join("workspace/tools/hsm/target").exists());
        first.cache_only = false;
        let a = run(&builder, &first)?;
        assert_eq!(a["compiled"], true);
        assert_eq!(a["hit"], false);
        let digest = a["file_hashes"]["products/result.txt"].clone();
        let artifact = PathBuf::from(a["artifacts"]["products/result.txt"].as_str().unwrap());
        assert!(artifact.is_absolute() && artifact.is_file());
        assert_eq!(a["missing_outputs"], json!(["products/optional.txt"]));

        // Staged metadata may be both an original input and a rewritten output. Generated
        // root files reread by the producer do not become prerequisites for the next stage.
        let mut self_reads = first.clone();
        self_reads.args = vec!["--self-reads".into()];
        self_reads.inputs = Some(vec!["metadata.txt".into()]);
        self_reads.outputs = Some(vec!["metadata.txt".into(), "products/self.txt".into()]);
        for (name, value) in [("METADATA_DIGEST", "generated metadata"),
            ("SELF_DIGEST", "self output"), ("INTERMEDIATE_DIGEST", "generated intermediate")] {
            self_reads.environment.insert(name.into(), format!("{:x}", Sha256::digest(value.as_bytes())));
        }
        put(&first_root.join("metadata.txt"), "original metadata")?;
        let made = run(&builder, &self_reads)?;
        assert_eq!(made["kept"], true);
        assert_eq!(made["hit"], false);
        let original_hash = format!("{:x}", Sha256::digest(b"original metadata"));
        assert_eq!(made["reads"], json!([["root", "metadata.txt", original_hash]]));
        let record = builder.dir.join("runs").join(format!("{}.json", made["key"].as_str().unwrap()));
        let mut older: Vec<Kept> = serde_json::from_slice(&fs::read(&record)?)?;
        older[0].reads.extend([
            ("root".into(), "metadata.txt".into(), self_reads.environment["METADATA_DIGEST"].clone()),
            ("root".into(), "products/self.txt".into(), self_reads.environment["SELF_DIGEST"].clone()),
            ("root".into(), "products/intermediate.txt".into(), self_reads.environment["INTERMEDIATE_DIGEST"].clone()),
        ]);
        write_atomic(&record, &serde_json::to_vec(&older)?)?;
        let fresh_root = f.stage("self-read-stage")?;
        put(&fresh_root.join("metadata.txt"), "original metadata")?;
        let fresh = f.ask(fresh_root.clone());
        self_reads.root = fresh.root;
        self_reads.environment.insert("PATH".into(), fresh.environment["PATH"].clone());
        self_reads.environment.insert("HSM_BUILD_PROGRESS".into(), fresh.environment["HSM_BUILD_PROGRESS"].clone());
        let restored_self = run(&builder, &self_reads)?;
        assert_eq!(restored_self["hit"], true);
        assert_eq!(restored_self["reads"], made["reads"]);
        assert_eq!(fs::read_to_string(fresh_root.join("metadata.txt"))?, "generated metadata");
        assert!(fresh_root.join("products/self.txt").is_file());
        assert!(!fresh_root.join("products/intermediate.txt").exists());

        let mut legacy = first.clone();
        legacy.inputs = None;
        legacy.outputs = None;
        let legacy_out = first_root.join("legacy");
        fs::create_dir_all(&legacy_out)?;
        legacy.args = vec!["--legacy-out".into(), legacy_out.display().to_string()];
        assert_eq!(run(&builder, &legacy)?["hit"], false);
        fs::remove_file(legacy_out.join("legacy.txt"))?;
        assert_eq!(run(&builder, &legacy)?["hit"], true);
        assert_eq!(fs::read_to_string(legacy_out.join("legacy.txt"))?, "legacy output");

        let mut consumer = first.clone();
        consumer.args = vec!["--consumer".into()];
        consumer.inputs = Some(vec!["products/result.txt".into()]);
        consumer.outputs = Some(vec!["products/final.txt".into()]);
        assert_eq!(run(&builder, &consumer)?["hit"], false);

        let second_root = f.stage("second")?;
        let mut second = f.ask(second_root.clone());
        second.cache_only = true;
        let restored = run(&builder, &second)?;
        assert_eq!(restored["hit"], true);
        assert_eq!(restored["artifacts"]["products/result.txt"], a["artifacts"]["products/result.txt"]);
        assert_eq!(fs::read(second_root.join("products/result.txt"))?, fs::read(&artifact)?);
        fs::remove_file(second_root.join("products/result.txt"))?;
        put(&second_root.join("products/optional.txt"), "stale optional output")?;
        assert_eq!(run(&builder, &second)?["hit"], true);
        assert!(!second_root.join("products/optional.txt").exists());

        // Workspace member order and unrelated source bytes are outside the selected split.
        f.put("workspace/tools/hsm/Cargo.toml", "[workspace]\nmembers=[\"other\",\"fixture\"]\nresolver=\"2\"\n")?;
        f.put("workspace/tools/hsm/other/lib.rs", "pub const OTHER: bool = false;\n")?;
        assert_eq!(run(&builder, &second)?["hit"], true);
        put(&second_root.join("runtime.txt"), "another input, same produced shape")?;
        assert_eq!(run(&builder, &second)?["available"], false);
        second.cache_only = false;
        let rerun = run(&builder, &second)?;
        assert_eq!(rerun["hit"], false);
        assert_eq!(rerun["compiled"], false);
        assert_eq!(rerun["file_hashes"]["products/result.txt"], digest);
        let mut second_consumer = f.ask(second_root.clone());
        second_consumer.args = consumer.args.clone();
        second_consumer.inputs = consumer.inputs.clone();
        second_consumer.outputs = consumer.outputs.clone();
        assert_eq!(run(&builder, &second_consumer)?["hit"], true);

        put(&second_root.join("optional.txt"), "now present")?;
        let optional = run(&builder, &second)?;
        assert_eq!(optional["hit"], false);
        assert_ne!(optional["file_hashes"]["products/result.txt"], digest);
        second.environment.insert("FLAVOR".into(), "blue".into());
        let blue = run(&builder, &second)?;
        assert_eq!(blue["hit"], false);
        second.environment.insert("HSM_BUILD_PROGRESS".into(), second_root.join("another-progress.log").display().to_string());
        second.environment.insert("HSM_KEEP_HOURS".into(), "48".into());
        assert_eq!(run(&builder, &second)?["key"], blue["key"]);

        f.put("workspace/tools/hsm/fixture/src/extra.rs", "pub fn value() -> &'static str { \"first module\" }\n")?;
        f.put("workspace/tools/hsm/fixture/src/main.rs", &PROGRAM.replace("// EXTRA_DECL", "mod extra;")
            .replace("\"extra-default\"", "extra::value()"))?;
        second.allow_compile = false;
        assert_eq!(run(&builder, &second)?["available"], false);
        second.allow_compile = true;
        let changed_code = run(&builder, &second)?;
        assert_eq!(changed_code["compiled"], true);
        assert!(changed_code["sources"].as_array().unwrap().contains(&json!("tools/hsm/fixture/src/extra.rs")));
        f.put("workspace/tools/hsm/fixture/src/extra.rs", "pub fn value() -> &'static str { \"edited module\" }\n")?;
        let changed_module = run(&builder, &second)?;
        assert_eq!(changed_module["compiled"], true);
        assert_ne!(changed_module["code"], changed_code["code"]);
        f.put("workspace/tools/hsm/fixture/src/embedded.txt", "new embedded bytes")?;
        put(&second_root.join("tools/hsm/fixture/src/embedded.txt"), "new embedded bytes")?;
        let embedded = run(&builder, &second)?;
        assert_eq!(embedded["compiled"], true);
        assert!(embedded["sources"].as_array().unwrap().contains(&json!("tools/hsm/fixture/src/embedded.txt")));
        assert!(embedded["reads"].as_array().unwrap().iter().any(|row|
            row[1] == "tools/hsm/fixture/src/embedded.txt"));

        let key = embedded["key"].as_str().unwrap();
        let record = builder.dir.join("runs").join(format!("{key}.json"));
        let aged = SystemTime::now() - Duration::from_secs(3 * 3600);
        fs::File::options().write(true).open(&record)?.set_modified(aged)?;
        builder.prune(Duration::from_secs(48 * 3600), false)?;
        let declared = builder.declared_reads(&second)?;
        assert!(builder.lookup(key, &second, &declared)?.is_some());
        fs::File::options().write(true).open(&record)?.set_modified(aged)?;
        builder.prune(Duration::from_secs(2 * 3600), false)?;
        assert!(builder.lookup(key, &second, &declared)?.is_none());
        Ok(())
    }

    #[test]
    fn a_new_dep_info_closure_keeps_only_the_supplied_configuration_split() {
        let names = |rows: &[&str]| rows.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>();
        assert_eq!(refreshed_sources(&names(&["main.rs", "old.rs", "canonical.json"]),
            &names(&["main.rs", "old.rs"]), names(&["main.rs", "new.rs", "embedded.json"])),
            names(&["canonical.json", "embedded.json", "main.rs", "new.rs"]));
    }

    #[test]
    fn watched_compiler_directories_hash_membership_and_selected_file_bytes() -> Result<()> {
        let f = Fixture::new()?;
        f.put("workspace/numbers/selected.rs", "selected")?;
        f.put("workspace/numbers/nested/unselected.rs", "unused")?;
        let builder = Builder::new(&f.0.join("store"), 1024)?;
        let workspace = f.0.join("workspace");
        let sources = vec!["numbers".to_owned(), "numbers/selected.rs".to_owned()];
        let code = || builder.code(&workspace, "fixture", "fixture", &sources, "toolchain")
            .map(|value| value.unwrap().native);
        let first = code()?;
        f.put("workspace/numbers/nested/unselected.rs", "edited unused member")?;
        assert_eq!(code()?, first);
        f.put("workspace/numbers/selected.rs", "edited selected source")?;
        let selected = code()?;
        assert_ne!(selected, first);
        f.put("workspace/numbers/nested/new.rs", "new member")?;
        let added = code()?;
        assert_ne!(added, selected);
        fs::rename(workspace.join("numbers/nested/new.rs"), workspace.join("numbers/nested/renamed.rs"))?;
        assert_ne!(code()?, added);
        fs::remove_file(workspace.join("numbers/nested/renamed.rs"))?;
        assert_eq!(code()?, selected);
        assert!(builder.sha(&workspace.join("numbers")).is_err());
        Ok(())
    }
}
