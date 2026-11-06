//! A worked concept: a plate with four holes, a pocket and raised lettering, inside a frame, in
//! the catalog's colours. Copy it to start a concept of your own.
use anyhow::Result;
use hsm_kernel::{Font, HAlign, Kind, Loop, Plane, Profile, VAlign, v2, v3};
use hsm_sandbox::{material, out, show};

fn main() -> Result<()> {
    let dir = out()?;
    let (width, depth, thick) = (120., 80., 6.);

    // A profile is an outline with holes, extruded along its plane's normal.
    let mut outline = Profile::rect(v2(0., 0.), width, depth);
    for x in [-50., 50.] {
        for y in [-30., 30.] {
            outline = outline.with_hole(Loop::circle(v2(x, y), 2.5));
        }
    }
    let plate = Plane::XY.extrude(&outline, thick)?;

    // Booleans take whole solids: the pocket is a box sunk into the top, the lettering stands on
    // it, each overlapping the plate a little so the faces don't coincide.
    let pocket = Plane::XY.extrude(&Profile::rect(v2(0., -12.), 60., 20.), thick)?.translate(v3(0., 0., thick / 2.));
    let font = Font::find("Helvetica Neue", Kind::Regular)?;
    let lettering = Plane::XY
        .text(&font, "SODA", 14., 1.2, HAlign::Center, VAlign::Center)?
        .translate(v3(0., 18., thick - 0.2));
    let plate = plate.cut(&pocket)?.union(&lettering)?;

    // A second body: a frame standing clear of the plate.
    let ring = Profile::rect(v2(0., 0.), width + 8., depth + 8.).with_hole(Loop::rect(v2(0., 0.), width + 1., depth + 1.));
    let frame = Plane::XY.extrude(&ring, thick + 2.)?;

    show(&dir, "plate", &[("plate", material("M_PETGF_BLACK")?, &plate), ("frame", material("M_STAINLESS")?, &frame)])
}
