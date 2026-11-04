//! Black DATA trim, white raised lettering, continuous nameplate wings.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
            line!(),
        );
        {
            let fun5 = e.get("next")?;
            let mut args3 = Vec::new();
            let mut kw4 = Vec::new();
            args3.push({
                let e = e.child();
                let out6 = Val::list(vec![]);
                for item7 in {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                        line!(),
                    );
                    {
                        let fun10 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                line!(),
                            );
                            {
                                let fun13 = e.get("Path")?;
                                let mut args11 = Vec::new();
                                let mut kw12 = Vec::new();
                                args11.push(e.get("__file__")?);
                                fun13.call(args11, kw12)?
                            }
                        }
                        .attr("resolve")?;
                        let mut args8 = Vec::new();
                        let mut kw9 = Vec::new();
                        fun10.call(args8, kw9)?
                    }
                }
                .attr("parents")?
                .iter()?
                {
                    e.set("p", item7)?;
                    if {
                        let v14 = e.get("p")?.attr("name")?;
                        let v15 = Val::Str("hardware".into());
                        Val::Bool(compare("eq", v14.clone(), v15.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out6.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out6
            });
            fun5.call(args3, kw4)?
        }
    };
    e.set("_hw", assigned2.clone())?;
    let assigned16 = {
        let mut s = Vec::new();
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                line!(),
            );
            {
                let fun19 = e.get("str")?;
                let mut args17 = Vec::new();
                let mut kw18 = Vec::new();
                args17.push(
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun22 = {
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                    line!(),
                                );
                                {
                                    let fun25 = e.get("Path")?;
                                    let mut args23 = Vec::new();
                                    let mut kw24 = Vec::new();
                                    args23.push(e.get("__file__")?);
                                    fun25.call(args23, kw24)?
                                }
                            }
                            .attr("resolve")?;
                            let mut args20 = Vec::new();
                            let mut kw21 = Vec::new();
                            fun22.call(args20, kw21)?
                        }
                    }
                    .attr("parent")?,
                );
                fun19.call(args17, kw18)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                line!(),
            );
            {
                let fun28 = e.get("str")?;
                let mut args26 = Vec::new();
                let mut kw27 = Vec::new();
                args26.push(binary(
                    "truediv",
                    e.get("_hw")?,
                    Val::Str("scripts".into()),
                )?);
                fun28.call(args26, kw27)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                line!(),
            );
            {
                let fun31 = e.get("str")?;
                let mut args29 = Vec::new();
                let mut kw30 = Vec::new();
                args29.push(binary(
                    "truediv",
                    e.get("_hw")?,
                    Val::Str("printed-parts/enclosure/enclosure".into()),
                )?);
                fun31.call(args29, kw30)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                line!(),
            );
            {
                let fun34 = e.get("str")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                args32.push(binary(
                    "truediv",
                    e.get("_hw")?,
                    Val::Str("printed-parts/enclosure/bulkhead-ring".into()),
                )?);
                fun34.call(args32, kw33)?
            }
        });
        s.push({
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                line!(),
            );
            {
                let fun37 = e.get("str")?;
                let mut args35 = Vec::new();
                let mut kw36 = Vec::new();
                args35.push(binary(
                    "truediv",
                    e.get("_hw")?,
                    Val::Str("printed-parts/enclosure/y-wall-of-back-top".into()),
                )?);
                fun37.call(args35, kw36)?
            }
        });
        Val::list(s)
    };
    e.get("sys")?.attr("path")?.set(
        Val::Slice {
            start: None,
            stop: Some(Val::Int(0i64).integer()?),
            step: 1,
        },
        assigned16.clone(),
    )?;
    e.set("cq", rt.import_module("cadquery")?)?;
    e.set("interface", rt.import_module("_data_wing_interface")?)?;
    e.set("ring", rt.import_module("bulkhead_ring")?)?;
    e.set("rear", rt.import_module("_y_wall_dimensions")?)?;
    let mod38 = rt.import_module("_cadq_export")?;
    e.set(
        "export_assembly",
        rt.member("_cadq_export", "export_assembly")?,
    )?;
    let mod39 = rt.import_module("_materials")?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    e.set("step_safe", rt.member("_materials", "step_safe")?)?;
    let assigned40 = binary(
        "truediv",
        e.get("_hw")?,
        Val::Str("printed-parts/enclosure/data-ring/data-ring.step".into()),
    )?;
    e.set("STEP", assigned40.clone())?;
    // build_word
    e.set("build_word",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned41={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun44={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun47={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun50={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun53={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun56=e.get("cq")?.attr("Workplane")?;let mut args54=Vec::new();let mut kw55=Vec::new();args54.push(Val::Str("XY".into()));fun56.call(args54,kw55)?}}.attr("text")?;let mut args51=Vec::new();let mut kw52=Vec::new();args51.push(Val::Str("DATA".into()));args51.push(e.get("ring")?.attr("WORD_SIZE")?);args51.push(binary("add",e.get("interface")?.attr("INK_DEPTH")?,e.get("ring")?.attr("WORD_RAISE")?)?);kw52.push(("font".into(),e.get("ring")?.attr("WORD_FONT")?));kw52.push(("kind".into(),e.get("ring")?.attr("WORD_KIND")?));kw52.push(("halign".into(),Val::Str("center".into())));kw52.push(("valign".into(),Val::Str("center".into())));fun53.call(args51,kw52)?}}.attr("val")?;let mut args48=Vec::new();let mut kw49=Vec::new();fun50.call(args48,kw49)?}}.attr("rotate")?;let mut args45=Vec::new();let mut kw46=Vec::new();args45.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args45.push({let mut s=Vec::new();s.push(Val::Int(1i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args45.push(Val::Int(90i64));fun47.call(args45,kw46)?}}.attr("rotate")?;let mut args42=Vec::new();let mut kw43=Vec::new();args42.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)});args42.push({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(1i64));Val::tuple(s)});args42.push(Val::Int(180i64));fun44.call(args42,kw43)?}};e.set("text",assigned41.clone())?;
