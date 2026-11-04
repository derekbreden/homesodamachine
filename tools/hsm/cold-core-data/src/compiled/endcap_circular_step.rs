#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
    };
    e.set("_here", assigned2.clone())?;
    {
        let fun11 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args9 = Vec::new();
        let mut kw10 = Vec::new();
        args9.push(Val::Int(0i64));
        args9.push({
            let fun14 = e.get("str")?;
            let mut args12 = Vec::new();
            let mut kw13 = Vec::new();
            args12.push(binary(
                "truediv",
                {
                    let fun17 = e.get("next")?;
                    let mut args15 = Vec::new();
                    let mut kw16 = Vec::new();
                    args15.push({
                        let e = e.child();
                        let out18 = Val::list(vec![]);
                        for item19 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item19)?;
                            if {
                                let v20 = e.get("p")?.attr("name")?;
                                let v21 = Val::Str("hardware".into());
                                Val::Bool(compare("eq", v20.clone(), v21.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out18.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out18
                    });
                    fun17.call(args15, kw16)?
                },
                Val::Str("scripts".into()),
            )?);
            fun14.call(args12, kw13)?
        });
        fun11.call(args9, kw10)?
    };
    {
        let fun24 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args22 = Vec::new();
        let mut kw23 = Vec::new();
        args22.push(Val::Int(0i64));
        args22.push({
            let fun27 = e.get("str")?;
            let mut args25 = Vec::new();
            let mut kw26 = Vec::new();
            args25.push(binary(
                "truediv",
                {
                    let fun30 = e.get("next")?;
                    let mut args28 = Vec::new();
                    let mut kw29 = Vec::new();
                    args28.push({
                        let e = e.child();
                        let out31 = Val::list(vec![]);
                        for item32 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item32)?;
                            if {
                                let fun35 = binary(
                                    "truediv",
                                    binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                    Val::Str("docgen".into()),
                                )?
                                .attr("is_dir")?;
                                let mut args33 = Vec::new();
                                let mut kw34 = Vec::new();
                                fun35.call(args33, kw34)?
                            }
                            .truthy()?
                            {
                                out31.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out31
                    });
                    fun30.call(args28, kw29)?
                },
                Val::Str("tools".into()),
            )?);
            fun27.call(args25, kw26)?
        });
        fun24.call(args22, kw23)?
    };
    let mod36 = rt.import_module("docgen")?;
    e.set(
        "substitute_py_comments",
        rt.member("docgen", "substitute_py_comments")?,
    )?;
    let mod37 = rt.import_module("endcap_circular_dxf")?;
    e.set(
        "_register_radius_in",
        rt.member("endcap_circular_dxf", "register_radius")?,
    )?;
    e.set(
        "_register_position_in",
        rt.member("endcap_circular_dxf", "register_position")?,
    )?;
    let assigned38 = Val::Float(25.4f64);
    e.set("inch", assigned38.clone())?;
    let assigned39 = binary("mul", Val::Float(4.86f64), e.get("inch")?)?;
    e.set("disc_diameter", assigned39.clone())?;
    let assigned40 = binary("truediv", e.get("disc_diameter")?, Val::Float(2.0f64))?;
    e.set("disc_radius", assigned40.clone())?;
    let assigned41 = binary("mul", Val::Float(0.25f64), e.get("inch")?)?;
    e.set("disc_thickness", assigned41.clone())?;
    let assigned42 = binary("mul", Val::Float(0.438f64), e.get("inch")?)?;
    e.set("hole_diameter", assigned42.clone())?;
    let assigned43 = binary("truediv", e.get("hole_diameter")?, Val::Float(2.0f64))?;
    e.set("hole_radius", assigned43.clone())?;
    let assigned44 = binary("mul", Val::Float(0.75f64), e.get("inch")?)?;
    e.set("hole_offset", assigned44.clone())?;
    let assigned45 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(unary("neg", e.get("hole_offset")?)?);
            s.push(Val::Float(0.0f64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(e.get("hole_offset")?);
            s.push(Val::Float(0.0f64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("hole_positions", assigned45.clone())?;
    let assigned46 = binary("mul", e.get("_register_radius_in")?, e.get("inch")?)?;
    e.set("register_radius", assigned46.clone())?;
    let assigned47 = {
        let fun50 = e.get("tuple")?;
        let mut args48 = Vec::new();
        let mut kw49 = Vec::new();
        args48.push({
            let e = e.child();
            let out51 = Val::list(vec![]);
            for item52 in e.get("_register_position_in")?.iter()? {
                e.set("v", item52)?;
                out51
                    .attr("append")?
                    .call(vec![binary("mul", e.get("v")?, e.get("inch")?)?], vec![])?;
            }
            out51
        });
        fun50.call(args48, kw49)?
    };
    e.set("register_position", assigned47.clone())?;
    let assigned53 = binary("mul", Val::Float(0.140625f64), e.get("inch")?)?;
    e.set("register_drill_diameter", assigned53.clone())?;
    let assigned54 = binary("mul", Val::Float(0.1f64), e.get("inch")?)?;
    e.set("register_depth", assigned54.clone())?;
    let assigned55 = {
        let fun58 = {
            let fun61 = e.get("Path")?;
            let mut args59 = Vec::new();
            let mut kw60 = Vec::new();
            args59.push(e.get("__file__")?);
            fun61.call(args59, kw60)?
        }
        .attr("resolve")?;
        let mut args56 = Vec::new();
        let mut kw57 = Vec::new();
        fun58.call(args56, kw57)?
    }
    .attr("parent")?;
    e.set("out_dir", assigned55.clone())?;
    let assigned62 = Val::Str("endcap-circular-2hole".into());
    e.set("out_name", assigned62.clone())?;
    // build_endcap
    e.set("build_endcap", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned63 = {
                let fun66 = {
                    let fun69 = {
                        let fun72 = e.get("cq")?.attr("Workplane")?;
                        let mut args70 = Vec::new();
                        let mut kw71 = Vec::new();
                        args70.push(Val::Str("XY".into()));
                        fun72.call(args70, kw71)?
                    }
                    .attr("circle")?;
                    let mut args67 = Vec::new();
                    let mut kw68 = Vec::new();
                    args67.push(e.get("disc_radius")?);
                    fun69.call(args67, kw68)?
                }
                .attr("extrude")?;
                let mut args64 = Vec::new();
                let mut kw65 = Vec::new();
                args64.push(e.get("disc_thickness")?);
                fun66.call(args64, kw65)?
            };
            e.set("disc", assigned63.clone())?;
            let assigned73 = {
                let fun76 = {
                    let fun79 = {
                        let fun82 = {
                            let fun85 = {
                                let fun88 = e.get("cq")?.attr("Workplane")?;
                                let mut args86 = Vec::new();
                                let mut kw87 = Vec::new();
                                args86.push(Val::Str("XY".into()));
                                fun88.call(args86, kw87)?
                            }
                            .attr("workplane")?;
                            let mut args83 = Vec::new();
                            let mut kw84 = Vec::new();
                            kw84.push(("offset".into(), unary("neg", Val::Float(0.5f64))?));
                            fun85.call(args83, kw84)?
                        }
                        .attr("pushPoints")?;
                        let mut args80 = Vec::new();
                        let mut kw81 = Vec::new();
                        args80.push(e.get("hole_positions")?);
                        fun82.call(args80, kw81)?
                    }
                    .attr("circle")?;
                    let mut args77 = Vec::new();
                    let mut kw78 = Vec::new();
                    args77.push(e.get("hole_radius")?);
                    fun79.call(args77, kw78)?
                }
                .attr("extrude")?;
                let mut args74 = Vec::new();
                let mut kw75 = Vec::new();
                args74.push(binary("add", e.get("disc_thickness")?, Val::Float(1.0f64))?);
                fun76.call(args74, kw75)?
            };
            e.set("npt_holes", assigned73.clone())?;
            let assigned89 = {
                let fun92 = {
                    let fun95 = {
                        let fun98 = {
                            let fun101 = {
                                let fun104 = e.get("cq")?.attr("Workplane")?;
                                let mut args102 = Vec::new();
                                let mut kw103 = Vec::new();
                                args102.push(Val::Str("XY".into()));
                                fun104.call(args102, kw103)?
                            }
                            .attr("workplane")?;
                            let mut args99 = Vec::new();
                            let mut kw100 = Vec::new();
                            kw100.push((
                                "offset".into(),
                                binary("add", e.get("disc_thickness")?, Val::Float(0.5f64))?,
                            ));
                            fun101.call(args99, kw100)?
                        }
                        .attr("moveTo")?;
                        let mut args96 = Vec::new();
                        let mut kw97 = Vec::new();
                        args96.extend(e.get("register_position")?.iter()?);
                        fun98.call(args96, kw97)?
                    }
                    .attr("circle")?;
                    let mut args93 = Vec::new();
                    let mut kw94 = Vec::new();
                    args93.push(binary(
                        "truediv",
                        e.get("register_drill_diameter")?,
                        Val::Float(2.0f64),
                    )?);
                    fun95.call(args93, kw94)?
                }
                .attr("extrude")?;
                let mut args90 = Vec::new();
                let mut kw91 = Vec::new();
                args90.push(unary(
                    "neg",
                    binary("add", e.get("register_depth")?, Val::Float(0.5f64))?,
                )?);
                fun92.call(args90, kw91)?
            };
            e.set("register", assigned89.clone())?;
            return Ok({
                let fun107 = {
                    let fun110 = e.get("disc")?.attr("cut")?;
                    let mut args108 = Vec::new();
                    let mut kw109 = Vec::new();
                    args108.push(e.get("npt_holes")?);
                    fun110.call(args108, kw109)?
                }
                .attr("cut")?;
                let mut args105 = Vec::new();
                let mut kw106 = Vec::new();
                args105.push(e.get("register")?);
                fun107.call(args105, kw106)?
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
            let mod111 = rt.import_module("_material_base")?;
            e.set("M_STAINLESS", rt.member("_material_base", "M_STAINLESS")?)?;
            let mod112 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("name".into()), e.get("out_name")?)?;
                d.set(Val::Str("radius".into()), e.get("disc_radius")?)?;
                d.set(Val::Str("height".into()), e.get("disc_thickness")?)?;
                d.set(
                    Val::Str("bores".into()),
                    binary(
                        "add",
                        {
                            let e = e.child();
                            let out113 = Val::list(vec![]);
                            for item114 in e.get("hole_positions")?.iter()? {
                                e.set("p", item114)?;
                                out113.attr("append")?.call(
                                    vec![{
                                        let d = Val::dict(vec![]);
                                        d.set(Val::Str("center".into()), {
                                            let fun117 = e.get("list")?;
                                            let mut args115 = Vec::new();
                                            let mut kw116 = Vec::new();
                                            args115.push(e.get("p")?);
                                            fun117.call(args115, kw116)?
                                        })?;
                                        d.set(Val::Str("radius".into()), e.get("hole_radius")?)?;
                                        d.set(Val::Str("floor".into()), Val::Float(0.0f64))?;
                                        d
                                    }],
                                    vec![],
                                )?;
                            }
                            out113
                        },
                        {
                            let mut s = Vec::new();
                            s.push({
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("center".into()), {
                                    let fun120 = e.get("list")?;
                                    let mut args118 = Vec::new();
                                    let mut kw119 = Vec::new();
                                    args118.push(e.get("register_position")?);
                                    fun120.call(args118, kw119)?
                                })?;
                                d.set(
                                    Val::Str("radius".into()),
                                    binary(
                                        "truediv",
                                        e.get("register_drill_diameter")?,
                                        Val::Float(2.0f64),
                                    )?,
                                )?;
                                d.set(
                                    Val::Str("floor".into()),
                                    binary(
                                        "sub",
                                        e.get("disc_thickness")?,
                                        e.get("register_depth")?,
                                    )?,
                                )?;
                                d
                            });
                            Val::list(s)
                        },
                    )?,
                )?;
                d.set(Val::Str("color".into()), {
                    let fun123 = e.get("list")?;
                    let mut args121 = Vec::new();
                    let mut kw122 = Vec::new();
                    args121.push({
                        let fun126 = e.get("linear")?;
                        let mut args124 = Vec::new();
                        let mut kw125 = Vec::new();
                        args124.push(e.get("M_STAINLESS")?);
                        fun126.call(args124, kw125)?
                    });
                    fun123.call(args121, kw122)?
                })?;
                d
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
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            {
                let fun129 = e.get("_rust_part")?.attr("cut")?;
                let mut args127 = Vec::new();
                let mut kw128 = Vec::new();
                args127.push(Val::Str("cold-core".into()));
                args127.push(Val::Str("endcap-circular-step".into()));
                args127.push({
                    let fun132 = e.get("numbers")?;
                    let mut args130 = Vec::new();
                    let mut kw131 = Vec::new();
                    fun132.call(args130, kw131)?
                });
                args127.push(e.get("out_dir")?);
                fun129.call(args127, kw128)?
            };
            let assigned133 = binary("truediv", e.get("out_dir")?, {
                let mut str134 = String::new();
                str134.push_str(&format(&e.get("out_name")?, &String::new())?);
                str134.push_str(".step");
                Val::Str(str134)
            })?;
            e.set("path", assigned133.clone())?;
            {
                let fun137 = e.get("print")?;
                let mut args135 = Vec::new();
                let mut kw136 = Vec::new();
                args135.push({
                    let mut str138 = String::new();
                    str138.push_str("Exported: ");
                    str138.push_str(&format(&e.get("path")?, &String::new())?);
                    Val::Str(str138)
                });
                fun137.call(args135, kw136)?
            };
            {
                let fun141 = e.get("print")?;
                let mut args139 = Vec::new();
                let mut kw140 = Vec::new();
                args139.push({
                    let mut str142 = String::new();
                    str142.push_str("  Disc:      Ø");
                    str142.push_str(&format(
                        &e.get("disc_diameter")?,
                        &val_string({
                            let mut str143 = String::new();
                            str143.push_str(".3f");
                            Val::Str(str143)
                        })?,
                    )?);
                    str142.push_str(" × ");
                    str142.push_str(&format(
                        &e.get("disc_thickness")?,
                        &val_string({
                            let mut str144 = String::new();
                            str144.push_str(".3f");
                            Val::Str(str144)
                        })?,
                    )?);
                    str142.push_str(" mm, 316 SS");
                    Val::Str(str142)
                });
                fun141.call(args139, kw140)?
            };
            {
                let fun147 = e.get("print")?;
                let mut args145 = Vec::new();
                let mut kw146 = Vec::new();
                args145.push({
                    let mut str148 = String::new();
                    str148.push_str("  NPT holes: 2× Ø");
                    str148.push_str(&format(
                        &e.get("hole_diameter")?,
                        &val_string({
                            let mut str149 = String::new();
                            str149.push_str(".3f");
                            Val::Str(str149)
                        })?,
                    )?);
                    str148.push_str(" mm THRU at X = ±");
                    str148.push_str(&format(
                        &e.get("hole_offset")?,
                        &val_string({
                            let mut str150 = String::new();
                            str150.push_str(".3f");
                            Val::Str(str150)
                        })?,
                    )?);
                    str148.push_str(" mm");
                    Val::Str(str148)
                });
                fun147.call(args145, kw146)?
            };
            {
                let fun153 = e.get("print")?;
                let mut args151 = Vec::new();
                let mut kw152 = Vec::new();
                args151.push({
                    let mut str154 = String::new();
                    str154.push_str("  Register:  Ø");
                    str154.push_str(&format(
                        &e.get("register_drill_diameter")?,
                        &val_string({
                            let mut str155 = String::new();
                            str155.push_str(".4g");
                            Val::Str(str155)
                        })?,
                    )?);
                    str154.push_str(" × ");
                    str154.push_str(&format(
                        &e.get("register_depth")?,
                        &val_string({
                            let mut str156 = String::new();
                            str156.push_str(".3g");
                            Val::Str(str156)
                        })?,
                    )?);
                    str154.push_str(" mm blind at ");
                    str154.push_str(&format(&e.get("register_position")?, &String::new())?);
                    str154.push_str(", +Z (inside) face");
                    Val::Str(str154)
                });
                fun153.call(args151, kw152)?
            };
            let assigned157 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("DISC_D_MM".into()), {
                    let mut str158 = String::new();
                    str158.push_str(&format(
                        &e.get("disc_diameter")?,
                        &val_string({
                            let mut str159 = String::new();
                            str159.push_str(".4g");
                            Val::Str(str159)
                        })?,
                    )?);
                    str158.push_str(" mm");
                    Val::Str(str158)
                })?;
                d.set(Val::Str("DISC_D_IN".into()), {
                    let mut str160 = String::new();
                    str160.push_str(&format(
                        &binary("truediv", e.get("disc_diameter")?, e.get("inch")?)?,
                        &val_string({
                            let mut str161 = String::new();
                            str161.push_str(".4g");
                            Val::Str(str161)
                        })?,
                    )?);
                    str160.push_str(" in");
                    Val::Str(str160)
                })?;
                d.set(Val::Str("DISC_R_MM".into()), {
                    let mut str162 = String::new();
                    str162.push_str(&format(
                        &e.get("disc_radius")?,
                        &val_string({
                            let mut str163 = String::new();
                            str163.push_str(".4g");
                            Val::Str(str163)
                        })?,
                    )?);
                    str162.push_str(" mm");
                    Val::Str(str162)
                })?;
                d.set(Val::Str("DISC_THK_MM".into()), {
                    let mut str164 = String::new();
                    str164.push_str(&format(
                        &e.get("disc_thickness")?,
                        &val_string({
                            let mut str165 = String::new();
                            str165.push_str(".4g");
                            Val::Str(str165)
                        })?,
                    )?);
                    str164.push_str(" mm");
                    Val::Str(str164)
                })?;
                d.set(Val::Str("HOLE_D_MM".into()), {
                    let mut str166 = String::new();
                    str166.push_str(&format(
                        &e.get("hole_diameter")?,
                        &val_string({
                            let mut str167 = String::new();
                            str167.push_str(".4g");
                            Val::Str(str167)
                        })?,
                    )?);
                    str166.push_str(" mm");
                    Val::Str(str166)
                })?;
                d.set(Val::Str("HOLE_R_MM".into()), {
                    let mut str168 = String::new();
                    str168.push_str(&format(
                        &e.get("hole_radius")?,
                        &val_string({
                            let mut str169 = String::new();
                            str169.push_str(".4g");
                            Val::Str(str169)
                        })?,
                    )?);
                    str168.push_str(" mm");
                    Val::Str(str168)
                })?;
                d.set(Val::Str("HOLE_OFFSET_MM".into()), {
                    let mut str170 = String::new();
                    str170.push_str(&format(
                        &e.get("hole_offset")?,
                        &val_string({
                            let mut str171 = String::new();
                            str171.push_str(".4g");
                            Val::Str(str171)
                        })?,
                    )?);
                    str170.push_str(" mm");
                    Val::Str(str170)
                })?;
                d.set(Val::Str("REG_X".into()), {
                    let mut str172 = String::new();
                    str172.push_str(&format(
                        &e.get("register_radius")?,
                        &val_string({
                            let mut str173 = String::new();
                            str173.push_str(".4g");
                            Val::Str(str173)
                        })?,
                    )?);
                    str172.push_str(" mm");
                    Val::Str(str172)
                })?;
                d.set(Val::Str("REG_D".into()), {
                    let mut str174 = String::new();
                    str174.push_str(&format(
                        &e.get("register_drill_diameter")?,
                        &val_string({
                            let mut str175 = String::new();
                            str175.push_str(".4g");
                            Val::Str(str175)
                        })?,
                    )?);
                    str174.push_str(" mm");
                    Val::Str(str174)
                })?;
                d.set(Val::Str("REG_DEPTH".into()), {
                    let mut str176 = String::new();
                    str176.push_str(&format(
                        &e.get("register_depth")?,
                        &val_string({
                            let mut str177 = String::new();
                            str177.push_str(".4g");
                            Val::Str(str177)
                        })?,
                    )?);
                    str176.push_str(" mm");
                    Val::Str(str176)
                })?;
                d.set(Val::Str("REG_PLATE_REMAINING".into()), {
                    let mut str178 = String::new();
                    str178.push_str(&format(
                        &binary("sub", e.get("disc_thickness")?, e.get("register_depth")?)?,
                        &val_string({
                            let mut str179 = String::new();
                            str179.push_str(".4g");
                            Val::Str(str179)
                        })?,
                    )?);
                    str178.push_str(" mm");
                    Val::Str(str178)
                })?;
                d
            };
            e.set("variables", assigned157.clone())?;
            {
                let fun182 = e.get("substitute_py_comments")?;
                let mut args180 = Vec::new();
                let mut kw181 = Vec::new();
                args180.push({
                    let fun185 = e.get("Path")?;
                    let mut args183 = Vec::new();
                    let mut kw184 = Vec::new();
                    args183.push(e.get("__file__")?);
                    fun185.call(args183, kw184)?
                });
                kw181.push(("variables".into(), e.get("variables")?));
                fun182.call(args180, kw181)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun188 = e.get("_rust_part")?.attr("start")?;
        let mut args186 = Vec::new();
        let mut kw187 = Vec::new();
        fun188.call(args186, kw187)?
    };
    {
        let fun191 = e.get("main")?;
        let mut args189 = Vec::new();
        let mut kw190 = Vec::new();
        fun191.call(args189, kw190)?
    };
    Ok(Val::None)
}
