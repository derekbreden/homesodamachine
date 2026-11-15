//! faucet-plate prepares a faucet style's plate from the checkout's meshes and the plate's
//! selections, through to its print-only archive.
//!
//!     faucet-plate sculpted|industrial OUT_DIR [--production] [--printer Mark1|Mark2] [--filament-colour '#RRGGBB']
//!
//! It runs the preparer: the one built beside it, or the installed command of that name. The two
//! programs are built and installed together from the checkout, and the plate is prepared from
//! inside the checkout:
//!
//!     tools/run -- "$(rustup which cargo)" build --release --locked --offline -j 2 \
//!       --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin faucet-plate --bin faucet-print-project
//!     hsm-run --install-tools "$PWD" tools/hsm/target/release/faucet-plate \
//!       tools/hsm/target/release/faucet-print-project
//!     tools/run -- faucet-plate sculpted OUT_DIR
//!
//! OUT_DIR is the run's own folder and must not exist. Each style lays its own base and mounting
//! plate beside the shared tip, display cover and lever. The base is filled under its mounting face
//! for the slice and laid on its sloped foundation from its own mesh. The tip's mating courses come
//! from a warped donor tip, sliced alone and laid back onto the real shoulder. The archive and
//! every stage's receipt are written in OUT_DIR. `--production` makes it the style's product
//! plate: its editable project and report go to the style's project path, its archive to the style's
//! archive path, and beside the project a record of the plate with the acceleration planner's
//! estimate of its motion, which the ledger's machine time reads. Nothing is sent to a printer.

use anyhow::{Context, Result, bail, ensure};
use hsm_print_prep::mesh::{Mesh, write_stl};
use hsm_print_prep::{base_courses, base_foundation, faucet_plate, feed_cap, filled_base, motion,
    plate_rings, plate_sequence, tip_courses, tip_supports, tip_warp, trial_archive};
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

const PREPARER: &str = "faucet-print-project";
const USAGE: &str = "usage: faucet-plate sculpted|industrial OUT_DIR [--production] [--printer Mark1|Mark2] [--filament-colour '#RRGGBB']";

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let style = faucet_plate::style(&args.next().context(USAGE)?)?;
    let out = PathBuf::from(args.next().context(USAGE)?);
    let (mut printer, mut colour, mut production) = ("Mark2".to_string(), "#161616".to_string(), false);
    while let Some(arg) = args.next() {
        if arg == "--production" {
            production = true;
            continue;
        }
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
    let plate = faucet_plate::selection(&root)?;
    // the preparer: the one built beside this program, or the installed command of its name
    let beside = std::env::current_exe()?.parent().context("the programs' folder")?.join(PREPARER);
    let preparer = if beside.is_file() { beside } else { PathBuf::from(PREPARER) };
    let prepare = |project: &Path, extra: &[&str]| -> Result<()> {
        let mut command = Command::new(&preparer);
        command.arg(project).args(["--style", style.name, "--printer", &printer, "--filament-colour", &colour]).args(extra);
        run(command.current_dir(&root))
    };
    let tip = root.join(faucet_plate::TIP.stl);

    // the selections the plate's projects take, naming the style's base and mounting plate: all of
    // them, and without the shallow overhang points for the donor tip and the plain plate
    let selection = style.finish(&plate);
    let finish = out.join("finish.json");
    fs::write(&finish, serde_json::to_string_pretty(&selection)? + "\n")?;
    let mut plain = selection.clone();
    plain.as_object_mut().context("the plate's selections")?.remove("shallow_overhang_wall_speed");
    let plain_finish = out.join("plain-finish.json");
    fs::write(&plain_finish, serde_json::to_string_pretty(&plain)? + "\n")?;
    let finish_args = ["--finish".to_string(), path(&finish)];
    let finish_args: Vec<&str> = finish_args.iter().map(String::as_str).collect();

    // the base filled to the bed under its mounting face, for the slicer
    let base = root.join(style.base.stl);
    let mesh = Mesh::read_stl(&base)?;
    let filled = out.join("filled-base.stl");
    let fill = filled_base::fill(&mesh, base_courses::INCLINE_DEGREES, filled_base::rim(&mesh)?)?;
    write_stl(&filled, &fill.vertices, &fill.faces)?;

    // the editable plate, and the donor tip warped from it, sliced alone and laid as courses
    let editable = out.join("editable.3mf");
    prepare(&editable, &[&["--physical-base"], finish_args.as_slice()].concat())?;
    let donor = out.join("donor");
    fs::create_dir_all(&donor)?;
    let warped = donor.join("tip-warped.stl");
    tip_warp::write(&tip_warp::SHORT_SHOULDER, &tip, &editable, &warped)?;
    let settings = donor.join("warp-settings.json");
    tip_supports::write(&donor.join("tip-warped.json"), &settings)?;
    let mut recipe: Value = serde_json::from_slice(&fs::read(&settings)?)?;
    recipe["support_top_gap_mm"] = faucet_plate::DONOR_SUPPORT_TOP_GAP_MM.into();
    fs::write(&settings, serde_json::to_string_pretty(&recipe)? + "\n")?;
    let donor_project = donor.join("donor.3mf");
    prepare(&donor_project, &["--warp-donor", "--tip-mesh", &path(&warped), "--warp-settings", &path(&settings),
        "--slice-output", &path(&donor.join("slice")), "--finish", &path(&plain_finish)])?;
    let tape = out.join("tip.gcode");
    tip_courses::write(&donor.join("slice/plate_1.gcode"), &donor.join("donor.print.json"), &donor.join("tip-warped.json"), &tape,
        &tip_courses::Banding { step: 0.0, uphill: false })?;

    // the plate's project, sliced with the standing slice path's cooling stages; where the plate's
    // selections splice the tip's end, the project without the shallow overhang points gives it
    let project = out.join("native.3mf");
    prepare(&project, &[&["--filled-base", &path(&filled)], finish_args.as_slice()].concat())?;
    let report: Value = serde_json::from_slice(&fs::read(out.join("native.print.json"))?)?;
    let plain = plate.get("tip_end_splice").map(|_| out.join("plain/native.3mf"));
    if let Some(plain) = &plain {
        fs::create_dir_all(plain.parent().unwrap())?;
        prepare(plain, &["--filled-base", &path(&filled), "--finish", &path(&plain_finish)])?;
    }
    let slice = out.join("slice");
    let cooling = faucet_plate::slice_with_cooling(&project, &report, &selection["tip_end_cooling"], &slice, plain.as_deref())?;
    fs::write(out.join("cooling.json"), serde_json::to_string_pretty(&cooling)? + "\n")?;

    // the base's foundation from its own mesh, the screw-seat rings and the plate's sequence
    let headmap = root.join(base_foundation::HEAD_MAP);
    base_foundation::foundation(&base_foundation::Foundation {
        archive: &slice.join("native.gcode.3mf"), report: &out.join("native.print.json"), stl: &base, headmap: &headmap,
        out_dir: &out.join("base"), deck_top: None, part_courses: Some(base_foundation::SHORT_FOUNDATION_COURSES),
        lift_share: faucet_plate::lift_share(&plate),
    })?;
    let rings = out.join("rings.gcode");
    fs::write(&rings, plate_rings::gcode(&plate_rings::seats(&report)?))?;
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
    let archive = out.join(format!("{}-faucet-plate.gcode.3mf", style.name));
    let package = trial_archive::package(&slice.join("native.gcode.3mf"), &progressed, &archive, timing.seconds, timing.first_course_seconds)?;
    fs::write(out.join("package.json"), serde_json::to_string_pretty(&package)? + "\n")?;
    println!("{}", archive.display());
    if production {
        product(&root, style, &out, &archive, &package)?;
    }
    Ok(())
}

