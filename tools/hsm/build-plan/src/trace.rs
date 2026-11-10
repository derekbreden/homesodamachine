//! Native tracing records compiler sources and runtime reads from a producer's actual empty-directory run.
use anyhow::{Context, Result, bail, ensure};
use hsm_build_data::{inventory, sources};
use hsm_run_slots::Lease;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::{
    collections::{BTreeMap, BTreeSet}, env, fs::{self, File, OpenOptions},
    io::{BufRead, BufReader, Read, Write}, os::unix::{fs::OpenOptionsExt, process::{CommandExt, ExitStatusExt}},
    path::{Path, PathBuf}, process::{Child, Command, ExitStatus},
    sync::atomic::{AtomicU64, Ordering}, thread,
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};

static SERIAL: AtomicU64 = AtomicU64::new(0);
const DEFAULT_TIMEOUT: Duration = Duration::from_secs(3600);
const DOCUMENT_MEDIA: [&str; 4] = [".md", ".mmd", ".csv", ".json"];

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ProgramSpec {
    #[serde(rename = "crate")] pub krate: String,
    pub name: String,
    #[serde(default)] pub output: String,
}

#[derive(Deserialize)]
struct Registry { programs: BTreeMap<String, ProgramSpec> }

pub fn registry(root: &Path) -> Result<BTreeMap<String, ProgramSpec>> {
    let record: Registry = serde_json::from_slice(&fs::read(root.join("tools/hsm/build-plan/programs.json"))?)?;
    Ok(record.programs)
}

#[derive(Debug, Clone, Default, Deserialize, Serialize)]
pub struct CompiledProgram {
    #[serde(rename = "crate")] pub krate: String,
    pub name: String,
    #[serde(default)] pub sources: BTreeSet<String>,
    #[serde(default, skip_serializing_if = "BTreeSet::is_empty")] pub runtime_inputs: BTreeSet<String>,
    #[serde(flatten)] pub extra: BTreeMap<String, Value>,
}

#[derive(Debug, Clone, Default, Deserialize, Serialize)]
pub struct Reading {
    #[serde(default)] pub reads: BTreeSet<String>,
    #[serde(default)] pub writes: BTreeSet<String>,
    #[serde(default)] pub rewritten: BTreeSet<String>,
    #[serde(default, skip_serializing_if = "Option::is_none")] pub program: Option<CompiledProgram>,
    #[serde(flatten)] pub extra: BTreeMap<String, Value>,
}

pub type Graph = BTreeMap<String, Reading>;

#[derive(Debug)]
struct Outcome { reading: Reading, raised: Option<String> }
impl Outcome {
    fn raised(message: impl Into<String>) -> Self { Self { reading: Reading::default(), raised: Some(message.into()) } }
}

#[derive(Debug, Deserialize)]
struct CargoPackage { id: String, manifest_path: PathBuf }
#[derive(Debug, Deserialize)]
struct DependencyKind { kind: Option<String> }
#[derive(Debug, Deserialize)]
struct Dependency { pkg: String, dep_kinds: Vec<DependencyKind> }
#[derive(Debug, Deserialize)]
struct Node { id: String, deps: Vec<Dependency> }
#[derive(Debug, Deserialize)]
struct Resolve { nodes: Vec<Node> }
#[derive(Debug, Deserialize)]
struct Metadata { packages: Vec<CargoPackage>, workspace_members: BTreeSet<String>, resolve: Resolve }

fn cargo() -> PathBuf {
    if let Some(path) = env::var_os("CARGO") { return path.into(); }
    #[allow(deprecated)]
    let home = env::home_dir().map(|home| home.join(".cargo/bin/cargo"));
    home.filter(|path| path.is_file()).or_else(|| {
        let path = PathBuf::from("/opt/homebrew/opt/rustup/bin/cargo"); path.is_file().then_some(path)
    }).unwrap_or_else(|| "cargo".into())
}

