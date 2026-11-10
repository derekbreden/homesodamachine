//! Concurrent publication requests coalesce onto the newest completed files.
use crate::{ContextData, POINTERS, empty, is_viewer, keys, merge_maps, strings, timing};
use crate::{pack, transport::Transport};
use anyhow::{Context, Result, ensure};
use clap::Parser;
use serde_json::{Value, json};
use std::{
    fs::{self, OpenOptions},
    io::Write,
    path::PathBuf,
    time::Instant,
};

#[derive(Parser)]
pub struct Options {
    #[arg(long, default_value = ".")]
    pub root: PathBuf,
    #[arg(long)]
    pub check: bool,
    #[arg(long)]
    pub selftest: bool,
}
#[derive(Debug)]
pub struct Debt {
    pub reason: String,
    pub moved: Vec<String>,
    pub heal: Vec<String>,
}
pub fn owed(ctx: &ContextData) -> Result<Debt> {
    if !ctx.root.join(POINTERS).is_file() {
        return Ok(Debt {
            reason: "there is no pointer file yet".into(),
            moved: vec![],
            heal: vec![],
        });
    }
    let held = ctx.held()?;
    let hashes = ctx.hashes(&ctx.solids()?)?;
    let sidecars = ctx.sidecars(&held)?;
    let moved = strings(&ctx.op(
        "bytes-drifted",
        json!({"held":held,"hashes":hashes,"sidecar_hashes":sidecars}),
    )?);
    if !moved.is_empty() {
        return Ok(Debt {
            reason: format!("{} member(s) have completed bytes to publish", moved.len()),
            moved,
            heal: vec![],
        });
    }
    let index = ctx.index()?;
    let lines = merge_maps(&[&held["solids"], &held["sidecars"]]);
    let tree = ctx.tree(&lines, &index)?;
    let inputs = ctx.op("made-moves", json!({"held":held["made"],"tree":tree}))?;
    let catalog_moved = ctx.op("catalog-moved", json!({"held":held}))?;
    let state=ctx.op("owed",json!({"held":held,"index":index,"pointers":POINTERS,"moved":moved,"inputs":inputs,"catalog_moved":catalog_moved}))?;
    Ok(Debt {
        reason: state[0].as_str().unwrap_or("").into(),
        moved: strings(&state[1]),
        heal: strings(&state[3]),
    })
}
fn publish_once(ctx: &ContextData, t: &impl Transport) -> Result<()> {
    let current = ctx.reload()?;
    let ctx = &current;
    let started = Instant::now();
    let mut published = pack::Published::default();
    let phase = Instant::now();
    let debt = owed(ctx)?;
    timing("identify", phase, json!({"moved":debt.moved}))?;
    if debt.reason.is_empty() && debt.heal.is_empty() {
        println!("  nothing owed ({:.2}s)", started.elapsed().as_secs_f64());
        return Ok(());
    }
    if !debt.reason.is_empty() {
        let viewer_only = debt.moved.iter().any(|p| is_viewer(p));
        let phase = Instant::now();
        let grafted = match pack::refresh_sources(ctx, &debt.moved) {
            Ok(refreshed) => {
                for error in refreshed.errors {
                    eprintln!(
                        "  scene refresh stopped short: {error}; completed references still publish"
                    );
                }
                refreshed.grafted
            }
            Err(error) => {
                eprintln!(
                    "  scene refresh stopped short: {error}; publishing completed bytes held here"
                );
                vec![]
            }
        };
        timing("references", phase, empty())?;
        let phase = Instant::now();
        let members = debt
            .moved
            .iter()
            .chain(&grafted)
            .cloned()
            .collect::<std::collections::BTreeSet<_>>();
        println!("  {}; publishing completed members", debt.reason);
        published = pack::publish_held(
            ctx,
            t,
            &grafted,
            viewer_only,
            (!members.is_empty()).then_some(&members),
        )?;
        if viewer_only && debt.moved.iter().any(|p| !is_viewer(p)) {
            fs::write(ctx.root.join(".cache/publish-now.again"), b"")?;
        }
        timing("objects", phase, empty())?;
    }
    let phase = Instant::now();
    let held = ctx.held()?;
    let index = ctx.index()?;
    let old = ctx.git(&["show", &format!("HEAD:{POINTERS}")])?;
    let before = serde_json::from_slice::<Value>(&old.stdout).unwrap_or_else(|_| empty());
    let plan=ctx.op("commit-plan",json!({"held":held,"index":index,"pointers":POINTERS,"before":before,"served":["release","bundle","solids","sidecars","website","mesh_assets"]}))?;
    let files = snapshot_files(ctx, &held, &published)?;
    let work = crate::Work::new(&ctx.root)?;
    let snapshot = work.path.join("commit.json");
    fs::write(
        &snapshot,
        serde_json::to_vec(&json!({"message":plan["message"],"files":files}))?,
    )?;
    let landing = std::env::var("HSM_LAND").unwrap_or_else(|_| "hsm-land".into());
    let committed = ctx.command(
        &landing,
        &[
            "--root".into(),
            ctx.root.to_string_lossy().into_owned(),
            "--commit-snapshot".into(),
            snapshot.to_string_lossy().into_owned(),
        ],
    )?;
    ensure!(
        committed.status.success(),
        "frozen pointer commit failed: {}",
        String::from_utf8_lossy(&committed.stderr)
    );
    let result: Value = serde_json::from_slice(&committed.stdout).context("frozen commit reply")?;
    if result["changed"] == true {
        let hook = ctx.post_commit()?;
        ensure!(
            hook.status.success(),
            "post-commit landing failed: {}",
            String::from_utf8_lossy(&hook.stderr)
        );
    }
    let landed = ctx.git(&["merge-base", "--is-ancestor", "HEAD", "origin/main"])?;
    ensure!(
        landed.status.success(),
        "pointer file is committed but has not landed on main; the next push carries it"
    );
    timing("commit-and-push", phase, empty())?;
    let phase = Instant::now();
    if plan["served"] == true {
        if let Err(error) = t.refresh() {
            eprintln!("  advisory site refresh failed ({error}); the site also polls");
        } else {
            println!("  the site is looking");
        }
    }
    timing("notify", phase, empty())?;
    timing("publication", started, empty())?;
    Ok(())
}

