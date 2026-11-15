//! sculpted-plate prepares the Sculpted faucet plate from the checkout's meshes, the standing
//! finish selection and the plate's own selections, through to its print-only archive.
//!
//!     sculpted-plate OUT_DIR [--printer Mark1|Mark2] [--filament-colour '#RRGGBB']
//!
//! It runs the preparer and `sculpted-dispense-face`: the ones built beside it, or the installed
//! commands of those names. The three programs are built and installed together from the checkout,
//! and the plate is prepared from inside the checkout:
//!
//!     tools/run -- "$(rustup which cargo)" build --release --locked --offline -j 2 \
//!       --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep -p hsm-faucet-display-cover \
//!       --bin sculpted-plate --bin sculpted-faucet-print-project --bin sculpted-dispense-face
//!     hsm-run --install-tools "$PWD" tools/hsm/target/release/sculpted-plate \
//!       tools/hsm/target/release/sculpted-faucet-print-project tools/hsm/target/release/sculpted-dispense-face
//!     tools/run -- sculpted-plate OUT_DIR
//!
//! OUT_DIR is the run's own folder and must not exist. The plate's tip and cover carry the
//! selections' dispense-face seam; the base is filled under its mounting face for the slice and
//! laid on its sloped foundation from its own mesh. The tip's mating courses come from a warped
//! donor tip, sliced alone and laid back onto the real shoulder. The archive and every stage's
//! receipt are written in OUT_DIR. Nothing is sent to a printer.

