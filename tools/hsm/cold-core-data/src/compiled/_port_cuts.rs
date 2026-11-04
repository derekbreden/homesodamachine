#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("fits", rt.import_module("fits")?)?;
    let mod1 = rt.import_module("_cold_core_interface")?;
    e.set(
        "wall_and_floor_thickness",
        rt.member("_cold_core_interface", "wall_and_floor_thickness")?,
    )?;
    e.set(
        "carbonator_support_ring_height",
        rt.member("_cold_core_interface", "carbonator_support_ring_height")?,
    )?;
    e.set(
        "outer_shell_wall",
        rt.member("_cold_core_interface", "outer_shell_wall")?,
    )?;
    e.set(
        "foam_shell_outer_height",
        rt.member("_cold_core_interface", "foam_shell_outer_height")?,
    )?;
    e.set(
        "water_outlet_climb_x",
        rt.member("_cold_core_interface", "water_outlet_climb_x")?,
    )?;
    e.set(
        "co2_inlet_y",
        rt.member("_cold_core_interface", "co2_inlet_y")?,
    )?;
    e.set(
        "co2_lane_x",
        rt.member("_cold_core_interface", "co2_lane_x")?,
    )?;
    e.set(
        "lldpe_tube_od",
        rt.member("_cold_core_interface", "lldpe_tube_od")?,
    )?;
    e.set(
        "port_lane_mid_y",
        rt.member("_cold_core_interface", "port_lane_mid_y")?,
    )?;
    e.set(
        "support_ring_radial_width",
        rt.member("_cold_core_interface", "support_ring_radial_width")?,
    )?;
    e.set(
        "carbonator_coil_envelope_radius",
        rt.member("_cold_core_interface", "carbonator_coil_envelope_radius")?,
    )?;
    e.set("make_box", rt.member("_cold_core_interface", "make_box")?)?;
    e.set("state", rt.member("_cold_core_interface", "state")?)?;
    let mod2 = rt.import_module("_support_ring")?;
    e.set(
        "slot_angular_width",
        rt.member("_support_ring", "slot_angular_width")?,
    )?;
    e.set("slot_clock", rt.member("_support_ring", "slot_clock")?)?;
    e.set("slot_count", rt.member("_support_ring", "slot_count")?)?;
    let assigned3 = Val::Float(11.2f64);
    e.set("bottom_port_drop", assigned3.clone())?;
    let assigned4 = binary(
        "sub",
        binary(
            "add",
            e.get("wall_and_floor_thickness")?,
            e.get("carbonator_support_ring_height")?,
        )?,
        e.get("bottom_port_drop")?,
    )?;
    e.set("front_face_port_z", assigned4.clone())?;
    let assigned5 = e.get("water_outlet_climb_x")?;
    e.set("water_outlet_ring_crossing_x", assigned5.clone())?;
    let assigned6 = e.get("carbonator_coil_envelope_radius")?;
    e.set("support_ring_outer_radius", assigned6.clone())?;
    let assigned7 = binary(
        "sub",
        e.get("support_ring_outer_radius")?,
        e.get("support_ring_radial_width")?,
    )?;
    e.set("support_ring_inner_radius", assigned7.clone())?;
    // ring_crossing_azimuths
    e.set("ring_crossing_azimuths", {
        let params = vec![
            ("x".into(), None, false),
            ("tube_radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned8 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("band", assigned8.clone())?;
            for item9 in {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("x")?, e.get("tube_radius")?)?);
                s.push(binary("add", e.get("x")?, e.get("tube_radius")?)?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("edge", item9)?;
                for item10 in {
                    let mut s = Vec::new();
                    s.push(e.get("support_ring_inner_radius")?);
                    s.push(e.get("support_ring_outer_radius")?);
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("radius", item10)?;
                    if {
                        let v14 = {
                            let fun13 = e.get("abs")?;
                            let mut args11 = Vec::new();
                            let mut kw12 = Vec::new();
                            args11.push(e.get("edge")?);
                            fun13.call(args11, kw12)?
                        };
                        let v15 = e.get("radius")?;
                        Val::Bool(compare("ge", v14.clone(), v15.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        continue;
                    }
                    {
                        let fun18 = e.get("band")?.attr("append")?;
                        let mut args16 = Vec::new();
                        let mut kw17 = Vec::new();
                        args16.push(binary(
                            "mod",
                            {
                                let fun21 = e.get("math")?.attr("degrees")?;
                                let mut args19 = Vec::new();
                                let mut kw20 = Vec::new();
                                args19.push({
                                    let fun24 = e.get("math")?.attr("atan2")?;
                                    let mut args22 = Vec::new();
                                    let mut kw23 = Vec::new();
                                    args22.push(unary("neg", {
                                        let fun27 = e.get("math")?.attr("sqrt")?;
                                        let mut args25 = Vec::new();
                                        let mut kw26 = Vec::new();
                                        args25.push(binary(
                                            "sub",
                                            binary("pow", e.get("radius")?, Val::Int(2i64))?,
                                            binary("pow", e.get("edge")?, Val::Int(2i64))?,
                                        )?);
                                        fun27.call(args25, kw26)?
                                    })?);
                                    args22.push(e.get("edge")?);
                                    fun24.call(args22, kw23)?
                                });
                                fun21.call(args19, kw20)?
                            },
                            Val::Float(360.0f64),
                        )?);
                        fun18.call(args16, kw17)?
                    };
                }
            }
            return Ok(if e.get("band")?.truthy()? {
                {
                    let mut s = Vec::new();
                    s.push({
                        let fun30 = e.get("min")?;
                        let mut args28 = Vec::new();
                        let mut kw29 = Vec::new();
                        args28.push(e.get("band")?);
                        fun30.call(args28, kw29)?
                    });
                    s.push({
                        let fun33 = e.get("max")?;
                        let mut args31 = Vec::new();
                        let mut kw32 = Vec::new();
                        args31.push(e.get("band")?);
                        fun33.call(args31, kw32)?
                    });
                    Val::tuple(s)
                }
            } else {
                Val::None
            });
            Ok(Val::None)
        })
    })?;
    // segment_ring_azimuths
    e.set("segment_ring_azimuths", {
        let params = vec![
            ("a".into(), None, false),
            ("b".into(), None, false),
            ("tube_radius".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned34 = {
                let mut s = Vec::new();
                s.push(e.get("a")?.get(Val::Slice {
                    start: None,
                    stop: Some(Val::Int(2i64).integer()?),
                    step: 1,
                })?);
                s.push(e.get("b")?.get(Val::Slice {
                    start: None,
                    stop: Some(Val::Int(2i64).integer()?),
                    step: 1,
                })?);
                Val::tuple(s)
            };
            let unpack35 = unpack(assigned34.clone(), 2)?;
            let unpack36 = unpack(unpack35[0].clone(), 2)?;
            e.set("ax", unpack36[0].clone())?;
            e.set("ay", unpack36[1].clone())?;
            let unpack37 = unpack(unpack35[1].clone(), 2)?;
            e.set("bx", unpack37[0].clone())?;
            e.set("by", unpack37[1].clone())?;
            let assigned38 = {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("bx")?, e.get("ax")?)?);
                s.push(binary("sub", e.get("by")?, e.get("ay")?)?);
                Val::tuple(s)
            };
            let unpack39 = unpack(assigned38.clone(), 2)?;
            e.set("dx", unpack39[0].clone())?;
            e.set("dy", unpack39[1].clone())?;
            let assigned40 = {
                let fun43 = e.get("math")?.attr("hypot")?;
                let mut args41 = Vec::new();
                let mut kw42 = Vec::new();
                args41.push(e.get("dx")?);
                args41.push(e.get("dy")?);
                fun43.call(args41, kw42)?
            };
            e.set("length", assigned40.clone())?;
            if {
                let v44 = e.get("length")?;
                let v45 = Val::Float(1e-09f64);
                Val::Bool(compare("lt", v44.clone(), v45.clone())?.truthy()?)
            }
            .truthy()?
            {
                return Ok(Val::None);
            }
            let assigned46 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    unary("neg", e.get("dy")?)?,
                    e.get("length")?,
                )?);
                s.push(binary("truediv", e.get("dx")?, e.get("length")?)?);
                Val::tuple(s)
            };
            let unpack47 = unpack(assigned46.clone(), 2)?;
            e.set("nx", unpack47[0].clone())?;
            e.set("ny", unpack47[1].clone())?;
            let assigned48 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("band", assigned48.clone())?;
            for item49 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Float(1.0f64))?);
                s.push(Val::Float(1.0f64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("side", item49)?;
                let assigned50 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("ax")?,
                        binary(
                            "mul",
                            binary("mul", e.get("nx")?, e.get("side")?)?,
                            e.get("tube_radius")?,
                        )?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("ay")?,
                        binary(
                            "mul",
                            binary("mul", e.get("ny")?, e.get("side")?)?,
                            e.get("tube_radius")?,
                        )?,
                    )?);
                    Val::tuple(s)
                };
                let unpack51 = unpack(assigned50.clone(), 2)?;
                e.set("ox", unpack51[0].clone())?;
                e.set("oy", unpack51[1].clone())?;
                for item52 in {
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("support_ring_inner_radius")?,
                        e.get("tube_radius")?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("support_ring_outer_radius")?,
                        e.get("tube_radius")?,
                    )?);
                    Val::tuple(s)
                }
                .iter()?
                {
                    e.set("radius", item52)?;
                    let assigned53 = binary(
                        "add",
                        binary("mul", e.get("dx")?, e.get("dx")?)?,
                        binary("mul", e.get("dy")?, e.get("dy")?)?,
                    )?;
                    e.set("qa", assigned53.clone())?;
                    let assigned54 = binary(
                        "mul",
                        Val::Float(2.0f64),
                        binary(
                            "add",
                            binary("mul", e.get("ox")?, e.get("dx")?)?,
                            binary("mul", e.get("oy")?, e.get("dy")?)?,
                        )?,
                    )?;
                    e.set("qb", assigned54.clone())?;
                    let assigned55 = binary(
                        "sub",
                        binary(
                            "add",
                            binary("mul", e.get("ox")?, e.get("ox")?)?,
                            binary("mul", e.get("oy")?, e.get("oy")?)?,
                        )?,
                        binary("mul", e.get("radius")?, e.get("radius")?)?,
                    )?;
                    e.set("qc", assigned55.clone())?;
                    let assigned56 = binary(
                        "sub",
                        binary("mul", e.get("qb")?, e.get("qb")?)?,
                        binary(
                            "mul",
                            binary("mul", Val::Float(4.0f64), e.get("qa")?)?,
                            e.get("qc")?,
                        )?,
                    )?;
                    e.set("disc", assigned56.clone())?;
                    if {
                        let v57 = e.get("disc")?;
                        let v58 = Val::Float(0.0f64);
                        Val::Bool(compare("lt", v57.clone(), v58.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        continue;
                    }
                    for item59 in {
                        let mut s = Vec::new();
                        s.push(binary(
                            "truediv",
                            binary("sub", unary("neg", e.get("qb")?)?, {
                                let fun74 = e.get("math")?.attr("sqrt")?;
                                let mut args72 = Vec::new();
                                let mut kw73 = Vec::new();
                                args72.push(e.get("disc")?);
                                fun74.call(args72, kw73)?
                            })?,
                            binary("mul", Val::Float(2.0f64), e.get("qa")?)?,
                        )?);
                        s.push(binary(
                            "truediv",
                            binary("add", unary("neg", e.get("qb")?)?, {
                                let fun77 = e.get("math")?.attr("sqrt")?;
                                let mut args75 = Vec::new();
                                let mut kw76 = Vec::new();
                                args75.push(e.get("disc")?);
                                fun77.call(args75, kw76)?
                            })?,
                            binary("mul", Val::Float(2.0f64), e.get("qa")?)?,
                        )?);
                        Val::tuple(s)
                    }
                    .iter()?
                    {
                        e.set("t", item59)?;
                        if {
                            let v60 = Val::Float(0.0f64);
                            let v61 = e.get("t")?;
                            let v62 = Val::Float(1.0f64);
                            Val::Bool(
                                compare("le", v60.clone(), v61.clone())?.truthy()?
                                    && compare("le", v61.clone(), v62.clone())?.truthy()?,
                            )
                        }
                        .truthy()?
                        {
                            {
                                let fun65 = e.get("band")?.attr("append")?;
                                let mut args63 = Vec::new();
                                let mut kw64 = Vec::new();
                                args63.push(binary(
                                    "mod",
                                    {
                                        let fun68 = e.get("math")?.attr("degrees")?;
                                        let mut args66 = Vec::new();
                                        let mut kw67 = Vec::new();
                                        args66.push({
                                            let fun71 = e.get("math")?.attr("atan2")?;
                                            let mut args69 = Vec::new();
                                            let mut kw70 = Vec::new();
                                            args69.push(binary(
                                                "add",
                                                e.get("oy")?,
                                                binary("mul", e.get("t")?, e.get("dy")?)?,
                                            )?);
                                            args69.push(binary(
                                                "add",
                                                e.get("ox")?,
                                                binary("mul", e.get("t")?, e.get("dx")?)?,
                                            )?);
                                            fun71.call(args69, kw70)?
                                        });
                                        fun68.call(args66, kw67)?
                                    },
                                    Val::Float(360.0f64),
                                )?);
                                fun65.call(args63, kw64)?
                            };
                        }
                    }
                }
            }
            return Ok(if e.get("band")?.truthy()? {
                {
                    let mut s = Vec::new();
                    s.push({
                        let fun80 = e.get("min")?;
                        let mut args78 = Vec::new();
                        let mut kw79 = Vec::new();
                        args78.push(e.get("band")?);
                        fun80.call(args78, kw79)?
                    });
                    s.push({
                        let fun83 = e.get("max")?;
                        let mut args81 = Vec::new();
                        let mut kw82 = Vec::new();
                        args81.push(e.get("band")?);
                        fun83.call(args81, kw82)?
                    });
                    Val::tuple(s)
                }
            } else {
                Val::None
            });
            Ok(Val::None)
        })
    })?;
    // ring_slot_spans
    e.set("ring_slot_spans", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned84 = binary("truediv", Val::Float(360.0f64), e.get("slot_count")?)?;
            e.set("step", assigned84.clone())?;
            return Ok({
                let e = e.child();
                let out85 = Val::list(vec![]);
                for item86 in {
                    let fun89 = e.get("range")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(e.get("slot_count")?);
                    fun89.call(args87, kw88)?
                }
                .iter()?
                {
                    e.set("i", item86)?;
                    out85.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(binary(
                                "sub",
                                binary(
                                    "add",
                                    binary(
                                        "mul",
                                        e.get("step")?,
                                        binary("add", e.get("i")?, Val::Float(0.5f64))?,
                                    )?,
                                    e.get("slot_clock")?,
                                )?,
                                binary(
                                    "truediv",
                                    e.get("slot_angular_width")?,
                                    Val::Float(2.0f64),
                                )?,
                            )?);
                            s.push(binary(
                                "add",
                                binary(
                                    "add",
                                    binary(
                                        "mul",
                                        e.get("step")?,
                                        binary("add", e.get("i")?, Val::Float(0.5f64))?,
                                    )?,
                                    e.get("slot_clock")?,
                                )?,
                                binary(
                                    "truediv",
                                    e.get("slot_angular_width")?,
                                    Val::Float(2.0f64),
                                )?,
                            )?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out85
            });
            Ok(Val::None)
        })
    })?;
    let assigned90 = {
        let fun93 = e.get("ring_crossing_azimuths")?;
        let mut args91 = Vec::new();
        let mut kw92 = Vec::new();
        args91.push(e.get("water_outlet_ring_crossing_x")?);
        args91.push(binary(
            "truediv",
            e.get("lldpe_tube_od")?,
            Val::Float(2.0f64),
        )?);
        fun93.call(args91, kw92)?
    };
    e.set("_crossing", assigned90.clone())?;
    {
        let fun96 = e.get("state")?;
        let mut args94 = Vec::new();
        let mut kw95 = Vec::new();
        args94.push(Val::Str("water-outlet-slot".into()));
        args94.push(Val::Str(
            "The carbonated-water outlet crosses the support ring in one slot".into(),
        ));
        args94.push(Val::Str("one slot holding the whole crossing".into()));
        args94.push({
            let v111 = {
                let v112 = e.get("_crossing")?;
                let v113 = Val::None;
                Val::Bool(compare("is_not", v112.clone(), v113.clone())?.truthy()?)
            };
            if v111.truthy()? {
                {
                    let fun99 = e.get("any")?;
                    let mut args97 = Vec::new();
                    let mut kw98 = Vec::new();
                    args97.push({
                        let e = e.child();
                        let out100 = Val::list(vec![]);
                        for item101 in {
                            let fun104 = e.get("ring_slot_spans")?;
                            let mut args102 = Vec::new();
                            let mut kw103 = Vec::new();
                            fun104.call(args102, kw103)?
                        }
                        .iter()?
                        {
                            let unpack105 = unpack(item101, 2)?;
                            e.set("lo", unpack105[0].clone())?;
                            e.set("hi", unpack105[1].clone())?;
                            out100.attr("append")?.call(
                                vec![{
                                    let v108 = {
                                        let v109 = e.get("lo")?;
                                        let v110 = e.get("_crossing")?.get(Val::Int(0i64))?;
                                        Val::Bool(
                                            compare("le", v109.clone(), v110.clone())?.truthy()?,
                                        )
                                    };
                                    if v108.truthy()? {
                                        {
                                            let v106 = e.get("_crossing")?.get(Val::Int(1i64))?;
                                            let v107 = e.get("hi")?;
                                            Val::Bool(
                                                compare("le", v106.clone(), v107.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                    } else {
                                        v108
                                    }
                                }],
                                vec![],
                            )?;
                        }
                        out100
                    });
                    fun99.call(args97, kw98)?
                }
            } else {
                v111
            }
        });
        args94.push(if {let v114=e.get("_crossing")?;let v115=Val::None;Val::Bool(compare("is",v114.clone(),v115.clone())?.truthy()?)}.truthy()? {{let mut str116=String::new();str116.push_str("the carbonated-water outlet at x ");str116.push_str(&format(&e.get("water_outlet_ring_crossing_x")?,&val_string({let mut str117=String::new();str117.push_str("g");Val::Str(str117)})?)?);str116.push_str(" passes clear outboard of the carbonator support ring and crosses no azimuth of it — the slot it is struck against is not the ring this line meets");Val::Str(str116)}} else {{let mut str118=String::new();str118.push_str("the carbonated-water outlet crosses the carbonator support ring at x ");str118.push_str(&format(&e.get("water_outlet_ring_crossing_x")?,&val_string({let mut str119=String::new();str119.push_str("g");Val::Str(str119)})?)?);str118.push_str(" over azimuths ");str118.push_str(&format(&e.get("_crossing")?.get(Val::Int(0i64))?,&val_string({let mut str120=String::new();str120.push_str(".1f");Val::Str(str120)})?)?);str118.push_str("°..");str118.push_str(&format(&e.get("_crossing")?.get(Val::Int(1i64))?,&val_string({let mut str121=String::new();str121.push_str(".1f");Val::Str(str121)})?)?);str118.push_str("°, which no slot of ");str118.push_str(&format(&{let fun124=e.get("ring_slot_spans")?;let mut args122=Vec::new();let mut kw123=Vec::new();fun124.call(args122,kw123)?},&String::new())?);str118.push_str(" holds — the line would have to be bored through a bearing segment");Val::Str(str118)}});
        fun96.call(args94, kw95)?
    };
    let assigned125 = {
        let mut s = Vec::new();
        s.push(Val::Float(0.0f64));
        s.push(e.get("co2_inlet_y")?);
        s.push(e.get("front_face_port_z")?);
        Val::tuple(s)
    };
    e.set("co2_inlet_xyz", assigned125.clone())?;
    let assigned126 = {
        let mut s = Vec::new();
        s.push(e.get("co2_lane_x")?);
        s.push(binary(
            "add",
            e.get("port_lane_mid_y")?,
            Val::Float(2.5f64),
        )?);
        s.push(e.get("front_face_port_z")?);
        Val::tuple(s)
    };
    e.set("co2_inlet_lane_xyz", assigned126.clone())?;
    let assigned127 = binary(
        "sub",
        {
            let fun130 = e.get("abs")?;
            let mut args128 = Vec::new();
            let mut kw129 = Vec::new();
            args128.push(e.get("port_lane_mid_y")?);
            fun130.call(args128, kw129)?
        },
        e.get("support_ring_outer_radius")?,
    )?;
    e.set("co2_bore_to_ring", assigned127.clone())?;
    let assigned131 = {
        let fun134 = e.get("segment_ring_azimuths")?;
        let mut args132 = Vec::new();
        let mut kw133 = Vec::new();
        args132.push(e.get("co2_inlet_lane_xyz")?);
        args132.push(e.get("co2_inlet_xyz")?);
        args132.push(binary(
            "truediv",
            e.get("lldpe_tube_od")?,
            Val::Float(2.0f64),
        )?);
        fun134.call(args132, kw133)?
    };
    e.set("_co2_crossing", assigned131.clone())?;
    {
        let fun137 = e.get("state")?;
        let mut args135 = Vec::new();
        let mut kw136 = Vec::new();
        args135.push(Val::Str("co2-inlet-slot".into()));
        args135.push(Val::Str(
            "The CO2 reach in crosses the support ring in one slot".into(),
        ));
        args135.push(Val::Str("one slot holding the whole crossing".into()));
        args135.push({
            let v152 = {
                let v153 = e.get("_co2_crossing")?;
                let v154 = Val::None;
                Val::Bool(compare("is_not", v153.clone(), v154.clone())?.truthy()?)
            };
            if v152.truthy()? {
                {
                    let fun140 = e.get("any")?;
                    let mut args138 = Vec::new();
                    let mut kw139 = Vec::new();
                    args138.push({
                        let e = e.child();
                        let out141 = Val::list(vec![]);
                        for item142 in {
                            let fun145 = e.get("ring_slot_spans")?;
                            let mut args143 = Vec::new();
                            let mut kw144 = Vec::new();
                            fun145.call(args143, kw144)?
                        }
                        .iter()?
                        {
                            let unpack146 = unpack(item142, 2)?;
                            e.set("lo", unpack146[0].clone())?;
                            e.set("hi", unpack146[1].clone())?;
                            out141.attr("append")?.call(
                                vec![{
                                    let v149 = {
                                        let v150 = e.get("lo")?;
                                        let v151 = e.get("_co2_crossing")?.get(Val::Int(0i64))?;
                                        Val::Bool(
                                            compare("le", v150.clone(), v151.clone())?.truthy()?,
                                        )
                                    };
                                    if v149.truthy()? {
                                        {
                                            let v147 =
                                                e.get("_co2_crossing")?.get(Val::Int(1i64))?;
                                            let v148 = e.get("hi")?;
                                            Val::Bool(
                                                compare("le", v147.clone(), v148.clone())?
                                                    .truthy()?,
                                            )
                                        }
                                    } else {
                                        v149
                                    }
                                }],
                                vec![],
                            )?;
                        }
                        out141
                    });
                    fun140.call(args138, kw139)?
                }
            } else {
                v152
            }
        });
        args135.push(if {let v155=e.get("_co2_crossing")?;let v156=Val::None;Val::Bool(compare("is",v155.clone(),v156.clone())?.truthy()?)}.truthy()? {{let mut str157=String::new();str157.push_str("the CO2 reach in from x ");str157.push_str(&format(&e.get("co2_inlet_lane_xyz")?.get(Val::Int(0i64))?,&val_string({let mut str158=String::new();str158.push_str("g");Val::Str(str158)})?)?);str157.push_str(" passes clear of the ring this is struck against");Val::Str(str157)}} else {{let mut str159=String::new();str159.push_str("the CO2 reach in from x ");str159.push_str(&format(&e.get("co2_inlet_lane_xyz")?.get(Val::Int(0i64))?,&val_string({let mut str160=String::new();str160.push_str("g");Val::Str(str160)})?)?);str159.push_str(" crosses the carbonator support ring over azimuths ");str159.push_str(&format(&e.get("_co2_crossing")?.get(Val::Int(0i64))?,&val_string({let mut str161=String::new();str161.push_str(".1f");Val::Str(str161)})?)?);str159.push_str("°..");str159.push_str(&format(&e.get("_co2_crossing")?.get(Val::Int(1i64))?,&val_string({let mut str162=String::new();str162.push_str(".1f");Val::Str(str162)})?)?);str159.push_str("°, which no slot of ");str159.push_str(&format(&{let fun165=e.get("ring_slot_spans")?;let mut args163=Vec::new();let mut kw164=Vec::new();fun165.call(args163,kw164)?},&String::new())?);str159.push_str(" holds — the line would have to be bored through a bearing segment that carries the carbonator");Val::Str(str159)}});
        fun137.call(args135, kw136)?
    };
    // cut_prv_vent_port
    e.set("cut_prv_vent_port", {
        let params = vec![("foam_shell".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod166 = rt.import_module("_internal_routes")?;
            e.set(
                "route_corridor",
                rt.member("_internal_routes", "route_corridor")?,
            )?;
            let assigned167 = {
                let fun170 = e.get("route_corridor")?;
                let mut args168 = Vec::new();
                let mut kw169 = Vec::new();
                args168.push(Val::Str("prv-vent".into()));
                fun170.call(args168, kw169)?
            };
            e.set("corridor", assigned167.clone())?;
            return Ok({
                let fun173 = {
                    let fun176 = e.get("foam_shell")?.attr("cut")?;
                    let mut args174 = Vec::new();
                    let mut kw175 = Vec::new();
                    args174.push(e.get("corridor")?);
                    fun176.call(args174, kw175)?
                }
                .attr("cut")?;
                let mut args171 = Vec::new();
                let mut kw172 = Vec::new();
                args171.push({
                    let fun179 = e.get("corridor")?.attr("translate")?;
                    let mut args177 = Vec::new();
                    let mut kw178 = Vec::new();
                    args177.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(e.get("fits")?.attr("supported_surface")?);
                        Val::tuple(s)
                    });
                    fun179.call(args177, kw178)?
                });
                fun173.call(args171, kw172)?
            });
            Ok(Val::None)
        })
    })?;
    // cut_copper_ports
    e.set("cut_copper_ports", {
        let params = vec![("foam_shell".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod180 = rt.import_module("_copper_ports")?;
            e.set("hole_radius", rt.member("_copper_ports", "hole_radius")?)?;
            e.set("stations", rt.member("_copper_ports", "stations")?)?;
            for item181 in {
                let fun198 = {
                    let fun201 = e.get("stations")?;
                    let mut args199 = Vec::new();
                    let mut kw200 = Vec::new();
                    fun201.call(args199, kw200)?
                }
                .attr("values")?;
                let mut args196 = Vec::new();
                let mut kw197 = Vec::new();
                fun198.call(args196, kw197)?
            }
            .iter()?
            {
                let unpack202 = unpack(item181, 2)?;
                let unpack203 = unpack(unpack202[0].clone(), 3)?;
                e.set("x", unpack203[0].clone())?;
                e.set("y", unpack203[1].clone())?;
                e.set("z", unpack203[2].clone())?;
                e.set("_axis", unpack202[1].clone())?;
                let assigned182 = {
                    let fun185 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                    let mut args183 = Vec::new();
                    let mut kw184 = Vec::new();
                    args183.push(e.get("hole_radius")?);
                    args183.push(binary(
                        "add",
                        e.get("outer_shell_wall")?,
                        Val::Float(4.0f64),
                    )?);
                    args183.push({
                        let fun188 = e.get("cq")?.attr("Vector")?;
                        let mut args186 = Vec::new();
                        let mut kw187 = Vec::new();
                        args186.push(binary("sub", e.get("x")?, Val::Float(2.0f64))?);
                        args186.push(e.get("y")?);
                        args186.push(e.get("z")?);
                        fun188.call(args186, kw187)?
                    });
                    args183.push({
                        let fun191 = e.get("cq")?.attr("Vector")?;
                        let mut args189 = Vec::new();
                        let mut kw190 = Vec::new();
                        args189.push(Val::Float(1.0f64));
                        args189.push(Val::Float(0.0f64));
                        args189.push(Val::Float(0.0f64));
                        fun191.call(args189, kw190)?
                    });
                    fun185.call(args183, kw184)?
                };
                e.set("bore", assigned182.clone())?;
                let assigned192 = {
                    let fun195 = e.get("foam_shell")?.attr("cut")?;
                    let mut args193 = Vec::new();
                    let mut kw194 = Vec::new();
                    args193.push(e.get("bore")?);
                    fun195.call(args193, kw194)?
                };
                e.set("foam_shell", assigned192.clone())?;
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
