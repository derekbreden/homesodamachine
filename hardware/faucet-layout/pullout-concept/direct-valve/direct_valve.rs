//! This study draws a one-moving-part shutoff valve inside the pull-out faucet head.
use anyhow::Result;
use hsm_faucet::Gooseneck;
use hsm_kernel::{Affine, Font, HAlign, Kind, Path, Plane, Profile, Solid, V3, VAlign, v2, v3};
use hsm_sandbox::{material, out, part, show};
use std::f64::consts::{PI, TAU};

#[allow(dead_code)]
#[path = "../../../assembly/calibration_inputs.rs"]
mod calibration_inputs;

type Item = (String, [f64; 3], Solid);

// Stations run along the valve axis from the tip frame's origin toward the hose. Radii are about that axis.
const FACE_S: f64 = -1.0;
const SEAT_BORE_R: f64 = 1.5;
const LIP_CREST_R: f64 = 1.75;
const LIP_BASE_R: f64 = 2.15;
const INSERT_REAR_S: f64 = 5.2;
const SEAL_S: f64 = 5.6;
const INSERT_THREAD_R: f64 = 4.5;
const INSERT_THREAD_END_S: f64 = 3.0;
const INSERT_PILOT_R: f64 = 3.98;
const LIFT: f64 = 0.7;
const STOP_SHIM: f64 = 0.1;

const NOSE_FRONT_S: f64 = -0.6;
const NOSE_R: f64 = 6.0;
const NOSE_PILOT_BORE_R: f64 = 4.0;
const CHAMBER_R: f64 = 3.7;
const TUBE_START_S: f64 = 7.0;
const NOSE_REAR_S: f64 = 11.5;
const CUP_THREAD_R: f64 = 6.95;

const TUBE_OUTER_R: f64 = 3.97;
const TUBE_WALL: f64 = 0.254;
const ORING_POCKET_R: f64 = 4.775;
const ORING_POCKET_DEPTH: f64 = 1.3;
const ORING_DRAWN_R: f64 = 0.4;
const ORING_SECTION: f64 = 1.0;

const WASHER_LENGTH: f64 = 3.0;
const WASHER_BORE_R: f64 = 4.0;
const DRY_STACK_R: f64 = 6.63;
const BOBBIN_LENGTH: f64 = 17.5;
const BOBBIN_BORE_R: f64 = 4.05;
const BOBBIN_FLANGE: f64 = 0.5;
const WINDING_INNER_R: f64 = 4.4;
const WINDING_OUTER_R: f64 = 6.55;

const POLE_FLANGE_S: f64 = 32.2;
const POLE_FLANGE_LENGTH: f64 = 3.0;
const POLE_FACE_S: f64 = 26.5;
const POLE_SPIGOT_R: f64 = 3.69;
const POLE_BORE_R: f64 = 1.5;
const INLET_TAPER_S: [f64; 2] = [34.0, 38.0];
const INLET_R: [f64; 2] = [4.3, 3.35];
const INLET_END_S: f64 = 51.5;

const PLUNGER_R: f64 = 3.65;
const PLUNGER_NOSE_R: f64 = 2.6;
const PLUNGER_SHOULDER_S: f64 = 10.8;
const PLUNGER_FRONT_S: f64 = 5.7;
const PLUG_R: f64 = 2.1;
const PLUG_NECK_R: f64 = 1.9;
const PLUG_LIP_S: f64 = 5.95;
const PLUG_POCKET_END_S: f64 = 7.2;
const SPRING_POCKET_R: f64 = 2.1;
const SPRING_POCKET_S: f64 = 18.7;
const PLUNGER_BORE_END_S: f64 = 8.6;
const CROSS_HOLE_R: f64 = 1.0;
const CROSS_HOLE_S: f64 = 9.6;
const CROSS_HOLES: usize = 3;

const SPRING_MEAN_R: f64 = 1.8;
const SPRING_WIRE_R: f64 = 0.2;
const SPRING_COILS: f64 = 9.0;
const SPRING_ACTIVE_COILS: f64 = 7.0;
const SPRING_PRELOAD_N: f64 = 1.5;
const SPRING_SHEAR_MODULUS_MPA: f64 = 69_000.0;

const CUP_R: f64 = 7.25;
const CUP_INNER_R: f64 = 6.65;
const CUP_REAR_WALL: f64 = 1.5;
const CUP_STEM_HOLE_R: f64 = 4.35;
const LEAD_HOLE: [f64; 2] = [4.0, 3.5];

