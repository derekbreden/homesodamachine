use super::*;
const MARKER: &str = "#!/bin/sh\n# hsm build launcher\n";
pub fn source_files() -> Vec<(&'static str, &'static str)> {
    vec![
        ("tools/hsm/run-slots/src/lib.rs", include_str!("../lib.rs")),
        ("tools/hsm/run-slots/src/ipc.rs", include_str!("../ipc.rs")),
        (
            "tools/hsm/run-slots/src/runtime.rs",
            include_str!("../runtime.rs"),
        ),
        (
            "tools/hsm/run-slots/src/runtime/slots.rs",
            include_str!("slots.rs"),
        ),
        (
            "tools/hsm/run-slots/src/runtime/cad.rs",
            include_str!("cad.rs"),
        ),
        (
            "tools/hsm/run-slots/src/runtime/runner.rs",
            include_str!("runner.rs"),
        ),
        (
            "tools/hsm/run-slots/src/runtime/install.rs",
            include_str!("install.rs"),
        ),
        (
            "tools/hsm/run-slots/src/main.rs",
            include_str!("../main.rs"),
        ),
        (
            "tools/hsm/run-slots/Cargo.toml",
            include_str!("../../Cargo.toml"),
        ),
        (
            "tools/hsm/run-native/Cargo.toml",
            include_str!("../../../run-native/Cargo.toml"),
        ),
        (
            "tools/hsm/run-native/src/lib.rs",
            include_str!("../../../run-native/src/lib.rs"),
        ),
        (
            "tools/hsm/run-slots.defaults.json",
            include_str!("../../../run-slots.defaults.json"),
        ),
    ]
}
fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}
pub fn source_id() -> String {
    let mut digest = Sha256::new();
    for (path, text) in source_files() {
        digest.update(path);
        digest.update(b"\0");
        digest.update(text);
    }
    format!("{:x}", digest.finalize())
}
fn library(dir: &Path) -> PathBuf {
    dir.join(format!(
        "{}hsm_run_native{}",
        env::consts::DLL_PREFIX,
        env::consts::DLL_SUFFIX
    ))
}
pub fn info(root: &Path) -> Result<Value> {
    let files = source_files();
    let matches = files
        .iter()
        .all(|(path, text)| fs::read(root.join(path)).is_ok_and(|bytes| bytes == text.as_bytes()));
    let exe = env::current_exe()?.canonicalize()?;
    let beside = library(exe.parent().context("runtime directory")?);
    let lib = if beside.is_file() {
        beside
    } else {
        library(&root.join("tools/hsm/target/release"))
    };
    Ok(
        json!({"abi":1,"source_id":source_id(),"source_match":matches,"executable":exe,"library":lib,"sources":files.into_iter().map(|(path,text)|(path,hash(text.as_bytes()))).collect::<BTreeMap<_,_>>()}),
    )
}
fn put(path: &Path, data: &[u8], mode: u32) -> Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let temp = path.with_file_name(format!(
        ".{}.{}",
        path.file_name().context("artifact name")?.to_string_lossy(),
        std::process::id()
    ));
    fs::write(&temp, data)?;
    fs::set_permissions(&temp, fs::Permissions::from_mode(mode))?;
    fs::rename(temp, path)?;
    Ok(())
}
pub fn prefix() -> PathBuf {
    #[allow(deprecated)]
    env::home_dir().unwrap_or_default().join(".local")
}
pub fn install_runtime(root: &Path, destination: &Path) -> Result<Value> {
    let current = info(root)?;
    ensure!(
        current["source_match"] == true,
        "runtime source changed; compile its current source before installation"
    );
    let runner = Path::new(text(&current["executable"])?);
    let lib = Path::new(text(&current["library"])?);
    let runner_bytes = fs::read(runner)?;
    let lib_bytes = fs::read(lib)?;
    let code = source_id();
    let artifact =
        hash(format!("{code}\n{}\n{}", hash(&runner_bytes), hash(&lib_bytes)).as_bytes());
    let dir = destination.join("lib/hsm/runtime").join(&artifact);
    let runner_out = dir.join("hsm-run");
    let lib_out = library(&dir);
    for (path, bytes) in [(&runner_out, &runner_bytes), (&lib_out, &lib_bytes)] {
        if !path.exists() {
            put(path, bytes, 0o555)?;
        } else {
            ensure!(
                fs::read(path)? == *bytes,
                "{} already holds a different artifact for this source",
                path.display()
            );
        }
    }
    let mut sources = current["sources"].clone();
    for path in [
        "hardware/scripts/_run_native.py",
        "hardware/scripts/_run_slots.py",
        "hardware/scripts/_run_lock.py",
    ] {
        if let Ok(bytes) = fs::read(root.join(path)) {
            sources[path] = json!(hash(&bytes));
        }
    }
    let receipt = json!({"schema":1,"abi":1,"source_id":code,"artifact_id":artifact,"source_sha256":sources,"root":root,"runner":runner_out,"library":lib_out,"runner_sha256":hash(&runner_bytes),"library_sha256":hash(&lib_bytes)});
    put(
        &dir.join("receipt.json"),
        (serde_json::to_string_pretty(&receipt)? + "\n").as_bytes(),
        0o644,
    )?;
    put(
        &destination.join("lib/hsm/runtime.json"),
        (serde_json::to_string_pretty(&receipt)? + "\n").as_bytes(),
        0o644,
    )?;
    put(
        &destination.join("bin/hsm-run"),
        launcher(&runner_out, None, &[]).as_bytes(),
        0o755,
    )?;
    Ok(receipt)
}

