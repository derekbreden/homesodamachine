//! The Industrial faucet on the kernel: the shell's gooseneck and cutters on round stock of its own
//! below the zone-5 seam — a foot disc, a body over the Westbrass and the neck standing on it —
//! its round above-counter plate and gasket, and its rectangular display cover, cut as it sits on
//! the tip and printed with its wings leaned in. `industrial_faucet.py` holds the numbers and
//! writes them for this program.
//!
//!     cargo run --release --manifest-path tools/hsm/faucet/Cargo.toml --bin industrial-faucet -- \
//!         <industrial-faucet.numbers.json> <out dir>
use anyhow::{Result, anyhow, bail, ensure};
use hsm_faucet::shell::{PAST, level, lower_bundle_opening, pieces, shell_from};
use hsm_faucet::{Gooseneck, display, pair, rows};
use hsm_kernel::part::{Numbers, args, write_printed, write_shown};
use hsm_kernel::*;

fn main() -> Result<()> {
    let (n, out) = args()?;
    let neck = Gooseneck::read(&n)?;
    let name = |key: &str| n.get("names")?[key].as_str().ok_or_else(|| anyhow!("no name for the {key}"));
    let black = Some(n.color("color")?);
    let seated = seated_cover(&n, &neck, false)?;
    let open = seated_cover(&n, &neck, true)?;
    let cover = display::relaxed(&neck, &seated, &open, n.f("cover_bezel_n")?, n.f("cover_wing_slope")?)?;
    let printed = [
        ("base", shell_base(&n, &neck)?, black),
        ("cover", cover, black),
        ("plate", plate(&n)?, black),
        ("gasket", gasket(&n)?, Some(n.color("gasket_color")?)),
    ];
    for (piece, solid, color) in &printed {
        ensure!(solid.components().len() == 1, "the Industrial {piece} is not one solid");
        let name = name(piece)?;
        println!("{}", write_printed(&out, name, &[Body { name, color: *color, solid }])?);
    }
    // The cover as it sits on the tip, which the Industrial assembly stands in place.
    let name = name("seated")?;
    println!("{}", write_shown(&out, name, &[Body { name, color: black, solid: &seated }])?);
    Ok(())
}

/// The base: the shell's gooseneck and cutters on the Industrial's own stock below the seam, its
/// lever corridor carried up to the top of the body, split from the tip as the shell is.
fn shell_base(n: &Numbers, neck: &Gooseneck) -> Result<Solid> {
    let (foot_top, body_top, seam) = (n.f("foot_top")?, n.f("body_top")?, n.f("zone5_z_top")?);
    let foot = Solid::cylinder(V3::ZERO, V3::Z, n.f("foot_radius")?, foot_top)?;
    let body = Solid::cylinder(v3(0.0, n.f("body_center_y")?, foot_top), V3::Z, n.f("body_radius")?, body_top - foot_top)?;
    let ring = Profile::circle(v2(0.0, n.f("neck_center_y")?), n.f("neck_radius")?);
    let stem = level(body_top).extrude(&ring, seam + n.f("neck_join_overlap")? - body_top)?;
    let stock = Solid::union_all(&[foot, body, stem])?;
    let xh = n.f("lever_clearance_x_half")?;
    let lever = Solid::cuboid(
        v3(-xh, n.f("lever_insertion_front_y")?, n.f("lever_rest_top_z")?),
        v3(xh, n.f("fill_y_min")?, body_top),
    );
    let full = shell_from(n, neck, stock, &ring.place(&level(seam)), &[lever])?;
    Ok(pieces(n, neck, &full)?.0)
}

/// The shank hole, the flavor pill and the cable lane, through from `z0` to `z1`.
fn through(n: &Numbers, z0: f64, z1: f64) -> Result<Vec<Solid>> {
    let (bottom, h) = (z0 - PAST, z1 - z0 + 2.0 * PAST);
    let (cx, cy) = n.pair("shank_hole_center")?;
    let shank = Solid::cylinder(v3(cx, cy, bottom), V3::Z, n.f("shank_hole_radius")?, h)?;
    let (px, py) = n.pair("pill_slot_center")?;
    let pill = Loop::slot(v2(px, py), n.f("pill_length_x")?, n.f("pill_width_y")?, 0.0);
    let pill = level(bottom).extrude(&Profile::new(pill), h)?;
    Ok(vec![shank, pill, lower_bundle_opening(n)?])
}

