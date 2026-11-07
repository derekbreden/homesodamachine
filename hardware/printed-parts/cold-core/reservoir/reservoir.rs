//! The flavour reservoirs' files. Each side's PETG cup, the side −1 cup the mirror of side +1: its
//! walls round the cavity, the heat-set insert bosses hung from its rim, and the level rod's anchor
//! on its floor. Each side's cap, from its wall's foot up to its plate: the plate and perimeter
//! wall, the screw bosses with their clearance holes and counterbores, the rod's register, and the
//! flush seats its fill, draw and air grips take. The gasket between cup and cap, and the two TPU grips.
//! The caps' and the grips' payloads are their prints' triangles, every one kept.
//!
//!     reservoir [<output directory>]
use anyhow::{Context, Result, bail, ensure};
use hsm_cold_core_interface as core;
use hsm_kernel::math::{TAU, cos, sin};
use hsm_kernel::part::write_part;
use hsm_kernel::rule::ring_count;
use hsm_kernel::write::PrintOutput;
use hsm_kernel::*;
use hsm_print_payload as presentation;
use hsm_reservoir_numbers as res;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::path::{Path, PathBuf};

const OUTPUT: &str = "hardware/printed-parts/cold-core/reservoir";
/// How far a cutter overruns the faces it opens.
const OVERCUT: f64 = 0.1;
/// The reach of the block that takes away what lies under a boss's flat.
const UNDER_FLAT: f64 = 500.;

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: reservoir [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let cup = cup()?;
    for side in [1, -1] {
        let label = if side > 0 { "right" } else { "left" };
        println!("{}", write_drawn(&out, &format!("reservoir-{label}"), res::cup_colour().linear, &placed(&cup, side))?);
        println!("{}", write_printed(&out, &format!("reservoir-cap-{label}"), res::cap_colour().linear, &cap(side)?)?);
    }
    println!("{}", write_drawn(&out, "reservoir-gasket", res::gasket_colour().linear, &gasket()?)?);
    for (name, grip_of) in [("reservoir-tube-grip", &res::LIQUID_GRIP), ("reservoir-air-grip", &res::AIR_GRIP)] {
        println!("{}", write_printed(&out, name, res::grip_colour().linear, &grip(grip_of)?)?);
    }
    Ok(())
}

/// The side +1 cup: the outline's walls and floor round the cavity, a boss under the rim at each
/// station with its flat underneath and its insert's pocket from above, and the rod's anchor boss
/// on the floor with the rod's blind seat.
fn cup() -> Result<Solid> {
    let [bottom, rim] = res::outer_z();
    let [floor, top] = res::inner_z();
    let mut cup = envelope(bottom, rim, 0., Some(res::OUTER_ROUND))?
        .cut(&envelope(floor, top, res::WALL_THICKNESS, Some(res::INNER_ROUND))?)?;
    let boss_bottom = rim - res::BOSS_HEIGHT;
    for station in res::stations() {
        let (pivot, toward) = (station.flat.pivot, station.flat.toward);
        let flat = Plane::new(
            v3(pivot[0], pivot[1], boss_bottom),
            v3(-toward[1], toward[0], 0.),
            v3(toward[0], toward[1], 1.),
        )?;
        let boss = cylinder(station.xy, boss_bottom - res::BOSS_OVERRUN, rim, res::BOSS_RADIUS)?
            .cut(&flat.extrude(&Profile::rect(v2(0., 0.), UNDER_FLAT, UNDER_FLAT), -UNDER_FLAT)?)?;
        let pocket = cylinder(station.xy, rim - res::INSERT_POCKET_DEPTH, rim + OVERCUT, res::INSERT_POCKET_RADIUS)?;
        cup = cup.union(&boss)?.cut(&pocket)?;
    }
    let rod = [res::rod_x(), res::ROD_Y];
    let anchor_top = floor + res::ROD_ANCHOR_HEIGHT;
    cup = cup.union(&cylinder(rod, floor, anchor_top, res::rod_boss_diameter() / 2.)?)?;
    cup.cut(&cylinder(rod, floor + res::ROD_ANCHOR_FLOOR, anchor_top + OVERCUT, res::rod_bore() / 2.)?)
}

