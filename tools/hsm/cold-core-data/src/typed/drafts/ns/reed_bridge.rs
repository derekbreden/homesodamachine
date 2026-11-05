//! `reed_bridge`: the printed PETG interposer that holds the two external level reeds against
//! the carbonator wall on the register azimuth and stands the evaporator coil off the glass.

use super::coil_mandrel;
use super::cold_core_interface as core;
use super::*;
use std::f64::consts::PI;

pub const NAME: &str = "reed_bridge";

pub const SERVING_VOLUME_ML: f64 = 355.0;
pub const SYRUP_DILUTION: f64 = 20.0;
pub const HIGH_FILL_FRACTION: f64 = 0.65;
pub const ROD_TACK_FILLET: f64 = 1.5;
pub const SKIRT_THICKNESS: f64 = 0.8;
pub const POCKET_END_WALL: f64 = 3.0;
pub const AXIAL_RAMP_LENGTH: f64 = 10.0;
pub const ARC_RAMP_WIDTH: f64 = 16.0;
pub const LEAD_GROOVE_WIDTH: f64 = 5.6;
pub const LEAD_GROOVE_Y: f64 = 5.4;
pub const LEAD_NOTCH_LENGTH: f64 = 2.0;
pub const OVERCUT: f64 = 1.0;
pub const GAUGE_ARC_DEGREES: f64 = 60.0;
pub const GAUGE_WALL: f64 = 3.0;
pub const GAUGE_HOOK_DEPTH: f64 = 3.5;
pub const GAUGE_HOOK_HEIGHT: f64 = 4.0;

pub struct State {
    here: PathBuf,
    hardware: PathBuf,
    fits: Val,
    float: Val,
    /// Provider values as their modules state them.
    carbonator_outer_radius_val: Val,
    carbonator_height_val: Val,
    m_petg_black: Val,
    tube_id_val: Val,
    register_radius_val: Val,
    register_drill_diameter_val: Val,
    disc_thickness_val: Val,
    float_height_val: Val,
    reed_glass_length_val: Val,
    reed_glass_diameter_val: Val,
    seat_clearance_val: Val,
    pub carbonator_outer_radius: f64,
    pub carbonator_height: f64,
    pub carbonator_support_ring_height: f64,
    pub wall_and_floor_thickness: f64,
    pub carbonator_float_top_stop_height: f64,
    pub carbonator_float_top_stop_diameter: f64,
    pub evap_tail_low_z: f64,
    pub evap_tail_high_z: f64,
    pub pitch: f64,
    pub tube_radius: f64,
    pub wrap_length: f64,
    pub tube_id: f64,
    pub register_radius: f64,
    pub register_drill_diameter: f64,
    pub disc_thickness: f64,
    pub tube_bottom_z_in_shell: f64,
    pub band_bottom_z: f64,
    pub band_top_z: f64,
    pub copper_od: f64,
    pub inter_wrap_clear: f64,
    pub plate_recess: f64,
    pub plate_thickness: f64,
    pub interior_floor_z: f64,
    pub interior_ceiling_z: f64,
    pub interior_height: f64,
    pub tube_id_mm: f64,
    pub interior_area: f64,
    pub volume_per_mm: f64,
    pub upper_stop_volume_ml: f64,
    pub interior_volume_ml: f64,
    pub carbonated_water_per_serving: f64,
    pub serving_level_rise: f64,
    pub high_level_z: f64,
    pub low_level_z: f64,
    pub headspace_height: f64,
    pub immersed_float_cc: f64,
    pub headspace_ml: f64,
    pub reserve_height: f64,
    pub reserve_ml: f64,
    pub stored_ml: f64,
    pub magnet_lead_above_surface: f64,
    pub reed_low_z: f64,
    pub reed_high_z: f64,
    pub float_height: f64,
    pub magnet_lowest_z: f64,
    pub magnet_highest_z: f64,
    pub float_wall_clearance: f64,
    pub reed_glass_length: f64,
    pub reed_glass_diameter: f64,
    pub seat_clearance: f64,
    pub inner_radius: f64,
    pub copper_clearance_over_glass: f64,
    pub pocket_depth: f64,
    pub plateau_radius: f64,
    pub skirt_radius: f64,
    pub pocket_length: f64,
    pub pocket_width: f64,
    pub plateau_z_bottom: f64,
    pub plateau_z_top: f64,
    pub bridge_z_bottom: f64,
    pub bridge_z_top: f64,
    pub bridge_height: f64,
    pub lead_groove_depth: f64,
    pub plateau_half_width: f64,
    pub bridge_half_width: f64,
    pub nominal_plateau_radius: f64,
    pub plateau_half_angle: f64,
    pub bridge_half_angle: f64,
    pub wraps_carried: f64,
    pub effective_lift_arc: f64,
    pub carried_copper: f64,
}

impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> {
        let here = resolve(&rt.file(NAME));
        let hardware = ancestor(&here, "hardware")?;
        rt.sys_path_insert(0, &hardware.join("scripts"))?;
        let docgen = ancestor_where(&here, |p| p.join("tools").join("docgen").is_dir())?;
        rt.sys_path_insert(0, &docgen.join("tools"))?;
        rt.sys_path_insert(0, &parent_n(&here, 1))?;
        rt.sys_path_insert(0, &parent_n(&here, 1).join("coil-mandrel"))?;
        rt.sys_path_insert(
            0,
            &hardware
                .join("cut-parts")
                .join("carbonation")
                .join("endcaps-circular"),
        )?;
        let core = core::state(rt)?;
        let b = &core.base;
        // The interface re-exports these from `_carbonator_stock` as that module states them.
        let carbonator_outer_radius_val = rt.pya("_carbonator_stock", "carbonator_outer_radius")?;
        let carbonator_height_val = rt.pya("_carbonator_stock", "carbonator_height")?;
        let m_petg_black = rt.pya("_materials", "M_PETG_BLACK")?;
        let fits = rt.py("fits")?;
        let mandrel = coil_mandrel::state(rt)?;
        // via namespace: endcap_circular_dxf
        let endcap = rt.import_module("endcap_circular_dxf")?;
        let tube_id_val = endcap.a("tube_id")?;
        let register_radius_val = endcap.a("register_radius")?;
        let register_drill_diameter_val = endcap.a("register_drill_diameter")?;
        let disc_thickness_val = endcap.a("disc_thickness")?;
        let float = rt.py("_float_interface")?;

        let carbonator_outer_radius = carbonator_outer_radius_val.f()?;
        let carbonator_height = carbonator_height_val.f()?;
        let (pitch, tube_radius, wrap_length) =
            (mandrel.pitch, mandrel.tube_radius, mandrel.wrap_length);
        let tube_id = tube_id_val.f()?;
        let register_radius = register_radius_val.f()?;
        let register_drill_diameter = register_drill_diameter_val.f()?;
        let disc_thickness = disc_thickness_val.f()?;

        let tube_bottom_z_in_shell = b.wall_and_floor_thickness + b.carbonator_support_ring_height;
        let band_bottom_z = b.evap_tail_low_z - tube_bottom_z_in_shell;
        let band_top_z = b.evap_tail_high_z - tube_bottom_z_in_shell;
        let copper_od = 2.0 * tube_radius;
        let inter_wrap_clear = pitch - copper_od;
        let plate_recess = disc_thickness * 25.4;
        let plate_thickness = disc_thickness * 25.4;
        let interior_floor_z = plate_recess + plate_thickness;
        let interior_ceiling_z = carbonator_height - plate_recess - plate_thickness;
        let interior_height = interior_ceiling_z - interior_floor_z;
        let tube_id_mm = tube_id * 25.4;
        let guide_diameter = float.a("guide_diameter")?.f()?;
        let interior_area = PI / 4.0 * (tube_id_mm.powf(2.0) - guide_diameter.powf(2.0));
        let volume_per_mm = interior_area / 1000.0;
        let upper_stop_volume_ml = PI / 4.0
            * (b.carbonator_float_top_stop_diameter.powf(2.0)
                - (register_drill_diameter * 25.4).powf(2.0))
            * b.carbonator_float_top_stop_height
            / 1000.0;
        let displacement_cc = float.a("displacement_cc")?.f()?;
        let interior_volume_ml =
            volume_per_mm * interior_height - displacement_cc - upper_stop_volume_ml;
        let carbonated_water_per_serving =
            SERVING_VOLUME_ML * SYRUP_DILUTION / (SYRUP_DILUTION + 1.0);
        let serving_level_rise = carbonated_water_per_serving / volume_per_mm;
        let high_level_z = interior_floor_z + HIGH_FILL_FRACTION * interior_height;
        let low_level_z = high_level_z - serving_level_rise;
        let headspace_height = interior_ceiling_z - high_level_z;
        let immersed_float_cc =
            float.a("design_mass_g")?.f()? / float.a("water_density")?.f()?;
        let headspace_ml = headspace_height * volume_per_mm
            - (displacement_cc - immersed_float_cc)
            - upper_stop_volume_ml;
        let reserve_height = low_level_z - interior_floor_z;
        let reserve_ml = reserve_height * volume_per_mm - immersed_float_cc;
        let stored_ml = (high_level_z - interior_floor_z) * volume_per_mm - immersed_float_cc;
        let magnet_lead_above_surface = float.m("magnet_above_waterline", vec![])?.f()?;
        let reed_low_z = low_level_z + magnet_lead_above_surface;
        let reed_high_z = high_level_z + magnet_lead_above_surface;
        let float_height_val = float.a("height")?;
        let float_height = float_height_val.f()?;
        let magnet_lowest_z = interior_floor_z + ROD_TACK_FILLET + float_height / 2.0;
        let magnet_highest_z =
            interior_ceiling_z - b.carbonator_float_top_stop_height - float_height / 2.0;
        let float_wall_clearance =
            (tube_id / 2.0 - register_radius) * 25.4 - float.a("diameter")?.f()? / 2.0;
        let reed_glass_length_val = float.a("reed_mount_length")?;
        let reed_glass_diameter_val = float.a("reed_mount_diameter")?;
        let (reed_glass_length, reed_glass_diameter) =
            (reed_glass_length_val.f()?, reed_glass_diameter_val.f()?);
        // `_fits.slip` and `_fits.supported_surface`, read once.
        let seat_clearance_val = fits.a("slip")?;
        let seat_clearance = seat_clearance_val.f()?;
        let slip = seat_clearance;
        let inner_radius = carbonator_outer_radius + seat_clearance;
        let supported_surface = fits.a("supported_surface")?.f()?;
        let copper_clearance_over_glass = 0.5 + supported_surface;
        let pocket_depth = reed_glass_diameter + copper_clearance_over_glass;
        let plateau_radius = carbonator_outer_radius + pocket_depth;
        let skirt_radius = inner_radius + SKIRT_THICKNESS;
        let pocket_length = reed_glass_length + 2.0 * slip;
        let pocket_width = reed_glass_diameter + 2.0 * slip;
        let plateau_z_bottom = reed_low_z - pocket_length / 2.0 - POCKET_END_WALL;
        let plateau_z_top = reed_high_z + pocket_length / 2.0 + POCKET_END_WALL;
        let bridge_z_bottom = plateau_z_bottom - AXIAL_RAMP_LENGTH;
        let bridge_z_top = plateau_z_top + AXIAL_RAMP_LENGTH;
        let bridge_height = bridge_z_top - bridge_z_bottom;
        let lead_groove_depth = plateau_radius - skirt_radius;
        let plateau_half_width = LEAD_GROOVE_Y + LEAD_GROOVE_WIDTH / 2.0 + 1.5;
        let bridge_half_width = plateau_half_width + ARC_RAMP_WIDTH;
        let nominal_plateau_radius = plateau_radius - supported_surface;
        let plateau_half_angle = (plateau_half_width / nominal_plateau_radius).asin();
        let bridge_half_angle = (bridge_half_width / nominal_plateau_radius).asin();
        let wraps_carried = bridge_height / pitch;
        let effective_lift_arc = 2.0 * plateau_half_width + ARC_RAMP_WIDTH;
        let carried_copper = wraps_carried * effective_lift_arc;
        Ok(Self {
            here,
            hardware,
            fits,
            float,
            carbonator_outer_radius_val,
            carbonator_height_val,
            m_petg_black,
            tube_id_val,
            register_radius_val,
            register_drill_diameter_val,
            disc_thickness_val,
            float_height_val,
            reed_glass_length_val,
            reed_glass_diameter_val,
            seat_clearance_val,
            carbonator_outer_radius,
            carbonator_height,
            carbonator_support_ring_height: b.carbonator_support_ring_height,
            wall_and_floor_thickness: b.wall_and_floor_thickness,
            carbonator_float_top_stop_height: b.carbonator_float_top_stop_height,
            carbonator_float_top_stop_diameter: b.carbonator_float_top_stop_diameter,
            evap_tail_low_z: b.evap_tail_low_z,
            evap_tail_high_z: b.evap_tail_high_z,
            pitch,
            tube_radius,
            wrap_length,
            tube_id,
            register_radius,
            register_drill_diameter,
            disc_thickness,
            tube_bottom_z_in_shell,
            band_bottom_z,
            band_top_z,
            copper_od,
            inter_wrap_clear,
            plate_recess,
            plate_thickness,
            interior_floor_z,
            interior_ceiling_z,
            interior_height,
            tube_id_mm,
            interior_area,
            volume_per_mm,
            upper_stop_volume_ml,
            interior_volume_ml,
            carbonated_water_per_serving,
            serving_level_rise,
            high_level_z,
            low_level_z,
            headspace_height,
            immersed_float_cc,
            headspace_ml,
            reserve_height,
            reserve_ml,
            stored_ml,
            magnet_lead_above_surface,
            reed_low_z,
            reed_high_z,
            float_height,
            magnet_lowest_z,
            magnet_highest_z,
            float_wall_clearance,
            reed_glass_length,
            reed_glass_diameter,
            seat_clearance,
            inner_radius,
            copper_clearance_over_glass,
            pocket_depth,
            plateau_radius,
            skirt_radius,
            pocket_length,
            pocket_width,
            plateau_z_bottom,
            plateau_z_top,
            bridge_z_bottom,
            bridge_z_top,
            bridge_height,
            lead_groove_depth,
            plateau_half_width,
            bridge_half_width,
            nominal_plateau_radius,
            plateau_half_angle,
            bridge_half_angle,
            wraps_carried,
            effective_lift_arc,
            carried_copper,
        })
    }
}

