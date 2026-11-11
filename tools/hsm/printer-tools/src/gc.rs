//! Retain recent timelapses and durably archive each stable clip before explicit removal.
use crate::{digest, ftp::Ftp, Args};
use anyhow::{bail, Context, Result};
use sha2::{Digest, Sha256};
use std::{
    fs::{self, File, OpenOptions},
    io::Write,
    os::fd::AsRawFd,
    path::{Path, PathBuf},
    time::{Duration, SystemTime, UNIX_EPOCH},
};
#[cfg(target_os = "macos")]
use std::os::unix::fs::OpenOptionsExt;

/// Flush directory metadata without asking iCloud to materialize its contents.
pub fn sync_directory(directory: &Path) -> Result<()> {
    let mut options = OpenOptions::new();
    options.read(true);
    #[cfg(target_os = "macos")]
    options.custom_flags(libc::O_EVTONLY | libc::O_DIRECTORY);
    options.open(directory)?.sync_all()?;
    Ok(())
}

#[derive(Clone, Debug)]
pub struct Clip {
    pub name: String,
    pub path: String,
    pub size: u64,
    pub mtime: Option<i64>,
}
pub trait Remote {
    fn metadata(&mut self, path: &str) -> Result<(u64, i64)>;
    fn retrieve(&mut self, path: &str, sink: &mut dyn Write) -> Result<()>;
    fn delete(&mut self, path: &str) -> Result<()>;
}
pub struct Policy {
    pub keep_gb: Option<f64>,
    pub keep_count: Option<usize>,
    pub max_age_days: Option<f64>,
    pub min_age_hours: f64,
}
pub fn plan(clips: &[Clip], now: i64, policy: &Policy) -> (Vec<Clip>, Vec<Clip>) {
    let (mut keep, mut candidates): (Vec<_>, Vec<_>) = clips.iter().cloned().partition(|c| {
        c.name.to_ascii_lowercase().starts_with("temp")
            || c.size == 0
            || c.mtime.is_none()
            || c.mtime
                .is_some_and(|mtime| (now - mtime) as f64 / 3600. < policy.min_age_hours)
    });
    candidates.sort_by_key(|c| std::cmp::Reverse(c.mtime));
    let mut bytes: u64 = keep.iter().map(|c| c.size).sum();
    let mut delete = Vec::new();
    for clip in candidates {
        let too_old = policy.max_age_days.is_some_and(|age| {
            clip.mtime
                .is_some_and(|mtime| (now - mtime) as f64 / 86400. > age)
        });
        let over_size = policy
            .keep_gb
            .is_some_and(|budget| (bytes + clip.size) as f64 > budget * 1_000_000_000.);
        let over_count = policy.keep_count.is_some_and(|count| keep.len() >= count);
        if too_old || over_size || over_count {
            delete.push(clip)
        } else {
            bytes += clip.size;
            keep.push(clip)
        }
    }
    delete.sort_by_key(|c| c.mtime);
    (delete, keep)
}
pub struct ArchiveLock {
    _file: File,
}
impl ArchiveLock {
    pub fn open(directory: &Path) -> Result<Self> {
        fs::create_dir_all(directory)?;
        let mut options = OpenOptions::new();
        options.write(true).create(true).truncate(false);
        #[cfg(target_os = "macos")]
        options.custom_flags(libc::O_EVTONLY);
        let file = options.open(directory.join(".rotation.lock"))?;
        if unsafe { libc::flock(file.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } != 0 {
            bail!("Another rotation is using this archive directory")
        };
        Ok(Self { _file: file })
    }
}
struct Temporary {
    path: PathBuf,
}
impl Temporary {
    fn new(directory: &Path, prefix: &str) -> Result<(Self, File)> {
        for index in 0..100 {
            let path = directory.join(format!(
                ".{prefix}-{}-{}-{index}.part",
                std::process::id(),
                SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos()
            ));
            match OpenOptions::new().write(true).create_new(true).open(&path) {
                Ok(file) => return Ok((Self { path }, file)),
                Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => continue,
                Err(e) => return Err(e.into()),
            }
        }
        bail!("Could not reserve an archive temporary file")
    }
}
impl Drop for Temporary {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.path);
    }
}
struct Download<'a> {
    file: &'a mut File,
    hash: Sha256,
    bytes: u64,
}
impl Write for Download<'_> {
    fn write(&mut self, bytes: &[u8]) -> std::io::Result<usize> {
        let written = self.file.write(bytes)?;
        self.hash.update(&bytes[..written]);
        self.bytes += written as u64;
        Ok(written)
    }
    fn flush(&mut self) -> std::io::Result<()> {
        self.file.flush()
    }
}
fn expected(clip: &Clip) -> Result<(u64, i64)> {
    Ok((
        clip.size,
        clip.mtime.context("Cannot archive an unknown timestamp")?,
    ))
}
pub fn archive(
    remote: &mut dyn Remote,
    clip: &Clip,
    directory: &Path,
) -> Result<(PathBuf, String)> {
    if clip.name.is_empty()
        || matches!(clip.name.as_str(), "." | "..")
        || Path::new(&clip.name).file_name().and_then(|p| p.to_str()) != Some(clip.name.as_str())
    {
        bail!("Clip must have a plain filename")
    }
    let expected = expected(clip)?;
    if remote.metadata(&clip.path)? != expected {
        bail!("Remote clip changed since listing: {}", clip.name)
    }
    fs::create_dir_all(directory)?;
    let destination = directory.join(&clip.name);
    let (temporary, mut file) = Temporary::new(directory, "clip")?;
    let mut download = Download {
        file: &mut file,
        hash: Sha256::new(),
        bytes: 0,
    };
    remote.retrieve(&clip.path, &mut download)?;
    download.flush()?;
    let bytes = download.bytes;
    let sha = format!("{:x}", download.hash.finalize());
    file.sync_all()?;
    if bytes != clip.size || file.metadata()?.len() != clip.size {
        bail!("Incomplete archive download: {}", clip.name)
    }
    if remote.metadata(&clip.path)? != expected {
        bail!("Remote clip changed during download: {}", clip.name)
    }
    if digest(&temporary.path)? != sha {
        bail!("Archive checksum verification failed: {}", clip.name)
    }
    if destination.exists()
        && (destination.metadata()?.len() != clip.size || digest(&destination)? != sha)
    {
        bail!(
            "Archive filename collision: {}; remote clip retained",
            clip.name
        )
    }
    fs::rename(&temporary.path, &destination)?;
    let (checksum, mut checksum_file) = Temporary::new(directory, "checksum")?;
    writeln!(checksum_file, "{sha}  {}", clip.name)?;
    checksum_file.sync_all()?;
    fs::rename(
        &checksum.path,
        directory.join(format!("{}.sha256", clip.name)),
    )?;
    sync_directory(directory)?;
    Ok((destination, sha))
}
pub fn archive_and_delete(
    remote: &mut dyn Remote,
    clip: &Clip,
    directory: &Path,
) -> Result<(PathBuf, String)> {
    let result = archive(remote, clip, directory)?;
    if remote.metadata(&clip.path)? != expected(clip)? {
        bail!("Remote clip changed before deletion: {}", clip.name)
    }
    remote.delete(&clip.path)?;
    Ok(result)
}
fn human(bytes: u64) -> String {
    let mut value = bytes as f64;
    for unit in ["B", "KB", "MB", "GB", "TB"] {
        if value < 1000. || unit == "TB" {
            return format!("{value:.1} {unit}");
        }
        value /= 1000.
    }
    unreachable!()
}
pub fn run(args: &mut Args) -> Result<()> {
    let host = args
        .option("--host")
        .or_else(|| std::env::var("H2C_HOST").ok())
        .context("need --host/$H2C_HOST")?;
    let code = args
        .option("--access-code")
        .or_else(|| std::env::var("H2C_ACCESS_CODE").ok())
        .context("need --access-code/$H2C_ACCESS_CODE")?;
    let user = args.option("--user").unwrap_or_else(|| "bblp".into());
    let port = args.number("--port", 990_u16)?;
    let timeout = args.number("--timeout", 30_f64)?;
    let folder = args
        .option("--folder")
        .unwrap_or_else(|| "timelapse".into());
    let thumb = args
        .option("--thumb-folder")
        .unwrap_or_else(|| format!("{folder}/thumbnail"));
    let pattern = args.option("--pattern").unwrap_or_else(|| "*.mp4".into());
    let keep_gb = args.number("--keep-gb", 0_f64)?;
    let keep = args.number("--keep", 96_usize)?;
    let min_age = args.number("--min-age-hours", 2_f64)?;
    let max_age = args
        .option("--max-age-days")
        .map(|s| s.parse::<f64>())
        .transpose()?;
    let directory = args.option("--archive-dir").map(|p| crate::expand(&p));
    let apply = args.flag("--apply");
    let list = args.flag("--list");
    let prune = args.flag("--prune-thumbnails");
    args.finish()?;
    if host.is_empty() || code.is_empty() {
        bail!("need --host/$H2C_HOST and --access-code/$H2C_ACCESS_CODE")
    }
    if apply && directory.is_none() {
        bail!("--apply requires --archive-dir; clips must be backed up before removal")
    }
    if !timeout.is_finite()
        || timeout <= 0.
        || !keep_gb.is_finite()
        || keep_gb < 0.
        || !min_age.is_finite()
        || min_age < 0.
        || max_age.is_some_and(|n| !n.is_finite() || n < 0.)
    {
        bail!("Timeout must be positive and retention limits nonnegative")
    }
    let _lock = if apply {
        Some(ArchiveLock::open(directory.as_ref().unwrap())?)
    } else {
        None
    };
    let now = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs() as i64;
    let mut ftp = Ftp::new(host, port, user, code, Duration::from_secs_f64(timeout))?;
    let clips = ftp.list(&folder, &pattern)?;
    println!(
        "Bambu /{}: {} clip(s), {} total",
        folder.trim_matches('/'),
        clips.len(),
        human(clips.iter().map(|c| c.size).sum())
    );
    if list || clips.is_empty() {
        for clip in clips {
            println!(
                "  {}  {:>9}  {}",
                crate::timestamp(clip.mtime),
                human(clip.size),
                clip.name
            )
        }
        return Ok(());
    }
    let (delete, keep) = plan(
        &clips,
        now,
        &Policy {
            keep_gb: (keep_gb > 0.).then_some(keep_gb),
            keep_count: Some(keep),
            max_age_days: max_age,
            min_age_hours: min_age,
        },
    );
    let freed = delete.iter().map(|c| c.size).sum();
    println!(
        "Keeping {} clip(s) ({}); {} {} ({}).",
        keep.len(),
        human(keep.iter().map(|c| c.size).sum()),
        if apply { "deleting" } else { "would delete" },
        delete.len(),
        human(freed)
    );
    for clip in delete {
        if !apply {
            println!(
                "  would delete  {}  {:>9}  {}",
                crate::timestamp(clip.mtime),
                human(clip.size),
                clip.name
            );
            continue;
        }
        let (destination, sha) = archive_and_delete(&mut ftp, &clip, directory.as_ref().unwrap())?;
        println!(
            "  archived      {} -> {}  sha256={sha}\n  deleted       {}  {:>9}  {}",
            clip.name,
            destination.display(),
            crate::timestamp(clip.mtime),
            human(clip.size),
            clip.name
        );
        if prune {
            let stem = Path::new(&clip.name).file_stem().unwrap().to_string_lossy();
            let path = format!("/{}/{stem}.jpg", thumb.trim_matches('/'));
            let _ = ftp.delete(&path);
        }
    }
    if apply {
        println!("Done. Freed {}.", human(freed))
    } else {
        println!("Dry run -- re-run with --apply to delete.")
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    struct Fixture {
        data: Vec<u8>,
        mtime: i64,
        metadata_calls: usize,
        change_at: Option<usize>,
        truncate: bool,
        deleted: bool,
    }
    impl Remote for Fixture {
        fn metadata(&mut self, _: &str) -> Result<(u64, i64)> {
            self.metadata_calls += 1;
            Ok((
                self.data.len() as u64,
                self.mtime + i64::from(self.change_at == Some(self.metadata_calls)),
            ))
        }
        fn retrieve(&mut self, _: &str, sink: &mut dyn Write) -> Result<()> {
            let len = self.data.len() - usize::from(self.truncate);
            sink.write_all(&self.data[..len])?;
            Ok(())
        }
        fn delete(&mut self, _: &str) -> Result<()> {
            self.deleted = true;
            Ok(())
        }
    }
    fn fixture() -> Fixture {
        Fixture {
            data: b"retained physical recording".to_vec(),
            mtime: 10,
            metadata_calls: 0,
            change_at: None,
            truncate: false,
            deleted: false,
        }
    }
    #[test]
    fn remote_removal_requires_durable_identical_local_bytes_and_stable_metadata() {
        let root = std::env::temp_dir().join(format!(
            "hsm-printer-gc-{}-{}",
            std::process::id(),
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        for change in [Some(1), Some(2), Some(3), None] {
            let mut remote = fixture();
            remote.change_at = change;
            let clip = Clip {
                name: "clip.mp4".into(),
                path: "/timelapse/clip.mp4".into(),
                size: remote.data.len() as u64,
                mtime: Some(remote.mtime),
            };
            let directory = root.join(format!("case-{change:?}"));
            let result = archive_and_delete(&mut remote, &clip, &directory);
            assert_eq!(result.is_ok(), change.is_none());
            assert_eq!(remote.deleted, change.is_none());
            if let Ok((path, sha)) = result {
                assert_eq!(fs::read(path).unwrap(), remote.data);
                assert_eq!(sha, crate::hash(&remote.data));
            }
        }
        let mut remote = fixture();
        remote.truncate = true;
        let clip = Clip {
            name: "clip.mp4".into(),
            path: "/clip.mp4".into(),
            size: remote.data.len() as u64,
            mtime: Some(10),
        };
        assert!(archive_and_delete(&mut remote, &clip, &root.join("truncated")).is_err());
        assert!(!remote.deleted);
        let directory = root.join("collision");
        fs::create_dir_all(&directory).unwrap();
        fs::write(directory.join("clip.mp4"), b"different").unwrap();
        let mut remote = fixture();
        assert!(archive_and_delete(&mut remote, &clip, &directory).is_err());
        assert!(!remote.deleted);
        assert_eq!(fs::read(directory.join("clip.mp4")).unwrap(), b"different");
        let lock = ArchiveLock::open(&directory).unwrap();
        assert!(ArchiveLock::open(&directory).is_err());
        drop(lock);
        assert!(ArchiveLock::open(&directory).is_ok());
        fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn active_and_unknown_clips_count_towards_the_retention_budget() {
        let clips = vec![
            Clip {
                name: "temp.mp4".into(),
                path: String::new(),
                size: 5,
                mtime: Some(1),
            },
            Clip {
                name: "unknown.mp4".into(),
                path: String::new(),
                size: 5,
                mtime: None,
            },
            Clip {
                name: "old.mp4".into(),
                path: String::new(),
                size: 5,
                mtime: Some(1),
            },
            Clip {
                name: "new.mp4".into(),
                path: String::new(),
                size: 5,
                mtime: Some(100000),
            },
        ];
        let (delete, keep) = plan(
            &clips,
            100000,
            &Policy {
                keep_gb: None,
                keep_count: Some(3),
                max_age_days: None,
                min_age_hours: 2.,
            },
        );
        assert_eq!(
            delete.iter().map(|c| c.name.as_str()).collect::<Vec<_>>(),
            ["old.mp4"]
        );
        assert_eq!(keep.len(), 3);
    }
}
