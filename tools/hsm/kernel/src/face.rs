//! Where every triangle came from: the surface it lies on, the operation that made it, and the
//! generator line that asked for it.
use crate::math::{Affine, V3, atan};
use crate::rule::canonical_axis;
use anyhow::{Context, Result, ensure};
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::fmt;
use std::panic::Location;
use std::path::{Component, Path, PathBuf};
use std::sync::Mutex;

/// Where a face came from: the generator line that asked for it, as `#[track_caller]` reports
/// it, or the file it was read from (`file_src`).
pub type Src = &'static dyn Source;

/// A file, and the line in it when the face came from a generator's line.
pub trait Source: fmt::Debug + Sync {
    /// A generator's file as rustc names it, or a read file by the name its reader gave it.
    fn file(&self) -> &str;
    fn line(&self) -> Option<u32>;
    fn column(&self) -> Option<u32>;
    /// A source string already recorded by a model, without rustc's workspace prefix.
    fn repo_relative(&self) -> bool { false }
    /// False when the producer explicitly recorded no source (`null`).
    fn recorded(&self) -> bool { true }
}

impl Source for Location<'static> {
    fn file(&self) -> &str {
        Location::file(self)
    }
    fn line(&self) -> Option<u32> {
        Some(Location::line(self))
    }
    fn column(&self) -> Option<u32> {
        Some(Location::column(self))
    }
}

impl PartialEq for dyn Source {
    fn eq(&self, other: &Self) -> bool {
        self.file() == other.file() && self.line() == other.line() && self.column() == other.column()
            && self.recorded() == other.recorded()
    }
}

#[derive(Debug)]
struct ReadFile {
    name: String,
    line: Option<u32>,
}

#[derive(Debug)]
struct UnknownSource;

impl Source for UnknownSource {
    fn file(&self) -> &str { "" }
    fn line(&self) -> Option<u32> { None }
    fn column(&self) -> Option<u32> { None }
    fn recorded(&self) -> bool { false }
}

/// A face whose model explicitly records no source.
pub fn unknown_src() -> Src {
    static UNKNOWN: UnknownSource = UnknownSource;
    &UNKNOWN
}

impl Source for ReadFile {
    fn file(&self) -> &str {
        &self.name
    }
    fn line(&self) -> Option<u32> {
        self.line
    }
    fn column(&self) -> Option<u32> {
        None
    }
    fn repo_relative(&self) -> bool { true }
}

/// The source of a face read from the file `name`, one per name for the run.
pub fn file_src(name: &str) -> Src {
    read_src(name, None)
}

fn read_src(name: &str, line: Option<u32>) -> Src {
    static NAMES: Mutex<BTreeMap<(String, Option<u32>), &'static ReadFile>> = Mutex::new(BTreeMap::new());
    let mut names = NAMES.lock().unwrap_or_else(|e| e.into_inner());
    let key = (name.to_owned(), line);
    if let Some(&src) = names.get(&key) {
        return src;
    }
    let src: &'static ReadFile = Box::leak(Box::new(ReadFile { name: name.to_owned(), line }));
    names.insert(key, src);
    src
}

/// A source already written as a repo-relative `path:line`, or a file name alone.
pub fn record_src(text: &str) -> Src {
    match text.rsplit_once(':').and_then(|(name, line)| line.parse().ok().map(|line| (name, line))) {
        Some((name, line)) => read_src(name, Some(line)),
        None => file_src(text),
    }
}

fn intern(text: &str) -> &'static str {
    static TEXT: Mutex<BTreeSet<&'static str>> = Mutex::new(BTreeSet::new());
    let mut held = TEXT.lock().unwrap_or_else(|e| e.into_inner());
    if let Some(&text) = held.get(text) { return text; }
    let text: &'static str = Box::leak(text.to_owned().into_boxed_str());
    held.insert(text);
    text
}

/// `path:line` of a generator line, the path from the checkout's root, as meshcad writes its own;
/// a read file's name alone.
pub fn src_line(src: Src) -> String {
    match src.line() {
        Some(line) if src.repo_relative() => format!("{}:{line}", src.file()),
        Some(line) => format!("{}:{line}", repo_path(src.file())),
        None => src.file().to_string(),
    }
}

/// A source file as rustc has it, named from the checkout's root. Cargo hands rustc a source
/// inside the workspace by its path from the workspace and one outside it whole, which would
/// name the checkout that built it.
fn repo_path(file: &str) -> String {
    let workspace = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let root = workspace.parent().and_then(Path::parent).unwrap();
    let file = workspace.join(file);
    let mut path = PathBuf::new();
    for c in file.strip_prefix(root).unwrap_or(&file).components() {
        match c {
            Component::ParentDir => {
                path.pop();
            }
            Component::CurDir => {}
            c => path.push(c),
        }
    }
    path.to_string_lossy().into_owned()
}

