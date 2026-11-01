//! STEP from solids, and the mesh model a mesh-kernel import reads beside it.
//!
//! A STEP here holds triangles, not a B-rep: AP242 triangulated surface sets, one product per
//! body under its name and colour, the bodies of a file of several under one assembly. It is the
//! file meshcad's `write.write_step` writes, so a reader takes one whichever kernel cut it:
//! `flute_payload`'s identity check, OCCT's reader, CAD programs. Its description carries
//! `MARK`, which tells a mesh-kernel `importStep` to read `model_bytes` beside it
//! (`<name>.step.npz`) and an OCCT import that it holds no B-rep. The page draws the payload
//! beside it instead: its occt-import-js 0.0.23 is OCCT 7.6, which reads no triangulated
//! surface set.
//!
//! Both are functions of the triangles, names and colours alone: the same bodies write the same
//! bytes on every run.
use crate::math::V3;
use crate::write::{Body, face_json};
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::fmt::Write as _;
use std::path::Path;

/// The file description of a STEP a mesh kernel wrote (meshcad's `write.STEP_MARK`).
pub const MARK: &str = "meshcad tessellated";

/// `x` as a STEP real: six decimals, trailing zeros taken off, the point kept.
fn real(x: f64) -> String {
    let mut s = format!("{x:.6}");
    while s.ends_with('0') {
        s.pop();
    }
    if s == "-0." { "0.".into() } else { s }
}

/// `s` as a STEP string: quotes doubled, anything past ASCII as `\X2\` UTF-16.
fn string(s: &str) -> String {
    let mut out = String::from("'");
    for c in s.chars() {
        match c {
            '\'' => out.push_str("''"),
            '\\' => out.push_str("\\\\"),
            ' '..='~' => out.push(c),
            _ => {
                out.push_str("\\X2\\");
                for u in c.encode_utf16(&mut [0; 2]) {
                    write!(out, "{:04X}", u).unwrap();
                }
                out.push_str("\\X0\\");
            }
        }
    }
    out.push('\'');
    out
}

/// A linear colour as the sRGB a STEP holds, converted as OCCT converts the single-precision
/// colour it keeps, so a reader converting back lands where an OCCT round trip would.
fn srgb(c: f64) -> f64 {
    let l = c as f32 as f64;
    if l <= 0.0031308 { l * 12.92 } else { l.powf(1.0 / 2.4) * 1.055 - 0.055 }
}

fn colour(c: f64) -> String {
    let mut s = format!("{:.12}", srgb(c));
    while s.ends_with('0') {
        s.pop();
    }
    s
}

struct Entities {
    text: String,
    next: usize,
}

impl Entities {
    /// Writes `body` as the next entity and returns its reference.
    fn add(&mut self, body: impl AsRef<str>) -> String {
        let id = self.next;
        self.next += 1;
        writeln!(self.text, "#{id} = {};", body.as_ref()).unwrap();
        format!("#{id}")
    }
}

/// The product of one body: its name, the definition its shape hangs on, and the category.
struct Product {
    definition: String,
    product: String,
}

fn product(e: &mut Entities, context: &str, name: &str, shape: &str) -> Product {
    let sdr = e.next;
    let pds = format!("#{}", sdr + 1);
    let pd = format!("#{}", sdr + 2);
    e.add(format!("SHAPE_DEFINITION_REPRESENTATION({pds},{shape})"));
    e.add(format!("PRODUCT_DEFINITION_SHAPE('','',{pd})"));
    let (pdf, pdc) = (format!("#{}", sdr + 3), format!("#{}", sdr + 6));
    e.add(format!("PRODUCT_DEFINITION('design','',{pdf},{pdc})"));
    let p = format!("#{}", sdr + 4);
    e.add(format!("PRODUCT_DEFINITION_FORMATION('','',{p})"));
    let n = string(name);
    e.add(format!("PRODUCT({n},{n},'',(#{}))", sdr + 5));
    e.add(format!("PRODUCT_CONTEXT('',{context},'mechanical')"));
    e.add(format!("PRODUCT_DEFINITION_CONTEXT('part definition',{context},'design')"));
    Product { definition: pd, product: p }
}

