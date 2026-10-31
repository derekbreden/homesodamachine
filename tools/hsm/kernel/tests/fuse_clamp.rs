//! The fuse clamp rebuilt on the kernel against the part OCCT published: volume within 0.01 % of
//! the published STEP's, surface within 0.005 mm of the published STL's both ways, and a payload
//! hsm-geometry reads back as the kernel wrote it.
#[path = "../examples/fuse_clamp.rs"]
mod fuse_clamp;
mod common;
use common::{hausdorff, occt, read_stl};
use hsm_kernel::*;

#[test]
fn matches_the_published_part() -> anyhow::Result<()> {
    let clamp = fuse_clamp::build()?;
    clamp.check()?;
    let published = occt("fuse_clamp_published");
    let rel = (clamp.volume() - published.volume) / published.volume;
    let (verts, tris) = read_stl(include_bytes!("fixtures/fuse-clamp.stl"));
    let apart = hausdorff((clamp.verts(), clamp.tris()), (&verts, &tris));
    println!(
        "fuse clamp: volume {:.4} against the published {:.4} ({rel:+.2e}), surfaces {apart:.1e} mm apart",
        clamp.volume(),
        published.volume
    );
    assert!(rel.abs() <= 1e-4, "volume {} against the published {}", clamp.volume(), published.volume);
    assert!(apart <= 0.005, "the surfaces lie {apart} mm apart");
    Ok(())
}

#[test]
fn payload_reads_back() -> anyhow::Result<()> {
    let clamp = fuse_clamp::build()?;
    let body = Body { name: "fuse-clamp", color: Some([0.02, 0.02, 0.02]), solid: &clamp };
    let bytes = payload_bytes(&[body], None, None);
    let payload = hsm_geometry::payload::decode(&bytes)?;
    assert_eq!(payload.meshes.len(), 1);
    let m = &payload.meshes[0];
    assert_eq!(m.name, "fuse-clamp");
    assert_eq!(m.color, Some([0.02, 0.02, 0.02]));
    assert_eq!(m.shape.indices().len(), clamp.tris().len());
    assert_eq!(m.faces.len(), hsm_kernel::topo::faces(&clamp).tris.len());
    assert_eq!(m.faces.last().unwrap()[1] as usize + 1, clamp.tris().len());
    let b = clamp.bounds();
    let aabb = m.shape.local_aabb();
    for (got, want) in [(aabb.mins.x, b.min.x), (aabb.mins.y, b.min.y), (aabb.mins.z, b.min.z)]
        .into_iter()
        .chain([(aabb.maxs.x, b.max.x), (aabb.maxs.y, b.max.y), (aabb.maxs.z, b.max.z)])
    {
        assert!((got - want).abs() < 1e-5, "payload bounds {got} against the solid's {want}");
    }
    assert!(clamp.faces().iter().all(|f| f.src.file().ends_with("examples/fuse_clamp.rs")));
    Ok(())
}
