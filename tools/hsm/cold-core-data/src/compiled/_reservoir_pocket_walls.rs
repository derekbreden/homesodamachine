#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod1 = rt.import_module("world_workplane")?;
    e.set(
        "WorldWorkplane",
        rt.member("world_workplane", "WorldWorkplane")?,
    )?;
    e.set(
        "WorldProfile",
        rt.member("world_workplane", "WorldProfile")?,
    )?;
    e.set(
        "xy_plane_z_up",
        rt.member("world_workplane", "xy_plane_z_up")?,
    )?;
    let mod2 = rt.import_module("_cold_core_interface")?;
    e.set(
        "wall_thickness",
        rt.member("_cold_core_interface", "wall_thickness")?,
    )?;
    e.set(
        "pocket_centerward_arc_outer_radius",
        rt.member("_cold_core_interface", "pocket_centerward_arc_outer_radius")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "bag_pocket_corner_inner_radius",
        rt.member("_cold_core_interface", "bag_pocket_corner_inner_radius")?,
    )?;
    e.set(
        "bag_pocket_y_inner_max",
        rt.member("_cold_core_interface", "bag_pocket_y_inner_max")?,
    )?;
    e.set(
        "bag_pocket_far_inner_x",
        rt.member("_cold_core_interface", "bag_pocket_far_inner_x")?,
    )?;
    let assigned3 = e.get("wall_thickness")?;
    e.set("w", assigned3.clone())?;
    let assigned4 = Val::Float(60.0f64);
    e.set("pocket_centerward_arc_transition_y", assigned4.clone())?;
    let assigned5 = e.get("pocket_centerward_arc_outer_radius")?;
    e.set("arc_cavity_r", assigned5.clone())?;
    let assigned6 = binary("sub", e.get("arc_cavity_r")?, e.get("w")?)?;
    e.set("arc_outer_r", assigned6.clone())?;
    let assigned7 = e.get("bag_pocket_y_inner_max")?;
    e.set("y_inner", assigned7.clone())?;
    let assigned8 = {
        let fun11 = e.get("math")?.attr("sqrt")?;
        let mut args9 = Vec::new();
        let mut kw10 = Vec::new();
        args9.push(binary(
            "sub",
            binary("pow", e.get("arc_outer_r")?, Val::Int(2i64))?,
            binary(
                "pow",
                e.get("pocket_centerward_arc_transition_y")?,
                Val::Int(2i64),
            )?,
        )?);
        fun11.call(args9, kw10)?
    };
    e.set("middle_outer_x", assigned8.clone())?;
    let assigned12 = {
        let fun15 = e.get("math")?.attr("sqrt")?;
        let mut args13 = Vec::new();
        let mut kw14 = Vec::new();
        args13.push(binary(
            "sub",
            binary("pow", e.get("arc_cavity_r")?, Val::Int(2i64))?,
            binary(
                "pow",
                e.get("pocket_centerward_arc_transition_y")?,
                Val::Int(2i64),
            )?,
        )?);
        fun15.call(args13, kw14)?
    };
    e.set("middle_cavity_x", assigned12.clone())?;
    let assigned16 = binary(
        "truediv",
        binary(
            "sub",
            e.get("y_inner")?,
            e.get("pocket_centerward_arc_transition_y")?,
        )?,
        Val::Float(2.0f64),
    )?;
    e.set("_chord_half_y", assigned16.clone())?;
    let assigned17 = Val::Float(56.655020677894306f64);
    e.set("transition_center_x", assigned17.clone())?;
    let assigned18 = binary(
        "truediv",
        binary(
            "add",
            e.get("y_inner")?,
            e.get("pocket_centerward_arc_transition_y")?,
        )?,
        Val::Float(2.0f64),
    )?;
    e.set("transition_center_y", assigned18.clone())?;
    let assigned19 = {
        let fun22 = e.get("math")?.attr("sqrt")?;
        let mut args20 = Vec::new();
        let mut kw21 = Vec::new();
        args20.push(binary(
            "add",
            binary(
                "pow",
                binary(
                    "sub",
                    e.get("transition_center_x")?,
                    e.get("middle_cavity_x")?,
                )?,
                Val::Int(2i64),
            )?,
            binary("pow", e.get("_chord_half_y")?, Val::Int(2i64))?,
        )?);
        fun22.call(args20, kw21)?
    };
    e.set("transition_cavity_r", assigned19.clone())?;
    let assigned23 = binary("add", e.get("transition_cavity_r")?, e.get("w")?)?;
    e.set("transition_outer_r", assigned23.clone())?;
    // build_plus_x_cavity
    e.set("build_plus_x_cavity", {
        let params = vec![("height".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v24 = e.get("height")?;
                let v25 = Val::None;
                Val::Bool(compare("is", v24.clone(), v25.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned26 = e.get("foam_shell_outer_height")?;
                e.set("height", assigned26.clone())?;
            }
            let assigned27 = e.get("bag_pocket_far_inner_x")?;
            e.set("far_x_inner", assigned27.clone())?;
            let assigned28 = e.get("bag_pocket_corner_inner_radius")?;
            e.set("corner_inner_r", assigned28.clone())?;
            let assigned29 = e.get("pocket_centerward_arc_transition_y")?;
            e.set("arc_y", assigned29.clone())?;
            // transition_apex
            e.set("transition_apex", {
                let params = vec![("y_sign".into(), None, false)];
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
                            e.get("transition_center_x")?,
                            e.get("transition_cavity_r")?,
                        )?);
                        s.push(binary(
                            "mul",
                            e.get("y_sign")?,
                            e.get("transition_center_y")?,
                        )?);
                        Val::tuple(s)
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned30 = {
                let fun33 = {
                    let fun36 = {
                        let fun39 = {
                            let fun42 = {
                                let fun45 = {
                                    let fun48 = {
                                        let fun51 = {
                                            let fun54 = {
                                                let fun57 = {
                                                    let fun60 = e.get("WorldProfile")?;
                                                    let mut args58 = Vec::new();
                                                    let mut kw59 = Vec::new();
                                                    fun60.call(args58, kw59)?
                                                }
                                                .attr("moveTo")?;
                                                let mut args55 = Vec::new();
                                                let mut kw56 = Vec::new();
                                                args55.push({
                                                    let mut s = Vec::new();
                                                    s.push(e.get("middle_cavity_x")?);
                                                    s.push(e.get("y_inner")?);
                                                    Val::tuple(s)
                                                });
                                                fun57.call(args55, kw56)?
                                            }
                                            .attr("lineTo")?;
                                            let mut args52 = Vec::new();
                                            let mut kw53 = Vec::new();
                                            args52.push({
                                                let mut s = Vec::new();
                                                s.push(binary(
                                                    "sub",
                                                    e.get("far_x_inner")?,
                                                    e.get("corner_inner_r")?,
                                                )?);
                                                s.push(e.get("y_inner")?);
                                                Val::tuple(s)
                                            });
                                            fun54.call(args52, kw53)?
                                        }
                                        .attr("radiusArc")?;
                                        let mut args49 = Vec::new();
                                        let mut kw50 = Vec::new();
                                        args49.push({
                                            let mut s = Vec::new();
                                            s.push(e.get("far_x_inner")?);
                                            s.push(binary(
                                                "sub",
                                                e.get("y_inner")?,
                                                e.get("corner_inner_r")?,
                                            )?);
                                            Val::tuple(s)
                                        });
                                        args49.push(e.get("corner_inner_r")?);
                                        fun51.call(args49, kw50)?
                                    }
                                    .attr("lineTo")?;
                                    let mut args46 = Vec::new();
                                    let mut kw47 = Vec::new();
                                    args46.push({
                                        let mut s = Vec::new();
                                        s.push(e.get("far_x_inner")?);
                                        s.push(unary(
                                            "neg",
                                            binary(
                                                "sub",
                                                e.get("y_inner")?,
                                                e.get("corner_inner_r")?,
                                            )?,
                                        )?);
                                        Val::tuple(s)
                                    });
                                    fun48.call(args46, kw47)?
                                }
                                .attr("radiusArc")?;
                                let mut args43 = Vec::new();
                                let mut kw44 = Vec::new();
                                args43.push({
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "sub",
                                        e.get("far_x_inner")?,
                                        e.get("corner_inner_r")?,
                                    )?);
                                    s.push(unary("neg", e.get("y_inner")?)?);
                                    Val::tuple(s)
                                });
                                args43.push(e.get("corner_inner_r")?);
                                fun45.call(args43, kw44)?
                            }
                            .attr("lineTo")?;
                            let mut args40 = Vec::new();
                            let mut kw41 = Vec::new();
                            args40.push({
                                let mut s = Vec::new();
                                s.push(e.get("middle_cavity_x")?);
                                s.push(unary("neg", e.get("y_inner")?)?);
                                Val::tuple(s)
                            });
                            fun42.call(args40, kw41)?
                        }
                        .attr("threePointArc")?;
                        let mut args37 = Vec::new();
                        let mut kw38 = Vec::new();
                        args37.push({
                            let fun63 = e.get("transition_apex")?;
                            let mut args61 = Vec::new();
                            let mut kw62 = Vec::new();
                            args61.push(unary("neg", Val::Int(1i64))?);
                            fun63.call(args61, kw62)?
                        });
                        args37.push({
                            let mut s = Vec::new();
                            s.push(e.get("middle_cavity_x")?);
                            s.push(unary("neg", e.get("arc_y")?)?);
                            Val::tuple(s)
                        });
                        fun39.call(args37, kw38)?
                    }
                    .attr("threePointArc")?;
                    let mut args34 = Vec::new();
                    let mut kw35 = Vec::new();
                    args34.push({
                        let mut s = Vec::new();
                        s.push(e.get("arc_cavity_r")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args34.push({
                        let mut s = Vec::new();
                        s.push(e.get("middle_cavity_x")?);
                        s.push(e.get("arc_y")?);
                        Val::tuple(s)
                    });
                    fun36.call(args34, kw35)?
                }
                .attr("threePointArc")?;
                let mut args31 = Vec::new();
                let mut kw32 = Vec::new();
                args31.push({
                    let fun66 = e.get("transition_apex")?;
                    let mut args64 = Vec::new();
                    let mut kw65 = Vec::new();
                    args64.push(unary("pos", Val::Int(1i64))?);
                    fun66.call(args64, kw65)?
                });
                args31.push({
                    let mut s = Vec::new();
                    s.push(e.get("middle_cavity_x")?);
                    s.push(e.get("y_inner")?);
                    Val::tuple(s)
                });
                fun33.call(args31, kw32)?
            };
            e.set("cavity_profile", assigned30.clone())?;
            return Ok({
                let fun69 = {
                    let fun72 = {
                        let fun75 = {
                            let fun78 = {
                                let fun81 = e.get("WorldWorkplane")?;
                                let mut args79 = Vec::new();
                                let mut kw80 = Vec::new();
                                args79.push(e.get("xy_plane_z_up")?);
                                fun81.call(args79, kw80)?
                            }
                            .attr("workplane")?;
                            let mut args76 = Vec::new();
                            let mut kw77 = Vec::new();
                            kw77.push(("offset".into(), Val::Int(0i64)));
                            fun78.call(args76, kw77)?
                        }
                        .attr("profile")?;
                        let mut args73 = Vec::new();
                        let mut kw74 = Vec::new();
                        args73.push(e.get("cavity_profile")?);
                        fun75.call(args73, kw74)?
                    }
                    .attr("wire")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    fun72.call(args70, kw71)?
                }
                .attr("extrude")?;
                let mut args67 = Vec::new();
                let mut kw68 = Vec::new();
                args67.push(e.get("height")?);
                fun69.call(args67, kw68)?
            });
            Ok(Val::None)
        })
    })?;
    // build_reservoir_pocket_walls
    e.set("build_reservoir_pocket_walls", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned82 = e.get("foam_shell_outer_height")?;
            e.set("height", assigned82.clone())?;
            let assigned83 = {
                let fun86 = {
                    let fun89 = e.get("build_plus_x_cavity")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(e.get("height")?);
                    fun89.call(args87, kw88)?
                }
                .attr("unwrap")?;
                let mut args84 = Vec::new();
                let mut kw85 = Vec::new();
                fun86.call(args84, kw85)?
            };
            e.set("cavity", assigned83.clone())?;
            let assigned90 = {
                let fun93 = {
                    let fun96 = {
                        let fun99 = e.get("cavity")?.attr("faces")?;
                        let mut args97 = Vec::new();
                        let mut kw98 = Vec::new();
                        args97.push(Val::Str("<Z".into()));
                        fun99.call(args97, kw98)?
                    }
                    .attr("wires")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    fun96.call(args94, kw95)?
                }
                .attr("val")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                fun93.call(args91, kw92)?
            };
            e.set("wire", assigned90.clone())?;
            let assigned100 = {
                let fun103 = e.get("wire")?.attr("offset2D")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push(e.get("w")?);
                kw102.push(("kind".into(), Val::Str("arc".into())));
                fun103.call(args101, kw102)?
            }
            .get(Val::Int(0i64))?;
            e.set("outer_wire", assigned100.clone())?;
            let assigned104 = {
                let fun107 = {
                    let fun110 = {
                        let fun113 = {
                            let fun116 = e.get("cq")?.attr("Workplane")?;
                            let mut args114 = Vec::new();
                            let mut kw115 = Vec::new();
                            args114.push(Val::Str("XY".into()));
                            fun116.call(args114, kw115)?
                        }
                        .attr("add")?;
                        let mut args111 = Vec::new();
                        let mut kw112 = Vec::new();
                        args111.push(e.get("outer_wire")?);
                        fun113.call(args111, kw112)?
                    }
                    .attr("toPending")?;
                    let mut args108 = Vec::new();
                    let mut kw109 = Vec::new();
                    fun110.call(args108, kw109)?
                }
                .attr("extrude")?;
                let mut args105 = Vec::new();
                let mut kw106 = Vec::new();
                args105.push(e.get("height")?);
                fun107.call(args105, kw106)?
            };
            e.set("outer", assigned104.clone())?;
            let assigned117 = {
                let fun120 = e.get("outer")?.attr("cut")?;
                let mut args118 = Vec::new();
                let mut kw119 = Vec::new();
                args118.push(e.get("cavity")?);
                fun120.call(args118, kw119)?
            };
            e.set("plus_x_pocket", assigned117.clone())?;
            return Ok({
                let fun123 = e.get("plus_x_pocket")?.attr("union")?;
                let mut args121 = Vec::new();
                let mut kw122 = Vec::new();
                args121.push({
                    let fun126 = e.get("plus_x_pocket")?.attr("mirror")?;
                    let mut args124 = Vec::new();
                    let mut kw125 = Vec::new();
                    args124.push(Val::Str("YZ".into()));
                    fun126.call(args124, kw125)?
                });
                fun123.call(args121, kw122)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
