//! The Sculpted faucet's display cover: a skin lofted from its skirt round the neck up to its face,
//! hollowed for the display and opened for the glass and round the neck, its lower front and rear
//! edges sloped up to the open underside, with the lips that snap into the shell's grooves; cut as
//! it sits on the tip, which the faucet assembly stands in place, and printed with its sides bowed
//! in by what they spring back from on the neck.
//!
//!     faucet-display-cover [<output directory>]
use anyhow::{Result, ensure};
use hsm_faucet::shell::PAST;
use hsm_faucet::{Gooseneck, display};
use hsm_faucet_display_cover_numbers as cover;
use hsm_faucet_numbers::catalog;
use hsm_faucet_numbers::shell::{
    DISPENSE_FACE_THICKNESS, DISPLAY_COVER_FRONT_RIM_N, DISPLAY_COVER_FRONT_RIM_SLOPE,
    DISPLAY_COVER_REAR_TRIM_DS_DN, DISPLAY_COVER_REAR_TRIM_S0, DISPLAY_HEAD_S_MIN,
};
use hsm_kernel::part::write_shown;
use hsm_kernel::*;
use hsm_print_payload::printed;
use std::f64::consts::FRAC_PI_2;

const PRINTED: &str = "faucet-display-cover";
const SEATED: &str = "faucet-display-cover-seated";

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/faucet-display-cover")?;
    let neck = Gooseneck::shell();
    let black = Some(catalog::faucet_black());
    let seated = seated_cover(&neck)?;
    let relaxed = display::relaxed_by(&neck, &seated, cover::BEZEL_N_BOTTOM, cover::wing_inward)?;
    ensure!(relaxed.components().len() == 1, "the display cover is not one solid");
    println!("{}", printed::write(&out, PRINTED, Body { name: PRINTED, color: black, solid: &relaxed })?);
    println!("{}", write_shown(&out, SEATED, &[Body { name: SEATED, color: black, solid: &seated }])?);
    Ok(())
}

/// The cover as it sits on the tip: its skin hollowed for the display, opened for the glass and
/// round the neck, its lower edges sloped, with its lips.
fn seated_cover(neck: &Gooseneck) -> Result<Solid> {
    let outer = clamped(neck, loft(neck, &cover::outer_rows())?, cover::outer_clamp())?;
    let mut cavity = loft(neck, &cover::cavity_rows())?;
    for clamp in cover::cavity_clamps() {
        cavity = clamped(neck, cavity, clamp)?;
    }
    let [s0, s1] = cover::window_s();
    let [n0, n1] = cover::window_n();
    let window = neck.cradle_prism(cover::WINDOW_HALF_X, (s0, s1), (n0, n1), cover::WINDOW_CORNER_R)?;
    let arch = display::neck_round(neck, cover::neck_clearance_r())?;
    let (_, _, normal) = neck.tip_frame();
    let [half_x, _, rear_s, n0, n1] = cover::outer_clamp();
    // Carry the nose cut past the cavity's front face so the cutters overlap.
    let nose_arch = clamped(
        neck,
        arch.translate(normal * cover::NOSE_ARCH_LIFT),
        [half_x, DISPLAY_HEAD_S_MIN - PAST, DISPENSE_FACE_THICKNESS + PAST, n0, n1],
    )?;
    let rear_arch = clamped(
        neck,
        arch.translate(normal * cover::REAR_ARCH_LIFT),
        [half_x, DISPLAY_COVER_REAR_TRIM_S0, rear_s + PAST, n0, n1],
    )?;
    let skin = sloped(neck, outer.cut_all(&[cavity, window, arch, nose_arch, rear_arch])?)?;
    // The band stands from under the skin's foot, so no face of it lies on the skin's.
    let [hx, s0, s1, n0, n1] = cover::lip_band();
    let band = neck.cradle_prism(hx, (s0, s1), (n0 - PAST, n1), 0.0)?;
    let lips = display::lips(&outer.intersect(&band)?, neck, cover::LIP_R, cover::LIP_RELIEF)?;
    skin.union(&lips)
}

/// The smooth loft through the rows' outlines (`outline`).
fn loft(neck: &Gooseneck, rows: &[[f64; 5]]) -> Result<Solid> {
    let sections: Vec<LoftSection> = rows.iter().map(|&[w, l, r, nn, centre]| outline(neck, w, l, r, nn, centre)).collect();
    let surface = SmoothLoft::new(&compatible(&sections)?)?;
    let (us, vs) = surface.grid();
    surface.solid_on(&us, &vs)
}

/// The eight-edge outline at height `nn` of the tip frame: `w` across and `l` along s about
/// `centre`, its corners rounded `r`, from the west end of its near side and anticlockwise seen
/// from +n.
fn outline(neck: &Gooseneck, w: f64, l: f64, r: f64, nn: f64, centre: f64) -> LoftSection {
    let (tip, up, normal) = neck.tip_frame();
    let at = |x: f64, s: f64| tip + V3::X * x + up * s + normal * nn;
    let (h, a, b) = (w / 2.0, centre - l / 2.0, centre + l / 2.0);
    let line = |p: V3, q: V3| LoftEdge::Line { a: p, b: q };
    // A quarter turn about `c` from `c + r x` towards `c + r y`.
    let arc = |c: V3, x: V3, y: V3| LoftEdge::Conic { c, x: x * r, y: y * r, t0: 0.0, t1: FRAC_PI_2 };
    LoftSection::new(vec![
        line(at(-h + r, a), at(h - r, a)),
        arc(at(h - r, a + r), -up, V3::X),
        line(at(h, a + r), at(h, b - r)),
        arc(at(h - r, b - r), V3::X, up),
        line(at(h - r, b), at(-h + r, b)),
        arc(at(-h + r, b - r), up, -V3::X),
        line(at(-h, b - r), at(-h, a + r)),
        arc(at(-h + r, a + r), -V3::X, -up),
    ])
}

/// `solid` cut to the prism `[half x, s0, s1, n0, n1]` of the tip frame.
fn clamped(neck: &Gooseneck, solid: Solid, [hx, s0, s1, n0, n1]: [f64; 5]) -> Result<Solid> {
    solid.intersect(&neck.cradle_prism(hx, (s0, s1), (n0, n1), 0.0)?)
}

/// `skin` with its lower front edge sloped up to `n = n0 - slope s` and its lower rear edge back
/// to `s = s0 + ds_dn n`, each from the open underside.
fn sloped(neck: &Gooseneck, skin: Solid) -> Result<Solid> {
    let (tip, up, normal) = neck.tip_frame();
    let front = Plane::new(tip + normal * DISPLAY_COVER_FRONT_RIM_N, V3::X, normal + up * DISPLAY_COVER_FRONT_RIM_SLOPE)?;
    let rear = Plane::new(tip + up * DISPLAY_COVER_REAR_TRIM_S0, V3::X, normal * DISPLAY_COVER_REAR_TRIM_DS_DN - up)?;
    skin.trim(&front)?.trim(&rear)
}
