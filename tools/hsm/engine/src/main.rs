mod build;
mod mcp;
mod published;
mod render;
mod service;
mod store;

use anyhow::{Context, Result, bail, ensure};
use clap::{Parser, Subcommand};
use fs2::FileExt;
use hsm_run_slots::{Lease, ipc};
use serde_json::{Value, json};
use service::{Query, Request};
use sha2::{Digest, Sha256};
use std::{
    fs::{self, OpenOptions},
    io::{BufRead, BufReader, Read, Write},
    os::unix::{
        fs::{OpenOptionsExt, PermissionsExt},
        io::AsRawFd,
        net::{UnixListener, UnixStream},
        process::CommandExt,
    },
    path::{Component, Path, PathBuf},
    process::{Command, Stdio},
    sync::Arc,
    thread,
    time::{Duration, Instant},
};

#[derive(Parser)]
#[command(
    version,
    about = "Query the machine's /3d meshes through one resident geometry process"
)]
struct Args {
    #[arg(long, global = true)]
    root: Option<PathBuf>,
    #[arg(long, global = true, default_value = "machine")]
    scene: String,
    #[arg(long, global = true)]
    socket: Option<PathBuf>,
    #[arg(long, global = true)]
    store: Option<PathBuf>,
    #[arg(long, global = true, default_value_t = 768)]
    cache_mb: u64,
    /// Memory the part runs a daemon this call starts may hold at once, by their measured peaks.
    #[arg(long, global = true, default_value_t = 1024)]
    build_mb: u64,
    /// What the kept part runs may hold on disk; the least recently used go at idle exit.
    #[arg(long, global = true, default_value_t = 4096)]
    keep_mb: u64,
    /// Minutes without a query before a daemon this call starts exits; 0 keeps it running.
    #[arg(long, global = true, default_value_t = 15.0)]
    idle_minutes: f64,
    #[command(subcommand)]
    command: Action,
}

#[derive(Subcommand)]
enum Action {
    /// Run the socket service in the foreground. Ordinary queries start it automatically.
    Daemon,
    /// Run an MCP server over standard input/output; it uses the shared daemon.
    Mcp,
    Status,
    Stop,
    /// This executable's build, default service endpoint and resolved executable path; starts no daemon.
    Endpoint,
    /// Run an enrolled Python generator and its declared producer dependencies.
    Generate {
        target: String,
        #[arg(long)]
        output: Option<PathBuf>,
        /// CAD interpreter to use when this worktree has no tools/cad-venv.
        #[arg(long)]
        python: Option<PathBuf>,
    },
    /// Names, world bounds, dimensions and stable payload indices.
    Where {
        #[arg(default_value = "")]
        pattern: String,
    },
    /// Surface distance, witnesses and solid clearance between two unique solids.
    Gap {
        a: String,
        b: String,
    },
    /// Intersection volume, including containment, in cubic millimetres.
    Overlap {
        a: String,
        b: String,
    },
    /// Test a translation against the scene without changing any geometry.
    Move {
        part: String,
        #[arg(long, num_args = 3, allow_hyphen_values = true, required = true)]
        by: Vec<f64>,
        #[arg(long)]
        against: Option<String>,
        #[arg(long, default_value_t = 1e-6)]
        min_volume: f64,
    },
    /// Triangle segments at normal.dot(point) = offset, retaining viewer face IDs.
    Section {
        part: String,
        #[arg(long, num_args = 3, allow_hyphen_values = true, required = true)]
        normal: Vec<f64>,
        #[arg(long, allow_hyphen_values = true)]
        offset: f64,
    },
    /// The nearest hit in the scene; direction is normalized and distance is in mm.
    Ray {
        #[arg(long, num_args = 3, allow_hyphen_values = true, required = true)]
        origin: Vec<f64>,
        #[arg(long, num_args = 3, allow_hyphen_values = true, required = true)]
        direction: Vec<f64>,
        #[arg(long, default_value_t = 1e6)]
        max_distance: f64,
    },
    /// Pictures of a payload, drawn on the GPU as /3d draws them.
    Render(render::RenderArgs),
    /// Send a JSON request using the socket protocol.
    Request {
        json: String,
    },
}

