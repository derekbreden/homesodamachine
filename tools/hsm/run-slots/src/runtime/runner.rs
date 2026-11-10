//! The command runner admits heavy processes and preserves their native lease and exit status.
use super::*;
use std::{os::unix::process::ExitStatusExt, time::Instant};
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

fn program_name(argument: &str) -> &str {
    Path::new(argument)
        .file_name()
        .and_then(|p| p.to_str())
        .unwrap_or(argument)
}
struct CommandView<'a> {
    start: usize,
    args: &'a [String],
    cwd: PathBuf,
}
fn command_view<'a>(command: &'a [String], cwd: &Path) -> Option<CommandView<'a>> {
    let mut start = 0;
    let mut cwd = resolved(cwd);
    loop {
        if program_name(command.get(start)?) != "env" {
            return Some(CommandView {
                start,
                args: &command[start..],
                cwd,
            });
        }
        start += 1;
        let mut options = true;
        let mut directory: Option<String> = None;
        loop {
            let argument = command.get(start)?;
            if options && (argument == "--" || argument == "-") {
                options = false;
                start += 1;
                continue;
            }
            if options && argument.starts_with("--") {
                let (flag, attached) = argument
                    .split_once('=')
                    .map_or((argument.as_str(), None), |(key, value)| (key, Some(value)));
                match flag {
                    "--ignore-environment" | "--debug" | "--null" | "--list-signal-handling"
                        if attached.is_none() =>
                    {
                        start += 1
                    }
                    "--block-signal" | "--default-signal" | "--ignore-signal" => start += 1,
                    "--unset" | "--chdir" | "--argv0" => {
                        let value = if let Some(value) = attached {
                            value
                        } else {
                            start += 1;
                            command.get(start)?
                        };
                        if flag == "--chdir" {
                            directory = Some(value.to_owned());
                        }
                        start += 1;
                    }
                    _ => return None,
                }
                continue;
            }
            if options && argument.starts_with('-') {
                let mut consumed = 1;
                let mut at = 1;
                while at < argument.len() {
                    match argument.as_bytes()[at] {
                        b'i' | b'v' | b'0' => at += 1,
                        b'u' | b'C' | b'P' | b'a' => {
                            let value = if at + 1 < argument.len() {
                                &argument[at + 1..]
                            } else {
                                consumed = 2;
                                command.get(start + 1)?
                            };
                            if argument.as_bytes()[at] == b'C' {
                                directory = Some(value.to_owned());
                            }
                            break;
                        }
                        _ => return None,
                    }
                }
                start += consumed;
                continue;
            }
            if argument.contains('=') {
                options = false;
                start += 1;
                continue;
            }
            break;
        }
        if let Some(directory) = directory {
            let directory = Path::new(&directory);
            cwd = resolved(&if directory.is_absolute() {
                directory.to_owned()
            } else {
                cwd.join(directory)
            });
        }
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
struct CommandClass {
    cargo_heavy: bool,
}
fn classify_command(command: &[String], cwd: &Path) -> CommandClass {
    let Some(view) = command_view(command, cwd) else {
        return CommandClass::default();
    };
    let program = program_name(&view.args[0]);
    let mut arguments = view
        .args
        .iter()
        .skip(1)
        .take_while(|arg| arg.as_str() != "--");
    CommandClass {
        cargo_heavy: program == "cargo"
            && arguments.any(|arg| {
                matches!(
                    arg.as_str(),
                    "build" | "test" | "run" | "check" | "bench" | "install" | "rustc"
                )
            }),
    }
}
fn resolved_argument(argument: &str, cwd: &Path) -> PathBuf {
    let path = Path::new(argument);
    resolved(&if path.is_absolute() {
        path.to_owned()
    } else {
        cwd.join(path)
    })
}

pub fn script_key(command: &[String], cwd: &Path) -> String {
    let Some(view) = command_view(command, cwd) else {
        return command
            .first()
            .map(|arg| program_name(arg).to_owned())
            .unwrap_or_default();
    };
    let command = view.args;
    let program = Path::new(&command[0])
        .file_name()
        .unwrap_or_default()
        .to_string_lossy();
    for arg in command {
        if [".py", ".js", ".mjs", ".sh", ".ts", ".tsx"]
            .iter()
            .any(|ext| arg.ends_with(ext))
        {
            let path = resolved_argument(arg, &view.cwd);
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
                        let path = resolved_argument(value, &view.cwd);
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
    let Some(view) = command_view(command, Path::new(".")) else {
        return command.to_vec();
    };
    let prefix = &command[..view.start];
    let command = view.args;
    let split = command
        .iter()
        .position(|v| v == "--")
        .unwrap_or(command.len());
    let mut kept = prefix.to_vec();
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
        if root.join("tools/hsm/Cargo.toml").is_file() {
            return root.into();
        }
    }
    here
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
                    "Run one heavy command under the host's shared admission policy.\n\nUsage: tools/run [--count 1..4] [--timing] [--cad] [--key NAME] -- COMMAND..."
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
        slots::set_count(value)?;
        println!("{}: {value}", directory()?.join("count").display());
        return Ok(0);
    }
    if check {
        return Ok(if slots::current("run") { 0 } else { 1 });
    }
    ensure!(!command.is_empty(), "usage: name a command after --");
    if !env::split_paths(&env::var_os("PATH").unwrap_or_default())
        .any(|dir| dir.join("cargo").is_file())
    {
        let mut candidates = vec![PathBuf::from("/opt/homebrew/opt/rustup/bin")];
        if let Some(home) = env::var_os("HOME") {
            candidates.push(PathBuf::from(home).join(".cargo/bin"));
        }
        if let Some(directory) = candidates
            .into_iter()
            .find(|dir| dir.join("cargo").is_file())
        {
            let mut paths = vec![directory];
            paths.extend(env::split_paths(&env::var_os("PATH").unwrap_or_default()));
            // The runner is single-threaded while preparing its command environment.
            unsafe {
                env::set_var("PATH", env::join_paths(paths)?);
            }
        }
    }
    let root = workspace_root();
    let key = key.unwrap_or_else(|| script_key(&command, &env::current_dir().unwrap_or_default()));
    let CommandClass { cargo_heavy } = classify_command(&command, &env::current_dir()?);
    if cargo_heavy {
        command = limit_jobs(&command, 2);
    }
    let cad_dir = env::temp_dir().join("hsm-cad-lock");
    if cad_arg {
        cad::wait_legacy(&cad_dir)?;
    }
    if let Err(error) = slots::acquire_run(Some(&key), timing) {
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
    if cad_arg {
        if let Some(code) = cad::acquire(&key, &root)? {
            return Ok(code);
        }
    }
    if cargo_heavy {
        slots::acquire_aux("compiler")?;
    }
    let broker = slots::new_broker()?;
    let mut environment = slots::child_env()?
        .as_object()
        .cloned()
        .context("child environment")?;
    environment.insert("CARGO_BUILD_JOBS".into(), json!("2"));
    environment.insert("CMAKE_BUILD_PARALLEL_LEVEL".into(), json!("2"));
    let began = Instant::now();
    let mut child = Command::new(&command[0]);
    child.args(&command[1..]);
    child.env_clear().envs(
        environment
            .iter()
            .filter_map(|(k, v)| v.as_str().map(|v| (k, v))),
    );
    slots::context()?.apply(&mut child)?;
    let child = match ipc::spawn(&mut child) {
        Ok(child) => child,
        Err(error) => {
            slots::close_broker(broker["id"].as_u64().unwrap())?;
            cad::record(&cad_dir, 1);
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
    cad::record(&cad_dir, code);
    cad::release(&cad_dir);
    slots::release(false);
    Ok(code)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn words(values: &[&str]) -> Vec<String> {
        values.iter().map(|value| (*value).to_owned()).collect()
    }

    #[test]
    fn env_assignments_reveal_the_compiler_without_becoming_script_keys() {
        let bare = words(&[
            "cargo",
            "build",
            "--manifest-path",
            "tools/hsm/Cargo.toml",
            "-p",
            "hsm-run-slots",
        ]);
        let wrapped = [
            words(&[
                "/usr/bin/env",
                "RUSTC=/some/compiler.py",
                "SETTING=spaces and --jobs=55",
            ]),
            bare.clone(),
        ]
        .concat();
        assert_eq!(
            classify_command(&wrapped, Path::new(".")),
            classify_command(&bare, Path::new("."))
        );
        assert!(classify_command(&wrapped, Path::new(".")).cargo_heavy);
        assert_eq!(
            script_key(&wrapped, Path::new(".")),
            script_key(&bare, Path::new("."))
        );
        assert_eq!(&limit_jobs(&wrapped, 2)[..3], &wrapped[..3]);
    }
    #[test]
    fn env_flags_and_nested_env_keep_utility_arguments_in_place() {
        let command = words(&[
            "env",
            "-iv",
            "-u",
            "-j99",
            "-P/opt/tools",
            "FIRST=one",
            "env",
            "--ignore-environment",
            "--unset=RUSTFLAGS",
            "RUSTC=rustc",
            "cargo",
            "+stable",
            "test",
            "-j12",
            "--",
            "--jobs=77",
        ]);
        let class = classify_command(&command, Path::new("."));
        assert!(class.cargo_heavy);
        let expected = words(&[
            "env",
            "-iv",
            "-u",
            "-j99",
            "-P/opt/tools",
            "FIRST=one",
            "env",
            "--ignore-environment",
            "--unset=RUSTFLAGS",
            "RUSTC=rustc",
            "cargo",
            "+stable",
            "test",
            "--jobs=2",
            "--",
            "--jobs=77",
        ]);
        assert_eq!(limit_jobs(&command, 2), expected);
    }
    #[test]
    fn outer_env_terminators_do_not_hide_inner_job_flags_or_touch_child_options() {
        let command = words(&[
            "env",
            "--",
            "RUSTC=rustc",
            "cargo",
            "run",
            "--jobs",
            "48",
            "-j32",
            "--jobs=8",
            "--",
            "-j99",
            "--jobs=77",
        ]);
        assert_eq!(
            limit_jobs(&command, 2),
            words(&[
                "env",
                "--",
                "RUSTC=rustc",
                "cargo",
                "run",
                "--jobs=2",
                "--",
                "-j99",
                "--jobs=77"
            ])
        );
        assert!(classify_command(&command, Path::new(".")).cargo_heavy);
    }
    #[test]
    fn env_directory_options_resolve_manifests_where_the_utility_runs() {
        let cwd = Path::new("/workspace");
        let command = words(&[
            "env",
            "-Cignored",
            "-C",
            "project",
            "env",
            "--chdir=inner",
            "cargo",
            "build",
            "--manifest-path",
            "Cargo.toml",
        ]);
        assert_eq!(
            script_key(&command, cwd),
            "cargo:--manifest-path:project/inner/Cargo.toml"
        );
        assert!(classify_command(&command, cwd).cargo_heavy);
    }
    #[test]
    fn split_strings_unknown_options_and_environment_only_calls_stay_opaque() {
        for command in [
            words(&["env", "-S", "cargo build -j12"]),
            words(&["env", "--unknown", "cargo", "build"]),
            words(&["env", "-u"]),
            words(&["env", "VAR=value"]),
        ] {
            assert_eq!(
                classify_command(&command, Path::new(".")),
                CommandClass::default()
            );
            assert_eq!(limit_jobs(&command, 2), command);
            assert_eq!(script_key(&command, Path::new(".")), "env");
        }
        assert!(
            !classify_command(
                &words(&["cargo", "metadata", "--", "build"]),
                Path::new(".")
            )
            .cargo_heavy
        );
    }
}