use anyhow::{Context, Result, bail, ensure};
use hsm_faucet_numbers::shell::{FOOT_DEPTH, FOOT_WIDTH};
use hsm_print_prep::mesh::{Mesh, write_stl};
use hsm_print_prep::{base_courses, base_foundation, faucet_underside, feed_cap, filled_base, motion, plate_rings,
    plate_sequence, sculpted_plate, tip_courses, tip_supports, tip_warp, trial_archive};
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const BASE: &str = "hardware/printed-parts/faucet/faucet-shell/faucet-shell-base.stl";
const ARCHIVE: &str = "sculpted-faucet-plate.gcode.3mf";

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let out = PathBuf::from(args.next().context("usage: sculpted-plate OUT_DIR [--printer Mark1|Mark2] [--filament-colour '#RRGGBB']")?);
    let (mut printer, mut colour) = ("Mark2".to_string(), "#161616".to_string());
    while let Some(arg) = args.next() {
        let value = args.next().with_context(|| format!("{arg} needs a value"))?;
        match arg.as_str() {
            "--printer" => printer = value,
            "--filament-colour" => colour = value,
            _ => bail!("unknown argument {arg}"),
        }
    }
    ensure!(!out.exists(), "{} already exists; give the run a new folder", out.display());
    fs::create_dir_all(&out)?;
    let out = out.canonicalize()?;
    let root = hsm_print_prep::root();
    let plate = sculpted_plate::selection(&root)?;
    // the programs it runs: the ones built beside it, or the installed commands of their names
    let programs = std::env::current_exe()?.parent().context("the programs' folder")?.to_path_buf();
    let program = |name: &str| {
        let beside = programs.join(name);
        if beside.is_file() { beside } else { PathBuf::from(name) }
    };
    let rotation = sculpted_plate::TIP_ROTATION_DEGREES.to_string();
    let prepare = |project: &Path, extra: &[&str]| -> Result<()> {
        let mut command = Command::new(program("sculpted-faucet-print-project"));
        command.arg(project).args(["--printer", &printer, "--filament-colour", &colour, "--tip-rotation", &rotation]).args(extra);
        run(command.current_dir(&root))
    };

    // the tip and cover, with the plate's dispense-face seam when its selections name one
    let heads = if plate.get("dispense_face_seam").is_some() {
        let dir = out.join("meshes");
        run(Command::new(program("sculpted-dispense-face")).arg(&dir).current_dir(&root))?;
        Some((dir.join("tip.stl"), dir.join("cover.stl")))
    } else {
        None
    };
    let tip = heads.as_ref().map_or_else(|| root.join("hardware/printed-parts/faucet/faucet-shell/faucet-shell-tip.stl"), |h| h.0.clone());
    let head_args: Vec<String> = heads.iter().flat_map(|(t, c)| ["--tip-mesh".into(), path(t), "--cover-mesh".into(), path(c)]).collect();
    let head_args: Vec<&str> = head_args.iter().map(String::as_str).collect();

    // the finish selection the plate's projects take: the standing one, with the plate's shallow
    // overhang points when its selections name them
    let finish = out.join("finish.json");
    let mut selection: Value = serde_json::from_slice(&fs::read(root.join(plate["finish_selection"].as_str().context("the standing finish selection")?))?)?;
    if let Some(entry) = plate.get("shallow_overhang_wall_speed") {
        selection["shallow_overhang_wall_speed"] = entry.clone();
    }
    fs::write(&finish, serde_json::to_string_pretty(&selection)? + "\n")?;
    let finish_args = ["--finish".to_string(), path(&finish)];
    let finish_args: Vec<&str> = finish_args.iter().map(String::as_str).collect();

    // the base filled to the bed under its mounting face, for the slicer
    let base = root.join(BASE);
    let filled = out.join("filled-base.stl");
    let fill = filled_base::fill(&Mesh::read_stl(&base)?, base_courses::INCLINE_DEGREES, [FOOT_WIDTH / 2.0, FOOT_DEPTH / 2.0])?;
    write_stl(&filled, &fill.vertices, &fill.faces)?;

    // the editable plate, and the donor tip warped from it, sliced alone and laid as courses
    let editable = out.join("editable.3mf");
    prepare(&editable, &[&["--physical-base"], head_args.as_slice(), finish_args.as_slice()].concat())?;
    let donor = out.join("donor");
    fs::create_dir_all(&donor)?;
    let warped = donor.join("tip-warped.stl");
    tip_warp::write(&tip_warp::SHORT_SHOULDER, &tip, &editable, &warped)?;
    let settings = donor.join("warp-settings.json");
    tip_supports::write(&donor.join("tip-warped.json"), &settings)?;
    let mut recipe: Value = serde_json::from_slice(&fs::read(&settings)?)?;
    recipe["support_top_gap_mm"] = sculpted_plate::DONOR_SUPPORT_TOP_GAP_MM.into();
    fs::write(&settings, serde_json::to_string_pretty(&recipe)? + "\n")?;
    let donor_project = donor.join("donor.3mf");
    prepare(&donor_project, &["--warp-donor", "--tip-mesh", &path(&warped), "--warp-settings", &path(&settings),
        "--slice-output", &path(&donor.join("slice"))])?;
    let tape = out.join("tip.gcode");
    tip_courses::write(&donor.join("slice/plate_1.gcode"), &donor.join("donor.print.json"), &donor.join("tip-warped.json"), &tape,
        &tip_courses::Banding { step: 0.0, uphill: false })?;

    // the plate's project, sliced with the standing slice path's cooling stages; where the plate's
    // selections splice the tip's end, the project without the shallow overhang points gives it
    let project = out.join("native.3mf");
    prepare(&project, &[&["--filled-base", &path(&filled)], head_args.as_slice(), finish_args.as_slice()].concat())?;
    let report: Value = serde_json::from_slice(&fs::read(out.join("native.print.json"))?)?;
    let plain = plate.get("tip_end_splice").map(|_| out.join("plain/native.3mf"));
    if let Some(plain) = &plain {
        fs::create_dir_all(plain.parent().unwrap())?;
        prepare(plain, &[&["--filled-base", &path(&filled)], head_args.as_slice()].concat())?;
    }
    let slice = out.join("slice");
    let cooling = sculpted_plate::slice_with_cooling(&project, &report, &slice, plain.as_deref())?;
    fs::write(out.join("cooling.json"), serde_json::to_string_pretty(&cooling)? + "\n")?;

    // the base's foundation from its own mesh, the screw-seat rings and the plate's sequence
    let headmap = root.join(faucet_underside::HEAD_MAP);
    base_foundation::foundation(&base_foundation::Foundation {
        archive: &slice.join("native.gcode.3mf"), report: &out.join("native.print.json"), stl: &base, headmap: &headmap,
        out_dir: &out.join("base"), deck_top: None, part_courses: Some(base_foundation::SHORT_FOUNDATION_COURSES),
        lift_share: sculpted_plate::lift_share(&plate),
    })?;
    let rings = out.join("rings.gcode");
    fs::write(&rings, plate_rings::gcode())?;
    let open = out.join("open.gcode");
    plate_sequence::foundation_sequence::compose(&out.join("base/plate_1.gcode"), &slice.join("plate_1.gcode"), &tape,
        &donor.join("tip-warped.json"), &open, &rings, &headmap)?;

    // the plug ramp's flow cap, the printer's progress and the print-only archive
    let capped = out.join("capped.gcode");
    feed_cap::cap(&open, &capped)?;
    let bound = out.join("plate.gcode");
    feed_cap::bind(&open, &capped, &bound, Some(&out.join("capped.json")))?;
    let progressed = out.join("progressed.gcode");
    trial_archive::progress(&bound, None, &progressed)?;
    let timing = motion::timing(&fs::read_to_string(&progressed)?)?;
    let package = trial_archive::package(&slice.join("native.gcode.3mf"), &progressed, &out.join(ARCHIVE),
        timing.seconds, timing.first_course_seconds)?;
    fs::write(out.join("package.json"), serde_json::to_string_pretty(&package)? + "\n")?;
    println!("{}", out.join(ARCHIVE).display());
    Ok(())
}

fn path(p: &Path) -> String {
    p.to_string_lossy().into_owned()
}

fn run(command: &mut Command) -> Result<()> {
    let status = command.status().with_context(|| format!("running {:?}", command.get_program()))?;
    ensure!(status.success(), "{:?} exited {}", command.get_program(), status);
    Ok(())
}
