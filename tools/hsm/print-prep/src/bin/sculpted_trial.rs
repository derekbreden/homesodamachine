//! sculpted-trial runs the Sculpted faucet trial plate's stages.
//!
//! The stages are the tip's warp, its donor supports and its courses; the base filled under its
//! mounting face, its foundation, its continued courses through the shaft and the cooling of
//! their join; the screw-seat rings; the tip, shaft, plug-ramp and short foundation sequencers; the
//! plug-ramp feed cap, the tip's end spliced from a second slice and
//! cooled as the standing path cools it, the printer's progress lines, and the print-only review
//! archive.
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
//!   sculpted-trial tape DONOR.gcode DONOR.print.json WARP.json OUT.gcode --band-step STEP [--uphill-all] --native-nose
//!   sculpted-trial fill BASE.stl OUT.stl
//!   sculpted-trial foundation SLICED.gcode.3mf PRINT.json BASE.stl HEADMAP.npz OUT_DIR [--deck-top MM] [--part-courses COUNT]
//!   sculpted-trial continued-base DONOR.gcode DONOR.print.json PHYSICAL.gcode PHYSICAL.print.json OUT.gcode
//!       [--uphill-wall-runs] [--stitch-mesh BASE.stl] [--fade-end MM] [--native-join-z MM]
//!   sculpted-trial cool-shaft-join SEQUENCED.gcode PROJECT.3mf OUT.gcode [--catalog SCALARS.json]
//!   sculpted-trial rings PRINT.json RINGS.gcode
//!   sculpted-trial sequence PRIOR.gcode NATIVE.gcode PLATE.gcode --tip-model TIP.gcode --entire-tip-custom [--plate-rings RINGS.gcode]
//!   sculpted-trial sequence-shaft FOUNDATION.gcode SEQUENCED.gcode [--donor CONTINUED-BASE.gcode]
//!   sculpted-trial sequence-foundations FOUNDATION.gcode NATIVE.gcode DONOR.gcode WARP.json RINGS.gcode OUT.gcode [--headmap HEADMAP.npz]
//!   sculpted-trial splice-tip-end LEVEL.gcode.3mf PLAIN.gcode.3mf TIP-END.json OUT_DIR STEM
//!   sculpted-trial cool-tip-end SLICE_DIR PROJECT.3mf PRINT.json
//!   sculpted-trial progress PLATE.gcode [PROGRESS.json] OUT.gcode
//!   sculpted-trial package NATIVE.gcode.3mf PLATE.gcode REVIEW.gcode.3mf [--motion-seconds S --first-course-seconds F]
//!   sculpted-trial merge PREVIOUS.gcode --candidate TIP.gcode PLATE.gcode [--candidate TIP.gcode PLATE.gcode ...]
//!   sculpted-trial cap-feed UNCAPPED.gcode CAPPED.gcode
//!   sculpted-trial bind-capped UNCAPPED.gcode CAPPED.gcode PLATE.gcode [--clamp-receipt CAPPED.json]
//!   sculpted-trial audit-tip TIP.stl WARP.json ARCHIVE.gcode.3mf OUT.json
//!   sculpted-trial head-map TOOLHEAD.step.npz OUT.npz
//!   sculpted-trial replay PLATE.gcode OUT.json [--head-map MAP.npz]
//!   sculpted-trial approaches PLATE.gcode REPLAY.json OUT.json

use anyhow::{bail, Context, Result};
use hsm_print_prep::mesh::{write_stl, Mesh};
use hsm_print_prep::{approaches, base_courses, base_foundation, feed_cap, filled_base, head_map, head_replay, plate_rings, plate_sequence, shaft_join_cooling, tip_audit, tip_courses, tip_supports, tip_warp, trial_archive};
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

    fn flag(&self, name: &str) -> bool {
        self.options.iter().any(|(k, _)| k == name)
    }

    fn count(&self, expected: usize) -> Result<()> {
        if self.positional.len() != expected {
            bail!("Expected {expected} paths, got {}", self.positional.len());
        }
        Ok(())
    }
}

fn number(args: &Args, name: &str) -> Result<f64> {
    let value = args.option(name).with_context(|| format!("{name} is required"))?;
    value.trim().parse().with_context(|| format!("{name} needs a number, not {value:?}"))
}

