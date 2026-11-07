//! The foam shell's files: the PET-GF casing the cold core is potted in, with the reservoirs'
//! pockets, the carbonator's support ring, the reed channels, the clamp screws' hosts and bores,
//! and the passages lines leave it by. It writes the STEP, the model and the STL that prints, the
//! payload the page draws, cut from that STL, and the copper feed-throughs the whole-machine
//! program places the evaporator's tails at.
//!
//!     foam-shell [<output directory>]
use anyhow::{Context, Result, anyhow, bail, ensure};
use hsm_cold_core_catalog as catalog;
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::{b_fill, cap, routes};
use hsm_foam_shell_numbers as numbers;
use hsm_kernel::math::{TAU, acos, cos, sin, tan};
use hsm_kernel::part::write_printed;
use hsm_kernel::*;
use hsm_print_payload as presentation;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::PathBuf;

const NAME: &str = "foam-shell";
const OUTPUT: &str = "hardware/printed-parts/cold-core/foam-shell";

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: foam-shell [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let shell = build()?;
    let colour = numbers::colour().linear;
    let mut written = write_printed(&out, NAME, &[Body { name: NAME, color: Some(colour), solid: &shell }])?;
    // The payload is cut from the print this run has just written, and names the STEP beside it.
    let own = |file: &str| std::fs::read(out.join(file)).with_context(|| format!("reading back {file}"));
    let payload = payload(&own(&format!("{NAME}.step"))?, &own(&format!("{NAME}.stl"))?, colour)?;
    let files = [(format!("{NAME}.step.mesh"), payload), (format!("{NAME}.numbers.json"), copper_feed_throughs())];
    for (file, bytes) in &files {
        keep(&out.join(file), bytes)?;
        written["files"].as_array_mut().context("the files written")?.push(Value::from(file.as_str()));
    }
    println!("{written}");
    Ok(())
}

/// The payload the page draws: the print's triangles reduced to the viewer's tolerance and creased
/// at its angle, named and coloured as the shell and bound to the STEP whose bytes are `step`.
fn payload(step: &[u8], stl: &[u8], colour: [f64; 3]) -> Result<Vec<u8>> {
    let src = format!("{:x}", Sha256::digest(step));
    let (mesh, _) = presentation::weld(stl)?;
    let cut = presentation::cut(
        &mesh,
        None,
        presentation::Request {
            name: json!(NAME),
            color: json!(colour),
            src: &src,
            crease_deg: presentation::CREASE_DEG,
            deflection_ratio: presentation::LINEAR_DEFLECTION_RATIO,
            preserve: false,
            unknown: false,
            check: false,
        },
    )?;
    Ok(cut.payload)
}

/// The copper feed-throughs by name and axis point, as the whole-machine program reads them.
fn copper_feed_throughs() -> Vec<u8> {
    let stations = numbers::copper_stations();
    let names: Vec<&str> = stations.iter().map(|s| s.name).collect();
    let origins: Vec<[f64; 3]> = stations.iter().map(|s| s.origin).collect();
    let file = json!({"copper_names": names, "copper_origins": origins});
    format!("{file:#}\n").into_bytes()
}

/// `bytes` at `path`, unless the file holds them already; any other lands whole, by a rename.
fn keep(path: &std::path::Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path.file_name().and_then(|f| f.to_str()).ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}

fn box3(x: (f64, f64), y: (f64, f64), z: (f64, f64)) -> Solid {
    Solid::cuboid(
        v3(x.0.min(x.1), y.0.min(y.1), z.0.min(z.1)),
        v3(x.0.max(x.1), y.0.max(y.1), z.0.max(z.1)),
    )
}

fn span(range: [f64; 2]) -> (f64, f64) {
    (range[0], range[1])
}

/// The +X pocket's cavity outline: its far wall's rounded corners, its ±Y walls, and its
/// centreward wall, the middle arc round the carbonator and coil between two transition arcs.
fn pocket_loop(corner: f64) -> Result<Loop> {
    let (x, y, far, r) = (numbers::middle_cavity_x(), core::BAG_POCKET_Y_INNER_MAX, core::BAG_POCKET_FAR_INNER_X, corner);
    let (tx, ty, turn) =
        (numbers::transition_apex_x(), numbers::TRANSITION_CENTER_Y, numbers::POCKET_CENTERWARD_ARC_TRANSITION_Y);
    Pen::new(v2(x, y))
        .line_to(v2(far - r, y))
        .radius_arc(v2(far, y - r), r)?
        .line_to(v2(far, -y + r))
        .radius_arc(v2(far - r, -y), r)?
        .line_to(v2(x, -y))
        .arc_through(v2(tx, -ty), v2(x, -turn))?
        .arc_through(v2(numbers::ARC_CAVITY_RADIUS, 0.0), v2(x, turn))?
        .arc_through(v2(tx, ty), v2(x, y))?
        .close()
}

