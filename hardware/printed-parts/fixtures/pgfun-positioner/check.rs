//! The positioner's sampled interference and conservative joint-load screens.
use anyhow::{Context, Result, bail, ensure};
use hsm_kernel::{Affine, Solid, V3};
use hsm_pgfun_positioner::{DIRECTORY, Design, load_meshes, references, root, sha256};
use serde::Deserialize;
use serde_json::json;
use std::{
    collections::{BTreeMap, BTreeSet},
    f64::consts::PI,
    path::{Path, PathBuf},
};

#[derive(Deserialize)]
struct Info {
    name: String,
    group: String,
    category: String,
}
#[derive(Deserialize)]
struct Printed {
    name: String,
    solid_mass_g: f64,
}
#[derive(Deserialize)]
struct Manifest {
    parts: Vec<Printed>,
}

fn overlap(a: &Solid, b: &Solid) -> Result<f64> {
    let (a0, b0) = (a.bounds(), b.bounds());
    if (0..3).any(|i| a0.min[i].max(b0.min[i]) >= a0.max[i].min(b0.max[i]) - 0.001) {
        return Ok(0.);
    }
    a.shared_volume(b)
}
fn intended(a: &str, b: &str) -> bool {
    [
        ("yaw-output-adapter", "yaw-journal"),
        ("pitch-output-adapter", "pitch-journal"),
        ("yaw-stop-sector", "yaw-stop-follower"),
        ("pitch-stop-sector", "pitch-stop-follower"),
    ]
    .iter()
    .any(|&(x, y)| (a == x && b == y) || (a == y && b == x))
}
fn round(value: f64, places: i32) -> f64 {
    let scale = 10_f64.powi(places);
    (value * scale).round_ties_even() / scale
}

