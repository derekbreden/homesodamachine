//! Authored HTML leaves supply the editable pages of the manual illustrated books.
use anyhow::{Context, Result, bail, ensure};
use hsm_pages::{Page, Rgb, RgbaImage};
use serde::Deserialize;
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::sync::Arc;
use std::time::{Duration, Instant};

pub const CANVAS: [u32; 2] = [2550, 3300];
pub const COVER: [u32; 2] = [800, 1035];
const RENDER_TIMEOUT: Duration = Duration::from_secs(1800);

pub struct Spec {
    pub id: &'static str,
    pub title: &'static str,
    pub subtitle: &'static str,
    pub contents_links: bool,
    pub delivery_copy: bool,
    pub sources: &'static [&'static str],
}

pub const SPECS: &[Spec] = &[
    Spec {
        id: "tube-insertion-guide",
        title: "Tube insertion jig build guide",
        subtitle: "Shop guide - build and use the tube insertion jig",
        contents_links: false,
        delivery_copy: true,
        sources: &[
            "hardware/printed-parts/fixtures/tube-insertion/README.md",
            "hardware/printed-parts/fixtures/tube-insertion/load-basis.md",
            "hardware/printed-parts/fixtures/tube-insertion/physical-acceptance.json",
            "hardware/printed-parts/fixtures/tube-insertion/parts.json",
            "hardware/printed-parts/fixtures/tube-insertion/print-layout.json",
            "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",
            "hardware/printed-parts/faucet/lever-replica/assembly-observations.json",
            "hardware/assembly/faucet-and-umbilical.md",
            "tools/tube-insertion-guide/art.rs",
            "tools/assembly-guides/artwork.rs",
            "hardware/printed-parts/fixtures/tube-insertion/tube_insertion.rs",
            "hardware/printed-parts/fixtures/tube-insertion/numbers.rs",
            "hardware/reference/touch-flo-faucet/westbrass-reference/numbers.rs",
        ],
    },
    Spec {
        id: "weld-rotator-guide",
        title: "Weld rotator build guide",
        subtitle: "Shop guide - build the bench rotator",
        contents_links: false,
        delivery_copy: false,
        sources: &["hardware/assembly/weld-rotation-rig.md"],
    },
    Spec {
        id: "reed-sweep-rig-guide",
        title: "Reed sweep rig build guide",
        subtitle: "Shop guide - print, assemble and set up the float calibration fixture",
        contents_links: false,
        delivery_copy: false,
        sources: &[
            "firmware/src_reed_rig/README.md",
            "firmware/src_reed_rig/main.cpp",
            "hardware/assembly/reed-sweep-rig.md",
            "hardware/printed-parts/fixtures/reed-sweep-rig/README.md",
            "hardware/printed-parts/fixtures/reed-sweep-rig/numbers.rs",
            "hardware/printed-parts/fixtures/reed-sweep-rig/reed_sweep_rig.rs",
            "hardware/printed-parts/fixtures/reed-sweep-rig/reed-sweep-rig-datums.json",
            "hardware/printed-parts/fixtures/reed-sweep-rig/print-layout.json",
            "hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md",
            "hardware/weld-rotator-guide/style.css",
            "ios/AppIcon.svg",
            "tools/hsm/peripheral/src/reed.rs",
        ],
    },
    Spec {
        id: "magnetic-float-guide",
        title: "ASA Aero magnetic float build guide",
        subtitle: "Shop guide - one-piece ASA Aero float and paused RC62 insertion",
        contents_links: false,
        delivery_copy: false,
        sources: &[
            "hardware/printed-parts/cold-core/magnetic-float/all-aero/design.json",
            "hardware/printed-parts/cold-core/magnetic-float/all-aero/physical-observations.json",
            "hardware/printed-parts/cold-core/magnetic-float/all-aero/integration-check.json",
            "hardware/printed-parts/cold-core/magnetic-float/all-aero/installation.md",
            "tools/magnetic-float-guide/build-recipe-sources.json",
        ],
    },
    Spec {
        id: "carbonator-filming-guide",
        title: "Carbonator weld filming guide",
        subtitle: "Hands-only filming - shots, camera setup and timing",
        contents_links: true,
        delivery_copy: true,
        sources: &[
            "marketing/video/carbonator-weld-shooting-plan.md",
            "hardware/assembly/weld-rotation-rig.md",
            "hardware/assembly/pressure-vessel.md",
        ],
    },
    Spec {
        id: "fdm-print-guide",
        title: "FDM print guide",
        subtitle: "Printing the Home Soda Machine",
        contents_links: false,
        delivery_copy: true,
        sources: &[
            "AGENTS.md",
            "hardware/printed-parts/AGENTS.md",
            "hardware/printed-parts/enclosure/enclosure/README.md",
            "hardware/printed-parts/enclosure/trial-preparation/README.md",
            "hardware/printed-parts/cooling/README.md",
            "tools/bambu-printers.md",
        ],
    },
    Spec {
        id: "printing-the-machine",
        title: "Printing the Machine",
        subtitle: "FDM lessons from printing the Home Soda Machine, by plastic",
        contents_links: false,
        delivery_copy: false,
        sources: &[],
    },
];

