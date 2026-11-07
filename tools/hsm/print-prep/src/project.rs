//! A Bambu Studio plate project: the objects on one plate, each a normal part with its paint,
//! plus modifier and extra parts and layer ranges, written as the 3MF archive Bambu Studio opens
//! and slices, element for element as the Python preparers wrote it.

use crate::ids::uuid5;
use crate::json::{python_number, Json};
use crate::profile::{Profile, SETTINGS_MEMBER};
use anyhow::Result;
use std::collections::BTreeMap;
use std::fmt::Write as _;
use std::io::Write as _;
use std::path::Path;

const CORE: &str = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02";
const PROD: &str = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06";
const REL: &str = "http://schemas.openxmlformats.org/package/2006/relationships";
const MODEL_TYPE: &str = "http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel";
pub const IDENTITY: &str = "1 0 0 0 1 0 0 0 1 0 0 0";
pub const MATRIX: &str = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1";
const CONTENT_TYPES: &str = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">\n<Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>\n<Default Extension=\"model\" ContentType=\"application/vnd.ms-package.3dmanufacturing-3dmodel+xml\"/>\n<Default Extension=\"config\" ContentType=\"application/octet-stream\"/>\n</Types>";

/// A triangle's paint: attribute name and value, such as `paint_supports` or `paint_seam`.
pub type Paint = Vec<(String, String)>;

pub struct Part {
    pub name: String,
    pub id: usize,
    pub subtype: String,
    pub member: String,
    pub vertices: Vec<[f64; 3]>,
    pub faces: Vec<[usize; 3]>,
    pub paint: Option<Vec<Paint>>,
    pub settings: Vec<(String, String)>,
}

pub struct Range {
    pub min_z: f64,
    pub max_z: f64,
    pub options: Vec<(String, String)>,
}

pub struct Object {
    pub name: String,
    pub object_id: usize,
    pub part_id: usize,
    pub identify_id: usize,
    pub source_file: String,
    pub source_center: [f64; 3],
    /// plate = rotation · local + translation
    pub rotation: [[f64; 3]; 3],
    pub translation: [f64; 3],
    pub member: String,
    pub vertices: Vec<[f64; 3]>,
    pub faces: Vec<[usize; 3]>,
    pub paint: Option<Vec<Paint>>,
    pub settings: Vec<(String, String)>,
    pub parts: Vec<Part>,
    pub ranges: Vec<Range>,
}

impl Object {
    /// The build item's transform: the rotation's transpose, row by row, then the translation.
    pub fn transform_values(&self) -> [f64; 12] {
        let r = self.rotation;
        [r[0][0], r[1][0], r[2][0], r[0][1], r[1][1], r[2][1], r[0][2], r[1][2], r[2][2],
         self.translation[0], self.translation[1], self.translation[2]]
    }

    pub fn transform(&self) -> String {
        self.transform_values().iter().map(|v| format!("{v:.9}")).collect::<Vec<_>>().join(" ")
    }
}

pub struct Plate {
    pub title: String,
    pub settings: Json,
    pub members: BTreeMap<String, Vec<u8>>,
    pub objects: Vec<Object>,
    /// Prefix of every object's name-based identifier, so a project's identities are its own.
    pub id_prefix: String,
    /// The filament map the plate carries; the project settings' own when None.
    pub filament_maps: Option<String>,
    /// The name the build's identifier is made from; `<title>/build` when None.
    pub build_name: Option<String>,
    /// How each object's mesh member is written.
    pub mesh_style: MeshStyle,
    next_id: usize,
}

/// The two ways the Python preparers wrote a mesh member: the enclosure's streamed form with six
/// decimals, and the faucet's ElementTree form with nine.
#[derive(Clone, Copy, PartialEq)]
pub enum MeshStyle {
    Streamed,
    Element,
}

impl Plate {
    pub fn new(title: &str, profile: &Profile, id_prefix: &str) -> Plate {
        Plate {
            title: title.to_string(),
            settings: profile.settings.clone(),
            members: profile.members.clone(),
            objects: Vec::new(),
            id_prefix: id_prefix.to_string(),
            filament_maps: None,
            build_name: None,
            mesh_style: MeshStyle::Streamed,
            next_id: 1,
        }
    }

    fn id(&mut self) -> usize {
        let v = self.next_id;
        self.next_id += 1;
        v
    }

    fn identifier(&self, name: &str) -> String {
        uuid5(&format!("{}{}", self.id_prefix, name))
    }

