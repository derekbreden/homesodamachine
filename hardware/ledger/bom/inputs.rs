//! What the BOM's hardware is counted from: the installed machine's facts and the above-core
//! layout, the manifold's, the AC harness's, the cold core's, the faucet's and the enclosure's
//! numbers, the compressor's reference, and the hardware written down beside them.
use crate::hardware as bought;
use anyhow::{Context as _, Result};
use hsm_coil_numbers as coil;
use hsm_cold_core_interface as core;
use hsm_enclosure_numbers::{rear_wall::c14, shell::FLUTE_DEPTH};
use hsm_foam_cap_numbers::deck;
use hsm_ledger::bom_sync::{C14, Coil, Compressor, Deck, Faucet, Inputs, Manifold, Relay, Wire};
use hsm_manifold_numbers as manifold;
use serde::Deserialize;
use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
use std::path::Path;

/// The installed machine's facts: what it places, the box's fittings and every run's length.
const FACTS: &str = "hardware/manifold-layout/enclosure-assembly.facts.json";
/// The above-core layout: its parts and the fittings it stands.
const ABOVE_CORE: &str = "hardware/manifold-layout/above-core.json";
/// The compressor's own dimensions.
const COMPRESSOR: &str = "hardware/reference/compressor/reference-parameters.json";

/// A JSON file of the tree, read whole and named to the build as read.
fn read<T: for<'de> Deserialize<'de>>(root: &Path, relative: &str) -> Result<T> {
    let path = root.join(relative);
    let bytes = std::fs::read(&path).with_context(|| format!("reading {}", path.display()))?;
    hsm_kernel::reads::read(&path, &bytes);
    serde_json::from_slice(&bytes).with_context(|| format!("parsing {}", path.display()))
}

/// The installed machine's facts, as far as the BOM counts them.
#[derive(Deserialize)]
struct Facts {
    bodies: BTreeMap<String, Value>,
    pack: Pack,
    #[serde(rename = "box")]
    enclosure: Enclosure,
    runs: Vec<Run>,
    constants: Constants,
}
#[derive(Deserialize)]
struct Pack {
    placed: BTreeSet<String>,
}
/// The box: its compressor bosses, its condenser mount (stand-off, band, and the screws it
/// takes), its collet plate, and its outer bounds.
#[derive(Deserialize)]
struct Enclosure {
    floor_bosses: Vec<Value>,
    cond_mount: (f64, f64, f64, Vec<Value>),
    collet_plate: ColletPlate,
    outer: [f64; 6],
}
#[derive(Deserialize)]
struct ColletPlate {
    holes: Vec<Value>,
}
#[derive(Deserialize)]
struct Run {
    id: String,
    length: Option<f64>,
}
#[derive(Deserialize)]
#[allow(non_snake_case)]
struct Constants {
    FLOOR_GROMMET_SQUEEZE: f64,
}

/// The above-core layout's parts, where each stands, and the fittings it stands.
#[derive(Deserialize)]
struct AboveCore {
    parts: BTreeMap<String, Part>,
    snapshots: Value,
}
#[derive(Deserialize)]
struct Part {
    translation_mm: [f64; 3],
}

/// The compressor's bolt bore.
#[derive(Deserialize)]
struct CompressorReference {
    mount_d_mm: f64,
}

/// The manifold's solenoids, tees, lower returns and pump tubes.
fn manifold() -> Manifold {
    Manifold {
        solenoids: manifold::stations().filter(|(name, _, _)| name.starts_with("V-")).count(),
        purchased_tees: manifold::purchased_tees().count(),
        lower_returns: manifold::lower_returns().count(),
        pump_tube_cut: manifold::pump_tube_cut(),
    }
}

/// The AC harness's 16 AWG cuts.
fn wire() -> Wire {
    use hsm_ac_harness_numbers as ac;
    Wire { mid: ac::MID, short_2: ac::SHORT_2, short: ac::SHORT, dc1: ac::DC1, dc2: ac::DC2, opening_join: ac::OPENING_JOIN }
}

/// The evaporator coil's copper, its tails' stubs and the roll it is cut from.
fn coil() -> Coil {
    Coil {
        pitch: coil::PITCH,
        wrap: coil::wrap_length(),
        cut: coil::cut_length(),
        spare_ft: coil::roll_spare_ft(),
        stubs: [coil::stub_allowance(coil::Tail::Inlet), coil::stub_allowance(coil::Tail::Outlet)],
        per_roll: coil::CARBONATORS_PER_ROLL,
    }
}

