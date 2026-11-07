//! The fuse clamp's files: the PETG bracket that pinches the SF76E's case on the compressor's power
//! box, one silhouette swept across its width with the case's channel cut through it, in the
//! cutoff's own frame; and its numbers file, the case it holds.
//!
//!     fuse-clamp [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_fuse_clamp_numbers as clamp;
use hsm_kernel::part::write_part;
use hsm_kernel::{Body, Plane, Profile, Solid, V2, V3, v2, v3};
use serde::Serialize;
use std::path::PathBuf;

const NAME: &str = "fuse-clamp";
const OUTPUT: &str = "hardware/printed-parts/refrigeration/fuse-clamp";

/// The clamp's numbers file: the case it holds, which the installed machine's wiring lays the
/// fuse's leads by.
#[derive(Serialize)]
struct Figures {
    /// The case's length along X.
    case_l: f64,
    /// The case's diameter.
    case_d: f64,
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: fuse-clamp [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let solid = build()?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::petg_black()), solid: &solid }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    let figures = Figures { case_l: clamp::CASE_L, case_d: clamp::CASE_D };
    std::fs::write(out.join(format!("{NAME}.numbers.json")), serde_json::to_string_pretty(&figures)? + "\n")?;
    Ok(())
}

/// The part's whole silhouette in the Y-Z plane, from the head's outboard top corner: the head,
/// the neck down the cover's flank to the plate's crown, and the two leaves reaching inboard into
/// the gap, each with its lead-in at the tip.
fn profile() -> Vec<V2> {
    let (head_y, head_z, neck_z) = (clamp::head_y(), clamp::head_z(), clamp::NECK_Z);
    let (floor, plate) = (clamp::box_floor(), clamp::plate_top());
    let (leaf, reach, lead_in) = (clamp::LEAF_Y, clamp::LEAF_REACH, clamp::LEAF_LEAD_IN);
    vec![
        v2(head_y, head_z),
        v2(-head_y, head_z),
        v2(-head_y, neck_z),
        v2(plate, neck_z),
        v2(plate, -reach + lead_in),
        v2(plate + lead_in, -reach),
        v2(plate + leaf, -reach),
        v2(plate + leaf, 0.),
        v2(floor - leaf, 0.),
        v2(floor - leaf, -reach),
        v2(floor - lead_in, -reach),
        v2(floor, -reach + lead_in),
        v2(floor, 0.),
        v2(head_y, 0.),
    ]
}

/// The profile swept the part's one width, with the channel cut through it, held to its pinch:
/// grown by the contact tolerance, the case seated in the channel meets the crown.
fn build() -> Result<Solid> {
    let width = clamp::part_x();
    let part = Plane::YZ.at(v3(-width / 2., 0., 0.)).extrude(&Profile::polygon(&profile()), width)?;
    let depth = clamp::channel_z();
    let channel = Plane::XY.at(v3(0., 0., depth / 2.)).cuboid(width + 2., clamp::channel_h(), depth);
    let body = part.cut(&channel)?;
    body.check()?;
    ensure!(body.components().len() == 1, "the fuse clamp is one closed printable body");

    let radius = clamp::CASE_D / 2.;
    let case = Solid::cylinder(v3(-clamp::CASE_L / 2., 0., radius), V3::X, radius + clamp::CONTACT_TOL, clamp::CASE_L)?;
    ensure!(body.shared_volume(&case)? > 0., "the crown bears on the case");
    Ok(body)
}