pub fn state(rt: &Runtime) -> Result<Rc<State>> {
    rt.state::<State>()
}

impl State {
    /// `_plan_outline_radius(angle)`: the bridge's plan radius at an azimuth, plateau then ramp.
    pub fn plan_outline_radius(&self, angle: f64) -> f64 {
        if angle.abs() <= self.plateau_half_angle {
            return self.plateau_radius;
        }
        let fraction = (angle.abs() - self.plateau_half_angle)
            / (self.bridge_half_angle - self.plateau_half_angle);
        self.plateau_radius - fraction * (self.plateau_radius - self.skirt_radius)
    }
}

/// `box(x, y, z)`: three ranges as the lists the recipe reads.
fn cut_box(x: [f64; 2], y: [f64; 2], z: [f64; 2]) -> Val {
    Val::list(vec![x.to_vec().to_val(), y.to_vec().to_val(), z.to_vec().to_val()])
}

/// `numbers()`: the figures the kernel's reed-bridge recipe cuts from.
pub fn numbers(rt: &Runtime) -> Result<Val> {
    let s = state(rt)?;
    let linear = rt.pya("_materials", "linear")?;
    let mut outline = vec![(0.0, 0.0)];
    for i in 0..49 {
        let angle = -s.bridge_half_angle + 2.0 * s.bridge_half_angle * i as f64 / 48.0;
        let radius = s.plan_outline_radius(angle);
        outline.push((radius * angle.cos(), radius * angle.sin()));
    }
    let (mut pockets, mut notches) = (vec![], vec![]);
    for reed_z in [s.reed_low_z, s.reed_high_z] {
        pockets.push(cut_box(
            [s.inner_radius - OVERCUT, s.plateau_radius + OVERCUT],
            [-s.pocket_width / 2.0, s.pocket_width / 2.0],
            [reed_z - s.pocket_length / 2.0, reed_z + s.pocket_length / 2.0],
        ));
        for z in [
            reed_z - s.pocket_length / 2.0,
            reed_z + s.pocket_length / 2.0 - LEAD_NOTCH_LENGTH,
        ] {
            notches.push(cut_box(
                [s.skirt_radius, s.plateau_radius + OVERCUT],
                [-s.pocket_width / 2.0, LEAD_GROOVE_Y + LEAD_GROOVE_WIDTH / 2.0],
                [z, z + LEAD_NOTCH_LENGTH],
            ));
        }
    }
    let ridge_section = vec![
        (s.inner_radius, s.bridge_z_bottom),
        (s.skirt_radius, s.bridge_z_bottom),
        (s.plateau_radius, s.plateau_z_bottom),
        (s.plateau_radius, s.plateau_z_top),
        (s.skirt_radius, s.bridge_z_top),
        (s.inner_radius, s.bridge_z_top),
    ];
    let gauge_section = vec![
        (s.inner_radius - GAUGE_HOOK_DEPTH, -GAUGE_HOOK_HEIGHT),
        (s.inner_radius + GAUGE_WALL, -GAUGE_HOOK_HEIGHT),
        (s.inner_radius + GAUGE_WALL, s.bridge_z_bottom),
        (s.inner_radius, s.bridge_z_bottom),
        (s.inner_radius, 0.0),
        (s.inner_radius - GAUGE_HOOK_DEPTH, 0.0),
    ];
    let lead_groove = cut_box(
        [s.skirt_radius, s.plateau_radius + OVERCUT],
        [
            LEAD_GROOVE_Y - LEAD_GROOVE_WIDTH / 2.0,
            LEAD_GROOVE_Y + LEAD_GROOVE_WIDTH / 2.0,
        ],
        [s.plateau_z_bottom, s.bridge_z_top + OVERCUT],
    );
    let color = Val::list(linear.c(vec![s.m_petg_black.clone()])?.list()?);
    Ok(Dict::new()
        .with("ridge_section", ridge_section)
        .with("plan_outline", outline)
        .with("plan_bottom", s.bridge_z_bottom - OVERCUT)
        .with("plan_height", s.bridge_height + 2.0 * OVERCUT)
        .with("pockets", pockets)
        .with("notches", notches)
        .with("lead_groove", lead_groove)
        .with("gauge_section", gauge_section)
        .with("gauge_arc_degrees", GAUGE_ARC_DEGREES)
        .with("color", color)
        .val())
}

