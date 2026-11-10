//! hsm-land lands commits on main and merges incoming changes into the shared checkout.
use anyhow::{Context, Result, bail, ensure};
use fs2::FileExt;
use serde_json::json;
use std::{
    collections::{BTreeMap, BTreeSet},
    env, fs,
    io::Write,
    os::unix::{
        ffi::OsStrExt,
        fs::{PermissionsExt, symlink},
    },
    path::PathBuf,
    process::{Command, Output, Stdio},
    time::{Instant, SystemTime, UNIX_EPOCH},
};

const POINTERS: &str = "hardware/cad-artifacts.json";
const UPSTREAM: &str = "origin/main";
const ATTEMPTS: usize = 6;
const CLEAR_ENV: &[&str] = &[
    "GIT_DIR",
    "GIT_INDEX_FILE",
    "GIT_WORK_TREE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_COMMON_DIR",
    "GIT_PREFIX",
];

#[derive(Clone, Debug, PartialEq, Eq)]
struct Entry {
    mode: String,
    blob: String,
}

struct Repo {
    root: PathBuf,
}

struct OwnedPath {
    path: PathBuf,
    remove: bool,
}
impl Drop for OwnedPath {
    fn drop(&mut self) {
        if self.remove {
            let _ = fs::remove_file(&self.path);
        }
    }
}

fn string(bytes: &[u8]) -> String {
    String::from_utf8_lossy(bytes).trim_end().to_owned()
}
fn quote(text: &str) -> String {
    format!("'{}'", text.replace('\'', "'\"'\"'"))
}

