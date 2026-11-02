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
    collections::{BTreeSet, HashMap, VecDeque},
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

/// What a run is asked for over the socket: `{"op":"run", ...}`.
#[derive(Debug, Deserialize, Serialize)]
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
}

/// A declared Python generator action. The shared plan supplies its inputs and outputs.
#[derive(Debug, Deserialize, Serialize)]
pub struct Generate {
    pub workspace: PathBuf,
    pub target: String,
    #[serde(default)]
    pub output: Option<PathBuf>,
    #[serde(default)]
    pub python: Option<PathBuf>,
}

/// A kept run.
#[derive(Clone, Deserialize, Serialize)]
struct Kept {
    /// Each file the run read: from the root, from the workspace, or `/` for a whole path.
    reads: Vec<(String, String, String)>,
    files: Vec<(String, String)>,
    stdout: String,
    stderr: String,
    seconds: f64,
    peak: u64,
    code: String,
    /// The run's key by its program's portable code.
    portable: String,
    sources: Vec<String>,
    #[serde(default)]
    action: Option<Value>,
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
        ask.workspace = ask
            .workspace
            .canonicalize()
            .with_context(|| format!("no workspace at {}", ask.workspace.display()))?;
        ask.root = ask
            .root
            .canonicalize()
            .with_context(|| format!("no root at {}", ask.root.display()))?;
        ensure!(
            plain(&ask.krate) && plain(&ask.name),
            "a crate and a program are plain names"
        );
        let args = self.classify(&ask)?;
        let out = args.iter().find_map(|a| match a {
            Arg::Out(p) => Some(p.clone()),
            _ => None,
        });
        let toolchain = self.toolchain(&ask.workspace)?;
        // A kept run needs its program's code, not the program: the sources it was last
        // compiled from, as they stand.
        let known = match self.sources(&ask.workspace, &ask.krate, &ask.name) {
            Some(sources) => self
                .code(&ask.workspace, &ask.krate, &ask.name, &sources, &toolchain)?
                .map(|code| (code, sources)),
            None => None,
        };
        let mut hit = match &known {
            Some((code, _)) => self.lookup(&primary(&code.native, &args), &ask)?,
            None => None,
        };
        // A stored answer does no heavy work. Every miss enters the host gate before taking
        // Cargo, memory or flight ownership; an admitted parent's RPC can therefore proceed.
        if hit.is_none() {
            lease = Some(hsm_run_slots::acquire(&format!("{}:{}", ask.krate, ask.name), lease, false)?);
        }
        let (code, sources, program, compiled, keepable) = match (&hit, known) {
            (Some(_), Some((code, sources))) => (code, sources, None, false, true),
            (_, known) => {
                let built = self.program(&ask, &toolchain, known, lease.as_ref().unwrap())?;
                (built.code, built.sources, Some(built.path), built.compiled, built.keepable)
            }
        };
        let key = primary(&code.native, &args);
        if hit.is_none() && compiled {
            hit = self.lookup(&key, &ask)?;
        }
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
            if leader {
                flight = Some(f);
            } else {
                let mut done = f.done.lock().unwrap();
                while !*done {
                    done = f.landed.wait(done).unwrap();
                }
                drop(done);
                hit = self.lookup(&key, &ask)?;
            }
        }
        let landing = Landing {
            builder: self,
            key: &key,
            flight,
        };
        let was_kept = hit.is_some();
        let (kept, kept_now) = match hit {
            Some(kept) => (kept, false),
            None => {
                let program = program.context("no program to run")?;
                let (kept, storable) = self.execute(&program, &ask, &args, &code, &sources, lease.as_ref().unwrap())?;
                let storable = storable && keepable;
                if storable {
                    self.keep(&key, &kept)?;
                }
                (kept, storable)
            }
        };
        drop(landing);
        if let Some(out) = &out {
            self.place(&kept.files, out)?;
        }
        Ok(json!({
            "stdout": kept.stdout, "stderr": kept.stderr, "sources": kept.sources,
            "reads": kept.reads, "files": kept.files.iter().map(|(n, _)| n).collect::<Vec<_>>(),
            "hit": was_kept, "kept": was_kept || kept_now, "compiled": compiled,
            "program_seconds": kept.seconds, "peak_bytes": kept.peak,
            "code": code.native, "key": key, "seconds": started.elapsed().as_secs_f64(),
        }))
    }

    fn generator_command(workspace: &Path, python: &Path, mode: &str) -> Command {
        let mut command = Command::new(python);
        command.arg(workspace.join("tools/hsm/generate.py")).arg(mode)
            .current_dir(workspace).env_clear().envs(cargo_env(&home()))
            .env("PYTHONDONTWRITEBYTECODE", "1");
        command
    }

    fn generate(&self, mut ask: Generate, socket: &Path, mut lease: Option<Lease>) -> Result<Value> {
        let started = Instant::now();
        ask.workspace = ask.workspace.canonicalize()?;
        let python = ask.workspace.join(ask.python.as_deref().unwrap_or(Path::new("tools/cad-venv/bin/python")));
        ensure!(plain(&ask.target), "a generator target is a plain name");
        let output = normal(&ask.workspace.join(ask.output.as_deref().unwrap_or(&ask.workspace)));
        fs::create_dir_all(&output)?;
        let mut describe = Self::generator_command(&ask.workspace, &python, "describe");
        describe.arg(&ask.target);
        let described = finish(describe)?;
        ensure!(described.ok, "generator plan failed:\n{}", String::from_utf8_lossy(&described.stderr));
        let recipe: Value = serde_json::from_slice(&described.stdout)?;
        let code = format!("{:x}", Sha256::digest(serde_json::to_vec(&recipe)?));
        let key = format!("{:x}", Sha256::digest(format!("hsm generator 1\n{code}")));
        // Existing runtime-read resolution is portable across the requesting checkouts.
        let logical = Ask { workspace: ask.workspace.clone(), root: ask.workspace.clone(),
                            krate: "generator".into(), name: ask.target.clone(), args: vec![] };
        let mut hit = self.lookup(&key, &logical)?;
        if hit.is_none() {
            lease = Some(hsm_run_slots::acquire(&format!("generator:{}", ask.target), lease, false)?);
        }
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
            if leader { flight = Some(f); }
            else {
                let mut done = f.done.lock().unwrap();
                while !*done { done = f.landed.wait(done).unwrap(); }
                drop(done);
                hit = self.lookup(&key, &logical)?;
            }
        }
        let landing = Landing { builder: self, key: &key, flight };
        let was_kept = hit.is_some();
        let scratch = self.dir.join("tmp").join(format!("{}-{}", std::process::id(), self.serial()));
        fs::create_dir_all(&scratch)?;
        let result = (|| {
            let recipe_path = scratch.join("recipe.json");
            fs::write(&recipe_path, serde_json::to_vec(&recipe)?)?;
            let (kept, kept_now) = match hit {
                Some(kept) => (kept, false),
                None => {
                    let mut command = Self::generator_command(&ask.workspace, &python, "execute");
                    command.arg(&recipe_path).arg(&scratch).arg(socket);
                    lease.as_ref().unwrap().apply(&mut command)?;
                    // This Python process synchronously asks this same engine to run Rust.
                    // It owns the host lease, but no outer memory/compiler ticket that its
                    // admitted inner Cargo/program would have to wait for.
                    let done = finish(command)?;
                    ensure!(done.ok, "generator {} exited {}:\n{}", ask.target, done.code,
                            String::from_utf8_lossy(&done.stderr));
                    self.measured(&format!("generator {}", ask.target), done.peak);
                    let receipt: Value = serde_json::from_slice(&fs::read(scratch.join("receipt.json"))?)?;
                    let reads = serde_json::from_value(receipt["external_reads"].clone())?;
                    let sources = recipe["inputs"].as_array().context("generator inputs")?.iter()
                        .map(|row| row["path"].as_str().map(str::to_owned).context("generator input path"))
                        .collect::<Result<Vec<_>>>()?;
                    let kept = Kept { reads, files: self.ingest(&scratch.join("out"))?,
                        stdout: String::from_utf8(done.stdout)?, stderr: String::from_utf8_lossy(&done.stderr).into_owned(),
                        seconds: done.seconds, peak: done.peak, code: code.clone(), portable: key.clone(),
                        sources, action: Some(receipt.clone()) };
                    let keepable = receipt["keepable"] == true;
                    if keepable { self.keep(&key, &kept)?; }
                    (kept, keepable)
                }
            };
            fs::write(scratch.join("placement.json"), serde_json::to_vec(&json!({"recipe":recipe,"files":kept.files}))?)?;
            let mut command = Self::generator_command(&ask.workspace, &python, "place");
            command.arg(scratch.join("placement.json")).arg(self.dir.join("blobs")).arg(&output);
            let placed = finish(command)?;
            ensure!(placed.ok, "generator carry failed:\n{}", String::from_utf8_lossy(&placed.stderr));
            let rewritten: BTreeSet<&str> = recipe["rewritten"].as_array().context("rewritten outputs")?
                .iter().filter_map(Value::as_str).collect();
            self.place(&kept.files.iter().filter(|(path, _)| !rewritten.contains(path.as_str()))
                       .cloned().collect::<Vec<_>>(), &output)?;
            Ok(json!({"target":ask.target,"output":output,"hit":was_kept,"kept":was_kept || kept_now,
                "key":key,"code":code,"recipe":recipe,"reads":kept.reads,"files":kept.files,
                "receipt":kept.action,"stdout":kept.stdout,"stderr":kept.stderr,
                "program_seconds":kept.seconds,"peak_bytes":kept.peak,"seconds":started.elapsed().as_secs_f64()}))
        })();
        let _ = fs::remove_dir_all(&scratch);
        drop(landing);
        result
    }

    /// Each argument: the one directory is where the files go, a file is read by its bytes, and
    /// anything else is passed as it is.
    fn classify(&self, ask: &Ask) -> Result<Vec<Arg>> {
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
        let bytes = match fs::read(path) {
            Ok(b) => b,
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => return Ok(None),
            Err(e) => return Err(e).with_context(|| format!("reading {}", path.display())),
        };
        let digest = format!("{:x}", Sha256::digest(&bytes));
        if stamp(path) == Some(before) {
            self.hashes
                .lock()
                .unwrap()
                .insert(path.to_path_buf(), (before, digest.clone()));
        }
        Ok(Some(digest))
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
        if let Some(sources) = self.sources(&ask.workspace, &ask.krate, &ask.name) {
            if let Some(code) = self.code(&ask.workspace, &ask.krate, &ask.name, &sources, toolchain)? {
                if let Some(path) = self.kept_program(ask, &code, &sources) {
                    return Ok(Built { path, code, sources, compiled: false, keepable: true });
                }
            }
        }
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
        let sources = self
            .sources(&ask.workspace, &ask.krate, &ask.name)
            .ok_or_else(|| anyhow!("cargo wrote no dep-info for {}", ask.name))?;
        let code = self
            .code(&ask.workspace, &ask.krate, &ask.name, &sources, toolchain)?
            .ok_or_else(|| anyhow!("a source of {} went away while it built", ask.name))?;
        let path = release.join(&ask.name);
        // A source written while cargo ran may or may not be what rustc read, so that program
        // runs, and neither it nor its run is kept under a code it may not be.
        if sources.iter().any(|s| changed_since(&ask.workspace.join(s), began)) {
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
            let Some(digest) = self.sha(&workspace.join(source))? else {
                return Ok(None);
            };
            h.update(format!("{source}\0{digest}\n"));
        }
        let portable = format!("{:x}", h.finalize());
        let native = format!("{:x}", Sha256::digest(format!("{toolchain}\n{portable}")));
        Ok(Some(Code { native, portable }))
    }

    /// The kept run for `key` whose reads still hold, if there is one.
    fn lookup(&self, key: &str, ask: &Ask) -> Result<Option<Kept>> {
        let path = self.dir.join("runs").join(format!("{key}.json"));
        let Ok(bytes) = fs::read(&path) else {
            return Ok(None);
        };
        let kept: Vec<Kept> = serde_json::from_slice(&bytes).unwrap_or_default();
        'each: for k in kept {
            for (base, file, digest) in &k.reads {
                if self.sha(&resolve(base, file, ask))?.as_deref() != Some(digest.as_str()) {
                    continue 'each;
                }
            }
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
                .env("HOME", home())
                .env("PATH", "/usr/bin:/bin")
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
            let (read, storable) = match fs::read_to_string(&reads) {
                Ok(text) => (self.read_list(&text, ask)?, true),
                Err(_) => (vec![], false),
            };
            Ok((
                Kept {
                    reads: read,
                    files: self.ingest(&out)?,
                    stdout: String::from_utf8(done.stdout)?,
                    stderr: String::from_utf8_lossy(&done.stderr).into_owned(),
                    seconds: done.seconds,
                    peak: done.peak,
                    code: code.native.clone(),
                    portable: primary(&code.portable, args),
                    sources: sources.to_vec(),
                    action: None,
                },
                storable,
            ))
        })();
        let _ = fs::remove_dir_all(&scratch);
        result
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
    fn place(&self, files: &[(String, String)], out: &Path) -> Result<()> {
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

    /// Runs, least recently used first, go until what the rest hold fits in `cap` bytes; then
    /// the blobs and programs no remaining run names.
    pub fn prune(&self, cap: u64) -> Result<()> {
        let mut runs: Vec<(SystemTime, PathBuf, Vec<Kept>)> = vec![];
        for entry in fs::read_dir(self.dir.join("runs"))?.flatten() {
            let Ok(bytes) = fs::read(entry.path()) else { continue };
            let kept = serde_json::from_slice(&bytes).unwrap_or_default();
            let used = entry.metadata().and_then(|m| m.modified()).unwrap_or(SystemTime::UNIX_EPOCH);
            runs.push((used, entry.path(), kept));
        }
        runs.sort_by(|a, b| b.0.cmp(&a.0));
        let size = |p: &Path| fs::metadata(p).map(|m| m.len()).unwrap_or(0);
        let (mut held, mut blobs, mut codes) = (0u64, BTreeSet::new(), BTreeSet::new());
        for (_, path, kept) in &runs {
            let mut cost = 0;
            for k in kept {
                for (_, d) in &k.files {
                    if !blobs.contains(d) {
                        cost += size(&self.dir.join("blobs").join(d));
                    }
                }
            }
            if held + cost > cap {
                let _ = fs::remove_file(path);
                continue;
            }
            held += cost;
            for k in kept {
                blobs.extend(k.files.iter().map(|(_, d)| d.clone()));
                codes.insert(k.code.clone());
            }
        }
        for entry in fs::read_dir(self.dir.join("blobs"))?.flatten() {
            if !blobs.contains(&entry.file_name().to_string_lossy().into_owned()) {
                let _ = fs::remove_file(entry.path());
            }
        }
        for entry in fs::read_dir(self.dir.join("programs"))?.flatten() {
            let name = entry.file_name().to_string_lossy().into_owned();
            if entry.path().is_dir() && !codes.contains(&name) {
                let _ = fs::remove_dir_all(entry.path());
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

    pub fn generate(self, ask: Generate, socket: &Path, lease: Option<Lease>) -> Result<Value> {
        self.0.generate(ask, socket, lease)
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