const WINDING_FILL: f64 = 0.55;
const WINDING_TURNS: f64 = 380.0;
const WIRE_AREA_MM2: f64 = 0.0509;
const SUPPLY_V: f64 = 12.0;
const LEAD_RESISTANCE_OHM: f64 = 0.5;
const COPPER_RESISTIVITY_OHM_MM: f64 = 1.724e-5;
const FLUX_REACHING_GAP: f64 = 0.85;
const HOLD_MARGIN: f64 = 2.0;
const SLIDING_FRICTION_ALLOWANCE_N: f64 = 0.3;
const MU0: f64 = 4.0e-7 * PI;
// The relief valve's setting is in the pressure vessel's page and the Lillium's inlet range in the pour model's.
const RELIEF_VALVE_PSI: f64 = 125.0;
const LILLIUM_INLET_MPA: [f64; 2] = [0.45, 0.55];

fn cyl(r: f64, s: f64, length: f64) -> Result<Solid> {
    Solid::cylinder(v3(0., s, 0.), V3::Y, r, length)
}

fn ring(outer: f64, inner: f64, s: f64, length: f64) -> Result<Solid> {
    cyl(outer, s, length)?.cut(&cyl(inner, s - 0.02, length + 0.04)?)
}

/// A turned part from its half section, as radius and station pairs.
fn turned(section: &[(f64, f64)]) -> Result<Solid> {
    let points: Vec<_> = section.iter().map(|&(r, s)| v2(r, s)).collect();
    Plane::XY.revolve(&Profile::polygon(&points), 360., v2(0., 0.), v2(0., 1.))
}

fn add(items: &mut Vec<Item>, name: &str, color: [f64; 3], solid: Solid) {
    items.push((name.into(), color, solid));
}

/// The annealed magnetic stainless's field strength for a flux density, read off a coarse curve.
fn iron_h(b: f64) -> f64 {
    let curve = [(0.0, 0.0), (0.6, 220.0), (1.0, 480.0), (1.2, 1000.0), (1.3, 2000.0), (1.4, 4500.0), (1.5, 9000.0), (1.6, 20000.0)];
    for pair in curve.windows(2) {
        if b <= pair[1].0 { return pair[0].1 + (pair[1].1 - pair[0].1) * (b - pair[0].0) / (pair[1].0 - pair[0].0); }
    }
    curve[curve.len() - 1].1 + (b - 1.6) * 100_000.0
}

struct Magnetics { gap_area: f64, cup_area: f64, radial_reluctance: f64, core_path: f64, cup_path: f64 }

impl Magnetics {
    /// The ampere-turns that drive `flux` webers across a working gap of `gap` millimetres.
    fn ampere_turns(&self, flux: f64, gap: f64) -> f64 {
        let air = flux * (gap * 1e-3 / (MU0 * self.gap_area * 1e-6) + self.radial_reluctance);
        let core = iron_h(flux / (self.gap_area * 1e-6)) * self.core_path * 1e-3;
        let shell = iron_h(flux / (self.cup_area * 1e-6)) * self.cup_path * 1e-3;
        air + core + shell
    }

    /// The pull on the plunger at `gap` millimetres under `ampere_turns`, with the leakage share removed.
    fn pull(&self, ampere_turns: f64, gap: f64) -> (f64, f64) {
        let (mut low, mut high) = (0.0, 1.7 * self.gap_area * 1e-6);
        for _ in 0..60 {
            let mid = (low + high) / 2.;
            if self.ampere_turns(mid, gap) < ampere_turns { low = mid } else { high = mid }
        }
        let b = FLUX_REACHING_GAP * low / (self.gap_area * 1e-6);
        (b, b * b * self.gap_area * 1e-6 / (2. * MU0))
    }
}

