//! Enclosure numbers and frames for the Rust producers.
//!
//! The enclosure's scalar source uses vectors, planes and placements. These are numeric
//! values here; every solid operation is an explicit Rust construction recipe. The normal
//! driver loads this namespace before the source, without loading a Python CAD kernel.
#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("importlib", rt.import_module("importlib")?)?;
    e.set("math", rt.import_module("math")?)?;
    let mod1 = rt.import_module("pathlib")?;
    e.set("Path", rt.member("pathlib", "Path")?)?;
    e.set("sys", rt.import_module("sys")?)?;
    e.set("Vector.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("x".into(), Some(Val::Float(0.0f64)), false),
            ("y".into(), Some(Val::Float(0.0f64)), false),
            ("z".into(), Some(Val::Float(0.0f64)), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun4 = e.get("isinstance")?;
                    let mut args2 = Vec::new();
                    let mut kw3 = Vec::new();
                    args2.push(e.get("x")?);
                    args2.push(e.get("Vector")?);
                    fun4.call(args2, kw3)?
                }
            }
            .truthy()?
            {
                let assigned5 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun8 = e.get("x")?.attr("toTuple")?;
                        let mut args6 = Vec::new();
                        let mut kw7 = Vec::new();
                        fun8.call(args6, kw7)?
                    }
                };
                let unpack9 = unpack(assigned5.clone(), 3)?;
                e.set("x", unpack9[0].clone())?;
                e.set("y", unpack9[1].clone())?;
                e.set("z", unpack9[2].clone())?;
            } else {
                if unary("not", {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun12 = e.get("isinstance")?;
                        let mut args10 = Vec::new();
                        let mut kw11 = Vec::new();
                        args10.push(e.get("x")?);
                        args10.push({
                            let mut s = Vec::new();
                            s.push(e.get("int")?);
                            s.push(e.get("float")?);
                            Val::tuple(s)
                        });
                        fun12.call(args10, kw11)?
                    }
                })?
                .truthy()?
                {
                    let assigned13 = e.get("x")?;
                    let unpack14 = unpack(assigned13.clone(), 3)?;
                    e.set("x", unpack14[0].clone())?;
                    e.set("y", unpack14[1].clone())?;
                    e.set("z", unpack14[2].clone())?;
                }
            }
            let assigned15 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun18 = e.get("map")?;
                    let mut args16 = Vec::new();
                    let mut kw17 = Vec::new();
                    args16.push(e.get("float")?);
                    args16.push({
                        let mut s = Vec::new();
                        s.push(e.get("x")?);
                        s.push(e.get("y")?);
                        s.push(e.get("z")?);
                        Val::tuple(s)
                    });
                    fun18.call(args16, kw17)?
                }
            };
            let unpack19 = unpack(assigned15.clone(), 3)?;
            e.get("self")?.setattr("x", unpack19[0].clone())?;
            e.get("self")?.setattr("y", unpack19[1].clone())?;
            e.get("self")?.setattr("z", unpack19[2].clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("Vector.toTuple", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(e.get("self")?.attr("x")?);
                s.push(e.get("self")?.attr("y")?);
                s.push(e.get("self")?.attr("z")?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    e.set("Vector.__iter__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun22 = e.get("self")?.attr("toTuple")?;
                    let mut args20 = Vec::new();
                    let mut kw21 = Vec::new();
                    fun22.call(args20, kw21)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Vector.__getitem__", {
        let params = vec![("self".into(), None, false), ("key".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun25 = e.get("self")?.attr("toTuple")?;
                    let mut args23 = Vec::new();
                    let mut kw24 = Vec::new();
                    fun25.call(args23, kw24)?
                }
            }
            .get(e.get("key")?)?);
            Ok(Val::None)
        })
    })?;
    e.set("Vector.__add__",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun28=e.get("Vector")?;let mut args26=Vec::new();let mut kw27=Vec::new();args26.extend({let e=e.child();let out29=Val::list(vec![]);for item30 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun33=e.get("zip")?;let mut args31=Vec::new();let mut kw32=Vec::new();args31.push(e.get("self")?);args31.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun36=e.get("Vector")?;let mut args34=Vec::new();let mut kw35=Vec::new();args34.push(e.get("other")?);fun36.call(args34,kw35)?}});fun33.call(args31,kw32)?}}.iter()? {let unpack37=unpack(item30,2)?;e.set("a",unpack37[0].clone())?;e.set("b",unpack37[1].clone())?;out29.attr("append")?.call(vec![binary("add",e.get("a")?,e.get("b")?)?],vec![])?;}out29}.iter()?);fun28.call(args26,kw27)?}});
Ok(Val::None)})})?;
    e.set("Vector.__sub__",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun40=e.get("Vector")?;let mut args38=Vec::new();let mut kw39=Vec::new();args38.extend({let e=e.child();let out41=Val::list(vec![]);for item42 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun45=e.get("zip")?;let mut args43=Vec::new();let mut kw44=Vec::new();args43.push(e.get("self")?);args43.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun48=e.get("Vector")?;let mut args46=Vec::new();let mut kw47=Vec::new();args46.push(e.get("other")?);fun48.call(args46,kw47)?}});fun45.call(args43,kw44)?}}.iter()? {let unpack49=unpack(item42,2)?;e.set("a",unpack49[0].clone())?;e.set("b",unpack49[1].clone())?;out41.attr("append")?.call(vec![binary("sub",e.get("a")?,e.get("b")?)?],vec![])?;}out41}.iter()?);fun40.call(args38,kw39)?}});