pub fn leaves(guide: &Path) -> Result<Vec<PathBuf>> {
    let mut found = Vec::new();
    for entry in std::fs::read_dir(guide)? {
        let path = entry?.path();
        let Some(name) = path.file_name().and_then(|n| n.to_str()) else {
            continue;
        };
        let bytes = name.as_bytes();
        if path.is_file()
            && bytes.len() > 3
            && bytes[0].is_ascii_digit()
            && bytes[1].is_ascii_digit()
            && bytes[2] == b'-'
            && name.ends_with(".html")
        {
            found.push(path);
        }
    }
    found.sort();
    ensure!(
        !found.is_empty(),
        "no authored leaves under {}",
        guide.display()
    );
    for (i, path) in found.iter().enumerate() {
        ensure!(
            path.file_name().unwrap().to_string_lossy()[..2].parse::<usize>()? == i + 1,
            "guide leaves are not consecutively numbered: {}",
            path.display()
        );
    }
    Ok(found)
}

fn stem(path: &Path) -> Result<&str> {
    path.file_stem()
        .and_then(|v| v.to_str())
        .context("HTML leaf stem")
}

fn title(path: &Path) -> Result<String> {
    let html = std::fs::read_to_string(path)?;
    if let Some((_, rest)) = html.split_once("<title>") {
        if let Some((title, _)) = rest.split_once("</title>") {
            return Ok(title
                .replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">"));
        }
    }
    Ok(stem(path)?[3..].replace('-', " "))
}

fn run_renderer(
    root: &Path,
    guide: &Path,
    out: &Path,
    pages: &[PathBuf],
    selected: &[usize],
) -> Result<()> {
    let mut calls = Vec::new();
    if selected.is_empty() {
        calls.push(vec![
            "--batch".into(),
            guide.as_os_str().to_owned(),
            out.as_os_str().to_owned(),
        ]);
    } else {
        for &number in selected {
            let page = pages
                .get(
                    number
                        .checked_sub(1)
                        .context("page numbering starts at the cover")?,
                )
                .context("page outside guide")?;
            calls.push(vec![
                page.as_os_str().to_owned(),
                out.join(format!("{}.png", stem(page)?)).into_os_string(),
            ]);
        }
    }
    for args in calls {
        let mut child = Command::new("node")
            .arg(root.join("tools/render/render-card.js"))
            .args(args)
            .args([
                "--size",
                "2550x3300",
                "--dpr",
                "1",
                "--pdf",
                "8.5x11in",
                "--page-timeout",
                "180000",
            ])
            .spawn()
            .context("start the HTML guide renderer")?;
        let start = Instant::now();
        loop {
            if let Some(status) = child.try_wait()? {
                ensure!(status.success(), "HTML renderer exited with {status}");
                break;
            }
            if start.elapsed() > RENDER_TIMEOUT {
                child.kill()?;
                child.wait()?;
                bail!("HTML guide rendering exceeded its deadline");
            }
            std::thread::sleep(Duration::from_millis(100));
        }
    }
    Ok(())
}

