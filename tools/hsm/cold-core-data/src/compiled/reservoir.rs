#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
    }
    .attr("parent")?;
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
            args12.push(binary(
                "truediv",
                {
                    let fun17 = e.get("next")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    args15.push({
                        let e = e.child();
                        let out18 = Val::list(vec![]);
                        for item19 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item19)?;
                            if {
                                let v20 = e.get("p")?.attr("name")?;
                                let v21 = Val::Str("printed-parts".into());
                                Val::Bool(compare("eq", v20.clone(), v21.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out18.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out18
                    });
                    fun17.call(args15, kw16)?
                },
                Val::Str("cadlib".into()),
            )?);
            fun14.call(args12, kw13)?
        });
        fun11.call(args9, kw10)?
    };
    {
        let fun24 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args22 = Vec::new();
        let mut kw23 = Vec::new();
        args22.push(Val::Int(0i64));
        args22.push({
            let fun27 = e.get("str")?;
            let mut args25 = Vec::new();
            let mut kw26 = Vec::new();
            args25.push(binary(
                "truediv",
                {
                    let fun30 = e.get("next")?;
                    let mut args28 = Vec::new();
                    let mut kw29 = Vec::new();
                    args28.push({
                        let e = e.child();
                        let out31 = Val::list(vec![]);
                        for item32 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item32)?;
                            if {
                                let v33 = e.get("p")?.attr("name")?;
                                let v34 = Val::Str("hardware".into());
                                Val::Bool(compare("eq", v33.clone(), v34.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out31.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out31
                    });
                    fun30.call(args28, kw29)?
                },
                Val::Str("scripts".into()),
            )?);
            fun27.call(args25, kw26)?
        });
        fun24.call(args22, kw23)?
    };
    {
        let fun37 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args35 = Vec::new();
        let mut kw36 = Vec::new();
        args35.push(Val::Int(0i64));
        args35.push({
            let fun40 = e.get("str")?;
            let mut args38 = Vec::new();
            let mut kw39 = Vec::new();
            args38.push(e.get("_here")?.attr("parent")?);
            fun40.call(args38, kw39)?
        });
        fun37.call(args35, kw36)?
    };
    {
        let fun43 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args41 = Vec::new();
        let mut kw42 = Vec::new();
        args41.push(Val::Int(0i64));
        args41.push({
            let fun46 = e.get("str")?;
            let mut args44 = Vec::new();
            let mut kw45 = Vec::new();
            args44.push(binary(
                "truediv",
                {
                    let fun49 = e.get("next")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    args47.push({
                        let e = e.child();
                        let out50 = Val::list(vec![]);
                        for item51 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item51)?;
                            if {
                                let fun54 = binary(
                                    "truediv",
                                    binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                    Val::Str("docgen".into()),
                                )?
                                .attr("is_dir")?;
                                let mut args52 = Vec::new();
                                let mut kw53 = Vec::new();
                                fun54.call(args52, kw53)?
                            }
                            .truthy()?
                            {
                                out50.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out50
                    });
                    fun49.call(args47, kw48)?
                },
                Val::Str("tools".into()),
            )?);
            fun46.call(args44, kw45)?
        });
        fun43.call(args41, kw42)?
    };
    e.set("_mat", rt.import_module("_materials")?)?;
    e.set("fits", rt.import_module("fits")?)?;
    e.set("tube_ports", rt.import_module("_reservoir_ports")?)?;
    let mod55 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    e.set(
        "substitute_py_comments",
        rt.member("docgen", "substitute_py_comments")?,
    )?;
    let mod56 = rt.import_module("_cold_core_interface")?;
    e.set(
        "cap_conduit_shell_xy",
        rt.member("_cold_core_interface", "cap_conduit_shell_xy")?,
    )?;
    e.set(
        "bag_pocket_far_inner_x",
        rt.member("_cold_core_interface", "bag_pocket_far_inner_x")?,
    )?;
    e.set(
        "bag_pocket_y_inner_max",
        rt.member("_cold_core_interface", "bag_pocket_y_inner_max")?,
    )?;
    e.set(
        "bag_pocket_floor_top_z",
        rt.member("_cold_core_interface", "bag_pocket_floor_top_z")?,
    )?;
    e.set(
        "bag_pocket_walls_top_z",
        rt.member("_cold_core_interface", "bag_pocket_walls_top_z")?,
    )?;
    e.set(
        "pocket_centerward_arc_outer_radius",
        rt.member("_cold_core_interface", "pocket_centerward_arc_outer_radius")?,
    )?;
    e.set(
        "port_hole_radius",
        rt.member("_cold_core_interface", "port_hole_radius")?,
    )?;
    e.set(
        "reservoir_clearance",
        rt.member("_cold_core_interface", "reservoir_clearance")?,
    )?;
    e.set(
        "reservoir_floor_thickness",
        rt.member("_cold_core_interface", "reservoir_floor_thickness")?,
    )?;
    e.set(
        "reservoir_draw_port",
        rt.member("_cold_core_interface", "reservoir_draw_port")?,
    )?;
    e.set(
        "reservoir_fill_port",
        rt.member("_cold_core_interface", "reservoir_fill_port")?,
    )?;
    e.set(
        "reservoir_fill_sides",
        rt.member("_cold_core_interface", "reservoir_fill_sides")?,
    )?;
    e.set(
        "level_rod_y",
        rt.member("_cold_core_interface", "level_rod_y")?,
    )?;
    e.set(
        "lldpe_tube_od",
        rt.member("_cold_core_interface", "lldpe_tube_od")?,
    )?;
    let mod57 = rt.import_module("_reed_channels")?;
    e.set(
        "reeds_per_reservoir",
        rt.member("_reed_channels", "reeds_per_reservoir")?,
    )?;
    e.set("_float", rt.import_module("_float_interface")?)?;
    let assigned58 = e.get("reservoir_floor_thickness")?;
    e.set("reservoir_wall_thickness", assigned58.clone())?;
    let assigned59 = Val::Float(6.0f64);
    e.set("outer_corner_fillet_radius", assigned59.clone())?;
    let assigned60 = Val::Float(6.0f64);
    e.set("inner_corner_fillet_radius", assigned60.clone())?;
    let assigned61 = e.get("tube_ports")?.attr("plate_thickness")?;
    e.set("cap_base_thickness", assigned61.clone())?;
    let assigned62 = Val::Float(5.0f64);
    e.set("cap_wall_height", assigned62.clone())?;
    let assigned63 = Val::Float(6.0f64);
    e.set("cap_wall_width", assigned63.clone())?;
    let assigned64 = binary(
        "add",
        Val::Float(5.5f64),
        binary("mul", Val::Float(2.0f64), e.get("fits")?.attr("slip")?)?,
    )?;
    e.set("cap_counterbore_diameter", assigned64.clone())?;
    let assigned65 = binary(
        "add",
        e.get("cap_base_thickness")?,
        e.get("fits")?.attr("supported_surface")?,
    )?;
    e.set("cap_counterbore_depth", assigned65.clone())?;
    let assigned66 = binary(
        "add",
        Val::Float(3.0f64),
        binary("mul", Val::Float(2.0f64), e.get("fits")?.attr("slip")?)?,
    )?;
    e.set("cap_clearance_hole_diameter", assigned66.clone())?;
    let assigned67 = Val::Float(2.0f64);
    e.set("gasket_thickness", assigned67.clone())?;
    let assigned68 = Val::Float(5.0f64);
    e.set("gasket_strip_width", assigned68.clone())?;
    let assigned69 = {
        let mut s = Vec::new();
        s.push(Val::Int(0i64));
        s.push(e.get("cap_wall_height")?);
        Val::tuple(s)
    };
    e.set("cap_perimeter_z_range", assigned69.clone())?;
    let assigned70 = {
        let mut s = Vec::new();
        s.push(e.get("cap_wall_height")?);
        s.push(binary(
            "add",
            e.get("cap_wall_height")?,
            e.get("cap_base_thickness")?,
        )?);
        Val::tuple(s)
    };
    e.set("cap_base_z_range", assigned70.clone())?;
    let assigned71 = e.get("cap_base_z_range")?.get(Val::Int(1i64))?;
    e.set("cap_total_height", assigned71.clone())?;
    let assigned72 = e.get("reservoir_fill_port")?;
    e.set("fill_position", assigned72.clone())?;
    let assigned73 = e.get("reservoir_draw_port")?;
    e.set("draw_position", assigned73.clone())?;
    let assigned74 = e.get("tube_ports")?.attr("air_position")?;
    e.set("vent_position", assigned74.clone())?;
    let assigned75 = e
        .get("tube_ports")?
        .attr("liquid_grip")?
        .get(Val::Str("waist_d".into()))?;
    e.set("fill_bore_diameter", assigned75.clone())?;
    let assigned76 = {
        let fun79 = e.get("len")?;
        let mut args77 = Vec::new();
        let mut kw78 = Vec::new();
        args77.push(e.get("fill_position")?);
        fun79.call(args77, kw78)?
    };
    e.set("reservoir_count", assigned76.clone())?;
    let assigned80 = e.get("level_rod_y")?;
    e.set("rod_position_y", assigned80.clone())?;
    let assigned81 = e.get("_float")?.attr("guide_diameter")?;
    e.set("rod_diameter", assigned81.clone())?;
    let assigned82 = binary(
        "add",
        e.get("rod_diameter")?,
        binary("mul", Val::Float(2.0f64), e.get("fits")?.attr("slip")?)?,
    )?;
    e.set("rod_bore", assigned82.clone())?;
    let assigned83 = binary("add", e.get("rod_bore")?, Val::Float(4.0f64))?;
    e.set("rod_boss_od", assigned83.clone())?;
    let assigned84 = Val::Float(2.0f64);
    e.set("rod_register_boss_height", assigned84.clone())?;
    let assigned85 = Val::Float(6.0f64);
    e.set("rod_anchor_boss_height", assigned85.clone())?;
    let assigned86 = Val::Float(0.0f64);
    e.set("rod_anchor_boss_floor", assigned86.clone())?;
    let assigned87 = Val::Float(2.0f64);
    e.set("insert_pocket_radius", assigned87.clone())?;
    let assigned88 = Val::Float(7.0f64);
    e.set("insert_pocket_depth", assigned88.clone())?;
    let assigned89 = Val::Float(3.0f64);
    e.set("boss_annulus", assigned89.clone())?;
    let assigned90 = binary(
        "add",
        e.get("insert_pocket_radius")?,
        e.get("boss_annulus")?,
    )?;
    e.set("body_boss_radius", assigned90.clone())?;
    let assigned91 = e.get("body_boss_radius")?;
    e.set("cap_boss_radius", assigned91.clone())?;
    let assigned92 = e.get("body_boss_radius")?;
    e.set("gasket_pad_radius", assigned92.clone())?;
    let assigned93 = Val::Float(15.0f64);
    e.set("boss_height", assigned93.clone())?;
    let assigned94 = Val::Float(5.0f64);
    e.set("_cyl_extra_below_bottom", assigned94.clone())?;
    let assigned95 = binary(
        "sub",
        e.get("bag_pocket_far_inner_x")?,
        e.get("reservoir_clearance")?,
    )?;
    e.set("outer_far_x_abs", assigned95.clone())?;
    let assigned96 = binary(
        "sub",
        e.get("bag_pocket_y_inner_max")?,
        e.get("reservoir_clearance")?,
    )?;
    e.set("outer_y_max", assigned96.clone())?;
    let assigned97 = binary(
        "add",
        e.get("pocket_centerward_arc_outer_radius")?,
        e.get("reservoir_clearance")?,
    )?;
    e.set("outer_centerward_radius", assigned97.clone())?;
    let assigned98 = binary(
        "sub",
        e.get("outer_far_x_abs")?,
        e.get("reservoir_wall_thickness")?,
    )?;
    e.set("inner_far_x_abs", assigned98.clone())?;
    let assigned99 = binary(
        "sub",
        e.get("outer_y_max")?,
        e.get("reservoir_wall_thickness")?,
    )?;
    e.set("inner_y_max", assigned99.clone())?;
    let assigned100 = binary(
        "add",
        e.get("outer_centerward_radius")?,
        e.get("reservoir_wall_thickness")?,
    )?;
    e.set("inner_centerward_radius", assigned100.clone())?;
    let assigned101 = e.get("_float")?.attr("diameter")?;
    e.set("float_capsule_od", assigned101.clone())?;
    let assigned102 = e.get("_float")?.attr("bore_diameter")?;
    e.set("float_capsule_bore", assigned102.clone())?;
    let assigned103 = binary(
        "sub",
        e.get("inner_far_x_abs")?,
        e.get("_float")?.attr("rod_axis_from_inner_wall")?,
    )?;
    e.set("rod_position_x", assigned103.clone())?;
    let assigned104 = {
        let fun107 = e.get("math")?.attr("degrees")?;
        let mut args105 = Vec::new();
        let mut kw106 = Vec::new();
        args105.push({
            let fun110 = e.get("math")?.attr("acos")?;
            let mut args108 = Vec::new();
            let mut kw109 = Vec::new();
            args108.push(binary(
                "truediv",
                e.get("outer_y_max")?,
                e.get("outer_centerward_radius")?,
            )?);
            fun110.call(args108, kw109)?
        });
        fun107.call(args105, kw106)?
    };
    e.set("outer_tab_interior_angle", assigned104.clone())?;
    let assigned111 = {
        let fun114 = e.get("math")?.attr("degrees")?;
        let mut args112 = Vec::new();
        let mut kw113 = Vec::new();
        args112.push({
            let fun117 = e.get("math")?.attr("acos")?;
            let mut args115 = Vec::new();
            let mut kw116 = Vec::new();
            args115.push(binary(
                "truediv",
                e.get("inner_y_max")?,
                e.get("inner_centerward_radius")?,
            )?);
            fun117.call(args115, kw116)?
        });
        fun114.call(args112, kw113)?
    };
    e.set("inner_corner_interior_angle", assigned111.clone())?;
    let assigned118 = binary(
        "add",
        binary("add", e.get("gasket_thickness")?, e.get("cap_wall_height")?)?,
        e.get("cap_base_thickness")?,
    )?;
    e.set("cap_stack_above_body", assigned118.clone())?;
    let assigned119 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            e.get("bag_pocket_floor_top_z")?,
            e.get("reservoir_clearance")?,
        )?);
        s.push(binary(
            "sub",
            binary(
                "sub",
                e.get("bag_pocket_walls_top_z")?,
                e.get("reservoir_clearance")?,
            )?,
            e.get("cap_stack_above_body")?,
        )?);
        Val::tuple(s)
    };
    e.set("outer_z_range", assigned119.clone())?;
    let assigned120 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            e.get("outer_z_range")?.get(Val::Int(0i64))?,
            e.get("reservoir_wall_thickness")?,
        )?);
        s.push(e.get("outer_z_range")?.get(Val::Int(1i64))?);
        Val::tuple(s)
    };
    e.set("inner_z_range", assigned120.clone())?;
    let assigned121 = binary(
        "add",
        e.get("outer_z_range")?.get(Val::Int(1i64))?,
        e.get("gasket_thickness")?,
    )?;
    e.set("cap_assembly_lift", assigned121.clone())?;
    let assigned122 = binary(
        "add",
        e.get("cap_assembly_lift")?,
        e.get("cap_total_height")?,
    )?;
    e.set("cap_top_z", assigned122.clone())?;
    let assigned123 = e.get("inner_z_range")?.get(Val::Int(0i64))?;
    e.set("rod_floor_z", assigned123.clone())?;
    let assigned124 = e.get("fits")?.attr("slip")?;
    e.set("reservoir_rod_clearance", assigned124.clone())?;
    let assigned125 = binary(
        "sub",
        binary(
            "sub",
            binary(
                "add",
                e.get("cap_assembly_lift")?,
                e.get("cap_wall_height")?,
            )?,
            binary(
                "add",
                e.get("rod_floor_z")?,
                e.get("rod_anchor_boss_floor")?,
            )?,
        )?,
        e.get("reservoir_rod_clearance")?,
    )?;
    e.set("reservoir_rod_len", assigned125.clone())?;
    let assigned126 = {
        let mut s = Vec::new();
        s.push(binary(
            "add",
            binary(
                "add",
                e.get("rod_floor_z")?,
                e.get("rod_anchor_boss_height")?,
            )?,
            e.get("_float")?.attr("magnet_midplane")?,
        )?);
        s.push(binary(
            "sub",
            binary(
                "sub",
                e.get("cap_assembly_lift")?,
                e.get("rod_register_boss_height")?,
            )?,
            binary(
                "sub",
                e.get("_float")?.attr("height")?,
                e.get("_float")?.attr("magnet_midplane")?,
            )?,
        )?);
        Val::tuple(s)
    };
    e.set("float_magnet_travel_z", assigned126.clone())?;
    let assigned127 = binary(
        "sub",
        e.get("float_magnet_travel_z")?.get(Val::Int(1i64))?,
        e.get("float_magnet_travel_z")?.get(Val::Int(0i64))?,
    )?;
    e.set("_float_travel", assigned127.clone())?;
    let assigned128 = {
        let fun131 = e.get("float")?;
        let mut args129 = Vec::new();
        let mut kw130 = Vec::new();
        args129.push({
            let fun134 = e.get("math")?.attr("floor")?;
            let mut args132 = Vec::new();
            let mut kw133 = Vec::new();
            args132.push(binary(
                "truediv",
                e.get("_float_travel")?,
                binary("sub", e.get("reeds_per_reservoir")?, Val::Int(1i64))?,
            )?);
            fun134.call(args132, kw133)?
        });
        fun131.call(args129, kw130)?
    };
    e.set("reservoir_reed_pitch", assigned128.clone())?;
    let assigned135 = binary(
        "mul",
        binary("sub", e.get("reeds_per_reservoir")?, Val::Int(1i64))?,
        e.get("reservoir_reed_pitch")?,
    )?;
    e.set("_reed_span", assigned135.clone())?;
    let assigned136 = binary(
        "truediv",
        {
            let fun139 = e.get("sum")?;
            let mut args137 = Vec::new();
            let mut kw138 = Vec::new();
            args137.push(e.get("float_magnet_travel_z")?);
            fun139.call(args137, kw138)?
        },
        Val::Int(2i64),
    )?;
    e.set("_reed_mid", assigned136.clone())?;
    let assigned140 = {
        let fun143 = e.get("tuple")?;
        let mut args141 = Vec::new();
        let mut kw142 = Vec::new();
        args141.push({
            let e = e.child();
            let out144 = Val::list(vec![]);
            for item145 in {
                let fun148 = e.get("range")?;
                let mut args146 = Vec::new();
                let mut kw147 = Vec::new();
                args146.push(e.get("reeds_per_reservoir")?);
                fun148.call(args146, kw147)?
            }
            .iter()?
            {
                e.set("i", item145)?;
                out144.attr("append")?.call(
                    vec![binary(
                        "add",
                        binary(
                            "sub",
                            e.get("_reed_mid")?,
                            binary("truediv", e.get("_reed_span")?, Val::Int(2i64))?,
                        )?,
                        binary("mul", e.get("i")?, e.get("reservoir_reed_pitch")?)?,
                    )?],
                    vec![],
                )?;
            }
            out144
        });
        fun143.call(args141, kw142)?
    };
    e.set("reservoir_reed_centres_z", assigned140.clone())?;
    if !{
        let v149 = e.get("_reed_span")?;
        let v150 = e.get("_float_travel")?;
        Val::Bool(compare("lt", v149.clone(), v150.clone())?.truthy()?)
    }
    .truthy()?
    {
        anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
    }
    let assigned151 = binary(
        "add",
        e.get("rod_floor_z")?,
        binary("truediv", e.get("lldpe_tube_od")?, Val::Int(2i64))?,
    )?;
    e.set("dip_tube_mouth_z", assigned151.clone())?;
    let assigned152 = {
        let fun155 = e.get("math")?.attr("sqrt")?;
        let mut args153 = Vec::new();
        let mut kw154 = Vec::new();
        args153.push(binary(
            "sub",
            binary("pow", e.get("outer_centerward_radius")?, Val::Int(2i64))?,
            binary("pow", e.get("outer_y_max")?, Val::Int(2i64))?,
        )?);
        fun155.call(args153, kw154)?
    };
    e.set("outer_corner_x", assigned152.clone())?;
    let assigned156 = {
        let fun159 = e.get("math")?.attr("sqrt")?;
        let mut args157 = Vec::new();
        let mut kw158 = Vec::new();
        args157.push(binary(
            "sub",
            binary("pow", e.get("inner_centerward_radius")?, Val::Int(2i64))?,
            binary("pow", e.get("inner_y_max")?, Val::Int(2i64))?,
        )?);
        fun159.call(args157, kw158)?
    };
    e.set("inner_corner_x", assigned156.clone())?;
    let assigned160 = e.get("outer_corner_fillet_radius")?;
    e.set("_screw_setback", assigned160.clone())?;
    let assigned161 = binary("sub", e.get("outer_far_x_abs")?, e.get("_screw_setback")?)?;
    e.set("_corner_xy_x", assigned161.clone())?;
    let assigned162 = binary("sub", e.get("outer_y_max")?, e.get("_screw_setback")?)?;
    e.set("_corner_xy_y", assigned162.clone())?;
    let assigned163 = binary("sub", e.get("outer_far_x_abs")?, e.get("_screw_setback")?)?;
    e.set("_far_mid_x", assigned163.clone())?;
    let assigned164 = binary(
        "add",
        e.get("outer_centerward_radius")?,
        e.get("_screw_setback")?,
    )?;
    e.set("_curve_apex_x", assigned164.clone())?;
    let assigned165 = binary(
        "sub",
        e.get("outer_y_max")?,
        e.get("outer_corner_fillet_radius")?,
    )?;
    e.set("_corner_curve_y", assigned165.clone())?;
    let assigned166 = binary(
        "add",
        e.get("outer_centerward_radius")?,
        e.get("outer_corner_fillet_radius")?,
    )?;
    e.set("_corner_curve_r", assigned166.clone())?;
    let assigned167 = {
        let fun170 = e.get("math")?.attr("sqrt")?;
        let mut args168 = Vec::new();
        let mut kw169 = Vec::new();
        args168.push(binary(
            "sub",
            binary("pow", e.get("_corner_curve_r")?, Val::Int(2i64))?,
            binary("pow", e.get("_corner_curve_y")?, Val::Int(2i64))?,
        )?);
        fun170.call(args168, kw169)?
    };
    e.set("_corner_curve_x", assigned167.clone())?;
    let assigned171 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(e.get("_corner_xy_x")?);
            s.push(e.get("_corner_xy_y")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(e.get("_corner_xy_x")?);
            s.push(unary("neg", e.get("_corner_xy_y")?)?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(e.get("_far_mid_x")?);
            s.push(Val::Float(0.0f64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(e.get("_corner_curve_x")?);
            s.push(e.get("_corner_curve_y")?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(e.get("_corner_curve_x")?);
            s.push(unary("neg", e.get("_corner_curve_y")?)?);
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(e.get("_curve_apex_x")?);
            s.push(Val::Float(0.0f64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("insert_positions_for_side_plus_1", assigned171.clone())?;
    let assigned172 = binary(
        "sub",
        e.get("outer_far_x_abs")?,
        e.get("reservoir_wall_thickness")?,
    )?;
    e.set("_far_wall_inner_x", assigned172.clone())?;
    let assigned173 = binary(
        "sub",
        e.get("outer_y_max")?,
        e.get("reservoir_wall_thickness")?,
    )?;
    e.set("_plus_y_wall_inner_y", assigned173.clone())?;
    let assigned174 = binary(
        "add",
        e.get("outer_centerward_radius")?,
        e.get("reservoir_wall_thickness")?,
    )?;
    e.set("_curve_inner_x_at_y0", assigned174.clone())?;
    let assigned175 = binary("truediv", Val::Float(1.0f64), {
        let fun178 = e.get("math")?.attr("sqrt")?;
        let mut args176 = Vec::new();
        let mut kw177 = Vec::new();
        args176.push(Val::Float(2.0f64));
        fun178.call(args176, kw177)?
    })?;
    e.set("_inv_sqrt2", assigned175.clone())?;
    let assigned179 = {
        let fun182 = e.get("math")?.attr("sqrt")?;
        let mut args180 = Vec::new();
        let mut kw181 = Vec::new();
        args180.push(binary(
            "sub",
            binary("pow", e.get("_curve_inner_x_at_y0")?, Val::Int(2i64))?,
            binary("pow", e.get("_plus_y_wall_inner_y")?, Val::Int(2i64))?,
        )?);
        fun182.call(args180, kw181)?
    };
    e.set("_inner_corner_curve_x", assigned179.clone())?;
    let assigned183 = binary(
        "sub",
        e.get("_inner_corner_curve_x")?,
        e.get("_corner_curve_x")?,
    )?;
    e.set("_corner_curve_to_inner_corner_dx", assigned183.clone())?;
    let assigned184 = binary(
        "sub",
        e.get("_plus_y_wall_inner_y")?,
        e.get("_corner_curve_y")?,
    )?;
    e.set("_corner_curve_to_inner_corner_dy", assigned184.clone())?;
    let assigned185 = {
        let fun188 = e.get("math")?.attr("sqrt")?;
        let mut args186 = Vec::new();
        let mut kw187 = Vec::new();
        args186.push(binary(
            "add",
            binary(
                "pow",
                e.get("_corner_curve_to_inner_corner_dx")?,
                Val::Int(2i64),
            )?,
            binary(
                "pow",
                e.get("_corner_curve_to_inner_corner_dy")?,
                Val::Int(2i64),
            )?,
        )?);
        fun188.call(args186, kw187)?
    };
    e.set("_corner_curve_to_inner_corner_dist", assigned185.clone())?;
    let assigned189 = binary(
        "truediv",
        e.get("_corner_curve_to_inner_corner_dx")?,
        e.get("_corner_curve_to_inner_corner_dist")?,
    )?;
    e.set("_corner_curve_wall_dir_x", assigned189.clone())?;
    let assigned190 = binary(
        "truediv",
        e.get("_corner_curve_to_inner_corner_dy")?,
        e.get("_corner_curve_to_inner_corner_dist")?,
    )?;
    e.set("_corner_curve_wall_dir_y", assigned190.clone())?;
    let assigned191 = Val::Float(2.0f64);
    e.set("_corner_curve_pivot_distance", assigned191.clone())?;
    let assigned192 = binary(
        "add",
        e.get("_corner_curve_x")?,
        binary(
            "mul",
            e.get("_corner_curve_pivot_distance")?,
            e.get("_corner_curve_wall_dir_x")?,
        )?,
    )?;
    e.set("_corner_curve_virtual_pivot_x", assigned192.clone())?;
    let assigned193 = binary(
        "add",
        e.get("_corner_curve_y")?,
        binary(
            "mul",
            e.get("_corner_curve_pivot_distance")?,
            e.get("_corner_curve_wall_dir_y")?,
        )?,
    )?;
    e.set("_corner_curve_virtual_pivot_y", assigned193.clone())?;
    let assigned194 = {
        let d = Val::dict(vec![]);
        d.set(
            {
                let mut s = Vec::new();
                s.push(e.get("_corner_xy_x")?);
                s.push(e.get("_corner_xy_y")?);
                Val::tuple(s)
            },
            {
                let mut s = Vec::new();
                s.push(e.get("_far_wall_inner_x")?);
                s.push(e.get("_plus_y_wall_inner_y")?);
                s.push(e.get("_inv_sqrt2")?);
                s.push(e.get("_inv_sqrt2")?);
                Val::tuple(s)
            },
        )?;
        d.set(
            {
                let mut s = Vec::new();
                s.push(e.get("_corner_xy_x")?);
                s.push(unary("neg", e.get("_corner_xy_y")?)?);
                Val::tuple(s)
            },
            {
                let mut s = Vec::new();
                s.push(e.get("_far_wall_inner_x")?);
                s.push(unary("neg", e.get("_plus_y_wall_inner_y")?)?);
                s.push(e.get("_inv_sqrt2")?);
                s.push(unary("neg", e.get("_inv_sqrt2")?)?);
                Val::tuple(s)
            },
        )?;
        d.set(
            {
                let mut s = Vec::new();
                s.push(e.get("_far_mid_x")?);
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            },
            {
                let mut s = Vec::new();
                s.push(e.get("_far_wall_inner_x")?);
                s.push(Val::Float(0.0f64));
                s.push(Val::Float(1.0f64));
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            },
        )?;
        d.set(
            {
                let mut s = Vec::new();
                s.push(e.get("_corner_curve_x")?);
                s.push(e.get("_corner_curve_y")?);
                Val::tuple(s)
            },
            {
                let mut s = Vec::new();
                s.push(e.get("_corner_curve_virtual_pivot_x")?);
                s.push(e.get("_corner_curve_virtual_pivot_y")?);
                s.push(e.get("_corner_curve_wall_dir_x")?);
                s.push(e.get("_corner_curve_wall_dir_y")?);
                Val::tuple(s)
            },
        )?;
        d.set(
            {
                let mut s = Vec::new();
                s.push(e.get("_corner_curve_x")?);
                s.push(unary("neg", e.get("_corner_curve_y")?)?);
                Val::tuple(s)
            },
            {
                let mut s = Vec::new();
                s.push(e.get("_corner_curve_virtual_pivot_x")?);
                s.push(unary("neg", e.get("_corner_curve_virtual_pivot_y")?)?);
                s.push(e.get("_corner_curve_wall_dir_x")?);
                s.push(unary("neg", e.get("_corner_curve_wall_dir_y")?)?);
                Val::tuple(s)
            },
        )?;
        d.set(
            {
                let mut s = Vec::new();
                s.push(e.get("_curve_apex_x")?);
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            },
            {
                let mut s = Vec::new();
                s.push(e.get("_curve_inner_x_at_y0")?);
                s.push(Val::Float(0.0f64));
                s.push(unary("neg", Val::Float(1.0f64))?);
                s.push(Val::Float(0.0f64));
                Val::tuple(s)
            },
        )?;
        d
    };
    e.set("body_boss_cut_info_for_side_plus_1", assigned194.clone())?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod195 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("outer_far_x".into()), e.get("outer_far_x_abs")?)?;
                d.set(Val::Str("outer_y".into()), e.get("outer_y_max")?)?;
                d.set(
                    Val::Str("outer_radius".into()),
                    e.get("outer_centerward_radius")?,
                )?;
                d.set(
                    Val::Str("outer_round".into()),
                    e.get("outer_corner_fillet_radius")?,
                )?;
                d.set(
                    Val::Str("inner_round".into()),
                    e.get("inner_corner_fillet_radius")?,
                )?;
                d.set(Val::Str("wall".into()), e.get("reservoir_wall_thickness")?)?;
                d.set(Val::Str("outer_z".into()), e.get("outer_z_range")?)?;
                d.set(Val::Str("inner_z".into()), e.get("inner_z_range")?)?;
                d.set(Val::Str("insert_stations".into()), {
                    let e = e.child();
                    let out196 = Val::list(vec![]);
                    for item197 in e.get("insert_positions_for_side_plus_1")?.iter()? {
                        e.set("xy", item197)?;
                        out196.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                d.set(Val::Str("cut".into()), {
                                    let fun200 =
                                        e.get("body_boss_cut_info_for_side_plus_1")?.attr("get")?;
                                    let mut args198 = Vec::new();
                                    let mut kw199 = Vec::new();
                                    args198.push(e.get("xy")?);
                                    fun200.call(args198, kw199)?
                                })?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out196
                })?;
                d.set(
                    Val::Str("body_boss_radius".into()),
                    e.get("body_boss_radius")?,
                )?;
                d.set(Val::Str("boss_height".into()), e.get("boss_height")?)?;
                d.set(
                    Val::Str("boss_extra_below".into()),
                    e.get("_cyl_extra_below_bottom")?,
                )?;
                d.set(
                    Val::Str("insert_radius".into()),
                    e.get("insert_pocket_radius")?,
                )?;
                d.set(
                    Val::Str("insert_depth".into()),
                    e.get("insert_pocket_depth")?,
                )?;
                d.set(Val::Str("rod_xy".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("rod_position_x")?);
                    s.push(e.get("rod_position_y")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("rod_floor".into()), e.get("rod_floor_z")?)?;
                d.set(
                    Val::Str("rod_anchor_height".into()),
                    e.get("rod_anchor_boss_height")?,
                )?;
                d.set(
                    Val::Str("rod_anchor_floor".into()),
                    e.get("rod_anchor_boss_floor")?,
                )?;
                d.set(
                    Val::Str("rod_register_height".into()),
                    e.get("rod_register_boss_height")?,
                )?;
                d.set(
                    Val::Str("rod_boss_radius".into()),
                    binary("truediv", e.get("rod_boss_od")?, Val::Int(2i64))?,
                )?;
                d.set(
                    Val::Str("rod_bore_radius".into()),
                    binary("truediv", e.get("rod_bore")?, Val::Int(2i64))?,
                )?;
                d.set(
                    Val::Str("cap_wall_height".into()),
                    e.get("cap_wall_height")?,
                )?;
                d.set(Val::Str("cap_wall_width".into()), e.get("cap_wall_width")?)?;
                d.set(
                    Val::Str("cap_base_thickness".into()),
                    e.get("cap_base_thickness")?,
                )?;
                d.set(Val::Str("cap_height".into()), e.get("cap_total_height")?)?;
                d.set(
                    Val::Str("cap_boss_radius".into()),
                    e.get("cap_boss_radius")?,
                )?;
                d.set(
                    Val::Str("clearance_radius".into()),
                    binary(
                        "truediv",
                        e.get("cap_clearance_hole_diameter")?,
                        Val::Int(2i64),
                    )?,
                )?;
                d.set(
                    Val::Str("counterbore_radius".into()),
                    binary(
                        "truediv",
                        e.get("cap_counterbore_diameter")?,
                        Val::Int(2i64),
                    )?,
                )?;
                d.set(
                    Val::Str("counterbore_depth".into()),
                    e.get("cap_counterbore_depth")?,
                )?;
                d.set(
                    Val::Str("gasket_thickness".into()),
                    e.get("gasket_thickness")?,
                )?;
                d.set(
                    Val::Str("gasket_strip_width".into()),
                    e.get("gasket_strip_width")?,
                )?;
                d.set(
                    Val::Str("gasket_pad_radius".into()),
                    e.get("gasket_pad_radius")?,
                )?;
                d.set(
                    Val::Str("plate_thickness".into()),
                    e.get("tube_ports")?.attr("plate_thickness")?,
                )?;
                d.set(
                    Val::Str("liquid_grip".into()),
                    e.get("tube_ports")?.attr("liquid_grip")?,
                )?;
                d.set(
                    Val::Str("air_grip".into()),
                    e.get("tube_ports")?.attr("air_grip")?,
                )?;
                d.set(Val::Str("ports".into()), {
                    let e = e.child();
                    let out201 = Val::list(vec![]);
                    for item202 in {
                        let mut s = Vec::new();
                        s.push(Val::Int(1i64));
                        s.push(unary("neg", Val::Int(1i64))?);
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("side", item202)?;
                        out201.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("side".into()), e.get("side")?)?;
                                d.set(
                                    Val::Str("vent".into()),
                                    e.get("vent_position")?.get(e.get("side")?)?,
                                )?;
                                d.set(
                                    Val::Str("fill".into()),
                                    if {
                                        let v203 = e.get("side")?;
                                        let v204 = e.get("reservoir_fill_sides")?;
                                        Val::Bool(
                                            compare("in", v203.clone(), v204.clone())?.truthy()?,
                                        )
                                    }
                                    .truthy()?
                                    {
                                        e.get("fill_position")?.get(e.get("side")?)?
                                    } else {
                                        Val::None
                                    },
                                )?;
                                d.set(
                                    Val::Str("draw".into()),
                                    e.get("draw_position")?.get(e.get("side")?)?,
                                )?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out201
                })?;
                d.set(Val::Str("reed_window".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let fun207 = e.get("min")?;
                        let mut args205 = Vec::new();
                        let mut kw206 = Vec::new();
                        args205.push(e.get("reservoir_reed_centres_z")?);
                        fun207.call(args205, kw206)?
                    });
                    s.push({
                        let fun210 = e.get("max")?;
                        let mut args208 = Vec::new();
                        let mut kw209 = Vec::new();
                        args208.push(e.get("reservoir_reed_centres_z")?);
                        fun210.call(args208, kw209)?
                    });
                    Val::tuple(s)
                })?;
                dict_extend(&d, {
                    let e = e.child();
                    let out211 = Val::dict(vec![]);
                    for item212 in {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("body".into()));
                            s.push(e.get("_mat")?.attr("C_RESERVOIR")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("cap".into()));
                            s.push(e.get("_mat")?.attr("C_RES_CAP")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("gasket".into()));
                            s.push(e.get("_mat")?.attr("C_SILICONE")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Str("grip".into()));
                            s.push(e.get("_mat")?.attr("M_TPU_BLACK")?);
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        let unpack213 = unpack(item212, 2)?;
                        e.set("name", unpack213[0].clone())?;
                        e.set("color", unpack213[1].clone())?;
                        out211.set(
                            {
                                let mut str214 = String::new();
                                str214.push_str("color_");
                                str214.push_str(&format(&e.get("name")?, &String::new())?);
                                Val::Str(str214)
                            },
                            {
                                let fun217 = e.get("list")?;
                                let mut args215 = Vec::new();
                                let mut kw216 = Vec::new();
                                args215.push({
                                    let fun220 = e.get("linear")?;
                                    let mut args218 = Vec::new();
                                    let mut kw219 = Vec::new();
                                    args218.push(e.get("color")?);
                                    fun220.call(args218, kw219)?
                                });
                                fun217.call(args215, kw216)?
                            },
                        )?;
                    }
                    out211
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // document
    e.set("document", {
        let params = vec![
            ("capacity_l".into(), None, false),
            ("window_l".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned221 = e.get("_here")?;
            e.set("here", assigned221.clone())?;
            let assigned222 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("FILL_BORE_D".into()), {
                    let mut str223 = String::new();
                    str223.push_str(&format(
                        &e.get("fill_bore_diameter")?,
                        &val_string({
                            let mut str224 = String::new();
                            str224.push_str(".4g");
                            Val::Str(str224)
                        })?,
                    )?);
                    str223.push_str(" mm");
                    Val::Str(str223)
                })?;
                d.set(Val::Str("CONDUIT_BORE_D".into()), {
                    let mut str225 = String::new();
                    str225.push_str(&format(
                        &binary("mul", e.get("port_hole_radius")?, Val::Int(2i64))?,
                        &val_string({
                            let mut str226 = String::new();
                            str226.push_str(".4g");
                            Val::Str(str226)
                        })?,
                    )?);
                    str225.push_str(" mm");
                    Val::Str(str225)
                })?;
                d.set(Val::Str("FILL_POSITION_A".into()), {
                    let fun229 = Val::Str("({:.4g}, {:.4g})".into()).attr("format")?;
                    let mut args227 = Vec::new();
                    let mut kw228 = Vec::new();
                    args227.extend(
                        e.get("fill_position")?
                            .get(unary("pos", Val::Int(1i64))?)?
                            .iter()?,
                    );
                    fun229.call(args227, kw228)?
                })?;
                d.set(Val::Str("FILL_POSITION_B".into()), {
                    let fun232 = Val::Str("({:.4g}, {:.4g})".into()).attr("format")?;
                    let mut args230 = Vec::new();
                    let mut kw231 = Vec::new();
                    args230.extend(
                        e.get("fill_position")?
                            .get(unary("neg", Val::Int(1i64))?)?
                            .iter()?,
                    );
                    fun232.call(args230, kw231)?
                })?;
                d.set(Val::Str("ROD_DIAMETER".into()), {
                    let mut str233 = String::new();
                    str233.push_str(&format(
                        &e.get("rod_diameter")?,
                        &val_string({
                            let mut str234 = String::new();
                            str234.push_str(".4g");
                            Val::Str(str234)
                        })?,
                    )?);
                    str233.push_str(" mm");
                    Val::Str(str233)
                })?;
                d.set(Val::Str("ROD_POSITION_X".into()), {
                    let mut str235 = String::new();
                    str235.push_str(&format(
                        &e.get("rod_position_x")?,
                        &val_string({
                            let mut str236 = String::new();
                            str236.push_str(".2f");
                            Val::Str(str236)
                        })?,
                    )?);
                    Val::Str(str235)
                })?;
                d.set(Val::Str("CAVITY_FAR_WALL_X".into()), {
                    let mut str237 = String::new();
                    str237.push_str(&format(
                        &e.get("inner_far_x_abs")?,
                        &val_string({
                            let mut str238 = String::new();
                            str238.push_str(".2f");
                            Val::Str(str238)
                        })?,
                    )?);
                    Val::Str(str237)
                })?;
                d.set(Val::Str("ROD_WALL_DISTANCE".into()), {
                    let mut str239 = String::new();
                    str239.push_str(&format(
                        &e.get("_float")?.attr("rod_axis_from_inner_wall")?,
                        &val_string({
                            let mut str240 = String::new();
                            str240.push_str("g");
                            Val::Str(str240)
                        })?,
                    )?);
                    str239.push_str(" mm");
                    Val::Str(str239)
                })?;
                d.set(Val::Str("FLOAT_DIAMETER".into()), {
                    let mut str241 = String::new();
                    str241.push_str(&format(
                        &e.get("_float")?.attr("diameter")?,
                        &val_string({
                            let mut str242 = String::new();
                            str242.push_str("g");
                            Val::Str(str242)
                        })?,
                    )?);
                    str241.push_str(" mm");
                    Val::Str(str241)
                })?;
                d.set(Val::Str("FLOAT_HEIGHT".into()), {
                    let mut str243 = String::new();
                    str243.push_str(&format(
                        &e.get("_float")?.attr("height")?,
                        &val_string({
                            let mut str244 = String::new();
                            str244.push_str("g");
                            Val::Str(str244)
                        })?,
                    )?);
                    str243.push_str(" mm");
                    Val::Str(str243)
                })?;
                d.set(Val::Str("FLOAT_TRAVEL".into()), {
                    let mut str245 = String::new();
                    str245.push_str(&format(
                        &e.get("float_magnet_travel_z")?.get(Val::Int(0i64))?,
                        &val_string({
                            let mut str246 = String::new();
                            str246.push_str(".2f");
                            Val::Str(str246)
                        })?,
                    )?);
                    str245.push_str("–");
                    str245.push_str(&format(
                        &e.get("float_magnet_travel_z")?.get(Val::Int(1i64))?,
                        &val_string({
                            let mut str247 = String::new();
                            str247.push_str(".2f");
                            Val::Str(str247)
                        })?,
                    )?);
                    str245.push_str(" mm");
                    Val::Str(str245)
                })?;
                d.set(Val::Str("REED_CENTRES".into()), {
                    let fun250 = Val::Str(", ".into()).attr("join")?;
                    let mut args248 = Vec::new();
                    let mut kw249 = Vec::new();
                    args248.push({
                        let e = e.child();
                        let out251 = Val::list(vec![]);
                        for item252 in e.get("reservoir_reed_centres_z")?.iter()? {
                            e.set("z", item252)?;
                            out251.attr("append")?.call(
                                vec![{
                                    let mut str253 = String::new();
                                    str253.push_str(&format(
                                        &e.get("z")?,
                                        &val_string({
                                            let mut str254 = String::new();
                                            str254.push_str(".2f");
                                            Val::Str(str254)
                                        })?,
                                    )?);
                                    Val::Str(str253)
                                }],
                                vec![],
                            )?;
                        }
                        out251
                    });
                    fun250.call(args248, kw249)?
                })?;
                d.set(Val::Str("ROD_POSITION_Y".into()), {
                    let mut str255 = String::new();
                    str255.push_str(&format(
                        &e.get("rod_position_y")?,
                        &val_string({
                            let mut str256 = String::new();
                            str256.push_str(".4g");
                            Val::Str(str256)
                        })?,
                    )?);
                    Val::Str(str255)
                })?;
                d.set(Val::Str("REEDS_PER_RES".into()), {
                    let mut str257 = String::new();
                    str257.push_str(&format(
                        &e.get("reeds_per_reservoir")?,
                        &val_string({
                            let mut str258 = String::new();
                            str258.push_str(".4g");
                            Val::Str(str258)
                        })?,
                    )?);
                    Val::Str(str257)
                })?;
                d.set(Val::Str("RESERVOIR_ROD_LEN".into()), {
                    let mut str259 = String::new();
                    str259.push_str(&format(
                        &e.get("reservoir_rod_len")?,
                        &val_string({
                            let mut str260 = String::new();
                            str260.push_str(".4g");
                            Val::Str(str260)
                        })?,
                    )?);
                    str259.push_str(" mm (");
                    str259.push_str(&format(
                        &binary("truediv", e.get("reservoir_rod_len")?, Val::Float(25.4f64))?,
                        &val_string({
                            let mut str261 = String::new();
                            str261.push_str(".3g");
                            Val::Str(str261)
                        })?,
                    )?);
                    str259.push_str(" in)");
                    Val::Str(str259)
                })?;
                d.set(Val::Str("RESERVOIR_SEAT_TO_SEAT".into()), {
                    let mut str262 = String::new();
                    str262.push_str(&format(
                        &binary(
                            "add",
                            e.get("reservoir_rod_len")?,
                            e.get("reservoir_rod_clearance")?,
                        )?,
                        &val_string({
                            let mut str263 = String::new();
                            str263.push_str(".4g");
                            Val::Str(str263)
                        })?,
                    )?);
                    str262.push_str(" mm");
                    Val::Str(str262)
                })?;
                d.set(Val::Str("ROD_END_CLEARANCE".into()), {
                    let mut str264 = String::new();
                    str264.push_str(&format(
                        &e.get("reservoir_rod_clearance")?,
                        &val_string({
                            let mut str265 = String::new();
                            str265.push_str("g");
                            Val::Str(str265)
                        })?,
                    )?);
                    str264.push_str(" mm");
                    Val::Str(str264)
                })?;
                d.set(Val::Str("REED_PITCH".into()), {
                    let mut str266 = String::new();
                    str266.push_str(&format(
                        &e.get("reservoir_reed_pitch")?,
                        &val_string({
                            let mut str267 = String::new();
                            str267.push_str("g");
                            Val::Str(str267)
                        })?,
                    )?);
                    str266.push_str(" mm");
                    Val::Str(str266)
                })?;
                d.set(Val::Str("REED_CONDUIT_XY".into()), {
                    let fun270 = Val::Str(", ".into()).attr("join")?;
                    let mut args268 = Vec::new();
                    let mut kw269 = Vec::new();
                    args268.push({
                        let e = e.child();
                        let out271 = Val::list(vec![]);
                        for item272 in {
                            let mut s = Vec::new();
                            s.push(Val::Str("reed-cable-a".into()));
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("n", item272)?;
                            out271.attr("append")?.call(
                                vec![{
                                    let mut str273 = String::new();
                                    str273.push_str(&format(&e.get("n")?, &String::new())?);
                                    str273.push_str(" (");
                                    str273.push_str(&format(
                                        &{
                                            let fun276 = e.get("cap_conduit_shell_xy")?;
                                            let mut args274 = Vec::new();
                                            let mut kw275 = Vec::new();
                                            args274.push(e.get("n")?);
                                            fun276.call(args274, kw275)?
                                        }
                                        .get(Val::Int(0i64))?,
                                        &val_string({
                                            let mut str277 = String::new();
                                            str277.push_str(".4g");
                                            Val::Str(str277)
                                        })?,
                                    )?);
                                    str273.push_str(", ");
                                    str273.push_str(&format(
                                        &{
                                            let fun280 = e.get("cap_conduit_shell_xy")?;
                                            let mut args278 = Vec::new();
                                            let mut kw279 = Vec::new();
                                            args278.push(e.get("n")?);
                                            fun280.call(args278, kw279)?
                                        }
                                        .get(Val::Int(1i64))?,
                                        &val_string({
                                            let mut str281 = String::new();
                                            str281.push_str(".4g");
                                            Val::Str(str281)
                                        })?,
                                    )?);
                                    str273.push_str(")");
                                    Val::Str(str273)
                                }],
                                vec![],
                            )?;
                        }
                        out271
                    });
                    fun270.call(args268, kw269)?
                })?;
                d.set(Val::Str("DRAW_POSITION_A".into()), {
                    let fun284 = Val::Str("({:.4g}, {:.4g})".into()).attr("format")?;
                    let mut args282 = Vec::new();
                    let mut kw283 = Vec::new();
                    args282.extend(
                        e.get("draw_position")?
                            .get(unary("pos", Val::Int(1i64))?)?
                            .iter()?,
                    );
                    fun284.call(args282, kw283)?
                })?;
                d.set(Val::Str("DRAW_POSITION_B".into()), {
                    let fun287 = Val::Str("({:.4g}, {:.4g})".into()).attr("format")?;
                    let mut args285 = Vec::new();
                    let mut kw286 = Vec::new();
                    args285.extend(
                        e.get("draw_position")?
                            .get(unary("neg", Val::Int(1i64))?)?
                            .iter()?,
                    );
                    fun287.call(args285, kw286)?
                })?;
                d.set(Val::Str("FLOOR_Z".into()), {
                    let mut str288 = String::new();
                    str288.push_str(&format(
                        &e.get("rod_floor_z")?,
                        &val_string({
                            let mut str289 = String::new();
                            str289.push_str(".4g");
                            Val::Str(str289)
                        })?,
                    )?);
                    str288.push_str(" mm");
                    Val::Str(str288)
                })?;
                d.set(Val::Str("RESERVOIR_CAPACITY".into()), {
                    let mut str290 = String::new();
                    str290.push_str(&format(
                        &e.get("capacity_l")?,
                        &val_string({
                            let mut str291 = String::new();
                            str291.push_str(".2f");
                            Val::Str(str291)
                        })?,
                    )?);
                    str290.push_str(" L");
                    Val::Str(str290)
                })?;
                d.set(Val::Str("RESERVOIR_WINDOW".into()), {
                    let mut str292 = String::new();
                    str292.push_str(&format(
                        &e.get("window_l")?,
                        &val_string({
                            let mut str293 = String::new();
                            str293.push_str(".2f");
                            Val::Str(str293)
                        })?,
                    )?);
                    str292.push_str(" L");
                    Val::Str(str292)
                })?;
                d.set(Val::Str("RESERVOIR_WALL_T".into()), {
                    let mut str294 = String::new();
                    str294.push_str(&format(
                        &e.get("reservoir_wall_thickness")?,
                        &val_string({
                            let mut str295 = String::new();
                            str295.push_str(".4g");
                            Val::Str(str295)
                        })?,
                    )?);
                    str294.push_str(" mm");
                    Val::Str(str294)
                })?;
                d.set(Val::Str("CAP_TOTAL_H".into()), {
                    let mut str296 = String::new();
                    str296.push_str(&format(
                        &e.get("cap_total_height")?,
                        &val_string({
                            let mut str297 = String::new();
                            str297.push_str(".4g");
                            Val::Str(str297)
                        })?,
                    )?);
                    str296.push_str(" mm");
                    Val::Str(str296)
                })?;
                d.set(Val::Str("ROD_BORE".into()), {
                    let mut str298 = String::new();
                    str298.push_str(&format(
                        &e.get("rod_bore")?,
                        &val_string({
                            let mut str299 = String::new();
                            str299.push_str(".4g");
                            Val::Str(str299)
                        })?,
                    )?);
                    str298.push_str(" mm");
                    Val::Str(str298)
                })?;
                d.set(Val::Str("ROD_BOSS_OD".into()), {
                    let mut str300 = String::new();
                    str300.push_str(&format(
                        &e.get("rod_boss_od")?,
                        &val_string({
                            let mut str301 = String::new();
                            str301.push_str(".4g");
                            Val::Str(str301)
                        })?,
                    )?);
                    str300.push_str(" mm");
                    Val::Str(str300)
                })?;
                d.set(Val::Str("BODY_BOSS_R".into()), {
                    let mut str302 = String::new();
                    str302.push_str(&format(
                        &e.get("body_boss_radius")?,
                        &val_string({
                            let mut str303 = String::new();
                            str303.push_str(".4g");
                            Val::Str(str303)
                        })?,
                    )?);
                    str302.push_str(" mm");
                    Val::Str(str302)
                })?;
                d.set(Val::Str("BODY_BOSS_D".into()), {
                    let mut str304 = String::new();
                    str304.push_str(&format(
                        &binary("mul", Val::Int(2i64), e.get("body_boss_radius")?)?,
                        &val_string({
                            let mut str305 = String::new();
                            str305.push_str(".4g");
                            Val::Str(str305)
                        })?,
                    )?);
                    str304.push_str(" mm");
                    Val::Str(str304)
                })?;
                d.set(Val::Str("CAP_BOSS_R".into()), {
                    let mut str306 = String::new();
                    str306.push_str(&format(
                        &e.get("cap_boss_radius")?,
                        &val_string({
                            let mut str307 = String::new();
                            str307.push_str(".4g");
                            Val::Str(str307)
                        })?,
                    )?);
                    str306.push_str(" mm");
                    Val::Str(str306)
                })?;
                d.set(Val::Str("CAP_STACK_H".into()), {
                    let mut str308 = String::new();
                    str308.push_str(&format(
                        &e.get("cap_stack_above_body")?,
                        &val_string({
                            let mut str309 = String::new();
                            str309.push_str(".4g");
                            Val::Str(str309)
                        })?,
                    )?);
                    str308.push_str(" mm");
                    Val::Str(str308)
                })?;
                d.set(Val::Str("CAP_ASSEMBLY_LIFT".into()), {
                    let mut str310 = String::new();
                    str310.push_str(&format(
                        &e.get("cap_assembly_lift")?,
                        &val_string({
                            let mut str311 = String::new();
                            str311.push_str(".4g");
                            Val::Str(str311)
                        })?,
                    )?);
                    str310.push_str(" mm");
                    Val::Str(str310)
                })?;
                d.set(Val::Str("CAP_TOP_Z".into()), {
                    let mut str312 = String::new();
                    str312.push_str(&format(
                        &e.get("cap_top_z")?,
                        &val_string({
                            let mut str313 = String::new();
                            str313.push_str(".4g");
                            Val::Str(str313)
                        })?,
                    )?);
                    str312.push_str(" mm");
                    Val::Str(str312)
                })?;
                d.set(Val::Str("OUTER_Y_MAX".into()), {
                    let mut str314 = String::new();
                    str314.push_str(&format(
                        &e.get("outer_y_max")?,
                        &val_string({
                            let mut str315 = String::new();
                            str315.push_str(".4g");
                            Val::Str(str315)
                        })?,
                    )?);
                    str314.push_str(" mm");
                    Val::Str(str314)
                })?;
                d.set(Val::Str("OUTER_CENTERWARD_R".into()), {
                    let mut str316 = String::new();
                    str316.push_str(&format(
                        &e.get("outer_centerward_radius")?,
                        &val_string({
                            let mut str317 = String::new();
                            str317.push_str(".4g");
                            Val::Str(str317)
                        })?,
                    )?);
                    str316.push_str(" mm");
                    Val::Str(str316)
                })?;
                d.set(Val::Str("INNER_Y_MAX".into()), {
                    let mut str318 = String::new();
                    str318.push_str(&format(
                        &e.get("inner_y_max")?,
                        &val_string({
                            let mut str319 = String::new();
                            str319.push_str(".4g");
                            Val::Str(str319)
                        })?,
                    )?);
                    str318.push_str(" mm");
                    Val::Str(str318)
                })?;
                d.set(Val::Str("OUTER_TAB_ANGLE".into()), {
                    let mut str320 = String::new();
                    str320.push_str(&format(
                        &e.get("outer_tab_interior_angle")?,
                        &val_string({
                            let mut str321 = String::new();
                            str321.push_str(".0f");
                            Val::Str(str321)
                        })?,
                    )?);
                    str320.push_str("°");
                    Val::Str(str320)
                })?;
                d.set(Val::Str("INNER_CORNER_ANGLE".into()), {
                    let mut str322 = String::new();
                    str322.push_str(&format(
                        &e.get("inner_corner_interior_angle")?,
                        &val_string({
                            let mut str323 = String::new();
                            str323.push_str(".0f");
                            Val::Str(str323)
                        })?,
                    )?);
                    str322.push_str("°");
                    Val::Str(str322)
                })?;
                d.set(Val::Str("CAP_COUNTERBORE_D".into()), {
                    let mut str324 = String::new();
                    str324.push_str(&format(
                        &e.get("cap_counterbore_diameter")?,
                        &val_string({
                            let mut str325 = String::new();
                            str325.push_str(".4g");
                            Val::Str(str325)
                        })?,
                    )?);
                    str324.push_str(" mm");
                    Val::Str(str324)
                })?;
                d.set(Val::Str("CAP_CLEARANCE_HOLE_D".into()), {
                    let mut str326 = String::new();
                    str326.push_str(&format(
                        &e.get("cap_clearance_hole_diameter")?,
                        &val_string({
                            let mut str327 = String::new();
                            str327.push_str(".4g");
                            Val::Str(str327)
                        })?,
                    )?);
                    str326.push_str(" mm");
                    Val::Str(str326)
                })?;
                d.set(Val::Str("GASKET_STRIP_W".into()), {
                    let mut str328 = String::new();
                    str328.push_str(&format(
                        &e.get("gasket_strip_width")?,
                        &val_string({
                            let mut str329 = String::new();
                            str329.push_str(".4g");
                            Val::Str(str329)
                        })?,
                    )?);
                    str328.push_str(" mm");
                    Val::Str(str328)
                })?;
                d.set(Val::Str("GASKET_THICKNESS".into()), {
                    let mut str330 = String::new();
                    str330.push_str(&format(
                        &e.get("gasket_thickness")?,
                        &val_string({
                            let mut str331 = String::new();
                            str331.push_str(".4g");
                            Val::Str(str331)
                        })?,
                    )?);
                    str330.push_str(" mm");
                    Val::Str(str330)
                })?;
                d.set(Val::Str("RESERVOIR_CLEARANCE".into()), {
                    let mut str332 = String::new();
                    str332.push_str(&format(
                        &e.get("reservoir_clearance")?,
                        &val_string({
                            let mut str333 = String::new();
                            str333.push_str(".4g");
                            Val::Str(str333)
                        })?,
                    )?);
                    str332.push_str(" mm");
                    Val::Str(str332)
                })?;
                d.set(Val::Str("INSERT_POCKET_DEPTH".into()), {
                    let mut str334 = String::new();
                    str334.push_str(&format(
                        &e.get("insert_pocket_depth")?,
                        &val_string({
                            let mut str335 = String::new();
                            str335.push_str(".4g");
                            Val::Str(str335)
                        })?,
                    )?);
                    str334.push_str(" mm");
                    Val::Str(str334)
                })?;
                d.set(Val::Str("OUTER_FILLET_R".into()), {
                    let mut str336 = String::new();
                    str336.push_str(&format(
                        &e.get("outer_corner_fillet_radius")?,
                        &val_string({
                            let mut str337 = String::new();
                            str337.push_str(".4g");
                            Val::Str(str337)
                        })?,
                    )?);
                    str336.push_str(" mm");
                    Val::Str(str336)
                })?;
                d.set(Val::Str("CORNER_XY_Y".into()), {
                    let mut str338 = String::new();
                    str338.push_str(&format(
                        &e.get("_corner_xy_y")?,
                        &val_string({
                            let mut str339 = String::new();
                            str339.push_str(".4g");
                            Val::Str(str339)
                        })?,
                    )?);
                    Val::Str(str338)
                })?;
                d.set(Val::Str("INNER_CORNER_CURVE_X".into()), {
                    let mut str340 = String::new();
                    str340.push_str(&format(
                        &e.get("_inner_corner_curve_x")?,
                        &val_string({
                            let mut str341 = String::new();
                            str341.push_str(".4g");
                            Val::Str(str341)
                        })?,
                    )?);
                    str340.push_str(" mm");
                    Val::Str(str340)
                })?;
                d.set(Val::Str("CORNER_CURVE_DIST".into()), {
                    let mut str342 = String::new();
                    str342.push_str(&format(
                        &e.get("_corner_curve_to_inner_corner_dist")?,
                        &val_string({
                            let mut str343 = String::new();
                            str343.push_str(".4g");
                            Val::Str(str343)
                        })?,
                    )?);
                    str342.push_str(" mm");
                    Val::Str(str342)
                })?;
                d.set(Val::Str("GASKET_PAD_D".into()), {
                    let mut str344 = String::new();
                    str344.push_str("ø");
                    str344.push_str(&format(
                        &binary("mul", Val::Int(2i64), e.get("gasket_pad_radius")?)?,
                        &val_string({
                            let mut str345 = String::new();
                            str345.push_str(".4g");
                            Val::Str(str345)
                        })?,
                    )?);
                    Val::Str(str344)
                })?;
                d
            };
            e.set("variables", assigned222.clone())?;
            {
                let fun348 = e.get("substitute_md")?;
                let mut args346 = Vec::new();
                let mut kw347 = Vec::new();
                args346.push(binary(
                    "truediv",
                    e.get("here")?,
                    Val::Str("vent.md".into()),
                )?);
                kw347.push(("variables".into(), e.get("variables")?));
                fun348.call(args346, kw347)?
            };
            {
                let fun351 = e.get("print")?;
                let mut args349 = Vec::new();
                let mut kw350 = Vec::new();
                args349.push(Val::Str("-> vent.md".into()));
                fun351.call(args349, kw350)?
            };
            {
                let fun354 = e.get("substitute_md")?;
                let mut args352 = Vec::new();
                let mut kw353 = Vec::new();
                args352.push(binary(
                    "truediv",
                    e.get("here")?,
                    Val::Str("level-sensing.md".into()),
                )?);
                kw353.push(("variables".into(), e.get("variables")?));
                fun354.call(args352, kw353)?
            };
            {
                let fun357 = e.get("print")?;
                let mut args355 = Vec::new();
                let mut kw356 = Vec::new();
                args355.push(Val::Str("-> level-sensing.md".into()));
                fun357.call(args355, kw356)?
            };
            {
                let fun360 = e.get("substitute_md")?;
                let mut args358 = Vec::new();
                let mut kw359 = Vec::new();
                args358.push(binary(
                    "truediv",
                    e.get("here")?,
                    Val::Str("floor-and-dip-tube.md".into()),
                )?);
                kw359.push(("variables".into(), e.get("variables")?));
                fun360.call(args358, kw359)?
            };
            {
                let fun363 = e.get("print")?;
                let mut args361 = Vec::new();
                let mut kw362 = Vec::new();
                args361.push(Val::Str("-> floor-and-dip-tube.md".into()));
                fun363.call(args361, kw362)?
            };
            {
                let fun366 = e.get("substitute_py_comments")?;
                let mut args364 = Vec::new();
                let mut kw365 = Vec::new();
                args364.push({
                    let fun369 = e.get("Path")?;
                    let mut args367 = Vec::new();
                    let mut kw368 = Vec::new();
                    args367.push(e.get("__file__")?);
                    fun369.call(args367, kw368)?
                });
                kw365.push(("variables".into(), e.get("variables")?));
                fun366.call(args364, kw365)?
            };
            {
                let fun372 = e.get("print")?;
                let mut args370 = Vec::new();
                let mut kw371 = Vec::new();
                args370.push({
                    let mut str373 = String::new();
                    str373.push_str("-> ");
                    str373.push_str(&format(
                        &{
                            let fun376 = e.get("Path")?;
                            let mut args374 = Vec::new();
                            let mut kw375 = Vec::new();
                            args374.push(e.get("__file__")?);
                            fun376.call(args374, kw375)?
                        }
                        .attr("name")?,
                        &String::new(),
                    )?);
                    str373.push_str(" (self)");
                    Val::Str(str373)
                });
                fun372.call(args370, kw371)?
            };
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("output".into(), Some(e.get("_here")?), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            let mod377 = rt.import_module("flute_payload")?;
            e.set("write_print_payload", rt.member("flute_payload", "cut")?)?;
            let assigned378 = {
                let fun381 = e.get("Path")?;
                let mut args379 = Vec::new();
                let mut kw380 = Vec::new();
                args379.push(e.get("output")?);
                fun381.call(args379, kw380)?
            };
            e.set("output", assigned378.clone())?;
            {
                let fun384 = e.get("output")?.attr("mkdir")?;
                let mut args382 = Vec::new();
                let mut kw383 = Vec::new();
                kw383.push(("parents".into(), Val::Bool(true)));
                kw383.push(("exist_ok".into(), Val::Bool(true)));
                fun384.call(args382, kw383)?
            };
            let assigned385 = {
                let fun388 = e.get("_rust_part")?.attr("cut")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push(Val::Str("cold-core".into()));
                args386.push(Val::Str("reservoir".into()));
                args386.push({
                    let fun391 = e.get("numbers")?;
                    let mut args389 = Vec::new();
                    let mut kw390 = Vec::new();
                    fun391.call(args389, kw390)?
                });
                args386.push(e.get("output")?);
                fun388.call(args386, kw387)?
            }
            .get(Val::Str("bodies".into()))?
            .get(Val::Int(0i64))?;
            e.set("readings", assigned385.clone())?;
            let assigned392 = {
                let mut s = Vec::new();
                s.push(e.get("readings")?.get(Val::Str("capacity_l".into()))?);
                s.push(e.get("readings")?.get(Val::Str("reed_window_l".into()))?);
                Val::tuple(s)
            };
            let unpack393 = unpack(assigned392.clone(), 2)?;
            e.set("capacity_l", unpack393[0].clone())?;
            e.set("window_l", unpack393[1].clone())?;
            for item394 in {
                let mut s = Vec::new();
                s.push(Val::Str("reservoir-cap-right".into()));
                s.push(Val::Str("reservoir-cap-left".into()));
                s.push(Val::Str("reservoir-tube-grip".into()));
                s.push(Val::Str("reservoir-air-grip".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("name", item394)?;
                {
                    let fun397 = e.get("write_print_payload")?;
                    let mut args395 = Vec::new();
                    let mut kw396 = Vec::new();
                    args395.push(binary(
                        "truediv",
                        e.get("output")?,
                        binary("add", e.get("name")?, Val::Str(".step".into()))?,
                    )?);
                    args395.push(binary(
                        "truediv",
                        e.get("output")?,
                        binary("add", e.get("name")?, Val::Str(".stl".into()))?,
                    )?);
                    kw396.push(("preserve_print_triangles".into(), Val::Bool(true)));
                    fun397.call(args395, kw396)?
                };
            }
            {
                let fun400 = e.get("print")?;
                let mut args398 = Vec::new();
                let mut kw399 = Vec::new();
                args398.push({
                    let mut str401 = String::new();
                    str401.push_str("   capacity ");
                    str401.push_str(&format(
                        &e.get("capacity_l")?,
                        &val_string({
                            let mut str402 = String::new();
                            str402.push_str(".3f");
                            Val::Str(str402)
                        })?,
                    )?);
                    str401.push_str(" L floor to rim; ");
                    str401.push_str(&format(
                        &e.get("window_l")?,
                        &val_string({
                            let mut str403 = String::new();
                            str403.push_str(".3f");
                            Val::Str(str403)
                        })?,
                    )?);
                    str401.push_str(" L between the end reeds");
                    Val::Str(str401)
                });
                fun400.call(args398, kw399)?
            };
            {
                let fun406 = e.get("document")?;
                let mut args404 = Vec::new();
                let mut kw405 = Vec::new();
                args404.push(e.get("capacity_l")?);
                args404.push(e.get("window_l")?);
                fun406.call(args404, kw405)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun409 = e.get("_rust_part")?.attr("start")?;
        let mut args407 = Vec::new();
        let mut kw408 = Vec::new();
        fun409.call(args407, kw408)?
    };
    let assigned410 = {
        let fun413 = e.get("argparse")?.attr("ArgumentParser")?;
        let mut args411 = Vec::new();
        let mut kw412 = Vec::new();
        kw412.push(("description".into(), e.get("__doc__")?));
        fun413.call(args411, kw412)?
    };
    e.set("parser", assigned410.clone())?;
    {
        let fun416 = e.get("parser")?.attr("add_argument")?;
        let mut args414 = Vec::new();
        let mut kw415 = Vec::new();
        args414.push(Val::Str("--output".into()));
        kw415.push(("type".into(), e.get("Path")?));
        kw415.push(("default".into(), e.get("_here")?));
        fun416.call(args414, kw415)?
    };
    let assigned417 = {
        let fun420 = e.get("parser")?.attr("parse_args")?;
        let mut args418 = Vec::new();
        let mut kw419 = Vec::new();
        fun420.call(args418, kw419)?
    };
    e.set("args", assigned417.clone())?;
    {
        let fun423 = e.get("main")?;
        let mut args421 = Vec::new();
        let mut kw422 = Vec::new();
        args421.push(e.get("args")?.attr("output")?);
        fun423.call(args421, kw422)?
    };
    Ok(Val::None)
}