/// Pointer commits use the exact referenced sidecar blobs while later work stays on disk.
pub fn snapshot_files(
    ctx: &ContextData,
    held: &Value,
    published: &pack::Published,
) -> Result<Vec<Value>> {
    let pointer = fs::read(ctx.root.join(POINTERS))?;
    ensure!(
        serde_json::from_slice::<Value>(&pointer)? == *held,
        "pointer bytes changed before their frozen commit"
    );
    let mut files = vec![json!({"path":POINTERS,"blob":ctx.blob(&pointer)?})];
    let index = ctx.index()?;
    let rels = keys(&held["sidecars"]);
    let ids = rels
        .iter()
        .filter(|rel| !published.sidecars.contains_key(*rel))
        .filter_map(|rel| index[rel].as_str().map(str::to_owned))
        .collect::<std::collections::BTreeSet<_>>();
    let blobs = ctx.blobs(&ids)?;
    for rel in rels {
        let expected = held["sidecars"][&rel]
            .as_str()
            .context("referenced sidecar digest")?;
        let blob = if let Some(frozen) = published.sidecars.get(&rel) {
            ensure!(
                frozen.digest == expected,
                "frozen sidecar identity changed: {rel}"
            );
            frozen.blob.clone()
        } else if let Some((id, _)) = index[&rel]
            .as_str()
            .and_then(|id| blobs.get(id).map(|bytes| (id, bytes)))
            .filter(|(_, bytes)| hsm_geometry::scene::digest(bytes) == expected)
        {
            id.to_owned()
        } else if let Some(bytes) = fs::read(ctx.root.join(&rel))
            .ok()
            .filter(|bytes| hsm_geometry::scene::digest(bytes) == expected)
        {
            ctx.blob(&bytes)?
        } else {
            let old = ctx.git(&["show", &format!("HEAD:{rel}")])?;
            if !ctx.root.join(&rel).is_file() && !old.status.success() {
                continue;
            }
            ensure!(
                old.status.success() && hsm_geometry::scene::digest(&old.stdout) == expected,
                "referenced sidecar bytes are unavailable: {rel}"
            );
            ctx.blob(&old.stdout)?
        };
        files.push(json!({"path":rel,"blob":blob}));
    }
    Ok(files)
}