/// The exact surface a face lies on. Normals point out of the solid.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Surface {
    Plane { p: V3, n: V3 },
    /// Axis through `p` along unit `d`.
    Cylinder { p: V3, d: V3, r: f64 },
    /// Radius `r` at `p`, growing by `slope` per unit along `d`.
    Cone { p: V3, d: V3, r: f64, slope: f64 },
    Sphere { c: V3, r: f64 },
    /// `major` from the axis to the tube's center, `minor` the tube's radius.
    Torus { c: V3, d: V3, major: f64, minor: f64 },
    /// A surface with no closed form here: an extrusion or revolution of a free curve, a ruled
    /// band, a blend.
    Free { kind: &'static str },
}

/// What two faces share to be one face: the surface, never where it came from. Components are
/// rounded integers, so equal keys hash alike.
#[derive(Clone, Debug, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum SurfaceKey {
    Plane([i64; 4]),
    Cylinder([i64; 7]),
    Cone([i64; 7]),
    Sphere([i64; 4]),
    Torus([i64; 8]),
}

fn q(x: f64, decimals: i32) -> i64 {
    (x * 10f64.powi(decimals)).round_ties_even() as i64
}

impl Surface {
    pub fn kind(&self) -> &'static str {
        match self {
            Surface::Plane { .. } => "PLANE",
            Surface::Cylinder { .. } => "CYLINDER",
            Surface::Cone { .. } => "CONE",
            Surface::Sphere { .. } => "SPHERE",
            Surface::Torus { .. } => "TORUS",
            Surface::Free { kind } => kind,
        }
    }

    pub fn is_analytic(&self) -> bool {
        !matches!(self, Surface::Free { .. })
    }

    /// The surface moved by `t`, which may scale uniformly and mirror.
    pub fn transformed(&self, t: &Affine) -> Surface {
        let s = t.length_scale();
        let dir = |d: V3| t.vector(d).unit();
        match *self {
            Surface::Plane { p, n } => Surface::Plane { p: t.point(p), n: t.normal(n) },
            Surface::Cylinder { p, d, r } => Surface::Cylinder { p: t.point(p), d: dir(d), r: r * s },
            Surface::Cone { p, d, r, slope } => Surface::Cone { p: t.point(p), d: dir(d), r: r * s, slope },
            Surface::Sphere { c, r } => Surface::Sphere { c: t.point(c), r: r * s },
            Surface::Torus { c, d, major, minor } => Surface::Torus {
                c: t.point(c),
                d: dir(d),
                major: major * s,
                minor: minor * s,
            },
            Surface::Free { kind } => Surface::Free { kind },
        }
    }

    /// For a plane, whether its normal points along its key's axis; true for every other surface.
    /// Two faces on one plane face the same way when their senses agree.
    pub fn sense(&self) -> bool {
        match *self {
            Surface::Plane { n, .. } => n.dot(canonical_axis(n)) > 0.0,
            _ => true,
        }
    }

    /// The key coincident surfaces share, or None for a free surface.
    pub fn key(&self) -> Option<SurfaceKey> {
        Some(match *self {
            Surface::Plane { p, n } => {
                let n = canonical_axis(n);
                SurfaceKey::Plane([q(n.x, 6), q(n.y, 6), q(n.z, 6), q(n.dot(p), 5)])
            }
            Surface::Cylinder { p, d, r } => {
                let d = canonical_axis(d);
                let foot = p - d * p.dot(d);
                SurfaceKey::Cylinder([
                    q(d.x, 6),
                    q(d.y, 6),
                    q(d.z, 6),
                    q(foot.x, 4),
                    q(foot.y, 4),
                    q(foot.z, 4),
                    q(r, 5),
                ])
            }
            Surface::Cone { p, d, r, slope } => {
                if slope == 0.0 {
                    return Surface::Cylinder { p, d, r }.key();
                }
                let apex = p - d * (r / slope);
                let dc = canonical_axis(d);
                SurfaceKey::Cone([
                    q(dc.x, 6),
                    q(dc.y, 6),
                    q(dc.z, 6),
                    q(apex.x, 4),
                    q(apex.y, 4),
                    q(apex.z, 4),
                    q(atan(slope).abs(), 6),
                ])
            }
            Surface::Sphere { c, r } => SurfaceKey::Sphere([q(c.x, 4), q(c.y, 4), q(c.z, 4), q(r, 5)]),
            Surface::Torus { c, d, major, minor } => {
                let d = canonical_axis(d);
                SurfaceKey::Torus([
                    q(d.x, 6),
                    q(d.y, 6),
                    q(d.z, 6),
                    q(c.x, 4),
                    q(c.y, 4),
                    q(c.z, 4),
                    q(major, 5),
                    q(minor, 5),
                ])
            }
            Surface::Free { .. } => return None,
        })
    }

    /// The surface's unit normal at (or nearest) `x`, in the record's own sense; None for a
    /// free surface.
    pub fn normal_at(&self, x: V3) -> Option<V3> {
        Some(match *self {
            Surface::Plane { n, .. } => n.unit(),
            Surface::Cylinder { p, d, .. } => (x - p).reject(d).unit(),
            Surface::Cone { p, d, slope, .. } => {
                let out = (x - p).reject(d).unit();
                (out - d * slope).unit()
            }
            Surface::Sphere { c, .. } => (x - c).unit(),
            Surface::Torus { c, d, major, .. } => {
                let v = x - c;
                let h = v.dot(d);
                let radial = v - d * h;
                let w = radial.unit() * (radial.norm() - major) + d * h;
                w.unit()
            }
            Surface::Free { .. } => return None,
        })
    }

    /// Signed distance from `x` to the surface, positive on the side the normal points; None
    /// for a free surface.
    pub fn distance(&self, x: V3) -> Option<f64> {
        Some(match *self {
            Surface::Plane { p, n } => (x - p).dot(n.unit()),
            Surface::Cylinder { p, d, r } => (x - p).reject(d).norm() - r,
            Surface::Cone { p, d, r, slope } => {
                let v = x - p;
                let h = v.dot(d);
                let rho = v.reject(d).norm();
                (rho - r - slope * h) / (1.0 + slope * slope).sqrt()
            }
            Surface::Sphere { c, r } => (x - c).norm() - r,
            Surface::Torus { c, d, major, minor } => {
                let v = x - c;
                let h = v.dot(d);
                let rho = v.reject(d).norm();
                ((rho - major).powi(2) + h * h).sqrt() - minor
            }
            Surface::Free { .. } => return None,
        })
    }
}

