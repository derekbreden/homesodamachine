//! The cold core, whole, in the foam shell's frame: the casing, the carbonator with its coil, its
//! fittings and its earth bond, both reservoirs in their pockets with their grips and air tubes,
//! the floats, reeds and probes, and the lines potted among them. It writes the core's STEP and the
//! payload the site draws, with the printed casing pieces drawn from their own print surfaces; the
//! fine model the whole-machine program places the core from (`cold-core-assembly.scene.npz`); and
//! the carbonator's earth-bond datums the machine's wiring lands its earth lead on
//! (`cold-core-assembly.numbers.json`).
//!
//!     cold-core-assembly [<output directory>]
#[path = "core-assembly/copper.rs"]
mod copper;
#[allow(dead_code)]
#[path = "core_routes.rs"]
mod core_routes;
#[path = "core-assembly/spools.rs"]
mod spools;
#[path = "core-assembly/stand_ins.rs"]
mod stand_ins;
#[path = "core-assembly/surfaces.rs"]
mod surfaces;

use anyhow::{Context, Result, anyhow, bail};
use hsm_carbonator_numbers::{self as carbonator, Plate};
use hsm_coil_numbers::Tail;
use hsm_cold_core_assembly_numbers::{self as numbers, Placement, Turn, presentation};
use hsm_cold_core_catalog::{self as catalog, Colour};
use hsm_cold_core_layout::routes;
use hsm_foam_assembly_numbers as casing;
use hsm_kernel::part::{AssemblyBody, write_assembly};
use hsm_kernel::*;
use hsm_reservoir_numbers as reservoir;
use serde_json::{Map, Value, json};
use std::path::{Path, PathBuf};

const NAME: &str = "cold-core-assembly";
const OUTPUT: &str = "hardware/cold-core-layout";

/// One body the core places: its name, what it is drawn in, its fine solid, and whether it is
/// drawn at its own part's viewer budget.
struct Piece {
    name: String,
    colour: Colour,
    fine: Solid,
    part_budget: bool,
}

fn main() -> Result<()> {
    let mut args = std::env::args_os().skip(1);
    let out = args.next().map(PathBuf::from).unwrap_or_else(|| PathBuf::from(OUTPUT));
    if args.next().is_some() {
        bail!("usage: cold-core-assembly [<output directory>]");
    }
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    // The solids go once their files are written; the printed surfaces go into the payload after.
    let mut answer = write(&out, &bodies()?, &lines()?)?;
    let model = out.join(format!("{NAME}.step.npz"));
    surfaces::graft(&out.join(format!("{NAME}.step.mesh")), &model, &printed_surfaces()?)?;
    std::fs::rename(&model, out.join(format!("{NAME}.scene.npz")))?;
    let datums = format!("{:#}\n", earth_datums()).into_bytes();
    keep(&out.join(format!("{NAME}.numbers.json")), &datums)?;
    answer["files"] = json!([
        format!("{NAME}.step"),
        format!("{NAME}.step.mesh"),
        format!("{NAME}.scene.npz"),
        format!("{NAME}.numbers.json")
    ]);
    println!("{answer}");
    Ok(())
}

// --- The bodies ---------------------------------------------------------------------------------

fn v(p: [f64; 3]) -> V3 {
    v3(p[0], p[1], p[2])
}

/// A part's printed file's fine bodies, placed: mirrored across X where asked, lifted, then turned,
/// moved and carried as the placement says, in order.
fn placed(path: &str, placement: &Placement, mirror_x: bool, lift: Option<f64>) -> Result<Vec<Solid>> {
    let turn = |mut solid: Solid, turns: &[Turn]| {
        for t in turns {
            if t.degrees != 0. {
                solid = solid.rotate(V3::ZERO, v(t.axis), t.degrees);
            }
        }
        solid
    };
    let read = hsm_kernel::import::model(path).with_context(|| format!("reading {path}"))?;
    Ok(read
        .into_iter()
        .map(|body| {
            let mut solid = body.solid;
            if mirror_x {
                solid = solid.mirror(V3::ZERO, V3::X);
            }
            if let Some(lift) = lift {
                solid = solid.translate(V3::Z * lift);
            }
            solid = turn(solid, &placement.turns);
            if placement.shift != [0.; 3] {
                solid = solid.translate(v(placement.shift));
            }
            if let Some(c) = &placement.carry {
                solid = solid.transformed(&Affine::from_columns(
                    v(c.columns[0]),
                    v(c.columns[1]),
                    v(c.columns[2]),
                    v(c.translation),
                ));
            }
            solid = turn(solid, &placement.after_turns);
            if placement.after_shift != [0.; 3] {
                solid = solid.translate(v(placement.after_shift));
            }
            solid
        })
        .collect())
}

