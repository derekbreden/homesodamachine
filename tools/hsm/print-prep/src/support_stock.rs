//! Identifies the emitted moves of deliberately removable solids for playback and support review.

use crate::audit::{Transform, apply, compose};
use crate::project::IDENTITY;
use crate::review::{Section, object_mesh};
use crate::{gcode, xml};
use anyhow::{Context, Result, ensure};
use serde::Deserialize;
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs::File;
use std::io::{self, Read};
use std::path::Path;
use zip::ZipArchive;

type Triangle = [[f64; 3]; 3];
type Bounds = [[f64; 3]; 2];
const POSE_TOLERANCE: f64 = 0.001;
const SECTION_INSET: f64 = 0.0001;

/// Source line numbers of commands that lay declared removable stock.
#[derive(Default)]
pub struct StockMoves(pub(crate) Vec<(usize, StockRole)>);

/// A removable solid can carry dense roof contact courses on its top face.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum StockRole {
    Body,
    Interface,
}

impl StockRole {
    pub const ALL: [Self; 2] = [Self::Body, Self::Interface];

    pub fn feature(self) -> &'static str {
        match self {
            Self::Body => "Support",
            Self::Interface => "Support interface",
        }
    }
}

impl StockMoves {
    pub fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    pub fn role(&self, line: usize) -> Option<StockRole> {
        if line < self.0.first()?.0 || line > self.0.last()?.0 {
            return None;
        }
        let index = self.0.binary_search_by_key(&line, |entry| entry.0).ok()?;
        Some(self.0[index].1)
    }

    /// Use the preparation beside a sliced plate when it binds that plate's G-code.
    pub fn beside(archive: &Path, gcode: &[u8], digest: &str) -> Result<Self> {
        if archive.extension().is_none_or(|ext| ext != "3mf") {
            return Ok(Self::default());
        }
        let path = archive.with_file_name("preparation.json");
        let record = match std::fs::read(&path) {
            Ok(bytes) => serde_json::from_slice(&bytes)
                .with_context(|| format!("reading {}", path.display()))?,
            Err(error) if error.kind() == io::ErrorKind::NotFound => return Ok(Self::default()),
            Err(error) => return Err(error).with_context(|| format!("reading {}", path.display())),
        };
        Self::from_preparation(archive, &record, gcode, digest)
    }

