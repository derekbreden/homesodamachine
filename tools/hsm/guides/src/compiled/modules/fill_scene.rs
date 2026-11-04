//! Guide recipe: `tools/install-guide/fill_scene.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("hashlib", rt.import_module("hashlib")?)?;
    e.set("json", rt.import_module("json")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("shutil", rt.import_module("shutil")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("cairosvg", rt.import_module("cairosvg")?)?;
    let mod2 = rt.import_module("PIL")?;
    e.set("Image", rt.member("PIL", "Image")?)?;
    let mod3 = rt.import_module("fontTools.ttLib")?;
    e.set("TTFont", rt.member("fontTools.ttLib", "TTFont")?)?;
    let mod4 = rt.import_module("fontTools.pens.svgPathPen")?;
    e.set(
        "SVGPathPen",
        rt.member("fontTools.pens.svgPathPen", "SVGPathPen")?,
    )?;
    let assigned5 = {
        let fun8 = {
            let fun11 = e.get("Path")?;
            let mut args9 = Vec::new();
            let mut kw10 = Vec::new();
            args9.push(e.get("__file__")?);
            fun11.call(args9, kw10)?
        }
        .attr("resolve")?;
        let mut args6 = Vec::new();
        let mut kw7 = Vec::new();
        fun8.call(args6, kw7)?
    }
    .attr("parents")?
    .get(Val::Int(2i64))?;
    e.set("ROOT", assigned5.clone())?;
    let assigned12 = binary("truediv", e.get("ROOT")?, Val::Str("hardware".into()))?;
    e.set("HARDWARE", assigned12.clone())?;
    let assigned13 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("install-guide".into()),
    )?;
    e.set("DIR", assigned13.clone())?;
    let assigned14 = binary(
        "truediv",
        e.get("DIR")?,
        Val::Str("out/fill-redesign".into()),
    )?;
    e.set("OUT", assigned14.clone())?;
    let assigned15 = binary(
        "truediv",
        e.get("HARDWARE")?,
        Val::Str("manifold-layout/enclosure-assembly.step".into()),
    )?;
    e.set("SOURCE", assigned15.clone())?;
    let assigned16 = {
        let fun19 = e.get("SOURCE")?.attr("with_suffix")?;
        let mut args17 = Vec::new();
        let mut kw18 = Vec::new();
        args17.push(Val::Str(".facts.json".into()));
        fun19.call(args17, kw18)?
    };
    e.set("FACTS", assigned16.clone())?;
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
                e.get("HARDWARE")?,
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
            args29.push(binary(
                "truediv",
                e.get("HARDWARE")?,
                Val::Str("printed-parts/enclosure/enclosure".into()),
            )?);
            fun31.call(args29, kw30)?
        });
        fun28.call(args26, kw27)?
    };
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    e.set("_mesh_payload", rt.import_module("_mesh_payload")?)?;
    let mod32 = rt.import_module("flute_payload")?;
    e.set("read_payload", rt.member("flute_payload", "read_payload")?)?;
    e.set("_swept_top", rt.import_module("_swept_top")?)?;
    e.set(
        "_enclosure_interface",
        rt.import_module("_enclosure_interface")?,
    )?;
    let assigned33 = {
        let fun36 = e.get("json")?.attr("loads")?;
        let mut args34 = Vec::new();
        let mut kw35 = Vec::new();
        args34.push({
            let fun39 = e.get("FACTS")?.attr("read_text")?;
            let mut args37 = Vec::new();
            let mut kw38 = Vec::new();
            fun39.call(args37, kw38)?
        });
        fun36.call(args34, kw35)?
    };
    e.set("ASSEMBLY_FACTS", assigned33.clone())?;
    let assigned40 = e
        .get("ASSEMBLY_FACTS")?
        .get(Val::Str("bodies".into()))?
        .get(Val::Str("funnel".into()))?;
    e.set("FUNNEL_BOUNDS", assigned40.clone())?;
    let assigned41 = Val::Int(20i64);
    e.set("TIP", assigned41.clone())?;
    let assigned42 = Val::Int(3i64);
    e.set("CLEARANCE", assigned42.clone())?;
    let assigned43 = {
        let mut s = Vec::new();
        s.push(Val::Int(0i64));
        s.push(unary("neg", {
            let fun46 = e.get("math")?.attr("cos")?;
            let mut args44 = Vec::new();
            let mut kw45 = Vec::new();
            args44.push({
                let fun49 = e.get("math")?.attr("radians")?;
                let mut args47 = Vec::new();
                let mut kw48 = Vec::new();
                args47.push(e.get("TIP")?);
                fun49.call(args47, kw48)?
            });
            fun46.call(args44, kw45)?
        })?);
        s.push({
            let fun52 = e.get("math")?.attr("sin")?;
            let mut args50 = Vec::new();
            let mut kw51 = Vec::new();
            args50.push({
                let fun55 = e.get("math")?.attr("radians")?;
                let mut args53 = Vec::new();
                let mut kw54 = Vec::new();
                args53.push(e.get("TIP")?);
                fun55.call(args53, kw54)?
            });
            fun52.call(args50, kw51)?
        });
        Val::tuple(s)
    };
    e.set("AXIS", assigned43.clone())?;
    let assigned56 = {
        let mut s = Vec::new();
        s.push(Val::Int(1i64));
        s.push(unary("neg", Val::Float(0.5f64))?);
        s.push(Val::Float(0.45f64));
        Val::tuple(s)
    };
    e.set("CAMERA", assigned56.clone())?;
    let assigned57 = {
        let mut s = Vec::new();
        s.push(Val::Int(0i64));
        s.push(Val::Int(150i64));
        s.push(Val::Int(380i64));
        Val::tuple(s)
    };
    e.set("TARGET", assigned57.clone())?;
    let assigned58 = Val::Int(230i64);
    e.set("SPAN", assigned58.clone())?;
    let assigned59 = {
        let mut s = Vec::new();
        s.push(Val::Int(225i64));
        s.push(Val::Int(0i64));
        Val::tuple(s)
    };
    let unpack60 = unpack(assigned59.clone(), 2)?;
    e.set("SWING_R", unpack60[0].clone())?;
    e.set("SWING_FROM", unpack60[1].clone())?;
    let assigned61 = {
        let fun64 = e.get("_swept_top")?.attr("profile")?;
        let mut args62 = Vec::new();
        let mut kw63 = Vec::new();
        args62.push(
            e.get("ASSEMBLY_FACTS")?
                .get(Val::Str("box".into()))?
                .get(Val::Str("outer".into()))?,
        );
        fun64.call(args62, kw63)?
    };
    e.set("DISPLAY_PROFILE", assigned61.clone())?;
    let assigned65 = {
        let fun68 = e.get("dict")?;
        let mut args66 = Vec::new();
        let mut kw67 = Vec::new();
        kw67.push(("width".into(), Val::Float(103.5f64)));
        kw67.push(("height".into(), Val::Float(62.1f64)));
        kw67.push(("angle_deg".into(), e.get("_swept_top")?.attr("ANGLE")?));
        kw67.push(("origin".into(), {
            let e = e.child();
            let out69 = Val::list(vec![]);
            for item70 in {
                let fun73 = e.get("zip")?;
                let mut args71 = Vec::new();
                let mut kw72 = Vec::new();
                args71.push(e.get("DISPLAY_PROFILE")?.get(Val::Str("origin".into()))?);
                args71.push(e.get("DISPLAY_PROFILE")?.get(Val::Str("normal".into()))?);
                fun73.call(args71, kw72)?
            }
            .iter()?
            {
                let unpack74 = unpack(item70, 2)?;
                e.set("p", unpack74[0].clone())?;
                e.set("n", unpack74[1].clone())?;
                out69.attr("append")?.call(
                    vec![binary(
                        "sub",
                        e.get("p")?,
                        binary(
                            "mul",
                            e.get("n")?,
                            binary(
                                "sub",
                                binary(
                                    "sub",
                                    e.get("_enclosure_interface")?.attr("display_bezel_depth")?,
                                    Val::Int(1i64),
                                )?,
                                Val::Float(0.05f64),
                            )?,
                        )?,
                    )?],
                    vec![],
                )?;
            }
            out69
        }));
        fun68.call(args66, kw67)?
    };
    e.set("SCREEN", assigned65.clone())?;
    let assigned75 = {
        let mut s = Vec::new();
        s.push(Val::Str("funnel".into()));
        s.push(Val::Str("funnel-cover".into()));
        s.push(Val::Str("funnel-frame".into()));
        s.push(Val::Str("nameplate".into()));
        s.push(Val::Str("nameplate-ink".into()));
        s.push(Val::Str("enclosure-front-top".into()));
        s.push(Val::Str("enclosure-front-bottom".into()));
        s.push(Val::Str("enclosure-back-top".into()));
        s.push(Val::Str("enclosure-back-bottom".into()));
        Val::set_values(s)
    };
    e.set("EXTERIOR", assigned75.clone())?;
    // visible
    e.set("visible", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let v78 = {
                    let v82 = {
                        let fun81 = e.get("name")?.attr("split")?;
                        let mut args79 = Vec::new();
                        let mut kw80 = Vec::new();
                        args79.push(Val::Str("/".into()));
                        fun81.call(args79, kw80)?
                    }
                    .get(Val::Int(0i64))?;
                    let v83 = e.get("EXTERIOR")?;
                    Val::Bool(compare("in", v82.clone(), v83.clone())?.truthy()?)
                };
                if v78.truthy()? {
                    v78
                } else {
                    {
                        let v76 = Val::Str("display".into());
                        let v77 = e.get("name")?;
                        Val::Bool(compare("in", v76.clone(), v77.clone())?.truthy()?)
                    }
                }
            });
            Ok(Val::None)
        })
    })?;
    // bottle
    e.set("bottle", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned84 = {
                let fun87 = {
                    let fun90 = {
                        let fun93 = {
                            let fun96 = {
                                let fun99 = {
                                    let fun102 = {
                                        let fun105 = {
                                            let fun108 = {
                                                let fun111 = {
                                                    let fun114 = {
                                                        let fun117 = {
                                                            let fun120 =
                                                                e.get("cq")?.attr("Workplane")?;
                                                            let mut args118 = Vec::new();
                                                            let mut kw119 = Vec::new();
                                                            args118.push(Val::Str("XZ".into()));
                                                            fun120.call(args118, kw119)?
                                                        }
                                                        .attr("moveTo")?;
                                                        let mut args115 = Vec::new();
                                                        let mut kw116 = Vec::new();
                                                        args115.push(Val::Int(0i64));
                                                        args115.push(Val::Int(0i64));
                                                        fun117.call(args115, kw116)?
                                                    }
                                                    .attr("lineTo")?;
                                                    let mut args112 = Vec::new();
                                                    let mut kw113 = Vec::new();
                                                    args112.push(Val::Float(13.5f64));
                                                    args112.push(Val::Int(0i64));
                                                    fun114.call(args112, kw113)?
                                                }
                                                .attr("lineTo")?;
                                                let mut args109 = Vec::new();
                                                let mut kw110 = Vec::new();
                                                args109.push(Val::Float(13.5f64));
                                                args109.push(Val::Int(23i64));
                                                fun111.call(args109, kw110)?
                                            }
                                            .attr("threePointArc")?;
                                            let mut args106 = Vec::new();
                                            let mut kw107 = Vec::new();
                                            args106.push({
                                                let mut s = Vec::new();
                                                s.push(Val::Float(14.3f64));
                                                s.push(Val::Int(29i64));
                                                Val::tuple(s)
                                            });
                                            args106.push({
                                                let mut s = Vec::new();
                                                s.push(Val::Int(18i64));
                                                s.push(Val::Int(34i64));
                                                Val::tuple(s)
                                            });
                                            fun108.call(args106, kw107)?
                                        }
                                        .attr("lineTo")?;
                                        let mut args103 = Vec::new();
                                        let mut kw104 = Vec::new();
                                        args103.push(Val::Int(29i64));
                                        args103.push(Val::Int(52i64));
                                        fun105.call(args103, kw104)?
                                    }
                                    .attr("threePointArc")?;
                                    let mut args100 = Vec::new();
                                    let mut kw101 = Vec::new();
                                    args100.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Float(31.8f64));
                                        s.push(Val::Int(58i64));
                                        Val::tuple(s)
                                    });
                                    args100.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Int(32i64));
                                        s.push(Val::Int(66i64));
                                        Val::tuple(s)
                                    });
                                    fun102.call(args100, kw101)?
                                }
                                .attr("lineTo")?;
                                let mut args97 = Vec::new();
                                let mut kw98 = Vec::new();
                                args97.push(Val::Float(32.5f64));
                                args97.push(Val::Int(190i64));
                                fun99.call(args97, kw98)?
                            }
                            .attr("threePointArc")?;
                            let mut args94 = Vec::new();
                            let mut kw95 = Vec::new();
                            args94.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(31.9f64));
                                s.push(Val::Int(198i64));
                                Val::tuple(s)
                            });
                            args94.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(27.5f64));
                                s.push(Val::Int(202i64));
                                Val::tuple(s)
                            });
                            fun96.call(args94, kw95)?
                        }
                        .attr("lineTo")?;
                        let mut args91 = Vec::new();
                        let mut kw92 = Vec::new();
                        args91.push(Val::Int(0i64));
                        args91.push(Val::Int(202i64));
                        fun93.call(args91, kw92)?
                    }
                    .attr("close")?;
                    let mut args88 = Vec::new();
                    let mut kw89 = Vec::new();
                    fun90.call(args88, kw89)?
                }
                .attr("revolve")?;
                let mut args85 = Vec::new();
                let mut kw86 = Vec::new();
                fun87.call(args85, kw86)?
            };
            e.set("outer", assigned84.clone())?;
            let assigned121 = {
                let fun124 = {
                    let fun127 = {
                        let fun130 = {
                            let fun133 = {
                                let fun136 = {
                                    let fun139 = {
                                        let fun142 = {
                                            let fun145 = {
                                                let fun148 = {
                                                    let fun151 = {
                                                        let fun154 = {
                                                            let fun157 =
                                                                e.get("cq")?.attr("Workplane")?;
                                                            let mut args155 = Vec::new();
                                                            let mut kw156 = Vec::new();
                                                            args155.push(Val::Str("XZ".into()));
                                                            fun157.call(args155, kw156)?
                                                        }
                                                        .attr("moveTo")?;
                                                        let mut args152 = Vec::new();
                                                        let mut kw153 = Vec::new();
                                                        args152.push(Val::Int(0i64));
                                                        args152.push(unary("neg", Val::Int(1i64))?);
                                                        fun154.call(args152, kw153)?
                                                    }
                                                    .attr("lineTo")?;
                                                    let mut args149 = Vec::new();
                                                    let mut kw150 = Vec::new();
                                                    args149.push(Val::Float(11.5f64));
                                                    args149.push(unary("neg", Val::Int(1i64))?);
                                                    fun151.call(args149, kw150)?
                                                }
                                                .attr("lineTo")?;
                                                let mut args146 = Vec::new();
                                                let mut kw147 = Vec::new();
                                                args146.push(Val::Float(11.5f64));
                                                args146.push(Val::Int(24i64));
                                                fun148.call(args146, kw147)?
                                            }
                                            .attr("lineTo")?;
                                            let mut args143 = Vec::new();
                                            let mut kw144 = Vec::new();
                                            args143.push(Val::Float(16.4f64));
                                            args143.push(Val::Int(34i64));
                                            fun145.call(args143, kw144)?
                                        }
                                        .attr("lineTo")?;
                                        let mut args140 = Vec::new();
                                        let mut kw141 = Vec::new();
                                        args140.push(Val::Int(28i64));
                                        args140.push(Val::Int(53i64));
                                        fun142.call(args140, kw141)?
                                    }
                                    .attr("threePointArc")?;
                                    let mut args137 = Vec::new();
                                    let mut kw138 = Vec::new();
                                    args137.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Float(30.7f64));
                                        s.push(Val::Int(60i64));
                                        Val::tuple(s)
                                    });
                                    args137.push({
                                        let mut s = Vec::new();
                                        s.push(Val::Int(31i64));
                                        s.push(Val::Int(66i64));
                                        Val::tuple(s)
                                    });
                                    fun139.call(args137, kw138)?
                                }
                                .attr("lineTo")?;
                                let mut args134 = Vec::new();
                                let mut kw135 = Vec::new();
                                args134.push(Val::Float(31.5f64));
                                args134.push(Val::Int(190i64));
                                fun136.call(args134, kw135)?
                            }
                            .attr("threePointArc")?;
                            let mut args131 = Vec::new();
                            let mut kw132 = Vec::new();
                            args131.push({
                                let mut s = Vec::new();
                                s.push(Val::Float(30.9f64));
                                s.push(Val::Int(196i64));
                                Val::tuple(s)
                            });
                            args131.push({
                                let mut s = Vec::new();
                                s.push(Val::Int(26i64));
                                s.push(Val::Int(198i64));
                                Val::tuple(s)
                            });
                            fun133.call(args131, kw132)?
                        }
                        .attr("lineTo")?;
                        let mut args128 = Vec::new();
                        let mut kw129 = Vec::new();
                        args128.push(Val::Int(0i64));
                        args128.push(Val::Int(198i64));
                        fun130.call(args128, kw129)?
                    }
                    .attr("close")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    fun127.call(args125, kw126)?
                }
                .attr("revolve")?;
                let mut args122 = Vec::new();
                let mut kw123 = Vec::new();
                fun124.call(args122, kw123)?
            };
            e.set("inside", assigned121.clone())?;
            let assigned158 = {
                let fun161 = {
                    let fun164 = {
                        let fun167 = {
                            let fun170 = {
                                let fun173 = {
                                    let fun176 = {
                                        let fun179 = {
                                            let fun182 = e.get("cq")?.attr("Workplane")?;
                                            let mut args180 = Vec::new();
                                            let mut kw181 = Vec::new();
                                            args180.push(Val::Str("XZ".into()));
                                            fun182.call(args180, kw181)?
                                        }
                                        .attr("moveTo")?;
                                        let mut args177 = Vec::new();
                                        let mut kw178 = Vec::new();
                                        args177.push(Val::Int(0i64));
                                        args177.push(Val::Int(200i64));
                                        fun179.call(args177, kw178)?
                                    }
                                    .attr("lineTo")?;
                                    let mut args174 = Vec::new();
                                    let mut kw175 = Vec::new();
                                    args174.push(Val::Int(16i64));
                                    args174.push(Val::Int(200i64));
                                    fun176.call(args174, kw175)?
                                }
                                .attr("threePointArc")?;
                                let mut args171 = Vec::new();
                                let mut kw172 = Vec::new();
                                args171.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Int(21i64));
                                    s.push(Val::Int(201i64));
                                    Val::tuple(s)
                                });
                                args171.push({
                                    let mut s = Vec::new();
                                    s.push(Val::Int(25i64));
                                    s.push(Val::Int(203i64));
                                    Val::tuple(s)
                                });
                                fun173.call(args171, kw172)?
                            }
                            .attr("lineTo")?;
                            let mut args168 = Vec::new();
                            let mut kw169 = Vec::new();
                            args168.push(Val::Int(25i64));
                            args168.push(Val::Int(206i64));
                            fun170.call(args168, kw169)?
                        }
                        .attr("lineTo")?;
                        let mut args165 = Vec::new();
                        let mut kw166 = Vec::new();
                        args165.push(Val::Int(0i64));
                        args165.push(Val::Int(206i64));
                        fun167.call(args165, kw166)?
                    }
                    .attr("close")?;
                    let mut args162 = Vec::new();
                    let mut kw163 = Vec::new();
                    fun164.call(args162, kw163)?
                }
                .attr("revolve")?;
                let mut args159 = Vec::new();
                let mut kw160 = Vec::new();
                fun161.call(args159, kw160)?
            };
            e.set("recess", assigned158.clone())?;
            let assigned183 = {
                let fun186 = {
                    let fun189 = e.get("outer")?.attr("cut")?;
                    let mut args187 = Vec::new();
                    let mut kw188 = Vec::new();
                    args187.push(e.get("inside")?);
                    fun189.call(args187, kw188)?
                }
                .attr("cut")?;
                let mut args184 = Vec::new();
                let mut kw185 = Vec::new();
                args184.push(e.get("recess")?);
                fun186.call(args184, kw185)?
            };
            e.set("shell", assigned183.clone())?;
            let assigned190 = {
                let fun193 = {
                    let fun196 = {
                        let fun199 = e.get("inside")?.attr("intersect")?;
                        let mut args197 = Vec::new();
                        let mut kw198 = Vec::new();
                        args197.push({
                            let fun202 = {
                                let fun205 = e.get("cq")?.attr("Workplane")?;
                                let mut args203 = Vec::new();
                                let mut kw204 = Vec::new();
                                args203.push(Val::Str("XY".into()));
                                fun205.call(args203, kw204)?
                            }
                            .attr("box")?;
                            let mut args200 = Vec::new();
                            let mut kw201 = Vec::new();
                            args200.push(Val::Int(80i64));
                            args200.push(Val::Int(80i64));
                            args200.push(Val::Int(186i64));
                            kw201.push(("centered".into(), {
                                let mut s = Vec::new();
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(false));
                                Val::tuple(s)
                            }));
                            fun202.call(args200, kw201)?
                        });
                        fun199.call(args197, kw198)?
                    }
                    .attr("val")?;
                    let mut args194 = Vec::new();
                    let mut kw195 = Vec::new();
                    fun196.call(args194, kw195)?
                }
                .attr("Volume")?;
                let mut args191 = Vec::new();
                let mut kw192 = Vec::new();
                fun193.call(args191, kw192)?
            };
            e.set("volume", assigned190.clone())?;
            let assigned206 = {
                let fun209 = {
                    let fun212 = {
                        let fun215 = {
                            let fun218 = {
                                let fun221 = e.get("cq")?.attr("Workplane")?;
                                let mut args219 = Vec::new();
                                let mut kw220 = Vec::new();
                                args219.push(Val::Str("XY".into()));
                                fun221.call(args219, kw220)?
                            }
                            .attr("workplane")?;
                            let mut args216 = Vec::new();
                            let mut kw217 = Vec::new();
                            kw217.push(("offset".into(), Val::Int(2i64)));
                            fun218.call(args216, kw217)?
                        }
                        .attr("circle")?;
                        let mut args213 = Vec::new();
                        let mut kw214 = Vec::new();
                        args213.push(Val::Float(15.2f64));
                        fun215.call(args213, kw214)?
                    }
                    .attr("circle")?;
                    let mut args210 = Vec::new();
                    let mut kw211 = Vec::new();
                    args210.push(Val::Float(13.4f64));
                    fun212.call(args210, kw211)?
                }
                .attr("extrude")?;
                let mut args207 = Vec::new();
                let mut kw208 = Vec::new();
                args207.push(Val::Int(17i64));
                fun209.call(args207, kw208)?
            };
            e.set("grip", assigned206.clone())?;
            let assigned222 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("shell")?);
                    s.push(Val::Str("bottle-pet".into()));
                    s.push({
                        let fun225 = e.get("cq")?.attr("Color")?;
                        let mut args223 = Vec::new();
                        let mut kw224 = Vec::new();
                        args223.push(Val::Float(0.85f64));
                        args223.push(Val::Float(0.89f64));
                        args223.push(Val::Float(0.9f64));
                        fun225.call(args223, kw224)?
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("grip")?);
                    s.push(Val::Str("bottle-collar".into()));
                    s.push({
                        let fun228 = e.get("cq")?.attr("Color")?;
                        let mut args226 = Vec::new();
                        let mut kw227 = Vec::new();
                        args226.push(Val::Float(0.065f64));
                        args226.push(Val::Float(0.065f64));
                        args226.push(Val::Float(0.065f64));
                        fun228.call(args226, kw227)?
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("parts", assigned222.clone())?;
            for item229 in {
                let fun252 = e.get("range")?;
                let mut args250 = Vec::new();
                let mut kw251 = Vec::new();
                args250.push(Val::Int(36i64));
                fun252.call(args250, kw251)?
            }
            .iter()?
            {
                e.set("i", item229)?;
                let assigned230 = {
                    let fun233 = {
                        let fun236 = {
                            let fun239 = {
                                let fun242 = e.get("cq")?.attr("Workplane")?;
                                let mut args240 = Vec::new();
                                let mut kw241 = Vec::new();
                                args240.push(Val::Str("XY".into()));
                                fun242.call(args240, kw241)?
                            }
                            .attr("box")?;
                            let mut args237 = Vec::new();
                            let mut kw238 = Vec::new();
                            args237.push(Val::Float(1.1f64));
                            args237.push(Val::Float(0.8f64));
                            args237.push(Val::Int(14i64));
                            fun239.call(args237, kw238)?
                        }
                        .attr("translate")?;
                        let mut args234 = Vec::new();
                        let mut kw235 = Vec::new();
                        args234.push({
                            let mut s = Vec::new();
                            s.push(Val::Float(15.25f64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Float(10.5f64));
                            Val::tuple(s)
                        });
                        fun236.call(args234, kw235)?
                    }
                    .attr("rotate")?;
                    let mut args231 = Vec::new();
                    let mut kw232 = Vec::new();
                    args231.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    args231.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    args231.push(binary("mul", e.get("i")?, Val::Int(10i64))?);
                    fun233.call(args231, kw232)?
                };
                e.set("rib", assigned230.clone())?;
                {
                    let fun245 = e.get("parts")?.attr("append")?;
                    let mut args243 = Vec::new();
                    let mut kw244 = Vec::new();
                    args243.push({
                        let mut s = Vec::new();
                        s.push(e.get("rib")?);
                        s.push({
                            let mut str246 = String::new();
                            str246.push_str("bottle-grip-");
                            str246.push_str(&format(&e.get("i")?, &String::new())?);
                            Val::Str(str246)
                        });
                        s.push({
                            let fun249 = e.get("cq")?.attr("Color")?;
                            let mut args247 = Vec::new();
                            let mut kw248 = Vec::new();
                            args247.push(Val::Float(0.08f64));
                            args247.push(Val::Float(0.08f64));
                            args247.push(Val::Float(0.08f64));
                            fun249.call(args247, kw248)?
                        });
                        Val::tuple(s)
                    });
                    fun245.call(args243, kw244)?
                };
            }
            for item253 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Float(14.5f64));
                    s.push(Val::Float(1.6f64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Float(20.5f64));
                    s.push(Val::Float(15.4f64));
                    s.push(Val::Float(1.8f64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(24i64));
                    s.push(Val::Float(14.6f64));
                    s.push(Val::Float(1.2f64));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack277 = unpack(item253, 3)?;
                e.set("z", unpack277[0].clone())?;
                e.set("radius", unpack277[1].clone())?;
                e.set("height", unpack277[2].clone())?;
                let assigned254 = {
                    let fun257 = {
                        let fun260 = {
                            let fun263 = {
                                let fun266 = {
                                    let fun269 = e.get("cq")?.attr("Workplane")?;
                                    let mut args267 = Vec::new();
                                    let mut kw268 = Vec::new();
                                    args267.push(Val::Str("XY".into()));
                                    fun269.call(args267, kw268)?
                                }
                                .attr("workplane")?;
                                let mut args264 = Vec::new();
                                let mut kw265 = Vec::new();
                                kw265.push(("offset".into(), e.get("z")?));
                                fun266.call(args264, kw265)?
                            }
                            .attr("circle")?;
                            let mut args261 = Vec::new();
                            let mut kw262 = Vec::new();
                            args261.push(e.get("radius")?);
                            fun263.call(args261, kw262)?
                        }
                        .attr("circle")?;
                        let mut args258 = Vec::new();
                        let mut kw259 = Vec::new();
                        args258.push(Val::Float(11.5f64));
                        fun260.call(args258, kw259)?
                    }
                    .attr("extrude")?;
                    let mut args255 = Vec::new();
                    let mut kw256 = Vec::new();
                    args255.push(e.get("height")?);
                    fun257.call(args255, kw256)?
                };
                e.set("ring", assigned254.clone())?;
                {
                    let fun272 = e.get("parts")?.attr("append")?;
                    let mut args270 = Vec::new();
                    let mut kw271 = Vec::new();
                    args270.push({
                        let mut s = Vec::new();
                        s.push(e.get("ring")?);
                        s.push({
                            let mut str273 = String::new();
                            str273.push_str("bottle-ring-");
                            str273.push_str(&format(&e.get("z")?, &String::new())?);
                            Val::Str(str273)
                        });
                        s.push({
                            let fun276 = e.get("cq")?.attr("Color")?;
                            let mut args274 = Vec::new();
                            let mut kw275 = Vec::new();
                            args274.push(Val::Float(0.81f64));
                            args274.push(Val::Float(0.85f64));
                            args274.push(Val::Float(0.86f64));
                            fun276.call(args274, kw275)?
                        });
                        Val::tuple(s)
                    });
                    fun272.call(args270, kw271)?
                };
            }
            // tipped
            e.set("tipped", {
                let params = vec![("shape".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun280 = e.get("shape")?.attr("rotate")?;
                        let mut args278 = Vec::new();
                        let mut kw279 = Vec::new();
                        args278.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        args278.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        args278.push(binary("sub", Val::Int(90i64), e.get("TIP")?)?);
                        fun280.call(args278, kw279)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned281 = {
                let e = e.child();
                let out282 = Val::list(vec![]);
                for item283 in e.get("parts")?.iter()? {
                    let unpack284 = unpack(item283, 3)?;
                    e.set("shape", unpack284[0].clone())?;
                    e.set("name", unpack284[1].clone())?;
                    e.set("color", unpack284[2].clone())?;
                    out282.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push({
                                let fun287 = e.get("tipped")?;
                                let mut args285 = Vec::new();
                                let mut kw286 = Vec::new();
                                args285.push(e.get("shape")?);
                                fun287.call(args285, kw286)?
                            });
                            s.push(e.get("name")?);
                            s.push(e.get("color")?);
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out282
            };
            e.set("parts", assigned281.clone())?;
            let assigned288 = {
                let fun291 = e.get("tipped")?;
                let mut args289 = Vec::new();
                let mut kw290 = Vec::new();
                args289.push(e.get("inside")?);
                fun291.call(args289, kw290)?
            };
            e.set("inside", assigned288.clone())?;
            let assigned292 = {
                let fun295 = {
                    let fun298 = e.get("inside")?.attr("val")?;
                    let mut args296 = Vec::new();
                    let mut kw297 = Vec::new();
                    fun298.call(args296, kw297)?
                }
                .attr("BoundingBox")?;
                let mut args293 = Vec::new();
                let mut kw294 = Vec::new();
                fun295.call(args293, kw294)?
            };
            e.set("bounds", assigned292.clone())?;
            // settled
            e.set("settled", {
                let params = vec![("level".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun301 = e.get("inside")?.attr("intersect")?;
                        let mut args299 = Vec::new();
                        let mut kw300 = Vec::new();
                        args299.push({
                            let fun304 = {
                                let fun307 = e.get("cq")?.attr("Workplane")?;
                                let mut args305 = Vec::new();
                                let mut kw306 = Vec::new();
                                args305.push(Val::Str("XY".into()));
                                kw306.push(("origin".into(), {
                                    let mut s = Vec::new();
                                    s.push(Val::Int(0i64));
                                    s.push(Val::Int(0i64));
                                    s.push(binary(
                                        "sub",
                                        e.get("bounds")?.attr("zmin")?,
                                        Val::Int(1i64),
                                    )?);
                                    Val::tuple(s)
                                }));
                                fun307.call(args305, kw306)?
                            }
                            .attr("box")?;
                            let mut args302 = Vec::new();
                            let mut kw303 = Vec::new();
                            args302.push(Val::Int(400i64));
                            args302.push(Val::Int(400i64));
                            args302.push(binary(
                                "add",
                                binary("sub", e.get("level")?, e.get("bounds")?.attr("zmin")?)?,
                                Val::Int(1i64),
                            )?);
                            kw303.push(("centered".into(), {
                                let mut s = Vec::new();
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(true));
                                s.push(Val::Bool(false));
                                Val::tuple(s)
                            }));
                            fun304.call(args302, kw303)?
                        });
                        fun301.call(args299, kw300)?
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned308 = {
                let mut s = Vec::new();
                s.push(e.get("bounds")?.attr("zmin")?);
                s.push(e.get("bounds")?.attr("zmax")?);
                Val::tuple(s)
            };
            let unpack309 = unpack(assigned308.clone(), 2)?;
            e.set("low", unpack309[0].clone())?;
            e.set("high", unpack309[1].clone())?;
            for item310 in {
                let fun327 = e.get("range")?;
                let mut args325 = Vec::new();
                let mut kw326 = Vec::new();
                args325.push(Val::Int(20i64));
                fun327.call(args325, kw326)?
            }
            .iter()?
            {
                e.set("_", item310)?;
                let assigned311 = binary(
                    "truediv",
                    binary("add", e.get("low")?, e.get("high")?)?,
                    Val::Int(2i64),
                )?;
                e.set("level", assigned311.clone())?;
                let assigned312 = if {
                    let v322 = {
                        let fun315 = {
                            let fun318 = {
                                let fun321 = e.get("settled")?;
                                let mut args319 = Vec::new();
                                let mut kw320 = Vec::new();
                                args319.push(e.get("level")?);
                                fun321.call(args319, kw320)?
                            }
                            .attr("val")?;
                            let mut args316 = Vec::new();
                            let mut kw317 = Vec::new();
                            fun318.call(args316, kw317)?
                        }
                        .attr("Volume")?;
                        let mut args313 = Vec::new();
                        let mut kw314 = Vec::new();
                        fun315.call(args313, kw314)?
                    };
                    let v323 = e.get("volume")?;
                    Val::Bool(compare("lt", v322.clone(), v323.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let mut s = Vec::new();
                        s.push(e.get("level")?);
                        s.push(e.get("high")?);
                        Val::tuple(s)
                    }
                } else {
                    {
                        let mut s = Vec::new();
                        s.push(e.get("low")?);
                        s.push(e.get("level")?);
                        Val::tuple(s)
                    }
                };
                let unpack324 = unpack(assigned312.clone(), 2)?;
                e.set("low", unpack324[0].clone())?;
                e.set("high", unpack324[1].clone())?;
            }
            {
                let fun330 = e.get("parts")?.attr("insert")?;
                let mut args328 = Vec::new();
                let mut kw329 = Vec::new();
                args328.push(Val::Int(1i64));
                args328.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun333 = e.get("settled")?;
                        let mut args331 = Vec::new();
                        let mut kw332 = Vec::new();
                        args331.push(e.get("low")?);
                        fun333.call(args331, kw332)?
                    });
                    s.push(Val::Str("bottle-concentrate".into()));
                    s.push({
                        let fun336 = e.get("cq")?.attr("Color")?;
                        let mut args334 = Vec::new();
                        let mut kw335 = Vec::new();
                        args334.push(Val::Float(0.22f64));
                        args334.push(Val::Float(0.09f64));
                        args334.push(Val::Float(0.035f64));
                        fun336.call(args334, kw335)?
                    });
                    Val::tuple(s)
                });
                fun330.call(args328, kw329)?
            };
            let assigned337 = {
                let fun340 = e.get("min")?;
                let mut args338 = Vec::new();
                let mut kw339 = Vec::new();
                args338.push({
                    let e = e.child();
                    let out341 = Val::list(vec![]);
                    for item342 in e.get("parts")?.iter()? {
                        let unpack343 = unpack(item342, 3)?;
                        e.set("shape", unpack343[0].clone())?;
                        e.set("_", unpack343[1].clone())?;
                        e.set("_", unpack343[2].clone())?;
                        out341.attr("append")?.call(
                            vec![
                                {
                                    let fun346 = {
                                        let fun349 = e.get("shape")?.attr("val")?;
                                        let mut args347 = Vec::new();
                                        let mut kw348 = Vec::new();
                                        fun349.call(args347, kw348)?
                                    }
                                    .attr("BoundingBox")?;
                                    let mut args344 = Vec::new();
                                    let mut kw345 = Vec::new();
                                    fun346.call(args344, kw345)?
                                }
                                .attr("zmin")?,
                            ],
                            vec![],
                        )?;
                    }
                    out341
                });
                fun340.call(args338, kw339)?
            };
            e.set("lowest", assigned337.clone())?;
            let assigned350 = {
                let mut s = Vec::new();
                s.extend(
                    e.get("ASSEMBLY_FACTS")?
                        .get(Val::Str("box".into()))?
                        .get(Val::Str("funnel".into()))?
                        .iter()?,
                );
                s.push(binary(
                    "sub",
                    binary(
                        "add",
                        e.get("FUNNEL_BOUNDS")?.get(Val::Int(5i64))?,
                        e.get("CLEARANCE")?,
                    )?,
                    e.get("lowest")?,
                )?);
                Val::tuple(s)
            };
            e.set("mouth", assigned350.clone())?;
            let assigned351 = {
                let fun354 = e.get("cq")?.attr("Assembly")?;
                let mut args352 = Vec::new();
                let mut kw353 = Vec::new();
                kw353.push(("name".into(), Val::Str("concentrate-bottle".into())));
                fun354.call(args352, kw353)?
            };
            e.set("a", assigned351.clone())?;
            for item355 in e.get("parts")?.iter()? {
                let unpack362 = unpack(item355, 3)?;
                e.set("shape", unpack362[0].clone())?;
                e.set("name", unpack362[1].clone())?;
                e.set("color", unpack362[2].clone())?;
                {
                    let fun358 = e.get("a")?.attr("add")?;
                    let mut args356 = Vec::new();
                    let mut kw357 = Vec::new();
                    args356.push({
                        let fun361 = e.get("shape")?.attr("translate")?;
                        let mut args359 = Vec::new();
                        let mut kw360 = Vec::new();
                        args359.push(e.get("mouth")?);
                        fun361.call(args359, kw360)?
                    });
                    kw357.push(("name".into(), e.get("name")?));
                    kw357.push(("color".into(), e.get("color")?));
                    fun358.call(args356, kw357)?
                };
            }
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("a")?);
                s.push(e.get("mouth")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // scene
    e.set("scene", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned363 = {
                let fun366 = e.get("bottle")?;
                let mut args364 = Vec::new();
                let mut kw365 = Vec::new();
                fun366.call(args364, kw365)?
            };
            let unpack367 = unpack(assigned363.clone(), 2)?;
            e.set("props", unpack367[0].clone())?;
            e.set("mouth", unpack367[1].clone())?;
            let assigned368 = {
                let fun371 = e.get("read_payload")?;
                let mut args369 = Vec::new();
                let mut kw370 = Vec::new();
                args369.push({
                    let fun374 = e.get("SOURCE")?.attr("with_suffix")?;
                    let mut args372 = Vec::new();
                    let mut kw373 = Vec::new();
                    args372.push(Val::Str(".step.mesh".into()));
                    fun374.call(args372, kw373)?
                });
                fun371.call(args369, kw370)?
            };
            e.set("current", assigned368.clone())?;
            if unary("not", e.get("current")?)?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let fun377 = e.get("ValueError")?;
                        let mut args375 = Vec::new();
                        let mut kw376 = Vec::new();
                        args375.push({
                            let mut str378 = String::new();
                            str378.push_str("No appliance payload at ");
                            str378.push_str(&format(&e.get("SOURCE")?, &String::new())?);
                            Val::Str(str378)
                        });
                        fun377.call(args375, kw376)?
                    })?
                );
            }
            let assigned379 = {
                let e = e.child();
                let out380 = Val::list(vec![]);
                for item381 in e.get("current")?.iter()? {
                    e.set("m", item381)?;
                    if {
                        let fun384 = e.get("visible")?;
                        let mut args382 = Vec::new();
                        let mut kw383 = Vec::new();
                        args382.push(e.get("m")?.get(Val::Str("name".into()))?);
                        fun384.call(args382, kw383)?
                    }
                    .truthy()?
                    {
                        out380.attr("append")?.call(vec![e.get("m")?], vec![])?;
                    }
                }
                out380
            };
            e.set("meshes", assigned379.clone())?;
            let assigned385 = {
                let fun388 = e.get("next")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push({
                    let e = e.child();
                    let out389 = Val::list(vec![]);
                    for item390 in e.get("meshes")?.iter()? {
                        e.set("m", item390)?;
                        if {
                            let v391 = e.get("m")?.get(Val::Str("name".into()))?;
                            let v392 = Val::Str("enclosure-back-top".into());
                            Val::Bool(compare("eq", v391.clone(), v392.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out389.attr("append")?.call(vec![e.get("m")?], vec![])?;
                        }
                    }
                    out389
                });
                fun388.call(args386, kw387)?
            };
            e.set("enclosure", assigned385.clone())?;
            let assigned393 = {
                let fun396 = e.get("next")?;
                let mut args394 = Vec::new();
                let mut kw395 = Vec::new();
                args394.push({
                    let e = e.child();
                    let out397 = Val::list(vec![]);
                    for item398 in e.get("meshes")?.iter()? {
                        e.set("m", item398)?;
                        if {
                            let v399 = e.get("m")?.get(Val::Str("name".into()))?;
                            let v400 = Val::Str("display-cover".into());
                            Val::Bool(compare("eq", v399.clone(), v400.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out397.attr("append")?.call(vec![e.get("m")?], vec![])?;
                        }
                    }
                    out397
                });
                fun396.call(args394, kw395)?
            };
            e.set("cover", assigned393.clone())?;
            let assigned401 = e.get("enclosure")?.get(Val::Str("color".into()))?;
            e.get("cover")?
                .set(Val::Str("color".into()), assigned401.clone())?;
            {
                let fun404 = e.get("meshes")?.attr("extend")?;
                let mut args402 = Vec::new();
                let mut kw403 = Vec::new();
                args402.push({
                    let fun407 = e.get("_mesh_payload")?.attr("from_assembly")?;
                    let mut args405 = Vec::new();
                    let mut kw406 = Vec::new();
                    args405.push(e.get("props")?);
                    fun407.call(args405, kw406)?
                });
                fun404.call(args402, kw403)?
            };
            // surface
            e.set("surface", {
                let params = vec![
                    ("name".into(), None, false),
                    ("positions".into(), None, false),
                    ("normals".into(), None, false),
                    ("uv".into(), None, false),
                    ("indices".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let fun410 = e.get("dict")?;
                        let mut args408 = Vec::new();
                        let mut kw409 = Vec::new();
                        kw409.push(("name".into(), e.get("name")?));
                        kw409.push(("color".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(1.0f64));
                            s.push(Val::Float(1.0f64));
                            Val::list(s)
                        }));
                        kw409.push(("pos".into(), {
                            let e = e.child();
                            let out411 = Val::list(vec![]);
                            for item412 in e.get("positions")?.iter()? {
                                e.set("row", item412)?;
                                for item413 in e.get("row")?.iter()? {
                                    e.set("v", item413)?;
                                    out411.attr("append")?.call(vec![e.get("v")?], vec![])?;
                                }
                            }
                            out411
                        }));
                        kw409.push(("nrm".into(), {
                            let e = e.child();
                            let out414 = Val::list(vec![]);
                            for item415 in e.get("normals")?.iter()? {
                                e.set("row", item415)?;
                                for item416 in e.get("row")?.iter()? {
                                    e.set("v", item416)?;
                                    out414.attr("append")?.call(vec![e.get("v")?], vec![])?;
                                }
                            }
                            out414
                        }));
                        kw409.push(("uv".into(), {
                            let e = e.child();
                            let out417 = Val::list(vec![]);
                            for item418 in e.get("uv")?.iter()? {
                                e.set("row", item418)?;
                                for item419 in e.get("row")?.iter()? {
                                    e.set("v", item419)?;
                                    out417.attr("append")?.call(vec![e.get("v")?], vec![])?;
                                }
                            }
                            out417
                        }));
                        kw409.push(("idx".into(), e.get("indices")?));
                        kw409.push(("fac".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(binary(
                                "sub",
                                binary(
                                    "floordiv",
                                    {
                                        let fun422 = e.get("len")?;
                                        let mut args420 = Vec::new();
                                        let mut kw421 = Vec::new();
                                        args420.push(e.get("indices")?);
                                        fun422.call(args420, kw421)?
                                    },
                                    Val::Int(3i64),
                                )?,
                                Val::Int(1i64),
                            )?);
                            Val::list(s)
                        }));
                        fun410.call(args408, kw409)?
                    });
                    Ok(Val::None)
                })
            })?;
            // transformed
            e.set("transformed", {
                let params = vec![
                    ("points".into(), None, false),
                    ("angle".into(), None, false),
                    ("origin".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned423 = {
                        let mut s = Vec::new();
                        s.push({
                            let fun426 = e.get("math")?.attr("cos")?;
                            let mut args424 = Vec::new();
                            let mut kw425 = Vec::new();
                            args424.push(e.get("angle")?);
                            fun426.call(args424, kw425)?
                        });
                        s.push({
                            let fun429 = e.get("math")?.attr("sin")?;
                            let mut args427 = Vec::new();
                            let mut kw428 = Vec::new();
                            args427.push(e.get("angle")?);
                            fun429.call(args427, kw428)?
                        });
                        Val::tuple(s)
                    };
                    let unpack430 = unpack(assigned423.clone(), 2)?;
                    e.set("c", unpack430[0].clone())?;
                    e.set("s", unpack430[1].clone())?;
                    return Ok({
                        let e = e.child();
                        let out431 = Val::list(vec![]);
                        for item432 in e.get("points")?.iter()? {
                            let unpack433 = unpack(item432, 3)?;
                            e.set("x", unpack433[0].clone())?;
                            e.set("y", unpack433[1].clone())?;
                            e.set("z", unpack433[2].clone())?;
                            out431.attr("append")?.call(
                                vec![{
                                    let mut s = Vec::new();
                                    s.push(binary(
                                        "add",
                                        e.get("x")?,
                                        e.get("origin")?.get(Val::Int(0i64))?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        binary(
                                            "sub",
                                            binary("mul", e.get("y")?, e.get("c")?)?,
                                            binary("mul", e.get("z")?, e.get("s")?)?,
                                        )?,
                                        e.get("origin")?.get(Val::Int(1i64))?,
                                    )?);
                                    s.push(binary(
                                        "add",
                                        binary(
                                            "add",
                                            binary("mul", e.get("y")?, e.get("s")?)?,
                                            binary("mul", e.get("z")?, e.get("c")?)?,
                                        )?,
                                        e.get("origin")?.get(Val::Int(2i64))?,
                                    )?);
                                    Val::list(s)
                                }],
                                vec![],
                            )?;
                        }
                        out431
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned434 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("SCREEN")?.get(Val::Str("width".into()))?,
                    Val::Int(2i64),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("SCREEN")?.get(Val::Str("height".into()))?,
                    Val::Int(2i64),
                )?);
                Val::tuple(s)
            };
            let unpack435 = unpack(assigned434.clone(), 2)?;
            e.set("w", unpack435[0].clone())?;
            e.set("h", unpack435[1].clone())?;
            let assigned436 = {
                let fun439 = e.get("math")?.attr("radians")?;
                let mut args437 = Vec::new();
                let mut kw438 = Vec::new();
                args437.push(e.get("SCREEN")?.get(Val::Str("angle_deg".into()))?);
                fun439.call(args437, kw438)?
            };
            e.set("angle", assigned436.clone())?;
            let assigned440 = {
                let fun443 = e.get("transformed")?;
                let mut args441 = Vec::new();
                let mut kw442 = Vec::new();
                args441.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", e.get("w")?)?);
                        s.push(unary("neg", e.get("h")?)?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("w")?);
                        s.push(unary("neg", e.get("h")?)?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", e.get("w")?)?);
                        s.push(e.get("h")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("w")?);
                        s.push(e.get("h")?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args441.push(e.get("angle")?);
                args441.push(e.get("SCREEN")?.get(Val::Str("origin".into()))?);
                fun443.call(args441, kw442)?
            };
            e.set("positions", assigned440.clone())?;
            let assigned444 = {
                let fun447 = e.get("transformed")?;
                let mut args445 = Vec::new();
                let mut kw446 = Vec::new();
                args445.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                args445.push(e.get("angle")?);
                args445.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                fun447.call(args445, kw446)?
            }
            .get(Val::Int(0i64))?;
            e.set("normal", assigned444.clone())?;
            {
                let fun450 = e.get("meshes")?.attr("append")?;
                let mut args448 = Vec::new();
                let mut kw449 = Vec::new();
                args448.push({
                    let fun453 = e.get("surface")?;
                    let mut args451 = Vec::new();
                    let mut kw452 = Vec::new();
                    args451.push(Val::Str("guide-fill-screen".into()));
                    args451.push(e.get("positions")?);
                    args451.push(binary(
                        "mul",
                        {
                            let mut s = Vec::new();
                            s.push(e.get("normal")?);
                            Val::list(s)
                        },
                        Val::Int(4i64),
                    )?);
                    args451.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(Val::Int(1i64));
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    args451.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(2i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(3i64));
                        s.push(Val::Int(2i64));
                        Val::list(s)
                    });
                    fun453.call(args451, kw452)?
                });
                fun450.call(args448, kw449)?
            };
            let assigned454 = {
                let fun457 = e.get("math")?.attr("radians")?;
                let mut args455 = Vec::new();
                let mut kw456 = Vec::new();
                args455.push(binary("sub", Val::Int(90i64), e.get("TIP")?)?);
                fun457.call(args455, kw456)?
            };
            e.set("tilt", assigned454.clone())?;
            let assigned458 = {
                let fun461 = e.get("math")?.attr("atan2")?;
                let mut args459 = Vec::new();
                let mut kw460 = Vec::new();
                args459.push(binary(
                    "add",
                    binary("mul", e.get("CAMERA")?.get(Val::Int(1i64))?, {
                        let fun464 = e.get("math")?.attr("cos")?;
                        let mut args462 = Vec::new();
                        let mut kw463 = Vec::new();
                        args462.push(e.get("tilt")?);
                        fun464.call(args462, kw463)?
                    })?,
                    binary("mul", e.get("CAMERA")?.get(Val::Int(2i64))?, {
                        let fun467 = e.get("math")?.attr("sin")?;
                        let mut args465 = Vec::new();
                        let mut kw466 = Vec::new();
                        args465.push(e.get("tilt")?);
                        fun467.call(args465, kw466)?
                    })?,
                )?);
                args459.push(e.get("CAMERA")?.get(Val::Int(0i64))?);
                fun461.call(args459, kw460)?
            };
            e.set("angle", assigned458.clone())?;
            let assigned468 = Val::Int(160i64);
            e.set("count", assigned468.clone())?;
            let assigned469 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                s.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                Val::tuple(s)
            };
            let unpack470 = unpack(assigned469.clone(), 4)?;
            e.set("positions", unpack470[0].clone())?;
            e.set("normals", unpack470[1].clone())?;
            e.set("uv", unpack470[2].clone())?;
            e.set("indices", unpack470[3].clone())?;
            for item471 in {
                let fun503 = e.get("range")?;
                let mut args501 = Vec::new();
                let mut kw502 = Vec::new();
                args501.push(Val::Int(2i64));
                fun503.call(args501, kw502)?
            }
            .iter()?
            {
                e.set("j", item471)?;
                let assigned472 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        Val::Int(72i64),
                        binary("mul", e.get("j")?, Val::Int(106i64))?,
                    )?);
                    s.push(binary(
                        "add",
                        Val::Float(32.25f64),
                        binary("mul", e.get("j")?, Val::Float(0.43f64))?,
                    )?);
                    Val::tuple(s)
                };
                let unpack473 = unpack(assigned472.clone(), 2)?;
                e.set("z", unpack473[0].clone())?;
                e.set("radius", unpack473[1].clone())?;
                for item474 in {
                    let fun500 = e.get("range")?;
                    let mut args498 = Vec::new();
                    let mut kw499 = Vec::new();
                    args498.push(binary("add", e.get("count")?, Val::Int(1i64))?);
                    fun500.call(args498, kw499)?
                }
                .iter()?
                {
                    e.set("i", item474)?;
                    let assigned475 = binary("truediv", e.get("i")?, e.get("count")?)?;
                    e.set("u", assigned475.clone())?;
                    let assigned476 = binary(
                        "add",
                        e.get("angle")?,
                        binary(
                            "mul",
                            binary("mul", Val::Int(2i64), e.get("math")?.attr("pi")?)?,
                            binary("sub", e.get("u")?, Val::Float(0.5f64))?,
                        )?,
                    )?;
                    e.set("theta", assigned476.clone())?;
                    {
                        let fun479 = e.get("positions")?.attr("append")?;
                        let mut args477 = Vec::new();
                        let mut kw478 = Vec::new();
                        args477.push({
                            let mut s = Vec::new();
                            s.push(binary("mul", e.get("radius")?, {
                                let fun482 = e.get("math")?.attr("cos")?;
                                let mut args480 = Vec::new();
                                let mut kw481 = Vec::new();
                                args480.push(e.get("theta")?);
                                fun482.call(args480, kw481)?
                            })?);
                            s.push(binary("mul", e.get("radius")?, {
                                let fun485 = e.get("math")?.attr("sin")?;
                                let mut args483 = Vec::new();
                                let mut kw484 = Vec::new();
                                args483.push(e.get("theta")?);
                                fun485.call(args483, kw484)?
                            })?);
                            s.push(e.get("z")?);
                            Val::tuple(s)
                        });
                        fun479.call(args477, kw478)?
                    };
                    {
                        let fun488 = e.get("normals")?.attr("append")?;
                        let mut args486 = Vec::new();
                        let mut kw487 = Vec::new();
                        args486.push({
                            let mut s = Vec::new();
                            s.push({
                                let fun491 = e.get("math")?.attr("cos")?;
                                let mut args489 = Vec::new();
                                let mut kw490 = Vec::new();
                                args489.push(e.get("theta")?);
                                fun491.call(args489, kw490)?
                            });
                            s.push({
                                let fun494 = e.get("math")?.attr("sin")?;
                                let mut args492 = Vec::new();
                                let mut kw493 = Vec::new();
                                args492.push(e.get("theta")?);
                                fun494.call(args492, kw493)?
                            });
                            s.push(Val::Int(0i64));
                            Val::tuple(s)
                        });
                        fun488.call(args486, kw487)?
                    };
                    {
                        let fun497 = e.get("uv")?.attr("append")?;
                        let mut args495 = Vec::new();
                        let mut kw496 = Vec::new();
                        args495.push({
                            let mut s = Vec::new();
                            s.push(binary("sub", Val::Int(1i64), e.get("u")?)?);
                            s.push(binary("sub", Val::Int(1i64), e.get("j")?)?);
                            Val::tuple(s)
                        });
                        fun497.call(args495, kw496)?
                    };
                }
            }
            for item504 in {
                let fun510 = e.get("range")?;
                let mut args508 = Vec::new();
                let mut kw509 = Vec::new();
                args508.push(e.get("count")?);
                fun510.call(args508, kw509)?
            }
            .iter()?
            {
                e.set("i", item504)?;
                {
                    let fun507 = e.get("indices")?.attr("extend")?;
                    let mut args505 = Vec::new();
                    let mut kw506 = Vec::new();
                    args505.push({
                        let mut s = Vec::new();
                        s.push(e.get("i")?);
                        s.push(binary("add", e.get("i")?, Val::Int(1i64))?);
                        s.push(binary(
                            "add",
                            binary("add", e.get("count")?, Val::Int(1i64))?,
                            e.get("i")?,
                        )?);
                        s.push(binary("add", e.get("i")?, Val::Int(1i64))?);
                        s.push(binary(
                            "add",
                            binary("add", e.get("count")?, Val::Int(2i64))?,
                            e.get("i")?,
                        )?);
                        s.push(binary(
                            "add",
                            binary("add", e.get("count")?, Val::Int(1i64))?,
                            e.get("i")?,
                        )?);
                        Val::tuple(s)
                    });
                    fun507.call(args505, kw506)?
                };
            }
            let assigned511 = {
                let fun514 = e.get("transformed")?;
                let mut args512 = Vec::new();
                let mut kw513 = Vec::new();
                args512.push(e.get("positions")?);
                args512.push(e.get("tilt")?);
                args512.push(e.get("mouth")?);
                fun514.call(args512, kw513)?
            };
            e.set("positions", assigned511.clone())?;
            let assigned515 = {
                let fun518 = e.get("transformed")?;
                let mut args516 = Vec::new();
                let mut kw517 = Vec::new();
                args516.push(e.get("normals")?);
                args516.push(e.get("tilt")?);
                args516.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                fun518.call(args516, kw517)?
            };
            e.set("normals", assigned515.clone())?;
            {
                let fun521 = e.get("meshes")?.attr("append")?;
                let mut args519 = Vec::new();
                let mut kw520 = Vec::new();
                args519.push({
                    let fun524 = e.get("surface")?;
                    let mut args522 = Vec::new();
                    let mut kw523 = Vec::new();
                    args522.push(Val::Str("bottle-label".into()));
                    args522.push(e.get("positions")?);
                    args522.push(e.get("normals")?);
                    args522.push(e.get("uv")?);
                    args522.push(e.get("indices")?);
                    fun524.call(args522, kw523)?
                });
                fun521.call(args519, kw520)?
            };
            let assigned525 = binary("truediv", e.get("OUT")?, Val::Str("fill.step.mesh".into()))?;
            e.set("path", assigned525.clone())?;
            {
                let fun528 = e.get("_mesh_payload")?.attr("write")?;
                let mut args526 = Vec::new();
                let mut kw527 = Vec::new();
                args526.push(e.get("meshes")?);
                args526.push(e.get("path")?);
                fun528.call(args526, kw527)?
            };
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("path")?);
                s.push(e.get("mouth")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // label
    e.set("label",{let params=vec![("kind".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned529={let fun532=e.get("TTFont")?;let mut args530=Vec::new();let mut kw531=Vec::new();args530.push(binary("truediv",e.get("DIR")?,Val::Str("fonts/Plex-Bold.ttf".into()))?);fun532.call(args530,kw531)?};e.set("font",assigned529.clone())?;
let assigned533={let fun536=e.get("font")?.attr("getGlyphSet")?;let mut args534=Vec::new();let mut kw535=Vec::new();fun536.call(args534,kw535)?};e.set("glyphs",assigned533.clone())?;
let assigned537={let fun540=e.get("font")?.attr("getBestCmap")?;let mut args538=Vec::new();let mut kw539=Vec::new();fun540.call(args538,kw539)?};e.set("mapping",assigned537.clone())?;
// text
e.set("text",{let params=vec![("value".into(),None,false),("y".into(),None,false),("size".into(),None,false),("color".into(),Some(Val::Str("#101828".into())),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned541={let e=e.child();let out542=Val::list(vec![]);for item543 in e.get("value")?.iter()? {e.set("c",item543)?;out542.attr("append")?.call(vec![e.get("font")?.get(Val::Str("hmtx".into()))?.get(e.get("mapping")?.get({let fun546=e.get("ord")?;let mut args544=Vec::new();let mut kw545=Vec::new();args544.push(e.get("c")?);fun546.call(args544,kw545)?})?)?.get(Val::Int(0i64))?],vec![])?;}out542};e.set("advances",assigned541.clone())?;
let assigned547=binary("truediv",e.get("size")?,e.get("font")?.get(Val::Str("head".into()))?.attr("unitsPerEm")?)?;e.set("scale",assigned547.clone())?;
let assigned548={let mut s=Vec::new();Val::list(s)};e.set("pieces",assigned548.clone())?;
let assigned549=binary("truediv",unary("neg",{let fun552=e.get("sum")?;let mut args550=Vec::new();let mut kw551=Vec::new();args550.push(e.get("advances")?);fun552.call(args550,kw551)?})?,Val::Int(2i64))?;e.set("x",assigned549.clone())?;
for item553 in {let fun573=e.get("zip")?;let mut args571=Vec::new();let mut kw572=Vec::new();args571.push(e.get("value")?);args571.push(e.get("advances")?);fun573.call(args571,kw572)?}.iter()? {
let unpack574=unpack(item553,2)?;e.set("char",unpack574[0].clone())?;e.set("advance",unpack574[1].clone())?;let assigned554={let fun557=e.get("SVGPathPen")?;let mut args555=Vec::new();let mut kw556=Vec::new();args555.push(e.get("glyphs")?);fun557.call(args555,kw556)?};e.set("pen",assigned554.clone())?;
{let fun560=e.get("glyphs")?.get(e.get("mapping")?.get({let fun563=e.get("ord")?;let mut args561=Vec::new();let mut kw562=Vec::new();args561.push(e.get("char")?);fun563.call(args561,kw562)?})?)?.attr("draw")?;let mut args558=Vec::new();let mut kw559=Vec::new();args558.push(e.get("pen")?);fun560.call(args558,kw559)?};
{let fun566=e.get("pieces")?.attr("append")?;let mut args564=Vec::new();let mut kw565=Vec::new();args564.push({let mut str567=String::new();str567.push_str("<path transform=\"translate(");str567.push_str(&format(&e.get("x")?,&String::new())?);str567.push_str(" 0)\" d=\"");str567.push_str(&format(&{let fun570=e.get("pen")?.attr("getCommands")?;let mut args568=Vec::new();let mut kw569=Vec::new();fun570.call(args568,kw569)?},&String::new())?);str567.push_str("\"/>");Val::Str(str567)});fun566.call(args564,kw565)?};
e.set("x",binary("add",e.get("x")?,e.get("advance")?)?)?;
}
return Ok(binary("add",binary("add",{let mut str575=String::new();str575.push_str("<g fill=\"");str575.push_str(&format(&e.get("color")?,&String::new())?);str575.push_str("\" transform=\"translate(600 ");str575.push_str(&format(&e.get("y")?,&String::new())?);str575.push_str(") scale(");str575.push_str(&format(&e.get("scale")?,&String::new())?);str575.push_str(" ");str575.push_str(&format(&unary("neg",e.get("scale")?)?,&String::new())?);str575.push_str(")\">");Val::Str(str575)},{let fun578=Val::Str("".into()).attr("join")?;let mut args576=Vec::new();let mut kw577=Vec::new();args576.push(e.get("pieces")?);fun578.call(args576,kw577)?})?,Val::Str("</g>".into()))?);
Ok(Val::None)})})?;
if {let v579=e.get("kind")?;let v580=Val::Str("pepsi".into());Val::Bool(compare("eq",v579.clone(),v580.clone())?.truthy()?)}.truthy()? {
let assigned581={let mut s=Vec::new();s.push(Val::Str("<rect width=\"1200\" height=\"560\" fill=\"#0755d6\"/>".into()));s.push(Val::Str("<defs><pattern id=\"dots\" width=\"22\" height=\"22\" patternUnits=\"userSpaceOnUse\"><circle cx=\"4\" cy=\"4\" r=\"2\" fill=\"#fff\" opacity=\".12\"/></pattern><clipPath id=\"globe\"><circle cx=\"600\" cy=\"306\" r=\"177\"/></clipPath></defs>".into()));s.push(Val::Str("<rect width=\"1200\" height=\"560\" fill=\"url(#dots)\"/>".into()));s.push(Val::Str("<ellipse cx=\"600\" cy=\"0\" rx=\"214\" ry=\"120\" fill=\"#fff\"/>".into()));s.push({let fun584=e.get("text")?;let mut args582=Vec::new();let mut kw583=Vec::new();args582.push(Val::Str("sodastream".into()));args582.push(Val::Int(48i64));args582.push(Val::Int(35i64));args582.push(Val::Str("#13386e".into()));fun584.call(args582,kw583)?});s.push({let fun587=e.get("text")?;let mut args585=Vec::new();let mut kw586=Vec::new();args585.push(Val::Str("drink mix".into()));args585.push(Val::Int(85i64));args585.push(Val::Int(24i64));args585.push(Val::Str("#13386e".into()));fun587.call(args585,kw586)?});s.push(Val::Str("<circle cx=\"600\" cy=\"306\" r=\"188\" fill=\"#fff\"/><circle cx=\"600\" cy=\"306\" r=\"181\" fill=\"#141414\"/>".into()));s.push(Val::Str("<g clip-path=\"url(#globe)\"><rect x=\"414\" y=\"120\" width=\"372\" height=\"372\" fill=\"#043dbd\"/><path d=\"M414 265 L414 120 H786 V265 Q610 223 414 265\" fill=\"#f32139\"/><path d=\"M414 265 Q610 223 786 265 V355 Q610 393 414 355 Z\" fill=\"#fff\"/></g>".into()));s.push({let fun590=e.get("text")?;let mut args588=Vec::new();let mut kw589=Vec::new();args588.push(Val::Str("PEPSI".into()));args588.push(Val::Int(338i64));args588.push(Val::Int(80i64));args588.push(Val::Str("#080808".into()));fun590.call(args588,kw589)?});s.push({let fun593=e.get("text")?;let mut args591=Vec::new();let mut kw592=Vec::new();args591.push(Val::Str("440 mL".into()));args591.push(Val::Int(532i64));args591.push(Val::Int(29i64));args591.push(Val::Str("#fff".into()));fun593.call(args591,kw592)?});Val::list(s)};e.set("pieces",assigned581.clone())?;
}else{
let assigned594={let mut s=Vec::new();s.push(Val::Str("<rect width=\"1200\" height=\"560\" fill=\"#f2f0e5\"/>".into()));s.push(Val::Str("<rect y=\"18\" width=\"1200\" height=\"54\" fill=\"#173581\"/>".into()));s.push({let fun597=e.get("text")?;let mut args595=Vec::new();let mut kw596=Vec::new();args595.push(Val::Str("DRINK MIX".into()));args595.push(Val::Int(59i64));args595.push(Val::Int(29i64));args595.push(Val::Str("#fff".into()));fun597.call(args595,kw596)?});s.push(Val::Str("<path d=\"M0 118 H1200 M0 462 H1200\" stroke=\"#c8c8bf\" stroke-width=\"3\"/>".into()));s.push({let fun600=e.get("text")?;let mut args598=Vec::new();let mut kw599=Vec::new();args598.push(Val::Str("COLA".into()));args598.push(Val::Int(303i64));args598.push(Val::Int(112i64));args598.push(Val::Str("#153383".into()));fun600.call(args598,kw599)?});s.push({let fun603=e.get("text")?;let mut args601=Vec::new();let mut kw602=Vec::new();args601.push(Val::Str("CONCENTRATE".into()));args601.push(Val::Int(365i64));args601.push(Val::Int(40i64));args601.push(Val::Str("#153383".into()));fun603.call(args601,kw602)?});s.push({let fun606=e.get("text")?;let mut args604=Vec::new();let mut kw605=Vec::new();args604.push(Val::Str("SodaStream-compatible".into()));args604.push(Val::Int(429i64));args604.push(Val::Int(26i64));args604.push(Val::Str("#505661".into()));fun606.call(args604,kw605)?});s.push({let fun609=e.get("text")?;let mut args607=Vec::new();let mut kw608=Vec::new();args607.push(Val::Str("440 mL".into()));args607.push(Val::Int(522i64));args607.push(Val::Int(31i64));args607.push(Val::Str("#153383".into()));fun609.call(args607,kw608)?});Val::list(s)};e.set("pieces",assigned594.clone())?;
}
let assigned610=binary("add",binary("add",Val::Str("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"1200\" height=\"560\">".into()),{let fun613=Val::Str("".into()).attr("join")?;let mut args611=Vec::new();let mut kw612=Vec::new();args611.push(e.get("pieces")?);fun613.call(args611,kw612)?})?,Val::Str("</svg>".into()))?;e.set("svg",assigned610.clone())?;
{let fun616=binary("truediv",e.get("OUT")?,{let mut str617=String::new();str617.push_str("label-");str617.push_str(&format(&e.get("kind")?,&String::new())?);str617.push_str(".svg");Val::Str(str617)})?.attr("write_text")?;let mut args614=Vec::new();let mut kw615=Vec::new();args614.push(e.get("svg")?);fun616.call(args614,kw615)?};
let assigned618=binary("truediv",e.get("OUT")?,{let mut str619=String::new();str619.push_str("label-");str619.push_str(&format(&e.get("kind")?,&String::new())?);str619.push_str(".png");Val::Str(str619)})?;e.set("target",assigned618.clone())?;
{let fun622=e.get("cairosvg")?.attr("svg2png")?;let mut args620=Vec::new();let mut kw621=Vec::new();kw621.push(("bytestring".into(),{let fun625=e.get("svg")?.attr("encode")?;let mut args623=Vec::new();let mut kw624=Vec::new();fun625.call(args623,kw624)?}));kw621.push(("write_to".into(),{let fun628=e.get("str")?;let mut args626=Vec::new();let mut kw627=Vec::new();args626.push(e.get("target")?);fun628.call(args626,kw627)?}));fun622.call(args620,kw621)?};
return Ok({let fun631=e.get("str")?;let mut args629=Vec::new();let mut kw630=Vec::new();args629.push(e.get("target")?);fun631.call(args629,kw630)?});
Ok(Val::None)})})?;
    // materials
    e.set("materials", {
        let params = vec![("label".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push({
                    let fun634 = e.get("dict")?;
                    let mut args632 = Vec::new();
                    let mut kw633 = Vec::new();
                    kw633.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("guide-fill-screen".into()));
                        Val::list(s)
                    }));
                    kw633.push(("texture".into(), {
                        let fun637 = e.get("str")?;
                        let mut args635 = Vec::new();
                        let mut kw636 = Vec::new();
                        args635.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/fill-screen.png".into()),
                        )?);
                        fun637.call(args635, kw636)?
                    }));
                    kw633.push(("unlit".into(), Val::Bool(true)));
                    kw633.push(("tone_mapped".into(), Val::Bool(false)));
                    kw633.push(("side".into(), Val::Str("front".into())));
                    fun634.call(args632, kw633)?
                });
                s.push({
                    let fun640 = e.get("dict")?;
                    let mut args638 = Vec::new();
                    let mut kw639 = Vec::new();
                    kw639.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("bottle-pet".into()));
                        Val::list(s)
                    }));
                    kw639.push(("color".into(), Val::Str("#dce9ee".into())));
                    kw639.push(("opacity".into(), Val::Float(0.065f64)));
                    kw639.push(("depth_write".into(), Val::Bool(false)));
                    kw639.push(("roughness".into(), Val::Float(0.18f64)));
                    kw639.push(("metalness".into(), Val::Float(0.02f64)));
                    kw639.push(("clearcoat".into(), Val::Float(0.5f64)));
                    kw639.push(("clearcoat_roughness".into(), Val::Float(0.18f64)));
                    kw639.push(("side".into(), Val::Str("front".into())));
                    kw639.push(("order".into(), Val::Int(5i64)));
                    fun640.call(args638, kw639)?
                });
                s.push({
                    let fun643 = e.get("dict")?;
                    let mut args641 = Vec::new();
                    let mut kw642 = Vec::new();
                    kw642.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("bottle-concentrate".into()));
                        Val::list(s)
                    }));
                    kw642.push(("color".into(), Val::Str("#361b0d".into())));
                    kw642.push(("roughness".into(), Val::Float(0.62f64)));
                    kw642.push(("metalness".into(), Val::Int(0i64)));
                    kw642.push(("side".into(), Val::Str("front".into())));
                    fun643.call(args641, kw642)?
                });
                s.push({
                    let fun646 = e.get("dict")?;
                    let mut args644 = Vec::new();
                    let mut kw645 = Vec::new();
                    kw645.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("bottle-ring-*".into()));
                        Val::list(s)
                    }));
                    kw645.push(("color".into(), Val::Str("#9daeb4".into())));
                    kw645.push(("opacity".into(), Val::Float(0.63f64)));
                    kw645.push(("roughness".into(), Val::Float(0.18f64)));
                    kw645.push(("metalness".into(), Val::Float(0.08f64)));
                    kw645.push(("depth_write".into(), Val::Bool(false)));
                    kw645.push(("side".into(), Val::Str("front".into())));
                    kw645.push(("order".into(), Val::Int(6i64)));
                    fun646.call(args644, kw645)?
                });
                s.push({
                    let fun649 = e.get("dict")?;
                    let mut args647 = Vec::new();
                    let mut kw648 = Vec::new();
                    kw648.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("bottle-grip-*".into()));
                        s.push(Val::Str("bottle-collar".into()));
                        Val::list(s)
                    }));
                    kw648.push(("color".into(), Val::Str("#17191a".into())));
                    kw648.push(("roughness".into(), Val::Float(0.42f64)));
                    kw648.push(("metalness".into(), Val::Int(0i64)));
                    kw648.push(("side".into(), Val::Str("front".into())));
                    fun649.call(args647, kw648)?
                });
                s.push({
                    let fun652 = e.get("dict")?;
                    let mut args650 = Vec::new();
                    let mut kw651 = Vec::new();
                    kw651.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("display/2".into()));
                        Val::list(s)
                    }));
                    kw651.push(("color".into(), Val::Str("#11151a".into())));
                    kw651.push(("unlit".into(), Val::Bool(true)));
                    kw651.push(("side".into(), Val::Str("front".into())));
                    fun652.call(args650, kw651)?
                });
                s.push({
                    let fun655 = e.get("dict")?;
                    let mut args653 = Vec::new();
                    let mut kw654 = Vec::new();
                    kw654.push(("names".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("bottle-label".into()));
                        Val::list(s)
                    }));
                    kw654.push(("texture".into(), e.get("label")?));
                    kw654.push(("roughness".into(), Val::Float(0.62f64)));
                    kw654.push(("metalness".into(), Val::Float(0.015f64)));
                    kw654.push(("side".into(), Val::Str("front".into())));
                    fun655.call(args653, kw654)?
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
            let assigned656 = {
                let fun659 = e.get("argparse")?.attr("ArgumentParser")?;
                let mut args657 = Vec::new();
                let mut kw658 = Vec::new();
                kw658.push(("description".into(), e.get("__doc__")?));
                fun659.call(args657, kw658)?
            };
            e.set("parser", assigned656.clone())?;
            {
                let fun662 = e.get("parser")?.attr("add_argument")?;
                let mut args660 = Vec::new();
                let mut kw661 = Vec::new();
                args660.push(Val::Str("--label".into()));
                kw661.push(("choices".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Str("neutral".into()));
                    s.push(Val::Str("pepsi".into()));
                    Val::list(s)
                }));
                kw661.push(("default".into(), Val::Str("neutral".into())));
                fun662.call(args660, kw661)?
            };
            {
                let fun665 = e.get("parser")?.attr("add_argument")?;
                let mut args663 = Vec::new();
                let mut kw664 = Vec::new();
                args663.push(Val::Str("--compare".into()));
                kw664.push(("action".into(), Val::Str("store_true".into())));
                fun665.call(args663, kw664)?
            };
            {
                let fun668 = e.get("parser")?.attr("add_argument")?;
                let mut args666 = Vec::new();
                let mut kw667 = Vec::new();
                args666.push(Val::Str("--scale".into()));
                kw667.push(("type".into(), e.get("float")?));
                kw667.push(("default".into(), Val::Int(1i64)));
                kw667.push((
                    "help".into(),
                    Val::Str("render scale with the same camera and scene coordinates".into()),
                ));
                fun668.call(args666, kw667)?
            };
            {
                let fun671 = e.get("parser")?.attr("add_argument")?;
                let mut args669 = Vec::new();
                let mut kw670 = Vec::new();
                args669.push(Val::Str("--publish".into()));
                kw670.push(("action".into(), Val::Str("store_true".into())));
                kw670.push((
                    "help".into(),
                    Val::Str(
                        "copy registered reference artwork or print artwork to the install guide"
                            .into(),
                    ),
                ));
                fun671.call(args669, kw670)?
            };
            let assigned672 = {
                let fun675 = e.get("parser")?.attr("parse_args")?;
                let mut args673 = Vec::new();
                let mut kw674 = Vec::new();
                fun675.call(args673, kw674)?
            };
            e.set("args", assigned672.clone())?;
            {
                let fun678 = e.get("OUT")?.attr("mkdir")?;
                let mut args676 = Vec::new();
                let mut kw677 = Vec::new();
                kw677.push(("parents".into(), Val::Bool(true)));
                kw677.push(("exist_ok".into(), Val::Bool(true)));
                fun678.call(args676, kw677)?
            };
            let assigned679 = {
                let fun682 = e.get("scene")?;
                let mut args680 = Vec::new();
                let mut kw681 = Vec::new();
                fun682.call(args680, kw681)?
            };
            let unpack683 = unpack(assigned679.clone(), 2)?;
            e.set("payload", unpack683[0].clone())?;
            e.set("mouth", unpack683[1].clone())?;
            let assigned684 = {
                let mut s = Vec::new();
                Val::list(s)
            };
            e.set("jobs", assigned684.clone())?;
            for item685 in if e.get("args")?.attr("compare")?.truthy()? {
                {
                    let mut s = Vec::new();
                    s.push(Val::Str("neutral".into()));
                    s.push(Val::Str("pepsi".into()));
                    Val::list(s)
                }
            } else {
                {
                    let mut s = Vec::new();
                    s.push(e.get("args")?.attr("label")?);
                    Val::list(s)
                }
            }
            .iter()?
            {
                e.set("kind", item685)?;
                {
                    let fun688 = e.get("jobs")?.attr("append")?;
                    let mut args686 = Vec::new();
                    let mut kw687 = Vec::new();
                    args686.push({
                        let fun691 = e.get("dict")?;
                        let mut args689 = Vec::new();
                        let mut kw690 = Vec::new();
                        kw690.push(("payload".into(), {
                            let fun694 = e.get("str")?;
                            let mut args692 = Vec::new();
                            let mut kw693 = Vec::new();
                            args692.push(e.get("payload")?);
                            fun694.call(args692, kw693)?
                        }));
                        kw690.push(("out".into(), {
                            let fun697 = e.get("str")?;
                            let mut args695 = Vec::new();
                            let mut kw696 = Vec::new();
                            args695.push(binary("truediv", e.get("OUT")?, {
                                let mut str698 = String::new();
                                str698.push_str("fill-");
                                str698.push_str(&format(&e.get("kind")?, &String::new())?);
                                str698.push_str(".png");
                                Val::Str(str698)
                            })?);
                            fun697.call(args695, kw696)?
                        }));
                        kw690.push(("materials".into(), {
                            let fun701 = e.get("materials")?;
                            let mut args699 = Vec::new();
                            let mut kw700 = Vec::new();
                            args699.push({
                                let fun704 = e.get("label")?;
                                let mut args702 = Vec::new();
                                let mut kw703 = Vec::new();
                                args702.push(e.get("kind")?);
                                fun704.call(args702, kw703)?
                            });
                            fun701.call(args699, kw700)?
                        }));
                        kw690.push(("hide".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Str("funnel-cover".into()));
                            Val::list(s)
                        }));
                        kw690.push(("cam".into(), e.get("CAMERA")?));
                        kw690.push(("target".into(), e.get("TARGET")?));
                        kw690.push(("span".into(), e.get("SPAN")?));
                        kw690.push(("size".into(), Val::Str("1600x1500".into())));
                        kw690.push(("up".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(0i64));
                            s.push(Val::Int(1i64));
                            Val::tuple(s)
                        }));
                        kw690.push(("bg".into(), Val::Str("#ffffff".into())));
                        kw690.push(("transparent".into(), Val::Bool(true)));
                        kw690.push(("solid".into(), Val::Bool(true)));
                        kw690.push(("ortho".into(), Val::Bool(true)));
                        kw690.push(("trim".into(), Val::Bool(false)));
                        kw690.push(("ground".into(), Val::Bool(false)));
                        kw690.push(("fog".into(), Val::Bool(false)));
                        fun691.call(args689, kw690)?
                    });
                    fun688.call(args686, kw687)?
                };
                {
                    let fun707 = e.get("jobs")?.attr("append")?;
                    let mut args705 = Vec::new();
                    let mut kw706 = Vec::new();
                    args705.push({
                        let fun710 = e.get("dict")?;
                        let mut args708 = Vec::new();
                        let mut kw709 = Vec::new();
                        args708.push(e.get("jobs")?.get(unary("neg", Val::Int(1i64))?)?);
                        kw709.push(("out".into(), {
                            let fun713 = e.get("str")?;
                            let mut args711 = Vec::new();
                            let mut kw712 = Vec::new();
                            args711.push(binary("truediv", e.get("OUT")?, {
                                let mut str714 = String::new();
                                str714.push_str("bottle-");
                                str714.push_str(&format(&e.get("kind")?, &String::new())?);
                                str714.push_str(".png");
                                Val::Str(str714)
                            })?);
                            fun713.call(args711, kw712)?
                        }));
                        kw709.push(("only".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Str("bottle-*".into()));
                            Val::list(s)
                        }));
                        kw709.push(("context".into(), Val::Str("hide".into())));
                        kw709.push(("target".into(), {
                            let e = e.child();
                            let out715 = Val::list(vec![]);
                            for item716 in {
                                let fun719 = e.get("zip")?;
                                let mut args717 = Vec::new();
                                let mut kw718 = Vec::new();
                                args717.push(e.get("mouth")?);
                                args717.push(e.get("AXIS")?);
                                fun719.call(args717, kw718)?
                            }
                            .iter()?
                            {
                                let unpack720 = unpack(item716, 2)?;
                                e.set("m", unpack720[0].clone())?;
                                e.set("a", unpack720[1].clone())?;
                                out715.attr("append")?.call(
                                    vec![binary(
                                        "add",
                                        e.get("m")?,
                                        binary("mul", Val::Int(102i64), e.get("a")?)?,
                                    )?],
                                    vec![],
                                )?;
                            }
                            out715
                        }));
                        kw709.push(("span".into(), Val::Int(114i64)));
                        kw709.push(("size".into(), Val::Str("1350x900".into())));
                        kw709.push(("trim".into(), Val::Bool(true)));
                        fun710.call(args708, kw709)?
                    });
                    fun707.call(args705, kw706)?
                };
            }
            {
                let fun723 = e.get("jobs")?.attr("append")?;
                let mut args721 = Vec::new();
                let mut kw722 = Vec::new();
                args721.push({
                    let fun726 = e.get("dict")?;
                    let mut args724 = Vec::new();
                    let mut kw725 = Vec::new();
                    args724.push(e.get("jobs")?.get(Val::Int(0i64))?);
                    kw725.push(("out".into(), {
                        let fun729 = e.get("str")?;
                        let mut args727 = Vec::new();
                        let mut kw728 = Vec::new();
                        args727.push(binary(
                            "truediv",
                            e.get("OUT")?,
                            Val::Str("fill-screen-framed.png".into()),
                        )?);
                        fun729.call(args727, kw728)?
                    }));
                    kw725.push(("only".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("display".into()));
                        s.push(Val::Str("display-cover".into()));
                        s.push(Val::Str("display-gasket".into()));
                        s.push(Val::Str("guide-fill-screen".into()));
                        Val::list(s)
                    }));
                    kw725.push(("context".into(), Val::Str("hide".into())));
                    kw725.push((
                        "cam".into(),
                        e.get("DISPLAY_PROFILE")?.get(Val::Str("normal".into()))?,
                    ));
                    kw725.push((
                        "target".into(),
                        e.get("SCREEN")?.get(Val::Str("origin".into()))?,
                    ));
                    kw725.push(("span".into(), Val::Int(46i64)));
                    kw725.push(("size".into(), Val::Str("1800x1020".into())));
                    kw725.push(("trim".into(), Val::Bool(true)));
                    fun726.call(args724, kw725)?
                });
                fun723.call(args721, kw722)?
            };
            {
                let fun732 = e.get("jobs")?.attr("append")?;
                let mut args730 = Vec::new();
                let mut kw731 = Vec::new();
                args730.push({
                    let fun735 = e.get("dict")?;
                    let mut args733 = Vec::new();
                    let mut kw734 = Vec::new();
                    args733.push(e.get("jobs")?.get(Val::Int(0i64))?);
                    kw734.push(("out".into(), {
                        let fun738 = e.get("str")?;
                        let mut args736 = Vec::new();
                        let mut kw737 = Vec::new();
                        args736.push(binary(
                            "truediv",
                            e.get("OUT")?,
                            Val::Str("fill-closed.png".into()),
                        )?);
                        fun738.call(args736, kw737)?
                    }));
                    kw734.push(("hide".into(), {
                        let mut s = Vec::new();
                        s.push(Val::Str("bottle-*".into()));
                        Val::list(s)
                    }));
                    fun735.call(args733, kw734)?
                });
                fun732.call(args730, kw731)?
            };
            if {
                let v739 = e.get("args")?.attr("scale")?;
                let v740 = Val::Int(0i64);
                Val::Bool(compare("le", v739.clone(), v740.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun743 = e.get("parser")?.attr("error")?;
                    let mut args741 = Vec::new();
                    let mut kw742 = Vec::new();
                    args741.push(Val::Str("--scale must be positive".into()));
                    fun743.call(args741, kw742)?
                };
            }
            for item744 in e.get("jobs")?.iter()? {
                e.set("job", item744)?;
                let assigned745 = {
                    let fun748 = Val::Str("x".into()).attr("join")?;
                    let mut args746 = Vec::new();
                    let mut kw747 = Vec::new();
                    args746.push({
                        let e = e.child();
                        let out749 = Val::list(vec![]);
                        for item750 in {
                            let fun753 =
                                e.get("job")?.get(Val::Str("size".into()))?.attr("split")?;
                            let mut args751 = Vec::new();
                            let mut kw752 = Vec::new();
                            args751.push(Val::Str("x".into()));
                            fun753.call(args751, kw752)?
                        }
                        .iter()?
                        {
                            e.set("value", item750)?;
                            out749.attr("append")?.call(
                                vec![{
                                    let fun756 = e.get("str")?;
                                    let mut args754 = Vec::new();
                                    let mut kw755 = Vec::new();
                                    args754.push({
                                        let fun759 = e.get("round")?;
                                        let mut args757 = Vec::new();
                                        let mut kw758 = Vec::new();
                                        args757.push(binary(
                                            "mul",
                                            {
                                                let fun762 = e.get("int")?;
                                                let mut args760 = Vec::new();
                                                let mut kw761 = Vec::new();
                                                args760.push(e.get("value")?);
                                                fun762.call(args760, kw761)?
                                            },
                                            e.get("args")?.attr("scale")?,
                                        )?);
                                        fun759.call(args757, kw758)?
                                    });
                                    fun756.call(args754, kw755)?
                                }],
                                vec![],
                            )?;
                        }
                        out749
                    });
                    fun748.call(args746, kw747)?
                };
                e.get("job")?
                    .set(Val::Str("size".into()), assigned745.clone())?;
            }
            let assigned763 = binary("truediv", e.get("OUT")?, Val::Str("jobs.json".into()))?;
            e.set("manifest", assigned763.clone())?;
            {
                let fun766 = e.get("manifest")?.attr("write_text")?;
                let mut args764 = Vec::new();
                let mut kw765 = Vec::new();
                args764.push(binary(
                    "add",
                    {
                        let fun769 = e.get("json")?.attr("dumps")?;
                        let mut args767 = Vec::new();
                        let mut kw768 = Vec::new();
                        args767.push(e.get("jobs")?);
                        kw768.push(("indent".into(), Val::Int(2i64)));
                        fun769.call(args767, kw768)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun766.call(args764, kw765)?
            };
            {
                let fun772 = e.get("_hsm_render")?.attr("render")?;
                let mut args770 = Vec::new();
                let mut kw771 = Vec::new();
                args770.push(e.get("jobs")?);
                fun772.call(args770, kw771)?
            };
            if e.get("args")?.attr("publish")?.truthy()? {
                {
                    let fun775 = e.get("publish")?;
                    let mut args773 = Vec::new();
                    let mut kw774 = Vec::new();
                    args773.push(e.get("args")?);
                    args773.push(e.get("mouth")?);
                    fun775.call(args773, kw774)?
                };
            }
            for item776 in e.get("jobs")?.iter()? {
                e.set("job", item776)?;
                {
                    let fun779 = e.get("print")?;
                    let mut args777 = Vec::new();
                    let mut kw778 = Vec::new();
                    args777.push(e.get("job")?.get(Val::Str("out".into()))?);
                    fun779.call(args777, kw778)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // publish
    e.set("publish", {
        let params = vec![("args".into(), None, false), ("mouth".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned780 = binary("truediv", e.get("OUT")?, {
                let mut str781 = String::new();
                str781.push_str("fill-");
                str781.push_str(&format(&e.get("args")?.attr("label")?, &String::new())?);
                str781.push_str(".png");
                Val::Str(str781)
            })?;
            e.set("fill", assigned780.clone())?;
            let assigned782 = binary(
                "truediv",
                e.get("OUT")?,
                Val::Str("fill-screen-framed.png".into()),
            )?;
            e.set("frame", assigned782.clone())?;
            let assigned783 = binary("truediv", e.get("OUT")?, Val::Str("fill-closed.png".into()))?;
            e.set("closed", assigned783.clone())?;
            if {
                let v784 = e.get("args")?.attr("scale")?;
                let v785 = Val::Int(1i64);
                Val::Bool(compare("eq", v784.clone(), v785.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned786 = {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("fill")?);
                        s.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/reference/fill-ready.png".into()),
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("frame")?);
                        s.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/reference/fill-screen-framed.png".into()),
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("closed")?);
                        s.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/reference/fill-closed.png".into()),
                        )?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                };
                e.set("targets", assigned786.clone())?;
                for item787 in e.get("targets")?.iter()? {
                    let unpack794 = unpack(item787, 2)?;
                    e.set("source", unpack794[0].clone())?;
                    e.set("target", unpack794[1].clone())?;
                    {
                        let fun790 = e.get("target")?.attr("parent")?.attr("mkdir")?;
                        let mut args788 = Vec::new();
                        let mut kw789 = Vec::new();
                        kw789.push(("parents".into(), Val::Bool(true)));
                        kw789.push(("exist_ok".into(), Val::Bool(true)));
                        fun790.call(args788, kw789)?
                    };
                    {
                        let fun793 = e.get("shutil")?.attr("copy2")?;
                        let mut args791 = Vec::new();
                        let mut kw792 = Vec::new();
                        args791.push(e.get("source")?);
                        args791.push(e.get("target")?);
                        fun793.call(args791, kw792)?
                    };
                }
                let assigned795 = {
                    let e = e.child();
                    let out796 = Val::list(vec![]);
                    for item797 in {
                        let fun800 = e.get("range")?;
                        let mut args798 = Vec::new();
                        let mut kw799 = Vec::new();
                        args798.push(e.get("SWING_FROM")?);
                        args798.push(binary("add", e.get("TIP")?, Val::Int(1i64))?);
                        args798.push(Val::Int(2i64));
                        fun800.call(args798, kw799)?
                    }
                    .iter()?
                    {
                        e.set("angle", item797)?;
                        out796.attr("append")?.call(
                            vec![{
                                let mut s = Vec::new();
                                s.push(e.get("mouth")?.get(Val::Int(0i64))?);
                                s.push(binary(
                                    "sub",
                                    e.get("mouth")?.get(Val::Int(1i64))?,
                                    binary("mul", e.get("SWING_R")?, {
                                        let fun803 = e.get("math")?.attr("cos")?;
                                        let mut args801 = Vec::new();
                                        let mut kw802 = Vec::new();
                                        args801.push({
                                            let fun806 = e.get("math")?.attr("radians")?;
                                            let mut args804 = Vec::new();
                                            let mut kw805 = Vec::new();
                                            args804.push(e.get("angle")?);
                                            fun806.call(args804, kw805)?
                                        });
                                        fun803.call(args801, kw802)?
                                    })?,
                                )?);
                                s.push(binary(
                                    "add",
                                    e.get("mouth")?.get(Val::Int(2i64))?,
                                    binary("mul", e.get("SWING_R")?, {
                                        let fun809 = e.get("math")?.attr("sin")?;
                                        let mut args807 = Vec::new();
                                        let mut kw808 = Vec::new();
                                        args807.push({
                                            let fun812 = e.get("math")?.attr("radians")?;
                                            let mut args810 = Vec::new();
                                            let mut kw811 = Vec::new();
                                            args810.push(e.get("angle")?);
                                            fun812.call(args810, kw811)?
                                        });
                                        fun809.call(args807, kw808)?
                                    })?,
                                )?);
                                Val::list(s)
                            }],
                            vec![],
                        )?;
                    }
                    out796
                };
                e.set("swing", assigned795.clone())?;
                let assigned813 = {
                    let fun816 = e.get("dict")?;
                    let mut args814 = Vec::new();
                    let mut kw815 = Vec::new();
                    kw815.push(("sources".into(), {
                        let e = e.child();
                        let out817 = Val::dict(vec![]);
                        for item818 in {
                            let mut s = Vec::new();
                            s.push(e.get("SOURCE")?);
                            s.push({
                                let fun821 = e.get("SOURCE")?.attr("with_suffix")?;
                                let mut args819 = Vec::new();
                                let mut kw820 = Vec::new();
                                args819.push(Val::Str(".step.mesh".into()));
                                fun821.call(args819, kw820)?
                            });
                            s.push(e.get("FACTS")?);
                            s.push({
                                let fun824 = {
                                    let fun827 = e.get("Path")?;
                                    let mut args825 = Vec::new();
                                    let mut kw826 = Vec::new();
                                    args825.push(e.get("_swept_top")?.attr("__file__")?);
                                    fun827.call(args825, kw826)?
                                }
                                .attr("resolve")?;
                                let mut args822 = Vec::new();
                                let mut kw823 = Vec::new();
                                fun824.call(args822, kw823)?
                            });
                            s.push({
                                let fun830 = {
                                    let fun833 = e.get("Path")?;
                                    let mut args831 = Vec::new();
                                    let mut kw832 = Vec::new();
                                    args831.push(e.get("_enclosure_interface")?.attr("__file__")?);
                                    fun833.call(args831, kw832)?
                                }
                                .attr("resolve")?;
                                let mut args828 = Vec::new();
                                let mut kw829 = Vec::new();
                                fun830.call(args828, kw829)?
                            });
                            s.push({
                                let fun836 = e.get("Path")?;
                                let mut args834 = Vec::new();
                                let mut kw835 = Vec::new();
                                args834.push(e.get("__file__")?);
                                fun836.call(args834, kw835)?
                            });
                            s.push({
                                let fun839 = {
                                    let fun842 = e.get("Path")?;
                                    let mut args840 = Vec::new();
                                    let mut kw841 = Vec::new();
                                    args840.push(e.get("_hsm_render")?.attr("__file__")?);
                                    fun842.call(args840, kw841)?
                                }
                                .attr("resolve")?;
                                let mut args837 = Vec::new();
                                let mut kw838 = Vec::new();
                                fun839.call(args837, kw838)?
                            });
                            s.push({
                                let fun845 = {
                                    let fun848 = e.get("Path")?;
                                    let mut args846 = Vec::new();
                                    let mut kw847 = Vec::new();
                                    args846.push(e.get("_mesh_payload")?.attr("__file__")?);
                                    fun848.call(args846, kw847)?
                                }
                                .attr("resolve")?;
                                let mut args843 = Vec::new();
                                let mut kw844 = Vec::new();
                                fun845.call(args843, kw844)?
                            });
                            s.push(binary(
                                "truediv",
                                e.get("ROOT")?,
                                Val::Str("web/public/finishes.json".into()),
                            )?);
                            s.extend(
                                {
                                    let fun851 = e.get("sorted")?;
                                    let mut args849 = Vec::new();
                                    let mut kw850 = Vec::new();
                                    args849.push({
                                        let fun854 = binary(
                                            "truediv",
                                            e.get("ROOT")?,
                                            Val::Str("tools/hsm/render".into()),
                                        )?
                                        .attr("rglob")?;
                                        let mut args852 = Vec::new();
                                        let mut kw853 = Vec::new();
                                        args852.push(Val::Str("*.rs".into()));
                                        fun854.call(args852, kw853)?
                                    });
                                    fun851.call(args849, kw850)?
                                }
                                .iter()?,
                            );
                            s.extend(
                                {
                                    let fun857 = e.get("sorted")?;
                                    let mut args855 = Vec::new();
                                    let mut kw856 = Vec::new();
                                    args855.push({
                                        let fun860 = binary(
                                            "truediv",
                                            e.get("ROOT")?,
                                            Val::Str("tools/hsm/render".into()),
                                        )?
                                        .attr("rglob")?;
                                        let mut args858 = Vec::new();
                                        let mut kw859 = Vec::new();
                                        args858.push(Val::Str("*.wgsl".into()));
                                        fun860.call(args858, kw859)?
                                    });
                                    fun857.call(args855, kw856)?
                                }
                                .iter()?,
                            );
                            Val::tuple(s)
                        }
                        .iter()?
                        {
                            e.set("p", item818)?;
                            out817.set(
                                {
                                    let fun863 = e.get("str")?;
                                    let mut args861 = Vec::new();
                                    let mut kw862 = Vec::new();
                                    args861.push({
                                        let fun866 = e.get("p")?.attr("relative_to")?;
                                        let mut args864 = Vec::new();
                                        let mut kw865 = Vec::new();
                                        args864.push(e.get("ROOT")?);
                                        fun866.call(args864, kw865)?
                                    });
                                    fun863.call(args861, kw862)?
                                },
                                {
                                    let fun869 = {
                                        let fun872 = e.get("hashlib")?.attr("sha256")?;
                                        let mut args870 = Vec::new();
                                        let mut kw871 = Vec::new();
                                        args870.push({
                                            let fun875 = e.get("p")?.attr("read_bytes")?;
                                            let mut args873 = Vec::new();
                                            let mut kw874 = Vec::new();
                                            fun875.call(args873, kw874)?
                                        });
                                        fun872.call(args870, kw871)?
                                    }
                                    .attr("hexdigest")?;
                                    let mut args867 = Vec::new();
                                    let mut kw868 = Vec::new();
                                    fun869.call(args867, kw868)?
                                },
                            )?;
                        }
                        out817
                    }));
                    kw815.push(("funnel_bounds".into(), e.get("FUNNEL_BOUNDS")?));
                    kw815.push(("bottle_mouth".into(), e.get("mouth")?));
                    kw815.push(("bottle_tip".into(), e.get("TIP")?));
                    kw815.push(("screen".into(), e.get("SCREEN")?));
                    kw815.push(("pose".into(), {
                        let fun878 = e.get("dict")?;
                        let mut args876 = Vec::new();
                        let mut kw877 = Vec::new();
                        kw877.push(("cam".into(), e.get("CAMERA")?));
                        kw877.push(("target".into(), e.get("TARGET")?));
                        kw877.push(("span".into(), e.get("SPAN")?));
                        kw877.push(("size".into(), {
                            let mut s = Vec::new();
                            s.push(Val::Int(1600i64));
                            s.push(Val::Int(1500i64));
                            Val::tuple(s)
                        }));
                        fun878.call(args876, kw877)?
                    }));
                    kw815.push(("arrow".into(), e.get("swing")?));
                    kw815.push(("artwork".into(), {
                        let e = e.child();
                        let out879 = Val::dict(vec![]);
                        for item880 in e.get("targets")?.iter()? {
                            let unpack881 = unpack(item880, 2)?;
                            e.set("_", unpack881[0].clone())?;
                            e.set("p", unpack881[1].clone())?;
                            out879.set(
                                {
                                    let fun884 = e.get("str")?;
                                    let mut args882 = Vec::new();
                                    let mut kw883 = Vec::new();
                                    args882.push({
                                        let fun887 = e.get("p")?.attr("relative_to")?;
                                        let mut args885 = Vec::new();
                                        let mut kw886 = Vec::new();
                                        args885.push(e.get("ROOT")?);
                                        fun887.call(args885, kw886)?
                                    });
                                    fun884.call(args882, kw883)?
                                },
                                {
                                    let fun890 = {
                                        let fun893 = e.get("hashlib")?.attr("sha256")?;
                                        let mut args891 = Vec::new();
                                        let mut kw892 = Vec::new();
                                        args891.push({
                                            let fun896 = e.get("p")?.attr("read_bytes")?;
                                            let mut args894 = Vec::new();
                                            let mut kw895 = Vec::new();
                                            fun896.call(args894, kw895)?
                                        });
                                        fun893.call(args891, kw892)?
                                    }
                                    .attr("hexdigest")?;
                                    let mut args888 = Vec::new();
                                    let mut kw889 = Vec::new();
                                    fun890.call(args888, kw889)?
                                },
                            )?;
                        }
                        out879
                    }));
                    fun816.call(args814, kw815)?
                };
                e.set("inputs", assigned813.clone())?;
                {
                    let fun899 = binary(
                        "truediv",
                        e.get("DIR")?,
                        Val::Str("assets/fill-scene-inputs.json".into()),
                    )?
                    .attr("write_text")?;
                    let mut args897 = Vec::new();
                    let mut kw898 = Vec::new();
                    args897.push(binary(
                        "add",
                        {
                            let fun902 = e.get("json")?.attr("dumps")?;
                            let mut args900 = Vec::new();
                            let mut kw901 = Vec::new();
                            args900.push(e.get("inputs")?);
                            kw901.push(("indent".into(), Val::Int(2i64)));
                            fun902.call(args900, kw901)?
                        },
                        Val::Str("\n".into()),
                    )?);
                    fun899.call(args897, kw898)?
                };
            } else {
                let assigned903 = binary(
                    "truediv",
                    e.get("HARDWARE")?,
                    Val::Str("install-guide/assets".into()),
                )?;
                e.set("install", assigned903.clone())?;
                let assigned904 = binary(
                    "truediv",
                    e.get("install")?,
                    Val::Str("print-resolution.json".into()),
                )?;
                e.set("resolution_file", assigned904.clone())?;
                let assigned905 = {
                    let fun908 = e.get("json")?.attr("loads")?;
                    let mut args906 = Vec::new();
                    let mut kw907 = Vec::new();
                    args906.push({
                        let fun911 = e.get("resolution_file")?.attr("read_text")?;
                        let mut args909 = Vec::new();
                        let mut kw910 = Vec::new();
                        fun911.call(args909, kw910)?
                    });
                    fun908.call(args906, kw907)?
                };
                e.set("resolutions", assigned905.clone())?;
                for item912 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("fill")?);
                        s.push(Val::Str("steps/fill-ready.png".into()));
                        s.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/reference/fill-ready.png".into()),
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("frame")?);
                        s.push(Val::Str("fill-screen-framed.png".into()));
                        s.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/reference/fill-screen-framed.png".into()),
                        )?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("closed")?);
                        s.push(Val::Str("steps/fill-closed.png".into()));
                        s.push(binary(
                            "truediv",
                            e.get("DIR")?,
                            Val::Str("assets/reference/fill-closed.png".into()),
                        )?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                }
                .iter()?
                {
                    let unpack953 = unpack(item912, 3)?;
                    e.set("source", unpack953[0].clone())?;
                    e.set("name", unpack953[1].clone())?;
                    e.set("reference", unpack953[2].clone())?;
                    let assigned913 = binary("truediv", e.get("install")?, e.get("name")?)?;
                    e.set("target", assigned913.clone())?;
                    {
                        let fun916 = e.get("shutil")?.attr("copy2")?;
                        let mut args914 = Vec::new();
                        let mut kw915 = Vec::new();
                        args914.push(e.get("source")?);
                        args914.push(e.get("target")?);
                        fun916.call(args914, kw915)?
                    };
                    let assigned917 = {
                        let fun920 = e.get("Image")?.attr("open")?;
                        let mut args918 = Vec::new();
                        let mut kw919 = Vec::new();
                        args918.push(e.get("reference")?);
                        fun920.call(args918, kw919)?
                    }
                    .attr("size")?;
                    e.set("reference_size", assigned917.clone())?;
                    let assigned921 = {
                        let fun924 = e.get("Image")?.attr("open")?;
                        let mut args922 = Vec::new();
                        let mut kw923 = Vec::new();
                        args922.push(e.get("target")?);
                        fun924.call(args922, kw923)?
                    }
                    .attr("size")?;
                    e.set("render_size", assigned921.clone())?;
                    let assigned925 = {
                        let fun928 = e.get("dict")?;
                        let mut args926 = Vec::new();
                        let mut kw927 = Vec::new();
                        kw927.push(("reference_size".into(), e.get("reference_size")?));
                        kw927.push(("render_size".into(), e.get("render_size")?));
                        kw927.push(("scale".into(), {
                            let e = e.child();
                            let out929 = Val::list(vec![]);
                            for item930 in {
                                let fun933 = e.get("zip")?;
                                let mut args931 = Vec::new();
                                let mut kw932 = Vec::new();
                                args931.push(e.get("render_size")?);
                                args931.push(e.get("reference_size")?);
                                fun933.call(args931, kw932)?
                            }
                            .iter()?
                            {
                                let unpack934 = unpack(item930, 2)?;
                                e.set("a", unpack934[0].clone())?;
                                e.set("b", unpack934[1].clone())?;
                                out929.attr("append")?.call(
                                    vec![binary("truediv", e.get("a")?, e.get("b")?)?],
                                    vec![],
                                )?;
                            }
                            out929
                        }));
                        kw927.push(("coordinate_reference_sha256".into(), {
                            let fun937 = {
                                let fun940 = e.get("hashlib")?.attr("sha256")?;
                                let mut args938 = Vec::new();
                                let mut kw939 = Vec::new();
                                args938.push({
                                    let fun943 = e.get("reference")?.attr("read_bytes")?;
                                    let mut args941 = Vec::new();
                                    let mut kw942 = Vec::new();
                                    fun943.call(args941, kw942)?
                                });
                                fun940.call(args938, kw939)?
                            }
                            .attr("hexdigest")?;
                            let mut args935 = Vec::new();
                            let mut kw936 = Vec::new();
                            fun937.call(args935, kw936)?
                        }));
                        kw927.push(("render_sha256".into(), {
                            let fun946 = {
                                let fun949 = e.get("hashlib")?.attr("sha256")?;
                                let mut args947 = Vec::new();
                                let mut kw948 = Vec::new();
                                args947.push({
                                    let fun952 = e.get("target")?.attr("read_bytes")?;
                                    let mut args950 = Vec::new();
                                    let mut kw951 = Vec::new();
                                    fun952.call(args950, kw951)?
                                });
                                fun949.call(args947, kw948)?
                            }
                            .attr("hexdigest")?;
                            let mut args944 = Vec::new();
                            let mut kw945 = Vec::new();
                            fun946.call(args944, kw945)?
                        }));
                        fun928.call(args926, kw927)?
                    };
                    e.get("resolutions")?
                        .get(Val::Str("assets".into()))?
                        .set(e.get("name")?, assigned925.clone())?;
                }
                {
                    let fun956 = e.get("resolution_file")?.attr("write_text")?;
                    let mut args954 = Vec::new();
                    let mut kw955 = Vec::new();
                    args954.push(binary(
                        "add",
                        {
                            let fun959 = e.get("json")?.attr("dumps")?;
                            let mut args957 = Vec::new();
                            let mut kw958 = Vec::new();
                            args957.push(e.get("resolutions")?);
                            kw958.push(("indent".into(), Val::Int(2i64)));
                            fun959.call(args957, kw958)?
                        },
                        Val::Str("\n".into()),
                    )?);
                    fun956.call(args954, kw955)?
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun962 = e.get("main")?;
        let mut args960 = Vec::new();
        let mut kw961 = Vec::new();
        fun962.call(args960, kw961)?
    };
    Ok(Val::None)
}