Ok(Val::None)})})?;
    e.set("Vector.__mul__", {
        let params = vec![("self".into(), None, false), ("scale".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun52 = e.get("Vector")?;
                    let mut args50 = Vec::new();
                    let mut kw51 = Vec::new();
                    args50.extend(
                        {
                            let e = e.child();
                            let out53 = Val::list(vec![]);
                            for item54 in e.get("self")?.iter()? {
                                e.set("a", item54)?;
                                out53.attr("append")?.call(
                                    vec![binary("mul", e.get("a")?, e.get("scale")?)?],
                                    vec![],
                                )?;
                            }
                            out53
                        }
                        .iter()?,
                    );
                    fun52.call(args50, kw51)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Vector.__truediv__", {
        let params = vec![("self".into(), None, false), ("scale".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "mul",
                e.get("self")?,
                binary("truediv", Val::Float(1.0f64), e.get("scale")?)?,
            )?);
            Ok(Val::None)
        })
    })?;
    e.set("Vector.__neg__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "mul",
                e.get("self")?,
                unary("neg", Val::Float(1.0f64))?,
            )?);
            Ok(Val::None)
        })
    })?;
    e.set("Vector.Length", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun57 = e.get("math")?.attr("sqrt")?;
                    let mut args55 = Vec::new();
                    let mut kw56 = Vec::new();
                    args55.push({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                            line!(),
                        );
                        {
                            let fun60 = e.get("self")?.attr("dot")?;
                            let mut args58 = Vec::new();
                            let mut kw59 = Vec::new();
                            args58.push(e.get("self")?);
                            fun60.call(args58, kw59)?
                        }
                    });
                    fun57.call(args55, kw56)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Vector.normalized", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(binary(
                "truediv",
                e.get("self")?,
                e.get("self")?.attr("Length")?,
            )?);
            Ok(Val::None)
        })
    })?;
    e.set("Vector.dot",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun63=e.get("sum")?;let mut args61=Vec::new();let mut kw62=Vec::new();args61.push({let e=e.child();let out64=Val::list(vec![]);for item65 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun68=e.get("zip")?;let mut args66=Vec::new();let mut kw67=Vec::new();args66.push(e.get("self")?);args66.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun71=e.get("Vector")?;let mut args69=Vec::new();let mut kw70=Vec::new();args69.push(e.get("other")?);fun71.call(args69,kw70)?}});fun68.call(args66,kw67)?}}.iter()? {let unpack72=unpack(item65,2)?;e.set("a",unpack72[0].clone())?;e.set("b",unpack72[1].clone())?;out64.attr("append")?.call(vec![binary("mul",e.get("a")?,e.get("b")?)?],vec![])?;}out64});fun63.call(args61,kw62)?}});
