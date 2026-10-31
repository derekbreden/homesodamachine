//! The fuse clamp on the kernel: the part's silhouette in the Y-Z plane swept its one width
//! across X, the channel cut through it, in the cutoff's own frame. `fuse_clamp.py` holds the
//! numbers, reads the donor's off the compressor and the cutoff, and writes them for this
//! program; its docstring says what each feature is for.
//!
//!     cargo run --release --manifest-path tools/hsm/refrigeration/Cargo.toml --bin fuse-clamp -- \
//!         <fuse-clamp.numbers.json> <out dir>
use anyhow::Result;
use hsm_kernel::part::{Numbers, args, write_part};
use hsm_kernel::{Body, Plane, Profile, Solid, V2, v2, v3};

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

fn main() -> Result<()> {
    let (n, out) = args()?;
    let clamp = build(&n)?;
    let name = n.text("name")?;
    let body = Body { name, color: Some(n.color("color")?), solid: &clamp };
    println!("{}", write_part(&out, name, &[body])?);
    Ok(())
}