struct Owner {
    lock: PathBuf,
    pid: String,
    active: bool,
}
impl Owner {
    fn release(&mut self) {
        if self.active && fs::read_to_string(&self.lock).is_ok_and(|v| v == self.pid) {
            let _ = fs::remove_file(&self.lock);
        }
        self.active = false;
    }
}
impl Drop for Owner {
    fn drop(&mut self) {
        self.release();
    }
}
fn acquire(ctx: &ContextData) -> Result<Option<Owner>> {
    let lock = ctx.root.join(".cache/publish-now.lock");
    let again = ctx.root.join(".cache/publish-now.again");
    fs::create_dir_all(lock.parent().unwrap())?;
    loop {
        match OpenOptions::new().write(true).create_new(true).open(&lock) {
            Ok(mut file) => {
                let pid = std::process::id().to_string();
                file.write_all(pid.as_bytes())?;
                return Ok(Some(Owner {
                    lock,
                    pid,
                    active: true,
                }));
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => {
                let marker = fs::read_to_string(&lock).unwrap_or_default();
                if let Ok(pid) = marker.trim().parse::<i32>() {
                    if unsafe { libc::kill(pid, 0) } < 0
                        && std::io::Error::last_os_error().raw_os_error() == Some(libc::ESRCH)
                    {
                        let _ = fs::remove_file(&lock);
                        continue;
                    }
                } else if lock
                    .metadata()
                    .and_then(|m| m.modified())
                    .ok()
                    .and_then(|m| m.elapsed().ok())
                    .is_some_and(|age| age.as_secs() > 5)
                {
                    let _ = fs::remove_file(&lock);
                    continue;
                }
                fs::write(&again, b"")?;
                if !lock.exists() {
                    continue;
                }
                return Ok(None);
            }
            Err(error) => return Err(error.into()),
        }
    }
}
pub fn run(ctx: &ContextData, t: &impl Transport, check: bool) -> Result<i32> {
    if check {
        let debt = owed(ctx)?;
        println!(
            "  --check: {}",
            if debt.reason.is_empty() {
                "nothing owed"
            } else {
                &debt.reason
            }
        );
        if !debt.heal.is_empty() {
            println!("  index differs: {}", debt.heal.join(", "));
        }
        return Ok(0);
    }
    let Some(mut owner) = acquire(ctx)? else {
        println!("  publication is already running; the completed files are queued");
        return Ok(0);
    };
    let again = ctx.root.join(".cache/publish-now.again");
    loop {
        let status = match publish_once(ctx, t) {
            Ok(()) => 0,
            Err(error) => {
                eprintln!("hsm-publish: {error:#}");
                1
            }
        };
        if fs::remove_file(&again).is_ok() {
            continue;
        }
        // Followers recheck after queuing, so a request racing release starts the next owner.
        owner.release();
        if !again.exists() {
            return Ok(status);
        }
        let Some(next) = acquire(ctx)? else {
            return Ok(status);
        };
        owner = next;
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn coalesced_and_stale_requests_keep_one_owner() -> Result<()> {
        let parent = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .ancestors()
            .nth(3)
            .unwrap();
        let work = crate::Work::new(parent)?;
        let ctx = ContextData::with_config(&work.path, empty(), empty())?;
        let mut first = acquire(&ctx)?.context("first publication owner")?;
        ensure!(
            acquire(&ctx)?.is_none(),
            "a second publisher became an owner"
        );
        ensure!(
            ctx.root.join(".cache/publish-now.again").is_file(),
            "a coalesced request was lost"
        );
        first.release();
        let next = acquire(&ctx)?.context("next publication owner")?;
        drop(first);
        ensure!(
            next.lock.is_file(),
            "dropping the released owner removed the next marker"
        );
        drop(next);
        let path = ctx.root.join(".cache/publish-now.lock");
        fs::write(&path, i32::MAX.to_string())?;
        ensure!(
            acquire(&ctx)?.is_some(),
            "a dead process marker kept publication locked"
        );
        fs::write(&path, b"")?;
        fs::File::options()
            .write(true)
            .open(&path)?
            .set_modified(std::time::UNIX_EPOCH)?;
        ensure!(
            acquire(&ctx)?.is_some(),
            "an abandoned partial marker kept publication locked"
        );
        Ok(())
    }
}
