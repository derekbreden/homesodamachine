//! The foam cap's files: the equipment lid on the cold core's crown with the mounts it carries for
//! the parts above the core, the open-topped closure under the core, the R14 holder reservoir B's
//! fill tube turns in, and the pump's snap cap. Each prints: its STEP, its fine model, the STL the
//! slicer reads and the payload the page draws, cut from that STL. Beside them, the numbers the
//! machine places the pump's cap, the wiring's wells, the union support and the cable conduits
//! from.
//!
//!     foam-cap [<output directory>]
use anyhow::{Context, Result, bail};
use hsm_cold_core_interface as core;
use hsm_cold_core_layout::b_fill as tube;
use hsm_cold_core_layout::cap::cap_face_z;
use hsm_foam_cap_numbers as cap;
use hsm_foam_cap_numbers::pump::{self, Cradle};
use hsm_foam_cap_numbers::reservoir_a::{self, Run};
use hsm_kernel::math::{PI, TAU, cos, sin};
use hsm_kernel::part::write_printed;
use hsm_kernel::*;
use hsm_print_payload as presentation;
use serde::Serialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::PathBuf;

const OUTPUT: &str = "hardware/printed-parts/cold-core/foam-cap";
/// How far a cutter runs past the face it opens, and a stock block into the face it joins.
const OVERCUT: f64 = 0.1;

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: foam-cap [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let colour = cap::colour().linear;
    let pieces = [
        ("foam-cap-lid-top", top_lid()?),
        ("foam-cap-bottom", bottom_cap()?),
        ("reservoir-b-fill-guide", b_holder()?),
        ("pump-snap-cap", pump_snap()?),
    ];
    for (name, solid) in &pieces {
        let mut said = write_printed(&out, name, &[Body { name, color: Some(colour), solid }])?;
        // The pump's cap keeps every printed triangle; the others are drawn at the viewer's
        // tolerance.
        payload(&out, name, colour, *name == "pump-snap-cap")?;
        said["files"].as_array_mut().context("the files written")?.push(json!(format!("{name}.step.mesh")));
        println!("{said}");
    }
    machine_numbers(&out)
}

/// The payload of `name`'s printed triangles, bound to its STEP.
fn payload(dir: &std::path::Path, name: &str, colour: [f64; 3], preserve: bool) -> Result<()> {
    let read = |file: String| std::fs::read(dir.join(&file)).with_context(|| format!("reading {file}"));
    let step = read(format!("{name}.step"))?;
    let stl = read(format!("{name}.stl"))?;
    let src: String = Sha256::digest(&step).iter().map(|b| format!("{b:02x}")).collect();
    let (mesh, _) = presentation::weld(&stl)?;
    let cut = presentation::cut(
        &mesh,
        None,
        presentation::Request {
            name: json!(name),
            color: json!(colour),
            src: &src,
            crease_deg: presentation::CREASE_DEG,
            deflection_ratio: presentation::LINEAR_DEFLECTION_RATIO,
            preserve,
            unknown: false,
            check: false,
        },
    )?;
    presentation::printed::keep(&dir.join(format!("{name}.step.mesh")), &cut.payload)
}

// --- Frames and shapes ---------------------------------------------------------------------------