pub fn runner(root: &Path) -> PathBuf {
    let beside = env::current_exe().ok().and_then(|path| path.parent().map(|parent| parent.join("hsm-run")));
    if let Some(path) = beside.filter(|path| path.is_file()) { return path; }
    let local = root.join("tools/hsm/target/release/hsm-run");
    if local.is_file() { return local; }
    #[derive(Deserialize)] struct Runtime { runner: PathBuf }
    #[allow(deprecated)] let home = env::home_dir();
    if let Some(runtime) = home.and_then(|home| fs::read(home.join(".local/lib/hsm/runtime.json")).ok())
        .and_then(|bytes| serde_json::from_slice::<Runtime>(&bytes).ok()).filter(|runtime| runtime.runner.is_file()) { return runtime.runner; }
    "hsm-run".into()
}

pub fn wrapped(root: &Path, executable: &Path, args: &[String], lease: &Lease) -> Result<Command> {
    let mut command = Command::new(runner(root));
    command.arg("--").arg(executable).args(args).current_dir(root).env("HSM_WORKSPACE", root);
    lease.apply(&mut command)?;
    Ok(command)
}

fn metadata(root: &Path, lease: &Lease) -> Result<Metadata> {
    let cargo = cargo();
    let rustc = cargo.with_file_name("rustc");
    let version = wrapped(root, &rustc, &["-vV".into()], lease)?.output()?;
    ensure!(version.status.success(), "rustc version: {}", String::from_utf8_lossy(&version.stderr));
    let version = String::from_utf8(version.stdout)?;
    let host = version.lines().find_map(|line| line.strip_prefix("host: ")).context("rustc host platform")?;
    let args = ["metadata", "--format-version", "1", "--offline", "--locked", "--filter-platform", host, "--manifest-path"]
        .into_iter().map(str::to_owned).chain([root.join("tools/hsm/Cargo.toml").to_string_lossy().into_owned()]).collect::<Vec<_>>();
    let result = wrapped(root, &cargo, &args, lease)?.output()?;
    ensure!(result.status.success(), "cargo metadata: {}", String::from_utf8_lossy(&result.stderr));
    serde_json::from_slice(&result.stdout).context("parse cargo metadata")
}

fn crates_of(metadata: &Metadata, manifest: &Path) -> BTreeSet<String> {
    let nodes = metadata.resolve.nodes.iter().map(|node| (&node.id, node)).collect::<BTreeMap<_, _>>();
    let mut todo = metadata.packages.iter().filter(|package| package.manifest_path == manifest).map(|package| package.id.clone()).collect::<Vec<_>>();
    let mut seen = BTreeSet::new();
    while let Some(package) = todo.pop() {
        if !seen.insert(package.clone()) { continue; }
        if let Some(node) = nodes.get(&package) {
            todo.extend(node.deps.iter().filter(|dependency| dependency.dep_kinds.iter().any(|kind| kind.kind.as_deref() != Some("dev"))).map(|dependency| dependency.pkg.clone()));
        }
    }
    seen
}

fn compiled_from(root: &Path, program: &ProgramSpec, metadata: &Metadata, files: &BTreeSet<String>, config: &Value) -> Result<BTreeSet<String>> {
    let mut compiled = sources::compiled(&root.join("tools/hsm/target/release").join(format!("{}.d", program.name)), root)?.into_iter().collect::<BTreeSet<_>>();
    let seen = crates_of(metadata, &root.join("tools/hsm").join(&program.krate).join("Cargo.toml"));
    if program.name == "hsm-cargo-config" {
        compiled.extend(["tools/hsm/Cargo.toml".to_owned(), "tools/hsm/Cargo.lock".to_owned()]);
    } else { compiled.insert("tools/hsm/cargo-config.json".into()); }
    for package in metadata.packages.iter().filter(|package| seen.contains(&package.id)) {
        if let Ok(relative) = package.manifest_path.strip_prefix(root) {
            compiled.insert(relative.to_string_lossy().into_owned());
            if !metadata.workspace_members.contains(&package.id) {
                let prefix = relative.parent().unwrap_or(Path::new("")).to_string_lossy().to_string() + "/";
                compiled.extend(files.iter().filter(|path| path.starts_with(&prefix)).cloned());
            }
        }
    }
    compiled.retain(|path| files.contains(path) && !inventory::inert(path, config));
    Ok(compiled)
}

