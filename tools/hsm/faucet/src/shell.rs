//! The faucet shell's stock and every cutter it is cut by: the Sculpted shell lofts its lower stock
//! up onto the neck, and the Industrial stands its own cylinders in its place (`shell_from`), under
//! the same gooseneck and the same cutters.
use crate::{Gooseneck, hull, p3, wrapped};
use anyhow::{Result, ensure};
use clipper2_rust::{EndType, FillRule, JoinType, PathD, PathsD, PointD};
use hsm_faucet_numbers::interface::*;
use hsm_faucet_numbers::shell::*;
use hsm_faucet_numbers::{paths, snap};
use hsm_kernel::profile::RLoop;
use hsm_kernel::*;

/// How far a cutter that opens through the stock's outside runs on past it, so that its end
/// meets no face of the stock.
pub const PAST: f64 = 1.0;

/// The ellipse CadQuery's `ellipse(rx, ry)` draws about `c`, OCCT's x on its major axis.
pub(crate) fn ellipse(c: V3, rx: f64, ry: f64) -> LoftSection {
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
pub fn lower_outer() -> Result<(Solid, Region)> {
    let mut sections: Vec<LoftSection> =
        LOWER_OUTER_SECTIONS.iter().map(|&[z, w, d, cy]| ellipse(v3(0.0, cy, z), w / 2.0, d / 2.0)).collect();
    let r = TUBE_SHELL_OUTER_R;
    let c = v3(0.0, SODA_FAUCET_TUBE_Y + TUBE_SHELL_CENTER_Y, LOWER_NECK_Z);
    sections.push(LoftSection::ellipse(c, v3(r, 0.0, 0.0), v3(0.0, r, 0.0)));
    let (body, _, ring) = loft(&sections)?;
    let land = Solid::extrude(&ring, V3::Z, v3(0.0, 0.0, ZONE5_Z_TOP + NECK_LAND_OVERRUN - LOWER_NECK_Z))?;
    Ok((body.union(&land)?, moved(&ring, v3(0.0, 0.0, ZONE5_Z_TOP - LOWER_NECK_Z))))
}

/// Four bearing pads under the display, their inner walls flush with the open channel.
pub fn feet_pads(neck: &Gooseneck) -> Result<Vec<Solid>> {
    let h = DISPLAY_FOOT_PAD_WIDTH / 2.0;
    let (feet, depth) = (DISPLAY_FEET_N, DISPLAY_FOOT_PAD_DEPTH);
    let mut pads = vec![];
    for [x, s] in display_foot_centers() {
        let (outer, inner) = (x.abs() + h, (x.abs() - h).min(DISPLAY_CHANNEL_HALF_WIDTH));
        let pad = neck.cradle_prism((outer - inner) / 2.0, (s - h, s + h), (feet - depth, feet), 0.0)?;
        pads.push(pad.translate(v3(((outer + inner) / 2.0).copysign(x), 0.0, 0.0)));
    }
    Ok(pads)
}

/// The Westbrass bore, a cylinder standing from `z0`.
fn bore(z0: f64, h: f64) -> Result<Solid> {
    Solid::cylinder(v3(WESTBRASS_BORE_X, WESTBRASS_BORE_Y, z0), V3::Z, WESTBRASS_BORE_DIAMETER / 2.0, h)
}

/// The flavor-tube pill, its -Y side filled out flat.
fn flavor_pill(z0: f64, h: f64) -> Result<Solid> {
    let [x, y] = FLAVOR_PILL_CENTER;
    let (l, w) = (PILL_LENGTH_X, PILL_WIDTH_Y);
    let fill = y - flavor_pill_y_minus_edge();
    let pill = level(z0).extrude(&Profile::new(Loop::slot(v2(x, y), l, w, 0.0)), h)?;
    pill.union(&level(z0).extrude(&Profile::rect(v2(x, y - fill / 2.0), l, fill), h)?)
}

/// The donor's lower bore and the flavor pill through zone 1.
pub fn zone1_inner() -> Result<Solid> {
    let z0 = ZONE1_Z_BOTTOM - PAST;
    let pill = flavor_pill(z0, ZONE1_HEIGHT + PAST)?;
    bore(z0, ZONE2_BORE_Z_BOTTOM - z0)?.union(&pill)
}

/// Three pedestal sockets, each with an insert pilot through its roof.
pub fn base_pod_holes() -> Result<Vec<Solid>> {
    let mut holes = vec![];
    for [x, y] in BASE_POD_CENTERS {
        let socket = Solid::cylinder(v3(x, y, BASE_POD_Z_BOTTOM - PAST), V3::Z, base_pod_hole_dia() / 2.0, BASE_POD_HOLE_DEPTH + PAST)?;
        let insert = Solid::cylinder(v3(x, y, BASE_INSERT_BOTTOM_Z), V3::Z, BASE_POD_INSERT_DIA / 2.0, BASE_POD_INSERT_DEPTH)?;
        holes.push(socket.union(&insert)?);
    }
    Ok(holes)
}

/// The donor's cross-section in zone 2: its rectangle with coved ±X faces, clipped to the bore,
/// and the flavor pill through.
pub fn zone2_inner() -> Result<Solid> {
    let (z0, z1) = (ZONE2_BORE_Z_BOTTOM, ZONE2_Z_TOP);
    let c = v2(WESTBRASS_BORE_X, WESTBRASS_BORE_Y);
    let (wx, wy) = (WESTBRASS_BORE_RECT_SHORT_X, WESTBRASS_BORE_RECT_LONG_Y);
    let cove = COVE_R;
    let reach = wy / 2.0 + BORE_OVERRUN;
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
    let column = column.intersect(&bore(z0, z1 - z0)?)?;
    column.union(&flavor_pill(ZONE2_Z_BOTTOM, ZONE2_HEIGHT)?)
}

/// The donor's arch clearance either side of the lever, joined behind it to the tube opening.
pub fn zone3_inner() -> Result<Solid> {
    let z0 = ZONE3_Z_BOTTOM;
    let (foot, peak) = (SHELL_ARCH_BORE_Z_FOOT_TOP, SHELL_ARCH_BORE_Z_PEAK);
    let (inner, outer) = (SHELL_ARCH_BORE_INNER_X, SHELL_ARCH_BORE_OUTER_X);
    let reach = WESTBRASS_BORE_DIAMETER / 2.0 + BORE_OVERRUN;
    let arch = |x0: f64, dx: f64| -> Result<Solid> {
        let outline = Pen::new(v2(reach, z0))
            .line_to(v2(-reach, z0))
            .line_to(v2(-reach, foot))
            .arc_through(v2(0.0, peak), v2(reach, foot))?
            .close()?;
        side(x0)?.extrude(&Profile::new(outline), dx)
    };
    let bores = arch(inner, outer - inner)?.union(&arch(-outer, outer - inner)?)?;
    let window = Solid::cuboid(v3(-inner, FILL_Y_MIN, z0), v3(inner, reach, peak));
    let bores = bores.union(&arch(-inner, 2.0 * inner)?.intersect(&window)?)?;
    bores.intersect(&bore(z0, peak - z0)?)
}

/// Open space beyond the square-cut drain mouth.
fn drain_relief_cut() -> Result<Solid> {
    let [o, x, t] = drain_relief().map(p3);
    let lead = DRAIN_RELIEF_LEAD;
    let r = DRAIN_TUBE_HOLE_DIA / 2.0;
    Plane::new(o - t * lead, x, t)?.extrude(&Profile::circle(v2(0.0, 0.0), r), paths::DRIP_END_CLEARANCE_MM + lead)
}

/// The round underside hole into the tube passage.
fn vent_outlet_cut() -> Result<Solid> {
    let (o, normal, offset) = vent_outlet();
    let (o, normal) = (p3(o), p3(normal));
    let plane = Plane::new(o + normal * offset, V3::X, normal)?;
    let depth = TUBE_SHELL_OUTER_R + WALL_THICKNESS_MIN;
    plane.extrude(&Profile::circle(v2(0.0, 0.0), paths::DRIP_HOLE_DIAMETER / 2.0), depth)
}

/// The decimal places the lever's outline is worked to: a ten-thousandth of a micron.
const OUTLINE_PRECISION: i32 = 8;

/// The lever's swing in its side view, (Y, Z): every pose of its profile from rest to full swing a
/// degree apart and each edge's sweep between neighbouring poses, with the corridor under the
/// paddle; grown by the lever's clearance with mitred corners, and with the plateau over the
/// donor's top. Each piece is a filled region, as GEOS's planar union fills it: wound
/// anticlockwise by its shoelace area, and a quad that crosses itself kept to the lobe that area
/// favours.
pub fn lever_outline() -> Vec<V2> {
    let [py, pz] = LEVER_PIVOT;
    let poses: Vec<Vec<[f64; 2]>> = (0..=LEVER_SWING_DEG)
        .map(|deg| {
            let a = deg as f64 * (std::f64::consts::PI / 180.0);
            let (c, s) = (a.cos(), a.sin());
            LEVER_PROFILE.iter().map(|[y, z]| [py + c * (y - py) - s * (z - pz), pz + s * (y - py) + c * (z - pz)]).collect()
        })
        .collect();
    let path = |pts: &[[f64; 2]]| -> PathD { pts.iter().map(|p| PointD::new(p[0], p[1])).collect() };
    // GEOS's rectangle: (a, b) to (c, e), from its corner at (c, b).
    let rect = |a: f64, b: f64, c: f64, e: f64| path(&[[c, b], [c, e], [a, e], [a, b]]);
    let mut regions: Vec<PathD> = poses.iter().map(|p| path(p)).collect();
    regions.push(rect(LEVER_INSERTION_FRONT_Y, ZONE2_Z_TOP + 1.0, LEVER_CORRIDOR_REAR_Y, LEVER_REST_TOP_Z));
    let n = LEVER_PROFILE.len();
    for w in poses.windows(2) {
        for i in 0..n {
            let j = (i + 1) % n;
            regions.push(path(&[w[0][i], w[0][j], w[1][j], w[1][i]]));
        }
    }
    let filled: PathsD = regions.iter().flat_map(filled_region).collect();
    let united = clipper2_rust::union_subjects_d(&filled, FillRule::NonZero, OUTLINE_PRECISION);
    let simplified = clipper2_rust::simplify_paths(&united, 0.001, true);
    let grown = clipper2_rust::inflate_paths_d(
        &simplified,
        LEVER_FIT_CLEARANCE + LEVER_SWEEP_ALLOWANCE,
        JoinType::Miter,
        EndType::Polygon,
        5.0,
        OUTLINE_PRECISION,
        0.0,
    );
    let plateau = rect(-WESTBRASS_BORE_RECT_LONG_Y / 2.0, LEVER_PLATEAU_Z, FILL_Y_MIN, LEVER_REST_TOP_Z);
    let outline = clipper2_rust::union_d(&grown, &vec![plateau], FillRule::NonZero, OUTLINE_PRECISION);
    outline[0].iter().map(|p| v2(p.x, p.y)).collect()
}

/// `piece` as a filled region: wound anticlockwise, and where it crosses itself, the lobes its
/// signed area favours. The area is the shoelace sum taken from the first corner, as GEOS takes a
/// ring's, so a self-crossing quad whose lobes all but balance keeps the lobe GEOS keeps.
fn filled_region(piece: &PathD) -> PathsD {
    let x0 = piece[0].x;
    let n = piece.len();
    let mut sum = 0.0;
    for i in 1..n {
        let prev = piece[i - 1];
        let next = piece[(i + 1) % n];
        sum += (piece[i].x - x0) * (prev.y - next.y);
    }
    let mut p = piece.clone();
    if sum / 2.0 > 0.0 {
        p.reverse();
    }
    clipper2_rust::union_subjects_d(&vec![p], FillRule::Positive, OUTLINE_PRECISION)
}

/// The lever's travel, the round relief over its resting top, and the straight front corridor
/// it goes in by.
pub fn lever_clearance() -> Result<Solid> {
    let xh = LEVER_CLEARANCE_X_HALF;
    let plane = side(-xh)?;
    let travel = plane.extrude(&Profile::polygon(&lever_outline()), 2.0 * xh)?;

    let (fill_y, top) = (FILL_Y_MIN, LEVER_REST_TOP_Z);
    let (r, cz) = (back_arch_r(), back_arch_center_z());
    let back = LEVER_CLEARANCE_Y_BACK;
    let front_y = fill_y - (r * r - (top - cz).powi(2)).sqrt();
    let rear_z = cz + (r * r - (back - fill_y).powi(2)).sqrt();
    let mid = 0.5 * ((top - cz).atan2(front_y - fill_y) + (rear_z - cz).atan2(back - fill_y));
    let relief = Pen::new(v2(front_y, top))
        .arc_through(v2(fill_y + r * mid.cos(), cz + r * mid.sin()), v2(back, rear_z))?
        .line_to(v2(back, top))
        .close()?;
    let overhead = plane.extrude(&Profile::new(relief), 2.0 * xh)?;

    let front_y = LEVER_INSERTION_FRONT_Y;
    let (seam, shoulder) = (ZONE5_Z_TOP, ZONE5_Z_BOTTOM);
    let shell_r = shell_outer_r();
    let opening = Solid::cuboid(v3(-xh, front_y, top), v3(xh, fill_y, seam));
    let cap = Solid::cylinder(v3(0.0, zone45_front_y() + shell_r, top), V3::Z, shell_r, seam - top)?;
    let entry = Solid::cuboid(v3(-xh, front_y, top), v3(xh, fill_y, shoulder));
    Solid::union_all(&[travel, overhead, opening.cut(&cap)?.union(&entry)?])
}

/// The display pocket over the feet, and the open channel under it.
fn display_cavity(neck: &Gooseneck, pads: &[Solid]) -> Result<Solid> {
    let s = (DISPENSE_FACE_THICKNESS, display_s_top());
    let half_x = DISPLAY_NECK_OUTER_R + WALL_THICKNESS_MIN;
    let device = neck.cradle_prism(half_x, s, (DISPLAY_SEAT_REFERENCE_N, DISPLAY_POCKET_TOP_N), 0.0)?.cut_all(pads)?;
    let channel = neck.cradle_prism(DISPLAY_CHANNEL_HALF_WIDTH, s, (0.0, DISPLAY_CHANNEL_TOP_N), 0.0)?;
    device.union(&channel)
}

/// The side grooves the display cover's lips snap into.
fn retention_grooves(neck: &Gooseneck) -> Result<Solid> {
    let slip = snap::END_SLIP;
    let band = neck.cradle_prism(
        DISPLAY_GROOVE_HALF_X,
        (display_clip_s_bottom() - slip, display_clip_s_top() + slip),
        (DISPLAY_CLIP_BOTTOM_N, DISPLAY_CLIP_TOP_N + snap::BEARING_SLIP),
        0.0,
    )?;
    let core = Profile::circle(v2(0.0, TUBE_SHELL_CENTER_Y), DISPLAY_GROOVE_CORE_R);
    band.cut(&neck.sweep(&core, 0.0, neck.length())?)
}

/// The flat rear cable lane and the opening that gathers the tubes and the cable from the
/// mounting channel into the neck: a smooth loft through the hulls round their clearances,
/// with straight lands below and above it.
pub fn lower_bundle_opening() -> Result<Solid> {
    let (z0, z1) = (SIGNAL_LANE_BOTTOM_Z, SIGNAL_LANE_TOP_Z);
    let [x, y] = SIGNAL_LOWER_EXIT;
    let lane_slot = Loop::slot(v2(x, y), SIGNAL_LANE_WIDTH, SIGNAL_LANE_DEPTH, SIGNAL_LOWER_EXIT_ANGLE);
    let lane = level(z0).extrude(&Profile::new(lane_slot), z1 - z0)?;
    let rows = lower_opening_sections();
    let sections = rows.iter().map(|(z, circles)| hull_section(&wrapped(circles), &level(*z))).collect::<Result<Vec<_>>>()?;
    let (transition, first, last) = loft(&sections)?;
    let (bottom, first_z) = (BUNDLE_LAND_BOTTOM_Z, rows[0].0);
    let lower = Solid::extrude(&moved(&first, v3(0.0, 0.0, bottom - first_z)), V3::Z, v3(0.0, 0.0, first_z - bottom))?;
    let upper = Solid::extrude(&last, V3::Z, v3(0.0, 0.0, BUNDLE_LAND_ABOVE))?;
    Solid::union_all(&[lane, lower, transition, upper])
}

/// Where station `s` of the tube centrelines (along the bend from the split joint) falls on the
/// gooseneck.
fn station(neck: &Gooseneck, s: f64) -> f64 {
    neck.at_angle(paths::JOINT_ANGLE + s / paths::water_radius())
}

/// The shared smooth passage up the neck: the tube and cable hull swept up to where the tubes
/// converge, lofted through their convergence, and swept on to where the cable leaves for the
/// display.
fn upstream_passage(neck: &Gooseneck) -> Result<Solid> {
    let mut sections = vec![];
    for row in passage_sections() {
        let plane = Plane::new(p3(row.origin), p3(row.xdir), p3(row.normal))?;
        sections.push(hull_section(&wrapped(&row.circles), &plane)?);
    }
    let (converge, first, last) = loft(&sections)?;
    let s0 = paths::converge_start_s();
    let s1 = s0 + paths::CONVERGE_LENGTH;
    let lower = Solid::sweep(&first, &neck.path(station(neck, s0), 0.0)?)?;
    let outlet = Solid::sweep(&last, &neck.path(station(neck, s1), station(neck, ribbon_end_s()))?)?;
    Solid::union_all(&[lower, converge, outlet])
}

/// The soda opening and the flavor capsule beyond where the cable leaves, out to the tip.
fn beverage_outlets(neck: &Gooseneck) -> Result<Solid> {
    let start = station(neck, ribbon_end_s() - BEVERAGE_LEAD);
    neck.sweep(&hull(&wrapped(&beverage_circles()))?, start, neck.length() + PAST)
}

/// The whole shell, before it is split into its two prints.
pub fn shell(neck: &Gooseneck) -> Result<Solid> {
    let (lower, seam) = lower_outer()?;
    shell_from(neck, lower, &seam, &[])
}

/// A shell whose stock below the zone-5 seam is `lower`, with `seam` the ring the gooseneck is
/// swept from, cut by the shell's cutters and `extra`, the variant's own.
pub fn shell_from(neck: &Gooseneck, lower: Solid, seam: &Region, extra: &[Solid]) -> Result<Solid> {
    let gooseneck = Solid::sweep(seam, &neck.path(0.0, neck.length())?)?;
    let pads = feet_pads(neck)?;
    let mut stock = vec![lower, gooseneck];
    stock.extend(pads.iter().cloned());
    let outer = Solid::union_all(&stock)?;
    let mut cutters = vec![zone1_inner()?];
    cutters.extend(base_pod_holes()?);
    cutters.push(zone2_inner()?);
    cutters.push(zone3_inner()?);
    cutters.push(drain_relief_cut()?);
    cutters.push(vent_outlet_cut()?);
    cutters.push(lever_clearance()?);
    cutters.push(display_cavity(neck, &pads)?);
    cutters.push(retention_grooves(neck)?);
    cutters.push(lower_bundle_opening()?);
    cutters.push(upstream_passage(neck)?);
    cutters.push(beverage_outlets(neck)?);
    cutters.extend(extra.iter().cloned());
    outer.cut_all(&cutters)
}

/// The base and the tip: split square to the bend at the junction, the base's socket opened
/// below it and the tip's plug carried down into it.
pub fn pieces(neck: &Gooseneck, full: &Solid) -> Result<(Solid, Solid)> {
    let junction = neck.at_angle(SPLIT_JUNCTION_ROT);
    // Each overlap runs on past the junction, so its end meets no face of the split.
    let past = junction + PAST;
    let (r, cy) = (TUBE_SHELL_OUTER_R, TUBE_SHELL_CENTER_Y);
    let socket = Profile::circle(v2(0.0, cy), r - SPLIT_SOCKET_SHRINK);
    let socket = neck.sweep(&socket, neck.at_angle(path_socket_start_rot()), past)?;
    let plug = Profile::circle(v2(0.0, cy), r - split_plug_shrink());
    let plug = neck.sweep(&plug, neck.at_angle(path_plug_start_rot()), past)?;
    let (p, t, _) = neck.frame(junction);
    let base = full.cut(&socket)?.trim(&Plane::new(p, V3::X, -t)?)?;
    let reach = 2.0 * full.bounds().diagonal();
    let above = Plane::new(p, V3::X, t)?.extrude(&Profile::rect(v2(0.0, 0.0), reach, reach), reach)?;
    let tip = full.intersect(&above.union(&plug)?)?;
    ensure!(base.components().len() == 1 && tip.components().len() == 1, "a shell piece is not one solid");
    Ok((base, tip))
}