/// A casing piece's placement, as the foam assembly stands it.
fn stack_placement(piece: &casing::Piece) -> Placement {
    Placement {
        turns: vec![Turn { axis: [0., 0., 1.], degrees: piece.turn }],
        shift: [0., 0., piece.lift],
        ..Placement::default()
    }
}

/// Every body the core places, in the order its files list them.
fn bodies() -> Result<Vec<Piece>> {
    let mut pieces = vec![];
    let mut add = |name: &str, colour: Colour, solids: Vec<Solid>| {
        let part_budget = presentation::PART_BUDGET.contains(&name);
        for fine in solids {
            pieces.push(Piece { name: name.to_owned(), colour, fine, part_budget });
        }
    };
    for c in numbers::clamps() {
        add(&c.name, catalog::donor_black(), vec![stand_ins::clamp_screw(&c)?]);
    }
    add(
        "reservoir-b-fill-guide",
        hsm_foam_cap_numbers::colour(),
        placed(numbers::B_FILL_HOLDER, &numbers::b_fill_holder(), false, None)?,
    );
    for piece in casing::pieces() {
        add(piece.name, piece.colour, placed(piece.model, &stack_placement(&piece), false, None)?);
    }
    let steel = carbonator::colour();
    add("carbonator-tube", steel, vec![stand_ins::tube()?]);
    add("endcap-bottom", steel, vec![stand_ins::plate(Plate::Bottom)?]);
    add("endcap-top", steel, vec![stand_ins::plate(Plate::Top)?]);
    add("float-rod-carb", steel, vec![stand_ins::carbonator_rod()?]);
    add("float-stop-carb-top", steel, vec![stand_ins::upper_stop()?]);
    add("carbonator-earth-screw", steel, vec![stand_ins::earth_screw()?]);
    add("carbonator-earth-lockwasher", steel, vec![stand_ins::earth_lockwasher()?]);
    let ports = carbonator::ports();
    for port in &ports {
        let (colour, solid) = match port.plate {
            Plate::Bottom => (carbonator::male_elbow_colour(), stand_ins::male_elbow(port)?),
            Plate::Top => (carbonator::street_elbow_colour(), stand_ins::street_elbow(port)?),
        };
        add(&format!("carbonator-elbow-{}", port.name), colour, vec![solid]);
    }
    for r in &numbers::RESERVOIRS {
        let name = format!("reservoir-{}", r.letter);
        add(&name, reservoir::cup_colour(), placed(r.body, &Placement::default(), false, None)?);
        let cap = Placement { shift: [0., 0., reservoir::cap_assembly_lift()], ..Placement::default() };
        add(&format!("{name}-cap"), reservoir::cap_colour(), placed(r.cap, &cap, false, None)?);
        let gasket = placed(numbers::GASKET, &Placement::default(), r.side < 0., Some(r.gasket_lift()))?;
        add(&format!("{name}-gasket"), reservoir::gasket_colour(), gasket);
    }
    for r in &numbers::RESERVOIRS {
        let grips = r.grips();
        for (port, xy, grip) in &grips {
            let solid = stand_ins::grip(grip, *xy, numbers::grip_z())?;
            add(&format!("reservoir-grip-{}-{port}", r.letter), reservoir::grip_colour(), vec![solid]);
        }
        let air = grips.iter().find(|(port, _, _)| *port == "air").context("a reservoir's air port")?.1;
        let tube = stand_ins::air_tube(air, numbers::air_tube_z())?;
        add(
            &format!("tube-reservoir-air-{}", r.letter),
            spools::colour(presentation::AIR_TUBE_SPOOL),
            vec![tube],
        );
    }
    add("evap-coil", catalog::copper(), vec![copper::wrap(numbers::COIL_PATH_CHORD)?]);
    for tail in Tail::BOTH {
        let solid = copper::tail(tail, false, numbers::COIL_PATH_CHORD)?;
        add(&format!("evap-tail-{}", tail.name()), catalog::copper(), vec![solid]);
    }
    add("water-inlet-jet-cap-nominal", steel, vec![stand_ins::jet()?]);
    for name in carbonator::COLLET_PORTS {
        let port = ports.iter().find(|p| p.name == name).context("a collet's port")?;
        add(&format!("collet-{name}"), carbonator::collet_colour(), vec![stand_ins::collet(port)?]);
    }
    let aero = catalog::asa_aero_white();
    let glass = catalog::glass();
    add("float-carb", aero, stand_ins::float_capsule(numbers::carbonator_float())?.into());
    for (i, at) in numbers::carbonator_reeds().into_iter().enumerate() {
        add(&format!("reed-carb-{}", i + 1), glass, vec![stand_ins::reed(at)?]);
    }
    for r in &numbers::RESERVOIRS {
        add(&format!("float-rod-{}", r.letter), steel, vec![stand_ins::reservoir_rod(r.rod_foot())?]);
        add(&format!("float-{}", r.letter), aero, stand_ins::float_capsule(r.float())?.into());
        for (i, at) in r.reeds().into_iter().enumerate() {
            add(&format!("reed-{}-{}", r.letter, i + 1), glass, vec![stand_ins::reed(at)?]);
        }
    }
    let epoxy = catalog::epoxy_black();
    add("probe-carbonator-ds18b20", epoxy, vec![stand_ins::to92_probe(numbers::carbonator_probe())?]);
    add("probe-coil-ds18s20", epoxy, vec![stand_ins::to92_probe(numbers::coil_probe())?]);
    let prv = ports.iter().find(|p| p.name == "prv").context("the PRV's port")?;
    add("prv-sv125", carbonator::prv_colour(), vec![stand_ins::sv125(prv)?]);
    add(
        "prv-shroud",
        hsm_prv_shroud_numbers::colour(),
        placed(numbers::PRV_SHROUD, &numbers::prv_shroud(), false, None)?,
    );
    add(
        "reed-bridge",
        hsm_reed_bridge_numbers::colour(),
        placed(numbers::REED_BRIDGE, &numbers::reed_bridge(), false, None)?,
    );
    Ok(pieces)
}

