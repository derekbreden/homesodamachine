#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
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
    };
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
                    let fun17 = binary(
                        "truediv",
                        binary(
                            "truediv",
                            binary("truediv", e.get("p")?, Val::Str("hardware".into()))?,
                            Val::Str("scripts".into()),
                        )?,
                        Val::Str("_cadq_export.py".into()),
                    )?
                    .attr("is_file")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    fun17.call(args15, kw16)?
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
    e.set("_repo", assigned9.clone())?;
    let assigned18 = binary("truediv", e.get("_repo")?, Val::Str("hardware".into()))?;
    e.set("_hw", assigned18.clone())?;
    let assigned19 = binary(
        "truediv",
        binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
        Val::Str("cold-core".into()),
    )?;
    e.set("_cold_core", assigned19.clone())?;
    {
        let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args20 = Vec::new();
        let mut kw21 = Vec::new();
        args20.push(Val::Int(0i64));
        args20.push({
            let fun25 = e.get("str")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(binary(
                "truediv",
                e.get("_hw")?,
                Val::Str("scripts".into()),
            )?);
            fun25.call(args23, kw24)?
        });
        fun22.call(args20, kw21)?
    };
    {
        let fun28 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        args26.push(Val::Int(0i64));
        args26.push({
            let fun31 = e.get("str")?;
            let mut args29 = Vec::new();
            let mut kw30 = Vec::new();
            args29.push(e.get("_cold_core")?);
            fun31.call(args29, kw30)?
        });
        fun28.call(args26, kw27)?
    };
    {
        let fun34 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args32 = Vec::new();
        let mut kw33 = Vec::new();
        args32.push(Val::Int(0i64));
        args32.push({
            let fun37 = e.get("str")?;
            let mut args35 = Vec::new();
            let mut kw36 = Vec::new();
            args35.push(binary(
                "truediv",
                binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
                Val::Str("cadlib".into()),
            )?);
            fun37.call(args35, kw36)?
        });
        fun34.call(args32, kw33)?
    };
    let mod38 = rt.import_module("_cold_core_interface")?;
    e.set(
        "cap_side_anchors",
        rt.member("_cold_core_interface", "cap_side_anchors")?,
    )?;
    e.set(
        "attachment_xy_positions",
        rt.member("_cold_core_interface", "attachment_xy_positions")?,
    )?;
    e.set(
        "cap_shell_clearance",
        rt.member("_cold_core_interface", "cap_shell_clearance")?,
    )?;
    e.set(
        "foam_cap_height",
        rt.member("_cold_core_interface", "foam_cap_height")?,
    )?;
    e.set(
        "cap_anchors",
        rt.member("_cold_core_interface", "cap_anchors")?,
    )?;
    e.set(
        "cap_conduits",
        rt.member("_cold_core_interface", "cap_conduits")?,
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
        "cap_cable_guides",
        rt.member("_cold_core_interface", "cap_cable_guides")?,
    )?;
    e.set(
        "cap_conduit_axis",
        rt.member("_cold_core_interface", "cap_conduit_axis")?,
    )?;
    e.set(
        "cap_conduit_bore_radius",
        rt.member("_cold_core_interface", "cap_conduit_bore_radius")?,
    )?;
    e.set(
        "co2_inlet_tube_radius",
        rt.member("_cold_core_interface", "co2_inlet_tube_radius")?,
    )?;
    e.set(
        "screw_clearance_radius",
        rt.member("_cold_core_interface", "screw_clearance_radius")?,
    )?;
    e.set(
        "deck_mount_xy",
        rt.member("_cold_core_interface", "deck_mount_xy")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "head_pad_height",
        rt.member("_cold_core_interface", "head_pad_height")?,
    )?;
    let mod39 = rt.import_module("_foam_cap")?;
    e.set("cap_face_z", rt.member("_foam_cap", "cap_face_z")?)?;
    e.set(
        "lid_total_height",
        rt.member("_foam_cap", "lid_total_height")?,
    )?;
    e.set("stack_floor_z", rt.member("_foam_cap", "stack_floor_z")?)?;
    e.set("top_cap_height", rt.member("_foam_cap", "top_cap_height")?)?;
    let mod40 = rt.import_module("_port_cuts")?;
    e.set("co2_inlet_xyz", rt.member("_port_cuts", "co2_inlet_xyz")?)?;
    e.set("routes", rt.import_module("_internal_routes")?)?;
    e.set("_routing", rt.import_module("_routing")?)?;
    e.set("_mat", rt.import_module("_materials")?)?;
    e.set("_above_mounts", rt.import_module("_above_core_mounts")?)?;
    let assigned41 = binary("sub", e.get("cap_face_z")?, e.get("stack_floor_z")?)?;
    e.set("cap_face_over_floor", assigned41.clone())?;
    let assigned42 = binary(
        "truediv",
        binary(
            "truediv",
            e.get("_cold_core")?,
            Val::Str("foam-shell".into()),
        )?,
        Val::Str("foam-shell.step".into()),
    )?;
    e.set("SHELL_STEP", assigned42.clone())?;
    let assigned43 = binary("truediv", e.get("_cold_core")?, Val::Str("foam-cap".into()))?;
    e.set("CAP_DIR", assigned43.clone())?;
    let assigned44 = binary(
        "truediv",
        e.get("_cold_core")?,
        Val::Str("reservoir".into()),
    )?;
    e.set("RESERVOIR_DIR", assigned44.clone())?;
    let assigned45 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("reservoir A".into()),
            Val::Str("reservoir-right".into()),
        )?;
        d.set(
            Val::Str("reservoir B".into()),
            Val::Str("reservoir-left".into()),
        )?;
        d
    };
    e.set("RESERVOIRS", assigned45.clone())?;
    let assigned46 = e.get("routes")?.attr("reservoir_cap_z")?;
    e.set("RESERVOIR_CAP_Z", assigned46.clone())?;
    let assigned47 = e.get("_mat")?.attr("C_FOAM_SHELL")?;
    e.set("SHELL_COLOR", assigned47.clone())?;
    let assigned48 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("foam-cap-lid-top".into()),
            e.get("_mat")?.attr("C_CAP_LID_TOP")?,
        )?;
        d.set(
            Val::Str("foam-cap-bottom".into()),
            e.get("_mat")?.attr("C_CAP_BOTTOM")?,
        )?;
        d
    };
    e.set("COLORS", assigned48.clone())?;
    let assigned49 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("water-in".into()), Val::Str("white".into()))?;
        d.set(Val::Str("carb-water-out".into()), Val::Str("blue".into()))?;
        d.set(Val::Str("co2-in".into()), Val::Str("red".into()))?;
        d.set(Val::Str("prv-vent".into()), Val::Str("black".into()))?;
        d.set(Val::Str("reservoir-a".into()), Val::Str("black".into()))?;
        d.set(
            Val::Str("reservoir-a-fill".into()),
            Val::Str("black".into()),
        )?;
        d.set(Val::Str("reservoir-b".into()), Val::Str("black".into()))?;
        d.set(
            Val::Str("reservoir-b-fill".into()),
            Val::Str("black".into()),
        )?;
        d
    };
    e.set("ROUTE_SPOOLS", assigned49.clone())?;
    let assigned50 = {
        let e = e.child();
        let out51 = Val::dict(vec![]);
        for item52 in {
            let fun55 = e.get("ROUTE_SPOOLS")?.attr("items")?;
            let mut args53 = Vec::new();
            let mut kw54 = Vec::new();
            fun55.call(args53, kw54)?
        }
        .iter()?
        {
            let unpack56 = unpack(item52, 2)?;
            e.set("name", unpack56[0].clone())?;
            e.set("key", unpack56[1].clone())?;
            out51.set(e.get("name")?, {
                let fun59 = e.get("_routing")?.attr("color")?;
                let mut args57 = Vec::new();
                let mut kw58 = Vec::new();
                args57.push(e.get("key")?);
                fun59.call(args57, kw58)?
            })?;
        }
        out51
    };
    e.set("ROUTE_COLORS", assigned50.clone())?;
    // spin_xy
    e.set("spin_xy", {
        let params = vec![("p".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(unary("neg", e.get("p")?.get(Val::Int(0i64))?)?);
                s.push(unary("neg", e.get("p")?.get(Val::Int(1i64))?)?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // cap_conduit_station
    e.set("cap_conduit_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun62 = e.get("spin_xy")?;
                let mut args60 = Vec::new();
                let mut kw61 = Vec::new();
                args60.push(e.get("cap_conduits")?.get(e.get("name")?)?);
                fun62.call(args60, kw61)?
            });
            Ok(Val::None)
        })
    })?;
    // cap_conduit_axis_out
    e.set("cap_conduit_axis_out", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("cap_conduit_axis")?);
            Ok(Val::None)
        })
    })?;
    // cap_conduit_mouth
    e.set("cap_conduit_mouth", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v63 = e.get("name")?;
                let v64 = Val::Str("reservoir-b-fill".into());
                Val::Bool(compare("eq", v63.clone(), v64.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned65 = {
                    let fun68 = e.get("_above_mounts")?.attr("reservoir_b_fill_passage")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    fun68.call(args66, kw67)?
                };
                e.set("passage", assigned65.clone())?;
                let assigned69 = e.get("passage")?.get(Val::Str("entry_world_mm".into()))?;
                e.set("point", assigned69.clone())?;
                let assigned70 = {
                    let fun73 = e.get("routes")?.attr("world_point_in_shell")?;
                    let mut args71 = Vec::new();
                    let mut kw72 = Vec::new();
                    args71.push(e.get("point")?);
                    fun73.call(args71, kw72)?
                };
                e.set("mouth", assigned70.clone())?;
                let assigned74 = {
                    let fun77 = e.get("routes")?.attr("world_point_in_shell")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    args75.push({
                        let fun80 = e.get("tuple")?;
                        let mut args78 = Vec::new();
                        let mut kw79 = Vec::new();
                        args78.push({
                            let e = e.child();
                            let out81 = Val::list(vec![]);
                            for item82 in {
                                let fun85 = e.get("zip")?;
                                let mut args83 = Vec::new();
                                let mut kw84 = Vec::new();
                                args83.push(e.get("point")?);
                                args83.push(
                                    e.get("passage")?
                                        .get(Val::Str("outward_axis_world".into()))?,
                                );
                                fun85.call(args83, kw84)?
                            }
                            .iter()?
                            {
                                let unpack86 = unpack(item82, 2)?;
                                e.set("p", unpack86[0].clone())?;
                                e.set("a", unpack86[1].clone())?;
                                out81
                                    .attr("append")?
                                    .call(vec![binary("add", e.get("p")?, e.get("a")?)?], vec![])?;
                            }
                            out81
                        });
                        fun80.call(args78, kw79)?
                    });
                    fun77.call(args75, kw76)?
                };
                e.set("outside", assigned74.clone())?;
                return Ok({
                    let mut s = Vec::new();
                    s.push(e.get("mouth")?);
                    s.push({
                        let fun89 = e.get("tuple")?;
                        let mut args87 = Vec::new();
                        let mut kw88 = Vec::new();
                        args87.push({
                            let e = e.child();
                            let out90 = Val::list(vec![]);
                            for item91 in {
                                let fun94 = e.get("zip")?;
                                let mut args92 = Vec::new();
                                let mut kw93 = Vec::new();
                                args92.push(e.get("mouth")?);
                                args92.push(e.get("outside")?);
                                fun94.call(args92, kw93)?
                            }
                            .iter()?
                            {
                                let unpack95 = unpack(item91, 2)?;
                                e.set("a", unpack95[0].clone())?;
                                e.set("b", unpack95[1].clone())?;
                                out90
                                    .attr("append")?
                                    .call(vec![binary("sub", e.get("b")?, e.get("a")?)?], vec![])?;
                            }
                            out90
                        });
                        fun89.call(args87, kw88)?
                    });
                    Val::tuple(s)
                });
            }
            let assigned96 = {
                let fun99 = e.get("cap_conduit_station")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                args97.push(e.get("name")?);
                fun99.call(args97, kw98)?
            };
            let unpack100 = unpack(assigned96.clone(), 2)?;
            e.set("x", unpack100[0].clone())?;
            e.set("y", unpack100[1].clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("cap_face_z")?);
                    Val::tuple(s)
                });
                s.push(e.get("cap_conduit_axis")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // cap_anchor_station
    e.set("cap_anchor_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun103 = e.get("spin_xy")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push(e.get("cap_anchors")?.get(e.get("name")?)?.attr("centre")?);
                fun103.call(args101, kw102)?
            });
            Ok(Val::None)
        })
    })?;
    // cap_side_anchor_station
    e.set("cap_side_anchor_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned104 = e.get("cap_side_anchors")?.get(e.get("name")?)?;
            e.set("a", assigned104.clone())?;
            return Ok({
                let fun107 = e.get("spin_xy")?;
                let mut args105 = Vec::new();
                let mut kw106 = Vec::new();
                args105.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("a")?.attr("centre")?.get(Val::Int(0i64))?,
                        e.get("a")?.attr("axis_off")?,
                    )?);
                    s.push(e.get("a")?.attr("centre")?.get(Val::Int(1i64))?);
                    Val::tuple(s)
                });
                fun107.call(args105, kw106)?
            });
            Ok(Val::None)
        })
    })?;
    // deck_mount_station
    e.set("deck_mount_station", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun110 = e.get("tuple")?;
                let mut args108 = Vec::new();
                let mut kw109 = Vec::new();
                args108.push({
                    let e = e.child();
                    let out111 = Val::list(vec![]);
                    for item112 in {
                        let fun115 = e.get("deck_mount_xy")?;
                        let mut args113 = Vec::new();
                        let mut kw114 = Vec::new();
                        args113.push(e.get("name")?);
                        fun115.call(args113, kw114)?
                    }
                    .iter()?
                    {
                        e.set("p", item112)?;
                        out111.attr("append")?.call(
                            vec![{
                                let fun118 = e.get("spin_xy")?;
                                let mut args116 = Vec::new();
                                let mut kw117 = Vec::new();
                                args116.push(e.get("p")?);
                                fun118.call(args116, kw117)?
                            }],
                            vec![],
                        )?;
                    }
                    out111
                });
                fun110.call(args108, kw109)?
            });
            Ok(Val::None)
        })
    })?;
    // rust_main
    e.set("rust_main", {
        let params = vec![("output".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            e.set("foam_numbers", rt.import_module("foam_numbers")?)?;
            let assigned317 = if {
                let v318 = e.get("output")?;
                let v319 = Val::None;
                Val::Bool(compare("is_not", v318.clone(), v319.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun322 = e.get("Path")?;
                    let mut args320 = Vec::new();
                    let mut kw321 = Vec::new();
                    args320.push(e.get("output")?);
                    fun322.call(args320, kw321)?
                }
            } else {
                e.get("_here")?.attr("parent")?
            };
            e.set("output", assigned317.clone())?;
            {
                let fun325 = e.get("output")?.attr("mkdir")?;
                let mut args323 = Vec::new();
                let mut kw324 = Vec::new();
                kw324.push(("parents".into(), Val::Bool(true)));
                kw324.push(("exist_ok".into(), Val::Bool(true)));
                fun325.call(args323, kw324)?
            };
            let assigned326 = {
                let fun329 = e.get("foam_numbers")?.attr("numbers")?;
                let mut args327 = Vec::new();
                let mut kw328 = Vec::new();
                fun329.call(args327, kw328)?
            };
            e.set("numbers", assigned326.clone())?;
            let assigned330 = {
                let fun333 = e.get("_rust_part")?.attr("cut")?;
                let mut args331 = Vec::new();
                let mut kw332 = Vec::new();
                args331.push(Val::Str("cold-core".into()));
                args331.push(Val::Str("foam-assembly".into()));
                args331.push(e.get("numbers")?);
                args331.push(e.get("output")?);
                fun333.call(args331, kw332)?
            };
            e.set("result", assigned330.clone())?;
            {
                let fun370 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args368 = Vec::new();
                let mut kw369 = Vec::new();
                args368.push(Val::Int(0i64));
                args368.push({
                    let fun373 = e.get("str")?;
                    let mut args371 = Vec::new();
                    let mut kw372 = Vec::new();
                    args371.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("cold-core-layout".into()),
                    )?);
                    fun373.call(args371, kw372)?
                });
                fun370.call(args368, kw369)?
            };
            let mod374 = rt.import_module("_core_presentation")?;
            e.set("finish", rt.member("_core_presentation", "finish")?)?;
            {
                let fun377 = e.get("finish")?;
                let mut args375 = Vec::new();
                let mut kw376 = Vec::new();
                args375.push(binary(
                    "truediv",
                    e.get("output")?,
                    Val::Str("foam-assembly.step".into()),
                )?);
                args375.push(e.get("numbers")?.get(Val::Str("models".into()))?);
                fun377.call(args375, kw376)?
            };
            return Ok(e.get("result")?);
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("argv".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("argparse", rt.import_module("argparse")?)?;
            let assigned378 = {
                let fun381 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args379 = Vec::new();
                let mut kw380 = Vec::new();
                kw380.push(("description".into(), e.get("__doc__")?));
                fun381.call(args379, kw380)?
            };
            e.set("parser", assigned378.clone())?;
            {
                let fun384 = e.get("parser")?.attr("add_argument")?;
                let mut args382 = Vec::new();
                let mut kw383 = Vec::new();
                args382.push(Val::Str("--output".into()));
                kw383.push(("type".into(), e.get("Path")?));
                kw383.push((
                    "help".into(),
                    Val::Str("directory for generated assembly files".into()),
                ));
                fun384.call(args382, kw383)?
            };
            let assigned385 = {
                let fun388 = e.get("parser")?.attr("parse_args")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push(e.get("argv")?);
                fun388.call(args386, kw387)?
            };
            e.set("args", assigned385.clone())?;
            {
                let fun391 = e.get("rust_main")?;
                let mut args389 = Vec::new();
                let mut kw390 = Vec::new();
                args389.push(e.get("args")?.attr("output")?);
                fun391.call(args389, kw390)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun394 = e.get("_rust_part")?.attr("start")?;
        let mut args392 = Vec::new();
        let mut kw393 = Vec::new();
        fun394.call(args392, kw393)?
    };
    {
        let fun397 = e.get("main")?;
        let mut args395 = Vec::new();
        let mut kw396 = Vec::new();
        fun397.call(args395, kw396)?
    };
    Ok(Val::None)
}