pub struct Client {
    executable: PathBuf,
    socket: PathBuf,
    store: PathBuf,
    root: PathBuf,
    scene: String,
    cache_mb: u64,
    build_mb: u64,
    keep_mb: u64,
    idle_minutes: f64,
}

fn build_id() -> String {
    let mut h = Sha256::new();
    h.update(include_str!("main.rs"));
    h.update(include_str!("build.rs"));
    h.update(include_str!("service.rs"));
    h.update(include_str!("store.rs"));
    h.update(include_str!("mcp.rs"));
    h.update(include_str!("published.rs"));
    h.update(include_str!("render.rs"));
    h.update(hsm_render::source_digest());
    h.update(hsm_run_slots::source_digest());
    h.update(store::geometry_version());
    format!("{:x}", h.finalize())
}

fn runtime_dir() -> PathBuf {
    // geteuid has no preconditions and does not read credentials.
    let uid = unsafe { libc::geteuid() };
    PathBuf::from(format!("/tmp/hsm-{uid}"))
}

fn cache_dir() -> Result<PathBuf> {
    if let Some(path) = std::env::var_os("HSM_STORE") {
        return Ok(path.into());
    }
    if let Some(path) = std::env::var_os("XDG_CACHE_HOME") {
        return Ok(PathBuf::from(path).join("hsm"));
    }
    let home = PathBuf::from(std::env::var_os("HOME").context("set HOME or --store")?);
    Ok(home.join(if cfg!(target_os = "macos") {
        "Library/Caches/hsm"
    } else {
        ".cache/hsm"
    }))
}

/// Resolve the existing prefix without creating a store an `endpoint` call only names.
fn store_path(path: &Path) -> Result<PathBuf> {
    for parent in path.ancestors() {
        if let Ok(mut full) = parent.canonicalize() {
            for component in path.strip_prefix(parent)?.components() {
                match component {
                    Component::ParentDir => { full.pop(); }
                    Component::CurDir => (),
                    component => full.push(component.as_os_str()),
                }
            }
            return Ok(full);
        }
    }
    bail!("cannot resolve store {}", path.display())
}

fn configuration(store: &Path, cache_mb: u64, build_mb: u64, keep_mb: u64) -> Value {
    json!({"store": store, "cache_mb": cache_mb, "build_mb": build_mb, "keep_mb": keep_mb})
}

fn default_socket(configuration: &Value) -> PathBuf {
    let mut hash = Sha256::new();
    hash.update(build_id());
    hash.update(configuration.to_string());
    runtime_dir().join(format!("engine-{:x}.sock", hash.finalize()))
}

fn private_directory(path: &Path) -> Result<()> {
    fs::create_dir_all(path)?;
    fs::set_permissions(path, fs::Permissions::from_mode(0o700))?;
    Ok(())
}

pub fn scene_path(root: &Path, scene: &str) -> PathBuf {
    let scene = match scene {
        "machine" => "hardware/manifold-layout/enclosure-assembly.step.mesh",
        "faucet" => "hardware/faucet-layout/faucet-assembly.step.mesh",
        "enclosure" => "hardware/printed-parts/enclosure/enclosure/enclosure.step.mesh",
        _ => scene,
    };
    let scene = if scene.ends_with(".step") {
        format!("{scene}.mesh")
    } else {
        scene.to_owned()
    };
    root.join(scene)
}

fn read_message(stream: &mut UnixStream, limit: u64) -> Result<Value> {
    let mut line = String::new();
    if BufReader::new(stream.take(limit)).read_line(&mut line)? == 0 {
        return Err(std::io::Error::from(std::io::ErrorKind::UnexpectedEof).into());
    }
    ensure!(
        line.ends_with('\n'),
        "incomplete or oversized socket message"
    );
    Ok(serde_json::from_str(&line)?)
}

