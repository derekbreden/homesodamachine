#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    let mod1 = rt.import_module("collections")?;
    e.set("namedtuple", rt.member("collections", "namedtuple")?)?;
    let mod2 = rt.import_module("functools")?;
    e.set("lru_cache", rt.member("functools", "lru_cache")?)?;
    let mod3 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    let mod4 = rt.import_module("types")?;
    e.set("SimpleNamespace", rt.member("types", "SimpleNamespace")?)?;
    let mod5 = rt.import_module("reportlab.pdfgen")?;
    e.set("canvas", rt.member("reportlab.pdfgen", "canvas")?)?;
    let assigned6 = {
        let fun9 = {
            let fun12 = e.get("Path")?;
            let mut args10 = Vec::new();
            let mut kw11 = Vec::new();
            args10.push(e.get("__file__")?);
            fun12.call(args10, kw11)?
        }
        .attr("resolve")?;
        let mut args7 = Vec::new();
        let mut kw8 = Vec::new();
        fun9.call(args7, kw8)?
    }
    .attr("parent")?;
    e.set("HERE", assigned6.clone())?;
    let assigned13 = e.get("HERE")?.attr("parent")?;
    e.set("HW", assigned13.clone())?;
    {
        let fun16 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args14 = Vec::new();
        let mut kw15 = Vec::new();
        args14.push(Val::Int(0i64));
        args14.push({
            let fun19 = e.get("str")?;
            let mut args17 = Vec::new();
            let mut kw18 = Vec::new();
            args17.push(binary("truediv", e.get("HW")?, Val::Str("scripts".into()))?);
            fun19.call(args17, kw18)?
        });
        fun16.call(args14, kw15)?
    };
    {
        let fun22 = e.get("sys")?.attr("path")?.attr("insert")?;
        let mut args20 = Vec::new();
        let mut kw21 = Vec::new();
        args20.push(Val::Int(0i64));
        args20.push({
            let fun25 = e.get("str")?;
            let mut args23 = Vec::new();
            let mut kw24 = Vec::new();
            args23.push(e.get("HERE")?);
            fun25.call(args23, kw24)?
        });
        fun22.call(args20, kw21)?
    };
    e.set("_rust_part", rt.import_module("_rust_part")?)?;
    {
        let fun28 = e.get("_rust_part")?.attr("start")?;
        let mut args26 = Vec::new();
        let mut kw27 = Vec::new();
        fun28.call(args26, kw27)?
    };
    let mod29 = rt.import_module("_mesh_projection")?;
    e.set(
        "model_outlines",
        rt.member("_mesh_projection", "model_outlines")?,
    )?;
    e.set("source", rt.import_module("_coil")?)?;
    e.set("mandrel", rt.import_module("coil_mandrel")?)?;
    let mod30 = rt.import_module("_fabrication_drawing")?;
    import_star(&e, mod30.clone())?;
    let assigned31 = binary(
        "truediv",
        e.get("HERE")?,
        Val::Str("evaporator-coil-drawing.pdf".into()),
    )?;
    e.set("PDF_PATH", assigned31.clone())?;
    let assigned32 = {
        let mut s = Vec::new();
        s.push(Val::Int(1224i64));
        s.push(Val::Int(792i64));
        Val::tuple(s)
    };
    e.set("SHEET", assigned32.clone())?;
    let assigned33 = binary("truediv", e.get("MM")?, Val::Int(2i64))?;
    e.set("SCALE", assigned33.clone())?;
    let assigned34 = binary("mul", Val::Float(0.031f64), Val::Float(25.4f64))?;
    e.set("WALL", assigned34.clone())?;
    let assigned35 = {
        let fun38 = e.get("source")?.attr("wrap_points_xyz")?;
        let mut args36 = Vec::new();
        let mut kw37 = Vec::new();
        fun38.call(args36, kw37)?
    };
    e.set("_laid_points", assigned35.clone())?;
    let assigned39 = {
        let fun42 = e.get("math")?.attr("ceil")?;
        let mut args40 = Vec::new();
        let mut kw41 = Vec::new();
        args40.push(binary(
            "add",
            {
                let fun45 = e.get("sum")?;
                let mut args43 = Vec::new();
                let mut kw44 = Vec::new();
                args43.push({
                    let e = e.child();
                    let out46 = Val::list(vec![]);
                    for item47 in {
                        let fun50 = e.get("zip")?;
                        let mut args48 = Vec::new();
                        let mut kw49 = Vec::new();
                        args48.push(e.get("_laid_points")?);
                        args48.push(e.get("_laid_points")?.get(Val::Slice {
                            start: Some(Val::Int(1i64).integer()?),
                            stop: None,
                            step: 1,
                        })?);
                        fun50.call(args48, kw49)?
                    }
                    .iter()?
                    {
                        let unpack51 = unpack(item47, 2)?;
                        e.set("a", unpack51[0].clone())?;
                        e.set("b", unpack51[1].clone())?;
                        out46.attr("append")?.call(
                            vec![{
                                let fun54 = e.get("math")?.attr("dist")?;
                                let mut args52 = Vec::new();
                                let mut kw53 = Vec::new();
                                args52.push(e.get("a")?);
                                args52.push(e.get("b")?);
                                fun54.call(args52, kw53)?
                            }],
                            vec![],
                        )?;
                    }
                    out46
                });
                fun45.call(args43, kw44)?
            },
            e.get("mandrel")?.attr("stub_total")?,
        )?);
        fun42.call(args40, kw41)?
    };
    e.set("CUT_LENGTH", assigned39.clone())?;
    let assigned55 = Val::Int(10i64);
    e.set("CUT_PLUS", assigned55.clone())?;
    let assigned56 = Val::Str("HSM-0015".into());
    e.set("MATERIAL_ID", assigned56.clone())?;
    let assigned57 = Val::Str("C".into());
    e.set("REVISION", assigned57.clone())?;
    let assigned58 = {
        let mut s = Vec::new();
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("elevation".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(442i64));
            s.push(Val::Int(687i64));
            s.push(Val::Int(756i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("plan-upper".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(265i64));
            s.push(Val::Int(687i64));
            s.push(Val::Int(439i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("plan-lower".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(120i64));
            s.push(Val::Int(687i64));
            s.push(Val::Int(280i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("dimensions".into()));
            s.push(Val::Int(700i64));
            s.push(Val::Int(476i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(756i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("requirements".into()));
            s.push(Val::Int(700i64));
            s.push(Val::Int(154i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(479i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(1i64));
            s.push(Val::Str("title-footer".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(1197i64));
            s.push(Val::Int(147i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("inlet-form-table".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(459i64));
            s.push(Val::Int(613i64));
            s.push(Val::Int(756i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("outlet-form-table".into()));
            s.push(Val::Int(622i64));
            s.push(Val::Int(451i64));
            s.push(Val::Int(1202i64));
            s.push(Val::Int(756i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("side-view".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(147i64));
            s.push(Val::Int(687i64));
            s.push(Val::Int(454i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("form-instructions".into()));
            s.push(Val::Int(700i64));
            s.push(Val::Int(252i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(449i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("tube-section".into()));
            s.push(Val::Int(700i64));
            s.push(Val::Int(149i64));
            s.push(Val::Int(1190i64));
            s.push(Val::Int(275i64));
            Val::tuple(s)
        });
        s.push({
            let mut s = Vec::new();
            s.push(Val::Int(2i64));
            s.push(Val::Str("title-footer".into()));
            s.push(Val::Int(35i64));
            s.push(Val::Int(27i64));
            s.push(Val::Int(1197i64));
            s.push(Val::Int(147i64));
            Val::tuple(s)
        });
        Val::list(s)
    };
    e.set("REVIEW_REGIONS", assigned58.clone())?;
    let assigned59 = {
        let fun62 = e.get("namedtuple")?;
        let mut args60 = Vec::new();
        let mut kw61 = Vec::new();
        args60.push(Val::Str("_Point".into()));
        args60.push(Val::Str("x y z".into()));
        fun62.call(args60, kw61)?
    };
    e.set("_Point", assigned59.clone())?;
    // tail_form
    e.set("tail_form", {
        let params = vec![
            ("end".into(), None, false),
            ("working_tail".into(), Some(Val::Bool(false)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned63 = {
                let fun66 = e.get("source")?.attr("tail_layout")?;
                let mut args64 = Vec::new();
                let mut kw65 = Vec::new();
                args64.push(e.get("end")?);
                kw65.push(("working_tail".into(), e.get("working_tail")?));
                fun66.call(args64, kw65)?
            };
            e.set("segments", assigned63.clone())?;
            return Ok({
                let fun69 = e.get("SimpleNamespace")?;
                let mut args67 = Vec::new();
                let mut kw68 = Vec::new();
                kw68.push(("segments".into(), e.get("segments")?));
                kw68.push(("point".into(), {
                    let fun72 = e.get("_Point")?;
                    let mut args70 = Vec::new();
                    let mut kw71 = Vec::new();
                    args70.extend(
                        e.get("segments")?
                            .get(unary("neg", Val::Int(1i64))?)?
                            .get(Val::Str("end".into()))?
                            .iter()?,
                    );
                    fun72.call(args70, kw71)?
                }));
                fun69.call(args67, kw68)?
            });
            Ok(Val::None)
        })
    })?;
    // drawing_model
    e.set("drawing_model", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned94 = binary(
                "truediv",
                binary(
                    "truediv",
                    binary(
                        "truediv",
                        e.get("HW")?.attr("parent")?,
                        Val::Str(".cache".into()),
                    )?,
                    Val::Str("drawings".into()),
                )?,
                Val::Str("evaporator-coil".into()),
            )?;
            e.set("directory", assigned94.clone())?;
            {
                let fun97 = e.get("directory")?.attr("mkdir")?;
                let mut args95 = Vec::new();
                let mut kw96 = Vec::new();
                kw96.push(("parents".into(), Val::Bool(true)));
                kw96.push(("exist_ok".into(), Val::Bool(true)));
                fun97.call(args95, kw96)?
            };
            {
                let fun100 = e.get("_rust_part")?.attr("run")?;
                let mut args98 = Vec::new();
                let mut kw99 = Vec::new();
                args98.push(Val::Str("cold-core-assembly".into()));
                args98.push(Val::Str("evaporator-coil-model".into()));
                args98.push(e.get("directory")?);
                fun100.call(args98, kw99)?
            };
            return Ok(binary(
                "truediv",
                e.get("directory")?,
                Val::Str("evaporator-coil.step.npz".into()),
            )?);
            Ok(Val::None)
        })
    })?;
    // outline
    e.set("outline", {
        let params = vec![("view".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned101 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("front".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("plan".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("side".into()), {
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d
            }
            .get(e.get("view")?)?;
            let unpack102 = unpack(assigned101.clone(), 2)?;
            e.set("normal", unpack102[0].clone())?;
            e.set("right", unpack102[1].clone())?;
            let assigned103 = {
                let e = e.child();
                let out104 = Val::list(vec![]);
                for item105 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("inlet".into()));
                    s.push(Val::Str("outlet".into()));
                    Val::list(s)
                }
                .iter()?
                {
                    e.set("end", item105)?;
                    out104.attr("append")?.call(
                        vec![{
                            let mut s = Vec::new();
                            s.push(
                                {
                                    let fun108 = e.get("tail_form")?;
                                    let mut args106 = Vec::new();
                                    let mut kw107 = Vec::new();
                                    args106.push(e.get("end")?);
                                    fun108.call(args106, kw107)?
                                }
                                .attr("segments")?
                                .get(Val::Int(0i64))?
                                .get(Val::Str("start".into()))?,
                            );
                            s.push(
                                {
                                    let fun111 = e.get("tail_form")?;
                                    let mut args109 = Vec::new();
                                    let mut kw110 = Vec::new();
                                    args109.push(e.get("end")?);
                                    fun111.call(args109, kw110)?
                                }
                                .attr("segments")?
                                .get(Val::Int(0i64))?
                                .get(Val::Str("tangent".into()))?,
                            );
                            Val::tuple(s)
                        }],
                        vec![],
                    )?;
                }
                out104
            };
            e.set("joins", assigned103.clone())?;
            return Ok({
                let fun114 = e.get("model_outlines")?;
                let mut args112 = Vec::new();
                let mut kw113 = Vec::new();
                args112.push({
                    let fun117 = e.get("drawing_model")?;
                    let mut args115 = Vec::new();
                    let mut kw116 = Vec::new();
                    fun117.call(args115, kw116)?
                });
                args112.push(e.get("normal")?);
                args112.push(e.get("right")?);
                kw113.push(("join_planes".into(), e.get("joins")?));
                fun114.call(args112, kw113)?
            });
            Ok(Val::None)
        })
    })?;
    // render_view
    e.set("render_view", {
        let params = vec![
            ("c".into(), None, false),
            ("view".into(), None, false),
            ("origin".into(), None, false),
            ("scale".into(), Some(e.get("SCALE")?), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            for item118 in {
                let fun132 = e.get("outline")?;
                let mut args130 = Vec::new();
                let mut kw131 = Vec::new();
                args130.push(e.get("view")?);
                fun132.call(args130, kw131)?
            }
            .iter()?
            {
                e.set("points", item118)?;
                if {
                    let v122 = {
                        let fun121 = e.get("len")?;
                        let mut args119 = Vec::new();
                        let mut kw120 = Vec::new();
                        args119.push(e.get("points")?);
                        fun121.call(args119, kw120)?
                    };
                    let v123 = Val::Int(1i64);
                    Val::Bool(compare("gt", v122.clone(), v123.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun126 = e.get("polyline")?;
                        let mut args124 = Vec::new();
                        let mut kw125 = Vec::new();
                        args124.push(e.get("c")?);
                        args124.push({
                            let e = e.child();
                            let out127 = Val::list(vec![]);
                            for item128 in e.get("points")?.iter()? {
                                let unpack129 = unpack(item128, 2)?;
                                e.set("u", unpack129[0].clone())?;
                                e.set("v", unpack129[1].clone())?;
                                out127.attr("append")?.call(
                                    vec![{
                                        let mut s = Vec::new();
                                        s.push(binary(
                                            "add",
                                            e.get("origin")?.get(Val::Int(0i64))?,
                                            binary("mul", e.get("u")?, e.get("scale")?)?,
                                        )?);
                                        s.push(binary(
                                            "add",
                                            e.get("origin")?.get(Val::Int(1i64))?,
                                            binary("mul", e.get("v")?, e.get("scale")?)?,
                                        )?);
                                        Val::tuple(s)
                                    }],
                                    vec![],
                                )?;
                            }
                            out127
                        });
                        args124.push(Val::Float(0.7f64));
                        fun126.call(args124, kw125)?
                    };
                }
            }
            if {
                let v133 = e.get("view")?;
                let v134 = {
                    let mut s = Vec::new();
                    s.push(Val::Str("plan".into()));
                    s.push(Val::Str("side".into()));
                    Val::list(s)
                };
                Val::Bool(compare("in", v133.clone(), v134.clone())?.truthy()?)
            }
            .truthy()?
            {
                for item135 in {
                    let mut s = Vec::new();
                    s.push(Val::Str("inlet".into()));
                    s.push(Val::Str("outlet".into()));
                    Val::list(s)
                }
                .iter()?
                {
                    e.set("end", item135)?;
                    let assigned136 = {
                        let fun139 = e.get("tail_form")?;
                        let mut args137 = Vec::new();
                        let mut kw138 = Vec::new();
                        args137.push(e.get("end")?);
                        kw138.push(("working_tail".into(), Val::Bool(true)));
                        fun139.call(args137, kw138)?
                    }
                    .attr("point")?;
                    e.set("point", assigned136.clone())?;
                    let assigned140 = if {
                        let v141 = e.get("view")?;
                        let v142 = Val::Str("plan".into());
                        Val::Bool(compare("eq", v141.clone(), v142.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        {
                            let mut s = Vec::new();
                            s.push(e.get("point")?.attr("x")?);
                            s.push(e.get("point")?.attr("y")?);
                            Val::tuple(s)
                        }
                    } else {
                        {
                            let mut s = Vec::new();
                            s.push(unary("neg", e.get("point")?.attr("x")?)?);
                            s.push(e.get("point")?.attr("z")?);
                            Val::tuple(s)
                        }
                    };
                    let unpack143 = unpack(assigned140.clone(), 2)?;
                    e.set("u", unpack143[0].clone())?;
                    e.set("v", unpack143[1].clone())?;
                    {
                        let fun146 = e.get("line")?;
                        let mut args144 = Vec::new();
                        let mut kw145 = Vec::new();
                        args144.push(e.get("c")?);
                        args144.push(binary(
                            "add",
                            e.get("origin")?.get(Val::Int(0i64))?,
                            binary("mul", e.get("u")?, e.get("scale")?)?,
                        )?);
                        args144.push(binary(
                            "add",
                            e.get("origin")?.get(Val::Int(1i64))?,
                            binary(
                                "mul",
                                binary("sub", e.get("v")?, e.get("source")?.attr("TUBE_R")?)?,
                                e.get("scale")?,
                            )?,
                        )?);
                        args144.push(binary(
                            "add",
                            e.get("origin")?.get(Val::Int(0i64))?,
                            binary("mul", e.get("u")?, e.get("scale")?)?,
                        )?);
                        args144.push(binary(
                            "add",
                            e.get("origin")?.get(Val::Int(1i64))?,
                            binary(
                                "mul",
                                binary("add", e.get("v")?, e.get("source")?.attr("TUBE_R")?)?,
                                e.get("scale")?,
                            )?,
                        )?);
                        args144.push(e.get("VISIBLE")?);
                        fun146.call(args144, kw145)?
                    };
                }
            }
            Ok(Val::None)
        })
    })?;
    // endpoint
    e.set("endpoint", {
        let params = vec![("end".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun149 = e.get("tuple")?;
                let mut args147 = Vec::new();
                let mut kw148 = Vec::new();
                args147.push(
                    {
                        let fun152 = e.get("tail_form")?;
                        let mut args150 = Vec::new();
                        let mut kw151 = Vec::new();
                        args150.push(e.get("end")?);
                        fun152.call(args150, kw151)?
                    }
                    .attr("point")?,
                );
                fun149.call(args147, kw148)?
            });
            Ok(Val::None)
        })
    })?;
    // station_mark
    e.set("station_mark", {
        let params = vec![
            ("c".into(), None, false),
            ("point".into(), None, false),
            ("label".into(), None, false),
            ("x".into(), None, false),
            ("y".into(), None, false),
            ("view".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned153 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("front".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("point")?.get(Val::Int(1i64))?);
                    s.push(e.get("point")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("plan".into()), {
                    let mut s = Vec::new();
                    s.push(e.get("point")?.get(Val::Int(0i64))?);
                    s.push(e.get("point")?.get(Val::Int(1i64))?);
                    Val::tuple(s)
                })?;
                d.set(Val::Str("side".into()), {
                    let mut s = Vec::new();
                    s.push(unary("neg", e.get("point")?.get(Val::Int(0i64))?)?);
                    s.push(e.get("point")?.get(Val::Int(2i64))?);
                    Val::tuple(s)
                })?;
                d
            }
            .get(e.get("view")?)?;
            let unpack154 = unpack(assigned153.clone(), 2)?;
            e.set("u", unpack154[0].clone())?;
            e.set("v", unpack154[1].clone())?;
            let assigned155 = {
                let mut s = Vec::new();
                s.push(binary(
                    "add",
                    e.get("x")?,
                    binary("mul", e.get("u")?, e.get("SCALE")?)?,
                )?);
                s.push(binary(
                    "add",
                    e.get("y")?,
                    binary("mul", e.get("v")?, e.get("SCALE")?)?,
                )?);
                Val::tuple(s)
            };
            let unpack156 = unpack(assigned155.clone(), 2)?;
            e.set("px", unpack156[0].clone())?;
            e.set("py", unpack156[1].clone())?;
            {
                let fun159 = e.get("center")?;
                let mut args157 = Vec::new();
                let mut kw158 = Vec::new();
                args157.push(e.get("c")?);
                args157.push(e.get("px")?);
                args157.push(e.get("py")?);
                args157.push(Val::Int(5i64));
                fun159.call(args157, kw158)?
            };
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("px")?);
                s.push(e.get("py")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // elevation
    e.set("elevation", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned160 = {
                let mut s = Vec::new();
                s.push(Val::Int(300i64));
                s.push(Val::Int(450i64));
                Val::tuple(s)
            };
            let unpack161 = unpack(assigned160.clone(), 2)?;
            e.set("x", unpack161[0].clone())?;
            e.set("z0", unpack161[1].clone())?;
            {
                let fun164 = e.get("text")?;
                let mut args162 = Vec::new();
                let mut kw163 = Vec::new();
                args162.push(e.get("c")?);
                args162.push(e.get("x")?);
                args162.push(Val::Int(741i64));
                args162.push(Val::Str("INSTALLED ELEVATION - LOOKING ALONG -X".into()));
                args162.push(Val::Int(11i64));
                kw163.push(("bold".into(), Val::Bool(true)));
                kw163.push(("align".into(), Val::Str("center".into())));
                fun164.call(args162, kw163)?
            };
            {
                let fun167 = e.get("text")?;
                let mut args165 = Vec::new();
                let mut kw166 = Vec::new();
                args165.push(e.get("c")?);
                args165.push(e.get("x")?);
                args165.push(Val::Int(724i64));
                args165.push(Val::Str(
                    "TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2".into(),
                ));
                args165.push(Val::Int(9i64));
                kw166.push(("align".into(), Val::Str("center".into())));
                fun167.call(args165, kw166)?
            };
            {
                let fun170 = e.get("render_view")?;
                let mut args168 = Vec::new();
                let mut kw169 = Vec::new();
                args168.push(e.get("c")?);
                args168.push(Val::Str("front".into()));
                args168.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("z0")?);
                    Val::tuple(s)
                });
                fun170.call(args168, kw169)?
            };
            let assigned171 = {
                let mut s = Vec::new();
                s.push(e.get("source")?.attr("evap_tail_low_z")?);
                s.push(e.get("source")?.attr("evap_tail_high_z")?);
                Val::tuple(s)
            };
            let unpack172 = unpack(assigned171.clone(), 2)?;
            e.set("lo", unpack172[0].clone())?;
            e.set("hi", unpack172[1].clone())?;
            let assigned173 = {
                let fun176 = e.get("tail_form")?;
                let mut args174 = Vec::new();
                let mut kw175 = Vec::new();
                args174.push(Val::Str("inlet".into()));
                fun176.call(args174, kw175)?
            }
            .attr("segments")?
            .get(Val::Int(0i64))?
            .get(Val::Str("start".into()))?;
            e.set("h1", assigned173.clone())?;
            let assigned177 = {
                let fun180 = e.get("tail_form")?;
                let mut args178 = Vec::new();
                let mut kw179 = Vec::new();
                args178.push(Val::Str("outlet".into()));
                fun180.call(args178, kw179)?
            }
            .attr("segments")?
            .get(Val::Int(0i64))?
            .get(Val::Str("start".into()))?;
            e.set("h2", assigned177.clone())?;
            for item181 in {
                let mut s = Vec::new();
                s.push(e.get("h1")?);
                s.push(e.get("h2")?);
                Val::list(s)
            }
            .iter()?
            {
                e.set("pt", item181)?;
                let assigned182 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("pt")?.get(Val::Int(1i64))?, e.get("SCALE")?)?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("z0")?,
                        binary("mul", e.get("pt")?.get(Val::Int(2i64))?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                };
                let unpack183 = unpack(assigned182.clone(), 2)?;
                e.set("px", unpack183[0].clone())?;
                e.set("py", unpack183[1].clone())?;
                {
                    let fun186 = e.get("line")?;
                    let mut args184 = Vec::new();
                    let mut kw185 = Vec::new();
                    args184.push(e.get("c")?);
                    args184.push(Val::Int(120i64));
                    args184.push(e.get("py")?);
                    args184.push(binary("sub", e.get("px")?, Val::Int(7i64))?);
                    args184.push(e.get("py")?);
                    fun186.call(args184, kw185)?
                };
            }
            {
                let fun189 = e.get("line")?;
                let mut args187 = Vec::new();
                let mut kw188 = Vec::new();
                args187.push(e.get("c")?);
                args187.push(Val::Int(125i64));
                args187.push(binary(
                    "add",
                    e.get("z0")?,
                    binary("mul", e.get("lo")?, e.get("SCALE")?)?,
                )?);
                args187.push(Val::Int(125i64));
                args187.push(binary(
                    "add",
                    e.get("z0")?,
                    binary("mul", e.get("hi")?, e.get("SCALE")?)?,
                )?);
                fun189.call(args187, kw188)?
            };
            {
                let fun192 = e.get("arrow")?;
                let mut args190 = Vec::new();
                let mut kw191 = Vec::new();
                args190.push(e.get("c")?);
                args190.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(125i64));
                    s.push(binary(
                        "add",
                        e.get("z0")?,
                        binary("mul", e.get("lo")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                args190.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(125i64));
                    s.push(binary(
                        "add",
                        e.get("z0")?,
                        binary("mul", e.get("hi")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                fun192.call(args190, kw191)?
            };
            {
                let fun195 = e.get("arrow")?;
                let mut args193 = Vec::new();
                let mut kw194 = Vec::new();
                args193.push(e.get("c")?);
                args193.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(125i64));
                    s.push(binary(
                        "add",
                        e.get("z0")?,
                        binary("mul", e.get("hi")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                args193.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(125i64));
                    s.push(binary(
                        "add",
                        e.get("z0")?,
                        binary("mul", e.get("lo")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                });
                fun195.call(args193, kw194)?
            };
            {
                let fun198 = e.get("c")?.attr("saveState")?;
                let mut args196 = Vec::new();
                let mut kw197 = Vec::new();
                fun198.call(args196, kw197)?
            };
            {
                let fun201 = e.get("c")?.attr("translate")?;
                let mut args199 = Vec::new();
                let mut kw200 = Vec::new();
                args199.push(Val::Int(115i64));
                args199.push(binary(
                    "add",
                    e.get("z0")?,
                    binary(
                        "truediv",
                        binary(
                            "mul",
                            binary("add", e.get("lo")?, e.get("hi")?)?,
                            e.get("SCALE")?,
                        )?,
                        Val::Int(2i64),
                    )?,
                )?);
                fun201.call(args199, kw200)?
            };
            {
                let fun204 = e.get("c")?.attr("rotate")?;
                let mut args202 = Vec::new();
                let mut kw203 = Vec::new();
                args202.push(Val::Int(90i64));
                fun204.call(args202, kw203)?
            };
            {
                let fun207 = e.get("text")?;
                let mut args205 = Vec::new();
                let mut kw206 = Vec::new();
                args205.push(e.get("c")?);
                args205.push(Val::Int(0i64));
                args205.push(Val::Int(0i64));
                args205.push({
                    let mut str208 = String::new();
                    str208.push_str(&format(
                        &e.get("source")?.attr("WIND_HEIGHT")?,
                        &val_string({
                            let mut str209 = String::new();
                            str209.push_str(".2f");
                            Val::Str(str209)
                        })?,
                    )?);
                    str208.push_str(" ±1.0 HELIX CL SPAN");
                    Val::Str(str208)
                });
                args205.push(Val::Float(9.5f64));
                kw206.push(("align".into(), Val::Str("center".into())));
                fun207.call(args205, kw206)?
            };
            {
                let fun212 = e.get("c")?.attr("restoreState")?;
                let mut args210 = Vec::new();
                let mut kw211 = Vec::new();
                fun212.call(args210, kw211)?
            };
            for item213 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("inlet".into()));
                    s.push(Val::Str("E1 / INLET".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("outlet".into()));
                    s.push(Val::Str("E2 / OUTLET".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack221 = unpack(item213, 2)?;
                e.set("end", unpack221[0].clone())?;
                e.set("label", unpack221[1].clone())?;
                let assigned214 = {
                    let fun217 = e.get("endpoint")?;
                    let mut args215 = Vec::new();
                    let mut kw216 = Vec::new();
                    args215.push(e.get("end")?);
                    fun217.call(args215, kw216)?
                };
                e.set("pt", assigned214.clone())?;
                {
                    let fun220 = e.get("text")?;
                    let mut args218 = Vec::new();
                    let mut kw219 = Vec::new();
                    args218.push(e.get("c")?);
                    args218.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("pt")?.get(Val::Int(1i64))?, e.get("SCALE")?)?,
                    )?);
                    args218.push(binary(
                        "sub",
                        binary(
                            "add",
                            e.get("z0")?,
                            binary("mul", e.get("pt")?.get(Val::Int(2i64))?, e.get("SCALE")?)?,
                        )?,
                        Val::Int(16i64),
                    )?);
                    args218.push(e.get("label")?);
                    args218.push(Val::Int(9i64));
                    kw219.push(("bold".into(), Val::Bool(true)));
                    kw219.push(("align".into(), Val::Str("center".into())));
                    fun220.call(args218, kw219)?
                };
            }
            let assigned222 = {
                let fun225 = e.get("station_mark")?;
                let mut args223 = Vec::new();
                let mut kw224 = Vec::new();
                args223.push(e.get("c")?);
                args223.push(e.get("h1")?);
                args223.push(Val::Str("H1".into()));
                args223.push(e.get("x")?);
                args223.push(e.get("z0")?);
                args223.push(Val::Str("front".into()));
                fun225.call(args223, kw224)?
            };
            e.set("p1", assigned222.clone())?;
            let assigned226 = {
                let fun229 = e.get("station_mark")?;
                let mut args227 = Vec::new();
                let mut kw228 = Vec::new();
                args227.push(e.get("c")?);
                args227.push(e.get("h2")?);
                args227.push(Val::Str("H2".into()));
                args227.push(e.get("x")?);
                args227.push(e.get("z0")?);
                args227.push(Val::Str("front".into()));
                fun229.call(args227, kw228)?
            };
            e.set("p2", assigned226.clone())?;
            {
                let fun232 = e.get("leader")?;
                let mut args230 = Vec::new();
                let mut kw231 = Vec::new();
                args230.push(e.get("c")?);
                args230.push(e.get("p2")?);
                args230.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(451i64));
                    s.push(Val::Int(704i64));
                    Val::tuple(s)
                });
                args230.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(476i64));
                    s.push(Val::Int(704i64));
                    Val::tuple(s)
                });
                args230.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("H2 / UPPER HELIX CL END".into()));
                    s.push({
                        let mut str233 = String::new();
                        str233.push_str("Z ");
                        str233.push_str(&format(
                            &e.get("hi")?,
                            &val_string({
                                let mut str234 = String::new();
                                str234.push_str(".2f");
                                Val::Str(str234)
                            })?,
                        )?);
                        str233.push_str(" REF");
                        Val::Str(str233)
                    });
                    Val::list(s)
                });
                args230.push(Val::Int(9i64));
                fun232.call(args230, kw231)?
            };
            {
                let fun237 = e.get("leader")?;
                let mut args235 = Vec::new();
                let mut kw236 = Vec::new();
                args235.push(e.get("c")?);
                args235.push(e.get("p1")?);
                args235.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(455i64));
                    s.push(Val::Int(450i64));
                    Val::tuple(s)
                });
                args235.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(479i64));
                    s.push(Val::Int(450i64));
                    Val::tuple(s)
                });
                args235.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("H1 / LOWER HELIX CL END".into()));
                    s.push({
                        let mut str238 = String::new();
                        str238.push_str("Z ");
                        str238.push_str(&format(
                            &e.get("lo")?,
                            &val_string({
                                let mut str239 = String::new();
                                str239.push_str(".2f");
                                Val::Str(str239)
                            })?,
                        )?);
                        str238.push_str(" ±0.5");
                        Val::Str(str238)
                    });
                    Val::list(s)
                });
                args235.push(Val::Int(9i64));
                fun237.call(args235, kw236)?
            };
            {
                let fun242 = e.get("text")?;
                let mut args240 = Vec::new();
                let mut kw241 = Vec::new();
                args240.push(e.get("c")?);
                args240.push(Val::Int(455i64));
                args240.push(Val::Int(625i64));
                args240.push(Val::Str("9.500 RIGHT-HAND TURNS".into()));
                args240.push(Val::Int(10i64));
                kw241.push(("bold".into(), Val::Bool(true)));
                fun242.call(args240, kw241)?
            };
            {
                let fun245 = e.get("text")?;
                let mut args243 = Vec::new();
                let mut kw244 = Vec::new();
                args243.push(e.get("c")?);
                args243.push(Val::Int(455i64));
                args243.push(Val::Int(608i64));
                args243.push({
                    let mut str246 = String::new();
                    str246.push_str(&format(
                        &e.get("source")?.attr("PITCH")?,
                        &val_string({
                            let mut str247 = String::new();
                            str247.push_str(".3f");
                            Val::Str(str247)
                        })?,
                    )?);
                    str246.push_str(" PITCH REF");
                    Val::Str(str246)
                });
                args243.push(Val::Int(9i64));
                fun245.call(args243, kw244)?
            };
            {
                let fun250 = e.get("text")?;
                let mut args248 = Vec::new();
                let mut kw249 = Vec::new();
                args248.push(e.get("c")?);
                args248.push(Val::Int(455i64));
                args248.push(Val::Int(573i64));
                args248.push(Val::Str("BOTH TAILS FULLY DEFINED".into()));
                args248.push(Val::Int(9i64));
                kw249.push(("bold".into(), Val::Bool(true)));
                fun250.call(args248, kw249)?
            };
            {
                let fun253 = e.get("text")?;
                let mut args251 = Vec::new();
                let mut kw252 = Vec::new();
                args251.push(e.get("c")?);
                args251.push(Val::Int(455i64));
                args251.push(Val::Int(557i64));
                args251.push(Val::Str("R15 FORMS / STATIONS ON SHEET 2".into()));
                args251.push(Val::Float(8.5f64));
                fun253.call(args251, kw252)?
            };
            {
                let fun256 = e.get("axes")?;
                let mut args254 = Vec::new();
                let mut kw255 = Vec::new();
                args254.push(e.get("c")?);
                args254.push(Val::Int(56i64));
                args254.push(Val::Int(456i64));
                args254.push(Val::Str("+Y".into()));
                args254.push(Val::Str("+Z".into()));
                fun256.call(args254, kw255)?
            };
            Ok(Val::None)
        })
    })?;
    // plan
    e.set("plan", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned257 = {
                let mut s = Vec::new();
                s.push(Val::Int(563i64));
                s.push(Val::Int(275i64));
                Val::tuple(s)
            };
            let unpack258 = unpack(assigned257.clone(), 2)?;
            e.set("x", unpack258[0].clone())?;
            e.set("y", unpack258[1].clone())?;
            {
                let fun261 = e.get("text")?;
                let mut args259 = Vec::new();
                let mut kw260 = Vec::new();
                args259.push(e.get("c")?);
                args259.push(Val::Int(325i64));
                args259.push(Val::Int(433i64));
                args259.push(Val::Str("PLAN - LOOKING ALONG -Z".into()));
                args259.push(Val::Int(11i64));
                kw260.push(("bold".into(), Val::Bool(true)));
                kw260.push(("align".into(), Val::Str("center".into())));
                fun261.call(args259, kw260)?
            };
            {
                let fun264 = e.get("text")?;
                let mut args262 = Vec::new();
                let mut kw263 = Vec::new();
                args262.push(e.get("c")?);
                args262.push(Val::Int(325i64));
                args262.push(Val::Int(417i64));
                args262.push(Val::Str(
                    "TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2".into(),
                ));
                args262.push(Val::Int(9i64));
                kw263.push(("align".into(), Val::Str("center".into())));
                fun264.call(args262, kw263)?
            };
            {
                let fun267 = e.get("render_view")?;
                let mut args265 = Vec::new();
                let mut kw266 = Vec::new();
                args265.push(e.get("c")?);
                args265.push(Val::Str("plan".into()));
                args265.push({
                    let mut s = Vec::new();
                    s.push(e.get("x")?);
                    s.push(e.get("y")?);
                    Val::tuple(s)
                });
                fun267.call(args265, kw266)?
            };
            {
                let fun270 = e.get("center")?;
                let mut args268 = Vec::new();
                let mut kw269 = Vec::new();
                args268.push(e.get("c")?);
                args268.push(e.get("x")?);
                args268.push(e.get("y")?);
                args268.push(Val::Int(13i64));
                fun270.call(args268, kw269)?
            };
            {
                let fun273 = e.get("text")?;
                let mut args271 = Vec::new();
                let mut kw272 = Vec::new();
                args271.push(e.get("c")?);
                args271.push(binary("add", e.get("x")?, Val::Int(12i64))?);
                args271.push(binary("sub", e.get("y")?, Val::Int(14i64))?);
                args271.push(Val::Str("O".into()));
                args271.push(Val::Int(9i64));
                fun273.call(args271, kw272)?
            };
            let assigned274 = {
                let fun277 = e.get("endpoint")?;
                let mut args275 = Vec::new();
                let mut kw276 = Vec::new();
                args275.push(Val::Str("inlet".into()));
                fun277.call(args275, kw276)?
            }
            .get(Val::Int(0i64))?;
            e.set("plane_x", assigned274.clone())?;
            let assigned278 = binary(
                "add",
                e.get("x")?,
                binary("mul", e.get("plane_x")?, e.get("SCALE")?)?,
            )?;
            e.set("px", assigned278.clone())?;
            {
                let fun281 = e.get("line")?;
                let mut args279 = Vec::new();
                let mut kw280 = Vec::new();
                args279.push(e.get("c")?);
                args279.push(e.get("px")?);
                args279.push(Val::Int(142i64));
                args279.push(e.get("px")?);
                args279.push(Val::Int(401i64));
                kw280.push(("dash".into(), e.get("CENTER_DASH")?));
                fun281.call(args279, kw280)?
            };
            {
                let fun284 = e.get("text")?;
                let mut args282 = Vec::new();
                let mut kw283 = Vec::new();
                args282.push(e.get("c")?);
                args282.push(e.get("px")?);
                args282.push(Val::Int(132i64));
                args282.push({
                    let mut str285 = String::new();
                    str285.push_str("E PLANE: X ");
                    str285.push_str(&format(
                        &e.get("plane_x")?,
                        &val_string({
                            let mut str286 = String::new();
                            str286.push_str(".2f");
                            Val::Str(str286)
                        })?,
                    )?);
                    Val::Str(str285)
                });
                args282.push(Val::Int(8i64));
                kw283.push(("align".into(), Val::Str("center".into())));
                fun284.call(args282, kw283)?
            };
            for item287 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("inlet".into()));
                    s.push(Val::Str("E1 / INLET".into()));
                    s.push(Val::Int(142i64));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("outlet".into()));
                    s.push(Val::Str("E2 / OUTLET".into()));
                    s.push(Val::Int(400i64));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack312 = unpack(item287, 3)?;
                e.set("end", unpack312[0].clone())?;
                e.set("label", unpack312[1].clone())?;
                e.set("dy", unpack312[2].clone())?;
                let assigned288 = {
                    let fun291 = e.get("endpoint")?;
                    let mut args289 = Vec::new();
                    let mut kw290 = Vec::new();
                    args289.push(e.get("end")?);
                    fun291.call(args289, kw290)?
                };
                let unpack292 = unpack(assigned288.clone(), 3)?;
                e.set("ex", unpack292[0].clone())?;
                e.set("ey", unpack292[1].clone())?;
                e.set("ez", unpack292[2].clone())?;
                let assigned293 = {
                    let fun296 = e.get("tail_form")?;
                    let mut args294 = Vec::new();
                    let mut kw295 = Vec::new();
                    args294.push(e.get("end")?);
                    kw295.push(("working_tail".into(), Val::Bool(true)));
                    fun296.call(args294, kw295)?
                }
                .attr("point")?;
                e.set("cut", assigned293.clone())?;
                let assigned297 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("ex")?, e.get("SCALE")?)?,
                    )?);
                    s.push(binary(
                        "add",
                        e.get("y")?,
                        binary("mul", e.get("ey")?, e.get("SCALE")?)?,
                    )?);
                    Val::tuple(s)
                };
                e.set("a", assigned297.clone())?;
                let assigned298 = {
                    let mut s = Vec::new();
                    s.push(binary(
                        "add",
                        e.get("x")?,
                        binary("mul", e.get("cut")?.attr("x")?, e.get("SCALE")?)?,
                    )?);
                    s.push(e.get("a")?.get(Val::Int(1i64))?);
                    Val::tuple(s)
                };
                e.set("b", assigned298.clone())?;
                {
                    let fun301 = e.get("center")?;
                    let mut args299 = Vec::new();
                    let mut kw300 = Vec::new();
                    args299.push(e.get("c")?);
                    args299.extend(e.get("a")?.iter()?);
                    args299.push(Val::Int(6i64));
                    fun301.call(args299, kw300)?
                };
                {
                    let fun304 = e.get("horizontal_dimension")?;
                    let mut args302 = Vec::new();
                    let mut kw303 = Vec::new();
                    args302.push(e.get("c")?);
                    args302.push(e.get("b")?.get(Val::Int(0i64))?);
                    args302.push(e.get("a")?.get(Val::Int(0i64))?);
                    args302.push(e.get("b")?.get(Val::Int(1i64))?);
                    args302.push(e.get("dy")?);
                    args302.push({
                        let mut str305 = String::new();
                        str305.push_str(&format(
                            &e.get("mandrel")?
                                .attr("stub_protrusion")?
                                .get(e.get("end")?)?,
                            &val_string({
                                let mut str306 = String::new();
                                str306.push_str(".0f");
                                Val::Str(str306)
                            })?,
                        )?);
                        str305.push_str(" +5 / -0 WORKING TAIL");
                        Val::Str(str305)
                    });
                    args302.push(Val::Int(9i64));
                    fun304.call(args302, kw303)?
                };
                {
                    let fun309 = e.get("text")?;
                    let mut args307 = Vec::new();
                    let mut kw308 = Vec::new();
                    args307.push(e.get("c")?);
                    args307.push(binary(
                        "truediv",
                        binary(
                            "add",
                            e.get("a")?.get(Val::Int(0i64))?,
                            e.get("b")?.get(Val::Int(0i64))?,
                        )?,
                        Val::Int(2i64),
                    )?);
                    args307.push(binary(
                        "add",
                        e.get("a")?.get(Val::Int(1i64))?,
                        if {
                            let v310 = e.get("end")?;
                            let v311 = Val::Str("inlet".into());
                            Val::Bool(compare("eq", v310.clone(), v311.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            Val::Int(15i64)
                        } else {
                            unary("neg", Val::Int(21i64))?
                        },
                    )?);
                    args307.push(e.get("label")?);
                    args307.push(Val::Int(9i64));
                    kw308.push(("bold".into(), Val::Bool(true)));
                    kw308.push(("align".into(), Val::Str("center".into())));
                    fun309.call(args307, kw308)?
                };
            }
            for item313 in {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("inlet".into()));
                    s.push(Val::Str("H1".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("outlet".into()));
                    s.push(Val::Str("H2".into()));
                    Val::tuple(s)
                });
                Val::list(s)
            }
            .iter()?
            {
                let unpack328 = unpack(item313, 2)?;
                e.set("end", unpack328[0].clone())?;
                e.set("ident", unpack328[1].clone())?;
                let assigned314 = {
                    let fun317 = e.get("tail_form")?;
                    let mut args315 = Vec::new();
                    let mut kw316 = Vec::new();
                    args315.push(e.get("end")?);
                    fun317.call(args315, kw316)?
                }
                .attr("segments")?
                .get(Val::Int(0i64))?
                .get(Val::Str("start".into()))?;
                e.set("point", assigned314.clone())?;
                let assigned318 = {
                    let fun321 = e.get("station_mark")?;
                    let mut args319 = Vec::new();
                    let mut kw320 = Vec::new();
                    args319.push(e.get("c")?);
                    args319.push(e.get("point")?);
                    args319.push(e.get("ident")?);
                    args319.push(e.get("x")?);
                    args319.push(e.get("y")?);
                    args319.push(Val::Str("plan".into()));
                    fun321.call(args319, kw320)?
                };
                let unpack322 = unpack(assigned318.clone(), 2)?;
                e.set("px", unpack322[0].clone())?;
                e.set("py", unpack322[1].clone())?;
                {
                    let fun325 = e.get("text")?;
                    let mut args323 = Vec::new();
                    let mut kw324 = Vec::new();
                    args323.push(e.get("c")?);
                    args323.push(binary("add", e.get("px")?, Val::Int(13i64))?);
                    args323.push(binary(
                        "add",
                        e.get("py")?,
                        if {
                            let v326 = e.get("end")?;
                            let v327 = Val::Str("inlet".into());
                            Val::Bool(compare("eq", v326.clone(), v327.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            unary("neg", Val::Int(15i64))?
                        } else {
                            Val::Int(12i64)
                        },
                    )?);
                    args323.push(e.get("ident")?);
                    args323.push(Val::Float(8.5f64));
                    fun325.call(args323, kw324)?
                };
            }
            {
                let fun331 = e.get("text")?;
                let mut args329 = Vec::new();
                let mut kw330 = Vec::new();
                args329.push(e.get("c")?);
                args329.push(e.get("x")?);
                args329.push(binary("add", e.get("y")?, Val::Int(40i64))?);
                args329.push(Val::Str("180° ±0.5° END CLOCKING".into()));
                args329.push(Val::Float(8.5f64));
                kw330.push(("align".into(), Val::Str("center".into())));
                fun331.call(args329, kw330)?
            };
            {
                let fun334 = e.get("text")?;
                let mut args332 = Vec::new();
                let mut kw333 = Vec::new();
                args332.push(e.get("c")?);
                args332.push(e.get("x")?);
                args332.push(binary("add", e.get("y")?, Val::Int(25i64))?);
                args332.push(Val::Str("INLET TO OUTLET CCW".into()));
                args332.push(Val::Int(8i64));
                kw333.push(("align".into(), Val::Str("center".into())));
                fun334.call(args332, kw333)?
            };
            {
                let fun337 = e.get("text")?;
                let mut args335 = Vec::new();
                let mut kw336 = Vec::new();
                args335.push(e.get("c")?);
                args335.push(e.get("x")?);
                args335.push(binary("sub", e.get("y")?, Val::Int(34i64))?);
                args335.push(Val::Str("HELIX CL Ø133.35 REF".into()));
                args335.push(Val::Float(8.5f64));
                kw336.push(("align".into(), Val::Str("center".into())));
                fun337.call(args335, kw336)?
            };
            {
                let fun340 = e.get("text")?;
                let mut args338 = Vec::new();
                let mut kw339 = Vec::new();
                args338.push(e.get("c")?);
                args338.push(e.get("x")?);
                args338.push(binary("sub", e.get("y")?, Val::Int(51i64))?);
                args338.push(Val::Str("LOCAL BRIDGE RELIEF: NOTE 4".into()));
                args338.push(Val::Float(7.5f64));
                kw339.push(("align".into(), Val::Str("center".into())));
                fun340.call(args338, kw339)?
            };
            {
                let fun343 = e.get("axes")?;
                let mut args341 = Vec::new();
                let mut kw342 = Vec::new();
                args341.push(e.get("c")?);
                args341.push(Val::Int(55i64));
                args341.push(Val::Int(322i64));
                args341.push(Val::Str("+X".into()));
                args341.push(Val::Str("+Y".into()));
                fun343.call(args341, kw342)?
            };
            Ok(Val::None)
        })
    })?;
    // dimension_table
    e.set("dimension_table", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned344 = {
                let mut s = Vec::new();
                s.push(Val::Int(714i64));
                s.push(Val::Int(1178i64));
                s.push(Val::Int(698i64));
                Val::tuple(s)
            };
            let unpack345 = unpack(assigned344.clone(), 3)?;
            e.set("x", unpack345[0].clone())?;
            e.set("r", unpack345[1].clone())?;
            e.set("top", unpack345[2].clone())?;
            {
                let fun348 = e.get("text")?;
                let mut args346 = Vec::new();
                let mut kw347 = Vec::new();
                args346.push(e.get("c")?);
                args346.push(e.get("x")?);
                args346.push(Val::Int(741i64));
                args346.push(Val::Str("PRODUCTION FORM DEFINITION".into()));
                args346.push(Val::Int(11i64));
                kw347.push(("bold".into(), Val::Bool(true)));
                fun348.call(args346, kw347)?
            };
            {
                let fun351 = e.get("text")?;
                let mut args349 = Vec::new();
                let mut kw350 = Vec::new();
                args349.push(e.get("c")?);
                args349.push(e.get("x")?);
                args349.push(Val::Int(724i64));
                args349.push(Val::Str(
                    "ONE CONTINUOUS COPPER TUBE - FINISHED FORM".into(),
                ));
                args349.push(Val::Int(9i64));
                fun351.call(args349, kw350)?
            };
            let assigned352 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("TUBE STOCK".into()));
                    s.push(Val::Str("1/4 IN OD x 0.031 IN WALL ACR COPPER".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("FINISHED WINDING".into()));
                    s.push({
                        let mut str353 = String::new();
                        str353.push_str(&format(
                            &e.get("source")?.attr("TOTAL_WRAPS")?,
                            &val_string({
                                let mut str354 = String::new();
                                str354.push_str(".3f");
                                Val::Str(str354)
                            })?,
                        )?);
                        str353.push_str(" RH TURNS / 180° END CLOCKING");
                        Val::Str(str353)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("HELIX CL SPAN".into()));
                    s.push({
                        let mut str355 = String::new();
                        str355.push_str(&format(
                            &e.get("source")?.attr("WIND_HEIGHT")?,
                            &val_string({
                                let mut str356 = String::new();
                                str356.push_str(".2f");
                                Val::Str(str356)
                            })?,
                        )?);
                        str355.push_str(" ±1.0");
                        Val::Str(str355)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("NOMINAL PITCH".into()));
                    s.push({
                        let mut str357 = String::new();
                        str357.push_str(&format(
                            &e.get("source")?.attr("PITCH")?,
                            &val_string({
                                let mut str358 = String::new();
                                str358.push_str(".3f");
                                Val::Str(str358)
                            })?,
                        )?);
                        str357.push_str(" REF");
                        Val::Str(str357)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("ALL TAIL BENDS".into()));
                    s.push({
                        let mut str359 = String::new();
                        str359.push_str("CL R");
                        str359.push_str(&format(
                            &e.get("source")?.attr("TAIL_BEND_R")?,
                            &val_string({
                                let mut str360 = String::new();
                                str360.push_str(".1f");
                                Val::Str(str360)
                            })?,
                        )?);
                        str359.push_str(" ±0.5");
                        Val::Str(str359)
                    });
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("FORMING DATA".into()));
                    s.push(Val::Str("ANGLES / STRAIGHT LENGTHS REF; SHEET 2".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("EXIT E1 / E2".into()));
                    s.push(Val::Str("Y -77.50 / +77.50; Z 28.425; ±0.25".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("EXIT DIRECTIONS".into()));
                    s.push(Val::Str("PARALLEL TO -X WITHIN 1°".into()));
                    Val::tuple(s)
                });
                s.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("STOCK CUT".into()));
                    s.push({
                        let mut str361 = String::new();
                        str361.push_str(&format(&e.get("CUT_LENGTH")?, &String::new())?);
                        str361.push_str(" +");
                        str361.push_str(&format(&e.get("CUT_PLUS")?, &String::new())?);
                        str361.push_str(" / -0; FINISH ENDS AFTER FORMING");
                        Val::Str(str361)
                    });
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("entries", assigned352.clone())?;
            let assigned362 = binary(
                "sub",
                e.get("top")?,
                binary("mul", Val::Int(22i64), {
                    let fun365 = e.get("len")?;
                    let mut args363 = Vec::new();
                    let mut kw364 = Vec::new();
                    args363.push(e.get("entries")?);
                    fun365.call(args363, kw364)?
                })?,
            )?;
            e.set("bottom", assigned362.clone())?;
            {
                let fun368 = e.get("c")?.attr("setLineWidth")?;
                let mut args366 = Vec::new();
                let mut kw367 = Vec::new();
                args366.push(e.get("THIN")?);
                fun368.call(args366, kw367)?
            };
            {
                let fun371 = e.get("c")?.attr("rect")?;
                let mut args369 = Vec::new();
                let mut kw370 = Vec::new();
                args369.push(e.get("x")?);
                args369.push(e.get("bottom")?);
                args369.push(binary("sub", e.get("r")?, e.get("x")?)?);
                args369.push(binary("sub", e.get("top")?, e.get("bottom")?)?);
                kw370.push(("stroke".into(), Val::Int(1i64)));
                kw370.push(("fill".into(), Val::Int(0i64)));
                fun371.call(args369, kw370)?
            };
            {
                let fun374 = e.get("line")?;
                let mut args372 = Vec::new();
                let mut kw373 = Vec::new();
                args372.push(e.get("c")?);
                args372.push(Val::Int(870i64));
                args372.push(e.get("bottom")?);
                args372.push(Val::Int(870i64));
                args372.push(e.get("top")?);
                fun374.call(args372, kw373)?
            };
            for item375 in {
                let fun388 = e.get("enumerate")?;
                let mut args386 = Vec::new();
                let mut kw387 = Vec::new();
                args386.push(e.get("entries")?);
                fun388.call(args386, kw387)?
            }
            .iter()?
            {
                let unpack389 = unpack(item375, 2)?;
                e.set("i", unpack389[0].clone())?;
                let unpack390 = unpack(unpack389[1].clone(), 2)?;
                e.set("label", unpack390[0].clone())?;
                e.set("value", unpack390[1].clone())?;
                let assigned376 = binary(
                    "sub",
                    e.get("top")?,
                    binary("mul", Val::Int(22i64), e.get("i")?)?,
                )?;
                e.set("yy", assigned376.clone())?;
                if e.get("i")?.truthy()? {
                    {
                        let fun379 = e.get("line")?;
                        let mut args377 = Vec::new();
                        let mut kw378 = Vec::new();
                        args377.push(e.get("c")?);
                        args377.push(e.get("x")?);
                        args377.push(e.get("yy")?);
                        args377.push(e.get("r")?);
                        args377.push(e.get("yy")?);
                        fun379.call(args377, kw378)?
                    };
                }
                {
                    let fun382 = e.get("text")?;
                    let mut args380 = Vec::new();
                    let mut kw381 = Vec::new();
                    args380.push(e.get("c")?);
                    args380.push(binary("add", e.get("x")?, Val::Int(7i64))?);
                    args380.push(binary("sub", e.get("yy")?, Val::Int(14i64))?);
                    args380.push(e.get("label")?);
                    args380.push(Val::Int(8i64));
                    kw381.push(("bold".into(), Val::Bool(true)));
                    fun382.call(args380, kw381)?
                };
                {
                    let fun385 = e.get("text")?;
                    let mut args383 = Vec::new();
                    let mut kw384 = Vec::new();
                    args383.push(e.get("c")?);
                    args383.push(Val::Int(877i64));
                    args383.push(binary("sub", e.get("yy")?, Val::Int(14i64))?);
                    args383.push(e.get("value")?);
                    args383.push(Val::Float(8.2f64));
                    fun385.call(args383, kw384)?
                };
            }
            Ok(Val::None)
        })
    })?;
    // requirements
    e.set("requirements",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun393=e.get("text")?;let mut args391=Vec::new();let mut kw392=Vec::new();args391.push(e.get("c")?);args391.push(Val::Int(714i64));args391.push(Val::Int(473i64));args391.push(Val::Str("MANUFACTURING AND ACCEPTANCE".into()));args391.push(Val::Int(10i64));kw392.push(("bold".into(),Val::Bool(true)));fun393.call(args391,kw392)?};