fn walk_files(root: &Path) -> Result<Vec<PathBuf>> {
    let mut paths = Vec::new(); let mut todo = vec![root.to_owned()];
    while let Some(directory) = todo.pop() {
        for entry in fs::read_dir(&directory)? {
            let entry = entry?; let kind = entry.file_type()?;
            if kind.is_dir() { todo.push(entry.path()); }
            else if kind.is_file() { paths.push(entry.path()); }
        }
    }
    paths.sort(); Ok(paths)
}

struct Scratch(PathBuf);
impl Scratch {
    fn new(root: &Path, name: &str) -> Result<Self> {
        let stamp = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
        let directory = root.join(".cache/runs").join(format!("trace-{name}-{stamp}-{}", std::process::id()));
        fs::create_dir_all(&directory)?; Ok(Self(directory))
    }
}
impl Drop for Scratch { fn drop(&mut self) { let _ = fs::remove_dir_all(&self.0); } }

struct Temporary(PathBuf);
impl Drop for Temporary { fn drop(&mut self) { let _ = fs::remove_file(&self.0); } }

fn copy(source: &Path, target: &Path) -> Result<()> {
    let parent = target.parent().context("trace output parent")?; fs::create_dir_all(parent)?;
    let (temporary, mut file) = loop {
        let serial = SERIAL.fetch_add(1, Ordering::Relaxed);
        let temporary = parent.join(format!(".{}.trace-{}-{serial}", target.file_name().context("trace output name")?.to_string_lossy(), std::process::id()));
        match OpenOptions::new().write(true).create_new(true).mode(0o600).open(&temporary) {
            Ok(file) => break (Temporary(temporary), file),
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => (),
            Err(error) => return Err(error.into()),
        }
    };
    std::io::copy(&mut File::open(source)?, &mut file)?; file.flush()?; drop(file);
    fs::set_permissions(&temporary.0, fs::metadata(target).or_else(|_| fs::metadata(source))?.permissions())?;
    fs::rename(&temporary.0, target)?; Ok(())
}

fn status_code(status: ExitStatus) -> i32 { status.code().unwrap_or_else(|| 128 + status.signal().unwrap_or(1)) }

fn wait(child: &mut Child, timeout: Duration) -> Result<Option<ExitStatus>> {
    let started = Instant::now();
    loop {
        if let Some(status) = child.try_wait()? { return Ok(Some(status)); }
        if started.elapsed() >= timeout {
            // The producer owns its process group; killing it also ends runner descendants.
            let group = i32::try_from(child.id()).context("producer process-group id")?;
            let sent = unsafe { libc::kill(-group, libc::SIGKILL) };
            if sent != 0 {
                let error = std::io::Error::last_os_error();
                if error.raw_os_error() != Some(libc::ESRCH) { return Err(error.into()); }
            }
            child.wait()?; return Ok(None);
        }
        thread::sleep(Duration::from_millis(100));
    }
}

fn runtime_reads(root: &Path, log: &Path) -> Result<BTreeSet<String>> {
    let file = File::open(log).with_context(|| format!("producer did not write its runtime-read receipt: {}", log.display()))?;
    let mut lines = BufReader::new(file).lines();
    ensure!(lines.next().transpose()?.as_deref() == Some("hsm-reads 1"), "unrecognized runtime-read receipt");
    let mut read = BTreeSet::new();
    for line in lines {
        let line = line?; let path = Path::new(line.split('\t').next().unwrap_or(""));
        if let Ok(relative) = path.strip_prefix(root) { read.insert(relative.to_string_lossy().into_owned()); }
    }
    Ok(read)
}

