//! STEP and model files read back as the kernel wrote them: the triangles, names and colours a
//! reader finds in each, and the same bytes from the same bodies.
use hsm_kernel::*;
use serde_json::Value;
use std::collections::BTreeMap;

fn solids() -> anyhow::Result<(Solid, Solid)> {
    Ok((Plane::XY.cuboid(20.0, 10.0, 5.0), Plane::XY.at(v3(40.0, 0.0, 0.0)).cylinder(6.0, 10.0)?))
}

/// The data section's entities, by id.
fn entities(text: &str) -> BTreeMap<usize, String> {
    let data = &text[text.find("DATA;\n").unwrap() + 6..text.find("ENDSEC;\nEND-ISO").unwrap()];
    data.split(";\n")
        .filter(|s| !s.is_empty())
        .map(|s| {
            let (id, body) = s.split_once(" = ").unwrap();
            (id[1..].parse().unwrap(), body.to_string())
        })
        .collect()
}

/// The numbers of the rows of an entity's last list, as rows.
fn rows(body: &str) -> Vec<Vec<f64>> {
    let list = &body[body.rfind(",(").unwrap() + 2..body.rfind("))").unwrap() + 1];
    list.split("),")
        .map(|r| r.trim().trim_matches(['(', ')']).split(',').map(|x| x.parse().unwrap()).collect())
        .collect()
}

/// Each triangulated surface set's enclosed volume.
fn volumes(e: &BTreeMap<usize, String>) -> Vec<f64> {
    e.values()
        .filter_map(|b| b.strip_prefix("TRIANGULATED_SURFACE_SET('',#"))
        .map(|b| {
            let points = rows(&e[&b[..b.find(',').unwrap()].parse::<usize>().unwrap()]);
            rows(b)
                .iter()
                .map(|t| {
                    let [a, b, c] = [0, 1, 2].map(|k| {
                        let p = &points[t[k] as usize - 1];
                        v3(p[0], p[1], p[2])
                    });
                    a.dot(b.cross(c)) / 6.0
                })
                .sum()
        })
        .collect()
}

fn named<'a>(e: &'a BTreeMap<usize, String>, kind: &str) -> Vec<&'a str> {
    e.values().filter_map(|b| b.strip_prefix(kind)).map(|b| &b[1..b[1..].find('\'').unwrap() + 1]).collect()
}

/// Every reference an entity makes is to an entity the file has.
fn closed(e: &BTreeMap<usize, String>) {
    for (id, body) in e {
        for r in body.split('#').skip(1) {
            let n: usize = r[..r.find(|c: char| !c.is_ascii_digit()).unwrap_or(r.len())].parse().unwrap();
            assert!(e.contains_key(&n), "#{id} names #{n}, which the file does not hold");
        }
    }
}

#[test]
fn one_body_is_its_product() -> anyhow::Result<()> {
    let (block, _) = solids()?;
    let body = Body { name: "block", color: Some([0.5, 0.25, 0.125]), solid: &block };
    let bytes = step_bytes(&[body], "unused")?;
    assert_eq!(bytes, step_bytes(&[body], "unused")?);
    let text = String::from_utf8(bytes)?;
    assert!(text[..200].contains(step::MARK));
    let e = entities(&text);
    closed(&e);
    assert_eq!(named(&e, "PRODUCT("), ["block"]);
    let [v] = volumes(&e)[..] else { panic!("one surface set") };
    assert!((v - 1000.0).abs() < 1e-9, "the surface set encloses {v}");
    assert_eq!(e.values().filter(|b| b.starts_with("COLOUR_RGB(")).count(), 1);
    Ok(())
}

