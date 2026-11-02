//! The one-piece angled collet press, in its original supportless print pose.
use anyhow::{ensure, Result};
use hsm_kernel::part::{args, write_part, Numbers};
use hsm_kernel::{v2, v3, Affine, Body, Loop, Pen, Plane, Profile, Solid, V3};

fn posed(n: &Numbers, solid: &Solid) -> Result<Solid> {
    Ok(solid.transformed(&Affine::rotation(V3::ZERO, V3::Y, -n.f("head_angle")?))
        .transformed(&Affine::translation(v3(0.0, 0.0, n.f("head_z_shift")?))))
}

fn build(n: &Numbers) -> Result<Solid> {
    let back = n.f("head_back")?;
    let front = n.f("head_front")?;
    let half = n.f("head_width")? / 2.0;
    let gap = n.f("jaw_gap")? / 2.0;
    let radius = n.f("tip_radius")?;
    let root = n.f("jaw_root")?;
    // Four nose quarters preserve the original straight bearing lands. The
    // clockwise half-circle is the constant-width U-slot's closed root.
    let head = Profile::new(Pen::new(v2(back, -half))
        .line_to(v2(front - radius, -half))
        .arc_center(v2(front - radius, -half + radius), v2(front, -half + radius), true)
        .line_to(v2(front, -gap - radius))
        .arc_center(v2(front - radius, -gap - radius), v2(front - radius, -gap), true)
        .line_to(v2(root, -gap))
        .arc_center(v2(root, 0.0), v2(root, gap), false)
        .line_to(v2(front - radius, gap))
        .arc_center(v2(front - radius, gap + radius), v2(front, gap + radius), true)
        .line_to(v2(front, half - radius))
        .arc_center(v2(front - radius, half - radius), v2(front - radius, half), true)
        .line_to(v2(back, half)).close()?);
    let head = posed(n, &Plane::XY.extrude(&head, n.f("head_thickness")?)?)?;

    let (rear, raw_front) = n.pair("handle_x")?;
    let width = n.f("handle_width")?;
    let handle = Plane::XY.extrude(&Profile::new(Loop::rounded_rect(
        v2((rear + raw_front) / 2.0, 0.0), raw_front - rear, width,
        n.f("handle_corner_radius")?,
    )?), n.f("handle_thickness")?)?;
    let points = n.list("handle_clip")?;
    let polygon = points.chunks_exact(2).map(|p| v2(p[0], p[1])).collect::<Vec<_>>();
    let clip = Plane::XZ.at(v3(0.0, width, 0.0))
        .extrude(&Profile::new(Loop::polygon(&polygon)), 2.0 * width)?;
    let tool = handle.intersect(&clip)?.union(&head)?;
    tool.check()?;
    ensure!(tool.components().len() == 1, "collet press must be one closed printable body");
    let tube_d = n.f("tube_diameter")?;
    ensure!(tube_d < 2.0 * gap && 2.0 * gap < n.f("collet_bore")?,
            "jaw must pass the tube and remain inside the collet bore");
    let tube = Solid::cylinder(v3(root, 0.0, -2.0), V3::Z,
                               tube_d / 2.0, n.f("head_thickness")? + 4.0)?;
    let interference = tool.shared_volume(&posed(n, &tube)?)?;
    ensure!(interference <= 1e-6, "tube path interference {interference} mm3");
    Ok(tool)
}

fn main() -> Result<()> {
    let (n, out) = args()?;
    let solid = build(&n)?;
    println!("{}", write_part(&out, "collet-press", &[Body {
        name: "collet-press", color: Some(n.color("color")?), solid: &solid,
    }])?);
    Ok(())
}
