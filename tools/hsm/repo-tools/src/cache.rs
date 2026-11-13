//! Cache cleanup deletes what Git can rebuild once nothing has used it for days, and keeps what builds still use.
use anyhow::{Context, Result, ensure};
use regex::Regex;
use std::{
    collections::{BTreeMap, BTreeSet, HashMap},
    ffi::CString,
    io::Read,
    os::unix::fs::MetadataExt,
    path::{Path, PathBuf},
    process::Command,
    time::{Duration, UNIX_EPOCH},
};

/// Days a file Git can rebuild stays after its last use.
const DAYS: f64 = 2.;
/// Days a cargo unit stays without a build reading its fingerprint.
const UNIT_DAYS: f64 = 1.;
/// A profile's directories whose entries carry their unit's hash.
const UNIT_DIRS: &[&str] = &["deps", "build", "examples", ".fingerprint"];
/// The lock files cargo holds in a profile directory through a build.
const LOCKS: &[&str] = &[".cargo-lock", ".cargo-build-lock"];
/// Scratch folders whose children age independently, each by its own newest write.
const CONTAINERS: &[&str] = &[
    "runs",
    "prints",
    "printer-control",
    "printer-control/imports",
    "meshes/publication",
];
/// Memo caches: an entry stays while a tracked file names its `.cache/` path.
const MEMOS: &[&str] = &["meshes", "realized"];
/// Mesh objects, kept while something in the tree names them.
const OBJECTS: &str = "meshes/scene-assets";
/// Enclosure stages, which bound their own storage; the cleanup takes the ones no build reused.
const STAGES: &str = "realized/rust-stages";
/// The last use the cleanup has seen of each unit it judges by use, so a use seen in one pass
/// still counts in the next.
const LEDGER: &str = "cache-gc-uses.json";
const KEEP: &[&str] = &["runtimes", "printer-control/venv", LEDGER];

pub fn newest_write(path: &Path) -> Result<(f64, u64)> {
    let metadata = std::fs::symlink_metadata(path)?;
    if metadata.file_type().is_symlink() || !metadata.is_dir() {
        return Ok((
            if path.file_name().is_some_and(|n| n == ".DS_Store") {
                0.
            } else {
                modified(&metadata)
            },
            metadata.len(),
        ));
    }
    let (mut newest, mut size) = (0_f64, 0_u64);
    let mut stack = vec![path.to_path_buf()];
    while let Some(dir) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(dir) else {
            continue;
        };
        for entry in entries.flatten() {
            let child = entry.path();
            let Ok(meta) = std::fs::symlink_metadata(&child) else {
                continue;
            };
            if meta.is_dir() {
                stack.push(child)
            } else if meta.file_type().is_symlink() && child.is_dir() {
            } else {
                size += meta.len();
                if entry.file_name() != ".DS_Store" {
                    newest = newest.max(modified(&meta));
                }
            }
        }
    }
    Ok((newest, size))
}
fn modified(metadata: &std::fs::Metadata) -> f64 {
    metadata
        .modified()
        .ok()
        .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
        .map_or(0., |d| d.as_secs_f64())
}
fn touched(metadata: &std::fs::Metadata) -> f64 {
    metadata
        .accessed()
        .ok()
        .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
        .map_or(0., |d| d.as_secs_f64())
        .max(modified(metadata))
}

/// Sets the access time of each file in `dir` just before its write time. On macOS a read moves a
/// file's access time only while it is older than the file's last write, so this lets the next
/// read show.
fn arm(dir: &Path) {
    for entry in std::fs::read_dir(dir).into_iter().flatten().flatten() {
        let Ok(meta) = entry.metadata() else {
            continue;
        };
        let (Ok(read), Ok(written)) = (meta.accessed(), meta.modified()) else {
            continue;
        };
        if !meta.is_file() || read < written {
            continue;
        }
        let before = written
            .checked_sub(Duration::from_secs(1))
            .unwrap_or(UNIX_EPOCH);
        if let Ok(file) = std::fs::File::open(entry.path()) {
            let _ = file.set_times(std::fs::FileTimes::new().set_accessed(before));
        }
    }
}

/// When the cleanup last saw each unit it judges by use: a build reading it, something in the
/// tree naming it, or a program running it.
pub struct Ledger {
    path: PathBuf,
    uses: BTreeMap<String, f64>,
}

impl Ledger {
    pub fn open(path: PathBuf) -> Self {
        let uses = std::fs::read(&path)
            .ok()
            .and_then(|bytes| serde_json::from_slice(&bytes).ok())
            .unwrap_or_default();
        Self { path, uses }
    }
    fn get(&self, unit: &Path) -> Option<f64> {
        self.uses.get(unit.to_string_lossy().as_ref()).copied()
    }
    fn set(&mut self, unit: &Path, at: f64) {
        self.uses.insert(unit.to_string_lossy().into_owned(), at);
    }
    fn forget(&mut self, unit: &Path) {
        self.uses.remove(unit.to_string_lossy().as_ref());
    }
    /// Writes the ledger, leaving out the units that are gone.
    pub fn save(&mut self) -> Result<()> {
        self.uses
            .retain(|unit, _| std::fs::symlink_metadata(unit).is_ok());
        let temporary = self
            .path
            .with_extension(format!("json.{}", std::process::id()));
        std::fs::write(&temporary, serde_json::to_vec(&self.uses)?)?;
        std::fs::rename(&temporary, &self.path)?;
        Ok(())
    }
}