fn main() -> Result<()> {
    let mut values: Vec<String> = std::env::args().skip(1).collect();
    if values.is_empty() {
        bail!("usage: sculpted-trial warp|supports|tape|fill|foundation|continued-base|cool-shaft-join|rings|sequence|sequence-shaft|sequence-foundations|splice-tip-end|cool-tip-end|progress|package|merge|cap-feed|bind-capped|audit-tip|head-map|replay|approaches ...");
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
            let (paths, flags) = values.split_at(4.min(values.len()));
            let [gcode, donor, warp, output] = paths else {
                bail!("usage: sculpted-trial tape DONOR.gcode DONOR.print.json WARP.json OUT.gcode --band-step STEP [--uphill-all] --native-nose");
            };
            let (mut step, mut uphill, mut native) = (None, false, false);
            let mut rest = flags.iter();
            while let Some(flag) = rest.next() {
                match flag.as_str() {
                    "--band-step" => step = Some(rest.next().context("--band-step needs a height")?.parse::<f64>()?),
                    "--uphill-all" => uphill = true,
                    "--native-nose" => native = true,
                    other => bail!("sculpted-trial tape does not take {other}"),
                }
            }
            if !native {
                bail!("sculpted-trial tape keeps the native nose; pass --native-nose");
            }
            let banding = tip_courses::Banding { step: step.context("sculpted-trial tape needs --band-step")?, uphill };
            tip_courses::write(Path::new(gcode), Path::new(donor), Path::new(warp), Path::new(output), &banding)?;
        }
        "fill" => {
            let [base, output] = values.as_slice() else {
                bail!("usage: sculpted-trial fill BASE.stl OUT.stl");
            };
            let mesh = Mesh::read_stl(Path::new(base))?;
            let filled = filled_base::fill(&mesh, base_courses::INCLINE_DEGREES, filled_base::rim(&mesh)?)?;
            write_stl(Path::new(output), &filled.vertices, &filled.faces)?;
        }
        "foundation" => {
            let p = paths(&values, 5, &[])?;
            let deck_top = valued(&values, "--deck-top").map(|v| v.parse::<f64>()).transpose().context("--deck-top needs a number")?;
            let part_courses = valued(&values, "--part-courses").map_or(Ok(base_foundation::SHORT_FOUNDATION_COURSES), |v| v.parse::<usize>())
                .context("--part-courses needs a count")?;
            base_foundation::foundation(&base_foundation::Foundation {
                archive: &p[0], report: &p[1], stl: &p[2], headmap: &p[3], out_dir: &p[4], deck_top, part_courses: Some(part_courses),
                lift_share: hsm_print_prep::faucet_plate::lift_share(&hsm_print_prep::faucet_plate::selection(&hsm_print_prep::root())?),
            })?;
        }
        "continued-base" => {
            let p = paths(&values, 5, &["--uphill-wall-runs"])?;
            let mesh = valued(&values, "--stitch-mesh").map(PathBuf::from);
            let number = |name: &str, default: f64| -> Result<f64> {
                valued(&values, name).map_or(Ok(default), |v| v.parse().with_context(|| format!("{name} needs a number")))
            };
            base_courses::continue_base(&base_courses::ContinuedBase {
                donor_gcode: &p[0], donor_report: &p[1], physical_gcode: &p[2], physical_report: &p[3], output: &p[4],
                uphill_wall_runs: values.iter().any(|a| a == "--uphill-wall-runs"),
                stitch_mesh: mesh.as_deref(),
                fade_end: number("--fade-end", base_courses::FADE_END)?,
                native_join_z: number("--native-join-z", base_courses::NATIVE_JOIN_Z)?,
            })?;
        }
        "cool-shaft-join" => {
            let p = paths(&values, 3, &[])?;
            let catalog = valued(&values, "--catalog").map(PathBuf::from)
                .unwrap_or_else(|| hsm_print_prep::root().join(shaft_join_cooling::CATALOG));
            shaft_join_cooling::cool_shaft_join(&p[0], &p[1], &p[2], &catalog)?;
        }
        "rings" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(2)?;
            let report: serde_json::Value = serde_json::from_slice(&std::fs::read(args.path(0)?)?)?;
            std::fs::write(args.path(1)?, plate_rings::gcode(&plate_rings::seats(&report)?))?;
        }
        "sequence" => {
            let args = Args::parse(values, &["--entire-tip-custom"], &["--tip-model", "--plate-rings"])?;
            args.count(3)?;
            if !args.flag("--entire-tip-custom") {
                bail!("This port composes the complete custom tip; pass --entire-tip-custom");
            }
            let tip = args.option("--tip-model").context("A complete tip replacement needs a custom model tape")?;
            let rings = args.option("--plate-rings").map(PathBuf::from);
            let report = plate_sequence::compose_tip(&args.path(0)?, &args.path(1)?, &args.path(2)?, &PathBuf::from(tip), rings.as_deref())?;
            println!("{}", serde_json::to_string_pretty(&plate_sequence::summary(&report))?);
        }
        "sequence-shaft" => {
            let args = Args::parse(values, &[], &["--donor"])?;
            args.count(2)?;
            let donor = args.option("--donor").map(PathBuf::from);
            let report = plate_sequence::compose_shaft(&args.path(0)?, &args.path(1)?, donor.as_deref())?;
            println!("{}", serde_json::to_string_pretty(&plate_sequence::summary(&report))?);
        }
        "sequence-foundations" => {
            let args = Args::parse(values, &[], &["--headmap"])?;
            args.count(6)?;
            let headmap = args.option("--headmap").map_or_else(|| hsm_print_prep::root().join(hsm_print_prep::base_foundation::HEAD_MAP), PathBuf::from);
            let report = plate_sequence::foundation_sequence::compose(
                &args.path(0)?, &args.path(1)?, &args.path(2)?, &args.path(3)?, &args.path(5)?, &args.path(4)?, &headmap,
            )?;
            println!("{}", serde_json::to_string_pretty(&plate_sequence::summary(&report))?);
        }
        "splice-tip-end" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(5)?;
            let stem = args.positional[4].clone();
            let receipt = trial_archive::splice_tip_end(&args.path(0)?, &args.path(1)?, &args.path(2)?, &args.path(3)?, &stem)?;
            println!("{}", serde_json::to_string_pretty(&receipt)?);
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
            let (plate, earlier, output) = match args.positional.len() {
                2 => (args.path(0)?, None, args.path(1)?),
                _ => { args.count(3)?; (args.path(0)?, Some(args.path(1)?), args.path(2)?) }
            };
            println!("{}", serde_json::to_string(&trial_archive::progress(&plate, earlier.as_deref(), &output)?)?);
        }
        "package" => {
            let args = Args::parse(values, &[], &["--motion-seconds", "--first-course-seconds"])?;
            args.count(3)?;
            let (seconds, first) = match (args.option("--motion-seconds"), args.option("--first-course-seconds")) {
                (None, None) => {
                    let timing = hsm_print_prep::motion::timing(&std::fs::read_to_string(args.path(1)?)?)?;
                    (timing.seconds, timing.first_course_seconds)
                }
                _ => (number(&args, "--motion-seconds")?, number(&args, "--first-course-seconds")?),
            };
            let summary = trial_archive::package(&args.path(0)?, &args.path(1)?, &args.path(2)?, seconds, first)?;
            println!("{}", serde_json::to_string(&summary)?);
        }
        "merge" => {
            let reference = values.first().map(PathBuf::from).context("Missing the previous plate")?;
            let mut candidates = Vec::new();
            let mut rest = values[1..].iter();
            while let Some(option) = rest.next() {
                match option.as_str() {
                    "--candidate" => {
                        let tip = rest.next().context("--candidate needs a tip tape and a plate")?;
                        let plate = rest.next().context("--candidate needs a tip tape and a plate")?;
                        candidates.push((PathBuf::from(tip), PathBuf::from(plate)));
                    }
                    _ => bail!("Unknown argument {option}"),
                }
            }
            if candidates.is_empty() {
                bail!("--candidate is required");
            }
            for summary in plate_sequence::merge(&reference, &candidates)? {
                println!("{}", serde_json::to_string(&summary)?);
            }
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
            let args = Args::parse(values, &[], &["--head-map"])?;
            args.count(2)?;
            let map = args.option("--head-map").map_or_else(|| hsm_print_prep::root().join(head_map::FULL_HEAD_MAP), PathBuf::from);
            std::fs::write(args.path(1)?, head_replay::replay(&args.path(0)?, &map)?)?;
        }
        "approaches" => {
            let args = Args::parse(values, &[], &[])?;
            args.count(3)?;
            let readings = approaches::read(&args.path(0)?, &args.path(1)?)?;
            std::fs::write(args.path(2)?, serde_json::to_string_pretty(&readings)? + "\n")?;
        }
        _ => bail!("Unknown command {command}; use warp, supports, tape, fill, foundation, continued-base, cool-shaft-join, rings, sequence, sequence-shaft, sequence-foundations, splice-tip-end, cool-tip-end, progress, package, merge, cap-feed, bind-capped, audit-tip, head-map, replay or approaches"),
    }
    Ok(())
}

/// The value after option `name`, if given.
fn valued(args: &[String], name: &str) -> Option<String> {
    args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned()
}

/// The first `count` paths among `args`, skipping each option and its value; `flags` take none.
fn paths(args: &[String], count: usize, flags: &[&str]) -> Result<Vec<PathBuf>> {
    let mut out = Vec::new();
    let mut i = 0;
    while i < args.len() && out.len() < count {
        if args[i].starts_with("--") {
            i += if flags.contains(&args[i].as_str()) { 1 } else { 2 };
            continue;
        }
        out.push(PathBuf::from(&args[i]));
        i += 1;
    }
    if out.len() < count {
        bail!("expected {count} paths");
    }
    Ok(out)
}
