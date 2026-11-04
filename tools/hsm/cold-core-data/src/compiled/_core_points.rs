#![allow(unused_variables, unused_mut, unreachable_code)]
use super::*;

pub fn initialize(rt: Runtime, e: Env) -> Result<()> {
    e.set("math", rt.import_module("math")?)?;
    // add
    e.set("add", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun3 = e.get("tuple")?;
                let mut args1 = Vec::new();
                let mut kw2 = Vec::new();
                args1.push({
                    let e = e.child();
                    let out4 = Val::list(vec![]);
                    for item5 in {
                        let fun8 = e.get("zip")?;
                        let mut args6 = Vec::new();
                        let mut kw7 = Vec::new();
                        args6.push(e.get("a")?);
                        args6.push(e.get("b")?);
                        fun8.call(args6, kw7)?
                    }
                    .iter()?
                    {
                        let unpack9 = unpack(item5, 2)?;
                        e.set("x", unpack9[0].clone())?;
                        e.set("y", unpack9[1].clone())?;
                        out4.attr("append")?
                            .call(vec![binary("add", e.get("x")?, e.get("y")?)?], vec![])?;
                    }
                    out4
                });
                fun3.call(args1, kw2)?
            });
            Ok(Val::None)
        })
    })?;
    // sub
    e.set("sub", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun12 = e.get("tuple")?;
                let mut args10 = Vec::new();
                let mut kw11 = Vec::new();
                args10.push({
                    let e = e.child();
                    let out13 = Val::list(vec![]);
                    for item14 in {
                        let fun17 = e.get("zip")?;
                        let mut args15 = Vec::new();
                        let mut kw16 = Vec::new();
                        args15.push(e.get("a")?);
                        args15.push(e.get("b")?);
                        fun17.call(args15, kw16)?
                    }
                    .iter()?
                    {
                        let unpack18 = unpack(item14, 2)?;
                        e.set("x", unpack18[0].clone())?;
                        e.set("y", unpack18[1].clone())?;
                        out13
                            .attr("append")?
                            .call(vec![binary("sub", e.get("x")?, e.get("y")?)?], vec![])?;
                    }
                    out13
                });
                fun12.call(args10, kw11)?
            });
            Ok(Val::None)
        })
    })?;
    // scale
    e.set("scale", {
        let params = vec![("a".into(), None, false), ("factor".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun21 = e.get("tuple")?;
                let mut args19 = Vec::new();
                let mut kw20 = Vec::new();
                args19.push({
                    let e = e.child();
                    let out22 = Val::list(vec![]);
                    for item23 in e.get("a")?.iter()? {
                        e.set("x", item23)?;
                        out22
                            .attr("append")?
                            .call(vec![binary("mul", e.get("x")?, e.get("factor")?)?], vec![])?;
                    }
                    out22
                });
                fun21.call(args19, kw20)?
            });
            Ok(Val::None)
        })
    })?;
    // unit
    e.set("unit", {
        let params = vec![("a".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun26 = e.get("scale")?;
                let mut args24 = Vec::new();
                let mut kw25 = Vec::new();
                args24.push(e.get("a")?);
                args24.push(binary("truediv", Val::Float(1.0f64), {
                    let fun29 = e.get("math")?.attr("sqrt")?;
                    let mut args27 = Vec::new();
                    let mut kw28 = Vec::new();
                    args27.push({
                        let fun32 = e.get("sum")?;
                        let mut args30 = Vec::new();
                        let mut kw31 = Vec::new();
                        args30.push({
                            let e = e.child();
                            let out33 = Val::list(vec![]);
                            for item34 in e.get("a")?.iter()? {
                                e.set("x", item34)?;
                                out33
                                    .attr("append")?
                                    .call(vec![binary("mul", e.get("x")?, e.get("x")?)?], vec![])?;
                            }
                            out33
                        });
                        fun32.call(args30, kw31)?
                    });
                    fun29.call(args27, kw28)?
                })?);
                fun26.call(args24, kw25)?
            });
            Ok(Val::None)
        })
    })?;
    // dot
    e.set("dot", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let fun37 = e.get("sum")?;
                let mut args35 = Vec::new();
                let mut kw36 = Vec::new();
                args35.push({
                    let e = e.child();
                    let out38 = Val::list(vec![]);
                    for item39 in {
                        let fun42 = e.get("zip")?;
                        let mut args40 = Vec::new();
                        let mut kw41 = Vec::new();
                        args40.push(e.get("a")?);
                        args40.push(e.get("b")?);
                        fun42.call(args40, kw41)?
                    }
                    .iter()?
                    {
                        let unpack43 = unpack(item39, 2)?;
                        e.set("x", unpack43[0].clone())?;
                        e.set("y", unpack43[1].clone())?;
                        out38
                            .attr("append")?
                            .call(vec![binary("mul", e.get("x")?, e.get("y")?)?], vec![])?;
                    }
                    out38
                });
                fun37.call(args35, kw36)?
            });
            Ok(Val::None)
        })
    })?;
    // cross
    e.set("cross", {
        let params = vec![("a".into(), None, false), ("b".into(), None, false)];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            return Ok({
                let mut s = Vec::new();
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(1i64))?,
                        e.get("b")?.get(Val::Int(2i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(2i64))?,
                        e.get("b")?.get(Val::Int(1i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(2i64))?,
                        e.get("b")?.get(Val::Int(0i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(0i64))?,
                        e.get("b")?.get(Val::Int(2i64))?,
                    )?,
                )?);
                s.push(binary(
                    "sub",
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(0i64))?,
                        e.get("b")?.get(Val::Int(1i64))?,
                    )?,
                    binary(
                        "mul",
                        e.get("a")?.get(Val::Int(1i64))?,
                        e.get("b")?.get(Val::Int(0i64))?,
                    )?,
                )?);
                Val::tuple(s)
            });
            Ok(Val::None)
        })
    })?;
    // turned
    e.set("turned", {
        let params = vec![
            ("vector".into(), None, false),
            ("axis".into(), None, false),
            ("radians".into(), None, false),
        ];
        let outer = e.clone();
        let runtime = rt.clone();
        Val::function(move |args, kwargs| {
            let rt = runtime.clone();
            let e = bind(&outer, &params, args, kwargs, None, None)?;
            let _frame = rt.frame(&outer);
            let assigned44 = {
                let mut s = Vec::new();
                s.push({
                    let fun47 = e.get("math")?.attr("cos")?;
                    let mut args45 = Vec::new();
                    let mut kw46 = Vec::new();
                    args45.push(e.get("radians")?);
                    fun47.call(args45, kw46)?
                });
                s.push({
                    let fun50 = e.get("math")?.attr("sin")?;
                    let mut args48 = Vec::new();
                    let mut kw49 = Vec::new();
                    args48.push(e.get("radians")?);
                    fun50.call(args48, kw49)?
                });
                Val::tuple(s)
            };
            let unpack51 = unpack(assigned44.clone(), 2)?;
            e.set("c", unpack51[0].clone())?;
            e.set("s", unpack51[1].clone())?;
            return Ok({
                let fun54 = e.get("add")?;
                let mut args52 = Vec::new();
                let mut kw53 = Vec::new();
                args52.push({
                    let fun57 = e.get("add")?;
                    let mut args55 = Vec::new();
                    let mut kw56 = Vec::new();
                    args55.push({
                        let fun60 = e.get("scale")?;
                        let mut args58 = Vec::new();
                        let mut kw59 = Vec::new();
                        args58.push(e.get("vector")?);
                        args58.push(e.get("c")?);
                        fun60.call(args58, kw59)?
                    });
                    args55.push({
                        let fun63 = e.get("scale")?;
                        let mut args61 = Vec::new();
                        let mut kw62 = Vec::new();
                        args61.push({
                            let fun66 = e.get("cross")?;
                            let mut args64 = Vec::new();
                            let mut kw65 = Vec::new();
                            args64.push(e.get("axis")?);
                            args64.push(e.get("vector")?);
                            fun66.call(args64, kw65)?
                        });
                        args61.push(e.get("s")?);
                        fun63.call(args61, kw62)?
                    });
                    fun57.call(args55, kw56)?
                });
                args52.push({
                    let fun69 = e.get("scale")?;
                    let mut args67 = Vec::new();
                    let mut kw68 = Vec::new();
                    args67.push(e.get("axis")?);
                    args67.push(binary(
                        "mul",
                        {
                            let fun72 = e.get("dot")?;
                            let mut args70 = Vec::new();
                            let mut kw71 = Vec::new();
                            args70.push(e.get("axis")?);
                            args70.push(e.get("vector")?);
                            fun72.call(args70, kw71)?
                        },
                        binary("sub", Val::Float(1.0f64), e.get("c")?)?,
                    )?);
                    fun69.call(args67, kw68)?
                });
                fun54.call(args52, kw53)?
            });
            Ok(Val::None)
        })
    })?;
    Ok(())
}
pub fn entrypoint(rt: Runtime, e: Env) -> Result<Val> {
    Ok(Val::None)
}
