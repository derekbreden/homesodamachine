#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let assigned2 = {
        let fun5 = {
            let fun8 = e.get("Path")?;
            let mut args6 = Vec::new();
            let mut kw7 = Vec::new();
            args6.push(e.get("__file__")?);
            fun8.call(args6, kw7)?
        }
        .attr("resolve")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        fun5.call(args3, kw4)?
    };
    e.set("_here", assigned2.clone())?;
    {
        let fun11 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args9 = Vec::new();
        let mut kw10 = Vec::new();
        args9.push(Val::Int(0i64));
        args9.push({
            let fun14 = e.get("str")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(e.get("_here")?.attr("parent")?);
            fun14.call(args12, kw13)?
        });
        fun11.call(args9, kw10)?
    };
    {
        let fun17 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args15 = Vec::new();
        let mut kw16 = Vec::new();
        args15.push(Val::Int(0i64));
        args15.push({
            let fun20 = e.get("str")?;
            let mut args18 = Vec::new();
            let mut kw19 = Vec::new();
            args18.push(binary(
                "truediv",
                e.get("_here")?.attr("parent")?,
                Val::Str("reservoir".into()),
            )?);
            fun20.call(args18, kw19)?
        });
        fun17.call(args15, kw16)?
    };
    {
        let fun23 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args21 = Vec::new();
        let mut kw22 = Vec::new();
        args21.push(Val::Int(0i64));
        args21.push({
            let fun26 = e.get("str")?;
            let mut args24 = Vec::new();
            let mut kw25 = Vec::new();
            args24.push(binary(
                "truediv",
                e.get("_here")?.attr("parent")?,
                Val::Str("prv-shroud".into()),
            )?);
            fun26.call(args24, kw25)?
        });
        fun23.call(args21, kw22)?
    };
    {
        let fun29 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args27 = Vec::new();
        let mut kw28 = Vec::new();
        args27.push(Val::Int(0i64));
        args27.push({
            let fun32 = e.get("str")?;
            let mut args30 = Vec::new();
            let mut kw31 = Vec::new();
            args30.push(binary(
                "truediv",
                e.get("_here")?.attr("parents")?.get(Val::Int(2i64))?,
                Val::Str("scripts".into()),
            )?);
            fun32.call(args30, kw31)?
        });
        fun29.call(args27, kw28)?
    };
    let mod33 = rt.import_module("_cold_core_interface")?;
    e.set(
        "cap_conduit_shell_xy",
        rt.member("_cold_core_interface", "cap_conduit_shell_xy")?,
    )?;
    e.set(
        "cap_conduit_floor_xy",
        rt.member("_cold_core_interface", "cap_conduit_floor_xy")?,
    )?;
    e.set(
        "cap_passive_guides",
        rt.member("_cold_core_interface", "cap_passive_guides")?,
    )?;
    e.set(
        "cap_shell_clearance",
        rt.member("_cold_core_interface", "cap_shell_clearance")?,
    )?;
    e.set(
        "co2_inlet_y",
        rt.member("_cold_core_interface", "co2_inlet_y")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "hole_shift_from_edge",
        rt.member("_cold_core_interface", "hole_shift_from_edge")?,
    )?;
    e.set(
        "lldpe_bend_radius",
        rt.member("_cold_core_interface", "lldpe_bend_radius")?,
    )?;
    e.set(
        "lldpe_tube_od",
        rt.member("_cold_core_interface", "lldpe_tube_od")?,
    )?;
    e.set(
        "port_hole_radius",
        rt.member("_cold_core_interface", "port_hole_radius")?,
    )?;
    e.set(
        "outer_shell_y_length",
        rt.member("_cold_core_interface", "outer_shell_y_length")?,
    )?;
    e.set(
        "port_lane_mid_y",
        rt.member("_cold_core_interface", "port_lane_mid_y")?,
    )?;
    e.set(
        "carbonator_coil_envelope_radius",
        rt.member("_cold_core_interface", "carbonator_coil_envelope_radius")?,
    )?;
    e.set(
        "carbonator_outer_radius",
        rt.member("_cold_core_interface", "carbonator_outer_radius")?,
    )?;
    e.set(
        "evap_tail_high_z",
        rt.member("_cold_core_interface", "evap_tail_high_z")?,
    )?;
    e.set(
        "evap_tail_low_z",
        rt.member("_cold_core_interface", "evap_tail_low_z")?,
    )?;
    e.set(
        "carbonator_support_ring_height",
        rt.member("_cold_core_interface", "carbonator_support_ring_height")?,
    )?;
    e.set(
        "carbonator_top_plate_z",
        rt.member("_cold_core_interface", "carbonator_top_plate_z")?,
    )?;
    e.set(
        "carbonator_port_offset",
        rt.member("_cold_core_interface", "carbonator_port_offset")?,
    )?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "pocket_centerward_arc_outer_radius",
        rt.member("_cold_core_interface", "pocket_centerward_arc_outer_radius")?,
    )?;
    e.set(
        "water_outlet_upper_climb_x",
        rt.member("_cold_core_interface", "water_outlet_upper_climb_x")?,
    )?;
    e.set(
        "water_outlet_drift_z",
        rt.member("_cold_core_interface", "water_outlet_drift_z")?,
    )?;
    e.set(
        "west_lane_mid_y",
        rt.member("_cold_core_interface", "west_lane_mid_y")?,
    )?;
    let mod34 = rt.import_module("_foam_cap")?;
    e.set("cap_face_z", rt.member("_foam_cap", "cap_face_z")?)?;
    e.set("top_cap_height", rt.member("_foam_cap", "top_cap_height")?)?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    let mod35 = rt.import_module("_port_cuts")?;
    e.set(
        "co2_inlet_lane_xyz",
        rt.member("_port_cuts", "co2_inlet_lane_xyz")?,
    )?;
    e.set("co2_inlet_xyz", rt.member("_port_cuts", "co2_inlet_xyz")?)?;
    e.set(
        "front_face_port_z",
        rt.member("_port_cuts", "front_face_port_z")?,
    )?;
    e.set(
        "water_outlet_ring_crossing_x",
        rt.member("_port_cuts", "water_outlet_ring_crossing_x")?,
    )?;
    e.set("_reservoir", rt.import_module("reservoir")?)?;
    e.set("_shroud", rt.import_module("prv_shroud")?)?;
    let mod36 = rt.import_module("_routing")?;
    e.set("stock_min", rt.member("_routing", "stock_min")?)?;
    e.set("stock_of", rt.member("_routing", "stock_of")?)?;
    let assigned37 = binary("truediv", e.get("lldpe_tube_od")?, Val::Float(2.0f64))?;
    e.set("line_radius", assigned37.clone())?;
    let assigned38 = Val::Float(2.0f64);
    e.set("line_hug", assigned38.clone())?;
    let assigned39 = {
        let fun42 = e.get("stock_min")?;
        let mut args40 = Vec::new();
        let mut kw41 = Vec::new();
        args40.push(Val::Str("fluid".into()));
        args40.push(e.get("lldpe_tube_od")?);
        fun42.call(args40, kw41)?
    };
    e.set("route_bend_radius", assigned39.clone())?;
    let assigned43 = {
        let fun46 = e.get("stock_of")?;
        let mut args44 = Vec::new();
        let mut kw45 = Vec::new();
        args44.push(Val::Str("fluid".into()));
        args44.push(e.get("lldpe_tube_od")?);
        fun46.call(args44, kw45)?
    };
    e.set("route_stock", assigned43.clone())?;
    let assigned47 = e.get("_reservoir")?.attr("dip_tube_mouth_z")?;
    e.set("dip_tube_z", assigned47.clone())?;
    let assigned48 = e.get("front_face_port_z")?;
    e.set("plate_storey_z", assigned48.clone())?;
    let assigned49 = binary(
        "add",
        e.get("carbonator_top_plate_z")?,
        e.get("hole_shift_from_edge")?,
    )?;
    e.set("top_band_z", assigned49.clone())?;
    let assigned50 = e.get("foam_shell_outer_height")?;
    e.set("shell_top_z", assigned50.clone())?;
    let assigned51 = e.get("cap_face_z")?;
    e.set("conduit_mouth_z", assigned51.clone())?;
    let assigned52 = binary("sub", e.get("shell_top_z")?, e.get("route_bend_radius")?)?;
    e.set("lane_step_top_z", assigned52.clone())?;
    let assigned53 = e.get("_reservoir")?.attr("cap_assembly_lift")?;
    e.set("reservoir_cap_z", assigned53.clone())?;
    let assigned54 = binary(
        "add",
        e.get("reservoir_cap_z")?,
        e.get("_reservoir")?.attr("cap_total_height")?,
    )?;
    e.set("reservoir_cap_top_z", assigned54.clone())?;
    let assigned55 = e.get("west_lane_mid_y")?;
    e.set("prv_vent_lane_y", assigned55.clone())?;
    let assigned56 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(e.get("prv_vent_lane_y")?);
        s.push(binary(
            "sub",
            binary(
                "add",
                e.get("carbonator_top_plate_z")?,
                e.get("hole_shift_from_edge")?,
            )?,
            binary(
                "truediv",
                e.get("_shroud")?.attr("outer_diameter")?,
                Val::Float(2.0f64),
            )?,
        )?);
        Val::tuple(s)
    };
    e.set("prv_vent_start", assigned56.clone())?;
    let assigned57 = binary(
        "truediv",
        e.get("outer_shell_y_length")?,
        Val::Float(2.0f64),
    )?;
    e.set("prv_vent_flank_y", assigned57.clone())?;
    let assigned58 = Val::Float(2.0f64);
    e.set("prv_vent_fall_margin", assigned58.clone())?;
    let assigned59 = binary(
        "sub",
        e.get("prv_vent_start")?.get(Val::Int(2i64))?,
        binary(
            "add",
            e.get("route_bend_radius")?,
            e.get("prv_vent_fall_margin")?,
        )?,
    )?;
    e.set("prv_vent_cross_z", assigned59.clone())?;
    let assigned60 = binary(
        "add",
        binary(
            "sub",
            e.get("route_bend_radius")?,
            binary("sub", e.get("prv_vent_flank_y")?, e.get("prv_vent_lane_y")?)?,
        )?,
        Val::Float(1.0f64),
    )?;
    e.set("prv_vent_reach", assigned60.clone())?;
    let assigned61 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            e.get("wall_and_floor_thickness")?,
            e.get("carbonator_support_ring_height")?,
        )?);
        s.push(e.get("carbonator_top_plate_z")?);
        Val::tuple(s)
    };
    e.set("carbonator_envelope_z_range", assigned61.clone())?;
    // coil_standoff_y
    e.set("coil_standoff_y", {
        let params = vec![("x".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned62 = binary(
                "add",
                binary(
                    "add",
                    e.get("carbonator_coil_envelope_radius")?,
                    e.get("line_radius")?,
                )?,
                e.get("line_hug")?,
            )?;
            e.set("clear", assigned62.clone())?;
            let assigned63 = binary(
                "sub",
                binary("pow", e.get("clear")?, Val::Int(2i64))?,
                binary("pow", e.get("x")?, Val::Int(2i64))?,
            )?;
            e.set("reach", assigned63.clone())?;
            return Ok(
                if {
                    let v64 = e.get("reach")?;
                    let v65 = Val::Float(0.0f64);
                    Val::Bool(compare("gt", v64.clone(), v65.clone())?.truthy()?)
                }
                .truthy()?
                {
                    unary("neg", {
                        let fun68 = e.get("math")?.attr("sqrt")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        args66.push(e.get("reach")?);
                        fun68.call(args66, kw67)?
                    })?
                } else {
                    Val::Float(0.0f64)
                },
            );
            Ok(Val::None)
        })
    })?;
    // annulus_y
    e.set("annulus_y", {
        let params = vec![("x".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned69 = binary(
                "truediv",
                binary(
                    "sub",
                    binary(
                        "add",
                        e.get("carbonator_coil_envelope_radius")?,
                        e.get("pocket_centerward_arc_outer_radius")?,
                    )?,
                    e.get("wall_and_floor_thickness")?,
                )?,
                Val::Float(2.0f64),
            )?;
            e.set("mid", assigned69.clone())?;
            let assigned70 = binary(
                "sub",
                binary("pow", e.get("mid")?, Val::Int(2i64))?,
                binary("pow", e.get("x")?, Val::Int(2i64))?,
            )?;
            e.set("reach", assigned70.clone())?;
            return Ok(
                if {
                    let v71 = e.get("reach")?;
                    let v72 = Val::Float(0.0f64);
                    Val::Bool(compare("gt", v71.clone(), v72.clone())?.truthy()?)
                }
                .truthy()?
                {
                    unary("neg", {
                        let fun75 = e.get("math")?.attr("sqrt")?;
                        let mut args73 = Vec::new();
                        let mut kw74 = Vec::new();
                        args73.push(e.get("reach")?);
                        fun75.call(args73, kw74)?
                    })?
                } else {
                    Val::Float(0.0f64)
                },
            );
            Ok(Val::None)
        })
    })?;
    // co2_run_y
    e.set("co2_run_y", {
        let params = vec![("x".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned76 = {
                let mut s = Vec::new();
                s.push(e.get("co2_inlet_lane_xyz")?);
                s.push(e.get("co2_inlet_xyz")?);
                Val::tuple(s)
            };
            let unpack77 = unpack(assigned76.clone(), 2)?;
            let unpack78 = unpack(unpack77[0].clone(), 3)?;
            e.set("x0", unpack78[0].clone())?;
            e.set("y0", unpack78[1].clone())?;
            e.set("_z0", unpack78[2].clone())?;
            let unpack79 = unpack(unpack77[1].clone(), 3)?;
            e.set("x1", unpack79[0].clone())?;
            e.set("y1", unpack79[1].clone())?;
            e.set("_z1", unpack79[2].clone())?;
            if unary("not", {
                let v86 = binary(
                    "sub",
                    {
                        let fun82 = e.get("min")?;
                        let mut args80 = Vec::new();
                        let mut kw81 = Vec::new();
                        args80.push(e.get("x0")?);
                        args80.push(e.get("x1")?);
                        fun82.call(args80, kw81)?
                    },
                    Val::Float(1e-09f64),
                )?;
                let v87 = e.get("x")?;
                let v88 = binary(
                    "add",
                    {
                        let fun85 = e.get("max")?;
                        let mut args83 = Vec::new();
                        let mut kw84 = Vec::new();
                        args83.push(e.get("x0")?);
                        args83.push(e.get("x1")?);
                        fun85.call(args83, kw84)?
                    },
                    Val::Float(1e-09f64),
                )?;
                Val::Bool(
                    compare("le", v86.clone(), v87.clone())?.truthy()?
                        && compare("le", v87.clone(), v88.clone())?.truthy()?,
                )
            })?
            .truthy()?
            {
                return Ok(Val::None);
            }
            return Ok(binary(
                "add",
                e.get("y0")?,
                binary(
                    "truediv",
                    binary(
                        "mul",
                        binary("sub", e.get("y1")?, e.get("y0")?)?,
                        binary("sub", e.get("x")?, e.get("x0")?)?,
                    )?,
                    binary("sub", e.get("x1")?, e.get("x0")?)?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    // _routes
    e.set("_routes", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned89 = e.get("water_outlet_ring_crossing_x")?;
            e.set("carb_x", assigned89.clone())?;
            let assigned90 = {
                let fun93 = e.get("annulus_y")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                args91.push(e.get("carb_x")?);
                fun93.call(args91, kw92)?
            };
            e.set("carb_riser_y", assigned90.clone())?;
            let assigned94 = e.get("water_outlet_upper_climb_x")?;
            e.set("carb_upper_x", assigned94.clone())?;
            let assigned95 = {
                let fun98 = e.get("coil_standoff_y")?;
                let mut args96 = Vec::new();
                let mut kw97 = Vec::new();
                args96.push(e.get("carb_upper_x")?);
                fun98.call(args96, kw97)?
            };
            e.set("carb_upper_y", assigned95.clone())?;
            let assigned99 = binary(
                "truediv",
                binary("add", e.get("carb_x")?, e.get("carb_upper_x")?)?,
                Val::Float(2.0f64),
            )?;
            e.set("carb_mid_x", assigned99.clone())?;
            let assigned100 = {
                let fun103 = e
                    .get("_above_mounts")?
                    .attr("above_core")?
                    .attr("specification")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                fun103.call(args101, kw102)?
            }
            .get(Val::Str("gas_guide_world_mm".into()))?;
            e.set("gas_guide", assigned100.clone())?;
            let assigned104 = {
                let mut s = Vec::new();
                s.push(Val::Float(75.0f64));
                s.push(Val::Float(371.8f64));
                Val::tuple(s)
            };
            e.set("gas_lower_xy", assigned104.clone())?;
            let assigned105 = {
                let fun108 = e.get("math")?.attr("dist")?;
                let mut args106 = Vec::new();
                let mut kw107 = Vec::new();
                args106.push(e.get("gas_guide")?.get(Val::Slice {
                    start: None,
                    stop: Some(Val::Int(2i64).integer()?),
                    step: 1,
                })?);
                args106.push(e.get("gas_lower_xy")?);
                fun108.call(args106, kw107)?
            };
            e.set("gas_shift", assigned105.clone())?;
            let assigned109 = {
                let fun112 = e.get("math")?.attr("acos")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                args110.push(binary(
                    "sub",
                    Val::Float(1.0f64),
                    binary(
                        "truediv",
                        e.get("gas_shift")?,
                        binary("mul", Val::Float(2.0f64), e.get("route_bend_radius")?)?,
                    )?,
                )?);
                fun112.call(args110, kw111)?
            };
            e.set("gas_theta", assigned109.clone())?;
            let assigned113 = binary("mul", e.get("route_bend_radius")?, {
                let fun116 = e.get("math")?.attr("tan")?;
                let mut args114 = Vec::new();
                let mut kw115 = Vec::new();
                args114.push(binary("truediv", e.get("gas_theta")?, Val::Float(2.0f64))?);
                fun116.call(args114, kw115)?
            })?;
            e.set("gas_setback", assigned113.clone())?;
            let assigned117 = binary(
                "mul",
                binary("mul", Val::Float(2.0f64), e.get("route_bend_radius")?)?,
                {
                    let fun120 = e.get("math")?.attr("sin")?;
                    let mut args118 = Vec::new();
                    let mut kw119 = Vec::new();
                    args118.push(e.get("gas_theta")?);
                    fun120.call(args118, kw119)?
                },
            )?;
            e.set("gas_drop", assigned117.clone())?;
            let assigned121 = Val::Float(230.4f64);
            e.set("gas_turn_z", assigned121.clone())?;
            let assigned122 = {
                let fun125 = e
                    .get("_above_mounts")?
                    .attr("above_core")?
                    .attr("specification")?;
                let mut args123 = Vec::new();
                let mut kw124 = Vec::new();
                fun125.call(args123, kw124)?
            }
            .get(Val::Str("cap_guides_world_mm".into()))?
            .get(Val::Str("water-in".into()))?;
            e.set("water_guide", assigned122.clone())?;
            let assigned126 = binary(
                "add",
                binary("truediv", e.get("math")?.attr("pi")?, Val::Float(4.0f64))?,
                {
                    let fun129 = e.get("math")?.attr("asin")?;
                    let mut args127 = Vec::new();
                    let mut kw128 = Vec::new();
                    args127.push(binary(
                        "truediv",
                        binary(
                            "sub",
                            binary("truediv", Val::Float(14.9f64), e.get("route_bend_radius")?)?,
                            Val::Float(1.0f64),
                        )?,
                        {
                            let fun132 = e.get("math")?.attr("sqrt")?;
                            let mut args130 = Vec::new();
                            let mut kw131 = Vec::new();
                            args130.push(Val::Float(2.0f64));
                            fun132.call(args130, kw131)?
                        },
                    )?);
                    fun129.call(args127, kw128)?
                },
            )?;
            e.set("water_theta", assigned126.clone())?;
            let assigned133 = binary("mul", e.get("route_bend_radius")?, {
                let fun136 = e.get("math")?.attr("tan")?;
                let mut args134 = Vec::new();
                let mut kw135 = Vec::new();
                args134.push(binary(
                    "truediv",
                    e.get("water_theta")?,
                    Val::Float(2.0f64),
                )?);
                fun136.call(args134, kw135)?
            })?;
            e.set("water_setback", assigned133.clone())?;
            let assigned137 = binary(
                "add",
                unary("neg", Val::Float(70.5f64))?,
                binary(
                    "mul",
                    e.get("route_bend_radius")?,
                    binary(
                        "add",
                        {
                            let fun140 = e.get("math")?.attr("sin")?;
                            let mut args138 = Vec::new();
                            let mut kw139 = Vec::new();
                            args138.push(e.get("water_theta")?);
                            fun140.call(args138, kw139)?
                        },
                        {
                            let fun143 = e.get("math")?.attr("cos")?;
                            let mut args141 = Vec::new();
                            let mut kw142 = Vec::new();
                            args141.push(e.get("water_theta")?);
                            fun143.call(args141, kw142)?
                        },
                    )?,
                )?,
            )?;
            e.set("water_turn_start", assigned137.clone())?;
            let assigned144 = unary("neg", Val::Float(78.5f64))?;
            e.set("water_lane_x", assigned144.clone())?;
            let assigned145 = Val::Float(363.0f64);
            e.set("water_return_y", assigned145.clone())?;
            let assigned146 = {
                let fun149 = e.get("math")?.attr("acos")?;
                let mut args147 = Vec::new();
                let mut kw148 = Vec::new();
                args147.push(binary(
                    "sub",
                    Val::Float(1.0f64),
                    binary(
                        "truediv",
                        {
                            let fun152 = e.get("abs")?;
                            let mut args150 = Vec::new();
                            let mut kw151 = Vec::new();
                            args150.push(binary(
                                "add",
                                e.get("water_lane_x")?,
                                Val::Float(70.5f64),
                            )?);
                            fun152.call(args150, kw151)?
                        },
                        binary("mul", Val::Float(2.0f64), e.get("route_bend_radius")?)?,
                    )?,
                )?);
                fun149.call(args147, kw148)?
            };
            e.set("water_return_theta", assigned146.clone())?;
            let assigned153 = binary("mul", e.get("route_bend_radius")?, {
                let fun156 = e.get("math")?.attr("tan")?;
                let mut args154 = Vec::new();
                let mut kw155 = Vec::new();
                args154.push(binary(
                    "truediv",
                    e.get("water_return_theta")?,
                    Val::Float(2.0f64),
                )?);
                fun156.call(args154, kw155)?
            })?;
            e.set("water_return_setback", assigned153.clone())?;
            let assigned157 = binary(
                "mul",
                binary("mul", Val::Float(2.0f64), e.get("route_bend_radius")?)?,
                {
                    let fun160 = e.get("math")?.attr("sin")?;
                    let mut args158 = Vec::new();
                    let mut kw159 = Vec::new();
                    args158.push(e.get("water_return_theta")?);
                    fun160.call(args158, kw159)?
                },
            )?;
            e.set("water_return_run", assigned157.clone())?;
            let assigned161 = {
                let fun164 = e.get("co2_run_y")?;
                let mut args162 = Vec::new();
                let mut kw163 = Vec::new();
                args162.push(e.get("carb_x")?);
                fun164.call(args162, kw163)?
            };
            e.set("co2_under_tank_y", assigned161.clone())?;
            let assigned165 = if {
                let v166 = e.get("co2_under_tank_y")?;
                let v167 = Val::None;
                Val::Bool(compare("is", v166.clone(), v167.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Float(0.0f64)
            } else {
                binary(
                    "mul",
                    binary("add", e.get("lldpe_tube_od")?, e.get("line_hug")?)?,
                    binary(
                        "truediv",
                        binary(
                            "sub",
                            e.get("carbonator_port_offset")?,
                            e.get("carb_riser_y")?,
                        )?,
                        binary(
                            "sub",
                            e.get("carbonator_port_offset")?,
                            e.get("co2_under_tank_y")?,
                        )?,
                    )?,
                )?
            };
            e.set("carb_co2_rise", assigned165.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("water-in".into()),
                    binary(
                        "add",
                        {
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.0f64));
                                s.push(unary("neg", e.get("carbonator_port_offset")?)?);
                                s.push(e.get("top_band_z")?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        },
                        {
                            let e = e.child();
                            let out168 = Val::list(vec![]);
                            for item169 in {
                                let mut s = Vec::new();
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(unary("neg", Val::Float(20.0f64))?);
                                    s.push(Val::Float(283.0f64));
                                    s.push(Val::Float(219.4f64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "sub",
                                        e.get("water_turn_start")?,
                                        e.get("water_setback")?,
                                    )?);
                                    s.push(Val::Float(283.0f64));
                                    s.push(Val::Float(219.4f64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(unary("neg", Val::Float(70.5f64))?);
                                    s.push(Val::Float(283.0f64));
                                    s.push(Val::Float(204.5f64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(unary("neg", Val::Float(70.5f64))?);
                                    s.push(binary(
                                        "add",
                                        e.get("water_return_y")?,
                                        e.get("water_return_setback")?,
                                    )?);
                                    s.push(Val::Float(204.5f64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("water_lane_x")?);
                                    s.push(binary(
                                        "sub",
                                        binary(
                                            "add",
                                            e.get("water_return_y")?,
                                            e.get("water_return_run")?,
                                        )?,
                                        e.get("water_return_setback")?,
                                    )?);
                                    s.push(Val::Float(204.5f64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.push(e.get("water_lane_x")?);
                                    s.push(Val::Float(385.0f64));
                                    s.push(Val::Float(204.5f64));
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.extend(
                                        e.get("water_guide")?
                                            .get(Val::Slice {
                                                start: None,
                                                stop: Some(Val::Int(2i64).integer()?),
                                                step: 1,
                                            })?
                                            .iter()?,
                                    );
                                    s.push(Val::Float(204.5f64));
                                    Val::tuple(s)
                                });
                                s.push(e.get("water_guide")?);
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                e.set("p", item169)?;
                                out168.attr("append")?.call(
                                    vec![{
                                        let fun172 = e.get("world_point_in_shell")?;
                                        let mut args170 = Vec::new();
                                        let mut kw171 = Vec::new();
                                        args170.push(e.get("p")?);
                                        fun172.call(args170, kw171)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out168
                        },
                    )?,
                )?;
                d.set(Val::Str("reservoir-a".into()), {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        {
                            let fun175 = e.get("cap_conduit_shell_xy")?;
                            let mut args173 = Vec::new();
                            let mut kw174 = Vec::new();
                            args173.push(Val::Str("reservoir-a".into()));
                            fun175.call(args173, kw174)?
                        },
                        {
                            let mut s = Vec::new();
                            s.push(e.get("dip_tube_z")?);
                            Val::tuple(s)
                        },
                    )?);
                    s.push(binary(
                        "add",
                        {
                            let fun178 = e.get("cap_conduit_shell_xy")?;
                            let mut args176 = Vec::new();
                            let mut kw177 = Vec::new();
                            args176.push(Val::Str("reservoir-a".into()));
                            fun178.call(args176, kw177)?
                        },
                        {
                            let mut s = Vec::new();
                            s.push(e.get("conduit_mouth_z")?);
                            Val::tuple(s)
                        },
                    )?);
                    Val::list(s)
                })?;
                d.set(Val::Str("reservoir-b".into()), {
                    let fun181 = e.get("reservoir_guide_route")?;
                    let mut args179 = Vec::new();
                    let mut kw180 = Vec::new();
                    args179.push(Val::Str("reservoir-b".into()));
                    args179.push(e.get("dip_tube_z")?);
                    fun181.call(args179, kw180)?
                })?;
                d.set(
                    Val::Str("co2-in".into()),
                    binary(
                        "add",
                        {
                            let e = e.child();
                            let out182 = Val::list(vec![]);
                            for item183 in {
                                let mut s = Vec::new();
                                s.push(e.get("gas_guide")?);
                                s.push({
                                    let mut s = Vec::new();
                                    s.extend(
                                        e.get("gas_guide")?
                                            .get(Val::Slice {
                                                start: None,
                                                stop: Some(Val::Int(2i64).integer()?),
                                                step: 1,
                                            })?
                                            .iter()?,
                                    );
                                    s.push(binary(
                                        "sub",
                                        e.get("gas_turn_z")?,
                                        e.get("gas_setback")?,
                                    )?);
                                    Val::tuple(s)
                                });
                                s.push({
                                    let mut s = Vec::new();
                                    s.extend(e.get("gas_lower_xy")?.iter()?);
                                    s.push(binary(
                                        "add",
                                        binary("sub", e.get("gas_turn_z")?, e.get("gas_drop")?)?,
                                        e.get("gas_setback")?,
                                    )?);
                                    Val::tuple(s)
                                });
                                Val::tuple(s)
                            }
                            .iter()?
                            {
                                e.set("p", item183)?;
                                out182.attr("append")?.call(
                                    vec![{
                                        let fun186 = e.get("world_point_in_shell")?;
                                        let mut args184 = Vec::new();
                                        let mut kw185 = Vec::new();
                                        args184.push(e.get("p")?);
                                        fun186.call(args184, kw185)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out182
                        },
                        {
                            let mut s = Vec::new();
                            s.push(e.get("co2_inlet_lane_xyz")?);
                            s.push(e.get("co2_inlet_xyz")?);
                            Val::list(s)
                        },
                    )?,
                )?;
                d.set(Val::Str("carb-water-out".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(unary("pos", e.get("carbonator_port_offset")?)?);
                        s.push(e.get("plate_storey_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("carb_x")?);
                        s.push(unary("pos", e.get("carbonator_port_offset")?)?);
                        s.push(e.get("plate_storey_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("carb_x")?);
                        s.push(e.get("carb_riser_y")?);
                        s.push(binary(
                            "add",
                            e.get("plate_storey_z")?,
                            e.get("carb_co2_rise")?,
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("carb_x")?);
                        s.push(e.get("carb_riser_y")?);
                        s.push(e.get("water_outlet_drift_z")?.get(Val::Int(0i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("carb_mid_x")?);
                        s.push({
                            let fun189 = e.get("coil_standoff_y")?;
                            let mut args187 = Vec::new();
                            let mut kw188 = Vec::new();
                            args187.push(e.get("carb_mid_x")?);
                            fun189.call(args187, kw188)?
                        });
                        s.push(binary(
                            "truediv",
                            {
                                let fun192 = e.get("sum")?;
                                let mut args190 = Vec::new();
                                let mut kw191 = Vec::new();
                                args190.push(e.get("water_outlet_drift_z")?);
                                fun192.call(args190, kw191)?
                            },
                            Val::Float(2.0f64),
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("carb_upper_x")?);
                        s.push(e.get("carb_upper_y")?);
                        s.push(e.get("water_outlet_drift_z")?.get(Val::Int(1i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("carb_upper_x")?);
                        s.push(e.get("carb_upper_y")?);
                        s.push(e.get("top_band_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.extend(
                            {
                                let fun195 = e.get("cap_conduit_shell_xy")?;
                                let mut args193 = Vec::new();
                                let mut kw194 = Vec::new();
                                args193.push(Val::Str("carb-water-out".into()));
                                fun195.call(args193, kw194)?
                            }
                            .iter()?,
                        );
                        s.push(e.get("top_band_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.extend(
                            {
                                let fun198 = e.get("cap_conduit_shell_xy")?;
                                let mut args196 = Vec::new();
                                let mut kw197 = Vec::new();
                                args196.push(Val::Str("carb-water-out".into()));
                                fun198.call(args196, kw197)?
                            }
                            .iter()?,
                        );
                        s.push(e.get("conduit_mouth_z")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                })?;
                d.set(Val::Str("prv-vent".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("prv_vent_start")?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("prv_vent_start")?.get(Val::Int(0i64))?);
                        s.push(e.get("prv_vent_lane_y")?);
                        s.push(e.get("prv_vent_cross_z")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("prv_vent_start")?.get(Val::Int(0i64))?);
                        s.push(binary(
                            "add",
                            e.get("prv_vent_flank_y")?,
                            e.get("prv_vent_reach")?,
                        )?);
                        s.push(e.get("prv_vent_cross_z")?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                })?;
                d.set(Val::Str("reservoir-a-fill".into()), {
                    let fun201 = e.get("reservoir_guide_route")?;
                    let mut args199 = Vec::new();
                    let mut kw200 = Vec::new();
                    args199.push(Val::Str("reservoir-a-fill".into()));
                    args199.push(binary(
                        "sub",
                        binary(
                            "add",
                            e.get("reservoir_cap_z")?,
                            e.get("_reservoir")?.attr("cap_wall_height")?,
                        )?,
                        Val::Float(1.0f64),
                    )?);
                    fun201.call(args199, kw200)?
                })?;
                d.set(Val::Str("reservoir-b-fill".into()), {
                    let e = e.child();
                    let out202 = Val::list(vec![]);
                    for item203 in {
                        let fun206 = e.get("_above_mounts")?.attr("reservoir_b_fill_passage")?;
                        let mut args204 = Vec::new();
                        let mut kw205 = Vec::new();
                        fun206.call(args204, kw205)?
                    }
                    .get(Val::Str("route_points_world_mm".into()))?
                    .iter()?
                    {
                        e.set("p", item203)?;
                        out202.attr("append")?.call(
                            vec![{
                                let fun209 = e.get("world_point_in_shell")?;
                                let mut args207 = Vec::new();
                                let mut kw208 = Vec::new();
                                args207.push(e.get("p")?);
                                fun209.call(args207, kw208)?
                            }],
                            vec![],
                        )?;
                    }
                    out202
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // world_point_in_shell
    e.set("world_point_in_shell", {
        let params = vec![("point".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned210 = {
                let fun213 = e
                    .get("_above_mounts")?
                    .attr("above_core")?
                    .attr("world_to_cap")?;
                let mut args211 = Vec::new();
                let mut kw212 = Vec::new();
                args211.push(e.get("point")?);
                fun213.call(args211, kw212)?
            };
            let unpack214 = unpack(assigned210.clone(), 3)?;
            e.set("x", unpack214[0].clone())?;
            e.set("y", unpack214[1].clone())?;
            e.set("z", unpack214[2].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(unary("neg", e.get("x")?)?);
                s.push(unary("neg", e.get("y")?)?);
                s.push(binary(
                    "add",
                    binary("add", e.get("z")?, e.get("foam_shell_outer_height")?)?,
                    e.get("top_cap_height")?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // reservoir_guide_route
    e.set("reservoir_guide_route", {
        let params = vec![
            ("name".into(), None, false),
            ("start_z".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned215 = {
                let fun218 = e.get("tuple")?;
                let mut args216 = Vec::new();
                let mut kw217 = Vec::new();
                args216.push({
                    let e = e.child();
                    let out219 = Val::list(vec![]);
                    for item220 in e.get("cap_conduit_floor_xy")?.get(e.get("name")?)?.iter()? {
                        e.set("v", item220)?;
                        out219
                            .attr("append")?
                            .call(vec![unary("neg", e.get("v")?)?], vec![])?;
                    }
                    out219
                });
                fun218.call(args216, kw217)?
            };
            e.set("lower_xy", assigned215.clone())?;
            return Ok({
                let fun223 = e.get("_above_mounts")?.attr("passive_guide_points")?;
                let mut args221 = Vec::new();
                let mut kw222 = Vec::new();
                args221.push(e.get("lower_xy")?);
                args221.push({
                    let fun226 = e.get("cap_conduit_shell_xy")?;
                    let mut args224 = Vec::new();
                    let mut kw225 = Vec::new();
                    args224.push(e.get("name")?);
                    fun226.call(args224, kw225)?
                });
                args221.push(e.get("start_z")?);
                args221.push(e.get("conduit_mouth_z")?);
                args221.push(binary(
                    "add",
                    binary(
                        "add",
                        binary(
                            "add",
                            e.get("foam_shell_outer_height")?,
                            e.get("cap_shell_clearance")?,
                        )?,
                        e.get("wall_and_floor_thickness")?,
                    )?,
                    Val::Float(0.25f64),
                )?);
                args221.push(e.get("route_bend_radius")?);
                fun223.call(args221, kw222)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned227 = {
        let fun230 = e.get("_routes")?;
        let mut args228 = Vec::new();
        let mut kw229 = Vec::new();
        fun230.call(args228, kw229)?
    };
    e.set("routes", assigned227.clone())?;
    // _route_points
    e.set("_route_points", {
        let params = vec![("points".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned231 = {
                let mut s = Vec::new();
                s.push({
                    let fun234 = e.get("tuple")?;
                    let mut args232 = Vec::new();
                    let mut kw233 = Vec::new();
                    args232.push(e.get("points")?.get(Val::Int(0i64))?);
                    fun234.call(args232, kw233)?
                });
                Val::list(s)
            };
            e.set("kept", assigned231.clone())?;
            for item235 in e
                .get("points")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: None,
                    step: 1,
                })?
                .iter()?
            {
                e.set("p", item235)?;
                let assigned236 = {
                    let fun239 = e.get("tuple")?;
                    let mut args237 = Vec::new();
                    let mut kw238 = Vec::new();
                    args237.push(e.get("p")?);
                    fun239.call(args237, kw238)?
                };
                e.set("v", assigned236.clone())?;
                if {
                    let v246 = {
                        let fun242 = e.get("_route_length")?;
                        let mut args240 = Vec::new();
                        let mut kw241 = Vec::new();
                        args240.push({
                            let fun245 = e.get("_route_sub")?;
                            let mut args243 = Vec::new();
                            let mut kw244 = Vec::new();
                            args243.push(e.get("v")?);
                            args243.push(e.get("kept")?.get(unary("neg", Val::Int(1i64))?)?);
                            fun245.call(args243, kw244)?
                        });
                        fun242.call(args240, kw241)?
                    };
                    let v247 = Val::Float(1e-09f64);
                    Val::Bool(compare("lt", v246.clone(), v247.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                if {
                    let v251 = {
                        let fun250 = e.get("len")?;
                        let mut args248 = Vec::new();
                        let mut kw249 = Vec::new();
                        args248.push(e.get("kept")?);
                        fun250.call(args248, kw249)?
                    };
                    let v252 = Val::Int(2i64);
                    Val::Bool(compare("ge", v251.clone(), v252.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned253 = {
                        let mut s = Vec::new();
                        s.push(e.get("kept")?.get(unary("neg", Val::Int(2i64))?)?);
                        s.push(e.get("kept")?.get(unary("neg", Val::Int(1i64))?)?);
                        Val::tuple(s)
                    };
                    let unpack254 = unpack(assigned253.clone(), 2)?;
                    e.set("a", unpack254[0].clone())?;
                    e.set("b", unpack254[1].clone())?;
                    if {
                        let v273 = {
                            let fun257 = e.get("_route_length")?;
                            let mut args255 = Vec::new();
                            let mut kw256 = Vec::new();
                            args255.push({
                                let fun260 = e.get("_route_cross")?;
                                let mut args258 = Vec::new();
                                let mut kw259 = Vec::new();
                                args258.push({
                                    let fun263 = e.get("_route_unit")?;
                                    let mut args261 = Vec::new();
                                    let mut kw262 = Vec::new();
                                    args261.push({
                                        let fun266 = e.get("_route_sub")?;
                                        let mut args264 = Vec::new();
                                        let mut kw265 = Vec::new();
                                        args264.push(e.get("b")?);
                                        args264.push(e.get("a")?);
                                        fun266.call(args264, kw265)?
                                    });
                                    fun263.call(args261, kw262)?
                                });
                                args258.push({
                                    let fun269 = e.get("_route_unit")?;
                                    let mut args267 = Vec::new();
                                    let mut kw268 = Vec::new();
                                    args267.push({
                                        let fun272 = e.get("_route_sub")?;
                                        let mut args270 = Vec::new();
                                        let mut kw271 = Vec::new();
                                        args270.push(e.get("v")?);
                                        args270.push(e.get("b")?);
                                        fun272.call(args270, kw271)?
                                    });
                                    fun269.call(args267, kw268)?
                                });
                                fun260.call(args258, kw259)?
                            });
                            fun257.call(args255, kw256)?
                        };
                        let v274 = Val::Float(1e-09f64);
                        Val::Bool(compare("lt", v273.clone(), v274.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned275 = e.get("v")?;
                        e.get("kept")?
                            .set(unary("neg", Val::Int(1i64))?, assigned275.clone())?;
                        continue;
                    }
                }
                {
                    let fun278 = e.get("kept")?.attr("append")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push(e.get("v")?);
                    fun278.call(args276, kw277)?
                };
            }
            return Ok(e.get("kept")?);
            Ok(Val::None)
        })
    })?;
    // _corner_data
    e.set("_corner_data", {
        let params = vec![
            ("points".into(), None, false),
            ("bend_radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned279 = {
                let fun282 = e.get("_route_points")?;
                let mut args280 = Vec::new();
                let mut kw281 = Vec::new();
                args280.push(e.get("points")?);
                fun282.call(args280, kw281)?
            };
            e.set("v", assigned279.clone())?;
            let assigned283 = {
                let fun286 = e.get("len")?;
                let mut args284 = Vec::new();
                let mut kw285 = Vec::new();
                args284.push(e.get("v")?);
                fun286.call(args284, kw285)?
            };
            e.set("n", assigned283.clone())?;
            let assigned287 = binary(
                "mul",
                {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    Val::list(s)
                },
                e.get("n")?,
            )?;
            e.set("half", assigned287.clone())?;
            for item288 in {
                let fun318 = e.get("range")?;
                let mut args316 = Vec::new();
                let mut kw317 = Vec::new();
                args316.push(Val::Int(1i64));
                args316.push(binary("sub", e.get("n")?, Val::Int(1i64))?);
                fun318.call(args316, kw317)?
            }
            .iter()?
            {
                e.set("i", item288)?;
                let assigned289 = {
                    let fun292 = e.get("_route_unit")?;
                    let mut args290 = Vec::new();
                    let mut kw291 = Vec::new();
                    args290.push({
                        let fun295 = e.get("_route_sub")?;
                        let mut args293 = Vec::new();
                        let mut kw294 = Vec::new();
                        args293.push(e.get("v")?.get(binary(
                            "sub",
                            e.get("i")?,
                            Val::Int(1i64),
                        )?)?);
                        args293.push(e.get("v")?.get(e.get("i")?)?);
                        fun295.call(args293, kw294)?
                    });
                    fun292.call(args290, kw291)?
                };
                e.set("u", assigned289.clone())?;
                let assigned296 = {
                    let fun299 = e.get("_route_unit")?;
                    let mut args297 = Vec::new();
                    let mut kw298 = Vec::new();
                    args297.push({
                        let fun302 = e.get("_route_sub")?;
                        let mut args300 = Vec::new();
                        let mut kw301 = Vec::new();
                        args300.push(e.get("v")?.get(binary(
                            "add",
                            e.get("i")?,
                            Val::Int(1i64),
                        )?)?);
                        args300.push(e.get("v")?.get(e.get("i")?)?);
                        fun302.call(args300, kw301)?
                    });
                    fun299.call(args297, kw298)?
                };
                e.set("w", assigned296.clone())?;
                let assigned303 = binary(
                    "truediv",
                    {
                        let fun306 = e.get("math")?.attr("acos")?;
                        let mut args304 = Vec::new();
                        let mut kw305 = Vec::new();
                        args304.push({
                            let fun309 = e.get("max")?;
                            let mut args307 = Vec::new();
                            let mut kw308 = Vec::new();
                            args307.push(unary("neg", Val::Float(1.0f64))?);
                            args307.push({
                                let fun312 = e.get("min")?;
                                let mut args310 = Vec::new();
                                let mut kw311 = Vec::new();
                                args310.push(Val::Float(1.0f64));
                                args310.push({
                                    let fun315 = e.get("_route_dot")?;
                                    let mut args313 = Vec::new();
                                    let mut kw314 = Vec::new();
                                    args313.push(e.get("u")?);
                                    args313.push(e.get("w")?);
                                    fun315.call(args313, kw314)?
                                });
                                fun312.call(args310, kw311)?
                            });
                            fun309.call(args307, kw308)?
                        });
                        fun306.call(args304, kw305)?
                    },
                    Val::Float(2.0f64),
                )?;
                e.get("half")?.set(e.get("i")?, assigned303.clone())?;
            }
            let assigned319 = binary(
                "mul",
                {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    Val::list(s)
                },
                e.get("n")?,
            )?;
            e.set("radius", assigned319.clone())?;
            for item320 in {
                let fun324 = e.get("range")?;
                let mut args322 = Vec::new();
                let mut kw323 = Vec::new();
                args322.push(Val::Int(1i64));
                args322.push(binary("sub", e.get("n")?, Val::Int(1i64))?);
                fun324.call(args322, kw323)?
            }
            .iter()?
            {
                e.set("i", item320)?;
                let assigned321 = e.get("bend_radius")?;
                e.get("radius")?.set(e.get("i")?, assigned321.clone())?;
            }
            for item325 in {
                let fun364 = e.get("range")?;
                let mut args362 = Vec::new();
                let mut kw363 = Vec::new();
                args362.push(Val::Int(64i64));
                fun364.call(args362, kw363)?
            }
            .iter()?
            {
                e.set("_", item325)?;
                let assigned326 = {
                    let e = e.child();
                    let out327 = Val::list(vec![]);
                    for item328 in {
                        let fun331 = e.get("range")?;
                        let mut args329 = Vec::new();
                        let mut kw330 = Vec::new();
                        args329.push(e.get("n")?);
                        fun331.call(args329, kw330)?
                    }
                    .iter()?
                    {
                        e.set("i", item328)?;
                        out327.attr("append")?.call(
                            vec![if {
                                let v332 = e.get("half")?.get(e.get("i")?)?;
                                let v333 = Val::Float(1e-09f64);
                                Val::Bool(compare("gt", v332.clone(), v333.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                binary("truediv", e.get("radius")?.get(e.get("i")?)?, {
                                    let fun336 = e.get("math")?.attr("tan")?;
                                    let mut args334 = Vec::new();
                                    let mut kw335 = Vec::new();
                                    args334.push(e.get("half")?.get(e.get("i")?)?);
                                    fun336.call(args334, kw335)?
                                })?
                            } else {
                                Val::Float(0.0f64)
                            }],
                            vec![],
                        )?;
                    }
                    out327
                };
                e.set("setback", assigned326.clone())?;
                let assigned337 = Val::Float(1.0f64);
                e.set("worst", assigned337.clone())?;
                for item338 in {
                    let fun355 = e.get("range")?;
                    let mut args353 = Vec::new();
                    let mut kw354 = Vec::new();
                    args353.push(binary("sub", e.get("n")?, Val::Int(1i64))?);
                    fun355.call(args353, kw354)?
                }
                .iter()?
                {
                    e.set("i", item338)?;
                    let assigned339 = {
                        let fun342 = e.get("_route_length")?;
                        let mut args340 = Vec::new();
                        let mut kw341 = Vec::new();
                        args340.push({
                            let fun345 = e.get("_route_sub")?;
                            let mut args343 = Vec::new();
                            let mut kw344 = Vec::new();
                            args343.push(e.get("v")?.get(binary(
                                "add",
                                e.get("i")?,
                                Val::Int(1i64),
                            )?)?);
                            args343.push(e.get("v")?.get(e.get("i")?)?);
                            fun345.call(args343, kw344)?
                        });
                        fun342.call(args340, kw341)?
                    };
                    e.set("leg", assigned339.clone())?;
                    let assigned346 = binary(
                        "add",
                        e.get("setback")?.get(e.get("i")?)?,
                        e.get("setback")?
                            .get(binary("add", e.get("i")?, Val::Int(1i64))?)?,
                    )?;
                    e.set("want", assigned346.clone())?;
                    if {
                        let v347 = e.get("want")?;
                        let v348 = e.get("leg")?;
                        Val::Bool(compare("gt", v347.clone(), v348.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned349 = {
                            let fun352 = e.get("min")?;
                            let mut args350 = Vec::new();
                            let mut kw351 = Vec::new();
                            args350.push(e.get("worst")?);
                            args350.push(binary("truediv", e.get("leg")?, e.get("want")?)?);
                            fun352.call(args350, kw351)?
                        };
                        e.set("worst", assigned349.clone())?;
                    }
                }
                if {
                    let v356 = e.get("worst")?;
                    let v357 = binary("sub", Val::Float(1.0f64), Val::Float(1e-12f64))?;
                    Val::Bool(compare("ge", v356.clone(), v357.clone())?.truthy()?)
                }
                .truthy()?
                {
                    break;
                }
                for item358 in {
                    let fun361 = e.get("range")?;
                    let mut args359 = Vec::new();
                    let mut kw360 = Vec::new();
                    args359.push(Val::Int(1i64));
                    args359.push(binary("sub", e.get("n")?, Val::Int(1i64))?);
                    fun361.call(args359, kw360)?
                }
                .iter()?
                {
                    e.set("i", item358)?;
                    e.get("radius")?.set(
                        e.get("i")?,
                        binary(
                            "mul",
                            e.get("radius")?.get(e.get("i")?)?,
                            binary("mul", e.get("worst")?, Val::Float(0.999f64))?,
                        )?,
                    )?;
                }
            }
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("v")?);
                s.push(e.get("radius")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // route_legs
    e.set("route_legs", {
        let params = vec![
            ("points".into(), None, false),
            (
                "bend_radius".into(),
                Some(e.get("route_bend_radius")?),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned365 = {
                let fun368 = e.get("corner_radii")?;
                let mut args366 = Vec::new();
                let mut kw367 = Vec::new();
                args366.push(e.get("points")?);
                args366.push(e.get("bend_radius")?);
                fun368.call(args366, kw367)?
            };
            let unpack369 = unpack(assigned365.clone(), 2)?;
            e.set("v", unpack369[0].clone())?;
            e.set("radius", unpack369[1].clone())?;
            let assigned370 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("legs", assigned370.clone())?;
            let assigned371 = e.get("v")?.get(Val::Int(0i64))?;
            e.set("tail", assigned371.clone())?;
            for item372 in {
                let fun413 = e.get("range")?;
                let mut args411 = Vec::new();
                let mut kw412 = Vec::new();
                args411.push(Val::Int(1i64));
                args411.push(binary(
                    "sub",
                    {
                        let fun416 = e.get("len")?;
                        let mut args414 = Vec::new();
                        let mut kw415 = Vec::new();
                        args414.push(e.get("v")?);
                        fun416.call(args414, kw415)?
                    },
                    Val::Int(1i64),
                )?);
                fun413.call(args411, kw412)?
            }
            .iter()?
            {
                e.set("i", item372)?;
                let assigned373 = {
                    let fun376 = binary(
                        "sub",
                        e.get("v")?
                            .get(binary("sub", e.get("i")?, Val::Int(1i64))?)?,
                        e.get("v")?.get(e.get("i")?)?,
                    )?
                    .attr("normalized")?;
                    let mut args374 = Vec::new();
                    let mut kw375 = Vec::new();
                    fun376.call(args374, kw375)?
                };
                e.set("u", assigned373.clone())?;
                let assigned377 = {
                    let fun380 = binary(
                        "sub",
                        e.get("v")?
                            .get(binary("add", e.get("i")?, Val::Int(1i64))?)?,
                        e.get("v")?.get(e.get("i")?)?,
                    )?
                    .attr("normalized")?;
                    let mut args378 = Vec::new();
                    let mut kw379 = Vec::new();
                    fun380.call(args378, kw379)?
                };
                e.set("w", assigned377.clone())?;
                let assigned381 = binary(
                    "truediv",
                    {
                        let fun384 = e.get("math")?.attr("acos")?;
                        let mut args382 = Vec::new();
                        let mut kw383 = Vec::new();
                        args382.push({
                            let fun387 = e.get("max")?;
                            let mut args385 = Vec::new();
                            let mut kw386 = Vec::new();
                            args385.push(unary("neg", Val::Float(1.0f64))?);
                            args385.push({
                                let fun390 = e.get("min")?;
                                let mut args388 = Vec::new();
                                let mut kw389 = Vec::new();
                                args388.push(Val::Float(1.0f64));
                                args388.push({
                                    let fun393 = e.get("u")?.attr("dot")?;
                                    let mut args391 = Vec::new();
                                    let mut kw392 = Vec::new();
                                    args391.push(e.get("w")?);
                                    fun393.call(args391, kw392)?
                                });
                                fun390.call(args388, kw389)?
                            });
                            fun387.call(args385, kw386)?
                        });
                        fun384.call(args382, kw383)?
                    },
                    Val::Float(2.0f64),
                )?;
                e.set("half", assigned381.clone())?;
                let assigned394 = binary("truediv", e.get("radius")?.get(e.get("i")?)?, {
                    let fun397 = e.get("math")?.attr("tan")?;
                    let mut args395 = Vec::new();
                    let mut kw396 = Vec::new();
                    args395.push(e.get("half")?);
                    fun397.call(args395, kw396)?
                })?;
                e.set("setback", assigned394.clone())?;
                let assigned398 = binary("add", e.get("v")?.get(e.get("i")?)?, {
                    let fun401 = e.get("u")?.attr("multiply")?;
                    let mut args399 = Vec::new();
                    let mut kw400 = Vec::new();
                    args399.push(e.get("setback")?);
                    fun401.call(args399, kw400)?
                })?;
                e.set("head", assigned398.clone())?;
                if {
                    let v402 = binary("sub", e.get("head")?, e.get("tail")?)?.attr("Length")?;
                    let v403 = Val::Float(1e-07f64);
                    Val::Bool(compare("gt", v402.clone(), v403.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun406 = e.get("legs")?.attr("append")?;
                        let mut args404 = Vec::new();
                        let mut kw405 = Vec::new();
                        args404.push({
                            let mut s = Vec::new();
                            s.push(e.get("tail")?);
                            s.push(e.get("head")?);
                            Val::tuple(s)
                        });
                        fun406.call(args404, kw405)?
                    };
                }
                let assigned407 = binary("add", e.get("v")?.get(e.get("i")?)?, {
                    let fun410 = e.get("w")?.attr("multiply")?;
                    let mut args408 = Vec::new();
                    let mut kw409 = Vec::new();
                    args408.push(e.get("setback")?);
                    fun410.call(args408, kw409)?
                })?;
                e.set("tail", assigned407.clone())?;
            }
            if {
                let v417 = binary(
                    "sub",
                    e.get("v")?.get(unary("neg", Val::Int(1i64))?)?,
                    e.get("tail")?,
                )?
                .attr("Length")?;
                let v418 = Val::Float(1e-07f64);
                Val::Bool(compare("gt", v417.clone(), v418.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun421 = e.get("legs")?.attr("append")?;
                    let mut args419 = Vec::new();
                    let mut kw420 = Vec::new();
                    args419.push({
                        let mut s = Vec::new();
                        s.push(e.get("tail")?);
                        s.push(e.get("v")?.get(unary("neg", Val::Int(1i64))?)?);
                        Val::tuple(s)
                    });
                    fun421.call(args419, kw420)?
                };
            }
            return Ok(e.get("legs")?);
            Ok(Val::None)
        })
    })?;
    // route_wire
    e.set("route_wire", {
        let params = vec![
            ("points".into(), None, false),
            (
                "bend_radius".into(),
                Some(e.get("route_bend_radius")?),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned422 = {
                let fun425 = e.get("corner_radii")?;
                let mut args423 = Vec::new();
                let mut kw424 = Vec::new();
                args423.push(e.get("points")?);
                args423.push(e.get("bend_radius")?);
                fun425.call(args423, kw424)?
            };
            let unpack426 = unpack(assigned422.clone(), 2)?;
            e.set("v", unpack426[0].clone())?;
            e.set("radius", unpack426[1].clone())?;
            let assigned427 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("edges", assigned427.clone())?;
            let assigned428 = e.get("v")?.get(Val::Int(0i64))?;
            e.set("tail", assigned428.clone())?;
            for item429 in {
                let fun503 = e.get("range")?;
                let mut args501 = Vec::new();
                let mut kw502 = Vec::new();
                args501.push(Val::Int(1i64));
                args501.push(binary(
                    "sub",
                    {
                        let fun506 = e.get("len")?;
                        let mut args504 = Vec::new();
                        let mut kw505 = Vec::new();
                        args504.push(e.get("v")?);
                        fun506.call(args504, kw505)?
                    },
                    Val::Int(1i64),
                )?);
                fun503.call(args501, kw502)?
            }
            .iter()?
            {
                e.set("i", item429)?;
                let assigned430 = {
                    let fun433 = binary(
                        "sub",
                        e.get("v")?
                            .get(binary("sub", e.get("i")?, Val::Int(1i64))?)?,
                        e.get("v")?.get(e.get("i")?)?,
                    )?
                    .attr("normalized")?;
                    let mut args431 = Vec::new();
                    let mut kw432 = Vec::new();
                    fun433.call(args431, kw432)?
                };
                e.set("u", assigned430.clone())?;
                let assigned434 = {
                    let fun437 = binary(
                        "sub",
                        e.get("v")?
                            .get(binary("add", e.get("i")?, Val::Int(1i64))?)?,
                        e.get("v")?.get(e.get("i")?)?,
                    )?
                    .attr("normalized")?;
                    let mut args435 = Vec::new();
                    let mut kw436 = Vec::new();
                    fun437.call(args435, kw436)?
                };
                e.set("w", assigned434.clone())?;
                let assigned438 = binary(
                    "truediv",
                    {
                        let fun441 = e.get("math")?.attr("acos")?;
                        let mut args439 = Vec::new();
                        let mut kw440 = Vec::new();
                        args439.push({
                            let fun444 = e.get("max")?;
                            let mut args442 = Vec::new();
                            let mut kw443 = Vec::new();
                            args442.push(unary("neg", Val::Float(1.0f64))?);
                            args442.push({
                                let fun447 = e.get("min")?;
                                let mut args445 = Vec::new();
                                let mut kw446 = Vec::new();
                                args445.push(Val::Float(1.0f64));
                                args445.push({
                                    let fun450 = e.get("u")?.attr("dot")?;
                                    let mut args448 = Vec::new();
                                    let mut kw449 = Vec::new();
                                    args448.push(e.get("w")?);
                                    fun450.call(args448, kw449)?
                                });
                                fun447.call(args445, kw446)?
                            });
                            fun444.call(args442, kw443)?
                        });
                        fun441.call(args439, kw440)?
                    },
                    Val::Float(2.0f64),
                )?;
                e.set("half", assigned438.clone())?;
                let assigned451 = binary("truediv", e.get("radius")?.get(e.get("i")?)?, {
                    let fun454 = e.get("math")?.attr("tan")?;
                    let mut args452 = Vec::new();
                    let mut kw453 = Vec::new();
                    args452.push(e.get("half")?);
                    fun454.call(args452, kw453)?
                })?;
                e.set("setback", assigned451.clone())?;
                let assigned455 = binary("add", e.get("v")?.get(e.get("i")?)?, {
                    let fun458 = e.get("u")?.attr("multiply")?;
                    let mut args456 = Vec::new();
                    let mut kw457 = Vec::new();
                    args456.push(e.get("setback")?);
                    fun458.call(args456, kw457)?
                })?;
                e.set("p_in", assigned455.clone())?;
                let assigned459 = binary("add", e.get("v")?.get(e.get("i")?)?, {
                    let fun462 = e.get("w")?.attr("multiply")?;
                    let mut args460 = Vec::new();
                    let mut kw461 = Vec::new();
                    args460.push(e.get("setback")?);
                    fun462.call(args460, kw461)?
                })?;
                e.set("p_out", assigned459.clone())?;
                let assigned463 = binary("add", e.get("v")?.get(e.get("i")?)?, {
                    let fun466 = {
                        let fun469 = binary(
                            "add",
                            {
                                let fun472 = e.get("u")?.attr("normalized")?;
                                let mut args470 = Vec::new();
                                let mut kw471 = Vec::new();
                                fun472.call(args470, kw471)?
                            },
                            {
                                let fun475 = e.get("w")?.attr("normalized")?;
                                let mut args473 = Vec::new();
                                let mut kw474 = Vec::new();
                                fun475.call(args473, kw474)?
                            },
                        )?
                        .attr("normalized")?;
                        let mut args467 = Vec::new();
                        let mut kw468 = Vec::new();
                        fun469.call(args467, kw468)?
                    }
                    .attr("multiply")?;
                    let mut args464 = Vec::new();
                    let mut kw465 = Vec::new();
                    args464.push(binary("truediv", e.get("radius")?.get(e.get("i")?)?, {
                        let fun478 = e.get("math")?.attr("sin")?;
                        let mut args476 = Vec::new();
                        let mut kw477 = Vec::new();
                        args476.push(e.get("half")?);
                        fun478.call(args476, kw477)?
                    })?);
                    fun466.call(args464, kw465)?
                })?;
                e.set("centre", assigned463.clone())?;
                let assigned479 = binary("add", e.get("centre")?, {
                    let fun482 = {
                        let fun485 =
                            binary("sub", e.get("v")?.get(e.get("i")?)?, e.get("centre")?)?
                                .attr("normalized")?;
                        let mut args483 = Vec::new();
                        let mut kw484 = Vec::new();
                        fun485.call(args483, kw484)?
                    }
                    .attr("multiply")?;
                    let mut args480 = Vec::new();
                    let mut kw481 = Vec::new();
                    args480.push(e.get("radius")?.get(e.get("i")?)?);
                    fun482.call(args480, kw481)?
                })?;
                e.set("mid", assigned479.clone())?;
                if {
                    let v486 = binary("sub", e.get("p_in")?, e.get("tail")?)?.attr("Length")?;
                    let v487 = Val::Float(1e-07f64);
                    Val::Bool(compare("gt", v486.clone(), v487.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun490 = e.get("edges")?.attr("append")?;
                        let mut args488 = Vec::new();
                        let mut kw489 = Vec::new();
                        args488.push({
                            let fun493 = e.get("cq")?.attr("Edge")?.attr("makeLine")?;
                            let mut args491 = Vec::new();
                            let mut kw492 = Vec::new();
                            args491.push(e.get("tail")?);
                            args491.push(e.get("p_in")?);
                            fun493.call(args491, kw492)?
                        });
                        fun490.call(args488, kw489)?
                    };
                }
                {
                    let fun496 = e.get("edges")?.attr("append")?;
                    let mut args494 = Vec::new();
                    let mut kw495 = Vec::new();
                    args494.push({
                        let fun499 = e.get("cq")?.attr("Edge")?.attr("makeThreePointArc")?;
                        let mut args497 = Vec::new();
                        let mut kw498 = Vec::new();
                        args497.push(e.get("p_in")?);
                        args497.push(e.get("mid")?);
                        args497.push(e.get("p_out")?);
                        fun499.call(args497, kw498)?
                    });
                    fun496.call(args494, kw495)?
                };
                let assigned500 = e.get("p_out")?;
                e.set("tail", assigned500.clone())?;
            }
            if {
                let v507 = binary(
                    "sub",
                    e.get("v")?.get(unary("neg", Val::Int(1i64))?)?,
                    e.get("tail")?,
                )?
                .attr("Length")?;
                let v508 = Val::Float(1e-07f64);
                Val::Bool(compare("gt", v507.clone(), v508.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun511 = e.get("edges")?.attr("append")?;
                    let mut args509 = Vec::new();
                    let mut kw510 = Vec::new();
                    args509.push({
                        let fun514 = e.get("cq")?.attr("Edge")?.attr("makeLine")?;
                        let mut args512 = Vec::new();
                        let mut kw513 = Vec::new();
                        args512.push(e.get("tail")?);
                        args512.push(e.get("v")?.get(unary("neg", Val::Int(1i64))?)?);
                        fun514.call(args512, kw513)?
                    });
                    fun511.call(args509, kw510)?
                };
            }
            return Ok({
                let fun517 = e.get("cq")?.attr("Wire")?.attr("assembleEdges")?;
                let mut args515 = Vec::new();
                let mut kw516 = Vec::new();
                args515.push(e.get("edges")?);
                fun517.call(args515, kw516)?
            });
            Ok(Val::None)
        })
    })?;
    // build_route
    e.set("build_route", {
        let params = vec![
            ("points".into(), None, false),
            (
                "bend_radius".into(),
                Some(e.get("route_bend_radius")?),
                false,
            ),
            ("radius".into(), Some(e.get("line_radius")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned518 = {
                let fun521 = e.get("route_wire")?;
                let mut args519 = Vec::new();
                let mut kw520 = Vec::new();
                args519.push(e.get("points")?);
                args519.push(e.get("bend_radius")?);
                fun521.call(args519, kw520)?
            };
            e.set("wire", assigned518.clone())?;
            let assigned522 = {
                let fun525 = e.get("cq")?.attr("Workplane")?;
                let mut args523 = Vec::new();
                let mut kw524 = Vec::new();
                args523.push({
                    let fun528 = e.get("cq")?.attr("Plane")?;
                    let mut args526 = Vec::new();
                    let mut kw527 = Vec::new();
                    kw527.push(("origin".into(), {
                        let fun531 = e.get("wire")?.attr("startPoint")?;
                        let mut args529 = Vec::new();
                        let mut kw530 = Vec::new();
                        fun531.call(args529, kw530)?
                    }));
                    kw527.push(("normal".into(), {
                        let fun534 = e.get("wire")?.attr("tangentAt")?;
                        let mut args532 = Vec::new();
                        let mut kw533 = Vec::new();
                        args532.push(Val::Int(0i64));
                        fun534.call(args532, kw533)?
                    }));
                    fun528.call(args526, kw527)?
                });
                fun525.call(args523, kw524)?
            };
            e.set("profile", assigned522.clone())?;
            return Ok({
                let fun537 = {
                    let fun540 = {
                        let fun543 = e.get("profile")?.attr("circle")?;
                        let mut args541 = Vec::new();
                        let mut kw542 = Vec::new();
                        args541.push(e.get("radius")?);
                        fun543.call(args541, kw542)?
                    }
                    .attr("sweep")?;
                    let mut args538 = Vec::new();
                    let mut kw539 = Vec::new();
                    args538.push({
                        let fun546 = {
                            let fun549 = e.get("cq")?.attr("Workplane")?;
                            let mut args547 = Vec::new();
                            let mut kw548 = Vec::new();
                            args547.push(Val::Str("XY".into()));
                            fun549.call(args547, kw548)?
                        }
                        .attr("newObject")?;
                        let mut args544 = Vec::new();
                        let mut kw545 = Vec::new();
                        args544.push({
                            let mut s = Vec::new();
                            s.push(e.get("wire")?);
                            Val::list(s)
                        });
                        fun546.call(args544, kw545)?
                    });
                    kw539.push(("isFrenet".into(), Val::Bool(true)));
                    fun540.call(args538, kw539)?
                }
                .attr("val")?;
                let mut args535 = Vec::new();
                let mut kw536 = Vec::new();
                fun537.call(args535, kw536)?
            });
            Ok(Val::None)
        })
    })?;
    // route_corridor
    e.set("route_corridor", {
        let params = vec![
            ("name".into(), None, false),
            ("radius".into(), Some(e.get("port_hole_radius")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun552 = e.get("build_route")?;
                let mut args550 = Vec::new();
                let mut kw551 = Vec::new();
                args550.push(e.get("routes")?.get(e.get("name")?)?);
                args550.push(e.get("route_bend_radius")?);
                args550.push(e.get("radius")?);
                fun552.call(args550, kw551)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned553 = binary("mul", Val::Float(0.5f64), e.get("lldpe_tube_od")?)?;
    e.set("bend_floor", assigned553.clone())?;
    let assigned554 = {
        let fun557 = e.get("tuple")?;
        let mut args555 = Vec::new();
        let mut kw556 = Vec::new();
        args555.push({
            let e = e.child();
            let out558 = Val::list(vec![]);
            for item559 in {
                let fun562 = e.get("range")?;
                let mut args560 = Vec::new();
                let mut kw561 = Vec::new();
                args560.push(Val::Int(24i64));
                fun562.call(args560, kw561)?
            }
            .iter()?
            {
                e.set("k", item559)?;
                out558.attr("append")?.call(
                    vec![binary("pow", Val::Float(0.85f64), e.get("k")?)?],
                    vec![],
                )?;
            }
            out558
        });
        fun557.call(args555, kw556)?
    };
    e.set("bend_ladder", assigned554.clone())?;
    let assigned563 = Val::Float(0.1f64);
    e.set("touch_volume", assigned563.clone())?;
    // fit_route
    e.set("fit_route", {
        let params = vec![
            ("points".into(), None, false),
            ("obstacles".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_overlap", rt.import_module("_overlap")?)?;
            for item564 in e.get("bend_ladder")?.iter()? {
                e.set("rung", item564)?;
                let assigned565 = binary("mul", e.get("route_bend_radius")?, e.get("rung")?)?;
                e.set("bend", assigned565.clone())?;
                if {
                    let v566 = e.get("bend")?;
                    let v567 = e.get("bend_floor")?;
                    Val::Bool(compare("lt", v566.clone(), v567.clone())?.truthy()?)
                }
                .truthy()?
                {
                    break;
                }
                let assigned568 = {
                    let fun571 = e.get("build_route")?;
                    let mut args569 = Vec::new();
                    let mut kw570 = Vec::new();
                    args569.push(e.get("points")?);
                    args569.push(e.get("bend")?);
                    fun571.call(args569, kw570)?
                };
                e.set("tube", assigned568.clone())?;
                if {
                    let fun574 = e.get("all")?;
                    let mut args572 = Vec::new();
                    let mut kw573 = Vec::new();
                    args572.push({
                        let e = e.child();
                        let out575 = Val::list(vec![]);
                        for item576 in {
                            let fun579 = e.get("obstacles")?.attr("values")?;
                            let mut args577 = Vec::new();
                            let mut kw578 = Vec::new();
                            fun579.call(args577, kw578)?
                        }
                        .iter()?
                        {
                            e.set("o", item576)?;
                            out575.attr("append")?.call(
                                vec![{
                                    let v583 = {
                                        let fun582 = e.get("_overlap")?.attr("volume")?;
                                        let mut args580 = Vec::new();
                                        let mut kw581 = Vec::new();
                                        args580.push(e.get("tube")?);
                                        args580.push(e.get("o")?);
                                        fun582.call(args580, kw581)?
                                    };
                                    let v584 = e.get("touch_volume")?;
                                    Val::Bool(compare("le", v583.clone(), v584.clone())?.truthy()?)
                                }],
                                vec![],
                            )?;
                        }
                        out575
                    });
                    fun574.call(args572, kw573)?
                }
                .truthy()?
                {
                    return Ok({
                        let mut s = Vec::new();
                        s.push(e.get("bend")?);
                        s.push(e.get("tube")?);
                        Val::tuple(s)
                    });
                }
            }
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("bend_floor")?);
                s.push({
                    let fun587 = e.get("build_route")?;
                    let mut args585 = Vec::new();
                    let mut kw586 = Vec::new();
                    args585.push(e.get("points")?);
                    args585.push(e.get("bend_floor")?);
                    fun587.call(args585, kw586)?
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // build_routes
    e.set("build_routes", {
        let params = vec![("obstacles".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v588 = e.get("obstacles")?;
                let v589 = Val::None;
                Val::Bool(compare("is", v588.clone(), v589.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok({
                    let e = e.child();
                    let out590 = Val::dict(vec![]);
                    for item591 in {
                        let fun594 = e.get("routes")?.attr("items")?;
                        let mut args592 = Vec::new();
                        let mut kw593 = Vec::new();
                        fun594.call(args592, kw593)?
                    }
                    .iter()?
                    {
                        let unpack595 = unpack(item591, 2)?;
                        e.set("n", unpack595[0].clone())?;
                        e.set("p", unpack595[1].clone())?;
                        out590.set(e.get("n")?, {
                            let mut s = Vec::new();
                            s.push(e.get("route_bend_radius")?);
                            s.push({
                                let fun598 = e.get("build_route")?;
                                let mut args596 = Vec::new();
                                let mut kw597 = Vec::new();
                                args596.push(e.get("p")?);
                                fun598.call(args596, kw597)?
                            });
                            Val::tuple(s)
                        })?;
                    }
                    out590
                });
            }
            return Ok({
                let e = e.child();
                let out599 = Val::dict(vec![]);
                for item600 in {
                    let fun603 = e.get("routes")?.attr("items")?;
                    let mut args601 = Vec::new();
                    let mut kw602 = Vec::new();
                    fun603.call(args601, kw602)?
                }
                .iter()?
                {
                    let unpack604 = unpack(item600, 2)?;
                    e.set("n", unpack604[0].clone())?;
                    e.set("p", unpack604[1].clone())?;
                    out599.set(e.get("n")?, {
                        let fun607 = e.get("fit_route")?;
                        let mut args605 = Vec::new();
                        let mut kw606 = Vec::new();
                        args605.push(e.get("p")?);
                        args605.push(e.get("obstacles")?);
                        fun607.call(args605, kw606)?
                    })?;
                }
                out599
            });
            Ok(Val::None)
        })
    })?;
    // carbonator_envelope
    e.set("carbonator_envelope", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned608 = e.get("carbonator_envelope_z_range")?;
            let unpack609 = unpack(assigned608.clone(), 2)?;
            e.set("z0", unpack609[0].clone())?;
            e.set("z1", unpack609[1].clone())?;
            let assigned610 = {
                let fun613 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args611 = Vec::new();
                let mut kw612 = Vec::new();
                args611.push(e.get("carbonator_outer_radius")?);
                args611.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                args611.push({
                    let fun616 = e.get("cq")?.attr("Vector")?;
                    let mut args614 = Vec::new();
                    let mut kw615 = Vec::new();
                    args614.push(Val::Int(0i64));
                    args614.push(Val::Int(0i64));
                    args614.push(e.get("z0")?);
                    fun616.call(args614, kw615)?
                });
                fun613.call(args611, kw612)?
            };
            e.set("tank", assigned610.clone())?;
            let assigned617 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("evap_tail_low_z")?,
                    binary("truediv", e.get("lldpe_tube_od")?, Val::Float(2.0f64))?,
                )?);
                s.push(binary(
                    "add",
                    e.get("evap_tail_high_z")?,
                    binary("truediv", e.get("lldpe_tube_od")?, Val::Float(2.0f64))?,
                )?);
                Val::tuple(s)
            };
            let unpack618 = unpack(assigned617.clone(), 2)?;
            e.set("coil_lo", unpack618[0].clone())?;
            e.set("coil_hi", unpack618[1].clone())?;
            let assigned619 = {
                let fun622 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args620 = Vec::new();
                let mut kw621 = Vec::new();
                args620.push(e.get("carbonator_coil_envelope_radius")?);
                args620.push(binary("sub", e.get("coil_hi")?, e.get("coil_lo")?)?);
                args620.push({
                    let fun625 = e.get("cq")?.attr("Vector")?;
                    let mut args623 = Vec::new();
                    let mut kw624 = Vec::new();
                    args623.push(Val::Int(0i64));
                    args623.push(Val::Int(0i64));
                    args623.push(e.get("coil_lo")?);
                    fun625.call(args623, kw624)?
                });
                fun622.call(args620, kw621)?
            };
            e.set("coil", assigned619.clone())?;
            return Ok({
                let fun628 = {
                    let fun631 = e.get("tank")?.attr("fuse")?;
                    let mut args629 = Vec::new();
                    let mut kw630 = Vec::new();
                    args629.push(e.get("coil")?);
                    fun631.call(args629, kw630)?
                }
                .attr("clean")?;
                let mut args626 = Vec::new();
                let mut kw627 = Vec::new();
                fun628.call(args626, kw627)?
            });
            Ok(Val::None)
        })
    })?;
    // report_routes
    e.set("report_routes", {
        let params = vec![
            ("fitted".into(), None, false),
            ("obstacles".into(), None, false),
            ("measurements".into(), Some(Val::None), true),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v632 = e.get("measurements")?;
                let v633 = Val::None;
                Val::Bool(compare("is", v632.clone(), v633.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("_overlap", rt.import_module("_overlap")?)?;
            } else {
                let assigned634 = {
                    let e = e.child();
                    let out635 = Val::dict(vec![]);
                    for item636 in e
                        .get("measurements")?
                        .get(Val::Str("routes".into()))?
                        .iter()?
                    {
                        e.set("row", item636)?;
                        out635.set(e.get("row")?.get(Val::Str("name".into()))?, e.get("row")?)?;
                    }
                    out635
                };
                e.set("readings", assigned634.clone())?;
            }
            {
                let fun639 = e.get("print")?;
                let mut args637 = Vec::new();
                let mut kw638 = Vec::new();
                args637.push(binary(
                    "mod",
                    Val::Str("  internal routes: %d lines in %s, stock arc %.4g mm — %s".into()),
                    {
                        let mut s = Vec::new();
                        s.push({
                            let fun642 = e.get("len")?;
                            let mut args640 = Vec::new();
                            let mut kw641 = Vec::new();
                            args640.push(e.get("fitted")?);
                            fun642.call(args640, kw641)?
                        });
                        s.push(e.get("route_stock")?.attr("name")?);
                        s.push(e.get("route_bend_radius")?);
                        s.push(e.get("route_stock")?.attr("source")?);
                        Val::tuple(s)
                    },
                )?);
                fun639.call(args637, kw638)?
            };
            let assigned643 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("short", assigned643.clone())?;
            for item644 in {
                let fun716 = e.get("sorted")?;
                let mut args714 = Vec::new();
                let mut kw715 = Vec::new();
                args714.push(e.get("fitted")?);
                fun716.call(args714, kw715)?
            }
            .iter()?
            {
                e.set("name", item644)?;
                let assigned645 = e.get("fitted")?.get(e.get("name")?)?;
                let unpack646 = unpack(assigned645.clone(), 2)?;
                e.set("bend", unpack646[0].clone())?;
                e.set("tube", unpack646[1].clone())?;
                if {
                    let v647 = e.get("measurements")?;
                    let v648 = Val::None;
                    Val::Bool(compare("is", v647.clone(), v648.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned649 = {
                        let fun652 = e.get("corner_radii")?;
                        let mut args650 = Vec::new();
                        let mut kw651 = Vec::new();
                        args650.push(e.get("routes")?.get(e.get("name")?)?);
                        args650.push(e.get("bend")?);
                        fun652.call(args650, kw651)?
                    };
                    let unpack653 = unpack(assigned649.clone(), 2)?;
                    e.set("_v", unpack653[0].clone())?;
                    e.set("radius", unpack653[1].clone())?;
                    let assigned654 = {
                        let fun657 = {
                            let fun660 = e.get("route_wire")?;
                            let mut args658 = Vec::new();
                            let mut kw659 = Vec::new();
                            args658.push(e.get("routes")?.get(e.get("name")?)?);
                            args658.push(e.get("bend")?);
                            fun660.call(args658, kw659)?
                        }
                        .attr("Length")?;
                        let mut args655 = Vec::new();
                        let mut kw656 = Vec::new();
                        fun657.call(args655, kw656)?
                    };
                    e.set("length", assigned654.clone())?;
                } else {
                    let assigned661 = e
                        .get("readings")?
                        .get(e.get("name")?)?
                        .get(Val::Str("radii".into()))?;
                    e.set("radius", assigned661.clone())?;
                    let assigned662 = e
                        .get("readings")?
                        .get(e.get("name")?)?
                        .get(Val::Str("length".into()))?;
                    e.set("length", assigned662.clone())?;
                }
                let assigned663 = {
                    let e = e.child();
                    let out664 = Val::list(vec![]);
                    for item665 in e
                        .get("radius")?
                        .get(Val::Slice {
                            start: Some(Val::Int(1i64).integer()?),
                            stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                            step: 1,
                        })?
                        .iter()?
                    {
                        e.set("r", item665)?;
                        if {
                            let v666 = e.get("r")?;
                            let v667 = Val::Float(0.0f64);
                            Val::Bool(compare("gt", v666.clone(), v667.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out664.attr("append")?.call(vec![e.get("r")?], vec![])?;
                        }
                    }
                    out664
                };
                e.set("corners", assigned663.clone())?;
                let assigned668 = if e.get("corners")?.truthy()? {
                    {
                        let fun671 = e.get("min")?;
                        let mut args669 = Vec::new();
                        let mut kw670 = Vec::new();
                        args669.push(e.get("corners")?);
                        fun671.call(args669, kw670)?
                    }
                } else {
                    {
                        let fun674 = e.get("float")?;
                        let mut args672 = Vec::new();
                        let mut kw673 = Vec::new();
                        args672.push(Val::Str("inf".into()));
                        fun674.call(args672, kw673)?
                    }
                };
                e.set("tightest", assigned668.clone())?;
                let assigned675 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("hits", assigned675.clone())?;
                for item676 in {
                    let fun697 = e.get("obstacles")?.attr("items")?;
                    let mut args695 = Vec::new();
                    let mut kw696 = Vec::new();
                    fun697.call(args695, kw696)?
                }
                .iter()?
                {
                    let unpack698 = unpack(item676, 2)?;
                    e.set("other", unpack698[0].clone())?;
                    e.set("solid", unpack698[1].clone())?;
                    let assigned677 = if {
                        let v678 = e.get("measurements")?;
                        let v679 = Val::None;
                        Val::Bool(compare("is", v678.clone(), v679.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun682 = e.get("_overlap")?.attr("volume")?;
                            let mut args680 = Vec::new();
                            let mut kw681 = Vec::new();
                            args680.push(e.get("tube")?);
                            args680.push(e.get("solid")?);
                            fun682.call(args680, kw681)?
                        }
                    } else {
                        {
                            let fun685 = e.get("next")?;
                            let mut args683 = Vec::new();
                            let mut kw684 = Vec::new();
                            args683.push({
                                let e = e.child();
                                let out686 = Val::list(vec![]);
                                for item687 in e
                                    .get("readings")?
                                    .get(e.get("name")?)?
                                    .get(Val::Str("blocked".into()))?
                                    .iter()?
                                {
                                    e.set("row", item687)?;
                                    if {
                                        let v688 = e.get("row")?.get(Val::Str("name".into()))?;
                                        let v689 = e.get("other")?;
                                        Val::Bool(
                                            compare("eq", v688.clone(), v689.clone())?.truthy()?,
                                        )
                                    }
                                    .truthy()?
                                    {
                                        out686.attr("append")?.call(
                                            vec![e.get("row")?.get(Val::Str("volume".into()))?],
                                            vec![],
                                        )?;
                                    }
                                }
                                out686
                            });
                            fun685.call(args683, kw684)?
                        }
                    };
                    e.set("volume", assigned677.clone())?;
                    if {
                        let v690 = e.get("volume")?;
                        let v691 = e.get("touch_volume")?;
                        Val::Bool(compare("gt", v690.clone(), v691.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun694 = e.get("hits")?.attr("append")?;
                            let mut args692 = Vec::new();
                            let mut kw693 = Vec::new();
                            args692.push(binary("mod", Val::Str("%s by %.2f mm³".into()), {
                                let mut s = Vec::new();
                                s.push(e.get("other")?);
                                s.push(e.get("volume")?);
                                Val::tuple(s)
                            })?);
                            fun694.call(args692, kw693)?
                        };
                    }
                }
                {
                    let fun701 = e.get("print")?;
                    let mut args699 = Vec::new();
                    let mut kw700 = Vec::new();
                    args699.push(binary(
                        "mod",
                        Val::Str(
                            "    %-17s %6.1f mm, %d corners, arc %5.2f mm, tightest %s — %s".into(),
                        ),
                        {
                            let mut s = Vec::new();
                            s.push(e.get("name")?);
                            s.push(e.get("length")?);
                            s.push({
                                let fun704 = e.get("len")?;
                                let mut args702 = Vec::new();
                                let mut kw703 = Vec::new();
                                args702.push(e.get("corners")?);
                                fun704.call(args702, kw703)?
                            });
                            s.push(e.get("bend")?);
                            s.push(if e.get("corners")?.truthy()? {
                                binary("mod", Val::Str("%5.2f mm".into()), e.get("tightest")?)?
                            } else {
                                Val::Str(" none  ".into())
                            });
                            s.push(if unary("not", e.get("hits")?)?.truthy()? {
                                Val::Str("clear".into())
                            } else {
                                binary("add", Val::Str("** ".into()), {
                                    let fun707 = Val::Str("; ".into()).attr("join")?;
                                    let mut args705 = Vec::new();
                                    let mut kw706 = Vec::new();
                                    args705.push(e.get("hits")?);
                                    fun707.call(args705, kw706)?
                                })?
                            });
                            Val::tuple(s)
                        },
                    )?);
                    fun701.call(args699, kw700)?
                };
                if {
                    let v710 = e.get("corners")?;
                    if v710.truthy()? {
                        {
                            let v708 = e.get("tightest")?;
                            let v709 =
                                binary("sub", e.get("route_bend_radius")?, Val::Float(1e-09f64))?;
                            Val::Bool(compare("lt", v708.clone(), v709.clone())?.truthy()?)
                        }
                    } else {
                        v710
                    }
                }
                .truthy()?
                {
                    {
                        let fun713 = e.get("short")?.attr("append")?;
                        let mut args711 = Vec::new();
                        let mut kw712 = Vec::new();
                        args711.push(binary("mod", Val::Str("%s at %.2f mm".into()), {
                            let mut s = Vec::new();
                            s.push(e.get("name")?);
                            s.push(e.get("tightest")?);
                            Val::tuple(s)
                        })?);
                        fun713.call(args711, kw712)?
                    };
                }
            }
            let assigned717 = {
                let fun720 = e.get("sorted")?;
                let mut args718 = Vec::new();
                let mut kw719 = Vec::new();
                args718.push(e.get("fitted")?);
                fun720.call(args718, kw719)?
            };
            e.set("names", assigned717.clone())?;
            let assigned721 = Val::Bool(false);
            e.set("crossed", assigned721.clone())?;
            for item722 in {
                let fun745 = e.get("enumerate")?;
                let mut args743 = Vec::new();
                let mut kw744 = Vec::new();
                args743.push(e.get("names")?);
                fun745.call(args743, kw744)?
            }
            .iter()?
            {
                let unpack746 = unpack(item722, 2)?;
                e.set("i", unpack746[0].clone())?;
                e.set("a", unpack746[1].clone())?;
                for item723 in e
                    .get("names")?
                    .get(Val::Slice {
                        start: Some(binary("add", e.get("i")?, Val::Int(1i64))?.integer()?),
                        stop: None,
                        step: 1,
                    })?
                    .iter()?
                {
                    e.set("b", item723)?;
                    let assigned724 = if {
                        let v725 = e.get("measurements")?;
                        let v726 = Val::None;
                        Val::Bool(compare("is", v725.clone(), v726.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let fun729 = e.get("_overlap")?.attr("volume")?;
                            let mut args727 = Vec::new();
                            let mut kw728 = Vec::new();
                            args727.push(e.get("fitted")?.get(e.get("a")?)?.get(Val::Int(1i64))?);
                            args727.push(e.get("fitted")?.get(e.get("b")?)?.get(Val::Int(1i64))?);
                            fun729.call(args727, kw728)?
                        }
                    } else {
                        {
                            let fun732 = e.get("next")?;
                            let mut args730 = Vec::new();
                            let mut kw731 = Vec::new();
                            args730.push({
                                let e = e.child();
                                let out733 = Val::list(vec![]);
                                for item734 in e
                                    .get("measurements")?
                                    .get(Val::Str("crossings".into()))?
                                    .iter()?
                                {
                                    e.set("row", item734)?;
                                    if {
                                        let v737 = {
                                            let v738 = e.get("row")?.get(Val::Str("a".into()))?;
                                            let v739 = e.get("a")?;
                                            Val::Bool(
                                                compare("eq", v738.clone(), v739.clone())?
                                                    .truthy()?,
                                            )
                                        };
                                        if v737.truthy()? {
                                            {
                                                let v735 =
                                                    e.get("row")?.get(Val::Str("b".into()))?;
                                                let v736 = e.get("b")?;
                                                Val::Bool(
                                                    compare("eq", v735.clone(), v736.clone())?
                                                        .truthy()?,
                                                )
                                            }
                                        } else {
                                            v737
                                        }
                                    }
                                    .truthy()?
                                    {
                                        out733.attr("append")?.call(
                                            vec![e.get("row")?.get(Val::Str("volume".into()))?],
                                            vec![],
                                        )?;
                                    }
                                }
                                out733
                            });
                            fun732.call(args730, kw731)?
                        }
                    };
                    e.set("volume", assigned724.clone())?;
                    if {
                        let v740 = e.get("volume")?;
                        let v741 = e.get("touch_volume")?;
                        Val::Bool(compare("gt", v740.clone(), v741.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        let assigned742 = Val::Bool(true);
                        e.set("crossed", assigned742.clone())?;
                    }
                }
            }
            {
                let fun749 = e.get("print")?;
                let mut args747 = Vec::new();
                let mut kw748 = Vec::new();
                args747.push(if unary("not", e.get("crossed")?)?.truthy()? {
                    Val::Str("    no line meets another".into())
                } else {
                    Val::Str("    ** LINES CROSS **".into())
                });
                fun749.call(args747, kw748)?
            };
            {
                let fun752 = e.get("print")?;
                let mut args750 = Vec::new();
                let mut kw751 = Vec::new();
                args750.push(if unary("not", e.get("short")?)?.truthy()? {
                    Val::Str("    every corner at the stock arc".into())
                } else {
                    binary(
                        "mod",
                        Val::Str("    under the %.4g mm stock arc: %s".into()),
                        {
                            let mut s = Vec::new();
                            s.push(e.get("route_bend_radius")?);
                            s.push({
                                let fun755 = Val::Str("; ".into()).attr("join")?;
                                let mut args753 = Vec::new();
                                let mut kw754 = Vec::new();
                                args753.push(e.get("short")?);
                                fun755.call(args753, kw754)?
                            });
                            Val::tuple(s)
                        },
                    )?
                });
                fun752.call(args750, kw751)?
            };
            Ok(Val::None)
        })
    })?;
    // _route_sub
    e.set("_route_sub", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun758 = e.get("tuple")?;
                let mut args756 = Vec::new();
                let mut kw757 = Vec::new();
                args756.push({
                    let e = e.child();
                    let out759 = Val::list(vec![]);
                    for item760 in {
                        let fun763 = e.get("zip")?;
                        let mut args761 = Vec::new();
                        let mut kw762 = Vec::new();
                        args761.push(e.get("a")?);
                        args761.push(e.get("b")?);
                        fun763.call(args761, kw762)?
                    }
                    .iter()?
                    {
                        let unpack764 = unpack(item760, 2)?;
                        e.set("x", unpack764[0].clone())?;
                        e.set("y", unpack764[1].clone())?;
                        out759
                            .attr("append")?
                            .call(vec![binary("sub", e.get("x")?, e.get("y")?)?], vec![])?;
                    }
                    out759
                });
                fun758.call(args756, kw757)?
            });
            Ok(Val::None)
        })
    })?;
    // _route_add
    e.set("_route_add", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun767 = e.get("tuple")?;
                let mut args765 = Vec::new();
                let mut kw766 = Vec::new();
                args765.push({
                    let e = e.child();
                    let out768 = Val::list(vec![]);
                    for item769 in {
                        let fun772 = e.get("zip")?;
                        let mut args770 = Vec::new();
                        let mut kw771 = Vec::new();
                        args770.push(e.get("a")?);
                        args770.push(e.get("b")?);
                        fun772.call(args770, kw771)?
                    }
                    .iter()?
                    {
                        let unpack773 = unpack(item769, 2)?;
                        e.set("x", unpack773[0].clone())?;
                        e.set("y", unpack773[1].clone())?;
                        out768
                            .attr("append")?
                            .call(vec![binary("add", e.get("x")?, e.get("y")?)?], vec![])?;
                    }
                    out768
                });
                fun767.call(args765, kw766)?
            });
            Ok(Val::None)
        })
    })?;
    // _route_mul
    e.set("_route_mul", {
        let params = vec![("a".into(), None, false), ("scale".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun776 = e.get("tuple")?;
                let mut args774 = Vec::new();
                let mut kw775 = Vec::new();
                args774.push({
                    let e = e.child();
                    let out777 = Val::list(vec![]);
                    for item778 in e.get("a")?.iter()? {
                        e.set("x", item778)?;
                        out777
                            .attr("append")?
                            .call(vec![binary("mul", e.get("x")?, e.get("scale")?)?], vec![])?;
                    }
                    out777
                });
                fun776.call(args774, kw775)?
            });
            Ok(Val::None)
        })
    })?;
    // _route_dot
    e.set("_route_dot", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun781 = e.get("sum")?;
                let mut args779 = Vec::new();
                let mut kw780 = Vec::new();
                args779.push({
                    let e = e.child();
                    let out782 = Val::list(vec![]);
                    for item783 in {
                        let fun786 = e.get("zip")?;
                        let mut args784 = Vec::new();
                        let mut kw785 = Vec::new();
                        args784.push(e.get("a")?);
                        args784.push(e.get("b")?);
                        fun786.call(args784, kw785)?
                    }
                    .iter()?
                    {
                        let unpack787 = unpack(item783, 2)?;
                        e.set("x", unpack787[0].clone())?;
                        e.set("y", unpack787[1].clone())?;
                        out782
                            .attr("append")?
                            .call(vec![binary("mul", e.get("x")?, e.get("y")?)?], vec![])?;
                    }
                    out782
                });
                fun781.call(args779, kw780)?
            });
            Ok(Val::None)
        })
    })?;
    // _route_length
    e.set("_route_length", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun790 = e.get("math")?.attr("sqrt")?;
                let mut args788 = Vec::new();
                let mut kw789 = Vec::new();
                args788.push({
                    let fun793 = e.get("_route_dot")?;
                    let mut args791 = Vec::new();
                    let mut kw792 = Vec::new();
                    args791.push(e.get("a")?);
                    args791.push(e.get("a")?);
                    fun793.call(args791, kw792)?
                });
                fun790.call(args788, kw789)?
            });
            Ok(Val::None)
        })
    })?;
    // _route_unit
    e.set("_route_unit", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun796 = e.get("_route_mul")?;
                let mut args794 = Vec::new();
                let mut kw795 = Vec::new();
                args794.push(e.get("a")?);
                args794.push(binary("truediv", Val::Float(1.0f64), {
                    let fun799 = e.get("_route_length")?;
                    let mut args797 = Vec::new();
                    let mut kw798 = Vec::new();
                    args797.push(e.get("a")?);
                    fun799.call(args797, kw798)?
                })?);
                fun796.call(args794, kw795)?
            });
            Ok(Val::None)
        })
    })?;
    // _route_cross
    e.set("_route_cross", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(1i64))?,
                        e.get("b")?.get(Val::Int(2i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(2i64))?,
                        e.get("b")?.get(Val::Int(1i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(2i64))?,
                        e.get("b")?.get(Val::Int(0i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(0i64))?,
                        e.get("b")?.get(Val::Int(2i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(0i64))?,
                        e.get("b")?.get(Val::Int(1i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(1i64))?,
                        e.get("b")?.get(Val::Int(0i64))?,
                    )?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // route_segments
    e.set("route_segments", {
        let params = vec![
            ("points".into(), None, false),
            (
                "bend_radius".into(),
                Some(e.get("route_bend_radius")?),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned800 = {
                let fun803 = e.get("_corner_data")?;
                let mut args801 = Vec::new();
                let mut kw802 = Vec::new();
                args801.push(e.get("points")?);
                args801.push(e.get("bend_radius")?);
                fun803.call(args801, kw802)?
            };
            let unpack804 = unpack(assigned800.clone(), 2)?;
            e.set("points", unpack804[0].clone())?;
            e.set("radii", unpack804[1].clone())?;
            let assigned805 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("segments", assigned805.clone())?;
            let assigned806 = e.get("points")?.get(Val::Int(0i64))?;
            e.set("tail", assigned806.clone())?;
            // line
            e.set("line", {
                let params = vec![("end".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    {
                        let fun809 = e.get("segments")?.attr("append")?;
                        let mut args807 = Vec::new();
                        let mut kw808 = Vec::new();
                        args807.push({
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("kind".into()), Val::Str("line".into()))?;
                            d.set(Val::Str("start_mm".into()), e.get("tail")?)?;
                            d.set(Val::Str("end_mm".into()), e.get("end")?)?;
                            d.set(Val::Str("length_mm".into()), {
                                let fun812 = e.get("_route_length")?;
                                let mut args810 = Vec::new();
                                let mut kw811 = Vec::new();
                                args810.push({
                                    let fun815 = e.get("_route_sub")?;
                                    let mut args813 = Vec::new();
                                    let mut kw814 = Vec::new();
                                    args813.push(e.get("end")?);
                                    args813.push(e.get("tail")?);
                                    fun815.call(args813, kw814)?
                                });
                                fun812.call(args810, kw811)?
                            })?;
                            d
                        });
                        fun809.call(args807, kw808)?
                    };
                    Ok(Val::None)
                })
            })?;
            for item816 in {
                let fun909 = e.get("range")?;
                let mut args907 = Vec::new();
                let mut kw908 = Vec::new();
                args907.push(Val::Int(1i64));
                args907.push(binary(
                    "sub",
                    {
                        let fun912 = e.get("len")?;
                        let mut args910 = Vec::new();
                        let mut kw911 = Vec::new();
                        args910.push(e.get("points")?);
                        fun912.call(args910, kw911)?
                    },
                    Val::Int(1i64),
                )?);
                fun909.call(args907, kw908)?
            }
            .iter()?
            {
                e.set("i", item816)?;
                let assigned817 = {
                    let fun820 = e.get("_route_unit")?;
                    let mut args818 = Vec::new();
                    let mut kw819 = Vec::new();
                    args818.push({
                        let fun823 = e.get("_route_sub")?;
                        let mut args821 = Vec::new();
                        let mut kw822 = Vec::new();
                        args821.push(e.get("points")?.get(binary(
                            "sub",
                            e.get("i")?,
                            Val::Int(1i64),
                        )?)?);
                        args821.push(e.get("points")?.get(e.get("i")?)?);
                        fun823.call(args821, kw822)?
                    });
                    fun820.call(args818, kw819)?
                };
                e.set("u", assigned817.clone())?;
                let assigned824 = {
                    let fun827 = e.get("_route_unit")?;
                    let mut args825 = Vec::new();
                    let mut kw826 = Vec::new();
                    args825.push({
                        let fun830 = e.get("_route_sub")?;
                        let mut args828 = Vec::new();
                        let mut kw829 = Vec::new();
                        args828.push(e.get("points")?.get(binary(
                            "add",
                            e.get("i")?,
                            Val::Int(1i64),
                        )?)?);
                        args828.push(e.get("points")?.get(e.get("i")?)?);
                        fun830.call(args828, kw829)?
                    });
                    fun827.call(args825, kw826)?
                };
                e.set("w", assigned824.clone())?;
                let assigned831 = binary(
                    "truediv",
                    {
                        let fun834 = e.get("math")?.attr("acos")?;
                        let mut args832 = Vec::new();
                        let mut kw833 = Vec::new();
                        args832.push({
                            let fun837 = e.get("max")?;
                            let mut args835 = Vec::new();
                            let mut kw836 = Vec::new();
                            args835.push(unary("neg", Val::Float(1.0f64))?);
                            args835.push({
                                let fun840 = e.get("min")?;
                                let mut args838 = Vec::new();
                                let mut kw839 = Vec::new();
                                args838.push(Val::Float(1.0f64));
                                args838.push({
                                    let fun843 = e.get("_route_dot")?;
                                    let mut args841 = Vec::new();
                                    let mut kw842 = Vec::new();
                                    args841.push(e.get("u")?);
                                    args841.push(e.get("w")?);
                                    fun843.call(args841, kw842)?
                                });
                                fun840.call(args838, kw839)?
                            });
                            fun837.call(args835, kw836)?
                        });
                        fun834.call(args832, kw833)?
                    },
                    Val::Float(2.0f64),
                )?;
                e.set("half", assigned831.clone())?;
                let assigned844 = binary("truediv", e.get("radii")?.get(e.get("i")?)?, {
                    let fun847 = e.get("math")?.attr("tan")?;
                    let mut args845 = Vec::new();
                    let mut kw846 = Vec::new();
                    args845.push(e.get("half")?);
                    fun847.call(args845, kw846)?
                })?;
                e.set("setback", assigned844.clone())?;
                let assigned848 = {
                    let fun851 = e.get("_route_add")?;
                    let mut args849 = Vec::new();
                    let mut kw850 = Vec::new();
                    args849.push(e.get("points")?.get(e.get("i")?)?);
                    args849.push({
                        let fun854 = e.get("_route_mul")?;
                        let mut args852 = Vec::new();
                        let mut kw853 = Vec::new();
                        args852.push(e.get("u")?);
                        args852.push(e.get("setback")?);
                        fun854.call(args852, kw853)?
                    });
                    fun851.call(args849, kw850)?
                };
                e.set("incoming", assigned848.clone())?;
                let assigned855 = {
                    let fun858 = e.get("_route_add")?;
                    let mut args856 = Vec::new();
                    let mut kw857 = Vec::new();
                    args856.push(e.get("points")?.get(e.get("i")?)?);
                    args856.push({
                        let fun861 = e.get("_route_mul")?;
                        let mut args859 = Vec::new();
                        let mut kw860 = Vec::new();
                        args859.push(e.get("w")?);
                        args859.push(e.get("setback")?);
                        fun861.call(args859, kw860)?
                    });
                    fun858.call(args856, kw857)?
                };
                e.set("outgoing", assigned855.clone())?;
                let assigned862 = {
                    let fun865 = e.get("_route_add")?;
                    let mut args863 = Vec::new();
                    let mut kw864 = Vec::new();
                    args863.push(e.get("points")?.get(e.get("i")?)?);
                    args863.push({
                        let fun868 = e.get("_route_mul")?;
                        let mut args866 = Vec::new();
                        let mut kw867 = Vec::new();
                        args866.push({
                            let fun871 = e.get("_route_unit")?;
                            let mut args869 = Vec::new();
                            let mut kw870 = Vec::new();
                            args869.push({
                                let fun874 = e.get("_route_add")?;
                                let mut args872 = Vec::new();
                                let mut kw873 = Vec::new();
                                args872.push(e.get("u")?);
                                args872.push(e.get("w")?);
                                fun874.call(args872, kw873)?
                            });
                            fun871.call(args869, kw870)?
                        });
                        args866.push(binary("truediv", e.get("radii")?.get(e.get("i")?)?, {
                            let fun877 = e.get("math")?.attr("sin")?;
                            let mut args875 = Vec::new();
                            let mut kw876 = Vec::new();
                            args875.push(e.get("half")?);
                            fun877.call(args875, kw876)?
                        })?);
                        fun868.call(args866, kw867)?
                    });
                    fun865.call(args863, kw864)?
                };
                e.set("centre", assigned862.clone())?;
                let assigned878 = {
                    let fun881 = e.get("_route_add")?;
                    let mut args879 = Vec::new();
                    let mut kw880 = Vec::new();
                    args879.push(e.get("centre")?);
                    args879.push({
                        let fun884 = e.get("_route_mul")?;
                        let mut args882 = Vec::new();
                        let mut kw883 = Vec::new();
                        args882.push({
                            let fun887 = e.get("_route_unit")?;
                            let mut args885 = Vec::new();
                            let mut kw886 = Vec::new();
                            args885.push({
                                let fun890 = e.get("_route_sub")?;
                                let mut args888 = Vec::new();
                                let mut kw889 = Vec::new();
                                args888.push(e.get("points")?.get(e.get("i")?)?);
                                args888.push(e.get("centre")?);
                                fun890.call(args888, kw889)?
                            });
                            fun887.call(args885, kw886)?
                        });
                        args882.push(e.get("radii")?.get(e.get("i")?)?);
                        fun884.call(args882, kw883)?
                    });
                    fun881.call(args879, kw880)?
                };
                e.set("mid", assigned878.clone())?;
                if {
                    let v897 = {
                        let fun893 = e.get("_route_length")?;
                        let mut args891 = Vec::new();
                        let mut kw892 = Vec::new();
                        args891.push({
                            let fun896 = e.get("_route_sub")?;
                            let mut args894 = Vec::new();
                            let mut kw895 = Vec::new();
                            args894.push(e.get("incoming")?);
                            args894.push(e.get("tail")?);
                            fun896.call(args894, kw895)?
                        });
                        fun893.call(args891, kw892)?
                    };
                    let v898 = Val::Float(1e-07f64);
                    Val::Bool(compare("gt", v897.clone(), v898.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun901 = e.get("line")?;
                        let mut args899 = Vec::new();
                        let mut kw900 = Vec::new();
                        args899.push(e.get("incoming")?);
                        fun901.call(args899, kw900)?
                    };
                }
                let assigned902 = binary(
                    "sub",
                    e.get("math")?.attr("pi")?,
                    binary("mul", Val::Float(2.0f64), e.get("half")?)?,
                )?;
                e.set("angle", assigned902.clone())?;
                {
                    let fun905 = e.get("segments")?.attr("append")?;
                    let mut args903 = Vec::new();
                    let mut kw904 = Vec::new();
                    args903.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("kind".into()), Val::Str("arc".into()))?;
                        d.set(Val::Str("start_mm".into()), e.get("incoming")?)?;
                        d.set(Val::Str("end_mm".into()), e.get("outgoing")?)?;
                        d.set(Val::Str("midpoint_mm".into()), e.get("mid")?)?;
                        d.set(
                            Val::Str("radius_mm".into()),
                            e.get("radii")?.get(e.get("i")?)?,
                        )?;
                        d.set(Val::Str("angle_radians".into()), e.get("angle")?)?;
                        d.set(
                            Val::Str("length_mm".into()),
                            binary("mul", e.get("radii")?.get(e.get("i")?)?, e.get("angle")?)?,
                        )?;
                        d
                    });
                    fun905.call(args903, kw904)?
                };
                let assigned906 = e.get("outgoing")?;
                e.set("tail", assigned906.clone())?;
            }
            if {
                let v919 = {
                    let fun915 = e.get("_route_length")?;
                    let mut args913 = Vec::new();
                    let mut kw914 = Vec::new();
                    args913.push({
                        let fun918 = e.get("_route_sub")?;
                        let mut args916 = Vec::new();
                        let mut kw917 = Vec::new();
                        args916.push(e.get("points")?.get(unary("neg", Val::Int(1i64))?)?);
                        args916.push(e.get("tail")?);
                        fun918.call(args916, kw917)?
                    });
                    fun915.call(args913, kw914)?
                };
                let v920 = Val::Float(1e-07f64);
                Val::Bool(compare("gt", v919.clone(), v920.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun923 = e.get("line")?;
                    let mut args921 = Vec::new();
                    let mut kw922 = Vec::new();
                    args921.push(e.get("points")?.get(unary("neg", Val::Int(1i64))?)?);
                    fun923.call(args921, kw922)?
                };
            }
            return Ok(e.get("segments")?);
            Ok(Val::None)
        })
    })?;
    // _drop_collinear
    e.set("_drop_collinear", {
        let params = vec![("points".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let e = e.child();
                let out924 = Val::list(vec![]);
                for item925 in {
                    let fun928 = e.get("_route_points")?;
                    let mut args926 = Vec::new();
                    let mut kw927 = Vec::new();
                    args926.push(e.get("points")?);
                    fun928.call(args926, kw927)?
                }
                .iter()?
                {
                    e.set("point", item925)?;
                    out924.attr("append")?.call(
                        vec![{
                            let fun931 = e.get("cq")?.attr("Vector")?;
                            let mut args929 = Vec::new();
                            let mut kw930 = Vec::new();
                            args929.extend(e.get("point")?.iter()?);
                            fun931.call(args929, kw930)?
                        }],
                        vec![],
                    )?;
                }
                out924
            });
            Ok(Val::None)
        })
    })?;
    // corner_radii
    e.set("corner_radii", {
        let params = vec![
            ("points".into(), None, false),
            ("bend_radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned932 = {
                let fun935 = e.get("_corner_data")?;
                let mut args933 = Vec::new();
                let mut kw934 = Vec::new();
                args933.push(e.get("points")?);
                args933.push(e.get("bend_radius")?);
                fun935.call(args933, kw934)?
            };
            let unpack936 = unpack(assigned932.clone(), 2)?;
            e.set("points", unpack936[0].clone())?;
            e.set("radii", unpack936[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let e = e.child();
                    let out937 = Val::list(vec![]);
                    for item938 in e.get("points")?.iter()? {
                        e.set("point", item938)?;
                        out937.attr("append")?.call(
                            vec![{
                                let fun941 = e.get("cq")?.attr("Vector")?;
                                let mut args939 = Vec::new();
                                let mut kw940 = Vec::new();
                                args939.extend(e.get("point")?.iter()?);
                                fun941.call(args939, kw940)?
                            }],
                            vec![],
                        )?;
                    }
                    out937
                });
                s.push(e.get("radii")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
