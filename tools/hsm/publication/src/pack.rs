//! Frozen changed members and shared objects advance pointers without waiting for unrelated producers.
use crate::transport::{self, Transport};
use crate::{
    ContextData, VIEWER_HOSTS, Work, empty, is_viewer, keys, merge_maps, now, replaced_export,
    strings, timing,
};
use anyhow::{Context, Result, ensure};
use clap::Parser;
use hsm_build_data::publication::archive;
use hsm_geometry::scene;
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::PathBuf,
    time::Instant,
};

#[derive(Parser, Default)]
pub struct Options {
    #[arg(value_parser=["selftest"])]
    pub mode: Option<String>,
    #[arg(long, default_value = ".")]
    pub root: PathBuf,
    #[arg(long)]
    pub write: bool,
    #[arg(long)]
    pub publish_held: bool,
    #[arg(long)]
    pub viewer_only: bool,
    #[arg(long)]
    pub members_json: Option<String>,
    #[arg(long)]
    pub grafted: Vec<String>,
    #[arg(long)]
    pub check: bool,
    #[arg(long)]
    pub prune: bool,
    #[arg(long)]
    pub allow_retired: bool,
    #[arg(long)]
    pub room: bool,
    #[arg(long)]
    pub retire: bool,
    #[arg(long, default_value_t = 12)]
    pub keep_cuts: usize,
    #[arg(long)]
    pub sidecar_debt: bool,
    #[arg(long)]
    pub selftest: bool,
}

#[derive(Clone, Debug)]
pub struct FrozenSidecar {
    pub digest: String,
    pub blob: String,
}
#[derive(Default)]
pub struct Published {
    pub sidecars: BTreeMap<String, FrozenSidecar>,
}

pub struct Refreshed {
    pub grafted: Vec<String>,
    pub errors: Vec<String>,
}
/// A completed producer replaces geometry through the assembly's retained import frames.
pub fn refresh_sources(ctx: &ContextData, changed: &[String]) -> Result<Refreshed> {
    let hosts = ctx
        .solids()?
        .into_iter()
        .filter(|p| is_viewer(p))
        .collect::<Vec<_>>();
    let mut grafted = BTreeSet::new();
    let mut errors = Vec::new();
    for relative in changed
        .iter()
        .filter(|p| p.ends_with(".step.mesh") && !VIEWER_HOSTS.contains(&p.as_str()))
    {
        let bytes = match fs::read(ctx.root.join(relative)) {
            Ok(bytes) => bytes,
            Err(error) => {
                errors.push(format!("{relative}: {error}"));
                continue;
            }
        };
        for host in &hosts {
            if host == relative {
                continue;
            }
            let file = ctx.root.join(host);
            let Ok(header) = hsm_build_data::payload::header(&file) else {
                continue;
            };
            if header["v"] != 4 && !VIEWER_HOSTS.contains(&host.as_str()) {
                continue;
            }
            let refreshed = (|| -> Result<usize> {
                let mut head = scene::pack(&fs::read(&file)?)?;
                let replaced = if host.ends_with(".glb.mesh") {
                    scene::replace_selected(&mut head, relative, &bytes)?
                } else {
                    scene::replace(&mut head, relative, &bytes)?
                };
                if replaced > 0 {
                    scene::keep(&file, &scene::encode(&head, &[])?)?;
                }
                Ok(replaced)
            })();
            match refreshed {
                Ok(replaced) if replaced > 0 => {
                    grafted.insert(host.clone());
                    println!("  {host}: {replaced} part reference(s) updated");
                }
                Ok(_) => {}
                Err(error) => errors.push(format!("{host} from {relative}: {error:#}")),
            }
        }
    }
    Ok(Refreshed {
        grafted: grafted.into_iter().collect(),
        errors,
    })
}
fn obsolete(ctx: &ContextData, held: &Value) -> Vec<String> {
    keys(&held["solids"])
        .into_iter()
        .filter(|p| {
            (p.ends_with(".step") || p.ends_with(".glb"))
                && hsm_build_data::payload::header(ctx.root.join(format!("{p}.mesh")))
                    .is_ok_and(|head| replaced_export(p, &head))
        })
        .collect()
}