/// The Python `main(output=None)`: reports the level budget, cuts the bridge and gauge on the
/// kernel and fills the documents.
pub fn write(rt: &Runtime, output: Option<&Path>) -> Result<()> {
    let s = state(rt)?;
    ensure!(
        s.reed_low_z > s.magnet_lowest_z,
        "low reed below the donut's reach"
    );
    ensure!(
        s.reed_high_z < s.magnet_highest_z,
        "high reed above the donut's reach"
    );
    let serving = s.carbonated_water_per_serving;
    rt.print(format!(
        "Wind band on the tube:  {} .. {} mm (pitch {}, clear channel {})",
        ff(s.band_bottom_z, ".1f"),
        ff(s.band_top_z, ".1f"),
        ff(s.pitch, ".3f"),
        ff(s.inter_wrap_clear, ".3f")
    ))?;
    rt.print(format!(
        "Wetted column:          {} .. {} mm = {} mm, {} mL/mm, {} mL",
        ff(s.interior_floor_z, ".2f"),
        ff(s.interior_ceiling_z, ".2f"),
        ff(s.interior_height, ".2f"),
        ff(s.volume_per_mm, ".3f"),
        ff(s.interior_volume_ml, ".0f")
    ))?;
    rt.print(format!(
        "Serving:                {} mL water = {} mm of level",
        ff(serving, ".1f"),
        ff(s.serving_level_rise, ".2f")
    ))?;
    rt.print(format!(
        "CHI (pump off):         level {} mm  stored {} mL = {} servings, headspace {} mL ({} %)",
        ff(s.high_level_z, ".2f"),
        ff(s.stored_ml, ".0f"),
        ff(s.stored_ml / serving, ".2f"),
        ff(s.headspace_ml, ".0f"),
        ff(100.0 - 100.0 * HIGH_FILL_FRACTION, ".0f")
    ))?;
    rt.print(format!(
        "CLO (pump on):          level {} mm  reserve {} mL = {} servings, band {} mm = 1.00 serving",
        ff(s.low_level_z, ".2f"),
        ff(s.reserve_ml, ".0f"),
        ff(s.reserve_ml / serving, ".2f"),
        ff(s.serving_level_rise, ".2f")
    ))?;
    rt.print(format!(
        "RC62 midplane reach:    {} .. {} mm (nominal body/wall clearance {} mm)",
        ff(s.magnet_lowest_z, ".1f"),
        ff(s.magnet_highest_z, ".1f"),
        ff(s.float_wall_clearance, ".2f")
    ))?;
    rt.print(format!(
        "Bridge:                 Z {} .. {} ({} mm), arc {} mm, {} mm proud",
        ff(s.bridge_z_bottom, ".2f"),
        ff(s.bridge_z_top, ".2f"),
        ff(s.bridge_height, ".2f"),
        ff(2.0 * s.bridge_half_width, ".1f"),
        ff(s.pocket_depth, ".1f")
    ))?;
    rt.print(format!(
        "Copper carried:         {} wraps x {} mm = {} mm",
        ff(s.wraps_carried, ".2f"),
        ff(s.effective_lift_arc, ".1f"),
        ff(s.carried_copper, ".0f")
    ))?;
    let out_dir = match output {
        Some(output) => output.to_path_buf(),
        None => parent_n(&s.here, 0),
    };
    std::fs::create_dir_all(&out_dir)?;
    let rust_part = rt.py("_rust_part")?;
    let bodies = rust_part
        .m(
            "cut",
            args!["cold-core", "reed-bridge", numbers(rt)?, out_dir],
        )?
        .k("bodies")?;
    let volumes = bodies
        .list()?
        .iter()
        .map(|body| body.k("volume"))
        .collect::<Result<Vec<_>>>()?;
    ensure!(
        volumes.len() == 2,
        "unpack: expected 2, got {}",
        volumes.len()
    );
    document(rt, &volumes[0], &volumes[1])
}

