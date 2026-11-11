//! The Industrial faucet: the shell's gooseneck and cutters on round stock of its own below the
//! zone-5 seam (a foot disc, a body over the Westbrass and the neck standing on it), its round
//! above-counter plate and gasket, and its rectangular display cover, cut as it sits on the tip,
//! which the Industrial assembly stands in place, and printed with its wings leaned in.
//! The approved lowered head exports the exact production tip and both cover shapes.
//!
//!     industrial-faucet [<output directory>]
use anyhow::{Context, Result, ensure};
use hsm_faucet::shell::{PAST, level, pieces, shell_from};
use hsm_faucet::{Gooseneck, counter, display};
use hsm_faucet_numbers::catalog;
use hsm_faucet_numbers::shell::*;
use hsm_industrial_faucet_numbers as industrial;
use hsm_kernel::part::write_shown;
use hsm_kernel::*;
use hsm_print_payload::printed;
use std::path::Path;

const APPROVED_HEAD_DIR: &str = "hardware/printed-parts/faucet/industrial/production/2026-10-25";

fn write_approved_head(out: &Path) -> Result<()> {
    let source = Path::new(APPROVED_HEAD_DIR);
    let read = |member: &str| -> Result<Vec<u8>> {
        let path = source.join(member);
        let data = std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?;
        reads::read(&path, &data);
        Ok(data)
    };
    let black = Some(catalog::faucet_black());
    for (name, step_source, stl_source, printable) in [
        ("industrial-production-display-cover", "sculpted-display-cover-print.step", "sculpted-display-cover.stl", true),
        ("industrial-production-display-cover-seated", "sculpted-display-cover-seated.step", "sculpted-display-cover-seated.stl", false),
        ("industrial-production-shell-tip", "faucet-shell-tip.step", "faucet-shell-tip.stl", true),
    ] {
        let step = read(step_source)?;
        let stl = read(stl_source)?;
        let mesh = printed::payload_for(name, black, &step, &stl)?;
        printed::keep(&out.join(format!("{name}.step")), &step)?;
        printed::keep(&out.join(format!("{name}.step.mesh")), &mesh)?;
        if printable {
            printed::keep(&out.join(format!("{name}.stl")), &stl)?;
        }
    }
    Ok(())
}

fn main() -> Result<()> {
    let out = printed::out_dir("hardware/printed-parts/faucet/industrial")?;
    let neck = Gooseneck::shell();
    let black = Some(catalog::faucet_black());
    let seated = seated_cover(&neck, false)?;
    let open = seated_cover(&neck, true)?;
    let cover = display::relaxed(&neck, &seated, &open, industrial::BEZEL_N_BOTTOM, industrial::wing_slope())?;
    // The round foot the plate and gasket share.
    let disc = |z0: f64, z1: f64| Solid::cylinder(v3(0.0, 0.0, z0), V3::Z, industrial::FOOT_RADIUS, z1 - z0);
    let printed_pieces = [
        ("industrial-shell-base", shell_base(&neck)?, black),
        ("industrial-display-cover", cover, black),
        ("industrial-above-counter-plate", counter::plate(disc)?, black),
        ("industrial-above-counter-gasket", counter::gasket(disc)?, Some(catalog::tpu_black())),
    ];
    for (name, solid, color) in &printed_pieces {
        ensure!(solid.components().len() == 1, "{name} is not one solid");
        println!("{}", printed::write(&out, name, Body { name, color: *color, solid })?);
    }
    let seated_name = "industrial-display-cover-seated";
    println!("{}", write_shown(&out, seated_name, &[Body { name: seated_name, color: black, solid: &seated }])?);
    write_approved_head(&out)?;
    Ok(())
}

/// The base: the shell's gooseneck and cutters on the Industrial's own stock below the seam, its
/// lever corridor carried up to the top of the body, split from the tip as the shell is.
fn shell_base(neck: &Gooseneck) -> Result<Solid> {
    let (foot_top, body_top, seam) = (industrial::FOOT_TOP, industrial::BODY_TOP, ZONE5_Z_TOP);
    let foot = Solid::cylinder(V3::ZERO, V3::Z, industrial::FOOT_RADIUS, foot_top)?;
    let body = Solid::cylinder(v3(0.0, industrial::BODY_CENTER_Y, foot_top), V3::Z, industrial::BODY_RADIUS, body_top - foot_top)?;
    let ring = Profile::circle(v2(0.0, industrial::NECK_CENTER_Y), industrial::NECK_RADIUS);
    let stem = level(body_top).extrude(&ring, seam + industrial::NECK_JOIN_OVERLAP - body_top)?;
    let stock = Solid::union_all(&[foot, body, stem])?;
    let xh = LEVER_CLEARANCE_X_HALF;
    let lever = Solid::cuboid(v3(-xh, LEVER_INSERTION_FRONT_Y, LEVER_REST_TOP_Z), v3(xh, FILL_Y_MIN, body_top));
    let full = shell_from(neck, stock, &ring.place(&level(seam)), &[lever])?;
    Ok(pieces(neck, &full)?.0)
}

/// The cover as it sits on the tip: its plate hollowed for the display, opened for the glass and
/// round the neck, with its lips. `open` runs the cavity on up through the bezel.
fn seated_cover(neck: &Gooseneck, open: bool) -> Result<Solid> {
    let half_x = industrial::COVER_WIDTH / 2.0;
    let outer = neck.cradle_prism(half_x, (0.0, industrial::COVER_LENGTH), (industrial::COVER_N_BOTTOM, industrial::COVER_N_TOP), 0.0)?;
    let [s0, s1] = industrial::window_s();
    let [n0, n1] = industrial::window_n();
    let window = neck.cradle_prism(industrial::WINDOW_HALF_X, (s0, s1), (n0, n1), industrial::WINDOW_CORNER_R)?;
    let (_, _, normal) = neck.tip_frame();
    let arch = display::neck_round(neck, industrial::neck_clearance_r())?.translate(normal * industrial::WING_EXTENSION);
    let band = neck.cradle_prism(
        half_x,
        (display_clip_s_bottom(), display_clip_s_top()),
        (DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N),
        0.0,
    )?;
    let lips = display::lips(&band, neck, industrial::LIP_R, industrial::LIP_RELIEF)?;
    outer.cut_all(&[cavity(neck, open)?, window, arch])?.union(&lips)
}

/// The display's cavity under the bezel, from the front wall to the rear: its sides stand
/// straight from under the cover to the display's feet and lean in from there to the bezel.
/// `open` runs them on along their lean, up through the bezel.
fn cavity(neck: &Gooseneck, open: bool) -> Result<Solid> {
    let mut sections: Vec<(f64, f64)> = industrial::cavity_sections().iter().map(|&[x, n]| (x, n)).collect();
    if open {
        let (x1, n1) = sections[sections.len() - 2];
        let (x2, n2) = sections[sections.len() - 1];
        sections.push((x2 + (x2 - x1) / (n2 - n1) * PAST, n2 + PAST));
    }
    let [s0, s1] = industrial::COVER_CAVITY_S;
    let (tip, up, normal) = neck.tip_frame();
    let at = |x: f64, nn: f64| tip + V3::X * x + up * s0 + normal * nn;
    let mut outline: Vec<V3> = sections.iter().map(|&(hx, nn)| at(hx, nn)).collect();
    outline.extend(sections.iter().rev().map(|&(hx, nn)| at(-hx, nn)));
    Solid::extrude(&Region::polygon(outline), up, up * (s1 - s0))
}
