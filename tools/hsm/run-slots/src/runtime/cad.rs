use super::*;
static ME: Mutex<Value> = Mutex::new(Value::Null);
fn lock_dir(d: &Value) -> PathBuf {
    d["lock_dir"]
        .as_str()
        .map(PathBuf::from)
        .unwrap_or_else(|| env::temp_dir().join("hsm-cad-lock"))
}
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
fn record(dir: &Path, code: &Value) {
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
fn live(dir: &Path, exclude: Option<i64>) -> Vec<Value> {
    let mut out = BTreeMap::new();
    if let Some(row) = read(&dir.join("build.json")) {
        if let Some(pid) = row["pid"].as_i64().filter(|&pid| alive(pid)) {
            out.insert(pid, row);
        }
    }
    if let Ok(rows) = fs::read_dir(dir) {
        for row in rows.flatten() {
            let name = row.file_name();
            let name = name.to_string_lossy();
            if name.starts_with("unlocked.") && name.ends_with(".json") {
                if let Some(value) = read(&row.path()) {
                    if let Some(pid) = value["pid"].as_i64().filter(|&pid| alive(pid)) {
                        out.insert(pid, value);
                    }
                }
            }
        }
    }
    if let Some(exclude) = exclude {
        out.remove(&exclude);
    }
    let mut rows = out.into_values().collect::<Vec<_>>();
    rows.sort_by(|a, b| {
        a["started"]
            .as_f64()
            .unwrap_or(0.)
            .total_cmp(&b["started"].as_f64().unwrap_or(0.))
    });
    rows
}
fn emit(callback: Host, stream: &str, message: String) -> Result<()> {
    host(callback, json!({"call":stream,"text":message}))?;
    Ok(())
}
fn attach(dir: &Path, holder: &Value, callback: Host) -> Result<Option<Value>> {
    let pid = holder["pid"].as_i64().context("build pid")?;
    let log = dir.join(format!("build.{pid}.log"));
    let result = dir.join(format!("build.{pid}.result"));
    emit(
        callback,
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
                    callback,
                    "stdout",
                    String::from_utf8_lossy(&bytes[pos..]).replace("\r\n", "\n"),
                )?;
                pos = bytes.len();
            }
        }
        if let Some(code) = read(&result) {
            return Ok(code.get("code").cloned().filter(|v| !v.is_null()));
        }
        if !holder_active(holder) {
            thread::sleep(Duration::from_millis(50));
            return Ok(read(&result)
                .and_then(|v| v.get("code").cloned())
                .filter(|v| !v.is_null()));
        }
        thread::sleep(Duration::from_millis(50));
    }
}
pub fn wait_legacy(dir: &Path, callback: Host) -> Result<()> {
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
                callback,
                "stderr",
                format!("[build] waiting for legacy native CAD pid {pid} before admission\n"),
            )?;
            announced = Some(pid);
        }
        thread::sleep(Duration::from_millis(50));
    }
}
pub fn acquire(d: &Value, root: &Path, callback: Host) -> Result<Value> {
    if !ME.lock().unwrap().is_null() {
        return Ok(json!({"identity":ME.lock().unwrap().clone()}));
    }
    let dir = lock_dir(d);
    if !slots::current("run") {
        wait_legacy(&dir, callback)?;
    }
    let script = text(&d["script"])?;
    slots::acquire_run(Some(script), false, callback)?;
    if slots::current("cad") {
        return Ok(json!({"identity":null}));
    }
    let source = d["source"]
        .as_str()
        .filter(|v| !v.is_empty())
        .map(str::to_owned)
        .or_else(|| env::var("HSM_BUILD_SOURCE").ok().filter(|v| !v.is_empty()))
        .unwrap_or("manual".into());
    fs::create_dir_all(&dir)?;
    let chosen = d["workspace"]
        .as_str()
        .map(PathBuf::from)
        .unwrap_or(root.into());
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
                    if let Some(code) = attach(&dir, &previous, callback)? {
                        return Ok(json!({"exit":code}));
                    }
                    continue;
                }
                if previous["run_slots"].as_i64().unwrap_or(0) == 0 && previous["run_slots"] != true
                {
                    if announced != Some(pid) {
                        emit(
                            callback,
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
    Ok(json!({"identity":identity,"tee":dir.join(format!("build.{}.log",std::process::id()))}))
}
pub fn release(dir: &Path) {
    record(dir, &json!(0));
    let me = ME.lock().unwrap().clone();
    if let Some(current) = read(&dir.join("build.json")) {
        if !me.is_null() && current["pid"] == me["pid"] {
            let _ = fs::remove_file(dir.join("build.json"));
            let _ = fs::remove_file(dir.join("build.by.json"));
        }
    }
    *ME.lock().unwrap() = Value::Null;
}
pub fn request(op: &str, d: &Value, root: &Path, callback: Host) -> Result<Value> {
    let dir = lock_dir(d);
    let value = match op {
        "cad_constants" => json!({"lock_dir":dir,"grace":5.,"poll":0.05,"wait":900.}),
        "cad_path" => {
            let pid = d["pid"].as_i64().context("build pid")?;
            let name = match text(&d["kind"])? {
                "unlocked" => format!("unlocked.{pid}.json"),
                "log" => format!("build.{pid}.log"),
                "result" => format!("build.{pid}.result"),
                _ => bail!("unknown CAD record path"),
            };
            json!(dir.join(name))
        }
        "cad_asked" => json!(asked(text(&d["name"])?)),
        "cad_read" => json!(read(Path::new(text(&d["path"])?))),
        "cad_alive" => json!(alive(d["pid"].as_i64().unwrap_or(-1))),
        "cad_newest" => json!(newest(
            d["workspace"].as_str().map(Path::new).unwrap_or(root)
        )),
        "cad_fresh" => json!(fresh(&d["holder"], root)),
        "cad_deliberate" => json!(
            !d["holder"]["source"]
                .as_str()
                .unwrap_or("")
                .starts_with("dev-server")
        ),
        "cad_who" => json!(who(&d["holder"])),
        "cad_age" => json!(age(&d["holder"])),
        "cad_attach" => json!(attach(&dir, &d["holder"], callback)?),
        "cad_record" => {
            record(&dir, &d["code"]);
            Value::Null
        }
        "cad_sweep" => {
            sweep(&dir);
            Value::Null
        }
        "cad_live" => json!(live(&dir, d["exclude"].as_i64())),
        "cad_drop_unlocked" => {
            let _ = fs::remove_file(dir.join(format!("unlocked.{}.json", d["pid"])));
            Value::Null
        }
        "cad_running_unlocked" => {
            let pid = std::process::id();
            let row = json!({"pid":pid,"source":d["source"],"script":d["script"],"started":now()});
            let written = fs::create_dir_all(&dir)
                .and_then(|_| {
                    sweep(&dir);
                    fs::write(dir.join(format!("unlocked.{pid}.json")), row.to_string())
                })
                .is_ok();
            let others = live(&dir, Some(pid as i64));
            if !others.is_empty() {
                let who = others
                    .iter()
                    .map(|o| format!("{} pid {}", who(o), o["pid"]))
                    .collect::<Vec<_>>()
                    .join(", ");
                emit(
                    callback,
                    "stderr",
                    format!(
                        "[build] running unlocked (HSM_NO_BUILD_LOCK) beside {} live build{}: {who} — this build supersedes none of them, none of them can follow it, and all of them are on the same cores\n",
                        others.len(),
                        if others.len() > 1 { "s" } else { "" }
                    ),
                )?;
            }
            json!(written)
        }
        "cad_exit_record" => {
            let value = if d["code"].is_string() {
                json!(1)
            } else if d["code"].is_null() || d["code"] == false || d["code"] == 0 {
                json!(0)
            } else {
                d["code"].clone()
            };
            record(&dir, &value);
            Value::Null
        }
        "cad_signal" => {
            let me = ME.lock().unwrap().clone();
            let by = read(&dir.join("build.by.json")).unwrap_or(Value::Null);
            let why = if !by.is_null() && !me.is_null() && by["victim"] == me["pid"] {
                format!("was superseded by {}", who(&by))
            } else {
                "was terminated (not by a newer build)".into()
            };
            emit(
                callback,
                "stderr",
                format!("[build] this build ({}) {why} — stopping\n", who(&me)),
            )?;
            record(&dir, &json!(143));
            json!(143)
        }
        "cad_release_legacy" => {
            release(&dir);
            Value::Null
        }
        "cad_release" => {
            slots::release(true);
            release(&dir);
            Value::Null
        }
        "cad_holder_active" => json!(holder_active(&d["holder"])),
        "cad_wait_legacy" => {
            wait_legacy(&dir, callback)?;
            Value::Null
        }
        "cad_acquire" => acquire(d, root, callback)?,
        _ => bail!("unknown CAD runtime operation {op}"),
    };
    slots::answer(value)
}
