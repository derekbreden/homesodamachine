//! Manual fabrication guides compose their source-backed bench instructions and publish their Letter pages.
mod assembly;
pub mod cuts;
mod drill;
pub mod letter;

use anyhow::{Context, Result, ensure};
use regex::Regex;
use serde::Serialize;
use serde_json::{Value, json};
use std::path::Path;

#[derive(Serialize)]
pub struct Recipe {
    power: u32,
    hz: u32,
    sweep: u32,
    feed: u32,
    gas: u32,
    wire_suffix: String,
    tacks: u32,
}

pub struct Data {
    rod: f64,
    rod_tolerance: f64,
    reservoir_rod: f64,
    faucet: cuts::FaucetCuts,
    recipe: Recipe,
    radial: String,
    face: String,
    travel: f64,
    overlap: f64,
    pump_tube_cut: f64,
    pump_tube_held: f64,
}

impl Data {
    fn new(root: &Path) -> Result<Self> {
        let procedure = hsm_pages::reads::text(root.join("hardware/assembly/pressure-vessel.md"))?;
        let recipe = Regex::new(
            r"Recorded practice settings: power (\d+) %, wobble (\d+) Hz × (\d+) mm, wire feed (\d+) mm/s, argon (\d+) s pre/post, ER316L \.(\d+) filler, (\d+)-tack opposite-side-bisecting pattern",
        )?;
        let groups = recipe
            .captures(&procedure)
            .context("review the closure practice recipe in pressure-vessel.md")?;
        let recipe = Recipe {
            power: groups[1].parse()?,
            hz: groups[2].parse()?,
            sweep: groups[3].parse()?,
            feed: groups[4].parse()?,
            gas: groups[5].parse()?,
            wire_suffix: groups[6].into(),
            tacks: groups[7].parse()?,
        };
        ensure!(recipe.tacks == 8, "review the authored tack illustration");
        let rig = hsm_pages::reads::text(root.join("hardware/assembly/weld-rotation-rig.md"))?;
        let limit = |pattern: &str| -> Result<String> {
            Ok(Regex::new(pattern)?
                .captures(&rig)
                .context("review the rotator runout requirement")?[1]
                .into())
        };
        let radial = limit(r"radial runout at the weld end \*\*≤ ([\d.]+) mm TIR")?;
        let face = limit(r"end-cap face runout at the weld circle \*\*≤ ([\d.]+) mm TIR")?;
        ensure!(
            rig.contains("through two dry revolutions"),
            "review the rotator continuity procedure"
        );
        let spec = hsm_cold_core_data::ROD_SPEC;
        Ok(Self {
            rod: spec.finished_length * hsm_endcap_circular_numbers::INCH,
            rod_tolerance: spec.length_tolerance * hsm_endcap_circular_numbers::INCH,
            reservoir_rod: hsm_reservoir_numbers::rod_length(),
            faucet: cuts::faucet()?,
            recipe,
            radial,
            face,
            travel: hsm_weld_rotator_numbers::recipe::TRAVEL_NOMINAL,
            overlap: hsm_weld_rotator_numbers::recipe::OVERLAP_DEGREES,
            pump_tube_cut: hsm_manifold_numbers::pump_tube_cut(),
            pump_tube_held: hsm_manifold_numbers::PUMP_TUBE_HELD,
        })
    }
}

const NUMBER_SOURCES: &[&str] = &[
    "tools/hsm/fabrication-guides/src/letter.rs",
    "tools/hsm/fabrication-guides/src/lib.rs",
    "tools/hsm/fabrication-guides/src/cuts.rs",
    "hardware/cut-parts/carbonation/endcaps-circular/numbers.rs",
    "hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_drawing.rs",
    "hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.rs",
    "hardware/printed-parts/cold-core/magnetic-float/all-aero/numbers.rs",
    "hardware/printed-parts/fixtures/weld-rotator/numbers.rs",
    "tools/hsm/cold-core-data/src/lib.rs",
    "hardware/printed-parts/cold-core/reservoir/numbers.rs",
    "hardware/printed-parts/faucet/numbers/paths.rs",
    "hardware/printed-parts/faucet/numbers/shell.rs",
    "hardware/faucet-layout/numbers.rs",
    "hardware/faucet-layout/assembly/cuts.rs",
    "hardware/faucet-layout/assembly/legs.rs",
    "hardware/faucet-layout/assembly/metrics.rs",
    "hardware/manifold-layout/manifold/lib.rs",
];

