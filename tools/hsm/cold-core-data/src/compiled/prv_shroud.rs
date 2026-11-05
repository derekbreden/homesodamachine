#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("argparse", rt.import_module("argparse")?)?;
    e.set("math", rt.import_module("math")?)?;
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
            args39.push(e.get("_here")?.attr("parents")?.get(Val::Int(1i64))?);
            fun41.call(args39, kw40)?
        });
        fun38.call(args36, kw37)?
    };
    {
        let fun44 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args42 = Vec::new();
        let mut kw43 = Vec::new();
        args42.push(Val::Int(0i64));
        args42.push({
            let fun47 = e.get("str")?;
            let mut args45 = Vec::new();
            let mut kw46 = Vec::new();
            args45.push(binary(
                "truediv",
                {
                    let fun50 = e.get("next")?;
                    let mut args48 = Vec::new();
                    let mut kw49 = Vec::new();
                    args48.push({
                        let e = e.child();
                        let out51 = Val::list(vec![]);
                        for item52 in e.get("_here")?.attr("parents")?.iter()? {
                            e.set("p", item52)?;
                            if {
                                let v53 = e.get("p")?.attr("name")?;
                                let v54 = Val::Str("printed-parts".into());
                                Val::Bool(compare("eq", v53.clone(), v54.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                out51.attr("append")?.call(vec![e.get("p")?], vec![])?;
                            }
                        }
                        out51
                    });
                    fun50.call(args48, kw49)?
                },
                Val::Str("cadlib".into()),
            )?);
            fun47.call(args45, kw46)?
        });
        fun44.call(args42, kw43)?
    };
    e.set("fits", rt.import_module("fits")?)?;
    let assigned56 = binary(
        "add",
        Val::Float(18.8f64),
        binary("mul", Val::Float(2.0f64), e.get("fits")?.attr("slip")?)?,
    )?;
    e.set("inner_diameter", assigned56.clone())?;
    let assigned57 = Val::Float(2.0f64);
    e.set("wall_thickness", assigned57.clone())?;
    let assigned58 = Val::Float(2.0f64);
    e.set("cap_thickness", assigned58.clone())?;
    let assigned59 = Val::Float(44.0f64);
    e.set("cavity_length", assigned59.clone())?;
    let assigned60 = binary(
        "add",
        Val::Float(6.5f64),
        binary("mul", Val::Float(2.0f64), e.get("fits")?.attr("slip")?)?,
    )?;
    e.set("vent_hole_diameter", assigned60.clone())?;
    let assigned61 = Val::Float(37.88f64);
    e.set("vent_station_z", assigned61.clone())?;
    let assigned62 = binary(
        "add",
        e.get("inner_diameter")?,
        binary("mul", Val::Int(2i64), e.get("wall_thickness")?)?,
    )?;
    e.set("outer_diameter", assigned62.clone())?;
    let assigned63 = binary("add", e.get("cavity_length")?, e.get("cap_thickness")?)?;
    e.set("total_length", assigned63.clone())?;
    let assigned64 = Val::Float(0.1f64);
    e.set("overcut", assigned64.clone())?;
    // numbers
    e.set("numbers", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let mod65 = rt.import_module("_materials")?;
            e.set("C_SHROUD", rt.member("_materials", "C_SHROUD")?)?;
            e.set("linear", rt.member("_materials", "linear")?)?;
            return Ok({
                let d = Val::dict(vec![]);
                d.set(
                    Val::Str("inner_radius".into()),
                    binary("truediv", e.get("inner_diameter")?, Val::Float(2.0f64))?,
                )?;
                d.set(
                    Val::Str("outer_radius".into()),
                    binary("truediv", e.get("outer_diameter")?, Val::Float(2.0f64))?,
                )?;
                d.set(Val::Str("cavity_length".into()), e.get("cavity_length")?)?;
                d.set(Val::Str("total_length".into()), e.get("total_length")?)?;
                d.set(
                    Val::Str("vent_radius".into()),
                    binary("truediv", e.get("vent_hole_diameter")?, Val::Float(2.0f64))?,
                )?;
                d.set(Val::Str("vent_station_z".into()), e.get("vent_station_z")?)?;
                d.set(Val::Str("overcut".into()), e.get("overcut")?)?;
                d.set(
                    Val::Str("supported_surface".into()),
                    e.get("fits")?.attr("supported_surface")?,
                )?;
                d.set(Val::Str("color".into()), {
                    let fun68 = e.get("list")?;
                    let mut args66 = Vec::new();
                    let mut kw67 = Vec::new();
                    args66.push({
                        let fun71 = e.get("linear")?;
                        let mut args69 = Vec::new();
                        let mut kw70 = Vec::new();
                        args69.push(e.get("C_SHROUD")?);
                        fun71.call(args69, kw70)?
                    });
                    fun68.call(args66, kw67)?
                })?;
                d
            });
            Ok(Val::None)
        })
    })?;
    // volume
    e.set("volume", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned72 = {
                let mut s = Vec::new();
                s.push(binary(
                    "truediv",
                    e.get("outer_diameter")?,
                    Val::Float(2.0f64),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("inner_diameter")?,
                    Val::Float(2.0f64),
                )?);
                s.push(binary(
                    "truediv",
                    e.get("vent_hole_diameter")?,
                    Val::Float(2.0f64),
                )?);
                Val::tuple(s)
            };
            let unpack73 = unpack(assigned72.clone(), 3)?;
            e.set("outer", unpack73[0].clone())?;
            e.set("inner", unpack73[1].clone())?;
            e.set("radius", unpack73[2].clone())?;
            let assigned74 = e.get("fits")?.attr("supported_surface")?;
            e.set("allowance", assigned74.clone())?;
            let assigned75 = {
                let fun78 = e.get("math")?.attr("acos")?;
                let mut args76 = Vec::new();
                let mut kw77 = Vec::new();
                args76.push(binary(
                    "truediv",
                    e.get("allowance")?,
                    binary("mul", Val::Float(2.0f64), e.get("radius")?)?,
                )?);
                fun78.call(args76, kw77)?
            };
            e.set("split", assigned75.clone())?;
            // strip
            e.set("strip", {
                let params = vec![
                    ("theta".into(), None, false),
                    ("overlapping".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned79 = binary("mul", e.get("radius")?, {
                        let fun82 = e.get("math")?.attr("sin")?;
                        let mut args80 = Vec::new();
                        let mut kw81 = Vec::new();
                        args80.push(e.get("theta")?);
                        fun82.call(args80, kw81)?
                    })?;
                    e.set("x", assigned79.clone())?;
                    let assigned83 = binary("mul", e.get("radius")?, {
                        let fun86 = e.get("math")?.attr("cos")?;
                        let mut args84 = Vec::new();
                        let mut kw85 = Vec::new();
                        args84.push(e.get("theta")?);
                        fun86.call(args84, kw85)?
                    })?;
                    e.set("half", assigned83.clone())?;
                    let assigned87 = binary(
                        "sub",
                        {
                            let fun90 = e.get("math")?.attr("sqrt")?;
                            let mut args88 = Vec::new();
                            let mut kw89 = Vec::new();
                            args88.push(binary(
                                "sub",
                                binary("mul", e.get("outer")?, e.get("outer")?)?,
                                binary("mul", e.get("x")?, e.get("x")?)?,
                            )?);
                            fun90.call(args88, kw89)?
                        },
                        {
                            let fun93 = e.get("math")?.attr("sqrt")?;
                            let mut args91 = Vec::new();
                            let mut kw92 = Vec::new();
                            args91.push(binary(
                                "sub",
                                binary("mul", e.get("inner")?, e.get("inner")?)?,
                                binary("mul", e.get("x")?, e.get("x")?)?,
                            )?);
                            fun93.call(args91, kw92)?
                        },
                    )?;
                    e.set("depth", assigned87.clone())?;
                    let assigned94 = if e.get("overlapping")?.truthy()? {
                        binary(
                            "add",
                            binary("mul", Val::Float(2.0f64), e.get("half")?)?,
                            e.get("allowance")?,
                        )?
                    } else {
                        binary("mul", Val::Float(4.0f64), e.get("half")?)?
                    };
                    e.set("height", assigned94.clone())?;
                    return Ok(binary(
                        "mul",
                        binary("mul", e.get("depth")?, e.get("height")?)?,
                        e.get("half")?,
                    )?);
                    Ok(Val::None)
                })
            })?;
            // integral
            e.set("integral", {
                let params = vec![
                    ("start".into(), None, false),
                    ("stop".into(), None, false),
                    ("overlapping".into(), None, false),
                ];
                let outer = e.clone();
                let runtime = rt.clone();
                Val::function(move |args, kwargs| {
                    let rt = runtime.clone();
                    let e = bind(&outer, &params, args, kwargs, None, None)?;
                    let _frame = rt.frame(&outer);
                    let assigned95 = Val::Int(128i64);
                    e.set("count", assigned95.clone())?;
                    let assigned96 = binary(
                        "truediv",
                        binary("sub", e.get("stop")?, e.get("start")?)?,
                        e.get("count")?,
                    )?;
                    e.set("step", assigned96.clone())?;
                    let assigned97 = binary(
                        "add",
                        {
                            let fun100 = e.get("strip")?;
                            let mut args98 = Vec::new();
                            let mut kw99 = Vec::new();
                            args98.push(e.get("start")?);
                            args98.push(e.get("overlapping")?);
                            fun100.call(args98, kw99)?
                        },
                        {
                            let fun103 = e.get("strip")?;
                            let mut args101 = Vec::new();
                            let mut kw102 = Vec::new();
                            args101.push(e.get("stop")?);
                            args101.push(e.get("overlapping")?);
                            fun103.call(args101, kw102)?
                        },
                    )?;
                    e.set("total", assigned97.clone())?;
                    e.set(
                        "total",
                        binary("add", e.get("total")?, {
                            let fun106 = e.get("sum")?;
                            let mut args104 = Vec::new();
                            let mut kw105 = Vec::new();
                            args104.push({
                                let e = e.child();
                                let out107 = Val::list(vec![]);
                                for item108 in {
                                    let fun111 = e.get("range")?;
                                    let mut args109 = Vec::new();
                                    let mut kw110 = Vec::new();
                                    args109.push(Val::Int(1i64));
                                    args109.push(e.get("count")?);
                                    fun111.call(args109, kw110)?
                                }
                                .iter()?
                                {
                                    e.set("i", item108)?;
                                    out107.attr("append")?.call(
                                        vec![binary(
                                            "mul",
                                            if binary("mod", e.get("i")?, Val::Int(2i64))?
                                                .truthy()?
                                            {
                                                Val::Int(4i64)
                                            } else {
                                                Val::Int(2i64)
                                            },
                                            {
                                                let fun114 = e.get("strip")?;
                                                let mut args112 = Vec::new();
                                                let mut kw113 = Vec::new();
                                                args112.push(binary(
                                                    "add",
                                                    e.get("start")?,
                                                    binary("mul", e.get("i")?, e.get("step")?)?,
                                                )?);
                                                args112.push(e.get("overlapping")?);
                                                fun114.call(args112, kw113)?
                                            },
                                        )?],
                                        vec![],
                                    )?;
                                }
                                out107
                            });
                            fun106.call(args104, kw105)?
                        })?,
                    )?;
                    return Ok(binary(
                        "truediv",
                        binary("mul", e.get("total")?, e.get("step")?)?,
                        Val::Float(3.0f64),
                    )?);
                    Ok(Val::None)
                })
            })?;
            let assigned115 = binary(
                "mul",
                Val::Float(2.0f64),
                binary(
                    "add",
                    {
                        let fun118 = e.get("integral")?;
                        let mut args116 = Vec::new();
                        let mut kw117 = Vec::new();
                        args116.push(Val::Float(0.0f64));
                        args116.push(e.get("split")?);
                        args116.push(Val::Bool(true));
                        fun118.call(args116, kw117)?
                    },
                    {
                        let fun121 = e.get("integral")?;
                        let mut args119 = Vec::new();
                        let mut kw120 = Vec::new();
                        args119.push(e.get("split")?);
                        args119.push(binary(
                            "truediv",
                            e.get("math")?.attr("pi")?,
                            Val::Float(2.0f64),
                        )?);
                        args119.push(Val::Bool(false));
                        fun121.call(args119, kw120)?
                    },
                )?,
            )?;
            e.set("removed", assigned115.clone())?;
            return Ok(binary(
                "sub",
                binary(
                    "mul",
                    e.get("math")?.attr("pi")?,
                    binary(
                        "sub",
                        binary(
                            "mul",
                            binary("mul", e.get("outer")?, e.get("outer")?)?,
                            e.get("total_length")?,
                        )?,
                        binary(
                            "mul",
                            binary("mul", e.get("inner")?, e.get("inner")?)?,
                            e.get("cavity_length")?,
                        )?,
                    )?,
                )?,
                e.get("removed")?,
            )?);
            Ok(Val::None)
        })
    })?;
    // main
    e.set("main", {
        let params = vec![("output".into(), Some(Val::None), false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned122 = if {
                let v123 = e.get("output")?;
                let v124 = Val::None;
                Val::Bool(compare("is_not", v123.clone(), v124.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let fun127 = e.get("Path")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    args125.push(e.get("output")?);
                    fun127.call(args125, kw126)?
                }
            } else {
                e.get("_here")?.attr("parent")?
            };
            e.set("out_dir", assigned122.clone())?;
            {
                let fun130 = e.get("out_dir")?.attr("mkdir")?;
                let mut args128 = Vec::new();
                let mut kw129 = Vec::new();
                kw129.push(("parents".into(), Val::Bool(true)));
                kw129.push(("exist_ok".into(), Val::Bool(true)));
                fun130.call(args128, kw129)?
            };
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            {
                let fun133 = e.get("_rust_part")?.attr("cut")?;
                let mut args131 = Vec::new();
                let mut kw132 = Vec::new();
                args131.push(Val::Str("cold-core".into()));
                args131.push(Val::Str("prv-shroud".into()));
                args131.push({
                    let fun136 = e.get("numbers")?;
                    let mut args134 = Vec::new();
                    let mut kw135 = Vec::new();
                    fun136.call(args134, kw135)?
                });
                args131.push(e.get("out_dir")?);
                fun133.call(args131, kw132)?
            };
            let assigned137 = {
                let fun140 = e.get("volume")?;
                let mut args138 = Vec::new();
                let mut kw139 = Vec::new();
                fun140.call(args138, kw139)?
            };
            e.set("vol", assigned137.clone())?;
            let assigned141 = binary("truediv", e.get("outer_diameter")?, Val::Float(2.0f64))?;
            e.set("radius", assigned141.clone())?;
            {
                let fun144 = e.get("print")?;
                let mut args142 = Vec::new();
                let mut kw143 = Vec::new();
                args142.push({
                    let mut str145 = String::new();
                    str145.push_str("-> prv-shroud.step  bbox X[");
                    str145.push_str(&format(
                        &unary("neg", e.get("radius")?)?,
                        &val_string({
                            let mut str146 = String::new();
                            str146.push_str("6.2f");
                            Val::Str(str146)
                        })?,
                    )?);
                    str145.push_str("..");
                    str145.push_str(&format(
                        &e.get("radius")?,
                        &val_string({
                            let mut str147 = String::new();
                            str147.push_str("6.2f");
                            Val::Str(str147)
                        })?,
                    )?);
                    str145.push_str("] Y[");
                    str145.push_str(&format(
                        &unary("neg", e.get("radius")?)?,
                        &val_string({
                            let mut str148 = String::new();
                            str148.push_str("6.2f");
                            Val::Str(str148)
                        })?,
                    )?);
                    str145.push_str("..");
                    str145.push_str(&format(
                        &e.get("radius")?,
                        &val_string({
                            let mut str149 = String::new();
                            str149.push_str("6.2f");
                            Val::Str(str149)
                        })?,
                    )?);
                    str145.push_str("] Z[");
                    str145.push_str(&format(
                        &Val::Float(0.0f64),
                        &val_string({
                            let mut str150 = String::new();
                            str150.push_str("6.2f");
                            Val::Str(str150)
                        })?,
                    )?);
                    str145.push_str("..");
                    str145.push_str(&format(
                        &e.get("total_length")?,
                        &val_string({
                            let mut str151 = String::new();
                            str151.push_str("6.2f");
                            Val::Str(str151)
                        })?,
                    )?);
                    str145.push_str("]  vol ");
                    str145.push_str(&format(
                        &e.get("vol")?,
                        &val_string({
                            let mut str152 = String::new();
                            str152.push_str(".3f");
                            Val::Str(str152)
                        })?,
                    )?);
                    str145.push_str(" mm^3");
                    Val::Str(str145)
                });
                fun144.call(args142, kw143)?
            };
            {
                let fun155 = e.get("document")?;
                let mut args153 = Vec::new();
                let mut kw154 = Vec::new();
                args153.push(e.get("vol")?);
                fun155.call(args153, kw154)?
            };
            Ok(Val::None)
        })
    })?;
    // document
    e.set("document", {
        let params = vec![("vol".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned156 = e.get("_here")?.attr("parent")?;
            e.set("out_dir", assigned156.clone())?;
            let assigned157 = binary("truediv", e.get("outer_diameter")?, Val::Float(2.0f64))?;
            e.set("radius", assigned157.clone())?;
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun209 = e.get("_rust_part")?.attr("start")?;
        let mut args207 = Vec::new();
        let mut kw208 = Vec::new();
        fun209.call(args207, kw208)?
    };
    let assigned210 = {
        let fun213 = e.get("argparse")?.attr("ArgumentParser")?;
        let mut args211 = Vec::new();
        let mut kw212 = Vec::new();
        kw212.push(("description".into(), e.get("__doc__")?));
        fun213.call(args211, kw212)?
    };
    e.set("parser", assigned210.clone())?;
    {
        let fun216 = e.get("parser")?.attr("add_argument")?;
        let mut args214 = Vec::new();
        let mut kw215 = Vec::new();
        args214.push(Val::Str("--output".into()));
        kw215.push(("type".into(), e.get("Path")?));
        kw215.push(("default".into(), e.get("_here")?.attr("parent")?));
        fun216.call(args214, kw215)?
    };
    let assigned217 = {
        let fun220 = e.get("parser")?.attr("parse_args")?;
        let mut args218 = Vec::new();
        let mut kw219 = Vec::new();
        fun220.call(args218, kw219)?
    };
    e.set("args", assigned217.clone())?;
    {
        let fun223 = e.get("main")?;
        let mut args221 = Vec::new();
        let mut kw222 = Vec::new();
        args221.push(e.get("args")?.attr("output")?);
        fun223.call(args221, kw222)?
    };
    Ok(Val::None)
}
