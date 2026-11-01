//! The fuse clamp on the kernel: the part's silhouette in the Y-Z plane swept its one width
//! across X, the channel cut through it, in the cutoff's own frame. `fuse_clamp.py` holds the
//! numbers, reads the donor's off the compressor and the cutoff, and writes them for this
//! program; its docstring says what each feature is for. The program holds the part to its pinch
//! before it writes anything, and `--check` says what the pinch measured and writes nothing.
//!
//!     cargo run --release --manifest-path tools/hsm/refrigeration/Cargo.toml --bin fuse-clamp -- \
//!         <fuse-clamp.numbers.json> <out dir>
//!     ... --bin fuse-clamp -- <fuse-clamp.numbers.json> --check
use anyhow::{Result, ensure};
use hsm_kernel::part::{Numbers, args, write_part_with_sources};
use hsm_kernel::{Body, Plane, Profile, Solid, V2, V3, v2, v3};

/// The part's whole silhouette in the Y-Z plane, from the head's outboard top corner: the head,
/// the neck down the cover's flank to the plate's crown, and the two leaves reaching inboard into
/// the gap, each with its lead-in at the tip.
pub fn profile(n: &Numbers) -> Result<Vec<V2>> {
    let (head_y, head_z, neck_z) = (n.f("head_y")?, n.f("head_z")?, n.f("neck_z")?);
    let (box_floor, plate_top) = (n.f("box_floor")?, n.f("plate_top")?);
    let (leaf_y, leaf_reach, lead_in) = (n.f("leaf_y")?, n.f("leaf_reach")?, n.f("leaf_lead_in")?);
    Ok(vec![
        v2(head_y, head_z),
        v2(-head_y, head_z),
        v2(-head_y, neck_z),
        v2(plate_top, neck_z),
        v2(plate_top, -leaf_reach + lead_in),
        v2(plate_top + lead_in, -leaf_reach),
        v2(plate_top + leaf_y, -leaf_reach),
        v2(plate_top + leaf_y, 0.0),
        v2(box_floor - leaf_y, 0.0),
        v2(box_floor - leaf_y, -leaf_reach),
        v2(box_floor - lead_in, -leaf_reach),
        v2(box_floor, -leaf_reach + lead_in),
        v2(box_floor, 0.0),
        v2(head_y, 0.0),
    ])
}

/// The profile swept the part's one width, with the channel cut through it.
pub fn build(n: &Numbers) -> Result<Solid> {
    let part_x = n.f("part_x")?;
    let (channel_h, channel_z) = (n.f("channel_h")?, n.f("channel_z")?);
    let part = Plane::YZ.at(v3(-part_x / 2.0, 0.0, 0.0)).extrude(&Profile::polygon(&profile(n)?), part_x)?;
    let channel = Plane::XY.at(v3(0.0, 0.0, channel_z / 2.0)).cuboid(part_x + 2.0, channel_h, channel_z);
    part.cut(&channel)
}

/// The crown lands ON the case: grown by `contact_tol`, the case meets the clamp, and a clamp
/// standing off is a case lying loose on a face. Returns how much of the grown case the clamp
/// holds, in mm³.
pub fn pinch(n: &Numbers, clamp: &Solid) -> Result<f64> {
    let (case_d, case_l, tol) = (n.f("case_d")?, n.f("case_l")?, n.f("contact_tol")?);
    let grown = Solid::cylinder(v3(-case_l / 2.0, 0.0, case_d / 2.0), V3::X, case_d / 2.0 + tol, case_l)?;
    let touch = clamp.intersect(&grown)?.volume();
    ensure!(
        touch > 0.0,
        "a case grown {tol} mm proud of its own Ø{case_d} still misses the clamp — the crown stands off \
         the generatrix it is meant to bear on, so nothing presses the case onto the cover and a {} °C \
         cutoff is reading cabinet air.",
        n.f("tf_c")?
    );
    Ok(touch)
}

fn main() -> Result<()> {
    if std::env::args().nth(2).as_deref() == Some("--check") {
        let n = Numbers::read(std::env::args().nth(1).unwrap_or_default())?;
        println!("{}", serde_json::json!({ "pinch": pinch(&n, &build(&n)?)? }));
        return Ok(());
    }
    let (n, out) = args()?;
    let clamp = build(&n)?;
    pinch(&n, &clamp)?;
    let name = n.text("name")?;
    let body = Body { name, color: Some(n.color("color")?), solid: &clamp };
    println!("{}", write_part_with_sources(&out, name, &[body])?);
    Ok(())
}