/// The bytes of the STEP of `bodies`, each solid simplified as a file takes it, one at a time as
/// it is written. A file of one body is that body's product; one of several stands each body's
/// product under an assembly named `root`.
pub fn step_bytes(bodies: &[Body], root: &str) -> Result<Vec<u8>> {
    step_with(bodies, root, true)
}

/// `step_bytes` of bodies whose solids are simplified already.
pub(crate) fn step_of(bodies: &[Body], root: &str) -> Result<Vec<u8>> {
    step_with(bodies, root, false)
}

fn step_with(bodies: &[Body], root: &str, simplify: bool) -> Result<Vec<u8>> {
    let mut e = Entities { text: String::new(), next: 1 };
    let app = e.next + 1;
    e.add(format!(
        "APPLICATION_PROTOCOL_DEFINITION('international standard','ap242_managed_model_based_3d_engineering',2013,#{app})"
    ));
    let app = e.add("APPLICATION_CONTEXT('Managed model based 3d engineering')");

    // One placement at the origin, and the units every representation states its numbers in.
    let units = |e: &mut Entities| -> String {
        let at = e.next;
        e.add(format!(
            "( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{})) \
             GLOBAL_UNIT_ASSIGNED_CONTEXT((#{},#{},#{})) REPRESENTATION_CONTEXT('Context #1',\
             '3D Context with UNIT and UNCERTAINTY') )",
            at + 4,
            at + 1,
            at + 2,
            at + 3
        ));
        e.add("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )");
        e.add("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )");
        e.add("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )");
        e.add(format!(
            "UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#{},'distance_accuracy_value','confusion accuracy')",
            at + 1
        ));
        format!("#{at}")
    };
    let placement = |e: &mut Entities| -> String {
        let at = e.next;
        e.add(format!("AXIS2_PLACEMENT_3D('',#{},#{},#{})", at + 1, at + 2, at + 3));
        e.add("CARTESIAN_POINT('',(0.,0.,0.))");
        e.add("DIRECTION('',(0.,0.,1.))");
        e.add("DIRECTION('',(1.,0.,0.))");
        format!("#{at}")
    };

    // Each body's surface set, under its own manifold surface representation.
    let tessellated = |e: &mut Entities, body: &Body, origin: &str, context: &str| -> Result<(String, String)> {
        let simple;
        let s = if simplify {
            simple = body.solid.simplified()?;
            &simple
        } else {
            body.solid
        };
        let rep = e.next;
        let set = format!("#{}", rep + 1);
        e.add(format!("MANIFOLD_SURFACE_SHAPE_REPRESENTATION('',({origin},{set}),{context})"));
        let mut tris = String::new();
        for (i, t) in s.tris().iter().enumerate() {
            if i > 0 {
                tris.push_str(",\n");
            }
            write!(tris, "({},{},{})", t[0] + 1, t[1] + 1, t[2] + 1).unwrap();
        }
        let n = s.verts().len();
        e.add(format!("TRIANGULATED_SURFACE_SET('',#{},{n},(),(),(\n{tris}))", rep + 2));
        let mut pts = String::new();
        for (i, p) in s.verts().iter().enumerate() {
            if i > 0 {
                pts.push_str(",\n");
            }
            write!(pts, "({},{},{})", real(p.x), real(p.y), real(p.z)).unwrap();
        }
        e.add(format!("COORDINATES_LIST('',{n},(\n{pts}))"));
        Ok((format!("#{rep}"), set))
    };

    let mut styled: Vec<(String, [f64; 3])> = vec![];
    let context;
    if let [body] = bodies {
        // The product's representation follows its seven entities: the representation, its
        // surface set and coordinates, then the placement and the units it names.
        let rep = e.next + 7;
        let p = product(&mut e, &app, body.name, &format!("#{rep}"));
        let origin = format!("#{}", rep + 3);
        context = format!("#{}", rep + 7);
        let (_, set) = tessellated(&mut e, body, &origin, &context)?;
        assert_eq!(placement(&mut e), origin);
        assert_eq!(units(&mut e), context);
        e.add(format!("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({}))", p.product));
        if let Some(c) = body.color {
            styled.push((set, c));
        }
    } else {
        let shape = format!("#{}", e.next + 7);
        let assembly = product(&mut e, &app, root, &shape);
        let at = e.next;
        let places: Vec<String> = (0..=bodies.len()).map(|k| format!("#{}", at + 1 + 4 * k)).collect();
        context = format!("#{}", at + 1 + 4 * (bodies.len() + 1));
        let rep = e.add(format!("SHAPE_REPRESENTATION('',({}),{context})", places.join(",")));
        for want in &places {
            assert_eq!(&placement(&mut e), want);
        }
        assert_eq!(units(&mut e), context);
        e.add(format!("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({}))", assembly.product));
        for (k, body) in bodies.iter().enumerate() {
            let shape = format!("#{}", e.next + 7);
            let p = product(&mut e, &app, body.name, &shape);
            let (own, set) = tessellated(&mut e, body, &places[0], &context)?;
            let at = e.next;
            e.add(format!("CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#{},#{})", at + 1, at + 3));
            e.add(format!(
                "( REPRESENTATION_RELATIONSHIP('','',{own},{rep}) REPRESENTATION_RELATIONSHIP_WITH_TRANSFORMATION(#{}) \
                 SHAPE_REPRESENTATION_RELATIONSHIP() )",
                at + 2
            ));
            e.add(format!("ITEM_DEFINED_TRANSFORMATION('','',{},{})", places[0], places[k + 1]));
            e.add(format!("PRODUCT_DEFINITION_SHAPE('Placement','Placement of an item',#{})", at + 4));
            e.add(format!(
                "NEXT_ASSEMBLY_USAGE_OCCURRENCE('{}',{},'',{},{},$)",
                k + 1,
                string(body.name),
                assembly.definition,
                p.definition
            ));
            e.add(format!("PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,({}))", p.product));
            if let Some(c) = body.color {
                styled.push((set, c));
            }
        }
    }

    // A colour per coloured body, on its surface set.
    if !styled.is_empty() {
        let at = e.next;
        let items: Vec<String> = (0..styled.len()).map(|k| format!("#{}", at + 1 + 8 * k)).collect();
        e.add(format!(
            "MECHANICAL_DESIGN_GEOMETRIC_PRESENTATION_REPRESENTATION('',({}),{context})",
            items.join(",")
        ));
        for (set, c) in &styled {
            let at = e.next;
            e.add(format!("STYLED_ITEM('color',(#{}),{set})", at + 1));
            e.add(format!("PRESENTATION_STYLE_ASSIGNMENT((#{}))", at + 2));
            e.add(format!("SURFACE_STYLE_USAGE(.BOTH.,#{})", at + 3));
            e.add(format!("SURFACE_SIDE_STYLE('',(#{}))", at + 4));
            e.add(format!("SURFACE_STYLE_FILL_AREA(#{})", at + 5));
            e.add(format!("FILL_AREA_STYLE('',(#{}))", at + 6));
            e.add(format!("FILL_AREA_STYLE_COLOUR('',#{})", at + 7));
            e.add(format!("COLOUR_RGB('',{},{},{})", colour(c[0]), colour(c[1]), colour(c[2])));
        }
    }

    let name = if let [body] = bodies { body.name } else { root };
    let mut out = String::new();
    out.push_str("ISO-10303-21;\nHEADER;\n");
    writeln!(out, "FILE_DESCRIPTION(({}),'2;1');", string(MARK))?;
    writeln!(out, "FILE_NAME({},'1970-01-01T00:00:00',(''),(''),'hsm-kernel','hsm-kernel','');", string(name))?;
    out.push_str("FILE_SCHEMA(('AP242_MANAGED_MODEL_BASED_3D_ENGINEERING_MIM_LF { 1 0 10303 442 1 1 4 }'));\n");
    out.push_str("ENDSEC;\nDATA;\n");
    out.push_str(&e.text);
    out.push_str("ENDSEC;\nEND-ISO-10303-21;\n");
    Ok(out.into_bytes())
}

