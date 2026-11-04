use super::*;
use std::{
    net::{TcpStream, ToSocketAddrs},
    os::unix::{fs::MetadataExt, process::ExitStatusExt},
    time::Instant,
};
fn resolved(path: &Path) -> PathBuf {
    if let Ok(path) = path.canonicalize() {
        return path;
    }
    let full = if path.is_absolute() {
        path.to_owned()
    } else {
        env::current_dir().unwrap_or_default().join(path)
    };
    let mut out = PathBuf::new();
    for part in full.components() {
        match part {
            std::path::Component::ParentDir => {
                out.pop();
            }
            std::path::Component::CurDir => (),
            part => out.push(part.as_os_str()),
        }
    }
    out
}
pub fn script_key(command: &[String], cwd: &Path) -> String {
    let program = Path::new(&command[0])
        .file_name()
        .unwrap_or_default()
        .to_string_lossy();
    if matches!(program.as_ref(), "bazel" | "bazelisk") {
        let verb = command
            .iter()
            .skip(1)
            .find(|v| !v.starts_with('-'))
            .map(String::as_str)
            .unwrap_or("build");
        let mut targets = command
            .iter()
            .skip(1)
            .filter(|v| v.starts_with("//") || v.starts_with('@'))
            .cloned()
            .collect::<Vec<_>>();
        targets.sort();
        let key = format!("bazel:{verb}:{}", targets.join(","));
        if key.chars().count() <= 512 {
            return key;
        }
        let digest = format!("{:x}", Sha256::digest(key.as_bytes()));
        let sample = targets
            .iter()
            .take(3)
            .cloned()
            .collect::<Vec<_>>()
            .join(",")
            .chars()
            .take(384)
            .collect::<String>();
        return format!(
            "bazel:{}:{} targets:{sample}...:{}",
            verb.chars().take(32).collect::<String>(),
            targets.len(),
            &digest[..16]
        );
    }
    for arg in command {
        if [".py", ".js", ".mjs", ".sh", ".ts", ".tsx"]
            .iter()
            .any(|ext| arg.ends_with(ext))
        {
            let path = resolved(Path::new(arg));
            return path
                .strip_prefix(resolved(cwd))
                .map(|v| v.to_string_lossy().into_owned())
                .unwrap_or_else(|_| {
                    Path::new(arg)
                        .file_name()
                        .unwrap_or_default()
                        .to_string_lossy()
                        .into_owned()
                });
        }
    }
    if matches!(program.as_ref(), "cargo" | "rustc") {
        let mut chosen = Vec::new();
        for flag in ["--manifest-path", "--bin", "-p", "--package"] {
            if let Some(i) = command.iter().position(|v| v == flag) {
                if let Some(value) = command.get(i + 1) {
                    let value = if flag == "--manifest-path" {
                        let path = resolved(Path::new(value));
                        path.strip_prefix(resolved(cwd))
                            .map(|p| p.to_string_lossy().into_owned())
                            .unwrap_or_else(|_| {
                                Path::new(value)
                                    .file_name()
                                    .unwrap_or_default()
                                    .to_string_lossy()
                                    .into_owned()
                            })
                    } else {
                        value.clone()
                    };
                    chosen.extend([flag.to_owned(), value]);
                }
            }
        }
        return format!("{program}:{}", chosen.join(":"));
    }
    program.into_owned()
}
pub fn limit_jobs(command: &[String], jobs: usize) -> Vec<String> {
    let split = command
        .iter()
        .position(|v| v == "--")
        .unwrap_or(command.len());
    let mut kept = Vec::new();
    let mut skip = false;
    for arg in &command[..split] {
        if skip {
            skip = false;
        } else if arg == "--jobs" || arg == "-j" {
            skip = true;
        } else if !arg.starts_with("--jobs=")
            && !(arg.starts_with("-j")
                && arg.len() > 2
                && arg[2..].bytes().all(|b| b.is_ascii_digit()))
        {
            kept.push(arg.clone());
        }
    }
    kept.push(format!("--jobs={jobs}"));
    kept.extend_from_slice(&command[split..]);
    kept
}
pub fn workspace_root() -> PathBuf {
    let here = resolved(&env::current_dir().unwrap_or_default());
    for root in here.ancestors() {
        if [
            ".bazelversion",
            "MODULE.bazel",
            "WORKSPACE",
            "WORKSPACE.bazel",
        ]
        .iter()
        .any(|name| root.join(name).exists())
        {
            return root.into();
        }
    }
    here
}
fn http(
    host: &str,
    port: u16,
    method: &str,
    route: &str,
    body: Option<&Value>,
    token: Option<&str>,
    timeout: f64,
) -> Result<(u16, Vec<u8>)> {
    let address = (host, port)
        .to_socket_addrs()?
        .next()
        .context("local viewer address")?;
    let mut peer = TcpStream::connect_timeout(&address, Duration::from_secs_f64(timeout))?;
    peer.set_read_timeout(Some(Duration::from_secs_f64(timeout)))?;
    peer.set_write_timeout(Some(Duration::from_secs_f64(timeout)))?;
    let bytes = body
        .map(serde_json::to_vec)
        .transpose()?
        .unwrap_or_default();
    write!(
        peer,
        "{method} {route} HTTP/1.1\r\nHost: {host}:{port}\r\nConnection: close\r\n"
    )?;
    if body.is_some() {
        write!(
            peer,
            "Content-Type: application/json\r\nContent-Length: {}\r\n",
            bytes.len()
        )?;
    }
    if let Some(token) = token {
        write!(peer, "X-HSM-Notify: {token}\r\n")?;
    }
    peer.write_all(b"\r\n")?;
    peer.write_all(&bytes)?;
    let mut reply = Vec::new();
    peer.read_to_end(&mut reply)?;
    let split = reply
        .windows(4)
        .position(|v| v == b"\r\n\r\n")
        .context("viewer HTTP header")?;
    let header = String::from_utf8_lossy(&reply[..split]);
    let status = header
        .lines()
        .next()
        .and_then(|v| v.split_whitespace().nth(1))
        .context("viewer status")?
        .parse()?;
    let mut payload = reply[split + 4..].to_vec();
    if header
        .lines()
        .any(|v| v.to_lowercase().starts_with("transfer-encoding: chunked"))
    {
        let mut decoded = Vec::new();
        let mut at = 0;
        loop {
            let n = payload[at..]
                .windows(2)
                .position(|v| v == b"\r\n")
                .context("viewer chunk length")?
                + at;
            let size = usize::from_str_radix(
                std::str::from_utf8(&payload[at..n])?
                    .split(';')
                    .next()
                    .unwrap_or(""),
                16,
            )?;
            at = n + 2;
            if size == 0 {
                break;
            }
            ensure!(at + size + 2 <= payload.len(), "viewer chunk range");
            decoded.extend_from_slice(&payload[at..at + size]);
            at += size + 2;
        }
        payload = decoded;
    }
    Ok((status, payload))
}
pub fn viewer_producer(command: &[String], root: &Path) -> Option<Value> {
    (move || -> Result<Value> {
        ensure!(
            !env::var("HSM_VIEWER_PRODUCER").is_ok_and(|v| !v.is_empty()),
            "nested producer"
        );
        ensure!(
            Path::new(&command[0])
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .starts_with("python"),
            "Python producer"
        );
        let script = command
            .iter()
            .skip(1)
            .find(|v| v.ends_with(".py"))
            .context("producer script")?;
        let script = resolved(Path::new(script));
        ensure!(
            script.starts_with(root.join("hardware")),
            "hardware producer"
        );
        let mut candidates = vec![
            ("127.0.0.1".to_owned(), 3000),
            ("127.0.0.1".to_owned(), 3001),
        ];
        if let Some(url) = env::var("HSM_VIEWER_URL").ok().filter(|v| !v.is_empty()) {
            let rest = url.strip_prefix("http://").context("local HTTP viewer")?;
            let authority = rest.split('/').next().unwrap_or("");
            let (host, port) = if let Some(rest) = authority.strip_prefix('[') {
                let (end, port) = rest.split_once(']').context("IPv6 viewer")?;
                (
                    end.to_owned(),
                    port.strip_prefix(':')
                        .map(str::parse)
                        .transpose()?
                        .unwrap_or(80),
                )
            } else if let Some((host, port)) = authority.rsplit_once(':') {
                (host.into(), port.parse()?)
            } else {
                (authority.into(), 80)
            };
            ensure!(
                ["localhost", "127.0.0.1", "::1"].contains(&host.as_str()),
                "local viewer"
            );
            candidates = vec![(host, port)];
        }
        for (host, port) in candidates {
            let Ok((200, bytes)) = http(&host, port, "GET", "/api/hsm", None, None, 0.05) else {
                continue;
            };
            let Ok(data) = serde_json::from_slice::<Value>(&bytes) else {
                continue;
            };
            if data["root"] == root.to_string_lossy().as_ref() && data["notify"].is_string() {
                let paths = fs::read(root.join("tools/bazel/graph.json"))
                    .ok()
                    .and_then(|v| serde_json::from_slice::<Value>(&v).ok())
                    .and_then(|v| {
                        v[script.strip_prefix(root).ok()?.to_string_lossy().as_ref()]["writes"]
                            .as_array()
                            .cloned()
                    })
                    .unwrap_or_default()
                    .into_iter()
                    .filter_map(|v| v.as_str().map(|p| root.join(p)))
                    .collect::<Vec<_>>();
                return Ok(json!([
                    host,
                    port,
                    data["notify"],
                    root,
                    script.parent(),
                    paths
                ]));
            }
        }
        bail!("no local viewer")
    })()
    .ok()
}
pub fn viewer_snapshot(producer: &Value) -> Result<Value> {
    if producer.is_null() {
        return Ok(json!({}));
    }
    let root = Path::new(text(&producer[3])?);
    let directory = Path::new(text(&producer[4])?);
    let mut paths = producer[5]
        .as_array()
        .context("producer outputs")?
        .iter()
        .map(|v| text(v).map(PathBuf::from))
        .collect::<Result<std::collections::BTreeSet<_>>>()?;
    for row in fs::read_dir(directory)? {
        paths.insert(row?.path());
    }
    let mut out = json!({});
    for path in paths {
        let name = path.file_name().unwrap_or_default().to_string_lossy();
        if name.starts_with('.')
            || !path.starts_with(root.join("hardware"))
            || ![".step", ".step.mesh", ".glb", ".dxf", ".pdf", ".mmd"]
                .iter()
                .any(|ext| name.ends_with(ext))
        {
            continue;
        }
        if let Ok(stat) = path.metadata() {
            let modified = stat.modified()?.duration_since(UNIX_EPOCH)?.as_nanos() as u64;
            out[path.to_string_lossy().as_ref()] =
                json!([stat.dev(), stat.ino(), stat.len(), modified]);
        }
    }
    Ok(out)
}
pub fn viewer_completed(producer: &Value, before: &Value) -> Result<()> {
    if producer.is_null() {
        return Ok(());
    }
    let root = Path::new(text(&producer[3])?);
    let mut files = std::collections::BTreeSet::new();
    let snapshot = viewer_snapshot(producer)?;
    for (path, stamp) in snapshot.as_object().context("viewer snapshot")? {
        if before.get(path) != Some(stamp) {
            let name = Path::new(path)
                .strip_prefix(root.join("hardware"))?
                .to_string_lossy()
                .into_owned();
            files.insert(if name.ends_with(".step.mesh") {
                name.strip_suffix(".mesh").unwrap().into()
            } else {
                name
            });
        }
    }
    if !files.is_empty() {
        let _ = http(
            text(&producer[0])?,
            producer[1].as_u64().context("viewer port")? as u16,
            "POST",
            "/api/hsm/files-changed",
            Some(&json!({"root":root,"files":files})),
            Some(text(&producer[2])?),
            0.1,
        );
    }
    Ok(())
}
pub fn request(op: &str, d: &Value) -> Result<Value> {
    let command = || -> Result<Vec<String>> {
        serde_json::from_value(d["command"].clone()).map_err(Into::into)
    };
    Ok(match op {
        "runner_script_key" => json!(script_key(&command()?, &env::current_dir()?)),
        "runner_limit_jobs" => json!(limit_jobs(
            &command()?,
            d["jobs"].as_u64().unwrap_or(2) as usize
        )),
        "runner_workspace_root" => json!(workspace_root()),
        "runner_viewer_producer" => {
            json!(viewer_producer(&command()?, Path::new(text(&d["root"])?)))
        }
        "runner_viewer_snapshot" => viewer_snapshot(&d["producer"])?,
        "runner_viewer_completed" => {
            viewer_completed(&d["producer"], &d["before"])?;
            Value::Null
        }
        "runner_launcher" => json!(install::launcher(
            Path::new(text(&d["current"])?),
            d["legacy"].as_str().map(Path::new),
            &serde_json::from_value::<Vec<String>>(d["sockets"].clone())?
        )),
        _ => bail!("unknown runner operation {op}"),
    })
}
pub fn run(args: &[String]) -> Result<i32> {
    let mut count_arg = None;
    let mut timing = false;
    let mut cad_arg = false;
    let mut check = false;
    let mut key = None;
    let mut i = 0;
    let mut command = Vec::new();
    while i < args.len() {
        let arg = &args[i];
        match arg.as_str() {
            "--count" | "--key" => {
                i += 1;
                let value = args.get(i).context("usage: option requires a value")?;
                if arg == "--count" {
                    count_arg = Some(
                        value
                            .parse::<i64>()
                            .context("usage: invalid integer for --count")?,
                    );
                } else {
                    key = Some(value.clone());
                }
            }
            "--timing" => timing = true,
            "--cad" => cad_arg = true,
            "--check-inherited" => check = true,
            "--" => {
                command.extend_from_slice(&args[i + 1..]);
                break;
            }
            "-h" | "--help" => {
                println!(
                    "Run one heavy command under the host's shared admission policy.\n\nUsage: python3 tools/run.py [--count 1..4] [--timing] [--cad] [--key NAME] -- COMMAND..."
                );
                return Ok(0);
            }
            _ if arg.starts_with("--count=") => {
                count_arg = Some(
                    arg[8..]
                        .parse::<i64>()
                        .context("usage: invalid integer for --count")?,
                )
            }
            _ if arg.starts_with("--key=") => key = Some(arg[6..].into()),
            _ if arg.starts_with('-') => bail!("usage: unrecognized argument: {arg}"),
            _ => {
                command.extend_from_slice(&args[i..]);
                break;
            }
        }
        i += 1;
    }
    if let Some(value) = count_arg {
        slots::request("set_count", &json!({"value":value}), None)?;
        println!("{}: {value}", directory()?.join("count").display());
        return Ok(0);
    }
    if check {
        return Ok(if slots::current("run") { 0 } else { 1 });
    }
    ensure!(!command.is_empty(), "usage: name a command after --");
    let root = workspace_root();
    let key = key.unwrap_or_else(|| script_key(&command, &env::current_dir().unwrap_or_default()));
    let producer = viewer_producer(&command, &root).unwrap_or(Value::Null);
    let before = viewer_snapshot(&producer).unwrap_or(json!({}));
    let program = Path::new(&command[0])
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .into_owned();
    let bazel = ["bazel", "bazelisk"].contains(&program.as_str());
    let bazel_heavy = bazel
        && command
            .iter()
            .skip(1)
            .any(|v| ["build", "test", "run", "coverage"].contains(&v.as_str()));
    let cargo_heavy = program == "cargo"
        && command.iter().skip(1).any(|v| {
            ["build", "test", "run", "check", "bench", "install", "rustc"].contains(&v.as_str())
        });
    if bazel_heavy || cargo_heavy {
        command = limit_jobs(&command, 2);
    }
    let stable = if bazel {
        Some(slots::broker_config(&root)?)
    } else {
        None
    };
    let guard = if let Some(config) = &stable {
        let raw: Value = serde_json::from_str(config)?;
        let file = open(&Path::new(text(&raw["path"])?).with_extension("guard"))?;
        file.lock_exclusive()?;
        Some(file)
    } else {
        None
    };
    let cad_dir = env::temp_dir().join("hsm-cad-lock");
    if cad_arg || bazel_heavy {
        cad::wait_legacy(&cad_dir, None)?;
    }
    if let Err(error) = slots::acquire_run(Some(&key), timing, None) {
        let message = error.to_string();
        if let Some(message) = message
            .strip_prefix("timing: ")
            .or_else(|| message.strip_prefix("inheritance: "))
        {
            eprintln!("[run] {message}");
            return Ok(2);
        }
        return Err(error);
    }
    if cad_arg || bazel_heavy {
        let result = cad::acquire(&json!({"script":key,"workspace":root}), &root, None)?;
        if let Some(code) = result["exit"].as_i64() {
            return Ok(code as i32);
        }
        if let Some(path) = result["tee"].as_str() {
            let _ = File::create(path);
        }
    }
    if bazel_heavy || cargo_heavy {
        slots::acquire_aux("compiler")?;
    }
    let broker = slots::new_broker(stable.as_deref())?;
    let mut environment = slots::child_env(None, true)?
        .as_object()
        .cloned()
        .context("child environment")?;
    environment.insert("CARGO_BUILD_JOBS".into(), json!("2"));
    environment.insert("CMAKE_BUILD_PARALLEL_LEVEL".into(), json!("2"));
    if program.starts_with("python") {
        environment.insert("HSM_VIEWER_PRODUCER".into(), json!("1"));
    }
    if bazel {
        for name in [
            RUN_ENV,
            CAD_ENV,
            COMPILER_ENV,
            PROFILE_ENV,
            "HSM_NO_BUILD_LOCK",
        ] {
            environment.remove(name);
        }
    }
    let began = Instant::now();
    let mut child = Command::new(&command[0]);
    child.args(&command[1..]);
    child.env_clear().envs(
        environment
            .iter()
            .filter_map(|(k, v)| v.as_str().map(|v| (k, v))),
    );
    if !bazel {
        slots::context()?.apply(&mut child)?;
    }
    let child = match ipc::spawn(&mut child) {
        Ok(child) => child,
        Err(error) => {
            slots::close_broker(broker["id"].as_u64().unwrap())?;
            cad::request("cad_record", &json!({"code":1}), &root, None)?;
            cad::release(&cad_dir);
            slots::release(false);
            eprintln!("[run] {error}");
            return Ok(1);
        }
    };
    let mut status = 0;
    let mut usage: libc::rusage = unsafe { std::mem::zeroed() };
    loop {
        let result = unsafe { libc::wait4(child.id() as i32, &mut status, 0, &mut usage) };
        if result >= 0 {
            break;
        }
        let error = std::io::Error::last_os_error();
        if error.kind() != std::io::ErrorKind::Interrupted {
            return Err(error.into());
        }
    }
    let status = std::process::ExitStatus::from_raw(status);
    let code = status
        .code()
        .unwrap_or_else(|| 128 + status.signal().unwrap_or(1));
    if timing {
        let peak = usage.ru_maxrss as u64 * if cfg!(target_os = "macos") { 1 } else { 1024 };
        eprintln!(
            "{}",
            json!({"command_seconds":began.elapsed().as_secs_f64(),"peak_process_rss_bytes":peak})
        );
    }
    slots::close_broker(broker["id"].as_u64().unwrap())?;
    drop(guard);
    if code == 0 {
        let _ = viewer_completed(&producer, &before);
    }
    cad::request("cad_record", &json!({"code":code}), &root, None)?;
    cad::release(&cad_dir);
    slots::release(false);
    Ok(code)
}
