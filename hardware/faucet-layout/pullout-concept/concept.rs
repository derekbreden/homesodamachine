//! This study shows the Sculpted faucet as a docked tap and a handheld dispenser with a sliding beverage bundle.
use anyhow::Result;
use hsm_faucet::Gooseneck;
use hsm_faucet_numbers::{paths, shell};
use hsm_kernel::{Affine, Font, HAlign, Kind, Loop, Path, Plane, Profile, Solid, V3, VAlign, v2, v3};
use hsm_sandbox::{material, out, part, show};

type Item = (String, [f64; 3], Solid);

const NECK_R: f64 = 17.5;
const BORE_R: f64 = 12.4;
const BUNDLE_R: f64 = 11.2;
const JOINT_GAP: f64 = 0.8;
const HOSE_TAIL: f64 = 65.0;
const LOOP_R: f64 = 70.0;
const LOOP_BOTTOM: f64 = -450.0;
const WEIGHT_DOCK_Z: f64 = -350.0;

fn add(items: &mut Vec<Item>, name: &str, color: [f64; 3], solid: Solid) {
    items.push((name.into(), color, solid));
}

fn annulus(plane: Plane, outer: f64, inner: f64, length: f64) -> Result<Solid> {
    plane.extrude(&Profile::circle(v2(0., 0.), outer).with_hole(Loop::circle(v2(0., 0.), inner)), length)
}

fn route(path: &Path, start: V3, tangent: V3, radius: f64) -> Result<Solid> {
    let across = if tangent.cross(V3::X).norm() > 0.1 { V3::X } else { V3::Y };
    Plane::new(start, across, tangent)?.sweep(&Profile::circle(v2(0., 0.), radius), path)
}

fn write(dir: &std::path::Path, name: &str, items: &[Item]) -> Result<()> {
    let refs: Vec<_> = items.iter().map(|(name, color, solid)| (name.as_str(), *color, solid)).collect();
    show(dir, name, &refs)
}