/// What the checkout names: memo entries by their `.cache/` path in a tracked file, and mesh
/// objects. A kind whose names can't be read stays whole.
#[derive(Default)]
pub struct Names {
    pub memos: Option<BTreeSet<String>>,
    pub objects: Option<BTreeSet<String>>,
}

impl Names {
    pub fn read(root: &Path, cache: &Path) -> Self {
        Self {
            memos: memos(root).ok(),
            objects: objects(root, cache).ok(),
        }
    }
}

/// Each match of `pattern` in the tracked files `paths` select.
fn grep(root: &Path, pattern: &str, paths: &[&str]) -> Result<Vec<String>> {
    let output = Command::new("git")
        .arg("-C")
        .arg(root)
        .args(["grep", "-h", "-o", "-I", "-E", pattern, "--"])
        .args(paths)
        .output()?;
    ensure!(
        output.status.success() || output.status.code() == Some(1),
        "git grep failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    Ok(String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(str::to_owned)
        .collect())
}

/// The memo entries a tracked file names, as `meshes/<entry>` or `realized/<entry>`.
fn memos(root: &Path) -> Result<BTreeSet<String>> {
    Ok(grep(root, r"\.cache/(meshes|realized)/[A-Za-z0-9_.-]+", &[])?
        .into_iter()
        .map(|m| m.trim_start_matches(".cache/").trim_end_matches('.').to_owned())
        .collect())
}

/// The mesh objects named in the tree: by payload headers, tracked JSON and the cache's pointer
/// files, with the objects of every named scene the object cache holds.
fn objects(root: &Path, cache: &Path) -> Result<BTreeSet<String>> {
    let mut named: BTreeSet<String> = grep(root, "[0-9a-f]{64}", &["*.json"])?
        .into_iter()
        .collect();
    let digest = Regex::new("[0-9a-f]{64}")?;
    for entry in std::fs::read_dir(cache)?.flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        if name.ends_with(".json") && name != LEDGER {
            if let Ok(bytes) = std::fs::read(entry.path()) {
                mentions(&digest, &String::from_utf8_lossy(&bytes), &mut named);
            }
        }
    }
    let mut dirs = vec![
        root.to_path_buf(),
        cache.join("realized"),
        cache.join("runs"),
        std::env::temp_dir().join("hsm-changes"),
    ];
    while let Some(dir) = dirs.pop() {
        for entry in std::fs::read_dir(&dir).into_iter().flatten().flatten() {
            let name = entry.file_name().to_string_lossy().into_owned();
            let Ok(kind) = entry.file_type() else {
                continue;
            };
            if kind.is_dir() {
                if !(name.starts_with('.')
                    || name == "target"
                    || name == "node_modules"
                    || name.ends_with("-venv"))
                {
                    dirs.push(entry.path());
                }
            } else if name.ends_with(".mesh") {
                named.extend(assets(&entry.path()));
            }
        }
    }
    let held = cache.join(OBJECTS);
    let mut pending: Vec<String> = named.iter().cloned().collect();
    while let Some(hash) = pending.pop() {
        for asset in assets(&held.join(format!("{hash}.mesh"))) {
            if named.insert(asset.clone()) {
                pending.push(asset);
            }
        }
    }
    Ok(named)
}

/// The mesh objects a payload's header names.
fn assets(path: &Path) -> Vec<String> {
    let Ok(mut file) = std::fs::File::open(path) else {
        return Vec::new();
    };
    let length = file.metadata().map_or(0, |meta| meta.len());
    let mut size = [0; 4];
    if file.read_exact(&mut size).is_err() {
        return Vec::new();
    }
    let size = u32::from_le_bytes(size) as u64;
    if size == 0 || size + 4 > length {
        return Vec::new();
    }
    let mut head = vec![0; size as usize];
    if file.read_exact(&mut head).is_err() {
        return Vec::new();
    }
    let Ok(head) = serde_json::from_slice::<serde_json::Value>(&head) else {
        return Vec::new();
    };
    head["meshes"]
        .as_array()
        .into_iter()
        .flatten()
        .filter_map(|row| row["asset"].as_str())
        .map(str::to_owned)
        .collect()
}

fn mentions(digest: &Regex, text: &str, named: &mut BTreeSet<String>) {
    named.extend(digest.find_iter(text).map(|m| m.as_str().to_owned()));
}

