//! Construction identity survives ordinary edits, booleans and retained model round trips.
use anyhow::Result;
use hsm_kernel::{Body, Solid, feature::{Feature, intern}, model_bytes, v3};

fn identity(id: &str) -> &'static Feature {
    intern(Feature { id: id.into(), label: id.into(), parent: None,
        related: vec!["relay-2".into()], source: "feature-test".into() })
}

#[test]
fn a_mount_keeps_its_identity_through_move_resize_cut_and_import() -> Result<()> {
    let wall = Solid::cuboid(v3(-5., -5., -2.), v3(5., 5., 0.));
    for (radius, shift) in [(2., 0.), (2.5, 1.)] {
        let tag = identity("relay-2-mount");
        let boss = Solid::cylinder(v3(shift, 0., -1.), hsm_kernel::V3::Z, radius, 5.)?.with_feature(tag);
        let bore = Solid::cylinder(v3(shift, 0., 1.), hsm_kernel::V3::Z, 0.5, 4.)?.with_feature(tag);
        let part = wall.union(&boss)?.cut(&bore)?.translate(v3(0., 3., 0.));
        assert!(part.faces().iter().any(|f| f.feature.is_none()));
        assert!(part.faces().iter().filter(|f| f.feature.is_some()).all(|f| f.feature == Some(tag)));
        let bytes = model_bytes(&[Body { name: "quadrant", color: None, solid: &part }]);
        let imported = hsm_kernel::import::model_bodies(&bytes)?.pop().unwrap().solid;
        assert!(imported.faces().iter().any(|f| f.feature == Some(tag)));
        assert_eq!(part.volume(), imported.volume());
    }
    Ok(())
}
