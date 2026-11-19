//! This study shows the Sculpted faucet as a docked tap and a handheld dispenser with a sliding beverage bundle.
use anyhow::Result;
use hsm_faucet::Gooseneck;
use hsm_faucet_numbers::{paths, shell};
use hsm_kernel::{Affine, Font, HAlign, Kind, Loop, Path, Plane, Profile, Solid, V3, VAlign, v2, v3};
use hsm_sandbox::{material, out, part, show};

type Item = (String, [f64; 3], Solid);

const NECK_R: f64 = 13.5;
const HEAD_R: f64 = 14.0;
const HEAD_BORE_R: f64 = 12.0;
const BORE_R: f64 = 11.5;
const BUNDLE_R: f64 = 9.8;
const JOINT_GAP: f64 = 0.6;
const HOSE_TAIL: f64 = 65.0;
const LOOP_R: f64 = 70.0;
const LOOP_BOTTOM: f64 = -450.0;
const WEIGHT_DOCK_Z: f64 = -350.0;
const DISPLAY_LIFT: f64 = 0.5;
const SEAT_D: f64 = 4.0;
const VALVE_LIFT: f64 = 0.6;
const ACTUATOR_R: f64 = 7.25;
const BALANCE_PISTON_S: f64 = 12.0;
const BALANCE_PISTON_LENGTH: f64 = 2.2;
const LOW_CHAMBER_END: f64 = 16.3;
const STEM_R: f64 = 0.8;
const VENT_R: f64 = 0.3;

fn tube(path: &Path, start: V3, tangent: V3, outer: f64, inner: f64) -> Result<Solid> {
    let across = if tangent.cross(V3::X).norm() > 0.1 { V3::X } else { V3::Y };
    Plane::new(start, across, tangent)?.sweep(
        &Profile::circle(v2(0., 0.), outer).with_hole(Loop::circle(v2(0., 0.), inner)), path)
}