impl Repo {
    fn index_git(
        &self,
        index: &std::path::Path,
        args: &[&str],
        input: Option<&[u8]>,
    ) -> Result<String> {
        let mut command = self.command();
        command
            .env("GIT_INDEX_FILE", index)
            .args(args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        if input.is_some() {
            command.stdin(Stdio::piped());
        }
        let mut child = command.spawn()?;
        if let Some(bytes) = input {
            child
                .stdin
                .take()
                .context("index stdin")?
                .write_all(bytes)?;
        }
        let out = child.wait_with_output()?;
        ensure!(
            out.status.success(),
            "git {}: {}",
            args.join(" "),
            string(&out.stderr)
        );
        Ok(string(&out.stdout))
    }

    /// Commit frozen blobs while retaining concurrent files and unrelated staged edits.
    fn commit_snapshot(&self, snapshot: &serde_json::Value) -> Result<serde_json::Value> {
        let message = snapshot["message"].as_str().context("snapshot message")?;
        ensure!(
            !message.trim().is_empty(),
            "snapshot needs a commit message"
        );
        let files = snapshot["files"].as_array().context("snapshot files")?;
        ensure!(!files.is_empty(), "snapshot needs selected files");
        let mut requested = BTreeMap::new();
        for file in files {
            let path = file["path"].as_str().context("snapshot file path")?;
            let parts = std::path::Path::new(path).components().collect::<Vec<_>>();
            ensure!(
                !parts.is_empty()
                    && parts
                        .iter()
                        .all(|p| matches!(p, std::path::Component::Normal(_)))
                    && !path.starts_with(".git/")
                    && path != ".git",
                "snapshot path must be a repository file: {path}"
            );
            let blob = file["blob"].as_str().context("snapshot blob id")?;
            ensure!(
                [40, 64].contains(&blob.len()) && blob.bytes().all(|b| b.is_ascii_hexdigit()),
                "snapshot blob id {blob}"
            );
            ensure!(
                self.git(&["cat-file", "-t", blob])? == "blob",
                "snapshot object is not a blob: {blob}"
            );
            let mode = file
                .get("mode")
                .and_then(|v| v.as_str())
                .unwrap_or("100644");
            ensure!(
                ["100644", "100755", "120000"].contains(&mode),
                "snapshot mode {mode}"
            );
            ensure!(
                requested
                    .insert(
                        path.to_owned(),
                        Entry {
                            mode: mode.into(),
                            blob: blob.into()
                        }
                    )
                    .is_none(),
                "duplicate snapshot path {path}"
            );
        }
        let index_path = self
            .root
            .join(self.git(&["rev-parse", "--git-path", "index"])?);
        let lock_path = index_path.with_extension("lock");
        let mut lock_file = fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&lock_path)
            .with_context(|| {
                format!("{} is in use; retry the frozen commit", lock_path.display())
            })?;
        let mut lock = OwnedPath {
            path: lock_path,
            remove: true,
        };
        let unique = format!(
            "hsm-snapshot-{}-{}",
            std::process::id(),
            SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos()
        );
        let folder = index_path.parent().context("index directory")?;
        let alternate = OwnedPath {
            path: folder.join(&unique),
            remove: true,
        };
        let preserved = OwnedPath {
            path: folder.join(format!("{unique}-staged")),
            remove: true,
        };
        for _ in 0..ATTEMPTS {
            let pre = self.git(&["rev-parse", "HEAD"])?;
            let tree = self.tree(&pre)?;
            let current = self.index()?;
            let changes = requested
                .iter()
                .filter(|(path, entry)| tree.get(*path) != Some(*entry))
                .collect::<Vec<_>>();
            if changes.is_empty() {
                return Ok(json!({"commit":pre,"changed":false}));
            }
            self.index_git(&alternate.path, &["read-tree", &pre], None)?;
            let staged = requested
                .iter()
                .map(|(path, e)| format!("{} {}\t{path}\0", e.mode, e.blob))
                .collect::<String>();
            self.index_git(
                &alternate.path,
                &["update-index", "-z", "--index-info"],
                Some(staged.as_bytes()),
            )?;
            let written = self.index_git(&alternate.path, &["write-tree"], None)?;
            let made = self.output(
                &["commit-tree", &written, "-p", &pre],
                Some(message.as_bytes()),
            )?;
            ensure!(
                made.status.success(),
                "create frozen commit: {}",
                string(&made.stderr)
            );
            let commit = string(&made.stdout);
            fs::copy(&index_path, &preserved.path)?;
            let index_updates = requested
                .iter()
                .filter(|(path, _)| current.get(*path) == tree.get(*path))
                .map(|(path, e)| format!("{} {}\t{path}\0", e.mode, e.blob))
                .collect::<String>();
            if !index_updates.is_empty() {
                self.index_git(
                    &preserved.path,
                    &["update-index", "-z", "--index-info"],
                    Some(index_updates.as_bytes()),
                )?;
            }
            if !self.ok(&[
                "update-ref",
                "-m",
                "commit frozen publication",
                "HEAD",
                &commit,
                &pre,
            ])? {
                continue;
            }
            lock_file.write_all(&fs::read(&preserved.path)?)?;
            lock_file.sync_all()?;
            fs::rename(&lock.path, &index_path)?;
            lock.remove = false;
            return Ok(json!({"commit":commit,"changed":true}));
        }
        bail!("HEAD kept moving; frozen blobs remain available to retry")
    }
    fn command(&self) -> Command {
        let mut cmd = Command::new("git");
        cmd.current_dir(&self.root)
            .env("HSM_PUSHING", "1")
            .env("HSM_SKIP_PRECOMMIT", "1");
        for key in CLEAR_ENV {
            cmd.env_remove(key);
        }
        cmd
    }

    fn output(&self, args: &[&str], input: Option<&[u8]>) -> Result<Output> {
        let mut cmd = self.command();
        cmd.args(args).stdout(Stdio::piped()).stderr(Stdio::piped());
        if input.is_some() {
            cmd.stdin(Stdio::piped());
        }
        let started = Instant::now();
        let mut child = cmd
            .spawn()
            .with_context(|| format!("start git {}", args.join(" ")))?;
        if let Some(bytes) = input {
            child.stdin.take().context("git stdin")?.write_all(bytes)?;
        }
        let out = child.wait_with_output()?;
        if matches!(args.first().copied(), Some("fetch" | "push")) {
            if let Some(path) = env::var_os("HSM_PUBLISH_TIMING") {
                let append = || -> Result<()> {
                    let mut log = fs::OpenOptions::new()
                        .create(true)
                        .append(true)
                        .open(path)?;
                    writeln!(
                        log,
                        "{}",
                        json!({"phase":format!("git.{}",args[0]),"pid":std::process::id(),"wall_time_ns":SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos(),"seconds":started.elapsed().as_secs_f64(),"exit_code":out.status.code()})
                    )?;
                    Ok(())
                };
                if let Err(e) = append() {
                    eprintln!("publication timing unavailable: {e:#}");
                }
            }
        }
        Ok(out)
    }