/// Every line, swept at the stock bend along its corners. The PRV's vent is cut flush with the
/// shell's flank it leaves by.
fn lines() -> Result<Vec<Piece>> {
    numbers::lines()
        .into_iter()
        .map(|line| {
            let points: Vec<V3> = line.points.iter().map(|&p| v(p)).collect();
            let mut fine = core_routes::build_route(&points, routes::bend_radius(), routes::line_radius())?;
            if line.name == "prv-vent" {
                fine = flush_with_flank(&fine)?;
            }
            let colour = spools::colour(presentation::line_spool(line.name));
            Ok(Piece { name: format!("line-{}", line.name), colour, fine, part_budget: false })
        })
        .collect()
}

/// A line cut off at the shell's +Y flank.
fn flush_with_flank(line: &Solid) -> Result<Solid> {
    let b = line.bounds();
    let flank = routes::PRV_VENT_FLANK_Y;
    let keep = Plane::XY.at(b.min - v3(1., 1., 1.)).extrude(
        &Profile::rect(
            v2((b.max.x - b.min.x + 2.) / 2., (flank - b.min.y + 1.) / 2.),
            b.max.x - b.min.x + 2.,
            flank - b.min.y + 1.,
        ),
        b.max.z - b.min.z + 2.,
    )?;
    line.intersect(&keep)
}

// --- The files ----------------------------------------------------------------------------------

