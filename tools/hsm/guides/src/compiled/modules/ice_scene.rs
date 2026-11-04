//! Guide recipe: `tools/install-guide/ice_scene.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
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
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned2.clone())?;
    let assigned9 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HARDWARE", assigned9.clone())?;
    let assigned10 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/out/ice".into()),
    )?;
    e.set("OUT", assigned10.clone())?;
    let assigned11 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide/out/pour-legibility/pour-running.step".into()),
    )?;
    e.set("SOURCE", assigned11.clone())?;
    {
        let fun14 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args12 = Vec::new();
        let mut kw13 = Vec::new();
        args12.push(Val::Int(0i64));
        args12.push({
            let fun17 = e.get("str")?;
            let mut args15 = Vec::new();
            let mut kw16 = Vec::new();
            args15.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("scripts".into()),
            )?);
            fun17.call(args15, kw16)?
        });
        fun14.call(args12, kw13)?
    };
    let mod18 = rt.import_module("_cadq_export")?;
    e.set(
        "_per_solid_color",
        rt.member("_cadq_export", "_per_solid_color")?,
    )?;
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    e.set("_mesh_payload", rt.import_module("_mesh_payload")?)?;
    let mod19 = rt.import_module("flute_payload")?;
    e.set("read_payload", rt.member("flute_payload", "read_payload")?)?;
    let assigned20 = {
        let mut s = Vec::new();
        s.push(Val::Int(0i64));
        s.push(unary("neg", Val::Float(133.99672200476698f64))?);
        Val::tuple(s)
    };
    e.set("GLASS_CENTER", assigned20.clone())?;
    let assigned21 = {
        let mut s = Vec::new();
        s.push(Val::Int(1i64));
        s.push(unary("neg", Val::Float(1.8f64))?);
        s.push(Val::Float(0.67f64));
        Val::tuple(s)
    };
    e.set("CAMERA", assigned21.clone())?;
    // scene
    e.set("scene", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned22 = {
                let fun25 = e.get("read_payload")?;
                let mut args23 = Vec::new();
                let mut kw24 = Vec::new();
                args23.push({
                    let fun28 = e.get("SOURCE")?.attr("with_suffix")?;
                    let mut args26 = Vec::new();
                    let mut kw27 = Vec::new();
                    args26.push(Val::Str(".step.mesh".into()));
                    fun28.call(args26, kw27)?
                });
                fun25.call(args23, kw24)?
            };
            e.set("meshes", assigned22.clone())?;
            if unary("not", e.get("meshes")?)?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun31 = e.get("ValueError")?;
                        let mut args29 = Vec::new();
                        let mut kw30 = Vec::new();
                        args29.push({
                            let mut str32 = String::new();
                            str32.push_str("No frozen first-pour payload at ");
                            str32.push_str(&format(&e.get("SOURCE")?, &String::new())?);
                            Val::Str(str32)
                        });
                        fun31.call(args29, kw30)?
                    })?
                );
            }
            let assigned33 = {
                let fun36 = e.get("cq")?.attr("Assembly")?;
                let mut args34 = Vec::new();
                let mut kw35 = Vec::new();
                kw35.push(("name".into(), Val::Str("first-pour-with-ice".into())));
                fun36.call(args34, kw35)?
            };
            e.set("result", assigned33.clone())?;
            let assigned37 = {
                let fun40 = e.get("math")?.attr("hypot")?;
                let mut args38 = Vec::new();
                let mut kw39 = Vec::new();
                args38.extend(
                    e.get("CAMERA")?
                        .get(Val::Slice {
                            start: None,
                            stop: Some(Val::Int(2i64).integer()?),
                            step: 1,
                        })?
                        .iter()?,
                );
                fun40.call(args38, kw39)?
            };
            e.set("length", assigned37.clone())?;
            let assigned41 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("CAMERA")?.get(Val::Int(0i64))?,
                    e.get("length")?,
                )?);
                s.push(binary(
                    "truediv",
                    e.get("CAMERA")?.get(Val::Int(1i64))?,
                    e.get("length")?,
                )?);
                Val::tuple(s)
            };
            e.set("front", assigned41.clone())?;
            let assigned42 = {
                let mut s = Vec::new();
                s.push(unary("neg", e.get("front")?.get(Val::Int(1i64))?)?);
                s.push(e.get("front")?.get(Val::Int(0i64))?);
                Val::tuple(s)
            };
            e.set("right", assigned42.clone())?;
            let assigned43 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(14i64))?);
                    s.push(unary("neg", Val::Int(8i64))?);
                    s.push(Val::Int(78i64));
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(21i64));
                        s.push(Val::Int(21i64));
                        s.push(Val::Int(23i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(11i64));
                        s.push(unary("neg", Val::Int(8i64))?);
                        s.push(Val::Int(18i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(15i64));
                    s.push(unary("neg", Val::Int(10i64))?);
                    s.push(Val::Int(79i64));
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(21i64));
                        s.push(Val::Int(21i64));
                        s.push(Val::Int(22i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(9i64))?);
                        s.push(Val::Int(12i64));
                        s.push(unary("neg", Val::Int(19i64))?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(15i64));
                    s.push(Val::Int(76i64));
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(22i64));
                        s.push(Val::Int(21i64));
                        s.push(Val::Int(24i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(8i64));
                        s.push(unary("neg", Val::Int(9i64))?);
                        s.push(Val::Int(34i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("cubes", assigned43.clone())?;
            let assigned44 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(14.8f64));
                    s.push(Val::Float(10.3f64));
                    s.push(unary("neg", Val::Int(12i64))?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(18.8f64));
                        s.push(Val::Float(19.0f64));
                        s.push(Val::Float(16.8f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(33.4f64));
                    s.push(Val::Float(10.8f64));
                    s.push(Val::Int(14i64));
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(20.0f64));
                        s.push(Val::Float(19.7f64));
                        s.push(Val::Float(17.2f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(51.9f64));
                    s.push(Val::Float(11.1f64));
                    s.push(unary("neg", Val::Int(5i64))?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Float(20.4f64));
                        s.push(Val::Float(20.1f64));
                        s.push(Val::Float(17.0f64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("layers", assigned44.clone())?;
            let assigned45 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(2i64))?);
                    s.push(Val::Int(2i64));
                    s.push(unary("neg", Val::Int(2i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(2i64));
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(Val::Int(2i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(unary("neg", Val::Int(1i64))?);
                    s.push(unary("neg", Val::Int(2i64))?);
                    s.push(unary("neg", Val::Int(3i64))?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1i64));
                    s.push(Val::Int(2i64));
                    s.push(Val::Int(3i64));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("turns", assigned45.clone())?;
            let assigned46 = {
                let fun49 = e.get("math")?.attr("degrees")?;
                let mut args47 = Vec::new();
                let mut kw48 = Vec::new();
                args47.push({
                    let fun52 = e.get("math")?.attr("atan2")?;
                    let mut args50 = Vec::new();
                    let mut kw51 = Vec::new();
                    args50.push(e.get("right")?.get(Val::Int(1i64))?);
                    args50.push(e.get("right")?.get(Val::Int(0i64))?);
                    fun52.call(args50, kw51)?
                });
                fun49.call(args47, kw48)?
            };
            e.set("alignment", assigned46.clone())?;
            for item53 in e.get("layers")?.iter()? {
                let unpack82 = unpack(item53, 4)?;
                e.set("z", unpack82[0].clone())?;
                e.set("spread", unpack82[1].clone())?;
                e.set("yaw", unpack82[2].clone())?;
                e.set("size", unpack82[3].clone())?;
                let assigned54 = {
                    let fun57 = e.get("math")?.attr("radians")?;
                    let mut args55 = Vec::new();
                    let mut kw56 = Vec::new();
                    args55.push(e.get("yaw")?);
                    fun57.call(args55, kw56)?
                };
                e.set("angle", assigned54.clone())?;
                for item58 in {
                    let fun78 = e.get("zip")?;
                    let mut args76 = Vec::new();
                    let mut kw77 = Vec::new();
                    args76.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", e.get("spread")?)?);
                            s.push(unary("neg", e.get("spread")?)?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("spread")?);
                            s.push(unary("neg", e.get("spread")?)?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("spread")?);
                            s.push(e.get("spread")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(unary("neg", e.get("spread")?)?);
                            s.push(e.get("spread")?);
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    args76.push(e.get("turns")?);
                    fun78.call(args76, kw77)?
                }
                .iter()?
                {
                    let unpack79 = unpack(item58, 2)?;
                    let unpack80 = unpack(unpack79[0].clone(), 2)?;
                    e.set("u", unpack80[0].clone())?;
                    e.set("v", unpack80[1].clone())?;
                    let unpack81 = unpack(unpack79[1].clone(), 3)?;
                    e.set("rx", unpack81[0].clone())?;
                    e.set("ry", unpack81[1].clone())?;
                    e.set("rz", unpack81[2].clone())?;
                    let assigned59 = {
                        let mut s = Vec::new();
                        s.push(binary(
                            "sub",
                            binary("mul", e.get("u")?, {
                                let fun62 = e.get("math")?.attr("cos")?;
                                let mut args60 = Vec::new();
                                let mut kw61 = Vec::new();
                                args60.push(e.get("angle")?);
                                fun62.call(args60, kw61)?
                            })?,
                            binary("mul", e.get("v")?, {
                                let fun65 = e.get("math")?.attr("sin")?;
                                let mut args63 = Vec::new();
                                let mut kw64 = Vec::new();
                                args63.push(e.get("angle")?);
                                fun65.call(args63, kw64)?
                            })?,
                        )?);
                        s.push(binary(
                            "add",
                            binary("mul", e.get("u")?, {
                                let fun68 = e.get("math")?.attr("sin")?;
                                let mut args66 = Vec::new();
                                let mut kw67 = Vec::new();
                                args66.push(e.get("angle")?);
                                fun68.call(args66, kw67)?
                            })?,
                            binary("mul", e.get("v")?, {
                                let fun71 = e.get("math")?.attr("cos")?;
                                let mut args69 = Vec::new();
                                let mut kw70 = Vec::new();
                                args69.push(e.get("angle")?);
                                fun71.call(args69, kw70)?
                            })?,
                        )?);
                        Val::tuple(s)
                    };
                    let unpack72 = unpack(assigned59.clone(), 2)?;
                    e.set("u", unpack72[0].clone())?;
                    e.set("v", unpack72[1].clone())?;
                    {
                        let fun75 = e.get("cubes")?.attr("append")?;
                        let mut args73 = Vec::new();
                        let mut kw74 = Vec::new();
                        args73.push({
                            let mut s = Vec::new();
                            s.push(e.get("u")?);
                            s.push(e.get("v")?);
                            s.push(e.get("z")?);
                            s.push(e.get("size")?);
                            s.push({
                                let mut s = Vec::new();
                                s.push(e.get("rx")?);
                                s.push(e.get("ry")?);
                                s.push(binary(
                                    "add",
                                    binary("sub", e.get("alignment")?, e.get("yaw")?)?,
                                    e.get("rz")?,
                                )?);
                                Val::tuple(s)
                            });
                            Val::tuple(s)
                        });
                        fun75.call(args73, kw74)?
                    };
                }
            }
            for item83 in {
                let fun121 = e.get("enumerate")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                args119.push(e.get("cubes")?);
                args119.push(Val::Int(1i64));
                fun121.call(args119, kw120)?
            }
            .iter()?
            {
                let unpack122 = unpack(item83, 2)?;
                e.set("i", unpack122[0].clone())?;
                let unpack123 = unpack(unpack122[1].clone(), 5)?;
                e.set("u", unpack123[0].clone())?;
                e.set("v", unpack123[1].clone())?;
                e.set("z", unpack123[2].clone())?;
                e.set("size", unpack123[3].clone())?;
                e.set("angles", unpack123[4].clone())?;
                let assigned84 = {
                    let fun87 = {
                        let fun90 = {
                            let fun93 = {
                                let fun96 = e.get("cq")?.attr("Workplane")?;
                                let mut args94 = Vec::new();
                                let mut kw95 = Vec::new();
                                args94.push(Val::Str("XY".into()));
                                fun96.call(args94, kw95)?
                            }
                            .attr("box")?;
                            let mut args91 = Vec::new();
                            let mut kw92 = Vec::new();
                            args91.extend(e.get("size")?.iter()?);
                            fun93.call(args91, kw92)?
                        }
                        .attr("edges")?;
                        let mut args88 = Vec::new();
                        let mut kw89 = Vec::new();
                        fun90.call(args88, kw89)?
                    }
                    .attr("fillet")?;
                    let mut args85 = Vec::new();
                    let mut kw86 = Vec::new();
                    args85.push(Val::Float(2.1f64));
                    fun87.call(args85, kw86)?
                };
                e.set("cube", assigned84.clone())?;
                for item97 in {
                    let fun104 = e.get("zip")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        });
                        Val::tuple(s)
                    });
                    args102.push(e.get("angles")?);
                    fun104.call(args102, kw103)?
                }
                .iter()?
                {
                    let unpack105 = unpack(item97, 2)?;
                    e.set("axis", unpack105[0].clone())?;
                    e.set("angle", unpack105[1].clone())?;
                    let assigned98 = {
                        let fun101 = e.get("cube")?.attr("rotate")?;
                        let mut args99 = Vec::new();
                        let mut kw100 = Vec::new();
                        args99.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        args99.push(e.get("axis")?);
                        args99.push(e.get("angle")?);
                        fun101.call(args99, kw100)?
                    };
                    e.set("cube", assigned98.clone())?;
                }
                let assigned106 = binary(
                    "add",
                    binary(
                        "add",
                        e.get("GLASS_CENTER")?.get(Val::Int(0i64))?,
                        binary("mul", e.get("right")?.get(Val::Int(0i64))?, e.get("u")?)?,
                    )?,
                    binary("mul", e.get("front")?.get(Val::Int(0i64))?, e.get("v")?)?,
                )?;
                e.set("x", assigned106.clone())?;
                let assigned107 = binary(
                    "add",
                    binary(
                        "add",
                        e.get("GLASS_CENTER")?.get(Val::Int(1i64))?,
                        binary("mul", e.get("right")?.get(Val::Int(1i64))?, e.get("u")?)?,
                    )?,
                    binary("mul", e.get("front")?.get(Val::Int(1i64))?, e.get("v")?)?,
                )?;
                e.set("y", assigned107.clone())?;
                let assigned108 = {
                    let fun111 = e.get("cube")?.attr("translate")?;
                    let mut args109 = Vec::new();
                    let mut kw110 = Vec::new();
                    args109.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    fun111.call(args109, kw110)?
                };
                e.set("cube", assigned108.clone())?;
                {
                    let fun114 = e.get("result")?.attr("add")?;
                    let mut args112 = Vec::new();
                    let mut kw113 = Vec::new();
                    args112.push(e.get("cube")?);
                    kw113.push(("name".into(), {
                        let mut str115 = String::new();
                        str115.push_str("ice-");
                        str115.push_str(&format(&e.get("i")?, &String::new())?);
                        Val::Str(str115)
                    }));
                    kw113.push(("color".into(), {
                        let fun118 = e.get("cq")?.attr("Color")?;
                        let mut args116 = Vec::new();
                        let mut kw117 = Vec::new();
                        args116.push(Val::Float(0.83f64));
                        args116.push(Val::Float(0.92f64));
                        args116.push(Val::Float(0.97f64));
                        fun118.call(args116, kw117)?
                    }));
                    fun114.call(args112, kw113)?
                };
            }
            let assigned124 = {
                let fun127 = e.get("_mesh_payload")?.attr("from_assembly")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.push({
                    let fun130 = e.get("_per_solid_color")?;
                    let mut args128 = Vec::new();
                    let mut kw129 = Vec::new();
                    args128.push(e.get("result")?);
                    fun130.call(args128, kw129)?
                });
                fun127.call(args125, kw126)?
            };
            e.set("ice", assigned124.clone())?;
            let mod131 = rt.import_module("_guide_native")?;
            e.set("ice_colors", rt.member("_guide_native", "ice_colors")?)?;
            e.set("drink_front", rt.member("_guide_native", "drink_front")?)?;
            {
                let fun134 = e.get("ice_colors")?;
                let mut args132 = Vec::new();
                let mut kw133 = Vec::new();
                args132.push(e.get("ice")?);
                fun134.call(args132, kw133)?
            };
            let assigned135 = {
                let fun138 = e.get("next")?;
                let mut args136 = Vec::new();
                let mut kw137 = Vec::new();
                args136.push({
                    let e = e.child();
                    let out139 = Val::list(vec![]);
                    for item140 in e.get("meshes")?.iter()? {
                        e.set("m", item140)?;
                        if {
                            let v141 = e.get("m")?.get(Val::Str("name".into()))?;
                            let v142 = Val::Str("drink".into());
                            Val::Bool(compare("eq", v141.clone(), v142.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out139.attr("append")?.call(vec![e.get("m")?], vec![])?;
                        }
                    }
                    out139
                });
                args136.push(Val::None);
                fun138.call(args136, kw137)?
            };
            e.set("drink", assigned135.clone())?;
            if {
                let v143 = e.get("drink")?;
                let v144 = Val::None;
                Val::Bool(compare("is", v143.clone(), v144.clone())?.truthy()?)
            }
            .truthy()?
            {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun147 = e.get("ValueError")?;
                        let mut args145 = Vec::new();
                        let mut kw146 = Vec::new();
                        args145.push(Val::Str("The frozen first-pour scene has no cola".into()));
                        fun147.call(args145, kw146)?
                    })?
                );
            }
            let assigned148 = {
                let fun151 = e.get("dict")?;
                let mut args149 = Vec::new();
                let mut kw150 = Vec::new();
                args149.push(e.get("drink")?);
                kw150.push(("name".into(), Val::Str("cola-depth".into())));
                fun151.call(args149, kw150)?
            };
            e.set("back", assigned148.clone())?;
            {
                let fun154 = e.get("drink_front")?;
                let mut args152 = Vec::new();
                let mut kw153 = Vec::new();
                args152.push(e.get("drink")?);
                fun154.call(args152, kw153)?
            };
            let assigned155 = binary(
                "truediv",
                e.get("OUT")?,
                Val::Str("pour-with-ice.step.mesh".into()),
            )?;
            e.set("target", assigned155.clone())?;
            {
                let fun158 = e.get("_mesh_payload")?.attr("write")?;
                let mut args156 = Vec::new();
                let mut kw157 = Vec::new();
                args156.push({
                    let mut s = Vec::new();
                    s.extend(e.get("meshes")?.iter()?);
                    s.extend(e.get("ice")?.iter()?);
                    s.push(e.get("back")?);
                    Val::list(s)
                });
                args156.push(e.get("target")?);
                fun158.call(args156, kw157)?
            };
            return Ok(e.get("target")?);
            Ok(Val::None)
        })
    })?;
    // materials
    e.set("materials", {
        let params = vec![
            ("style".into(), None, false),
            ("opacity".into(), None, false),
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
                    let fun161 = e.get("dict")?;
                    let mut args159 = Vec::new();
                    let mut kw160 = Vec::new();
                    kw160.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("cola-depth".into()));
                        Val::list(s)
                    }));
                    kw160.push(("color".into(), Val::Str("#351a0f".into())));
                    kw160.push(("unlit".into(), Val::Bool(true)));
                    kw160.push(("side".into(), Val::Str("back".into())));
                    fun161.call(args159, kw160)?
                });
                s.push({
                    let fun164 = e.get("dict")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    kw163.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("glass".into()));
                        Val::list(s)
                    }));
                    kw163.push(("color".into(), Val::Str("#d6e8ec".into())));
                    kw163.push(("opacity".into(), Val::Float(0.045f64)));
                    kw163.push(("roughness".into(), Val::Float(0.15f64)));
                    kw163.push(("metalness".into(), Val::Float(0.05f64)));
                    kw163.push(("depth_write".into(), Val::Bool(false)));
                    kw163.push(("side".into(), Val::Str("double".into())));
                    kw163.push(("order".into(), Val::Int(10i64)));
                    fun164.call(args162, kw163)?
                });
                s.push({
                    let fun167 = e.get("dict")?;
                    let mut args165 = Vec::new();
                    let mut kw166 = Vec::new();
                    kw166.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("glass-rim".into()));
                        s.push(Val::Str("glass-base".into()));
                        Val::list(s)
                    }));
                    kw166.push(("color".into(), Val::Str("#edf2f3".into())));
                    kw166.push(("unlit".into(), Val::Bool(true)));
                    kw166.push(("side".into(), Val::Str("front".into())));
                    fun167.call(args165, kw166)?
                });
                s.push({
                    let fun170 = e.get("dict")?;
                    let mut args168 = Vec::new();
                    let mut kw169 = Vec::new();
                    kw169.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("drink".into()));
                        Val::list(s)
                    }));
                    kw169.push(("color".into(), Val::Str("#351a0f".into())));
                    kw169.push(("unlit".into(), Val::Bool(true)));
                    kw169.push(("opacity".into(), e.get("opacity")?));
                    kw169.push(("depth_write".into(), {
                        let v171 = e.get("opacity")?;
                        let v172 = Val::Int(1i64);
                        Val::Bool(compare("eq", v171.clone(), v172.clone())?.truthy()?)
                    }));
                    kw169.push(("side".into(), Val::Str("front".into())));
                    kw169.push(("order".into(), Val::Int(2i64)));
                    fun170.call(args168, kw169)?
                });
                s.push({
                    let fun175 = e.get("dict")?;
                    let mut args173 = Vec::new();
                    let mut kw174 = Vec::new();
                    kw174.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("drink-top".into()));
                        Val::list(s)
                    }));
                    kw174.push(("color".into(), Val::Str("#6f422b".into())));
                    kw174.push(("unlit".into(), Val::Bool(true)));
                    kw174.push(("opacity".into(), e.get("opacity")?));
                    kw174.push(("depth_write".into(), {
                        let v176 = e.get("opacity")?;
                        let v177 = Val::Int(1i64);
                        Val::Bool(compare("eq", v176.clone(), v177.clone())?.truthy()?)
                    }));
                    kw174.push(("side".into(), Val::Str("front".into())));
                    kw174.push(("order".into(), Val::Int(3i64)));
                    fun175.call(args173, kw174)?
                });
                s.push({
                    let fun180 = e.get("dict")?;
                    let mut args178 = Vec::new();
                    let mut kw179 = Vec::new();
                    kw179.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("ice-*".into()));
                        Val::list(s)
                    }));
                    kw179.push(("color".into(), Val::Str("#ffffff".into())));
                    kw179.push(("unlit".into(), Val::Bool(true)));
                    kw179.push(("tone_mapped".into(), Val::Bool(false)));
                    kw179.push(("vertex_colors".into(), Val::Bool(true)));
                    kw179.push((
                        "opacity".into(),
                        if {
                            let v181 = e.get("style")?;
                            let v182 = Val::Str("clear".into());
                            Val::Bool(compare("eq", v181.clone(), v182.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            Val::Float(0.78f64)
                        } else {
                            Val::Int(1i64)
                        },
                    ));
                    kw179.push(("depth_write".into(), Val::Bool(true)));
                    kw179.push(("side".into(), Val::Str("front".into())));
                    kw179.push(("order".into(), Val::Int(1i64)));
                    fun180.call(args178, kw179)?
                });
                Val::list(s)
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
            let assigned183 = {
                let fun186 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                kw185.push(("description".into(), e.get("__doc__")?));
                fun186.call(args184, kw185)?
            };
            e.set("parser", assigned183.clone())?;
            {
                let fun189 = e.get("parser")?.attr("add_argument")?;
                let mut args187 = Vec::new();
                let mut kw188 = Vec::new();
                args187.push(Val::Str("--style".into()));
                kw188.push(("choices".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Str("frosted".into()));
                    s.push(Val::Str("clear".into()));
                    Val::list(s)
                }));
                kw188.push(("default".into(), Val::Str("clear".into())));
                fun189.call(args187, kw188)?
            };
            {
                let fun192 = e.get("parser")?.attr("add_argument")?;
                let mut args190 = Vec::new();
                let mut kw191 = Vec::new();
                args190.push(Val::Str("--cola-opacity".into()));
                kw191.push(("type".into(), e.get("float")?));
                kw191.push(("default".into(), Val::Float(0.82f64)));
                fun192.call(args190, kw191)?
            };
            {
                let fun195 = e.get("parser")?.attr("add_argument")?;
                let mut args193 = Vec::new();
                let mut kw194 = Vec::new();
                args193.push(Val::Str("--compare".into()));
                kw194.push(("action".into(), Val::Str("store_true".into())));
                fun195.call(args193, kw194)?
            };
            let assigned196 = {
                let fun199 = e.get("parser")?.attr("parse_args")?;
                let mut args197 = Vec::new();
                let mut kw198 = Vec::new();
                fun199.call(args197, kw198)?
            };
            e.set("args", assigned196.clone())?;
            if unary("not", {
                let v200 = Val::Int(0i64);
                let v201 = e.get("args")?.attr("cola_opacity")?;
                let v202 = Val::Int(1i64);
                Val::Bool(
                    compare("lt", v200.clone(), v201.clone())?.truthy()?
                        && compare("le", v201.clone(), v202.clone())?.truthy()?,
                )
            })?
            .truthy()?
            {
                {
                    let fun205 = e.get("parser")?.attr("error")?;
                    let mut args203 = Vec::new();
                    let mut kw204 = Vec::new();
                    args203.push(Val::Str("--cola-opacity must be between 0 and 1".into()));
                    fun205.call(args203, kw204)?
                };
            }
            {
                let fun208 = e.get("OUT")?.attr("mkdir")?;
                let mut args206 = Vec::new();
                let mut kw207 = Vec::new();
                kw207.push(("parents".into(), Val::Bool(true)));
                kw207.push(("exist_ok".into(), Val::Bool(true)));
                fun208.call(args206, kw207)?
            };
            let assigned209 = {
                let fun212 = e.get("scene")?;
                let mut args210 = Vec::new();
                let mut kw211 = Vec::new();
                fun212.call(args210, kw211)?
            };
            e.set("payload", assigned209.clone())?;
            let assigned213 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("entries", assigned213.clone())?;
            for item214 in if e.get("args")?.attr("compare")?.truthy()? {
                {
                    let mut s = Vec::new();
                    s.push(Val::Float(0.7f64));
                    s.push(Val::Float(0.82f64));
                    Val::list(s)
                }
            } else {
                {
                    let mut s = Vec::new();
                    s.push(e.get("args")?.attr("cola_opacity")?);
                    Val::list(s)
                }
            }
            .iter()?
            {
                e.set("opacity", item214)?;
                let assigned215 = binary("truediv", e.get("OUT")?, {
                    let mut str216 = String::new();
                    str216.push_str("cola-");
                    str216.push_str(&format(
                        &{
                            let fun219 = e.get("round")?;
                            let mut args217 = Vec::new();
                            let mut kw218 = Vec::new();
                            args217.push(binary("mul", e.get("opacity")?, Val::Int(100i64))?);
                            fun219.call(args217, kw218)?
                        },
                        &String::new(),
                    )?);
                    Val::Str(str216)
                })?;
                e.set("directory", assigned215.clone())?;
                {
                    let fun222 = e.get("directory")?.attr("mkdir")?;
                    let mut args220 = Vec::new();
                    let mut kw221 = Vec::new();
                    kw221.push(("exist_ok".into(), Val::Bool(true)));
                    fun222.call(args220, kw221)?
                };
                let assigned223 = {
                    let fun226 = e.get("dict")?;
                    let mut args224 = Vec::new();
                    let mut kw225 = Vec::new();
                    kw225.push(("payload".into(), {
                        let fun229 = e.get("str")?;
                        let mut args227 = Vec::new();
                        let mut kw228 = Vec::new();
                        args227.push(e.get("payload")?);
                        fun229.call(args227, kw228)?
                    }));
                    kw225.push(("out".into(), {
                        let fun232 = e.get("str")?;
                        let mut args230 = Vec::new();
                        let mut kw231 = Vec::new();
                        args230.push(binary(
                            "truediv",
                            e.get("directory")?,
                            Val::Str("pour-base.png".into()),
                        )?);
                        fun232.call(args230, kw231)?
                    }));
                    kw225.push(("materials".into(), {
                        let fun235 = e.get("materials")?;
                        let mut args233 = Vec::new();
                        let mut kw234 = Vec::new();
                        args233.push(e.get("args")?.attr("style")?);
                        args233.push(e.get("opacity")?);
                        fun235.call(args233, kw234)?
                    }));
                    kw225.push(("hide".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("countertop".into()));
                        s.push(Val::Str("glass-edge-*".into()));
                        s.push(Val::Str("glass-highlight-*".into()));
                        s.push(Val::Str("glass-rim-edge".into()));
                        s.push(Val::Str("glass-base-edge".into()));
                        Val::list(s)
                    }));
                    kw225.push(("cam".into(), e.get("CAMERA")?));
                    kw225.push(("target".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(unary("neg", Val::Int(78i64))?);
                        s.push(Val::Int(119i64));
                        Val::tuple(s)
                    }));
                    kw225.push(("span".into(), Val::Int(140i64)));
                    kw225.push(("size".into(), Val::Str("1600x1500".into())));
                    kw225.push(("up".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    }));
                    kw225.push(("bg".into(), Val::Str("#ffffff".into())));
                    kw225.push(("transparent".into(), Val::Bool(true)));
                    kw225.push(("solid".into(), Val::Bool(true)));
                    kw225.push(("ortho".into(), Val::Bool(true)));
                    kw225.push(("trim".into(), Val::Bool(false)));
                    kw225.push(("ground".into(), Val::Bool(false)));
                    kw225.push(("fog".into(), Val::Bool(false)));
                    fun226.call(args224, kw225)?
                };
                e.set("job", assigned223.clone())?;
                {
                    let fun238 = e.get("entries")?.attr("append")?;
                    let mut args236 = Vec::new();
                    let mut kw237 = Vec::new();
                    args236.push(e.get("job")?);
                    fun238.call(args236, kw237)?
                };
            }
            let assigned239 = binary("truediv", e.get("OUT")?, Val::Str("jobs.json".into()))?;
            e.set("jobs", assigned239.clone())?;
            {
                let fun242 = e.get("jobs")?.attr("write_text")?;
                let mut args240 = Vec::new();
                let mut kw241 = Vec::new();
                args240.push(binary(
                    "add",
                    {
                        let fun245 = e.get("json")?.attr("dumps")?;
                        let mut args243 = Vec::new();
                        let mut kw244 = Vec::new();
                        args243.push(e.get("entries")?);
                        kw244.push(("indent".into(), Val::Int(2i64)));
                        fun245.call(args243, kw244)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun242.call(args240, kw241)?
            };
            {
                let fun248 = e.get("_hsm_render")?.attr("render")?;
                let mut args246 = Vec::new();
                let mut kw247 = Vec::new();
                args246.push(e.get("entries")?);
                fun248.call(args246, kw247)?
            };
            for item249 in e.get("entries")?.iter()? {
                e.set("job", item249)?;
                {
                    let fun252 = e.get("print")?;
                    let mut args250 = Vec::new();
                    let mut kw251 = Vec::new();
                    args250.push(e.get("job")?.get(Val::Str("out".into()))?);
                    fun252.call(args250, kw251)?
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun255 = e.get("main")?;
        let mut args253 = Vec::new();
        let mut kw254 = Vec::new();
        fun255.call(args253, kw254)?
    };
    Ok(Val::None)
}
