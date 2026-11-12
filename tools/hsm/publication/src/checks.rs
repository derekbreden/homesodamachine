//! Explicit offline fixtures exercise publication without contacting either object store.
use crate::{
    ContextData, POINTERS, Work, empty, keys, merge_maps, pack, publish,
    transport::{self, Transport},
};
use anyhow::{Context, Result, ensure};
use hsm_build_data::publication::archive;
use hsm_geometry::scene;
use serde_json::{Value, json};
use std::os::unix::process::ExitStatusExt;
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
    process::{Command, Output},
    sync::Mutex,
};

const VIEWER: &str = "hardware/parts/plate.step.mesh";
const PRINT: &str = "hardware/parts/plate.stl";

struct Fixture {
    work: Work,
    ctx: ContextData,
}
impl Fixture {
    fn new(parent: &Path) -> Result<Self> {
        let work = Work::new(parent)?;
        let root = &work.path;
        for directory in ["hardware/ledger", "hardware/parts", "tools/hsm/build-plan"] {
            fs::create_dir_all(root.join(directory))?;
        }
        fs::write(root.join("hardware/parts/build.rs"), "fn main() {}\n")?;
        fs::write(
            root.join("hardware/parts/dimensions.rs"),
            "pub const WIDTH:f64=8.;\n",
        )?;
        fs::write(
            root.join("hardware/ledger/materials.json"),
            serde_json::to_vec(
                &json!({"materials":[{"id":"HSM-FIXTURE","models":[{"file":"parts/plate.step"}]}]}),
            )?,
        )?;
        fs::write(
            root.join("tools/hsm/build-plan/graph.json"),
            serde_json::to_vec(
                &json!({"hardware/parts/build.rs":{"reads":["hardware/parts/dimensions.rs"],"writes":[VIEWER,PRINT]}}),
            )?,
        )?;
        let git = |args: &[&str]| -> Result<()> {
            let out = Command::new("git")
                .args(args)
                .current_dir(root)
                .env_remove("GIT_INDEX_FILE")
                .output()?;
            ensure!(
                out.status.success(),
                "fixture Git: {}",
                String::from_utf8_lossy(&out.stderr)
            );
            Ok(())
        };
        git(&["init", "--quiet"])?;
        for (key, value) in [
            ("user.name", "Publication fixture"),
            ("user.email", "fixture@example.invalid"),
            ("commit.gpgSign", "false"),
            ("core.hooksPath", "/dev/null"),
        ] {
            git(&["config", key, value])?;
        }
        git(&[
            "remote",
            "add",
            "origin",
            "https://github.com/example/publication-fixture.git",
        ])?;
        git(&[
            "add",
            "hardware/ledger/materials.json",
            "hardware/parts/build.rs",
            "hardware/parts/dimensions.rs",
            "tools/hsm/build-plan/graph.json",
        ])?;
        git(&["commit", "--quiet", "-m", "fixture sources"])?;
        fs::write(
            root.join(VIEWER),
            scene::encode(&json!({"v":4,"meshes":[]}), &[])?,
        )?;
        fs::write(root.join(PRINT), b"initial printable geometry")?;
        let mut policy: Value = serde_json::from_str(include_str!("../config.json"))?;
        policy["BUNDLED_MESH_DIRS"] = json!(["hardware/parts"]);
        policy["BUNDLED_PAYLOAD_DIRS"] = json!(["hardware/parts"]);
        let inventory = json!({"runtime_reads":{},"rust_runtime_reads":{},"inert_suffixes":[],"inert_basenames":[],"implicit_solids":{},"action_intermediate":{}});
        let ctx = ContextData::with_config(root, policy, inventory)?;
        let rels = ctx.solids()?;
        let hashes = ctx.hashes(&rels)?;
        let sidecars = empty();
        let whole = merge_maps(&[&hashes, &sidecars]);
        let made = ctx.made(&empty(), &whole, &whole, &rels, &[])?;
        let mut data =
            ctx.pointers(&empty(), &hashes, &sidecars, &made, &"a".repeat(64), 16, 1.)?;
        data["mesh_assets"] = json!([]);
        ctx.write(&data)?;
        git(&["add", POINTERS])?;
        git(&["commit", "--quiet", "-m", "fixture pointers"])?;
        Ok(Self { work, ctx })
    }
    fn root(&self) -> &Path {
        &self.work.path
    }
    fn write(&self, rel: &str, bytes: impl AsRef<[u8]>) -> Result<()> {
        let path = self.root().join(rel);
        fs::create_dir_all(path.parent().context("fixture parent")?)?;
        fs::write(path, bytes)?;
        Ok(())
    }
}