/// `document(bridge_volume, gauge_volume)`: fills the bridge README, the reservoir's
/// level-sensing page and this file's comments.
pub fn document(rt: &Runtime, bridge_volume: &Val, gauge_volume: &Val) -> Result<()> {
    let s = state(rt)?;
    let out_dir = parent_n(&s.here, 0);
    let unit = |x: f64, spec: &str, unit: &str| format!("{}{unit}", ff(x, spec));
    let serving = s.carbonated_water_per_serving;
    let variables: Vec<(String, String)> = [
        ("BAND_BOTTOM", unit(s.band_bottom_z, ".4g", " mm")),
        ("BAND_TOP", unit(s.band_top_z, ".4g", " mm")),
        ("WRAP_PITCH", unit(s.pitch, ".4g", " mm")),
        ("COPPER_OD", unit(s.copper_od, ".4g", " mm")),
        ("INTER_WRAP_CLEAR", unit(s.inter_wrap_clear, ".4g", " mm")),
        ("INTERIOR_FLOOR", unit(s.interior_floor_z, ".4g", " mm")),
        ("INTERIOR_CEILING", unit(s.interior_ceiling_z, ".4g", " mm")),
        ("INTERIOR_H", unit(s.interior_height, ".4g", " mm")),
        ("TUBE_ID_MM", unit(s.tube_id_mm, ".4g", " mm")),
        ("ML_PER_MM", unit(s.volume_per_mm, ".4g", " mL")),
        ("INTERIOR_ML", unit(s.interior_volume_ml, ".4g", " mL")),
        ("WATER_PER_SERVING", unit(serving, ".4g", " mL")),
        ("SERVING_RISE", unit(s.serving_level_rise, ".4g", " mm")),
        ("HIGH_LEVEL", unit(s.high_level_z, ".4g", " mm")),
        ("LOW_LEVEL", unit(s.low_level_z, ".4g", " mm")),
        ("HEADSPACE_ML", unit(s.headspace_ml, ".4g", " mL")),
        ("RESERVE_ML", unit(s.reserve_ml, ".4g", " mL")),
        ("RESERVE_SERVINGS", ff(s.reserve_ml / serving, ".3g")),
        ("STORED_ML", unit(s.stored_ml, ".4g", " mL")),
        ("STORED_SERVINGS", ff(s.stored_ml / serving, ".3g")),
        ("MAGNET_LOWEST", unit(s.magnet_lowest_z, ".4g", " mm")),
        ("MAGNET_HIGHEST", unit(s.magnet_highest_z, ".4g", " mm")),
        (
            "FLOAT_WALL_CLEARANCE",
            unit(s.float_wall_clearance, ".3g", " mm"),
        ),
        (
            "MAGNET_LEAD",
            unit(s.magnet_lead_above_surface, ".3f", " mm"),
        ),
        ("REED_LOW_Z", unit(s.reed_low_z, ".3f", " mm")),
        ("REED_HIGH_Z", unit(s.reed_high_z, ".3f", " mm")),
        ("REED_GLASS_L", unit(s.reed_glass_length, ".4g", " mm")),
        ("REED_GLASS_D", unit(s.reed_glass_diameter, ".4g", " mm")),
        ("POCKET_DEPTH", unit(s.pocket_depth, ".4g", " mm")),
        ("POCKET_L", unit(s.pocket_length, ".4g", " mm")),
        ("POCKET_W", unit(s.pocket_width, ".4g", " mm")),
        ("SKIRT_T", unit(SKIRT_THICKNESS, ".4g", " mm")),
        ("AXIAL_RAMP", unit(AXIAL_RAMP_LENGTH, ".4g", " mm")),
        ("ARC_RAMP", unit(ARC_RAMP_WIDTH, ".4g", " mm")),
        ("BRIDGE_Z_BOTTOM", unit(s.bridge_z_bottom, ".4g", " mm")),
        ("BRIDGE_Z_TOP", unit(s.bridge_z_top, ".4g", " mm")),
        ("BRIDGE_H", unit(s.bridge_height, ".4g", " mm")),
        ("BRIDGE_ARC", unit(2.0 * s.bridge_half_width, ".4g", " mm")),
        ("EFFECTIVE_ARC", unit(s.effective_lift_arc, ".4g", " mm")),
        (
            "CARRIED_FRACTION",
            unit(100.0 * s.carried_copper / s.wrap_length, ".2g", " %"),
        ),
        ("LEAD_GROOVE_W", unit(LEAD_GROOVE_WIDTH, ".4g", " mm")),
        ("LEAD_GROOVE_D", unit(s.lead_groove_depth, ".4g", " mm")),
        ("WRAPS_CARRIED", ff(s.wraps_carried, ".3g")),
        ("CARRIED_COPPER", unit(s.carried_copper, ".0f", " mm")),
        (
            "BRIDGE_VOL",
            unit(bridge_volume.f()? / 1000.0, ".3g", " cm³"),
        ),
        ("GAUGE_VOL", unit(gauge_volume.f()? / 1000.0, ".3g", " cm³")),
        ("GAUGE_ARC_DEG", unit(GAUGE_ARC_DEGREES, ".3g", "°")),
    ]
    .into_iter()
    .map(|(k, v)| (k.to_owned(), v))
    .collect();
    rt.substitute_md(&out_dir.join("README.md"), &variables, Some(NAME))?;
    rt.print("-> README.md")?;
    let level_sensing = parent_n(&out_dir, 0)
        .join("reservoir")
        .join("level-sensing.md");
    rt.substitute_md(&level_sensing, &variables, Some(NAME))?;
    rt.print("-> ../reservoir/level-sensing.md")?;
    let file = rt.file(NAME);
    rt.substitute_py_comments(&file, &variables, Some(NAME))?;
    let name = file.file_name().map(|n| n.to_string_lossy().into_owned());
    rt.print(format!("-> {} (self)", name.unwrap_or_default()))
}