    /// `vertices` are in the source frame less `source_center`.
    #[allow(clippy::too_many_arguments)]
    pub fn add_object(&mut self, name: &str, vertices: Vec<[f64; 3]>, faces: Vec<[usize; 3]>, source_file: &str,
                      source_center: [f64; 3], rotation: [[f64; 3]; 3], translation: [f64; 3],
                      paint: Option<Vec<Paint>>, settings: Vec<(String, String)>) -> usize {
        let part_id = self.id();
        let object_id = self.id();
        let index = self.objects.len() + 1;
        self.objects.push(Object {
            name: name.to_string(), object_id, part_id, identify_id: 1900 + index,
            source_file: source_file.to_string(), source_center, rotation, translation,
            member: format!("3D/Objects/object_{index}.model"), vertices, faces, paint, settings,
            parts: Vec::new(), ranges: Vec::new(),
        });
        self.objects.len() - 1
    }

    pub fn add_part(&mut self, object: usize, name: &str, vertices: Vec<[f64; 3]>, faces: Vec<[usize; 3]>,
                    subtype: &str, settings: Vec<(String, String)>, paint_all: Option<&str>) -> usize {
        let id = self.id();
        let obj = &mut self.objects[object];
        let slug: String = {
            let mut s = String::new();
            let mut dash = false;
            for c in name.chars() {
                if c.is_ascii_alphanumeric() || c == '_' || c == '.' || c == '-' {
                    s.push(c);
                    dash = false;
                } else if !dash {
                    s.push('-');
                    dash = true;
                }
            }
            s.trim_matches('-').to_string()
        };
        let member = format!("3D/Objects/{}-{}-{}.model", slug, obj.parts.len() + 1, obj.object_id);
        let paint = paint_all.map(|code| vec![vec![("paint_supports".to_string(), code.to_string())]; faces.len()]);
        obj.parts.push(Part { name: name.to_string(), id, subtype: subtype.to_string(), member, vertices, faces, paint, settings });
        id
    }