pub fn cover(source: &Path, target: &Path) -> Result<()> {
    let image = RgbaImage::read_png(&std::fs::read(source)?)?.flatten(Rgb::WHITE);
    let mut page = Page::default();
    page.picture(Arc::new(image), [0., 0.], [612., 792.]);
    let mut pixmap = tiny_skia::Pixmap::new(COVER[0], COVER[1]).context("guide cover canvas")?;
    pixmap.fill(tiny_skia::Color::WHITE);
    hsm_pages::raster::draw(
        &mut pixmap,
        &page,
        hsm_pages::raster::fit([612., 792.], COVER[0], 0),
    );
    crate::write(target, &hsm_pages::RgbImage::from_pixmap(&pixmap).png()?)
}

#[derive(Deserialize)]
struct FloatInputs {
    current_cad_revision: String,
    pages: Vec<String>,
}
#[derive(Deserialize)]
struct ArtScene {
    file: String,
    sha256: String,
}
#[derive(Deserialize)]
struct FloatArt {
    cad_revision: String,
    dimensions_mm: BTreeMap<String, f64>,
    scenes: BTreeMap<String, ArtScene>,
}

fn validate_float(root: &Path, guide: &Path, pages: &[PathBuf]) -> Result<()> {
    let inputs: FloatInputs =
        serde_json::from_slice(&std::fs::read(guide.join("guide-inputs.json"))?)?;
    let art: FloatArt = serde_json::from_slice(&std::fs::read(guide.join("art/manifest.json"))?)?;
    let design: Value = serde_json::from_slice(&std::fs::read(
        root.join("hardware/printed-parts/cold-core/magnetic-float/all-aero/design.json"),
    )?)?;
    let actual: Vec<_> = pages
        .iter()
        .map(|p| p.file_name().unwrap().to_string_lossy().into_owned())
        .collect();
    ensure!(
        inputs.pages == actual,
        "float guide leaves differ from their authored input record"
    );
    ensure!(
        inputs.current_cad_revision == art.cad_revision
            && design["cad_revision"].as_str() == Some(art.cad_revision.as_str()),
        "float guide text and artwork use different geometry revisions"
    );
    for (art_key, design_key) in [
        ("diameter", "diameter"),
        ("height", "height"),
        ("guide_bore", "guide_bore"),
        ("pocket_depth", "pocket_depth"),
        ("magnet_center_z", "magnet_midplane"),
    ] {
        let a = art
            .dimensions_mm
            .get(art_key)
            .context("float artwork dimension")?;
        let b = design["dimensions_mm"][design_key]
            .as_f64()
            .context("current float dimension")?;
        ensure!(
            (a - b).abs() < 1e-9,
            "float artwork differs from current {design_key}"
        );
    }
    for scene in art.scenes.values() {
        ensure!(
            crate::sha(&guide.join("art").join(&scene.file))? == scene.sha256,
            "float artwork changed: {}",
            scene.file
        );
    }
    Ok(())
}