Ok(Val::None)})})?;
    e.set("Vector.cross", {
        let params = vec![("self".into(), None, false), ("other".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned73 = e.get("self")?;
            let unpack74 = unpack(assigned73.clone(), 3)?;
            e.set("a", unpack74[0].clone())?;
            e.set("b", unpack74[1].clone())?;
            e.set("c", unpack74[2].clone())?;
            let assigned75 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun78 = e.get("Vector")?;
                    let mut args76 = Vec::new();
                    let mut kw77 = Vec::new();
                    args76.push(e.get("other")?);
                    fun78.call(args76, kw77)?
                }
            };
            let unpack79 = unpack(assigned75.clone(), 3)?;
            e.set("d", unpack79[0].clone())?;
            e.set("e", unpack79[1].clone())?;
            e.set("f", unpack79[2].clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun82 = e.get("Vector")?;
                    let mut args80 = Vec::new();
                    let mut kw81 = Vec::new();
                    args80.push(binary(
                        "sub",
                        binary("mul", e.get("b")?, e.get("f")?)?,
                        binary("mul", e.get("c")?, e.get("e")?)?,
                    )?);
                    args80.push(binary(
                        "sub",
                        binary("mul", e.get("c")?, e.get("d")?)?,
                        binary("mul", e.get("a")?, e.get("f")?)?,
                    )?);
                    args80.push(binary(
                        "sub",
                        binary("mul", e.get("a")?, e.get("e")?)?,
                        binary("mul", e.get("b")?, e.get("d")?)?,
                    )?);
                    fun82.call(args80, kw81)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Vector.getAngle",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned83={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun86=e.get("Vector")?;let mut args84=Vec::new();let mut kw85=Vec::new();args84.push(e.get("other")?);fun86.call(args84,kw85)?}};e.set("other",assigned83.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun89=e.get("math")?.attr("acos")?;let mut args87=Vec::new();let mut kw88=Vec::new();args87.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun92=e.get("max")?;let mut args90=Vec::new();let mut kw91=Vec::new();args90.push(unary("neg",Val::Float(1.0f64))?);args90.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun95=e.get("min")?;let mut args93=Vec::new();let mut kw94=Vec::new();args93.push(Val::Float(1.0f64));args93.push(binary("truediv",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun98=e.get("self")?.attr("dot")?;let mut args96=Vec::new();let mut kw97=Vec::new();args96.push(e.get("other")?);fun98.call(args96,kw97)?}},binary("mul",e.get("self")?.attr("Length")?,e.get("other")?.attr("Length")?)?)?);fun95.call(args93,kw94)?}});fun92.call(args90,kw91)?}});fun89.call(args87,kw88)?}});
Ok(Val::None)})})?;
    e.set("Vector.__repr__", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut str99 = String::new();
                str99.push_str("Vector");
                str99.push_str(&format(
                    &builtin_call(
                        "repr",
                        vec![{
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                                line!(),
                            );
                            {
                                let fun102 = e.get("self")?.attr("toTuple")?;
                                let mut args100 = Vec::new();
                                let mut kw101 = Vec::new();
                                fun102.call(args100, kw101)?
                            }
                        }],
                        vec![],
                    )?,
                    &String::new(),
                )?);
                Val::Str(str99)
            });
            Ok(Val::None)
        })
    })?;
    e.set("Vector", rt.python_type("_enclosure_datums", "Vector")?)?;
    e.set("Plane.__init__", {
        let params = vec![
            ("self".into(), None, false),
            (
                "origin".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }),
                false,
            ),
            (
                "xDir".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(1i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }),
                false,
            ),
            (
                "normal".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(1i64));
                    Val::tuple(s)
                }),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned103 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun106 = e.get("Vector")?;
                    let mut args104 = Vec::new();
                    let mut kw105 = Vec::new();
                    args104.push(e.get("origin")?);
                    fun106.call(args104, kw105)?
                }
            };
            e.get("self")?.setattr("origin", assigned103.clone())?;
            let assigned107 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun110 = {
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                            line!(),
                        );
                        {
                            let fun113 = e.get("Vector")?;
                            let mut args111 = Vec::new();
                            let mut kw112 = Vec::new();
                            args111.push(e.get("normal")?);
                            fun113.call(args111, kw112)?
                        }
                    }
                    .attr("normalized")?;
                    let mut args108 = Vec::new();
                    let mut kw109 = Vec::new();
                    fun110.call(args108, kw109)?
                }
            };
            e.get("self")?.setattr("zDir", assigned107.clone())?;
            let assigned114 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun117 = binary(
                        "sub",
                        {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                                line!(),
                            );
                            {
                                let fun120 = e.get("Vector")?;
                                let mut args118 = Vec::new();
                                let mut kw119 = Vec::new();
                                args118.push(e.get("xDir")?);
                                fun120.call(args118, kw119)?
                            }
                        },
                        binary("mul", e.get("self")?.attr("zDir")?, {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                                line!(),
                            );
                            {
                                let fun123 = e.get("self")?.attr("zDir")?.attr("dot")?;
                                let mut args121 = Vec::new();
                                let mut kw122 = Vec::new();
                                args121.push(e.get("xDir")?);
                                fun123.call(args121, kw122)?
                            }
                        })?,
                    )?
                    .attr("normalized")?;
                    let mut args115 = Vec::new();
                    let mut kw116 = Vec::new();
                    fun117.call(args115, kw116)?
                }
            };
            e.get("self")?.setattr("xDir", assigned114.clone())?;
            let assigned124 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun127 = e.get("self")?.attr("zDir")?.attr("cross")?;
                    let mut args125 = Vec::new();
                    let mut kw126 = Vec::new();
                    args125.push(e.get("self")?.attr("xDir")?);
                    fun127.call(args125, kw126)?
                }
            };
            e.get("self")?.setattr("yDir", assigned124.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("Plane.named", {
        let params = vec![
            ("cls".into(), None, false),
            ("name".into(), None, false),
            (
                "origin".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }),
                false,
            ),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned128 = {
                let d = Val::dict(vec![]);
                d.set(Val::Str("XY".into()), {
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
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("YZ".into()), {
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
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("XZ".into()), {
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
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("YX".into()), {
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
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        s.push(unary("neg", Val::Int(1i64))?);
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("ZY".into()), {
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
                        s.push(unary("neg", Val::Int(1i64))?);
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d.set(Val::Str("ZX".into()), {
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
                        s.push(Val::Int(0i64));
                        s.push(Val::Int(1i64));
                        s.push(Val::Int(0i64));
                        Val::tuple(s)
                    });
                    Val::tuple(s)
                })?;
                d
            };
            e.set("axes", assigned128.clone())?;
            let assigned129 = e.get("axes")?.get(e.get("name")?)?;
            let unpack130 = unpack(assigned129.clone(), 2)?;
            e.set("x", unpack130[0].clone())?;
            e.set("z", unpack130[1].clone())?;
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun133 = e.get("cls")?;
                    let mut args131 = Vec::new();
                    let mut kw132 = Vec::new();
                    args131.push(e.get("origin")?);
                    args131.push(e.get("x")?);
                    args131.push(e.get("z")?);
                    fun133.call(args131, kw132)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Plane.toWorldCoords", {
        let params = vec![("self".into(), None, false), ("point".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned134 = {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun137 = e.get("tuple")?;
                    let mut args135 = Vec::new();
                    let mut kw136 = Vec::new();
                    args135.push(e.get("point")?);
                    fun137.call(args135, kw136)?
                }
            };
            e.set("point", assigned134.clone())?;
            if {
                let v141 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun140 = e.get("len")?;
                        let mut args138 = Vec::new();
                        let mut kw139 = Vec::new();
                        args138.push(e.get("point")?);
                        fun140.call(args138, kw139)?
                    }
                };
                let v142 = Val::Int(2i64);
                Val::Bool(compare("eq", v141.clone(), v142.clone())?.truthy()?)
            }
            .truthy()?
            {
                let assigned143 = {
                    let mut s = Vec::new();
                    s.extend(e.get("point")?.iter()?);
                    s.push(Val::Float(0.0f64));
                    Val::tuple(s)
                };
                e.set("point", assigned143.clone())?;
            }
            return Ok(binary(
                "add",
                binary(
                    "add",
                    binary(
                        "add",
                        e.get("self")?.attr("origin")?,
                        binary(
                            "mul",
                            e.get("self")?.attr("xDir")?,
                            e.get("point")?.get(Val::Int(0i64))?,
                        )?,
                    )?,
                    binary(
                        "mul",
                        e.get("self")?.attr("yDir")?,
                        e.get("point")?.get(Val::Int(1i64))?,
                    )?,
                )?,
                binary(
                    "mul",
                    e.get("self")?.attr("zDir")?,
                    e.get("point")?.get(Val::Int(2i64))?,
                )?,
            )?);
            Ok(Val::None)
        })
    })?;
    e.set("Plane.toLocalCoords",{let params=vec![("self".into(),None,false),("point".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned144=binary("sub",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun147=e.get("Vector")?;let mut args145=Vec::new();let mut kw146=Vec::new();args145.push(e.get("point")?);fun147.call(args145,kw146)?}},e.get("self")?.attr("origin")?)?;e.set("point",assigned144.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun150=e.get("Vector")?;let mut args148=Vec::new();let mut kw149=Vec::new();args148.extend({let e=e.child();let out151=Val::list(vec![]);for item152 in {let mut s=Vec::new();s.push(e.get("self")?.attr("xDir")?);s.push(e.get("self")?.attr("yDir")?);s.push(e.get("self")?.attr("zDir")?);Val::tuple(s)}.iter()? {e.set("axis",item152)?;out151.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun155=e.get("point")?.attr("dot")?;let mut args153=Vec::new();let mut kw154=Vec::new();args153.push(e.get("axis")?);fun155.call(args153,kw154)?}}],vec![])?;}out151}.iter()?);fun150.call(args148,kw149)?}});