/// One side's cap, its wall's foot at Z = 0: the plate over the outline and the wall round it, a
/// boss the wall's height at each station with its clearance hole and its counterbore from the
/// plate's top, mirrored to its side; then the air grip's seat, the rod's register boss reaching
/// down past the wall with its blind seat, and the fill and draw grips' seats, each at its side's
/// port.
fn cap(side: i64) -> Result<Solid> {
    let (height, wall) = (res::CAP_HEIGHT, res::CAP_WALL_HEIGHT);
    let stations = res::stations();
    let mut cap = envelope(0., height, 0., Some(res::OUTER_ROUND))?
        .cut(&envelope(0., wall, res::CAP_WALL_WIDTH, None)?)?;
    let bosses = stations.iter().map(|s| cylinder(s.xy, 0., wall, res::BOSS_RADIUS)).collect::<Result<Vec<_>>>()?;
    cap = cap.union(&Solid::compose(&bosses))?;
    let shank = res::clearance_hole_diameter() / 2.;
    let holes = stations.iter().map(|s| cylinder(s.xy, -OVERCUT, height + OVERCUT, shank)).collect::<Result<Vec<_>>>()?;
    cap = cap.cut(&Solid::compose(&holes))?;
    let (head, seat_z) = (res::counterbore_diameter() / 2., height - res::counterbore_depth());
    let heads = stations.iter().map(|s| cylinder(s.xy, seat_z, height + OVERCUT, head)).collect::<Result<Vec<_>>>()?;
    cap = placed(&cap.cut(&Solid::compose(&heads))?, side);
    cap = cap.cut(&seat(&res::AIR_GRIP, port(&res::AIR_PORT, side)?, wall)?)?;
    let rod = [res::rod_x() * side as f64, res::ROD_Y];
    cap = cap
        .union(&cylinder(rod, -res::ROD_REGISTER_HEIGHT, wall, res::rod_boss_diameter() / 2.)?)?
        .cut(&cylinder(rod, -res::ROD_REGISTER_HEIGHT - OVERCUT, wall, res::rod_bore() / 2.)?)?;
    if core::RESERVOIR_FILL_SIDES.contains(&side) {
        cap = cap.cut(&seat(&res::LIQUID_GRIP, port(&core::RESERVOIR_FILL_PORT, side)?, wall)?)?;
    }
    cap.cut(&seat(&res::LIQUID_GRIP, port(&core::RESERVOIR_DRAW_PORT, side)?, wall)?)
}

/// The gasket: the strip round the outline, a pad at each station, and each pad's clearance hole.
fn gasket() -> Result<Solid> {
    let height = res::GASKET_THICKNESS;
    let stations = res::stations();
    let gasket = envelope(0., height, 0., Some(res::OUTER_ROUND))?
        .cut(&envelope(0., height, res::GASKET_STRIP_WIDTH, None)?)?;
    let pads = stations.iter().map(|s| cylinder(s.xy, 0., height, res::BOSS_RADIUS)).collect::<Result<Vec<_>>>()?;
    let gasket = gasket.union(&Solid::compose(&pads))?;
    let shank = res::clearance_hole_diameter() / 2.;
    let holes = stations.iter().map(|s| cylinder(s.xy, -OVERCUT, height + OVERCUT, shank)).collect::<Result<Vec<_>>>()?;
    gasket.cut(&Solid::compose(&holes))
}

/// A grip on its axis, standing on Z = 0: its spool, and the tube's bore through it with its
/// lead-ins.
fn grip(grip: &res::Grip) -> Result<Solid> {
    let (bore, lead, lead_h) = (grip.bore_d / 2., grip.lead_d / 2., grip.lead_h);
    let top = res::PLATE_THICKNESS;
    let opening = cylinder([0., 0.], -OVERCUT, top + OVERCUT, bore)?
        .union(&Solid::cone(V3::ZERO, V3::Z, lead, bore, lead_h)?)?
        .union(&Solid::cone(v3(0., 0., top - lead_h), V3::Z, bore, lead, lead_h)?)?;
    spool(grip, [0., 0.], 0.)?.cut(&opening)
}

/// A grip's spool through the plate from `z0`: the waist, and a flare at each face.
#[track_caller]
fn spool(grip: &res::Grip, xy: [f64; 2], z0: f64) -> Result<Solid> {
    let (waist, flare) = (grip.waist_d / 2., grip.flare_d / 2.);
    let (z1, depth) = (z0 + res::PLATE_THICKNESS, flare - waist);
    cylinder(xy, z0, z1, waist)?
        .union(&Solid::cone(v3(xy[0], xy[1], z0), V3::Z, flare, waist, depth)?)?
        .union(&Solid::cone(v3(xy[0], xy[1], z1 - depth), V3::Z, waist, flare, depth)?)
}

/// A grip's seat through the plate from `z0`: its spool, opened a little past the plate's outer
/// face at the flare, so a seat that overlaps the wall keeps the wall's lip under it.
#[track_caller]
fn seat(grip: &res::Grip, xy: [f64; 2], z0: f64) -> Result<Solid> {
    let z1 = z0 + res::PLATE_THICKNESS;
    spool(grip, xy, z0)?.union(&cylinder(xy, z1, z1 + OVERCUT, grip.flare_d / 2.)?)
}

/// A side's port off one of the interface's port tables.
fn port(table: &[(i64, [f64; 2])], side: i64) -> Result<[f64; 2]> {
    core::reservoir_port(table, side).with_context(|| format!("no port on side {side}"))
}

/// The part on `side`: side +1's as built, side −1's its mirror across X = 0.
fn placed(shape: &Solid, side: i64) -> Solid {
    if side < 0 { shape.mirror(V3::ZERO, V3::X) } else { shape.clone() }
}

