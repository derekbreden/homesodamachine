#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let assigned2 = {
        let fun5 = e.get("next")?;
        let mut args3 = Vec::new();
        let mut kw4 = Vec::new();
        args3.push({
            let e = e.child();
            let out6 = Val::list(vec![]);
            for item7 in {
                let fun10 = {
                    let fun13 = e.get("Path")?;
                    let mut args11 = Vec::new();
                    let mut kw12 = Vec::new();
                    args11.push(e.get("__file__")?);
                    fun13.call(args11, kw12)?
                }
                .attr("resolve")?;
                let mut args8 = Vec::new();
                let mut kw9 = Vec::new();
                fun10.call(args8, kw9)?
            }
            .attr("parents")?
            .iter()?
            {
                e.set("p", item7)?;
                if {
                    let fun16 = binary(
                        "truediv",
                        e.get("p")?,
                        Val::Str("hardware/scripts/_rust_part.py".into()),
                    )?
                    .attr("is_file")?;
                    let mut args14 = Vec::new();
                    let mut kw15 = Vec::new();
                    fun16.call(args14, kw15)?
                }
                .truthy()?
                {
                    out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out6
        });
        fun5.call(args3, kw4)?
    };
    e.set("ROOT", assigned2.clone())?;
    let assigned17 = binary(
        "truediv",
        e.get("ROOT")?,
        Val::Str("hardware/printed-parts/cold-core".into()),
    )?;
    e.set("COLD", assigned17.clone())?;
    for item18 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("ROOT")?,
            Val::Str("hardware/scripts".into()),
        )?);
        s.push(e.get("COLD")?);
        s.push(binary(
            "truediv",
            e.get("ROOT")?,
            Val::Str("hardware/printed-parts/cadlib".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("path", item18)?;
        {
            let fun21 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args19 = Vec::new();
            let mut kw20 = Vec::new();
            args19.push(Val::Int(0i64));
            args19.push({
                let fun24 = e.get("str")?;
                let mut args22 = Vec::new();
                let mut kw23 = Vec::new();
                args22.push(e.get("path")?);
                fun24.call(args22, kw23)?
            });
            fun21.call(args19, kw20)?
        };
    }
    // stack_numbers
    e.set("stack_numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod25 = rt.import_module("_cadq_export")?;
            e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
            let mod26 = rt.import_module("_foam_cap")?;
            e.set("cap_face_z", rt.member("_foam_cap", "cap_face_z")?)?;
            e.set(
                "lid_total_height",
                rt.member("_foam_cap", "lid_total_height")?,
            )?;
            e.set("stack_floor_z", rt.member("_foam_cap", "stack_floor_z")?)?;
            let mod27 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            e.set("C_FOAM_SHELL", rt.member("_materials", "C_FOAM_SHELL")?)?;
            e.set("C_CAP_LID_TOP", rt.member("_materials", "C_CAP_LID_TOP")?)?;
            e.set("C_CAP_BOTTOM", rt.member("_materials", "C_CAP_BOTTOM")?)?;
            // piece
            e.set("piece", {
                let params = vec![
                    ("name".into(), None, false),
                    ("folder".into(), None, false),
                    ("color".into(), None, false),
                    ("rotation".into(), Some(Val::Float(0.0f64)), false),
                    ("z".into(), Some(Val::Float(0.0f64)), false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned28 = {
                        let mut str29 = String::new();
                        str29.push_str("hardware/printed-parts/cold-core/");
                        str29.push_str(&format(&e.get("folder")?, &String::new())?);
                        str29.push_str("/");
                        str29.push_str(&format(&e.get("name")?, &String::new())?);
                        str29.push_str(".step.npz");
                        Val::Str(str29)
                    };
                    e.set("model", assigned28.clone())?;
                    {
                        let fun32 = e.get("note_read")?;
                        let mut args30 = Vec::new();
                        let mut kw31 = Vec::new();
                        args30.push(binary("truediv", e.get("ROOT")?, e.get("model")?)?);
                        fun32.call(args30, kw31)?
                    };
                    return Ok({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("name".into()), e.get("name")?)?;
                        d.set(Val::Str("model".into()), e.get("model")?)?;
                        d.set(Val::Str("color".into()), {
                            let fun35 = e.get("list")?;
                            let mut args33 = Vec::new();
                            let mut kw34 = Vec::new();
                            args33.push({
                                let fun38 = e.get("linear")?;
                                let mut args36 = Vec::new();
                                let mut kw37 = Vec::new();
                                args36.push(e.get("color")?);
                                fun38.call(args36, kw37)?
                            });
                            fun35.call(args33, kw34)?
                        })?;
                        d.set(Val::Str("rotation_z_degrees".into()), e.get("rotation")?)?;
                        d.set(Val::Str("translation".into()), {
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            s.push(e.get("z")?);
                            Val::list(s)
                        })?;
                        d
                    });
                    Ok(Val::None)
                })
            })?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("models".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let fun41 = e.get("piece")?;
                        let mut args39 = Vec::new();
                        let mut kw40 = Vec::new();
                        args39.push(Val::Str("foam-shell".into()));
                        args39.push(Val::Str("foam-shell".into()));
                        args39.push(e.get("C_FOAM_SHELL")?);
                        fun41.call(args39, kw40)?
                    });
                    s.push({
                        let fun44 = e.get("piece")?;
                        let mut args42 = Vec::new();
                        let mut kw43 = Vec::new();
                        args42.push(Val::Str("foam-cap-lid-top".into()));
                        args42.push(Val::Str("foam-cap".into()));
                        args42.push(e.get("C_CAP_LID_TOP")?);
                        args42.push(Val::Float(180.0f64));
                        args42.push(binary(
                            "sub",
                            e.get("cap_face_z")?,
                            e.get("lid_total_height")?,
                        )?);
                        fun44.call(args42, kw43)?
                    });
                    s.push({
                        let fun47 = e.get("piece")?;
                        let mut args45 = Vec::new();
                        let mut kw46 = Vec::new();
                        args45.push(Val::Str("foam-cap-bottom".into()));
                        args45.push(Val::Str("foam-cap".into()));
                        args45.push(e.get("C_CAP_BOTTOM")?);
                        kw46.push(("z".into(), e.get("stack_floor_z")?));
                        fun47.call(args45, kw46)?
                    });
                    Val::list(s)
                })?;
                d.set(Val::Str("document".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("frame".into()),
                        Val::Str("foam assembly source".into()),
                    )?;
                    d.set(
                        Val::Str("schema".into()),
                        Val::Str("hsm-foam-assembly-1".into()),
                    )?;
                    d
                })?;
                d
            });
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
            let mod48 = rt.import_module("_cadq_export")?;
            e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
            e.set("source", rt.import_module("foam_assembly")?)?;
            let mod49 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            let mod50 = rt.import_module("_payload_rules")?;
            e.set(
                "LINEAR_DEFLECTION_RATIO",
                rt.member("_payload_rules", "LINEAR_DEFLECTION_RATIO")?,
            )?;
            let assigned51 = e.get("source")?.attr("routes")?;
            e.set("route", assigned51.clone())?;
            let assigned52 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("probes", assigned52.clone())?;
            for item53 in e.get("source")?.attr("cap_conduits")?.iter()? {
                e.set("name", item53)?;
                let assigned54 = if {
                    let v55 = e.get("name")?;
                    let v56 = Val::Str("reservoir-b-fill".into());
                    Val::Bool(compare("eq", v55.clone(), v56.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("route")?.attr("line_radius")?
                } else {
                    binary(
                        "sub",
                        e.get("source")?.attr("cap_conduit_bore_radius")?,
                        Val::Float(0.3f64),
                    )?
                };
                e.set("radius", assigned54.clone())?;
                if {
                    let v57 = e.get("name")?;
                    let v58 = e.get("source")?.attr("cap_cable_guides")?;
                    Val::Bool(compare("in", v57.clone(), v58.clone())?.truthy()?)
                }
                .truthy()?
                {
                    let assigned59 = {
                        let fun62 = e
                            .get("source")?
                            .attr("_above_mounts")?
                            .attr("cable_guide_points")?;
                        let mut args60 = Vec::new();
                        let mut kw61 = Vec::new();
                        args60.push(e.get("name")?);
                        fun62.call(args60, kw61)?
                    };
                    e.set("passage", assigned59.clone())?;
                    let assigned63 = {
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("kind".into()), Val::Str("route".into()))?;
                        d.set(Val::Str("points".into()), {
                            let e = e.child();
                            let out64 = Val::list(vec![]);
                            for item65 in e
                                .get("passage")?
                                .get(Val::Str("points_mm".into()))?
                                .iter()?
                            {
                                e.set("p", item65)?;
                                out64.attr("append")?.call(
                                    vec![{
                                        let fun68 = e.get("route")?.attr("world_point_in_shell")?;
                                        let mut args66 = Vec::new();
                                        let mut kw67 = Vec::new();
                                        args66.push(e.get("p")?);
                                        fun68.call(args66, kw67)?
                                    }],
                                    vec![],
                                )?;
                            }
                            out64
                        })?;
                        d.set(
                            Val::Str("bend".into()),
                            e.get("passage")?.get(Val::Str("bend_radius_mm".into()))?,
                        )?;
                        d
                    };
                    e.set("probe", assigned63.clone())?;
                } else {
                    if {
                        let v71 = {
                            let v72 = e.get("name")?;
                            let v73 = e.get("source")?.attr("cap_passive_guides")?;
                            Val::Bool(compare("in", v72.clone(), v73.clone())?.truthy()?)
                        };
                        if v71.truthy()? {
                            v71
                        } else {
                            {
                                let v69 = e.get("name")?;
                                let v70 = {
                                    let mut s = Vec::new();
                                    s.push(Val::Str("water-in".into()));
                                    s.push(Val::Str("carb-water-out".into()));
                                    s.push(Val::Str("reservoir-b-fill".into()));
                                    Val::tuple(s)
                                };
                                Val::Bool(compare("in", v69.clone(), v70.clone())?.truthy()?)
                            }
                        }
                    }
                    .truthy()?
                    {
                        let assigned74 = {
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("kind".into()), Val::Str("route".into()))?;
                            d.set(
                                Val::Str("points".into()),
                                e.get("route")?.attr("routes")?.get(e.get("name")?)?,
                            )?;
                            d.set(
                                Val::Str("bend".into()),
                                e.get("route")?.attr("route_bend_radius")?,
                            )?;
                            d
                        };
                        e.set("probe", assigned74.clone())?;
                    } else {
                        let assigned75 = {
                            let fun78 = e.get("source")?.attr("cap_conduit_station")?;
                            let mut args76 = Vec::new();
                            let mut kw77 = Vec::new();
                            args76.push(e.get("name")?);
                            fun78.call(args76, kw77)?
                        };
                        let unpack79 = unpack(assigned75.clone(), 2)?;
                        e.set("x", unpack79[0].clone())?;
                        e.set("y", unpack79[1].clone())?;
                        let assigned80 = {
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("kind".into()), Val::Str("cylinder".into()))?;
                            d.set(Val::Str("at".into()), {
                                let mut s = Vec::new();
                                s.push(e.get("x")?);
                                s.push(e.get("y")?);
                                s.push(binary(
                                    "sub",
                                    e.get("source")?.attr("foam_shell_outer_height")?,
                                    Val::Float(1.0f64),
                                )?);
                                Val::tuple(s)
                            })?;
                            d.set(
                                Val::Str("height".into()),
                                binary(
                                    "add",
                                    binary(
                                        "sub",
                                        e.get("source")?.attr("cap_face_z")?,
                                        e.get("source")?.attr("foam_shell_outer_height")?,
                                    )?,
                                    Val::Float(2.0f64),
                                )?,
                            )?;
                            d
                        };
                        e.set("probe", assigned80.clone())?;
                    }
                }
                {
                    let fun83 = e.get("probes")?.attr("append")?;
                    let mut args81 = Vec::new();
                    let mut kw82 = Vec::new();
                    args81.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("name".into()), e.get("name")?)?;
                        d.set(Val::Str("radius".into()), e.get("radius")?)?;
                        dict_extend(&d, e.get("probe")?)?;
                        d.set(Val::Str("lower_xy".into()), {
                            let fun86 = e.get("source")?.attr("spin_xy")?;
                            let mut args84 = Vec::new();
                            let mut kw85 = Vec::new();
                            args84.push(
                                e.get("source")?
                                    .attr("cap_conduit_floor_xy")?
                                    .get(e.get("name")?)?,
                            );
                            fun86.call(args84, kw85)?
                        })?;
                        d.set(
                            Val::Str("mouth".into()),
                            {
                                let fun89 = e.get("source")?.attr("cap_conduit_mouth")?;
                                let mut args87 = Vec::new();
                                let mut kw88 = Vec::new();
                                args87.push(e.get("name")?);
                                fun89.call(args87, kw88)?
                            }
                            .get(Val::Int(0i64))?,
                        )?;
                        d
                    });
                    fun83.call(args81, kw82)?
                };
            }
            let assigned90 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("obstacles", assigned90.clone())?;
            for item91 in {
                let fun108 = e.get("source")?.attr("RESERVOIRS")?.attr("items")?;
                let mut args106 = Vec::new();
                let mut kw107 = Vec::new();
                fun108.call(args106, kw107)?
            }
            .iter()?
            {
                let unpack109 = unpack(item91, 2)?;
                e.set("name", unpack109[0].clone())?;
                e.set("stem", unpack109[1].clone())?;
                for item92 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("name")?);
                        s.push(e.get("stem")?);
                        s.push(Val::Float(0.0f64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut str101 = String::new();
                            str101.push_str(&format(&e.get("name")?, &String::new())?);
                            str101.push_str("'s cap");
                            Val::Str(str101)
                        });
                        s.push({
                            let fun104 = e.get("stem")?.attr("replace")?;
                            let mut args102 = Vec::new();
                            let mut kw103 = Vec::new();
                            args102.push(Val::Str("reservoir".into()));
                            args102.push(Val::Str("reservoir-cap".into()));
                            fun104.call(args102, kw103)?
                        });
                        s.push(e.get("source")?.attr("RESERVOIR_CAP_Z")?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    let unpack105 = unpack(item92, 3)?;
                    e.set("label", unpack105[0].clone())?;
                    e.set("item", unpack105[1].clone())?;
                    e.set("z", unpack105[2].clone())?;
                    let assigned93 = {
                        let mut str94 = String::new();
                        str94.push_str("hardware/printed-parts/cold-core/reservoir/");
                        str94.push_str(&format(&e.get("item")?, &String::new())?);
                        str94.push_str(".step.npz");
                        Val::Str(str94)
                    };
                    e.set("model", assigned93.clone())?;
                    {
                        let fun97 = e.get("note_read")?;
                        let mut args95 = Vec::new();
                        let mut kw96 = Vec::new();
                        args95.push(binary("truediv", e.get("ROOT")?, e.get("model")?)?);
                        fun97.call(args95, kw96)?
                    };
                    {
                        let fun100 = e.get("obstacles")?.attr("append")?;
                        let mut args98 = Vec::new();
                        let mut kw99 = Vec::new();
                        args98.push({
                            let d = Val::dict(vec![]);
                            d.set(Val::Str("name".into()), e.get("label")?)?;
                            d.set(Val::Str("model".into()), e.get("model")?)?;
                            d.set(Val::Str("translation".into()), {
                                let mut s = Vec::new();
                                s.push(Val::Float(0.0f64));
                                s.push(Val::Float(0.0f64));
                                s.push(e.get("z")?);
                                Val::tuple(s)
                            })?;
                            d
                        });
                        fun100.call(args98, kw99)?
                    };
                }
            }
            return Ok({
                let d = Val::dict(vec![]);
                dict_extend(&d, {
                    let fun112 = e.get("stack_numbers")?;
                    let mut args110 = Vec::new();
                    let mut kw111 = Vec::new();
                    fun112.call(args110, kw111)?
                })?;
                d.set(Val::Str("obstacles".into()), e.get("obstacles")?)?;
                d.set(Val::Str("envelope".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("tank_radius".into()),
                        e.get("route")?.attr("carbonator_outer_radius")?,
                    )?;
                    d.set(
                        Val::Str("tank_z".into()),
                        e.get("route")?.attr("carbonator_envelope_z_range")?,
                    )?;
                    d.set(
                        Val::Str("coil_radius".into()),
                        e.get("route")?.attr("carbonator_coil_envelope_radius")?,
                    )?;
                    d.set(Val::Str("coil_z".into()), {
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            e.get("route")?.attr("evap_tail_low_z")?,
                            binary(
                                "truediv",
                                e.get("route")?.attr("lldpe_tube_od")?,
                                Val::Float(2.0f64),
                            )?,
                        )?);
                        s.push(binary(
                            "add",
                            e.get("route")?.attr("evap_tail_high_z")?,
                            binary(
                                "truediv",
                                e.get("route")?.attr("lldpe_tube_od")?,
                                Val::Float(2.0f64),
                            )?,
                        )?);
                        Val::tuple(s)
                    })?;
                    d
                })?;
                d.set(Val::Str("routes".into()), {
                    let e = e.child();
                    let out113 = Val::list(vec![]);
                    for item114 in {
                        let fun117 = e.get("sorted")?;
                        let mut args115 = Vec::new();
                        let mut kw116 = Vec::new();
                        args115.push({
                            let fun120 = e.get("route")?.attr("routes")?.attr("items")?;
                            let mut args118 = Vec::new();
                            let mut kw119 = Vec::new();
                            fun120.call(args118, kw119)?
                        });
                        fun117.call(args115, kw116)?
                    }
                    .iter()?
                    {
                        let unpack121 = unpack(item114, 2)?;
                        e.set("name", unpack121[0].clone())?;
                        e.set("points", unpack121[1].clone())?;
                        out113.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("name".into()), e.get("name")?)?;
                                d.set(Val::Str("points".into()), e.get("points")?)?;
                                d.set(Val::Str("color".into()), {
                                    let fun124 = e.get("linear")?;
                                    let mut args122 = Vec::new();
                                    let mut kw123 = Vec::new();
                                    args122.push(
                                        e.get("source")?
                                            .attr("ROUTE_COLORS")?
                                            .get(e.get("name")?)?,
                                    );
                                    fun124.call(args122, kw123)?
                                })?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out113
                })?;
                d.set(Val::Str("routing".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("stock_bend".into()),
                        e.get("route")?.attr("route_bend_radius")?,
                    )?;
                    d.set(
                        Val::Str("radius".into()),
                        e.get("route")?.attr("line_radius")?,
                    )?;
                    d.set(
                        Val::Str("floor".into()),
                        e.get("route")?.attr("bend_floor")?,
                    )?;
                    d.set(
                        Val::Str("ladder".into()),
                        e.get("route")?.attr("bend_ladder")?,
                    )?;
                    d.set(
                        Val::Str("touch_volume".into()),
                        e.get("route")?.attr("touch_volume")?,
                    )?;
                    d.set(Val::Str("stock".into()), {
                        let fun127 = e.get("vars")?;
                        let mut args125 = Vec::new();
                        let mut kw126 = Vec::new();
                        args125.push(e.get("route")?.attr("route_stock")?);
                        fun127.call(args125, kw126)?
                    })?;
                    d.set(
                        Val::Str("prv_flank_y".into()),
                        e.get("route")?.attr("prv_vent_flank_y")?,
                    )?;
                    d
                })?;
                d.set(Val::Str("report".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("floor".into()),
                        e.get("source")?.attr("stack_floor_z")?,
                    )?;
                    d.set(
                        Val::Str("face".into()),
                        e.get("source")?.attr("cap_face_z")?,
                    )?;
                    d.set(
                        Val::Str("lid_height".into()),
                        e.get("source")?.attr("lid_total_height")?,
                    )?;
                    d.set(Val::Str("probes".into()), e.get("probes")?)?;
                    d.set(
                        Val::Str("co2_points".into()),
                        e.get("route")?
                            .attr("routes")?
                            .get(Val::Str("co2-in".into()))?,
                    )?;
                    d.set(
                        Val::Str("co2_radius".into()),
                        binary(
                            "sub",
                            e.get("source")?.attr("co2_inlet_tube_radius")?,
                            Val::Float(0.3f64),
                        )?,
                    )?;
                    d.set(
                        Val::Str("co2_height".into()),
                        e.get("source")?
                            .attr("co2_inlet_xyz")?
                            .get(Val::Int(2i64))?,
                    )?;
                    d.set(
                        Val::Str("lower_probe_radius".into()),
                        binary(
                            "sub",
                            e.get("source")?.attr("cap_conduit_bore_radius")?,
                            Val::Float(0.3f64),
                        )?,
                    )?;
                    d.set(
                        Val::Str("screw_xy".into()),
                        e.get("source")?.attr("attachment_xy_positions")?,
                    )?;
                    d.set(
                        Val::Str("screw_probe_radius".into()),
                        binary(
                            "sub",
                            e.get("source")?.attr("screw_clearance_radius")?,
                            Val::Float(0.3f64),
                        )?,
                    )?;
                    d
                })?;
                d.set(Val::Str("presentation".into()), {
                    let d = Val::dict(vec![]);
                    d.set(
                        Val::Str("deflection_ratio".into()),
                        e.get("LINEAR_DEFLECTION_RATIO")?,
                    )?;
                    d.set(
                        Val::Str("simplification_fraction".into()),
                        Val::Float(0.5f64),
                    )?;
                    d
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