/// Rebuild the host runner and its adapter library under the existing compiler lease.
pub fn rebuild_runtime(root: &Path) -> Result<()> {
    slots::acquire_run(Some("hsm:runtime-bootstrap"), false, None)?;
    slots::acquire_aux("compiler")?;
    let cargo = env::var_os("CARGO")
        .map(PathBuf::from)
        .filter(|path| path.is_file())
        .or_else(|| {
            [
                PathBuf::from("/opt/homebrew/opt/rustup/bin/cargo"),
                prefix()
                    .parent()
                    .unwrap_or(Path::new("/"))
                    .join(".cargo/bin/cargo"),
            ]
            .into_iter()
            .find(|path| path.is_file())
        })
        .unwrap_or_else(|| PathBuf::from("cargo"));
    let mut cmd = Command::new(&cargo);
    cmd.args([
        "build",
        "--release",
        "--locked",
        "--jobs=2",
        "--manifest-path",
    ])
    .arg(root.join("tools/hsm/Cargo.toml"))
    .args(["-p", "hsm-run-slots", "-p", "hsm-run-native"])
    .current_dir(root)
    .env("CARGO_TARGET_DIR", root.join("tools/hsm/target"));
    if let Some(directory) = cargo.parent().filter(|p| !p.as_os_str().is_empty()) {
        let mut paths = vec![directory.to_path_buf()];
        paths.extend(env::split_paths(&env::var_os("PATH").unwrap_or_default()));
        cmd.env("PATH", env::join_paths(paths)?);
    }
    slots::context()?.apply(&mut cmd)?;
    ensure!(
        ipc::spawn(&mut cmd)?.wait()?.success(),
        "native runtime build failed"
    );
    let mut install = Command::new(root.join("tools/hsm/target/release/hsm-run"));
    install.arg("--install-runtime").arg(root);
    slots::context()?.apply(&mut install)?;
    ensure!(
        ipc::spawn(&mut install)?.wait()?.success(),
        "native runtime installation failed"
    );
    Ok(())
}

