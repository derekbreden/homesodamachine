//! A part the kernel cuts for the build, from the numbers its Python module writes.
//!
//! The module derives every number the part's geometry takes — from the parts it closes on, the
//! fits, the interfaces it meets — and writes them to `<name>.numbers.json` beside the part, so
//! each number keeps one home and every Python reader of it reads the same module. The part's
//! program reads that file and nothing else:
//!
//! ```text
//! <program> <numbers.json> <out dir>
//! ```
//!
//! and `write_part` writes what the build publishes: `<name>.stl`, `<name>.step`, the model file
//! a mesh-kernel import reads beside it (`<name>.step.npz`), and the payload the page draws
//! (`<name>.step.mesh`), which names the STEP it was written with by that file's SHA-256.
//! `write_shown` writes the same set without the STL, for bodies the page draws and nothing
//! prints. A file already holding the same bytes is left as it is; any other lands whole, by a
//! rename. Each call answers with what its files hold, and the program prints each answer on a
//! line of its own, which is all its standard output carries.
use crate::solid::Solid;
use crate::step::{model_bytes, step_bytes};
use crate::write::{Body, payload_bytes, stl_bytes};
use anyhow::{Context, Result, anyhow, ensure};
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

/// One part's numbers, as its Python module wrote them.
pub struct Numbers {
    v: Value,
    path: String,
}

impl Numbers {
    pub fn read(path: impl AsRef<Path>) -> Result<Numbers> {
        let path = path.as_ref();
        let text = std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
        let v = serde_json::from_str(&text).with_context(|| format!("parsing {}", path.display()))?;
        Ok(Numbers { v, path: path.display().to_string() })
    }

    pub fn get(&self, key: &str) -> Result<&Value> {
        self.v.get(key).ok_or_else(|| anyhow!("{} has no `{key}`", self.path))
    }

    pub fn f(&self, key: &str) -> Result<f64> {
        self.get(key)?.as_f64().ok_or_else(|| anyhow!("{}: `{key}` is not a number", self.path))
    }

    pub fn list(&self, key: &str) -> Result<Vec<f64>> {
        let a = self.get(key)?.as_array().ok_or_else(|| anyhow!("{}: `{key}` is not a list", self.path))?;
        a.iter()
            .map(|x| x.as_f64().ok_or_else(|| anyhow!("{}: `{key}` holds a non-number", self.path)))
            .collect()
    }

    pub fn pair(&self, key: &str) -> Result<(f64, f64)> {
        match self.list(key)?[..] {
            [a, b] => Ok((a, b)),
            _ => Err(anyhow!("{}: `{key}` is not a pair", self.path)),
        }
    }

    /// A body's colour, linear RGB, as the payload carries it.
    pub fn color(&self, key: &str) -> Result<[f64; 3]> {
        match self.list(key)?[..] {
            [r, g, b] => Ok([r, g, b]),
            _ => Err(anyhow!("{}: `{key}` is not a colour", self.path)),
        }
    }

    pub fn text(&self, key: &str) -> Result<&str> {
        self.get(key)?.as_str().ok_or_else(|| anyhow!("{}: `{key}` is not text", self.path))
    }
}

/// The numbers file and the directory a part's files go to, from the command line.
pub fn args() -> Result<(Numbers, PathBuf)> {
    let a: Vec<String> = std::env::args().collect();
    ensure!(a.len() == 3, "usage: {} <numbers.json> <out dir>", a[0]);
    Ok((Numbers::read(&a[1])?, a[2].clone().into()))
}

/// Write the part's files into `dir`, the STEP and the root of its assembly named `name`, and say
/// what they hold: the files, and per body its name, volume, area, bounds and triangles.
pub fn write_part(dir: &Path, name: &str, bodies: &[Body]) -> Result<Value> {
    write_set(dir, name, bodies, true)
}

/// `write_part` without the STL.
pub fn write_shown(dir: &Path, name: &str, bodies: &[Body]) -> Result<Value> {
    write_set(dir, name, bodies, false)
}