fn upload_mesh_assets(
    ctx: &ContextData,
    t: &impl Transport,
    rels: &[String],
    held: &Value,
    sources: &BTreeMap<String, PathBuf>,
    lines: &Value,
    keep: bool,
) -> Result<Vec<String>> {
    let mut assets = BTreeSet::new();
    for rel in rels.iter().filter(|p| is_viewer(p)) {
        let file = sources
            .get(rel)
            .cloned()
            .unwrap_or_else(|| ctx.root.join(rel));
        let Ok(mut head) = hsm_build_data::payload::header(&file) else {
            continue;
        };
        if head["v"] != 4 {
            continue;
        }
        if let Some(expected) = lines[rel].as_str() {
            if scene::digest(&fs::read(&file)?) != expected {
                head = scene::header(&fs::read(
                    ctx.root
                        .join(format!(".cache/meshes/scene-assets/{expected}.mesh")),
                )?)?
                .0;
            }
        }
        assets.extend(scene::assets(&head));
    }
    let known = strings(&held["mesh_assets"])
        .into_iter()
        .collect::<BTreeSet<_>>();
    let candidates = assets.difference(&known).cloned().collect::<Vec<_>>();
    let present = transport::objects_in_store(ctx, t, candidates.clone());
    let todo = candidates
        .into_iter()
        .filter(|sha| !present.contains(sha))
        .collect::<Vec<_>>();
    let cache = ctx.root.join(".cache/meshes/publication");
    fs::create_dir_all(&cache)?;
    ctx.op("gzip-many",json!({"files":todo.iter().map(|sha|json!({"source":ctx.root.join(format!(".cache/meshes/scene-assets/{sha}.mesh")),"output":cache.join(ctx.asset(sha))})).collect::<Vec<_>>(),"level":1}))?;
    let results = crate::parallel(&todo, |sha| {
        t.put(
            &format!("{}{}", ctx.store_url(), ctx.asset(sha)),
            &cache.join(ctx.asset(sha)),
        )
    });
    ensure!(
        results.iter().all(|ok| *ok),
        "a shared mesh object did not upload; manifests retain their current pointers"
    );
    if !todo.is_empty() {
        println!("  {} shared mesh object(s) uploaded", todo.len());
    }
    if keep {
        assets.extend(known);
    }
    Ok(assets.into_iter().collect())
}
fn adopt(
    ctx: &ContextData,
    t: &impl Transport,
    held: &Value,
    rels: &[String],
    work: &Work,
) -> Result<Vec<String>> {
    let mut taken = Vec::new();
    for (index, rel) in rels.iter().enumerate() {
        let sha = held["solids"][rel].as_str().context("old member digest")?;
        let url = ctx.op("object-url", json!({"held":held,"digest":sha}))?;
        let Some(url) = url.as_str() else {
            continue;
        };
        let file = work.path.join(format!("adopt-{index}.gz"));
        let result = (|| -> Result<()> {
            t.download(url, &file)?;
            let bytes = archive::decompress(&fs::read(&file)?)?;
            ensure!(
                archive::adopt(&ctx.root, rel, sha, &bytes)?,
                "object bytes differ from pointer"
            );
            Ok(())
        })();
        match result {
            Ok(()) => taken.push(rel.clone()),
            Err(error) => {
                eprintln!("  {rel}: main's bytes did not arrive ({error}); local bytes remain")
            }
        }
    }
    Ok(taken)
}
pub fn publish_held(
    ctx: &ContextData,
    t: &impl Transport,
    grafted: &[String],
    viewer_only: bool,
    members: Option<&BTreeSet<String>>,
) -> Result<Published> {
    let captured = now();
    let started = Instant::now();
    let work = Work::new(&ctx.root)?;
    let mut held = ctx.held()?;
    let retired = obsolete(ctx, &held);
    for rel in &retired {
        for kind in ["solids", "made"] {
            if let Some(map) = held[kind].as_object_mut() {
                map.remove(rel);
            }
        }
    }
    let mut rels = ctx.solids()?;
    rels.retain(|rel| {
        members.is_none_or(|set| set.contains(rel)) && (!viewer_only || is_viewer(rel))
    });
    let mut hashes = ctx.hashes(&rels)?;
    let mut sidecars = if viewer_only {
        held["sidecars"]
            .as_object()
            .cloned()
            .map(Value::Object)
            .unwrap_or_else(empty)
    } else {
        ctx.sidecars(&held)?
    };
    let mut published = Published::default();
    if !viewer_only {
        let changed = keys(&sidecars)
            .into_iter()
            .filter(|rel| held["sidecars"][rel] != sidecars[rel] && ctx.root.join(rel).is_file())
            .collect::<Vec<_>>();
        let stable=ctx.op("freeze",json!({"directory":work.path.join("sidecars"),"files":changed.iter().map(|rel|json!({"relative":rel,"source":ctx.root.join(rel)})).collect::<Vec<_>>()}))?;
        for row in stable.as_array().context("frozen sidecars")? {
            let rel = row["relative"].as_str().context("frozen sidecar path")?;
            let digest = row["sha256"]
                .as_str()
                .context("frozen sidecar digest")?
                .to_owned();
            let bytes = fs::read(row["source"].as_str().context("frozen sidecar bytes")?)?;
            let blob = ctx.blob(&bytes)?;
            sidecars[rel] = json!(digest);
            published
                .sidecars
                .insert(rel.into(), FrozenSidecar { digest, blob });
        }
    }
    let mtimes = ctx.op("mtimes", json!({"rels":rels}))?;
    let initial = ctx.op(
        "held-state",
        json!({"held":held,"rels":rels,"now":hashes,"sidecar_now":sidecars,"mtimes":mtimes}),
    )?;
    for rel in adopt(ctx, t, &held, &strings(&initial["stale"]), &work)? {
        hashes[&rel] = held["solids"][&rel].clone();
    }
    let state = ctx.op(
        "held-state",
        json!({"held":held,"rels":rels,"now":hashes,"sidecar_now":sidecars,"mtimes":mtimes}),
    )?;
    let pinned = strings(&state["pinned"]);
    let moved = strings(&state["moved"]);
    let mut lines = state["lines"].clone();
    let mut walked = merge_maps(&[&hashes, &sidecars]);
    let stable=ctx.op("freeze",json!({"directory":work.path,"files":pinned.iter().map(|rel|json!({"relative":rel,"source":ctx.root.join(rel)})).collect::<Vec<_>>()}))?;
    let mut sources = BTreeMap::new();
    for row in stable.as_array().context("frozen members")? {
        let rel = row["relative"].as_str().context("relative frozen member")?;
        hashes[rel] = row["sha256"].clone();
        lines[rel] = row["sha256"].clone();
        walked[rel] = row["sha256"].clone();
        sources.insert(
            rel.into(),
            PathBuf::from(row["source"].as_str().context("frozen source")?),
        );
    }
    let whole = merge_maps(&[&lines, &sidecars]);
    let mut made = if viewer_only {
        let mut made = held["made"]
            .as_object()
            .cloned()
            .map(Value::Object)
            .unwrap_or_else(empty);
        let head = ctx.git_text(&["rev-parse", "HEAD"])?;
        for rel in &moved {
            if !made[rel].is_object() {
                made[rel] = empty();
            }
            made[rel]["commit"] = json!(head);
            made[rel]["unproven"] = json!(true);
        }
        made
    } else {
        ctx.made(&held, &whole, &walked, &moved, grafted)?
    };
    if !viewer_only {
        for row in stable.as_array().context("frozen member identities")? {
            let rel = row["relative"]
                .as_str()
                .context("relative frozen identity")?;
            let live = hsm_build_data::artifact_cache::identity(&ctx.root.join(rel))
                .ok()
                .map(|identity| json!(identity));
            if row["source_stable"] != true || live.as_ref() != Some(&row["source_identity"]) {
                if !made[rel].is_object() {
                    made[rel] = empty();
                }
                made[rel].as_object_mut().unwrap().remove("inputs");
                made[rel]["unproven"] = json!(true);
            }
        }
    }
    if pinned.is_empty() {
        let records=ctx.op("held-record-state",json!({"held":held,"made":made,"side_moved":state["side_moved"],"website":ctx.website(&held)?}))?;
        if records["unchanged"] == true && retired.is_empty() {
            return Ok(published);
        }
        held["sidecars"] = sidecars;
        held["made"] = made;
        ctx.write(&held)?;
        return Ok(published);
    }
    timing("pack.plan", started, json!({"members":pinned}))?;
    let phase = Instant::now();
    let asset_members = if viewer_only {
        pinned.clone()
    } else {
        keys(&lines)
            .into_iter()
            .filter(|p| ctx.root.join(p).is_file())
            .collect()
    };
    let incomplete = keys(&lines)
        .iter()
        .any(|path| is_viewer(path) && !ctx.root.join(path).is_file());
    let mesh_assets = upload_mesh_assets(
        ctx,
        t,
        &asset_members,
        &held,
        &sources,
        &lines,
        viewer_only || members.is_some() || incomplete,
    )?;
    timing("pack.mesh-objects", phase, empty())?;
    if let Some(digest) = held["bundle"]["sha256"].as_str() {
        let phase = Instant::now();
        let known = transport::objects_in_store(
            ctx,
            t,
            pinned
                .iter()
                .filter_map(|p| hashes[p].as_str().map(str::to_owned)),
        );
        timing("pack.member-heads", phase, empty())?;
        let phase = Instant::now();
        if transport::upload_objects(ctx, t, &pinned, &hashes, &known, &sources)? {
            timing("pack.members", phase, empty())?;
            let mut data = ctx.pointers(
                &held,
                &lines,
                &sidecars,
                &made,
                digest,
                held["bundle"]["bytes"].as_u64().unwrap_or(0),
                captured,
            )?;
            data["mesh_assets"] = json!(mesh_assets);
            data["bundle"] = held["bundle"].clone();
            data["bundle"]["behind"] = json!(true);
            data["release"]["objects"] = json!(ctx.prefix());
            ctx.write(&data)?;
            println!("  {} completed member(s) published by hash", pinned.len());
            return Ok(published);
        }
        ensure!(
            !viewer_only && members.is_none(),
            "completed members did not upload; pointer file is unchanged"
        );
    }
    cut_bundle(
        ctx,
        t,
        &held,
        &keys(&lines),
        &lines,
        &sidecars,
        &made,
        &mesh_assets,
        captured,
        false,
        &sources,
    )?;
    Ok(published)
}
fn cut_bundle(
    ctx: &ContextData,
    t: &impl Transport,
    held: &Value,
    rels: &[String],
    hashes: &Value,
    sidecars: &Value,
    made: &Value,
    mesh_assets: &[String],
    captured: f64,
    preserve_objects: bool,
    sources: &BTreeMap<String, PathBuf>,
) -> Result<()> {
    let work = Work::new(&ctx.root)?;
    let bundle = work.path.join("bundle.tar.gz");
    let expected = serde_json::from_value(hashes.clone())?;
    let digest = archive::bundle_sources(&ctx.root, rels, &bundle, sources, &expected)?;
    let size = bundle.metadata()?.len();
    let mut data = ctx.pointers(held, hashes, sidecars, made, &digest, size, captured)?;
    let asset = data["release"]["asset"]
        .as_str()
        .context("bundle asset")?
        .to_owned();
    transport::make_room(ctx, t, rels.len() + 1)?;
    transport::upload_bundle(ctx, t, &bundle, &asset, &digest, size)?;
    let known = transport::objects_in_store(
        ctx,
        t,
        hashes
            .as_object()
            .into_iter()
            .flatten()
            .filter_map(|(_, sha)| sha.as_str().map(str::to_owned)),
    );
    if preserve_objects && held["release"]["objects"].is_string()
        || transport::upload_objects(ctx, t, rels, hashes, &known, sources)?
    {
        data["release"]["objects"] = json!(ctx.prefix());
    }
    data["mesh_assets"] = json!(mesh_assets);
    ctx.write(&data)?;
    println!("  bundle {asset} published");
    Ok(())
}

