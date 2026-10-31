mod mcp;
mod service;
mod store;

use anyhow::{Context, Result, bail, ensure};
use clap::{Parser, Subcommand};
use fs2::FileExt;
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
    path::{Path, PathBuf},
    process::{Command, Stdio},
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
    /// Send a JSON request using the socket protocol.
    Request {
        json: String,
    },
}

pub struct Client {
    socket: PathBuf,
    store: PathBuf,
    root: PathBuf,
    scene: String,
    cache_mb: u64,
    idle_minutes: f64,
}

fn build_id() -> String {
    let mut h = Sha256::new();
    h.update(include_str!("main.rs"));
    h.update(include_str!("service.rs"));
    h.update(include_str!("store.rs"));
    h.update(include_str!("mcp.rs"));
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
    stream.set_read_timeout(Some(Duration::from_secs(300)))?;
    serde_json::to_writer(&mut stream, request)?;
    stream.write_all(b"\n")?;
    read_message(&mut stream, 64 * 1024 * 1024)
}

fn control(query: Query) -> Request {
    Request {
        scene: PathBuf::new(),
        query,
    }
}

impl Client {
    fn compatible(&self, response: &Value) -> bool {
        response["result"]["build_id"] == build_id()
            && response["result"]["cache"]["cache_budget_bytes"]
                == json!(self.cache_mb.saturating_mul(1048576))
    }

    pub fn call(&self, request: &Request) -> Result<Value> {
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
        if ping().ok().is_some_and(|p| self.compatible(&p)) {
            return Ok(());
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
            if self.compatible(&p) {
                return Ok(());
            }
            send(&self.socket, &control(Query::Shutdown))?;
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
        let mut command = Command::new(std::env::current_exe()?);
        command
            .args(["--socket"])
            .arg(&self.socket)
            .arg("--store")
            .arg(&self.store)
            .arg("--cache-mb")
            .arg(self.cache_mb.to_string())
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
        command.spawn().context("start hsm daemon")?;
        let start = Instant::now();
        while start.elapsed() < Duration::from_secs(10) {
            if let Ok(p) = ping() {
                ensure!(
                    self.compatible(&p),
                    "socket serves another hsm build or configuration"
                );
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
    let build = build_id();
    eprintln!(
        "hsm: pid {} listening at {}",
        std::process::id(),
        client.socket.display()
    );
    let idle = Duration::from_secs_f64(client.idle_minutes * 60.0);
    let mut last = Instant::now();
    loop {
        if client.idle_minutes > 0.0 && !pending(&listener, idle.saturating_sub(last.elapsed()))? {
            // The socket goes first, so a new caller starts a fresh daemon; whoever connected
            // before it went is still answered.
            fs::remove_file(&client.socket)?;
            listener.set_nonblocking(true)?;
            while let Ok((stream, _)) = listener.accept() {
                answer(stream, &mut store, &build)?;
            }
            eprintln!(
                "hsm: pid {} exiting after {} idle minutes",
                std::process::id(),
                client.idle_minutes
            );
            return Ok(());
        }
        let (stream, _) = listener.accept()?;
        if answer(stream, &mut store, &build)? {
            break;
        }
        last = Instant::now();
    }
    fs::remove_file(&client.socket)?;
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

/// Answer one caller; true when it asked the service to stop.
fn answer(mut stream: UnixStream, store: &mut store::Store, build: &str) -> Result<bool> {
    // An accepted socket inherits a non-blocking listener's mode on macOS.
    stream.set_nonblocking(false)?;
    stream.set_read_timeout(Some(Duration::from_secs(5)))?;
    let started = Instant::now();
    let mut stopping = false;
    let response = (|| -> Result<Value> {
        let request: Request = serde_json::from_value(read_message(&mut stream, 4 * 1024 * 1024)?)?;
        stopping = matches!(request.query, Query::Shutdown);
        service::execute(store, request, build)
    })();
    let response = match response {
        Ok(result) => {
            json!({"ok": true, "result": result, "elapsed_ms": started.elapsed().as_secs_f64() * 1000.0})
        }
        Err(e) => {
            json!({"ok": false, "error": format!("{e:#}"), "elapsed_ms": started.elapsed().as_secs_f64() * 1000.0})
        }
    };
    // A disconnected caller does not stop the shared service.
    if serde_json::to_writer(&mut stream, &response).is_ok() {
        let _ = stream.write_all(b"\n");
    }
    Ok(stopping)
}

fn triple(v: Vec<f64>) -> Result<[f64; 3]> {
    v.try_into()
        .map_err(|_| anyhow::anyhow!("expected three coordinates"))
}

fn run() -> Result<bool> {
    let args = Args::parse();
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
    let socket = args
        .socket
        .or_else(|| std::env::var_os("HSM_SOCKET").map(PathBuf::from))
        .unwrap_or_else(|| runtime_dir().join("engine.sock"));
    if socket.parent() == Some(runtime_dir().as_path()) {
        private_directory(&runtime_dir())?;
    }
    let socket = if socket.is_absolute() {
        socket
    } else {
        cwd.join(socket)
    };
    let store = match args.store {
        Some(path) => path,
        None => cache_dir()?,
    };
    let store = if store.is_absolute() {
        store
    } else {
        cwd.join(store)
    };
    let client = Client {
        socket,
        store,
        root,
        scene: args.scene,
        cache_mb: args.cache_mb,
        idle_minutes: args.idle_minutes,
    };
    ensure!(
        client.idle_minutes.is_finite() && client.idle_minutes >= 0.0,
        "--idle-minutes must be a nonnegative number"
    );
    let query = match args.command {
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
            if request.scene.as_os_str().is_empty() {
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
