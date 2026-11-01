//! A laser outline read from a DXF against what CadQuery's `importDXF` reads from the same file
//! (`dxf_reference.py`): the same holes, the face's area, its bounds within LINEAR, and the plate
//! extruded from it within LINEAR × its surface area of OCCT's volume.
use hsm_kernel::*;
use serde_json::Value;

#[test]
fn an_outline_matches_cadquery() {
    let want: Value = serde_json::from_str(include_str!("dxf_reference.json")).unwrap();
    let f = |k: &str| want[k].as_f64().unwrap();
    let profile = dxf::outline(include_str!("fixtures/outline.dxf")).unwrap();
    assert_eq!(profile.holes.len() as u64, want["holes"].as_u64().unwrap());
    assert!((profile.area() - f("area")).abs() < 1e-6, "area {} against CadQuery's {}", profile.area(), f("area"));
    let plate = Plane::XY.extrude(&profile, f("thickness")).unwrap();
    plate.check().unwrap();
    let b = plate.bounds();
    let bbox: Vec<f64> = want["bbox"].as_array().unwrap().iter().map(|x| x.as_f64().unwrap()).collect();
    let off = [b.min.x - bbox[0], b.min.y - bbox[1], b.max.x - bbox[2], b.max.y - bbox[3]].iter().fold(0.0f64, |m, d| m.max(d.abs()));
    println!("area {:.9} against {:.9}, bounds {off:.1e} off, volume {:.6} against {:.6}", profile.area(), f("area"), plate.volume(), f("volume"));
    assert!(off <= LINEAR, "bounds {b:?} against CadQuery's {bbox:?}");
    assert!((plate.volume() - f("volume")).abs() <= LINEAR * plate.area(), "volume {} against {}", plate.volume(), f("volume"));
}

#[test]
fn an_open_outline_is_refused() {
    let text = "0\nSECTION\n2\nENTITIES\n0\nLINE\n8\n0\n10\n0.0\n20\n0.0\n11\n1.0\n21\n0.0\n0\nLINE\n8\n0\n10\n1.0\n20\n0.0\n11\n1.0\n21\n1.0\n0\nENDSEC\n0\nEOF\n";
    let err = dxf::outline(text).unwrap_err();
    assert!(format!("{err:#}").contains("open at"), "{err:#}");
}
