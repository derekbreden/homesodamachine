//! The faucet shell's stock and every cutter it is cut by, from the numbers `faucet_shell.py`
//! writes: the Sculpted shell lofts its lower stock up onto the neck, and the Industrial stands
//! its own cylinders in its place (`shell_from`), under the same gooseneck and the same cutters.
use crate::{Gooseneck, circles, floats, hull, pair, point, points2, rows};
use anyhow::{Context, Result, anyhow};
use hsm_kernel::part::Numbers;
use hsm_kernel::profile::RLoop;
use hsm_kernel::*;

/// How far a cutter that opens through the stock's outside runs on past it, so that its end
/// meets no face of the stock.
pub const PAST: f64 = 1.0;

/// The ellipse CadQuery's `ellipse(rx, ry)` draws about `c`, OCCT's x on its major axis.
fn ellipse(c: V3, rx: f64, ry: f64) -> LoftSection {
    if ry > rx {
        LoftSection::ellipse(c, v3(0.0, ry, 0.0), v3(-rx, 0.0, 0.0))
    } else {
        LoftSection::ellipse(c, v3(rx, 0.0, 0.0), v3(0.0, ry, 0.0))
    }
}

/// `region` moved by `d`.
pub fn moved(region: &Region, d: V3) -> Region {
    Region {
        loops: region
            .loops
            .iter()
            .map(|lp| RLoop { pts: lp.pts.iter().map(|&p| p + d).collect(), seg: lp.seg.clone() })
            .collect(),
        curves: region
            .curves
            .iter()
            .map(|&c| match c {
                Curve::Circle { c, axis, r } => Curve::Circle { c: c + d, axis, r },
                other => other,
            })
            .collect(),
    }
}

/// A smooth loft through `sections`, and its two end rings for the solids that meet it.
fn loft(sections: &[LoftSection]) -> Result<(Solid, Region, Region)> {
    let surface = SmoothLoft::new(&compatible(sections)?)?;
    let (us, vs) = surface.grid();
    Ok((surface.solid_on(&us, &vs)?, surface.end_region(false, &us), surface.end_region(true, &us)))
}

/// The XY plane at height `z`.
pub fn level(z: f64) -> Plane {
    Plane::XY.at(v3(0.0, 0.0, z))
}

/// The YZ plane at `x`: drawn in (world Y, world Z), extruded along +X.
fn side(x: f64) -> Result<Plane> {
    Plane::new(v3(x, 0.0, 0.0), V3::Y, V3::X)
}

/// The oval lower shell lofted up onto the round neck and the neck's land standing on it to the
/// zone-5 seam, with the neck's ring at the seam, which the gooseneck is swept from.
pub fn lower_outer(n: &Numbers) -> Result<(Solid, Region)> {
    let mut sections = vec![];
    for row in rows(n.get("lower_outer_sections")?)? {
        match floats(row).as_deref() {
            Some([z, w, d, cy]) => sections.push(ellipse(v3(0.0, *cy, *z), w / 2.0, d / 2.0)),
            _ => return Err(anyhow!("{row} is not a lower outer section")),
        }
    }
    let neck_z = n.f("lower_neck_z")?;
    let r = n.f("tube_shell_outer_r")?;
    let c = v3(0.0, n.f("soda_faucet_tube_y")? + n.f("tube_shell_center_y")?, neck_z);
    sections.push(LoftSection::ellipse(c, v3(r, 0.0, 0.0), v3(0.0, r, 0.0)));
    let (body, _, ring) = loft(&sections)?;
    let seam = n.f("zone5_z_top")?;
    let land = Solid::extrude(&ring, V3::Z, v3(0.0, 0.0, seam + n.f("neck_land_overrun")? - neck_z))?;
    Ok((body.union(&land)?, moved(&ring, v3(0.0, 0.0, seam - neck_z))))
}

