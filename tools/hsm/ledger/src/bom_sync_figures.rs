// Document marker values derived from the same hardware count records.
fn figures(input: &Value, n: &Value, casting: &Value) -> Result<(Variables, Variables)> {
    let mut bom = labor::casting_figures(casting)?;
    bom.insert(
        "FUNNEL_KIT_YIELD".into(),
        fmt(1098.0 / num(&casting["mixed_g"])?, ".2f"),
    );
    bom.insert(
        "FUNNEL_BATCH_COST".into(),
        format!(
            "${}",
            fmt((35.16 * num(&casting["mixed_g"])?) / 1098.0, ".2f")
        ),
    );
    bom.insert(
        "END_CAPS".into(),
        fmt(num(&n["end_cap_plates_per_carbonator"])?, ".4g"),
    );
    bom.insert(
        "CARBONATOR_PORTS".into(),
        fmt(num(&n["carbonator_ports"])?, ".4g"),
    );
    bom.insert(
        "RESERVOIRS".into(),
        fmt(num(&n["reservoirs_per_build"])?, ".4g"),
    );
    bom.insert(
        "RESERVOIR_CAP_COUNT".into(),
        fmt(num(&n["reservoirs_per_build"])?, ".4g"),
    );
    bom.insert(
        "AERO_FLOATS".into(),
        fmt(num(&n["floats_per_build"])?, ".4g"),
    );
    bom.insert("RC62_TOTAL".into(), fmt(num(&n["rc62_per_build"])?, ".4g"));
    bom.insert(
        "RC62_COST".into(),
        pack_cost(num(&n["rc62_per_build"])?, "88.28", "30")?,
    );
    bom.insert(
        "REEDS_PER_RES".into(),
        fmt(num(&n["reeds_per_reservoir"])?, ".4g"),
    );
    bom.insert(
        "CARB_REEDS".into(),
        fmt(num(&n["reeds_per_carbonator"])?, ".4g"),
    );
    bom.insert(
        "RES_REEDS_TOTAL".into(),
        fmt(num(&n["reservoir_reeds_total"])?, ".4g"),
    );
    bom.insert(
        "REEDS_TOTAL".into(),
        fmt(num(&n["total_reeds_per_build"])?, ".4g"),
    );
    bom.insert("SOLENOIDS".into(), fmt(num(&n["solenoid_count"])?, ".4g"));
    bom.insert("TEES".into(), fmt(num(&n["tee_count"])?, ".4g"));
    bom.insert(
        "TEES_COST".into(),
        pack_cost(num(&n["tee_count"])?, "42.68", "20")?,
    );
    bom.insert(
        "FOUR_INCH_TIES".into(),
        fmt(num(&n["four_inch_ties_per_build"])?, ".4g"),
    );
    bom.insert(
        "FOUR_INCH_TIES_COST".into(),
        pack_cost(num(&n["four_inch_ties_per_build"])?, "4.28", "200")?,
    );
    bom.insert(
        "RESERVOIR_A_TIES".into(),
        fmt(num(&n["reservoir_a_ties_per_build"])?, ""),
    );
    bom.insert(
        "RESERVOIR_A_SNAP_CAPS".into(),
        fmt(num(&n["reservoir_a_snap_caps_per_build"])?, ""),
    );
    bom.insert(
        "SIX_INCH_TIES".into(),
        fmt(num(&n["six_inch_ties_per_build"])?, ".4g"),
    );
    bom.insert(
        "SIX_INCH_TIES_COST".into(),
        pack_cost(num(&n["six_inch_ties_per_build"])?, "6.42", "100")?,
    );
    bom.insert(
        "SOLID16_CUT_LENGTH".into(),
        format!("{} m", n["solid16_cut_m"].as_str().unwrap()),
    );
    bom.insert(
        "SOLID16_ALLOCATION".into(),
        format!("{} m", n["solid16_allocation_m"].as_str().unwrap()),
    );
    bom.insert(
        "SOLID16_COST".into(),
        pack_cost(num(&n["solid16_allocation_m"])?, "12.86", "7.62")?,
    );
    bom.insert(
        "PP1208E_PANEL".into(),
        fmt(num(&n["panel_umbilical_bulkheads"])?, ".4g"),
    );
    bom.insert(
        "PP1208E_INLET".into(),
        fmt(num(&n["panel_water_inlet_bulkheads"])?, ".4g"),
    );
    bom.insert(
        "PP1208E_TOTAL".into(),
        fmt(num(&n["pp1208e_per_build"])?, ".4g"),
    );
    bom.insert(
        "FOAM_INSERTS".into(),
        fmt(num(&n["foam_cap_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "FOAM_CLAMP_INSERTS".into(),
        fmt(num(&n["foam_cap_clamp_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "FOAM_SCREWS".into(),
        fmt(num(&n["foam_cap_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "FOAM_FACE_SCREWS".into(),
        fmt(num(&n["inserts_per_foam_cap_face"])?, ".4g"),
    );
    bom.insert(
        "RES_INSERTS_PER_CAP".into(),
        fmt(num(&n["inserts_per_reservoir_cap"])?, ".4g"),
    );
    bom.insert(
        "RES_INSERTS".into(),
        fmt(num(&n["reservoir_cap_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "RES_SCREWS".into(),
        fmt(num(&n["reservoir_cap_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "TOUCHFLO_INSERTS".into(),
        fmt(num(&n["touchflo_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "TOUCHFLO_SCREWS".into(),
        fmt(num(&n["touchflo_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "FAUCET_DISPLAY_INSERTS".into(),
        fmt(num(&n["faucet_display_cover_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "FAUCET_DISPLAY_SCREWS".into(),
        fmt(num(&n["faucet_display_cover_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "SHELF_INSERTS".into(),
        fmt(num(&n["shelf_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "SHELF_SCREWS".into(),
        fmt(num(&n["shelf_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "SHELF_SCREWS_PSU".into(),
        fmt(num(&n["shelf_psu_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "SHELF_SCREWS_PCBA".into(),
        fmt(num(&n["shelf_pcba_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "SHELF_SCREWS_RELAY".into(),
        fmt(num(&n["shelf_relay_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "COND_INSERTS".into(),
        fmt(num(&n["cond_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "COND_SCREWS".into(),
        fmt(num(&n["cond_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "SHORT_INSERT_LEN".into(),
        fmt(num(&input["heatset_len"])?, "g"),
    );
    bom.insert("PSU_EAR_T".into(), fmt(num(&input["psu_ledge_h"])?, "g"));
    bom.insert("PSU_BORE".into(), fmt(num(&n["psu_bore"])?, ".3g"));
    bom.insert(
        "PSU_SCREW_REACH".into(),
        fmt(num(&n["psu_screw_reach"])?, ".3g"),
    );
    bom.insert(
        "PSU_SCREW_REACH_MAX".into(),
        fmt(num(&n["psu_screw_reach_max"])?, ".3g"),
    );
    bom.insert(
        "PSU_SCREW_TIP".into(),
        fmt(
            num(&n["psu_bore"])? - num(&n["psu_screw_reach_max"])?,
            ".3g",
        ),
    );
    bom.insert(
        "PCBA_BOARD_T".into(),
        fmt(num(&input["pcba_thickness"])?, "g"),
    );
    bom.insert(
        "PCBA_INSERT_RECESS".into(),
        fmt(num(&n["pcba_insert_recess"])?, ".3g"),
    );
    bom.insert("PCBA_BORE".into(), fmt(num(&n["pcba_bore"])?, ".3g"));
    bom.insert(
        "PCBA_SCREW_REACH".into(),
        fmt(num(&n["pcba_screw_reach"])?, ".3g"),
    );
    bom.insert(
        "PCBA_SCREW_TIP".into(),
        fmt(num(&n["pcba_bore"])? - num(&n["pcba_screw_reach"])?, ".3g"),
    );
    bom.insert(
        "RELAY_BOARD_T".into(),
        fmt(num(&input["relay_pcb_t"])?, "g"),
    );
    bom.insert(
        "RELAY_INSERT_LEN".into(),
        fmt(num(&input["relay_fasteners"]["insert_length_mm"])?, "g"),
    );
    bom.insert(
        "RELAY_INSERT_SETBACK".into(),
        fmt(
            num(&input["relay_fasteners"]["insert_face_setback_mm"])?,
            "g",
        ),
    );
    bom.insert(
        "RELAY_BACKING".into(),
        fmt(
            num(&input["relay_fasteners"]["minimum_blind_backing_mm"])?,
            ".3g",
        ),
    );
    bom.insert(
        "RELAY_FLUTED_BACKING".into(),
        fmt(
            num(&input["relay_fasteners"]["minimum_fluted_backing_mm"])?,
            ".3g",
        ),
    );
    bom.insert("RELAY_BORE".into(), fmt(num(&n["relay_bore"])?, ".3g"));
    bom.insert(
        "RELAY_SCREW_REACH".into(),
        fmt(num(&n["relay_screw_reach"])?, ".3g"),
    );
    bom.insert(
        "RELAY_SCREW_TIP".into(),
        fmt(
            num(&n["relay_bore"])? - num(&n["relay_screw_reach"])?,
            ".3g",
        ),
    );
    bom.insert(
        "C14_FLANGE_T".into(),
        fmt(num(&input["c14_flange_t"])?, "g"),
    );
    bom.insert(
        "C14_RIM_PROUD".into(),
        fmt(num(&input["c14_rim_proud"])?, "g"),
    );
    bom.insert("C14_BORE".into(), fmt(num(&n["c14_bore"])?, "g"));
    bom.insert(
        "C14_SCREW_REACH".into(),
        fmt(num(&n["c14_screw_reach"])?, ".3g"),
    );
    bom.insert(
        "C14_SCREW_TIP".into(),
        fmt(num(&n["c14_bore"])? - num(&n["c14_screw_reach"])?, ".3g"),
    );
    bom.insert(
        "C14_WASHERS".into(),
        fmt(num(&n["c14_washers_per_build"])?, "g"),
    );
    bom.insert(
        "C14_WASHER_T".into(),
        fmt(num(&n["c14_washer_thickness"])?, "g"),
    );
    bom.insert(
        "C14_WASHERS_COST".into(),
        pack_cost(num(&n["c14_washers_per_build"])?, "7.82", "200")?,
    );
    bom.insert(
        "SMALL_WASHERS".into(),
        fmt(num(&n["small_washers_per_build"])?, "g"),
    );
    bom.insert(
        "SMALL_WASHERS_COST".into(),
        pack_cost(num(&n["small_washers_per_build"])?, "7.82", "200")?,
    );
    bom.insert("M3X8_TOTAL".into(), fmt(num(&n["m3x8_per_build"])?, ".4g"));
    bom.insert(
        "M3X8_COST".into(),
        pack_cost(num(&n["m3x8_per_build"])?, "7.71", "120")?,
    );
    bom.insert(
        "NAMEPLATE_INSERTS".into(),
        fmt(num(&n["nameplate_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "NAMEPLATE_SCREWS".into(),
        fmt(num(&n["nameplate_screws_per_build"])?, ".4g"),
    );
    bom.insert("NAMEPLATE_MOUNT".into(),format!("retained in `enclosure-back-top` by {} coplanar horizontal wings. The plate takes {} screws and {} inserts.",fmt(num(&n["nameplate_wings_per_build"])?,""),fmt(num(&n["nameplate_screws_per_build"])?,""),fmt(num(&n["nameplate_inserts_per_build"])?,"")));
    bom.insert(
        "DISPLAY_COVER_INSERTS".into(),
        fmt(num(&n["display_cover_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "DISPLAY_COVER_SCREWS".into(),
        fmt(num(&n["display_cover_screws_per_build"])?, ".4g"),
    );
    bom.insert("DISPLAY_COVER_MOUNT".into(),format!("retained flush with `enclosure-front-top`'s {}° display plane by {} coplanar horizontal wings. The TPU ring bears between the cover's lap and the glass. The cover takes {} screws and {} inserts.",fmt(num(&input["display_angle"])?,"g"),fmt(num(&n["display_cover_wings_per_build"])?,""),fmt(num(&n["display_cover_screws_per_build"])?,""),fmt(num(&n["display_cover_inserts_per_build"])?,"")));
    bom.insert(
        "M3X10_TOTAL".into(),
        fmt(num(&n["m3x10_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3X10_COST".into(),
        pack_cost(num(&n["m3x10_per_build"])?, "8.57", "120")?,
    );
    bom.insert(
        "B_FILL_CLAMP_SCREWS".into(),
        fmt(num(&n["b_fill_clamp_fasteners_per_build"])?, ".4g"),
    );
    bom.insert(
        "B_FILL_CLAMP_INSERTS".into(),
        fmt(num(&n["b_fill_clamp_fasteners_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3X20_TOTAL".into(),
        fmt(num(&n["m3x20_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3X20_COST".into(),
        pack_cost(num(&n["m3x20_per_build"])?, "8.14", "60")?,
    );
    bom.insert(
        "FUNNEL_FRAME_SCREWS".into(),
        fmt(num(&n["funnel_frame_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "ROOF_CLOSURE_INSERTS".into(),
        fmt(num(&n["roof_closure_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "ROOF_CLOSURE_SCREWS".into(),
        fmt(num(&n["roof_closure_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3X60_TOTAL".into(),
        fmt(num(&n["m3x60_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3X60_COST".into(),
        pack_cost(num(&n["m3x60_per_build"])?, "10.18", "60")?,
    );
    bom.insert(
        "M3X12_TOTAL".into(),
        fmt(num(&n["m3x12_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3X12_COST".into(),
        pack_cost(num(&n["m3x12_per_build"])?, "8.57", "120")?,
    );
    bom.insert(
        "SEAM_RODS".into(),
        fmt(num(&n["enclosure_seam_rods_per_build"])?, ".4g"),
    );
    bom.insert(
        "M5X100_TOTAL".into(),
        fmt(
            num(&n["enclosure_seam_rods_per_build"])? + num(&n["foam_cap_screws_per_build"])?,
            ".4g",
        ),
    );
    bom.insert(
        "M5X100_COST".into(),
        pack_cost(
            num(&n["enclosure_seam_rods_per_build"])? + num(&n["foam_cap_screws_per_build"])?,
            "7.70",
            "20",
        )?,
    );
    bom.insert("SEAM_SCREW_UNIT_COST".into(), pack_cost(1.0, "7.70", "20")?);
    bom.insert(
        "SEAM_SCREWS_COST".into(),
        pack_cost(num(&n["enclosure_seam_rods_per_build"])?, "7.70", "20")?,
    );
    bom.insert(
        "SEAM_INSERTS".into(),
        fmt(num(&n["enclosure_seam_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "DOCK_PUMP_TUBES".into(),
        fmt(length(&input["collet_holes"]), ""),
    );
    bom.insert(
        "PUMP_TUBE_CUT".into(),
        format!(
            "{} mm",
            fmt(num(&input["manifold"]["pump_tube_cut"])?, ".3g")
        ),
    );
    bom.insert(
        "DOCK_TEES".into(),
        fmt(length(&input["manifold"]["pump_junctions"]), ""),
    );
    bom.insert(
        "DOCK_RETURNS".into(),
        fmt(length(&input["manifold"]["lower_connections"]), ""),
    );
    bom.insert(
        "DOCK_ELBOWS".into(),
        fmt(2.0 * length(&input["manifold"]["lower_connections"]), ""),
    );
    bom.insert(
        "DOCK_ELBOWS_COST".into(),
        stem_cost(2. * length(&input["manifold"]["lower_connections"]))?,
    );
    bom.insert(
        "STEM_ELBOWS".into(),
        fmt(num(&n["stem_elbows_per_build"])?, ".4g"),
    );
    bom.insert(
        "STEM_ELBOWS_COST".into(),
        stem_cost(num(&n["stem_elbows_per_build"])?)?,
    );
    bom.insert(
        "PP0308E_TOTAL".into(),
        fmt(num(&n["pp0308e_per_build"])?, ""),
    );
    bom.insert(
        "PP0308E_COST".into(),
        pack_cost(num(&n["pp0308e_per_build"])?, "68.49", "30")?,
    );
    bom.insert(
        "DOCK_TEES".into(),
        fmt(num(&n["dock_tees_per_build"])?, ".4g"),
    );
    bom.insert(
        "DOCK_FIXTURE_LOCKS".into(),
        fmt(num(&n["dock_fixture_locks_per_build"])?, ".4g"),
    );
    bom.insert(
        "PUMP_RETAINER_INSERTS".into(),
        fmt(num(&n["pump_retainer_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "PUMP_RETAINER_SCREWS".into(),
        fmt(num(&n["pump_retainer_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "FLOOR_INSERTS".into(),
        fmt(num(&n["floor_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "FLOOR_SCREWS".into(),
        fmt(num(&n["floor_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "FLOOR_WASHERS".into(),
        fmt(num(&n["floor_washers_per_build"])?, ".4g"),
    );
    bom.insert(
        "COMPRESSOR_LIGAMENT".into(),
        fmt(num(&input["compressor_mount_ligament"])?, ".4g"),
    );
    bom.insert(
        "COMPRESSOR_BORE".into(),
        fmt(num(&input["compressor_mount_d"])?, ".4g"),
    );
    bom.insert(
        "WASHER_MAX_OD".into(),
        fmt(
            num(&input["compressor_mount_d"])? + (2.0 * num(&input["compressor_mount_ligament"])?),
            ".4g",
        ),
    );
    bom.insert(
        "GROMMET_SQUEEZE".into(),
        fmt(num(&input["floor_grommet_squeeze"])?, ".4g"),
    );
    bom.insert(
        "DECK_INSERTS".into(),
        fmt(num(&n["foam_cap_deck_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "PUMP_MOUNT_SCREWS".into(),
        fmt(num(&n["pump_mount_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "FLAT_WASHERS_9".into(),
        fmt(num(&n["flat_washers_9_per_build"])?, ".4g"),
    );
    bom.insert(
        "FLAT_WASHERS_9_COST".into(),
        pack_cost(num(&n["flat_washers_9_per_build"])?, "9.00", "200")?,
    );
    bom.insert(
        "RES_SCREWS_COST".into(),
        pack_cost(num(&n["reservoir_cap_screws_per_build"])?, "8.66", "120")?,
    );
    bom.insert(
        "CAP_CRADLES".into(),
        fmt(length(&input["cap_cradles"]), ".4g"),
    );
    bom.insert(
        "TOTAL_M3_INSERTS".into(),
        fmt(num(&n["total_m3_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3_LONG_INSERTS".into(),
        fmt(num(&n["m3_long_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3_LONG_INSERTS_COST".into(),
        pack_cost(num(&n["m3_long_inserts_per_build"])?, "10.71", "100")?,
    );
    bom.insert(
        "M3_SHORT_INSERTS".into(),
        fmt(num(&n["m3_short_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "M3_SHORT_INSERTS_COST".into(),
        pack_cost(num(&n["m3_short_inserts_per_build"])?, "10.71", "100")?,
    );
    bom.insert(
        "C14_INSERTS".into(),
        fmt(num(&n["c14_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "C14_SCREWS".into(),
        fmt(num(&n["c14_screws_per_build"])?, ".4g"),
    );
    bom.insert(
        "TOTAL_M5_INSERTS".into(),
        fmt(num(&n["total_m5_inserts_per_build"])?, ".4g"),
    );
    bom.insert(
        "M5_INSERTS_COST".into(),
        pack_cost(num(&n["total_m5_inserts_per_build"])?, "10.71", "50")?,
    );
    bom.insert(
        "PITCH".into(),
        format!("{} mm", fmt(num(&input["coil"]["pitch"])?, ".4g")),
    );
    bom.insert(
        "NET_UNDERSIZE".into(),
        format!(
            "{} mm",
            fmt(num(&input["mandrel"]["net_undersize"])?, ".4g")
        ),
    );
    bom.insert(
        "LAID_FT".into(),
        format!("{} ft", fmt(num(&n["_wrap_mm"])? / 304.8, ".4g")),
    );
    bom.insert(
        "MANDREL_FT".into(),
        format!(
            "{} ft",
            fmt(
                num(&input["mandrel"]["mandrel_wrap_length"])? / 304.8,
                ".4g"
            )
        ),
    );
    bom.insert(
        "STUB_INLET".into(),
        format!(
            "{} mm",
            fmt(num(&input["mandrel"]["stub_allowance"]["inlet"])?, ".4g")
        ),
    );
    bom.insert(
        "STUB_OUTLET".into(),
        format!(
            "{} mm",
            fmt(num(&input["mandrel"]["stub_allowance"]["outlet"])?, ".4g")
        ),
    );
    bom.insert(
        "ROLL_SHARE".into(),
        format!(
            "1/{}",
            fmt(num(&input["mandrel"]["carbonators_per_roll"])?, "")
        ),
    );
    bom.insert(
        "CUT_FT".into(),
        format!("{} ft", fmt(num(&n["_cut_mm"])? / 304.8, ".4g")),
    );
    bom.insert(
        "ROLL_SPARE".into(),
        format!("{} ft", fmt(num(&n["_roll_spare_ft"])?, "+.2f")),
    );
    bom.insert(
        "PRV_VENT_MM".into(),
        format!("{} mm", fmt(num(&n["_prv_vent_mm"])?, ".0f")),
    );
    bom.insert(
        "FLAVOR_CUT".into(),
        fmt(num(&input["faucet"]["flavor_cut"])?, "g"),
    );
    bom.insert(
        "FLAVOR_4MM_FT".into(),
        fmt(num(&n["_flavor_4mm_mm"])? / 304.8, ".2f"),
    );
    bom.insert(
        "FLAVOR_4MM_COST".into(),
        format!(
            "${}",
            fmt((num(&n["_flavor_4mm_mm"])? / 304.8) * 0.13, ".2f")
        ),
    );
    bom.insert(
        "SODA_FAUCET_CUT".into(),
        fmt(num(&input["faucet"]["soda_cut"])?, "g"),
    );
    bom.insert(
        "SODA_FAUCET_FT".into(),
        fmt(num(&input["faucet"]["soda_cut"])? / 304.8, ".2f"),
    );
    let mut labor = Variables::new();
    labor.insert(
        "TOTAL_INSERTS".into(),
        fmt(
            num(&n["total_m3_inserts_per_build"])? + num(&n["total_m5_inserts_per_build"])?,
            ".4g",
        ),
    );
    labor.insert(
        "TOTAL_SCREWS".into(),
        fmt(
            num(&n["total_m3_screws_per_build"])? + num(&n["total_m5_screws_per_build"])?,
            ".4g",
        ),
    );
    labor.insert(
        "TOTAL_M3_INSERTS".into(),
        fmt(num(&n["total_m3_inserts_per_build"])?, ".4g"),
    );
    labor.insert(
        "TOTAL_M5_INSERTS".into(),
        fmt(num(&n["total_m5_inserts_per_build"])?, ".4g"),
    );
    labor.insert(
        "SEAM_INSERTS".into(),
        fmt(num(&n["enclosure_seam_inserts_per_build"])?, ".4g"),
    );
    labor.insert(
        "SEAM_RODS".into(),
        fmt(num(&n["enclosure_seam_rods_per_build"])?, ".4g"),
    );
    labor.insert(
        "FOAM_CLAMP_INSERTS".into(),
        fmt(num(&n["foam_cap_clamp_inserts_per_build"])?, ".4g"),
    );
    labor.insert(
        "FOAM_SCREWS".into(),
        fmt(num(&n["foam_cap_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "FOAM_FACE_SCREWS".into(),
        fmt(num(&n["inserts_per_foam_cap_face"])?, ".4g"),
    );
    labor.insert(
        "PUMP_MOUNT_SCREWS".into(),
        fmt(num(&n["pump_mount_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "RES_SCREWS".into(),
        fmt(num(&n["reservoir_cap_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "TOUCHFLO_SCREWS".into(),
        fmt(num(&n["touchflo_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "FAUCET_DISPLAY_INSERTS".into(),
        fmt(num(&n["faucet_display_cover_inserts_per_build"])?, ".4g"),
    );
    labor.insert(
        "FAUCET_DISPLAY_SCREWS".into(),
        fmt(num(&n["faucet_display_cover_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "SHELF_INSERTS".into(),
        fmt(num(&n["shelf_inserts_per_build"])?, ".4g"),
    );
    labor.insert(
        "SHELF_SCREWS".into(),
        fmt(num(&n["shelf_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "COND_SCREWS".into(),
        fmt(num(&n["cond_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "DISPLAY_COVER_SCREWS".into(),
        fmt(num(&n["display_cover_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "PUMP_RETAINER_SCREWS".into(),
        fmt(num(&n["pump_retainer_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "DOCK_LOCKS".into(),
        fmt(num(&n["dock_fixture_locks_per_build"])?, ".4g"),
    );
    labor.insert(
        "C14_SCREWS".into(),
        fmt(num(&n["c14_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "ROOF_CLOSURE_SCREWS".into(),
        fmt(num(&n["roof_closure_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "NAMEPLATE_SCREWS".into(),
        fmt(num(&n["nameplate_screws_per_build"])?, ".4g"),
    );
    labor.insert(
        "FLOOR_SCREWS".into(),
        fmt(num(&n["floor_screws_per_build"])?, ".4g"),
    );
    labor.insert("SOLENOIDS".into(), fmt(num(&n["solenoid_count"])?, ".4g"));
    Ok((bom, labor))
}
