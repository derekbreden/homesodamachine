//! The same models write the same bytes: built twice in one process, and again in a process of
//! their own, every writer's output hashes alike.
#[allow(dead_code)]
#[path = "../../../../hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.rs"]
mod fuse_clamp;
use hsm_kernel::*;
use sha2::{Digest, Sha256};
use std::process::Command;

const AGAIN: &str = "HSM_KERNEL_IDENTICAL_AGAIN";

fn models() -> anyhow::Result<Vec<(&'static str, Solid)>> {
    let block = Solid::cuboid(V3::ZERO, v3(100.0, 60.0, 10.0));
    let pins: Vec<Solid> = (0..10)
        .flat_map(|i| (0..6).map(move |j| (i, j)))
        .map(|(i, j)| Solid::cylinder(v3(5.0 + 10.0 * i as f64, 5.0 + 10.0 * j as f64, -1.0), V3::Z, 2.5, 12.0))
        .collect::<anyhow::Result<_>>()?;
    let ring = Profile::polygon(&[v2(5.0, 0.0), v2(9.0, 0.0), v2(9.0, 6.0), v2(5.0, 6.0)]);
    let bend = Path::new(v3(-40.0, 0.0, 0.0))
        .line_to(v3(-40.0, 0.0, 20.0))
        .arc_center(v3(-30.0, 0.0, 20.0), v3(-30.0, 0.0, 30.0), V3::Y)?;
    let annulus = Profile::circle(V2::ZERO, 3.0).with_hole(Loop::circle(V2::ZERO, 2.0));
    let sections = [
        Profile::new(Loop::rounded_rect(V2::ZERO, 12.0, 8.0, 2.0)?).place(&Plane::XY.at(v3(0.0, 40.0, 0.0))),
        Profile::new(Loop::rounded_rect(V2::ZERO, 8.0, 6.0, 1.0)?).place(&Plane::XY.at(v3(0.0, 40.0, 9.0))),
    ];
    let arial = Font::find("Arial", Kind::Regular)?;
    Ok(vec![
        ("fuse-clamp", fuse_clamp::build(&part::Numbers::read(concat!(env!("CARGO_MANIFEST_DIR"), "/../../../hardware/printed-parts/refrigeration/fuse-clamp/fuse-clamp.numbers.json"))?)?),
        ("holes-60", block.cut_all(&pins)?),
        ("ball", Solid::sphere(v3(0.0, 0.0, 40.0), 7.0)?),
        ("ring", Solid::torus(v3(40.0, 0.0, 40.0), v3(1.0, 1.0, 0.0), 10.0, 3.0)?),
        ("revolved", Plane::XZ.revolve(&ring, 270.0, v2(0.0, 0.0), v2(0.0, 1.0))?),
        ("drafted", Plane::XY.at(v3(0.0, -40.0, 0.0)).extrude_drafted(&Profile::circle(V2::ZERO, 6.0), 5.0, 10.0)?),
        ("tube", Plane::XY.at(v3(-40.0, 0.0, 0.0)).sweep(&annulus, &bend)?),
        ("lofted", Solid::loft(&sections)?),
        ("label", Plane::XY.at(v3(0.0, 80.0, 0.0)).text(&arial, "HSM 42", 6.0, 1.0, HAlign::Center, VAlign::Center)?),
    ])
}

/// Each writer's SHA-256 over every model.
fn digests() -> anyhow::Result<String> {
    let models = models()?;
    let solids: Vec<&Solid> = models.iter().map(|(_, s)| s).collect();
    let bodies: Vec<Body> = models.iter().map(|(name, solid)| Body { name, color: None, solid }).collect();
    let files = [
        ("stl", stl_bytes(&solids)?),
        ("3mf", threemf_bytes(&solids, "corpus")?),
        ("step.mesh", payload_bytes(&bodies, None, None)),
        ("glb", glb_bytes(&bodies)),
    ];
    Ok(files
        .iter()
        .map(|(kind, bytes)| {
            let hex: String = Sha256::digest(bytes).iter().map(|b| format!("{b:02x}")).collect();
            format!("{kind}:{hex}")
        })
        .collect::<Vec<_>>()
        .join(" "))
}

#[test]
fn identical_across_runs() -> anyhow::Result<()> {
    let first = digests()?;
    if std::env::var_os(AGAIN).is_some() {
        println!("digests {first}");
        return Ok(());
    }
    assert_eq!(first, digests()?, "a second build in the same process wrote other bytes");
    let out = Command::new(std::env::current_exe()?)
        .args(["identical_across_runs", "--exact", "--nocapture", "--test-threads=1"])
        .env(AGAIN, "1")
        .output()?;
    let text = String::from_utf8_lossy(&out.stdout);
    let theirs = text.lines().find_map(|l| l.split_once("digests ").map(|(_, d)| d)).expect("the second process printed its digests");
    assert_eq!(first, theirs, "a second process wrote other bytes");
    for d in first.split(' ') {
        println!("{d}");
    }
    Ok(())
}