/// Four bearing pads under the display, their inner walls flush with the open channel.
pub fn feet_pads(n: &Numbers, neck: &Gooseneck) -> Result<Vec<Solid>> {
    let h = n.f("display_foot_pad_width")? / 2.0;
    let feet = n.f("display_feet_n")?;
    let depth = n.f("display_foot_pad_depth")?;
    let channel = n.f("display_channel_half_width")?;
    let mut pads = vec![];
    for c in rows(n.get("display_foot_centers")?)? {
        let (x, s) = pair(c)?;
        let (outer, inner) = (x.abs() + h, (x.abs() - h).min(channel));
        let pad = neck.cradle_prism((outer - inner) / 2.0, (s - h, s + h), (feet - depth, feet), 0.0)?;
        pads.push(pad.translate(v3(((outer + inner) / 2.0).copysign(x), 0.0, 0.0)));
    }
    Ok(pads)
}

/// The Westbrass bore, a cylinder standing from `z0`.
fn bore(n: &Numbers, z0: f64, h: f64) -> Result<Solid> {
    let c = v3(n.f("westbrass_bore_x")?, n.f("westbrass_bore_y")?, z0);
    Solid::cylinder(c, V3::Z, n.f("westbrass_bore_diameter")? / 2.0, h)
}

/// The flavor-tube pill, its -Y side filled out flat.
fn flavor_pill(n: &Numbers, z0: f64, h: f64) -> Result<Solid> {
    let (x, y) = n.pair("flavor_pill_center")?;
    let (l, w) = (n.f("pill_length_x")?, n.f("pill_width_y")?);
    let fill = y - n.f("flavor_pill_y_minus_edge")?;
    let pill = level(z0).extrude(&Profile::new(Loop::slot(v2(x, y), l, w, 0.0)), h)?;
    pill.union(&level(z0).extrude(&Profile::rect(v2(x, y - fill / 2.0), l, fill), h)?)
}

/// The donor's lower bore and the flavor pill through zone 1.
pub fn zone1_inner(n: &Numbers) -> Result<Solid> {
    let z0 = n.f("zone1_z_bottom")? - PAST;
    let pill = flavor_pill(n, z0, n.f("zone1_height")? + PAST)?;
    bore(n, z0, n.f("zone2_bore_z_bottom")? - z0)?.union(&pill)
}

/// Three pedestal sockets, each with an insert pilot through its roof.
pub fn base_pod_holes(n: &Numbers) -> Result<Vec<Solid>> {
    let mut holes = vec![];
    for c in rows(n.get("base_pod_centers")?)? {
        let (x, y) = pair(c)?;
        let socket = Solid::cylinder(
            v3(x, y, n.f("base_pod_z_bottom")? - PAST),
            V3::Z,
            n.f("base_pod_hole_dia")? / 2.0,
            n.f("base_pod_hole_depth")? + PAST,
        )?;
        let insert = Solid::cylinder(
            v3(x, y, n.f("base_insert_bottom_z")?),
            V3::Z,
            n.f("base_pod_insert_dia")? / 2.0,
            n.f("base_pod_insert_depth")?,
        )?;
        holes.push(socket.union(&insert)?);
    }
    Ok(holes)
}

/// The donor's cross-section in zone 2: its rectangle with coved ±X faces, clipped to the bore,
/// and the flavor pill through.
pub fn zone2_inner(n: &Numbers) -> Result<Solid> {
    let (z0, z1) = (n.f("zone2_bore_z_bottom")?, n.f("zone2_z_top")?);
    let c = v2(n.f("westbrass_bore_x")?, n.f("westbrass_bore_y")?);
    let (wx, wy) = (n.f("westbrass_bore_rect_short_x")?, n.f("westbrass_bore_rect_long_y")?);
    let cove = n.f("cove_r")?;
    let reach = wy / 2.0 + n.f("bore_overrun")?;
    let mut column = level(z0).extrude(&Profile::rect(c, wx, wy), z1 - z0)?;
    for sign in [1.0, -1.0] {
        let flat = c.x + sign * wx / 2.0;
        let filler = level(z0).extrude(&Profile::rect(v2(flat + sign * cove / 2.0, c.y), cove, 2.0 * reach), cove)?;
        column = column.union(&filler)?;
    }
    for sign in [1.0, -1.0] {
        let flat = c.x + sign * wx / 2.0;
        let cutter = Solid::cylinder(v3(flat + sign * cove, c.y - reach, z0 + cove), V3::Y, cove, 2.0 * reach)?;
        column = column.cut(&cutter)?;
    }
    let column = column.intersect(&bore(n, z0, z1 - z0)?)?;
    column.union(&flavor_pill(n, n.f("zone2_z_bottom")?, n.f("zone2_height")?)?)
}

