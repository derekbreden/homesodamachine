//! The water-inlet jet drilling fixture's files: the fixed jaw on its base and the loose jaw, each
//! with half the groove the jet cap's rod stands in, both in their print orientation. They hold the
//! rod upright while the drill press bores the jet's passage down it.
//!
//!     water-inlet-jet-fixture [<output directory>]
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Solid, V3, v3};
use hsm_water_inlet_jet_fixture_numbers as fixture;
use serde_json::json;
use std::path::PathBuf;

const OUTPUT: &str = "hardware/printed-parts/fixtures/water-inlet-jet";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: water-inlet-jet-fixture [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let (fixed, loose) = build()?;
    let color = Some(petgf_black()?);
    let (mut files, mut bodies) = (vec![], vec![]);
    for (name, solid) in [("water-inlet-jet-fixture-fixed", &fixed), ("water-inlet-jet-fixture-loose", &loose)] {
        let said = write_part(&out, name, &[Body { name, color, solid }])?;
        files.extend(said["files"].as_array().into_iter().flatten().cloned());
        bodies.extend(said["bodies"].as_array().into_iter().flatten().cloned());
    }
    println!("{}", json!({"files": files, "bodies": bodies}));
    Ok(())
}

fn build() -> Result<(Solid, Solid)> {
    let [base_x, base_y, base_z] = fixture::BASE;
    let [width, depth, height] = fixture::JAW;
    let (gap, radius) = (fixture::GAP, fixture::GROOVE_RADIUS);
    let groove = Solid::cylinder(v3(0., 0., base_z - 1.), V3::Z, radius, height + 2.)?;
    let fixed = Solid::cuboid(v3(-base_x / 2., -base_y / 2., 0.), v3(base_x / 2., base_y / 2., base_z)).union(
        &Solid::cuboid(v3(-width / 2., gap / 2., base_z), v3(width / 2., gap / 2. + depth, base_z + height))
            .cut(&groove)?,
    )?;
    let loose = Solid::cuboid(v3(-width / 2., -gap / 2. - depth, base_z), v3(width / 2., -gap / 2., base_z + height))
        .cut(&groove)?;
    for (name, part) in [("fixed jaw and base", &fixed), ("loose jaw", &loose)] {
        part.check()?;
        ensure!(part.components().len() == 1 && part.volume() > 0., "{name}: one solid of positive volume");
    }
    // The jaws still close on the rod at either end of its tolerance, before they meet.
    for diameter in [-1., 0., 1.].map(|s| fixture::STOCK_DIAMETER + s * fixture::STOCK_TOLERANCE) {
        let closure = 2. * radius - diameter;
        ensure!(closure > 0. && gap - closure > 0., "the rod's tolerance exhausts the jaws' travel");
    }
    // The drill, running down the rod off its axis by the groove's slip, meets neither jaw.
    let (below_top, run) = (4., 15.);
    let drill = Solid::cylinder(
        v3(0., fixture::RADIAL_SLIP, base_z + fixture::MINIMUM_BLANK - below_top),
        V3::Z,
        fixture::DRILL_DIAMETER / 2.,
        run,
    )?;
    ensure!(fixed.shared_volume(&drill)? + loose.shared_volume(&drill)? <= 1e-6, "the drill's path reaches a jaw");
    let loose = loose.translate(v3(0., 0., -base_z));
    Ok((fixed, loose))
}

/// Glass-filled PETG as the payload carries it: the materials catalog's colour, linear RGB at
/// single precision.
fn petgf_black() -> Result<[f64; 3]> {
    let catalog: serde_json::Value =
        serde_json::from_str(include_str!("../../../../tools/hsm/shared-data/catalog/materials.json"))?;
    let args = &catalog["colors"]["M_PETGF_BLACK"]["args"];
    let mut linear = [0.; 3];
    for (i, channel) in linear.iter_mut().enumerate() {
        let c = args[i].as_f64().context("the PET-GF colour's channels")?;
        let curved = if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) };
        *channel = curved as f32 as f64;
    }
    Ok(linear)
}