Ok(Val::None)})})?;
    e.set("Plane.location", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun158 = e.get("Location")?;
                    let mut args156 = Vec::new();
                    let mut kw157 = Vec::new();
                    args156.push(e.get("self")?);
                    fun158.call(args156, kw157)?
                }
            });
            Ok(Val::None)
        })
    })?;
    e.set("Plane", rt.python_type("_enclosure_datums", "Plane")?)?;
    e.set("_Matrix.__init__", {
        let params = vec![("self".into(), None, false), ("rows".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned159 = e.get("rows")?;
            e.get("self")?.setattr("rows", assigned159.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("_Matrix.Transformation", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?);
            Ok(Val::None)
        })
    })?;
    e.set("_Matrix.Value", {
        let params = vec![
            ("self".into(), None, false),
            ("row".into(), None, false),
            ("column".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e
                .get("self")?
                .attr("rows")?
                .get(binary("sub", e.get("row")?, Val::Int(1i64))?)?
                .get(binary("sub", e.get("column")?, Val::Int(1i64))?)?);
            Ok(Val::None)
        })
    })?;
    e.set("_Matrix", rt.python_type("_enclosure_datums", "_Matrix")?)?;
    e.set("Location.__init__",{let params=vec![("self".into(),None,false),("point".into(),Some({let mut s=Vec::new();s.push(Val::Int(0i64));s.push(Val::Int(0i64));s.push(Val::Int(0i64));Val::tuple(s)}),false),("axis".into(),Some(Val::None),false),("angle".into(),Some(Val::Float(0.0f64)),false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun162=e.get("isinstance")?;let mut args160=Vec::new();let mut kw161=Vec::new();args160.push(e.get("point")?);args160.push(e.get("Location")?);fun162.call(args160,kw161)?}}.truthy()? {
let assigned163=e.get("point")?.attr("rows")?;e.get("self")?.setattr("rows",assigned163.clone())?;
}else{
if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun166=e.get("isinstance")?;let mut args164=Vec::new();let mut kw165=Vec::new();args164.push(e.get("point")?);args164.push(e.get("Plane")?);fun166.call(args164,kw165)?}}.truthy()? {
let assigned167={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun170=e.get("tuple")?;let mut args168=Vec::new();let mut kw169=Vec::new();args168.push({let e=e.child();let out171=Val::list(vec![]);for item172 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun175=e.get("range")?;let mut args173=Vec::new();let mut kw174=Vec::new();args173.push(Val::Int(3i64));fun175.call(args173,kw174)?}}.iter()? {e.set("k",item172)?;out171.attr("append")?.call(vec![binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun178=e.get("tuple")?;let mut args176=Vec::new();let mut kw177=Vec::new();args176.push({let e=e.child();let out179=Val::list(vec![]);for item180 in {let mut s=Vec::new();s.push(e.get("point")?.attr("xDir")?);s.push(e.get("point")?.attr("yDir")?);s.push(e.get("point")?.attr("zDir")?);Val::tuple(s)}.iter()? {e.set("axis",item180)?;out179.attr("append")?.call(vec![e.get("axis")?.get(e.get("k")?)?],vec![])?;}out179});fun178.call(args176,kw177)?}},{let mut s=Vec::new();s.push(e.get("point")?.attr("origin")?.get(e.get("k")?)?);Val::tuple(s)})?],vec![])?;}out171});fun170.call(args168,kw169)?}};e.get("self")?.setattr("rows",assigned167.clone())?;
}else{
let assigned181={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun184=e.get("Vector")?;let mut args182=Vec::new();let mut kw183=Vec::new();args182.push(e.get("point")?);fun184.call(args182,kw183)?}};e.set("point",assigned181.clone())?;
if {let v185=e.get("axis")?;let v186=Val::None;Val::Bool(compare("is",v185.clone(),v186.clone())?.truthy()?)}.truthy()? {
let assigned187={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));s.push(Val::Float(0.0f64));Val::tuple(s)});s.push({let mut s=Vec::new();s.push(Val::Float(0.0f64));s.push(Val::Float(0.0f64));s.push(Val::Float(1.0f64));Val::tuple(s)});Val::tuple(s)};e.set("rotation",assigned187.clone())?;
}else{
let assigned188={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun191={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun194=e.get("Vector")?;let mut args192=Vec::new();let mut kw193=Vec::new();args192.push(e.get("axis")?);fun194.call(args192,kw193)?}}.attr("normalized")?;let mut args189=Vec::new();let mut kw190=Vec::new();fun191.call(args189,kw190)?}};let unpack195=unpack(assigned188.clone(),3)?;e.set("x",unpack195[0].clone())?;e.set("y",unpack195[1].clone())?;e.set("z",unpack195[2].clone())?;
let assigned196={let mut s=Vec::new();s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun199=e.get("math")?.attr("cos")?;let mut args197=Vec::new();let mut kw198=Vec::new();args197.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun202=e.get("math")?.attr("radians")?;let mut args200=Vec::new();let mut kw201=Vec::new();args200.push(e.get("angle")?);fun202.call(args200,kw201)?}});fun199.call(args197,kw198)?}});s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun205=e.get("math")?.attr("sin")?;let mut args203=Vec::new();let mut kw204=Vec::new();args203.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun208=e.get("math")?.attr("radians")?;let mut args206=Vec::new();let mut kw207=Vec::new();args206.push(e.get("angle")?);fun208.call(args206,kw207)?}});fun205.call(args203,kw204)?}});Val::tuple(s)};let unpack209=unpack(assigned196.clone(),2)?;e.set("c",unpack209[0].clone())?;e.set("s",unpack209[1].clone())?;
let assigned210=binary("sub",Val::Float(1.0f64),e.get("c")?)?;e.set("d",assigned210.clone())?;
let assigned211={let mut s=Vec::new();s.push({let mut s=Vec::new();s.push(binary("add",e.get("c")?,binary("mul",binary("mul",e.get("x")?,e.get("x")?)?,e.get("d")?)?)?);s.push(binary("sub",binary("mul",binary("mul",e.get("x")?,e.get("y")?)?,e.get("d")?)?,binary("mul",e.get("z")?,e.get("s")?)?)?);s.push(binary("add",binary("mul",binary("mul",e.get("x")?,e.get("z")?)?,e.get("d")?)?,binary("mul",e.get("y")?,e.get("s")?)?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("add",binary("mul",binary("mul",e.get("y")?,e.get("x")?)?,e.get("d")?)?,binary("mul",e.get("z")?,e.get("s")?)?)?);s.push(binary("add",e.get("c")?,binary("mul",binary("mul",e.get("y")?,e.get("y")?)?,e.get("d")?)?)?);s.push(binary("sub",binary("mul",binary("mul",e.get("y")?,e.get("z")?)?,e.get("d")?)?,binary("mul",e.get("x")?,e.get("s")?)?)?);Val::tuple(s)});s.push({let mut s=Vec::new();s.push(binary("sub",binary("mul",binary("mul",e.get("z")?,e.get("x")?)?,e.get("d")?)?,binary("mul",e.get("y")?,e.get("s")?)?)?);s.push(binary("add",binary("mul",binary("mul",e.get("z")?,e.get("y")?)?,e.get("d")?)?,binary("mul",e.get("x")?,e.get("s")?)?)?);s.push(binary("add",e.get("c")?,binary("mul",binary("mul",e.get("z")?,e.get("z")?)?,e.get("d")?)?)?);Val::tuple(s)});Val::tuple(s)};e.set("rotation",assigned211.clone())?;
}
let assigned212={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun215=e.get("tuple")?;let mut args213=Vec::new();let mut kw214=Vec::new();args213.push({let e=e.child();let out216=Val::list(vec![]);for item217 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun220=e.get("enumerate")?;let mut args218=Vec::new();let mut kw219=Vec::new();args218.push(e.get("rotation")?);fun220.call(args218,kw219)?}}.iter()? {let unpack221=unpack(item217,2)?;e.set("k",unpack221[0].clone())?;e.set("row",unpack221[1].clone())?;out216.attr("append")?.call(vec![binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun224=e.get("tuple")?;let mut args222=Vec::new();let mut kw223=Vec::new();args222.push(e.get("row")?);fun224.call(args222,kw223)?}},{let mut s=Vec::new();s.push(e.get("point")?.get(e.get("k")?)?);Val::tuple(s)})?],vec![])?;}out216});fun215.call(args213,kw214)?}};e.get("self")?.setattr("rows",assigned212.clone())?;
}
}
let assigned225={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun228=e.get("_Matrix")?;let mut args226=Vec::new();let mut kw227=Vec::new();args226.push(e.get("self")?.attr("rows")?);fun228.call(args226,kw227)?}};e.get("self")?.setattr("wrapped",assigned225.clone())?;
Ok(Val::None)})})?;
    e.set("Location.__mul__",{let params=vec![("self".into(),None,false),("other".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned229={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun232=e.get("Location")?;let mut args230=Vec::new();let mut kw231=Vec::new();args230.push(e.get("other")?);fun232.call(args230,kw231)?}};e.set("other",assigned229.clone())?;
let assigned233={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun236=e.get("tuple")?;let mut args234=Vec::new();let mut kw235=Vec::new();args234.push({let e=e.child();let out237=Val::list(vec![]);for item238 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun241=e.get("range")?;let mut args239=Vec::new();let mut kw240=Vec::new();args239.push(Val::Int(3i64));fun241.call(args239,kw240)?}}.iter()? {e.set("i",item238)?;out237.attr("append")?.call(vec![binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun244=e.get("tuple")?;let mut args242=Vec::new();let mut kw243=Vec::new();args242.push({let e=e.child();let out245=Val::list(vec![]);for item246 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun249=e.get("range")?;let mut args247=Vec::new();let mut kw248=Vec::new();args247.push(Val::Int(3i64));fun249.call(args247,kw248)?}}.iter()? {e.set("j",item246)?;out245.attr("append")?.call(vec![{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun252=e.get("sum")?;let mut args250=Vec::new();let mut kw251=Vec::new();args250.push({let e=e.child();let out253=Val::list(vec![]);for item254 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun257=e.get("range")?;let mut args255=Vec::new();let mut kw256=Vec::new();args255.push(Val::Int(3i64));fun257.call(args255,kw256)?}}.iter()? {e.set("k",item254)?;out253.attr("append")?.call(vec![binary("mul",e.get("self")?.attr("rows")?.get(e.get("i")?)?.get(e.get("k")?)?,e.get("other")?.attr("rows")?.get(e.get("k")?)?.get(e.get("j")?)?)?],vec![])?;}out253});fun252.call(args250,kw251)?}}],vec![])?;}out245});fun244.call(args242,kw243)?}},{let mut s=Vec::new();s.push(binary("add",e.get("self")?.attr("rows")?.get(e.get("i")?)?.get(Val::Int(3i64))?,{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun260=e.get("sum")?;let mut args258=Vec::new();let mut kw259=Vec::new();args258.push({let e=e.child();let out261=Val::list(vec![]);for item262 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun265=e.get("range")?;let mut args263=Vec::new();let mut kw264=Vec::new();args263.push(Val::Int(3i64));fun265.call(args263,kw264)?}}.iter()? {e.set("k",item262)?;out261.attr("append")?.call(vec![binary("mul",e.get("self")?.attr("rows")?.get(e.get("i")?)?.get(e.get("k")?)?,e.get("other")?.attr("rows")?.get(e.get("k")?)?.get(Val::Int(3i64))?)?],vec![])?;}out261});fun260.call(args258,kw259)?}})?);Val::tuple(s)})?],vec![])?;}out237});fun236.call(args234,kw235)?}};e.set("rows",assigned233.clone())?;
let assigned266={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun269=e.get("Location")?;let mut args267=Vec::new();let mut kw268=Vec::new();fun269.call(args267,kw268)?}};e.set("result",assigned266.clone())?;
let assigned270={let mut s=Vec::new();s.push(e.get("rows")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun273=e.get("_Matrix")?;let mut args271=Vec::new();let mut kw272=Vec::new();args271.push(e.get("rows")?);fun273.call(args271,kw272)?}});Val::tuple(s)};let unpack274=unpack(assigned270.clone(),2)?;e.get("result")?.setattr("rows",unpack274[0].clone())?;e.get("result")?.setattr("wrapped",unpack274[1].clone())?;
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    e.set("Location.inverse",{let params=vec![("self".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);let assigned275={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun278=e.get("tuple")?;let mut args276=Vec::new();let mut kw277=Vec::new();args276.push({let e=e.child();let out279=Val::list(vec![]);for item280 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun283=e.get("range")?;let mut args281=Vec::new();let mut kw282=Vec::new();args281.push(Val::Int(3i64));fun283.call(args281,kw282)?}}.iter()? {e.set("i",item280)?;out279.attr("append")?.call(vec![binary("add",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun286=e.get("tuple")?;let mut args284=Vec::new();let mut kw285=Vec::new();args284.push({let e=e.child();let out287=Val::list(vec![]);for item288 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun291=e.get("range")?;let mut args289=Vec::new();let mut kw290=Vec::new();args289.push(Val::Int(3i64));fun291.call(args289,kw290)?}}.iter()? {e.set("j",item288)?;out287.attr("append")?.call(vec![e.get("self")?.attr("rows")?.get(e.get("j")?)?.get(e.get("i")?)?],vec![])?;}out287});fun286.call(args284,kw285)?}},{let mut s=Vec::new();s.push(unary("neg",{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun294=e.get("sum")?;let mut args292=Vec::new();let mut kw293=Vec::new();args292.push({let e=e.child();let out295=Val::list(vec![]);for item296 in {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun299=e.get("range")?;let mut args297=Vec::new();let mut kw298=Vec::new();args297.push(Val::Int(3i64));fun299.call(args297,kw298)?}}.iter()? {e.set("j",item296)?;out295.attr("append")?.call(vec![binary("mul",e.get("self")?.attr("rows")?.get(e.get("j")?)?.get(e.get("i")?)?,e.get("self")?.attr("rows")?.get(e.get("j")?)?.get(Val::Int(3i64))?)?],vec![])?;}out295});fun294.call(args292,kw293)?}})?);Val::tuple(s)})?],vec![])?;}out279});fun278.call(args276,kw277)?}};e.set("rows",assigned275.clone())?;
let assigned300={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun303=e.get("Location")?;let mut args301=Vec::new();let mut kw302=Vec::new();fun303.call(args301,kw302)?}};e.set("result",assigned300.clone())?;
let assigned304={let mut s=Vec::new();s.push(e.get("rows")?);s.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun307=e.get("_Matrix")?;let mut args305=Vec::new();let mut kw306=Vec::new();args305.push(e.get("rows")?);fun307.call(args305,kw306)?}});Val::tuple(s)};let unpack308=unpack(assigned304.clone(),2)?;e.get("result")?.setattr("rows",unpack308[0].clone())?;e.get("result")?.setattr("wrapped",unpack308[1].clone())?;
return Ok(e.get("result")?);
Ok(Val::None)})})?;
    e.set("Location", rt.python_type("_enclosure_datums", "Location")?)?;
    e.set("Workplane.__init__", {
        let params = vec![
            ("self".into(), None, false),
            ("plane".into(), Some(Val::Str("XY".into())), false),
            (
                "origin".into(),
                Some({
                    let mut s = Vec::new();
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    s.push(Val::Int(0i64));
                    Val::tuple(s)
                }),
                false,
            ),
            ("obj".into(), Some(Val::None), false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned309 = if {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun312 = e.get("isinstance")?;
                    let mut args310 = Vec::new();
                    let mut kw311 = Vec::new();
                    args310.push(e.get("plane")?);
                    args310.push(e.get("Plane")?);
                    fun312.call(args310, kw311)?
                }
            }
            .truthy()?
            {
                e.get("plane")?
            } else {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun315 = e.get("Plane")?.attr("named")?;
                        let mut args313 = Vec::new();
                        let mut kw314 = Vec::new();
                        args313.push(e.get("plane")?);
                        args313.push(e.get("origin")?);
                        fun315.call(args313, kw314)?
                    }
                }
            };
            e.get("self")?.setattr("plane", assigned309.clone())?;
            let assigned316 = if {
                let v317 = e.get("obj")?;
                let v318 = Val::None;
                Val::Bool(compare("is", v317.clone(), v318.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let mut s = Vec::new();
                    Val::list(s)
                }
            } else {
                {
                    let mut s = Vec::new();
                    s.push(e.get("obj")?);
                    Val::list(s)
                }
            };
            e.get("self")?.setattr("objects", assigned316.clone())?;
            Ok(Val::None)
        })
    })?;
    e.set("Workplane.val", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            if unary("not", e.get("self")?.attr("objects")?)?.truthy()? {
                anyhow::bail!(
                    "{}",
                    val_string({
                        let _site = rt.source_at(
                            "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                            line!(),
                        );
                        {
                            let fun321 = e.get("TypeError")?;
                            let mut args319 = Vec::new();
                            let mut kw320 = Vec::new();
                            args319.push(Val::Str(
                                "normal enclosure geometry must be a Rust recipe".into(),
                            ));
                            fun321.call(args319, kw320)?
                        }
                    })?
                );
            }
            return Ok(e.get("self")?.attr("objects")?.get(Val::Int(0i64))?);
            Ok(Val::None)
        })
    })?;
    e.set("Workplane.vals", {
        let params = vec![("self".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok(e.get("self")?.attr("objects")?);
            Ok(Val::None)
        })
    })?;
    e.set("Workplane.__getattr__",{let params=vec![("self".into(),None,false),("name".into(),None,false)];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,None,None)?;let _frame=rt.frame(&outer);if {let v322=e.get("name")?;let v323={let mut s=Vec::new();s.push(Val::Str("fuse".into()));s.push(Val::Str("cut".into()));s.push(Val::Str("intersect".into()));s.push(Val::Str("clean".into()));s.push(Val::Str("translate".into()));s.push(Val::Str("rotate".into()));s.push(Val::Str("mirror".into()));s.push(Val::Str("moved".into()));Val::tuple(s)};Val::Bool(compare("in",v322.clone(),v323.clone())?.truthy()?)}.truthy()? {
// operation
e.set("operation",{let params=vec![];let outer=e.clone();let runtime=rt.clone();Val::function(move |args,kwargs| {let rt=runtime.clone();let e=bind(&outer,&params,args,kwargs,Some("args"),Some("kwargs"))?;let _frame=rt.frame(&outer);let assigned324={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun327=e.get("tuple")?;let mut args325=Vec::new();let mut kw326=Vec::new();args325.push({let e=e.child();let out328=Val::list(vec![]);for item329 in e.get("args")?.iter()? {e.set("a",item329)?;out328.attr("append")?.call(vec![if {let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun332=e.get("isinstance")?;let mut args330=Vec::new();let mut kw331=Vec::new();args330.push(e.get("a")?);args330.push(e.get("Workplane")?);fun332.call(args330,kw331)?}}.truthy()? {{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun335=e.get("a")?.attr("val")?;let mut args333=Vec::new();let mut kw334=Vec::new();fun335.call(args333,kw334)?}}} else {e.get("a")?}],vec![])?;}out328});fun327.call(args325,kw326)?}};e.set("args",assigned324.clone())?;
return Ok({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun338=e.get("Workplane")?;let mut args336=Vec::new();let mut kw337=Vec::new();args336.push(e.get("self")?.attr("plane")?);kw337.push(("obj".into(),{let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun341={let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun344=e.get("getattr")?;let mut args342=Vec::new();let mut kw343=Vec::new();args342.push({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun347=e.get("self")?.attr("val")?;let mut args345=Vec::new();let mut kw346=Vec::new();fun347.call(args345,kw346)?}});args342.push(e.get("name")?);fun344.call(args342,kw343)?}};let mut args339=Vec::new();let mut kw340=Vec::new();args339.extend(e.get("args")?.iter()?);kw340.extend(keyword_items(e.get("kwargs")?)?);fun341.call(args339,kw340)?}}));fun338.call(args336,kw337)?}});
Ok(Val::None)})})?;
return Ok(e.get("operation")?);
}
anyhow::bail!("{}",val_string({let _site=rt.source_at("tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",line!());{let fun350=e.get("AttributeError")?;let mut args348=Vec::new();let mut kw349=Vec::new();args348.push({let mut str351=String::new();str351.push_str(&format(&e.get("name")?,&String::new())?);str351.push_str(": normal enclosure geometry must be a Rust recipe");Val::Str(str351)});fun350.call(args348,kw349)?}})?);
Ok(Val::None)})})?;
    e.set(
        "Workplane",
        rt.python_type("_enclosure_datums", "Workplane")?,
    )?;
    e.set("Shape", rt.python_type("_enclosure_datums", "Shape")?)?;
    // install
    e.set("install", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned352 = binary(
                "truediv",
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun355 = {
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                                line!(),
                            );
                            {
                                let fun358 = e.get("Path")?;
                                let mut args356 = Vec::new();
                                let mut kw357 = Vec::new();
                                args356.push(e.get("__file__")?);
                                fun358.call(args356, kw357)?
                            }
                        }
                        .attr("resolve")?;
                        let mut args353 = Vec::new();
                        let mut kw354 = Vec::new();
                        fun355.call(args353, kw354)?
                    }
                }
                .attr("parents")?
                .get(Val::Int(3i64))?,
                Val::Str("scripts".into()),
            )?;
            e.set("scripts", assigned352.clone())?;
            if {
                let v362 = {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun361 = e.get("str")?;
                        let mut args359 = Vec::new();
                        let mut kw360 = Vec::new();
                        args359.push(e.get("scripts")?);
                        fun361.call(args359, kw360)?
                    }
                };
                let v363 = e.get("sys")?.attr("path")?;
                Val::Bool(compare("not_in", v362.clone(), v363.clone())?.truthy()?)
            }
            .truthy()?
            {
                {
                    let _site = rt.source_at(
                        "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                        line!(),
                    );
                    {
                        let fun366 = e.get("sys")?.attr("path")?.attr("insert")?;
                        let mut args364 = Vec::new();
                        let mut kw365 = Vec::new();
                        args364.push(Val::Int(0i64));
                        args364.push({
                            let _site = rt.source_at(
                                "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                                line!(),
                            );
                            {
                                let fun369 = e.get("str")?;
                                let mut args367 = Vec::new();
                                let mut kw368 = Vec::new();
                                args367.push(e.get("scripts")?);
                                fun369.call(args367, kw368)?
                            }
                        });
                        fun366.call(args364, kw365)?
                    }
                };
            }
            e.set("_rust_part", rt.import_module("_rust_part")?)?;
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun372 = e.get("_rust_part")?.attr("start")?;
                    let mut args370 = Vec::new();
                    let mut kw371 = Vec::new();
                    fun372.call(args370, kw371)?
                }
            };
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun375 = e.get("_rust_part")?.attr("_STANDINS")?.attr("update")?;
                    let mut args373 = Vec::new();
                    let mut kw374 = Vec::new();
                    kw374.push(("Vector".into(), e.get("Vector")?));
                    kw374.push(("Plane".into(), e.get("Plane")?));
                    kw374.push(("Location".into(), e.get("Location")?));
                    kw374.push(("Workplane".into(), e.get("Workplane")?));
                    kw374.push(("Shape".into(), e.get("Shape")?));
                    kw374.push(("Solid".into(), e.get("Shape")?));
                    kw374.push(("Compound".into(), e.get("Shape")?));
                    kw374.push(("Face".into(), e.get("Shape")?));
                    kw374.push(("Wire".into(), e.get("Shape")?));
                    kw374.push(("Edge".into(), e.get("Shape")?));
                    kw374.push(("MESH".into(), Val::Bool(false)));
                    kw374.push(("__path__".into(), {
                        let mut s = Vec::new();
                        Val::list(s)
                    }));
                    fun375.call(args373, kw374)?
                }
            };
            Ok(Val::None)
        })
    })?;
    // load
    e.set("load", {
        let params = vec![];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            {
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun378 = e.get("install")?;
                    let mut args376 = Vec::new();
                    let mut kw377 = Vec::new();
                    fun378.call(args376, kw377)?
                }
            };
            return Ok({
                let _site = rt.source_at(
                    "tools/hsm/enclosure-data/src/compiled/_enclosure_datums.rs",
                    line!(),
                );
                {
                    let fun381 = e.get("importlib")?.attr("import_module")?;
                    let mut args379 = Vec::new();
                    let mut kw380 = Vec::new();
                    args379.push(Val::Str("enclosure".into()));
                    fun381.call(args379, kw380)?
                }
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