fn is_digest(name: &str) -> bool {
    name.len() == 64
        && name
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

/// The executables of the running programs this user can see.
fn running() -> Vec<PathBuf> {
    #[cfg(target_os = "macos")]
    {
        use std::os::unix::ffi::OsStrExt;
        let mut pids = vec![0 as libc::c_int; 1 << 14];
        let bytes = (pids.len() * std::mem::size_of::<libc::c_int>()) as libc::c_int;
        let count = unsafe { libc::proc_listallpids(pids.as_mut_ptr().cast(), bytes) };
        pids.truncate(count.max(0) as usize);
        pids.into_iter()
            .filter_map(|pid| {
                let mut path = [0_u8; libc::PROC_PIDPATHINFO_MAXSIZE as usize];
                let length =
                    unsafe { libc::proc_pidpath(pid, path.as_mut_ptr().cast(), path.len() as u32) };
                (length > 0).then(|| {
                    PathBuf::from(std::ffi::OsStr::from_bytes(&path[..length as usize]))
                })
            })
            .collect()
    }
    #[cfg(not(target_os = "macos"))]
    {
        std::fs::read_dir("/proc")
            .into_iter()
            .flatten()
            .flatten()
            .filter_map(|entry| std::fs::read_link(entry.path().join("exe")).ok())
            .collect()
    }
}

/// The unit hash in a fingerprint, output or build-script name: `name-<hash>[.ext]`.
fn unit_hash(name: &str) -> Option<&str> {
    let bytes = name.as_bytes();
    name.match_indices('-')
        .map(|(i, _)| i + 1)
        .filter(|&start| {
            bytes.get(start..start + 16).is_some_and(|hash| {
                hash.iter()
                    .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(b))
            }) && bytes.get(start + 16).is_none_or(|&b| b == b'.')
        })
        .last()
        .map(|start| &name[start..start + 16])
}

/// Every cargo profile directory under `target`: each one holding `.fingerprint`.
fn profiles(target: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut stack = vec![(target.to_path_buf(), 0)];
    while let Some((dir, depth)) = stack.pop() {
        if dir.join(".fingerprint").is_dir() {
            out.push(dir);
            continue;
        }
        let Ok(entries) = std::fs::read_dir(&dir) else {
            continue;
        };
        for entry in entries.flatten() {
            if depth < 3 && entry.file_type().is_ok_and(|t| t.is_dir()) {
                stack.push((entry.path(), depth + 1));
            }
        }
    }
    out.sort();
    out
}

/// The newest read or write of a unit's fingerprint files that shows on disk.
fn last_read(unit: &Path) -> f64 {
    let newest = std::fs::read_dir(unit)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|entry| entry.metadata().ok())
        .map(|meta| touched(&meta))
        .fold(0., f64::max);
    if newest > 0. {
        newest
    } else {
        std::fs::symlink_metadata(unit).map_or(0., |meta| modified(&meta))
    }
}

/// The bytes removing `path` frees; a file another hard link still names frees none.
fn freed(path: &Path) -> u64 {
    let mut total = 0;
    let mut stack = vec![path.to_path_buf()];
    while let Some(path) = stack.pop() {
        let Ok(meta) = std::fs::symlink_metadata(&path) else {
            continue;
        };
        if meta.is_dir() {
            stack.extend(
                std::fs::read_dir(&path)
                    .into_iter()
                    .flatten()
                    .flatten()
                    .map(|e| e.path()),
            );
        } else if meta.nlink() == 1 {
            total += meta.blocks() * 512;
        }
    }
    total
}

/// Deletes a file, a link or a directory.
fn remove(path: &Path) -> std::io::Result<()> {
    if std::fs::symlink_metadata(path)?.is_dir() {
        std::fs::remove_dir_all(path)
    } else {
        std::fs::remove_file(path)
    }
}

#[derive(Default, Debug)]
pub struct Sweep {
    pub removed: usize,
    pub kept: usize,
    pub busy: usize,
    pub failed: usize,
    pub bytes: u64,
}

/// Removes the cargo units under `target` that no build has read since `cutoff`, holding each
/// profile's cargo locks and passing over a profile a build holds. A build's read shows on a
/// fingerprint the last pass armed; a unit the ledger has not seen counts as read now. Top-level
/// binaries and dep-info stay.
pub fn sweep(
    target: &Path,
    ledger: &mut Ledger,
    cutoff: f64,
    now: f64,
    apply: bool,
) -> Result<Sweep> {
    let mut sweep = Sweep::default();
    for profile in profiles(target) {
        let locks = LOCKS
            .iter()
            .map(|name| {
                std::fs::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(profile.join(name))
            })
            .collect::<std::io::Result<Vec<_>>>()?;
        if locks.iter().any(|lock| lock.try_lock().is_err()) {
            println!("  in use        {}", profile.display());
            sweep.busy += 1;
            continue;
        }
        let mut read = HashMap::new();
        for entry in std::fs::read_dir(profile.join(".fingerprint"))?.flatten() {
            let name = entry.file_name().to_string_lossy().into_owned();
            if let Some(hash) = unit_hash(&name) {
                let unit = entry.path();
                let seen = last_read(&unit);
                let last = ledger.get(&unit).map_or(now, |known| known.max(seen));
                read.insert(hash.to_owned(), (last, unit));
            }
        }
        let (removed, mut bytes) = (sweep.removed, 0);
        sweep.kept += read.values().filter(|(t, _)| *t >= cutoff).count();
        sweep.removed += read.values().filter(|(t, _)| *t < cutoff).count();
        for dir in UNIT_DIRS {
            let Ok(entries) = std::fs::read_dir(profile.join(dir)) else {
                continue;
            };
            for entry in entries.flatten() {
                let name = entry.file_name().to_string_lossy().into_owned();
                let Some(hash) = unit_hash(&name) else {
                    continue;
                };
                let path = entry.path();
                let when = read.get(hash).map_or_else(
                    || std::fs::symlink_metadata(&path).map_or(f64::MAX, |meta| touched(&meta)),
                    |(t, _)| *t,
                );
                if when >= cutoff {
                    continue;
                }
                let size = freed(&path);
                if apply {
                    if let Err(error) = remove(&path) {
                        println!("  failed        {}: {error}", path.display());
                        sweep.failed += 1;
                        continue;
                    }
                }
                bytes += size;
            }
        }
        for (last, unit) in read.values() {
            if *last < cutoff {
                ledger.forget(unit);
            } else {
                ledger.set(unit, *last);
                if apply {
                    arm(unit);
                }
            }
        }
        println!(
            "  {}  {:9.1} MB  {} unit(s) in {}",
            if apply { "deleted" } else { "would delete" },
            bytes as f64 / 1e6,
            sweep.removed - removed,
            profile.display()
        );
        sweep.bytes += bytes;
    }
    Ok(sweep)
}

