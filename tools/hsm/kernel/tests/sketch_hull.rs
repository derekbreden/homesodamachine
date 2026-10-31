//! Hulls of circles and points against CadQuery's `Sketch.hull` for the same sets
//! (`sketch_hull_reference.py`): the same edges in the same order, lines to the same ends and arcs
//! to the same centres, radii and parameters.
use hsm_kernel::*;
use serde_json::Value;

fn f(x: &Value) -> f64 {
    x.as_f64().unwrap()
}

#[test]
fn hulls_match_cadquery() {
    let all: Value = serde_json::from_str(include_str!("sketch_hull_reference.json")).unwrap();
    let mut worst = 0.0f64;
    for (name, case) in all.as_object().unwrap() {
        let mut wrapped: Vec<Wrapped> = case["circles"]
            .as_array()
            .unwrap()
            .iter()
            .map(|c| Wrapped::Circle { c: v2(f(&c[0]), f(&c[1])), r: f(&c[2]) })
            .collect();
        wrapped.extend(case["points"].as_array().unwrap().iter().map(|p| Wrapped::Point(v2(f(&p[0]), f(&p[1])))));
        let got = hull_edges(&wrapped).unwrap_or_else(|e| panic!("{name}: {e}"));
        let want = case["edges"].as_array().unwrap();
        assert_eq!(got.len(), want.len(), "{name}: {got:?}");
        for (k, (g, w)) in got.iter().zip(want).enumerate() {
            let off = match (g, w.get("line"), w.get("arc")) {
                (HullEdge::Line { a, b }, Some(l), None) => {
                    let (wa, wb) = (v2(f(&l[0][0]), f(&l[0][1])), v2(f(&l[1][0]), f(&l[1][1])));
                    (*a - wa).norm().max((*b - wb).norm())
                }
                (HullEdge::Arc { c, r, t0, t1, .. }, None, Some(a)) => {
                    let wc = v2(f(&a["c"][0]), f(&a["c"][1]));
                    (*c - wc).norm().max((r - f(&a["r"])).abs()).max((t0 - f(&a["t0"])).abs()).max((t1 - f(&a["t1"])).abs())
                }
                _ => panic!("{name}: edge {k} is {g:?}, CadQuery's {w}"),
            };
            assert!(off < 1e-9, "{name}: edge {k} {g:?} lies {off:e} off CadQuery's {w}");
            worst = worst.max(off);
        }
    }
    println!("{} hulls, every edge within {worst:.1e} of CadQuery's", all.as_object().unwrap().len());
}