fn write_set(dir: &Path, name: &str, bodies: &[Body], printed: bool) -> Result<Value> {
    let step = step_bytes(bodies, name)?;
    let digest: String = Sha256::digest(&step).iter().map(|b| format!("{b:02x}")).collect();
    let mut files = vec![
        (format!("{name}.step"), step),
        (format!("{name}.step.npz"), model_bytes(bodies)),
        (format!("{name}.step.mesh"), payload_bytes(bodies, Some(&digest), None)),
    ];
    if printed {
        let solids: Vec<&Solid> = bodies.iter().map(|b| b.solid).collect();
        files.push((format!("{name}.stl"), stl_bytes(&solids)?));
    }
    for (file, bytes) in &files {
        keep(&dir.join(file), bytes)?;
    }
    let held: Vec<Value> = bodies
        .iter()
        .map(|b| {
            let s = b.solid.bounds();
            json!({
                "name": b.name,
                "volume": b.solid.volume(),
                "area": b.solid.area(),
                "min": s.min.to_array(),
                "max": s.max.to_array(),
                "triangles": b.solid.tris().len(),
            })
        })
        .collect();
    Ok(json!({"files": files.iter().map(|(f, _)| f.as_str()).collect::<Vec<_>>(), "bodies": held}))
}

/// `bytes` at `path`, unless the file holds them already. They are written to a sibling named
/// to end as `path` does, so whatever keeps `path` out of the tree keeps it out too, and renamed
/// onto it.
fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path.file_name().and_then(|f| f.to_str()).ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::plane::Plane;

    #[test]
    fn a_part_lands_once() -> Result<()> {
        let dir = std::env::temp_dir().join(format!("hsm-part-{}", std::process::id()));
        std::fs::create_dir_all(&dir)?;
        let block = Plane::XY.cuboid(20.0, 10.0, 5.0);
        let body = Body { name: "block", color: Some([0.5, 0.25, 0.125]), solid: &block };
        let said = write_part(&dir, "block", &[body])?;
        assert_eq!(said["files"], json!(["block.step", "block.step.npz", "block.step.mesh", "block.stl"]));
        assert!((said["bodies"][0]["volume"].as_f64().unwrap() - 1000.0).abs() < 1e-9);
        let step = std::fs::read(dir.join("block.step"))?;
        let digest: String = Sha256::digest(&step).iter().map(|b| format!("{b:02x}")).collect();
        let payload = std::fs::read(dir.join("block.step.mesh"))?;
        let head = u32::from_le_bytes(payload[..4].try_into()?) as usize;
        let header: Value = serde_json::from_slice(&payload[4..4 + head])?;
        assert_eq!(header["src"], json!(digest));
        let before = std::fs::metadata(dir.join("block.stl"))?.modified()?;
        std::thread::sleep(std::time::Duration::from_millis(20));
        write_part(&dir, "block", &[body])?;
        assert_eq!(std::fs::metadata(dir.join("block.stl"))?.modified()?, before);
        let mut left: Vec<String> = std::fs::read_dir(&dir)?.map(|e| e.unwrap().file_name().into_string().unwrap()).collect();
        left.sort();
        assert_eq!(left, ["block.step", "block.step.mesh", "block.step.npz", "block.stl"]);
        std::fs::remove_dir_all(&dir)?;
        Ok(())
    }

    #[test]
    fn a_shown_set_has_no_stl() -> Result<()> {
        let dir = std::env::temp_dir().join(format!("hsm-shown-{}", std::process::id()));
        std::fs::create_dir_all(&dir)?;
        let block = Plane::XY.cuboid(20.0, 10.0, 5.0);
        let said = write_shown(&dir, "block", &[Body { name: "block", color: None, solid: &block }])?;
        assert_eq!(said["files"], json!(["block.step", "block.step.npz", "block.step.mesh"]));
        assert!(!dir.join("block.stl").exists());
        std::fs::remove_dir_all(&dir)?;
        Ok(())
    }
}
