#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod2 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
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
    .attr("parent")?;
    e.set("HERE", assigned3.clone())?;
    {
        let fun12 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args10 = Vec::new();
        let mut kw11 = Vec::new();
        args10.push(Val::Int(0i64));
        args10.push({
            let fun15 = e.get("str")?;
            let mut args13 = Vec::new();
            let mut kw14 = Vec::new();
            args13.push(binary(
                "truediv",
                e.get("HERE")?.attr("parent")?,
                Val::Str("scripts".into()),
            )?);
            fun15.call(args13, kw14)?
        });
        fun12.call(args10, kw11)?
    };
    let mod16 = rt.import_module("_carbonator_drawing")?;
    import_star(&e, mod16.clone())?;
    let assigned17 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("carbonator-vessel-weldment-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned17.clone())?;
    let assigned18 = {
        let mut s = Vec::new();
        s.push(binary("mul", Val::Int(17i64), e.get("IN")?)?);
        s.push(binary("mul", Val::Int(11i64), e.get("IN")?)?);
        Val::tuple(s)
    };
    e.set("SHEET", assigned18.clone())?;
    let assigned19 = {
        let mut s = Vec::new();
        s.push(Val::Int(330i64));
        s.push(Val::Int(242i64));
        Val::tuple(s)
    };
    let unpack20 = unpack(assigned19.clone(), 2)?;
    e.set("CX", unpack20[0].clone())?;
    e.set("BASE", unpack20[1].clone())?;
    let assigned21 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("section-upper".into()));
            s.push(Val::Int(30i64));
            s.push(Val::Int(594i64));
            s.push(Val::Int(655i64));
            s.push(Val::Int(765i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("section-body".into()));
            s.push(Val::Int(30i64));
            s.push(Val::Int(330i64));
            s.push(Val::Int(655i64));
            s.push(Val::Int(600i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("section-lower".into()));
            s.push(Val::Int(30i64));
            s.push(Val::Int(185i64));
            s.push(Val::Int(655i64));
            s.push(Val::Int(335i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("end-view".into()));
            s.push(Val::Int(640i64));
            s.push(Val::Int(473i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(765i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("closure-detail".into()));
            s.push(Val::Int(875i64));
            s.push(Val::Int(478i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(765i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("parts-list".into()));
            s.push(Val::Int(642i64));
            s.push(Val::Int(353i64));
            s.push(Val::Int(1180i64));
            s.push(Val::Int(476i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("requirements".into()));
            s.push(Val::Int(642i64));
            s.push(Val::Int(145i64));
            s.push(Val::Int(1180i64));
            s.push(Val::Int(355i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Str("title-release".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(1197i64));
            s.push(Val::Int(181i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("REVIEW_REGIONS", assigned21.clone())?;
    // z
    e.set("z", {
        let params = vec![("value".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                e.get("BASE")?,
                binary("mul", e.get("value")?, e.get("IN")?)?,
            )?);
            Ok(Val::None)
        })
    })?;
    // longitudinal_section
    e.set("longitudinal_section", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun24 = e.get("text")?;
                let mut args22 = Vec::new();
                let mut kw23 = Vec::new();
                args22.push(e.get("c")?);
                args22.push(e.get("CX")?);
                args22.push(Val::Int(750i64));
                args22.push(Val::Str("SECTION A-A".into()));
                args22.push(Val::Int(12i64));
                kw23.push(("bold".into(), Val::Bool(true)));
                kw23.push(("align".into(), Val::Str("center".into())));
                fun24.call(args22, kw23)?
            };
            {
                let fun27 = e.get("text")?;
                let mut args25 = Vec::new();
                let mut kw26 = Vec::new();
                args25.push(e.get("c")?);
                args25.push(e.get("CX")?);
                args25.push(Val::Int(733i64));
                args25.push(Val::Str("LOOKING +X; RIGHT IS -Y - SCALE 1:1".into()));
                args25.push(Val::Int(9i64));
                kw26.push(("align".into(), Val::Str("center".into())));
                fun27.call(args25, kw26)?
            };
            let assigned28 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("CX")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("OD")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("CX")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("OD")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack29 = unpack(assigned28.clone(), 2)?;
            e.set("left", unpack29[0].clone())?;
            e.set("right", unpack29[1].clone())?;
            let assigned30 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("CX")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("ID")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("CX")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("ID")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack31 = unpack(assigned30.clone(), 2)?;
            e.set("bore_l", unpack31[0].clone())?;
            e.set("bore_r", unpack31[1].clone())?;
            let assigned32 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("CX")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("CAP_D")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push(binary(
                    "add",
                    e.get("CX")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("CAP_D")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack33 = unpack(assigned32.clone(), 2)?;
            e.set("cap_l", unpack33[0].clone())?;
            e.set("cap_r", unpack33[1].clone())?;
            for item34 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(e.get("bore_l")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("bore_r")?);
                    s.push(e.get("right")?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack44 = unpack(item34, 2)?;
                e.set("a", unpack44[0].clone())?;
                e.set("b", unpack44[1].clone())?;
                {
                    let fun37 = e.get("section_material")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    args35.push(e.get("c")?);
                    args35.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push(e.get("BASE")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push(e.get("BASE")?);
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push({
                                let fun40 = e.get("z")?;
                                let mut args38 = Vec::new();
                                let mut kw39 = Vec::new();
                                args38.push(e.get("LENGTH")?);
                                fun40.call(args38, kw39)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push({
                                let fun43 = e.get("z")?;
                                let mut args41 = Vec::new();
                                let mut kw42 = Vec::new();
                                args41.push(e.get("LENGTH")?);
                                fun43.call(args41, kw42)?
                            });
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    kw36.push(("spacing".into(), Val::Int(6i64)));
                    fun37.call(args35, kw36)?
                };
            }
            for item45 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("RECESS")?);
                    s.push(e.get("FLOOR")?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("CEILING")?);
                    s.push(binary("sub", e.get("LENGTH")?, e.get("RECESS")?)?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack61 = unpack(item45, 2)?;
                e.set("lo", unpack61[0].clone())?;
                e.set("hi", unpack61[1].clone())?;
                {
                    let fun48 = e.get("section_material")?;
                    let mut args46 = Vec::new();
                    let mut kw47 = Vec::new();
                    args46.push(e.get("c")?);
                    args46.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("cap_l")?);
                            s.push({
                                let fun51 = e.get("z")?;
                                let mut args49 = Vec::new();
                                let mut kw50 = Vec::new();
                                args49.push(e.get("lo")?);
                                fun51.call(args49, kw50)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("cap_r")?);
                            s.push({
                                let fun54 = e.get("z")?;
                                let mut args52 = Vec::new();
                                let mut kw53 = Vec::new();
                                args52.push(e.get("lo")?);
                                fun54.call(args52, kw53)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("cap_r")?);
                            s.push({
                                let fun57 = e.get("z")?;
                                let mut args55 = Vec::new();
                                let mut kw56 = Vec::new();
                                args55.push(e.get("hi")?);
                                fun57.call(args55, kw56)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("cap_l")?);
                            s.push({
                                let fun60 = e.get("z")?;
                                let mut args58 = Vec::new();
                                let mut kw59 = Vec::new();
                                args58.push(e.get("hi")?);
                                fun60.call(args58, kw59)?
                            });
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    kw47.push(("reverse".into(), Val::Bool(true)));
                    fun48.call(args46, kw47)?
                };
            }
            for item62 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("bore_l")?);
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(e.get("bore_r")?);
                    s.push(unary("neg", Val::Int(1i64))?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack99 = unpack(item62, 2)?;
                e.set("wall_x", unpack99[0].clone())?;
                e.set("side", unpack99[1].clone())?;
                for item63 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun94 = e.get("z")?;
                            let mut args92 = Vec::new();
                            let mut kw93 = Vec::new();
                            args92.push(e.get("RECESS")?);
                            fun94.call(args92, kw93)?
                        });
                        s.push(unary("neg", Val::Int(1i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push({
                            let fun97 = e.get("z")?;
                            let mut args95 = Vec::new();
                            let mut kw96 = Vec::new();
                            args95.push(binary("sub", e.get("LENGTH")?, e.get("RECESS")?)?);
                            fun97.call(args95, kw96)?
                        });
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    let unpack98 = unpack(item63, 2)?;
                    e.set("face_y", unpack98[0].clone())?;
                    e.set("up", unpack98[1].clone())?;
                    let assigned64 = {
                        let fun67 = e.get("c")?.attr("beginPath")?;
                        let mut args65 = Vec::new();
                        let mut kw66 = Vec::new();
                        fun67.call(args65, kw66)?
                    };
                    e.set("p", assigned64.clone())?;
                    {
                        let fun70 = e.get("p")?.attr("moveTo")?;
                        let mut args68 = Vec::new();
                        let mut kw69 = Vec::new();
                        args68.push(binary(
                            "add",
                            e.get("wall_x")?,
                            binary("mul", e.get("side")?, Val::Int(5i64))?,
                        )?);
                        args68.push(e.get("face_y")?);
                        fun70.call(args68, kw69)?
                    };
                    {
                        let fun73 = e.get("p")?.attr("curveTo")?;
                        let mut args71 = Vec::new();
                        let mut kw72 = Vec::new();
                        args71.push(binary(
                            "add",
                            e.get("wall_x")?,
                            binary("mul", e.get("side")?, Val::Int(2i64))?,
                        )?);
                        args71.push(binary(
                            "add",
                            e.get("face_y")?,
                            binary("mul", e.get("up")?, Val::Float(0.5f64))?,
                        )?);
                        args71.push(binary(
                            "add",
                            e.get("wall_x")?,
                            binary("mul", e.get("side")?, Val::Float(0.5f64))?,
                        )?);
                        args71.push(binary(
                            "add",
                            e.get("face_y")?,
                            binary("mul", e.get("up")?, Val::Int(2i64))?,
                        )?);
                        args71.push(e.get("wall_x")?);
                        args71.push(binary(
                            "add",
                            e.get("face_y")?,
                            binary("mul", e.get("up")?, Val::Int(5i64))?,
                        )?);
                        fun73.call(args71, kw72)?
                    };
                    {
                        let fun76 = e.get("p")?.attr("lineTo")?;
                        let mut args74 = Vec::new();
                        let mut kw75 = Vec::new();
                        args74.push(e.get("wall_x")?);
                        args74.push(e.get("face_y")?);
                        fun76.call(args74, kw75)?
                    };
                    {
                        let fun79 = e.get("p")?.attr("close")?;
                        let mut args77 = Vec::new();
                        let mut kw78 = Vec::new();
                        fun79.call(args77, kw78)?
                    };
                    {
                        let fun82 = e.get("c")?.attr("setFillColorRGB")?;
                        let mut args80 = Vec::new();
                        let mut kw81 = Vec::new();
                        args80.push(Val::Float(0.85f64));
                        args80.push(Val::Float(0.85f64));
                        args80.push(Val::Float(0.85f64));
                        fun82.call(args80, kw81)?
                    };
                    {
                        let fun85 = e.get("c")?.attr("setLineWidth")?;
                        let mut args83 = Vec::new();
                        let mut kw84 = Vec::new();
                        args83.push(Val::Float(0.5f64));
                        fun85.call(args83, kw84)?
                    };
                    {
                        let fun88 = e.get("c")?.attr("drawPath")?;
                        let mut args86 = Vec::new();
                        let mut kw87 = Vec::new();
                        args86.push(e.get("p")?);
                        kw87.push(("fill".into(), Val::Int(1i64)));
                        kw87.push(("stroke".into(), Val::Int(1i64)));
                        fun88.call(args86, kw87)?
                    };
                    {
                        let fun91 = e.get("c")?.attr("setFillColorRGB")?;
                        let mut args89 = Vec::new();
                        let mut kw90 = Vec::new();
                        args89.push(Val::Int(0i64));
                        args89.push(Val::Int(0i64));
                        args89.push(Val::Int(0i64));
                        fun91.call(args89, kw90)?
                    };
                }
            }
            for item100 in {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    unary("neg", e.get("carb")?.attr("carbonator_port_offset")?)?,
                    e.get("MM")?,
                )?);
                s.push(binary(
                    "truediv",
                    e.get("carb")?.attr("carbonator_port_offset")?,
                    e.get("MM")?,
                )?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("px", item100)?;
                let assigned101 = binary(
                    "add",
                    e.get("CX")?,
                    binary("mul", e.get("px")?, e.get("IN")?)?,
                )?;
                e.set("x", assigned101.clone())?;
                for item102 in {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("RECESS")?);
                        s.push(e.get("FLOOR")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("CEILING")?);
                        s.push(binary("sub", e.get("LENGTH")?, e.get("RECESS")?)?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                }
                .iter()?
                {
                    let unpack133 = unpack(item102, 2)?;
                    e.set("lo", unpack133[0].clone())?;
                    e.set("hi", unpack133[1].clone())?;
                    {
                        let fun105 = e.get("c")?.attr("setFillColorRGB")?;
                        let mut args103 = Vec::new();
                        let mut kw104 = Vec::new();
                        args103.push(Val::Int(1i64));
                        args103.push(Val::Int(1i64));
                        args103.push(Val::Int(1i64));
                        fun105.call(args103, kw104)?
                    };
                    {
                        let fun108 = e.get("c")?.attr("rect")?;
                        let mut args106 = Vec::new();
                        let mut kw107 = Vec::new();
                        args106.push(binary(
                            "sub",
                            e.get("x")?,
                            binary("mul", e.get("cap")?.attr("hole_radius")?, e.get("IN")?)?,
                        )?);
                        args106.push({
                            let fun111 = e.get("z")?;
                            let mut args109 = Vec::new();
                            let mut kw110 = Vec::new();
                            args109.push(e.get("lo")?);
                            fun111.call(args109, kw110)?
                        });
                        args106.push(binary(
                            "mul",
                            binary("mul", Val::Int(2i64), e.get("cap")?.attr("hole_radius")?)?,
                            e.get("IN")?,
                        )?);
                        args106.push(binary(
                            "mul",
                            binary("sub", e.get("hi")?, e.get("lo")?)?,
                            e.get("IN")?,
                        )?);
                        kw107.push(("fill".into(), Val::Int(1i64)));
                        kw107.push(("stroke".into(), Val::Int(0i64)));
                        fun108.call(args106, kw107)?
                    };
                    {
                        let fun114 = e.get("c")?.attr("setFillColorRGB")?;
                        let mut args112 = Vec::new();
                        let mut kw113 = Vec::new();
                        args112.push(Val::Int(0i64));
                        args112.push(Val::Int(0i64));
                        args112.push(Val::Int(0i64));
                        fun114.call(args112, kw113)?
                    };
                    {
                        let fun117 = e.get("line")?;
                        let mut args115 = Vec::new();
                        let mut kw116 = Vec::new();
                        args115.push(e.get("c")?);
                        args115.push(binary(
                            "sub",
                            e.get("x")?,
                            binary("mul", e.get("cap")?.attr("hole_radius")?, e.get("IN")?)?,
                        )?);
                        args115.push({
                            let fun120 = e.get("z")?;
                            let mut args118 = Vec::new();
                            let mut kw119 = Vec::new();
                            args118.push(e.get("lo")?);
                            fun120.call(args118, kw119)?
                        });
                        args115.push(binary(
                            "sub",
                            e.get("x")?,
                            binary("mul", e.get("cap")?.attr("hole_radius")?, e.get("IN")?)?,
                        )?);
                        args115.push({
                            let fun123 = e.get("z")?;
                            let mut args121 = Vec::new();
                            let mut kw122 = Vec::new();
                            args121.push(e.get("hi")?);
                            fun123.call(args121, kw122)?
                        });
                        args115.push(e.get("VISIBLE")?);
                        fun117.call(args115, kw116)?
                    };
                    {
                        let fun126 = e.get("line")?;
                        let mut args124 = Vec::new();
                        let mut kw125 = Vec::new();
                        args124.push(e.get("c")?);
                        args124.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", e.get("cap")?.attr("hole_radius")?, e.get("IN")?)?,
                        )?);
                        args124.push({
                            let fun129 = e.get("z")?;
                            let mut args127 = Vec::new();
                            let mut kw128 = Vec::new();
                            args127.push(e.get("lo")?);
                            fun129.call(args127, kw128)?
                        });
                        args124.push(binary(
                            "add",
                            e.get("x")?,
                            binary("mul", e.get("cap")?.attr("hole_radius")?, e.get("IN")?)?,
                        )?);
                        args124.push({
                            let fun132 = e.get("z")?;
                            let mut args130 = Vec::new();
                            let mut kw131 = Vec::new();
                            args130.push(e.get("hi")?);
                            fun132.call(args130, kw131)?
                        });
                        args124.push(e.get("VISIBLE")?);
                        fun126.call(args124, kw125)?
                    };
                }
            }
            let assigned134 = binary(
                "add",
                e.get("CX")?,
                binary("mul", e.get("ROD_RADIUS")?, e.get("IN")?)?,
            )?;
            e.set("rod_x", assigned134.clone())?;
            {
                let fun137 = e.get("register_opening")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                args135.push(e.get("c")?);
                args135.push(e.get("rod_x")?);
                args135.push({
                    let fun140 = e.get("z")?;
                    let mut args138 = Vec::new();
                    let mut kw139 = Vec::new();
                    args138.push(e.get("FLOOR")?);
                    fun140.call(args138, kw139)?
                });
                args135.push(e.get("IN")?);
                args135.push(unary("neg", Val::Int(1i64))?);
                fun137.call(args135, kw136)?
            };
            {
                let fun143 = e.get("register_opening")?;
                let mut args141 = Vec::new();
                let mut kw142 = Vec::new();
                args141.push(e.get("c")?);
                args141.push(e.get("rod_x")?);
                args141.push({
                    let fun146 = e.get("z")?;
                    let mut args144 = Vec::new();
                    let mut kw145 = Vec::new();
                    args144.push(e.get("CEILING")?);
                    fun146.call(args144, kw145)?
                });
                args141.push(e.get("IN")?);
                args141.push(Val::Int(1i64));
                fun143.call(args141, kw142)?
            };
            let assigned147 = binary(
                "sub",
                e.get("CEILING")?,
                binary(
                    "truediv",
                    e.get("carb")?.attr("UPPER_STOP_H")?,
                    e.get("MM")?,
                )?,
            )?;
            e.set("stop_lo", assigned147.clone())?;
            for item148 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                binary(
                                    "truediv",
                                    e.get("carb")?.attr("UPPER_STOP_D")?,
                                    e.get("MM")?,
                                )?,
                                e.get("IN")?,
                            )?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(binary(
                        "sub",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                binary(
                                    "truediv",
                                    e.get("carb")?.attr("UPPER_STOP_BORE")?,
                                    e.get("MM")?,
                                )?,
                                e.get("IN")?,
                            )?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                binary(
                                    "truediv",
                                    e.get("carb")?.attr("UPPER_STOP_BORE")?,
                                    e.get("MM")?,
                                )?,
                                e.get("IN")?,
                            )?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                binary(
                                    "truediv",
                                    e.get("carb")?.attr("UPPER_STOP_D")?,
                                    e.get("MM")?,
                                )?,
                                e.get("IN")?,
                            )?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    Val::tuple(s)
                });
                Val::tuple(s)
            }
            .iter()?
            {
                let unpack164 = unpack(item148, 2)?;
                e.set("a", unpack164[0].clone())?;
                e.set("b", unpack164[1].clone())?;
                {
                    let fun151 = e.get("section_material")?;
                    let mut args149 = Vec::new();
                    let mut kw150 = Vec::new();
                    args149.push(e.get("c")?);
                    args149.push({
                        let mut s = Vec::new();
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push({
                                let fun154 = e.get("z")?;
                                let mut args152 = Vec::new();
                                let mut kw153 = Vec::new();
                                args152.push(e.get("stop_lo")?);
                                fun154.call(args152, kw153)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push({
                                let fun157 = e.get("z")?;
                                let mut args155 = Vec::new();
                                let mut kw156 = Vec::new();
                                args155.push(e.get("stop_lo")?);
                                fun157.call(args155, kw156)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("b")?);
                            s.push({
                                let fun160 = e.get("z")?;
                                let mut args158 = Vec::new();
                                let mut kw159 = Vec::new();
                                args158.push(e.get("CEILING")?);
                                fun160.call(args158, kw159)?
                            });
                            Val::tuple(s)
                        });
                        s.push({
                            let mut s = Vec::new();
                            s.push(e.get("a")?);
                            s.push({
                                let fun163 = e.get("z")?;
                                let mut args161 = Vec::new();
                                let mut kw162 = Vec::new();
                                args161.push(e.get("CEILING")?);
                                fun163.call(args161, kw162)?
                            });
                            Val::tuple(s)
                        });
                        Val::list(s)
                    });
                    kw150.push(("spacing".into(), Val::Int(4i64)));
                    fun151.call(args149, kw150)?
                };
            }
            {
                let fun167 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args165 = Vec::new();
                let mut kw166 = Vec::new();
                args165.push(Val::Int(1i64));
                args165.push(Val::Int(1i64));
                args165.push(Val::Int(1i64));
                fun167.call(args165, kw166)?
            };
            {
                let fun170 = e.get("c")?.attr("setLineWidth")?;
                let mut args168 = Vec::new();
                let mut kw169 = Vec::new();
                args168.push(e.get("VISIBLE")?);
                fun170.call(args168, kw169)?
            };
            {
                let fun173 = e.get("c")?.attr("rect")?;
                let mut args171 = Vec::new();
                let mut kw172 = Vec::new();
                args171.push(binary(
                    "sub",
                    e.get("rod_x")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("ROD_D")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                args171.push({
                    let fun176 = e.get("z")?;
                    let mut args174 = Vec::new();
                    let mut kw175 = Vec::new();
                    args174.push(e.get("ROD_BOTTOM")?);
                    fun176.call(args174, kw175)?
                });
                args171.push(binary("mul", e.get("ROD_D")?, e.get("IN")?)?);
                args171.push(binary(
                    "mul",
                    binary("sub", e.get("ROD_TOP")?, e.get("ROD_BOTTOM")?)?,
                    e.get("IN")?,
                )?);
                kw172.push(("stroke".into(), Val::Int(1i64)));
                kw172.push(("fill".into(), Val::Int(1i64)));
                fun173.call(args171, kw172)?
            };
            {
                let fun179 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args177 = Vec::new();
                let mut kw178 = Vec::new();
                args177.push(Val::Int(0i64));
                args177.push(Val::Int(0i64));
                args177.push(Val::Int(0i64));
                fun179.call(args177, kw178)?
            };
            {
                let fun182 = e.get("line")?;
                let mut args180 = Vec::new();
                let mut kw181 = Vec::new();
                args180.push(e.get("c")?);
                args180.push(e.get("CX")?);
                args180.push(binary("sub", e.get("BASE")?, Val::Int(15i64))?);
                args180.push(e.get("CX")?);
                args180.push(binary(
                    "add",
                    {
                        let fun185 = e.get("z")?;
                        let mut args183 = Vec::new();
                        let mut kw184 = Vec::new();
                        args183.push(e.get("LENGTH")?);
                        fun185.call(args183, kw184)?
                    },
                    Val::Int(15i64),
                )?);
                kw181.push(("dash".into(), e.get("CENTER_DASH")?));
                fun182.call(args180, kw181)?
            };
            {
                let fun188 = e.get("line")?;
                let mut args186 = Vec::new();
                let mut kw187 = Vec::new();
                args186.push(e.get("c")?);
                args186.push(e.get("rod_x")?);
                args186.push(binary(
                    "sub",
                    {
                        let fun191 = e.get("z")?;
                        let mut args189 = Vec::new();
                        let mut kw190 = Vec::new();
                        args189.push(e.get("ROD_BOTTOM")?);
                        fun191.call(args189, kw190)?
                    },
                    Val::Int(9i64),
                )?);
                args186.push(e.get("rod_x")?);
                args186.push(binary(
                    "add",
                    {
                        let fun194 = e.get("z")?;
                        let mut args192 = Vec::new();
                        let mut kw193 = Vec::new();
                        args192.push(e.get("ROD_TOP")?);
                        fun194.call(args192, kw193)?
                    },
                    Val::Int(9i64),
                )?);
                kw187.push(("dash".into(), e.get("CENTER_DASH")?));
                fun188.call(args186, kw187)?
            };
            let assigned195 = {
                let mut s = Vec::new();
                s.push(binary("mul", e.get("FLOAT_D")?, e.get("IN")?)?);
                s.push(binary("mul", e.get("FLOAT_H")?, e.get("IN")?)?);
                Val::tuple(s)
            };
            let unpack196 = unpack(assigned195.clone(), 2)?;
            e.set("float_w", unpack196[0].clone())?;
            e.set("float_h", unpack196[1].clone())?;
            {
                let fun199 = e.get("c")?.attr("setDash")?;
                let mut args197 = Vec::new();
                let mut kw198 = Vec::new();
                args197.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(10i64));
                    s.push(Val::Int(3i64));
                    s.push(Val::Int(2i64));
                    s.push(Val::Int(3i64));
                    s.push(Val::Int(2i64));
                    s.push(Val::Int(3i64));
                    Val::tuple(s)
                });
                fun199.call(args197, kw198)?
            };
            {
                let fun202 = e.get("c")?.attr("setLineWidth")?;
                let mut args200 = Vec::new();
                let mut kw201 = Vec::new();
                args200.push(e.get("THIN")?);
                fun202.call(args200, kw201)?
            };
            {
                let fun205 = e.get("c")?.attr("rect")?;
                let mut args203 = Vec::new();
                let mut kw204 = Vec::new();
                args203.push(binary(
                    "sub",
                    e.get("rod_x")?,
                    binary("truediv", e.get("float_w")?, Val::Int(2i64))?,
                )?);
                args203.push({
                    let fun208 = e.get("z")?;
                    let mut args206 = Vec::new();
                    let mut kw207 = Vec::new();
                    args206.push(Val::Float(2.6f64));
                    fun208.call(args206, kw207)?
                });
                args203.push(e.get("float_w")?);
                args203.push(e.get("float_h")?);
                kw204.push(("stroke".into(), Val::Int(1i64)));
                kw204.push(("fill".into(), Val::Int(0i64)));
                fun205.call(args203, kw204)?
            };
            {
                let fun211 = e.get("c")?.attr("setDash")?;
                let mut args209 = Vec::new();
                let mut kw210 = Vec::new();
                fun211.call(args209, kw210)?
            };
            {
                let fun214 = e.get("balloon")?;
                let mut args212 = Vec::new();
                let mut kw213 = Vec::new();
                args212.push(e.get("c")?);
                args212.push(Val::Int(1i64));
                args212.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(126i64));
                    s.push(Val::Int(488i64));
                    Val::tuple(s)
                });
                args212.push({
                    let mut s = Vec::new();
                    s.push(e.get("left")?);
                    s.push(Val::Int(454i64));
                    Val::tuple(s)
                });
                fun214.call(args212, kw213)?
            };
            {
                let fun217 = e.get("balloon")?;
                let mut args215 = Vec::new();
                let mut kw216 = Vec::new();
                args215.push(e.get("c")?);
                args215.push(Val::Int(2i64));
                args215.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(185i64));
                    s.push(Val::Int(610i64));
                    Val::tuple(s)
                });
                args215.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(210i64));
                    s.push({
                        let fun220 = e.get("z")?;
                        let mut args218 = Vec::new();
                        let mut kw219 = Vec::new();
                        args218.push(e.get("CEILING")?);
                        fun220.call(args218, kw219)?
                    });
                    Val::tuple(s)
                });
                fun217.call(args215, kw216)?
            };
            {
                let fun223 = e.get("balloon")?;
                let mut args221 = Vec::new();
                let mut kw222 = Vec::new();
                args221.push(e.get("c")?);
                args221.push(Val::Int(2i64));
                args221.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(185i64));
                    s.push(Val::Int(310i64));
                    Val::tuple(s)
                });
                args221.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(210i64));
                    s.push({
                        let fun226 = e.get("z")?;
                        let mut args224 = Vec::new();
                        let mut kw225 = Vec::new();
                        args224.push(e.get("FLOOR")?);
                        fun226.call(args224, kw225)?
                    });
                    Val::tuple(s)
                });
                fun223.call(args221, kw222)?
            };
            {
                let fun229 = e.get("balloon")?;
                let mut args227 = Vec::new();
                let mut kw228 = Vec::new();
                args227.push(e.get("c")?);
                args227.push(Val::Int(3i64));
                args227.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(352i64));
                    s.push(Val::Int(554i64));
                    Val::tuple(s)
                });
                args227.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary("mul", e.get("ROD_D")?, e.get("IN")?)?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(Val::Int(525i64));
                    Val::tuple(s)
                });
                fun229.call(args227, kw228)?
            };
            {
                let fun232 = e.get("balloon")?;
                let mut args230 = Vec::new();
                let mut kw231 = Vec::new();
                args230.push(e.get("c")?);
                args230.push(Val::Int(4i64));
                args230.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(365i64));
                    s.push(Val::Int(399i64));
                    Val::tuple(s)
                });
                args230.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "sub",
                        e.get("rod_x")?,
                        binary("truediv", e.get("float_w")?, Val::Int(2i64))?,
                    )?);
                    s.push(binary(
                        "add",
                        {
                            let fun235 = e.get("z")?;
                            let mut args233 = Vec::new();
                            let mut kw234 = Vec::new();
                            args233.push(Val::Float(2.6f64));
                            fun235.call(args233, kw234)?
                        },
                        Val::Int(20i64),
                    )?);
                    Val::tuple(s)
                });
                fun232.call(args230, kw231)?
            };
            {
                let fun238 = e.get("balloon")?;
                let mut args236 = Vec::new();
                let mut kw237 = Vec::new();
                args236.push(e.get("c")?);
                args236.push(Val::Int(5i64));
                args236.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(547i64));
                    s.push(Val::Int(609i64));
                    Val::tuple(s)
                });
                args236.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                binary(
                                    "truediv",
                                    e.get("carb")?.attr("UPPER_STOP_D")?,
                                    e.get("MM")?,
                                )?,
                                e.get("IN")?,
                            )?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(binary(
                        "add",
                        {
                            let fun241 = e.get("z")?;
                            let mut args239 = Vec::new();
                            let mut kw240 = Vec::new();
                            args239.push(e.get("stop_lo")?);
                            fun241.call(args239, kw240)?
                        },
                        Val::Int(4i64),
                    )?);
                    Val::tuple(s)
                });
                fun238.call(args236, kw237)?
            };
            {
                let fun244 = e.get("vdim")?;
                let mut args242 = Vec::new();
                let mut kw243 = Vec::new();
                args242.push(e.get("c")?);
                args242.push(Val::Int(95i64));
                args242.push(e.get("BASE")?);
                args242.push({
                    let fun247 = e.get("z")?;
                    let mut args245 = Vec::new();
                    let mut kw246 = Vec::new();
                    args245.push(e.get("LENGTH")?);
                    fun247.call(args245, kw246)?
                });
                args242.push(e.get("left")?);
                args242.push(e.get("left")?);
                args242.push({
                    let mut str248 = String::new();
                    str248.push_str(&format(
                        &e.get("LENGTH")?,
                        &val_string({
                            let mut str249 = String::new();
                            str249.push_str(".3f");
                            Val::Str(str249)
                        })?,
                    )?);
                    str248.push_str(" REF");
                    Val::Str(str248)
                });
                kw243.push(("size".into(), Val::Int(10i64)));
                fun244.call(args242, kw243)?
            };
            let assigned250 = Val::Int(250i64);
            e.set("gap_x", assigned250.clone())?;
            {
                let fun253 = e.get("line")?;
                let mut args251 = Vec::new();
                let mut kw252 = Vec::new();
                args251.push(e.get("c")?);
                args251.push(e.get("gap_x")?);
                args251.push({
                    let fun256 = e.get("z")?;
                    let mut args254 = Vec::new();
                    let mut kw255 = Vec::new();
                    args254.push(e.get("FLOOR")?);
                    fun256.call(args254, kw255)?
                });
                args251.push(e.get("gap_x")?);
                args251.push({
                    let fun259 = e.get("z")?;
                    let mut args257 = Vec::new();
                    let mut kw258 = Vec::new();
                    args257.push(e.get("CEILING")?);
                    fun259.call(args257, kw258)?
                });
                fun253.call(args251, kw252)?
            };
            {
                let fun262 = e.get("arrow")?;
                let mut args260 = Vec::new();
                let mut kw261 = Vec::new();
                args260.push(e.get("c")?);
                args260.push({
                    let mut s = Vec::new();
                    s.push(e.get("gap_x")?);
                    s.push({
                        let fun265 = e.get("z")?;
                        let mut args263 = Vec::new();
                        let mut kw264 = Vec::new();
                        args263.push(e.get("FLOOR")?);
                        fun265.call(args263, kw264)?
                    });
                    Val::tuple(s)
                });
                args260.push({
                    let mut s = Vec::new();
                    s.push(e.get("gap_x")?);
                    s.push({
                        let fun268 = e.get("z")?;
                        let mut args266 = Vec::new();
                        let mut kw267 = Vec::new();
                        args266.push(e.get("CEILING")?);
                        fun268.call(args266, kw267)?
                    });
                    Val::tuple(s)
                });
                fun262.call(args260, kw261)?
            };
            {
                let fun271 = e.get("arrow")?;
                let mut args269 = Vec::new();
                let mut kw270 = Vec::new();
                args269.push(e.get("c")?);
                args269.push({
                    let mut s = Vec::new();
                    s.push(e.get("gap_x")?);
                    s.push({
                        let fun274 = e.get("z")?;
                        let mut args272 = Vec::new();
                        let mut kw273 = Vec::new();
                        args272.push(e.get("CEILING")?);
                        fun274.call(args272, kw273)?
                    });
                    Val::tuple(s)
                });
                args269.push({
                    let mut s = Vec::new();
                    s.push(e.get("gap_x")?);
                    s.push({
                        let fun277 = e.get("z")?;
                        let mut args275 = Vec::new();
                        let mut kw276 = Vec::new();
                        args275.push(e.get("FLOOR")?);
                        fun277.call(args275, kw276)?
                    });
                    Val::tuple(s)
                });
                fun271.call(args269, kw270)?
            };
            {
                let fun280 = e.get("text")?;
                let mut args278 = Vec::new();
                let mut kw279 = Vec::new();
                args278.push(e.get("c")?);
                args278.push(binary("sub", e.get("gap_x")?, Val::Int(9i64))?);
                args278.push({
                    let fun283 = e.get("z")?;
                    let mut args281 = Vec::new();
                    let mut kw282 = Vec::new();
                    args281.push(binary(
                        "truediv",
                        binary("add", e.get("FLOOR")?, e.get("CEILING")?)?,
                        Val::Int(2i64),
                    )?);
                    fun283.call(args281, kw282)?
                });
                args278.push({
                    let mut str284 = String::new();
                    str284.push_str(&format(
                        &e.get("INSIDE_SPAN")?,
                        &val_string({
                            let mut str285 = String::new();
                            str285.push_str(".3f");
                            Val::Str(str285)
                        })?,
                    )?);
                    str284.push_str(" ±");
                    str284.push_str(&format(
                        &e.get("INSIDE_SPAN_TOL")?,
                        &val_string({
                            let mut str286 = String::new();
                            str286.push_str(".3f");
                            Val::Str(str286)
                        })?,
                    )?);
                    Val::Str(str284)
                });
                args278.push(Val::Int(10i64));
                kw279.push(("align".into(), Val::Str("right".into())));
                fun280.call(args278, kw279)?
            };
            {
                let fun289 = e.get("text")?;
                let mut args287 = Vec::new();
                let mut kw288 = Vec::new();
                args287.push(e.get("c")?);
                args287.push(binary("sub", e.get("gap_x")?, Val::Int(9i64))?);
                args287.push(binary(
                    "sub",
                    {
                        let fun292 = e.get("z")?;
                        let mut args290 = Vec::new();
                        let mut kw291 = Vec::new();
                        args290.push(binary(
                            "truediv",
                            binary("add", e.get("FLOOR")?, e.get("CEILING")?)?,
                            Val::Int(2i64),
                        )?);
                        fun292.call(args290, kw291)?
                    },
                    Val::Int(14i64),
                )?);
                args287.push(Val::Str("CAP SPAN AT R1".into()));
                args287.push(Val::Int(8i64));
                kw288.push(("align".into(), Val::Str("right".into())));
                fun289.call(args287, kw288)?
            };
            {
                let fun295 = e.get("c")?.attr("setLineWidth")?;
                let mut args293 = Vec::new();
                let mut kw294 = Vec::new();
                args293.push(Val::Float(0.5f64));
                fun295.call(args293, kw294)?
            };
            {
                let fun298 = e.get("c")?.attr("circle")?;
                let mut args296 = Vec::new();
                let mut kw297 = Vec::new();
                args296.push(binary("sub", e.get("bore_r")?, Val::Int(2i64))?);
                args296.push(binary(
                    "add",
                    {
                        let fun301 = e.get("z")?;
                        let mut args299 = Vec::new();
                        let mut kw300 = Vec::new();
                        args299.push(binary("sub", e.get("LENGTH")?, e.get("RECESS")?)?);
                        fun301.call(args299, kw300)?
                    },
                    Val::Int(2i64),
                )?);
                args296.push(Val::Int(23i64));
                kw297.push(("stroke".into(), Val::Int(1i64)));
                kw297.push(("fill".into(), Val::Int(0i64)));
                fun298.call(args296, kw297)?
            };
            {
                let fun304 = e.get("line")?;
                let mut args302 = Vec::new();
                let mut kw303 = Vec::new();
                args302.push(e.get("c")?);
                args302.push(binary("add", e.get("bore_r")?, Val::Int(13i64))?);
                args302.push(binary(
                    "add",
                    {
                        let fun307 = e.get("z")?;
                        let mut args305 = Vec::new();
                        let mut kw306 = Vec::new();
                        args305.push(binary("sub", e.get("LENGTH")?, e.get("RECESS")?)?);
                        fun307.call(args305, kw306)?
                    },
                    Val::Int(19i64),
                )?);
                args302.push(Val::Int(546i64));
                args302.push(Val::Int(708i64));
                fun304.call(args302, kw303)?
            };
            {
                let fun310 = e.get("text")?;
                let mut args308 = Vec::new();
                let mut kw309 = Vec::new();
                args308.push(e.get("c")?);
                args308.push(Val::Int(551i64));
                args308.push(Val::Int(710i64));
                args308.push(Val::Str("B".into()));
                args308.push(Val::Int(12i64));
                kw309.push(("bold".into(), Val::Bool(true)));
                fun310.call(args308, kw309)?
            };
            {
                let fun313 = e.get("leader")?;
                let mut args311 = Vec::new();
                let mut kw312 = Vec::new();
                args311.push(e.get("c")?);
                args311.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("rod_x")?,
                        binary(
                            "truediv",
                            binary("mul", e.get("ROD_D")?, e.get("IN")?)?,
                            Val::Int(2i64),
                        )?,
                    )?);
                    s.push(Val::Int(580i64));
                    Val::tuple(s)
                });
                args311.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(525i64));
                    s.push(Val::Int(550i64));
                    Val::tuple(s)
                });
                args311.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(545i64));
                    s.push(Val::Int(550i64));
                    Val::tuple(s)
                });
                args311.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("FINISHED ROD".into()));
                    s.push(Val::Str("PER FR-CARB-01".into()));
                    Val::list(s)
                });
                args311.push(Val::Float(8.5f64));
                fun313.call(args311, kw312)?
            };
            let assigned314 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("rod_x")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("ROD_D")?, e.get("IN")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                s.push({
                    let fun317 = e.get("z")?;
                    let mut args315 = Vec::new();
                    let mut kw316 = Vec::new();
                    args315.push(e.get("FLOOR")?);
                    fun317.call(args315, kw316)?
                });
                Val::tuple(s)
            };
            e.set("tack_tip", assigned314.clone())?;
            let assigned318 = {
                let fun321 = e.get("path_from_points")?;
                let mut args319 = Vec::new();
                let mut kw320 = Vec::new();
                args319.push(e.get("c")?);
                args319.push({
                    let mut s = Vec::new();
                    s.push(e.get("tack_tip")?);
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("tack_tip")?.get(Val::Int(0i64))?,
                            Val::Float(2.5f64),
                        )?);
                        s.push(e.get("tack_tip")?.get(Val::Int(1i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("tack_tip")?.get(Val::Int(0i64))?);
                        s.push(binary(
                            "add",
                            e.get("tack_tip")?.get(Val::Int(1i64))?,
                            Val::Float(2.5f64),
                        )?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun321.call(args319, kw320)?
            };
            e.set("tack", assigned318.clone())?;
            {
                let fun324 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args322 = Vec::new();
                let mut kw323 = Vec::new();
                args322.push(Val::Float(0.85f64));
                args322.push(Val::Float(0.85f64));
                args322.push(Val::Float(0.85f64));
                fun324.call(args322, kw323)?
            };
            {
                let fun327 = e.get("c")?.attr("drawPath")?;
                let mut args325 = Vec::new();
                let mut kw326 = Vec::new();
                args325.push(e.get("tack")?);
                kw326.push(("fill".into(), Val::Int(1i64)));
                kw326.push(("stroke".into(), Val::Int(1i64)));
                fun327.call(args325, kw326)?
            };
            {
                let fun330 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args328 = Vec::new();
                let mut kw329 = Vec::new();
                args328.push(Val::Int(0i64));
                args328.push(Val::Int(0i64));
                args328.push(Val::Int(0i64));
                fun330.call(args328, kw329)?
            };
            {
                let fun333 = e.get("leader")?;
                let mut args331 = Vec::new();
                let mut kw332 = Vec::new();
                args331.push(e.get("c")?);
                args331.push({
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("tack_tip")?.get(Val::Int(0i64))?,
                        Val::Int(1i64),
                    )?);
                    s.push(binary(
                        "add",
                        e.get("tack_tip")?.get(Val::Int(1i64))?,
                        Val::Int(1i64),
                    )?);
                    Val::tuple(s)
                });
                args331.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(525i64));
                    s.push(Val::Int(320i64));
                    Val::tuple(s)
                });
                args331.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(545i64));
                    s.push(Val::Int(320i64));
                    Val::tuple(s)
                });
                args331.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("T1 - ROD TACK".into()));
                    s.push(Val::Str("BOTTOM CAP ONLY".into()));
                    Val::list(s)
                });
                args331.push(Val::Float(8.5f64));
                fun333.call(args331, kw332)?
            };
            {
                let fun336 = e.get("text")?;
                let mut args334 = Vec::new();
                let mut kw335 = Vec::new();
                args334.push(e.get("c")?);
                args334.push(e.get("CX")?);
                args334.push(Val::Int(211i64));
                args334.push(Val::Str(
                    "FIXED-LENGTH ROD SEATS IN BOTTOM REGISTER; TOP REGISTER RETAINS CLEARANCE."
                        .into(),
                ));
                args334.push(Val::Int(8i64));
                kw335.push(("align".into(), Val::Str("center".into())));
                fun336.call(args334, kw335)?
            };
            {
                let fun339 = e.get("text")?;
                let mut args337 = Vec::new();
                let mut kw338 = Vec::new();
                args337.push(e.get("c")?);
                args337.push(e.get("CX")?);
                args337.push(Val::Int(197i64));
                args337.push(Val::Str(
                    "PORTS AND ROD SHARE THIS PLANE. FLOAT ENVELOPE IS REFERENCE ONLY.".into(),
                ));
                args337.push(Val::Int(8i64));
                kw338.push(("align".into(), Val::Str("center".into())));
                fun339.call(args337, kw338)?
            };
            Ok(Val::None)
        })
    })?;
    // outside_end_view
    e.set("outside_end_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned340 = {
                let mut s = Vec::new();
                s.push(Val::Int(780i64));
                s.push(Val::Int(613i64));
                s.push(binary("truediv", e.get("IN")?, Val::Int(2i64))?);
                Val::tuple(s)
            };
            let unpack341 = unpack(assigned340.clone(), 3)?;
            e.set("x", unpack341[0].clone())?;
            e.set("y", unpack341[1].clone())?;
            e.set("s", unpack341[2].clone())?;
            {
                let fun344 = e.get("text")?;
                let mut args342 = Vec::new();
                let mut kw343 = Vec::new();
                args342.push(e.get("c")?);
                args342.push(e.get("x")?);
                args342.push(Val::Int(750i64));
                args342.push(Val::Str("TOP OUTSIDE END VIEW".into()));
                args342.push(Val::Int(11i64));
                kw343.push(("bold".into(), Val::Bool(true)));
                kw343.push(("align".into(), Val::Str("center".into())));
                fun344.call(args342, kw343)?
            };
            {
                let fun347 = e.get("text")?;
                let mut args345 = Vec::new();
                let mut kw346 = Vec::new();
                args345.push(e.get("c")?);
                args345.push(e.get("x")?);
                args345.push(Val::Int(733i64));
                args345.push(Val::Str("LOOKING DOWN -Z - SCALE 1:2".into()));
                args345.push(Val::Float(8.5f64));
                kw346.push(("align".into(), Val::Str("center".into())));
                fun347.call(args345, kw346)?
            };
            {
                let fun350 = e.get("c")?.attr("setLineWidth")?;
                let mut args348 = Vec::new();
                let mut kw349 = Vec::new();
                args348.push(e.get("VISIBLE")?);
                fun350.call(args348, kw349)?
            };
            {
                let fun353 = e.get("c")?.attr("circle")?;
                let mut args351 = Vec::new();
                let mut kw352 = Vec::new();
                args351.push(e.get("x")?);
                args351.push(e.get("y")?);
                args351.push(binary(
                    "truediv",
                    binary("mul", e.get("OD")?, e.get("s")?)?,
                    Val::Int(2i64),
                )?);
                kw352.push(("stroke".into(), Val::Int(1i64)));
                kw352.push(("fill".into(), Val::Int(0i64)));
                fun353.call(args351, kw352)?
            };
            {
                let fun356 = e.get("c")?.attr("setLineWidth")?;
                let mut args354 = Vec::new();
                let mut kw355 = Vec::new();
                args354.push(e.get("THIN")?);
                fun356.call(args354, kw355)?
            };
            {
                let fun359 = e.get("c")?.attr("circle")?;
                let mut args357 = Vec::new();
                let mut kw358 = Vec::new();
                args357.push(e.get("x")?);
                args357.push(e.get("y")?);
                args357.push(binary(
                    "truediv",
                    binary("mul", e.get("ID")?, e.get("s")?)?,
                    Val::Int(2i64),
                )?);
                kw358.push(("stroke".into(), Val::Int(1i64)));
                kw358.push(("fill".into(), Val::Int(0i64)));
                fun359.call(args357, kw358)?
            };
            {
                let fun362 = e.get("line")?;
                let mut args360 = Vec::new();
                let mut kw361 = Vec::new();
                args360.push(e.get("c")?);
                args360.push(binary("sub", e.get("x")?, Val::Int(101i64))?);
                args360.push(e.get("y")?);
                args360.push(binary("add", e.get("x")?, Val::Int(101i64))?);
                args360.push(e.get("y")?);
                kw361.push(("dash".into(), e.get("CENTER_DASH")?));
                fun362.call(args360, kw361)?
            };
            {
                let fun365 = e.get("line")?;
                let mut args363 = Vec::new();
                let mut kw364 = Vec::new();
                args363.push(e.get("c")?);
                args363.push(e.get("x")?);
                args363.push(binary("sub", e.get("y")?, Val::Int(101i64))?);
                args363.push(e.get("x")?);
                args363.push(binary("add", e.get("y")?, Val::Int(101i64))?);
                kw364.push(("dash".into(), e.get("CENTER_DASH")?));
                fun365.call(args363, kw364)?
            };
            let assigned366 = binary("mul", e.get("cap")?.attr("hole_radius")?, e.get("s")?)?;
            e.set("port_r", assigned366.clone())?;
            for item367 in {
                let mut s = Vec::new();
                s.push(unary("neg", Val::Int(1i64))?);
                s.push(Val::Int(1i64));
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("sign", item367)?;
                let assigned368 = binary(
                    "add",
                    e.get("y")?,
                    binary(
                        "mul",
                        binary(
                            "truediv",
                            binary(
                                "mul",
                                e.get("sign")?,
                                e.get("carb")?.attr("carbonator_port_offset")?,
                            )?,
                            e.get("MM")?,
                        )?,
                        e.get("s")?,
                    )?,
                )?;
                e.set("py", assigned368.clone())?;
                {
                    let fun371 = e.get("c")?.attr("setLineWidth")?;
                    let mut args369 = Vec::new();
                    let mut kw370 = Vec::new();
                    args369.push(e.get("VISIBLE")?);
                    fun371.call(args369, kw370)?
                };
                {
                    let fun374 = e.get("c")?.attr("circle")?;
                    let mut args372 = Vec::new();
                    let mut kw373 = Vec::new();
                    args372.push(e.get("x")?);
                    args372.push(e.get("py")?);
                    args372.push(e.get("port_r")?);
                    kw373.push(("stroke".into(), Val::Int(1i64)));
                    kw373.push(("fill".into(), Val::Int(0i64)));
                    fun374.call(args372, kw373)?
                };
                {
                    let fun377 = e.get("c")?.attr("setLineWidth")?;
                    let mut args375 = Vec::new();
                    let mut kw376 = Vec::new();
                    args375.push(e.get("THIN")?);
                    fun377.call(args375, kw376)?
                };
                {
                    let fun380 = e.get("c")?.attr("arc")?;
                    let mut args378 = Vec::new();
                    let mut kw379 = Vec::new();
                    args378.push(binary(
                        "sub",
                        binary("sub", e.get("x")?, e.get("port_r")?)?,
                        Val::Float(1.5f64),
                    )?);
                    args378.push(binary(
                        "sub",
                        binary("sub", e.get("py")?, e.get("port_r")?)?,
                        Val::Float(1.5f64),
                    )?);
                    args378.push(binary(
                        "add",
                        binary("add", e.get("x")?, e.get("port_r")?)?,
                        Val::Float(1.5f64),
                    )?);
                    args378.push(binary(
                        "add",
                        binary("add", e.get("py")?, e.get("port_r")?)?,
                        Val::Float(1.5f64),
                    )?);
                    args378.push(Val::Int(35i64));
                    args378.push(Val::Int(270i64));
                    fun380.call(args378, kw379)?
                };
                {
                    let fun383 = e.get("center")?;
                    let mut args381 = Vec::new();
                    let mut kw382 = Vec::new();
                    args381.push(e.get("c")?);
                    args381.push(e.get("x")?);
                    args381.push(e.get("py")?);
                    args381.push(Val::Int(13i64));
                    fun383.call(args381, kw382)?
                };
            }
            let assigned384 = {
                let mut s = Vec::new();
                s.push(e.get("x")?);
                s.push(binary(
                    "sub",
                    e.get("y")?,
                    binary("mul", e.get("ROD_RADIUS")?, e.get("s")?)?,
                )?);
                Val::tuple(s)
            };
            let unpack385 = unpack(assigned384.clone(), 2)?;
            e.set("rx", unpack385[0].clone())?;
            e.set("ry", unpack385[1].clone())?;
            {
                let fun388 = e.get("c")?.attr("setDash")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(3i64));
                    s.push(Val::Int(2i64));
                    Val::tuple(s)
                });
                fun388.call(args386, kw387)?
            };
            {
                let fun391 = e.get("c")?.attr("circle")?;
                let mut args389 = Vec::new();
                let mut kw390 = Vec::new();
                args389.push(e.get("rx")?);
                args389.push(e.get("ry")?);
                args389.push(binary(
                    "truediv",
                    binary("mul", e.get("REG_D")?, e.get("s")?)?,
                    Val::Int(2i64),
                )?);
                kw390.push(("stroke".into(), Val::Int(1i64)));
                kw390.push(("fill".into(), Val::Int(0i64)));
                fun391.call(args389, kw390)?
            };
            {
                let fun394 = e.get("c")?.attr("setDash")?;
                let mut args392 = Vec::new();
                let mut kw393 = Vec::new();
                fun394.call(args392, kw393)?
            };
            {
                let fun397 = e.get("center")?;
                let mut args395 = Vec::new();
                let mut kw396 = Vec::new();
                args395.push(e.get("c")?);
                args395.push(e.get("rx")?);
                args395.push(e.get("ry")?);
                args395.push(Val::Int(8i64));
                fun397.call(args395, kw396)?
            };
            {
                let fun400 = e.get("line")?;
                let mut args398 = Vec::new();
                let mut kw399 = Vec::new();
                args398.push(e.get("c")?);
                args398.push(e.get("x")?);
                args398.push(binary("sub", e.get("y")?, Val::Int(103i64))?);
                args398.push(e.get("x")?);
                args398.push(binary("add", e.get("y")?, Val::Int(103i64))?);
                kw399.push(("dash".into(), {
                    let mut s = Vec::new();
                    s.push(Val::Int(15i64));
                    s.push(Val::Int(3i64));
                    s.push(Val::Int(3i64));
                    s.push(Val::Int(3i64));
                    Val::tuple(s)
                }));
                fun400.call(args398, kw399)?
            };
            for item401 in {
                let mut s = Vec::new();
                s.push(binary("sub", e.get("y")?, Val::Int(103i64))?);
                s.push(binary("add", e.get("y")?, Val::Int(103i64))?);
                Val::tuple(s)
            }
            .iter()?
            {
                e.set("ey", item401)?;
                {
                    let fun404 = e.get("line")?;
                    let mut args402 = Vec::new();
                    let mut kw403 = Vec::new();
                    args402.push(e.get("c")?);
                    args402.push(e.get("x")?);
                    args402.push(e.get("ey")?);
                    args402.push(binary("sub", e.get("x")?, Val::Int(18i64))?);
                    args402.push(e.get("ey")?);
                    args402.push(e.get("VISIBLE")?);
                    fun404.call(args402, kw403)?
                };
                {
                    let fun407 = e.get("arrow")?;
                    let mut args405 = Vec::new();
                    let mut kw406 = Vec::new();
                    args405.push(e.get("c")?);
                    args405.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("ey")?);
                        Val::tuple(s)
                    });
                    args405.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("x")?, Val::Int(18i64))?);
                        s.push(e.get("ey")?);
                        Val::tuple(s)
                    });
                    fun407.call(args405, kw406)?
                };
                {
                    let fun410 = e.get("text")?;
                    let mut args408 = Vec::new();
                    let mut kw409 = Vec::new();
                    args408.push(e.get("c")?);
                    args408.push(binary("sub", e.get("x")?, Val::Int(23i64))?);
                    args408.push(binary("sub", e.get("ey")?, Val::Int(3i64))?);
                    args408.push(Val::Str("A".into()));
                    args408.push(Val::Int(10i64));
                    kw409.push(("bold".into(), Val::Bool(true)));
                    kw409.push(("align".into(), Val::Str("right".into())));
                    fun410.call(args408, kw409)?
                };
            }
            {
                let fun413 = e.get("text")?;
                let mut args411 = Vec::new();
                let mut kw412 = Vec::new();
                args411.push(e.get("c")?);
                args411.push(binary("add", e.get("x")?, Val::Int(9i64))?);
                args411.push(binary("add", e.get("y")?, Val::Int(104i64))?);
                args411.push(Val::Str("+Y".into()));
                args411.push(Val::Int(8i64));
                fun413.call(args411, kw412)?
            };
            {
                let fun416 = e.get("text")?;
                let mut args414 = Vec::new();
                let mut kw415 = Vec::new();
                args414.push(e.get("c")?);
                args414.push(binary("add", e.get("rx")?, Val::Int(14i64))?);
                args414.push(binary("sub", e.get("ry")?, Val::Int(3i64))?);
                args414.push(Val::Str("R1".into()));
                args414.push(Val::Int(8i64));
                kw415.push(("bold".into(), Val::Bool(true)));
                fun416.call(args414, kw415)?
            };
            {
                let fun419 = e.get("horizontal_dimension")?;
                let mut args417 = Vec::new();
                let mut kw418 = Vec::new();
                args417.push(e.get("c")?);
                args417.push(binary(
                    "sub",
                    e.get("x")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("OD")?, e.get("s")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                args417.push(binary(
                    "add",
                    e.get("x")?,
                    binary(
                        "truediv",
                        binary("mul", e.get("OD")?, e.get("s")?)?,
                        Val::Int(2i64),
                    )?,
                )?);
                args417.push(e.get("y")?);
                args417.push(Val::Int(496i64));
                args417.push({
                    let mut str420 = String::new();
                    str420.push_str("Ø");
                    str420.push_str(&format(
                        &e.get("OD")?,
                        &val_string({
                            let mut str421 = String::new();
                            str421.push_str(".3f");
                            Val::Str(str421)
                        })?,
                    )?);
                    str420.push_str(" REF");
                    Val::Str(str420)
                });
                args417.push(Val::Int(9i64));
                fun419.call(args417, kw418)?
            };
            {
                let fun424 = e.get("text")?;
                let mut args422 = Vec::new();
                let mut kw423 = Vec::new();
                args422.push(e.get("c")?);
                args422.push(e.get("x")?);
                args422.push(Val::Int(481i64));
                args422.push(Val::Str(
                    "BOTH R1 REGISTERS ON -Y; BOTH PORT PAIRS ON ±Y.".into(),
                ));
                args422.push(Val::Float(7.7f64));
                kw423.push(("align".into(), Val::Str("center".into())));
                fun424.call(args422, kw423)?
            };
            Ok(Val::None)
        })
    })?;
    // closure_detail
    e.set("closure_detail", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned425 = {
                let mut s = Vec::new();
                s.push(Val::Int(1050i64));
                s.push(Val::Int(701i64));
                s.push(binary("mul", Val::Int(4i64), e.get("IN")?)?);
                Val::tuple(s)
            };
            let unpack426 = unpack(assigned425.clone(), 3)?;
            e.set("x", unpack426[0].clone())?;
            e.set("rim", unpack426[1].clone())?;
            e.set("s", unpack426[2].clone())?;
            let assigned427 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("rim")?,
                    binary("mul", e.get("RECESS")?, e.get("s")?)?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("rim")?,
                    binary(
                        "mul",
                        binary("add", e.get("RECESS")?, e.get("CAP_T")?)?,
                        e.get("s")?,
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack428 = unpack(assigned427.clone(), 2)?;
            e.set("outside", unpack428[0].clone())?;
            e.set("inside", unpack428[1].clone())?;
            let assigned429 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("x")?,
                    binary("mul", e.get("WALL")?, e.get("s")?)?,
                )?);
                s.push(binary(
                    "sub",
                    e.get("x")?,
                    binary(
                        "mul",
                        binary(
                            "truediv",
                            binary("sub", e.get("ID")?, e.get("CAP_D")?)?,
                            Val::Int(2i64),
                        )?,
                        e.get("s")?,
                    )?,
                )?);
                Val::tuple(s)
            };
            let unpack430 = unpack(assigned429.clone(), 2)?;
            e.set("wall_right", unpack430[0].clone())?;
            e.set("cap_edge", unpack430[1].clone())?;
            {
                let fun433 = e.get("text")?;
                let mut args431 = Vec::new();
                let mut kw432 = Vec::new();
                args431.push(e.get("c")?);
                args431.push(Val::Int(1050i64));
                args431.push(Val::Int(750i64));
                args431.push(Val::Str("DETAIL B - CLOSURE JOINT".into()));
                args431.push(Val::Float(10.5f64));
                kw432.push(("bold".into(), Val::Bool(true)));
                kw432.push(("align".into(), Val::Str("center".into())));
                fun433.call(args431, kw432)?
            };
            {
                let fun436 = e.get("text")?;
                let mut args434 = Vec::new();
                let mut kw435 = Vec::new();
                args434.push(e.get("c")?);
                args434.push(Val::Int(1050i64));
                args434.push(Val::Int(733i64));
                args434.push(Val::Str("SCALE 4:1 - LOWER END MIRRORED".into()));
                args434.push(Val::Float(8.3f64));
                kw435.push(("align".into(), Val::Str("center".into())));
                fun436.call(args434, kw435)?
            };
            {
                let fun439 = e.get("section_material")?;
                let mut args437 = Vec::new();
                let mut kw438 = Vec::new();
                args437.push(e.get("c")?);
                args437.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("rim")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("wall_right")?);
                        s.push(e.get("rim")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("wall_right")?);
                        s.push(binary("sub", e.get("inside")?, Val::Int(22i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "mul",
                                binary("mul", e.get("WALL")?, e.get("s")?)?,
                                Val::Float(0.66f64),
                            )?,
                        )?);
                        s.push(binary("sub", e.get("inside")?, Val::Int(19i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary(
                            "add",
                            e.get("x")?,
                            binary(
                                "mul",
                                binary("mul", e.get("WALL")?, e.get("s")?)?,
                                Val::Float(0.33f64),
                            )?,
                        )?);
                        s.push(binary("sub", e.get("inside")?, Val::Int(25i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(binary("sub", e.get("inside")?, Val::Int(22i64))?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                kw438.push(("spacing".into(), Val::Int(8i64)));
                fun439.call(args437, kw438)?
            };
            let assigned440 = binary("sub", e.get("x")?, Val::Int(76i64))?;
            e.set("cap_left", assigned440.clone())?;
            {
                let fun443 = e.get("section_material")?;
                let mut args441 = Vec::new();
                let mut kw442 = Vec::new();
                args441.push(e.get("c")?);
                args441.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("cap_left")?);
                        s.push(e.get("outside")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("cap_edge")?);
                        s.push(e.get("outside")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("cap_edge")?);
                        s.push(e.get("inside")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("cap_left")?);
                        s.push(e.get("inside")?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("cap_left")?, Val::Int(3i64))?);
                        s.push(binary("add", e.get("inside")?, Val::Int(20i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("cap_left")?, Val::Int(3i64))?);
                        s.push(binary("add", e.get("inside")?, Val::Int(29i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("add", e.get("cap_left")?, Val::Int(3i64))?);
                        s.push(binary("add", e.get("inside")?, Val::Int(38i64))?);
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("cap_left")?);
                        s.push(binary("add", e.get("inside")?, Val::Int(45i64))?);
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                kw442.push(("spacing".into(), Val::Int(7i64)));
                kw442.push(("reverse".into(), Val::Bool(true)));
                fun443.call(args441, kw442)?
            };
            let assigned444 = {
                let fun447 = e.get("c")?.attr("beginPath")?;
                let mut args445 = Vec::new();
                let mut kw446 = Vec::new();
                fun447.call(args445, kw446)?
            };
            e.set("p", assigned444.clone())?;
            {
                let fun450 = e.get("p")?.attr("moveTo")?;
                let mut args448 = Vec::new();
                let mut kw449 = Vec::new();
                args448.push(binary("sub", e.get("x")?, Val::Int(20i64))?);
                args448.push(e.get("outside")?);
                fun450.call(args448, kw449)?
            };
            {
                let fun453 = e.get("p")?.attr("curveTo")?;
                let mut args451 = Vec::new();
                let mut kw452 = Vec::new();
                args451.push(binary("sub", e.get("x")?, Val::Int(8i64))?);
                args451.push(binary("add", e.get("outside")?, Val::Int(2i64))?);
                args451.push(binary("sub", e.get("x")?, Val::Int(2i64))?);
                args451.push(binary("add", e.get("outside")?, Val::Int(8i64))?);
                args451.push(e.get("x")?);
                args451.push(binary("add", e.get("outside")?, Val::Int(20i64))?);
                fun453.call(args451, kw452)?
            };
            {
                let fun456 = e.get("p")?.attr("lineTo")?;
                let mut args454 = Vec::new();
                let mut kw455 = Vec::new();
                args454.push(e.get("x")?);
                args454.push(e.get("outside")?);
                fun456.call(args454, kw455)?
            };
            {
                let fun459 = e.get("p")?.attr("close")?;
                let mut args457 = Vec::new();
                let mut kw458 = Vec::new();
                fun459.call(args457, kw458)?
            };
            {
                let fun462 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args460 = Vec::new();
                let mut kw461 = Vec::new();
                args460.push(Val::Float(0.85f64));
                args460.push(Val::Float(0.85f64));
                args460.push(Val::Float(0.85f64));
                fun462.call(args460, kw461)?
            };
            {
                let fun465 = e.get("c")?.attr("setLineWidth")?;
                let mut args463 = Vec::new();
                let mut kw464 = Vec::new();
                args463.push(Val::Float(0.7f64));
                fun465.call(args463, kw464)?
            };
            {
                let fun468 = e.get("c")?.attr("drawPath")?;
                let mut args466 = Vec::new();
                let mut kw467 = Vec::new();
                args466.push(e.get("p")?);
                kw467.push(("fill".into(), Val::Int(1i64)));
                kw467.push(("stroke".into(), Val::Int(1i64)));
                fun468.call(args466, kw467)?
            };
            {
                let fun471 = e.get("c")?.attr("setFillColorRGB")?;
                let mut args469 = Vec::new();
                let mut kw470 = Vec::new();
                args469.push(Val::Int(0i64));
                args469.push(Val::Int(0i64));
                args469.push(Val::Int(0i64));
                fun471.call(args469, kw470)?
            };
            {
                let fun474 = e.get("vdim")?;
                let mut args472 = Vec::new();
                let mut kw473 = Vec::new();
                args472.push(e.get("c")?);
                args472.push(Val::Int(947i64));
                args472.push(e.get("outside")?);
                args472.push(e.get("rim")?);
                args472.push(e.get("cap_left")?);
                args472.push(e.get("x")?);
                args472.push({
                    let mut str475 = String::new();
                    str475.push_str("2X ");
                    str475.push_str(&format(
                        &e.get("RECESS")?,
                        &val_string({
                            let mut str476 = String::new();
                            str476.push_str(".3f");
                            Val::Str(str476)
                        })?,
                    )?);
                    Val::Str(str475)
                });
                fun474.call(args472, kw473)?
            };
            {
                let fun479 = e.get("leader")?;
                let mut args477 = Vec::new();
                let mut kw478 = Vec::new();
                args477.push(e.get("c")?);
                args477.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, Val::Int(11i64))?);
                    s.push(binary("add", e.get("outside")?, Val::Int(6i64))?);
                    Val::tuple(s)
                });
                args477.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1094i64));
                    s.push(Val::Int(583i64));
                    Val::tuple(s)
                });
                args477.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(1114i64));
                    s.push(Val::Int(583i64));
                    Val::tuple(s)
                });
                args477.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("W1 - FILLET".into()));
                    s.push(Val::Str("BOTH ENDS".into()));
                    Val::list(s)
                });
                args477.push(Val::Float(8.5f64));
                fun479.call(args477, kw478)?
            };
            {
                let fun482 = e.get("text")?;
                let mut args480 = Vec::new();
                let mut kw481 = Vec::new();
                args480.push(e.get("c")?);
                args480.push(Val::Int(1050i64));
                args480.push(Val::Int(507i64));
                args480.push(Val::Str(
                    "WELD PROFILE DIAGRAMMATIC; SIZE NOT ESTABLISHED.".into(),
                ));
                args480.push(Val::Float(7.8f64));
                kw481.push(("align".into(), Val::Str("center".into())));
                fun482.call(args480, kw481)?
            };
            {
                let fun485 = e.get("text")?;
                let mut args483 = Vec::new();
                let mut kw484 = Vec::new();
                args483.push(e.get("c")?);
                args483.push(Val::Int(1050i64));
                args483.push(Val::Int(493i64));
                args483.push(Val::Str(
                    "CAP OD / BORE SLIP GAP SHOWN; DO NOT CHAMFER WELD ROOT.".into(),
                ));
                args483.push(Val::Float(7.5f64));
                kw484.push(("align".into(), Val::Str("center".into())));
                fun485.call(args483, kw484)?
            };
            Ok(Val::None)
        })
    })?;
    // parts_list
    e.set("parts_list", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned486 = {
                let mut s = Vec::new();
                s.push(Val::Int(650i64));
                s.push(Val::Int(1177i64));
                s.push(Val::Int(452i64));
                s.push(Val::Int(19i64));
                Val::tuple(s)
            };
            let unpack487 = unpack(assigned486.clone(), 4)?;
            e.set("left", unpack487[0].clone())?;
            e.set("right", unpack487[1].clone())?;
            e.set("top", unpack487[2].clone())?;
            e.set("height", unpack487[3].clone())?;
            let assigned488 = {
                let mut s = Vec::new();
                s.push(e.get("left")?);
                s.push(Val::Int(681i64));
                s.push(Val::Int(715i64));
                s.push(Val::Int(797i64));
                s.push(e.get("right")?);
                Val::tuple(s)
            };
            e.set("columns", assigned488.clone())?;
            {
                let fun491 = e.get("text")?;
                let mut args489 = Vec::new();
                let mut kw490 = Vec::new();
                args489.push(e.get("c")?);
                args489.push(e.get("left")?);
                args489.push(binary("add", e.get("top")?, Val::Int(13i64))?);
                args489.push(Val::Str("PARTS AT CLOSURE".into()));
                args489.push(Val::Int(10i64));
                kw490.push(("bold".into(), Val::Bool(true)));
                fun491.call(args489, kw490)?
            };
            let assigned492 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("ITEM".into()));
                    s.push(Val::Str("QTY".into()));
                    s.push(Val::Str("MATERIAL".into()));
                    s.push(Val::Str("DESCRIPTION / DEFINITION".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("1".into()));
                    s.push(Val::Str("1".into()));
                    s.push(Val::Str("HSM-000008".into()));
                    s.push({
                        let mut str493 = String::new();
                        str493.push_str("316 SS TUBE; Ø");
                        str493.push_str(&format(
                            &e.get("OD")?,
                            &val_string({
                                let mut str494 = String::new();
                                str494.push_str(".3f");
                                Val::Str(str494)
                            })?,
                        )?);
                        str493.push_str(" x ");
                        str493.push_str(&format(
                            &e.get("WALL")?,
                            &val_string({
                                let mut str495 = String::new();
                                str495.push_str(".3f");
                                Val::Str(str495)
                            })?,
                        )?);
                        str493.push_str(" WALL x ");
                        str493.push_str(&format(
                            &e.get("LENGTH")?,
                            &val_string({
                                let mut str496 = String::new();
                                str496.push_str(".3f");
                                Val::Str(str496)
                            })?,
                        )?);
                        Val::Str(str493)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("2".into()));
                    s.push(Val::Str("2".into()));
                    s.push(Val::Str("HSM-000009".into()));
                    s.push(Val::Str("316 SS FINISHED END CAP; END-CAP-01".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("3".into()));
                    s.push(Val::Str("1".into()));
                    s.push(Val::Str("HSM-000336".into()));
                    s.push(Val::Str("316 SS FLOAT GUIDE ROD; FR-CARB-01".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("4".into()));
                    s.push(Val::Str("1".into()));
                    s.push(Val::Str("HSM-000032".into()));
                    s.push(Val::Str(
                        "ASA AERO MAGNETIC FLOAT; INSTALL BEFORE CLOSURE".into(),
                    ));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("5".into()));
                    s.push(Val::Str("1".into()));
                    s.push(Val::Str("316 SS".into()));
                    s.push(Val::Str("UPPER FLOAT STOP; DEFINITION IN NOTE 5".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("rows", assigned492.clone())?;
            {
                let fun499 = e.get("c")?.attr("setLineWidth")?;
                let mut args497 = Vec::new();
                let mut kw498 = Vec::new();
                args497.push(e.get("THIN")?);
                fun499.call(args497, kw498)?
            };
            {
                let fun502 = e.get("c")?.attr("rect")?;
                let mut args500 = Vec::new();
                let mut kw501 = Vec::new();
                args500.push(e.get("left")?);
                args500.push(binary(
                    "sub",
                    e.get("top")?,
                    binary(
                        "mul",
                        {
                            let fun505 = e.get("len")?;
                            let mut args503 = Vec::new();
                            let mut kw504 = Vec::new();
                            args503.push(e.get("rows")?);
                            fun505.call(args503, kw504)?
                        },
                        e.get("height")?,
                    )?,
                )?);
                args500.push(binary("sub", e.get("right")?, e.get("left")?)?);
                args500.push(binary(
                    "mul",
                    {
                        let fun508 = e.get("len")?;
                        let mut args506 = Vec::new();
                        let mut kw507 = Vec::new();
                        args506.push(e.get("rows")?);
                        fun508.call(args506, kw507)?
                    },
                    e.get("height")?,
                )?);
                kw501.push(("stroke".into(), Val::Int(1i64)));
                kw501.push(("fill".into(), Val::Int(0i64)));
                fun502.call(args500, kw501)?
            };
            for item509 in e
                .get("columns")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("col", item509)?;
                {
                    let fun512 = e.get("line")?;
                    let mut args510 = Vec::new();
                    let mut kw511 = Vec::new();
                    args510.push(e.get("c")?);
                    args510.push(e.get("col")?);
                    args510.push(binary(
                        "sub",
                        e.get("top")?,
                        binary(
                            "mul",
                            {
                                let fun515 = e.get("len")?;
                                let mut args513 = Vec::new();
                                let mut kw514 = Vec::new();
                                args513.push(e.get("rows")?);
                                fun515.call(args513, kw514)?
                            },
                            e.get("height")?,
                        )?,
                    )?);
                    args510.push(e.get("col")?);
                    args510.push(e.get("top")?);
                    fun512.call(args510, kw511)?
                };
            }
            for item516 in {
                let fun533 = e.get("enumerate")?;
                let mut args531 = Vec::new();
                let mut kw532 = Vec::new();
                args531.push(e.get("rows")?);
                fun533.call(args531, kw532)?
            }
            .iter()?
            {
                let unpack534 = unpack(item516, 2)?;
                e.set("i", unpack534[0].clone())?;
                e.set("row", unpack534[1].clone())?;
                let assigned517 = binary(
                    "sub",
                    binary(
                        "sub",
                        e.get("top")?,
                        binary("mul", e.get("i")?, e.get("height")?)?,
                    )?,
                    Val::Int(12i64),
                )?;
                e.set("baseline", assigned517.clone())?;
                if e.get("i")?.truthy()? {
                    {
                        let fun520 = e.get("line")?;
                        let mut args518 = Vec::new();
                        let mut kw519 = Vec::new();
                        args518.push(e.get("c")?);
                        args518.push(e.get("left")?);
                        args518.push(binary(
                            "sub",
                            e.get("top")?,
                            binary("mul", e.get("i")?, e.get("height")?)?,
                        )?);
                        args518.push(e.get("right")?);
                        args518.push(binary(
                            "sub",
                            e.get("top")?,
                            binary("mul", e.get("i")?, e.get("height")?)?,
                        )?);
                        fun520.call(args518, kw519)?
                    };
                }
                for item521 in {
                    let fun529 = e.get("enumerate")?;
                    let mut args527 = Vec::new();
                    let mut kw528 = Vec::new();
                    args527.push(e.get("row")?);
                    fun529.call(args527, kw528)?
                }
                .iter()?
                {
                    let unpack530 = unpack(item521, 2)?;
                    e.set("j", unpack530[0].clone())?;
                    e.set("value", unpack530[1].clone())?;
                    {
                        let fun524 = e.get("text")?;
                        let mut args522 = Vec::new();
                        let mut kw523 = Vec::new();
                        args522.push(e.get("c")?);
                        args522.push(binary(
                            "add",
                            e.get("columns")?.get(e.get("j")?)?,
                            Val::Int(5i64),
                        )?);
                        args522.push(e.get("baseline")?);
                        args522.push(e.get("value")?);
                        args522.push(Val::Float(7.7f64));
                        kw523.push(("bold".into(), {
                            let v525 = e.get("i")?;
                            let v526 = Val::Int(0i64);
                            Val::Bool(compare("eq", v525.clone(), v526.clone())?.truthy()?)
                        }));
                        fun524.call(args522, kw523)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    // requirements
    e.set("requirements",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun537=e.get("text")?;let mut args535=Vec::new();let mut kw536=Vec::new();args535.push(e.get("c")?);args535.push(Val::Int(650i64));args535.push(Val::Int(315i64));args535.push(Val::Str("ASSEMBLY REQUIREMENTS".into()));args535.push(Val::Int(10i64));kw536.push(("bold".into(),Val::Bool(true)));fun537.call(args535,kw536)?};
let assigned538={let mut s=Vec::new();s.push(Val::Str("1. Fabrication state of HSM-000004 before permanent fittings. Component ports, registers and edge preparation: END-CAP-01. Stock dimensions are nominal.".into()));s.push({let mut str539=String::new();str539.push_str("2. Finished cap inside-face spacing AT ROD AXIS: ");str539.push_str(&format(&e.get("INSIDE_SPAN")?,&val_string({let mut str540=String::new();str540.push_str(".3f");Val::Str(str540)})?)?);str539.push_str(" ±");str539.push_str(&format(&e.get("INSIDE_SPAN_TOL")?,&val_string({let mut str541=String::new();str541.push_str(".3f");Val::Str(str541)})?)?);str539.push_str(". Set both outside faces 0.250 below adjacent tube rims. Align both port pairs on ±Y; both R1 register axes coaxial on -Y, opposite the reservoirs' +Y sensing stations.");Val::Str(str539)});s.push(Val::Str("3. Use the fixed-length rod per FR-CARB-01. Seat and tack it in the bottom register before the bottom closure weld. Install the float before top closure; verify top engagement, free travel and full cap seating at the specified spacing.".into()));s.push(Val::Str("4. W1: continuous internal-corner fillet around BOTH cap perimeters. ER316L .030 filler. Clean bore band and cap outside face; preserve the square cap weld root. T1: tack rod to bottom cap. Welding, inspection, hydro and passivation: pressure-vessel procedure, steps 2-8.".into()));s.push({let mut str542=String::new();str542.push_str("5. Upper stop: Ø");str542.push_str(&format(&binary("truediv",e.get("carb")?.attr("UPPER_STOP_D")?,e.get("MM")?)?,&val_string({let mut str543=String::new();str543.push_str(".3f");Val::Str(str543)})?)?);str542.push_str(" stock, Ø9/64 THRU, ");str542.push_str(&format(&binary("truediv",e.get("carb")?.attr("UPPER_STOP_H")?,e.get("MM")?)?,&val_string({let mut str544=String::new();str544.push_str(".4f");Val::Str(str544)})?)?);str542.push_str(" +0.0000/-0.0079 long; square faces, deburr. T2: tack concentrically over top R1 before closure. Keep bore clear. With inlet fitted, retain 0.039 MIN axial air above the stopped float; verify through full radial guide play. Stop attachment and installed clearance require qualification.");Val::Str(str542)});Val::list(s)};e.set("paragraphs",assigned538.clone())?;
let assigned545={let fun548=e.get("wrap_lines")?;let mut args546=Vec::new();let mut kw547=Vec::new();args546.push(e.get("c")?);args546.push(Val::Int(650i64));args546.push(Val::Int(297i64));args546.push(e.get("paragraphs")?);args546.push(Val::Int(525i64));kw547.push(("size".into(),Val::Float(8.0f64)));kw547.push(("leading".into(),Val::Float(10.2f64)));kw547.push(("gap".into(),Val::Int(4i64)));fun548.call(args546,kw547)?};e.set("end",assigned545.clone())?;
return Ok(e.get("end")?);
Ok(Val::None)})})?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned549={let fun552=e.get("canvas")?.attr("Canvas")?;let mut args550=Vec::new();let mut kw551=Vec::new();args550.push({let fun555=e.get("str")?;let mut args553=Vec::new();let mut kw554=Vec::new();args553.push(e.get("path")?);fun555.call(args553,kw554)?});kw551.push(("pagesize".into(),e.get("SHEET")?));kw551.push(("invariant".into(),Val::Int(1i64)));kw551.push(("pageCompression".into(),Val::Int(1i64)));fun552.call(args550,kw551)?};e.set("c",assigned549.clone())?;
{let fun558=e.get("c")?.attr("setTitle")?;let mut args556=Vec::new();let mut kw557=Vec::new();args556.push(Val::Str("Carbonator vessel - closure assembly engineering drawing".into()));fun558.call(args556,kw557)?};
{let fun561=e.get("c")?.attr("setAuthor")?;let mut args559=Vec::new();let mut kw560=Vec::new();args559.push(Val::Str("Home Soda Machine / Codex".into()));fun561.call(args559,kw560)?};
{let fun564=e.get("c")?.attr("setSubject")?;let mut args562=Vec::new();let mut kw563=Vec::new();args562.push(Val::Str("CV-WLD-01 Rev C: -Y sensing azimuth and upper float stop".into()));fun564.call(args562,kw563)?};
{let fun567=e.get("frame")?;let mut args565=Vec::new();let mut kw566=Vec::new();args565.push(e.get("c")?);args565.push(e.get("SHEET")?);fun567.call(args565,kw566)?};
{let fun570=e.get("longitudinal_section")?;let mut args568=Vec::new();let mut kw569=Vec::new();args568.push(e.get("c")?);fun570.call(args568,kw569)?};
{let fun573=e.get("outside_end_view")?;let mut args571=Vec::new();let mut kw572=Vec::new();args571.push(e.get("c")?);fun573.call(args571,kw572)?};
{let fun576=e.get("closure_detail")?;let mut args574=Vec::new();let mut kw575=Vec::new();args574.push(e.get("c")?);fun576.call(args574,kw575)?};
{let fun579=e.get("parts_list")?;let mut args577=Vec::new();let mut kw578=Vec::new();args577.push(e.get("c")?);fun579.call(args577,kw578)?};
{let fun582=e.get("requirements")?;let mut args580=Vec::new();let mut kw581=Vec::new();args580.push(e.get("c")?);fun582.call(args580,kw581)?};
{let fun585=e.get("text")?;let mut args583=Vec::new();let mut kw584=Vec::new();args583.push(e.get("c")?);args583.push(Val::Int(47i64));args583.push(Val::Int(168i64));args583.push(Val::Str("RELEASE ITEMS: W1 SIZE AND WELD QUALIFICATION; REMAINING UNSPECIFIED ASSEMBLY TOLERANCES.".into()));args583.push(Val::Float(8.5f64));kw584.push(("bold".into(),Val::Bool(true)));fun585.call(args583,kw584)?};
{let fun588=e.get("title_block")?;let mut args586=Vec::new();let mut kw587=Vec::new();args586.push(e.get("c")?);args586.push(e.get("SHEET")?);args586.push(Val::Str("CARBONATOR VESSEL - CLOSURE ASSEMBLY".into()));args586.push(Val::Str("CV-WLD-01".into()));args586.push(Val::Str("SEE PARTS LIST".into()));args586.push(Val::Str("1 PER MACHINE".into()));args586.push(Val::Str("HSM-000004 / FABRICATION STATE".into()));kw587.push(("revision".into(),Val::Str("C".into())));kw587.push(("date".into(),Val::Str("2026-10-28".into())));fun588.call(args586,kw587)?};
{let fun591=e.get("c")?.attr("showPage")?;let mut args589=Vec::new();let mut kw590=Vec::new();fun591.call(args589,kw590)?};
{let fun594=e.get("c")?.attr("save")?;let mut args592=Vec::new();let mut kw593=Vec::new();fun594.call(args592,kw593)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun597 = e.get("export_pdf")?;
        let mut args595 = Vec::new();
        let mut kw596 = Vec::new();
        args595.push(e.get("build_pdf")?);
        args595.push({
            let fun600 = e.get("str")?;
            let mut args598 = Vec::new();
            let mut kw599 = Vec::new();
            args598.push(e.get("PDF_PATH")?);
            fun600.call(args598, kw599)?
        });
        fun597.call(args595, kw596)?
    };
    {
        let fun603 = e.get("print")?;
        let mut args601 = Vec::new();
        let mut kw602 = Vec::new();
        args601.push({
            let mut str604 = String::new();
            str604.push_str("Exported: ");
            str604.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
            Val::Str(str604)
        });
        fun603.call(args601, kw602)?
    };
    Ok(Val::None)
}