/// The ring the carbonator stands on, with its pour slots cut through it; each slot's sides lie on
/// the ring's own radii.
fn support_ring() -> Result<Solid> {
    let (inner, outer) = (numbers::SUPPORT_RING_INNER_RADIUS, numbers::SUPPORT_RING_OUTER_RADIUS);
    let (z0, z1) = (numbers::SUPPORT_RING_BOTTOM_Z, numbers::SUPPORT_RING_TOP_Z);
    let section = |a, b| Profile::polygon(&[v2(a, z0), v2(b, z0), v2(b, z1), v2(a, z1)]);
    let mut ring = Plane::XZ.revolve(&section(inner, outer), 360.0, v2(0.0, 0.0), v2(0.0, 1.0))?;
    let margin = numbers::SLOT_RADIAL_MARGIN;
    let slot = Plane::XZ.revolve(
        &section(inner - margin, outer + margin),
        numbers::SLOT_ANGULAR_WIDTH,
        v2(0.0, 0.0),
        v2(0.0, 1.0),
    )?;
    for [start, _] in numbers::slot_spans() {
        ring = ring.cut(&slot.rotate(V3::ZERO, v3(0.0, 0.0, 1.0), start))?;
    }
    Ok(ring)
}

/// A route's corners joined by straight legs and arcs of radius `bend` at each corner, each arc
/// shrunk where two corners' arcs would overlap on the leg between them.
fn rounded_path(points: &[V3], bend: f64) -> Result<Path> {
    ensure!(points.len() >= 2, "a route has at least two points");
    let mut v = vec![points[0]];
    for &p in &points[1..] {
        if (p - v[v.len() - 1]).norm() < 1e-9 {
            continue;
        }
        if v.len() >= 2 {
            let (a, b) = (v[v.len() - 2], v[v.len() - 1]);
            if (b - a).unit().cross((p - b).unit()).norm() < 1e-9 {
                *v.last_mut().unwrap() = p;
                continue;
            }
        }
        v.push(p);
    }
    let count = v.len();
    let mut half = vec![0.0; count];
    let mut radii = vec![0.0; count];
    for i in 1..count - 1 {
        half[i] = acos((v[i - 1] - v[i]).unit().dot((v[i + 1] - v[i]).unit()).clamp(-1.0, 1.0)) / 2.0;
        radii[i] = bend;
    }
    for _ in 0..64 {
        let setback: Vec<f64> =
            (0..count).map(|i| if half[i] > 1e-9 { radii[i] / tan(half[i]) } else { 0.0 }).collect();
        let mut worst: f64 = 1.0;
        for i in 0..count - 1 {
            let (leg, want) = ((v[i + 1] - v[i]).norm(), setback[i] + setback[i + 1]);
            if want > leg {
                worst = worst.min(leg / want);
            }
        }
        if worst >= 1.0 - 1e-12 {
            break;
        }
        for r in &mut radii[1..count - 1] {
            *r *= worst * 0.999;
        }
    }
    let mut path = Path::new(v[0]);
    let mut tail = v[0];
    for i in 1..count - 1 {
        let (u, w) = ((v[i - 1] - v[i]).unit(), (v[i + 1] - v[i]).unit());
        let setback = radii[i] / tan(half[i]);
        let (enter, leave) = (v[i] + u * setback, v[i] + w * setback);
        let centre = v[i] + (u + w).unit() * (radii[i] / sin(half[i]));
        let mid = centre + (v[i] - centre).unit() * radii[i];
        if (enter - tail).norm() > 1e-7 {
            path = path.line_to(enter);
        }
        path = path.arc_through(mid, leave)?;
        tail = leave;
    }
    if (v[count - 1] - tail).norm() > 1e-7 {
        path = path.line_to(v[count - 1]);
    }
    Ok(path)
}