struct FakeState {
    events: Vec<String>,
    objects: BTreeMap<String, Vec<u8>>,
    store_success: bool,
    github_success: bool,
    release_exists: bool,
    mutate: Option<(PathBuf, Vec<u8>)>,
}
struct Fake {
    state: Mutex<FakeState>,
}
impl Default for Fake {
    fn default() -> Self {
        Self {
            state: Mutex::new(FakeState {
                events: vec![],
                objects: BTreeMap::new(),
                store_success: true,
                github_success: true,
                release_exists: true,
                mutate: None,
            }),
        }
    }
}
impl Fake {
    fn events(&self) -> Vec<String> {
        self.state.lock().unwrap().events.clone()
    }
    fn object(&self, url: &str) -> Option<Vec<u8>> {
        self.state.lock().unwrap().objects.get(url).cloned()
    }
}
fn output(ok: bool, bytes: impl AsRef<[u8]>) -> Output {
    Output {
        status: std::process::ExitStatus::from_raw(if ok { 0 } else { 1 << 8 }),
        stdout: bytes.as_ref().to_vec(),
        stderr: vec![],
    }
}
impl Transport for Fake {
    fn head(&self, url: &str) -> bool {
        let mut state = self.state.lock().unwrap();
        state.events.push(format!("head:{url}"));
        state.objects.contains_key(url)
    }
    fn put(&self, url: &str, file: &Path) -> bool {
        let bytes = archive::decompress(&fs::read(file).expect("fixture upload file"))
            .expect("fixture gzip");
        let mut state = self.state.lock().unwrap();
        state.events.push(format!("put:{url}"));
        if let Some((path, bytes)) = state.mutate.take() {
            fs::write(path, bytes).expect("concurrent fixture checkpoint");
        }
        if state.store_success {
            state.objects.insert(url.into(), bytes);
            true
        } else {
            false
        }
    }
    fn download(&self, url: &str, file: &Path) -> Result<()> {
        let bytes = self.object(url).context("fixture object absent")?;
        let source = file.with_extension("raw");
        fs::write(&source, bytes)?;
        archive::gzip(&source, file, 1)?;
        fs::remove_file(source)?;
        Ok(())
    }
    fn github(&self, args: &[String]) -> Result<Output> {
        let mut state = self.state.lock().unwrap();
        state.events.push(format!("gh:{}", args.join(" ")));
        if args.get(1).is_some_and(|s| s == "view") {
            return Ok(output(state.release_exists, b"{\"assets\":[]}"));
        }
        if args.get(1).is_some_and(|s| s == "create") {
            state.release_exists = true;
        }
        Ok(output(state.github_success, b""))
    }
    fn refresh(&self) -> Result<()> {
        self.state.lock().unwrap().events.push("refresh".into());
        Ok(())
    }
}

fn debt_questions(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let fake = Fake::default();
    let debt = publish::owed(ctx)?;
    ensure!(
        debt.reason.is_empty() && debt.heal.is_empty(),
        "an unchanged fixture owes publication: {debt:?}"
    );
    ensure!(
        publish::run(ctx, &fake, true)? == 0 && fake.events().is_empty(),
        "a read-only debt query contacted a remote"
    );
    fixture.write("hardware/parts/dimensions.rs", "pub const WIDTH:f64=9.;\n")?;
    ensure!(
        ctx.git(&["add", "hardware/parts/dimensions.rs"])?
            .status
            .success(),
        "stage fixture dimensions"
    );
    ensure!(
        ctx.git(&["commit", "--quiet", "-m", "fixture dimension edit"])?
            .status
            .success(),
        "commit fixture dimensions"
    );
    let debt = publish::owed(ctx)?;
    ensure!(
        debt.moved.is_empty() && debt.reason.contains("made"),
        "input-only debt was missed: {debt:?}"
    );
    let fixture = Fixture::new(parent)?;
    fixture.write(
        "hardware/ledger/materials.json",
        serde_json::to_vec(&json!({"materials":[]}))?,
    )?;
    let debt = publish::owed(&fixture.ctx)?;
    ensure!(
        debt.moved.is_empty() && debt.reason.contains("catalog"),
        "catalog-only debt was missed: {debt:?}"
    );
    fixture.write(POINTERS, b"invalid pointer JSON")?;
    ensure!(
        publish::owed(&fixture.ctx).is_err(),
        "invalid pointer bytes were treated as an unchanged or empty publication"
    );
    Ok(())
}

fn cold_and_sidecar_publication(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let fake = Fake::default();
    fs::remove_file(fixture.root().join(POINTERS))?;
    ensure!(
        publish::owed(ctx)?.reason.contains("no pointer"),
        "a missing pointer was treated as current"
    );
    pack::publish_held(ctx, &fake, &[], false, None)?;
    let held = ctx.held()?;
    ensure!(
        held["solids"][VIEWER].is_string()
            && held["solids"][PRINT].is_string()
            && held["bundle"]["sha256"].is_string(),
        "an initial publication omitted completed members"
    );
    let score = "hardware/parts/plate.scorecard.json";
    fixture.write(score, b"{\"score\":1}")?;
    let mut graph = ctx.graph_source.clone();
    graph["hardware/parts/build.rs"]["writes"]
        .as_array_mut()
        .unwrap()
        .push(json!(score));
    fixture.write("tools/hsm/build-plan/graph.json", serde_json::to_vec(&graph)?)?;
    let next = ctx.reload()?;
    ensure!(
        !next.solids()?.contains(&score.into()),
        "a catalog-selected scorecard entered the geometry member set"
    );
    ensure!(
        publish::owed(&next)?.moved.contains(&score.into()),
        "a completed sidecar was not owed"
    );
    let count = fake.events().len();
    pack::publish_held(
        &next,
        &fake,
        &[],
        false,
        Some(&BTreeSet::from([score.into()])),
    )?;
    let held = next.held()?;
    ensure!(
        held["sidecars"][score] == scene::digest(b"{\"score\":1}"),
        "a sidecar-only pass retained the preceding score"
    );
    ensure!(
        fake.events()[count..].is_empty(),
        "a sidecar-only pass uploaded geometry"
    );
    let heal = next.op(
        "heal",
        json!({"held":held,"index":next.index()?,"pointers":POINTERS}),
    )?;
    ensure!(
        crate::strings(&heal).contains(&score.into()),
        "the pointer's sidecar did not accompany its Git commit"
    );
    Ok(())
}

