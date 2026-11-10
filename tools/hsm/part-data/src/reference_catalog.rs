// Compiled dimensional providers. Source relationships are evaluated by Rust.
#![allow(unused_parens, unused_mut, unused_variables, unreachable_code)]
use super::*;
pub(super) fn globals(cx: &mut Context, module: &str) -> Result<Env> {
    if let Some(v) = cx.cache.get(module) {
        return Ok(v.clone());
    }
    let mut e = Env::new();
    match module {
        "asse1022_assembly" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/asse1022-assembly"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/asse1022-assembly"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/asse1022-assembly/asse1022_assembly.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "BARREL_UPSTREAM".into(),
                attr(cx, "multiplex_asse1022", "INLET_LENGTH")?,
            );
            e.insert(
                "BARREL_DOWNSTREAM".into(),
                b(
                    "+",
                    g(&e, "BARREL_UPSTREAM"),
                    attr(cx, "multiplex_asse1022", "BARREL_LENGTH")?,
                ),
            );
            e.insert(
                "COUPLING_X".into(),
                b(
                    "-",
                    g(&e, "BARREL_UPSTREAM"),
                    attr(cx, "gagira_reducing_coupling", "LENGTH")?,
                ),
            );
            e.insert(
                "PTC_X".into(),
                b(
                    "-",
                    b(
                        "+",
                        g(&e, "COUPLING_X"),
                        attr(cx, "gagira_reducing_coupling", "SMALL_SOCKET_DEPTH")?,
                    ),
                    attr(cx, "jg_pp010822e", "LENGTH")?,
                ),
            );
            e.insert("OUTLET_X".into(), g(&e, "BARREL_DOWNSTREAM"));
            e.insert(
                "TERMINALS".into(),
                object(vec![
                    (
                        json!("tube-in"),
                        t(vec![json!("jg-pp010822e"), json!("tube_port")]),
                    ),
                    (
                        json!("tube-out"),
                        t(vec![json!("flare38-14ptc"), json!("tube_port")]),
                    ),
                    (
                        json!("vent-tip"),
                        t(vec![json!("multiplex-asse1022"), json!("vent")]),
                    ),
                ]),
            );
        }
        "asse1022_threaded_chain" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/asse1022-threaded-chain"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/asse1022-threaded-chain"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/asse1022-threaded-chain/asse1022_threaded_chain.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
        }
        "beduan_solenoid" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/beduan-solenoid"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/beduan-solenoid"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/beduan-solenoid/beduan_solenoid.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            {
                let temp1 = t(vec![json!(hsm_valve_seat_numbers::valve::CORNER_SPACING_X), json!(hsm_valve_seat_numbers::valve::CORNER_SPACING_Y)]);
                e.insert("corner_spacing_x".into(), ix(temp1.clone(), json!(0)));
                e.insert("corner_spacing_y".into(), ix(temp1.clone(), json!(1)));
            }
            {
                let temp2 = t(vec![
                    b("/", g(&e, "corner_spacing_x"), json!(2)),
                    b("/", g(&e, "corner_spacing_y"), json!(2)),
                ]);
                e.insert("corner_inset_x".into(), ix(temp2.clone(), json!(0)));
                e.insert("corner_inset_y".into(), ix(temp2.clone(), json!(1)));
            }
            e.insert("corner_spacing".into(), g(&e, "corner_spacing_x"));
            e.insert("corner_inset".into(), g(&e, "corner_inset_x"));
            e.insert("corner_boss_radius".into(), json!(hsm_valve_seat_numbers::valve::CORNER_BOSS_RADIUS));
            e.insert("post_shoulder_z".into(), json!(hsm_valve_seat_numbers::valve::POST_SHOULDER_Z));
            e.insert("upper_corner_radius".into(), json!(hsm_valve_seat_numbers::valve::UPPER_CORNER_RADIUS));
            {
                let temp3 = t(vec![json!(1.6), json!(3.0)]);
                e.insert("post_mouth_radius".into(), ix(temp3.clone(), json!(0)));
                e.insert("post_mouth_depth".into(), ix(temp3.clone(), json!(1)));
            }
            e.insert("body_radius".into(), json!(hsm_valve_seat_numbers::valve::BODY_RADIUS));
            e.insert("body_width".into(), b("*", json!(2), g(&e, "body_radius")));
            e.insert("bearing_radius".into(), json!(hsm_valve_seat_numbers::valve::BEARING_RADIUS));
            e.insert("bearing_z_range".into(), t(vec![json!(hsm_valve_seat_numbers::valve::BEARING_Z[0]), json!(hsm_valve_seat_numbers::valve::BEARING_Z[1])]));
            e.insert("lower_edge_fillet".into(), json!(2.5));
            e.insert(
                "body_main_z_range".into(),
                t(vec![json!(hsm_valve_seat_numbers::valve::BODY_MAIN_Z[0]), json!(hsm_valve_seat_numbers::valve::BODY_MAIN_Z[1])]),
            );
            {
                let temp4 = t(vec![json!(hsm_valve_seat_numbers::valve::CAP_WIDTH_X), json!(hsm_valve_seat_numbers::valve::CAP_DEPTH_Y), json!(hsm_valve_seat_numbers::valve::CAP_CORNER_RADIUS)]);
                e.insert("cap_width_x".into(), ix(temp4.clone(), json!(0)));
                e.insert("cap_depth_y".into(), ix(temp4.clone(), json!(1)));
                e.insert("cap_corner_radius".into(), ix(temp4.clone(), json!(2)));
            }
            e.insert("top_box_z_range".into(), t(vec![json!(hsm_valve_seat_numbers::valve::TOP_BOX_Z[0]), json!(hsm_valve_seat_numbers::valve::TOP_BOX_Z[1])]));
            e.insert("body_top_z".into(), ix(g(&e, "top_box_z_range"), json!(1)));
            e.insert(
                "top_box_height".into(),
                b(
                    "-",
                    g(&e, "body_top_z"),
                    ix(g(&e, "top_box_z_range"), json!(0)),
                ),
            );
            e.insert(
                "boss_z_range".into(),
                t(vec![
                    ix(g(&e, "bearing_z_range"), json!(0)),
                    g(&e, "body_top_z"),
                ]),
            );
            e.insert(
                "corner_boss_z_range".into(),
                t(vec![json!(0.0), g(&e, "body_top_z")]),
            );
            e.insert("body_width_x".into(), json!(34.25));
            e.insert(
                "body_x_pad".into(),
                b(
                    "/",
                    b("-", g(&e, "body_width_x"), g(&e, "cap_width_x")),
                    json!(2),
                ),
            );
            e.insert("coil_depth".into(), json!(24.4));
            e.insert("coil_z_range".into(), t(vec![json!(27.9), json!(57.3)]));
            e.insert("bracket_top_z".into(), json!(56.4));
            {
                let temp5 = t(vec![json!(0.15), u("-", json!(0.1))]);
                e.insert("coil_center_x".into(), ix(temp5.clone(), json!(0)));
                e.insert("coil_center_y".into(), ix(temp5.clone(), json!(1)));
            }
            e.insert("coil_radius".into(), json!(12.15));
            e.insert(
                "coil_body_z_range".into(),
                t(vec![json!(28.2), json!(54.8)]),
            );
            {
                let temp6 = t(vec![json!(32.4), json!(17.2), json!(1.6)]);
                e.insert("bracket_width".into(), ix(temp6.clone(), json!(0)));
                e.insert("bracket_depth".into(), ix(temp6.clone(), json!(1)));
                e.insert("bracket_thickness".into(), ix(temp6.clone(), json!(2)));
            }
            e.insert("bracket_outer_bend".into(), json!(2.4));
            e.insert(
                "bracket_base_z_range".into(),
                t(vec![json!(26.0), json!(27.9)]),
            );
            {
                let temp7 = t(vec![json!(3.2), json!(2.3)]);
                e.insert("screw_head_radius".into(), ix(temp7.clone(), json!(0)));
                e.insert("screw_head_height".into(), ix(temp7.clone(), json!(1)));
            }
            {
                let temp8 = t(vec![json!(hsm_valve_seat_numbers::valve::PORT_RADIUS), json!(59.5), json!(hsm_valve_seat_numbers::valve::PORT_CENTER_Z)]);
                e.insert("port_radius".into(), ix(temp8.clone(), json!(0)));
                e.insert("port_length".into(), ix(temp8.clone(), json!(1)));
                e.insert("port_center_z".into(), ix(temp8.clone(), json!(2)));
            }
            e.insert("port_neck_radius".into(), json!(6.1));
            {
                let temp9 = t(vec![json!(5.1), json!(4.9)]);
                e.insert("collet_radius".into(), ix(temp9.clone(), json!(0)));
                e.insert("collet_neck_radius".into(), ix(temp9.clone(), json!(1)));
            }
            e.insert("collet_ear_radius".into(), json!(6.9));
            e.insert(
                "collet_ear_sectors".into(),
                object(vec![
                    (u("-", json!(1)), t(vec![t(vec![json!(2.0), json!(33.0)])])),
                    (
                        json!(1),
                        t(vec![t(vec![u("-", json!(115.0)), u("-", json!(76.0))])]),
                    ),
                ]),
            );
            e.insert("collet_clip_radius".into(), json!(6.75));
            e.insert(
                "collet_clip_sectors".into(),
                object(vec![
                    (
                        u("-", json!(1)),
                        t(vec![u("-", json!(130.0)), json!(140.0)]),
                    ),
                    (json!(1), t(vec![json!(140.0), json!(380.0)])),
                ]),
            );
            {
                let temp10 = t(vec![json!(3.2), json!(7.5)]);
                e.insert("port_mouth_radius".into(), ix(temp10.clone(), json!(0)));
                e.insert("port_mouth_depth".into(), ix(temp10.clone(), json!(1)));
            }
            {
                let temp11 = t(vec![json!(6.3), json!(0.8)]);
                e.insert("spade_width".into(), ix(temp11.clone(), json!(0)));
                e.insert("spade_thickness".into(), ix(temp11.clone(), json!(1)));
            }
            e.insert("spade_x_spacing".into(), json!(14.9));
            e.insert("spade_z_center".into(), json!(52.2));
            e.insert("coil_face_y".into(), json!(18.5));
            e.insert("spade_length".into(), json!(8.6));
            e.insert("spade_hole_radius".into(), json!(0.9));
            e.insert(
                "terminal_block_z_range".into(),
                t(vec![json!(50.0), json!(57.3)]),
            );
            e.insert(
                "underside_relief_xy".into(),
                t(vec![u("-", json!(0.25)), json!(8.4)]),
            );
            e.insert(
                "underside_relief_size".into(),
                t(vec![json!(5.5), json!(5.2)]),
            );
            e.insert("underside_relief_top_z".into(), json!(6.9));
        }
        "branch_stem_tees" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/branch-stem-tees"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/branch-stem-tees"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/branch-stem-tees/branch_stem_tees.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "STEP_PATHS".into(),
                object(vec![
                    (
                        json!("neofit"),
                        b("/", g(&e, "HERE"), json!("neofit-atbu444-e-estimate.step")),
                    ),
                    (
                        json!("john-guest"),
                        b(
                            "/",
                            g(&e, "HERE"),
                            json!("john-guest-ci580808w-estimate.step"),
                        ),
                    ),
                ]),
            );
        }
        "compressor" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/compressor"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/compressor"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/compressor/compressor.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("BASE_X".into(), json!(96.0));
            e.insert("BASE_Y".into(), json!(160.0));
            e.insert("BASE_Z".into(), json!(15.0));
            e.insert("SHELL_X".into(), json!(110.0));
            e.insert("SHELL_Y".into(), json!(125.0));
            e.insert("SHELL_Z".into(), json!(120.0));
            e.insert("SHELL_OFFSET_Y".into(), json!(10.0));
            e.insert("MOUNT_D".into(), json!(14.0));
            e.insert("MOUNT_INSET".into(), json!(14.5));
            e.insert("POWER_X".into(), json!(45.0));
            e.insert("POWER_Y".into(), json!(27.5));
            e.insert("POWER_Z".into(), json!(45.0));
            e.insert("POWER_GAP".into(), json!(15.0));
            e.insert(
                "OVERALL_H".into(),
                b("+", g(&e, "BASE_Z"), g(&e, "SHELL_Z")),
            );
            e.insert(
                "MOUNT_PITCH_X".into(),
                b(
                    "-",
                    g(&e, "BASE_X"),
                    b("*", json!(2.0), g(&e, "MOUNT_INSET")),
                ),
            );
            e.insert(
                "MOUNT_PITCH_Y".into(),
                b(
                    "-",
                    g(&e, "BASE_Y"),
                    b("*", json!(2.0), g(&e, "MOUNT_INSET")),
                ),
            );
            e.insert(
                "SHELL_OVERHANG_X".into(),
                b("/", b("-", g(&e, "SHELL_X"), g(&e, "BASE_X")), json!(2.0)),
            );
            e.insert(
                "PLATE_REACH_LONG".into(),
                b(
                    "+",
                    b("/", b("-", g(&e, "BASE_Y"), g(&e, "SHELL_Y")), json!(2.0)),
                    g(&e, "SHELL_OFFSET_Y"),
                ),
            );
            e.insert(
                "PLATE_REACH_SHORT".into(),
                b(
                    "-",
                    b("/", b("-", g(&e, "BASE_Y"), g(&e, "SHELL_Y")), json!(2.0)),
                    g(&e, "SHELL_OFFSET_Y"),
                ),
            );
            e.insert(
                "MOUNT_LIGAMENT".into(),
                b(
                    "-",
                    g(&e, "MOUNT_INSET"),
                    b("/", g(&e, "MOUNT_D"), json!(2.0)),
                ),
            );
            e.insert(
                "SHELL_TANGENT_Y".into(),
                b(
                    "-",
                    g(&e, "SHELL_OFFSET_Y"),
                    b("/", g(&e, "SHELL_Y"), json!(2.0)),
                ),
            );
            e.insert(
                "POWER_Y0".into(),
                b("/", u("-", g(&e, "BASE_Y")), json!(2.0)),
            );
            e.insert(
                "POWER_Z0".into(),
                b("+", g(&e, "BASE_Z"), g(&e, "POWER_GAP")),
            );
            e.insert(
                "POWER_Z1".into(),
                b("+", g(&e, "POWER_Z0"), g(&e, "POWER_Z")),
            );
            e.insert(
                "POWER_FLANK_REACH".into(),
                b(
                    "-",
                    b("/", g(&e, "BASE_X"), json!(2.0)),
                    b("/", g(&e, "POWER_X"), json!(2.0)),
                ),
            );
            e.insert("DISCHARGE_Z".into(), json!(75.0));
            e.insert("SUCTION_Z".into(), json!(60.0));
            e.insert("PROCESS_Z".into(), json!(100.0));
            e.insert("PROCESS_CLAMP".into(), json!(20.0));
            e.insert(
                "PROCESS_OVER_SUCTION".into(),
                b("-", g(&e, "PROCESS_Z"), g(&e, "SUCTION_Z")),
            );
        }
        "condenser_block" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/condenser-block"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/condenser-block"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/condenser-block/condenser_block.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("AIRFLOW".into(), json!(56.0));
            e.insert("FACE_A".into(), json!(154.0));
            e.insert("FACE_B".into(), json!(137.0));
            e.insert("PLATE_T".into(), json!(0.4));
            e.insert("RECESS_Y".into(), json!(20.0));
            e.insert(
                "RECESS_Z".into(),
                b("-", g(&e, "FACE_B"), b("*", json!(2.0), g(&e, "PLATE_T"))),
            );
            e.insert("MOUNT_D".into(), json!(5.0));
            e.insert("MOUNT_IN_INTAKE".into(), json!(29.0));
            e.insert("MOUNT_IN_AFT".into(), json!(15.0));
        }
        "digiten_flow_sensor" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/digiten-flow-sensor"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/digiten-flow-sensor"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/digiten-flow-sensor/digiten_flow_sensor.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("port_face".into(), json!(30.5));
            e.insert("port_dia".into(), json!(18.3));
            e.insert("port_neck_radius".into(), json!(7.95));
            e.insert("port_neck_end".into(), json!(19.6));
            e.insert("port_collar_end".into(), json!(26.8));
            e.insert(
                "port_collar_radii".into(),
                t(vec![json!(8.95), json!(9.15)]),
            );
            e.insert("port_collet_radius".into(), json!(5.0));
            e.insert("port_mouth_radius".into(), json!(3.25));
            e.insert("port_mouth_depth".into(), json!(6.0));
            e.insert("body_dia".into(), json!(35.0));
            e.insert("body_len".into(), json!(28.3));
            e.insert("body_center_x".into(), json!(0.0));
            e.insert("body_center_z".into(), json!(8.9));
            e.insert("label_y".into(), json!(18.7));
            e.insert("underside_y".into(), u("-", json!(9.4)));
            e.insert(
                "housing_profile".into(),
                t(vec![
                    t(vec![u("-", json!(9.4)), json!(13.9)]),
                    t(vec![u("-", json!(8.1)), json!(15.1)]),
                    t(vec![json!(7.3), json!(15.45)]),
                    t(vec![json!(7.3), json!(17.5)]),
                    t(vec![json!(10.6), json!(17.5)]),
                    t(vec![json!(10.6), json!(17.45)]),
                    t(vec![json!(14.8), json!(17.45)]),
                    t(vec![json!(14.8), json!(17.5)]),
                    t(vec![json!(17.2), json!(17.5)]),
                    t(vec![json!(18.7), json!(13.2)]),
                ]),
            );
            e.insert("boss_x".into(), json!(12.5));
            e.insert("boss_z".into(), json!(14.0));
            e.insert("boss_radius".into(), json!(3.45));
            e.insert("boss_y_range".into(), t(vec![json!(0.0), json!(17.2)]));
            e.insert("screw_head_radius".into(), json!(2.65));
            e.insert(
                "screw_head_y_range".into(),
                t(vec![json!(17.2), json!(18.9)]),
            );
            e.insert(
                "wire_root".into(),
                t(vec![json!(0.0), json!(14.8), json!(26.5)]),
            );
            e.insert("wire_root_width".into(), json!(6.0));
            e.insert("wire_root_depth".into(), json!(3.0));
            e.insert("wire_boss_dia".into(), g(&e, "wire_root_width"));
            e.insert("wire_boss_len".into(), json!(1.5));
        }
        "flare38_14ptc" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/flare38-14ptc"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/flare38-14ptc"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/flare38-14ptc/flare38_14ptc.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("NUT_ACROSS_CORNERS".into(), json!(22.0));
            e.insert("NUT_LENGTH".into(), json!(14.0));
            e.insert("NUT_BORE_D".into(), json!(15.88));
            {
                let temp1 = t(vec![json!(14.0), json!(8.0)]);
                e.insert("NECK_D".into(), ix(temp1.clone(), json!(0)));
                e.insert("NECK_LENGTH".into(), ix(temp1.clone(), json!(1)));
            }
            {
                let temp2 = t(vec![json!(17.5), json!(15.5)]);
                e.insert("COLLET38_D".into(), ix(temp2.clone(), json!(0)));
                e.insert("COLLET38_LENGTH".into(), ix(temp2.clone(), json!(1)));
            }
            e.insert("COLLAR_LENGTH".into(), json!(2.0));
            {
                let temp3 = t(vec![json!(14.0), json!(13.5)]);
                e.insert("COLLET14_D".into(), ix(temp3.clone(), json!(0)));
                e.insert("COLLET14_LENGTH".into(), ix(temp3.clone(), json!(1)));
            }
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert(
                "LENGTH".into(),
                b(
                    "+",
                    b(
                        "+",
                        b(
                            "+",
                            b("+", g(&e, "NUT_LENGTH"), g(&e, "NECK_LENGTH")),
                            g(&e, "COLLET38_LENGTH"),
                        ),
                        g(&e, "COLLAR_LENGTH"),
                    ),
                    g(&e, "COLLET14_LENGTH"),
                ),
            );
        }
        "g_ganen_foot" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/common-foot"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/common-foot"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/g-ganen-pump/common-foot/g_ganen_foot.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("PAD_THICKNESS".into(), json!(7.0));
            e.insert("SLOT_Y".into(), json!(38.5));
            e.insert("WIDTH".into(), json!(18.0));
            e.insert("SLOT_WIDTH".into(), json!(4.5));
            e.insert("SLOT_LENGTH".into(), json!(6.8));
            e.insert(
                "CLIP_AXIAL_INTERVAL".into(),
                t(vec![u("-", json!(9.0)), json!(9.0)]),
            );
            e.insert(
                "PROFILE_YZ".into(),
                t(vec![
                    t(vec![u("-", json!(10.5)), json!(0.0)]),
                    t(vec![json!(9.0), json!(0.0)]),
                    t(vec![json!(9.0), g(&e, "PAD_THICKNESS")]),
                    t(vec![u("-", json!(3.5)), g(&e, "PAD_THICKNESS")]),
                    t(vec![u("-", json!(5.5)), json!(9.4)]),
                    t(vec![u("-", json!(10.0)), json!(9.4)]),
                    t(vec![u("-", json!(10.5)), json!(10.0)]),
                    t(vec![u("-", json!(10.5)), json!(12.0)]),
                    t(vec![u("-", json!(10.0)), json!(15.4)]),
                    t(vec![u("-", json!(10.9)), json!(15.8)]),
                    t(vec![u("-", json!(11.2)), json!(16.2)]),
                    t(vec![u("-", json!(13.5)), json!(15.1)]),
                    t(vec![u("-", json!(14.4)), json!(15.6)]),
                    t(vec![u("-", json!(14.5)), json!(16.3)]),
                    t(vec![u("-", json!(12.8)), json!(17.8)]),
                    t(vec![u("-", json!(13.5)), json!(18.4)]),
                    t(vec![u("-", json!(14.2)), json!(18.4)]),
                    t(vec![u("-", json!(14.9)), json!(18.0)]),
                    t(vec![u("-", json!(15.7)), json!(17.9)]),
                    t(vec![u("-", json!(16.0)), json!(9.7)]),
                    t(vec![u("-", json!(12.2)), json!(8.4)]),
                    t(vec![u("-", json!(12.2)), json!(7.5)]),
                    t(vec![u("-", json!(13.5)), json!(4.2)]),
                    t(vec![u("-", json!(12.2)), json!(2.1)]),
                ]),
            );
        }
        "g_ganen_pump" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/g-ganen-pump"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/g-ganen-pump"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/g-ganen-pump/g_ganen_pump.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
        }
        "g_ganen_installation" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/installation"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/installation"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/g-ganen-pump/installation/g_ganen_installation.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("SCENE_KEY".into(), json!("g-ganen-pump"));
            e.insert("YAW".into(), json!(90.0));
            e.insert("REAR_CLEARANCE".into(), json!(9.7));
            e.insert("WASHER_OD".into(), json!(9.0));
            e.insert("WASHER_T".into(), json!(0.8));
            e.insert("SCREW_D".into(), json!(3.0));
            e.insert("SCREW_LENGTH".into(), json!(20.0));
            e.insert("SCREW_BORE_MIN_DEPTH".into(), json!(8.5));
            e.insert("SCREW_SLOT_OFFSET_OUTWARD".into(), json!(1.5));
            e.insert("RAIL_X".into(), t(vec![json!(0.5), json!(76.5)]));
            e.insert("CLIP_X".into(), {
                let argv = vec![];
                let kwargs = json!({});
                call(
                    cx,
                    "g_ganen_foot",
                    "rail_engagement_interval",
                    argv,
                    kwargs,
                    None,
                )?
            });
            e.insert("SELECTED_SLIDER_X".into(), {
                let mut e = e.clone();
                let mut temp1 = Vec::new();
                for item in seq(t(vec![
                    json!("rear_yminus"),
                    json!("rear_yplus"),
                    json!("head_yminus"),
                    json!("head_yplus"),
                ])) {
                    e.insert("name".into(), item);
                    temp1.push((
                        g(&e, "name"),
                        (if truth(&method(g(&e, "name"), "startswith", vec![json!("head_")])) {
                            b(
                                "-",
                                ix(g(&e, "RAIL_X"), json!(0)),
                                ix(g(&e, "CLIP_X"), json!(0)),
                            )
                        } else {
                            b(
                                "-",
                                ix(g(&e, "RAIL_X"), json!(1)),
                                ix(g(&e, "CLIP_X"), json!(1)),
                            )
                        }),
                    ));
                }
                object(temp1)
            });
            e.insert("SLOT_Y".into(), attr(cx, "g_ganen_foot", "SLOT_Y")?);
            e.insert(
                "CAP_PUMP_ORIGIN".into(),
                t(vec![
                    b(
                        "+",
                        u("-", json!(59.13545827612205)),
                        g(&e, "REAR_CLEARANCE"),
                    ),
                    json!(2.07113514496717),
                ]),
            );
            e.insert(
                "CAP_MOUNT_XY".into(),
                t(seq({
                    let mut e = e.clone();
                    let mut temp2 = Vec::new();
                    for item in seq(method(g(&e, "SELECTED_SLIDER_X"), "items", vec![])) {
                        {
                            let temp3 = item;
                            e.insert("name".into(), ix(temp3.clone(), json!(0)));
                            e.insert("x".into(), ix(temp3.clone(), json!(1)));
                        }
                        temp2.push(t(vec![
                            b("-", ix(g(&e, "CAP_PUMP_ORIGIN"), json!(0)), g(&e, "x")),
                            b(
                                "-",
                                ix(g(&e, "CAP_PUMP_ORIGIN"), json!(1)),
                                b(
                                    "*",
                                    (if truth(&json!(compare("in", json!("yminus"), g(&e, "name"))))
                                    {
                                        u("-", json!(1))
                                    } else {
                                        json!(1)
                                    }),
                                    b("+", g(&e, "SLOT_Y"), g(&e, "SCREW_SLOT_OFFSET_OUTWARD")),
                                ),
                            ),
                        ]));
                    }
                    json!(temp2)
                })),
            );
        }
        "g_ganen_integration" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/integration-envelope"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/integration-envelope"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/g-ganen-pump/integration-envelope/g_ganen_integration.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "NATIVE".into(),
                b(
                    "/",
                    g(&e, "HERE"),
                    json!("g-ganen-integration-envelope.step"),
                ),
            );
        }
        "native_queries" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/integration-envelope"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/g-ganen-pump/integration-envelope"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/g-ganen-pump/integration-envelope/native_queries.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
        }
        "gagira_reducing_coupling" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/gagira-reducing-coupling"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/gagira-reducing-coupling"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/gagira-reducing-coupling/gagira_reducing_coupling.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("HEX_ACROSS_CORNERS".into(), json!(25.67));
            e.insert("LENGTH".into(), json!(30.5));
            e.insert("SMALL_SOCKET_D".into(), json!(13.72));
            e.insert("SMALL_SOCKET_DEPTH".into(), json!(11.0));
            e.insert("LARGE_SOCKET_D".into(), json!(17.15));
            e.insert("LARGE_SOCKET_DEPTH".into(), json!(13.0));
        }
        "gasher_check_valve" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/gasher-check-valve"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/gasher-check-valve"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/gasher-check-valve/gasher_check_valve.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("HEX_ACROSS_CORNERS".into(), json!(17.0));
            e.insert("TOTAL_LENGTH".into(), json!(40.0));
            e.insert("THREAD_D".into(), json!(13.7));
            e.insert("STUB_LENGTH".into(), json!(11.0));
            e.insert("SOCKET_D".into(), json!(15.5));
            e.insert("SOCKET_LENGTH".into(), json!(11.0));
            e.insert(
                "HEX_LENGTH".into(),
                b(
                    "-",
                    b("-", g(&e, "TOTAL_LENGTH"), g(&e, "STUB_LENGTH")),
                    g(&e, "SOCKET_LENGTH"),
                ),
            );
        }
        "hlghlg_check_valve" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/hlghlg-check-valve"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/hlghlg-check-valve"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/hlghlg-check-valve/hlghlg_check_valve.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert("LENGTH".into(), json!(51.0));
            e.insert("BODY_D".into(), json!(14.0));
            e.insert(
                "SECTIONS".into(),
                t(vec![
                    t(vec![json!("inlet collet"), json!(12.0), json!(1.6)]),
                    t(vec![json!("inlet socket"), g(&e, "BODY_D"), json!(14.4)]),
                    t(vec![json!("neck"), json!(9.3), json!(6.2)]),
                    t(vec![json!("barrel"), json!(12.6), json!(11.6)]),
                    t(vec![json!("barrel step"), json!(13.0), json!(1.8)]),
                    t(vec![json!("outlet socket"), g(&e, "BODY_D"), json!(13.4)]),
                    t(vec![json!("outlet collet"), json!(12.6), json!(2.0)]),
                ]),
            );
        }
        "iec_c14_inlet" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/iec-c14-inlet"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/iec-c14-inlet"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/iec-c14-inlet/iec_c14_inlet.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("FLANGE_W".into(), json!(49.77));
            e.insert("FLANGE_H".into(), json!(21.9));
            e.insert("FLANGE_T".into(), json!(3.25));
            e.insert("FLANGE_END_CHORD".into(), json!(17.98));
            e.insert("EAR_CX".into(), json!(20.0));
            e.insert(
                "EAR_R".into(),
                b("-", b("/", g(&e, "FLANGE_W"), json!(2.0)), g(&e, "EAR_CX")),
            );
            e.insert(
                "FLANGE_SHOULDER_X".into(),
                b(
                    "-",
                    b("/", g(&e, "FLANGE_W"), json!(2.0)),
                    math_fn(
                        "sqrt",
                        vec![b(
                            "-",
                            b("**", g(&e, "FLANGE_END_CHORD"), json!(2)),
                            b("**", b("/", g(&e, "FLANGE_H"), json!(2.0)), json!(2)),
                        )],
                    ),
                ),
            );
            e.insert("FLANGE_KNUCKLE_R".into(), json!(1.2));
            e.insert("SCREW_PITCH".into(), json!(40.21));
            e.insert("SCREW_D".into(), json!(3.24));
            e.insert("CSK_D".into(), json!(6.1));
            e.insert(
                "CSK_DEPTH".into(),
                b("/", b("-", g(&e, "CSK_D"), g(&e, "SCREW_D")), json!(2.0)),
            );
            e.insert("CUTOUT_W".into(), json!(30.95));
            e.insert("CUTOUT_H".into(), json!(22.15));
            e.insert("CUTOUT_R".into(), json!(3.0));
            e.insert("RIM_W".into(), json!(31.03));
            e.insert("RIM_H".into(), json!(22.13));
            e.insert("RIM_R".into(), json!(6.0));
            e.insert("RIM_PROUD".into(), json!(1.84));
            e.insert("MOUTH_W".into(), json!(24.82));
            e.insert("MOUTH_H".into(), json!(16.26));
            e.insert("MOUTH_TOP_R".into(), json!(2.3));
            e.insert("MOUTH_CHAMFER".into(), json!(4.8));
            e.insert("CAVITY_FLOOR_Y".into(), u("-", json!(14.3)));
            e.insert("BLADE_W".into(), json!(4.0));
            e.insert("BLADE_T".into(), json!(2.0));
            e.insert(
                "BLADE_STATIONS".into(),
                t(vec![
                    t(vec![u("-", json!(6.45)), json!(2.3), u("-", json!(2.9))]),
                    t(vec![json!(0.3), u("-", json!(1.9)), u("-", json!(1.1))]),
                    t(vec![json!(6.95), json!(2.2), u("-", json!(2.9))]),
                ]),
            );
            e.insert("BODY_W".into(), json!(26.1));
            e.insert("BODY_H".into(), json!(18.0));
            e.insert("BODY_DEPTH".into(), json!(13.65));
            e.insert("BODY_CHAMFER_LEG".into(), json!(4.85));
            e.insert("BODY_TOP_R".into(), json!(1.0));
            e.insert("BOSS_W".into(), json!(4.0));
            e.insert("BOSS_H".into(), json!(10.0));
            e.insert("BOSS_R".into(), json!(1.0));
            e.insert("BOSS_PROUD".into(), json!(1.17));
            e.insert("TAB_W".into(), json!(6.3));
            e.insert("TAB_T".into(), json!(0.8));
            e.insert("TAB_TIP_Y".into(), u("-", json!(25.0)));
            e.insert("TAB_HOLE_D".into(), json!(2.0));
            e.insert("TAB_HOLE_FROM_TIP".into(), json!(3.5));
            e.insert(
                "TAB_STATIONS".into(),
                t(vec![
                    t(vec![u("-", json!(6.7)), json!(2.45)]),
                    t(vec![json!(0.35), u("-", json!(2.6))]),
                    t(vec![json!(7.1), json!(2.65)]),
                ]),
            );
            e.insert(
                "BOSS_STATIONS".into(),
                t(vec![
                    t(vec![u("-", json!(6.7)), json!(2.0)]),
                    t(vec![json!(0.35), u("-", json!(2.5))]),
                    t(vec![json!(7.1), json!(2.0)]),
                ]),
            );
            e.insert("flange_back_y".into(), u("-", g(&e, "FLANGE_T")));
            e.insert(
                "body_end_y".into(),
                b("-", g(&e, "flange_back_y"), g(&e, "BODY_DEPTH")),
            );
            e.insert(
                "boss_end_y".into(),
                b("-", g(&e, "body_end_y"), g(&e, "BOSS_PROUD")),
            );
        }
        "jg_bulkhead_union" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/jg-bulkhead-union"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/jg-bulkhead-union"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/jg-bulkhead-union/jg_bulkhead_union.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("PORT_D".into(), json!(6.35));
            e.insert("TUBE_OD".into(), json!(6.35));
            e.insert("THREAD_D".into(), json!(16.7));
            e.insert("MOUNTING_HOLE_D".into(), json!(17.0));
            e.insert("TUBE_STOP_DEPTH".into(), json!(15.7));
            e.insert("PORT_DEPTH".into(), json!(15.7));
            e.insert("OVERALL".into(), json!(37.55273081350097));
            e.insert("near_ring_face_y".into(), json!(11.521369623928024));
            e.insert("PROUD_LENGTH".into(), json!(11.521369623928024));
            e.insert("far_ring_face_y".into(), u("-", json!(26.031361189572948)));
            e.insert("BODY_D".into(), json!(23.34348));
            e.insert("FLANGE_D".into(), json!(23.34348));
            e.insert("RING_D".into(), json!(10.9));
            e.insert("FLANGE_AF".into(), json!(18.83501909374671));
            e.insert("NUT_AF".into(), json!(20.001471308895436));
            e.insert("NUT_D".into(), json!(22.50104));
            e.insert("NUT_LEN".into(), json!(5.939959183240793));
            e.insert("CAPTURED_NUT_GAP".into(), json!(5.691909221634731));
            e.insert("PANEL_THREAD".into(), json!(13.5));
        }
        "jg_pp010822e" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/jg-pp010822e"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/jg-pp010822e"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/jg-pp010822e/jg_pp010822e.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("COLLET_D".into(), json!(14.0));
            e.insert("COLLET_LENGTH".into(), json!(13.5));
            e.insert("HEX_ACROSS_CORNERS".into(), json!(16.5));
            e.insert("HEX_LENGTH".into(), json!(5.0));
            e.insert("SHANK_D".into(), json!(13.7));
            e.insert("SHANK_LENGTH".into(), json!(11.0));
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert(
                "LENGTH".into(),
                b(
                    "+",
                    b("+", g(&e, "COLLET_LENGTH"), g(&e, "HEX_LENGTH")),
                    g(&e, "SHANK_LENGTH"),
                ),
            );
        }
        "jg_pp0208e_tee" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/jg-pp0208e-tee"));
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/jg-pp0208e-tee"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/jg-pp0208e-tee/jg_pp0208e_tee.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("TUBE_OD".into(), json!(6.35));
            e.insert("RUN_SPAN".into(), json!(39.0));
            e.insert("REACH".into(), json!(19.5));
            e.insert("INSERTION".into(), json!(15.7));
            e.insert("COLLAR_D".into(), json!(16.3));
            e.insert("BORE_D".into(), json!(4.3));
            e.insert("BRANCH_ENVELOPE".into(), json!(27.7));
            e.insert("ARM_D".into(), json!(10.6));
            e.insert("COLLAR_NEAR".into(), json!(8.2));
            e.insert("COLLAR_FAR".into(), json!(16.3));
            e.insert("COLLET_D".into(), json!(9.7));
            e.insert("COLLET_BORE".into(), json!(6.7));
            e.insert(
                "COLLET_PROUD".into(),
                b("-", g(&e, "REACH"), g(&e, "COLLAR_FAR")),
            );
            e.insert("MEASURE_TOL".into(), json!(0.06));
            e.insert(
                "ARMS".into(),
                t(vec![
                    t(vec![
                        t(vec![json!(0.0), json!(0.0), json!(1.0)]),
                        json!("+z"),
                    ]),
                    t(vec![
                        t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
                        json!("-z"),
                    ]),
                    t(vec![
                        t(vec![json!(0.0), json!(1.0), json!(0.0)]),
                        json!("branch"),
                    ]),
                ]),
            );
        }
        "elbow" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/jg-pp0308e-elbow"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/jg-pp0308e-elbow"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/jg-pp0308e-elbow/elbow.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("TUBE_OD".into(), json!(6.35));
            e.insert("COLLET_FACE".into(), json!(20.56239));
            e.insert("FIXED_FACE".into(), json!(18.84));
            e.insert("INSERTION".into(), Value::Null);
            e.insert("RELEASE_TRAVEL".into(), Value::Null);
        }
        "jg_pp0408w" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/jg-pp0408w"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/jg-pp0408w"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/jg-pp0408w/jg_pp0408w.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("RING_D".into(), json!(15.1));
            e.insert("RING_LEN".into(), json!(12.08));
            e.insert("BARREL_D".into(), json!(9.31));
            e.insert("BARREL_LEN".into(), json!(12.16));
            e.insert("COLLET_D".into(), json!(9.57));
            e.insert("COLLET_WALL".into(), json!(1.44));
            e.insert("PORT_D".into(), json!(6.35));
            e.insert("BODY_LEN".into(), json!(36.32));
            e.insert("OVERALL".into(), json!(41.8));
            e.insert("OVERALL_PRESSED".into(), json!(39.13));
            e.insert("INSERTION".into(), json!(16.0));
            e.insert(
                "COLLET_BORE".into(),
                b(
                    "-",
                    g(&e, "COLLET_D"),
                    b("*", json!(2.0), g(&e, "COLLET_WALL")),
                ),
            );
            e.insert(
                "COLLET_PROUD".into(),
                b("/", b("-", g(&e, "OVERALL"), g(&e, "BODY_LEN")), json!(2.0)),
            );
            e.insert(
                "COLLET_TRAVEL".into(),
                b(
                    "/",
                    b("-", g(&e, "OVERALL"), g(&e, "OVERALL_PRESSED")),
                    json!(2.0),
                ),
            );
            e.insert("BORE_D".into(), json!(4.32));
            e.insert(
                "barrel_face_z".into(),
                b("/", g(&e, "BARREL_LEN"), json!(2.0)),
            );
            e.insert(
                "ring_face_z".into(),
                b("+", g(&e, "barrel_face_z"), g(&e, "RING_LEN")),
            );
            e.insert(
                "port_face_z".into(),
                b("+", g(&e, "ring_face_z"), g(&e, "COLLET_PROUD")),
            );
        }
        "jg_pp061208w" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/jg-pp061208w"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/jg-pp061208w"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/jg-pp061208w/jg_pp061208w.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "PARAMETER_SNAPSHOT_SHA256".into(),
                json!("605b991c076da190a2655bdeda8b7d49691228aa4dbbbada204f4be7200971e4"),
            );
            e.insert(
                "PARAMETERS".into(),
                object(vec![
                    (json!("units"), json!("mm")),
                    (json!("part"), json!("John Guest PP061208W")),
                    (json!("nominal_stem_diameter_mm"), json!(9.525)),
                    (json!("nominal_free_stem_to_shoulder_mm"), json!(18.29)),
                    (json!("stem_tip_chamfer_display_mm"), json!(0.6)),
                    (
                        json!("source_stem_tip_station_mm"),
                        json!(75.83561645217995),
                    ),
                    (
                        json!("source_shoulder_station_mm"),
                        json!(94.12561645217995),
                    ),
                    (
                        json!("source_release_station_mm"),
                        json!(107.76171740799833),
                    ),
                    (json!("source_body_end_station_mm"), json!(106.175)),
                    (json!("source_collet_start_station_mm"), json!(106.255)),
                    (json!("stem_cylinder_end_mm"), json!(17.239383547820054)),
                    (json!("body_face_x_mm"), json!(30.33938354782005)),
                    (json!("collet_start_x_mm"), json!(30.419383547820047)),
                    (json!("length_mm"), json!(31.926100955818384)),
                    (
                        json!("body_profile_x_radius_mm"),
                        json!([
                            (json!([(json!(17.239383547820054)), (json!(4.805))])),
                            (json!([(json!(17.639383547820046)), (json!(4.962))])),
                            (json!([(json!(18.03938354782005)), (json!(5.358))])),
                            (json!([(json!(18.239383547820054)), (json!(6.281))])),
                            (json!([(json!(18.439383547820057)), (json!(6.59))])),
                            (json!([(json!(18.83938354782005)), (json!(6.858))])),
                            (json!([(json!(19.639383547820046)), (json!(6.959))])),
                            (json!([(json!(22.239383547820054)), (json!(6.951))])),
                            (json!([(json!(22.639383547820046)), (json!(7.11))])),
                            (json!([(json!(23.439383547820057)), (json!(7.921))])),
                            (json!([(json!(23.83938354782005)), (json!(8.184))])),
                            (json!([(json!(27.03938354782005)), (json!(8.293))])),
                            (json!([(json!(27.439383547820057)), (json!(8.26))])),
                            (json!([(json!(27.83938354782005)), (json!(8.045))])),
                            (json!([(json!(28.03938354782005)), (json!(7.277))])),
                            (json!([(json!(28.239383547820054)), (json!(7.076))])),
                            (json!([(json!(29.639383547820046)), (json!(7.252))])),
                            (json!([(json!(30.03938354782005)), (json!(7.055))])),
                            (json!([(json!(30.239383547820054)), (json!(6.118))])),
                            (json!([(json!(30.33938354782005)), (json!(5.802000000000023))]))
                        ]),
                    ),
                    (
                        json!("collet_profile_x_radius_mm"),
                        json!([
                            (json!([(json!(30.419383547820047)), (json!(5.549200000000031))])),
                            (json!([(json!(30.439383547820057)), (json!(5.486))])),
                            (json!([(json!(30.83938354782005)), (json!(5.305))])),
                            (json!([(json!(31.926100955818384)), (json!(5.255861473725293))]))
                        ]),
                    ),
                    (json!("nominal_tube_diameter_mm"), json!(6.35)),
                    (json!("tube_bore_display_diameter_mm"), json!(6.48)),
                    (json!("through_bore_display_diameter_mm"), json!(5.84)),
                    (json!("body_face_to_stop_display_mm"), json!(14.1)),
                    (
                        json!("captured_rotation"),
                        json!([
                            (json!([
                                (json!(0.9999006182304766)),
                                (u("-", json!(0.01341462891749083))),
                                (u("-", json!(0.004336057347023858)))
                            ])),
                            (json!([
                                (json!(0.013414502787343326)),
                                (json!(0.9999100198172864)),
                                (u("-", json!(5.8171834587589795e-05)))
                            ])),
                            (json!([
                                (json!(0.004336447541365958)),
                                (json!(0.0)),
                                (json!(0.9999905975671577))
                            ]))
                        ]),
                    ),
                    (
                        json!("captured_tip_origin_mm"),
                        json!([
                            (json!(75.82807977442403)),
                            (u("-", json!(0.24210931411608816))),
                            (json!(27.112817468003414))
                        ]),
                    ),
                    (
                        json!("scan_evidence_sha256"),
                        json!("9cecaf4a67a686bd0d3e359e17212f48c60dac4e0830dc77ca6e87b353f66ce7"),
                    ),
                ]),
            );
            e.insert(
                "STEM_D".into(),
                ix(g(&e, "PARAMETERS"), json!("nominal_stem_diameter_mm")),
            );
            e.insert(
                "STEM_LENGTH".into(),
                ix(
                    g(&e, "PARAMETERS"),
                    json!("nominal_free_stem_to_shoulder_mm"),
                ),
            );
            e.insert(
                "STEM_TIP_CHAMFER".into(),
                ix(g(&e, "PARAMETERS"), json!("stem_tip_chamfer_display_mm")),
            );
            e.insert(
                "TUBE_D".into(),
                ix(g(&e, "PARAMETERS"), json!("nominal_tube_diameter_mm")),
            );
            e.insert(
                "TUBE_BORE_D".into(),
                ix(g(&e, "PARAMETERS"), json!("tube_bore_display_diameter_mm")),
            );
            e.insert(
                "THROUGH_BORE_D".into(),
                ix(
                    g(&e, "PARAMETERS"),
                    json!("through_bore_display_diameter_mm"),
                ),
            );
            e.insert(
                "TUBE_STOP_DEPTH".into(),
                ix(g(&e, "PARAMETERS"), json!("body_face_to_stop_display_mm")),
            );
            e.insert(
                "BODY_D".into(),
                b(
                    "*",
                    json!(2),
                    builtin(
                        "max",
                        vec![{
                            let mut e = e.clone();
                            let mut temp1 = Vec::new();
                            for item in
                                seq(ix(g(&e, "PARAMETERS"), json!("body_profile_x_radius_mm")))
                            {
                                {
                                    let temp2 = item;
                                    e.insert("x".into(), ix(temp2.clone(), json!(0)));
                                    e.insert("r".into(), ix(temp2.clone(), json!(1)));
                                }
                                temp1.push(g(&e, "r"));
                            }
                            json!(temp1)
                        }],
                    ),
                ),
            );
            e.insert(
                "body_face_x".into(),
                ix(g(&e, "PARAMETERS"), json!("body_face_x_mm")),
            );
            e.insert("LENGTH".into(), ix(g(&e, "PARAMETERS"), json!("length_mm")));
            e.insert(
                "COLLET_PROUD".into(),
                b("-", g(&e, "LENGTH"), g(&e, "body_face_x")),
            );
            e.insert(
                "tube_stop_x".into(),
                b("-", g(&e, "body_face_x"), g(&e, "TUBE_STOP_DEPTH")),
            );
            e.insert(
                "TUBE_INSERTION_DEPTH".into(),
                b("-", g(&e, "LENGTH"), g(&e, "tube_stop_x")),
            );
            e.insert("stem_to_shoulder_x".into(), g(&e, "STEM_LENGTH"));
        }
        "kamoer_kphm400" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/kamoer-kphm400"));
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/kamoer-kphm400"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/kamoer-kphm400/kamoer_kphm400.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            {
                let temp1 = t(vec![
                    attr_value(g(&e, "pc"), "center_x"),
                    attr_value(g(&e, "pc"), "center_y"),
                ]);
                e.insert("cx".into(), ix(temp1.clone(), json!(0)));
                e.insert("cy".into(), ix(temp1.clone(), json!(1)));
            }
            e.insert("rear_axis_y_shift".into(), u("-", json!(1.0)));
            e.insert(
                "rear_axis_y".into(),
                b("+", g(&e, "cy"), g(&e, "rear_axis_y_shift")),
            );
            e.insert("base_plane_z".into(), json!(0.0));
            e.insert(
                "octagon_top_z".into(),
                attr_value(g(&e, "pc"), "bore_bottom_z"),
            );
            e.insert("outlet_above_skirt_bottom".into(), json!(0.0));
            e.insert(
                "arch_plane_z".into(),
                b(
                    "+",
                    attr_value(g(&e, "pc"), "skirt_bottom_z"),
                    g(&e, "outlet_above_skirt_bottom"),
                ),
            );
            e.insert("y_face".into(), attr_value(g(&e, "pc"), "pos_y_face_y"));
            e.insert("tube_casing_w".into(), json!(12.75));
            e.insert("shaft_w".into(), json!(13.0));
            e.insert("outlet_span_x".into(), json!(72.5));
            e.insert(
                "barb_pitch".into(),
                b("-", g(&e, "outlet_span_x"), g(&e, "tube_casing_w")),
            );
            e.insert(
                "outlet_open_span_x".into(),
                b("+", g(&e, "barb_pitch"), g(&e, "shaft_w")),
            );
            e.insert(
                "arch_xs".into(),
                t(vec![
                    b("-", g(&e, "cx"), b("/", g(&e, "barb_pitch"), json!(2.0))),
                    b("+", g(&e, "cx"), b("/", g(&e, "barb_pitch"), json!(2.0))),
                ]),
            );
            e.insert("skirt_depth".into(), json!(8.0));
            e.insert("head_front_below_skirt".into(), json!(41.15));
            e.insert("skirt_support_air".into(), json!(0.15));
            e.insert("skirt_y".into(), json!(62.5));
            e.insert("skirt_y_max".into(), json!(30.11));
            e.insert("skirt_y_plus_air".into(), json!(0.3));
            e.insert("skirt_upper_band".into(), json!(3.0));
            e.insert("skirt_body_y".into(), json!(54.0));
            e.insert("skirt_support_xy_air".into(), json!(0.15));
            e.insert("skirt_support_y_minus".into(), json!(5.0));
            e.insert("skirt_support_y_plus".into(), json!(3.482));
            e.insert(
                "skirt_body_y_max".into(),
                b(
                    "-",
                    b(
                        "-",
                        b("+", g(&e, "skirt_y_max"), g(&e, "skirt_y_plus_air")),
                        g(&e, "skirt_support_y_plus"),
                    ),
                    g(&e, "skirt_support_xy_air"),
                ),
            );
            e.insert(
                "skirt_body_y_min".into(),
                b("-", g(&e, "skirt_body_y_max"), g(&e, "skirt_body_y")),
            );
            e.insert("head_w".into(), json!(62.61));
            e.insert("head_depth".into(), json!(47.88));
            e.insert("motor_dia".into(), json!(35.73));
            e.insert("motor_reach".into(), json!(62.55));
            e.insert(
                "pump_len".into(),
                b("+", g(&e, "head_depth"), g(&e, "motor_reach")),
            );
            e.insert(
                "body_y_face".into(),
                b("+", g(&e, "cy"), b("/", g(&e, "head_w"), json!(2))),
            );
            e.insert("bracket_w".into(), g(&e, "head_w"));
            e.insert("bracket_t".into(), json!(0.0));
            e.insert("bracket_z".into(), g(&e, "base_plane_z"));
            e.insert("outlet_relief".into(), json!(2.075));
            e.insert("outlet_relief_top_z".into(), u("-", json!(36.295)));
            e.insert(
                "outlet_relief_run".into(),
                b("+", g(&e, "head_depth"), g(&e, "outlet_relief_top_z")),
            );
            e.insert(
                "head_front_z".into(),
                b("-", g(&e, "base_plane_z"), g(&e, "head_depth")),
            );
            e.insert(
                "motor_end_z".into(),
                b("+", g(&e, "base_plane_z"), g(&e, "motor_reach")),
            );
        }
        "meanwell_irm90" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/meanwell-irm90"));
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/meanwell-irm90"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/meanwell-irm90/meanwell_irm90.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("width".into(), json!(52.0));
            e.insert("length".into(), json!(109.0));
            e.insert("height".into(), json!(33.5));
            e.insert("ledge_h".into(), json!(6.7));
            e.insert("ledge_len".into(), json!(13.0));
            e.insert("hole_dia".into(), json!(3.5));
            e.insert("hole_dx".into(), b("/", json!(33.0), json!(2.0)));
            e.insert("hole_dy".into(), b("/", json!(98.0), json!(2.0)));
            e.insert("mass_g".into(), json!(219.0));
            e.insert("holes".into(), {
                let mut e = e.clone();
                let mut temp1 = Vec::new();
                for item in seq(t(vec![u("-", json!(1.0)), json!(1.0)])) {
                    e.insert("sx".into(), item);
                    for item in seq(t(vec![u("-", json!(1.0)), json!(1.0)])) {
                        e.insert("sy".into(), item);
                        temp1.push(t(vec![
                            b("*", g(&e, "sx"), g(&e, "hole_dx")),
                            b("*", g(&e, "sy"), g(&e, "hole_dy")),
                        ]));
                    }
                }
                json!(temp1)
            });
            e.insert("block_inset".into(), json!(6.0));
            e.insert("block_h".into(), json!(7.0));
            e.insert(
                "block_w".into(),
                object(vec![
                    (json!(1.0), json!(16.0)),
                    (u("-", json!(1.0)), json!(25.0)),
                ]),
            );
            e.insert("block_len".into(), json!(8.0));
            let parameters = parse_json(read_file(
                cx, b("/", g(&e, "HERE"), json!("replica-parameters.json")),
            )?)?;
            e.insert("terminal_interfaces".into(), ix(parameters, json!("terminal_interfaces")));
        }
        "mq6_gas_sensor" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/mq6-gas-sensor"));
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/mq6-gas-sensor"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/mq6-gas-sensor/mq6_gas_sensor.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            {
                let temp1 = t(vec![json!(32.0), json!(20.0), json!(1.6)]);
                e.insert("PCB_X".into(), ix(temp1.clone(), json!(0)));
                e.insert("PCB_Y".into(), ix(temp1.clone(), json!(1)));
                e.insert("PCB_T".into(), ix(temp1.clone(), json!(2)));
            }
            {
                let temp2 = t(vec![json!(19.0), json!(14.0)]);
                e.insert("CAN_D".into(), ix(temp2.clone(), json!(0)));
                e.insert("CAN_H".into(), ix(temp2.clone(), json!(1)));
            }
            e.insert("PIN_LEN".into(), json!(6.0));
            e.insert("PIN_SQ".into(), json!(0.64));
            e.insert("PIN_PITCH".into(), json!(2.54));
            e.insert("PIN_COUNT".into(), json!(4));
            e.insert("PIN_ROW_INSET".into(), json!(3.0));
        }
        "multiplex_asse1022" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/multiplex-asse1022"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/multiplex-asse1022"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/multiplex-asse1022/multiplex_asse1022.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("TOTAL_LENGTH".into(), json!(65.05));
            e.insert("INLET_LENGTH".into(), json!(12.7));
            e.insert("FLARE_LENGTH".into(), json!(15.85));
            e.insert(
                "BARREL_LENGTH".into(),
                b(
                    "-",
                    b("-", g(&e, "TOTAL_LENGTH"), g(&e, "INLET_LENGTH")),
                    g(&e, "FLARE_LENGTH"),
                ),
            );
            e.insert("BODY_CENTER_Z".into(), json!(27.45));
            e.insert("HEX_ACROSS_FLATS".into(), json!(28.65));
            e.insert("CAP_ACROSS_FLATS".into(), json!(28.73));
            e.insert("HEX_ACROSS_CORNERS".into(), json!(33.1));
            e.insert(
                "BODY_UNDERSIDE_Z".into(),
                b(
                    "-",
                    g(&e, "BODY_CENTER_Z"),
                    b("/", g(&e, "HEX_ACROSS_FLATS"), json!(2.0)),
                ),
            );
            e.insert("VENT_X".into(), json!(24.65));
            e.insert("VENT_Y".into(), json!(0.07));
            e.insert("VENT_D".into(), json!(7.7));
            e.insert("VENT_DROP".into(), g(&e, "BODY_UNDERSIDE_Z"));
            e.insert("VENT_INTO_BODY".into(), json!(0.4));
            e.insert("INLET_THREAD_D".into(), json!(17.7));
            e.insert("FLARE_THREAD_D".into(), json!(15.8));
            e.insert(
                "INLET_PROFILE".into(),
                t(vec![
                    t(vec![json!(0.0), json!(6.6)]),
                    t(vec![json!(0.4), json!(7.25)]),
                    t(vec![json!(1.0), json!(7.85)]),
                    t(vec![json!(1.6), json!(8.4)]),
                    t(vec![json!(11.7), json!(8.75)]),
                    t(vec![
                        g(&e, "INLET_LENGTH"),
                        b("/", g(&e, "INLET_THREAD_D"), json!(2)),
                    ]),
                ]),
            );
            e.insert(
                "COLLAR_PROFILE".into(),
                t(vec![
                    t(vec![json!(12.7), json!(11.65)]),
                    t(vec![json!(13.0), json!(12.2)]),
                    t(vec![json!(13.4), json!(12.6)]),
                    t(vec![json!(14.0), json!(12.9)]),
                    t(vec![json!(17.4), json!(12.9)]),
                    t(vec![json!(17.65), json!(13.0)]),
                    t(vec![json!(17.8), json!(13.45)]),
                ]),
            );
            e.insert(
                "BODY_PROFILE".into(),
                t(vec![
                    t(vec![json!(17.75), json!(12.95)]),
                    t(vec![json!(17.8), json!(14.7)]),
                    t(vec![json!(18.0), json!(15.8)]),
                    t(vec![json!(18.3), json!(16.17)]),
                    t(vec![json!(30.8), json!(16.17)]),
                    t(vec![json!(31.15), json!(16.1)]),
                    t(vec![json!(31.45), json!(15.6)]),
                    t(vec![json!(31.65), json!(14.5)]),
                    t(vec![json!(31.9), json!(14.2)]),
                    t(vec![json!(36.1), json!(14.22)]),
                ]),
            );
            e.insert(
                "CAP_PROFILE".into(),
                t(vec![
                    t(vec![json!(36.1), json!(14.22)]),
                    t(vec![json!(36.4), json!(14.4)]),
                    t(vec![json!(36.8), json!(15.0)]),
                    t(vec![json!(37.3), json!(15.9)]),
                    t(vec![json!(37.7), json!(16.55)]),
                    t(vec![json!(47.65), json!(16.55)]),
                    t(vec![json!(48.0), json!(16.3)]),
                    t(vec![json!(48.4), json!(15.7)]),
                    t(vec![json!(48.9), json!(14.9)]),
                    t(vec![json!(49.2), json!(14.3)]),
                ]),
            );
            e.insert(
                "FLARE_PROFILE".into(),
                t(vec![
                    t(vec![json!(49.2), json!(8.65)]),
                    t(vec![json!(49.5), json!(8.15)]),
                    t(vec![json!(49.9), b("/", g(&e, "FLARE_THREAD_D"), json!(2))]),
                    t(vec![json!(58.5), b("/", g(&e, "FLARE_THREAD_D"), json!(2))]),
                    t(vec![json!(59.1), json!(7.4)]),
                    t(vec![json!(59.7), json!(6.9)]),
                    t(vec![json!(62.4), json!(6.9)]),
                    t(vec![g(&e, "TOTAL_LENGTH"), json!(4.25)]),
                ]),
            );
            e.insert(
                "VENT_PROFILE".into(),
                t(vec![
                    t(vec![json!(0.0), json!(2.85)]),
                    t(vec![json!(0.25), json!(3.2)]),
                    t(vec![json!(0.6), json!(3.4)]),
                    t(vec![json!(1.3), json!(3.5)]),
                    t(vec![json!(2.4), json!(3.5)]),
                    t(vec![json!(3.1), json!(3.42)]),
                    t(vec![json!(4.2), json!(3.55)]),
                    t(vec![json!(5.4), json!(3.4)]),
                    t(vec![json!(6.5), json!(3.45)]),
                    t(vec![json!(7.5), json!(3.6)]),
                    t(vec![json!(8.4), json!(3.75)]),
                    t(vec![json!(8.95), b("/", g(&e, "VENT_D"), json!(2))]),
                ]),
            );
        }
        "neofit_achv44_check" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/neofit-achv44-check"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/neofit-achv44-check"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/neofit-achv44-check/neofit_achv44_check.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("NAME".into(), json!("neofit-achv44-check"));
            e.insert("TUBE_OD".into(), json!(6.35));
            e.insert("LENGTH".into(), json!(55.43160662774284));
            e.insert(
                "FAMILY_SOCKET_COLLAR_OD".into(),
                b("*", json!(0.61), json!(25.4)),
            );
            e.insert("SOCKET_INSERTION".into(), b("*", json!(0.665), json!(25.4)));
            e.insert("FLOW_BORE".into(), json!(4.24));
            e.insert("MAX_BODY_RADIUS".into(), json!(8.431478550423588));
            e.insert(
                "VENDOR_SCALE_MM".into(),
                b("/", g(&e, "FAMILY_SOCKET_COLLAR_OD"), json!(2.0)),
            );
            e.insert(
                "FIXED_PROFILE".into(),
                t(vec![
                    t(vec![json!(1.4918678819097033), json!(6.685769623082552)]),
                    t(vec![json!(2.1155012981638155), json!(7.773918561310365)]),
                    t(vec![json!(4.43650159122278), json!(8.431478550423588)]),
                    t(vec![json!(20.1931249738797), json!(8.431478550423588)]),
                    t(vec![json!(24.342417995807825), json!(7.715426633980778)]),
                    t(vec![json!(35.372597297220466), json!(7.715426633980778)]),
                    t(vec![json!(36.381257169432544), json!(6.7020875787197784)]),
                    t(vec![json!(37.27680945017563), json!(5.592155695691845)]),
                    t(vec![json!(39.05784542515604), json!(6.668577440316712)]),
                    t(vec![json!(39.62182603172706), json!(7.747)]),
                    t(vec![json!(41.50279771928595), json!(7.747)]),
                    t(vec![json!(41.50279771928595), json!(7.512193784122122)]),
                    t(vec![json!(43.02043604852694), json!(7.512193784122122)]),
                    t(vec![json!(43.02043604852694), json!(7.747)]),
                    t(vec![json!(51.022312542450955), json!(7.747)]),
                    t(vec![json!(51.022312542450955), json!(7.512193784122122)]),
                    t(vec![json!(51.36782764017353), json!(7.512193784122122)]),
                    t(vec![json!(51.36782764017353), json!(7.747)]),
                    t(vec![json!(53.88637759368245), json!(7.747)]),
                    t(vec![json!(54.55184555902435), json!(6.668577440316712)]),
                ]),
            );
            e.insert("COLLET_MAJOR_RADIUS".into(), json!(7.339657287797431));
            e.insert("COLLET_MINOR_RADIUS".into(), json!(5.847196129402403));
            e.insert("COLLET_LIP_LENGTH".into(), json!(0.7843799685783712));
            e.insert("COLLET_STEM_RADIUS".into(), json!(5.490659780048598));
            e.insert("COLLET_REACH".into(), json!(6.6315760979807745));
        }
        "neofit_acvus44_check" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/neofit-acvus44-check"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/neofit-acvus44-check"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/neofit-acvus44-check/neofit_acvus44_check.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("STEM_D".into(), json!(6.35));
            e.insert(
                "PROFILE".into(),
                t(vec![
                    t(vec![json!(0.0), json!(2.83062)]),
                    t(vec![json!(0.27949), json!(3.15484)]),
                    t(vec![json!(0.40449), json!(3.175)]),
                    t(vec![json!(0.90449), json!(3.175)]),
                    t(vec![json!(7.77949), json!(3.175)]),
                    t(vec![json!(8.15449), json!(3.16232)]),
                    t(vec![json!(8.52949), json!(3.00886)]),
                    t(vec![json!(8.77949), json!(2.99506)]),
                    t(vec![json!(10.02949), json!(3.175)]),
                    t(vec![json!(17.0), json!(3.175)]),
                    t(vec![json!(17.65449), json!(3.23247)]),
                    t(vec![json!(17.90449), json!(3.38674)]),
                    t(vec![json!(18.02949), json!(3.56799)]),
                    t(vec![json!(18.15449), json!(6.16171)]),
                    t(vec![json!(18.40449), json!(6.54923)]),
                    t(vec![json!(18.52949), json!(7.69027)]),
                    t(vec![json!(18.65449), json!(7.85511)]),
                    t(vec![json!(19.02949), json!(7.96635)]),
                    t(vec![json!(24.40449), json!(7.95844)]),
                    t(vec![json!(24.77949), json!(7.88006)]),
                    t(vec![json!(24.90449), json!(7.80932)]),
                    t(vec![json!(25.02949), json!(7.64961)]),
                    t(vec![json!(25.15449), json!(7.38235)]),
                    t(vec![json!(25.27949), json!(5.12092)]),
                    t(vec![json!(25.65449), json!(4.88934)]),
                    t(vec![json!(31.52949), json!(4.87047)]),
                    t(vec![json!(33.52949), json!(4.9357)]),
                    t(vec![json!(35.02949), json!(4.90125)]),
                    t(vec![json!(35.27949), json!(5.0098)]),
                    t(vec![json!(35.52949), json!(5.24616)]),
                    t(vec![json!(35.65449), json!(5.53062)]),
                    t(vec![json!(35.77949), json!(5.95805)]),
                    t(vec![json!(35.90449), json!(6.14981)]),
                    t(vec![json!(36.40449), json!(6.67839)]),
                    t(vec![json!(36.65449), json!(6.87179)]),
                    t(vec![json!(37.15449), json!(6.9992)]),
                    t(vec![json!(39.77949), json!(7.05706)]),
                    t(vec![json!(40.02949), json!(7.16171)]),
                    t(vec![json!(40.40449), json!(7.46785)]),
                    t(vec![json!(40.77949), json!(7.5948)]),
                    t(vec![json!(41.15449), json!(7.63918)]),
                    t(vec![json!(44.77949), json!(7.71604)]),
                    t(vec![json!(45.27949), json!(7.58796)]),
                    t(vec![json!(45.77949), json!(7.22239)]),
                    t(vec![json!(46.90449), json!(7.24716)]),
                    t(vec![json!(47.40449), json!(7.20526)]),
                    t(vec![json!(47.65449), json!(7.1137)]),
                    t(vec![json!(47.77949), json!(7.0014)]),
                    t(vec![json!(47.90449), json!(6.85042)]),
                    t(vec![json!(48.15449), json!(6.31601)]),
                    t(vec![json!(48.52949), json!(6.2125)]),
                    t(vec![json!(48.90449), json!(6.27323)]),
                    t(vec![json!(49.02949), json!(5.16382)]),
                    t(vec![json!(49.15449), json!(5.16382)]),
                    t(vec![json!(49.27949), json!(5.29114)]),
                    t(vec![json!(49.40449), json!(6.46237)]),
                    t(vec![json!(49.52949), json!(6.55167)]),
                    t(vec![json!(50.02949), json!(6.79878)]),
                    t(vec![json!(50.40449), json!(6.79541)]),
                    t(vec![json!(50.65449), json!(6.73775)]),
                    t(vec![json!(50.90449), json!(6.53016)]),
                    t(vec![json!(51.091994723978004), json!(6.45353)]),
                ]),
            );
            e.insert(
                "LENGTH".into(),
                ix(ix(g(&e, "PROFILE"), u("-", json!(1))), json!(0)),
            );
            e.insert("SHOULDER".into(), json!(18.20643880297786));
            e.insert("INSERTION".into(), json!(16.891));
            e.insert("SOCKET_D".into(), json!(6.5));
            e.insert("BORE_D".into(), json!(4.3));
        }
        "neofit_bulkhead" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/neofit-bulkhead"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/neofit-bulkhead"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/neofit-bulkhead/neofit_bulkhead.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("_IN".into(), json!(25.4));
            e.insert("TUBE_OD".into(), json!(6.35));
            e.insert("THREAD_D".into(), json!(17.0));
            e.insert("THREAD_PITCH".into(), json!(1.5));
            e.insert("OVERALL".into(), b("*", json!(1.346), g(&e, "_IN")));
            e.insert("FLANGE_AF".into(), b("*", json!(0.748), g(&e, "_IN")));
            e.insert("NUT_AF".into(), b("*", json!(0.827), g(&e, "_IN")));
            e.insert("TUBE_STOP_DEPTH".into(), b("*", json!(0.665), g(&e, "_IN")));
            e.insert("NOMINAL_OUTBOARD_REACH".into(), json!(16.891));
            e.insert("PANEL_THREAD".into(), b("*", json!(0.311), g(&e, "_IN")));
            e.insert("NUT_LEN".into(), b("*", json!(0.276), g(&e, "_IN")));
            e.insert("MASS_G".into(), json!(9.4));
            e.insert("PRESSURE_PSI_68F".into(), json!(290.0));
            e.insert("MAX_TORQUE_FTLB".into(), json!(1.1));
            e.insert("FLANGE_D".into(), {
                let argv = vec![g(&e, "FLANGE_AF")];
                let kwargs = json!({});
                call(cx, "neofit_bulkhead", "_corners", argv, kwargs, Some(&e))?
            });
            e.insert("NUT_D".into(), {
                let argv = vec![g(&e, "NUT_AF")];
                let kwargs = json!({});
                call(cx, "neofit_bulkhead", "_corners", argv, kwargs, Some(&e))?
            });
            e.insert("near_ring_face_y".into(), g(&e, "NOMINAL_OUTBOARD_REACH"));
            e.insert(
                "far_ring_face_y".into(),
                b("-", g(&e, "NOMINAL_OUTBOARD_REACH"), g(&e, "OVERALL")),
            );
            e.insert(
                "far_body_face_y".into(),
                u("-", b("+", g(&e, "PANEL_THREAD"), g(&e, "NUT_LEN"))),
            );
            e.insert("PROUD_LENGTH".into(), g(&e, "near_ring_face_y"));
        }
        "neofit_drain_bulkhead" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/neofit-drain-bulkhead"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/neofit-drain-bulkhead"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "PARAMETER_SNAPSHOT_SHA256".into(),
                json!("f3183e2bc9814537e9db2e2ab2b2855ce1b4055a7d83e6bb9b5947ea99e4c6e6"),
            );
            e.insert("PARAMETERS".into(),object(vec![(json!("units"),json!("mm")),(json!("material_id"),json!("HSM-0061")),(json!("panel_seat_local_x_mm"),u("-",json!(4.366836575879036))),(json!("outboard_mouth_local_x_mm"),u("-",json!(16.194239450616685))),(json!("inboard_mouth_local_x_mm"),json!(17.09425949942281)),(json!("overall_mm"),json!(33.2884989500395)),(json!("near_ring_face_y_mm"),json!(11.827402874737649)),(json!("far_ring_face_y_mm"),u("-",json!(21.461096075301846))),(json!("body_hex"),object(vec![(json!("across_flats_mm"),json!(17.104185173888958)),(json!("center_yz_mm"),json!([(u("-",json!(0.04768709067598976))),(u("-",json!(0.05612018401489432)))])),(json!("vertex_clock_degrees"),u("-",json!(2.4051501489046956)))])),(json!("body_hex_stop_local_x_mm"),u("-",json!(6.35))),(json!("nut_hex"),object(vec![(json!("across_flats_mm"),json!(18.003496010716436)),(json!("center_yz_mm"),json!([(u("-",json!(0.01158748418158394))),(u("-",json!(0.08839434533385554)))])),(json!("vertex_clock_degrees"),u("-",json!(5.014448978196818)))])),(json!("nut_hex_start_local_x_mm"),json!(2.9)),(json!("nut_axial_range_local_mm"),json!([(json!(1.1612581975635323)),(json!(7.968500093292667))])),(json!("captured_nut_gap_mm"),json!(5.528094773442568)),(json!("barrel_end_local_x_mm"),json!(10.75)),(json!("profiles"),object(vec![(json!("outboard"),json!([(json!([(u("-",json!(16.19424))),(json!(4.96158))])),(json!([(u("-",json!(16.13174))),(json!(4.96158))])),(json!([(u("-",json!(15.88174))),(json!(5.24215))])),(json!([(u("-",json!(15.75674))),(json!(5.31402))])),(json!([(u("-",json!(14.88174))),(json!(5.40967))])),(json!([(u("-",json!(14.75674))),(json!(5.51821))])),(json!([(u("-",json!(14.50674))),(json!(5.99143))])),(json!([(u("-",json!(14.38174))),(json!(6.14039))])),(json!([(u("-",json!(14.13174))),(json!(6.302))])),(json!([(u("-",json!(13.75674))),(json!(6.36745))])),(json!([(u("-",json!(12.38174))),(json!(6.31295))])),(json!([(u("-",json!(11.75674))),(json!(6.69304))])),(json!([(u("-",json!(11.13174))),(json!(6.77188))])),(json!([(u("-",json!(11.00674))),(json!(6.90072))])),(json!([(u("-",json!(10.75674))),(json!(6.90072))])),(json!([(u("-",json!(10.63174))),(json!(7.18068))])),(json!([(u("-",json!(10.50674))),(json!(7.28462))])),(json!([(u("-",json!(10.38174))),(json!(7.98927))])),(json!([(u("-",json!(10.25674))),(json!(8.35845))])),(json!([(u("-",json!(10.00674))),(json!(8.89807))])),(json!([(u("-",json!(9.75674))),(json!(9.34704))])),(json!([(u("-",json!(9.50674))),(json!(9.60895))])),(json!([(u("-",json!(9.38174))),(json!(9.66911))])),(json!([(u("-",json!(9.00674))),(json!(9.71024))])),(json!([(u("-",json!(7.25674))),(json!(9.6443))])),(json!([(u("-",json!(6.13174))),(json!(9.68507))])),(json!([(u("-",json!(6.00674))),(json!(9.74362))])),(json!([(u("-",json!(5.75674))),(json!(10.0493))])),(json!([(u("-",json!(5.63174))),(json!(10.14832))])),(json!([(u("-",json!(5.38174))),(json!(10.22951))])),(json!([(u("-",json!(4.75674))),(json!(10.17168))])),(json!([(u("-",json!(4.50674))),(json!(10.05211))])),(json!([(u("-",json!(4.36684))),(json!(9.90899))]))])),(json!("inboard"),json!([(json!([(json!(10.75)),(json!(7.1135))])),(json!([(json!(10.8125)),(json!(7.1135))])),(json!([(json!(11.4375)),(json!(6.59594))])),(json!([(json!(11.8125)),(json!(6.45312))])),(json!([(json!(13.1875)),(json!(6.2739))])),(json!([(json!(14.4375)),(json!(6.28671))])),(json!([(json!(14.9375)),(json!(6.22282))])),(json!([(json!(15.1875)),(json!(6.11181))])),(json!([(json!(15.3125)),(json!(5.9947))])),(json!([(json!(15.4375)),(json!(5.78421))])),(json!([(json!(15.5625)),(json!(5.40208))])),(json!([(json!(15.6875)),(json!(5.16172))])),(json!([(json!(16.5625)),(json!(5.00578))])),(json!([(json!(16.8125)),(json!(4.83622))])),(json!([(json!(17.09426)),(json!(4.76881))]))])),(json!("nut"),json!([(json!([(json!(1.16126)),(json!(10.03375))])),(json!([(json!(1.72376)),(json!(10.12894))])),(json!([(json!(3.22376)),(json!(9.99822))])),(json!([(json!(4.47376)),(json!(9.98225))])),(json!([(json!(6.72376)),(json!(10.07864))])),(json!([(json!(7.22376)),(json!(9.88391))])),(json!([(json!(7.59876)),(json!(9.5566))])),(json!([(json!(7.84876)),(json!(9.21939))])),(json!([(json!(7.9685)),(json!(9.21939))]))]))])),(json!("profile_method"),json!("97.5th percentile outward-facing radius in 0.125 mm axial bins; three-bin median; 0.035 mm radial simplification.")),(json!("published"),object(vec![(json!("tube_od_mm"),json!(4.0)),(json!("thread_diameter_mm"),json!(15.0)),(json!("thread_pitch_mm"),json!(1.5)),(json!("overall_mm"),json!(32.4)),(json!("bare_panel_span_mm"),json!(8.1)),(json!("nut_length_mm"),json!(6.5)),(json!("body_hex_af_mm"),json!(17.0)),(json!("nut_hex_af_mm"),json!(18.0)),(json!("tube_stop_depth_mm"),json!(14.7))])),(json!("scan_evidence_sha256"),json!("6365e533b0f0ce29ff06607c17b90a0ad06f1f768dbc4b12d056d1c467757577"))]));
            e.insert(
                "TUBE_OD".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("published")),
                    json!("tube_od_mm"),
                ),
            );
            e.insert(
                "THREAD_D".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("published")),
                    json!("thread_diameter_mm"),
                ),
            );
            e.insert(
                "THREAD_PITCH".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("published")),
                    json!("thread_pitch_mm"),
                ),
            );
            e.insert(
                "PANEL_THREAD".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("published")),
                    json!("bare_panel_span_mm"),
                ),
            );
            e.insert(
                "NUT_LEN".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("published")),
                    json!("nut_length_mm"),
                ),
            );
            e.insert(
                "TUBE_STOP_DEPTH".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("published")),
                    json!("tube_stop_depth_mm"),
                ),
            );
            e.insert(
                "OVERALL".into(),
                ix(g(&e, "PARAMETERS"), json!("overall_mm")),
            );
            e.insert(
                "FLANGE_AF".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("body_hex")),
                    json!("across_flats_mm"),
                ),
            );
            e.insert(
                "NUT_AF".into(),
                ix(
                    ix(g(&e, "PARAMETERS"), json!("nut_hex")),
                    json!("across_flats_mm"),
                ),
            );
            e.insert(
                "FLANGE_D".into(),
                b(
                    "*",
                    json!(2),
                    builtin(
                        "max",
                        vec![{
                            let mut e = e.clone();
                            let mut temp1 = Vec::new();
                            for item in seq(ix(
                                ix(g(&e, "PARAMETERS"), json!("profiles")),
                                json!("outboard"),
                            )) {
                                {
                                    let temp2 = item;
                                    e.insert("x".into(), ix(temp2.clone(), json!(0)));
                                    e.insert("r".into(), ix(temp2.clone(), json!(1)));
                                }
                                temp1.push(g(&e, "r"));
                            }
                            json!(temp1)
                        }],
                    ),
                ),
            );
            e.insert(
                "NUT_D".into(),
                b(
                    "*",
                    json!(2),
                    builtin(
                        "max",
                        vec![{
                            let mut e = e.clone();
                            let mut temp3 = Vec::new();
                            for item in
                                seq(ix(ix(g(&e, "PARAMETERS"), json!("profiles")), json!("nut")))
                            {
                                {
                                    let temp4 = item;
                                    e.insert("x".into(), ix(temp4.clone(), json!(0)));
                                    e.insert("r".into(), ix(temp4.clone(), json!(1)));
                                }
                                temp3.push(g(&e, "r"));
                            }
                            json!(temp3)
                        }],
                    ),
                ),
            );
            e.insert(
                "near_ring_face_y".into(),
                ix(g(&e, "PARAMETERS"), json!("near_ring_face_y_mm")),
            );
            e.insert(
                "far_ring_face_y".into(),
                ix(g(&e, "PARAMETERS"), json!("far_ring_face_y_mm")),
            );
            e.insert(
                "far_body_face_y".into(),
                b(
                    "-",
                    ix(g(&e, "PARAMETERS"), json!("panel_seat_local_x_mm")),
                    ix(g(&e, "PARAMETERS"), json!("barrel_end_local_x_mm")),
                ),
            );
            e.insert("PROUD_LENGTH".into(), g(&e, "near_ring_face_y"));
        }
        "neofit_flavor_reducer" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/neofit-flavor-reducer"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/neofit-flavor-reducer"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/neofit-flavor-reducer/neofit_flavor_reducer.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("STEM_OD".into(), json!(6.35));
            e.insert("TUBE_OD".into(), json!(4.0));
            e.insert("BODY_D".into(), b("*", json!(0.52), json!(25.4)));
            e.insert("OVERALL".into(), b("*", json!(1.445), json!(25.4)));
            e.insert("STEM_LENGTH".into(), b("*", json!(0.827), json!(25.4)));
            e.insert(
                "PROUD_LENGTH".into(),
                b("-", g(&e, "OVERALL"), g(&e, "STEM_LENGTH")),
            );
        }
        "neofit_stem_elbow" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/neofit-stem-elbow"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/neofit-stem-elbow"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/neofit-stem-elbow/neofit_stem_elbow.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "PARAMETER_SNAPSHOT_SHA256".into(),
                json!("84973fc2472c7af9c8b961dd57016219ef8a321611841fc5e919aec2bd18ce9c"),
            );
            e.insert(
                "PARAMETERS".into(),
                object(vec![
                    (json!("units"), json!("mm")),
                    (json!("material_id"), json!("HSM-0330")),
                    (json!("tube_od_mm"), json!(6.35)),
                    (json!("stem_od_mm"), json!(6.35)),
                    (json!("stem_tip_x_mm"), u("-", json!(27.02535353479422))),
                    (
                        json!("stem_shoulder_x_mm"),
                        u("-", json!(6.113547528963171)),
                    ),
                    (json!("socket_mouth_y_mm"), json!(21.082366093950743)),
                    (json!("stem_length_mm"), json!(20.91180600583105)),
                    (json!("flow_bore_display_mm"), json!(4.3)),
                    (json!("published_socket_insertion_mm"), json!(16.891)),
                    (json!("fixed_nose_y_mm"), json!(19.0)),
                    (json!("collet_start_y_mm"), json!(19.08)),
                    (json!("bend_radius_mm"), json!(5.066279836802499)),
                    (
                        json!("collet_ellipse"),
                        object(vec![
                            (
                                json!("center_xz_mm"),
                                json!([
                                    (u("-", json!(0.06848629126006257))),
                                    (u("-", json!(0.05282793793301456)))
                                ]),
                            ),
                            (json!("angle_radians"), json!(0.297310387790615)),
                            (json!("minor_major_ratio"), json!(0.8413251285872266)),
                        ]),
                    ),
                    (
                        json!("profiles"),
                        object(vec![
                            (
                                json!("fixed_body_y"),
                                json!([
                                    (json!([(json!(0.0)), (json!(5.11019))])),
                                    (json!([(json!(4.95)), (json!(5.09439))])),
                                    (json!([(json!(5.35)), (json!(5.13339))])),
                                    (json!([(json!(5.45)), (json!(5.21773))])),
                                    (json!([(json!(5.55)), (json!(5.42916))])),
                                    (json!([(json!(5.65)), (json!(6.26253))])),
                                    (json!([(json!(5.75)), (json!(6.53757))])),
                                    (json!([(json!(5.95)), (json!(6.83879))])),
                                    (json!([(json!(6.25)), (json!(7.10216))])),
                                    (json!([(json!(6.65)), (json!(7.24498))])),
                                    (json!([(json!(7.95)), (json!(7.30081))])),
                                    (json!([(json!(8.55)), (json!(7.71255))])),
                                    (json!([(json!(9.05)), (json!(7.83786))])),
                                    (json!([(json!(14.95)), (json!(7.89743))])),
                                    (json!([(json!(15.65)), (json!(7.86289))])),
                                    (json!([(json!(15.95)), (json!(7.72594))])),
                                    (json!([(json!(16.25)), (json!(7.45757))])),
                                    (json!([(json!(16.45)), (json!(7.35603))])),
                                    (json!([(json!(16.75)), (json!(7.30671))])),
                                    (json!([(json!(17.95)), (json!(7.28925))])),
                                    (json!([(json!(18.45)), (json!(7.07686))])),
                                    (json!([(json!(18.65)), (json!(6.87668))])),
                                    (json!([(json!(18.85)), (json!(6.34219))])),
                                    (json!([(json!(18.95)), (json!(5.74134))])),
                                    (json!([(json!(19.0)), (json!(5.74134))]))
                                ]),
                            ),
                            (
                                json!("release_collet_y"),
                                json!([
                                    (json!([(json!(19.08)), (json!(6.08151))])),
                                    (json!([(json!(19.33)), (json!(6.11464))])),
                                    (json!([(json!(19.83)), (json!(5.93075))])),
                                    (json!([(json!(20.63)), (json!(5.85555))])),
                                    (json!([(json!(21.08237)), (json!(5.72046))]))
                                ]),
                            ),
                            (
                                json!("stem_x"),
                                json!([
                                    (json!([(u("-", json!(27.02535))), (json!(3.0))])),
                                    (json!([(u("-", json!(26.80535))), (json!(3.175))])),
                                    (json!([(u("-", json!(6.25355))), (json!(3.175))])),
                                    (json!([(u("-", json!(6.13355))), (json!(4.75))])),
                                    (json!([(u("-", json!(6.07535))), (json!(4.76682))])),
                                    (json!([(u("-", json!(5.97535))), (json!(4.91636))])),
                                    (json!([(u("-", json!(5.8))), (json!(4.99467))])),
                                    (json!([(u("-", json!(5.5))), (json!(5.08))])),
                                    (json!([(json!(0.0)), (json!(5.08))]))
                                ]),
                            ),
                        ]),
                    ),
                    (
                        json!("scan_evidence_sha256"),
                        json!("e04699c3d443b69e31c1c4e9f0864ce6c365c6055f804d188d2bb86f16b567a3"),
                    ),
                ]),
            );
            e.insert(
                "TUBE_OD".into(),
                ix(g(&e, "PARAMETERS"), json!("tube_od_mm")),
            );
            e.insert(
                "STEM_OD".into(),
                ix(g(&e, "PARAMETERS"), json!("stem_od_mm")),
            );
            e.insert(
                "STEM_TIP_REACH".into(),
                u("-", ix(g(&e, "PARAMETERS"), json!("stem_tip_x_mm"))),
            );
            e.insert(
                "HUB_BACK_REACH".into(),
                u("-", ix(g(&e, "PARAMETERS"), json!("stem_shoulder_x_mm"))),
            );
            e.insert(
                "STEM_LENGTH".into(),
                ix(g(&e, "PARAMETERS"), json!("stem_length_mm")),
            );
            e.insert(
                "SOCKET_MOUTH_REACH".into(),
                ix(g(&e, "PARAMETERS"), json!("socket_mouth_y_mm")),
            );
            e.insert(
                "SOCKET_INSERTION".into(),
                ix(g(&e, "PARAMETERS"), json!("published_socket_insertion_mm")),
            );
            e.insert(
                "COLLAR_OD".into(),
                b(
                    "*",
                    json!(2),
                    builtin(
                        "max",
                        vec![{
                            let mut e = e.clone();
                            let mut temp1 = Vec::new();
                            for item in seq(ix(
                                ix(g(&e, "PARAMETERS"), json!("profiles")),
                                json!("fixed_body_y"),
                            )) {
                                {
                                    let temp2 = item;
                                    e.insert("y".into(), ix(temp2.clone(), json!(0)));
                                    e.insert("r".into(), ix(temp2.clone(), json!(1)));
                                }
                                temp1.push(g(&e, "r"));
                            }
                            json!(temp1)
                        }],
                    ),
                ),
            );
            e.insert(
                "OVERALL_STEM_AXIS".into(),
                b(
                    "+",
                    g(&e, "STEM_TIP_REACH"),
                    b("/", g(&e, "COLLAR_OD"), json!(2)),
                ),
            );
            e.insert(
                "OVERALL_SOCKET_AXIS".into(),
                b(
                    "+",
                    g(&e, "SOCKET_MOUTH_REACH"),
                    ix(g(&e, "PARAMETERS"), json!("bend_radius_mm")),
                ),
            );
            e.insert(
                "FLOW_BORE".into(),
                ix(g(&e, "PARAMETERS"), json!("flow_bore_display_mm")),
            );
        }
        "pump_barb_joint" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/pump-barb-joint"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/pump-barb-joint"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/pump-barb-joint/pump_barb_joint.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "PORTS".into(),
                object(vec![
                    (json!("suction"), json!("port_yminus")),
                    (json!("discharge"), json!("port_yplus")),
                ]),
            );
            e.insert("TUBE_ID".into(), json!(9.525));
            e.insert("TUBE_OD".into(), json!(15.088));
            e.insert("TUBE_ROOT_SETBACK".into(), json!(0.9));
            e.insert("TRIM".into(), json!(10.0));
            e.insert(
                "CUT_X".into(),
                b("-", attr(cx, "jg_pp061208w", "STEM_LENGTH")?, g(&e, "TRIM")),
            );
            e.insert("RANGE".into(), t(vec![json!(10.0), json!(16.0)]));
            e.insert("BAND_W".into(), json!(9.0));
            e.insert("BAND_T".into(), json!(0.6));
            e.insert("HOUSING_L".into(), json!(13.0));
            e.insert("HOUSING_W".into(), json!(10.0));
            e.insert("HOUSING_H".into(), json!(7.0));
            {
                let temp1 = t(vec![json!(6.0), json!(3.0)]);
                e.insert("NECK_D".into(), ix(temp1.clone(), json!(0)));
                e.insert("NECK_L".into(), ix(temp1.clone(), json!(1)));
            }
            e.insert("KEY_L".into(), json!(27.0));
            {
                let temp2 = t(vec![json!(8.0), json!(26.0)]);
                e.insert("KEY_NECK_W".into(), ix(temp2.clone(), json!(0)));
                e.insert("KEY_W".into(), ix(temp2.clone(), json!(1)));
            }
            e.insert("KEY_T".into(), json!(5.0));
        }
        "riteav_keystone" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/riteav-keystone"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/riteav-keystone"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/riteav-keystone/riteav_keystone.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("FACE_W".into(), json!(14.5));
            e.insert("FACE_H".into(), json!(16.0));
            e.insert("APERTURE_W".into(), json!(14.9));
            e.insert("APERTURE_H".into(), json!(16.3));
            e.insert("LIP_D".into(), json!(3.0));
            e.insert("POCKET_W".into(), json!(14.9));
            e.insert("POCKET_H".into(), json!(24.4));
            e.insert("POCKET_RISE".into(), json!(1.67));
            e.insert("DEPTH".into(), json!(9.7));
            e.insert("EASE_DEG".into(), json!(50.0));
            e.insert("CATCH_UPPER".into(), t(vec![json!(2.0), json!(1.4)]));
            e.insert("CATCH_LOWER".into(), t(vec![json!(2.6), json!(1.3)]));
            e.insert("RECEPTACLE_WALL".into(), json!(3.0));
            e.insert("BODY_DEPTH".into(), json!(30.0));
            e.insert("PORT_W".into(), json!(9.5));
            e.insert("PORT_H".into(), json!(7.6));
            e.insert("PORT_DEPTH".into(), json!(8.0));
            e.insert("LATCH_SLOT_W".into(), json!(3.4));
            e.insert("LATCH_SLOT_H".into(), json!(3.6));
            e.insert("FIT_SLIP".into(), json!(0.25));
        }
        "seaflo_discharge_chain" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/seaflo-discharge-chain"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/seaflo-discharge-chain"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/seaflo-discharge-chain/seaflo_discharge_chain.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("NPT_ENGAGE".into(), json!(11.0));
            {
                let temp1 = t(vec![json!(15.0), json!(8.0)]);
                e.insert("JG_SOCKET_D".into(), ix(temp1.clone(), json!(0)));
                e.insert("JG_SOCKET_L".into(), ix(temp1.clone(), json!(1)));
            }
            {
                let temp2 = t(vec![json!(16.5), json!(5.0)]);
                e.insert("JG_HEX".into(), ix(temp2.clone(), json!(0)));
                e.insert("JG_HEX_L".into(), ix(temp2.clone(), json!(1)));
            }
            {
                let temp3 = t(vec![json!(14.0), json!(13.0)]);
                e.insert("JG_COLLET_D".into(), ix(temp3.clone(), json!(0)));
                e.insert("JG_COLLET_L".into(), ix(temp3.clone(), json!(1)));
            }
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert(
                "SECTIONS".into(),
                t(seq({
                    let mut e = e.clone();
                    let mut temp4 = Vec::new();
                    for item in seq(t(vec![
                        t(vec![
                            json!("PP010822E collet"),
                            attr(cx, "jg_pp010822e", "COLLET_D")?,
                            attr(cx, "jg_pp010822e", "COLLET_LENGTH")?,
                        ]),
                        t(vec![
                            json!("PP010822E hex"),
                            attr(cx, "jg_pp010822e", "HEX_ACROSS_CORNERS")?,
                            attr(cx, "jg_pp010822e", "HEX_LENGTH")?,
                        ]),
                        t(vec![
                            json!("PP010822E NPT"),
                            attr(cx, "jg_pp010822e", "SHANK_D")?,
                            b(
                                "-",
                                attr(cx, "jg_pp010822e", "SHANK_LENGTH")?,
                                g(&e, "NPT_ENGAGE"),
                            ),
                        ]),
                        t(vec![
                            json!("GASHER socket"),
                            attr(cx, "gasher_check_valve", "SOCKET_D")?,
                            attr(cx, "gasher_check_valve", "SOCKET_LENGTH")?,
                        ]),
                        t(vec![
                            json!("GASHER hex"),
                            attr(cx, "gasher_check_valve", "HEX_ACROSS_CORNERS")?,
                            attr(cx, "gasher_check_valve", "HEX_LENGTH")?,
                        ]),
                        t(vec![
                            json!("GASHER stub"),
                            attr(cx, "gasher_check_valve", "THREAD_D")?,
                            b(
                                "-",
                                attr(cx, "gasher_check_valve", "STUB_LENGTH")?,
                                g(&e, "NPT_ENGAGE"),
                            ),
                        ]),
                        t(vec![
                            json!("PP450822E socket"),
                            g(&e, "JG_SOCKET_D"),
                            g(&e, "JG_SOCKET_L"),
                        ]),
                        t(vec![
                            json!("PP450822E hex"),
                            g(&e, "JG_HEX"),
                            g(&e, "JG_HEX_L"),
                        ]),
                        t(vec![
                            json!("PP450822E collet"),
                            g(&e, "JG_COLLET_D"),
                            g(&e, "JG_COLLET_L"),
                        ]),
                    ])) {
                        e.insert("row".into(), item);
                        if truth(&json!(compare(">", ix(g(&e, "row"), json!(2)), json!(0.0)))) {
                            temp4.push(g(&e, "row"));
                        }
                    }
                    json!(temp4)
                })),
            );
            e.insert(
                "LENGTH".into(),
                builtin(
                    "sum",
                    vec![{
                        let mut e = e.clone();
                        let mut temp5 = Vec::new();
                        for item in seq(g(&e, "SECTIONS")) {
                            {
                                let temp6 = item;
                                e.insert("_label".into(), ix(temp6.clone(), json!(0)));
                                e.insert("_dia".into(), ix(temp6.clone(), json!(1)));
                                e.insert("length".into(), ix(temp6.clone(), json!(2)));
                            }
                            temp5.push(g(&e, "length"));
                        }
                        json!(temp5)
                    }],
                ),
            );
        }
        "sf76e_thermal_fuse" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/sf76e-thermal-fuse"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/sf76e-thermal-fuse"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/sf76e-thermal-fuse/sf76e_thermal_fuse.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("BODY_D".into(), json!(4.2));
            e.insert("BODY_L".into(), json!(11.0));
            e.insert("LEAD_D".into(), json!(1.0));
            e.insert("LEAD_STUB".into(), json!(3.0));
            e.insert("LEAD_SHORT".into(), json!(20.0));
            e.insert("LEAD_LONG".into(), json!(35.0));
            e.insert("OVERALL_L".into(), json!(66.0));
            e.insert("TF_C".into(), json!(77));
            e.insert("TH_C".into(), json!(62));
            e.insert("TM_C".into(), json!(150));
            e.insert("RATED_A".into(), json!(10));
            e.insert("RATED_V".into(), json!(250));
            e.insert(
                "LENGTH".into(),
                b("+", g(&e, "BODY_L"), b("*", json!(2.0), g(&e, "LEAD_STUB"))),
            );
            e.insert("AXIS_Z".into(), b("/", g(&e, "BODY_D"), json!(2.0)));
            e.insert(
                "LEAD_STANDOFF".into(),
                b("-", g(&e, "AXIS_Z"), b("/", g(&e, "LEAD_D"), json!(2.0))),
            );
        }
        "shok_blok_regulator" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/shok-blok-regulator"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/shok-blok-regulator"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/shok-blok-regulator/shok_blok_regulator.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert("LENGTH".into(), json!(101.6));
            e.insert(
                "SECTIONS".into(),
                t(vec![
                    t(vec![json!("inlet collet"), json!(11.4), json!(4.3)]),
                    t(vec![json!("inlet socket"), json!(17.8), json!(13.0)]),
                    t(vec![json!("inlet hex"), json!(24.5), json!(6.2)]),
                    t(vec![json!("shoulder"), json!(29.3), json!(4.1)]),
                    t(vec![json!("label band"), json!(30.3), json!(21.1)]),
                    t(vec![json!("body ring"), json!(34.3), json!(19.2)]),
                    t(vec![json!("outlet hex"), json!(21.7), json!(8.5)]),
                    t(vec![json!("outlet socket"), json!(18.4), json!(21.6)]),
                    t(vec![json!("outlet collet"), json!(11.4), json!(3.6)]),
                ]),
            );
        }
        "taprite_3741_regulator" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/taprite-3741-regulator"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/taprite-3741-regulator"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("FACTORY_SET_PSI".into(), json!(75.0));
            e.insert("RELIEF_PSI".into(), json!(130.0));
            e.insert("CGA320_NUT_FLATS".into(), b("*", json!(25.4), json!(1.125)));
            e.insert("CGA320_THREAD_D".into(), b("*", json!(25.4), json!(0.825)));
            e.insert("CGA320_NUT_LENGTH".into(), json!(25.4));
            e.insert("CGA320_NIPPLE_D".into(), json!(15.9));
            e.insert("PTC_COLLET_D".into(), json!(14.0));
            e.insert("PTC_COLLET_LENGTH".into(), json!(13.5));
            e.insert("PTC_HEX_ACROSS_CORNERS".into(), json!(16.5));
            e.insert("PTC_HEX_LENGTH".into(), json!(5.0));
            e.insert("NPT_D".into(), json!(13.7));
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert("DIAL_D".into(), json!(51.0));
            e.insert("WINDOW_D".into(), json!(48.5));
            e.insert("CASE_D".into(), json!(58.5));
            e.insert("CASE_DEPTH".into(), json!(28.0));
            e.insert("GAUGE_FACE_Y".into(), json!(14.0));
            e.insert("BEZEL_PROUD".into(), json!(3.0));
            e.insert("OUTLET_REACH".into(), json!(67.0));
            e.insert("TANK_REACH".into(), json!(65.0));
            e.insert("GAUGE_STEM_D".into(), json!(13.7));
            e.insert("GAUGE_BLOCK_W".into(), json!(14.0));
            e.insert("GAUGE_BLOCK_LENGTH".into(), json!(9.0));
            e.insert("BODY_D".into(), json!(44.0));
            e.insert("BODY_BACK_Y".into(), u("-", json!(11.0)));
            e.insert("BODY_FRONT_Y".into(), json!(13.5));
            e.insert("PORT_BOSS_D".into(), json!(18.0));
            e.insert("PORT_FACE_R".into(), json!(23.0));
            e.insert("FLANGE_D".into(), json!(50.0));
            e.insert("FLANGE_FRONT_Y".into(), json!(25.4));
            e.insert("FLANGE_EDGE_R".into(), json!(2.0));
            e.insert("NECK_FLATS".into(), json!(31.0));
            e.insert("NECK_FRONT_Y".into(), json!(39.0));
            e.insert("NOSE_D".into(), json!(29.0));
            e.insert("NOSE_FRONT_Y".into(), json!(62.3));
            e.insert("NOSE_CHAMFER".into(), json!(2.0));
            e.insert("JAM_NUT_FLATS".into(), b("*", json!(25.4), json!(0.5)));
            e.insert("JAM_NUT_FRONT_Y".into(), json!(70.0));
            e.insert("SCREW_D".into(), b("*", json!(25.4), json!(0.375)));
            e.insert("SCREW_TIP_Y".into(), json!(92.3));
            e.insert("SLOT_W".into(), json!(1.6));
            e.insert("SLOT_DEPTH".into(), json!(3.0));
            e.insert(
                "INLET_AXIS".into(),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            );
            e.insert(
                "TANK_AXIS".into(),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            );
            e.insert("INLET_NIPPLE_D".into(), json!(14.0));
            e.insert("INLET_NUT_NEAR".into(), json!(60.0));
            e.insert(
                "INLET_NUT_FACE".into(),
                b("+", g(&e, "INLET_NUT_NEAR"), g(&e, "CGA320_NUT_LENGTH")),
            );
            e.insert(
                "INLET_NIPPLE_END".into(),
                b("-", g(&e, "INLET_NUT_FACE"), json!(9.0)),
            );
            e.insert(
                "OUTLET_THREAD_Z".into(),
                b("-", u("-", g(&e, "PORT_FACE_R")), json!(1.0)),
            );
            e.insert(
                "OUTLET_HEX_Z".into(),
                b("-", g(&e, "OUTLET_THREAD_Z"), g(&e, "PTC_HEX_LENGTH")),
            );
            e.insert(
                "OUTLET_MOUTH_Z".into(),
                b("-", g(&e, "OUTLET_HEX_Z"), g(&e, "PTC_COLLET_LENGTH")),
            );
            e.insert("BLOWOFF_BEARING_DEG".into(), json!(135.0));
            e.insert("BLOWOFF_ROOT_R".into(), json!(18.0));
            e.insert("BLOWOFF_BODY_D".into(), json!(11.0));
            e.insert("BLOWOFF_BODY_R".into(), json!(30.0));
            e.insert("BLOWOFF_CAP_D".into(), json!(13.0));
            e.insert("BLOWOFF_CAP_R".into(), json!(37.0));
            e.insert("BLOWOFF_VENT_D".into(), json!(1.6));
            e.insert("DIAL_ZERO_DEG".into(), json!(225.0));
            e.insert("DIAL_SWEEP_DEG".into(), json!(270.0));
            e.insert("TANK_FULL_PSI".into(), json!(2000.0));
            e.insert("OUTLET_FULL_PSI".into(), json!(160.0));
            e.insert(
                "OUTLET_DIAL".into(),
                object(vec![
                    (json!("outer"), {
                        let argv = vec![
                            g(&e, "OUTLET_FULL_PSI"),
                            json!(20.0),
                            json!(5.0),
                            t(vec![
                                json!(20),
                                json!(40),
                                json!(60),
                                json!(80),
                                json!(100),
                                json!(120),
                                json!(140),
                                json!(160),
                            ]),
                        ];
                        let kwargs = json!({});
                        call(
                            cx,
                            "taprite_3741_regulator",
                            "_ring_spec",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    }),
                    (json!("inner"), {
                        let argv = vec![
                            b("/", g(&e, "OUTLET_FULL_PSI"), json!(14.5038)),
                            json!(2.0),
                            json!(1.0),
                            t(vec![json!(2), json!(4), json!(6), json!(8), json!(10)]),
                        ];
                        let kwargs = json!({});
                        call(
                            cx,
                            "taprite_3741_regulator",
                            "_ring_spec",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    }),
                    (json!("units"), t(vec![json!("psi"), json!("bar")])),
                    (json!("stamp"), json!("TAPRITE")),
                    (json!("bands"), t(vec![])),
                ]),
            );
            e.insert("OUTER_NUMERAL_R".into(), json!(20.6));
            e.insert("OUTER_TICK_OUT_R".into(), json!(23.6));
            e.insert("OUTER_TICK_MAJOR_R".into(), b("+", json!(20.0), json!(2.2)));
            e.insert("OUTER_TICK_MINOR_R".into(), json!(22.4));
            e.insert("INNER_ARC_R".into(), json!(14.6));
            e.insert("INNER_TICK_MAJOR_R".into(), json!(12.2));
            e.insert("INNER_TICK_MINOR_R".into(), json!(13.3));
            e.insert("INNER_NUMERAL_R".into(), json!(10.3));
            e.insert("UNIT_UPPER_R".into(), json!(6.9));
            e.insert("UNIT_LOWER_R".into(), json!(10.2));
            e.insert("STAMP_R".into(), json!(5.2));
            e.insert("NUMERAL_SIZE".into(), json!(3.0));
            e.insert("STAMP_SIZE".into(), json!(2.4));
            e.insert("UNIT_SIZE".into(), json!(2.8));
            e.insert("MAJOR_TICK_W".into(), json!(0.8));
            e.insert("MINOR_TICK_W".into(), json!(0.45));
            e.insert("PRINT_T".into(), json!(0.6));
            e.insert("BAND_T".into(), json!(0.25));
            e.insert("NEEDLE_R".into(), json!(19.0));
            e.insert("NEEDLE_TAIL_R".into(), json!(4.6));
            e.insert("NEEDLE_W".into(), json!(1.3));
            e.insert("HUB_DIAL_D".into(), json!(4.6));
            e.insert("BAND_NEAR_R".into(), json!(16.0));
            e.insert("BAND_FAR_R".into(), json!(23.6));
        }
        "tee_connector" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/tee-connector"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/tee-connector"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/tee-connector/tee_connector.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "BRANCH_MEASUREMENTS".into(),
                b(
                    "/",
                    g(&e, "_hw"),
                    json!("reference/jg-pp0208e-tee/branch-operating-measurements.json"),
                ),
            );
            e.insert(
                "_branch".into(),
                parse_json(read_file(cx, g(&e, "BRANCH_MEASUREMENTS"))?)?,
            );
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert("RUN_SPAN".into(), json!(42.5));
            e.insert("RUN_SPAN_PRESSED".into(), json!(39.2));
            e.insert("RUN_HALF".into(), b("/", g(&e, "RUN_SPAN"), json!(2.0)));
            e.insert(
                "RUN_COLLET_TRAVEL".into(),
                b(
                    "/",
                    b("-", g(&e, "RUN_SPAN"), g(&e, "RUN_SPAN_PRESSED")),
                    json!(2.0),
                ),
            );
            e.insert("FIRST_RESISTANCE".into(), json!(7.0));
            e.insert("GRIP_DEPTH".into(), json!(8.5));
            e.insert("INSERTION".into(), json!(10.0));
            e.insert(
                "RUN_INSERTION_EXTENDED".into(),
                b("+", g(&e, "INSERTION"), g(&e, "RUN_COLLET_TRAVEL")),
            );
            e.insert("COLLAR_NOMINAL_D".into(), json!(16.3));
            e.insert("COLLAR_ENVELOPE_D".into(), json!(16.5));
            e.insert(
                "BARREL_R".into(),
                b("/", g(&e, "COLLAR_ENVELOPE_D"), json!(2.0)),
            );
            e.insert("HALF_W".into(), g(&e, "BARREL_R"));
            e.insert("ARM_R".into(), json!(7.0));
            e.insert("RUN_ROOT_BAND".into(), t(vec![json!(6.9), json!(9.8)]));
            e.insert("BRANCH_ROOT_BAND".into(), t(vec![json!(8.7), json!(11.7)]));
            e.insert("RUN_COLLAR_BAND".into(), t(vec![json!(12.0), json!(15.1)]));
            e.insert(
                "BRANCH_COLLAR_BAND".into(),
                t(vec![json!(13.8), json!(16.6)]),
            );
            e.insert("ARM_ROOT".into(), ix(g(&e, "BRANCH_ROOT_BAND"), json!(0)));
            {
                let temp1 = g(&e, "BRANCH_COLLAR_BAND");
                e.insert("CAP_NEAR".into(), ix(temp1.clone(), json!(0)));
                e.insert("CAP_FAR".into(), ix(temp1.clone(), json!(1)));
            }
            e.insert("BARREL_NEAR".into(), ix(g(&e, "RUN_ROOT_BAND"), json!(0)));
            e.insert(
                "RUN_ENVELOPE_SHOULDER".into(),
                t(vec![json!(9.8), json!(10.5)]),
            );
            e.insert(
                "BRANCH_ENVELOPE_SHOULDER".into(),
                t(vec![json!(11.7), json!(12.0)]),
            );
            e.insert(
                "BRANCH_WIDTH_EXTENDED".into(),
                ix(g(&e, "_branch"), json!("extended_width_mm")),
            );
            e.insert(
                "BRANCH_WIDTH_PRESSED".into(),
                ix(g(&e, "_branch"), json!("pressed_width_mm")),
            );
            e.insert(
                "BRANCH_REACH".into(),
                b(
                    "-",
                    g(&e, "BRANCH_WIDTH_EXTENDED"),
                    b("/", g(&e, "COLLAR_NOMINAL_D"), json!(2.0)),
                ),
            );
            e.insert(
                "BRANCH_PRESSED_REACH".into(),
                b(
                    "-",
                    g(&e, "BRANCH_WIDTH_PRESSED"),
                    b("/", g(&e, "COLLAR_NOMINAL_D"), json!(2.0)),
                ),
            );
            e.insert(
                "BRANCH_COLLET_TRAVEL".into(),
                b(
                    "-",
                    g(&e, "BRANCH_WIDTH_EXTENDED"),
                    g(&e, "BRANCH_WIDTH_PRESSED"),
                ),
            );
            e.insert(
                "BRANCH_INSERTION_EXTENDED".into(),
                b("+", g(&e, "INSERTION"), g(&e, "BRANCH_COLLET_TRAVEL")),
            );
            e.insert("FIXED_NOSE_R".into(), json!(7.75));
            e.insert("RUN_COLLAR_END".into(), json!(15.75));
            e.insert("BRANCH_COLLAR_END".into(), json!(17.5));
            e.insert("RUN_FIXED_END".into(), json!(18.5));
            e.insert("BRANCH_FIXED_END".into(), json!(20.25));
            e.insert("COLLET_NOSE_R".into(), json!(5.715));
            e.insert("BARREL_FAR".into(), g(&e, "RUN_COLLAR_END"));
            e.insert(
                "COLLET_PROUD".into(),
                b("-", g(&e, "BRANCH_REACH"), g(&e, "BRANCH_FIXED_END")),
            );
            e.insert("UNQUALIFIED_DATUMS".into(),object(vec![(json!("run_fixed_nose_clearance_end_mm"),g(&e,"RUN_FIXED_END")),(json!("branch_fixed_nose_clearance_end_mm"),g(&e,"BRANCH_FIXED_END")),(json!("fixed_reduced_barrel_clearance_radius_mm"),g(&e,"FIXED_NOSE_R")),(json!("release_nose_radius_mm"),g(&e,"COLLET_NOSE_R")),(json!("qualification"),json!("Fixed ends and sleeve radius are conservative clearance proxies; the exact terminal-ring seam/OD is not caliper-qualified."))]));
            e.insert("MEASURE_TOL".into(), json!(0.01));
            e.insert("CARRIER_AFT_COLLET_GAP".into(), json!(0.5));
            e.insert(
                "CARRIER_STROKE".into(),
                b(
                    "+",
                    g(&e, "BRANCH_COLLET_TRAVEL"),
                    g(&e, "CARRIER_AFT_COLLET_GAP"),
                ),
            );
            e.insert("CARRIER_MAX_STROKE".into(), json!(2.5));
            e.insert("CARRIER_RELEASE_OFFSET".into(), json!(0.0));
            e.insert("CARRIER_SQUEEZE_OFFSET".into(), json!(0.0));
            e.insert("CARRIER_CONNECTED_OFFSET".into(), g(&e, "CARRIER_STROKE"));
            e.insert("CARRIER_PARK_OFFSET".into(), g(&e, "CARRIER_STROKE"));
            e.insert(
                "CARRIER_STATES".into(),
                object(vec![
                    (
                        json!("release"),
                        t(vec![g(&e, "CARRIER_RELEASE_OFFSET"), g(&e, "INSERTION")]),
                    ),
                    (
                        json!("squeeze"),
                        t(vec![g(&e, "CARRIER_SQUEEZE_OFFSET"), g(&e, "INSERTION")]),
                    ),
                    (
                        json!("connected"),
                        t(vec![
                            g(&e, "CARRIER_CONNECTED_OFFSET"),
                            g(&e, "BRANCH_INSERTION_EXTENDED"),
                        ]),
                    ),
                    (
                        json!("park"),
                        t(vec![g(&e, "CARRIER_PARK_OFFSET"), Value::Null]),
                    ),
                ]),
            );
        }
        "teyleten_relay" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/teyleten-relay"));
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/teyleten-relay"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/teyleten-relay/teyleten_relay.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            let data = parse_json(read_file(
                cx, b("/", g(&e, "HERE"), json!("scan-datums.json")),
            )?)?;
            let size = ix(ix(data.clone(), json!("pcb")), json!("size_mm"));
            e.insert("length".into(), ix(size.clone(), json!(0)));
            e.insert("width".into(), ix(size.clone(), json!(1)));
            e.insert("pcb_t".into(), ix(size, json!(2)));
            let bounds = ix(data.clone(), json!("observed_bounds_mm"));
            let low_z = ix(ix(bounds.clone(), json!(0)), json!(2));
            let high_z = ix(ix(bounds, json!(1)), json!(2));
            e.insert("envelope_z".into(), b("-", high_z, low_z.clone()));
            e.insert("pin_drop".into(), u("-", low_z));
            let holes = seq(ix(data.clone(), json!("holes")));
            let mut hole_xy = Vec::new();
            let mut radius = 0.;
            let mut dx = 0.;
            let mut dy = 0.;
            for hole in &holes {
                let center = ix(hole.clone(), json!("center_mm"));
                let x = ix(center.clone(), json!(0));
                let y = ix(center, json!(1));
                radius += n(&ix(hole.clone(), json!("radius_mm")));
                dx += n(&x).abs();
                dy += n(&y).abs();
                hole_xy.push(t(vec![x, y]));
            }
            e.insert("hole_dia".into(), json!(radius * 2. / holes.len() as f64));
            e.insert("hole_dx".into(), json!(dx / holes.len() as f64));
            e.insert("hole_dy".into(), json!(dy / holes.len() as f64));
            e.insert("name".into(), json!("relay"));
            e.insert("holes".into(), json!(hole_xy));
            let ports = ix(data.clone(), json!("ports"));
            let contacts = ix(ports.clone(), json!("contacts"));
            let logic = ix(ports, json!("logic"));
            let contact_point = ix(contacts.clone(), json!("point_mm"));
            let logic_point = ix(logic.clone(), json!("point_mm"));
            e.insert("screw_blk_inset".into(), b("-", b("/", g(&e, "length"), json!(2)), ix(contact_point.clone(), json!(0))));
            e.insert("header_inset".into(), b("+", b("/", g(&e, "length"), json!(2)), ix(logic_point, json!(0))));
            let components = seq(ix(data, json!("components")));
            for (key, name) in [("screw_blk_h", "contact-terminals"), ("header_h", "logic-terminals")] {
                let component = components.iter().find(|c| ix((*c).clone(), json!("name")) == json!(name)).expect("terminal component");
                e.insert(key.into(), b("-", ix(component.clone(), json!("surface_top_mm")), g(&e, "pcb_t")));
            }
            e.insert("land_z".into(), ix(contact_point, json!(2)));
            e.insert("contact_port".into(), contacts);
            e.insert("logic_port".into(), logic);
        }
        "wago_221" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/wago-221"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/wago-221"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/wago-221/wago_221.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "SIZES".into(),
                object(vec![
                    (
                        json!("413"),
                        object(vec![
                            (json!("width"), json!(18.8)),
                            (json!("height"), json!(8.4)),
                            (json!("depth"), json!(18.6)),
                            (json!("poles"), json!(3)),
                            (json!("rows"), json!(1)),
                        ]),
                    ),
                    (
                        json!("415"),
                        object(vec![
                            (json!("width"), json!(30.0)),
                            (json!("height"), json!(8.4)),
                            (json!("depth"), json!(18.6)),
                            (json!("poles"), json!(5)),
                            (json!("rows"), json!(1)),
                        ]),
                    ),
                    (
                        json!("420"),
                        object(vec![
                            (json!("width"), json!(29.8)),
                            (json!("height"), json!(15.8)),
                            (json!("depth"), json!(18.3)),
                            (json!("poles"), json!(10)),
                            (json!("rows"), json!(2)),
                        ]),
                    ),
                ]),
            );
            e.insert("lever_open".into(), json!(15.25));
            e.insert(
                "lever_swing".into(),
                b(
                    "-",
                    g(&e, "lever_open"),
                    ix(ix(g(&e, "SIZES"), json!("413")), json!("height")),
                ),
            );
            e.insert("groove_w".into(), json!(3.0));
            e.insert("groove_d".into(), json!(9.0));
            e.insert("groove_h".into(), json!(0.6));
            e.insert(
                "width".into(),
                ix(ix(g(&e, "SIZES"), json!("413")), json!("width")),
            );
            e.insert(
                "depth".into(),
                ix(ix(g(&e, "SIZES"), json!("413")), json!("depth")),
            );
            e.insert(
                "height".into(),
                ix(ix(g(&e, "SIZES"), json!("413")), json!("height")),
            );
            e.insert(
                "poles".into(),
                ix(ix(g(&e, "SIZES"), json!("413")), json!("poles")),
            );
            e.insert("STEP_PATHS".into(), {
                let mut e = e.clone();
                let mut temp1 = Vec::new();
                for item in seq(g(&e, "SIZES")) {
                    e.insert("size".into(), item);
                    temp1.push((
                        g(&e, "size"),
                        b(
                            "/",
                            g(&e, "_HERE"),
                            json!(
                                [
                                    "wago-221-".to_owned(),
                                    format_value(g(&e, "size"), "")?,
                                    ".step".to_owned()
                                ]
                                .concat()
                            ),
                        ),
                    ));
                }
                object(temp1)
            });
        }
        "water_split" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/water-split"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/water-split"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/water-split/water_split.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("RUN_REACH".into(), attr(cx, "tee_connector", "RUN_HALF")?);
            e.insert(
                "BRANCH_REACH".into(),
                attr(cx, "tee_connector", "BRANCH_REACH")?,
            );
            e.insert("REACH".into(), g(&e, "RUN_REACH"));
            e.insert("TUBE_D".into(), attr(cx, "tee_connector", "TUBE_D")?);
            e.insert(
                "_TURNS".into(),
                t(vec![
                    t(vec![
                        t(vec![json!(1.0), json!(0.0), json!(0.0)]),
                        u("-", json!(90.0)),
                    ]),
                    t(vec![
                        t(vec![json!(0.0), json!(1.0), json!(0.0)]),
                        json!(90.0),
                    ]),
                ]),
            );
        }
        "waveshare_43b_display" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/waveshare-43b-display"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/waveshare-43b-display"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/waveshare-43b-display/waveshare_43b_display.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("body_width".into(), json!(106.0));
            e.insert("body_height".into(), json!(69.0));
            e.insert("body_depth".into(), json!(17.0));
            e.insert("bezel_width".into(), json!(113.5));
            e.insert("bezel_height".into(), json!(77.0));
            e.insert("bezel_depth".into(), json!(1.0));
            e.insert("bezel_corner_r".into(), json!(2.5));
            e.insert("bezel_offset_x".into(), u("-", json!(0.5)));
            e.insert("bezel_offset_z".into(), json!(1.0));
            e.insert("bezel_y0".into(), json!(0.0));
            e.insert(
                "bezel_y1".into(),
                b("+", g(&e, "bezel_y0"), g(&e, "bezel_depth")),
            );
            e.insert("body_y0".into(), g(&e, "bezel_y1"));
            e.insert(
                "body_y1".into(),
                b("+", g(&e, "body_y0"), g(&e, "body_depth")),
            );
            e.insert("total_depth".into(), g(&e, "body_y1"));
            e.insert(
                "bezel_y_center".into(),
                b(
                    "+",
                    g(&e, "bezel_y0"),
                    b("/", g(&e, "bezel_depth"), json!(2.0)),
                ),
            );
            e.insert(
                "body_y_center".into(),
                b(
                    "+",
                    g(&e, "body_y0"),
                    b("/", g(&e, "body_depth"), json!(2.0)),
                ),
            );
        }
        "wr1110_regulator" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/wr1110-regulator"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/wr1110-regulator"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/reference/wr1110-regulator/wr1110_regulator.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("BODY_D".into(), json!(18.87));
            e.insert("BODY_START".into(), json!(14.65));
            e.insert("BODY_END".into(), json!(50.05));
            e.insert(
                "BODY_LENGTH".into(),
                b("-", g(&e, "BODY_END"), g(&e, "BODY_START")),
            );
            e.insert("INLET_HEX_AF".into(), json!(19.0));
            e.insert("INLET_HEX_D".into(), json!(20.6));
            e.insert("OUTLET_HEX_AF".into(), json!(19.08));
            e.insert("OUTLET_HEX_D".into(), json!(21.76));
            e.insert("OUTLET_HEX_CLOCK".into(), u("-", json!(2.0)));
            e.insert("TOTAL_LENGTH".into(), json!(54.47));
            e.insert("STUB_LENGTH".into(), json!(9.18));
            e.insert("STUB_D".into(), json!(14.2));
            e.insert(
                "OVERALL_LENGTH".into(),
                b("+", g(&e, "TOTAL_LENGTH"), g(&e, "STUB_LENGTH")),
            );
            e.insert(
                "INLET_PROFILE".into(),
                t(vec![
                    t(vec![json!(0.0), json!(9.38)]),
                    t(vec![json!(0.35), json!(9.93)]),
                    t(vec![json!(0.8), b("/", g(&e, "INLET_HEX_D"), json!(2))]),
                    t(vec![json!(13.35), b("/", g(&e, "INLET_HEX_D"), json!(2))]),
                    t(vec![json!(13.7), json!(10.22)]),
                    t(vec![json!(14.2), json!(9.78)]),
                    t(vec![g(&e, "BODY_START"), b("/", g(&e, "BODY_D"), json!(2))]),
                ]),
            );
            e.insert(
                "OUTLET_PROFILE".into(),
                t(vec![
                    t(vec![g(&e, "BODY_END"), b("/", g(&e, "BODY_D"), json!(2))]),
                    t(vec![json!(50.4), json!(9.7)]),
                    t(vec![json!(50.9), json!(10.38)]),
                    t(vec![json!(51.35), json!(10.78)]),
                    t(vec![json!(51.65), b("/", g(&e, "OUTLET_HEX_D"), json!(2))]),
                    t(vec![json!(53.35), b("/", g(&e, "OUTLET_HEX_D"), json!(2))]),
                    t(vec![json!(53.75), json!(10.65)]),
                    t(vec![json!(54.1), json!(10.12)]),
                    t(vec![g(&e, "TOTAL_LENGTH"), json!(9.45)]),
                ]),
            );
            e.insert(
                "STUB_PROFILE".into(),
                t(vec![
                    t(vec![
                        g(&e, "TOTAL_LENGTH"),
                        b("/", g(&e, "STUB_D"), json!(2)),
                    ]),
                    t(vec![json!(54.9), json!(6.85)]),
                    t(vec![json!(55.3), json!(6.48)]),
                    t(vec![json!(55.7), json!(6.1)]),
                    t(vec![json!(56.2), json!(6.3)]),
                    t(vec![json!(56.8), json!(6.65)]),
                    t(vec![json!(57.2), json!(6.72)]),
                    t(vec![json!(61.6), json!(6.6)]),
                    t(vec![json!(62.1), json!(6.48)]),
                    t(vec![json!(62.5), json!(6.05)]),
                    t(vec![json!(63.2), json!(5.5)]),
                    t(vec![g(&e, "OVERALL_LENGTH"), json!(4.1)]),
                ]),
            );
        }
        "y_divider" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert("HERE".into(), path(cx, "hardware/reference/y-divider"));
            e.insert("_HERE".into(), path(cx, "hardware/reference/y-divider"));
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/y-divider/y_divider.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "MEASUREMENTS".into(),
                b(
                    "/",
                    attr_value(g(&e, "_here"), "parent"),
                    json!("native-measurements.json"),
                ),
            );
            e.insert("HALF".into(), json!(19.25));
            e.insert("OUTLET_Y".into(), json!(7.35));
            e.insert("HALF_W".into(), json!(8.1));
            e.insert("TUBE_D".into(), json!(6.35));
            e.insert("MEASURE_TOL".into(), json!(0.01));
        }
        "yyfkgcp_pogo_4p" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/reference/yyfkgcp-pogo-4p"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/reference/yyfkgcp-pogo-4p"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/reference/yyfkgcp-pogo-4p/yyfkgcp_pogo_4p.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("STEP_PATHS".into(), {
                let mut e = e.clone();
                let mut temp1 = Vec::new();
                for item in seq(t(vec![json!("female"), json!("male")])) {
                    e.insert("half".into(), item);
                    temp1.push((
                        g(&e, "half"),
                        b(
                            "/",
                            attr_value(g(&e, "_here"), "parent"),
                            json!(
                                [
                                    "pogo-4p-".to_owned(),
                                    format_value(g(&e, "half"), "")?,
                                    ".step".to_owned()
                                ]
                                .concat()
                            ),
                        ),
                    ));
                }
                object(temp1)
            });
            {
                let temp3 = t(vec![json!(17.54), json!(4.0), json!(4.0)]);
                e.insert("BODY_L".into(), ix(temp3.clone(), json!(0)));
                e.insert("BODY_W".into(), ix(temp3.clone(), json!(1)));
                e.insert("BODY_T".into(), ix(temp3.clone(), json!(2)));
            }
            {
                let temp4 = t(vec![json!(2.0), json!(1.0)]);
                e.insert("EAR_FACE".into(), ix(temp4.clone(), json!(0)));
                e.insert("EAR_T".into(), ix(temp4.clone(), json!(1)));
            }
            {
                let temp5 = t(vec![json!(20.44), json!(1.5)]);
                e.insert("EAR_PITCH".into(), ix(temp5.clone(), json!(0)));
                e.insert("EAR_HOLE_D".into(), ix(temp5.clone(), json!(1)));
            }
            e.insert("EAR_L".into(), json!(23.4));
            {
                let temp6 = t(vec![json!(4), json!(2.54)]);
                e.insert("PINS".into(), ix(temp6.clone(), json!(0)));
                e.insert("PIN_PITCH".into(), ix(temp6.clone(), json!(1)));
            }
            {
                let temp7 = t(vec![json!(0.7), json!(1.5)]);
                e.insert("TAIL_D".into(), ix(temp7.clone(), json!(0)));
                e.insert("TAIL_L".into(), ix(temp7.clone(), json!(1)));
            }
            {
                let temp8 = t(vec![json!(0.9), json!(1.0), json!(1.1)]);
                e.insert("PIN_D".into(), ix(temp8.clone(), json!(0)));
                e.insert("PIN_PROUD".into(), ix(temp8.clone(), json!(1)));
                e.insert("STROKE".into(), ix(temp8.clone(), json!(2)));
            }
            e.insert("PAD_D".into(), json!(1.5));
            e.insert("MAGNET_PITCH".into(), json!(13.54));
        }
        "_rotator_interface" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/printed-parts/fixtures/weld-rotator"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/printed-parts/fixtures/weld-rotator"),
            );
            e.insert(
                "_here".into(),
                path(
                    cx,
                    "hardware/printed-parts/fixtures/weld-rotator/_rotator_interface.py",
                ),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("MM_PER_IN".into(), json!(25.4));
            e.insert("TUBE_OD".into(), b("*", json!(5.0), g(&e, "MM_PER_IN")));
            e.insert("TUBE_WALL".into(), b("*", json!(0.065), g(&e, "MM_PER_IN")));
            e.insert(
                "TUBE_ID".into(),
                b(
                    "-",
                    g(&e, "TUBE_OD"),
                    b("*", json!(2.0), g(&e, "TUBE_WALL")),
                ),
            );
            e.insert("TUBE_LENGTH".into(), b("*", json!(6.0), g(&e, "MM_PER_IN")));
            e.insert(
                "ENDCAP_RECESS".into(),
                b("*", json!(0.25), g(&e, "MM_PER_IN")),
            );
            e.insert("SERVICE_BORE_DIAMETER".into(), json!(90.0));
            e.insert("BASE_CLEARANCE".into(), json!(24.0));
            e.insert("BELT_PITCH".into(), json!(5.0));
            e.insert("BELT_PITCH_LENGTH".into(), json!(550.0));
            e.insert("BELT_WIDTH".into(), json!(15.0));
            e.insert("BELT_PITCH_LINE_OFFSET".into(), json!(0.5715));
            e.insert("BELT_TOOTH_HEIGHT".into(), json!(2.06));
            e.insert("BELT_THICKNESS".into(), json!(3.81));
            e.insert("MOTOR_PULLEY_TEETH".into(), json!(20));
            e.insert("TABLE_PULLEY_TEETH".into(), json!(90));
            e.insert("MOTOR_PULLEY_LENGTH".into(), json!(20.0));
            e.insert("MOTOR_PULLEY_FLANGE_DIAMETER".into(), json!(35.0));
            e.insert("MOTOR_PULLEY_FLANGE_LENGTH".into(), json!(2.0));
            e.insert(
                "MOTOR_PULLEY_LAND_LENGTH".into(),
                b(
                    "-",
                    g(&e, "MOTOR_PULLEY_LENGTH"),
                    b("*", json!(2.0), g(&e, "MOTOR_PULLEY_FLANGE_LENGTH")),
                ),
            );
            e.insert("MOTOR_FULL_STEPS".into(), json!(200));
            e.insert("DRIVER_MICROSTEPS".into(), json!(16));
            e.insert(
                "MOTOR_PULSES_PER_REV".into(),
                b("*", g(&e, "MOTOR_FULL_STEPS"), g(&e, "DRIVER_MICROSTEPS")),
            );
            e.insert("TRAVEL_MIN".into(), json!(5.0));
            e.insert("TRAVEL_NOMINAL".into(), json!(8.0));
            e.insert("TRAVEL_MAX".into(), json!(15.0));
            e.insert("OVERLAP_DEGREES".into(), json!(20.0));
            e.insert("MOTOR_FRAME".into(), json!(57.3));
            e.insert("MOTOR_BODY_LENGTH".into(), json!(76.5));
            e.insert("MOTOR_SHAFT_DIAMETER".into(), json!(6.35));
            e.insert("MOTOR_SHAFT_LENGTH".into(), json!(21.0));
            e.insert("MOTOR_SHAFT_DCUT_LENGTH".into(), json!(15.0));
            e.insert("MOTOR_PILOT_DIAMETER".into(), json!(38.1));
            e.insert("MOTOR_PILOT_LENGTH".into(), json!(1.6));
            e.insert("MOTOR_MOUNT_SQUARE".into(), json!(47.14));
            e.insert("MOTOR_MOUNT_HOLE_DIAMETER".into(), json!(5.2));
        }
        "_bound" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/printed-parts/shop-storage/_bound.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("EXACT".into(), json!("exact"));
            e.insert("MOST".into(), json!("most"));
            e.insert("NEST_INTERLOCKS".into(), json!(0.75));
            e.insert("NEST_COMPACT".into(), json!(1.0));
            e.insert("NEST_TANGLES".into(), json!(1.4));
        }
        "_kit" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/printed-parts/shop-storage/_kit.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert(
                "_STOCK_PATH".into(),
                b(
                    "/",
                    attr_value(g(&e, "_here"), "parent"),
                    json!("gridfinity-stock/manifest.json"),
                ),
            );
            e.insert(
                "_STOCK".into(),
                parse_json(read_file(cx, g(&e, "_STOCK_PATH"))?)?,
            );
            {
                let value = ix(g(&e, "_STOCK"), json!("constants"));
                extend_env(&mut e, value);
            }
            e.insert("grid_unit".into(), g(&e, "GRU"));
            e.insert("height_unit".into(), g(&e, "GRHU"));
            e.insert("grid_clearance".into(), g(&e, "GR_TOL"));
            e.insert("seat_clearance".into(), g(&e, "GR_BASE_CLR"));
            e.insert("h2c_build_x".into(), json!(325.0));
            e.insert("h2c_build_y".into(), json!(320.0));
            e.insert("h2c_build_z".into(), json!(320.0));
            e.insert("dock_extra_depth".into(), json!(6.0));
            e.insert(
                "dock_seat_z".into(),
                b("-", g(&e, "dock_extra_depth"), g(&e, "seat_clearance")),
            );
            e.insert("lip_inset".into(), json!(2.6));
            e.insert("_stock_bin".into(), {
                let argv = vec![];
                let kwargs = merge(vec![ix(g(&e, "_STOCK"), json!("defaults"))]);
                call(cx, "_kit", "SimpleNamespace", argv, kwargs, Some(&e))?
            });
            e.insert("wall_thickness".into(), g(&e, "GR_WALL"));
            e.insert("divider_thickness".into(), g(&e, "GR_DIV_WALL"));
            e.insert("bin_floor_z".into(), g(&e, "GR_BOT_H"));
            e.insert(
                "label_tape_width".into(),
                attr_value(g(&e, "_stock_bin"), "label_width"),
            );
            e.insert(
                "label_tape_height".into(),
                attr_value(g(&e, "_stock_bin"), "label_height"),
            );
        }
        "_holder" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/printed-parts/shop-storage/_holder.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("wall".into(), json!(3.0));
            e.insert("slip".into(), json!(1.5));
            e.insert("trough_angle".into(), json!(45.0));
            e.insert("slot_mouth".into(), json!(34.0));
            e.insert("slot_root".into(), json!(5.0));
            e.insert("slot_taper".into(), json!(14.0));
            e.insert("slot_floor".into(), json!(6.0));
        }
        "catalog" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/printed-parts/shop-storage/catalog.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("EXACT".into(), attr(cx, "_bound", "EXACT")?);
            e.insert("MOST".into(), attr(cx, "_bound", "MOST")?);
            e.insert(
                "NEST_INTERLOCKS".into(),
                attr(cx, "_bound", "NEST_INTERLOCKS")?,
            );
            e.insert("NEST_TANGLES".into(), attr(cx, "_bound", "NEST_TANGLES")?);
            e.insert("inch".into(), json!(25.4));
            e.insert(
                "DIN912".into(),
                json!("DIN 912 / ISO 4762 socket head cap screw"),
            );
            e.insert(
                "_din912".into(),
                object(vec![
                    (json!(2.0), t(vec![json!(3.8), json!(2.0)])),
                    (json!(3.0), t(vec![json!(5.5), json!(3.0)])),
                    (json!(5.0), t(vec![json!(8.5), json!(5.0)])),
                ]),
            );
            e.insert("M3X25".into(), {
                let argv = vec![
                    json!("BNUOK M3 x 25, 12.9 black oxide"),
                    json!(3.0),
                    json!(25.0),
                    json!(60),
                    json!("B0DJQGF665"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("M3X12SS".into(), {
                let argv = vec![
                    json!("BNUOK M3 x 12, 304 SS — wet joints"),
                    json!(3.0),
                    json!(12.0),
                    json!(120),
                    json!("B0DJQGMQZM"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("M3X12".into(), {
                let argv = vec![
                    json!("BNUOK M3 x 12, 12.9 black oxide — dry joints"),
                    json!(3.0),
                    json!(12.0),
                    json!(120),
                    json!("B0DJQGVK8S"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("M3X10".into(), {
                let argv = vec![
                    json!("BNUOK M3 x 10, 12.9 black oxide"),
                    json!(3.0),
                    json!(10.0),
                    json!(120),
                    json!("B0DJQGGDP2"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("M3X8".into(), {
                let argv = vec![
                    json!("BNUOK M3 x 8, 12.9 black oxide"),
                    json!(3.0),
                    json!(8.0),
                    json!(120),
                    json!("B0DJQGPRPV"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("M5X10".into(), {
                let argv = vec![
                    json!("MewuDecor M5 x 10, 12.9 black oxide"),
                    json!(5.0),
                    json!(10.0),
                    json!(100),
                    json!("B0BHZVXNJX"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("M2X6".into(), {
                let argv = vec![
                    json!("Sutemribor M2 x 6, 12.9 black oxide"),
                    json!(2.0),
                    json!(6.0),
                    json!(105),
                    json!("B0CXQ7Q7L3"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cap_screw", argv, kwargs, Some(&e))?
            });
            e.insert("ULP_HEAD".into(), t(vec![json!(6.0), json!(1.5)]));
            e.insert("ULPM3X6".into(), {
                let argv = vec![
                    json!("McMaster 91223A412 M3 x 6 ultra-low-profile, 316 SS"),
                    json!(100),
                    {
                        let argv = {
                            let mut temp2 = vec![];
                            temp2.extend(seq(g(&e, "ULP_HEAD")));
                            temp2.push(json!(3.0));
                            temp2.push(json!(6.0));
                            temp2
                        };
                        let kwargs = json!({});
                        call(cx, "catalog", "screw_volume", argv, kwargs, Some(&e))?
                    },
                    json!("McMaster 91223A412; head over every published ultra-low M3"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("ULPM3X8".into(), {
                let argv = vec![
                    json!("McMaster 91223A413 M3 x 8 ultra-low-profile, 316 SS"),
                    json!(100),
                    {
                        let argv = {
                            let mut temp3 = vec![];
                            temp3.extend(seq(g(&e, "ULP_HEAD")));
                            temp3.push(json!(3.0));
                            temp3.push(json!(8.0));
                            temp3
                        };
                        let kwargs = json!({});
                        call(cx, "catalog", "screw_volume", argv, kwargs, Some(&e))?
                    },
                    json!("McMaster 91223A413; head over every published ultra-low M3"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("M5WASHER".into(),{let argv=vec![json!("M5 x 25 mm OD fender washer, 304 SS"),json!(60),{let argv=vec![json!(25.0),json!(1.5)];let kwargs=json!({});call(cx,"catalog","cylinder_volume",argv,kwargs,Some(&e))?},json!("B0GSMDY5GL states both diameters; 1.5 mm is the thick end of 304 at this width")];let kwargs=object(vec![("nest".into(),json!(0.8))]);call(cx,"_bound","heap",argv,kwargs,None)?});
            e.insert("RUTHEX_M3".into(), {
                let argv = vec![
                    json!("ruthex RX-M3x5.7 heat-set insert — the appliance default"),
                    json!(100),
                    {
                        let argv = vec![json!(4.6), json!(5.7)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("ruthex RX-M3x5.7 published body; count from B08BCRZZS3"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("RUTHEX_M3S".into(), {
                let argv = vec![
                    json!("ruthex RX-M3Sx4.0 heat-set insert — shallow bores only"),
                    json!(100),
                    {
                        let argv = vec![json!(4.6), json!(4.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("ruthex RX-M3Sx4.0 published body; count from B09ZHSGHXD"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("RUTHEX_M2".into(), {
                let argv = vec![
                    json!("ruthex RX-M2x4 heat-set insert"),
                    json!(70),
                    {
                        let argv = vec![json!(3.6), json!(4.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("ruthex RX-M2x4 published body; count from B088QJG676"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("RUTHEX_M5".into(), {
                let argv = vec![
                    json!("ruthex RX-M5x9.5 heat-set insert"),
                    json!(50),
                    {
                        let argv = vec![json!(7.1), json!(9.5)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("ruthex RX-M5x9.5 published body; count from B07YSVXWS8"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("MAGNETS".into(), {
                let argv = vec![
                    json!("neodymium disc magnets, 3 x 1 mm N52"),
                    json!(100),
                    {
                        let argv = vec![json!(3.0), json!(1.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("B0BQ3LPGZ1 states 3 x 1 mm"),
                ];
                let kwargs = object(vec![("nest".into(), json!(0.9))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("MEMBRANES".into(),{let argv=vec![json!("LVDALAB PTFE membrane filters, 13 mm x 0.45 um"),json!(100),{let argv=vec![json!(13.0),json!(0.15)];let kwargs=json!({});call(cx,"catalog","cylinder_volume",argv,kwargs,Some(&e))?},json!("B0D41KT345 states the diameter; 0.15 mm is the thick end of a supported membrane")];let kwargs=object(vec![("nest".into(),json!(0.9))]);call(cx,"_bound","heap",argv,kwargs,None)?});
            e.insert(
                "_din46228".into(),
                object(vec![
                    (json!(0.34), t(vec![json!(3.4), json!(12.0)])),
                    (json!(0.5), t(vec![json!(3.8), json!(14.0)])),
                    (json!(0.75), t(vec![json!(4.0), json!(14.0)])),
                    (json!(1.0), t(vec![json!(4.4), json!(14.0)])),
                    (json!(1.5), t(vec![json!(4.8), json!(14.0)])),
                    (json!(2.5), t(vec![json!(5.6), json!(16.0)])),
                ]),
            );
            e.insert(
                "FERRULES".into(),
                t(vec![
                    {
                        let argv = vec![json!(0.34), json!("turquoise — 22 AWG"), json!(250)];
                        let kwargs = json!({});
                        call(cx, "catalog", "ferrule", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!(1.5), json!("black — 16 AWG"), json!(250)];
                        let kwargs = json!({});
                        call(cx, "catalog", "ferrule", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!(0.5), json!("white"), json!(150)];
                        let kwargs = json!({});
                        call(cx, "catalog", "ferrule", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!(0.75), json!("grey"), json!(100)];
                        let kwargs = json!({});
                        call(cx, "catalog", "ferrule", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!(1.0), json!("red"), json!(100)];
                        let kwargs = json!({});
                        call(cx, "catalog", "ferrule", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!(2.5), json!("blue"), json!(100)];
                        let kwargs = json!({});
                        call(cx, "catalog", "ferrule", argv, kwargs, Some(&e))?
                    },
                ]),
            );
            e.insert(
                "SHRINK".into(),
                t(vec![
                    {
                        let argv = vec![
                            json!("1.06 - 1.59 mm"),
                            json!(1.59),
                            json!(190),
                            json!(40.0),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "shrink", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!("2.12 mm"), json!(2.12), json!(100), json!(40.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "shrink", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv =
                            vec![json!("3.18 - 3.57 mm"), json!(3.57), json!(90), json!(40.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "shrink", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![json!("3.97 mm"), json!(3.97), json!(70), json!(40.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "shrink", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv =
                            vec![json!("5.08 - 5.95 mm"), json!(5.95), json!(50), json!(40.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "shrink", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv =
                            vec![json!("7.94 - 9.92 mm"), json!(9.92), json!(80), json!(40.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "shrink", argv, kwargs, Some(&e))?
                    },
                ]),
            );
            e.insert(
                "TERMINALS".into(),
                t(vec![
                    {
                        let argv = vec![
                            json!("6.3 mm female push-on, red — Baomain"),
                            json!("6.3 mm"),
                            json!(100),
                            json!("B01G408A4M"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "spade", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!("4.8 mm female push-on, red — Baomain"),
                            json!("4.8 mm"),
                            json!(100),
                            json!("B01N5APVEE"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "spade", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!("#4 ring, red — smseace"),
                            json!("#4 ring"),
                            json!(150),
                            json!("B08B5VS8ZR"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "spade", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!("6.3 mm female, assorted — three kits decanted"),
                            json!("6.3 mm"),
                            json!(123),
                            json!("B0B4H54KPS"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "spade", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!("4.8 mm female, assorted — three kits decanted"),
                            json!("4.8 mm"),
                            json!(123),
                            json!("B0B9MZJ2ML"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "spade", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!("2.8 mm male — Baomain 0.11 in"),
                            json!("2.8 mm"),
                            json!(214),
                            json!("B01MZZGAJP"),
                            json!(4.5),
                            json!(18.0),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "spade", argv, kwargs, Some(&e))?
                    },
                ]),
            );
            e.insert(
                "LEVERS".into(),
                t(vec![
                    {
                        let argv = vec![
                            json!("WAGO 221-413, 3-conductor"),
                            json!(50),
                            b("*", b("*", json!(13.0), json!(12.5)), json!(8.2)),
                            json!("WAGO 221-413 datasheet, 13.0 x 12.5 x 8.2 mm"),
                        ];
                        let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                        call(cx, "_bound", "heap", argv, kwargs, None)?
                    },
                    {
                        let argv = vec![
                            json!("WAGO 221-415, 5-conductor"),
                            json!(25),
                            b("*", b("*", json!(13.0), json!(12.5)), json!(13.0)),
                            json!("WAGO 221-415 datasheet, 13.0 x 12.5 x 13.0 mm"),
                        ];
                        let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                        call(cx, "_bound", "heap", argv, kwargs, None)?
                    },
                    {
                        let argv = vec![
                            json!("WAGO 221-420, 10-conductor"),
                            json!(15),
                            b("*", b("*", json!(13.0), json!(12.5)), json!(25.6)),
                            json!("WAGO 221-420 datasheet, 13.0 x 12.5 x 25.6 mm"),
                        ];
                        let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                        call(cx, "_bound", "heap", argv, kwargs, None)?
                    },
                ]),
            );
            e.insert(
                "TIES".into(),
                t(vec![
                    {
                        let argv = vec![
                            json!(4),
                            json!(2.5),
                            json!(1.0),
                            json!(200),
                            json!("B0BC1VH4XB"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "zip_ties", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!(6),
                            json!(2.5),
                            json!(1.0),
                            json!(100),
                            json!("B0DR8KSVQD"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "zip_ties", argv, kwargs, Some(&e))?
                    },
                    {
                        let argv = vec![
                            json!(8),
                            json!(4.8),
                            json!(1.1),
                            json!(100),
                            json!("B08BKSHJ93"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "zip_ties", argv, kwargs, Some(&e))?
                    },
                ]),
            );
            e.insert("XH_PITCH".into(), json!(2.5));
            e.insert(
                "XH_HOUSINGS".into(),
                t(seq({
                    let mut e = e.clone();
                    let mut temp5 = Vec::new();
                    for item in seq(t(vec![
                        t(vec![json!(3), json!(40)]),
                        t(vec![json!(4), json!(40)]),
                        t(vec![json!(5), json!(30)]),
                        t(vec![json!(6), json!(30)]),
                        t(vec![json!(7), json!(20)]),
                        t(vec![json!(9), json!(20)]),
                        t(vec![json!(10), json!(20)]),
                    ])) {
                        {
                            let temp6 = item;
                            e.insert("p".into(), ix(temp6.clone(), json!(0)));
                            e.insert("n".into(), ix(temp6.clone(), json!(1)));
                        }
                        temp5.push({
                            let argv = vec![g(&e, "p"), g(&e, "n")];
                            let kwargs = json!({});
                            call(cx, "catalog", "xh_housing", argv, kwargs, Some(&e))?
                        });
                    }
                    json!(temp5)
                })),
            );
            e.insert("XH_CONTACTS".into(), {
                let argv = vec![
                    json!("JST SXH-001T contacts, loose"),
                    json!(400),
                    b("*", b("*", json!(1.6), json!(2.4)), json!(8.6)),
                    json!("JST SXH-001T-P0.6 drawing; count from the CQRobot kits"),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_TANGLES"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("XH_LEADS".into(), {
                let argv = vec![
                    json!("pre-crimped XH leads"),
                    json!(100),
                    b("+", b("*", b("*", json!(1.6), json!(2.4)), json!(8.6)), {
                        let argv = vec![json!(1.7), json!(150.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    }),
                    json!("SXH-001T contact on 1.7 mm OD 22 AWG silicone, coiled"),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_TANGLES"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("RJ11_JACKS".into(), {
                let argv = vec![
                    json!("RiteAV RJ11 6P4C punchdown keystone jacks, black"),
                    json!(10),
                    b("*", b("*", json!(14.8), json!(22.5)), json!(30.0)),
                    json!("the keystone form factor is 14.8 x 22.5 mm; 30 mm over the IDC block"),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("RJ11_PLUGS".into(), {
                let argv = vec![
                    json!("EZYUMM RJ11 6P4C 3-prong modular plugs"),
                    json!(20),
                    b("*", b("*", json!(9.65), json!(11.7)), json!(7.6)),
                    json!("FCC 6P4C plug is 9.65 mm across the latch; count from the EZYUMM pack"),
                ];
                let kwargs = object(vec![("nest".into(), json!(0.9))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("UNION_TEES".into(), {
                let argv = vec![
                    json!("PP0208E"),
                    json!("union tee"),
                    json!(39.1),
                    json!(16.3),
                    json!(30),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("UNION_ELBOWS".into(), {
                let argv = vec![
                    json!("PP0308E"),
                    json!("union elbow"),
                    json!(28.5),
                    json!(16.3),
                    json!(40),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("TWO_WAY".into(), {
                let argv = vec![
                    json!("PP2308E"),
                    json!("two-way divider"),
                    json!(35.7),
                    json!(16.3),
                    json!(20),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("BULKHEADS".into(), {
                let argv = vec![
                    json!("PP1208E"),
                    json!("bulkhead union"),
                    json!(34.6),
                    json!(22.9),
                    json!(10),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("BULKHEADS_ACETAL".into(), {
                let argv = vec![
                    json!("PI1208S"),
                    json!("acetal bulkhead union"),
                    json!(34.9),
                    json!(22.2),
                    json!(2),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("MALE_CONNECTORS".into(), {
                let argv = vec![
                    json!("PI010822S / PP010822E / PP010821WP"),
                    json!("male connectors"),
                    json!(38.0),
                    json!(20.0),
                    json!(30),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("FEMALE_ADAPTERS".into(), {
                let argv = vec![
                    json!("PP450822E"),
                    json!("female adapter"),
                    json!(32.2),
                    json!(24.0),
                    json!(10),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("FLARE_ADAPTERS".into(), {
                let argv = vec![
                    json!("PI4512F6S / PP061208W"),
                    json!("flare adapter and reducer stem"),
                    json!(38.1),
                    json!(22.2),
                    json!(20),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("BRASS_FLARE".into(), {
                let argv = vec![
                    json!("MI4508F4SLF"),
                    json!("brass flare connector"),
                    json!(45.0),
                    json!(18.0),
                    json!(10),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "jg", argv, kwargs, Some(&e))?
            });
            e.insert("NEOFIT_BULKHEADS".into(), {
                let argv = vec![
                    json!("neoFit ABU44-E acetal bulkheads"),
                    json!(40.0),
                    json!(26.0),
                    json!(10),
                    json!("B0DPL88RHC"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("PURESEC_ELBOWS".into(), {
                let argv = vec![
                    json!("PureSec 90-degree elbow bulkheads"),
                    json!(45.0),
                    json!(30.0),
                    json!(5),
                    json!("B07P8784D2"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("BALL_VALVES".into(), {
                let argv = vec![
                    json!("NeoFit push-fit ball valves"),
                    json!(50.8),
                    json!(25.0),
                    json!(5),
                    json!("B0DPLBYZB4"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("CHECK_VALVES".into(), {
                let argv = vec![
                    json!("GASHER and ChillWaves 1/4 NPT check valves"),
                    json!(65.0),
                    json!(26.0),
                    json!(8),
                    json!("B08J2DN6HC"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("COUPLINGS".into(), {
                let argv = vec![
                    json!("GAGIRA, LTWFITTING and TAISHER couplings and elbows"),
                    json!(40.0),
                    json!(25.0),
                    json!(14),
                    json!("B0BVR3R58V"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("BARBS".into(), {
                let argv = vec![
                    json!("LTWFITTING and MAACFLOW barb adapters"),
                    json!(50.0),
                    json!(18.0),
                    json!(9),
                    json!("B07PNPHWMG"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("PNEUMATIC".into(), {
                let argv = vec![
                    json!("MALIDA, TAILONZ and DERPIPE push-fit"),
                    json!(35.0),
                    json!(20.0),
                    json!(25),
                    json!("B07HGTKQ89"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("CLAMPS".into(), {
                let argv = vec![
                    json!("YDS and WC-316SS-06 hose clamps"),
                    json!(42.0),
                    json!(25.0),
                    json!(20),
                    json!("B0968K4JRN"),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("STIFFENERS".into(), {
                let argv = vec![
                    json!("Siptenk 1/4 in tube stiffeners"),
                    json!(15.0),
                    json!(7.0),
                    json!(100),
                    json!("B0CS662NVK"),
                    json!(0.9),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "listed", argv, kwargs, Some(&e))?
            });
            e.insert("REGULATOR".into(), {
                let argv = vec![
                    json!("Interstate Pneumatics WR1110 regulator"),
                    json!(32.0),
                    json!(32.0),
                    json!(90.0),
                    json!("Interstate Pneumatics WR1110 published body"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("RELIEF_VALVE".into(), {
                let argv = vec![
                    json!("Control Devices SV-125 relief valve"),
                    json!(30.0),
                    json!(22.0),
                    json!(65.0),
                    json!("Control Devices SV-125 published body"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("WIRE_REEL".into(),{let argv=vec![json!("BNTECHGO 22 AWG silicone, 250 ft black"),json!(99.1),json!(99.1),json!(88.9),json!("B06Y2PNW41 package — the listing publishes the wire's 1.7 mm OD and no reel figure")];let kwargs=json!({});call(cx,"_bound","parcel",argv,kwargs,None)?});
            e.insert("RIBBON_REEL".into(), {
                let argv = vec![
                    json!("BNTECHGO 28 AWG 4-conductor silicone ribbon, 50 ft"),
                    json!(81.0),
                    json!(77.0),
                    json!(68.0),
                    json!("B0DK4V733Q package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("SOLDER_ROLL".into(),{let argv=vec![json!("Kester 24-6337-0027 0.031 in, 1 lb"),json!(63.5),json!(58.4),json!(58.4),json!("B00068IJNQ package — Kester publishes the alloy and the fill, not the spool")];let kwargs=json!({});call(cx,"_bound","parcel",argv,kwargs,None)?});
            e.insert("SOLDER_POCKET".into(), {
                let argv = vec![
                    json!("Kester 44 0.020 in, 3/4 oz pocket pack"),
                    json!(44.5),
                    json!(44.5),
                    json!(12.7),
                    json!("B00068IJQI package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("BRAID_BOBBIN".into(), {
                let argv = vec![
                    json!("Chemtronics Soder-Wick on its ESD bobbin"),
                    json!(44.5),
                    json!(44.5),
                    json!(6.4),
                    json!("B00425FUW2 package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("KAPTON_ROLLS".into(), {
                let argv = vec![
                    json!("ELEGOO polyimide tape, four widths"),
                    json!(100.0),
                    json!(100.0),
                    json!(60.0),
                    json!("B07XD98YYT package, the four rolls stacked"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("PTFE_TAPE".into(), {
                let argv = vec![
                    json!("Millrose 70894 PTFE thread seal tape"),
                    json!(53.0),
                    json!(53.0),
                    json!(15.0),
                    json!("B07C9ZV4PG package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("SN2549".into(), {
                let argv = vec![
                    json!("iCrimp SN-2549 ratcheting crimper, AWG 28-18"),
                    json!(190.0),
                    json!(65.0),
                    json!(27.9),
                    json!("iwiss.com publishes the SN-2549's 190 x 65 x 27.9 mm product envelope"),
                    t(vec![g(&e, "EXACT"), g(&e, "EXACT"), g(&e, "EXACT")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("HS9327".into(), {
                let argv = vec![
                    json!("haisstronica HS-9327 ratchet crimper, AWG 22-10"),
                    json!(230.1),
                    json!(59.9),
                    json!(30.0),
                    json!("B08F3JKDD3 states 230.1 x 59.9 mm; the thickness is the parcel's"),
                    t(vec![g(&e, "EXACT"), g(&e, "EXACT"), g(&e, "MOST")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("PRECIVA".into(), {
                let argv = vec![
                    json!("Preciva ferrule crimper, AWG 28-5"),
                    json!(240.0),
                    json!(48.0),
                    json!(32.0),
                    json!("B0DS622GKN states a 240 x 48 mm tool; the thickness is the kit case's"),
                    t(vec![g(&e, "EXACT"), g(&e, "EXACT"), g(&e, "MOST")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("KLEIN_11063W".into(),{let argv=vec![json!("Klein 11063W Katapult stripper, 8-20 AWG solid"),json!(167.5),json!(69.0),json!(25.0),json!("Klein publishes 6.594 in overall and no other figure; the rest is B00CXKOEQ6"),t(vec![g(&e,"EXACT"),g(&e,"MOST"),g(&e,"MOST")])];let kwargs=json!({});call(cx,"_bound","mixed",argv,kwargs,None)?});
            e.insert("KLEIN_11057".into(), {
                let argv = vec![
                    json!("Klein 11057 wire stripper"),
                    json!(184.0),
                    json!(70.0),
                    json!(25.0),
                    json!("Klein publishes the overall length; the rest is the parcel"),
                    t(vec![g(&e, "EXACT"), g(&e, "MOST"), g(&e, "MOST")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("KLEIN_VDV427".into(), {
                let argv = vec![
                    json!("Klein VDV427-300 impact punchdown, 66/110 blade"),
                    json!(152.0),
                    json!(38.0),
                    json!(25.0),
                    json!("Klein publishes 6 in x 1.5 in x 1 in overall"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("KNIPEX_860180".into(), {
                let argv = vec![
                    json!("KNIPEX 86 01 180 Pliers Wrench"),
                    json!(180.0),
                    json!(46.0),
                    json!(15.0),
                    json!("KNIPEX 180 x 46 x 15 mm; joint thickness 12.0 mm, jaw thickness 8.0 mm"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("VCE_GJ668BL".into(), {
                let argv = vec![
                    json!("VCE GJ668BL modular crimper"),
                    json!(200.0),
                    json!(75.0),
                    json!(30.0),
                    json!("B0BPJ8FJQC package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("KATA_CUTTER".into(), {
                let argv = vec![
                    json!("KATA micro flush cutter"),
                    json!(127.0),
                    json!(40.0),
                    json!(17.0),
                    json!("B0BBML9M2V names a 127 mm tool; the rest is the parcel"),
                    t(vec![g(&e, "EXACT"), g(&e, "MOST"), g(&e, "MOST")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("MUDDER_CUTTER".into(), {
                let argv = vec![
                    json!("Mudder tubing cutter"),
                    json!(80.0),
                    json!(34.0),
                    json!(24.0),
                    json!("B0968K4JRN package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("MASTERCOOL_70025".into(), {
                let argv = vec![
                    json!("MASTERCOOL 70025 capillary tube cutter"),
                    json!(120.0),
                    json!(68.0),
                    json!(21.0),
                    json!("B00AYJ0B7Y carton — MASTERCOOL publishes no figure for the 70025"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("RIDGID_150".into(), {
                let argv = vec![
                    json!("RIDGID 150 constant-swing tubing cutter"),
                    json!(124.0),
                    json!(92.0),
                    json!(41.0),
                    json!("RIDGID publishes 4-7/8 in overall; the rest is B0009W6T8G"),
                    t(vec![g(&e, "EXACT"), g(&e, "MOST"), g(&e, "MOST")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("IFIXIT_TWEEZERS".into(),{let argv=vec![json!("iFixit precision tweezers — extra-fine, angled, blunt"),json!(127.0),json!(12.0),json!(8.0),json!("iFixit publishes the 127 mm length; the rest is one tweezer out of B079K874CQ"),t(vec![g(&e,"EXACT"),g(&e,"MOST"),g(&e,"MOST")])];let kwargs=json!({});call(cx,"_bound","mixed",argv,kwargs,None)?});
            e.insert("T18_TIP".into(), {
                let argv = vec![
                    json!("Hakko / VECO-T T18 soldering tip"),
                    json!(6.5),
                    json!(44.0),
                    json!("the T18 series barrel is 6.5 mm, the fit to an FX-888D's collar"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert("INSERT_TIP".into(), {
                let argv = vec![
                    json!("heat-set insert tip, M2 to M8"),
                    json!(6.5),
                    json!(40.0),
                    json!("the seven tips share the T18 6.5 mm barrel of the iron they screw into"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert("COBALT_DRILL".into(), {
                let argv = vec![
                    json!("Drill Hulk 9/64\" M35 cobalt jobber drill"),
                    b("*", b("/", json!(9.0), json!(64.0)), g(&e, "inch")),
                    b("*", json!(2.875), g(&e, "inch")),
                    json!("ANSI jobber-length 9/64 in; 12 of them from B07XNNNC5Y"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert("PILOT_DRILL".into(), {
                let argv = vec![
                    json!("Mollom hole-saw pilot drill"),
                    b("*", json!(0.25), g(&e, "inch")),
                    json!(95.0),
                    json!("the arbor takes a 1/4 in pilot; length from the set B0BZQ4J5B1"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert("NPT_TAP".into(), {
                let argv = vec![
                    json!("HSS 1/4\"-18 NPT taper pipe tap"),
                    b(
                        "*",
                        b("*", json!(0.421), g(&e, "inch")),
                        b("**", json!(2.0), json!(0.5)),
                    ),
                    b("*", json!(2.44), g(&e, "inch")),
                    json!("ANSI B94.9 1/4-18 NPT: 0.421 in square across flats, 2.44 in overall"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert("TAP_GUIDE".into(), {
                let argv = vec![
                    json!("Brown & Sharpe 599-792-30 spring tap guide"),
                    b("*", json!(0.5), g(&e, "inch")),
                    json!(115.0),
                    json!("B&S publishes the 1/2 in hardened shank; the length is generous"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert(
                "COUNTERSINKS".into(),
                t(seq({
                    let mut e = e.clone();
                    let mut temp7 = Vec::new();
                    for item in seq(t(vec![
                        t(vec![json!("1/4 in"), json!(0.25)]),
                        t(vec![json!("3/8 in"), json!(0.375)]),
                        t(vec![json!("1/2 in"), json!(0.5)]),
                        t(vec![json!("5/8 in"), json!(0.625)]),
                        t(vec![json!("3/4 in"), json!(0.75)]),
                    ])) {
                        {
                            let temp8 = item;
                            e.insert("label".into(), ix(temp8.clone(), json!(0)));
                            e.insert("fraction".into(), ix(temp8.clone(), json!(1)));
                        }
                        temp7.push({
                            let argv = vec![
                                json!(
                                    [
                                        "JNB Pro 82-degree countersink, ".to_owned(),
                                        format_value(g(&e, "label"), "")?,
                                        " head".to_owned()
                                    ]
                                    .concat()
                                ),
                                b("*", g(&e, "fraction"), g(&e, "inch")),
                                json!(70.0),
                                json!(
                                    [
                                        "ANSI 82-degree countersink, ".to_owned(),
                                        format_value(g(&e, "label"), "")?,
                                        " nominal head; the set is B09C4X5R8F".to_owned()
                                    ]
                                    .concat()
                                ),
                            ];
                            let kwargs = json!({});
                            call(cx, "_bound", "bore", argv, kwargs, None)?
                        });
                    }
                    json!(temp7)
                })),
            );
            e.insert("DOWEL_PIN".into(), {
                let argv = vec![
                    json!("POWERTEC 71476 ground dowel pin"),
                    b("*", json!(0.25), g(&e, "inch")),
                    b("*", json!(2.0), g(&e, "inch")),
                    json!("POWERTEC 71476 is a ground 1/4 x 2 in dowel"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "bore", argv, kwargs, None)?
            });
            e.insert("SPADE_BIT".into(), {
                let argv = vec![
                    json!("Bosch DSB1013 spade bit, 1 in x 6 in"),
                    b("*", json!(6.0), g(&e, "inch")),
                    b("*", json!(1.0), g(&e, "inch")),
                    json!(4.0),
                    json!("B001NGPAA0 names a 1 in x 6 in bit; the paddle thickness is generous"),
                    t(vec![g(&e, "EXACT"), g(&e, "EXACT"), g(&e, "MOST")]),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "mixed", argv, kwargs, None)?
            });
            e.insert("HOLE_SAW_ARBOR".into(), {
                let argv = vec![
                    json!("Mollom hole-saw arbor with its pilot fitted"),
                    json!(115.0),
                    json!(30.0),
                    json!(30.0),
                    json!("B0BZQ4J5B1 set — Mollom publishes the saw's cut and no arbor figure"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("FLUX_JAR".into(), {
                let argv = vec![
                    json!("MG Chemicals 8341 flux, 49 g jar"),
                    json!(52.0),
                    json!(52.0),
                    json!(45.0),
                    json!("B005KDEIZ0 package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("FLUX_BOTTLE".into(), {
                let argv = vec![
                    json!("BEEYUIHF no-clean flux, 30 mL"),
                    json!(32.0),
                    json!(32.0),
                    json!(100.0),
                    json!("B0BC1VH4XB package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("FLUX_SYRINGES".into(),{let argv=vec![json!("no-clean flux syringes, 10 cc, four"),json!(34.0),json!(34.0),json!(90.0),json!("a 10 cc Luer syringe is 16 mm across the barrel and 90 mm long; four, two by two")];let kwargs=json!({});call(cx,"_bound","exact",argv,kwargs,None)?});
            e.insert("FLUX_BRUSHES".into(),{let argv=vec![json!("acid flux brushes, 36 standing"),json!(52.0),json!(52.0),json!(152.0),json!("a #2 acid brush is 6 in long on an 8 mm ferrule; 36 of them bundle to 52 mm across")];let kwargs=json!({});call(cx,"_bound","exact",argv,kwargs,None)?});
            e.insert("HEAT_GUN".into(), {
                let argv = vec![
                    json!("QWORK mini heat gun"),
                    json!(66.0),
                    json!(66.0),
                    json!(160.0),
                    json!("B08VW15TK8 package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("HOTEND_SOCKS".into(), {
                let argv = vec![
                    json!("DUROZZLE silicone hotend socks"),
                    json!(8),
                    b("*", b("*", json!(26.0), json!(26.0)), json!(20.0)),
                    json!("B0CZ38MYL1 pack; a H2C sock is about 26 mm square"),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("HOTENDS".into(), {
                let argv = vec![
                    json!("H2C hotends, the four a both-printer swap pulls"),
                    json!(4),
                    b("*", b("*", json!(30.0), json!(30.0)), json!(60.0)),
                    json!("the Bambu H2C hotend body, generous, lying down in the swap well"),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("DEPRESSORS".into(), {
                let argv = vec![
                    json!("JMU 6\" tongue depressors, 100"),
                    json!(100.0),
                    json!(48.0),
                    json!(152.4),
                    json!("a 6 x 3/4 x 1/12 in depressor is a standard size; 100 standing 5 x 20"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("PIGMENT".into(), {
                let argv = vec![
                    json!("BBDINO black silicone pigment, 150 g"),
                    json!(63.5),
                    json!(63.5),
                    json!(88.9),
                    json!("B0FQPGDD49 package"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("MIXING_CUPS".into(), {
                let argv = vec![
                    json!("Pouring Masters 5 oz mixing cups, 50 nested"),
                    json!(82.0),
                    json!(82.0),
                    json!(227.1),
                    json!("B07V6XKZG9 package — the nested column"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "parcel", argv, kwargs, None)?
            });
            e.insert("FLARE_NUTS".into(), {
                let argv = vec![
                    json!("Joywayus brass 1/4\" SAE 45-degree flare nuts"),
                    json!(5),
                    {
                        let argv = vec![json!(20.0), json!(20.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("a 1/4 in SAE flare nut on a 7/16-20 thread is 20 mm across corners"),
                ];
                let kwargs = object(vec![("nest".into(), json!(0.9))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("SLIP_COUPLINGS".into(), {
                let argv = vec![
                    json!("1/4\" OD ACR copper slip couplings"),
                    json!(10),
                    {
                        let argv = vec![json!(7.5), json!(16.0)];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!("B0FH549N6D states a 6.3 mm bore, 16 mm long, 0.6 mm wall"),
                ];
                let kwargs = object(vec![("nest".into(), json!(0.9))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            e.insert("FILTER_DRIER".into(), {
                let argv = vec![
                    json!("Supco D111 filter-drier"),
                    json!(38.1),
                    json!(63.5),
                    json!(88.9),
                    json!("B00DM8KGXS states 1.5 x 2.5 x 3.5 in in its title"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("PIERCING_VALVE".into(), {
                let argv = vec![
                    json!("Supco BPV31 bullet-piercing valve"),
                    json!(50.8),
                    json!(50.8),
                    json!(44.5),
                    json!("distributor spec tables give 2 x 2 x 1-3/4 in"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("NOGA".into(), {
                let argv = vec![
                    json!("Noga NG8150 deburr tool, NogaGrip-1 handle"),
                    json!(155.0),
                    json!(28.0),
                    json!(28.0),
                    json!("Noga publishes the NG8150's 125 x 28 mm handle; the blade adds 30 mm"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
            e.insert("NPT_DIE".into(), {
                let argv = vec![
                    json!("Drill America 1-1/2\" OD round adjustable NPT die"),
                    b("*", json!(1.5), g(&e, "inch")),
                    b("*", json!(1.5), g(&e, "inch")),
                    json!(18.0),
                    json!("the die is 1-1/2 in OD by its own designation; 18 mm thick is generous"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "exact", argv, kwargs, None)?
            });
        }
        "holders" => {
            e.insert("ROOT".into(), path(cx, ""));
            e.insert("_repo_root".into(), path(cx, ""));
            e.insert("_repo".into(), path(cx, ""));
            if let Some(input) = cx.inputs.get(module).and_then(Value::as_object) {
                e.extend(input.iter().map(|(k, v)| (k.clone(), v.clone())));
            }
            e.insert(
                "HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_HERE".into(),
                path(cx, "hardware/printed-parts/shop-storage"),
            );
            e.insert(
                "_here".into(),
                path(cx, "hardware/printed-parts/shop-storage/holders.py"),
            );
            e.insert("_hw".into(), path(cx, "hardware"));
            e.insert("HW".into(), path(cx, "hardware"));
            e.insert("EXACT".into(), attr(cx, "_bound", "EXACT")?);
            e.insert("DOCKS".into(),json!([({let argv=vec![json!("dock-3x3"),json!("dock"),json!(3),json!(3),json!(0)];let kwargs=object(vec![("note".into(),json!("The bench plate. Print as many as the bench has room for; any baseplate docks any holder."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?})]));
            e.insert("CRADLES".into(),json!([({let argv=vec![json!("reel-cradle"),json!("cradle"),json!(3),json!(3),json!(6)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","WIRE_REEL")?,attr(cx,"catalog","RIBBON_REEL")?,attr(cx,"catalog","KAPTON_ROLLS")?])),("note".into(),json!("A 90-degree V. A reel rests on two lines and centres itself between them at any radius, and turns as the wire is pulled. Nothing here is cut to a reel's diameter or to its width."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("roll-cradle"),json!("cradle"),json!(2),json!(2),json!(5)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","SOLDER_ROLL")?,attr(cx,"catalog","SOLDER_POCKET")?,attr(cx,"catalog","BRAID_BOBBIN")?,attr(cx,"catalog","PTFE_TAPE")?])),("note".into(),json!("The same V at bench-roll size: solder off the reel, braid off the bobbin, tape off the roll."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("reel-spacer"),json!("spacer"),json!(3),json!(3),json!(6)];let kwargs=object(vec![("note".into(),json!("Drops into the reel cradle's trough beside a narrow reel and takes up its run. Print as many as the slack wants.")),("opts".into(),object(vec![(json!("width"),json!(20.0))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("roll-spacer"),json!("spacer"),json!(2),json!(2),json!(5)];let kwargs=object(vec![("note".into(),json!("The roll cradle's spacer.")),("opts".into(),object(vec![(json!("width"),json!(12.0))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?})]));
            e.insert("COMBS".into(),json!([({let argv=vec![json!("crimp-comb"),json!("comb"),json!(3),json!(2),json!(9)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","SN2549")?,attr(cx,"catalog","HS9327")?,attr(cx,"catalog","PRECIVA")?])),("note".into(),json!("The three ratcheting crimpers, head down. Each slot is cut to its own tool, so the SN-2549 does not rattle in a mouth sized for the Preciva."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("strip-comb"),json!("comb"),json!(3),json!(3),json!(8)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","KLEIN_11063W")?,attr(cx,"catalog","KLEIN_11057")?,attr(cx,"catalog","VCE_GJ668BL")?])),("note".into(),json!("The two strippers and the modular crimper."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("punch-comb"),json!("comb"),json!(2),json!(2),json!(8)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","KLEIN_VDV427")?,attr(cx,"catalog","MASTERCOOL_70025")?])),("note".into(),json!("The punchdown and the capillary cutter — two tools whose makers publish between them one usable figure."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("cut-comb"),json!("comb"),json!(2),json!(2),json!(7)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","KATA_CUTTER")?,attr(cx,"catalog","KATA_CUTTER")?,attr(cx,"catalog","MUDDER_CUTTER")?])),("note".into(),json!("Both flush cutters and the tube cutter."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("fine-comb"),json!("comb"),json!(2),json!(1),json!(8)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","IFIXIT_TWEEZERS")?,attr(cx,"catalog","IFIXIT_TWEEZERS")?,attr(cx,"catalog","IFIXIT_TWEEZERS")?])),("note".into(),json!("The three iFixit tweezers, points down to the root of the taper.")),("opts".into(),object(vec![(json!("root"),json!(3.0)),(json!("taper"),json!(10.0))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("tube-comb"),json!("comb"),json!(3),json!(3),json!(9)];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","KNIPEX_860180")?,attr(cx,"catalog","RIDGID_150")?])),("note".into(),json!("The pliers wrench and the tubing cutter. KNIPEX publishes 180 x 46 x 15 mm and RIDGID publishes a length, so one slot is cut to a drawing and the other to a parcel, 26 mm wider."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?})]));
            e.insert("INDEXES".into(),json!([({let argv=vec![json!("tip-index"),json!("index"),json!(3),json!(2),json!(5)];let kwargs=object(vec![("note".into(),json!("Twenty T18 soldering tips and the seven heat-set insert tips that share their barrel. One bore for all twenty-seven: the README's table is what tells them apart.")),("opts".into(),object(vec![(json!("rows"),json!([(json!([(t(vec![attr(cx,"catalog","T18_TIP")?,json!(10)]))])),(json!([(t(vec![attr(cx,"catalog","T18_TIP")?,json!(10)]))])),(json!([(t(vec![attr(cx,"catalog","INSERT_TIP")?,json!(7)]))]))]))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("drill-index"),json!("index"),json!(3),json!(3),json!(5)];let kwargs=object(vec![("note".into(),json!("The drill-press station. Countersinks stand head down — a head is a nominal inch fraction — and everything else shank down.")),("opts".into(),object(vec![(json!("rows"),json!([(json!([(t(vec![attr(cx,"catalog","COBALT_DRILL")?,json!(12)]))])),(json!([(t(vec![attr(cx,"catalog","PILOT_DRILL")?,json!(2)])),(t(vec![attr(cx,"catalog","TAP_GUIDE")?,json!(1)]))])),(json!([(t(vec![attr(cx,"catalog","NPT_TAP")?,json!(3)]))])),({let mut e=e.clone();let mut temp1=Vec::new();for item in seq(attr(cx,"catalog","COUNTERSINKS")?) {e.insert("cs".into(),item);temp1.push(t(vec![g(&e,"cs"),json!(1)]));}json!(temp1)})]))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("dowel-index"),json!("index"),json!(2),json!(1),json!(5)];let kwargs=object(vec![("note".into(),json!("Ten ground dowel pins, points up.")),("opts".into(),object(vec![(json!("rows"),json!([(json!([(t(vec![attr(cx,"catalog","DOWEL_PIN")?,json!(5)]))])),(json!([(t(vec![attr(cx,"catalog","DOWEL_PIN")?,json!(5)]))]))]))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?})]));
            e.insert("TUBS".into(),json!([({let argv=vec![json!("m3-tub"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","M3X25")?,attr(cx,"catalog","M3X12SS")?,attr(cx,"catalog","M3X12")?,attr(cx,"catalog","M3X10")?,attr(cx,"catalog","M3X8")?])),("note".into(),json!("The five M3 lengths. The two M3 x 12 troughs are adjacent and their contents are not interchangeable: 304 SS closes the wet reservoir caps, black oxide bolts the dry above-counter plate.")),("opts".into(),object(vec![(json!("length_div"),json!(4))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("m5-tub"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","M5X10")?,attr(cx,"catalog","M5WASHER")?,attr(cx,"catalog","RUTHEX_M5")?])),("note".into(),json!("The compressor floor stack.")),("opts".into(),object(vec![(json!("length_div"),json!(2))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("insert-tub"),json!("tub"),json!(3),json!(1),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","RUTHEX_M3")?,attr(cx,"catalog","RUTHEX_M3S")?,attr(cx,"catalog","RUTHEX_M2")?])),("note".into(),json!("LABEL THIS ONE FIRST. The long and short M3 share a knurl and a hole and differ only in body length; pressed into the wrong station the short one is a weaker joint that looks identical.")),("opts".into(),object(vec![(json!("length_div"),json!(2))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("small-tub"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","M2X6")?,attr(cx,"catalog","ULPM3X6")?,attr(cx,"catalog","ULPM3X8")?,attr(cx,"catalog","MAGNETS")?,attr(cx,"catalog","MEMBRANES")?])),("note".into(),json!("M2, the two ultra-low-profile M3 lengths, and the two that are not screws. The sixth compartment stands empty for whatever is in play.")),("opts".into(),object(vec![(json!("length_div"),json!(2)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("ferrule-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),attr(cx,"catalog","FERRULES")?),("note".into(),json!("Six DIN 46228-4 cross-sections. The machine's largest conductor is 16 AWG, so the kit's 4 mm2 and up stay in the kit's own case.")),("opts".into(),object(vec![(json!("length_div"),json!(2)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("shrink-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),attr(cx,"catalog","SHRINK")?),("note".into(),json!("Eleven sizes of 2:1 sleeving decanted into six bands; a band's compartment is sized on the widest sleeve in it.")),("opts".into(),object(vec![(json!("length_div"),json!(2)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("terminal-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),attr(cx,"catalog","TERMINALS")?),("note".into(),json!("Push-ons and rings, the single-gauge packs and the mixed kits decanted beside them.")),("opts".into(),object(vec![(json!("length_div"),json!(2)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("lever-tub"),json!("tub"),json!(3),json!(1),Value::Null];let kwargs=object(vec![("takes".into(),attr(cx,"catalog","LEVERS")?),("note".into(),json!("WAGO 221 in three widths.")),("opts".into(),object(vec![(json!("length_div"),json!(2))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("tie-tub"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),attr(cx,"catalog","TIES")?),("note".into(),json!("Zip ties in three lengths; the 6 in and 8 in lie doubled back.")),("opts".into(),object(vec![(json!("length_div"),json!(2))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("xh-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),b("+",t(vec![attr(cx,"catalog","XH_CONTACTS")?,attr(cx,"catalog","XH_LEADS")?]),attr(cx,"catalog","XH_HOUSINGS")?)),("note".into(),json!("The JST XH station: contacts, pre-crimped leads, and the seven pole counts. Every figure here is the XH series drawing's.")),("opts".into(),object(vec![(json!("length_div"),json!(2)),(json!("width_div"),json!(2))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("keystone-tub"),json!("tub"),json!(2),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","RJ11_JACKS")?,attr(cx,"catalog","RJ11_PLUGS")?])),("note".into(),json!("RJ11 6P4C jacks and plugs. 6P4C is a standard and the keystone form factor is a standard, so neither figure is a parcel's.")),("opts".into(),object(vec![(json!("length_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("junction-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","UNION_TEES")?,attr(cx,"catalog","UNION_ELBOWS")?])),("note".into(),json!("Thirty union tees and forty union elbows, on John Guest's own drawings.")),("opts".into(),object(vec![(json!("length_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("bulkhead-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","BULKHEADS")?,attr(cx,"catalog","NEOFIT_BULKHEADS")?,attr(cx,"catalog","PURESEC_ELBOWS")?,attr(cx,"catalog","BALL_VALVES")?])),("note".into(),json!("Everything that passes a wall, and the valves that sit in line with it.")),("opts".into(),object(vec![(json!("length_div"),json!(1)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("adapter-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","MALE_CONNECTORS")?,attr(cx,"catalog","FEMALE_ADAPTERS")?,attr(cx,"catalog","FLARE_ADAPTERS")?,attr(cx,"catalog","PNEUMATIC")?])),("note".into(),json!("Thread to tube, in both directions.")),("opts".into(),object(vec![(json!("length_div"),json!(1)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("npt-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","CHECK_VALVES")?,attr(cx,"catalog","COUPLINGS")?,attr(cx,"catalog","BARBS")?,attr(cx,"catalog","BRASS_FLARE")?])),("note".into(),json!("The NPT stock. The regulator and the relief valve stand in the pressure-tub beside it.")),("opts".into(),object(vec![(json!("length_div"),json!(1)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("pressure-tub"),json!("tub"),json!(2),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","REGULATOR")?,attr(cx,"catalog","RELIEF_VALVE")?])),("note".into(),json!("The two bodies that stand on end.")),("opts".into(),object(vec![(json!("length_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("stock-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","TWO_WAY")?,attr(cx,"catalog","CLAMPS")?,attr(cx,"catalog","STIFFENERS")?])),("note".into(),json!("Dividers, clamps and stiffeners — the bulk of the tube bench.")),("opts".into(),object(vec![(json!("length_div"),json!(2))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("copper-tub"),json!("tub"),json!(3),json!(1),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","FLARE_NUTS")?,attr(cx,"catalog","SLIP_COUPLINGS")?])),("note".into(),json!("The flare nuts and slip couplings the copper bench works through.")),("opts".into(),object(vec![(json!("length_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("service-tub"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","FILTER_DRIER")?,attr(cx,"catalog","PIERCING_VALVE")?])),("note".into(),json!("The loop-service spare and one piercing valve per appliance, both standing.")),("opts".into(),object(vec![(json!("length_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("flux-tub"),json!("tub"),json!(3),json!(3),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","FLUX_JAR")?,attr(cx,"catalog","FLUX_BOTTLE")?,attr(cx,"catalog","FLUX_SYRINGES")?])),("note".into(),json!("The wet end of the solder bench: the jar, the bottle and the four syringes, all standing. The fourth compartment takes whatever is open.")),("opts".into(),object(vec![(json!("length_div"),json!(1)),(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("brush-quiver"),json!("tub"),json!(2),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","FLUX_BRUSHES")?])),("note".into(),json!("Thirty-six acid brushes standing. They come out of the flux tub because a 152 mm brush would put a 45 mm jar at the bottom of a 158 mm well."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("heat-gun-tub"),json!("tub"),json!(2),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","HEAT_GUN")?])),("note".into(),json!("The mini heat gun, nozzle down."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("deburr-tub"),json!("tub"),json!(4),json!(1),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","NOGA")?])),("note".into(),json!("The Noga NG8150, lying down."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("saw-tub"),json!("tub"),json!(4),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","HOLE_SAW_ARBOR")?,attr(cx,"catalog","SPADE_BIT")?])),("note".into(),json!("The saw set lies down: the arbor's flange and the spade bit's paddle are both wider than their shanks, and a bore cut to a shank leaves the wide end to foul its neighbours. The bit is 6 in long, which is what makes this the one four-unit tub.")),("opts".into(),object(vec![(json!("width_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("die-tub"),json!("tub"),json!(2),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","NPT_DIE")?])),("note".into(),json!("The 1-1/2 in round adjustable NPT die, lying flat."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("hotend-tub"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","HOTEND_SOCKS")?,attr(cx,"catalog","HOTENDS")?])),("note".into(),json!("The silicone socks, and the swap well a both-printer change pulls into.")),("opts".into(),object(vec![(json!("length_div"),json!(1))]))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("depressor-quiver"),json!("tub"),json!(3),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","DEPRESSORS")?])),("note".into(),json!("A hundred 6 in depressors standing. A depressor is a standard size and the quiver is cut to the bundle."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?}),({let argv=vec![json!("pigment-tub"),json!("tub"),json!(2),json!(2),Value::Null];let kwargs=object(vec![("takes".into(),t(vec![attr(cx,"catalog","PIGMENT")?])),("note".into(),json!("The silicone pigment. The two-part kits, the aerosols and the 32 oz cups all stand wider than a footprint and stay at the pour bench."))]);call(cx,"holders","Holder",argv,kwargs,Some(&e))?})]));
            e.insert(
                "HOLDERS".into(),
                b(
                    "+",
                    b(
                        "+",
                        b(
                            "+",
                            b("+", g(&e, "DOCKS"), g(&e, "CRADLES")),
                            g(&e, "COMBS"),
                        ),
                        g(&e, "INDEXES"),
                    ),
                    g(&e, "TUBS"),
                ),
            );
        }
        other => bail!("Unknown reference module {other}"),
    };
    cx.cache.insert(module.into(), e.clone());
    Ok(e)
}
pub(super) fn call(
    cx: &mut Context,
    module: &str,
    name: &str,
    args: Vec<Value>,
    kwargs: Value,
    scope: Option<&Env>,
) -> Result<Value> {
    let mut e = if let Some(v) = scope {
        v.clone()
    } else {
        globals(cx, module)?
    };
    if let Some(fields) = cx.overrides.get(module).and_then(Value::as_object) {
        e.extend(fields.iter().map(|(k, v)| (k.clone(), v.clone())));
    }
    match (module, name) {
        ("asse1022_assembly", "flow_axis") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    json!(0.0),
                    attr(cx, "multiplex_asse1022", "BODY_CENTER_Z")?,
                ]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("asse1022_assembly", "ports") => {
            return Ok({
                let mut e = e.clone();
                let mut temp3 = Vec::new();
                for item in seq(g(&e, "TERMINALS")) {
                    e.insert("name".into(), item);
                    temp3.push((g(&e, "name"), {
                        let argv = vec![g(&e, "name")];
                        let kwargs = json!({});
                        call(cx, "asse1022_assembly", "port", argv, kwargs, Some(&e))?
                    }));
                }
                object(temp3)
            });
            Ok(Value::Null)
        }
        ("asse1022_threaded_chain", "parameters") => {
            return Ok(ix(
                parse_json(read_file(
                    cx,
                    b("/", g(&e, "HERE"), json!("reference-parameters.json")),
                )?)?,
                json!("components"),
            ));
            Ok(Value::Null)
        }
        ("asse1022_threaded_chain", "ports") => {
            e.insert("data".into(), {
                let argv = vec![];
                let kwargs = json!({});
                call(
                    cx,
                    "asse1022_threaded_chain",
                    "parameters",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            e.insert(
                "result".into(),
                object(vec![(json!("vent"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "multiplex_asse1022", "vent", argv, kwargs, None)?
                })]),
            );
            e.insert("inlet".into(), ix(g(&e, "data"), json!("pp010822e")));
            e.insert(
                "station".into(),
                ix(
                    ix(ix(g(&e, "inlet"), json!("visible_profile")), json!(0)),
                    json!(0),
                ),
            );
            {
                let temp1 = t(vec![
                    ix(g(&e, "inlet"), json!("rotation")),
                    ix(g(&e, "inlet"), json!("origin_mm")),
                ]);
                e.insert("r".into(), ix(temp1.clone(), json!(0)));
                e.insert("t".into(), ix(temp1.clone(), json!(1)));
            }
            {
                let key = json!("inlet");
                let temp4 = t(vec![
                    t(seq({
                        let mut e = e.clone();
                        let mut temp2 = Vec::new();
                        for item in seq(builtin("range", vec![json!(3)])) {
                            e.insert("i".into(), item);
                            temp2.push(b(
                                "+",
                                ix(g(&e, "t"), g(&e, "i")),
                                b(
                                    "*",
                                    ix(ix(g(&e, "r"), g(&e, "i")), json!(0)),
                                    g(&e, "station"),
                                ),
                            ));
                        }
                        json!(temp2)
                    })),
                    t(seq({
                        let mut e = e.clone();
                        let mut temp3 = Vec::new();
                        for item in seq(builtin("range", vec![json!(3)])) {
                            e.insert("i".into(), item);
                            temp3.push(u("-", ix(ix(g(&e, "r"), g(&e, "i")), json!(0))));
                        }
                        json!(temp3)
                    })),
                ]);
                setitem(&mut e, "result", key, temp4);
            }
            e.insert("tee".into(), ix(g(&e, "data"), json!("atbu444-e")));
            {
                let temp5 = t(vec![
                    ix(g(&e, "tee"), json!("rotation")),
                    ix(g(&e, "tee"), json!("origin_mm")),
                ]);
                e.insert("r".into(), ix(temp5.clone(), json!(0)));
                e.insert("t".into(), ix(temp5.clone(), json!(1)));
            }
            for item in seq(json!([
                (t(vec![json!(1), json!("plus")])),
                (t(vec![u("-", json!(1)), json!("minus")]))
            ])) {
                {
                    let temp6 = item;
                    e.insert("sign".into(), ix(temp6.clone(), json!(0)));
                    e.insert("name".into(), ix(temp6.clone(), json!(1)));
                }
                e.insert(
                    "reach".into(),
                    ix(
                        ix(
                            ix(ix(g(&e, "tee"), json!("run_profiles")), g(&e, "name")),
                            u("-", json!(1)),
                        ),
                        json!(0),
                    ),
                );
                {
                    let key = b("+", json!("outlet_"), g(&e, "name"));
                    let temp9 = t(vec![
                        t(seq({
                            let mut e = e.clone();
                            let mut temp7 = Vec::new();
                            for item in seq(builtin("range", vec![json!(3)])) {
                                e.insert("i".into(), item);
                                temp7.push(b(
                                    "+",
                                    ix(g(&e, "t"), g(&e, "i")),
                                    b(
                                        "*",
                                        b(
                                            "*",
                                            g(&e, "sign"),
                                            ix(ix(g(&e, "r"), g(&e, "i")), json!(1)),
                                        ),
                                        g(&e, "reach"),
                                    ),
                                ));
                            }
                            json!(temp7)
                        })),
                        t(seq({
                            let mut e = e.clone();
                            let mut temp8 = Vec::new();
                            for item in seq(builtin("range", vec![json!(3)])) {
                                e.insert("i".into(), item);
                                temp8.push(b(
                                    "*",
                                    g(&e, "sign"),
                                    ix(ix(g(&e, "r"), g(&e, "i")), json!(1)),
                                ));
                            }
                            json!(temp8)
                        })),
                    ]);
                    setitem(&mut e, "result", key, temp9);
                }
            }
            return Ok(g(&e, "result"));
            Ok(Value::Null)
        }
        ("beduan_solenoid", "mounting_centers") => {
            return Ok(t(seq({
                let mut e = e.clone();
                let mut temp12 = Vec::new();
                for item in seq(t(vec![u("-", json!(1)), json!(1)])) {
                    e.insert("sx".into(), item);
                    for item in seq(t(vec![u("-", json!(1)), json!(1)])) {
                        e.insert("sy".into(), item);
                        temp12.push(t(vec![
                            b("*", g(&e, "sx"), g(&e, "corner_inset_x")),
                            b("*", g(&e, "sy"), g(&e, "corner_inset_y")),
                        ]));
                    }
                }
                json!(temp12)
            })));
            Ok(Value::Null)
        }
        ("beduan_solenoid", "inlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("/", u("-", g(&e, "port_length")), json!(2)),
                    g(&e, "port_center_z"),
                ]),
                t(vec![json!(0.0), u("-", json!(1.0)), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("beduan_solenoid", "outlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("/", g(&e, "port_length"), json!(2)),
                    g(&e, "port_center_z"),
                ]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("branch_stem_tees", "specification") => {
            e.insert(
                "variant".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "variant"))
                    .unwrap_or_else(|| json!("neofit")),
            );
            return Ok(ix(
                ix(
                    parse_json(read_file(
                        cx,
                        b("/", g(&e, "HERE"), json!("dimensions.json")),
                    )?)?,
                    json!("variants"),
                ),
                g(&e, "variant"),
            ));
            Ok(Value::Null)
        }
        ("branch_stem_tees", "stations") => {
            e.insert(
                "variant".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "variant"))
                    .unwrap_or_else(|| json!("neofit")),
            );
            return Ok(ix(
                {
                    let argv = vec![g(&e, "variant")];
                    let kwargs = json!({});
                    call(
                        cx,
                        "branch_stem_tees",
                        "specification",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                },
                json!("ports"),
            ));
            Ok(Value::Null)
        }
        ("compressor", "mount_pattern") => {
            return Ok({
                let mut e = e.clone();
                let mut temp1 = Vec::new();
                for item in seq(t(vec![u("-", json!(1.0)), json!(1.0)])) {
                    e.insert("sx".into(), item);
                    for item in seq(t(vec![u("-", json!(1.0)), json!(1.0)])) {
                        e.insert("sy".into(), item);
                        temp1.push(t(vec![
                            b("/", b("*", g(&e, "sx"), g(&e, "MOUNT_PITCH_X")), json!(2.0)),
                            b("/", b("*", g(&e, "sy"), g(&e, "MOUNT_PITCH_Y")), json!(2.0)),
                        ]));
                    }
                }
                json!(temp1)
            });
            Ok(Value::Null)
        }
        ("compressor", "power_face") => {
            return Ok(t(vec![
                t(vec![
                    b("/", g(&e, "POWER_X"), json!(2.0)),
                    b("+", g(&e, "POWER_Y0"), b("/", g(&e, "POWER_Y"), json!(2.0))),
                    b(
                        "/",
                        b("+", g(&e, "POWER_Z0"), g(&e, "POWER_Z1")),
                        json!(2.0),
                    ),
                ]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("compressor", "process_tube") => {
            return Ok(t(vec![
                t(vec![
                    b(
                        "-",
                        b("/", u("-", g(&e, "SHELL_X")), json!(2.0)),
                        g(&e, "PROCESS_CLAMP"),
                    ),
                    g(&e, "SHELL_OFFSET_Y"),
                    g(&e, "PROCESS_Z"),
                ]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("compressor", "stations") => {
            return Ok(object(vec![
                (
                    json!("refrig-discharge"),
                    t(vec![
                        t(vec![
                            b("/", g(&e, "SHELL_X"), json!(2.0)),
                            g(&e, "SHELL_OFFSET_Y"),
                            g(&e, "DISCHARGE_Z"),
                        ]),
                        t(vec![json!(1.0), json!(0.0), json!(0.0)]),
                    ]),
                ),
                (
                    json!("refrig-suction"),
                    t(vec![
                        t(vec![
                            b("/", u("-", g(&e, "SHELL_X")), json!(2.0)),
                            g(&e, "SHELL_OFFSET_Y"),
                            g(&e, "SUCTION_Z"),
                        ]),
                        t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
                    ]),
                ),
            ]));
            Ok(Value::Null)
        }
        ("compressor", "stations_hold") => {
            for item in seq(method(
                {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "compressor", "stations", argv, kwargs, Some(&e))?
                },
                "items",
                vec![],
            )) {
                {
                    let temp2 = item;
                    e.insert("name".into(), ix(temp2.clone(), json!(0)));
                    {
                        let temp3 = ix(temp2.clone(), json!(1));
                        e.insert("pos".into(), ix(temp3.clone(), json!(0)));
                        e.insert("_axis".into(), ix(temp3.clone(), json!(1)));
                    }
                }
                if truth(&u(
                    "not",
                    json!(
                        compare("<=", g(&e, "BASE_Z"), ix(g(&e, "pos"), json!(2)))
                            && compare("<=", ix(g(&e, "pos"), json!(2)), g(&e, "OVERALL_H"))
                    ),
                )) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "compressor ".to_owned(),
                                format_value(g(&e, "name"), "")?,
                                " stands at z = ".to_owned(),
                                format_value(ix(g(&e, "pos"), json!(2)), "g")?,
                                ", outside the shell's own ".to_owned(),
                                format_value(g(&e, "BASE_Z"), "g")?,
                                "..".to_owned(),
                                format_value(g(&e, "OVERALL_H"), "g")?,
                                " — the stub has left the can it is brazed into.".to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
            }
            Ok(Value::Null)
        }
        ("compressor", "power_hold") => {
            if truth(&json!(compare(
                ">",
                builtin(
                    "abs",
                    vec![b(
                        "-",
                        b("+", g(&e, "POWER_Y0"), g(&e, "POWER_Y")),
                        g(&e, "SHELL_TANGENT_Y")
                    )]
                ),
                json!(1e-09)
            ))) {
                bail!("{}",string(&json!(["the box runs y ".to_owned(),format_value(g(&e,"POWER_Y0"),"g")?,"..".to_owned(),format_value(b("+",g(&e,"POWER_Y0"),g(&e,"POWER_Y")),"g")?," and the plate's long reach ends at the shell's tangent y = ".to_owned(),format_value(g(&e,"SHELL_TANGENT_Y"),"g")?," — the box no longer fills the reach the shell's own offset opened for it.".to_owned()].concat())));
            } else {
            }
            if truth(&json!(compare(
                "<=",
                g(&e, "POWER_Z0"),
                b("+", g(&e, "BASE_Z"), json!(1e-09))
            ))) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            "the box's underside stands at z ".to_owned(),
                            format_value(g(&e, "POWER_Z0"), "g")?,
                            " against the plate's crown at ".to_owned(),
                            format_value(g(&e, "BASE_Z"), "g")?,
                            " — it is sitting on the plate rather than hanging off the shell."
                                .to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            for item in seq({
                let argv = vec![];
                let kwargs = json!({});
                call(cx, "compressor", "mount_pattern", argv, kwargs, Some(&e))?
            }) {
                {
                    let temp4 = item;
                    e.insert("x".into(), ix(temp4.clone(), json!(0)));
                    e.insert("y".into(), ix(temp4.clone(), json!(1)));
                }
                if truth(&{
                    let value = json!(compare(
                        "<",
                        builtin("abs", vec![g(&e, "x")]),
                        b(
                            "+",
                            b("/", g(&e, "POWER_X"), json!(2.0)),
                            b("/", g(&e, "MOUNT_D"), json!(2.0))
                        )
                    ));
                    if truth(&value) {
                        json!(
                            compare("<=", g(&e, "POWER_Y0"), g(&e, "y"))
                                && compare(
                                    "<=",
                                    g(&e, "y"),
                                    b("+", g(&e, "POWER_Y0"), g(&e, "POWER_Y"))
                                )
                        )
                    } else {
                        value
                    }
                }) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "the mount at (".to_owned(),
                                format_value(g(&e, "x"), "g")?,
                                ", ".to_owned(),
                                format_value(g(&e, "y"), "g")?,
                                ") stands under the box — a Ø".to_owned(),
                                format_value(g(&e, "MOUNT_D"), "g")?,
                                " hole ".to_owned(),
                                format_value(
                                    b(
                                        "-",
                                        builtin("abs", vec![g(&e, "x")]),
                                        b("/", g(&e, "POWER_X"), json!(2.0))
                                    ),
                                    "g"
                                )?,
                                " outboard of a box face is not a hole a driver reaches."
                                    .to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
            }
            Ok(Value::Null)
        }
        ("compressor", "mounts_hold") => {
            if truth(&json!(compare("<", g(&e, "MOUNT_LIGAMENT"), json!(0.0)))) {
                bail!("{}",string(&json!(["a Ø".to_owned(),format_value(g(&e,"MOUNT_D"),"g")?," hole inset ".to_owned(),format_value(g(&e,"MOUNT_INSET"),"g")?," breaks out of the plate's own edge by ".to_owned(),format_value(u("-",g(&e,"MOUNT_LIGAMENT")),"g")?," — that is an open slot, and the donor's plate is bolted through closed holes.".to_owned()].concat())));
            } else {
            }
            for item in seq({
                let argv = vec![];
                let kwargs = json!({});
                call(cx, "compressor", "mount_pattern", argv, kwargs, Some(&e))?
            }) {
                {
                    let temp5 = item;
                    e.insert("x".into(), ix(temp5.clone(), json!(0)));
                    e.insert("y".into(), ix(temp5.clone(), json!(1)));
                }
                if truth(&json!(compare(
                    ">=",
                    builtin("abs", vec![g(&e, "x")]),
                    b("/", g(&e, "SHELL_X"), json!(2.0))
                ))) {
                    continue;
                } else {
                }
                e.insert(
                    "half".into(),
                    b(
                        "*",
                        b("/", g(&e, "SHELL_Y"), json!(2.0)),
                        math_fn(
                            "sqrt",
                            vec![b(
                                "-",
                                json!(1.0),
                                b(
                                    "**",
                                    b("/", g(&e, "x"), b("/", g(&e, "SHELL_X"), json!(2.0))),
                                    json!(2),
                                ),
                            )],
                        ),
                    ),
                );
                if truth(&json!(compare(
                    "<",
                    builtin("abs", vec![b("-", g(&e, "y"), g(&e, "SHELL_OFFSET_Y"))]),
                    g(&e, "half")
                ))) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "the mount at (".to_owned(),
                                format_value(g(&e, "x"), "g")?,
                                ", ".to_owned(),
                                format_value(g(&e, "y"), "g")?,
                                ") stands under the shell's own belly — the shell reaches "
                                    .to_owned(),
                                format_value(b("-", g(&e, "SHELL_OFFSET_Y"), g(&e, "half")), "g")?,
                                "..".to_owned(),
                                format_value(b("+", g(&e, "SHELL_OFFSET_Y"), g(&e, "half")), "g")?,
                                " on Y at that X, and a bolt cannot be driven through it."
                                    .to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
            }
            Ok(Value::Null)
        }
        ("compressor", "_docvars") => {
            e.insert(
                "plain".into(),
                t(vec![
                    json!("BASE_X"),
                    json!("BASE_Y"),
                    json!("BASE_Z"),
                    json!("SHELL_X"),
                    json!("SHELL_Y"),
                    json!("SHELL_Z"),
                    json!("SHELL_OFFSET_Y"),
                    json!("MOUNT_D"),
                    json!("MOUNT_INSET"),
                    json!("OVERALL_H"),
                    json!("MOUNT_PITCH_X"),
                    json!("MOUNT_PITCH_Y"),
                    json!("SHELL_OVERHANG_X"),
                    json!("PLATE_REACH_LONG"),
                    json!("PLATE_REACH_SHORT"),
                    json!("MOUNT_LIGAMENT"),
                    json!("POWER_X"),
                    json!("POWER_Y"),
                    json!("POWER_Z"),
                    json!("POWER_Z0"),
                    json!("POWER_Z1"),
                    json!("SHELL_TANGENT_Y"),
                    json!("POWER_FLANK_REACH"),
                    json!("PROCESS_Z"),
                    json!("PROCESS_CLAMP"),
                    json!("PROCESS_OVER_SUCTION"),
                ]),
            );
            return Ok({
                let mut e = e.clone();
                let mut temp6 = Vec::new();
                for item in seq(g(&e, "plain")) {
                    e.insert("name".into(), item);
                    temp6.push((
                        g(&e, "name"),
                        json!([format_value(ix(json!(e), g(&e, "name")), "g")?].concat()),
                    ));
                }
                object(temp6)
            });
            Ok(Value::Null)
        }
        ("condenser_block", "mount_xy") => {
            return Ok(t(vec![
                g(&e, "MOUNT_IN_INTAKE"),
                b("-", g(&e, "FACE_A"), g(&e, "MOUNT_IN_AFT")),
            ]));
            Ok(Value::Null)
        }
        ("condenser_block", "recess_y") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "RECESS_Y")]),
                t(vec![
                    b("-", g(&e, "FACE_A"), g(&e, "RECESS_Y")),
                    g(&e, "FACE_A"),
                ]),
            ]));
            Ok(Value::Null)
        }
        ("condenser_block", "flange_z") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "PLATE_T")]),
                t(vec![
                    b("-", g(&e, "FACE_B"), g(&e, "PLATE_T")),
                    g(&e, "FACE_B"),
                ]),
            ]));
            Ok(Value::Null)
        }
        ("condenser_block", "stations") => {
            return Ok(object(vec![
                (
                    json!("refrig-inlet"),
                    t(vec![
                        t(vec![json!(0.0), json!(87.0), json!(66.0)]),
                        t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
                    ]),
                ),
                (
                    json!("refrig-outlet"),
                    t(vec![
                        t(vec![json!(33.0), g(&e, "FACE_A"), json!(38.75)]),
                        t(vec![json!(0.0), json!(1.0), json!(0.0)]),
                    ]),
                ),
                (
                    json!("fan-power"),
                    t(vec![
                        t(vec![
                            g(&e, "AIRFLOW"),
                            json!(30.0),
                            b("/", g(&e, "FACE_B"), json!(2.0)),
                        ]),
                        t(vec![json!(1.0), json!(0.0), json!(0.0)]),
                    ]),
                ),
            ]));
            Ok(Value::Null)
        }
        ("condenser_block", "mounts") => {
            {
                let temp1 = {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "condenser_block", "mount_xy", argv, kwargs, Some(&e))?
                };
                e.insert("x".into(), ix(temp1.clone(), json!(0)));
                e.insert("y".into(), ix(temp1.clone(), json!(1)));
            }
            return Ok(object(vec![
                (
                    json!("mount-base"),
                    t(vec![
                        t(vec![g(&e, "x"), g(&e, "y"), json!(0.0)]),
                        t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
                    ]),
                ),
                (
                    json!("mount-crown"),
                    t(vec![
                        t(vec![g(&e, "x"), g(&e, "y"), g(&e, "FACE_B")]),
                        t(vec![json!(0.0), json!(0.0), json!(1.0)]),
                    ]),
                ),
            ]));
            Ok(Value::Null)
        }
        ("condenser_block", "mount_seats") => {
            {
                let temp2 = {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "condenser_block", "mount_xy", argv, kwargs, Some(&e))?
                };
                e.insert("x".into(), ix(temp2.clone(), json!(0)));
                e.insert("y".into(), ix(temp2.clone(), json!(1)));
            }
            return Ok(object(vec![
                (
                    json!("mount-base"),
                    t(vec![
                        t(vec![g(&e, "x"), g(&e, "y"), json!(0.0)]),
                        t(vec![json!(0.0), json!(0.0), json!(1.0)]),
                    ]),
                ),
                (
                    json!("mount-crown"),
                    t(vec![
                        t(vec![
                            g(&e, "x"),
                            g(&e, "y"),
                            b("-", g(&e, "FACE_B"), g(&e, "PLATE_T")),
                        ]),
                        t(vec![json!(0.0), json!(0.0), json!(1.0)]),
                    ]),
                ),
            ]));
            Ok(Value::Null)
        }
        ("condenser_block", "stations_hold") => {
            e.insert(
                "span".into(),
                object(vec![
                    (json!("x"), t(vec![json!(0.0), g(&e, "AIRFLOW")])),
                    (json!("y"), t(vec![json!(0.0), g(&e, "FACE_A")])),
                    (json!("z"), t(vec![json!(0.0), g(&e, "FACE_B")])),
                ]),
            );
            for item in seq(method(
                {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "condenser_block", "stations", argv, kwargs, Some(&e))?
                },
                "items",
                vec![],
            )) {
                {
                    let temp3 = item;
                    e.insert("name".into(), ix(temp3.clone(), json!(0)));
                    {
                        let temp4 = ix(temp3.clone(), json!(1));
                        e.insert("pos".into(), ix(temp4.clone(), json!(0)));
                        e.insert("axis".into(), ix(temp4.clone(), json!(1)));
                    }
                }
                for item in seq(builtin("enumerate", vec![json!("xyz")])) {
                    {
                        let temp5 = item;
                        e.insert("i".into(), ix(temp5.clone(), json!(0)));
                        e.insert("ax".into(), ix(temp5.clone(), json!(1)));
                    }
                    {
                        let temp6 = ix(g(&e, "span"), g(&e, "ax"));
                        e.insert("lo".into(), ix(temp6.clone(), json!(0)));
                        e.insert("hi".into(), ix(temp6.clone(), json!(1)));
                    }
                    if truth(&{
                        let value = u("not", ix(g(&e, "axis"), g(&e, "i")));
                        if truth(&value) {
                            u(
                                "not",
                                json!(
                                    compare("<=", g(&e, "lo"), ix(g(&e, "pos"), g(&e, "i")))
                                        && compare("<=", ix(g(&e, "pos"), g(&e, "i")), g(&e, "hi"))
                                ),
                            )
                        } else {
                            value
                        }
                    }) {
                        bail!(
                            "{}",
                            string(&json!(
                                [
                                    "condenser ".to_owned(),
                                    format_value(g(&e, "name"), "")?,
                                    " stands at ".to_owned(),
                                    format_value(g(&e, "ax"), "")?,
                                    " = ".to_owned(),
                                    format_value(ix(g(&e, "pos"), g(&e, "i")), "g")?,
                                    ", outside the block's own ".to_owned(),
                                    format_value(g(&e, "lo"), "g")?,
                                    "..".to_owned(),
                                    format_value(g(&e, "hi"), "g")?,
                                    " — the pick is off the face it is meant to cross.".to_owned()
                                ]
                                .concat()
                            ))
                        );
                    } else {
                    }
                }
            }
            Ok(Value::Null)
        }
        ("digiten_flow_sensor", "inlet") => {
            return Ok(t(vec![
                t(vec![u("-", g(&e, "port_face")), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("digiten_flow_sensor", "outlet") => {
            return Ok(t(vec![
                t(vec![g(&e, "port_face"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("digiten_flow_sensor", "wire_exit") => {
            return Ok(t(vec![
                g(&e, "wire_root"),
                t(vec![json!(0.0), json!(0.0), json!(1.0)]),
            ]));
            Ok(Value::Null)
        }
        ("digiten_flow_sensor", "mounting_profile") => {
            e.insert(
                "sign".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sign"))
                    .unwrap_or_else(|| missing("sign")),
            );
            return Ok(t(vec![
                t(vec![
                    json!(15.5),
                    g(&e, "port_neck_end"),
                    g(&e, "port_neck_radius"),
                    g(&e, "port_neck_radius"),
                ]),
                {
                    let mut temp1 = vec![];
                    temp1.push(g(&e, "port_neck_end"));
                    temp1.push(g(&e, "port_collar_end"));
                    temp1.extend(seq(g(&e, "port_collar_radii")));
                    t(temp1)
                },
            ]));
            Ok(Value::Null)
        }
        ("flare38_14ptc", "flare_face") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("flare38_14ptc", "tube_port") => {
            return Ok(t(vec![
                t(vec![g(&e, "LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("g_ganen_foot", "parameters") => {
            return Ok(object(vec![
                (
                    json!("frame"),
                    json!("slot centre; X rail, +Y outward, Z0 bearing"),
                ),
                (json!("identical_feet"), json!(true)),
                (json!("pad_thickness_mm"), g(&e, "PAD_THICKNESS")),
                (json!("axial_width_mm"), g(&e, "WIDTH")),
                (json!("outward_nose_radius_mm"), json!(9.0)),
                (json!("slot_width_mm"), g(&e, "SLOT_WIDTH")),
                (json!("slot_length_mm"), g(&e, "SLOT_LENGTH")),
                (json!("slot_long_axis"), json!("+Y")),
                (json!("installed_slot_y_abs_mm"), g(&e, "SLOT_Y")),
                (
                    json!("clip_axial_interval_mm"),
                    json!(seq(g(&e, "CLIP_AXIAL_INTERVAL"))),
                ),
                (json!("visible_profile_yz_mm"), {
                    let mut e = e.clone();
                    let mut temp1 = Vec::new();
                    for item in seq(g(&e, "PROFILE_YZ")) {
                        e.insert("p".into(), item);
                        temp1.push(json!(seq(g(&e, "p"))));
                    }
                    json!(temp1)
                }),
                (
                    json!("undercuts"),
                    json!("two visible underside reliefs, separated by a central rib"),
                ),
                (
                    json!("qualification"),
                    json!(
                        "Purchased-part visible geometry reference. The hidden rail cavity and elastomer compliance are not qualified for manufacture."
                    ),
                ),
                (
                    json!("travel_scope"),
                    json!(
                        "Full axial engagement is a chosen mounting datum; scan observations include partially overhanging feet and do not establish hard stops."
                    ),
                ),
            ]));
            Ok(Value::Null)
        }
        ("g_ganen_foot", "rail_engagement_interval") => {
            return Ok(g(&e, "CLIP_AXIAL_INTERVAL"));
            Ok(Value::Null)
        }
        ("g_ganen_pump", "parameters") => {
            return Ok(parse_json(read_file(
                cx,
                b("/", g(&e, "HERE"), json!("reference-parameters.json")),
            )?)?);
            Ok(Value::Null)
        }
        ("g_ganen_pump", "port") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "row".into(),
                ix(
                    ix(
                        {
                            let argv = vec![];
                            let kwargs = json!({});
                            call(cx, "g_ganen_pump", "parameters", argv, kwargs, Some(&e))?
                        },
                        json!("ports"),
                    ),
                    g(&e, "name"),
                ),
            );
            return Ok(t(vec![
                t(seq(ix(g(&e, "row"), json!("tip_mm")))),
                t(seq(ix(g(&e, "row"), json!("outward_axis")))),
            ]));
            Ok(Value::Null)
        }
        ("g_ganen_pump", "suction") => {
            return Ok({
                let argv = vec![json!("port_yminus")];
                let kwargs = json!({});
                call(cx, "g_ganen_pump", "port", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("g_ganen_pump", "discharge") => {
            return Ok({
                let argv = vec![json!("port_yplus")];
                let kwargs = json!({});
                call(cx, "g_ganen_pump", "port", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("g_ganen_pump", "mount_slots") => {
            return Ok(t(seq(ix(
                {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "g_ganen_pump", "parameters", argv, kwargs, Some(&e))?
                },
                json!("mounting_feet"),
            ))));
            Ok(Value::Null)
        }
        ("g_ganen_pump", "port_profile") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            return Ok(ix(
                ix(
                    {
                        let argv = vec![];
                        let kwargs = json!({});
                        call(cx, "g_ganen_pump", "parameters", argv, kwargs, Some(&e))?
                    },
                    json!("ports"),
                ),
                g(&e, "name"),
            ));
            Ok(Value::Null)
        }
        ("g_ganen_pump", "sliding_rails") => {
            return Ok(t(seq(ix(
                {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "g_ganen_pump", "parameters", argv, kwargs, Some(&e))?
                },
                json!("sliding_rails"),
            ))));
            Ok(Value::Null)
        }
        ("g_ganen_pump", "mount_seat_z") => {
            return Ok(json!(0.0));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "mount_seat_z") => {
            e.insert(
                "hull".into(),
                ix(
                    builtin(
                        "next",
                        vec![{
                            let mut e = e.clone();
                            let mut temp4 = Vec::new();
                            for item in seq(ix(
                                {
                                    let argv = vec![];
                                    let kwargs = json!({});
                                    call(
                                        cx,
                                        "g_ganen_installation",
                                        "parameters",
                                        argv,
                                        kwargs,
                                        Some(&e),
                                    )?
                                },
                                json!("casing_shell_envelopes"),
                            )) {
                                e.insert("row".into(), item);
                                if truth(&json!(compare(
                                    "==",
                                    ix(g(&e, "row"), json!("id")),
                                    json!("lower_cradle_occupied")
                                ))) {
                                    temp4.push(g(&e, "row"));
                                }
                            }
                            json!(temp4)
                        }],
                    ),
                    json!("external_envelope"),
                ),
            );
            return Ok(builtin(
                "min",
                vec![{
                    let mut e = e.clone();
                    let mut temp5 = Vec::new();
                    for item in seq(ix(g(&e, "hull"), json!("vertices_mm"))) {
                        e.insert("point".into(), item);
                        temp5.push(ix(g(&e, "point"), json!(2)));
                    }
                    json!(temp5)
                }],
            ));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "mount_stations") => {
            e.insert("rows".into(), json!([]));
            for item in seq({
                let argv = vec![];
                let kwargs = json!({});
                call(cx, "g_ganen_integration", "mount_slots", argv, kwargs, None)?
            }) {
                e.insert("observed".into(), item);
                e.insert("name".into(), ix(g(&e, "observed"), json!("id")));
                e.insert(
                    "side".into(),
                    (if truth(&json!(compare("in", json!("yminus"), g(&e, "name")))) {
                        u("-", json!(1))
                    } else {
                        json!(1)
                    }),
                );
                e.insert("x".into(), ix(g(&e, "SELECTED_SLIDER_X"), g(&e, "name")));
                e.insert(
                    "interval".into(),
                    (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                        g(&e, "CLIP_X")
                    } else {
                        t(vec![
                            u("-", ix(g(&e, "CLIP_X"), json!(1))),
                            u("-", ix(g(&e, "CLIP_X"), json!(0))),
                        ])
                    }),
                );
                {
                    let item = object(vec![
                        (json!("id"), g(&e, "name")),
                        (
                            json!("station_mm"),
                            t(vec![
                                g(&e, "x"),
                                b(
                                    "*",
                                    g(&e, "side"),
                                    b("+", g(&e, "SLOT_Y"), g(&e, "SCREW_SLOT_OFFSET_OUTWARD")),
                                ),
                                json!(0.0),
                            ]),
                        ),
                        (
                            json!("slot_center_mm"),
                            t(vec![
                                g(&e, "x"),
                                b("*", g(&e, "side"), g(&e, "SLOT_Y")),
                                json!(0.0),
                            ]),
                        ),
                        (
                            json!("screw_offset_outward_mm"),
                            g(&e, "SCREW_SLOT_OFFSET_OUTWARD"),
                        ),
                        (json!("shape_basis"), json!("shared_purchased_rubber_foot")),
                        (
                            json!("pad_thickness_mm"),
                            attr(cx, "g_ganen_foot", "PAD_THICKNESS")?,
                        ),
                        (
                            json!("rail_engagement_x_mm"),
                            t(vec![
                                b("+", g(&e, "x"), ix(g(&e, "interval"), json!(0))),
                                b("+", g(&e, "x"), ix(g(&e, "interval"), json!(1))),
                            ]),
                        ),
                        (
                            json!("station_basis"),
                            json!("outermost_complete_visible_rail_engagement"),
                        ),
                        (
                            json!("observed_pad_top_mm"),
                            json!([(object(vec![
                                (
                                    json!("pass"),
                                    json!("Derek_direct_measurement_approximately_7_mm")
                                ),
                                (
                                    json!("at_screw_axis_mm"),
                                    attr(cx, "g_ganen_foot", "PAD_THICKNESS")?
                                ),
                                (
                                    json!("over_washer_min_mm"),
                                    attr(cx, "g_ganen_foot", "PAD_THICKNESS")?
                                ),
                                (
                                    json!("over_washer_max_mm"),
                                    attr(cx, "g_ganen_foot", "PAD_THICKNESS")?
                                )
                            ]))]),
                        ),
                        (json!("through_slot_physically_qualified"), json!(false)),
                        (json!("washer_physically_qualified"), json!(false)),
                    ]);
                    mutate(&mut e, "rows", "append", item);
                }
            }
            return Ok(t(seq(g(&e, "rows"))));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "mount_holes") => {
            return Ok(t(vec![]));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "bearing_datum") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "g_ganen_installation",
                        "mount_seat_z",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }]),
                t(vec![json!(0.0), json!(0.0), json!(1.0)]),
            ]));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "observed_pad_upper_z") => {
            return Ok(builtin(
                "max",
                vec![{
                    let mut e = e.clone();
                    let mut temp6 = Vec::new();
                    for item in seq({
                        let argv = vec![];
                        let kwargs = json!({});
                        call(
                            cx,
                            "g_ganen_installation",
                            "mount_stations",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    }) {
                        e.insert("foot".into(), item);
                        for item in seq(ix(g(&e, "foot"), json!("observed_pad_top_mm"))) {
                            e.insert("top".into(), item);
                            temp6.push(ix(g(&e, "top"), json!("over_washer_max_mm")));
                        }
                    }
                    json!(temp6)
                }],
            ));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "observed_pad_lower_z") => {
            return Ok(builtin(
                "min",
                vec![{
                    let mut e = e.clone();
                    let mut temp7 = Vec::new();
                    for item in seq({
                        let argv = vec![];
                        let kwargs = json!({});
                        call(
                            cx,
                            "g_ganen_installation",
                            "mount_stations",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    }) {
                        e.insert("foot".into(), item);
                        for item in seq(ix(g(&e, "foot"), json!("observed_pad_top_mm"))) {
                            e.insert("top".into(), item);
                            temp7.push(ix(g(&e, "top"), json!("over_washer_min_mm")));
                        }
                    }
                    json!(temp7)
                }],
            ));
            Ok(Value::Null)
        }
        ("g_ganen_installation", "profiled_barb_length") => {
            e.insert(
                "port_name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port_name"))
                    .unwrap_or_else(|| missing("port_name")),
            );
            e.insert(
                "key".into(),
                method(
                    object(vec![
                        (json!("suction"), json!("port_yminus")),
                        (json!("discharge"), json!("port_yplus")),
                    ]),
                    "get",
                    vec![g(&e, "port_name"), g(&e, "port_name")],
                ),
            );
            return Ok(ix(
                {
                    let argv = vec![g(&e, "key")];
                    let kwargs = json!({});
                    call(
                        cx,
                        "g_ganen_installation",
                        "port_profile",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                },
                json!("profiled_exterior_length_mm"),
            ));
            Ok(Value::Null)
        }
        ("gagira_reducing_coupling", "small_end") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("gagira_reducing_coupling", "large_end") => {
            return Ok(t(vec![
                t(vec![g(&e, "LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("gasher_check_valve", "inlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("/", u("-", g(&e, "TOTAL_LENGTH")), json!(2.0)),
                    json!(0.0),
                ]),
                t(vec![json!(0.0), u("-", json!(1.0)), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("gasher_check_valve", "outlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("/", g(&e, "TOTAL_LENGTH"), json!(2.0)),
                    json!(0.0),
                ]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("gasher_check_valve", "stations") => {
            return Ok(object(vec![
                (json!("inlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "gasher_check_valve", "inlet", argv, kwargs, Some(&e))?
                }),
                (json!("outlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "gasher_check_valve", "outlet", argv, kwargs, Some(&e))?
                }),
            ]));
            Ok(Value::Null)
        }
        ("hlghlg_check_valve", "sections") => {
            {
                let temp1 = t(vec![json!([]), json!(0.0)]);
                e.insert("out".into(), ix(temp1.clone(), json!(0)));
                e.insert("s".into(), ix(temp1.clone(), json!(1)));
            }
            for item in seq(g(&e, "SECTIONS")) {
                {
                    let temp2 = item;
                    e.insert("label".into(), ix(temp2.clone(), json!(0)));
                    e.insert("dia".into(), ix(temp2.clone(), json!(1)));
                    e.insert("length".into(), ix(temp2.clone(), json!(2)));
                }
                {
                    let item = t(vec![
                        g(&e, "label"),
                        b("/", g(&e, "dia"), json!(2.0)),
                        g(&e, "s"),
                        b("+", g(&e, "s"), g(&e, "length")),
                    ]);
                    mutate(&mut e, "out", "append", item);
                }
                e.insert("s".into(), b("+", g(&e, "s"), g(&e, "length")));
            }
            return Ok(t(seq(g(&e, "out"))));
            Ok(Value::Null)
        }
        ("hlghlg_check_valve", "inlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![json!(0.0), json!(0.0), json!(1.0)]),
            ]));
            Ok(Value::Null)
        }
        ("hlghlg_check_valve", "outlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), u("-", g(&e, "LENGTH"))]),
                t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
            ]));
            Ok(Value::Null)
        }
        ("hlghlg_check_valve", "tube_port") => {
            return Ok({
                let argv = vec![];
                let kwargs = json!({});
                call(cx, "hlghlg_check_valve", "outlet", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "panel_cutout") => {
            return Ok(t(vec![
                g(&e, "CUTOUT_W"),
                g(&e, "CUTOUT_H"),
                g(&e, "CUTOUT_R"),
            ]));
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "bore_outline") => {
            return Ok(t(vec![g(&e, "RIM_W"), g(&e, "RIM_H"), g(&e, "RIM_R")]));
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "panel_screws") => {
            return Ok(t(vec![
                t(vec![
                    b("/", u("-", g(&e, "SCREW_PITCH")), json!(2.0)),
                    json!(0.0),
                ]),
                t(vec![b("/", g(&e, "SCREW_PITCH"), json!(2.0)), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "panel_footprint") => {
            return Ok(t(vec![g(&e, "FLANGE_W"), g(&e, "FLANGE_H")]));
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "panel_stack") => {
            return Ok(t(vec![
                g(&e, "RIM_PROUD"),
                b(
                    "+",
                    b("+", g(&e, "FLANGE_T"), g(&e, "BODY_DEPTH")),
                    g(&e, "BOSS_PROUD"),
                ),
            ]));
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "_flange_landmarks") => {
            e.insert("a".into(), g(&e, "FLANGE_SHOULDER_X"));
            e.insert("h".into(), b("/", g(&e, "FLANGE_H"), json!(2.0)));
            e.insert("kr".into(), g(&e, "FLANGE_KNUCKLE_R"));
            e.insert(
                "shoulder_center".into(),
                t(vec![g(&e, "a"), b("-", g(&e, "h"), g(&e, "kr"))]),
            );
            e.insert("ear_center".into(), t(vec![g(&e, "EAR_CX"), json!(0.0)]));
            e.insert(
                "dx".into(),
                b(
                    "-",
                    ix(g(&e, "ear_center"), json!(0)),
                    ix(g(&e, "shoulder_center"), json!(0)),
                ),
            );
            e.insert(
                "dz".into(),
                b(
                    "-",
                    ix(g(&e, "ear_center"), json!(1)),
                    ix(g(&e, "shoulder_center"), json!(1)),
                ),
            );
            e.insert(
                "span".into(),
                math_fn("hypot", vec![g(&e, "dx"), g(&e, "dz")]),
            );
            if truth(&json!(compare(
                "<=",
                g(&e, "span"),
                builtin("abs", vec![b("-", g(&e, "EAR_R"), g(&e, "kr"))])
            ))) {
                bail!(
                    "{}",
                    string(&json!(
                        "the flange shoulder and ear rounds swallow their tangent"
                    ))
                );
            } else {
            }
            {
                let temp1 = t(vec![
                    b("/", g(&e, "dx"), g(&e, "span")),
                    b("/", g(&e, "dz"), g(&e, "span")),
                ]);
                e.insert("ux".into(), ix(temp1.clone(), json!(0)));
                e.insert("uz".into(), ix(temp1.clone(), json!(1)));
            }
            e.insert(
                "along".into(),
                b("/", b("-", g(&e, "kr"), g(&e, "EAR_R")), g(&e, "span")),
            );
            e.insert(
                "across".into(),
                math_fn(
                    "sqrt",
                    vec![b("-", json!(1.0), b("*", g(&e, "along"), g(&e, "along")))],
                ),
            );
            e.insert(
                "nx".into(),
                b(
                    "+",
                    b("*", g(&e, "along"), g(&e, "ux")),
                    b("*", g(&e, "across"), u("-", g(&e, "uz"))),
                ),
            );
            e.insert(
                "nz".into(),
                b(
                    "+",
                    b("*", g(&e, "along"), g(&e, "uz")),
                    b("*", g(&e, "across"), g(&e, "ux")),
                ),
            );
            e.insert(
                "q".into(),
                t(vec![
                    b(
                        "+",
                        ix(g(&e, "shoulder_center"), json!(0)),
                        b("*", g(&e, "kr"), g(&e, "nx")),
                    ),
                    b(
                        "+",
                        ix(g(&e, "shoulder_center"), json!(1)),
                        b("*", g(&e, "kr"), g(&e, "nz")),
                    ),
                ]),
            );
            e.insert(
                "t".into(),
                t(vec![
                    b(
                        "+",
                        ix(g(&e, "ear_center"), json!(0)),
                        b("*", g(&e, "EAR_R"), g(&e, "nx")),
                    ),
                    b(
                        "+",
                        ix(g(&e, "ear_center"), json!(1)),
                        b("*", g(&e, "EAR_R"), g(&e, "nz")),
                    ),
                ]),
            );
            e.insert(
                "theta".into(),
                math_fn("atan2", vec![g(&e, "nz"), g(&e, "nx")]),
            );
            e.insert(
                "mid_theta".into(),
                b(
                    "/",
                    b(
                        "+",
                        b("/", json!(std::f64::consts::PI), json!(2.0)),
                        g(&e, "theta"),
                    ),
                    json!(2.0),
                ),
            );
            e.insert(
                "mid".into(),
                t(vec![
                    b(
                        "+",
                        ix(g(&e, "shoulder_center"), json!(0)),
                        b("*", g(&e, "kr"), math_fn("cos", vec![g(&e, "mid_theta")])),
                    ),
                    b(
                        "+",
                        ix(g(&e, "shoulder_center"), json!(1)),
                        b("*", g(&e, "kr"), math_fn("sin", vec![g(&e, "mid_theta")])),
                    ),
                ]),
            );
            return Ok(object(vec![
                (json!("shoulder"), t(vec![g(&e, "a"), g(&e, "h")])),
                (json!("round_mid"), g(&e, "mid")),
                (json!("tangent_start"), g(&e, "q")),
                (json!("ear_tangent"), g(&e, "t")),
                (
                    json!("nose"),
                    t(vec![b("/", g(&e, "FLANGE_W"), json!(2.0)), json!(0.0)]),
                ),
                (
                    json!("taper_angle_deg"),
                    math_fn(
                        "degrees",
                        vec![math_fn(
                            "atan2",
                            vec![
                                b("-", ix(g(&e, "q"), json!(1)), ix(g(&e, "t"), json!(1))),
                                b("-", ix(g(&e, "t"), json!(0)), ix(g(&e, "q"), json!(0))),
                            ],
                        )],
                    ),
                ),
            ]));
            Ok(Value::Null)
        }
        ("iec_c14_inlet", "stations_hold") => {
            {
                let temp2 = {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "iec_c14_inlet", "bore_outline", argv, kwargs, Some(&e))?
                };
                e.insert("bore_w".into(), ix(temp2.clone(), json!(0)));
                e.insert("_bore_h".into(), ix(temp2.clone(), json!(1)));
                e.insert("_bore_r".into(), ix(temp2.clone(), json!(2)));
            }
            for item in seq({
                let argv = vec![];
                let kwargs = json!({});
                call(cx, "iec_c14_inlet", "panel_screws", argv, kwargs, Some(&e))?
            }) {
                {
                    let temp3 = item;
                    e.insert("sx".into(), ix(temp3.clone(), json!(0)));
                    e.insert("sz".into(), ix(temp3.clone(), json!(1)));
                }
                if truth(&json!(compare(
                    ">",
                    b(
                        "+",
                        builtin("abs", vec![g(&e, "sx")]),
                        b("/", g(&e, "CSK_D"), json!(2.0))
                    ),
                    b("/", g(&e, "FLANGE_W"), json!(2.0))
                ))) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "the screw at (".to_owned(),
                                format_value(g(&e, "sx"), "g")?,
                                ", ".to_owned(),
                                format_value(g(&e, "sz"), "g")?,
                                ") leaves the flange".to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
                if truth(&json!(compare(
                    "<",
                    b(
                        "-",
                        builtin("abs", vec![g(&e, "sx")]),
                        b("/", g(&e, "CSK_D"), json!(2.0))
                    ),
                    b("/", g(&e, "bore_w"), json!(2.0))
                ))) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "the screw at (".to_owned(),
                                format_value(g(&e, "sx"), "g")?,
                                ", ".to_owned(),
                                format_value(g(&e, "sz"), "g")?,
                                ") breaks into the bore".to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
            }
            Ok(Value::Null)
        }
        ("jg_bulkhead_union", "panel_hole_d") => {
            e.insert(
                "clearance".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "clearance"))
                    .unwrap_or_else(|| missing("clearance")),
            );
            return Ok(b("+", g(&e, "MOUNTING_HOLE_D"), g(&e, "clearance")));
            Ok(Value::Null)
        }
        ("jg_bulkhead_union", "panel_footprint") => {
            e.insert(
                "diameter".into(),
                builtin("max", vec![g(&e, "FLANGE_D"), g(&e, "NUT_D")]),
            );
            return Ok(t(vec![g(&e, "diameter"), g(&e, "diameter")]));
            Ok(Value::Null)
        }
        ("jg_bulkhead_union", "flange_footprint") => {
            return Ok(g(&e, "FLANGE_D"));
            Ok(Value::Null)
        }
        ("jg_bulkhead_union", "port") => {
            e.insert(
                "side".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "side"))
                    .unwrap_or_else(|| missing("side")),
            );
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                        g(&e, "near_ring_face_y")
                    } else {
                        g(&e, "far_ring_face_y")
                    }),
                    json!(0.0),
                ]),
                t(vec![
                    json!(0.0),
                    (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                        json!(1.0)
                    } else {
                        u("-", json!(1.0))
                    }),
                    json!(0.0),
                ]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp010822e", "tube_port") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp010822e", "shank_end") => {
            return Ok(t(vec![
                t(vec![g(&e, "LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp0208e_tee", "run") => {
            e.insert(
                "sign".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sign"))
                    .unwrap_or_else(|| missing("sign")),
            );
            e.insert(
                "s".into(),
                (if truth(&json!(compare(">", g(&e, "sign"), json!(0)))) {
                    json!(1.0)
                } else {
                    u("-", json!(1.0))
                }),
            );
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    json!(0.0),
                    b("*", g(&e, "s"), g(&e, "REACH")),
                ]),
                t(vec![json!(0.0), json!(0.0), g(&e, "s")]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp0208e_tee", "branch") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "REACH"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp0208e_tee", "stations") => {
            return Ok(object(vec![
                (json!("+z"), {
                    let argv = vec![u("+", json!(1.0))];
                    let kwargs = json!({});
                    call(cx, "jg_pp0208e_tee", "run", argv, kwargs, Some(&e))?
                }),
                (json!("-z"), {
                    let argv = vec![u("-", json!(1.0))];
                    let kwargs = json!({});
                    call(cx, "jg_pp0208e_tee", "run", argv, kwargs, Some(&e))?
                }),
                (json!("branch"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "jg_pp0208e_tee", "branch", argv, kwargs, Some(&e))?
                }),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp0208e_tee", "envelope") => {
            return Ok(t(vec![
                g(&e, "COLLAR_D"),
                g(&e, "RUN_SPAN"),
                g(&e, "BRANCH_ENVELOPE"),
            ]));
            Ok(Value::Null)
        }
        ("elbow", "port") => {
            e.insert(
                "leg".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "leg"))
                    .unwrap_or_else(|| missing("leg")),
            );
            e.insert(
                "axis".into(),
                ix(
                    object(vec![
                        (json!("y"), t(vec![json!(0.0), json!(1.0), json!(0.0)])),
                        (json!("z"), t(vec![json!(0.0), json!(0.0), json!(1.0)])),
                    ]),
                    g(&e, "leg"),
                ),
            );
            return Ok(t(vec![
                t(seq({
                    let mut e = e.clone();
                    let mut temp1 = Vec::new();
                    for item in seq(g(&e, "axis")) {
                        e.insert("a".into(), item);
                        temp1.push(b("*", g(&e, "COLLET_FACE"), g(&e, "a")));
                    }
                    json!(temp1)
                })),
                g(&e, "axis"),
            ]));
            Ok(Value::Null)
        }
        ("elbow", "stations") => {
            return Ok({
                let mut e = e.clone();
                let mut temp2 = Vec::new();
                for item in seq(t(vec![json!("y"), json!("z")])) {
                    e.insert("leg".into(), item);
                    temp2.push((g(&e, "leg"), {
                        let argv = vec![g(&e, "leg")];
                        let kwargs = json!({});
                        call(cx, "elbow", "port", argv, kwargs, Some(&e))?
                    }));
                }
                object(temp2)
            });
            Ok(Value::Null)
        }
        ("jg_pp0408w", "port") => {
            e.insert(
                "side".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "side"))
                    .unwrap_or_else(|| missing("side")),
            );
            e.insert(
                "s".into(),
                (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                    json!(1.0)
                } else {
                    u("-", json!(1.0))
                }),
            );
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    json!(0.0),
                    b("*", g(&e, "s"), g(&e, "port_face_z")),
                ]),
                t(vec![json!(0.0), json!(0.0), g(&e, "s")]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp0408w", "envelope") => {
            return Ok(t(vec![g(&e, "RING_D"), g(&e, "OVERALL")]));
            Ok(Value::Null)
        }
        ("jg_pp0408w", "reach") => {
            return Ok(g(&e, "port_face_z"));
            Ok(Value::Null)
        }
        ("jg_pp061208w", "stem_tip") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp061208w", "stem_shoulder") => {
            return Ok(t(vec![
                t(vec![g(&e, "STEM_LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp061208w", "tube_port") => {
            return Ok(t(vec![
                t(vec![g(&e, "LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("jg_pp061208w", "captured_transform") => {
            {
                let temp3 = t(vec![
                    ix(g(&e, "PARAMETERS"), json!("captured_rotation")),
                    ix(g(&e, "PARAMETERS"), json!("captured_tip_origin_mm")),
                ]);
                e.insert("r".into(), ix(temp3.clone(), json!(0)));
                e.insert("t".into(), ix(temp3.clone(), json!(1)));
            }
            return Ok(b(
                "+",
                {
                    let mut e = e.clone();
                    let mut temp4 = Vec::new();
                    for item in seq(builtin("range", vec![json!(3)])) {
                        e.insert("i".into(), item);
                        temp4.push({
                            let mut temp5 = vec![];
                            temp5.extend(seq(ix(g(&e, "r"), g(&e, "i"))));
                            temp5.push(ix(g(&e, "t"), g(&e, "i")));
                            json!(temp5)
                        });
                    }
                    json!(temp4)
                },
                json!([(json!([(json!(0.0)), (json!(0.0)), (json!(0.0)), (json!(1.0))]))]),
            ));
            Ok(Value::Null)
        }
        ("kamoer_kphm400", "barb") => {
            e.insert(
                "i".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "i"))
                    .unwrap_or_else(|| missing("i")),
            );
            return Ok(t(vec![
                t(vec![
                    ix(g(&e, "arch_xs"), g(&e, "i")),
                    g(&e, "body_y_face"),
                    g(&e, "arch_plane_z"),
                ]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("kamoer_kphm400", "barbs") => {
            return Ok(t(seq({
                let mut e = e.clone();
                let mut temp2 = Vec::new();
                for item in seq(builtin(
                    "range",
                    vec![builtin("len", vec![g(&e, "arch_xs")])],
                )) {
                    e.insert("i".into(), item);
                    temp2.push({
                        let argv = vec![g(&e, "i")];
                        let kwargs = json!({});
                        call(cx, "kamoer_kphm400", "barb", argv, kwargs, Some(&e))?
                    });
                }
                json!(temp2)
            })));
            Ok(Value::Null)
        }
        ("kamoer_kphm400", "_body_parts") => {
            return Ok(json!([
                (t(vec![
                    json!("head"),
                    g(&e, "build_head"),
                    g(&e, "C_PUMP_HEAD")
                ])),
                (t(vec![
                    json!("rotor_housing"),
                    g(&e, "build_rotor_housing"),
                    g(&e, "C_PUMP_BOSS")
                ])),
                (t(vec![
                    json!("motor_body"),
                    g(&e, "build_motor_body"),
                    g(&e, "C_PUMP_MOTOR")
                ]))
            ]));
            Ok(Value::Null)
        }
        ("meanwell_irm90", "_block") => {
            e.insert(
                "sy".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sy"))
                    .unwrap_or_else(|| missing("sy")),
            );
            let side = if n(&g(&e, "sy")) > 0. { "ac" } else { "dc" };
            let terminal = ix(g(&e, "terminal_interfaces"), json!(side));
            return Ok(t(vec![
                t(seq(ix(terminal.clone(), json!("screw_center")))),
                t(seq(ix(terminal, json!("screw_axis")))),
            ]));
            Ok(Value::Null)
        }
        ("meanwell_irm90", "ac_in") => {
            return Ok({
                let argv = vec![json!(1.0)];
                let kwargs = json!({});
                call(cx, "meanwell_irm90", "_block", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("meanwell_irm90", "dc_out") => {
            return Ok({
                let argv = vec![u("-", json!(1.0))];
                let kwargs = json!({});
                call(cx, "meanwell_irm90", "_block", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("meanwell_irm90", "wire_entry") => {
            e.insert(
                "side".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "side"))
                    .unwrap_or_else(|| missing("side")),
            );
            let side = if n(&g(&e, "side")) > 0. { "ac" } else { "dc" };
            let terminal = ix(g(&e, "terminal_interfaces"), json!(side));
            return Ok(t(vec![
                t(seq(ix(terminal.clone(), json!("wire_center")))),
                t(seq(ix(terminal, json!("wire_axis")))),
            ]));
            Ok(Value::Null)
        }
        ("mq6_gas_sensor", "card_plane") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    json!(0.0),
                    b("+", g(&e, "PIN_LEN"), b("/", g(&e, "PCB_T"), json!(2.0))),
                ]),
                t(vec![json!(0.0), json!(0.0), json!(1.0)]),
            ]));
            Ok(Value::Null)
        }
        ("mq6_gas_sensor", "header_span") => {
            return Ok(t(vec![
                b(
                    "+",
                    b(
                        "/",
                        b(
                            "*",
                            b("-", g(&e, "PIN_COUNT"), json!(1)),
                            g(&e, "PIN_PITCH"),
                        ),
                        json!(2.0),
                    ),
                    b("/", g(&e, "PIN_SQ"), json!(2.0)),
                ),
                b(
                    "-",
                    b("/", g(&e, "PCB_X"), json!(2.0)),
                    g(&e, "PIN_ROW_INSET"),
                ),
            ]));
            Ok(Value::Null)
        }
        ("multiplex_asse1022", "inlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), g(&e, "BODY_CENTER_Z")]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("multiplex_asse1022", "outlet") => {
            return Ok(t(vec![
                t(vec![
                    g(&e, "TOTAL_LENGTH"),
                    json!(0.0),
                    g(&e, "BODY_CENTER_Z"),
                ]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("multiplex_asse1022", "vent") => {
            return Ok(t(vec![
                t(vec![g(&e, "VENT_X"), g(&e, "VENT_Y"), json!(0.0)]),
                t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "inlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("/", u("-", g(&e, "LENGTH")), json!(2.0)),
                    json!(0.0),
                ]),
                t(vec![json!(0.0), u("-", json!(1.0)), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "outlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("/", g(&e, "LENGTH"), json!(2.0)),
                    json!(0.0),
                ]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "socket_depth") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| Value::Null),
            );
            return Ok(g(&e, "SOCKET_INSERTION"));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "ports") => {
            e.insert("result".into(), object(vec![]));
            for item in seq(t(vec![
                t(vec![json!("inlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "neofit_achv44_check", "inlet", argv, kwargs, Some(&e))?
                }]),
                t(vec![json!("outlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "neofit_achv44_check", "outlet", argv, kwargs, Some(&e))?
                }]),
            ])) {
                {
                    let temp1 = item;
                    e.insert("name".into(), ix(temp1.clone(), json!(0)));
                    e.insert("station".into(), ix(temp1.clone(), json!(1)));
                }
                {
                    let temp2 = g(&e, "station");
                    e.insert("position".into(), ix(temp2.clone(), json!(0)));
                    e.insert("outward".into(), ix(temp2.clone(), json!(1)));
                }
                {
                    let key = g(&e, "name");
                    let temp3 = object(vec![
                        (json!("position"), g(&e, "position")),
                        (json!("outward"), g(&e, "outward")),
                        (json!("tube_od_mm"), g(&e, "TUBE_OD")),
                        (json!("insertion_mm"), {
                            let argv = vec![g(&e, "name")];
                            let kwargs = json!({});
                            call(
                                cx,
                                "neofit_achv44_check",
                                "socket_depth",
                                argv,
                                kwargs,
                                Some(&e),
                            )?
                        }),
                        (
                            json!("insertion_status"),
                            json!("same_family_inference_unmeasured_check"),
                        ),
                    ]);
                    setitem(&mut e, "result", key, temp3);
                }
            }
            return Ok(g(&e, "result"));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "bearing_band") => {
            return Ok(t(vec![
                json!(4.43650159122278),
                json!(20.1931249738797),
                g(&e, "MAX_BODY_RADIUS"),
            ]));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "sections") => {
            e.insert(
                "rows".into(),
                json!([(t(vec![
                    json!("inlet-release-collet"),
                    g(&e, "COLLET_MAJOR_RADIUS"),
                    json!(0.0),
                    g(&e, "COLLET_REACH")
                ]))]),
            );
            for item in seq(builtin(
                "enumerate",
                vec![builtin(
                    "zip",
                    vec![
                        g(&e, "FIXED_PROFILE"),
                        slice(g(&e, "FIXED_PROFILE"), json!(1), Value::Null),
                    ],
                )],
            )) {
                {
                    let temp4 = item;
                    e.insert("index".into(), ix(temp4.clone(), json!(0)));
                    {
                        let temp5 = ix(temp4.clone(), json!(1));
                        {
                            let temp6 = ix(temp5.clone(), json!(0));
                            e.insert("s0".into(), ix(temp6.clone(), json!(0)));
                            e.insert("r0".into(), ix(temp6.clone(), json!(1)));
                        }
                        {
                            let temp7 = ix(temp5.clone(), json!(1));
                            e.insert("s1".into(), ix(temp7.clone(), json!(0)));
                            e.insert("r1".into(), ix(temp7.clone(), json!(1)));
                        }
                    }
                }
                if truth(&json!(compare(">", g(&e, "s1"), g(&e, "s0")))) {
                    e.insert(
                        "label".into(),
                        (if truth(&json!(compare("==", g(&e, "index"), json!(2)))) {
                            json!("barrel")
                        } else {
                            json!(
                                [
                                    "fixed-body-".to_owned(),
                                    format_value(g(&e, "index"), "02")?
                                ]
                                .concat()
                            )
                        }),
                    );
                    {
                        let item = t(vec![
                            g(&e, "label"),
                            builtin("max", vec![g(&e, "r0"), g(&e, "r1")]),
                            g(&e, "s0"),
                            g(&e, "s1"),
                        ]);
                        mutate(&mut e, "rows", "append", item);
                    }
                } else {
                }
            }
            {
                let item = t(vec![
                    json!("outlet-release-collet"),
                    g(&e, "COLLET_MAJOR_RADIUS"),
                    b("-", g(&e, "LENGTH"), g(&e, "COLLET_REACH")),
                    g(&e, "LENGTH"),
                ]);
                mutate(&mut e, "rows", "append", item);
            }
            return Ok(t(seq(g(&e, "rows"))));
            Ok(Value::Null)
        }
        ("neofit_achv44_check", "specification") => {
            return Ok(parse_json(read_file(
                cx,
                b("/", g(&e, "HERE"), json!("model-dimensions.json")),
            )?)?);
            Ok(Value::Null)
        }
        ("neofit_acvus44_check", "stem_tip") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_acvus44_check", "tube_port") => {
            return Ok(t(vec![
                t(vec![g(&e, "LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_bulkhead", "_corners") => {
            e.insert(
                "across_flats".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "across_flats"))
                    .unwrap_or_else(|| missing("across_flats")),
            );
            return Ok(b(
                "/",
                g(&e, "across_flats"),
                math_fn("cos", vec![math_fn("radians", vec![json!(30.0)])]),
            ));
            Ok(Value::Null)
        }
        ("neofit_bulkhead", "panel_hole_d") => {
            e.insert(
                "clearance".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "clearance"))
                    .unwrap_or_else(|| missing("clearance")),
            );
            return Ok(b("+", g(&e, "THREAD_D"), g(&e, "clearance")));
            Ok(Value::Null)
        }
        ("neofit_bulkhead", "panel_footprint") => {
            return Ok(t(vec![g(&e, "NUT_D"), g(&e, "NUT_D")]));
            Ok(Value::Null)
        }
        ("neofit_bulkhead", "flange_footprint") => {
            return Ok(g(&e, "FLANGE_D"));
            Ok(Value::Null)
        }
        ("neofit_bulkhead", "port") => {
            e.insert(
                "side".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "side"))
                    .unwrap_or_else(|| missing("side")),
            );
            e.insert(
                "face".into(),
                (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                    g(&e, "near_ring_face_y")
                } else {
                    g(&e, "far_ring_face_y")
                }),
            );
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "face"), json!(0.0)]),
                t(vec![
                    json!(0.0),
                    (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                        json!(1.0)
                    } else {
                        u("-", json!(1.0))
                    }),
                    json!(0.0),
                ]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_drain_bulkhead", "panel_hole_d") => {
            e.insert(
                "clearance".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "clearance"))
                    .unwrap_or_else(|| missing("clearance")),
            );
            return Ok(b("+", g(&e, "THREAD_D"), g(&e, "clearance")));
            Ok(Value::Null)
        }
        ("neofit_drain_bulkhead", "panel_footprint") => {
            e.insert(
                "diameter".into(),
                builtin("max", vec![g(&e, "FLANGE_D"), g(&e, "NUT_D")]),
            );
            return Ok(t(vec![g(&e, "diameter"), g(&e, "diameter")]));
            Ok(Value::Null)
        }
        ("neofit_drain_bulkhead", "flange_footprint") => {
            return Ok(g(&e, "FLANGE_D"));
            Ok(Value::Null)
        }
        ("neofit_drain_bulkhead", "port") => {
            e.insert(
                "side".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "side"))
                    .unwrap_or_else(|| missing("side")),
            );
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                        g(&e, "near_ring_face_y")
                    } else {
                        g(&e, "far_ring_face_y")
                    }),
                    json!(0.0),
                ]),
                t(vec![
                    json!(0.0),
                    (if truth(&json!(compare(">", g(&e, "side"), json!(0)))) {
                        json!(1.0)
                    } else {
                        u("-", json!(1.0))
                    }),
                    json!(0.0),
                ]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_drain_bulkhead", "radius_at") => {
            e.insert(
                "profile".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "profile"))
                    .unwrap_or_else(|| missing("profile")),
            );
            e.insert(
                "x".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x"))
                    .unwrap_or_else(|| missing("x")),
            );
            if truth(&json!(compare(
                "<=",
                g(&e, "x"),
                ix(ix(g(&e, "profile"), json!(0)), json!(0))
            ))) {
                return Ok(ix(ix(g(&e, "profile"), json!(0)), json!(1)));
            } else {
            }
            if truth(&json!(compare(
                ">=",
                g(&e, "x"),
                ix(ix(g(&e, "profile"), u("-", json!(1))), json!(0))
            ))) {
                return Ok(ix(ix(g(&e, "profile"), u("-", json!(1))), json!(1)));
            } else {
            }
            for item in seq(builtin(
                "zip",
                vec![
                    g(&e, "profile"),
                    slice(g(&e, "profile"), json!(1), Value::Null),
                ],
            )) {
                {
                    let temp5 = item;
                    {
                        let temp6 = ix(temp5.clone(), json!(0));
                        e.insert("a".into(), ix(temp6.clone(), json!(0)));
                        e.insert("ra".into(), ix(temp6.clone(), json!(1)));
                    }
                    {
                        let temp7 = ix(temp5.clone(), json!(1));
                        e.insert("b".into(), ix(temp7.clone(), json!(0)));
                        e.insert("rb".into(), ix(temp7.clone(), json!(1)));
                    }
                }
                if truth(&json!(
                    compare("<=", g(&e, "a"), g(&e, "x")) && compare("<=", g(&e, "x"), g(&e, "b"))
                )) {
                    return Ok(b(
                        "+",
                        g(&e, "ra"),
                        b(
                            "/",
                            b(
                                "*",
                                b("-", g(&e, "rb"), g(&e, "ra")),
                                b("-", g(&e, "x"), g(&e, "a")),
                            ),
                            b("-", g(&e, "b"), g(&e, "a")),
                        ),
                    ));
                } else {
                }
            }
            bail!("{}", string(&json!("Station outside the recorded profile")));
            Ok(Value::Null)
        }
        ("neofit_drain_bulkhead", "profile_between") => {
            e.insert(
                "profile".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "profile"))
                    .unwrap_or_else(|| missing("profile")),
            );
            e.insert(
                "lo".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "lo"))
                    .unwrap_or_else(|| missing("lo")),
            );
            e.insert(
                "hi".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "hi"))
                    .unwrap_or_else(|| missing("hi")),
            );
            return Ok({
                let mut temp8 = vec![];
                temp8.push(t(vec![g(&e, "lo"), {
                    let argv = vec![g(&e, "profile"), g(&e, "lo")];
                    let kwargs = json!({});
                    call(
                        cx,
                        "neofit_drain_bulkhead",
                        "radius_at",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }]));
                temp8.extend(seq({
                    let mut e = e.clone();
                    let mut temp9 = Vec::new();
                    for item in seq(g(&e, "profile")) {
                        {
                            let temp10 = item;
                            e.insert("x".into(), ix(temp10.clone(), json!(0)));
                            e.insert("r".into(), ix(temp10.clone(), json!(1)));
                        }
                        if truth(&json!(
                            compare("<", b("+", g(&e, "lo"), json!(0.0001)), g(&e, "x"))
                                && compare("<", g(&e, "x"), b("-", g(&e, "hi"), json!(0.0001)))
                        )) {
                            temp9.push(t(vec![g(&e, "x"), g(&e, "r")]));
                        }
                    }
                    json!(temp9)
                }));
                temp8.push(t(vec![g(&e, "hi"), {
                    let argv = vec![g(&e, "profile"), g(&e, "hi")];
                    let kwargs = json!({});
                    call(
                        cx,
                        "neofit_drain_bulkhead",
                        "radius_at",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }]));
                json!(temp8)
            });
            Ok(Value::Null)
        }
        ("neofit_flavor_reducer", "port") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "PROUD_LENGTH"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_stem_elbow", "socket") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "SOCKET_MOUTH_REACH"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_stem_elbow", "stem_tip") => {
            return Ok(t(vec![
                t(vec![
                    u("-", g(&e, "STEM_TIP_REACH")),
                    json!(0.0),
                    json!(0.0),
                ]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_stem_elbow", "stem_shoulder") => {
            return Ok(t(vec![
                t(vec![
                    u("-", g(&e, "HUB_BACK_REACH")),
                    json!(0.0),
                    json!(0.0),
                ]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("neofit_stem_elbow", "seated_host_mouth") => {
            e.insert(
                "insertion".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "insertion"))
                    .unwrap_or_else(|| json!(12.7)),
            );
            if truth(&u(
                "not",
                json!(
                    compare("<", json!(0), g(&e, "insertion"))
                        && compare("<=", g(&e, "insertion"), g(&e, "STEM_LENGTH"))
                ),
            )) {
                bail!(
                    "{}",
                    string(&json!("Insertion must fit within the male stem"))
                );
            } else {
            }
            return Ok(t(vec![
                t(vec![
                    b("-", g(&e, "insertion"), g(&e, "STEM_TIP_REACH")),
                    json!(0.0),
                    json!(0.0),
                ]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("pump_barb_joint", "barb") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| missing("port")),
            );
            e.insert(
                "rows".into(),
                ix(
                    {
                        let argv = vec![ix(g(&e, "PORTS"), g(&e, "port"))];
                        let kwargs = json!({});
                        call(cx, "g_ganen_pump", "port_profile", argv, kwargs, None)?
                    },
                    json!("profile"),
                ),
            );
            return Ok(builtin(
                "sorted",
                vec![{
                    let mut e = e.clone();
                    let mut temp3 = Vec::new();
                    for item in seq(g(&e, "rows")) {
                        e.insert("row".into(), item);
                        temp3.push(t(vec![
                            ix(g(&e, "row"), json!("distance_from_tip_mm")),
                            ix(g(&e, "row"), json!("radius_mm")),
                        ]));
                    }
                    json!(temp3)
                }],
            ));
            Ok(Value::Null)
        }
        ("pump_barb_joint", "root") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| missing("port")),
            );
            return Ok(b(
                "+",
                ix(
                    ix(
                        {
                            let argv = vec![g(&e, "port")];
                            let kwargs = json!({});
                            call(cx, "pump_barb_joint", "barb", argv, kwargs, Some(&e))?
                        },
                        json!(0),
                    ),
                    json!(0),
                ),
                g(&e, "TUBE_ROOT_SETBACK"),
            ));
            Ok(Value::Null)
        }
        ("pump_barb_joint", "tube_length") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| missing("port")),
            );
            return Ok(b("-", g(&e, "TRIM"), {
                let argv = vec![g(&e, "port")];
                let kwargs = json!({});
                call(cx, "pump_barb_joint", "root", argv, kwargs, Some(&e))?
            }));
            Ok(Value::Null)
        }
        ("pump_barb_joint", "opened") => {
            e.insert(
                "r_bore".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "r_bore"))
                    .unwrap_or_else(|| missing("r_bore")),
            );
            return Ok(math_fn(
                "sqrt",
                vec![b(
                    "+",
                    b("**", g(&e, "r_bore"), json!(2)),
                    b(
                        "/",
                        b(
                            "-",
                            b("**", g(&e, "TUBE_OD"), json!(2)),
                            b("**", g(&e, "TUBE_ID"), json!(2)),
                        ),
                        json!(4.0),
                    ),
                )],
            ));
            Ok(Value::Null)
        }
        ("pump_barb_joint", "bands") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| missing("port")),
            );
            e.insert(
                "centres".into(),
                object(vec![
                    (
                        json!("barb"),
                        b(
                            "/",
                            {
                                let argv = vec![g(&e, "port")];
                                let kwargs = json!({});
                                call(cx, "pump_barb_joint", "root", argv, kwargs, Some(&e))?
                            },
                            json!(2.0),
                        ),
                    ),
                    (json!("stem"), b("/", g(&e, "TRIM"), json!(2.0))),
                ]),
            );
            return Ok({
                let mut e = e.clone();
                let mut temp4 = Vec::new();
                for item in seq(method(g(&e, "centres"), "items", vec![])) {
                    {
                        let temp5 = item;
                        e.insert("n".into(), ix(temp5.clone(), json!(0)));
                        e.insert("xc".into(), ix(temp5.clone(), json!(1)));
                    }
                    temp4.push((
                        g(&e, "n"),
                        t(vec![g(&e, "xc"), {
                            let argv = vec![g(&e, "port"), g(&e, "xc")];
                            let kwargs = json!({});
                            call(cx, "pump_barb_joint", "band_d", argv, kwargs, Some(&e))?
                        }]),
                    ));
                }
                object(temp4)
            });
            Ok(Value::Null)
        }
        ("pump_barb_joint", "pivot") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| missing("port")),
            );
            return Ok(t(vec![
                json!(0.0),
                json!(0.0),
                u(
                    "-",
                    ix(
                        ix(
                            {
                                let argv = vec![g(&e, "port")];
                                let kwargs = json!({});
                                call(cx, "pump_barb_joint", "barb", argv, kwargs, Some(&e))?
                            },
                            u("-", json!(1)),
                        ),
                        json!(1),
                    ),
                ),
            ]));
            Ok(Value::Null)
        }
        ("pump_barb_joint", "mouth") => {
            e.insert(
                "port".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "port"))
                    .unwrap_or_else(|| missing("port")),
            );
            e.insert(
                "bend".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "bend"))
                    .unwrap_or_else(|| json!(0.0)),
            );
            e.insert("b".into(), math_fn("radians", vec![g(&e, "bend")]));
            {
                let temp6 = t(vec![
                    math_fn("cos", vec![g(&e, "b")]),
                    math_fn("sin", vec![g(&e, "b")]),
                ]);
                e.insert("c".into(), ix(temp6.clone(), json!(0)));
                e.insert("s".into(), ix(temp6.clone(), json!(1)));
            }
            {
                let temp7 = t(vec![
                    b("-", attr(cx, "jg_pp061208w", "LENGTH")?, g(&e, "CUT_X")),
                    ix(
                        {
                            let argv = vec![g(&e, "port")];
                            let kwargs = json!({});
                            call(cx, "pump_barb_joint", "pivot", argv, kwargs, Some(&e))?
                        },
                        json!(2),
                    ),
                ]);
                e.insert("x".into(), ix(temp7.clone(), json!(0)));
                e.insert("pivot_z".into(), ix(temp7.clone(), json!(1)));
            }
            return Ok(t(vec![
                t(vec![
                    b(
                        "-",
                        b("*", g(&e, "x"), g(&e, "c")),
                        b("*", g(&e, "pivot_z"), g(&e, "s")),
                    ),
                    json!(0.0),
                    b(
                        "+",
                        b("*", u("-", g(&e, "x")), g(&e, "s")),
                        b("*", g(&e, "pivot_z"), b("-", json!(1.0), g(&e, "c"))),
                    ),
                ]),
                t(vec![g(&e, "c"), json!(0.0), u("-", g(&e, "s"))]),
            ]));
            Ok(Value::Null)
        }
        ("riteav_keystone", "receptacle_envelope") => {
            return Ok(t(vec![
                b(
                    "+",
                    g(&e, "POCKET_W"),
                    b("*", json!(2.0), g(&e, "RECEPTACLE_WALL")),
                ),
                b(
                    "+",
                    g(&e, "POCKET_H"),
                    b("*", json!(2.0), g(&e, "RECEPTACLE_WALL")),
                ),
            ]));
            Ok(Value::Null)
        }
        ("riteav_keystone", "panel_cutout") => {
            return Ok(t(vec![
                g(&e, "APERTURE_W"),
                g(&e, "APERTURE_H"),
                json!(0.4),
            ]));
            Ok(Value::Null)
        }
        ("riteav_keystone", "panel_footprint") => {
            return Ok({
                let argv = vec![];
                let kwargs = json!({});
                call(
                    cx,
                    "riteav_keystone",
                    "receptacle_envelope",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            Ok(Value::Null)
        }
        ("riteav_keystone", "ease_rise") => {
            return Ok(b(
                "*",
                g(&e, "LIP_D"),
                math_fn("tan", vec![math_fn("radians", vec![g(&e, "EASE_DEG")])]),
            ));
            Ok(Value::Null)
        }
        ("seaflo_discharge_chain", "sections") => {
            {
                let temp7 = t(vec![json!([]), json!(0.0)]);
                e.insert("out".into(), ix(temp7.clone(), json!(0)));
                e.insert("s".into(), ix(temp7.clone(), json!(1)));
            }
            for item in seq(g(&e, "SECTIONS")) {
                {
                    let temp8 = item;
                    e.insert("label".into(), ix(temp8.clone(), json!(0)));
                    e.insert("dia".into(), ix(temp8.clone(), json!(1)));
                    e.insert("length".into(), ix(temp8.clone(), json!(2)));
                }
                {
                    let item = t(vec![
                        g(&e, "label"),
                        b("/", g(&e, "dia"), json!(2.0)),
                        g(&e, "s"),
                        b("+", g(&e, "s"), g(&e, "length")),
                    ]);
                    mutate(&mut e, "out", "append", item);
                }
                e.insert("s".into(), b("+", g(&e, "s"), g(&e, "length")));
            }
            return Ok(t(seq(g(&e, "out"))));
            Ok(Value::Null)
        }
        ("seaflo_discharge_chain", "inlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![json!(0.0), json!(0.0), json!(1.0)]),
            ]));
            Ok(Value::Null)
        }
        ("seaflo_discharge_chain", "tube_port") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), u("-", g(&e, "LENGTH"))]),
                t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
            ]));
            Ok(Value::Null)
        }
        ("shok_blok_regulator", "sections") => {
            {
                let temp1 = t(vec![json!([]), json!(0.0)]);
                e.insert("result".into(), ix(temp1.clone(), json!(0)));
                e.insert("s".into(), ix(temp1.clone(), json!(1)));
            }
            for item in seq(g(&e, "SECTIONS")) {
                {
                    let temp2 = item;
                    e.insert("label".into(), ix(temp2.clone(), json!(0)));
                    e.insert("diameter".into(), ix(temp2.clone(), json!(1)));
                    e.insert("length".into(), ix(temp2.clone(), json!(2)));
                }
                {
                    let item = t(vec![
                        g(&e, "label"),
                        b("/", g(&e, "diameter"), json!(2)),
                        g(&e, "s"),
                        b("+", g(&e, "s"), g(&e, "length")),
                    ]);
                    mutate(&mut e, "result", "append", item);
                }
                e.insert("s".into(), b("+", g(&e, "s"), g(&e, "length")));
            }
            return Ok(t(seq(g(&e, "result"))));
            Ok(Value::Null)
        }
        ("shok_blok_regulator", "inlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("shok_blok_regulator", "outlet") => {
            return Ok(t(vec![
                t(vec![g(&e, "LENGTH"), json!(0.0), json!(0.0)]),
                t(vec![json!(1.0), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "_ring_spec") => {
            e.insert(
                "full".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "full"))
                    .unwrap_or_else(|| missing("full")),
            );
            e.insert(
                "major".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "major"))
                    .unwrap_or_else(|| missing("major")),
            );
            e.insert(
                "minor".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "minor"))
                    .unwrap_or_else(|| missing("minor")),
            );
            e.insert(
                "labels".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "labels"))
                    .unwrap_or_else(|| missing("labels")),
            );
            return Ok(object(vec![
                (json!("full"), g(&e, "full")),
                (json!("major"), g(&e, "major")),
                (json!("minor"), g(&e, "minor")),
                (json!("labels"), g(&e, "labels")),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "inlet") => {
            return Ok(t(vec![
                t(vec![
                    u("-", g(&e, "INLET_NUT_FACE")),
                    json!(0.0),
                    json!(0.0),
                ]),
                g(&e, "INLET_AXIS"),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "outlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), g(&e, "OUTLET_MOUTH_Z")]),
                t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "adjustment") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "SCREW_TIP_Y"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "relief") => {
            {
                let temp1 = {
                    let argv = vec![g(&e, "BLOWOFF_CAP_R")];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "_bearing",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                };
                e.insert("x".into(), ix(temp1.clone(), json!(0)));
                e.insert("z".into(), ix(temp1.clone(), json!(1)));
            }
            return Ok(t(vec![t(vec![g(&e, "x"), json!(0.0), g(&e, "z")]), {
                let argv = vec![json!(1.0)];
                let kwargs = object(vec![("as_axis".into(), json!(true))]);
                call(
                    cx,
                    "taprite_3741_regulator",
                    "_bearing",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            }]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "tank_dial") => {
            return Ok(t(vec![
                t(vec![g(&e, "TANK_REACH"), g(&e, "GAUGE_FACE_Y"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "outlet_dial") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    g(&e, "GAUGE_FACE_Y"),
                    g(&e, "OUTLET_REACH"),
                ]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "stations") => {
            return Ok(object(vec![
                (json!("inlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "inlet",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }),
                (json!("outlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "outlet",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }),
                (json!("adjustment"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "adjustment",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }),
                (json!("relief"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "relief",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }),
                (json!("tank-dial"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "tank_dial",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }),
                (json!("outlet-dial"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "taprite_3741_regulator",
                        "outlet_dial",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                }),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "_bearing") => {
            e.insert(
                "r".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "r"))
                    .unwrap_or_else(|| missing("r")),
            );
            e.insert(
                "as_axis".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "as_axis"))
                    .unwrap_or_else(|| json!(false)),
            );
            e.insert(
                "a".into(),
                math_fn("radians", vec![g(&e, "BLOWOFF_BEARING_DEG")]),
            );
            {
                let temp2 = t(vec![
                    b("*", g(&e, "r"), math_fn("cos", vec![g(&e, "a")])),
                    b("*", g(&e, "r"), math_fn("sin", vec![g(&e, "a")])),
                ]);
                e.insert("x".into(), ix(temp2.clone(), json!(0)));
                e.insert("z".into(), ix(temp2.clone(), json!(1)));
            }
            return Ok((if truth(&g(&e, "as_axis")) {
                t(vec![g(&e, "x"), json!(0.0), g(&e, "z")])
            } else {
                t(vec![g(&e, "x"), g(&e, "z")])
            }));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "_scale_deg") => {
            e.insert(
                "value".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "value"))
                    .unwrap_or_else(|| missing("value")),
            );
            e.insert(
                "full".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "full"))
                    .unwrap_or_else(|| missing("full")),
            );
            return Ok(b(
                "-",
                g(&e, "DIAL_ZERO_DEG"),
                b(
                    "/",
                    b("*", g(&e, "DIAL_SWEEP_DEG"), g(&e, "value")),
                    g(&e, "full"),
                ),
            ));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "_at") => {
            e.insert(
                "r".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "r"))
                    .unwrap_or_else(|| missing("r")),
            );
            e.insert(
                "deg".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "deg"))
                    .unwrap_or_else(|| missing("deg")),
            );
            e.insert("a".into(), math_fn("radians", vec![g(&e, "deg")]));
            return Ok(t(vec![
                b("*", g(&e, "r"), math_fn("cos", vec![g(&e, "a")])),
                b("*", g(&e, "r"), math_fn("sin", vec![g(&e, "a")])),
            ]));
            Ok(Value::Null)
        }
        ("taprite_3741_regulator", "_steps") => {
            e.insert(
                "step".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "step"))
                    .unwrap_or_else(|| missing("step")),
            );
            e.insert(
                "full".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "full"))
                    .unwrap_or_else(|| missing("full")),
            );
            e.insert(
                "n".into(),
                builtin(
                    "int",
                    vec![math_fn(
                        "floor",
                        vec![b("+", b("/", g(&e, "full"), g(&e, "step")), json!(1e-09))],
                    )],
                ),
            );
            return Ok({
                let mut e = e.clone();
                let mut temp3 = Vec::new();
                for item in seq(builtin("range", vec![b("+", g(&e, "n"), json!(1))])) {
                    e.insert("i".into(), item);
                    temp3.push(b("*", g(&e, "i"), g(&e, "step")));
                }
                json!(temp3)
            });
            Ok(Value::Null)
        }
        ("tee_connector", "carrier_collet_depression") => {
            e.insert(
                "offset".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "offset"))
                    .unwrap_or_else(|| missing("offset")),
            );
            return Ok(builtin(
                "min",
                vec![
                    g(&e, "BRANCH_COLLET_TRAVEL"),
                    builtin(
                        "max",
                        vec![
                            json!(0.0),
                            b("-", g(&e, "BRANCH_COLLET_TRAVEL"), g(&e, "offset")),
                        ],
                    ),
                ],
            ));
            Ok(Value::Null)
        }
        ("tee_connector", "run") => {
            e.insert(
                "sign".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sign"))
                    .unwrap_or_else(|| missing("sign")),
            );
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    json!(0.0),
                    b("*", g(&e, "sign"), g(&e, "RUN_HALF")),
                ]),
                t(vec![json!(0.0), json!(0.0), g(&e, "sign")]),
            ]));
            Ok(Value::Null)
        }
        ("tee_connector", "run_barrel") => {
            e.insert(
                "sign".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sign"))
                    .unwrap_or_else(|| missing("sign")),
            );
            {
                let temp2 = g(&e, "RUN_COLLAR_BAND");
                e.insert("near".into(), ix(temp2.clone(), json!(0)));
                e.insert("far".into(), ix(temp2.clone(), json!(1)));
            }
            return Ok(t(vec![
                t(vec![
                    t(vec![
                        json!(0.0),
                        json!(0.0),
                        b(
                            "/",
                            b("*", g(&e, "sign"), b("+", g(&e, "near"), g(&e, "far"))),
                            json!(2),
                        ),
                    ]),
                    t(vec![json!(0.0), json!(0.0), g(&e, "sign")]),
                ]),
                g(&e, "BARREL_R"),
                b("-", g(&e, "far"), g(&e, "near")),
            ]));
            Ok(Value::Null)
        }
        ("tee_connector", "branch") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "BRANCH_REACH"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("tee_connector", "branch_collar") => {
            return Ok(t(vec![
                t(vec![
                    t(vec![
                        json!(0.0),
                        b("/", b("+", g(&e, "CAP_NEAR"), g(&e, "CAP_FAR")), json!(2)),
                        json!(0.0),
                    ]),
                    t(vec![json!(0.0), json!(1.0), json!(0.0)]),
                ]),
                g(&e, "BARREL_R"),
                b("-", g(&e, "CAP_FAR"), g(&e, "CAP_NEAR")),
            ]));
            Ok(Value::Null)
        }
        ("tee_connector", "stations") => {
            return Ok(object(vec![
                (json!("+z"), {
                    let argv = vec![json!(1.0)];
                    let kwargs = json!({});
                    call(cx, "tee_connector", "run", argv, kwargs, Some(&e))?
                }),
                (json!("-z"), {
                    let argv = vec![u("-", json!(1.0))];
                    let kwargs = json!({});
                    call(cx, "tee_connector", "run", argv, kwargs, Some(&e))?
                }),
                (json!("branch"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "tee_connector", "branch", argv, kwargs, Some(&e))?
                }),
            ]));
            Ok(Value::Null)
        }
        ("teyleten_relay", "contacts") => {
            return Ok(t(vec![
                t(seq(ix(g(&e, "contact_port"), json!("point_mm")))),
                t(seq(ix(g(&e, "contact_port"), json!("outward_axis")))),
            ]));
            Ok(Value::Null)
        }
        ("teyleten_relay", "logic") => {
            return Ok(t(vec![
                t(seq(ix(g(&e, "logic_port"), json!("point_mm")))),
                t(seq(ix(g(&e, "logic_port"), json!("outward_axis")))),
            ]));
            Ok(Value::Null)
        }
        ("water_split", "supply") => {
            return Ok(t(vec![
                t(vec![json!(0.0), g(&e, "REACH"), json!(0.0)]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("water_split", "to_vk") => {
            return Ok(t(vec![
                t(vec![u("-", g(&e, "BRANCH_REACH")), json!(0.0), json!(0.0)]),
                t(vec![u("-", json!(1.0)), json!(0.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("water_split", "to_flavor") => {
            return Ok(t(vec![
                t(vec![json!(0.0), u("-", g(&e, "REACH")), json!(0.0)]),
                t(vec![json!(0.0), u("-", json!(1.0)), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("water_split", "run_barrel") => {
            {
                let temp1 = attr(cx, "tee_connector", "RUN_COLLAR_BAND")?;
                e.insert("near".into(), ix(temp1.clone(), json!(0)));
                e.insert("far".into(), ix(temp1.clone(), json!(1)));
            }
            return Ok(t(vec![
                t(vec![
                    t(vec![
                        json!(0.0),
                        b("/", b("+", g(&e, "near"), g(&e, "far")), json!(2.0)),
                        json!(0.0),
                    ]),
                    t(vec![json!(0.0), json!(1.0), json!(0.0)]),
                ]),
                attr(cx, "tee_connector", "BARREL_R")?,
                b("-", g(&e, "far"), g(&e, "near")),
            ]));
            Ok(Value::Null)
        }
        ("water_split", "clearance_seat") => {
            e.insert(
                "span".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "span"))
                    .unwrap_or_else(|| missing("span")),
            );
            e.insert(
                "tie_width".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "tie_width"))
                    .unwrap_or_else(|| missing("tie_width")),
            );
            {
                let temp2 = {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "water_split", "run_barrel", argv, kwargs, Some(&e))?
                };
                e.insert("station".into(), ix(temp2.clone(), json!(0)));
                e.insert("radius".into(), ix(temp2.clone(), json!(1)));
                e.insert("_".into(), ix(temp2.clone(), json!(2)));
            }
            e.insert("mid".into(), ix(ix(g(&e, "station"), json!(0)), json!(1)));
            {
                let temp3 = t(vec![
                    b("-", g(&e, "mid"), b("/", g(&e, "span"), json!(2.0))),
                    b("+", g(&e, "mid"), b("/", g(&e, "span"), json!(2.0))),
                ]);
                e.insert("lo".into(), ix(temp3.clone(), json!(0)));
                e.insert("hi".into(), ix(temp3.clone(), json!(1)));
            }
            if truth(&{
                let value = json!(compare(
                    "<=",
                    g(&e, "lo"),
                    attr(cx, "tee_connector", "BARREL_R")?
                ));
                if truth(&value) {
                    value
                } else {
                    json!(compare(
                        ">=",
                        g(&e, "hi"),
                        b(
                            "-",
                            g(&e, "RUN_REACH"),
                            attr(cx, "tee_connector", "RUN_COLLET_TRAVEL")?
                        )
                    ))
                }
            }) {
                bail!(
                    "{}",
                    string(&json!(
                        "water-split seat reaches the branch or the fully pressed run face"
                    ))
                );
            } else {
            }
            if truth(&json!(compare(
                ">",
                attr(cx, "tee_connector", "COLLET_NOSE_R")?,
                g(&e, "radius")
            ))) {
                bail!(
                    "{}",
                    string(&json!(
                        "water-split release sleeve exceeds the seat clearance envelope"
                    ))
                );
            } else {
            }
            return Ok(t(vec![g(&e, "station"), g(&e, "radius"), g(&e, "span")]));
            Ok(Value::Null)
        }
        ("wr1110_regulator", "inlet") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), json!(0.0)]),
                t(vec![json!(0.0), u("-", json!(1.0)), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("wr1110_regulator", "outlet") => {
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("+", g(&e, "TOTAL_LENGTH"), g(&e, "STUB_LENGTH")),
                    json!(0.0),
                ]),
                t(vec![json!(0.0), json!(1.0), json!(0.0)]),
            ]));
            Ok(Value::Null)
        }
        ("wr1110_regulator", "barrel") => {
            return Ok(t(vec![
                t(vec![
                    t(vec![
                        json!(0.0),
                        b(
                            "+",
                            g(&e, "BODY_START"),
                            b("/", g(&e, "BODY_LENGTH"), json!(2.0)),
                        ),
                        json!(0.0),
                    ]),
                    t(vec![json!(0.0), json!(1.0), json!(0.0)]),
                ]),
                b("/", g(&e, "BODY_D"), json!(2.0)),
                g(&e, "BODY_LENGTH"),
            ]));
            Ok(Value::Null)
        }
        ("wr1110_regulator", "stations") => {
            return Ok(object(vec![
                (json!("inlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "wr1110_regulator", "inlet", argv, kwargs, Some(&e))?
                }),
                (json!("outlet"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "wr1110_regulator", "outlet", argv, kwargs, Some(&e))?
                }),
            ]));
            Ok(Value::Null)
        }
        ("y_divider", "stem") => {
            return Ok(t(vec![
                t(vec![json!(0.0), json!(0.0), u("+", g(&e, "HALF"))]),
                t(vec![json!(0.0), json!(0.0), json!(1.0)]),
            ]));
            Ok(Value::Null)
        }
        ("y_divider", "outlet") => {
            e.insert(
                "sign".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sign"))
                    .unwrap_or_else(|| missing("sign")),
            );
            return Ok(t(vec![
                t(vec![
                    json!(0.0),
                    b("*", g(&e, "sign"), g(&e, "OUTLET_Y")),
                    u("-", g(&e, "HALF")),
                ]),
                t(vec![json!(0.0), json!(0.0), u("-", json!(1.0))]),
            ]));
            Ok(Value::Null)
        }
        ("y_divider", "stations") => {
            return Ok(object(vec![
                (json!("stem"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(cx, "y_divider", "stem", argv, kwargs, Some(&e))?
                }),
                (json!("-y"), {
                    let argv = vec![u("-", json!(1.0))];
                    let kwargs = json!({});
                    call(cx, "y_divider", "outlet", argv, kwargs, Some(&e))?
                }),
                (json!("+y"), {
                    let argv = vec![u("+", json!(1.0))];
                    let kwargs = json!({});
                    call(cx, "y_divider", "outlet", argv, kwargs, Some(&e))?
                }),
            ]));
            Ok(Value::Null)
        }
        ("y_divider", "_collet_offsets") => {
            e.insert(
                "readings".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "readings"))
                    .unwrap_or_else(|| missing("readings")),
            );
            e.insert(
                "axis".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "axis"))
                    .unwrap_or_else(|| missing("axis")),
            );
            e.insert(
                "bore_r".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "bore_r"))
                    .unwrap_or_else(|| missing("bore_r")),
            );
            e.insert(
                "tol".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "tol"))
                    .unwrap_or_else(|| json!(0.0001)),
            );
            for item in seq(ix(g(&e, "readings"), json!("bores"))) {
                e.insert("bore".into(), item);
                if truth(&{
                    let value = json!(compare(
                        "==",
                        ix(g(&e, "bore"), json!("axis")),
                        g(&e, "axis")
                    ));
                    if truth(&value) {
                        json!(compare(
                            "<=",
                            builtin(
                                "abs",
                                vec![b(
                                    "-",
                                    ix(g(&e, "bore"), json!("radius_mm")),
                                    g(&e, "bore_r")
                                )]
                            ),
                            g(&e, "tol")
                        ))
                    } else {
                        value
                    }
                }) {
                    return Ok(builtin(
                        "sorted",
                        vec![{
                            let mut e = e.clone();
                            let mut temp1 = Vec::new();
                            for item in seq(ix(g(&e, "bore"), json!("centres_mm"))) {
                                e.insert("centre".into(), item);
                                temp1.push(t(seq(g(&e, "centre"))));
                            }
                            json!(temp1)
                        }],
                    ));
                } else {
                }
            }
            bail!(
                "{}",
                string(&json!(
                    [
                        "no bore of r=".to_owned(),
                        format_value(g(&e, "bore_r"), "g")?,
                        " running along ".to_owned(),
                        format_value(g(&e, "axis"), "")?,
                        " — the solid carries ".to_owned(),
                        format_value(
                            builtin(
                                "sorted",
                                vec![{
                                    let mut e = e.clone();
                                    let mut temp2 = Vec::new();
                                    for item in seq(ix(g(&e, "readings"), json!("bores"))) {
                                        e.insert("b".into(), item);
                                        temp2.push(t(vec![
                                            ix(g(&e, "b"), json!("axis")),
                                            ix(g(&e, "b"), json!("radius_mm")),
                                        ]));
                                    }
                                    unique(temp2)
                                }]
                            ),
                            ""
                        )?
                    ]
                    .concat()
                ))
            );
            Ok(Value::Null)
        }
        ("y_divider", "stations_hold") => {
            e.insert(
                "readings".into(),
                parse_json(read_file(cx, g(&e, "MEASUREMENTS"))?)?,
            );
            e.insert("bounds".into(), ix(g(&e, "readings"), json!("bounds_mm")));
            for item in seq(t(vec![
                t(vec![
                    json!("HALF"),
                    g(&e, "HALF"),
                    ix(g(&e, "bounds"), json!("zmax")),
                ]),
                t(vec![
                    json!("HALF_W"),
                    g(&e, "HALF_W"),
                    ix(g(&e, "bounds"), json!("xmax")),
                ]),
            ])) {
                {
                    let temp3 = item;
                    e.insert("name".into(), ix(temp3.clone(), json!(0)));
                    e.insert("claimed".into(), ix(temp3.clone(), json!(1)));
                    e.insert("actual".into(), ix(temp3.clone(), json!(2)));
                }
                if truth(&json!(compare(
                    ">",
                    builtin("abs", vec![b("-", g(&e, "actual"), g(&e, "claimed"))]),
                    g(&e, "MEASURE_TOL")
                ))) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "y-divider ".to_owned(),
                                format_value(g(&e, "name"), "")?,
                                " is ".to_owned(),
                                format_value(g(&e, "claimed"), "g")?,
                                " and the STEP's own is ".to_owned(),
                                format_value(g(&e, "actual"), ".4f")?,
                                " — ".to_owned(),
                                format_value(
                                    builtin("abs", vec![b("-", g(&e, "actual"), g(&e, "claimed"))]),
                                    ".4f"
                                )?,
                                " mm apart, over the ".to_owned(),
                                format_value(g(&e, "MEASURE_TOL"), "g")?,
                                " mm this file rounds to. Every leg placed off ".to_owned(),
                                format_value(g(&e, "name"), "")?,
                                " closes on tube that is not there.".to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
            }
            e.insert("ys".into(), {
                let mut e = e.clone();
                let mut temp4 = Vec::new();
                for item in seq({
                    let argv = vec![
                        g(&e, "readings"),
                        json!("z"),
                        b("/", g(&e, "TUBE_D"), json!(2.0)),
                    ];
                    let kwargs = json!({});
                    call(cx, "y_divider", "_collet_offsets", argv, kwargs, Some(&e))?
                }) {
                    {
                        let temp5 = item;
                        e.insert("_x".into(), ix(temp5.clone(), json!(0)));
                        e.insert("y".into(), ix(temp5.clone(), json!(1)));
                    }
                    temp4.push(g(&e, "y"));
                }
                json!(temp4)
            });
            e.insert(
                "want".into(),
                builtin(
                    "sorted",
                    vec![unique(vec![
                        u("-", g(&e, "OUTLET_Y")),
                        json!(0.0),
                        u("+", g(&e, "OUTLET_Y")),
                    ])],
                ),
            );
            if truth(&{
                let value = json!(compare("!=", builtin("len", vec![g(&e, "ys")]), json!(3)));
                if truth(&value) {
                    value
                } else {
                    json!(compare(
                        ">",
                        builtin(
                            "max",
                            vec![{
                                let mut e = e.clone();
                                let mut temp6 = Vec::new();
                                for item in seq(builtin("zip", vec![g(&e, "ys"), g(&e, "want")])) {
                                    {
                                        let temp7 = item;
                                        e.insert("a".into(), ix(temp7.clone(), json!(0)));
                                        e.insert("b".into(), ix(temp7.clone(), json!(1)));
                                    }
                                    temp6
                                        .push(builtin("abs", vec![b("-", g(&e, "a"), g(&e, "b"))]));
                                }
                                json!(temp6)
                            }]
                        ),
                        g(&e, "MEASURE_TOL")
                    ))
                }
            }) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            "y-divider OUTLET_Y is ".to_owned(),
                            format_value(g(&e, "OUTLET_Y"), "g")?,
                            ", so its three 1/4\" bores should run at y = ".to_owned(),
                            format_value(g(&e, "want"), "")?,
                            "; the STEP's run at ".to_owned(),
                            format_value(g(&e, "ys"), "")?,
                            ". The outlets are not where the legs are aimed.".to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            Ok(Value::Null)
        }
        ("yyfkgcp_pogo_4p", "contact_xs") => {
            return Ok(t(seq({
                let mut e = e.clone();
                let mut temp9 = Vec::new();
                for item in seq(builtin("range", vec![g(&e, "PINS")])) {
                    e.insert("i".into(), item);
                    temp9.push(b(
                        "*",
                        b(
                            "-",
                            g(&e, "i"),
                            b("/", b("-", g(&e, "PINS"), json!(1)), json!(2.0)),
                        ),
                        g(&e, "PIN_PITCH"),
                    ));
                }
                json!(temp9)
            })));
            Ok(Value::Null)
        }
        ("yyfkgcp_pogo_4p", "ear_xs") => {
            return Ok(t(vec![
                b("/", u("-", g(&e, "EAR_PITCH")), json!(2.0)),
                b("/", g(&e, "EAR_PITCH"), json!(2.0)),
            ]));
            Ok(Value::Null)
        }
        ("yyfkgcp_pogo_4p", "ear_back") => {
            return Ok(b("+", g(&e, "EAR_FACE"), g(&e, "EAR_T")));
            Ok(Value::Null)
        }
        ("yyfkgcp_pogo_4p", "reach_back") => {
            return Ok(b("+", g(&e, "BODY_T"), g(&e, "TAIL_L")));
            Ok(Value::Null)
        }
        ("_rotator_interface", "pitch_diameter") => {
            e.insert(
                "teeth".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "teeth"))
                    .unwrap_or_else(|| missing("teeth")),
            );
            return Ok(b(
                "/",
                b("*", g(&e, "teeth"), g(&e, "BELT_PITCH")),
                json!(std::f64::consts::PI),
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "belt_inner_offset") => {
            return Ok(b(
                "+",
                g(&e, "BELT_TOOTH_HEIGHT"),
                g(&e, "BELT_PITCH_LINE_OFFSET"),
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "belt_outer_offset") => {
            return Ok(b("-", g(&e, "BELT_THICKNESS"), {
                let argv = vec![];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "belt_inner_offset",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            }));
            Ok(Value::Null)
        }
        ("_rotator_interface", "belt_center_distance") => {
            e.insert("large".into(), {
                let argv = vec![g(&e, "TABLE_PULLEY_TEETH")];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "pitch_diameter",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            e.insert("small".into(), {
                let argv = vec![g(&e, "MOTOR_PULLEY_TEETH")];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "pitch_diameter",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            e.insert(
                "b".into(),
                b(
                    "-",
                    b(
                        "/",
                        b(
                            "*",
                            json!(std::f64::consts::PI),
                            b("+", g(&e, "large"), g(&e, "small")),
                        ),
                        json!(2.0),
                    ),
                    g(&e, "BELT_PITCH_LENGTH"),
                ),
            );
            e.insert(
                "c".into(),
                b(
                    "/",
                    b("**", b("-", g(&e, "large"), g(&e, "small")), json!(2)),
                    json!(4.0),
                ),
            );
            return Ok(b(
                "/",
                b(
                    "+",
                    u("-", g(&e, "b")),
                    math_fn(
                        "sqrt",
                        vec![b(
                            "-",
                            b("*", g(&e, "b"), g(&e, "b")),
                            b("*", json!(8.0), g(&e, "c")),
                        )],
                    ),
                ),
                json!(4.0),
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "span_tangent_angle") => {
            e.insert(
                "center".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "center"))
                    .unwrap_or_else(|| missing("center")),
            );
            e.insert(
                "large".into(),
                b(
                    "/",
                    {
                        let argv = vec![g(&e, "TABLE_PULLEY_TEETH")];
                        let kwargs = json!({});
                        call(
                            cx,
                            "_rotator_interface",
                            "pitch_diameter",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    },
                    json!(2.0),
                ),
            );
            e.insert(
                "small".into(),
                b(
                    "/",
                    {
                        let argv = vec![g(&e, "MOTOR_PULLEY_TEETH")];
                        let kwargs = json!({});
                        call(
                            cx,
                            "_rotator_interface",
                            "pitch_diameter",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    },
                    json!(2.0),
                ),
            );
            return Ok(math_fn(
                "acos",
                vec![b(
                    "/",
                    b("-", g(&e, "large"), g(&e, "small")),
                    g(&e, "center"),
                )],
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "small_pulley_wrap_degrees") => {
            e.insert("large".into(), {
                let argv = vec![g(&e, "TABLE_PULLEY_TEETH")];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "pitch_diameter",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            e.insert("small".into(), {
                let argv = vec![g(&e, "MOTOR_PULLEY_TEETH")];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "pitch_diameter",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            e.insert("center".into(), {
                let argv = vec![];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "belt_center_distance",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            });
            return Ok(math_fn(
                "degrees",
                vec![b(
                    "-",
                    json!(std::f64::consts::PI),
                    b(
                        "*",
                        json!(2.0),
                        math_fn(
                            "asin",
                            vec![b(
                                "/",
                                b("-", g(&e, "large"), g(&e, "small")),
                                b("*", json!(2.0), g(&e, "center")),
                            )],
                        ),
                    ),
                )],
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "bead_circumference") => {
            return Ok(b("*", json!(std::f64::consts::PI), g(&e, "TUBE_ID")));
            Ok(Value::Null)
        }
        ("_rotator_interface", "table_rpm") => {
            e.insert(
                "travel_mm_s".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "travel_mm_s"))
                    .unwrap_or_else(|| missing("travel_mm_s")),
            );
            return Ok(b("/", b("*", g(&e, "travel_mm_s"), json!(60.0)), {
                let argv = vec![];
                let kwargs = json!({});
                call(
                    cx,
                    "_rotator_interface",
                    "bead_circumference",
                    argv,
                    kwargs,
                    Some(&e),
                )?
            }));
            Ok(Value::Null)
        }
        ("_rotator_interface", "drive_ratio") => {
            return Ok(b(
                "/",
                g(&e, "TABLE_PULLEY_TEETH"),
                g(&e, "MOTOR_PULLEY_TEETH"),
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "motor_rpm") => {
            e.insert(
                "travel_mm_s".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "travel_mm_s"))
                    .unwrap_or_else(|| missing("travel_mm_s")),
            );
            return Ok(b(
                "*",
                {
                    let argv = vec![g(&e, "travel_mm_s")];
                    let kwargs = json!({});
                    call(
                        cx,
                        "_rotator_interface",
                        "table_rpm",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                },
                {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "_rotator_interface",
                        "drive_ratio",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                },
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "pulse_hz") => {
            e.insert(
                "travel_mm_s".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "travel_mm_s"))
                    .unwrap_or_else(|| missing("travel_mm_s")),
            );
            return Ok(b(
                "/",
                b(
                    "*",
                    {
                        let argv = vec![g(&e, "travel_mm_s")];
                        let kwargs = json!({});
                        call(
                            cx,
                            "_rotator_interface",
                            "motor_rpm",
                            argv,
                            kwargs,
                            Some(&e),
                        )?
                    },
                    g(&e, "MOTOR_PULSES_PER_REV"),
                ),
                json!(60.0),
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "table_pulses_per_rev") => {
            return Ok(builtin(
                "int",
                vec![b("*", g(&e, "MOTOR_PULSES_PER_REV"), {
                    let argv = vec![];
                    let kwargs = json!({});
                    call(
                        cx,
                        "_rotator_interface",
                        "drive_ratio",
                        argv,
                        kwargs,
                        Some(&e),
                    )?
                })],
            ));
            Ok(Value::Null)
        }
        ("_rotator_interface", "pulses_for_degrees") => {
            e.insert(
                "degrees".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "degrees"))
                    .unwrap_or_else(|| missing("degrees")),
            );
            return Ok(builtin(
                "round",
                vec![b(
                    "/",
                    b(
                        "*",
                        {
                            let argv = vec![];
                            let kwargs = json!({});
                            call(
                                cx,
                                "_rotator_interface",
                                "table_pulses_per_rev",
                                argv,
                                kwargs,
                                Some(&e),
                            )?
                        },
                        g(&e, "degrees"),
                    ),
                    json!(360.0),
                )],
            ));
            Ok(Value::Null)
        }
        ("_bound", "exact") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "x".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x"))
                    .unwrap_or_else(|| missing("x")),
            );
            e.insert(
                "y".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y"))
                    .unwrap_or_else(|| missing("y")),
            );
            e.insert(
                "z".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "z"))
                    .unwrap_or_else(|| missing("z")),
            );
            e.insert(
                "source".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "source"))
                    .unwrap_or_else(|| missing("source")),
            );
            return Ok({
                let argv = vec![
                    g(&e, "name"),
                    g(&e, "x"),
                    g(&e, "y"),
                    g(&e, "z"),
                    g(&e, "EXACT"),
                    g(&e, "source"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "Env", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("_bound", "parcel") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "x".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x"))
                    .unwrap_or_else(|| missing("x")),
            );
            e.insert(
                "y".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y"))
                    .unwrap_or_else(|| missing("y")),
            );
            e.insert(
                "z".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "z"))
                    .unwrap_or_else(|| missing("z")),
            );
            e.insert(
                "source".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "source"))
                    .unwrap_or_else(|| missing("source")),
            );
            return Ok({
                let argv = vec![
                    g(&e, "name"),
                    g(&e, "x"),
                    g(&e, "y"),
                    g(&e, "z"),
                    g(&e, "MOST"),
                    g(&e, "source"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "Env", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("_bound", "mixed") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "x".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x"))
                    .unwrap_or_else(|| missing("x")),
            );
            e.insert(
                "y".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y"))
                    .unwrap_or_else(|| missing("y")),
            );
            e.insert(
                "z".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "z"))
                    .unwrap_or_else(|| missing("z")),
            );
            e.insert(
                "source".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "source"))
                    .unwrap_or_else(|| missing("source")),
            );
            e.insert(
                "bounds".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "bounds"))
                    .unwrap_or_else(|| missing("bounds")),
            );
            return Ok({
                let argv = vec![
                    g(&e, "name"),
                    g(&e, "x"),
                    g(&e, "y"),
                    g(&e, "z"),
                    t(seq(g(&e, "bounds"))),
                    g(&e, "source"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "Env", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("_bound", "bore") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "diameter".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "diameter"))
                    .unwrap_or_else(|| missing("diameter")),
            );
            e.insert(
                "length".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length"))
                    .unwrap_or_else(|| missing("length")),
            );
            e.insert(
                "source".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "source"))
                    .unwrap_or_else(|| missing("source")),
            );
            return Ok({
                let argv = vec![
                    g(&e, "name"),
                    g(&e, "diameter"),
                    g(&e, "diameter"),
                    g(&e, "length"),
                    g(&e, "EXACT"),
                    g(&e, "source"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "Env", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("_bound", "heap") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "count".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            e.insert(
                "piece_envelope".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "piece_envelope"))
                    .unwrap_or_else(|| missing("piece_envelope")),
            );
            e.insert(
                "source".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "source"))
                    .unwrap_or_else(|| missing("source")),
            );
            e.insert(
                "nest".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "nest"))
                    .unwrap_or_else(|| g(&e, "NEST_COMPACT")),
            );
            e.insert(
                "side".into(),
                b(
                    "**",
                    b(
                        "*",
                        b("*", g(&e, "count"), g(&e, "piece_envelope")),
                        g(&e, "nest"),
                    ),
                    b("/", json!(1.0), json!(3.0)),
                ),
            );
            return Ok({
                let argv = vec![
                    g(&e, "name"),
                    g(&e, "side"),
                    g(&e, "side"),
                    g(&e, "side"),
                    g(&e, "EXACT"),
                    g(&e, "source"),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "Heap", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("_kit", "outer_size") => {
            e.insert(
                "units".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "units"))
                    .unwrap_or_else(|| missing("units")),
            );
            return Ok(b(
                "-",
                b("*", g(&e, "units"), g(&e, "grid_unit")),
                g(&e, "grid_clearance"),
            ));
            Ok(Value::Null)
        }
        ("_kit", "inner_size") => {
            e.insert(
                "units".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "units"))
                    .unwrap_or_else(|| missing("units")),
            );
            return Ok(b(
                "-",
                {
                    let argv = vec![g(&e, "units")];
                    let kwargs = json!({});
                    call(cx, "_kit", "outer_size", argv, kwargs, Some(&e))?
                },
                b("*", json!(2.0), g(&e, "wall_thickness")),
            ));
            Ok(Value::Null)
        }
        ("_kit", "top_reference_z") => {
            e.insert(
                "height_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            return Ok(b("*", g(&e, "height_u"), g(&e, "height_unit")));
            Ok(Value::Null)
        }
        ("_kit", "plateau_half") => {
            e.insert(
                "units".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "units"))
                    .unwrap_or_else(|| missing("units")),
            );
            return Ok(b(
                "-",
                b(
                    "/",
                    {
                        let argv = vec![g(&e, "units")];
                        let kwargs = json!({});
                        call(cx, "_kit", "outer_size", argv, kwargs, Some(&e))?
                    },
                    json!(2.0),
                ),
                g(&e, "lip_inset"),
            ));
            Ok(Value::Null)
        }
        ("_kit", "interior_ceiling_z") => {
            e.insert(
                "height_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "height".into(),
                b(
                    "+",
                    ix(g(&e, "_STOCK"), json!("height_offset_mm")),
                    b("*", g(&e, "GRHU"), g(&e, "height_u")),
                ),
            );
            return Ok(b(
                "+",
                g(&e, "bin_floor_z"),
                b(
                    "-",
                    b("-", g(&e, "height"), g(&e, "GR_LIP_H")),
                    g(&e, "GR_BOT_H"),
                ),
            ));
            Ok(Value::Null)
        }
        ("_kit", "cell_span") => {
            e.insert(
                "units".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "units"))
                    .unwrap_or_else(|| missing("units")),
            );
            e.insert(
                "divisions".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "divisions"))
                    .unwrap_or_else(|| missing("divisions")),
            );
            return Ok(b(
                "/",
                b(
                    "-",
                    {
                        let argv = vec![g(&e, "units")];
                        let kwargs = json!({});
                        call(cx, "_kit", "inner_size", argv, kwargs, Some(&e))?
                    },
                    b("*", g(&e, "divider_thickness"), g(&e, "divisions")),
                ),
                b("+", g(&e, "divisions"), json!(1)),
            ));
            Ok(Value::Null)
        }
        ("_holder", "tub_holds") => {
            e.insert(
                "x_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "length_div".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            e.insert(
                "width_div".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "width_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            return Ok(t(vec![
                {
                    let argv = vec![g(&e, "x_u"), g(&e, "length_div")];
                    let kwargs = json!({});
                    call(cx, "_kit", "cell_span", argv, kwargs, None)?
                },
                {
                    let argv = vec![g(&e, "y_u"), g(&e, "width_div")];
                    let kwargs = json!({});
                    call(cx, "_kit", "cell_span", argv, kwargs, None)?
                },
                b(
                    "-",
                    {
                        let argv = vec![g(&e, "height_u")];
                        let kwargs = json!({});
                        call(cx, "_kit", "interior_ceiling_z", argv, kwargs, None)?
                    },
                    attr(cx, "_kit", "bin_floor_z")?,
                ),
            ]));
            Ok(Value::Null)
        }
        ("_holder", "assert_tub_takes") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "env".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "env"))
                    .unwrap_or_else(|| missing("env")),
            );
            e.insert(
                "x_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "length_div".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            e.insert(
                "width_div".into(),
                args.get(6)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "width_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            {
                let temp1 = {
                    let argv = vec![
                        g(&e, "x_u"),
                        g(&e, "y_u"),
                        g(&e, "height_u"),
                        g(&e, "length_div"),
                        g(&e, "width_div"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "tub_holds", argv, kwargs, Some(&e))?
                };
                e.insert("clear_x".into(), ix(temp1.clone(), json!(0)));
                e.insert("clear_y".into(), ix(temp1.clone(), json!(1)));
                e.insert("clear_z".into(), ix(temp1.clone(), json!(2)));
            }
            let _ = {
                let message = vec![string(&json!(
                    [
                        "   ".to_owned(),
                        format_value(g(&e, "name"), "")?,
                        ": ".to_owned(),
                        format_value(attr_value(g(&e, "env"), "name"), "")?,
                        " in ".to_owned(),
                        format_value(g(&e, "clear_x"), ".1f")?,
                        " x ".to_owned(),
                        format_value(g(&e, "clear_y"), ".1f")?,
                        " x ".to_owned(),
                        format_value(g(&e, "clear_z"), ".1f")?,
                        " mm, ".to_owned(),
                        format_value(
                            builtin(
                                "min",
                                vec![
                                    b(
                                        "-",
                                        g(&e, "clear_x"),
                                        storage::method(g(&e, "env"), "most", vec![json!("x")])?
                                    ),
                                    b(
                                        "-",
                                        g(&e, "clear_y"),
                                        storage::method(g(&e, "env"), "most", vec![json!("y")])?
                                    ),
                                    b(
                                        "-",
                                        g(&e, "clear_z"),
                                        storage::method(g(&e, "env"), "most", vec![json!("z")])?
                                    )
                                ]
                            ),
                            ".1f"
                        )?,
                        " mm spare".to_owned()
                    ]
                    .concat()
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            Ok(Value::Null)
        }
        ("_holder", "tub_height_for") => {
            e.insert(
                "x_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "takes".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "takes"))
                    .unwrap_or_else(|| missing("takes")),
            );
            e.insert(
                "length_div".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            e.insert(
                "width_div".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "width_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            e.insert(
                "headroom".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "headroom"))
                    .unwrap_or_else(|| json!(4.0)),
            );
            e.insert(
                "margin".into(),
                args.get(6)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "margin"))
                    .unwrap_or_else(|| g(&e, "slip")),
            );
            e.insert(
                "limit".into(),
                args.get(7)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "limit"))
                    .unwrap_or_else(|| json!(30)),
            );
            {
                let temp2 = {
                    let argv = vec![
                        g(&e, "x_u"),
                        g(&e, "y_u"),
                        json!(2),
                        g(&e, "length_div"),
                        g(&e, "width_div"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "tub_holds", argv, kwargs, Some(&e))?
                };
                e.insert("clear_x".into(), ix(temp2.clone(), json!(0)));
                e.insert("clear_y".into(), ix(temp2.clone(), json!(1)));
                e.insert("_".into(), ix(temp2.clone(), json!(2)));
            }
            for item in seq(g(&e, "takes")) {
                e.insert("env".into(), item);
                if truth(&builtin(
                    "isinstance",
                    vec![g(&e, "env"), json!({"$class":"Heap"})],
                )) {
                    continue;
                } else {
                }
                for item in seq(t(vec![
                    t(vec![json!("x"), g(&e, "clear_x")]),
                    t(vec![json!("y"), g(&e, "clear_y")]),
                ])) {
                    {
                        let temp3 = item;
                        e.insert("axis".into(), ix(temp3.clone(), json!(0)));
                        e.insert("clear".into(), ix(temp3.clone(), json!(1)));
                    }
                    if truth(&json!(compare(
                        ">",
                        b(
                            "+",
                            storage::method(g(&e, "env"), "most", vec![g(&e, "axis")])?,
                            g(&e, "margin")
                        ),
                        g(&e, "clear")
                    ))) {
                        bail!("{}",string(&json!([format_value(attr_value(g(&e,"env"),"name"),"")?," is ".to_owned(),format_value(storage::method(g(&e,"env"),"most",vec![g(&e,"axis")])?,".1f")?," mm in ".to_owned(),format_value(g(&e,"axis"),"")?," and a ".to_owned(),format_value(g(&e,"x_u"),"")?,"x".to_owned(),format_value(g(&e,"y_u"),"")?," split ".to_owned(),format_value(g(&e,"length_div"),"")?," x ".to_owned(),format_value(g(&e,"width_div"),"")?," offers ".to_owned(),format_value(g(&e,"clear"),".1f")?," mm. No depth fixes a footprint: split it less, or stand it on a wider one.".to_owned()].concat())));
                    } else {
                    }
                }
            }
            for item in seq(builtin(
                "range",
                vec![json!(2), b("+", g(&e, "limit"), json!(1))],
            )) {
                e.insert("height_u".into(), item);
                {
                    let temp4 = {
                        let argv = vec![
                            g(&e, "x_u"),
                            g(&e, "y_u"),
                            g(&e, "height_u"),
                            g(&e, "length_div"),
                            g(&e, "width_div"),
                        ];
                        let kwargs = json!({});
                        call(cx, "_holder", "tub_holds", argv, kwargs, Some(&e))?
                    };
                    e.insert("clear_x".into(), ix(temp4.clone(), json!(0)));
                    e.insert("clear_y".into(), ix(temp4.clone(), json!(1)));
                    e.insert("clear_z".into(), ix(temp4.clone(), json!(2)));
                }
                e.insert(
                    "floor".into(),
                    b(
                        "*",
                        b("-", g(&e, "clear_x"), b("*", json!(2.0), g(&e, "margin"))),
                        b("-", g(&e, "clear_y"), b("*", json!(2.0), g(&e, "margin"))),
                    ),
                );
                if truth(&json!(compare("<=", g(&e, "floor"), json!(0.0)))) {
                    continue;
                } else {
                }
                e.insert("deepest".into(), json!(0.0));
                for item in seq(g(&e, "takes")) {
                    e.insert("env".into(), item);
                    if truth(&builtin(
                        "isinstance",
                        vec![g(&e, "env"), json!({"$class":"Heap"})],
                    )) {
                        e.insert(
                            "deepest".into(),
                            builtin(
                                "max",
                                vec![
                                    g(&e, "deepest"),
                                    b(
                                        "+",
                                        b("/", attr_value(g(&e, "env"), "volume"), g(&e, "floor")),
                                        g(&e, "headroom"),
                                    ),
                                ],
                            ),
                        );
                    } else {
                        e.insert(
                            "deepest".into(),
                            builtin(
                                "max",
                                vec![
                                    g(&e, "deepest"),
                                    b(
                                        "+",
                                        storage::method(g(&e, "env"), "most", vec![json!("z")])?,
                                        g(&e, "margin"),
                                    ),
                                ],
                            ),
                        );
                    }
                }
                if truth(&json!(compare("<=", g(&e, "deepest"), g(&e, "clear_z")))) {
                    return Ok(g(&e, "height_u"));
                } else {
                }
            }
            bail!(
                "{}",
                string(&json!(
                    [
                        "nothing under ".to_owned(),
                        format_value(g(&e, "limit"), "")?,
                        " units takes ".to_owned(),
                        format_value(builtin("len", vec![g(&e, "takes")]), "")?,
                        " things on a ".to_owned(),
                        format_value(g(&e, "x_u"), "")?,
                        "x".to_owned(),
                        format_value(g(&e, "y_u"), "")?,
                        " footprint split ".to_owned(),
                        format_value(g(&e, "length_div"), "")?,
                        " x ".to_owned(),
                        format_value(g(&e, "width_div"), "")?
                    ]
                    .concat()
                ))
            );
            Ok(Value::Null)
        }
        ("_holder", "assert_heap_fits") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "env".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "env"))
                    .unwrap_or_else(|| missing("env")),
            );
            e.insert(
                "x_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "length_div".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            e.insert(
                "width_div".into(),
                args.get(6)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "width_div"))
                    .unwrap_or_else(|| json!(0)),
            );
            {
                let temp5 = {
                    let argv = vec![
                        g(&e, "x_u"),
                        g(&e, "y_u"),
                        g(&e, "height_u"),
                        g(&e, "length_div"),
                        g(&e, "width_div"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "tub_holds", argv, kwargs, Some(&e))?
                };
                e.insert("clear_x".into(), ix(temp5.clone(), json!(0)));
                e.insert("clear_y".into(), ix(temp5.clone(), json!(1)));
                e.insert("clear_z".into(), ix(temp5.clone(), json!(2)));
            }
            e.insert(
                "floor".into(),
                b(
                    "*",
                    b("-", g(&e, "clear_x"), b("*", json!(2.0), g(&e, "slip"))),
                    b("-", g(&e, "clear_y"), b("*", json!(2.0), g(&e, "slip"))),
                ),
            );
            e.insert(
                "stands".into(),
                b("/", attr_value(g(&e, "env"), "volume"), g(&e, "floor")),
            );
            let _ = {
                let message = vec![string(&json!(
                    [
                        "   ".to_owned(),
                        format_value(g(&e, "name"), "")?,
                        ": ".to_owned(),
                        format_value(attr_value(g(&e, "env"), "name"), "")?,
                        " stands ".to_owned(),
                        format_value(g(&e, "stands"), ".1f")?,
                        " mm of ".to_owned(),
                        format_value(g(&e, "clear_z"), ".1f")?,
                        " mm".to_owned()
                    ]
                    .concat()
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            return Ok(g(&e, "stands"));
            Ok(Value::Null)
        }
        ("_holder", "cradle_profile") => {
            e.insert(
                "x_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "end_wall".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "end_wall"))
                    .unwrap_or_else(|| g(&e, "wall")),
            );
            e.insert(
                "vertex_flat".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "vertex_flat"))
                    .unwrap_or_else(|| json!(2.0)),
            );
            e.insert("top_z".into(), {
                let argv = vec![g(&e, "height_u")];
                let kwargs = json!({});
                call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
            });
            {
                let temp6 = {
                    let argv = vec![
                        g(&e, "x_u"),
                        g(&e, "y_u"),
                        g(&e, "height_u"),
                        g(&e, "end_wall"),
                        g(&e, "vertex_flat"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "cradle_trough", argv, kwargs, Some(&e))?
                };
                e.insert("half_mouth".into(), ix(temp6.clone(), json!(0)));
                e.insert("depth".into(), ix(temp6.clone(), json!(1)));
                e.insert("length".into(), ix(temp6.clone(), json!(2)));
            }
            e.insert("half_mouth".into(), b("/", g(&e, "half_mouth"), json!(2.0)));
            e.insert(
                "profile".into(),
                json!([
                    (t(vec![
                        u("-", g(&e, "half_mouth")),
                        b("+", g(&e, "top_z"), json!(0.2))
                    ])),
                    (t(vec![
                        b("/", u("-", g(&e, "vertex_flat")), json!(2.0)),
                        b("-", g(&e, "top_z"), g(&e, "depth"))
                    ])),
                    (t(vec![
                        b("/", g(&e, "vertex_flat"), json!(2.0)),
                        b("-", g(&e, "top_z"), g(&e, "depth"))
                    ])),
                    (t(vec![
                        g(&e, "half_mouth"),
                        b("+", g(&e, "top_z"), json!(0.2))
                    ]))
                ]),
            );
            return Ok(t(vec![g(&e, "profile"), g(&e, "length")]));
            Ok(Value::Null)
        }
        ("_holder", "cradle_trough") => {
            e.insert(
                "x_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "end_wall".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "end_wall"))
                    .unwrap_or_else(|| g(&e, "wall")),
            );
            e.insert(
                "vertex_flat".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "vertex_flat"))
                    .unwrap_or_else(|| json!(2.0)),
            );
            e.insert("top_z".into(), {
                let argv = vec![g(&e, "height_u")];
                let kwargs = json!({});
                call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
            });
            e.insert(
                "half_mouth".into(),
                builtin(
                    "min",
                    vec![
                        b(
                            "+",
                            b("/", g(&e, "vertex_flat"), json!(2.0)),
                            b("-", g(&e, "top_z"), attr(cx, "_kit", "bin_floor_z")?),
                        ),
                        b(
                            "-",
                            {
                                let argv = vec![g(&e, "y_u")];
                                let kwargs = json!({});
                                call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                            },
                            g(&e, "wall"),
                        ),
                    ],
                ),
            );
            e.insert(
                "depth".into(),
                b(
                    "-",
                    g(&e, "half_mouth"),
                    b("/", g(&e, "vertex_flat"), json!(2.0)),
                ),
            );
            e.insert(
                "length".into(),
                b(
                    "*",
                    json!(2.0),
                    b(
                        "-",
                        {
                            let argv = vec![g(&e, "x_u")];
                            let kwargs = json!({});
                            call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                        },
                        g(&e, "end_wall"),
                    ),
                ),
            );
            return Ok(t(vec![
                b("*", json!(2.0), g(&e, "half_mouth")),
                g(&e, "depth"),
                g(&e, "length"),
            ]));
            Ok(Value::Null)
        }
        ("_holder", "cradle_seat") => {
            e.insert(
                "mouth".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "mouth"))
                    .unwrap_or_else(|| missing("mouth")),
            );
            e.insert(
                "depth".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "depth"))
                    .unwrap_or_else(|| missing("depth")),
            );
            e.insert(
                "diameter".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "diameter"))
                    .unwrap_or_else(|| missing("diameter")),
            );
            e.insert(
                "vertex_flat".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "vertex_flat"))
                    .unwrap_or_else(|| json!(2.0)),
            );
            e.insert("radius".into(), b("/", g(&e, "diameter"), json!(2.0)));
            e.insert("half_mouth".into(), b("/", g(&e, "mouth"), json!(2.0)));
            if truth(&json!(compare(
                "<=",
                b("/", g(&e, "radius"), b("**", json!(2.0), json!(0.5))),
                g(&e, "half_mouth")
            ))) {
                return Ok(b(
                    "-",
                    b("*", g(&e, "radius"), b("**", json!(2.0), json!(0.5))),
                    g(&e, "depth"),
                ));
            } else {
            }
            return Ok(b(
                "**",
                b(
                    "-",
                    b("**", g(&e, "radius"), json!(2)),
                    b("**", g(&e, "half_mouth"), json!(2)),
                ),
                json!(0.5),
            ));
            Ok(Value::Null)
        }
        ("_holder", "assert_cradle_takes") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "env".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "env"))
                    .unwrap_or_else(|| missing("env")),
            );
            e.insert(
                "x_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "end_wall".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "end_wall"))
                    .unwrap_or_else(|| g(&e, "wall")),
            );
            {
                let temp7 = {
                    let argv = vec![
                        g(&e, "x_u"),
                        g(&e, "y_u"),
                        g(&e, "height_u"),
                        g(&e, "end_wall"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "cradle_trough", argv, kwargs, Some(&e))?
                };
                e.insert("mouth".into(), ix(temp7.clone(), json!(0)));
                e.insert("depth".into(), ix(temp7.clone(), json!(1)));
                e.insert("length".into(), ix(temp7.clone(), json!(2)));
            }
            e.insert("width".into(), attr_value(g(&e, "env"), "thinnest"));
            e.insert("across".into(), attr_value(g(&e, "env"), "longest"));
            if truth(&json!(compare(
                ">",
                b("+", g(&e, "width"), g(&e, "slip")),
                g(&e, "length")
            ))) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            format_value(g(&e, "name"), "")?,
                            ": ".to_owned(),
                            format_value(attr_value(g(&e, "env"), "name"), "")?,
                            " is up to ".to_owned(),
                            format_value(g(&e, "width"), ".1f")?,
                            " mm wide in a ".to_owned(),
                            format_value(g(&e, "length"), ".1f")?,
                            " mm trough".to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            e.insert("rides".into(), {
                let argv = vec![g(&e, "mouth"), g(&e, "depth"), g(&e, "across")];
                let kwargs = json!({});
                call(cx, "_holder", "cradle_seat", argv, kwargs, Some(&e))?
            });
            e.insert(
                "overhang".into(),
                b(
                    "-",
                    b("-", b("/", g(&e, "across"), json!(2.0)), g(&e, "rides")),
                    b(
                        "/",
                        {
                            let argv = vec![g(&e, "y_u")];
                            let kwargs = json!({});
                            call(cx, "_kit", "outer_size", argv, kwargs, None)?
                        },
                        json!(2.0),
                    ),
                ),
            );
            let _ = {
                let message = vec![string(&json!(
                    [
                        "   ".to_owned(),
                        format_value(g(&e, "name"), "")?,
                        ": ".to_owned(),
                        format_value(attr_value(g(&e, "env"), "name"), "")?,
                        " up to ".to_owned(),
                        format_value(g(&e, "width"), ".1f")?,
                        " mm wide and ".to_owned(),
                        format_value(g(&e, "across"), ".1f")?,
                        " mm across, in a ".to_owned(),
                        format_value(g(&e, "mouth"), ".1f")?,
                        " mm mouth ".to_owned(),
                        format_value(g(&e, "depth"), ".1f")?,
                        " mm deep over ".to_owned(),
                        format_value(g(&e, "length"), ".1f")?,
                        " mm; riding ".to_owned(),
                        format_value(g(&e, "rides"), "+.1f")?,
                        " mm on the plateau and standing ".to_owned(),
                        format_value(b("+", g(&e, "across"), g(&e, "rides")), ".0f")?,
                        " mm over the bench".to_owned()
                    ]
                    .concat()
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            if truth(&json!(compare(">", g(&e, "overhang"), json!(0.0)))) {
                let _ = {
                    let message=vec![string(&json!(["   ".to_owned(),format_value(g(&e,"name"),"")?,": and reaching ".to_owned(),format_value(g(&e,"overhang"),".1f")?," mm past the module in Y at its widest, so nothing tall stands beside it".to_owned()].concat()))].join(" ");
                    cx.messages.push(message);
                    Value::Null
                };
            } else {
            }
            return Ok(g(&e, "rides"));
            Ok(Value::Null)
        }
        ("_holder", "spacer_profile") => {
            e.insert(
                "width".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "width"))
                    .unwrap_or_else(|| missing("width")),
            );
            e.insert(
                "x_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "end_wall".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "end_wall"))
                    .unwrap_or_else(|| g(&e, "wall")),
            );
            e.insert(
                "vertex_flat".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "vertex_flat"))
                    .unwrap_or_else(|| json!(2.0)),
            );
            {
                let temp8 = {
                    let argv = vec![
                        g(&e, "x_u"),
                        g(&e, "y_u"),
                        g(&e, "height_u"),
                        g(&e, "end_wall"),
                        g(&e, "vertex_flat"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "cradle_trough", argv, kwargs, Some(&e))?
                };
                e.insert("mouth".into(), ix(temp8.clone(), json!(0)));
                e.insert("depth".into(), ix(temp8.clone(), json!(1)));
                e.insert("_".into(), ix(temp8.clone(), json!(2)));
            }
            e.insert(
                "half_mouth".into(),
                b("-", b("/", g(&e, "mouth"), json!(2.0)), json!(0.4)),
            );
            e.insert(
                "profile".into(),
                json!([
                    (t(vec![u("-", g(&e, "half_mouth")), json!(0.0)])),
                    (t(vec![
                        b("/", u("-", g(&e, "vertex_flat")), json!(2.0)),
                        g(&e, "depth")
                    ])),
                    (t(vec![
                        b("/", g(&e, "vertex_flat"), json!(2.0)),
                        g(&e, "depth")
                    ])),
                    (t(vec![g(&e, "half_mouth"), json!(0.0)]))
                ]),
            );
            return Ok(g(&e, "profile"));
            Ok(Value::Null)
        }
        ("_holder", "slot_mouth_for") => {
            e.insert(
                "env".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "env"))
                    .unwrap_or_else(|| missing("env")),
            );
            e.insert(
                "clearance".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "clearance"))
                    .unwrap_or_else(|| json!(2.0)),
            );
            e.insert(
                "least".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "least"))
                    .unwrap_or_else(|| json!(8.0)),
            );
            return Ok(builtin(
                "max",
                vec![
                    g(&e, "least"),
                    b(
                        "+",
                        attr_value(g(&e, "env"), "thinnest"),
                        g(&e, "clearance"),
                    ),
                ],
            ));
            Ok(Value::Null)
        }
        ("_holder", "comb_layout") => {
            e.insert(
                "x_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "mouths".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "mouths"))
                    .unwrap_or_else(|| missing("mouths")),
            );
            e.insert(
                "root".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "root"))
                    .unwrap_or_else(|| g(&e, "slot_root")),
            );
            e.insert(
                "floor".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "floor"))
                    .unwrap_or_else(|| g(&e, "slot_floor")),
            );
            e.insert(
                "taper".into(),
                args.get(6)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "taper"))
                    .unwrap_or_else(|| g(&e, "slot_taper")),
            );
            e.insert("top_z".into(), {
                let argv = vec![g(&e, "height_u")];
                let kwargs = json!({});
                call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
            });
            e.insert(
                "floor_z".into(),
                b("+", attr(cx, "_kit", "bin_floor_z")?, g(&e, "floor")),
            );
            e.insert("throat_z".into(), b("+", g(&e, "floor_z"), g(&e, "taper")));
            if truth(&json!(compare(">=", g(&e, "throat_z"), g(&e, "top_z")))) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            "a ".to_owned(),
                            format_value(g(&e, "taper"), ".1f")?,
                            " mm taper leaves no throat in a ".to_owned(),
                            format_value(b("-", g(&e, "top_z"), g(&e, "floor_z")), ".1f")?,
                            " mm slot".to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            e.insert(
                "length".into(),
                b(
                    "*",
                    json!(2.0),
                    b(
                        "-",
                        {
                            let argv = vec![g(&e, "y_u")];
                            let kwargs = json!({});
                            call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                        },
                        g(&e, "wall"),
                    ),
                ),
            );
            e.insert(
                "run".into(),
                b(
                    "*",
                    json!(2.0),
                    b(
                        "-",
                        {
                            let argv = vec![g(&e, "x_u")];
                            let kwargs = json!({});
                            call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                        },
                        g(&e, "wall"),
                    ),
                ),
            );
            e.insert(
                "span".into(),
                b(
                    "+",
                    builtin("sum", vec![g(&e, "mouths")]),
                    b(
                        "*",
                        g(&e, "wall"),
                        b("-", builtin("len", vec![g(&e, "mouths")]), json!(1)),
                    ),
                ),
            );
            if truth(&json!(compare(">", g(&e, "span"), g(&e, "run")))) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            format_value(builtin("len", vec![g(&e, "mouths")]), "")?,
                            " slots run ".to_owned(),
                            format_value(g(&e, "span"), ".1f")?,
                            " mm over a ".to_owned(),
                            format_value(g(&e, "run"), ".1f")?,
                            " mm plateau".to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            e.insert("profiles".into(), json!([]));
            e.insert("x".into(), b("/", u("-", g(&e, "span")), json!(2.0)));
            for item in seq(g(&e, "mouths")) {
                e.insert("mouth".into(), item);
                e.insert(
                    "x".into(),
                    b("+", g(&e, "x"), b("/", g(&e, "mouth"), json!(2.0))),
                );
                e.insert(
                    "profile".into(),
                    json!([
                        (t(vec![
                            b("-", g(&e, "x"), b("/", g(&e, "mouth"), json!(2.0))),
                            b("+", g(&e, "top_z"), json!(0.2))
                        ])),
                        (t(vec![
                            b("-", g(&e, "x"), b("/", g(&e, "mouth"), json!(2.0))),
                            g(&e, "throat_z")
                        ])),
                        (t(vec![
                            b("-", g(&e, "x"), b("/", g(&e, "root"), json!(2.0))),
                            g(&e, "floor_z")
                        ])),
                        (t(vec![
                            b("+", g(&e, "x"), b("/", g(&e, "root"), json!(2.0))),
                            g(&e, "floor_z")
                        ])),
                        (t(vec![
                            b("+", g(&e, "x"), b("/", g(&e, "mouth"), json!(2.0))),
                            g(&e, "throat_z")
                        ])),
                        (t(vec![
                            b("+", g(&e, "x"), b("/", g(&e, "mouth"), json!(2.0))),
                            b("+", g(&e, "top_z"), json!(0.2))
                        ]))
                    ]),
                );
                {
                    let item = g(&e, "profile");
                    mutate(&mut e, "profiles", "append", item);
                }
                e.insert(
                    "x".into(),
                    b(
                        "+",
                        g(&e, "x"),
                        b("+", b("/", g(&e, "mouth"), json!(2.0)), g(&e, "wall")),
                    ),
                );
            }
            return Ok(t(vec![g(&e, "profiles"), g(&e, "length")]));
            Ok(Value::Null)
        }
        ("_holder", "comb_slot") => {
            e.insert(
                "y_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "mouth".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "mouth"))
                    .unwrap_or_else(|| missing("mouth")),
            );
            e.insert(
                "root".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "root"))
                    .unwrap_or_else(|| g(&e, "slot_root")),
            );
            e.insert(
                "floor".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "floor"))
                    .unwrap_or_else(|| g(&e, "slot_floor")),
            );
            e.insert(
                "depth".into(),
                b(
                    "-",
                    {
                        let argv = vec![g(&e, "height_u")];
                        let kwargs = json!({});
                        call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
                    },
                    b("+", attr(cx, "_kit", "bin_floor_z")?, g(&e, "floor")),
                ),
            );
            return Ok(t(vec![
                g(&e, "mouth"),
                g(&e, "root"),
                g(&e, "depth"),
                b(
                    "*",
                    json!(2.0),
                    b(
                        "-",
                        {
                            let argv = vec![g(&e, "y_u")];
                            let kwargs = json!({});
                            call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                        },
                        g(&e, "wall"),
                    ),
                ),
            ]));
            Ok(Value::Null)
        }
        ("_holder", "comb_grip") => {
            e.insert(
                "depth".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "depth"))
                    .unwrap_or_else(|| missing("depth")),
            );
            e.insert(
                "thickness".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "thickness"))
                    .unwrap_or_else(|| missing("thickness")),
            );
            e.insert(
                "mouth".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "mouth"))
                    .unwrap_or_else(|| missing("mouth")),
            );
            e.insert(
                "root".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "root"))
                    .unwrap_or_else(|| g(&e, "slot_root")),
            );
            e.insert(
                "taper".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "taper"))
                    .unwrap_or_else(|| g(&e, "slot_taper")),
            );
            e.insert("throat".into(), b("-", g(&e, "depth"), g(&e, "taper")));
            if truth(&json!(compare(">=", g(&e, "thickness"), g(&e, "mouth")))) {
                return Ok(g(&e, "throat"));
            } else {
            }
            if truth(&json!(compare("<=", g(&e, "thickness"), g(&e, "root")))) {
                return Ok(g(&e, "depth"));
            } else {
            }
            return Ok(b(
                "+",
                g(&e, "throat"),
                b(
                    "/",
                    b(
                        "*",
                        g(&e, "taper"),
                        b("-", g(&e, "mouth"), g(&e, "thickness")),
                    ),
                    b("-", g(&e, "mouth"), g(&e, "root")),
                ),
            ));
            Ok(Value::Null)
        }
        ("_holder", "assert_comb_takes") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "env".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "env"))
                    .unwrap_or_else(|| missing("env")),
            );
            e.insert(
                "y_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "mouth".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "mouth"))
                    .unwrap_or_else(|| missing("mouth")),
            );
            e.insert(
                "root".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "root"))
                    .unwrap_or_else(|| g(&e, "slot_root")),
            );
            e.insert(
                "floor".into(),
                args.get(6)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "floor"))
                    .unwrap_or_else(|| g(&e, "slot_floor")),
            );
            e.insert(
                "taper".into(),
                args.get(7)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "taper"))
                    .unwrap_or_else(|| g(&e, "slot_taper")),
            );
            {
                let temp9 = {
                    let argv = vec![
                        g(&e, "y_u"),
                        g(&e, "height_u"),
                        g(&e, "mouth"),
                        g(&e, "root"),
                        g(&e, "floor"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "comb_slot", argv, kwargs, Some(&e))?
                };
                e.insert("mouth_w".into(), ix(temp9.clone(), json!(0)));
                e.insert("root_w".into(), ix(temp9.clone(), json!(1)));
                e.insert("depth".into(), ix(temp9.clone(), json!(2)));
                e.insert("length".into(), ix(temp9.clone(), json!(3)));
            }
            e.insert("thick".into(), attr_value(g(&e, "env"), "thinnest"));
            e.insert(
                "across".into(),
                ix(
                    builtin(
                        "sorted",
                        vec![t(vec![
                            attr_value(g(&e, "env"), "x"),
                            attr_value(g(&e, "env"), "y"),
                            attr_value(g(&e, "env"), "z"),
                        ])],
                    ),
                    json!(1),
                ),
            );
            if truth(&json!(compare(">", g(&e, "across"), g(&e, "length")))) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            format_value(g(&e, "name"), "")?,
                            ": ".to_owned(),
                            format_value(attr_value(g(&e, "env"), "name"), "")?,
                            " is up to ".to_owned(),
                            format_value(g(&e, "across"), ".1f")?,
                            " mm across a ".to_owned(),
                            format_value(g(&e, "length"), ".1f")?,
                            " mm slot".to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            e.insert("grip".into(), {
                let argv = vec![
                    g(&e, "depth"),
                    g(&e, "thick"),
                    g(&e, "mouth_w"),
                    g(&e, "root_w"),
                    g(&e, "taper"),
                ];
                let kwargs = json!({});
                call(cx, "_holder", "comb_grip", argv, kwargs, Some(&e))?
            });
            e.insert(
                "stands".into(),
                b("-", attr_value(g(&e, "env"), "longest"), g(&e, "grip")),
            );
            e.insert(
                "lean".into(),
                b(
                    "/",
                    b(
                        "*",
                        attr_value(g(&e, "env"), "longest"),
                        b("-", g(&e, "mouth_w"), g(&e, "thick")),
                    ),
                    g(&e, "grip"),
                ),
            );
            let _ = {
                let message = vec![string(&json!(
                    [
                        "   ".to_owned(),
                        format_value(g(&e, "name"), "")?,
                        ": ".to_owned(),
                        format_value(attr_value(g(&e, "env"), "name"), "")?,
                        " up to ".to_owned(),
                        format_value(g(&e, "thick"), ".1f")?,
                        " mm thick in a ".to_owned(),
                        format_value(g(&e, "mouth_w"), ".1f")?,
                        " mm mouth, held over ".to_owned(),
                        format_value(g(&e, "grip"), ".1f")?,
                        " mm, standing ".to_owned(),
                        format_value(g(&e, "stands"), ".0f")?,
                        " mm proud, leaning at most ".to_owned(),
                        format_value(g(&e, "lean"), ".0f")?,
                        " mm".to_owned()
                    ]
                    .concat()
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            return Ok(g(&e, "stands"));
            Ok(Value::Null)
        }
        ("_holder", "index_layout") => {
            e.insert(
                "x_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "x_u"))
                    .unwrap_or_else(|| missing("x_u")),
            );
            e.insert(
                "y_u".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "y_u"))
                    .unwrap_or_else(|| missing("y_u")),
            );
            e.insert(
                "height_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "rows".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "rows"))
                    .unwrap_or_else(|| missing("rows")),
            );
            e.insert(
                "depth".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "depth"))
                    .unwrap_or_else(|| Value::Null),
            );
            e.insert(
                "floor".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "floor"))
                    .unwrap_or_else(|| json!(4.0)),
            );
            e.insert("top_z".into(), {
                let argv = vec![g(&e, "height_u")];
                let kwargs = json!({});
                call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
            });
            e.insert(
                "floor_z".into(),
                b("+", attr(cx, "_kit", "bin_floor_z")?, g(&e, "floor")),
            );
            if truth(&json!(compare("!=", g(&e, "depth"), Value::Null))) {
                e.insert(
                    "floor_z".into(),
                    builtin(
                        "max",
                        vec![g(&e, "floor_z"), b("-", g(&e, "top_z"), g(&e, "depth"))],
                    ),
                );
            } else {
            }
            e.insert(
                "reach_x".into(),
                b(
                    "-",
                    {
                        let argv = vec![g(&e, "x_u")];
                        let kwargs = json!({});
                        call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                    },
                    g(&e, "wall"),
                ),
            );
            e.insert(
                "reach_y".into(),
                b(
                    "-",
                    {
                        let argv = vec![g(&e, "y_u")];
                        let kwargs = json!({});
                        call(cx, "_kit", "plateau_half", argv, kwargs, None)?
                    },
                    g(&e, "wall"),
                ),
            );
            e.insert("laid".into(), json!([]));
            for item in seq(g(&e, "rows")) {
                e.insert("row".into(), item);
                e.insert("bores".into(), {
                    let mut e = e.clone();
                    let mut temp10 = Vec::new();
                    for item in seq(g(&e, "row")) {
                        {
                            let temp11 = item;
                            e.insert("env".into(), ix(temp11.clone(), json!(0)));
                            e.insert("count".into(), ix(temp11.clone(), json!(1)));
                        }
                        for item in seq(builtin("range", vec![g(&e, "count")])) {
                            e.insert("_".into(), item);
                            temp10.push(t(vec![
                                g(&e, "env"),
                                b(
                                    "+",
                                    storage::method(g(&e, "env"), "size", vec![json!("x")])?,
                                    g(&e, "slip"),
                                ),
                            ]));
                        }
                    }
                    json!(temp10)
                });
                e.insert(
                    "run".into(),
                    b(
                        "+",
                        builtin(
                            "sum",
                            vec![{
                                let mut e = e.clone();
                                let mut temp12 = Vec::new();
                                for item in seq(g(&e, "bores")) {
                                    {
                                        let temp13 = item;
                                        e.insert("_".into(), ix(temp13.clone(), json!(0)));
                                        e.insert("d".into(), ix(temp13.clone(), json!(1)));
                                    }
                                    temp12.push(g(&e, "d"));
                                }
                                json!(temp12)
                            }],
                        ),
                        b(
                            "*",
                            g(&e, "wall"),
                            b("-", builtin("len", vec![g(&e, "bores")]), json!(1)),
                        ),
                    ),
                );
                if truth(&json!(compare(
                    ">",
                    g(&e, "run"),
                    b("*", json!(2.0), g(&e, "reach_x"))
                ))) {
                    bail!(
                        "{}",
                        string(&json!(
                            [
                                "a row of ".to_owned(),
                                format_value(builtin("len", vec![g(&e, "bores")]), "")?,
                                " bores runs ".to_owned(),
                                format_value(g(&e, "run"), ".1f")?,
                                " mm over a ".to_owned(),
                                format_value(b("*", json!(2.0), g(&e, "reach_x")), ".1f")?,
                                " mm plateau".to_owned()
                            ]
                            .concat()
                        ))
                    );
                } else {
                }
                e.insert("x".into(), b("/", u("-", g(&e, "run")), json!(2.0)));
                e.insert("placed_row".into(), json!([]));
                for item in seq(g(&e, "bores")) {
                    {
                        let temp14 = item;
                        e.insert("env".into(), ix(temp14.clone(), json!(0)));
                        e.insert("diameter".into(), ix(temp14.clone(), json!(1)));
                    }
                    e.insert(
                        "x".into(),
                        b("+", g(&e, "x"), b("/", g(&e, "diameter"), json!(2.0))),
                    );
                    {
                        let item = t(vec![g(&e, "env"), g(&e, "x"), g(&e, "diameter")]);
                        mutate(&mut e, "placed_row", "append", item);
                    }
                    e.insert(
                        "x".into(),
                        b(
                            "+",
                            g(&e, "x"),
                            b("+", b("/", g(&e, "diameter"), json!(2.0)), g(&e, "wall")),
                        ),
                    );
                }
                {
                    let item = t(vec![
                        g(&e, "placed_row"),
                        builtin(
                            "max",
                            vec![{
                                let mut e = e.clone();
                                let mut temp15 = Vec::new();
                                for item in seq(g(&e, "bores")) {
                                    {
                                        let temp16 = item;
                                        e.insert("_".into(), ix(temp16.clone(), json!(0)));
                                        e.insert("d".into(), ix(temp16.clone(), json!(1)));
                                    }
                                    temp15.push(g(&e, "d"));
                                }
                                json!(temp15)
                            }],
                        ),
                    ]);
                    mutate(&mut e, "laid", "append", item);
                }
            }
            e.insert(
                "height".into(),
                b(
                    "+",
                    builtin(
                        "sum",
                        vec![{
                            let mut e = e.clone();
                            let mut temp17 = Vec::new();
                            for item in seq(g(&e, "laid")) {
                                {
                                    let temp18 = item;
                                    e.insert("_".into(), ix(temp18.clone(), json!(0)));
                                    e.insert("depth_y".into(), ix(temp18.clone(), json!(1)));
                                }
                                temp17.push(g(&e, "depth_y"));
                            }
                            json!(temp17)
                        }],
                    ),
                    b(
                        "*",
                        g(&e, "wall"),
                        b("-", builtin("len", vec![g(&e, "laid")]), json!(1)),
                    ),
                ),
            );
            if truth(&json!(compare(
                ">",
                g(&e, "height"),
                b("*", json!(2.0), g(&e, "reach_y"))
            ))) {
                bail!(
                    "{}",
                    string(&json!(
                        [
                            format_value(builtin("len", vec![g(&e, "laid")]), "")?,
                            " rows stand ".to_owned(),
                            format_value(g(&e, "height"), ".1f")?,
                            " mm over a ".to_owned(),
                            format_value(b("*", json!(2.0), g(&e, "reach_y")), ".1f")?,
                            " mm plateau".to_owned()
                        ]
                        .concat()
                    ))
                );
            } else {
            }
            e.insert("placed".into(), json!([]));
            e.insert("y".into(), b("/", g(&e, "height"), json!(2.0)));
            for item in seq(g(&e, "laid")) {
                {
                    let temp19 = item;
                    e.insert("placed_row".into(), ix(temp19.clone(), json!(0)));
                    e.insert("row_depth".into(), ix(temp19.clone(), json!(1)));
                }
                e.insert(
                    "y".into(),
                    b("-", g(&e, "y"), b("/", g(&e, "row_depth"), json!(2.0))),
                );
                for item in seq(g(&e, "placed_row")) {
                    {
                        let temp20 = item;
                        e.insert("env".into(), ix(temp20.clone(), json!(0)));
                        e.insert("x".into(), ix(temp20.clone(), json!(1)));
                        e.insert("diameter".into(), ix(temp20.clone(), json!(2)));
                    }
                    {
                        let item = t(vec![
                            g(&e, "env"),
                            g(&e, "x"),
                            g(&e, "y"),
                            g(&e, "diameter"),
                        ]);
                        mutate(&mut e, "placed", "append", item);
                    }
                }
                e.insert(
                    "y".into(),
                    b(
                        "-",
                        g(&e, "y"),
                        b("+", b("/", g(&e, "row_depth"), json!(2.0)), g(&e, "wall")),
                    ),
                );
            }
            return Ok(t(vec![g(&e, "floor_z"), g(&e, "top_z"), g(&e, "placed")]));
            Ok(Value::Null)
        }
        ("_holder", "index_depth") => {
            e.insert(
                "height_u".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "floor".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "floor"))
                    .unwrap_or_else(|| json!(4.0)),
            );
            e.insert(
                "depth".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "depth"))
                    .unwrap_or_else(|| Value::Null),
            );
            e.insert("top_z".into(), {
                let argv = vec![g(&e, "height_u")];
                let kwargs = json!({});
                call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
            });
            e.insert(
                "floor_z".into(),
                b("+", attr(cx, "_kit", "bin_floor_z")?, g(&e, "floor")),
            );
            if truth(&json!(compare("!=", g(&e, "depth"), Value::Null))) {
                e.insert(
                    "floor_z".into(),
                    builtin(
                        "max",
                        vec![g(&e, "floor_z"), b("-", g(&e, "top_z"), g(&e, "depth"))],
                    ),
                );
            } else {
            }
            return Ok(b("-", g(&e, "top_z"), g(&e, "floor_z")));
            Ok(Value::Null)
        }
        ("_holder", "assert_index_holds") => {
            e.insert(
                "name".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "name"))
                    .unwrap_or_else(|| missing("name")),
            );
            e.insert(
                "env".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "env"))
                    .unwrap_or_else(|| missing("env")),
            );
            e.insert(
                "height_u".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height_u"))
                    .unwrap_or_else(|| missing("height_u")),
            );
            e.insert(
                "floor".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "floor"))
                    .unwrap_or_else(|| json!(4.0)),
            );
            e.insert(
                "depth".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "depth"))
                    .unwrap_or_else(|| Value::Null),
            );
            e.insert("grip".into(), {
                let argv = vec![g(&e, "height_u"), g(&e, "floor"), g(&e, "depth")];
                let kwargs = json!({});
                call(cx, "_holder", "index_depth", argv, kwargs, Some(&e))?
            });
            e.insert(
                "stands".into(),
                b(
                    "-",
                    storage::method(g(&e, "env"), "size", vec![json!("z")])?,
                    g(&e, "grip"),
                ),
            );
            let _ = {
                let message = vec![string(&json!(
                    [
                        "   ".to_owned(),
                        format_value(g(&e, "name"), "")?,
                        ": ".to_owned(),
                        format_value(attr_value(g(&e, "env"), "name"), "")?,
                        " at ".to_owned(),
                        format_value(
                            storage::method(g(&e, "env"), "size", vec![json!("x")])?,
                            ".2f"
                        )?,
                        " mm, held over ".to_owned(),
                        format_value(g(&e, "grip"), ".1f")?,
                        " mm, standing ".to_owned(),
                        format_value(g(&e, "stands"), ".0f")?,
                        " mm proud".to_owned()
                    ]
                    .concat()
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            return Ok(g(&e, "stands"));
            Ok(Value::Null)
        }
        ("catalog", "cylinder_volume") => {
            e.insert(
                "diameter".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "diameter"))
                    .unwrap_or_else(|| missing("diameter")),
            );
            e.insert(
                "height".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "height"))
                    .unwrap_or_else(|| missing("height")),
            );
            return Ok(b(
                "*",
                b(
                    "*",
                    json!(std::f64::consts::PI),
                    b("**", b("/", g(&e, "diameter"), json!(2.0)), json!(2)),
                ),
                g(&e, "height"),
            ));
            Ok(Value::Null)
        }
        ("catalog", "screw_volume") => {
            e.insert(
                "head_diameter".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "head_diameter"))
                    .unwrap_or_else(|| missing("head_diameter")),
            );
            e.insert(
                "head_height".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "head_height"))
                    .unwrap_or_else(|| missing("head_height")),
            );
            e.insert(
                "thread_diameter".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "thread_diameter"))
                    .unwrap_or_else(|| missing("thread_diameter")),
            );
            e.insert(
                "length".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length"))
                    .unwrap_or_else(|| missing("length")),
            );
            return Ok({
                let argv = vec![
                    g(&e, "head_diameter"),
                    b("+", g(&e, "head_height"), g(&e, "length")),
                ];
                let kwargs = json!({});
                call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
            });
            Ok(Value::Null)
        }
        ("catalog", "cap_screw") => {
            e.insert(
                "label".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "label"))
                    .unwrap_or_else(|| missing("label")),
            );
            e.insert(
                "thread".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "thread"))
                    .unwrap_or_else(|| missing("thread")),
            );
            e.insert(
                "length".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length"))
                    .unwrap_or_else(|| missing("length")),
            );
            e.insert(
                "count".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            e.insert(
                "asin".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "asin"))
                    .unwrap_or_else(|| missing("asin")),
            );
            {
                let temp1 = ix(g(&e, "_din912"), g(&e, "thread"));
                e.insert("head_d".into(), ix(temp1.clone(), json!(0)));
                e.insert("head_h".into(), ix(temp1.clone(), json!(1)));
            }
            return Ok({
                let argv = vec![
                    g(&e, "label"),
                    g(&e, "count"),
                    {
                        let argv = vec![
                            g(&e, "head_d"),
                            g(&e, "head_h"),
                            g(&e, "thread"),
                            g(&e, "length"),
                        ];
                        let kwargs = json!({});
                        call(cx, "catalog", "screw_volume", argv, kwargs, Some(&e))?
                    },
                    json!(
                        [
                            format_value(g(&e, "DIN912"), "")?,
                            ", M".to_owned(),
                            format_value(g(&e, "thread"), ".0f")?,
                            " x ".to_owned(),
                            format_value(g(&e, "length"), ".0f")?,
                            "; count from ".to_owned(),
                            format_value(g(&e, "asin"), "")?
                        ]
                        .concat()
                    ),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "ferrule") => {
            e.insert(
                "section".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "section"))
                    .unwrap_or_else(|| missing("section")),
            );
            e.insert(
                "colour".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "colour"))
                    .unwrap_or_else(|| missing("colour")),
            );
            e.insert(
                "count".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            {
                let temp4 = ix(g(&e, "_din46228"), g(&e, "section"));
                e.insert("collar_d".into(), ix(temp4.clone(), json!(0)));
                e.insert("length".into(), ix(temp4.clone(), json!(1)));
            }
            return Ok({
                let argv = vec![
                    json!(
                        [
                            format_value(g(&e, "section"), "g")?,
                            " mm2 ferrule, ".to_owned(),
                            format_value(g(&e, "colour"), "")?
                        ]
                        .concat()
                    ),
                    g(&e, "count"),
                    {
                        let argv = vec![g(&e, "collar_d"), g(&e, "length")];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!(
                        [
                            "DIN 46228-4 ".to_owned(),
                            format_value(g(&e, "section"), "g")?,
                            " mm2; count from the Preciva kit B0DS622GKN".to_owned()
                        ]
                        .concat()
                    ),
                ];
                let kwargs = json!({});
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "shrink") => {
            e.insert(
                "band".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "band"))
                    .unwrap_or_else(|| missing("band")),
            );
            e.insert(
                "widest".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "widest"))
                    .unwrap_or_else(|| missing("widest")),
            );
            e.insert(
                "pieces".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "pieces"))
                    .unwrap_or_else(|| missing("pieces")),
            );
            e.insert(
                "piece_length".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "piece_length"))
                    .unwrap_or_else(|| missing("piece_length")),
            );
            e.insert(
                "wall".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "wall"))
                    .unwrap_or_else(|| json!(0.5)),
            );
            return Ok({
                let argv = vec![
                    json!(
                        [
                            "2:1 heat shrink, ".to_owned(),
                            format_value(g(&e, "band"), "")?
                        ]
                        .concat()
                    ),
                    g(&e, "pieces"),
                    b(
                        "*",
                        b(
                            "*",
                            b(
                                "/",
                                b("*", json!(std::f64::consts::PI), g(&e, "widest")),
                                json!(2.0),
                            ),
                            b("*", json!(2.0), g(&e, "wall")),
                        ),
                        g(&e, "piece_length"),
                    ),
                    json!(
                        [
                            "Ginsco B01MFA3OFA states eleven fractional-inch diameters; "
                                .to_owned(),
                            format_value(g(&e, "band"), "")?,
                            " is its band".to_owned()
                        ]
                        .concat()
                    ),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_TANGLES"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "spade") => {
            e.insert(
                "label".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "label"))
                    .unwrap_or_else(|| missing("label")),
            );
            e.insert(
                "tab".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "tab"))
                    .unwrap_or_else(|| missing("tab")),
            );
            e.insert(
                "count".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            e.insert(
                "asin".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "asin"))
                    .unwrap_or_else(|| missing("asin")),
            );
            e.insert(
                "sleeve_diameter".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "sleeve_diameter"))
                    .unwrap_or_else(|| json!(6.5)),
            );
            e.insert(
                "length".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length"))
                    .unwrap_or_else(|| json!(22.0)),
            );
            return Ok({
                let argv = vec![
                    g(&e, "label"),
                    g(&e, "count"),
                    {
                        let argv = vec![g(&e, "sleeve_diameter"), g(&e, "length")];
                        let kwargs = json!({});
                        call(cx, "catalog", "cylinder_volume", argv, kwargs, Some(&e))?
                    },
                    json!(
                        [
                            format_value(g(&e, "tab"), "")?,
                            " tab is a standard; count from ".to_owned(),
                            format_value(g(&e, "asin"), "")?,
                            "; the insulated sleeve is generous".to_owned()
                        ]
                        .concat()
                    ),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "zip_ties") => {
            e.insert(
                "length_in".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length_in"))
                    .unwrap_or_else(|| missing("length_in")),
            );
            e.insert(
                "strap".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "strap"))
                    .unwrap_or_else(|| missing("strap")),
            );
            e.insert(
                "thickness".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "thickness"))
                    .unwrap_or_else(|| missing("thickness")),
            );
            e.insert(
                "count".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            e.insert(
                "asin".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "asin"))
                    .unwrap_or_else(|| missing("asin")),
            );
            return Ok({
                let argv = vec![
                    json!(
                        [
                            format_value(g(&e, "length_in"), "g")?,
                            "\" zip tie, ".to_owned(),
                            format_value(g(&e, "strap"), "")?,
                            " mm strap".to_owned()
                        ]
                        .concat()
                    ),
                    g(&e, "count"),
                    b(
                        "*",
                        b(
                            "*",
                            b("*", g(&e, "length_in"), g(&e, "inch")),
                            g(&e, "strap"),
                        ),
                        g(&e, "thickness"),
                    ),
                    json!(
                        [
                            format_value(g(&e, "length_in"), "g")?,
                            " in nominal length and ".to_owned(),
                            format_value(g(&e, "strap"), "")?,
                            " mm strap from ".to_owned(),
                            format_value(g(&e, "asin"), "")?
                        ]
                        .concat()
                    ),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_TANGLES"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "xh_housing") => {
            e.insert(
                "poles".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "poles"))
                    .unwrap_or_else(|| missing("poles")),
            );
            e.insert(
                "count".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            return Ok({
                let argv = vec![
                    json!(
                        [
                            "JST XH ".to_owned(),
                            format_value(g(&e, "poles"), "")?,
                            "P housing".to_owned()
                        ]
                        .concat()
                    ),
                    g(&e, "count"),
                    b(
                        "*",
                        b(
                            "*",
                            b("+", b("*", g(&e, "poles"), g(&e, "XH_PITCH")), json!(1.9)),
                            json!(5.8),
                        ),
                        json!(8.0),
                    ),
                    json!(
                        [
                            "JST XH series drawing, ".to_owned(),
                            format_value(g(&e, "poles"), "")?,
                            "P at ".to_owned(),
                            format_value(g(&e, "XH_PITCH"), "")?,
                            " mm pitch; count from the CQRobot kits".to_owned()
                        ]
                        .concat()
                    ),
                ];
                let kwargs = object(vec![("nest".into(), json!(0.9))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "jg") => {
            e.insert(
                "part".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "part"))
                    .unwrap_or_else(|| missing("part")),
            );
            e.insert(
                "label".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "label"))
                    .unwrap_or_else(|| missing("label")),
            );
            e.insert(
                "length".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length"))
                    .unwrap_or_else(|| missing("length")),
            );
            e.insert(
                "across".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "across"))
                    .unwrap_or_else(|| missing("across")),
            );
            e.insert(
                "count".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            return Ok({
                let argv = vec![
                    json!(
                        [
                            "John Guest ".to_owned(),
                            format_value(g(&e, "part"), "")?,
                            " — ".to_owned(),
                            format_value(g(&e, "label"), "")?
                        ]
                        .concat()
                    ),
                    g(&e, "count"),
                    b(
                        "*",
                        b("*", g(&e, "length"), g(&e, "across")),
                        g(&e, "across"),
                    ),
                    json!(
                        [
                            "John Guest ".to_owned(),
                            format_value(g(&e, "part"), "")?,
                            " catalogue drawing, ".to_owned(),
                            format_value(g(&e, "length"), "")?,
                            " x ".to_owned(),
                            format_value(g(&e, "across"), "")?,
                            " mm".to_owned()
                        ]
                        .concat()
                    ),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "NEST_INTERLOCKS"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("catalog", "listed") => {
            e.insert(
                "label".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "label"))
                    .unwrap_or_else(|| missing("label")),
            );
            e.insert(
                "length".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "length"))
                    .unwrap_or_else(|| missing("length")),
            );
            e.insert(
                "across".into(),
                args.get(2)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "across"))
                    .unwrap_or_else(|| missing("across")),
            );
            e.insert(
                "count".into(),
                args.get(3)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "count"))
                    .unwrap_or_else(|| missing("count")),
            );
            e.insert(
                "asin".into(),
                args.get(4)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "asin"))
                    .unwrap_or_else(|| missing("asin")),
            );
            e.insert(
                "nest".into(),
                args.get(5)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "nest"))
                    .unwrap_or_else(|| g(&e, "NEST_INTERLOCKS")),
            );
            return Ok({
                let argv = vec![
                    g(&e, "label"),
                    g(&e, "count"),
                    b(
                        "*",
                        b("*", g(&e, "length"), g(&e, "across")),
                        g(&e, "across"),
                    ),
                    json!(
                        [
                            format_value(g(&e, "asin"), "")?,
                            " listing figures, ".to_owned(),
                            format_value(g(&e, "length"), "")?,
                            " x ".to_owned(),
                            format_value(g(&e, "across"), "")?,
                            " mm".to_owned()
                        ]
                        .concat()
                    ),
                ];
                let kwargs = object(vec![("nest".into(), g(&e, "nest"))]);
                call(cx, "_bound", "heap", argv, kwargs, None)?
            });
            Ok(Value::Null)
        }
        ("holders", "sizes") => {
            for item in seq(g(&e, "HOLDERS")) {
                e.insert("holder".into(), item);
                if truth(&json!(compare(
                    "!=",
                    attr_value(g(&e, "holder"), "shape"),
                    json!("tub")
                ))) {
                    continue;
                } else {
                }
                e.insert("opts".into(), attr_value(g(&e, "holder"), "opts"));
                e.insert("height_u".into(), {
                    let value = attr_value(g(&e, "holder"), "height_u");
                    if truth(&value) {
                        value
                    } else {
                        {
                            let argv = vec![
                                attr_value(g(&e, "holder"), "x_u"),
                                attr_value(g(&e, "holder"), "y_u"),
                                attr_value(g(&e, "holder"), "takes"),
                                method(g(&e, "opts"), "get", vec![json!("length_div"), json!(0)]),
                                method(g(&e, "opts"), "get", vec![json!("width_div"), json!(0)]),
                            ];
                            let kwargs = json!({});
                            call(cx, "_holder", "tub_height_for", argv, kwargs, None)?
                        }
                    }
                });
                e.insert("clear".into(), {
                    let argv = vec![
                        attr_value(g(&e, "holder"), "x_u"),
                        attr_value(g(&e, "holder"), "y_u"),
                        g(&e, "height_u"),
                        method(g(&e, "opts"), "get", vec![json!("length_div"), json!(0)]),
                        method(g(&e, "opts"), "get", vec![json!("width_div"), json!(0)]),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "tub_holds", argv, kwargs, None)?
                });
                let _ = {
                    let message = vec![string(&json!(
                        [
                            format_value(attr_value(g(&e, "holder"), "name"), "20s")?,
                            " ".to_owned(),
                            format_value(attr_value(g(&e, "holder"), "x_u"), "")?,
                            "x".to_owned(),
                            format_value(attr_value(g(&e, "holder"), "y_u"), "")?,
                            "x".to_owned(),
                            format_value(g(&e, "height_u"), "<3d")?,
                            " ".to_owned(),
                            format_value(b("*", g(&e, "height_u"), json!(7)), "5.0f")?,
                            " mm tall   cell ".to_owned(),
                            format_value(ix(g(&e, "clear"), json!(0)), "5.1f")?,
                            " x ".to_owned(),
                            format_value(ix(g(&e, "clear"), json!(1)), "5.1f")?,
                            " x ".to_owned(),
                            format_value(ix(g(&e, "clear"), json!(2)), "5.1f")?,
                            "   ".to_owned(),
                            format_value(
                                builtin("len", vec![attr_value(g(&e, "holder"), "takes")]),
                                ""
                            )?,
                            " of ".to_owned(),
                            format_value(
                                b(
                                    "*",
                                    b(
                                        "+",
                                        method(
                                            g(&e, "opts"),
                                            "get",
                                            vec![json!("length_div"), json!(0)]
                                        ),
                                        json!(1)
                                    ),
                                    b(
                                        "+",
                                        method(
                                            g(&e, "opts"),
                                            "get",
                                            vec![json!("width_div"), json!(0)]
                                        ),
                                        json!(1)
                                    )
                                ),
                                ""
                            )?
                        ]
                        .concat()
                    ))]
                    .join(" ");
                    cx.messages.push(message);
                    Value::Null
                };
            }
            Ok(Value::Null)
        }
        ("holders", "figures") => {
            e.insert(
                "marks".into(),
                object(vec![
                    (
                        json!("HOLDER_COUNT"),
                        builtin("str", vec![builtin("len", vec![g(&e, "HOLDERS")])]),
                    ),
                    (
                        json!("GRID"),
                        json!(
                            [
                                format_value(attr(cx, "_kit", "grid_unit")?, ".0f")?,
                                " mm x ".to_owned(),
                                format_value(attr(cx, "_kit", "grid_unit")?, ".0f")?,
                                " mm x ".to_owned(),
                                format_value(attr(cx, "_kit", "height_unit")?, ".0f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                    (
                        json!("H2C_ENVELOPE"),
                        json!(
                            [
                                format_value(attr(cx, "_kit", "h2c_build_x")?, ".0f")?,
                                " x ".to_owned(),
                                format_value(attr(cx, "_kit", "h2c_build_y")?, ".0f")?,
                                " x ".to_owned(),
                                format_value(attr(cx, "_kit", "h2c_build_z")?, ".0f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                    (
                        json!("TROUGH"),
                        method(json!("{:.0f} mm x {:.0f} mm"), "format", {
                            let mut temp2 = vec![];
                            temp2.extend(seq(slice(
                                {
                                    let argv = vec![json!(3), json!(3), json!(6)];
                                    let kwargs = json!({});
                                    call(cx, "_holder", "cradle_trough", argv, kwargs, None)?
                                },
                                Value::Null,
                                json!(2),
                            )));
                            temp2
                        }),
                    ),
                    (
                        json!("ROLL_TROUGH"),
                        method(json!("{:.0f} mm x {:.0f} mm"), "format", {
                            let mut temp3 = vec![];
                            temp3.extend(seq(slice(
                                {
                                    let argv = vec![json!(2), json!(2), json!(5)];
                                    let kwargs = json!({});
                                    call(cx, "_holder", "cradle_trough", argv, kwargs, None)?
                                },
                                Value::Null,
                                json!(2),
                            )));
                            temp3
                        }),
                    ),
                    (
                        json!("SLOT_ROOT"),
                        json!(
                            [
                                format_value(attr(cx, "_holder", "slot_root")?, ".0f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                    (
                        json!("SLOT_TAPER"),
                        json!(
                            [
                                format_value(attr(cx, "_holder", "slot_taper")?, ".0f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                    (json!("SLOT_CLEAR"), json!("2 mm")),
                    (
                        json!("BORE_SLIP"),
                        json!(
                            [
                                format_value(attr(cx, "_holder", "slip")?, ".1f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                    (
                        json!("WALL"),
                        json!(
                            [
                                format_value(attr(cx, "_holder", "wall")?, ".0f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                    (
                        json!("LABEL_TAPE"),
                        json!(
                            [
                                format_value(attr(cx, "_kit", "label_tape_width")?, ".0f")?,
                                " mm".to_owned()
                            ]
                            .concat()
                        ),
                    ),
                ]),
            );
            for item in seq(g(&e, "HOLDERS")) {
                e.insert("holder".into(), item);
                e.insert(
                    "key".into(),
                    method(
                        method(attr_value(g(&e, "holder"), "name"), "upper", vec![]),
                        "replace",
                        vec![json!("-"), json!("_")],
                    ),
                );
                {
                    let key = json!([format_value(g(&e, "key"), "")?, "_SIZE".to_owned()].concat());
                    let temp4 = (if truth(&json!(compare(
                        "in",
                        attr_value(g(&e, "holder"), "shape"),
                        t(vec![json!("dock"), json!("spacer")])
                    ))) {
                        json!(
                            [
                                format_value(attr_value(g(&e, "holder"), "x_u"), "")?,
                                " x ".to_owned(),
                                format_value(attr_value(g(&e, "holder"), "y_u"), "")?
                            ]
                            .concat()
                        )
                    } else {
                        json!(
                            [
                                format_value(attr_value(g(&e, "holder"), "x_u"), "")?,
                                " x ".to_owned(),
                                format_value(attr_value(g(&e, "holder"), "y_u"), "")?,
                                " x ".to_owned(),
                                format_value(attr_value(g(&e, "holder"), "height_u"), "")?
                            ]
                            .concat()
                        )
                    });
                    setitem(&mut e, "marks", key, temp4);
                }
            }
            return Ok(g(&e, "marks"));
            Ok(Value::Null)
        }
        ("holders", "parcels") => {
            let _ = {
                let message = vec![string(&json!(
                    "Slots cut to a parcel. One caliper reading each closes the slack:\n"
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            let _ = {
                let message = vec![string(&json!(
                    [
                        format_value(json!("holder"), "<13")?,
                        format_value(json!("tool"), "<46")?,
                        format_value(json!("mouth"), ">6")?,
                        format_value(json!("known"), ">9")?,
                        "   source".to_owned()
                    ]
                    .concat()
                ))]
                .join(" ");
                cx.messages.push(message);
                Value::Null
            };
            for item in seq(g(&e, "COMBS")) {
                e.insert("holder".into(), item);
                for item in seq(method(
                    json!({"$class":"dict"}),
                    "fromkeys",
                    vec![attr_value(g(&e, "holder"), "takes")],
                )) {
                    e.insert("env".into(), item);
                    e.insert(
                        "thin".into(),
                        ix(json!("xyz"), {
                            let values = seq(builtin("range", vec![json!(3)]));
                            let mut temp5 = Vec::new();
                            for value in values {
                                let mut e = e.clone();
                                e.insert("i".into(), value.clone());
                                let key = ix(
                                    t(vec![
                                        attr_value(g(&e, "env"), "x"),
                                        attr_value(g(&e, "env"), "y"),
                                        attr_value(g(&e, "env"), "z"),
                                    ]),
                                    g(&e, "i"),
                                );
                                temp5.push((key, value));
                            }
                            let mut best: Option<(Value, Value)> = None;
                            for pair in temp5 {
                                if best
                                    .as_ref()
                                    .is_none_or(|b| cmp(&pair.0, &b.0) == Ordering::Less)
                                {
                                    best = Some(pair)
                                }
                            }
                            best.expect("empty keyed extremum").1
                        }),
                    );
                    if truth(&json!(compare(
                        "==",
                        storage::method(g(&e, "env"), "reading", vec![g(&e, "thin")])?,
                        g(&e, "EXACT")
                    ))) {
                        continue;
                    } else {
                    }
                    let _ = {
                        let message = vec![string(&json!(
                            [
                                format_value(attr_value(g(&e, "holder"), "name"), "<13")?,
                                format_value(
                                    slice(attr_value(g(&e, "env"), "name"), Value::Null, json!(44)),
                                    "<46"
                                )?,
                                format_value(
                                    {
                                        let argv = vec![g(&e, "env")];
                                        let kwargs = json!({});
                                        call(cx, "_holder", "slot_mouth_for", argv, kwargs, None)?
                                    },
                                    "5.1f"
                                )?,
                                " ".to_owned(),
                                format_value(attr_value(g(&e, "env"), "thinnest"), "8.1f")?,
                                "-   ".to_owned(),
                                format_value(attr_value(g(&e, "env"), "source"), "")?
                            ]
                            .concat()
                        ))]
                        .join(" ");
                        cx.messages.push(message);
                        Value::Null
                    };
                }
            }
            Ok(Value::Null)
        }
        ("holders", "numbers") => {
            e.insert("source".into(), g(&e, "HERE"));
            e.insert("root".into(), attr(cx, "_kit", "_repo_root")?);
            e.insert("manifest".into(), attr(cx, "_kit", "_STOCK")?);
            let _ = {
                let path = attr(cx, "_kit", "_STOCK_PATH")?;
                register_path(cx, path);
                Value::Null
            };
            e.insert("assets".into(), object(vec![]));
            for item in seq(method(
                ix(g(&e, "manifest"), json!("models")),
                "items",
                vec![],
            )) {
                {
                    let temp6 = item;
                    e.insert("key".into(), ix(temp6.clone(), json!(0)));
                    e.insert("model".into(), ix(temp6.clone(), json!(1)));
                }
                e.insert(
                    "path".into(),
                    b(
                        "/",
                        b("/", g(&e, "source"), json!("gridfinity-stock")),
                        ix(g(&e, "model"), json!("path")),
                    ),
                );
                let _ = {
                    let path = g(&e, "path");
                    register_path(cx, path);
                    Value::Null
                };
                {
                    let key = g(&e, "key");
                    let temp7 = method(
                        method(g(&e, "path"), "relative_to", vec![g(&e, "root")]),
                        "as_posix",
                        vec![],
                    );
                    setitem(&mut e, "assets", key, temp7);
                }
            }
            e.insert("tub_defaults".into(), g(&e, "tub_defaults"));
            e.insert("rows".into(), json!([]));
            {
                let mut updated = vec![];
                for item in seq(g(&e, "HOLDERS")) {
                    e.insert("holder".into(), item);
                    e.insert(
                        "opts".into(),
                        builtin("dict", vec![attr_value(g(&e, "holder"), "opts")]),
                    );
                    e.insert(
                        "row".into(),
                        object(vec![
                            (json!("name"), attr_value(g(&e, "holder"), "name")),
                            (json!("kind"), attr_value(g(&e, "holder"), "shape")),
                            (json!("cuts"), json!([])),
                            (json!("seat"), Value::Null),
                            (json!("height_delta"), json!(0.0)),
                        ]),
                    );
                    {
                        let temp8 = t(vec![
                            attr_value(g(&e, "holder"), "x_u"),
                            attr_value(g(&e, "holder"), "y_u"),
                        ]);
                        e.insert("x".into(), ix(temp8.clone(), json!(0)));
                        e.insert("y".into(), ix(temp8.clone(), json!(1)));
                    }
                    if truth(&json!(compare(
                        "==",
                        attr_value(g(&e, "holder"), "shape"),
                        json!("tub")
                    ))) {
                        {
                            let temp9 = t(vec![
                                method(g(&e, "opts"), "get", vec![json!("length_div"), json!(0)]),
                                method(g(&e, "opts"), "get", vec![json!("width_div"), json!(0)]),
                            ]);
                            e.insert("ld".into(), ix(temp9.clone(), json!(0)));
                            e.insert("wd".into(), ix(temp9.clone(), json!(1)));
                        }
                        if truth(&json!(compare(
                            "==",
                            attr_value(g(&e, "holder"), "height_u"),
                            Value::Null
                        ))) {
                            {
                                let temp10 = {
                                    let argv = vec![
                                        g(&e, "x"),
                                        g(&e, "y"),
                                        attr_value(g(&e, "holder"), "takes"),
                                        g(&e, "ld"),
                                        g(&e, "wd"),
                                    ];
                                    let kwargs = json!({});
                                    call(cx, "_holder", "tub_height_for", argv, kwargs, None)?
                                };
                                assign_attribute(&mut e, "holder", "height_u", temp10);
                            }
                        } else {
                        }
                        e.insert(
                            "cells".into(),
                            b(
                                "*",
                                b("+", g(&e, "ld"), json!(1)),
                                b("+", g(&e, "wd"), json!(1)),
                            ),
                        );
                        if truth(&json!(compare(
                            ">",
                            builtin("len", vec![attr_value(g(&e, "holder"), "takes")]),
                            g(&e, "cells")
                        ))) {
                            bail!(
                                "{}",
                                string(&json!(
                                    [
                                        format_value(attr_value(g(&e, "holder"), "name"), "")?,
                                        ": ".to_owned(),
                                        format_value(
                                            builtin(
                                                "len",
                                                vec![attr_value(g(&e, "holder"), "takes")]
                                            ),
                                            ""
                                        )?,
                                        " things into ".to_owned(),
                                        format_value(g(&e, "cells"), "")?,
                                        " compartments".to_owned()
                                    ]
                                    .concat()
                                ))
                            );
                        } else {
                        }
                        for item in seq(attr_value(g(&e, "holder"), "takes")) {
                            e.insert("env".into(), item);
                            let _ = (if truth(&builtin(
                                "isinstance",
                                vec![g(&e, "env"), json!({"$class":"Heap"})],
                            )) {
                                {
                                    let argv = vec![
                                        attr_value(g(&e, "holder"), "name"),
                                        g(&e, "env"),
                                        g(&e, "x"),
                                        g(&e, "y"),
                                        attr_value(g(&e, "holder"), "height_u"),
                                        g(&e, "ld"),
                                        g(&e, "wd"),
                                    ];
                                    let kwargs = json!({});
                                    call(cx, "_holder", "assert_heap_fits", argv, kwargs, None)?
                                }
                            } else {
                                {
                                    let argv = vec![
                                        attr_value(g(&e, "holder"), "name"),
                                        g(&e, "env"),
                                        g(&e, "x"),
                                        g(&e, "y"),
                                        attr_value(g(&e, "holder"), "height_u"),
                                        g(&e, "ld"),
                                        g(&e, "wd"),
                                    ];
                                    let kwargs = json!({});
                                    call(cx, "_holder", "assert_tub_takes", argv, kwargs, None)?
                                }
                            });
                        }
                        {
                            let key = json!("stock");
                            let temp11 = {
                                let argv = vec![
                                    merge(vec![
                                        object(vec![(json!("kind"), json!("GridfinityBox"))]),
                                        object(vec![(json!("length_u"), g(&e, "x"))]),
                                        object(vec![(json!("width_u"), g(&e, "y"))]),
                                        object(vec![(
                                            json!("height_u"),
                                            ix(g(&e, "manifest"), json!("template_height_u")),
                                        )]),
                                        object(vec![(json!("length_div"), g(&e, "ld"))]),
                                        object(vec![(json!("width_div"), g(&e, "wd"))]),
                                        object(vec![(
                                            json!("labels"),
                                            attr_value(
                                                ix(g(&e, "tub_defaults"), json!("labels")),
                                                "default",
                                            ),
                                        )]),
                                        object(vec![(
                                            json!("scoops"),
                                            attr_value(
                                                ix(g(&e, "tub_defaults"), json!("scoops")),
                                                "default",
                                            ),
                                        )]),
                                        g(&e, "opts"),
                                    ]),
                                    g(&e, "manifest"),
                                ];
                                let kwargs = json!({});
                                call(cx, "holders", "_stock_key", argv, kwargs, Some(&e))?
                            };
                            setitem(&mut e, "row", key, temp11);
                        }
                    } else {
                        if truth(&json!(compare(
                            "==",
                            attr_value(g(&e, "holder"), "shape"),
                            json!("dock")
                        ))) {
                            {
                                let key = json!("stock");
                                let temp12 = {
                                    let argv = vec![
                                        object(vec![
                                            (json!("kind"), json!("GridfinityBaseplate")),
                                            (json!("length_u"), g(&e, "x")),
                                            (json!("width_u"), g(&e, "y")),
                                            (
                                                json!("ext_depth"),
                                                attr(cx, "_kit", "dock_extra_depth")?,
                                            ),
                                            (json!("straight_bottom"), json!(true)),
                                        ]),
                                        g(&e, "manifest"),
                                    ];
                                    let kwargs = json!({});
                                    call(cx, "holders", "_stock_key", argv, kwargs, Some(&e))?
                                };
                                setitem(&mut e, "row", key, temp12);
                            }
                        } else {
                            if truth(&json!(compare(
                                "==",
                                attr_value(g(&e, "holder"), "shape"),
                                json!("spacer")
                            ))) {
                                {
                                    let key = json!("prism");
                                    let temp13 = object(vec![
                                        (json!("plane"), json!("YZ")),
                                        (json!("length"), ix(g(&e, "opts"), json!("width"))),
                                        (json!("profile"), {
                                            let argv = vec![
                                                ix(g(&e, "opts"), json!("width")),
                                                g(&e, "x"),
                                                g(&e, "y"),
                                                attr_value(g(&e, "holder"), "height_u"),
                                            ];
                                            let kwargs = json!({});
                                            call(
                                                cx,
                                                "_holder",
                                                "spacer_profile",
                                                argv,
                                                kwargs,
                                                None,
                                            )?
                                        }),
                                    ]);
                                    setitem(&mut e, "row", key, temp13);
                                }
                            } else {
                                {
                                    let key = json!("stock");
                                    let temp14 = {
                                        let argv = vec![
                                            object(vec![
                                                (json!("kind"), json!("GridfinityBox")),
                                                (json!("length_u"), g(&e, "x")),
                                                (json!("width_u"), g(&e, "y")),
                                                (
                                                    json!("height_u"),
                                                    ix(
                                                        g(&e, "manifest"),
                                                        json!("template_height_u"),
                                                    ),
                                                ),
                                                (json!("solid"), json!(true)),
                                            ]),
                                            g(&e, "manifest"),
                                        ];
                                        let kwargs = json!({});
                                        call(cx, "holders", "_stock_key", argv, kwargs, Some(&e))?
                                    };
                                    setitem(&mut e, "row", key, temp14);
                                }
                                if truth(&json!(compare(
                                    "==",
                                    attr_value(g(&e, "holder"), "shape"),
                                    json!("cradle")
                                ))) {
                                    {
                                        let temp15 = {
                                            let argv = vec![
                                                g(&e, "x"),
                                                g(&e, "y"),
                                                attr_value(g(&e, "holder"), "height_u"),
                                            ];
                                            let kwargs = json!({});
                                            call(
                                                cx,
                                                "_holder",
                                                "cradle_profile",
                                                argv,
                                                kwargs,
                                                None,
                                            )?
                                        };
                                        e.insert("profile".into(), ix(temp15.clone(), json!(0)));
                                        e.insert("length".into(), ix(temp15.clone(), json!(1)));
                                    }
                                    {
                                        let key = json!("cuts");
                                        let temp16 = json!([(object(vec![
                                            (json!("kind"), json!("prism")),
                                            (json!("plane"), json!("YZ")),
                                            (json!("length"), g(&e, "length")),
                                            (json!("profile"), g(&e, "profile"))
                                        ]))]);
                                        setitem(&mut e, "row", key, temp16);
                                    }
                                    for item in seq(attr_value(g(&e, "holder"), "takes")) {
                                        e.insert("env".into(), item);
                                        let _ = {
                                            let argv = vec![
                                                attr_value(g(&e, "holder"), "name"),
                                                g(&e, "env"),
                                                g(&e, "x"),
                                                g(&e, "y"),
                                                attr_value(g(&e, "holder"), "height_u"),
                                            ];
                                            let kwargs = json!({});
                                            call(
                                                cx,
                                                "_holder",
                                                "assert_cradle_takes",
                                                argv,
                                                kwargs,
                                                None,
                                            )?
                                        };
                                    }
                                } else {
                                    if truth(&json!(compare(
                                        "==",
                                        attr_value(g(&e, "holder"), "shape"),
                                        json!("comb")
                                    ))) {
                                        e.insert("mouths".into(), {
                                            let mut e = e.clone();
                                            let mut temp17 = Vec::new();
                                            for item in seq(attr_value(g(&e, "holder"), "takes")) {
                                                e.insert("env".into(), item);
                                                temp17.push({
                                                    let argv = vec![g(&e, "env")];
                                                    let kwargs = json!({});
                                                    call(
                                                        cx,
                                                        "_holder",
                                                        "slot_mouth_for",
                                                        argv,
                                                        kwargs,
                                                        None,
                                                    )?
                                                });
                                            }
                                            json!(temp17)
                                        });
                                        {
                                            let temp18 = {
                                                let argv = vec![
                                                    g(&e, "x"),
                                                    g(&e, "y"),
                                                    attr_value(g(&e, "holder"), "height_u"),
                                                    g(&e, "mouths"),
                                                ];
                                                let kwargs = merge(vec![g(&e, "opts")]);
                                                call(
                                                    cx,
                                                    "_holder",
                                                    "comb_layout",
                                                    argv,
                                                    kwargs,
                                                    None,
                                                )?
                                            };
                                            e.insert(
                                                "profiles".into(),
                                                ix(temp18.clone(), json!(0)),
                                            );
                                            e.insert("length".into(), ix(temp18.clone(), json!(1)));
                                        }
                                        {
                                            let key = json!("cuts");
                                            let temp20 = {
                                                let mut e = e.clone();
                                                let mut temp19 = Vec::new();
                                                for item in seq(g(&e, "profiles")) {
                                                    e.insert("p".into(), item);
                                                    temp19.push(object(vec![
                                                        (json!("kind"), json!("prism")),
                                                        (json!("plane"), json!("XZ")),
                                                        (json!("length"), g(&e, "length")),
                                                        (json!("profile"), g(&e, "p")),
                                                    ]));
                                                }
                                                json!(temp19)
                                            };
                                            setitem(&mut e, "row", key, temp20);
                                        }
                                        for item in seq(builtin(
                                            "zip",
                                            vec![
                                                attr_value(g(&e, "holder"), "takes"),
                                                g(&e, "mouths"),
                                            ],
                                        )) {
                                            {
                                                let temp21 = item;
                                                e.insert(
                                                    "env".into(),
                                                    ix(temp21.clone(), json!(0)),
                                                );
                                                e.insert(
                                                    "mouth".into(),
                                                    ix(temp21.clone(), json!(1)),
                                                );
                                            }
                                            let _ = {
                                                let argv = vec![
                                                    attr_value(g(&e, "holder"), "name"),
                                                    g(&e, "env"),
                                                    g(&e, "y"),
                                                    attr_value(g(&e, "holder"), "height_u"),
                                                    g(&e, "mouth"),
                                                ];
                                                let kwargs = merge(vec![g(&e, "opts")]);
                                                call(
                                                    cx,
                                                    "_holder",
                                                    "assert_comb_takes",
                                                    argv,
                                                    kwargs,
                                                    None,
                                                )?
                                            };
                                        }
                                    } else {
                                        if truth(&json!(compare(
                                            "==",
                                            attr_value(g(&e, "holder"), "shape"),
                                            json!("index")
                                        ))) {
                                            {
                                                let temp22 = {
                                                    let argv = vec![
                                                        g(&e, "x"),
                                                        g(&e, "y"),
                                                        attr_value(g(&e, "holder"), "height_u"),
                                                        ix(g(&e, "opts"), json!("rows")),
                                                    ];
                                                    let kwargs = json!({});
                                                    call(
                                                        cx,
                                                        "_holder",
                                                        "index_layout",
                                                        argv,
                                                        kwargs,
                                                        None,
                                                    )?
                                                };
                                                e.insert(
                                                    "floor".into(),
                                                    ix(temp22.clone(), json!(0)),
                                                );
                                                e.insert(
                                                    "top".into(),
                                                    ix(temp22.clone(), json!(1)),
                                                );
                                                e.insert(
                                                    "placed".into(),
                                                    ix(temp22.clone(), json!(2)),
                                                );
                                            }
                                            {
                                                let key = json!("cuts");
                                                let temp25 = {
                                                    let mut e = e.clone();
                                                    let mut temp23 = Vec::new();
                                                    for item in seq(g(&e, "placed")) {
                                                        {
                                                            let temp24 = item;
                                                            e.insert(
                                                                "_env".into(),
                                                                ix(temp24.clone(), json!(0)),
                                                            );
                                                            e.insert(
                                                                "bx".into(),
                                                                ix(temp24.clone(), json!(1)),
                                                            );
                                                            e.insert(
                                                                "by".into(),
                                                                ix(temp24.clone(), json!(2)),
                                                            );
                                                            e.insert(
                                                                "d".into(),
                                                                ix(temp24.clone(), json!(3)),
                                                            );
                                                        }
                                                        temp23.push(object(vec![
                                                            (json!("kind"), json!("bore")),
                                                            (
                                                                json!("origin"),
                                                                json!([
                                                                    (g(&e, "bx")),
                                                                    (g(&e, "by")),
                                                                    (g(&e, "floor"))
                                                                ]),
                                                            ),
                                                            (json!("diameter"), g(&e, "d")),
                                                            (
                                                                json!("height"),
                                                                b(
                                                                    "+",
                                                                    b(
                                                                        "-",
                                                                        g(&e, "top"),
                                                                        g(&e, "floor"),
                                                                    ),
                                                                    json!(0.2),
                                                                ),
                                                            ),
                                                        ]));
                                                    }
                                                    json!(temp23)
                                                };
                                                setitem(&mut e, "row", key, temp25);
                                            }
                                            for item in seq(method(
                                                json!({"$class":"dict"}),
                                                "fromkeys",
                                                vec![{
                                                    let mut e = e.clone();
                                                    let mut temp26 = Vec::new();
                                                    for item in seq(g(&e, "placed")) {
                                                        {
                                                            let temp27 = item;
                                                            e.insert(
                                                                "env".into(),
                                                                ix(temp27.clone(), json!(0)),
                                                            );
                                                            e.insert(
                                                                "_".into(),
                                                                json!(seq(slice(
                                                                    temp27.clone(),
                                                                    json!(1),
                                                                    Value::Null
                                                                ))),
                                                            );
                                                        }
                                                        temp26.push(g(&e, "env"));
                                                    }
                                                    json!(temp26)
                                                }],
                                            )) {
                                                e.insert("env".into(), item);
                                                let _ = {
                                                    let argv = vec![
                                                        attr_value(g(&e, "holder"), "name"),
                                                        g(&e, "env"),
                                                        attr_value(g(&e, "holder"), "height_u"),
                                                    ];
                                                    let kwargs = json!({});
                                                    call(
                                                        cx,
                                                        "_holder",
                                                        "assert_index_holds",
                                                        argv,
                                                        kwargs,
                                                        None,
                                                    )?
                                                };
                                            }
                                        } else {
                                            bail!(
                                                "{}",
                                                string(&json!(
                                                    [
                                                        format_value(
                                                            attr_value(g(&e, "holder"), "name"),
                                                            ""
                                                        )?,
                                                        ": ".to_owned(),
                                                        format_value(
                                                            attr_value(g(&e, "holder"), "shape"),
                                                            ""
                                                        )?,
                                                        " is not a holder shape".to_owned()
                                                    ]
                                                    .concat()
                                                ))
                                            );
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if truth(&json!(compare(
                        "not in",
                        attr_value(g(&e, "holder"), "shape"),
                        t(vec![json!("dock"), json!("spacer")])
                    ))) {
                        {
                            let key = json!("height_delta");
                            let temp28 = b(
                                "*",
                                b(
                                    "-",
                                    attr_value(g(&e, "holder"), "height_u"),
                                    ix(g(&e, "manifest"), json!("template_height_u")),
                                ),
                                attr(cx, "_kit", "height_unit")?,
                            );
                            setitem(&mut e, "row", key, temp28);
                        }
                        e.insert(
                            "seat".into(),
                            ix(
                                ix(g(&e, "manifest"), json!("seats")),
                                json!(
                                    [
                                        format_value(g(&e, "x"), "")?,
                                        "x".to_owned(),
                                        format_value(g(&e, "y"), "")?
                                    ]
                                    .concat()
                                ),
                            ),
                        );
                        e.insert(
                            "point".into(),
                            json!(seq(ix(g(&e, "seat"), json!("body_point_mm")))),
                        );
                        {
                            let key = json!(2);
                            let temp29 = b(
                                "+",
                                ix(g(&e, "point"), json!(2)),
                                b(
                                    "-",
                                    attr(cx, "_kit", "dock_seat_z")?,
                                    ix(g(&e, "seat"), json!("translation_z_mm")),
                                ),
                            );
                            setitem(&mut e, "point", key, temp29);
                        }
                        {
                            let key = json!("seat");
                            let temp30 = object(vec![
                                (json!("dock"), ix(g(&e, "seat"), json!("dock_key"))),
                                (json!("z"), attr(cx, "_kit", "dock_seat_z")?),
                                (
                                    json!("plate_point"),
                                    ix(g(&e, "seat"), json!("plate_point_mm")),
                                ),
                                (json!("body_point"), g(&e, "point")),
                            ]);
                            setitem(&mut e, "row", key, temp30);
                        }
                    } else {
                    }
                    {
                        let item = g(&e, "row");
                        mutate(&mut e, "rows", "append", item);
                    }
                    updated.push(g(&e, "holder"));
                }
                e.insert("HOLDERS".into(), json!(updated));
            }
            e.insert(
                "holder".into(),
                builtin(
                    "next",
                    vec![{
                        let mut e = e.clone();
                        let mut temp31 = Vec::new();
                        for item in seq(g(&e, "HOLDERS")) {
                            e.insert("h".into(), item);
                            if truth(&json!(compare(
                                "==",
                                attr_value(g(&e, "h"), "name"),
                                json!("reel-cradle")
                            ))) {
                                temp31.push(g(&e, "h"));
                            }
                        }
                        json!(temp31)
                    }],
                ),
            );
            {
                let temp32 = {
                    let argv = vec![
                        attr_value(g(&e, "holder"), "x_u"),
                        attr_value(g(&e, "holder"), "y_u"),
                        attr_value(g(&e, "holder"), "height_u"),
                    ];
                    let kwargs = json!({});
                    call(cx, "_holder", "cradle_trough", argv, kwargs, None)?
                };
                e.insert("mouth".into(), ix(temp32.clone(), json!(0)));
                e.insert("depth".into(), ix(temp32.clone(), json!(1)));
                e.insert("run".into(), ix(temp32.clone(), json!(2)));
            }
            e.insert("top".into(), {
                let argv = vec![attr_value(g(&e, "holder"), "height_u")];
                let kwargs = json!({});
                call(cx, "_kit", "top_reference_z", argv, kwargs, None)?
            });
            e.insert(
                "diameters".into(),
                t(vec![json!(40.0), json!(72.0), json!(110.0)]),
            );
            e.insert(
                "width".into(),
                b(
                    "/",
                    g(&e, "run"),
                    b("+", builtin("len", vec![g(&e, "diameters")]), json!(1)),
                ),
            );
            e.insert("reels".into(), {
                let mut e = e.clone();
                let mut temp33 = Vec::new();
                for item in seq(builtin("enumerate", vec![g(&e, "diameters")])) {
                    {
                        let temp34 = item;
                        e.insert("i".into(), ix(temp34.clone(), json!(0)));
                        e.insert("d".into(), ix(temp34.clone(), json!(1)));
                    }
                    temp33.push(object(vec![
                        (
                            json!("name"),
                            json!(["reel-".to_owned(), format_value(g(&e, "d"), ".0f")?].concat()),
                        ),
                        (json!("diameter"), g(&e, "d")),
                        (
                            json!("width"),
                            b("*", b("*", json!(2.0), g(&e, "width")), json!(0.35)),
                        ),
                        (
                            json!("origin"),
                            json!([
                                (b(
                                    "+",
                                    b("/", u("-", g(&e, "run")), json!(2.0)),
                                    b("*", g(&e, "width"), b("+", g(&e, "i"), json!(1)))
                                )),
                                (json!(0.0)),
                                (b("+", g(&e, "top"), {
                                    let argv = vec![g(&e, "mouth"), g(&e, "depth"), g(&e, "d")];
                                    let kwargs = json!({});
                                    call(cx, "_holder", "cradle_seat", argv, kwargs, None)?
                                }))
                            ]),
                        ),
                    ]));
                }
                json!(temp33)
            });
            e.insert("signature".into(), g(&e, "seated_defaults"));
            cx.holder_updates = g(&e, "HOLDERS");
            return Ok(object(vec![
                (json!("holders"), g(&e, "rows")),
                (json!("assets"), g(&e, "assets")),
                (json!("reels"), g(&e, "reels")),
                (
                    json!("extension_z"),
                    ix(g(&e, "manifest"), json!("extension_z_mm")),
                ),
                (json!("color"), json!(seq(g(&e, "kit_color")))),
                (json!("witness_color"), json!(seq(g(&e, "witness_color")))),
                (
                    json!("limits"),
                    json!([
                        (attr(cx, "_kit", "h2c_build_x")?),
                        (attr(cx, "_kit", "h2c_build_y")?),
                        (attr(cx, "_kit", "h2c_build_z")?)
                    ]),
                ),
                (
                    json!("max_overlap"),
                    attr_value(
                        ix(
                            attr_value(g(&e, "signature"), "parameters"),
                            json!("max_overlap"),
                        ),
                        "default",
                    ),
                ),
                (
                    json!("max_gap"),
                    attr_value(
                        ix(
                            attr_value(g(&e, "signature"), "parameters"),
                            json!("max_gap"),
                        ),
                        "default",
                    ),
                ),
            ]));
            Ok(Value::Null)
        }
        ("holders", "_stock_key") => {
            e.insert(
                "parameters".into(),
                args.get(0)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "parameters"))
                    .unwrap_or_else(|| missing("parameters")),
            );
            e.insert(
                "manifest".into(),
                args.get(1)
                    .cloned()
                    .or_else(|| kwarg(&kwargs, "manifest"))
                    .unwrap_or_else(|| missing("manifest")),
            );
            for item in seq(method(
                ix(g(&e, "manifest"), json!("models")),
                "items",
                vec![],
            )) {
                {
                    let temp35 = item;
                    e.insert("key".into(), ix(temp35.clone(), json!(0)));
                    e.insert("model".into(), ix(temp35.clone(), json!(1)));
                }
                if truth(&json!(compare(
                    "==",
                    ix(g(&e, "model"), json!("parameters")),
                    g(&e, "parameters")
                ))) {
                    return Ok(g(&e, "key"));
                } else {
                }
            }
            bail!(
                "{}",
                string(&json!(
                    [
                        "no stock reference for ".to_owned(),
                        format_value(g(&e, "parameters"), "")?
                    ]
                    .concat()
                ))
            );
            Ok(Value::Null)
        }
        _ => manual(cx, module, name, args, kwargs),
    }
}
