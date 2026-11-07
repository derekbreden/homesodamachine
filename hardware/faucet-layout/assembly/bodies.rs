//! The assembly's bodies in the order the bench lists them: every tube along its centreline, the
//! cable, the display on the tip, the slab and the plate the stack clamps through, the foam and
//! the braid, the base's screws and inserts, and the printed parts and vendor bodies it stands in
//! place, each read from its own files.
use crate::legs::{self, path};
use crate::{Variant, metrics, ribbon};
use anyhow::{Context, Result, bail, ensure};
use hsm_faucet::{p3, wrapped};
use hsm_faucet_assembly_numbers::*;
use hsm_faucet_numbers::interface::*;
use hsm_faucet_numbers::{Color, catalog, countertop, shell};
use hsm_kernel::*;
use serde_json::Value;
use std::path::Path as FilePath;

/// A body of the assembly and its colour.
pub struct Shown {
    pub name: String,
    pub color: Color,
    pub solid: Solid,
}

/// The XY plane at height `z`.
fn level(z: f64) -> Plane {
    Plane::XY.at(v3(0.0, 0.0, z))
}

/// A file the step reads, named for the trace.
fn read(path: &str) -> Result<Vec<u8>> {
    let bytes = std::fs::read(path).with_context(|| format!("reading {path}"))?;
    hsm_kernel::reads::read(FilePath::new(path), &bytes);
    Ok(bytes)
}

