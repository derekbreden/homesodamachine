//! Explicit check readings feed the site's settings gear; opt-in pinning commits only their clockless verdict.
use anyhow::{Context, Result, ensure};
use serde::{Deserialize, Serialize};
use std::{
    collections::BTreeMap,
    io::Write,
    os::fd::AsRawFd,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::Instant,
};
const CHECKS: [(&str, &str); 6] = [
    (
        "check_enclosure_mating_clearance",
        "enclosure-mating-clearance",
    ),
    ("check_ledger", "ledger"),
    ("check_pinmap", "pinmap"),
    ("check_purchase_evidence", "purchase-evidence"),
    ("check_step_colours", "step-colours"),
    ("check_paths", "paths"),
];
const SUBJECT: &str = "checks: the reading this commit's tree gives";
const REL: &str = "web/public/checks.json";
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct Row {
    check: String,
    status: String,
    note: String,
}
#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Eq)]
pub struct Verdict {
    green: bool,
    checks: Vec<Row>,
    detail: BTreeMap<String, Vec<String>>,
}
struct Run {
    check: String,
    code: i32,
    seconds: f64,
    out: String,
    err: String,
}
fn verdict(runs: &[Run]) -> Verdict {
    let mut checks = Vec::new();
    let mut detail = BTreeMap::new();
    for run in runs {
        let body = if run.out.is_empty() {
            &run.err
        } else {
            &run.out
        };
        let note = body
            .lines()
            .rev()
            .find(|l| !l.trim().is_empty())
            .unwrap_or("")
            .trim()
            .to_owned();
        checks.push(Row {
            check: run.check.clone(),
            status: if run.code == 0 { "ok" } else { "red" }.into(),
            note,
        });
        if run.code != 0 {
            let body = run.out.clone() + &run.err;
            let mut lines = body
                .lines()
                .map(str::trim_end)
                .filter(|l| !l.trim().is_empty() && !l.trim_start().starts_with("[build]"))
                .map(str::to_owned)
                .collect::<Vec<_>>();
            if lines.len() > 25 {
                lines.drain(..lines.len() - 25);
            }
            detail.insert(run.check.clone(), lines);
        }
    }
    Verdict {
        green: detail.is_empty(),
        checks,
        detail,
    }
}
pub fn read(root: &Path) -> Result<Verdict> {
    let executable = std::env::current_exe()?;
    let mut runs = Vec::new();
    for (id, name) in CHECKS {
        let started = Instant::now();
        let run = Command::new(&executable)
            .args([
                "--root",
                root.to_str().context("UTF-8 repository path")?,
                "check",
                name,
            ])
            .current_dir(root)
            .output()?;
        runs.push(Run {
            check: id.into(),
            code: run.status.code().unwrap_or(1),
            seconds: started.elapsed().as_secs_f64(),
            out: String::from_utf8_lossy(&run.stdout).into_owned(),
            err: String::from_utf8_lossy(&run.stderr).into_owned(),
        });
    }
    let reading = verdict(&runs);
    let width = runs.iter().map(|r| r.check.len()).max().unwrap_or(0);
    for (run, row) in runs.iter().zip(&reading.checks) {
        println!(
            "  {} {:width$}  {:5.1}s  {}",
            if run.code == 0 { "ok  " } else { "RED " },
            run.check,
            run.seconds,
            row.note.chars().take(64).collect::<String>()
        );
    }
    println!(
        "\n{}/{} green, {:.0}s total",
        runs.iter().filter(|r| r.code == 0).count(),
        runs.len(),
        runs.iter().map(|r| r.seconds).sum::<f64>()
    );
    for run in runs.iter().filter(|r| r.code != 0) {
        println!("\n──── {} ────", run.check);
        let body = run.out.clone() + &run.err;
        let lines = body.trim().lines().collect::<Vec<_>>();
        for line in lines.iter().skip(lines.len().saturating_sub(25)) {
            println!("  {line}");
        }
    }
    Ok(reading)
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut json = None;
    let mut list = false;
    let mut it = args.iter();
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--list" => list = true,
            "--json" => json = Some(PathBuf::from(it.next().context("--json needs a path")?)),
            "--help" | "-h" => {
                println!(
                    "repo-tools checks [--list] [--json PATH]\nRuns the explicit retained list on request. The optional JSON carries no time or duration; red is a reading and holds no build or publish."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown checks option {arg}"),
        }
    }
    if list {
        for (id, name) in CHECKS {
            println!("  {id}  (repo-tools check {name})");
        }
        println!("{} check(s)", CHECKS.len());
        return Ok(0);
    }
    let reading = read(root)?;
    if let Some(path) = json {
        crate::write_json(
            &if path.is_absolute() {
                path
            } else {
                root.join(path)
            },
            &reading,
        )?;
    }
    Ok(i32::from(!reading.green))
}
fn message(args: &[String]) -> Result<(bool, Option<String>)> {
    let mut check = false;
    let mut file = None;
    let mut session = None;
    let mut it = args.iter();
    while let Some(arg) = it.next() {
        match arg.as_str() {
            "--check" => check = true,
            "--message-file" => {
                file = Some(PathBuf::from(
                    it.next().context("--message-file needs a path")?,
                ))
            }
            "--session" => {
                session = Some(
                    it.next()
                        .context("--session needs the current chat title")?
                        .to_owned(),
                )
            }
            _ => anyhow::bail!("unknown checks-now option {arg}"),
        }
    }
    ensure!(
        file.is_none() || session.is_none(),
        "choose --message-file or --session"
    );
    let message = if let Some(file) = file {
        let message = crate::text(file)?;
        ensure!(
            !message.trim().is_empty() && message.lines().any(|l| l.starts_with("Session: ")),
            "--message-file needs the complete caller-authored subject and trailer block, including Session"
        );
        Some(message)
    } else if let Some(session) = session {
        ensure!(
            !session.trim().is_empty() && !session.contains(['\n', '\r']),
            "--session needs one nonempty title"
        );
        Some(format!("{SUBJECT}\n\nSession: {session}\n"))
    } else {
        None
    };
    ensure!(
        check || message.is_some(),
        "checks-now write/pin needs --session '<current chat title>' or --message-file with a complete message"
    );
    Ok((check, message))
}
fn hash(root: &Path, bytes: &[u8]) -> Result<String> {
    let mut child = Command::new("git")
        .args(["hash-object", "-w", "--stdin"])
        .current_dir(root)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;
    child.stdin.take().context("blob stdin")?.write_all(bytes)?;
    let out = child.wait_with_output()?;
    ensure!(
        out.status.success(),
        "write verdict blob: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    Ok(String::from_utf8(out.stdout)?.trim().into())
}
fn bytes(reading: &Verdict) -> Result<Vec<u8>> {
    let mut bytes = serde_json::to_vec_pretty(reading)?;
    bytes.push(b'\n');
    Ok(bytes)
}
fn changed(root: &Path, bytes: &[u8]) -> Result<bool> {
    let previous = crate::command(root, "git", &["show", &format!("HEAD:{REL}")])?;
    Ok(!previous.status.success() || previous.stdout != bytes)
}
fn pin(root: &Path, bytes: &[u8], message: &str) -> Result<()> {
    #[derive(Serialize)]
    struct File<'a> {
        path: &'a str,
        blob: String,
        mode: &'a str,
    }
    #[derive(Serialize)]
    struct Snapshot<'a> {
        message: &'a str,
        files: Vec<File<'a>>,
    }
    let snapshot = Snapshot {
        message,
        files: vec![File {
            path: REL,
            blob: hash(root, bytes)?,
            mode: "100644",
        }],
    };
    let scratch = root
        .join(".cache/runs")
        .join(format!("checks-pin-{}", std::process::id()));
    std::fs::create_dir_all(&scratch)?;
    let path = scratch.join("snapshot.json");
    crate::write_json(&path, &snapshot)?;
    let land = crate::program(root, "hsm-land")?;
    let run = Command::new(land)
        .arg("--root")
        .arg(root)
        .arg("--commit-snapshot")
        .arg(&path)
        .output()?;
    let _ = std::fs::remove_file(path);
    let _ = std::fs::remove_dir(scratch);
    ensure!(
        run.status.success(),
        "pin verdict: {}",
        String::from_utf8_lossy(&run.stderr)
    );
    let result: serde_json::Value = serde_json::from_slice(&run.stdout)?;
    if result["changed"] == true {
        let hook = crate::command(
            root,
            "git",
            &["hook", "run", "--ignore-missing", "post-commit"],
        )?;
        if !hook.status.success() {
            eprintln!(
                "the reading committed; post-commit reported: {}",
                String::from_utf8_lossy(&hook.stderr)
            );
        }
    }
    Ok(())
}
fn head_is_reading(root: &Path) -> Result<bool> {
    if crate::git(root, &["log", "-1", "--format=%s"])? != SUBJECT {
        return Ok(false);
    }
    Ok(crate::git(root, &["status", "--porcelain", "--untracked-files=normal"])?.is_empty())
}
fn once(root: &Path, message: Option<&str>, check: bool) -> Result<()> {
    if head_is_reading(root)? {
        println!("  HEAD is already a reading of this content");
        return Ok(());
    }
    let started = Instant::now();
    let reading = read(root)?;
    let bytes = bytes(&reading)?;
    let different = changed(root, &bytes)?;
    if check {
        println!(
            "  --check: {}, {}",
            if reading.green { "green" } else { "red" },
            if different {
                "would pin it"
            } else {
                "unchanged from this commit"
            }
        );
        return Ok(());
    }
    if !different {
        println!(
            "  {}, and unchanged from what this commit carries ({:.0}s)",
            if reading.green { "green" } else { "red" },
            started.elapsed().as_secs_f64()
        );
        return Ok(());
    }
    let target = root.join(REL);
    std::fs::create_dir_all(target.parent().unwrap())?;
    std::fs::write(target, &bytes)?;
    println!(
        "  {}, pinning the reading ({:.0}s)",
        if reading.green {
            "green again"
        } else {
            "RED — the gear goes red, /settings names it"
        },
        started.elapsed().as_secs_f64()
    );
    pin(root, &bytes, message.context("pin message")?)
}
pub fn now(root: &Path, args: &[String]) -> Result<i32> {
    if args.iter().any(|a| a == "--help" || a == "-h") {
        println!(
            "repo-tools checks-now --check\nrepo-tools checks-now --session '<current chat title>'\nrepo-tools checks-now --message-file PATH\nThe check mode keeps the verdict in memory. The write mode pins only web/public/checks.json through hsm-land and requires the caller's commit identity. No hook starts these readings."
        );
        return Ok(0);
    }
    let (check, message) = message(args)?;
    if check {
        once(root, None, true)?;
        return Ok(0);
    }
    let cache = root.join(".cache");
    std::fs::create_dir_all(&cache)?;
    let again = cache.join("checks-now.again");
    let mut lock = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .truncate(false)
        .open(cache.join("checks-now.lock"))?;
    if unsafe { libc::flock(lock.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } != 0 {
        let error = std::io::Error::last_os_error();
        if error.kind() != std::io::ErrorKind::WouldBlock {
            return Err(error.into());
        }
        std::fs::write(&again, b"read again\n")?;
        println!("  a read is already running — it will read the tree again when it finishes");
        return Ok(0);
    }
    lock.set_len(0)?;
    writeln!(lock, "{}", std::process::id())?;
    let result = (|| {
        once(root, message.as_deref(), false)?;
        while again.exists() {
            std::fs::remove_file(&again)?;
            println!("  another read was requested — reading the tree again");
            once(root, message.as_deref(), false)?;
        }
        Ok::<_, anyhow::Error>(())
    })();
    let _ = std::fs::remove_file(&again);
    drop(lock);
    result?;
    Ok(0)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn verdict_has_no_clock_and_filters_queue_pids() {
        let runs = vec![Run {
            check: "check_example".into(),
            code: 1,
            seconds: 42.,
            out: "[build] queued pid 9\nactual finding\n".into(),
            err: String::new(),
        }];
        let first = verdict(&runs);
        let second = verdict(&[Run {
            check: "check_example".into(),
            code: 1,
            seconds: 81.,
            out: "[build] queued pid 17\nactual finding\n".into(),
            err: String::new(),
        }]);
        assert_eq!(first, second);
        assert_eq!(first.detail["check_example"], vec!["actual finding"]);
        let json = String::from_utf8(bytes(&first).unwrap()).unwrap();
        assert!(!json.contains("seconds"));
    }
    #[test]
    fn pin_identity_is_explicit() {
        assert!(message(&[]).is_err());
        assert!(message(&["--check".into()]).is_ok());
        let (_, message) = message(&["--session".into(), "Native operations".into()]).unwrap();
        assert_eq!(
            message.unwrap(),
            format!("{SUBJECT}\n\nSession: Native operations\n")
        );
    }
}