/// The round plate the base stands on: a pedestal under each mounting pod, chamfered round its
/// top, bored for the pod's screw and counterbored from below, and the holes through.
fn plate(n: &Numbers) -> Result<Solid> {
    let (z0, z1) = n.pair("plate_z")?;
    let disc = Solid::cylinder(v3(0.0, 0.0, z0), V3::Z, n.f("foot_radius")?, z1 - z0)?;
    let (h, chamfer) = (n.f("base_pedestal_height")?, n.f("base_pedestal_chamfer")?);
    let mut stock = vec![disc];
    let mut cutters = through(n, z0, z1)?;
    for c in rows(n.get("base_pod_centers")?)? {
        let (x, y) = pair(c)?;
        // Standing from inside the disc, so its foot meets no face of it.
        let mid = 0.5 * (z0 + z1);
        let pedestal = Solid::cylinder(v3(x, y, mid), V3::Z, n.f("base_pedestal_dia")? / 2.0, h - mid)?;
        stock.push(pedestal.chamfer(&pedestal.edges(">Z")?, chamfer)?);
        let shank = n.f("base_pod_shank_dia")? / 2.0;
        cutters.push(Solid::cylinder(v3(x, y, z0 - PAST), V3::Z, shank, h - z0 + 2.0 * PAST)?);
        let counterbore = n.f("base_pod_counterbore_dia")? / 2.0;
        cutters.push(Solid::cylinder(v3(x, y, z0 - PAST), V3::Z, counterbore, n.f("base_screw_counterbore_depth")? + PAST)?);
    }
    Solid::union_all(&stock)?.cut_all(&cutters)
}

/// The gasket under the plate, with the same holes through.
fn gasket(n: &Numbers) -> Result<Solid> {
    let (z0, z1) = n.pair("gasket_z")?;
    Solid::cylinder(v3(0.0, 0.0, z0), V3::Z, n.f("foot_radius")?, z1 - z0)?.cut_all(&through(n, z0, z1)?)
}

/// The cover as it sits on the tip: its plate hollowed for the display, opened for the glass and
/// round the neck, with its lips. `open` runs the cavity on up through the bezel.
fn seated_cover(n: &Numbers, neck: &Gooseneck, open: bool) -> Result<Solid> {
    let half_x = n.f("cover_half_x")?;
    let outer = neck.cradle_prism(half_x, (0.0, n.f("cover_length")?), n.pair("cover_n")?, 0.0)?;
    let window = neck.cradle_prism(
        n.f("cover_window_half_x")?,
        n.pair("cover_window_s")?,
        n.pair("cover_window_n")?,
        n.f("cover_window_corner_r")?,
    )?;
    let (_, _, normal) = neck.tip_frame();
    let arch = display::neck_round(n, neck, n.f("cover_neck_clearance_r")?)?.translate(normal * n.f("cover_arch_lift")?);
    let band = neck.cradle_prism(
        half_x,
        (n.f("display_clip_s_bottom")?, n.f("display_clip_s_top")?),
        (n.f("display_clip_bottom_n")?, n.f("display_clip_top_n")?),
        0.0,
    )?;
    let lips = display::lips(&band, n, neck, n.f("cover_lip_r")?, n.f("cover_lip_relief")?)?;
    outer.cut_all(&[cavity(n, neck, open)?, window, arch])?.union(&lips)
}

/// The display's cavity under the bezel, from the front wall to the rear: its sides stand
/// straight from under the cover to the display's feet and lean in from there to the bezel.
/// `open` runs them on along their lean, up through the bezel.
fn cavity(n: &Numbers, neck: &Gooseneck, open: bool) -> Result<Solid> {
    let mut sections: Vec<(f64, f64)> = rows(n.get("cover_cavity_sections")?)?.iter().map(pair).collect::<Result<_>>()?;
    if open {
        let &[.., (x1, n1), (x2, n2)] = &sections[..] else { bail!("a cavity of fewer than two sections") };
        sections.push((x2 + (x2 - x1) / (n2 - n1) * PAST, n2 + PAST));
    }
    let (s0, s1) = n.pair("cover_cavity_s")?;
    let (tip, up, normal) = neck.tip_frame();
    let at = |x: f64, nn: f64| tip + V3::X * x + up * s0 + normal * nn;
    let mut outline: Vec<V3> = sections.iter().map(|&(hx, nn)| at(hx, nn)).collect();
    outline.extend(sections.iter().rev().map(|&(hx, nn)| at(-hx, nn)));
    Solid::extrude(&Region::polygon(outline), up, up * (s1 - s0))
}