pub fn write_step(path: impl AsRef<Path>, bodies: &[Body], root: &str) -> Result<()> {
    let path = path.as_ref();
    std::fs::write(path, step_bytes(bodies, root)?).with_context(|| format!("writing {}", path.display()))
}

/// One `.npy` array: version 1.0, little-endian, C order.
fn npy(descr: &str, shape: &[usize], data: &[u8]) -> Vec<u8> {
    let dims = match shape {
        [n] => format!("({n},)"),
        _ => format!("({})", shape.iter().map(|d| d.to_string()).collect::<Vec<_>>().join(", ")),
    };
    let mut head = format!("{{'descr': '{descr}', 'fortran_order': False, 'shape': {dims}, }}");
    while (10 + head.len() + 1) % 64 != 0 {
        head.push(' ');
    }
    head.push('\n');
    let mut out = Vec::with_capacity(10 + head.len() + data.len());
    out.extend_from_slice(b"\x93NUMPY\x01\x00");
    out.extend_from_slice(&(head.len() as u16).to_le_bytes());
    out.extend_from_slice(head.as_bytes());
    out.extend_from_slice(data);
    out
}

/// A zip archive of stored entries, each dated 1980-01-01 00:00, as numpy's `.npz` holds them.
fn stored_zip(entries: &[(String, Vec<u8>)]) -> Vec<u8> {
    const DATE: u16 = (1 << 5) | 1;
    let mut out = vec![];
    let mut central = vec![];
    for (name, data) in entries {
        let crc = crate::write::crc32(data);
        let offset = out.len() as u32;
        let head = |sig: u32, central: bool| -> Vec<u8> {
            let mut h = vec![];
            h.extend_from_slice(&sig.to_le_bytes());
            if central {
                h.extend_from_slice(&20u16.to_le_bytes());
            }
            for v in [20u16, 0, 0, 0, DATE] {
                h.extend_from_slice(&v.to_le_bytes());
            }
            for v in [crc, data.len() as u32, data.len() as u32] {
                h.extend_from_slice(&v.to_le_bytes());
            }
            h.extend_from_slice(&(name.len() as u16).to_le_bytes());
            h.extend_from_slice(&0u16.to_le_bytes());
            if central {
                for v in [0u16, 0, 0] {
                    h.extend_from_slice(&v.to_le_bytes());
                }
                h.extend_from_slice(&0u32.to_le_bytes());
                h.extend_from_slice(&offset.to_le_bytes());
            }
            h.extend_from_slice(name.as_bytes());
            h
        };
        out.extend(head(0x0403_4b50, false));
        out.extend_from_slice(data);
        central.extend(head(0x0201_4b50, true));
    }
    let at = out.len() as u32;
    out.extend_from_slice(&central);
    out.extend_from_slice(&0x0605_4b50u32.to_le_bytes());
    for v in [0u16, 0, entries.len() as u16, entries.len() as u16] {
        out.extend_from_slice(&v.to_le_bytes());
    }
    out.extend_from_slice(&(central.len() as u32).to_le_bytes());
    out.extend_from_slice(&at.to_le_bytes());
    out.extend_from_slice(&0u16.to_le_bytes());
    out
}

