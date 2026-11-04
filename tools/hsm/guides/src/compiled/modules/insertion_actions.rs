//! Guide recipe: `tools/install-guide/insertion_actions.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("struct", rt.import_module("struct")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod2 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    let assigned3 = {
        let fun6 = {
            let fun9 = e.get("Path")?;
            let mut args7 = Vec::new();
            let mut kw8 = Vec::new();
            args7.push(e.get("__file__")?);
            fun9.call(args7, kw8)?
        }
        .attr("resolve")?;
        let mut args4 = Vec::new();
        let mut kw5 = Vec::new();
        fun6.call(args4, kw5)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned3.clone())?;
    let assigned10 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HARDWARE", assigned10.clone())?;
    let assigned11 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/out".into()),
    )?;
    e.set("SNAPSHOTS", assigned11.clone())?;
    let assigned12 = binary(
        "truediv",
        e.get("SNAPSHOTS")?,
        Val::Str("insertion-actions".into()),
    )?;
    e.set("OUT", assigned12.clone())?;
    let assigned13 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/art/insertion-actions".into()),
    )?;
    e.set("ART", assigned13.clone())?;
    {
        let fun16 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args14 = Vec::new();
        let mut kw15 = Vec::new();
        args14.push(Val::Int(0i64));
        args14.push({
            let fun19 = e.get("str")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun19.call(args17, kw18)?
        });
        fun16.call(args14, kw15)?
    };
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    let assigned20 = Val::Float(25.0f64);
    e.set("POWER_RETREAT", assigned20.clone())?;
    let assigned21 = Val::Float(50.0f64);
    e.set("BOTTLE_LIFT", assigned21.clone())?;
    let assigned22 = {
        let fun25 = e.get("json")?.attr("loads")?;
        let mut args23 = Vec::new();
        let mut kw24 = Vec::new();
        args23.push({
            let fun28 = binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("manifold-layout/enclosure-assembly.facts.json".into()),
            )?
            .attr("read_text")?;
            let mut args26 = Vec::new();
            let mut kw27 = Vec::new();
            fun28.call(args26, kw27)?
        });
        fun25.call(args23, kw24)?
    };
    e.set("_machine_facts", assigned22.clone())?;
    let assigned29 = e
        .get("_machine_facts")?
        .get(Val::Str("constants".into()))?
        .get(Val::Str("C14_STATION".into()))?;
    let unpack30 = unpack(assigned29.clone(), 2)?;
    e.set("_power_x", unpack30[0].clone())?;
    e.set("_power_z", unpack30[1].clone())?;
    let assigned31 = e
        .get("_machine_facts")?
        .get(Val::Str("box".into()))?
        .get(Val::Str("outer".into()))?
        .get(Val::Int(3i64))?;
    e.set("_rear_y", assigned31.clone())?;
    let assigned32 = {
        let d = Val::dict(vec![]);
        d.set(Val::Str("power-ready".into()), {
            let fun35 = e.get("dict")?;
            let mut args33 = Vec::new();
            let mut kw34 = Vec::new();
            kw34.push(("cam".into(), {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Float(0.85f64))?);
                s.push(Val::Int(1i64));
                s.push(Val::Float(0.25f64));
                Val::tuple(s)
            }));
            kw34.push(("target".into(), {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("_power_x")?, Val::Int(8i64))?);
                s.push(binary("add", e.get("_rear_y")?, Val::Int(34i64))?);
                s.push(binary("sub", e.get("_power_z")?, Val::Int(16i64))?);
                Val::tuple(s)
            }));
            kw34.push(("span".into(), Val::Int(64i64)));
            kw34.push(("size".into(), {
                let mut s = Vec::new();
                s.push(Val::Int(1800i64));
                s.push(Val::Int(1300i64));
                Val::tuple(s)
            }));
            fun35.call(args33, kw34)?
        })?;
        d.set(Val::Str("fill-ready".into()), {
            let fun38 = e.get("dict")?;
            let mut args36 = Vec::new();
            let mut kw37 = Vec::new();
            kw37.push(("cam".into(), {
                let mut s = Vec::new();
                s.push(Val::Float(0.65f64));
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Float(0.5f64));
                Val::tuple(s)
            }));
            kw37.push(("target".into(), {
                let mut s = Vec::new();
                s.push(Val::Int(0i64));
                s.push(Val::Int(140i64));
                s.push(Val::Int(465i64));
                Val::tuple(s)
            }));
            kw37.push(("span".into(), Val::Int(265i64)));
            kw37.push(("size".into(), {
                let mut s = Vec::new();
                s.push(Val::Int(1600i64));
                s.push(Val::Int(1500i64));
                Val::tuple(s)
            }));
            fun38.call(args36, kw37)?
        })?;
        d
    };
    e.set("POSES", assigned32.clone())?;
    // unit
    e.set("unit", {
        let params = vec![("vector".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned39 = {
                let fun42 = e.get("math")?.attr("sqrt")?;
                let mut args40 = Vec::new();
                let mut kw41 = Vec::new();
                args40.push({
                    let fun45 = e.get("sum")?;
                    let mut args43 = Vec::new();
                    let mut kw44 = Vec::new();
                    args43.push({
                        let e = e.child();
                        let out46 = Val::list(vec![]);
                        for item47 in e.get("vector")?.iter()? {
                            e.set("value", item47)?;
                            out46.attr("append")?.call(
                                vec![binary("mul", e.get("value")?, e.get("value")?)?],
                                vec![],
                            )?;
                        }
                        out46
                    });
                    fun45.call(args43, kw44)?
                });
                fun42.call(args40, kw41)?
            };
            e.set("length", assigned39.clone())?;
            return Ok({
                let fun50 = e.get("tuple")?;
                let mut args48 = Vec::new();
                let mut kw49 = Vec::new();
                args48.push({
                    let e = e.child();
                    let out51 = Val::list(vec![]);
                    for item52 in e.get("vector")?.iter()? {
                        e.set("value", item52)?;
                        out51.attr("append")?.call(
                            vec![binary("truediv", e.get("value")?, e.get("length")?)?],
                            vec![],
                        )?;
                    }
                    out51
                });
                fun50.call(args48, kw49)?
            });
            Ok(Val::None)
        })
    })?;
    // pixel
    e.set("pixel", {
        let params = vec![("point".into(), None, false), ("pose".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = {
                let fun56 = e.get("unit")?;
                let mut args54 = Vec::new();
                let mut kw55 = Vec::new();
                args54.push(e.get("pose")?.get(Val::Str("cam".into()))?);
                fun56.call(args54, kw55)?
            };
            e.set("direction", assigned53.clone())?;
            let assigned57 = {
                let fun60 = e.get("unit")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                args58.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("direction")?.get(Val::Int(1i64))?)?);
                    s.push(e.get("direction")?.get(Val::Int(0i64))?);
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                fun60.call(args58, kw59)?
            };
            e.set("right", assigned57.clone())?;
            let assigned61 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("direction")?.get(Val::Int(1i64))?,
                        e.get("right")?.get(Val::Int(2i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("direction")?.get(Val::Int(2i64))?,
                        e.get("right")?.get(Val::Int(1i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("direction")?.get(Val::Int(2i64))?,
                        e.get("right")?.get(Val::Int(0i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("direction")?.get(Val::Int(0i64))?,
                        e.get("right")?.get(Val::Int(2i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("direction")?.get(Val::Int(0i64))?,
                        e.get("right")?.get(Val::Int(1i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("direction")?.get(Val::Int(1i64))?,
                        e.get("right")?.get(Val::Int(0i64))?,
                    )?,
                )?);
                Val::tuple(s)
            };
            e.set("up", assigned61.clone())?;
            let assigned62 = {
                let fun65 = e.get("tuple")?;
                let mut args63 = Vec::new();
                let mut kw64 = Vec::new();
                args63.push({
                    let e = e.child();
                    let out66 = Val::list(vec![]);
                    for item67 in {
                        let fun70 = e.get("zip")?;
                        let mut args68 = Vec::new();
                        let mut kw69 = Vec::new();
                        args68.push(e.get("point")?);
                        args68.push(e.get("pose")?.get(Val::Str("target".into()))?);
                        fun70.call(args68, kw69)?
                    }
                    .iter()?
                    {
                        let unpack71 = unpack(item67, 2)?;
                        e.set("value", unpack71[0].clone())?;
                        e.set("target", unpack71[1].clone())?;
                        out66.attr("append")?.call(
                            vec![binary("sub", e.get("value")?, e.get("target")?)?],
                            vec![],
                        )?;
                    }
                    out66
                });
                fun65.call(args63, kw64)?
            };
            e.set("delta", assigned62.clone())?;
            let assigned72 = e.get("pose")?.get(Val::Str("size".into()))?;
            let unpack73 = unpack(assigned72.clone(), 2)?;
            e.set("width", unpack73[0].clone())?;
            e.set("height", unpack73[1].clone())?;
            let assigned74 = binary(
                "truediv",
                e.get("height")?,
                binary(
                    "mul",
                    Val::Int(2i64),
                    e.get("pose")?.get(Val::Str("span".into()))?,
                )?,
            )?;
            e.set("scale", assigned74.clone())?;
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    binary("truediv", e.get("width")?, Val::Int(2i64))?,
                    binary(
                        "mul",
                        {
                            let fun77 = e.get("sum")?;
                            let mut args75 = Vec::new();
                            let mut kw76 = Vec::new();
                            args75.push({
                                let e = e.child();
                                let out78 = Val::list(vec![]);
                                for item79 in {
                                    let fun82 = e.get("zip")?;
                                    let mut args80 = Vec::new();
                                    let mut kw81 = Vec::new();
                                    args80.push(e.get("delta")?);
                                    args80.push(e.get("right")?);
                                    fun82.call(args80, kw81)?
                                }
                                .iter()?
                                {
                                    let unpack83 = unpack(item79, 2)?;
                                    e.set("value", unpack83[0].clone())?;
                                    e.set("axis", unpack83[1].clone())?;
                                    out78.attr("append")?.call(
                                        vec![binary("mul", e.get("value")?, e.get("axis")?)?],
                                        vec![],
                                    )?;
                                }
                                out78
                            });
                            fun77.call(args75, kw76)?
                        },
                        e.get("scale")?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary("truediv", e.get("height")?, Val::Int(2i64))?,
                    binary(
                        "mul",
                        {
                            let fun86 = e.get("sum")?;
                            let mut args84 = Vec::new();
                            let mut kw85 = Vec::new();
                            args84.push({
                                let e = e.child();
                                let out87 = Val::list(vec![]);
                                for item88 in {
                                    let fun91 = e.get("zip")?;
                                    let mut args89 = Vec::new();
                                    let mut kw90 = Vec::new();
                                    args89.push(e.get("delta")?);
                                    args89.push(e.get("up")?);
                                    fun91.call(args89, kw90)?
                                }
                                .iter()?
                                {
                                    let unpack92 = unpack(item88, 2)?;
                                    e.set("value", unpack92[0].clone())?;
                                    e.set("axis", unpack92[1].clone())?;
                                    out87.attr("append")?.call(
                                        vec![binary("mul", e.get("value")?, e.get("axis")?)?],
                                        vec![],
                                    )?;
                                }
                                out87
                            });
                            fun86.call(args84, kw85)?
                        },
                        e.get("scale")?,
                    )?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // mesh_bounds
    e.set("mesh_bounds", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod93 = rt.import_module("_guide_native")?;
            e.set("bounds", rt.member("_guide_native", "mesh_bounds")?)?;
            return Ok({
                let fun96 = e.get("bounds")?;
                let mut args94 = Vec::new();
                let mut kw95 = Vec::new();
                args94.push(e.get("path")?);
                fun96.call(args94, kw95)?
            });
            Ok(Val::None)
        })
    })?;
    // anchor
    e.set("anchor", {
        let params = vec![("point".into(), None, false), ("pose".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun99 = e.get("dict")?;
                let mut args97 = Vec::new();
                let mut kw98 = Vec::new();
                kw98.push(("world".into(), e.get("point")?));
                kw98.push(("pixel".into(), {
                    let fun102 = e.get("pixel")?;
                    let mut args100 = Vec::new();
                    let mut kw101 = Vec::new();
                    args100.push(e.get("point")?);
                    args100.push(e.get("pose")?);
                    fun102.call(args100, kw101)?
                }));
                fun99.call(args97, kw98)?
            });
            Ok(Val::None)
        })
    })?;
    // metadata
    e.set("metadata", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned103 = e.get("POSES")?.get(e.get("name")?)?;
            e.set("pose", assigned103.clone())?;
            let assigned104 = if {
                let v105 = e.get("name")?;
                let v106 = Val::Str("power-ready".into());
                Val::Bool(compare("eq", v105.clone(), v106.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Str("power-ready".into())
            } else {
                Val::Str("fill-seated".into())
            };
            e.set("source", assigned104.clone())?;
            let assigned107 = binary("truediv", e.get("SNAPSHOTS")?, {
                let mut str108 = String::new();
                str108.push_str(&format(&e.get("source")?, &String::new())?);
                str108.push_str(".step");
                Val::Str(str108)
            })?;
            e.set("step", assigned107.clone())?;
            let assigned109 = {
                let fun112 = e.get("step")?.attr("with_suffix")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                args110.push(Val::Str(".step.mesh".into()));
                fun112.call(args110, kw111)?
            };
            e.set("mesh", assigned109.clone())?;
            let assigned113 = {
                let fun116 = e.get("mesh_bounds")?;
                let mut args114 = Vec::new();
                let mut kw115 = Vec::new();
                args114.push(e.get("mesh")?);
                fun116.call(args114, kw115)?
            };
            e.set("bounds", assigned113.clone())?;
            if {
                let v117 = e.get("name")?;
                let v118 = Val::Str("power-ready".into());
                Val::Bool(compare("eq", v117.clone(), v118.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned119 = e.get("bounds")?.get(Val::Str("cordset/1".into()))?;
                let unpack120 = unpack(assigned119.clone(), 2)?;
                e.set("plug_min", unpack120[0].clone())?;
                e.set("plug_max", unpack120[1].clone())?;
                let assigned121 = binary(
                    "truediv",
                    binary(
                        "add",
                        e.get("plug_min")?.get(Val::Int(0i64))?,
                        e.get("plug_max")?.get(Val::Int(0i64))?,
                    )?,
                    Val::Int(2i64),
                )?;
                e.set("x", assigned121.clone())?;
                let assigned122 = binary(
                    "truediv",
                    binary(
                        "add",
                        e.get("plug_min")?.get(Val::Int(2i64))?,
                        e.get("plug_max")?.get(Val::Int(2i64))?,
                    )?,
                    Val::Int(2i64),
                )?;
                e.set("z", assigned122.clone())?;
                let assigned123 = binary(
                    "add",
                    e.get("plug_min")?.get(Val::Int(1i64))?,
                    e.get("POWER_RETREAT")?,
                )?;
                e.set("front_y", assigned123.clone())?;
                let assigned124 = binary(
                    "add",
                    binary(
                        "truediv",
                        binary(
                            "add",
                            e.get("plug_min")?.get(Val::Int(1i64))?,
                            e.get("plug_max")?.get(Val::Int(1i64))?,
                        )?,
                        Val::Int(2i64),
                    )?,
                    e.get("POWER_RETREAT")?,
                )?;
                e.set("body_y", assigned124.clone())?;
                let assigned125 = e
                    .get("bounds")?
                    .get(Val::Str("c14-inlet".into()))?
                    .get(Val::Int(1i64))?
                    .get(Val::Int(1i64))?;
                e.set("socket_y", assigned125.clone())?;
                let assigned126 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("connector-mouth".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("front_y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("connector-body".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("body_y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("connector-body-top".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("body_y")?);
                        s.push(e.get("plug_max")?.get(Val::Int(2i64))?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("connector-body-side".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("plug_min")?.get(Val::Int(0i64))?);
                        s.push(e.get("body_y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("socket-mouth".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("socket_y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("arrow-start".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("plug_min")?.get(Val::Int(0i64))?);
                        s.push(e.get("body_y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("arrow-end".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("plug_min")?.get(Val::Int(0i64))?);
                        s.push(binary("add", e.get("socket_y")?, Val::Int(18i64))?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    })?;
                    d
                };
                e.set("points", assigned126.clone())?;
                let assigned127 = {
                    let fun130 = e.get("dict")?;
                    let mut args128 = Vec::new();
                    let mut kw129 = Vec::new();
                    kw129.push(("prefix".into(), Val::Str("cordset".into())));
                    kw129.push(("translation".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(e.get("POWER_RETREAT")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    }));
                    kw129.push(("expected".into(), Val::Int(3i64)));
                    fun130.call(args128, kw129)?
                };
                e.set("action", assigned127.clone())?;
                let assigned131 = {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(160i64));
                    s.push(Val::Int(1800i64));
                    s.push(Val::Int(1140i64));
                    Val::tuple(s)
                };
                e.set("crop", assigned131.clone())?;
                let assigned132 = binary("sub", e.get("front_y")?, e.get("socket_y")?)?;
                e.set("gap", assigned132.clone())?;
                let assigned133 = {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                };
                e.set("axis", assigned133.clone())?;
            } else {
                let assigned134 = e.get("bounds")?.get(Val::Str("bottle-neck".into()))?;
                let unpack135 = unpack(assigned134.clone(), 2)?;
                e.set("neck_min", unpack135[0].clone())?;
                e.set("neck_max", unpack135[1].clone())?;
                let assigned136 = e.get("bounds")?.get(Val::Str("bottle-body".into()))?;
                let unpack137 = unpack(assigned136.clone(), 2)?;
                e.set("body_min", unpack137[0].clone())?;
                e.set("body_max", unpack137[1].clone())?;
                let assigned138 = binary(
                    "truediv",
                    binary(
                        "add",
                        e.get("neck_min")?.get(Val::Int(0i64))?,
                        e.get("neck_max")?.get(Val::Int(0i64))?,
                    )?,
                    Val::Int(2i64),
                )?;
                e.set("x", assigned138.clone())?;
                let assigned139 = binary(
                    "truediv",
                    binary(
                        "add",
                        e.get("neck_min")?.get(Val::Int(1i64))?,
                        e.get("neck_max")?.get(Val::Int(1i64))?,
                    )?,
                    Val::Int(2i64),
                )?;
                e.set("y", assigned139.clone())?;
                let assigned140 = binary(
                    "truediv",
                    binary(
                        "sub",
                        e.get("body_max")?.get(Val::Int(0i64))?,
                        e.get("body_min")?.get(Val::Int(0i64))?,
                    )?,
                    Val::Int(2i64),
                )?;
                e.set("radius", assigned140.clone())?;
                let assigned141 = {
                    let fun144 = e.get("unit")?;
                    let mut args142 = Vec::new();
                    let mut kw143 = Vec::new();
                    args142.push({
                        let mut s = Vec::new();
                        s.push(
                            e.get("pose")?
                                .get(Val::Str("cam".into()))?
                                .get(Val::Int(0i64))?,
                        );
                        s.push(
                            e.get("pose")?
                                .get(Val::Str("cam".into()))?
                                .get(Val::Int(1i64))?,
                        );
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    fun144.call(args142, kw143)?
                };
                e.set("facing", assigned141.clone())?;
                let assigned145 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("x")?,
                        binary(
                            "mul",
                            e.get("radius")?,
                            e.get("facing")?.get(Val::Int(0i64))?,
                        )?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("y")?,
                        binary(
                            "mul",
                            e.get("radius")?,
                            e.get("facing")?.get(Val::Int(1i64))?,
                        )?,
                    )?);
                    Val::tuple(s)
                };
                let unpack146 = unpack(assigned145.clone(), 2)?;
                e.set("surface_x", unpack146[0].clone())?;
                e.set("surface_y", unpack146[1].clone())?;
                let assigned147 = binary(
                    "add",
                    e.get("neck_min")?.get(Val::Int(2i64))?,
                    e.get("BOTTLE_LIFT")?,
                )?;
                e.set("mouth_z", assigned147.clone())?;
                let assigned148 = e
                    .get("bounds")?
                    .get(Val::Str("funnel".into()))?
                    .get(Val::Int(1i64))?
                    .get(Val::Int(2i64))?;
                e.set("rim_z", assigned148.clone())?;
                let assigned149 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("bottle-mouth".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("mouth_z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("bottle-body".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("surface_x")?);
                        s.push(e.get("surface_y")?);
                        s.push(binary(
                            "add",
                            binary(
                                "truediv",
                                binary(
                                    "add",
                                    e.get("body_min")?.get(Val::Int(2i64))?,
                                    e.get("body_max")?.get(Val::Int(2i64))?,
                                )?,
                                Val::Int(2i64),
                            )?,
                            e.get("BOTTLE_LIFT")?,
                        )?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("bottle-top".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(binary(
                            "add",
                            e.get("bounds")?
                                .get(Val::Str("bottle-base".into()))?
                                .get(Val::Int(1i64))?
                                .get(Val::Int(2i64))?,
                            e.get("BOTTLE_LIFT")?,
                        )?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("funnel-mouth".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("rim_z")?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("arrow-start".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("surface_x")?);
                        s.push(e.get("surface_y")?);
                        s.push(binary(
                            "sub",
                            binary(
                                "add",
                                e.get("body_max")?.get(Val::Int(2i64))?,
                                e.get("BOTTLE_LIFT")?,
                            )?,
                            Val::Int(35i64),
                        )?);
                        Val::tuple(s)
                    })?;
                    d.set(Val::Str("arrow-end".into()), {
                        let mut s = Vec::new();
                        s.push(e.get("surface_x")?);
                        s.push(e.get("surface_y")?);
                        s.push(binary(
                            "add",
                            binary(
                                "add",
                                e.get("body_min")?.get(Val::Int(2i64))?,
                                e.get("BOTTLE_LIFT")?,
                            )?,
                            Val::Int(24i64),
                        )?);
                        Val::tuple(s)
                    })?;
                    d
                };
                e.set("points", assigned149.clone())?;
                let assigned150 = {
                    let fun153 = e.get("dict")?;
                    let mut args151 = Vec::new();
                    let mut kw152 = Vec::new();
                    kw152.push(("prefix".into(), Val::Str("bottle-".into())));
                    kw152.push(("translation".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(e.get("BOTTLE_LIFT")?);
                        Val::tuple(s)
                    }));
                    kw152.push(("expected".into(), Val::Int(4i64)));
                    fun153.call(args151, kw152)?
                };
                e.set("action", assigned150.clone())?;
                let assigned154 = {
                    let mut s = Vec::new();
                    s.push(Val::Int(290i64));
                    s.push(Val::Int(190i64));
                    s.push(Val::Int(1550i64));
                    s.push(Val::Int(1500i64));
                    Val::tuple(s)
                };
                e.set("crop", assigned154.clone())?;
                let assigned155 = binary("sub", e.get("mouth_z")?, e.get("rim_z")?)?;
                e.set("gap", assigned155.clone())?;
                let assigned156 = {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(unary("neg", Val::Int(1i64))?);
                    Val::tuple(s)
                };
                e.set("axis", assigned156.clone())?;
            }
            return Ok({
                let fun159 = e.get("dict")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                kw158.extend(keyword_items(e.get("pose")?)?);
                kw158.push(("source_step".into(), {
                    let fun162 = e.get("str")?;
                    let mut args160 = Vec::new();
                    let mut kw161 = Vec::new();
                    args160.push({
                        let fun165 = e.get("step")?.attr("relative_to")?;
                        let mut args163 = Vec::new();
                        let mut kw164 = Vec::new();
                        args163.push(e.get("ROOT")?);
                        fun165.call(args163, kw164)?
                    });
                    fun162.call(args160, kw161)?
                }));
                kw158.push(("source_mesh".into(), {
                    let fun168 = e.get("str")?;
                    let mut args166 = Vec::new();
                    let mut kw167 = Vec::new();
                    args166.push({
                        let fun171 = e.get("mesh")?.attr("relative_to")?;
                        let mut args169 = Vec::new();
                        let mut kw170 = Vec::new();
                        args169.push(e.get("ROOT")?);
                        fun171.call(args169, kw170)?
                    });
                    fun168.call(args166, kw167)?
                }));
                kw158.push(("source_mesh_sha256".into(), {
                    let fun174 = {
                        let fun177 = e.get("hashlib")?.attr("sha256")?;
                        let mut args175 = Vec::new();
                        let mut kw176 = Vec::new();
                        args175.push({
                            let fun180 = e.get("mesh")?.attr("read_bytes")?;
                            let mut args178 = Vec::new();
                            let mut kw179 = Vec::new();
                            fun180.call(args178, kw179)?
                        });
                        fun177.call(args175, kw176)?
                    }
                    .attr("hexdigest")?;
                    let mut args172 = Vec::new();
                    let mut kw173 = Vec::new();
                    fun174.call(args172, kw173)?
                }));
                kw158.push(("projection".into(), Val::Str("orthographic".into())));
                kw158.push(("up".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }));
                kw158.push(("trim".into(), Val::Bool(false)));
                kw158.push(("pixel_origin".into(), Val::Str("top-left".into())));
                kw158.push((
                    "pixels_per_mm".into(),
                    binary(
                        "truediv",
                        e.get("pose")?
                            .get(Val::Str("size".into()))?
                            .get(Val::Int(1i64))?,
                        binary(
                            "mul",
                            Val::Int(2i64),
                            e.get("pose")?.get(Val::Str("span".into()))?,
                        )?,
                    )?,
                ));
                kw158.push(("crop".into(), e.get("crop")?));
                kw158.push(("action".into(), e.get("action")?));
                kw158.push(("visible_axis_gap_mm".into(), e.get("gap")?));
                kw158.push(("insertion_axis".into(), e.get("axis")?));
                kw158.push(("points".into(), {
                    let e = e.child();
                    let out181 = Val::dict(vec![]);
                    for item182 in {
                        let fun185 = e.get("points")?.attr("items")?;
                        let mut args183 = Vec::new();
                        let mut kw184 = Vec::new();
                        fun185.call(args183, kw184)?
                    }
                    .iter()?
                    {
                        let unpack186 = unpack(item182, 2)?;
                        e.set("key", unpack186[0].clone())?;
                        e.set("value", unpack186[1].clone())?;
                        out181.set(e.get("key")?, {
                            let fun189 = e.get("anchor")?;
                            let mut args187 = Vec::new();
                            let mut kw188 = Vec::new();
                            args187.push(e.get("value")?);
                            args187.push(e.get("pose")?);
                            fun189.call(args187, kw188)?
                        })?;
                    }
                    out181
                }));
                fun159.call(args157, kw158)?
            });
            Ok(Val::None)
        })
    })?;
    // moved_payload
    e.set("moved_payload", {
        let params = vec![("name".into(), None, false), ("entry".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod190 = rt.import_module("_guide_native")?;
            e.set("move", rt.member("_guide_native", "moved_payload")?)?;
            return Ok({
                let fun193 = e.get("move")?;
                let mut args191 = Vec::new();
                let mut kw192 = Vec::new();
                args191.push(e.get("name")?);
                args191.push(e.get("entry")?);
                args191.push(e.get("ROOT")?);
                args191.push(e.get("OUT")?);
                fun193.call(args191, kw192)?
            });
            Ok(Val::None)
        })
    })?;
    // registration
    e.set("registration", {
        let params = vec![
            ("entry".into(), None, false),
            ("report".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod194 = rt.import_module("_guide_native")?;
            e.set("register", rt.member("_guide_native", "registration")?)?;
            return Ok({
                let fun197 = e.get("register")?;
                let mut args195 = Vec::new();
                let mut kw196 = Vec::new();
                args195.push(e.get("entry")?);
                args195.push(e.get("report")?);
                fun197.call(args195, kw196)?
            });
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned198 = {
                let fun201 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args199 = Vec::new();
                let mut kw200 = Vec::new();
                kw200.push(("description".into(), e.get("__doc__")?));
                fun201.call(args199, kw200)?
            };
            e.set("parser", assigned198.clone())?;
            {
                let fun204 = e.get("parser")?.attr("add_argument")?;
                let mut args202 = Vec::new();
                let mut kw203 = Vec::new();
                args202.push(Val::Str("scenes".into()));
                kw203.push(("nargs".into(), Val::Str("*".into())));
                kw203.push(("choices".into(), {
                    let fun207 = e.get("list")?;
                    let mut args205 = Vec::new();
                    let mut kw206 = Vec::new();
                    args205.push(e.get("POSES")?);
                    fun207.call(args205, kw206)?
                }));
                fun204.call(args202, kw203)?
            };
            {
                let fun210 = e.get("parser")?.attr("add_argument")?;
                let mut args208 = Vec::new();
                let mut kw209 = Vec::new();
                args208.push(Val::Str("--stage-only".into()));
                kw209.push(("action".into(), Val::Str("store_true".into())));
                fun210.call(args208, kw209)?
            };
            let assigned211 = {
                let fun214 = e.get("parser")?.attr("parse_args")?;
                let mut args212 = Vec::new();
                let mut kw213 = Vec::new();
                fun214.call(args212, kw213)?
            };
            e.set("args", assigned211.clone())?;
            {
                let fun217 = e.get("OUT")?.attr("mkdir")?;
                let mut args215 = Vec::new();
                let mut kw216 = Vec::new();
                kw216.push(("parents".into(), Val::Bool(true)));
                kw216.push(("exist_ok".into(), Val::Bool(true)));
                fun217.call(args215, kw216)?
            };
            {
                let fun220 = e.get("ART")?.attr("mkdir")?;
                let mut args218 = Vec::new();
                let mut kw219 = Vec::new();
                kw219.push(("parents".into(), Val::Bool(true)));
                kw219.push(("exist_ok".into(), Val::Bool(true)));
                fun220.call(args218, kw219)?
            };
            let assigned221 = {
                let e = e.child();
                let out222 = Val::dict(vec![]);
                for item223 in {
                    let v224 = e.get("args")?.attr("scenes")?;
                    if v224.truthy()? {
                        v224
                    } else {
                        e.get("POSES")?
                    }
                }
                .iter()?
                {
                    e.set("name", item223)?;
                    out222.set(e.get("name")?, {
                        let fun227 = e.get("metadata")?;
                        let mut args225 = Vec::new();
                        let mut kw226 = Vec::new();
                        args225.push(e.get("name")?);
                        fun227.call(args225, kw226)?
                    })?;
                }
                out222
            };
            e.set("entries", assigned221.clone())?;
            let assigned228 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("jobs", assigned228.clone())?;
            for item229 in {
                let fun266 = e.get("entries")?.attr("items")?;
                let mut args264 = Vec::new();
                let mut kw265 = Vec::new();
                fun266.call(args264, kw265)?
            }
            .iter()?
            {
                let unpack267 = unpack(item229, 2)?;
                e.set("name", unpack267[0].clone())?;
                e.set("entry", unpack267[1].clone())?;
                let assigned230 = {
                    let fun233 = e.get("moved_payload")?;
                    let mut args231 = Vec::new();
                    let mut kw232 = Vec::new();
                    args231.push(e.get("name")?);
                    args231.push(e.get("entry")?);
                    fun233.call(args231, kw232)?
                };
                e.set("payload", assigned230.clone())?;
                {
                    let fun236 = e.get("jobs")?.attr("append")?;
                    let mut args234 = Vec::new();
                    let mut kw235 = Vec::new();
                    args234.push({
                        let fun239 = e.get("dict")?;
                        let mut args237 = Vec::new();
                        let mut kw238 = Vec::new();
                        kw238.push(("step".into(), {
                            let fun242 = e.get("str")?;
                            let mut args240 = Vec::new();
                            let mut kw241 = Vec::new();
                            args240.push({
                                let fun245 = {
                                    let fun248 = e.get("Path")?;
                                    let mut args246 = Vec::new();
                                    let mut kw247 = Vec::new();
                                    args246
                                        .push(e.get("entry")?.get(Val::Str("source_step".into()))?);
                                    fun248.call(args246, kw247)?
                                }
                                .attr("relative_to")?;
                                let mut args243 = Vec::new();
                                let mut kw244 = Vec::new();
                                args243.push(Val::Str("hardware".into()));
                                fun245.call(args243, kw244)?
                            });
                            fun242.call(args240, kw241)?
                        }));
                        kw238.push(("payload".into(), {
                            let fun251 = e.get("str")?;
                            let mut args249 = Vec::new();
                            let mut kw250 = Vec::new();
                            args249.push(e.get("payload")?);
                            fun251.call(args249, kw250)?
                        }));
                        kw238.push(("out".into(), {
                            let fun254 = e.get("str")?;
                            let mut args252 = Vec::new();
                            let mut kw253 = Vec::new();
                            args252.push(binary("truediv", e.get("ART")?, {
                                let mut str255 = String::new();
                                str255.push_str(&format(&e.get("name")?, &String::new())?);
                                str255.push_str(".png");
                                Val::Str(str255)
                            })?);
                            fun254.call(args252, kw253)?
                        }));
                        kw238.push(("cam".into(), e.get("entry")?.get(Val::Str("cam".into()))?));
                        kw238.push((
                            "target".into(),
                            e.get("entry")?.get(Val::Str("target".into()))?,
                        ));
                        kw238.push(("span".into(), e.get("entry")?.get(Val::Str("span".into()))?));
                        kw238.push(("size".into(), {
                            let fun258 = Val::Str("x".into()).attr("join")?;
                            let mut args256 = Vec::new();
                            let mut kw257 = Vec::new();
                            args256.push({
                                let e = e.child();
                                let out259 = Val::list(vec![]);
                                for item260 in
                                    e.get("entry")?.get(Val::Str("size".into()))?.iter()?
                                {
                                    e.set("n", item260)?;
                                    out259.attr("append")?.call(
                                        vec![{
                                            let fun263 = e.get("str")?;
                                            let mut args261 = Vec::new();
                                            let mut kw262 = Vec::new();
                                            args261.push(e.get("n")?);
                                            fun263.call(args261, kw262)?
                                        }],
                                        vec![],
                                    )?;
                                }
                                out259
                            });
                            fun258.call(args256, kw257)?
                        }));
                        kw238.push(("up".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }));
                        kw238.push(("bg".into(), Val::Str("#f2eee8".into())));
                        kw238.push(("transparent".into(), Val::Bool(true)));
                        kw238.push(("solid".into(), Val::Bool(true)));
                        kw238.push(("ortho".into(), Val::Bool(true)));
                        kw238.push(("trim".into(), Val::Bool(false)));
                        kw238.push(("ground".into(), Val::Bool(false)));
                        kw238.push(("fog".into(), Val::Bool(false)));
                        fun239.call(args237, kw238)?
                    });
                    fun236.call(args234, kw235)?
                };
            }
            let assigned268 = binary("truediv", e.get("OUT")?, Val::Str("scenes.json".into()))?;
            e.set("manifest", assigned268.clone())?;
            {
                let fun271 = e.get("manifest")?.attr("write_text")?;
                let mut args269 = Vec::new();
                let mut kw270 = Vec::new();
                args269.push(binary(
                    "add",
                    {
                        let fun274 = e.get("json")?.attr("dumps")?;
                        let mut args272 = Vec::new();
                        let mut kw273 = Vec::new();
                        args272.push(e.get("jobs")?);
                        kw273.push(("indent".into(), Val::Int(2i64)));
                        fun274.call(args272, kw273)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun271.call(args269, kw270)?
            };
            if unary("not", e.get("args")?.attr("stage_only")?)?.truthy()? {
                let assigned275 = {
                    let fun278 = e.get("_hsm_render")?.attr("render")?;
                    let mut args276 = Vec::new();
                    let mut kw277 = Vec::new();
                    args276.push(e.get("jobs")?);
                    kw277.push(("reports".into(), Val::Bool(true)));
                    fun278.call(args276, kw277)?
                };
                e.set("reports", assigned275.clone())?;
                for item279 in {
                    let fun333 = e.get("zip")?;
                    let mut args331 = Vec::new();
                    let mut kw332 = Vec::new();
                    args331.push({
                        let fun336 = e.get("entries")?.attr("items")?;
                        let mut args334 = Vec::new();
                        let mut kw335 = Vec::new();
                        fun336.call(args334, kw335)?
                    });
                    args331.push(e.get("reports")?);
                    kw332.push(("strict".into(), Val::Bool(true)));
                    fun333.call(args331, kw332)?
                }
                .iter()?
                {
                    let unpack337 = unpack(item279, 2)?;
                    let unpack338 = unpack(unpack337[0].clone(), 2)?;
                    e.set("name", unpack338[0].clone())?;
                    e.set("entry", unpack338[1].clone())?;
                    e.set("report", unpack337[1].clone())?;
                    let context280 = {
                        let fun283 = e.get("Image")?.attr("open")?;
                        let mut args281 = Vec::new();
                        let mut kw282 = Vec::new();
                        args281.push(binary("truediv", e.get("ART")?, {
                            let mut str284 = String::new();
                            str284.push_str(&format(&e.get("name")?, &String::new())?);
                            str284.push_str(".png");
                            Val::Str(str284)
                        })?);
                        fun283.call(args281, kw282)?
                    };
                    e.set(
                        "rendered",
                        context280.attr("__enter__")?.call(vec![], vec![])?,
                    )?;
                    let context_result299 = (|| -> Result<Flow> {
                        if !{
                            let v285 = e.get("rendered")?.attr("mode")?;
                            let v286 = Val::Str("RGBA".into());
                            Val::Bool(compare("eq", v285.clone(), v286.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
                        }
                        if !{
                            let v290 = e.get("rendered")?.attr("size")?;
                            let v291 = {
                                let fun289 = e.get("tuple")?;
                                let mut args287 = Vec::new();
                                let mut kw288 = Vec::new();
                                args287.push(e.get("entry")?.get(Val::Str("size".into()))?);
                                fun289.call(args287, kw288)?
                            };
                            Val::Bool(compare("eq", v290.clone(), v291.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
                        }
                        let assigned292 = {
                            let fun295 = {
                                let fun298 = e.get("rendered")?.attr("getchannel")?;
                                let mut args296 = Vec::new();
                                let mut kw297 = Vec::new();
                                args296.push(Val::Str("A".into()));
                                fun298.call(args296, kw297)?
                            }
                            .attr("getbbox")?;
                            let mut args293 = Vec::new();
                            let mut kw294 = Vec::new();
                            fun295.call(args293, kw294)?
                        };
                        e.get("entry")?
                            .set(Val::Str("alpha_bounds".into()), assigned292.clone())?;
                        Ok(Flow::Continue)
                    })();
                    context280
                        .attr("__exit__")?
                        .call(vec![Val::None, Val::None, Val::None], vec![])?;
                    match context_result299? {
                        Flow::Continue => {}
                        Flow::Return(value) => return Ok(value),
                        Flow::Break => break,
                        Flow::Next => continue,
                    }
                    let assigned300 = {
                        let fun303 = e.get("registration")?;
                        let mut args301 = Vec::new();
                        let mut kw302 = Vec::new();
                        args301.push(e.get("entry")?);
                        args301.push(e.get("report")?);
                        fun303.call(args301, kw302)?
                    };
                    e.set("measured_registration", assigned300.clone())?;
                    {
                        let fun306 = binary("truediv", e.get("OUT")?, {
                            let mut str307 = String::new();
                            str307.push_str(&format(&e.get("name")?, &String::new())?);
                            str307.push_str(".render.json");
                            Val::Str(str307)
                        })?
                        .attr("write_text")?;
                        let mut args304 = Vec::new();
                        let mut kw305 = Vec::new();
                        args304.push(binary(
                            "add",
                            {
                                let fun310 = e.get("json")?.attr("dumps")?;
                                let mut args308 = Vec::new();
                                let mut kw309 = Vec::new();
                                args308.push(e.get("measured_registration")?);
                                kw309.push(("indent".into(), Val::Int(2i64)));
                                fun310.call(args308, kw309)?
                            },
                            Val::Str("\n".into()),
                        )?);
                        fun306.call(args304, kw305)?
                    };
                    for item311 in {
                        let fun329 = e
                            .get("entry")?
                            .get(Val::Str("points".into()))?
                            .attr("items")?;
                        let mut args327 = Vec::new();
                        let mut kw328 = Vec::new();
                        fun329.call(args327, kw328)?
                    }
                    .iter()?
                    {
                        let unpack330 = unpack(item311, 2)?;
                        e.set("point", unpack330[0].clone())?;
                        e.set("anchor_entry", unpack330[1].clone())?;
                        let assigned312 = e
                            .get("measured_registration")?
                            .get(Val::Str("points".into()))?
                            .get(e.get("point")?)?;
                        e.set("measured", assigned312.clone())?;
                        if !{
                            let v325 = {
                                let fun315 = e.get("max")?;
                                let mut args313 = Vec::new();
                                let mut kw314 = Vec::new();
                                args313.push({
                                    let e = e.child();
                                    let out316 = Val::list(vec![]);
                                    for item317 in {
                                        let fun320 = e.get("zip")?;
                                        let mut args318 = Vec::new();
                                        let mut kw319 = Vec::new();
                                        args318.push(e.get("measured")?);
                                        args318.push(
                                            e.get("anchor_entry")?.get(Val::Str("pixel".into()))?,
                                        );
                                        fun320.call(args318, kw319)?
                                    }
                                    .iter()?
                                    {
                                        let unpack321 = unpack(item317, 2)?;
                                        e.set("a", unpack321[0].clone())?;
                                        e.set("b", unpack321[1].clone())?;
                                        out316.attr("append")?.call(
                                            vec![{
                                                let fun324 = e.get("abs")?;
                                                let mut args322 = Vec::new();
                                                let mut kw323 = Vec::new();
                                                args322.push(binary(
                                                    "sub",
                                                    e.get("a")?,
                                                    e.get("b")?,
                                                )?);
                                                fun324.call(args322, kw323)?
                                            }],
                                            vec![],
                                        )?;
                                    }
                                    out316
                                });
                                fun315.call(args313, kw314)?
                            };
                            let v326 = Val::Float(1e-05f64);
                            Val::Bool(compare("lt", v325.clone(), v326.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
                        }
                    }
                }
            }
            {
                let fun341 = binary("truediv", e.get("OUT")?, Val::Str("anchors.json".into()))?
                    .attr("write_text")?;
                let mut args339 = Vec::new();
                let mut kw340 = Vec::new();
                args339.push(binary(
                    "add",
                    {
                        let fun344 = e.get("json")?.attr("dumps")?;
                        let mut args342 = Vec::new();
                        let mut kw343 = Vec::new();
                        args342.push({
                            let fun347 = e.get("dict")?;
                            let mut args345 = Vec::new();
                            let mut kw346 = Vec::new();
                            kw346.push(("scenes".into(), e.get("entries")?));
                            fun347.call(args345, kw346)?
                        });
                        kw343.push(("indent".into(), Val::Int(2i64)));
                        fun344.call(args342, kw343)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun341.call(args339, kw340)?
            };
            {
                let fun350 = e.get("print")?;
                let mut args348 = Vec::new();
                let mut kw349 = Vec::new();
                args348.push(binary(
                    "truediv",
                    e.get("OUT")?,
                    Val::Str("anchors.json".into()),
                )?);
                fun350.call(args348, kw349)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun353 = e.get("main")?;
        let mut args351 = Vec::new();
        let mut kw352 = Vec::new();
        fun353.call(args351, kw352)?
    };
    Ok(Val::None)
}