fn p3(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

fn box3(x0: f64, x1: f64, y0: f64, y1: f64, z0: f64, z1: f64) -> Solid {
    Solid::cuboid(v3(x0.min(x1), y0.min(y1), z0.min(z1)), v3(x0.max(x1), y0.max(y1), z0.max(z1)))
}

fn cuboid(b: [[f64; 3]; 2]) -> Solid {
    Solid::cuboid(p3(b[0]), p3(b[1]))
}

/// A placement from a pose's rotation rows and translation.
fn placement(rotation: [[f64; 3]; 3], translation: [f64; 3]) -> Affine {
    let column = |i: usize| v3(rotation[0][i], rotation[1][i], rotation[2][i]);
    Affine::from_columns(column(0), column(1), column(2), p3(translation))
}

/// The enclosure carried into the cap's own frame.
fn world_to_cap() -> Affine {
    let (origin, axes) = cap::world_to_cap();
    Affine::from_columns(p3(axes[0]), p3(axes[1]), p3(axes[2]), p3(origin))
}

/// The casing's rounded outline, inset by `inset`, from `z0` to `z1`.
fn outline(z0: f64, z1: f64, inset: f64) -> Result<Solid> {
    Plane::XY.offset(z0).extrude(
        &Profile::new(Loop::rounded_rect(
            v2(0., 0.),
            core::OUTER_SHELL_X_LENGTH - 2. * inset,
            core::OUTER_SHELL_Y_LENGTH - 2. * inset,
            core::CORNER_ROUND_RADIUS - inset,
        )?),
        z1 - z0,
    )
}

fn cylinder(xy: V2, z0: f64, z1: f64, radius: f64) -> Result<Solid> {
    Solid::cylinder(v3(xy.x, xy.y, z0), V3::Z, radius, z1 - z0)
}

fn xy(p: [f64; 2]) -> V2 {
    v2(p[0], p[1])
}

// --- The clamp stack -----------------------------------------------------------------------------

/// How far a head pocket's outward slot runs past the casing's outside.
const SLOT_OVERRUN: f64 = 1.;

/// The clamp screws' head pockets, open to the outside so no thin counterbore rim is left at the
/// casing's edge; a corner's slot meets the round normally.
fn head_pockets(top: bool, z: f64, depth: f64) -> Result<Solid> {
    let r = core::HEAD_CBORE_RADIUS;
    let (width, depth_y, corner) = (core::OUTER_SHELL_X_LENGTH, core::OUTER_SHELL_Y_LENGTH, core::CORNER_ROUND_RADIUS);
    let stations = if top { core::lid_attachment_stations() } else { core::attachment_stations() };
    let mut cuts = vec![];
    for (station, wall) in stations {
        let p = xy(station);
        cuts.push(cylinder(p, z, z + depth, r)?);
        match wall {
            "corner" => {
                let ox = p.x - p.x.signum() * (width / 2. - corner);
                let oy = p.y - p.y.signum() * (depth_y / 2. - corner);
                let angle = hsm_kernel::math::atan2(oy, ox) * 180. / PI - 90.;
                cuts.push(
                    box3(-r, r, 0., 2. * corner + 2. * SLOT_OVERRUN, 0., depth)
                        .rotate(V3::ZERO, V3::Z, angle)
                        .translate(v3(p.x, p.y, z)),
                );
            }
            "x" => cuts.push(box3(p.x, p.x.signum() * (width / 2. + SLOT_OVERRUN), p.y - r, p.y + r, z, z + depth)),
            _ => cuts.push(box3(p.x - r, p.x + r, p.y, p.y.signum() * (depth_y / 2. + SLOT_OVERRUN), z, z + depth)),
        }
    }
    Solid::union_all(&cuts)
}

/// The clamp bosses on the casing's walls, `height` tall and `r` round.
fn bosses(height: f64, r: f64) -> Result<Solid> {
    let mut stock = vec![];
    for (station, wall) in core::attachment_stations() {
        let p = xy(station);
        stock.push(cylinder(p, 0., height, r)?);
        if matches!(wall, "corner" | "y") {
            stock.push(box3(p.x - r, p.x + r, p.y, p.y.signum() * core::OUTER_SHELL_Y_LENGTH / 2., 0., height));
        }
        if matches!(wall, "corner" | "x") {
            stock.push(box3(p.x, p.x.signum() * core::OUTER_SHELL_X_LENGTH / 2., p.y - r, p.y + r, 0., height));
        }
    }
    Solid::union_all(&stock)?.intersect(&outline(0., height, 0.)?)
}

/// The bottom closure: one open-topped cup on its outside floor, its clamp bosses and their head
/// pads inside, its pour holes and vents.
fn bottom_cap() -> Result<Solid> {
    let fits = cap::fits();
    let h = core::bottom_cap_height(&fits);
    let boss = core::SCREW_BOSS_SIZE / 2.;
    let body = outline(0., h, 0.)?
        .cut(&outline(core::WALL_AND_FLOOR_THICKNESS, h, core::OUTER_SHELL_WALL)?)?
        .union(&bosses(h, boss)?)?
        .union(&bosses(core::foam_cap_lid_height(&fits), boss + cap::head_pad_growth())?)?
        .cut(&head_pockets(false, 0., core::head_cbore_depth(&fits) + fits.supported_surface)?)?;
    let mut cuts = vec![];
    for (station, _) in core::attachment_stations() {
        cuts.push(cylinder(xy(station), 0., h + OVERCUT, core::screw_clearance_radius(&fits))?);
    }
    for hole in cap::bottom_holes() {
        cuts.push(cylinder(xy(hole.xy), -OVERCUT, h + OVERCUT, hole.radius)?);
    }
    body.cut(&Solid::union_all(&cuts)?)
}

// --- Reservoir B's fill tube -----------------------------------------------------------------------

/// The channel's round section with a pointed roof, so it prints without support.
fn teardrop(radius: f64) -> Result<Profile> {
    let (x, z) = (tube::BEND_RADIUS, tube::CHANNEL_CENTRE);
    let k = radius / 2_f64.sqrt();
    Ok(Profile::new(
        Pen::new(v2(x + k, z + k))
            .line_to(v2(x, z + 2_f64.sqrt() * radius))
            .line_to(v2(x - k, z + k))
            .arc_through(v2(x, z - radius), v2(x + k, z + k))?
            .close()?,
    ))
}

/// The holder's section: flat on its back, domed over the channel.
fn b_body() -> Result<Profile> {
    let (bend, outer, z) = (tube::BEND_RADIUS, cap::b_fill::outer(), tube::CHANNEL_CENTRE + tube::DOME_LIFT);
    Ok(Profile::new(
        Pen::new(v2(bend - outer, 0.))
            .line_to(v2(bend + outer, 0.))
            .line_to(v2(bend + outer, z))
            .arc_through(v2(bend, z + outer), v2(bend - outer, z))?
            .close()?,
    ))
}

/// A mouth's insertion lead-in: a cone from outside the face down into the bore.
fn b_mouth(tear: bool) -> Result<Solid> {
    let mut sections = vec![];
    for (y, r) in [
        (-tube::MOUTH_OVERRUN, tube::CHANNEL_RADIUS + tube::MOUTH + tube::MOUTH_OVERRUN),
        (tube::MOUTH + tube::MOUTH_MERGE, tube::CHANNEL_RADIUS - tube::MOUTH_MERGE),
    ] {
        let profile = if tear { teardrop(r)? } else { Profile::circle(v2(tube::BEND_RADIUS, tube::CHANNEL_CENTRE), r) };
        sections.push(profile.place(&Plane::XZ.at(v3(0., y, 0.))));
    }
    Solid::loft(&sections)
}

/// The tube's channel through the lid: its straight inlet from the front face, the bend, and both
/// mouths, with the supported roof's allowance toward print-up.
fn b_channel() -> Result<Solid> {
    let passage = tube::passage();
    let inlet = passage.inlet_leg();
    let section = Profile::circle(v2(tube::BEND_RADIUS, tube::CHANNEL_CENTRE), tube::CHANNEL_RADIUS);
    let mut air = Plane::XZ
        .revolve(&section, 90., v2(0., 0.), v2(0., 1.))?
        .union(&Plane::XZ.extrude(&section, inlet)?)?;
    let mouth = b_mouth(false)?;
    air = air.union(&mouth.translate(v3(0., -inlet, 0.)))?.union(&mouth.mirror(V3::ZERO, v3(1., -1., 0.)))?;
    let end = p3(passage.bend_end);
    air = air
        .rotate(V3::ZERO, V3::Y, -90.)
        .translate(v3(end.x + tube::CHANNEL_CENTRE, end.y - tube::BEND_RADIUS, end.z));
    air = air.union(&air.translate(V3::Z * passage.roof_allowance))?;
    Ok(air.transformed(&world_to_cap()))
}

/// A section whose arcs are halved so a turn swept through it keeps the combined chord error of
/// section and turn inside the fabrication rule.
fn fine_section(profile: Profile) -> Result<Profile> {
    let mut segments = vec![];
    for segment in profile.outer.segs {
        if let Seg::Arc { a, b, c, ccw } = segment {
            let v = a - c;
            let mut turn = (b - c).angle() - v.angle();
            if ccw {
                while turn <= 0. {
                    turn += TAU;
                }
            } else {
                while turn >= 0. {
                    turn -= TAU;
                }
            }
            let count =
                2 * ((hsm_kernel::rule::ring_count(v.norm()) as f64 * turn.abs() / TAU - 1e-9).ceil() as usize).max(1);
            let mut start = a;
            for i in 1..=count {
                let angle = turn * i as f64 / count as f64;
                let end = if i == count {
                    b
                } else {
                    c + v2(v.x * cos(angle) - v.y * sin(angle), v.x * sin(angle) + v.y * cos(angle))
                };
                segments.push(Seg::Arc { a: start, b: end, c, ccw });
                start = end;
            }
        } else {
            segments.push(segment);
        }
    }
    Ok(Profile::new(Loop::new(segments)?))
}

/// The R14 holder: the accepted holder's quarter turn, printed flat on its domed back.
fn b_holder() -> Result<Solid> {
    let body = Plane::XZ.revolve(&fine_section(b_body()?)?, 90., v2(0., 0.), v2(0., 1.))?;
    let air = Plane::XZ.revolve(&fine_section(teardrop(tube::CHANNEL_RADIUS)?)?, 90., v2(0., 0.), v2(0., 1.))?;
    let mouth = b_mouth(true)?;
    body.cut(&air)?.cut(&mouth)?.cut(&mouth.mirror(V3::ZERO, v3(1., -1., 0.)))
}

// --- The pump --------------------------------------------------------------------------------------

/// How far the motor's room runs past each end of its band.
const ROOM_OVERRUN: f64 = 1.;
/// The rails' rooms rise to this height in the pump's frame, past everything above them.
const RAIL_ROOM_TOP: f64 = 100.;

/// The motor's room in the snap cap: a cylinder on the can's axis through the band and past it.
fn pump_room(c: &Cradle) -> Result<Solid> {
    let axis = p3(c.can.axis_direction);
    let origin = p3(c.can.axis_point_mm);
    let [first, last] = c.band;
    let x = first - ROOM_OVERRUN;
    let start = v3(x, origin.y, origin.z + axis.z * (x - origin.x) / axis.x);
    let t = placement(c.frame.rotation, c.frame.translation_mm);
    Solid::cylinder(t.point(start), t.vector(axis), c.bore_radius, (last - first + 2. * ROOM_OVERRUN) / axis.x)
}

/// The shared downward half pipe turned up over the motor: the pump's removable cap.
fn pump_cap_world(shape: &Solid, c: &Cradle) -> Solid {
    shape.rotate(v3(c.centre[0], 0., 0.), V3::Y, 180.).translate(V3::Z * c.centre[2])
}

/// The cradle: one broad lid-rooted block with a straight channel, stops on both rails, the rails'
/// rooms, the head's clearance ramp, the snap cap's pockets and the airline's corner opening.
fn pump_cradle() -> Result<Solid> {
    let c = pump::cradle();
    let running = cap::fits().running;
    let [cx, _, cz] = c.centre;
    let first = c.band[0];
    let fy = c.frame.translation_mm[1];
    let face = cap_face_z();
    let wide = c.stock_half_width + pump::FLANK_STOCK;
    let half = pump::CHANNEL_HALF_WIDTH;
    let [[fore0, fore1], [rear0, rear1]] = c.selected.rail_stop_native_x_mm;
    let mut body = box3(cx - wide, cx + wide, fy + fore0, fy + rear1, face - OVERCUT, cz);
    body = body.cut(&box3(cx - half, cx + half, fy + fore0 - OVERCUT, fy + rear1 + OVERCUT, face, cz + 1.))?;
    let frame = placement(c.frame.rotation, c.frame.translation_mm);
    for rail in &c.rails {
        let [a, b, k] = rail.floor_planes[0];
        let k = k - running * (1. + a * a + b * b).sqrt();
        let outer = rail.outer_y;
        let near = rail.side as f64 * half;
        let mut profiles = vec![];
        for x in [fore1, rear0] {
            profiles.push(Region::polygon(vec![
                v3(x, outer, a * x + b * outer + k),
                v3(x, near, a * x + b * near + k),
                v3(x, near, RAIL_ROOM_TOP),
                v3(x, outer, RAIL_ROOM_TOP),
            ]));
        }
        body = body.cut(&Solid::loft(&profiles)?.transformed(&frame))?;
    }
    // The end stop keeps one flat roof through its whole contact depth; the head's clearance ramp
    // begins at the stop's rear bearing plane.
    let tz = c.frame.translation_mm[2];
    let head = c.selected.rail_stop_native_z_mm;
    let slope = (cz - tz - head) / first;
    for (xa, xb) in [(fore0 - OVERCUT, fore1), (fore1, first)] {
        let mut profiles = vec![];
        for x in [xa, xb] {
            let (z, y) = (tz + head + slope * x.max(fore1), fy + x);
            profiles.push(Region::polygon(vec![
                v3(cx - wide - OVERCUT, y, z),
                v3(cx + wide + OVERCUT, y, z),
                v3(cx + wide + OVERCUT, y, cz + 1.),
                v3(cx - wide - OVERCUT, y, cz + 1.),
            ]));
        }
        body = body.cut(&Solid::loft(&profiles)?)?;
    }
    let s = &c.station;
    for side in [-1., 1.] {
        let far = s.axis_x + side * (wide + 1.);
        for (start, z0, z1) in [(s.ledge, s.split - 1., s.bearing), (s.neck, s.bearing, s.ceiling)] {
            let x = s.axis_x + side * start;
            let pocket = box3(x, far, s.y0 - running, s.y1 + running, z0, z1);
            body = body.cut(&pump_cap_world(&pocket, c))?;
        }
        let radius = s.root_radius;
        let near = s.axis_x + side * (s.inner - radius - running);
        let relief = box3(near, far, s.y0 - running, s.y1 + running, s.root - running, s.root + radius + running);
        body = body.cut(&pump_cap_world(&relief, c))?;
    }
    // The air passage opens through this outside corner behind the cap; the whole bearing lands
    // stay inboard of the spring's outer face.
    let (east, aft) = (cx + wide, fy + rear1);
    let cap_end = s.y1 + running;
    let clearance = box3(cx + c.stock_half_width, east + OVERCUT, cap_end, aft + OVERCUT, face - 2. * OVERCUT, cz + 2. * OVERCUT);
    Ok(body.cut(&clearance)?.transformed(&world_to_cap()))
}

/// The snap cap: a filled box half pipe with a thick crown and two independent spring wings,
/// standing on one axial end so its body, wings and hooks grow as vertical walls.
fn pump_snap() -> Result<Solid> {
    let c = pump::cradle();
    let s = &c.station;
    let (x, w, wi, h) = (s.axis_x, s.outer, s.inner, s.hook);
    let base = -cap::fits().slip;
    let root = s.root_radius;
    let k = root / 2_f64.sqrt();
    let r = c.bore_radius + c.selected.cap_arch_wall_mm;
    let west = [
        v2(x - w, 0.),
        v2(x - w, s.tip),
        v2(x - h, s.catch + s.nose_land),
        v2(x - h, s.catch),
        v2(x - wi, s.catch),
        v2(x - wi, base + root),
    ];
    let mut pen = Pen::new(west[0]);
    for &p in &west[1..] {
        pen = pen.line_to(p);
    }
    pen = pen
        .arc_through(v2(x - wi + root - k, base + root - k), v2(x - wi + root, base))?
        .line_to(v2(x + wi - root, base))
        .arc_through(v2(x + wi - root + k, base + root - k), v2(x + wi, base + root))?;
    for p in west.iter().rev().skip(1) {
        pen = pen.line_to(v2(2. * x - p.x, p.y));
    }
    pen = pen.line_to(v2(x + w, -r)).line_to(v2(x - c.selected.cap_east_roof_half_width_mm, -r));
    let blank = Plane::XZ.at(v3(0., s.y1, 0.)).extrude(&Profile::new(pen.close()?), s.y1 - s.y0)?;
    let snap = pump_cap_world(&blank, c).cut(&pump_room(c)?)?.rotate(V3::ZERO, V3::X, 90.);
    let b = snap.bounds();
    Ok(snap.translate(v3(-(b.min.x + b.max.x) / 2., -(b.min.y + b.max.y) / 2., -b.min.z)))
}

// --- V-B's wall, the union support and the wells -----------------------------------------------------

/// V-B's upright wall: the bearing block and its root, the valve seat's four blind sockets and its
/// port channel open through both faces.
fn valve_wall() -> Result<Solid> {
    use hsm_valve_seat_numbers as seat;
    let w = cap::valve::wall();
    let body = cuboid(w.bearing).union(&cuboid(w.root))?;
    let pose = cap::valve::pose();
    let t = placement(pose.rotation, pose.translation);
    let mut cuts = vec![];
    for sx in [-1., 1.] {
        for sy in [-1., 1.] {
            cuts.push(
                cylinder(
                    v2(sx * seat::valve::CORNER_INSET_X, sy * seat::valve::CORNER_INSET_Y),
                    seat::SOCKET_FLOOR_Z,
                    seat::SEAT_TOP_Z + 1.,
                    seat::SOCKET_RADIUS,
                )?
                .transformed(&t),
            );
        }
    }
    let length = 2. * seat::half_y(cap::fits().slip) + 2.;
    cuts.push(
        Solid::cylinder(
            v3(0., -length / 2., seat::valve::PORT_CENTER_Z),
            V3::Y,
            seat::valve::PORT_RADIUS + seat::PORT_AIR,
            length,
        )?
        .transformed(&t),
    );
    Ok(body.cut(&Solid::union_all(&cuts)?)?.transformed(&world_to_cap()))
}

/// The union support's bearing, in the cap's frame, and its closed tie passage.
fn union_support() -> Result<(Solid, Solid)> {
    use cap::unions;
    let t = world_to_cap();
    let d = unions::vb_outlet_return();
    let stock = Solid::cuboid(p3(d.stock_min), p3(d.stock_max))
        .cut(&Solid::cylinder(p3(d.bore_origin), p3(d.bore_axis), d.seat_radius, d.bore_length)?)?
        .transformed(&t);
    let normal = p3(d.tie_profile_normal);
    let plane = Plane::new(p3(d.tie_profile_origin) - normal * (unions::TIE_PASSAGE_LENGTH / 2.), p3(d.tie_profile_x), normal)?;
    let points: Vec<V2> = unions::TIE_PROFILE.iter().map(|p| v2(p[0], p[1])).collect();
    let passage = plane.extrude(&Profile::polygon(&points), unions::TIE_PASSAGE_LENGTH)?.transformed(&t);
    Ok((stock, passage))
}

/// The wiring's wells, their stock and their pockets, in the cap's frame.
fn wells() -> Result<(Solid, Solid)> {
    use cap::wells::{POCKET_OVERRUN, WALL};
    let fit = cap::wells::fit();
    let (mut stock, mut cuts) = (vec![], vec![]);
    let t = world_to_cap();
    for well in cap::wells::wells() {
        let (width, depth, height) = (well.wago.width, well.wago.depth, well.wago.height);
        let at = placement(well.rotation, well.translation);
        stock.push(
            box3(-width / 2. - fit - WALL, width / 2. + fit + WALL, -depth / 2. - fit - WALL, 0., -fit - WALL, height + fit + WALL)
                .transformed(&at)
                .transformed(&t),
        );
        cuts.push(
            box3(-width / 2. - fit, width / 2. + fit, -depth / 2. - fit, POCKET_OVERRUN, -fit, height + fit)
                .transformed(&at)
                .transformed(&t),
        );
    }
    Ok((Solid::union_all(&stock)?, Solid::union_all(&cuts)?))
}

// --- Clips and cable seats -----------------------------------------------------------------------

/// A C2 tube clip in the enclosure: the filled root down to the lid's face and the two free jaws,
/// traced as one section and extruded along the tube.
fn tube_clip(c: &cap::clips::Clip) -> Result<Solid> {
    let centre = p3(c.centre);
    let u = p3(c.along).unit();
    let plane = Plane::new(centre - u * (c.span / 2.), u.cross(V3::Z), u)?;
    let (ri, wing, span) = (c.radius, c.wing, c.span);
    let (ro, rm, nose) = (ri + wing, ri + wing / 2., wing / 2.);
    let tip = c.tip_degrees * PI / 180.;
    let point = |r: f64, t: f64| v2(r * sin(t), r * cos(t));
    let (a, b, cc, d) = (point(ro, -tip), point(ro, tip), point(ri, tip), point(ri, -tip));
    let (cp, cn) = (point(rm, tip), point(rm, -tip));
    let reach = centre.z - cap_face_z() + OVERCUT;
    // The filled root replaces the outer half-circle on the host's side of the tube's axis.
    let outer = Pen::new(v2(-ro, reach))
        .line_to(v2(ro, reach))
        .line_to(v2(ro, 0.))
        .arc_through(point(ro, (PI / 2. + tip) / 2.), b)?
        .arc_through(cp + v2(nose * cos(tip), -nose * sin(tip)), cc)?
        .arc_through(v2(0., ri), d)?
        .arc_through(cn + v2(-nose * cos(-tip), nose * sin(-tip)), a)?
        .arc_through(point(ro, -(PI / 2. + tip) / 2.), v2(-ro, 0.))?
        .close()?;
    plane.extrude(&Profile::new(outer), span)
}

/// The crossover's clip, cut where V-B's wall roots so each half ends on the root's plane, and the
/// self-supporting sloped bridge that joins its filled root to the wall.
fn flavor_a_clip(c: &cap::clips::Clip, wall: &cap::valve::Wall) -> Result<Solid> {
    let x0 = wall.root[0][0];
    let y0 = wall.root[1][1] - OVERCUT;
    let z0 = cap_face_z() - OVERCUT;
    let [cx, cy, cz] = c.centre;
    let root_front = cy - (c.radius + c.wing);
    let front = root_front + OVERCUT;
    let half = c.span / 2.;
    let bridge = Plane::YZ.at(v3(x0, 0., 0.)).extrude(
        &Profile::polygon(&[v2(y0, z0), v2(front, z0), v2(front, cz + front - root_front), v2(y0, cz + y0 - root_front)]),
        cx + half - x0,
    )?;
    let left = cap::clips::Clip { centre: [(cx - half + x0) / 2., cy, cz], span: x0 - cx + half, ..*c };
    let right = cap::clips::Clip { centre: [(cx + half + x0) / 2., cy, cz], span: cx + half - x0, ..*c };
    tube_clip(&left)?.union(&tube_clip(&right)?.union(&bridge)?)
}

/// How far a cable seat's section runs down into the lid's face.
const SEAT_SINK: f64 = 0.1;

/// The manifold bank's section: two stepped seats, each with its retaining lip.
fn bank_section(s: &cap::cables::Bank) -> Vec<V2> {
    let (stock, depth, beak) = (s.stock, s.seat_depth, s.beak);
    let [first, second] = s.seat_heights;
    let (a, b, c, d) = (stock, stock + depth, 2. * stock + depth, 2. * (stock + depth));
    let width = 3. * stock + 2. * depth;
    let (ra, rb) = (stock + first, stock + second);
    let (ta, tb) = (ra + stock + beak, rb + stock + beak);
    vec![
        v2(0., -SEAT_SINK),
        v2(width - stock, -SEAT_SINK),
        v2(width, stock - SEAT_SINK),
        v2(width, tb),
        v2(d, tb),
        v2(d - beak, tb - beak),
        v2(d - beak, rb),
        v2(d, rb),
        v2(d, stock),
        v2(c, stock),
        v2(c, ta),
        v2(b, ta),
        v2(b - beak, ta - beak),
        v2(b - beak, ra),
        v2(b, ra),
        v2(b, stock),
        v2(a, stock),
        v2(a, ta),
        v2(0., ta),
    ]
}

/// The level hook's section: one seat and its lip.
fn hook_section(s: &cap::cables::Hook) -> Vec<V2> {
    let (stock, depth, beak) = (s.stock, s.seat_depth, s.beak);
    let inner = stock + depth;
    let width = 2. * stock + depth;
    let roof = stock + s.seat_height;
    let top = roof + stock + beak;
    vec![
        v2(0., -SEAT_SINK),
        v2(width, -SEAT_SINK),
        v2(width, top),
        v2(inner, top),
        v2(inner - beak, top - beak),
        v2(inner - beak, roof),
        v2(inner, roof),
        v2(inner, stock),
        v2(stock, stock),
        v2(stock, top),
        v2(0., top),
    ]
}

/// A cable seat's section in the enclosure's XZ plane at `origin`, extruded along Y over `span`.
fn cable_seat(points: &[V2], origin: [f64; 3], span: f64) -> Result<Solid> {
    let origin = p3(origin) + V3::Y * (span / 2.);
    Ok(Plane::XZ.at(origin).extrude(&Profile::polygon(points), span)?.transformed(&world_to_cap()))
}

// --- Reservoir A's anchors -------------------------------------------------------------------------

/// A seat's clearance along a whole route: a circle swept on the route's centreline.
fn route_air(runs: &[Run], radius: f64) -> Result<Solid> {
    let first = p3(runs[0].first());
    let mut path = Path::new(first);
    for run in runs {
        match run {
            Run::Line { points } => path = path.line_to(p3(points[1])),
            Run::Arc { points, .. } => path = path.arc_through(p3(points[1]), p3(points[2]))?,
        }
    }
    // A swept circle has both section and path chord error; the same circular path, subdivided at
    // half intervals, keeps the combined error within LINEAR.
    let mut fine = Path::new(first);
    for leg in &path.legs {
        match *leg {
            Leg::Line { b, .. } => fine = fine.line_to(b),
            Leg::Arc { a, b, c, d, turn } => {
                let count =
                    2 * ((hsm_kernel::rule::ring_count((a - c).norm() + radius) as f64 * turn / TAU - 1e-9).ceil() as usize)
                        .max(1);
                let v = a - c;
                for i in 1..=count {
                    let angle = turn * i as f64 / count as f64;
                    let end = if i == count {
                        b
                    } else {
                        c + v * cos(angle) + d.cross(v) * sin(angle) + d * (d.dot(v) * (1. - cos(angle)))
                    };
                    fine = fine.arc_center(c, end, d)?;
                }
            }
            Leg::Curve { .. } => bail!("a seat's route is lines and circular arcs"),
        }
    }
    let normal = match path.legs.first().context("a route has runs")? {
        Leg::Line { a, b } => (*b - *a).unit(),
        Leg::Arc { a, c, d, .. } => d.cross(*a - *c).unit(),
        _ => bail!("a seat's route is lines and circular arcs"),
    };
    let (_, x, _) = hsm_kernel::rule::plane_frame(normal);
    Plane::new(first, x, normal)?.sweep(&Profile::circle(v2(0., 0.), radius), &fine)
}

/// Reservoir A's anchors, in the cap's frame: the aft saddle with its seats swept along both
/// routes and its tie slot and mouths cut, then the fore pair's base with both bores; and the aft
/// saddle's slot and mouths, which the lid takes too.
fn a_seats() -> Result<(Solid, Solid)> {
    use reservoir_a::aft;
    let t = world_to_cap();
    let seat = reservoir_a::aft_seat();
    let (lo, hi) = (p3(seat.stock[0]), p3(seat.stock[1]));
    let mut profile = vec![v2(lo.x, lo.z), v2(hi.x, lo.z)];
    for p in seat.seat_roof.iter().rev() {
        profile.push(v2(p[0], p[1]));
    }
    let mut saddle = Plane::XZ.at(v3(0., hi.y, 0.)).extrude(&Profile::polygon(&profile), hi.y - lo.y)?;
    for route in aft::ROUTES_WEST_TO_EAST {
        saddle = saddle.cut(&route_air(&reservoir_a::routes()[route], aft::SEAT_RADIUS)?)?;
    }
    let mouths = Solid::union_all(&[cuboid(seat.tie_slot), cuboid(seat.access[0]), cuboid(seat.access[1])])?;
    let saddle = saddle.cut(&mouths)?.transformed(&t);
    // The fore pair's bores cut the broad common base across its whole span; its clips join the
    // other C2 seats.
    let pair = reservoir_a::pair();
    let mut base = cuboid(pair.base);
    let span = reservoir_a::pair::SPAN;
    for centre in pair.tube_centres {
        base = base.cut(&Solid::cylinder(p3(centre) - V3::Y * (span / 2. + OVERCUT), V3::Y, pair.seat_radius, span + 2. * OVERCUT)?)?;
    }
    Ok((Solid::union_all(&[saddle, base.transformed(&t)])?, Solid::union_all(&[mouths.transformed(&t)])?))
}

// --- The lid -------------------------------------------------------------------------------------

/// The equipment lid: one uniform plate on its flat underside, the clamp screws' recessed heads,
/// the conduits' bores and countersinks, reservoir B's fill channel and its holder's window, the
/// straight guides, the board's deck columns, and the mounts the crown's parts stand in.
fn top_lid() -> Result<Solid> {
    let fits = cap::fits();
    let h = core::foam_cap_lid_height(&fits);
    let floor = core::WALL_AND_FLOOR_THICKNESS;
    let through = cap::lid_cut_through_depth();
    let bore = core::CAP_CONDUIT_BORE_RADIUS;
    let t = world_to_cap();
    let head_depth = core::head_cbore_depth(&fits);
    let mut body = outline(0., h, 0.)?.cut(&head_pockets(true, h - head_depth, head_depth)?)?;
    let mut cuts = vec![];
    for (station, _) in core::lid_attachment_stations() {
        cuts.push(cylinder(xy(station), 0., through, core::screw_clearance_radius(&fits))?);
    }
    for conduit in cap::conduits::lid_bores() {
        cuts.push(cylinder(xy(conduit.xy), 0., through, cap::conduits::bore_radius(conduit.name))?);
    }
    for conduit in cap::conduits::reliefs() {
        let p = xy(conduit.xy);
        cuts.push(Solid::cone(v3(p.x, p.y, h - floor), V3::Z, bore, core::cap_conduit_entry_relief_radius(), floor)?);
    }
    cuts.push(b_channel()?);
    let guides = cap::conduits::straight_guides();
    for g in &guides {
        let p = p3(g.point);
        cuts.push(Solid::cylinder(v3(p.x, p.y, g.floor - 1.), V3::Z, bore, p.z + 2. - g.floor)?.transformed(&t));
    }
    body = body.cut(&Solid::union_all(&cuts)?)?;
    for g in &guides {
        let p = t.point(p3(g.point));
        let guide = cylinder(v2(p.x, p.y), 0., p.z, bore + cap::conduits::GUIDE_WALL)?
            .cut(&cylinder(v2(p.x, p.y), -OVERCUT, p.z + 1., bore)?)?;
        body = body.union(&guide)?;
    }
    // A plain clearance window lets the independent R14 holder stay with its tube.
    let [lo, hi] = cap::b_fill::holder_bounds();
    let gap = cap::b_fill::WINDOW_CLEARANCE;
    body = body.cut(&box3(lo[0] - gap, hi[0] + gap, lo[1] - gap, hi[1] + gap, -OVERCUT, h + OVERCUT))?;
    let bore_depth = cap::deck::bore_depth();
    for column in cap::deck::columns() {
        let p = xy(column.xy);
        body = body
            .union(&cylinder(p, h - OVERCUT, column.top, core::DECK_MOUNT_BOSS_RADIUS)?)?
            .cut(&cylinder(p, column.top - bore_depth, column.top + OVERCUT, core::DECK_MOUNT_BORE_RADIUS)?)?;
    }
    body = body.union(&pump_cradle()?)?.union(&valve_wall()?)?;
    let (support, passage) = union_support()?;
    body = body.union(&support)?.cut(&passage)?;
    let (stock, pockets) = wells()?;
    body = body.union(&stock.intersect(&outline(-1., stock.bounds().max.z + 1., 0.)?)?)?.cut(&pockets)?;
    let (stock, passages) = a_seats()?;
    body = body.union(&stock)?.cut(&passages)?;
    let wall = cap::valve::wall();
    for (i, clip) in cap::clips::clips().iter().enumerate() {
        let clip = if i == 1 { flavor_a_clip(clip, &wall)? } else { tube_clip(clip)? };
        body = body.union(&clip.transformed(&t))?;
    }
    let bank = cap::cables::manifold_bank();
    let hook = cap::cables::level_hook();
    body = body
        .union(&cable_seat(&bank_section(&bank), bank.origin, bank.span)?)?
        .union(&cable_seat(&hook_section(&hook), hook.origin, hook.span)?)?;
    let air_top = body.bounds().max.z + OVERCUT;
    let mut air = vec![];
    for hole in cap::air_holes() {
        air.push(cylinder(xy(hole.xy), -OVERCUT, air_top, hole.radius)?);
    }
    // One straight shallow recess clears the pump's molded cover and its forward head.
    let c = pump::cradle();
    let cx = c.centre[0];
    let fy = c.frame.translation_mm[1];
    let fore = c.selected.cover_channel_fore_native_x_mm;
    let aft = c.selected.rail_stop_native_x_mm[1][1];
    let face = cap_face_z();
    let half = pump::CHANNEL_HALF_WIDTH;
    let recess = box3(cx - half, cx + half, fy + fore - OVERCUT, fy + aft + OVERCUT, face - c.selected.cover_channel_recess_mm, face + OVERCUT)
        .transformed(&t);
    body.cut(&Solid::union_all(&air)?)?.cut(&recess)
}

// --- The numbers the machine reads -------------------------------------------------------------------

/// `foam-cap.numbers.json`: the pump's mount, the wiring's wells, the union support and the
/// conduits the wiring's cables pass, as the whole machine reads them.
fn machine_numbers(dir: &std::path::Path) -> Result<()> {
    let c = pump::cradle();
    let s = &c.station;
    let station = json!({
        "axis_x": s.axis_x, "y0": s.y0, "y1": s.y1, "split": s.split, "neck": s.neck,
        "ledge": s.ledge, "inner": s.inner, "outer": s.outer, "hook": s.hook, "bearing": s.bearing,
        "catch": s.catch, "tip": s.tip, "ceiling": s.ceiling, "root": s.root,
        "nose_land": s.nose_land, "root_radius": s.root_radius,
        "tool_angle_degrees": s.tool_angle_degrees, "tool_end_stock": s.tool_end_stock,
        "tool_outer_edges": [s.tool_outer_edge, Value::Null], "tool_ports": [],
    });
    let rails: Vec<Value> = c
        .rails
        .iter()
        .map(|r| json!({"side": r.side, "outer_y_mm": r.outer_y, "floor_planes": r.floor_planes}))
        .collect();
    let mut cap_datum = json!({
        "band_native_x_mm": c.band, "can": c.can, "centre_world_mm": c.centre,
        "cover_room_native_y_mm": c.cover_room,
        "frame": {"reference": c.frame.reference, "rotation": c.frame.rotation, "translation_mm": c.frame.translation_mm},
        "rail_rooms": rails, "seat_bore_radius_mm": c.seat_bore_radius, "selected": c.selected,
        "bore_radius_mm": c.bore_radius, "snap_station": station, "cap_band_native_x_mm": c.cap_band,
        "pocket_band_native_x_mm": c.pocket_band, "stock_half_width_mm": c.stock_half_width,
    });
    let mut datum = cap_datum.clone();
    datum["caps"] = json!([cap_datum.take()]);
    datum["end_stock_mm"] = json!(c.end_stock);

    let wells: Vec<Value> = cap::wells::wells()
        .iter()
        .map(|w| {
            json!({"name": w.name, "pose": {"parent": cap::wells::HOST, "rotation": w.rotation,
                   "size": w.wago.size, "translation_mm": w.translation}})
        })
        .collect();

    let u = cap::unions::vb_outlet_return();
    let support = json!({
        "stock_min_world_mm": u.stock_min, "stock_max_world_mm": u.stock_max,
        "bore_origin_world_mm": u.bore_origin, "bore_axis_world": u.bore_axis,
        "bore_length_mm": u.bore_length, "seat_radius_mm": u.seat_radius,
        "native_leg": cap::unions::NATIVE_LEG, "native_band_mm": cap::unions::NATIVE_BAND,
        "tie_window_min_world_mm": u.tie_window_min, "tie_window_max_world_mm": u.tie_window_max,
        "tie_profile_origin_world_mm": u.tie_profile_origin, "tie_profile_x_world": u.tie_profile_x,
        "tie_profile_normal_world": u.tie_profile_normal, "tie_profile_mm": cap::unions::TIE_PROFILE,
        "tie_route_native_down_mm": u.tie_route_down, "centre_world_mm": u.centre,
        "wall_mm": cap::unions::WALL, "parent": cap::unions::HOST, "support_implemented": true,
    });

    let conduits: serde_json::Map<String, Value> =
        cap::conduits::lid_bores().iter().map(|c| (c.name.to_owned(), json!(c.xy))).collect();

    let numbers = json!({
        "pump": datum, "wells": wells, "union_supports": {"vb-outlet-return": support}, "conduits": conduits,
    });
    let mut text = Vec::new();
    let mut writer = serde_json::Serializer::with_formatter(&mut text, serde_json::ser::PrettyFormatter::with_indent(b" "));
    numbers.serialize(&mut writer)?;
    text.push(b'\n');
    presentation::printed::keep(&dir.join("foam-cap.numbers.json"), &text)
}
