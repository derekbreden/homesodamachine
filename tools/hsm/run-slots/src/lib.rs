//! Host-wide heavy-run leases coordinate native commands and inherited engine work.
//! Descriptors carry BSD flock ownership; environment text alone is not admission.
pub mod ipc;
#[cfg(feature = "native-runtime")]
pub mod runtime;

use anyhow::{Context, Result, bail, ensure};
use command_fds::CommandFdExt;
use fs2::FileExt;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::{
    env,
    fs::{self, File, OpenOptions},
    io::{Read, Write},
    os::fd::{AsFd, AsRawFd, BorrowedFd, FromRawFd, OwnedFd},
    os::unix::fs::{MetadataExt, OpenOptionsExt, PermissionsExt},
    os::unix::net::UnixStream,
    path::{Path, PathBuf},
    process::Command,
    sync::{Mutex, OnceLock},
    thread,
    time::{Duration, SystemTime, UNIX_EPOCH},
};

pub const RUN_ENV: &str = "HSM_RUN_LEASE";
pub const CAD_ENV: &str = "HSM_CAD_LEASE";
pub const COMPILER_ENV: &str = "HSM_COMPILER_LEASE";
pub const BROKER_ENV: &str = "HSM_RUN_BROKER";
pub const PROFILE_ENV: &str = "HSM_RUN_PROFILE";

#[derive(Deserialize)]
struct Defaults {
    slots: usize,
    stagger_seconds: f64,
    critical_pressure_level: i32,
    max_swap_bytes: u64,
}

fn defaults() -> &'static Defaults {
    static VALUE: OnceLock<Defaults> = OnceLock::new();
    VALUE.get_or_init(|| {
        serde_json::from_str(include_str!("../../run-slots.defaults.json")).expect("run-slot defaults")
    })
}

pub fn capacity() -> usize {
    defaults().slots
}

pub fn directory() -> Result<PathBuf> {
    // geteuid takes no arguments and reads no process memory.
    let uid = unsafe { libc::geteuid() };
    let root = PathBuf::from(format!("/tmp/hsm-{uid}/heavy"));
    fs::create_dir_all(&root)?;
    fs::set_permissions(&root, fs::Permissions::from_mode(0o700))?;
    Ok(root)
}

fn lock_path(slot: Option<usize>) -> Result<PathBuf> {
    Ok(directory()?.join(slot.map_or_else(|| "cad.lock".to_owned(), |i| format!("slot.{i}.lock"))))
}

fn auxiliary_path(kind: &str) -> Result<PathBuf> {
    Ok(directory()?.join(format!("{kind}.lock")))
}

pub fn count() -> Result<usize> {
    let path = directory()?.join("count");
    let count = match fs::read_to_string(&path) {
        Ok(value) => value.trim().parse().with_context(|| format!("read {}", path.display()))?,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => capacity(),
        Err(e) => return Err(e.into()),
    };
    ensure!((1..=capacity()).contains(&count), "{} must hold 1 through {}", path.display(), capacity());
    Ok(count)
}

/// System memory controls only new roots. Existing leases always remain usable.
pub fn machine_ready() -> Result<bool> {
    #[cfg(target_os = "macos")]
    {
        let mut level: libc::c_int = 0;
        let mut size = std::mem::size_of_val(&level);
        // Both names are static NUL-terminated strings; outputs and sizes are owned here.
        let pressure = unsafe {
            libc::sysctlbyname(
                c"kern.memorystatus_vm_pressure_level".as_ptr(),
                (&mut level as *mut libc::c_int).cast(),
                &mut size,
                std::ptr::null_mut(),
                0,
            )
        };
        let mut swap: libc::xsw_usage = unsafe { std::mem::zeroed() };
        let mut size = std::mem::size_of_val(&swap);
        let usage = unsafe {
            libc::sysctlbyname(
                c"vm.swapusage".as_ptr(),
                (&mut swap as *mut libc::xsw_usage).cast(),
                &mut size,
                std::ptr::null_mut(),
                0,
            )
        };
        return Ok(!(pressure == 0 && level >= defaults().critical_pressure_level
            || usage == 0 && swap.xsu_used > defaults().max_swap_bytes));
    }
    #[cfg(not(target_os = "macos"))]
    Ok(true)
}

fn open(path: &Path) -> Result<File> {
    Ok(OpenOptions::new().create(true).truncate(false).read(true).write(true).mode(0o600).open(path)?)
}

