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
    {
        let fun38 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args36 = Vec::new();
        let mut kw37 = Vec::new();
        args36.push(Val::Int(0i64));
        args36.push({
            let fun41 = e.get("str")?;
            let mut args39 = Vec::new();
            let mut kw40 = Vec::new();
            args39.push(binary(
                "truediv",
                {
                    let fun44 = e.get("next")?;
                    let mut args42 = Vec::new();
                    let mut kw43 = Vec::new();
                    args42.push({
                        let e = e.child();
                        let out45 = Val::list(vec![]);
                        for item46 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item46)?;
                            if {
                                let v47 = e.get("p")?.attr("name")?;
                                let v48 = Val::Str("printed-parts".into());
                                Val::Bool(compare("eq", v47.clone(), v48.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out45.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out45
                    });
                    fun44.call(args42, kw43)?
                },
                Val::Str("cadlib".into()),
            )?);
            fun41.call(args39, kw40)?
        });
        fun38.call(args36, kw37)?
    };
    {
        let fun51 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args49 = Vec::new();
        let mut kw50 = Vec::new();
        args49.push(Val::Int(0i64));
        args49.push({
            let fun54 = e.get("str")?;
            let mut args52 = Vec::new();
            let mut kw53 = Vec::new();
            args52.push(e.get("_here")?.attr("parents")?.get(Val::Int(1i64))?);
            fun54.call(args52, kw53)?
        });
        fun51.call(args49, kw50)?
    };
    let mod55 = rt.import_module("docgen")?;
    e.set(
        "substitute_py_comments",
        rt.member("docgen", "substitute_py_comments")?,
    )?;
    let mod56 = rt.import_module("_cold_core_interface")?;
    e.set(
        "evap_tail_low_z",
        rt.member("_cold_core_interface", "evap_tail_low_z")?,
    )?;
    e.set(
        "evap_tail_high_z",
        rt.member("_cold_core_interface", "evap_tail_high_z")?,
    )?;
    let assigned57 = binary(
        "truediv",
        {
            let fun60 = e.get("next")?;
            let mut args58 = Vec::new();
            let mut kw59 = Vec::new();
            args58.push({
                let e = e.child();
                let out61 = Val::list(vec![]);
                for item62 in e.get("_here")?.attr("parents")?.iter()? {
                    e.set("p", item62)?;
                    if {
                        let v63 = e.get("p")?.attr("name")?;
                        let v64 = Val::Str("hardware".into());
                        Val::Bool(compare("eq", v63.clone(), v64.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        out61.attr("append")?.call(vec![e.get("p")?], vec![])?;
                    }
                }
                out61
            });
            fun60.call(args58, kw59)?
        },
        Val::Str("cold-core-layout".into()),
    )?;
    e.set("_layout", assigned57.clone())?;
    if {
        let v68 = {
            let fun67 = e.get("str")?;
            let mut args65 = Vec::new();
            let mut kw66 = Vec::new();
            args65.push(e.get("_layout")?);
            fun67.call(args65, kw66)?
        };
        let v69 = e.get("sys")?.attr("path")?;
        Val::Bool(compare("not_in", v68.clone(), v69.clone())?.truthy()?)
    }
    .truthy()?
    {
        {
            let fun72 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args70 = Vec::new();
            let mut kw71 = Vec::new();
            args70.push(Val::Int(0i64));
            args70.push({
                let fun75 = e.get("str")?;
                let mut args73 = Vec::new();
                let mut kw74 = Vec::new();
                args73.push(e.get("_layout")?);
                fun75.call(args73, kw74)?
            });
            fun72.call(args70, kw71)?
        };
    }
    let mod76 = rt.import_module("_cold_core_data")?;
    e.set("_read", rt.member("_cold_core_data", "read")?)?;
    // _recipe
    e.set("_recipe", {
        let params = vec![("op".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, Some("inputs"))?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun79 = e.get("_read")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push(e.get("op")?);
                kw78.push(("evap_tail_low_z".into(), e.get("evap_tail_low_z")?));
                kw78.push(("evap_tail_high_z".into(), e.get("evap_tail_high_z")?));
                kw78.extend(keyword_items(e.get("inputs")?)?);
                fun79.call(args77, kw78)?
            });
            Ok(Val::None)
        })
    })?;
    {
        let fun82 = {
            let fun85 = e.get("globals")?;
            let mut args83 = Vec::new();
            let mut kw84 = Vec::new();
            fun85.call(args83, kw84)?
        }
        .attr("update")?;
        let mut args80 = Vec::new();
        let mut kw81 = Vec::new();
        args80.push({
            let fun88 = e.get("_recipe")?;
            let mut args86 = Vec::new();
            let mut kw87 = Vec::new();
            args86.push(Val::Str("mandrel".into()));
            fun88.call(args86, kw87)?
        });
        fun82.call(args80, kw81)?
    };
    for item89 in {
        let mut s = Vec::new();
        s.push(Val::Str("mandrel_r_range".into()));
        s.push(Val::Str("mandrel_z_range".into()));
        s.push(Val::Str("lower_handle_z_range".into()));
        s.push(Val::Str("wind_z_range".into()));
        s.push(Val::Str("upper_handle_z_range".into()));
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_name", item89)?;
        let assigned90 = {
            let fun93 = e.get("tuple")?;
            let mut args91 = Vec::new();
            let mut kw92 = Vec::new();
            args91.push(
                {
                    let fun96 = e.get("globals")?;
                    let mut args94 = Vec::new();
                    let mut kw95 = Vec::new();
                    fun96.call(args94, kw95)?
                }
                .get(e.get("_name")?)?,
            );
            fun93.call(args91, kw92)?
        };
        {
            let fun99 = e.get("globals")?;
            let mut args97 = Vec::new();
            let mut kw98 = Vec::new();
            fun99.call(args97, kw98)?
        }
        .set(e.get("_name")?, assigned90.clone())?;
    }
    // __getattr__
    e.set("__getattr__", {
        let params = vec![("name".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let v100 = e.get("name")?;
                let v101 = {
                    let mut s = Vec::new();
                    s.push(Val::Str("M_PETG_BLACK".into()));
                    s.push(Val::Str("linear".into()));
                    Val::set_values(s)
                };
                Val::Bool(compare("in", v100.clone(), v101.clone())?.truthy()?)
            }
            .truthy()?
            {
                e.set("_materials", rt.import_module("_materials")?)?;
                return Ok({
                    let fun104 = e.get("getattr")?;
                    let mut args102 = Vec::new();
                    let mut kw103 = Vec::new();
                    args102.push(e.get("_materials")?);
                    args102.push(e.get("name")?);
                    fun104.call(args102, kw103)?
                });
            }
            anyhow::bail!(
                "{}",
                val_string({
                    let fun107 = e.get("AttributeError")?;
                    let mut args105 = Vec::new();
                    let mut kw106 = Vec::new();
                    args105.push(e.get("name")?);
                    fun107.call(args105, kw106)?
                })?
            );
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
            let mod108 = rt.import_module("_materials")?;
            e.set("M_PETG_BLACK", rt.member("_materials", "M_PETG_BLACK")?)?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let fun111 = e.get("_recipe")?;
                let mut args109 = Vec::new();
                let mut kw110 = Vec::new();
                args109.push(Val::Str("mandrel-numbers".into()));
                kw110.push(("color".into(), {
                    let fun114 = e.get("list")?;
                    let mut args112 = Vec::new();
                    let mut kw113 = Vec::new();
                    args112.push({
                        let fun117 = e.get("linear")?;
                        let mut args115 = Vec::new();
                        let mut kw116 = Vec::new();
                        args115.push(e.get("M_PETG_BLACK")?);
                        fun117.call(args115, kw116)?
                    });
                    fun114.call(args112, kw113)?
                }));
                fun111.call(args109, kw110)?
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
                let fun120 = e.get("print")?;
                let mut args118 = Vec::new();
                let mut kw119 = Vec::new();
                args118.push({
                    let fun123 = e.get("_recipe")?;
                    let mut args121 = Vec::new();
                    let mut kw122 = Vec::new();
                    args121.push(Val::Str("mandrel-report".into()));
                    fun123.call(args121, kw122)?
                });
                kw119.push(("end".into(), Val::Str("".into())));
                fun120.call(args118, kw119)?
            };
            let assigned124 = {
                let fun127 = e.get("_rust_part")?.attr("cut")?;
                let mut args125 = Vec::new();
                let mut kw126 = Vec::new();
                args125.push(Val::Str("cold-core".into()));
                args125.push(Val::Str("coil-mandrel".into()));
                args125.push({
                    let fun130 = e.get("numbers")?;
                    let mut args128 = Vec::new();
                    let mut kw129 = Vec::new();
                    fun130.call(args128, kw129)?
                });
                args125.push(e.get("_here")?.attr("parent")?);
                fun127.call(args125, kw126)?
            };
            e.set("said", assigned124.clone())?;
            let assigned131 = e
                .get("said")?
                .get(Val::Str("bodies".into()))?
                .get(Val::Int(0i64))?;
            e.set("body", assigned131.clone())?;
            let assigned132 = {
                let mut s = Vec::new();
                s.push(e.get("body")?.get(Val::Str("min".into()))?);
                s.push(e.get("body")?.get(Val::Str("max".into()))?);
                Val::tuple(s)
            };
            let unpack133 = unpack(assigned132.clone(), 2)?;
            let unpack134 = unpack(unpack133[0].clone(), 3)?;
            e.set("xmin", unpack134[0].clone())?;
            e.set("ymin", unpack134[1].clone())?;
            e.set("zmin", unpack134[2].clone())?;
            let unpack135 = unpack(unpack133[1].clone(), 3)?;
            e.set("xmax", unpack135[0].clone())?;
            e.set("ymax", unpack135[1].clone())?;
            e.set("zmax", unpack135[2].clone())?;
            {
                let fun138 = e.get("print")?;
                let mut args136 = Vec::new();
                let mut kw137 = Vec::new();
                args136.push({
                    let mut str139 = String::new();
                    str139.push_str("\nResult: X[");
                    str139.push_str(&format(
                        &e.get("xmin")?,
                        &val_string({
                            let mut str140 = String::new();
                            str140.push_str(".1f");
                            Val::Str(str140)
                        })?,
                    )?);
                    str139.push_str(",");
                    str139.push_str(&format(
                        &e.get("xmax")?,
                        &val_string({
                            let mut str141 = String::new();
                            str141.push_str(".1f");
                            Val::Str(str141)
                        })?,
                    )?);
                    str139.push_str("] Y[");
                    str139.push_str(&format(
                        &e.get("ymin")?,
                        &val_string({
                            let mut str142 = String::new();
                            str142.push_str(".1f");
                            Val::Str(str142)
                        })?,
                    )?);
                    str139.push_str(",");
                    str139.push_str(&format(
                        &e.get("ymax")?,
                        &val_string({
                            let mut str143 = String::new();
                            str143.push_str(".1f");
                            Val::Str(str143)
                        })?,
                    )?);
                    str139.push_str("] Z[");
                    str139.push_str(&format(
                        &e.get("zmin")?,
                        &val_string({
                            let mut str144 = String::new();
                            str144.push_str(".1f");
                            Val::Str(str144)
                        })?,
                    )?);
                    str139.push_str(",");
                    str139.push_str(&format(
                        &e.get("zmax")?,
                        &val_string({
                            let mut str145 = String::new();
                            str145.push_str(".1f");
                            Val::Str(str145)
                        })?,
                    )?);
                    str139.push_str("], V=");
                    str139.push_str(&format(
                        &e.get("body")?.get(Val::Str("volume".into()))?,
                        &val_string({
                            let mut str146 = String::new();
                            str146.push_str(".0f");
                            Val::Str(str146)
                        })?,
                    )?);
                    str139.push_str(" mm^3, ");
                    str139.push_str(&format(
                        &e.get("body")?.get(Val::Str("triangles".into()))?,
                        &String::new(),
                    )?);
                    str139.push_str(" triangles");
                    Val::Str(str139)
                });
                fun138.call(args136, kw137)?
            };
            {
                let fun149 = e.get("print")?;
                let mut args147 = Vec::new();
                let mut kw148 = Vec::new();
                args147.push(binary("add", Val::Str("-> ".into()), {
                    let fun152 = Val::Str(", ".into()).attr("join")?;
                    let mut args150 = Vec::new();
                    let mut kw151 = Vec::new();
                    args150.push(e.get("said")?.get(Val::Str("files".into()))?);
                    fun152.call(args150, kw151)?
                })?);
                fun149.call(args147, kw148)?
            };
            let assigned153 = {
                let fun156 = e.get("_recipe")?;
                let mut args154 = Vec::new();
                let mut kw155 = Vec::new();
                args154.push(Val::Str("mandrel-variables".into()));
                fun156.call(args154, kw155)?
            };
            e.set("variables", assigned153.clone())?;
            {
                let fun159 = e.get("substitute_py_comments")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                args157.push({
                    let fun162 = e.get("Path")?;
                    let mut args160 = Vec::new();
                    let mut kw161 = Vec::new();
                    args160.push(e.get("__file__")?);
                    fun162.call(args160, kw161)?
                });
                kw158.push(("variables".into(), e.get("variables")?));
                fun159.call(args157, kw158)?
            };
            {
                let fun165 = e.get("print")?;
                let mut args163 = Vec::new();
                let mut kw164 = Vec::new();
                args163.push({
                    let mut str166 = String::new();
                    str166.push_str("-> ");
                    str166.push_str(&format(
                        &{
                            let fun169 = e.get("Path")?;
                            let mut args167 = Vec::new();
                            let mut kw168 = Vec::new();
                            args167.push(e.get("__file__")?);
                            fun169.call(args167, kw168)?
                        }
                        .attr("name")?,
                        &String::new(),
                    )?);
                    Val::Str(str166)
                });
                fun165.call(args163, kw164)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun172 = e.get("_rust_part")?.attr("start")?;
        let mut args170 = Vec::new();
        let mut kw171 = Vec::new();
        fun172.call(args170, kw171)?
    };
    {
        let fun175 = e.get("main")?;
        let mut args173 = Vec::new();
        let mut kw174 = Vec::new();
        fun175.call(args173, kw174)?
    };
    Ok(Val::None)
}