let assigned57={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun60=e.get("text")?.attr("BoundingBox")?;let mut args58=Vec::new();let mut kw59=Vec::new();fun60.call(args58,kw59)?}};e.set("bb",assigned57.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/data_ring.rs",line!());{let fun63=e.get("text")?.attr("translate")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push({let mut s=Vec::new();s.push(binary("truediv",unary("neg",binary("add",e.get("bb")?.attr("xmin")?,e.get("bb")?.attr("xmax")?)?)?,Val::Int(2i64))?);s.push(binary("sub",binary("sub",e.get("interface")?.attr("THICK")?,e.get("interface")?.attr("INK_DEPTH")?)?,e.get("bb")?.attr("ymin")?)?);s.push(binary("sub",binary("truediv",binary("add",Val::Float(11.0f64),e.get("interface")?.attr("TOP")?)?,Val::Int(2i64))?,binary("truediv",binary("add",e.get("bb")?.attr("zmin")?,e.get("bb")?.attr("zmax")?)?,Val::Int(2i64))?)?);Val::tuple(s)});fun63.call(args61,kw62)?}});
Ok(Val::None)})})?;
    // build_ring
    e.set("build_ring", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun66 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun69 = e.get("interface")?.attr("blank")?;
                            let mut args67 = Vec::new();
                            let mut kw68 = Vec::new();
                            fun69.call(args67, kw68)?
                        }
                    }
                    .attr("cut")?;
                    let mut args64 = Vec::new();
                    let mut kw65 = Vec::new();
                    args64.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun72 = e.get("build_word")?;
                            let mut args70 = Vec::new();
                            let mut kw71 = Vec::new();
                            fun72.call(args70, kw71)?
                        }
                    });
                    fun66.call(args64, kw65)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // build_part
    e.set("build_part", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned73 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun76 = e.get("cq")?.attr("Assembly")?;
                    let mut args74 = Vec::new();
                    let mut kw75 = Vec::new();
                    fun76.call(args74, kw75)?
                }
            };
            e.set("assembly", assigned73.clone())?;
            for item77 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("data-ring".into()));
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun80 = e.get("build_ring")?;
                            let mut args78 = Vec::new();
                            let mut kw79 = Vec::new();
                            fun80.call(args78, kw79)?
                        }
                    });
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun83 = e.get("rear")?.attr("chip_color")?;
                            let mut args81 = Vec::new();
                            let mut kw82 = Vec::new();
                            args81.push(Val::Str("flavor".into()));
                            fun83.call(args81, kw82)?
                        }
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("data-ring-word".into()));
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun86 = e.get("build_word")?;
                            let mut args84 = Vec::new();
                            let mut kw85 = Vec::new();
                            fun86.call(args84, kw85)?
                        }
                    });
                    s.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun89 = e.get("rear")?.attr("word_color")?;
                            let mut args87 = Vec::new();
                            let mut kw88 = Vec::new();
                            args87.push(Val::Str("flavor".into()));
                            fun89.call(args87, kw88)?
                        }
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack90 = unpack(item77, 3)?;
                e.set("name", unpack90[0].clone())?;
                e.set("solid", unpack90[1].clone())?;
                e.set("color", unpack90[2].clone())?;
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                        line!(),
                    );
                    {
                        let fun93 = e.get("assembly")?.attr("add")?;
                        let mut args91 = Vec::new();
                        let mut kw92 = Vec::new();
                        args91.push(e.get("solid")?);
                        kw92.push(("name".into(), e.get("name")?));
                        kw92.push(("color".into(), {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                line!(),
                            );
                            {
                                let fun96 = e.get("step_safe")?;
                                let mut args94 = Vec::new();
                                let mut kw95 = Vec::new();
                                args94.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                        line!(),
                                    );
                                    {
                                        let fun99 = e.get("cq")?.attr("Color")?;
                                        let mut args97 = Vec::new();
                                        let mut kw98 = Vec::new();
                                        args97.extend(
                                            {
                                                let e = e.child();
                                                let out100 = Val::list(vec![]);
                                                for item101 in e.get("color")?.iter()? {
                                                    e.set("c", item101)?;
                                                    out100.attr("append")?.call(
                                                        vec![binary(
                                                            "truediv",
                                                            e.get("c")?,
                                                            Val::Int(255i64),
                                                        )?],
                                                        vec![],
                                                    )?;
                                                }
                                                out100
                                            }
                                            .iter()?,
                                        );
                                        fun99.call(args97, kw98)?
                                    }
                                });
                                fun96.call(args94, kw95)?
                            }
                        }));
                        fun93.call(args91, kw92)?
                    }
                };
            }
            return Ok(e.get("assembly")?);
            Ok(Val::None)
        })
    })?;
    // split
    e.set("split", {
        let params = vec![("shape".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun104 = e.get("ring")?.attr("split")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push(e.get("shape")?);
                    fun104.call(args102, kw103)?
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
            let mod105 = rt.import_module("_cadq_export")?;
            e.set("note_read", rt.member("_cadq_export", "note_read")?)?;
            let mod106 = rt.import_module("_enclosure_data")?;
            e.set("dimensions", rt.member("_enclosure_data", "dimensions")?)?;
            e.set("read", rt.member("_enclosure_data", "read")?)?;
            let assigned107 = binary(
                "truediv",
                e.get("STEP")?.attr("parent")?,
                Val::Str("data-word.json".into()),
            )?;
            e.set("artwork", assigned107.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun110 = e.get("note_read")?;
                    let mut args108 = Vec::new();
                    let mut kw109 = Vec::new();
                    args108.push(e.get("artwork")?);
                    fun110.call(args108, kw109)?
                }
            };
            // color
            e.set("color", {
                let params = vec![("rgb".into(), None, false)];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    return Ok({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun113 = e.get("linear")?;
                            let mut args111 = Vec::new();
                            let mut kw112 = Vec::new();
                            args111.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                    line!(),
                                );
                                {
                                    let fun116 = e.get("step_safe")?;
                                    let mut args114 = Vec::new();
                                    let mut kw115 = Vec::new();
                                    args114.push({
                                        let _site = rt.source_at(
                                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                            line!(),
                                        );
                                        {
                                            let fun119 = e.get("cq")?.attr("Color")?;
                                            let mut args117 = Vec::new();
                                            let mut kw118 = Vec::new();
                                            args117.extend(
                                                {
                                                    let e = e.child();
                                                    let out120 = Val::list(vec![]);
                                                    for item121 in e.get("rgb")?.iter()? {
                                                        e.set("c", item121)?;
                                                        out120.attr("append")?.call(
                                                            vec![binary(
                                                                "truediv",
                                                                e.get("c")?,
                                                                Val::Float(255.0f64),
                                                            )?],
                                                            vec![],
                                                        )?;
                                                    }
                                                    out120
                                                }
                                                .iter()?,
                                            );
                                            fun119.call(args117, kw118)?
                                        }
                                    });
                                    fun116.call(args114, kw115)?
                                }
                            });
                            fun113.call(args111, kw112)?
                        }
                    });
                    Ok(Val::None)
                })
            })?;
            let assigned122 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun125 = e.get("dimensions")?;
                    let mut args123 = Vec::new();
                    let mut kw124 = Vec::new();
                    fun125.call(args123, kw124)?
                }
            };
            e.set("values", assigned122.clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun128 = e.get("read")?;
                    let mut args126 = Vec::new();
                    let mut kw127 = Vec::new();
                    args126.push(Val::Str("data-recipe".into()));
                    kw127.push((
                        "data".into(),
                        e.get("values")?.get(Val::Str("data".into()))?,
                    ));
                    kw127.push((
                        "nameplate".into(),
                        e.get("values")?.get(Val::Str("nameplate".into()))?,
                    ));
                    kw127.push((
                        "bulkhead".into(),
                        e.get("values")?.get(Val::Str("bulkhead".into()))?,
                    ));
                    kw127.push(("artwork_path".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun131 = e.get("str")?;
                            let mut args129 = Vec::new();
                            let mut kw130 = Vec::new();
                            args129.push(e.get("artwork")?);
                            fun131.call(args129, kw130)?
                        }
                    }));
                    kw127.push(("chip_color".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun134 = e.get("color")?;
                            let mut args132 = Vec::new();
                            let mut kw133 = Vec::new();
                            args132.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                    line!(),
                                );
                                {
                                    let fun137 = e.get("rear")?.attr("chip_color")?;
                                    let mut args135 = Vec::new();
                                    let mut kw136 = Vec::new();
                                    args135.push(Val::Str("flavor".into()));
                                    fun137.call(args135, kw136)?
                                }
                            });
                            fun134.call(args132, kw133)?
                        }
                    }));
                    kw127.push(("word_color".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun140 = e.get("color")?;
                            let mut args138 = Vec::new();
                            let mut kw139 = Vec::new();
                            args138.push({
                                let _site = rt.source_at(
                                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                                    line!(),
                                );
                                {
                                    let fun143 = e.get("rear")?.attr("word_color")?;
                                    let mut args141 = Vec::new();
                                    let mut kw142 = Vec::new();
                                    args141.push(Val::Str("flavor".into()));
                                    fun143.call(args141, kw142)?
                                }
                            });
                            fun140.call(args138, kw139)?
                        }
                    }));
                    fun128.call(args126, kw127)?
                }
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
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                    line!(),
                );
                {
                    let fun146 = e.get("_rust_part")?.attr("cut")?;
                    let mut args144 = Vec::new();
                    let mut kw145 = Vec::new();
                    args144.push(Val::Str("enclosure-components".into()));
                    args144.push(Val::Str("data-ring".into()));
                    args144.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
                            line!(),
                        );
                        {
                            let fun149 = e.get("numbers")?;
                            let mut args147 = Vec::new();
                            let mut kw148 = Vec::new();
                            fun149.call(args147, kw148)?
                        }
                    });
                    args144.push(e.get("STEP")?.attr("parent")?);
                    fun146.call(args144, kw145)?
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
            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
            line!(),
        );
        {
            let fun152 = e.get("_rust_part")?.attr("start")?;
            let mut args150 = Vec::new();
            let mut kw151 = Vec::new();
            fun152.call(args150, kw151)?
        }
    };
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/data_ring.rs",
            line!(),
        );
        {
            let fun155 = e.get("main")?;
            let mut args153 = Vec::new();
            let mut kw154 = Vec::new();
            fun155.call(args153, kw154)?
        }
    };
    Ok(Val::None)
}