fn token() -> Result<String> {
    let mut bytes = [0u8; 16];
    File::open("/dev/urandom")?.read_exact(&mut bytes)?;
    Ok(bytes.iter().map(|b| format!("{b:02x}")).collect())
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Slot {
    pub slot: usize,
    pub token: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Cad {
    pub token: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct WireLease {
    pub v: u8,
    pub slots: Vec<Slot>,
    pub cad: Option<Cad>,
    pub compiler: Option<Cad>,
    pub profile: Option<String>,
}

#[derive(Deserialize, Serialize)]
struct Entry {
    fd: i32,
    slot: Option<usize>,
    token: String,
}
#[derive(Deserialize)]
struct RunEnv {
    v: u8,
    fds: Vec<Entry>,
}
#[derive(Deserialize)]
struct CadEnv {
    v: u8,
    fd: i32,
    token: String,
}

struct Held {
    file: File,
    slot: Option<usize>,
    token: String,
}

/// Close-only: an explicitly unlocked flock would also release surviving children's lease.
pub struct Lease {
    held: Vec<Held>,
    cad: Option<Held>,
    compiler: Option<Held>,
    pub profile: String,
}

fn read_token(file: &File) -> Result<Value> {
    use std::os::unix::fs::FileExt;
    let mut bytes = [0u8; 16384];
    let n = file.read_at(&mut bytes, 0)?;
    Ok(serde_json::from_slice(&bytes[..n])?)
}

fn validate(file: File, slot: Option<usize>, token: String, kind: &str) -> Result<Held> {
    ensure!(slot.is_none_or(|i| i < capacity()), "invalid run-slot index");
    let path = if slot.is_some() { lock_path(slot)? } else { auxiliary_path(kind)? };
    let (held, named) = (file.metadata()?, fs::metadata(&path)?);
    ensure!(
        held.is_file() && held.dev() == named.dev() && held.ino() == named.ino(),
        "lease descriptor names another file"
    );
    let probe = OpenOptions::new().read(true).write(true).open(&path)?;
    match probe.try_lock_exclusive() {
        Ok(()) => bail!("descriptor is not a held lease"),
        Err(e) if e.kind() == std::io::ErrorKind::WouldBlock || e.raw_os_error() == Some(libc::EACCES) => (),
        Err(e) => return Err(e.into()),
    }
    file.try_lock_exclusive().context("descriptor does not share the held open-file description")?;
    let record = read_token(&file)?;
    ensure!(record["token"] == token && record["kind"] == kind, "lease token or kind differs");
    Ok(Held { file, slot, token })
}

fn duplicate_raw(fd: i32) -> Result<File> {
    ensure!(fd >= 3, "lease descriptor is not an auxiliary descriptor");
    // fcntl accepts any integer descriptor and reports EBADF for an invalid one. A successful
    // F_DUPFD_CLOEXEC returns a fresh descriptor we alone own, preserving the flock's OFD.
    let fresh = unsafe { libc::fcntl(fd, libc::F_DUPFD_CLOEXEC, 3) };
    if fresh < 0 {
        return Err(std::io::Error::last_os_error().into());
    }
    Ok(unsafe { File::from_raw_fd(fresh) })
}

fn cloexec(fd: i32) -> Result<()> {
    // F_GETFD/F_SETFD validate the descriptor themselves; flags are local to this process's FD.
    let flags = unsafe { libc::fcntl(fd, libc::F_GETFD) };
    if flags < 0 || unsafe { libc::fcntl(fd, libc::F_SETFD, flags | libc::FD_CLOEXEC) } < 0 {
        return Err(std::io::Error::last_os_error().into());
    }
    Ok(())
}

impl Lease {
    pub fn from_wire(wire: WireLease, fds: Vec<OwnedFd>) -> Result<Self> {
        ensure!(
            wire.v == 1
                && fds.len()
                    == wire.slots.len()
                        + usize::from(wire.cad.is_some())
                        + usize::from(wire.compiler.is_some()),
            "lease ancillary count/version differs"
        );
        let mut fds = fds.into_iter();
        let mut held = Vec::new();
        for entry in wire.slots {
            ensure!(!held.iter().any(|h: &Held| h.slot == Some(entry.slot)), "duplicate run slot");
            held.push(validate(File::from(fds.next().unwrap()), Some(entry.slot), entry.token, "run")?);
        }
        ensure!(held.windows(2).all(|p| p[0].token == p[1].token), "one run has different slot tokens");
        let cad = wire
            .cad
            .map(|entry| validate(File::from(fds.next().unwrap()), None, entry.token, "cad"))
            .transpose()?;
        let compiler = wire
            .compiler
            .map(|entry| validate(File::from(fds.next().unwrap()), None, entry.token, "compiler"))
            .transpose()?;
        ensure!(!held.is_empty(), "an auxiliary lease has no heavy-run lease");
        Ok(Self { held, cad, compiler, profile: wire.profile.unwrap_or_default() })
    }

    pub fn wire(&self) -> WireLease {
        WireLease {
            v: 1,
            slots: self.held.iter().map(|h| Slot { slot: h.slot.unwrap(), token: h.token.clone() }).collect(),
            cad: self.cad.as_ref().map(|h| Cad { token: h.token.clone() }),
            compiler: self.compiler.as_ref().map(|h| Cad { token: h.token.clone() }),
            profile: Some(self.profile.clone()),
        }
    }

    pub fn descriptors(&self) -> Vec<BorrowedFd<'_>> {
        self.held.iter().chain(self.cad.iter()).chain(self.compiler.iter()).map(|h| h.file.as_fd()).collect()
    }

    pub fn token(&self) -> Option<&str> {
        self.held.first().map(|h| h.token.as_str())
    }
    pub fn slots(&self) -> usize {
        self.held.len()
    }

    pub fn ensure_timing(&self, timing: bool) -> Result<()> {
        ensure!(
            !timing || self.slots() == capacity(),
            "request timing at the root before acquiring a partial run lease"
        );
        Ok(())
    }

    /// Compiler work shares an existing parent's compiler lease, or takes the host compiler
    /// lock before any target or memory mutex. The returned context can drop after Cargo ends.
    pub fn compiler(&self) -> Result<Self> {
        let duplicate = |h: &Held| -> Result<Held> {
            Ok(Held { file: h.file.try_clone()?, slot: h.slot, token: h.token.clone() })
        };
        let mut lease = Self {
            held: self.held.iter().map(duplicate).collect::<Result<_>>()?,
            cad: self.cad.as_ref().map(duplicate).transpose()?,
            compiler: self.compiler.as_ref().map(duplicate).transpose()?,
            profile: self.profile.clone(),
        };
        if lease.compiler.is_none() {
            let mut file = open(&auxiliary_path("compiler")?)?;
            file.lock_exclusive()?;
            let token = token()?;
            file.set_len(0)?;
            file.write_all(
                format!("{}\n", json!({"v":1,"kind":"compiler","token":token,"pid":std::process::id()}))
                    .as_bytes(),
            )?;
            lease.compiler = Some(Held { file, slot: None, token });
        }
        Ok(lease)
    }

    pub fn apply(&self, command: &mut Command) -> Result<()> {
        let mut files = Vec::new();
        let mut entries = Vec::new();
        for held in &self.held {
            let fd: OwnedFd = held.file.try_clone()?.into();
            entries.push(json!({"fd":fd.as_raw_fd(),"slot":held.slot.unwrap(),"token":held.token}));
            files.push(fd);
        }
        command.env(RUN_ENV, json!({"v":1,"fds":entries}).to_string()).env(PROFILE_ENV, &self.profile);
        if let Some(held) = &self.cad {
            let fd: OwnedFd = held.file.try_clone()?.into();
            command.env(CAD_ENV, json!({"v":1,"fd":fd.as_raw_fd(),"token":held.token}).to_string());
            command.env("HSM_NO_BUILD_LOCK", "1");
            files.push(fd);
        } else {
            command.env_remove(CAD_ENV).env_remove("HSM_NO_BUILD_LOCK");
        }
        if let Some(held) = &self.compiler {
            let fd: OwnedFd = held.file.try_clone()?.into();
            command.env(COMPILER_ENV, json!({"v":1,"fd":fd.as_raw_fd(),"token":held.token}).to_string());
            files.push(fd);
        } else {
            command.env_remove(COMPILER_ENV);
        }
        command.preserved_fds(files);
        Ok(())
    }
}

fn local_inherited() -> Result<Option<Lease>> {
    let mut held = Vec::new();
    if let Some(text) = env::var_os(RUN_ENV) {
        let run: RunEnv = serde_json::from_str(&text.to_string_lossy())?;
        ensure!(run.v == 1 && !run.fds.is_empty(), "invalid inherited run lease");
        for entry in run.fds {
            ensure!(
                entry.slot.is_some() && !held.iter().any(|h: &Held| h.slot == entry.slot),
                "invalid inherited slot"
            );
            let fd = duplicate_raw(entry.fd)?;
            held.push(validate(fd, entry.slot, entry.token, "run")?);
            cloexec(entry.fd)?;
        }
    }
    let cad = if let Some(text) = env::var_os(CAD_ENV) {
        let entry: CadEnv = serde_json::from_str(&text.to_string_lossy())?;
        ensure!(entry.v == 1, "invalid inherited CAD lease");
        let held = validate(duplicate_raw(entry.fd)?, None, entry.token, "cad")?;
        cloexec(entry.fd)?;
        Some(held)
    } else {
        None
    };
    let compiler = if let Some(text) = env::var_os(COMPILER_ENV) {
        let entry: CadEnv = serde_json::from_str(&text.to_string_lossy())?;
        ensure!(entry.v == 1, "invalid inherited compiler lease");
        let held = validate(duplicate_raw(entry.fd)?, None, entry.token, "compiler")?;
        cloexec(entry.fd)?;
        Some(held)
    } else {
        None
    };
    if !held.is_empty() {
        ensure!(held.windows(2).all(|p| p[0].token == p[1].token), "one inherited run has different tokens");
        return Ok(Some(Lease { held, cad, compiler, profile: env::var(PROFILE_ENV).unwrap_or_default() }));
    }
    ensure!(cad.is_none() && compiler.is_none(), "auxiliary lease has no heavy-run lease");
    Ok(None)
}

fn broker_inherited() -> Result<Option<Lease>> {
    if let Some(text) = env::var_os(BROKER_ENV) {
        let config: Value = serde_json::from_str(&text.to_string_lossy())?;
        let path = Path::new(config["path"].as_str().context("broker has no path")?);
        ensure!(
            path.parent().context("broker path has no parent")?.canonicalize()?
                == directory()?.canonicalize()?,
            "broker is outside the run directory"
        );
        let owner: Value = serde_json::from_slice(&fs::read(path.with_extension("json"))?)?;
        let stream = UnixStream::connect(path)?;
        stream.set_read_timeout(Some(Duration::from_secs(1)))?;
        ipc::send(&stream, &json!({"v":1,"token":owner["token"]}), &[])?;
        let (reply, fds) = ipc::receive(&stream, 16384, Duration::from_secs(1))?;
        ensure!(reply["ok"] == true, "run broker refused this logical parent");
        return Ok(Some(Lease::from_wire(serde_json::from_value(reply["_lease"].clone())?, fds)?));
    }
    Ok(None)
}

/// Numeric FD metadata can outlive the descriptors across default-close-fds launchers. Only a
/// live broker returning independently validated rights can recover that parent's admission.
pub fn inherited() -> Result<Option<Lease>> {
    match local_inherited() {
        Ok(Some(lease)) => Ok(Some(lease)),
        Ok(None) => broker_inherited(),
        Err(local_error) => {
            // A partial local context may still contain real inherited FDs after the first
            // stale entry. Mark those before a detached child can inherit them as well.
            for fd in validated_originals() {
                cloexec(fd)?;
            }
            match broker_inherited() {
                Ok(Some(lease)) => Ok(Some(lease)),
                Ok(None) => Err(local_error),
                Err(error) => Err(error.context(format!("local run lease unavailable: {local_error:#}"))),
            }
        }
    }
}

/// Inspect originals before broker adoption can allocate a new FD at a stale metadata number.
/// Each temporary validation duplicate is dropped before examining the next number.
fn validated_originals() -> Vec<i32> {
    let mut entries = Vec::new();
    if let Some(text) = env::var_os(RUN_ENV) {
        if let Ok(run) = serde_json::from_str::<RunEnv>(&text.to_string_lossy()) {
            entries.extend(run.fds.into_iter().map(|entry| (entry, "run")));
        }
    }
    for (name, kind) in [(CAD_ENV, "cad"), (COMPILER_ENV, "compiler")] {
        if let Some(text) = env::var_os(name) {
            if let Ok(entry) = serde_json::from_str::<CadEnv>(&text.to_string_lossy()) {
                entries.push((Entry { fd: entry.fd, slot: None, token: entry.token }, kind));
            }
        }
    }
    let mut originals = std::collections::BTreeSet::new();
    for (entry, kind) in entries {
        if kind == "run" && entry.slot.is_none() {
            continue;
        }
        if duplicate_raw(entry.fd).and_then(|file| validate(file, entry.slot, entry.token, kind)).is_ok() {
            originals.insert(entry.fd);
        }
    }
    originals.into_iter().collect()
}

pub fn acquire(key: &str, incoming: Option<Lease>, timing: bool) -> Result<Lease> {
    if let Some(mut lease) = incoming {
        if lease.profile.is_empty() {
            lease.profile = key.to_owned();
        }
        lease.ensure_timing(timing)?;
        return Ok(lease);
    }
    let token = token()?;
    let mut waiting = false;
    loop {
        if !machine_ready()? {
            if !waiting {
                eprintln!("[run] waiting for machine memory pressure");
                waiting = true;
            }
            thread::sleep(Duration::from_millis(250));
            continue;
        }
        let admission = open(&directory()?.join("admission.lock"))?;
        admission.lock_exclusive()?;
        let mut held = Vec::new();
        let mut active = std::collections::BTreeSet::new();
        let mut newest_busy_start = 0;
        for slot in 0..capacity() {
            let file = open(&lock_path(Some(slot))?)?;
            match file.try_lock_exclusive() {
                Ok(()) => held.push(Held { file, slot: Some(slot), token: token.clone() }),
                Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                    let record = read_token(&file).unwrap_or_else(|_| json!({}));
                    active.insert(
                        record["token"].as_str().map(str::to_owned).unwrap_or_else(|| format!("slot:{slot}")),
                    );
                    newest_busy_start = newest_busy_start.max(record["started_unix_ms"].as_u64().unwrap_or(0));
                }
                Err(e) => return Err(e.into()),
            }
        }
        let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_millis() as u64;
        let stamp = directory()?.join("admission.json");
        let spaced = active.is_empty()
            || now.saturating_sub(newest_busy_start) as f64
                >= defaults().stagger_seconds * 1000.0;
        let available = if timing {
            active.is_empty() && held.len() == capacity()
        } else {
            active.len() < count()? && !held.is_empty()
        };
        if spaced && available {
            if !timing {
                held.truncate(1);
            }
            for entry in &mut held {
                entry.file.set_len(0)?;
                entry.file.write_all(format!("{}\n", json!({"v":1,"kind":"run","token":token,"pid":std::process::id(),"key":key,"slot":entry.slot,"started_unix_ms":now})).as_bytes())?;
            }
            fs::write(&stamp, format!("{}\n", json!({"v":1,"last_start_unix_ms":now})))?;
            return Ok(Lease { held, cad: None, compiler: None, profile: key.to_owned() });
        }
        drop(held);
        drop(admission);
        if !waiting {
            eprintln!("[run] waiting for heavy-run admission");
            waiting = true;
        }
        thread::sleep(Duration::from_millis(25));
    }
}

/// Call at a persistent service's main entry, before it starts threads. It must not retain a
/// caller's lease for its own lifetime, nor pass it into a detached service child.
pub fn clear_inherited_for_service() -> Result<()> {
    let originals = validated_originals();
    let validated = inherited()?;
    for fd in originals {
        // These are validated inherited descriptors at process entry, before any Rust object
        // owns their original FD. Closing here leaves parent and validated duplicate OFDs alive.
        unsafe {
            libc::close(fd);
        }
    }
    drop(validated);
    // No service threads exist yet; no concurrent environment readers/writers exist.
    for name in [RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, PROFILE_ENV, "HSM_NO_BUILD_LOCK"] {
        unsafe {
            env::remove_var(name);
        }
    }
    Ok(())
}

pub fn detach(command: &mut Command) {
    for name in [RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, PROFILE_ENV, "HSM_NO_BUILD_LOCK"] {
        command.env_remove(name);
    }
}

static PROCESS: OnceLock<Lease> = OnceLock::new();
static PROCESS_INIT: Mutex<()> = Mutex::new(());

/// A direct native program retains its lease until process exit; the OS releases its FDs.
pub fn process_enter(key: &str) -> Result<()> {
    let _initializing = PROCESS_INIT.lock().unwrap();
    if PROCESS.get().is_some() {
        return Ok(());
    }
    let lease = acquire(key, inherited()?, env::var("HSM_RUN_TIMING").is_ok_and(|v| v == "1"))?;
    let _ = PROCESS.set(lease);
    Ok(())
}

pub fn native_key() -> String {
    let name = env::current_exe()
        .ok()
        .and_then(|p| p.file_name().map(|s| s.to_string_lossy().into_owned()))
        .unwrap_or_else(|| "kernel-part".to_owned());
    format!("native:{name}")
}

pub fn source_digest() -> String {
    let mut hash = Sha256::new();
    for text in [
        include_str!("lib.rs"),
        include_str!("ipc.rs"),
        include_str!("runtime.rs"),
        include_str!("runtime/slots.rs"),
        include_str!("runtime/cad.rs"),
        include_str!("runtime/runner.rs"),
        include_str!("runtime/install.rs"),
        include_str!("main.rs"),
        include_str!("../Cargo.toml"),
        include_str!("../../run-slots.defaults.json"),
    ] {
        hash.update(text);
    }
    format!("{:x}", hash.finalize())
}
