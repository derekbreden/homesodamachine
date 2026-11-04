use super::*;
pub fn pressure_vessel(request: &Request) -> Result<Output> {
    let input = &request.input;
    let mm_per_in: f64 = 25.4;
    let psi_per_bar: f64 = 14.5038;
    let psi_per_atm: f64 = 14.6959;
    let secondary_regulator_bar: f64 = 3.0;
    let secondary_regulator_pressure_psi: f64 = round(secondary_regulator_bar * psi_per_bar, 1);
    let tube_wall: f64 = 0.065 * mm_per_in;
    let hoop_stress_psi: f64 =
        (secondary_regulator_pressure_psi * n(input, "carbonator_outer_radius")?) / tube_wall;
    let (lo, hi) = (2.0, 4.0);
    let tap_water_c: f64 = 15.0;
    let carbonator_rod_len: f64 = n(input, "rod_spec.finished_length")? * mm_per_in;
    let carbonator_rod_tolerance: f64 = n(input, "rod_spec.length_tolerance")? * mm_per_in;
    if request.operation != "document" && !request.operation.is_empty() {
        let t_c = n(input, "t_c")?;
        let value = match request.operation.as_str() {
            "vapor_atm" => vapor_atm(t_c),
            "bunsen" => bunsen(n(input, "a1")?, n(input, "a2")?, n(input, "a3")?, t_c),
            "headspace_air_atm" => headspace_air_atm(t_c),
            "carbonation_volumes" => carbonation_volumes(
                t_c,
                input["air"].as_bool().unwrap_or(false),
                secondary_regulator_pressure_psi,
            ),
            _ => bail!("unknown pressure operation"),
        };
        return Ok(Output {
            exports: BTreeMap::from([("value".into(), json!(value))]),
            ..Output::default()
        });
    }
    ensure!(
        n(input, "above_carbonator_elbows_height")? == n(input, "below_carbonator_elbows_height")?,
        "split ELBOW_ENV into ABOVE / BELOW variables"
    );
    let mut variables = Variables::new();
    variables.insert(
        "TANK_H".into(),
        [
            fmt(n(input, "carbonator_height")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ELBOW_ENV".into(),
        [
            fmt(n(input, "above_carbonator_elbows_height")?, ".4g")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "ROD_LEN".into(),
        [
            fmt(n(input, "rod_spec.finished_length")?, ".3f")?,
            " ±".to_owned(),
            fmt(n(input, "rod_spec.length_tolerance")?, ".3f")?,
            " in (".to_owned(),
            fmt(carbonator_rod_len, ".2f")?,
            " ±".to_owned(),
            fmt(carbonator_rod_tolerance, ".2f")?,
            " mm)".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "REGISTER_RADIUS_IN".into(),
        [fmt(n(input, "register_radius")?, ".4f")?].concat(),
    );
    variables.insert(
        "REGISTER_RADIUS_MM".into(),
        [
            fmt(n(input, "register_radius")? * mm_per_in, ".3f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "WORKING_PSI".into(),
        [
            fmt(secondary_regulator_pressure_psi, ".4g")?,
            " PSI".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "REG_FIXED".into(),
        [
            "fixed ".to_owned(),
            fmt(secondary_regulator_bar, "g")?,
            "-bar (".to_owned(),
            fmt(secondary_regulator_pressure_psi, ".4g")?,
            " PSI)".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "HOOP_PSI".into(),
        [fmt(round(hoop_stress_psi, -1), ",.0f")?, " PSI".to_owned()].concat(),
    );
    variables.insert(
        "CARB_PURE".into(),
        [
            fmt(
                carbonation_volumes(lo, false, secondary_regulator_pressure_psi),
                ".1f",
            )?,
            " volumes at ".to_owned(),
            fmt(lo, "g")?,
            " °C and ".to_owned(),
            fmt(
                carbonation_volumes(hi, false, secondary_regulator_pressure_psi),
                ".1f",
            )?,
            " at ".to_owned(),
            fmt(hi, "g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "CARB_AIR".into(),
        [
            fmt(
                carbonation_volumes(lo, true, secondary_regulator_pressure_psi),
                ".1f",
            )?,
            " volumes at ".to_owned(),
            fmt(lo, "g")?,
            " °C and ".to_owned(),
            fmt(
                carbonation_volumes(hi, true, secondary_regulator_pressure_psi),
                ".1f",
            )?,
            " at ".to_owned(),
            fmt(hi, "g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "HEADSPACE_AIR".into(),
        [
            fmt(headspace_air_atm(lo) * psi_per_atm, ".0f")?,
            " PSI".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PORT_BORE".into(),
        [
            "⌀".to_owned(),
            fmt(n(input, "hole_diameter")? * mm_per_in, ".4g")?,
            " mm (".to_owned(),
            fmt(n(input, "hole_diameter")?, ".3f")?,
            "\")".to_owned(),
        ]
        .concat(),
    );
    let mut output = Output::document("hardware/assembly/pressure-vessel.md", variables);
    output.exports.insert("MM_PER_IN".into(), json!(mm_per_in));
    output
        .exports
        .insert("PSI_PER_BAR".into(), json!(psi_per_bar));
    output
        .exports
        .insert("PSI_PER_ATM".into(), json!(psi_per_atm));
    output.exports.insert(
        "secondary_regulator_bar".into(),
        json!(secondary_regulator_bar),
    );
    output.exports.insert(
        "secondary_regulator_pressure_psi".into(),
        json!(secondary_regulator_pressure_psi),
    );
    output.exports.insert("tube_wall".into(), json!(tube_wall));
    output
        .exports
        .insert("hoop_stress_psi".into(), json!(hoop_stress_psi));
    output
        .exports
        .insert("tap_water_c".into(), json!(tap_water_c));
    output
        .exports
        .insert("carbonator_rod_len".into(), json!(carbonator_rod_len));
    output.exports.insert(
        "carbonator_rod_tolerance".into(),
        json!(carbonator_rod_tolerance),
    );
    output
        .exports
        .insert("carbonation_basis_c".into(), json!([lo, hi]));
    Ok(output)
}
pub fn firmware_and_commissioning(request: &Request) -> Result<Output> {
    let input = &request.input;
    if request.operation == "constexpr" {
        return Ok(Output {
            exports: BTreeMap::from([(
                "value".into(),
                json!(constexpr(
                    &request.root,
                    input["name"].as_str().context("constexpr name")?
                )?),
            )]),
            data_reads: vec!["firmware/lib/machine_policy/cold_policy.h".into()],
            ..Output::default()
        });
    }
    let gpio_relay1: f64 = 19.0;
    let gpio_onewire: f64 = 26.0;
    let gpio_flow: f64 = 25.0;
    let gpio_relay2: f64 = 2.0;
    let mcp_valves_addr: f64 = 32.0;
    let mcp_reservoirs_addr: f64 = 33.0;
    let rtc_addr: f64 = 104.0;
    let reed_low_loc: String = "0x21 PB4".to_owned();
    let reed_high_loc: String = "0x21 PB5".to_owned();
    let manifold_valves = list(input, "manifold_stations")?
        .iter()
        .filter(|v| v.as_str().is_some_and(|n| n.starts_with("V-")))
        .count() as f64;
    let off_manifold_valves: f64 = 1.0;
    let valve_count: f64 = manifold_valves + off_manifold_valves;
    let reeds_per_reservoir: f64 = 4.0;
    let reeds_carbonator: f64 = 2.0;
    let reeds_total: f64 = (n(input, "reservoir_count")? * reeds_per_reservoir) + reeds_carbonator;
    let rail_12v_nominal: f64 = 12.0;
    let rail_12v_tol: f64 = 0.2;
    let rail_5v_nominal: f64 = 5.0;
    let rail_5v_tol: f64 = 0.1;
    let rail_33v_nominal: f64 = 3.3;
    let rail_33v_tol: f64 = 0.05;
    let onewire_pullup_kohm: f64 = 4.7;
    let ds18b20_count: f64 = 2.0;
    let ambient_tol_c: f64 = 2.0;
    let carbonator_target_c = constexpr(&request.root, "kTankTargetC")?;
    let hysteresis_c = constexpr(&request.root, "kHysteresisC")?;
    let comp_on_temp_c: f64 = carbonator_target_c + hysteresis_c;
    let comp_off_temp_c: f64 = carbonator_target_c;
    let freeze_cutoff_c = constexpr(&request.root, "kFreezeCutoffC")?;
    let freeze_recover_c = constexpr(&request.root, "kFreezeRecoverC")?;
    let min_off_time_min: f64 = constexpr(&request.root, "kMinOffMs")? / 60000.0;
    let min_on_time_s: f64 = constexpr(&request.root, "kMinOnMs")? / 1000.0;
    let reading_stale_s: f64 = constexpr(&request.root, "kReadingStaleMs")? / 1000.0;
    let max_simultaneous_valves: f64 = n(input, "_ac.max_simultaneous_valves")?;
    let board_peak_a: f64 = n(input, "_ac.board_peak_a")?;
    let diaphragm_peak_a: f64 = n(input, "_ac.diaphragm_peak_a")?;
    let psu_max_dc_a: f64 = n(input, "_ac.psu_max_dc_a")?;
    let coincident_peak_a: f64 = n(input, "_ac.coincident_peak_a")?;
    let mut variables = Variables::new();
    variables.insert(
        "GPIO_RELAY1".into(),
        ["GPIO ".to_owned(), fmt(gpio_relay1, "d")?].concat(),
    );
    variables.insert(
        "GPIO_ONEWIRE".into(),
        ["GPIO ".to_owned(), fmt(gpio_onewire, "d")?].concat(),
    );
    variables.insert("REED_LOW".into(), reed_low_loc.clone());
    variables.insert("REED_HIGH".into(), reed_high_loc.clone());
    variables.insert(
        "GPIO_FLOW".into(),
        ["GPIO ".to_owned(), fmt(gpio_flow, "d")?].concat(),
    );
    variables.insert(
        "MCP_VALVES".into(),
        ["0x".to_owned(), fmt(mcp_valves_addr, "02x")?].concat(),
    );
    variables.insert(
        "MCP_RESERVOIRS".into(),
        ["0x".to_owned(), fmt(mcp_reservoirs_addr, "02x")?].concat(),
    );
    variables.insert(
        "RTC_ADDR".into(),
        ["0x".to_owned(), fmt(rtc_addr, "02x")?].concat(),
    );
    variables.insert("VALVE_COUNT".into(), [fmt(valve_count, "d")?].concat());
    variables.insert(
        "RSVR_COUNT".into(),
        [fmt(n(input, "reservoir_count")?, "d")?].concat(),
    );
    variables.insert(
        "REEDS_PER_RSVR".into(),
        [fmt(reeds_per_reservoir, "d")?].concat(),
    );
    variables.insert("REEDS_CARB".into(), [fmt(reeds_carbonator, "d")?].concat());
    variables.insert("REEDS_TOTAL".into(), [fmt(reeds_total, "d")?].concat());
    variables.insert(
        "RAIL_12V".into(),
        [fmt(rail_12v_nominal, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "RAIL_12V_TOL".into(),
        ["± ".to_owned(), fmt(rail_12v_tol, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "RAIL_5V".into(),
        [fmt(rail_5v_nominal, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "RAIL_5V_TOL".into(),
        ["± ".to_owned(), fmt(rail_5v_tol, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "RAIL_33V".into(),
        [fmt(rail_33v_nominal, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "RAIL_33V_TOL".into(),
        ["± ".to_owned(), fmt(rail_33v_tol, ".4g")?, " V".to_owned()].concat(),
    );
    variables.insert(
        "ONEWIRE_PULLUP".into(),
        [fmt(onewire_pullup_kohm, ".4g")?, " kΩ".to_owned()].concat(),
    );
    variables.insert(
        "AMBIENT_TOL".into(),
        ["±".to_owned(), fmt(ambient_tol_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "TANK_TARGET".into(),
        [fmt(carbonator_target_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "HYSTERESIS".into(),
        ["±".to_owned(), fmt(hysteresis_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "COMP_ON_TEMP".into(),
        [fmt(comp_on_temp_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "COMP_OFF_TEMP".into(),
        [fmt(comp_off_temp_c, ".4g")?, " °C".to_owned()].concat(),
    );
    variables.insert(
        "FREEZE_CUTOFF".into(),
        [
            "−".to_owned(),
            fmt((freeze_cutoff_c).abs(), ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "FREEZE_RECOVER".into(),
        [
            "−".to_owned(),
            fmt((freeze_recover_c).abs(), ".4g")?,
            " °C".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "MIN_ON_TIME".into(),
        [fmt(min_on_time_s, ".4g")?, " s".to_owned()].concat(),
    );
    variables.insert(
        "READING_STALE".into(),
        [fmt(reading_stale_s, ".4g")?, " s".to_owned()].concat(),
    );
    variables.insert(
        "MIN_OFF_TIME".into(),
        [fmt(min_off_time_min, ".4g")?, "-minute".to_owned()].concat(),
    );
    variables.insert(
        "MIN_OFF_TIME_HYPHEN".into(),
        [fmt(min_off_time_min, ".4g")?, "-min".to_owned()].concat(),
    );
    variables.insert(
        "MIN_OFF_TIME_BARE".into(),
        [fmt(min_off_time_min, ".4g")?, " min".to_owned()].concat(),
    );
    variables.insert(
        "MAX_VALVES".into(),
        [fmt(max_simultaneous_valves, "d")?].concat(),
    );
    variables.insert(
        "GPIO_RELAY2".into(),
        ["GPIO ".to_owned(), fmt(gpio_relay2, "d")?].concat(),
    );
    variables.insert(
        "BOARD_PEAK_A".into(),
        [fmt(board_peak_a, ".3g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "DIAPHRAGM_A".into(),
        [fmt(diaphragm_peak_a, ".3g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "COINCIDENT_A".into(),
        [fmt(coincident_peak_a, ".3g")?, " A".to_owned()].concat(),
    );
    variables.insert(
        "PSU_MAX_A".into(),
        [fmt(psu_max_dc_a, ".3g")?, " A".to_owned()].concat(),
    );
    let mut output = Output::document("hardware/assembly/firmware-and-commissioning.md", variables);
    output
        .exports
        .insert("gpio_relay1".into(), json!(gpio_relay1 as i64));
    output
        .exports
        .insert("gpio_onewire".into(), json!(gpio_onewire as i64));
    output
        .exports
        .insert("gpio_flow".into(), json!(gpio_flow as i64));
    output
        .exports
        .insert("gpio_relay2".into(), json!(gpio_relay2 as i64));
    output
        .exports
        .insert("mcp_valves_addr".into(), json!(mcp_valves_addr as i64));
    output.exports.insert(
        "mcp_reservoirs_addr".into(),
        json!(mcp_reservoirs_addr as i64),
    );
    output
        .exports
        .insert("rtc_addr".into(), json!(rtc_addr as i64));
    output
        .exports
        .insert("reed_low_loc".into(), json!(reed_low_loc));
    output
        .exports
        .insert("reed_high_loc".into(), json!(reed_high_loc));
    output
        .exports
        .insert("manifold_valves".into(), json!(manifold_valves as i64));
    output.exports.insert(
        "off_manifold_valves".into(),
        json!(off_manifold_valves as i64),
    );
    output
        .exports
        .insert("valve_count".into(), json!(valve_count as i64));
    output.exports.insert(
        "reeds_per_reservoir".into(),
        json!(reeds_per_reservoir as i64),
    );
    output
        .exports
        .insert("reeds_carbonator".into(), json!(reeds_carbonator as i64));
    output
        .exports
        .insert("reeds_total".into(), json!(reeds_total as i64));
    output
        .exports
        .insert("rail_12v_nominal".into(), json!(rail_12v_nominal));
    output
        .exports
        .insert("rail_12v_tol".into(), json!(rail_12v_tol));
    output
        .exports
        .insert("rail_5v_nominal".into(), json!(rail_5v_nominal));
    output
        .exports
        .insert("rail_5v_tol".into(), json!(rail_5v_tol));
    output
        .exports
        .insert("rail_33v_nominal".into(), json!(rail_33v_nominal));
    output
        .exports
        .insert("rail_33v_tol".into(), json!(rail_33v_tol));
    output
        .exports
        .insert("onewire_pullup_kohm".into(), json!(onewire_pullup_kohm));
    output
        .exports
        .insert("ds18b20_count".into(), json!(ds18b20_count as i64));
    output
        .exports
        .insert("ambient_tol_c".into(), json!(ambient_tol_c as i64));
    output
        .exports
        .insert("carbonator_target_c".into(), json!(carbonator_target_c));
    output
        .exports
        .insert("hysteresis_c".into(), json!(hysteresis_c));
    output
        .exports
        .insert("comp_on_temp_c".into(), json!(comp_on_temp_c));
    output
        .exports
        .insert("comp_off_temp_c".into(), json!(comp_off_temp_c));
    output
        .exports
        .insert("freeze_cutoff_c".into(), json!(freeze_cutoff_c));
    output
        .exports
        .insert("freeze_recover_c".into(), json!(freeze_recover_c));
    output
        .exports
        .insert("min_off_time_min".into(), json!(min_off_time_min));
    output
        .exports
        .insert("min_on_time_s".into(), json!(min_on_time_s));
    output
        .exports
        .insert("reading_stale_s".into(), json!(reading_stale_s));
    output.exports.insert(
        "max_simultaneous_valves".into(),
        json!(max_simultaneous_valves as i64),
    );
    output
        .exports
        .insert("board_peak_a".into(), json!(board_peak_a));
    output
        .exports
        .insert("diaphragm_peak_a".into(), json!(diaphragm_peak_a as i64));
    output
        .exports
        .insert("psu_max_dc_a".into(), json!(psu_max_dc_a));
    output
        .exports
        .insert("coincident_peak_a".into(), json!(coincident_peak_a));
    output
        .data_reads
        .push("firmware/lib/machine_policy/cold_policy.h".into());
    Ok(output)
}
pub fn weld_rotation_rig(request: &Request) -> Result<Output> {
    let input = &request.input;
    let mm_per_in: f64 = 25.4;
    let tube_length: f64 = 6.0 * mm_per_in;
    let rod_diameter: f64 = 0.125 * mm_per_in;
    let density_316l: f64 = 0.00798;
    let wire_diameter: f64 = 0.03 * mm_per_in;
    let wire_feed: f64 = 12.0;
    if request.operation == "settings" {
        return Ok(Output {
            exports: BTreeMap::from([("SPEEDS".into(), json!([5, 6, 8, 10, 12, 15]))]),
            ..Output::default()
        });
    }
    if request.operation == "fillet_leg" || request.operation == "cylinder_mass" {
        let value = if request.operation == "fillet_leg" {
            (2.0 * std::f64::consts::PI * wire_diameter.powi(2) / 4.0 * wire_feed
                / n(input, "travel_mm_s")?)
            .sqrt()
        } else {
            std::f64::consts::PI * n(input, "diameter")?.powi(2) / 4.0
                * n(input, "length")?
                * density_316l
        };
        return Ok(Output {
            exports: BTreeMap::from([("value".into(), json!(value))]),
            ..Output::default()
        });
    }
    let canonical_id = n(input, "tube_id")? * mm_per_in;
    ensure!(
        (canonical_id - n(input, "interface.TUBE_ID")?).abs() <= 1e-6,
        "rotator tube ID disagrees with end-cap geometry"
    );
    let cylinder_mass = |diameter: f64, length: f64| {
        std::f64::consts::PI * diameter.powi(2) / 4.0 * length * density_316l
    };
    let tube = std::f64::consts::PI / 4.0
        * (n(input, "interface.TUBE_OD")?.powi(2) - n(input, "interface.TUBE_ID")?.powi(2))
        * tube_length
        * density_316l;
    let plate = cylinder_mass(
        n(input, "disc_diameter")? * mm_per_in,
        n(input, "disc_thickness")? * mm_per_in,
    );
    let rod = cylinder_mass(rod_diameter, n(input, "carbonator_rod_len")?);
    let mass_first = tube + plate;
    let mass_second = tube + 2.0 * plate + rod;
    let wire_area = std::f64::consts::PI * wire_diameter.powi(2) / 4.0;
    let fillet_leg = |travel: f64| (2.0 * wire_area * wire_feed / travel).sqrt();
    let overlap_length: f64 = (n(input, "interface.bead_circumference()")?
        * n(input, "interface.OVERLAP_DEGREES")?)
        / 360.0;
    let mut variables = Variables::new();
    variables.insert(
        "BEAD_D".into(),
        [
            fmt(n(input, "interface.TUBE_ID")?, ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BEAD_C".into(),
        [
            fmt(n(input, "interface.bead_circumference()")?, ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RECESS".into(),
        [
            fmt(n(input, "interface.ENDCAP_RECESS")?, ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SERVICE_BORE".into(),
        [
            fmt(n(input, "interface.SERVICE_BORE_DIAMETER")?, ".0f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BASE_CLEARANCE".into(),
        [
            fmt(n(input, "interface.BASE_CLEARANCE")?, ".0f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "MASS_FIRST".into(),
        [fmt(mass_first / 1000.0, ".2f")?, " kg".to_owned()].concat(),
    );
    variables.insert(
        "MASS_SECOND".into(),
        [fmt(mass_second / 1000.0, ".2f")?, " kg".to_owned()].concat(),
    );
    variables.insert(
        "SPEED_MIN".into(),
        [
            fmt(n(input, "interface.TRAVEL_MIN")?, ".0f")?,
            " mm/s".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SPEED_NOM".into(),
        [
            fmt(n(input, "interface.TRAVEL_NOMINAL")?, ".0f")?,
            " mm/s".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SPEED_MAX".into(),
        [
            fmt(n(input, "interface.TRAVEL_MAX")?, ".0f")?,
            " mm/s".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RPM_WINDOW".into(),
        [
            fmt(
                n(input, "interface.table_rpm(interface.TRAVEL_MIN)")?,
                ".3f",
            )?,
            "–".to_owned(),
            fmt(
                n(input, "interface.table_rpm(interface.TRAVEL_MAX)")?,
                ".3f",
            )?,
            " rpm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RPM_NOM".into(),
        [
            fmt(
                n(input, "interface.table_rpm(interface.TRAVEL_NOMINAL)")?,
                ".3f",
            )?,
            " rpm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "MOTOR_RPM_NOM".into(),
        [
            fmt(
                n(input, "interface.motor_rpm(interface.TRAVEL_NOMINAL)")?,
                ".3f",
            )?,
            " rpm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "PULSE_HZ_NOM".into(),
        [
            fmt(
                n(input, "interface.pulse_hz(interface.TRAVEL_NOMINAL)")?,
                ".1f",
            )?,
            " Hz".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "RATIO".into(),
        [
            fmt(n(input, "interface.drive_ratio()")?, ".1f")?,
            ":1".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "BELT_CENTER".into(),
        [
            fmt(n(input, "interface.belt_center_distance()")?, ".1f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SMALL_WRAP".into(),
        [
            fmt(n(input, "interface.small_pulley_wrap_degrees()")?, ".1f")?,
            "°".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "SMALL_WRAP_TEETH".into(),
        [fmt(
            (n(input, "interface.small_pulley_wrap_degrees()")? / 360.0)
                * n(input, "interface.MOTOR_PULLEY_TEETH")?,
            ".1f",
        )?]
        .concat(),
    );
    variables.insert(
        "TABLE_PULSES".into(),
        [fmt(n(input, "interface.table_pulses_per_rev()")?, ",")?].concat(),
    );
    variables.insert(
        "INDEX_PULSES".into(),
        [fmt(n(input, "interface.pulses_for_degrees(45.0)")?, ",")?].concat(),
    );
    variables.insert(
        "TABLE_STEP_DEG".into(),
        [
            fmt(360.0 / n(input, "interface.table_pulses_per_rev()")?, ".3f")?,
            "°".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "TABLE_STEP_MM".into(),
        [
            fmt(
                n(input, "interface.bead_circumference()")?
                    / n(input, "interface.table_pulses_per_rev()")?,
                ".3f",
            )?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "OVERLAP_DEG".into(),
        [
            fmt(n(input, "interface.OVERLAP_DEGREES")?, ".0f")?,
            "°".to_owned(),
        ]
        .concat(),
    );
    variables.insert(
        "OVERLAP_MM".into(),
        [fmt(overlap_length, ".1f")?, " mm".to_owned()].concat(),
    );
    variables.insert(
        "WIRE_FEED".into(),
        [fmt(wire_feed, ".0f")?, " mm/s".to_owned()].concat(),
    );
    variables.insert(
        "WIRE_AREA".into(),
        [fmt(wire_area, ".3f")?, " mm²".to_owned()].concat(),
    );
    variables.insert(
        "FILLET_NOM".into(),
        [
            fmt(fillet_leg(n(input, "interface.TRAVEL_NOMINAL")?), ".2f")?,
            " mm".to_owned(),
        ]
        .concat(),
    );
    for speed in [5, 6, 8, 10, 12, 15] {
        variables.insert(
            format!("RPM_{speed}"),
            fmt(
                input["table_rpm_per_speed"][speed.to_string()]
                    .as_f64()
                    .context("table speed")?,
                ".3f",
            )?,
        );
        variables.insert(
            format!("REV_{speed}"),
            fmt(
                n(input, "interface.bead_circumference()")? / speed as f64,
                ".1f",
            )?,
        );
        variables.insert(
            format!("PULSE_{speed}"),
            fmt(
                input["pulse_hz_per_speed"][speed.to_string()]
                    .as_f64()
                    .context("pulse speed")?,
                ".1f",
            )?,
        );
        variables.insert(
            format!("LEG_{speed}"),
            fmt(fillet_leg(speed as f64), ".2f")?,
        );
    }
    let mut output = Output::document("hardware/assembly/weld-rotation-rig.md", variables);
    output.exports.insert("MM_PER_IN".into(), json!(mm_per_in));
    output
        .exports
        .insert("TUBE_LENGTH".into(), json!(tube_length));
    output
        .exports
        .insert("ROD_DIAMETER".into(), json!(rod_diameter));
    output
        .exports
        .insert("DENSITY_316L".into(), json!(density_316l));
    output
        .exports
        .insert("WIRE_DIAMETER".into(), json!(wire_diameter));
    output.exports.insert("WIRE_FEED".into(), json!(wire_feed));
    output
        .exports
        .insert("overlap_length".into(), json!(overlap_length));
    output
        .exports
        .insert("rotating_masses".into(), json!([mass_first, mass_second]));
    output
        .exports
        .insert("SPEEDS".into(), json!([5, 6, 8, 10, 12, 15]));
    output.stdout = format!(
        "bead {} mm; nominal {} rpm, {} Hz, {} s/rev\n",
        fmt(n(input, "interface.bead_circumference()")?, ".2f")?,
        fmt(
            n(input, "interface.table_rpm(interface.TRAVEL_NOMINAL)")?,
            ".3f"
        )?,
        fmt(
            n(input, "interface.pulse_hz(interface.TRAVEL_NOMINAL)")?,
            ".1f"
        )?,
        fmt(
            n(input, "interface.bead_circumference()")? / n(input, "interface.TRAVEL_NOMINAL")?,
            ".1f"
        )?
    );
    Ok(output)
}
pub fn cable_assemblies(request: &Request) -> Result<Output> {
    let _input = &request.input;
    let board = "hardware/pcb/pcba/pcba.tsx";
    let board_text = std::fs::read_to_string(request.root.join(board))?;
    let pins = connector_pins(&board_text)?;
    let wanted = (1..12)
        .chain(std::iter::once(13))
        .map(|n| format!("J{n}"))
        .collect::<Vec<_>>();
    let missing = wanted
        .iter()
        .filter(|name| !pins.contains_key(*name))
        .collect::<Vec<_>>();
    ensure!(
        missing.is_empty(),
        "pcba.tsx: no connector declaration found for {missing:?}"
    );
    let schedule = super::ac_wiring_schedule(request)?.exports;
    let sn = |name: &str| {
        schedule
            .get(name)
            .and_then(Value::as_f64)
            .with_context(|| format!("schedule number {name}"))
    };
    let mut variables = Variables::new();
    for name in &wanted {
        variables.insert(format!("{name}_PINS"), pins[name].to_string());
    }
    variables.insert(
        "LOOM_J1".into(),
        fmt((sn("len_man_a_mm")?).max(sn("len_man_a_com_mm")?), "g")? + " mm",
    );
    variables.insert(
        "LOOM_J2".into(),
        fmt(
            (sn("len_man_b_mm")?)
                .max(sn("len_man_b_com_mm")?)
                .max(sn("len_fan_mm")?)
                .max(sn("len_vk_mm")?),
            "g",
        )? + " mm",
    );
    variables.insert(
        "LOOM_J3".into(),
        fmt(sn("len_faucet_inboard_mm")?, "g")? + " mm",
    );
    variables.insert(
        "LOOM_J4".into(),
        fmt(
            (sn("len_onewire_mm")?)
                .max(sn("len_flow_mm")?)
                .max(sn("len_sensors_gnd_mm")?),
            "g",
        )? + " mm",
    );
    variables.insert("LOOM_J5".into(), fmt(sn("len_relays_mm")?, "g")? + " mm");
    variables.insert("LOOM_J6".into(), fmt(sn("len_reeds_a_mm")?, "g")? + " mm");
    variables.insert(
        "LOOM_J7".into(),
        fmt(
            (sn("len_reeds_b_mm")?)
                .max(sn("len_carb_reeds_mm")?)
                .max(sn("len_reeds_gnd_mm")?),
            "g",
        )? + " mm",
    );
    variables.insert(
        "LOOM_J9".into(),
        fmt(sn("len_front_face_mm")?, "g")? + " mm",
    );
    variables.insert("LOOM_J11".into(), fmt(sn("len_gas_mm")?, "g")? + " mm");
    variables.insert(
        "LOOM_J13".into(),
        fmt(sn("len_pump_fixed_mm")?, "g")? + " mm",
    );
    variables.insert(
        "EXTERNAL_SIG6".into(),
        fmt(sn("len_umbilical_m")?, "g")? + " m",
    );
    let mut output = Output::document("hardware/assembly/cable-assemblies.md", variables);
    output.exports.insert("connector_pins".into(), json!(pins));
    output.data_reads.push(board.into());
    output.stdout = wanted
        .iter()
        .map(|j| format!("{j}={}", pins[j]))
        .collect::<Vec<_>>()
        .join(" ")
        + "\n";
    Ok(output)
}

// Fresh-water Bunsen coefficients: Weiss (1970); CO2 solubility: Weiss (1974).
// Incoming water is saturated with air at 15 C; the sealed headspace settles
// where the outgoing water carries the incoming dissolved air.
fn vapor_atm(t_c: f64) -> f64 {
    0.61121 * ((18.678 - t_c / 234.5) * (t_c / (257.14 + t_c))).exp() / 101.325
}
fn bunsen(a1: f64, a2: f64, a3: f64, t_c: f64) -> f64 {
    let t = t_c + 273.15;
    (a1 + a2 * (100.0 / t) + a3 * (t / 100.0).ln()).exp()
}
fn headspace_air_atm(t_c: f64) -> f64 {
    let dry = 1.0 - vapor_atm(15.0);
    [
        (0.78084, -59.6274, 85.7661, 24.3696),
        (0.20946, -58.3877, 85.8079, 23.8439),
        (0.00934, -55.6578, 82.0262, 22.5929),
    ]
    .into_iter()
    .map(|(x, a1, a2, a3)| x * dry * bunsen(a1, a2, a3, 15.0) / bunsen(a1, a2, a3, t_c))
    .sum()
}
fn carbonation_volumes(t_c: f64, air: bool, secondary_psi: f64) -> f64 {
    let t = t_c + 273.15;
    let p_total = secondary_psi / 14.6959 + 1.0;
    let p_co2 = p_total - vapor_atm(t_c) - if air { headspace_air_atm(t_c) } else { 0.0 };
    let k0 = (-58.0931 + 90.5069 * (100.0 / t) + 22.2940 * (t / 100.0).ln()).exp();
    let b = -1636.75 + 12.0408 * t - 3.27957e-2 * t.powi(2) + 3.16528e-5 * t.powi(3);
    let fugacity = p_co2 * (b * p_total / (82.0578 * t)).exp();
    k0 * fugacity * 22.26
}
fn constexpr(root: &Path, name: &str) -> Result<f64> {
    let path = root.join("firmware/lib/machine_policy/cold_policy.h");
    let pattern = regex::Regex::new(&format!(
        r"constexpr\s+\w+\s+{}\s*=\s*(-?[\d.]+)f?\s*;",
        regex::escape(name)
    ))?;
    let text = std::fs::read_to_string(&path)?;
    let value = pattern
        .captures(&text)
        .with_context(|| format!("cold_policy.h: no constexpr {name}"))?;
    Ok(value[1].parse()?)
}
fn connector_pins(board: &str) -> Result<BTreeMap<String, u64>> {
    let jst = regex::Regex::new(r#"<Jst\s+name="(J\d+)"[^>]*?count=\{(\d+)\}"#)?;
    let kf301 = regex::Regex::new(r#"<KF301_5_0_2P\s+name="(J\d+)""#)?;
    let mut pins = BTreeMap::new();
    for capture in jst.captures_iter(board) {
        pins.insert(capture[1].to_owned(), capture[2].parse()?);
    }
    for capture in kf301.captures_iter(board) {
        pins.insert(capture[1].to_owned(), 2);
    }
    Ok(pins)
}
