//! Guide recipe: `hardware/install-guide/plumbing/modern/render_modern_tee.py`.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    e.set("tempfile", rt.import_module("tempfile")?)?;
    e.set("shutil", rt.import_module("shutil")?)?;
    let mod1 = rt.import_module("dataclasses")?;
    e.set("dataclass", rt.member("dataclasses", "dataclass")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
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
    let assigned10 = {
        let fun13 = e.get("next")?;
        let mut args11 = Vec::new();
        let mut kw12 = Vec::new();
        args11.push({
            let e = e.child();
            let out14 = Val::list(vec![]);
            for item15 in e.get("HERE")?.attr("parents")?.iter()? {
                e.set("parent", item15)?;
                if {
                    let v16 = e.get("parent")?.attr("name")?;
                    let v17 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v16.clone(), v17.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out14.attr("append")?.call(vec![e.get("parent")?], vec![])?;
                }
            }
            out14
        });
        fun13.call(args11, kw12)?
    };
    e.set("HARDWARE", assigned10.clone())?;
    let assigned18 = e.get("HARDWARE")?.attr("parent")?;
    e.set("ROOT", assigned18.clone())?;
    let assigned19 = binary("truediv", e.get("HERE")?, Val::Str("art".into()))?;
    e.set("ART", assigned19.clone())?;
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
                Val::Str("install-guide".into()),
            )?);
            fun31.call(args29, kw30)?
        });
        fun28.call(args26, kw27)?
    };
    {
        let fun34 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args32 = Vec::new();
        let mut kw33 = Vec::new();
        args32.push(Val::Int(0i64));
        args32.push({
            let fun37 = e.get("str")?;
            let mut args35 = Vec::new();
            let mut kw36 = Vec::new();
            args35.push(binary(
                "truediv",
                binary("truediv", e.get("HARDWARE")?, Val::Str("reference".into()))?,
                Val::Str("jg-pp0408w".into()),
            )?);
            fun37.call(args35, kw36)?
        });
        fun34.call(args32, kw33)?
    };
    let mod38 = rt.import_module("_plumbing_art_mesh")?;
    e.set("note_write", rt.member("_plumbing_art_mesh", "note_write")?)?;
    e.set("_hsm_render", rt.import_module("_hsm_render")?)?;
    e.set("union_ref", rt.import_module("jg_pp0408w")?)?;
    e.set("View", rt.python_type("render_modern_tee", "View")?)?;
    let mod39 = rt.import_module("_rust_data")?;
    e.set("_data_request", rt.member("_rust_data", "request")?)?;
    // _plumbing_data
    e.set("_plumbing_data", {
        let params = vec![("fn".into(), Some(Val::Str("datums".into())), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, Some("values"))?;
            let _frame = rt.frame(&outer);
            if {
                let v40 = e.get("fn")?;
                let v41 = Val::Str("datums".into());
                Val::Bool(compare("eq", v40.clone(), v41.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun44 = e.get("values")?.attr("update")?;
                    let mut args42 = Vec::new();
                    let mut kw43 = Vec::new();
                    kw43.push(("union_reach".into(), {
                        let fun47 = e.get("union_ref")?.attr("reach")?;
                        let mut args45 = Vec::new();
                        let mut kw46 = Vec::new();
                        fun47.call(args45, kw46)?
                    }));
                    kw43.push((
                        "union_insertion".into(),
                        e.get("union_ref")?.attr("INSERTION")?,
                    ));
                    fun44.call(args42, kw43)?
                };
            }
            return Ok({
                let fun50 = e.get("_data_request")?;
                let mut args48 = Vec::new();
                let mut kw49 = Vec::new();
                args48.push(Val::Str("faucet-data".into()));
                args48.push(Val::Str("faucet-data".into()));
                args48.push({
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("op".into()), Val::Str("plumbing".into()))?;
                    d.set(Val::Str("fn".into()), e.get("fn")?)?;
                    d.set(Val::Str("root".into()), {
                        let fun53 = e.get("str")?;
                        let mut args51 = Vec::new();
                        let mut kw52 = Vec::new();
                        args51.push(e.get("ROOT")?);
                        fun53.call(args51, kw52)?
                    })?;
                    d.set(Val::Str("modern".into()), Val::Bool(true))?;
                    dict_extend(&d, e.get("values")?)?;
                    d
                });
                fun50.call(args48, kw49)?
            });
            Ok(Val::None)
        })
    })?;
    let assigned54 = {
        let fun57 = e.get("_plumbing_data")?;
        let mut args55 = Vec::new();
        let mut kw56 = Vec::new();
        fun57.call(args55, kw56)?
    };
    e.set("_plumbing_values", assigned54.clone())?;
    for item58 in {
        let fun83 = e.get("_plumbing_values")?.attr("items")?;
        let mut args81 = Vec::new();
        let mut kw82 = Vec::new();
        fun83.call(args81, kw82)?
    }
    .iter()?
    {
        let unpack84 = unpack(item58, 2)?;
        e.set("_name", unpack84[0].clone())?;
        e.set("_value", unpack84[1].clone())?;
        if {
            let fun61 = e.get("_name")?.attr("endswith")?;
            let mut args59 = Vec::new();
            let mut kw60 = Vec::new();
            args59.push(Val::Str("_VIEW".into()));
            fun61.call(args59, kw60)?
        }
        .truthy()?
        {
            let assigned62 = {
                let fun65 = e.get("View")?;
                let mut args63 = Vec::new();
                let mut kw64 = Vec::new();
                args63.push({
                    let fun68 = e.get("tuple")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    args66.push(e.get("_value")?.get(Val::Str("camera".into()))?);
                    fun68.call(args66, kw67)?
                });
                args63.push({
                    let fun71 = e.get("tuple")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    args69.push(e.get("_value")?.get(Val::Str("target".into()))?);
                    fun71.call(args69, kw70)?
                });
                args63.push(e.get("_value")?.get(Val::Str("span".into()))?);
                fun65.call(args63, kw64)?
            };
            {
                let fun74 = e.get("globals")?;
                let mut args72 = Vec::new();
                let mut kw73 = Vec::new();
                fun74.call(args72, kw73)?
            }
            .set(e.get("_name")?, assigned62.clone())?;
        } else {
            if {
                let v75 = e.get("_name")?;
                let v76 = Val::Str("SCENES".into());
                Val::Bool(compare("ne", v75.clone(), v76.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned77 = e.get("_value")?;
                {
                    let fun80 = e.get("globals")?;
                    let mut args78 = Vec::new();
                    let mut kw79 = Vec::new();
                    fun80.call(args78, kw79)?
                }
                .set(e.get("_name")?, assigned77.clone())?;
            }
        }
    }
    let assigned85 = {
        let fun88 = e.get("tuple")?;
        let mut args86 = Vec::new();
        let mut kw87 = Vec::new();
        args86.push({
            let e = e.child();
            let out89 = Val::list(vec![]);
            for item90 in e
                .get("_plumbing_values")?
                .get(Val::Str("SCENES".into()))?
                .iter()?
            {
                let unpack91 = unpack(item90, 2)?;
                e.set("name", unpack91[0].clone())?;
                e.set("view", unpack91[1].clone())?;
                out89.attr("append")?.call(
                    vec![{
                        let mut s = Vec::new();
                        s.push(e.get("name")?);
                        s.push({
                            let fun94 = e.get("View")?;
                            let mut args92 = Vec::new();
                            let mut kw93 = Vec::new();
                            args92.push({
                                let fun97 = e.get("tuple")?;
                                let mut args95 = Vec::new();
                                let mut kw96 = Vec::new();
                                args95.push(e.get("view")?.get(Val::Str("camera".into()))?);
                                fun97.call(args95, kw96)?
                            });
                            args92.push({
                                let fun100 = e.get("tuple")?;
                                let mut args98 = Vec::new();
                                let mut kw99 = Vec::new();
                                args98.push(e.get("view")?.get(Val::Str("target".into()))?);
                                fun100.call(args98, kw99)?
                            });
                            args92.push(e.get("view")?.get(Val::Str("span".into()))?);
                            fun94.call(args92, kw93)?
                        });
                        Val::tuple(s)
                    }],
                    vec![],
                )?;
            }
            out89
        });
        fun88.call(args86, kw87)?
    };
    e.set("SCENES", assigned85.clone())?;
    // _canonicalize_png
    e.set("_canonicalize_png", {
        let params = vec![("path".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun103 = e.get("_plumbing_data")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                args101.push(Val::Str("canonicalize-png".into()));
                kw102.push(("path".into(), {
                    let fun106 = e.get("str")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push(e.get("path")?);
                    fun106.call(args104, kw105)?
                }));
                fun103.call(args101, kw102)?
            };
            Ok(Val::None)
        })
    })?;
    // _job
    e.set("_job", {
        let params = vec![
            ("step".into(), None, false),
            ("output".into(), None, false),
            ("view".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun109 = e.get("_plumbing_data")?;
                let mut args107 = Vec::new();
                let mut kw108 = Vec::new();
                args107.push(Val::Str("job".into()));
                kw108.push(("step".into(), {
                    let fun112 = e.get("str")?;
                    let mut args110 = Vec::new();
                    let mut kw111 = Vec::new();
                    args110.push(e.get("step")?);
                    fun112.call(args110, kw111)?
                }));
                kw108.push(("output".into(), {
                    let fun115 = e.get("str")?;
                    let mut args113 = Vec::new();
                    let mut kw114 = Vec::new();
                    args113.push(e.get("output")?);
                    fun115.call(args113, kw114)?
                }));
                kw108.push(("view".into(), {
                    let fun118 = e.get("vars")?;
                    let mut args116 = Vec::new();
                    let mut kw117 = Vec::new();
                    args116.push(e.get("view")?);
                    fun118.call(args116, kw117)?
                }));
                fun109.call(args107, kw108)?
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
            {
                let fun121 = e.get("ART")?.attr("mkdir")?;
                let mut args119 = Vec::new();
                let mut kw120 = Vec::new();
                kw120.push(("parents".into(), Val::Bool(true)));
                kw120.push(("exist_ok".into(), Val::Bool(true)));
                fun121.call(args119, kw120)?
            };
            let assigned122 = binary("truediv", e.get("HERE")?, Val::Str("out".into()))?;
            e.set("shared", assigned122.clone())?;
            {
                let fun125 = e.get("shared")?.attr("mkdir")?;
                let mut args123 = Vec::new();
                let mut kw124 = Vec::new();
                kw124.push(("parents".into(), Val::Bool(true)));
                kw124.push(("exist_ok".into(), Val::Bool(true)));
                fun125.call(args123, kw124)?
            };
            e.set("outputs", {
                let mut s = Vec::new();
                Val::list(s)
            })?;
            let context126 = {
                let fun129 = e.get("tempfile")?.attr("TemporaryDirectory")?;
                let mut args127 = Vec::new();
                let mut kw128 = Vec::new();
                kw128.push(("prefix".into(), Val::Str(".modern-pushfit-".into())));
                kw128.push(("dir".into(), e.get("HERE")?));
                fun129.call(args127, kw128)?
            };
            e.set(
                "directory",
                context126.attr("__enter__")?.call(vec![], vec![])?,
            )?;
            let context_result188 = (|| -> Result<Flow> {
                let assigned130 = {
                    let fun133 = e.get("Path")?;
                    let mut args131 = Vec::new();
                    let mut kw132 = Vec::new();
                    args131.push(e.get("directory")?);
                    fun133.call(args131, kw132)?
                };
                e.set("work", assigned130.clone())?;
                let mod134 = rt.import_module("_plumbing_art_mesh")?;
                e.set("export", rt.member("_plumbing_art_mesh", "export")?)?;
                let assigned135 = {
                    let fun138 = e.get("export")?;
                    let mut args136 = Vec::new();
                    let mut kw137 = Vec::new();
                    args136.push(e.namespace());
                    args136.push({
                        let e = e.child();
                        let out139 = Val::list(vec![]);
                        for item140 in e.get("SCENES")?.iter()? {
                            let unpack141 = unpack(item140, 2)?;
                            e.set("name", unpack141[0].clone())?;
                            e.set("_", unpack141[1].clone())?;
                            out139.attr("append")?.call(vec![e.get("name")?], vec![])?;
                        }
                        out139
                    });
                    args136.push(e.get("work")?);
                    kw137.push(("modern".into(), Val::Bool(true)));
                    fun138.call(args136, kw137)?
                };
                e.set("steps", assigned135.clone())?;
                let assigned142 = {
                    let mut s = Vec::new();
                    Val::list(s)
                };
                e.set("jobs", assigned142.clone())?;
                for item143 in e.get("SCENES")?.iter()? {
                    let unpack177 = unpack(item143, 2)?;
                    e.set("name", unpack177[0].clone())?;
                    e.set("view", unpack177[1].clone())?;
                    let assigned144 = binary(
                        "truediv",
                        if {
                            let v145 = e.get("name")?;
                            let v146 = Val::Str("modern-water-on".into());
                            Val::Bool(compare("eq", v145.clone(), v146.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            e.get("shared")?
                        } else {
                            e.get("work")?
                        },
                        {
                            let mut str147 = String::new();
                            str147.push_str(&format(&e.get("name")?, &String::new())?);
                            str147.push_str(".step");
                            Val::Str(str147)
                        },
                    )?;
                    e.set("step", assigned144.clone())?;
                    let assigned148 = binary("truediv", e.get("ART")?, {
                        let mut str149 = String::new();
                        str149.push_str(&format(&e.get("name")?, &String::new())?);
                        str149.push_str(".png");
                        Val::Str(str149)
                    })?;
                    e.set("output", assigned148.clone())?;
                    if {
                        let v150 = e.get("name")?;
                        let v151 = Val::Str("modern-water-on".into());
                        Val::Bool(compare("eq", v150.clone(), v151.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        for item152 in {
                            let fun161 = e.get("_plumbing_data")?;
                            let mut args159 = Vec::new();
                            let mut kw160 = Vec::new();
                            args159.push(Val::Str("copy-step".into()));
                            kw160.push(("source".into(), {
                                let fun164 = e.get("str")?;
                                let mut args162 = Vec::new();
                                let mut kw163 = Vec::new();
                                args162.push(e.get("steps")?.get(e.get("name")?)?);
                                fun164.call(args162, kw163)?
                            }));
                            kw160.push(("target".into(), {
                                let fun167 = e.get("str")?;
                                let mut args165 = Vec::new();
                                let mut kw166 = Vec::new();
                                args165.push(e.get("step")?);
                                fun167.call(args165, kw166)?
                            }));
                            fun161.call(args159, kw160)?
                        }
                        .iter()?
                        {
                            e.set("target", item152)?;
                            {
                                let fun155 = e.get("note_write")?;
                                let mut args153 = Vec::new();
                                let mut kw154 = Vec::new();
                                args153.push({
                                    let fun158 = e.get("Path")?;
                                    let mut args156 = Vec::new();
                                    let mut kw157 = Vec::new();
                                    args156.push(e.get("target")?);
                                    fun158.call(args156, kw157)?
                                });
                                fun155.call(args153, kw154)?
                            };
                        }
                    }
                    {
                        let fun170 = e.get("jobs")?.attr("append")?;
                        let mut args168 = Vec::new();
                        let mut kw169 = Vec::new();
                        args168.push({
                            let fun173 = e.get("_job")?;
                            let mut args171 = Vec::new();
                            let mut kw172 = Vec::new();
                            args171.push(e.get("step")?);
                            args171.push(e.get("output")?);
                            args171.push(e.get("view")?);
                            fun173.call(args171, kw172)?
                        });
                        fun170.call(args168, kw169)?
                    };
                    {
                        let fun176 = e.get("outputs")?.attr("append")?;
                        let mut args174 = Vec::new();
                        let mut kw175 = Vec::new();
                        args174.push(e.get("output")?);
                        fun176.call(args174, kw175)?
                    };
                }
                {
                    let fun180 = e.get("_hsm_render")?.attr("render")?;
                    let mut args178 = Vec::new();
                    let mut kw179 = Vec::new();
                    args178.push(e.get("jobs")?);
                    fun180.call(args178, kw179)?
                };
                for item181 in e.get("outputs")?.iter()? {
                    e.set("output", item181)?;
                    {
                        let fun184 = e.get("_canonicalize_png")?;
                        let mut args182 = Vec::new();
                        let mut kw183 = Vec::new();
                        args182.push(e.get("output")?);
                        fun184.call(args182, kw183)?
                    };
                    {
                        let fun187 = e.get("note_write")?;
                        let mut args185 = Vec::new();
                        let mut kw186 = Vec::new();
                        args185.push(e.get("output")?);
                        fun187.call(args185, kw186)?
                    };
                }
                Ok(Flow::Continue)
            })();
            context126
                .attr("__exit__")?
                .call(vec![Val::None, Val::None, Val::None], vec![])?;
            match context_result188? {
                Flow::Continue => {}
                Flow::Return(value) => return Ok(value),
                Flow::Break => anyhow::bail!("break outside a loop"),
                Flow::Next => anyhow::bail!("continue outside a loop"),
            }
            {
                let fun191 = e.get("print")?;
                let mut args189 = Vec::new();
                let mut kw190 = Vec::new();
                args189.push(Val::Str("modern push-connect installation art:".into()));
                fun191.call(args189, kw190)?
            };
            for item192 in e.get("outputs")?.iter()? {
                e.set("output", item192)?;
                {
                    let fun195 = e.get("print")?;
                    let mut args193 = Vec::new();
                    let mut kw194 = Vec::new();
                    args193.push({
                        let mut str196 = String::new();
                        str196.push_str("  ");
                        str196.push_str(&format(&e.get("output")?, &String::new())?);
                        Val::Str(str196)
                    });
                    fun195.call(args193, kw194)?
                };
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun199 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args197 = Vec::new();
        let mut kw198 = Vec::new();
        args197.push(Val::Int(0i64));
        args197.push({
            let fun202 = e.get("str")?;
            let mut args200 = Vec::new();
            let mut kw201 = Vec::new();
            args200.push(binary(
                "truediv",
                {
                    let fun205 = {
                        let fun208 = e.get("Path")?;
                        let mut args206 = Vec::new();
                        let mut kw207 = Vec::new();
                        args206.push(e.get("__file__")?);
                        fun208.call(args206, kw207)?
                    }
                    .attr("resolve")?;
                    let mut args203 = Vec::new();
                    let mut kw204 = Vec::new();
                    fun205.call(args203, kw204)?
                }
                .attr("parents")?
                .get(Val::Int(3i64))?,
                Val::Str("scripts".into()),
            )?);
            fun202.call(args200, kw201)?
        });
        fun199.call(args197, kw198)?
    };
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun211 = e.get("_rust_part")?.attr("start")?;
        let mut args209 = Vec::new();
        let mut kw210 = Vec::new();
        fun211.call(args209, kw210)?
    };
    {
        let fun214 = e.get("main")?;
        let mut args212 = Vec::new();
        let mut kw213 = Vec::new();
        fun214.call(args212, kw213)?
    };
    Ok(Val::None)
}