fn sorted(dir: &Path) -> Result<Vec<std::fs::DirEntry>> {
    let mut entries: Vec<_> = std::fs::read_dir(dir)?.filter_map(|e| e.ok()).collect();
    entries.sort_by_key(|e| e.file_name());
    Ok(entries)
}

/// The units under `cache` that age by their own newest write: each top-level entry, each child
/// of a container, and each memo entry no tracked file names. With no names read, memo entries stay.
pub fn units(cache: &Path, memos: Option<&BTreeSet<String>>) -> Result<Vec<(String, PathBuf)>> {
    let mut out = Vec::new();
    let mut pending = vec![(String::new(), cache.to_path_buf())];
    while let Some((prefix, dir)) = pending.pop() {
        for entry in sorted(&dir)? {
            let name = entry.file_name().to_string_lossy().into_owned();
            let rel = if prefix.is_empty() {
                name.clone()
            } else {
                format!("{prefix}/{name}")
            };
            if name == ".DS_Store" || KEEP.contains(&rel.as_str()) || rel == OBJECTS || rel == STAGES
            {
                continue;
            }
            let expands = CONTAINERS.contains(&rel.as_str()) || MEMOS.contains(&rel.as_str());
            if expands && entry.file_type().is_ok_and(|t| t.is_dir()) {
                pending.push((rel, entry.path()));
            } else if MEMOS.contains(&prefix.as_str())
                && memos.is_none_or(|named| named.contains(&rel))
            {
                continue;
            } else {
                out.push((rel, entry.path()));
            }
        }
    }
    out.sort();
    Ok(out)
}
fn date(stamp: f64, format: &str) -> String {
    if stamp == 0. {
        return "never".into();
    }
    let stamp = stamp as libc::time_t;
    let mut tm = std::mem::MaybeUninit::uninit();
    let mut output = [0_i8; 64];
    let format = CString::new(format).expect("date format");
    unsafe {
        if libc::localtime_r(&stamp, tm.as_mut_ptr()).is_null() {
            return stamp.to_string();
        };
        let length = libc::strftime(
            output.as_mut_ptr(),
            output.len(),
            format.as_ptr(),
            tm.as_ptr(),
        );
        String::from_utf8_lossy(std::slice::from_raw_parts(
            output.as_ptr().cast::<u8>(),
            length,
        ))
        .into_owned()
    }
}
#[derive(Default, Debug)]
pub struct Summary {
    pub removed: usize,
    pub kept: usize,
    pub failed: usize,
    pub bytes: u64,
}

fn report(summary: &mut Summary, verb: &str, removed: usize, bytes: u64, what: &str, rel: &str) {
    if removed > 0 {
        println!("  {verb}  {:9.1} MB  {removed} {what} in {rel}", bytes as f64 / 1e6);
    }
    summary.removed += removed;
    summary.bytes += bytes;
}

