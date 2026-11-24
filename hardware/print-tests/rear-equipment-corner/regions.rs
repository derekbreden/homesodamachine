//! A receiver crop keeps the manufacturing regions of the enclosure surfaces it retains.
use serde_json::{Value, json};

fn clip_bounds(row: &mut Value, key: &str, lo: [f64; 3], hi: [f64; 3]) -> bool {
    let Some(b) = row.get(key).and_then(Value::as_array) else { return true; };
    let mut b: Vec<f64> = b.iter().filter_map(Value::as_f64).collect();
    if b.len() != 6 { return false; }
    for k in 0..3 {
        b[2*k] = b[2*k].max(lo[k]);
        b[2*k+1] = b[2*k+1].min(hi[k]);
        if b[2*k] >= b[2*k+1] { return false; }
    }
    row[key] = json!(b);
    true
}

pub fn crop_regions(native: &Value, producer: &str, sha: &str, lo: [f64; 3], hi: [f64; 3],
                    include: impl Fn(&Value) -> bool) -> Value {
    let mut regions = json!({"producer":producer, "source_stl_sha256":sha,
                             "boundary_overlap_mm":native["boundary_overlap_mm"]});
    for key in ["support_free_regions", "support_regions", "bridge_regions"] {
        let rows: Vec<Value> = native[key].as_array().into_iter().flatten().filter_map(|r| {
            if !include(r) { return None; }
            let mut row = r.clone();
            (clip_bounds(&mut row, "bounds_source_mm", lo, hi)
             && clip_bounds(&mut row, "blocking_bounds_source_mm", lo, hi)).then_some(row)
        }).collect();
        regions[key] = json!(rows);
    }
    regions
}