    pub fn write(&self, path: &Path) -> Result<()> {
        let mut model = String::new();
        let _ = write!(model, "<?xml version='1.0' encoding='UTF-8'?>\n<model xmlns=\"{CORE}\" xmlns:p=\"{PROD}\" unit=\"millimeter\" requiredextensions=\"p\" xmlns:BambuStudio=\"http://schemas.bambulab.com/package/2021\">");
        let _ = write!(model, "<metadata name=\"Application\">BambuStudio-02.08.02.61</metadata><metadata name=\"BambuStudio:3mfVersion\">1</metadata><metadata name=\"Title\">{}</metadata><resources>", text(&self.title));
        let build_name = self.build_name.clone().unwrap_or_else(|| format!("{}/build", self.title));
        let mut build = format!("<build p:UUID=\"{}\">", self.identifier(&build_name));
        let mut config = String::from("<?xml version='1.0' encoding='UTF-8'?>\n<config>");
        let mut plate = String::from("<plate>");
        let maps = self.filament_maps.clone().unwrap_or_else(|| {
            match self.settings.get("filament_map") {
                Some(m) => m.list().iter().filter_map(Json::text).collect::<Vec<_>>().join(" "),
                None => "1".into(),
            }
        });
        let bed = self.settings.get("curr_bed_type").and_then(Json::text).unwrap_or("").to_string();
        for (key, value) in [("plater_id", "1".to_string()), ("plater_name", self.title.clone()), ("locked", "false".into()),
                             ("filament_map_mode", "Auto For Flush".into()), ("filament_maps", maps),
                             ("filament_volume_maps", "0".into()), ("bed_type", bed)] {
            metadata(&mut plate, key, &value);
        }
        let mut assemble = String::from("<assemble>");
        let mut rels = format!("<?xml version='1.0' encoding='UTF-8'?>\n<Relationships xmlns=\"{REL}\">");
        let mut ranges = String::from("<?xml version='1.0' encoding='UTF-8'?>\n<objects>");
        let mut any_ranges = false;
        for (index, obj) in self.objects.iter().enumerate() {
            let index = index + 1;
            let name = &obj.name;
            let _ = write!(model, "<object id=\"{}\" type=\"model\" p:UUID=\"{}\"><components><component objectid=\"{}\" transform=\"{IDENTITY}\" p:path=\"/{}\" p:UUID=\"{}\" />",
                           obj.object_id, self.identifier(name), obj.part_id, attr(&obj.member), self.identifier(&format!("{name}/component")));
            let _ = write!(rels, "<Relationship Target=\"/{}\" Id=\"rel-{index}\" Type=\"{MODEL_TYPE}\" />", attr(&obj.member));
            let transform = obj.transform();
            let _ = write!(build, "<item objectid=\"{}\" transform=\"{transform}\" printable=\"1\" p:UUID=\"{}\" />", obj.object_id, self.identifier(&format!("{name}/item")));
            let _ = write!(config, "<object id=\"{}\">", obj.object_id);
            metadata(&mut config, "name", name);
            metadata(&mut config, "extruder", "1");
            for (k, v) in &obj.settings {
                metadata(&mut config, k, v);
            }
            let _ = write!(config, "<metadata face_count=\"{}\" /><part id=\"{}\" subtype=\"normal_part\" uuid=\"{}\">", obj.faces.len(), obj.part_id, self.identifier(&format!("{name}/part")));
            for (k, v) in [("name", name.clone()), ("matrix", MATRIX.into()), ("source_file", obj.source_file.clone()),
                           ("source_object_id", "0".into()), ("source_volume_id", "0".into()),
                           ("source_offset_x", python_number(obj.source_center[0])),
                           ("source_offset_y", python_number(obj.source_center[1])),
                           ("source_offset_z", python_number(obj.source_center[2]))] {
                metadata(&mut config, k, &v);
            }
            mesh_stat(&mut config, obj.faces.len());
            config.push_str("</part>");
            for extra in &obj.parts {
                if extra.subtype == "normal_part" {
                    let _ = write!(model, "<component objectid=\"{}\" transform=\"{IDENTITY}\" p:path=\"/{}\" p:UUID=\"{}\" />",
                                   extra.id, attr(&extra.member), self.identifier(&format!("{name}/{}", extra.member)));
                } else {
                    let _ = write!(model, "<component objectid=\"{}\" transform=\"{IDENTITY}\" p:path=\"/{}\" />", extra.id, attr(&extra.member));
                }
                let _ = write!(rels, "<Relationship Target=\"/{}\" Id=\"part-{}\" Type=\"{MODEL_TYPE}\" />", attr(&extra.member), extra.id);
                let _ = write!(config, "<part id=\"{}\" subtype=\"{}\" uuid=\"{}\">", extra.id, attr(&extra.subtype), self.identifier(&format!("{name}/{}/part", extra.member)));
                metadata(&mut config, "name", &extra.name);
                metadata(&mut config, "matrix", MATRIX);
                for (k, v) in &extra.settings {
                    metadata(&mut config, k, v);
                }
                mesh_stat(&mut config, extra.faces.len());
                config.push_str("</part>");
            }
            model.push_str("</components></object>");
            config.push_str("</object>");
            plate.push_str("<model_instance>");
            for (k, v) in [("object_id", obj.object_id), ("instance_id", 0), ("identify_id", obj.identify_id)] {
                metadata(&mut plate, k, &v.to_string());
            }
            plate.push_str("</model_instance>");
            let _ = write!(assemble, "<assemble_item object_id=\"{}\" instance_id=\"0\" transform=\"{transform}\" offset=\"0 0 0\" /><assemble_item object_id=\"{}\" volume_id=\"0\" transform=\"{IDENTITY}\" />", obj.object_id, obj.object_id);
            if !obj.ranges.is_empty() {
                any_ranges = true;
                // Bambu keys layer ranges by the object's 1-based plate order.
                let _ = write!(ranges, "<object id=\"{index}\">");
                for band in &obj.ranges {
                    let _ = write!(ranges, "<range min_z=\"{:.4}\" max_z=\"{:.4}\">", band.min_z, band.max_z);
                    for (k, v) in &band.options {
                        let _ = write!(ranges, "<option opt_key=\"{}\">{}</option>", attr(k), text(v));
                    }
                    ranges.push_str("</range>");
                }
                ranges.push_str("</object>");
            }
        }
        model.push_str("</resources>");
        build.push_str("</build>");
        model.push_str(&build);
        model.push_str("</model>");
        plate.push_str("</plate>");
        assemble.push_str("</assemble>");
        config.push_str(&plate);
        config.push_str(&assemble);
        config.push_str("</config>");
        rels.push_str("</Relationships>");
        ranges.push_str("</objects>");
        let mut members = self.members.clone();
        members.insert(SETTINGS_MEMBER.to_string(), (self.settings.dumps() + "\n").into_bytes());
        members.insert("3D/3dmodel.model".into(), model.into_bytes());
        members.insert("3D/_rels/3dmodel.model.rels".into(), rels.into_bytes());
        members.insert("_rels/.rels".into(), format!("<?xml version='1.0' encoding='UTF-8'?>\n<Relationships xmlns=\"{REL}\"><Relationship Target=\"/3D/3dmodel.model\" Id=\"rel-1\" Type=\"{MODEL_TYPE}\" /></Relationships>").into_bytes());
        members.insert("Metadata/model_settings.config".into(), config.into_bytes());
        if any_ranges {
            members.insert("Metadata/layer_config_ranges.xml".into(), ranges.into_bytes());
        }
        members.insert("[Content_Types].xml".into(), CONTENT_TYPES.as_bytes().to_vec());

        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let temporary = path.with_extension(format!("{}.tmp", path.extension().and_then(|e| e.to_str()).unwrap_or("")));
        {
            let file = std::fs::File::create(&temporary)?;
            let mut archive = zip::ZipWriter::new(file);
            for (name, data) in &members {
                archive.start_file(name.as_str(), options())?;
                archive.write_all(data)?;
            }
            for obj in &self.objects {
                stream_mesh(&mut archive, self.mesh_style, &obj.member, obj.part_id, &obj.vertices, &obj.faces, obj.paint.as_deref())?;
                for extra in &obj.parts {
                    stream_mesh(&mut archive, self.mesh_style, &extra.member, extra.id, &extra.vertices, &extra.faces, extra.paint.as_deref())?;
                }
            }
            archive.finish()?;
        }
        std::fs::rename(&temporary, path)?;
        Ok(())
    }
}