/// Removes what `cache` holds that nothing has used since `days` ago: scratch by its newest write,
/// mesh objects by the last time anything named, wrote or read them, and stages no build reused.
pub fn collect(
    cache: &Path,
    names: &Names,
    ledger: &mut Ledger,
    days: f64,
    apply: bool,
    now: f64,
) -> Result<Summary> {
    ensure!(
        days.is_finite() && days >= 0.,
        "--days needs a finite nonnegative duration"
    );
    let mut summary = Summary::default();
    let cutoff = now - days * 86400.;
    let verb = if apply { "deleted" } else { "would delete" };
    for (rel, path) in units(cache, names.memos.as_ref())? {
        let (newest, size) = newest_write(&path)?;
        if newest >= cutoff {
            summary.kept += 1;
            continue;
        }
        let when = date(newest, "%Y-%m-%d %H:%M");
        if apply {
            if let Err(error) = remove(&path) {
                println!(
                    "  failed        {when}  {:9.1} MB  {rel}: {error}",
                    size as f64 / 1e6
                );
                summary.failed += 1;
                continue;
            }
        }
        println!("  {verb}  {when}  {:9.1} MB  {rel}", size as f64 / 1e6);
        summary.removed += 1;
        summary.bytes += size;
    }
    if let Some(named) = &names.objects {
        let (mut removed, mut bytes) = (0, 0);
        for entry in std::fs::read_dir(cache.join(OBJECTS))
            .into_iter()
            .flatten()
            .flatten()
        {
            let (path, name) = (entry.path(), entry.file_name().to_string_lossy().into_owned());
            let Ok(meta) = std::fs::symlink_metadata(&path) else {
                continue;
            };
            if !meta.is_file() || name == ".DS_Store" {
                continue;
            }
            let last = if name
                .strip_suffix(".mesh")
                .is_some_and(|hash| named.contains(hash))
            {
                now
            } else {
                ledger.get(&path).unwrap_or(0.).max(touched(&meta))
            };
            if last >= cutoff {
                ledger.set(&path, last);
                summary.kept += 1;
                continue;
            }
            let size = freed(&path);
            if apply && std::fs::remove_file(&path).is_err() {
                summary.failed += 1;
                continue;
            }
            ledger.forget(&path);
            removed += 1;
            bytes += size;
        }
        report(&mut summary, verb, removed, bytes, "mesh object(s) nothing names", OBJECTS);
    }
    let (mut removed, mut bytes) = (0, 0);
    for entry in std::fs::read_dir(cache.join(STAGES))
        .into_iter()
        .flatten()
        .flatten()
    {
        let path = entry.path();
        let Ok(meta) = std::fs::symlink_metadata(&path) else {
            continue;
        };
        let (Ok(read), Ok(written)) = (meta.accessed(), meta.modified()) else {
            continue;
        };
        if !meta.is_file() || entry.file_name() == ".DS_Store" {
            continue;
        }
        if modified(&meta) >= cutoff || read >= written {
            summary.kept += 1;
            continue;
        }
        let size = freed(&path);
        if apply && std::fs::remove_file(&path).is_err() {
            summary.failed += 1;
            continue;
        }
        removed += 1;
        bytes += size;
    }
    report(&mut summary, verb, removed, bytes, "stage(s) no build reused", STAGES);
    Ok(summary)
}

/// Removes the builds under `prefix`/lib/hsm that no launcher names and no running program
/// executes, once the last time anything named, ran or installed them is before `cutoff`.
pub fn installed(
    prefix: &Path,
    ledger: &mut Ledger,
    cutoff: f64,
    now: f64,
    apply: bool,
) -> Result<Summary> {
    let mut summary = Summary::default();
    let lib = prefix.join("lib/hsm");
    let digest = Regex::new("[0-9a-f]{64}")?;
    let mut named = BTreeSet::new();
    for entry in std::fs::read_dir(prefix.join("bin"))
        .into_iter()
        .flatten()
        .flatten()
    {
        let path = entry.path();
        let Ok(meta) = std::fs::symlink_metadata(&path) else {
            continue;
        };
        if meta.file_type().is_symlink() {
            if let Ok(to) = std::fs::read_link(&path) {
                mentions(&digest, &to.to_string_lossy(), &mut named);
            }
        } else if meta.is_file() && meta.len() < 1 << 20 {
            if let Ok(bytes) = std::fs::read(&path) {
                mentions(&digest, &String::from_utf8_lossy(&bytes), &mut named);
            }
        }
    }
    for record in ["launcher.json", "runtime.json"] {
        if let Ok(bytes) = std::fs::read(lib.join(record)) {
            mentions(&digest, &String::from_utf8_lossy(&bytes), &mut named);
        }
    }
    for program in running() {
        if program.starts_with(&lib) {
            mentions(&digest, &program.to_string_lossy(), &mut named);
        }
    }
    let (mut removed, mut bytes) = (0, 0);
    for sub in ["", "tools", "runtime", "legacy"] {
        for entry in std::fs::read_dir(lib.join(sub))
            .into_iter()
            .flatten()
            .flatten()
        {
            let name = entry.file_name().to_string_lossy().into_owned();
            if !is_digest(&name) || !entry.file_type().is_ok_and(|t| t.is_dir()) {
                continue;
            }
            let path = entry.path();
            let last = if named.contains(&name) {
                now
            } else {
                ledger
                    .get(&path)
                    .unwrap_or(0.)
                    .max(newest_write(&path).map_or(0., |(t, _)| t))
            };
            if last >= cutoff {
                ledger.set(&path, last);
                summary.kept += 1;
                continue;
            }
            let size = freed(&path);
            if apply {
                if let Err(error) = std::fs::remove_dir_all(&path) {
                    println!("  failed        {}: {error}", path.display());
                    summary.failed += 1;
                    continue;
                }
            }
            ledger.forget(&path);
            removed += 1;
            bytes += size;
        }
    }
    println!(
        "  {}  {:9.1} MB  {removed} build(s) in {}",
        if apply { "deleted" } else { "would delete" },
        bytes as f64 / 1e6,
        lib.display()
    );
    summary.removed = removed;
    summary.bytes = bytes;
    Ok(summary)
}

pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut cache = root.join(".cache");
    let mut target = root.join("tools/hsm/target");
    let mut prefix = std::env::var_os("HOME").map(|home| PathBuf::from(home).join(".local"));
    let mut days = DAYS;
    let mut apply = false;
    let mut args = args.iter();
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--cache" => cache = PathBuf::from(args.next().context("--cache needs a path")?),
            "--target" => target = PathBuf::from(args.next().context("--target needs a path")?),
            "--prefix" => {
                prefix = Some(PathBuf::from(args.next().context("--prefix needs a path")?))
            }
            "--days" => days = args.next().context("--days needs a duration")?.parse()?,
            "--apply" => apply = true,
            "--help" | "-h" => {
                println!(
                    "repo-tools cache-gc [--cache path] [--target path] [--prefix path] [--days duration] [--apply]\nThe default lists what Git can rebuild that nothing has used lately: expired scratch, memo entries and mesh objects nothing names, stages no build reused, cargo units no build has read and installed builds no launcher names. --apply deletes them and records the uses it saw. Installed runtimes remain."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown cache-gc option {arg}"),
        }
    }
    let now = crate::now();
    let stamp = date(now, "%Y-%m-%d %H:%M:%S");
    let verb = if apply { "freed" } else { "would free" };
    let mut ledger = Ledger::open(cache.join(LEDGER));
    let mut failed = 0;
    if cache.is_dir() {
        let names = Names::read(root, &cache);
        if names.memos.is_none() {
            println!("  the tracked files could not be read; memo entries stay");
        }
        if names.objects.is_none() {
            println!("  the tree's payloads could not be read; mesh objects stay");
        }
        let summary = collect(&cache, &names, &mut ledger, days, apply, now)?;
        println!(
            "{stamp} :: .cache {verb} {:.2} GB in {} unit(s); {} kept{}",
            summary.bytes as f64 / 1e9,
            summary.removed,
            summary.kept,
            if summary.failed > 0 {
                format!("; {} failed", summary.failed)
            } else {
                String::new()
            }
        );
        failed += summary.failed;
    } else {
        println!("{stamp} :: {} does not exist", cache.display());
    }
    if target.is_dir() {
        let swept = sweep(&target, &mut ledger, now - UNIT_DAYS * 86400., now, apply)?;
        println!(
            "{stamp} :: {} {verb} {:.2} GB in {} unit(s); {} kept{}{}",
            target.strip_prefix(root).unwrap_or(&target).display(),
            swept.bytes as f64 / 1e9,
            swept.removed,
            swept.kept,
            if swept.busy > 0 {
                format!("; {} profile(s) in use", swept.busy)
            } else {
                String::new()
            },
            if swept.failed > 0 {
                format!("; {} failed", swept.failed)
            } else {
                String::new()
            }
        );
        failed += swept.failed;
    }
    if let Some(prefix) = prefix.filter(|prefix| prefix.join("lib/hsm").is_dir()) {
        let summary = installed(&prefix, &mut ledger, now - days * 86400., now, apply)?;
        println!(
            "{stamp} :: {} {verb} {:.2} GB in {} build(s); {} kept{}",
            prefix.join("lib/hsm").display(),
            summary.bytes as f64 / 1e9,
            summary.removed,
            summary.kept,
            if summary.failed > 0 {
                format!("; {} failed", summary.failed)
            } else {
                String::new()
            }
        );
        failed += summary.failed;
    }
    if apply && cache.is_dir() {
        ledger.save()?;
    }
    Ok(i32::from(failed > 0))
}

