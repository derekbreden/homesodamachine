//! Focused fixtures distinguish material defects from empty gaps and preserve print-source identity.
use super::*;
use hsm_kernel::{
    plane::Plane as Workplane,
    write::{Body, PrintOutput},
};
use std::sync::atomic::{AtomicU64, Ordering};
static NEXT: AtomicU64 = AtomicU64::new(0);

fn block(lo: [f64; 3], hi: [f64; 3]) -> Mesh {
    let [x, y, z] = lo;
    let [a, b, c] = hi;
    Mesh {
        vertices: vec![
            [x, y, z],
            [a, y, z],
            [a, b, z],
            [x, b, z],
            [x, y, c],
            [a, y, c],
            [a, b, c],
            [x, b, c],
        ],
        faces: vec![
            [0, 2, 1],
            [0, 3, 2],
            [4, 5, 6],
            [4, 6, 7],
            [0, 1, 5],
            [0, 5, 4],
            [3, 7, 6],
            [3, 6, 2],
            [0, 4, 7],
            [0, 7, 3],
            [1, 2, 6],
            [1, 6, 5],
        ],
    }
}
fn combine(mut a: Mesh, b: Mesh) -> Mesh {
    let base = a.vertices.len();
    a.vertices.extend(b.vertices);
    a.faces
        .extend(b.faces.into_iter().map(|f| f.map(|i| i + base)));
    a
}
fn data(mesh: Mesh) -> Data {
    Data::new(mesh).unwrap()
}

#[test]
fn thin_measures_material_and_ignores_the_gap_between_parts() {
    let d = data(block([0., 0., 0.], [10., 10., 0.4]));
    let found = thin::find(&d).unwrap();
    assert!(!found.is_empty());
    assert!((-found[0].score - 0.4).abs() < 1e-6, "{}", found[0].line);
    let d = data(combine(
        block([0., 0., 0.], [10., 10., 1.]),
        block([0., 0., 1.3], [10., 10., 2.3]),
    ));
    let found = thin::find(&d).unwrap();
    assert!(!found.is_empty());
    assert!(
        found.iter().all(|f| -f.score >= 0.99),
        "{:?}",
        found.iter().map(|f| &f.line).collect::<Vec<_>>()
    );
}

#[test]
fn planar_classes_find_a_step_strip_ceiling_and_small_ledge() {
    let d = data(combine(
        block([0., 0., 0.], [10., 10., 1.]),
        block([0., 0., 1.], [5., 10., 1.25]),
    ));
    assert!(!planes::find(&d, "step", 1., 0.).unwrap().is_empty());
    let d = data(block([0., 0., 0.], [0.5, 10., 5.]));
    assert!(!planes::find(&d, "sliver", 1., 0.).unwrap().is_empty());
    let d = data(combine(
        block([0., 0., 0.], [10., 10., 1.]),
        block([0., 0., 5.], [10., 10., 6.]),
    ));
    assert!(!planes::find(&d, "ceiling", 1., 0.).unwrap().is_empty());
    let d = data(combine(
        block([0., 0., 0.], [10., 10., 1.]),
        block([0., 0., 5.], [2., 5., 6.]),
    ));
    assert!(!planes::find(&d, "ledge", 1., 0.).unwrap().is_empty());
}

#[test]
fn bump_requires_a_raised_patch_returning_to_the_flat_on_both_sides() {
    let profile = [
        [-5., 0.],
        [-2., 0.],
        [-1., 0.15],
        [0., 0.25],
        [1., 0.15],
        [2., 0.],
        [5., 0.],
    ];
    let vertices = profile
        .iter()
        .flat_map(|p| [[p[0], 0., p[1]], [p[0], 10., p[1]]])
        .collect();
    let faces = (0..profile.len() - 1)
        .flat_map(|i| {
            let a = 2 * i;
            [[a, a + 2, a + 3], [a, a + 3, a + 1]]
        })
        .collect();
    let d = data(Mesh { vertices, faces });
    let found = planes::find(&d, "bump", 1., 0.).unwrap();
    assert!(!found.is_empty());
    assert!(found[0].line.contains("0.250 mm"));
}

#[test]
fn collapsed_triangles_never_produce_nan_findings() {
    let mut mesh = block([0., 0., 0.], [0.5, 10., 5.]);
    mesh.faces.push([0, 0, 1]);
    let d = data(mesh);
    for class in CLASSES {
        let found = if class == "thin" {
            thin::find(&d)
        } else {
            planes::find(&d, class, 1., 0.)
        }
        .unwrap();
        assert!(
            found
                .iter()
                .all(|f| f.score.is_finite() && !f.line.contains("NaN"))
        );
        serde_json::to_string(&found).unwrap();
    }
}

#[test]
fn source_records_require_the_exact_stl_binding() -> Result<()> {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .ancestors()
        .nth(3)
        .unwrap();
    let dir = root.join(format!(
        ".cache/runs/native-lint-test-{}-{}",
        std::process::id(),
        NEXT.fetch_add(1, Ordering::Relaxed)
    ));
    std::fs::create_dir_all(&dir)?;
    let stl = dir.join("part.stl");
    let model = dir.join("part.step.npz");
    let solid = Workplane::XY.cuboid(0.5, 10., 5.);
    let bodies = [Body {
        name: "part",
        color: None,
        solid: &solid,
    }];
    let print = PrintOutput::new(&bodies);
    std::fs::write(&stl, print.stl_bytes())?;
    std::fs::write(&model, print.model_bytes(&bodies, "part.stl", None)?)?;
    let options = Options {
        classes: vec!["sliver".into()],
        sources: Some(model),
        ..Options::default()
    };
    let report = review(&stl, &options)?;
    assert!(
        report.source_binding.starts_with("bound STL"),
        "{}",
        report.source_binding
    );
    assert!(!report.findings["sliver"].is_empty());
    assert!(
        report.findings["sliver"]
            .iter()
            .any(|f| f.sources.as_ref().unwrap().iter().any(|r| r["src"]
                .as_str()
                .is_some_and(|src| src.contains("tests.rs"))))
    );
    let mut bytes = std::fs::read(&stl)?;
    bytes[0] ^= 1;
    std::fs::write(&stl, bytes)?;
    let report = review(&stl, &options)?;
    assert!(report.source_binding.contains("stale STL binding"));
    assert!(
        report.findings["sliver"]
            .iter()
            .all(|f| f.sources == Some(vec![Value::Null]))
    );
    std::fs::remove_dir_all(dir)?;
    Ok(())
}

#[test]
fn answer_points_exclude_normals_and_keep_both_edge_ends() {
    let points = pick_points(
        "face: plane · n x=0 y=0 z=1 · thru x=5 y=6 z=7\nedge: x=2 y=3 z=4 → x=8 y=9 z=10 · dir x=1 y=0 z=0\nclick: x=11 y=12 z=13",
    );
    assert_eq!(
        points,
        vec![
            v3(5., 6., 7.),
            v3(2., 3., 4.),
            v3(8., 9., 10.),
            v3(11., 12., 13.)
        ]
    );
}