fn run(root: &Path, out: &Path, fixed_reference: Option<&Path>) -> Result<()> {
    let d = Design::read(out.join("design.json"))?;
    let items: Vec<Info> =
        serde_json::from_slice(&std::fs::read(out.join("display-meshes.json"))?)?;
    let mut info: BTreeMap<_, _> = items.into_iter().map(|p| (p.name.clone(), p)).collect();
    let mut meshes = load_meshes(out.join("assembly-meshes.npz"))?;
    let reference_path = fixed_reference
        .map(PathBuf::from)
        .unwrap_or_else(|| out.join("reference-meshes.npz"));
    let pinned = if let Some(path) = fixed_reference {
        load_meshes(path)?
    } else {
        references(root, out, &d)?
    };
    let gun_frame = d.gun_transform();
    for (name, mesh) in pinned {
        let gun = name.starts_with("gun:");
        let mesh = if gun {
            mesh.transformed(&gun_frame)
        } else {
            mesh
        };
        info.insert(
            name.clone(),
            Info {
                name: name.clone(),
                group: if gun { "pitch" } else { "fixed" }.into(),
                category: "reference".into(),
            },
        );
        meshes.insert(name, mesh);
    }
    let printed: BTreeSet<_> = info
        .iter()
        .filter(|(_, p)| ["print", "liner"].contains(&p.category.as_str()))
        .map(|(n, _)| n.clone())
        .collect();
    let external: Vec<_> = meshes
        .keys()
        .filter(|n| {
            printed.contains(*n)
                || n.starts_with("gun:")
                || n.starts_with("rotator:")
                || ["-reducer", "-motor", "-stop-follower"]
                    .iter()
                    .any(|&suffix| n.ends_with(suffix))
                || ["camera-envelope", "raynox-dcr250"].contains(&n.as_str())
        })
        .cloned()
        .collect();
    let solids: BTreeMap<_, _> = external
        .iter()
        .map(|n| {
            Ok((
                n.clone(),
                meshes[n].solid(n).with_context(|| format!("reading {n}"))?,
            ))
        })
        .collect::<Result<_>>()?;
    let angles = [
        -d.hard_stop_deg,
        -d.soft_limit_deg,
        0.,
        d.soft_limit_deg,
        d.hard_stop_deg,
    ];
    let mut poses = vec![];
    let mut findings = vec![];
    let mut contacts = vec![];
    let mut pairs = 0_u64;
    let pivot = d.pivot();
    for yaw in angles {
        for pitch in angles {
            println!("checking pose {yaw} {pitch}");
            poses.push([yaw, pitch]);
            let ty = Affine::rotation(pivot, V3::Z, yaw);
            let tp = Affine::rotation(pivot, V3::X, pitch);
            let moved: BTreeMap<_, _> = external
                .iter()
                .map(|name| {
                    let frame = match info[name].group.as_str() {
                        "pitch" => tp.then(&ty),
                        "yaw" => ty,
                        _ => Affine::IDENTITY,
                    };
                    (name.clone(), solids[name].transformed(&frame))
                })
                .collect();
            for (i, a) in external.iter().enumerate() {
                for b in &external[i + 1..] {
                    if !printed.contains(a) && !printed.contains(b) {
                        continue;
                    }
                    if info[a].group == info[b].group && (yaw != 0. || pitch != 0.) {
                        continue;
                    }
                    pairs += 1;
                    let volume = overlap(&moved[a], &moved[b])
                        .with_context(|| format!("overlap of {a} and {b} at {yaw}, {pitch}"))?;
                    if volume > 0.5 {
                        let row = json!({"yaw_deg":yaw,"pitch_deg":pitch,"parts":[a,b],"overlap_mm3":round(volume,4)});
                        if intended(a, b) {
                            contacts.push(row);
                        } else {
                            findings.push(row);
                        }
                    }
                }
            }
        }
    }
    let manifest: Manifest =
        serde_json::from_slice(&std::fs::read(out.join("print-manifest.json"))?)?;
    let masses: BTreeMap<_, _> = manifest
        .parts
        .into_iter()
        .map(|p| (p.name, p.solid_mass_g / 1000.))
        .collect();
    let gun: Vec<_> = meshes
        .iter()
        .filter(|(n, _)| n.starts_with("gun:"))
        .flat_map(|(_, m)| m.vertices.iter())
        .map(|&p| V3::from(p))
        .collect();
    let max_y = gun.iter().map(|p| (p.y - pivot.y).abs()).fold(0., f64::max);
    let max_r = gun.iter().map(|p| (*p - pivot).norm()).fold(0., f64::max);
    let gravity_gun = d.gun_supported_mass_kg * 9.80665 * max_y / 1000.;
    let gravity_print = meshes
        .iter()
        .filter(|(name, _)| masses.contains_key(*name) && info[*name].group == "pitch")
        .map(|(name, m)| {
            let points: Vec<_> = m.vertices.iter().copied().map(V3::from).collect();
            let center = hsm_kernel::mass::of(&points, &m.faces).centroid;
            masses[name] * 9.80665 * (center.y - pivot.y).abs() / 1000.
        })
        .sum::<f64>();
    let cable = d.design_cable_force_n * max_r / 1000.;
    let torque = gravity_gun + gravity_print + cable;
    let t = d.design_joint_torque_nm * 1000.;
    let tf = d.structural_fault_torque_nm * 1000.;
    let net_polar = PI * (d.journal_diameter.powi(4) - 8_f64.powi(4)) / 32.
        - 6. * (PI * 9.4_f64.powi(4) / 32. + PI * 9.4_f64.powi(2) / 4. * 12_f64.powi(2));
    let screen = json!({"gun_mass_kg":d.gun_supported_mass_kg,"gun_max_pitch_lever_mm":round(max_y,3),"gun_max_radial_lever_mm":round(max_r,3),
        "gun_gravity_upper_bound_Nm":gravity_gun,"printed_pitch_gravity_upper_bound_Nm":gravity_print,"cable_force_N":d.design_cable_force_n,
        "cable_torque_upper_bound_Nm":cable,"pitch_service_torque_upper_bound_Nm":torque,"joint_screening_torque_Nm":d.design_joint_torque_nm,
        "six_key_bearing_stress_MPa":t/(6.*20.*6.*6.),"structural_fault_torque_Nm":d.structural_fault_torque_nm,
        "six_key_fault_bearing_stress_MPa":tf/(6.*20.*6.*6.),"journal_net_polar_moment_mm4":net_polar,"journal_torsion_MPa":t*(d.journal_diameter/2.)/net_polar,
        "bearing_moment_couple_N":t/14.,"6808_seller_static_load_N":4180.,"journal_flange_fastener_tangential_force_N_each":t/(6.*29.),
        "inner_bearing_seat_average_contact_MPa":500./(40.*7.),"outer_bearing_seat_average_contact_MPa":500./(52.*7.),"stop_follower_force_N":t/d.stop_radius,
        "stop_slot_fault_average_bearing_MPa":(tf/d.stop_radius)/(6.*11.2),"yaw_stop_arm_root_bending_MPa":(t/d.stop_radius)*11.*9./(12.*18_f64.powi(3)/12.),
        "yaw_stop_arm_fault_root_bending_MPa":(tf/d.stop_radius)*11.*9./(12.*18_f64.powi(3)/12.),
        "pitch_stop_arm_fault_root_bending_MPa":tf*24./((14.*(48_f64.powi(3)-18.2_f64.powi(3))+10.*(18.2_f64.powi(3)-14.4_f64.powi(3)))/12.),
        "bridge_80mm_net_width_bending_MPa":t*9./(80.*18_f64.powi(3)/12.),"journal_elastic_twist_at_7Nm_rad":t*25.2/(d.analysis_modulus_mpa/2.7*net_polar),
        "assumed_print_allowable_MPa":d.analysis_allowable_mpa,"assumed_print_E_MPa":d.analysis_modulus_mpa,
        "scope":"Conservative whole-gun mass at exterior extremum and design cable-force bound. Beam/contact screening assumptions, not measured printed strength or life."});
    let motion: serde_json::Value =
        serde_json::from_slice(&std::fs::read(out.join("motion-geometry.json"))?)?;
    let receipt = json!({"geometry_sha256":motion["sha256"],"assembly_mesh_sha256":sha256(out.join("assembly-meshes.npz"))?,"reference_mesh_sha256":sha256(reference_path)?,
        "poses_deg":poses,"pair_evaluations":pairs,"reporting_threshold_mm3":0.5,"intentional_key_interference_and_stop_contact":contacts,"unintended_intersections":findings,
        "scope":"Full-precision tessellated solids at sampled extreme and working poses. Fastener heads, physical cable, roller levers and continuous swept volumes require assembly checks."});
    std::fs::write(
        out.join("clearance-check.json"),
        serde_json::to_vec_pretty(&receipt)?,
    )?;
    std::fs::write(
        out.join("load-screen.json"),
        serde_json::to_vec_pretty(&screen)?,
    )?;
    println!(
        "{}",
        json!({"unintended_intersections":findings.len(),"service_torque_upper_bound_Nm":torque})
    );
    ensure!(findings.is_empty(), "unintended assembly intersections");
    ensure!(
        torque <= d.design_joint_torque_nm,
        "service torque exceeds the joint screen"
    );
    Ok(())
}

fn main() -> Result<()> {
    let root = root();
    let mut out = None;
    let mut fixed = None;
    let mut args = std::env::args_os().skip(1);
    while let Some(argument) = args.next() {
        if argument == "--fixed-reference" {
            fixed = Some(PathBuf::from(args.next().context("reference NPZ path")?));
        } else if out.is_none() {
            out = Some(PathBuf::from(argument));
        } else {
            bail!("usage: pgfun-check [<fixture directory>] [--fixed-reference <reference NPZ>]");
        }
    }
    hsm_kernel::reads::begin();
    run(
        &root,
        &out.unwrap_or_else(|| root.join(DIRECTORY)),
        fixed.as_deref(),
    )
}