    fn git(&self, args: &[&str]) -> Result<String> {
        let out = self.output(args, None)?;
        ensure!(
            out.status.success(),
            "git {}: {}",
            args.join(" "),
            string(&out.stderr)
        );
        Ok(string(&out.stdout))
    }
    fn ok(&self, args: &[&str]) -> Result<bool> {
        Ok(self.output(args, None)?.status.success())
    }
    fn blob(&self, id: &str) -> Result<Vec<u8>> {
        let out = self.output(&["cat-file", "blob", id], None)?;
        ensure!(
            out.status.success(),
            "read blob {id}: {}",
            string(&out.stderr)
        );
        Ok(out.stdout)
    }
    fn hash(&self, bytes: &[u8]) -> Result<String> {
        let out = self.output(&["hash-object", "--stdin"], Some(bytes))?;
        ensure!(
            out.status.success(),
            "hash working copy: {}",
            string(&out.stderr)
        );
        Ok(string(&out.stdout))
    }
    fn tree(&self, revision: &str) -> Result<BTreeMap<String, Entry>> {
        let out = self.output(&["ls-tree", "-r", "-z", revision], None)?;
        ensure!(
            out.status.success(),
            "read tree {revision}: {}",
            string(&out.stderr)
        );
        let mut entries = BTreeMap::new();
        for row in out.stdout.split(|b| *b == 0).filter(|b| !b.is_empty()) {
            let (meta, path) =
                row.split_at(row.iter().position(|b| *b == b'\t').context("tree entry")?);
            let fields: Vec<_> = std::str::from_utf8(meta)?.split_whitespace().collect();
            entries.insert(
                std::str::from_utf8(&path[1..])?.to_owned(),
                Entry {
                    mode: fields[0].to_owned(),
                    blob: fields[2].to_owned(),
                },
            );
        }
        Ok(entries)
    }
    fn index(&self) -> Result<BTreeMap<String, Entry>> {
        let out = self.output(&["ls-files", "--stage", "-z"], None)?;
        ensure!(out.status.success(), "read index: {}", string(&out.stderr));
        let mut entries = BTreeMap::new();
        for row in out.stdout.split(|b| *b == 0).filter(|b| !b.is_empty()) {
            let (meta, path) = row.split_at(
                row.iter()
                    .position(|b| *b == b'\t')
                    .context("index entry")?,
            );
            let fields: Vec<_> = std::str::from_utf8(meta)?.split_whitespace().collect();
            ensure!(
                fields[2] == "0",
                "resolve the index conflict in {} before landing",
                std::str::from_utf8(&path[1..])?
            );
            entries.insert(
                std::str::from_utf8(&path[1..])?.to_owned(),
                Entry {
                    mode: fields[0].to_owned(),
                    blob: fields[1].to_owned(),
                },
            );
        }
        Ok(entries)
    }
    fn patch_ids(&self, range: &str) -> Result<BTreeMap<String, String>> {
        let mut ids = BTreeMap::new();
        for sha in self.git(&["rev-list", range])?.lines() {
            let show = self.output(&["show", sha], None)?;
            ensure!(show.status.success(), "read patch {sha}");
            let out = self.output(&["patch-id", "--stable"], Some(&show.stdout))?;
            ensure!(out.status.success(), "identify patch {sha}");
            if let Some(id) = string(&out.stdout).split_whitespace().next() {
                ids.insert(id.to_owned(), sha.to_owned());
            }
        }
        Ok(ids)
    }
    fn merge_driver(&self) -> Result<Option<PathBuf>> {
        let sibling = env::current_exe()?
            .parent()
            .context("executable directory")?
            .join("hsm-merge-pointers");
        let mut choices = Vec::new();
        if let Some(p) = env::var_os("HSM_MERGE_POINTERS") {
            choices.push(PathBuf::from(p));
        }
        choices.push(
            self.root
                .join("tools/hsm/target/release/hsm-merge-pointers"),
        );
        choices.push(sibling);
        if let Some(home) = env::var_os("HOME") {
            choices.push(PathBuf::from(home).join(".local/bin/hsm-merge-pointers"));
        }
        let found = choices.into_iter().find(|p| p.is_file());
        if self.root.join(POINTERS).exists() {
            ensure!(
                found.is_some(),
                "install hsm-merge-pointers before landing CAD publications"
            );
        }
        Ok(found)
    }
    fn configure_driver(&self) -> Result<()> {
        if let Some(binary) = self.merge_driver()? {
            let command = format!("{} %O %A %B", quote(&binary.to_string_lossy()));
            if self
                .git(&["config", "--get", "merge.cadpointers.driver"])
                .unwrap_or_default()
                != command
            {
                self.git(&["config", "merge.cadpointers.driver", &command])?;
                self.git(&[
                    "config",
                    "merge.cadpointers.name",
                    "the CAD pointer file, merged by member",
                ])?;
            }
        }
        Ok(())
    }
    fn replay(&self, sha: &str, onto: &str) -> Result<Option<String>> {
        let parent = self.git(&["rev-parse", &format!("{sha}^")])?;
        let merged = self.output(
            &[
                "merge-tree",
                "--write-tree",
                &format!("--merge-base={parent}"),
                onto,
                sha,
            ],
            None,
        )?;
        if merged.status.code() == Some(1) {
            return Ok(None);
        }
        ensure!(
            merged.status.success(),
            "merge {sha}: {}",
            string(&merged.stderr)
        );
        let tree = std::str::from_utf8(&merged.stdout)?
            .lines()
            .next()
            .context("merged tree")?;
        let original = self.output(
            &["show", "-s", "--format=%an%x00%ae%x00%aI%x00%B", sha],
            None,
        )?;
        ensure!(original.status.success(), "read commit author {sha}");
        let fields: Vec<_> = original.stdout.splitn(4, |b| *b == 0).collect();
        ensure!(fields.len() == 4, "commit author fields {sha}");
        let mut cmd = self.command();
        cmd.args(["commit-tree", tree, "-p", onto])
            .env("GIT_AUTHOR_NAME", std::str::from_utf8(fields[0])?)
            .env("GIT_AUTHOR_EMAIL", std::str::from_utf8(fields[1])?)
            .env("GIT_AUTHOR_DATE", std::str::from_utf8(fields[2])?)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        let mut child = cmd.spawn()?;
        child
            .stdin
            .take()
            .context("commit message stdin")?
            .write_all(fields[3])?;
        let made = child.wait_with_output()?;
        ensure!(
            made.status.success(),
            "create replayed commit: {}",
            string(&made.stderr)
        );
        Ok(Some(string(&made.stdout)))
    }
    fn disk(&self, path: &str) -> Result<Option<Vec<u8>>> {
        let path = self.root.join(path);
        match fs::symlink_metadata(&path) {
            Ok(m) if m.file_type().is_symlink() => {
                Ok(Some(fs::read_link(path)?.as_os_str().as_bytes().to_vec()))
            }
            Ok(m) if m.is_file() => Ok(Some(fs::read(path)?)),
            Ok(_) => bail!("{} is a directory; leave it in place", path.display()),
            Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(None),
            Err(e) => Err(e.into()),
        }
    }
    fn write_work(&self, name: &str, entry: Option<&Entry>, bytes: Option<&[u8]>) -> Result<()> {
        let path = self.root.join(name);
        if let Some(entry) = entry {
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent)?;
            }
            if entry.mode == "120000" {
                if path.symlink_metadata().is_ok() {
                    fs::remove_file(&path)?;
                }
                symlink(
                    std::ffi::OsStr::from_bytes(bytes.context("symlink target")?),
                    &path,
                )?;
            } else {
                let temp = path.with_file_name(format!(
                    ".hsm-land-{}-{}",
                    std::process::id(),
                    path.file_name().context("file name")?.to_string_lossy()
                ));
                fs::write(&temp, bytes.context("file bytes")?)?;
                fs::set_permissions(
                    &temp,
                    fs::Permissions::from_mode(if entry.mode == "100755" { 0o755 } else { 0o644 }),
                )?;
                fs::rename(temp, path)?;
            }
        } else if path.symlink_metadata().is_ok() {
            fs::remove_file(path)?;
        }
        Ok(())
    }
    fn merge_work(
        &self,
        name: &str,
        work: &[u8],
        base: &Entry,
        incoming: &Entry,
        label: &str,
    ) -> Result<(Vec<u8>, bool)> {
        let dir = self
            .root
            .join(self.git(&["rev-parse", "--git-path", "hsm-land-merge"])?);
        fs::create_dir_all(&dir)?;
        let result = (|| -> Result<(Vec<u8>, bool)> {
            let a = dir.join("work");
            let b = dir.join("base");
            let c = dir.join("incoming");
            fs::write(&a, work)?;
            fs::write(&b, self.blob(&base.blob)?)?;
            fs::write(&c, self.blob(&incoming.blob)?)?;
            if name == POINTERS {
                if let Some(driver) = self.merge_driver()? {
                    let run = Command::new(driver).args([&b, &a, &c]).output()?;
                    if run.status.success() {
                        return Ok((fs::read(&a)?, false));
                    }
                    eprintln!("pointer merge: {}", string(&run.stderr));
                }
            }
            let run = self.output(
                &[
                    "merge-file",
                    "-p",
                    "-L",
                    "this tree",
                    "-L",
                    "base",
                    "-L",
                    label,
                    a.to_str().context("merge path")?,
                    b.to_str().context("base path")?,
                    c.to_str().context("incoming path")?,
                ],
                None,
            )?;
            ensure!(
                run.status.code().is_some_and(|s| (0..128).contains(&s)),
                "merge {name}: {}",
                string(&run.stderr)
            );
            Ok((run.stdout, !run.status.success()))
        })();
        let _ = fs::remove_dir_all(dir);
        result
    }
    fn settle(&self, pre: &str, landed: &str, base: &str, dry: bool) -> Result<bool> {
        let before = self.tree(base)?;
        let local = self.tree(pre)?;
        let remote = self.tree(landed)?;
        let index = self.index()?;
        let paths: BTreeSet<_> = before
            .keys()
            .chain(local.keys())
            .chain(remote.keys())
            .filter(|p| before.get(*p) != remote.get(*p) || local.get(*p) != remote.get(*p))
            .cloned()
            .collect();
        if !dry {
            if self.git(&["rev-parse", "HEAD"])? != pre {
                return Ok(false);
            }
            self.git(&["update-ref", "ORIG_HEAD", pre])?;
            if !self.ok(&["update-ref", "HEAD", landed, pre])? {
                return Ok(false);
            }
            let mut updates = Vec::new();
            for p in local.keys().chain(remote.keys()).collect::<BTreeSet<_>>() {
                if local.get(p) == remote.get(p) || index.get(p) != local.get(p) {
                    continue;
                }
                if let Some(e) = remote.get(p) {
                    updates.extend_from_slice(format!("{} {}\t{}\0", e.mode, e.blob, p).as_bytes());
                } else {
                    updates.extend_from_slice(format!("0 {}\t{}\0", "0".repeat(40), p).as_bytes());
                }
            }
            if !updates.is_empty() {
                let done = self.output(&["update-index", "-z", "--index-info"], Some(&updates))?;
                ensure!(
                    done.status.success(),
                    "bring index to landed tree: {}",
                    string(&done.stderr)
                );
            }
        }
        let mut advanced = 0;
        let mut merged = 0;
        for p in paths {
            let b = before.get(&p);
            let l = remote.get(&p);
            let work = match self.disk(&p) {
                Ok(w) => w,
                Err(e) => {
                    eprintln!("left alone: {p}: {e:#}");
                    continue;
                }
            };
            let hash = work.as_ref().map(|bytes| self.hash(bytes)).transpose()?;
            if hash.as_deref() == l.map(|e| e.blob.as_str()) || l == b {
                continue;
            }
            if hash.as_deref() == b.map(|e| e.blob.as_str()) {
                advanced += 1;
                if !dry {
                    let bytes = l.map(|e| self.blob(&e.blob)).transpose()?;
                    if self.disk(&p)? == work {
                        self.write_work(&p, l, bytes.as_deref())?;
                    } else {
                        eprintln!("left alone: {p}: edited while main arrived");
                    }
                }
                continue;
            }
            let (Some(b), Some(l), Some(work)) = (b, l, work) else {
                eprintln!(
                    "left alone: {p}: added, deleted or changed on both sides; incoming copy is {landed}:{p}"
                );
                continue;
            };
            let attr = self.git(&["check-attr", "merge", "--", &p])?;
            let binary = self
                .git(&["diff", "--numstat", base, landed, "--", &p])?
                .starts_with("-\t-")
                || attr.ends_with(": unset")
                || b.mode == "120000"
                || l.mode == "120000"
                || work.contains(&0);
            if binary {
                eprintln!(
                    "left alone: {p}: binary changed on both sides; incoming copy is {landed}:{p}"
                );
                continue;
            }
            merged += 1;
            if dry {
                continue;
            }
            let met = self.git(&[
                "log",
                "-1",
                "--format=%h %s [%(trailers:key=Session,valueonly)]",
                &format!("{base}..{landed}"),
                "--",
                &p,
            ])?;
            let label = format!("main {met}");
            let (bytes, marked) = self.merge_work(&p, &work, b, l, &label)?;
            if self.disk(&p)?.as_deref() == Some(work.as_slice()) {
                self.write_work(&p, Some(l), Some(&bytes))?;
                if marked {
                    eprintln!("CONFLICT MARKERS: {p}; met {met}; resolve and commit this path");
                }
            } else {
                eprintln!("left alone: {p}: edited while main arrived");
            }
        }
        println!(
            "{} main's files: {advanced} advanced, {merged} merged; edits and staged work retained",
            if dry { "would bring" } else { "brought" }
        );
        Ok(true)
    }
    fn land(&self, check: bool) -> Result<i32> {
        if !check {
            self.configure_driver()?;
        }
        let started = Instant::now();
        for attempt in 1..=ATTEMPTS {
            self.git(&["fetch", "--quiet", "origin", "main"])?;
            let pre = self.git(&["rev-parse", "HEAD"])?;
            let up = self.git(&["rev-parse", UPSTREAM])?;
            self.git(&["merge-base", &pre, &up])?;
            let ahead = self.git(&["rev-list", "--count", &format!("{up}..{pre}")])?;
            let behind = self.git(&["rev-list", "--count", &format!("{pre}..{up}")])?;
            if ahead == "0" && behind == "0" {
                println!(
                    "already on {UPSTREAM} ({:.1}s)",
                    started.elapsed().as_secs_f64()
                );
                return Ok(0);
            }
            if ahead == "0" {
                if self.settle(&pre, &up, &pre, check)? {
                    return Ok(0);
                }
                continue;
            }
            let mine = self.patch_ids(&format!("{up}..{pre}"))?;
            let theirs = if behind == "0" {
                BTreeMap::new()
            } else {
                self.patch_ids(&format!("{pre}..{up}"))?
            };
            let mut real = BTreeSet::new();
            let mut twins = 0;
            for (patch, sha) in &mine {
                if let Some(other) = theirs.get(patch) {
                    println!(
                        "{} is already on {UPSTREAM} as {} (same patch)",
                        &sha[..8],
                        &other[..8]
                    );
                    twins += 1;
                } else {
                    real.insert(sha.clone());
                }
            }
            if twins > 0 && real.is_empty() {
                if self.settle(&pre, &up, &pre, check)? {
                    return Ok(0);
                }
                continue;
            }
            if behind == "0" {
                if check {
                    println!("would push {ahead} commit(s) fast-forward");
                    return Ok(0);
                }
                if self.ok(&["push", "origin", "HEAD:main"])? {
                    println!(
                        "landed {ahead} commit(s) ({:.1}s)",
                        started.elapsed().as_secs_f64()
                    );
                    return Ok(0);
                }
                eprintln!("push lost a race ({attempt}/{ATTEMPTS}); reading main again");
                continue;
            }
            if check {
                println!(
                    "would replay {} commit(s), dropping {twins} twin(s)",
                    real.len()
                );
                self.settle(&pre, &up, &pre, true)?;
                return Ok(0);
            }
            let order: Vec<_> = self
                .git(&["rev-list", "--reverse", &format!("{up}..{pre}")])?
                .lines()
                .filter(|s| real.contains(*s))
                .map(str::to_owned)
                .collect();
            let mut landed = up.clone();
            let mut picked = 0;
            for sha in &order {
                let Some(next) = self.replay(sha, &landed)? else {
                    break;
                };
                landed = next;
                picked += 1;
            }
            if picked > 0 {
                if !self.ok(&["push", "origin", &format!("{landed}:main")])? {
                    eprintln!("push lost a race ({attempt}/{ATTEMPTS}); reading main again");
                    continue;
                }
                self.git(&["fetch", "--quiet", "origin", "main"])?;
            }
            let work_base = if picked < order.len() {
                self.git(&["rev-parse", &format!("{}^", order[picked])])?
            } else {
                pre.clone()
            };
            if !self.settle(&pre, &landed, &work_base, false)? {
                continue;
            }
            if picked < order.len() {
                eprintln!(
                    "{} commit(s) did not replay and stand uncommitted; ORIG_HEAD retains {pre}",
                    order.len() - picked
                );
                for sha in &order[picked..] {
                    eprintln!(
                        "  {} {}",
                        &sha[..8],
                        self.git(&["log", "-1", "--format=%s", sha])?
                    );
                }
                return Ok(1);
            }
            println!(
                "landed {picked} replayed commit(s) ({:.1}s)",
                started.elapsed().as_secs_f64()
            );
            return Ok(0);
        }
        eprintln!("main kept moving; work remains committed locally");
        Ok(1)
    }
}

