//! Firmware publication packages the phone's image targets without flashing a device.
use crate::{ContextData, Work, empty, read_json};
use anyhow::{Context, Result, ensure};
use clap::Parser;
use hsm_build_data::publication::archive;
use hsm_geometry::scene::digest;
use hsm_publication::transport::{self, Transport};
use serde_json::{Value, json};
use std::{
    collections::{BTreeMap, BTreeSet},
    fs,
    path::{Path, PathBuf},
    process::Command,
    sync::Arc,
};

const POINTERS: &str = "firmware/firmware-images.json";
const TAG: &str = "firmware";
#[derive(Clone, Copy)]
struct Target {
    name: &'static str,
    environment: &'static str,
    source: &'static str,
    what: &'static str,
    art: bool,
}
const TARGETS: [Target; 4] = [
    Target {
        name: "appliance",
        environment: "appliance",
        source: "src_appliance",
        what: "the main board's own firmware",
        art: false,
    },
    Target {
        name: "art",
        environment: "esp32s3_front",
        source: "src_front",
        what: "the machine display's loading animation",
        art: true,
    },
    Target {
        name: "enclosure",
        environment: "esp32s3_front",
        source: "src_front",
        what: "the 4.3\" machine display",
        art: false,
    },
    Target {
        name: "faucet",
        environment: "esp32s3_faucet",
        source: "src_faucet",
        what: "the 1.47\" faucet display",
        art: false,
    },
];
#[derive(Parser, Default)]
#[command(
    name = "hsm-publish-firmware",
    about = "Build or inspect the phone's firmware images and publish an explicitly requested bundle"
)]
struct Args {
    #[arg(long)]
    write: bool,
    #[arg(long)]
    check: bool,
    #[arg(long)]
    no_build: bool,
    #[arg(value_parser=["appliance","art","enclosure","faucet"])]
    targets: Vec<String>,
}
struct Programs {
    pio: PathBuf,
    marketing: PathBuf,
}
impl Programs {
    fn load() -> Self {
        let pio = std::env::var_os("HSM_PIO_BIN")
            .map(PathBuf::from)
            .or_else(|| {
                std::env::var_os("HOME")
                    .map(|root| PathBuf::from(root).join(".platformio/penv/bin/pio"))
                    .filter(|path| path.is_file())
            })
            .unwrap_or_else(|| "pio".into());
        Self {
            pio,
            marketing: std::env::var_os("HSM_MARKETING_BIN")
                .map(PathBuf::from)
                .unwrap_or_else(|| "hsm-marketing".into()),
        }
    }
}
fn selected(names: &[String]) -> Vec<Target> {
    TARGETS
        .into_iter()
        .filter(|target| names.is_empty() || names.iter().any(|name| name == target.name))
        .collect()
}
fn image_path(root: &Path, target: Target) -> PathBuf {
    root.join(".pio/build")
        .join(target.environment)
        .join(if target.art {
            "art.bin"
        } else {
            "firmware.bin"
        })
}
fn crc32(bytes: &[u8]) -> u32 {
    let table: [u32; 256] = std::array::from_fn(|index| {
        let mut value = index as u32;
        for _ in 0..8 {
            value = (value >> 1) ^ if value & 1 != 0 { 0xedb88320 } else { 0 };
        }
        value
    });
    !bytes.iter().fold(u32::MAX, |crc, byte| {
        table[((crc ^ u32::from(*byte)) & 255) as usize] ^ (crc >> 8)
    })
}
fn define<'a>(header: &'a str, name: &str) -> Option<&'a str> {
    header.lines().find_map(|line| {
        let line = line.trim_start().strip_prefix("#define")?.trim_start();
        let at = line.find(char::is_whitespace)?;
        (&line[..at] == name).then(|| line[at..].trim_start())
    })
}
fn version(header: &str) -> Option<String> {
    Some(
        define(header, "FW_VERSION")?
            .strip_prefix('"')?
            .split_once('"')?
            .0
            .into(),
    )
}
fn epoch(header: &str) -> Option<u64> {
    let raw = define(header, "FW_BUILD_EPOCH")?;
    raw.chars()
        .take_while(char::is_ascii_digit)
        .collect::<String>()
        .parse()
        .ok()
}
fn metadata(target: Target, bytes: &[u8], header: &str) -> Value {
    let mut row = json!({"env":target.environment,"machine":"appliance","what":target.what,"kind":if target.art{"art"}else{"app"},"version":if target.art{None}else{version(header)},"build_epoch":if target.art{None}else{epoch(header)},"bytes":bytes.len(),"crc32":crc32(bytes),"sha256":digest(bytes),"file":format!("{}.bin",target.name)});
    if target.art {
        row["art_crc32"] = json!(
            bytes
                .iter()
                .skip(16)
                .take(4)
                .enumerate()
                .fold(0u32, |value, (at, byte)| value
                    | (u32::from(*byte) << (at * 8)))
        );
    }
    row
}
struct Images {
    rows: Value,
    sources: BTreeMap<String, PathBuf>,
}
fn collect(ctx: &ContextData, targets: &[Target], freeze: Option<&Path>) -> Result<Images> {
    let mut rows = serde_json::Map::new();
    let mut sources = BTreeMap::new();
    for &target in targets {
        let source = image_path(&ctx.root, target);
        if !source.is_file() {
            continue;
        }
        let path = if let Some(directory) = freeze {
            fs::create_dir_all(directory)?;
            let path = directory.join(format!("{}.bin", target.name));
            fs::copy(&source, &path)?;
            path
        } else {
            source
        };
        let bytes = fs::read(&path)?;
        let header = fs::read_to_string(
            ctx.root
                .join("firmware")
                .join(target.source)
                .join("fw_version.h"),
        )
        .unwrap_or_default();
        let row = metadata(target, &bytes, &header);
        sources.insert(row["file"].as_str().unwrap().into(), path);
        rows.insert(target.name.into(), row);
    }
    Ok(Images {
        rows: Value::Object(rows),
        sources,
    })
}
fn build(ctx: &ContextData, target: Target, programs: &Programs) -> Result<()> {
    let mut command = if target.art {
        let mut command = Command::new(&programs.marketing);
        command.args(["make-art", "enclosure", "-q"]);
        command
    } else {
        let mut command = Command::new(&programs.pio);
        command.args(["run", "--jobs", "2", "-e", target.environment]);
        command
    };
    command
        .current_dir(&ctx.root)
        .env("HSM_ROOT", &ctx.root)
        .env_remove("GIT_INDEX_FILE");
    if let Some(lease) = &ctx.lease {
        lease.apply(&mut command)?;
    }
    let output = hsm_run_slots::ipc::output(&mut command)
        .with_context(|| format!("{}: start image builder", target.name))?;
    let tail = String::from_utf8_lossy(&output.stdout)
        .lines()
        .chain(String::from_utf8_lossy(&output.stderr).lines())
        .map(str::to_owned)
        .collect::<Vec<_>>();
    ensure!(
        output.status.success(),
        "{}: image build failed; firmware release unchanged\n{}",
        target.name,
        tail[tail.len().saturating_sub(20)..].join("\n")
    );
    ensure!(
        image_path(&ctx.root, target).is_file(),
        "{}: build produced no image; firmware release unchanged",
        target.name
    );
    Ok(())
}
fn dirty_paths(bytes: &[u8]) -> Result<Vec<String>> {
    let fields = bytes.split(|byte| *byte == 0).collect::<Vec<_>>();
    let mut paths = BTreeSet::new();
    let mut at = 0;
    while at < fields.len() {
        let row = fields[at];
        at += 1;
        if row.len() < 4 {
            continue;
        }
        let path = std::str::from_utf8(&row[3..])?;
        if !path.ends_with('/') && !path.is_empty() {
            paths.insert(path.to_owned());
        }
        if row[..2].iter().any(|value| matches!(value, b'R' | b'C')) {
            at += 1;
        }
    }
    Ok(paths.into_iter().collect())
}
fn pointers(ctx: &ContextData, images: &Value, sha: &str, size: u64) -> Result<Value> {
    let slug = ctx.op(
        "origin-slug",
        json!({"url":ctx.git_text(&["remote","get-url","origin"])?}),
    )?;
    let asset = format!("fw-{}.tar.gz", &sha[..16]);
    let mut pointer = json!({"_":"Written by hsm-publish-firmware. The images are fetched, not committed — web/scripts/fetch-firmware.mjs reads this at deploy and /api/firmware serves it.","release":{"tag":TAG,"asset":asset,"url":format!("https://github.com/{}/releases/download/{TAG}/{asset}",slug.as_str().context("origin repository")?)},"source":{"commit":ctx.git_text(&["rev-parse","HEAD"])?},"bundle":{"sha256":sha,"bytes":size,"images":images.as_object().map_or(0,|rows|rows.len())},"images":images});
    let status = ctx.git(&["status", "--porcelain", "-z", "--", "firmware", "tools"])?;
    ensure!(
        status.status.success(),
        "firmware source status could not be read"
    );
    let dirty = dirty_paths(&status.stdout)?;
    if !dirty.is_empty() {
        pointer["unproven"] = json!({"_":"source.commit does not describe these images: an uncommitted path below reaches what built them.","paths":dirty});
    }
    Ok(pointer)
}
fn bundle(ctx: &ContextData, images: &Images, path: &Path) -> Result<String> {
    let rels = images.sources.keys().cloned().collect::<Vec<_>>();
    let expected = images
        .rows
        .as_object()
        .context("image rows")?
        .values()
        .map(|row| {
            Ok((
                row["file"].as_str().context("image filename")?.into(),
                row["sha256"].as_str().context("image hash")?.into(),
            ))
        })
        .collect::<Result<BTreeMap<String, String>>>()?;
    archive::bundle_sources(&ctx.root, &rels, path, &images.sources, &expected)
}
fn upload(
    ctx: &ContextData,
    t: &impl Transport,
    path: &Path,
    asset: &str,
    sha: &str,
    size: u64,
) -> Result<()> {
    let listing = transport::github(t, &["release", "view", TAG, "--json", "assets"])?;
    if listing.status.success() {
        let assets = serde_json::from_slice::<Value>(&listing.stdout)?["assets"].clone();
        let state = ctx.op(
            "release-state",
            json!({"assets":assets,"asset":asset,"digest":sha,"size":size}),
        )?;
        if state["matches"] == true {
            println!("  {asset} is already on the release at the verified size and digest");
            return Ok(());
        }
    } else {
        let made = transport::github(
            t,
            &[
                "release",
                "create",
                TAG,
                "--title",
                "Firmware images",
                "--notes",
                "The images a phone pushes over BLE, fetched at deploy by web/scripts/fetch-firmware.mjs and served from /api/firmware. Each asset is named by its own sha256 and pointed at from firmware/firmware-images.json.",
            ],
        )?;
        ensure!(
            made.status.success(),
            "firmware release creation failed: {}",
            String::from_utf8_lossy(&made.stderr)
        );
    }
    let work = Work::new(&ctx.root)?;
    let staged = work.path.join(asset);
    fs::copy(path, &staged)?;
    let sent = transport::github(
        t,
        &[
            "release",
            "upload",
            TAG,
            &staged.to_string_lossy(),
            "--clobber",
        ],
    )?;
    ensure!(
        sent.status.success(),
        "firmware release upload failed: {}",
        String::from_utf8_lossy(&sent.stderr)
    );
    println!("  uploaded {asset}");
    Ok(())
}
fn check(ctx: &ContextData, targets: &[Target]) -> Result<i32> {
    let held = read_json(ctx.root.join(POINTERS)).unwrap_or_else(|_| empty());
    let images = collect(ctx, targets, None)?;
    let mut gaps = Vec::new();
    for (target, row) in images.rows.as_object().context("image rows")? {
        if held["images"][target].is_null() {
            gaps.push(format!(
                "{target} — built here, absent from the pointer file"
            ));
        } else if held["images"][target]["sha256"] != row["sha256"] {
            gaps.push(format!(
                "{target} — {} is not what the pointer file names",
                row["version"]
                    .as_str()
                    .filter(|v| !v.is_empty())
                    .unwrap_or("art")
            ));
        }
    }
    if gaps.is_empty() {
        println!("{} image(s) at the pointed-at hash", images.sources.len());
        return Ok(0);
    }
    println!(
        "firmware-images.json does not name {} image(s) on this disk:",
        gaps.len()
    );
    for gap in gaps {
        println!("    {gap}");
    }
    println!("    hsm-publish-firmware --write");
    Ok(1)
}
fn show(images: &Value) {
    if let Some(images) = images.as_object() {
        if images.is_empty() {
            println!("no images on this disk — build them, or run with --write");
        }
        for (name, row) in images {
            println!(
                "  {name:<10}  {:>9} B  crc32 {:#010x}  {}",
                row["bytes"].as_u64().unwrap_or(0),
                row["crc32"].as_u64().unwrap_or(0),
                row["version"]
                    .as_str()
                    .filter(|v| !v.is_empty())
                    .unwrap_or("—")
            );
        }
    }
}
fn run_with(ctx: &ContextData, t: &impl Transport, args: Args, programs: &Programs) -> Result<i32> {
    let targets = selected(&args.targets);
    if args.check {
        return check(ctx, &targets);
    }
    let mut active = ctx.clone();
    if !args.no_build {
        if active.lease.is_none() {
            active.lease = Some(Arc::new(hsm_run_slots::acquire(
                "firmware-publish",
                None,
                false,
            )?));
        }
        for &target in &targets {
            println!("building {} ({})", target.name, target.environment);
            build(&active, target, programs)?;
        }
    }
    if !args.write {
        show(&collect(&active, &targets, None)?.rows);
        return Ok(0);
    }
    let work = Work::new(&active.root)?;
    let images = collect(&active, &targets, Some(&work.path.join("images")))?;
    show(&images.rows);
    if images.sources.is_empty() {
        return Ok(1);
    }
    let missing = targets
        .iter()
        .filter(|target| images.rows.get(target.name).is_none())
        .map(|target| target.name)
        .collect::<Vec<_>>();
    ensure!(
        missing.is_empty(),
        "Missing requested images: {}; firmware release unchanged",
        missing.join(", ")
    );
    let path = work.path.join("firmware.tar.gz");
    let sha = bundle(&active, &images, &path)?;
    let size = path.metadata()?.len();
    let pointer = pointers(&active, &images.rows, &sha, size)?;
    let asset = pointer["release"]["asset"]
        .as_str()
        .context("firmware release asset")?;
    upload(&active, t, &path, asset, &sha, size)?;
    fs::write(
        active.root.join(POINTERS),
        serde_json::to_string_pretty(&pointer)? + "\n",
    )?;
    println!(
        "pointed at {POINTERS} — {asset} ({:.1} MB)",
        size as f64 / 1e6
    );
    Ok(0)
}
pub fn run(ctx: &ContextData, args: &[String]) -> Result<i32> {
    let args = match Args::try_parse_from(
        std::iter::once("hsm-publish-firmware".into()).chain(args.iter().cloned()),
    ) {
        Ok(args) => args,
        Err(error) => {
            let status = error.exit_code();
            error.print()?;
            return Ok(status);
        }
    };
    run_with(
        ctx,
        &transport::Live { context: ctx },
        args,
        &Programs::load(),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        os::unix::{fs::PermissionsExt, process::ExitStatusExt},
        process::Output,
        sync::Mutex,
    };
    struct Fixture {
        work: Work,
        ctx: ContextData,
    }
    impl Fixture {
        fn new() -> Result<Self> {
            let parent = Path::new(env!("CARGO_MANIFEST_DIR"))
                .ancestors()
                .nth(3)
                .unwrap();
            let work = Work::new(parent)?;
            let ctx = ContextData::with_config(&work.path, empty(), empty())?;
            fs::create_dir_all(ctx.root.join("firmware"))?;
            ctx.git_text(&["init", "--quiet"])?;
            for (name, value) in [
                ("user.name", "Firmware fixture"),
                ("user.email", "firmware@example.invalid"),
                ("commit.gpgSign", "false"),
                ("core.hooksPath", "/dev/null"),
            ] {
                ctx.git_text(&["config", name, value])?;
            }
            ctx.git_text(&[
                "remote",
                "add",
                "origin",
                "https://github.com/example/firmware-fixture.git",
            ])?;
            ctx.git_text(&["commit", "--allow-empty", "--quiet", "-m", "fixture"])?;
            Ok(Self { work, ctx })
        }
        fn image(&self, target: Target, bytes: &[u8]) -> Result<()> {
            let path = image_path(&self.ctx.root, target);
            fs::create_dir_all(path.parent().unwrap())?;
            fs::write(path, bytes)?;
            Ok(())
        }
        fn header(&self, target: Target) -> Result<()> {
            let path = self
                .ctx
                .root
                .join("firmware")
                .join(target.source)
                .join("fw_version.h");
            fs::create_dir_all(path.parent().unwrap())?;
            fs::write(
                path,
                "#define FW_VERSION \"2026.11.10 abcdef+\"\n#define FW_BUILD_EPOCH 1794344344u\n",
            )?;
            Ok(())
        }
    }
    #[derive(Default)]
    struct Fake {
        events: Mutex<Vec<Vec<String>>>,
        assets: Value,
        exists: bool,
        success: bool,
    }
    fn result(ok: bool, bytes: Vec<u8>) -> Output {
        Output {
            status: std::process::ExitStatus::from_raw(if ok { 0 } else { 256 }),
            stdout: bytes,
            stderr: vec![],
        }
    }
    impl Transport for Fake {
        fn head(&self, _: &str) -> bool {
            panic!("firmware uses release assets")
        }
        fn put(&self, _: &str, _: &Path) -> bool {
            panic!("firmware uses release assets")
        }
        fn download(&self, _: &str, _: &Path) -> Result<()> {
            panic!("fixture does not download")
        }
        fn refresh(&self) -> Result<()> {
            panic!("firmware publication leaves site deployment to its committed pointer")
        }
        fn github(&self, args: &[String]) -> Result<Output> {
            self.events.lock().unwrap().push(args.to_vec());
            if args.get(1).is_some_and(|value| value == "view") {
                Ok(result(
                    self.exists,
                    serde_json::to_vec(&json!({"assets":self.assets}))?,
                ))
            } else {
                Ok(result(self.success, vec![]))
            }
        }
    }
    fn programs(path: &Path) -> Programs {
        Programs {
            pio: path.into(),
            marketing: path.into(),
        }
    }
    fn members(path: &Path) -> Result<BTreeMap<String, Vec<u8>>> {
        let bytes = archive::decompress(&fs::read(path)?)?;
        let mut at = 0;
        let mut found = BTreeMap::new();
        while at + 512 <= bytes.len() && bytes[at..at + 512].iter().any(|value| *value != 0) {
            let header = &bytes[at..at + 512];
            let name = String::from_utf8(
                header[..100]
                    .iter()
                    .copied()
                    .take_while(|value| *value != 0)
                    .collect(),
            )?;
            let size = usize::from_str_radix(
                std::str::from_utf8(&header[124..136])?.trim_matches(['\0', ' ']),
                8,
            )?;
            let start = at + 512;
            found.insert(name, bytes[start..start + size].to_vec());
            at = start + size.div_ceil(512) * 512;
        }
        Ok(found)
    }

    #[test]
    fn versions_crc_and_phone_target_selection() {
        assert_eq!(crc32(b"123456789"), 0xcbf43926);
        let header = "#define FW_VERSION \"date sha+\"\n#define FW_BUILD_EPOCH 123u\n";
        assert_eq!(version(header), Some("date sha+".into()));
        assert_eq!(epoch(header), Some(123));
        assert_eq!(epoch(""), None);
        assert!(Args::try_parse_from(["fw", "pcba_bench"]).is_err());
        assert_eq!(
            selected(&["faucet".into()])[0].environment,
            "esp32s3_faucet"
        );
        let mut art = vec![0; 20];
        art[16..20].copy_from_slice(&0x12345678u32.to_le_bytes());
        let meta = metadata(TARGETS[1], &art, header);
        assert!(meta["version"].is_null() && meta["build_epoch"].is_null());
        assert_eq!(meta["art_crc32"], 0x12345678u32);
    }
    #[test]
    fn frozen_images_pack_deterministically_and_keep_their_identities() -> Result<()> {
        let fixture = Fixture::new()?;
        fixture.image(TARGETS[0], b"appliance bytes")?;
        fixture.header(TARGETS[0])?;
        let mut art = vec![0; 32];
        art[16..20].copy_from_slice(&0x87654321u32.to_le_bytes());
        fixture.image(TARGETS[1], &art)?;
        let images = collect(
            &fixture.ctx,
            &TARGETS[..2],
            Some(&fixture.work.path.join("frozen")),
        )?;
        fixture.image(TARGETS[0], b"later checkpoint")?;
        let a = fixture.work.path.join("a.gz");
        let b = fixture.work.path.join("b.gz");
        let sha = bundle(&fixture.ctx, &images, &a)?;
        assert_eq!(bundle(&fixture.ctx, &images, &b)?, sha);
        let packed = members(&a)?;
        assert_eq!(packed["appliance.bin"], b"appliance bytes");
        assert_eq!(packed["art.bin"], art);
        let pointers = pointers(&fixture.ctx, &images.rows, &sha, a.metadata()?.len())?;
        assert_eq!(
            pointers["images"]["appliance"]["sha256"],
            digest(&packed["appliance.bin"])
        );
        assert_eq!(
            pointers["images"]["art"]["crc32"],
            crc32(&packed["art.bin"])
        );
        assert_eq!(pointers["release"]["tag"], TAG);
        Ok(())
    }
    #[test]
    fn failed_build_and_upload_leave_firmware_pointers_unchanged() -> Result<()> {
        let fixture = Fixture::new()?;
        fixture.image(TARGETS[0], b"earlier image")?;
        let pointer = fixture.ctx.root.join(POINTERS);
        fs::write(&pointer, b"preceding pointer")?;
        let script = fixture.work.path.join("failed-builder");
        fs::write(&script, "#!/bin/sh\nexit 1\n")?;
        fs::set_permissions(&script, fs::Permissions::from_mode(0o755))?;
        let fake = Fake {
            exists: true,
            success: true,
            ..Default::default()
        };
        let options = Args {
            write: true,
            targets: vec!["appliance".into()],
            ..Default::default()
        };
        assert!(run_with(&fixture.ctx, &fake, options, &programs(&script)).is_err());
        assert!(fake.events.lock().unwrap().is_empty());
        assert_eq!(fs::read(&pointer)?, b"preceding pointer");
        let fake = Fake {
            exists: true,
            success: false,
            ..Default::default()
        };
        let options = Args {
            write: true,
            no_build: true,
            targets: vec!["appliance".into()],
            ..Default::default()
        };
        assert!(
            run_with(
                &fixture.ctx,
                &fake,
                options,
                &programs(Path::new("/not-called"))
            )
            .is_err()
        );
        assert_eq!(fs::read(pointer)?, b"preceding pointer");
        Ok(())
    }
    #[test]
    fn verified_release_skips_upload_and_empty_release_is_not_recreated() -> Result<()> {
        let fixture = Fixture::new()?;
        let file = fixture.work.path.join("bundle");
        fs::write(&file, b"bytes")?;
        let fake = Fake {
            exists: true,
            success: true,
            assets: json!([{"name":"fw-a.tar.gz","state":"uploaded","size":5,"digest":"sha256:a"}]),
            ..Default::default()
        };
        upload(&fixture.ctx, &fake, &file, "fw-a.tar.gz", "a", 5)?;
        assert_eq!(fake.events.lock().unwrap().len(), 1);
        let fake = Fake {
            exists: true,
            success: true,
            assets: json!([]),
            ..Default::default()
        };
        upload(&fixture.ctx, &fake, &file, "fw-a.tar.gz", "a", 5)?;
        let events = fake.events.lock().unwrap();
        assert!(events.iter().all(|row| row[1] != "create"));
        assert!(events.iter().any(|row| row[1] == "upload" && row[2] == TAG));
        Ok(())
    }
    #[test]
    fn selected_missing_images_and_read_only_check_start_no_publication() -> Result<()> {
        let fixture = Fixture::new()?;
        fixture.image(TARGETS[0], b"image")?;
        let fake = Fake::default();
        let options = Args {
            write: true,
            no_build: true,
            ..Default::default()
        };
        assert!(
            run_with(
                &fixture.ctx,
                &fake,
                options,
                &programs(Path::new("/not-called"))
            )
            .is_err()
        );
        assert!(fake.events.lock().unwrap().is_empty());
        let options = Args {
            check: true,
            targets: vec!["faucet".into()],
            ..Default::default()
        };
        assert_eq!(
            run_with(
                &fixture.ctx,
                &fake,
                options,
                &programs(Path::new("/not-called"))
            )?,
            0
        );
        assert!(fake.events.lock().unwrap().is_empty());
        assert_eq!(
            dirty_paths(b" M firmware/a.cpp\0R  tools/new.rs\0tools/old.rs\0?? tools/study/\0")?,
            ["firmware/a.cpp", "tools/new.rs"]
        );
        Ok(())
    }
    #[test]
    #[ignore = "reads only existing local display images and packs a private fixture bundle"]
    fn existing_display_images_pack_without_build_or_upload() -> Result<()> {
        let root = Path::new(env!("CARGO_MANIFEST_DIR"))
            .ancestors()
            .nth(3)
            .unwrap();
        let ctx = ContextData::load(root)?;
        let work = Work::new(root)?;
        let targets = selected(&["art".into(), "enclosure".into()]);
        ensure!(
            targets
                .iter()
                .all(|target| image_path(root, *target).is_file()),
            "existing display images are absent"
        );
        let images = collect(&ctx, &targets, Some(&work.path.join("images")))?;
        let path = work.path.join("fixture.tar.gz");
        let sha = bundle(&ctx, &images, &path)?;
        let members = members(&path)?;
        for (target, row) in images.rows.as_object().unwrap() {
            let bytes = &members[row["file"].as_str().unwrap()];
            assert_eq!(row["sha256"], digest(bytes));
            assert_eq!(row["crc32"], crc32(bytes));
            println!("{target}: {} bytes sha256 {}", bytes.len(), row["sha256"]);
        }
        println!(
            "local firmware fixture: {} bytes sha256 {sha}",
            path.metadata()?.len()
        );
        Ok(())
    }
}