/// The variables a docgen call passes, as `str()` of each value.
fn substitution(c: &mut Call) -> Result<(PathBuf, Vec<(String, String)>)> {
    let path = PathBuf::from(c.req::<Val>(0, "path")?.str()?);
    let variables: Val = c.req(1, "variables")?;
    let mut values = vec![];
    for key in variables.iter()? {
        values.push((key.str()?, variables.get(key)?.str()?));
    }
    Ok((path, values))
}

/// The native `substitute_md(path, variables)` this module imported from docgen.
fn substitute_md(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let (path, values) = substitution(c)?;
    rt.substitute_md(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

/// The native `substitute_py_comments(path, variables)` this module imported from docgen.
fn substitute_py_comments(rt: &Runtime, c: &mut Call) -> Result<Val> {
    let (path, values) = substitution(c)?;
    rt.substitute_py_comments(&path, &values, Some(NAME))?;
    Ok(Val::None)
}

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    let s = state(rt)?;
    ns.module(rt, "argparse", "argparse")?;
    ns.module(rt, "math", "math")?;
    ns.module(rt, "sys", "sys")?;
    ns.value("Path", rt.import_module("pathlib")?.a("Path")?);
    ns.value("_here", s.here.clone());
    ns.value("_hardware", s.hardware.clone());
    ns.func(rt, "substitute_md", substitute_md);
    ns.func(rt, "substitute_py_comments", substitute_py_comments);
    ns.value("carbonator_outer_radius", s.carbonator_outer_radius_val.clone());
    ns.value("carbonator_height", s.carbonator_height_val.clone());
    ns.value("carbonator_support_ring_height", s.carbonator_support_ring_height);
    ns.value("wall_and_floor_thickness", s.wall_and_floor_thickness);
    ns.value(
        "carbonator_float_top_stop_height",
        s.carbonator_float_top_stop_height,
    );
    ns.value(
        "carbonator_float_top_stop_diameter",
        s.carbonator_float_top_stop_diameter,
    );
    ns.value("evap_tail_low_z", s.evap_tail_low_z);
    ns.value("evap_tail_high_z", s.evap_tail_high_z);
    ns.value("M_PETG_BLACK", s.m_petg_black.clone());
    ns.value("_fits", s.fits.clone());
    ns.value("pitch", s.pitch);
    ns.value("tube_radius", s.tube_radius);
    ns.value("wrap_length", s.wrap_length);
    ns.value("tube_id", s.tube_id_val.clone());
    ns.value("register_radius", s.register_radius_val.clone());
    ns.value("register_drill_diameter", s.register_drill_diameter_val.clone());
    ns.value("disc_thickness", s.disc_thickness_val.clone());
    ns.value("_float", s.float.clone());
    ns.value("tube_bottom_z_in_shell", s.tube_bottom_z_in_shell);
    ns.value("band_bottom_z", s.band_bottom_z);
    ns.value("band_top_z", s.band_top_z);
    ns.value("copper_od", s.copper_od);
    ns.value("inter_wrap_clear", s.inter_wrap_clear);
    ns.value("plate_recess", s.plate_recess);
    ns.value("plate_thickness", s.plate_thickness);
    ns.value("interior_floor_z", s.interior_floor_z);
    ns.value("interior_ceiling_z", s.interior_ceiling_z);
    ns.value("interior_height", s.interior_height);
    ns.value("tube_id_mm", s.tube_id_mm);
    ns.value("interior_area", s.interior_area);
    ns.value("volume_per_mm", s.volume_per_mm);
    ns.value("upper_stop_volume_ml", s.upper_stop_volume_ml);
    ns.value("interior_volume_ml", s.interior_volume_ml);
    ns.value("serving_volume_ml", SERVING_VOLUME_ML);
    ns.value("syrup_dilution", SYRUP_DILUTION);
    ns.value("carbonated_water_per_serving", s.carbonated_water_per_serving);
    ns.value("serving_level_rise", s.serving_level_rise);
    ns.value("high_fill_fraction", HIGH_FILL_FRACTION);
    ns.value("high_level_z", s.high_level_z);
    ns.value("low_level_z", s.low_level_z);
    ns.value("headspace_height", s.headspace_height);
    ns.value("_immersed_float_cc", s.immersed_float_cc);
    ns.value("headspace_ml", s.headspace_ml);
    ns.value("reserve_height", s.reserve_height);
    ns.value("reserve_ml", s.reserve_ml);
    ns.value("stored_ml", s.stored_ml);
    ns.value("magnet_lead_above_surface", s.magnet_lead_above_surface);
    ns.value("reed_low_z", s.reed_low_z);
    ns.value("reed_high_z", s.reed_high_z);
    ns.value("float_height", s.float_height_val.clone());
    ns.value("rod_tack_fillet", ROD_TACK_FILLET);
    ns.value("magnet_lowest_z", s.magnet_lowest_z);
    ns.value("magnet_highest_z", s.magnet_highest_z);
    ns.value("float_wall_clearance", s.float_wall_clearance);
    ns.value("reed_glass_length", s.reed_glass_length_val.clone());
    ns.value("reed_glass_diameter", s.reed_glass_diameter_val.clone());
    ns.value("seat_clearance", s.seat_clearance_val.clone());
    ns.value("inner_radius", s.inner_radius);
    ns.value("skirt_thickness", SKIRT_THICKNESS);
    ns.value("copper_clearance_over_glass", s.copper_clearance_over_glass);
    ns.value("pocket_depth", s.pocket_depth);
    ns.value("plateau_radius", s.plateau_radius);
    ns.value("skirt_radius", s.skirt_radius);
    ns.value("pocket_length", s.pocket_length);
    ns.value("pocket_width", s.pocket_width);
    ns.value("pocket_end_wall", POCKET_END_WALL);
    ns.value("plateau_z_bottom", s.plateau_z_bottom);
    ns.value("plateau_z_top", s.plateau_z_top);
    ns.value("axial_ramp_length", AXIAL_RAMP_LENGTH);
    ns.value("arc_ramp_width", ARC_RAMP_WIDTH);
    ns.value("bridge_z_bottom", s.bridge_z_bottom);
    ns.value("bridge_z_top", s.bridge_z_top);
    ns.value("bridge_height", s.bridge_height);
    ns.value("lead_groove_width", LEAD_GROOVE_WIDTH);
    ns.value("lead_groove_depth", s.lead_groove_depth);
    ns.value("lead_groove_y", LEAD_GROOVE_Y);
    ns.value("lead_notch_length", LEAD_NOTCH_LENGTH);
    ns.value("plateau_half_width", s.plateau_half_width);
    ns.value("bridge_half_width", s.bridge_half_width);
    ns.value("nominal_plateau_radius", s.nominal_plateau_radius);
    ns.value("plateau_half_angle", s.plateau_half_angle);
    ns.value("bridge_half_angle", s.bridge_half_angle);
    ns.value("wraps_carried", s.wraps_carried);
    ns.value("effective_lift_arc", s.effective_lift_arc);
    ns.value("carried_copper", s.carried_copper);
    ns.value("overcut", OVERCUT);
    ns.func(rt, "_plan_outline_radius", |rt, c| {
        let angle: f64 = c.req(0, "angle")?;
        Ok(Val::Float(state(rt)?.plan_outline_radius(angle)))
    });
    ns.value("gauge_arc_degrees", GAUGE_ARC_DEGREES);
    ns.value("gauge_wall", GAUGE_WALL);
    ns.value("gauge_hook_depth", GAUGE_HOOK_DEPTH);
    ns.value("gauge_hook_height", GAUGE_HOOK_HEIGHT);
    ns.func(rt, "numbers", |rt, _| numbers(rt));
    ns.func(rt, "main", |rt, c| {
        let output: Option<PathBuf> = c.opt(0, "output", None)?;
        write(rt, output.as_deref())?;
        Ok(Val::None)
    });
    ns.func(rt, "document", |rt, c| {
        let bridge_volume: Val = c.req(0, "bridge_volume")?;
        let gauge_volume: Val = c.req(1, "gauge_volume")?;
        document(rt, &bridge_volume, &gauge_volume)?;
        Ok(Val::None)
    });
    Ok(())
}

/// The `__main__` block: `--output` names the directory the pieces go to.
pub fn main(rt: &Runtime) -> Result<()> {
    rt.py("_rust_part")?.m("start", vec![])?;
    let s = state(rt)?;
    let description = super::table::documentation(NAME).map_or(Val::None, Val::from);
    let parser = rt
        .py("argparse")?
        .mk("ArgumentParser", vec![], kw!["description" => description])?;
    let path = rt.import_module("pathlib")?.a("Path")?;
    parser.mk(
        "add_argument",
        args!["--output"],
        kw!["type" => path, "default" => parent_n(&s.here, 0)],
    )?;
    let args = parser.m("parse_args", vec![])?;
    let output: Option<PathBuf> = Option::from_val(&args.a("output")?)?;
    write(rt, output.as_deref())
}
