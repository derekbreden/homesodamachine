//! Output-unit conversion and the countertop's existing exported-STL reading.
use anyhow::{Result, bail};
use hsm_documents::format_number;
use serde_json::{Value, json};
use std::{collections::HashMap, fs};

#[derive(serde::Serialize)]
struct CountertopInfo {
    status: &'static str,
    envelope_mm: Vec<f64>,
    clear_under_slab_mm: Value,
    volume_cm3: f64,
}

fn stl(path: &str) -> Result<(usize, usize, bool, bool, usize)> {
    let raw = fs::read(path)?;
    if raw.len() < 84 || (raw.len() - 84) % 50 != 0 {
        bail!("Malformed binary STL {path}")
    }
    let mut vertices = HashMap::new();
    let mut edges: HashMap<(usize, usize), Vec<(usize, bool)>> = HashMap::new();
    let count = (raw.len() - 84) / 50;
    let mut parents = (0..count).collect::<Vec<_>>();
    fn root(parents: &mut [usize], mut x: usize) -> usize {
        while parents[x] != x {
            let p = parents[x];
            parents[x] = parents[p];
            x = parents[x];
        }
        x
    }
    for (triangle, row) in raw[84..].chunks_exact(50).enumerate() {
        let mut ids = [0; 3];
        for (i, id) in ids.iter_mut().enumerate() {
            let mut key = [0; 3];
            for (axis, bit) in key.iter_mut().enumerate() {
                let at = 12 + 12 * i + 4 * axis;
                let x = f32::from_le_bytes(row[at..at + 4].try_into()?);
                *bit = if x == 0.0 { 0 } else { x.to_bits() };
            }
            let next = vertices.len();
            *id = *vertices.entry(key).or_insert(next);
        }
        for (a, b) in [(ids[0], ids[1]), (ids[1], ids[2]), (ids[2], ids[0])] {
            let key = (a.min(b), a.max(b));
            edges.entry(key).or_default().push((triangle, a < b));
        }
    }
    let mut winding = true;
    let mut closed = true;
    let mut loose = 0;
    for rows in edges.values() {
        if rows.len() != 2 {
            closed = false;
        }
        if rows.len() > 2 {
            loose += 1;
        }
        if rows.len() == 2 && rows[0].1 == rows[1].1 {
            winding = false;
        }
        for &(b, _) in rows.iter().skip(1) {
            let a = root(&mut parents, rows[0].0);
            let b = root(&mut parents, b);
            parents[b] = a;
        }
    }
    let mut roots = std::collections::HashSet::new();
    for i in 0..count {
        roots.insert(root(&mut parents, i));
    }
    Ok((count, loose, closed, winding, roots.len()))
}
pub(super) fn request(v: &Value) -> Result<Value> {
    let body = &v["body"];
    let lo = body
        .get("min")
        .map(crate::point)
        .transpose()?
        .unwrap_or([0.0; 3]);
    let hi = body
        .get("max")
        .map(crate::point)
        .transpose()?
        .unwrap_or([0.0; 3]);
    let span = [hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]];
    let volume = crate::num(body, "volume")? / 1000.0;
    let volume_spec = v["volume_spec"].as_str().unwrap_or(".3f");
    let span_spec = v["span_spec"].as_str().unwrap_or(".2f");
    let mut out = json!({"span":span,"volume_cm3":volume,
        "volume":format_number(volume,volume_spec)?,
        "dimensions":span.into_iter().map(|n|format_number(n,span_spec)).collect::<Result<Vec<_>>>()?});
    if let Some(path) = v["countertop_stl"].as_str() {
        let (facets, loose, closed, winding, components) = stl(path)?;
        if loose != 0 || !closed || !winding || components != 1 {
            bail!(
                "fake-countertop.stl: expected one closed, consistently wound printable body; {loose} non-manifold edges"
            )
        }
        let round =
            |value: f64, spec: &str| -> Result<f64> { Ok(format_number(value, spec)?.parse()?) };
        let info = CountertopInfo {
            status: "CAD checks passed; the print is untested",
            envelope_mm: span
                .into_iter()
                .map(|n| round(n, ".2f"))
                .collect::<Result<Vec<_>>>()?,
            clear_under_slab_mm: crate::countertop(&json!({}))?["values"]["clear_height"].clone(),
            volume_cm3: round(volume, ".1f")?,
        };
        out["countertop_info_json"] = json!(serde_json::to_string_pretty(&info)?);
        out["countertop_info"] = serde_json::to_value(info)?;
        out["countertop_line"] = json!(format!(
            "-> fake-countertop.step, fake-countertop.stl: {} cm³, {facets} facets",
            format_number(volume, ".1f")?
        ));
        out["facets"] = json!(facets);
    }
    if v["shop"].as_bool().unwrap_or(false) {
        let dimensions = out["dimensions"].as_array().unwrap();
        let name = body["name"].as_str().unwrap_or("");
        let mut lines = vec![format!(
            "   {name}: {} x {} x {} mm",
            dimensions[0].as_str().unwrap(),
            dimensions[1].as_str().unwrap(),
            dimensions[2].as_str().unwrap()
        )];
        if let Some(overlap) = body["dock_overlap_mm3"].as_f64() {
            lines.push(format!(
                "   {name} on the dock: {} mm^3 overlap, {} mm gap bound",
                format_number(overlap, ".4f")?,
                format_number(crate::num(body, "dock_gap_upper_bound_mm")?, ".4f")?
            ));
        }
        out["lines"] = json!(lines);
    }
    Ok(out)
}