/// Writes the core's STEP, payload and fine model, the drawn surfaces simplified to the viewer's
/// budget.
fn write(out: &Path, pieces: &[Piece], lines: &[Piece]) -> Result<Value> {
    let all = || pieces.iter().chain(lines);
    let mut low = v3(f64::INFINITY, f64::INFINITY, f64::INFINITY);
    let mut high = -low;
    for piece in all() {
        let b = piece.fine.bounds();
        low = v3(low.x.min(b.min.x), low.y.min(b.min.y), low.z.min(b.min.z));
        high = v3(high.x.max(b.max.x), high.y.max(b.max.y), high.z.max(b.max.z));
    }
    let ratio = hsm_print_payload::LINEAR_DEFLECTION_RATIO;
    let reduction = presentation::SIMPLIFICATION_FRACTION;
    let deflection = |size: V3| (size.x + size.y + size.z) / 3. * ratio;
    let global = deflection(high - low).max(TOLERANCE);
    let shown: Vec<Solid> = all()
        .map(|piece| {
            let tolerance = if piece.part_budget {
                let b = piece.fine.bounds();
                deflection(b.max - b.min).max(TOLERANCE)
            } else {
                global
            };
            piece.fine.simplified_to((tolerance * reduction).max(TOLERANCE))
        })
        .collect::<Result<_>>()?;
    let bodies: Vec<AssemblyBody> = all()
        .zip(&shown)
        .map(|(piece, shown)| AssemblyBody {
            name: &piece.name,
            color: Some(piece.colour.linear),
            fine: &piece.fine,
            presentation: shown,
        })
        .collect();
    let alphas: Map<String, Value> =
        all().map(|piece| (piece.name.clone(), json!(presentation::recorded_alpha(piece.colour)))).collect();
    let document =
        json!({"frame": "foam assembly source", "schema": "hsm-cold-core-model-1", "alpha_by_name": alphas});
    write_assembly(out, NAME, &bodies, Some(&document))
}

/// The printed casing pieces drawn from their own print surfaces, each with its payload and the
/// placement its fine model takes.
fn printed_surfaces() -> Result<Vec<(&'static str, &'static str, Placement)>> {
    presentation::PRINTED_SURFACES
        .iter()
        .map(|&(name, file)| {
            let placement = if name == "reservoir-b-fill-guide" {
                numbers::b_fill_holder()
            } else {
                stack_placement(
                    casing::pieces().iter().find(|p| p.name == name).context("a printed casing piece")?,
                )
            };
            Ok((name, file, placement))
        })
        .collect()
}

/// What the machine's wiring lands the carbonator's earth lead by: the body the bond is screwed
/// into, where the ring's tongue meets the rim and the way out of the wall there, where the lead
/// leaves the ring's barrel and the way it leaves, the terminal's envelope, and the top plate
/// the bond is struck off.
fn earth_datums() -> Value {
    let d = carbonator::bond();
    json!({
        "bond": {
            "body": carbonator::BOND_BODY,
            "contact_point_mm": d.contact_point,
            "contact_outward": d.contact_outward,
            "wire_exit_mm": d.wire_exit,
            "wire_outward": d.wire_outward,
            "ring_tongue_thickness_mm": carbonator::bond::RING_TONGUE_THICKNESS,
            "ring_eye_diameter_mm": carbonator::bond::RING_EYE_DIAMETER,
            "ring_barrel_diameter_mm": carbonator::bond::RING_BARREL_DIAMETER,
            "ring_barrel_length_mm": carbonator::bond::RING_BARREL_LENGTH,
        },
        "carbonator": {"top_plate_z": carbonator::TOP_PLATE_Z},
    })
}

/// `bytes` at `path`, unless the file holds them already; any other lands whole, by a rename.
fn keep(path: &Path, bytes: &[u8]) -> Result<()> {
    if std::fs::read(path).is_ok_and(|held| held == bytes) {
        return Ok(());
    }
    let file = path
        .file_name()
        .and_then(|f| f.to_str())
        .ok_or_else(|| anyhow!("no file name in {}", path.display()))?;
    let tmp = path.with_file_name(format!(".{file}.{}.{file}", std::process::id()));
    std::fs::write(&tmp, bytes).with_context(|| format!("writing {}", tmp.display()))?;
    std::fs::rename(&tmp, path).with_context(|| format!("renaming onto {}", path.display()))
}
