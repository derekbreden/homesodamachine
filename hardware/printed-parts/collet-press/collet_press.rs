//! The collet press's files: the one-piece PET-GF hand tool in its supportless print pose, the
//! handle flat on the bed and the forked head rising from it.
//!
//!     collet-press [<output directory>]
use anyhow::{Result, bail, ensure};
use hsm_collet_press_numbers as press;
use hsm_kernel::part::write_part;
use hsm_kernel::{Affine, Body, Loop, Pen, Plane, Profile, Solid, V3, v2, v3};
use std::path::PathBuf;

const NAME: &str = "collet-press";
const OUTPUT: &str = "hardware/printed-parts/collet-press";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: collet-press [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let solid = build()?;
    let bodies = [Body { name: NAME, color: Some(hsm_catalog::petgf_black()), solid: &solid }];
    println!("{}", write_part(&out, NAME, &bodies)?);
    Ok(())
}

/// A solid in the head's frame, tilted up and lifted into the print pose.
fn posed(solid: &Solid) -> Solid {
    solid
        .transformed(&Affine::rotation(V3::ZERO, V3::Y, -press::HEAD_ANGLE))
        .transformed(&Affine::translation(v3(0., 0., press::head_z_shift())))
}

fn build() -> Result<Solid> {
    let (back, front) = (press::head_back(), press::head_front());
    let half = press::HEAD_WIDTH / 2.;
    let gap = press::JAW_GAP / 2.;
    let radius = press::TIP_RADIUS;
    let root = press::JAW_ROOT;
    // The nose's four quarter rounds keep the straight bearing lands either side of the slot;
    // the half circle closes the constant-width slot's root.
    let head = Profile::new(
        Pen::new(v2(back, -half))
            .line_to(v2(front - radius, -half))
            .arc_center(v2(front - radius, -half + radius), v2(front, -half + radius), true)
            .line_to(v2(front, -gap - radius))
            .arc_center(v2(front - radius, -gap - radius), v2(front - radius, -gap), true)
            .line_to(v2(root, -gap))
            .arc_center(v2(root, 0.), v2(root, gap), false)
            .line_to(v2(front - radius, gap))
            .arc_center(v2(front - radius, gap + radius), v2(front, gap + radius), true)
            .line_to(v2(front, half - radius))
            .arc_center(v2(front - radius, half - radius), v2(front - radius, half), true)
            .line_to(v2(back, half))
            .close()?,
    );
    let head = posed(&Plane::XY.extrude(&head, press::HEAD_THICKNESS)?);

    let [rear, reach] = press::handle_x();
    let width = press::HEAD_WIDTH;
    let handle = Plane::XY.extrude(
        &Profile::new(Loop::rounded_rect(v2((rear + reach) / 2., 0.), reach - rear, width, radius)?),
        press::HEAD_THICKNESS,
    )?;
    let clip: Vec<_> = press::handle_clip().iter().map(|&[x, z]| v2(x, z)).collect();
    let clip = Plane::XZ.at(v3(0., width, 0.)).extrude(&Profile::new(Loop::polygon(&clip)), 2. * width)?;
    let tool = handle.intersect(&clip)?.union(&head)?;
    tool.check()?;
    ensure!(tool.components().len() == 1, "the collet press is one closed printable body");

    let tube = press::PORT_DIAMETER;
    ensure!(
        tube < press::JAW_GAP && press::JAW_GAP < press::collet_bore(),
        "the jaw passes the tube and stays inside the release sleeve's bore"
    );
    let path = Solid::cylinder(v3(root, 0., -2.), V3::Z, tube / 2., press::HEAD_THICKNESS + 4.)?;
    let interference = tool.shared_volume(&posed(&path))?;
    ensure!(interference <= 1e-6, "the tube's path through the slot is clear");
    Ok(tool)
}