fn source_paths(
    root: &Path,
    guide: &Path,
    spec: &Spec,
    pages: &[PathBuf],
) -> Result<BTreeSet<PathBuf>> {
    let mut paths: BTreeSet<_> = pages.iter().cloned().collect();
    for name in [
        "style.css",
        "README.md",
        "guide-inputs.json",
        "art/manifest.json",
    ] {
        let path = guide.join(name);
        if path.is_file() {
            paths.insert(path);
        }
    }
    let art = guide.join("art");
    if art.is_dir() {
        for entry in std::fs::read_dir(art)? {
            let path = entry?.path();
            if path.is_file() {
                paths.insert(path);
            }
        }
    }
    for path in spec.sources {
        let path = root.join(path);
        if path.is_file() {
            paths.insert(path);
        }
    }
    if guide.join("guide-inputs.json").is_file() {
        for input in print_guide_inputs(guide)?.into_values() {
            if input.revision.is_none() {
                paths.insert(root.join(input.path));
            }
        }
    }
    for source in [
        "src/lib.rs",
        "src/main.rs",
        "src/html.rs",
        "src/pdf.rs",
        "Cargo.toml",
    ] {
        paths.insert(root.join("tools/hsm/manual-guides").join(source));
    }
    if spec.id == "magnetic-float-guide" {
        paths.insert(root.join("tools/hsm/manual-guides/src/float.rs"));
    }
    Ok(paths)
}

#[derive(Deserialize)]
struct SettingSource {
    path: String,
    revision: Option<String>,
    member: Option<String>,
}

fn print_guide_inputs(guide: &Path) -> Result<BTreeMap<String, SettingSource>> {
    let path = guide.join("guide-inputs.json");
    Ok(serde_json::from_slice(&std::fs::read(path)?)?)
}

// Resolve the guide's displayed values from the selected recipes and slice records.
fn print_guide_leaves(root: &Path, guide: &Path, out: &Path, pages: &[PathBuf]) -> Result<PathBuf> {
    let mut settings = BTreeMap::new();
    for (name, input) in print_guide_inputs(guide)? {
        let bytes = if let Some(revision) = input.revision {
            let read = Command::new("git")
                .args(["show", &format!("{revision}:{}", input.path)])
                .current_dir(root)
                .output()?;
            ensure!(
                read.status.success(),
                "cannot read {revision}:{}",
                input.path
            );
            read.stdout
        } else if let Some(member) = input.member {
            let read = Command::new("unzip")
                .arg("-p")
                .arg(root.join(&input.path))
                .arg(&member)
                .output()?;
            ensure!(
                read.status.success(),
                "cannot read {member} in {}",
                input.path
            );
            read.stdout
        } else {
            std::fs::read(root.join(&input.path))?
        };
        let source: Value = serde_json::from_slice(&bytes).with_context(|| input.path.clone())?;
        settings.insert(name, source);
    }
    let staged = out.join("source");
    if staged.is_dir() {
        std::fs::remove_dir_all(&staged)?;
    }
    let escape = |s: &str| {
        s.replace('&', "&amp;")
            .replace('"', "&quot;")
            .replace('<', "&lt;")
            .replace('>', "&gt;")
    };
    let base = escape(
        &guide
            .to_string_lossy()
            .replace('%', "%25")
            .replace('#', "%23")
            .replace('?', "%3F"),
    );
    for page in pages {
        let html = std::fs::read_to_string(page)?;
        let html = html.replacen(
            "<head>",
            &format!("<head>\n  <base href=\"file://{base}/\">"),
            1,
        );
        let mut remaining = html.as_str();
        let mut rendered = String::new();
        while let Some((before, rest)) = remaining.split_once("{{") {
            let (key, after) = rest.split_once("}}").context("unclosed guide setting")?;
            let (source, pointer) = key
                .split_once(':')
                .context("expected source:JSON pointer")?;
            let value = settings
                .get(source)
                .and_then(|data| data.pointer(pointer))
                .with_context(|| format!("{} has no setting {key}", page.display()))?;
            rendered.push_str(before);
            match value {
                Value::String(s) => rendered.push_str(&escape(s)),
                Value::Number(n) => rendered.push_str(&n.to_string()),
                _ => bail!("guide setting {key} must be a string or number"),
            }
            remaining = after;
        }
        rendered.push_str(remaining);
        crate::write(
            &staged.join(page.file_name().context("guide leaf name")?),
            rendered.as_bytes(),
        )?;
    }
    Ok(staged)
}