/// The PRV vent's corridor: the line's clearance bore swept along its route, out of the shroud,
/// down the west lane and out through the +Y flank.
fn vent() -> Result<Solid> {
    let points: Vec<V3> = routes::prv_vent().into_iter().map(V3::from).collect();
    let path = rounded_path(&points, routes::bend_radius())?;
    let radius = core::PORT_HOLE_RADIUS;
    // The swept bend combines the path's and section's chord errors. Bisect each path
    // interval on the same circular arc so their combined error stays within LINEAR.
    let mut fine = Path::new(points[0]);
    for leg in &path.legs {
        match *leg {
            Leg::Line { b, .. } => fine = fine.line_to(b),
            Leg::Arc { a, b, c, d, turn } => {
                let count = 2
                    * ((hsm_kernel::rule::ring_count((a - c).norm() + radius) as f64 * turn / TAU - 1e-9).ceil()
                        as usize)
                        .max(1);
                let v = a - c;
                for i in 1..=count {
                    let angle = turn * i as f64 / count as f64;
                    let end = if i == count {
                        b
                    } else {
                        c + v * cos(angle) + d.cross(v) * sin(angle) + d * (d.dot(v) * (1.0 - cos(angle)))
                    };
                    fine = fine.arc_center(c, end, d)?;
                }
            }
            Leg::Curve { .. } => bail!("the vent's route runs in straight and circular legs"),
        }
    }
    let normal = match path.legs.first().context("the vent's route has a leg")? {
        Leg::Line { a, b } => (*b - *a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(*a - *c).unit(),
        Leg::Curve { .. } => bail!("the vent's route runs in straight and circular legs"),
    };
    let (_, x, _) = hsm_kernel::rule::plane_frame(normal);
    Plane::new(points[0], x, normal)?.sweep(&Profile::circle(v2(0.0, 0.0), radius), &fine)
}

/// The enclosure's frame carried into the shell's, from the cap lid's pose.
fn world_to_shell() -> Affine {
    let origin = cap::world_to_shell([0.; 3]);
    let axis = |a: [f64; 3]| {
        let p = cap::world_to_shell(a);
        v3(p[0] - origin[0], p[1] - origin[1], p[2] - origin[2])
    };
    Affine::from_columns(axis([1., 0., 0.]), axis([0., 1., 0.]), axis([0., 0., 1.]), V3::from(origin))
}

/// Reservoir B's fill tube's channel air where the top cap's cup meets the shell: the cap's
/// channel, run in level from the cap's front face and turned down on its bend, with the lead-in
/// at each mouth and its roof's print allowance, carried into the shell's frame.
fn b_fill_air() -> Result<Solid> {
    let passage = b_fill::passage();
    let (bend, centre, radius) = (b_fill::BEND_RADIUS, b_fill::CHANNEL_CENTRE, b_fill::CHANNEL_RADIUS);
    let inlet = passage.inlet_leg();
    let section = Profile::circle(v2(bend, centre), radius);
    let turn = Plane::XZ.revolve(&section, 90.0, v2(0.0, 0.0), v2(0.0, 1.0))?;
    let mut channel = turn.union(&Plane::XZ.extrude(&section, inlet)?)?;
    let (start_y, end_y) = (-b_fill::MOUTH_OVERRUN, b_fill::MOUTH + b_fill::MOUTH_MERGE);
    let mouth = Solid::cone(
        v3(bend, start_y, centre),
        V3::Y,
        radius + b_fill::MOUTH + b_fill::MOUTH_OVERRUN,
        radius - b_fill::MOUTH_MERGE,
        end_y - start_y,
    )?;
    channel = channel.union(&mouth.translate(v3(0.0, -inlet, 0.0)))?.union(&mouth.mirror(V3::ZERO, v3(1.0, -1.0, 0.0)))?;
    let end = passage.bend_end;
    channel = channel.rotate(V3::ZERO, V3::Y, -90.0).translate(v3(end[0] + centre, end[1] - bend, end[2]));
    channel = channel.union(&channel.translate(v3(0.0, 0.0, passage.roof_allowance)))?;
    Ok(channel.transformed(&world_to_shell()))
}

/// The clamp screws' hosts: a column round each station, webbed to the outer wall it stands on,
/// trimmed to the casing's footprint.
fn attachment_hosts(height: f64, radius: f64) -> Result<Solid> {
    let (width, depth) = (core::OUTER_SHELL_X_LENGTH, core::OUTER_SHELL_Y_LENGTH);
    let footprint = Plane::XY.extrude(
        &Profile::new(Loop::rounded_rect(v2(0.0, 0.0), width, depth, core::CORNER_ROUND_RADIUS)?),
        height,
    )?;
    let stations = core::attachment_stations();
    let mut hosts = vec![];
    for ([x, y], _) in &stations {
        hosts.push(Plane::XY.at(v3(*x, *y, 0.0)).cylinder(radius, height)?);
    }
    for &([x, y], wall) in &stations {
        hosts.push(match wall {
            "y" => box3((x - radius, x + radius), (y, y.signum() * depth / 2.0), (0.0, height)),
            "x" => box3((x, x.signum() * width / 2.0), (y - radius, y + radius), (0.0, height)),
            other => bail!("a clamp station stands on the x or the y wall, not {other:?}"),
        });
    }
    Solid::union_all(&hosts)?.intersect(&footprint)
}

/// A cutter at every clamp station, made by `cutter` at the station's plan point.
fn at_stations(cutter: impl Fn(f64, f64) -> Result<Solid>) -> Result<Vec<Solid>> {
    core::attachment_stations().iter().map(|([x, y], _)| cutter(*x, *y)).collect()
}

fn build() -> Result<Solid> {
    let fits = catalog::fits();
    let height = core::foam_shell_rim_z(&fits);
    let pocket_height = core::FOAM_SHELL_OUTER_HEIGHT;
    let floor = core::WALL_AND_FLOOR_THICKNESS;
    let (wall, outer_wall) = (core::WALL_THICKNESS, core::OUTER_SHELL_WALL);
    let (width, depth, corner) = (core::OUTER_SHELL_X_LENGTH, core::OUTER_SHELL_Y_LENGTH, core::CORNER_ROUND_RADIUS);
    let supported = fits.supported_surface;

    // The outer shell: a rounded box open at the top on its floor, with the clamp hosts.
    let footprint = Loop::rounded_rect(v2(0.0, 0.0), width, depth, corner)?;
    let outside = Plane::XY.extrude(&Profile::new(footprint), height)?;
    let inside = Plane::XY.at(v3(0.0, 0.0, floor)).extrude(
        &Profile::new(Loop::rounded_rect(
            v2(0.0, 0.0),
            width - 2.0 * outer_wall,
            depth - 2.0 * outer_wall,
            corner - outer_wall,
        )?),
        height - floor,
    )?;
    let hosts = attachment_hosts(height, core::SCREW_GUARD_DIAMETER / 2.0)?;
    let mut outer = outside.cut(&inside)?.union(&hosts)?;
    // The seam channel down the +Y face, with the wall folded in behind it.
    let (face, seam_floor, half) =
        (depth / 2.0, depth / 2.0 - core::SEAM_CHANNEL_DEPTH, core::SEAM_CHANNEL_WIDTH / 2.0);
    outer = outer
        .union(&box3((-half - outer_wall, half + outer_wall), (seam_floor - outer_wall, seam_floor), (0.0, height)))?
        .cut(&box3((-half, half), (seam_floor, face + 1.0), (-1.0, height + 1.0)))?;

    // The reservoirs' pockets: each cavity's outline offset into the foam by the wall's stock,
    // the −X pocket the +X one's mirror.
    let pocket = pocket_loop(core::bag_pocket_corner_inner_radius(&fits))?.ccw();
    let cavity = Plane::XY.extrude(&Profile::new(pocket.clone()), pocket_height)?;
    let grown = Plane::XY.extrude(&Profile::new(pocket.offset(wall, true)?), pocket_height)?;
    let pocket = grown.cut(&cavity)?;
    let mut shell = pocket
        .union(&pocket.mirror(V3::ZERO, v3(1.0, 0.0, 0.0)))?
        .union(&support_ring()?)?
        .union(&outer)?;

    // The reed channels on each pocket's far wall: the cavity's envelope, open at the top, and the
    // backing that stands over the pocket's wall to the rim.
    let sides = [1.0, -1.0];
    for side in sides {
        let x = side * core::REED_CHANNEL_INNER_X;
        let envelope = box3(
            (x, x + side * (core::REED_X_DEPTH + core::WALL_THICKNESS)),
            span(core::REED_ENVELOPE_Y_RANGE),
            span(core::reed_envelope_z_range(&fits)),
        );
        let reeds = box3(
            (x, x + side * core::REED_X_DEPTH),
            span(core::REED_CAVITY_Y_RANGE),
            span(core::reed_cavity_z_range(&fits)),
        );
        let back = box3(
            (side * core::BAG_POCKET_FAR_INNER_X, x),
            span(core::REED_ENVELOPE_Y_RANGE),
            (core::FOAM_SHELL_OUTER_HEIGHT, height),
        );
        shell = shell.union(&envelope.cut(&reeds)?.union(&back)?)?;
    }

    // The clamp stack's bores: the heat-set inserts' pockets, the bottom one deeper by the
    // allowance of the face it prints over; the bottom bores' blind ends, which narrow as fast as
    // they rise to print without support; and the screws' passages beyond the inserts.
    let (insert_radius, insert_depth) = (core::INSERT_POCKET_RADIUS, core::INSERT_POCKET_DEPTH);
    let tail_radius = core::screw_clearance_radius(&fits);
    let (bottom_tail, top_tail) = (core::bottom_screw_bore_depth(&fits), core::top_screw_bore_depth(&fits));
    for (bottom, length) in [(0.0, insert_depth + supported), (height - insert_depth, insert_depth)] {
        shell = shell.cut_all(&at_stations(|x, y| Plane::XY.at(v3(x, y, bottom)).cylinder(insert_radius, length))?)?;
    }
    for (bottom, lower, upper) in
        [(insert_depth + supported, insert_radius, tail_radius), (bottom_tail + supported, tail_radius, 0.0)]
    {
        shell = shell.cut_all(&at_stations(|x, y| Solid::cone(v3(x, y, bottom), V3::Z, lower, upper, 2.0 * (lower - upper)))?)?;
    }
    for (bottom, length) in [(0.0, bottom_tail + supported), (height - top_tail, top_tail)] {
        shell = shell.cut_all(&at_stations(|x, y| Plane::XY.at(v3(x, y, bottom)).cylinder(tail_radius, length))?)?;
    }

    // The PRV vent's corridor, its roof raised by the supported-surface allowance.
    let corridor = vent()?;
    shell = shell.cut(&corridor)?.cut(&corridor.translate(v3(0.0, 0.0, supported)))?;

    // The copper feed-throughs, through the front wall and past both its faces.
    for station in numbers::copper_stations() {
        let p = V3::from(station.origin);
        shell = shell.cut(&Solid::cylinder(
            p - v3(2.0, 0.0, 0.0),
            v3(1.0, 0.0, 0.0),
            numbers::COPPER_HOLE_RADIUS,
            outer_wall + 4.0,
        )?)?;
    }

    // Each reed channel's sensing window through its pocket's far wall, up to the pockets' top,
    // and the window's roof, which peaks across its width so it prints without support.
    let windows: Vec<(f64, f64)> = sides
        .iter()
        .map(|side| {
            let (a, b) = (side * core::BAG_POCKET_FAR_INNER_X, side * core::BAG_POCKET_OUTERMOST_X);
            (a.min(b), a.max(b))
        })
        .collect();
    for &(x0, x1) in &windows {
        shell = shell.cut(&box3((x0, x1), span(core::REED_CAVITY_Y_RANGE), (floor, core::FOAM_SHELL_OUTER_HEIGHT)))?;
    }
    for &(x0, x1) in &windows {
        let [y0, y1] = core::REED_CAVITY_Y_RANGE;
        let z = core::FOAM_SHELL_OUTER_HEIGHT;
        let roof = [v2(y0, z), v2(y1, z), v2(core::REED_Y_CENTER, z + 2.0 * core::REED_Y_HALF_W)];
        shell = shell.cut(&Plane::new(v3(x0, 0.0, 0.0), V3::Y, V3::X)?.extrude(&Profile::polygon(&roof), x1 - x0)?)?;
    }

    shell = shell.cut(&b_fill_air()?)?;

    // Reservoir B's reed cable outlet through the front face.
    let (lo, hi) = (numbers::REED_B_OUTLET_MIN, numbers::REED_B_OUTLET_MAX);
    let shoulder = numbers::REED_B_OUTLET_SHOULDER_Z;
    let window = [
        v2(lo[1], lo[2]),
        v2(hi[1], lo[2]),
        v2(hi[1], shoulder),
        v2(numbers::REED_B_OUTLET_AXIS[1], numbers::REED_B_OUTLET_PEAK_Z),
        v2(lo[1], shoulder),
    ];
    let notch = Plane::new(v3(lo[0], 0.0, 0.0), V3::Y, V3::X)?.extrude(&Profile::polygon(&window), hi[0] - lo[0])?;
    shell.cut(&notch)
}
