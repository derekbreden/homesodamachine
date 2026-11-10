//! Cache cleanup ages each scratch unit by its own newest file write and retains shared memo and runtime caches.
use anyhow::{Context, Result, ensure};
use std::{
    ffi::CString,
    path::{Path, PathBuf},
    time::UNIX_EPOCH,
};

const CONTAINERS: &[&str] = &["runs", "prints", "printer-control"];
const KEEP: &[&str] = &[
    "meshes",
    "boxes",
    "realized",
    "runtimes",
    "printer-control/venv",
];

pub fn newest_write(path: &Path) -> Result<(f64, u64)> {
    let metadata = std::fs::symlink_metadata(path)?;
    if metadata.file_type().is_symlink() || !metadata.is_dir() {
        return Ok((
            if path.file_name().is_some_and(|n| n == ".DS_Store") {
                0.
            } else {
                modified(&metadata)
            },
            metadata.len(),
        ));
    }
    let (mut newest, mut size) = (0_f64, 0_u64);
    let mut stack = vec![path.to_path_buf()];
    while let Some(dir) = stack.pop() {
        let Ok(entries) = std::fs::read_dir(dir) else {
            continue;
        };
        for entry in entries.flatten() {
            let child = entry.path();
            let Ok(meta) = std::fs::symlink_metadata(&child) else {
                continue;
            };
            if meta.is_dir() {
                stack.push(child)
            } else if meta.file_type().is_symlink() && child.is_dir() {
            } else {
                size += meta.len();
                if entry.file_name() != ".DS_Store" {
                    newest = newest.max(modified(&meta));
                }
            }
        }
    }
    Ok((newest, size))
}
fn modified(metadata: &std::fs::Metadata) -> f64 {
    metadata
        .modified()
        .ok()
        .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
        .map_or(0., |d| d.as_secs_f64())
}

pub fn units(cache: &Path) -> Result<Vec<(String, PathBuf)>> {
    let mut out = Vec::new();
    let mut entries: Vec<_> = std::fs::read_dir(cache)?
        .filter_map(|entry| entry.ok())
        .collect();
    entries.sort_by_key(|e| e.file_name());
    for entry in entries {
        let name = entry.file_name().to_string_lossy().into_owned();
        if name == ".DS_Store" || KEEP.contains(&name.as_str()) {
            continue;
        }
        if CONTAINERS.contains(&name.as_str()) && entry.file_type()?.is_dir() {
            let mut children: Vec<_> = std::fs::read_dir(entry.path())?
                .filter_map(|entry| entry.ok())
                .collect();
            children.sort_by_key(|e| e.file_name());
            for child in children {
                let rel = format!("{name}/{}", child.file_name().to_string_lossy());
                if child.file_name() != ".DS_Store" && !KEEP.contains(&rel.as_str()) {
                    out.push((rel, child.path()));
                }
            }
        } else {
            out.push((name, entry.path()));
        }
    }
    Ok(out)
}
fn date(stamp: f64, format: &str) -> String {
    if stamp == 0. {
        return "never".into();
    }
    let stamp = stamp as libc::time_t;
    let mut tm = std::mem::MaybeUninit::uninit();
    let mut output = [0_i8; 64];
    let format = CString::new(format).expect("date format");
    unsafe {
        if libc::localtime_r(&stamp, tm.as_mut_ptr()).is_null() {
            return stamp.to_string();
        };
        let length = libc::strftime(
            output.as_mut_ptr(),
            output.len(),
            format.as_ptr(),
            tm.as_ptr(),
        );
        String::from_utf8_lossy(std::slice::from_raw_parts(
            output.as_ptr().cast::<u8>(),
            length,
        ))
        .into_owned()
    }
}
#[derive(Default, Debug)]
pub struct Summary {
    pub removed: usize,
    pub kept: usize,
    pub failed: usize,
    pub bytes: u64,
}
pub fn collect(cache: &Path, days: f64, apply: bool, now: f64) -> Result<Summary> {
    ensure!(
        days.is_finite() && days >= 0.,
        "--days needs a finite nonnegative duration"
    );
    let mut summary = Summary::default();
    let cutoff = now - days * 86400.;
    for (rel, path) in units(cache)? {
        let (newest, size) = newest_write(&path)?;
        if newest >= cutoff {
            summary.kept += 1;
            continue;
        }
        let when = date(newest, "%Y-%m-%d %H:%M");
        if apply {
            let result = std::fs::symlink_metadata(&path).and_then(|m| {
                if m.is_dir() {
                    std::fs::remove_dir_all(&path)
                } else {
                    std::fs::remove_file(&path)
                }
            });
            if let Err(error) = result {
                println!(
                    "  failed        {when}  {:9.1} MB  {rel}: {error}",
                    size as f64 / 1e6
                );
                summary.failed += 1;
                continue;
            }
        }
        println!(
            "  {}  {when}  {:9.1} MB  {rel}",
            if apply { "deleted" } else { "would delete" },
            size as f64 / 1e6
        );
        summary.removed += 1;
        summary.bytes += size;
    }
    Ok(summary)
}
pub fn cli(root: &Path, args: &[String]) -> Result<i32> {
    let mut cache = root.join(".cache");
    let mut days = 3.;
    let mut apply = false;
    let mut args = args.iter();
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--cache" => cache = PathBuf::from(args.next().context("--cache needs a path")?),
            "--days" => days = args.next().context("--days needs a duration")?.parse()?,
            "--apply" => apply = true,
            "--help" | "-h" => {
                println!(
                    "repo-tools cache-gc [--cache path] [--days duration] [--apply]\nThe default lists expired scratch; --apply deletes it. Shared geometry memo and installed runtime caches remain."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown cache-gc option {arg}"),
        }
    }
    let stamp = date(crate::now(), "%Y-%m-%d %H:%M:%S");
    if !cache.is_dir() {
        println!("{stamp} :: {} does not exist", cache.display());
        return Ok(0);
    }
    let summary = collect(&cache, days, apply, crate::now())?;
    println!(
        "{stamp} :: .cache {} {:.2} GB in {} unit(s); {} kept{}",
        if apply { "freed" } else { "would free" },
        summary.bytes as f64 / 1e9,
        summary.removed,
        summary.kept,
        if summary.failed > 0 {
            format!("; {} failed", summary.failed)
        } else {
            String::new()
        }
    );
    Ok(i32::from(summary.failed > 0))
}

