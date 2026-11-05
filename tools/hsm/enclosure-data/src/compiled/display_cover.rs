//! Accepted face-up display bezel with coplanar horizontal retaining wings.
//!
//! The visible face is local Z=0. The back and both wings share one flat bed plane.
//! The TPU ring separates the bezel from the glass.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let assigned2 = {
        let _site = rt.source_at(
            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
            line!(),
        );
        {
            let fun5 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
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
            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
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
    for item17 in {
        let mut s = Vec::new();
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("scripts".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("_hw")?,
            Val::Str("printed-parts/enclosure/enclosure".into()),
        )?);
        s.push(binary(
            "truediv",
            e.get("_hw")?.attr("parent")?,
            Val::Str("tools".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("directory", item17)?;
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                line!(),
            );
            {
                let fun20 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(Val::Int(0i64));
                args18.push({
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                        line!(),
                    );
                    {
                        let fun23 = e.get("str")?;
                        let mut args21 = Vec::new();
                        let mut kw22 = Vec::new();
                        args21.push(e.get("directory")?);
                        fun23.call(args21, kw22)?
                    }
                });
                fun20.call(args18, kw19)?
            }
        };
    }
    if {
        let v32 = {
            let v33 = e.get("__name__")?;
            let v34 = Val::Str("__main__".into());
            Val::Bool(compare("eq", v33.clone(), v34.clone())?.truthy()?)
        };
        if v32.truthy()? {
            unary("not", {
                let v26 = {
                    let v30 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun29 = e.get("len")?;
                            let mut args27 = Vec::new();
                            let mut kw28 = Vec::new();
                            args27.push(e.get("sys")?.attr("argv")?);
                            fun29.call(args27, kw28)?
                        }
                    };
                    let v31 = Val::Int(1i64);
                    Val::Bool(compare("gt", v30.clone(), v31.clone())?.truthy()?)
                };
                if v26.truthy()? {
                    {
                        let v24 = e.get("sys")?.attr("argv")?.get(Val::Int(1i64))?;
                        let v25 = Val::Str("selftest".into());
                        Val::Bool(compare("eq", v24.clone(), v25.clone())?.truthy()?)
                    }
                } else {
                    v26
                }
            })?
        } else {
            v32
        }
    }
    .truthy()?
    {
        e.set("_rust_part", rt.import_module("_rust_part")?)?;
        {
            let _site = rt.source_at(
                "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                line!(),
            );
            {
                let fun37 = e.get("_rust_part")?.attr("start")?;
                let mut args35 = Vec::new();
                let mut kw36 = Vec::new();
                fun37.call(args35, kw36)?
            }
        };
    }
    e.set("cq", rt.import_module("cadquery")?)?;
    let mod38 = rt.import_module("_cadq_export")?;
    e.set(
        "export_assembly",
        rt.member("_cadq_export", "export_assembly")?,
    )?;
    let mod39 = rt.import_module("_materials")?;
    e.set("M_PETGF_BLACK", rt.member("_materials", "M_PETGF_BLACK")?)?;
    e.set("linear", rt.member("_materials", "linear")?)?;
    e.set("one_body", rt.member("_materials", "one_body")?)?;
    e.set("dims", rt.import_module("_enclosure_interface")?)?;
    e.set("wings", rt.import_module("_display_wing_interface")?)?;
    e.set("retention", rt.import_module("_display_retention")?)?;
    let mod41 = rt.import_module("_swept_top")?;
    e.set("rounded_prism", rt.member("_swept_top", "rounded_prism")?)?;
    let assigned42 = {
        let mut s = Vec::new();
        s.push(e.get("wings")?.attr("COVER_X")?);
        s.push(e.get("wings")?.attr("COVER_Y")?);
        s.push(e.get("wings")?.attr("CORNER_R")?);
        Val::tuple(s)
    };
    let unpack43 = unpack(assigned42.clone(), 3)?;
    e.set("cover_x", unpack43[0].clone())?;
    e.set("cover_slope", unpack43[1].clone())?;
    e.set("cover_corner_r", unpack43[2].clone())?;
    let assigned44 = e.get("wings")?.attr("BODY_X_AIR")?;
    e.set("cover_slip", assigned44.clone())?;
    let assigned45 = {
        let mut s = Vec::new();
        s.push(e.get("wings")?.attr("WINDOW_X")?);
        s.push(e.get("wings")?.attr("WINDOW_Y")?);
        s.push(e.get("wings")?.attr("WINDOW_R")?);
        Val::tuple(s)
    };
    let unpack46 = unpack(assigned45.clone(), 3)?;
    e.set("window_x", unpack46[0].clone())?;
    e.set("window_slope", unpack46[1].clone())?;
    e.set("window_corner_r", unpack46[2].clone())?;
    // build_display_cover
    e.set("build_display_cover", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                    line!(),
                );
                {
                    let fun49 = e.get("cq")?.attr("Workplane")?;
                    let mut args47 = Vec::new();
                    let mut kw48 = Vec::new();
                    kw48.push(("obj".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun52 = e.get("wings")?.attr("cover")?;
                            let mut args50 = Vec::new();
                            let mut kw51 = Vec::new();
                            fun52.call(args50, kw51)?
                        }
                    }));
                    fun49.call(args47, kw48)?
                }
            });
            Ok(Val::None)
        })
    })?;
    // selftest
    e.set("selftest", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned53 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                    line!(),
                );
                {
                    let fun56 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun59 = e.get("build_display_cover")?;
                            let mut args57 = Vec::new();
                            let mut kw58 = Vec::new();
                            fun59.call(args57, kw58)?
                        }
                    }
                    .attr("val")?;
                    let mut args54 = Vec::new();
                    let mut kw55 = Vec::new();
                    fun56.call(args54, kw55)?
                }
            };
            e.set("body", assigned53.clone())?;
            if !{
                let v68 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                        line!(),
                    );
                    {
                        let fun71 = e.get("body")?.attr("isValid")?;
                        let mut args69 = Vec::new();
                        let mut kw70 = Vec::new();
                        fun71.call(args69, kw70)?
                    }
                };
                if v68.truthy()? {
                    {
                        let v66 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                                line!(),
                            );
                            {
                                let fun62 = e.get("len")?;
                                let mut args60 = Vec::new();
                                let mut kw61 = Vec::new();
                                args60.push({
                                    let _site = rt.source_at(
                                        "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                                        line!(),
                                    );
                                    {
                                        let fun65 = e.get("body")?.attr("Solids")?;
                                        let mut args63 = Vec::new();
                                        let mut kw64 = Vec::new();
                                        fun65.call(args63, kw64)?
                                    }
                                });
                                fun62.call(args60, kw61)?
                            }
                        };
                        let v67 = Val::Int(1i64);
                        Val::Bool(compare("eq", v66.clone(), v67.clone())?.truthy()?)
                    }
                } else {
                    v68
                }
            }
            .truthy()?
            {
                anyhow::bail!("{}", val_string(Val::Str("assertion failed".into()))?);
            }
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                    line!(),
                );
                {
                    let fun74 = e.get("print")?;
                    let mut args72 = Vec::new();
                    let mut kw73 = Vec::new();
                    args72.push(Val::Str("Display cover: one valid solid.".into()));
                    fun74.call(args72, kw73)?
                }
            };
            return Ok(Val::Int(0i64));
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
            let mod75 = rt.import_module("_enclosure_data")?;
            e.set("dimensions", rt.member("_enclosure_data", "dimensions")?)?;
            e.set("read", rt.member("_enclosure_data", "read")?)?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                    line!(),
                );
                {
                    let fun78 = e.get("read")?;
                    let mut args76 = Vec::new();
                    let mut kw77 = Vec::new();
                    args76.push(Val::Str("cover-recipe".into()));
                    kw77.push((
                        "display".into(),
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                                line!(),
                            );
                            {
                                let fun81 = e.get("dimensions")?;
                                let mut args79 = Vec::new();
                                let mut kw80 = Vec::new();
                                fun81.call(args79, kw80)?
                            }
                        }
                        .get(Val::Str("display".into()))?,
                    ));
                    kw77.push(("color".into(), {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun84 = e.get("linear")?;
                            let mut args82 = Vec::new();
                            let mut kw83 = Vec::new();
                            args82.push(e.get("M_PETGF_BLACK")?);
                            fun84.call(args82, kw83)?
                        }
                    }));
                    fun78.call(args76, kw77)?
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
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                    line!(),
                );
                {
                    let fun87 = e.get("_rust_part")?.attr("cut")?;
                    let mut args85 = Vec::new();
                    let mut kw86 = Vec::new();
                    args85.push(Val::Str("enclosure-components".into()));
                    args85.push(Val::Str("display-cover".into()));
                    args85.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun90 = e.get("numbers")?;
                            let mut args88 = Vec::new();
                            let mut kw89 = Vec::new();
                            fun90.call(args88, kw89)?
                        }
                    });
                    args85.push(e.get("_here")?.attr("parent")?);
                    fun87.call(args85, kw86)?
                }
            };
            let mod91 = rt.import_module("_enclosure_data")?;
            e.set("dimensions", rt.member("_enclosure_data", "dimensions")?)?;
            e.set("read", rt.member("_enclosure_data", "read")?)?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                    line!(),
                );
                {
                    let fun103 = e.get("print")?;
                    let mut args101 = Vec::new();
                    let mut kw102 = Vec::new();
                    args101.push(Val::Str(
                        "-> display-cover.step, display-cover.stl, README.md".into(),
                    ));
                    fun103.call(args101, kw102)?
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
            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
            line!(),
        );
        {
            let fun106 = e.get("sys")?.attr("exit")?;
            let mut args104 = Vec::new();
            let mut kw105 = Vec::new();
            args104.push(
                if {
                    let v109 = {
                        let v113 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                                line!(),
                            );
                            {
                                let fun112 = e.get("len")?;
                                let mut args110 = Vec::new();
                                let mut kw111 = Vec::new();
                                args110.push(e.get("sys")?.attr("argv")?);
                                fun112.call(args110, kw111)?
                            }
                        };
                        let v114 = Val::Int(1i64);
                        Val::Bool(compare("gt", v113.clone(), v114.clone())?.truthy()?)
                    };
                    if v109.truthy()? {
                        {
                            let v107 = e.get("sys")?.attr("argv")?.get(Val::Int(1i64))?;
                            let v108 = Val::Str("selftest".into());
                            Val::Bool(compare("eq", v107.clone(), v108.clone())?.truthy()?)
                        }
                    } else {
                        v109
                    }
                }
                .truthy()?
                {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun117 = e.get("selftest")?;
                            let mut args115 = Vec::new();
                            let mut kw116 = Vec::new();
                            fun117.call(args115, kw116)?
                        }
                    }
                } else {
                    {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/display_cover.rs",
                            line!(),
                        );
                        {
                            let fun120 = e.get("main")?;
                            let mut args118 = Vec::new();
                            let mut kw119 = Vec::new();
                            fun120.call(args118, kw119)?
                        }
                    }
                },
            );
            fun106.call(args104, kw105)?
        }
    };
    Ok(Val::None)
}