#[test]
fn bodies_stand_under_an_assembly() -> anyhow::Result<()> {
    let (block, pin) = solids()?;
    let bodies = [
        Body { name: "block", color: Some([0.5, 0.25, 0.125]), solid: &block },
        Body { name: "pin", color: None, solid: &pin },
    ];
    let text = String::from_utf8(step_bytes(&bodies, "pair")?)?;
    let e = entities(&text);
    closed(&e);
    assert_eq!(named(&e, "PRODUCT("), ["pair", "block", "pin"]);
    assert_eq!(e.values().filter(|b| b.starts_with("NEXT_ASSEMBLY_USAGE_OCCURRENCE(")).count(), 2);
    assert_eq!(e.values().filter(|b| b.starts_with("COLOUR_RGB(")).count(), 1);
    let got = volumes(&e);
    for (v, s) in got.iter().zip([&block, &pin]) {
        let want = s.simplified()?.volume();
        assert!((v - want).abs() <= want * 1e-6, "a surface set encloses {v} where its solid holds {want}");
    }
    Ok(())
}

/// The stored entries of a zip, by name.
fn stored(zip: &[u8]) -> Vec<(String, &[u8])> {
    let mut out = vec![];
    let mut at = 0;
    while zip[at..at + 4] == [0x50, 0x4b, 0x03, 0x04] {
        let short = |o: usize| u16::from_le_bytes([zip[at + o], zip[at + o + 1]]) as usize;
        let size = u32::from_le_bytes(zip[at + 18..at + 22].try_into().unwrap()) as usize;
        let start = at + 30 + short(26) + short(28);
        out.push((String::from_utf8(zip[at + 30..at + 30 + short(26)].to_vec()).unwrap(), &zip[start..start + size]));
        at = start + size;
    }
    out
}

/// An `.npy` array's header and data.
fn npy(data: &[u8]) -> (String, &[u8]) {
    assert_eq!(&data[..8], b"\x93NUMPY\x01\x00");
    let n = u16::from_le_bytes([data[8], data[9]]) as usize;
    assert_eq!((10 + n) % 64, 0);
    (String::from_utf8(data[10..10 + n].to_vec()).unwrap(), &data[10 + n..])
}

#[test]
fn model_holds_the_solids() -> anyhow::Result<()> {
    let (block, pin) = solids()?;
    let bodies = [
        Body { name: "block", color: Some([0.5, 0.25, 0.125]), solid: &block },
        Body { name: "pin", color: None, solid: &pin },
    ];
    let bytes = model_bytes(&bodies);
    assert_eq!(bytes, model_bytes(&bodies));
    let entries = stored(&bytes);
    let names: Vec<&str> = entries.iter().map(|(n, _)| n.as_str()).collect();
    assert_eq!(names, ["V0.npy", "T0.npy", "F0.npy", "V1.npy", "T1.npy", "F1.npy", "names.npy", "colors.npy", "records.npy"]);
    for (i, s) in [&block, &pin].into_iter().enumerate() {
        let (head, v) = npy(entries[3 * i].1);
        assert!(head.contains(&format!("'descr': '<f8', 'fortran_order': False, 'shape': ({}, 3)", s.verts().len())));
        let v: Vec<f64> = v.chunks(8).map(|c| f64::from_le_bytes(c.try_into().unwrap())).collect();
        assert_eq!(v, s.verts().iter().flat_map(|p| p.to_array()).collect::<Vec<_>>());
        let (_, t) = npy(entries[3 * i + 1].1);
        let t: Vec<u32> = t.chunks(4).map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect();
        assert_eq!(t, s.tris().iter().flatten().copied().collect::<Vec<_>>());
        let (_, f) = npy(entries[3 * i + 2].1);
        let f: Vec<u32> = f.chunks(4).map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect();
        assert_eq!(f, s.face_of());
    }
    let json = |k: usize| -> Value { serde_json::from_slice(npy(entries[k].1).1).unwrap() };
    assert_eq!(json(6), serde_json::json!(["block", "pin"]));
    assert_eq!(json(7), serde_json::json!([[0.5, 0.25, 0.125], null]));
    let records = json(8);
    assert_eq!(records[0].as_array().unwrap().len(), block.faces().len());
    assert_eq!(records[1].as_array().unwrap().len(), pin.faces().len());
    assert!(records[1].as_array().unwrap().iter().any(|r| r["kind"] == "CYLINDER"));
    Ok(())
}