fn run() -> Result<i32> {
    let mut root = None;
    let mut check = false;
    let mut snapshot = None;
    let mut args = env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--root" => {
                root = Some(PathBuf::from(
                    args.next().context("--root needs a directory")?,
                ))
            }
            "--check" => check = true,
            "--commit-snapshot" => {
                snapshot = Some(PathBuf::from(
                    args.next().context("--commit-snapshot needs a JSON path")?,
                ))
            }
            "-h" | "--help" => {
                println!(
                    "{}",
                    "Land commits on main and retain shared edits.\nUsage: hsm-land [--root DIRECTORY] [--check]\nCommit frozen blobs locally: hsm-land [--root DIRECTORY] --commit-snapshot JSON_PATH\nSnapshot: {message:string,files:[{path:string,blob:GitBlobId,mode?:string}]}\nThe snapshot operation leaves worktree edits in place and runs no hook; callers run post-commit after it returns."
                );
                return Ok(0);
            }
            _ => bail!("unknown argument {arg}"),
        }
    }
    ensure!(
        !(check && snapshot.is_some()),
        "--check and --commit-snapshot are separate operations"
    );
    if env::var_os("HSM_PUSHING").is_some() {
        ensure!(
            snapshot.is_none(),
            "a replay cannot create a publication snapshot"
        );
        return Ok(0);
    }
    let start = Repo {
        root: root.unwrap_or(env::current_dir()?),
    };
    let repo = Repo {
        root: PathBuf::from(start.git(&["rev-parse", "--show-toplevel"])?),
    };
    if repo.git(&["rev-parse", "--git-dir"])? != repo.git(&["rev-parse", "--git-common-dir"])? {
        println!("linked checkout: land from the shared main checkout");
        return Ok(0);
    }
    for state in ["rebase-merge", "rebase-apply"] {
        if repo
            .root
            .join(repo.git(&["rev-parse", "--git-path", state])?)
            .exists()
        {
            println!("{state} is in progress; leaving its commits alone");
            return Ok(0);
        }
    }
    for state in ["MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD"] {
        if repo.ok(&["rev-parse", "--verify", "-q", state])? {
            println!("{state} is in progress; leaving its commits alone");
            return Ok(0);
        }
    }
    let lock = fs::OpenOptions::new()
        .create(true)
        .truncate(false)
        .read(true)
        .write(true)
        .open(
            repo.root
                .join(repo.git(&["rev-parse", "--git-path", "hsm-land.lock"])?),
        )?;
    lock.lock_exclusive()?;
    if let Some(path) = snapshot {
        let frozen: serde_json::Value = serde_json::from_slice(&fs::read(path)?)?;
        println!("{}", repo.commit_snapshot(&frozen)?);
        return Ok(0);
    }
    repo.land(check)
}
fn main() {
    match run() {
        Ok(code) => std::process::exit(code),
        Err(e) => {
            eprintln!("hsm-land: {e:#}");
            std::process::exit(1)
        }
    }
}

#[cfg(test)]
mod tests;