#[cfg(test)]
mod tests {
    use super::*;
    const DAY: f64 = 86400.;
    fn temp() -> PathBuf {
        let p = std::env::temp_dir().join(format!(
            "hsm-cache-gc-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        std::fs::create_dir_all(&p).unwrap();
        p
    }
    fn at(seconds: f64) -> std::time::SystemTime {
        UNIX_EPOCH + Duration::from_secs_f64(seconds)
    }
    fn aged(path: &Path, now: f64) {
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, b"model").unwrap();
        std::fs::File::open(path)
            .unwrap()
            .set_times(std::fs::FileTimes::new().set_modified(at(now)))
            .unwrap();
    }
    fn times(path: &Path, read: f64, written: f64) {
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, b"unit").unwrap();
        std::fs::File::open(path)
            .unwrap()
            .set_times(
                std::fs::FileTimes::new()
                    .set_accessed(at(read))
                    .set_modified(at(written)),
            )
            .unwrap();
    }
    fn read_at(path: &Path, at: f64) {
        times(path, at, at)
    }
    fn names(memos: &[&str], objects: &[&str]) -> Names {
        Names {
            memos: Some(memos.iter().map(|s| s.to_string()).collect()),
            objects: Some(objects.iter().map(|s| s.to_string()).collect()),
        }
    }
    #[test]
    fn scratch_ages_by_its_own_write_and_memos_by_their_names() {
        let root = temp();
        let now = crate::now();
        let old = now - 5. * DAY;
        aged(&root.join("runs/finished/model"), old);
        aged(&root.join("runs/current/model"), now);
        aged(&root.join("printer-control/imports/sent-before/plate.3mf"), old);
        aged(&root.join("printer-control/imports/sent-now/plate.3mf"), now);
        aged(&root.join("meshes/publication/uploaded.gz"), old);
        aged(&root.join("realized/current-step/model"), old);
        aged(&root.join("realized/retired-step/model"), old);
        aged(&root.join(LEDGER), old);
        for keep in ["runtimes", "printer-control/venv"] {
            aged(&root.join(keep).join("model"), old);
        }
        let mut uses = Ledger::open(root.join(LEDGER));
        let names = names(&["realized/current-step"], &[]);
        collect(&root, &names, &mut uses, 3., true, now).unwrap();
        assert!(!root.join("runs/finished").exists());
        assert!(root.join("runs/current/model").is_file());
        assert!(!root.join("printer-control/imports/sent-before").exists());
        assert!(root.join("printer-control/imports/sent-now/plate.3mf").is_file());
        assert!(!root.join("meshes/publication/uploaded.gz").exists());
        assert!(root.join("realized/current-step/model").is_file());
        assert!(!root.join("realized/retired-step").exists());
        assert!(root.join(LEDGER).is_file());
        for keep in ["runtimes", "printer-control/venv"] {
            assert!(root.join(keep).join("model").is_file())
        }
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn unread_names_keep_every_memo() {
        let root = temp();
        let old = crate::now() - 5. * DAY;
        aged(&root.join("realized/some-step/model"), old);
        aged(&root.join(OBJECTS).join(format!("{}.mesh", "a".repeat(64))), old);
        let mut uses = Ledger::open(root.join(LEDGER));
        collect(&root, &Names::default(), &mut uses, 2., true, crate::now()).unwrap();
        assert!(root.join("realized/some-step/model").is_file());
        assert!(root.join(OBJECTS).join(format!("{}.mesh", "a".repeat(64))).is_file());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn objects_stay_while_named() {
        let root = temp();
        let now = crate::now();
        let old = now - 5. * DAY;
        let objects = root.join(OBJECTS);
        let [named, unnamed, recent] = ["a", "b", "c"].map(|c| objects.join(format!("{}.mesh", c.repeat(64))));
        for path in [&named, &unnamed, &recent] {
            read_at(path, old);
        }
        let mut uses = Ledger::open(root.join(LEDGER));
        uses.set(&recent, now - 3600.);
        collect(&root, &names(&[], &[&"a".repeat(64)]), &mut uses, 2., true, now).unwrap();
        assert!(named.is_file() && recent.is_file());
        assert!(!unnamed.exists());
        assert_eq!(uses.get(&named), Some(now));
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn stages_go_once_old_and_never_read_since_written() {
        let root = temp();
        let now = crate::now();
        let old = now - 5. * DAY;
        let stages = root.join(STAGES);
        times(&stages.join("unread.npz"), old - 60., old);
        times(&stages.join("reused.npz"), old + 3600., old);
        times(&stages.join("fresh.npz"), now - 60., now);
        let mut uses = Ledger::open(root.join(LEDGER));
        collect(&root, &names(&[], &[]), &mut uses, 2., true, now).unwrap();
        assert!(!stages.join("unread.npz").exists());
        assert!(stages.join("reused.npz").is_file() && stages.join("fresh.npz").is_file());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[cfg(unix)]
    #[test]
    fn expired_run_symlink_keeps_target() {
        use std::os::unix::ffi::OsStrExt;
        let root = temp();
        let target = root.join("finished.3mf");
        std::fs::write(&target, b"ready print").unwrap();
        let runs = root.join("cache/runs");
        std::fs::create_dir_all(&runs).unwrap();
        let link = runs.join("input");
        std::os::unix::fs::symlink(&target, &link).unwrap();
        let at = (crate::now() - 5. * DAY) as libc::time_t;
        let times = [libc::timespec {
            tv_sec: at,
            tv_nsec: 0,
        }; 2];
        let name = CString::new(link.as_os_str().as_bytes()).unwrap();
        assert_eq!(
            unsafe {
                libc::utimensat(
                    libc::AT_FDCWD,
                    name.as_ptr(),
                    times.as_ptr(),
                    libc::AT_SYMLINK_NOFOLLOW,
                )
            },
            0
        );
        let mut uses = Ledger::open(root.join("cache").join(LEDGER));
        collect(&root.join("cache"), &Names::default(), &mut uses, 3., true, crate::now()).unwrap();
        assert!(!link.exists());
        assert_eq!(std::fs::read(target).unwrap(), b"ready print");
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn sweep_drops_units_no_build_read() {
        let root = temp();
        let (now, old) = (crate::now(), crate::now() - 5. * DAY);
        let profile = root.join("release");
        read_at(&profile.join(".fingerprint/gone-0123456789abcdef/lib-gone"), old);
        read_at(&profile.join("deps/libgone-0123456789abcdef.rlib"), old);
        read_at(&profile.join("build/gone-0123456789abcdef/out/generated.rs"), old);
        read_at(&profile.join(".fingerprint/live-fedcba9876543210/lib-live"), now);
        read_at(&profile.join("deps/liblive-fedcba9876543210.rlib"), old);
        read_at(&profile.join("live"), old);
        read_at(&profile.join("live.d"), old);
        let mut uses = Ledger::open(root.join(LEDGER));
        uses.set(&profile.join(".fingerprint/gone-0123456789abcdef"), old);
        let swept = sweep(&root, &mut uses, now - DAY, now, true).unwrap();
        assert_eq!((swept.removed, swept.kept, swept.busy), (1, 1, 0));
        assert!(!profile.join(".fingerprint/gone-0123456789abcdef").exists());
        assert!(!profile.join("deps/libgone-0123456789abcdef.rlib").exists());
        assert!(!profile.join("build/gone-0123456789abcdef").exists());
        assert!(profile.join("deps/liblive-fedcba9876543210.rlib").is_file());
        assert!(profile.join("live").is_file() && profile.join("live.d").is_file());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn sweep_sees_reads_the_mac_would_hide() {
        // A fingerprint whose access time is its write time shows no read on macOS.
        let root = temp();
        let start = crate::now();
        let old = start - 5. * DAY;
        let profile = root.join("release");
        let fingerprint = profile.join(".fingerprint/live-fedcba9876543210/lib-live");
        read_at(&fingerprint, old);
        read_at(&profile.join("deps/liblive-fedcba9876543210.rlib"), old);
        let mut uses = Ledger::open(root.join(LEDGER));
        // Unseen, the unit counts as read now, and the pass arms it so that a read shows.
        assert_eq!(sweep(&root, &mut uses, start - DAY, start, true).unwrap().removed, 0);
        std::fs::read(&fingerprint).unwrap();
        let meta = std::fs::metadata(&fingerprint).unwrap();
        assert!(meta.accessed().unwrap() > meta.modified().unwrap());
        // A build reading it a day later keeps it; a day with no read after that removes it.
        std::fs::File::open(&fingerprint)
            .unwrap()
            .set_times(std::fs::FileTimes::new().set_accessed(at(start + DAY)))
            .unwrap();
        let kept = sweep(&root, &mut uses, start + 0.5 * DAY, start + 1.5 * DAY, true).unwrap();
        assert_eq!(kept.removed, 0);
        let gone = sweep(&root, &mut uses, start + 2. * DAY, start + 3. * DAY, true).unwrap();
        assert_eq!(gone.removed, 1);
        assert!(!profile.join("deps/liblive-fedcba9876543210.rlib").exists());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn sweep_passes_over_a_profile_a_build_holds() {
        let root = temp();
        let old = crate::now() - 5. * DAY;
        let profile = root.join("release");
        read_at(&profile.join(".fingerprint/gone-0123456789abcdef/lib-gone"), old);
        read_at(&profile.join("deps/libgone-0123456789abcdef.rlib"), old);
        let build = std::fs::File::create(profile.join(".cargo-build-lock")).unwrap();
        build.lock().unwrap();
        let mut uses = Ledger::open(root.join(LEDGER));
        uses.set(&profile.join(".fingerprint/gone-0123456789abcdef"), old);
        let swept = sweep(&root, &mut uses, crate::now() - DAY, crate::now(), true).unwrap();
        assert_eq!((swept.removed, swept.busy), (0, 1));
        assert!(profile.join("deps/libgone-0123456789abcdef.rlib").is_file());
        drop(build);
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn installed_builds_stay_while_a_launcher_names_them() {
        let root = temp();
        let now = crate::now();
        let old = now - 5. * DAY;
        let lib = root.join("lib/hsm");
        let [current, replaced, tool, runtime] = ["1", "2", "3", "4"].map(|c| c.repeat(64));
        let dirs = [
            lib.join(&current),
            lib.join(&replaced),
            lib.join("tools").join(&tool),
            lib.join("runtime").join(&runtime),
        ];
        for dir in &dirs {
            aged(&dir.join("program"), old);
        }
        std::fs::create_dir_all(root.join("bin")).unwrap();
        std::fs::write(root.join("bin/hsm"), format!("exec {}/hsm \"$@\"\n", dirs[0].display())).unwrap();
        std::os::unix::fs::symlink(dirs[2].join("program"), root.join("bin/program")).unwrap();
        std::fs::write(lib.join("runtime.json"), format!("{{\"artifact_id\":\"{runtime}\"}}")).unwrap();
        let mut uses = Ledger::open(root.join(LEDGER));
        let swept = installed(&root, &mut uses, now - 2. * DAY, now, true).unwrap();
        assert_eq!((swept.removed, swept.kept), (1, 3));
        assert!(!dirs[1].exists());
        assert!(dirs[0].is_dir() && dirs[2].is_dir() && dirs[3].is_dir());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn unit_hash_reads_the_name_suffix() {
        assert_eq!(unit_hash("libhsm_kernel-00844a35c28df087.rlib"), Some("00844a35c28df087"));
        assert_eq!(unit_hash("hsm-kernel-00844a35c28df087"), Some("00844a35c28df087"));
        assert_eq!(unit_hash("cafe-deadbeefdeadbeef-00844a35c28df087.d"), Some("00844a35c28df087"));
        assert_eq!(unit_hash("hsm_kernel-1x2y3z"), None);
        assert_eq!(unit_hash("hsm"), None);
    }
}