fn metadata_membership(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let excluded = [
        "plate.scorecard.json",
        "plate.numbers.json",
        "plate.source.json",
        "plate.print-features.json",
    ];
    let included = [
        "plate.step.json",
        "plate.facts.json",
        "plate.frame.json",
        "guide.pdf",
        "guide.pdf.json",
        "illustration.png",
        "illustration.png.scene.json",
        "board/out/board.picks.json",
    ];
    for name in excluded.iter().chain(included.iter()) {
        fixture.write(&format!("hardware/parts/{name}"), b"{}")?;
    }
    let mut models = vec![
        json!({"file":"parts/plate.step"}),
        json!({"file":"parts/guide.pdf"}),
        json!({"file":"parts/board/out/board.step"}),
    ];
    models.extend(
        excluded
            .iter()
            .map(|name| json!({"file":format!("parts/{name}")})),
    );
    fixture.write(
        "hardware/ledger/materials.json",
        serde_json::to_vec(&json!({"materials":[{"id":"HSM-FIXTURE","models":models}]}))?,
    )?;
    let mut graph = fixture.ctx.graph_source.clone();
    graph["hardware/parts/build.rs"]["writes"]
        .as_array_mut()
        .unwrap()
        .extend(
            excluded
                .iter()
                .chain(included.iter())
                .map(|name| json!(format!("hardware/parts/{name}"))),
        );
    fixture.write("tools/hsm/build-plan/graph.json", serde_json::to_vec(&graph)?)?;
    let mut policy = fixture.ctx.policy.clone();
    policy["BUNDLED_BOARD_DIRS"] = json!(["hardware/parts/board/out"]);
    policy["BUNDLED_ART_DIRS"] = json!(["hardware/parts"]);
    let ctx = ContextData::with_config(fixture.root(), policy, fixture.ctx.inventory.clone())?;
    let solids = ctx.solids()?;
    for name in excluded {
        ensure!(
            !solids.contains(&format!("hardware/parts/{name}")),
            "catalog metadata entered geometry membership: {name}"
        );
    }
    for name in included {
        ensure!(
            solids.contains(&format!("hardware/parts/{name}")),
            "a website JSON/art consumer left publication: {name}"
        );
    }
    Ok(())
}

fn changing_checkpoint(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let fake = Fake::default();
    let first = scene::encode(&json!({"v":4,"meshes":[],"src":"completed mechanics"}), &[])?;
    let next = scene::encode(&json!({"v":4,"meshes":[],"src":"completed wiring"}), &[])?;
    fixture.write(VIEWER, &first)?;
    fake.state.lock().unwrap().mutate = Some((fixture.root().join(VIEWER), next.clone()));
    pack::publish_held(
        ctx,
        &fake,
        &[],
        true,
        Some(&BTreeSet::from([VIEWER.into()])),
    )?;
    let held = ctx.held()?;
    let first_sha = scene::digest(&first);
    ensure!(
        held["solids"][VIEWER] == first_sha,
        "a concurrent checkpoint was recorded under an earlier upload"
    );
    ensure!(
        fake.object(&format!("{}{}", ctx.store_url(), ctx.asset(&first_sha))) == Some(first),
        "uploaded bytes did not come from the frozen checkpoint"
    );
    let debt = publish::owed(ctx)?;
    ensure!(
        debt.moved.contains(&VIEWER.into()),
        "a checkpoint completed during upload was lost"
    );
    pack::publish_held(
        ctx,
        &fake,
        &[],
        true,
        Some(&BTreeSet::from([VIEWER.into()])),
    )?;
    ensure!(
        ctx.held()?["solids"][VIEWER] == scene::digest(&next),
        "the next publication missed the later checkpoint"
    );
    Ok(())
}

