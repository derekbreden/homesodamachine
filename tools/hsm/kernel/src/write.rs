//! Files from solids: binary STL, 3MF, GLB and the viewer's `.step.mesh` payload.
//!
//! Every writer is a function of the triangles and face records alone, so the same solid writes
//! the same bytes every run: no timestamps, no order that depends on a hash seed. STL and 3MF
//! take the solid simplified to the rule's TOLERANCE (`Solid::simplified`); the payload and GLB
//! take it whole, grouped by the faces a reader sees (`topo::faces`).
use crate::face::{Face, Surface};
use crate::math::V3;
use crate::solid::Solid;
use crate::topo;
use anyhow::{Context, Result};
use serde_json::{Value, json};
use std::path::Path;

/// One named, coloured solid of a file.
#[derive(Clone, Copy)]
pub struct Body<'a> {
    pub name: &'a str,
    /// Linear RGB, 0 to 1.
    pub color: Option<[f64; 3]>,
    pub solid: &'a Solid,
}

pub const STL_HEADER: &[u8] = b"hsm-kernel binary STL";

fn tri_normal(a: V3, b: V3, c: V3) -> V3 {
    let n = (b - a).cross(c - a);
    let l = n.norm();
    if l > 0.0 { n / l } else { V3::ZERO }
}

fn f32s(p: V3) -> [f32; 3] {
    [p.x as f32, p.y as f32, p.z as f32]
}

fn widened(p: [f32; 3]) -> V3 {
    V3::from([p[0] as f64, p[1] as f64, p[2] as f64])
}

pub fn stl_bytes(solids: &[&Solid]) -> Result<Vec<u8>> {
    let mut tris: Vec<[[f32; 3]; 3]> = vec![];
    for s in solids {
        let s = s.simplified()?;
        for t in &s.tris {
            tris.push(t.map(|i| f32s(s.verts[i as usize])));
        }
    }
    let mut out = Vec::with_capacity(84 + 50 * tris.len());
    let mut header = STL_HEADER.to_vec();
    header.resize(80, b' ');
    out.extend_from_slice(&header);
    out.extend_from_slice(&(tris.len() as u32).to_le_bytes());
    for t in &tris {
        let n = tri_normal(widened(t[0]), widened(t[1]), widened(t[2]));
        for x in f32s(n).into_iter().chain(t.iter().flatten().copied()) {
            out.extend_from_slice(&x.to_le_bytes());
        }
        out.extend_from_slice(&[0, 0]);
    }
    Ok(out)
}

