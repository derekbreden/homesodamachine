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
    let assigned9 = {
        let fun12 = e.get("next")?;
        let mut args10 = Vec::new();
        let mut kw11 = Vec::new();
        args10.push({
            let e = e.child();
            let out13 = Val::list(vec![]);
            for item14 in e.get("_here")?.attr("parents")?.iter()? {
                e.set("p", item14)?;
                if {
                    let v15 = e.get("p")?.attr("name")?;
                    let v16 = Val::Str("printed-parts".into());
                    Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out13.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out13
        });
        fun12.call(args10, kw11)?
    };
    e.set("_printed", assigned9.clone())?;
    {
        let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args17 = Vec::new();
        let mut kw18 = Vec::new();
        args17.push(Val::Int(0i64));
        args17.push({
            let fun22 = e.get("str")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(binary(
                "truediv",
                e.get("_printed")?,
                Val::Str("cadlib".into()),
            )?);
            fun22.call(args20, kw21)?
        });
        fun19.call(args17, kw18)?
    };
    {
        let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args23 = Vec::new();
        let mut kw24 = Vec::new();
        args23.push(Val::Int(0i64));
        args23.push({
            let fun28 = e.get("str")?;
            let mut args26 = Vec::new();
            let mut kw27 = Vec::new();
            args26.push(binary(
                "truediv",
                {
                    let fun31 = e.get("next")?;
                    let mut args29 = Vec::new();
                    let mut kw30 = Vec::new();
                    args29.push({
                        let e = e.child();
                        let out32 = Val::list(vec![]);
                        for item33 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item33)?;
                            if {
                                let v34 = e.get("p")?.attr("name")?;
                                let v35 = Val::Str("hardware".into());
                                Val::Bool(compare("eq", v34.clone(), v35.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out32.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out32
                    });
                    fun31.call(args29, kw30)?
                },
                Val::Str("scripts".into()),
            )?);
            fun28.call(args26, kw27)?
        });
        fun25.call(args23, kw24)?
    };
    {
        let fun38 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args36 = Vec::new();
        let mut kw37 = Vec::new();
        args36.push(Val::Int(0i64));
        args36.push({
            let fun41 = e.get("str")?;
            let mut args39 = Vec::new();
            let mut kw40 = Vec::new();
            args39.push(e.get("_here")?.attr("parent")?);
            fun41.call(args39, kw40)?
        });
        fun38.call(args36, kw37)?
    };
    {
        let fun44 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args42 = Vec::new();
        let mut kw43 = Vec::new();
        args42.push(Val::Int(0i64));
        args42.push({
            let fun47 = e.get("str")?;
            let mut args45 = Vec::new();
            let mut kw46 = Vec::new();
            args45.push(binary(
                "truediv",
                e.get("_printed")?,
                Val::Str("valve-seat".into()),
            )?);
            fun47.call(args45, kw46)?
        });
        fun44.call(args42, kw43)?
    };
    {
        let fun50 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args48 = Vec::new();
        let mut kw49 = Vec::new();
        args48.push(Val::Int(0i64));
        args48.push({
            let fun53 = e.get("str")?;
            let mut args51 = Vec::new();
            let mut kw52 = Vec::new();
            args51.push(binary(
                "truediv",
                {
                    let fun56 = e.get("next")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    args54.push({
                        let e = e.child();
                        let out57 = Val::list(vec![]);
                        for item58 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item58)?;
                            if {
                                let fun61 = binary(
                                    "truediv",
                                    binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                    Val::Str("docgen".into()),
                                )?
                                .attr("is_dir")?;
                                let mut args59 = Vec::new();
                                let mut kw60 = Vec::new();
                                fun61.call(args59, kw60)?
                            }
                            .truthy()?
                            {
                                out57.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out57
                    });
                    fun56.call(args54, kw55)?
                },
                Val::Str("tools".into()),
            )?);
            fun53.call(args51, kw52)?
        });
        fun50.call(args48, kw49)?
    };
    e.set("fits", rt.import_module("fits")?)?;
    e.set("_mat", rt.import_module("_materials")?)?;
    e.set("seat", rt.import_module("valve_seat")?)?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    e.set("_a_anchors", rt.import_module("_reservoir_a_anchors")?)?;
    e.set("above_core_wiring", rt.import_module("above_core_wiring")?)?;
    e.set("reservoir_ports", rt.import_module("_reservoir_ports")?)?;
    e.set("_reservoir_b_fill", rt.import_module("_reservoir_b_fill")?)?;
    let mod62 = rt.import_module("_foam_cap")?;
    e.set(
        "head_pad_growth",
        rt.member("_foam_cap", "head_pad_growth")?,
    )?;
    e.set(
        "lid_cut_through_depth",
        rt.member("_foam_cap", "lid_cut_through_depth")?,
    )?;
    e.set(
        "lid_total_height",
        rt.member("_foam_cap", "lid_total_height")?,
    )?;
    e.set("top_cap_height", rt.member("_foam_cap", "top_cap_height")?)?;
    let mod63 = rt.import_module("_cold_core_interface")?;
    e.set(
        "cap_conduit_links",
        rt.member("_cold_core_interface", "cap_conduit_links")?,
    )?;
    e.set(
        "cap_conduit_link_width",
        rt.member("_cold_core_interface", "cap_conduit_link_width")?,
    )?;
    let mod64 = rt.import_module("_cold_core_interface")?;
    e.set(
        "attachment_xy_positions",
        rt.member("_cold_core_interface", "attachment_xy_positions")?,
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
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "corner_round_radius",
        rt.member("_cold_core_interface", "corner_round_radius")?,
    )?;
    e.set(
        "foam_cap_lid_pour_radius",
        rt.member("_cold_core_interface", "foam_cap_lid_pour_radius")?,
    )?;
    e.set(
        "foam_cap_lid_pour_xy",
        rt.member("_cold_core_interface", "foam_cap_lid_pour_xy")?,
    )?;
    e.set(
        "foam_cap_lid_vent_radius",
        rt.member("_cold_core_interface", "foam_cap_lid_vent_radius")?,
    )?;
    e.set(
        "foam_cap_lid_vent_xy",
        rt.member("_cold_core_interface", "foam_cap_lid_vent_xy")?,
    )?;
    e.set(
        "head_pad_height",
        rt.member("_cold_core_interface", "head_pad_height")?,
    )?;
    e.set(
        "screw_clearance_radius",
        rt.member("_cold_core_interface", "screw_clearance_radius")?,
    )?;
    e.set(
        "head_cbore_radius",
        rt.member("_cold_core_interface", "head_cbore_radius")?,
    )?;
    e.set(
        "head_cbore_depth",
        rt.member("_cold_core_interface", "head_cbore_depth")?,
    )?;
    e.set(
        "deck_mounts",
        rt.member("_cold_core_interface", "deck_mounts")?,
    )?;
    e.set(
        "deck_mount_cap_gap",
        rt.member("_cold_core_interface", "deck_mount_cap_gap")?,
    )?;
    e.set(
        "deck_mount_xy",
        rt.member("_cold_core_interface", "deck_mount_xy")?,
    )?;
    e.set(
        "deck_mount_boss_radius",
        rt.member("_cold_core_interface", "deck_mount_boss_radius")?,
    )?;
    e.set(
        "deck_mount_bore_radius",
        rt.member("_cold_core_interface", "deck_mount_bore_radius")?,
    )?;
    e.set(
        "deck_mount_bore_depth",
        rt.member("_cold_core_interface", "deck_mount_bore_depth")?,
    )?;
    e.set(
        "deck_mount_standoff",
        rt.member("_cold_core_interface", "deck_mount_standoff")?,
    )?;
    e.set(
        "deck_lid_hole_radius",
        rt.member("_cold_core_interface", "deck_lid_hole_radius")?,
    )?;
    e.set(
        "cap_conduits",
        rt.member("_cold_core_interface", "cap_conduits")?,
    )?;
    e.set(
        "cap_conduit_bore_radius",
        rt.member("_cold_core_interface", "cap_conduit_bore_radius")?,
    )?;
    e.set(
        "cap_conduit_boss_radius",
        rt.member("_cold_core_interface", "cap_conduit_boss_radius")?,
    )?;
    e.set(
        "cap_conduit_entry_relief_radius",
        rt.member("_cold_core_interface", "cap_conduit_entry_relief_radius")?,
    )?;
    e.set(
        "cap_cradles",
        rt.member("_cold_core_interface", "cap_cradles")?,
    )?;
    e.set(
        "cap_cradle_boss_radius",
        rt.member("_cold_core_interface", "cap_cradle_boss_radius")?,
    )?;
    e.set(
        "cap_cradle_socket_radius",
        rt.member("_cold_core_interface", "cap_cradle_socket_radius")?,
    )?;
    e.set(
        "cap_cradle_wall",
        rt.member("_cold_core_interface", "cap_cradle_wall")?,
    )?;
    e.set(
        "cap_cradle_room_gap",
        rt.member("_cold_core_interface", "cap_cradle_room_gap")?,
    )?;
    e.set(
        "cap_cradle_half_x",
        rt.member("_cold_core_interface", "cap_cradle_half_x")?,
    )?;
    e.set(
        "cap_cradle_half_y",
        rt.member("_cold_core_interface", "cap_cradle_half_y")?,
    )?;
    e.set(
        "cap_anchors",
        rt.member("_cold_core_interface", "cap_anchors")?,
    )?;
    e.set(
        "cap_anchor_axis_over_face",
        rt.member("_cold_core_interface", "cap_anchor_axis_over_face")?,
    )?;
    e.set(
        "cap_side_anchors",
        rt.member("_cold_core_interface", "cap_side_anchors")?,
    )?;
    e.set(
        "cap_side_anchor_height",
        rt.member("_cold_core_interface", "cap_side_anchor_height")?,
    )?;
    e.set(
        "cap_side_anchor_holds",
        rt.member("_cold_core_interface", "cap_side_anchor_holds")?,
    )?;
    e.set(
        "cap_side_axis_y",
        rt.member("_cold_core_interface", "cap_side_axis_y")?,
    )?;
    e.set(
        "cap_side_tunnel_h",
        rt.member("_cold_core_interface", "cap_side_tunnel_h")?,
    )?;
    e.set(
        "cap_side_tunnel_roof",
        rt.member("_cold_core_interface", "cap_side_tunnel_roof")?,
    )?;
    e.set(
        "cap_side_back_relief",
        rt.member("_cold_core_interface", "cap_side_back_relief")?,
    )?;
    e.set(
        "cap_side_cav_w",
        rt.member("_cold_core_interface", "cap_side_cav_w")?,
    )?;
    e.set(
        "cap_side_flank",
        rt.member("_cold_core_interface", "cap_side_flank")?,
    )?;
    e.set(
        "cap_side_len",
        rt.member("_cold_core_interface", "cap_side_len")?,
    )?;
    e.set(
        "cap_side_wall",
        rt.member("_cold_core_interface", "cap_side_wall")?,
    )?;
    e.set(
        "cap_anchor_cav_w",
        rt.member("_cold_core_interface", "cap_anchor_cav_w")?,
    )?;
    e.set(
        "cap_anchor_cav_wall",
        rt.member("_cold_core_interface", "cap_anchor_cav_wall")?,
    )?;
    e.set(
        "cap_anchor_len",
        rt.member("_cold_core_interface", "cap_anchor_len")?,
    )?;
    e.set(
        "cap_anchor_wall",
        rt.member("_cold_core_interface", "cap_anchor_wall")?,
    )?;
    e.set(
        "cap_anchor_channel_height",
        rt.member("_cold_core_interface", "cap_anchor_channel_height")?,
    )?;
    e.set(
        "outer_shell_wall",
        rt.member("_cold_core_interface", "outer_shell_wall")?,
    )?;
    e.set(
        "outer_shell_x_length",
        rt.member("_cold_core_interface", "outer_shell_x_length")?,
    )?;
    e.set(
        "outer_shell_y_length",
        rt.member("_cold_core_interface", "outer_shell_y_length")?,
    )?;
    // deck_boss_z_top
    e.set("deck_boss_z_top", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary("add", e.get("lid_total_height")?, {
                let fun68 = e.get("deck_mount_standoff")?;
                let mut args66 = Vec::new();
                let mut kw67 = Vec::new();
                args66.push(e.get("name")?);
                fun68.call(args66, kw67)?
            })?);
            Ok(Val::None)
        })
    })?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("itertools", rt.import_module("itertools")?)?;
            e.set("core", rt.import_module("_cold_core_interface")?)?;
            e.set("a_snap", rt.import_module("_reservoir_a_c2")?)?;
            e.set("above_core_routes", rt.import_module("above_core_routes")?)?;
            e.set("rear_snaps", rt.import_module("rear_snaps")?)?;
            let mod69 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            let assigned70 = {
                let fun73 = e.get("next")?;
                let mut args71 = Vec::new();
                let mut kw72 = Vec::new();
                args71.push({
                    let e = e.child();
                    let out74 = Val::list(vec![]);
                    for item75 in e.get("_here")?.attr("parents")?.iter()? {
                        e.set("p", item75)?;
                        if {
                            let fun78 =
                                binary("truediv", e.get("p")?, Val::Str("hardware".into()))?
                                    .attr("is_dir")?;
                            let mut args76 = Vec::new();
                            let mut kw77 = Vec::new();
                            fun78.call(args76, kw77)?
                        }
                        .truthy()?
                        {
                            out74.attr("append")?.call(vec![e.get("p")?], vec![])?;
                        }
                    }
                    out74
                });
                fun73.call(args71, kw72)?
            };
            e.set("root", assigned70.clone())?;
            {
                let fun81 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                args79.push(Val::Int(0i64));
                args79.push({
                    let fun84 = e.get("str")?;
                    let mut args82 = Vec::new();
                    let mut kw83 = Vec::new();
                    args82.push(e.get("root")?);
                    fun84.call(args82, kw83)?
                });
                fun81.call(args79, kw80)?
            };
            let mod85 = rt.import_module("hardware.wiring.installed.retainers")?;
            e.set(
                "manifold_bank_site",
                rt.member("hardware.wiring.installed.retainers", "manifold_bank_site")?,
            )?;
            e.set(
                "rear_level_hook_site",
                rt.member(
                    "hardware.wiring.installed.retainers",
                    "rear_level_hook_site",
                )?,
            )?;
            let assigned86 = e.get("_above_mounts")?.attr("above_core")?;
            e.set("layout", assigned86.clone())?;
            let assigned87 = {
                let fun90 = e.get("layout")?.attr("cap_lid_pose")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                fun90.call(args88, kw89)?
            };
            e.set("pose", assigned87.clone())?;
            let assigned91 = {
                let fun94 = e.get("layout")?.attr("world_to_cap")?;
                let mut args92 = Vec::new();
                let mut kw93 = Vec::new();
                args92.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun94.call(args92, kw93)?
            };
            e.set("world_origin", assigned91.clone())?;
            let assigned95 = {
                let e = e.child();
                let out96 = Val::list(vec![]);
                for item97 in {
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
                    e.set("axis", item97)?;
                    out96.attr("append")?.call(
                        vec![{
                            let fun100 = e.get("tuple")?;
                            let mut args98 = Vec::new();
                            let mut kw99 = Vec::new();
                            args98.push({
                                let e = e.child();
                                let out101 = Val::list(vec![]);
                                for item102 in {
                                    let fun105 = e.get("zip")?;
                                    let mut args103 = Vec::new();
                                    let mut kw104 = Vec::new();
                                    args103.push(e.get("world_origin")?);
                                    args103.push({
                                        let fun108 = e.get("layout")?.attr("world_to_cap")?;
                                        let mut args106 = Vec::new();
                                        let mut kw107 = Vec::new();
                                        args106.push(e.get("axis")?);
                                        fun108.call(args106, kw107)?
                                    });
                                    fun105.call(args103, kw104)?
                                }
                                .iter()?
                                {
                                    let unpack109 = unpack(item102, 2)?;
                                    e.set("a", unpack109[0].clone())?;
                                    e.set("b", unpack109[1].clone())?;
                                    out101.attr("append")?.call(
                                        vec![binary("sub", e.get("b")?, e.get("a")?)?],
                                        vec![],
                                    )?;
                                }
                                out101
                            });
                            fun100.call(args98, kw99)?
                        }],
                        vec![],
                    )?;
                }
                out96
            };
            e.set("world_axes", assigned95.clone())?;
            let assigned110 = {
                let fun113 = e.get("_above_mounts")?.attr("pump_cradle_datums")?;
                let mut args111 = Vec::new();
                let mut kw112 = Vec::new();
                fun113.call(args111, kw112)?
            };
            e.set("pump", assigned110.clone())?;
            let assigned114 = {
                let fun117 = e.get("_reservoir_b_fill")?.attr("passage")?;
                let mut args115 = Vec::new();
                let mut kw116 = Vec::new();
                fun117.call(args115, kw116)?
            };
            e.set("b_fill", assigned114.clone())?;
            let assigned118 = e.get("_reservoir_b_fill")?.attr("CHANNEL_RADIUS")?;
            e.set("r", assigned118.clone())?;
            let assigned119 = e.get("_reservoir_b_fill")?.attr("CHANNEL_CENTRE")?;
            e.set("centre", assigned119.clone())?;
            let assigned120 = binary(
                "add",
                e.get("r")?,
                e.get("_reservoir_b_fill")?.attr("WALL")?,
            )?;
            e.set("outer", assigned120.clone())?;
            let assigned121 = binary(
                "add",
                binary(
                    "add",
                    e.get("centre")?,
                    e.get("_reservoir_b_fill")?.attr("DOME_LIFT")?,
                )?,
                e.get("outer")?,
            )?;
            e.set("height", assigned121.clone())?;
            let assigned122 = e.get("b_fill")?.get(Val::Str("bend_end_world_mm".into()))?;
            let unpack123 = unpack(assigned122.clone(), 3)?;
            e.set("x", unpack123[0].clone())?;
            e.set("y", unpack123[1].clone())?;
            e.set("z", unpack123[2].clone())?;
            let assigned124 = e.get("_reservoir_b_fill")?.attr("BEND_RADIUS")?;
            e.set("bend", assigned124.clone())?;
            let assigned125 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        binary("add", e.get("x")?, e.get("centre")?)?,
                        e.get("height")?,
                    )?);
                    s.push(binary("add", e.get("x")?, e.get("centre")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("y")?, e.get("bend")?)?);
                    s.push(binary("add", e.get("y")?, e.get("outer")?)?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        binary("add", e.get("z")?, e.get("bend")?)?,
                        e.get("outer")?,
                    )?);
                    s.push(binary(
                        "add",
                        binary("add", e.get("z")?, e.get("bend")?)?,
                        e.get("outer")?,
                    )?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            };
            e.set("guide_world_bounds", assigned125.clone())?;
            let assigned126 = {
                let e = e.child();
                let out127 = Val::list(vec![]);
                for item128 in {
                    let fun131 = e.get("itertools")?.attr("product")?;
                    let mut args129 = Vec::new();
                    let mut kw130 = Vec::new();
                    args129.extend(e.get("guide_world_bounds")?.iter()?);
                    fun131.call(args129, kw130)?
                }
                .iter()?
                {
                    e.set("p", item128)?;
                    out127.attr("append")?.call(
                        vec![{
                            let fun134 = e.get("layout")?.attr("world_to_cap")?;
                            let mut args132 = Vec::new();
                            let mut kw133 = Vec::new();
                            args132.push(e.get("p")?);
                            fun134.call(args132, kw133)?
                        }],
                        vec![],
                    )?;
                }
                out127
            };
            e.set("corners", assigned126.clone())?;
            let assigned135 = {
                let mut s = Vec::new();
                s.push({
                    let e = e.child();
                    let out136 = Val::list(vec![]);
                    for item137 in {
                        let fun140 = e.get("range")?;
                        let mut args138 = Vec::new();
                        let mut kw139 = Vec::new();
                        args138.push(Val::Int(3i64));
                        fun140.call(args138, kw139)?
                    }
                    .iter()?
                    {
                        e.set("i", item137)?;
                        out136.attr("append")?.call(
                            vec![{
                                let fun143 = e.get("min")?;
                                let mut args141 = Vec::new();
                                let mut kw142 = Vec::new();
                                args141.push({
                                    let e = e.child();
                                    let out144 = Val::list(vec![]);
                                    for item145 in e.get("corners")?.iter()? {
                                        e.set("p", item145)?;
                                        out144
                                            .attr("append")?
                                            .call(vec![e.get("p")?.get(e.get("i")?)?], vec![])?;
                                    }
                                    out144
                                });
                                fun143.call(args141, kw142)?
                            }],
                            vec![],
                        )?;
                    }
                    out136
                });
                s.push({
                    let e = e.child();
                    let out146 = Val::list(vec![]);
                    for item147 in {
                        let fun150 = e.get("range")?;
                        let mut args148 = Vec::new();
                        let mut kw149 = Vec::new();
                        args148.push(Val::Int(3i64));
                        fun150.call(args148, kw149)?
                    }
                    .iter()?
                    {
                        e.set("i", item147)?;
                        out146.attr("append")?.call(
                            vec![{
                                let fun153 = e.get("max")?;
                                let mut args151 = Vec::new();
                                let mut kw152 = Vec::new();
                                args151.push({
                                    let e = e.child();
                                    let out154 = Val::list(vec![]);
                                    for item155 in e.get("corners")?.iter()? {
                                        e.set("p", item155)?;
                                        out154
                                            .attr("append")?
                                            .call(vec![e.get("p")?.get(e.get("i")?)?], vec![])?;
                                    }
                                    out154
                                });
                                fun153.call(args151, kw152)?
                            }],
                            vec![],
                        )?;
                    }
                    out146
                });
                Val::list(s)
            };
            e.set("guide_bounds", assigned135.clone())?;
            let assigned156 = {
                let fun159 = e.get("layout")?.attr("specification")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                fun159.call(args157, kw158)?
            };
            e.set("spec", assigned156.clone())?;
            let assigned160 = e
                .get("spec")?
                .get(Val::Str("fore_routes".into()))?
                .get(Val::Str("va_feed_snap".into()))?;
            e.set("va", assigned160.clone())?;
            let assigned161 = {
                let mut s = Vec::new();
                s.push({
                    let fun164 = e.get("dict")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    kw163.push((
                        "centre".into(),
                        e.get("va")?.get(Val::Str("centre_world_mm".into()))?,
                    ));
                    kw163.push((
                        "along".into(),
                        e.get("va")?.get(Val::Str("along_world".into()))?,
                    ));
                    kw163.push((
                        "radius".into(),
                        binary("truediv", Val::Float(6.35f64), Val::Float(2.0f64))?,
                    ));
                    kw163.push(("wing".into(), Val::Float(2.4f64)));
                    kw163.push(("span".into(), Val::Float(8.0f64)));
                    kw163.push(("tip_degrees".into(), Val::Float(125.42102606277044f64)));
                    fun164.call(args162, kw163)?
                });
                Val::list(s)
            };
            e.set("clips", assigned161.clone())?;
            e.set(
                "clips",
                binary("add", e.get("clips")?, {
                    let e = e.child();
                    let out165 = Val::list(vec![]);
                    for item166 in {
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(26.5f64));
                                s.push(Val::Float(266.0f64));
                                s.push(Val::Float(296.0f64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(0.0f64));
                                Val::tuple(s)
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(35.0f64));
                                s.push(Val::Float(414.0f64));
                                s.push(Val::Float(264.0f64));
                                Val::tuple(s)
                            });
                            s.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(1.0f64));
                                s.push(Val::Float(0.0f64));
                                Val::tuple(s)
                            });
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        let unpack167 = unpack(item166, 2)?;
                        e.set("p", unpack167[0].clone())?;
                        e.set("u", unpack167[1].clone())?;
                        out165.attr("append")?.call(
                            vec![{
                                let fun170 = e.get("dict")?;
                                let mut args168 = Vec::new();
                                let mut kw169 = Vec::new();
                                kw169.push(("centre".into(), e.get("p")?));
                                kw169.push(("along".into(), e.get("u")?));
                                kw169.push((
                                    "radius".into(),
                                    binary("truediv", Val::Float(4.1f64), Val::Float(2.0f64))?,
                                ));
                                kw169.push(("wing".into(), Val::Float(1.52f64)));
                                kw169.push(("span".into(), Val::Float(8.0f64)));
                                kw169.push((
                                    "tip_degrees".into(),
                                    Val::Float(125.42102606277044f64),
                                ));
                                fun170.call(args168, kw169)?
                            }],
                            vec![],
                        )?;
                    }
                    out165
                })?,
            )?;
            let assigned171 = {
                let fun174 = e.get("a_snap")?.attr("specification")?;
                let mut args172 = Vec::new();
                let mut kw173 = Vec::new();
                fun174.call(args172, kw173)?
            };
            e.set("a_spec", assigned171.clone())?;
            e.set(
                "clips",
                binary("add", e.get("clips")?, {
                    let e = e.child();
                    let out175 = Val::list(vec![]);
                    for item176 in e
                        .get("a_spec")?
                        .get(Val::Str("tube_centers_world_mm".into()))?
                        .iter()?
                    {
                        e.set("p", item176)?;
                        out175.attr("append")?.call(
                            vec![{
                                let fun179 = e.get("dict")?;
                                let mut args177 = Vec::new();
                                let mut kw178 = Vec::new();
                                kw178.push(("centre".into(), e.get("p")?));
                                kw178.push((
                                    "along".into(),
                                    e.get("a_spec")?.get(Val::Str("tube_axis_world".into()))?,
                                ));
                                kw178.push((
                                    "radius".into(),
                                    e.get("a_spec")?.get(Val::Str("seat_radius_mm".into()))?,
                                ));
                                kw178.push((
                                    "wing".into(),
                                    e.get("a_spec")?
                                        .get(Val::Str("spring_thickness_mm".into()))?,
                                ));
                                kw178.push((
                                    "span".into(),
                                    e.get("a_spec")?.get(Val::Str("station_length_mm".into()))?,
                                ));
                                kw178.push((
                                    "tip_degrees".into(),
                                    e.get("a_spec")?.get(Val::Str("tip_degrees".into()))?,
                                ));
                                fun179.call(args177, kw178)?
                            }],
                            vec![],
                        )?;
                    }
                    out175
                })?,
            )?;
            let assigned180 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("wells", assigned180.clone())?;
            for item181 in {
                let fun192 = {
                    let fun195 = e.get("above_core_wiring")?.attr("placements")?;
                    let mut args193 = Vec::new();
                    let mut kw194 = Vec::new();
                    fun195.call(args193, kw194)?
                }
                .attr("items")?;
                let mut args190 = Vec::new();
                let mut kw191 = Vec::new();
                fun192.call(args190, kw191)?
            }
            .iter()?
            {
                let unpack196 = unpack(item181, 2)?;
                e.set("name", unpack196[0].clone())?;
                e.set("placement", unpack196[1].clone())?;
                if {
                    let v182 = e.get("placement")?.get(Val::Str("parent".into()))?;
                    let v183 = Val::Str("cold-core".into());
                    Val::Bool(compare("ne", v182.clone(), v183.clone())?.truthy()?)
                }
                .truthy()?
                {
                    continue;
                }
                {
                    let fun186 = e.get("wells")?.attr("append")?;
                    let mut args184 = Vec::new();
                    let mut kw185 = Vec::new();
                    args184.push({
                        let fun189 = e.get("dict")?;
                        let mut args187 = Vec::new();
                        let mut kw188 = Vec::new();
                        kw188.push(("name".into(), e.get("name")?));
                        kw188.push(("pose".into(), e.get("placement")?));
                        kw188.push((
                            "size".into(),
                            e.get("above_core_wiring")?
                                .attr("SIZES")?
                                .get(e.get("placement")?.get(Val::Str("size".into()))?)?,
                        ));
                        fun189.call(args187, kw188)?
                    });
                    fun186.call(args184, kw185)?
                };
            }
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("width".into()),
                    e.get("core")?.attr("outer_shell_x_length")?,
                )?;
                d.set(
                    Val::Str("depth".into()),
                    e.get("core")?.attr("outer_shell_y_length")?,
                )?;
                d.set(
                    Val::Str("corner".into()),
                    e.get("core")?.attr("corner_round_radius")?,
                )?;
                d.set(
                    Val::Str("wall".into()),
                    e.get("core")?.attr("outer_shell_wall")?,
                )?;
                d.set(
                    Val::Str("floor".into()),
                    e.get("core")?.attr("wall_and_floor_thickness")?,
                )?;
                d.set(Val::Str("lid_height".into()), e.get("lid_total_height")?)?;
                d.set(
                    Val::Str("bottom_height".into()),
                    e.get("core")?.attr("bottom_cap_height")?,
                )?;
                d.set(
                    Val::Str("head_radius".into()),
                    e.get("core")?.attr("head_cbore_radius")?,
                )?;
                d.set(
                    Val::Str("head_depth".into()),
                    e.get("core")?.attr("head_cbore_depth")?,
                )?;
                d.set(
                    Val::Str("screw_radius".into()),
                    e.get("core")?.attr("screw_clearance_radius")?,
                )?;
                d.set(
                    Val::Str("boss_radius".into()),
                    binary(
                        "truediv",
                        e.get("core")?.attr("screw_boss_size")?,
                        Val::Float(2.0f64),
                    )?,
                )?;
                d.set(
                    Val::Str("head_pad_growth".into()),
                    e.get("head_pad_growth")?,
                )?;
                d.set(
                    Val::Str("supported_surface".into()),
                    e.get("fits")?.attr("supported_surface")?,
                )?;
                d.set(Val::Str("running".into()), e.get("fits")?.attr("running")?)?;
                d.set(Val::Str("slip".into()), e.get("fits")?.attr("slip")?)?;
                d.set(Val::Str("bottom_stations".into()), {
                    let e = e.child();
                    let out197 = Val::list(vec![]);
                    for item198 in e.get("core")?.attr("attachment_stations")?.iter()? {
                        let unpack199 = unpack(item198, 2)?;
                        e.set("xy", unpack199[0].clone())?;
                        e.set("wall", unpack199[1].clone())?;
                        out197.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                d.set(Val::Str("wall".into()), e.get("wall")?)?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out197
                })?;
                d.set(Val::Str("top_stations".into()), {
                    let e = e.child();
                    let out200 = Val::list(vec![]);
                    for item201 in e.get("core")?.attr("lid_attachment_stations")?.iter()? {
                        let unpack202 = unpack(item201, 2)?;
                        e.set("xy", unpack202[0].clone())?;
                        e.set("wall", unpack202[1].clone())?;
                        out200.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                d.set(Val::Str("wall".into()), e.get("wall")?)?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out200
                })?;
                d.set(
                    Val::Str("bottom_holes".into()),
                    binary(
                        "add",
                        {
                            let e = e.child();
                            let out203 = Val::list(vec![]);
                            for item204 in e.get("core")?.attr("bottom_pour_positions")?.iter()? {
                                e.set("xy", item204)?;
                                out203.attr("append")?.call(
                                    vec![{
                                        let d = Val::dict(vec![]);
                                        d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                        d.set(
                                            Val::Str("radius".into()),
                                            e.get("core")?.attr("bottom_pour_radius")?,
                                        )?;
                                        d
                                    }],
                                    vec![],
                                )?;
                            }
                            out203
                        },
                        {
                            let e = e.child();
                            let out205 = Val::list(vec![]);
                            for item206 in {
                                let fun209 = e.get("core")?.attr("foam_cap_lid_vent_xy")?;
                                let mut args207 = Vec::new();
                                let mut kw208 = Vec::new();
                                kw208.push(("top".into(), Val::Bool(false)));
                                fun209.call(args207, kw208)?
                            }
                            .iter()?
                            {
                                e.set("xy", item206)?;
                                out205.attr("append")?.call(
                                    vec![{
                                        let d = Val::dict(vec![]);
                                        d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                        d.set(
                                            Val::Str("radius".into()),
                                            e.get("core")?.attr("foam_cap_lid_vent_radius")?,
                                        )?;
                                        d
                                    }],
                                    vec![],
                                )?;
                            }
                            out205
                        },
                    )?,
                )?;
                d.set(Val::Str("air_holes".into()), {
                    let e = e.child();
                    let out210 = Val::list(vec![]);
                    for item211 in {
                        let fun214 = e
                            .get("reservoir_ports")?
                            .attr("air_position")?
                            .attr("values")?;
                        let mut args212 = Vec::new();
                        let mut kw213 = Vec::new();
                        fun214.call(args212, kw213)?
                    }
                    .iter()?
                    {
                        e.set("xy", item211)?;
                        out210.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("xy".into()), {
                                    let e = e.child();
                                    let out215 = Val::list(vec![]);
                                    for item216 in e.get("xy")?.iter()? {
                                        e.set("v", item216)?;
                                        out215
                                            .attr("append")?
                                            .call(vec![unary("neg", e.get("v")?)?], vec![])?;
                                    }
                                    out215
                                })?;
                                d.set(
                                    Val::Str("radius".into()),
                                    binary(
                                        "truediv",
                                        e.get("reservoir_ports")?.attr("air_passage_diameter")?,
                                        Val::Float(2.0f64),
                                    )?,
                                )?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out210
                })?;
                d.set(Val::Str("conduits".into()), {
                    let e = e.child();
                    let out217 = Val::dict(vec![]);
                    for item218 in {
                        let fun221 = e.get("core")?.attr("cap_conduits")?.attr("items")?;
                        let mut args219 = Vec::new();
                        let mut kw220 = Vec::new();
                        fun221.call(args219, kw220)?
                    }
                    .iter()?
                    {
                        let unpack222 = unpack(item218, 2)?;
                        e.set("name", unpack222[0].clone())?;
                        e.set("xy", unpack222[1].clone())?;
                        if {
                            let v223 = e.get("name")?;
                            let v224 = {
                                let mut s = Vec::new();
                                s.push(Val::Str("reservoir-b-fill".into()));
                                s.push(Val::Str("water-in".into()));
                                s.push(Val::Str("carb-water-out".into()));
                                Val::tuple(s)
                            };
                            Val::Bool(compare("not_in", v223.clone(), v224.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out217.set(e.get("name")?, e.get("xy")?)?;
                        }
                    }
                    out217
                })?;
                d.set(Val::Str("reliefs".into()), {
                    let e = e.child();
                    let out225 = Val::dict(vec![]);
                    for item226 in {
                        let fun229 = e.get("core")?.attr("cap_conduits")?.attr("items")?;
                        let mut args227 = Vec::new();
                        let mut kw228 = Vec::new();
                        fun229.call(args227, kw228)?
                    }
                    .iter()?
                    {
                        let unpack230 = unpack(item226, 2)?;
                        e.set("name", unpack230[0].clone())?;
                        e.set("xy", unpack230[1].clone())?;
                        if {
                            let v231 = e.get("name")?;
                            let v232 = {
                                let mut s = Vec::new();
                                s.push(Val::Str("reservoir-b-fill".into()));
                                s.push(Val::Str("water-in".into()));
                                s.push(Val::Str("sensor-cable".into()));
                                s.extend(e.get("core")?.attr("cap_conduit_bore_radii")?.iter()?);
                                Val::tuple(s)
                            };
                            Val::Bool(compare("not_in", v231.clone(), v232.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out225.set(e.get("name")?, e.get("xy")?)?;
                        }
                    }
                    out225
                })?;
                d.set(
                    Val::Str("conduit_radius".into()),
                    e.get("core")?.attr("cap_conduit_bore_radius")?,
                )?;
                d.set(
                    Val::Str("conduit_radii".into()),
                    e.get("core")?.attr("cap_conduit_bore_radii")?,
                )?;
                d.set(
                    Val::Str("relief_radius".into()),
                    e.get("core")?.attr("cap_conduit_entry_relief_radius")?,
                )?;
                d.set(Val::Str("deck_columns".into()), {
                    let e = e.child();
                    let out233 = Val::list(vec![]);
                    for item234 in e.get("core")?.attr("deck_mounts")?.iter()? {
                        e.set("name", item234)?;
                        for item235 in {
                            let fun238 = e.get("core")?.attr("deck_mount_xy")?;
                            let mut args236 = Vec::new();
                            let mut kw237 = Vec::new();
                            args236.push(e.get("name")?);
                            fun238.call(args236, kw237)?
                        }
                        .iter()?
                        {
                            e.set("xy", item235)?;
                            out233.attr("append")?.call(
                                vec![{
                                    let d = Val::dict(vec![]);
                                    d.set(Val::Str("xy".into()), e.get("xy")?)?;
                                    d.set(Val::Str("top".into()), {
                                        let fun241 = e.get("deck_boss_z_top")?;
                                        let mut args239 = Vec::new();
                                        let mut kw240 = Vec::new();
                                        args239.push(e.get("name")?);
                                        fun241.call(args239, kw240)?
                                    })?;
                                    d
                                }],
                                vec![],
                            )?;
                        }
                    }
                    out233
                })?;
                d.set(
                    Val::Str("deck_radius".into()),
                    e.get("core")?.attr("deck_mount_boss_radius")?,
                )?;
                d.set(
                    Val::Str("deck_bore_radius".into()),
                    e.get("core")?.attr("deck_mount_bore_radius")?,
                )?;
                d.set(
                    Val::Str("deck_bore_depth".into()),
                    e.get("core")?.attr("deck_mount_bore_depth")?,
                )?;
                d.set(Val::Str("straight_guides".into()), {
                    let e = e.child();
                    let out242 = Val::list(vec![]);
                    for item243 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("water-in".into()));
                        s.push(Val::Str("carb-water-out".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("name", item243)?;
                        out242.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(
                                    Val::Str("point".into()),
                                    e.get("spec")?
                                        .get(Val::Str("cap_guides_world_mm".into()))?
                                        .get(e.get("name")?)?,
                                )?;
                                d.set(
                                    Val::Str("floor".into()),
                                    binary(
                                        "sub",
                                        e.get("pose")?
                                            .get(Val::Str("translation_mm".into()))?
                                            .get(Val::Int(2i64))?,
                                        e.get("top_cap_height")?,
                                    )?,
                                )?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out242
                })?;
                d.set(
                    Val::Str("world_to_cap_origin".into()),
                    e.get("world_origin")?,
                )?;
                d.set(Val::Str("world_to_cap_axes".into()), e.get("world_axes")?)?;
                d.set(
                    Val::Str("cap_face_world_z".into()),
                    e.get("spec")?.get(Val::Str("cap_face_z_mm".into()))?,
                )?;
                d.set(Val::Str("pump".into()), e.get("pump")?)?;
                d.set(Val::Str("snap".into()), {
                    let e = e.child();
                    let out244 = Val::dict(vec![]);
                    for item245 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("WING".into()));
                        s.push(Val::Str("REACH".into()));
                        s.push(Val::Str("LEDGE".into()));
                        s.push(Val::Str("HOOK".into()));
                        s.push(Val::Str("CATCH".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("name", item245)?;
                        out244.set(e.get("name")?, {
                            let fun248 = e.get("getattr")?;
                            let mut args246 = Vec::new();
                            let mut kw247 = Vec::new();
                            args246.push(e.get("rear_snaps")?);
                            args246.push(e.get("name")?);
                            fun248.call(args246, kw247)?
                        })?;
                    }
                    out244
                })?;
                d.set(Val::Str("valve_wall".into()), {
                    let fun251 = e.get("_above_mounts")?.attr("valve_support_datums")?;
                    let mut args249 = Vec::new();
                    let mut kw250 = Vec::new();
                    args249.push(Val::Str("valve-v-b".into()));
                    args249.push(e.get("lid_total_height")?);
                    fun251.call(args249, kw250)?
                })?;
                d.set(Val::Str("valve_pose".into()), {
                    let fun254 = e.get("layout")?.attr("pose")?;
                    let mut args252 = Vec::new();
                    let mut kw253 = Vec::new();
                    args252.push(Val::Str("valve-v-b".into()));
                    fun254.call(args252, kw253)?
                })?;
                d.set(Val::Str("valve".into()), {
                    let e = e.child();
                    let out255 = Val::dict(vec![]);
                    for item256 in {
                        let mut s = Vec::new();
                        s.push(Val::Str("corner_inset_x".into()));
                        s.push(Val::Str("corner_inset_y".into()));
                        s.push(Val::Str("socket_radius".into()));
                        s.push(Val::Str("socket_floor_z".into()));
                        s.push(Val::Str("seat_top_z".into()));
                        s.push(Val::Str("seat_half_y".into()));
                        s.push(Val::Str("port_air".into()));
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("key", item256)?;
                        out255.set(e.get("key")?, {
                            let fun259 = e.get("getattr")?;
                            let mut args257 = Vec::new();
                            let mut kw258 = Vec::new();
                            args257.push(e.get("seat")?);
                            args257.push(e.get("key")?);
                            fun259.call(args257, kw258)?
                        })?;
                    }
                    out255
                })?;
                d.set(
                    Val::Str("valve_port_radius".into()),
                    e.get("seat")?.attr("valve")?.attr("port_radius")?,
                )?;
                d.set(
                    Val::Str("valve_port_z".into()),
                    e.get("seat")?.attr("valve")?.attr("port_center_z")?,
                )?;
                d.set(Val::Str("union_supports".into()), {
                    let fun262 = e.get("_above_mounts")?.attr("union_support_datums")?;
                    let mut args260 = Vec::new();
                    let mut kw261 = Vec::new();
                    fun262.call(args260, kw261)?
                })?;
                d.set(Val::Str("wells".into()), e.get("wells")?)?;
                d.set(
                    Val::Str("well_wall".into()),
                    e.get("above_core_wiring")?.attr("WALL")?,
                )?;
                d.set(
                    Val::Str("well_fit".into()),
                    e.get("above_core_wiring")?.attr("FIT")?,
                )?;
                d.set(Val::Str("a_seats".into()), {
                    let fun265 = e.get("_a_anchors")?.attr("datums")?;
                    let mut args263 = Vec::new();
                    let mut kw264 = Vec::new();
                    fun265.call(args263, kw264)?
                })?;
                d.set(Val::Str("a_seat_spec".into()), {
                    let fun268 = e.get("_a_anchors")?.attr("specification")?;
                    let mut args266 = Vec::new();
                    let mut kw267 = Vec::new();
                    fun268.call(args266, kw267)?
                })?;
                d.set(Val::Str("a_snap".into()), e.get("a_spec")?)?;
                d.set(Val::Str("a_routes".into()), {
                    let e = e.child();
                    let out269 = Val::dict(vec![]);
                    for item270 in {
                        let fun273 = {
                            let fun276 = e
                                .get("above_core_routes")?
                                .attr("reservoir_a_route_specs")?;
                            let mut args274 = Vec::new();
                            let mut kw275 = Vec::new();
                            fun276.call(args274, kw275)?
                        }
                        .attr("items")?;
                        let mut args271 = Vec::new();
                        let mut kw272 = Vec::new();
                        fun273.call(args271, kw272)?
                    }
                    .iter()?
                    {
                        let unpack277 = unpack(item270, 2)?;
                        e.set("name", unpack277[0].clone())?;
                        e.set("row", unpack277[1].clone())?;
                        out269.set(
                            e.get("name")?,
                            e.get("row")?.get(Val::Str("segments".into()))?,
                        )?;
                    }
                    out269
                })?;
                d.set(Val::Str("tube_clips".into()), e.get("clips")?)?;
                d.set(Val::Str("flavor_wall".into()), {
                    let fun280 = e.get("_above_mounts")?.attr("valve_support_datums")?;
                    let mut args278 = Vec::new();
                    let mut kw279 = Vec::new();
                    args278.push(Val::Str("valve-v-b".into()));
                    fun280.call(args278, kw279)?
                })?;
                d.set(Val::Str("cable_bank".into()), {
                    let fun283 = e.get("manifold_bank_site")?;
                    let mut args281 = Vec::new();
                    let mut kw282 = Vec::new();
                    fun283.call(args281, kw282)?
                })?;
                d.set(Val::Str("cable_hook".into()), {
                    let fun286 = e.get("rear_level_hook_site")?;
                    let mut args284 = Vec::new();
                    let mut kw285 = Vec::new();
                    fun286.call(args284, kw285)?
                })?;
                d.set(Val::Str("b_fill".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("bend".into()), e.get("bend")?)?;
                    d.set(Val::Str("radius".into()), e.get("r")?)?;
                    d.set(Val::Str("centre".into()), e.get("centre")?)?;
                    d.set(Val::Str("outer".into()), e.get("outer")?)?;
                    d.set(
                        Val::Str("dome_lift".into()),
                        e.get("_reservoir_b_fill")?.attr("DOME_LIFT")?,
                    )?;
                    d.set(
                        Val::Str("inlet".into()),
                        binary(
                            "sub",
                            binary("sub", e.get("y")?, e.get("bend")?)?,
                            e.get("b_fill")?
                                .get(Val::Str("entry_world_mm".into()))?
                                .get(Val::Int(1i64))?,
                        )?,
                    )?;
                    d.set(
                        Val::Str("mouth".into()),
                        e.get("_reservoir_b_fill")?.attr("MOUTH")?,
                    )?;
                    d.set(
                        Val::Str("mouth_start".into()),
                        unary("neg", Val::Float(0.3f64))?,
                    )?;
                    d.set(
                        Val::Str("mouth_end".into()),
                        binary(
                            "add",
                            e.get("_reservoir_b_fill")?.attr("MOUTH")?,
                            Val::Float(0.05f64),
                        )?,
                    )?;
                    d.set(Val::Str("end_world".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::list(s)
                    })?;
                    d.set(Val::Str("guide_bounds_cap".into()), e.get("guide_bounds")?)?;
                    d
                })?;
                d.set(Val::Str("colors".into()), {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("foam-cap-lid-top".into()), {
                        let fun289 = e.get("linear")?;
                        let mut args287 = Vec::new();
                        let mut kw288 = Vec::new();
                        args287.push(e.get("_mat")?.attr("C_CAP_LID_TOP")?);
                        fun289.call(args287, kw288)?
                    })?;
                    d.set(Val::Str("foam-cap-bottom".into()), {
                        let fun292 = e.get("linear")?;
                        let mut args290 = Vec::new();
                        let mut kw291 = Vec::new();
                        args290.push(e.get("_mat")?.attr("C_CAP_BOTTOM")?);
                        fun292.call(args290, kw291)?
                    })?;
                    d.set(Val::Str("reservoir-b-fill-guide".into()), {
                        let fun295 = e.get("linear")?;
                        let mut args293 = Vec::new();
                        let mut kw294 = Vec::new();
                        args293.push(e.get("_mat")?.attr("C_CAP_TOP")?);
                        fun295.call(args293, kw294)?
                    })?;
                    d.set(Val::Str("pump-snap-cap".into()), {
                        let fun298 = e.get("linear")?;
                        let mut args296 = Vec::new();
                        let mut kw297 = Vec::new();
                        args296.push(e.get("_mat")?.attr("M_PETGF_BLACK")?);
                        fun298.call(args296, kw297)?
                    })?;
                    d
                })?;
                d
            });
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
            e.set("flute_payload", rt.import_module("flute_payload")?)?;
            let assigned299 = {
                let fun302 = e.get("Path")?;
                let mut args300 = Vec::new();
                let mut kw301 = Vec::new();
                args300.push(e.get("output")?);
                fun302.call(args300, kw301)?
            };
            e.set("output", assigned299.clone())?;
            {
                let fun305 = e.get("output")?.attr("mkdir")?;
                let mut args303 = Vec::new();
                let mut kw304 = Vec::new();
                kw304.push(("parents".into(), Val::Bool(true)));
                kw304.push(("exist_ok".into(), Val::Bool(true)));
                fun305.call(args303, kw304)?
            };
            {
                let fun308 = e.get("_rust_part")?.attr("cut")?;
                let mut args306 = Vec::new();
                let mut kw307 = Vec::new();
                args306.push(Val::Str("cold-core".into()));
                args306.push(Val::Str("foam-cap".into()));
                args306.push({
                    let fun311 = e.get("numbers")?;
                    let mut args309 = Vec::new();
                    let mut kw310 = Vec::new();
                    fun311.call(args309, kw310)?
                });
                args306.push(e.get("output")?);
                fun308.call(args306, kw307)?
            };
            for item312 in {
                let mut s = Vec::new();
                s.push(Val::Str("foam-cap-lid-top".into()));
                s.push(Val::Str("foam-cap-bottom".into()));
                s.push(Val::Str("reservoir-b-fill-guide".into()));
                s.push(Val::Str("pump-snap-cap".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("name", item312)?;
                {
                    let fun315 = e.get("flute_payload")?.attr("cut")?;
                    let mut args313 = Vec::new();
                    let mut kw314 = Vec::new();
                    args313.push(binary("truediv", e.get("output")?, {
                        let mut str316 = String::new();
                        str316.push_str(&format(&e.get("name")?, &String::new())?);
                        str316.push_str(".step");
                        Val::Str(str316)
                    })?);
                    args313.push(binary("truediv", e.get("output")?, {
                        let mut str317 = String::new();
                        str317.push_str(&format(&e.get("name")?, &String::new())?);
                        str317.push_str(".stl");
                        Val::Str(str317)
                    })?);
                    kw314.push(("preserve_print_triangles".into(), {
                        let v318 = e.get("name")?;
                        let v319 = Val::Str("pump-snap-cap".into());
                        Val::Bool(compare("eq", v318.clone(), v319.clone())?.truthy()?)
                    }));
                    fun315.call(args313, kw314)?
                };
            }
            for item320 in {
                let mut s = Vec::new();
                s.push(Val::Str("foam-cap-top".into()));
                s.push(Val::Str("foam-cap-lid-bottom".into()));
                s.push(Val::Str("pump-snap-cap-rear".into()));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("name", item320)?;
                for item321 in {
                    let mut s = Vec::new();
                    s.push(Val::Str(".step".into()));
                    s.push(Val::Str(".step.mesh".into()));
                    s.push(Val::Str(".stl".into()));
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("suffix", item321)?;
                    {
                        let fun324 = binary("truediv", e.get("output")?, {
                            let mut str325 = String::new();
                            str325.push_str(&format(&e.get("name")?, &String::new())?);
                            str325.push_str(&format(&e.get("suffix")?, &String::new())?);
                            Val::Str(str325)
                        })?
                        .attr("unlink")?;
                        let mut args322 = Vec::new();
                        let mut kw323 = Vec::new();
                        kw323.push(("missing_ok".into(), Val::Bool(true)));
                        fun324.call(args322, kw323)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun328 = e.get("_rust_part")?.attr("start")?;
        let mut args326 = Vec::new();
        let mut kw327 = Vec::new();
        fun328.call(args326, kw327)?
    };
    let assigned329 = {
        let fun332 = e.get("argparse")?.attr("ArgumentParser")?;
        let mut args330 = Vec::new();
        let mut kw331 = Vec::new();
        kw331.push(("description".into(), e.get("__doc__")?));
        fun332.call(args330, kw331)?
    };
    e.set("parser", assigned329.clone())?;
    {
        let fun335 = e.get("parser")?.attr("add_argument")?;
        let mut args333 = Vec::new();
        let mut kw334 = Vec::new();
        args333.push(Val::Str("--output".into()));
        kw334.push(("type".into(), e.get("Path")?));
        kw334.push(("default".into(), e.get("_here")?));
        fun335.call(args333, kw334)?
    };
    let assigned336 = {
        let fun339 = e.get("parser")?.attr("parse_args")?;
        let mut args337 = Vec::new();
        let mut kw338 = Vec::new();
        fun339.call(args337, kw338)?
    };
    e.set("args", assigned336.clone())?;
    {
        let fun342 = e.get("main")?;
        let mut args340 = Vec::new();
        let mut kw341 = Vec::new();
        args340.push(e.get("args")?.attr("output")?);
        fun342.call(args340, kw341)?
    };
    Ok(Val::None)
}