fn cached_and_indexed_inputs(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let rel = "hardware/parts/cache.step";
    fixture.write(rel, b"original")?;
    let path = fixture.root().join(rel);
    let before = path.metadata()?;
    let hashes = ctx.hashes(&[rel.into()])?;
    fixture.write(rel, b"modified")?;
    fs::File::options().write(true).open(&path)?.set_times(
        fs::FileTimes::new()
            .set_accessed(before.accessed()?)
            .set_modified(before.modified()?),
    )?;
    ensure!(
        ctx.hashes(&[rel.into()])? != hashes,
        "same-size bytes with restored mtime reused a stale digest"
    );
    let replacement = fixture.root().join("replacement");
    fs::write(&replacement, b"replaced")?;
    fs::rename(replacement, &path)?;
    ensure!(
        ctx.hashes(&[rel.into()])?[rel] == scene::digest(b"replaced"),
        "replaced inode retained an earlier digest"
    );
    fixture.write(".cache/cad-artifact-digests.json", b"[")?;
    ensure!(
        ctx.hashes(&[rel.into()])?[rel] == scene::digest(b"replaced"),
        "a malformed cache prevented cold hashing"
    );
    fixture.write("hardware/parts/later.rs", b"new source")?;
    std::os::unix::fs::symlink(
        "dimensions.rs",
        fixture.root().join("hardware/parts/source-link"),
    )?;
    ensure!(
        ctx.git(&["add", "hardware/parts/source-link"])?
            .status
            .success(),
        "stage fixture symlink"
    );
    ensure!(
        ctx.git(&["add", "-N", "hardware/parts/later.rs"])?
            .status
            .success(),
        "stage fixture intent to add"
    );
    let listed = |ctx: &ContextData| -> Result<Value> {
        let out = ctx.git(&["ls-files", "--stage", "-z"])?;
        ensure!(out.status.success(), "Git index listing failed");
        let mut map = serde_json::Map::new();
        for row in out.stdout.split(|b| *b == 0) {
            let Some((meta, path)) = row
                .iter()
                .position(|b| *b == b'\t')
                .map(|at| (&row[..at], &row[at + 1..]))
            else {
                continue;
            };
            let fields = meta.split(|b| b.is_ascii_whitespace()).collect::<Vec<_>>();
            if fields.len() == 3 && fields[2] == b"0" {
                map.insert(
                    String::from_utf8(path.to_vec())?,
                    json!(String::from_utf8(fields[1].to_vec())?),
                );
            }
        }
        Ok(Value::Object(map))
    };
    ensure!(
        ctx.index()? == listed(ctx)?,
        "native index differs from Git's staged listing"
    );
    ensure!(
        hsm_build_data::artifacts::blob_id(&fixture.root().join("hardware/parts/source-link"))
            == ctx.index()?["hardware/parts/source-link"],
        "symlink identity differs from Git"
    );
    for flags in [
        vec!["update-index", "--index-version", "4"],
        vec!["update-index", "--split-index"],
    ] {
        ensure!(
            ctx.git(&flags)?.status.success(),
            "write alternate Git index"
        );
        ensure!(
            ctx.index()? == listed(ctx)?,
            "alternate Git index did not fall back to Git"
        );
    }
    Ok(())
}

fn progressive_and_new_members(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let before = ctx.held()?;
    let fake = Fake::default();
    let object = scene::encode(&json!({"v":3,"meshes":[]}), &[])?;
    let object_hash = scene::digest(&object);
    fixture.write(
        &format!(".cache/meshes/scene-assets/{object_hash}.mesh"),
        &object,
    )?;
    let viewer = scene::encode(
        &json!({"v":4,"meshes":[{"name":"plate","asset":object_hash}]}),
        &[],
    )?;
    fixture.write(VIEWER, &viewer)?;
    fixture.write(PRINT, b"changed printable geometry")?;
    let selected = BTreeSet::from([VIEWER.into(), PRINT.into()]);
    pack::publish_held(ctx, &fake, &[], true, Some(&selected))?;
    let first = ctx.held()?;
    ensure!(
        first["solids"][VIEWER] == scene::digest(&viewer),
        "completed viewer member did not advance"
    );
    ensure!(
        first["solids"][PRINT] == before["solids"][PRINT],
        "manufacturing advanced during the first view"
    );
    let events = fake.events();
    let asset = events
        .iter()
        .position(|v| v == &format!("put:{}{}", ctx.store_url(), ctx.asset(&object_hash)))
        .context("shared object upload")?;
    let manifest = events
        .iter()
        .position(|v| {
            v == &format!(
                "put:{}{}",
                ctx.store_url(),
                ctx.asset(&scene::digest(&viewer))
            )
        })
        .context("manifest upload")?;
    ensure!(
        asset < manifest,
        "a manifest uploaded before its shared mesh object"
    );
    pack::publish_held(ctx, &fake, &[], false, Some(&selected))?;
    let second = ctx.held()?;
    ensure!(
        second["solids"][PRINT] == scene::digest(b"changed printable geometry"),
        "manufacturing member did not advance after the viewer"
    );
    ensure!(
        second["solids"][VIEWER] == first["solids"][VIEWER],
        "manufacturing pass changed the first view"
    );
    let mut held = second;
    held["solids"]["hardware/parts/absent.step.mesh"] = json!("b".repeat(64));
    held["mesh_assets"]
        .as_array_mut()
        .unwrap()
        .push(json!("c".repeat(64)));
    ctx.write(&held)?;
    let new = "hardware/parts/new.step.mesh";
    let newbytes = scene::encode(&json!({"v":4,"meshes":[],"src":"new part"}), &[])?;
    fixture.write(new, &newbytes)?;
    let mut graph = ctx.graph_source.clone();
    graph["hardware/parts/new.rs"] = json!({"reads":[],"writes":[new]});
    fixture.write("tools/hsm/build-plan/graph.json", serde_json::to_vec(&graph)?)?;
    fixture.write("hardware/ledger/materials.json",serde_json::to_vec(&json!({"materials":[{"id":"HSM-FIXTURE","models":[{"file":"parts/plate.step"}]},{"id":"HSM-NEW","models":[{"file":"parts/new.step"}]}]}))?)?;
    let next = ctx.reload()?;
    let debt = publish::owed(&next)?;
    ensure!(
        debt.moved.contains(&new.into()),
        "new producer membership was not discovered"
    );
    pack::publish_held(&next, &fake, &[], true, Some(&BTreeSet::from([new.into()])))?;
    let held = next.held()?;
    ensure!(
        held["solids"][new] == scene::digest(&newbytes)
            && held["website"]["solids"][new] == held["solids"][new],
        "a new part did not enter the published website selection"
    );
    ensure!(
        held["solids"]["hardware/parts/absent.step.mesh"] == "b".repeat(64),
        "a selective update retired an absent retained member"
    );
    fixture.write(PRINT, b"next printable geometry")?;
    pack::publish_held(&next, &fake, &[], false, None)?;
    ensure!(
        crate::strings(&next.held()?["mesh_assets"]).contains(&"c".repeat(64)),
        "an absent retained manifest lost its shared mesh object retention"
    );
    Ok(())
}