/// The PRV vent's tube along its centreline: its legs, less what each corner's bend cuts off
/// them, and the bends.
fn prv_vent() -> f64 {
    use hsm_cold_core_layout::routes;
    let (points, radius) = (routes::prv_vent(), routes::bend_radius());
    let sub = |a: [f64; 3], b: [f64; 3]| [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    let norm = |v: [f64; 3]| (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt();
    let legs: f64 = points.windows(2).map(|pair| norm(sub(pair[1], pair[0]))).sum();
    let bends: f64 = points
        .windows(3)
        .map(|corner| {
            let (a, b) = (sub(corner[1], corner[0]), sub(corner[2], corner[1]));
            let cos = (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]) / (norm(a) * norm(b));
            let turn = cos.clamp(-1., 1.).acos();
            radius * turn - 2. * radius * (turn / 2.).tan()
        })
        .sum();
    legs + bends
}

/// The faucet's flavor and soda tube cuts, as the bench cuts them off the assembly's centrelines.
fn faucet() -> Result<Faucet> {
    use hsm_faucet_assembly::cuts;
    Ok(Faucet { flavor_cut: cuts::flavor()?, soda_cut: cuts::soda_faucet()? })
}

/// A relay board's wall screws: back-top's insert faces and pilots, and the wall left behind a
/// pilot at the box's west flank, plain and under its flutes.
fn relay(above: &AboveCore, west: f64) -> Result<Relay> {
    use bought::*;
    use hsm_enclosure_numbers::rear_wall::hosts::{PILOT_DEPTH, RELAY_SETBACK};
    let x = ["relay-1", "relay-2"]
        .iter()
        .map(|name| Ok(above.parts.get(*name).with_context(|| format!("the above-core layout places no {name}"))?.translation_mm[0]))
        .collect::<Result<Vec<f64>>>()?
        .into_iter()
        .fold(f64::INFINITY, f64::min);
    let backing = x - RELAY_SETBACK - PILOT_DEPTH - west;
    Ok(Relay {
        screws: RELAY_SCREWS,
        board: RELAY_BOARD,
        setback: RELAY_SETBACK,
        insert: SHORT_INSERT,
        reach: RELAY_SCREW_LENGTH - RELAY_BOARD - RELAY_SETBACK,
        bore: PILOT_DEPTH,
        backing,
        fluted_backing: backing - FLUTE_DEPTH,
    })
}

pub fn inputs(root: &Path) -> Result<Inputs> {
    let facts: Facts = read(root, FACTS)?;
    let above: AboveCore = read(root, ABOVE_CORE)?;
    let compressor: CompressorReference = read(root, COMPRESSOR)?;
    let placed = facts.pack.placed;
    let relays = above.parts.keys().filter(|name| name.starts_with("relay-") && placed.contains(*name)).count();
    Ok(Inputs {
        relays,
        placed,
        bodies: facts.bodies.into_keys().collect(),
        run_lengths: facts.runs.into_iter().filter_map(|r| Some((r.id, r.length?))).collect(),
        floor_bosses: facts.enclosure.floor_bosses.len(),
        condenser_screws: facts.enclosure.cond_mount.3.len(),
        dock_tees: facts.enclosure.collet_plate.holes.len(),
        floor_grommet_squeeze: facts.constants.FLOOR_GROMMET_SQUEEZE,
        manifold: manifold(),
        wire: wire(),
        coil: coil(),
        prv_vent: prv_vent(),
        faucet: faucet()?,
        reservoir_a_ties: bought::RESERVOIR_A_TIES,
        cap_tie_paths: bought::CAP_TIE_PATHS,
        foam_cap_face_inserts: core::attachment_stations().len(),
        reservoir_cap_inserts: hsm_reservoir_numbers::stations().len(),
        reeds_per_reservoir: core::REEDS_PER_RESERVOIR,
        deck: Deck { screws: deck::hole_xy().len(), board: deck::BOARD_THICKNESS, reach: deck::reach(), bore: deck::bore_depth() },
        touchflo_inserts: hsm_faucet_numbers::shell::BASE_POD_CENTERS.len(),
        union_elbows: hsm_layout_data::union_elbow_names(&above.snapshots).len(),
        stem_elbows: hsm_layout_data::stem_elbow_names(&above.snapshots).len(),
        psu_screws: bought::PSU_SCREWS,
        relay: relay(&above, facts.enclosure.outer[0])?,
        c14: C14 {
            screws: bought::C14_SCREWS,
            flange: c14::FLANGE_T,
            bore: c14::PILOT_DEPTH,
            reach: bought::C14_SCREW_LENGTH - c14::FLANGE_T - c14::RIM_PROUD - bought::C14_WASHER,
        },
        seam_rods: bought::SEAM_RODS,
        funnel_screws: bought::FUNNEL_SCREWS,
        compressor: Compressor {
            bore: compressor.mount_d_mm,
            ligament: bought::COMPRESSOR_HOLE_INSET - compressor.mount_d_mm / 2.0,
        },
    })
}