/// A tube of radius `r` along `legs`, bored `bore` when it has one.
fn tube(legs: &[legs::Leg], r: f64, bore: Option<f64>) -> Result<Solid> {
    let path = path(legs)?;
    let t = match *path.legs.first().context("a path of no legs")? {
        Leg::Line { a, b } => (b - a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(a - c).unit(),
        Leg::Curve { k, .. } => path.curves[k].derivative(path.curves[k].range().0).unit(),
    };
    let across = if t.cross(V3::X).norm() > 1e-6 { V3::X } else { V3::Y };
    let mut section = Profile::circle(v2(0.0, 0.0), r);
    if let Some(bore) = bore {
        section = section.with_hole(Loop::circle(v2(0.0, 0.0), bore));
    }
    Plane::new(path.legs[0].start(), across, t)?.sweep(&section, &path)
}

/// A ring about `c` from `r_in` out to `r`, standing from `z0` to `z1`.
fn annulus(c: V2, r: f64, r_in: f64, z0: f64, z1: f64) -> Result<Solid> {
    level(z0).extrude(&Profile::circle(c, r).with_hole(Loop::circle(c, r_in)), z1 - z0)
}

/// Every solid of a STEP the assembly stands in place, as one, moved by `at`.
fn part(step: &str, at: V3) -> Result<Solid> {
    let bodies = import::step(step)?;
    Ok(Solid::compose(&bodies.into_iter().map(|b| b.solid).collect::<Vec<_>>()).translate(at))
}

/// An M3 socket-head screw where it seats under the base: its thread a plain shaft, its hex
/// socket cut up into the head from just below its underside.
fn screw(x: f64, y: f64) -> Result<Solid> {
    let seat = shell::BASE_SCREW_SEAT_Z;
    let head_height = shell::BASE_SCREW_HEAD_HEIGHT;
    let head_bottom = seat - head_height;
    let shaft = level(seat).extrude(&Profile::circle(v2(x, y), BASE_SCREW_SHAFT_R), shell::BASE_SCREW_LENGTH)?;
    let head = level(head_bottom).extrude(&Profile::circle(v2(x, y), BASE_SCREW_HEAD_R), head_height)?;
    let socket_d = BASE_SCREW_SOCKET_AF / (std::f64::consts::PI / 6.0).cos();
    let hex = Profile::new(Loop::regular(v2(x, y), 6, socket_d));
    let socket = level(head_bottom - BASE_SCREW_SOCKET_BELOW).extrude(&hex, BASE_SCREW_SOCKET_DEPTH)?;
    shaft.union(&head)?.cut(&socket)
}

/// A box on the display's axis, `width` by `length`, its corners along Z rounded `r`, from `z0` to
/// `z1`.
fn rounded(width: f64, length: f64, r: f64, z0: f64, z1: f64) -> Result<Solid> {
    level(z0).extrude(&Profile::new(Loop::rounded_rect(v2(0.0, 0.0), width, length, r)?), z1 - z0)
}

/// The display and its screen on the tip: the housing on its PCB with the components under it
/// and the screen's recess in its face, drawn in the display's own frame, then turned down the
/// tip and set on the feet pads.
fn display() -> Result<(Solid, Solid)> {
    let components: Value = serde_json::from_slice(&read(DISPLAY_COMPONENTS)?)?;
    let buttons: Value = serde_json::from_slice(&read(DISPLAY_BUTTONS)?)?;
    let buttons = buttons["buttons"].as_array().context("the display's buttons")?;
    let mut parts = vec![
        rounded(DISPLAY_PCB_WIDTH, DISPLAY_PCB_LENGTH, DISPLAY_PCB_CORNER_R, DISPLAY_PCB_BOTTOM_Z, DISPLAY_PCB_TOP_Z)?,
        rounded(DISPLAY_HOUSING_WIDTH, DISPLAY_HOUSING_LENGTH, DISPLAY_CORNER_R, DISPLAY_PCB_TOP_Z, DISPLAY_TOTAL_DEPTH)?,
    ];
    let f = |v: &Value| v.as_f64().context("a display component's number");
    for row in components["components"].as_array().context("the display's components")? {
        if buttons.iter().any(|b| b["vendor_solid_index"] == row["vendor_solid_index"]) {
            continue;
        }
        parts.push(if let Some(c) = row.get("conservative_cylinder") {
            let (x, y, z0) = (f(&c["center_xy_mm"][0])?, f(&c["center_xy_mm"][1])?, f(&c["z_mm"][0])?);
            Solid::cylinder(v3(x, y, z0), V3::Z, f(&c["radius_mm"])?, f(&c["z_mm"][1])? - z0)?
        } else {
            let corner = |k: usize| -> Result<V3> {
                let b = &row["bounds_mm"][k];
                Ok(v3(f(&b[0])?, f(&b[1])?, f(&b[2])?))
            };
            let (lo, hi) = (corner(0)?, corner(1)?);
            Solid::cuboid(lo, v3(hi.x, hi.y, hi.z.max(DISPLAY_PCB_BOTTOM_Z + 0.02)))
        });
    }
    for button in buttons {
        let file = button["file"].as_str().context("a button's file")?;
        parts.push(part(&format!("{DISPLAY_REFERENCE}/{file}"), V3::ZERO)?);
    }
    let screen_z = DISPLAY_TOTAL_DEPTH - DISPLAY_SCREEN_DEPTH;
    let pocket = rounded(DISPLAY_SCREEN_WIDTH, DISPLAY_SCREEN_LENGTH, DISPLAY_SCREEN_CORNER_R, screen_z, screen_z + DISPLAY_SCREEN_DEPTH + 1.0)?;
    let body = Solid::union_all(&parts)?.cut(&pocket)?;
    let screen = rounded(DISPLAY_SCREEN_WIDTH, DISPLAY_SCREEN_LENGTH, DISPLAY_SCREEN_CORNER_R, screen_z, screen_z + DISPLAY_SCREEN_DEPTH)?;
    // Turned down the tip and seated on the feet pads.
    let turn = (shell::GN_BEND1_SWEEP_RAD + shell::GN_BEND2_SWEEP_RAD - std::f64::consts::PI / 2.0) * (180.0 / std::f64::consts::PI);
    let [end, up, normal] = shell::tip_frame();
    let along = DISPLAY_HOUSING_LENGTH / 2.0 + shell::display_s_bottom() + shell::DISPLAY_CRADLE_CLEARANCE;
    let mut seat = [0.0; 3];
    for i in 0..3 {
        seat[i] = end[i] + normal[i] * shell::DISPLAY_FEET_N;
        seat[i] += up[i] * along;
    }
    let on_tip = |s: &Solid| s.rotate(V3::ZERO, V3::X, turn).translate(p3(seat));
    Ok((on_tip(&body), on_tip(&screen)))
}

/// The cut plate, off the DXF the laser reads, its x turned onto world Y.
fn under_counter_plate() -> Result<Solid> {
    let outline = dxf::read("hardware/cut-parts/faucet/under-counter-plate/under-counter-plate.dxf")?;
    let z = countertop::BOTTOM_Z - UNDER_COUNTER_PLATE_THICKNESS;
    Ok(level(z).extrude(&outline, UNDER_COUNTER_PLATE_THICKNESS)?.rotate(V3::ZERO, V3::Z, 90.0))
}

/// A loft section of the braid's neck: the hull round `circles` at `z`, its first edge walked
/// back and the rest reversed, as a bottom face walks them.
fn hull_bottom(circles: &[[f64; 3]], z: f64) -> Result<LoftSection> {
    let mut section = hull_section(&wrapped(circles), &level(z))?;
    section.edges = std::iter::once(section.edges[0].reversed()).chain(section.edges[1..].iter().rev().map(LoftEdge::reversed)).collect();
    Ok(section)
}

/// The braid: over the gather and over the pack, each the hull round its tubes at the lane and
/// at the lane and the wall, ruled across the neck from the bare tubes onto the organizer's puck,
/// and round the puck.
fn sleeve() -> Result<Solid> {
    let run = |outer: Vec<[f64; 3]>, inner: Vec<[f64; 3]>, z0: f64, z1: f64| -> Result<Solid> {
        let outer = level(z0).extrude(&hsm_faucet::hull(&wrapped(&outer))?, z1 - z0)?;
        outer.cut(&level(z0).extrude(&hsm_faucet::hull(&wrapped(&inner))?, z1 - z0)?)
    };
    let (umbilical, gather) = (umbilical_z_bottom(), gather_start_z());
    let [cx, cy] = hsm_umbilical_organizer_numbers::CENTRE_XY;
    let od = hsm_umbilical_organizer_numbers::OD;
    let neck = |wall: f64| -> Result<Vec<LoftSection>> {
        let plane = Plane::new(v3(cx, cy, ORGANIZER_BOTTOM_Z), V3::X, V3::Z)?;
        let r = od / 2.0 + wall;
        Ok(vec![hull_bottom(&bare_circles(CABLE_LANE + wall), gather)?, LoftSection::ellipse(plane.origin, plane.x * r, plane.y * r)])
    };
    let neck = Solid::thru_sections(&neck(SLEEVE_WALL)?, false)?.cut(&Solid::thru_sections(&neck(0.0)?, false)?)?;
    let ring = annulus(v2(cx, cy), od / 2.0 + SLEEVE_WALL, od / 2.0, ORGANIZER_BOTTOM_Z, ORGANIZER_TOP_Z)?;
    Solid::union_all(&[
        run(gather_circles(CABLE_LANE + SLEEVE_WALL), gather_circles(CABLE_LANE), umbilical, gather)?,
        run(bundle_circles(CABLE_LANE + SLEEVE_WALL), bundle_circles(CABLE_LANE), SLEEVE_Z_BOTTOM, umbilical)?,
        neck,
        ring,
    ])
}

/// A collar threaded on its tail and the word lettered in it. The body that runs the collar's
/// whole length is the collar and every other body a letter; the collar's +Y, outboard along its
/// tube, is laid down toward the tail and its flag turned out of the bundle, away from the pack's
/// centre.
fn collar(which: &str, x: f64, y: f64, sleeve_center_y: f64) -> Result<(Solid, Solid)> {
    let length = hsm_tube_collar_numbers::LENGTH;
    let step = format!("hardware/printed-parts/faucet/tube-collar/tube-collar-{which}.step");
    let mut bodies = part(&step, V3::ZERO)?.components();
    let full: Vec<usize> = (0..bodies.len()).filter(|&i| (bodies[i].bounds().size().y - length).abs() < 1e-3).collect();
    ensure!(full.len() == 1 && bodies.len() >= 2, "{step} holds {} bodies, {} of them running the whole {length} mm", bodies.len(), full.len());
    let body = bodies.remove(full[0]);
    let (ux, uy) = (x - 0.0, y - sleeve_center_y);
    let reach = ux.hypot(uy);
    let azimuth = (-ux / reach).atan2(uy / reach) * (180.0 / std::f64::consts::PI);
    let threaded = |s: &Solid| s.rotate(V3::ZERO, V3::X, -90.0).rotate(V3::ZERO, V3::Z, azimuth).translate(v3(x, y, collar_top_z()));
    Ok((threaded(&body), threaded(&Solid::compose(&bodies))))
}

/// The lever's place: its back at the donor's, its top at the donor's top, from its own bounds.
fn lever_at() -> Result<V3> {
    let frame: Value = serde_json::from_slice(&read(LEVER_FRAME)?)?;
    let max = &frame["bounds_mm"][1];
    let f = |v: &Value| v.as_f64().context("the lever's bounds");
    Ok(v3(0.0, LEVER_AFT_Y - f(&max[1])?, LEVER_TOP_Z - f(&max[2])?))
}

/// A colour by sRGB fractions.
fn srgb(r: f64, g: f64, b: f64) -> Color {
    catalog::linear([r, g, b])
}

/// A tube's spool colour: its port's.
fn spool(chips: &Value, fluid: &str) -> Result<Color> {
    let rgb = &chips["port_colors"][fluid];
    let channel = |i: usize| rgb[i].as_f64().map(|c| c / 255.0).context("a port colour");
    Ok(srgb(channel(0)?, channel(1)?, channel(2)?))
}

/// A collar's chip colour and its word's: the filaments its chip on the wall prints in.
fn collar_colors(chips: &Value, which: &str) -> Result<(Color, Color)> {
    let (_, fluid) = hsm_tube_collar_numbers::word_and_fluid(which);
    let chip = hsm_shared_data::color::rgb8_linear(&chips["chip_filaments"][fluid][1], false)?;
    let word = hsm_shared_data::color::rgb8_linear(&chips["chip_word_colors"][fluid], false)?;
    Ok((chip, word))
}

/// The printed parts each variant stands in place: its shell's base, its plate, its gasket and its
/// seated display cover.
fn printed(variant: Variant) -> [(&'static str, &'static str); 4] {
    match variant {
        Variant::Sculpted => [
            ("shell_base", "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base.step"),
            ("above_counter_plate", "hardware/printed-parts/faucet/above-counter-plate/above-counter-plate.step"),
            ("above_counter_gasket", "hardware/printed-parts/faucet/above-counter-gasket/above-counter-gasket.step"),
            ("faucet-display-cover-seated", "hardware/printed-parts/faucet/faucet-display-cover/faucet-display-cover-seated.step"),
        ],
        Variant::Industrial => [
            ("shell_base", "hardware/printed-parts/faucet/industrial/industrial-shell-base.step"),
            ("above_counter_plate", "hardware/printed-parts/faucet/industrial/industrial-above-counter-plate.step"),
            ("above_counter_gasket", "hardware/printed-parts/faucet/industrial/industrial-above-counter-gasket.step"),
            ("faucet-display-cover-seated", "hardware/printed-parts/faucet/industrial/industrial-display-cover-seated.step"),
        ],
    }
}

/// The assembly's bodies.
pub fn bodies(variant: Variant) -> Result<Vec<Shown>> {
    let chips = hsm_shared_data::color::chips()?;
    let black_lldpe = spool(&chips, "flavor")?;
    let donor = catalog::color("M_DONOR_BLACK");
    let faucet_black = catalog::faucet_black();
    let tpu = catalog::tpu_black();
    let [base, plate, gasket, cover] = printed(variant);
    let mut out = vec![];
    let mut add = |name: &str, color: Color, solid: Solid| out.push(Shown { name: name.to_owned(), color, solid });

    add("westbrass", donor, part("hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step", V3::ZERO)?);
    add("soda_faucet_tube", black_lldpe, tube(&legs::soda_legs(), SODA_FAUCET_TUBE_R, None)?);
    let ring_at = v3(0.0, PORT_CENTER_DEPTH, SODA_FAUCET_TUBE_Z_BOTTOM - hsm_tpu_o_ring_numbers::CAP_THICKNESS);
    add("tpu_o_ring", tpu, part("hardware/printed-parts/faucet/tpu-o-ring/tpu-o-ring.step", ring_at)?);
    for s in [1.0, -1.0] {
        let side = if s > 0.0 { "pos_x" } else { "neg_x" };
        add(&format!("flavor_tube_{side}"), black_lldpe, tube(&legs::flavor_run(s)?, FLAVOR_TUBE_R, None)?);
        add(&format!("flavor_umbilical_tube_{side}"), black_lldpe, tube(&legs::flavor_umbilical(s), FLAVOR_TUBE_R, None)?);
    }
    let soda = Solid::cylinder(v3(0.0, 0.0, UMBILICAL_TAIL_Z), V3::Z, SODA_UMBILICAL_TUBE_R, SODA_UMBILICAL_TUBE_Z_TOP - UMBILICAL_TAIL_Z)?;
    add("soda_umbilical_tube", spool(&chips, "carb")?, soda);
    add("drain_tube", spool(&chips, "drain")?, tube(&legs::drain_legs()?, DRAIN_TUBE_R, Some(DRAIN_TUBE_R_IN))?);
    add("lever", donor, part("hardware/printed-parts/faucet/lever-replica/lever-replica.step", lever_at()?)?);
    add(plate.0, faucet_black, part(plate.1, V3::ZERO)?);
    add(gasket.0, tpu, part(gasket.1, V3::ZERO)?);
    add(base.0, faucet_black, part(base.1, V3::ZERO)?);
    add("shell_tip", faucet_black, part("hardware/printed-parts/faucet/faucet-shell/faucet-shell-tip.step", V3::ZERO)?);
    add(cover.0, faucet_black, part(cover.1, V3::ZERO)?);
    let brass = catalog::color("M_BRASS");
    for (i, [x, y]) in shell::BASE_POD_CENTERS.iter().enumerate() {
        add(&format!("base_screw_{}", i + 1), donor, screw(*x, *y)?);
        let z0 = shell::BASE_INSERT_BOTTOM_Z;
        let insert = annulus(v2(*x, *y), shell::BASE_INSERT_OUTER_DIA / 2.0, BASE_INSERT_INNER_R, z0, z0 + shell::BASE_INSERT_LENGTH)?;
        add(&format!("base_insert_{}", i + 1), brass, insert);
    }
    let (display, screen) = display()?;
    add("faucet_display", catalog::color("C_FAUCET_DISPLAY"), display);
    add("faucet_display_screen", catalog::color("C_FAUCET_DISPLAY_GLASS"), screen);
    add("display_signal_ribbon", catalog::color("M_SILICONE_BLACK"), ribbon::ribbon()?);
    let hole = Loop::circle(v2(0.0, countertop::hole_center_y()), countertop::HOLE_RADIUS);
    let slab = level(countertop::BOTTOM_Z).extrude(&Profile::rect(v2(0.0, 0.0), countertop::SLAB, countertop::SLAB).with_hole(hole), countertop::TOP_Z - countertop::BOTTOM_Z)?;
    // The kitchen's slab is context, not a part.
    add("countertop", srgb(0.55, 0.55, 0.58), slab);
    add("under_counter_plate", catalog::color("M_STAINLESS"), under_counter_plate()?);
    let foam = annulus(v2(0.0, 0.0), FOAM_R, SODA_UMBILICAL_TUBE_R, FOAM_Z_BOTTOM, foam_z_top())?;
    add("cold_line_foam", catalog::color("M_NITRILE_BLACK"), foam);
    add("umbilical_sleeve", catalog::color("M_PET_BRAID"), sleeve()?);
    let [cx, cy] = hsm_umbilical_organizer_numbers::CENTRE_XY;
    let organizer_at = v3(cx, cy, ORGANIZER_TOP_Z - hsm_umbilical_organizer_numbers::LENGTH);
    add("umbilical-organizer", faucet_black, part("hardware/printed-parts/faucet/umbilical-organizer/umbilical-organizer.step", organizer_at)?);
    let (_, pack_centre, _) = metrics::hull(&wrapped(&bundle_circles(CABLE_LANE)))?;
    for (which, x, y) in collar_tails() {
        let name = format!("collar_{}", which.replace('-', "_"));
        let (body, word) = collar(which, x, y, pack_centre.y)?;
        let (chip, lettering) = collar_colors(&chips, which)?;
        add(&name, chip, body);
        add(&format!("{name}_word"), lettering, word);
    }
    if out.iter().any(|s| s.solid.components().is_empty()) {
        bail!("an assembly body came out empty");
    }
    Ok(out)
}