fn partial_reference_refresh(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let good = "hardware/parts/a-host.step.mesh";
    let bad = "hardware/parts/z-bad.step.mesh";
    fixture.write(
        VIEWER,
        scene::encode(&json!({"v":4,"meshes":[],"src":"new source"}), &[])?,
    )?;
    let mut groups = empty();
    groups[VIEWER] = json!([{"prefix":"","transform":[[1,0,0,0],[0,1,0,0],[0,0,1,0]]}]);
    fixture.write(
        good,
        scene::encode(&json!({"v":4,"meshes":[],"source_groups":groups}), &[])?,
    )?;
    fixture.write(bad, scene::encode(&json!({"v":4,"meshes":null}), &[])?)?;
    let built = "hardware/parts/m-built.step.mesh";
    let revision = scene::digest(&fs::read(fixture.root().join(VIEWER))?);
    let as_built = scene::encode(
        &json!({"v":4,"sources":{(VIEWER):revision},"meshes":[{"name":"plate","source":VIEWER,
            "source_sha256":revision,"asset":"a".repeat(64),"bytes":0,
            "entries":[{"name":"plate","color":null}]}]}),
        &[],
    )?;
    fixture.write(built, &as_built)?;
    let behind = "hardware/parts/n-behind.step.mesh";
    let earlier = scene::digest(b"an earlier revision");
    fixture.write(
        behind,
        scene::encode(
            &json!({"v":4,"sources":{(VIEWER):earlier},
                "source_inventory":{(VIEWER):[{"name":"plate","transform":null}]},
                "meshes":[{"name":"plate","source":VIEWER,"source_sha256":earlier,
                    "asset":"a".repeat(64),"bytes":0,"entries":[{"name":"plate","color":null}]}]}),
            &[],
        )?,
    )?;
    let mut graph = ctx.graph_source.clone();
    graph["hardware/parts/build.rs"]["writes"]
        .as_array_mut()
        .unwrap()
        .extend([json!(good), json!(bad), json!(built), json!(behind)]);
    fixture.write("tools/hsm/build-plan/graph.json", serde_json::to_vec(&graph)?)?;
    let ctx = ctx.reload()?;
    let refreshed = pack::refresh_sources(&ctx, &[VIEWER.into()])?;
    ensure!(
        refreshed.grafted == [good, behind]
            && refreshed.errors.iter().any(|row| row.contains(bad)),
        "a later refresh failure discarded completed hosts"
    );
    ensure!(
        fs::read(fixture.root().join(built))? == as_built,
        "a host built from the current source was rewritten"
    );
    ensure!(
        hsm_build_data::payload::header(fixture.root().join(behind))?["sources"][VIEWER]
            == revision,
        "a host behind the current source kept its earlier revision"
    );
    let head = hsm_build_data::payload::header(fixture.root().join(good))?;
    ensure!(
        head["sources"][VIEWER] == scene::digest(&fs::read(fixture.root().join(VIEWER))?),
        "the completed host did not bind the current source"
    );
    let fake = Fake::default();
    pack::publish_held(
        &ctx,
        &fake,
        &refreshed.grafted,
        true,
        Some(&BTreeSet::from([VIEWER.into(), good.into()])),
    )?;
    ensure!(
        ctx.held()?["solids"][good].is_string(),
        "the completed host was omitted from partial publication"
    );
    Ok(())
}

fn obsolete_standalone_exports(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let step = "hardware/parts/plate.step";
    fixture.write(step, b"retired standalone export")?;
    fixture.write(
        VIEWER,
        scene::encode(&json!({"v":4,"meshes":[],"step_export":false}), &[])?,
    )?;
    let mut held = ctx.held()?;
    held["solids"][step] = json!(scene::digest(b"retired standalone export"));
    ctx.write(&held)?;
    ensure!(
        !ctx.solids()?.contains(&step.into()),
        "a shared scene's retired standalone export remains eligible"
    );
    let fake = Fake::default();
    pack::publish_held(ctx, &fake, &[], true, None)?;
    ensure!(
        ctx.held()?["solids"].get(step).is_none(),
        "a retired standalone export returned to the pointer file"
    );
    ensure!(
        !publish::owed(ctx)?.moved.contains(&step.into()),
        "a retired standalone export continually owes another upload"
    );
    Ok(())
}