/// The bytes of the model a mesh-kernel import of the STEP reads (`<name>.step.npz`, meshcad's
/// `write.write_model`): per body its float64 vertices `V<i>`, triangles `T<i>`, the face
/// record of each triangle `F<i>`, and the records, names and linear colours as JSON.
pub fn model_bytes(bodies: &[Body]) -> Vec<u8> {
    model_with_document(bodies, None)
}

/// A fine model with an optional JSON document beside its unchanged arrays and identities.
pub fn model_bytes_with_document(bodies: &[Body], document: Option<&Value>) -> Vec<u8> {
    model_with_document(bodies, document)
}

fn model_with_document(bodies: &[Body], document: Option<&Value>) -> Vec<u8> {
    model_archive(bodies, document, None)
}

pub(crate) fn model_with_print(bodies: &[Body], document: &Value, print: &crate::write::PrintOutput) -> Vec<u8> {
    model_archive(bodies, Some(document), Some(print))
}

fn model_archive(bodies: &[Body], document: Option<&Value>, print: Option<&crate::write::PrintOutput>) -> Vec<u8> {
    let mut entries = vec![];
    let mut records = vec![];
    for (i, b) in bodies.iter().enumerate() {
        let s = b.solid;
        let v: Vec<u8> = s.verts().iter().flat_map(|p: &V3| p.to_array()).flat_map(f64::to_le_bytes).collect();
        let t: Vec<u8> = s.tris().iter().flatten().flat_map(|x| x.to_le_bytes()).collect();
        let f: Vec<u8> = s.face_of().iter().flat_map(|x| x.to_le_bytes()).collect();
        entries.push((format!("V{i}.npy"), npy("<f8", &[s.verts().len(), 3], &v)));
        entries.push((format!("T{i}.npy"), npy("<u4", &[s.tris().len(), 3], &t)));
        entries.push((format!("F{i}.npy"), npy("<u4", &[s.tris().len()], &f)));
        records.push(Value::from(s.faces().iter().map(face_json).collect::<Vec<_>>()));
    }
    let text = |v: Value| -> Vec<u8> {
        let bytes = serde_json::to_vec(&v).unwrap();
        npy("|u1", &[bytes.len()], &bytes)
    };
    let names: Vec<Value> = bodies.iter().map(|b| Value::from(b.name)).collect();
    let colors: Vec<Value> = bodies
        .iter()
        .map(|b| b.color.map_or(Value::Null, |c| Value::from(c.to_vec())))
        .collect();
    entries.push(("names.npy".into(), text(Value::from(names))));
    entries.push(("colors.npy".into(), text(Value::from(colors))));
    entries.push(("records.npy".into(), text(Value::from(records))));
    if let Some(document) = document {
        entries.push(("document.npy".into(), text(document.clone())));
    }
    if let Some(print) = print {
        for (i, faces) in print.faces.iter().enumerate() {
            let bytes: Vec<_> = faces.iter().flat_map(|f| f.to_le_bytes()).collect();
            entries.push((format!("print-F{i}.npy"), npy("<u4", &[faces.len()], &bytes)));
        }
        entries.push(("print-records.npy".into(), text(json!(print.records))));
    }
    stored_zip(&entries)
}

pub fn write_model(path: impl AsRef<Path>, bodies: &[Body]) -> Result<()> {
    let path = path.as_ref();
    std::fs::write(path, model_bytes(bodies)).with_context(|| format!("writing {}", path.display()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reals_keep_their_point() {
        assert_eq!(real(3.0), "3.");
        assert_eq!(real(12.5), "12.5");
        assert_eq!(real(-0.0000001), "0.");
        assert_eq!(real(-1.25), "-1.25");
    }

    #[test]
    fn strings_escape() {
        assert_eq!(string("fuse-clamp"), "'fuse-clamp'");
        assert_eq!(string("it's"), "'it''s'");
        assert_eq!(string("Ø4"), "'\\X2\\00D8\\X0\\4'");
    }

    #[test]
    fn colour_is_occt_srgb() {
        // M_PETG_BLACK, linear, back to the sRGB 38/255 and 41/255 OCCT writes for it.
        assert_eq!(colour(0.019382361322641373), "0.149019609447");
        assert_eq!(colour(0.022173885256052017), "0.160784315601");
    }
}
