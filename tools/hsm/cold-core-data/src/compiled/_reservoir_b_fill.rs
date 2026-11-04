#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("functools")?;
    e.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    e.set("importlib", rt.import_module("importlib")?)?;
    e.set("math", rt.import_module("math")?)?;
    let assigned2 = Val::Float(14.0f64);
    e.set("BEND_RADIUS", assigned2.clone())?;
    let assigned3 = Val::Float(6.8f64);
    e.set("CHANNEL_DIAMETER", assigned3.clone())?;
    let assigned4 = Val::Float(2.0f64);
    e.set("WALL", assigned4.clone())?;
    let assigned5 = Val::Float(0.5f64);
    e.set("MOUTH", assigned5.clone())?;
    let assigned6 = binary("truediv", e.get("CHANNEL_DIAMETER")?, Val::Float(2.0f64))?;
    e.set("CHANNEL_RADIUS", assigned6.clone())?;
    let assigned7 = binary("add", e.get("WALL")?, e.get("CHANNEL_RADIUS")?)?;
    e.set("CHANNEL_CENTRE", assigned7.clone())?;
    let assigned8 = binary(
        "mul",
        binary(
            "sub",
            {
                let fun11 = e.get("math")?.attr("sqrt")?;
                let mut args9 = Vec::new();
                let mut kw10 = Vec::new();
                args9.push(Val::Float(2.0f64));
                fun11.call(args9, kw10)?
            },
            Val::Float(1.0f64),
        )?,
        e.get("CHANNEL_RADIUS")?,
    )?;
    e.set("DOME_LIFT", assigned8.clone())?;
    // passage
    e.set("passage", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned12 = {
                let fun15 = e.get("importlib")?.attr("import_module")?;
                let mut args13 = Vec::new();
                let mut kw14 = Vec::new();
                args13.push(Val::Str("_cold_core_interface".into()));
                fun15.call(args13, kw14)?
            };
            e.set("core", assigned12.clone())?;
            let assigned16 = {
                let fun19 = e.get("importlib")?.attr("import_module")?;
                let mut args17 = Vec::new();
                let mut kw18 = Vec::new();
                args17.push(Val::Str("above_core".into()));
                fun19.call(args17, kw18)?
            };
            e.set("layout", assigned16.clone())?;
            let assigned20 = {
                let fun23 = e.get("layout")?.attr("cap_lid_pose")?;
                let mut args21 = Vec::new();
                let mut kw22 = Vec::new();
                fun23.call(args21, kw22)?
            };
            e.set("pose", assigned20.clone())?;
            let assigned24 = binary(
                "sub",
                e.get("core")?.attr("foam_cap_height")?,
                e.get("core")?.attr("head_pad_height")?,
            )?;
            e.set("cup_height", assigned24.clone())?;
            let assigned25 = binary(
                "add",
                binary(
                    "sub",
                    e.get("pose")?
                        .get(Val::Str("translation_mm".into()))?
                        .get(Val::Int(2i64))?,
                    e.get("cup_height")?,
                )?,
                e.get("core")?.attr("cap_shell_clearance")?,
            )?;
            e.set("floor", assigned25.clone())?;
            let assigned26 = {
                let fun29 = e.get("layout")?.attr("point")?;
                let mut args27 = Vec::new();
                let mut kw28 = Vec::new();
                args27.push(e.get("pose")?);
                args27.push({
                    let mut s = Vec::new();
                    s.extend(
                        {
                            let fun32 = e.get("core")?.attr("reservoir_fill_conduit_xy")?;
                            let mut args30 = Vec::new();
                            let mut kw31 = Vec::new();
                            args30.push(unary("neg", Val::Int(1i64))?);
                            fun32.call(args30, kw31)?
                        }
                        .iter()?,
                    );
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun29.call(args27, kw28)?
            }
            .get(Val::Slice {
                start: None,
                stop: Some(Val::Int(2i64).integer()?),
                step: 1,
            })?;
            let unpack33 = unpack(assigned26.clone(), 2)?;
            e.set("x", unpack33[0].clone())?;
            e.set("y", unpack33[1].clone())?;
            let assigned34 = {
                let fun37 = e.get("layout")?.attr("point")?;
                let mut args35 = Vec::new();
                let mut kw36 = Vec::new();
                args35.push(e.get("pose")?);
                args35.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "truediv",
                        e.get("core")?.attr("outer_shell_x_length")?,
                        Val::Float(2.0f64),
                    )?);
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun37.call(args35, kw36)?
            }
            .get(Val::Int(1i64))?;
            e.set("front", assigned34.clone())?;
            e.set("fits", rt.import_module("fits")?)?;
            let assigned38 = e.get("floor")?;
            e.set("tangent_z", assigned38.clone())?;
            let assigned39 = {
                let mut s = Vec::new();
                s.push(e.get("x")?);
                s.push(e.get("front")?);
                s.push(binary("add", e.get("tangent_z")?, e.get("BEND_RADIUS")?)?);
                Val::tuple(s)
            };
            e.set("entry", assigned39.clone())?;
            let assigned40 = {
                let mut s = Vec::new();
                s.push(e.get("x")?);
                s.push(e.get("y")?);
                s.push(binary("sub", e.get("floor")?, Val::Float(5.4f64))?);
                Val::tuple(s)
            };
            e.set("tip", assigned40.clone())?;
            let assigned41 = {
                let fun44 = e.get("layout")?.attr("specification")?;
                let mut args42 = Vec::new();
                let mut kw43 = Vec::new();
                fun44.call(args42, kw43)?
            }
            .get(Val::Str("cap_face_z_mm".into()))?;
            e.set("face", assigned41.clone())?;
            let assigned45 = binary(
                "sub",
                e.get("y")?,
                binary(
                    "mul",
                    e.get("BEND_RADIUS")?,
                    binary("sub", Val::Float(1.0f64), {
                        let fun48 = e.get("math")?.attr("sin")?;
                        let mut args46 = Vec::new();
                        let mut kw47 = Vec::new();
                        args46.push(binary(
                            "truediv",
                            e.get("math")?.attr("pi")?,
                            Val::Float(4.0f64),
                        )?);
                        fun48.call(args46, kw47)?
                    })?,
                )?,
            )?;
            e.set("lift_y", assigned45.clone())?;
            let assigned49 = binary("add", e.get("front")?, Val::Float(23.0f64))?;
            e.set("fore_y", assigned49.clone())?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("entry_world_mm".into()), e.get("entry")?)?;
                d.set(Val::Str("outward_axis_world".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(unary("neg", Val::Float(1.0f64))?);
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("route_points_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("entry")?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("entry")?.get(Val::Int(2i64))?);
                        Val::tuple(s)
                    });
                    s.push(e.get("tip")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("bend_radius_mm".into()), e.get("BEND_RADIUS")?)?;
                d.set(
                    Val::Str("channel_diameter_mm".into()),
                    e.get("CHANNEL_DIAMETER")?,
                )?;
                d.set(Val::Str("channel_section".into()), Val::Str("round".into()))?;
                d.set(Val::Str("wall_mm".into()), e.get("WALL")?)?;
                d.set(Val::Str("outlet_leg_mm".into()), Val::Float(0.0f64))?;
                d.set(Val::Str("mouth_lead_in_mm".into()), e.get("MOUTH")?)?;
                d.set(Val::Str("cup_mouth_relief_mm".into()), e.get("MOUTH")?)?;
                d.set(
                    Val::Str("supported_roof_allowance_mm".into()),
                    e.get("fits")?.attr("supported_surface")?,
                )?;
                d.set(Val::Str("print_up_world".into()), {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(0.0f64));
                    s.push(Val::Float(1.0f64));
                    Val::tuple(s)
                })?;
                d.set(Val::Str("bend_end_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("tangent_z")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("outlet_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    s.push(e.get("floor")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("tip_world_mm".into()), e.get("tip")?)?;
                d.set(Val::Str("cup_floor_world_z_mm".into()), e.get("floor")?)?;
                d.set(
                    Val::Str("cup_top_world_z_mm".into()),
                    binary(
                        "sub",
                        e.get("pose")?
                            .get(Val::Str("translation_mm".into()))?
                            .get(Val::Int(2i64))?,
                        e.get("core")?.attr("cap_lid_clearance")?,
                    )?,
                )?;
                d.set(
                    Val::Str("lid_bottom_world_z_mm".into()),
                    e.get("pose")?
                        .get(Val::Str("translation_mm".into()))?
                        .get(Val::Int(2i64))?,
                )?;
                d.set(Val::Str("lid_face_world_z_mm".into()), e.get("face")?)?;
                d.set(Val::Str("roof_top_world_z_mm".into()), e.get("face")?)?;
                d.set(
                    Val::Str("throat_roof_stock_mm".into()),
                    binary(
                        "sub",
                        e.get("face")?,
                        binary(
                            "add",
                            binary(
                                "add",
                                e.get("entry")?.get(Val::Int(2i64))?,
                                e.get("CHANNEL_RADIUS")?,
                            )?,
                            e.get("fits")?.attr("supported_surface")?,
                        )?,
                    )?,
                )?;
                d.set(
                    Val::Str("entry_leadin_roof_stock_mm".into()),
                    binary(
                        "sub",
                        e.get("face")?,
                        binary(
                            "add",
                            binary(
                                "add",
                                binary(
                                    "add",
                                    e.get("entry")?.get(Val::Int(2i64))?,
                                    e.get("CHANNEL_RADIUS")?,
                                )?,
                                e.get("MOUTH")?,
                            )?,
                            e.get("fits")?.attr("supported_surface")?,
                        )?,
                    )?,
                )?;
                d.set(Val::Str("stock_min_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, Val::Float(16.5f64))?);
                    s.push(e.get("front")?);
                    s.push(e.get("floor")?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("stock_max_world_mm".into()), {
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, Val::Float(16.5f64))?);
                    s.push(binary("add", e.get("y")?, Val::Float(15.0f64))?);
                    s.push(e.get("face")?);
                    Val::tuple(s)
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // _body_section
    e.set("_body_section", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned50 = binary("add", e.get("CHANNEL_RADIUS")?, e.get("WALL")?)?;
            e.set("outer", assigned50.clone())?;
            let assigned51 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("BEND_RADIUS")?, e.get("outer")?)?);
                s.push(binary("add", e.get("BEND_RADIUS")?, e.get("outer")?)?);
                Val::tuple(s)
            };
            let unpack52 = unpack(assigned51.clone(), 2)?;
            e.set("lo", unpack52[0].clone())?;
            e.set("hi", unpack52[1].clone())?;
            let assigned53 = binary("add", e.get("CHANNEL_CENTRE")?, e.get("DOME_LIFT")?)?;
            e.set("z", assigned53.clone())?;
            return Ok({
                let fun56 = {
                    let fun59 = {
                        let fun62 = {
                            let fun65 = {
                                let fun68 = {
                                    let fun71 = e.get("cq")?.attr("Workplane")?;
                                    let mut args69 = Vec::new();
                                    let mut kw70 = Vec::new();
                                    args69.push(Val::Str("XZ".into()));
                                    fun71.call(args69, kw70)?
                                }
                                .attr("moveTo")?;
                                let mut args66 = Vec::new();
                                let mut kw67 = Vec::new();
                                args66.push(e.get("lo")?);
                                args66.push(Val::Float(0.0f64));
                                fun68.call(args66, kw67)?
                            }
                            .attr("lineTo")?;
                            let mut args63 = Vec::new();
                            let mut kw64 = Vec::new();
                            args63.push(e.get("hi")?);
                            args63.push(Val::Float(0.0f64));
                            fun65.call(args63, kw64)?
                        }
                        .attr("lineTo")?;
                        let mut args60 = Vec::new();
                        let mut kw61 = Vec::new();
                        args60.push(e.get("hi")?);
                        args60.push(e.get("z")?);
                        fun62.call(args60, kw61)?
                    }
                    .attr("threePointArc")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push({
                        let mut s = Vec::new();
                        s.push(e.get("BEND_RADIUS")?);
                        s.push(binary("add", e.get("z")?, e.get("outer")?)?);
                        Val::tuple(s)
                    });
                    args57.push({
                        let mut s = Vec::new();
                        s.push(e.get("lo")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    fun59.call(args57, kw58)?
                }
                .attr("close")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                fun56.call(args54, kw55)?
            });
            Ok(Val::None)
        })
    })?;
    // _channel_section
    e.set("_channel_section", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            return Ok({
                let fun74 = {
                    let fun77 = {
                        let fun80 = e.get("cq")?.attr("Workplane")?;
                        let mut args78 = Vec::new();
                        let mut kw79 = Vec::new();
                        args78.push(Val::Str("XZ".into()));
                        fun80.call(args78, kw79)?
                    }
                    .attr("moveTo")?;
                    let mut args75 = Vec::new();
                    let mut kw76 = Vec::new();
                    args75.push(e.get("BEND_RADIUS")?);
                    args75.push(e.get("CHANNEL_CENTRE")?);
                    fun77.call(args75, kw76)?
                }
                .attr("circle")?;
                let mut args72 = Vec::new();
                let mut kw73 = Vec::new();
                args72.push(e.get("CHANNEL_RADIUS")?);
                fun74.call(args72, kw73)?
            });
            Ok(Val::None)
        })
    })?;
    // _mouth
    e.set("_mouth", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            // at
            e.set("at", {
                let params = vec![("y".into(), None, false), ("radius".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned81 = {
                        let fun84 = e.get("cq")?.attr("Plane")?;
                        let mut args82 = Vec::new();
                        let mut kw83 = Vec::new();
                        kw83.push(("origin".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(e.get("y")?);
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        }));
                        kw83.push(("xDir".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        }));
                        kw83.push(("normal".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(unary("neg", Val::Float(1.0f64))?);
                            s.push(Val::Float(0.0f64));
                            Val::tuple(s)
                        }));
                        fun84.call(args82, kw83)?
                    };
                    e.set("plane", assigned81.clone())?;
                    return Ok({
                        let fun87 = {
                            let fun90 = {
                                let fun93 = {
                                    let fun96 = {
                                        let fun99 = e.get("cq")?.attr("Workplane")?;
                                        let mut args97 = Vec::new();
                                        let mut kw98 = Vec::new();
                                        args97.push(e.get("plane")?);
                                        fun99.call(args97, kw98)?
                                    }
                                    .attr("moveTo")?;
                                    let mut args94 = Vec::new();
                                    let mut kw95 = Vec::new();
                                    args94.push(e.get("BEND_RADIUS")?);
                                    args94.push(e.get("CHANNEL_CENTRE")?);
                                    fun96.call(args94, kw95)?
                                }
                                .attr("circle")?;
                                let mut args91 = Vec::new();
                                let mut kw92 = Vec::new();
                                args91.push(e.get("radius")?);
                                fun93.call(args91, kw92)?
                            }
                            .attr("wires")?;
                            let mut args88 = Vec::new();
                            let mut kw89 = Vec::new();
                            fun90.call(args88, kw89)?
                        }
                        .attr("val")?;
                        let mut args85 = Vec::new();
                        let mut kw86 = Vec::new();
                        fun87.call(args85, kw86)?
                    });
                    Ok(Val::None)
                })
            })?;
            return Ok({
                let fun102 = e.get("cq")?.attr("Solid")?.attr("makeLoft")?;
                let mut args100 = Vec::new();
                let mut kw101 = Vec::new();
                args100.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun105 = e.get("at")?;
                        let mut args103 = Vec::new();
                        let mut kw104 = Vec::new();
                        args103.push(unary("neg", Val::Float(0.3f64))?);
                        args103.push(binary(
                            "add",
                            binary("add", e.get("CHANNEL_RADIUS")?, e.get("MOUTH")?)?,
                            Val::Float(0.3f64),
                        )?);
                        fun105.call(args103, kw104)?
                    });
                    s.push({
                        let fun108 = e.get("at")?;
                        let mut args106 = Vec::new();
                        let mut kw107 = Vec::new();
                        args106.push(binary("add", e.get("MOUTH")?, Val::Float(0.05f64))?);
                        args106.push(binary(
                            "sub",
                            e.get("CHANNEL_RADIUS")?,
                            Val::Float(0.05f64),
                        )?);
                        fun108.call(args106, kw107)?
                    });
                    Val::list(s)
                });
                kw101.push(("ruled".into(), Val::Bool(true)));
                fun102.call(args100, kw101)?
            });
            Ok(Val::None)
        })
    })?;
    // holder_sections
    e.set("holder_sections", {
        let params = vec![
            ("inlet_leg".into(), None, false),
            ("outlet_leg".into(), Some(Val::Float(0.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned109 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
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
                Val::tuple(s)
            };
            e.set("axis", assigned109.clone())?;
            let assigned110 = {
                let fun113 = e.get("cq")?.attr("Vector")?;
                let mut args111 = Vec::new();
                let mut kw112 = Vec::new();
                args111.push({
                    let fun116 = e.get("math")?.attr("sqrt")?;
                    let mut args114 = Vec::new();
                    let mut kw115 = Vec::new();
                    args114.push(Val::Float(0.5f64));
                    fun116.call(args114, kw115)?
                });
                args111.push(unary("neg", {
                    let fun119 = e.get("math")?.attr("sqrt")?;
                    let mut args117 = Vec::new();
                    let mut kw118 = Vec::new();
                    args117.push(Val::Float(0.5f64));
                    fun119.call(args117, kw118)?
                })?);
                args111.push(Val::Float(0.0f64));
                fun113.call(args111, kw112)?
            };
            e.set("mirror", assigned110.clone())?;
            let assigned120 = {
                let fun123 = e.get("cq")?.attr("Vector")?;
                let mut args121 = Vec::new();
                let mut kw122 = Vec::new();
                fun123.call(args121, kw122)?
            };
            e.set("origin", assigned120.clone())?;
            let assigned124 = {
                let fun127 = {
                    let fun130 = {
                        let fun133 = e.get("_body_section")?;
                        let mut args131 = Vec::new();
                        let mut kw132 = Vec::new();
                        fun133.call(args131, kw132)?
                    }
                    .attr("revolve")?;
                    let mut args128 = Vec::new();
                    let mut kw129 = Vec::new();
                    args128.push(Val::Float(90.0f64));
                    args128.extend(e.get("axis")?.iter()?);
                    fun130.call(args128, kw129)?
                }
                .attr("union")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.push({
                    let fun136 = {
                        let fun139 = e.get("_body_section")?;
                        let mut args137 = Vec::new();
                        let mut kw138 = Vec::new();
                        fun139.call(args137, kw138)?
                    }
                    .attr("extrude")?;
                    let mut args134 = Vec::new();
                    let mut kw135 = Vec::new();
                    args134.push(e.get("inlet_leg")?);
                    fun136.call(args134, kw135)?
                });
                fun127.call(args125, kw126)?
            };
            e.set("body", assigned124.clone())?;
            let assigned140 = {
                let fun143 = {
                    let fun146 = {
                        let fun149 = e.get("_channel_section")?;
                        let mut args147 = Vec::new();
                        let mut kw148 = Vec::new();
                        fun149.call(args147, kw148)?
                    }
                    .attr("revolve")?;
                    let mut args144 = Vec::new();
                    let mut kw145 = Vec::new();
                    args144.push(Val::Float(90.0f64));
                    args144.extend(e.get("axis")?.iter()?);
                    fun146.call(args144, kw145)?
                }
                .attr("union")?;
                let mut args141 = Vec::new();
                let mut kw142 = Vec::new();
                args141.push({
                    let fun152 = {
                        let fun155 = e.get("_channel_section")?;
                        let mut args153 = Vec::new();
                        let mut kw154 = Vec::new();
                        fun155.call(args153, kw154)?
                    }
                    .attr("extrude")?;
                    let mut args150 = Vec::new();
                    let mut kw151 = Vec::new();
                    args150.push(e.get("inlet_leg")?);
                    fun152.call(args150, kw151)?
                });
                fun143.call(args141, kw142)?
            };
            e.set("channel", assigned140.clone())?;
            if {
                let v156 = e.get("outlet_leg")?;
                let v157 = Val::Float(0.0f64);
                Val::Bool(compare("gt", v156.clone(), v157.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned158 = {
                    let fun161 = e.get("body")?.attr("union")?;
                    let mut args159 = Vec::new();
                    let mut kw160 = Vec::new();
                    args159.push({
                        let fun164 = {
                            let fun167 = {
                                let fun170 = e.get("_body_section")?;
                                let mut args168 = Vec::new();
                                let mut kw169 = Vec::new();
                                fun170.call(args168, kw169)?
                            }
                            .attr("extrude")?;
                            let mut args165 = Vec::new();
                            let mut kw166 = Vec::new();
                            args165.push(e.get("outlet_leg")?);
                            fun167.call(args165, kw166)?
                        }
                        .attr("mirror")?;
                        let mut args162 = Vec::new();
                        let mut kw163 = Vec::new();
                        args162.push(e.get("mirror")?);
                        args162.push(e.get("origin")?);
                        fun164.call(args162, kw163)?
                    });
                    fun161.call(args159, kw160)?
                };
                e.set("body", assigned158.clone())?;
                let assigned171 = {
                    let fun174 = e.get("channel")?.attr("union")?;
                    let mut args172 = Vec::new();
                    let mut kw173 = Vec::new();
                    args172.push({
                        let fun177 = {
                            let fun180 = {
                                let fun183 = e.get("_channel_section")?;
                                let mut args181 = Vec::new();
                                let mut kw182 = Vec::new();
                                fun183.call(args181, kw182)?
                            }
                            .attr("extrude")?;
                            let mut args178 = Vec::new();
                            let mut kw179 = Vec::new();
                            args178.push(e.get("outlet_leg")?);
                            fun180.call(args178, kw179)?
                        }
                        .attr("mirror")?;
                        let mut args175 = Vec::new();
                        let mut kw176 = Vec::new();
                        args175.push(e.get("mirror")?);
                        args175.push(e.get("origin")?);
                        fun177.call(args175, kw176)?
                    });
                    fun174.call(args172, kw173)?
                };
                e.set("channel", assigned171.clone())?;
            }
            let assigned184 = {
                let fun187 = {
                    let fun190 = e.get("_mouth")?;
                    let mut args188 = Vec::new();
                    let mut kw189 = Vec::new();
                    fun190.call(args188, kw189)?
                }
                .attr("translate")?;
                let mut args185 = Vec::new();
                let mut kw186 = Vec::new();
                args185.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(0.0f64));
                    s.push(unary("neg", e.get("inlet_leg")?)?);
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                });
                fun187.call(args185, kw186)?
            };
            e.set("start", assigned184.clone())?;
            let assigned191 = {
                let fun194 = {
                    let fun197 = {
                        let fun200 = e.get("_mouth")?;
                        let mut args198 = Vec::new();
                        let mut kw199 = Vec::new();
                        fun200.call(args198, kw199)?
                    }
                    .attr("translate")?;
                    let mut args195 = Vec::new();
                    let mut kw196 = Vec::new();
                    args195.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(unary("neg", e.get("outlet_leg")?)?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    fun197.call(args195, kw196)?
                }
                .attr("mirror")?;
                let mut args192 = Vec::new();
                let mut kw193 = Vec::new();
                args192.push(e.get("mirror")?);
                args192.push(e.get("origin")?);
                fun194.call(args192, kw193)?
            };
            e.set("end", assigned191.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let fun203 = e.get("body")?.attr("val")?;
                    let mut args201 = Vec::new();
                    let mut kw202 = Vec::new();
                    fun203.call(args201, kw202)?
                });
                s.push({
                    let fun206 = {
                        let fun209 = {
                            let fun212 = e.get("channel")?.attr("val")?;
                            let mut args210 = Vec::new();
                            let mut kw211 = Vec::new();
                            fun212.call(args210, kw211)?
                        }
                        .attr("fuse")?;
                        let mut args207 = Vec::new();
                        let mut kw208 = Vec::new();
                        args207.push(e.get("start")?);
                        args207.push(e.get("end")?);
                        fun209.call(args207, kw208)?
                    }
                    .attr("clean")?;
                    let mut args204 = Vec::new();
                    let mut kw205 = Vec::new();
                    fun206.call(args204, kw205)?
                });
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // channel_air
    e.set("channel_air", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned213 = {
                let fun216 = e.get("passage")?;
                let mut args214 = Vec::new();
                let mut kw215 = Vec::new();
                fun216.call(args214, kw215)?
            };
            e.set("data", assigned213.clone())?;
            let assigned217 = e.get("data")?.get(Val::Str("bend_end_world_mm".into()))?;
            let unpack218 = unpack(assigned217.clone(), 3)?;
            e.set("x", unpack218[0].clone())?;
            e.set("y", unpack218[1].clone())?;
            e.set("tangent_z", unpack218[2].clone())?;
            let assigned219 = binary("sub", e.get("y")?, e.get("BEND_RADIUS")?)?;
            e.set("turn_y", assigned219.clone())?;
            let assigned220 = {
                let fun223 = e.get("holder_sections")?;
                let mut args221 = Vec::new();
                let mut kw222 = Vec::new();
                args221.push(binary(
                    "sub",
                    e.get("turn_y")?,
                    e.get("data")?
                        .get(Val::Str("entry_world_mm".into()))?
                        .get(Val::Int(1i64))?,
                )?);
                args221.push(Val::Float(0.0f64));
                fun223.call(args221, kw222)?
            };
            let unpack224 = unpack(assigned220.clone(), 2)?;
            e.set("_body", unpack224[0].clone())?;
            e.set("channel", unpack224[1].clone())?;
            let assigned225 = {
                let fun228 = {
                    let fun231 = e.get("channel")?.attr("rotate")?;
                    let mut args229 = Vec::new();
                    let mut kw230 = Vec::new();
                    args229.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args229.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args229.push(unary("neg", Val::Float(90.0f64))?);
                    fun231.call(args229, kw230)?
                }
                .attr("translate")?;
                let mut args226 = Vec::new();
                let mut kw227 = Vec::new();
                args226.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("CHANNEL_CENTRE")?)?);
                    s.push(e.get("turn_y")?);
                    s.push(e.get("tangent_z")?);
                    Val::tuple(s)
                });
                fun228.call(args226, kw227)?
            };
            e.set("channel", assigned225.clone())?;
            return Ok({
                let fun234 = {
                    let fun237 = e.get("channel")?.attr("fuse")?;
                    let mut args235 = Vec::new();
                    let mut kw236 = Vec::new();
                    args235.push({
                        let fun240 = e.get("channel")?.attr("translate")?;
                        let mut args238 = Vec::new();
                        let mut kw239 = Vec::new();
                        args238.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(
                                e.get("data")?
                                    .get(Val::Str("supported_roof_allowance_mm".into()))?,
                            );
                            Val::tuple(s)
                        });
                        fun240.call(args238, kw239)?
                    });
                    fun237.call(args235, kw236)?
                }
                .attr("clean")?;
                let mut args232 = Vec::new();
                let mut kw233 = Vec::new();
                fun234.call(args232, kw233)?
            });
            Ok(Val::None)
        })
    })?;
    // guide_native
    e.set("guide_native", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            rt.import_module("importlib.util")?;
            e.set("importlib", rt.import_module("importlib")?)?;
            let mod241 = rt.import_module("pathlib")?;
            e.set("Path", rt.member("pathlib", "Path")?)?;
            let assigned242 = {
                let fun245 = e.get("next")?;
                let mut args243 = Vec::new();
                let mut kw244 = Vec::new();
                args243.push({
                    let e = e.child();
                    let out246 = Val::list(vec![]);
                    for item247 in {
                        let fun250 = {
                            let fun253 = e.get("Path")?;
                            let mut args251 = Vec::new();
                            let mut kw252 = Vec::new();
                            args251.push(e.get("__file__")?);
                            fun253.call(args251, kw252)?
                        }
                        .attr("resolve")?;
                        let mut args248 = Vec::new();
                        let mut kw249 = Vec::new();
                        fun250.call(args248, kw249)?
                    }
                    .attr("parents")?
                    .iter()?
                    {
                        e.set("p", item247)?;
                        if {
                            let fun256 = binary("truediv", e.get("p")?, Val::Str("future".into()))?
                                .attr("is_dir")?;
                            let mut args254 = Vec::new();
                            let mut kw255 = Vec::new();
                            fun256.call(args254, kw255)?
                        }
                        .truthy()?
                        {
                            out246.attr("append")?.call(vec![e.get("p")?], vec![])?;
                        }
                    }
                    out246
                });
                fun245.call(args243, kw244)?
            };
            e.set("root", assigned242.clone())?;
            let assigned257 = {
                let fun260 = e
                    .get("importlib")?
                    .attr("util")?
                    .attr("spec_from_file_location")?;
                let mut args258 = Vec::new();
                let mut kw259 = Vec::new();
                args258.push(Val::Str("_b_fill_r14".into()));
                args258.push(binary(
                    "truediv",
                    e.get("root")?,
                    Val::Str("future/tube-bend-holder-exploration/tube_bend_holder.py".into()),
                )?);
                fun260.call(args258, kw259)?
            };
            e.set("spec", assigned257.clone())?;
            let assigned261 = {
                let fun264 = e.get("importlib")?.attr("util")?.attr("module_from_spec")?;
                let mut args262 = Vec::new();
                let mut kw263 = Vec::new();
                args262.push(e.get("spec")?);
                fun264.call(args262, kw263)?
            };
            e.set("module", assigned261.clone())?;
            {
                let fun267 = e.get("spec")?.attr("loader")?.attr("exec_module")?;
                let mut args265 = Vec::new();
                let mut kw266 = Vec::new();
                args265.push(e.get("module")?);
                fun267.call(args265, kw266)?
            };
            return Ok({
                let fun270 = {
                    let fun273 = e.get("module")?.attr("holder")?;
                    let mut args271 = Vec::new();
                    let mut kw272 = Vec::new();
                    args271.push(e.get("WALL")?);
                    args271.push(Val::Float(0.0f64));
                    fun273.call(args271, kw272)?
                }
                .attr("val")?;
                let mut args268 = Vec::new();
                let mut kw269 = Vec::new();
                fun270.call(args268, kw269)?
            });
            Ok(Val::None)
        })
    })?;
    // guide_world
    e.set("guide_world", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned274 = {
                let fun277 = e.get("passage")?;
                let mut args275 = Vec::new();
                let mut kw276 = Vec::new();
                fun277.call(args275, kw276)?
            }
            .get(Val::Str("bend_end_world_mm".into()))?;
            let unpack278 = unpack(assigned274.clone(), 3)?;
            e.set("x", unpack278[0].clone())?;
            e.set("y", unpack278[1].clone())?;
            e.set("z", unpack278[2].clone())?;
            return Ok({
                let fun281 = {
                    let fun284 = {
                        let fun287 = e.get("guide_native")?;
                        let mut args285 = Vec::new();
                        let mut kw286 = Vec::new();
                        fun287.call(args285, kw286)?
                    }
                    .attr("rotate")?;
                    let mut args282 = Vec::new();
                    let mut kw283 = Vec::new();
                    args282.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args282.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args282.push(unary("neg", Val::Float(90.0f64))?);
                    fun284.call(args282, kw283)?
                }
                .attr("translate")?;
                let mut args279 = Vec::new();
                let mut kw280 = Vec::new();
                args279.push({
                    let mut s = Vec::new();
                    s.push(binary("add", e.get("x")?, e.get("CHANNEL_CENTRE")?)?);
                    s.push(binary("sub", e.get("y")?, e.get("BEND_RADIUS")?)?);
                    s.push(e.get("z")?);
                    Val::tuple(s)
                });
                fun281.call(args279, kw280)?
            });
            Ok(Val::None)
        })
    })?;
    // features
    e.set("features", {
        let params = vec![("cup_height".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("cut".into()), {
                    let fun290 = e.get("channel_air")?;
                    let mut args288 = Vec::new();
                    let mut kw289 = Vec::new();
                    fun290.call(args288, kw289)?
                })?;
                d.set(Val::Str("channel_air".into()), {
                    let fun293 = e.get("channel_air")?;
                    let mut args291 = Vec::new();
                    let mut kw292 = Vec::new();
                    fun293.call(args291, kw292)?
                })?;
                d.set(Val::Str("holder_outer".into()), {
                    let fun296 = e.get("guide_world")?;
                    let mut args294 = Vec::new();
                    let mut kw295 = Vec::new();
                    fun296.call(args294, kw295)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
