#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
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
    let mod55 = rt.import_module("_materials")?;
    e.set("C_FOAM_SHELL", rt.member("_materials", "C_FOAM_SHELL")?)?;
    let mod56 = rt.import_module("_cold_core_interface")?;
    e.set(
        "above_carbonator_elbows_height",
        rt.member("_cold_core_interface", "above_carbonator_elbows_height")?,
    )?;
    e.set(
        "attachment_xy_positions",
        rt.member("_cold_core_interface", "attachment_xy_positions")?,
    )?;
    e.set(
        "casing_foil_land",
        rt.member("_cold_core_interface", "casing_foil_land")?,
    )?;
    e.set(
        "seam_channel_depth",
        rt.member("_cold_core_interface", "seam_channel_depth")?,
    )?;
    e.set(
        "seam_channel_land",
        rt.member("_cold_core_interface", "seam_channel_land")?,
    )?;
    e.set(
        "seam_channel_width",
        rt.member("_cold_core_interface", "seam_channel_width")?,
    )?;
    e.set(
        "bag_pocket_corner_inner_radius",
        rt.member("_cold_core_interface", "bag_pocket_corner_inner_radius")?,
    )?;
    e.set(
        "bag_pocket_far_inner_x",
        rt.member("_cold_core_interface", "bag_pocket_far_inner_x")?,
    )?;
    e.set(
        "bag_pocket_outermost_x",
        rt.member("_cold_core_interface", "bag_pocket_outermost_x")?,
    )?;
    e.set(
        "bag_pocket_width",
        rt.member("_cold_core_interface", "bag_pocket_width")?,
    )?;
    e.set(
        "bag_pocket_y_inner_max",
        rt.member("_cold_core_interface", "bag_pocket_y_inner_max")?,
    )?;
    e.set(
        "coil_radial_clearance",
        rt.member("_cold_core_interface", "coil_radial_clearance")?,
    )?;
    e.set(
        "carbonator_coil_envelope_radius",
        rt.member("_cold_core_interface", "carbonator_coil_envelope_radius")?,
    )?;
    e.set(
        "corner_round_radius",
        rt.member("_cold_core_interface", "corner_round_radius")?,
    )?;
    e.set(
        "forward_band_width",
        rt.member("_cold_core_interface", "forward_band_width")?,
    )?;
    e.set(
        "outer_shell_wall",
        rt.member("_cold_core_interface", "outer_shell_wall")?,
    )?;
    e.set(
        "pour_band_pocket_side_y",
        rt.member("_cold_core_interface", "pour_band_pocket_side_y")?,
    )?;
    e.set(
        "pour_band_shell_side_y",
        rt.member("_cold_core_interface", "pour_band_shell_side_y")?,
    )?;
    e.set(
        "foam_cap_interior_height",
        rt.member("_cold_core_interface", "foam_cap_interior_height")?,
    )?;
    e.set(
        "cap_shell_clearance",
        rt.member("_cold_core_interface", "cap_shell_clearance")?,
    )?;
    e.set(
        "cap_lid_clearance",
        rt.member("_cold_core_interface", "cap_lid_clearance")?,
    )?;
    e.set(
        "foam_cap_lid_pour_radius",
        rt.member("_cold_core_interface", "foam_cap_lid_pour_radius")?,
    )?;
    e.set(
        "foam_cap_lid_vent_radius",
        rt.member("_cold_core_interface", "foam_cap_lid_vent_radius")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "foam_shell_rim_z",
        rt.member("_cold_core_interface", "foam_shell_rim_z")?,
    )?;
    e.set(
        "insert_pocket_depth",
        rt.member("_cold_core_interface", "insert_pocket_depth")?,
    )?;
    e.set(
        "front_wall_x",
        rt.member("_cold_core_interface", "front_wall_x")?,
    )?;
    e.set(
        "mid_screw_x_offset",
        rt.member("_cold_core_interface", "mid_screw_x_offset")?,
    )?;
    e.set(
        "outer_shell_foam_gap",
        rt.member("_cold_core_interface", "outer_shell_foam_gap")?,
    )?;
    e.set(
        "port_lane_inner_y",
        rt.member("_cold_core_interface", "port_lane_inner_y")?,
    )?;
    e.set(
        "port_lane_mid_y",
        rt.member("_cold_core_interface", "port_lane_mid_y")?,
    )?;
    e.set(
        "port_lane_outer_y",
        rt.member("_cold_core_interface", "port_lane_outer_y")?,
    )?;
    e.set(
        "outer_shell_x_length",
        rt.member("_cold_core_interface", "outer_shell_x_length")?,
    )?;
    e.set(
        "outer_shell_y_length",
        rt.member("_cold_core_interface", "outer_shell_y_length")?,
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
        "screw_boss_size",
        rt.member("_cold_core_interface", "screw_boss_size")?,
    )?;
    e.set(
        "support_ring_radial_width",
        rt.member("_cold_core_interface", "support_ring_radial_width")?,
    )?;
    e.set(
        "carbonator_height",
        rt.member("_cold_core_interface", "carbonator_height")?,
    )?;
    e.set(
        "carbonator_outer_radius",
        rt.member("_cold_core_interface", "carbonator_outer_radius")?,
    )?;
    e.set(
        "carbonator_support_ring_height",
        rt.member("_cold_core_interface", "carbonator_support_ring_height")?,
    )?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "wall_thickness",
        rt.member("_cold_core_interface", "wall_thickness")?,
    )?;
    let mod57 = rt.import_module("_reservoir_pocket_walls")?;
    e.set(
        "pocket_centerward_arc_transition_y",
        rt.member(
            "_reservoir_pocket_walls",
            "pocket_centerward_arc_transition_y",
        )?,
    )?;
    e.set(
        "transition_outer_r",
        rt.member("_reservoir_pocket_walls", "transition_outer_r")?,
    )?;
    let mod58 = rt.import_module("_port_cuts")?;
    e.set("co2_inlet_xyz", rt.member("_port_cuts", "co2_inlet_xyz")?)?;
    let mod59 = rt.import_module("_cold_core_interface")?;
    e.set(
        "cap_screw_beyond_face",
        rt.member("_cold_core_interface", "cap_screw_beyond_face")?,
    )?;
    e.set(
        "cap_screw_length",
        rt.member("_cold_core_interface", "cap_screw_length")?,
    )?;
    e.set(
        "head_cbore_radius",
        rt.member("_cold_core_interface", "head_cbore_radius")?,
    )?;
    e.set(
        "head_pad_height",
        rt.member("_cold_core_interface", "head_pad_height")?,
    )?;
    e.set(
        "insert_length",
        rt.member("_cold_core_interface", "insert_length")?,
    )?;
    e.set(
        "screw_head_height",
        rt.member("_cold_core_interface", "screw_head_height")?,
    )?;
    let mod61 = rt.import_module("_copper_ports")?;
    e.set("evap_cross_z", rt.member("_copper_ports", "evap_cross_z")?)?;
    e.set(
        "copper_hole_radius",
        rt.member("_copper_ports", "hole_radius")?,
    )?;
    e.set("stations", rt.member("_copper_ports", "stations")?)?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("fits", rt.import_module("fits")?)?;
            e.set("core", rt.import_module("_cold_core_interface")?)?;
            e.set("pockets", rt.import_module("_reservoir_pocket_walls")?)?;
            e.set("support", rt.import_module("_support_ring")?)?;
            e.set("reeds", rt.import_module("_reed_channels")?)?;
            e.set("outlet", rt.import_module("_reed_b_outlet")?)?;
            e.set("routes", rt.import_module("_internal_routes")?)?;
            e.set("b_fill", rt.import_module("_reservoir_b_fill")?)?;
            e.set("mounts", rt.import_module("_above_core_mounts")?)?;
            let mod62 = rt.import_module("_foam_cap")?;
            e.set("top_cap_height", rt.member("_foam_cap", "top_cap_height")?)?;
            let mod63 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            // box
            e.set("box", {
                let params = vec![
                    ("x".into(), None, false),
                    ("y".into(), None, false),
                    ("z".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let mut s = Vec::new();
                        s.push({
                            let fun66 = e.get("list")?;
                            let mut args64 = Vec::new();
                            let mut kw65 = Vec::new();
                            args64.push(e.get("x")?);
                            fun66.call(args64, kw65)?
                        });
                        s.push({
                            let fun69 = e.get("list")?;
                            let mut args67 = Vec::new();
                            let mut kw68 = Vec::new();
                            args67.push(e.get("y")?);
                            fun69.call(args67, kw68)?
                        });
                        s.push({
                            let fun72 = e.get("list")?;
                            let mut args70 = Vec::new();
                            let mut kw71 = Vec::new();
                            args70.push(e.get("z")?);
                            fun72.call(args70, kw71)?
                        });
                        Val::list(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned73 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                Val::tuple(s)
            };
            let unpack74 = unpack(assigned73.clone(), 5)?;
            e.set("envelopes", unpack74[0].clone())?;
            e.set("cavities", unpack74[1].clone())?;
            e.set("openings", unpack74[2].clone())?;
            e.set("upper_backs", unpack74[3].clone())?;
            e.set("roofs", unpack74[4].clone())?;
            for item75 in {
                let mut s = Vec::new();
                s.push(Val::Int(1i64));
                s.push(unary("neg", Val::Int(1i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("side", item75)?;
                let assigned76 = binary(
                    "mul",
                    e.get("side")?,
                    e.get("core")?.attr("reed_channel_inner_x")?,
                )?;
                e.set("x", assigned76.clone())?;
                {
                    let fun79 = e.get("envelopes")?.attr("append")?;
                    let mut args77 = Vec::new();
                    let mut kw78 = Vec::new();
                    args77.push({
                        let fun82 = e.get("box")?;
                        let mut args80 = Vec::new();
                        let mut kw81 = Vec::new();
                        args80.push({
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(binary(
                                "add",
                                e.get("x")?,
                                binary(
                                    "mul",
                                    e.get("side")?,
                                    binary(
                                        "add",
                                        e.get("core")?.attr("reed_x_depth")?,
                                        e.get("core")?.attr("wall_thickness")?,
                                    )?,
                                )?,
                            )?);
                            Val::tuple(s)
                        });
                        args80.push(e.get("reeds")?.attr("reed_envelope_y_range")?);
                        args80.push(e.get("reeds")?.attr("reed_envelope_z_range")?);
                        fun82.call(args80, kw81)?
                    });
                    fun79.call(args77, kw78)?
                };
                {
                    let fun85 = e.get("cavities")?.attr("append")?;
                    let mut args83 = Vec::new();
                    let mut kw84 = Vec::new();
                    args83.push({
                        let fun88 = e.get("box")?;
                        let mut args86 = Vec::new();
                        let mut kw87 = Vec::new();
                        args86.push({
                            let mut s = Vec::new();
                            s.push(e.get("x")?);
                            s.push(binary(
                                "add",
                                e.get("x")?,
                                binary(
                                    "mul",
                                    e.get("side")?,
                                    e.get("core")?.attr("reed_x_depth")?,
                                )?,
                            )?);
                            Val::tuple(s)
                        });
                        args86.push(e.get("reeds")?.attr("reed_cavity_y_range")?);
                        args86.push(e.get("reeds")?.attr("reed_cavity_z_range")?);
                        fun88.call(args86, kw87)?
                    });
                    fun85.call(args83, kw84)?
                };
                {
                    let fun91 = e.get("openings")?.attr("append")?;
                    let mut args89 = Vec::new();
                    let mut kw90 = Vec::new();
                    args89.push({
                        let fun94 = e.get("box")?;
                        let mut args92 = Vec::new();
                        let mut kw93 = Vec::new();
                        args92.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "mul",
                                e.get("side")?,
                                e.get("core")?.attr("bag_pocket_far_inner_x")?,
                            )?);
                            s.push(binary(
                                "mul",
                                e.get("side")?,
                                e.get("core")?.attr("bag_pocket_outermost_x")?,
                            )?);
                            Val::tuple(s)
                        });
                        args92.push(e.get("reeds")?.attr("reed_cavity_y_range")?);
                        args92.push({
                            let mut s = Vec::new();
                            s.push(e.get("core")?.attr("wall_and_floor_thickness")?);
                            s.push(e.get("core")?.attr("foam_shell_outer_height")?);
                            Val::tuple(s)
                        });
                        fun94.call(args92, kw93)?
                    });
                    fun91.call(args89, kw90)?
                };
                {
                    let fun97 = e.get("upper_backs")?.attr("append")?;
                    let mut args95 = Vec::new();
                    let mut kw96 = Vec::new();
                    args95.push({
                        let fun100 = e.get("box")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push({
                            let mut s = Vec::new();
                            s.push(binary(
                                "mul",
                                e.get("side")?,
                                e.get("core")?.attr("bag_pocket_far_inner_x")?,
                            )?);
                            s.push(binary(
                                "mul",
                                e.get("side")?,
                                e.get("core")?.attr("reed_channel_inner_x")?,
                            )?);
                            Val::tuple(s)
                        });
                        args98.push(e.get("reeds")?.attr("reed_envelope_y_range")?);
                        args98.push({
                            let mut s = Vec::new();
                            s.push(e.get("core")?.attr("foam_shell_outer_height")?);
                            s.push(e.get("core")?.attr("foam_shell_rim_z")?);
                            Val::tuple(s)
                        });
                        fun100.call(args98, kw99)?
                    });
                    fun97.call(args95, kw96)?
                };
                let assigned101 = {
                    let fun104 = e.get("sorted")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "mul",
                            e.get("side")?,
                            e.get("core")?.attr("bag_pocket_far_inner_x")?,
                        )?);
                        s.push(binary(
                            "mul",
                            e.get("side")?,
                            e.get("core")?.attr("bag_pocket_outermost_x")?,
                        )?);
                        Val::tuple(s)
                    });
                    fun104.call(args102, kw103)?
                };
                let unpack105 = unpack(assigned101.clone(), 2)?;
                e.set("x0", unpack105[0].clone())?;
                e.set("x1", unpack105[1].clone())?;
                let assigned106 = e.get("reeds")?.attr("reed_cavity_y_range")?;
                let unpack107 = unpack(assigned106.clone(), 2)?;
                e.set("y0", unpack107[0].clone())?;
                e.set("y1", unpack107[1].clone())?;
                let assigned108 = e.get("core")?.attr("foam_shell_outer_height")?;
                e.set("z", assigned108.clone())?;
                {
                    let fun111 = e.get("roofs")?.attr("append")?;
                    let mut args109 = Vec::new();
                    let mut kw110 = Vec::new();
                    args109.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("section".into()), {
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("y0")?);
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("y1")?);
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("reeds")?.attr("reed_y_center")?);
                                s.push(binary(
                                    "add",
                                    e.get("z")?,
                                    binary(
                                        "mul",
                                        Val::Float(2.0f64),
                                        e.get("core")?.attr("reed_y_half_w")?,
                                    )?,
                                )?);
                                Val::tuple(s)
                            });
                            Val::list(s)
                        })?;
                        d.set(Val::Str("start_x".into()), e.get("x0")?)?;
                        d.set(
                            Val::Str("depth".into()),
                            binary("sub", e.get("x1")?, e.get("x0")?)?,
                        )?;
                        d
                    });
                    fun111.call(args109, kw110)?
                };
            }
            // world_to_shell
            e.set("world_to_shell", {
                let params = vec![("point".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned112 = {
                        let fun115 = e.get("mounts")?.attr("above_core")?.attr("world_to_cap")?;
                        let mut args113 = Vec::new();
                        let mut kw114 = Vec::new();
                        args113.push(e.get("point")?);
                        fun115.call(args113, kw114)?
                    };
                    let unpack116 = unpack(assigned112.clone(), 3)?;
                    e.set("x", unpack116[0].clone())?;
                    e.set("y", unpack116[1].clone())?;
                    e.set("z", unpack116[2].clone())?;
                    return Ok({
                        let mut s = Vec::new();
                        s.push(unary("neg", e.get("x")?)?);
                        s.push(unary("neg", e.get("y")?)?);
                        s.push(binary(
                            "add",
                            binary(
                                "add",
                                e.get("z")?,
                                e.get("core")?.attr("foam_shell_outer_height")?,
                            )?,
                            e.get("top_cap_height")?,
                        )?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned117 = {
                let fun120 = e.get("world_to_shell")?;
                let mut args118 = Vec::new();
                let mut kw119 = Vec::new();
                args118.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun120.call(args118, kw119)?
            };
            e.set("origin", assigned117.clone())?;
            let assigned121 = {
                let e = e.child();
                let out122 = Val::list(vec![]);
                for item123 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("axis", item123)?;
                    out122.attr("append")?.call(
                        vec![{
                            let fun126 = e.get("tuple")?;
                            let mut args124 = Vec::new();
                            let mut kw125 = Vec::new();
                            args124.push({
                                let e = e.child();
                                let out127 = Val::list(vec![]);
                                for item128 in {
                                    let fun131 = e.get("zip")?;
                                    let mut args129 = Vec::new();
                                    let mut kw130 = Vec::new();
                                    args129.push(e.get("origin")?);
                                    args129.push({
                                        let fun134 = e.get("world_to_shell")?;
                                        let mut args132 = Vec::new();
                                        let mut kw133 = Vec::new();
                                        args132.push(e.get("axis")?);
                                        fun134.call(args132, kw133)?
                                    });
                                    fun131.call(args129, kw130)?
                                }
                                .iter()?
                                {
                                    let unpack135 = unpack(item128, 2)?;
                                    e.set("a", unpack135[0].clone())?;
                                    e.set("b", unpack135[1].clone())?;
                                    out127.attr("append")?.call(
                                        vec![binary("sub", e.get("b")?, e.get("a")?)?],
                                        vec![],
                                    )?;
                                }
                                out127
                            });
                            fun126.call(args124, kw125)?
                        }],
                        vec![],
                    )?;
                }
                out122
            };
            e.set("axes", assigned121.clone())?;
            let assigned136 = {
                let fun139 = e.get("b_fill")?.attr("passage")?;
                let mut args137 = Vec::new();
                let mut kw138 = Vec::new();
                fun139.call(args137, kw138)?
            };
            e.set("b_passage", assigned136.clone())?;
            let assigned140 = e
                .get("b_passage")?
                .get(Val::Str("bend_end_world_mm".into()))?;
            e.set("b_end", assigned140.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("height".into()),
                    e.get("core")?.attr("foam_shell_rim_z")?,
                )?;
                d.set(
                    Val::Str("pocket_height".into()),
                    e.get("core")?.attr("foam_shell_outer_height")?,
                )?;
                d.set(
                    Val::Str("floor".into()),
                    e.get("core")?.attr("wall_and_floor_thickness")?,
                )?;
                d.set(
                    Val::Str("wall".into()),
                    e.get("core")?.attr("wall_thickness")?,
                )?;
                d.set(
                    Val::Str("outer_wall".into()),
                    e.get("core")?.attr("outer_shell_wall")?,
                )?;
                d.set(
                    Val::Str("width".into()),
                    e.get("core")?.attr("outer_shell_x_length")?,
                )?;
                d.set(
                    Val::Str("depth".into()),
                    e.get("core")?.attr("outer_shell_y_length")?,
                )?;
                d.set(
                    Val::Str("corner_radius".into()),
                    e.get("core")?.attr("corner_round_radius")?,
                )?;
                d.set(Val::Str("pocket".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("middle_x".into()),
                        e.get("pockets")?.attr("middle_cavity_x")?,
                    )?;
                    d.set(
                        Val::Str("inner_y".into()),
                        e.get("pockets")?.attr("y_inner")?,
                    )?;
                    d.set(
                        Val::Str("far_x".into()),
                        e.get("core")?.attr("bag_pocket_far_inner_x")?,
                    )?;
                    d.set(
                        Val::Str("corner_radius".into()),
                        e.get("core")?.attr("bag_pocket_corner_inner_radius")?,
                    )?;
                    d.set(
                        Val::Str("transition_y".into()),
                        e.get("pockets")?
                            .attr("pocket_centerward_arc_transition_y")?,
                    )?;
                    d.set(
                        Val::Str("transition_x".into()),
                        binary(
                            "sub",
                            e.get("pockets")?.attr("transition_center_x")?,
                            e.get("pockets")?.attr("transition_cavity_r")?,
                        )?,
                    )?;
                    d.set(
                        Val::Str("transition_mid_y".into()),
                        e.get("pockets")?.attr("transition_center_y")?,
                    )?;
                    d.set(
                        Val::Str("arc_radius".into()),
                        e.get("pockets")?.attr("arc_cavity_r")?,
                    )?;
                    d
                })?;
                d.set(Val::Str("support".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("outer_radius".into()),
                        e.get("core")?.attr("carbonator_coil_envelope_radius")?,
                    )?;
                    d.set(
                        Val::Str("inner_radius".into()),
                        binary(
                            "sub",
                            e.get("core")?.attr("carbonator_coil_envelope_radius")?,
                            e.get("core")?.attr("support_ring_radial_width")?,
                        )?,
                    )?;
                    d.set(
                        Val::Str("bottom".into()),
                        e.get("core")?.attr("wall_and_floor_thickness")?,
                    )?;
                    d.set(
                        Val::Str("top".into()),
                        binary(
                            "add",
                            e.get("core")?.attr("wall_and_floor_thickness")?,
                            e.get("core")?.attr("carbonator_support_ring_height")?,
                        )?,
                    )?;
                    d.set(
                        Val::Str("slots".into()),
                        e.get("support")?.attr("slot_count")?,
                    )?;
                    d.set(
                        Val::Str("slot_angle".into()),
                        e.get("support")?.attr("slot_angular_width")?,
                    )?;
                    d.set(
                        Val::Str("slot_clock".into()),
                        e.get("support")?.attr("slot_clock")?,
                    )?;
                    d.set(
                        Val::Str("slot_margin".into()),
                        e.get("support")?.attr("slot_radial_margin")?,
                    )?;
                    d
                })?;
                d.set(
                    Val::Str("host_radius".into()),
                    binary(
                        "truediv",
                        e.get("core")?.attr("screw_guard_diameter")?,
                        Val::Float(2.0f64),
                    )?,
                )?;
                d.set(Val::Str("attachment_stations".into()), {
                    let e = e.child();
                    let out141 = Val::list(vec![]);
                    for item142 in e.get("core")?.attr("attachment_stations")?.iter()? {
                        let unpack143 = unpack(item142, 2)?;
                        e.set("xy", unpack143[0].clone())?;
                        e.set("wall", unpack143[1].clone())?;
                        out141.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                d.set(Val::Str("wall".into()), e.get("wall")?)?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out141
                })?;
                d.set(
                    Val::Str("insert_radius".into()),
                    e.get("core")?.attr("insert_pocket_radius")?,
                )?;
                d.set(
                    Val::Str("insert_depth".into()),
                    e.get("core")?.attr("insert_pocket_depth")?,
                )?;
                d.set(
                    Val::Str("tail_radius".into()),
                    e.get("core")?.attr("screw_clearance_radius")?,
                )?;
                d.set(
                    Val::Str("bottom_tail_depth".into()),
                    e.get("core")?.attr("bottom_screw_bore_depth")?,
                )?;
                d.set(
                    Val::Str("top_tail_depth".into()),
                    e.get("core")?.attr("top_screw_bore_depth")?,
                )?;
                d.set(Val::Str("bottom_tapers".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let d = Val::dict(vec![]);
                        d.set(
                            Val::Str("bottom".into()),
                            binary(
                                "add",
                                e.get("core")?.attr("insert_pocket_depth")?,
                                e.get("fits")?.attr("supported_surface")?,
                            )?,
                        )?;
                        d.set(
                            Val::Str("lower_radius".into()),
                            e.get("core")?.attr("insert_pocket_radius")?,
                        )?;
                        d.set(
                            Val::Str("upper_radius".into()),
                            e.get("core")?.attr("screw_clearance_radius")?,
                        )?;
                        d.set(
                            Val::Str("height".into()),
                            binary(
                                "mul",
                                Val::Float(2.0f64),
                                binary(
                                    "sub",
                                    e.get("core")?.attr("insert_pocket_radius")?,
                                    e.get("core")?.attr("screw_clearance_radius")?,
                                )?,
                            )?,
                        )?;
                        d
                    });
                    s.push({
                        let d = Val::dict(vec![]);
                        d.set(
                            Val::Str("bottom".into()),
                            binary(
                                "add",
                                e.get("core")?.attr("bottom_screw_bore_depth")?,
                                e.get("fits")?.attr("supported_surface")?,
                            )?,
                        )?;
                        d.set(
                            Val::Str("lower_radius".into()),
                            e.get("core")?.attr("screw_clearance_radius")?,
                        )?;
                        d.set(Val::Str("upper_radius".into()), Val::Float(0.0f64))?;
                        d.set(
                            Val::Str("height".into()),
                            binary(
                                "mul",
                                Val::Float(2.0f64),
                                e.get("core")?.attr("screw_clearance_radius")?,
                            )?,
                        )?;
                        d
                    });
                    Val::list(s)
                })?;
                d.set(
                    Val::Str("supported_surface".into()),
                    e.get("fits")?.attr("supported_surface")?,
                )?;
                d.set(
                    Val::Str("seam_depth".into()),
                    e.get("core")?.attr("seam_channel_depth")?,
                )?;
                d.set(
                    Val::Str("seam_width".into()),
                    e.get("core")?.attr("seam_channel_width")?,
                )?;
                d.set(Val::Str("reed_envelopes".into()), e.get("envelopes")?)?;
                d.set(Val::Str("reed_cavities".into()), e.get("cavities")?)?;
                d.set(Val::Str("reed_openings".into()), e.get("openings")?)?;
                d.set(Val::Str("reed_upper_backs".into()), e.get("upper_backs")?)?;
                d.set(Val::Str("reed_roofs".into()), e.get("roofs")?)?;
                d.set(Val::Str("reed_b_outlet".into()), {
                    let fun146 = e.get("outlet")?.attr("datums")?;
                    let mut args144 = Vec::new();
                    let mut kw145 = Vec::new();
                    fun146.call(args144, kw145)?
                })?;
                d.set(
                    Val::Str("vent_route".into()),
                    e.get("routes")?
                        .attr("routes")?
                        .get(Val::Str("prv-vent".into()))?,
                )?;
                d.set(
                    Val::Str("vent_bend".into()),
                    e.get("routes")?.attr("route_bend_radius")?,
                )?;
                d.set(
                    Val::Str("vent_radius".into()),
                    e.get("core")?.attr("port_hole_radius")?,
                )?;
                d.set(
                    Val::Str("copper_radius".into()),
                    e.get("copper_hole_radius")?,
                )?;
                d.set(Val::Str("copper_origins".into()), {
                    let e = e.child();
                    let out147 = Val::list(vec![]);
                    for item148 in {
                        let fun151 = {
                            let fun154 = e.get("stations")?;
                            let mut args152 = Vec::new();
                            let mut kw153 = Vec::new();
                            fun154.call(args152, kw153)?
                        }
                        .attr("values")?;
                        let mut args149 = Vec::new();
                        let mut kw150 = Vec::new();
                        fun151.call(args149, kw150)?
                    }
                    .iter()?
                    {
                        let unpack155 = unpack(item148, 2)?;
                        e.set("point", unpack155[0].clone())?;
                        e.set("_axis", unpack155[1].clone())?;
                        out147.attr("append")?.call(vec![e.get("point")?], vec![])?;
                    }
                    out147
                })?;
                d.set(Val::Str("copper_names".into()), {
                    let fun158 = e.get("list")?;
                    let mut args156 = Vec::new();
                    let mut kw157 = Vec::new();
                    args156.push({
                        let fun161 = e.get("stations")?;
                        let mut args159 = Vec::new();
                        let mut kw160 = Vec::new();
                        fun161.call(args159, kw160)?
                    });
                    fun158.call(args156, kw157)?
                })?;
                d.set(Val::Str("b_fill".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("bend_radius".into()),
                        e.get("b_fill")?.attr("BEND_RADIUS")?,
                    )?;
                    d.set(
                        Val::Str("channel_centre".into()),
                        e.get("b_fill")?.attr("CHANNEL_CENTRE")?,
                    )?;
                    d.set(
                        Val::Str("channel_radius".into()),
                        e.get("b_fill")?.attr("CHANNEL_RADIUS")?,
                    )?;
                    d.set(Val::Str("mouth".into()), e.get("b_fill")?.attr("MOUTH")?)?;
                    d.set(
                        Val::Str("mouth_start_y".into()),
                        unary("neg", Val::Float(0.3f64))?,
                    )?;
                    d.set(
                        Val::Str("mouth_end_y".into()),
                        binary("add", e.get("b_fill")?.attr("MOUTH")?, Val::Float(0.05f64))?,
                    )?;
                    d.set(
                        Val::Str("mouth_start_radius".into()),
                        binary(
                            "add",
                            binary(
                                "add",
                                e.get("b_fill")?.attr("CHANNEL_RADIUS")?,
                                e.get("b_fill")?.attr("MOUTH")?,
                            )?,
                            Val::Float(0.3f64),
                        )?,
                    )?;
                    d.set(
                        Val::Str("mouth_end_radius".into()),
                        binary(
                            "sub",
                            e.get("b_fill")?.attr("CHANNEL_RADIUS")?,
                            Val::Float(0.05f64),
                        )?,
                    )?;
                    d.set(
                        Val::Str("inlet_leg".into()),
                        binary(
                            "sub",
                            binary(
                                "sub",
                                e.get("b_end")?.get(Val::Int(1i64))?,
                                e.get("b_fill")?.attr("BEND_RADIUS")?,
                            )?,
                            e.get("b_passage")?
                                .get(Val::Str("entry_world_mm".into()))?
                                .get(Val::Int(1i64))?,
                        )?,
                    )?;
                    d.set(Val::Str("bend_end_world".into()), e.get("b_end")?)?;
                    d.set(
                        Val::Str("roof_allowance".into()),
                        e.get("b_passage")?
                            .get(Val::Str("supported_roof_allowance_mm".into()))?,
                    )?;
                    d.set(Val::Str("world_to_shell_origin".into()), e.get("origin")?)?;
                    d.set(Val::Str("world_to_shell_axes".into()), e.get("axes")?)?;
                    d
                })?;
                d.set(Val::Str("color".into()), {
                    let fun164 = e.get("list")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    args162.push({
                        let fun167 = e.get("linear")?;
                        let mut args165 = Vec::new();
                        let mut kw166 = Vec::new();
                        args165.push(e.get("C_FOAM_SHELL")?);
                        fun167.call(args165, kw166)?
                    });
                    fun164.call(args162, kw163)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // update_readme
    e.set("update_readme", {
        let params = vec![
            ("output".into(), None, false),
            ("volume".into(), None, false),
            ("bbox".into(), None, false),
            ("centroid".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
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
            let assigned314 = {
                let fun317 = e.get("Path")?;
                let mut args315 = Vec::new();
                let mut kw316 = Vec::new();
                args315.push(e.get("output")?);
                fun317.call(args315, kw316)?
            };
            e.set("output", assigned314.clone())?;
            {
                let fun320 = e.get("output")?.attr("mkdir")?;
                let mut args318 = Vec::new();
                let mut kw319 = Vec::new();
                kw319.push(("parents".into(), Val::Bool(true)));
                kw319.push(("exist_ok".into(), Val::Bool(true)));
                fun320.call(args318, kw319)?
            };
            let assigned321 = {
                let fun324 = e.get("_rust_part")?.attr("cut")?;
                let mut args322 = Vec::new();
                let mut kw323 = Vec::new();
                args322.push(Val::Str("cold-core".into()));
                args322.push(Val::Str("foam-shell".into()));
                args322.push({
                    let fun327 = e.get("numbers")?;
                    let mut args325 = Vec::new();
                    let mut kw326 = Vec::new();
                    fun327.call(args325, kw326)?
                });
                args322.push(e.get("output")?);
                fun324.call(args322, kw323)?
            }
            .get(Val::Str("bodies".into()))?
            .get(Val::Int(0i64))?;
            e.set("readings", assigned321.clone())?;
            let assigned328 = e.get("readings")?.get(Val::Str("front_ports".into()))?;
            e.set("ports", assigned328.clone())?;
            {
                let fun331 = e.get("print")?;
                let mut args329 = Vec::new();
                let mut kw330 = Vec::new();
                args329.push(binary(
                    "add",
                    {
                        let mut str332 = String::new();
                        str332.push_str("  front face:       ");
                        str332.push_str(&format(
                            &{
                                let fun335 = e.get("len")?;
                                let mut args333 = Vec::new();
                                let mut kw334 = Vec::new();
                                args333.push(e.get("ports")?);
                                fun335.call(args333, kw334)?
                            },
                            &String::new(),
                        )?);
                        str332.push_str(" stations on x ");
                        str332.push_str(&format(
                            &e.get("front_wall_x")?,
                            &val_string({
                                let mut str336 = String::new();
                                str336.push_str(".4g");
                                Val::Str(str336)
                            })?,
                        )?);
                        str332.push_str(", all open — ");
                        Val::Str(str332)
                    },
                    {
                        let fun339 = Val::Str(", ".into()).attr("join")?;
                        let mut args337 = Vec::new();
                        let mut kw338 = Vec::new();
                        args337.push({
                            let e = e.child();
                            let out340 = Val::list(vec![]);
                            for item341 in e.get("ports")?.iter()? {
                                e.set("p", item341)?;
                                out340.attr("append")?.call(
                                    vec![{
                                        let mut str342 = String::new();
                                        str342.push_str(&format(
                                            &e.get("p")?.get(Val::Str("name".into()))?,
                                            &String::new(),
                                        )?);
                                        str342.push_str(" y ");
                                        str342.push_str(&format(
                                            &e.get("p")?
                                                .get(Val::Str("origin".into()))?
                                                .get(Val::Int(1i64))?,
                                            &val_string({
                                                let mut str343 = String::new();
                                                str343.push_str(".4g");
                                                Val::Str(str343)
                                            })?,
                                        )?);
                                        str342.push_str(" z ");
                                        str342.push_str(&format(
                                            &e.get("p")?
                                                .get(Val::Str("origin".into()))?
                                                .get(Val::Int(2i64))?,
                                            &val_string({
                                                let mut str344 = String::new();
                                                str344.push_str(".4g");
                                                Val::Str(str344)
                                            })?,
                                        )?);
                                        Val::Str(str342)
                                    }],
                                    vec![],
                                )?;
                            }
                            out340
                        });
                        fun339.call(args337, kw338)?
                    },
                )?);
                fun331.call(args329, kw330)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun347 = e.get("_rust_part")?.attr("start")?;
        let mut args345 = Vec::new();
        let mut kw346 = Vec::new();
        fun347.call(args345, kw346)?
    };
    let assigned348 = {
        let fun351 = e.get("argparse")?.attr("ArgumentParser")?;
        let mut args349 = Vec::new();
        let mut kw350 = Vec::new();
        kw350.push(("description".into(), e.get("__doc__")?));
        fun351.call(args349, kw350)?
    };
    e.set("parser", assigned348.clone())?;
    {
        let fun354 = e.get("parser")?.attr("add_argument")?;
        let mut args352 = Vec::new();
        let mut kw353 = Vec::new();
        args352.push(Val::Str("--output".into()));
        kw353.push(("type".into(), e.get("Path")?));
        kw353.push(("default".into(), e.get("_here")?));
        fun354.call(args352, kw353)?
    };
    let assigned355 = {
        let fun358 = e.get("parser")?.attr("parse_args")?;
        let mut args356 = Vec::new();
        let mut kw357 = Vec::new();
        fun358.call(args356, kw357)?
    };
    e.set("args", assigned355.clone())?;
    {
        let fun361 = e.get("main")?;
        let mut args359 = Vec::new();
        let mut kw360 = Vec::new();
        args359.push(e.get("args")?.attr("output")?);
        fun361.call(args359, kw360)?
    };
    Ok(Val::None)
}
