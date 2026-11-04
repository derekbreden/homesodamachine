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
    let assigned9 = {
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
            Val::Str("cold-core-layout".into()),
        )?);
        Val::tuple(s)
    }
    .iter()?
    {
        e.set("_p", item17)?;
        if {
            let v21 = {
                let fun20 = e.get("str")?;
                let mut args18 = Vec::new();
                let mut kw19 = Vec::new();
                args18.push(e.get("_p")?);
                fun20.call(args18, kw19)?
            };
            let v22 = e.get("sys")?.attr("path")?;
            Val::Bool(compare("not_in", v21.clone(), v22.clone())?.truthy()?)
        }
        .truthy()?
        {
            {
                let fun25 = e.get("sys")?.attr("path")?.attr("insert")?;
                let mut args23 = Vec::new();
                let mut kw24 = Vec::new();
                args23.push(Val::Int(0i64));
                args23.push({
                    let fun28 = e.get("str")?;
                    let mut args26 = Vec::new();
                    let mut kw27 = Vec::new();
                    args26.push(e.get("_p")?);
                    fun28.call(args26, kw27)?
                });
                fun25.call(args23, kw24)?
            };
        }
    }
    e.set("_carb", rt.import_module("_carbonator_stock")?)?;
    let assigned29 = e.get("_carb")?.attr("TUBE_OD")?;
    e.set("tube_od", assigned29.clone())?;
    let assigned30 = e.get("_carb")?.attr("TUBE_ID")?;
    e.set("tube_id", assigned30.clone())?;
    let assigned31 = e.get("_carb")?.attr("TUBE_WALL")?;
    e.set("tube_wall", assigned31.clone())?;
    let assigned32 = e.get("_carb")?.attr("carbonator_height")?;
    e.set("tube_length", assigned32.clone())?;
    let assigned33 = e.get("_here")?.attr("parent")?;
    e.set("out_dir", assigned33.clone())?;
    let assigned34 = Val::Str("carbonator-tube".into());
    e.set("out_name", assigned34.clone())?;
    // build_tube
    e.set("build_tube", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            e.set("cq", rt.import_module("cadquery")?)?;
            let assigned35 = {
                let fun38 = {
                    let fun41 = {
                        let fun44 = e.get("cq")?.attr("Workplane")?;
                        let mut args42 = Vec::new();
                        let mut kw43 = Vec::new();
                        args42.push(Val::Str("XY".into()));
                        fun44.call(args42, kw43)?
                    }
                    .attr("circle")?;
                    let mut args39 = Vec::new();
                    let mut kw40 = Vec::new();
                    args39.push(binary("truediv", e.get("tube_od")?, Val::Float(2.0f64))?);
                    fun41.call(args39, kw40)?
                }
                .attr("extrude")?;
                let mut args36 = Vec::new();
                let mut kw37 = Vec::new();
                args36.push(e.get("tube_length")?);
                fun38.call(args36, kw37)?
            };
            e.set("outer", assigned35.clone())?;
            let assigned45 = {
                let fun48 = {
                    let fun51 = {
                        let fun54 = {
                            let fun57 = e.get("cq")?.attr("Workplane")?;
                            let mut args55 = Vec::new();
                            let mut kw56 = Vec::new();
                            args55.push(Val::Str("XY".into()));
                            fun57.call(args55, kw56)?
                        }
                        .attr("workplane")?;
                        let mut args52 = Vec::new();
                        let mut kw53 = Vec::new();
                        kw53.push(("offset".into(), unary("neg", Val::Float(0.5f64))?));
                        fun54.call(args52, kw53)?
                    }
                    .attr("circle")?;
                    let mut args49 = Vec::new();
                    let mut kw50 = Vec::new();
                    args49.push(binary("truediv", e.get("tube_id")?, Val::Float(2.0f64))?);
                    fun51.call(args49, kw50)?
                }
                .attr("extrude")?;
                let mut args46 = Vec::new();
                let mut kw47 = Vec::new();
                args46.push(binary("add", e.get("tube_length")?, Val::Float(1.0f64))?);
                fun48.call(args46, kw47)?
            };
            e.set("bore", assigned45.clone())?;
            return Ok({
                let fun60 = e.get("outer")?.attr("cut")?;
                let mut args58 = Vec::new();
                let mut kw59 = Vec::new();
                args58.push(e.get("bore")?);
                fun60.call(args58, kw59)?
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
            let mod61 = rt.import_module("_material_base")?;
            e.set("M_STAINLESS", rt.member("_material_base", "M_STAINLESS")?)?;
            let mod62 = rt.import_module("_materials")?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(Val::Str("name".into()), e.get("out_name")?)?;
                d.set(
                    Val::Str("radius".into()),
                    binary("truediv", e.get("tube_od")?, Val::Float(2.0f64))?,
                )?;
                d.set(Val::Str("height".into()), e.get("tube_length")?)?;
                d.set(Val::Str("bores".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let d = Val::dict(vec![]);
                        d.set(Val::Str("center".into()), {
                            let mut s = Vec::new();
                            s.push(Val::Float(0.0f64));
                            s.push(Val::Float(0.0f64));
                            Val::list(s)
                        })?;
                        d.set(
                            Val::Str("radius".into()),
                            binary("truediv", e.get("tube_id")?, Val::Float(2.0f64))?,
                        )?;
                        d.set(Val::Str("floor".into()), Val::Float(0.0f64))?;
                        d
                    });
                    Val::list(s)
                })?;
                d.set(Val::Str("color".into()), {
                    let fun65 = e.get("list")?;
                    let mut args63 = Vec::new();
                    let mut kw64 = Vec::new();
                    args63.push({
                        let fun68 = e.get("linear")?;
                        let mut args66 = Vec::new();
                        let mut kw67 = Vec::new();
                        args66.push(e.get("M_STAINLESS")?);
                        fun68.call(args66, kw67)?
                    });
                    fun65.call(args63, kw64)?
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
                let fun71 = e.get("_rust_part")?.attr("cut")?;
                let mut args69 = Vec::new();
                let mut kw70 = Vec::new();
                args69.push(Val::Str("cold-core".into()));
                args69.push(Val::Str("carbonator-tube".into()));
                args69.push({
                    let fun74 = e.get("numbers")?;
                    let mut args72 = Vec::new();
                    let mut kw73 = Vec::new();
                    fun74.call(args72, kw73)?
                });
                args69.push(e.get("out_dir")?);
                fun71.call(args69, kw70)?
            };
            let assigned75 = binary("truediv", e.get("out_dir")?, {
                let mut str76 = String::new();
                str76.push_str(&format(&e.get("out_name")?, &String::new())?);
                str76.push_str(".step");
                Val::Str(str76)
            })?;
            e.set("path", assigned75.clone())?;
            {
                let fun79 = e.get("print")?;
                let mut args77 = Vec::new();
                let mut kw78 = Vec::new();
                args77.push({
                    let mut str80 = String::new();
                    str80.push_str("Exported: ");
                    str80.push_str(&format(&e.get("path")?, &String::new())?);
                    Val::Str(str80)
                });
                fun79.call(args77, kw78)?
            };
            {
                let fun83 = e.get("print")?;
                let mut args81 = Vec::new();
                let mut kw82 = Vec::new();
                args81.push({
                    let mut str84 = String::new();
                    str84.push_str("  Tube:   Ø");
                    str84.push_str(&format(
                        &e.get("tube_od")?,
                        &val_string({
                            let mut str85 = String::new();
                            str85.push_str(".3f");
                            Val::Str(str85)
                        })?,
                    )?);
                    str84.push_str(" OD × ");
                    str84.push_str(&format(
                        &e.get("tube_wall")?,
                        &val_string({
                            let mut str86 = String::new();
                            str86.push_str(".3f");
                            Val::Str(str86)
                        })?,
                    )?);
                    str84.push_str(" wall × ");
                    str84.push_str(&format(
                        &e.get("tube_length")?,
                        &val_string({
                            let mut str87 = String::new();
                            str87.push_str(".1f");
                            Val::Str(str87)
                        })?,
                    )?);
                    str84.push_str(" long, 316 SS");
                    Val::Str(str84)
                });
                fun83.call(args81, kw82)?
            };
            {
                let fun90 = e.get("print")?;
                let mut args88 = Vec::new();
                let mut kw89 = Vec::new();
                args88.push({
                    let mut str91 = String::new();
                    str91.push_str("  Bore:   Ø");
                    str91.push_str(&format(
                        &e.get("tube_id")?,
                        &val_string({
                            let mut str92 = String::new();
                            str92.push_str(".3f");
                            Val::Str(str92)
                        })?,
                    )?);
                    Val::Str(str91)
                });
                fun90.call(args88, kw89)?
            };
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun95 = e.get("_rust_part")?.attr("start")?;
        let mut args93 = Vec::new();
        let mut kw94 = Vec::new();
        fun95.call(args93, kw94)?
    };
    {
        let fun98 = e.get("main")?;
        let mut args96 = Vec::new();
        let mut kw97 = Vec::new();
        fun98.call(args96, kw97)?
    };
    Ok(Val::None)
}