/// Run through the runner compiled from this checkout's host policy.
pub fn run_current(root: &Path, args: &[String]) -> Result<i32> {
    let current = info(root)?;
    if current["source_match"] == true {
        return runner::run(args);
    }
    let mut bootstrap = Command::new(env::current_exe()?);
    bootstrap.arg("--rebuild-runtime").arg(root);
    if let Some(lease) = crate::inherited()? {
        lease.apply(&mut bootstrap)?;
    }
    ensure!(
        ipc::spawn(&mut bootstrap)?.wait()?.success(),
        "native runtime refresh failed"
    );
    let mut fresh = Command::new(root.join("tools/hsm/target/release/hsm-run"));
    fresh.arg("--workspace").arg(root).args(args);
    if let Some(lease) = crate::inherited()? {
        lease.apply(&mut fresh)?;
    }
    let status = ipc::spawn(&mut fresh)?.wait()?;
    Ok(status.code().unwrap_or(1))
}

/// Install command artifacts without replacing an executable a running job still holds.
pub fn install_tools(root: &Path, destination: &Path, binaries: &[PathBuf]) -> Result<Value> {
    let mut installed = Vec::new();
    for binary in binaries {
        let binary = if binary.is_absolute() {
            binary.clone()
        } else {
            root.join(binary)
        };
        let binary = binary.canonicalize()?;
        let name = binary.file_name().context("tool name")?.to_string_lossy();
        ensure!(
            !name.is_empty()
                && name
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_'),
            "tool name {name}"
        );
        let bytes = fs::read(&binary)?;
        let digest = hash(&bytes);
        let artifact = destination
            .join("lib/hsm/tools")
            .join(&digest)
            .join(name.as_ref());
        if !artifact.exists() {
            put(&artifact, &bytes, 0o555)?;
        }
        let command = destination.join("bin").join(name.as_ref());
        put(&command, launcher(&artifact, None, &[]).as_bytes(), 0o755)?;
        installed
            .push(json!({"name":name,"sha256":digest,"executable":artifact,"command":command}));
    }
    Ok(json!({"tools":installed}))
}
pub fn bootstrap(root: &Path) -> Result<Value> {
    slots::acquire_run(Some("hsm:runtime-bootstrap"), false, None)?;
    slots::acquire_aux("compiler")?;
    let cargo = env::var_os("CARGO")
        .map(PathBuf::from)
        .or_else(|| {
            let p = PathBuf::from(env::var_os("HOME").unwrap_or_default()).join(".cargo/bin/cargo");
            p.is_file().then_some(p)
        })
        .unwrap_or_else(|| PathBuf::from("/opt/homebrew/opt/rustup/bin/cargo"));
    let mut command = Command::new(&cargo);
    command
        .args([
            "build",
            "--release",
            "--locked",
            "--lib",
            "--jobs=2",
            "--manifest-path",
        ])
        .arg(root.join("tools/hsm/run-native/Cargo.toml"))
        .current_dir(root)
        .env("CARGO_TARGET_DIR", root.join("tools/hsm/target"))
        .env("CARGO_BUILD_JOBS", "2");
    if let Some(parent) = cargo.parent() {
        let path = env::var_os("PATH").unwrap_or_default();
        let mut paths = vec![parent.to_path_buf()];
        paths.extend(env::split_paths(&path));
        command.env("PATH", env::join_paths(paths)?);
    }
    slots::context()?.apply(&mut command)?;
    ensure!(
        ipc::spawn(&mut command)?.wait()?.success(),
        "native runtime library build failed"
    );
    install_runtime(root, &prefix())
}
fn endpoint(binary: &Path) -> Result<Value> {
    let out = Command::new(binary).arg("endpoint").output()?;
    ensure!(out.status.success(), "{} endpoint failed", binary.display());
    Ok(serde_json::from_slice(&out.stdout)?)
}
fn quote(text: &str) -> String {
    if !text.is_empty()
        && text
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"_@%+=:,./-".contains(&c))
    {
        return text.into();
    }
    format!("'{}'", text.replace('\'', "'\"'\"'"))
}
pub fn launcher(current: &Path, legacy: Option<&Path>, sockets: &[String]) -> String {
    let mut text = MARKER.to_owned();
    if let Some(legacy) = legacy {
        text.push_str("socket=\nprevious=\naction=\nfor arg in \"$@\"; do\n    if [ -n \"$previous\" ]; then\n        if [ \"$previous\" = --socket ]; then socket=$arg; fi\n        previous=\n        continue\n    fi\n    case \"$arg\" in\n        --socket) previous=--socket ;;\n        --socket=*) socket=${arg#--socket=} ;;\n        --root|--scene|--store|--cache-mb|--build-mb|--keep-mb|--keep-hours|--idle-minutes) previous=value ;;\n        -*) ;;\n        *) if [ -z \"$action\" ]; then action=$arg; fi ;;\n    esac\ndone\nif [ \"$action\" = daemon ]; then\n    case \"$socket\" in\n");
        text.push_str("        ");
        text.push_str(
            &sockets
                .iter()
                .map(|s| quote(s))
                .collect::<Vec<_>>()
                .join("|"),
        );
        text.push_str(&format!(
            ") exec {} \"$@\" ;;\n",
            quote(&legacy.to_string_lossy())
        ));
        text.push_str("    esac\nfi\n");
    }
    text.push_str(&format!(
        "exec {} \"$@\"\n",
        quote(&current.to_string_lossy())
    ));
    text
}
pub fn install_hsm(
    binary: &Path,
    destination: &Path,
    sockets: &[String],
    workspace: &Path,
) -> Result<Value> {
    let binary = binary.canonicalize()?;
    let destination = if destination.is_absolute() {
        destination.to_path_buf()
    } else {
        env::current_dir()?.join(destination)
    };
    let build = endpoint(&binary)?["build_id"]
        .as_str()
        .context("hsm build id")?
        .to_owned();
    let directory = destination.join("lib/hsm");
    let current = directory.join(&build).join("hsm");
    if !current.exists() {
        put(&current, &fs::read(&binary)?, 0o555)?;
    } else {
        ensure!(
            endpoint(&current)?["build_id"] == build,
            "{} serves another build; installation left unchanged",
            current.display()
        );
    }
    let state_path = directory.join("launcher.json");
    let mut state: Value = fs::read(&state_path)
        .ok()
        .map(|bytes| serde_json::from_slice(&bytes))
        .transpose()?
        .unwrap_or(json!({"legacy":null,"legacy_sockets":[]}));
    let command = destination.join("bin/hsm");
    if state["legacy"].is_null() && command.exists() {
        let data = fs::read(&command)?;
        if !data.starts_with(MARKER.as_bytes()) {
            let legacy = directory.join("legacy").join(hash(&data)).join("hsm");
            if !legacy.exists() {
                put(&legacy, &data, 0o555)?;
            }
            state["legacy"] = json!(legacy);
        }
    }
    let mut sockets_all = state["legacy_sockets"]
        .as_array()
        .context("legacy sockets")?
        .iter()
        .map(|v| text(v).map(str::to_owned))
        .collect::<Result<std::collections::BTreeSet<_>>>()?;
    sockets_all.extend(sockets.iter().cloned());
    sockets_all.insert(format!("/tmp/hsm-{}/engine.sock", unsafe {
        libc::geteuid()
    }));
    let sockets_all = sockets_all.into_iter().collect::<Vec<_>>();
    state["legacy_sockets"] = json!(sockets_all);
    put(
        &state_path,
        (serde_json::to_string_pretty(&state)? + "\n").as_bytes(),
        0o644,
    )?;
    let script = launcher(
        &current,
        state["legacy"].as_str().map(Path::new),
        &sockets_all,
    );
    put(&command, script.as_bytes(), 0o755)?;
    let runtime = install_runtime(workspace, &destination)?;
    Ok(
        json!({"command":command,"build_id":build,"executable":current,"legacy":state["legacy"],"runtime":runtime}),
    )
}
