//! The explicit enclosure reading derives probes from the native quadrant recipes and measures their existing fine models.
use anyhow::{Context, Result, ensure};
use hsm_enclosure_numbers::{
    catalog::{running, slip, supported},
    shell::*,
    spec::Box,
};
use hsm_enclosure_quadrants::{
    handholds::{band_x, handhold_backing_end, handhold_levels},
    quadrant::Y,
    rails::{rail_x, z_rail_runs},
};
use serde::Serialize;
use std::{path::Path, process::Command};
#[derive(Serialize)]
pub struct Probe {
    feature: String,
    parts: [String; 2],
    point: [f64; 3],
    normal: [f64; 3],
    gap: f64,
}
pub fn probes(b: &Box) -> Vec<Probe> {
    let mut probes = Vec::new();
    let mut add = |feature: String, a: &str, c: &str, point, normal, gap| {
        probes.push(Probe {
            feature,
            parts: [a.into(), c.into()],
            point,
            normal,
            gap,
        })
    };
    let [bed, roof, _] = handhold_levels(&b.inner);
    for (xi, sx) in [(b.inner[0], 1.), (b.inner[1], -1.)] {
        let side = if sx > 0. { "west" } else { "east" };
        let [_, cap] = band_x(xi - sx * WALL, sx);
        let gap = running() + supported();
        let fore = b.y_joint + (LIP_LEN - Y_STACK_CBORE_DIA) / 4.;
        add(
            format!("{side} handhold inner wall/knuckle fore rib"),
            "front-bottom",
            "back-bottom",
            [cap - sx * HANDHOLD_WALL / 2., fore, roof - gap],
            [0., 0., 1.],
            gap,
        );
        add(
            format!("{side} inner wall and floor square end"),
            "front-bottom",
            "back-bottom",
            [
                cap - sx * HANDHOLD_WALL / 2.,
                handhold_backing_end(b.y_joint, Y::Front),
                (bed + roof) / 2.,
            ],
            [0., 1., 0.],
            running(),
        );
        let x = rail_x(sx, Y::Front);
        add(
            format!("{side} rail entrance/tee wall"),
            "front-bottom",
            "front-top",
            [
                (x.arm + x.arm_end) / 2.,
                b.pack.collet_plate.wall_aft_y + slide_slip(),
                b.splits[0] + 1.,
            ],
            [0., -1., 0.],
            slide_slip(),
        );
    }
    for [x, y, _] in &b.pack.vent_chase {
        add(
            "vent chase seam".into(),
            "back-bottom",
            "back-top",
            [x - VENT_RIB_WALL / 2., *y, b.splits[1] + Z_RISE],
            [0., 0., 1.],
            slide_slip(),
        );
    }
    for ((side, column), z) in [("front", Y::Front), ("back", Y::Back)]
        .into_iter()
        .zip(b.splits)
    {
        for run in z_rail_runs(&b.inner, b.y_joint, column) {
            let sy = if run.y1 > run.y0 { 1. } else { -1. };
            let x = rail_x(run.sx, column);
            let flank = if run.sx > 0. { "west" } else { "east" };
            add(
                format!("{side} {flank} rail end"),
                &format!("{side}-top"),
                &format!("{side}-bottom"),
                [
                    (x.hook + x.foot) / 2.,
                    run.y1 - sy * RAIL_STOP_LEN,
                    z + HOOK_FOOT / 2.,
                ],
                [0., sy, 0.],
                slide_slip(),
            );
        }
    }
    probes
}
pub fn run(root: &Path) -> Result<i32> {
    #[derive(Serialize)]
    struct Piece {
        name: &'static str,
        model: String,
        print_up: i32,
    }
    #[derive(Serialize)]
    struct Fits {
        slip: f64,
        running: f64,
        supported_surface: f64,
    }
    #[derive(Serialize)]
    struct Numbers {
        pieces: Vec<Piece>,
        fits: Fits,
        probes: Vec<Probe>,
    }
    let b = Box::read(&root.join("hardware/manifold-layout/enclosure-box.json"))?;
    let directory = "hardware/printed-parts/enclosure/enclosure";
    let numbers = Numbers {
        pieces: [
            ("front-bottom", 1),
            ("back-bottom", 1),
            ("front-top", 1),
            ("back-top", -1),
        ]
        .into_iter()
        .map(|(name, print_up)| Piece {
            name,
            model: format!("{directory}/enclosure-{name}.step.npz"),
            print_up,
        })
        .collect(),
        fits: Fits {
            slip: slip(),
            running: running(),
            supported_surface: supported(),
        },
        probes: probes(&b),
    };
    let scratch = root
        .join(".cache/runs")
        .join(format!("enclosure-mating-{}", std::process::id()));
    std::fs::create_dir_all(&scratch)?;
    let input = scratch.join("numbers.json");
    crate::write_json(&input, &numbers)?;
    let program = crate::program(root, "enclosure-mating")?;
    let run = Command::new(root.join("tools/run"))
        .arg("--")
        .arg(program)
        .arg(&input)
        .arg("--check")
        .current_dir(root)
        .output()?;
    let _ = std::fs::remove_file(input);
    let _ = std::fs::remove_dir(scratch);
    ensure!(
        run.status.success(),
        "enclosure-mating: {}",
        String::from_utf8_lossy(&run.stderr)
    );
    let report: serde_json::Value =
        serde_json::from_slice(&run.stdout).context("enclosure-mating report")?;
    let target = root.join("hardware/printed-parts/enclosure/mating-clearance-check.json");
    crate::write_json(&target, &report)?;
    let failures = report["failures"]
        .as_array()
        .context("mating failures")?
        .len();
    let patches = report["checked_patches"]
        .as_u64()
        .context("mating patches")?;
    let gaps = report["required_gaps"]
        .as_array()
        .context("required gaps")?
        .len();
    if failures == 0 {
        println!("✓ {patches} mating patches and {gaps} required gaps keep their fits.");
    } else {
        println!(
            "✗ {failures} of {patches} mating patches and {gaps} required gaps miss their fits; see hardware/printed-parts/enclosure/mating-clearance-check.json."
        );
    }
    Ok(i32::from(report["status"] != "pass"))
}
