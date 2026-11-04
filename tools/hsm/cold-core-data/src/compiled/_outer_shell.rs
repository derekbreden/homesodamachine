#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("world_workplane")?;
    e.set(
        "WorldWorkplane",
        rt.member("world_workplane", "WorldWorkplane")?,
    )?;
    e.set(
        "xy_plane_z_up",
        rt.member("world_workplane", "xy_plane_z_up")?,
    )?;
    e.set("fits", rt.import_module("fits")?)?;
    let mod2 = rt.import_module("_cold_core_interface")?;
    e.set(
        "attachment_stations",
        rt.member("_cold_core_interface", "attachment_stations")?,
    )?;
    e.set(
        "seam_channel_depth",
        rt.member("_cold_core_interface", "seam_channel_depth")?,
    )?;
    e.set(
        "seam_channel_width",
        rt.member("_cold_core_interface", "seam_channel_width")?,
    )?;
    e.set(
        "outer_shell_wall",
        rt.member("_cold_core_interface", "outer_shell_wall")?,
    )?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
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
        "outer_shell_x_length",
        rt.member("_cold_core_interface", "outer_shell_x_length")?,
    )?;
    e.set(
        "outer_shell_y_length",
        rt.member("_cold_core_interface", "outer_shell_y_length")?,
    )?;
    e.set(
        "attachment_xy_positions",
        rt.member("_cold_core_interface", "attachment_xy_positions")?,
    )?;
    e.set(
        "screw_boss_size",
        rt.member("_cold_core_interface", "screw_boss_size")?,
    )?;
    e.set(
        "screw_guard_diameter",
        rt.member("_cold_core_interface", "screw_guard_diameter")?,
    )?;
    e.set(
        "screw_clearance_radius",
        rt.member("_cold_core_interface", "screw_clearance_radius")?,
    )?;
    e.set(
        "bottom_screw_bore_depth",
        rt.member("_cold_core_interface", "bottom_screw_bore_depth")?,
    )?;
    e.set(
        "top_screw_bore_depth",
        rt.member("_cold_core_interface", "top_screw_bore_depth")?,
    )?;
    e.set(
        "corner_round_radius",
        rt.member("_cold_core_interface", "corner_round_radius")?,
    )?;
    e.set(
        "insert_pocket_radius",
        rt.member("_cold_core_interface", "insert_pocket_radius")?,
    )?;
    e.set(
        "insert_pocket_depth",
        rt.member("_cold_core_interface", "insert_pocket_depth")?,
    )?;
    e.set("make_box", rt.member("_cold_core_interface", "make_box")?)?;
    // _rounded_footprint
    e.set("_rounded_footprint", {
        let params = vec![("height".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun5 = {
                    let fun8 = {
                        let fun11 = {
                            let fun14 = {
                                let fun17 = {
                                    let fun20 = e.get("WorldWorkplane")?;
                                    let mut args18 = Vec::new();
                                    let mut kw19 = Vec::new();
                                    args18.push(e.get("xy_plane_z_up")?);
                                    fun20.call(args18, kw19)?
                                }
                                .attr("workplane")?;
                                let mut args15 = Vec::new();
                                let mut kw16 = Vec::new();
                                kw16.push(("offset".into(), Val::Int(0i64)));
                                fun17.call(args15, kw16)?
                            }
                            .attr("rect")?;
                            let mut args12 = Vec::new();
                            let mut kw13 = Vec::new();
                            args12.push(e.get("outer_shell_x_length")?);
                            args12.push(e.get("outer_shell_y_length")?);
                            fun14.call(args12, kw13)?
                        }
                        .attr("extrude")?;
                        let mut args9 = Vec::new();
                        let mut kw10 = Vec::new();
                        args9.push(e.get("height")?);
                        fun11.call(args9, kw10)?
                    }
                    .attr("edges")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    args6.push(Val::Str("|Z".into()));
                    fun8.call(args6, kw7)?
                }
                .attr("fillet")?;
                let mut args3 = Vec::new();
                let mut kw4 = Vec::new();
                args3.push(e.get("corner_round_radius")?);
                fun5.call(args3, kw4)?
            });
            Ok(Val::None)
        })
    })?;
    // cavity_plan
    e.set("cavity_plan", {
        let params = vec![
            ("z0".into(), None, false),
            ("z1".into(), None, false),
            ("wall".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned21 = if {
                let v22 = e.get("wall")?;
                let v23 = Val::None;
                Val::Bool(compare("is", v22.clone(), v23.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.get("outer_shell_wall")?
            } else {
                e.get("wall")?
            };
            e.set("w", assigned21.clone())?;
            return Ok({
                let fun26 = {
                    let fun29 = {
                        let fun32 = {
                            let fun35 = {
                                let fun38 = {
                                    let fun41 = e.get("WorldWorkplane")?;
                                    let mut args39 = Vec::new();
                                    let mut kw40 = Vec::new();
                                    args39.push(e.get("xy_plane_z_up")?);
                                    fun41.call(args39, kw40)?
                                }
                                .attr("workplane")?;
                                let mut args36 = Vec::new();
                                let mut kw37 = Vec::new();
                                kw37.push(("offset".into(), e.get("z0")?));
                                fun38.call(args36, kw37)?
                            }
                            .attr("rect")?;
                            let mut args33 = Vec::new();
                            let mut kw34 = Vec::new();
                            args33.push(binary(
                                "sub",
                                e.get("outer_shell_x_length")?,
                                binary("mul", Val::Int(2i64), e.get("w")?)?,
                            )?);
                            args33.push(binary(
                                "sub",
                                e.get("outer_shell_y_length")?,
                                binary("mul", Val::Int(2i64), e.get("w")?)?,
                            )?);
                            fun35.call(args33, kw34)?
                        }
                        .attr("extrude")?;
                        let mut args30 = Vec::new();
                        let mut kw31 = Vec::new();
                        args30.push(binary("sub", e.get("z1")?, e.get("z0")?)?);
                        fun32.call(args30, kw31)?
                    }
                    .attr("edges")?;
                    let mut args27 = Vec::new();
                    let mut kw28 = Vec::new();
                    args27.push(Val::Str("|Z".into()));
                    fun29.call(args27, kw28)?
                }
                .attr("fillet")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(binary("sub", e.get("corner_round_radius")?, e.get("w")?)?);
                fun26.call(args24, kw25)?
            });
            Ok(Val::None)
        })
    })?;
    // trim_cup_floor
    e.set("trim_cup_floor", {
        let params = vec![
            ("cup".into(), None, false),
            ("z0".into(), None, false),
            ("z1".into(), None, false),
            ("wall".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun44 = e.get("cup")?.attr("cut")?;
                let mut args42 = Vec::new();
                let mut kw43 = Vec::new();
                args42.push({
                    let fun47 = e.get("cavity_plan")?;
                    let mut args45 = Vec::new();
                    let mut kw46 = Vec::new();
                    args45.push(e.get("z0")?);
                    args45.push(e.get("z1")?);
                    kw46.push(("wall".into(), e.get("wall")?));
                    fun47.call(args45, kw46)?
                });
                fun44.call(args42, kw43)?
            });
            Ok(Val::None)
        })
    })?;
    // build_attachment_bosses
    e.set("build_attachment_bosses", {
        let params = vec![
            ("height".into(), None, false),
            ("oversize".into(), Some(Val::Float(0.0f64)), false),
            ("diameter".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned48 = binary(
                "add",
                binary(
                    "truediv",
                    if {
                        let v49 = e.get("diameter")?;
                        let v50 = Val::None;
                        Val::Bool(compare("is", v49.clone(), v50.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("screw_boss_size")?
                    } else {
                        e.get("diameter")?
                    },
                    Val::Int(2i64),
                )?,
                e.get("oversize")?,
            )?;
            e.set("r", assigned48.clone())?;
            let assigned51 = binary("truediv", e.get("outer_shell_x_length")?, Val::Int(2i64))?;
            e.set("corner_x", assigned51.clone())?;
            let assigned52 = binary("truediv", e.get("outer_shell_y_length")?, Val::Int(2i64))?;
            e.set("corner_y", assigned52.clone())?;
            let assigned53 = {
                let fun56 = {
                    let fun59 = {
                        let fun62 = {
                            let fun65 = {
                                let fun68 = e.get("WorldWorkplane")?;
                                let mut args66 = Vec::new();
                                let mut kw67 = Vec::new();
                                args66.push(e.get("xy_plane_z_up")?);
                                fun68.call(args66, kw67)?
                            }
                            .attr("workplane")?;
                            let mut args63 = Vec::new();
                            let mut kw64 = Vec::new();
                            kw64.push(("offset".into(), Val::Int(0i64)));
                            fun65.call(args63, kw64)?
                        }
                        .attr("pushPoints")?;
                        let mut args60 = Vec::new();
                        let mut kw61 = Vec::new();
                        args60.push(e.get("attachment_xy_positions")?);
                        fun62.call(args60, kw61)?
                    }
                    .attr("circle")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push(e.get("r")?);
                    fun59.call(args57, kw58)?
                }
                .attr("extrude")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push(e.get("height")?);
                fun56.call(args54, kw55)?
            };
            e.set("bosses", assigned53.clone())?;
            for item69 in e.get("attachment_stations")?.iter()? {
                let unpack99 = unpack(item69, 2)?;
                let unpack100 = unpack(unpack99[0].clone(), 2)?;
                e.set("cx", unpack100[0].clone())?;
                e.set("cy", unpack100[1].clone())?;
                e.set("wall", unpack99[1].clone())?;
                let assigned70 = Val::None;
                e.set("boss_webs", assigned70.clone())?;
                if {
                    let v71 = e.get("wall")?;
                    let v72 = {
                        let mut s = Vec::new();
                        s.push(Val::Str("corner".into()));
                        s.push(Val::Str("y".into()));
                        Val::tuple(s)
                    };
                    Val::Bool(compare("in", v71.clone(), v72.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned73 = if {
                        let v74 = e.get("cy")?;
                        let v75 = Val::Int(0i64);
                        Val::Bool(compare("gt", v74.clone(), v75.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        Val::Int(1i64)
                    } else {
                        unary("neg", Val::Int(1i64))?
                    };
                    e.set("y_sign", assigned73.clone())?;
                    let assigned76 = {
                        let fun79 = e.get("make_box")?;
                        let mut args77 = Vec::new();
                        let mut kw78 = Vec::new();
                        args77.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("cx")?, e.get("r")?)?);
                            s.push(binary("add", e.get("cx")?, e.get("r")?)?);
                            Val::tuple(s)
                        });
                        args77.push({
                            let mut s = Vec::new();
                            s.push(e.get("cy")?);
                            s.push(binary("mul", e.get("y_sign")?, e.get("corner_y")?)?);
                            Val::tuple(s)
                        });
                        args77.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(e.get("height")?);
                            Val::tuple(s)
                        });
                        fun79.call(args77, kw78)?
                    };
                    e.set("boss_webs", assigned76.clone())?;
                }
                if {
                    let v80 = e.get("wall")?;
                    let v81 = {
                        let mut s = Vec::new();
                        s.push(Val::Str("corner".into()));
                        s.push(Val::Str("x".into()));
                        Val::tuple(s)
                    };
                    Val::Bool(compare("in", v80.clone(), v81.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned82 = if {
                        let v83 = e.get("cx")?;
                        let v84 = Val::Int(0i64);
                        Val::Bool(compare("gt", v83.clone(), v84.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        Val::Int(1i64)
                    } else {
                        unary("neg", Val::Int(1i64))?
                    };
                    e.set("x_sign", assigned82.clone())?;
                    let assigned85 = {
                        let fun88 = e.get("make_box")?;
                        let mut args86 = Vec::new();
                        let mut kw87 = Vec::new();
                        args86.push({
                            let mut s = Vec::new();
                            s.push(e.get("cx")?);
                            s.push(binary("mul", e.get("x_sign")?, e.get("corner_x")?)?);
                            Val::tuple(s)
                        });
                        args86.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", e.get("cy")?, e.get("r")?)?);
                            s.push(binary("add", e.get("cy")?, e.get("r")?)?);
                            Val::tuple(s)
                        });
                        args86.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(e.get("height")?);
                            Val::tuple(s)
                        });
                        fun88.call(args86, kw87)?
                    };
                    e.set("web", assigned85.clone())?;
                    let assigned89 = if {
                        let v90 = e.get("boss_webs")?;
                        let v91 = Val::None;
                        Val::Bool(compare("is", v90.clone(), v91.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        e.get("web")?
                    } else {
                        {
                            let fun94 = e.get("boss_webs")?.attr("union")?;
                            let mut args92 = Vec::new();
                            let mut kw93 = Vec::new();
                            args92.push(e.get("web")?);
                            fun94.call(args92, kw93)?
                        }
                    };
                    e.set("boss_webs", assigned89.clone())?;
                }
                let assigned95 = {
                    let fun98 = e.get("bosses")?.attr("union")?;
                    let mut args96 = Vec::new();
                    let mut kw97 = Vec::new();
                    args96.push(e.get("boss_webs")?);
                    fun98.call(args96, kw97)?
                };
                e.set("bosses", assigned95.clone())?;
            }
            return Ok({
                let fun103 = e.get("bosses")?.attr("intersect")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push({
                    let fun106 = {
                        let fun109 = e.get("_rounded_footprint")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push(e.get("height")?);
                        fun109.call(args107, kw108)?
                    }
                    .attr("unwrap")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    fun106.call(args104, kw105)?
                });
                fun103.call(args101, kw102)?
            });
            Ok(Val::None)
        })
    })?;
    // fold_seam_channel
    e.set("fold_seam_channel", {
        let params = vec![("shell".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned110 = binary(
                "truediv",
                e.get("outer_shell_y_length")?,
                Val::Float(2.0f64),
            )?;
            e.set("face_y", assigned110.clone())?;
            let assigned111 = binary("sub", e.get("face_y")?, e.get("seam_channel_depth")?)?;
            e.set("floor_y", assigned111.clone())?;
            let assigned112 = binary("truediv", e.get("seam_channel_width")?, Val::Float(2.0f64))?;
            e.set("half", assigned112.clone())?;
            let assigned113 = e.get("foam_shell_rim_z")?;
            e.set("h", assigned113.clone())?;
            let assigned114 = {
                let fun117 = e.get("make_box")?;
                let mut args115 = Vec::new();
                let mut kw116 = Vec::new();
                args115.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        unary("neg", e.get("half")?)?,
                        e.get("outer_shell_wall")?,
                    )?);
                    s.push(binary("add", e.get("half")?, e.get("outer_shell_wall")?)?);
                    Val::tuple(s)
                });
                args115.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("floor_y")?,
                        e.get("outer_shell_wall")?,
                    )?);
                    s.push(e.get("floor_y")?);
                    Val::tuple(s)
                });
                args115.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(e.get("h")?);
                    Val::tuple(s)
                });
                fun117.call(args115, kw116)?
            };
            e.set("fold", assigned114.clone())?;
            let assigned118 = {
                let fun121 = e.get("make_box")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("half")?)?);
                    s.push(e.get("half")?);
                    Val::tuple(s)
                });
                args119.push({
                    let mut s = Vec::new();
                    s.push(e.get("floor_y")?);
                    s.push(binary("add", e.get("face_y")?, Val::Float(1.0f64))?);
                    Val::tuple(s)
                });
                args119.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    s.push(binary("add", e.get("h")?, Val::Float(1.0f64))?);
                    Val::tuple(s)
                });
                fun121.call(args119, kw120)?
            };
            e.set("channel", assigned118.clone())?;
            return Ok({
                let fun124 = {
                    let fun127 = e.get("shell")?.attr("union")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    args125.push(e.get("fold")?);
                    fun127.call(args125, kw126)?
                }
                .attr("cut")?;
                let mut args122 = Vec::new();
                let mut kw123 = Vec::new();
                args122.push(e.get("channel")?);
                fun124.call(args122, kw123)?
            });
            Ok(Val::None)
        })
    })?;
    // build_outer_shell
    e.set("build_outer_shell", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned128 = e.get("foam_shell_rim_z")?;
            e.set("h", assigned128.clone())?;
            let assigned129 = {
                let fun132 = {
                    let fun135 = e.get("_rounded_footprint")?;
                    let mut args133 = Vec::new();
                    let mut kw134 = Vec::new();
                    args133.push(e.get("h")?);
                    fun135.call(args133, kw134)?
                }
                .attr("cut")?;
                let mut args130 = Vec::new();
                let mut kw131 = Vec::new();
                args130.push({
                    let fun138 = e.get("cavity_plan")?;
                    let mut args136 = Vec::new();
                    let mut kw137 = Vec::new();
                    args136.push(e.get("wall_and_floor_thickness")?);
                    args136.push(e.get("h")?);
                    fun138.call(args136, kw137)?
                });
                fun132.call(args130, kw131)?
            };
            e.set("shell", assigned129.clone())?;
            let assigned139 = {
                let fun142 = e.get("build_attachment_bosses")?;
                let mut args140 = Vec::new();
                let mut kw141 = Vec::new();
                args140.push(e.get("h")?);
                kw141.push(("diameter".into(), e.get("screw_guard_diameter")?));
                fun142.call(args140, kw141)?
            };
            e.set("hosts", assigned139.clone())?;
            return Ok({
                let fun145 = {
                    let fun148 = e.get("fold_seam_channel")?;
                    let mut args146 = Vec::new();
                    let mut kw147 = Vec::new();
                    args146.push({
                        let fun151 = e.get("shell")?.attr("union")?;
                        let mut args149 = Vec::new();
                        let mut kw150 = Vec::new();
                        args149.push(e.get("hosts")?);
                        fun151.call(args149, kw150)?
                    });
                    fun148.call(args146, kw147)?
                }
                .attr("unwrap")?;
                let mut args143 = Vec::new();
                let mut kw144 = Vec::new();
                fun145.call(args143, kw144)?
            });
            Ok(Val::None)
        })
    })?;
    // cut_insert_pockets
    e.set("cut_insert_pockets", {
        let params = vec![("foam_shell".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer); // insert_pockets_at
            e.set("insert_pockets_at", {
                let params = vec![
                    ("z_floor".into(), None, false),
                    ("depth".into(), Some(e.get("insert_pocket_depth")?), false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun154 = {
                            let fun157 = {
                                let fun160 = {
                                    let fun163 = {
                                        let fun166 = e.get("WorldWorkplane")?;
                                        let mut args164 = Vec::new();
                                        let mut kw165 = Vec::new();
                                        args164.push(e.get("xy_plane_z_up")?);
                                        fun166.call(args164, kw165)?
                                    }
                                    .attr("workplane")?;
                                    let mut args161 = Vec::new();
                                    let mut kw162 = Vec::new();
                                    kw162.push(("offset".into(), e.get("z_floor")?));
                                    fun163.call(args161, kw162)?
                                }
                                .attr("pushPoints")?;
                                let mut args158 = Vec::new();
                                let mut kw159 = Vec::new();
                                args158.push(e.get("attachment_xy_positions")?);
                                fun160.call(args158, kw159)?
                            }
                            .attr("circle")?;
                            let mut args155 = Vec::new();
                            let mut kw156 = Vec::new();
                            args155.push(e.get("insert_pocket_radius")?);
                            fun157.call(args155, kw156)?
                        }
                        .attr("extrude")?;
                        let mut args152 = Vec::new();
                        let mut kw153 = Vec::new();
                        args152.push(e.get("depth")?);
                        fun154.call(args152, kw153)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned167 = {
                let fun170 = {
                    let fun173 = e.get("insert_pockets_at")?;
                    let mut args171 = Vec::new();
                    let mut kw172 = Vec::new();
                    args171.push(Val::Int(0i64));
                    args171.push(binary(
                        "add",
                        e.get("insert_pocket_depth")?,
                        e.get("fits")?.attr("supported_surface")?,
                    )?);
                    fun173.call(args171, kw172)?
                }
                .attr("unwrap")?;
                let mut args168 = Vec::new();
                let mut kw169 = Vec::new();
                fun170.call(args168, kw169)?
            };
            e.set("bottom_pockets", assigned167.clone())?;
            let assigned174 = {
                let fun177 = {
                    let fun180 = e.get("insert_pockets_at")?;
                    let mut args178 = Vec::new();
                    let mut kw179 = Vec::new();
                    args178.push(binary(
                        "sub",
                        e.get("foam_shell_rim_z")?,
                        e.get("insert_pocket_depth")?,
                    )?);
                    fun180.call(args178, kw179)?
                }
                .attr("unwrap")?;
                let mut args175 = Vec::new();
                let mut kw176 = Vec::new();
                fun177.call(args175, kw176)?
            };
            e.set("top_pockets", assigned174.clone())?;
            // tails
            e.set("tails", {
                let params = vec![("z0".into(), None, false), ("depth".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun183 = {
                            let fun186 = {
                                let fun189 = {
                                    let fun192 = {
                                        let fun195 = {
                                            let fun198 = e.get("WorldWorkplane")?;
                                            let mut args196 = Vec::new();
                                            let mut kw197 = Vec::new();
                                            args196.push(e.get("xy_plane_z_up")?);
                                            fun198.call(args196, kw197)?
                                        }
                                        .attr("workplane")?;
                                        let mut args193 = Vec::new();
                                        let mut kw194 = Vec::new();
                                        kw194.push(("offset".into(), e.get("z0")?));
                                        fun195.call(args193, kw194)?
                                    }
                                    .attr("pushPoints")?;
                                    let mut args190 = Vec::new();
                                    let mut kw191 = Vec::new();
                                    args190.push(e.get("attachment_xy_positions")?);
                                    fun192.call(args190, kw191)?
                                }
                                .attr("circle")?;
                                let mut args187 = Vec::new();
                                let mut kw188 = Vec::new();
                                args187.push(e.get("screw_clearance_radius")?);
                                fun189.call(args187, kw188)?
                            }
                            .attr("extrude")?;
                            let mut args184 = Vec::new();
                            let mut kw185 = Vec::new();
                            args184.push(e.get("depth")?);
                            fun186.call(args184, kw185)?
                        }
                        .attr("unwrap")?;
                        let mut args181 = Vec::new();
                        let mut kw182 = Vec::new();
                        fun183.call(args181, kw182)?
                    });
                    Ok(Val::None)
                })
            })?;
            // taper
            e.set("taper", {
                let params = vec![
                    ("z0".into(), None, false),
                    ("lower_radius".into(), None, false),
                    ("upper_radius".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned199 = binary(
                        "mul",
                        Val::Float(2.0f64),
                        binary("sub", e.get("lower_radius")?, e.get("upper_radius")?)?,
                    )?;
                    e.set("height", assigned199.clone())?;
                    return Ok({
                        let fun202 = e.get("cq")?.attr("Compound")?.attr("makeCompound")?;
                        let mut args200 = Vec::new();
                        let mut kw201 = Vec::new();
                        args200.push({
                            let e = e.child();
                            let out203 = Val::list(vec![]);
                            for item204 in e.get("attachment_xy_positions")?.iter()? {
                                let unpack205 = unpack(item204, 2)?;
                                e.set("x", unpack205[0].clone())?;
                                e.set("y", unpack205[1].clone())?;
                                out203.attr("append")?.call(
                                    vec![{
                                        let fun208 =
                                            e.get("cq")?.attr("Solid")?.attr("makeCone")?;
                                        let mut args206 = Vec::new();
                                        let mut kw207 = Vec::new();
                                        args206.push(e.get("lower_radius")?);
                                        args206.push(e.get("upper_radius")?);
                                        args206.push(e.get("height")?);
                                        args206.push({
                                            let fun211 = e.get("cq")?.attr("Vector")?;
                                            let mut args209 = Vec::new();
                                            let mut kw210 = Vec::new();
                                            args209.push(e.get("x")?);
                                            args209.push(e.get("y")?);
                                            args209.push(e.get("z0")?);
                                            fun211.call(args209, kw210)?
                                        });
                                        fun208.call(args206, kw207)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out203
                        });
                        fun202.call(args200, kw201)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned212 = binary(
                "add",
                e.get("insert_pocket_depth")?,
                e.get("fits")?.attr("supported_surface")?,
            )?;
            e.set("pilot_end", assigned212.clone())?;
            let assigned213 = binary(
                "add",
                e.get("bottom_screw_bore_depth")?,
                e.get("fits")?.attr("supported_surface")?,
            )?;
            e.set("tail_end", assigned213.clone())?;
            return Ok({
                let fun216 = {
                    let fun219 = {
                        let fun222 = {
                            let fun225 = {
                                let fun228 = {
                                    let fun231 = e.get("foam_shell")?.attr("cut")?;
                                    let mut args229 = Vec::new();
                                    let mut kw230 = Vec::new();
                                    args229.push(e.get("bottom_pockets")?);
                                    fun231.call(args229, kw230)?
                                }
                                .attr("cut")?;
                                let mut args226 = Vec::new();
                                let mut kw227 = Vec::new();
                                args226.push(e.get("top_pockets")?);
                                fun228.call(args226, kw227)?
                            }
                            .attr("cut")?;
                            let mut args223 = Vec::new();
                            let mut kw224 = Vec::new();
                            args223.push({
                                let fun234 = e.get("tails")?;
                                let mut args232 = Vec::new();
                                let mut kw233 = Vec::new();
                                args232.push(Val::Float(0.0f64));
                                args232.push(e.get("tail_end")?);
                                fun234.call(args232, kw233)?
                            });
                            fun225.call(args223, kw224)?
                        }
                        .attr("cut")?;
                        let mut args220 = Vec::new();
                        let mut kw221 = Vec::new();
                        args220.push({
                            let fun237 = e.get("taper")?;
                            let mut args235 = Vec::new();
                            let mut kw236 = Vec::new();
                            args235.push(e.get("pilot_end")?);
                            args235.push(e.get("insert_pocket_radius")?);
                            args235.push(e.get("screw_clearance_radius")?);
                            fun237.call(args235, kw236)?
                        });
                        fun222.call(args220, kw221)?
                    }
                    .attr("cut")?;
                    let mut args217 = Vec::new();
                    let mut kw218 = Vec::new();
                    args217.push({
                        let fun240 = e.get("taper")?;
                        let mut args238 = Vec::new();
                        let mut kw239 = Vec::new();
                        args238.push(e.get("tail_end")?);
                        args238.push(e.get("screw_clearance_radius")?);
                        args238.push(Val::Float(0.0f64));
                        fun240.call(args238, kw239)?
                    });
                    fun219.call(args217, kw218)?
                }
                .attr("cut")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                args214.push({
                    let fun243 = e.get("tails")?;
                    let mut args241 = Vec::new();
                    let mut kw242 = Vec::new();
                    args241.push(binary(
                        "sub",
                        e.get("foam_shell_rim_z")?,
                        e.get("top_screw_bore_depth")?,
                    )?);
                    args241.push(e.get("top_screw_bore_depth")?);
                    fun243.call(args241, kw242)?
                });
                fun216.call(args214, kw215)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