/// The donor's arch clearance either side of the lever, joined behind it to the tube opening.
pub fn zone3_inner(n: &Numbers) -> Result<Solid> {
    let z0 = n.f("zone3_z_bottom")?;
    let (foot, peak) = (n.f("shell_arch_bore_z_foot_top")?, n.f("shell_arch_bore_z_peak")?);
    let (inner, outer) = (n.f("shell_arch_bore_inner_x")?, n.f("shell_arch_bore_outer_x")?);
    let reach = n.f("westbrass_bore_diameter")? / 2.0 + n.f("bore_overrun")?;
    let arch = |x0: f64, dx: f64| -> Result<Solid> {
        let outline = Pen::new(v2(reach, z0))
            .line_to(v2(-reach, z0))
            .line_to(v2(-reach, foot))
            .arc_through(v2(0.0, peak), v2(reach, foot))?
            .close()?;
        side(x0)?.extrude(&Profile::new(outline), dx)
    };
    let bores = arch(inner, outer - inner)?.union(&arch(-outer, outer - inner)?)?;
    let window = Solid::cuboid(v3(-inner, n.f("fill_y_min")?, z0), v3(inner, reach, peak));
    let bores = bores.union(&arch(-inner, 2.0 * inner)?.intersect(&window)?)?;
    bores.intersect(&bore(n, z0, peak - z0)?)
}

/// Open space beyond the square-cut drain mouth.
fn drain_relief(n: &Numbers) -> Result<Solid> {
    let f = n.get("drain_relief")?;
    let (o, x, t) = (point(&f["origin"])?, point(&f["xdir"])?, point(&f["normal"])?);
    let lead = n.f("drain_relief_lead")?;
    let r = n.f("drain_tube_hole_dia")? / 2.0;
    Plane::new(o - t * lead, x, t)?.extrude(&Profile::circle(v2(0.0, 0.0), r), n.f("drip_end_clearance")? + lead)
}

/// The round underside hole into the tube passage.
fn vent_outlet(n: &Numbers) -> Result<Solid> {
    let f = n.get("vent_outlet")?;
    let (o, normal) = (point(&f["origin"])?, point(&f["normal"])?);
    let plane = Plane::new(o + normal * n.f("vent_outlet_offset")?, V3::X, normal)?;
    let depth = n.f("tube_shell_outer_r")? + n.f("wall_thickness_min")?;
    plane.extrude(&Profile::circle(v2(0.0, 0.0), n.f("drip_hole_diameter")? / 2.0), depth)
}

/// The lever's travel, the round relief over its resting top, and the straight front corridor
/// it goes in by.
pub fn lever_clearance(n: &Numbers) -> Result<Solid> {
    let xh = n.f("lever_clearance_x_half")?;
    let plane = side(-xh)?;
    let travel = plane.extrude(&Profile::polygon(&points2(n.get("lever_outline")?)?), 2.0 * xh)?;

    let (fill_y, top) = (n.f("fill_y_min")?, n.f("lever_rest_top_z")?);
    let (r, cz) = (n.f("back_arch_r")?, n.f("back_arch_center_z")?);
    let back = n.f("lever_clearance_y_back")?;
    let front_y = fill_y - (r * r - (top - cz).powi(2)).sqrt();
    let rear_z = cz + (r * r - (back - fill_y).powi(2)).sqrt();
    let mid = 0.5 * ((top - cz).atan2(front_y - fill_y) + (rear_z - cz).atan2(back - fill_y));
    let relief = Pen::new(v2(front_y, top))
        .arc_through(v2(fill_y + r * mid.cos(), cz + r * mid.sin()), v2(back, rear_z))?
        .line_to(v2(back, top))
        .close()?;
    let overhead = plane.extrude(&Profile::new(relief), 2.0 * xh)?;

    let front_y = n.f("lever_insertion_front_y")?;
    let (seam, shoulder) = (n.f("zone5_z_top")?, n.f("zone5_z_bottom")?);
    let shell_r = n.f("shell_outer_r")?;
    let opening = Solid::cuboid(v3(-xh, front_y, top), v3(xh, fill_y, seam));
    let cap = Solid::cylinder(v3(0.0, n.f("zone45_front_y")? + shell_r, top), V3::Z, shell_r, seam - top)?;
    let entry = Solid::cuboid(v3(-xh, front_y, top), v3(xh, fill_y, shoulder));
    Solid::union_all(&[travel, overhead, opening.cut(&cap)?.union(&entry)?])
}

