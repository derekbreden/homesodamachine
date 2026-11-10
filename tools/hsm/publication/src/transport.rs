//! Content-addressed objects use the public store and GitHub release fallback.
use crate::{ContextData, Work, now, parallel, strings};
use anyhow::{Context, Result, ensure};
use serde_json::{Value, json};
use std::{collections::BTreeSet, fs, path::Path, process::Output};

pub trait Transport: Sync {
    fn head(&self, url: &str) -> bool;
    fn put(&self, url: &str, file: &Path) -> bool;
    fn download(&self, url: &str, file: &Path) -> Result<()>;
    fn github(&self, args: &[String]) -> Result<Output>;
    fn refresh(&self) -> Result<()>;
}
pub struct Live<'a> {
    pub context: &'a ContextData,
}
impl Transport for Live<'_> {
    fn head(&self, url: &str) -> bool {
        self.context
            .command(
                "curl",
                &[
                    "--silent",
                    "--show-error",
                    "--fail",
                    "--location",
                    "--max-time",
                    "30",
                    "--head",
                    "--output",
                    "/dev/null",
                    url,
                ]
                .map(str::to_owned),
            )
            .is_ok_and(|o| o.status.success())
    }
    fn put(&self, url: &str, file: &Path) -> bool {
        self.context
            .command(
                "curl",
                &[
                    "--silent",
                    "--show-error",
                    "--fail",
                    "--location",
                    "--max-time",
                    "300",
                    "--request",
                    "PUT",
                    "--header",
                    "Content-Type: application/gzip",
                    "--upload-file",
                    &file.to_string_lossy(),
                    "--output",
                    "/dev/null",
                    url,
                ]
                .map(str::to_owned),
            )
            .is_ok_and(|o| o.status.success())
    }
    fn download(&self, url: &str, file: &Path) -> Result<()> {
        let out = self.context.command(
            "curl",
            &[
                "--silent",
                "--show-error",
                "--fail",
                "--location",
                "--max-time",
                "120",
                "--output",
                &file.to_string_lossy(),
                url,
            ]
            .map(str::to_owned),
        )?;
        ensure!(
            out.status.success(),
            "object download failed: {}",
            String::from_utf8_lossy(&out.stderr)
        );
        Ok(())
    }
    fn github(&self, args: &[String]) -> Result<Output> {
        self.context.command("gh", args)
    }
    fn refresh(&self) -> Result<()> {
        let result = self.context.command(
            "curl",
            &[
                "--silent",
                "--show-error",
                "--fail",
                "--max-time",
                "10",
                "--request",
                "POST",
                "--data",
                "",
                "--output",
                "/dev/null",
                "https://homesodamachine.com/api/artifacts/refresh",
            ]
            .map(str::to_owned),
        )?;
        ensure!(result.status.success(), "site refresh request failed");
        Ok(())
    }
}
pub fn github(t: &impl Transport, args: &[&str]) -> Result<Output> {
    t.github(&args.iter().map(|s| (*s).into()).collect::<Vec<_>>())
}
pub fn release_assets(ctx: &ContextData, t: &impl Transport) -> Result<Value> {
    let out = github(t, &["release", "view", ctx.tag(), "--json", "assets"])?;
    if !out.status.success() {
        return Ok(json!([]));
    }
    Ok(serde_json::from_slice::<Value>(&out.stdout)?["assets"].clone())
}
pub fn objects_in_store(
    ctx: &ContextData,
    t: &impl Transport,
    hashes: impl IntoIterator<Item = String>,
) -> BTreeSet<String> {
    let hashes = hashes
        .into_iter()
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect::<Vec<_>>();
    parallel(&hashes, |sha| {
        t.head(&format!("{}{}", ctx.store_url(), ctx.asset(sha)))
            .then(|| sha.clone())
    })
    .into_iter()
    .flatten()
    .collect()
}
pub fn history(ctx: &ContextData) -> Result<Vec<Value>> {
    ensure!(
        ctx.git_text(&["rev-parse", "--is-shallow-repository"])? != "true",
        "release retirement requires complete Git history"
    );
    let revisions = ctx.git_text(&["rev-list", "HEAD", "--", crate::POINTERS])?;
    let mut rows = Vec::new();
    for rev in revisions.split_whitespace() {
        let got = ctx.git(&["show", &format!("{rev}:{}", crate::POINTERS)])?;
        if got.status.success() {
            if let Ok(held) = serde_json::from_slice::<Value>(&got.stdout) {
                rows.push(ctx.op("pointer-assets", json!({"held":held,"prefix":ctx.prefix()}))?);
            }
        }
    }
    Ok(rows)
}
pub fn room(ctx: &ContextData, t: &impl Transport, keep: usize) -> Result<Value> {
    let assets = release_assets(ctx, t)?;
    let held = assets.as_array().map_or(0, Vec::len);
    let plan=ctx.op("retirable",json!({"assets":assets,"history":history(ctx)?,"disk":ctx.op("pointer-assets",json!({"held":ctx.held()?,"prefix":ctx.prefix()}))?,"keep_cuts":keep,"now":now(),"floor":ctx.policy["RETIRE_FLOOR_S"]}))?;
    ctx.op("release-room",json!({"held":held,"capacity":ctx.policy["RELEASE_ASSET_CAP"],"unreachable":plan[0],"superseded":plan[1]}))
}
pub fn retire(
    ctx: &ContextData,
    t: &impl Transport,
    keep: usize,
    unreachable_only: bool,
) -> Result<i32> {
    let state = room(ctx, t, keep)?;
    let going = strings(&ctx.op(
        "retire-plan",
        json!({"state":state,"unreachable_only":unreachable_only}),
    )?);
    let failed = parallel(&going, |name| {
        github(t, &["release", "delete-asset", ctx.tag(), name, "--yes"])
            .is_ok_and(|o| o.status.success())
    });
    let bad = failed.iter().filter(|ok| !**ok).count();
    println!(
        "{} release asset(s) retired; {bad} failed",
        going.len() - bad
    );
    Ok(i32::from(bad > 0))
}
pub fn make_room(ctx: &ContextData, t: &impl Transport, need: usize) -> Result<bool> {
    let assets = release_assets(ctx, t)?;
    let held = assets.as_array().map_or(0, Vec::len);
    let cap = ctx.policy["RELEASE_ASSET_CAP"].as_u64().unwrap_or(1000) as usize;
    if cap.saturating_sub(held) >= need {
        return Ok(false);
    }
    if ctx.git_text(&["rev-parse", "--is-shallow-repository"])? == "true" {
        println!("  shallow history; no release assets are retired");
        return Ok(false);
    }
    retire(
        ctx,
        t,
        ctx.policy["CUTS_KEPT"].as_u64().unwrap_or(12) as usize,
        false,
    )?;
    Ok(true)
}
pub fn upload_bundle(
    ctx: &ContextData,
    t: &impl Transport,
    file: &Path,
    asset: &str,
    sha: &str,
    size: u64,
) -> Result<()> {
    let release = github(t, &["release", "view", ctx.tag(), "--json", "assets"])?;
    let exists = release.status.success();
    let assets = if exists {
        serde_json::from_slice::<Value>(&release.stdout)?["assets"].clone()
    } else {
        json!([])
    };
    let state = ctx.op(
        "release-state",
        json!({"assets":assets,"asset":asset,"digest":sha,"size":size}),
    )?;
    if state["matches"] == true {
        return Ok(());
    }
    if !exists {
        let made = github(
            t,
            &[
                "release",
                "create",
                ctx.tag(),
                "--title",
                "CAD artifacts",
                "--notes",
                "Content-addressed machine geometry and printable parts.",
            ],
        )?;
        ensure!(
            made.status.success(),
            "release creation failed: {}",
            String::from_utf8_lossy(&made.stderr)
        );
    }
    let work = Work::new(&ctx.root)?;
    let staged = work.path.join(asset);
    fs::copy(file, &staged)?;
    let out = github(
        t,
        &[
            "release",
            "upload",
            ctx.tag(),
            &staged.to_string_lossy(),
            "--clobber",
        ],
    )?;
    ensure!(
        out.status.success(),
        "bundle upload failed: {}",
        String::from_utf8_lossy(&out.stderr)
    );
    Ok(())
}
pub fn upload_objects(
    ctx: &ContextData,
    t: &impl Transport,
    rels: &[String],
    hashes: &Value,
    known: &BTreeSet<String>,
    sources: &std::collections::BTreeMap<String, std::path::PathBuf>,
) -> Result<bool> {
    let todo = strings(&ctx.op(
        "objects-to-send",
        json!({"rels":rels,"hashes":hashes,"known":known}),
    )?);
    let work = Work::new(&ctx.root)?;
    let mut sources = sources.clone();
    let unfrozen = todo
        .iter()
        .filter(|rel| !sources.contains_key(*rel))
        .collect::<Vec<_>>();
    let stable=ctx.op("freeze",json!({"directory":work.path,"files":unfrozen.iter().map(|rel|json!({"relative":rel,"source":ctx.root.join(rel)})).collect::<Vec<_>>()}))?;
    for row in stable.as_array().context("frozen object uploads")? {
        let rel = row["relative"].as_str().context("relative object upload")?;
        ensure!(
            row["sha256"] == hashes[rel],
            "member changed before object upload: {rel}"
        );
        sources.insert(
            rel.into(),
            row["source"]
                .as_str()
                .context("frozen object source")?
                .into(),
        );
    }
    let cache = ctx.root.join(".cache/meshes/publication");
    fs::create_dir_all(&cache)?;
    ctx.op("gzip-many",json!({"files":todo.iter().map(|rel|json!({"source":sources.get(rel).cloned().unwrap_or_else(||ctx.root.join(rel)),"output":cache.join(ctx.asset(hashes[rel].as_str().unwrap()))})).collect::<Vec<_>>(),"level":1}))?;
    let fallback = std::sync::Mutex::new(false);
    let outcomes = parallel(&todo, |rel| -> Result<bool> {
        let sha = hashes[rel].as_str().context("member digest")?;
        let file = cache.join(ctx.asset(sha));
        if t.put(&format!("{}{}", ctx.store_url(), ctx.asset(sha)), &file) {
            return Ok(true);
        }
        {
            let mut ready = fallback.lock().unwrap();
            if !*ready {
                make_room(ctx, t, todo.len())?;
                *ready = true;
            }
        }
        Ok(github(
            t,
            &[
                "release",
                "upload",
                ctx.tag(),
                &file.to_string_lossy(),
                "--clobber",
            ],
        )?
        .status
        .success())
    });
    let complete = outcomes.into_iter().collect::<Result<Vec<_>>>()?;
    let good = complete.iter().filter(|ok| **ok).count();
    println!("  {good} of {} changed object(s) uploaded", todo.len());
    Ok(good == todo.len())
}