#[cfg(test)]
mod tests {
    use super::*;
    fn temp() -> PathBuf {
        let p = std::env::temp_dir().join(format!(
            "hsm-cache-gc-{}-{}",
            std::process::id(),
            crate::now().to_bits()
        ));
        std::fs::create_dir_all(&p).unwrap();
        p
    }
    fn aged(path: &Path, now: f64) {
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, b"model").unwrap();
        std::fs::File::open(path)
            .unwrap()
            .set_times(
                std::fs::FileTimes::new()
                    .set_modified(UNIX_EPOCH + std::time::Duration::from_secs_f64(now)),
            )
            .unwrap();
    }
    #[test]
    fn new_run_does_not_retain_old_runs_or_expire_memos() {
        let root = temp();
        let now = crate::now();
        let old = root.join("runs/finished/model");
        let current = root.join("runs/current/model");
        aged(&old, now - 5. * 86400.);
        aged(&current, now);
        for keep in KEEP {
            aged(&root.join(keep).join("model"), now - 5. * 86400.);
        }
        collect(&root, 3., true, now).unwrap();
        assert!(!old.parent().unwrap().exists());
        assert!(current.is_file());
        for keep in KEEP {
            assert!(root.join(keep).join("model").is_file())
        }
        std::fs::remove_dir_all(root).unwrap();
    }
    #[cfg(unix)]
    #[test]
    fn expired_run_symlink_keeps_target() {
        use std::os::unix::ffi::OsStrExt;
        let root = temp();
        let target = root.join("finished.3mf");
        std::fs::write(&target, b"ready print").unwrap();
        let runs = root.join("cache/runs");
        std::fs::create_dir_all(&runs).unwrap();
        let link = runs.join("input");
        std::os::unix::fs::symlink(&target, &link).unwrap();
        let at = (crate::now() - 5. * 86400.) as libc::time_t;
        let times = [libc::timespec {
            tv_sec: at,
            tv_nsec: 0,
        }; 2];
        let name = CString::new(link.as_os_str().as_bytes()).unwrap();
        assert_eq!(
            unsafe {
                libc::utimensat(
                    libc::AT_FDCWD,
                    name.as_ptr(),
                    times.as_ptr(),
                    libc::AT_SYMLINK_NOFOLLOW,
                )
            },
            0
        );
        collect(&root.join("cache"), 3., true, crate::now()).unwrap();
        assert!(!link.exists());
        assert_eq!(std::fs::read(target).unwrap(), b"ready print");
        std::fs::remove_dir_all(root).unwrap();
    }
}