let assigned394={let mut s=Vec::new();s.push(Val::Str("1. Units: mm. O is the winding axis in X,Y. Z=0 is the cold-core shell base plane. Form and inspect on a fixture locating that axis and the shell exits. This drawing defines the coil before final refrigeration tie-in.".into()));s.push(Val::Str("2. Material: soft ACR copper, continuous and clean. No joint within the core. Form nine full turns plus the 180° upper-end clocking. The helix rises CCW from H1 to H2 when viewed from +Z.".into()));s.push(Val::Str("3. Tail geometry is the tangent sequence on sheet 2. Coordinate stations are tube-centerline points. All bends are R15; preserve the stated straight lengths and exit directions. The working-tail dimensions are measured from E, before refrigeration trimming.".into()));s.push({let mut str395=String::new();str395.push_str("4. Fit to the nominal Ø");str395.push_str(&format(&binary("mul",Val::Int(2i64),e.get("source")?.attr("carbonator_outer_radius")?)?,&val_string({let mut str396=String::new();str396.push_str(".0f");Val::Str(str396)})?)?);str395.push_str(" vessel with the foil thermal interface. Over the reed bridge, raise the tube centerline ");str395.push_str(&format(&e.get("source")?.attr("BRIDGE_LIFT")?,&val_string({let mut str397=String::new();str397.push_str(".2f");Val::Str(str397)})?)?);str395.push_str(" ±0.5 radially and blend smoothly at R12.7 MIN. Bridge zone Z ");str395.push_str(&format(&e.get("source")?.attr("BRIDGE_Z")?.get(Val::Int(0i64))?,&val_string({let mut str398=String::new();str398.push_str(".2f");Val::Str(str398)})?)?);str395.push_str("-");str395.push_str(&format(&e.get("source")?.attr("BRIDGE_Z")?.get(Val::Int(1i64))?,&val_string({let mut str399=String::new();str399.push_str(".2f");Val::Str(str399)})?)?);str395.push_str(" REF, centered on -Y. Preserve reed clearance and thermal contact elsewhere.");Val::Str(str395)});s.push(Val::Str("5. Use the undersized mandrel for rough forming; feed stock and adjust winding to the finished dimensions on the vessel fixture. Acceptance is the specified finished form, not the mandrel groove or an assumed springback.".into()));s.push(Val::Str("6. Reject kinks, creases, cracks and visible flattening. Square-cut and deburr both ends; remove chips and cutting fluid, preserve the open bore and cap the ends until tie-in. Verify the formed coil and both feed-throughs before foam.".into()));s.push(Val::Str("7. Refrigeration joint preparation, heat protection, brazing and leak acceptance follow assembly/refrigerant-loop.md. Trim working tails only at that assembly operation.".into()));Val::list(s)};e.set("items",assigned394.clone())?;
return Ok({let fun402=e.get("paragraphs")?;let mut args400=Vec::new();let mut kw401=Vec::new();args400.push(e.get("c")?);args400.push(Val::Int(714i64));args400.push(Val::Int(453i64));args400.push(e.get("items")?);args400.push(Val::Int(464i64));kw401.push(("size".into(),Val::Int(9i64)));kw401.push(("leading".into(),Val::Int(12i64)));kw401.push(("gap".into(),Val::Int(6i64)));fun402.call(args400,kw401)?});
Ok(Val::None)})})?;
    // table
    e.set("table", {
        let params = vec![
            ("c".into(), None, false),
            ("end".into(), None, false),
            ("x".into(), None, false),
            ("right".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned403 = if {
                let v404 = e.get("end")?;
                let v405 = Val::Str("inlet".into());
                Val::Bool(compare("eq", v404.clone(), v405.clone())?.truthy()?)
            }
            .truthy()?
            {
                Val::Str("INLET TAIL / E1".into())
            } else {
                Val::Str("OUTLET TAIL / E2".into())
            };
            e.set("title", assigned403.clone())?;
            {
                let fun408 = e.get("text")?;
                let mut args406 = Vec::new();
                let mut kw407 = Vec::new();
                args406.push(e.get("c")?);
                args406.push(e.get("x")?);
                args406.push(Val::Int(741i64));
                args406.push(binary(
                    "add",
                    e.get("title")?,
                    Val::Str(" - TANGENT STATIONS".into()),
                )?);
                args406.push(Val::Int(11i64));
                kw407.push(("bold".into(), Val::Bool(true)));
                fun408.call(args406, kw407)?
            };
            {
                let fun411 = e.get("text")?;
                let mut args409 = Vec::new();
                let mut kw410 = Vec::new();
                args409.push(e.get("c")?);
                args409.push(e.get("x")?);
                args409.push(Val::Int(724i64));
                args409.push(Val::Str(
                    "FOLLOW FROM HELIX TO CUT END; ALL BENDS CL R15 ±0.5".into(),
                ));
                args409.push(Val::Float(8.5f64));
                fun411.call(args409, kw410)?
            };
            let assigned412 = {
                let fun415 = e.get("tail_form")?;
                let mut args413 = Vec::new();
                let mut kw414 = Vec::new();
                args413.push(e.get("end")?);
                kw414.push(("working_tail".into(), Val::Bool(true)));
                fun415.call(args413, kw414)?
            };
            e.set("form", assigned412.clone())?;
            let assigned416 = {
                let mut s = Vec::new();
                s.push({
                    let mut s = Vec::new();
                    s.push(
                        if {
                            let v417 = e.get("end")?;
                            let v418 = Val::Str("inlet".into());
                            Val::Bool(compare("eq", v417.clone(), v418.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            Val::Str("H1".into())
                        } else {
                            Val::Str("H2".into())
                        },
                    );
                    s.push(Val::Str("START".into()));
                    s.push(Val::Str("-".into()));
                    s.push(
                        e.get("form")?
                            .attr("segments")?
                            .get(Val::Int(0i64))?
                            .get(Val::Str("start".into()))?,
                    );
                    Val::tuple(s)
                });
                Val::list(s)
            };
            e.set("data", assigned416.clone())?;
            for item419 in e.get("form")?.attr("segments")?.iter()? {
                e.set("segment", item419)?;
                if {
                    let v420 = e.get("segment")?.get(Val::Str("kind".into()))?;
                    let v421 = Val::Str("bend".into());
                    Val::Bool(compare("eq", v420.clone(), v421.clone())?.truthy()?)
                }
                .truthy()?
                {
                    {
                        let fun424 = e.get("data")?.attr("append")?;
                        let mut args422 = Vec::new();
                        let mut kw423 = Vec::new();
                        args422.push({
                            let mut s = Vec::new();
                            s.push(e.get("segment")?.get(Val::Str("id".into()))?);
                            s.push({
                                let mut str425 = String::new();
                                str425.push_str(&format(
                                    &e.get("segment")?.get(Val::Str("angle".into()))?,
                                    &val_string({
                                        let mut str426 = String::new();
                                        str426.push_str(".2f");
                                        Val::Str(str426)
                                    })?,
                                )?);
                                str425.push_str("°");
                                Val::Str(str425)
                            });
                            s.push(
                                if {
                                    let v427 = e.get("segment")?.get(Val::Str("id".into()))?;
                                    let v428 = {
                                        let mut s = Vec::new();
                                        s.push(Val::Str("B0".into()));
                                        s.push(Val::Str("B3".into()));
                                        s.push(Val::Str("B4".into()));
                                        Val::list(s)
                                    };
                                    Val::Bool(compare("in", v427.clone(), v428.clone())?.truthy()?)
                                }
                                .truthy()?
                                {
                                    Val::Str("XZ".into())
                                } else {
                                    Val::Str("XY".into())
                                },
                            );
                            s.push(e.get("segment")?.get(Val::Str("end".into()))?);
                            Val::tuple(s)
                        });
                        fun424.call(args422, kw423)?
                    };
                } else {
                    let assigned429 = if {
                        let v430 = e.get("segment")?.get(Val::Str("id".into()))?;
                        let v431 = Val::Str("WORKING TAIL".into());
                        Val::Bool(compare("eq", v430.clone(), v431.clone())?.truthy()?)
                    }
                    .truthy()?
                    {
                        Val::Str("CUT".into())
                    } else {
                        if {
                            let v434 = {
                                let v435 = e.get("segment")?.get(Val::Str("id".into()))?;
                                let v436 = Val::Str("S2".into());
                                Val::Bool(compare("eq", v435.clone(), v436.clone())?.truthy()?)
                            };
                            if v434.truthy()? {
                                {
                                    let v432 = e.get("end")?;
                                    let v433 = Val::Str("inlet".into());
                                    Val::Bool(compare("eq", v432.clone(), v433.clone())?.truthy()?)
                                }
                            } else {
                                v434
                            }
                        }
                        .truthy()?
                        {
                            Val::Str("E1".into())
                        } else {
                            if {
                                let v437 = e.get("segment")?.get(Val::Str("id".into()))?;
                                let v438 = Val::Str("S2".into());
                                Val::Bool(compare("eq", v437.clone(), v438.clone())?.truthy()?)
                            }
                            .truthy()?
                            {
                                Val::Str("E2".into())
                            } else {
                                e.get("segment")?.get(Val::Str("id".into()))?
                            }
                        }
                    };
                    e.set("label", assigned429.clone())?;
                    {
                        let fun441 = e.get("data")?.attr("append")?;
                        let mut args439 = Vec::new();
                        let mut kw440 = Vec::new();
                        args439.push({
                            let mut s = Vec::new();
                            s.push(e.get("label")?);
                            s.push({
                                let mut str442 = String::new();
                                str442.push_str(&format(
                                    &e.get("segment")?.get(Val::Str("length".into()))?,
                                    &val_string({
                                        let mut str443 = String::new();
                                        str443.push_str(".2f");
                                        Val::Str(str443)
                                    })?,
                                )?);
                                Val::Str(str442)
                            });
                            s.push(Val::Str("STRAIGHT".into()));
                            s.push(e.get("segment")?.get(Val::Str("end".into()))?);
                            Val::tuple(s)
                        });
                        fun441.call(args439, kw440)?
                    };
                }
            }
            let assigned444 = {
                let mut s = Vec::new();
                s.push(e.get("x")?);
                s.push(binary("add", e.get("x")?, Val::Int(51i64))?);
                s.push(binary("add", e.get("x")?, Val::Int(140i64))?);
                s.push(binary("add", e.get("x")?, Val::Int(209i64))?);
                s.push(binary("add", e.get("x")?, Val::Int(314i64))?);
                s.push(binary("add", e.get("x")?, Val::Int(419i64))?);
                s.push(e.get("right")?);
                Val::list(s)
            };
            e.set("cols", assigned444.clone())?;
            let assigned445 = {
                let mut s = Vec::new();
                s.push(Val::Int(698i64));
                s.push(Val::Int(24i64));
                Val::tuple(s)
            };
            let unpack446 = unpack(assigned445.clone(), 2)?;
            e.set("top", unpack446[0].clone())?;
            e.set("row", unpack446[1].clone())?;
            let assigned447 = binary(
                "sub",
                binary("sub", e.get("top")?, Val::Int(23i64))?,
                binary("mul", e.get("row")?, {
                    let fun450 = e.get("len")?;
                    let mut args448 = Vec::new();
                    let mut kw449 = Vec::new();
                    args448.push(e.get("data")?);
                    fun450.call(args448, kw449)?
                })?,
            )?;
            e.set("bottom", assigned447.clone())?;
            {
                let fun453 = e.get("c")?.attr("setLineWidth")?;
                let mut args451 = Vec::new();
                let mut kw452 = Vec::new();
                args451.push(e.get("THIN")?);
                fun453.call(args451, kw452)?
            };
            {
                let fun456 = e.get("c")?.attr("rect")?;
                let mut args454 = Vec::new();
                let mut kw455 = Vec::new();
                args454.push(e.get("x")?);
                args454.push(e.get("bottom")?);
                args454.push(binary("sub", e.get("right")?, e.get("x")?)?);
                args454.push(binary("sub", e.get("top")?, e.get("bottom")?)?);
                kw455.push(("stroke".into(), Val::Int(1i64)));
                kw455.push(("fill".into(), Val::Int(0i64)));
                fun456.call(args454, kw455)?
            };
            for item457 in e
                .get("cols")?
                .get(Val::Slice {
                    start: Some(Val::Int(1i64).integer()?),
                    stop: Some(unary("neg", Val::Int(1i64))?.integer()?),
                    step: 1,
                })?
                .iter()?
            {
                e.set("xx", item457)?;
                {
                    let fun460 = e.get("line")?;
                    let mut args458 = Vec::new();
                    let mut kw459 = Vec::new();
                    args458.push(e.get("c")?);
                    args458.push(e.get("xx")?);
                    args458.push(e.get("bottom")?);
                    args458.push(e.get("xx")?);
                    args458.push(e.get("top")?);
                    fun460.call(args458, kw459)?
                };
            }
            for item461 in {
                let fun467 = e.get("enumerate")?;
                let mut args465 = Vec::new();
                let mut kw466 = Vec::new();
                args465.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("END".into()));
                    s.push(Val::Str("ANGLE / L REF".into()));
                    s.push(Val::Str("PLANE".into()));
                    s.push(Val::Str("X".into()));
                    s.push(Val::Str("Y".into()));
                    s.push(Val::Str("Z".into()));
                    Val::list(s)
                });
                fun467.call(args465, kw466)?
            }
            .iter()?
            {
                let unpack468 = unpack(item461, 2)?;
                e.set("j", unpack468[0].clone())?;
                e.set("title", unpack468[1].clone())?;
                {
                    let fun464 = e.get("text")?;
                    let mut args462 = Vec::new();
                    let mut kw463 = Vec::new();
                    args462.push(e.get("c")?);
                    args462.push(binary(
                        "truediv",
                        binary(
                            "add",
                            e.get("cols")?.get(e.get("j")?)?,
                            e.get("cols")?
                                .get(binary("add", e.get("j")?, Val::Int(1i64))?)?,
                        )?,
                        Val::Int(2i64),
                    )?);
                    args462.push(binary("sub", e.get("top")?, Val::Int(15i64))?);
                    args462.push(e.get("title")?);
                    args462.push(Val::Int(8i64));
                    kw463.push(("bold".into(), Val::Bool(true)));
                    kw463.push(("align".into(), Val::Str("center".into())));
                    fun464.call(args462, kw463)?
                };
            }
            {
                let fun471 = e.get("line")?;
                let mut args469 = Vec::new();
                let mut kw470 = Vec::new();
                args469.push(e.get("c")?);
                args469.push(e.get("x")?);
                args469.push(binary("sub", e.get("top")?, Val::Int(23i64))?);
                args469.push(e.get("right")?);
                args469.push(binary("sub", e.get("top")?, Val::Int(23i64))?);
                fun471.call(args469, kw470)?
            };
            for item472 in {
                let fun493 = e.get("enumerate")?;
                let mut args491 = Vec::new();
                let mut kw492 = Vec::new();
                args491.push(e.get("data")?);
                fun493.call(args491, kw492)?
            }
            .iter()?
            {
                let unpack494 = unpack(item472, 2)?;
                e.set("i", unpack494[0].clone())?;
                let unpack495 = unpack(unpack494[1].clone(), 4)?;
                e.set("label", unpack495[0].clone())?;
                e.set("value", unpack495[1].clone())?;
                e.set("plane", unpack495[2].clone())?;
                e.set("point", unpack495[3].clone())?;
                let assigned473 = binary(
                    "sub",
                    binary("sub", e.get("top")?, Val::Int(23i64))?,
                    binary("mul", e.get("row")?, e.get("i")?)?,
                )?;
                e.set("yy", assigned473.clone())?;
                if e.get("i")?.truthy()? {
                    {
                        let fun476 = e.get("line")?;
                        let mut args474 = Vec::new();
                        let mut kw475 = Vec::new();
                        args474.push(e.get("c")?);
                        args474.push(e.get("x")?);
                        args474.push(e.get("yy")?);
                        args474.push(e.get("right")?);
                        args474.push(e.get("yy")?);
                        fun476.call(args474, kw475)?
                    };
                }
                for item477 in {
                    let fun485 = e.get("enumerate")?;
                    let mut args483 = Vec::new();
                    let mut kw484 = Vec::new();
                    args483.push({
                        let mut s = Vec::new();
                        s.push(e.get("label")?);
                        s.push(e.get("value")?);
                        s.push(e.get("plane")?);
                        s.extend(
                            {
                                let e = e.child();
                                let out486 = Val::list(vec![]);
                                for item487 in e.get("point")?.iter()? {
                                    e.set("v", item487)?;
                                    out486.attr("append")?.call(
                                        vec![{
                                            let mut str488 = String::new();
                                            str488.push_str(&format(
                                                &e.get("v")?,
                                                &val_string({
                                                    let mut str489 = String::new();
                                                    str489.push_str(".3f");
                                                    Val::Str(str489)
                                                })?,
                                            )?);
                                            Val::Str(str488)
                                        }],
                                        vec![],
                                    )?;
                                }
                                out486
                            }
                            .iter()?,
                        );
                        Val::list(s)
                    });
                    fun485.call(args483, kw484)?
                }
                .iter()?
                {
                    let unpack490 = unpack(item477, 2)?;
                    e.set("j", unpack490[0].clone())?;
                    e.set("value", unpack490[1].clone())?;
                    {
                        let fun480 = e.get("text")?;
                        let mut args478 = Vec::new();
                        let mut kw479 = Vec::new();
                        args478.push(e.get("c")?);
                        args478.push(binary(
                            "truediv",
                            binary(
                                "add",
                                e.get("cols")?.get(e.get("j")?)?,
                                e.get("cols")?
                                    .get(binary("add", e.get("j")?, Val::Int(1i64))?)?,
                            )?,
                            Val::Int(2i64),
                        )?);
                        args478.push(binary("sub", e.get("yy")?, Val::Int(16i64))?);
                        args478.push(e.get("value")?);
                        args478.push(Val::Float(8.3f64));
                        kw479.push(("align".into(), Val::Str("center".into())));
                        kw479.push(("bold".into(), {
                            let v481 = e.get("j")?;
                            let v482 = Val::Int(0i64);
                            Val::Bool(compare("eq", v481.clone(), v482.clone())?.truthy()?)
                        }));
                        fun480.call(args478, kw479)?
                    };
                }
            }
            return Ok(e.get("bottom")?);
            Ok(Val::None)
        })
    })?;
    // side_view
    e.set("side_view", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let fun498 = e.get("text")?;
                let mut args496 = Vec::new();
                let mut kw497 = Vec::new();
                args496.push(e.get("c")?);
                args496.push(Val::Int(325i64));
                args496.push(Val::Int(441i64));
                args496.push(Val::Str("SIDE - LOOKING ALONG -Y".into()));
                args496.push(Val::Int(11i64));
                kw497.push(("bold".into(), Val::Bool(true)));
                kw497.push(("align".into(), Val::Str("center".into())));
                fun498.call(args496, kw497)?
            };
            {
                let fun501 = e.get("text")?;
                let mut args499 = Vec::new();
                let mut kw500 = Vec::new();
                args499.push(e.get("c")?);
                args499.push(Val::Int(325i64));
                args499.push(Val::Int(425i64));
                args499.push(Val::Str(
                    "TUBE OUTLINES - NOMINAL WINDING - SCALE 1:2".into(),
                ));
                args499.push(Val::Int(9i64));
                kw500.push(("align".into(), Val::Str("center".into())));
                fun501.call(args499, kw500)?
            };
            {
                let fun504 = e.get("render_view")?;
                let mut args502 = Vec::new();
                let mut kw503 = Vec::new();
                args502.push(e.get("c")?);
                args502.push(Val::Str("side".into()));
                args502.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(150i64));
                    s.push(Val::Int(160i64));
                    Val::tuple(s)
                });
                fun504.call(args502, kw503)?
            };
            let assigned505 = {
                let fun508 = e.get("tail_form")?;
                let mut args506 = Vec::new();
                let mut kw507 = Vec::new();
                args506.push(Val::Str("outlet".into()));
                fun508.call(args506, kw507)?
            };
            e.set("outlet", assigned505.clone())?;
            let assigned509 = {
                let fun512 = e.get("next")?;
                let mut args510 = Vec::new();
                let mut kw511 = Vec::new();
                args510.push({
                    let e = e.child();
                    let out513 = Val::list(vec![]);
                    for item514 in e.get("outlet")?.attr("segments")?.iter()? {
                        e.set("seg", item514)?;
                        if {
                            let v515 = e.get("seg")?.get(Val::Str("id".into()))?;
                            let v516 = Val::Str("S1".into());
                            Val::Bool(compare("eq", v515.clone(), v516.clone())?.truthy()?)
                        }
                        .truthy()?
                        {
                            out513.attr("append")?.call(vec![e.get("seg")?], vec![])?;
                        }
                    }
                    out513
                });
                fun512.call(args510, kw511)?
            };
            e.set("straight", assigned509.clone())?;
            let assigned517 = binary(
                "add",
                Val::Int(150i64),
                binary(
                    "mul",
                    binary(
                        "add",
                        unary(
                            "neg",
                            e.get("straight")?
                                .get(Val::Str("start".into()))?
                                .get(Val::Int(0i64))?,
                        )?,
                        e.get("source")?.attr("TUBE_R")?,
                    )?,
                    e.get("SCALE")?,
                )?,
            )?;
            e.set("px", assigned517.clone())?;
            let assigned518 = binary(
                "add",
                Val::Int(160i64),
                binary(
                    "truediv",
                    binary(
                        "mul",
                        binary(
                            "add",
                            e.get("straight")?
                                .get(Val::Str("start".into()))?
                                .get(Val::Int(2i64))?,
                            e.get("straight")?
                                .get(Val::Str("end".into()))?
                                .get(Val::Int(2i64))?,
                        )?,
                        e.get("SCALE")?,
                    )?,
                    Val::Int(2i64),
                )?,
            )?;
            e.set("py", assigned518.clone())?;
            {
                let fun521 = e.get("leader")?;
                let mut args519 = Vec::new();
                let mut kw520 = Vec::new();
                args519.push(e.get("c")?);
                args519.push({
                    let mut s = Vec::new();
                    s.push(e.get("px")?);
                    s.push(e.get("py")?);
                    Val::tuple(s)
                });
                args519.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(300i64));
                    s.push(Val::Int(330i64));
                    Val::tuple(s)
                });
                args519.push({
                    let mut s = Vec::new();
                    s.push(Val::Int(324i64));
                    s.push(Val::Int(330i64));
                    Val::tuple(s)
                });
                args519.push({
                    let mut s = Vec::new();
                    s.push(Val::Str("OUTLET VERTICAL STRAIGHT".into()));
                    s.push({
                        let mut str522 = String::new();
                        str522.push_str(&format(
                            &e.get("straight")?.get(Val::Str("length".into()))?,
                            &val_string({
                                let mut str523 = String::new();
                                str523.push_str(".2f");
                                Val::Str(str523)
                            })?,
                        )?);
                        str522.push_str(" REF");
                        Val::Str(str522)
                    });
                    Val::list(s)
                });
                args519.push(Val::Int(9i64));
                fun521.call(args519, kw520)?
            };
            {
                let fun526 = e.get("text")?;
                let mut args524 = Vec::new();
                let mut kw525 = Vec::new();
                args524.push(e.get("c")?);
                args524.push(Val::Int(47i64));
                args524.push(Val::Int(153i64));
                args524.push(Val::Str(
                    "BOTH TAILS CONTINUOUS WITH THE HELIX. HIDDEN LINES OMITTED.".into(),
                ));
                args524.push(Val::Int(8i64));
                fun526.call(args524, kw525)?
            };
            {
                let fun529 = e.get("axes")?;
                let mut args527 = Vec::new();
                let mut kw528 = Vec::new();
                args527.push(e.get("c")?);
                args527.push(Val::Int(65i64));
                args527.push(Val::Int(170i64));
                args527.push(Val::Str("-X".into()));
                args527.push(Val::Str("+Z".into()));
                fun529.call(args527, kw528)?
            };
            Ok(Val::None)
        })
    })?;
    // forming_notes
    e.set("forming_notes",{let params=vec![("c".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);{let fun532=e.get("text")?;let mut args530=Vec::new();let mut kw531=Vec::new();args530.push(e.get("c")?);args530.push(Val::Int(714i64));args530.push(Val::Int(434i64));args530.push(Val::Str("HOW THE FORM TABLES DEFINE THE TAILS".into()));args530.push(Val::Int(10i64));kw531.push(("bold".into(),Val::Bool(true)));fun532.call(args530,kw531)?};
let assigned533={let mut s=Vec::new();s.push(Val::Str("1. Each row gives the END of the identified bend or straight. Begin at H1/H2 with the helix tangent. B0 is the small pitch roll-off ending parallel to -X.".into()));s.push(Val::Str("2. B1/B2 are opposite circular bends in XY: first toward the exit lane (-Y inlet, +Y outlet), then back parallel to -X. Each pair has zero intervening straight.".into()));s.push(Val::Str("3. Inlet B3/B4 are opposite bends in XZ, first downward and then back parallel to -X. Outlet B3 turns downward 90°; S1 is vertical; B4 turns 90° back parallel to -X.".into()));s.push(Val::Str("4. E1/E2 end the in-core straights. Continue straight along -X to CUT. Straight lengths are tangent-to-tangent; bend angles are changes in direction. Use a form fixture to reproduce the specified geometry.".into()));s.push(Val::Str("5. Centerline stations: ±0.5 unless separately toleranced. Exit Y/Z: ±0.25. H2 Z and CUT coordinates are REF. Keep every junction tangent; inspect after forming and end finishing.".into()));Val::list(s)};e.set("items",assigned533.clone())?;
return Ok({let fun536=e.get("paragraphs")?;let mut args534=Vec::new();let mut kw535=Vec::new();args534.push(e.get("c")?);args534.push(Val::Int(714i64));args534.push(Val::Int(414i64));args534.push(e.get("items")?);args534.push(Val::Int(464i64));kw535.push(("size".into(),Val::Int(9i64)));kw535.push(("leading".into(),Val::Int(12i64)));kw535.push(("gap".into(),Val::Int(6i64)));fun536.call(args534,kw535)?});
Ok(Val::None)})})?;
    // tube_section
    e.set("tube_section", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned537 = {
                let mut s = Vec::new();
                s.push(Val::Int(780i64));
                s.push(Val::Int(206i64));
                s.push(binary("mul", Val::Int(4i64), e.get("MM")?)?);
                Val::tuple(s)
            };
            let unpack538 = unpack(assigned537.clone(), 3)?;
            e.set("x", unpack538[0].clone())?;
            e.set("y", unpack538[1].clone())?;
            e.set("s", unpack538[2].clone())?;
            let assigned539 = binary("mul", e.get("source")?.attr("TUBE_R")?, e.get("s")?)?;
            e.set("outer", assigned539.clone())?;
            let assigned540 = {
                let fun543 = e.get("c")?.attr("beginPath")?;
                let mut args541 = Vec::new();
                let mut kw542 = Vec::new();
                fun543.call(args541, kw542)?
            };
            e.set("annulus", assigned540.clone())?;
            {
                let fun546 = e.get("annulus")?.attr("circle")?;
                let mut args544 = Vec::new();
                let mut kw545 = Vec::new();
                args544.push(e.get("x")?);
                args544.push(e.get("y")?);
                args544.push(e.get("outer")?);
                fun546.call(args544, kw545)?
            };
            {
                let fun549 = e.get("annulus")?.attr("circle")?;
                let mut args547 = Vec::new();
                let mut kw548 = Vec::new();
                args547.push(e.get("x")?);
                args547.push(e.get("y")?);
                args547.push(binary(
                    "sub",
                    e.get("outer")?,
                    binary("mul", e.get("WALL")?, e.get("s")?)?,
                )?);
                fun549.call(args547, kw548)?
            };
            {
                let fun552 = e.get("hatch")?;
                let mut args550 = Vec::new();
                let mut kw551 = Vec::new();
                args550.push(e.get("c")?);
                args550.push(e.get("annulus")?);
                args550.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("x")?, e.get("outer")?)?);
                    s.push(binary("sub", e.get("y")?, e.get("outer")?)?);
                    s.push(binary("add", e.get("x")?, e.get("outer")?)?);
                    s.push(binary("add", e.get("y")?, e.get("outer")?)?);
                    Val::tuple(s)
                });
                kw551.push(("spacing".into(), Val::Int(6i64)));
                fun552.call(args550, kw551)?
            };
            {
                let fun555 = e.get("c")?.attr("setLineWidth")?;
                let mut args553 = Vec::new();
                let mut kw554 = Vec::new();
                args553.push(e.get("VISIBLE")?);
                fun555.call(args553, kw554)?
            };
            for item556 in {
                let mut s = Vec::new();
                s.push(e.get("outer")?);
                s.push(binary(
                    "sub",
                    e.get("outer")?,
                    binary("mul", e.get("WALL")?, e.get("s")?)?,
                )?);
                Val::list(s)
            }
            .iter()?
            {
                e.set("r", item556)?;
                {
                    let fun559 = e.get("c")?.attr("circle")?;
                    let mut args557 = Vec::new();
                    let mut kw558 = Vec::new();
                    args557.push(e.get("x")?);
                    args557.push(e.get("y")?);
                    args557.push(e.get("r")?);
                    kw558.push(("stroke".into(), Val::Int(1i64)));
                    kw558.push(("fill".into(), Val::Int(0i64)));
                    fun559.call(args557, kw558)?
                };
            }
            {
                let fun562 = e.get("center")?;
                let mut args560 = Vec::new();
                let mut kw561 = Vec::new();
                args560.push(e.get("c")?);
                args560.push(e.get("x")?);
                args560.push(e.get("y")?);
                args560.push(binary("add", e.get("outer")?, Val::Int(6i64))?);
                fun562.call(args560, kw561)?
            };
            {
                let fun565 = e.get("text")?;
                let mut args563 = Vec::new();
                let mut kw564 = Vec::new();
                args563.push(e.get("c")?);
                args563.push(e.get("x")?);
                args563.push(Val::Int(160i64));
                args563.push(Val::Str("TUBE SECTION - 4:1".into()));
                args563.push(Val::Int(8i64));
                kw564.push(("align".into(), Val::Str("center".into())));
                fun565.call(args563, kw564)?
            };
            {
                let fun568 = e.get("text")?;
                let mut args566 = Vec::new();
                let mut kw567 = Vec::new();
                args566.push(e.get("c")?);
                args566.push(Val::Int(840i64));
                args566.push(Val::Int(224i64));
                args566.push(Val::Str("1/4 IN OD x 0.031 IN WALL".into()));
                args566.push(Val::Int(8i64));
                fun568.call(args566, kw567)?
            };
            {
                let fun571 = e.get("text")?;
                let mut args569 = Vec::new();
                let mut kw570 = Vec::new();
                args569.push(e.get("c")?);
                args569.push(Val::Int(840i64));
                args569.push(Val::Int(208i64));
                args569.push(Val::Str("Ø6.35 x 0.787 WALL REF".into()));
                args569.push(Val::Int(8i64));
                fun571.call(args569, kw570)?
            };
            {
                let fun574 = e.get("text")?;
                let mut args572 = Vec::new();
                let mut kw573 = Vec::new();
                args572.push(e.get("c")?);
                args572.push(Val::Int(840i64));
                args572.push(Val::Int(191i64));
                args572.push(Val::Str("OPEN BORE; ENDS DEBURRED".into()));
                args572.push(Val::Int(8i64));
                fun574.call(args572, kw573)?
            };
            Ok(Val::None)
        })
    })?;
    // bridge_section
    e.set("bridge_section", {
        let params = vec![("c".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned575 = Val::Int(1035i64);
            e.set("vessel_x", assigned575.clone())?;
            let assigned576 = binary("mul", Val::Int(4i64), e.get("MM")?)?;
            e.set("scale", assigned576.clone())?;
            let assigned577 = binary(
                "mul",
                e.get("source")?.attr("BRIDGE_LIFT")?,
                e.get("scale")?,
            )?;
            e.set("lift", assigned577.clone())?;
            let assigned578 = Val::Int(206i64);
            e.set("cy", assigned578.clone())?;
            let assigned579 = binary("mul", e.get("source")?.attr("TUBE_R")?, e.get("scale")?)?;
            e.set("outer", assigned579.clone())?;
            let assigned580 = binary(
                "add",
                binary("add", e.get("vessel_x")?, e.get("lift")?)?,
                e.get("outer")?,
            )?;
            e.set("cx", assigned580.clone())?;
            let assigned581 = {
                let fun584 = e.get("path_from_points")?;
                let mut args582 = Vec::new();
                let mut kw583 = Vec::new();
                args582.push(e.get("c")?);
                args582.push({
                    let mut s = Vec::new();
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("vessel_x")?, Val::Int(15i64))?);
                        s.push(Val::Int(170i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("vessel_x")?);
                        s.push(Val::Int(170i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(e.get("vessel_x")?);
                        s.push(Val::Int(245i64));
                        Val::tuple(s)
                    });
                    s.push({
                        let mut s = Vec::new();
                        s.push(binary("sub", e.get("vessel_x")?, Val::Int(15i64))?);
                        s.push(Val::Int(245i64));
                        Val::tuple(s)
                    });
                    Val::list(s)
                });
                fun584.call(args582, kw583)?
            };
            e.set("steel", assigned581.clone())?;
            {
                let fun587 = e.get("hatch")?;
                let mut args585 = Vec::new();
                let mut kw586 = Vec::new();
                args585.push(e.get("c")?);
                args585.push(e.get("steel")?);
                args585.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("vessel_x")?, Val::Int(15i64))?);
                    s.push(Val::Int(170i64));
                    s.push(e.get("vessel_x")?);
                    s.push(Val::Int(245i64));
                    Val::tuple(s)
                });
                kw586.push(("spacing".into(), Val::Int(6i64)));
                fun587.call(args585, kw586)?
            };
            {
                let fun590 = e.get("c")?.attr("setLineWidth")?;
                let mut args588 = Vec::new();
                let mut kw589 = Vec::new();
                args588.push(e.get("VISIBLE")?);
                fun590.call(args588, kw589)?
            };
            {
                let fun593 = e.get("c")?.attr("drawPath")?;
                let mut args591 = Vec::new();
                let mut kw592 = Vec::new();
                args591.push(e.get("steel")?);
                kw592.push(("stroke".into(), Val::Int(1i64)));
                kw592.push(("fill".into(), Val::Int(0i64)));
                fun593.call(args591, kw592)?
            };
            {
                let fun596 = e.get("c")?.attr("rect")?;
                let mut args594 = Vec::new();
                let mut kw595 = Vec::new();
                args594.push(e.get("vessel_x")?);
                args594.push(binary("sub", e.get("cy")?, Val::Int(17i64))?);
                args594.push(e.get("lift")?);
                args594.push(Val::Int(34i64));
                kw595.push(("stroke".into(), Val::Int(1i64)));
                kw595.push(("fill".into(), Val::Int(0i64)));
                fun596.call(args594, kw595)?
            };
            let assigned597 = {
                let fun600 = e.get("c")?.attr("beginPath")?;
                let mut args598 = Vec::new();
                let mut kw599 = Vec::new();
                fun600.call(args598, kw599)?
            };
            e.set("annulus", assigned597.clone())?;
            {
                let fun603 = e.get("annulus")?.attr("circle")?;
                let mut args601 = Vec::new();
                let mut kw602 = Vec::new();
                args601.push(e.get("cx")?);
                args601.push(e.get("cy")?);
                args601.push(e.get("outer")?);
                fun603.call(args601, kw602)?
            };
            {
                let fun606 = e.get("annulus")?.attr("circle")?;
                let mut args604 = Vec::new();
                let mut kw605 = Vec::new();
                args604.push(e.get("cx")?);
                args604.push(e.get("cy")?);
                args604.push(binary(
                    "sub",
                    e.get("outer")?,
                    binary("mul", e.get("WALL")?, e.get("scale")?)?,
                )?);
                fun606.call(args604, kw605)?
            };
            {
                let fun609 = e.get("hatch")?;
                let mut args607 = Vec::new();
                let mut kw608 = Vec::new();
                args607.push(e.get("c")?);
                args607.push(e.get("annulus")?);
                args607.push({
                    let mut s = Vec::new();
                    s.push(binary("sub", e.get("cx")?, e.get("outer")?)?);
                    s.push(binary("sub", e.get("cy")?, e.get("outer")?)?);
                    s.push(binary("add", e.get("cx")?, e.get("outer")?)?);
                    s.push(binary("add", e.get("cy")?, e.get("outer")?)?);
                    Val::tuple(s)
                });
                kw608.push(("spacing".into(), Val::Int(6i64)));
                fun609.call(args607, kw608)?
            };
            {
                let fun612 = e.get("c")?.attr("setLineWidth")?;
                let mut args610 = Vec::new();
                let mut kw611 = Vec::new();
                args610.push(e.get("VISIBLE")?);
                fun612.call(args610, kw611)?
            };
            {
                let fun615 = e.get("c")?.attr("drawPath")?;
                let mut args613 = Vec::new();
                let mut kw614 = Vec::new();
                args613.push(e.get("annulus")?);
                kw614.push(("stroke".into(), Val::Int(1i64)));
                kw614.push(("fill".into(), Val::Int(0i64)));
                fun615.call(args613, kw614)?
            };
            {
                let fun618 = e.get("horizontal_dimension")?;
                let mut args616 = Vec::new();
                let mut kw617 = Vec::new();
                args616.push(e.get("c")?);
                args616.push(e.get("vessel_x")?);
                args616.push(binary("add", e.get("vessel_x")?, e.get("lift")?)?);
                args616.push(binary("add", e.get("cy")?, Val::Int(17i64))?);
                args616.push(Val::Int(252i64));
                args616.push({
                    let mut str619 = String::new();
                    str619.push_str(&format(
                        &e.get("source")?.attr("BRIDGE_LIFT")?,
                        &val_string({
                            let mut str620 = String::new();
                            str620.push_str(".2f");
                            Val::Str(str620)
                        })?,
                    )?);
                    str619.push_str(" ±0.5");
                    Val::Str(str619)
                });
                args616.push(Val::Float(8.5f64));
                fun618.call(args616, kw617)?
            };
            {
                let fun623 = e.get("text")?;
                let mut args621 = Vec::new();
                let mut kw622 = Vec::new();
                args621.push(e.get("c")?);
                args621.push(Val::Int(1090i64));
                args621.push(Val::Int(158i64));
                args621.push(Val::Str("BRIDGE RELIEF - RADIAL SECTION 4:1".into()));
                args621.push(Val::Float(7.4f64));
                kw622.push(("align".into(), Val::Str("center".into())));
                fun623.call(args621, kw622)?
            };
            Ok(Val::None)
        })
    })?;
    // build_pdf
    e.set("build_pdf",{let params=vec![("path".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned624={let fun627=e.get("canvas")?.attr("Canvas")?;let mut args625=Vec::new();let mut kw626=Vec::new();args625.push({let fun630=e.get("str")?;let mut args628=Vec::new();let mut kw629=Vec::new();args628.push(e.get("path")?);fun630.call(args628,kw629)?});kw626.push(("pagesize".into(),e.get("SHEET")?));kw626.push(("invariant".into(),Val::Int(1i64)));kw626.push(("pageCompression".into(),Val::Int(1i64)));fun627.call(args625,kw626)?};e.set("c",assigned624.clone())?;
{let fun633=e.get("c")?.attr("setTitle")?;let mut args631=Vec::new();let mut kw632=Vec::new();args631.push(Val::Str("Evaporator coil - production engineering drawing".into()));fun633.call(args631,kw632)?};
{let fun636=e.get("c")?.attr("setAuthor")?;let mut args634=Vec::new();let mut kw635=Vec::new();args634.push(Val::Str("Home Soda Machine / Codex".into()));fun636.call(args634,kw635)?};
{let fun639=e.get("c")?.attr("setSubject")?;let mut args637=Vec::new();let mut kw638=Vec::new();args637.push(Val::Str("EVAP-01 Rev C: complete formed tube, R15 tangent tails and production form tables".into()));fun639.call(args637,kw638)?};
{let fun642=e.get("frame")?;let mut args640=Vec::new();let mut kw641=Vec::new();args640.push(e.get("c")?);args640.push(e.get("SHEET")?);fun642.call(args640,kw641)?};
{let fun645=e.get("elevation")?;let mut args643=Vec::new();let mut kw644=Vec::new();args643.push(e.get("c")?);fun645.call(args643,kw644)?};
{let fun648=e.get("plan")?;let mut args646=Vec::new();let mut kw647=Vec::new();args646.push(e.get("c")?);fun648.call(args646,kw647)?};
{let fun651=e.get("dimension_table")?;let mut args649=Vec::new();let mut kw650=Vec::new();args649.push(e.get("c")?);fun651.call(args649,kw650)?};
{let fun654=e.get("requirements")?;let mut args652=Vec::new();let mut kw653=Vec::new();args652.push(e.get("c")?);fun654.call(args652,kw653)?};
{let fun657=e.get("title_block")?;let mut args655=Vec::new();let mut kw656=Vec::new();args655.push(e.get("c")?);args655.push(e.get("SHEET")?);args655.push(Val::Str("EVAPORATOR COIL".into()));args655.push(Val::Str("EVAP-01".into()));args655.push(Val::Str("ACR COPPER TUBE".into()));args655.push(Val::Str("1 PER COLD CORE".into()));args655.push(e.get("MATERIAL_ID")?);args655.push({let mut s=Vec::new();s.push(Val::Str("PRODUCTION PART".into()));s.push(Val::Str("FORMED COIL".into()));Val::tuple(s)});kw656.push(("revision".into(),e.get("REVISION")?));kw656.push(("sheet_label".into(),Val::Str("1 OF 2".into())));kw656.push(("date".into(),Val::Str("2026-10-28".into())));fun657.call(args655,kw656)?};
{let fun660=e.get("c")?.attr("showPage")?;let mut args658=Vec::new();let mut kw659=Vec::new();fun660.call(args658,kw659)?};
{let fun663=e.get("frame")?;let mut args661=Vec::new();let mut kw662=Vec::new();args661.push(e.get("c")?);args661.push(e.get("SHEET")?);fun663.call(args661,kw662)?};
{let fun666=e.get("table")?;let mut args664=Vec::new();let mut kw665=Vec::new();args664.push(e.get("c")?);args664.push(Val::Str("inlet".into()));args664.push(Val::Int(47i64));args664.push(Val::Int(605i64));fun666.call(args664,kw665)?};
{let fun669=e.get("table")?;let mut args667=Vec::new();let mut kw668=Vec::new();args667.push(e.get("c")?);args667.push(Val::Str("outlet".into()));args667.push(Val::Int(635i64));args667.push(Val::Int(1190i64));fun669.call(args667,kw668)?};
{let fun672=e.get("side_view")?;let mut args670=Vec::new();let mut kw671=Vec::new();args670.push(e.get("c")?);fun672.call(args670,kw671)?};
{let fun675=e.get("forming_notes")?;let mut args673=Vec::new();let mut kw674=Vec::new();args673.push(e.get("c")?);fun675.call(args673,kw674)?};
{let fun678=e.get("tube_section")?;let mut args676=Vec::new();let mut kw677=Vec::new();args676.push(e.get("c")?);fun678.call(args676,kw677)?};
{let fun681=e.get("bridge_section")?;let mut args679=Vec::new();let mut kw680=Vec::new();args679.push(e.get("c")?);fun681.call(args679,kw680)?};
{let fun684=e.get("title_block")?;let mut args682=Vec::new();let mut kw683=Vec::new();args682.push(e.get("c")?);args682.push(e.get("SHEET")?);args682.push(Val::Str("EVAPORATOR COIL / TAIL FORMS".into()));args682.push(Val::Str("EVAP-01".into()));args682.push(Val::Str("ACR COPPER TUBE".into()));args682.push(Val::Str("1 PER COLD CORE".into()));args682.push(e.get("MATERIAL_ID")?);args682.push({let mut s=Vec::new();s.push(Val::Str("PRODUCTION PART".into()));s.push(Val::Str("FORMED COIL".into()));Val::tuple(s)});kw683.push(("revision".into(),e.get("REVISION")?));kw683.push(("sheet_label".into(),Val::Str("2 OF 2".into())));kw683.push(("date".into(),Val::Str("2026-10-28".into())));fun684.call(args682,kw683)?};
{let fun687=e.get("c")?.attr("showPage")?;let mut args685=Vec::new();let mut kw686=Vec::new();fun687.call(args685,kw686)?};
{let fun690=e.get("c")?.attr("save")?;let mut args688=Vec::new();let mut kw689=Vec::new();fun690.call(args688,kw689)?};
Ok(Val::None)})})?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    {
        let fun693 = e.get("export_pdf")?;
        let mut args691 = Vec::new();
        let mut kw692 = Vec::new();
        args691.push(e.get("build_pdf")?);
        args691.push({
            let fun696 = e.get("str")?;
            let mut args694 = Vec::new();
            let mut kw695 = Vec::new();
            args694.push(e.get("PDF_PATH")?);
            fun696.call(args694, kw695)?
        });
        fun693.call(args691, kw692)?
    };
    {
        let fun699 = e.get("print")?;
        let mut args697 = Vec::new();
        let mut kw698 = Vec::new();
        args697.push({
            let mut str700 = String::new();
            str700.push_str("Exported: ");
            str700.push_str(&format(&e.get("PDF_PATH")?, &String::new())?);
            Val::Str(str700)
        });
        kw698.push(("flush".into(), Val::Bool(true)));
        fun699.call(args697, kw698)?
    };
    Ok(Val::None)
}
