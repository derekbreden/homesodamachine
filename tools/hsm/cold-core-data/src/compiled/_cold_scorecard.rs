#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("json", rt.import_module("json")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("dataclasses")?;
    e.set("dataclass", rt.member("dataclasses", "dataclass")?)?;
    e.set("field", rt.member("dataclasses", "field")?)?;
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
    };
    e.set("_here", assigned3.clone())?;
    let assigned10 = {
        let fun13 = e.get("next")?;
        let mut args11 = Vec::new();
        let mut kw12 = Vec::new();
        args11.push({
            let e = e.child();
            let out14 = Val::list(vec![]);
            for item15 in e.get("_here")?.attr("parents")?.iter()? {
                e.set("p", item15)?;
                if {
                    let v16 = e.get("p")?.attr("name")?;
                    let v17 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v16.clone(), v17.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out14.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out14
        });
        fun13.call(args11, kw12)?
    };
    e.set("_hw", assigned10.clone())?;
    let assigned18 = e.get("_hw")?.attr("parent")?;
    e.set("_repo", assigned18.clone())?;
    if {
        let v22 = {
            let fun21 = e.get("str")?;
            let mut args19 = Vec::new();
            let mut kw20 = Vec::new();
            args19.push(binary(
                "truediv",
                e.get("_hw")?,
                Val::Str("scripts".into()),
            )?);
            fun21.call(args19, kw20)?
        };
        let v23 = e.get("sys")?.attr("path")?;
        Val::Bool(compare("not_in", v22.clone(), v23.clone())?.truthy()?)
    }
    .truthy()?
    {
        {
            let fun26 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args24 = Vec::new();
            let mut kw25 = Vec::new();
            args24.push(Val::Int(0i64));
            args24.push({
                let fun29 = e.get("str")?;
                let mut args27 = Vec::new();
                let mut kw28 = Vec::new();
                args27.push(binary(
                    "truediv",
                    e.get("_hw")?,
                    Val::Str("scripts".into()),
                )?);
                fun29.call(args27, kw28)?
            });
            fun26.call(args24, kw25)?
        };
    }
    let mod30 = rt.import_module("_card")?;
    e.set("Check", rt.member("_card", "Check")?)?;
    e.set("verdict", rt.member("_card", "verdict")?)?;
    let assigned31 = Val::Int(8i64);
    e.set("DETAIL_MAX", assigned31.clone())?;
    let assigned32 = Val::Int(24i64);
    e.set("FOCUS_DETAIL_MAX", assigned32.clone())?;
    let assigned33 = {
        let mut s = Vec::new();
        s.push(Val::Str("bom-covered".into()));
        s.push(Val::Str("mounted".into()));
        s.push(Val::Str("inlet-jet-qualified".into()));
        s.push(Val::Str("gas-adapter-envelope".into()));
        Val::tuple(s)
    };
    e.set("FOCUS_IDS", assigned33.clone())?;
    let assigned34 = Val::Float(0.1f64);
    e.set("TOUCH_VOLUME", assigned34.clone())?;
    e.set("Scorecard.gates_pass", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun37 = e.get("all")?;
                let mut args35 = Vec::new();
                let mut kw36 = Vec::new();
                args35.push({
                    let e = e.child();
                    let out38 = Val::list(vec![]);
                    for item39 in e.get("self")?.attr("checks")?.iter()? {
                        e.set("c", item39)?;
                        if {
                            let v40 = e.get("c")?.attr("kind")?;
                            let v41 = Val::Str("gate".into());
                            Val::Bool(compare("eq", v40.clone(), v41.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out38.attr("append")?.call(
                                vec![{
                                    let v42 = e.get("c")?.attr("status")?;
                                    let v43 = Val::Str("fail".into());
                                    Val::Bool(compare("ne", v42.clone(), v43.clone())?.truthy()?)
                                }],
                                vec![],
                            )?;
                        }
                    }
                    out38
                });
                fun37.call(args35, kw36)?
            });
            Ok(Val::None)
        })
    })?;
    e.set("Scorecard", rt.python_type("_cold_scorecard", "Scorecard")?)?;
    // to_dict
    e.set("to_dict", {
        let params = vec![("sc".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("gatesPass".into()),
                    e.get("sc")?.attr("gates_pass")?,
                )?;
                d.set(Val::Str("checks".into()), {
                    let e = e.child();
                    let out44 = Val::list(vec![]);
                    for item45 in e.get("sc")?.attr("checks")?.iter()? {
                        e.set("c", item45)?;
                        out44.attr("append")?.call(
                            vec![{
                                let d = Val::dict(vec![]);
                                d.set(Val::Str("id".into()), e.get("c")?.attr("id")?)?;
                                d.set(Val::Str("label".into()), e.get("c")?.attr("label")?)?;
                                d.set(Val::Str("kind".into()), e.get("c")?.attr("kind")?)?;
                                d.set(Val::Str("status".into()), e.get("c")?.attr("status")?)?;
                                d.set(Val::Str("value".into()), e.get("c")?.attr("value")?)?;
                                d.set(Val::Str("target".into()), e.get("c")?.attr("target")?)?;
                                d.set(Val::Str("detail".into()), {
                                    let fun48 = e.get("list")?;
                                    let mut args46 = Vec::new();
                                    let mut kw47 = Vec::new();
                                    args46.push(e.get("c")?.attr("detail")?);
                                    fun48.call(args46, kw47)?
                                })?;
                                d.set(
                                    Val::Str("active".into()),
                                    if {
                                        let v49 = e.get("c")?.attr("kind")?;
                                        let v50 = Val::Str("goal".into());
                                        Val::Bool(
                                            compare("eq", v49.clone(), v50.clone())?.truthy()?,
                                        )
                                    }
                                    .truthy()?
                                    {
                                        {
                                            let v53 = e.get("c")?.attr("active")?;
                                            if v53.truthy()? {
                                                {
                                                    let v51 = e.get("c")?.attr("id")?;
                                                    let v52 = e.get("FOCUS_IDS")?;
                                                    Val::Bool(
                                                        compare("in", v51.clone(), v52.clone())?
                                                            .truthy()?,
                                                    )
                                                }
                                            } else {
                                                v53
                                            }
                                        }
                                    } else {
                                        e.get("c")?.attr("active")?
                                    },
                                )?;
                                d
                            }],
                            vec![],
                        )?;
                    }
                    out44
                })?;
                d.set(Val::Str("bodies".into()), e.get("sc")?.attr("bodies")?)?;
                d.set(Val::Str("bends".into()), e.get("sc")?.attr("bends")?)?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // write
    e.set("write", {
        let params = vec![("sc".into(), None, false), ("step".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned54 = binary(
                "truediv",
                e.get("step")?.attr("parent")?,
                binary(
                    "add",
                    e.get("step")?.attr("stem")?,
                    Val::Str(".scorecard.json".into()),
                )?,
            )?;
            e.set("out", assigned54.clone())?;
            {
                let fun57 = e.get("out")?.attr("write_text")?;
                let mut args55 = Vec::new();
                let mut kw56 = Vec::new();
                args55.push(binary(
                    "add",
                    {
                        let fun60 = e.get("json")?.attr("dumps")?;
                        let mut args58 = Vec::new();
                        let mut kw59 = Vec::new();
                        args58.push({
                            let fun63 = e.get("to_dict")?;
                            let mut args61 = Vec::new();
                            let mut kw62 = Vec::new();
                            args61.push(e.get("sc")?);
                            fun63.call(args61, kw62)?
                        });
                        kw59.push(("indent".into(), Val::Int(1i64)));
                        fun60.call(args58, kw59)?
                    },
                    Val::Str("\n".into()),
                )?);
                fun57.call(args55, kw56)?
            };
            return Ok(e.get("out")?);
            Ok(Val::None)
        })
    })?;
    // report
    e.set("report", {
        let params = vec![("sc".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun66 = e.get("print")?;
                let mut args64 = Vec::new();
                let mut kw65 = Vec::new();
                args64.push(Val::Str("\nscorecard".into()));
                fun66.call(args64, kw65)?
            };
            for item67 in e.get("sc")?.attr("checks")?.iter()? {
                e.set("c", item67)?;
                let assigned68 = {
                    let d = Val::dict(vec![]);
                    d.set(Val::Str("pass".into()), Val::Str("OK  ".into()))?;
                    d.set(Val::Str("fail".into()), Val::Str("FAIL".into()))?;
                    d.set(Val::Str("warn".into()), Val::Str("    ".into()))?;
                    d
                }
                .get(e.get("c")?.attr("status")?)?;
                e.set("mark", assigned68.clone())?;
                {
                    let fun71 = e.get("print")?;
                    let mut args69 = Vec::new();
                    let mut kw70 = Vec::new();
                    args69.push({
                        let mut str72 = String::new();
                        str72.push_str("  ");
                        str72.push_str(&format(&e.get("mark")?, &String::new())?);
                        str72.push_str(" ");
                        str72.push_str(&format(
                            &e.get("c")?.attr("id")?,
                            &val_string({
                                let mut str73 = String::new();
                                str73.push_str("14");
                                Val::Str(str73)
                            })?,
                        )?);
                        str72.push_str(" ");
                        str72.push_str(&format(
                            &e.get("c")?.attr("value")?,
                            &val_string({
                                let mut str74 = String::new();
                                str74.push_str("34");
                                Val::Str(str74)
                            })?,
                        )?);
                        str72.push_str(" ");
                        str72.push_str(&format(&e.get("c")?.attr("label")?, &String::new())?);
                        Val::Str(str72)
                    });
                    fun71.call(args69, kw70)?
                };
                let assigned75 = if {
                    let v76 = e.get("c")?.attr("id")?;
                    let v77 = e.get("FOCUS_IDS")?;
                    Val::Bool(compare("in", v76.clone(), v77.clone())?.truthy()?)
                }
                .truthy()?
                {
                    e.get("FOCUS_DETAIL_MAX")?
                } else {
                    e.get("DETAIL_MAX")?
                };
                e.set("limit", assigned75.clone())?;
                for item78 in e
                    .get("c")?
                    .attr("detail")?
                    .get(Val::Slice {
                        start: None,
                        stop: Some(e.get("limit")?.integer()?),
                        step: 1,
                    })?
                    .iter()?
                {
                    e.set("line", item78)?;
                    {
                        let fun81 = e.get("print")?;
                        let mut args79 = Vec::new();
                        let mut kw80 = Vec::new();
                        args79.push({
                            let mut str82 = String::new();
                            str82.push_str("         ");
                            str82.push_str(&format(&e.get("line")?, &String::new())?);
                            Val::Str(str82)
                        });
                        fun81.call(args79, kw80)?
                    };
                }
                if {
                    let v86 = {
                        let fun85 = e.get("len")?;
                        let mut args83 = Vec::new();
                        let mut kw84 = Vec::new();
                        args83.push(e.get("c")?.attr("detail")?);
                        fun85.call(args83, kw84)?
                    };
                    let v87 = e.get("limit")?;
                    Val::Bool(compare("gt", v86.clone(), v87.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun90 = e.get("print")?;
                        let mut args88 = Vec::new();
                        let mut kw89 = Vec::new();
                        args88.push({
                            let mut str91 = String::new();
                            str91.push_str("         … ");
                            str91.push_str(&format(
                                &binary(
                                    "sub",
                                    {
                                        let fun94 = e.get("len")?;
                                        let mut args92 = Vec::new();
                                        let mut kw93 = Vec::new();
                                        args92.push(e.get("c")?.attr("detail")?);
                                        fun94.call(args92, kw93)?
                                    },
                                    e.get("limit")?,
                                )?,
                                &String::new(),
                            )?);
                            str91.push_str(" more");
                            Val::Str(str91)
                        });
                        fun90.call(args88, kw89)?
                    };
                }
            }
            if e.get("sc")?.attr("bends")?.truthy()? {
                {
                    let fun97 = e.get("print")?;
                    let mut args95 = Vec::new();
                    let mut kw96 = Vec::new();
                    args95.push(Val::Str("\nlines".into()));
                    fun97.call(args95, kw96)?
                };
                {
                    let fun100 = e.get("print")?;
                    let mut args98 = Vec::new();
                    let mut kw99 = Vec::new();
                    args98.push({
                        let mut str101 = String::new();
                        str101.push_str("  ");
                        str101.push_str(&format(
                            &Val::Str("line".into()),
                            &val_string({
                                let mut str102 = String::new();
                                str102.push_str("18");
                                Val::Str(str102)
                            })?,
                        )?);
                        str101.push_str(" ");
                        str101.push_str(&format(
                            &Val::Str("grade".into()),
                            &val_string({
                                let mut str103 = String::new();
                                str103.push_str("7");
                                Val::Str(str103)
                            })?,
                        )?);
                        str101.push_str(" ");
                        str101.push_str(&format(
                            &Val::Str("length".into()),
                            &val_string({
                                let mut str104 = String::new();
                                str104.push_str(">8");
                                Val::Str(str104)
                            })?,
                        )?);
                        str101.push_str(" ");
                        str101.push_str(&format(
                            &Val::Str("reach".into()),
                            &val_string({
                                let mut str105 = String::new();
                                str105.push_str(">8");
                                Val::Str(str105)
                            })?,
                        )?);
                        str101.push_str(" ");
                        str101.push_str(&format(
                            &Val::Str("detour".into()),
                            &val_string({
                                let mut str106 = String::new();
                                str106.push_str(">7");
                                Val::Str(str106)
                            })?,
                        )?);
                        str101.push_str(" ");
                        str101.push_str(&format(
                            &Val::Str("tightest".into()),
                            &val_string({
                                let mut str107 = String::new();
                                str107.push_str(">9");
                                Val::Str(str107)
                            })?,
                        )?);
                        str101.push_str(" corners");
                        Val::Str(str101)
                    });
                    fun100.call(args98, kw99)?
                };
                for item108 in e.get("sc")?.attr("bends")?.iter()? {
                    e.set("d", item108)?;
                    let assigned109 = e
                        .get("d")?
                        .get(Val::Str("need".into()))?
                        .get(Val::Str("detour".into()))?;
                    e.set("det", assigned109.clone())?;
                    let assigned110 = if {
                        let v111 = e.get("d")?.get(Val::Str("reach".into()))?;
                        let v112 = Val::None;
                        Val::Bool(compare("is", v111.clone(), v112.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        Val::Str("—".into())
                    } else {
                        {
                            let mut str113 = String::new();
                            str113.push_str(&format(
                                &e.get("d")?.get(Val::Str("reach".into()))?,
                                &val_string({
                                    let mut str114 = String::new();
                                    str114.push_str(".1f");
                                    Val::Str(str114)
                                })?,
                            )?);
                            Val::Str(str113)
                        }
                    };
                    e.set("reach", assigned110.clone())?;
                    {
                        let fun117 = e.get("print")?;
                        let mut args115 = Vec::new();
                        let mut kw116 = Vec::new();
                        args115.push({
                            let mut str118 = String::new();
                            str118.push_str("  ");
                            str118.push_str(&format(
                                &e.get("d")?.get(Val::Str("id".into()))?,
                                &val_string({
                                    let mut str119 = String::new();
                                    str119.push_str("18");
                                    Val::Str(str119)
                                })?,
                            )?);
                            str118.push_str(" ");
                            str118.push_str(&format(
                                &{
                                    let fun122 = e.get("str")?;
                                    let mut args120 = Vec::new();
                                    let mut kw121 = Vec::new();
                                    args120.push({
                                        let v123 = e.get("d")?.get(Val::Str("grade".into()))?;
                                        if v123.truthy()? {
                                            v123
                                        } else {
                                            Val::Str("straight".into())
                                        }
                                    });
                                    fun122.call(args120, kw121)?
                                },
                                &val_string({
                                    let mut str124 = String::new();
                                    str124.push_str("7");
                                    Val::Str(str124)
                                })?,
                            )?);
                            str118.push_str(" ");
                            str118.push_str(&format(
                                &e.get("d")?.get(Val::Str("length".into()))?,
                                &val_string({
                                    let mut str125 = String::new();
                                    str125.push_str("8.1f");
                                    Val::Str(str125)
                                })?,
                            )?);
                            str118.push_str(" ");
                            str118.push_str(&format(
                                &e.get("reach")?,
                                &val_string({
                                    let mut str126 = String::new();
                                    str126.push_str(">8");
                                    Val::Str(str126)
                                })?,
                            )?);
                            str118.push_str(" ");
                            str118.push_str(&format(
                                &if {
                                    let v127 = e.get("det")?;
                                    let v128 = Val::None;
                                    Val::Bool(compare("is", v127.clone(), v128.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    Val::Str("    — ".into())
                                } else {
                                    {
                                        let mut str129 = String::new();
                                        str129.push_str(&format(
                                            &e.get("det")?,
                                            &val_string({
                                                let mut str130 = String::new();
                                                str130.push_str("5.2f");
                                                Val::Str(str130)
                                            })?,
                                        )?);
                                        str129.push_str("x");
                                        Val::Str(str129)
                                    }
                                },
                                &String::new(),
                            )?);
                            str118.push_str(" ");
                            str118.push_str(&format(
                                &e.get("d")?.get(Val::Str("radius".into()))?,
                                &val_string({
                                    let mut str131 = String::new();
                                    str131.push_str("9.2f");
                                    Val::Str(str131)
                                })?,
                            )?);
                            str118.push_str(" ");
                            str118.push_str(&format(
                                &{
                                    let fun134 = e.get("len")?;
                                    let mut args132 = Vec::new();
                                    let mut kw133 = Vec::new();
                                    args132.push(e.get("d")?.get(Val::Str("corners".into()))?);
                                    fun134.call(args132, kw133)?
                                },
                                &String::new(),
                            )?);
                            Val::Str(str118)
                        });
                        fun117.call(args115, kw116)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
