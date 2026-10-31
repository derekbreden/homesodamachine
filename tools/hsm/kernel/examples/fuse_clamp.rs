//! The fuse clamp (`hardware/printed-parts/refrigeration/fuse-clamp/fuse_clamp.py`) on the
//! kernel: the part's silhouette in the Y-Z plane swept its one width across X, the channel cut
//! through it.
//!
//!     cargo run --release -p hsm-kernel --example fuse_clamp -- <out dir>
//!
//! writes `fuse-clamp.step.mesh`, `.stl`, `.3mf` and `.glb` into `<out dir>`.
use anyhow::Result;
use hsm_kernel::{Body, Plane, Profile, Solid, V2, v2, v3};

// The donor's figures: the compressor's power box and the SF76E cutoff.
const FACE_Y: f64 = 45.0; // the flank's standing height (compressor POWER_Z)
const GAP: f64 = 15.0; // the air under the box (POWER_GAP)
const CASE_D: f64 = 4.2; // the cutoff's case (sf76e BODY_D)
const CASE_L: f64 = 11.0; // (BODY_L)
const LEAD_STUB: f64 = 3.0; // the datasheet's no-bend zone (LEAD_STUB)
const SLIP: f64 = 0.15; // fits.slip

const BOX_FLOOR: f64 = -FACE_Y / 2.0;
const PLATE_TOP: f64 = BOX_FLOOR - GAP;

// The head and its channel.
const CHANNEL_H: f64 = CASE_D + 2.0 * SLIP;
const CHANNEL_Z: f64 = CASE_D;
const CROWN: f64 = 2.5;
const HEAD_Z: f64 = CHANNEL_Z + CROWN;
const LEAD_RELEASE: f64 = 0.5;
const PART_X: f64 = CASE_L + 2.0 * (LEAD_STUB + LEAD_RELEASE);
const HEAD_PAD: f64 = 6.7;
const HEAD_Y: f64 = CHANNEL_H / 2.0 + HEAD_PAD;

// The neck and the leaves.
const NECK_Z: f64 = 3.5;
const LEAF_Y: f64 = 2.5;
const LEAF_REACH: f64 = 22.0;
const LEAF_LEAD_IN: f64 = 1.5;

/// The part's whole silhouette in the Y-Z plane, from the head's outboard top corner.
pub fn profile() -> Vec<V2> {
    vec![
        v2(HEAD_Y, HEAD_Z),
        v2(-HEAD_Y, HEAD_Z),
        v2(-HEAD_Y, NECK_Z),
        v2(PLATE_TOP, NECK_Z),
        v2(PLATE_TOP, -LEAF_REACH + LEAF_LEAD_IN),
        v2(PLATE_TOP + LEAF_LEAD_IN, -LEAF_REACH),
        v2(PLATE_TOP + LEAF_Y, -LEAF_REACH),
        v2(PLATE_TOP + LEAF_Y, 0.0),
        v2(BOX_FLOOR - LEAF_Y, 0.0),
        v2(BOX_FLOOR - LEAF_Y, -LEAF_REACH),
        v2(BOX_FLOOR - LEAF_LEAD_IN, -LEAF_REACH),
        v2(BOX_FLOOR, -LEAF_REACH + LEAF_LEAD_IN),
        v2(BOX_FLOOR, 0.0),
        v2(HEAD_Y, 0.0),
    ]
}

/// The profile swept the part's one width, with the channel cut through it.
pub fn build() -> Result<Solid> {
    let part = Plane::YZ.at(v3(-PART_X / 2.0, 0.0, 0.0)).extrude(&Profile::polygon(&profile()), PART_X)?;
    let channel = Plane::XY.at(v3(0.0, 0.0, CHANNEL_Z / 2.0)).cuboid(PART_X + 2.0, CHANNEL_H, CHANNEL_Z);
    part.cut(&channel)
}

#[allow(dead_code)]
fn main() -> Result<()> {
    let out = std::path::PathBuf::from(std::env::args().nth(1).unwrap_or_else(|| ".".into()));
    let clamp = build()?;
    let b = clamp.bounds();
    println!("fuse clamp — the SF76E's case, held on the compressor's power box flank");
    println!(
        "  X[{:.2}, {:.2}]  Y[{:.2}, {:.2}]  Z[{:.2}, {:.2}]",
        b.min.x, b.max.x, b.min.y, b.max.y, b.min.z, b.max.z
    );
    println!("  volume  {:.2} cm³, {} faces", clamp.volume() / 1000.0, clamp.faces().len());
    for f in clamp.faces() {
        println!("    {f}");
    }
    let body = Body { name: "fuse-clamp", color: Some([0.02, 0.02, 0.02]), solid: &clamp };
    hsm_kernel::write_payload(out.join("fuse-clamp.step.mesh"), &[body], None, None)?;
    hsm_kernel::write_stl(out.join("fuse-clamp.stl"), &[&clamp])?;
    hsm_kernel::write_3mf(out.join("fuse-clamp.3mf"), &[&clamp], "fuse-clamp")?;
    hsm_kernel::write_glb(out.join("fuse-clamp.glb"), &[body])?;
    println!("-> {}", out.join("fuse-clamp.step.mesh").display());
    Ok(())
}