fn reading(source: &str, program: &ProgramSpec, compiled: BTreeSet<String>, read: BTreeSet<String>, writes: BTreeSet<String>, files: &BTreeSet<String>, config: &Value) -> Result<Reading> {
    let runtime_inputs = read.intersection(&compiled).cloned().collect();
    let rewritten = writes.intersection(&read).filter(|path| DOCUMENT_MEDIA.iter().any(|suffix| path.ends_with(suffix))).cloned().collect::<BTreeSet<_>>();
    let generated_only = writes.difference(&rewritten).cloned().collect::<BTreeSet<_>>();
    let mut reads = read.into_iter().filter(|path| files.contains(path) && !inventory::inert(path, config)).collect::<BTreeSet<_>>();
    reads.extend(compiled.iter().cloned()); reads.retain(|path| !generated_only.contains(path));
    ensure!(reads.contains(source), "compiler did not name registered producer source {source}");
    Ok(Reading { reads, writes, rewritten, program: Some(CompiledProgram {
        krate: program.krate.clone(), name: program.name.clone(), sources: compiled, runtime_inputs, extra: BTreeMap::new(),
    }), extra: BTreeMap::new() })
}

fn trace_one(root: &Path, source: &str, program: &ProgramSpec, metadata: &Metadata, files: &BTreeSet<String>, config: &Value, lease: &Lease, timeout: Duration) -> Result<Outcome> {
    let cargo = cargo();
    let build = ["build", "--release", "--locked", "-j", "2", "--manifest-path"].into_iter().map(str::to_owned)
        .chain([root.join("tools/hsm").join(&program.krate).join("Cargo.toml").to_string_lossy().into_owned(), "--bin".into(), program.name.clone()]).collect::<Vec<_>>();
    let built = wrapped(root, &cargo, &build, lease)?.env("CARGO_TARGET_DIR", root.join("tools/hsm/target")).status()?;
    if !built.success() { return Ok(Outcome::raised(format!("cargo build exited {}", status_code(built)))); }
    let compiled = compiled_from(root, program, metadata, files, config)?;
    let scratch = Scratch::new(root, &program.name)?; let made = scratch.0.join("out"); fs::create_dir(&made)?;
    let log = scratch.0.join("reads"); let stderr = scratch.0.join("stderr.log");
    let executable = root.join("tools/hsm/target/release").join(&program.name);
    let mut command = wrapped(root, &executable, &[made.to_string_lossy().into_owned()], lease)?;
    command.env("HSM_READS", &log).env("HSM_REPO_ROOT", root)
        .stdout(File::create(scratch.0.join("stdout.log"))?).stderr(File::create(&stderr)?);
    command.process_group(0);
    let mut child = command.spawn()?;
    let Some(status) = wait(&mut child, timeout)? else { return Ok(Outcome::raised(format!("producer exceeded {} seconds", timeout.as_secs()))); };
    if !status.success() {
        let last = BufReader::new(File::open(stderr)?).lines().map_while(std::result::Result::ok).filter(|line| !line.trim().is_empty()).last();
        return Ok(Outcome::raised(last.unwrap_or_else(|| format!("producer exited {}", status_code(status)))));
    }
    let read = runtime_reads(root, &log)?;
    let written = walk_files(&made)?;
    let mut writes = BTreeSet::new();
    for path in written {
        let relative = path.strip_prefix(&made)?;
        let target = Path::new(&program.output).join(relative);
        copy(&path, &root.join(&target))?;
        let relative = target.to_string_lossy().into_owned();
        if !inventory::inert(&relative, config) { writes.insert(relative); }
    }
    Ok(Outcome { reading: reading(source, program, compiled, read, writes, files, config)?, raised: None })
}

fn read_graph(path: &Path) -> Result<Graph> {
    match fs::read(path) { Ok(bytes) => serde_json::from_slice(&bytes).context("read trace graph"), Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(BTreeMap::new()), Err(error) => Err(error.into()) }
}

