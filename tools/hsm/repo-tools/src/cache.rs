//! Cache cleanup ages each scratch unit by its own newest file write and each cargo unit by its last fingerprint read, and retains shared memo and runtime caches.
use anyhow::{Context, Result, ensure};
use std::{
    collections::HashMap,
    ffi::CString,
    os::unix::fs::MetadataExt,
    path::{Path, PathBuf},
    time::UNIX_EPOCH,
};

/// Days a cargo unit stays without a build reading its fingerprint.
const UNIT_DAYS: f64 = 1.;
/// A profile's directories whose entries carry their unit's hash.
const UNIT_DIRS: &[&str] = &["deps", "build", "examples", ".fingerprint"];
/// The lock files cargo holds in a profile directory through a build.
const LOCKS: &[&str] = &[".cargo-lock", ".cargo-build-lock"];
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
fn touched(metadata: &std::fs::Metadata) -> f64 {
    metadata
        .accessed()
        .ok()
        .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
        .map_or(0., |d| d.as_secs_f64())
        .max(modified(metadata))
}

/// The unit hash in a fingerprint, output or build-script name: `name-<hash>[.ext]`.
fn unit_hash(name: &str) -> Option<&str> {
    let bytes = name.as_bytes();
    name.match_indices('-')
        .map(|(i, _)| i + 1)
        .filter(|&start| {
            bytes.get(start..start + 16).is_some_and(|hash| {
                hash.iter()
                    .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(b))
            }) && bytes.get(start + 16).is_none_or(|&b| b == b'.')
        })
        .last()
        .map(|start| &name[start..start + 16])
}

/// Every cargo profile directory under `target`: each one holding `.fingerprint`.
fn profiles(target: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    let mut stack = vec![(target.to_path_buf(), 0)];
    while let Some((dir, depth)) = stack.pop() {
        if dir.join(".fingerprint").is_dir() {
            out.push(dir);
            continue;
        }
        let Ok(entries) = std::fs::read_dir(&dir) else {
            continue;
        };
        for entry in entries.flatten() {
            if depth < 3 && entry.file_type().is_ok_and(|t| t.is_dir()) {
                stack.push((entry.path(), depth + 1));
            }
        }
    }
    out.sort();
    out
}

/// When a build last read a unit's fingerprint.
fn last_read(unit: &Path) -> f64 {
    let newest = std::fs::read_dir(unit)
        .into_iter()
        .flatten()
        .flatten()
        .filter_map(|entry| entry.metadata().ok())
        .map(|meta| touched(&meta))
        .fold(0., f64::max);
    if newest > 0. {
        newest
    } else {
        std::fs::symlink_metadata(unit).map_or(0., |meta| modified(&meta))
    }
}

/// The bytes removing `path` frees; a file another hard link still names frees none.
fn freed(path: &Path) -> u64 {
    let mut total = 0;
    let mut stack = vec![path.to_path_buf()];
    while let Some(path) = stack.pop() {
        let Ok(meta) = std::fs::symlink_metadata(&path) else {
            continue;
        };
        if meta.is_dir() {
            stack.extend(
                std::fs::read_dir(&path)
                    .into_iter()
                    .flatten()
                    .flatten()
                    .map(|e| e.path()),
            );
        } else if meta.nlink() == 1 {
            total += meta.blocks() * 512;
        }
    }
    total
}

#[derive(Default, Debug)]
pub struct Sweep {
    pub removed: usize,
    pub kept: usize,
    pub busy: usize,
    pub failed: usize,
    pub bytes: u64,
}