fn archived_producer_graphs(parent: &Path) -> Result<()> {
    for legacy in [false, true] {
        let fixture = Fixture::new(parent)?;
        let ctx = &fixture.ctx;
        let current_graph = "tools/hsm/build-plan/graph.json";
        let archived_graph = if legacy {
            "tools/bazel/graph.json"
        } else {
            current_graph
        };
        if legacy {
            fs::create_dir_all(fixture.root().join("tools/bazel"))?;
            ensure!(ctx.git(&["mv", current_graph, archived_graph])?.status.success(), "archive fixture graph");
            ensure!(ctx.git(&["commit", "--quiet", "-m", "fixture historical graph"])?.status.success(), "commit archived fixture graph");
        }
        let archived_commit = ctx.git_text(&["rev-parse", "HEAD"])?;
        ensure!(ctx.git(&["rm", "--", "hardware/parts/build.rs", archived_graph])?.status.success(), "retire fixture producer");
        fixture.write(current_graph, b"{}")?;
        ensure!(ctx.git(&["add", current_graph])?.status.success(), "stage current fixture graph");
        ensure!(ctx.git(&["commit", "--quiet", "-m", "fixture retired source"])?.status.success(), "commit fixture source retirement");
        let mut held = ctx.held()?;
        held["made"][VIEWER]["commit"] = json!(archived_commit);
        ctx.write(&held)?;
        ensure!(pack::retirement_evidence(ctx, &[VIEWER.into()])?.is_empty(), "archived producer graph loses source-retirement evidence: {archived_graph}");
    }
    Ok(())
}

fn board_glb_with_stale_mesh(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let board = "hardware/pcb/pcba/out/pcba.glb";
    let named = "hardware/assembly/scenes/glb/fixture.glb";
    for relative in [board, named] {
        fixture.write(relative, b"old GLB")?;
        fixture.write(
            &format!("{relative}.mesh"),
            scene::encode(&json!({"v":4,"meshes":[],"src":"stale sibling"}), &[])?,
        )?;
    }
    fixture.write(
        "hardware/ledger/materials.json",
        serde_json::to_vec(&json!({"materials":[
            {"id":"HSM-FIXTURE","models":[{"file":"parts/plate.step"}]},
            {"id":"HSM-PCB-FIXTURE","models":[{"file":"printed-parts/electronics/pcba-tray/pcba-board.step"}]}
        ]}))?,
    )?;
    for name in [
        "pcba.top3d.png",
        "pcba.bottom3d.png",
        "pcba.picks.json",
        "pcba.circuit.json",
        "pcba.numbers.json",
    ] {
        fixture.write(&format!("hardware/pcb/pcba/out/{name}"), b"{}")?;
    }
    let ctx = fixture.ctx.reload()?;
    let mut held = ctx.held()?;
    held["solids"][board] = json!(scene::digest(b"old GLB"));
    held["solids"][named] = json!(scene::digest(b"old GLB"));
    ctx.write(&held)?;
    fixture.write(board, b"native board GLB with current component hierarchy")?;
    ensure!(
        ctx.solids()?.contains(&board.into()),
        "a board's stale sibling hides its current GLB"
    );
    let solids = ctx.solids()?;
    for name in ["pcba.top3d.png", "pcba.bottom3d.png", "pcba.picks.json"] {
        ensure!(
            solids.contains(&format!("hardware/pcb/pcba/out/{name}")),
            "the current board family loses {name} with a STEP-only catalog model"
        );
    }
    for name in ["pcba.circuit.json", "pcba.numbers.json"] {
        ensure!(
            !solids.contains(&format!("hardware/pcb/pcba/out/{name}")),
            "board source/metadata enters website membership: {name}"
        );
    }
    ensure!(
        !ctx.solids()?.contains(&named.into()),
        "a shared named view republishes its duplicate GLB"
    );
    ensure!(
        crate::is_viewer(board),
        "the browser's board GLB waits behind manufacturing publication"
    );
    ensure!(
        publish::owed(&ctx)?.moved.contains(&board.into()),
        "a changed board GLB is not owed"
    );
    let fake = Fake::default();
    pack::publish_held(
        &ctx,
        &fake,
        &[],
        true,
        Some(&BTreeSet::from([board.into()])),
    )?;
    let held = ctx.held()?;
    ensure!(
        held["solids"][board] == scene::digest(&fs::read(fixture.root().join(board))?),
        "the first-view pointer did not adopt the completed board GLB"
    );
    ensure!(
        held["solids"].get(named).is_none(),
        "a redundant named-view GLB survived retirement"
    );
    ensure!(
        !publish::owed(&ctx)?.moved.contains(&board.into()),
        "the current board GLB still owes publication"
    );
    Ok(())
}