pub fn bind(
    root: &Path,
    name: &str,
    output: Option<&Path>,
    reuse: bool,
    selected: &[usize],
) -> Result<()> {
    let spec = SPECS
        .iter()
        .find(|s| s.id == name)
        .with_context(|| format!("unknown HTML guide {name}"))?;
    let guide = root.join("hardware").join(spec.id);
    let pages = leaves(&guide)?;
    if name == "magnetic-float-guide" {
        validate_float(root, &guide, &pages)?;
    }
    let dest = output.unwrap_or(&guide);
    let out = if output.is_some() {
        dest.join("leaves")
    } else {
        guide.join("out")
    };
    std::fs::create_dir_all(&out)?;
    if !reuse {
        for (i, page) in pages.iter().enumerate() {
            if !selected.is_empty() && !selected.contains(&(i + 1)) {
                continue;
            }
            for ext in ["png", "pdf"] {
                let path = out.join(format!("{}.{ext}", stem(page)?));
                if path.is_file() {
                    std::fs::remove_file(path)?;
                }
            }
        }
        if guide.join("guide-inputs.json").is_file() {
            let staged = print_guide_leaves(root, &guide, &out, &pages)?;
            run_renderer(root, &staged, &out, &leaves(&staged)?, selected)?;
        } else {
            run_renderer(root, &guide, &out, &pages, selected)?;
        }
    }
    let leaves = pages
        .iter()
        .map(|p| Ok((out.join(format!("{}.pdf", stem(p)?)), title(p)?)))
        .collect::<Result<Vec<_>>>()?;
    for (path, _) in &leaves {
        ensure!(path.is_file(), "missing rendered leaf {}", path.display());
    }
    let pdf = dest.join(format!("{}.pdf", spec.id));
    crate::pdf::merge(&leaves, spec.title, spec.contents_links, &pdf)?;
    let cover_name = format!("{}.cover.png", spec.id);
    cover(
        &out.join(format!("{}.png", stem(&pages[0])?)),
        &dest.join(&cover_name),
    )?;
    let subtitle = if name == "carbonator-filming-guide" {
        format!(
            "Hands-only filming - {} shots, camera setup and timing, {} Letter pages",
            pages
                .iter()
                .filter(|p| p.file_name().unwrap().to_string_lossy().contains("-shot-"))
                .count(),
            pages.len()
        )
    } else {
        format!(
            "{}, {} pages, 8.5 x 11 in, single sided",
            spec.subtitle,
            pages.len()
        )
    };
    crate::write_json(
        &pdf.with_extension("pdf.json"),
        &json!({"title":spec.title,"subtitle":subtitle,"pages":pages.len(),"cover":cover_name,"cover_size":COVER}),
    )?;
    let mut sources = BTreeMap::new();
    for path in source_paths(root, &guide, spec, &pages)? {
        sources.insert(
            path.strip_prefix(root)?.to_string_lossy().into_owned(),
            crate::sha(&path)?,
        );
    }
    let receipt = json!({"purpose":"Record the authored inputs of this manual guide edition.","pdf":pdf.file_name().unwrap().to_string_lossy(),"pages":pages.len(),"page_inches":[8.5,11],"print_layout":{"canvas_px":CANVAS,"dpi":300,"print_scaling":"100% / none","sides":"single sided"},"source_sha256":sources,"pdf_sha256":crate::sha(&pdf)?});
    let delivery = if output.is_some() || !spec.delivery_copy {
        pdf.clone()
    } else {
        root.join("output/pdf").join(pdf.file_name().unwrap())
    };
    if delivery != pdf {
        crate::write(&delivery, &std::fs::read(&pdf)?)?;
    }
    crate::write_json(&delivery.with_extension("sources.json"), &receipt)?;
    println!("{}: {} pages", pdf.display(), pages.len());
    Ok(())
}