    pub(crate) fn from_preparation(
        archive: &Path,
        record: &Value,
        gcode: &[u8],
        digest: &str,
    ) -> Result<Self> {
        if record["gcode_sha256"].as_str() != Some(digest) {
            return Ok(Self::default());
        }
        let objects: Vec<_> = record["objects"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|object| {
                let stock = object["removable_support_stock"].as_array()?;
                (!stock.is_empty()).then_some((object, stock))
            })
            .collect();
        if objects.is_empty() {
            return Ok(Self::default());
        }
        let mut file = File::open(archive)?;
        let mut hash = Sha256::new();
        io::copy(&mut file, &mut hash)?;
        ensure!(
            record["archive_sha256"].as_str() == Some(&format!("{:x}", hash.finalize())),
            "the slice with declared removable support stock differs from its preparation"
        );
        let mut zip = ZipArchive::new(file)?;
        let settings = xml::parse(&member(&mut zip, "Metadata/model_settings.config")?)?;
        let model = xml::parse(&member(&mut zip, "3D/3dmodel.model")?)?;
        let mut meshes = HashMap::new();
        let mut parts = Vec::new();
        for (object, stock) in objects {
            let identify = object["identify_id"]
                .as_i64()
                .context("stock object's identify ID")?;
            let stock: Vec<Declaration> = stock
                .iter()
                .map(|row| serde_json::from_value(row.clone()))
                .collect::<Result<_, _>>()?;
            parts.push(read_object(
                &mut zip,
                &model,
                &settings,
                &mut meshes,
                identify,
                &stock,
            )?);
        }
        drop(meshes);
        Ok(Self(gcode::stock_lines(
            std::str::from_utf8(gcode)?,
            &parts,
        )))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::audit::{Options, audit_with_stock};
    use crate::review::box_triangles;

    #[test]
    fn only_moves_wholly_in_removable_stock_reach_the_audit() {
        let bounds = [[1., 1., 0.], [6., 6., 1.]];
        let parts = [StockObject {
            identify: 1901,
            stock: vec![StockPart {
                bounds,
                interface_start_z: None,
                triangles: box_triangles(bounds[0], bounds[1]),
            }],
            model: vec![box_triangles([3., 1., 0.], [4., 3., 1.])],
        }];
        let code = "M83\n; Z_HEIGHT: .2\n; LAYER_HEIGHT: .2\n; OBJECT_ID: 1901\n\
                    ; FEATURE: Outer wall\nG1 X1.5 Y2 Z.2\nG1 X2.5 E.1\n\
                    G1 X4.5 E.1\nG1 X5.5 Z.24 E.1\n; OBJECT_ID: 1902\n\
                    G1 X2.5 Y4 Z.2\nG1 X4.5 E.1\n";
        let stock = StockMoves(gcode::stock_lines(code, &parts));
        // The second extrusion crosses retained model stock and the third changes Z.
        assert_eq!(stock.0, [(7, StockRole::Body)]);
        let audit = audit_with_stock(
            code.as_bytes(),
            &Options {
                piece: "stock fixture".into(),
                object: Some(1901),
                include_unlabelled: false,
                cad_transform: None,
                bed_reseat: None,
                inputs: Value::Null,
            },
            &stock,
        );
        assert_eq!(audit["summary"]["removable_stock_moves"], 1);
        assert_eq!(audit["trees"][0]["declared_removable_stock"], true);
        assert!(audit["summary"]["interface_islands"].is_null());
    }

    #[test]
    fn cap_role_is_local_to_its_stock_and_print_height() {
        let bounds = [[1., 1., 0.], [6., 6., 1.]];
        let part = StockObject {
            identify: 1901,
            stock: vec![StockPart {
                bounds,
                interface_start_z: Some(0.4),
                triangles: box_triangles(bounds[0], bounds[1]),
            }],
            model: vec![],
        };
        let code = "M83\n; OBJECT_ID: 1901\n; FEATURE: Outer wall\n; Z_HEIGHT: .2\n\
                    G1 X2 Y2 Z.2\nG1 X4 E.1\n; Z_HEIGHT: .4\nG1 Z.4\nG1 X2 E.1\n\
                    ; Z_HEIGHT: .6\nG1 Z.6\nG1 X4 E.1\nG1 X8 E.1\n";
        let stock = StockMoves(gcode::stock_lines(code, &[part]));
        assert_eq!(stock.0, [(6, StockRole::Body), (9, StockRole::Body), (12, StockRole::Interface)]);
        assert_eq!(stock.role(13), None);
    }
}

#[derive(Deserialize)]
struct Declaration {
    name: String,
    plate_bounds_mm: Bounds,
    interface_top_depth_mm: Option<f64>,
}

fn member(zip: &mut ZipArchive<File>, path: &str) -> Result<String> {
    let mut text = String::new();
    zip.by_name(path)?.read_to_string(&mut text)?;
    Ok(text)
}

fn metadata<'a>(node: &'a xml::Element, key: &str) -> Option<&'a str> {
    node.children_named("metadata")
        .find(|entry| entry.attribute("key") == Some(key))?
        .attribute("value")
}

fn transform(node: &xml::Element) -> Result<Transform> {
    let values: Vec<f64> = node
        .attribute("transform")
        .unwrap_or(IDENTITY)
        .split_whitespace()
        .map(str::parse)
        .collect::<Result<_, _>>()?;
    ensure!(
        values.len() == 12 && values.iter().all(|n| n.is_finite()),
        "invalid plate transform"
    );
    Ok(values.try_into().unwrap())
}

