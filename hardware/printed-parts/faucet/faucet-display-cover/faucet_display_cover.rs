//! The Sculpted faucet's display cover on the kernel: a skin lofted from its skirt round the neck
//! up to its face, hollowed for the display and opened for the glass and round the neck, its lower
//! front and rear edges sloped up to the open underside, with the lips that snap into the shell's
//! grooves; cut as it sits on the tip and printed with its wings leaned in.
//! `faucet_display_cover.py` holds the numbers and writes them for this program.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin faucet-display-cover -- \
//!         <faucet-display-cover.numbers.json> <out dir>
use anyhow::{Result, anyhow, bail, ensure};
use hsm_faucet::shell::PAST;
use hsm_faucet::{Gooseneck, display, floats, rows};
use hsm_kernel::part::{Numbers, args, write_printed, write_shown};
use hsm_kernel::*;
use serde_json::Value;
use std::f64::consts::FRAC_PI_2;

fn main() -> Result<()> {
    let (n, out) = args()?;
    let neck = Gooseneck::read(&n)?;
    let name = |key: &str| n.get("names")?[key].as_str().ok_or_else(|| anyhow!("no name for the {key}"));
    let black = Some(n.color("color")?);
    let seated = seated_cover(&n, &neck, false)?;
    let open = seated_cover(&n, &neck, true)?;
    let cover = display::relaxed(&neck, &seated, &open, n.f("cover_bezel_n")?, n.f("cover_wing_slope")?)?;
    ensure!(cover.components().len() == 1, "the display cover is not one solid");
    let printed = name("cover")?;
    println!("{}", write_printed(&out, printed, &[Body { name: printed, color: black, solid: &cover }])?);
    // The cover as it sits on the tip, which the faucet assembly stands in place.
    let shown = name("seated")?;
    println!("{}", write_shown(&out, shown, &[Body { name: shown, color: black, solid: &seated }])?);
    Ok(())
}

/// The cover as it sits on the tip: its skin hollowed for the display, opened for the glass and
/// round the neck, its lower edges sloped, with its lips. `open` runs the display's cavity on up
/// through the bezel.
fn seated_cover(n: &Numbers, neck: &Gooseneck, open: bool) -> Result<Solid> {
    let (outer, top, _) = loft(neck, n.get("cover_outer_rows")?)?;
    let outer = clamped(neck, outer, n.get("cover_outer_clamp")?)?;
    let (mut cavity, ceiling, ring) = loft(neck, n.get("cover_cavity_rows")?)?;
    for clamp in rows(n.get("cover_cavity_clamps")?)? {
        cavity = clamped(neck, cavity, clamp)?;
    }
    if open {
        // Stood on the loft's own ring at the ceiling, so the two meet point for point.
        let (_, _, normal) = neck.tip_frame();
        cavity = cavity.union(&Solid::extrude(&ring, normal, normal * (top + PAST - ceiling))?)?;
    }
    let window = neck.cradle_prism(
        n.f("cover_window_half_x")?,
        n.pair("cover_window_s")?,
        n.pair("cover_window_n")?,
        n.f("cover_window_corner_r")?,
    )?;
    let arch = display::neck_round(n, neck, n.f("cover_neck_clearance_r")?)?;
    let skin = sloped(n, neck, outer.cut_all(&[cavity, window, arch])?)?;
    // The band stands from under the skin's foot, so no face of it lies on the skin's.
    let band = match floats(n.get("cover_lip_band")?).as_deref() {
        Some(&[hx, s0, s1, n0, n1]) => neck.cradle_prism(hx, (s0, s1), (n0 - PAST, n1), 0.0)?,
        _ => bail!("the lip band is not a prism"),
    };
    let lips = display::lips(&outer.intersect(&band)?, n, neck, n.f("cover_lip_r")?, n.f("cover_lip_relief")?)?;
    skin.union(&lips)
}

/// The smooth loft through the rows' outlines (`outline`), with the n of its last row and its
/// ring there.
fn loft(neck: &Gooseneck, rows_of: &Value) -> Result<(Solid, f64, Region)> {
    let mut sections = vec![];
    let mut last = f64::NAN;
    for row in rows(rows_of)? {
        match floats(row).as_deref() {
            Some(&[w, l, r, nn, centre]) => {
                sections.push(outline(neck, w, l, r, nn, centre));
                last = nn;
            }
            _ => bail!("{row} is not an outline row"),
        }
    }
    let surface = SmoothLoft::new(&compatible(&sections)?)?;
    let (us, vs) = surface.grid();
    Ok((surface.solid_on(&us, &vs)?, last, surface.end_region(true, &us)))
}

/// The eight-edge outline `_display_outline_wire` draws at height `nn` of the tip frame: `w`
/// across and `l` along s about `centre`, its corners rounded `r`, from the west end of its near
/// side and anticlockwise seen from +n.
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
fn clamped(neck: &Gooseneck, solid: Solid, prism: &Value) -> Result<Solid> {
    match floats(prism).as_deref() {
        Some(&[hx, s0, s1, n0, n1]) => solid.intersect(&neck.cradle_prism(hx, (s0, s1), (n0, n1), 0.0)?),
        _ => bail!("{prism} is not a prism"),
    }
}

/// `skin` with its lower front edge sloped up to `n = n0 - slope s` and its lower rear edge back
/// to `s = s0 + ds_dn n`, each from the open underside.
fn sloped(n: &Numbers, neck: &Gooseneck, skin: Solid) -> Result<Solid> {
    let (tip, up, normal) = neck.tip_frame();
    let (front_n, slope) = n.pair("cover_front_rim")?;
    let (rear_s, ds_dn) = n.pair("cover_rear_trim")?;
    let front = Plane::new(tip + normal * front_n, V3::X, normal + up * slope)?;
    let rear = Plane::new(tip + up * rear_s, V3::X, normal * ds_dn - up)?;
    skin.trim(&front)?.trim(&rear)
}