fn send(socket: &Path, request: &Request) -> Result<Value> {
    let mut stream = UnixStream::connect(socket)?;
    // A part run waits its turn and may compile first; a query is answered or it is stuck.
    let wait = match request.query {
        Query::Run { .. } | Query::Generate { .. } | Query::Render { .. } => None,
        _ => Some(Duration::from_secs(300)),
    };
    stream.set_read_timeout(wait)?;
    let mut message = serde_json::to_value(request)?;
    let lease = if matches!(request.query, Query::Run { .. } | Query::Generate { .. } | Query::Render { .. }) {
        hsm_run_slots::inherited()?
    } else { None };
    if let Some(lease) = &lease { message["_lease"] = serde_json::to_value(lease.wire())?; }
    ipc::send(&stream, &message, &lease.as_ref().map_or_else(Vec::new, Lease::descriptors))?;
    read_message(&mut stream, 64 * 1024 * 1024)
}

fn control(query: Query) -> Request {
    Request {
        scene: PathBuf::new(),
        query,
    }
}

impl Client {
    fn configuration(&self) -> Value {
        configuration(&self.store, self.cache_mb, self.build_mb, self.keep_mb)
    }

    fn compatible(&self, response: &Value) -> Result<()> {
        ensure!(
            response["ok"] == true && response["result"]["build_id"] == build_id(),
            "{} serves hsm build {}; this client is build {}; use its default endpoint or stop that daemon explicitly",
            self.socket.display(), response["result"]["build_id"], build_id()
        );
        ensure!(
            response["result"]["configuration"] == self.configuration(),
            "{} serves configuration {}; requested {}; use the default endpoint or stop that daemon explicitly",
            self.socket.display(), response["result"]["configuration"], self.configuration()
        );
        Ok(())
    }

    pub fn call(&self, request: &Request) -> Result<Value> {
        if request.query.needs_scene() { published::ensure(&request.scene)?; }
        self.ensure_daemon()?;
        send(&self.socket, request).or_else(|e| {
            // A daemon that went idle between the ping and this request has closed its socket.
            // Queries change nothing, so the request goes once more, to a fresh daemon.
            let gone = e.downcast_ref::<std::io::Error>().is_some_and(|e| {
                use std::io::ErrorKind::*;
                matches!(
                    e.kind(),
                    NotFound | ConnectionRefused | ConnectionReset | BrokenPipe | UnexpectedEof
                )
            });
            if !gone {
                return Err(e);
            }
            self.ensure_daemon()?;
            send(&self.socket, request)
        })
    }

    fn ensure_daemon(&self) -> Result<()> {
        let ping = || send(&self.socket, &control(Query::Ping));
        if let Ok(p) = ping() {
            return self.compatible(&p);
        }
        let parent = self
            .socket
            .parent()
            .context("socket needs a parent directory")?;
        fs::create_dir_all(parent)?;
        let startup = OpenOptions::new()
            .create(true)
            .truncate(false)
            .read(true)
            .write(true)
            .mode(0o600)
            .open(self.socket.with_extension("start.lock"))?;
        startup.lock_exclusive()?;
        if let Ok(p) = ping() {
            return self.compatible(&p);
        }
        // Socket removal precedes destruction of the old scene. Wait for its
        // lifetime lock as well, so the replacement can acquire that lock.
        let ownership = OpenOptions::new()
            .create(true)
            .truncate(false)
            .read(true)
            .write(true)
            .mode(0o600)
            .open(self.socket.with_extension("daemon.lock"))?;
        let waiting = Instant::now();
        loop {
            match ownership.try_lock_exclusive() {
                Ok(()) => break,
                Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                    ensure!(
                        waiting.elapsed() < Duration::from_secs(10),
                        "previous hsm daemon has not exited"
                    );
                    thread::sleep(Duration::from_millis(20));
                }
                Err(e) => return Err(e.into()),
            }
        }
        drop(ownership);
        private_directory(&self.store)?;
        let log = OpenOptions::new()
            .create(true)
            .append(true)
            .mode(0o600)
            .open(self.store.join("daemon.log"))?;
        let mut command = Command::new(&self.executable);
        command
            .args(["--socket"])
            .arg(&self.socket)
            .arg("--store")
            .arg(&self.store)
            .arg("--cache-mb")
            .arg(self.cache_mb.to_string())
            .arg("--build-mb")
            .arg(self.build_mb.to_string())
            .arg("--keep-mb")
            .arg(self.keep_mb.to_string())
            .arg("--idle-minutes")
            .arg(self.idle_minutes.to_string())
            .arg("daemon")
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(log);
        // Detach from the caller's terminal/session. setsid is async-signal-safe
        // and the pre-exec callback allocates nothing.
        unsafe {
            command.pre_exec(|| {
                if libc::setsid() == -1 {
                    return Err(std::io::Error::last_os_error());
                }
                Ok(())
            });
        }
        // Validate inherited descriptors and mark the originals CLOEXEC before detaching. The
        // service must not pin an initiating caller's lease for the service's whole lifetime.
        let _caller = hsm_run_slots::inherited()?;
        hsm_run_slots::detach(&mut command);
        ipc::spawn(&mut command).context("start hsm daemon")?;
        let start = Instant::now();
        while start.elapsed() < Duration::from_secs(10) {
            if let Ok(p) = ping() {
                self.compatible(&p)?;
                return Ok(());
            }
            thread::sleep(Duration::from_millis(20));
        }
        bail!(
            "daemon did not start; see {}",
            self.store.join("daemon.log").display()
        )
    }
}

