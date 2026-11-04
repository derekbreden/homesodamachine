//! The 1 mm TPU ring between the machine display glass and its snap-retained cover.
//!
//! The ring lies in the cover's local frame: X across, Y up the display plane and Z
//! out of the face. Its outer outline matches the glass and its inner outline the window.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun8 = e.get("Path")?;
                    let mut args6 = Vec::new();
                    let mut kw7 = Vec::new();
                    args6.push(e.get("__file__")?);
                    fun8.call(args6, kw7)?
                }
            }
            .attr("resolve")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            fun5.call(args3, kw4)?
        }
    };
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun12 = e.get("next")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push({
                let e = e.child();
                let out13 = Val::list(vec![]);
                for item14 in e.get("_here")?.attr("parents")?.iter()? {
                    e.set("p", item14)?;
                    if {
                        let v15 = e.get("p")?.attr("name")?;
                        let v16 = Val::Str("hardware".into());
                        Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out13.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out13
            });
            fun12.call(args10, kw11)?
        }
    };
    e.set("_hw", assigned9.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(Val::Int(0i64));
            args17.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun22 = e.get("str")?;
                    let mut args20 = Vec::new();
                    let mut kw21 = Vec::new();
                    args20.push(binary(
                        "truediv",
                        e.get("_hw")?,
                        Val::Str("scripts".into()),
                    )?);
                    fun22.call(args20, kw21)?
                }
            });
            fun19.call(args17, kw18)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(Val::Int(0i64));
            args23.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun28=e.get("str")?;let mut args26=Vec::new();let mut kw27=Vec::new();args26.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun31=e.get("next")?;let mut args29=Vec::new();let mut kw30=Vec::new();args29.push({let e=e.child();let out32=Val::list(vec![]);for item33 in e.get("_here")?.attr("parents")?.iter()? {e.set("p",item33)?;if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun36=binary("truediv",binary("truediv",e.get("p")?,Val::Str("tools".into()))?,Val::Str("docgen".into()))?.attr("is_dir")?;let mut args34=Vec::new();let mut kw35=Vec::new();fun36.call(args34,kw35)?}}.truthy()? {out32.attr("append")?.call(vec![e.get("p")?],vec![])?;}}out32});fun31.call(args29,kw30)?}},Val::Str("tools".into()))?);fun28.call(args26,kw27)?}});
            fun25.call(args23, kw24)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun39 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args37 = Vec::new();
            let mut kw38 = Vec::new();
            args37.push(Val::Int(0i64));
            args37.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun42 = e.get("str")?;
                    let mut args40 = Vec::new();
                    let mut kw41 = Vec::new();
                    args40.push(binary(
                        "truediv",
                        binary(
                            "truediv",
                            binary("truediv", e.get("_hw")?, Val::Str("printed-parts".into()))?,
                            Val::Str("enclosure".into()),
                        )?,
                        Val::Str("enclosure".into()),
                    )?);
                    fun42.call(args40, kw41)?
                }
            });
            fun39.call(args37, kw38)?
        }
    };
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod43 = rt.import_module("_cadq_export")?;
    e.set(
        "export_assembly",
        rt.member("_cadq_export", "export_assembly")?,
    )?;
    let mod44 = rt.import_module("_materials")?;
    e.set("M_TPU_BLACK", rt.member("_materials", "M_TPU_BLACK")?)?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    e.set("one_body", rt.member("_materials", "one_body")?)?;
    let mod45 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    e.set(
        "substitute_py_comments",
        rt.member("docgen", "substitute_py_comments")?,
    )?;
    let mod46 = rt.import_module("_enclosure_interface")?;
    e.set(
        "display_bezel_depth",
        rt.member("_enclosure_interface", "display_bezel_depth")?,
    )?;
    e.set(
        "display_bezel_slope",
        rt.member("_enclosure_interface", "display_bezel_slope")?,
    )?;
    e.set(
        "display_bezel_x",
        rt.member("_enclosure_interface", "display_bezel_x")?,
    )?;
    e.set(
        "display_corner_r",
        rt.member("_enclosure_interface", "display_corner_r")?,
    )?;
    e.set(
        "display_inset_depth",
        rt.member("_enclosure_interface", "display_inset_depth")?,
    )?;
    e.set(
        "display_inset_lap",
        rt.member("_enclosure_interface", "display_inset_lap")?,
    )?;
    let mod47 = rt.import_module("_enclosure_data")?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    // _data
    e.set("_data", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun50 = e.get("_read")?;
                    let mut args48 = Vec::new();
                    let mut kw49 = Vec::new();
                    args48.push(Val::Str("gasket".into()));
                    kw49.push(("display_bezel_x".into(), e.get("display_bezel_x")?));
                    kw49.push(("display_bezel_slope".into(), e.get("display_bezel_slope")?));
                    kw49.push(("display_corner_r".into(), e.get("display_corner_r")?));
                    kw49.push(("display_inset_lap".into(), e.get("display_inset_lap")?));
                    kw49.push(("display_bezel_depth".into(), e.get("display_bezel_depth")?));
                    kw49.push(("display_inset_depth".into(), e.get("display_inset_depth")?));
                    kw49.push(("color".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                            line!(),
                        );
                        {
                            let fun53 = e.get("linear")?;
                            let mut args51 = Vec::new();
                            let mut kw52 = Vec::new();
                            args51.push(e.get("M_TPU_BLACK")?);
                            fun53.call(args51, kw52)?
                        }
                    }));
                    fun50.call(args48, kw49)?
                }
            });
            Ok(Val::None)
        })
    })?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun56 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun59 = e.get("globals")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    fun59.call(args57, kw58)?
                }
            }
            .attr("update")?;
            let mut args54 = Vec::new();
            let mut kw55 = Vec::new();
            args54.push(
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                        line!(),
                    );
                    {
                        let fun62 = e.get("_data")?;
                        let mut args60 = Vec::new();
                        let mut kw61 = Vec::new();
                        fun62.call(args60, kw61)?
                    }
                }
                .get(Val::Str("scalars".into()))?,
            );
            fun56.call(args54, kw55)?
        }
    };
    // _rounded_prism
    e.set("_rounded_prism",{let params=vec![("x".into(),None,false),("slope".into(),None,false),("r".into(),None,false),("z0".into(),None,false),("z1".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun65={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun68={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun71={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun74={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun77={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/display_gasket.rs",line!());{let fun80=e.get("cq")?.attr("Workplane")?;let mut args78=Vec::new();let mut kw79=Vec::new();args78.push(Val::Str("XY".into()));fun80.call(args78,kw79)?}}.attr("workplane")?;let mut args75=Vec::new();let mut kw76=Vec::new();kw76.push(("offset".into(),e.get("z0")?));fun77.call(args75,kw76)?}}.attr("rect")?;let mut args72=Vec::new();let mut kw73=Vec::new();args72.push(e.get("x")?);args72.push(e.get("slope")?);fun74.call(args72,kw73)?}}.attr("extrude")?;let mut args69=Vec::new();let mut kw70=Vec::new();args69.push(binary("sub",e.get("z1")?,e.get("z0")?)?);fun71.call(args69,kw70)?}}.attr("edges")?;let mut args66=Vec::new();let mut kw67=Vec::new();args66.push(Val::Str("|Z".into()));fun68.call(args66,kw67)?}}.attr("fillet")?;let mut args63=Vec::new();let mut kw64=Vec::new();args63.push(e.get("r")?);fun65.call(args63,kw64)?}});
Ok(Val::None)})})?;
    // build_display_gasket
    e.set("build_display_gasket", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned81 = Val::Float(1.0f64);
            e.set("proud", assigned81.clone())?;
            let assigned82 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun85 = e.get("_rounded_prism")?;
                    let mut args83 = Vec::new();
                    let mut kw84 = Vec::new();
                    args83.push(e.get("outer_x")?);
                    args83.push(e.get("outer_slope")?);
                    args83.push(e.get("corner_r")?);
                    args83.push(e.get("z_bottom")?);
                    args83.push(e.get("z_top")?);
                    fun85.call(args83, kw84)?
                }
            };
            e.set("ring", assigned82.clone())?;
            let assigned86 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun89 = e.get("_rounded_prism")?;
                    let mut args87 = Vec::new();
                    let mut kw88 = Vec::new();
                    args87.push(e.get("inner_x")?);
                    args87.push(e.get("inner_slope")?);
                    args87.push(e.get("corner_r")?);
                    args87.push(binary("sub", e.get("z_bottom")?, e.get("proud")?)?);
                    args87.push(binary("add", e.get("z_top")?, e.get("proud")?)?);
                    fun89.call(args87, kw88)?
                }
            };
            e.set("window", assigned86.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun92 = e.get("ring")?.attr("cut")?;
                    let mut args90 = Vec::new();
                    let mut kw91 = Vec::new();
                    args90.push(e.get("window")?);
                    fun92.call(args90, kw91)?
                }
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
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun95 = e.get("_data")?;
                    let mut args93 = Vec::new();
                    let mut kw94 = Vec::new();
                    fun95.call(args93, kw94)?
                }
            }
            .get(Val::Str("recipe".into()))?);
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
            let assigned96 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun99 = e.get("_rust_part")?.attr("cut")?;
                    let mut args97 = Vec::new();
                    let mut kw98 = Vec::new();
                    args97.push(Val::Str("enclosure-components".into()));
                    args97.push(Val::Str("display-gasket".into()));
                    args97.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                            line!(),
                        );
                        {
                            let fun102 = e.get("numbers")?;
                            let mut args100 = Vec::new();
                            let mut kw101 = Vec::new();
                            fun102.call(args100, kw101)?
                        }
                    });
                    args97.push(e.get("_here")?.attr("parent")?);
                    fun99.call(args97, kw98)?
                }
            };
            e.set("result", assigned96.clone())?;
            let assigned103 = binary(
                "truediv",
                e.get("_here")?.attr("parent")?,
                Val::Str("display-gasket.step".into()),
            )?;
            e.set("out", assigned103.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun106 = e.get("print")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push({
                        let mut str107 = String::new();
                        str107.push_str("-> ");
                        str107.push_str(&format(&e.get("out")?.attr("name")?, &String::new())?);
                        Val::Str(str107)
                    });
                    fun106.call(args104, kw105)?
                }
            };
            let assigned108 = {
                let mut s = Vec::new();
                s.push(
                    e.get("result")?
                        .get(Val::Str("bodies".into()))?
                        .get(Val::Int(0i64))?
                        .get(Val::Str("min".into()))?,
                );
                s.push(
                    e.get("result")?
                        .get(Val::Str("bodies".into()))?
                        .get(Val::Int(0i64))?
                        .get(Val::Str("max".into()))?,
                );
                Val::tuple(s)
            };
            let unpack109 = unpack(assigned108.clone(), 2)?;
            e.set("lo", unpack109[0].clone())?;
            e.set("hi", unpack109[1].clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun112 = e.get("print")?;
                    let mut args110 = Vec::new();
                    let mut kw111 = Vec::new();
                    args110.push(Val::Str("Display gasket".into()));
                    fun112.call(args110, kw111)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun115 = e.get("print")?;
                    let mut args113 = Vec::new();
                    let mut kw114 = Vec::new();
                    args113.push({
                        let mut str116 = String::new();
                        str116.push_str("  ");
                        str116.push_str(&format(
                            &e.get("outer_x")?,
                            &val_string({
                                let mut str117 = String::new();
                                str117.push_str("g");
                                Val::Str(str117)
                            })?,
                        )?);
                        str116.push_str(" x ");
                        str116.push_str(&format(
                            &e.get("outer_slope")?,
                            &val_string({
                                let mut str118 = String::new();
                                str118.push_str("g");
                                Val::Str(str118)
                            })?,
                        )?);
                        str116.push_str(" outer, ");
                        str116.push_str(&format(
                            &e.get("inner_x")?,
                            &val_string({
                                let mut str119 = String::new();
                                str119.push_str("g");
                                Val::Str(str119)
                            })?,
                        )?);
                        str116.push_str(" x ");
                        str116.push_str(&format(
                            &e.get("inner_slope")?,
                            &val_string({
                                let mut str120 = String::new();
                                str120.push_str("g");
                                Val::Str(str120)
                            })?,
                        )?);
                        str116.push_str(" inner — a ");
                        str116.push_str(&format(
                            &e.get("display_inset_lap")?,
                            &val_string({
                                let mut str121 = String::new();
                                str121.push_str("g");
                                Val::Str(str121)
                            })?,
                        )?);
                        str116.push_str(" ring, r");
                        str116.push_str(&format(
                            &e.get("corner_r")?,
                            &val_string({
                                let mut str122 = String::new();
                                str122.push_str("g");
                                Val::Str(str122)
                            })?,
                        )?);
                        str116.push_str(" corners");
                        Val::Str(str116)
                    });
                    fun115.call(args113, kw114)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun125 = e.get("print")?;
                    let mut args123 = Vec::new();
                    let mut kw124 = Vec::new();
                    args123.push({
                        let mut str126 = String::new();
                        str126.push_str("  ");
                        str126.push_str(&format(
                            &e.get("thickness")?,
                            &val_string({
                                let mut str127 = String::new();
                                str127.push_str("g");
                                Val::Str(str127)
                            })?,
                        )?);
                        str126.push_str(" thick, from the plate's underside at ");
                        str126.push_str(&format(
                            &e.get("display_inset_depth")?,
                            &val_string({
                                let mut str128 = String::new();
                                str128.push_str("g");
                                Val::Str(str128)
                            })?,
                        )?);
                        str126.push_str(" down to the glass at ");
                        str126.push_str(&format(
                            &e.get("glass_face_depth")?,
                            &val_string({
                                let mut str129 = String::new();
                                str129.push_str("g");
                                Val::Str(str129)
                            })?,
                        )?);
                        Val::Str(str126)
                    });
                    fun125.call(args123, kw124)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun132 = e.get("print")?;
                    let mut args130 = Vec::new();
                    let mut kw131 = Vec::new();
                    args130.push({
                        let mut str133 = String::new();
                        str133.push_str("  Bounding box: X [");
                        str133.push_str(&format(
                            &e.get("lo")?.get(Val::Int(0i64))?,
                            &val_string({
                                let mut str134 = String::new();
                                str134.push_str(".2f");
                                Val::Str(str134)
                            })?,
                        )?);
                        str133.push_str(", ");
                        str133.push_str(&format(
                            &e.get("hi")?.get(Val::Int(0i64))?,
                            &val_string({
                                let mut str135 = String::new();
                                str135.push_str(".2f");
                                Val::Str(str135)
                            })?,
                        )?);
                        str133.push_str("]  Y [");
                        str133.push_str(&format(
                            &e.get("lo")?.get(Val::Int(1i64))?,
                            &val_string({
                                let mut str136 = String::new();
                                str136.push_str(".2f");
                                Val::Str(str136)
                            })?,
                        )?);
                        str133.push_str(", ");
                        str133.push_str(&format(
                            &e.get("hi")?.get(Val::Int(1i64))?,
                            &val_string({
                                let mut str137 = String::new();
                                str137.push_str(".2f");
                                Val::Str(str137)
                            })?,
                        )?);
                        str133.push_str("]  Z [");
                        str133.push_str(&format(
                            &e.get("lo")?.get(Val::Int(2i64))?,
                            &val_string({
                                let mut str138 = String::new();
                                str138.push_str(".2f");
                                Val::Str(str138)
                            })?,
                        )?);
                        str133.push_str(", ");
                        str133.push_str(&format(
                            &e.get("hi")?.get(Val::Int(2i64))?,
                            &val_string({
                                let mut str139 = String::new();
                                str139.push_str(".2f");
                                Val::Str(str139)
                            })?,
                        )?);
                        str133.push_str("]");
                        Val::Str(str133)
                    });
                    fun132.call(args130, kw131)?
                }
            };
            let assigned140 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun143 = e.get("_data")?;
                    let mut args141 = Vec::new();
                    let mut kw142 = Vec::new();
                    fun143.call(args141, kw142)?
                }
            }
            .get(Val::Str("variables".into()))?;
            e.set("variables", assigned140.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun146 = e.get("substitute_md")?;
                    let mut args144 = Vec::new();
                    let mut kw145 = Vec::new();
                    args144.push(binary(
                        "truediv",
                        e.get("_here")?.attr("parent")?,
                        Val::Str("README.md".into()),
                    )?);
                    kw145.push(("variables".into(), e.get("variables")?));
                    fun146.call(args144, kw145)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun149 = e.get("print")?;
                    let mut args147 = Vec::new();
                    let mut kw148 = Vec::new();
                    args147.push(Val::Str("-> README.md".into()));
                    fun149.call(args147, kw148)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun152 = e.get("substitute_py_comments")?;
                    let mut args150 = Vec::new();
                    let mut kw151 = Vec::new();
                    args150.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                            line!(),
                        );
                        {
                            let fun155 = e.get("Path")?;
                            let mut args153 = Vec::new();
                            let mut kw154 = Vec::new();
                            args153.push(e.get("__file__")?);
                            fun155.call(args153, kw154)?
                        }
                    });
                    kw151.push(("variables".into(), e.get("variables")?));
                    fun152.call(args150, kw151)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                    line!(),
                );
                {
                    let fun158 = e.get("print")?;
                    let mut args156 = Vec::new();
                    let mut kw157 = Vec::new();
                    args156.push({
                        let mut str159 = String::new();
                        str159.push_str("-> ");
                        str159.push_str(&format(
                            &{
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
                                    line!(),
                                );
                                {
                                    let fun162 = e.get("Path")?;
                                    let mut args160 = Vec::new();
                                    let mut kw161 = Vec::new();
                                    args160.push(e.get("__file__")?);
                                    fun162.call(args160, kw161)?
                                }
                            }
                            .attr("name")?,
                            &String::new(),
                        )?);
                        Val::Str(str159)
                    });
                    fun158.call(args156, kw157)?
                }
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun165 = e.get("_rust_part")?.attr("start")?;
            let mut args163 = Vec::new();
            let mut kw164 = Vec::new();
            fun165.call(args163, kw164)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_gasket.rs",
            line!(),
        );
        {
            let fun168 = e.get("main")?;
            let mut args166 = Vec::new();
            let mut kw167 = Vec::new();
            fun168.call(args166, kw167)?
        }
    };
    Ok(Val::None)
}
