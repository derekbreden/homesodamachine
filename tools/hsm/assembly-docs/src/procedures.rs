use super::*;
mod specialized;
pub fn run(request: &Request) -> Result<Output> {
    match request.driver.as_str() {
        "ac-wiring-schedule" => ac_wiring_schedule(request),
        "acceptance-and-burn-in" => acceptance_and_burn_in(request),
        "asse-drain" => asse_drain(request),
        "cable-assemblies" => specialized::cable_assemblies(request),
        "cold-core" => cold_core(request),
        "electronics-bay" => electronics_bay(request),
        "enclosure-mechanical" => enclosure_mechanical(request),
        "faucet-and-umbilical" => faucet_and_umbilical(request),
        "finish-pack-ship" => finish_pack_ship(request),
        "firmware-and-commissioning" => specialized::firmware_and_commissioning(request),
        "handwork" => handwork(request),
        "internal-plumbing" => internal_plumbing(request),
        "pressure-vessel" => specialized::pressure_vessel(request),
        "refrigerant-loop" => refrigerant_loop(request),
        "water-inlet-jet" => water_inlet_jet(request),
        "weld-rotation-rig" => specialized::weld_rotation_rig(request),
        "wiring" => wiring(request),
        _ => bail!("unknown procedure {}", request.driver),
    }
}
fn ac_wiring_schedule(request: &Request) -> Result<Output> {
    let _input = &request.input;
    let line_voltage_v: f64 = 120.0;
    let ac_primary_fuse_a: f64 = 5.0;
    let awg_mains: f64 = 16.0;
    let awg_ac_branch: f64 = 16.0;
    let awg_compressor_lead: f64 = 18.0;
    let awg_sig: f64 = 22.0;
    let awg_lv: f64 = 22.0;
    let psu_primary_a: f64 = 0.67;
    let psu_full_load_w: f64 = 80.0;
    let psu_max_dc_a: f64 = 6.7;
    let diaphragm_peak_a: f64 = 5.0;
    let pump_peak_a: f64 = 0.8;
    let fan_current_a: f64 = 0.35;
    let solenoid_coil_a: f64 = 5.5 / 12.0;
    let max_simultaneous_valves: f64 = 3.0;
    let board_peak_a: f64 =
        ((2.0 * pump_peak_a) + (max_simultaneous_valves * solenoid_coil_a)) + fan_current_a;
    let coincident_peak_a: f64 = board_peak_a + diaphragm_peak_a;
    let wago_221_413_rated_a: f64 = 32.0;
    let v_rail_dc: f64 = 12.0;
    let v_rail_logic: f64 = 5.0;
    let v_rail_io: f64 = 3.3;
    let ds18b20_pullup_kohm: f64 = 4.7;
    let compressor_wires_wall_relay: f64 = 3.0;
    let compressor_wires_local_relay: f64 = 5.0;
    let solenoid_count: f64 = 10.0;
    let len_short_mm: f64 = hsm_ac_harness_numbers::SHORT;
    let len_short_2_mm: f64 = hsm_ac_harness_numbers::SHORT_2;
    let len_dc1_mm: f64 = hsm_ac_harness_numbers::DC1;
    let len_dc2_mm: f64 = hsm_ac_harness_numbers::DC2;
    let len_mid_mm: f64 = hsm_ac_harness_numbers::MID;
    let len_pump_mm: f64 = 350.0;
    let len_earth_carbonator_mm: f64 = 500.0;
    let len_relays_mm: f64 = 350.0;
    let len_vk_mm: f64 = 350.0;
    let len_man_a_com_mm: f64 = 350.0;
    let len_man_b_com_mm: f64 = 350.0;
    let len_flow_mm: f64 = 350.0;
    let len_onewire_mm: f64 = 650.0;
    let len_sensors_gnd_mm: f64 = 300.0;
    let len_reeds_gnd_mm: f64 = 300.0;
    let len_man_a_mm: f64 = 600.0;
    let len_moisture_mm: f64 = 350.0;
    let len_carb_reeds_mm: f64 = 650.0;
    let len_man_b_mm: f64 = 550.0;
    let len_man_a_fanout_mm: f64 = 450.0;
    let len_man_b_fanout_mm: f64 = 450.0;
    let len_pump_fixed_mm: f64 = 500.0;
    let len_front_face_mm: f64 = 400.0;
    let len_faucet_inboard_mm: f64 = 400.0;
    let len_reeds_b_mm: f64 = 500.0;
    let len_fan_mm: f64 = 650.0;
    let len_reeds_a_mm: f64 = 650.0;
    let len_gas_mm: f64 = 600.0;
    let len_compressor_mm: f64 = 700.0;
    let len_opening_join_mm: f64 = hsm_ac_harness_numbers::OPENING_JOIN;
    let len_umbilical_m: f64 = 2.0;
    let jst_pitch_mm: f64 = 2.5;
    let mut variables = Variables::new();
    variables.insert(
        "V_LINE".into(),
        [fmt(line_voltage_v, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "PRIMARY_FUSE_A".into(),
        [fmt(ac_primary_fuse_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert("AWG_MAINS".into(), [fmt(awg_mains, ".4g")?].concat());
    variables.insert(
        "AWG_AC_BRANCH".into(),
        [fmt(awg_ac_branch, ".4g")?].concat(),
    );
    variables.insert(
        "AWG_COMP_LEAD".into(),
        [fmt(awg_compressor_lead, ".4g")?].concat(),
    );
    variables.insert("AWG_SIG".into(), [fmt(awg_sig, ".4g")?].concat());
    variables.insert("AWG_LV".into(), [fmt(awg_lv, ".4g")?].concat());
    variables.insert(
        "AWG_MAINS_U".into(),
        [fmt(awg_mains, ".4g")?, " AWG".to_owned()].concat(),
    );
    variables.insert(
        "AWG_AC_BRANCH_U".into(),
        [fmt(awg_ac_branch, ".4g")?, " AWG".to_owned()].concat(),
    );
    variables.insert(
        "AWG_COMP_LEAD_U".into(),
        [fmt(awg_compressor_lead, ".4g")?, " AWG".to_owned()].concat(),
    );
    variables.insert(
        "PSU_PRI_A".into(),
        [fmt(psu_primary_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "PSU_W".into(),
        [fmt(psu_full_load_w, ".4g")?, " W".to_owned()].concat(),
    );
    variables.insert(
        "PSU_MAX_A".into(),
        [fmt(psu_max_dc_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "DIAPHRAGM_A".into(),
        [fmt(diaphragm_peak_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "PUMP_PEAK_A".into(),
        [fmt(pump_peak_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "FAN_A".into(),
        [fmt(fan_current_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "COIL_A".into(),
        [fmt(solenoid_coil_a, ".2g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "MAX_VALVES".into(),
        [fmt(max_simultaneous_valves, "d")?].concat(),
    );
    variables.insert(
        "BOARD_PEAK_A".into(),
        [fmt(board_peak_a, ".3g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "COINCIDENT_A".into(),
        [fmt(coincident_peak_a, ".3g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "WAGO_RATED_A".into(),
        [fmt(wago_221_413_rated_a, ".4g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "V_DC".into(),
        [fmt(v_rail_dc, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "V_LOGIC".into(),
        [fmt(v_rail_logic, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "V_IO".into(),
        [fmt(v_rail_io, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "DS18B20_PULLUP".into(),
        [fmt(ds18b20_pullup_kohm, ".4g")?, " kΩ".to_owned()].concat(),
    );
    variables.insert(
        "COMP_WIRES".into(),
        [fmt(compressor_wires_wall_relay, ".4g")?].concat(),
    );
    variables.insert(
        "COMP_WIRES_ALT".into(),
        [fmt(compressor_wires_local_relay, ".4g")?].concat(),
    );
    variables.insert(
        "SOLENOID_COUNT".into(),
        [fmt(solenoid_count, ".4g")?].concat(),
    );
    variables.insert(
        "LEN_SHORT".into(),
        ["~".to_owned(), fmt(len_short_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_SHORT_2".into(),
        [
            "~".to_owned(),
            fmt(len_short_2_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_DC1".into(),
        ["~".to_owned(), fmt(len_dc1_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_DC2".into(),
        ["~".to_owned(), fmt(len_dc2_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_MID".into(),
        ["~".to_owned(), fmt(len_mid_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_PUMP".into(),
        ["~".to_owned(), fmt(len_pump_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_EARTH_CARBONATOR".into(),
        [
            "~".to_owned(),
            fmt(len_earth_carbonator_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_RELAYS".into(),
        ["~".to_owned(), fmt(len_relays_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_VK".into(),
        ["~".to_owned(), fmt(len_vk_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_MAN_A_COM".into(),
        [
            "~".to_owned(),
            fmt(len_man_a_com_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_MAN_B_COM".into(),
        [
            "~".to_owned(),
            fmt(len_man_b_com_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_MAN_A_FANOUT".into(),
        [
            "~".to_owned(),
            fmt(len_man_a_fanout_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_MAN_B_FANOUT".into(),
        [
            "~".to_owned(),
            fmt(len_man_b_fanout_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_FLOW".into(),
        ["~".to_owned(), fmt(len_flow_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_ONEWIRE".into(),
        [
            "~".to_owned(),
            fmt(len_onewire_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_SENSORS_GND".into(),
        [
            "~".to_owned(),
            fmt(len_sensors_gnd_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_REEDS_GND".into(),
        [
            "~".to_owned(),
            fmt(len_reeds_gnd_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_MAN_A".into(),
        ["~".to_owned(), fmt(len_man_a_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_MOISTURE".into(),
        [
            "~".to_owned(),
            fmt(len_moisture_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_CARB_REEDS".into(),
        [
            "~".to_owned(),
            fmt(len_carb_reeds_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_MAN_B".into(),
        ["~".to_owned(), fmt(len_man_b_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_PUMP_FIXED".into(),
        [
            "~".to_owned(),
            fmt(len_pump_fixed_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_FRONT_FACE".into(),
        [
            "~".to_owned(),
            fmt(len_front_face_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_FAUCET_INBOARD".into(),
        [
            "~".to_owned(),
            fmt(len_faucet_inboard_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_REEDS_B".into(),
        [
            "~".to_owned(),
            fmt(len_reeds_b_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_FAN".into(),
        ["~".to_owned(), fmt(len_fan_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_REEDS_A".into(),
        [
            "~".to_owned(),
            fmt(len_reeds_a_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_GAS".into(),
        ["~".to_owned(), fmt(len_gas_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LEN_COMPRESSOR".into(),
        [
            "~".to_owned(),
            fmt(len_compressor_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_JOIN".into(),
        [
            "~".to_owned(),
            fmt(len_opening_join_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LEN_UMBILICAL".into(),
        [
            "~".to_owned(),
            fmt(len_umbilical_m, ".4g")?,
            " m".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "JST_PITCH".into(),
        [fmt(jst_pitch_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    let mut output = Output::document("hardware/wiring/ac-wiring-schedule.md", variables);
    output
        .exports
        .insert("line_voltage_v".into(), json!(line_voltage_v as i64));
    output
        .exports
        .insert("ac_primary_fuse_a".into(), json!(ac_primary_fuse_a as i64));
    output
        .exports
        .insert("awg_mains".into(), json!(awg_mains as i64));
    output
        .exports
        .insert("awg_ac_branch".into(), json!(awg_ac_branch as i64));
    output.exports.insert(
        "awg_compressor_lead".into(),
        json!(awg_compressor_lead as i64),
    );
    output
        .exports
        .insert("awg_sig".into(), json!(awg_sig as i64));
    output.exports.insert("awg_lv".into(), json!(awg_lv as i64));
    output
        .exports
        .insert("psu_primary_a".into(), json!(psu_primary_a));
    output
        .exports
        .insert("psu_full_load_w".into(), json!(psu_full_load_w as i64));
    output
        .exports
        .insert("psu_max_dc_a".into(), json!(psu_max_dc_a));
    output
        .exports
        .insert("diaphragm_peak_a".into(), json!(diaphragm_peak_a as i64));
    output
        .exports
        .insert("pump_peak_a".into(), json!(pump_peak_a));
    output
        .exports
        .insert("fan_current_a".into(), json!(fan_current_a));
    output
        .exports
        .insert("solenoid_coil_a".into(), json!(solenoid_coil_a));
    output.exports.insert(
        "max_simultaneous_valves".into(),
        json!(max_simultaneous_valves as i64),
    );
    output
        .exports
        .insert("board_peak_a".into(), json!(board_peak_a));
    output
        .exports
        .insert("coincident_peak_a".into(), json!(coincident_peak_a));
    output.exports.insert(
        "wago_221_413_rated_a".into(),
        json!(wago_221_413_rated_a as i64),
    );
    output
        .exports
        .insert("v_rail_dc".into(), json!(v_rail_dc as i64));
    output
        .exports
        .insert("v_rail_logic".into(), json!(v_rail_logic as i64));
    output.exports.insert("v_rail_io".into(), json!(v_rail_io));
    output
        .exports
        .insert("ds18b20_pullup_kohm".into(), json!(ds18b20_pullup_kohm));
    output.exports.insert(
        "compressor_wires_wall_relay".into(),
        json!(compressor_wires_wall_relay as i64),
    );
    output.exports.insert(
        "compressor_wires_local_relay".into(),
        json!(compressor_wires_local_relay as i64),
    );
    output
        .exports
        .insert("solenoid_count".into(), json!(solenoid_count as i64));
    output
        .exports
        .insert("len_short_mm".into(), json!(len_short_mm as i64));
    output
        .exports
        .insert("len_short_2_mm".into(), json!(len_short_2_mm as i64));
    output
        .exports
        .insert("len_dc1_mm".into(), json!(len_dc1_mm as i64));
    output
        .exports
        .insert("len_dc2_mm".into(), json!(len_dc2_mm as i64));
    output
        .exports
        .insert("len_mid_mm".into(), json!(len_mid_mm as i64));
    output
        .exports
        .insert("len_pump_mm".into(), json!(len_pump_mm as i64));
    output.exports.insert(
        "len_earth_carbonator_mm".into(),
        json!(len_earth_carbonator_mm as i64),
    );
    output
        .exports
        .insert("len_relays_mm".into(), json!(len_relays_mm as i64));
    output
        .exports
        .insert("len_vk_mm".into(), json!(len_vk_mm as i64));
    output
        .exports
        .insert("len_man_a_com_mm".into(), json!(len_man_a_com_mm as i64));
    output
        .exports
        .insert("len_man_b_com_mm".into(), json!(len_man_b_com_mm as i64));
    output
        .exports
        .insert("len_flow_mm".into(), json!(len_flow_mm as i64));
    output
        .exports
        .insert("len_onewire_mm".into(), json!(len_onewire_mm as i64));
    output.exports.insert(
        "len_sensors_gnd_mm".into(),
        json!(len_sensors_gnd_mm as i64),
    );
    output
        .exports
        .insert("len_reeds_gnd_mm".into(), json!(len_reeds_gnd_mm as i64));
    output
        .exports
        .insert("len_man_a_mm".into(), json!(len_man_a_mm as i64));
    output
        .exports
        .insert("len_moisture_mm".into(), json!(len_moisture_mm as i64));
    output
        .exports
        .insert("len_carb_reeds_mm".into(), json!(len_carb_reeds_mm as i64));
    output
        .exports
        .insert("len_man_b_mm".into(), json!(len_man_b_mm as i64));
    output.exports.insert(
        "len_man_a_fanout_mm".into(),
        json!(len_man_a_fanout_mm as i64),
    );
    output.exports.insert(
        "len_man_b_fanout_mm".into(),
        json!(len_man_b_fanout_mm as i64),
    );
    output
        .exports
        .insert("len_pump_fixed_mm".into(), json!(len_pump_fixed_mm as i64));
    output
        .exports
        .insert("len_front_face_mm".into(), json!(len_front_face_mm as i64));
    output.exports.insert(
        "len_faucet_inboard_mm".into(),
        json!(len_faucet_inboard_mm as i64),
    );
    output
        .exports
        .insert("len_reeds_b_mm".into(), json!(len_reeds_b_mm as i64));
    output
        .exports
        .insert("len_fan_mm".into(), json!(len_fan_mm as i64));
    output
        .exports
        .insert("len_reeds_a_mm".into(), json!(len_reeds_a_mm as i64));
    output
        .exports
        .insert("len_gas_mm".into(), json!(len_gas_mm as i64));
    output
        .exports
        .insert("len_compressor_mm".into(), json!(len_compressor_mm as i64));
    output.exports.insert(
        "len_opening_join_mm".into(),
        json!(len_opening_join_mm as i64),
    );
    output
        .exports
        .insert("len_umbilical_m".into(), json!(len_umbilical_m));
    output
        .exports
        .insert("jst_pitch_mm".into(), json!(jst_pitch_mm));
    Ok(output)
}
fn acceptance_and_burn_in(request: &Request) -> Result<Output> {
    let input = &request.input;
    let carbonator_wall_setpoint_c: f64 = 2.0;
    let carbonator_wall_band_c: f64 = 2.0;
    let evap_coil_freeze_cutout_c: f64 = -(8.0);
    let compressor_min_off_min: f64 = 3.0;
    let bench_water_press_min_psi: f64 = 40.0;
    let bench_water_press_max_psi: f64 = 80.0;
    let bench_water_temp_max_c: f64 = 20.0;
    let co2_cyl_small_lb: f64 = 5.0;
    let co2_cyl_large_lb: f64 = 10.0;
    let co2_primary_set_psi: f64 = 75.0;
    let co2_primary_set_tol_psi: f64 = 5.0;
    let co2_primary_relief_psi: f64 = 130.0;
    let co2_primary_relief_tol_psi: f64 = 4.0;
    let secondary_listed_psi: f64 = 44.0;
    let co2_centerline_psi: f64 = n(input, "secondary_regulator_pressure_psi")?;
    let glass_capacity_oz: f64 = crate::calibration_inputs::GLASS_CAPACITY_OZ;
    let graduated_cyl_min_ml: f64 = 250.0;
    let thermo_range_low_c: f64 = 0.0;
    let thermo_range_high_c: f64 = 20.0;
    let thermo_accuracy_c: f64 = 0.5;
    let refractometer_range_brix_low: f64 = 0.0;
    let refractometer_range_brix_high: f64 = 32.0;
    let concentrate_consumed_ml_per_unit: f64 = 50.0;
    let sodastream_bottle_ml: f64 = 440.0;
    let concentrate_consumed_pct: f64 = round(
        (concentrate_consumed_ml_per_unit / sodastream_bottle_ml) * 100.0,
        0,
    );
    let prv_hold_min: f64 = 2.0;
    let wall_disp_gate_c: f64 = carbonator_wall_setpoint_c + carbonator_wall_band_c;
    let dispense_temp_max_c: f64 = crate::calibration_inputs::DISPENSE_TEMP_MAX_C;
    let foam_head_hold_sec: f64 = 10.0;
    let syrup_ratio_water: f64 = crate::calibration_inputs::SYRUP_RATIO_WATER;
    let syrup_ratio_syrup: f64 = 1.0;
    let metered_water_ml: f64 = crate::calibration_inputs::METERED_WATER_ML;
    let metered_flavor_ml: f64 = crate::calibration_inputs::METERED_FLAVOR_ML;
    let metered_total_ml: f64 = crate::calibration_inputs::METERED_TOTAL_ML;
    let ratio_volume_tol_pct: f64 = crate::calibration_inputs::RATIO_VOLUME_TOL_PCT;
    let metered_total_low_ml: f64 =
        round(metered_total_ml * (1.0 - (ratio_volume_tol_pct / 100.0)), 0);
    let metered_total_high_ml: f64 =
        round(metered_total_ml * (1.0 + (ratio_volume_tol_pct / 100.0)), 0);
    let channel_to_channel_tol_pct: f64 = 10.0;
    let reservoir_burnin_fill_pct: f64 = 50.0;
    let burn_in_dispense_oz: f64 = 6.0;
    let burn_in_interval_min: f64 = 75.0;
    let burn_in_hours: f64 = 8.0;
    let burn_in_min_dispenses: f64 = 6.0;
    let duty_cycle_low_pct: f64 = 10.0;
    let duty_cycle_high_pct: f64 = 70.0;
    ensure!(
        co2_primary_set_psi - co2_primary_set_tol_psi
            > co2_centerline_psi.max(secondary_listed_psi),
        "primary factory setting must feed the PISCO preset from above"
    );
    ensure!(
        co2_primary_set_psi + co2_primary_set_tol_psi
            < co2_primary_relief_psi - co2_primary_relief_tol_psi,
        "primary factory setting reaches its blow-off"
    );
    let basis = list(input, "carbonation_basis_c")?;
    ensure!(
        basis.len() == 2
            && basis[0].as_f64() == Some(carbonator_wall_setpoint_c)
            && basis[1].as_f64() == Some(carbonator_wall_setpoint_c + carbonator_wall_band_c),
        "carbonation temperature basis differs from the wall setpoint"
    );
    let mut variables = Variables::new();
    variables.insert(
        "GPIO_RELAY2".into(),
        ["GPIO ".to_owned(), fmt(n(input, "_fc_gpio_relay2")?, "d")?].concat(),
    );
    variables.insert(
        "VALVE_COUNT".into(),
        [fmt(n(input, "_fc_valve_count")?, "d")?].concat(),
    );
    variables.insert(
        "WALL_SETPOINT".into(),
        [fmt(carbonator_wall_setpoint_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "WALL_BAND".into(),
        [
            "± ".to_owned(),
            fmt(carbonator_wall_band_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FREEZE_CUTOUT".into(),
        [
            "−".to_owned(),
            fmt((evap_coil_freeze_cutout_c).abs(), ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "MIN_OFF".into(),
        [fmt(compressor_min_off_min, ".4g")?, " min".to_owned()].concat(),
    );
    variables.insert(
        "WATER_PRESS_RANGE".into(),
        [
            fmt(bench_water_press_min_psi, ".4g")?,
            "–".to_owned(),
            fmt(bench_water_press_max_psi, ".4g")?,
            " PSI".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "WATER_TEMP_MAX".into(),
        [
            "~".to_owned(),
            fmt(bench_water_temp_max_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TAP_WATER_TEMP".into(),
        [
            "~".to_owned(),
            fmt(bench_water_temp_max_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CO2_CYL_SMALL".into(),
        [fmt(co2_cyl_small_lb, ".4g")?, " lb".to_owned()].concat(),
    );
    variables.insert(
        "CO2_CYL_LARGE".into(),
        [fmt(co2_cyl_large_lb, ".4g")?, " lb".to_owned()].concat(),
    );
    variables.insert(
        "CO2_PRIMARY_SET".into(),
        [fmt(co2_primary_set_psi, ".4g")?, " PSI".to_owned()].concat(),
    );
    variables.insert(
        "CO2_PRIMARY_TOL".into(),
        [
            "± ".to_owned(),
            fmt(co2_primary_set_tol_psi, ".4g")?,
            " PSI".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CO2_CENTERLINE".into(),
        [fmt(co2_centerline_psi, ".4g")?, " PSI".to_owned()].concat(),
    );
    variables.insert(
        "GLASS_OZ".into(),
        [fmt(glass_capacity_oz, ".4g")?, " oz".to_owned()].concat(),
    );
    variables.insert(
        "CYL_MIN".into(),
        [fmt(graduated_cyl_min_ml, ".4g")?, " mL".to_owned()].concat(),
    );
    variables.insert(
        "THERMO_RANGE".into(),
        [
            fmt(thermo_range_low_c, ".4g")?,
            "–".to_owned(),
            fmt(thermo_range_high_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "THERMO_ACC".into(),
        [
            "±".to_owned(),
            fmt(thermo_accuracy_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BRIX_RANGE".into(),
        [
            fmt(refractometer_range_brix_low, ".4g")?,
            "–".to_owned(),
            fmt(refractometer_range_brix_high, ".4g")?,
            " °Brix".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CONC_ML".into(),
        [
            "~".to_owned(),
            fmt(concentrate_consumed_ml_per_unit, ".4g")?,
            " mL".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CONC_PCT".into(),
        [
            "~".to_owned(),
            fmt(concentrate_consumed_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BOTTLE_L".into(),
        [fmt(sodastream_bottle_ml / 1000.0, ".2f")?, " L".to_owned()].concat(),
    );
    variables.insert(
        "PRV_HOLD".into(),
        [fmt(prv_hold_min, ".4g")?, "-minute".to_owned()].concat(),
    );
    variables.insert(
        "WALL_DISP_GATE".into(),
        [fmt(wall_disp_gate_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "DISP_TEMP_MAX".into(),
        [
            "~".to_owned(),
            fmt(dispense_temp_max_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DISP_TEMP_FAIL".into(),
        [fmt(dispense_temp_max_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "FOAM_HOLD".into(),
        [fmt(foam_head_hold_sec, ".4g")?, " seconds".to_owned()].concat(),
    );
    variables.insert(
        "RATIO".into(),
        [
            fmt(syrup_ratio_syrup, ".4g")?,
            ":".to_owned(),
            fmt(syrup_ratio_water, ".4g")?,
        ]
        .concat(),
    );
    variables.insert(
        "METERED_WATER".into(),
        [
            "~".to_owned(),
            fmt(metered_water_ml, ".4g")?,
            " mL".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "METERED_FLAVOR".into(),
        [
            "~".to_owned(),
            fmt(metered_flavor_ml, ".4g")?,
            " mL".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "METERED_TOTAL".into(),
        [
            "~".to_owned(),
            fmt(metered_total_ml, ".4g")?,
            " mL".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RATIO_TOL".into(),
        [
            "~".to_owned(),
            fmt(ratio_volume_tol_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RATIO_TOL_SIGNED".into(),
        [
            "±".to_owned(),
            fmt(ratio_volume_tol_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "METERED_RANGE".into(),
        [
            "~".to_owned(),
            fmt(metered_total_low_ml, ".4g")?,
            "–".to_owned(),
            fmt(metered_total_high_ml, ".4g")?,
            " mL".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CHANNEL_TOL".into(),
        [
            "~".to_owned(),
            fmt(channel_to_channel_tol_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CHANNEL_TOL_FAIL".into(),
        [fmt(channel_to_channel_tol_pct, ".4g")?, " %".to_owned()].concat(),
    );
    variables.insert(
        "RESERVOIR_FILL_PCT".into(),
        [
            "~".to_owned(),
            fmt(reservoir_burnin_fill_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BURN_IN_DISP".into(),
        [
            "~".to_owned(),
            fmt(burn_in_dispense_oz, ".4g")?,
            " oz".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DISP_INTERVAL".into(),
        [fmt(burn_in_interval_min, ".4g")?, " minutes".to_owned()].concat(),
    );
    variables.insert(
        "BURN_IN_HOURS".into(),
        [fmt(burn_in_hours, ".4g")?, " hours".to_owned()].concat(),
    );
    variables.insert(
        "BURN_IN_HOURS_DASH".into(),
        [fmt(burn_in_hours, ".4g")?, "-hour".to_owned()].concat(),
    );
    variables.insert(
        "BURN_IN_MIN_DISP".into(),
        [
            fmt(burn_in_min_dispenses, ".4g")?,
            " metered dispenses".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BURN_IN_MIN_DISP_SHORT".into(),
        [fmt(burn_in_min_dispenses, ".4g")?, " dispenses".to_owned()].concat(),
    );
    variables.insert(
        "BURN_IN_TARGET".into(),
        [
            fmt(burn_in_hours, ".4g")?,
            "-hour / ".to_owned(),
            fmt(burn_in_min_dispenses, ".4g")?,
            "-dispense".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DUTY_HIGH".into(),
        [
            "~".to_owned(),
            fmt(duty_cycle_high_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DUTY_LOW".into(),
        [
            "~".to_owned(),
            fmt(duty_cycle_low_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DUTY_BAND".into(),
        [
            fmt(duty_cycle_low_pct, ".4g")?,
            "–".to_owned(),
            fmt(duty_cycle_high_pct, ".4g")?,
            " %".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/acceptance-and-burn-in.md", variables);
    output.exports.insert(
        "carbonator_wall_setpoint_c".into(),
        json!(carbonator_wall_setpoint_c as i64),
    );
    output.exports.insert(
        "carbonator_wall_band_c".into(),
        json!(carbonator_wall_band_c as i64),
    );
    output.exports.insert(
        "evap_coil_freeze_cutout_c".into(),
        json!(evap_coil_freeze_cutout_c as i64),
    );
    output.exports.insert(
        "compressor_min_off_min".into(),
        json!(compressor_min_off_min as i64),
    );
    output.exports.insert(
        "bench_water_press_min_psi".into(),
        json!(bench_water_press_min_psi as i64),
    );
    output.exports.insert(
        "bench_water_press_max_psi".into(),
        json!(bench_water_press_max_psi as i64),
    );
    output.exports.insert(
        "bench_water_temp_max_c".into(),
        json!(bench_water_temp_max_c as i64),
    );
    output
        .exports
        .insert("co2_cyl_small_lb".into(), json!(co2_cyl_small_lb as i64));
    output
        .exports
        .insert("co2_cyl_large_lb".into(), json!(co2_cyl_large_lb as i64));
    output.exports.insert(
        "co2_primary_set_psi".into(),
        json!(co2_primary_set_psi as i64),
    );
    output.exports.insert(
        "co2_primary_set_tol_psi".into(),
        json!(co2_primary_set_tol_psi as i64),
    );
    output.exports.insert(
        "co2_primary_relief_psi".into(),
        json!(co2_primary_relief_psi as i64),
    );
    output.exports.insert(
        "co2_primary_relief_tol_psi".into(),
        json!(co2_primary_relief_tol_psi as i64),
    );
    output.exports.insert(
        "secondary_listed_psi".into(),
        json!(secondary_listed_psi as i64),
    );
    output
        .exports
        .insert("co2_centerline_psi".into(), json!(co2_centerline_psi));
    output
        .exports
        .insert("glass_capacity_oz".into(), json!(glass_capacity_oz as i64));
    output.exports.insert(
        "graduated_cyl_min_ml".into(),
        json!(graduated_cyl_min_ml as i64),
    );
    output.exports.insert(
        "thermo_range_low_c".into(),
        json!(thermo_range_low_c as i64),
    );
    output.exports.insert(
        "thermo_range_high_c".into(),
        json!(thermo_range_high_c as i64),
    );
    output
        .exports
        .insert("thermo_accuracy_c".into(), json!(thermo_accuracy_c));
    output.exports.insert(
        "refractometer_range_brix_low".into(),
        json!(refractometer_range_brix_low as i64),
    );
    output.exports.insert(
        "refractometer_range_brix_high".into(),
        json!(refractometer_range_brix_high as i64),
    );
    output.exports.insert(
        "concentrate_consumed_ml_per_unit".into(),
        json!(concentrate_consumed_ml_per_unit as i64),
    );
    output.exports.insert(
        "sodastream_bottle_ml".into(),
        json!(sodastream_bottle_ml as i64),
    );
    output.exports.insert(
        "concentrate_consumed_pct".into(),
        json!(concentrate_consumed_pct as i64),
    );
    output
        .exports
        .insert("prv_hold_min".into(), json!(prv_hold_min as i64));
    output
        .exports
        .insert("wall_disp_gate_c".into(), json!(wall_disp_gate_c as i64));
    output.exports.insert(
        "dispense_temp_max_c".into(),
        json!(dispense_temp_max_c as i64),
    );
    output.exports.insert(
        "foam_head_hold_sec".into(),
        json!(foam_head_hold_sec as i64),
    );
    output
        .exports
        .insert("syrup_ratio_water".into(), json!(syrup_ratio_water as i64));
    output
        .exports
        .insert("syrup_ratio_syrup".into(), json!(syrup_ratio_syrup as i64));
    output
        .exports
        .insert("metered_water_ml".into(), json!(metered_water_ml as i64));
    output
        .exports
        .insert("metered_flavor_ml".into(), json!(metered_flavor_ml));
    output
        .exports
        .insert("metered_total_ml".into(), json!(metered_total_ml));
    output.exports.insert(
        "ratio_volume_tol_pct".into(),
        json!(ratio_volume_tol_pct as i64),
    );
    output.exports.insert(
        "metered_total_low_ml".into(),
        json!(metered_total_low_ml as i64),
    );
    output.exports.insert(
        "metered_total_high_ml".into(),
        json!(metered_total_high_ml as i64),
    );
    output.exports.insert(
        "channel_to_channel_tol_pct".into(),
        json!(channel_to_channel_tol_pct as i64),
    );
    output.exports.insert(
        "reservoir_burnin_fill_pct".into(),
        json!(reservoir_burnin_fill_pct as i64),
    );
    output.exports.insert(
        "burn_in_dispense_oz".into(),
        json!(burn_in_dispense_oz as i64),
    );
    output.exports.insert(
        "burn_in_interval_min".into(),
        json!(burn_in_interval_min as i64),
    );
    output
        .exports
        .insert("burn_in_hours".into(), json!(burn_in_hours as i64));
    output.exports.insert(
        "burn_in_min_dispenses".into(),
        json!(burn_in_min_dispenses as i64),
    );
    output.exports.insert(
        "duty_cycle_low_pct".into(),
        json!(duty_cycle_low_pct as i64),
    );
    output.exports.insert(
        "duty_cycle_high_pct".into(),
        json!(duty_cycle_high_pct as i64),
    );
    Ok(output)
}
fn asse_drain(request: &Request) -> Result<Output> {
    let input = &request.input;
    let mut variables = Variables::new();
    variables.insert(
        "DRAIN_OD".into(),
        [fmt(n(input, "_drain.OD")?, "g")?].concat(),
    );
    variables.insert(
        "DRAIN_ID".into(),
        [fmt(n(input, "_drain.ID")?, "g")?].concat(),
    );
    variables.insert(
        "DRAIN_WALL".into(),
        [fmt(
            (n(input, "_drain.OD")? - n(input, "_drain.ID")?) / 2.0,
            "g",
        )?]
        .concat(),
    );
    variables.insert(
        "DRAIN_BEND_R".into(),
        [fmt(n(input, "_drain.MIN_R")?, "g")?].concat(),
    );
    variables.insert(
        "DRAIN_THREAD_D".into(),
        [fmt(n(input, "bulkhead.THREAD_D")?, "g")?].concat(),
    );
    variables.insert(
        "DRAIN_THREAD_PITCH".into(),
        [fmt(n(input, "bulkhead.THREAD_PITCH")?, "g")?].concat(),
    );
    variables.insert(
        "DRAIN_PANEL_BARREL".into(),
        [fmt(n(input, "bulkhead.PANEL_THREAD")?, "g")?].concat(),
    );
    let output = Output::document("hardware/assembly/asse-drain.md", variables);
    Ok(output)
}
fn cold_core(request: &Request) -> Result<Output> {
    let input = &request.input;
    let cap_clamp_inserts: f64 = (list(input, "attachment_xy_positions")?.len() as f64) * 2.0;
    let cap_face_screws: f64 = list(input, "attachment_xy_positions")?.len() as f64;
    let reservoir_inserts: f64 =
        (list(input, "insert_positions_for_side_plus_1")?.len() as f64) * 2.0;
    let b_fill_clamps: f64 = 0.0;
    let cap_deck_inserts: f64 = list(input, "deck_mount_positions")?
        .iter()
        .map(|v| v.as_array().map_or(0, Vec::len))
        .sum::<usize>() as f64;
    let mut variables = Variables::new();
    variables.insert(
        "GROOVE_DEPTH".into(),
        [
            fmt(n(input, "_coil_mandrel_gen.groove_depth")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "MANDREL_OD".into(),
        [
            fmt(n(input, "_coil_mandrel_gen.mandrel_od")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TANK_OD".into(),
        [
            fmt(n(input, "_coil_mandrel_gen.carbonator_od")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "NET_UNDERSIZE".into(),
        [
            fmt(n(input, "_coil_mandrel_gen.net_undersize")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "WIND_LENGTH".into(),
        [
            fmt(n(input, "_coil_mandrel_gen.wind_length")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TOTAL_WRAPS".into(),
        [fmt(n(input, "_coil_gen.TOTAL_WRAPS")?, ".3f")?].concat(),
    );
    variables.insert(
        "PITCH".into(),
        [fmt(n(input, "_coil_gen.PITCH")?, ".2f")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "SPRUNG_LEN".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.fitted_wrap_length")? / 1000.0,
                ".4g",
            )?,
            " m".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LAID_FT".into(),
        [
            fmt(n(input, "_coil_gen.wrap_length()")? / 304.8, ".4g")?,
            " ft".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "STUB_INLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_allowance['inlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "STUB_OUTLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_allowance['outlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PROT_INLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_protrusion['inlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PROT_OUTLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_protrusion['outlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ROLL_SHARE".into(),
        [
            "1/".to_owned(),
            fmt(n(input, "_coil_mandrel_gen.carbonators_per_roll")?, "")?,
        ]
        .concat(),
    );
    variables.insert(
        "CUT_FT".into(),
        [
            fmt(n(input, "_coil_gen.cut_length()")? / 304.8, ".4g")?,
            " ft".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TAIL_INLET_Y".into(),
        [fmt(n(input, "_coil_mandrel_gen.tail_inlet_y")?, ".4g")?].concat(),
    );
    variables.insert(
        "TAIL_OUTLET_Y".into(),
        [fmt(n(input, "_coil_mandrel_gen.tail_outlet_y")?, ".4g")?].concat(),
    );
    variables.insert(
        "CAP_H".into(),
        [
            fmt(
                n(input, "bottom_cap_height")? - n(input, "wall_and_floor_thickness")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CAP_H_TOP".into(),
        [
            fmt(
                n(input, "foam_shell_rim_z")? - n(input, "foam_shell_outer_height")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FOAM_CAP_LID_H".into(),
        [
            fmt(n(input, "foam_cap_lid_height")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "POUR_D".into(),
        [
            fmt(n(input, "bottom_pour_radius")? * 2.0, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LID_VENT_D".into(),
        [
            fmt(n(input, "foam_cap_lid_vent_radius")? * 2.0, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "INSERT_POCKET_D".into(),
        [
            fmt(n(input, "insert_pocket_radius")? * 2.0, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "INSERT_LEN".into(),
        [fmt(n(input, "insert_length")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "INSERT_RELIEF".into(),
        [
            fmt(
                n(input, "insert_pocket_depth")? - n(input, "insert_length")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CC_INSERTS".into(),
        [fmt(
            ((cap_clamp_inserts + cap_deck_inserts) + reservoir_inserts) + b_fill_clamps,
            "",
        )?]
        .concat(),
    );
    variables.insert(
        "CAP_INSERTS".into(),
        [fmt(
            (cap_clamp_inserts + cap_deck_inserts) + b_fill_clamps,
            "",
        )?]
        .concat(),
    );
    variables.insert("B_FILL_CLAMPS".into(), fmt(b_fill_clamps, "")?);
    variables.insert(
        "CAP_CLAMP_INSERTS".into(),
        [fmt(cap_clamp_inserts, "")?].concat(),
    );
    variables.insert(
        "CAP_FACE_SCREWS".into(),
        [fmt(cap_face_screws, "")?].concat(),
    );
    variables.insert(
        "CAP_DECK_INSERTS".into(),
        [fmt(cap_deck_inserts, "")?].concat(),
    );
    variables.insert("RES_INSERTS".into(), [fmt(reservoir_inserts, "")?].concat());
    variables.insert(
        "TUBE_HOLE_D".into(),
        [
            fmt(n(input, "port_hole_radius")? * 2.0, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "COTWO_INLET_Y".into(),
        [fmt(n(input, "co2_inlet_y")?, ".4g")?].concat(),
    );
    variables.insert(
        "TOP_BAND".into(),
        [fmt(n(input, "top_band_to_cap")?, ".4g")?].concat(),
    );
    variables.insert(
        "LLDPE_BEND_R".into(),
        [
            fmt(n(input, "lldpe_bend_radius")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FORWARD_BAND".into(),
        [
            fmt(n(input, "forward_band_width")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "REED_CONDUIT_XY".into(),
        [
            "reed-cable-a (".into(),
            fmt(
                n(input, "cap_conduit_shell_xy(\"reed-cable-a\")[0]")?,
                ".4g",
            )?,
            ", ".into(),
            fmt(
                n(input, "cap_conduit_shell_xy(\"reed-cable-a\")[1]")?,
                ".4g",
            )?,
            ")".into(),
        ]
        .concat(),
    );
    variables.insert(
        "RESERVOIR_GAP".into(),
        [
            fmt(n(input, "reservoir_clearance")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SHELL_OUTER_X".into(),
        [
            fmt(n(input, "outer_shell_x_length")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CCORE_OUTER_Y".into(),
        [fmt(n(input, "outer_shell_y_length")?, ".4g")?].concat(),
    );
    variables.insert(
        "OUTER_H".into(),
        [fmt(n(input, "foam_shell_rim_z")?, ".2f")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "CCORE_CAPPED_H".into(),
        [
            fmt(n(input, "cap_face_z")? - n(input, "stack_floor_z")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LOW_LEVEL".into(),
        [
            fmt(n(input, "_reed_bridge_gen.low_level_z")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "HIGH_LEVEL".into(),
        [
            fmt(n(input, "_reed_bridge_gen.high_level_z")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "REED_LOW_Z".into(),
        [
            fmt(n(input, "_reed_bridge_gen.reed_low_z")?, ".3f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "REED_HIGH_Z".into(),
        [
            fmt(n(input, "_reed_bridge_gen.reed_high_z")?, ".3f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "INTER_WRAP_CLEAR".into(),
        [
            fmt(n(input, "_reed_bridge_gen.inter_wrap_clear")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BRIDGE_Z_BOTTOM".into(),
        [
            fmt(n(input, "_reed_bridge_gen.bridge_z_bottom")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "POCKET_DEPTH".into(),
        [
            fmt(n(input, "_reed_bridge_gen.pocket_depth")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/cold-core.md", variables);
    output
        .exports
        .insert("CAP_CLAMP_INSERTS".into(), json!(cap_clamp_inserts as i64));
    output
        .exports
        .insert("CAP_FACE_SCREWS".into(), json!(cap_face_screws as i64));
    output
        .exports
        .insert("RESERVOIR_INSERTS".into(), json!(reservoir_inserts as i64));
    output
        .exports
        .insert("B_FILL_CLAMPS".into(), json!(b_fill_clamps as i64));
    output
        .exports
        .insert("CAP_DECK_INSERTS".into(), json!(cap_deck_inserts as i64));
    let mut variables = Variables::new();
    variables.insert(
        "CO2_INLET_Y".into(),
        [fmt(n(input, "_port_cuts.co2_inlet_y")?, ".4g")?].concat(),
    );
    variables.insert(
        "FRONT_FACE_PORT_Z".into(),
        [fmt(n(input, "_port_cuts.front_face_port_z")?, ".4g")?].concat(),
    );
    variables.insert(
        "PORT_HOLE_DIAMETER".into(),
        [fmt(n(input, "port_hole_radius")? * 2.0, ".4g")?].concat(),
    );
    output.jobs.push(Job {
        path: "hardware/printed-parts/cold-core/_port_cuts.py".into(),
        kind: "python".into(),
        variables,
    });
    output.stdout.push_str("-> _port_cuts.py\n");
    let mut variables = Variables::new();
    variables.insert(
        "PORT_HOLE_DIAMETER".into(),
        [fmt(n(input, "port_hole_radius")? * 2.0, ".4g")?].concat(),
    );
    variables.insert(
        "LLDPE_TUBE_OD".into(),
        [fmt(n(input, "lldpe_tube_od")?, ".4g")?].concat(),
    );
    output.jobs.push(Job {
        path: "hardware/printed-parts/cold-core/_internal_routes.py".into(),
        kind: "python".into(),
        variables,
    });
    output.stdout.push_str("-> _internal_routes.py\n");
    Ok(output)
}
fn electronics_bay(request: &Request) -> Result<Output> {
    let _input = &request.input;
    let relay_compressor_gpio: f64 = 19.0;
    let relay_diaphragm_gpio: f64 = 2.0;
    let variables = Variables::new();
    let mut output = Output::document("hardware/assembly/electronics-bay.md", variables);
    output.exports.insert(
        "relay_compressor_gpio".into(),
        json!(relay_compressor_gpio as i64),
    );
    output.exports.insert(
        "relay_diaphragm_gpio".into(),
        json!(relay_diaphragm_gpio as i64),
    );
    Ok(output)
}
fn enclosure_mechanical(request: &Request) -> Result<Output> {
    let input = &request.input;
    let bay_width: f64 = (n(input, "compressor.xmax")?).max(n(input, "condenser.xmax")?)
        - (n(input, "compressor.xmin")?).min(n(input, "condenser.xmin")?);
    let mut variables = Variables::new();
    variables.insert(
        "BOX_SIZE".into(),
        [
            fmt(n(input, "outer[1]")? - n(input, "outer[0]")?, ".6g")?,
            " × ".to_owned(),
            fmt(n(input, "outer[3]")? - n(input, "outer[2]")?, ".6g")?,
            " × ".to_owned(),
            fmt(n(input, "outer[5]")? - n(input, "outer[4]")?, ".6g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "WALL_T".into(),
        [fmt(n(input, "enc.wall")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "FLOOR_T".into(),
        [fmt(n(input, "enc.floor_t")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "FRONT_WALL".into(),
        [fmt(n(input, "enc.front_wall")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "FRONT_TOP_FLANK".into(),
        [
            fmt(n(input, "enc.front_top_flank_t")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BACK_TOP_FLANK".into(),
        [
            fmt(n(input, "enc.back_top_flank_t")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CEILING_LANE".into(),
        [fmt(
            (n(input, "enc.appliance_height")? - n(input, "enc.floor_t")?) - n(input, "enc.wall")?,
            ".4g",
        )?]
        .concat(),
    );
    variables.insert(
        "LIP_UNDERWALL".into(),
        [fmt(2.0 * n(input, "enc.wall")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "Y_SEAM".into(),
        [fmt(n(input, "box['y_joint']")?, ".4g")?].concat(),
    );
    for (key, value) in input["enc.y_stack_figures(box['inner'])"]
        .as_object()
        .context("provider figures")?
    {
        variables.insert(
            key.clone(),
            value.as_str().context("figure string")?.to_owned(),
        );
    }
    variables.insert(
        "Z_SEAM_FRONT".into(),
        [fmt(n(input, "box['splits'][0]")?, ".4g")?].concat(),
    );
    variables.insert("RAIL_TRAVEL_FRONT".into(), [fmt(n(input, "enc._z_rail_travel(box['inner'], box['y_joint'], 'front', plate if box['pump_bay'] else None, box['vent_chase'])")?, ".4g")?, " mm".to_owned()].concat());
    variables.insert(
        "DOCK_TEES".into(),
        [fmt(list(input, "plate['holes']")?.len() as f64, "")?].concat(),
    );
    variables.insert(
        "APPLIANCE_W".into(),
        [
            fmt(n(input, "enc.appliance_width")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert("COMP_BAY_X".into(), [fmt(bay_width, ".0f")?].concat());
    variables.insert(
        "CORE_X".into(),
        [fmt(n(input, "outer_shell_y_length")?, ".0f")?].concat(),
    );
    variables.insert(
        "SIDE_BAND".into(),
        [
            fmt(n(input, "enc.side_band_inset")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CORE_HOLD_REACH".into(),
        [
            fmt(n(input, "enc.core_hold_reach")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "REAR_SEAM_CLEAR".into(),
        [
            fmt(n(input, "enc.rear_seam_clear")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "Y_OVERLAP".into(),
        [fmt(n(input, "enc.lip_len")?, ".3g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "GROMMET_SQUEEZE".into(),
        [fmt(
            n(input, "facts.constants.FLOOR_GROMMET_SQUEEZE")?,
            ".4g",
        )?]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/enclosure-mechanical.md", variables);
    output.exports.insert("bay_width".into(), json!(bay_width));
    Ok(output)
}
fn faucet_and_umbilical(request: &Request) -> Result<Output> {
    let input = &request.input;
    let plate_gasket: f64 = n(input, "faucet.above_counter_plate.plate_thickness")?
        + n(input, "faucet.above_counter_gasket.gasket_thickness")?;
    let mut variables = Variables::new();
    variables.insert(
        "CAP_HOLE_D".into(),
        [
            fmt(n(input, "tpu.cap_hole_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "WESTBRASS_PORT_D".into(),
        [
            fmt(n(input, "tpu.westbrass_port_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORING_OUTER_D".into(),
        [
            fmt(n(input, "tpu.outer_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "WESTBRASS_SQUEEZE".into(),
        [
            fmt(n(input, "tpu.westbrass_squeeze")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORING_INNER_D".into(),
        [
            fmt(n(input, "tpu.inner_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LLDPE_INTERFERENCE".into(),
        [
            fmt(n(input, "tpu.lldpe_interference")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TOTAL_H".into(),
        [fmt(n(input, "tpu.total_height")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "ORING_CAP_T".into(),
        [
            fmt(n(input, "tpu.cap_thickness")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CYL_L".into(),
        [
            fmt(n(input, "tpu.cylinder_length")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "LLDPE_ID".into(),
        [fmt(n(input, "tpu.lldpe_id")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LLDPE_OD".into(),
        [fmt(n(input, "tpu.lldpe_od")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "PLATE_D".into(),
        [
            fmt(n(input, "plate.disc_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SHANK_HOLE_D".into(),
        [
            fmt(n(input, "plate.shank_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PILL_L".into(),
        [
            fmt(n(input, "plate.pill_long_y")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PILL_W".into(),
        [
            fmt(n(input, "plate.pill_short_x")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FILLET_R".into(),
        [
            fmt(n(input, "plate.fillet_radius")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "COUNTERTOP_HOLE_D".into(),
        [
            fmt(n(input, "faucet.countertop_hole_diameter")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "GASKET_COVER".into(),
        [
            fmt(n(input, "faucet.gasket_hole_cover()")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "COLLAR_LENGTH".into(),
        [
            fmt(n(input, "faucet.tube_collar.LENGTH")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "COLLAR_BORE_PRINTED".into(),
        [fmt(n(input, "faucet.tube_collar.bore_printed()")?, ".4g")?].concat(),
    );
    variables.insert(
        "COLLAR_TUBE_OD".into(),
        [fmt(n(input, "faucet.tube_collar.TUBE_OD")?, ".4g")?].concat(),
    );
    variables.insert(
        "COLLAR_SLEEVE_TAIL".into(),
        [
            fmt(n(input, "faucet.foam_bare_at_wall")?, ".3g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_PLATE_GAP".into(),
        [
            fmt(
                n(input, "faucet.under_counter_plate_bottom_z")?
                    - n(input, "faucet.organizer_top_z")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_TOP_Z".into(),
        [
            fmt(n(input, "faucet.organizer_top_z")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_LENGTH".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.LENGTH")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_TUBE_BORE".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.TUBE_BORE")?, ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_FLAVOR_BORE".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.FLAVOR_BORE")?, ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_DRAIN_BORE".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.DRAIN_BORE")?, ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_CABLE_SLOT".into(),
        [
            fmt(
                n(input, "faucet.umbilical_organizer.CABLE_SLOT_LENGTH")?,
                "g",
            )?,
            " × ".to_owned(),
            fmt(
                n(input, "faucet.umbilical_organizer.CABLE_SLOT_DEPTH")?,
                "g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_MIN_MATERIAL".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.MIN_MATERIAL")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_FLAVOR_SPREAD".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.FLAVOR_SPREAD")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_FLAVOR_FORWARD".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.FLAVOR_FORWARD")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ORGANIZER_DRAIN_FORWARD".into(),
        [
            fmt(n(input, "faucet.umbilical_organizer.DRAIN_FORWARD")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RIBBON_T".into(),
        [
            fmt(n(input, "faucet.cable_lane")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RIBBON_SECTION".into(),
        [
            fmt(n(input, "faucet.cable_lane")?, ".4g")?,
            " × ".to_owned(),
            fmt(n(input, "faucet.cable_width")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SLEEVE_GIRTH".into(),
        [
            fmt(n(input, "faucet.bundle_girth()")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SLEEVE_BORE".into(),
        [
            fmt(n(input, "faucet.bundle_bore()")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SLEEVE_BORE_IN".into(),
        [
            fmt(n(input, "faucet.bundle_bore()")? / 25.4, ".3g")?,
            "\"".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TURN_IN".into(),
        [fmt(
            n(input, "envelope.TURN_IN_LEAD_BEND")? + n(input, "collet")?,
            "g",
        )?]
        .concat(),
    );
    variables.insert("PLATE_GASKET".into(), [fmt(plate_gasket, "g")?].concat());
    variables.insert(
        "FLAVOR_CUT".into(),
        [fmt(n(input, "faucet.flavor_cut_length")?, "g")?].concat(),
    );
    variables.insert(
        "BLUE_CUT".into(),
        [fmt(n(input, "faucet.blue_cut_length")?, "g")?].concat(),
    );
    variables.insert(
        "DRAIN_CUT".into(),
        [fmt(n(input, "faucet.drain_factory_cut_length()")?, "g")?].concat(),
    );
    variables.insert(
        "FAUCET_FLAVOR_RUN".into(),
        [fmt(n(input, "faucet.flavor_path_above_foot()")?, ".1f")?].concat(),
    );
    variables.insert(
        "CUT_DIFFERENCE".into(),
        [fmt(
            n(input, "faucet.flavor_cut_length")? - n(input, "faucet.blue_cut_length")?,
            "g",
        )?]
        .concat(),
    );
    variables.insert(
        "TAIL_OFFSET".into(),
        [fmt(n(input, "faucet.tails_apart")?, ".2f")?].concat(),
    );
    variables.insert(
        "FAUCET_PLATE_T".into(),
        [fmt(
            n(input, "faucet.above_counter_plate.plate_thickness")?,
            "g",
        )?]
        .concat(),
    );
    variables.insert(
        "FLAVOR_NOMINAL".into(),
        [fmt(
            ((1200.0 + n(input, "faucet.countertop_thickness")?) + plate_gasket)
                + n(input, "faucet.flavor_path_above_foot()")?,
            ".0f",
        )?]
        .concat(),
    );
    variables.insert(
        "BLUE_NOMINAL".into(),
        [fmt(
            (1200.0 + n(input, "faucet.soda_umbilical_tube_z_top")?)
                - n(input, "faucet.countertop_bottom_z")?,
            ".0f",
        )?]
        .concat(),
    );
    variables.insert(
        "SODA_FAUCET_CUT".into(),
        [fmt(n(input, "faucet.soda_faucet_cut_length")?, "g")?].concat(),
    );
    variables.insert(
        "COUNTERTOP_MAX_THICKNESS".into(),
        [
            fmt(n(input, "faucet.countertop_max_thickness")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FOAM_LENGTH".into(),
        [fmt(n(input, "faucet.foam_length")?, ".0f")?].concat(),
    );
    variables.insert(
        "FOAM_BARE_TOP".into(),
        [
            fmt(n(input, "faucet.foam_bare_at_westbrass")?, ".0f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SLEEVE_ABOVE_FOAM".into(),
        [
            fmt(
                n(input, "faucet.sleeve_z_top")? - n(input, "faucet.umbilical_z_bottom")?,
                ".0f",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "UNION_SLEEVE_BORE".into(),
        [
            fmt(
                n(input, "faucet.bare_bundle_girth()")? / std::f64::consts::PI,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/faucet-and-umbilical.md", variables);
    output
        .exports
        .insert("plate_gasket".into(), json!(plate_gasket));
    Ok(output)
}
fn finish_pack_ship(request: &Request) -> Result<Output> {
    let _input = &request.input;
    let founder_edition_count: f64 = 50.0;
    let founder_edition_price_usd: f64 = 7500.0;
    let water_drained_kg: f64 = 1.5;
    let flavor_drained_kg: f64 = 1.0;
    let appliance_weight_low_kg: f64 = 10.0;
    let appliance_weight_high_kg: f64 = 15.0;
    let carton_gross_weight_low_kg: f64 = 15.0;
    let carton_gross_weight_high_kg: f64 = 20.0;
    let carton_length_cm: f64 = 60.0;
    let carton_width_cm: f64 = 50.0;
    let carton_height_cm: f64 = 50.0;
    let scale_precision_kg: f64 = 0.1;
    let carrier_ground_limit_lb: f64 = 70.0;
    let carrier_ground_limit_kg: f64 = 32.0;
    let splash_check_tilt_deg: f64 = 15.0;
    let mut variables = Variables::new();
    variables.insert(
        "FOUNDER_EDITION_COUNT".into(),
        [fmt(founder_edition_count, ".4g")?].concat(),
    );
    variables.insert(
        "FOUNDER_EDITION_PRICE".into(),
        ["$".to_owned(), fmt(founder_edition_price_usd, ",")?].concat(),
    );
    variables.insert(
        "WATER_DRAINED".into(),
        [
            "~".to_owned(),
            fmt(water_drained_kg, ".4g")?,
            " kg".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FLAVOR_DRAINED".into(),
        [
            "~".to_owned(),
            fmt(flavor_drained_kg, ".4g")?,
            " kg".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "APPLIANCE_W_LOW".into(),
        [fmt(appliance_weight_low_kg, ".4g")?].concat(),
    );
    variables.insert(
        "APPLIANCE_W_HIGH".into(),
        [fmt(appliance_weight_high_kg, ".4g")?, " kg".to_owned()].concat(),
    );
    variables.insert(
        "CARTON_W_LOW".into(),
        [fmt(carton_gross_weight_low_kg, ".4g")?].concat(),
    );
    variables.insert(
        "CARTON_W_HIGH".into(),
        [fmt(carton_gross_weight_high_kg, ".4g")?, " kg".to_owned()].concat(),
    );
    variables.insert(
        "SLOSH_CARTON_W".into(),
        [fmt(carton_gross_weight_high_kg, ".4g")?, " kg".to_owned()].concat(),
    );
    variables.insert("CARTON_L".into(), [fmt(carton_length_cm, ".4g")?].concat());
    variables.insert(
        "CARTON_W_DIM".into(),
        [fmt(carton_width_cm, ".4g")?].concat(),
    );
    variables.insert(
        "CARTON_H_DIM".into(),
        [fmt(carton_height_cm, ".4g")?, " cm".to_owned()].concat(),
    );
    variables.insert(
        "SCALE_PRECISION".into(),
        [fmt(scale_precision_kg, ".4g")?, " kg".to_owned()].concat(),
    );
    variables.insert(
        "TILT_ANGLE".into(),
        [
            "~".to_owned(),
            fmt(splash_check_tilt_deg, ".4g")?,
            "°".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CARRIER_LIMIT_LB".into(),
        [fmt(carrier_ground_limit_lb, ".4g")?, " lb".to_owned()].concat(),
    );
    variables.insert(
        "CARRIER_LIMIT_KG".into(),
        [
            "~".to_owned(),
            fmt(carrier_ground_limit_kg, ".4g")?,
            " kg".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/finish-pack-ship.md", variables);
    output.exports.insert(
        "founder_edition_count".into(),
        json!(founder_edition_count as i64),
    );
    output.exports.insert(
        "founder_edition_price_usd".into(),
        json!(founder_edition_price_usd as i64),
    );
    output
        .exports
        .insert("water_drained_kg".into(), json!(water_drained_kg));
    output
        .exports
        .insert("flavor_drained_kg".into(), json!(flavor_drained_kg));
    output.exports.insert(
        "appliance_weight_low_kg".into(),
        json!(appliance_weight_low_kg as i64),
    );
    output.exports.insert(
        "appliance_weight_high_kg".into(),
        json!(appliance_weight_high_kg as i64),
    );
    output.exports.insert(
        "carton_gross_weight_low_kg".into(),
        json!(carton_gross_weight_low_kg as i64),
    );
    output.exports.insert(
        "carton_gross_weight_high_kg".into(),
        json!(carton_gross_weight_high_kg as i64),
    );
    output
        .exports
        .insert("carton_length_cm".into(), json!(carton_length_cm as i64));
    output
        .exports
        .insert("carton_width_cm".into(), json!(carton_width_cm as i64));
    output
        .exports
        .insert("carton_height_cm".into(), json!(carton_height_cm as i64));
    output
        .exports
        .insert("scale_precision_kg".into(), json!(scale_precision_kg));
    output.exports.insert(
        "carrier_ground_limit_lb".into(),
        json!(carrier_ground_limit_lb as i64),
    );
    output.exports.insert(
        "carrier_ground_limit_kg".into(),
        json!(carrier_ground_limit_kg as i64),
    );
    output.exports.insert(
        "splash_check_tilt_deg".into(),
        json!(splash_check_tilt_deg as i64),
    );
    Ok(output)
}
fn handwork(request: &Request) -> Result<Output> {
    let input = &request.input;
    let mm_per_in: f64 = 25.4;
    let mut variables = Variables::new();
    variables.insert(
        "ROD_LEN".into(),
        [
            fmt(n(input, "carbonator_rod_len")? / mm_per_in, ".3f")?,
            " ±".to_owned(),
            fmt(n(input, "carbonator_rod_tolerance")? / mm_per_in, ".3f")?,
            " in (".to_owned(),
            fmt(n(input, "carbonator_rod_len")?, ".2f")?,
            " ±".to_owned(),
            fmt(n(input, "carbonator_rod_tolerance")?, ".2f")?,
            " mm)".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RESERVOIR_ROD_LEN".into(),
        [
            fmt(n(input, "reservoir.reservoir_rod_len")?, ".4g")?,
            " mm (".to_owned(),
            fmt(n(input, "reservoir.reservoir_rod_len")? / mm_per_in, ".3g")?,
            " in)".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PITCH".into(),
        [fmt(n(input, "_coil_gen.PITCH")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "LAID_FT".into(),
        [
            fmt(n(input, "_coil_gen.wrap_length()")? / 304.8, ".4g")?,
            " ft".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "STUB_INLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_allowance['inlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "STUB_OUTLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_allowance['outlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/handwork.md", variables);
    output.exports.insert("MM_PER_IN".into(), json!(mm_per_in));
    Ok(output)
}
fn internal_plumbing(request: &Request) -> Result<Output> {
    let input = &request.input;
    let reservoir_a_lengths = route_lengths(&input["reservoir_a_route_specs"])?;
    let mut variables = Variables::new();
    variables.insert(
        "MANIFOLD_TEES".into(),
        [fmt(
            list(input, "manifold.PURCHASED_TEES")?.len() as f64,
            "",
        )?]
        .concat(),
    );
    variables.insert(
        "DOCK_TEE_STROKE".into(),
        [
            fmt(
                n(input, "manifold._returns.tee.BRANCH_COLLET_TRAVEL")?,
                ".3g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_TEE_INSERTION".into(),
        [
            fmt(n(input, "manifold._returns.RUN_INSERTION")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_VALVE_INSERTION".into(),
        [
            fmt(
                n(input, "manifold._returns.VALVE_INSERTION_NOMINAL")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_FORE_LINK".into(),
        [
            fmt(n(input, "manifold.FORE_STUB_EXPOSED")?, ".6g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_UPPER_TAIL".into(),
        [
            fmt(
                (n(input, "manifold.FORE_STUB_EXPOSED")?
                    + n(input, "manifold._returns.RUN_INSERTION")?)
                    + n(input, "manifold._returns.VALVE_INSERTION_NOMINAL")?,
                ".6g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_RETURN_INNER".into(),
        [fmt(n(input, "returns['Y-C']")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "DOCK_RETURN_OUTER".into(),
        [fmt(n(input, "returns['Y-D']")?, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "DOCK_ELBOW_SOCKET".into(),
        [
            fmt(n(input, "manifold._returns.elbow.SOCKET_INSERTION")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_TEE_ELBOW_STEM".into(),
        [
            fmt(n(input, "elbows[0]['stem']")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_VALVE_ELBOW_STEM".into(),
        [
            fmt(n(input, "elbows[1]['stem']")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_VALVE_ELBOW_SHOWING".into(),
        [
            fmt(n(input, "elbows[1]['showing']")?, ".3g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_PUMP_TUBE_CUT".into(),
        [
            fmt(n(input, "manifold.PUMP_TUBE_CUT")?, ".3g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DOCK_BODY_GAP".into(),
        [
            fmt(
                n(input, "enc.bay_back_y(box['collet_plate'])")?
                    - n(
                        input,
                        "enc.pump_cartridge_aft_y(box['pump_trays'], box['collet_plate'])",
                    )?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RESERVOIR_A_FILL_WARM".into(),
        [
            fmt(
                *reservoir_a_lengths
                    .get("fluid-14")
                    .context("reservoir route")?,
                ".3f",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RESERVOIR_A_DRAW_WARM".into(),
        [
            fmt(
                *reservoir_a_lengths
                    .get("fluid-16")
                    .context("reservoir route")?,
                ".3f",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RESERVOIR_B_FILL_WARM".into(),
        [
            fmt(
                n(
                    input,
                    "next((run.length for run in facts.runs if run.id == 'fluid-24'))",
                )?,
                ".3f",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    let output = Output::document("hardware/assembly/internal-plumbing.md", variables);
    Ok(output)
}
fn refrigerant_loop(request: &Request) -> Result<Output> {
    let input = &request.input;
    let unit_a_factory_charge_g: f64 = 15.0;
    let unit_b_factory_charge_g: f64 = 23.0;
    let system_charge_approx_g: f64 = 40.0;
    let recharge_tolerance_g: f64 = 1.0;
    let volume_correction_low_g: f64 = 5.0;
    let volume_correction_high_g: f64 = 15.0;
    let evap_volume_delta_low_ml: f64 = 80.0;
    let evap_volume_delta_high_ml: f64 = 110.0;
    let vacuum_target_microns: f64 = 500.0;
    let vacuum_hold_minutes: f64 = 15.0;
    let compressor_running_current_a: f64 = 1.0;
    let compressor_off_time_min: f64 = 3.0;
    let vent_ignition_clearance_m: f64 = 3.0;
    let sf76e_open_temp_c: f64 = 77.0;
    let braze_joint_temp_c: f64 = 700.0;
    let ambient_c: f64 = 20.0;
    let copper_k_w_mk: f64 = 380.0;
    let fin_h_w_m2k: f64 = 35.0;
    let joint_standoff_mm: f64 = 92.0;
    let _tube_od_mm: f64 = 6.35;
    let _tube_wall_mm: f64 = 0.031 * 25.4;
    let _tube_id_mm: f64 = _tube_od_mm - (2.0 * _tube_wall_mm);
    let _area_m2: f64 = ((std::f64::consts::PI / 4.0)
        * ((_tube_od_mm).powf(2.0) - (_tube_id_mm).powf(2.0)))
        / 1000000.0;
    let _perimeter_m: f64 = (std::f64::consts::PI * _tube_od_mm) / 1000.0;
    let fin_decay_mm: f64 =
        ((copper_k_w_mk * _area_m2) / (fin_h_w_m2k * _perimeter_m)).sqrt() * 1000.0;
    let exit_rise_c: f64 =
        (braze_joint_temp_c - ambient_c) * ((-(joint_standoff_mm)) / fin_decay_mm).exp();
    let exit_temp_c: f64 = ambient_c + exit_rise_c;
    let mut variables = Variables::new();
    variables.insert(
        "UNIT_A_CHARGE".into(),
        [fmt(unit_a_factory_charge_g, ".4g")?, " g".to_owned()].concat(),
    );
    variables.insert(
        "UNIT_B_CHARGE".into(),
        [fmt(unit_b_factory_charge_g, ".4g")?, " g".to_owned()].concat(),
    );
    variables.insert(
        "SYSTEM_CHARGE".into(),
        [
            "~".to_owned(),
            fmt(system_charge_approx_g, ".4g")?,
            " g".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RECHARGE_TOL".into(),
        [
            "±".to_owned(),
            fmt(recharge_tolerance_g, ".4g")?,
            " g".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "VOL_CORRECTION".into(),
        [
            "+".to_owned(),
            fmt(volume_correction_low_g, ".4g")?,
            "-".to_owned(),
            fmt(volume_correction_high_g, ".4g")?,
            " g".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "EVAP_VOL_DELTA".into(),
        [
            "~".to_owned(),
            fmt(evap_volume_delta_low_ml, ".4g")?,
            "-".to_owned(),
            fmt(evap_volume_delta_high_ml, ".4g")?,
            " mL".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "VACUUM_TARGET".into(),
        [fmt(vacuum_target_microns, ".4g")?, " microns".to_owned()].concat(),
    );
    variables.insert(
        "VACUUM_HOLD".into(),
        [fmt(vacuum_hold_minutes, ".4g")?, " min".to_owned()].concat(),
    );
    variables.insert(
        "VACUUM_HOLD_FULL".into(),
        [fmt(vacuum_hold_minutes, ".4g")?, " minutes".to_owned()].concat(),
    );
    variables.insert(
        "RUN_CURRENT".into(),
        [
            "~".to_owned(),
            fmt(compressor_running_current_a, ".4g")?,
            " A".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "OFF_TIME".into(),
        [fmt(compressor_off_time_min, ".4g")?, "-minute".to_owned()].concat(),
    );
    variables.insert(
        "VENT_CLEARANCE".into(),
        [fmt(vent_ignition_clearance_m, ".4g")?, " m".to_owned()].concat(),
    );
    variables.insert(
        "SF76E_TEMP".into(),
        [fmt(sf76e_open_temp_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "PROT_INLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_protrusion['inlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PROT_OUTLET".into(),
        [
            fmt(
                n(input, "_coil_mandrel_gen.stub_protrusion['outlet']")?,
                ".4g",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BRAZE_TEMP".into(),
        [
            "~".to_owned(),
            fmt(braze_joint_temp_c, ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "COPPER_K".into(),
        [fmt(copper_k_w_mk, ".4g")?, " W/m·K".to_owned()].concat(),
    );
    variables.insert(
        "FIN_H".into(),
        [fmt(fin_h_w_m2k, ".4g")?, " W/m²K".to_owned()].concat(),
    );
    variables.insert(
        "JOINT_STANDOFF".into(),
        [
            "~".to_owned(),
            fmt(joint_standoff_mm, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FIN_DECAY".into(),
        [fmt(fin_decay_mm, ".1f")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "EXIT_RISE".into(),
        ["~".to_owned(), fmt(exit_rise_c, ".0f")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "EXIT_TEMP".into(),
        ["~".to_owned(), fmt(exit_temp_c, ".0f")?, " °C".to_owned()].concat(),
    );
    let mut output = Output::document("hardware/assembly/refrigerant-loop.md", variables);
    output.exports.insert(
        "unit_a_factory_charge_g".into(),
        json!(unit_a_factory_charge_g as i64),
    );
    output.exports.insert(
        "unit_b_factory_charge_g".into(),
        json!(unit_b_factory_charge_g as i64),
    );
    output.exports.insert(
        "system_charge_approx_g".into(),
        json!(system_charge_approx_g as i64),
    );
    output.exports.insert(
        "recharge_tolerance_g".into(),
        json!(recharge_tolerance_g as i64),
    );
    output.exports.insert(
        "volume_correction_low_g".into(),
        json!(volume_correction_low_g as i64),
    );
    output.exports.insert(
        "volume_correction_high_g".into(),
        json!(volume_correction_high_g as i64),
    );
    output.exports.insert(
        "evap_volume_delta_low_ml".into(),
        json!(evap_volume_delta_low_ml as i64),
    );
    output.exports.insert(
        "evap_volume_delta_high_ml".into(),
        json!(evap_volume_delta_high_ml as i64),
    );
    output.exports.insert(
        "vacuum_target_microns".into(),
        json!(vacuum_target_microns as i64),
    );
    output.exports.insert(
        "vacuum_hold_minutes".into(),
        json!(vacuum_hold_minutes as i64),
    );
    output.exports.insert(
        "compressor_running_current_a".into(),
        json!(compressor_running_current_a as i64),
    );
    output.exports.insert(
        "compressor_off_time_min".into(),
        json!(compressor_off_time_min as i64),
    );
    output.exports.insert(
        "vent_ignition_clearance_m".into(),
        json!(vent_ignition_clearance_m as i64),
    );
    output
        .exports
        .insert("sf76e_open_temp_c".into(), json!(sf76e_open_temp_c as i64));
    output.exports.insert(
        "braze_joint_temp_c".into(),
        json!(braze_joint_temp_c as i64),
    );
    output
        .exports
        .insert("ambient_c".into(), json!(ambient_c as i64));
    output
        .exports
        .insert("copper_k_w_mk".into(), json!(copper_k_w_mk as i64));
    output
        .exports
        .insert("fin_h_w_m2k".into(), json!(fin_h_w_m2k as i64));
    output
        .exports
        .insert("joint_standoff_mm".into(), json!(joint_standoff_mm));
    output
        .exports
        .insert("_tube_od_mm".into(), json!(_tube_od_mm));
    output
        .exports
        .insert("_tube_wall_mm".into(), json!(_tube_wall_mm));
    output
        .exports
        .insert("_tube_id_mm".into(), json!(_tube_id_mm));
    output.exports.insert("_area_m2".into(), json!(_area_m2));
    output
        .exports
        .insert("_perimeter_m".into(), json!(_perimeter_m));
    output
        .exports
        .insert("fin_decay_mm".into(), json!(fin_decay_mm));
    output
        .exports
        .insert("exit_rise_c".into(), json!(exit_rise_c));
    output
        .exports
        .insert("exit_temp_c".into(), json!(exit_temp_c));
    Ok(output)
}
fn water_inlet_jet(request: &Request) -> Result<Output> {
    let input = &request.input;
    let drill_trial_rpm: f64 = 1100.0;
    let mm_per_inch: f64 = 25.4;
    let bore_inches: f64 = n(input, "JET_PASSAGE_D")? / mm_per_inch;
    let mut variables = Variables::new();
    variables.insert(
        "CAP_OD".into(),
        [fmt(n(input, "JET_CAP_D")?, "g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "CAP_THICKNESS".into(),
        [fmt(n(input, "JET_CAP_T")?, "g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "JET_BORE".into(),
        [
            fraction(bore_inches, 128),
            " inch / ".to_owned(),
            fmt(n(input, "JET_PASSAGE_D")?, "g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "JET_LD".into(),
        [fmt(
            n(input, "JET_CAP_T")? / n(input, "JET_PASSAGE_D")?,
            ".2f",
        )?]
        .concat(),
    );
    variables.insert(
        "JET_AREA".into(),
        [
            fmt(
                (std::f64::consts::PI * (n(input, "JET_PASSAGE_D")?).powf(2.0)) / 4.0,
                ".3f",
            )?,
            " mm²".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DRILL_RPM".into(),
        [fmt(drill_trial_rpm, "")?, " rpm".to_owned()].concat(),
    );
    variables.insert(
        "DRILL_SFM".into(),
        [
            fmt(
                ((std::f64::consts::PI * bore_inches) * drill_trial_rpm) / 12.0,
                ".1f",
            )?,
            " surface feet/minute".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/water-inlet-jet.md", variables);
    output
        .exports
        .insert("DRILL_TRIAL_RPM".into(), json!(drill_trial_rpm as i64));
    output
        .exports
        .insert("MM_PER_INCH".into(), json!(mm_per_inch));
    output
        .exports
        .insert("bore_inches".into(), json!(bore_inches));
    Ok(output)
}
fn wiring(request: &Request) -> Result<Output> {
    let input = &request.input;
    let cabinet_slack_mm: f64 = 200.0;
    let winding_r_low_ohm: f64 = 10.0;
    let winding_r_high_ohm: f64 = 30.0;
    let compressor_class_w: f64 = 100.0;
    let mut variables = Variables::new();
    variables.insert(
        "AWG_AC_MAIN".into(),
        [
            fmt(n(input, "_sched_awg_mains")?, ".4g")?,
            " AWG".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "AWG_AC_BRANCH_U".into(),
        [
            fmt(n(input, "_sched_awg_ac_branch")?, ".4g")?,
            " AWG".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "AWG_DC_BRANCH".into(),
        [fmt(n(input, "_sched_awg_sig")?, ".4g")?, " AWG".to_owned()].concat(),
    );
    variables.insert(
        "AWG_SIGNAL".into(),
        [fmt(n(input, "_sched_awg_lv")?, ".4g")?, " AWG".to_owned()].concat(),
    );
    variables.insert(
        "AWG_TRIPLE".into(),
        [
            fmt(n(input, "_sched_awg_mains")?, ".4g")?,
            "/".to_owned(),
            fmt(n(input, "_sched_awg_sig")?, ".4g")?,
            " AWG".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "AC_LINE_V".into(),
        [
            fmt(n(input, "_sched_line_voltage_v")?, ".4g")?,
            " VAC".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "DC_BUS_V".into(),
        [fmt(n(input, "_sched_v_rail_dc")?, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "LOGIC_V".into(),
        [
            fmt(n(input, "_sched_v_rail_logic")?, ".4g")?,
            " V".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "MCU_V".into(),
        [fmt(n(input, "_sched_v_rail_io")?, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "COMP_LEAD_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_compressor_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "JOIN_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_opening_join_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "COMP_FAN_OUT".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_short_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "AC1_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_mid_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "AC2_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_short_2_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "EARTH_CARBONATOR_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_earth_carbonator_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SIG_ONEWIRE_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_onewire_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SIG_REEDS_A_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_reeds_a_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SIG_UMBILICAL_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_umbilical_m")?, ".4g")?,
            " m".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SIG_DISPLAY_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_front_face_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FAN_RUN_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_fan_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "VK_RUN_LEN".into(),
        [
            "~".to_owned(),
            fmt(n(input, "_sched_len_vk_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "JST_PITCH".into(),
        [
            fmt(n(input, "_sched_jst_pitch_mm")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PULLUP_R".into(),
        [
            fmt(n(input, "_sched_ds18b20_pullup_kohm")?, ".4g")?,
            " kΩ".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CABINET_SLACK".into(),
        [fmt(cabinet_slack_mm, ".4g")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "WINDING_R_LOW".into(),
        [fmt(winding_r_low_ohm, ".4g")?].concat(),
    );
    variables.insert(
        "WINDING_R_HIGH".into(),
        [fmt(winding_r_high_ohm, ".4g")?, " Ω".to_owned()].concat(),
    );
    variables.insert(
        "COMP_CLASS_W".into(),
        [fmt(compressor_class_w, ".4g")?, " W".to_owned()].concat(),
    );
    variables.insert(
        "COMP_LEAD_AWG".into(),
        [
            fmt(n(input, "_sched_awg_compressor_lead")?, ".4g")?,
            " AWG".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/wiring.md", variables);
    output
        .exports
        .insert("cabinet_slack_mm".into(), json!(cabinet_slack_mm as i64));
    output
        .exports
        .insert("winding_r_low_ohm".into(), json!(winding_r_low_ohm as i64));
    output.exports.insert(
        "winding_r_high_ohm".into(),
        json!(winding_r_high_ohm as i64),
    );
    output.exports.insert(
        "compressor_class_w".into(),
        json!(compressor_class_w as i64),
    );
    Ok(output)
}

fn route_lengths(specs: &Value) -> Result<BTreeMap<String, f64>> {
    specs
        .as_object()
        .context("reservoir route specifications")?
        .iter()
        .map(|(name, row)| {
            let length = row["segments"]
                .as_array()
                .context("route segments")?
                .iter()
                .map(|segment| -> Result<f64> {
                    if segment["kind"] == "line" {
                        let points = segment["points_mm"].as_array().context("line points")?;
                        ensure!(points.len() == 2, "line segment needs two points");
                        let a = points[0].as_array().context("line start")?;
                        let b = points[1].as_array().context("line end")?;
                        ensure!(a.len() == b.len(), "line endpoint dimensions");
                        Ok(a.iter()
                            .zip(b)
                            .map(|(a, b)| {
                                Ok((a.as_f64().context("point coordinate")?
                                    - b.as_f64().context("point coordinate")?)
                                .powi(2))
                            })
                            .collect::<Result<Vec<f64>>>()?
                            .into_iter()
                            .sum::<f64>()
                            .sqrt())
                    } else {
                        Ok(segment["radius_mm"].as_f64().context("arc radius")?
                            * segment["angle_rad"].as_f64().context("arc angle")?)
                    }
                })
                .collect::<Result<Vec<f64>>>()?
                .into_iter()
                .sum();
            Ok((name.clone(), length))
        })
        .collect()
}