fn serve(client: &Client) -> Result<()> {
    let parent = client
        .socket
        .parent()
        .context("socket needs a parent directory")?;
    fs::create_dir_all(parent)?;
    let lock = OpenOptions::new()
        .create(true)
        .truncate(false)
        .read(true)
        .write(true)
        .mode(0o600)
        .open(client.socket.with_extension("daemon.lock"))?;
    lock.try_lock_exclusive()
        .context("an hsm daemon already owns this socket")?;
    if client.socket.exists() {
        fs::remove_file(&client.socket)?;
    }
    let listener = UnixListener::bind(&client.socket)?;
    fs::set_permissions(&client.socket, fs::Permissions::from_mode(0o600))?;
    let mut store = store::Store::new(client.cache_mb)?;
    let builds = Arc::new(build::Builder::new(&client.store, client.build_mb)?);
    let build = build_id();
    let configuration = client.configuration();
    eprintln!(
        "hsm: pid {} listening at {}",
        std::process::id(),
        client.socket.display()
    );
    let idle = Duration::from_secs_f64(client.idle_minutes * 60.0);
    let mut last = Instant::now();
    loop {
        // A part run answers on its own thread, so while one is going the loop looks again every
        // few seconds for the moment the daemon has gone quiet.
        let (asks, since) = builds.busy();
        let wait = if asks > 0 {
            Duration::from_secs(5)
        } else {
            idle.saturating_sub(last.elapsed().min(since))
        };
        if client.idle_minutes > 0.0 && !pending(&listener, wait)? {
            let (asks, since) = builds.busy();
            if asks > 0 || last.elapsed().min(since) < idle {
                continue;
            }
            // The socket goes first, so a new caller starts a fresh daemon; whoever connected
            // before it went is still answered.
            fs::remove_file(&client.socket)?;
            listener.set_nonblocking(true)?;
            while let Ok((stream, _)) = listener.accept() {
                answer(stream, &mut store, &builds, &build, &configuration, &client.socket)?;
            }
            builds.wait_idle();
            if let Err(e) = builds.prune(client.keep_mb.saturating_mul(1 << 20)) {
                eprintln!("hsm: pruning kept part runs: {e:#}");
            }
            eprintln!(
                "hsm: pid {} exiting after {} idle minutes",
                std::process::id(),
                client.idle_minutes
            );
            return Ok(());
        }
        let (stream, _) = listener.accept()?;
        if answer(stream, &mut store, &builds, &build, &configuration, &client.socket)? {
            break;
        }
        last = Instant::now();
    }
    // A replacement may start at once: it waits on the socket and this lock, not on the part runs
    // still finishing here, whose callers are answered before this process exits.
    fs::remove_file(&client.socket)?;
    drop(listener);
    drop(lock);
    builds.wait_idle();
    Ok(())
}

