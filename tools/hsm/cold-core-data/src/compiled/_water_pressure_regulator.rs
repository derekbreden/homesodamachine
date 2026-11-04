#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    let mod1 = rt.import_module("functools")?;
    e.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    let mod2 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("cq", rt.import_module("cadquery")?)?;
    let assigned3 = {
        let fun6 = e.get("next")?;
        let mut args4 = Vec::new();
        let mut kw5 = Vec::new();
        args4.push({
            let e = e.child();
            let out7 = Val::list(vec![]);
            for item8 in {
                let fun11 = {
                    let fun14 = e.get("Path")?;
                    let mut args12 = Vec::new();
                    let mut kw13 = Vec::new();
                    args12.push(e.get("__file__")?);
                    fun14.call(args12, kw13)?
                }
                .attr("resolve")?;
                let mut args9 = Vec::new();
                let mut kw10 = Vec::new();
                fun11.call(args9, kw10)?
            }
            .attr("parents")?
            .iter()?
            {
                e.set("p", item8)?;
                if {
                    let v15 = e.get("p")?.attr("name")?;
                    let v16 = Val::Str("hardware".into());
                    Val::Bool(compare("eq", v15.clone(), v16.clone())?.truthy()?)
                }
                .truthy()?
                {
                    out7.attr("append")?.call(vec![e.get("p")?], vec![])?;
                }
            }
            out7
        });
        fun6.call(args4, kw5)?
    };
    e.set("HW", assigned3.clone())?;
    {
        let fun19 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args17 = Vec::new();
        let mut kw18 = Vec::new();
        args17.push(Val::Int(0i64));
        args17.push({
            let fun22 = e.get("str")?;
            let mut args20 = Vec::new();
            let mut kw21 = Vec::new();
            args20.push(binary(
                "truediv",
                e.get("HW")?,
                Val::Str("reference/shok-blok-regulator".into()),
            )?);
            fun22.call(args20, kw21)?
        });
        fun19.call(args17, kw18)?
    };
    e.set("regulator", rt.import_module("shok_blok_regulator")?)?;
    let assigned23 = {
        let mut s = Vec::new();
        s.push(unary("neg", Val::Float(5.2f64))?);
        s.push(unary("neg", Val::Float(49.3f64))?);
        Val::tuple(s)
    };
    e.set("INLET_XY", assigned23.clone())?;
    let assigned24 = Val::Float(48.6f64);
    e.set("INLET_OVER_FACE", assigned24.clone())?;
    let assigned25 = {
        let fun28 = {
            let fun31 = {
                let fun34 = e.get("cq")?.attr("Vector")?;
                let mut args32 = Vec::new();
                let mut kw33 = Vec::new();
                args32.push(unary("neg", Val::Float(0.985f64))?);
                args32.push(unary("neg", Val::Float(0.08f64))?);
                args32.push(unary("neg", Val::Float(0.152f64))?);
                fun34.call(args32, kw33)?
            }
            .attr("normalized")?;
            let mut args29 = Vec::new();
            let mut kw30 = Vec::new();
            fun31.call(args29, kw30)?
        }
        .attr("toTuple")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        fun28.call(args26, kw27)?
    };
    e.set("AXIS", assigned25.clone())?;
    let assigned35 = Val::Float(96.0f64);
    e.set("BEARING_S", assigned35.clone())?;
    let assigned36 = Val::Float(9.45f64);
    e.set("SEAT_R", assigned36.clone())?;
    let assigned37 = binary("add", e.get("SEAT_R")?, Val::Float(3.25f64))?;
    e.set("HALF_WIDTH", assigned37.clone())?;
    let assigned38 = Val::Float(8.8f64);
    e.set("LENGTH", assigned38.clone())?;
    let assigned39 = Val::Float(2.8f64);
    e.set("TIE_WIDTH", assigned39.clone())?;
    let assigned40 = Val::Float(3.25f64);
    e.set("TIE_HEIGHT", assigned40.clone())?;
    let assigned41 = Val::Float(4.5f64);
    e.set("UNDER_BORE", assigned41.clone())?;
    // inlet
    e.set("inlet", {
        let params = vec![("face_z".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun44 = e.get("cq")?.attr("Vector")?;
                let mut args42 = Vec::new();
                let mut kw43 = Vec::new();
                args42.extend(e.get("INLET_XY")?.iter()?);
                args42.push(binary("add", e.get("face_z")?, e.get("INLET_OVER_FACE")?)?);
                fun44.call(args42, kw43)?
            });
            Ok(Val::None)
        })
    })?;
    // bearing
    e.set("bearing", {
        let params = vec![("face_z".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "add",
                {
                    let fun47 = e.get("inlet")?;
                    let mut args45 = Vec::new();
                    let mut kw46 = Vec::new();
                    args45.push(e.get("face_z")?);
                    fun47.call(args45, kw46)?
                },
                binary(
                    "mul",
                    {
                        let fun50 = e.get("cq")?.attr("Vector")?;
                        let mut args48 = Vec::new();
                        let mut kw49 = Vec::new();
                        args48.extend(e.get("AXIS")?.iter()?);
                        fun50.call(args48, kw49)?
                    },
                    e.get("BEARING_S")?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    // cradle
    e.set("cradle", {
        let params = vec![("face_z".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned51 = {
                let fun54 = e.get("bearing")?;
                let mut args52 = Vec::new();
                let mut kw53 = Vec::new();
                args52.push(e.get("face_z")?);
                fun54.call(args52, kw53)?
            };
            e.set("mid", assigned51.clone())?;
            let assigned55 = {
                let fun58 = e.get("cq")?.attr("Vector")?;
                let mut args56 = Vec::new();
                let mut kw57 = Vec::new();
                args56.extend(e.get("AXIS")?.iter()?);
                fun58.call(args56, kw57)?
            };
            e.set("along", assigned55.clone())?;
            let assigned59 = binary(
                "truediv",
                e.get("along")?.attr("z")?,
                e.get("along")?.attr("x")?,
            )?;
            e.set("slope", assigned59.clone())?;
            let assigned60 = {
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    e.get("mid")?.attr("x")?,
                    binary("truediv", e.get("LENGTH")?, Val::Int(2i64))?,
                )?);
                s.push(binary(
                    "add",
                    e.get("mid")?.attr("x")?,
                    binary("truediv", e.get("LENGTH")?, Val::Int(2i64))?,
                )?);
                Val::tuple(s)
            };
            let unpack61 = unpack(assigned60.clone(), 2)?;
            e.set("x0", unpack61[0].clone())?;
            e.set("x1", unpack61[1].clone())?;
            let assigned62 = binary("sub", e.get("mid")?.attr("y")?, e.get("HALF_WIDTH")?)?;
            e.set("y0", assigned62.clone())?;
            let assigned63 = {
                let fun66 = e.get("cq")?.attr("Wire")?.attr("makePolygon")?;
                let mut args64 = Vec::new();
                let mut kw65 = Vec::new();
                args64.push({
                    let mut s = Vec::new();
                    s.push({
                        let fun69 = e.get("cq")?.attr("Vector")?;
                        let mut args67 = Vec::new();
                        let mut kw68 = Vec::new();
                        args67.push(e.get("x0")?);
                        args67.push(e.get("y0")?);
                        args67.push(e.get("face_z")?);
                        fun69.call(args67, kw68)?
                    });
                    s.push({
                        let fun72 = e.get("cq")?.attr("Vector")?;
                        let mut args70 = Vec::new();
                        let mut kw71 = Vec::new();
                        args70.push(e.get("x1")?);
                        args70.push(e.get("y0")?);
                        args70.push(e.get("face_z")?);
                        fun72.call(args70, kw71)?
                    });
                    s.push({
                        let fun75 = e.get("cq")?.attr("Vector")?;
                        let mut args73 = Vec::new();
                        let mut kw74 = Vec::new();
                        args73.push(e.get("x1")?);
                        args73.push(e.get("y0")?);
                        args73.push(binary(
                            "add",
                            e.get("mid")?.attr("z")?,
                            binary(
                                "mul",
                                e.get("slope")?,
                                binary("sub", e.get("x1")?, e.get("mid")?.attr("x")?)?,
                            )?,
                        )?);
                        fun75.call(args73, kw74)?
                    });
                    s.push({
                        let fun78 = e.get("cq")?.attr("Vector")?;
                        let mut args76 = Vec::new();
                        let mut kw77 = Vec::new();
                        args76.push(e.get("x0")?);
                        args76.push(e.get("y0")?);
                        args76.push(binary(
                            "add",
                            e.get("mid")?.attr("z")?,
                            binary(
                                "mul",
                                e.get("slope")?,
                                binary("sub", e.get("x0")?, e.get("mid")?.attr("x")?)?,
                            )?,
                        )?);
                        fun78.call(args76, kw77)?
                    });
                    s.push({
                        let fun81 = e.get("cq")?.attr("Vector")?;
                        let mut args79 = Vec::new();
                        let mut kw80 = Vec::new();
                        args79.push(e.get("x0")?);
                        args79.push(e.get("y0")?);
                        args79.push(e.get("face_z")?);
                        fun81.call(args79, kw80)?
                    });
                    Val::list(s)
                });
                fun66.call(args64, kw65)?
            };
            e.set("wire", assigned63.clone())?;
            let assigned82 = {
                let fun85 = e.get("cq")?.attr("Solid")?.attr("extrudeLinear")?;
                let mut args83 = Vec::new();
                let mut kw84 = Vec::new();
                args83.push(e.get("wire")?);
                args83.push({
                    let mut s = Vec::new();
                    Val::list(s)
                });
                args83.push({
                    let fun88 = e.get("cq")?.attr("Vector")?;
                    let mut args86 = Vec::new();
                    let mut kw87 = Vec::new();
                    args86.push(Val::Int(0i64));
                    args86.push(binary("mul", Val::Int(2i64), e.get("HALF_WIDTH")?)?);
                    args86.push(Val::Int(0i64));
                    fun88.call(args86, kw87)?
                });
                fun85.call(args83, kw84)?
            };
            e.set("post", assigned82.clone())?;
            let assigned89 = {
                let fun92 = e.get("cq")?.attr("Solid")?.attr("makeCylinder")?;
                let mut args90 = Vec::new();
                let mut kw91 = Vec::new();
                args90.push(e.get("SEAT_R")?);
                args90.push(Val::Int(30i64));
                args90.push(binary(
                    "sub",
                    e.get("mid")?,
                    binary("mul", e.get("along")?, Val::Int(15i64))?,
                )?);
                args90.push(e.get("along")?);
                fun92.call(args90, kw91)?
            };
            e.set("bore", assigned89.clone())?;
            let assigned93 = binary(
                "sub",
                binary("sub", e.get("mid")?.attr("z")?, e.get("SEAT_R")?)?,
                e.get("UNDER_BORE")?,
            )?;
            e.set("roof", assigned93.clone())?;
            let assigned94 = {
                let fun97 = e.get("cq")?.attr("Solid")?.attr("makeBox")?;
                let mut args95 = Vec::new();
                let mut kw96 = Vec::new();
                args95.push(e.get("TIE_WIDTH")?);
                args95.push(binary(
                    "add",
                    binary("mul", Val::Int(2i64), e.get("HALF_WIDTH")?)?,
                    Val::Int(2i64),
                )?);
                args95.push(e.get("TIE_HEIGHT")?);
                args95.push({
                    let fun100 = e.get("cq")?.attr("Vector")?;
                    let mut args98 = Vec::new();
                    let mut kw99 = Vec::new();
                    args98.push(binary(
                        "sub",
                        e.get("mid")?.attr("x")?,
                        binary("truediv", e.get("TIE_WIDTH")?, Val::Int(2i64))?,
                    )?);
                    args98.push(binary("sub", e.get("y0")?, Val::Int(1i64))?);
                    args98.push(binary("sub", e.get("roof")?, e.get("TIE_HEIGHT")?)?);
                    fun100.call(args98, kw99)?
                });
                fun97.call(args95, kw96)?
            };
            e.set("passage", assigned94.clone())?;
            return Ok({
                let fun103 = {
                    let fun106 = {
                        let fun109 = e.get("post")?.attr("cut")?;
                        let mut args107 = Vec::new();
                        let mut kw108 = Vec::new();
                        args107.push(e.get("bore")?);
                        fun109.call(args107, kw108)?
                    }
                    .attr("cut")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push(e.get("passage")?);
                    fun106.call(args104, kw105)?
                }
                .attr("clean")?;
                let mut args101 = Vec::new();
                let mut kw102 = Vec::new();
                fun103.call(args101, kw102)?
            });
            Ok(Val::None)
        })
    })?;
    // proud
    e.set("proud", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun112 = {
                    let fun115 = e.get("cradle")?;
                    let mut args113 = Vec::new();
                    let mut kw114 = Vec::new();
                    args113.push(Val::Float(0.0f64));
                    fun115.call(args113, kw114)?
                }
                .attr("BoundingBox")?;
                let mut args110 = Vec::new();
                let mut kw111 = Vec::new();
                fun112.call(args110, kw111)?
            }
            .attr("zmax")?);
            Ok(Val::None)
        })
    })?;
    // tie_loop
    e.set("tie_loop", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned116 = {
                let fun119 = e.get("cq")?.attr("Vector")?;
                let mut args117 = Vec::new();
                let mut kw118 = Vec::new();
                args117.extend(e.get("AXIS")?.iter()?);
                fun119.call(args117, kw118)?
            };
            e.set("axis", assigned116.clone())?;
            let assigned120 = binary(
                "truediv",
                {
                    let fun123 = e.get("abs")?;
                    let mut args121 = Vec::new();
                    let mut kw122 = Vec::new();
                    args121.push(e.get("axis")?.attr("x")?);
                    fun123.call(args121, kw122)?
                },
                {
                    let fun126 = e.get("math")?.attr("hypot")?;
                    let mut args124 = Vec::new();
                    let mut kw125 = Vec::new();
                    args124.push(e.get("axis")?.attr("x")?);
                    args124.push(e.get("axis")?.attr("y")?);
                    fun126.call(args124, kw125)?
                },
            )?;
            e.set("horizontal", assigned120.clone())?;
            let assigned127 = binary("truediv", e.get("HALF_WIDTH")?, e.get("horizontal")?)?;
            e.set("w", assigned127.clone())?;
            let assigned128 = binary(
                "truediv",
                binary("add", e.get("SEAT_R")?, e.get("UNDER_BORE")?)?,
                {
                    let fun131 = e.get("math")?.attr("sqrt")?;
                    let mut args129 = Vec::new();
                    let mut kw130 = Vec::new();
                    args129.push(binary(
                        "sub",
                        Val::Int(1i64),
                        binary("pow", e.get("axis")?.attr("z")?, Val::Int(2i64))?,
                    )?);
                    fun131.call(args129, kw130)?
                },
            )?;
            e.set("h", assigned128.clone())?;
            let assigned132 = e.get("SEAT_R")?;
            e.set("r", assigned132.clone())?;
            return Ok(binary(
                "add",
                binary(
                    "add",
                    binary(
                        "add",
                        binary("mul", Val::Int(2i64), e.get("w")?)?,
                        binary("mul", Val::Int(2i64), e.get("h")?)?,
                    )?,
                    binary("mul", Val::Int(2i64), {
                        let fun135 = e.get("math")?.attr("sqrt")?;
                        let mut args133 = Vec::new();
                        let mut kw134 = Vec::new();
                        args133.push(binary(
                            "sub",
                            binary("mul", e.get("w")?, e.get("w")?)?,
                            binary("mul", e.get("r")?, e.get("r")?)?,
                        )?);
                        fun135.call(args133, kw134)?
                    })?,
                )?,
                binary(
                    "mul",
                    e.get("r")?,
                    binary(
                        "sub",
                        e.get("math")?.attr("pi")?,
                        binary("mul", Val::Int(2i64), {
                            let fun138 = e.get("math")?.attr("acos")?;
                            let mut args136 = Vec::new();
                            let mut kw137 = Vec::new();
                            args136.push(binary("truediv", e.get("r")?, e.get("w")?)?);
                            fun138.call(args136, kw137)?
                        })?,
                    )?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