fn main() -> Result<()> {
    let dir = out()?;
    let old = part("faucet-layout/faucet-assembly.step")?;
    let body = |name: &str| hsm_kernel::import::body(&old, name);
    let black = material("M_PETGF_BLACK")?;
    let steel = material("M_STAINLESS")?;
    let green = [0.10, 0.58, 0.29];
    let pale = [0.73, 0.80, 0.74];
    let neck = Gooseneck::shell();
    let joint = neck.at_angle(paths::JOINT_ANGLE);
    let round = v2(0., shell::TUBE_SHELL_CENTER_Y);
    let hose_profile = Profile::circle(round, BORE_R);
    let outer = Profile::circle(round, NECK_R).with_hole(Loop::circle(round, BORE_R));
    let lower_cut = Solid::cuboid(v3(-100., -150., -2.), v3(100., 100., 62.));
    let lower_bore = Solid::cylinder(v3(0., paths::WATER_Y + round.y, -3.), V3::Z, BORE_R, 75.)?;
    let lower = body("shell_base")?.intersect(&lower_cut)?.cut(&lower_bore)?;
    let stem = lower.union(&neck.sweep(&outer, -12., joint - JOINT_GAP / 2.)?)?;
    let center = |u: f64| { let (p, _, n) = neck.frame(u); p + n * round.y };
    let heel = center(joint + JOINT_GAP / 2.);
    let (_, tangent, normal) = neck.frame(joint);
    let pivot = center(joint);
    let font = Font::find("Helvetica Neue", Kind::Regular)?;
    let head_sleeve_end = neck.length() - 54.;
    let enlarged_grip = neck.sweep(&outer, joint + JOINT_GAP / 2., head_sleeve_end - 14.)?;
    let mut blend_sections = vec![];
    for step in 0..=8 {
        let f = step as f64 / 8.;
        let radius = NECK_R + (shell::TUBE_SHELL_OUTER_R - NECK_R) * (f * f * (3. - 2. * f));
        let polygon: Vec<_> = (0..128).map(|i| {
            let a = std::f64::consts::TAU * i as f64 / 128.;
            round + v2(a.cos(), a.sin()) * radius
        }).collect();
        blend_sections.push(Profile::polygon(&polygon).place(&neck.plane(head_sleeve_end - 14.2 + f * 14.4)?));
    }
    let grip_blend = Solid::loft(&blend_sections)?.cut(&neck.sweep(&hose_profile, joint - 1., head_sleeve_end + 1.)?)?;
    let original_tip = body("shell_tip")?.cut(&neck.sweep(&hose_profile, joint - 22., head_sleeve_end + 1.)?)?;
    let trim = neck.plane(joint + JOINT_GAP / 2.)?.extrude(&Profile::rect(v2(0., 0.), 100., 100.), 250.)?;
    let tip = original_tip.intersect(&trim)?.union(&enlarged_grip)?.union(&grip_blend)?;
    let sleeve_color = [0.022, 0.025, 0.026];
    let counter = Solid::cuboid(v3(-210., -320., -30.), v3(290., 145., 0.))
        .cut(&Solid::cylinder(v3(0., paths::WATER_Y + round.y, -31.), V3::Z, 17., 33.)?)?;
    let shank = annulus(Plane::XY.at(v3(0., paths::WATER_Y + round.y, -64.)), 15., BORE_R, 64.)?;

    for pulled in [false, true] {
        let mut scene = vec![];
        let pose = if pulled {
            Affine::translation(v3(-145., -165., -28.))
                .then(&Affine::rotation(pivot + v3(-145., -165., -28.), V3::Z, 12.))
                .then(&Affine::rotation(pivot + v3(-145., -165., -28.), V3::X, 12.))
        } else { Affine::IDENTITY };
        add(&mut scene, "fixed_sculpted_stem", black, stem.clone());
        add(&mut scene, "existing_base_lever_electronic_actuation", black, body("lever")?.clone());
        add(&mut scene, "countertop", [0.57, 0.56, 0.53], counter.clone());
        add(&mut scene, "hollow_mounting_shank", steel, shank.clone());
        add(&mut scene, "sliding_bundle_inside_stem", sleeve_color,
            neck.sweep(&Profile::circle(round, BUNDLE_R), -HOSE_TAIL - shell::ZONE5_Z_TOP, joint - JOINT_GAP / 2.)?);
        add(&mut scene, "pull_off_curved_grip", black, tip.transformed(&pose));
        for name in ["faucet-display-cover-seated", "faucet_display", "faucet_display_screen"] {
            add(&mut scene, &format!("head_{name}"), black, body(name)?.transformed(&pose));
        }
        let dock_plane = Plane::new(pivot - tangent * 3., V3::X, tangent)?;
        add(&mut scene, "keyed_magnetic_dock", steel, annulus(dock_plane, NECK_R - 1.5, BORE_R, 2.)?);
        let sensor = Solid::cuboid(v3(-3., -2., 0.), v3(3., 2., 2.)).placed(&Plane::XY,
            &Plane::new(pivot + normal * (NECK_R - 2.), V3::X, normal)?);
        add(&mut scene, "dock_presence_sensor", green, sensor);
        let head_heel = pose.point(heel);
        let head_tangent = pose.vector(tangent);
        let (outside_path, outside_length) = if pulled {
            let start = center(joint - JOINT_GAP / 2.);
            let mid = v3(-75., -120., 178.);
            let p = Path::new(start)
                .bezier(&[start, start + tangent * 55., mid - v3(-45., -35., -20.), mid])?
                .bezier(&[mid, mid + v3(-45., -35., -20.), head_heel - head_tangent * 70., head_heel])?;
            let length: f64 = p.curves.iter().map(|curve| {
                let (a, b) = curve.range();
                (0..200).map(|i| {
                    let ta = a + (b - a) * i as f64 / 200.;
                    let tb = a + (b - a) * (i + 1) as f64 / 200.;
                    (curve.point(tb) - curve.point(ta)).norm()
                }).sum::<f64>()
            }).sum();
            (Some(p), length)
        } else { (None, 0.) };
        if let Some(path) = outside_path {
            let start = center(joint - JOINT_GAP / 2.);
            add(&mut scene, "flexible_braided_beverage_bundle", sleeve_color, route(&path, start, tangent, BUNDLE_R)?);
        }
        let heel_plane = Plane::new(heel, V3::X, tangent)?;
        add(&mut scene, "soft_hose_strain_relief", sleeve_color,
            annulus(heel_plane.offset(-12.), 13.2, BUNDLE_R - 1., 18.)?.transformed(&pose));
        let below_y = paths::WATER_Y + round.y;
        let bottom = LOOP_BOTTOM + outside_length / 2.;
        let start = v3(0., below_y, -HOSE_TAIL);
        let low = bottom + LOOP_R;
        let loop_path = Path::new(start).line_to(v3(0., below_y, low))
            .arc_center(v3(LOOP_R, below_y, low), v3(2. * LOOP_R, below_y, low), -V3::Y)?
            .line_to(v3(2. * LOOP_R, below_y, -80.));
        add(&mut scene, "under_counter_moving_loop", sleeve_color, route(&loop_path, start, -V3::Z, BUNDLE_R)?);
        let weight_z = WEIGHT_DOCK_Z + outside_length;
        add(&mut scene, "split_return_weight", [0.08, 0.09, 0.095],
            annulus(Plane::XY.at(v3(0., below_y, weight_z - 16.)), 24., BUNDLE_R + 0.3, 32.)?);
        add(&mut scene, "stationary_bundle_anchor", steel,
            annulus(Plane::XY.at(v3(2. * LOOP_R, below_y, -92.)), 17., BUNDLE_R + 0.3, 24.)?);
        add(&mut scene, "anchor_bracket", steel, Solid::cuboid(v3(2. * LOOP_R - 20., below_y + 12., -91.),
            v3(2. * LOOP_R + 20., below_y + 17., -30.)));

        let screen_center = body("faucet_display_screen")?.bounds().center();
        let (dispense, _, display_normal) = neck.tip_frame();
        let display_plane = Plane::new(dispense, V3::X, display_normal)?;
        let (screen_xy, screen_n) = display_plane.local(screen_center);
        let screen = display_plane.offset(screen_n + 0.40);
        let face = screen.extrude(&Profile::new(Loop::rounded_rect(screen_xy, 17.3, 32.3, 1.3)?), 0.15)?;
        add(&mut scene, "screen_lit_background", [0.006, 0.018, 0.012], face.transformed(&pose));
        let line = |text: &str, x: f64, y: f64, size: f64| -> Result<Solid> {
            Ok(screen.offset(0.20).shifted(screen_xy + v2(x, y))
                .text(&font, text, size, 0.12, HAlign::Center, VAlign::Center)?.transformed(&pose))
        };
        add(&mut scene, "screen_mode", pale, line(if pulled { "HANDHELD" } else { "ON TAP" }, 0., 11., 2.15)?);
        add(&mut scene, "screen_flavor", green, line("DEW", 0., 5.3, 4.1)?);
        add(&mut scene, "screen_other_flavor", pale, line("PEPSI", 0., 0.1, 2.7)?);
        let button = screen.offset(0.20).extrude(&Profile::new(Loop::rounded_rect(screen_xy + v2(0., -9.), 14.8, 8.4, 1.4)?), 0.12)?;
        add(&mut scene, "screen_hold_button", green, button.transformed(&pose));
        add(&mut scene, "screen_hold_label", [0.002, 0.018, 0.008], line(if pulled { "HOLD" } else { "READY" }, 0., -9., 2.55)?);

        let overview_name = if pulled { "pulled-out" } else { "docked" };
        write(&dir, overview_name, &scene)?;
        scene.retain(|(name, _, _)| !["under_counter_moving_loop", "split_return_weight", "stationary_bundle_anchor", "anchor_bracket", "hollow_mounting_shank", "sliding_bundle_inside_stem"].contains(&name.as_str()));
        write(&dir, &format!("{overview_name}-above-counter"), &scene)?;
        if pulled {
            scene.retain(|(name, _, _)| name.starts_with("head_") || name.starts_with("screen_")
                || ["pull_off_curved_grip", "soft_hose_strain_relief"].contains(&name.as_str()));
            write(&dir, "handheld-detail", &scene)?;
        }
        println!("{overview_name}: exposed bundle {outside_length:.1} mm; loop bottom {bottom:.1} mm");
    }
    Ok(())
}