/// Removes the cargo units under `target` that no build has read since `cutoff`, holding each
/// profile's cargo locks and passing over a profile a build holds. Top-level binaries and dep-info stay.
pub fn sweep(target: &Path, cutoff: f64, apply: bool) -> Result<Sweep> {
    let mut sweep = Sweep::default();
    for profile in profiles(target) {
        let locks = LOCKS
            .iter()
            .map(|name| {
                std::fs::OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(profile.join(name))
            })
            .collect::<std::io::Result<Vec<_>>>()?;
        if locks.iter().any(|lock| lock.try_lock().is_err()) {
            println!("  in use        {}", profile.display());
            sweep.busy += 1;
            continue;
        }
        let mut read = HashMap::new();
        for entry in std::fs::read_dir(profile.join(".fingerprint"))?.flatten() {
            let name = entry.file_name().to_string_lossy().into_owned();
            if let Some(hash) = unit_hash(&name) {
                read.insert(hash.to_owned(), last_read(&entry.path()));
            }
        }
        let (removed, mut bytes) = (sweep.removed, 0);
        sweep.kept += read.values().filter(|&&t| t >= cutoff).count();
        sweep.removed += read.values().filter(|&&t| t < cutoff).count();
        for dir in UNIT_DIRS {
            let Ok(entries) = std::fs::read_dir(profile.join(dir)) else {
                continue;
            };
            for entry in entries.flatten() {
                let name = entry.file_name().to_string_lossy().into_owned();
                let Some(hash) = unit_hash(&name) else {
                    continue;
                };
                let path = entry.path();
                let when = read.get(hash).copied().unwrap_or_else(|| {
                    std::fs::symlink_metadata(&path).map_or(f64::MAX, |meta| touched(&meta))
                });
                if when >= cutoff {
                    continue;
                }
                let size = freed(&path);
                if apply {
                    let result = if entry.file_type().is_ok_and(|t| t.is_dir()) {
                        std::fs::remove_dir_all(&path)
                    } else {
                        std::fs::remove_file(&path)
                    };
                    if let Err(error) = result {
                        println!("  failed        {}: {error}", path.display());
                        sweep.failed += 1;
                        continue;
                    }
                }
                bytes += size;
            }
        }
        println!(
            "  {}  {:9.1} MB  {} unit(s) in {}",
            if apply { "deleted" } else { "would delete" },
            bytes as f64 / 1e6,
            sweep.removed - removed,
            profile.display()
        );
        sweep.bytes += bytes;
    }
    Ok(sweep)
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
    let mut target = root.join("tools/hsm/target");
    let mut days = 3.;
    let mut apply = false;
    let mut args = args.iter();
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--cache" => cache = PathBuf::from(args.next().context("--cache needs a path")?),
            "--target" => target = PathBuf::from(args.next().context("--target needs a path")?),
            "--days" => days = args.next().context("--days needs a duration")?.parse()?,
            "--apply" => apply = true,
            "--help" | "-h" => {
                println!(
                    "repo-tools cache-gc [--cache path] [--target path] [--days duration] [--apply]\nThe default lists expired scratch and the cargo units no build has read lately; --apply deletes them. Shared geometry memo and installed runtime caches remain."
                );
                return Ok(0);
            }
            _ => anyhow::bail!("unknown cache-gc option {arg}"),
        }
    }
    let stamp = date(crate::now(), "%Y-%m-%d %H:%M:%S");
    let verb = if apply { "freed" } else { "would free" };
    let mut failed = 0;
    if cache.is_dir() {
        let summary = collect(&cache, days, apply, crate::now())?;
        println!(
            "{stamp} :: .cache {verb} {:.2} GB in {} unit(s); {} kept{}",
            summary.bytes as f64 / 1e9,
            summary.removed,
            summary.kept,
            if summary.failed > 0 {
                format!("; {} failed", summary.failed)
            } else {
                String::new()
            }
        );
        failed += summary.failed;
    } else {
        println!("{stamp} :: {} does not exist", cache.display());
    }
    if target.is_dir() {
        let swept = sweep(&target, crate::now() - UNIT_DAYS * 86400., apply)?;
        println!(
            "{stamp} :: {} {verb} {:.2} GB in {} unit(s); {} kept{}{}",
            target.strip_prefix(root).unwrap_or(&target).display(),
            swept.bytes as f64 / 1e9,
            swept.removed,
            swept.kept,
            if swept.busy > 0 {
                format!("; {} profile(s) in use", swept.busy)
            } else {
                String::new()
            },
            if swept.failed > 0 {
                format!("; {} failed", swept.failed)
            } else {
                String::new()
            }
        );
        failed += swept.failed;
    }
    Ok(i32::from(failed > 0))
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
    fn read_at(path: &Path, at: f64) {
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(path, b"unit").unwrap();
        let at = UNIX_EPOCH + std::time::Duration::from_secs_f64(at);
        std::fs::File::open(path)
            .unwrap()
            .set_times(std::fs::FileTimes::new().set_accessed(at).set_modified(at))
            .unwrap();
    }
    #[test]
    fn sweep_drops_units_no_build_read() {
        let root = temp();
        let (now, old) = (crate::now(), crate::now() - 5. * 86400.);
        let profile = root.join("release");
        read_at(&profile.join(".fingerprint/gone-0123456789abcdef/lib-gone"), old);
        read_at(&profile.join("deps/libgone-0123456789abcdef.rlib"), old);
        read_at(&profile.join("build/gone-0123456789abcdef/out/generated.rs"), old);
        read_at(&profile.join(".fingerprint/live-fedcba9876543210/lib-live"), now);
        read_at(&profile.join("deps/liblive-fedcba9876543210.rlib"), old);
        read_at(&profile.join("live"), old);
        read_at(&profile.join("live.d"), old);
        let swept = sweep(&root, now - 86400., true).unwrap();
        assert_eq!((swept.removed, swept.kept, swept.busy), (1, 1, 0));
        assert!(!profile.join(".fingerprint/gone-0123456789abcdef").exists());
        assert!(!profile.join("deps/libgone-0123456789abcdef.rlib").exists());
        assert!(!profile.join("build/gone-0123456789abcdef").exists());
        assert!(profile.join("deps/liblive-fedcba9876543210.rlib").is_file());
        assert!(profile.join("live").is_file() && profile.join("live.d").is_file());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn sweep_passes_over_a_profile_a_build_holds() {
        let root = temp();
        let old = crate::now() - 5. * 86400.;
        let profile = root.join("release");
        read_at(&profile.join(".fingerprint/gone-0123456789abcdef/lib-gone"), old);
        read_at(&profile.join("deps/libgone-0123456789abcdef.rlib"), old);
        let build = std::fs::File::create(profile.join(".cargo-build-lock")).unwrap();
        build.lock().unwrap();
        let swept = sweep(&root, crate::now() - 86400., true).unwrap();
        assert_eq!((swept.removed, swept.busy), (0, 1));
        assert!(profile.join("deps/libgone-0123456789abcdef.rlib").is_file());
        drop(build);
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn unit_hash_reads_the_name_suffix() {
        assert_eq!(unit_hash("libhsm_kernel-00844a35c28df087.rlib"), Some("00844a35c28df087"));
        assert_eq!(unit_hash("hsm-kernel-00844a35c28df087"), Some("00844a35c28df087"));
        assert_eq!(unit_hash("cafe-deadbeefdeadbeef-00844a35c28df087.d"), Some("00844a35c28df087"));
        assert_eq!(unit_hash("hsm_kernel-1x2y3z"), None);
        assert_eq!(unit_hash("hsm"), None);
    }
}
