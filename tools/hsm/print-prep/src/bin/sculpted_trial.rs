//! sculpted-trial runs the Sculpted faucet trial plate's stages.
//!
//! The stages are the product plate's, one at a time: the tip's warp, its donor supports and its
//! courses; the base filled under its mounting face and its foundation; the screw-seat rings; the
//! foundation sequencer; the plug ramp's feed cap; the tip's end cooled as the standing path cools
//! it; the printer's progress lines and the print-only review archive.
//!
//! The checks of a finished plate run by hand, each when someone asks its question. `audit-tip`
//! measures the tip's courses, support contacts and clear waterways against the tip's mesh.
//! `head-map` folds the whole toolhead model into the left-active head's height map. `replay`
//! plays the plate's moves against the material laid before each one, with the modeled toolhead
//! over them. `approaches` reads the head replay's dry nozzle approaches again at their exact
//! positions over the earlier beads.
//!
//!   sculpted-trial warp matched-shoulder|short-shoulder TIP.stl EDITABLE.3mf OUT.stl
//!   sculpted-trial supports WARP.json OUT.json
//!   sculpted-trial tape DONOR.gcode DONOR.print.json WARP.json OUT.gcode
//!   sculpted-trial fill BASE.stl OUT.stl
//!   sculpted-trial foundation SLICED.gcode.3mf PRINT.json BASE.stl HEADMAP.npz OUT_DIR
//!   sculpted-trial rings PRINT.json RINGS.gcode
//!   sculpted-trial sequence-foundations FOUNDATION.gcode NATIVE.gcode DONOR.gcode WARP.json RINGS.gcode OUT.gcode
//!   sculpted-trial cool-tip-end SLICE_DIR PROJECT.3mf PRINT.json
//!   sculpted-trial progress PLATE.gcode OUT.gcode
//!   sculpted-trial package NATIVE.gcode.3mf PLATE.gcode REVIEW.gcode.3mf
//!   sculpted-trial cap-feed UNCAPPED.gcode CAPPED.gcode
//!   sculpted-trial bind-capped UNCAPPED.gcode CAPPED.gcode PLATE.gcode [--clamp-receipt CAPPED.json]
//!   sculpted-trial audit-tip TIP.stl WARP.json ARCHIVE.gcode.3mf OUT.json
//!   sculpted-trial head-map TOOLHEAD.step.npz OUT.npz
//!   sculpted-trial replay PLATE.gcode OUT.json
//!   sculpted-trial approaches PLATE.gcode REPLAY.json OUT.json

use anyhow::{bail, Context, Result};
use hsm_print_prep::mesh::{write_stl, Mesh};
use hsm_print_prep::{approaches, base_foundation, feed_cap, filled_base, head_map, head_replay, plate_rings, plate_sequence, tip_audit, tip_courses, tip_supports, tip_warp, trial_archive};
use std::path::{Path, PathBuf};

struct Args {
    positional: Vec<String>,
    options: Vec<(String, Option<String>)>,
}

impl Args {
    fn parse(values: Vec<String>, flags: &[&str], valued: &[&str]) -> Result<Args> {
        let (mut positional, mut options) = (Vec::new(), Vec::new());
        let mut values = values.into_iter();
        while let Some(value) = values.next() {
            if flags.contains(&value.as_str()) {
                options.push((value, None));
            } else if valued.contains(&value.as_str()) {
                let given = values.next().with_context(|| format!("{value} needs a value"))?;
                options.push((value, Some(given)));
            } else if value.starts_with("--") {
                bail!("Unknown option {value}");
            } else {
                positional.push(value);
            }
        }
        Ok(Args { positional, options })
    }

    fn path(&self, index: usize) -> Result<PathBuf> {
        self.positional.get(index).map(PathBuf::from).with_context(|| format!("Missing argument {}", index + 1))
    }

    fn option(&self, name: &str) -> Option<&str> {
        self.options.iter().rev().find(|(k, _)| k == name).and_then(|(_, v)| v.as_deref())
    }

    fn count(&self, expected: usize) -> Result<()> {
        if self.positional.len() != expected {
            bail!("Expected {expected} paths, got {}", self.positional.len());
        }
        Ok(())
    }
}

