//! Manual guide pictures draw their current named solids through the installed native renderer.
use anyhow::{Context, Result, ensure};
use hsm_kernel::{Body, Solid, import};
use serde_json::{Value, json};
use std::path::{Path, PathBuf};
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

pub struct Scene {
    pub name: String,
    pub bodies: Vec<crate::tube_fixture::Component>,
    pub camera: [f64; 3],
    pub up: [f64; 3],
    pub size: String,
    pub target: Option<[f64; 3]>,
    pub span: Option<f64>,
}

pub fn read(root: &Path, relative: &str) -> Result<Solid> {
    let path = root.join(relative);
    let model = PathBuf::from(format!("{}.npz", path.display()));
    let pieces = if model.is_file() {
        import::model(model)?
    } else {
        let payload = PathBuf::from(format!("{}.mesh", path.display()));
        if payload.is_file() {
            import::payload(payload)?
        } else if relative.ends_with(".stl") {
            return crate::tube_fixture::stl(&path);
        } else {
            import::step(path)?
        }
    };
    ensure!(!pieces.is_empty(), "guide component is empty: {relative}");
    Solid::union_all(&pieces.into_iter().map(|p| p.solid).collect::<Vec<_>>())
}

pub fn component(
    name: impl Into<String>,
    solid: Solid,
    color: [f64; 3],
) -> crate::tube_fixture::Component {
    crate::tube_fixture::Component {
        name: name.into(),
        solid,
        color,
    }
}
pub fn color(rgb: [f64; 3]) -> [f64; 3] {
    rgb.map(|v| {
        if v <= 0.04045 {
            v / 12.92
        } else {
            ((v + 0.055) / 1.055).powf(2.4)
        }
    })
}

fn renderer(root: &Path) -> Result<PathBuf> {
    if let Some(path) = std::env::var_os("HSM_RENDERER") {
        return Ok(path.into());
    }
    let local = root.join("tools/hsm/target/release/hsm-render");
    if local.is_file() {
        return Ok(local);
    }
    for directory in std::env::split_paths(&std::env::var_os("PATH").unwrap_or_default()) {
        let path = directory.join("hsm-render");
        if path.is_file() {
            return Ok(path);
        }
    }
    anyhow::bail!("install the native hsm renderer before drawing guide artwork")
}

pub fn render(root: &Path, output: &Path, scenes: Vec<Scene>) -> Result<()> {
    let stamp = SystemTime::now().duration_since(UNIX_EPOCH)?.as_nanos();
    let scratch = root.join(format!(
        ".cache/runs/manual-guide-art-{}-{stamp}",
        std::process::id()
    ));
    std::fs::create_dir_all(&scratch)?;
    std::fs::create_dir_all(output)?;
    let result = (|| -> Result<()> {
        let mut jobs = Vec::<Value>::new();
        for scene in &scenes {
            let bodies: Vec<_> = scene
                .bodies
                .iter()
                .map(|b| Body {
                    name: &b.name,
                    color: Some(b.color),
                    solid: &b.solid,
                })
                .collect();
            let payload = scratch.join(format!("{}.step.mesh", scene.name));
            crate::write(
                &payload,
                &hsm_kernel::write::payload_bytes(&bodies, None, None),
            )?;
            let mut job = json!({"payload":payload,"out":output.join(format!("{}.png",scene.name)),"cam":scene.camera,"up":scene.up,"size":scene.size,"bg":"#ffffff","transparent":true,"trim":true,"solid":true,"ortho":true,"ground":false,"fog":false});
            if let Some(target) = scene.target {
                job["target"] = json!(target);
            }
            if let Some(span) = scene.span {
                job["span"] = json!(span);
            }
            jobs.push(job);
        }
        let manifest = scratch.join("jobs.json");
        crate::write_json(&manifest, &jobs)?;
        let status = Command::new(renderer(root)?)
            .arg("--root")
            .arg(root)
            .arg("--jobs")
            .arg(&manifest)
            .status()
            .context("run native guide artwork renderer")?;
        ensure!(status.success(), "guide renderer exited with {status}");
        for scene in &scenes {
            println!("{}", output.join(format!("{}.png", scene.name)).display());
        }
        Ok(())
    })();
    if result.is_ok() {
        std::fs::remove_dir_all(&scratch)?;
    } else {
        eprintln!("guide render inputs retained at {}", scratch.display());
    }
    result
}