/// The boolean that brought a tool's face into a solid.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Via {
    pub op: &'static str,
    pub src: Src,
}

/// One face record: every triangle of a solid names one.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Face {
    pub surface: Surface,
    /// The builder that made the face: "box", "extrude", "revolve", "cylinder", "sweep", …
    pub op: &'static str,
    pub src: Src,
    pub via: Option<Via>,
    /// The complete model record was null, distinct from an object's nullable source.
    pub record_null: bool,
}

impl Face {
    pub fn new(surface: Surface, op: &'static str, src: Src) -> Face {
        Face { surface, op, src, via: None, record_null: false }
    }

    pub fn transformed(&self, t: &Affine) -> Face {
        Face { surface: self.surface.transformed(t), ..*self }
    }

    /// The analytic surface and source record written by `write::face_json` or meshcad.
    pub fn from_json(record: &Value) -> Result<Face> {
        if record.is_null() {
            return Ok(Face {
                surface: Surface::Free { kind: "" },
                op: "",
                src: unknown_src(),
                via: None,
                record_null: true,
            });
        }
        let number = |key: &str| -> Result<f64> {
            let value = record[key].as_f64().with_context(|| format!("face has no numeric {key}"))?;
            ensure!(value.is_finite(), "face {key} is not finite");
            Ok(value)
        };
        let vector = |key: &str| -> Result<V3> {
            let value = record[key].as_array().with_context(|| format!("face has no vector {key}"))?;
            ensure!(value.len() == 3, "face {key} is not a three-vector");
            let mut out = [0.0; 3];
            for (i, v) in value.iter().enumerate() {
                out[i] = v.as_f64().with_context(|| format!("face {key} is not numeric"))?;
                ensure!(out[i].is_finite(), "face {key} is not finite");
            }
            Ok(V3::from(out))
        };
        let kind = record["kind"].as_str().context("face has no surface kind")?;
        let surface = match kind {
            "PLANE" => Surface::Plane { p: vector("p")?, n: vector("n")? },
            "CYLINDER" => Surface::Cylinder { p: vector("p")?, d: vector("d")?, r: number("r")? },
            "CONE" => Surface::Cone { p: vector("p")?, d: vector("d")?, r: number("r")?, slope: number("slope")? },
            "SPHERE" => Surface::Sphere { c: vector("c")?, r: number("r")? },
            "TORUS" => Surface::Torus { c: vector("c")?, d: vector("d")?, major: number("R")?, minor: number("r")? },
            kind => Surface::Free { kind: intern(kind) },
        };
        let source = record.get("src").context("face has no source field")?;
        let source = if source.is_null() { unknown_src() }
            else { record_src(source.as_str().context("face source is not text or null")?) };
        let mut face = Face::new(surface,
            intern(record["op"].as_str().context("face has no builder")?), source);
        if let Some(via) = record.get("via").filter(|v| !v.is_null()) {
            let (op, src) = via.as_str().and_then(|v| v.split_once(" at "))
                .context("face via is not 'operation at source'")?;
            face.via = Some(Via { op: intern(op), src: record_src(src) });
        }
        Ok(face)
    }
}

impl fmt::Display for Face {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} {} at {}", self.surface.kind(), self.op, src_line(self.src))?;
        if let Some(v) = self.via {
            write!(f, ", {} at {}", v.op, src_line(v.src))?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sources_are_named_from_the_root() {
        let root = Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap();
        let part = root.join("hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs");
        assert_eq!(repo_path(part.to_str().unwrap()), "hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs");
        assert_eq!(repo_path("kernel/tests/../src/face.rs"), "tools/hsm/kernel/src/face.rs");
    }
}