/// The display pocket over the feet, and the open channel under it.
fn display_cavity(n: &Numbers, neck: &Gooseneck, pads: &[Solid]) -> Result<Solid> {
    let s = (n.f("dispense_face_thickness")?, n.f("display_s_top")?);
    let half_x = n.f("display_neck_outer_r")? + n.f("wall_thickness_min")?;
    let device = neck
        .cradle_prism(half_x, s, (n.f("display_seat_reference_n")?, n.f("display_pocket_top_n")?), 0.0)?
        .cut_all(pads)?;
    let channel = neck.cradle_prism(n.f("display_channel_half_width")?, s, (0.0, n.f("display_channel_top_n")?), 0.0)?;
    device.union(&channel)
}

/// The side grooves the display cover's lips snap into.
fn retention_grooves(n: &Numbers, neck: &Gooseneck) -> Result<Solid> {
    let slip = n.f("snap_end_slip")?;
    let band = neck.cradle_prism(
        n.f("display_groove_half_x")?,
        (n.f("display_clip_s_bottom")? - slip, n.f("display_clip_s_top")? + slip),
        (n.f("display_clip_bottom_n")?, n.f("display_clip_top_n")? + n.f("snap_bearing_slip")?),
        0.0,
    )?;
    let core = Profile::circle(v2(0.0, n.f("tube_shell_center_y")?), n.f("display_groove_core_r")?);
    band.cut(&neck.sweep(&core, 0.0, neck.length())?)
}

/// The flat rear cable lane and the opening that gathers the tubes and the cable from the
/// mounting channel into the neck: a smooth loft through the hulls round their clearances,
/// with straight lands below and above it.
pub fn lower_bundle_opening(n: &Numbers) -> Result<Solid> {
    let (z0, z1) = n.pair("signal_lane_z")?;
    let (x, y) = n.pair("signal_lower_exit")?;
    let width = n.f("signal_lane_width")?;
    let lane_slot = Loop::slot(v2(x, y), width, n.f("signal_lane_depth")?, n.f("signal_lower_exit_angle")?);
    let lane = level(z0).extrude(&Profile::new(lane_slot), z1 - z0)?;
    let mut sections = vec![];
    let mut heights = vec![];
    for row in rows(n.get("lower_opening_sections")?)? {
        let z = row["z"].as_f64().context("a lower opening section's height")?;
        sections.push(hull_section(&circles(&row["circles"])?, &level(z))?);
        heights.push(z);
    }
    let (transition, first, last) = loft(&sections)?;
    let bottom = n.f("bundle_land_bottom_z")?;
    let lower = Solid::extrude(&moved(&first, v3(0.0, 0.0, bottom - heights[0])), V3::Z, v3(0.0, 0.0, heights[0] - bottom))?;
    let upper = Solid::extrude(&last, V3::Z, v3(0.0, 0.0, n.f("bundle_land_above")?))?;
    Solid::union_all(&[lane, lower, transition, upper])
}

/// Where station `s` of `faucet_paths` (along the bend from the split joint) falls on the
/// gooseneck.
fn station(n: &Numbers, neck: &Gooseneck, s: f64) -> Result<f64> {
    Ok(neck.at_angle(n.f("joint_angle")? + s / n.f("water_radius")?))
}