/// The outline extruded from `bottom` to `top`, `inset` in from the cup's outer faces and out from
/// its curve, its corners rounded to `round` where it has one.
#[track_caller]
fn envelope(bottom: f64, top: f64, inset: f64, round: Option<f64>) -> Result<Solid> {
    Plane::XY.at(v3(0., 0., bottom)).extrude(&outline(inset, round)?, top - bottom)
}

/// The cup's outline in plan, `inset` in: the far face, the ±Y faces, and the centreward curve
/// through its apex, each arc cut finer than the rule cuts it.
fn outline(inset: f64, round: Option<f64>) -> Result<Profile> {
    let far = res::outer_far_x() - inset;
    let y = res::outer_y() - inset;
    let radius = res::outer_radius() + inset;
    let x = (radius * radius - y * y).sqrt();
    let outline = Pen::new(v2(x, y))
        .line_to(v2(far, y))
        .line_to(v2(far, -y))
        .line_to(v2(x, -y))
        .arc_through(v2(radius, 0.), v2(x, y))?
        .close()?;
    let outline = match round {
        Some(r) => outline.fillet(r)?,
        None => outline,
    };
    Ok(Profile::new(finer_arcs(outline)?))
}

/// `outline` with each arc cut into twice the arcs the rule gives its radius and turn, on the same
/// centre: the large concave curve then meets its corner rounds within the rule.
fn finer_arcs(outline: Loop) -> Result<Loop> {
    let mut segments = vec![];
    for segment in outline.segs {
        let Seg::Arc { a, b, c, ccw } = segment else {
            segments.push(segment);
            continue;
        };
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
        let count = 2 * ((ring_count(v.norm()) as f64 * turn.abs() / TAU - 1e-9).ceil() as usize).max(1);
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
    }
    Loop::new(segments)
}

/// A cylinder on the XY plane at `xy`, from `bottom` to `top`.
#[track_caller]
fn cylinder(xy: [f64; 2], bottom: f64, top: f64, radius: f64) -> Result<Solid> {
    Plane::XY.at(v3(xy[0], xy[1], bottom)).cylinder(radius, top - bottom)
}

/// A piece the site draws from its solid: its STEP, fine model, payload and STL.
fn write_drawn(dir: &Path, name: &str, colour: [f64; 3], solid: &Solid) -> Result<Value> {
    one_body(name, solid)?;
    write_part(dir, name, &[Body { name, color: Some(colour), solid }])
}

/// A piece the site draws as its print: its STEP, its fine model bound to its STL, the STL, and
/// the payload cut from the STL's triangles with every one kept, naming the STEP by its SHA-256.
fn write_printed(dir: &Path, name: &str, colour: [f64; 3], solid: &Solid) -> Result<Value> {
    one_body(name, solid)?;
    let fine = [Body { name, color: Some(colour), solid }];
    let step = step_bytes(&fine, name)?;
    let simple = solid.simplified()?;
    let print = PrintOutput::new(&[Body { name, color: Some(colour), solid: &simple }]);
    let model = print.model_bytes(&fine, &format!("{name}.stl"), None)?;
    let stl = print.into_stl_bytes();
    let (mesh, _) = presentation::weld(&stl)?;
    let src = format!("{:x}", Sha256::digest(&step));
    let payload = presentation::cut(&mesh, None, presentation::Request {
        name: json!(name),
        color: json!(colour),
        src: &src,
        crease_deg: presentation::CREASE_DEG,
        deflection_ratio: presentation::LINEAR_DEFLECTION_RATIO,
        preserve: true,
        unknown: false,
        check: false,
    })?
    .payload;
    let files = [
        (format!("{name}.step"), step),
        (format!("{name}.step.npz"), model),
        (format!("{name}.step.mesh"), payload),
        (format!("{name}.stl"), stl),
    ];
    for (file, bytes) in &files {
        keep(&dir.join(file), bytes)?;
    }
    let bounds = solid.bounds();
    Ok(json!({
        "files": files.iter().map(|(file, _)| file.as_str()).collect::<Vec<_>>(),
        "bodies": [{
            "name": name,
            "volume": solid.volume(),
            "area": solid.area(),
            "min": bounds.min.to_array(),
            "max": bounds.max.to_array(),
            "triangles": solid.tris().len(),
        }],
    }))
}

fn one_body(name: &str, solid: &Solid) -> Result<()> {
    ensure!(solid.components().len() == 1, "{name} is one connected body");
    Ok(())
}

/// `bytes` at `path`, unless the file holds them already: written to a sibling and renamed onto it,
/// so the file lands whole.
fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path.file_name().and_then(|f| f.to_str()).with_context(|| format!("no file name in {}", path.display()))?;
    let sibling = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&sibling, bytes).with_context(|| format!("writing {}", sibling.display()))?;
    std::fs::rename(&sibling, path).with_context(|| format!("renaming onto {}", path.display()))
}