fn tracked(root: &Path, graph: &Graph, config: &Value) -> Result<BTreeSet<String>> {
    let publication: Value = serde_json::from_slice(&fs::read(root.join("tools/hsm/publication/config.json"))?)?;
    let mut files = inventory::tracked(root, config, &publication)?;
    files.extend(graph.values().flat_map(|entry| entry.writes.iter().cloned()));
    files.retain(|path| !inventory::inert(path, config)); Ok(files)
}

fn gave_up(prior: &Reading, current: &Reading) -> bool { prior.reads.len() > current.reads.len() || prior.writes.len() > current.writes.len() }

#[derive(Debug, Default, PartialEq, Eq)]
struct Retention { kept: usize, missing: usize }

// A full sweep retains prior declarations only while the checkout still holds their paths.
fn replacement(root: &Path, prior: Option<&Reading>, mut current: Reading, all: bool) -> (Reading, Retention) {
    let mut retention = Retention::default();
    if let Some(prior) = prior.filter(|_| all) {
        for (old, fresh) in [(&prior.reads, &mut current.reads), (&prior.writes, &mut current.writes), (&prior.rewritten, &mut current.rewritten)] {
            for path in old.difference(fresh).cloned().collect::<Vec<_>>() {
                if root.join(&path).exists() { fresh.insert(path); retention.kept += 1; }
                else { retention.missing += 1; }
            }
        }
    }
    (current, retention)
}

fn digest(path: &Path) -> Result<String> {
    let mut file = File::open(path)?; let mut hash = Sha256::new(); let mut bytes = [0; 65536];
    loop { let count = file.read(&mut bytes)?; if count == 0 { break; } hash.update(&bytes[..count]); }
    Ok(format!("{:x}", hash.finalize()))
}

fn pointer_debt(root: &Path, writes: &BTreeSet<String>) -> Result<Vec<String>> {
    #[derive(Default, Deserialize)] struct Pointers { #[serde(default)] solids: BTreeMap<String, String> }
    let held: Pointers = match fs::read(root.join("hardware/cad-artifacts.json")) { Ok(bytes) => serde_json::from_slice(&bytes)?, Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(Vec::new()), Err(error) => return Err(error.into()) };
    let mut changed = Vec::new();
    for path in writes { if let Some(expected) = held.solids.get(path) { let file = root.join(path); if file.is_file() && digest(&file)? != *expected { changed.push(path.clone()); } } }
    Ok(changed)
}

pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut all = false; let mut selected = Vec::new(); let mut graph_path = root.join("tools/bazel/graph.json"); let mut timeout = DEFAULT_TIMEOUT;
    let mut at = 0;
    while at < args.len() {
        match args[at].as_str() {
            "--all" => all = true,
            "--graph" => { at += 1; graph_path = PathBuf::from(args.get(at).context("--graph requires a path")?); if graph_path.is_relative() { graph_path = root.join(graph_path); } }
            "--timeout" => { at += 1; timeout = Duration::from_secs(args.get(at).context("--timeout requires seconds")?.parse()?); }
            "--help" | "-h" => { println!("Trace registered native producers and carry their outputs.\n\nUsage: hsm-build-plan trace-inputs [--graph FILE] [--timeout SECONDS] SOURCE.rs ...\nUse --all to trace the full registered set and retain prior declarations whose paths still exist."); return Ok(0); }
            option if option.starts_with('-') => bail!("unknown trace option {option}"),
            source => selected.push(source.trim_start_matches("./").to_owned()),
        }
        at += 1;
    }
    ensure!(!timeout.is_zero(), "trace timeout must be positive");
    let programs = registry(root)?;
    let config: Value = serde_json::from_slice(&fs::read(root.join("tools/hsm/build-plan/inventory.json"))?)?;
    let mut graph = read_graph(&graph_path)?;
    let files = tracked(root, &graph, &config)?;
    if selected.is_empty() && !all {
        eprintln!("Select the native producer source whose inputs need a new reading. Use --all for an intentional full sweep."); return Ok(2);
    }
    if selected.is_empty() { selected = programs.keys().filter(|source| files.contains(*source) && root.join(source).exists()).cloned().collect(); }
    for source in &selected { ensure!(programs.contains_key(source), "not a registered native producer: {source}"); }
    let lease = hsm_run_slots::acquire("build-plan:trace", hsm_run_slots::inherited()?, false)?;
    let metadata = metadata(root, &lease)?;
    let mut shrank = Vec::new(); let mut wrote = BTreeSet::new(); let mut retention = Retention::default();
    for (index, source) in selected.iter().enumerate() {
        let mut result = trace_one(root, source, &programs[source], &metadata, &files, &config, &lease, timeout)?;
        if !result.reading.writes.is_empty() {
            // Pointer debt concerns exports made by this run, not retained declarations.
            wrote.extend(result.reading.writes.iter().cloned());
            let (reading, kept) = replacement(root, graph.get(source), result.reading, all);
            result.reading = reading; retention.kept += kept.kept; retention.missing += kept.missing;
            if let Some(prior) = graph.get(source).filter(|prior| gave_up(prior, &result.reading)) { shrank.push((source.clone(), prior.reads.len(), result.reading.reads.len(), prior.writes.len(), result.reading.writes.len())); }
            graph.insert(source.clone(), result.reading.clone());
            if let Some(parent) = graph_path.parent() { fs::create_dir_all(parent)?; }
            fs::write(&graph_path, serde_json::to_string_pretty(&graph)? + "\n")?;
        } else if let Some(raised) = result.raised {
            println!("[{:>3}/{}] {source} raised {raised} — {}", index + 1, selected.len(), if graph.contains_key(source) { "keeping its prior reading" } else { "no graph entry is available" });
            std::io::stdout().flush()?; continue;
        } else if graph.contains_key(source) {
            println!("[{:>3}/{}] {source} wrote nothing — keeping its prior reading", index + 1, selected.len());
            std::io::stdout().flush()?; continue;
        }
        println!("[{:>3}/{}] {source}: {} read, {} written", index + 1, selected.len(), result.reading.reads.len(), result.reading.writes.len());
        std::io::stdout().flush()?;
    }
    println!("{} generator(s) in the graph", graph.len());
    if all { println!("{} prior declaration(s) retained because their paths exist; {} missing path(s) dropped", retention.kept, retention.missing); }
    if !shrank.is_empty() {
        println!("{} reading(s) gave up prior inputs or outputs:", shrank.len());
        for (source, old_reads, reads, old_writes, writes) in shrank { println!("  {source}: {old_reads} -> {reads} read, {old_writes} -> {writes} written"); }
    }
    let behind = pointer_debt(root, &wrote)?;
    if !behind.is_empty() {
        println!("{} traced member(s) differ from the served pointer:", behind.len());
        for path in behind { println!("  {path}"); }
        println!("The trace carries generated bytes; publication is a separate request.");
    }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn scratch(name: &str) -> Scratch {
        Scratch::new(Path::new(env!("CARGO_MANIFEST_DIR")).join("../../..").as_path(), name).unwrap()
    }

    #[test]
    fn dependency_closure_excludes_dev_only_edges_and_keeps_build_dependencies() {
        let metadata: Metadata = serde_json::from_value(json!({"packages":[{"id":"app","manifest_path":"/repo/app/Cargo.toml"},{"id":"normal","manifest_path":"/external/normal/Cargo.toml"},{"id":"build","manifest_path":"/external/build/Cargo.toml"},{"id":"test","manifest_path":"/external/test/Cargo.toml"}],"workspace_members":["app"],"resolve":{"nodes":[{"id":"app","deps":[{"pkg":"normal","dep_kinds":[{"kind":null}]},{"pkg":"build","dep_kinds":[{"kind":"build"}]},{"pkg":"test","dep_kinds":[{"kind":"dev"}]}]},{"id":"normal","deps":[]},{"id":"build","deps":[]},{"id":"test","deps":[]}]}})).unwrap();
        assert_eq!(crates_of(&metadata, Path::new("/repo/app/Cargo.toml")), ["app", "build", "normal"].map(str::to_owned).into());
    }

    #[test]
    fn losing_either_side_of_a_reading_is_reported() {
        let reading = |read: usize, write: usize| Reading { reads: (0..read).map(|i| format!("r{i}")).collect(), writes: (0..write).map(|i| format!("w{i}")).collect(), ..Reading::default() };
        assert!(gave_up(&reading(5,3), &reading(9,1)));
        assert!(gave_up(&reading(9,1), &reading(5,3)));
        assert!(!gave_up(&reading(5,1), &reading(9,3)));
        assert!(!gave_up(&reading(9,3), &reading(9,3)));
    }

    #[test]
    fn graph_roundtrip_retains_program_runtime_inputs_and_unknown_metadata() {
        let input = json!({"producer.rs":{"reads":["Cargo.toml","producer.rs"],"writes":["out.json"],"rewritten":[],"trace_note":"kept","program":{"crate":"producer","name":"producer","sources":["Cargo.toml","producer.rs"],"runtime_inputs":["Cargo.toml"],"future":true}}});
        let graph: Graph = serde_json::from_value(input.clone()).unwrap();
        assert_eq!(serde_json::to_value(graph).unwrap(), input);
    }

    #[test]
    fn full_sweep_retains_existing_prior_paths_without_retaining_old_compiler_metadata() {
        let scratch = scratch("retention-test");
        for path in ["old.rs", "present.stl", "notes.md"] { fs::write(scratch.0.join(path), "held").unwrap(); }
        let prior = Reading { reads: ["old.rs", "missing.rs", "notes.md"].map(str::to_owned).into(),
            writes: ["present.stl", "missing.stl", "notes.md"].map(str::to_owned).into(),
            rewritten: ["notes.md", "missing.md"].map(str::to_owned).into(),
            program: Some(CompiledProgram { name: "old-program".into(), sources: ["old.rs".into()].into(), ..CompiledProgram::default() }),
            ..Reading::default() };
        let current = Reading { reads: ["new.rs".into()].into(), writes: ["new.stl".into()].into(),
            program: Some(CompiledProgram { name: "new-program".into(), sources: ["new.rs".into()].into(), ..CompiledProgram::default() }),
            ..Reading::default() };
        let (merged, retention) = replacement(&scratch.0, Some(&prior), current.clone(), true);
        assert_eq!(retention, Retention { kept: 5, missing: 3 });
        assert_eq!(merged.reads, ["new.rs", "old.rs", "notes.md"].map(str::to_owned).into());
        assert_eq!(merged.writes, ["new.stl", "present.stl", "notes.md"].map(str::to_owned).into());
        assert_eq!(merged.rewritten, ["notes.md".into()].into());
        assert_eq!(merged.program.as_ref().unwrap().name, "new-program");
        assert_eq!(merged.program.as_ref().unwrap().sources, ["new.rs".into()].into());
        let (narrow, retention) = replacement(&scratch.0, Some(&prior), current, false);
        assert_eq!(retention, Retention::default());
        assert_eq!(narrow.reads, ["new.rs".into()].into());
        assert_eq!(narrow.writes, ["new.stl".into()].into());
        assert!(narrow.rewritten.is_empty());
    }

    #[test]
    fn runtime_receipts_keep_only_repo_reads_and_require_the_protocol() {
        let scratch = scratch("receipt-test");
        let log = scratch.0.join("reads");
        let root = scratch.0.join("repo");
        fs::write(&log, format!("hsm-reads 1\n{}/Cargo.toml\tdigest\n/external/dependency.rs\tdigest\n{}/part.stl\tdigest\n", root.display(), root.display())).unwrap();
        assert_eq!(runtime_reads(&root, &log).unwrap(), ["Cargo.toml", "part.stl"].map(str::to_owned).into());
        fs::write(&log, "old protocol\n").unwrap();
        assert!(runtime_reads(&root, &log).is_err());
    }

    #[test]
    fn trace_keeps_runtime_compiler_inputs_and_ignored_generated_handoffs() {
        let source = "producer.rs";
        let program = ProgramSpec { krate: "producer".into(), name: "producer".into(), output: String::new() };
        let compiled = [source, "Cargo.toml"].map(str::to_owned).into();
        let read = ["Cargo.toml", "ignored/intermediate.json", "part.stl", "notes.md", "unrelated", "workspace.3mf"].map(str::to_owned).into();
        let writes = ["part.stl", "notes.md"].map(str::to_owned).into();
        let files = [source, "Cargo.toml", "ignored/intermediate.json", "part.stl", "notes.md", "workspace.3mf"].map(str::to_owned).into();
        let result = reading(source, &program, compiled, read, writes, &files, &json!({"inert_suffixes":[".3mf"]})).unwrap();
        assert_eq!(result.reads, ["Cargo.toml", "ignored/intermediate.json", "notes.md", source].map(str::to_owned).into());
        assert_eq!(result.rewritten, ["notes.md".into()].into());
        assert_eq!(result.program.unwrap().runtime_inputs, ["Cargo.toml".into()].into());
    }

    #[test]
    fn cargo_config_compiles_without_depending_on_its_own_generated_output() {
        let scratch = scratch("config-input-test"); let root = scratch.0.canonicalize().unwrap();
        let source = "tools/hsm/cargo-config/src/cargo_config.rs";
        let target = root.join("tools/hsm/target/release"); fs::create_dir_all(&target).unwrap();
        fs::write(target.join("hsm-cargo-config.d"), format!("config: {}\n", root.join(source).display())).unwrap();
        let manifest = root.join("tools/hsm/cargo-config/Cargo.toml");
        let metadata: Metadata = serde_json::from_value(json!({"packages":[{"id":"config","manifest_path":manifest}],"workspace_members":["config"],"resolve":{"nodes":[{"id":"config","deps":[]}]}})).unwrap();
        let files = [source, "tools/hsm/cargo-config/Cargo.toml", "tools/hsm/Cargo.toml", "tools/hsm/Cargo.lock", "tools/hsm/cargo-config.json"].map(str::to_owned).into();
        let result = compiled_from(&root, &ProgramSpec { krate: "cargo-config".into(), name: "hsm-cargo-config".into(), output: String::new() }, &metadata, &files, &json!({})).unwrap();
        assert!(result.contains(source));
        assert!(result.contains("tools/hsm/Cargo.toml")); assert!(result.contains("tools/hsm/Cargo.lock"));
        assert!(!result.contains("tools/hsm/cargo-config.json"));
    }

    #[test]
    fn output_carry_replaces_one_file_and_cleans_its_temporary() {
        use std::os::unix::fs::PermissionsExt;
        let scratch = scratch("copy-test");
        let source = scratch.0.join("built"); let target = scratch.0.join("tree/part.stl");
        fs::write(&source, "fresh mesh").unwrap();
        copy(&source, &target).unwrap();
        fs::set_permissions(&target, fs::Permissions::from_mode(0o640)).unwrap();
        fs::write(&source, "newer mesh").unwrap();
        copy(&source, &target).unwrap();
        assert_eq!(fs::read(&target).unwrap(), b"newer mesh");
        assert_eq!(fs::metadata(&target).unwrap().permissions().mode() & 0o777, 0o640);
        assert!(copy(&scratch.0.join("absent"), &target).is_err());
        assert_eq!(fs::read(&target).unwrap(), b"newer mesh");
        assert_eq!(fs::read_dir(target.parent().unwrap()).unwrap().count(), 1);
    }

    #[test]
    fn timeout_reaps_the_isolated_producer() {
        let mut command = Command::new("/bin/sleep");
        command.arg("30").process_group(0);
        let mut child = command.spawn().unwrap();
        assert!(wait(&mut child, Duration::from_millis(1)).unwrap().is_none());
        assert!(!child.try_wait().unwrap().unwrap().success());
    }
}