/// The valve in its own frame: the fixed and moving pieces, then the water, with the plunger `lift` off its seat.
fn valve(lift: f64, steel: [f64; 3]) -> Result<(Vec<Item>, Vec<Item>)> {
    let mut items = vec![];
    let mut fluids = vec![];
    let magnetic = [0.28, 0.31, 0.34];
    let moving_steel = [0.72, 0.60, 0.36];
    let seat_steel = [0.55, 0.58, 0.61];
    let copper = [0.58, 0.24, 0.085];
    let polymer = [0.11, 0.13, 0.15];
    let rubber = [0.12, 0.22, 0.19];
    let tube_inner = TUBE_OUTER_R - TUBE_WALL;
    let washer_s = NOSE_REAR_S;
    let bobbin_s = washer_s + WASHER_LENGTH;
    let tube_end_s = POLE_FLANGE_S + ORING_POCKET_DEPTH;
    let cup_rear_s = POLE_FLANGE_S + POLE_FLANGE_LENGTH;

    let mut insert = turned(&[
        (SEAT_BORE_R + 0.3, FACE_S), (SEAT_BORE_R, FACE_S + 0.3), (SEAT_BORE_R, SEAL_S), (LIP_CREST_R, SEAL_S),
        (LIP_BASE_R, INSERT_REAR_S), (INSERT_PILOT_R, INSERT_REAR_S), (INSERT_PILOT_R, 4.7), (3.2, 4.7), (3.2, 3.4),
        (INSERT_PILOT_R, 3.4), (INSERT_PILOT_R, INSERT_THREAD_END_S), (INSERT_THREAD_R, INSERT_THREAD_END_S),
        (INSERT_THREAD_R, FACE_S),
    ])?;
    for x in [-3.1, 3.1] {
        insert = insert.cut(&Solid::cylinder(v3(x, FACE_S - 0.1, 0.), V3::Y, 0.6, 1.6)?)?;
    }
    add(&mut items, "head_valve_seat_insert", seat_steel, insert.clone());
    add(&mut items, "head_valve_seat_oring", rubber, Solid::torus(v3(0., 4.05, 0.), V3::Y, 3.6, ORING_DRAWN_R)?);

    add(&mut items, "head_valve_nose", steel, turned(&[
        (INSERT_THREAD_R, NOSE_FRONT_S), (NOSE_R, NOSE_FRONT_S), (NOSE_R, TUBE_START_S), (CUP_THREAD_R, TUBE_START_S),
        (CUP_THREAD_R, NOSE_REAR_S), (ORING_POCKET_R, NOSE_REAR_S), (ORING_POCKET_R, NOSE_REAR_S - ORING_POCKET_DEPTH),
        (TUBE_OUTER_R + 0.02, NOSE_REAR_S - ORING_POCKET_DEPTH), (TUBE_OUTER_R + 0.02, TUBE_START_S),
        (CHAMBER_R, TUBE_START_S), (CHAMBER_R, SEAL_S), (NOSE_PILOT_BORE_R, SEAL_S),
        (NOSE_PILOT_BORE_R, INSERT_THREAD_END_S), (INSERT_THREAD_R, INSERT_THREAD_END_S),
    ])?);
    let oring_major = (TUBE_OUTER_R + ORING_POCKET_R) / 2.;
    add(&mut items, "head_valve_tube_front_oring", rubber,
        Solid::torus(v3(0., NOSE_REAR_S - ORING_POCKET_DEPTH / 2., 0.), V3::Y, oring_major, ORING_DRAWN_R)?);
    add(&mut items, "head_valve_plunger_tube", [0.62, 0.65, 0.68],
        ring(TUBE_OUTER_R, tube_inner, TUBE_START_S, tube_end_s - TUBE_START_S)?);
    add(&mut items, "head_valve_flux_washer", magnetic, ring(DRY_STACK_R, WASHER_BORE_R, washer_s, WASHER_LENGTH)?);
    let bobbin_end = bobbin_s + BOBBIN_LENGTH;
    add(&mut items, "head_valve_coil_bobbin", polymer, turned(&[
        (BOBBIN_BORE_R, bobbin_s), (WINDING_OUTER_R + 0.05, bobbin_s), (WINDING_OUTER_R + 0.05, bobbin_s + BOBBIN_FLANGE),
        (WINDING_INNER_R, bobbin_s + BOBBIN_FLANGE), (WINDING_INNER_R, bobbin_end - BOBBIN_FLANGE),
        (WINDING_OUTER_R + 0.05, bobbin_end - BOBBIN_FLANGE), (WINDING_OUTER_R + 0.05, bobbin_end), (BOBBIN_BORE_R, bobbin_end),
    ])?);
    add(&mut items, "head_valve_copper_winding", copper, ring(WINDING_OUTER_R, WINDING_INNER_R,
        bobbin_s + BOBBIN_FLANGE, BOBBIN_LENGTH - 2. * BOBBIN_FLANGE)?);
    add(&mut items, "head_valve_tube_rear_oring", rubber,
        Solid::torus(v3(0., POLE_FLANGE_S + ORING_POCKET_DEPTH / 2., 0.), V3::Y, oring_major, ORING_DRAWN_R)?);
    add(&mut items, "head_valve_pole_and_inlet", magnetic, turned(&[
        (POLE_BORE_R, POLE_FACE_S), (POLE_SPIGOT_R, POLE_FACE_S), (POLE_SPIGOT_R, tube_end_s),
        (ORING_POCKET_R, tube_end_s), (ORING_POCKET_R, POLE_FLANGE_S), (DRY_STACK_R, POLE_FLANGE_S),
        (DRY_STACK_R, cup_rear_s), (INLET_R[0], cup_rear_s), (INLET_R[0], INLET_END_S), (INLET_R[1], INLET_END_S),
        (INLET_R[1], INLET_TAPER_S[1]), (POLE_BORE_R, INLET_TAPER_S[0]),
    ])?);
    add(&mut items, "head_valve_stop_shim", [0.74, 0.70, 0.52],
        ring(PLUNGER_R - 0.05, POLE_BORE_R, POLE_FACE_S - STOP_SHIM, STOP_SHIM)?);
    let lead_hole = Solid::cylinder(v3(LEAD_HOLE[0], cup_rear_s - 0.1, LEAD_HOLE[1]), V3::Y, 1.0, CUP_REAR_WALL + 0.2)?;
    add(&mut items, "head_valve_yoke_cup", magnetic, turned(&[
        (CUP_THREAD_R, TUBE_START_S), (CUP_R, TUBE_START_S), (CUP_R, cup_rear_s + CUP_REAR_WALL),
        (CUP_STEM_HOLE_R, cup_rear_s + CUP_REAR_WALL), (CUP_STEM_HOLE_R, cup_rear_s), (CUP_INNER_R, cup_rear_s),
        (CUP_INNER_R, NOSE_REAR_S), (CUP_THREAD_R, NOSE_REAR_S),
    ])?.cut(&lead_hole)?);
    let lead_start = v3(LEAD_HOLE[0], bobbin_end - 0.2, LEAD_HOLE[1]);
    let lead_points = [lead_start, v3(LEAD_HOLE[0], cup_rear_s + 4., LEAD_HOLE[1]), v3(4.3, 47.6, 5.5)];
    let lead_path = Path::new(lead_start).spline_through(&lead_points)?;
    add(&mut items, "head_valve_coil_leads", [0.62, 0.18, 0.12], Plane::new(lead_start, V3::X, V3::Y)?
        .sweep(&Profile::circle(v2(0., 0.), 0.6), &lead_path)?);

    let moving = Affine::translation(v3(0., lift, 0.));
    let plunger_rear_s = POLE_FACE_S - STOP_SHIM - LIFT;
    let mut plunger = cyl(PLUNGER_NOSE_R, PLUNGER_FRONT_S, PLUNGER_SHOULDER_S - PLUNGER_FRONT_S)?
        .union(&cyl(PLUNGER_R, PLUNGER_SHOULDER_S, plunger_rear_s - PLUNGER_SHOULDER_S)?)?
        .cut(&cyl(SPRING_POCKET_R, SPRING_POCKET_S, plunger_rear_s - SPRING_POCKET_S + 0.1)?)?
        .cut(&cyl(POLE_BORE_R, PLUNGER_BORE_END_S, SPRING_POCKET_S - PLUNGER_BORE_END_S + 0.1)?)?
        .cut(&cyl(PLUG_R, PLUG_LIP_S, PLUG_POCKET_END_S - PLUG_LIP_S)?)?
        .cut(&cyl(PLUG_NECK_R + 0.05, PLUNGER_FRONT_S - 0.1, PLUG_LIP_S - PLUNGER_FRONT_S + 0.2)?)?;
    for index in 0..CROSS_HOLES {
        let angle = TAU * (index as f64 / CROSS_HOLES as f64 + 0.25);
        let out = v3(angle.cos(), 0., angle.sin());
        plunger = plunger.cut(&Solid::cylinder(v3(0., CROSS_HOLE_S, 0.), out, CROSS_HOLE_R, PLUNGER_NOSE_R + 0.5)?)?;
    }
    let plunger = plunger.transformed(&moving);
    let plug = cyl(PLUG_R, PLUG_LIP_S, PLUG_POCKET_END_S - PLUG_LIP_S)?
        .union(&cyl(PLUG_NECK_R, SEAL_S, PLUG_LIP_S - SEAL_S + 0.02)?)?.transformed(&moving);
    add(&mut items, "head_valve_plunger", moving_steel, plunger.clone());
    add(&mut items, "head_valve_rubber_plug", rubber, plug.clone());
    let spring_start = SPRING_POCKET_S + SPRING_WIRE_R + lift;
    let spring_length = POLE_FACE_S - STOP_SHIM - SPRING_WIRE_R - spring_start;
    let pitch = spring_length / SPRING_COILS;
    let spring_plane = Plane::new(v3(SPRING_MEAN_R, spring_start, 0.), V3::X, v3(0., pitch, -TAU * SPRING_MEAN_R))?;
    add(&mut items, "head_valve_return_spring", steel, spring_plane.helix_sweep(
        &Profile::circle(v2(0., 0.), SPRING_WIRE_R), v3(0., spring_start, 0.), V3::Y, pitch, SPRING_COILS)?);

    let shim_face_s = POLE_FACE_S - STOP_SHIM;
    let wet = cyl(NOSE_PILOT_BORE_R, INSERT_REAR_S, SEAL_S - INSERT_REAR_S)?
        .union(&cyl(CHAMBER_R, SEAL_S - 0.02, TUBE_START_S - SEAL_S + 0.04)?)?
        .union(&cyl(tube_inner, TUBE_START_S, shim_face_s - TUBE_START_S)?)?
        .union(&cyl(POLE_BORE_R, shim_face_s - 0.02, INLET_TAPER_S[0] - shim_face_s + 0.04)?)?
        .union(&Solid::cone(v3(0., INLET_TAPER_S[0], 0.), V3::Y, POLE_BORE_R, INLET_R[1],
            INLET_TAPER_S[1] - INLET_TAPER_S[0])?)?
        .union(&cyl(INLET_R[1], INLET_TAPER_S[1] - 0.02, INLET_END_S - INLET_TAPER_S[1] + 0.02)?)?;
    let film = ring(tube_inner + 0.02, PLUNGER_R - 0.05, PLUNGER_SHOULDER_S + lift, plunger_rear_s - PLUNGER_SHOULDER_S)?;
    let mut supply = wet.cut(&insert)?.cut(&plunger)?.cut(&plug)?.cut(&film)?;
    if lift == 0. {
        supply = supply.cut(&cyl(SEAT_BORE_R, INSERT_REAR_S - 0.05, SEAL_S - INSERT_REAR_S + 0.05)?)?;
    } else {
        add(&mut fluids, "fluid_pouring_through_outlet", [0.12, 0.72, 0.70],
            cyl(SEAT_BORE_R, FACE_S - 3., INSERT_REAR_S - FACE_S + 3.)?);
    }
    add(&mut fluids, "fluid_at_supply_pressure", [0.06, 0.40, 0.68], supply);
    Ok((items, fluids))
}