fn part_mesh(text: &str, id: &str, pose: &Transform) -> Result<Vec<Triangle>> {
    // A sliced Bambu member can hold many volumes. Parse only the requested mesh block.
    let prefix = format!("id=\"{id}\"");
    let body = text
        .split("<object ")
        .skip(1)
        .find_map(|object| {
            let (tag, body) = object.split_once('>')?;
            if tag.split_whitespace().any(|word| word == prefix) {
                return body.split_once("</object>").map(|(body, _)| body);
            }
            None
        })
        .with_context(|| format!("sliced plate has no mesh for part {id}"))?;
    let (vertices, faces) = object_mesh(body);
    ensure!(
        !vertices.is_empty() && !faces.is_empty(),
        "empty plate mesh for part {id}"
    );
    let posed: Vec<_> = vertices.into_iter().map(|v| apply(v, pose)).collect();
    faces
        .into_iter()
        .map(|[a, b, c]| {
            ensure!(
                a < posed.len() && b < posed.len() && c < posed.len(),
                "invalid face in plate part {id}"
            );
            Ok([posed[a], posed[b], posed[c]])
        })
        .collect()
}

fn read_object(
    zip: &mut ZipArchive<File>,
    model: &xml::Element,
    settings: &xml::Element,
    meshes: &mut HashMap<String, String>,
    identify: i64,
    declared: &[Declaration],
) -> Result<StockObject> {
    let instance = settings
        .children_named("plate")
        .flat_map(|p| p.children_named("model_instance"))
        .find(|row| metadata(row, "identify_id").and_then(|s| s.parse().ok()) == Some(identify))
        .with_context(|| format!("sliced plate has no object with identify ID {identify}"))?;
    let id = metadata(instance, "object_id").context("sliced object ID")?;
    let instance_id: usize = metadata(instance, "instance_id")
        .context("sliced instance ID")?
        .parse()?;
    let build = model
        .child("build")
        .context("sliced plate build")?
        .children_named("item")
        .filter(|item| item.attribute("objectid") == Some(id))
        .nth(instance_id)
        .context("sliced object build item")?;
    let build = transform(build)?;
    let parts = settings
        .children_named("object")
        .find(|node| node.attribute("id") == Some(id))
        .context("sliced object settings")?;
    let owner = model
        .child("resources")
        .context("sliced plate resources")?
        .children_named("object")
        .find(|node| node.attribute("id") == Some(id))
        .context("sliced object resource")?;
    let components = owner
        .child("components")
        .context("sliced object components")?;
    let mut stock = Vec::new();
    let mut model = Vec::new();
    let lowest = declared
        .iter()
        .map(|s| s.plate_bounds_mm[0][2])
        .fold(f64::INFINITY, f64::min);
    let highest = declared
        .iter()
        .map(|s| s.plate_bounds_mm[1][2])
        .fold(f64::NEG_INFINITY, f64::max);
    for part in parts
        .children_named("part")
        .filter(|part| part.attribute("subtype") == Some("normal_part"))
    {
        let name = metadata(part, "name").context("sliced part name")?;
        let part_id = part.attribute("id").context("sliced part ID")?;
        let component = components
            .children_named("component")
            .find(|node| node.attribute("objectid") == Some(part_id))
            .context("sliced part component")?;
        let path = component
            .attribute("p:path")
            .context("sliced part mesh member")?
            .trim_start_matches('/');
        if !meshes.contains_key(path) {
            meshes.insert(path.to_string(), member(zip, path)?);
        }
        let mut triangles = part_mesh(
            &meshes[path],
            part_id,
            &compose(&transform(component)?, &build),
        )?;
        if let Some(declaration) = declared.iter().find(|row| row.name == name) {
            let bounds = triangles.iter().flatten().fold(
                [[f64::INFINITY; 3], [f64::NEG_INFINITY; 3]],
                |[lo, hi], point| {
                    [
                        std::array::from_fn(|i| lo[i].min(point[i])),
                        std::array::from_fn(|i| hi[i].max(point[i])),
                    ]
                },
            );
            ensure!(
                bounds
                    .iter()
                    .flatten()
                    .zip(declaration.plate_bounds_mm.iter().flatten())
                    .all(|(actual, declared)| (actual - declared).abs() < POSE_TOLERANCE),
                "sliced placement of {name} differs from its preparation"
            );
            let interface_start_z = declaration.interface_top_depth_mm.map(|depth| bounds[1][2] - depth);
            ensure!(
                interface_start_z.is_none_or(|z| (bounds[0][2]..bounds[1][2]).contains(&z)),
                "invalid removable interface depth on {name}"
            );
            stock.push(StockPart { bounds, triangles, interface_start_z });
        } else {
            triangles.retain(|t| {
                t.iter().any(|p| p[2] <= highest + POSE_TOLERANCE)
                    && t.iter().any(|p| p[2] >= lowest - POSE_TOLERANCE)
            });
            model.push(triangles);
        }
    }
    ensure!(
        stock.len() == declared.len() && !model.is_empty(),
        "cannot identify the removable meshes of object {identify}"
    );
    Ok(StockObject {
        identify,
        stock,
        model,
    })
}

