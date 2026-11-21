//! Places the installed fasteners for the main PCB, condenser, compressor and mains inlet.
use anyhow::{Context, Result};
use hsm_enclosure_numbers::{fasteners, layout::layout, rear_wall::c14, shell, spec};
use hsm_kernel::{Affine, Body, Plane, Profile, Solid, V3, v2, v3};
use hsm_kernel::part::write_shown;
use std::path::PathBuf;

fn screw(diameter: f64, length: f64, head_diameter: f64, head_height: f64, key: f64) -> Result<Solid> {
    let shaft = Solid::cylinder(V3::ZERO, -V3::Z, diameter / 2., length)?;
    let head = Solid::cylinder(V3::ZERO, V3::Z, head_diameter / 2., head_height)?;
    let radius = key / 3_f64.sqrt();
    let hex: Vec<_> = (0..6).map(|i| {
        let a = std::f64::consts::TAU * i as f64 / 6.;
        v2(radius * a.cos(), radius * a.sin())
    }).collect();
    let socket = Plane::XY.at(v3(0., 0., head_height / 2.)).extrude(&Profile::polygon(&hex), head_height)?;
    head.union(&shaft)?.cut(&socket)
}

fn ring(outside: f64, inside: f64, height: f64) -> Result<Solid> {
    Solid::cylinder(V3::ZERO, V3::Z, outside / 2., height)?
        .cut(&Solid::cylinder(v3(0., 0., -0.1), V3::Z, inside / 2., height + 0.2)?)
}

fn frame(axis: V3, at: V3) -> Affine {
    let (_, x, y) = hsm_kernel::rule::plane_frame(axis);
    Affine::from_columns(x, y, axis, at)
}

fn main() -> Result<()> {
    let out = std::env::args_os().nth(1).map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("hardware/printed-parts/enclosure/equipment-clamps"));
    hsm_kernel::reads::begin();
    std::fs::create_dir_all(&out)?;
    let l = layout();
    let mut installed = Vec::new();
    let document = hsm_enclosure_interface::input::json("hardware/manifold-layout/enclosure-box.json")?;
    let b = spec::Box::from_document(document)?;
    let steel = [0.025; 3];
    let brass = [0.65, 0.38, 0.09];
    for (i, column) in hsm_foam_cap_numbers::deck::columns().iter().enumerate() {
        let at = hsm_cold_core_layout::cap::cap_to_world([column.xy[0], column.xy[1], column.top]);
        let [x, y, z] = at;
        let bearing = z + hsm_foam_cap_numbers::deck::BOARD_THICKNESS;
        installed.push((format!("pcba-screw-{}", i + 1), steel,
            screw(3., hsm_foam_cap_numbers::deck::SCREW_LENGTH, 5.5, 3., 2.5)?.translate(v3(x, y, bearing))));
        installed.push((format!("pcba-insert-{}", i + 1), brass,
            ring(fasteners::M3_INSERT_DIAMETER, 2.5, fasteners::M3_INSERT_LENGTH)?.translate(v3(x, y, z - fasteners::M3_INSERT_LENGTH))));
    }
    for (i, &[x, y, tip]) in b.pack.cond_mount.3.iter().enumerate() {
        let bearing = tip + shell::COND_FLANGE_THICKNESS;
        installed.push((format!("condenser-washer-{}", i + 1), [0.72; 3],
            ring(fasteners::M3_WASHER_OUTER_DIAMETER, fasteners::M3_WASHER_INNER_DIAMETER,
                 shell::COND_WASHER_THICKNESS)?.translate(v3(x, y, bearing))));
        installed.push((format!("condenser-screw-{}", i + 1), steel,
            screw(3., shell::COND_SCREW_LEN, 5.5, 3., 2.5)?.translate(v3(x, y, bearing + shell::COND_WASHER_THICKNESS))));
        installed.push((format!("condenser-insert-{}", i + 1), brass,
            ring(fasteners::M3_INSERT_DIAMETER, 2.5, fasteners::M3_INSERT_LENGTH)?
                .translate(v3(x, y, tip - fasteners::M3_INSERT_LENGTH))));
    }
    for (i, &[x, y, tip, _]) in b.pack.floor_bosses.iter().enumerate() {
        installed.push((format!("compressor-screw-{}", i + 1), steel,
            screw(5., shell::FLOOR_SCREW_LENGTH, 8.5, 5., 4.)?.translate(v3(x, y, tip + shell::FLOOR_WASHER_THICKNESS))));
        installed.push((format!("compressor-washer-{}", i + 1), [0.72; 3],
            ring(25., 5.5, shell::FLOOR_WASHER_THICKNESS)?.translate(v3(x, y, tip))));
        installed.push((format!("compressor-insert-{}", i + 1), brass,
            ring(fasteners::M5_INSERT_DIAMETER, 4.3, fasteners::M5_INSERT_LENGTH)?
                .translate(v3(x, y, tip - fasteners::M5_INSERT_LENGTH))));
    }
    let [cx, cy, cz] = l.parts.c14_inlet.translation_mm;
    let face = cy + c14::RIM_PROUD;
    for (i, dx) in [-c14::EAR_CX, c14::EAR_CX].into_iter().enumerate() {
        let head = face - c14::RIM_PROUD - c14::FLANGE_T - c14::WASHER_THICKNESS;
        installed.push((format!("c14-screw-{}", i + 1), steel,
            screw(3., c14::SCREW_LENGTH, 5.5, 3., 2.5)?.transformed(&frame(-V3::Y, v3(cx + dx, head, cz)))));
        installed.push((format!("c14-washer-{}", i + 1), [0.72; 3],
            ring(fasteners::M3_WASHER_OUTER_DIAMETER, fasteners::M3_WASHER_INNER_DIAMETER, c14::WASHER_THICKNESS)?.transformed(&frame(V3::Y, v3(cx + dx, head, cz)))));
        installed.push((format!("c14-insert-{}", i + 1), brass,
            ring(fasteners::M3_INSERT_DIAMETER, 2.5, fasteners::M3_INSERT_LENGTH)?.transformed(&frame(V3::Y, v3(cx + dx, face, cz)))));
    }
    let bodies: Vec<_> = installed.iter().map(|(name, color, solid)| Body { name, color: Some(*color), solid }).collect();
    println!("{}", write_shown(&out, "equipment-clamps-installed", &bodies).context("installed mount hardware")?);
    Ok(())
}