fn write(dir: &std::path::Path, name: &str, items: &[Item]) -> Result<()> {
    let refs: Vec<_> = items.iter().map(|(name, color, solid)| (name.as_str(), *color, solid)).collect();
    show(dir, name, &refs)
}

/// The pieces a section leaves whole.
fn stays_whole(name: &str) -> bool {
    ["head_valve_return_spring", "head_valve_coil_leads"].contains(&name)
}

fn main() -> Result<()> {
    let dir = out()?;
    let steel = material("M_STAINLESS")?;
    let neck = Gooseneck::shell();
    let frame = hsm_faucet::display::tip_plane(&neck)?;
    let head = part("faucet-layout/pullout-concept/docked-above-counter.step")?;
    let (closed, closed_water) = valve(0., steel)?;
    let (open, open_water) = valve(LIFT, steel)?;

    // The concept's hose end joins this valve's inlet: its elbow, barb, crimp and hose are shown as they are.
    let kept_inlet = |name: &str| ["head_valve_curved_inlet", "head_valve_integral_hose_barb", "head_factory_hose_crimp"]
        .contains(&name) || name.starts_with("head_valve_barb_ridge_");
    let near_half = Solid::cuboid(v3(0., -6., -25.), v3(40., 95., 30.));
    let upright = Plane::new(V3::ZERO, V3::X, V3::Y)?;
    let section = |pieces: &[Item], water: &[Item]| -> Result<Vec<Item>> {
        let mut output = vec![];
        for (name, color, solid) in pieces.iter().chain(water) {
            if name == "head_valve_coil_leads" { continue; }
            let shown = if stays_whole(name) { solid.clone() } else { solid.cut(&near_half)? };
            add(&mut output, name, *color, shown.placed(&upright, &Plane::XY));
        }
        for body in head.iter().filter(|body| kept_inlet(&body.name)) {
            add(&mut output, &body.name.replace("head_valve_", "head_inlet_"), body.color.unwrap_or(steel),
                body.solid.placed(&frame, &Plane::XY).placed(&upright, &Plane::XY));
        }
        Ok(output)
    };
    write(&dir, "direct-valve-closed", &section(&closed, &closed_water)?)?;
    write(&dir, "direct-valve-open", &section(&open, &open_water)?)?;

    // Each piece on its own, in the order it goes together, with the plunger's pieces on the upper row.
    let font = Font::find("Helvetica Neue", Kind::Regular)?;
    let rows: [&[(&str, &str)]; 2] = [
        &[("head_valve_seat_insert", "SEAT INSERT"), ("head_valve_seat_oring", "O-RING"), ("head_valve_nose", "NOSE"),
            ("head_valve_tube_front_oring", "O-RING"), ("head_valve_plunger_tube", "TUBE"),
            ("head_valve_flux_washer", "FLUX WASHER"), ("head_valve_coil_bobbin", "COIL"),
            ("head_valve_tube_rear_oring", "O-RING"), ("head_valve_pole_and_inlet", "POLE AND INLET"),
            ("head_valve_yoke_cup", "YOKE CUP")],
        &[("head_valve_rubber_plug", "RUBBER PLUG"), ("head_valve_plunger", "PLUNGER"),
            ("head_valve_return_spring", "SPRING"), ("head_valve_stop_shim", "STOP SHIM")],
    ];
    let mut parts = vec![];
    for (row, names) in rows.iter().enumerate() {
        let mut along = if row == 0 { 0. } else { 38. };
        let height = if row == 0 { 0. } else { 34. };
        for (index, (name, label)) in names.iter().enumerate() {
            let (_, color, solid) = closed.iter().find(|(n, _, _)| n == name).expect("a named piece");
            let mut shown = if stays_whole(name) { solid.clone() } else { solid.cut(&near_half)? };
            let mut colors = vec![(name.to_string(), *color)];
            if *name == "head_valve_coil_bobbin" {
                let (_, copper, winding) = closed.iter().find(|(n, _, _)| n == "head_valve_copper_winding").expect("the winding");
                add(&mut parts, "head_valve_copper_winding", *copper, Solid::empty());
                colors.push(("head_valve_copper_winding".into(), *copper));
                let winding = winding.cut(&near_half)?;
                let bounds = shown.bounds();
                let shift = v3(0., along - bounds.min.y, 0.);
                let last = parts.len() - 1;
                parts[last].2 = lay(&winding.translate(shift), height);
                shown = shown.translate(shift);
            } else {
                let bounds = shown.bounds();
                shown = shown.translate(v3(0., along - bounds.min.y, 0.));
            }
            let bounds = shown.bounds();
            add(&mut parts, name, *color, lay(&shown, height));
            let drop = if index % 2 == 0 { 11. } else { 14.5 };
            let label_at = Plane::new(v3((bounds.min.y + bounds.max.y) / 2., 0., height - drop), V3::X, -V3::Y)?;
            add(&mut parts, &format!("label_{}_{}", row, label.replace(' ', "_")), [0.05, 0.055, 0.055],
                label_at.text(&font, label, 2.3, 0.1, HAlign::Center, VAlign::Center)?);
            along = bounds.max.y + 7.;
        }
    }
    parts.retain(|(_, _, solid)| !solid.is_empty());
    write(&dir, "direct-valve-parts", &parts)?;

    // The head keeps the concept's grip, display, lines and hose, and takes this valve on the same axis.
    let place = |solid: &Solid| solid.placed(&Plane::XY, &frame);
    let nose_seat = cyl(NOSE_R + 0.1, NOSE_FRONT_S, 2.)?.union(&cyl(INSERT_THREAD_R + 0.2, NOSE_FRONT_S - 1., 1.1)?)?;
    let cap_fill = ring(5.4, INSERT_THREAD_R + 0.2, -0.92, 0.32)?;
    let mut scene = vec![];
    let mut cutaway = vec![];
    let near_half_placed = place(&near_half);
    for body in &head {
        let name = body.name.as_str();
        let keep = name == "pull_off_curved_grip" || name == "soft_hose_strain_relief" || name.starts_with("screen_")
            || (name.starts_with("head_") && (!name.starts_with("head_valve_") || kept_inlet(name) || name == "head_valve_fly_leads"));
        if !keep { continue; }
        let color = body.color.unwrap_or(steel);
        let solid = if name == "pull_off_curved_grip" {
            body.solid.union(&place(&cap_fill))?.cut(&place(&nose_seat))?
        } else { body.solid.clone() };
        let shown_name = name.replace("head_valve_curved_inlet", "head_inlet_curved_inlet")
            .replace("head_valve_integral_hose_barb", "head_inlet_integral_hose_barb")
            .replace("head_valve_barb_ridge_", "head_inlet_barb_ridge_");
        if name == "pull_off_curved_grip" {
            add(&mut cutaway, &shown_name, color, solid.cut(&near_half_placed)?);
        } else if name != "head_flavor_a_line" {
            add(&mut cutaway, &shown_name, color, solid.clone());
        }
        add(&mut scene, &shown_name, color, solid);
    }
    for (name, color, solid) in &closed {
        add(&mut scene, name, *color, place(solid));
        let shown = if stays_whole(name) { solid.clone() } else { solid.cut(&near_half)? };
        add(&mut cutaway, name, *color, place(&shown));
    }
    write(&dir, "head-direct-valve", &scene)?;
    write(&dir, "head-direct-valve-cutaway", &cutaway)?;

    design(&dir)
}

