use super::*;
use std::{
    collections::BTreeMap,
    os::unix::net::UnixListener,
    sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
    },
};
#[derive(Default)]
struct State {
    run: Option<Part>,
    cad: Option<Part>,
    compiler: Option<Part>,
    checked: bool,
    brokers: BTreeMap<u64, Broker>,
    active: Option<u64>,
    next: u64,
}
struct Part {
    held: Vec<Held>,
    inherited: bool,
}
struct Broker {
    path: PathBuf,
    token: String,
    stop: Arc<AtomicBool>,
}
static ENVIRONMENT: OnceLock<Mutex<BTreeMap<String, String>>> = OnceLock::new();
fn environment() -> &'static Mutex<BTreeMap<String, String>> {
    ENVIRONMENT.get_or_init(|| {
        Mutex::new(
            env::vars()
                .filter(|(k, _)| {
                    [RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, PROFILE_ENV].contains(&k.as_str())
                })
                .collect(),
        )
    })
}
pub fn refresh_environment(value: &Value) {
    if let Some(values) = value.as_object() {
        let mut current = environment().lock().unwrap();
        for name in [RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, PROFILE_ENV] {
            if let Some(value) = values.get(name).and_then(Value::as_str) {
                current.insert(name.into(), value.into());
            } else {
                current.remove(name);
            }
        }
    }
}
fn env_value(name: &str) -> Option<String> {
    environment().lock().unwrap().get(name).cloned()
}
static STATE: Mutex<State> = Mutex::new(State {
    run: None,
    cad: None,
    compiler: None,
    checked: false,
    brokers: BTreeMap::new(),
    active: None,
    next: 0,
});
fn entries(part: Option<&Part>) -> Value {
    part.map(|p|json!({"entries":p.held.iter().map(|h|{let mut v=json!({"fd":h.file.as_raw_fd(),"token":h.token});if let Some(slot)=h.slot{v["slot"]=json!(slot);}v}).collect::<Vec<_>>(),"inherited":p.inherited})).unwrap_or(Value::Null)
}
fn valid_entry(value: &Value, kind: &str) -> bool {
    let check = (|| -> Result<()> {
        let fd = value["fd"].as_i64().context("fd")?;
        ensure!(fd >= 3 && fd <= i32::MAX as i64, "auxiliary descriptor");
        let slot = if kind == "run" {
            Some(value["slot"].as_u64().context("slot")? as usize)
        } else {
            None
        };
        let token = text(&value["token"])?;
        let _ = validate(duplicate_raw(fd as i32)?, slot, token.to_owned(), kind)?;
        Ok(())
    })();
    check.is_ok()
}
fn env_part(kind: &str) -> Option<Part> {
    (move || -> Result<Part> {
        let name = match kind {
            "run" => RUN_ENV,
            "cad" => CAD_ENV,
            _ => COMPILER_ENV,
        };
        let raw: Value = serde_json::from_str(&env_value(name).context("lease environment")?)?;
        ensure!(raw["v"] == 1, "lease version");
        let values = if kind == "run" {
            raw["fds"].as_array().context("run entries")?.clone()
        } else {
            vec![raw]
        };
        ensure!(!values.is_empty(), "lease entries");
        let mut seen = std::collections::BTreeSet::new();
        for value in &values {
            ensure!(valid_entry(value, kind), "lease descriptor");
            if kind == "run" {
                ensure!(seen.insert(value["slot"].as_u64()), "duplicate slot");
            }
        }
        for value in &values {
            cloexec(value["fd"].as_i64().unwrap() as i32)?;
        }
        let held = values
            .into_iter()
            .map(|value| Held {
                file: unsafe { File::from_raw_fd(value["fd"].as_i64().unwrap() as i32) },
                slot: if kind == "run" {
                    Some(value["slot"].as_u64().unwrap() as usize)
                } else {
                    None
                },
                token: value["token"].as_str().unwrap().into(),
            })
            .collect();
        Ok(Part {
            held,
            inherited: true,
        })
    })()
    .ok()
}
fn mark_originals() {
    for (kind, name) in [
        ("run", RUN_ENV),
        ("cad", CAD_ENV),
        ("compiler", COMPILER_ENV),
    ] {
        if let Some(raw) = env_value(name).and_then(|v| serde_json::from_str::<Value>(&v).ok()) {
            let values = if kind == "run" {
                raw["fds"].as_array().cloned().unwrap_or_default()
            } else {
                vec![raw]
            };
            for value in values {
                if valid_entry(&value, kind) {
                    let _ = cloexec(value["fd"].as_i64().unwrap() as i32);
                }
            }
        }
    }
}
impl State {
    fn part(&self, kind: &str) -> Option<&Part> {
        match kind {
            "run" => self.run.as_ref(),
            "cad" => self.cad.as_ref(),
            _ => self.compiler.as_ref(),
        }
    }
    fn put(&mut self, kind: &str, part: Option<Part>) {
        match kind {
            "run" => self.run = part,
            "cad" => self.cad = part,
            _ => self.compiler = part,
        }
    }
    fn current(&mut self, kind: &str) {
        if self.part(kind).is_none() {
            self.put(kind, env_part(kind));
            if self.part(kind).is_none() && !self.checked {
                let _ = self.from_broker();
            }
        }
    }
    fn from_broker(&mut self) -> Result<bool> {
        let result = (|| -> Result<(Value, Vec<OwnedFd>)> {
            let raw: Value =
                serde_json::from_str(&env_value(BROKER_ENV).context("broker environment")?)?;
            let path = Path::new(text(&raw["path"])?);
            if self
                .active
                .and_then(|id| self.brokers.get(&id))
                .is_some_and(|b| b.path == path)
            {
                self.checked = true;
                return Ok((json!({"ok":false}), vec![]));
            }
            ensure!(
                path.parent().context("broker parent")?.canonicalize()?
                    == directory()?.canonicalize()?,
                "broker directory"
            );
            let owner: Value = serde_json::from_slice(&fs::read(path.with_extension("json"))?)?;
            mark_originals();
            let peer = UnixStream::connect(path)?;
            peer.set_read_timeout(Some(Duration::from_secs(1)))?;
            ipc::send(&peer, &json!({"v":1,"token":owner["token"]}), &[])?;
            ipc::receive(&peer, 16384, Duration::from_secs(1))
        })();
        let Ok((reply, fds)) = result else {
            return Ok(false);
        };
        if reply["ok"] != true {
            return Ok(false);
        }
        let raw = fds
            .into_iter()
            .map(IntoRawFd::into_raw_fd)
            .collect::<Vec<_>>();
        let ok = self.adopt(&reply["_lease"], raw)?;
        Ok(ok)
    }
    fn adopt(&mut self, metadata: &Value, raw: Vec<i32>) -> Result<bool> {
        let mut seen = std::collections::BTreeSet::new();
        if raw
            .iter()
            .any(|&fd| fd < 0 || !seen.insert(fd) || unsafe { libc::fcntl(fd, libc::F_GETFD) } < 0)
        {
            for fd in raw.into_iter().collect::<std::collections::BTreeSet<_>>() {
                if fd >= 0 {
                    unsafe { libc::close(fd) };
                }
            }
            return Ok(false);
        }
        let mut owned = raw
            .iter()
            .map(|&fd| unsafe { OwnedFd::from_raw_fd(fd) })
            .collect::<Vec<_>>();
        let result = (|| -> Result<(Vec<Value>, Option<Value>, Option<Value>)> {
            let slots = metadata["slots"].as_array().context("lease slots")?;
            let cad = metadata.get("cad").filter(|v| !v.is_null());
            let compiler = metadata.get("compiler").filter(|v| !v.is_null());
            ensure!(
                metadata["v"] == 1
                    && raw.len()
                        == slots.len()
                            + usize::from(cad.is_some())
                            + usize::from(compiler.is_some()),
                "lease descriptor count does not match"
            );
            let runs = slots
                .iter()
                .zip(&raw)
                .map(|(row, &fd)| json!({"slot":row["slot"],"token":row["token"],"fd":fd}))
                .collect::<Vec<_>>();
            let mut n = slots.len();
            let ce = cad.map(|v| {
                let out = json!({"fd":raw[n],"token":v["token"]});
                n += 1;
                out
            });
            let build = compiler.map(|v| json!({"fd":raw[n],"token":v["token"]}));
            ensure!(
                runs.iter().all(|e| valid_entry(e, "run"))
                    && ce.as_ref().is_none_or(|e| valid_entry(e, "cad"))
                    && build.as_ref().is_none_or(|e| valid_entry(e, "compiler")),
                "received descriptors are not held leases"
            );
            Ok((runs, ce, build))
        })();
        let Ok((runs, cad, compiler)) = result else {
            return Ok(false);
        };
        for fd in owned.drain(..) {
            let _ = fd.into_raw_fd();
        }
        for (kind, values) in [
            ("run", runs),
            ("cad", cad.into_iter().collect()),
            ("compiler", compiler.into_iter().collect()),
        ] {
            if !values.is_empty() {
                self.put(kind, None);
                self.put(
                    kind,
                    Some(Part {
                        held: values
                            .into_iter()
                            .map(|v| Held {
                                file: unsafe {
                                    File::from_raw_fd(v["fd"].as_i64().unwrap() as i32)
                                },
                                slot: if kind == "run" {
                                    Some(v["slot"].as_u64().unwrap() as usize)
                                } else {
                                    None
                                },
                                token: v["token"].as_str().unwrap().into(),
                            })
                            .collect(),
                        inherited: true,
                    }),
                );
            }
        }
        if let Some(profile) = metadata["profile"].as_str().filter(|v| !v.is_empty()) {
            setenv(PROFILE_ENV, Some(profile));
        }
        self.export();
        self.checked = true;
        Ok(true)
    }
    fn expects_parent(&self) -> bool {
        if [RUN_ENV, CAD_ENV, COMPILER_ENV]
            .iter()
            .any(|name| env_value(name).is_some_and(|v| !v.is_empty()))
        {
            return true;
        }
        if let Some(raw) = env_value(BROKER_ENV) {
            if raw.is_empty() {
                return false;
            }
            let path = serde_json::from_str::<Value>(&raw)
                .ok()
                .and_then(|v| v["path"].as_str().map(PathBuf::from));
            return self
                .active
                .and_then(|id| self.brokers.get(&id))
                .is_none_or(|b| Some(&b.path) != path.as_ref());
        }
        false
    }
    fn wire(&mut self) -> Result<(Option<Value>, Vec<i32>)> {
        if !self.checked {
            self.from_broker()?;
        }
        for kind in ["run", "cad", "compiler"] {
            self.current(kind);
        }
        let mut fds = Vec::new();
        let mut slots = Vec::new();
        if let Some(run) = &self.run {
            for h in &run.held {
                fds.push(h.file.as_raw_fd());
                slots.push(json!({"slot":h.slot,"token":h.token}));
            }
        }
        let cad = self.cad.as_ref().map(|part| {
            let h = &part.held[0];
            fds.push(h.file.as_raw_fd());
            json!({"token":h.token})
        });
        let compiler = self.compiler.as_ref().map(|part| {
            let h = &part.held[0];
            fds.push(h.file.as_raw_fd());
            json!({"token":h.token})
        });
        if fds.is_empty() {
            return Ok((None, fds));
        }
        Ok((
            Some(
                json!({"v":1,"slots":slots,"cad":cad,"compiler":compiler,"profile":env_value(PROFILE_ENV)}),
            ),
            fds,
        ))
    }
    fn export(&self) {
        for (kind, name) in [
            ("run", RUN_ENV),
            ("cad", CAD_ENV),
            ("compiler", COMPILER_ENV),
        ] {
            let data = entries(self.part(kind));
            let out = if kind == "run" {
                json!({"v":1,"fds":data["entries"]})
            } else {
                let mut e = data["entries"][0].clone();
                if e.is_object() {
                    e["v"] = json!(1);
                }
                e
            };
            if !data.is_null() {
                let raw = out.to_string();
                setenv(name, Some(&raw));
            }
        }
    }
}
fn setenv(name: &str, value: Option<&str>) {
    let mut values = environment().lock().unwrap();
    if let Some(v) = value {
        values.insert(name.into(), v.into());
    } else {
        values.remove(name);
    }
}
pub fn answer(value: Value) -> Result<Value> {
    let state = STATE.lock().unwrap();
    let mut environment = json!({});
    for name in [RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, PROFILE_ENV] {
        environment[name] = json!(env_value(name));
    }
    Ok(
        json!({"result":value,"leases":{"run":entries(state.run.as_ref()),"cad":entries(state.cad.as_ref()),"compiler":entries(state.compiler.as_ref())},"environment":environment,"checked":state.checked,"broker":state.active.and_then(|id|state.brokers.get(&id).map(|b|json!({"id":id,"path":b.path,"token":b.token})))}),
    )
}
pub fn current(kind: &str) -> bool {
    let mut s = STATE.lock().unwrap();
    s.current(kind);
    s.part(kind).is_some()
}
pub fn acquire_run(key: Option<&str>, timing: bool, callback: Host) -> Result<()> {
    {
        let mut s = STATE.lock().unwrap();
        s.current("run");
        if let Some(run) = &s.run {
            ensure!(
                !timing || run.held.len() >= capacity(),
                "timing: request timing at the logical root so it can reserve all slots"
            );
            return Ok(());
        }
        ensure!(
            !s.expects_parent(),
            "inheritance: the advertised parent lease or broker could not be validated; refusing a second logical run"
        );
    }
    let token = token()?;
    let mut waiting = None;
    loop {
        let gate = open(&directory()?.join("admission.lock"))?;
        gate.lock_exclusive()?;
        let mut free = Vec::new();
        let mut busy = std::collections::BTreeSet::new();
        let mut newest = 0;
        for slot in 0..capacity() {
            let file = open(&lock_path(Some(slot))?)?;
            match file.try_lock_exclusive() {
                Ok(()) => free.push(Held {
                    file,
                    slot: Some(slot),
                    token: token.clone(),
                }),
                Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                    let row = read_token(&file).unwrap_or(json!({}));
                    busy.insert(
                        row["token"]
                            .as_str()
                            .map(str::to_owned)
                            .unwrap_or(format!("unknown:{slot}")),
                    );
                    newest = newest.max(row["started_unix_ms"].as_u64().unwrap_or(0));
                }
                Err(e) => return Err(e.into()),
            }
        }
        let limit = count()?;
        let (level, swap) = pressure();
        let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_millis() as u64;
        let reason = if level == Some(defaults().critical_pressure_level)
            || swap.is_some_and(|v| v > defaults().max_swap_bytes)
        {
            Some(format!(
                "host pressure level={}, swap={} bytes",
                level.map(|v| v.to_string()).unwrap_or("None".into()),
                swap.map(|v| v.to_string()).unwrap_or("None".into())
            ))
        } else if timing && !busy.is_empty() {
            Some("all heavy-run slots for timing".into())
        } else if busy.len() >= limit {
            Some(format!(
                "capacity {limit} ({} active logical runs)",
                busy.len()
            ))
        } else if !busy.is_empty()
            && defaults().stagger_seconds - (now as f64 - newest as f64) / 1000. > 0.
        {
            Some("staggering concurrent logical starts".into())
        } else if free.is_empty() {
            Some("available heavy-run descriptor".into())
        } else {
            None
        };
        if let Some(reason) = reason {
            drop(free);
            drop(gate);
            if waiting.as_ref() != Some(&reason) {
                host(
                    callback,
                    json!({"call":"stderr","text":format!("[run] waiting: {reason}\n")}),
                )?;
                waiting = Some(reason);
            }
            thread::sleep(Duration::from_millis(100));
            continue;
        }
        if !timing {
            free.truncate(1);
        }
        for entry in &mut free {
            entry.file.set_len(0)?;
            entry.file.write_all(format!("{}\n",json!({"v":1,"kind":"run","token":token,"pid":std::process::id(),"key":key,"slot":entry.slot,"started_unix_ms":now})).as_bytes())?;
        }
        fs::write(
            directory()?.join("admission.json"),
            format!("{}\n", json!({"v":1,"last_start_unix_ms":now})),
        )?;
        let mut s = STATE.lock().unwrap();
        s.run = Some(Part {
            held: free,
            inherited: false,
        });
        if let Some(key) = key.filter(|v| !v.is_empty()) {
            setenv(PROFILE_ENV, Some(key));
        }
        s.export();
        return Ok(());
    }
}
pub fn acquire_aux(kind: &str) -> Result<()> {
    let mut s = STATE.lock().unwrap();
    s.current(kind);
    if s.part(kind).is_some() {
        return Ok(());
    }
    if kind == "cad" {
        s.current("compiler");
        ensure!(
            s.compiler.is_none(),
            "native CAD must be reserved before compiler; use --cad at the logical root"
        );
    }
    drop(s);
    let mut file = open(&auxiliary_path(kind)?)?;
    file.lock_exclusive()?;
    let token = token()?;
    file.set_len(0)?;
    file.write_all(
        format!(
            "{}\n",
            json!({"v":1,"kind":kind,"token":token,"pid":std::process::id()})
        )
        .as_bytes(),
    )?;
    let mut s = STATE.lock().unwrap();
    s.put(
        kind,
        Some(Part {
            held: vec![Held {
                file,
                slot: None,
                token,
            }],
            inherited: false,
        }),
    );
    s.export();
    Ok(())
}
pub fn release(cad_only: bool) {
    let mut s = STATE.lock().unwrap();
    if !cad_only {
        s.compiler = None;
        s.run = None;
        setenv(COMPILER_ENV, None);
        setenv(RUN_ENV, None);
    }
    s.cad = None;
    s.checked = false;
    setenv(CAD_ENV, None);
}
pub fn context() -> Result<Lease> {
    let mut s = STATE.lock().unwrap();
    for kind in ["run", "cad", "compiler"] {
        s.current(kind);
    }
    let duplicate = |h: &Held| {
        Ok(Held {
            file: h.file.try_clone()?,
            slot: h.slot,
            token: h.token.clone(),
        })
    };
    Ok(Lease {
        held: s
            .run
            .as_ref()
            .map(|p| p.held.iter().map(duplicate).collect::<Result<Vec<_>>>())
            .transpose()?
            .unwrap_or_default(),
        cad: s.cad.as_ref().map(|p| duplicate(&p.held[0])).transpose()?,
        compiler: s
            .compiler
            .as_ref()
            .map(|p| duplicate(&p.held[0]))
            .transpose()?,
        profile: env_value(PROFILE_ENV).unwrap_or_default(),
    })
}
pub fn pressure() -> (Option<i32>, Option<u64>) {
    #[cfg(target_os = "macos")]
    {
        let mut level: libc::c_int = 0;
        let mut size = std::mem::size_of_val(&level);
        let a = unsafe {
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
        let b = unsafe {
            libc::sysctlbyname(
                c"vm.swapusage".as_ptr(),
                (&mut swap as *mut libc::xsw_usage).cast(),
                &mut size,
                std::ptr::null_mut(),
                0,
            )
        };
        return ((a == 0).then_some(level), (b == 0).then_some(swap.xsu_used));
    }
    #[cfg(not(target_os = "macos"))]
    {
        (None, None)
    }
}
pub fn broker_config(workspace: &Path) -> Result<String> {
    let path = workspace.canonicalize().unwrap_or(workspace.into());
    let name = format!("{:x}", Sha256::digest(path.to_string_lossy().as_bytes()));
    Ok(json!({"path":directory()?.join(format!("w.{}.sock",&name[..16]))}).to_string())
}
pub fn new_broker(config: Option<&str>) -> Result<Value> {
    let path = if let Some(config) = config {
        let data: Value = serde_json::from_str(config)?;
        PathBuf::from(text(&data["path"])?)
    } else {
        directory()?.join(format!("b.{}.sock", std::process::id()))
    };
    let token = token()?;
    let _ = fs::remove_file(&path);
    let listener = UnixListener::bind(&path)?;
    listener.set_nonblocking(true)?;
    fs::write(
        path.with_extension("json"),
        serde_json::to_vec(&json!({"v":1,"token":token,"pid":std::process::id()}))?,
    )?;
    let stop = Arc::new(AtomicBool::new(false));
    let flag = stop.clone();
    let mut s = STATE.lock().unwrap();
    s.next += 1;
    let id = s.next;
    s.brokers.insert(
        id,
        Broker {
            path: path.clone(),
            token: token.clone(),
            stop,
        },
    );
    s.active = Some(id);
    drop(s);
    let result = json!({"id":id,"path":path,"token":token});
    thread::spawn(move || {
        while !flag.load(Ordering::Relaxed) {
            let (peer, _) = match listener.accept() {
                Ok(v) => v,
                Err(_) => {
                    thread::sleep(Duration::from_millis(20));
                    continue;
                }
            };
            let work = (|| -> Result<()> {
                peer.set_read_timeout(Some(Duration::from_secs(1)))?;
                let (asked, incoming) = ipc::receive(&peer, 4096, Duration::from_secs(1))?;
                ensure!(
                    incoming.is_empty(),
                    "a broker request carries no lease descriptors"
                );
                let mut s = STATE.lock().unwrap();
                let (metadata, descriptors) = s.wire()?;
                let asked_token = asked["token"].as_str().unwrap_or("").as_bytes();
                let expected = token.as_bytes();
                let mut difference = asked_token.len() ^ expected.len();
                for index in 0..asked_token.len().max(expected.len()) {
                    difference |= usize::from(
                        asked_token.get(index).copied().unwrap_or(0)
                            ^ expected.get(index).copied().unwrap_or(0),
                    );
                }
                let ok = asked["v"] == 1 && difference == 0;
                let descriptors = if ok {
                    descriptors
                        .into_iter()
                        .map(duplicate_raw)
                        .collect::<Result<Vec<_>>>()?
                } else {
                    vec![]
                };
                drop(s);
                ipc::send(
                    &peer,
                    &json!({"ok":ok&&metadata.is_some(),"_lease":if ok{metadata}else{None}}),
                    &descriptors.iter().map(AsFd::as_fd).collect::<Vec<_>>(),
                )
            })();
            let _ = work;
        }
    });
    Ok(result)
}
pub fn close_broker(id: u64) -> Result<()> {
    let mut s = STATE.lock().unwrap();
    if let Some(b) = s.brokers.remove(&id) {
        b.stop.store(true, Ordering::Relaxed);
        let _ = fs::remove_file(&b.path);
        let _ = fs::remove_file(b.path.with_extension("json"));
    }
    if s.active == Some(id) {
        s.active = None;
    }
    Ok(())
}
pub fn child_env(base: Option<&Value>, broker: bool) -> Result<Value> {
    let need = {
        let mut s = STATE.lock().unwrap();
        broker && !s.wire()?.1.is_empty() && s.active.is_none()
    };
    if need {
        new_broker(None)?;
    }
    let mut s = STATE.lock().unwrap();
    if broker {
        if let Some(b) = s.active.and_then(|id| s.brokers.get(&id)) {
            setenv(BROKER_ENV, Some(&json!({"path":b.path}).to_string()));
        }
    }
    let mut out = base
        .and_then(Value::as_object)
        .cloned()
        .unwrap_or_else(|| env::vars().map(|(k, v)| (k, json!(v))).collect());
    for name in [RUN_ENV, CAD_ENV, COMPILER_ENV, BROKER_ENV, PROFILE_ENV] {
        if let Some(v) = env_value(name) {
            out.insert(name.into(), json!(v));
        }
    }
    s.current("cad");
    if s.cad.is_some() {
        out.insert("HSM_NO_BUILD_LOCK".into(), json!("1"));
    } else {
        out.remove("HSM_NO_BUILD_LOCK");
    }
    Ok(json!(out))
}
pub fn request(op: &str, d: &Value, callback: Host) -> Result<Value> {
    let value = match op {
        "directory" => json!(directory()?),
        "defaults" => serde_json::from_str(include_str!("../../../run-slots.defaults.json"))?,
        "capacity" => json!(capacity()),
        "count" => json!(count()?),
        "set_count" => {
            let n = d["value"].as_u64().unwrap_or(0) as usize;
            ensure!(
                (1..=capacity()).contains(&n),
                "count must be an integer from 1 to {}",
                capacity()
            );
            let gate = open(&directory()?.join("admission.lock"))?;
            gate.lock_exclusive()?;
            let temporary = directory()?.join(format!(".count.{}", std::process::id()));
            fs::write(&temporary, format!("{n}\n"))?;
            fs::rename(temporary, directory()?.join("count"))?;
            Value::Null
        }
        "path" => {
            let kind = text(&d["kind"])?;
            json!(if ["cad", "compiler"].contains(&kind) {
                auxiliary_path(kind)?
            } else {
                directory()?.join(format!("slot.{}.lock", d["slot"]))
            })
        }
        "read_fd" => {
            let fd = d["fd"].as_i64().context("fd")? as i32;
            json!(
                duplicate_raw(fd)
                    .and_then(|f| read_token(&f))
                    .unwrap_or(json!({}))
            )
        }
        "write_fd" => {
            let fd = d["fd"].as_i64().context("fd")? as i32;
            let bytes = serde_json::to_vec(&d["value"])?;
            let mut text = bytes;
            text.push(b'\n');
            ensure!(
                unsafe { libc::ftruncate(fd, 0) } == 0,
                "truncate lease record"
            );
            ensure!(
                unsafe { libc::pwrite(fd, text.as_ptr().cast(), text.len(), 0) }
                    == text.len() as isize,
                "write lease record"
            );
            Value::Null
        }
        "open" => json!(open(Path::new(text(&d["path"])?))?.into_raw_fd()),
        "valid" => json!(valid_entry(&d["entry"], text(&d["kind"])?)),
        "env_lease" => {
            let kind = text(&d["kind"])?;
            let mut s = STATE.lock().unwrap();
            s.current(kind);
            entries(s.part(kind))
        }
        "current" => json!(current(text(&d["kind"])?)),
        "expects_parent" => json!(STATE.lock().unwrap().expects_parent()),
        "from_broker" => json!(STATE.lock().unwrap().from_broker()?),
        "wire" => {
            let mut s = STATE.lock().unwrap();
            let (a, b) = s.wire()?;
            json!([a, b])
        }
        "adopt" => {
            let fds = serde_json::from_value(d["fds"].clone())?;
            json!(STATE.lock().unwrap().adopt(&d["metadata"], fds)?)
        }
        "acquire" => {
            acquire_run(
                d["key"].as_str(),
                d["timing"].as_bool().unwrap_or(false),
                callback,
            )?;
            Value::Null
        }
        "acquire_cad" => {
            acquire_aux("cad")?;
            Value::Null
        }
        "acquire_compiler" => {
            acquire_aux("compiler")?;
            Value::Null
        }
        "release" => {
            release(false);
            Value::Null
        }
        "release_cad" => {
            release(true);
            Value::Null
        }
        "export" => {
            let kind = text(&d["kind"])?;
            let value = if kind == "run" {
                json!({"v":1,"fds":d["entries"]})
            } else {
                let mut value = d["entries"][0].clone();
                value["v"] = json!(1);
                value
            };
            setenv(
                match kind {
                    "run" => RUN_ENV,
                    "cad" => CAD_ENV,
                    _ => COMPILER_ENV,
                },
                Some(&value.to_string()),
            );
            Value::Null
        }
        "lease_close" => {
            let kind = text(&d["kind"])?;
            let mut s = STATE.lock().unwrap();
            let values = d["entries"].as_array().context("lease entries")?;
            let matches = s.part(kind).is_some_and(|p| {
                p.held
                    .iter()
                    .map(|h| h.file.as_raw_fd())
                    .eq(values.iter().map(|e| e["fd"].as_i64().unwrap_or(-1) as i32))
            });
            if matches {
                s.put(kind, None);
            } else {
                for e in values {
                    unsafe { libc::close(e["fd"].as_i64().context("lease fd")? as i32) };
                }
            }
            Value::Null
        }
        "close_fds" => {
            for fd in d["fds"].as_array().context("fds")? {
                unsafe { libc::close(fd.as_i64().context("fd")? as i32) };
            }
            Value::Null
        }
        "pressure" => json!(pressure()),
        "broker_config" => json!(broker_config(Path::new(text(&d["workspace"])?))?),
        "broker_new" => new_broker(d["config"].as_str())?,
        "broker_close" => {
            close_broker(d["id"].as_u64().context("broker id")?)?;
            Value::Null
        }
        "child_env" => child_env(
            d.get("environment").filter(|v| !v.is_null()),
            d["broker"].as_bool().unwrap_or(true),
        )?,
        "command" => {
            let mut out = vec![
                d["python"].clone(),
                json!(Path::new(text(&d["root"])?).join("tools/run.py")),
            ];
            if let Some(key) = d["key"].as_str().filter(|v| !v.is_empty()) {
                out.extend([json!("--key"), json!(key)]);
            }
            out.push(json!("--"));
            out.extend(d["argv"].as_array().context("argv")?.clone());
            json!(out)
        }
        _ => bail!("unknown run-slot operation {op}"),
    };
    answer(value)
}
