//! Plate layout and settings travel as text. Meshes, triangle paint and previews travel by hash.

use anyhow::{bail, ensure, Context, Result};
use hsm_print_prep::{plate_picture, profile::{settings_bytes, SETTINGS_MEMBER}, slice};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::Path;
use std::process::Command;
use zip::{write::SimpleFileOptions, ZipArchive, ZipWriter};

const ASSET_KEY: &str = "geometry_asset_sha256";
const MODEL: &str = "3D/3dmodel.model";
/// Where the Parts page's plate pictures are served from, in the checkout.
const PLATE_PICTURES: &str = "web/public/parts/plates";
type Recipe = BTreeMap<String, Value>;

fn asset_digest(path: &Path) -> Result<String> {
    let mut hash = Sha256::new();
    io::copy(&mut File::open(path).with_context(|| format!("opening {}", path.display()))?, &mut hash)?;
    Ok(format!("{:x}", hash.finalize()))
}

fn write_new(path: &Path, write: impl FnOnce(File) -> Result<()>) -> Result<()> {
    let file = File::create_new(path).with_context(|| format!("creating {}", path.display()))?;
    let result = write(file);
    if result.is_err() {
        let _ = fs::remove_file(path);
    }
    result
}

fn as_text(name: &str, size: u64) -> bool {
    name == MODEL && size <= 1024 * 1024
        || Path::new(name).extension().and_then(|s| s.to_str())
            .is_some_and(|ext| matches!(ext, "xml" | "rels" | "json" | "config" | "txt"))
}

fn capture(input: &Path, output: &Path, assets: Option<&Path>) -> Result<()> {
    let mut package = ZipArchive::new(File::open(input)?)?;
    let mut recipe = Recipe::new();
    let mut geometry = Vec::new();
    let mut editable = false;
    for index in 0..package.len() {
        let mut entry = package.by_index(index)?;
        let name = entry.name()?.to_string();
        editable |= name == MODEL;
        if name.ends_with('/') {
            continue;
        }
        if assets.is_some() {
            ensure!(!name.ends_with(".gcode"), "capture needs the editable plate before slicing");
        } else if name != SETTINGS_MEMBER
            && !(name.starts_with("Metadata/filament_settings_") && name.ends_with(".config"))
        {
            continue;
        }
        if as_text(&name, entry.size()) {
            let mut text = String::new();
            entry.read_to_string(&mut text).with_context(|| format!("reading {name}"))?;
            if name == MODEL && text.contains("<mesh") {
                geometry.push(index);
                continue;
            }
            let value = match serde_json::from_str(&text) {
                Ok(value @ Value::Object(_)) => value,
                _ => Value::String(text),
            };
            ensure!(recipe.insert(name.clone(), value).is_none(), "duplicate {name}");
        } else {
            geometry.push(index);
        }
    }
    ensure!(recipe.get(SETTINGS_MEMBER).is_some_and(Value::is_object), "no Bambu Studio project settings");
    if let Some(assets) = assets {
        ensure!(editable, "no editable model in {}", input.display());
        if !geometry.is_empty() {
            fs::create_dir_all(assets)?;
            let staging = assets.join(format!("plate-recipe-{}.tmp", std::process::id()));
            write_new(&staging, |file| {
                let mut payload = ZipWriter::new(file);
                for index in geometry {
                    payload.raw_copy_file(package.by_index_raw(index)?)?;
                }
                payload.finish()?;
                Ok(())
            })?;
            let digest = asset_digest(&staging)?;
            let target = assets.join(format!("{digest}.zip"));
            fs::rename(staging, &target)?;
            println!("{}", target.display());
            recipe.insert(ASSET_KEY.into(), Value::String(digest));
        }
    }
    write_new(output, |mut file| {
        serde_json::to_writer_pretty(&mut file, &recipe)?;
        writeln!(file)?;
        Ok(())
    })
}