/// A piece laid along the picture's width for the row of separate pieces.
fn lay(solid: &Solid, height: f64) -> Solid {
    solid.rotate(V3::ZERO, V3::Z, -90.).translate(v3(0., 0., height))
}

/// The record of this valve's sizes and first-order budgets, written from the numbers that draw it.
fn design(dir: &std::path::Path) -> Result<()> {
    let tube_inner = TUBE_OUTER_R - TUBE_WALL;
    let seal_area = PI * LIP_CREST_R.powi(2);
    let curtain = TAU * SEAT_BORE_R * LIFT;
    let bore_area = PI * SEAT_BORE_R.powi(2);
    let pour = |l_min: f64| (l_min / 60_000. / (0.65 * curtain * 1e-6)).powi(2) * 1000. / 2. / 100_000.;
    let spring_rate = SPRING_SHEAR_MODULUS_MPA * (2. * SPRING_WIRE_R).powi(4)
        / (8. * (2. * SPRING_MEAN_R).powi(3) * SPRING_ACTIVE_COILS);
    let spring_open = SPRING_PRELOAD_N + spring_rate * LIFT;
    let washer_to_flange = POLE_FLANGE_S + POLE_FLANGE_LENGTH / 2. - NOSE_REAR_S - WASHER_LENGTH / 2.;
    let feed_mpa = calibration_inputs::SECONDARY_REGULATOR_BAR / 10.;
    let relief_mpa = RELIEF_VALVE_PSI / calibration_inputs::PSI_PER_BAR / 10.;
    let magnetics = Magnetics {
        gap_area: PI * (PLUNGER_R.powi(2) - SPRING_POCKET_R.powi(2)),
        cup_area: PI * (CUP_R.powi(2) - CUP_INNER_R.powi(2)),
        radial_reluctance: (TUBE_WALL + tube_inner - PLUNGER_R) * 1e-3
            / (MU0 * TAU * (TUBE_OUTER_R + PLUNGER_R) / 2. * WASHER_LENGTH * 1e-6),
        core_path: washer_to_flange + 2. * (DRY_STACK_R - POLE_SPIGOT_R),
        cup_path: washer_to_flange,
    };
    let winding_length = BOBBIN_LENGTH - 2. * BOBBIN_FLANGE;
    let copper_area = (WINDING_OUTER_R - WINDING_INNER_R) * winding_length * WINDING_FILL;
    let turn_length = PI * (WINDING_OUTER_R + WINDING_INNER_R);
    let resistance = COPPER_RESISTIVITY_OHM_MM * WINDING_TURNS * turn_length / WIRE_AREA_MM2;
    let peak_current = SUPPLY_V / (resistance + LEAD_RESISTANCE_OHM);
    let peak_turns = peak_current * WINDING_TURNS;
    let (peak_b, peak_pull) = magnetics.pull(peak_turns, LIFT + STOP_SHIM);
    let hold_need = HOLD_MARGIN * (spring_open + pour(2.) * 0.1 * seal_area);
    let hold_flux = (2. * MU0 * hold_need * magnetics.gap_area * 1e-6).sqrt() / FLUX_REACHING_GAP;
    let hold_turns = magnetics.ampere_turns(hold_flux, STOP_SHIM);
    let hold_current = hold_turns / WINDING_TURNS;
    let opening = |mpa: f64| {
        let load = mpa * seal_area + SPRING_PRELOAD_N + SLIDING_FRICTION_ALLOWANCE_N;
        serde_json::json!({ "pressure_mpa": mpa, "water_holds_seat_shut_n": mpa * seal_area,
            "opening_load_n": load, "pull_over_load": peak_pull / load })
    };
    let record = serde_json::json!({
        "purpose": "This record owns the one-moving-part head valve's sizes and first-order budgets.",
        "date": "2026-11-19",
        "state": "Proposed mechanism and packaging. Forces, flow and coil values are first-order estimates from the drawn sizes, not measurements.",
        "geometry_mm": {
            "seat_bore": 2. * SEAT_BORE_R, "seal_circle": 2. * LIP_CREST_R, "lift": LIFT, "stop_shim": STOP_SHIM,
            "plunger_diameter": 2. * PLUNGER_R, "plunger_length": POLE_FACE_S - STOP_SHIM - LIFT - PLUNGER_FRONT_S,
            "tube_outside_diameter": 2. * TUBE_OUTER_R, "tube_wall": TUBE_WALL,
            "tube_length": POLE_FLANGE_S + ORING_POCKET_DEPTH - TUBE_START_S,
            "yoke_cup_outside_diameter": 2. * CUP_R, "nose_diameter": 2. * NOSE_R,
            "dispense_face_to_cup_rear": POLE_FLANGE_S + POLE_FLANGE_LENGTH + CUP_REAR_WALL - FACE_S,
            "dispense_face_to_inlet_end": INLET_END_S - FACE_S,
            "oring_section": ORING_SECTION, "static_orings": 3, "sliding_seals": 0
        },
        "water": {
            "seal_area_mm2": seal_area, "seat_bore_area_mm2": bore_area, "curtain_area_mm2": curtain,
            "pole_bore_area_mm2": PI * POLE_BORE_R.powi(2),
            "cross_hole_area_mm2": CROSS_HOLES as f64 * PI * CROSS_HOLE_R.powi(2),
            "seat_drop_bar_at_l_min_assuming_cd_0_65": { "1.5": pour(1.5), "2.0": pour(2.0) },
            "outlet_speed_m_s_at_2_l_min": 2. / 60_000. / (bore_area * 1e-6),
            "liquid_past_the_seat_mm3": bore_area * (SEAL_S - FACE_S),
            "pressures_mpa": {
                "machine_regulator_feed": feed_mpa, "lillium_co2_inlet_range": LILLIUM_INLET_MPA, "relief_valve": relief_mpa,
                "sources": ["hardware/assembly/pressure-vessel.md", "future/model.md"]
            },
            "opening": [opening(feed_mpa), opening(LILLIUM_INLET_MPA[1]), opening(relief_mpa)]
        },
        "spring": {
            "wire_mm": 2. * SPRING_WIRE_R, "mean_diameter_mm": 2. * SPRING_MEAN_R, "active_coils": SPRING_ACTIVE_COILS,
            "rate_n_mm": spring_rate, "closed_force_n": SPRING_PRELOAD_N, "open_force_n": spring_open,
            "free_length_mm": POLE_FACE_S - STOP_SHIM - SPRING_POCKET_S + SPRING_PRELOAD_N / spring_rate
        },
        "coil_and_pull": {
            "turns": WINDING_TURNS, "bare_wire_area_mm2": WIRE_AREA_MM2, "copper_fill": WINDING_FILL,
            "turns_the_window_holds_at_that_fill": copper_area / WIRE_AREA_MM2,
            "cold_resistance_ohm": resistance, "supply_v": SUPPLY_V, "lead_resistance_allowance_ohm": LEAD_RESISTANCE_OHM,
            "peak_current_a": peak_current, "peak_ampere_turns": peak_turns,
            "peak_copper_loss_w": peak_current.powi(2) * resistance,
            "gap_area_mm2": magnetics.gap_area, "yoke_cup_wall_area_mm2": magnetics.cup_area,
            "share_of_flux_reaching_the_gap": FLUX_REACHING_GAP,
            "gap_flux_density_t_at_full_lift": peak_b, "pull_n_at_full_lift": peak_pull,
            "hold_force_need_n": hold_need, "hold_ampere_turns": hold_turns, "hold_current_a": hold_current,
            "hold_copper_loss_w": hold_current.powi(2) * resistance,
            "sliding_friction_allowance_n": SLIDING_FRICTION_ALLOWANCE_N,
            "method": "A one-loop magnetic circuit: the working gap, the crossing through the tube wall at the flux washer, and the iron from a coarse curve for annealed magnetic stainless, with a fixed share of the flux taken as leakage."
        },
        "open_questions": [
            "The pull is not from a field solution or a bench pull test.",
            "Where the supply pressure is shed upstream of the seat, and the outlet's shape, decide foam and the stream.",
            "Magnetic stainless and EPDM in cold carbonated water over years.",
            "The thin stock tube is to be confirmed as a stocked size."
        ]
    });
    std::fs::write(dir.join("direct-valve-design.json"), serde_json::to_string_pretty(&record)? + "\n")?;
    Ok(())
}