fn frozen_sidecar_commits(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let score = "hardware/parts/plate.scorecard.json";
    let ctx = &fixture.ctx;
    let mut graph = ctx.graph_source.clone();
    graph["hardware/parts/build.rs"]["writes"]
        .as_array_mut()
        .unwrap()
        .push(json!(score));
    fixture.write("tools/hsm/build-plan/graph.json", serde_json::to_vec(&graph)?)?;
    fixture.write(score, b"{\"score\":1}")?;
    let ctx = ctx.reload()?;
    let mut held = ctx.held()?;
    held["sidecars"][score] = json!(scene::digest(b"{\"score\":1}"));
    ctx.write(&held)?;
    ensure!(
        ctx.git(&["add", score, POINTERS])?.status.success(),
        "stage initial fixture sidecar"
    );
    ensure!(
        ctx.git(&["commit", "--quiet", "-m", "fixture sidecar"])?
            .status
            .success(),
        "commit initial fixture sidecar"
    );
    fixture.write(score, b"{\"score\":2}")?;
    ensure!(
        ctx.git(&["add", score])?.status.success(),
        "stage a concurrent sidecar edit"
    );
    fixture.write(
        VIEWER,
        scene::encode(&json!({"v":4,"meshes":[],"src":"new view"}), &[])?,
    )?;
    let fake = Fake::default();
    let published = pack::publish_held(
        &ctx,
        &fake,
        &[],
        true,
        Some(&BTreeSet::from([VIEWER.into()])),
    )?;
    let viewer_files = publish::snapshot_files(&ctx, &ctx.held()?, &published)?;
    let pointer_side = viewer_files
        .iter()
        .find(|row| row["path"] == score)
        .context("viewer sidecar snapshot")?;
    let blob = ctx.git(&["cat-file", "blob", pointer_side["blob"].as_str().unwrap()])?;
    ensure!(
        blob.stdout == b"{\"score\":1}",
        "a first view captured an unpointed newer scorecard"
    );
    ensure!(
        fs::read(fixture.root().join(score))? == b"{\"score\":2}",
        "snapshot preparation overwrote a later scorecard"
    );
    fixture.write(PRINT, b"next printable result")?;
    fake.state.lock().unwrap().mutate =
        Some((fixture.root().join(score), b"{\"score\":3}".to_vec()));
    let published = pack::publish_held(&ctx, &fake, &[], false, None)?;
    let held = ctx.held()?;
    let files = publish::snapshot_files(&ctx, &held, &published)?;
    let row = files
        .iter()
        .find(|row| row["path"] == score)
        .context("manufacturing sidecar snapshot")?;
    let blob = ctx.git(&["cat-file", "blob", row["blob"].as_str().unwrap()])?;
    ensure!(
        blob.stdout == b"{\"score\":2}" && held["sidecars"][score] == scene::digest(&blob.stdout),
        "the frozen sidecar commit differs from its pointer digest"
    );
    ensure!(
        fs::read(fixture.root().join(score))? == b"{\"score\":3}",
        "the frozen snapshot replaced later live work"
    );
    ensure!(
        publish::owed(&ctx)?.moved.contains(&score.into()),
        "a sidecar completed during upload ceased to be owed"
    );
    Ok(())
}

fn failed_upload_keeps_pointers(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let before = fs::read(fixture.root().join(POINTERS))?;
    let fake = Fake::default();
    {
        let mut state = fake.state.lock().unwrap();
        state.store_success = false;
        state.github_success = false;
    }
    let bytes = scene::encode(&json!({"v":4,"meshes":[],"src":"attempt"}), &[])?;
    fixture.write(VIEWER, bytes)?;
    ensure!(
        pack::publish_held(
            ctx,
            &fake,
            &[],
            true,
            Some(&BTreeSet::from([VIEWER.into()]))
        )
        .is_err(),
        "a failed member upload reported completion"
    );
    ensure!(
        fs::read(fixture.root().join(POINTERS))? == before,
        "a failed upload advanced the pointer file"
    );
    let object = scene::encode(&json!({"v":3,"meshes":[]}), &[])?;
    let sha = scene::digest(&object);
    fixture.write(&format!(".cache/meshes/scene-assets/{sha}.mesh"), object)?;
    fixture.write(
        VIEWER,
        scene::encode(&json!({"v":4,"meshes":[{"asset":sha}]}), &[])?,
    )?;
    let count = fake.events().len();
    ensure!(
        pack::publish_held(
            ctx,
            &fake,
            &[],
            true,
            Some(&BTreeSet::from([VIEWER.into()]))
        )
        .is_err(),
        "a failed shared object upload reported completion"
    );
    ensure!(
        fake.events()[count..]
            .iter()
            .all(|row| !row.starts_with("gh:release upload")),
        "a manifest was offered after its shared object failed"
    );
    ensure!(
        fs::read(fixture.root().join(POINTERS))? == before,
        "a failed shared object upload advanced the pointer file"
    );
    Ok(())
}