/// Wait up to `timeout` for a caller; true when one is waiting.
fn pending(listener: &UnixListener, timeout: Duration) -> Result<bool> {
    let mut fd = libc::pollfd {
        fd: listener.as_raw_fd(),
        events: libc::POLLIN,
        revents: 0,
    };
    let ms = timeout.as_millis().min(i32::MAX as u128) as i32;
    loop {
        // poll reads one descriptor this process owns and writes only `revents`.
        let n = unsafe { libc::poll(&mut fd, 1, ms) };
        if n >= 0 {
            return Ok(n > 0);
        }
        let e = std::io::Error::last_os_error();
        if e.kind() != std::io::ErrorKind::Interrupted {
            return Err(e.into());
        }
    }
}

/// Answer one caller; true when it asked the service to stop. A part run is answered on a thread
/// of its own, so the queries behind it are not held up while it waits its turn and runs.
fn answer(
    stream: UnixStream,
    store: &mut store::Store,
    builds: &Arc<build::Builder>,
    build: &str,
    configuration: &Value,
    socket: &Path,
) -> Result<bool> {
    // An accepted socket inherits a non-blocking listener's mode on macOS.
    stream.set_nonblocking(false)?;
    stream.set_read_timeout(Some(Duration::from_secs(5)))?;
    let started = Instant::now();
    let mut stopping = false;
    let received = ipc::receive(&stream, 4 * 1024 * 1024, Duration::from_secs(5));
    let mut incoming = None;
    let request = received.and_then(|(mut value, fds)| {
        let wire = value.as_object_mut().and_then(|o| o.remove("_lease"));
        if let Some(wire) = wire { incoming = Some(Lease::from_wire(serde_json::from_value(wire)?, fds)?); }
        else { ensure!(fds.is_empty(), "ancillary descriptors have no lease metadata"); }
        Ok(serde_json::from_value::<Request>(value)?)
    });
    let request = match request {
        Ok(Request { query: Query::Run { workspace, root, krate, name, args }, .. }) => {
            let entered = builds.enter();
            thread::spawn(move || {
                reply(stream, entered.answer(build::Ask { workspace, root, krate, name, args }, incoming), started);
            });
            return Ok(false);
        }
        Ok(Request { query: Query::Generate { workspace, target, output, python }, .. }) => {
            let entered = builds.enter();
            let socket = socket.to_path_buf();
            thread::spawn(move || {
                reply(stream, entered.generate(build::Generate { workspace, target, output, python }, &socket, incoming), started);
            });
            return Ok(false);
        }
        Ok(Request { query: Query::Render { root, job, list }, .. }) => {
            let entered = builds.enter();
            thread::spawn(move || {
                let response = (|| {
                    // This worker waits before entering the renderer mutex. The accept loop
                    // remains free for an RPC from a parent that already holds a lease.
                    let _lease = hsm_run_slots::acquire("hsm:render", incoming, false)?;
                    render::execute(&root, &job, list)
                })();
                reply(stream, response, started);
                drop(entered);
            });
            return Ok(false);
        }
        other => other,
    };
    drop(incoming);
    let response = request.and_then(|request| {
        stopping = matches!(request.query, Query::Shutdown);
        let identifies_service = matches!(request.query, Query::Ping | Query::Status);
        let mut result = service::execute(store, builds, request, build)?;
        if identifies_service {
            result["configuration"] = configuration.clone();
        }
        Ok(result)
    });
    reply(stream, response, started);
    Ok(stopping)
}

fn reply(mut stream: UnixStream, response: Result<Value>, started: Instant) {
    let elapsed_ms = started.elapsed().as_secs_f64() * 1000.0;
    let response = match response {
        Ok(result) => json!({"ok": true, "result": result, "elapsed_ms": elapsed_ms}),
        Err(e) => json!({"ok": false, "error": format!("{e:#}"), "elapsed_ms": elapsed_ms}),
    };
    // A disconnected caller does not stop the shared service.
    if serde_json::to_writer(&mut stream, &response).is_ok() {
        let _ = stream.write_all(b"\n");
    }
}

fn triple(v: Vec<f64>) -> Result<[f64; 3]> {
    v.try_into()
        .map_err(|_| anyhow::anyhow!("expected three coordinates"))
}