fn endcap_manifest() -> Value {
    use hsm_endcap_circular_numbers as n;
    json!({"disc_diameter":n::DIAMETER_IN,"disc_thickness":n::THICKNESS_IN,"hole_diameter":n::HOLE_DIAMETER_IN,
        "hole_spacing":n::HOLE_SPACING_IN,"register_radius":n::REGISTER_RADIUS_IN,
        "register_drill_diameter":n::REGISTER_DRILL_IN,"register_depth":n::REGISTER_DEPTH_IN})
}

pub fn build(root: &Path, out: &Path, guide: &str) -> Result<Value> {
    let d = Data::new(root)?;
    let mut c = letter::Canvas::new(root)?;
    let mut sources = NUMBER_SOURCES.to_vec();
    let (publication, extra) = match guide {
        "assembly-letter" => {
            assembly::compose(&mut c, &d);
            sources.extend_from_slice(assembly::SOURCES);
            (
                letter::Publication {
                    stem: "assembly-drill-and-weld-letter",
                    directory: "hardware/assembly-letter-guide",
                    title: "Drill and weld bench sheets",
                    subtitle: "Shop guide - endcap register and closure weld, 3 pages, 8.5 x 11 in",
                    subject: "Blind register, weld setup, pedal and trigger",
                    sources: &[],
                },
                json!({"endcap_inches":endcap_manifest(),"rotator_mm":{"TUBE_OD":hsm_weld_rotator_numbers::tube::OD,
                    "TUBE_ID":hsm_weld_rotator_numbers::tube::ID,"TUBE_WALL":hsm_weld_rotator_numbers::tube::WALL,
                    "ENDCAP_RECESS":hsm_weld_rotator_numbers::recipe::ENDCAP_RECESS,"TRAVEL_NOMINAL":d.travel,"OVERLAP_DEGREES":d.overlap},
                    "practice_recipe":d.recipe,"manufacturer_source":assembly::MANUAL}),
            )
        }
        "drill-and-cut-guide" => {
            drill::compose(&mut c, &d);
            sources.extend_from_slice(drill::SOURCES);
            (
                letter::Publication {
                    stem: "drill-and-cut-guide",
                    directory: "hardware/drill-and-cut-guide",
                    title: "Drill & cut bench guide",
                    subtitle: "28 illustrated Letter pages: endcaps, rods, inlet jet, metal and fluid tubing, coverings and harness stock.",
                    subject: "Fabrication setups, cutting actions and fit checks",
                    sources: &[],
                },
                json!({"external_sources":{"WEN 4208T":drill::PRESS_MANUAL,"WEN BA4555":drill::SAW_MANUAL},
                    "external_checked":"2026-10-04","numeric_inputs":{"endcap":endcap_manifest(),
                    "carbonator_rod_finished_mm":d.rod,"carbonator_rod_tolerance_mm":d.rod_tolerance,
                    "reservoir_rod_mm":d.reservoir_rod,"faucet_cuts_mm":d.faucet,
                    "pump_tube_cut_mm":d.pump_tube_cut,"pump_tube_held_mm":d.pump_tube_held}}),
            )
        }
        _ => anyhow::bail!("unknown fabrication guide {guide}"),
    };
    letter::publish(
        root,
        out,
        &c,
        letter::Publication {
            sources: &sources,
            ..publication
        },
        extra,
    )
}
