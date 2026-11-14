//! sculpted-trial runs the Sculpted faucet trial plate's stages.
//!
//! The stages are the tip's warp, its donor supports and its courses; the base's continued courses
//! through the shaft and the cooling of their join; the screw-seat rings; the tip-trial,
//! shaft-trial and plug-ramp sequencers; the plug-ramp feed cap; and the print-only review archive.
//!
//!   sculpted-trial warp tip-shoulder|plug-ramp TIP.stl EDITABLE.3mf OUT.stl
//!   sculpted-trial supports WARP.json OUT.json
//!   sculpted-trial tape DONOR.gcode DONOR.print.json WARP.json OUT.gcode --band-step STEP [--uphill-all] --native-nose
//!   sculpted-trial continued-base DONOR.gcode DONOR.print.json PHYSICAL.gcode PHYSICAL.print.json OUT.gcode
//!       [--uphill-wall-runs] [--stitch-mesh BASE.stl] [--fade-end MM] [--native-join-z MM]
//!   sculpted-trial cool-shaft-join SEQUENCED.gcode PROJECT.3mf OUT.gcode [--catalog SCALARS.json]
//!   sculpted-trial rings RINGS.gcode
//!   sculpted-trial sequence PRIOR.gcode NATIVE.gcode PLATE.gcode --tip-model TIP.gcode --entire-tip-custom [--plate-rings RINGS.gcode]
//!   sculpted-trial sequence-shaft FOUNDATION.gcode SEQUENCED.gcode [--donor CONTINUED-BASE.gcode]
//!   sculpted-trial package NATIVE.gcode.3mf PLATE.gcode REVIEW.gcode.3mf --motion-seconds S --first-course-seconds F
//!   sculpted-trial merge PREVIOUS.gcode --candidate TIP.gcode PLATE.gcode [--candidate TIP.gcode PLATE.gcode ...]
//!       [--reference-sha256 SHA] [--rings COUNT] [--sequencer-sha256 SHA]
//!   sculpted-trial cap-feed UNCAPPED.gcode CAPPED.gcode
//!   sculpted-trial bind-capped UNCAPPED.gcode CAPPED.gcode PLATE.gcode [--clamp-receipt CAPPED.json]

use hsm_print_prep::{base_courses, feed_cap, plate_rings, plate_sequence, python_text, shaft_join_cooling, tip_courses, tip_supports, tip_warp, trial_archive};
use std::path::Path;
use anyhow::{bail, Context, Result};
use std::path::PathBuf;

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
    python_text::float(args.option(name).with_context(|| format!("{name} is required"))?)
}

fn main() -> Result<()> {
    let mut values: Vec<String> = std::env::args().skip(1).collect();
    if values.is_empty() {
        bail!("usage: sculpted-trial warp|supports|tape|continued-base|cool-shaft-join|rings|sequence|sequence-shaft|package|merge|cap-feed|bind-capped ...");
    }
    let command = values.remove(0);
    match command.as_str() {
        "warp" => {
            let [recipe, mesh, project, output] = values.as_slice() else {
                bail!("usage: sculpted-trial warp tip-shoulder|plug-ramp TIP.stl EDITABLE.3mf OUT.stl");
            };
            let recipe = match recipe.as_str() {
                "tip-shoulder" => &tip_warp::TIP_SHOULDER,
                "plug-ramp" => &tip_warp::PLUG_RAMP,
                other => bail!("sculpted-trial knows the tip-shoulder and plug-ramp warps, not {other}"),
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
            args.count(1)?;
            std::fs::write(args.path(0)?, plate_rings::gcode())?;
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
            println!("{}", plate_sequence::summary(&report).dumps_indented());
        }
        "sequence-shaft" => {
            let args = Args::parse(values, &[], &["--donor"])?;
            args.count(2)?;
            let donor = args.option("--donor").map(PathBuf::from);
            let report = plate_sequence::compose_shaft(&args.path(0)?, &args.path(1)?, donor.as_deref())?;
            println!("{}", plate_sequence::summary(&report).dumps_indented());
        }
        "package" => {
            let args = Args::parse(values, &[], &["--motion-seconds", "--first-course-seconds"])?;
            args.count(3)?;
            let summary = trial_archive::package(&args.path(0)?, &args.path(1)?, &args.path(2)?,
                                                 number(&args, "--motion-seconds")?, number(&args, "--first-course-seconds")?)?;
            println!("{}", summary.dumps());
        }
        "merge" => {
            let reference = values.first().map(PathBuf::from).context("Missing the previous plate")?;
            let mut candidates = Vec::new();
            let mut pins = plate_sequence::MergePins::default();
            let mut rest = values[1..].iter();
            while let Some(option) = rest.next() {
                match option.as_str() {
                    "--candidate" => {
                        let tip = rest.next().context("--candidate needs a tip tape and a plate")?;
                        let plate = rest.next().context("--candidate needs a tip tape and a plate")?;
                        candidates.push((PathBuf::from(tip), PathBuf::from(plate)));
                    }
                    "--reference-sha256" => pins.reference_sha256 = Some(rest.next().context("--reference-sha256 needs a hash")?.clone()),
                    "--rings" => pins.rings = Some(rest.next().context("--rings needs a count")?.parse()?),
                    "--sequencer-sha256" => pins.sequencer_sha256 = Some(rest.next().context("--sequencer-sha256 needs a hash")?.clone()),
                    _ => bail!("Unknown argument {option}"),
                }
            }
            if candidates.is_empty() {
                bail!("--candidate is required");
            }
            for summary in plate_sequence::merge(&reference, &candidates, &pins)? {
                println!("{}", summary.dumps());
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
        _ => bail!("Unknown command {command}; use rings, sequence, sequence-shaft, package, merge, cap-feed or bind-capped"),
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
