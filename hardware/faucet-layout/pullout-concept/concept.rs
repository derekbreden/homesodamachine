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
const VALVE_N: f64 = -40.0;
const VALVE_S: f64 = -28.0;
const STEM_LIFT: f64 = 80.0;

fn rounded_section(x: f64, y: f64, radius: f64) -> Profile {
    let mut points = vec![];
    for corner in 0..4 {
        let cx = if corner == 0 || corner == 3 { x - radius } else { radius - x };
        let cy = if corner < 2 { y - radius } else { radius - y };
        for sample in 0..=16 {
            let a = (corner as f64 + sample as f64 / 16.) * std::f64::consts::FRAC_PI_2;
            points.push(v2(cx + radius * a.cos(), cy + radius * a.sin()));
        }
    }
    Profile::polygon(&points)
}

fn pod(neck: &Gooseneck, inside: bool) -> Result<Solid> {
    let (tip, back, normal) = neck.tip_frame();
    let inset = if inside { 2.5 } else { 0. };
    let sections = [
        (-48. + inset, 14., -49., 16.),
        (-38. + inset, 24., -24., 40.),
        (-20. + inset, 26., -7., 57.),
        (48. - inset, 26., -7., 57.),
        (66. - inset, 22., -4., 44.),
        (86. - inset, 19., -34., 26.),
        (104. - inset, 17.5, -42., 17.5),
    ].into_iter().map(|(s, x, n, r)| {
        let plane = Plane::new(tip + back * s + normal * n, V3::X, back)?;
        Ok(rounded_section(x - inset, r - inset, 7.0_f64.min(r - inset - 1.)).place(&plane))
    }).collect::<Result<Vec<_>>>()?;
    Solid::loft(&sections)
}

