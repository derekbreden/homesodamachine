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
                                let fun22 = binary(
                                    "truediv",
                                    binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                    Val::Str("docgen".into()),
                                )?
                                .attr("is_dir")?;
                                let mut args20 = Vec::new();
                                let mut kw21 = Vec::new();
                                fun22.call(args20, kw21)?
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
                Val::Str("tools".into()),
            )?);
            fun14.call(args12, kw13)?
        });
        fun11.call(args9, kw10)?
    };
    {
        let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args23 = Vec::new();
        let mut kw24 = Vec::new();
        args23.push(Val::Int(0i64));
        args23.push({
            let fun28 = e.get("str")?;
            let mut args26 = Vec::new();
            let mut kw27 = Vec::new();
            args26.push(binary(
                "truediv",
                {
                    let fun31 = e.get("next")?;
                    let mut args29 = Vec::new();
                    let mut kw30 = Vec::new();
                    args29.push({
                        let e = e.child();
                        let out32 = Val::list(vec![]);
                        for item33 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item33)?;
                            if {
                                let v34 = e.get("p")?.attr("name")?;
                                let v35 = Val::Str("hardware".into());
                                Val::Bool(compare("eq", v34.clone(), v35.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out32.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out32
                    });
                    fun31.call(args29, kw30)?
                },
                Val::Str("scripts".into()),
            )?);
            fun28.call(args26, kw27)?
        });
        fun25.call(args23, kw24)?
    };
    let mod37 = rt.import_module("_document_export")?;
    e.set("export_dxf", rt.member("_document_export", "export_dxf")?)?;
    {
        let fun40 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args38 = Vec::new();
        let mut kw39 = Vec::new();
        args38.push(Val::Int(0i64));
        args38.push({
            let fun43 = e.get("str")?;
            let mut args41 = Vec::new();
            let mut kw42 = Vec::new();
            args41.push(binary(
                "truediv",
                binary(
                    "truediv",
                    {
                        let fun46 = e.get("next")?;
                        let mut args44 = Vec::new();
                        let mut kw45 = Vec::new();
                        args44.push({
                            let e = e.child();
                            let out47 = Val::list(vec![]);
                            for item48 in e.get("_here")?.attr("parents")?.iter()? {
                                e.set("p", item48)?;
                                if {
                                    let v49 = e.get("p")?.attr("name")?;
                                    let v50 = Val::Str("hardware".into());
                                    Val::Bool(compare("eq", v49.clone(), v50.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    out47.attr("append")?.call(vec![e.get("p")?], vec![])?;
                                }
                            }
                            out47
                        });
                        fun46.call(args44, kw45)?
                    },
                    Val::Str("printed-parts".into()),
                )?,
                Val::Str("cold-core".into()),
            )?);
            fun43.call(args41, kw42)?
        });
        fun40.call(args38, kw39)?
    };
    let assigned52 = Val::Float(hsm_endcap_circular_numbers::DIAMETER_IN);
    e.set("disc_diameter", assigned52.clone())?;
    let assigned53 = binary("truediv", e.get("disc_diameter")?, Val::Int(2i64))?;
    e.set("disc_radius", assigned53.clone())?;
    let assigned54 = Val::Float(hsm_endcap_circular_numbers::THICKNESS_IN);
    e.set("disc_thickness", assigned54.clone())?;
    let assigned55 = Val::Float(hsm_endcap_circular_numbers::HOLE_DIAMETER_IN);
    e.set("hole_diameter", assigned55.clone())?;
    let assigned56 = binary("truediv", e.get("hole_diameter")?, Val::Int(2i64))?;
    e.set("hole_radius", assigned56.clone())?;
    let assigned57 = Val::Float(hsm_endcap_circular_numbers::HOLE_SPACING_IN);
    e.set("hole_spacing", assigned57.clone())?;
    let assigned58 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(binary(
                "truediv",
                unary("neg", e.get("hole_spacing")?)?,
                Val::Int(2i64),
            )?);
            s.push(Val::Float(0.0f64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(binary(
                "truediv",
                unary("pos", e.get("hole_spacing")?)?,
                Val::Int(2i64),
            )?);
            s.push(Val::Float(0.0f64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("hole_positions", assigned58.clone())?;
    let assigned59 = Val::Float(hsm_endcap_circular_numbers::TUBE_ID_IN);
    e.set("tube_id", assigned59.clone())?;
    let assigned60 = binary("truediv", e.get("tube_id")?, Val::Int(2i64))?;
    e.set("tube_id_radius", assigned60.clone())?;
    let assigned61 = Val::Float(hsm_endcap_circular_numbers::REGISTER_RADIUS_IN);
    e.set("register_radius", assigned61.clone())?;
    let assigned62 = {
        let mut s = Vec::new();
        s.push(unary("neg", e.get("register_radius")?)?);
        s.push(Val::Float(0.0f64));
        Val::tuple(s)
    };
    e.set("register_position", assigned62.clone())?;
    let assigned63 = Val::Float(hsm_endcap_circular_numbers::REGISTER_DRILL_IN);
    e.set("register_drill_diameter", assigned63.clone())?;
    let assigned64 = Val::Float(hsm_endcap_circular_numbers::REGISTER_DEPTH_IN);
    e.set("register_depth", assigned64.clone())?;
    let assigned65 = {
        let fun68 = {
            let fun71 = e.get("Path")?;
            let mut args69 = Vec::new();
            let mut kw70 = Vec::new();
            args69.push(e.get("__file__")?);
            fun71.call(args69, kw70)?
        }
        .attr("resolve")?;
        let mut args66 = Vec::new();
        let mut kw67 = Vec::new();
        fun68.call(args66, kw67)?
    }
    .attr("parent")?;
    e.set("out_dir", assigned65.clone())?;
    let assigned72 = Val::Str("endcap-circular-2hole".into());
    e.set("out_name", assigned72.clone())?;
    // make_disc
    e.set("make_disc", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("ezdxf", rt.import_module("ezdxf")?)?;
            let assigned73 = {
                let fun76 = e.get("ezdxf")?.attr("new")?;
                let mut args74 = Vec::new();
                let mut kw75 = Vec::new();
                kw75.push(("dxfversion".into(), Val::Str("R2010".into())));
                fun76.call(args74, kw75)?
            };
            e.set("doc", assigned73.clone())?;
            let assigned77 = Val::Int(1i64);
            e.get("doc")?
                .attr("header")?
                .set(Val::Str("$INSUNITS".into()), assigned77.clone())?;
            let assigned78 = {
                let fun81 = e.get("doc")?.attr("modelspace")?;
                let mut args79 = Vec::new();
                let mut kw80 = Vec::new();
                fun81.call(args79, kw80)?
            };
            e.set("msp", assigned78.clone())?;
            {
                let fun84 = e.get("msp")?.attr("add_circle")?;
                let mut args82 = Vec::new();
                let mut kw83 = Vec::new();
                args82.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                });
                args82.push(e.get("disc_radius")?);
                fun84.call(args82, kw83)?
            };
            for item85 in e.get("hole_positions")?.iter()? {
                e.set("hole_center", item85)?;
                {
                    let fun88 = e.get("msp")?.attr("add_circle")?;
                    let mut args86 = Vec::new();
                    let mut kw87 = Vec::new();
                    args86.push(e.get("hole_center")?);
                    args86.push(e.get("hole_radius")?);
                    fun88.call(args86, kw87)?
                };
            }
            let assigned89 = binary("truediv", e.get("out_dir")?, {
                let mut str90 = String::new();
                str90.push_str(&format(&e.get("out_name")?, &String::new())?);
                str90.push_str(".dxf");
                Val::Str(str90)
            })?;
            e.set("path", assigned89.clone())?;
            {
                let fun93 = e.get("export_dxf")?;
                let mut args91 = Vec::new();
                let mut kw92 = Vec::new();
                args91.push(e.get("doc")?);
                args91.push({
                    let fun96 = e.get("str")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    args94.push(e.get("path")?);
                    fun96.call(args94, kw95)?
                });
                fun93.call(args91, kw92)?
            };
            return Ok(e.get("path")?);
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
            let assigned97 = {
                let fun100 = e.get("make_disc")?;
                let mut args98 = Vec::new();
                let mut kw99 = Vec::new();
                fun100.call(args98, kw99)?
            };
            e.set("path", assigned97.clone())?;
            {
                let fun103 = e.get("print")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push({
                    let mut str104 = String::new();
                    str104.push_str("Exported: ");
                    str104.push_str(&format(&e.get("path")?, &String::new())?);
                    str104.push_str("  (");
                    str104.push_str(&format(
                        &{
                            let fun107 = e.get("len")?;
                            let mut args105 = Vec::new();
                            let mut kw106 = Vec::new();
                            args105.push(e.get("hole_positions")?);
                            fun107.call(args105, kw106)?
                        },
                        &String::new(),
                    )?);
                    str104.push_str(" holes)");
                    Val::Str(str104)
                });
                fun103.call(args101, kw102)?
            };
            {
                let fun110 = e.get("print")?;
                let mut args108 = Vec::new();
                let mut kw109 = Vec::new();
                args108.push({
                    let mut str111 = String::new();
                    str111.push_str("  Disc diameter:   ");
                    str111.push_str(&format(&e.get("disc_diameter")?, &String::new())?);
                    str111.push_str("\"  (fits 5.000\" OD x 0.065\" wall tube, ID 4.870\")");
                    Val::Str(str111)
                });
                fun110.call(args108, kw109)?
            };
            {
                let fun114 = e.get("print")?;
                let mut args112 = Vec::new();
                let mut kw113 = Vec::new();
                args112.push({
                    let mut str115 = String::new();
                    str115.push_str("  Disc thickness:  ");
                    str115.push_str(&format(&e.get("disc_thickness")?, &String::new())?);
                    str115.push_str("\"");
                    Val::Str(str115)
                });
                fun114.call(args112, kw113)?
            };
            {
                let fun118 = e.get("print")?;
                let mut args116 = Vec::new();
                let mut kw117 = Vec::new();
                args116.push({
                    let mut str119 = String::new();
                    str119.push_str("  Hole diameter:   ");
                    str119.push_str(&format(&e.get("hole_diameter")?, &String::new())?);
                    str119.push_str("\"  (7/16\" tap drill for 1/4\"-18 NPT)");
                    Val::Str(str119)
                });
                fun118.call(args116, kw117)?
            };
            {
                let fun122 = e.get("print")?;
                let mut args120 = Vec::new();
                let mut kw121 = Vec::new();
                args120.push({
                    let mut str123 = String::new();
                    str123.push_str("  Hole spacing:    ");
                    str123.push_str(&format(
                        &e.get("hole_spacing")?,
                        &val_string({
                            let mut str124 = String::new();
                            str124.push_str(".4g");
                            Val::Str(str124)
                        })?,
                    )?);
                    str123.push_str("\" center-to-center along one axis");
                    Val::Str(str123)
                });
                fun122.call(args120, kw121)?
            };
            {
                let fun127 = e.get("print")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.push({
                    let mut str128 = String::new();
                    str128.push_str("  Material:        316 SS, laser-cut");
                    Val::Str(str128)
                });
                fun127.call(args125, kw126)?
            };
            {
                let fun131 = e.get("print")?;
                let mut args129 = Vec::new();
                let mut kw130 = Vec::new();
                args129.push({
                    let mut str132 = String::new();
                    str132.push_str(
                        "  Per carbonator:  2 identical discs, each tapped 2x 1/4\"-18 NPT",
                    );
                    Val::Str(str132)
                });
                fun131.call(args129, kw130)?
            };
            {
                let fun135 = e.get("print")?;
                let mut args133 = Vec::new();
                let mut kw134 = Vec::new();
                args133.push({
                    let mut str136 = String::new();
                    str136.push_str("  Rod register:    blind drill (NOT cut) at ");
                    str136.push_str(&format(&e.get("register_position")?, &String::new())?);
                    str136.push_str(" in, Ø");
                    str136.push_str(&format(
                        &e.get("register_drill_diameter")?,
                        &val_string({
                            let mut str137 = String::new();
                            str137.push_str(".4g");
                            Val::Str(str137)
                        })?,
                    )?);
                    str136.push_str("\" x ");
                    str136.push_str(&format(
                        &e.get("register_depth")?,
                        &val_string({
                            let mut str138 = String::new();
                            str138.push_str(".3g");
                            Val::Str(str138)
                        })?,
                    )?);
                    str136.push_str("\" deep, from inside face");
                    Val::Str(str136)
                });
                fun135.call(args133, kw134)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun176 = e.get("main")?;
        let mut args174 = Vec::new();
        let mut kw175 = Vec::new();
        fun176.call(args174, kw175)?
    };
    Ok(Val::None)
}