fn build(input: &Path, output: &Path, assets: &Path) -> Result<()> {
    let mut recipe: Recipe = serde_json::from_reader(io::BufReader::new(File::open(input)?))?;
    let payload = if let Some(value) = recipe.remove(ASSET_KEY) {
        let digest = value.as_str().context("geometry asset needs a SHA-256 digest")?;
        ensure!(digest.len() == 64 && digest.bytes().all(|byte| byte.is_ascii_hexdigit()), "invalid geometry digest");
        let path = assets.join(format!("{digest}.zip"));
        ensure!(asset_digest(&path)? == digest, "{} has the wrong digest", path.display());
        Some(ZipArchive::new(File::open(path)?)?)
    } else {
        None
    };
    ensure!(recipe.contains_key(SETTINGS_MEMBER), "no Bambu Studio project settings");
    ensure!(
        recipe.contains_key(MODEL) || payload.as_ref().is_some_and(|zip| zip.file_names().any(|name| name.as_deref().is_ok_and(|name| name == MODEL))),
        "no editable model"
    );
    write_new(output, |file| {
        let mut project = ZipWriter::new(file);
        let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated);
        for (name, value) in &recipe {
            let contents = match value {
                Value::Object(_) => settings_bytes(value)?,
                Value::String(text) => text.as_bytes().to_vec(),
                _ => bail!("{name} needs text or JSON settings"),
            };
            project.start_file(name, options)?;
            project.write_all(&contents)?;
        }
        if let Some(mut asset) = payload {
            for index in 0..asset.len() {
                let entry = asset.by_index_raw(index)?;
                let name = entry.name()?;
                ensure!(!recipe.contains_key::<str>(name.as_ref()), "duplicate {name}");
                project.raw_copy_file(entry)?;
            }
        }
        project.finish()?;
        Ok(())
    })
}

/// Draws each `ID=PROJECT.3mf[:PLATE]` as the Parts page's picture of plate ID: `hsm render`
/// draws the plate's payload, and the Parts tiles' fitter crops and pads it to a WebP.
fn picture(entries: &[String]) -> Result<()> {
    let root = hsm_print_prep::root();
    let runs = root.join(".cache/runs");
    fs::create_dir_all(&runs)?;
    let scratch = runs.join(format!("plate-pictures-{}", std::process::id()));
    fs::create_dir(&scratch).with_context(|| format!("creating {}", scratch.display()))?;
    let drawn = draw(&root, &scratch, entries);
    let _ = fs::remove_dir_all(&scratch);
    drawn
}

fn draw(root: &Path, scratch: &Path, entries: &[String]) -> Result<()> {
    let pictures = root.join(PLATE_PICTURES);
    let (mut jobs, mut fits) = (Vec::new(), Vec::new());
    for entry in entries {
        let (id, source) = entry.split_once('=').context("expected ID=PROJECT.3mf[:PLATE]")?;
        ensure!(Path::new(id).file_name() == Some(id.as_ref()), "an ID must be a filename stem");
        let (project, plate) = match source.split_once(':') {
            Some((project, plate)) => (project, plate.parse().with_context(|| format!("plate {plate}"))?),
            None => (source, 1),
        };
        let (mesh, png) = (scratch.join(format!("{id}.mesh")), scratch.join(format!("{id}.png")));
        fs::write(&mesh, plate_picture::payload(Path::new(project), plate)?)?;
        jobs.push(plate_picture::job(&mesh, &png));
        fits.extend([png, pictures.join(format!("{id}.webp"))]);
    }
    let manifest = scratch.join("jobs.json");
    fs::write(&manifest, serde_json::to_vec(&jobs)?)?;
    let render = Command::new("hsm").arg("render").arg("--root").arg(root).arg("--jobs").arg(&manifest)
        .current_dir(root).status().context("running hsm render")?;
    ensure!(render.success(), "hsm render failed");
    fs::create_dir_all(&pictures)?;
    let fit = Command::new("node").arg("tools/render/catalog-thumbnail.mjs").args(&fits)
        .current_dir(root).status().context("running node")?;
    ensure!(fit.success(), "fitting the pictures to their Parts tiles failed");
    Ok(())
}

fn main() -> Result<()> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    match args.as_slice() {
        [command, input, output] if command == "profile" => capture(input.as_ref(), output.as_ref(), None),
        [command, input, output, assets] if command == "capture" => {
            capture(input.as_ref(), output.as_ref(), Some(assets.as_ref()))
        }
        [command, input, output, assets] if command == "build" => {
            build(input.as_ref(), output.as_ref(), assets.as_ref())
        }
        [command, input, output] if command == "slice" => {
            let project = Path::new(input);
            let directory = Path::new(output);
            fs::create_dir(directory)?;
            slice::run(Path::new(slice::SLICER), project, directory)?;
            slice::apply_directory(directory, project)?;
            Ok(())
        }
        [command, entries @ ..] if command == "picture" && !entries.is_empty() => picture(entries),
        _ => bail!("usage: plate-recipe profile PROJECT.3mf PROFILE.json\n       plate-recipe capture PROJECT.3mf RECIPE.json ASSET_DIR\n       plate-recipe build RECIPE.json PROJECT.3mf ASSET_DIR\n       plate-recipe slice PROJECT.3mf NEW_DIRECTORY\n       plate-recipe picture ID=PROJECT.3mf[:PLATE]..."),
    }
}
