//! CAD coordination retains shared lease ownership and follows matching active commands.
use super::*;
static ME: Mutex<Value> = Mutex::new(Value::Null);
fn read(path: &Path) -> Option<Value> {
    fs::read(path)
        .ok()
        .and_then(|v| serde_json::from_slice(&v).ok())
}
fn alive(pid: i64) -> bool {
    pid > 0 && pid <= i32::MAX as i64 && unsafe { libc::kill(pid as i32, 0) } == 0
}
fn asked(name: &str) -> bool {
    !matches!(
        env::var(name)
            .unwrap_or_default()
            .trim()
            .to_lowercase()
            .as_str(),
        "" | "0" | "no" | "false" | "off"
    )
}
fn who(holder: &Value) -> String {
    if holder.is_null()
        || holder == &json!(false)
        || holder == &json!(0)
        || holder.as_str() == Some("")
        || holder.as_array().is_some_and(Vec::is_empty)
        || holder.as_object().is_some_and(serde_json::Map::is_empty)
    {
        "a newer build".into()
    } else {
        format!(
            "{} ({})",
            holder["source"].as_str().unwrap_or("?"),
            holder["script"].as_str().unwrap_or("?")
        )
    }
}
fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}
fn age(holder: &Value) -> String {
    let Some(started) = holder["started"].as_f64().filter(|v| *v != 0.) else {
        return "age unknown".into();
    };
    let secs = (now() - started).max(0.);
    if secs < 90. {
        format!("{secs:.0}s in")
    } else {
        format!("{:.0}m{:02.0}s in", (secs / 60.).floor(), secs % 60.)
    }
}
fn newest(root: &Path) -> f64 {
    fn walk(path: &Path, out: &mut f64) {
        let Ok(rows) = fs::read_dir(path) else { return };
        for row in rows.flatten() {
            let Ok(kind) = row.file_type() else { continue };
            let name = row.file_name();
            let name = name.to_string_lossy();
            if kind.is_dir() {
                if !name.starts_with('.')
                    && !matches!(
                        name.as_ref(),
                        "__pycache__" | ".pio" | "node_modules" | ".git" | "cad-venv" | "pcb-venv"
                    )
                {
                    walk(&row.path(), out);
                }
            } else if name.ends_with(".py") {
                if let Ok(time) = fs::metadata(row.path()).and_then(|m| m.modified()) {
                    if let Ok(time) = time.duration_since(UNIX_EPOCH) {
                        *out = out.max(time.as_secs_f64());
                    }
                }
            }
        }
    }
    let mut out = 0.;
    walk(&root.join("hardware"), &mut out);
    out
}
fn fresh(holder: &Value, root: &Path) -> bool {
    holder["started"]
        .as_f64()
        .filter(|v| *v != 0.)
        .is_some_and(|started| {
            newest(holder["root"].as_str().map(Path::new).unwrap_or(root)) <= started
        })
}
fn holder_active(holder: &Value) -> bool {
    if holder["run_slots"].as_bool().unwrap_or(false)
        || holder["run_slots"].as_i64().is_some_and(|v| v != 0)
    {
        let Ok(file) = open(&directory().unwrap_or_default().join("cad.lock")) else {
            return false;
        };
        return file
            .try_lock_exclusive()
            .is_err_and(|e| e.kind() == std::io::ErrorKind::WouldBlock);
    }
    alive(holder["pid"].as_i64().unwrap_or(-1))
}
pub fn record(dir: &Path, code: i32) {
    let me = ME.lock().unwrap();
    let Some(pid) = me["pid"].as_i64() else {
        return;
    };
    let path = dir.join(format!("build.{pid}.result"));
    if !path.exists() {
        let _ = fs::write(path, json!({"code":code}).to_string());
    }
}
fn sweep(dir: &Path) {
    let Ok(rows) = fs::read_dir(dir) else { return };
    for row in rows.flatten() {
        let name = row.file_name();
        let name = name.to_string_lossy();
        let is_log = name.starts_with("build.") && name.ends_with(".log");
        let unlocked = name.starts_with("unlocked.") && name.ends_with(".json");
        if !is_log && !unlocked {
            continue;
        }
        let Some(pid) = name.split('.').nth(1).and_then(|s| s.parse::<i64>().ok()) else {
            continue;
        };
        if !alive(pid) {
            let _ = fs::remove_file(row.path());
            if is_log {
                let _ = fs::remove_file(dir.join(format!("build.{pid}.result")));
            }
        }
    }
}
fn emit(stream: &str, message: String) -> Result<()> {
    match stream {
        "stdout" => {
            print!("{message}");
            std::io::stdout().flush()?;
        }
        "stderr" => {
            eprint!("{message}");
            std::io::stderr().flush()?;
        }
        _ => unreachable!("CAD log stream"),
    }
    Ok(())
}
fn attach(dir: &Path, holder: &Value) -> Result<Option<i32>> {
    let pid = holder["pid"].as_i64().context("build pid")?;
    let log = dir.join(format!("build.{pid}.log"));
    let result = dir.join(format!("build.{pid}.result"));
    emit(
        "stderr",
        format!(
            "[build] a {} build of this script is already running (pid {pid}) — following it instead of starting a second one\n",
            holder["source"].as_str().unwrap_or("?")
        ),
    )?;
    let mut pos = 0usize;
    loop {
        if let Ok(bytes) = fs::read(&log) {
            if bytes.len() > pos {
                emit(
                    "stdout",
                    String::from_utf8_lossy(&bytes[pos..]).replace("\r\n", "\n"),
                )?;
                pos = bytes.len();
            }
        }
        if let Some(code) = read(&result) {
            return Ok(code["code"].as_i64().map(|value| value as i32));
        }
        if !holder_active(holder) {
            thread::sleep(Duration::from_millis(50));
            return Ok(read(&result)
                .and_then(|value| value["code"].as_i64())
                .map(|value| value as i32));
        }
        thread::sleep(Duration::from_millis(50));
    }
}
pub fn wait_legacy(dir: &Path) -> Result<()> {
    if slots::current("cad") {
        return Ok(());
    }
    let mut announced = None;
    loop {
        let Some(holder) = read(&dir.join("build.json")) else {
            return Ok(());
        };
        let pid = holder["pid"].as_i64().unwrap_or(-1);
        if holder["run_slots"].as_i64().unwrap_or(0) != 0
            || holder["run_slots"] == true
            || pid == std::process::id() as i64
            || !alive(pid)
        {
            return Ok(());
        }
        if announced != Some(pid) {
            emit(
                "stderr",
                format!("[build] waiting for legacy native CAD pid {pid} before admission\n"),
            )?;
            announced = Some(pid);
        }
        thread::sleep(Duration::from_millis(50));
    }
}
pub fn acquire(script: &str, root: &Path) -> Result<Option<i32>> {
    if !ME.lock().unwrap().is_null() {
        return Ok(None);
    }
    let dir = env::temp_dir().join("hsm-cad-lock");
    if !slots::current("run") {
        wait_legacy(&dir)?;
    }
    slots::acquire_run(Some(script), false)?;
    if slots::current("cad") {
        return Ok(None);
    }
    let source = env::var("HSM_BUILD_SOURCE")
        .ok()
        .filter(|value| !value.is_empty())
        .unwrap_or("manual".into());
    fs::create_dir_all(&dir)?;
    let chosen = root.to_path_buf();
    let chosen = chosen.canonicalize().unwrap_or(chosen);
    let identity = json!({"pid":std::process::id(),"source":source,"script":script,"root":chosen,"started":now(),"run_slots":1,"protected":asked("HSM_BUILD_LOCK_PROTECT")});
    let mut announced = None;
    loop {
        if let Some(previous) = read(&dir.join("build.json")) {
            let pid = previous["pid"].as_i64().unwrap_or(-1);
            if pid != std::process::id() as i64 && holder_active(&previous) {
                if previous["script"] == script
                    && previous["root"] == identity["root"]
                    && env::var("HSM_NO_BUILD_ATTACH").map_or(true, |v| v.is_empty())
                    && fresh(&previous, root)
                {
                    if let Some(code) = attach(&dir, &previous)? {
                        return Ok(Some(code));
                    }
                    continue;
                }
                if previous["run_slots"].as_i64().unwrap_or(0) == 0 && previous["run_slots"] != true
                {
                    if announced != Some(pid) {
                        emit(
                            "stderr",
                            format!(
                                "[build] waiting for native CAD pid {pid} ({}, {})\n",
                                who(&previous),
                                age(&previous)
                            ),
                        )?;
                        announced = Some(pid);
                    }
                    thread::sleep(Duration::from_millis(50));
                    continue;
                }
            }
        }
        slots::acquire_aux("cad")?;
        if let Some(previous) = read(&dir.join("build.json")) {
            let pid = previous["pid"].as_i64().unwrap_or(-1);
            if previous["run_slots"].as_i64().unwrap_or(0) == 0
                && previous["run_slots"] != true
                && pid != std::process::id() as i64
                && alive(pid)
            {
                slots::release(true);
                continue;
            }
        }
        break;
    }
    *ME.lock().unwrap() = identity.clone();
    let temporary = dir.join(format!(".build.{}.json", std::process::id()));
    fs::write(&temporary, identity.to_string())?;
    fs::rename(temporary, dir.join("build.json"))?;
    sweep(&dir);
    let _ = File::create(dir.join(format!("build.{}.log", std::process::id())));
    Ok(None)
}
pub fn release(dir: &Path) {
    record(dir, 0);
    let me = ME.lock().unwrap().clone();
    if let Some(current) = read(&dir.join("build.json")) {
        if !me.is_null() && current["pid"] == me["pid"] {
            let _ = fs::remove_file(dir.join("build.json"));
            let _ = fs::remove_file(dir.join("build.by.json"));
        }
    }
    *ME.lock().unwrap() = Value::Null;
}