/// The shared smooth passage up the neck: the tube and cable hull swept up to where the tubes
/// converge, lofted through their convergence, and swept on to where the cable leaves for the
/// display.
fn upstream_passage(n: &Numbers, neck: &Gooseneck) -> Result<Solid> {
    let mut sections = vec![];
    for row in rows(n.get("passage_sections")?)? {
        let plane = Plane::new(point(&row["origin"])?, point(&row["xdir"])?, point(&row["normal"])?)?;
        sections.push(hull_section(&circles(&row["circles"])?, &plane)?);
    }
    let (converge, first, last) = loft(&sections)?;
    let s0 = n.f("converge_start_s")?;
    let s1 = s0 + n.f("converge_length")?;
    let lower = Solid::sweep(&first, &neck.path(station(n, neck, s0)?, 0.0)?)?;
    let outlet = Solid::sweep(&last, &neck.path(station(n, neck, s1)?, station(n, neck, n.f("ribbon_end_s")?)?)?)?;
    Solid::union_all(&[lower, converge, outlet])
}

/// The soda opening and the flavor capsule beyond where the cable leaves, out to the tip.
fn beverage_outlets(n: &Numbers, neck: &Gooseneck) -> Result<Solid> {
    let start = station(n, neck, n.f("ribbon_end_s")? - n.f("beverage_lead")?)?;
    neck.sweep(&hull(&circles(n.get("beverage_circles")?)?)?, start, neck.length() + PAST)
}

/// The whole shell, before it is split into its two prints.
pub fn shell(n: &Numbers, neck: &Gooseneck) -> Result<Solid> {
    let (lower, seam) = lower_outer(n)?;
    shell_from(n, neck, lower, &seam, &[])
}

/// A shell whose stock below the zone-5 seam is `lower`, with `seam` the ring the gooseneck is
/// swept from, cut by the shell's cutters and `extra`, the variant's own.
pub fn shell_from(n: &Numbers, neck: &Gooseneck, lower: Solid, seam: &Region, extra: &[Solid]) -> Result<Solid> {
    let gooseneck = Solid::sweep(seam, &neck.path(0.0, neck.length())?)?;
    let pads = feet_pads(n, neck)?;
    let mut stock = vec![lower, gooseneck];
    stock.extend(pads.iter().cloned());
    let outer = Solid::union_all(&stock)?;
    let mut cutters = vec![zone1_inner(n)?];
    cutters.extend(base_pod_holes(n)?);
    cutters.push(zone2_inner(n)?);
    cutters.push(zone3_inner(n)?);
    cutters.push(drain_relief(n)?);
    cutters.push(vent_outlet(n)?);
    cutters.push(lever_clearance(n)?);
    cutters.push(display_cavity(n, neck, &pads)?);
    cutters.push(retention_grooves(n, neck)?);
    cutters.push(lower_bundle_opening(n)?);
    cutters.push(upstream_passage(n, neck)?);
    cutters.push(beverage_outlets(n, neck)?);
    cutters.extend(extra.iter().cloned());
    outer.cut_all(&cutters)
}

/// The base and the tip: split square to the bend at the junction, the base's socket opened
/// below it and the tip's plug carried down into it.
pub fn pieces(n: &Numbers, neck: &Gooseneck, full: &Solid) -> Result<(Solid, Solid)> {
    let junction = neck.at_angle(n.f("split_junction_rot")?);
    // Each overlap runs on past the junction, so its end meets no face of the split.
    let past = junction + PAST;
    let (r, cy) = (n.f("tube_shell_outer_r")?, n.f("tube_shell_center_y")?);
    let socket = Profile::circle(v2(0.0, cy), r - n.f("split_socket_shrink")?);
    let socket = neck.sweep(&socket, neck.at_angle(n.f("path_socket_start_rot")?), past)?;
    let plug = Profile::circle(v2(0.0, cy), r - n.f("split_plug_shrink")?);
    let plug = neck.sweep(&plug, neck.at_angle(n.f("path_plug_start_rot")?), past)?;
    let (p, t, _) = neck.frame(junction);
    let base = full.cut(&socket)?.trim(&Plane::new(p, V3::X, -t)?)?;
    let reach = 2.0 * full.bounds().diagonal();
    let above = Plane::new(p, V3::X, t)?.extrude(&Profile::rect(v2(0.0, 0.0), reach, reach), reach)?;
    let tip = full.intersect(&above.union(&plug)?)?;
    Ok((base, tip))
}