fn main() -> Result<()> {
    let mut values: Vec<String> = std::env::args().skip(1).collect();
    if values.is_empty() {
        bail!("usage: sculpted-trial warp|supports|tape|fill|foundation|rings|sequence-foundations|cool-tip-end|progress|package|cap-feed|bind-capped|audit-tip|head-map|replay|approaches ...");
    }
    let command = values.remove(0);
    match command.as_str() {
        "warp" => {
            let [recipe, mesh, project, output] = values.as_slice() else {
                bail!("usage: sculpted-trial warp matched-shoulder|short-shoulder TIP.stl EDITABLE.3mf OUT.stl");
            };
            let recipe = match recipe.as_str() {
                "matched-shoulder" => &tip_warp::MATCHED_SHOULDER,
                "short-shoulder" => &tip_warp::SHORT_SHOULDER,
                other => bail!("unknown tip warp {other}"),
            };
            tip_warp::write(recipe, Path::new(mesh), Path::new(project), Path::new(output))?;
        }
        "supports" => {
            let [warp, output] = values.as_slice() else {
                bail!("usage: sculpted-trial supports WARP.json OUT.json");
            };
            tip_supports::write(Path::new(warp), Path::new(output))?;
        }
        "tape" => {
            let [gcode, donor, warp, output] = values.as_slice() else {
                bail!("usage: sculpted-trial tape DONOR.gcode DONOR.print.json WARP.json OUT.gcode");
            };
            tip_courses::write(Path::new(gcode), Path::new(donor), Path::new(warp), Path::new(output))?;
        }
        "fill" => {
            let [base, output] = values.as_slice() else {
                bail!("usage: sculpted-trial fill BASE.stl OUT.stl");
            };
            let mesh = Mesh::read_stl(Path::new(base))?;
            let filled = filled_base::fill(&mesh, filled_base::INCLINE_DEGREES, filled_base::rim(&mesh)?)?;
            write_stl(Path::new(output), &filled.vertices, &filled.faces)?;
        }
        "foundation" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(5)?;
            base_foundation::foundation(&base_foundation::Foundation {
                archive: &args.path(0)?, report: &args.path(1)?, stl: &args.path(2)?, headmap: &args.path(3)?, out_dir: &args.path(4)?,
                lift_share: hsm_print_prep::faucet_plate::lift_share(&hsm_print_prep::faucet_plate::selection(&hsm_print_prep::root())?),
            })?;
        }
        "rings" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(2)?;
            let report: serde_json::Value = serde_json::from_slice(&std::fs::read(args.path(0)?)?)?;
            std::fs::write(args.path(1)?, plate_rings::gcode(&plate_rings::seats(&report)?))?;
        }
        "sequence-foundations" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(6)?;
            let root = hsm_print_prep::root();
            let headmap = root.join(hsm_print_prep::base_foundation::HEAD_MAP);
            let tip = root.join(hsm_print_prep::faucet_plate::TIP.stl);
            let report = plate_sequence::foundation_sequence::compose(
                &args.path(0)?, &args.path(1)?, &args.path(2)?, &args.path(3)?, &args.path(5)?, &args.path(4)?, &headmap, &tip,
            )?;
            println!("{}", serde_json::to_string_pretty(&plate_sequence::summary(&report))?);
        }
        "cool-tip-end" => {
            // the standing slice path's last G-code stage, on a slice made outside it
            let args = Args::parse(values, &[], &[])?;
            args.count(3)?;
            let directory = args.path(0)?;
            let report: serde_json::Value = serde_json::from_slice(&std::fs::read(args.path(2)?)?)?;
            let cooling = &hsm_print_prep::faucet_plate::selection(&hsm_print_prep::root())?["tip_end_cooling"];
            let stretch = hsm_print_prep::faucet_contact::recorded_tip_end_stretch(&report, cooling)?;
            std::fs::create_dir_all(directory.join("mapped-slice"))?;
            let reading = hsm_print_prep::faucet_contact::apply_stretch_cooling(&args.path(1)?, &directory, "tip-end-cooling", &stretch)?;
            println!("{}", serde_json::to_string_pretty(&reading)?);
        }
        "progress" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(2)?;
            println!("{}", serde_json::to_string(&trial_archive::progress(&args.path(0)?, &args.path(1)?)?)?);
        }
        "package" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(3)?;
            let timing = hsm_print_prep::motion::timing(&std::fs::read_to_string(args.path(1)?)?)?;
            let summary = trial_archive::package(&args.path(0)?, &args.path(1)?, &args.path(2)?, timing.seconds, timing.first_course_seconds)?;
            println!("{}", serde_json::to_string(&summary)?);
        }
        "cap-feed" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(2)?;
            feed_cap::cap(&args.path(0)?, &args.path(1)?)?;
        }
        "bind-capped" => {
            let args = Args::parse(values, &[], &["--clamp-receipt"])?;
            args.count(3)?;
            let receipt = args.option("--clamp-receipt").map(PathBuf::from);
            println!("{}", feed_cap::bind(&args.path(0)?, &args.path(1)?, &args.path(2)?, receipt.as_deref())?);
        }
        "audit-tip" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(4)?;
            let report = tip_audit::audit(&args.path(0)?, &args.path(1)?, &args.path(2)?)?;
            std::fs::write(args.path(3)?, serde_json::to_string_pretty(&report)? + "\n")?;
        }
        "head-map" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(2)?;
            let mut map = head_map::HeadMap::read(&hsm_print_prep::root().join(hsm_print_prep::base_foundation::HEAD_MAP))?;
            map.fold(&args.path(0)?)?;
            map.write(&args.path(1)?)?;
        }
        "replay" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(2)?;
            let map = hsm_print_prep::root().join(head_map::FULL_HEAD_MAP);
            std::fs::write(args.path(1)?, head_replay::replay(&args.path(0)?, &map)?)?;
        }
        "approaches" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(3)?;
            let readings = approaches::read(&args.path(0)?, &args.path(1)?)?;
            std::fs::write(args.path(2)?, serde_json::to_string_pretty(&readings)? + "\n")?;
        }
        _ => bail!("Unknown command {command}; use warp, supports, tape, fill, foundation, rings, sequence-foundations, cool-tip-end, progress, package, cap-feed, bind-capped, audit-tip, head-map, replay or approaches"),
    }
    Ok(())
}