/// A 3MF package with one object per solid.
pub fn threemf_bytes(solids: &[&Solid], name: &str) -> Result<Vec<u8>> {
    use std::fmt::Write;
    let mut objs = String::new();
    let mut items = String::new();
    for (i, s) in solids.iter().enumerate() {
        let i = i + 1;
        let s = s.simplified()?;
        write!(objs, r#"<object id="{i}" type="model" name="{}-{i}"><mesh><vertices>"#, xml(name))?;
        for p in &s.verts {
            write!(objs, r#"<vertex x="{:.6}" y="{:.6}" z="{:.6}"/>"#, p.x, p.y, p.z)?;
        }
        objs.push_str("</vertices><triangles>");
        for t in &s.tris {
            write!(objs, r#"<triangle v1="{}" v2="{}" v3="{}"/>"#, t[0], t[1], t[2])?;
        }
        objs.push_str("</triangles></mesh></object>");
        write!(items, r#"<item objectid="{i}"/>"#)?;
    }
    let model = format!(
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<model unit=\"millimeter\" xml:lang=\"en-US\" \
         xmlns=\"http://schemas.microsoft.com/3dmanufacturing/core/2015/02\"><resources>{objs}</resources>\
         <build>{items}</build></model>"
    );
    let types = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">\
        <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>\
        <Default Extension=\"model\" ContentType=\"application/vnd.ms-package.3dmanufacturing-3dmodel+xml\"/></Types>";
    let rels = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">\
        <Relationship Target=\"/3D/3dmodel.model\" Id=\"rel0\" \
        Type=\"http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel\"/></Relationships>";
    Ok(zip(&[
        ("[Content_Types].xml", types.as_bytes()),
        ("_rels/.rels", rels.as_bytes()),
        ("3D/3dmodel.model", model.as_bytes()),
    ]))
}

fn xml(s: &str) -> String {
    s.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;").replace('"', "&quot;")
}

pub(crate) fn crc32(data: &[u8]) -> u32 {
    let mut table = [0u32; 256];
    for (i, e) in table.iter_mut().enumerate() {
        let mut c = i as u32;
        for _ in 0..8 {
            c = if c & 1 != 0 { 0xEDB8_8320 ^ (c >> 1) } else { c >> 1 };
        }
        *e = c;
    }
    let mut c = !0u32;
    for &b in data {
        c = table[((c ^ b as u32) & 0xFF) as usize] ^ (c >> 8);
    }
    !c
}

/// A zip archive of deflated entries, each dated 1980-01-01 00:00.
pub fn zip(entries: &[(&str, &[u8])]) -> Vec<u8> {
    const DATE: u16 = (1 << 5) | 1;
    let mut out = vec![];
    let mut central = vec![];
    for (name, data) in entries {
        let packed = miniz_oxide::deflate::compress_to_vec(data, 6);
        let crc = crc32(data);
        let offset = out.len() as u32;
        let head = |sig: u32, central: bool| -> Vec<u8> {
            let mut h = vec![];
            h.extend_from_slice(&sig.to_le_bytes());
            if central {
                h.extend_from_slice(&20u16.to_le_bytes());
            }
            for v in [20u16, 0, 8, 0, DATE] {
                h.extend_from_slice(&v.to_le_bytes());
            }
            for v in [crc, packed.len() as u32, data.len() as u32] {
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
        out.extend_from_slice(&packed);
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

/// One `.step.mesh` entry: per face its own vertices, so normals are smooth within a face and
/// sharp across its edges, and one inclusive triangle range per face. A vertex on an analytic
/// face takes the surface's own normal there.
struct Arrays {
    pos: Vec<f32>,
    nrm: Vec<f32>,
    idx: Vec<u32>,
    fac: Vec<u32>,
}

fn arrays(s: &Solid) -> Arrays {
    let faces = topo::faces(s);
    let mut a = Arrays { pos: vec![], nrm: vec![], idx: vec![], fac: vec![] };
    let mut base = 0u32;
    let mut first = 0u32;
    for (f, tris) in faces.tris.iter().enumerate() {
        let record = &s.faces[faces.record[f] as usize];
        let mut local: Vec<u32> = vec![];
        let mut slot = std::collections::HashMap::new();
        let mut summed: Vec<V3> = vec![];
        let mut idx = vec![];
        for &t in tris {
            let tri = s.tris[t as usize];
            let n = (s.verts[tri[1] as usize] - s.verts[tri[0] as usize])
                .cross(s.verts[tri[2] as usize] - s.verts[tri[0] as usize]);
            for v in tri {
                let k = *slot.entry(v).or_insert_with(|| {
                    local.push(v);
                    summed.push(V3::ZERO);
                    local.len() as u32 - 1
                });
                summed[k as usize] += n;
                idx.push(base + k);
            }
        }
        for (k, &v) in local.iter().enumerate() {
            let p = s.verts[v as usize];
            let around = summed[k];
            let n = match record.surface.normal_at(p) {
                Some(n) if n.is_finite() && !matches!(record.surface, Surface::Free { .. }) => {
                    if n.dot(around) < 0.0 { -n } else { n }
                }
                _ => around.unit(),
            };
            let n = if n.is_finite() { n } else { V3::ZERO };
            a.pos.extend(f32s(p));
            a.nrm.extend(f32s(n));
        }
        a.idx.extend(idx);
        a.fac.extend([first, first + tris.len() as u32 - 1]);
        first += tris.len() as u32;
        base += local.len() as u32;
    }
    a
}

fn color_json(c: Option<[f64; 3]>) -> String {
    match c {
        None => "null".into(),
        Some(c) => format!("[{},{},{}]", c[0], c[1], c[2]),
    }
}

/// The bytes of a version 3 `.step.mesh`: a little-endian u32 header length, the JSON header
/// padded with spaces to a multiple of four, then the arrays. `src` names what the payload was
/// cut from; `cut` is the reduction it records.
pub fn payload_bytes(bodies: &[Body], src: Option<&str>, cut: Option<&Value>) -> Vec<u8> {
    let mut blob: Vec<u8> = vec![];
    let mut entries = vec![];
    for b in bodies {
        let a = arrays(b.solid);
        let mut put = |bytes: Vec<u8>, n: usize| -> String {
            let at = blob.len();
            blob.extend(bytes);
            format!("[{at},{n}]")
        };
        let pos = put(a.pos.iter().flat_map(|x| x.to_le_bytes()).collect(), a.pos.len());
        let nrm = put(a.nrm.iter().flat_map(|x| x.to_le_bytes()).collect(), a.nrm.len());
        let idx = put(a.idx.iter().flat_map(|x| x.to_le_bytes()).collect(), a.idx.len());
        let fac = put(a.fac.iter().flat_map(|x| x.to_le_bytes()).collect(), a.fac.len());
        entries.push(format!(
            r#"{{"name":{},"color":{},"pos":{pos},"nrm":{nrm},"idx":{idx},"fac":{fac}}}"#,
            Value::from(b.name),
            color_json(b.color)
        ));
    }
    let mut head = format!(r#"{{"v":3,"meshes":[{}]"#, entries.join(","));
    if let Some(s) = src {
        head.push_str(&format!(r#","src":{}"#, Value::from(s)));
    }
    if let Some(c) = cut {
        head.push_str(&format!(r#","cut":{c}"#));
    }
    head.push('}');
    while (head.len() + 4) % 4 != 0 {
        head.push(' ');
    }
    let mut out = Vec::with_capacity(4 + head.len() + blob.len());
    out.extend_from_slice(&(head.len() as u32).to_le_bytes());
    out.extend_from_slice(head.as_bytes());
    out.extend(blob);
    out
}

/// What a face record says in a file: its surface and its parameters, the builder and line that
/// made it, and the boolean that brought it in.
pub fn face_json(f: &Face) -> Value {
    let v = |p: V3| json!([r9(p.x), r9(p.y), r9(p.z)]);
    let mut out = match f.surface {
        Surface::Plane { p, n } => json!({"p": v(p), "n": v(n)}),
        Surface::Cylinder { p, d, r } => json!({"p": v(p), "d": v(d), "r": r9(r)}),
        Surface::Cone { p, d, r, slope } => json!({"p": v(p), "d": v(d), "r": r9(r), "slope": r9(slope)}),
        Surface::Sphere { c, r } => json!({"c": v(c), "r": r9(r)}),
        Surface::Torus { c, d, major, minor } => json!({"c": v(c), "d": v(d), "R": r9(major), "r": r9(minor)}),
        Surface::Free { .. } => json!({}),
    };
    let o = out.as_object_mut().unwrap();
    o.insert("kind".into(), f.surface.kind().into());
    o.insert("op".into(), f.op.into());
    o.insert("src".into(), format!("{}:{}", f.src.file(), f.src.line()).into());
    if let Some(via) = f.via {
        o.insert("via".into(), format!("{} at {}:{}", via.op, via.src.file(), via.src.line()).into());
    }
    out
}

fn r9(x: f64) -> f64 {
    let r = (x * 1e9).round_ties_even() / 1e9;
    if r == 0.0 { 0.0 } else { r }
}

/// A binary glTF with one node per body. Each primitive's triangles run face by face, and
/// `extras.faces` lists per face its first triangle, its count and its record (`face_json`).
pub fn glb_bytes(bodies: &[Body]) -> Vec<u8> {
    let mut blob: Vec<u8> = vec![];
    let mut views = vec![];
    let mut accessors = vec![];
    let mut meshes = vec![];
    let mut nodes = vec![];
    let mut materials = vec![];
    for (bi, b) in bodies.iter().enumerate() {
        let s = b.solid;
        let faces = topo::faces(s);
        let mut order: Vec<u32> = vec![];
        let mut listed = vec![];
        for (f, tris) in faces.tris.iter().enumerate() {
            let mut rec = face_json(&s.faces[faces.record[f] as usize]);
            let o = rec.as_object_mut().unwrap();
            o.insert("first".into(), (order.len() as u64).into());
            o.insert("count".into(), (tris.len() as u64).into());
            listed.push(rec);
            order.extend(tris);
        }
        while blob.len() % 4 != 0 {
            blob.push(0);
        }
        let pos: Vec<[f32; 3]> = s.verts.iter().map(|&p| f32s(p)).collect();
        let (mut lo, mut hi) = ([f32::INFINITY; 3], [f32::NEG_INFINITY; 3]);
        for p in &pos {
            for k in 0..3 {
                lo[k] = lo[k].min(p[k]);
                hi[k] = hi[k].max(p[k]);
            }
        }
        let at = blob.len();
        blob.extend(pos.iter().flatten().flat_map(|x| x.to_le_bytes()));
        views.push(json!({"buffer": 0, "byteOffset": at, "byteLength": blob.len() - at, "target": 34962}));
        accessors.push(json!({"bufferView": views.len() - 1, "componentType": 5126, "count": pos.len(),
                              "type": "VEC3", "min": lo, "max": hi}));
        let at = blob.len();
        blob.extend(order.iter().flat_map(|&t| s.tris[t as usize]).flat_map(|i| i.to_le_bytes()));
        views.push(json!({"buffer": 0, "byteOffset": at, "byteLength": blob.len() - at, "target": 34963}));
        accessors.push(json!({"bufferView": views.len() - 1, "componentType": 5125, "count": 3 * order.len(),
                              "type": "SCALAR"}));
        let mut prim = json!({"attributes": {"POSITION": accessors.len() - 2}, "indices": accessors.len() - 1,
                              "extras": {"faces": listed}});
        if let Some(c) = b.color {
            materials.push(json!({"pbrMetallicRoughness": {"baseColorFactor": [c[0], c[1], c[2], 1.0],
                                                            "metallicFactor": 0.0}}));
            prim["material"] = json!(materials.len() - 1);
        }
        meshes.push(json!({"name": b.name, "primitives": [prim]}));
        nodes.push(json!({"name": b.name, "mesh": bi}));
    }
    let mut gltf = json!({
        "asset": {"version": "2.0", "generator": "hsm-kernel"},
        "scene": 0,
        "scenes": [{"nodes": (0..nodes.len()).collect::<Vec<_>>()}],
        "nodes": nodes,
        "meshes": meshes,
        "accessors": accessors,
        "bufferViews": views,
        "buffers": [{"byteLength": blob.len()}],
    });
    if !materials.is_empty() {
        gltf["materials"] = json!(materials);
    }
    let mut js = serde_json::to_vec(&gltf).unwrap();
    while js.len() % 4 != 0 {
        js.push(b' ');
    }
    while blob.len() % 4 != 0 {
        blob.push(0);
    }
    let total = 12 + 8 + js.len() + 8 + blob.len();
    let mut out = Vec::with_capacity(total);
    out.extend_from_slice(b"glTF");
    out.extend_from_slice(&2u32.to_le_bytes());
    out.extend_from_slice(&(total as u32).to_le_bytes());
    out.extend_from_slice(&(js.len() as u32).to_le_bytes());
    out.extend_from_slice(b"JSON");
    out.extend(js);
    out.extend_from_slice(&(blob.len() as u32).to_le_bytes());
    out.extend_from_slice(b"BIN\0");
    out.extend(blob);
    out
}

fn put(path: &Path, bytes: &[u8]) -> Result<()> {
    std::fs::write(path, bytes).with_context(|| format!("writing {}", path.display()))
}

pub fn write_stl(path: impl AsRef<Path>, solids: &[&Solid]) -> Result<()> {
    put(path.as_ref(), &stl_bytes(solids)?)
}

pub fn write_3mf(path: impl AsRef<Path>, solids: &[&Solid], name: &str) -> Result<()> {
    put(path.as_ref(), &threemf_bytes(solids, name)?)
}

pub fn write_payload(path: impl AsRef<Path>, bodies: &[Body], src: Option<&str>, cut: Option<&Value>) -> Result<()> {
    put(path.as_ref(), &payload_bytes(bodies, src, cut))
}

pub fn write_glb(path: impl AsRef<Path>, bodies: &[Body]) -> Result<()> {
    put(path.as_ref(), &glb_bytes(bodies))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn crc_of_a_known_string() {
        assert_eq!(crc32(b"123456789"), 0xCBF4_3926);
    }
}
