//! Booleans against Manifold run plainly on the same operands: the kernel's result has Manifold's
//! volume and area, its surface lies on Manifold's, and every face of it names the operand face it
//! came from.
mod common;
use common::hausdorff;
use hsm_kernel::*;
use manifold_csg::{Manifold, OpType};
use std::time::Instant;

const Z: V3 = V3::Z;

fn plain(s: &Solid) -> Manifold {
    let props: Vec<f64> = s.verts().iter().flat_map(|p| [p.x, p.y, p.z]).collect();
    let tris: Vec<u64> = s.tris().iter().flat_map(|t| t.map(u64::from)).collect();
    Manifold::from_mesh_f64(&props, 3, &tris).unwrap()
}

fn mesh(m: &Manifold) -> (Vec<V3>, Vec<[u32; 3]>) {
    let (props, n, tris) = m.to_mesh_f64();
    let verts = props.chunks(n).map(|c| v3(c[0], c[1], c[2])).collect();
    let tris = tris.chunks(3).map(|t| [t[0] as u32, t[1] as u32, t[2] as u32]).collect();
    (verts, tris)
}

fn oracle(operands: &[&Solid], op: OpType) -> Manifold {
    let ms: Vec<Manifold> = operands.iter().map(|s| plain(s)).collect();
    Manifold::batch_boolean(&ms, op)
}

/// The kernel's result is closed and is Manifold's: volume and area to a part in 10⁹, every
/// sampled point of either surface within 10⁻⁷ mm of the other.
fn agrees(name: &str, got: &Solid, want: &Manifold) {
    got.check().unwrap_or_else(|e| panic!("{name}: {e}"));
    let (wv, wt) = mesh(want);
    let (v, a) = (got.volume(), got.area());
    let (mv, ma) = (want.volume(), want.surface_area());
    let h = hausdorff((got.verts(), got.tris()), (&wv, &wt));
    println!(
        "{name:18} volume {v:12.6} (Manifold {mv:12.6})  area {a:11.6} (Manifold {ma:11.6})  apart {h:.1e}  {} faces",
        got.faces().len()
    );
    assert!((v - mv).abs() <= 1e-9 * mv.abs().max(1.0), "{name}: volume {v} against Manifold's {mv}");
    assert!((a - ma).abs() <= 1e-9 * ma.abs().max(1.0), "{name}: area {a} against Manifold's {ma}");
    assert!(h <= 1e-7, "{name}: the surfaces lie {h:e} apart");
}

fn pins() -> Vec<Solid> {
    (0..10)
        .flat_map(|i| (0..6).map(move |j| (i, j)))
        .map(|(i, j)| Solid::cylinder(v3(5.0 + 10.0 * i as f64, 5.0 + 10.0 * j as f64, -1.0), Z, 2.5, 12.0).unwrap())
        .collect()
}

#[test]
fn union_cut_intersect() -> anyhow::Result<()> {
    let cube = Plane::XY.cuboid(10.0, 10.0, 10.0);
    let moved = cube.translate(v3(5.0, 5.0, 5.0));
    agrees("union_boxes", &cube.union(&moved)?, &oracle(&[&cube, &moved], OpType::Add));
    let plate = Plane::XY.cuboid(20.0, 20.0, 10.0);
    let bore = Solid::cylinder(v3(0.0, 0.0, -6.0), Z, 4.0, 12.0)?;
    agrees("cut_bore", &plate.cut(&bore)?, &oracle(&[&plate, &bore], OpType::Subtract));
    let ball = Solid::sphere(V3::ZERO, 6.5)?;
    agrees("intersect_ball", &cube.intersect(&ball)?, &oracle(&[&cube, &ball], OpType::Intersect));
    Ok(())
}

/// Sixty holes in one cut: the block's six faces and the sixty bores, each bore a cylinder
/// brought in by the cut.
#[test]
fn sixty_holes() -> anyhow::Result<()> {
    let block = Solid::cuboid(V3::ZERO, v3(100.0, 60.0, 10.0));
    let pins = pins();
    let t = Instant::now();
    let holed = block.cut_all(&pins)?;
    let kernel = t.elapsed();
    let mut operands = vec![&block];
    operands.extend(pins.iter());
    let t = Instant::now();
    let want = oracle(&operands, OpType::Subtract);
    let _ = want.num_tri();
    let manifold = t.elapsed();
    agrees("holes_60", &holed, &want);
    println!("holes_60: the kernel's cut {kernel:.2?}, Manifold's alone {manifold:.2?}");
    let bores = holed.faces().iter().filter(|f| matches!(f.surface, Surface::Cylinder { .. })).collect::<Vec<_>>();
    assert_eq!(holed.faces().len(), 66);
    assert_eq!(bores.len(), 60);
    let here = std::panic::Location::caller();
    for f in &bores {
        assert_eq!(f.op, "cylinder");
        let via = f.via.expect("a bore names the cut that brought it in");
        assert_eq!(via.op, "cut");
        assert_eq!(via.src.file(), here.file());
    }
    let walls = holed.faces().iter().filter(|f| f.op == "box" && f.via.is_none()).count();
    assert_eq!(walls, 6);
    Ok(())
}