// The dimensional drawing owns the valve envelope; the plug and adapters are reserved packaging space.
fn valve_parts(neck: &Gooseneck, steel: [f64; 3]) -> Result<(Vec<Item>, Solid, Solid)> {
    let tip_plane = hsm_faucet::display::tip_plane(neck)?;
    let valve_frame = Plane::new(v3(0., VALVE_S, VALVE_N), V3::X, V3::Y)?;
    let place = |s: Solid| s.placed(&Plane::XY, &valve_frame).placed(&Plane::XY, &tip_plane);
    let mut items = vec![];
    let block = Plane::XY.extrude(&Profile::polygon(&[
        v2(-17.32, 0.), v2(-8.66, -15.), v2(8.66, -15.),
        v2(17.32, 0.), v2(8.66, 15.), v2(-8.66, 15.),
    ]), 22.)?;
    let bosses = Solid::cylinder(v3(0., -19.5, 7.), V3::Y, 8., 39.)?;
    let ports = Solid::cylinder(v3(0., -20., 7.), V3::Y, 4.3, 9.)?
        .union(&Solid::cylinder(v3(0., 20., 7.), -V3::Y, 4.3, 9.)?)?;
    add(&mut items, "head_ODE_21L1K1T25_stainless_body", steel, place(block.union(&bosses)?.cut(&ports)?));
    add(&mut items, "head_ODE_armature_tube", steel,
        place(Solid::cylinder(v3(0., 0., 22.), V3::Z, 6.5, 54.)?));
    let coil = Solid::cuboid(v3(-18., -30., 34.), v3(18., 18., 73.))
        .cut(&Solid::cylinder(v3(0., 0., 33.), V3::Z, 6.5, 42.)?)?;
    add(&mut items, "head_ODE_12V_12W_coil", [0.045, 0.047, 0.050], place(coil));
    add(&mut items, "head_ODE_coil_retaining_nut", steel,
        place(Solid::cylinder(v3(0., 0., 73.), V3::Z, 9., 5.)?));
    for x in [-9.5, 9.5] {
        add(&mut items, "head_ODE_spade_terminal", [0.65, 0.47, 0.18],
            place(Solid::cuboid(v3(x - 3., -42., 48.), v3(x + 3., -30., 48.8))));
    }
    add(&mut items, "head_DIN_connector_envelope", [0.13, 0.14, 0.15],
        place(Solid::cuboid(v3(-16.5, -66., 34.), v3(16.5, -30., 67.))));

    let p = |x: f64, s: f64, n: f64| tip_plane.point(v2(x, s)) + tip_plane.z * n;
    let make = |s: Solid| s.placed(&Plane::XY, &tip_plane);
    let blue = [0.12, 0.43, 0.68];
    let joint = neck.at_angle(paths::JOINT_ANGLE) + JOINT_GAP / 2.;
    let (heel, heel_tangent, heel_normal) = neck.frame(joint);
    let heel = heel + heel_normal * shell::TUBE_SHELL_CENTER_Y;
    let (heel_xy, heel_n) = tip_plane.local(heel);
    let left = V3::X.cross(heel_tangent);
    let ts = heel_tangent.dot(tip_plane.y);
    let tn = heel_tangent.dot(tip_plane.z);
    let ars = left.dot(tip_plane.y);
    let arn = left.dot(tip_plane.z) + 1.;
    let inlet_n = 33.;
    let ds = 39. - heel_xy.y;
    let dn = inlet_n - heel_n;
    let det = ts * arn - tn * ars;
    let straight = (ds * arn - dn * ars) / det;
    let bend_radius = (ts * dn - tn * ds) / det;
    let arc_start = heel + heel_tangent * straight;
    let arc_center = arc_start + left * bend_radius;
    let arc_end = arc_center + tip_plane.z * bend_radius;
    let hose_path = Path::new(heel).line_to(arc_start)
        .arc_center(arc_center, arc_end, V3::X)?
        .line_to(p(0., 0., inlet_n));
    println!("Head soda hose bend radius {bend_radius:.3} mm");
    add(&mut items, "head_pressurized_soda_hose", blue,
        route(&hose_path, heel, heel_tangent, 5.8)?);
    let inlet_s = VALVE_S + 7.;
    let inlet_port_n = VALVE_N + 19.5;
    let inlet_path = Path::new(p(0., 0., inlet_n))
        .line_to(p(0., inlet_s + 6., inlet_n))
        .arc_center(p(0., inlet_s + 6., inlet_n - 6.), p(0., inlet_s, inlet_n - 6.), V3::X)?
        .line_to(p(0., inlet_s, inlet_port_n - 6.));
    let inlet_adapter = route(&inlet_path, p(0., 0., inlet_n), -tip_plane.y, 4.8)?
        .cut(&route(&inlet_path, p(0., 0., inlet_n), -tip_plane.y, 3.35)?)?;
    add(&mut items, "head_custom_stainless_inlet_adapter", steel, inlet_adapter);
    let outlet_s = VALVE_S + 7.;
    let outlet_n = VALVE_N - 19.5;
    let outlet_path = Path::new(p(0., outlet_s, outlet_n + 6.))
        .line_to(p(0., outlet_s, outlet_n - 9.5))
        .bezier(&[p(0., outlet_s, outlet_n - 9.5), p(0., outlet_s, outlet_n - 18.5),
            p(0., VALVE_S, outlet_n - 18.5), p(0., VALVE_S - 10., outlet_n - 18.5)])?;
    let outlet = route(&outlet_path, p(0., outlet_s, outlet_n + 6.), -tip_plane.z, 4.8)?;
    let bore = route(&outlet_path, p(0., outlet_s, outlet_n + 6.), -tip_plane.z, 2.)?;
    add(&mut items, "head_short_post_valve_nozzle", steel, outlet.cut(&bore)?);
    add(&mut items, "head_nozzle_end", steel,
        make(annulus(Plane::new(v3(0., VALVE_S - 13., outlet_n - 18.5), V3::X, V3::Y)?, 4.8, 2., 3.)?));
    let wire_start = p(15., VALVE_S + 67., VALVE_N + 52.);
    let wires = Path::new(wire_start)
        .bezier(&[wire_start, p(18., 72., 20.), heel + heel_tangent * 20., heel])?;
    add(&mut items, "head_valve_power_pair", [0.72, 0.18, 0.12],
        route(&wires, wire_start, p(18., 72., 20.) - wire_start, 1.8)?);
    let hose_spine = route(&hose_path, heel, heel_tangent, 8.3)?;
    let hose_clearance = route(&hose_path, heel, heel_tangent, 6.6)?;
    Ok((items, hose_spine, hose_clearance))
}

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
    let original_neck = Gooseneck::shell();
    let original_tip_plane = hsm_faucet::display::tip_plane(&original_neck)?;
    let mut neck = original_neck;
    neck.lift += STEM_LIFT;
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
    let trim = neck.plane(joint + JOINT_GAP / 2.)?.extrude(&Profile::rect(v2(0., 0.), 500., 500.), 250.)?;
    let tip_plane = hsm_faucet::display::tip_plane(&neck)?;
    let (valve, hose_spine, hose_clearance) = valve_parts(&neck, steel)?;
    let shell_outer = pod(&neck, false)?.union(&enlarged_grip)?.union(&grip_blend)?
        .union(&hose_spine)?.intersect(&trim)?;
    let mut tip = shell_outer.cut(&pod(&neck, true)?)?.cut(&hose_clearance)?;
    let pcb = body("faucet_display")?.placed(&original_tip_plane, &Plane::XY);
    let display_shift = Affine::translation(tip_plane.z * (42. - pcb.bounds().min.z));
    let screen_center = body("faucet_display_screen")?.placed(&original_tip_plane, &tip_plane)
        .transformed(&display_shift).bounds().center();
    let (screen_xy, screen_n) = tip_plane.local(screen_center);
    let window = tip_plane.offset(40.).shifted(screen_xy).extrude(
        &Profile::new(Loop::rounded_rect(v2(0., 0.), 26., 46., 3.)?), 40.)?;
    tip = tip.cut(&window)?;
    tip = tip.cut(&Solid::cylinder(v3(0., VALVE_S + 7., VALVE_N - 45.), V3::Z, 5.3, 40.)?
        .placed(&Plane::XY, &tip_plane))?;
    let plinth_profile = Profile::new(Loop::rounded_rect(v2(0., 0.), 30., 50., 4.)?)
        .with_hole(Loop::rounded_rect(v2(0., 0.), 26., 46., 3.)?);
    tip = tip.union(&tip_plane.offset(40.).shifted(screen_xy).extrude(&plinth_profile, screen_n - 41.1)?)?;
    let bezel_plane = tip_plane.offset(screen_n - 1.1).shifted(screen_xy);
    let bezel = bezel_plane.extrude(&Profile::new(Loop::rounded_rect(v2(0., 0.), 30., 50., 4.)?)
        .with_hole(Loop::rounded_rect(v2(0., 0.), 18.3, 33.3, 1.8)?), 1.4)?;
    let envelope = tip.union(&bezel)?.placed(&tip_plane, &Plane::XY).bounds();
    println!("Head shell in tip frame: {envelope:?}");
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
        for name in ["faucet_display", "faucet_display_screen"] {
            add(&mut scene, &format!("head_{name}"), black,
                body(name)?.placed(&original_tip_plane, &tip_plane).transformed(&display_shift).transformed(&pose));
        }
        add(&mut scene, "head_display_bezel", black, bezel.transformed(&pose));
        for (name, color, component) in &valve {
            add(&mut scene, name, *color, component.transformed(&pose));
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
            let mid = v3(-75., -120., 178. + STEM_LIFT);
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
        let screen = tip_plane.offset(screen_n + 0.40);
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
        scene.retain(|(name, _, _)| !["under_counter_moving_loop", "split_return_weight", "hollow_mounting_shank", "sliding_bundle_inside_stem"].contains(&name.as_str()));
        write(&dir, &format!("{overview_name}-above-counter"), &scene)?;
        if pulled {
            scene.retain(|(name, _, _)| name.starts_with("head_") || name.starts_with("screen_")
                || ["pull_off_curved_grip", "soft_hose_strain_relief"].contains(&name.as_str()));
            write(&dir, "handheld-detail", &scene)?;
            let mut cutaway = scene.clone();
            let removed_half = Solid::cuboid(v3(0., -120., -100.), v3(150., 160., 130.))
                .placed(&Plane::XY, &tip_plane).transformed(&pose);
            for (name, _, solid) in &mut cutaway {
                if name == "pull_off_curved_grip" { *solid = solid.cut(&removed_half)?; }
            }
            write(&dir, "head-valve-cutaway", &cutaway)?;
            write(&dir, "selected-electronic-valve", &valve.iter()
                .filter(|(name, _, _)| name.starts_with("head_ODE") || name == "head_DIN_connector_envelope")
                .map(|(name, color, solid)| (name.clone(), *color, solid.placed(&tip_plane, &Plane::XY)
                    .placed(&Plane::new(v3(0., VALVE_S, VALVE_N), V3::X, V3::Y).unwrap(), &Plane::XY)))
                .collect::<Vec<_>>())?;
        }
        println!("{overview_name}: exposed bundle {outside_length:.1} mm; loop bottom {bottom:.1} mm");
    }
    Ok(())
}