/// Members dated 1980-01-01, deflated, readable by all.
pub fn options() -> zip::write::SimpleFileOptions {
    zip::write::SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .compression_level(Some(6))
        .last_modified_time(zip::DateTime::default())
        .unix_permissions(0o644)
}

#[allow(clippy::too_many_arguments)]
fn stream_mesh(archive: &mut zip::ZipWriter<std::fs::File>, style: MeshStyle, member: &str, object_id: usize,
               vertices: &[[f64; 3]], faces: &[[usize; 3]], paint: Option<&[Paint]>) -> Result<()> {
    let close = if style == MeshStyle::Element { " />" } else { "/>" };
    archive.start_file(member, options())?;
    let mut out = String::new();
    let _ = write!(out, "<?xml version='1.0' encoding='UTF-8'?>\n<model xmlns=\"{CORE}\" unit=\"millimeter\"><resources><object id=\"{object_id}\" type=\"model\"><mesh><vertices>");
    for v in vertices {
        if style == MeshStyle::Element {
            let _ = write!(out, "<vertex x=\"{:.9}\" y=\"{:.9}\" z=\"{:.9}\" />", v[0], v[1], v[2]);
        } else {
            let _ = write!(out, "<vertex x=\"{:.6}\" y=\"{:.6}\" z=\"{:.6}\"/>", v[0], v[1], v[2]);
        }
        if out.len() > 1 << 20 {
            archive.write_all(out.as_bytes())?;
            out.clear();
        }
    }
    out.push_str("</vertices><triangles>");
    for (i, f) in faces.iter().enumerate() {
        let _ = write!(out, "<triangle v1=\"{}\" v2=\"{}\" v3=\"{}\"", f[0], f[1], f[2]);
        if let Some(codes) = paint {
            for (k, v) in &codes[i] {
                if k == "paint_supports" && (v.is_empty() || v == "0") {
                    continue;
                }
                let _ = write!(out, " {k}=\"{v}\"");
            }
        }
        out.push_str(close);
        if out.len() > 1 << 20 {
            archive.write_all(out.as_bytes())?;
            out.clear();
        }
    }
    out.push_str("</triangles></mesh></object></resources></model>");
    archive.write_all(out.as_bytes())?;
    Ok(())
}

fn metadata(out: &mut String, key: &str, value: &str) {
    let _ = write!(out, "<metadata key=\"{}\" value=\"{}\" />", attr(key), attr(value));
}

fn mesh_stat(out: &mut String, faces: usize) {
    let _ = write!(out, "<mesh_stat face_count=\"{faces}\" edges_fixed=\"0\" degenerate_facets=\"0\" facets_removed=\"0\" facets_reversed=\"0\" backwards_edges=\"0\" />");
}

/// Attribute text, escaped as ElementTree escapes it.
pub fn attr(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\r' => out.push_str("&#13;"),
            '\n' => out.push_str("&#10;"),
            '\t' => out.push_str("&#09;"),
            c => out.push(c),
        }
    }
    out
}

/// Element text, escaped as ElementTree escapes it.
pub fn text(s: &str) -> String {
    s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;")
}