struct StockPart {
    bounds: Bounds,
    triangles: Vec<Triangle>,
    interface_start_z: Option<f64>,
}

pub(crate) struct StockObject {
    identify: i64,
    stock: Vec<StockPart>,
    model: Vec<Vec<Triangle>>,
}

pub(crate) struct StockSection {
    identify: i64,
    pub(crate) role: StockRole,
    bounds: Bounds,
    solid: Section,
    model: std::rc::Rc<Vec<Section>>,
}

impl StockObject {
    pub(crate) fn sections(&self, bottom: f64, top: f64) -> Vec<StockSection> {
        let mid = (bottom + top) / 2.;
        let mut model: HashMap<_, std::rc::Rc<Vec<Section>>> = HashMap::new();
        self.stock
            .iter()
            .filter_map(|part| {
                let [low, high] = part.bounds;
                if top <= low[2] || mid >= high[2] {
                    return None;
                }
                // A root slightly above the slice plane can still be deposited on this course.
                let plane = mid.max(low[2] + SECTION_INSET);
                let model = model.entry(plane.to_bits()).or_insert_with(|| {
                    std::rc::Rc::new(
                        self.model
                            .iter()
                            .map(|mesh| Section::new(mesh, plane))
                            .collect(),
                    )
                });
                Some(StockSection {
                    identify: self.identify,
                    role: if part.interface_start_z.is_some_and(|z| plane >= z - POSE_TOLERANCE) {
                        StockRole::Interface
                    } else {
                        StockRole::Body
                    },
                    bounds: part.bounds,
                    solid: Section::new(&part.triangles, plane),
                    model: model.clone(),
                })
            })
            .collect()
    }
}

impl StockSection {
    pub(crate) fn contains(&self, road: &gcode::Road, top: f64) -> bool {
        if road.object != Some(self.identify)
            || (road.z0 - top).abs() > POSE_TOLERANCE
            || (road.z1 - top).abs() > POSE_TOLERANCE
        {
            return false;
        }
        let [lo, hi] = self.bounds;
        let (a, b) = ([road.x0, road.y0], [road.x1, road.y1]);
        (0..2).all(|i| lo[i] <= a[i].min(b[i]) && a[i].max(b[i]) <= hi[i])
            && self.solid.contains(a)
            && !self.solid.meets_boundary(a, b)
            && !self
                .model
                .iter()
                .any(|section| section.contains(a) || section.meets_boundary(a, b))
    }
}
