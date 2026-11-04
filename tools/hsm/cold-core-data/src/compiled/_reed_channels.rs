#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("_cold_core_interface")?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "wall_thickness",
        rt.member("_cold_core_interface", "wall_thickness")?,
    )?;
    e.set(
        "reed_channel_inner_x",
        rt.member("_cold_core_interface", "reed_channel_inner_x")?,
    )?;
    e.set(
        "bag_pocket_far_inner_x",
        rt.member("_cold_core_interface", "bag_pocket_far_inner_x")?,
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
        "bag_pocket_outermost_x",
        rt.member("_cold_core_interface", "bag_pocket_outermost_x")?,
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
        "cap_conduit_shell_xy",
        rt.member("_cold_core_interface", "cap_conduit_shell_xy")?,
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
        "reed_x_depth",
        rt.member("_cold_core_interface", "reed_x_depth")?,
    )?;
    e.set(
        "reed_y_half_w",
        rt.member("_cold_core_interface", "reed_y_half_w")?,
    )?;
    e.set(
        "level_rod_y",
        rt.member("_cold_core_interface", "level_rod_y")?,
    )?;
    e.set("make_box", rt.member("_cold_core_interface", "make_box")?)?;
    e.set("bound", rt.member("_cold_core_interface", "bound")?)?;
    let assigned2 = e.get("wall_thickness")?;
    e.set("w", assigned2.clone())?;
    let assigned3 = Val::Int(4i64);
    e.set("reeds_per_reservoir", assigned3.clone())?;
    let assigned4 = e.get("level_rod_y")?;
    e.set("reed_y_center", assigned4.clone())?;
    let assigned5 = {
        let mut s = Vec::new();
        s.push(e.get("wall_and_floor_thickness")?);
        s.push(e.get("foam_shell_rim_z")?);
        Val::tuple(s)
    };
    e.set("reed_cavity_z_range", assigned5.clone())?;
    let assigned6 = {
        let mut s = Vec::new();
        s.push(Val::Int(0i64));
        s.push(e.get("foam_shell_rim_z")?);
        Val::tuple(s)
    };
    e.set("reed_envelope_z_range", assigned6.clone())?;
    let assigned7 = {
        let mut s = Vec::new();
        s.push(binary(
            "sub",
            e.get("reed_y_center")?,
            e.get("reed_y_half_w")?,
        )?);
        s.push(binary(
            "add",
            e.get("reed_y_center")?,
            e.get("reed_y_half_w")?,
        )?);
        Val::tuple(s)
    };
    e.set("reed_cavity_y_range", assigned7.clone())?;
    let assigned8 = {
        let mut s = Vec::new();
        s.push(binary(
            "sub",
            e.get("reed_cavity_y_range")?.get(Val::Int(0i64))?,
            e.get("w")?,
        )?);
        s.push(binary(
            "add",
            e.get("reed_cavity_y_range")?.get(Val::Int(1i64))?,
            e.get("w")?,
        )?);
        Val::tuple(s)
    };
    e.set("reed_envelope_y_range", assigned8.clone())?;
    let assigned9 = binary("truediv", e.get("lldpe_tube_od")?, Val::Float(2.0f64))?;
    e.set("reed_line_clearance", assigned9.clone())?;
    let assigned10 = {
        let d = Val::dict(vec![]);
        d.set(
            Val::Str("reed-cable-a".into()),
            unary("pos", Val::Int(1i64))?,
        )?;
        d
    };
    e.set("REED_CABLE_CONDUITS", assigned10.clone())?;
    // reed_channel_plan_room
    e.set("reed_channel_plan_room", {
        let params = vec![("x".into(), None, false), ("y".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned11 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("room", assigned11.clone())?;
            for item12 in {
                let mut s = Vec::new();
                s.push(unary("pos", Val::Int(1i64))?);
                s.push(unary("neg", Val::Int(1i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("s", item12)?;
                let assigned13 = {
                    let fun16 = e.get("sorted")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    args14.push({
                        let mut s = Vec::new();
                        s.push(binary("mul", e.get("s")?, e.get("reed_channel_inner_x")?)?);
                        s.push(binary(
                            "mul",
                            e.get("s")?,
                            binary(
                                "add",
                                binary(
                                    "add",
                                    e.get("reed_channel_inner_x")?,
                                    e.get("reed_x_depth")?,
                                )?,
                                e.get("w")?,
                            )?,
                        )?);
                        Val::tuple(s)
                    });
                    fun16.call(args14, kw15)?
                };
                e.set("env_x", assigned13.clone())?;
                let assigned17 = {
                    let fun20 = e.get("max")?;
                    let mut args18 = Vec::new();
                    let mut kw19 = Vec::new();
                    args18.push(binary(
                        "sub",
                        e.get("env_x")?.get(Val::Int(0i64))?,
                        e.get("x")?,
                    )?);
                    args18.push(binary(
                        "sub",
                        e.get("x")?,
                        e.get("env_x")?.get(Val::Int(1i64))?,
                    )?);
                    fun20.call(args18, kw19)?
                };
                e.set("dx", assigned17.clone())?;
                let assigned21 = {
                    let fun24 = e.get("max")?;
                    let mut args22 = Vec::new();
                    let mut kw23 = Vec::new();
                    args22.push(binary(
                        "sub",
                        e.get("reed_envelope_y_range")?.get(Val::Int(0i64))?,
                        e.get("y")?,
                    )?);
                    args22.push(binary(
                        "sub",
                        e.get("y")?,
                        e.get("reed_envelope_y_range")?.get(Val::Int(1i64))?,
                    )?);
                    fun24.call(args22, kw23)?
                };
                e.set("dy", assigned21.clone())?;
                {
                    let fun27 = e.get("room")?.attr("append")?;
                    let mut args25 = Vec::new();
                    let mut kw26 = Vec::new();
                    args25.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun30 = e.get("max")?;
                            let mut args28 = Vec::new();
                            let mut kw29 = Vec::new();
                            args28.push(e.get("dx")?);
                            args28.push(e.get("dy")?);
                            fun30.call(args28, kw29)?
                        });
                        s.push({
                            let mut str31 = String::new();
                            str31.push_str("reservoir ");
                            str31.push_str(&format(
                                &Val::Str("AB".into()).get({
                                    let v32 = e.get("s")?;
                                    let v33 = Val::Int(0i64);
                                    Val::Bool(compare("lt", v32.clone(), v33.clone())?.truthy()?)
                                })?,
                                &String::new(),
                            )?);
                            str31.push_str("'s reed channel");
                            Val::Str(str31)
                        });
                        Val::tuple(s)
                    });
                    fun27.call(args25, kw26)?
                };
            }
            return Ok({
                let fun36 = e.get("min")?;
                let mut args34 = Vec::new();
                let mut kw35 = Vec::new();
                args34.push(e.get("room")?);
                fun36.call(args34, kw35)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned37 = {
        let fun40 = e.get("bound")?;
        let mut args38 = Vec::new();
        let mut kw39 = Vec::new();
        args38.push(Val::Str("reed-channel-clear".into()));
        args38.push(Val::Str(
            "Every conduit's line falls clear of both reed channels".into(),
        ));
        args38.push({
            let mut str41 = String::new();
            str41.push_str(&format(
                &e.get("reed_line_clearance")?,
                &val_string({
                    let mut str42 = String::new();
                    str42.push_str("g");
                    Val::Str(str42)
                })?,
            )?);
            str41.push_str(" mm off the nearer channel");
            Val::Str(str41)
        });
        fun40.call(args38, kw39)?
    };
    e.set("_reed_clear", assigned37.clone())?;
    for item43 in e.get("cap_conduits")?.iter()? {
        e.set("_name", item43)?;
        if {
            let v44 = e.get("_name")?;
            let v45 = e.get("REED_CABLE_CONDUITS")?;
            Val::Bool(compare("in", v44.clone(), v45.clone())?.truthy()?)
        }
        .truthy()?
        {
            continue;
        }
        let assigned46 = {
            let fun49 = e.get("reed_channel_plan_room")?;
            let mut args47 = Vec::new();
            let mut kw48 = Vec::new();
            args47.extend(
                {
                    let e = e.child();
                    let out50 = Val::list(vec![]);
                    for item51 in e
                        .get("cap_conduit_floor_xy")?
                        .get(e.get("_name")?)?
                        .iter()?
                    {
                        e.set("v", item51)?;
                        out50
                            .attr("append")?
                            .call(vec![unary("neg", e.get("v")?)?], vec![])?;
                    }
                    out50
                }
                .iter()?,
            );
            fun49.call(args47, kw48)?
        };
        let unpack52 = unpack(assigned46.clone(), 2)?;
        e.set("_room", unpack52[0].clone())?;
        e.set("_what", unpack52[1].clone())?;
        {
            let fun55 = e.get("_reed_clear")?;
            let mut args53 = Vec::new();
            let mut kw54 = Vec::new();
            args53.push({
                let v56 = e.get("_room")?;
                let v57 = binary("sub", e.get("reed_line_clearance")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v56.clone(), v57.clone())?.truthy()?)
            });
            args53.push({let mut str58=String::new();str58.push_str("cap conduit ");str58.push_str(&format(&e.get("_name")?,&String::new())?);str58.push_str(": the line coming down it stands ");str58.push_str(&format(&e.get("_room")?,&val_string({let mut str59=String::new();str59.push_str(".3f");Val::Str(str59)})?)?);str58.push_str(" mm off ");str58.push_str(&format(&e.get("_what")?,&String::new())?);str58.push_str(", inside the ");str58.push_str(&format(&e.get("reed_line_clearance")?,&val_string({let mut str60=String::new();str60.push_str("g");Val::Str(str60)})?)?);str58.push_str(" mm a ⌀");str58.push_str(&format(&e.get("lldpe_tube_od")?,&val_string({let mut str61=String::new();str61.push_str("g");Val::Str(str61)})?)?);str58.push_str(" tube's own section takes — a line over a reed cavity is a void meeting a void and collides with nothing");Val::Str(str58)});
            fun55.call(args53, kw54)?
        };
    }
    let assigned62 = e.get("port_hole_radius")?;
    e.set("reed_cable_mouth_min", assigned62.clone())?;
    let assigned63 = {
        let fun66 = e.get("bound")?;
        let mut args64 = Vec::new();
        let mut kw65 = Vec::new();
        args64.push(Val::Str(
            "reed-cable-conduit-stands-over-its-channel".into(),
        ));
        args64.push(Val::Str(
            "Every reed-cable conduit opens on the channel its own cable climbs".into(),
        ));
        args64.push({
            let mut str67 = String::new();
            str67.push_str(&format(
                &e.get("reed_cable_mouth_min")?,
                &val_string({
                    let mut str68 = String::new();
                    str68.push_str("g");
                    Val::Str(str68)
                })?,
            )?);
            str67.push_str(" mm of shared mouth on each axis");
            Val::Str(str67)
        });
        fun66.call(args64, kw65)?
    };
    e.set("_reed_cable_over", assigned63.clone())?;
    for item69 in {
        let fun121 = e.get("sorted")?;
        let mut args119 = Vec::new();
        let mut kw120 = Vec::new();
        args119.push({
            let fun124 = e.get("REED_CABLE_CONDUITS")?.attr("items")?;
            let mut args122 = Vec::new();
            let mut kw123 = Vec::new();
            fun124.call(args122, kw123)?
        });
        fun121.call(args119, kw120)?
    }
    .iter()?
    {
        let unpack125 = unpack(item69, 2)?;
        e.set("_name", unpack125[0].clone())?;
        e.set("_side", unpack125[1].clone())?;
        if {
            let v70 = e.get("_name")?;
            let v71 = e.get("cap_conduits")?;
            Val::Bool(compare("not_in", v70.clone(), v71.clone())?.truthy()?)
        }
        .truthy()?
        {
            anyhow::bail!(
                "{}",
                val_string({
                    let fun74 = e.get("ValueError")?;
                    let mut args72 = Vec::new();
                    let mut kw73 = Vec::new();
                    args72.push({let mut str75=String::new();str75.push_str("`REED_CABLE_CONDUITS` names ");str75.push_str(&format(&builtin_call("repr",vec![e.get("_name")?],vec![])?,&String::new())?);str75.push_str(" as the bore reservoir ");str75.push_str(&format(&Val::Str("AB".into()).get({let v76=e.get("_side")?;let v77=Val::Int(0i64);Val::Bool(compare("lt",v76.clone(),v77.clone())?.truthy()?)})?,&String::new())?);str75.push_str("'s cable leaves by, and the cap carries no conduit by that name — the exemption above is what is still holding it out of `reed-channel-clear`.");Val::Str(str75)});
                    fun74.call(args72, kw73)?
                })?
            );
        }
        let assigned78 = {
            let e = e.child();
            let out79 = Val::list(vec![]);
            for item80 in e
                .get("cap_conduit_floor_xy")?
                .get(e.get("_name")?)?
                .iter()?
            {
                e.set("v", item80)?;
                out79
                    .attr("append")?
                    .call(vec![unary("neg", e.get("v")?)?], vec![])?;
            }
            out79
        };
        let unpack81 = unpack(assigned78.clone(), 2)?;
        e.set("_x", unpack81[0].clone())?;
        e.set("_y", unpack81[1].clone())?;
        let assigned82 = {
            let fun85 = e.get("sorted")?;
            let mut args83 = Vec::new();
            let mut kw84 = Vec::new();
            args83.push({
                let mut s = Vec::new();
                s.push(binary(
                    "mul",
                    e.get("_side")?,
                    e.get("reed_channel_inner_x")?,
                )?);
                s.push(binary(
                    "mul",
                    e.get("_side")?,
                    binary(
                        "add",
                        e.get("reed_channel_inner_x")?,
                        e.get("reed_x_depth")?,
                    )?,
                )?);
                Val::tuple(s)
            });
            fun85.call(args83, kw84)?
        };
        e.set("_cav_x", assigned82.clone())?;
        let assigned86 = e.get("reed_cavity_y_range")?;
        e.set("_cav_y", assigned86.clone())?;
        let assigned87 = binary(
            "sub",
            {
                let fun90 = e.get("min")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                args88.push(e.get("_cav_x")?.get(Val::Int(1i64))?);
                args88.push(binary("add", e.get("_x")?, e.get("port_hole_radius")?)?);
                fun90.call(args88, kw89)?
            },
            {
                let fun93 = e.get("max")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                args91.push(e.get("_cav_x")?.get(Val::Int(0i64))?);
                args91.push(binary("sub", e.get("_x")?, e.get("port_hole_radius")?)?);
                fun93.call(args91, kw92)?
            },
        )?;
        e.set("_mouth_x", assigned87.clone())?;
        let assigned94 = binary(
            "sub",
            {
                let fun97 = e.get("min")?;
                let mut args95 = Vec::new();
                let mut kw96 = Vec::new();
                args95.push(e.get("_cav_y")?.get(Val::Int(1i64))?);
                args95.push(binary("add", e.get("_y")?, e.get("port_hole_radius")?)?);
                fun97.call(args95, kw96)?
            },
            {
                let fun100 = e.get("max")?;
                let mut args98 = Vec::new();
                let mut kw99 = Vec::new();
                args98.push(e.get("_cav_y")?.get(Val::Int(0i64))?);
                args98.push(binary("sub", e.get("_y")?, e.get("port_hole_radius")?)?);
                fun100.call(args98, kw99)?
            },
        )?;
        e.set("_mouth_y", assigned94.clone())?;
        {
            let fun103 = e.get("_reed_cable_over")?;
            let mut args101 = Vec::new();
            let mut kw102 = Vec::new();
            args101.push({
                let v107 = {
                    let fun106 = e.get("min")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push(e.get("_mouth_x")?);
                    args104.push(e.get("_mouth_y")?);
                    fun106.call(args104, kw105)?
                };
                let v108 = binary("sub", e.get("reed_cable_mouth_min")?, Val::Float(1e-09f64))?;
                Val::Bool(compare("ge", v107.clone(), v108.clone())?.truthy()?)
            });
            args101.push({let mut str109=String::new();str109.push_str("reed-cable conduit ");str109.push_str(&format(&e.get("_name")?,&String::new())?);str109.push_str(": its bore at (");str109.push_str(&format(&e.get("_x")?,&val_string({let mut str110=String::new();str110.push_str(".3f");Val::Str(str110)})?)?);str109.push_str(", ");str109.push_str(&format(&e.get("_y")?,&val_string({let mut str111=String::new();str111.push_str(".3f");Val::Str(str111)})?)?);str109.push_str(") and reservoir ");str109.push_str(&format(&Val::Str("AB".into()).get({let v112=e.get("_side")?;let v113=Val::Int(0i64);Val::Bool(compare("lt",v112.clone(),v113.clone())?.truthy()?)})?,&String::new())?);str109.push_str("'s cavity share a mouth ");str109.push_str(&format(&e.get("_mouth_x")?,&val_string({let mut str114=String::new();str114.push_str(".3f");Val::Str(str114)})?)?);str109.push_str(" ");str109.push_str(&format(&{let fun117=e.get("chr")?;let mut args115=Vec::new();let mut kw116=Vec::new();args115.push(Val::Int(215i64));fun117.call(args115,kw116)?},&String::new())?);str109.push_str(" ");str109.push_str(&format(&e.get("_mouth_y")?,&val_string({let mut str118=String::new();str118.push_str(".3f");Val::Str(str118)})?)?);str109.push_str(" mm — the cable comes up the cavity and leaves by this bore, and what the two do not share is solid shell over the channel");Val::Str(str109)});
            fun103.call(args101, kw102)?
        };
    }
    // build_reed_channels
    e.set("build_reed_channels", {
        let params = vec![("side".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned126 = e.get("side")?;
            e.set("s", assigned126.clone())?;
            let assigned127 = binary("mul", e.get("s")?, e.get("reed_channel_inner_x")?)?;
            e.set("bag_x", assigned127.clone())?;
            let assigned128 = {
                let mut s = Vec::new();
                s.push(e.get("bag_x")?);
                s.push(binary(
                    "add",
                    e.get("bag_x")?,
                    binary(
                        "mul",
                        e.get("s")?,
                        binary("add", e.get("reed_x_depth")?, e.get("w")?)?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("reed_envelope_x_range", assigned128.clone())?;
            let assigned129 = {
                let mut s = Vec::new();
                s.push(e.get("bag_x")?);
                s.push(binary(
                    "add",
                    e.get("bag_x")?,
                    binary("mul", e.get("s")?, e.get("reed_x_depth")?)?,
                )?);
                Val::tuple(s)
            };
            e.set("reed_cavity_x_range", assigned129.clone())?;
            let assigned130 = {
                let fun133 = e.get("make_box")?;
                let mut args131 = Vec::new();
                let mut kw132 = Vec::new();
                args131.push(e.get("reed_envelope_x_range")?);
                args131.push(e.get("reed_envelope_y_range")?);
                args131.push(e.get("reed_envelope_z_range")?);
                fun133.call(args131, kw132)?
            };
            e.set("reed_envelope", assigned130.clone())?;
            let assigned134 = {
                let fun137 = e.get("make_box")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                args135.push(e.get("reed_cavity_x_range")?);
                args135.push(e.get("reed_cavity_y_range")?);
                args135.push(e.get("reed_cavity_z_range")?);
                fun137.call(args135, kw136)?
            };
            e.set("reed_cavity", assigned134.clone())?;
            let assigned138 = {
                let fun141 = e.get("make_box")?;
                let mut args139 = Vec::new();
                let mut kw140 = Vec::new();
                args139.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "mul",
                        e.get("s")?,
                        e.get("bag_pocket_far_inner_x")?,
                    )?);
                    s.push(binary("mul", e.get("s")?, e.get("reed_channel_inner_x")?)?);
                    Val::tuple(s)
                });
                args139.push(e.get("reed_envelope_y_range")?);
                args139.push({
                    let mut s = Vec::new();
                    s.push(e.get("foam_shell_outer_height")?);
                    s.push(e.get("foam_shell_rim_z")?);
                    Val::tuple(s)
                });
                fun141.call(args139, kw140)?
            };
            e.set("upper_back", assigned138.clone())?;
            return Ok({
                let fun144 = {
                    let fun147 = e.get("reed_envelope")?.attr("cut")?;
                    let mut args145 = Vec::new();
                    let mut kw146 = Vec::new();
                    args145.push(e.get("reed_cavity")?);
                    fun147.call(args145, kw146)?
                }
                .attr("union")?;
                let mut args142 = Vec::new();
                let mut kw143 = Vec::new();
                args142.push(e.get("upper_back")?);
                fun144.call(args142, kw143)?
            });
            Ok(Val::None)
        })
    })?;
    // cut_reed_channel_openings
    e.set("cut_reed_channel_openings", {
        let params = vec![("foam_shell".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            for item148 in {
                let mut s = Vec::new();
                s.push(unary("pos", Val::Int(1i64))?);
                s.push(unary("neg", Val::Int(1i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("s", item148)?;
                let assigned149 = binary("mul", e.get("s")?, e.get("bag_pocket_outermost_x")?)?;
                e.set("wall_x_outer", assigned149.clone())?;
                let assigned150 = binary("mul", e.get("s")?, e.get("bag_pocket_far_inner_x")?)?;
                e.set("wall_x_inner", assigned150.clone())?;
                let assigned151 = {
                    let fun154 = e.get("make_box")?;
                    let mut args152 = Vec::new();
                    let mut kw153 = Vec::new();
                    args152.push({
                        let mut s = Vec::new();
                        s.push(e.get("wall_x_inner")?);
                        s.push(e.get("wall_x_outer")?);
                        Val::tuple(s)
                    });
                    args152.push(e.get("reed_cavity_y_range")?);
                    args152.push({
                        let mut s = Vec::new();
                        s.push(e.get("wall_and_floor_thickness")?);
                        s.push(e.get("foam_shell_outer_height")?);
                        Val::tuple(s)
                    });
                    fun154.call(args152, kw153)?
                };
                e.set("reed_opening", assigned151.clone())?;
                let assigned155 = {
                    let fun158 = e.get("foam_shell")?.attr("cut")?;
                    let mut args156 = Vec::new();
                    let mut kw157 = Vec::new();
                    args156.push(e.get("reed_opening")?);
                    fun158.call(args156, kw157)?
                };
                e.set("foam_shell", assigned155.clone())?;
                let assigned159 = binary("mul", Val::Float(2.0f64), e.get("reed_y_half_w")?)?;
                e.set("rise", assigned159.clone())?;
                let assigned160 = e.get("foam_shell_outer_height")?;
                e.set("z", assigned160.clone())?;
                let assigned161 = {
                    let fun164 = e.get("sorted")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    args162.push({
                        let mut s = Vec::new();
                        s.push(e.get("wall_x_inner")?);
                        s.push(e.get("wall_x_outer")?);
                        Val::tuple(s)
                    });
                    fun164.call(args162, kw163)?
                };
                let unpack165 = unpack(assigned161.clone(), 2)?;
                e.set("x0", unpack165[0].clone())?;
                e.set("x1", unpack165[1].clone())?;
                let assigned166 = e.get("reed_cavity_y_range")?;
                let unpack167 = unpack(assigned166.clone(), 2)?;
                e.set("y0", unpack167[0].clone())?;
                e.set("y1", unpack167[1].clone())?;
                let assigned168 = {
                    let fun171 = e.get("cq")?.attr("Plane")?;
                    let mut args169 = Vec::new();
                    let mut kw170 = Vec::new();
                    kw170.push(("origin".into(), {
                        let mut s = Vec::new();
                        s.push(e.get("x0")?);
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    }));
                    kw170.push(("xDir".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    }));
                    kw170.push(("normal".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Float(1.0f64));
                        s.push(Val::Float(0.0f64));
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    }));
                    fun171.call(args169, kw170)?
                };
                e.set("plane", assigned168.clone())?;
                let assigned172 = {
                    let fun175 = {
                        let fun178 = {
                            let fun181 = {
                                let fun184 = {
                                    let fun187 = e.get("cq")?.attr("Workplane")?;
                                    let mut args185 = Vec::new();
                                    let mut kw186 = Vec::new();
                                    args185.push(e.get("plane")?);
                                    fun187.call(args185, kw186)?
                                }
                                .attr("polyline")?;
                                let mut args182 = Vec::new();
                                let mut kw183 = Vec::new();
                                args182.push({
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
                                        s.push(e.get("reed_y_center")?);
                                        s.push(binary("add", e.get("z")?, e.get("rise")?)?);
                                        Val::tuple(s)
                                    });
                                    Val::list(s)
                                });
                                fun184.call(args182, kw183)?
                            }
                            .attr("close")?;
                            let mut args179 = Vec::new();
                            let mut kw180 = Vec::new();
                            fun181.call(args179, kw180)?
                        }
                        .attr("extrude")?;
                        let mut args176 = Vec::new();
                        let mut kw177 = Vec::new();
                        args176.push(binary("sub", e.get("x1")?, e.get("x0")?)?);
                        fun178.call(args176, kw177)?
                    }
                    .attr("val")?;
                    let mut args173 = Vec::new();
                    let mut kw174 = Vec::new();
                    fun175.call(args173, kw174)?
                };
                e.set("roof", assigned172.clone())?;
                let assigned188 = {
                    let fun191 = e.get("foam_shell")?.attr("cut")?;
                    let mut args189 = Vec::new();
                    let mut kw190 = Vec::new();
                    args189.push(e.get("roof")?);
                    fun191.call(args189, kw190)?
                };
                e.set("foam_shell", assigned188.clone())?;
            }
            return Ok(e.get("foam_shell")?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