fn retirement_evidence(ctx: &ContextData, retired: &[String]) -> Result<Vec<String>> {
    let groups = ctx.op(
        "retirement-groups",
        json!({"held":ctx.held()?,"retired":retired}),
    )?;
    let mut records = Vec::new();
    for commit in keys(&groups).into_iter().filter(|c| !c.is_empty()) {
        let graph = ctx.git(&["show", &format!("{commit}:tools/bazel/graph.json")])?;
        let changed = ctx.git(&["diff", "--name-only", &commit, "HEAD"])?;
        records.push(json!({"rels":groups[&commit],"graph":String::from_utf8_lossy(&graph.stdout),"graph_ok":graph.status.success(),"diff_ok":changed.status.success(),"changed":String::from_utf8_lossy(&changed.stdout).lines().collect::<Vec<_>>()}));
    }
    Ok(strings(&ctx.op(
        "retirement-evidence",
        json!({"records":records,"unrecorded":groups[""]}),
    )?))
}
pub fn run(ctx: &ContextData, t: &impl Transport, args: &Options) -> Result<i32> {
    ensure!(
        !args.publish_held || args.write,
        "--publish-held requires --write"
    );
    ensure!(
        args.grafted.is_empty() || args.publish_held,
        "--grafted requires --publish-held"
    );
    ensure!(
        !args.viewer_only || args.publish_held,
        "--viewer-only requires --publish-held"
    );
    ensure!(
        args.members_json.is_none() || args.publish_held,
        "--members-json requires --publish-held"
    );
    ensure!(
        !args.room || !(args.write || args.check || args.prune || args.retire || args.sidecar_debt),
        "--room is a separate read-only query"
    );
    ensure!(
        !args.retire || !(args.write || args.check || args.prune || args.sidecar_debt),
        "--retire is a separate explicit step"
    );
    ensure!(
        !args.sidecar_debt || !(args.write || args.check || args.prune || args.allow_retired),
        "--sidecar-debt is a separate read-only query"
    );
    ensure!(
        !args.prune || !(args.write || args.check),
        "--prune is a separate explicit step"
    );
    if args.room {
        println!(
            "{}",
            serde_json::to_string_pretty(&transport::room(ctx, t, args.keep_cuts)?)?
        );
        return Ok(0);
    }
    if args.retire {
        return transport::retire(ctx, t, args.keep_cuts, false);
    }
    if args.sidecar_debt {
        let members = strings(&ctx.op("sidecar-debt", empty())?);
        let (targets, unowned) = ctx.targets_for(&members)?;
        ensure!(
            unowned.is_empty(),
            "scorecards have no producer: {}",
            unowned.join(", ")
        );
        for target in targets {
            println!("{target}");
        }
        return Ok(0);
    }
    if args.prune {
        let retired = strings(&ctx.op(
            "retired-outputs",
            json!({"declared":ctx.op("declared",json!({"same_root":true}))?}),
        )?);
        if !args.allow_retired {
            let unexplained = retirement_evidence(ctx, &retired)?;
            ensure!(
                unexplained.is_empty(),
                "retired outputs have no producing-source evidence: {}",
                unexplained.join(", ")
            );
        }
        let removed = ctx.op("prune", json!({"retired":retired}))?;
        println!("{}", serde_json::to_string_pretty(&removed)?);
        return Ok(0);
    }
    ensure!(!args.allow_retired, "--allow-retired requires --prune");
    if args.publish_held {
        let members = args
            .members_json
            .as_deref()
            .map(serde_json::from_str::<Vec<String>>)
            .transpose()?
            .map(|v| v.into_iter().collect());
        publish_held(ctx, t, &args.grafted, args.viewer_only, members.as_ref())?;
        return Ok(0);
    }
    let mut rels = ctx.solids()?;
    let mut held = ctx.held()?;
    let mut hashes = ctx.hashes(&rels)?;
    let mut sidecars = ctx.sidecars(&held)?;
    let state = ctx.op(
        "reconcile-state",
        json!({"held":held,"now":hashes,"sidecars":sidecars}),
    )?;
    if !args.write {
        println!(
            "{} generated member(s); pointer {}",
            rels.len(),
            if state["same_solids"] == true && state["same_sidecars"] == true {
                "matches"
            } else {
                "differs"
            }
        );
        return Ok(
            if args.check && !(state["same_solids"] == true && state["same_sidecars"] == true) {
                1
            } else {
                0
            },
        );
    }
    // The explicit reconciler carries current producer output through the native print driver.
    let lines = merge_maps(&[&hashes, &sidecars]);
    let tree = ctx.tree(&lines, &ctx.index()?)?;
    let debt = strings(&ctx.op("made-moves", json!({"held":held["made"],"tree":tree}))?);
    let changed = strings(&ctx.op(
        "changed-lines",
        json!({"old":merge_maps(&[&held["solids"],&held["sidecars"]]),"new":lines}),
    )?);
    let affected = debt
        .into_iter()
        .chain(changed)
        .collect::<BTreeSet<_>>()
        .into_iter()
        .collect::<Vec<_>>();
    if !affected.is_empty() {
        let (mut targets, _) = ctx.targets_for(&affected)?;
        if !targets.is_empty() {
            let planner =
                std::env::var("HSM_BUILD_PLAN").unwrap_or_else(|_| "hsm-build-plan".into());
            let mut command = vec![
                "--root".into(),
                ctx.root.to_string_lossy().into_owned(),
                "affected".into(),
                "--dirty-sources".into(),
                "--json".into(),
            ];
            for rel in keys(&sidecars)
                .into_iter()
                .chain(keys(&held["sidecars"]))
                .collect::<BTreeSet<_>>()
            {
                command.extend(["--exclude".into(), rel]);
            }
            let selected = ctx.command(&planner, &command)?;
            ensure!(
                selected.status.success(),
                "dirty-source selection failed: {}",
                String::from_utf8_lossy(&selected.stderr)
            );
            let selection: Value = serde_json::from_slice(&selected.stdout)?;
            let dirty = strings(&selection["targets"])
                .into_iter()
                .collect::<BTreeSet<_>>();
            targets.retain(|target| !dirty.contains(target));
        }
        if !targets.is_empty() {
            let driver =
                std::env::var("HSM_PRINT_BUILD").unwrap_or_else(|_| "hsm-print-build".into());
            let mut command = vec![
                "--root".into(),
                ctx.root.to_string_lossy().into_owned(),
                "--publisher".into(),
                "/usr/bin/true".into(),
            ];
            command.extend(targets);
            let result = ctx.command(&driver, &command)?;
            print!("{}", String::from_utf8_lossy(&result.stdout));
            eprint!("{}", String::from_utf8_lossy(&result.stderr));
        }
    }
    publish_held(ctx, t, &[], false, None)?;
    held = ctx.held()?;
    rels = ctx.solids()?;
    hashes = ctx.hashes(&rels)?;
    sidecars = ctx.sidecars(&held)?;
    if held["bundle"]["behind"] == true {
        let absent = keys(&held["solids"])
            .into_iter()
            .filter(|rel| !ctx.root.join(rel).is_file())
            .collect::<Vec<_>>();
        if !absent.is_empty() {
            println!(
                "  bundle remains behind; {} retained member(s) are absent locally",
                absent.len()
            );
            return Ok(0);
        }
        let full = merge_maps(&[&held["solids"], &held["sidecars"]]);
        let made = ctx.made(&held, &full, &merge_maps(&[&hashes, &sidecars]), &[], &[])?;
        let assets = upload_mesh_assets(
            ctx,
            t,
            &rels,
            &held,
            &BTreeMap::new(),
            &held["solids"],
            false,
        )?;
        cut_bundle(
            ctx,
            t,
            &held,
            &rels,
            &hashes,
            &sidecars,
            &made,
            &assets,
            now(),
            true,
            &BTreeMap::new(),
        )?;
    } else {
        let missing = keys(&held["solids"])
            .into_iter()
            .any(|rel| !ctx.root.join(rel).is_file());
        if missing {
            return Ok(0);
        }
        let digest = held["bundle"]["sha256"]
            .as_str()
            .context("published bundle digest")?;
        let asset = held["release"]["asset"]
            .as_str()
            .context("published bundle asset")?;
        let assets = transport::release_assets(ctx, t)?;
        let state = ctx.op(
            "release-state",
            json!({"assets":assets,"asset":asset,"digest":digest,"size":held["bundle"]["bytes"]}),
        )?;
        if state["matches"] != true {
            let work = Work::new(&ctx.root)?;
            let target = work.path.join("bundle.tar.gz");
            let expected = serde_json::from_value(held["solids"].clone())?;
            let actual = archive::bundle_sources(
                &ctx.root,
                &keys(&held["solids"]),
                &target,
                &BTreeMap::new(),
                &expected,
            )?;
            ensure!(
                actual == digest,
                "local bundle does not match the published cut"
            );
            transport::upload_bundle(ctx, t, &target, asset, digest, target.metadata()?.len())?;
        }
        let known = transport::objects_in_store(
            ctx,
            t,
            hashes
                .as_object()
                .into_iter()
                .flatten()
                .filter_map(|(_, sha)| sha.as_str().map(str::to_owned)),
        );
        if transport::upload_objects(ctx, t, &rels, &hashes, &known, &BTreeMap::new())?
            && held["release"]["objects"] != ctx.prefix()
        {
            held["release"]["objects"] = json!(ctx.prefix());
            ctx.write(&held)?;
        }
    }
    Ok(0)
}
