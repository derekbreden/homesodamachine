//! Doc-sync driver for hardware/printed-parts/enclosure/nameplate/README.md.
//!
//! Run: tools/cad-venv/bin/python hardware/printed-parts/enclosure/nameplate/_nameplate_dimensions.py
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
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
    }
    .attr("parent")?;
    e.set("_here", assigned2.clone())?;
    let assigned9 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
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
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                            line!(),
                        );
                        {
                            let fun17 = binary(
                                "truediv",
                                binary("truediv", e.get("p")?, Val::Str("tools".into()))?,
                                Val::Str("docgen".into()),
                            )?
                            .attr("is_dir")?;
                            let mut args15 = Vec::new();
                            let mut kw16 = Vec::new();
                            fun17.call(args15, kw16)?
                        }
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
    e.set("_root", assigned9.clone())?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
            line!(),
        );
        {
            let fun20 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args18 = Vec::new();
            let mut kw19 = Vec::new();
            args18.push(Val::Int(0i64));
            args18.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun23 = e.get("str")?;
                    let mut args21 = Vec::new();
                    let mut kw22 = Vec::new();
                    args21.push(binary(
                        "truediv",
                        e.get("_root")?,
                        Val::Str("tools".into()),
                    )?);
                    fun23.call(args21, kw22)?
                }
            });
            fun20.call(args18, kw19)?
        }
    };
    let mod24 = rt.import_module("docgen")?;
    e.set("substitute_md", rt.member("docgen", "substitute_md")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
            line!(),
        );
        {
            let fun27 = e.get("sys")?.attr("path")?.attr("insert")?;
            let mut args25 = Vec::new();
            let mut kw26 = Vec::new();
            args25.push(Val::Int(0i64));
            args25.push({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun30 = e.get("str")?;
                    let mut args28 = Vec::new();
                    let mut kw29 = Vec::new();
                    args28.push(binary(
                        "truediv",
                        e.get("_root")?,
                        Val::Str("hardware/printed-parts/enclosure/enclosure".into()),
                    )?);
                    fun30.call(args28, kw29)?
                }
            });
            fun27.call(args25, kw26)?
        }
    };
    let mod31 = rt.import_module("_enclosure_data")?;
    e.set("_dimensions", rt.member("_enclosure_data", "dimensions")?)?;
    e.set("_read", rt.member("_enclosure_data", "read")?)?;
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
            line!(),
        );
        {
            let fun34 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun37 = e.get("globals")?;
                    let mut args35 = Vec::new();
                    let mut kw36 = Vec::new();
                    fun37.call(args35, kw36)?
                }
            }
            .attr("update")?;
            let mut args32 = Vec::new();
            let mut kw33 = Vec::new();
            args32.push(
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                        line!(),
                    );
                    {
                        let fun40 = e.get("_dimensions")?;
                        let mut args38 = Vec::new();
                        let mut kw39 = Vec::new();
                        fun40.call(args38, kw39)?
                    }
                }
                .get(Val::Str("plan".into()))?,
            );
            fun34.call(args32, kw33)?
        }
    };
    // serial_of
    e.set("serial_of", {
        let params = vec![("unit".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun43 = e.get("_read")?;
                    let mut args41 = Vec::new();
                    let mut kw42 = Vec::new();
                    args41.push(Val::Str("nameplate-unit".into()));
                    kw42.push(("unit".into(), e.get("unit")?));
                    kw42.push(("portal_host".into(), e.get("portal_host")?));
                    fun43.call(args41, kw42)?
                }
            }
            .get(Val::Str("serial".into()))?);
            Ok(Val::None)
        })
    })?;
    // unit_url
    e.set("unit_url", {
        let params = vec![("unit".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun46 = e.get("_read")?;
                    let mut args44 = Vec::new();
                    let mut kw45 = Vec::new();
                    args44.push(Val::Str("nameplate-unit".into()));
                    kw45.push(("unit".into(), e.get("unit")?));
                    kw45.push(("portal_host".into(), e.get("portal_host")?));
                    fun46.call(args44, kw45)?
                }
            }
            .get(Val::Str("url".into()))?);
            Ok(Val::None)
        })
    })?;
    // unit_url_plain
    e.set("unit_url_plain", {
        let params = vec![("unit".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun49 = e.get("_read")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    args47.push(Val::Str("nameplate-unit".into()));
                    kw48.push(("unit".into(), e.get("unit")?));
                    kw48.push(("portal_host".into(), e.get("portal_host")?));
                    fun49.call(args47, kw48)?
                }
            }
            .get(Val::Str("plain".into()))?);
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
            let assigned50 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun53 = e.get("_read")?;
                    let mut args51 = Vec::new();
                    let mut kw52 = Vec::new();
                    args51.push(Val::Str("plan-variables".into()));
                    kw52.push((
                        "plan".into(),
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                                line!(),
                            );
                            {
                                let fun56 = e.get("_dimensions")?;
                                let mut args54 = Vec::new();
                                let mut kw55 = Vec::new();
                                fun56.call(args54, kw55)?
                            }
                        }
                        .get(Val::Str("plan".into()))?,
                    ));
                    fun53.call(args51, kw52)?
                }
            };
            e.set("variables", assigned50.clone())?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun59 = e.get("substitute_md")?;
                    let mut args57 = Vec::new();
                    let mut kw58 = Vec::new();
                    args57.push(binary(
                        "truediv",
                        e.get("_here")?,
                        Val::Str("README.md".into()),
                    )?);
                    kw58.push(("variables".into(), e.get("variables")?));
                    fun59.call(args57, kw58)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun62 = e.get("print")?;
                    let mut args60 = Vec::new();
                    let mut kw61 = Vec::new();
                    args60.push(Val::Str("-> README.md".into()));
                    fun62.call(args60, kw61)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun65 = e.get("substitute_md")?;
                    let mut args63 = Vec::new();
                    let mut kw64 = Vec::new();
                    args63.push(binary(
                        "truediv",
                        binary("truediv", e.get("_root")?, Val::Str("future".into()))?,
                        Val::Str("unit-links.md".into()),
                    )?);
                    kw64.push(("variables".into(), e.get("variables")?));
                    fun65.call(args63, kw64)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
                    line!(),
                );
                {
                    let fun68 = e.get("print")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    args66.push(Val::Str("-> future/unit-links.md".into()));
                    fun68.call(args66, kw67)?
                }
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/_nameplate_dimensions.rs",
            line!(),
        );
        {
            let fun71 = e.get("main")?;
            let mut args69 = Vec::new();
            let mut kw70 = Vec::new();
            fun71.call(args69, kw70)?
        }
    };
    Ok(Val::None)
}