fn run() -> Result<bool> {
    let args = Args::parse();
    if matches!(args.command, Action::Daemon | Action::Mcp) {
        hsm_run_slots::clear_inherited_for_service()?;
    }
    let cwd = std::env::current_dir()?;
    let root = args
        .root
        .unwrap_or_else(|| {
            cwd.ancestors()
                .find(|p| p.join(".git").exists())
                .unwrap_or(&cwd)
                .to_path_buf()
        })
        .canonicalize()?;
    let store = match args.store {
        Some(path) => path,
        None => cache_dir()?,
    };
    let store = if store.is_absolute() {
        store
    } else {
        cwd.join(store)
    };
    let store = store_path(&store)?;
    let socket = args.socket
        .or_else(|| std::env::var_os("HSM_SOCKET").map(PathBuf::from))
        .unwrap_or_else(|| default_socket(&configuration(&store, args.cache_mb, args.build_mb, args.keep_mb)));
    if socket.parent() == Some(runtime_dir().as_path()) {
        private_directory(&runtime_dir())?;
    }
    let socket = if socket.is_absolute() { socket } else { cwd.join(socket) };
    let client = Client {
        // Installations retain each build at an immutable path. Resolve the command's symlink
        // now, so this client can restart its own daemon after a later installation.
        executable: std::env::current_exe()?.canonicalize()?,
        socket,
        store,
        root,
        scene: args.scene,
        cache_mb: args.cache_mb,
        build_mb: args.build_mb,
        keep_mb: args.keep_mb,
        idle_minutes: args.idle_minutes,
    };
    ensure!(
        client.idle_minutes.is_finite() && client.idle_minutes >= 0.0,
        "--idle-minutes must be a nonnegative number"
    );
    let query = match args.command {
        Action::Endpoint => {
            println!("{}", serde_json::to_string_pretty(&json!({
                "build_id": build_id(), "socket": client.socket, "executable": client.executable,
                "configuration": client.configuration(), "run_slots": 1
            }))?);
            return Ok(true);
        }
        Action::Daemon => {
            serve(&client)?;
            return Ok(true);
        }
        Action::Mcp => {
            mcp::serve(&client)?;
            return Ok(true);
        }
        Action::Stop => {
            if !client.socket.exists() {
                println!("{{\"ok\":true,\"running\":false}}");
                return Ok(true);
            }
            let response = send(&client.socket, &control(Query::Shutdown))?;
            println!("{}", serde_json::to_string_pretty(&response)?);
            return Ok(response["ok"] == true);
        }
        Action::Render(args) => return render::run(&client, args),
        Action::Generate { target, output, python } => Query::Generate { workspace: client.root.clone(), target, output, python },
        Action::Status => Query::Status,
        Action::Where { pattern } => Query::Where { pattern },
        Action::Gap { a, b } => Query::Gap { a, b },
        Action::Overlap { a, b } => Query::Overlap { a, b },
        Action::Move {
            part,
            by,
            against,
            min_volume,
        } => Query::Move {
            part,
            by: triple(by)?,
            against,
            min_volume,
        },
        Action::Section {
            part,
            normal,
            offset,
        } => Query::Section {
            part,
            normal: triple(normal)?,
            offset,
        },
        Action::Ray {
            origin,
            direction,
            max_distance,
        } => Query::Ray {
            origin: triple(origin)?,
            direction: triple(direction)?,
            max_distance,
        },
        Action::Request { json: input } => {
            let mut request: Request = serde_json::from_str(&input)?;
            if !request.query.needs_scene() {
                // Control, render and part requests name their own inputs.
            } else if request.scene.as_os_str().is_empty() {
                request.scene = scene_path(&client.root, &client.scene);
            } else if request.scene.is_relative() {
                request.scene = client.root.join(request.scene);
            }
            let response = client.call(&request)?;
            println!("{}", serde_json::to_string_pretty(&response)?);
            return Ok(response["ok"] == true);
        }
    };
    let response = client.call(&Request {
        scene: scene_path(&client.root, &client.scene),
        query,
    })?;
    println!("{}", serde_json::to_string_pretty(&response)?);
    Ok(response["ok"] == true)
}

fn main() {
    match run() {
        Ok(true) => (),
        Ok(false) => std::process::exit(1),
        Err(e) => {
            eprintln!("hsm: {e:#}");
            std::process::exit(1);
        }
    }
}