// The head carries a balanced wet cartridge, a dry magnetic actuator and separate beverage lines.
fn custom_valve(neck: &Gooseneck, steel: [f64; 3], lift: f64) -> Result<(Vec<Item>, Vec<Item>)> {
    let mut items = vec![];
    let mut fluids = vec![];
    let frame = hsm_faucet::display::tip_plane(neck)?;
    let make = |solid: Solid| solid.placed(&Plane::XY, &frame);
    let p = |x: f64, s: f64, n: f64| frame.point(v2(x, s)) + frame.z * n;
    let cyl = |r: f64, s: f64, length: f64| Solid::cylinder(v3(0., s, 0.), V3::Y, r, length);
    let ring = |outer: f64, inner: f64, s: f64, length: f64| -> Result<Solid> {
        cyl(outer, s, length)?.cut(&cyl(inner, s - 0.02, length + 0.04)?)
    };
    let copper = [0.58, 0.24, 0.085];
    let polymer = [0.11, 0.13, 0.15];
    let seal = [0.12, 0.22, 0.19];
    let magnetic = [0.28, 0.31, 0.34];

    let bridge_stations = [(24.0, 3.0), (48.0, 1.2)];
    let bridge_clearance = |r: f64| -> Result<Solid> {
        Solid::union_all(&bridge_stations.iter().map(|&(s, length)| cyl(r, s, length))
            .collect::<Result<Vec<_>>>()?)
    };
    let outer_sleeve = ring(4.3, 3.7, 0., 50.5)?.cut(&bridge_clearance(4.4)?)?;
    add(&mut items, "head_valve_pressure_sleeve", steel, make(outer_sleeve));
    let inner = cyl(2.9, 0.8, 48.5)?
        .cut(&cyl(2.5, 0.7, BALANCE_PISTON_S - 0.7)?)?
        .cut(&cyl(2.0, BALANCE_PISTON_S - 0.02, LOW_CHAMBER_END - BALANCE_PISTON_S + 0.02)?)?
        .cut(&cyl(0.95, LOW_CHAMBER_END - 0.02, 1.1)?)?
        .cut(&cyl(2.6, 17.3, 32.1)?)?;
    let mut liner = inner.cut(&bridge_clearance(3.0)?)?;
    for s in [4.0, 7.0] {
        liner = liner.cut(&Solid::cylinder(v3(-4., s, 0.), V3::X, 1.0, 8.)?)?;
        liner = liner.cut(&Solid::cylinder(v3(0., s, -4.), V3::Z, 1.0, 8.)?)?;
    }
    add(&mut items, "head_valve_wet_dry_liner", steel, make(liner));
    add(&mut items, "head_valve_outlet_seat", steel, make(ring(4.3, 1.9, -1.0, 1.6)?));
    add(&mut items, "head_valve_front_retainer", polymer, make(ring(5.25, 4.35, -0.8, 1.6)?));
    add(&mut items, "head_valve_seat_lip", steel,
        make(Solid::cone(v3(0., 0.6, 0.), V3::Y, 2.1, SEAT_D / 2., 0.2)?
            .cut(&cyl(1.9, 0.5, 0.4)?)?));

    let moving = Affine::translation(v3(0., lift, 0.));
    let stem = cyl(STEM_R, 0.8, 35.3)?
        .cut(&cyl(VENT_R, 0.7, 14.4)?)?
        .cut(&Solid::cylinder(v3(-1.0, 14.9, 0.), V3::X, VENT_R, 2.)?)?;
    add(&mut items, "head_valve_hollow_poppet_stem", steel, make(stem.transformed(&moving)));
    add(&mut items, "head_valve_poppet_face", seal,
        make(ring(2.2, VENT_R, 0.8, 0.55)?.transformed(&moving)));
    add(&mut items, "head_valve_balance_piston", steel,
        make(ring(2.0, STEM_R + 0.01, BALANCE_PISTON_S, BALANCE_PISTON_LENGTH)?.transformed(&moving)));
    add(&mut items, "head_valve_balance_seal", seal,
        make(Solid::torus(v3(0., BALANCE_PISTON_S + 1.05, 0.), V3::Y, 1.74, 0.26)?.transformed(&moving)));
    add(&mut items, "head_valve_dry_rod_seal", seal,
        make(Solid::torus(v3(0., 16.8, 0.), V3::Y, 1.03, 0.23)?));
    add(&mut items, "head_valve_spring_washer", steel,
        make(ring(1.9, STEM_R + 0.03, 17.8, 0.5)?.transformed(&moving)));
    add(&mut items, "head_valve_fixed_spring_seat", steel,
        make(ring(2.55, 1.0, 23.1, 0.3)?));
    let spring_start = v3(1.75, 18.3 + lift, 0.);
    let pitch = (4.8 - lift) / 8.;
    let spring_plane = Plane::new(spring_start, V3::X, v3(0., pitch, -std::f64::consts::TAU * 1.75))?;
    let spring = spring_plane.helix_sweep(&Profile::circle(v2(0., 0.), 0.16),
        v3(0., 18.3 + lift, 0.), V3::Y, pitch, 8.)?;
    add(&mut items, "head_valve_return_spring", steel, make(spring));

    add(&mut items, "head_valve_dry_armature", magnetic,
        make(cyl(2.5, 23.5, 21.7)?.transformed(&moving)));
    let flow_spider = |s: f64, length: f64, inner_r: f64| -> Result<Solid> {
        let mut bridge = if inner_r > 0. { ring(ACTUATOR_R, inner_r, s, length)? }
            else { cyl(ACTUATOR_R, s, length)? };
        for index in 0..8 {
            let angle = index as f64 * std::f64::consts::TAU / 8.;
            let points: Vec<_> = [2.95, 3.65].into_iter().enumerate().flat_map(|(side, radius)| {
                (0..=8).map(move |j| {
                    let f = if side == 0 { j as f64 / 8. } else { 1. - j as f64 / 8. };
                    let a = angle + (f * 24. - 12.).to_radians();
                    v2(radius * a.cos(), radius * a.sin())
                })
            }).collect();
            let cut = Plane::new(v3(0., s - 0.1, 0.), V3::X, V3::Y)?
                .extrude(&Profile::polygon(&points), length + 0.2)?;
            bridge = bridge.cut(&cut)?;
        }
        Ok(bridge)
    };
    let front_spider = flow_spider(24., 3., 2.6)?;
    let rear_spider = flow_spider(48., 1.2, 0.)?.union(&cyl(2.5, 45.88, 3.32)?)?;
    add(&mut items, "head_valve_front_flux_spider", magnetic, make(front_spider.clone()));
    add(&mut items, "head_valve_fixed_pole_and_rear_spider", magnetic, make(rear_spider.clone()));
    add(&mut items, "head_valve_nonmagnetic_stop", polymer, make(ring(2.5, 1.7, 45.8, 0.08)?));
    add(&mut items, "head_valve_coil_bobbin", polymer, make(ring(4.6, 4.35, 27.0, 21.)?));
    add(&mut items, "head_valve_custom_copper_winding", copper, make(ring(6.6, 4.6, 28.0, 17.)?));
    add(&mut items, "head_valve_magnetic_return_yoke", magnetic, make(ring(ACTUATOR_R, 6.8, 24., 25.2)?));
    add(&mut items, "head_valve_pressure_rear_cap", steel, make(ring(4.3, 3.35, 50.5, 1.0)?));

    let join_u = neck.length() - 58.;
    let (join_path, join_tangent, join_normal) = neck.frame(join_u);
    let join = join_path + join_normal * shell::TUBE_SHELL_CENTER_Y;
    let backward = -join_tangent;
    let adapter_path = Path::new(p(0., 51.4, 0.)).bezier(&[
        p(0., 51.4, 0.), p(0., 55., 0.), join - backward * 2., join])?;
    let adapter = tube(&adapter_path, p(0., 51.4, 0.), frame.y, 4.3, 3.35)?;
    add(&mut items, "head_valve_curved_inlet", steel, adapter);
    let barb_plane = Plane::new(join, V3::X, backward)?;
    add(&mut items, "head_valve_integral_hose_barb", steel, annulus(barb_plane, 3.65, 3.0, 12.)?);
    for distance in [3., 7., 10.5] {
        add(&mut items, &format!("head_valve_barb_ridge_{distance}"), steel,
            Solid::torus(join + backward * distance, backward, 3.5, 0.30)?);
    }
    add(&mut items, "head_factory_hose_crimp", steel,
        annulus(barb_plane.offset(0.8), 6.3, 5.85, 4.)?);
    let joint_u = neck.at_angle(paths::JOINT_ANGLE) + JOINT_GAP / 2.;
    add(&mut items, "head_pressurized_soda_hose", [0.08, 0.33, 0.56], neck.sweep(
        &Profile::circle(v2(0., shell::TUBE_SHELL_CENTER_Y), 5.8)
            .with_hole(Loop::circle(v2(0., shell::TUBE_SHELL_CENTER_Y), 3.35)), join_u, joint_u)?);

    let fan_end = neck.length() - 70.;
    let routes = [
        ("head_flavor_a_line", 0., -3.0_f64.atan2(9.5), [0.45, 0.64, 0.19]),
        ("head_flavor_b_line", std::f64::consts::PI, std::f64::consts::PI + 3.0_f64.atan2(9.5), [0.60, 0.28, 0.64]),
        ("head_fault_drain", std::f64::consts::FRAC_PI_2, 0.5_f64.atan2(-9.5), [0.73, 0.76, 0.74]),
    ];
    for (name, start_angle, end_angle, color) in routes {
        let end_radius = if name == "head_fault_drain" { 9.513148795 } else { 9.962429423 };
        let points: Vec<_> = (0..=64).map(|i| {
            let u = joint_u + (neck.length() + 1.3 - joint_u) * i as f64 / 64.;
            let f = ((u - joint_u) / (fan_end - joint_u)).clamp(0., 1.);
            let f = f * f * (3. - 2. * f);
            let angle = start_angle + (end_angle - start_angle) * f;
            let radius = 7.3 + (end_radius - 7.3) * f;
            let (point, _, normal) = neck.frame(u);
            point + V3::X * (radius * angle.cos())
                + normal * (shell::TUBE_SHELL_CENTER_Y + radius * angle.sin())
        }).collect();
        let path = Path::new(points[0]).spline_through(&points)?;
        add(&mut items, name, color, tube(&path, points[0], points[1] - points[0], 1.5, 1.0)?);
    }

    let cable_points = [p(4.5, 48.5, 6.0), p(7.5, 55., 2.0), p(7.0, 65., -5.),
        p(5.0, 84., -25.), p(0., 100., -47.)];
    let power_path = Path::new(cable_points[0]).spline_through(&cable_points)?;
    add(&mut items, "head_valve_fly_leads", [0.62, 0.18, 0.12],
        route(&power_path, cable_points[0], cable_points[1] - cable_points[0], 0.7)?);
    let flex_path = Path::new(p(0., 22., 8.1)).bezier(&[
        p(0., 22., 8.1), p(0., 42., 8.1), p(0., 47., 8.1), p(4.5, 48.5, 6.0)])?;
    add(&mut items, "head_signal_and_valve_flex", [0.24, 0.23, 0.19],
        Plane::new(p(0., 22., 8.1), V3::X, frame.y)?
            .sweep(&Profile::rect(v2(0., 0.), 5., 0.6), &flex_path)?);

    let hp_annulus = ring(3.7, 2.9, 1.0, 49.4)?.cut(&front_spider)?.cut(&rear_spider)?;
    let hp_core = cyl(2.5, 1.4 + lift, BALANCE_PISTON_S - 1.4)?
        .cut(&cyl(STEM_R, 1.0, BALANCE_PISTON_S + lift)?)?;
    add(&mut fluids, "fluid_high_pressure_annulus", [0.06, 0.40, 0.68], make(hp_annulus));
    add(&mut fluids, "fluid_high_pressure_seat_chamber", [0.06, 0.40, 0.68], make(hp_core));
    add(&mut fluids, "fluid_low_pressure_balance_chamber", [0.12, 0.72, 0.70],
        make(ring(2.0, STEM_R, BALANCE_PISTON_S + BALANCE_PISTON_LENGTH + lift,
            LOW_CHAMBER_END - BALANCE_PISTON_S - BALANCE_PISTON_LENGTH - lift)?));
    Ok((items, fluids))
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
    let neck = Gooseneck::shell();
    let tip_plane = hsm_faucet::display::tip_plane(&neck)?;
    let original_tip_plane = tip_plane;
    let joint = neck.at_angle(paths::JOINT_ANGLE);
    let round = v2(0., shell::TUBE_SHELL_CENTER_Y);
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
    let head_profile = Profile::circle(round, HEAD_R).with_hole(Loop::circle(round, HEAD_BORE_R));
    let mut tip = neck.sweep(&head_profile, joint + JOINT_GAP / 2., neck.length() + 1.2)?;
    let (valve, fluids) = custom_valve(&neck, steel, 0.)?;
    let (open_valve, open_fluids) = custom_valve(&neck, steel, VALVE_LIFT)?;
    let display_shift = Affine::translation(tip_plane.z * DISPLAY_LIFT);
    let screen_center = body("faucet_display_screen")?.transformed(&display_shift).bounds().center();
    let (screen_xy, screen_n) = tip_plane.local(screen_center);
    let window = tip_plane.offset(6.5).shifted(screen_xy).extrude(
        &Profile::new(Loop::rounded_rect(v2(0., 0.), 25.4, 46., 2.0)?), 30.)?;
    tip = tip.cut(&window)?;
    let plinth_profile = Profile::new(Loop::rounded_rect(v2(0., 0.), 28., 49., 4.5)?)
        .with_hole(Loop::rounded_rect(v2(0., 0.), 25.4, 46., 2.0)?);
    tip = tip.union(&tip_plane.offset(6.5).shifted(screen_xy)
        .extrude(&plinth_profile, screen_n - 7.5)?)?;
    let bezel = tip_plane.offset(screen_n - 1.0).shifted(screen_xy).extrude(
        &Profile::new(Loop::rounded_rect(v2(0., 0.), 28., 49., 4.5)?)
            .with_hole(Loop::rounded_rect(v2(0., 0.), 18.3, 33.3, 1.8)?), 1.3)?;
    let cap_plane = Plane::new(tip_plane.point(v2(0., -1.2)) + tip_plane.z * round.y, V3::X, tip_plane.y)?;
    let mut nose = cap_plane.extrude(&Profile::circle(v2(0., 0.), HEAD_R), 1.8)?;
    for (x, n, r) in [(0., 0., 4.4), (9.5, round.y - 3., 1.6),
        (-9.5, round.y - 3., 1.6), (-9.5, round.y + 0.5, 1.6)] {
        let hole = Solid::cylinder(v3(x, -1.4, n), V3::Y, r, 2.3)?.placed(&Plane::XY, &tip_plane);
        nose = nose.cut(&hole)?;
    }
    tip = tip.union(&nose)?.cut(&bezel)?;
    let actuator_relief = Solid::cylinder(v3(0., 23.5, 0.), V3::Y, 7.75, 26.3)?
        .placed(&Plane::XY, &tip_plane);
    tip = tip.cut(&actuator_relief)?;
    let collar_relief = Solid::cylinder(v3(0., -0.9, 0.), V3::Y, 5.35, 1.7)?
        .placed(&Plane::XY, &tip_plane);
    tip = tip.cut(&collar_relief)?;
    println!("Custom shell tip-frame bounds {:?}", tip.union(&bezel)?.placed(&tip_plane, &Plane::XY).bounds());
    let pi = std::f64::consts::PI;
    let seat_area = pi * SEAT_D.powi(2) / 4.;
    let outlet_volume = pi * 1.9_f64.powi(2) * 1.8;
    let balance_volume = pi * (2.0_f64.powi(2) - STEM_R.powi(2))
        * (LOW_CHAMBER_END - BALANCE_PISTON_S - BALANCE_PISTON_LENGTH);
    let vent_volume = pi * VENT_R.powi(2) * (14.1 + 2.0);
    let gland_volume = pi * (0.95_f64.powi(2) - STEM_R.powi(2));
    let spring_rate = 77_000. * 0.32_f64.powi(4) / (8. * 3.5_f64.powi(3) * 6.);
    let residual_force = 1.6 * pi / 4. * ((SEAT_D + 0.02).powi(2) - SEAT_D.powi(2));
    let opening_load = 1.2 + spring_rate * VALVE_LIFT + 0.5 + 0.15 + 0.25 + residual_force;
    let winding_length = 600. * pi * 11.2 / 1000.;
    let resistance = 0.01724 * winding_length / 0.0201;
    let turn_capacity_fill = 600. * 0.0201 / ((6.6 - 4.6) * 17.);
    let face_height = tip_plane.point(v2(0., -1.)).z;
    let original_bounds = body("shell_base")?.union(body("shell_tip")?)?.bounds();
    let custom_bounds = stem.union(&tip)?.union(&bezel)?.bounds();
    let design = serde_json::json!({
        "purpose": "This record owns the custom valve's geometry and first-order design budgets for the slim pull-out faucet.",
        "date": "2026-11-18",
        "state": "Proposed end-state mechanism and packaging; performance values below are requirements or first-order estimates, not qualified hardware ratings.",
        "geometry": {
            "stem_od_mm": NECK_R * 2., "stem_sliding_bore_mm": BORE_R * 2.,
            "head_nominal_od_mm": HEAD_R * 2.,
            "head_front_depth_at_display_mm": HEAD_R * 2.
                + (screen_n + 0.3 - round.y - HEAD_R).max(0.),
            "bundle_envelope_od_mm": BUNDLE_R * 2.,
            "actuator_od_mm": ACTUATOR_R * 2., "actuator_length_mm": 25.2,
            "pressure_sleeve_od_mm": 8.6, "effective_seat_and_balance_diameter_mm": SEAT_D,
            "seat_flow_bore_mm": 3.8, "opening_lift_mm": VALVE_LIFT,
            "seat_to_outlet_mm": 1.8, "display_outward_shift_mm": DISPLAY_LIFT,
            "flavor_and_drain_tube_od_mm": 3., "flavor_tube_id_mm": 2.,
            "main_hose_od_mm": 11.6, "main_hose_id_mm": 6.7,
            "docked_water_outlet_center_height_mm": face_height,
            "reference_shell_max_z_mm": original_bounds.max.z,
            "custom_shell_max_z_mm": custom_bounds.max.z
        },
        "hydraulic_targets_and_estimates": {
            "working_pressure_target_bar": 16., "pour_target_l_min": [1.5, 2.0],
            "unbalanced_seat_force_at_pressure_target_n": 1.6 * seat_area,
            "effective_diameter_match_allowance_mm": 0.02,
            "residual_pressure_force_allowance_n": residual_force,
            "curtain_area_mm2": pi * SEAT_D * VALVE_LIFT,
            "seat_only_drop_bar_at_2_l_min_assuming_cd_0_65":
                (2. / 60000. / (0.65 * pi * SEAT_D * VALVE_LIFT * 1e-6)).powi(2) * 1000. / 2. / 100000.,
            "nominal_outlet_connected_liquid_volume_mm3": outlet_volume + balance_volume + vent_volume + gland_volume,
            "volume_scope": "Outlet bore, small wet balance chamber, hollow stem and rod-gland clearance. Seal grooves and films are not included. The armature and return spring occupy a separate dry chamber."
        },
        "actuator_targets_and_estimates": {
            "architecture": "Spring-closed pull solenoid, matched pressure areas, closed magnetic circuit with flow-through flux spiders and an anti-remanence stop.",
            "coil_turns": 600, "bare_wire_area_mm2": 0.0201,
            "winding_copper_fill_estimate": turn_capacity_fill,
            "cold_coil_resistance_estimate_ohm": resistance,
            "peak_current_target_a": 0.9, "peak_duration_target_ms": 30.,
            "hold_current_target_a": 0.18,
            "cold_hold_copper_loss_estimate_w": 0.18_f64.powi(2) * resistance,
            "cold_peak_copper_loss_estimate_w": 0.9_f64.powi(2) * resistance,
            "driver": "Current-regulated peak and hold with an enclosure-side boost rail; power off releases the return spring.",
            "drive_rail_target_v": 24., "pull_force_requirement_n_at_full_stroke": 4.,
            "spring_preload_target_n": 1.2, "spring_rate_estimate_n_mm": spring_rate,
            "wet_seal_friction_allowance_n": 0.5, "dry_rod_seal_friction_allowance_n": 0.15,
            "flow_force_allowance_n": 0.25, "full_stroke_opening_load_budget_n": opening_load,
            "force_margin_target": 4. / opening_load,
            "qualification": "Magnetic finite-element analysis, seal friction, force versus stroke and temperature, closure, carbonation and life remain engineering work."
        },
        "materials_and_process": {
            "wet_pressure_tubes_and_seat": "Precision-turned and laser-joined stainless steel; smooth outlet seat.",
            "flux_bridges": "Passivated magnetic stainless, with axial water passages and sealed interfaces to the dry armature bore.",
            "dynamic_seals": "Food-contact compound to be specified; low-friction piston seal and a separate low-pressure rod seal.",
            "coil": "Custom winding on an insulated bobbin, protected inside its magnetic return yoke.",
            "inlet": "Integral angled barb and factory crimp; no exposed disconnect at the docking seam.",
            "bundle": "Reinforced beverage hose, smaller separate flavor and drain lines, flexible conductors, a thin insulating layer and continuous protective sleeve."
        },
        "architecture_reference": "https://patents.google.com/patent/EP1597501A1/en",
        "reference_scope": "The pressure-balancing architecture is established. The reference does not validate this geometry, food service, magnetic design or performance."
    });
    std::fs::write(dir.join("custom-valve-design.json"), serde_json::to_string_pretty(&design)? + "\n")?;

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
            annulus(heel_plane.offset(-9.), 11.2, BUNDLE_R - 0.2, 14.)?.transformed(&pose));
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
        if !pulled {
            let mut comparison = vec![];
            let left = Affine::translation(v3(-76., -57., 0.));
            let right = Affine::translation(v3(76., 57., 0.));
            for name in ["shell_base", "shell_tip", "lever", "faucet-display-cover-seated", "faucet_display", "faucet_display_screen"] {
                add(&mut comparison, &format!("original_{name}"), black, body(name)?.transformed(&left));
            }
            for (name, color, solid) in &scene {
                if name == "countertop" { continue; }
                add(&mut comparison, &format!("custom_{name}"), *color, solid.transformed(&right));
                if name.starts_with("screen_") {
                    add(&mut comparison, &format!("original_{name}"), *color,
                        solid.transformed(&Affine::translation(-tip_plane.z * DISPLAY_LIFT)).transformed(&left));
                }
            }
            let stage = Solid::cuboid(v3(-180., -230., -12.), v3(220., 130., 0.));
            add(&mut comparison, "comparison_counter", [0.57, 0.56, 0.53], stage);
            for (text, x, y) in [("CURRENT", -76., -127.), ("CUSTOM VALVE", 76., -13.)] {
                add(&mut comparison, &format!("label_{text}"), [0.05, 0.055, 0.055],
                    Plane::XY.at(v3(x, y, 0.1)).text(&font, text, 7., 0.12, HAlign::Center, VAlign::Center)?);
            }
            write(&dir, "profile-comparison", &comparison)?;
        }
        if pulled {
            scene.retain(|(name, _, _)| name.starts_with("head_") || name.starts_with("screen_")
                || ["pull_off_curved_grip", "soft_hose_strain_relief"].contains(&name.as_str()));
            write(&dir, "handheld-detail", &scene)?;
            let mut cutaway = scene.clone();
            let removed_half = Solid::cuboid(v3(0., -120., -100.), v3(150., 160., 130.))
                .placed(&Plane::XY, &tip_plane).transformed(&pose);
            for (name, _, solid) in &mut cutaway {
                if name == "pull_off_curved_grip" || ["head_valve_pressure_sleeve", "head_valve_wet_dry_liner",
                    "head_valve_outlet_seat", "head_valve_front_retainer", "head_valve_coil_bobbin",
                    "head_valve_custom_copper_winding", "head_valve_magnetic_return_yoke",
                    "head_valve_front_flux_spider", "head_valve_fixed_pole_and_rear_spider"]
                    .contains(&name.as_str()) { *solid = solid.cut(&removed_half)?; }
            }
            write(&dir, "head-valve-cutaway", &cutaway)?;
            let section_cut = Solid::cuboid(v3(0., -4., -20.), v3(30., 90., 25.))
                .placed(&Plane::XY, &tip_plane);
            let sectioned = |parts: &[Item], fluid_parts: &[Item]| -> Result<Vec<Item>> {
                let mut output = vec![];
                for (name, color, solid) in parts {
                    if !name.starts_with("head_valve_") || name == "head_valve_fly_leads" { continue; }
                    let s = if ["head_valve_pressure_sleeve", "head_valve_wet_dry_liner", "head_valve_outlet_seat",
                        "head_valve_front_retainer", "head_valve_seat_lip", "head_valve_coil_bobbin",
                        "head_valve_custom_copper_winding", "head_valve_magnetic_return_yoke",
                        "head_valve_front_flux_spider", "head_valve_fixed_pole_and_rear_spider", "head_valve_pressure_rear_cap"]
                        .contains(&name.as_str()) { solid.cut(&section_cut)? } else { solid.clone() };
                    add(&mut output, name, *color, s.placed(&tip_plane, &Plane::XY)
                        .placed(&Plane::new(V3::ZERO, V3::X, V3::Y)?, &Plane::XY));
                }
                for (name, color, solid) in fluid_parts {
                    add(&mut output, name, *color, solid.cut(&section_cut)?.placed(&tip_plane, &Plane::XY)
                        .placed(&Plane::new(V3::ZERO, V3::X, V3::Y)?, &Plane::XY));
                }
                Ok(output)
            };
            write(&dir, "custom-valve-closed", &sectioned(&valve, &fluids)?)?;
            write(&dir, "custom-valve-open", &sectioned(&open_valve, &open_fluids)?)?;

        }
        println!("{overview_name}: exposed bundle {outside_length:.1} mm; loop bottom {bottom:.1} mm");
    }
    Ok(())
}