/// Two boxes sharing a face are one box, the shared face gone.
#[test]
fn stacked() -> anyhow::Result<()> {
    let low = Solid::cuboid(V3::ZERO, v3(10.0, 10.0, 10.0));
    let high = Solid::cuboid(v3(0.0, 0.0, 10.0), v3(10.0, 10.0, 20.0));
    let both = low.union(&high)?;
    agrees("stacked", &both, &oracle(&[&low, &high], OpType::Add));
    assert_eq!(both.components().len(), 1);
    assert!((both.volume() - 2000.0).abs() < 1e-9);
    assert!((both.area() - 1000.0).abs() < 1e-9);
    Ok(())
}

/// A pocket whose floor is inside the block and whose mouth is flush with its top face.
#[test]
fn flush_cut() -> anyhow::Result<()> {
    let block = Solid::cuboid(V3::ZERO, v3(10.0, 10.0, 10.0));
    let pocket = Solid::cuboid(v3(2.0, 2.0, 5.0), v3(8.0, 8.0, 10.0));
    let cut = block.cut(&pocket)?;
    agrees("flush_cut", &cut, &oracle(&[&block, &pocket], OpType::Subtract));
    assert!((cut.volume() - 820.0).abs() < 1e-9);
    assert!((cut.area() - (600.0 + 4.0 * 6.0 * 5.0)).abs() < 1e-9);
    Ok(())
}

/// A bore filled again by a pin of its own radius and the plate's thickness: the plate whole.
#[test]
fn refilled_bore() -> anyhow::Result<()> {
    let plate = Solid::cuboid(v3(-10.0, -10.0, 0.0), v3(10.0, 10.0, 4.0));
    let bore = Solid::cylinder(v3(0.0, 0.0, -1.0), Z, 3.0, 6.0)?;
    let pin = Solid::cylinder(V3::ZERO, Z, 3.0, 4.0)?;
    let holed = plate.cut(&bore)?;
    let filled = holed.union(&pin)?;
    filled.check()?;
    let ours = (filled.volume(), filled.area(), filled.components().len());
    let want = oracle(&[&holed, &pin], OpType::Add);
    println!(
        "refilled_bore: volume {:.9} area {:.9} in {} pieces; Manifold alone {:.9} area {:.9} in {} pieces",
        ours.0,
        ours.1,
        ours.2,
        want.volume(),
        want.surface_area(),
        want.decompose().len()
    );
    assert!((ours.0 - plate.volume()).abs() < 1e-6, "volume {} against the plate's {}", ours.0, plate.volume());
    assert_eq!(ours.2, 1);
    Ok(())
}

/// A post set on a shelf by moving it up a thickness computed as 0.1 + 0.2: its foot lands
/// 2 × 10⁻¹⁰ mm above the shelf's top, which the shelf's builder put on the 2⁻³⁰ grid. One
/// coordinate to the union, so one solid; Manifold alone leaves two.
#[test]
fn one_coordinate() -> anyhow::Result<()> {
    let shelf = Solid::cuboid(V3::ZERO, v3(10.0, 10.0, 0.3));
    let post = Solid::cuboid(V3::ZERO, v3(1.0, 1.0, 5.0)).translate(v3(0.0, 0.0, 0.1 + 0.2));
    let gap = post.bounds().min.z - shelf.bounds().max.z;
    assert!(gap > 0.0 && gap < FUZZ, "the post stands {gap:e} off the shelf");
    let joined = shelf.union(&post)?;
    joined.check()?;
    assert_eq!(joined.components().len(), 1);
    assert_eq!(oracle(&[&shelf, &post], OpType::Add).decompose().len(), 2);
    println!("one_coordinate: a {gap:.1e} mm gap closed; {} faces", joined.faces().len());
    Ok(())
}

/// A plane split: the parts above and below, each closed by a face of the plane whose normal
/// points out of it.
#[test]
fn split() -> anyhow::Result<()> {
    let cube = Solid::cuboid(V3::ZERO, v3(10.0, 10.0, 10.0));
    let (above, below) = cube.split(&Plane::XY.at(v3(0.0, 0.0, 3.0)))?;
    let (up, down) = plain(&cube).split_by_plane([0.0, 0.0, 1.0], 3.0);
    agrees("split_above", &above, &up);
    agrees("split_below", &below, &down);
    let cap = |s: &Solid| -> V3 {
        let f: Vec<&Face> = s.faces().iter().filter(|f| f.via.is_some_and(|v| v.op == "split")).collect();
        assert_eq!(f.len(), 1);
        match f[0].surface {
            Surface::Plane { n, .. } => n,
            _ => panic!("the split face is no plane"),
        }
    };
    assert_eq!(cap(&above), -Z);
    assert_eq!(cap(&below), Z);
    Ok(())
}