fn object_and_release_transport(parent: &Path) -> Result<()> {
    let fixture = Fixture::new(parent)?;
    let ctx = &fixture.ctx;
    let fake = Fake::default();
    fixture.write("hardware/parts/twin-a.step", b"same object")?;
    fixture.write("hardware/parts/twin-b.step", b"same object")?;
    let sha = scene::digest(b"same object");
    let hashes = json!({"hardware/parts/twin-a.step":sha,"hardware/parts/twin-b.step":sha});
    ensure!(
        transport::upload_objects(
            ctx,
            &fake,
            &keys(&hashes),
            &hashes,
            &BTreeSet::new(),
            &BTreeMap::new()
        )?,
        "store upload failed"
    );
    ensure!(
        fake.events()
            .iter()
            .filter(|s| s.starts_with("put:"))
            .count()
            == 1,
        "identical bytes uploaded more than once"
    );
    ensure!(
        fake.object(&format!("{}{}", ctx.store_url(), ctx.asset(&sha)))
            == Some(b"same object".to_vec()),
        "store bytes do not match the named digest"
    );
    let fallback = Fake::default();
    fallback.state.lock().unwrap().store_success = false;
    ensure!(
        transport::upload_objects(
            ctx,
            &fallback,
            &keys(&hashes),
            &hashes,
            &BTreeSet::new(),
            &BTreeMap::new()
        )?,
        "GitHub member fallback failed"
    );
    ensure!(
        fallback
            .events()
            .iter()
            .filter(|s| s.starts_with("gh:release upload"))
            .count()
            == 1,
        "GitHub fallback lost hash deduplication"
    );
    let file = fixture.root().join("bundle.gz");
    fs::write(&file, b"bundle")?;
    transport::upload_bundle(ctx, &fake, &file, "cad-fixture.tar.gz", "fixture", 6)?;
    ensure!(
        fake.events()
            .iter()
            .all(|s| !s.starts_with("gh:release create")),
        "an existing empty release was recreated"
    );
    let absent = Fake::default();
    absent.state.lock().unwrap().release_exists = false;
    transport::upload_bundle(ctx, &absent, &file, "cad-fixture.tar.gz", "fixture", 6)?;
    ensure!(
        absent
            .events()
            .iter()
            .any(|s| s.starts_with("gh:release create")),
        "a missing release was not created"
    );
    Ok(())
}

fn frozen_bundle(parent: &Path) -> Result<()> {
    let work = Work::new(parent)?;
    let source = work.path.join("part.step");
    fs::write(&source, b"original")?;
    let frozen = work.path.join("frozen");
    fs::copy(&source, &frozen)?;
    fs::write(&source, b"concurrent edit")?;
    let sources = BTreeMap::from([("part.step".into(), frozen)]);
    let expected = BTreeMap::from([("part.step".into(), scene::digest(b"original"))]);
    let a = work.path.join("a.gz");
    let b = work.path.join("b.gz");
    let rels = vec!["part.step".into()];
    let sha = archive::bundle_sources(&work.path, &rels, &a, &sources, &expected)?;
    ensure!(
        archive::bundle_sources(&work.path, &rels, &b, &sources, &expected)? == sha
            && fs::read(&a)? == fs::read(&b)?,
        "bundles are not deterministic"
    );
    let tar = archive::decompress(&fs::read(a)?)?;
    ensure!(
        &tar[512..520] == b"original",
        "bundle read live bytes instead of its frozen source"
    );
    ensure!(
        archive::bundle_sources(&work.path, &rels, &b, &BTreeMap::new(), &expected).is_err(),
        "a changed bundle member kept a stale digest"
    );
    Ok(())
}

pub fn run(parent: &Path) -> Result<i32> {
    for (name, check) in [
        ("debt queries", debt_questions as fn(&Path) -> Result<()>),
        ("progressive and new members", progressive_and_new_members),
        ("failed uploads", failed_upload_keeps_pointers),
        ("object and release transport", object_and_release_transport),
        ("frozen bundle", frozen_bundle),
        ("concurrent checkpoints", changing_checkpoint),
        ("cached and indexed inputs", cached_and_indexed_inputs),
        ("cold and sidecar publication", cold_and_sidecar_publication),
        ("partial reference refresh", partial_reference_refresh),
        ("obsolete standalone exports", obsolete_standalone_exports),
        ("archived producer graphs", archived_producer_graphs),
        ("board GLB with stale mesh", board_glb_with_stale_mesh),
        ("frozen sidecar commits", frozen_sidecar_commits),
        ("metadata membership", metadata_membership),
    ] {
        check(parent).with_context(|| name.to_owned())?;
        println!("publication fixture: {name}");
    }
    Ok(0)
}

#[cfg(test)]
mod tests {
    use super::*;
    fn parent() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .ancestors()
            .nth(3)
            .unwrap()
            .to_owned()
    }
    #[test]
    fn debt_queries() -> Result<()> {
        debt_questions(&parent())
    }
    #[test]
    fn progressive_members() -> Result<()> {
        progressive_and_new_members(&parent())
    }
    #[test]
    fn failure_is_atomic() -> Result<()> {
        failed_upload_keeps_pointers(&parent())
    }
    #[test]
    fn transports() -> Result<()> {
        object_and_release_transport(&parent())
    }
    #[test]
    fn frozen_bytes() -> Result<()> {
        frozen_bundle(&parent())
    }
    #[test]
    fn concurrent_checkpoints() -> Result<()> {
        changing_checkpoint(&parent())
    }
    #[test]
    fn cached_indexed_inputs() -> Result<()> {
        cached_and_indexed_inputs(&parent())
    }
    #[test]
    fn cold_and_sidecars() -> Result<()> {
        cold_and_sidecar_publication(&parent())
    }
    #[test]
    fn partial_refresh() -> Result<()> {
        partial_reference_refresh(&parent())
    }
    #[test]
    fn obsolete_exports() -> Result<()> {
        obsolete_standalone_exports(&parent())
    }
    #[test]
    fn archived_graph_lineage() -> Result<()> {
        archived_producer_graphs(&parent())
    }
    #[test]
    fn board_glb_source() -> Result<()> {
        board_glb_with_stale_mesh(&parent())
    }
    #[test]
    fn sidecar_commits() -> Result<()> {
        frozen_sidecar_commits(&parent())
    }
    #[test]
    fn metadata_scope() -> Result<()> {
        metadata_membership(&parent())
    }
}