/// The style's product plate from the run in `out`: the editable project and its report, the
/// print-only archive, and the record of the plate beside the project.
fn product(root: &Path, style: &faucet_plate::Style, out: &Path, archive: &Path, package: &Value) -> Result<()> {
    let project = root.join(style.project);
    fs::copy(out.join("editable.3mf"), &project)?;
    let mut report: Value = serde_json::from_slice(&fs::read(out.join("editable.print.json"))?)?;
    report["project"] = style.project.into();
    // the selections by their file in the checkout, in place of the run's copy of them
    report["finish_selection"] = faucet_plate::SELECTION.into();
    report.as_object_mut().context("the editable project's report")?.remove("finish_selection_sha256");
    let sources = report["source_sha256"].as_object_mut().context("the report's sources")?;
    let copy = hsm_print_prep::profile::relative(&out.join("finish.json"), root);
    sources.remove(&copy).with_context(|| format!("the report's sources have no {copy}"))?;
    sources.insert(faucet_plate::SELECTION.into(), hsm_print_prep::sha256_hex(&fs::read(root.join(faucet_plate::SELECTION))?).into());
    fs::write(project.with_extension("print.json"), serde_json::to_string_pretty(&report)? + "\n")?;
    let kept = root.join(style.archive);
    fs::create_dir_all(kept.parent().context("the archive's folder")?)?;
    fs::copy(archive, &kept)?;
    let sha = |path: &Path| -> Result<String> { Ok(hsm_print_prep::sha256_hex(&fs::read(path)?)) };
    let record = serde_json::json!({
        "purpose": "Binds the style's product plate: its editable project, its print-only archive and the acceleration planner's estimate of the sequenced plate's motion.",
        "style": style.name,
        "project": style.project, "project_sha256": sha(&project)?,
        "archive": style.archive, "archive_sha256": sha(&kept)?, "gcode_sha256": package["gcode_sha256"],
        "estimate": "the acceleration planner's motion time for the sequenced plate's G-code, as its progress lines count it down",
        "estimated_motion_seconds": package["estimated_motion_seconds"],
        "printer_layers": package["printer_layers"],
        "deposition_weight_g": package["deposition_weight_g"],
    });
    fs::write(project.with_extension("plate.json"), serde_json::to_string_pretty(&record)? + "\n")?;
    println!("{}", project.display());
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
